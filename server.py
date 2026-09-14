"""FastAPI demo: upload a 2D floor plan and run furniture detection."""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import os
import secrets
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from starlette.middleware.sessions import SessionMiddleware

from engine.furniture import DISPLAY_NAMES
from engine.pipeline import FloorPlanPipeline
from engine.plans import SAMPLE_PLANS

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

STATIC_DIR = ROOT / "static"
SAMPLES_DIR = ROOT / "data" / "samples"
UPLOADS_DIR = ROOT / "data" / "uploads"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI-Powered 2D Floor Plan Detection",
    description="Upload a 2D architectural floor plan and receive structure plus furniture detections.",
)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET_KEY", secrets.token_hex(32)),
    session_cookie="fp_session",
)
detector = FloorPlanPipeline()

# Dummy demo account — good enough to gate the demo, not meant for real users.
DEMO_USERNAME = os.environ.get("DEMO_USERNAME", "demo")
DEMO_PASSWORD_HASH = hashlib.sha256(
    os.environ.get("DEMO_PASSWORD", "demo@9558").encode("utf-8")
).hexdigest()


def _check_credentials(username: str, password: str) -> bool:
    if not hmac.compare_digest(username, DEMO_USERNAME):
        return False
    candidate_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(candidate_hash, DEMO_PASSWORD_HASH)


def require_login(request: Request) -> str:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return user


def _encode_png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _to_data_url(png_bytes: bytes) -> str:
    encoded = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"


@app.post("/api/login")
async def login(request: Request) -> JSONResponse:
    payload = await request.json()
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    if not _check_credentials(username, password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    request.session["user"] = username
    return JSONResponse({"ok": True, "user": username})


@app.post("/api/logout")
def logout(request: Request) -> JSONResponse:
    request.session.clear()
    return JSONResponse({"ok": True})


@app.get("/api/me")
def me(request: Request) -> JSONResponse:
    user = request.session.get("user")
    return JSONResponse({"authenticated": bool(user), "user": user})


@app.get("/api/samples")
def list_samples(user: str = Depends(require_login)) -> list[dict]:
    samples = [
        {
            "id": plan.plan_id,
            "title": plan.title,
            "subtitle": plan.subtitle,
            "filename": plan.filename,
            "description": plan.description,
            "image_url": f"/api/samples/{plan.plan_id}/image",
        }
        for plan in SAMPLE_PLANS
        if (SAMPLES_DIR / plan.filename).exists()
    ]
    real_plan = SAMPLES_DIR / "real_residential_plan.jpg"
    if real_plan.exists():
        samples.insert(
            0,
            {
                "id": "real_residential",
                "title": "Real residential CAD plan",
                "subtitle": "External floor-plan drawing",
                "filename": real_plan.name,
                "description": "Real architectural drawing used to validate inference beyond synthetic samples.",
                "image_url": "/api/samples/real_residential/image",
            },
        )
    apartment = SAMPLES_DIR / "user_apartment_plan.jpg"
    if apartment.exists():
        samples.insert(
            0,
            {
                "id": "user_apartment",
                "title": "Furnished apartment plan",
                "subtitle": "Colored interior-style drawing",
                "filename": apartment.name,
                "description": "Modern furnished apartment plan with sofa, bed, kitchen and terrace.",
                "image_url": "/api/samples/user_apartment/image",
            },
        )
    return samples


@app.get("/api/samples/{plan_id}/image")
def sample_image(plan_id: str, user: str = Depends(require_login)) -> FileResponse:
    if plan_id == "user_apartment":
        path = SAMPLES_DIR / "user_apartment_plan.jpg"
        if not path.exists():
            raise HTTPException(status_code=404, detail="Apartment sample missing.")
        return FileResponse(path, media_type="image/jpeg", filename=path.name)
    if plan_id == "real_residential":
        path = SAMPLES_DIR / "real_residential_plan.jpg"
        if not path.exists():
            raise HTTPException(status_code=404, detail="Real sample missing.")
        return FileResponse(path, media_type="image/jpeg", filename=path.name)
    plan = next((item for item in SAMPLE_PLANS if item.plan_id == plan_id), None)
    if plan is None:
        raise HTTPException(status_code=404, detail="Sample plan not found.")
    path = SAMPLES_DIR / plan.filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Sample image missing. Run generate_samples.py.")
    return FileResponse(path, media_type="image/png", filename=plan.filename)


@app.get("/api/classes")
def list_classes(user: str = Depends(require_login)) -> dict:
    return {"classes": DISPLAY_NAMES, "engine": detector.engine_name}


@app.post("/api/detect")
async def detect(file: UploadFile = File(...), user: str = Depends(require_login)) -> JSONResponse:
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file.")
    try:
        image = Image.open(io.BytesIO(contents))
        image.load()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read the uploaded image.") from exc

    content_hash = hashlib.sha1(contents).hexdigest()[:10]
    safe_name = Path(file.filename or "floorplan.png").name
    stamp = int(time.time())
    upload_path = UPLOADS_DIR / f"{stamp}_{content_hash}_{safe_name}"
    upload_path.write_bytes(contents)

    result = detector.detect(image)
    annotated_bytes = _encode_png(result.pop("annotated_image"))
    original_bytes = _encode_png(image.convert("RGB"))
    return JSONResponse(
        {
            "filename": safe_name,
            "content_hash": content_hash,
            "byte_size": len(contents),
            "engine": result.get("engine", detector.engine_name),
            "plan_style": result.get("plan_style"),
            "object_count": result["object_count"],
            "furniture_count": result.get("furniture_count", result["object_count"]),
            "door_count": result.get("door_count", 0),
            "window_count": result.get("window_count", 0),
            "room_count": result["room_count"],
            "roboflow_count": result.get("roboflow_count", 0),
            "roboflow_model": result.get("roboflow_model"),
            "summary": result["summary"],
            "objects": result["objects"],
            "rooms": result["rooms"],
            "image_width": result["image_width"],
            "image_height": result["image_height"],
            "inference_ms": result["inference_ms"],
            "original_data_url": _to_data_url(original_bytes),
            "annotated_data_url": _to_data_url(annotated_bytes),
            "message": (
                None
                if result["object_count"] > 0
                else "No symbols detected. Try a clearer CAD/PDF export or a higher-resolution floor plan."
            ),
        }
    )


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "engine": detector.engine_name,
        "roboflow_model": detector.roboflow.model_id if detector.roboflow.enabled else None,
        "roboflow_enabled": detector.roboflow.enabled,
    }


@app.get("/login")
def login_page(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/")
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/")
def index(request: Request):
    if not request.session.get("user"):
        return RedirectResponse(url="/login")
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

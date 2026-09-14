"""Roboflow-hosted floor-plan object detector (floor-plan-all-objects/4)."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image

DEFAULT_MODEL_ID = "floor-plan-all-objects/4"
DEFAULT_API_URL = "https://serverless.roboflow.com"

# Map the model's 21 classes into our pipeline vocabulary.
# Keys are lowercased, whitespace-preserved class names as Roboflow returns them.
CLASS_MAP = {
    "dinner table": ("Dining Table", "table", True),
    "double bed": ("Double Bed", "bed", True),
    "double door": ("Double Door", "door", False),
    "oven stove": ("Oven/Stove", "stove", True),
    "plant": ("Plant", "plant", True),
    "refrigerator": ("Refrigerator", "refrigerator", True),
    "showcase table": ("Showcase Table", "table", True),
    "shower": ("Shower", "shower", True),
    "single bed": ("Single Bed", "bed", True),
    "single door": ("Door", "door", False),
    "sink": ("Sink", "sink", True),
    "sofa": ("Sofa", "sofa", True),
    "stairs": ("Stairs", "stairs", False),
    "study table": ("Study Table", "table", True),
    "table": ("Table", "table", True),
    "television": ("Television", "television", True),
    "toilet": ("Toilet", "toilet", True),
    "wardrobe": ("Wardrobe", "wardrobe", True),
    "wash basin": ("Wash Basin", "sink", True),
    "washing machine": ("Washing Machine", "washing_machine", True),
    "windows": ("Window", "window", False),
}

STRUCTURE_KEEP = {"door", "window"}
FURNITURE_KEEP = {
    "table",
    "bed",
    "stove",
    "plant",
    "refrigerator",
    "shower",
    "sink",
    "sofa",
    "television",
    "toilet",
    "wardrobe",
    "washing_machine",
}


class RoboflowFloorPlanDetector:
    def __init__(
        self,
        api_key: str | None = None,
        model_id: str | None = None,
        api_url: str | None = None,
        confidence: float = 0.2,
    ) -> None:
        self.api_key = api_key or os.getenv("ROBOFLOW_API_KEY") or os.getenv("api_key")
        self.model_id = model_id or os.getenv("ROBOFLOW_MODEL_ID") or DEFAULT_MODEL_ID
        self.api_url = api_url or os.getenv("ROBOFLOW_API_URL") or DEFAULT_API_URL
        self.confidence = confidence
        self._client = None
        self.enabled = bool(self.api_key)

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise RuntimeError("Roboflow api_key is missing.")
        from inference_sdk import InferenceConfiguration, InferenceHTTPClient

        self._client = InferenceHTTPClient(
            api_url=self.api_url,
            api_key=self.api_key,
        ).configure(
            InferenceConfiguration(
                api_key_transport="header",
                confidence_threshold=self.confidence,
                iou_threshold=0.4,
            )
        )
        return self._client

    def detect(self, pil_image: Image.Image) -> list[dict]:
        if not self.enabled:
            return []
        import tempfile

        client = self._get_client()
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as temp_file:
            pil_image.convert("RGB").save(temp_file.name, format="JPEG", quality=92)
            result = client.infer(temp_file.name, model_id=self.model_id)
        predictions = result.get("predictions", []) if isinstance(result, dict) else []
        objects: list[dict] = []
        for prediction in predictions:
            raw_class = str(prediction.get("class") or "").strip()
            confidence = float(prediction.get("confidence") or 0.0)
            if confidence < self.confidence:
                continue
            mapped = CLASS_MAP.get(raw_class.lower())
            if mapped is None:
                label = raw_class.title() or "Object"
                canonical = raw_class.lower().replace(" ", "_") or "object"
                is_furniture = False
            else:
                label, canonical, is_furniture = mapped

            center_x = float(prediction["x"])
            center_y = float(prediction["y"])
            width = float(prediction["width"])
            height = float(prediction["height"])
            x1 = int(max(0, center_x - width / 2))
            y1 = int(max(0, center_y - height / 2))
            x2 = int(center_x + width / 2)
            y2 = int(center_y + height / 2)
            objects.append(
                {
                    "class_name": canonical,
                    "label": label,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2],
                    "centroid": [int(center_x), int(center_y)],
                    "area_px": int(max(1, width * height)),
                    "is_furniture": is_furniture,
                    "source": "roboflow",
                    "roboflow_class": raw_class,
                }
            )
        return objects


def load_roboflow_api_key(env_path: Path | None = None) -> str | None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        load_dotenv = None
    if load_dotenv is not None:
        path = env_path or Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(path)
    return os.getenv("ROBOFLOW_API_KEY") or os.getenv("api_key")

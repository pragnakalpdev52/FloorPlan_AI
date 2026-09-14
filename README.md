# AI-Powered 2D Floor Plan Furniture Segmentation & Detection

Demo app for detecting, classifying, and segmenting furniture on CAD-style 2D floor plans.

The client-facing flow is:

1. Preview the 2D floor plan
2. Upload that file
3. Review bounding boxes, instance masks, room inventory, and JSON

## Run

This project uses [uv](https://docs.astral.sh/uv/) for environment and dependency management.

```bash
uv venv
uv pip install -r requirements.txt
uv run generate_samples.py
uv run uvicorn server:app --host 127.0.0.1 --port 8000
```

Or just run:

```bash
./run.sh
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and sign in with the demo account: `demo` / `demo@9558`.

## Inference engine

The API runs two models on every upload:

1. **CubiCasa ResNet-34 UNet** — walls, doors, windows, rooms (best for general architect drawings)
2. **FloorPlanCAD YOLOv8n** — furniture symbols when the drawing style matches

Best results: clean 2D CAD / PDF exports.


Record at desktop width. The previous clip only showed two uploads; this flow has to show detections.

1. Open the app. **Residential Unit A** loads as a full 2D CAD plan. Pause 3–4 seconds on the drawing.
2. Click **Upload this plan & detect**. Keep the processing overlay on screen.
3. Show the results: original vs annotated plan, inventory table (beds, sofas, chairs, tables, fixtures), class counts, JSON.
4. Click **Residential Unit B**, pause on that 2D plan, then **Upload this plan & detect** again so the second drawing also shows boxed objects.

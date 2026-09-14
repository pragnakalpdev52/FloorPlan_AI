"""Render sample 2D floor plans and furniture templates."""

from __future__ import annotations

from pathlib import Path

from engine.furniture import export_templates
from engine.plans import SAMPLE_PLANS, render_plan

ROOT = Path(__file__).resolve().parent
SAMPLES_DIR = ROOT / "data" / "samples"
TEMPLATES_DIR = ROOT / "data" / "templates"


def main() -> None:
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    export_templates(TEMPLATES_DIR)
    for plan in SAMPLE_PLANS:
        image = render_plan(plan.plan_id)
        output_path = SAMPLES_DIR / plan.filename
        image.save(output_path, format="PNG")
        print(f"Wrote {output_path} ({image.width}x{image.height})")
    print(f"Wrote templates to {TEMPLATES_DIR}")


if __name__ == "__main__":
    main()

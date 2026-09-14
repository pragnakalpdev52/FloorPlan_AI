"""Generate the Label Studio labeling config from engine/classes.py.

Keeps the annotation taxonomy in sync with training/inference automatically
instead of hand-copying class names into an XML file.
"""

from __future__ import annotations

from pathlib import Path

from engine.classes import DISPLAY_NAMES, FURNITURE_CLASSES, STRUCTURE_CLASSES

OUT_PATH = Path(__file__).resolve().parent / "label_config.xml"

STRUCTURE_COLOR = "#d94f4f"
FURNITURE_COLOR = "#4f8fd9"


def main() -> None:
    labels = []
    for name in STRUCTURE_CLASSES:
        labels.append(f'    <Label value="{name}" background="{STRUCTURE_COLOR}"/>  <!-- {DISPLAY_NAMES[name]} -->')
    for name in FURNITURE_CLASSES:
        labels.append(f'    <Label value="{name}" background="{FURNITURE_COLOR}"/>  <!-- {DISPLAY_NAMES[name]} -->')
    labels_block = "\n".join(labels)

    config = f"""<View>
  <Image name="image" value="$image" zoom="true" zoomControl="true"/>
  <RectangleLabels name="label" toName="image">
{labels_block}
  </RectangleLabels>
</View>
"""
    OUT_PATH.write_text(config)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

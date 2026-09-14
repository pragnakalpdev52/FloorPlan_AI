"""Architectural plan-view furniture symbols and wall drawing helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont


INK = (28, 28, 28)
PAPER = (255, 255, 255)
MUTED = (90, 90, 90)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CANONICAL_SIZES: dict[str, tuple[int, int]] = {
    "bed": (200, 160),
    "sofa": (246, 90),
    "chair": (46, 46),
    "table": (102, 62),
    "dining_table": (154, 92),
    "wardrobe": (52, 184),
    "bedside_cupboard": (48, 48),
    "tv_cabinet": (230, 42),
    "toilet": (42, 70),
    "sink": (60, 44),
    "bathtub": (172, 78),
    "stove": (62, 62),
    "refrigerator": (56, 72),
    "cabinet": (150, 44),
}

DISPLAY_NAMES: dict[str, str] = {
    "bed": "Bed",
    "sofa": "Sofa",
    "chair": "Chair",
    "table": "Table",
    "dining_table": "Dining Table",
    "wardrobe": "Wardrobe",
    "bedside_cupboard": "Nightstand",
    "tv_cabinet": "TV Cabinet",
    "toilet": "Toilet",
    "sink": "Sink",
    "bathtub": "Bathtub",
    "stove": "Stove",
    "refrigerator": "Refrigerator",
    "cabinet": "Cabinet",
    "door": "Door",
    "window": "Window",
    "shower": "Shower",
    "stairs": "Stairs",
    "plant": "Plant",
    "television": "Television",
    "washing_machine": "Washing Machine",
}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONT_BOLD_PATH if bold else FONT_PATH
    try:
        return ImageFont.truetype(path, size=size)
    except OSError:
        return ImageFont.load_default()


def _rect(draw: ImageDraw.ImageDraw, box: list[int], width: int = 2) -> None:
    draw.rectangle(box, outline=INK, width=width)


def _draw_bed(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    headboard_height = max(10, int(height * 0.12))
    draw.rectangle([x, y, x + width - 1, y + headboard_height], outline=INK, width=2)
    pillow_gap = 8
    pillow_width = int(width * 0.36)
    pillow_height = int(height * 0.18)
    left = x + pillow_gap
    right = x + width - pillow_gap - pillow_width
    pillow_top = y + headboard_height + 6
    _rect(draw, [left, pillow_top, left + pillow_width, pillow_top + pillow_height], 2)
    _rect(draw, [right, pillow_top, right + pillow_width, pillow_top + pillow_height], 2)
    blanket_y = pillow_top + pillow_height + 10
    draw.line([(x + 4, blanket_y), (x + width - 5, blanket_y)], fill=INK, width=1)
    draw.line(
        [(x + 4, y + height - 14), (x + width - 5, y + height - 14)],
        fill=INK,
        width=1,
    )


def _draw_sofa(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    backrest = max(12, int(height * 0.28))
    draw.rectangle([x, y, x + width - 1, y + backrest], outline=INK, width=2)
    arm = max(10, int(width * 0.08))
    draw.rectangle([x, y, x + arm, y + height - 1], outline=INK, width=2)
    draw.rectangle([x + width - arm - 1, y, x + width - 1, y + height - 1], outline=INK, width=2)
    seat_top = y + backrest
    seat_width = width - 2 * arm
    for index in range(1, 3):
        split_x = x + arm + int(seat_width * index / 3)
        draw.line([(split_x, seat_top), (split_x, y + height - 2)], fill=INK, width=1)


def _draw_chair(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    backrest = max(7, int(height * 0.22))
    draw.rectangle([x, y, x + width - 1, y + backrest], outline=INK, width=2)
    inset = 8
    _rect(
        draw,
        [x + inset, y + backrest + 4, x + width - inset - 1, y + height - inset],
        1,
    )


def _draw_table(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    inset = 8
    _rect(
        draw,
        [x + inset, y + inset, x + width - inset - 1, y + height - inset - 1],
        1,
    )


def _draw_dining_table(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    cx = x + width // 2
    cy = y + height // 2
    draw.ellipse(
        [cx - 10, cy - 10, cx + 10, cy + 10],
        outline=INK,
        width=2,
    )
    draw.line([(x + 12, cy), (x + width - 13, cy)], fill=INK, width=1)
    draw.line([(cx, y + 12), (cx, y + height - 13)], fill=INK, width=1)


def _draw_wardrobe(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    mid = x + width // 2
    draw.line([(mid, y + 2), (mid, y + height - 3)], fill=INK, width=2)
    handle_y1 = y + height // 3
    handle_y2 = y + (2 * height) // 3
    draw.ellipse([mid - 10, handle_y1 - 4, mid - 3, handle_y1 + 4], outline=INK, width=1)
    draw.ellipse([mid + 3, handle_y2 - 4, mid + 10, handle_y2 + 4], outline=INK, width=1)


def _draw_bedside(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    draw.line(
        [(x + 4, y + height // 2), (x + width - 5, y + height // 2)],
        fill=INK,
        width=1,
    )
    knob_x = x + width // 2
    knob_y = y + height // 2 + 8
    draw.ellipse([knob_x - 3, knob_y - 3, knob_x + 3, knob_y + 3], outline=INK, width=1)


def _draw_tv_cabinet(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    draw.line(
        [(x + 6, y + height // 2), (x + width - 7, y + height // 2)],
        fill=INK,
        width=1,
    )
    for fraction in (0.25, 0.5, 0.75):
        split_x = x + int(width * fraction)
        draw.line([(split_x, y + 2), (split_x, y + height - 3)], fill=INK, width=1)


def _draw_toilet(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    tank_height = int(height * 0.32)
    _rect(draw, [x, y, x + width - 1, y + tank_height], 2)
    bowl_top = y + tank_height - 2
    draw.ellipse(
        [x + 2, bowl_top, x + width - 3, y + height - 1],
        outline=INK,
        width=2,
    )
    inner_pad = 8
    draw.ellipse(
        [
            x + inner_pad,
            bowl_top + 8,
            x + width - inner_pad - 1,
            y + height - 8,
        ],
        outline=INK,
        width=1,
    )


def _draw_sink(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    pad_x, pad_y = 8, 8
    draw.ellipse(
        [x + pad_x, y + pad_y, x + width - pad_x - 1, y + height - pad_y - 1],
        outline=INK,
        width=2,
    )
    faucet_x = x + width // 2
    draw.line([(faucet_x, y + 3), (faucet_x, y + pad_y + 4)], fill=INK, width=2)
    draw.line(
        [(faucet_x - 6, y + pad_y + 4), (faucet_x + 6, y + pad_y + 4)],
        fill=INK,
        width=2,
    )


def _draw_bathtub(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    pad = 8
    draw.rounded_rectangle(
        [x + pad, y + pad, x + width - pad - 1, y + height - pad - 1],
        radius=16,
        outline=INK,
        width=2,
    )
    draw.ellipse([x + 14, y + height // 2 - 6, x + 28, y + height // 2 + 6], outline=INK, width=1)


def _draw_stove(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    burner_r = max(6, width // 8)
    offsets = [
        (width * 0.30, height * 0.30),
        (width * 0.70, height * 0.30),
        (width * 0.30, height * 0.70),
        (width * 0.70, height * 0.70),
    ]
    for offset_x, offset_y in offsets:
        cx = x + int(offset_x)
        cy = y + int(offset_y)
        draw.ellipse(
            [cx - burner_r, cy - burner_r, cx + burner_r, cy + burner_r],
            outline=INK,
            width=2,
        )


def _draw_refrigerator(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    split = y + int(height * 0.38)
    draw.line([(x + 2, split), (x + width - 3, split)], fill=INK, width=2)
    draw.line([(x + width - 10, y + 8), (x + width - 10, split - 6)], fill=INK, width=2)
    draw.line(
        [(x + width - 10, split + 6), (x + width - 10, y + height - 8)],
        fill=INK,
        width=2,
    )


def _draw_cabinet(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    _rect(draw, [x, y, x + width - 1, y + height - 1], 2)
    for fraction in (0.33, 0.66):
        split_x = x + int(width * fraction)
        draw.line([(split_x, y + 2), (split_x, y + height - 3)], fill=INK, width=1)
    handle_y = y + height // 2
    for fraction in (0.16, 0.50, 0.83):
        hx = x + int(width * fraction)
        draw.ellipse([hx - 3, handle_y - 3, hx + 3, handle_y + 3], outline=INK, width=1)


SYMBOL_DRAWERS: dict[str, Callable[[ImageDraw.ImageDraw, int, int, int, int], None]] = {
    "bed": _draw_bed,
    "sofa": _draw_sofa,
    "chair": _draw_chair,
    "table": _draw_table,
    "dining_table": _draw_dining_table,
    "wardrobe": _draw_wardrobe,
    "bedside_cupboard": _draw_bedside,
    "tv_cabinet": _draw_tv_cabinet,
    "toilet": _draw_toilet,
    "sink": _draw_sink,
    "bathtub": _draw_bathtub,
    "stove": _draw_stove,
    "refrigerator": _draw_refrigerator,
    "cabinet": _draw_cabinet,
}


def render_sprite(
    class_name: str,
    width: int | None = None,
    height: int | None = None,
    rotation: int = 0,
    padding: int = 4,
) -> Image.Image:
    if class_name not in SYMBOL_DRAWERS:
        raise KeyError(f"Unknown furniture class: {class_name}")
    canonical_width, canonical_height = CANONICAL_SIZES[class_name]
    width = width or canonical_width
    height = height or canonical_height
    sprite = Image.new("RGB", (width, height), PAPER)
    drawer = SYMBOL_DRAWERS[class_name]
    drawer(ImageDraw.Draw(sprite), 0, 0, width, height)
    if rotation:
        sprite = sprite.rotate(rotation, expand=True, fillcolor=PAPER)
    if padding:
        padded = Image.new(
            "RGB",
            (sprite.width + padding * 2, sprite.height + padding * 2),
            PAPER,
        )
        padded.paste(sprite, (padding, padding))
        return padded
    return sprite


def paste_furniture(
    canvas: Image.Image,
    class_name: str,
    left: int,
    top: int,
    rotation: int = 0,
) -> dict:
    sprite = render_sprite(class_name, rotation=rotation, padding=0)
    canvas.paste(sprite, (left, top))
    return {
        "class_name": class_name,
        "bbox": [left, top, left + sprite.width, top + sprite.height],
        "rotation": rotation,
    }


def export_templates(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for class_name in SYMBOL_DRAWERS:
        for rotation in (0, 90):
            sprite = render_sprite(class_name, rotation=rotation, padding=2)
            suffix = "" if rotation == 0 else f"_r{rotation}"
            sprite.save(output_dir / f"{class_name}{suffix}.png")


def draw_horizontal_wall(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    length: int,
    thickness: int,
) -> None:
    draw.rectangle(
        [x, y - thickness // 2, x + length, y + thickness // 2],
        fill=INK,
    )


def draw_vertical_wall(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    length: int,
    thickness: int,
) -> None:
    draw.rectangle(
        [x - thickness // 2, y, x + thickness // 2, y + length],
        fill=INK,
    )


def cut_opening(draw: ImageDraw.ImageDraw, box: list[int]) -> None:
    draw.rectangle(box, fill=PAPER)


def draw_door_swing(
    draw: ImageDraw.ImageDraw,
    hinge_x: int,
    hinge_y: int,
    leaf: int,
    orientation: str,
) -> None:
    """orientation: n, s, e, w — direction the opening faces into the room."""
    if orientation == "s":
        draw.line([(hinge_x, hinge_y), (hinge_x, hinge_y + leaf)], fill=INK, width=2)
        draw.arc(
            [hinge_x - leaf, hinge_y - leaf, hinge_x + leaf, hinge_y + leaf],
            start=0,
            end=90,
            fill=INK,
            width=1,
        )
    elif orientation == "n":
        draw.line([(hinge_x, hinge_y), (hinge_x, hinge_y - leaf)], fill=INK, width=2)
        draw.arc(
            [hinge_x - leaf, hinge_y - leaf, hinge_x + leaf, hinge_y + leaf],
            start=270,
            end=360,
            fill=INK,
            width=1,
        )
    elif orientation == "e":
        draw.line([(hinge_x, hinge_y), (hinge_x + leaf, hinge_y)], fill=INK, width=2)
        draw.arc(
            [hinge_x - leaf, hinge_y - leaf, hinge_x + leaf, hinge_y + leaf],
            start=0,
            end=90,
            fill=INK,
            width=1,
        )
    elif orientation == "w":
        draw.line([(hinge_x, hinge_y), (hinge_x - leaf, hinge_y)], fill=INK, width=2)
        draw.arc(
            [hinge_x - leaf, hinge_y - leaf, hinge_x + leaf, hinge_y + leaf],
            start=90,
            end=180,
            fill=INK,
            width=1,
        )


def draw_window_horizontal(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    wall_thickness: int,
) -> None:
    cut_opening(
        draw,
        [x, y - wall_thickness // 2, x + width, y + wall_thickness // 2],
    )
    draw.line([(x, y - 3), (x + width, y - 3)], fill=INK, width=2)
    draw.line([(x, y + 3), (x + width, y + 3)], fill=INK, width=2)
    draw.line(
        [(x, y - wall_thickness // 2), (x, y + wall_thickness // 2)],
        fill=INK,
        width=2,
    )
    draw.line(
        [(x + width, y - wall_thickness // 2), (x + width, y + wall_thickness // 2)],
        fill=INK,
        width=2,
    )


def draw_window_vertical(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    height: int,
    wall_thickness: int,
) -> None:
    cut_opening(
        draw,
        [x - wall_thickness // 2, y, x + wall_thickness // 2, y + height],
    )
    draw.line([(x - 3, y), (x - 3, y + height)], fill=INK, width=2)
    draw.line([(x + 3, y), (x + 3, y + height)], fill=INK, width=2)
    draw.line(
        [(x - wall_thickness // 2, y), (x + wall_thickness // 2, y)],
        fill=INK,
        width=2,
    )
    draw.line(
        [(x - wall_thickness // 2, y + height), (x + wall_thickness // 2, y + height)],
        fill=INK,
        width=2,
    )

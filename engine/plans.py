"""Two CAD-style 2D floor plans with architectural furniture symbols."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw

from engine.furniture import (
    INK,
    PAPER,
    cut_opening,
    draw_door_swing,
    draw_horizontal_wall,
    draw_vertical_wall,
    draw_window_horizontal,
    draw_window_vertical,
    load_font,
    paste_furniture,
)


MM_PER_PIXEL = 10
EXTERIOR_WALL = 18
INTERIOR_WALL = 10


@dataclass(frozen=True)
class SamplePlan:
    plan_id: str
    title: str
    subtitle: str
    filename: str
    description: str


SAMPLE_PLANS: list[SamplePlan] = [
    SamplePlan(
        plan_id="unit_a",
        title="Residential Unit A",
        subtitle="Ground floor · 2 bedroom apartment",
        filename="unit_a_ground_floor.png",
        description="Two bedrooms, living/dining, kitchen and bathroom with full furniture layout.",
    ),
    SamplePlan(
        plan_id="unit_b",
        title="Residential Unit B",
        subtitle="Ground floor · open-plan apartment",
        filename="unit_b_open_plan.png",
        description="Open living-kitchen, bedroom, study nook and bathroom.",
    ),
]


def _label(draw: ImageDraw.ImageDraw, text: str, cx: int, cy: int, size: int = 18) -> None:
    font = load_font(size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    draw.text((cx - width // 2, cy - height // 2), text, fill=INK, font=font)


def _muted_label(draw: ImageDraw.ImageDraw, text: str, cx: int, cy: int, size: int = 13) -> None:
    font = load_font(size, bold=False)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    draw.text((cx - width // 2, cy - height // 2), text, fill=(110, 110, 110), font=font)


def _title_block(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    canvas_height: int,
    project: str,
    drawing: str,
) -> None:
    top = canvas_height - 118
    draw.rectangle([40, top, canvas_width - 40, canvas_height - 36], outline=INK, width=2)
    draw.line([(40, top + 28), (canvas_width - 40, top + 28)], fill=INK, width=1)
    font_small = load_font(11)
    font_title = load_font(16, bold=True)
    draw.text((54, top + 6), "AI FLOOR PLAN DETECTION  ·  ARCHITECTURAL DRAWING", fill=INK, font=font_small)
    draw.text((54, top + 38), f"PROJECT  {project}", fill=INK, font=font_title)
    draw.text((54, top + 62), f"DRAWING  {drawing}", fill=INK, font=load_font(13))
    draw.text((canvas_width - 430, top + 38), "SCALE  1:100", fill=INK, font=load_font(13))
    draw.text((canvas_width - 430, top + 62), "UNITS  millimetres", fill=INK, font=load_font(13))


def _north_arrow(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.polygon([(x, y - 36), (x - 10, y + 8), (x, y), (x + 10, y + 8)], outline=INK)
    draw.polygon([(x, y - 36), (x - 10, y + 8), (x, y)], fill=INK)
    font = load_font(14, bold=True)
    draw.text((x - 6, y + 12), "N", fill=INK, font=font)


def _scale_bar(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """1 m and 2 m bar at 1 px = 10 mm, so 100 px = 1 m."""
    draw.rectangle([x, y, x + 100, y + 8], fill=INK)
    draw.rectangle([x + 100, y, x + 200, y + 8], outline=INK, width=1)
    font = load_font(11)
    draw.text((x - 4, y + 12), "0", fill=INK, font=font)
    draw.text((x + 88, y + 12), "1 m", fill=INK, font=font)
    draw.text((x + 184, y + 12), "2 m", fill=INK, font=font)


def _dimension(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, text: str) -> None:
    draw.line([(x1, y1), (x2, y2)], fill=INK, width=1)
    font = load_font(12)
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    if abs(x2 - x1) > abs(y2 - y1):
        draw.text((cx - width // 2, cy - 16), text, fill=INK, font=font)
        draw.line([(x1, y1 - 6), (x1, y1 + 6)], fill=INK, width=1)
        draw.line([(x2, y2 - 6), (x2, y2 + 6)], fill=INK, width=1)
    else:
        draw.text((cx + 8, cy - 6), text, fill=INK, font=font)
        draw.line([(x1 - 6, y1), (x1 + 6, y1)], fill=INK, width=1)
        draw.line([(x2 - 6, y2), (x2 + 6, y2)], fill=INK, width=1)


def _horizontal_door(
    draw: ImageDraw.ImageDraw,
    wall_y: int,
    opening_x: int,
    leaf: int,
    wall_thickness: int,
    swing: str,
) -> None:
    cut_opening(
        draw,
        [
            opening_x,
            wall_y - wall_thickness // 2 - 1,
            opening_x + leaf,
            wall_y + wall_thickness // 2 + 1,
        ],
    )
    draw_door_swing(draw, opening_x, wall_y, leaf, swing)


def _vertical_door(
    draw: ImageDraw.ImageDraw,
    wall_x: int,
    opening_y: int,
    leaf: int,
    wall_thickness: int,
    swing: str,
) -> None:
    cut_opening(
        draw,
        [
            wall_x - wall_thickness // 2 - 1,
            opening_y,
            wall_x + wall_thickness // 2 + 1,
            opening_y + leaf,
        ],
    )
    draw_door_swing(draw, wall_x, opening_y, leaf, swing)


def render_unit_a() -> Image.Image:
    canvas_width, canvas_height = 2100, 1580
    image = Image.new("RGB", (canvas_width, canvas_height), PAPER)
    draw = ImageDraw.Draw(image)

    origin_x, origin_y = 340, 210
    inner_w, inner_h = 1400, 1000
    exterior = EXTERIOR_WALL

    draw.rectangle(
        [
            origin_x - exterior,
            origin_y - exterior,
            origin_x + inner_w + exterior,
            origin_y + inner_h + exterior,
        ],
        fill=INK,
    )
    draw.rectangle(
        [origin_x, origin_y, origin_x + inner_w, origin_y + inner_h],
        fill=PAPER,
    )

    bedroom_depth = 400
    split_x = origin_x + 560
    bath_w = 280
    wet_h = 320
    hall_top = origin_y + bedroom_depth + wet_h

    draw_horizontal_wall(draw, origin_x, origin_y + bedroom_depth, inner_w, INTERIOR_WALL)
    draw_vertical_wall(draw, split_x, origin_y, bedroom_depth, INTERIOR_WALL)
    draw_vertical_wall(draw, split_x, origin_y + bedroom_depth, inner_h - bedroom_depth, INTERIOR_WALL)
    draw_horizontal_wall(draw, origin_x, hall_top, split_x - origin_x, INTERIOR_WALL)
    draw_vertical_wall(draw, origin_x + bath_w, origin_y + bedroom_depth, wet_h, INTERIOR_WALL)

    _horizontal_door(draw, origin_y + bedroom_depth, origin_x + 210, 90, INTERIOR_WALL, "s")
    _horizontal_door(draw, origin_y + bedroom_depth, origin_x + 720, 90, INTERIOR_WALL, "s")
    _vertical_door(draw, origin_x + bath_w, origin_y + 470, 80, INTERIOR_WALL, "e")
    _vertical_door(draw, split_x, origin_y + 470, 80, INTERIOR_WALL, "e")
    _horizontal_door(draw, origin_y + inner_h, origin_x + 180, 100, exterior, "n")

    north = origin_y
    south = origin_y + inner_h
    west = origin_x
    east = origin_x + inner_w
    draw_window_horizontal(draw, origin_x + 80, north, 180, exterior)
    draw_window_horizontal(draw, origin_x + 300, north, 160, exterior)
    draw_window_horizontal(draw, origin_x + 680, north, 220, exterior)
    draw_window_horizontal(draw, origin_x + 1000, north, 220, exterior)
    draw_window_vertical(draw, east, origin_y + 80, 180, exterior)
    draw_window_vertical(draw, east, origin_y + 560, 260, exterior)
    draw_window_horizontal(draw, origin_x + 780, south, 240, exterior)
    draw_window_horizontal(draw, origin_x + 1080, south, 200, exterior)
    draw_window_vertical(draw, west, origin_y + 80, 160, exterior)
    draw_window_vertical(draw, west, origin_y + 460, 120, exterior)

    paste_furniture(image, "bed", origin_x + 170, origin_y + 28)
    paste_furniture(image, "bedside_cupboard", origin_x + 112, origin_y + 28)
    paste_furniture(image, "bedside_cupboard", origin_x + 380, origin_y + 28)
    paste_furniture(image, "wardrobe", origin_x + 24, origin_y + 120)
    paste_furniture(image, "chair", origin_x + 460, origin_y + 300)

    paste_furniture(image, "bed", origin_x + 780, origin_y + 28)
    paste_furniture(image, "bedside_cupboard", origin_x + 722, origin_y + 28)
    paste_furniture(image, "bedside_cupboard", origin_x + 990, origin_y + 28)
    paste_furniture(image, "wardrobe", origin_x + 1320, origin_y + 40)
    paste_furniture(image, "table", origin_x + 600, origin_y + 300)
    paste_furniture(image, "chair", origin_x + 628, origin_y + 248)

    paste_furniture(image, "bathtub", origin_x + 24, origin_y + 424)
    paste_furniture(image, "toilet", origin_x + 214, origin_y + 430)
    paste_furniture(image, "sink", origin_x + 24, origin_y + 640)

    paste_furniture(image, "cabinet", origin_x + 300, origin_y + 424)
    paste_furniture(image, "stove", origin_x + 460, origin_y + 424)
    paste_furniture(image, "sink", origin_x + 300, origin_y + 480)
    paste_furniture(image, "refrigerator", origin_x + 488, origin_y + 620)

    paste_furniture(image, "tv_cabinet", origin_x + 720, origin_y + 430)
    paste_furniture(image, "sofa", origin_x + 720, origin_y + 860)
    paste_furniture(image, "table", origin_x + 790, origin_y + 760)
    paste_furniture(image, "dining_table", origin_x + 1120, origin_y + 620)
    paste_furniture(image, "chair", origin_x + 1174, origin_y + 568)
    paste_furniture(image, "chair", origin_x + 1174, origin_y + 718)
    paste_furniture(image, "chair", origin_x + 1068, origin_y + 644)
    paste_furniture(image, "chair", origin_x + 1280, origin_y + 644)

    _label(draw, "BEDROOM 1", origin_x + 280, origin_y + 250)
    _muted_label(draw, "16.8 m²", origin_x + 280, origin_y + 274)
    _label(draw, "BEDROOM 2", origin_x + 980, origin_y + 250)
    _muted_label(draw, "25.2 m²", origin_x + 980, origin_y + 274)
    _label(draw, "BATH", origin_x + 140, origin_y + 560, 16)
    _muted_label(draw, "6.7 m²", origin_x + 140, origin_y + 582)
    _label(draw, "KITCHEN", origin_x + 420, origin_y + 560, 16)
    _muted_label(draw, "6.7 m²", origin_x + 420, origin_y + 582)
    _label(draw, "ENTRY", origin_x + 280, origin_y + 860, 16)
    _label(draw, "LIVING / DINING", origin_x + 980, origin_y + 700)
    _muted_label(draw, "37.8 m²", origin_x + 980, origin_y + 724)

    _title_block(
        draw,
        canvas_width,
        canvas_height,
        "RESIDENTIAL UNIT A",
        "GROUND FLOOR PLAN  ·  FURNITURE LAYOUT",
    )
    _north_arrow(draw, 120, 160)
    _scale_bar(draw, 70, 240)
    _dimension(
        draw,
        origin_x,
        origin_y - 48,
        origin_x + inner_w,
        origin_y - 48,
        "14000",
    )
    _dimension(
        draw,
        origin_x - 48,
        origin_y,
        origin_x - 48,
        origin_y + inner_h,
        "10000",
    )
    header = load_font(22, bold=True)
    draw.text((340, 48), "GROUND FLOOR PLAN", fill=INK, font=header)
    draw.text((340, 82), "Unit A  ·  Two-bedroom apartment  ·  CAD 2D", fill=(90, 90, 90), font=load_font(14))
    return image


def render_unit_b() -> Image.Image:
    canvas_width, canvas_height = 2100, 1580
    image = Image.new("RGB", (canvas_width, canvas_height), PAPER)
    draw = ImageDraw.Draw(image)

    origin_x, origin_y = 300, 200
    inner_w, inner_h = 1480, 1040
    exterior = EXTERIOR_WALL

    draw.rectangle(
        [
            origin_x - exterior,
            origin_y - exterior,
            origin_x + inner_w + exterior,
            origin_y + inner_h + exterior,
        ],
        fill=INK,
    )
    draw.rectangle(
        [origin_x, origin_y, origin_x + inner_w, origin_y + inner_h],
        fill=PAPER,
    )

    bedroom_w = 520
    bedroom_h = 460
    bath_h = 300

    draw_vertical_wall(draw, origin_x + bedroom_w, origin_y, bedroom_h + bath_h, INTERIOR_WALL)
    draw_horizontal_wall(draw, origin_x, origin_y + bedroom_h, bedroom_w, INTERIOR_WALL)
    draw_horizontal_wall(draw, origin_x, origin_y + bedroom_h + bath_h, bedroom_w, INTERIOR_WALL)
    draw_vertical_wall(draw, origin_x + 250, origin_y + bedroom_h, bath_h, INTERIOR_WALL)

    _vertical_door(draw, origin_x + bedroom_w, origin_y + 180, 90, INTERIOR_WALL, "e")
    _horizontal_door(draw, origin_y + bedroom_h, origin_x + 80, 80, INTERIOR_WALL, "s")
    _vertical_door(draw, origin_x + 250, origin_y + 520, 80, INTERIOR_WALL, "w")
    _horizontal_door(draw, origin_y + inner_h, origin_x + 1040, 110, exterior, "n")

    draw_window_horizontal(draw, origin_x + 80, origin_y, 200, exterior)
    draw_window_horizontal(draw, origin_x + 300, origin_y, 160, exterior)
    draw_window_horizontal(draw, origin_x + 640, origin_y, 260, exterior)
    draw_window_horizontal(draw, origin_x + 1100, origin_y, 280, exterior)
    draw_window_vertical(draw, origin_x + inner_w, origin_y + 80, 220, exterior)
    draw_window_vertical(draw, origin_x + inner_w, origin_y + 420, 280, exterior)
    draw_window_horizontal(draw, origin_x + 620, origin_y + inner_h, 280, exterior)
    draw_window_vertical(draw, origin_x, origin_y + 80, 180, exterior)
    draw_window_vertical(draw, origin_x, origin_y + 800, 140, exterior)

    paste_furniture(image, "bed", origin_x + 150, origin_y + 36)
    paste_furniture(image, "bedside_cupboard", origin_x + 92, origin_y + 36)
    paste_furniture(image, "bedside_cupboard", origin_x + 360, origin_y + 36)
    paste_furniture(image, "wardrobe", origin_x + 28, origin_y + 220)
    paste_furniture(image, "chair", origin_x + 420, origin_y + 360)

    paste_furniture(image, "bathtub", origin_x + 20, origin_y + 484)
    paste_furniture(image, "toilet", origin_x + 200, origin_y + 490)
    paste_furniture(image, "sink", origin_x + 24, origin_y + 680)

    paste_furniture(image, "table", origin_x + 300, origin_y + 800)
    paste_furniture(image, "chair", origin_x + 328, origin_y + 748)
    paste_furniture(image, "cabinet", origin_x + 300, origin_y + 900)

    paste_furniture(image, "sofa", origin_x + 620, origin_y + 80, rotation=90)
    paste_furniture(image, "table", origin_x + 740, origin_y + 150)
    paste_furniture(image, "tv_cabinet", origin_x + 900, origin_y + 40)
    paste_furniture(image, "dining_table", origin_x + 900, origin_y + 420)
    paste_furniture(image, "chair", origin_x + 954, origin_y + 368)
    paste_furniture(image, "chair", origin_x + 954, origin_y + 518)
    paste_furniture(image, "chair", origin_x + 848, origin_y + 444)
    paste_furniture(image, "chair", origin_x + 1060, origin_y + 444)

    paste_furniture(image, "cabinet", origin_x + 1180, origin_y + 80)
    paste_furniture(image, "cabinet", origin_x + 1340, origin_y + 80)
    paste_furniture(image, "stove", origin_x + 1220, origin_y + 140)
    paste_furniture(image, "sink", origin_x + 1320, origin_y + 140)
    paste_furniture(image, "refrigerator", origin_x + 1400, origin_y + 220)
    paste_furniture(image, "dining_table", origin_x + 1180, origin_y + 320)
    paste_furniture(image, "chair", origin_x + 1234, origin_y + 268)
    paste_furniture(image, "chair", origin_x + 1234, origin_y + 418)

    _label(draw, "BEDROOM", origin_x + 260, origin_y + 280)
    _muted_label(draw, "17.9 m²", origin_x + 260, origin_y + 304)
    _label(draw, "BATH", origin_x + 125, origin_y + 600, 16)
    _muted_label(draw, "5.6 m²", origin_x + 125, origin_y + 622)
    _label(draw, "STUDY", origin_x + 385, origin_y + 860, 16)
    _muted_label(draw, "6.1 m²", origin_x + 385, origin_y + 882)
    _label(draw, "LIVING", origin_x + 720, origin_y + 360)
    _muted_label(draw, "open plan", origin_x + 720, origin_y + 384)
    _label(draw, "DINING", origin_x + 980, origin_y + 620, 16)
    _label(draw, "KITCHEN", origin_x + 1320, origin_y + 560)
    _muted_label(draw, "island + run", origin_x + 1320, origin_y + 584)

    _title_block(
        draw,
        canvas_width,
        canvas_height,
        "RESIDENTIAL UNIT B",
        "GROUND FLOOR PLAN  ·  OPEN PLAN FURNITURE LAYOUT",
    )
    _north_arrow(draw, 120, 150)
    _scale_bar(draw, 70, 230)
    _dimension(
        draw,
        origin_x,
        origin_y - 48,
        origin_x + inner_w,
        origin_y - 48,
        "14800",
    )
    _dimension(
        draw,
        origin_x - 52,
        origin_y,
        origin_x - 52,
        origin_y + inner_h,
        "10400",
    )
    header = load_font(22, bold=True)
    draw.text((300, 42), "GROUND FLOOR PLAN", fill=INK, font=header)
    draw.text((300, 76), "Unit B  ·  Open-plan apartment  ·  CAD 2D", fill=(90, 90, 90), font=load_font(14))
    return image


RENDERERS = {
    "unit_a": render_unit_a,
    "unit_b": render_unit_b,
}


def render_plan(plan_id: str) -> Image.Image:
    if plan_id not in RENDERERS:
        raise KeyError(f"Unknown plan id: {plan_id}")
    return RENDERERS[plan_id]()

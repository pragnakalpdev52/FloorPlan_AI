"""Floor-plan detection pipeline backed by a single Roboflow-hosted model."""

from __future__ import annotations

import time
from collections import defaultdict

import cv2
import numpy as np
from PIL import Image

from engine.roboflow_detector import RoboflowFloorPlanDetector, load_roboflow_api_key


class FloorPlanPipeline:
    def __init__(self, roboflow_api_key: str | None = None) -> None:
        api_key = roboflow_api_key if roboflow_api_key is not None else load_roboflow_api_key()
        self.roboflow = RoboflowFloorPlanDetector(api_key=api_key, confidence=0.2)
        self.engine_name = "roboflow"

    def detect(self, pil_image: Image.Image) -> dict:
        started = time.perf_counter()
        rgb = pil_image.convert("RGB")
        width, height = rgb.size

        objects: list[dict] = []
        roboflow_error = None
        if self.roboflow.enabled:
            try:
                objects = self.roboflow.detect(rgb)
            except Exception as exc:
                roboflow_error = str(exc)
                objects = []
        else:
            roboflow_error = "Roboflow API key is not configured."

        objects = _nms(objects, 0.4)
        objects.sort(key=lambda item: (not item.get("is_furniture", False), -item["confidence"]))
        for index, item in enumerate(objects, start=1):
            item["id"] = index

        doors = [item for item in objects if item["class_name"] == "door"]
        windows = [item for item in objects if item["class_name"] == "window"]
        furniture_count = sum(1 for item in objects if item.get("is_furniture"))

        summary: dict[str, int] = defaultdict(int)
        for item in objects:
            summary[item["class_name"]] += 1

        annotated = render_pipeline_overlay(rgb, objects)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return {
            "objects": objects,
            "rooms": [],
            "summary": dict(summary),
            "object_count": len(objects),
            "furniture_count": furniture_count,
            "door_count": len(doors),
            "window_count": len(windows),
            "room_count": 0,
            "roboflow_count": len(objects),
            "roboflow_model": self.roboflow.model_id if self.roboflow.enabled else None,
            "roboflow_error": roboflow_error,
            "image_width": width,
            "image_height": height,
            "inference_ms": elapsed_ms,
            "engine": self.engine_name,
            "plan_style": None,
            "annotated_image": annotated,
        }


def _iou(box_a: list[int], box_b: list[int]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter = max(0, min(ax2, bx2) - max(ax1, bx1)) * max(0, min(ay2, by2) - max(ay1, by1))
    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union = area_a + area_b - inter
    return 0.0 if union <= 0 else inter / union


def _nms(detections: list[dict], iou_threshold: float) -> list[dict]:
    ordered = sorted(detections, key=lambda item: item["confidence"], reverse=True)
    kept: list[dict] = []
    for candidate in ordered:
        if any(_iou(candidate["bbox"], selected["bbox"]) >= iou_threshold for selected in kept):
            continue
        kept.append(candidate)
    return kept


def render_pipeline_overlay(rgb: Image.Image, objects: list[dict]) -> Image.Image:
    base = cv2.cvtColor(np.array(rgb.convert("RGB")), cv2.COLOR_RGB2BGR)
    blended = base.copy()

    for item in objects:
        color = (46, 168, 122) if item.get("is_furniture") else (220, 140, 40)
        thickness = 2
        caption = f"{item['label']} {item['confidence'] * 100:.0f}%"
        x1, y1, x2, y2 = item["bbox"]
        cv2.rectangle(blended, (x1, y1), (x2, y2), color, thickness)
        text_size, _baseline = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        text_w, text_h = text_size
        label_y = max(0, y1 - text_h - 8)
        cv2.rectangle(
            blended,
            (x1, label_y),
            (min(x1 + text_w + 8, blended.shape[1] - 1), label_y + text_h + 8),
            color,
            thickness=-1,
        )
        cv2.putText(
            blended,
            caption,
            (x1 + 4, label_y + text_h + 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
    return Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))

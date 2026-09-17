"""Native-resolution photographic introductions for V4, no fabricated imagery."""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from tools.uqam_video_review import cover_image

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT.parents[1] / "assets/uqam_promo"
FONT = ROOT / "assets/fonts/NotoSans-Regular.ttf"
BOLD = ROOT / "assets/fonts/NotoSans-Bold.ttf"
PHOTO_SPECS = {
    "v4_01_opening": {
        "filename": "president_kennedy.jpg", "focal": (0.5, 0.50),
        "credit": "Photo UQAM", "heading": "Mathématiques à l'UQAM",
        "detail": "Pavillon Président-Kennedy · Montréal", "default_end": 6.0,
    },
    "v4_12_conclusion": {
        "filename": "research_math.jpg", "focal": (0.5, 0.48),
        "credit": "Photo : Nathalie St-Pierre · UQAM",
        "heading": "Un milieu pour explorer les mathématiques",
        "detail": "Pôle mathématique · Complexe des sciences Pierre-Dansereau",
        "default_end": 6.0,
    },
}


def end_time(scene_id: str, actions: dict | None = None) -> float:
    spec = PHOTO_SPECS.get(scene_id)
    if not spec:
        return 0.0
    if actions and "photo_intro" in actions:
        value = actions["photo_intro"]
        return float(value.end if hasattr(value, "end") else value[1])
    return spec["default_end"]


@lru_cache(maxsize=8)
def photo_frame(scene_id: str, width: int, height: int) -> np.ndarray:
    spec = PHOTO_SPECS[scene_id]
    image = cover_image(ASSETS / spec["filename"], (width, height), spec["focal"])
    # Local opaque panels protect contrast without dimming the entire building.
    draw = ImageDraw.Draw(image)
    scale = width / 1280
    def font(size, bold=False):
        return ImageFont.truetype(str(BOLD if bold else FONT), round(size * scale))
    heading_font, detail_font, credit_font = font(36, True), font(19), font(17)
    x, y = round(60 * scale), round(330 * scale)
    heading, detail = spec["heading"], spec["detail"]
    lengths = [draw.textlength(heading, font=heading_font), draw.textlength(detail, font=detail_font)]
    if max(lengths) > width - 150 * scale:
        raise ValueError("Photographic title exceeds safe horizontal area")
    draw.rectangle((x - 18 * scale, y - 16 * scale, x + max(lengths) + 18 * scale, y + 102 * scale), fill="#18212B")
    draw.text((x, y), heading, font=heading_font, fill="white")
    draw.text((x, y + 62 * scale), detail, font=detail_font, fill="white")
    credit = spec["credit"]
    length = draw.textlength(credit, font=credit_font)
    right, top = width - 35 * scale, 30 * scale
    draw.rectangle((right - length - 24 * scale, top, right, top + 36 * scale), fill="#18212B")
    draw.text((right - length - 12 * scale, top + 6 * scale), credit, font=credit_font, fill="white")
    return np.array(image, dtype=np.uint8)


def composite(scene_id: str, t: float, frame: np.ndarray, actions=None) -> np.ndarray:
    end = end_time(scene_id, actions)
    if end <= 0 or t >= end:
        return frame
    photo = photo_frame(scene_id, frame.shape[1], frame.shape[0])
    fade = min(0.5, end / 3)
    if t <= end - fade:
        return photo.copy()
    alpha = max(0.0, min(1.0, (end - t) / fade))
    return np.rint(photo.astype(np.float32) * alpha + frame.astype(np.float32) * (1 - alpha)).astype(np.uint8)


def credit_records(scene_id: str, start: float, actions=None) -> list[dict]:
    if scene_id not in PHOTO_SPECS:
        return []
    spec = PHOTO_SPECS[scene_id]
    return [{"filename": spec["filename"], "start": start,
             "end": start + end_time(scene_id, actions),
             "displayed_credit": spec["credit"], "placement": "upper-right opaque panel",
             "crop_focal_point": list(spec["focal"]), "context": spec["detail"]}]

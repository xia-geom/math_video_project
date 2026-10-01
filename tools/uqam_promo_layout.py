"""Photo placement and actual-object checks shared by the two UQAM capsules."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from manim import ImageMobject, config
from PIL import Image, ImageOps

from tools.uqam_video_review import cover_image, crop_box


def mark_copy(obj, text: str, *, role: str = "message"):
    obj.uqam_copy = text
    obj.uqam_copy_role = role
    return obj


def placed_photo(path: Path, width: float, height: float, focal=(0.5, 0.5)):
    """Check useful source pixels against 1080p placement, then crop, never stretch."""
    target = (round(width / config.frame_width * 1920), round(height / config.frame_height * 1080))
    with Image.open(path) as source:
        size = ImageOps.exif_transpose(source).size
    left, top, right, bottom = crop_box(size, target, focal)
    enlargement = max(target[0] / (right - left), target[1] / (bottom - top))
    if enlargement > 1.05:
        raise ValueError(f"Photo would be enlarged {enlargement:.2f} times at 1080p: {path.name}")
    pixels = cover_image(path, target, focal)
    photo = ImageMobject(np.array(pixels))
    photo.stretch_to_fit_width(width).stretch_to_fit_height(height)
    photo.uqam_photo = path.name
    return photo


def check_copy_layout(roots, context: str) -> dict:
    """Inspect rendered text/raster bounds, including panel containment and collisions."""
    labels, seen = [], set()
    for root in roots:
        for obj in root.get_family():
            if id(obj) in seen or not hasattr(obj, "uqam_copy"):
                continue
            seen.add(id(obj))
            box = [
                float(obj.get_left()[0]),
                float(obj.get_right()[0]),
                float(obj.get_bottom()[1]),
                float(obj.get_top()[1]),
            ]
            role = getattr(obj, "uqam_copy_role", "message")
            safe = (-config.frame_width / 2 + 0.48, config.frame_width / 2 - 0.48, -2.30, 3.30)
            if role in {"credit", "preview"}:
                safe = (
                    -config.frame_width / 2 + 0.12,
                    config.frame_width / 2 - 0.12,
                    -config.frame_height / 2 + 0.12,
                    config.frame_height / 2 - 0.12,
                )
            if not all(math.isfinite(x) for x in box):
                raise ValueError(f"Nonfinite text bounds: {context}: {obj.uqam_copy}")
            if box[0] < safe[0] or box[1] > safe[1] or box[2] < safe[2] or box[3] > safe[3]:
                raise ValueError(f"Text outside safe area: {context}: {obj.uqam_copy}: {box}")
            panel = getattr(obj, "uqam_containing_panel", None)
            if panel is not None:
                p = [
                    panel.get_left()[0] + 0.18,
                    panel.get_right()[0] - 0.18,
                    panel.get_bottom()[1] + 0.16,
                    panel.get_top()[1] - 0.16,
                ]
                if box[0] < p[0] or box[1] > p[1] or box[2] < p[2] or box[3] > p[3]:
                    raise ValueError(f"Copy outside card padding: {context}: {obj.uqam_copy}")
            labels.append({"text": obj.uqam_copy, "role": role, "box": box})
    for index, a in enumerate(labels):
        for b in labels[index + 1 :]:
            x1, x2, y1, y2 = a["box"]
            u1, u2, v1, v2 = b["box"]
            if min(x2, u2) - max(x1, u1) > 0.025 and min(y2, v2) - max(y1, v1) > 0.025:
                raise ValueError(f"Overlapping copy: {context}: {a['text']} / {b['text']}")
    if not labels:
        raise ValueError(f"No visible copy was checked: {context}")
    return {"context": context, "labels": labels}


def photo_canvas(
    path: Path,
    *,
    width: float,
    height: float,
    center=(0.0, 0.0),
    focal=(0.5, 0.5),
    veil=0.0,
    veil_color="black",
):
    """Precompose only the photograph, not the text, for a true pixel crossfade.

    Animating a photo and a translucent veil separately changes the effective
    opacity twice and causes a brightness pulse. One opaque background prevents it.
    """
    if not 0 <= veil <= 1:
        raise ValueError("Veil opacity must be between zero and one")
    photo = placed_photo(path, width, height, focal)
    pixels = Image.fromarray(photo.pixel_array).convert("RGB")
    if veil:
        pixels = Image.blend(pixels, Image.new("RGB", pixels.size, veil_color), veil)
    canvas = Image.new("RGB", (1920, 1080), "white")
    x = round(960 + center[0] / config.frame_width * 1920 - pixels.width / 2)
    y = round(540 - center[1] / config.frame_height * 1080 - pixels.height / 2)
    canvas.paste(pixels, (x, y))
    result = ImageMobject(np.array(canvas))
    result.stretch_to_fit_width(config.frame_width).stretch_to_fit_height(config.frame_height)
    result.uqam_photo = path.name
    return result

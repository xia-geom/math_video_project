"""Small deterministic review primitives; never imply human approval."""
from __future__ import annotations

import math
import re
from pathlib import Path

from PIL import Image, ImageOps


def crop_box(source_size: tuple[int, int], target_size: tuple[int, int], focal=(0.5, 0.5)) -> tuple[int, int, int, int]:
    """Aspect-preserving cover crop around an explicit normalized focal point."""
    width, height = source_size
    target_width, target_height = target_size
    if min(width, height, target_width, target_height) <= 0:
        raise ValueError("Image dimensions must be positive")
    if len(focal) != 2 or any(not math.isfinite(v) or not 0 <= v <= 1 for v in focal):
        raise ValueError("Focal point must contain two finite values in [0,1]")
    ratio = target_width / target_height
    crop_width = min(width, round(height * ratio))
    crop_height = min(height, round(width / ratio))
    left = max(0, min(width - crop_width, round(focal[0] * width - crop_width / 2)))
    top = max(0, min(height - crop_height, round(focal[1] * height - crop_height / 2)))
    return left, top, left + crop_width, top + crop_height


def cover_image(path: Path, size: tuple[int, int], focal=(0.5, 0.5)) -> Image.Image:
    with Image.open(path) as source:
        source = ImageOps.exif_transpose(source).convert("RGB")
        return source.crop(crop_box(source.size, size, focal)).resize(size, Image.Resampling.LANCZOS)


def contrast_ratio(first: str, second: str) -> float:
    def luminance(value):
        channels = [int(value.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
        return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))
    low, high = sorted((luminance(first), luminance(second)))
    return (high + 0.05) / (low + 0.05)


def validate_subtitles(path: Path, duration: float) -> dict:
    """Strict SRT structure plus review warnings, not a listening certificate."""
    if not math.isfinite(duration) or duration <= 0:
        raise RuntimeError("Video duration must be finite and positive")
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise RuntimeError("SRT contains no timed captions")
    time_pattern = r"(\d{2,}):(\d{2}):(\d{2}),(\d{3})"
    pattern = re.compile(time_pattern + r" --> " + time_pattern)
    previous_end = 0.0
    intervals, warnings = [], []
    for index, block in enumerate(re.split(r"\r?\n\s*\r?\n", text), 1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0].strip() != str(index):
            raise RuntimeError(f"Malformed SRT cue or nonsequential index: {index}")
        match = pattern.fullmatch(lines[1].strip())
        if not match:
            raise RuntimeError(f"Malformed SRT timecode: cue {index}")
        values = list(map(int, match.groups()))
        if any(values[i] >= 60 for i in (1, 2, 5, 6)):
            raise RuntimeError(f"Invalid SRT minute/second field: cue {index}")
        start = values[0] * 3600 + values[1] * 60 + values[2] + values[3] / 1000
        end = values[4] * 3600 + values[5] * 60 + values[6] + values[7] / 1000
        if end <= start or start < previous_end - 0.02 or end > duration + 0.25:
            raise RuntimeError(f"Invalid, overlapping or out-of-range SRT interval: cue {index}")
        caption = " ".join(lines[2:]).strip()
        if not caption or re.search(r"<[^>]+>", caption):
            raise RuntimeError(f"Empty caption or SSML/HTML markup: cue {index}")
        cps = len(caption) / (end - start)
        if len(lines[2:]) > 2 or any(len(line) > 42 for line in lines[2:]):
            warnings.append({"cue": index, "issue": "line_length", "limit": "2 lines, 42 characters/line"})
        if cps > 20:
            warnings.append({"cue": index, "issue": "reading_speed", "characters_per_second": round(cps, 2)})
        intervals.append((start, end))
        previous_end = end
    return {"caption_count": len(intervals), "first_caption_seconds": intervals[0][0],
            "last_caption_seconds": intervals[-1][1], "reading_warnings": warnings,
            "audio_alignment": "pending listening review", "human_review": "pending"}


def photo_credit_inventory(assets: dict, shots: list[dict]) -> list[dict]:
    records = []
    for asset in assets.get("assets", []):
        if asset.get("kind") != "image":
            continue
        occurrences = [shot for shot in shots if shot.get("filename") == asset["filename"]]
        records.append({"filename": asset["filename"], "expected_credit": asset.get("credit"),
                        "source_page": asset.get("source_page"), "rights_status": asset.get("rights_status"),
                        "occurrences": occurrences,
                        "description_credit": asset.get("credit"),
                        "institutional_approval": "not inferred"})
    return records


def review_times(shots: list[dict], duration: float, fps: float = 60.0) -> list[float]:
    times = {0.0, max(0.0, duration - 1 / fps)}
    for shot in shots:
        start, end = float(shot["start"]), float(shot["end"])
        times.add((start + end) / 2)
        for boundary in (start, end):
            times.update((boundary - 1 / fps, boundary, boundary + 1 / fps))
    return sorted({round(max(0.0, min(duration - 1 / fps, t)), 6) for t in times})

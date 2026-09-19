"""Small, dependency-free contract for the third UQAM promotion film."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCENE_PATH = HERE / "bac_sciences_ouvertures_fr_scene.py"


def _flat(text: str) -> str:
    return " ".join(text.split())


def load_project(path: Path | None = None) -> dict:
    data = json.loads((path or HERE / "project.json").read_text(encoding="utf-8"))
    validate_project(data)
    return data


def validate_project(data: dict) -> None:
    if data["schema_version"] != 3:
        raise ValueError("Unsupported project schema")
    if data.get("visual_concept") != "photo_led_high_resolution":
        raise ValueError("This clip must keep the audited high-resolution photo-led concept")
    expected_assets = {"campus", "math_activity", "math_hub", "student_life"}
    if set(data["assets"]) != expected_assets:
        raise ValueError("Expected the four audited UQAM photographs")
    if [b["id"] for b in data["beats"]] != ["hook", "major", "openings", "horizons"]:
        raise ValueError("Expected the four ordered storyboard beats")

    durations = [float(b["seconds"]) for b in data["beats"]]
    if not all(math.isfinite(n) and n > 0 for n in durations):
        raise ValueError("Beat durations must be finite and positive")
    if abs(sum(durations) - data["target_seconds"]) > 1e-6:
        raise ValueError("Storyboard timings must add up to the target")

    backgrounds = [beat["background"] for beat in data["beats"]]
    if len(set(backgrounds)) != len(backgrounds):
        raise ValueError("Each beat must use a distinct photograph")

    registered_pages = set(data["source"]["claim_pages"])
    registered_pages.update(data["source"].get("context_pages", []))
    registered_pages.update(data["source"].get("resource_pages", []))
    for beat in data["beats"]:
        if _flat(beat["caption"]) != _flat(beat["text"]):
            raise ValueError("Captions must match spoken text exactly")
        if any(mark in beat["caption"] for mark in ("<", ">")):
            raise ValueError("No SSML in captions")
        if len(beat["caption"].splitlines()) > 2:
            raise ValueError("Use at most two subtitle lines")
        if any(len(line) > 52 for line in beat["caption"].splitlines()):
            raise ValueError("Subtitle line is too long")
        screen = beat.get("screen", [])
        if not 1 <= len(screen) <= 3:
            raise ValueError("Each beat must use one to three on-screen lines")
        if any(len(line) > 38 for line in screen):
            raise ValueError("Sparse on-screen copy is too long")
        if beat["background"] not in data["assets"]:
            raise ValueError("Every beat must use a registered UQAM photograph")
        if not set(beat["source_pages"]).issubset(registered_pages):
            raise ValueError("An on-screen claim has no registered source page")

    narration = " ".join(beat["text"].lower() for beat in data["beats"])
    if "certificat" in narration:
        raise ValueError("The revised 20-second capsule must not mention certificates")
    if "bac en sciences" in narration or "baccalauréat" in narration:
        raise ValueError("The shortened capsule must not imply the omitted cumulative-bachelor mechanism")


def validate_assets(data: dict) -> dict[str, Path]:
    """Require the exact audited UQAM photographs and return their paths."""
    resolved: dict[str, Path] = {}
    for key, asset in data["assets"].items():
        path = (HERE / asset["path"]).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Missing UQAM photograph: {path}")
        blob = path.read_bytes()
        if not blob.startswith(b"\xff\xd8\xff"):
            raise ValueError(f"UQAM asset is not a JPEG: {path}")
        digest = hashlib.sha256(blob).hexdigest()
        if digest != asset["sha256"]:
            raise ValueError(f"UQAM asset hash mismatch: {path}")
        if int(asset["width"]) < 1600 or int(asset["height"]) < 900:
            raise ValueError(f"Photo is too small for a 1080p full-screen treatment: {path}")
        if not asset.get("credit") or not asset.get("source_url"):
            raise ValueError(f"Photo source/credit metadata missing: {path}")
        resolved[key] = path
    return resolved


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    seconds, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def write_srt(timeline: list[dict], destination: Path) -> None:
    previous_end = 0.0
    entries = []
    for index, beat in enumerate(timeline, start=1):
        start, end = beat["start"], beat["end"]
        if start < previous_end - 0.001 or end <= start:
            raise ValueError("Invalid or overlapping subtitle cue")
        entries.append(
            f"{index}\n{srt_time(start)} --> {srt_time(end)}\n{beat['caption']}\n"
        )
        previous_end = end
    destination.write_text("\n".join(entries), encoding="utf-8")

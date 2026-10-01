"""Data, image and measured-time contracts for the 30-second UQAM capsule."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageOps

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
    if data["schema_version"] != 4:
        raise ValueError("Unsupported project schema")
    if data.get("visual_concept") != "photo_led_editorial_pathway":
        raise ValueError("Expected the editorial pathway treatment")
    if [b["id"] for b in data["beats"]] != ["hook", "major", "openings", "degree", "horizons"]:
        raise ValueError("Expected the five ordered pathway beats")
    lower, upper = data["accepted_duration_seconds"]
    if not 0 < lower <= data["target_seconds"] <= upper <= 30:
        raise ValueError("The complete capsule must fit within 30 seconds")
    if not 2 <= data["final_hold_seconds"] < data["beats"][-1]["seconds"]:
        raise ValueError("Reserve two seconds after the final spoken sentence")
    durations = [float(b["seconds"]) for b in data["beats"]]
    if not all(math.isfinite(n) and n > 0 for n in durations):
        raise ValueError("Beat durations must be finite and positive")
    if abs(sum(durations) - data["target_seconds"]) > 1e-6:
        raise ValueError("Storyboard timings must add up to the target")
    registered = set(data["source"]["claim_pages"] + data["source"].get("resource_pages", []))
    previous = None
    for beat in data["beats"]:
        if not 0 < beat["min_seconds"] <= beat["seconds"]:
            raise ValueError("Invalid minimum reading time")
        if _flat(beat["caption"]) != _flat(beat["text"]):
            raise ValueError("Captions must match spoken text exactly")
        if any(mark in beat["caption"] for mark in ("<", ">")):
            raise ValueError("No SSML in captions")
        if len(beat["caption"].splitlines()) > 2 or any(len(x) > 52 for x in beat["caption"].splitlines()):
            raise ValueError("Use at most two subtitle lines, at most 52 characters each")
        if not 1 <= len(beat["screen"]) <= 3 or any(len(x) > 38 for x in beat["screen"]):
            raise ValueError("Use one to three short on-screen message lines")
        key = beat["background"]
        if beat["layout"] not in {"full_bleed", "split", "pathway"}:
            raise ValueError("Unknown editorial layout")
        if beat["layout"] == "pathway":
            if key is not None:
                raise ValueError("The pathway is a graphic, not a misleading stock photo")
        elif key not in data["assets"]:
            raise ValueError("Every photograph must be registered")
        if beat.get("keep_background") and (
            previous is None or (previous["background"], previous["layout"]) != (key, beat["layout"])
        ):
            raise ValueError("Only consecutive identical backgrounds may be retained")
        if not set(beat["source_pages"]).issubset(registered):
            raise ValueError("An on-screen claim has no registered source page")
        previous = beat
    narration = " ".join(b["text"].casefold() for b in data["beats"])
    for required in ("majeure", "certificat", "mineure", "compatible", "baccalauréat en sciences"):
        if required not in narration:
            raise ValueError(f"Missing part of the complete degree pathway: {required}")
    for rejected in ("classroom_math.jpg", "research_math.jpg"):
        if any(asset["path"].endswith(rejected) for asset in data["assets"].values()):
            raise ValueError("A rejected examination/group photograph returned")


def allocate_slots(data: dict, speech_seconds: list[float], fps: float) -> list[float]:
    """Fit measured speech and final reading hold; never truncate or accelerate audio."""
    if len(speech_seconds) != len(data["beats"]) or not math.isfinite(fps) or fps <= 0:
        raise ValueError("Invalid speech durations or frame rate")
    if not all(math.isfinite(x) and x > 0 for x in speech_seconds):
        raise ValueError("Speech duration must be finite and positive")
    minima = [max(b["min_seconds"], s + 0.12) for b, s in zip(data["beats"], speech_seconds)]
    minima[-1] = max(minima[-1], speech_seconds[-1] + data["final_hold_seconds"])
    frames = [math.ceil(n * fps) for n in minima]
    maximum = math.floor(data["accepted_duration_seconds"][1] * fps)
    target = max(round(data["target_seconds"] * fps), sum(frames))
    if target > maximum:
        raise ValueError("Measured narration plus readable holds exceeds 30 seconds; shorten the script, never cut the voice")
    slack = target - sum(frames)
    weights = [max(0, round(b["seconds"] * fps) - n) for b, n in zip(data["beats"], frames)]
    total = sum(weights)
    additions = [math.floor(slack * w / total) if total else 0 for w in weights]
    additions[-1] += slack - sum(additions)
    return [(n + a) / fps for n, a in zip(frames, additions)]


def validate_assets(data: dict) -> dict[str, Path]:
    """Check exact bytes AND decoded dimensions; low-resolution photos are panel-only."""
    resolved = {}
    for key, asset in data["assets"].items():
        path = (HERE / asset["path"]).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Missing UQAM photo; run the shared asset fetcher: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != asset["sha256"]:
            raise ValueError(f"UQAM asset hash mismatch: {path}")
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = ImageOps.exif_transpose(image).size
        if (width, height) != (asset["width"], asset["height"]):
            raise ValueError(f"Declared dimensions differ from decoded pixels: {path}")
        if asset.get("placement", "full_bleed") == "full_bleed":
            if min(width / 1920, height / 1080) < 1:
                raise ValueError(f"Photo is too small for full-screen 1080p: {path}")
        elif width < 900 or height < 600:
            raise ValueError(f"Photo is too small even for the bounded panel: {path}")
        if not asset.get("credit") or not asset.get("source_url"):
            raise ValueError(f"Missing source or credit: {path}")
        resolved[key] = path
    return resolved


def srt_time(seconds: float) -> str:
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("Invalid subtitle time")
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    seconds, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def write_srt(timeline: list[dict], destination: Path) -> None:
    previous_end, entries = 0.0, []
    for index, beat in enumerate(timeline, 1):
        start, end = beat["start"], beat.get("caption_end", beat["end"])
        if not all(math.isfinite(x) for x in (start, end)) or start < previous_end - 0.001 or end <= start:
            raise ValueError("Invalid or overlapping subtitle cue")
        entries.append(f"{index}\n{srt_time(start)} --> {srt_time(end)}\n{beat['caption']}\n")
        previous_end = end
    destination.write_text("\n".join(entries), encoding="utf-8")

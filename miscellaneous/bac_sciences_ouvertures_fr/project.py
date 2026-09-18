"""Data, source-photo, and caption contracts for the third UQAM film."""
from __future__ import annotations

import hashlib
import json
import math
import os
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
    if data["schema_version"] != 2 or data["visual_concept"] != "photo_led_sparse":
        raise ValueError("Unsupported project schema or visual concept")
    if set(data["assets"]) != {"students", "building"}:
        raise ValueError("Expected only the two audited slide photographs")
    if [b["id"] for b in data["beats"]] != ["hook", "major", "certificate", "degree"]:
        raise ValueError("Expected the four ordered storyboard beats")
    durations = [float(b["seconds"]) for b in data["beats"]]
    if not all(math.isfinite(n) and n > 0 for n in durations):
        raise ValueError("Beat durations must be finite and positive")
    if abs(sum(durations) - data["target_seconds"]) > 1e-6:
        raise ValueError("Storyboard timings must add up to the target")
    pages = set(data["source"]["visual_pages"] + data["source"]["claim_pages"])
    pages.update(data["source"].get("resource_pages", []))
    for beat in data["beats"]:
        if _flat(beat["caption"]) != _flat(beat["text"]):
            raise ValueError("Captions must match spoken text exactly")
        if any(mark in beat["caption"] for mark in ("<", ">")):
            raise ValueError("No SSML in captions")
        if len(beat["caption"].splitlines()) > 2:
            raise ValueError("Use at most two subtitle lines")
        if any(len(line) > 48 for line in beat["caption"].splitlines()):
            raise ValueError("Subtitle line is too long")
        screen = beat.get("screen", [])
        if not 1 <= len(screen) <= 3 or any(len(line) > 38 for line in screen):
            raise ValueError("Sparse on-screen copy is too long")
        if beat["background"] not in data["assets"]:
            raise ValueError("Every beat must use a registered slide photograph")
        if not set(beat["source_pages"]).issubset(pages):
            raise ValueError("Unregistered source page")
        for key in ("minimum_seconds", "tail_seconds"):
            n = float(beat[key])
            if not math.isfinite(n) or n < 0:
                raise ValueError(f"Invalid {key}")
        if not 0 < beat["minimum_seconds"] <= beat["seconds"]:
            raise ValueError("Reading minimum exceeds the preferred duration")


def native_asset_directory() -> Path:
    return Path(os.getenv("UQAM_OUVERTURES_SOURCE_ASSETS", str(HERE / "assets/native")))


def inspect_assets(data: dict, *, require_native: bool = False) -> tuple[dict, dict]:
    """Decode and check pixels, not merely JPEG magic bytes and a declared hash."""
    from PIL import Image

    native = native_asset_directory()
    use_native = native.is_dir() and (native / "manifest.json").is_file()
    if require_native and not use_native:
        raise ValueError(
            "Native slide photos required. Run restore_slide_photos.py --pdf ORIGINAL.pdf, "
            "or install the supplied native-photo bundle. The old thumbnails are preview-only."
        )
    if use_native:
        manifest = json.loads((native / "manifest.json").read_text(encoding="utf-8"))
        if manifest["source_pdf_sha256"] != data["source"]["sha256"]:
            raise ValueError("Native photo bundle has the wrong PDF provenance")
    paths, evidence = {}, {}
    for key, legacy in data["assets"].items():
        asset = data["native_assets"][key] if use_native else legacy
        path = native / asset["path"] if use_native else HERE / asset["path"]
        raw = path.read_bytes()
        with Image.open(path) as image:
            image.load()  # Detect truncated/corrupt payloads.
            if list(image.size) != [asset["width"], asset["height"]]:
                raise ValueError(f"Image dimensions differ from manifest: {key}")
            pixels = hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()
        digest = hashlib.sha256(raw).hexdigest()
        expected = asset["pixel_sha256"] if use_native else asset["sha256"]
        if (pixels if use_native else digest) != expected:
            raise ValueError(f"Image integrity mismatch: {key}")
        paths[key] = path
        evidence[key] = {"path": str(path), "sha256": digest, "pixel_sha256": pixels,
                         "width": asset["width"], "height": asset["height"],
                         "enlargement_at_1920px": round(1920 / asset["width"], 3)}
    return paths, {"tier": "native_crop" if use_native else "legacy_thumbnail_preview_only",
                   "native_source_recovered": use_native, "assets": evidence,
                   "warning": None if use_native else "Small legacy images; not an image-quality approval"}


def validate_assets(data: dict, *, require_native: bool = False) -> dict[str, Path]:
    return inspect_assets(data, require_native=require_native)[0]


def srt_time(seconds: float) -> str:
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("Invalid subtitle time")
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    seconds, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def write_srt(timeline: list[dict], destination: Path) -> None:
    previous_end = 0.0
    entries = []
    for index, beat in enumerate(timeline, start=1):
        start = beat.get("speech_start")
        end = beat.get("speech_end")
        start = beat["start"] if start is None else start
        end = beat["end"] if end is None else end
        if not all(math.isfinite(n) for n in (start, end)):
            raise ValueError("Nonfinite subtitle cue")
        if start < previous_end - 0.001 or end <= start:
            raise ValueError("Invalid or overlapping subtitle cue")
        if start < beat["start"] or end > beat["end"] + 0.001:
            raise ValueError("Caption falls outside its scene")
        entries.append(f"{index}\n{srt_time(start)} --> {srt_time(end)}\n{beat['caption']}\n")
        previous_end = end
    destination.write_text("\n".join(entries), encoding="utf-8")

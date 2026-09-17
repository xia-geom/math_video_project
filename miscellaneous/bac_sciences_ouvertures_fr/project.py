"""Small, dependency-free contract for the third UQAM promotion film."""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCENE_PATH = HERE / "bac_sciences_ouvertures_fr_scene.py"


def load_project(path: Path | None = None) -> dict:
    data = json.loads((path or HERE / "project.json").read_text(encoding="utf-8"))
    validate_project(data)
    return data


def validate_project(data: dict) -> None:
    if data["schema_version"] != 1:
        raise ValueError("Unsupported project schema")
    if [b["id"] for b in data["beats"]] != ["hook", "major", "certificate", "degree"]:
        raise ValueError("Expected the four ordered storyboard beats")
    durations = [float(b["seconds"]) for b in data["beats"]]
    if not all(math.isfinite(n) and n > 0 for n in durations):
        raise ValueError("Beat durations must be finite and positive")
    if abs(sum(durations) - data["target_seconds"]) > 1e-6:
        raise ValueError("Storyboard timings must add up to the target")
    for beat in data["beats"]:
        if " ".join(beat["caption"].split()) != " ".join(beat["text"].split()):
            raise ValueError("Captions must match spoken text exactly")
        if any(mark in beat["caption"] for mark in ("<", ">")):
            raise ValueError("No SSML in captions")
        if len(beat["caption"].splitlines()) > 2:
            raise ValueError("Use at most two subtitle lines")
        if any(len(line) > 44 for line in beat["caption"].splitlines()):
            raise ValueError("Subtitle line is too long")
        if not set(beat["source_pages"]).issubset(data["source"]["pdf_pages"]):
            raise ValueError("An on-screen claim has no registered source page")


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

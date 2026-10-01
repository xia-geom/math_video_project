"""Build an explicitly silent preview of the actual promo scene, with measured frames."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import subprocess
import sys
import textwrap
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from manim import config, tempconfig  # noqa: E402

from miscellaneous.bac_math_uqam_fr.bac_math_uqam_fr_scene import (  # noqa: E402
    ASSET_DIR,
    FONT_PATH,
    BacMathUQAMFR,
)
from miscellaneous.bac_math_uqam_fr.promo_beats import NARRATION_BEATS, REVIEW_SECONDS  # noqa: E402
from tools.uqam_video_review import validate_subtitles  # noqa: E402


class SilentPromoReview(BacMathUQAMFR):
    @contextmanager
    def narrate(self, text, *, rate=None):
        clocks = {
            text: seconds
            for name, texts in NARRATION_BEATS.items()
            for text, seconds in zip(texts, REVIEW_SECONDS[name])
        }
        duration = math.ceil(clocks[text] * config.frame_rate) / config.frame_rate
        start = float(self.renderer.time)
        yield SimpleNamespace(duration=duration)
        remaining_frames = round((start + duration - float(self.renderer.time)) * config.frame_rate)
        if remaining_frames > 0:
            self.wait(remaining_frames / config.frame_rate + 1e-8)

    def construct(self):
        self.visual_only = True
        self.construct_film()


def probe(path):
    return json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]
    ))


def timecode(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def preview_subtitles(units, destination):
    """Fixture-only captions; never exported as measured Azure alignment."""
    cues = []
    for unit in units:
        lines = textwrap.wrap(unit["text"], width=42, break_long_words=False, break_on_hyphens=False)
        chunks = ["\n".join(lines[i : i + 2]) for i in range(0, len(lines), 2)]
        weights = [len(chunk) for chunk in chunks]
        start = unit["start"]
        for chunk, weight in zip(chunks, weights):
            end = start + (unit["speech_end"] - unit["start"]) * weight / sum(weights)
            cues.append(f"{len(cues) + 1}\n{timecode(start)} --> {timecode(end)}\n{chunk}\n")
            start = end
    destination.write_text("\n".join(cues), encoding="utf-8")


def source_inventory():
    paths = [
        *Path(__file__).parent.glob("*.py"), ROOT / "tools/uqam_promo_layout.py",
        ROOT / "tools/uqam_video_review.py", ROOT / "tools/tts.py", FONT_PATH,
        ASSET_DIR / "sources.json",
    ]
    paths.extend(ASSET_DIR / name for name in (
        "sciences_biologiques_uqam.jpg", "math_workshop_2019.jpg", "support_students.jpg",
        "bibliotheque_sciences_2026.jpg", "student_welcome_2025.jpg", "montreal_skyline_2026.jpg",
    ))
    return {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(set(paths))}


def build_visual_preview(output: Path, quality="ql"):
    hashes_before = source_inventory()
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    timeline_path = output / "timeline.json"
    previous = os.environ.get("UQAM_TIMELINE_PATH")
    os.environ["UQAM_TIMELINE_PATH"] = str(timeline_path)
    width, height, fps = {"ql": (854, 480, 15), "qm": (1280, 720, 30), "qh": (1920, 1080, 60)}[quality]
    try:
        with tempconfig({
            "media_dir": str(output / "media"), "output_file": "bac_math_uqam_fr_silent_preview",
            "pixel_width": width, "pixel_height": height, "frame_rate": fps,
            "disable_caching": True, "preview": False, "write_to_movie": True,
        }):
            scene = SilentPromoReview()
            scene.render()
            raw = Path(scene.renderer.file_writer.movie_file_path)
    finally:
        if previous is None:
            os.environ.pop("UQAM_TIMELINE_PATH", None)
        else:
            os.environ["UQAM_TIMELINE_PATH"] = previous
    if any(s["codec_type"] == "audio" for s in probe(raw)["streams"]):
        raise RuntimeError("Silent review unexpectedly contains audio")
    video = output / "bac_math_uqam_fr_silent_preview.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-c", "copy", "-movflags", "+faststart", str(video)], check=True)
    timeline = json.loads(timeline_path.read_text())
    info = probe(video)
    duration = float(info["format"]["duration"])
    if not 60 <= duration <= 90 or abs(duration - timeline["duration"]) > 0.15:
        raise RuntimeError("Encoded promo duration differs from its checked timeline or format")
    subtitles = output / "bac_math_uqam_fr_preview_captions.srt"
    preview_subtitles(timeline["speech_units"], subtitles)
    caption_check = validate_subtitles(subtitles, duration)
    burned = output / "bac_math_uqam_fr_silent_preview_subtitled.mp4"
    style = "FontName=Roboto,FontSize=18,Alignment=2,MarginV=14,BorderStyle=3,Outline=0,Shadow=0,PrimaryColour=&H00FFFFFF,BackColour=&H80000000"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", video.name,
        "-vf", f"subtitles={subtitles.name}:force_style='{style}'", "-c:v", "libx264",
        "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", burned.name,
    ], cwd=output, check=True)
    frames = output / "frames"
    frames.mkdir()
    samples = []
    for state in timeline["states"]:
        samples.append(((state["start"] + state["end"]) / 2, state["state"]))
        if state["start"] > 0.8:
            samples.append((state["start"] - 0.38, state["state"] + "_transition"))
    for index, (timestamp, name) in enumerate(sorted(samples)):
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.3f}", "-i", str(video),
            "-frames:v", "1", "-update", "1", str(frames / f"{index:02d}_{name}.jpg"),
        ], check=True)
    if source_inventory() != hashes_before:
        raise RuntimeError("Sources changed during the preview render")
    report = {
        "source_sha256": hashes_before,
        "font_sha256": hashlib.sha256(FONT_PATH.read_bytes()).hexdigest(),
        "manim_version": importlib.metadata.version("manim"), "mode": "visual_only_no_audio",
        "voice": None, "duration_seconds": duration, "quality": quality, "subtitles": caption_check,
        "subtitle_alignment": "preview_fixtures_only", "layout_states_checked": len(timeline["layout"]),
        "video_sha256": hashlib.sha256(video.read_bytes()).hexdigest(), "visual_inspection": "pending",
        "listening_review": "not_performed", "release_ready": False, "photo_credits": timeline["shots"],
    }
    (output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--quality", choices=("ql", "qm", "qh"), default="ql")
    args = parser.parse_args()
    build_visual_preview(args.output, args.quality)


if __name__ == "__main__":
    main()

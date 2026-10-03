#!/usr/bin/env python3
"""Isolated Manim/Azure review build. No publishing, silent fallback or stale reuse."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from miscellaneous.bac_sciences_ouvertures_fr.project import (  # noqa: E402
    HERE,
    SCENE_PATH,
    load_project,
    validate_assets,
    write_srt,
)


def run(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def probe(path: Path) -> dict:
    result = run(
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path,
        capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def validate_media(info: dict, spec: dict, mode: str) -> float:
    if mode not in {"silent", "azure"}:
        raise ValueError("Select silent or azure explicitly")
    seconds = float(info["format"]["duration"])
    lower, upper = spec["accepted_duration_seconds"]
    if not lower <= seconds <= upper:
        raise ValueError(f"Duration {seconds:.3f}s is outside {lower}–{upper}s; no audio was cut")
    streams = info["streams"]
    video = [s for s in streams if s["codec_type"] == "video"]
    audio = [s for s in streams if s["codec_type"] == "audio"]
    # Manim ql uses 854x480: allow only the unavoidable one-pixel rounding.
    if len(video) != 1 or abs(video[0]["width"] - video[0]["height"] * 16 / 9) > 1.0:
        raise ValueError("Expected exactly one 16:9 video stream")
    if mode == "azure" and len(audio) != 1:
        raise ValueError("Narrated review must have exactly one real audio stream")
    if mode == "silent" and audio:
        raise ValueError("Explicit silent preview unexpectedly contains audio")
    if mode == "silent" and abs(seconds - spec["target_seconds"]) > 0.1:
        raise ValueError("Silent storyboard drifted from its frame-aligned target")
    return seconds


def validate_timeline(timeline: dict, spec: dict, duration: float, mode: str) -> dict:
    """An audio stream alone is not proof of narrated content or synchronized captions."""
    if timeline.get("mode") != mode or abs(duration - timeline["duration"]) > 0.08:
        raise ValueError("Timeline and encoded video disagree")
    expected = [b["id"] for b in spec["beats"]]
    if [b["id"] for b in timeline["beats"]] != expected:
        raise ValueError("Missing or reordered rendered beats")
    previous = 0.0
    for actual, authored in zip(timeline["beats"], spec["beats"]):
        start, end = actual["start"], actual["end"]
        if (
            not all(math.isfinite(x) for x in (start, end))
            or abs(start - previous) > 0.04
            or end <= start
        ):
            raise ValueError("Rendered beats must be finite, ordered and contiguous")
        if actual["caption"] != authored["caption"]:
            raise ValueError("Rendered captions are stale")
        if end - start < authored["min_seconds"] - 0.04:
            raise ValueError("Rendered beat is too short to read")
        caption_end = actual["caption_end"]
        if not start < caption_end <= end + 0.04:
            raise ValueError("Caption ends outside its beat")
        speech = actual.get("speech_seconds")
        if mode == "azure":
            if (
                not timeline.get("voice")
                or not isinstance(speech, (float, int))
                or not math.isfinite(speech)
                or speech <= 0
            ):
                raise ValueError("Narrated review needs measured speech, not just an audio stream")
            if abs(caption_end - start - speech) > 0.04:
                raise ValueError("Captions do not follow measured speech")
        elif speech is not None or timeline.get("voice") is not None:
            raise ValueError("Silent review must not claim speech")
        previous = end
    if abs(previous - duration) > 0.08:
        raise ValueError("Timeline does not cover the complete film")
    final = timeline["beats"][-1]
    hold = final["end"] - final["caption_end"]
    if hold < spec["final_hold_seconds"] - 0.04:
        raise ValueError("Final message has no two-second reading hold")
    return {
        "complete_pathway": "passed",
        "final_reading_hold_seconds": hold,
        "speech_timing": "measured" if mode == "azure" else "not_tested_silent_storyboard",
    }


def source_hashes() -> dict:
    spec = load_project()
    paths = [
        *HERE.glob("*.py"), *validate_assets(spec).values(),
        HERE / "project.json", HERE / "requirements.txt",
        HERE / "sources/accueil_septembre_2026.md",
        ROOT / "assets/uqam_promo/sources.json", ROOT / "tools/tts.py",
        ROOT / "tools/uqam_promo_layout.py", ROOT / "tools/uqam_video_review.py",
        ROOT / "miscellaneous/bac_math_uqam_fr/fetch_uqam_promo_assets.py",
    ]
    font = ROOT / "assets/uqam_promo/fonts/Roboto-VariableFont_wdth,wght.ttf"
    if font.exists():
        paths.append(font)
    if spec["official_logo"]:
        paths.append(ROOT / "assets/branding/uqam_logo.png")
    unique = sorted(set(path.resolve() for path in paths))
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in unique
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["silent", "azure"], default="azure")
    parser.add_argument("--quality", choices=["ql", "qm", "qh"], default="ql")
    parser.add_argument("--output", type=Path, help="New output directory; existing paths are refused")
    args = parser.parse_args(argv)
    spec = load_project()
    validate_assets(spec)
    for command in ("ffmpeg", "ffprobe"):
        if not shutil.which(command):
            parser.error(f"Missing {command}")
    if args.mode == "azure":
        from tools.tts import configure_azure_speech_environment, resolve_voice
        selector = os.getenv(
            "UQAM_OUVERTURES_VOICE",
            os.getenv("UQAM_PROMO_VOICE", os.getenv("MANIM_VOICE", spec["voice_selector"])),
        )
        configure_azure_speech_environment(resolve_voice(selector), require_credentials=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = (args.output or ROOT / "dist" / spec["id"] / f"{stamp}-{args.mode}").resolve()
    output.mkdir(parents=True, exist_ok=False)
    label = "silent_preview" if args.mode == "silent" else "azure_review"
    stem = f"{spec['id']}_{label}"
    timeline_path = output / "timeline.json"
    environment = os.environ.copy()
    environment.update({
        "PYTHONPATH": str(ROOT) + os.pathsep + environment.get("PYTHONPATH", ""),
        "UQAM_OUVERTURES_MODE": args.mode,
        "UQAM_OUVERTURES_TIMELINE": str(timeline_path),
    })
    hashes_before = source_hashes()
    with tempfile.TemporaryDirectory(prefix="uqam-ouvertures-") as temporary:
        media = Path(temporary)
        with (output / "render.log").open("w", encoding="utf-8") as log:
            run(sys.executable, "-m", "manim", f"-{args.quality}", "--renderer=cairo",
                "--disable_caching", "--media_dir", media, "-o", stem,
                SCENE_PATH, spec["scene_class"], cwd=ROOT, env=environment,
                stdout=log, stderr=subprocess.STDOUT)
        candidates = list(media.glob(f"videos/**/{stem}.mp4"))
        if len(candidates) != 1:
            raise RuntimeError(f"Expected one freshly rendered film; found {len(candidates)}")
        master = output / f"{stem}.mp4"
        run("ffmpeg", "-v", "error", "-y", "-i", candidates[0], "-c:v", "libx264",
            "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000",
            "-b:a", "192k", "-movflags", "+faststart", master)
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    srt = output / f"{stem}.srt"
    write_srt(timeline["beats"], srt)
    info = probe(master)
    (output / "ffprobe.json").write_text(json.dumps(info, indent=2) + "\n")
    duration = validate_media(info, spec, args.mode)
    timeline_checks = validate_timeline(timeline, spec, duration, args.mode)
    if source_hashes() != hashes_before:
        raise RuntimeError("Sources changed while rendering")
    # Relative filter paths handle spaces and apostrophes in the user's home directory.
    subtitled = output / f"{stem}_subtitled.mp4"
    style = (
        "FontName=DejaVu Sans,FontSize=16,Alignment=2,MarginV=14,MarginL=18,MarginR=18,"
        "BorderStyle=3,Outline=2,Shadow=0,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H80000000,BackColour=&H80000000"
    )
    run("ffmpeg", "-v", "error", "-y", "-i", master.name,
        "-vf", f"subtitles={srt.name}:force_style='{style}'", "-c:v", "libx264",
        "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags",
        "+faststart", subtitled.name, cwd=output)
    validate_media(probe(subtitled), spec, args.mode)
    if args.mode == "azure":
        run("ffmpeg", "-v", "error", "-y", "-i", master, "-vn", "-acodec", "pcm_s16le",
            "-ar", "48000", "-ac", "1", output / f"{stem}_narration.wav")
    frames = output / "frames"
    frames.mkdir()
    subtitle_frames = output / "subtitle_frames"
    subtitle_frames.mkdir()
    for i, beat in enumerate(timeline["beats"], start=1):
        sample = (beat["start"] + beat["end"]) / 2
        run("ffmpeg", "-v", "error", "-y", "-ss", f"{sample:.3f}", "-i", master,
            "-frames:v", "1", "-update", "1", frames / f"{i:02d}_{beat['id']}.png")
        run("ffmpeg", "-v", "error", "-y", "-ss", f"{sample:.3f}", "-i", subtitled,
            "-frames:v", "1", "-update", "1", subtitle_frames / f"{i:02d}_{beat['id']}.png")
        if i > 1:
            run("ffmpeg", "-v", "error", "-y", "-ss",
                f"{beat['start'] + beat['transition_seconds'] / 2:.3f}", "-i", master,
                "-frames:v", "1", "-update", "1", frames / f"{i:02d}_{beat['id']}_transition.png")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    manifest = {
        "project": spec["id"], "created_utc": stamp, "mode": args.mode,
        "quality": args.quality, "duration_seconds": duration,
        "source_commit": commit.stdout.strip() if commit.returncode == 0 else None,
        "source_sha256": hashes_before, "slide_source": spec["source"],
        "voice": timeline["voice"], "voice_selector": timeline["voice_selector"],
        "timeline_checks": timeline_checks, "voice_rate": timeline["rate"],
        "font": timeline["font"], "music": None, "official_logo": spec["official_logo"], "release_ready": False,
        "visual_review_frame_source": "clean_master",
        "checks": {"encoded_duration": "passed", "stream_contract": "passed",
                   "subtitle_timing": "passed", "layout_bounds_and_text_overlap": "passed",
                   "fresh_sources": "passed"},
        "human_review": {"complete_listening": "pending" if args.mode == "azure" else "not_applicable",
                         "visual_review": "pending", "programme_approval": "pending"},
        "versions": {name: importlib.metadata.version(name)
                     for name in ["manim", "manim-voiceover", "azure-cognitiveservices-speech"]},
        "outputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(output.iterdir()) if p.suffix in {".mp4", ".wav", ".srt"}},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "rendered_for_review", "mode": args.mode,
                      "duration_seconds": duration, "output": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

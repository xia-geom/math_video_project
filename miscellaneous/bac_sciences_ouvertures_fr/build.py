#!/usr/bin/env python3
"""Audio-first Manim/Azure review build. No publication or silent fallback."""
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
from miscellaneous.bac_sciences_ouvertures_fr.narration import (  # noqa: E402
    prepare_narration,
    verify_package,
)
from miscellaneous.bac_sciences_ouvertures_fr.project import (  # noqa: E402
    HERE,
    SCENE_PATH,
    inspect_assets,
    load_project,
    native_asset_directory,
    write_srt,
)
from miscellaneous.bac_sciences_ouvertures_fr.timing import (  # noqa: E402
    TimingBudgetError,
    plan_timeline,
)


def run(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def probe(path: Path) -> dict:
    result = run("ffprobe", "-v", "error", "-show_streams", "-show_format",
                 "-of", "json", path, capture_output=True, text=True)
    return json.loads(result.stdout)


def validate_media(info: dict, spec: dict, mode: str) -> float:
    if mode not in {"silent", "azure"}:
        raise ValueError("Unsupported output mode")
    seconds = float(info["format"]["duration"])
    lower, upper = spec["accepted_duration_seconds"]
    if not math.isfinite(seconds) or not lower <= seconds <= upper:
        raise ValueError(f"Duration {seconds:.3f}s outside {lower}–{upper}s; no audio was cut")
    video = [s for s in info["streams"] if s["codec_type"] == "video"]
    audio = [s for s in info["streams"] if s["codec_type"] == "audio"]
    if len(video) != 1 or video[0]["height"] <= 0 or abs(video[0]["width"] - video[0]["height"] * 16 / 9) > 1:
        raise ValueError("Expected exactly one 16:9 video stream")
    if mode == "azure" and len(audio) != 1:
        raise ValueError("Narrated review must have one real audio stream")
    if mode == "silent" and audio:
        raise ValueError("Explicit silent preview unexpectedly contains audio")
    return seconds


def source_hashes() -> dict:
    paths = list(HERE.glob("*.py")) + [HERE / "project.json", HERE / "requirements.txt",
             HERE / "sources/accueil_septembre_2026.md", ROOT / "tools/tts.py"]
    paths.extend(p for p in (HERE / "assets").rglob("*") if p.is_file())
    native = native_asset_directory()
    if native.is_dir():
        paths.extend(p for p in native.iterdir() if p.is_file())
    font = ROOT / "assets/uqam_promo/fonts/Roboto-VariableFont_wdth,wght.ttf"
    if font.is_file():
        paths.append(font)
    def label(path):
        return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    return {label(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["silent", "azure"], default="azure")
    parser.add_argument("--quality", choices=["ql", "qm", "qh"], default="ql")
    parser.add_argument("--output", type=Path, help="New output directory; existing paths refused")
    parser.add_argument("--source-pdf", type=Path, help="Recover native crops from the supplied PDF")
    parser.add_argument("--audio-only", action="store_true", help="Measure Azure takes; do not render video")
    parser.add_argument("--audio-package", type=Path, help="Reuse a measured audio.json, including a rejected take")
    args = parser.parse_args(argv)
    if args.mode == "silent" and (args.audio_only or args.audio_package):
        parser.error("Audio flags require --mode azure")
    spec = load_project()
    for command in ("ffmpeg", "ffprobe"):
        if not shutil.which(command):
            parser.error(f"Missing {command}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = (args.output or ROOT / "dist" / spec["id"] / f"{stamp}-{args.mode}").resolve()
    output.mkdir(parents=True, exist_ok=False)
    status = {"status": "started", "stage": "source_assets", "mode": args.mode, "release_ready": False}
    _save(output / "status.json", status)
    try:
        if args.source_pdf:
            from miscellaneous.bac_sciences_ouvertures_fr.restore_slide_photos import restore
            if hashlib.sha256(args.source_pdf.read_bytes()).hexdigest() != spec["source"]["sha256"]:
                raise ValueError("Source PDF hash mismatch")
            if not (native_asset_directory() / "manifest.json").is_file():
                restore(args.source_pdf, native_asset_directory())
        assets = None
        if not args.audio_only:
            _, assets = inspect_assets(spec, require_native=args.mode == "azure")
            _save(output / "asset_quality.json", assets)
        hashes_before = source_hashes()
        fps = {"ql": 15, "qm": 30, "qh": 60}[args.quality]
        status["stage"] = "audio_preflight"
        package = None
        if args.mode == "azure":
            if args.audio_package:
                package = verify_package(spec, args.audio_package)
                audio_dir = output / "audio"
                audio_dir.mkdir()
                for clip in package["clips"]:
                    shutil.copyfile(args.audio_package.parent / clip["path"], audio_dir / clip["path"])
                _save(audio_dir / "audio.json", package)
            else:
                package = prepare_narration(spec, output / "audio")
        durations = None if package is None else [c["duration_seconds"] for c in package["clips"]]
        plan = plan_timeline(spec, durations, fps)
        _save(output / "timing_plan.json", plan)
        if args.audio_only:
            _save(output / "status.json", {**status, "status": "audio_preflight_passed",
                                            "video_rendered": False, "listening_review": "pending"})
            print(f"Audio measured and preserved: {output}")
            return 0
        status["stage"] = "render"
        label = "silent_preview" if args.mode == "silent" else "azure_review"
        stem = f"{spec['id']}_{label}"
        timeline_path = output / "timeline.json"
        environment = os.environ.copy()
        environment.update({"PYTHONPATH": str(ROOT) + os.pathsep + environment.get("PYTHONPATH", ""),
                            "UQAM_OUVERTURES_MODE": args.mode,
                            "UQAM_OUVERTURES_TIMELINE": str(timeline_path)})
        if package is not None:
            environment["UQAM_OUVERTURES_AUDIO_PACKAGE"] = str(output / "audio/audio.json")
        with tempfile.TemporaryDirectory(prefix="uqam-ouvertures-") as temporary:
            media = Path(temporary)
            with (output / "render.log").open("w", encoding="utf-8") as log:
                run(sys.executable, "-m", "manim", f"-{args.quality}", "--renderer=cairo",
                    "--disable_caching", "--media_dir", media, "-o", stem, SCENE_PATH,
                    spec["scene_class"], cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
            candidates = list(media.glob(f"videos/**/{stem}.mp4"))
            if len(candidates) != 1:
                raise RuntimeError("Expected one freshly rendered film")
            master = output / f"{stem}.mp4"
            run("ffmpeg", "-v", "error", "-y", "-i", candidates[0], "-c:v", "libx264",
                "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000",
                "-b:a", "192k", "-movflags", "+faststart", master)
        status["stage"] = "encoded_validation"
        timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
        info = probe(master)
        _save(output / "ffprobe.json", info)
        duration = validate_media(info, spec, args.mode)
        if abs(duration - timeline["duration"]) > 0.15:
            raise ValueError("Encoded video and measured timeline disagree")
        if abs(timeline["duration"] - spec["target_seconds"]) > 1.1 / fps:
            raise ValueError("Rendered timeline differs from the frame-exact plan")
        if source_hashes() != hashes_before:
            raise RuntimeError("Sources changed while rendering")
        srt = output / f"{stem}.srt"
        write_srt(timeline["beats"], srt)
        subtitled = output / f"{stem}_subtitled.mp4"
        style = ("FontName=DejaVu Sans,FontSize=18,Alignment=2,MarginV=14,"
                 "BorderStyle=3,Outline=0,Shadow=0,PrimaryColour=&H00FFFFFF,BackColour=&H80000000")
        run("ffmpeg", "-v", "error", "-y", "-i", master.name, "-vf",
            f"subtitles={srt.name}:force_style='{style}'", "-c:v", "libx264", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", subtitled.name, cwd=output)
        validate_media(probe(subtitled), spec, args.mode)
        frames = output / "frames"
        frames.mkdir()
        # Inspect transitions as well as static midpoints; also sample the subtitle variant.
        for item in timeline["review_times"]:
            for video, suffix in ((master, "clean"), (subtitled, "subtitled")):
                run("ffmpeg", "-v", "error", "-y", "-ss", f"{item['seconds']:.6f}",
                    "-i", video, "-frames:v", "1", "-update", "1", frames / f"{item['id']}_{suffix}.png")
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
        manifest = {
            "project": spec["id"], "created_utc": stamp, "mode": args.mode, "quality": args.quality,
            "duration_seconds": duration, "source_commit": commit.stdout.strip() if commit.returncode == 0 else None,
            "worktree_dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None,
            "source_sha256": hashes_before, "slide_source": spec["source"],
            "voice": timeline["voice"], "voice_selector": timeline["voice_selector"],
            "voice_rate": timeline["rate"], "font": timeline["font"], "music": None,
            "official_logo": False, "release_ready": False, "asset_quality": assets,
            "audio_package": None if package is None else "audio/audio.json",
            "visual_review_frame_source": "clean_master_and_subtitled_variant",
            "checks": {"encoded_duration": "passed", "stream_contract": "passed",
                       "subtitle_timing": "passed", "layout_bounds_and_text_overlap": "passed",
                       "fresh_sources": "passed", "global_timing_budget": "passed",
                       "source_image_quality": "native_crop_recovered" if assets["native_source_recovered"] else "preview_only"},
            "human_review": {"complete_listening": "pending" if package else "not_applicable",
                             "visual_review": "pending", "programme_approval": "pending"},
            "versions": {name: importlib.metadata.version(name) for name in
                         ["manim", "manim-voiceover", "azure-cognitiveservices-speech"]},
            "outputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(output.iterdir()) if p.suffix in {".mp4", ".srt"}},
        }
        _save(output / "manifest.json", manifest)
        _save(output / "status.json", {**status, "status": "rendered_for_review", "stage": "complete"})
        print(json.dumps({"status": "rendered_for_review", "mode": args.mode,
                          "duration_seconds": duration, "output": str(output)}, ensure_ascii=False))
        return 0
    except Exception as exc:
        if isinstance(exc, TimingBudgetError):
            _save(output / "timing_plan.json", exc.report)
        _save(output / "status.json", {**status, "status": "failed", "error": str(exc),
                                       "audio_preserved": (output / "audio/audio.json").is_file()})
        raise


if __name__ == "__main__":
    raise SystemExit(main())

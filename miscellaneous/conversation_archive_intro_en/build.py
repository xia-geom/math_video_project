"""Build a silent English Manim preview in a fresh directory; no TTS or publishing."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NAME = "conversation_archive_intro_en_silent_preview"
QUALITIES = {"ql": (854, 480, 15), "qh": (1920, 1080, 60)}


def story():
    data = json.loads((HERE / "storyboard.json").read_text(encoding="utf-8"))
    if data["language"] != "en" or data["mode"] != "silent_captioned_preview":
        raise ValueError("This builder is English and intentionally silent")
    expected = ["opening", "evidence", "connections", "questions", "corrections", "architecture", "start"]
    if [beat["id"] for beat in data["beats"]] != expected:
        raise ValueError("Scene methods and storyboard order must match")
    for beat in data["beats"]:
        if type(beat["seconds"]) is not int or beat["seconds"] < 5:
            raise ValueError("Every beat needs an explicit readable duration")
        if len(beat["caption"].splitlines()) > 2:
            raise ValueError("Use at most two caption lines")
        if any(len(line) > 74 for line in beat["caption"].splitlines()):
            raise ValueError("Shorten or split captions; do not shrink them")
    if data["beats"][5]["claim_status"] != "target_not_shipped_in_source_commit":
        raise ValueError("Storage roadmap must not be relabeled as shipped behavior")
    return data


def timecode(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def accessibility(data):
    lines, script, cursor = [], [], 0
    for number, beat in enumerate(data["beats"], 1):
        lines.extend([str(number), f"{timecode(cursor)} --> {timecode(cursor + beat['seconds'])}", beat["caption"], ""])
        script.extend([f"{number}. {beat['title']}", beat["script_en"], ""])
        cursor += beat["seconds"]
    return "\n".join(lines), "\n".join(script)


def inspect_video(path, quality, duration):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                            capture_output=True, text=True, check=True, timeout=30)
    info = json.loads(result.stdout)
    videos = [s for s in info["streams"] if s["codec_type"] == "video"]
    if len(videos) != 1 or any(s["codec_type"] == "audio" for s in info["streams"]):
        raise ValueError("Expected one video stream and no audio; do not mislabel narration")
    width, height, fps = QUALITIES[quality]
    video = videos[0]
    if (video["width"], video["height"]) != (width, height):
        raise ValueError("Unexpected render dimensions")
    numerator, denominator = map(int, video["avg_frame_rate"].split("/"))
    if abs(numerator / denominator - fps) > 0.01:
        raise ValueError("Unexpected frame rate")
    actual = float(info["format"]["duration"])
    if abs(actual - duration) > 2 / fps:
        raise ValueError(f"Unexpected duration: {actual}; target {duration}")
    return {"width": width, "height": height, "fps": fps, "duration_seconds": actual,
            "audio_present": False, "codec": video["codec_name"]}


def build(output, quality="ql"):
    data = story()
    if quality not in QUALITIES:
        raise ValueError("Unsupported render quality")
    output = Path(output).resolve()
    # Re-running never deletes an old render, even an empty output directory.
    output.mkdir(parents=True, exist_ok=False)
    subtitle, script = accessibility(data)
    (output / "captions.en.srt").write_text(subtitle, encoding="utf-8")
    (output / "narration-script.en.txt").write_text(script, encoding="utf-8")
    log_path = output / "manim-render.log"
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run([sys.executable, "-m", "manim", "-" + quality,
                                 str(HERE / "conversation_archive_intro_en_scene.py"), "ConversationArchiveIntroEN",
                                 "--media_dir", str(output / "media"), "--output_file", NAME, "--disable_caching"],
                                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=600)
    if result.returncode:
        print("\n".join(log_path.read_text(encoding="utf-8").splitlines()[-70:]), file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, result.args)
    matches = list((output / "media").rglob(NAME + ".mp4"))
    if len(matches) != 1:
        raise ValueError("Expected exactly one completed Manim render")
    movie = output / (NAME + ".mp4")
    # Faststart improves browser playback without changing animation or timing.
    subprocess.run(["ffmpeg", "-v", "error", "-n", "-i", str(matches[0]), "-c", "copy",
                    "-movflags", "+faststart", str(movie)], check=True, timeout=60)
    duration = sum(beat["seconds"] for beat in data["beats"])
    measured = inspect_video(movie, quality, duration)
    frames = output / "review_frames"
    frames.mkdir()
    cursor = 0
    for number, beat in enumerate(data["beats"], 1):
        subprocess.run(["ffmpeg", "-v", "error", "-n", "-ss", str(cursor + beat["seconds"] / 2),
                        "-i", str(movie), "-frames:v", "1", str(frames / f"{number:02d}-{beat['id']}.png")],
                       check=True, timeout=30)
        cursor += beat["seconds"]
    report = {"title": data["title"], "language": "en", "mode": data["mode"], "media": measured,
              "source_commit": data["source_commit"], "movie_sha256": hashlib.sha256(movie.read_bytes()).hexdigest(),
              "storyboard_sha256": hashlib.sha256((HERE / "storyboard.json").read_bytes()).hexdigest(),
              "geometry_boundary_checks": "executed by scene", "human_visual_review": "not established by this build",
              "listening_review": "not applicable; no audio", "publication": "not performed",
              "data": "invented examples", "files": [movie.name, "captions.en.srt", "narration-script.en.txt", "review_frames/"]}
    (output / "render-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality", choices=tuple(QUALITIES), default="ql")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate content only; do not render")
    args = parser.parse_args(argv)
    try:
        if args.check:
            data = story()
            result = {"status": "content_checked_not_rendered", "seconds": sum(b["seconds"] for b in data["beats"]), "beats": len(data["beats"])}
        else:
            if not all(shutil.which(command) for command in ("ffmpeg", "ffprobe")):
                raise ValueError("Install FFmpeg/ffprobe before rendering")
            output = args.output or ROOT / "dist" / "conversation_archive_intro_en" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            result = build(output, args.quality)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

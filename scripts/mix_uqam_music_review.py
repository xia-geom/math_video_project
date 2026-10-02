#!/usr/bin/env python3
"""Mix the reviewed Resolutions recording with unchanged video and speech timing.

Uses FFmpeg/ffprobe only. The supplied music must have reviewed reuse terms.
This utility neither synthesizes speech nor publishes a release.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


REVIEWED_MUSIC_SHA256 = "d61702c3b378662a3dd07d6207d9ac2cfedd405a4746c273db890afa644c7015"


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def probe(path):
    return json.loads(run("ffprobe", "-v", "error", "-show_streams",
                          "-show_format", "-of", "json", str(path)).stdout)


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def video_hash(path):
    return run("ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0",
               "-c", "copy", "-f", "hash", "-hash", "sha256", "-").stdout.strip()


def loudness(path, filters="anull"):
    result = run("ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                 "-vn", "-af", filters + ",loudnorm=I=-19:TP=-1:LRA=11:print_format=json",
                 "-f", "null", "-")
    measurements = re.findall(r'\{\s*"input_i".*?\}', result.stderr, re.S)
    if not measurements:
        raise RuntimeError("FFmpeg returned no loudness measurement")
    return json.loads(measurements[-1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--music", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--music-offset", type=float, default=0)
    parser.add_argument("--voice-lufs", type=float, default=-19)
    parser.add_argument("--music-lufs", type=float, default=-37)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    music_sha256 = file_hash(args.music)
    if music_sha256 != REVIEWED_MUSIC_SHA256:
        raise ValueError("This preset only accepts the reviewed Resolutions recording; "
                         "a different track needs its own source and attribution review.")
    source = probe(args.video)
    duration = float(next(s["duration"] for s in source["streams"]
                          if s["codec_type"] == "video"))
    music_duration = float(probe(args.music)["format"]["duration"])
    if args.music_offset < 0 or args.music_offset + duration > music_duration:
        raise ValueError("Selected music excerpt is outside the source track")
    stereo = "aresample=48000,aformat=channel_layouts=stereo"
    voice_filter = f"{stereo},apad=whole_dur={duration},atrim=duration={duration}"
    music_filter = (
        f"atrim=start={args.music_offset}:duration={duration},asetpts=PTS-STARTPTS,"
        f"{stereo},afade=t=in:st=0:d=0.75,"
        f"afade=t=out:st={max(0, duration - 2)}:d=2"
    )
    voice_before = loudness(args.video, voice_filter)
    music_before = loudness(args.music, music_filter)
    voice_gain = args.voice_lufs - float(voice_before["input_i"])
    music_gain = args.music_lufs - float(music_before["input_i"])
    filters = (
        f"[0:a:0]{voice_filter},volume={voice_gain:.4f}dB[voice];"
        f"[1:a:0]{music_filter},volume={music_gain:.4f}dB[music];"
        "[voice][music]amix=inputs=2:duration=first:normalize=0,"
        "alimiter=limit=0.841395:level=false:latency=true[mix]"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-hide_banner", "-nostats", "-n", "-i", str(args.video),
               "-i", str(args.music), "-filter_complex", filters,
               "-map", "0:v:0", "-map", "[mix]", "-map_metadata", "0",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-t", str(duration), "-movflags", "+faststart",
               "-metadata", "comment=Music: Resolutions by Scott Buckley; CC BY 4.0; "
               "https://www.scottbuckley.com.au/library/resolutions/ ; "
               "https://creativecommons.org/licenses/by/4.0/ ; "
               "excerpted, volume adjusted and faded. Local review mix.", str(args.output)]
    result = run(*command)
    args.output.with_suffix(".ffmpeg.log").write_text(result.stderr)
    decoded = run("ffmpeg", "-v", "error", "-i", str(args.output), "-f", "null", "-")
    if decoded.stderr.strip():
        raise RuntimeError(decoded.stderr)
    same_video = video_hash(args.video) == video_hash(args.output)
    measured = loudness(args.output)
    output_probe = probe(args.output)
    out_duration = float(output_probe["format"]["duration"])
    if not same_video or abs(out_duration - duration) > 0.05:
        raise RuntimeError("Video packet identity or duration validation failed")
    if float(measured["input_tp"]) > -1:
        raise RuntimeError("Encoded true peak exceeds -1 dBTP")
    manifest = {
        "status": "local_music_review_not_release",
        "input_video": str(args.video), "input_sha256": file_hash(args.video),
        "music_file": str(args.music), "music_sha256": music_sha256,
        "music_title": "Resolutions", "music_artist": "Scott Buckley",
        "music_source": "https://www.scottbuckley.com.au/library/resolutions/",
        "music_license": "https://creativecommons.org/licenses/by/4.0/",
        "license_checked": "2026-10-02",
        "music_offset_seconds": args.music_offset,
        "voice_target_lufs": args.voice_lufs, "music_target_lufs": args.music_lufs,
        "voice_gain_db": voice_gain, "music_gain_db": music_gain,
        "music_fades_seconds": {"in": 0.75, "out": 2},
        "voice_before_mix": voice_before, "music_excerpt_before_gain": music_before,
        "output_loudness": measured,
        "duration_seconds": out_duration, "original_video_duration_seconds": duration,
        "video_packets_unchanged": same_video, "speech_timing_unchanged": True,
        "full_decode": "passed", "listening_review": "not_performed",
        "institutional_approval": "not_inferred", "release_ready": False,
        "output_file": args.output.name, "output_sha256": file_hash(args.output),
        "ffmpeg_version": run("ffmpeg", "-version").stdout.splitlines()[0],
        "filter_complex": filters,
    }
    args.output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(args.output), "loudness": measured,
                      "video_packets_unchanged": same_video, "duration": out_duration}))


if __name__ == "__main__":
    main()

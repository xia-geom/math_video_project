#!/usr/bin/env python3
"""Mix a source-verified music recording with unchanged video and speech timing.

Pass --music-manifest for another recording; omitting it retains Resolutions.
Uses FFmpeg/ffprobe only. The supplied music must have reviewed reuse terms.
This utility neither synthesizes speech nor publishes a release.
"""

import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


REVIEWED_MUSIC_SHA256 = "d61702c3b378662a3dd07d6207d9ac2cfedd405a4746c273db890afa644c7015"
LEGACY_MUSIC = {
    "schema_version": 1,
    "title": "Resolutions", "creator": "Scott Buckley",
    "source_url": "https://www.scottbuckley.com.au/library/resolutions/",
    "license_name": "CC BY 4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
    "download_url": "https://www.scottbuckley.com.au/library/wp-content/uploads/2022/01/Resolutions.mp3",
    "sha256": REVIEWED_MUSIC_SHA256, "license_checked": "2026-10-02",
    "default_offset_seconds": 0.85,
}


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def probe(path):
    return json.loads(run("ffprobe", "-v", "error", "-show_streams",
                          "-show_format", "-of", "json", str(path)).stdout)


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def music_metadata(music, manifest_path=None):
    """Bind attribution to the bytes reviewed, before running any media command."""
    metadata = (json.loads(manifest_path.read_text()) if manifest_path
                else dict(LEGACY_MUSIC))
    if not isinstance(metadata, dict) or metadata.get("schema_version") != 1:
        raise ValueError("Music metadata must be a schema_version 1 object")
    for key in ("title", "creator", "source_url", "license_name", "license_url",
                "download_url", "sha256", "license_checked"):
        value = metadata.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Music metadata requires a nonempty {key}")
    for key in ("source_url", "license_url", "download_url"):
        url = urlsplit(metadata[key])
        if url.scheme not in {"https", "http"} or not url.netloc:
            raise ValueError(f"Music metadata {key} must be an HTTP(S) URL")
    if not re.fullmatch(r"[0-9a-f]{64}", metadata["sha256"]):
        raise ValueError("Music metadata sha256 must contain 64 lowercase hex digits")
    if file_hash(music) != metadata["sha256"]:
        raise ValueError("Music recording does not match its reviewed SHA-256; "
                         "provide the correct recording and --music-manifest")
    offset = metadata.get("default_offset_seconds", 0.0)
    if not isinstance(offset, (int, float)) or not math.isfinite(offset) or offset < 0:
        raise ValueError("Music default_offset_seconds must be finite and nonnegative")
    return metadata


def music_credit(metadata):
    return (f"Music: {metadata['title']} by {metadata['creator']}; "
            f"{metadata['license_name']}; {metadata['source_url']}; "
            f"{metadata['license_url']}; excerpted, volume adjusted, "
            "ducked when enabled, and faded. Local review mix.")


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
    parser.add_argument("--music-manifest", type=Path,
                        help="JSON sidecar with title, creator, source/license/download URLs, "
                             "license name/check date, and recording SHA-256")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--music-offset", type=float,
                        help="Override this recording's default_offset_seconds (new tracks: 0)")
    parser.add_argument("--voice-lufs", type=float, default=-19)
    parser.add_argument("--music-lufs", type=float, default=-25)
    parser.add_argument("--duck-music", action=argparse.BooleanOptionalAction, default=True,
                        help="Gently lower the music while the narrator speaks")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    metadata = music_metadata(args.music, args.music_manifest)
    music_sha256 = metadata["sha256"]
    music_offset = (args.music_offset if args.music_offset is not None
                    else metadata.get("default_offset_seconds", 0.0))
    if not all(math.isfinite(x) for x in (music_offset, args.voice_lufs, args.music_lufs)):
        raise ValueError("Music offset and loudness targets must be finite")
    source = probe(args.video)
    duration = float(next(s["duration"] for s in source["streams"]
                          if s["codec_type"] == "video"))
    music_duration = float(probe(args.music)["format"]["duration"])
    if music_offset < 0 or music_offset + duration > music_duration:
        raise ValueError("Selected music excerpt is outside the source track")
    stereo = "aresample=48000,aformat=channel_layouts=stereo"
    voice_filter = f"{stereo},apad=whole_dur={duration},atrim=duration={duration}"
    music_filter = (
        f"atrim=start={music_offset}:duration={duration},asetpts=PTS-STARTPTS,"
        f"{stereo},afade=t=in:st=0:d=0.75,"
        f"afade=t=out:st={max(0, duration - 2)}:d=2"
    )
    voice_before = loudness(args.video, voice_filter)
    music_before = loudness(args.music, music_filter)
    voice_gain = args.voice_lufs - float(voice_before["input_i"])
    music_gain = args.music_lufs - float(music_before["input_i"])
    if not all(math.isfinite(x) for x in (voice_gain, music_gain)):
        raise ValueError("Voice and selected music excerpt must contain measurable audio")
    music_stem = args.output.with_suffix(".music-bed.wav")
    if music_stem.exists():
        raise FileExistsError(music_stem)
    voice_routing = "asplit=2[voice][sidechain]" if args.duck_music else "anull[voice]"
    music_routing = (
        "[music][sidechain]sidechaincompress=threshold=0.04:ratio=2:"
        "attack=100:release=600:makeup=1[bed];"
        if args.duck_music else "[music]anull[bed];"
    )
    filters = (
        f"[0:a:0]{voice_filter},volume={voice_gain:.4f}dB,{voice_routing};"
        f"[1:a:0]{music_filter},volume={music_gain:.4f}dB[music];"
        + music_routing + "[bed]asplit=2[musicmix][musicstem];"
        "[voice][musicmix]amix=inputs=2:duration=first:normalize=0,"
        "alimiter=limit=0.841395:level=false:latency=true[mix]"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-hide_banner", "-nostats", "-n", "-i", str(args.video),
               "-i", str(args.music), "-filter_complex", filters,
               "-map", "0:v:0", "-map", "[mix]", "-map_metadata", "0",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-t", str(duration), "-movflags", "+faststart",
               "-metadata", "comment=" + music_credit(metadata), str(args.output),
               "-map", "[musicstem]", "-c:a", "pcm_s24le", "-ar", "48000", str(music_stem)]
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
        "music_title": metadata["title"], "music_artist": metadata["creator"],
        "music_source": metadata["source_url"],
        "music_license": metadata["license_url"],
        "music_download_url": metadata["download_url"],
        "license_checked": metadata["license_checked"],
        "music_metadata": metadata,
        "music_metadata_file": str(args.music_manifest) if args.music_manifest else None,
        "music_metadata_sha256": file_hash(args.music_manifest) if args.music_manifest else None,
        "music_offset_seconds": music_offset,
        "voice_target_lufs": args.voice_lufs, "music_target_lufs": args.music_lufs,
        "voice_gain_db": voice_gain, "music_gain_db": music_gain,
        "music_ducking": ({"threshold_linear": 0.04, "ratio": 2,
                           "attack_ms": 100, "release_ms": 600}
                          if args.duck_music else None),
        "music_bed_file": music_stem.name,
        "music_bed_loudness": loudness(music_stem),
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
    args.output.with_suffix(".credits.txt").write_text(
        music_credit(metadata) + "\n\nInclude this credit in the post caption or video description.\n"
        "Photo attributions are supplied in CREDITS.txt and must accompany distribution.\n")
    print(json.dumps({"output": str(args.output), "loudness": measured,
                      "video_packets_unchanged": same_video, "duration": out_duration}))


if __name__ == "__main__":
    main()

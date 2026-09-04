"""Render, validate, stamp, and optionally deliver the UQAM short promo."""

from __future__ import annotations

# The release helper is executable directly from its scene directory.
# ruff: noqa: E402
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import re
import shutil
import subprocess
import sys
import wave
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from bac_math_uqam_fr_scene import (
    ASSET_DIR,
    CTA_DISPLAY,
    CTA_URL,
    FONT_PATH,
    LOGO_PATH,
    NARRATION_SEGMENTS,
    PROMO_RATE,
    PROMO_VOICE,
    TEXT_RASTER_SCALE,
)

from tools.tts import (
    MAI_VOICE_2,
    MAI_VOICE_2_REGION,
    VOICE_LOCALES,
    configure_azure_speech_environment,
    ssml,
)

SCENE_FILE = Path(__file__).with_name("bac_math_uqam_fr_scene.py")
SCENE_CLASS = "BacMathUQAMFR"
ARTIFACT_SLUG = "bac_math_uqam_fr"
RAW_DIR = REPO_ROOT / "dist" / ARTIFACT_SLUG
VOICE_CACHE = REPO_ROOT / "media" / "voiceovers"
DEFAULT_DRIVE_DIR = Path("/Users/xiaxiao/My Drive/UQAM-apercu-programme")
CLAIM_SOURCES = [
    "https://etudier.uqam.ca/programme/baccalaureat-mathematiques",
    "https://sciences.uqam.ca/etudiants/services-aux-etudiants-de-la-faculte/",
    "https://sciences.uqam.ca/futurs-etudiants/pourquoi-etudier-en-sciences-a-luqam/",
    "https://bibliotheques.uqam.ca/services-offerts/espaces-aux-bibliotheques/",
    "https://cirget.uqam.ca/fr/membres.html",
    "https://lacim.uqam.ca/fr/",
    "https://plancampus.uqam.ca/se-rendre-uqam",
]
UQAM_VIDEO_GUIDE = (
    "https://services-medias.uqam.ca/media/uploads/sites/6/2024/12/"
    "17082749/Guide_normes_videos_Novembre2023.pdf"
)
TARGET_LUFS = -18.5
# Leave AAC headroom so the decoded deliverable remains at or below -1 dBFS.
TARGET_TRUE_PEAK = -1.3
MAX_TRUE_PEAK = -1.0
RENDER_PROVENANCE = RAW_DIR / "render_provenance.json"


def run_checked(command: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=REPO_ROOT, env=env, check=True)


def capture(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def prepare_render_environment() -> dict[str, str]:
    if PROMO_VOICE != MAI_VOICE_2:
        raise RuntimeError(
            f"This release must use MAI-Voice-2; resolved UQAM_PROMO_VOICE={PROMO_VOICE!r}"
        )
    region = configure_azure_speech_environment(PROMO_VOICE)
    if region != MAI_VOICE_2_REGION:
        raise RuntimeError(f"MAI-Voice-2 must use {MAI_VOICE_2_REGION}")

    explicit_logo_approval = os.getenv("UQAM_LOGO_APPROVED", "0") == "1"
    requested_logo = os.getenv("UQAM_USE_OFFICIAL_LOGO", "0") == "1"
    if requested_logo and not explicit_logo_approval:
        raise RuntimeError(
            "UQAM_USE_OFFICIAL_LOGO=1 requires UQAM_LOGO_APPROVED=1. "
            "Otherwise build without the official UQAM logo."
        )

    environment = os.environ.copy()
    environment.update(
        {
            "UQAM_PROMO_VOICE": "MAI-Voice-2",
            "UQAM_PROMO_RATE": "+2%",
            "UQAM_USE_REAL_PHOTOS": "1",
            "UQAM_USE_OFFICIAL_LOGO": (
                "1" if requested_logo and explicit_logo_approval else "0"
            ),
            "UQAM_LOGO_APPROVED": "1" if explicit_logo_approval else "0",
            "UQAM_SHOW_PHOTO_CREDITS": "0",
            "UQAM_PROMO_CTA_URL": (
                "https://etudier.uqam.ca/programme/baccalaureat-mathematiques"
            ),
            "UQAM_PROMO_CTA_DISPLAY": "etudier.uqam.ca",
            "RENDER_SKIP_DRIVE_COPY": "1",
        }
    )
    return environment


def render_configuration(environment: dict[str, str], quality: str) -> dict[str, str]:
    keys = (
        "UQAM_PROMO_VOICE",
        "UQAM_PROMO_RATE",
        "UQAM_USE_REAL_PHOTOS",
        "UQAM_PROMO_ASSET_DIR",
        "UQAM_VIDEO_FONT",
        "UQAM_VIDEO_FONT_PATH",
        "UQAM_USE_OFFICIAL_LOGO",
        "UQAM_LOGO_APPROVED",
        "UQAM_PROMO_LOGO_PATH",
        "UQAM_SHOW_PHOTO_CREDITS",
        "UQAM_PROMO_CTA_URL",
        "UQAM_PROMO_CTA_DISPLAY",
        "UQAM_TEACHING_PORTRAIT_HOLD",
        "UQAM_RESEARCH_GRAPH_HOLD",
        "UQAM_FINAL_MESSAGE_HOLD",
        "UQAM_FINAL_CARD_HOLD",
        "UQAM_SUPPORT_HUMAN_HOLD",
        "UQAM_SUPPORT_LIBRARY_HOLD",
        "UQAM_MONTREAL_BUILDING_HOLD",
        "UQAM_MONTREAL_PHOTO_HOLD",
    )
    result = {key: environment.get(key, "") for key in keys}
    result["render_quality"] = quality
    result["typography_renderer"] = "Pillow/FreeType"
    result["text_raster_scale"] = str(TEXT_RASTER_SCALE)
    result["pillow_version"] = package_version("Pillow")
    result["font_sha256"] = sha256_file(FONT_PATH)
    return result


def source_file_inventory(environment: dict[str, str]) -> dict[str, dict[str, str]]:
    candidates = {
        "scene": SCENE_FILE,
        "build_release": Path(__file__).resolve(),
        "asset_fetcher": Path(__file__).with_name("fetch_uqam_promo_assets.py"),
        "tts_helper": REPO_ROOT / "tools" / "tts.py",
        "render_script": REPO_ROOT / "scripts" / "render.sh",
        "asset_manifest": ASSET_DIR / "sources.json",
    }
    if environment.get("UQAM_USE_OFFICIAL_LOGO") == "1":
        candidates["official_logo"] = LOGO_PATH

    inventory: dict[str, dict[str, str]] = {}
    for name, path in candidates.items():
        if not path.is_file():
            raise RuntimeError(f"Render dependency is missing: {name}: {path}")
        inventory[name] = {"path": str(path.resolve()), "sha256": sha256_file(path)}
    return inventory


def render_toolchain() -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "manim": package_version("manim"),
        "manim_voiceover": package_version("manim-voiceover"),
        "azure_speech": package_version("azure-cognitiveservices-speech"),
        "ffmpeg": capture(["ffmpeg", "-version"]).splitlines()[0],
    }


def write_render_provenance(
    raw_video: Path,
    raw_srt: Path,
    environment: dict[str, str],
    quality: str,
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "raw_video_sha256": sha256_file(raw_video),
        "raw_srt_sha256": sha256_file(raw_srt),
        "configuration": render_configuration(environment, quality),
        "source_files": source_file_inventory(environment),
        "toolchain": render_toolchain(),
        "written_at": datetime.now(ZoneInfo("America/Toronto")).isoformat(),
    }
    RENDER_PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    RENDER_PROVENANCE.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return payload


def verify_render_provenance(
    raw_video: Path,
    raw_srt: Path,
    environment: dict[str, str],
    quality: str,
) -> dict[str, Any]:
    if not RENDER_PROVENANCE.is_file():
        raise RuntimeError(
            "--skip-render is unsafe without render_provenance.json; rerender once normally."
        )

    payload = json.loads(RENDER_PROVENANCE.read_text(encoding="utf-8"))
    checks = {
        "raw MP4": (payload.get("raw_video_sha256"), sha256_file(raw_video)),
        "raw SRT": (payload.get("raw_srt_sha256"), sha256_file(raw_srt)),
        "render configuration": (
            payload.get("configuration"),
            render_configuration(environment, quality),
        ),
        "render dependency inventory": (
            payload.get("source_files"),
            source_file_inventory(environment),
        ),
        "render toolchain": (payload.get("toolchain"), render_toolchain()),
    }
    mismatches = [name for name, (recorded, current) in checks.items() if recorded != current]
    if mismatches:
        raise RuntimeError(
            "Stale or mismatched --skip-render inputs:\n- "
            + "\n- ".join(mismatches)
        )
    return payload


def preflight_assets(*, require_logo: bool) -> dict[str, Any]:
    source_manifest = ASSET_DIR / "sources.json"
    required = [
        ASSET_DIR / "classroom_math.jpg",
        ASSET_DIR / "francois_bergeron.jpg",
        ASSET_DIR / "lisa_berger.jpg",
        ASSET_DIR / "research_math.jpg",
        ASSET_DIR / "bibliotheque_sciences.jpg",
        ASSET_DIR / "president_kennedy.jpg",
        ASSET_DIR / "international_students.jpg",
        ASSET_DIR / "allo_pk.jpg",
        FONT_PATH,
        ASSET_DIR / "fonts" / "OFL.txt",
        source_manifest,
    ]
    if require_logo:
        required.append(LOGO_PATH)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("Required release assets are missing:\n- " + "\n- ".join(missing))

    data = json.loads(source_manifest.read_text(encoding="utf-8"))
    records = data.get("assets", [])
    records_by_name = {item.get("filename"): item for item in records}
    expected_names = {
        path.relative_to(ASSET_DIR).as_posix()
        for path in required
        if path not in {source_manifest, LOGO_PATH}
    }
    missing_records = sorted(expected_names - records_by_name.keys())
    invalid_records = sorted(
        name
        for name in expected_names
        if records_by_name.get(name, {}).get("status") != "present"
    )
    if missing_records or invalid_records:
        raise RuntimeError(
            "Asset source manifest does not match required assets; "
            f"missing={missing_records}, invalid={invalid_records}"
        )
    for item in records:
        if item.get("status") != "present":
            continue
        path = ASSET_DIR / item["filename"]
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Asset hash differs from source manifest: {path}")
    return data


def render_master(environment: dict[str, str], quality: str) -> tuple[Path, Path]:
    run_checked(
        [
            str(REPO_ROOT / "scripts" / "render.sh"),
            str(SCENE_FILE.relative_to(REPO_ROOT)),
            SCENE_CLASS,
            quality,
        ],
        env=environment,
    )
    raw_video = RAW_DIR / f"{ARTIFACT_SLUG}.mp4"
    raw_srt = RAW_DIR / f"{ARTIFACT_SLUG}.srt"
    if not raw_video.is_file() or not raw_srt.is_file():
        raise RuntimeError("The shared render pipeline did not create MP4 and SRT outputs")
    write_render_provenance(raw_video, raw_srt, environment, quality)
    return raw_video, raw_srt


def ffprobe(path: Path, *, packets: bool = False) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
    ]
    if packets:
        command.extend(
            [
                "-select_streams",
                "a:0",
                "-show_packets",
                "-show_entries",
                "packet=pts_time,duration_time",
            ]
        )
    else:
        command.extend(["-show_format", "-show_streams"])
    command.append(str(path))
    return json.loads(capture(command))


def extract_representative_frames(
    video: Path, destination: Path
) -> list[dict[str, Any]]:
    duration = float(ffprobe(video)["format"]["duration"])
    fractions = (0.04, 0.10, 0.22, 0.34, 0.47, 0.60, 0.73, 0.86, 0.95)
    destination.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for index, fraction in enumerate(fractions, start=1):
        timestamp = duration * fraction
        frame = destination / f"qa_{index:02d}_{timestamp:06.2f}s.png"
        run_checked(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                str(frame),
            ]
        )
        records.append(
            {
                "path": str(frame.resolve()),
                "time_seconds": timestamp,
                "sha256": sha256_file(frame),
            }
        )

    if len({item["sha256"] for item in records}) < 6:
        raise RuntimeError(
            "Representative-frame extraction produced too few distinct frames"
        )
    return records


def verify_manifest_output_hashes(manifest: dict[str, Any]) -> None:
    outputs = manifest.get("outputs", {})
    if not outputs:
        raise RuntimeError("Build manifest contains no recorded outputs")
    for key, record in outputs.items():
        path = Path(record["path"])
        if not path.is_file():
            raise RuntimeError(f"Manifest output is missing: {key}: {path}")
        if sha256_file(path) != record.get("sha256"):
            raise RuntimeError(f"Manifest output hash mismatch: {key}: {path}")


def fraction_value(value: str) -> float:
    return float(Fraction(value))


def media_summary(path: Path) -> dict[str, Any]:
    probe = ffprobe(path)
    video_streams = [
        stream for stream in probe["streams"] if stream.get("codec_type") == "video"
    ]
    audio_streams = [
        stream for stream in probe["streams"] if stream.get("codec_type") == "audio"
    ]
    if len(video_streams) != 1 or len(audio_streams) != 1:
        raise RuntimeError("Release master must contain exactly one video and one audio stream")
    video = video_streams[0]
    audio = audio_streams[0]
    packets = ffprobe(path, packets=True).get("packets", [])
    maximum_gap = 0.0
    previous_end: float | None = None
    for packet in packets:
        if "pts_time" not in packet:
            continue
        start = float(packet["pts_time"])
        duration = float(packet.get("duration_time", 0.0))
        if previous_end is not None:
            maximum_gap = max(maximum_gap, start - previous_end)
        previous_end = start + duration
    return {
        "duration_seconds": float(probe["format"]["duration"]),
        "video": {
            "codec": video.get("codec_name"),
            "pixel_format": video.get("pix_fmt"),
            "width": int(video.get("width", 0)),
            "height": int(video.get("height", 0)),
            "r_frame_rate": video.get("r_frame_rate"),
            "avg_frame_rate": video.get("avg_frame_rate"),
            "fps": fraction_value(video["r_frame_rate"]),
            "average_fps": fraction_value(video["avg_frame_rate"]),
            "start_time": float(video.get("start_time", 0.0)),
        },
        "audio": {
            "codec": audio.get("codec_name"),
            "sample_rate": int(audio.get("sample_rate", 0)),
            "channels": int(audio.get("channels", 0)),
            "start_time": float(audio.get("start_time", 0.0)),
            "duration_seconds": float(audio.get("duration", probe["format"]["duration"])),
            "maximum_packet_gap_seconds": maximum_gap,
        },
    }


def parse_loudnorm_json(stderr: str) -> dict[str, float]:
    matches = re.findall(r"\{\s*\"input_i\".*?\}", stderr, flags=re.DOTALL)
    if not matches:
        raise RuntimeError("FFmpeg did not return loudness measurements")
    payload = json.loads(matches[-1])
    fields = {
        "input_i": "integrated_lufs",
        "input_tp": "true_peak_dbfs",
        "input_lra": "loudness_range_lu",
        "input_thresh": "threshold_lufs",
        "target_offset": "target_offset_lu",
    }
    values: dict[str, float] = {}
    for source, target in fields.items():
        value = payload[source]
        values[target] = float(value) if value not in {"-inf", "inf"} else math.inf
    return values


def measure_loudness(
    path: Path, *, prefilter: str | None = None
) -> dict[str, float]:
    audio_filter = (
        f"{prefilter},loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA=7:print_format=json"
        if prefilter
        else f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA=7:print_format=json"
    )
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-af",
            audio_filter,
            "-f",
            "null",
            "-",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return parse_loudnorm_json(result.stderr)


def normalize_if_needed(
    raw_video: Path, destination: Path
) -> tuple[bool, dict[str, float], dict[str, float]]:
    raw_probe = ffprobe(raw_video)
    raw_audio = next(
        stream for stream in raw_probe["streams"] if stream.get("codec_type") == "audio"
    )
    if int(raw_audio.get("channels", 0)) == 2:
        # Manim's container is stereo even though Azure supplies mono. Average
        # the duplicate channels before loudness measurement to avoid the 3 dB
        # gain of FFmpeg's default stereo-to-mono matrix.
        channel_filter = "pan=mono|c0=0.5*c0+0.5*c1"
    else:
        channel_filter = "aformat=channel_layouts=mono"

    before = measure_loudness(raw_video, prefilter=channel_filter)
    normalize = (
        abs(before["integrated_lufs"] - TARGET_LUFS) > 0.5
        or before["true_peak_dbfs"] > TARGET_TRUE_PEAK
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not normalize:
        run_checked(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(raw_video),
                "-map",
                "0:v:0",
                "-map",
                "0:a:0",
                "-c:v",
                "copy",
                "-af",
                f"{channel_filter},apad",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "48000",
                "-ac",
                "1",
                "-shortest",
                str(destination),
            ]
        )
    else:
        audio_filter = (
            f"{channel_filter},loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA=7:"
            f"measured_I={before['integrated_lufs']}:"
            f"measured_TP={before['true_peak_dbfs']}:"
            f"measured_LRA={before['loudness_range_lu']}:"
            f"measured_thresh={before['threshold_lufs']}:"
            f"offset={before['target_offset_lu']}:linear=true:print_format=summary,apad"
        )
        run_checked(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-i",
                str(raw_video),
                "-map",
                "0:v:0",
                "-map",
                "0:a:0",
                "-c:v",
                "copy",
                "-af",
                audio_filter,
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "48000",
                "-ac",
                "1",
                "-shortest",
                str(destination),
            ]
        )
    after = measure_loudness(destination)
    return normalize, before, after


def extract_wav(video: Path, wav_path: Path) -> dict[str, int]:
    run_checked(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-map",
            "0:a:0",
            "-c:a",
            "pcm_s16le",
            "-ar",
            "48000",
            "-ac",
            "1",
            str(wav_path),
        ]
    )
    with wave.open(str(wav_path), "rb") as wav:
        return {
            "sample_rate": wav.getframerate(),
            "channels": wav.getnchannels(),
            "sample_width_bytes": wav.getsampwidth(),
            "frames": wav.getnframes(),
        }


def validate_srt(path: Path, duration: float) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    pattern = re.compile(
        r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> "
        r"(\d\d):(\d\d):(\d\d),(\d\d\d)"
    )
    intervals: list[tuple[float, float]] = []
    for match in pattern.finditer(text):
        values = [int(value) for value in match.groups()]
        start = values[0] * 3600 + values[1] * 60 + values[2] + values[3] / 1000
        end = values[4] * 3600 + values[5] * 60 + values[6] + values[7] / 1000
        intervals.append((start, end))
    if not intervals:
        raise RuntimeError("SRT contains no timed captions")
    if any(start < 0 or end <= start for start, end in intervals):
        raise RuntimeError("SRT contains an invalid interval")
    if any(
        intervals[index][0] < intervals[index - 1][1] - 0.02
        for index in range(1, len(intervals))
    ):
        raise RuntimeError("SRT intervals overlap")
    if intervals[-1][1] > duration + 0.25:
        raise RuntimeError("SRT extends beyond the release video")
    if "<lang" in text or "<prosody" in text or "<break" in text:
        raise RuntimeError("SRT contains SSML markup")
    return {
        "caption_count": len(intervals),
        "first_caption_seconds": intervals[0][0],
        "last_caption_seconds": intervals[-1][1],
    }


def decode_float_audio(path: Path, sample_rate: int = 16000) -> np.ndarray:
    result = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-f",
            "f32le",
            "-",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return np.frombuffer(result.stdout, dtype="<f4")


def longest_true_run(mask: np.ndarray, hop_seconds: float) -> float:
    longest = current = 0
    for value in mask:
        current = current + 1 if value else 0
        longest = max(longest, current)
    return longest * hop_seconds


def analyze_segment_audio(path: Path) -> dict[str, Any]:
    sample_rate = 16000
    samples = decode_float_audio(path, sample_rate)
    if samples.size < sample_rate:
        raise RuntimeError(f"Narration segment is unexpectedly short: {path}")
    frame_size = int(0.04 * sample_rate)
    hop = int(0.02 * sample_rate)
    frames = np.lib.stride_tricks.sliding_window_view(samples, frame_size)[::hop]
    rms = np.sqrt(np.mean(np.square(frames), axis=1) + 1e-12)
    rms_db = 20 * np.log10(rms)
    internal = rms_db[10:-10] if rms_db.size > 20 else rms_db
    longest_internal_silence = longest_true_run(internal < -50.0, hop / sample_rate)

    pitch_values: list[float] = []
    pitch_positions: list[int] = []
    window = np.hanning(frame_size)
    minimum_lag = sample_rate // 350
    maximum_lag = sample_rate // 65
    for index, (frame, level) in enumerate(zip(frames, rms_db)):
        if level < -38:
            continue
        centered = (frame - np.mean(frame)) * window
        correlation = np.correlate(centered, centered, mode="full")[frame_size - 1 :]
        if correlation[0] <= 1e-8:
            continue
        region = correlation[minimum_lag:maximum_lag]
        lag = int(np.argmax(region)) + minimum_lag
        strength = correlation[lag] / correlation[0]
        if strength >= 0.32:
            pitch_values.append(sample_rate / lag)
            pitch_positions.append(index)

    median_pitch = float(np.median(pitch_values)) if pitch_values else 0.0
    deep_mask = np.zeros(rms_db.size, dtype=bool)
    if median_pitch:
        threshold = max(65.0, median_pitch * 0.55)
        for position, pitch in zip(pitch_positions, pitch_values):
            deep_mask[position] = pitch < threshold
    longest_deep_run = longest_true_run(deep_mask, hop / sample_rate)

    boundary_samples = int(0.012 * sample_rate)
    head_peak = float(np.max(np.abs(samples[:boundary_samples])))
    tail_peak = float(np.max(np.abs(samples[-boundary_samples:])))
    absolute_peak = float(np.max(np.abs(samples)))
    passed = (
        longest_internal_silence <= 1.25
        and longest_deep_run <= 0.45
        and absolute_peak < 1.0
        and head_peak < 0.20
        and tail_peak < 0.20
    )
    return {
        "file": path.name,
        "duration_seconds": samples.size / sample_rate,
        "peak_linear": absolute_peak,
        "head_peak_linear": head_peak,
        "tail_peak_linear": tail_peak,
        "longest_internal_silence_seconds": longest_internal_silence,
        "median_voiced_pitch_hz": median_pitch,
        "longest_deep_pitch_run_seconds": longest_deep_run,
        "passed": passed,
    }


def narration_segment_qa() -> list[dict[str, Any]]:
    cache_path = VOICE_CACHE / "cache.json"
    if not cache_path.is_file():
        raise RuntimeError("Voiceover cache is missing")
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    locale = VOICE_LOCALES.get(PROMO_VOICE, "fr-CA")
    checks: list[dict[str, Any]] = []
    for name, narration in NARRATION_SEGMENTS.items():
        expected = ssml(narration, rate=PROMO_RATE, locale=locale)
        entries = [
            item
            for item in cache
            if item.get("input_text") == expected
            and item.get("input_data", {}).get("config", {}).get("voice") == PROMO_VOICE
        ]
        if not entries:
            raise RuntimeError(f"No MAI cache entry found for narration segment {name!r}")
        audio_path = VOICE_CACHE / entries[-1]["final_audio"]
        if not audio_path.is_file():
            raise RuntimeError(f"Cached narration file is missing: {audio_path}")
        result = analyze_segment_audio(audio_path)
        result["segment"] = name
        result["sha256"] = sha256_file(audio_path)
        checks.append(result)
    if not all(check["passed"] for check in checks):
        failures = [check["segment"] for check in checks if not check["passed"]]
        raise RuntimeError("Narration segment audio QA failed: " + ", ".join(failures))
    return checks


def validate_release(
    video: Path,
    srt_path: Path,
    wav_info: dict[str, int],
    loudness: dict[str, float],
) -> tuple[dict[str, Any], dict[str, Any]]:
    media = media_summary(video)
    duration = media["duration_seconds"]
    video_info = media["video"]
    audio_info = media["audio"]
    errors: list[str] = []
    if not 60.0 <= duration <= 90.0:
        errors.append(f"duration {duration:.3f}s is outside 60–90s")
    if (video_info["width"], video_info["height"]) != (1920, 1080):
        errors.append("video is not 1920×1080")
    if abs(video_info["fps"] - 60.0) > 0.001:
        errors.append(f"nominal frame rate is {video_info['fps']}")
    if abs(video_info["average_fps"] - 60.0) > 0.05:
        errors.append(f"average frame rate is {video_info['average_fps']}")
    if video_info["codec"] != "h264" or video_info["pixel_format"] != "yuv420p":
        errors.append("video is not H.264/yuv420p")
    if audio_info["codec"] != "aac":
        errors.append("audio is not AAC")
    if audio_info["sample_rate"] != 48000 or audio_info["channels"] != 1:
        errors.append("audio is not 48 kHz mono")
    if audio_info["maximum_packet_gap_seconds"] > 0.025:
        errors.append(
            f"audio packet gap is {audio_info['maximum_packet_gap_seconds']:.4f}s"
        )
    if abs(audio_info["duration_seconds"] - duration) > 0.05:
        errors.append("audio timestamps do not continue through the full video")
    if wav_info["sample_rate"] != 48000 or wav_info["channels"] != 1:
        errors.append("WAV is not 48 kHz mono")
    if abs(loudness["integrated_lufs"] - TARGET_LUFS) > 0.7:
        errors.append(f"integrated loudness is {loudness['integrated_lufs']:.2f} LUFS")
    if loudness["true_peak_dbfs"] > MAX_TRUE_PEAK:
        errors.append(f"true peak is {loudness['true_peak_dbfs']:.2f} dBFS")
    subtitles = validate_srt(srt_path, duration)
    if errors:
        raise RuntimeError("Release validation failed:\n- " + "\n- ".join(errors))
    return media, subtitles


def copy_verified(files: list[Path], destination: Path) -> list[dict[str, str]]:
    destination.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []
    for source in files:
        target = destination / source.name
        shutil.copy2(source, target)
        source_hash = sha256_file(source)
        target_hash = sha256_file(target)
        if source_hash != target_hash:
            raise RuntimeError(f"Drive copy hash mismatch: {target}")
        results.append(
            {
                "source": str(source),
                "destination": str(target),
                "sha256": source_hash,
            }
        )
    return results


def build_report_text(manifest: dict[str, Any]) -> str:
    output = manifest["outputs"]
    media = manifest["validation"]["media"]
    loudness = manifest["validation"]["loudness_after"]
    lines = [
        "# UQAM short mathematics promo — build report",
        "",
        f"- Build time: {manifest['built_at']}",
        f"- Video: {Path(output['video']['path']).name}",
        f"- Duration: {media['duration_seconds']:.3f} s",
        "- Picture: 1920×1080, 60 fps, H.264/yuv420p",
        "- Sound: MAI-Voice-2, Canada Central, +2%, AAC 48 kHz mono; no music",
        (
            f"- Loudness: {loudness['integrated_lufs']:.2f} LUFS, "
            f"{loudness['true_peak_dbfs']:.2f} dBFS true peak"
        ),
        f"- Narration normalization applied: {manifest['normalization_applied']}",
        (
            f"- Subtitles: {manifest['validation']['subtitles']['caption_count']} "
            "synchronized French cues"
        ),
        "- Visual QA: explicitly approved after inspection of representative frames.",
        "- Audio QA: all six individual MAI clips passed silence, clipping, boundary, and sustained deep-pitch scans.",
        "- Existing programme-overview files were not modified or replaced.",
        "",
        "Claim sources:",
        *[f"- {url}" for url in CLAIM_SOURCES],
        "",
    ]
    if manifest.get("drive_copy"):
        lines.append(
            f"Google Drive: {len(manifest['drive_copy']) + 2} stamped files copied and SHA-256 verified."
        )
        lines.append("")
    return "\n".join(lines)


def deliver_existing_release(release_dir: Path, drive_dir: Path) -> int:
    release_dir = release_dir.resolve()
    manifests = list(release_dir.glob("*_build_manifest.json"))
    reports = list(release_dir.glob("*_build_report.md"))
    if len(manifests) != 1 or len(reports) != 1:
        raise RuntimeError("Release directory must contain one build manifest and one report")
    build_manifest_path = manifests[0]
    build_report_path = reports[0]
    manifest = json.loads(build_manifest_path.read_text(encoding="utf-8"))
    verify_manifest_output_hashes(manifest)
    outputs = manifest["outputs"]
    deliverables = [
        Path(outputs["video"]["path"]),
        Path(outputs["subtitles"]["path"]),
        Path(outputs["narration_wav"]["path"]),
        Path(outputs["source_credit_manifest"]["path"]),
    ]
    manifest["drive_copy"] = copy_verified(deliverables, drive_dir.resolve())
    build_manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    build_report_path.write_text(build_report_text(manifest), encoding="utf-8")
    copy_verified([build_manifest_path, build_report_path], drive_dir.resolve())
    print(f"DRIVE {drive_dir.resolve()}")
    print(f"FILES {len(deliverables) + 2}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality", choices=("qh",), default="qh")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument(
        "--visual-qa-approved",
        action="store_true",
        help="confirm that the extracted representative frames were inspected",
    )
    parser.add_argument("--stamp", help="YYYYMMDD_HHMMSS; defaults to Toronto local time")
    parser.add_argument("--source-archive", type=Path)
    parser.add_argument("--copy-to-drive", action="store_true")
    parser.add_argument("--drive-dir", type=Path, default=DEFAULT_DRIVE_DIR)
    parser.add_argument(
        "--deliver-existing",
        type=Path,
        help="copy and verify an already validated release directory",
    )
    args = parser.parse_args()

    if args.deliver_existing:
        return deliver_existing_release(args.deliver_existing, args.drive_dir)

    environment = prepare_render_environment()
    assets = preflight_assets(
        require_logo=environment.get("UQAM_USE_OFFICIAL_LOGO") == "1"
    )
    if args.visual_qa_approved and not args.skip_render:
        raise RuntimeError(
            "--visual-qa-approved requires --skip-render after inspecting the extracted frames"
        )
    if args.skip_render:
        raw_video = RAW_DIR / f"{ARTIFACT_SLUG}.mp4"
        raw_srt = RAW_DIR / f"{ARTIFACT_SLUG}.srt"
        if not raw_video.is_file() or not raw_srt.is_file():
            raise RuntimeError("--skip-render requires existing shared MP4 and SRT outputs")
        render_provenance = verify_render_provenance(
            raw_video, raw_srt, environment, args.quality
        )
    else:
        raw_video, raw_srt = render_master(environment, args.quality)
        render_provenance = json.loads(RENDER_PROVENANCE.read_text(encoding="utf-8"))

    qa_dir = RAW_DIR / "qa" / sha256_file(raw_video)[:12]
    qa_frames = extract_representative_frames(raw_video, qa_dir)
    if not args.visual_qa_approved:
        print(f"VISUAL_QA_REQUIRED {qa_dir}")
        print("Inspect the representative frames, then rerun with --skip-render --visual-qa-approved.")
        return 2

    stamp = args.stamp or datetime.now(ZoneInfo("America/Toronto")).strftime(
        "%Y%m%d_%H%M%S"
    )
    stem = f"uqam_bac_mathematiques_promo_fr_{stamp}"
    release_dir = RAW_DIR / "releases" / stamp
    release_dir.mkdir(parents=True, exist_ok=False)
    video = release_dir / f"{stem}.mp4"
    srt_path = release_dir / f"{stem}.srt"
    wav_path = release_dir / f"{stem}_narration.wav"
    source_manifest_path = release_dir / f"{stem}_source_credit_manifest.json"
    build_manifest_path = release_dir / f"{stem}_build_manifest.json"
    build_report_path = release_dir / f"{stem}_build_report.md"

    normalized, loudness_before, loudness_after = normalize_if_needed(raw_video, video)
    shutil.copy2(raw_srt, srt_path)
    wav_info = extract_wav(video, wav_path)
    shutil.copy2(ASSET_DIR / "sources.json", source_manifest_path)
    media, subtitles = validate_release(video, srt_path, wav_info, loudness_after)
    segment_qa = narration_segment_qa()

    source_archive: dict[str, str] | None = None
    if args.source_archive:
        archive = args.source_archive.resolve()
        if not archive.is_file():
            raise RuntimeError(f"Source archive does not exist: {archive}")
        source_archive = {"path": str(archive), "sha256": sha256_file(archive)}

    deliverables = [video, srt_path, wav_path, source_manifest_path]
    drive_copy: list[dict[str, str]] = []
    if args.copy_to_drive:
        drive_copy = copy_verified(deliverables, args.drive_dir.resolve())

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "title": "UQAM short mathematics recruitment film",
        "built_at": datetime.now(ZoneInfo("America/Toronto")).isoformat(),
        "stamp": stamp,
        "scene": {
            "path": str(SCENE_FILE),
            "sha256": sha256_file(SCENE_FILE),
            "class": SCENE_CLASS,
        },
        "source_archive": source_archive,
        "configuration": {
            "voice_selector": "MAI-Voice-2",
            "azure_voice": PROMO_VOICE,
            "azure_region": MAI_VOICE_2_REGION,
            "narration_rate": PROMO_RATE,
            "music": False,
            "real_photos": True,
            "vector_fallback_available": True,
            "visible_photo_credits": False,
            "official_logo_final_card_only": True,
            "cta": CTA_URL,
            "cta_display": CTA_DISPLAY,
            "font": "Roboto",
            "typography_renderer": "Pillow/FreeType",
            "text_raster_scale": TEXT_RASTER_SCALE,
            "font_sha256": sha256_file(FONT_PATH),
            "visual_qa_approved": True,
        },
        "sources": {
            "claims": CLAIM_SOURCES,
            "video_guide": UQAM_VIDEO_GUIDE,
            "asset_inventory": assets,
            "source_files": source_file_inventory(environment),
            "render_provenance": render_provenance,
            "official_logo": {
                "path": str(LOGO_PATH),
                "sha256": sha256_file(LOGO_PATH) if LOGO_PATH.is_file() else None,
                "use": (
                    "Official UQAM logo included on the final card after explicit approval."
                    if environment.get("UQAM_USE_OFFICIAL_LOGO") == "1"
                    else "Official UQAM logo not used in this build; approval is not inferred."
                ),
            },
        },
        "software": {
            "python": sys.version.split()[0],
            "manim": package_version("manim"),
            "manim_voiceover": package_version("manim-voiceover"),
            "azure_speech": package_version("azure-cognitiveservices-speech"),
            "pillow": package_version("Pillow"),
            "ffmpeg": capture(["ffmpeg", "-version"]).splitlines()[0],
            "ffprobe": capture(["ffprobe", "-version"]).splitlines()[0],
        },
        "normalization_applied": normalized,
        "validation": {
            "media": media,
            "loudness_before": loudness_before,
            "loudness_after": loudness_after,
            "wav": wav_info,
            "subtitles": subtitles,
            "narration_segments": segment_qa,
            "representative_frames": qa_frames,
        },
        "outputs": {
            "video": {"path": str(video), "sha256": sha256_file(video)},
            "subtitles": {"path": str(srt_path), "sha256": sha256_file(srt_path)},
            "narration_wav": {"path": str(wav_path), "sha256": sha256_file(wav_path)},
            "source_credit_manifest": {
                "path": str(source_manifest_path),
                "sha256": sha256_file(source_manifest_path),
            },
        },
        "drive_copy": drive_copy,
    }
    build_manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    build_report_path.write_text(build_report_text(manifest), encoding="utf-8")

    if args.copy_to_drive:
        copy_verified([build_manifest_path, build_report_path], args.drive_dir.resolve())

    print(f"VIDEO {video}")
    print(f"SRT {srt_path}")
    print(f"WAV {wav_path}")
    print(f"MANIFEST {build_manifest_path}")
    print(f"REPORT {build_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

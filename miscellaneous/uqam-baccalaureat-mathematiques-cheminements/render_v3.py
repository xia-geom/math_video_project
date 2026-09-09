#!/usr/bin/env python3
"""Render the 3:35 V3 UQAM mathematics-program overview.

The V3 pipeline has three deliberate sources of truth:

* ``v3_storyboard_data.py`` defines the exact 215-second scene clock;
* ``voiceover_v3_fr.txt`` defines the authored sentence-level narration;
* Azure bookmark offsets stored by ``v3_audio.py`` drive subtitles and the
  semantic visual reveals.

No word-count timing and no speech-engine fallback are used.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import tomllib
from typing import Iterable, Mapping
import wave

# MoviePy must use the same system FFmpeg binary that is checked below.
if system_ffmpeg := shutil.which("ffmpeg"):
    os.environ.setdefault("IMAGEIO_FFMPEG_EXE", system_ffmpeg)

import numpy as np
from moviepy import VideoClip
from PIL import Image, ImageDraw, ImageFont

import v3_audio
import v3_storyboard_data as storyboard
import v3_visuals


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "project-manifest.toml"


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    with path.open("rb") as handle:
        manifest = tomllib.load(handle)
    if manifest.get("schema_version") != 1:
        raise RuntimeError(f"Unsupported manifest schema in {path}")
    if "v3" not in manifest:
        raise RuntimeError(f"V3 configuration is missing from {path}")
    return manifest


MANIFEST = load_manifest()
V3 = MANIFEST["v3"]
V3_NARRATION = V3["narration"]
V3_RENDER = V3["render"]
V3_ARTIFACTS = V3["artifacts"]

BUILD_DIR = ROOT / V3_ARTIFACTS["build_dir"]
AUDIO_DIR = BUILD_DIR / "audio"
SCENE_DIR = BUILD_DIR / "scenes"
MASTER_AUDIO_PATH = AUDIO_DIR / "v3-master.wav"
DIST_DIR = ROOT / V3_ARTIFACTS["dist_dir"]
PREVIEW_DIR = DIST_DIR / "previews"
NARRATION_PATH = ROOT / V3_NARRATION["source"]

SOURCE_YEAR_SLUG = MANIFEST["project"]["source_year"].replace("–", "-")
ARTIFACT_STEM = V3_ARTIFACTS["stem_template"].format(
    source_year=SOURCE_YEAR_SLUG
)

WIDTH = int(V3_RENDER["width"])
HEIGHT = int(V3_RENDER["height"])
FPS = int(V3_RENDER["fps"])
TARGET_DURATION = float(V3["target_duration_seconds"])
DEFAULT_AZURE_VOICE = os.getenv(
    "MANIM_VOICE",
    str(V3_NARRATION["voice"]),
)
BACKGROUND_RGB = (247, 248, 250)


@dataclass
class SceneRuntime:
    spec: storyboard.SceneSpec
    narration: v3_audio.Narration
    audio_path: Path
    metadata: dict[str, object] | None = None

    @property
    def duration(self) -> float:
        return self.spec.duration


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def _version_tuple(value: str) -> tuple[int, ...]:
    match = re.match(r"(\d+(?:\.\d+)*)", value)
    return tuple(int(part) for part in match.group(1).split(".")) if match else ()


def wrap_subtitle(text: str, width: int = 42) -> tuple[str, ...]:
    lines = tuple(
        textwrap.wrap(
            text,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )
    if not lines or len(lines) > 2:
        raise ValueError(
            f"Subtitle cue must fit on at most two {width}-character lines: "
            f"{text!r}"
        )
    return lines


def build_runtimes() -> list[SceneRuntime]:
    storyboard.validate_storyboard()
    narrations = v3_audio.load_narration(NARRATION_PATH)
    if storyboard.SCENE_IDS != v3_audio.EXPECTED_SCENE_IDS:
        raise RuntimeError("V3 scene IDs disagree between storyboard and narration")
    runtimes = []
    for spec in storyboard.SCENES:
        narration = narrations[spec.id]
        if len(narration.cues) != len(spec.narration_cue_ids):
            raise RuntimeError(
                f"{spec.id} has {len(narration.cues)} narration cues but "
                f"{len(spec.narration_cue_ids)} storyboard cue IDs"
            )
        for cue in narration.cues:
            wrap_subtitle(cue)
        runtimes.append(
            SceneRuntime(
                spec=spec,
                narration=narration,
                audio_path=AUDIO_DIR / f"{spec.id}.wav",
            )
        )
    return runtimes


def select_runtimes(
    runtimes: list[SceneRuntime],
    scene_id: str | None,
) -> list[tuple[int, SceneRuntime]]:
    indexed = list(enumerate(runtimes, start=1))
    if scene_id is None:
        return indexed
    selected = [
        (index, runtime)
        for index, runtime in indexed
        if runtime.spec.id == scene_id
    ]
    if not selected:
        available = ", ".join(runtime.spec.id for _, runtime in indexed)
        raise SystemExit(f"Unknown scene: {scene_id}\nAvailable scenes: {available}")
    return selected


def azure_config(
    runtime: SceneRuntime,
    *,
    voice: str = DEFAULT_AZURE_VOICE,
) -> v3_audio.AzureConfig:
    rate = V3_NARRATION.get("scene_rates", {}).get(
        runtime.spec.id,
        V3_NARRATION["rate"],
    )
    return v3_audio.AzureConfig(
        voice=voice,
        locale=MANIFEST["project"]["language"],
        rate=str(rate),
        lead_silence_ms=int(V3_NARRATION["lead_silence_ms"]),
        tail_silence_ms=int(V3_NARRATION["minimum_tail_silence_ms"]),
        intercue_break_ms=int(V3_NARRATION["intercue_break_ms"]),
        target_duration_ms=round(runtime.duration * 1000),
        target_dbfs=float(V3_NARRATION["target_dbfs"]),
        output_format=str(V3_NARRATION["azure_output_format"]),
    )


def prepare_audio(
    runtimes: Iterable[SceneRuntime],
    *,
    tts: str,
    voice: str = DEFAULT_AZURE_VOICE,
) -> None:
    """Generate or strictly validate only the supplied scene recordings."""

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for runtime in runtimes:
        config = azure_config(runtime, voice=voice)
        if tts == "azure":
            print(f"Azure narration: {runtime.spec.id}", flush=True)
            try:
                runtime.metadata = v3_audio.generate_azure(
                    runtime.narration,
                    runtime.audio_path,
                    config=config,
                )
            except Exception as exc:
                raise RuntimeError(
                    f"Azure narration failed for {runtime.spec.id}: {exc}"
                ) from exc
        elif tts == "existing":
            try:
                runtime.metadata = v3_audio.validate_existing(
                    runtime.narration,
                    runtime.audio_path,
                    config=config,
                )
            except v3_audio.StaleAudioError as exc:
                raise RuntimeError(
                    f"{exc}\nRegenerate this exact segment with:\n"
                    f".venv/bin/python render_v3.py --scene "
                    f"{runtime.spec.id} --tts azure --audio-only"
                ) from None
        else:
            raise ValueError(f"Unsupported V3 narration mode: {tts}")


def cue_starts(runtime: SceneRuntime) -> tuple[float, ...]:
    if runtime.metadata is None:
        return ()
    cues = runtime.metadata.get("cues")
    if not isinstance(cues, list):
        raise ValueError(f"{runtime.spec.id} metadata has no cue list")
    return tuple(
        int(cue["start_ticks_100ns"]) / v3_audio.TICKS_PER_SECOND
        for cue in cues
    )


# These reveals introduce the exact subject named by the corresponding cue.
# Structural motion that teaches the layout remains on the storyboard clock.
SEMANTIC_CUE_ACTIONS: dict[str, dict[str, int]] = {
    "v3_05_common_foundation": {
        "show_first_table": 0,
        "separate_paths": 3,
    },
    "v3_06_fundamental_mathematics": {
        "show_analysis": 0,
        "show_algebra": 2,
        "show_geometry": 4,
    },
    "v3_07_statistics": {
        "show_collection": 0,
        "show_models": 2,
        "show_learning": 4,
    },
    "v3_08_mathematics_computing": {
        "show_programming": 0,
        "show_algorithms": 1,
        "show_databases": 3,
    },
    "v3_09_computing_profiles": {
        "show_common_card": 0,
        "highlight_math_profile": 1,
        "highlight_stat_profile": 2,
    },
    "v3_11_guide": {
        "show_guide": 0,
        "show_guide_title": 1,
        "show_detail_load": 2,
        "show_detail_choices": 3,
        "show_url": 4,
    },
}


def aligned_actions(runtime: SceneRuntime) -> dict[str, tuple[float, float]]:
    """Return absolute local action windows, with semantic reveals cue-aligned."""

    windows = {
        window.action: (window.start, window.end)
        for window in v3_visuals.DEFAULT_ACTIONS[runtime.spec.id]
    }
    starts = cue_starts(runtime)
    for action, cue_index in SEMANTIC_CUE_ACTIONS.get(
        runtime.spec.id,
        {},
    ).items():
        if cue_index >= len(starts) or action not in windows:
            continue
        start = starts[cue_index]
        end = min(runtime.duration, start + 0.50)
        if runtime.spec.id == "v3_11_guide" and end > 12.5:
            # Preserve the authored 4.5-second final still hold.
            continue
        if end > start:
            windows[action] = (start, end)
    if runtime.spec.id == "v3_05_common_foundation" and len(starts) >= 4:
        # This is a six-chip sequence, not a single reveal.  Give each common
        # subject a readable hold between the cue that names the mathematical
        # foundations and the cue that starts separating the pathways.
        windows["highlight_foundation"] = (starts[1], starts[3])
    return windows


def make_frame(runtime: SceneRuntime):
    actions = aligned_actions(runtime)

    def frame(t: float) -> np.ndarray:
        result = v3_visuals.draw_scene(
            runtime.spec.id,
            t,
            runtime.duration,
            actions,
        )
        if (
            result.shape != (HEIGHT, WIDTH, 3)
            or result.dtype != np.uint8
        ):
            raise RuntimeError(
                f"Invalid frame returned for {runtime.spec.id}: "
                f"shape={result.shape}, dtype={result.dtype}"
            )
        return result

    return frame


def scene_video_path(index: int, runtime: SceneRuntime) -> Path:
    return SCENE_DIR / f"{index:02d}-{runtime.spec.id}.mp4"


def render_scene(runtime: SceneRuntime, index: int) -> Path:
    if runtime.metadata is None:
        raise RuntimeError(f"Narration was not prepared for {runtime.spec.id}")
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    destination = scene_video_path(index, runtime)
    with tempfile.TemporaryDirectory(
        prefix=f".{runtime.spec.id}-",
        dir=SCENE_DIR,
    ) as temporary:
        video_only_path = Path(temporary) / "video-only.mp4"
        temporary_path = Path(temporary) / destination.name
        video = VideoClip(
            frame_function=make_frame(runtime),
            duration=runtime.duration,
        )
        try:
            video.write_videofile(
                str(video_only_path),
                fps=FPS,
                codec=str(V3_RENDER["video_codec"]),
                bitrate=str(V3_RENDER["video_bitrate"]),
                preset=str(V3_RENDER.get("preset", "veryfast")),
                threads=int(V3_RENDER.get("threads", 2)),
                audio=False,
                pixel_format=str(V3_RENDER["pixel_format"]),
                logger=None,
            )
        finally:
            video.close()
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(video_only_path),
                "-i",
                str(runtime.audio_path),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                str(V3_RENDER["audio_codec"]),
                "-b:a",
                str(V3_RENDER["audio_bitrate"]),
                "-ar",
                "48000",
                "-ac",
                "1",
                "-t",
                f"{runtime.duration:.6f}",
                "-movflags",
                "+faststart",
                str(temporary_path),
            ],
            check=True,
        )
        os.replace(temporary_path, destination)
    validate_video(destination, expected_duration=runtime.duration)
    return destination


def _concat_line(path: Path) -> str:
    # FFmpeg concat escaping for a single quote inside a single-quoted path.
    escaped = str(path.resolve()).replace("'", "'\\''")
    return f"file '{escaped}'"


def build_master_audio(runtimes: list[SceneRuntime]) -> Path:
    """Concatenate the exact PCM scene clocks without resampling or padding."""

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    expected_total_frames = round(TARGET_DURATION * 48_000)
    total_frames = 0
    with tempfile.TemporaryDirectory(prefix=".master-audio-", dir=AUDIO_DIR) as temp:
        temporary_path = Path(temp) / MASTER_AUDIO_PATH.name
        with wave.open(str(temporary_path), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(48_000)
            output.setcomptype("NONE", "not compressed")
            for runtime in runtimes:
                with wave.open(str(runtime.audio_path), "rb") as source:
                    if (
                        source.getnchannels() != 1
                        or source.getsampwidth() != 2
                        or source.getframerate() != 48_000
                        or source.getcomptype() != "NONE"
                    ):
                        raise RuntimeError(
                            f"Unexpected PCM format in {runtime.audio_path}"
                        )
                    expected_frames = round(runtime.duration * 48_000)
                    if source.getnframes() != expected_frames:
                        raise RuntimeError(
                            f"PCM duration mismatch in {runtime.audio_path}"
                        )
                    payload = source.readframes(source.getnframes())
                    output.writeframesraw(payload)
                    total_frames += expected_frames
            output.writeframes(b"")
        if total_frames != expected_total_frames:
            raise RuntimeError(
                f"Master PCM has {total_frames} frames; "
                f"expected {expected_total_frames}"
            )
        os.replace(temporary_path, MASTER_AUDIO_PATH)
    return MASTER_AUDIO_PATH


def assemble(
    scene_paths: list[Path],
    runtimes: list[SceneRuntime],
) -> tuple[Path, Path]:
    if len(scene_paths) != int(V3["scene_count"]):
        raise ValueError(
            f"Assembly requires {V3['scene_count']} scenes; "
            f"received {len(scene_paths)}"
        )
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    concat_path = SCENE_DIR / "concat-v3.txt"
    concat_path.write_text(
        "\n".join(
            (
                f"{_concat_line(path)}\n"
                f"duration {runtime.duration:.6f}"
            )
            for path, runtime in zip(scene_paths, runtimes)
        )
        + "\n",
        encoding="utf-8",
    )
    master_audio = build_master_audio(runtimes)
    output = DIST_DIR / f"{ARTIFACT_STEM}.mp4"
    with tempfile.TemporaryDirectory(prefix=".assemble-v3-", dir=DIST_DIR) as temp:
        video_only_path = Path(temp) / "video-only.mp4"
        temporary_path = Path(temp) / output.name
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-map",
                "0:v:0",
                "-an",
                "-c",
                "copy",
                str(video_only_path),
            ],
            check=True,
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(video_only_path),
                "-i",
                str(master_audio),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                str(V3_RENDER["audio_codec"]),
                "-b:a",
                str(V3_RENDER["audio_bitrate"]),
                "-ar",
                "48000",
                "-ac",
                "1",
                "-t",
                f"{TARGET_DURATION:.6f}",
                "-movflags",
                "+faststart",
                str(temporary_path),
            ],
            check=True,
        )
        os.replace(temporary_path, output)
    return output, master_audio


def srt_time(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1_000)
    return (
        f"{hours:02d}:{minutes:02d}:{seconds:02d},"
        f"{milliseconds:03d}"
    )


def write_srt(runtimes: list[SceneRuntime]) -> Path:
    """Write sentence-level cues directly from stored Azure bookmarks."""

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    path = DIST_DIR / f"{ARTIFACT_STEM}.srt"
    blocks = []
    cue_number = 1
    previous_end_ms = -1
    for runtime in runtimes:
        if runtime.metadata is None:
            raise RuntimeError(
                f"Narration metadata was not prepared for {runtime.spec.id}"
            )
        intervals = v3_audio.subtitle_intervals(
            runtime.narration,
            runtime.metadata,
        )
        for interval in intervals:
            if interval.start < 0 or interval.end > runtime.duration + 0.001:
                raise RuntimeError(
                    f"Subtitle interval falls outside {runtime.spec.id}"
                )
            if interval.end <= interval.start:
                raise RuntimeError(
                    f"Subtitle interval is empty in {runtime.spec.id}"
                )
            lines = wrap_subtitle(interval.text)
            global_start = runtime.spec.start + interval.start
            global_end = runtime.spec.start + interval.end
            start_ms = round(global_start * 1000)
            end_ms = round(global_end * 1000)
            if end_ms <= start_ms:
                raise RuntimeError(
                    f"Subtitle cue collapses after millisecond rounding in "
                    f"{runtime.spec.id}"
                )
            if start_ms < previous_end_ms:
                raise RuntimeError(
                    f"Subtitle cues overlap after millisecond rounding in "
                    f"{runtime.spec.id}"
                )
            blocks.append(
                f"{cue_number}\n"
                f"{srt_time(global_start)} --> {srt_time(global_end)}\n"
                f"{chr(10).join(lines)}\n"
            )
            cue_number += 1
            previous_end_ms = end_ms
    expected_cues = sum(len(runtime.narration.cues) for runtime in runtimes)
    if cue_number - 1 != expected_cues:
        raise RuntimeError("Subtitle cue count does not match narration")
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


def _preview_time(runtime: SceneRuntime) -> float:
    preferred = {
        "v3_01_opening": 5.8,
        "v3_02_reading_the_table": 13.0,
        "v3_03_course_load": 12.5,
        "v3_04_complementary_column": 13.0,
        "v3_05_common_foundation": 13.5,
        "v3_06_fundamental_mathematics": 29.0,
        "v3_07_statistics": 29.0,
        "v3_08_mathematics_computing": 30.0,
        "v3_09_computing_profiles": 13.5,
        "v3_10_comparison": 16.0,
        "v3_11_guide": 15.0,
    }
    return preferred[runtime.spec.id]


def write_preview(runtime: SceneRuntime, index: int) -> Path:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    path = PREVIEW_DIR / f"{index:02d}-{runtime.spec.id}.png"
    Image.fromarray(make_frame(runtime)(_preview_time(runtime))).save(path)
    return path


def build_storyboard(
    indexed_runtimes: list[tuple[int, SceneRuntime]],
) -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    columns = 3
    thumb_width, thumb_height = 426, 240
    label_height = 42
    rows = math.ceil(len(indexed_runtimes) / columns)
    board = Image.new(
        "RGB",
        (
            columns * thumb_width,
            rows * (thumb_height + label_height),
        ),
        "white",
    )
    draw = ImageDraw.Draw(board)
    label_font = ImageFont.truetype(
        str(ROOT / MANIFEST["fonts"]["bold"]),
        14,
    )
    for position, (index, runtime) in enumerate(indexed_runtimes):
        frame = Image.fromarray(
            make_frame(runtime)(_preview_time(runtime))
        ).resize(
            (thumb_width, thumb_height),
            Image.Resampling.LANCZOS,
        )
        x = (position % columns) * thumb_width
        y = (position // columns) * (thumb_height + label_height)
        board.paste(frame, (x, y))
        label = f"{index:02d} · {runtime.spec.title}"
        draw.text(
            (x + 10, y + thumb_height + 10),
            label,
            font=label_font,
            fill=(24, 33, 43),
        )
    path = DIST_DIR / f"{ARTIFACT_STEM}-storyboard.png"
    board.save(path)
    return path


def probe_video(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            (
                "format=duration:"
                "stream=index,codec_type,codec_name,width,height,"
                "r_frame_rate,avg_frame_rate,pix_fmt,sample_rate,channels"
                ",duration,nb_frames"
            ),
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def validate_video(
    path: Path,
    *,
    expected_duration: float,
) -> dict:
    probe = probe_video(path)
    video_streams = [
        stream
        for stream in probe.get("streams", [])
        if stream.get("codec_type") == "video"
    ]
    audio_streams = [
        stream
        for stream in probe.get("streams", [])
        if stream.get("codec_type") == "audio"
    ]
    problems = []
    if len(video_streams) != 1:
        problems.append("expected exactly one video stream")
    else:
        video = video_streams[0]
        if video.get("codec_name") != "h264":
            problems.append(f"expected H.264; found {video.get('codec_name')}")
        if (video.get("width"), video.get("height")) != (WIDTH, HEIGHT):
            problems.append(
                f"expected {WIDTH}×{HEIGHT}; "
                f"found {video.get('width')}×{video.get('height')}"
            )
        if video.get("pix_fmt") != V3_RENDER["pixel_format"]:
            problems.append(
                f"expected {V3_RENDER['pixel_format']}; "
                f"found {video.get('pix_fmt')}"
            )
        numerator, denominator = (
            int(value)
            for value in video.get("avg_frame_rate", "0/1").split("/")
        )
        actual_fps = numerator / denominator if denominator else 0
        if not math.isclose(actual_fps, FPS, rel_tol=0, abs_tol=0.001):
            problems.append(f"expected {FPS} fps; found {actual_fps:g}")
        expected_frames = round(expected_duration * FPS)
        try:
            actual_frames = int(video.get("nb_frames", ""))
        except (TypeError, ValueError):
            actual_frames = -1
        if actual_frames != expected_frames:
            problems.append(
                f"expected {expected_frames} video frames; "
                f"found {video.get('nb_frames')}"
            )
    if len(audio_streams) != 1:
        problems.append("expected exactly one audio stream")
    else:
        audio = audio_streams[0]
        if audio.get("codec_name") != "aac":
            problems.append(f"expected AAC; found {audio.get('codec_name')}")
        if audio.get("sample_rate") != "48000":
            problems.append(
                f"expected 48 kHz audio; found {audio.get('sample_rate')}"
            )
        if int(audio.get("channels", 0)) != 1:
            problems.append(
                f"expected mono audio; found {audio.get('channels')} channels"
            )
    actual_duration = float(probe.get("format", {}).get("duration", 0))
    if not math.isclose(
        actual_duration,
        expected_duration,
        rel_tol=0,
        abs_tol=0.08,
    ):
        problems.append(
            f"expected {expected_duration:.3f}s; found "
            f"{actual_duration:.3f}s"
        )
    if problems:
        raise RuntimeError(
            f"Rendered video validation failed for {path}:\n- "
            + "\n- ".join(problems)
        )
    return probe


def _static_hash_checks() -> list[tuple[Path, str, str]]:
    return [
        (
            ROOT / MANIFEST["source"]["guide"]["path"],
            MANIFEST["source"]["guide"]["sha256"],
            "official guide",
        ),
        (
            ROOT / MANIFEST["identity"]["svg"],
            MANIFEST["identity"]["svg_sha256"],
            "official UQAM SVG",
        ),
        (
            ROOT / MANIFEST["identity"]["png"],
            MANIFEST["identity"]["png_sha256"],
            "official UQAM PNG",
        ),
        (
            ROOT / MANIFEST["fonts"]["regular"],
            MANIFEST["fonts"]["regular_sha256"],
            "regular font",
        ),
        (
            ROOT / MANIFEST["fonts"]["bold"],
            MANIFEST["fonts"]["bold_sha256"],
            "bold font",
        ),
        (
            ROOT / MANIFEST["fonts"]["mono"],
            MANIFEST["fonts"]["mono_sha256"],
            "monospace font",
        ),
        (
            ROOT / V3["storyboard"],
            V3["storyboard_sha256"],
            "V3 storyboard",
        ),
        (
            ROOT / V3["source"]["guide_cover"],
            V3["source"]["guide_cover_sha256"],
            "guide cover",
        ),
    ]


def check_environment() -> dict[str, str]:
    problems: list[str] = []
    versions: dict[str, str] = {"python": sys.version.split()[0]}
    running_python = sys.version_info[:3]
    minimum = _version_tuple(MANIFEST["toolchain"]["python_min"])
    maximum = _version_tuple(MANIFEST["toolchain"]["python_max_exclusive"])
    if running_python < minimum or running_python >= maximum:
        problems.append(
            f"Python {MANIFEST['toolchain']['python_min']}–"
            f"{MANIFEST['toolchain']['python_max_exclusive']} "
            f"(exclusive) is required; found {sys.version.split()[0]}"
        )

    for distribution, expected in MANIFEST["toolchain"]["packages"].items():
        try:
            actual = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            problems.append(f"Python package is missing: {distribution}=={expected}")
            continue
        versions[distribution] = actual
        if actual != expected:
            problems.append(
                f"{distribution} must be {expected}; found {actual}"
            )

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg:
        problems.append("FFmpeg is missing from PATH")
    if not ffprobe:
        problems.append("ffprobe is missing from PATH")
    if ffmpeg:
        version_result = subprocess.run(
            [ffmpeg, "-version"],
            check=True,
            capture_output=True,
            text=True,
        )
        match = re.search(r"ffmpeg version\s+([^\s]+)", version_result.stdout)
        version = match.group(1) if match else "unknown"
        versions["ffmpeg"] = version
        if _version_tuple(version) < _version_tuple(
            MANIFEST["toolchain"]["ffmpeg_min"]
        ):
            problems.append(
                f"FFmpeg {MANIFEST['toolchain']['ffmpeg_min']} or newer "
                f"is required; found {version}"
            )
        encoders = subprocess.run(
            [ffmpeg, "-hide_banner", "-encoders"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        for encoder in (
            str(V3_RENDER["video_codec"]),
            str(V3_RENDER["audio_codec"]),
        ):
            if not re.search(rf"\b{re.escape(encoder)}\b", encoders):
                problems.append(f"FFmpeg encoder is unavailable: {encoder}")

    for path, expected_hash, label in _static_hash_checks():
        if not path.is_file():
            problems.append(f"{label} is missing: {path}")
        elif sha256_file(path) != expected_hash:
            problems.append(f"{label} does not match its manifest hash: {path}")

    try:
        runtimes = build_runtimes()
        if len(runtimes) != int(V3["scene_count"]):
            problems.append("V3 scene count does not match the manifest")
        if not math.isclose(
            sum(runtime.duration for runtime in runtimes),
            TARGET_DURATION,
            rel_tol=0,
            abs_tol=0.0001,
        ):
            problems.append("V3 scene durations do not total 215 seconds")
        if (v3_visuals.WIDTH, v3_visuals.HEIGHT, v3_visuals.FPS) != (
            WIDTH,
            HEIGHT,
            FPS,
        ):
            problems.append("V3 visual dimensions or frame rate disagree")
        for runtime in runtimes:
            sample = v3_visuals.draw_scene(
                runtime.spec.id,
                min(0.5, runtime.duration),
                runtime.duration,
            )
            if sample.shape != (HEIGHT, WIDTH, 3) or sample.dtype != np.uint8:
                problems.append(f"Invalid sample frame for {runtime.spec.id}")
    except Exception as exc:
        problems.append(f"V3 source validation failed: {exc}")

    if problems:
        raise RuntimeError(
            "V3 environment check failed:\n- "
            + "\n- ".join(problems)
            + "\nInstall the pinned requirements and retry."
        )
    return versions


def write_build_manifest(
    runtimes: list[SceneRuntime],
    scene_paths: list[Path],
    outputs: Iterable[Path],
    master_audio: Path,
    *,
    tool_versions: Mapping[str, str],
    final_probe: Mapping[str, object],
) -> Path:
    input_paths = [
        MANIFEST_PATH,
        ROOT / "render_v3.py",
        ROOT / "v3_audio.py",
        ROOT / "v3_visuals.py",
        ROOT / "v3_storyboard_data.py",
        ROOT / "program_data.py",
        NARRATION_PATH,
        ROOT / V3["storyboard"],
        ROOT / "requirements.txt",
        ROOT / "requirements.lock",
        ROOT / MANIFEST["source"]["guide"]["path"],
        ROOT / V3["source"]["guide_cover"],
        ROOT / MANIFEST["identity"]["svg"],
        ROOT / MANIFEST["identity"]["png"],
        ROOT / MANIFEST["fonts"]["regular"],
        ROOT / MANIFEST["fonts"]["bold"],
        ROOT / MANIFEST["fonts"]["mono"],
        ROOT / "assets/fonts/OFL-1.1.txt",
    ]
    audio_records = []
    for runtime in runtimes:
        if runtime.metadata is None:
            raise RuntimeError(
                f"Missing narration metadata for {runtime.spec.id}"
            )
        metadata_path = v3_audio.voice_metadata_path(runtime.audio_path)
        audio_records.append(
            {
                "scene_id": runtime.spec.id,
                "start_seconds": runtime.spec.start,
                "duration_seconds": runtime.duration,
                "narration_sha256": runtime.narration.digest,
                "audio": artifact_record(runtime.audio_path),
                "metadata": artifact_record(metadata_path),
                "synthesis_config": runtime.metadata["synthesis_config"],
                "cue_bookmarks": runtime.metadata["cues"],
            }
        )
    payload = {
        "schema": 3,
        "project": {
            "id": MANIFEST["project"]["id"],
            "release": V3["release"],
            "language": MANIFEST["project"]["language"],
            "source_year": MANIFEST["project"]["source_year"],
            "target_duration_seconds": TARGET_DURATION,
        },
        "identity": {
            "provenance_url": MANIFEST["identity"]["provenance_url"],
            "usage_policy_url": MANIFEST["identity"]["usage_policy_url"],
            "authorization": MANIFEST["identity"]["authorization"],
        },
        "timing": {
            "scene_clock": "v3_storyboard_data.py",
            "narration_source": V3_NARRATION["source"],
            "subtitle_source": "azure_bookmarks",
            "semantic_motion_source": "azure_bookmarks",
            "word_count_timing": False,
        },
        "render": {
            **V3_RENDER,
            "actual_fps": FPS,
        },
        "toolchain": dict(tool_versions),
        "inputs": [
            artifact_record(path)
            for path in sorted(input_paths, key=lambda item: item.as_posix())
        ],
        "narration_segments": audio_records,
        "master_audio": artifact_record(master_audio),
        "scene_videos": [
            artifact_record(path)
            for path in scene_paths
        ],
        "outputs": [
            artifact_record(path)
            for path in sorted(outputs, key=lambda item: item.as_posix())
        ],
        "video_probe": final_probe,
    }
    path = DIST_DIR / "build-manifest-v3.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def validated_scene_paths(
    indexed_runtimes: list[tuple[int, SceneRuntime]],
) -> list[Path]:
    paths = []
    for index, runtime in indexed_runtimes:
        path = scene_video_path(index, runtime)
        if not path.is_file():
            raise RuntimeError(
                f"Rendered scene is missing: {path}\n"
                f"Render it with:\n.venv/bin/python render_v3.py "
                f"--scene {runtime.spec.id} --tts existing"
            )
        validate_video(path, expected_duration=runtime.duration)
        paths.append(path)
    return paths


def finalize(
    runtimes: list[SceneRuntime],
    indexed_runtimes: list[tuple[int, SceneRuntime]],
    scene_paths: list[Path],
    tool_versions: Mapping[str, str],
) -> tuple[Path, Path, Path, Path]:
    video, master_audio = assemble(scene_paths, runtimes)
    subtitles = write_srt(runtimes)
    for index, runtime in indexed_runtimes:
        write_preview(runtime, index)
    storyboard_path = build_storyboard(indexed_runtimes)
    probe = validate_video(video, expected_duration=TARGET_DURATION)
    build_manifest = write_build_manifest(
        runtimes,
        scene_paths,
        (video, subtitles, storyboard_path),
        master_audio,
        tool_versions=tool_versions,
        final_probe=probe,
    )
    return video, subtitles, storyboard_path, build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render the exact 3:35 UQAM program-overview V3."
    )
    parser.add_argument("--scene", help="Prepare and render only this scene ID")
    parser.add_argument(
        "--tts",
        choices=("existing", "azure"),
        default="existing",
        help="Strictly validate cached Azure audio or regenerate it",
    )
    parser.add_argument("--azure-voice", default=DEFAULT_AZURE_VOICE)
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Prepare selected narration without rendering video",
    )
    parser.add_argument(
        "--previews-only",
        action="store_true",
        help="Export selected still previews without preparing narration",
    )
    parser.add_argument(
        "--assemble-only",
        action="store_true",
        help="Validate existing audio/scenes and assemble the full release",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate dependencies, assets, narration, timing, and frames",
    )
    args = parser.parse_args()

    operation_count = sum(
        bool(value)
        for value in (
            args.audio_only,
            args.previews_only,
            args.assemble_only,
            args.check,
        )
    )
    if operation_count > 1:
        parser.error(
            "--audio-only, --previews-only, --assemble-only, and --check "
            "are mutually exclusive"
        )
    if args.assemble_only and args.scene:
        parser.error("--assemble-only always requires all eleven scenes")
    if args.assemble_only and args.tts != "existing":
        parser.error("--assemble-only requires --tts existing")

    runtimes = build_runtimes()
    selected = select_runtimes(runtimes, args.scene)
    tool_versions = check_environment()
    if args.check:
        print("V3 environment, assets, narration, timing, and frames: OK")
        for name, version in sorted(tool_versions.items()):
            print(f"{name}={version}")
        return

    if args.previews_only:
        paths = [
            write_preview(runtime, index)
            for index, runtime in selected
        ]
        board = build_storyboard(selected)
        for path in (*paths, board):
            print(path)
        return

    if args.assemble_only:
        prepare_audio(
            runtimes,
            tts="existing",
            voice=args.azure_voice,
        )
        all_indexed = select_runtimes(runtimes, None)
        paths = validated_scene_paths(all_indexed)
        for output in finalize(
            runtimes,
            all_indexed,
            paths,
            tool_versions,
        ):
            print(output)
        return

    selected_runtimes = [runtime for _, runtime in selected]
    prepare_audio(
        selected_runtimes,
        tts=args.tts,
        voice=args.azure_voice,
    )
    if args.audio_only:
        for runtime in selected_runtimes:
            print(runtime.audio_path)
            print(v3_audio.voice_metadata_path(runtime.audio_path))
        return

    rendered = [
        render_scene(runtime, index)
        for index, runtime in selected
    ]
    if args.scene:
        print(rendered[0])
        return

    for output in finalize(
        runtimes,
        selected,
        rendered,
        tool_versions,
    ):
        print(output)


if __name__ == "__main__":
    main()

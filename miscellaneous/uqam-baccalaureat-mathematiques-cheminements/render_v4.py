#!/usr/bin/env python3
"""Render the naturally paced V4 UQAM mathematics-program overview.

V4 deliberately keeps the proven V3 encoding and validation machinery while
isolating every V4 source and artifact.  The adapter below temporarily presents
the V4 modules and paths to the reusable V3 functions; the original V3 module
is restored immediately after each delegated call.

The V4 timing contract is:

* scene durations are authored in :mod:`v4_storyboard_data`;
* ``voiceover_v4_fr.txt`` is the only narration source;
* verified narration cue offsets drive sentence subtitles and semantic reveals;
* Azure may pad a scene with silence, but speech is never accelerated or
  time-stretched to meet a round programme duration.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
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
import tomllib
from typing import Iterable, Iterator, Mapping

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools import tts as project_tts

import render_v3 as v3_pipeline
import v4_audio
import v4_narration
import v4_storyboard_data as storyboard
import v4_visuals
import v4_photos
from tools.uqam_video_review import validate_subtitles


ROOT = Path(__file__).resolve().parent
PROJECT_TTS_PATH = PROJECT_ROOT / "tools/tts.py"
MANIFEST_PATH = ROOT / "project-manifest.toml"

# Keep the closing scene readable after its last reveal, then fade completely
# to the programme background.  The clean-background hold makes the endpoint
# visible in the encoded master rather than just beyond its final frame.
FINAL_FADE_SECONDS = 0.65
FINAL_BACKGROUND_HOLD_SECONDS = 0.50


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    """Load the reproducible manifest and require a complete V4 section."""

    with path.open("rb") as handle:
        manifest = tomllib.load(handle)
    if manifest.get("schema_version") != 1:
        raise RuntimeError(f"Unsupported manifest schema in {path}")
    if "v4" not in manifest:
        raise RuntimeError(f"V4 configuration is missing from {path}")
    required = {"release", "scene_count", "storyboard", "narration", "render", "artifacts"}
    missing = sorted(required - set(manifest["v4"]))
    if missing:
        raise RuntimeError(
            "Incomplete V4 configuration in "
            f"{path}: missing {', '.join(missing)}"
        )
    return manifest


MANIFEST = load_manifest()
V4 = MANIFEST["v4"]
V4_NARRATION = V4["narration"]
NARRATION_PATH = ROOT / V4_NARRATION["source"]
V4_MUSIC = V4.get("music")
MUSIC_PATH = ROOT / str(V4_MUSIC["source"]) if V4_MUSIC else None
MUSIC_PROVENANCE_PATH = (
    ROOT / str(V4_MUSIC["provenance"])
    if V4_MUSIC and V4_MUSIC.get("provenance")
    else None
)
SOURCE_YEAR_SLUG = V4["source"]["course_map_source_year"].replace("–", "-")

RENDER_PROFILE = "720p30"
PROFILE_CONFIG: dict[str, object] = {}
V4_RENDER: dict[str, object]
V4_ARTIFACTS: dict[str, object]
BUILD_DIR: Path
AUDIO_DIR: Path
SCENE_DIR: Path
MASTER_AUDIO_PATH: Path
DIST_DIR: Path
PREVIEW_DIR: Path
ARTIFACT_STEM: str
ARTIFACT_SUFFIX: str
BUILD_MANIFEST_NAME: str
WIDTH: int
HEIGHT: int
FPS: int


def configure_render_profile(
    profile_id: str,
    *,
    artifact_tag: str | None = None,
) -> None:
    """Select a native render profile and optionally isolate a test release."""

    if profile_id == "720p30":
        profile: dict[str, object] = {
            "profile_id": "720p30",
            "native_render": True,
            "post_scale": False,
            "render": V4["render"],
            "artifacts": V4["artifacts"],
            "audio_dir": "build/v4/audio",
            "master_audio_name": "v4-master.wav",
            "artifact_suffix": "v4",
            "build_manifest_name": "build-manifest-v4.json",
        }
    else:
        try:
            profile = dict(V4["variants"][profile_id])
        except KeyError as exc:
            available = ", ".join(
                ("720p30", *sorted(V4.get("variants", {})))
            )
            raise ValueError(
                f"Unknown V4 render profile {profile_id!r}; expected {available}"
            ) from exc

    render = dict(profile["render"])
    artifacts = dict(profile["artifacts"])
    width = int(render["width"])
    height = int(render["height"])
    fps = int(render["fps"])
    suffix = str(profile["artifact_suffix"])
    stem = str(artifacts["stem_template"]).format(
        source_year=SOURCE_YEAR_SLUG
    )
    if not stem.endswith(f"-{suffix}"):
        raise RuntimeError(
            f"The {profile_id} artifact stem must end in '-{suffix}'"
        )
    tag = artifact_tag.strip() if artifact_tag else ""
    if tag and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", tag):
        raise ValueError(
            "Artifact tag must start with a letter or digit and contain only "
            "letters, digits, dots, underscores, or hyphens"
        )

    build_dir = Path(str(artifacts["build_dir"]))
    audio_dir = Path(str(profile["audio_dir"]))
    dist_dir = Path(str(artifacts["dist_dir"]))
    build_manifest_name = str(profile["build_manifest_name"])
    if tag:
        build_dir = build_dir.with_name(f"{build_dir.name}-{tag}")
        audio_build_dir = audio_dir.parent
        audio_dir = (
            audio_build_dir.with_name(f"{audio_build_dir.name}-{tag}")
            / audio_dir.name
        )
        dist_dir = dist_dir.with_name(f"{dist_dir.name}-{tag}")
        stem = f"{stem}-{tag}"
        manifest_path = Path(build_manifest_name)
        build_manifest_name = (
            f"{manifest_path.stem}-{tag}{manifest_path.suffix}"
        )
        profile["artifact_tag"] = tag

    global RENDER_PROFILE, PROFILE_CONFIG, V4_RENDER, V4_ARTIFACTS
    global BUILD_DIR, AUDIO_DIR, SCENE_DIR, MASTER_AUDIO_PATH
    global DIST_DIR, PREVIEW_DIR, ARTIFACT_STEM, ARTIFACT_SUFFIX
    global BUILD_MANIFEST_NAME, WIDTH, HEIGHT, FPS
    RENDER_PROFILE = profile_id
    PROFILE_CONFIG = profile
    V4_RENDER = render
    V4_ARTIFACTS = artifacts
    BUILD_DIR = ROOT / build_dir
    AUDIO_DIR = ROOT / audio_dir
    SCENE_DIR = BUILD_DIR / "scenes"
    MASTER_AUDIO_PATH = AUDIO_DIR / str(profile["master_audio_name"])
    DIST_DIR = ROOT / dist_dir
    PREVIEW_DIR = DIST_DIR / "previews"
    ARTIFACT_STEM = stem
    ARTIFACT_SUFFIX = suffix
    BUILD_MANIFEST_NAME = build_manifest_name
    WIDTH, HEIGHT, FPS = width, height, fps
    v4_visuals.configure_output(width, height, fps)


configure_render_profile("720p30")

# The total is derived from the authored scenes, never from a round target.
TARGET_DURATION = float(sum(scene.duration for scene in storyboard.SCENES))
DEFAULT_AZURE_VOICE = project_tts.resolve_voice(
    os.getenv("MANIM_VOICE") or str(V4_NARRATION["voice"])
)


@dataclass
class SceneRuntime:
    spec: storyboard.SceneSpec
    narration: v4_audio.Narration
    audio_path: Path
    metadata: dict[str, object] | None = None

    @property
    def duration(self) -> float:
        return float(self.spec.duration)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(path: Path) -> dict[str, object]:
    try:
        relative = path.relative_to(ROOT)
        path_base = None
    except ValueError:
        relative = path.relative_to(PROJECT_ROOT)
        path_base = "repository_root"
    record = {
        "path": relative.as_posix(),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }
    if path_base:
        record["path_base"] = path_base
    return record


def _version_tuple(value: str) -> tuple[int, ...]:
    match = re.match(r"(\d+(?:\.\d+)*)", value)
    return tuple(int(part) for part in match.group(1).split(".")) if match else ()


def wrap_subtitle(
    text: str,
    width: int = v4_narration.SUBTITLE_LINE_WIDTH,
) -> tuple[str, ...]:
    """Apply the V4 sentence-level, two-line subtitle contract."""

    return v4_narration.wrap_subtitle(text, width=width)


def _validate_authored_clock() -> None:
    storyboard.validate_storyboard()
    if len(storyboard.SCENES) != int(V4["scene_count"]):
        raise RuntimeError("V4 scene count does not match the manifest")
    cursor = 0.0
    for scene in storyboard.SCENES:
        if not math.isclose(scene.start, cursor, rel_tol=0, abs_tol=1e-9):
            raise RuntimeError(f"V4 scenes are not contiguous at {scene.id}")
        if scene.duration <= 0:
            raise RuntimeError(f"V4 scene has no duration: {scene.id}")
        cursor = float(scene.end)
    if not math.isclose(cursor, TARGET_DURATION, rel_tol=0, abs_tol=1e-9):
        raise RuntimeError("Computed V4 duration disagrees with the scene clock")
    authored = V4.get("authored_duration_seconds")
    if authored is not None and not math.isclose(
        float(authored),
        TARGET_DURATION,
        rel_tol=0,
        abs_tol=1e-9,
    ):
        raise RuntimeError(
            "Manifest authored_duration_seconds disagrees with "
            "v4_storyboard_data.py"
        )


def build_runtimes() -> list[SceneRuntime]:
    _validate_authored_clock()
    narrations = v4_audio.load_narration(NARRATION_PATH)
    scene_ids = tuple(scene.id for scene in storyboard.SCENES)
    if scene_ids != v4_audio.EXPECTED_SCENE_IDS:
        raise RuntimeError("V4 scene IDs disagree between storyboard and narration")

    runtimes: list[SceneRuntime] = []
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
) -> v4_audio.AzureConfig:
    """Build one uniform, natural-pacing Azure configuration.

    ``target_duration_ms`` asks the shared audio engine to add exact PCM
    silence.  The engine raises if speech plus the minimum tail does not fit;
    it has no speed-up or time-stretch path.
    """

    if V4_NARRATION.get("scene_rates"):
        raise RuntimeError("V4 forbids scene-specific narration rates")
    if V4_NARRATION.get("allow_speed_up", False):
        raise RuntimeError("V4 narration must not permit speed-up")
    if V4_NARRATION.get("allow_time_stretch", False):
        raise RuntimeError("V4 narration must not permit time-stretch")
    resolved_voice = project_tts.resolve_voice(voice)
    is_mai = project_tts.is_mai_voice(resolved_voice)
    locale = (
        project_tts.VOICE_LOCALES[resolved_voice]
        if is_mai
        else str(MANIFEST["project"]["language"])
    )
    rate = (
        project_tts.VOICE_CONFIGS[resolved_voice]
        if is_mai
        else str(V4_NARRATION["rate"])
    )
    output_format = (
        project_tts.AZURE_OUTPUT_FORMAT
        if is_mai
        else str(V4_NARRATION["azure_output_format"])
    )
    return v4_audio.AzureConfig(
        voice=resolved_voice,
        locale=locale,
        rate=rate,
        lead_silence_ms=int(V4_NARRATION["lead_silence_ms"]),
        tail_silence_ms=int(V4_NARRATION["minimum_tail_silence_ms"]),
        intercue_break_ms=int(V4_NARRATION["intercue_break_ms"]),
        target_duration_ms=round(runtime.duration * 1000),
        target_dbfs=float(V4_NARRATION["target_dbfs"]),
        output_format=output_format,
        timing_mode=(
            v4_audio.TIMING_MODE_CUE_SEGMENTS
            if is_mai
            else v4_audio.TIMING_MODE_AZURE_BOOKMARKS
        ),
    )


def prepare_audio(
    runtimes: Iterable[SceneRuntime],
    *,
    tts: str,
    voice: str = DEFAULT_AZURE_VOICE,
) -> None:
    """Generate or strictly validate only the supplied V4 scene recordings."""

    resolved_voice = project_tts.resolve_voice(voice)
    project_tts.configure_azure_speech_environment(
        resolved_voice,
        require_credentials=tts == "azure",
    )
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for runtime in runtimes:
        config = azure_config(runtime, voice=resolved_voice)
        if tts == "azure":
            print(f"Azure narration: {runtime.spec.id}", flush=True)
            try:
                runtime.metadata = v4_audio.generate_azure(
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
                runtime.metadata = v4_audio.validate_existing(
                    runtime.narration,
                    runtime.audio_path,
                    config=config,
                )
            except v4_audio.StaleAudioError as exc:
                raise RuntimeError(
                    f"Existing V4 narration for {runtime.spec.id} is absent "
                    f"or stale: {exc}\n"
                    "No fallback voice was used. Regenerate this exact "
                    "segment with:\n"
                    f".venv/bin/python render_v4.py --scene "
                    f"{runtime.spec.id} --tts azure --audio-only"
                ) from None
        else:
            raise ValueError(f"Unsupported V4 narration mode: {tts}")


def cue_starts(runtime: SceneRuntime) -> tuple[float, ...]:
    if runtime.metadata is None:
        return ()
    cues = runtime.metadata.get("cues")
    if not isinstance(cues, list):
        raise ValueError(f"{runtime.spec.id} metadata has no cue list")
    return tuple(
        int(cue["start_ticks_100ns"]) / v4_audio.TICKS_PER_SECOND
        for cue in cues
    )


# Only semantically meaningful reveals are cue-aligned.  Secondary staggered
# elements retain their authored visual timing.
SEMANTIC_CUE_ACTIONS: dict[str, dict[str, int]] = {
    "v4_01_opening": {
        "show_title": 0,
    },
    "v4_03_course_load": {
        "show_five": 0,
        "show_four": 1,
        "show_load_note": 1,
    },
    "v4_04_complementary_column": {
        "show_complementary": 0,
        "show_society": 1,
        "show_choice_note": 2,
    },
    "v4_05_common_to_specialization": {
        "show_common": 0,
        "show_subjects": 1,
        "show_transition": 2,
    },
    "v4_06_fundamental_mathematics": {
        "show_algebra": 4,
        "show_geometry": 5,
    },
    "v4_07_statistics": {
        "show_models": 3,
        "show_advanced": 5,
    },
    "v4_08_mathematics_computing": {
        "show_programming": 2,
        "show_algorithms": 2,
        "show_systems": 3,
        "show_profiles_transition": 4,
    },
    "v4_09_computing_profiles": {
        "show_math_profile": 0,
        "show_math_details": 0,
        "show_statistics_profile": 2,
        "show_statistics_details": 2,
        "show_orientation_note": 4,
        "show_common_note": 5,
    },
    "v4_10_comparison": {
        "show_objects": 0,
        "show_statistics": 2,
        "show_computing": 3,
        "show_tools": 4,
        "show_comparison_note": 5,
    },
    "v4_11_guide": {
        "show_guide": 0,
        "show_guide_title": 1,
        "show_loads": 2,
        "show_url": 3,
    },
    "v4_12_conclusion": {
        "show_logo": 2,
        "show_world": 2,
        "show_future": 3,
        "show_url": 3,
    },
}

# When one bookmark introduces a staggered visual group, its first action is
# aligned exactly and the remaining actions move by the same delta.  This
# preserves authored ordering: a later card or year can never appear before
# the element that introduces its group.
SEMANTIC_FOLLOWUP_ACTIONS: dict[
    str,
    dict[str, tuple[str, ...]],
] = {
    "v4_01_opening": {
        "show_math_card": (
            "show_statistics_card",
            "show_computing_card",
        ),
    },
    "v4_03_course_load": {
        "show_five": ("show_three_years",),
        "show_four": ("show_extended_path",),
    },
    "v4_04_complementary_column": {
        "show_complementary": ("show_option",),
    },
    "v4_05_common_to_specialization": {
        "show_transition": (
            "show_concentrations",
            "show_specialization_note",
        ),
    },
    "v4_11_guide": {
        "show_guide_title": ("show_prerequisites",),
        "show_loads": ("show_starts",),
    },
}

# A few dense explanatory sequences use intentionally tighter spacing than
# their no-audio storyboard defaults.  Values are offsets from the cue-aligned
# anchor and leave a useful reading hold before the scene boundary.
SEMANTIC_FOLLOWUP_OFFSETS: dict[
    str,
    dict[str, dict[str, float]],
] = {
    "v4_05_common_to_specialization": {
        "show_transition": {
            "show_concentrations": 1.4,
            "show_specialization_note": 3.4,
        },
    },
}


def _default_action_windows(
    runtime: SceneRuntime,
) -> dict[str, tuple[float, float]]:
    configured = getattr(v4_visuals, "DEFAULT_ACTIONS", {}).get(
        runtime.spec.id,
        runtime.spec.actions,
    )
    return {
        action.action: (float(action.start), float(action.end))
        for action in configured
    }


def aligned_actions(runtime: SceneRuntime) -> dict[str, tuple[float, float]]:
    """Return local visual windows with semantic starts on Azure bookmarks."""

    windows = _default_action_windows(runtime)
    authored_windows = dict(windows)
    starts = cue_starts(runtime)
    active_end = runtime.duration - float(runtime.spec.final_still_hold)
    shifts: dict[str, float] = {}
    for action, cue_index in SEMANTIC_CUE_ACTIONS.get(
        runtime.spec.id,
        {},
    ).items():
        if action not in windows or cue_index >= len(starts):
            continue
        default_start, default_end = windows[action]
        reveal_duration = max(0.01, default_end - default_start)
        start = min(starts[cue_index], active_end)
        end = min(active_end, start + reveal_duration)
        if end > start:
            windows[action] = (start, end)
            shifts[action] = start - default_start

    semantic_actions = SEMANTIC_CUE_ACTIONS.get(runtime.spec.id, {})
    for anchor, followups in SEMANTIC_FOLLOWUP_ACTIONS.get(
        runtime.spec.id,
        {},
    ).items():
        if anchor not in shifts:
            continue
        shift = shifts[anchor]
        for action in followups:
            if action in semantic_actions or action not in authored_windows:
                continue
            authored_start, authored_end = authored_windows[action]
            duration = authored_end - authored_start
            explicit_offset = SEMANTIC_FOLLOWUP_OFFSETS.get(
                runtime.spec.id,
                {},
            ).get(anchor, {}).get(action)
            if explicit_offset is None:
                proposed_start = authored_start + shift
            else:
                proposed_start = windows[anchor][0] + explicit_offset
            start = max(0.0, min(active_end, proposed_start))
            end = min(active_end, start + duration)
            if end > start:
                windows[action] = (start, end)
    if runtime.spec.id == "v4_01_opening" and len(starts) >= 2:
        # Introduce the three concentrations in a calm, left-to-right sequence
        # when the narration begins describing the proposed pathways.
        base = starts[1]
        for action, offset in (
            ("show_math_card", 0.0),
            ("show_statistics_card", 1.0),
            ("show_computing_card", 2.0),
        ):
            if action not in windows:
                continue
            default_start, default_end = windows[action]
            reveal_duration = max(0.01, default_end - default_start)
            start = min(base + offset, active_end)
            end = min(active_end, start + reveal_duration)
            if end > start:
                windows[action] = (start, end)
    if runtime.spec.id in v4_photos.PHOTO_SPECS:
        cue_index = 1 if runtime.spec.id == "v4_01_opening" else 2
        photo_end = starts[cue_index] if len(starts) > cue_index else 6.0
        photo_end = max(0.5, min(photo_end, active_end - 0.5))
        windows["photo_intro"] = (0.0, photo_end)
    return windows


def make_frame(runtime: SceneRuntime):
    """Create a V4 frame function with a stable hold and complete end fade."""

    actions = aligned_actions(runtime)
    active_end = runtime.duration - float(runtime.spec.final_still_hold)
    ordered_actions = tuple(sorted(actions.items()))
    static_frames: dict[tuple[int, ...], np.ndarray] = {}
    background = np.asarray(
        Image.new("RGB", (WIDTH, HEIGHT), v4_visuals.BACKGROUND),
        dtype=np.uint8,
    )

    def final_opacity(t: float) -> float:
        if runtime.spec.final_still_hold <= 0:
            return 1.0
        fade_end = runtime.duration - FINAL_BACKGROUND_HOLD_SECONDS
        fade_start = fade_end - FINAL_FADE_SECONDS
        if t <= fade_start:
            return 1.0
        if t >= fade_end:
            return 0.0
        progress = (t - fade_start) / FINAL_FADE_SECONDS
        eased = progress * progress * (3.0 - 2.0 * progress)
        return 1.0 - eased

    def static_signature(t: float) -> tuple[int, ...] | None:
        """Identify holds whose pixels are independent of absolute time."""

        if t < v4_photos.end_time(runtime.spec.id, actions):
            return None  # Includes photographic crossfade; never reuse a stale still.
        signature: list[int] = []
        for _name, (start, end) in ordered_actions:
            if start < t < end:
                return None
            signature.append(1 if t >= end else 0)
        return tuple(signature)

    def frame(t: float) -> np.ndarray:
        local_t = min(max(float(t), 0.0), runtime.duration)
        visual_t = min(local_t, active_end)
        signature = static_signature(visual_t)
        if signature is not None and signature in static_frames:
            result = static_frames[signature]
        else:
            result = v4_visuals.draw_scene(
                runtime.spec.id,
                visual_t,
                runtime.duration,
                actions,
            )
            if result.shape != (HEIGHT, WIDTH, 3) or result.dtype != np.uint8:
                raise RuntimeError(
                    f"Invalid frame returned for {runtime.spec.id}: "
                    f"shape={result.shape}, dtype={result.dtype}"
                )
            if signature is not None:
                static_frames[signature] = result

        opacity = final_opacity(local_t)
        if opacity >= 1.0:
            return result
        if opacity <= 0.0:
            return background.copy()
        return np.rint(
            result.astype(np.float32) * opacity
            + background.astype(np.float32) * (1.0 - opacity)
        ).astype(np.uint8)

    return frame


@contextmanager
def _v3_adapter() -> Iterator[None]:
    """Temporarily route reusable V3 pipeline primitives to isolated V4 state."""

    replacements = {
        "V3": V4,
        "V3_NARRATION": V4_NARRATION,
        "V3_RENDER": V4_RENDER,
        "V3_ARTIFACTS": V4_ARTIFACTS,
        "BUILD_DIR": BUILD_DIR,
        "AUDIO_DIR": AUDIO_DIR,
        "SCENE_DIR": SCENE_DIR,
        "MASTER_AUDIO_PATH": MASTER_AUDIO_PATH,
        "DIST_DIR": DIST_DIR,
        "PREVIEW_DIR": PREVIEW_DIR,
        "NARRATION_PATH": NARRATION_PATH,
        "ARTIFACT_STEM": ARTIFACT_STEM,
        "WIDTH": WIDTH,
        "HEIGHT": HEIGHT,
        "FPS": FPS,
        "TARGET_DURATION": TARGET_DURATION,
        "DEFAULT_AZURE_VOICE": DEFAULT_AZURE_VOICE,
        "v3_audio": v4_audio,
        "storyboard": storyboard,
        "v3_visuals": v4_visuals,
        "SEMANTIC_CUE_ACTIONS": SEMANTIC_CUE_ACTIONS,
        "make_frame": make_frame,
    }
    previous = {
        name: getattr(v3_pipeline, name)
        for name in replacements
    }
    try:
        for name, value in replacements.items():
            setattr(v3_pipeline, name, value)
        yield
    finally:
        for name, value in previous.items():
            setattr(v3_pipeline, name, value)


def scene_video_path(index: int, runtime: SceneRuntime) -> Path:
    return SCENE_DIR / f"{index:02d}-{runtime.spec.id}.mp4"


def render_scene(runtime: SceneRuntime, index: int) -> Path:
    """Render one scene through the tested V3 MoviePy/FFmpeg primitive."""

    with _v3_adapter():
        return v3_pipeline.render_scene(runtime, index)


def build_master_audio(runtimes: list[SceneRuntime]) -> Path:
    """Concatenate exact 48 kHz scene clocks through the tested V3 primitive."""

    with _v3_adapter():
        return v3_pipeline.build_master_audio(runtimes)


def _concat_line(path: Path) -> str:
    escaped = str(path.resolve()).replace("'", "'\\''")
    return f"file '{escaped}'"


def background_music_filter() -> str:
    """Return the deterministic mono narration/music mix graph."""

    if not V4_MUSIC:
        raise RuntimeError("V4 background-music configuration is missing")
    crossfade = float(V4_MUSIC["loop_crossfade_seconds"])
    fade_in = float(V4_MUSIC["fade_in_seconds"])
    fade_out = float(V4_MUSIC["fade_out_seconds"])
    source_duration = float(V4_MUSIC["duration_seconds"])
    if crossfade >= source_duration or TARGET_DURATION > 2 * source_duration - crossfade:
        raise RuntimeError("Music coverage is too short; explicitly revise the loop before extending V4")
    fade_out_start = TARGET_DURATION - fade_out
    gain_db = float(V4_MUSIC["gain_db"])
    speech_cut_db = float(V4_MUSIC["speech_band_cut_db"])
    threshold = float(V4_MUSIC["duck_threshold"])
    ratio = float(V4_MUSIC["duck_ratio"])
    attack = int(V4_MUSIC["duck_attack_ms"])
    release = int(V4_MUSIC["duck_release_ms"])
    if min(crossfade, fade_in, fade_out) < 0 or fade_out_start < 0:
        raise RuntimeError("V4 background-music fades must fit the release")
    return (
        "[2:a]aresample=48000,"
        "pan=mono|c0=0.5*c0+0.5*c1,asplit=2[music_a][music_b];"
        f"[music_a][music_b]acrossfade=d={crossfade:g}:c1=qsin:c2=qsin,"
        f"atrim=duration={TARGET_DURATION:g},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d={fade_in:g},"
        f"afade=t=out:st={fade_out_start:g}:d={fade_out:g},"
        "highpass=f=80,lowpass=f=8500,"
        f"equalizer=f=2200:t=q:w=1.2:g={speech_cut_db:g},"
        f"volume={gain_db:g}dB[music];"
        "[1:a]aformat=sample_fmts=fltp:sample_rates=48000:"
        "channel_layouts=mono,asplit=2[narration][sidechain];"
        f"[music][sidechain]sidechaincompress=threshold={threshold:g}:"
        f"ratio={ratio:g}:attack={attack}:release={release}[ducked];"
        "[narration][ducked]amix=inputs=2:duration=first:normalize=0:"
        "dropout_transition=0,alimiter=limit=0.841395:attack=5:release=50:"
        "level=false:latency=true[mixed]"
    )


def assemble(
    scene_paths: list[Path],
    runtimes: list[SceneRuntime],
    *,
    include_music: bool = False,
) -> tuple[Path, Path]:
    if len(scene_paths) != int(V4["scene_count"]):
        raise ValueError(
            f"Assembly requires {V4['scene_count']} scenes; "
            f"received {len(scene_paths)}"
        )
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    concat_path = SCENE_DIR / f"concat-{ARTIFACT_SUFFIX}.txt"
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
    with tempfile.TemporaryDirectory(
        prefix=f".assemble-{ARTIFACT_SUFFIX}-",
        dir=DIST_DIR,
    ) as temp:
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
        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video_only_path),
            "-i",
            str(master_audio),
        ]
        if include_music:
            if MUSIC_PATH is None or not MUSIC_PATH.is_file():
                raise RuntimeError("Configured V4 background music is missing")
            command.extend(
                [
                    "-i",
                    str(MUSIC_PATH),
                    "-filter_complex",
                    background_music_filter(),
                    "-map",
                    "0:v:0",
                    "-map",
                    "[mixed]",
                ]
            )
        else:
            command.extend(["-map", "0:v:0", "-map", "1:a:0"])
        command.extend(
            [
                "-c:v",
                "copy",
                "-c:a",
                str(V4_RENDER["audio_codec"]),
                "-b:a",
                str(V4_RENDER["audio_bitrate"]),
                "-ar",
                "48000",
                "-ac",
                "1",
                "-t",
                f"{TARGET_DURATION:.6f}",
                "-movflags",
                "+faststart",
                str(temporary_path),
            ]
        )
        subprocess.run(command, check=True)
        os.replace(temporary_path, output)
    return output, master_audio


def srt_time(seconds: float) -> str:
    return v3_pipeline.srt_time(seconds)


def write_srt(runtimes: list[SceneRuntime]) -> Path:
    """Write sentence cues from verified native or PCM-boundary offsets."""

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    path = DIST_DIR / f"{ARTIFACT_STEM}.srt"
    blocks: list[str] = []
    cue_number = 1
    previous_end_ms = -1
    for runtime in runtimes:
        if runtime.metadata is None:
            raise RuntimeError(
                f"Narration metadata was not prepared for {runtime.spec.id}"
            )
        intervals = v4_audio.subtitle_intervals(
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
            global_start = float(runtime.spec.start) + interval.start
            global_end = float(runtime.spec.start) + interval.end
            start_ms = round(global_start * 1000)
            end_ms = round(global_end * 1000)
            if end_ms <= start_ms:
                raise RuntimeError(
                    "Subtitle cue collapses after millisecond rounding in "
                    f"{runtime.spec.id}"
                )
            if start_ms < previous_end_ms:
                raise RuntimeError(
                    "Subtitle cues overlap after millisecond rounding in "
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
    path.with_suffix(".review.json").write_text(json.dumps(validate_subtitles(path, TARGET_DURATION), indent=2), encoding="utf-8")
    return path


def _preview_time(runtime: SceneRuntime) -> float:
    preferred = {
        "v4_01_opening": 11.0,
        "v4_03_course_load": 13.5,
        "v4_04_complementary_column": 12.5,
        "v4_05_common_to_specialization": 12.0,
        "v4_06_fundamental_mathematics": 25.0,
        "v4_07_statistics": 26.0,
        "v4_08_mathematics_computing": 18.5,
        "v4_09_computing_profiles": 27.0,
        "v4_10_comparison": 21.5,
        "v4_11_guide": 17.0,
        "v4_12_conclusion": 17.0,
    }
    active_end = runtime.duration - float(runtime.spec.final_still_hold)
    return min(preferred.get(runtime.spec.id, runtime.duration / 2), active_end)


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
        (columns * thumb_width, rows * (thumb_height + label_height)),
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
        draw.text(
            (x + 10, y + thumb_height + 10),
            f"{index:02d} · {runtime.spec.title}",
            font=label_font,
            fill=(24, 33, 43),
        )
    # Put the selected variant at the filename endpoint.
    stem_without_variant = ARTIFACT_STEM.removesuffix(
        f"-{ARTIFACT_SUFFIX}"
    )
    path = DIST_DIR / (
        f"{stem_without_variant}-storyboard-{ARTIFACT_SUFFIX}.png"
    )
    board.save(path)
    return path


def probe_video(path: Path) -> dict:
    return v3_pipeline.probe_video(path)


def validate_video(
    path: Path,
    *,
    expected_duration: float,
) -> dict:
    with _v3_adapter():
        return v3_pipeline.validate_video(
            path,
            expected_duration=expected_duration,
        )


def _static_hash_checks() -> list[tuple[Path, str, str]]:
    """Return all immutable V4 inputs whose manifest hashes are mandatory."""

    checks = [
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
            ROOT / V4["storyboard"],
            V4["storyboard_sha256"],
            "V4 storyboard",
        ),
        (
            ROOT / V4["source"]["guide_cover"],
            V4["source"]["guide_cover_sha256"],
            "guide cover",
        ),
        (
            ROOT / V4["source"]["guide_tex"],
            V4["source"]["guide_tex_sha256"],
            "current guide TeX",
        ),
    ]
    if V4_MUSIC and MUSIC_PATH is not None:
        checks.append(
            (MUSIC_PATH, str(V4_MUSIC["sha256"]), "V4 background music")
        )
    if V4_MUSIC and MUSIC_PROVENANCE_PATH is not None:
        checks.append(
            (
                MUSIC_PROVENANCE_PATH,
                str(V4_MUSIC["provenance_sha256"]),
                "V4 background-music provenance",
            )
        )
    checks.extend([
        (ROOT / V4["source"]["guide_pdf"], V4["source"]["guide_pdf_sha256"], "current official guide"),
        (v4_photos.ASSETS / "president_kennedy.jpg", V4["source"]["pk_sha256"], "President-Kennedy photo"),
        (v4_photos.ASSETS / "research_math.jpg", V4["source"]["research_photo_sha256"], "research-hub photo"),
    ])
    return checks


def check_environment(
    runtimes: list[SceneRuntime] | None = None,
) -> dict[str, str]:
    """Validate dependencies, strict source hashes, timing, and V4 frames."""

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
            problems.append(f"{distribution} must be {expected}; found {actual}")

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
            str(V4_RENDER["video_codec"]),
            str(V4_RENDER["audio_codec"]),
        ):
            if not re.search(rf"\b{re.escape(encoder)}\b", encoders):
                problems.append(f"FFmpeg encoder is unavailable: {encoder}")

    try:
        checks = _static_hash_checks()
    except KeyError as exc:
        problems.append(f"V4 manifest is missing a required hash field: {exc}")
        checks = []
    for path, expected_hash, label in checks:
        if not path.is_file():
            problems.append(f"{label} is missing: {path}")
        elif sha256_file(path) != expected_hash:
            problems.append(f"{label} does not match its manifest hash: {path}")

    try:
        _validate_authored_clock()
        checked_runtimes = runtimes if runtimes is not None else build_runtimes()
        if (v4_visuals.WIDTH, v4_visuals.HEIGHT, v4_visuals.FPS) != (
            WIDTH,
            HEIGHT,
            FPS,
        ):
            problems.append("V4 visual dimensions or frame rate disagree")
        for runtime in checked_runtimes:
            sample = make_frame(runtime)(min(0.5, runtime.duration))
            if sample.shape != (HEIGHT, WIDTH, 3) or sample.dtype != np.uint8:
                problems.append(f"Invalid sample frame for {runtime.spec.id}")
            if runtime.spec.final_still_hold:
                frame = make_frame(runtime)
                hold_start = runtime.duration - runtime.spec.final_still_hold
                fade_start = runtime.duration - (
                    FINAL_FADE_SECONDS + FINAL_BACKGROUND_HOLD_SECONDS
                )
                at_start = frame(hold_start)
                at_fade_start = frame(fade_start)
                at_background = frame(
                    runtime.duration - FINAL_BACKGROUND_HOLD_SECONDS
                )
                at_end = frame(runtime.duration)
                expected_background = np.asarray(
                    Image.new(
                        "RGB",
                        (WIDTH, HEIGHT),
                        v4_visuals.BACKGROUND,
                    ),
                    dtype=np.uint8,
                )
                if not np.array_equal(at_start, at_fade_start):
                    problems.append(
                        f"Final still hold is not stable in {runtime.spec.id}"
                    )
                if not np.array_equal(at_background, expected_background):
                    problems.append(
                        f"End fade does not reach the background in "
                        f"{runtime.spec.id}"
                    )
                if not np.array_equal(at_background, at_end):
                    problems.append(
                        f"Final background hold is not stable in "
                        f"{runtime.spec.id}"
                    )
    except Exception as exc:
        problems.append(f"V4 source validation failed: {exc}")

    if problems:
        raise RuntimeError(
            "V4 environment check failed:\n- "
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
    include_music: bool = False,
) -> Path:
    """Write the strict, reproducible V4 release manifest."""

    # Recheck immutable sources at release time; a build manifest must never be
    # produced from a bootstrapping or stale source set.
    for path, expected_hash, label in _static_hash_checks():
        if not path.is_file() or sha256_file(path) != expected_hash:
            raise RuntimeError(
                f"Cannot write V4 build manifest: {label} hash is invalid"
            )

    input_paths = [
        PROJECT_TTS_PATH,
        MANIFEST_PATH,
        ROOT / "render_v4.py",
        ROOT / "render_v3.py",
        ROOT / "v4_audio.py",
        ROOT / "v4_narration.py",
        ROOT / "v4_visuals.py",
        ROOT / "v4_storyboard_data.py",
        ROOT / "v3_audio.py",
        ROOT / "program_data.py",  # Historical baseline remains an explicit dependency.
        ROOT / "program_data_v4.py",
        ROOT / "v4_photos.py",
        PROJECT_ROOT / "tools/uqam_video_review.py",
        v4_photos.ASSETS / "sources.json",
        v4_photos.ASSETS / "president_kennedy.jpg",
        v4_photos.ASSETS / "research_math.jpg",
        ROOT / V4["source"]["guide_pdf"],
        ROOT / "theme.py",
        NARRATION_PATH,
        ROOT / V4["storyboard"],
        ROOT / "requirements.txt",
        ROOT / "requirements.lock",
        ROOT / MANIFEST["source"]["guide"]["path"],
        ROOT / V4["source"]["guide_cover"],
        ROOT / V4["source"]["guide_tex"],
        ROOT / MANIFEST["identity"]["svg"],
        ROOT / MANIFEST["identity"]["png"],
        ROOT / MANIFEST["fonts"]["regular"],
        ROOT / MANIFEST["fonts"]["bold"],
        ROOT / MANIFEST["fonts"]["mono"],
        ROOT / "assets/fonts/OFL-1.1.txt",
    ]
    if include_music and MUSIC_PATH is not None:
        input_paths.append(MUSIC_PATH)
        if MUSIC_PROVENANCE_PATH is not None:
            input_paths.append(MUSIC_PROVENANCE_PATH)
    audio_records = []
    for runtime in runtimes:
        if runtime.metadata is None:
            raise RuntimeError(
                f"Missing narration metadata for {runtime.spec.id}"
            )
        metadata_path = v4_audio.voice_metadata_path(runtime.audio_path)
        audio_records.append(
            {
                "scene_id": runtime.spec.id,
                "start_seconds": runtime.spec.start,
                "duration_seconds": runtime.duration,
                "narration_sha256": runtime.narration.digest,
                "audio": artifact_record(runtime.audio_path),
                "metadata": artifact_record(metadata_path),
                "synthesis_config": runtime.metadata["synthesis_config"],
                "cue_timing": runtime.metadata.get(
                    "timing",
                    {
                        "mode": v4_audio.TIMING_MODE_AZURE_BOOKMARKS,
                        "source": "azure_bookmark_events",
                    },
                ),
                "cue_bookmarks": runtime.metadata["cues"],
            }
        )

    timing_sources = {
        str(record["cue_timing"]["source"])
        for record in audio_records
    }
    if len(timing_sources) != 1:
        raise RuntimeError("V4 narration segments use mixed cue timing sources")
    cue_timing_source = timing_sources.pop()
    speech_region = (
        os.getenv("SPEECH_REGION")
        or os.getenv("AZURE_SERVICE_REGION")
        or ""
    ).strip().casefold()
    selected_voices = {
        str(record["synthesis_config"]["voice"])
        for record in audio_records
    }
    if any(project_tts.is_mai_voice(voice) for voice in selected_voices):
        if speech_region != project_tts.MAI_VOICE_2_REGION:
            raise RuntimeError(
                "A MAI V4 release manifest requires "
                f"SPEECH_REGION={project_tts.MAI_VOICE_2_REGION}"
            )

    payload = {
        "schema": 4,
        "project": {
            "id": MANIFEST["project"]["id"],
            "release": V4["release"],
            "render_profile": RENDER_PROFILE,
            "language": MANIFEST["project"]["language"],
            "source_year": V4["source"]["course_map_source_year"],
            "authored_duration_seconds": TARGET_DURATION,
        },
        "source_context": {
            "course_map_source_year": V4["source"]["course_map_source_year"],
            "guide_tex_academic_year": V4["source"]["guide_tex_academic_year"],
            "visible_year_label": bool(V4["source"]["visible_year_label"]),
        },
        "identity": {
            "provenance_url": MANIFEST["identity"]["provenance_url"],
            "usage_policy_url": MANIFEST["identity"]["usage_policy_url"],
            "authorization": MANIFEST["identity"]["authorization"],
        },
        "timing": {
            "scene_clock": "v4_storyboard_data.py",
            "duration_policy": "sum_of_authored_scene_durations",
            "narration_source": V4_NARRATION["source"],
            "subtitle_source": cue_timing_source,
            "semantic_motion_source": cue_timing_source,
            "audio_target_duration_use": "silence_padding_only",
            "word_count_timing": False,
            "speed_up": False,
            "time_stretch": False,
        },
        "speech_service": {
            "region": speech_region or None,
            "credential_source": "environment",
        },
        "render": {
            **V4_RENDER,
            "actual_fps": FPS,
            "logical_width": storyboard.WIDTH,
            "logical_height": storyboard.HEIGHT,
            "native_render": bool(PROFILE_CONFIG["native_render"]),
            "post_scale": bool(PROFILE_CONFIG["post_scale"]),
            "logical_to_physical_scale": WIDTH / storyboard.WIDTH,
        },
        "toolchain": dict(tool_versions),
        "inputs": [
            artifact_record(path)
            for path in sorted(input_paths, key=lambda item: item.as_posix())
        ],
        "narration_segments": audio_records,
        "master_audio": artifact_record(master_audio),
        "background_music": (
            {
                "enabled": True,
                "asset": artifact_record(MUSIC_PATH),
                "title": V4_MUSIC["title"],
                "creator": V4_MUSIC["creator"],
                "source_url": V4_MUSIC["source_url"],
                "license_url": V4_MUSIC["license_url"],
                "mix": {
                    key: value
                    for key, value in V4_MUSIC.items()
                    if key
                    not in {
                        "source",
                        "sha256",
                        "title",
                        "creator",
                        "source_url",
                        "license_url",
                        "provenance",
                        "provenance_sha256",
                    }
                },
            }
            if include_music and V4_MUSIC and MUSIC_PATH is not None
            else {"enabled": False}
        ),
        "scene_videos": [artifact_record(path) for path in scene_paths],
        "outputs": [
            artifact_record(path)
            for path in sorted(outputs, key=lambda item: item.as_posix())
        ],
        "video_probe": final_probe,
        "review_status": {"encoded_visual_review": "pending", "full_listening": "pending", "institutional_approval": "not inferred"},
        "photo_credits": [record for runtime in runtimes for record in v4_photos.credit_records(runtime.spec.id, runtime.spec.start, aligned_actions(runtime))],
    }
    path = DIST_DIR / BUILD_MANIFEST_NAME
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def validated_scene_paths(
    indexed_runtimes: list[tuple[int, SceneRuntime]],
) -> list[Path]:
    paths: list[Path] = []
    for index, runtime in indexed_runtimes:
        path = scene_video_path(index, runtime)
        if not path.is_file():
            raise RuntimeError(
                f"Rendered scene is missing: {path}\nRender it with:\n"
                f".venv/bin/python render_v4.py --scene "
                f"{runtime.spec.id} --tts existing"
            )
        validate_video(path, expected_duration=runtime.duration)
        paths.append(path)
    return paths


def finalize(
    runtimes: list[SceneRuntime],
    indexed_runtimes: list[tuple[int, SceneRuntime]],
    scene_paths: list[Path],
    tool_versions: Mapping[str, str],
    *,
    include_music: bool = False,
) -> tuple[Path, Path, Path, Path]:
    video, master_audio = assemble(
        scene_paths,
        runtimes,
        include_music=include_music,
    )
    subtitles = write_srt(runtimes)
    previews = [
        write_preview(runtime, index)
        for index, runtime in indexed_runtimes
    ]
    storyboard_path = build_storyboard(indexed_runtimes)
    probe = validate_video(video, expected_duration=TARGET_DURATION)
    build_manifest = write_build_manifest(
        runtimes,
        scene_paths,
        (video, subtitles, storyboard_path, *previews),
        master_audio,
        tool_versions=tool_versions,
        final_probe=probe,
        include_music=include_music,
    )
    return video, subtitles, storyboard_path, build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Render the naturally paced UQAM programme-overview V4 "
            f"({TARGET_DURATION:g} authored seconds)."
        )
    )
    parser.add_argument(
        "--render-profile",
        choices=("720p30", *sorted(V4.get("variants", {}))),
        default="720p30",
        help="Select an isolated native resolution/frame-rate profile",
    )
    parser.add_argument(
        "--artifact-tag",
        help=(
            "Append a safe stamp to build/output folders and filenames so a "
            "test release cannot replace the canonical master"
        ),
    )
    parser.add_argument(
        "--background-music",
        action="store_true",
        help="Mix the manifest-pinned Pixabay track under the narration",
    )
    parser.add_argument("--scene", help="Prepare and render only this scene ID")
    parser.add_argument(
        "--tts",
        choices=("existing", "azure"),
        default="existing",
        help="Strictly validate cached Azure audio or regenerate it",
    )
    parser.add_argument(
        "--azure-voice",
        default=DEFAULT_AZURE_VOICE,
        help="Azure voice ShortName or project selector such as MAI-Voice-2",
    )
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
        help="Validate existing audio/scenes and assemble the full V4 release",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate dependencies, assets, narration, timing, and frames",
    )
    args = parser.parse_args()
    configure_render_profile(
        args.render_profile,
        artifact_tag=args.artifact_tag,
    )

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
        parser.error(
            f"--assemble-only always requires all {len(storyboard.SCENES)} scenes"
        )
    if args.assemble_only and args.tts != "existing":
        parser.error("--assemble-only requires --tts existing")
    if args.background_music and not args.artifact_tag:
        parser.error("--background-music requires --artifact-tag")
    if args.background_music and (
        args.audio_only or args.previews_only or args.check or args.scene
    ):
        parser.error(
            "--background-music applies only to a full render or assembly"
        )

    runtimes = build_runtimes()
    selected = select_runtimes(runtimes, args.scene)
    selected_runtimes = [runtime for _, runtime in selected]
    # With --scene, expensive frame checks remain isolated to that scene.
    tool_versions = check_environment(
        selected_runtimes if args.scene else runtimes
    )
    if args.check:
        print(
            "V4 environment, assets, narration, authored timing, and frames: OK"
        )
        print(f"render_profile={RENDER_PROFILE}")
        print(f"native_output={WIDTH}x{HEIGHT}@{FPS}")
        print(f"authored_duration_seconds={TARGET_DURATION:g}")
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
            include_music=args.background_music,
        ):
            print(output)
        return

    prepare_audio(
        selected_runtimes,
        tts=args.tts,
        voice=args.azure_voice,
    )
    if args.audio_only:
        for runtime in selected_runtimes:
            print(runtime.audio_path)
            print(v4_audio.voice_metadata_path(runtime.audio_path))
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
        include_music=args.background_music,
    ):
        print(output)


if __name__ == "__main__":
    main()

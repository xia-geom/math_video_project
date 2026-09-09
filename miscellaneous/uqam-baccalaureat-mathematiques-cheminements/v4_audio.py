"""V4-facing narration API backed by the shared Azure bookmark engine.

The synthesis/cache implementation remains in :mod:`v3_audio` so V3 stays
reproducible.  This facade supplies the V4 scene order and its independently
authored narration parser without duplicating the audio implementation.
"""

from __future__ import annotations

from v3_audio import (
    AzureConfig,
    METADATA_SCHEMA,
    StaleAudioError,
    SubtitleInterval,
    SynthesisError,
    TICKS_PER_SECOND,
    TIMING_MODE_AZURE_BOOKMARKS,
    TIMING_MODE_CUE_SEGMENTS,
    bookmark_name,
    build_azure_ssml,
    cache_key,
    generate_azure,
    sha256_file,
    subtitle_intervals,
    validate_existing,
    voice_metadata_path,
)
from v4_narration import (
    EXPECTED_SCENE_IDS,
    NarrationError,
    NarrationScene as Narration,
    load_narration,
    parse_narration_text,
)


__all__ = (
    "AzureConfig",
    "EXPECTED_SCENE_IDS",
    "METADATA_SCHEMA",
    "Narration",
    "NarrationError",
    "StaleAudioError",
    "SubtitleInterval",
    "SynthesisError",
    "TICKS_PER_SECOND",
    "TIMING_MODE_AZURE_BOOKMARKS",
    "TIMING_MODE_CUE_SEGMENTS",
    "bookmark_name",
    "build_azure_ssml",
    "cache_key",
    "generate_azure",
    "load_narration",
    "parse_narration_text",
    "sha256_file",
    "subtitle_intervals",
    "validate_existing",
    "voice_metadata_path",
)

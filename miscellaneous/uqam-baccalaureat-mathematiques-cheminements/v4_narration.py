"""Authored V4 narration and natural-pacing synthesis policy.

``voiceover_v4_fr.txt`` is the single source of narration text.  This module
only validates that source and exposes its scenes in renderer order.  Visual
scene durations remain authored in ``v4_storyboard_data.py``.  When the
renderer builds an Azure configuration, it must use that scene duration as the
target duration; the audio engine may add silence but may not alter speech
speed.  Synthesis must fail clearly if speech plus the minimum tail does not
fit the authored scene.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import textwrap


ROOT = Path(__file__).resolve().parent
NARRATION_PATH = ROOT / "voiceover_v4_fr.txt"

EXPECTED_SCENE_IDS = (
    "v4_01_opening",
    "v4_03_course_load",
    "v4_04_complementary_column",
    "v4_05_common_to_specialization",
    "v4_06_fundamental_mathematics",
    "v4_07_statistics",
    "v4_08_mathematics_computing",
    "v4_09_computing_profiles",
    "v4_10_comparison",
    "v4_11_guide",
    "v4_12_conclusion",
)

EXPECTED_CUE_COUNTS = {
    "v4_01_opening": 3,
    "v4_03_course_load": 4,
    "v4_04_complementary_column": 4,
    "v4_05_common_to_specialization": 3,
    "v4_06_fundamental_mathematics": 7,
    "v4_07_statistics": 8,
    "v4_08_mathematics_computing": 5,
    "v4_09_computing_profiles": 6,
    "v4_10_comparison": 7,
    "v4_11_guide": 4,
    "v4_12_conclusion": 4,
}

SUBTITLE_LINE_WIDTH = 44
SUBTITLE_MAX_LINES = 2

_SECTION_RE = re.compile(r"^\[([a-z0-9_]+)]$")
_SENTENCE_END_RE = re.compile(r"[.!?…][”»']?$")
_MULTIPLE_SENTENCES_RE = re.compile(r"[.!?…][”»']?\s+\S")


class NarrationError(ValueError):
    """The V4 narration source is incomplete or malformed."""


@dataclass(frozen=True, slots=True)
class NarrationScene:
    """One ordered scene of sentence-level narration cues."""

    scene_id: str
    cues: tuple[str, ...]

    @property
    def text(self) -> str:
        return " ".join(self.cues)

    @property
    def cue_ids(self) -> tuple[str, ...]:
        return tuple(
            f"{self.scene_id}:{index:02d}"
            for index in range(1, len(self.cues) + 1)
        )

    @property
    def digest(self) -> str:
        canonical = json.dumps(
            {"scene_id": self.scene_id, "cues": list(self.cues)},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class AzureNarrationPolicy:
    """V4 synthesis settings chosen for a measured, natural delivery.

    ``target_duration_ms`` remains unset here because the renderer supplies
    the duration of the current authored scene.
    """

    provider: str = "azure"
    voice: str = "fr-CA-SylvieNeural"
    locale: str = "fr-CA"
    rate: str = "-10%"
    lead_silence_ms: int = 350
    intercue_break_ms: int = 180
    minimum_tail_silence_ms: int = 800
    target_dbfs: float = -18.5
    output_format: str = "Audio48Khz192KBitRateMonoMp3"
    target_duration_ms: int | None = None
    allow_time_stretch: bool = False
    allow_speed_up: bool = False


V4_AUDIO_POLICY = AzureNarrationPolicy()


def wrap_subtitle(
    cue: str,
    *,
    width: int = SUBTITLE_LINE_WIDTH,
) -> tuple[str, ...]:
    """Return the renderer-ready subtitle lines for one authored sentence."""

    lines = tuple(
        textwrap.wrap(
            cue,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )
    if not lines or len(lines) > SUBTITLE_MAX_LINES:
        raise NarrationError(
            "Subtitle cue must fit on at most "
            f"{SUBTITLE_MAX_LINES} lines of {width} characters: {cue!r}"
        )
    return lines


def parse_narration_text(source: str) -> dict[str, NarrationScene]:
    """Parse and validate the V4 sentence-level narration source."""

    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line_number, raw_line in enumerate(source.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        section_match = _SECTION_RE.fullmatch(line)
        if section_match:
            current = section_match.group(1)
            if current in sections:
                raise NarrationError(
                    f"Duplicate narration section [{current}] at line {line_number}"
                )
            sections[current] = []
            continue

        if current is None:
            raise NarrationError(
                f"Narration text appears before the first section at line {line_number}"
            )
        if not _SENTENCE_END_RE.search(line):
            raise NarrationError(
                f"Narration cue must end in sentence punctuation at line {line_number}"
            )
        if _MULTIPLE_SENTENCES_RE.search(line):
            raise NarrationError(
                f"Narration cue must contain one sentence at line {line_number}"
            )
        wrap_subtitle(line)
        sections[current].append(line)

    expected = set(EXPECTED_SCENE_IDS)
    actual = set(sections)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    empty = sorted(scene_id for scene_id, cues in sections.items() if not cues)
    problems = []
    if missing:
        problems.append("missing: " + ", ".join(missing))
    if unknown:
        problems.append("unknown: " + ", ".join(unknown))
    if empty:
        problems.append("empty: " + ", ".join(empty))
    if problems:
        raise NarrationError(
            "Invalid V4 narration source (" + "; ".join(problems) + ")"
        )

    for scene_id in EXPECTED_SCENE_IDS:
        actual_count = len(sections[scene_id])
        expected_count = EXPECTED_CUE_COUNTS[scene_id]
        if actual_count != expected_count:
            raise NarrationError(
                f"[{scene_id}] has {actual_count} cues; expected {expected_count}"
            )

    return {
        scene_id: NarrationScene(scene_id, tuple(sections[scene_id]))
        for scene_id in EXPECTED_SCENE_IDS
    }


def load_narration(
    path: Path = NARRATION_PATH,
) -> dict[str, NarrationScene]:
    """Load the single V4 narration source from disk."""

    return parse_narration_text(path.read_text(encoding="utf-8"))


NARRATIONS = load_narration()
TOTAL_CUE_COUNT = sum(len(scene.cues) for scene in NARRATIONS.values())

if TOTAL_CUE_COUNT != 55:
    raise NarrationError(
        f"V4 narration contains {TOTAL_CUE_COUNT} cues; expected 55"
    )

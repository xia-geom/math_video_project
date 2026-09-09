"""Deterministic narration and subtitle timing for the V3 storyboard.

The module is intentionally independent from the visual renderer.  Azure
bookmarks are inserted immediately before every authored sentence.  Their
audio offsets become the single source of truth for subtitle and animation
timing.
"""

from __future__ import annotations

import audioop
from dataclasses import asdict, dataclass
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Callable, Mapping
import wave


EXPECTED_SCENE_IDS = (
    "v3_01_opening",
    "v3_02_reading_the_table",
    "v3_03_course_load",
    "v3_04_complementary_column",
    "v3_05_common_foundation",
    "v3_06_fundamental_mathematics",
    "v3_07_statistics",
    "v3_08_mathematics_computing",
    "v3_09_computing_profiles",
    "v3_10_comparison",
    "v3_11_guide",
)

TICKS_PER_SECOND = 10_000_000
METADATA_SCHEMA = 3
TIMING_MODE_AZURE_BOOKMARKS = "azure_bookmarks"
TIMING_MODE_CUE_SEGMENTS = "cue_segments"
TIMING_SOURCES = {
    TIMING_MODE_AZURE_BOOKMARKS: "azure_bookmark_events",
    TIMING_MODE_CUE_SEGMENTS: "pcm_cue_segment_boundaries",
}
AZURE_SYNTHESIS_ATTEMPTS = 3
CUE_SEGMENTER_VERSION = 1
CUE_EDGE_WINDOW_MS = 10
CUE_EDGE_RELATIVE_THRESHOLD_DB = -35.0
CUE_RETAINED_LEAD_MS = 40
CUE_RETAINED_TAIL_MS = 180
_SECTION_RE = re.compile(r"^\[([a-z0-9_]+)]$")
_SENTENCE_END_RE = re.compile(r"[.!?…][”»']?$")
_MULTIPLE_SENTENCES_RE = re.compile(r"[.!?…][”»']?\s+\S")


class NarrationError(ValueError):
    """The authored narration source is malformed."""


class StaleAudioError(RuntimeError):
    """An existing WAV/metadata pair does not match its inputs."""


class SynthesisError(RuntimeError):
    """Azure did not produce a complete, bookmark-aligned recording."""


@dataclass(frozen=True)
class Narration:
    scene_id: str
    cues: tuple[str, ...]

    @property
    def text(self) -> str:
        return " ".join(self.cues)

    @property
    def digest(self) -> str:
        return _sha256_json(
            {"scene_id": self.scene_id, "cues": list(self.cues)}
        )


@dataclass(frozen=True)
class AzureConfig:
    voice: str = "fr-CA-SylvieNeural"
    locale: str = "fr-CA"
    rate: str = "-14%"
    lead_silence_ms: int = 350
    tail_silence_ms: int = 750
    intercue_break_ms: int = 0
    target_duration_ms: int | None = None
    target_dbfs: float = -18.5
    output_format: str = "Riff48Khz16BitMonoPcm"
    timing_mode: str = TIMING_MODE_AZURE_BOOKMARKS

    def __post_init__(self) -> None:
        if not self.voice.strip():
            raise ValueError("Azure voice cannot be empty")
        if not self.locale.strip():
            raise ValueError("Azure locale cannot be empty")
        if (
            self.lead_silence_ms < 0
            or self.tail_silence_ms < 0
            or self.intercue_break_ms < 0
        ):
            raise ValueError("Silence durations cannot be negative")
        if self.target_duration_ms is not None and self.target_duration_ms <= 0:
            raise ValueError("Target duration must be positive")
        if self.timing_mode not in TIMING_SOURCES:
            choices = ", ".join(sorted(TIMING_SOURCES))
            raise ValueError(
                f"Unknown narration timing mode {self.timing_mode!r}; "
                f"expected one of: {choices}"
            )

    def cache_dict(self) -> dict[str, object]:
        values = asdict(self)
        # Preserve the schema-3 cache identity of the native bookmark path.
        # The explicit field is required for alternate timing modes so those
        # recordings can never be confused with a native-bookmark recording.
        if self.timing_mode == TIMING_MODE_AZURE_BOOKMARKS:
            values.pop("timing_mode")
        else:
            values["cue_segmentation"] = {
                "version": CUE_SEGMENTER_VERSION,
                "edge_window_ms": CUE_EDGE_WINDOW_MS,
                "relative_threshold_db": CUE_EDGE_RELATIVE_THRESHOLD_DB,
                "retained_lead_ms": CUE_RETAINED_LEAD_MS,
                "retained_tail_ms": CUE_RETAINED_TAIL_MS,
            }
        return {"provider": "azure", **values}


@dataclass(frozen=True)
class SubtitleInterval:
    start: float
    end: float
    text: str


RawSynthesizer = Callable[[str, Path], Mapping[str, int]]


def _sha256_json(value: object) -> str:
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_narration_text(source: str) -> dict[str, Narration]:
    """Parse the eleven INI-like V3 sections and their sentence cues."""

    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line_number, raw_line in enumerate(source.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        section = _SECTION_RE.fullmatch(line)
        if section:
            current = section.group(1)
            if current in sections:
                raise NarrationError(
                    f"Duplicate narration section [{current}] at line {line_number}"
                )
            sections[current] = []
            continue
        if current is None:
            raise NarrationError(
                f"Narration text before the first section at line {line_number}"
            )
        if not _SENTENCE_END_RE.search(line):
            raise NarrationError(
                f"Narration cue must end in sentence punctuation at line {line_number}"
            )
        if _MULTIPLE_SENTENCES_RE.search(line):
            raise NarrationError(
                f"Narration cue must contain one sentence at line {line_number}"
            )
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
        raise NarrationError("Invalid V3 narration source (" + "; ".join(problems) + ")")

    return {
        scene_id: Narration(scene_id, tuple(sections[scene_id]))
        for scene_id in EXPECTED_SCENE_IDS
    }


def load_narration(path: Path) -> dict[str, Narration]:
    return parse_narration_text(path.read_text(encoding="utf-8"))


def bookmark_name(index: int) -> str:
    return f"cue_{index:03d}"


def build_azure_ssml(narration: Narration, config: AzureConfig) -> str:
    """Build SSML with one bookmark immediately before each sentence."""

    parts = []
    for index, cue in enumerate(narration.cues):
        part = (
            f'<bookmark mark="{bookmark_name(index)}"/>'
            + html.escape(cue, quote=False)
        )
        if index + 1 < len(narration.cues) and config.intercue_break_ms:
            part += f'<break time="{config.intercue_break_ms}ms"/>'
        parts.append(part)
    body = " ".join(parts)
    return (
        '<speak version="1.0" '
        'xmlns="http://www.w3.org/2001/10/synthesis" '
        f'xml:lang="{html.escape(config.locale, quote=True)}">'
        f'<voice name="{html.escape(config.voice, quote=True)}">'
        f'<prosody rate="{html.escape(config.rate, quote=True)}">'
        f"{body}</prosody></voice></speak>"
    )


def cache_key(narration: Narration, config: AzureConfig) -> str:
    return _sha256_json(
        {
            "narration": {
                "scene_id": narration.scene_id,
                "cues": list(narration.cues),
            },
            "synthesis_config": config.cache_dict(),
        }
    )


def voice_metadata_path(audio_path: Path) -> Path:
    return audio_path.with_suffix(".voice.json")


def _wav_facts(path: Path) -> dict[str, int]:
    with wave.open(str(path), "rb") as wav:
        if wav.getcomptype() != "NONE":
            raise ValueError("WAV must contain uncompressed PCM")
        return {
            "sample_rate_hz": wav.getframerate(),
            "channels": wav.getnchannels(),
            "sample_width_bytes": wav.getsampwidth(),
            "frame_count": wav.getnframes(),
        }


def _silence_is_zero(
    path: Path,
    *,
    lead_frames: int,
    tail_frames: int,
) -> bool:
    """Confirm that the authored lead and tail are literal PCM silence."""

    with wave.open(str(path), "rb") as wav:
        total_frames = wav.getnframes()
        lead = wav.readframes(lead_frames)
        if tail_frames:
            wav.setpos(total_frames - tail_frames)
            tail = wav.readframes(tail_frames)
        else:
            tail = b""
    return not any(lead) and not any(tail)


def _frames_to_ticks(frames: int, sample_rate: int) -> int:
    return round(frames * TICKS_PER_SECOND / sample_rate)


def _add_pcm_silence(
    raw_path: Path,
    output_path: Path,
    *,
    lead_ms: int,
    tail_ms: int,
    target_duration_ms: int | None = None,
) -> tuple[int, int]:
    with wave.open(str(raw_path), "rb") as source:
        params = source.getparams()
        if source.getcomptype() != "NONE":
            raise SynthesisError("Azure narration WAV must contain uncompressed PCM")
        payload = source.readframes(source.getnframes())

    lead_frames = round(params.framerate * lead_ms / 1000)
    minimum_tail_frames = round(params.framerate * tail_ms / 1000)
    tail_frames = minimum_tail_frames
    if target_duration_ms is not None:
        target_frames = round(params.framerate * target_duration_ms / 1000)
        raw_frames = len(payload) // (params.sampwidth * params.nchannels)
        tail_frames = target_frames - lead_frames - raw_frames
        if tail_frames < minimum_tail_frames:
            speech_ms = raw_frames * 1000 / params.framerate
            raise SynthesisError(
                "Azure narration does not fit the authored scene duration: "
                f"speech={speech_ms:.1f} ms, target={target_duration_ms} ms"
            )
    silence_frame = b"\0" * params.sampwidth * params.nchannels
    with wave.open(str(output_path), "wb") as output:
        output.setparams(params)
        output.writeframes(silence_frame * lead_frames)
        output.writeframes(payload)
        output.writeframes(silence_frame * tail_frames)
    return lead_frames, tail_frames


def _normalize_pcm_wav(
    source_path: Path,
    output_path: Path,
    *,
    target_dbfs: float,
) -> None:
    """Normalize speech before silence is added, preserving the bookmark clock."""

    with wave.open(str(source_path), "rb") as source:
        params = source.getparams()
        payload = source.readframes(source.getnframes())
    rms = audioop.rms(payload, params.sampwidth)
    if rms:
        full_scale = float(1 << (8 * params.sampwidth - 1))
        current_dbfs = 20 * math.log10(rms / full_scale)
        gain = 10 ** ((target_dbfs - current_dbfs) / 20)
        payload = audioop.mul(payload, params.sampwidth, gain)
    with wave.open(str(output_path), "wb") as output:
        output.setparams(params)
        output.writeframes(payload)


def _raw_suffix(output_format: str) -> str:
    lowered = output_format.lower()
    if "mp3" in lowered:
        return ".mp3"
    if "ogg" in lowered:
        return ".ogg"
    if "webm" in lowered:
        return ".webm"
    if "riff" in lowered:
        return ".wav"
    return ".audio"


def _decode_to_pcm_wav(
    source_path: Path,
    output_path: Path,
    *,
    output_format: str,
) -> None:
    """Decode Azure's selected transport format to 48 kHz mono PCM.

    Azure Speech SDK 1.51 on macOS currently cancels RIFF/RAW file synthesis
    with CoreAudio error -50.  Its documented high-bitrate MP3 transport is
    reliable, and decoding it once here gives the renderer a deterministic PCM
    cache.  The final release encodes that continuous PCM master to AAC once.
    """

    if "riff" in output_format.lower():
        shutil.copyfile(source_path, output_path)
        return
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required to decode Azure narration")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source_path),
            "-ar",
            "48000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(output_path),
        ],
        check=True,
    )


def _trim_pcm_edge_silence(source_path: Path, output_path: Path) -> None:
    """Trim service padding while retaining safe speech-edge pre/post-roll.

    The activity threshold is relative to each cue's loudest 10 ms window, so
    normalization level does not affect the result.  Generous retained edges
    protect quiet consonants while preventing service padding from stacking on
    top of the authored inter-cue pause.
    """

    with wave.open(str(source_path), "rb") as source:
        if source.getcomptype() != "NONE":
            raise SynthesisError("Decoded Azure cue must be PCM WAV")
        channels = source.getnchannels()
        sample_width = source.getsampwidth()
        sample_rate = source.getframerate()
        frame_count = source.getnframes()
        payload = source.readframes(frame_count)
    if frame_count <= 0:
        raise SynthesisError("Azure returned an empty narration cue")

    bytes_per_frame = channels * sample_width
    window_frames = max(1, round(sample_rate * CUE_EDGE_WINDOW_MS / 1000))
    levels = []
    for start in range(0, frame_count, window_frames):
        end = min(frame_count, start + window_frames)
        levels.append(
            audioop.rms(
                payload[start * bytes_per_frame : end * bytes_per_frame],
                sample_width,
            )
        )
    peak = max(levels)
    if peak <= 0:
        raise SynthesisError("Azure returned a silent narration cue")
    threshold = max(
        1,
        round(peak * 10 ** (CUE_EDGE_RELATIVE_THRESHOLD_DB / 20)),
    )
    first_active = next(
        index for index, level in enumerate(levels) if level >= threshold
    )
    last_active = len(levels) - 1 - next(
        index for index, level in enumerate(reversed(levels)) if level >= threshold
    )

    retained_lead_frames = round(sample_rate * CUE_RETAINED_LEAD_MS / 1000)
    retained_tail_frames = round(sample_rate * CUE_RETAINED_TAIL_MS / 1000)
    start_frame = max(0, first_active * window_frames - retained_lead_frames)
    end_frame = min(
        frame_count,
        (last_active + 1) * window_frames + retained_tail_frames,
    )
    if end_frame <= start_frame:
        raise SynthesisError("Azure narration cue has no retained audio")

    with wave.open(str(output_path), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(sample_width)
        output.setframerate(sample_rate)
        output.setcomptype("NONE", "not compressed")
        output.writeframes(
            payload[start_frame * bytes_per_frame : end_frame * bytes_per_frame]
        )


def _concatenate_pcm_segments(
    segment_paths: tuple[Path, ...],
    output_path: Path,
    *,
    intercue_break_ms: int,
) -> dict[str, int]:
    """Join cue recordings and return exact starts in 100 ns ticks.

    MAI-Voice-2 currently returns audio without Speech SDK bookmark or word
    boundary events.  Its sentence recordings are therefore joined at exact
    PCM frame boundaries.  The resulting offsets enter the same metadata,
    subtitle, and semantic-animation clock as native Azure bookmarks.
    """

    if not segment_paths:
        raise SynthesisError("Cue-segment synthesis requires narration cues")

    expected_format: tuple[int, int, int, str] | None = None
    offsets: dict[str, int] = {}
    cursor_frames = 0

    with wave.open(str(output_path), "wb") as output:
        for index, path in enumerate(segment_paths):
            with wave.open(str(path), "rb") as source:
                audio_format = (
                    source.getnchannels(),
                    source.getsampwidth(),
                    source.getframerate(),
                    source.getcomptype(),
                )
                if source.getcomptype() != "NONE":
                    raise SynthesisError("Decoded Azure cue must be PCM WAV")
                if source.getnframes() <= 0:
                    raise SynthesisError("Azure returned an empty narration cue")
                if expected_format is None:
                    expected_format = audio_format
                    channels, sample_width, sample_rate, _ = expected_format
                    output.setnchannels(channels)
                    output.setsampwidth(sample_width)
                    output.setframerate(sample_rate)
                    output.setcomptype("NONE", "not compressed")
                elif audio_format != expected_format:
                    raise SynthesisError(
                        "Decoded Azure cues do not share one PCM format"
                    )

                offsets[bookmark_name(index)] = _frames_to_ticks(
                    cursor_frames,
                    source.getframerate(),
                )
                frame_count = source.getnframes()
                output.writeframesraw(source.readframes(frame_count))
                cursor_frames += frame_count

            if index + 1 < len(segment_paths):
                assert expected_format is not None
                channels, sample_width, sample_rate, _ = expected_format
                break_frames = round(sample_rate * intercue_break_ms / 1000)
                silence_frame = b"\0" * channels * sample_width
                output.writeframesraw(silence_frame * break_frames)
                cursor_frames += break_frames
        output.writeframes(b"")
    return offsets


def _synthesize_cue_segments(
    narration: Narration,
    temporary_dir: Path,
    output_path: Path,
    config: AzureConfig,
    synthesize: RawSynthesizer,
) -> Mapping[str, int]:
    """Synthesize authored cues independently for deterministic MAI timing."""

    decoded_paths: list[Path] = []
    for index, cue in enumerate(narration.cues):
        raw_path = temporary_dir / (
            f"azure-cue-{index:03d}" + _raw_suffix(config.output_format)
        )
        decoded_path = temporary_dir / f"azure-cue-{index:03d}-decoded.wav"
        trimmed_path = temporary_dir / f"azure-cue-{index:03d}-trimmed.wav"
        cue_narration = Narration(narration.scene_id, (cue,))
        # MAI may return an empty mapping here.  In cue-segment mode the exact
        # decoded PCM boundaries, rather than service events, are authoritative.
        synthesize(build_azure_ssml(cue_narration, config), raw_path)
        if not raw_path.is_file():
            raise SynthesisError(
                f"Azure synthesis did not create narration cue {index}"
            )
        _decode_to_pcm_wav(
            raw_path,
            decoded_path,
            output_format=config.output_format,
        )
        _trim_pcm_edge_silence(decoded_path, trimmed_path)
        decoded_paths.append(trimmed_path)

    return _concatenate_pcm_segments(
        tuple(decoded_paths),
        output_path,
        intercue_break_ms=config.intercue_break_ms,
    )


def azure_synthesize_raw(
    ssml: str,
    output_path: Path,
    config: AzureConfig,
) -> Mapping[str, int]:
    """Synthesize raw PCM WAV and return Azure bookmark offsets in 100 ns ticks."""

    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError as exc:
        raise RuntimeError(
            "Azure Speech support is missing; install the project requirements"
        ) from exc

    key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
    region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
    if not key or not region:
        raise RuntimeError(
            "Set SPEECH_KEY and SPEECH_REGION before generating V3 narration"
        )

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    try:
        output_format = getattr(
            speechsdk.SpeechSynthesisOutputFormat,
            config.output_format,
        )
    except AttributeError as exc:
        raise ValueError(
            f"Unknown Azure output format: {config.output_format}"
        ) from exc
    speech_config.set_speech_synthesis_output_format(output_format)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )
    offsets: dict[str, int] = {}

    def on_bookmark(event: object) -> None:
        name = str(getattr(event, "text"))
        if name in offsets:
            raise SynthesisError(f"Azure returned duplicate bookmark {name}")
        offsets[name] = int(getattr(event, "audio_offset"))

    synthesizer.bookmark_reached.connect(on_bookmark)
    result = synthesizer.speak_ssml_async(ssml).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = getattr(result, "cancellation_details", None)
        message = getattr(details, "error_details", None) or str(result.reason)
        raise SynthesisError(f"Azure speech synthesis failed: {message}")
    return offsets


def _metadata_for(
    narration: Narration,
    config: AzureConfig,
    audio_path: Path,
    bookmark_offsets: Mapping[str, int],
    lead_frames: int,
    tail_frames: int,
) -> dict[str, object]:
    expected_marks = [bookmark_name(index) for index in range(len(narration.cues))]
    if set(bookmark_offsets) != set(expected_marks):
        missing = sorted(set(expected_marks) - set(bookmark_offsets))
        unknown = sorted(set(bookmark_offsets) - set(expected_marks))
        raise SynthesisError(
            "Azure bookmark mismatch"
            + (f"; missing: {', '.join(missing)}" if missing else "")
            + (f"; unknown: {', '.join(unknown)}" if unknown else "")
        )

    audio = _wav_facts(audio_path)
    sample_rate = audio["sample_rate_hz"]
    lead_ticks = _frames_to_ticks(lead_frames, sample_rate)
    tail_ticks = _frames_to_ticks(tail_frames, sample_rate)
    duration_ticks = _frames_to_ticks(audio["frame_count"], sample_rate)
    speech_end_ticks = duration_ticks - tail_ticks
    cues = []
    previous = -1
    for index, text in enumerate(narration.cues):
        mark = bookmark_name(index)
        azure_offset = int(bookmark_offsets[mark])
        if azure_offset < 0 or azure_offset <= previous:
            raise SynthesisError("Azure bookmark offsets are not monotonic")
        start_ticks = lead_ticks + azure_offset
        if start_ticks > speech_end_ticks:
            raise SynthesisError(f"Azure bookmark {mark} occurs after speech")
        cues.append(
            {
                "index": index,
                "bookmark": mark,
                "text": text,
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "azure_audio_offset_ticks_100ns": azure_offset,
                "start_ticks_100ns": start_ticks,
                "start_ms": round(start_ticks / 10_000, 4),
            }
        )
        previous = azure_offset

    return {
        "schema": METADATA_SCHEMA,
        "scene_id": narration.scene_id,
        "narration_sha256": narration.digest,
        "cache_key_sha256": cache_key(narration, config),
        "synthesis_config": config.cache_dict(),
        "timing": {
            "mode": config.timing_mode,
            "source": TIMING_SOURCES[config.timing_mode],
        },
        "audio": {
            **audio,
            "sha256": sha256_file(audio_path),
            "duration_ticks_100ns": duration_ticks,
        },
        "speech": {
            "start_ticks_100ns": lead_ticks,
            "end_ticks_100ns": speech_end_ticks,
        },
        "silence": {
            "lead_frames": lead_frames,
            "lead_ticks_100ns": lead_ticks,
            "tail_frames": tail_frames,
            "tail_ticks_100ns": tail_ticks,
        },
        "cues": cues,
    }


def generate_azure(
    narration: Narration,
    audio_path: Path,
    *,
    config: AzureConfig = AzureConfig(),
    raw_synthesizer: RawSynthesizer | None = None,
) -> dict[str, object]:
    """Generate WAV and metadata, replacing the validated pair atomically per file."""

    audio_path = Path(audio_path)
    metadata_path = voice_metadata_path(audio_path)
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    synthesize = raw_synthesizer
    if synthesize is None:
        def synthesize(ssml: str, path: Path) -> Mapping[str, int]:
            for attempt in range(1, AZURE_SYNTHESIS_ATTEMPTS + 1):
                try:
                    return azure_synthesize_raw(ssml, path, config)
                except SynthesisError:
                    if attempt == AZURE_SYNTHESIS_ATTEMPTS:
                        raise
                    path.unlink(missing_ok=True)
                    time.sleep(attempt)
            raise AssertionError("Azure synthesis retry loop did not return")

    with tempfile.TemporaryDirectory(
        prefix=f".{narration.scene_id}-",
        dir=audio_path.parent,
    ) as temp_dir:
        temporary_dir = Path(temp_dir)
        decoded_path = temporary_dir / "azure-decoded.wav"
        normalized_path = temporary_dir / "azure-normalized.wav"
        final_path = temporary_dir / audio_path.name
        metadata_temp = temporary_dir / metadata_path.name
        if config.timing_mode == TIMING_MODE_CUE_SEGMENTS:
            offsets = _synthesize_cue_segments(
                narration,
                temporary_dir,
                decoded_path,
                config,
                synthesize,
            )
        else:
            raw_path = temporary_dir / (
                "azure-raw" + _raw_suffix(config.output_format)
            )
            offsets = synthesize(build_azure_ssml(narration, config), raw_path)
            if not raw_path.is_file():
                raise SynthesisError("Azure synthesis did not create an audio file")
            _decode_to_pcm_wav(
                raw_path,
                decoded_path,
                output_format=config.output_format,
            )
        _normalize_pcm_wav(
            decoded_path,
            normalized_path,
            target_dbfs=config.target_dbfs,
        )
        lead_frames, tail_frames = _add_pcm_silence(
            normalized_path,
            final_path,
            lead_ms=config.lead_silence_ms,
            tail_ms=config.tail_silence_ms,
            target_duration_ms=config.target_duration_ms,
        )
        metadata = _metadata_for(
            narration,
            config,
            final_path,
            offsets,
            lead_frames,
            tail_frames,
        )
        metadata_temp.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(final_path, audio_path)
        os.replace(metadata_temp, metadata_path)
    return metadata


def validate_existing(
    narration: Narration,
    audio_path: Path,
    *,
    config: AzureConfig = AzureConfig(),
) -> dict[str, object]:
    """Strictly validate an existing WAV and its exact transcript/config cache."""

    audio_path = Path(audio_path)
    metadata_path = voice_metadata_path(audio_path)
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("schema") != METADATA_SCHEMA:
            raise ValueError("metadata schema mismatch")
        if metadata.get("scene_id") != narration.scene_id:
            raise ValueError("scene id mismatch")
        if metadata.get("narration_sha256") != narration.digest:
            raise ValueError("narration changed")
        if metadata.get("synthesis_config") != config.cache_dict():
            raise ValueError("synthesis configuration changed")
        expected_timing = {
            "mode": config.timing_mode,
            "source": TIMING_SOURCES[config.timing_mode],
        }
        recorded_timing = metadata.get("timing")
        if recorded_timing is None:
            # Schema-3 native-bookmark caches created before timing provenance
            # was recorded remain valid.  Alternate modes are always explicit.
            if config.timing_mode != TIMING_MODE_AZURE_BOOKMARKS:
                raise ValueError("timing provenance is missing")
        elif recorded_timing != expected_timing:
            raise ValueError("timing provenance mismatch")
        if metadata.get("cache_key_sha256") != cache_key(narration, config):
            raise ValueError("cache key mismatch")
        actual = _wav_facts(audio_path)
        if (
            actual["sample_rate_hz"] != 48_000
            or actual["channels"] != 1
            or actual["sample_width_bytes"] != 2
        ):
            raise ValueError("audio must be 48 kHz, mono, 16-bit PCM")
        recorded_audio = metadata["audio"]
        for key, value in actual.items():
            if recorded_audio.get(key) != value:
                raise ValueError(f"audio {key} mismatch")
        if recorded_audio.get("sha256") != sha256_file(audio_path):
            raise ValueError("audio hash mismatch")
        duration_ticks = _frames_to_ticks(
            actual["frame_count"], actual["sample_rate_hz"]
        )
        if recorded_audio.get("duration_ticks_100ns") != duration_ticks:
            raise ValueError("audio duration mismatch")
        cues = metadata["cues"]
        if len(cues) != len(narration.cues):
            raise ValueError("cue count mismatch")
        previous_start = -1
        previous_azure_offset = -1
        speech_end = int(metadata["speech"]["end_ticks_100ns"])
        silence = metadata["silence"]
        lead_frames = int(silence["lead_frames"])
        tail_frames = int(silence["tail_frames"])
        lead_ticks = int(silence["lead_ticks_100ns"])
        tail_ticks = int(silence["tail_ticks_100ns"])
        if lead_frames < 0 or tail_frames < 0:
            raise ValueError("silence frame counts cannot be negative")
        if lead_ticks != _frames_to_ticks(lead_frames, actual["sample_rate_hz"]):
            raise ValueError("lead frame/tick mismatch")
        if tail_ticks != _frames_to_ticks(tail_frames, actual["sample_rate_hz"]):
            raise ValueError("tail frame/tick mismatch")
        for index, (cue, text) in enumerate(zip(cues, narration.cues)):
            if cue.get("index") != index:
                raise ValueError("cue index mismatch")
            if cue.get("bookmark") != bookmark_name(index):
                raise ValueError("cue bookmark mismatch")
            if cue.get("text") != text:
                raise ValueError("cue transcript mismatch")
            expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if cue.get("text_sha256") != expected_hash:
                raise ValueError("cue transcript hash mismatch")
            start = int(cue["start_ticks_100ns"])
            azure_offset = int(cue["azure_audio_offset_ticks_100ns"])
            if azure_offset < 0 or azure_offset <= previous_azure_offset:
                raise ValueError("Azure bookmark offsets are not strictly increasing")
            if start != lead_ticks + azure_offset:
                raise ValueError("cue start/bookmark offset mismatch")
            if start <= previous_start or start > speech_end:
                raise ValueError("cue timestamps are invalid")
            if cue.get("start_ms") != round(start / 10_000, 4):
                raise ValueError("cue millisecond timestamp mismatch")
            previous_start = start
            previous_azure_offset = azure_offset
        if lead_frames != round(
            actual["sample_rate_hz"] * config.lead_silence_ms / 1000
        ):
            raise ValueError("lead silence mismatch")
        if tail_ticks < round(config.tail_silence_ms * 10_000):
            raise ValueError("tail silence is shorter than configured")
        if int(metadata["speech"]["start_ticks_100ns"]) != lead_ticks:
            raise ValueError("speech/lead boundary mismatch")
        if speech_end != duration_ticks - tail_ticks:
            raise ValueError("speech/tail boundary mismatch")
        if not _silence_is_zero(
            audio_path,
            lead_frames=lead_frames,
            tail_frames=tail_frames,
        ):
            raise ValueError("authored lead or tail silence contains samples")
        if config.target_duration_ms is not None:
            expected_frames = round(
                actual["sample_rate_hz"] * config.target_duration_ms / 1000
            )
            if actual["frame_count"] != expected_frames:
                raise ValueError("target duration mismatch")
    except (
        FileNotFoundError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        wave.Error,
    ) as exc:
        raise StaleAudioError(
            f"Existing V3 narration for {narration.scene_id} is missing or stale: "
            f"{exc}"
        ) from None
    return metadata


def subtitle_intervals(
    narration: Narration,
    metadata: Mapping[str, object],
) -> tuple[SubtitleInterval, ...]:
    """Use stored bookmark starts; the final cue ends at the speech/tail boundary."""

    if metadata.get("scene_id") != narration.scene_id:
        raise ValueError("Metadata scene does not match narration")
    if metadata.get("narration_sha256") != narration.digest:
        raise ValueError("Metadata narration does not match")
    cues = metadata.get("cues")
    speech = metadata.get("speech")
    if not isinstance(cues, list) or not isinstance(speech, Mapping):
        raise ValueError("Metadata does not contain cue timing")
    if len(cues) != len(narration.cues):
        raise ValueError("Metadata cue count does not match narration")
    speech_end = int(speech["end_ticks_100ns"])
    intervals = []
    for index, text in enumerate(narration.cues):
        start = int(cues[index]["start_ticks_100ns"])
        end = (
            int(cues[index + 1]["start_ticks_100ns"])
            if index + 1 < len(cues)
            else speech_end
        )
        if end < start:
            raise ValueError("Subtitle cue timestamps are not monotonic")
        intervals.append(
            SubtitleInterval(
                start=start / TICKS_PER_SECOND,
                end=end / TICKS_PER_SECOND,
                text=text,
            )
        )
    return tuple(intervals)

from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from pydub import AudioSegment


@dataclass
class MediaInfo:
    path: Path
    duration: float
    width: int | None
    height: int | None
    frame_rate: float | None
    has_audio: bool
    has_video: bool
    raw: dict


@dataclass
class FrameAnalysis:
    frames: list[Path]
    contact_sheet: Path | None
    mean_luma: list[float]
    contrast: list[float]
    adjacent_diff: list[float]


@dataclass
class AudioStats:
    duration_seconds: float
    dbfs: float
    max_dbfs: float


def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def ffprobe(video_path: Path) -> MediaInfo:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,width,height,r_frame_rate",
        "-of",
        "json",
        str(video_path),
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    raw = json.loads(result.stdout)
    streams = raw.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    frame_rate = _parse_rate(video_stream.get("r_frame_rate"))
    return MediaInfo(
        path=video_path,
        duration=float(raw.get("format", {}).get("duration", 0.0)),
        width=video_stream.get("width"),
        height=video_stream.get("height"),
        frame_rate=frame_rate,
        has_audio=audio_stream is not None,
        has_video=bool(video_stream),
        raw=raw,
    )


def sample_frames(video_path: Path, duration: float, artifacts_dir: Path, count: int = 8) -> FrameAnalysis:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    if duration <= 0:
        return FrameAnalysis([], None, [], [], [])

    start = min(0.5, duration / 4)
    end = max(start, duration - 0.5)
    if count <= 1 or math.isclose(start, end):
        timestamps = [duration / 2]
    else:
        step = (end - start) / (count - 1)
        timestamps = [start + i * step for i in range(count)]

    frames: list[Path] = []
    for index, timestamp in enumerate(timestamps, start=1):
        frame_path = artifacts_dir / f"frame_{index:02d}_{timestamp:06.2f}s.png"
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            f"{timestamp:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            str(frame_path),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        frames.append(frame_path)

    mean_luma, contrast = _frame_luma_stats(frames)
    adjacent_diff = _adjacent_diffs(frames)
    contact_sheet = make_contact_sheet(frames, artifacts_dir / "contact_sheet.png")
    return FrameAnalysis(frames, contact_sheet, mean_luma, contrast, adjacent_diff)


def make_contact_sheet(frames: list[Path], out_path: Path, thumb_width: int = 240) -> Path | None:
    if not frames:
        return None
    thumbs = []
    for frame in frames:
        image = Image.open(frame).convert("RGB")
        ratio = thumb_width / image.width
        thumb = image.resize((thumb_width, max(1, int(image.height * ratio))))
        thumbs.append(thumb)

    cols = min(4, len(thumbs))
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * thumbs[0].width, rows * thumbs[0].height), "white")
    for idx, thumb in enumerate(thumbs):
        x = (idx % cols) * thumb.width
        y = (idx // cols) * thumb.height
        sheet.paste(thumb, (x, y))
    sheet.save(out_path)
    return out_path


def audio_stats(video_path: Path) -> AudioStats:
    with tempfile.TemporaryDirectory() as tmp:
        wav_path = Path(tmp) / "audio.wav"
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "48000",
            "-ac",
            "1",
            str(wav_path),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segment = AudioSegment.from_file(wav_path)
        return AudioStats(
            duration_seconds=len(segment) / 1000,
            dbfs=float(segment.dBFS),
            max_dbfs=float(segment.max_dBFS),
        )


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    if not path.exists():
        return []
    blocks = path.read_text(encoding="utf-8", errors="replace").strip().split("\n\n")
    entries: list[tuple[float, float, str]] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2 or "-->" not in lines[1]:
            continue
        start_s, end_s = [part.strip() for part in lines[1].split("-->", 1)]
        entries.append((_parse_srt_time(start_s), _parse_srt_time(end_s), " ".join(lines[2:])))
    return entries


def _parse_rate(value: str | None) -> float | None:
    if not value:
        return None
    if "/" in value:
        top, bottom = value.split("/", 1)
        denom = float(bottom)
        return float(top) / denom if denom else None
    return float(value)


def _frame_luma_stats(frames: list[Path]) -> tuple[list[float], list[float]]:
    means: list[float] = []
    contrasts: list[float] = []
    for frame in frames:
        image = Image.open(frame).convert("L")
        stat = ImageStat.Stat(image)
        means.append(float(stat.mean[0]))
        contrasts.append(float(stat.stddev[0]))
    return means, contrasts


def _adjacent_diffs(frames: list[Path]) -> list[float]:
    diffs: list[float] = []
    images = [Image.open(frame).convert("L") for frame in frames]
    for prev, curr in zip(images, images[1:]):
        diff = ImageChops.difference(prev, curr)
        diffs.append(float(ImageStat.Stat(diff).mean[0]))
    return diffs


def _parse_srt_time(value: str) -> float:
    hours, minutes, rest = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)

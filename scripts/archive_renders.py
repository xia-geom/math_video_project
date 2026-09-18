#!/usr/bin/env python3
"""Keep a local, deduplicated history of rendered MP4 files."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIST_ROOT = PROJECT_ROOT / "dist"
ARCHIVE_DIRNAME = "_render_archive"
SCHEMA_VERSION = 1


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_state(project_root: Path) -> tuple[str, bool]:
    def capture(*args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    try:
        commit = capture("rev-parse", "--short=12", "HEAD")
        dirty = bool(capture("status", "--porcelain", "--untracked-files=no"))
    except (OSError, subprocess.CalledProcessError):
        return "unknown", False
    return commit, dirty


def probe_media(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(path),
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        raw = json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"ffprobe failed for {path}: {exc}") from exc

    video_streams = [
        stream for stream in raw.get("streams", []) if stream.get("codec_type") == "video"
    ]
    if not video_streams:
        raise RuntimeError(f"no video stream found in {path}")
    video = video_streams[0]
    rate_text = video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1"
    try:
        frame_rate = float(Fraction(rate_text))
    except (ValueError, ZeroDivisionError):
        frame_rate = 0.0
    try:
        duration = float(raw.get("format", {}).get("duration", 0.0))
    except (TypeError, ValueError):
        duration = 0.0
    return {
        "duration_seconds": round(duration, 6),
        "width": int(video.get("width", 0)),
        "height": int(video.get("height", 0)),
        "frame_rate": round(frame_rate, 6),
        "has_audio": any(
            stream.get("codec_type") == "audio" for stream in raw.get("streams", [])
        ),
    }


def infer_quality(media: dict[str, Any]) -> str | None:
    signature = (
        media["width"],
        media["height"],
        round(float(media["frame_rate"]), 3),
    )
    return {
        (854, 480, 15.0): "ql",
        (1280, 720, 30.0): "qm",
        (1920, 1080, 60.0): "qh",
    }.get(signature)


def fps_label(frame_rate: float) -> str:
    rounded = round(frame_rate)
    if abs(frame_rate - rounded) < 0.001:
        value = str(rounded)
    else:
        value = f"{frame_rate:.2f}".rstrip("0").rstrip(".")
    return value + "fps"


def read_records(index_path: Path) -> list[dict[str, Any]]:
    if not index_path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid archive index line {line_number}: {exc}") from exc
    return records


def relative_video_path(video: Path, dist_root: Path) -> Path:
    resolved = video.resolve()
    try:
        relative = resolved.relative_to(dist_root.resolve())
    except ValueError as exc:
        raise ValueError(f"video must be inside {dist_root}: {video}") from exc
    if relative.parts and relative.parts[0] == ARCHIVE_DIRNAME:
        raise ValueError("cannot archive a file already inside the render archive")
    return relative


def store_object(video: Path, object_path: Path) -> None:
    if object_path.is_file():
        return
    object_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f".{object_path.name}.", dir=object_path.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        shutil.copy2(video, temporary)
        os.replace(temporary, object_path)
    finally:
        temporary.unlink(missing_ok=True)


def link_version(object_path: Path, version_path: Path) -> None:
    if version_path.exists():
        return
    version_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(object_path, version_path)
    except OSError:
        shutil.copy2(object_path, version_path)


def register_video(
    video: Path,
    *,
    dist_root: Path = DEFAULT_DIST_ROOT,
    archive_root: Path | None = None,
    quality: str | None = None,
    snapshot_label: str | None = None,
    observed_only: bool = False,
    now: datetime | None = None,
    project_root: Path = PROJECT_ROOT,
) -> tuple[dict[str, Any], bool]:
    video = video.resolve()
    dist_root = dist_root.resolve()
    archive_root = (archive_root or dist_root / ARCHIVE_DIRNAME).resolve()
    if not video.is_file() or video.suffix.lower() != ".mp4":
        raise FileNotFoundError(f"MP4 not found: {video}")
    relative = relative_video_path(video, dist_root)
    digest = sha256_file(video)
    media = probe_media(video)
    commit, dirty = git_state(project_root)
    moment = now or datetime.now().astimezone()
    timestamp = moment.strftime("%Y%m%d-%H%M%S")
    iso_timestamp = moment.isoformat()
    quality = quality or infer_quality(media)
    index_path = archive_root / "index.jsonl"
    lock_path = archive_root / ".index.lock"
    archive_root.mkdir(parents=True, exist_ok=True)

    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        records = read_records(index_path)
        for record in records:
            if record["original_path"] == relative.as_posix() and record["sha256"] == digest:
                return record, False

        object_path = archive_root / "objects" / digest[:2] / f"{digest}.mp4"
        store_object(video, object_path)
        media_label = (
            f"{media['width']}x{media['height']}-{fps_label(media['frame_rate'])}"
        )
        version_name = (
            f"{video.stem}__{timestamp}__git-{commit}__{media_label}.mp4"
        )
        version_path = archive_root / "versions" / relative.parent / video.stem / version_name
        collision = 1
        while version_path.exists() and sha256_file(version_path) != digest:
            version_path = version_path.with_name(
                f"{version_path.stem}-{collision}{version_path.suffix}"
            )
            collision += 1
        link_version(object_path, version_path)

        identity = hashlib.sha256(
            f"{relative.as_posix()}\0{digest}".encode("utf-8")
        ).hexdigest()[:20]
        record: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "version_id": identity,
            "original_path": relative.as_posix(),
            "archive_path": version_path.relative_to(archive_root).as_posix(),
            "object_path": object_path.relative_to(archive_root).as_posix(),
            "archive_label": version_name,
            "snapshot_label": snapshot_label,
            "archived_at": iso_timestamp,
            "git_commit": commit,
            "git_dirty": dirty,
            "sha256": digest,
            "size_bytes": video.stat().st_size,
            "duration_seconds": media["duration_seconds"],
            "width": media["width"],
            "height": media["height"],
            "frame_rate": media["frame_rate"],
            "has_audio": media["has_audio"],
            "render_quality": quality,
        }
        if observed_only:
            record["observed_at_commit"] = commit
            record["render_commit"] = None
        else:
            record["render_commit"] = commit

        with index_path.open("a", encoding="utf-8") as index:
            index.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            index.flush()
            os.fsync(index.fileno())
        return record, True


def iter_dist_videos(dist_root: Path) -> Iterable[Path]:
    archive_root = (dist_root / ARCHIVE_DIRNAME).resolve()
    for video in sorted(dist_root.rglob("*.mp4")):
        try:
            video.resolve().relative_to(archive_root)
        except ValueError:
            yield video


def snapshot(
    *,
    dist_root: Path = DEFAULT_DIST_ROOT,
    archive_root: Path | None = None,
    label: str,
    project_root: Path = PROJECT_ROOT,
) -> tuple[int, int]:
    total = 0
    added = 0
    for video in iter_dist_videos(dist_root):
        total += 1
        _, created = register_video(
            video,
            dist_root=dist_root,
            archive_root=archive_root,
            snapshot_label=label,
            observed_only=True,
            project_root=project_root,
        )
        added += int(created)
    return total, added


def restore_version(
    version_id: str,
    output: Path,
    *,
    archive_root: Path,
) -> dict[str, Any]:
    matches = [
        record
        for record in read_records(archive_root / "index.jsonl")
        if record["version_id"] == version_id
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one archive version {version_id!r}, found {len(matches)}")
    record = matches[0]
    source = archive_root / record["object_path"]
    if sha256_file(source) != record["sha256"]:
        raise RuntimeError(f"archive object checksum mismatch: {source}")
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{output.name}.", dir=output.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-root", type=Path, default=DEFAULT_DIST_ROOT)
    parser.add_argument("--archive-root", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--label", required=True)

    register_parser = subparsers.add_parser("register")
    register_parser.add_argument("video", type=Path)
    register_parser.add_argument("--quality", choices=("ql", "qm", "qh"))

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--path", type=Path)

    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("version_id")
    restore_parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    dist_root = args.dist_root.resolve()
    archive_root = (args.archive_root or dist_root / ARCHIVE_DIRNAME).resolve()
    if args.command == "snapshot":
        total, added = snapshot(
            dist_root=dist_root,
            archive_root=archive_root,
            label=args.label,
        )
        print(f"Archive snapshot: {added} added, {total - added} unchanged, {total} total")
    elif args.command == "register":
        record, created = register_video(
            args.video,
            dist_root=dist_root,
            archive_root=archive_root,
            quality=args.quality,
        )
        status = "registered" if created else "unchanged"
        print(f"Archive {status}: {record['version_id']} {record['original_path']}")
    elif args.command == "list":
        records = read_records(archive_root / "index.jsonl")
        if args.path:
            requested = args.path.as_posix()
            try:
                requested = args.path.resolve().relative_to(dist_root).as_posix()
            except ValueError:
                pass
            records = [record for record in records if record["original_path"] == requested]
        for record in records:
            print(
                f"{record['version_id']}  {record['archived_at']}  "
                f"{record['sha256'][:12]}  {record['original_path']}"
            )
    elif args.command == "restore":
        record = restore_version(args.version_id, args.output, archive_root=archive_root)
        print(f"Restored {record['version_id']} to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

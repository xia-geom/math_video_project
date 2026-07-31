#!/usr/bin/env python3
"""Render, validate, package, and mirror the new French curriculum collection."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT_ROOT / "curriculum" / "nouveau_programme_fr.yaml"
QUALITY_SPECS = {
    "ql": (854, 480, Fraction(15, 1)),
    "qm": (1280, 720, Fraction(30, 1)),
    "qh": (1920, 1080, Fraction(60, 1)),
}


@dataclass(frozen=True)
class Entry:
    order: int
    track: str
    module: str
    title: str
    delivery_slug: str
    scene_file: str
    scene_class: str
    coverage: str

    @property
    def artifact_slug(self) -> str:
        return Path(self.scene_file).parent.name

    @property
    def source_video(self) -> Path:
        return PROJECT_ROOT / "dist" / self.artifact_slug / f"{self.artifact_slug}.mp4"

    @property
    def source_subtitle(self) -> Path:
        return PROJECT_ROOT / "dist" / self.artifact_slug / f"{self.artifact_slug}.srt"

    @property
    def delivery_name(self) -> str:
        return f"{self.order:02d}_{self.delivery_slug}"

    @property
    def collection_root(self) -> str:
        return "1 - Programme principal" if self.track == "core" else "2 - Suppléments"


def read_manifest(path: Path) -> tuple[dict[str, Any], list[Entry]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    required_top = {"version", "title", "package_root", "drive_root", "entries"}
    missing_top = required_top - set(raw or {})
    if missing_top:
        raise ValueError(f"Manifest missing top-level fields: {sorted(missing_top)}")

    required_entry = {
        "order",
        "track",
        "module",
        "title",
        "delivery_slug",
        "scene_file",
        "scene_class",
        "coverage",
    }
    entries: list[Entry] = []
    seen: set[tuple[str, int]] = set()
    for index, item in enumerate(raw["entries"], start=1):
        missing = required_entry - set(item)
        if missing:
            raise ValueError(f"Manifest entry {index} missing fields: {sorted(missing)}")
        entry = Entry(**{field: item[field] for field in required_entry})
        if entry.track not in {"core", "supplement"}:
            raise ValueError(f"Invalid track for {entry.scene_class}: {entry.track!r}")
        key = (entry.track, entry.order)
        if key in seen:
            raise ValueError(f"Duplicate order within track: {key}")
        seen.add(key)
        scene_path = PROJECT_ROOT / entry.scene_file
        if not scene_path.is_file():
            raise FileNotFoundError(f"Scene source not found: {scene_path}")
        entries.append(entry)

    core_orders = sorted(entry.order for entry in entries if entry.track == "core")
    supplement_orders = sorted(entry.order for entry in entries if entry.track == "supplement")
    if core_orders != list(range(1, 25)):
        raise ValueError(f"Core orders must be 1..24, got {core_orders}")
    if supplement_orders != list(range(1, 10)):
        raise ValueError(f"Supplement orders must be 1..9, got {supplement_orders}")

    return raw, sorted(entries, key=lambda entry: (entry.track != "core", entry.order))


def select_entries(
    entries: list[Entry],
    *,
    track: str,
    orders: set[int] | None,
) -> list[Entry]:
    selected = [
        entry
        for entry in entries
        if track == "all"
        or (track == "core" and entry.track == "core")
        or (track == "supplements" and entry.track == "supplement")
    ]
    if orders:
        selected = [entry for entry in selected if entry.order in orders]
    return selected


def probe_video(path: Path) -> dict[str, Any]:
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
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def validate_media(
    entry: Entry,
    *,
    quality: str | None,
    require_subtitle: bool,
    require_audio: bool = True,
) -> list[str]:
    errors: list[str] = []
    if not entry.source_video.is_file():
        return [f"missing MP4: {entry.source_video}"]

    try:
        metadata = probe_video(entry.source_video)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        return [f"ffprobe failed for {entry.source_video}: {exc}"]

    video_streams = [
        stream for stream in metadata.get("streams", []) if stream.get("codec_type") == "video"
    ]
    audio_streams = [
        stream for stream in metadata.get("streams", []) if stream.get("codec_type") == "audio"
    ]
    if not video_streams:
        errors.append("no video stream")
    if require_audio and not audio_streams:
        errors.append("no audio stream")
    if require_subtitle and not entry.source_subtitle.is_file():
        errors.append(f"missing SRT: {entry.source_subtitle}")

    try:
        duration = float(metadata.get("format", {}).get("duration", 0))
        if duration <= 0:
            errors.append("duration is not positive")
    except (TypeError, ValueError):
        errors.append("duration is invalid")

    if quality and video_streams:
        expected_width, expected_height, expected_rate = QUALITY_SPECS[quality]
        stream = video_streams[0]
        dimensions = (int(stream.get("width", 0)), int(stream.get("height", 0)))
        if dimensions != (expected_width, expected_height):
            errors.append(
                f"dimensions are {dimensions[0]}x{dimensions[1]}, "
                f"expected {expected_width}x{expected_height}"
            )
        try:
            rate = Fraction(stream.get("r_frame_rate", "0/1"))
        except (ValueError, ZeroDivisionError):
            rate = Fraction(0, 1)
        if rate != expected_rate:
            errors.append(f"frame rate is {rate}, expected {expected_rate}")

    return errors


def render_entries(
    entries: list[Entry],
    *,
    quality: str,
    resume: bool,
    disable_voiceover: bool,
) -> None:
    failures: list[str] = []
    for position, entry in enumerate(entries, start=1):
        if resume:
            errors = validate_media(
                entry,
                quality=quality,
                require_subtitle=entry.track == "core" and not disable_voiceover,
                require_audio=not disable_voiceover,
            )
            if not errors:
                print(f"[{position}/{len(entries)}] Reusing {entry.delivery_name}")
                continue

        print(f"[{position}/{len(entries)}] Rendering {entry.delivery_name}")
        env = os.environ.copy()
        env["RENDER_SKIP_DRIVE_COPY"] = "1"
        if disable_voiceover:
            env["MANIM_DISABLE_VOICEOVER"] = "1"
        command = [
            str(PROJECT_ROOT / "scripts" / "render.sh"),
            entry.scene_file,
            entry.scene_class,
            quality,
        ]
        result = subprocess.run(command, cwd=PROJECT_ROOT, env=env)
        if result.returncode:
            failures.append(f"{entry.delivery_name}: render exited {result.returncode}")
            continue

        errors = validate_media(
            entry,
            quality=quality,
            require_subtitle=entry.track == "core" and not disable_voiceover,
            require_audio=not disable_voiceover,
        )
        if errors:
            failures.append(f"{entry.delivery_name}: {'; '.join(errors)}")

    if failures:
        joined = "\n  - ".join(failures)
        raise RuntimeError(f"Curriculum render failures:\n  - {joined}")


def write_playlist_csv(root: Path, entries: list[Entry]) -> None:
    with (root / "playlist.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "track",
                "order",
                "module",
                "title",
                "scene_class",
                "video",
                "subtitles",
                "coverage",
            ]
        )
        for entry in entries:
            relative_dir = Path(entry.collection_root) / entry.module
            video = relative_dir / f"{entry.delivery_name}.mp4"
            subtitle = relative_dir / f"{entry.delivery_name}.srt"
            writer.writerow(
                [
                    entry.track,
                    entry.order,
                    entry.module,
                    entry.title,
                    entry.scene_class,
                    video.as_posix(),
                    subtitle.as_posix() if (root / subtitle).is_file() else "",
                    entry.coverage,
                ]
            )


def write_collection_index(root: Path, title: str, entries: list[Entry]) -> None:
    lines = [
        f"# {title}",
        "",
        "Les vidéos du programme principal sont numérotées dans l'ordre recommandé.",
        "Les suppléments forment une collection séparée.",
        "",
    ]
    for track, heading in (("core", "Programme principal"), ("supplement", "Suppléments")):
        track_entries = [entry for entry in entries if entry.track == track]
        if not track_entries:
            continue
        lines.extend([f"## {heading}", ""])
        active_module = None
        for entry in track_entries:
            if entry.module != active_module:
                active_module = entry.module
                lines.extend([f"### {active_module}", ""])
            lines.append(f"{entry.order:02d}. **{entry.title}** — {entry.coverage}")
        lines.append("")
    (root / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def write_checksums(root: Path) -> None:
    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS.txt"
    )
    lines = []
    for path in files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(root).as_posix()}")
    (root / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def package_entries(
    manifest: dict[str, Any],
    entries: list[Entry],
    *,
    package_root: Path,
) -> None:
    core_entries = [entry for entry in entries if entry.track == "core"]
    if core_entries and len(core_entries) != 24:
        raise ValueError("A packaged core collection must contain exactly 24 entries")

    failures: list[str] = []
    for entry in entries:
        errors = validate_media(
            entry,
            quality="qh" if entry.track == "core" else None,
            require_subtitle=entry.track == "core",
            # Supplements are preserved exactly as previously rendered; the
            # production audio requirement applies only to the 24 core videos.
            require_audio=entry.track == "core",
        )
        if errors:
            failures.append(f"{entry.delivery_name}: {'; '.join(errors)}")
    if failures:
        joined = "\n  - ".join(failures)
        raise RuntimeError(f"Cannot package invalid media:\n  - {joined}")

    package_root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".{package_root.name}-",
        dir=package_root.parent,
    ) as temporary:
        staging = Path(temporary) / package_root.name
        staging.mkdir()
        for entry in entries:
            destination = staging / entry.collection_root / entry.module
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry.source_video, destination / f"{entry.delivery_name}.mp4")
            if entry.source_subtitle.is_file():
                shutil.copy2(entry.source_subtitle, destination / f"{entry.delivery_name}.srt")

        coverage = PROJECT_ROOT / "curriculum" / "couverture_programme.md"
        shutil.copy2(coverage, staging / coverage.name)
        write_playlist_csv(staging, entries)
        write_collection_index(staging, manifest["title"], entries)
        write_checksums(staging)

        previous = package_root.with_name(f".{package_root.name}.previous")
        if previous.exists():
            shutil.rmtree(previous)
        if package_root.exists():
            package_root.rename(previous)
        staging.rename(package_root)
        if previous.exists():
            shutil.rmtree(previous)

    print(f"Package: {package_root}")


def mirror_to_drive(package_root: Path, drive_root: Path) -> None:
    if not package_root.is_dir():
        raise FileNotFoundError(f"Package does not exist: {package_root}")
    drive_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package_root, drive_root, dirs_exist_ok=True)
    print(f"Drive mirror: {drive_root}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--track",
        choices=("core", "supplements", "all"),
        default="core",
    )
    parser.add_argument("--order", type=int, action="append", dest="orders")
    parser.add_argument("--quality", choices=tuple(QUALITY_SPECS), default="qh")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--disable-voiceover", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--drive", action="store_true")
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--drive-root", type=Path)
    parser.add_argument("--list", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    manifest_path = args.manifest.resolve()
    manifest, all_entries = read_manifest(manifest_path)
    entries = select_entries(
        all_entries,
        track=args.track,
        orders=set(args.orders) if args.orders else None,
    )
    if not entries:
        raise ValueError("No curriculum entries matched the selection")

    if args.list:
        for entry in entries:
            print(
                f"{entry.track:10} {entry.order:02d} "
                f"{entry.scene_class:40} {entry.scene_file}"
            )

    if args.render:
        render_entries(
            entries,
            quality=args.quality,
            resume=args.resume,
            disable_voiceover=args.disable_voiceover,
        )

    if args.validate:
        failures = []
        for entry in entries:
            errors = validate_media(
                entry,
                quality=args.quality if entry.track == "core" else None,
                require_subtitle=entry.track == "core" and not args.disable_voiceover,
                require_audio=entry.track == "core" and not args.disable_voiceover,
            )
            if errors:
                failures.append(f"{entry.delivery_name}: {'; '.join(errors)}")
        if failures:
            raise RuntimeError("Validation failures:\n  - " + "\n  - ".join(failures))
        print(f"Validated {len(entries)} curriculum entries")

    package_root = args.package_root or (PROJECT_ROOT / manifest["package_root"])
    package_root = package_root.resolve()
    if args.package or args.drive:
        package_entries(manifest, entries, package_root=package_root)
    if args.drive:
        drive_root = (args.drive_root or Path(manifest["drive_root"])).expanduser().resolve()
        mirror_to_drive(package_root, drive_root)

    if not any(
        (args.list, args.render, args.validate, args.package, args.drive)
    ):
        print("Manifest is valid. Use --list, --render, --validate, --package, or --drive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

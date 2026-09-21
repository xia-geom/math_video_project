#!/usr/bin/env python3
"""Render, validate, package, and mirror the French mathematics collections."""

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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.course_catalog import load_catalog  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT_ROOT / "curriculum" / "programme_principal_fr.yaml"
QUALITY_SPECS = {
    "ql": (854, 480, Fraction(15, 1)),
    "qm": (1280, 720, Fraction(30, 1)),
    "qh": (1920, 1080, Fraction(60, 1)),
}
ARCHIVE_SCRIPT = PROJECT_ROOT / "scripts" / "archive_renders.py"


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
    lesson_id: str
    legacy_id: str
    requires_narration: bool

    @property
    def artifact_slug(self) -> str:
        return self.delivery_name

    @property
    def source_video(self) -> Path:
        return PROJECT_ROOT / "dist" / self.artifact_slug / f"{self.artifact_slug}.mp4"

    @property
    def source_subtitle(self) -> Path:
        return PROJECT_ROOT / "dist" / self.artifact_slug / f"{self.artifact_slug}.srt"

    def rendered_video(self, quality: str) -> Path:
        if quality == "qh":
            return self.source_video
        return (
            PROJECT_ROOT
            / "dist"
            / "_previews"
            / quality
            / self.artifact_slug
            / f"{self.artifact_slug}__{quality}.mp4"
        )

    def rendered_subtitle(self, quality: str) -> Path:
        if quality == "qh":
            return self.source_subtitle
        return self.rendered_video(quality).with_suffix(".srt")

    @property
    def delivery_name(self) -> str:
        return f"{self.order:02d}_{self.delivery_slug}"

    @property
    def is_production_lesson(self) -> bool:
        return self.requires_narration

    @property
    def package_relative_dir(self) -> Path:
        return Path(self.module) if self.track == "programme" else Path()


def read_manifest(path: Path) -> tuple[dict[str, Any], list[Entry]]:
    raw, rows = load_catalog(path, root=PROJECT_ROOT)
    fields = set(Entry.__dataclass_fields__)
    return raw, [Entry(**{key: row[key] for key in fields}) for row in rows]


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
        or (track == "programme" and entry.track == "programme")
        or (track == "errors" and entry.track == "errors")
    ]
    if orders is not None:
        unknown = orders - {entry.order for entry in selected}
        if unknown:
            raise ValueError(f"Unknown global course numbers for this track: {sorted(unknown)}")
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
    video_path: Path | None = None,
    subtitle_path: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    video_path = video_path or entry.source_video
    subtitle_path = subtitle_path or entry.source_subtitle
    if not video_path.is_file():
        return [f"missing MP4: {video_path}"]

    try:
        metadata = probe_video(video_path)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        return [f"ffprobe failed for {video_path}: {exc}"]

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
    if require_subtitle and not subtitle_path.is_file():
        errors.append(f"missing SRT: {subtitle_path}")

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
                quality=quality if entry.is_production_lesson else None,
                require_subtitle=entry.is_production_lesson and not disable_voiceover,
                require_audio=entry.is_production_lesson and not disable_voiceover,
                video_path=entry.rendered_video(quality),
                subtitle_path=entry.rendered_subtitle(quality),
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
            quality=quality if entry.is_production_lesson else None,
            require_subtitle=entry.is_production_lesson and not disable_voiceover,
            require_audio=entry.is_production_lesson and not disable_voiceover,
            video_path=entry.rendered_video(quality),
            subtitle_path=entry.rendered_subtitle(quality),
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
            relative_dir = entry.package_relative_dir
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
    lines = [f"# {title}", ""]
    if entries[0].track == "programme":
        lines.extend(
            [
                f"Les {len(entries)} vidéos suivent la numérotation globale du cours.",
                "",
            ]
        )
        active_module = None
        for entry in entries:
            if entry.module != active_module:
                active_module = entry.module
                lines.extend([f"## {active_module}", ""])
            lines.append(f"{entry.order:02d}. **{entry.title}** — {entry.coverage}")
        lines.append("")
    else:
        lines.extend(
            [
                "Six capsules indépendantes consacrées aux erreurs mathématiques fréquentes.",
                "",
            ]
        )
        for entry in entries:
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


def archive_mp4_tree(root: Path) -> None:
    """Register every MP4 below root before or after an atomic package replacement."""
    if not root.is_dir():
        return
    try:
        root.resolve().relative_to((PROJECT_ROOT / "dist").resolve())
    except ValueError:
        return
    for video in sorted(root.rglob("*.mp4")):
        subprocess.run(
            [sys.executable, str(ARCHIVE_SCRIPT), "register", str(video)],
            cwd=PROJECT_ROOT,
            check=True,
        )


def package_entries(
    manifest: dict[str, Any],
    entries: list[Entry],
    *,
    package_root: Path,
) -> None:
    tracks = {entry.track for entry in entries}
    if len(tracks) != 1:
        raise ValueError("Each local package must contain exactly one track")
    track = next(iter(tracks))
    canonical_ids = {e["lesson_id"] for e in manifest["entries"] if e["track"] == track}
    if {e.lesson_id for e in entries} != canonical_ids:
        raise ValueError("Package selection does not match the canonical track")
    expected_count = manifest["expected_counts"][track]
    if len(entries) != expected_count:
        raise ValueError(
            f"A packaged {track} collection must contain exactly {expected_count} entries"
        )

    failures: list[str] = []
    for entry in entries:
        errors = validate_media(
            entry,
            quality="qh" if entry.is_production_lesson else None,
            require_subtitle=entry.is_production_lesson,
            # Requirements are explicit, never inferred from the display number.
            require_audio=entry.is_production_lesson,
        )
        if errors:
            failures.append(f"{entry.delivery_name}: {'; '.join(errors)}")
    if failures:
        joined = "\n  - ".join(failures)
        raise RuntimeError(f"Cannot package invalid media:\n  - {joined}")

    package_root.parent.mkdir(parents=True, exist_ok=True)
    archive_mp4_tree(package_root)
    with tempfile.TemporaryDirectory(
        prefix=f".{package_root.name}-",
        dir=package_root.parent,
    ) as temporary:
        staging = Path(temporary) / package_root.name
        staging.mkdir()
        for entry in entries:
            destination = staging / entry.package_relative_dir
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry.source_video, destination / f"{entry.delivery_name}.mp4")
            if entry.source_subtitle.is_file():
                shutil.copy2(entry.source_subtitle, destination / f"{entry.delivery_name}.srt")

        if track == "programme":
            coverage = PROJECT_ROOT / "curriculum" / "couverture_programme.md"
            shutil.copy2(coverage, staging / coverage.name)
        write_playlist_csv(staging, entries)
        collection_title = (
            manifest["title"] if track == "programme" else manifest["errors_title"]
        )
        write_collection_index(staging, collection_title, entries)
        write_checksums(staging)

        previous = package_root.with_name(f".{package_root.name}.previous")
        if previous.exists():
            shutil.rmtree(previous)
        if package_root.exists():
            package_root.rename(previous)
        staging.rename(package_root)
        if previous.exists():
            shutil.rmtree(previous)

    archive_mp4_tree(package_root)
    print(f"Package: {package_root}")


def mirror_mp4_collection(package_root: Path, drive_root: Path) -> None:
    if not package_root.is_dir():
        raise FileNotFoundError(f"Package does not exist: {package_root}")
    drive_root.parent.mkdir(parents=True, exist_ok=True)
    videos = sorted(package_root.rglob("*.mp4"))
    if not videos:
        raise ValueError(f"Package has no MP4 files: {package_root}")

    with tempfile.TemporaryDirectory(
        prefix=f".{drive_root.name}-",
        dir=drive_root.parent,
    ) as temporary:
        staging = Path(temporary) / drive_root.name
        staging.mkdir()
        for video in videos:
            relative = video.relative_to(package_root)
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(video, destination)

        previous = drive_root.with_name(f".{drive_root.name}.previous")
        if previous.exists():
            shutil.rmtree(previous)
        if drive_root.exists():
            drive_root.rename(previous)
        staging.rename(drive_root)
        if previous.exists():
            shutil.rmtree(previous)

    # Google Drive/Finder can restore legacy custom-icon metadata while a
    # replaced folder is synchronizing. Keep managed collections MP4-only.
    for path in drive_root.rglob("*"):
        if path.is_file() and path.suffix.lower() != ".mp4":
            path.unlink()
    print(f"Drive MP4 mirror: {drive_root} ({len(videos)} videos)")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--track",
        choices=("programme", "errors", "all"),
        default="programme",
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
    parser.add_argument("--errors-package-root", type=Path)
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
                quality=args.quality if entry.is_production_lesson else None,
                require_subtitle=entry.is_production_lesson and not args.disable_voiceover,
                require_audio=entry.is_production_lesson and not args.disable_voiceover,
                video_path=entry.rendered_video(args.quality),
                subtitle_path=entry.rendered_subtitle(args.quality),
            )
            if errors:
                failures.append(f"{entry.delivery_name}: {'; '.join(errors)}")
        if failures:
            raise RuntimeError("Validation failures:\n  - " + "\n  - ".join(failures))
        print(f"Validated {len(entries)} curriculum entries")

    package_roots = {
        "programme": (
            args.package_root or (PROJECT_ROOT / manifest["package_root"])
        ).resolve(),
        "errors": (
            args.errors_package_root
            or (PROJECT_ROOT / manifest["errors_package_root"])
        ).resolve(),
    }
    if args.package or args.drive:
        for track in ("programme", "errors"):
            track_entries = [entry for entry in entries if entry.track == track]
            if track_entries:
                package_entries(
                    manifest,
                    track_entries,
                    package_root=package_roots[track],
                )
    if args.drive:
        drive_base = (
            args.drive_root or Path(manifest["drive_root"])
        ).expanduser().resolve()
        destinations = {
            "programme": drive_base / "1 - Programme principal",
            "errors": drive_base / "2 - Erreurs fréquentes",
        }
        for track in ("programme", "errors"):
            if any(entry.track == track for entry in entries):
                mirror_mp4_collection(package_roots[track], destinations[track])

    if not any(
        (args.list, args.render, args.validate, args.package, args.drive)
    ):
        print("Manifest is valid. Use --list, --render, --validate, --package, or --drive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

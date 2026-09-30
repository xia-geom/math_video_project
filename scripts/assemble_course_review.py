#!/usr/bin/env python3
"""Assemble a non-release 43-lesson review collection from verified local media."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.course_catalog import delivery_name, load_catalog  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    result = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]
    )
    data = json.loads(result)
    if len([s for s in data["streams"] if s["codec_type"] == "video"]) != 1:
        raise ValueError(f"Expected one video stream: {path}")
    if float(data["format"]["duration"]) <= 0:
        raise ValueError(f"Invalid duration: {path}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, required=True, help="Fresh ten-lesson recheck directory")
    parser.add_argument("--output", type=Path, required=True, help="New collection directory")
    args = parser.parse_args()
    review, output = args.review.resolve(), args.output.resolve()
    if output.exists():
        parser.error(f"Output already exists: {output}")
    catalog, entries = load_catalog()
    migration = json.loads((ROOT / "curriculum/numbering_migration.json").read_text())
    old_by_id = {e["lesson_id"]: e for e in migration["entries"]}
    review_status = json.loads((review / "STATUS.json").read_text())
    source_commit = review_status.get("source_commit", "")
    if not source_commit or subprocess.run(
        ["git", "merge-base", "--is-ancestor", source_commit, "HEAD"], cwd=ROOT,
        check=False,
    ).returncode:
        raise ValueError("Review source commit is not in the checked-out course history")
    passed = {v["lesson_id"]: v for v in review_status.get("videos", []) if v["render"] == "passed"}
    if len(passed) != 10:
        raise ValueError("Expected ten passed fresh renders")

    prepared = []
    for entry in entries:
        name = delivery_name(entry)
        if entry["legacy_id"].startswith("S"):
            status = passed.get(entry["lesson_id"])
            if status is None or status["source_sha256"] != sha256(ROOT / entry["scene_file"]):
                raise ValueError(f"Missing or stale new render: {name}")
            source = review / name / f"{name}_silent_review.mp4"
            suffix, provenance = "silent_preview", "fresh_current_source"
            if status.get("video_sha256") != sha256(source):
                raise ValueError(f"Review MP4 hash mismatch: {source}")
        else:
            old = old_by_id[entry["lesson_id"]]
            slug = old["old_artifact_slug"]
            source = ROOT / "dist" / slug / f"{slug}.mp4"
            suffix, provenance = "legacy_render", "historical_local_media"
        if not source.is_file():
            raise FileNotFoundError(source)
        media = probe(source)
        audio = any(s["codec_type"] == "audio" for s in media["streams"])
        if provenance == "fresh_current_source" and audio:
            raise ValueError(f"Silent preview unexpectedly has audio: {source}")
        prepared.append((entry, source, suffix, provenance, media, audio))

    staging = output.with_name(output.name + ".pending")
    if staging.exists():
        parser.error(f"Staging directory already exists: {staging}")
    staging.mkdir(parents=True)
    rows = []
    try:
        for entry, source, suffix, provenance, media, audio in prepared:
            folder = staging / entry["module"] if entry["track"] == "programme" else staging / "10 - Erreurs fréquentes"
            folder.mkdir(parents=True, exist_ok=True)
            destination = folder / f"{delivery_name(entry)}__{suffix}.mp4"
            try:
                os.link(source, destination)
            except OSError:
                shutil.copy2(source, destination)
            rows.append({
                "order": entry["order"], "module": entry["module"], "title": entry["title"],
                "lesson_id": entry["lesson_id"], "legacy_id": entry["legacy_id"],
                "path": destination.relative_to(staging).as_posix(),
                "source": str(source), "provenance": provenance,
                "audio": audio, "duration_seconds": media["format"]["duration"],
                "sha256": sha256(destination), "release_ready": False,
            })
        with (staging / "playlist.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        (staging / "playlist.m3u").write_text(
            "#EXTM3U\n" + "".join(row["path"] + "\n" for row in rows), encoding="utf-8"
        )
        (staging / "STATUS.json").write_text(json.dumps({
            "source_commit": review_status["source_commit"],
            "catalog_version": catalog["version"], "video_count": len(rows),
            "new_silent_previews": 10, "existing_legacy_renders": 33,
            "narration_review": "pending", "visual_review": "pending",
            "release_ready": False, "videos": rows,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        staging.rename(output)
    except BaseException:
        shutil.rmtree(staging)
        raise
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

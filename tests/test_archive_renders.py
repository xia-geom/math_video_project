from __future__ import annotations

import importlib.util
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "archive_renders.py"
SPEC = importlib.util.spec_from_file_location("archive_renders", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
archive_renders = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = archive_renders
SPEC.loader.exec_module(archive_renders)


def fake_media() -> dict[str, object]:
    return {
        "duration_seconds": 12.5,
        "width": 1920,
        "height": 1080,
        "frame_rate": 60.0,
        "has_audio": True,
    }


def configure_fake_provenance(monkeypatch) -> None:
    monkeypatch.setattr(archive_renders, "probe_media", lambda _path: fake_media())
    monkeypatch.setattr(archive_renders, "git_state", lambda _root: ("abc123def456", True))


def test_snapshot_deduplicates_content_and_is_idempotent(tmp_path: Path, monkeypatch) -> None:
    configure_fake_provenance(monkeypatch)
    dist = tmp_path / "dist"
    first = dist / "topic" / "topic.mp4"
    duplicate = dist / "package" / "topic.mp4"
    ignored = dist / "_render_archive" / "already.mp4"
    for path in (first, duplicate, ignored):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"same-video")

    assert archive_renders.snapshot(
        dist_root=dist, label="pre-merge", project_root=tmp_path
    ) == (2, 2)
    assert archive_renders.snapshot(
        dist_root=dist, label="pre-merge", project_root=tmp_path
    ) == (2, 0)

    archive = dist / "_render_archive"
    records = archive_renders.read_records(archive / "index.jsonl")
    objects = list((archive / "objects").rglob("*.mp4"))
    versions = list((archive / "versions").rglob("*.mp4"))
    assert len(records) == 2
    assert len(objects) == 1
    assert len(versions) == 2
    assert {record["snapshot_label"] for record in records} == {"pre-merge"}
    assert all(record["observed_at_commit"] == "abc123def456" for record in records)


def test_register_records_metadata_and_restores_exact_content(tmp_path: Path, monkeypatch) -> None:
    configure_fake_provenance(monkeypatch)
    dist = tmp_path / "dist"
    video = dist / "lesson" / "lesson.mp4"
    video.parent.mkdir(parents=True)
    video.write_bytes(b"version-one")
    moment = datetime(2026, 9, 17, 14, 5, 6, tzinfo=timezone.utc)

    first, created = archive_renders.register_video(
        video,
        dist_root=dist,
        quality="qh",
        now=moment,
        project_root=tmp_path,
    )
    assert created
    assert first["archive_label"] == (
        "lesson__20260917-140506__git-abc123def456__1920x1080-60fps.mp4"
    )
    assert first["render_quality"] == "qh"
    assert first["git_dirty"] is True
    assert first["duration_seconds"] == 12.5
    assert first["has_audio"] is True

    restored = tmp_path / "restored.mp4"
    archive_renders.restore_version(
        first["version_id"], restored, archive_root=dist / "_render_archive"
    )
    assert restored.read_bytes() == b"version-one"
    assert archive_renders.sha256_file(restored) == first["sha256"]

    video.write_bytes(b"version-two")
    second, second_created = archive_renders.register_video(
        video,
        dist_root=dist,
        quality="qh",
        now=moment,
        project_root=tmp_path,
    )
    assert second_created
    assert second["version_id"] != first["version_id"]
    assert len(archive_renders.read_records(dist / "_render_archive" / "index.jsonl")) == 2


def test_render_output_routing_separates_previews_from_production() -> None:
    helper = ROOT / "scripts" / "render_outputs.sh"
    command = (
        'source "$1"; resolve_render_dist_dir "$2" "$3" "$4"; '
        'resolve_render_output_stem "$3" "$4"'
    )

    qh = subprocess.run(
        ["bash", "-c", command, "bash", str(helper), "/project", "topic", "qh"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    ql = subprocess.run(
        ["bash", "-c", command, "bash", str(helper), "/project", "topic", "ql"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    assert qh == ["/project/dist/topic", "topic"]
    assert ql == ["/project/dist/_previews/ql/topic", "topic__ql"]

"""Recording identity and media checks for local music-review mixes."""

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/mix_uqam_music_review.py"
SPEC = importlib.util.spec_from_file_location("uqam_music_review", SCRIPT)
MIX = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIX)


def metadata(path):
    return {
        "schema_version": 1, "title": "Synthetic test music", "creator": "Test author",
        "source_url": "https://example.org/track", "license_name": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "download_url": "https://example.org/track.wav", "sha256": MIX.file_hash(path),
        "license_checked": "2026-10-03",
    }


def test_recording_must_match_attribution_sidecar(tmp_path):
    music = tmp_path / "music.wav"
    music.write_bytes(b"reviewed recording")
    sidecar = tmp_path / "music.json"
    sidecar.write_text(json.dumps(metadata(music)))
    music.write_bytes(b"a different recording")
    with pytest.raises(ValueError, match="SHA-256"):
        MIX.music_metadata(music, sidecar)


def test_new_recording_does_not_inherit_legacy_offset(tmp_path):
    music = tmp_path / "music.wav"
    music.write_bytes(b"reviewed recording")
    sidecar = tmp_path / "music.json"
    sidecar.write_text(json.dumps(metadata(music)))
    assert MIX.music_metadata(music, sidecar).get("default_offset_seconds", 0.0) == 0.0
    with patch.object(MIX, "file_hash", return_value=MIX.REVIEWED_MUSIC_SHA256):
        legacy = MIX.music_metadata(music)
    assert legacy["title"] == "Resolutions"
    assert legacy["default_offset_seconds"] == 0.85


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
                    reason="FFmpeg and ffprobe are required for the media integration check")
def test_real_mix_keeps_video_and_records_selected_track(tmp_path):
    source, music, output = (tmp_path / name for name in ("source.mp4", "music.wav", "mix.mp4"))
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "color=c=navy:s=96x54:r=10:d=3", "-f", "lavfi", "-i",
                    "sine=frequency=700:sample_rate=48000:duration=3",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-shortest", str(source)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "sine=frequency=220:sample_rate=48000:duration=5", str(music)], check=True)
    sidecar = music.with_suffix(".json")
    track = metadata(music)
    track["default_offset_seconds"] = 0.2
    sidecar.write_text(json.dumps(track))
    subprocess.run([sys.executable, str(SCRIPT), "--video", str(source), "--music", str(music),
                    "--music-manifest", str(sidecar), "--output", str(output)],
                   check=True, capture_output=True, text=True)
    manifest = json.loads(output.with_suffix(".manifest.json").read_text())
    assert manifest["music_title"] == track["title"]
    assert manifest["music_sha256"] == MIX.file_hash(music)
    assert manifest["music_metadata_sha256"] == MIX.file_hash(sidecar)
    assert manifest["music_offset_seconds"] == 0.2
    assert manifest["video_packets_unchanged"]
    assert manifest["duration_seconds"] == pytest.approx(3, abs=0.05)
    assert float(manifest["output_loudness"]["input_tp"]) <= -1
    credit = MIX.probe(output)["format"]["tags"]["comment"]
    assert track["title"] in credit and track["creator"] in credit
    assert "Resolutions" not in credit
    assert track["license_url"] in output.with_suffix(".credits.txt").read_text()
    assert MIX.video_hash(source) == MIX.video_hash(output)

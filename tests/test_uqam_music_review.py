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


def test_source_audio_end_allows_codec_padding_but_counts_start_offset():
    video = {"duration": "3", "start_time": "0"}
    result = MIX.validate_audio_end(video, {"duration": "3.021333", "start_time": "0"})
    assert result["audio_end_tolerance_seconds"] == 0.05
    with pytest.raises(ValueError, match="cut the soundtrack"):
        MIX.validate_audio_end(video, {"duration": "3", "start_time": "0.2"})
    with pytest.raises(ValueError, match="measured stream durations"):
        MIX.validate_audio_end(video, {})


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
                    reason="FFmpeg and ffprobe are required for the media integration check")
def test_mix_rejects_a_source_whose_soundtrack_would_be_cut(tmp_path):
    source, music, output = (tmp_path / name for name in ("source.mp4", "music.wav", "mix.mp4"))
    MIX.run("ffmpeg", "-v", "error", "-f", "lavfi", "-i",
            "color=c=navy:s=160x90:r=30:d=0.6", "-f", "lavfi", "-i",
            "sine=frequency=700:sample_rate=48000:duration=1.2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(source))
    MIX.run("ffmpeg", "-v", "error", "-f", "lavfi", "-i",
            "sine=frequency=220:sample_rate=48000:duration=4", str(music))
    sidecar = music.with_suffix(".json")
    sidecar.write_text(json.dumps(metadata(music)))
    with patch.object(sys, "argv", [str(SCRIPT), "--video", str(source), "--music", str(music),
                                   "--music-manifest", str(sidecar), "--output", str(output)]):
        with pytest.raises(ValueError, match="cut the soundtrack"):
            MIX.main()
    assert not output.exists()
    assert not output.with_suffix(".music-bed.wav").exists()


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
                    reason="FFmpeg and ffprobe are required for the media integration check")
@pytest.mark.parametrize("credits_mode", ["stem", "fallback", "both"])
def test_real_mix_keeps_video_and_records_selected_track(tmp_path, credits_mode):
    source, music, output = (tmp_path / name for name in ("source.mp4", "music.wav", "mix.mp4"))
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "color=c=navy:s=96x54:r=10:d=3", "-f", "lavfi", "-i",
                    "sine=frequency=700:sample_rate=48000:duration=3",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-metadata", "comment=Photo : Synthetic source photographer",
                    "-shortest", str(source)], check=True)
    stem_credits = source.with_suffix(".credits.txt")
    shared_credits = source.parent / "CREDITS.txt"
    if credits_mode in {"stem", "both"}:
        stem_credits.write_text("Image context: synthetic test footage.\n")
    if credits_mode in {"fallback", "both"}:
        shared_credits.write_text("Shared synthetic film credits.\n")
    source_credits = shared_credits if credits_mode == "fallback" else stem_credits
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
    assert "Photo : Synthetic source photographer" in credit
    assert source_credits.read_text().strip() in credit
    assert manifest["source_comment_preserved"] is True
    assert manifest["source_credits_file"] == str(source_credits)
    assert manifest["source_credits_sha256"] == MIX.file_hash(source_credits)
    assert "Resolutions" not in credit
    output_credits = output.with_suffix(".credits.txt").read_text()
    assert track["license_url"] in output_credits
    assert "Photo : Synthetic source photographer" in output_credits
    assert source_credits.read_text().strip() in output_credits
    if credits_mode == "both":
        assert shared_credits.read_text().strip() not in credit
        assert shared_credits.read_text().strip() not in output_credits
    assert MIX.video_hash(source) == MIX.video_hash(output)

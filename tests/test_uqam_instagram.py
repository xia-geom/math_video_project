"""Caption readability and timing preservation for portrait delivery."""

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/package_uqam_instagram.py"
SPEC = importlib.util.spec_from_file_location("uqam_instagram", SCRIPT)
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


def test_long_cue_preserves_words_and_measured_outer_bounds():
    original = [{"start": 4.133, "end": 10.829,
                 "text": "Commencez par une majeure en mathématiques ou en statistique, "
                         "généralement en deux ans à temps plein."}]
    cues = PACKAGE.portrait_cues(original)
    assert len(cues) > 1
    assert cues[0]["start"] == original[0]["start"]
    assert cues[-1]["end"] == original[0]["end"]
    assert " ".join(cue["text"] for cue in cues) == original[0]["text"]
    face = PACKAGE.font(PACKAGE.CAPTION_SIZE, 700)
    for cue in cues:
        lines = PACKAGE.wrap_two_lines(cue["text"], face, PACKAGE.CAPTION_WIDTH)
        assert len(lines) <= 2
        assert max(face.getlength(line) for line in lines) <= PACKAGE.CAPTION_WIDTH
        assert cue["timing_estimated_within_source_cue"]
    for left, right in zip(cues, cues[1:]):
        assert left["end"] == right["start"]


def test_short_cues_keep_real_pauses_and_times():
    original = [{"start": 0, "end": 2, "text": "Les maths à l’UQAM."},
                {"start": 2.2, "end": 4, "text": "Plusieurs horizons."}]
    cues = PACKAGE.portrait_cues(original)
    assert [(cue["start"], cue["end"], cue["text"]) for cue in cues] == [
        (cue["start"], cue["end"], cue["text"]) for cue in original]
    assert not any(cue["timing_estimated_within_source_cue"] for cue in cues)


def test_caption_split_avoids_a_one_word_flash():
    cues = PACKAGE.portrait_cues([{"start": 18.550, "end": 22.366,
        "text": "Ce parcours peut mener à un baccalauréat en sciences par cumul."}])
    assert len(cues) == 2
    assert min(len(cue["text"].split()) for cue in cues) >= 4
    assert min(cue["end"] - cue["start"] for cue in cues) >= 1


def test_invalid_or_overlapping_timing_is_rejected(tmp_path):
    srt = tmp_path / "bad.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:02,000\nFirst\n\n"
                   "2\n00:00:01,000 --> 00:00:03,000\nSecond\n")
    with pytest.raises(ValueError, match="non-overlapping"):
        PACKAGE.read_cues(srt, 3)


@pytest.mark.parametrize("selection", [[], ["--subtitles", "input.srt", "--no-captions"]])
def test_cli_requires_exactly_one_caption_mode(selection):
    with pytest.raises(SystemExit) as error:
        PACKAGE.main(["--video", "input.mp4", "--title", "Mathématiques",
                      "--output", "output.mp4", *selection])
    assert error.value.code == 2


@pytest.mark.skipif(not all(shutil.which(tool) for tool in ("ffmpeg", "ffprobe")),
                    reason="FFmpeg and ffprobe are required for the packaging smoke test")
@pytest.mark.parametrize("captions_enabled", [False, True])
def test_portrait_export_caption_modes(tmp_path, captions_enabled):
    source = tmp_path / "landscape.mp4"
    PACKAGE.run("ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "color=c=blue:s=160x90:r=30:d=0.6", "-f", "lavfi", "-i",
                "sine=frequency=440:sample_rate=48000:duration=0.6",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                "-shortest", str(source))
    source.with_suffix(".credits.txt").write_text("Synthetic test footage.\n")
    output = tmp_path / "portrait.mp4"
    selection = ["--no-captions"]
    if captions_enabled:
        srt = tmp_path / "input.srt"
        srt.write_text("1\n00:00:00,000 --> 00:00:00,600\nParoles.\n")
        selection = ["--subtitles", str(srt)]
    PACKAGE.main(["--video", str(source), "--title", "Mathématiques à l’UQAM",
                  "--output", str(output), *selection])

    manifest = json.loads(output.with_suffix(".manifest.json").read_text())
    assert manifest["captions_enabled"] is captions_enabled
    assert manifest["video"]["width"] == 1080
    assert manifest["video"]["height"] == 1920
    assert manifest["video"]["r_frame_rate"] == "30/1"
    assert manifest["audio"]["codec_name"] == "aac"
    assert manifest["audio"]["sample_rate"] == "48000"
    assert manifest["duration_seconds"] == pytest.approx(0.6, abs=0.05)
    assert manifest["full_decode"] == "passed"
    assert manifest["speech_speed_changed"] is False
    assert output.with_suffix(".credits.txt").read_text() == "Synthetic test footage.\n"
    assert output.with_suffix(".ass").exists() is captions_enabled
    assert output.with_suffix(".portrait.srt").exists() is captions_enabled
    if captions_enabled:
        assert manifest["input_srt"] == str(srt)
        assert manifest["input_srt_sha256"] == PACKAGE.sha256(srt)
        assert manifest["caption_word_sequence_preserved"] is True
        assert manifest["caption_max_lines"] == 1
        assert manifest["cues"][0]["text"] == "Paroles."
    else:
        assert manifest["cues"] == manifest["original_cues"] == []
        assert manifest["caption_max_lines"] == 0
        for field in ("input_srt", "input_srt_sha256", "portrait_srt", "caption_area",
                      "caption_font_size", "caption_word_sequence_preserved",
                      "caption_timing_method", "caption_word_timing_estimated",
                      "caption_word_timing_forced_aligned", "caption_timing_precision_seconds"):
            assert manifest[field] is None

    # Inspect encoded pixels: narration captions disappear, titles and CTA remain.
    frame = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", "0.2", "-i", str(output), "-frames:v", "1",
         "-pix_fmt", "gray", "-f", "rawvideo", "-"], check=True, capture_output=True)
    image = Image.frombytes("L", (1080, 1920), frame.stdout)
    caption_min = image.crop((100, 1135, 980, 1415)).getextrema()[0]
    assert (caption_min < 150) if captions_enabled else (caption_min > 235)
    assert image.crop((100, 210, 980, 330)).getextrema()[0] < 100
    assert image.crop((100, 1510, 980, 1640)).getextrema()[0] < 100

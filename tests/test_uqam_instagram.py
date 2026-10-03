"""Caption readability and timing preservation for portrait delivery."""

import importlib.util
from pathlib import Path

import pytest


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

"""Safeguards for the photo variant without cloud speech or a full video render."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "miscellaneous/bac_math_uqam_fr/build_full_photo.py"
spec = importlib.util.spec_from_file_location("uqam_full_photo", BUILDER)
assert spec is not None and spec.loader is not None
full_photo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(full_photo)


@pytest.fixture
def source_fixture(tmp_path, monkeypatch):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source whose identity is pinned for this test")
    monkeypatch.setattr(full_photo, "SOURCE_SHA256", full_photo.sha256(source))
    info = {"streams": [{"codec_type": "audio", "codec_name": "aac"}],
            "format": {"duration": str(full_photo.DURATION)}}
    monkeypatch.setattr(full_photo, "probe", lambda path: info)
    return source, info


def test_source_validation_accepts_pinned_aac_export(source_fixture):
    source, info = source_fixture
    assert full_photo.validate_source(source) is info


def test_source_validation_rejects_replaced_export_before_probing(source_fixture, monkeypatch):
    source, _ = source_fixture
    source.write_bytes(b"different cut or soundtrack")

    def unexpected_probe(path):
        pytest.fail("An unrecognized source should be rejected before media processing")

    monkeypatch.setattr(full_photo, "probe", unexpected_probe)
    with pytest.raises(ValueError, match="verified October 22"):
        full_photo.validate_source(source)


@pytest.mark.parametrize("audio_streams", [
    [],
    [{"codec_type": "audio", "codec_name": "mp3"}],
    [{"codec_type": "audio", "codec_name": "aac"}] * 2,
])
def test_source_validation_rejects_missing_wrong_or_ambiguous_audio(source_fixture, audio_streams):
    source, info = source_fixture
    info["streams"] = [{"codec_type": "video", "codec_name": "h264"}, *audio_streams]
    with pytest.raises(ValueError, match="Exactly one existing AAC"):
        full_photo.validate_source(source)


@pytest.mark.parametrize("delta", [-1.0, 1.0])
def test_source_validation_rejects_duration_change(source_fixture, delta):
    source, info = source_fixture
    info["format"]["duration"] = str(full_photo.DURATION + delta)
    with pytest.raises(ValueError, match="different duration"):
        full_photo.validate_source(source)


def test_editorial_states_cover_the_soundtrack_at_frame_precision():
    anchors = full_photo.frame_anchors()
    assert anchors[0] == 0
    assert anchors[-1] / full_photo.FPS == pytest.approx(66.083333, abs=0.000001)
    assert sum(end - start for start, end in zip(anchors, anchors[1:])) == anchors[-1]
    for state, frame in zip(full_photo.STATES, anchors):
        assert abs(frame / full_photo.FPS - state["start"]) <= 0.5 / full_photo.FPS
    research = [state for state in full_photo.STATES
                if state["id"] in {"research_intro", "cirget", "lacim", "statqam"}]
    assert len({state["photo"] for state in research}) == 1
    by_id = {state["id"]: state for state in full_photo.STATES}
    # These are the measured October 22 replacement/CTA boundaries, not the
    # slightly earlier endpoints in the October 4 Manim semantic timeline.
    assert by_id["summary_4"]["start"] == pytest.approx(2707168 / 48000, abs=0.000001)
    assert by_id["call_to_action"]["start"] == pytest.approx(2780752 / 48000, abs=0.000001)


@pytest.mark.parametrize("starts", [
    [1.0, 2.0],        # Uncovered opening.
    [0.0, 5.0, 4.0],  # Backward edit.
    [0.0, 5.0, 5.0],  # Two states sharing a frame.
    [0.0, 67.0],      # State past the preserved soundtrack.
    [0.0, 0.1],       # Transition longer than the shot.
])
def test_invalid_state_timing_is_rejected(starts):
    with pytest.raises(ValueError):
        full_photo.frame_anchors([{"start": start} for start in starts])


@pytest.mark.parametrize("state", full_photo.STATES, ids=lambda state: state["id"])
def test_actual_french_copy_fits_safe_frame_with_nonoverlapping_rendered_glyphs(state):
    layer, boxes = full_photo.copy_layer(state)
    ink = layer.getchannel("A").getbbox()
    assert ink is not None
    assert ink[0] >= 70 and ink[1] >= 54
    assert ink[2] <= 1850 and ink[3] <= 1026
    for index, box in enumerate(boxes):
        assert box[2] > box[0] and box[3] > box[1]
        for other in boxes[index + 1:]:
            assert (box[2] <= other[0] or other[2] <= box[0]
                    or box[3] <= other[1] or other[3] <= box[1])


@pytest.mark.parametrize("lines, message", [
    ([full_photo.line("A heading that cannot fit " * 8, 100)], "safe frame"),
    ([full_photo.line("Outside bottom", 1040)], "safe frame"),
    ([full_photo.line("First heading", 100), full_photo.line("Second heading", 100)], "overlaps"),
])
def test_invalid_typography_is_rejected(lines, message):
    with pytest.raises(ValueError, match=message):
        full_photo.copy_layer({"id": "invalid", "lines": copy.deepcopy(lines)})


def test_output_verification_rejects_changed_soundtrack(monkeypatch):
    monkeypatch.setattr(full_photo, "probe", lambda path: {
        "streams": [{"codec_type": "video", "width": 1920, "height": 1080,
                     "nb_frames": str(full_photo.FRAME_COUNT)}],
        "format": {"duration": str(full_photo.DURATION)},
    })
    monkeypatch.setattr(full_photo, "run", lambda *args: "")
    monkeypatch.setattr(full_photo, "audio_digest", lambda path: str(path))
    with pytest.raises(ValueError, match="copied soundtrack changed"):
        full_photo.verify(Path("original.mp4"), Path("changed.mp4"))

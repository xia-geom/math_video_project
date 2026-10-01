"""Contracts for the complete, thirty-second-maximum degree-pathway capsule."""

import json
from pathlib import Path

import pytest

from miscellaneous.bac_sciences_ouvertures_fr.build import validate_media, validate_timeline
from miscellaneous.bac_sciences_ouvertures_fr.project import (
    HERE,
    allocate_slots,
    load_project,
    srt_time,
    validate_assets,
    validate_project,
    write_srt,
)

ROOT = Path(__file__).resolve().parents[1]


def test_complete_pathway_is_twenty_nine_seconds():
    spec = load_project()
    assert spec["schema_version"] == 4
    assert sum(b["seconds"] for b in spec["beats"]) == 29
    assert spec["accepted_duration_seconds"] == [28, 30]
    assert spec["source"]["claim_pages"] == [21, 22, 23]
    assert len(spec["source"]["sha256"]) == 64
    narration = " ".join(b["text"].casefold() for b in spec["beats"])
    for word in ("majeure", "certificat", "mineure", "compatible", "baccalauréat en sciences"):
        assert word in narration
    for word in ("garanti", "emploi", "maîtrise"):
        assert word not in narration
    assert spec["music"] is None and spec["official_logo"] is False


def test_actual_photos_are_decoded_and_low_resolution_stays_in_panel():
    spec = load_project()
    paths = validate_assets(spec)
    assert set(paths) == {"campus", "math_activity", "student_life"}
    assert paths["math_activity"].name == "math_workshop_2019.jpg"
    assert spec["assets"]["math_activity"]["placement"] == "panel"
    assert spec["assets"]["math_activity"]["width"] == 1000
    assert spec["beats"][2]["background"] is None
    assert spec["beats"][3]["keep_background"] is True
    assert all(p.name not in {"research_math.jpg", "classroom_math.jpg"} for p in paths.values())


def test_sparse_copy_and_four_fields():
    spec = load_project()
    assert max(len(b["screen"]) for b in spec["beats"]) <= 3
    assert set(spec["fields"]) == {"Communication", "Finance", "Économie", "Informatique"}
    assert "bâtir votre avenir" in spec["beats"][-1]["text"]


@pytest.mark.parametrize("bad", [-1, 0, float("nan"), float("inf")])
def test_invalid_durations_rejected(bad):
    spec = load_project()
    spec["beats"][0]["seconds"] = bad
    with pytest.raises(ValueError):
        validate_project(spec)


@pytest.mark.parametrize("field,value", [
    ("caption", "A different message"), ("background", "unregistered"), ("screen", ["A", "B", "C", "D"]),
])
def test_invalid_beat_contract_rejected(field, value):
    spec = load_project()
    spec["beats"][0][field] = value
    with pytest.raises(ValueError):
        validate_project(spec)


def test_declared_dimensions_cannot_fake_high_resolution():
    spec = load_project()
    spec["assets"]["math_activity"]["width"] = 4000
    with pytest.raises(ValueError, match="decoded"):
        validate_assets(spec)
    spec = load_project()
    spec["assets"]["math_activity"]["placement"] = "full_bleed"
    with pytest.raises(ValueError, match="full-screen"):
        validate_assets(spec)


def test_invalid_background_reuse_rejected():
    spec = load_project()
    spec["beats"][1]["keep_background"] = True
    with pytest.raises(ValueError, match="identical"):
        validate_project(spec)


@pytest.mark.parametrize("fps", [15, 30, 60])
def test_actual_speech_allocator_is_frame_exact_and_preserves_final_hold(fps):
    spec = load_project()
    speech = [1.8, 6.1, 7.1, 3.0, 5.6]
    slots = allocate_slots(spec, speech, fps)
    assert 29 <= sum(slots) <= 30
    assert all(s * fps == pytest.approx(round(s * fps)) for s in slots)
    assert all(slot >= seconds + 0.12 - 1e-8 for slot, seconds in zip(slots, speech))
    assert slots[-1] >= speech[-1] + 2


@pytest.mark.parametrize("speech", [[3, 8, 9, 4, 8], [1, 2, 3, 4, float("nan")], [1, 2]])
def test_speech_overrun_or_bad_measurements_never_cut(speech):
    with pytest.raises(ValueError):
        allocate_slots(load_project(), speech, 60)


def fixture_timeline():
    spec = load_project()
    timeline = {"mode": "silent", "voice": None, "duration": 29, "beats": []}
    start = 0.0
    for beat in spec["beats"]:
        end = start + beat["seconds"]
        timeline["beats"].append({
            "id": beat["id"], "start": start, "end": end,
            "caption_end": end - (2 if beat["id"] == "horizons" else 0),
            "caption": beat["caption"], "speech_seconds": None,
        })
        start = end
    return timeline


def test_srt_uses_timeline_and_keeps_final_reading_hold(tmp_path):
    timeline = fixture_timeline()
    target = tmp_path / "captions.srt"
    write_srt(timeline["beats"], target)
    srt = target.read_text()
    assert srt.count(" --> ") == 5
    assert "00:00:27,000" in srt
    assert "<prosody" not in srt
    assert srt_time(59.9996) == "00:01:00,000"
    assert validate_timeline(timeline, load_project(), 29, "silent")["final_reading_hold_seconds"] == 2


def test_music_or_synthetic_clock_cannot_be_passed_off_as_azure():
    timeline = fixture_timeline()
    timeline["mode"] = "azure"
    with pytest.raises(ValueError, match="measured speech"):
        validate_timeline(timeline, load_project(), 29, "azure")


def test_final_hold_is_verified_not_just_declared():
    timeline = fixture_timeline()
    timeline["beats"][-1]["caption_end"] = 29
    with pytest.raises(ValueError, match="reading hold"):
        validate_timeline(timeline, load_project(), 29, "silent")


def test_overlapping_subtitles_rejected(tmp_path):
    with pytest.raises(ValueError):
        write_srt([{"start": 0, "end": 4, "caption": "A"}, {"start": 3, "end": 5, "caption": "B"}], tmp_path / "bad.srt")


def media(mode="silent", duration=29):
    streams = [{"codec_type": "video", "width": 1920, "height": 1080}]
    if mode == "azure":
        streams.append({"codec_type": "audio"})
    return {"format": {"duration": str(duration)}, "streams": streams}


def test_silent_and_narrated_stream_contracts():
    spec = load_project()
    assert validate_media(media(), spec, "silent") == 29
    assert validate_media(media("azure", 29.5), spec, "azure") == 29.5
    with pytest.raises(ValueError):
        validate_media(media(), spec, "azure")
    with pytest.raises(ValueError):
        validate_media(media("azure"), spec, "silent")


@pytest.mark.parametrize("duration", [27.9, 30.01, float("nan")])
def test_encoded_duration_guard_rejects_overrun(duration):
    with pytest.raises(ValueError):
        validate_media(media("azure", duration), load_project(), "azure")


def test_aspect_and_storyboard_drift_rejected():
    info = media()
    info["streams"][0].update(width=1080, height=1920)
    with pytest.raises(ValueError):
        validate_media(info, load_project(), "silent")
    with pytest.raises(ValueError):
        validate_media(media(duration=30), load_project(), "silent")
    info["streams"][0].update(width=854, height=480)
    assert validate_media(info, load_project(), "silent") == 29


def test_parallel_projects_exist_and_paths_are_unique():
    registry = json.loads((ROOT / "miscellaneous/uqam_promotion.json").read_text())
    paths = [p["path"] for p in registry["videos"]]
    assert len(set(paths)) == len(paths) == 3
    for path in paths:
        assert (ROOT / path).is_dir()
    assert (HERE / "sources/accueil_septembre_2026.md").is_file()

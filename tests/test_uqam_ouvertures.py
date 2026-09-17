"""Network-free contracts for the third UQAM promotion video."""
import json
from pathlib import Path

import pytest

from miscellaneous.bac_sciences_ouvertures_fr.build import validate_media
from miscellaneous.bac_sciences_ouvertures_fr.project import (
    HERE,
    load_project,
    srt_time,
    validate_project,
    write_srt,
)

ROOT = Path(__file__).resolve().parents[1]


def test_project_storyboard_is_exactly_twenty_seconds():
    spec = load_project()
    assert sum(b["seconds"] for b in spec["beats"]) == 20
    assert spec["source"]["pdf_pages"] == [21, 22, 23]
    assert len(spec["source"]["sha256"]) == 64


def test_four_fields_follow_supplied_slide_23():
    assert set(load_project()["fields"]) == {"Communication", "Finance", "Économique", "Informatique"}


def test_no_automatic_masters_claim_or_music_or_logo():
    spec = load_project()
    narration = " ".join(b["text"].lower() for b in spec["beats"])
    assert "maîtrise" not in narration and "garanti" not in narration
    assert "majeure" in narration and "certificat" in narration and "par cumul" in narration
    assert spec["music"] is None and spec["official_logo"] is False


@pytest.mark.parametrize("bad", [-1, 0, float("nan"), float("inf")])
def test_invalid_durations_rejected(bad):
    spec = load_project()
    spec["beats"][0]["seconds"] = bad
    with pytest.raises(ValueError):
        validate_project(spec)


def test_caption_mismatch_rejected():
    spec = load_project()
    spec["beats"][0]["caption"] = "A different message"
    with pytest.raises(ValueError):
        validate_project(spec)


def test_srt_generated_from_measured_timeline(tmp_path):
    timeline, start = [], 0.0
    for b in load_project()["beats"]:
        end = start + b["seconds"]
        timeline.append({"start": start, "end": end, "caption": b["caption"]})
        start = end
    target = tmp_path / "captions.srt"
    write_srt(timeline, target)
    srt = target.read_text()
    assert srt.count(" --> ") == 4
    assert "00:00:20,000" in srt
    assert "<prosody" not in srt
    assert srt_time(59.9996) == "00:01:00,000"


def test_overlapping_subtitles_rejected(tmp_path):
    with pytest.raises(ValueError):
        write_srt([{"start": 0, "end": 4, "caption": "A"},
                   {"start": 3, "end": 5, "caption": "B"}], tmp_path / "bad.srt")


def media(mode="silent", duration=20.0):
    streams = [{"codec_type": "video", "width": 1920, "height": 1080}]
    if mode == "azure":
        streams.append({"codec_type": "audio"})
    return {"format": {"duration": str(duration)}, "streams": streams}


def test_silent_and_narrated_stream_contracts():
    spec = load_project()
    assert validate_media(media(), spec, "silent") == 20
    assert validate_media(media("azure", 21.5), spec, "azure") == 21.5
    with pytest.raises(ValueError):
        validate_media(media(), spec, "azure")
    with pytest.raises(ValueError):
        validate_media(media("azure"), spec, "silent")


@pytest.mark.parametrize("duration", [17.9, 22.1])
def test_narration_never_cut_to_hide_duration_overrun(duration):
    with pytest.raises(ValueError):
        validate_media(media("azure", duration), load_project(), "azure")


def test_vertical_crop_and_preview_drift_rejected():
    info = media()
    info["streams"][0].update(width=1080, height=1920)
    with pytest.raises(ValueError):
        validate_media(info, load_project(), "silent")
    with pytest.raises(ValueError):
        validate_media(media(duration=21), load_project(), "silent")


def test_parallel_projects_exist_and_paths_are_unique():
    registry_path = ROOT / "miscellaneous/uqam_promotion.json"
    registry = json.loads(registry_path.read_text())
    assert len(registry["videos"]) == 3
    paths = [p["path"] for p in registry["videos"]]
    assert len(set(paths)) == 3
    for path in paths:
        assert (ROOT / path).is_dir()
    assert (HERE / "sources/accueil_septembre_2026.md").is_file()


def test_manim_480p_pixel_rounding_is_not_a_vertical_crop():
    info = media()
    info["streams"][0].update(width=854, height=480)
    assert validate_media(info, load_project(), "silent") == 20
    info["streams"][0]["width"] = 840
    with pytest.raises(ValueError):
        validate_media(info, load_project(), "silent")

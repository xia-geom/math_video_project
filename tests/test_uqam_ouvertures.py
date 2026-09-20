"""Network-free contracts for the third UQAM promotion video."""
import json
from pathlib import Path

import pytest

from miscellaneous.bac_sciences_ouvertures_fr.build import validate_media
from miscellaneous.bac_sciences_ouvertures_fr.project import (
    HERE,
    load_project,
    srt_time,
    validate_assets,
    validate_project,
    write_srt,
)

ROOT = Path(__file__).resolve().parents[1]


def test_project_storyboard_is_exactly_twenty_seconds():
    spec = load_project()
    assert spec["schema_version"] == 3
    assert sum(b["seconds"] for b in spec["beats"]) == 20
    assert spec["source"]["claim_pages"] == [21, 23]
    assert spec["source"]["context_pages"] == [22]
    assert spec["source"]["resource_pages"] == [7]
    assert len(spec["source"]["sha256"]) == 64


def test_visuals_are_four_distinct_high_resolution_uqam_photos():
    spec = load_project()
    assets = validate_assets(spec)
    assert spec["visual_concept"] == "photo_led_high_resolution"
    assert set(assets) == {"campus", "math_activity", "math_hub", "student_life"}
    assert all(asset["width"] >= 1600 for asset in spec["assets"].values())
    assert all(asset["height"] >= 900 for asset in spec["assets"].values())
    backgrounds = [beat["background"] for beat in spec["beats"]]
    assert len(backgrounds) == len(set(backgrounds)) == 4
    assert all("slide_01_" not in str(path) for path in assets.values())
    assert spec["assets"]["campus"]["path"].endswith("sciences_biologiques_uqam.jpg")
    assert "president_kennedy.jpg" not in spec["assets"]["campus"]["path"]


def test_sparse_screen_copy_replaces_card_grid():
    spec = load_project()
    assert max(len(beat["screen"]) for beat in spec["beats"]) <= 3
    scene = (HERE / "bac_sciences_ouvertures_fr_scene.py").read_text(encoding="utf-8")
    assert "ImageMobject" in scene
    assert "RoundedRectangle" not in scene
    assert "def card(" not in scene
    assert "qualifier" not in scene


def test_four_opening_fields_use_natural_discipline_names():
    assert set(load_project()["fields"]) == {
        "Communication",
        "Finance",
        "Économie",
        "Informatique",
    }


def test_revised_copy_omits_certificate_and_incomplete_bachelor_mechanism():
    spec = load_project()
    narration = " ".join(b["text"].lower() for b in spec["beats"])
    assert "maîtrise" not in narration
    assert "garanti" not in narration
    assert "emploi" not in narration
    assert "majeure" in narration
    assert "certificat" not in narration
    assert "bac en sciences" not in narration
    assert "baccalauréat" not in narration
    assert "communication" in narration
    assert "finance" in narration
    assert "économie" in narration
    assert "informatique" in narration
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


def test_unregistered_background_rejected():
    spec = load_project()
    spec["beats"][0]["background"] = "generic_stock_photo"
    with pytest.raises(ValueError):
        validate_project(spec)


def test_repeated_background_rejected():
    spec = load_project()
    spec["beats"][1]["background"] = spec["beats"][0]["background"]
    with pytest.raises(ValueError):
        validate_project(spec)


def test_low_resolution_photo_contract_rejected():
    spec = load_project()
    spec["assets"]["math_activity"]["width"] = 384
    with pytest.raises(ValueError):
        validate_assets(spec)


def test_screen_clutter_rejected():
    spec = load_project()
    spec["beats"][0]["screen"] = ["A", "B", "C", "D"]
    with pytest.raises(ValueError):
        validate_project(spec)


def test_srt_generated_from_measured_timeline(tmp_path):
    timeline, start = [], 0.0
    for beat in load_project()["beats"]:
        end = start + beat["seconds"]
        timeline.append({"start": start, "end": end, "caption": beat["caption"]})
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
        write_srt(
            [
                {"start": 0, "end": 4, "caption": "A"},
                {"start": 3, "end": 5, "caption": "B"},
            ],
            tmp_path / "bad.srt",
        )


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
    paths = [project["path"] for project in registry["videos"]]
    assert len(set(paths)) == 3
    for path in paths:
        assert (ROOT / path).is_dir()
    assert (HERE / "sources/accueil_septembre_2026.md").is_file()
    assert (ROOT / "assets/uqam_promo/sources.json").is_file()


def test_manim_480p_pixel_rounding_is_not_a_vertical_crop():
    info = media()
    info["streams"][0].update(width=854, height=480)
    assert validate_media(info, load_project(), "silent") == 20
    info["streams"][0]["width"] = 840
    with pytest.raises(ValueError):
        validate_media(info, load_project(), "silent")

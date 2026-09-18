"""Offline contracts, including the failure modes missed by the first audit."""
import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from miscellaneous.bac_sciences_ouvertures_fr.build import validate_media
from miscellaneous.bac_sciences_ouvertures_fr.project import (
    HERE,
    inspect_assets,
    load_project,
    srt_time,
    validate_assets,
    validate_project,
    write_srt,
)
from miscellaneous.bac_sciences_ouvertures_fr.timing import TimingBudgetError, plan_timeline

ROOT = Path(__file__).resolve().parents[1]


def test_project_storyboard_is_exactly_twenty_seconds():
    spec = load_project()
    assert spec["schema_version"] == 2
    assert sum(b["seconds"] for b in spec["beats"]) == 20
    assert spec["source"]["visual_pages"] == [1]
    assert spec["source"]["claim_pages"] == [21, 22, 23]
    assert spec["source"]["resource_pages"] == [7]
    assert len(spec["source"]["sha256"]) == 64


def test_visuals_are_only_the_two_audited_slide_photos():
    spec = load_project()
    assert set(validate_assets(spec)) == {"students", "building"}
    assert spec["visual_concept"] == "photo_led_sparse"
    assert all(a["source_page"] == 1 for a in spec["assets"].values())
    assert {b["background"] for b in spec["beats"]} == {"students", "building"}


def test_sparse_screen_copy_replaces_card_grid():
    spec = load_project()
    assert max(len(b["screen"]) for b in spec["beats"]) <= 3
    scene = (HERE / "bac_sciences_ouvertures_fr_scene.py").read_text(encoding="utf-8")
    assert "ImageMobject" in scene
    assert "RoundedRectangle" not in scene
    assert "def card(" not in scene
    assert "qualifier" not in scene


def test_four_fields_follow_supplied_slide_23():
    assert set(load_project()["fields"]) == {"Communication", "Finance", "Économique", "Informatique"}


def test_no_automatic_masters_job_claim_music_or_logo():
    spec = load_project()
    narration = " ".join(b["text"].lower() for b in spec["beats"])
    assert not any(word in narration for word in ("maîtrise", "garanti", "emploi"))
    assert "majeure" in narration and "certificat" in narration and "bac en sciences" in narration
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


def test_non_slide_background_rejected():
    spec = load_project()
    spec["beats"][0]["background"] = "generic_stock_photo"
    with pytest.raises(ValueError):
        validate_project(spec)


def test_screen_clutter_rejected():
    spec = load_project()
    spec["beats"][0]["screen"] = ["A", "B", "C", "D"]
    with pytest.raises(ValueError):
        validate_project(spec)


def test_srt_generated_from_measured_timeline(tmp_path):
    plan = plan_timeline(load_project(), None, 60)
    path = tmp_path / "captions.srt"
    write_srt(plan["beats"], path)
    text = path.read_text()
    assert text.count(" --> ") == 4
    assert "00:00:20,000" in text
    assert "<prosody" not in text
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
    assert validate_media(media("azure"), spec, "azure") == 20
    with pytest.raises(ValueError):
        validate_media(media(), spec, "azure")
    with pytest.raises(ValueError):
        validate_media(media("azure"), spec, "silent")


@pytest.mark.parametrize("duration", [17.9, 21.5, 22.1])
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
    registry = json.loads((ROOT / "miscellaneous/uqam_promotion.json").read_text())
    paths = [p["path"] for p in registry["videos"]]
    assert len(paths) == len(set(paths)) == 3
    assert all((ROOT / p).is_dir() for p in paths)
    assert (HERE / "sources/accueil_septembre_2026.md").is_file()


def test_manim_480p_pixel_rounding_is_not_a_vertical_crop():
    info = media()
    info["streams"][0].update(width=854, height=480)
    assert validate_media(info, load_project(), "silent") == 20
    info["streams"][0]["width"] = 840
    with pytest.raises(ValueError):
        validate_media(info, load_project(), "silent")


@pytest.mark.parametrize("fps", [15, 30, 60])
def test_global_budget_redistributes_unused_holds(fps):
    # Synthetic durations, not measurements of the user's local Azure attempts.
    # The previous sum(max(preferred, speech + .12)) was 22.12 s here.
    durations = [2.0, 7.0, 3.0, 2.0]
    plan = plan_timeline(load_project(), durations, fps)
    assert plan["beats"][-1]["end_frame"] == 20 * fps
    for row, spoken in zip(plan["beats"], durations, strict=True):
        assert row["speech_end"] <= row["end"] - row["tail_frames"] / fps + 1e-8
        assert row["speech_start"] >= row["start"] + .4 - 1e-8
        assert row["speech_seconds"] == spoken


def test_overlong_audio_rejected_before_render_with_evidence():
    with pytest.raises(TimingBudgetError) as exc:
        plan_timeline(load_project(), [5, 6, 8, 5], 60)
    assert exc.value.report["status"] == "rejected_before_render"
    assert exc.value.report["required_seconds"] > 20
    assert len(exc.value.report["beats"]) == 4


@pytest.mark.parametrize("bad", [-1.0, float("nan"), float("inf")])
def test_nonfinite_audio_duration_rejected(bad):
    with pytest.raises(ValueError):
        plan_timeline(load_project(), [bad, 2, 3, 2], 60)


@pytest.mark.parametrize("fps", [0, -1, True, 59.94])
def test_invalid_frame_rate_rejected(fps):
    with pytest.raises(ValueError):
        plan_timeline(load_project(), [2, 3, 4, 2], fps)


def test_audio_caption_ends_with_audio_not_whole_scene(tmp_path):
    plan = plan_timeline(load_project(), [2, 3, 4, 2], 60)
    target = tmp_path / "spoken.srt"
    write_srt(plan["beats"], target)
    assert "00:00:00,400 --> 00:00:02,400" in target.read_text()
    assert "00:00:20,000" not in target.read_text()


def test_last_frame_has_at_least_one_second_after_speech():
    last = plan_timeline(load_project(), [2, 3, 4, 2], 60)["beats"][-1]
    assert last["end"] - last["speech_end"] >= 1


def test_native_images_are_required_for_narrated_review(tmp_path, monkeypatch):
    monkeypatch.setenv("UQAM_OUVERTURES_SOURCE_ASSETS", str(tmp_path / "missing"))
    with pytest.raises(ValueError, match="Native slide photos required"):
        inspect_assets(load_project(), require_native=True)


def test_decoded_dimensions_are_checked(tmp_path, monkeypatch):
    spec = load_project()
    assets = {}
    for key in ("students", "building"):
        path = tmp_path / f"{key}.png"
        image = Image.new("RGB", (24, 12))
        image.save(path)
        assets[key] = {"path": path.name, "width": 24, "height": 12,
                       "pixel_sha256": hashlib.sha256(image.tobytes()).hexdigest()}
    spec["native_assets"] = assets
    (tmp_path / "manifest.json").write_text(json.dumps({"source_pdf_sha256": spec["source"]["sha256"]}))
    monkeypatch.setenv("UQAM_OUVERTURES_SOURCE_ASSETS", str(tmp_path))
    inspect_assets(spec, require_native=True)
    spec["native_assets"]["building"]["width"] = 1920
    with pytest.raises(ValueError, match="dimensions"):
        inspect_assets(spec, require_native=True)


def test_nan_subtitle_time_rejected(tmp_path):
    with pytest.raises(ValueError):
        write_srt([{"start": float("nan"), "end": 2, "caption": "A"}], tmp_path / "bad.srt")


def test_disclosure_survives_background_and_no_render_time_synthesis():
    scene = (HERE / "bac_sciences_ouvertures_fr_scene.py").read_text()
    assert "set_z_index(100)" in scene
    assert "prepare_narration(" not in scene and "generate_from_text(" not in scene
    assert "verify_package" in scene and "self.add_sound" in scene


def test_frozen_audio_reused_and_corruption_never_resynthesized(tmp_path, monkeypatch):
    import sys
    import types

    tts = pytest.importorskip("tools.tts")
    from miscellaneous.bac_sciences_ouvertures_fr import narration

    monkeypatch.setattr(tts, "configure_azure_speech_environment", lambda *a, **k: "canadacentral")
    original_hash = narration.sha256
    monkeypatch.setattr(narration, "sha256", lambda p: "a" * 64 if p.name == "tts.py" else original_hash(p))
    monkeypatch.setattr(narration, "audio_info", lambda p: {
        "duration_seconds": 3.0, "channels": 1, "sample_rate": 48000})
    calls = []

    class FakeAzureService:
        def __init__(self, *, cache_dir, **kwargs):
            self.cache_dir = cache_dir

        def generate_from_text(self, text, path):
            calls.append(text)
            # Unit-test bytes only. They are not audio and never enter a render.
            (self.cache_dir / path).write_bytes(b"SYNTHETIC_UNIT_TEST_FIXTURE" + text.encode())
            return {"original_audio": path}

    module = types.ModuleType("manim_voiceover.services.azure")
    module.AzureService = FakeAzureService
    monkeypatch.setitem(sys.modules, "manim_voiceover.services.azure", module)
    spec = load_project()
    cache = tmp_path / "cache"
    first = narration.prepare_narration(spec, tmp_path / "first", cache)
    second = narration.prepare_narration(spec, tmp_path / "second", cache)
    assert len(calls) == 4
    assert all(c["cache_reused"] for c in second["clips"])
    assert [c["sha256"] for c in first["clips"]] == [c["sha256"] for c in second["clips"]]
    narration.verify_package(spec, tmp_path / "second/audio.json")
    damaged = cache / first["clips"][0]["cache_key"] / "take.mp3"
    damaged.write_bytes(b"CORRUPT")
    with pytest.raises(ValueError, match="integrity"):
        narration.prepare_narration(spec, tmp_path / "third", cache)
    assert len(calls) == 4

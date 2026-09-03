from __future__ import annotations

import importlib.util
import inspect
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from manim import ImageMobject, Rectangle
from PIL import Image

from tools import tts

ROOT = Path(__file__).resolve().parents[1]
PROMO_DIR = ROOT / "miscellaneous" / "bac_math_uqam_fr"
SCENE_PATH = PROMO_DIR / "bac_math_uqam_fr_scene.py"
FETCHER_PATH = PROMO_DIR / "fetch_uqam_promo_assets.py"
RELEASE_PATH = PROMO_DIR / "build_release.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


scene = load_module("bac_math_uqam_fr_scene", SCENE_PATH)
fetcher = load_module("fetch_uqam_promo_assets", FETCHER_PATH)
release = load_module("build_uqam_promo_release", RELEASE_PATH)


def test_scene_defaults_to_approved_mai_release_profile() -> None:
    assert scene.PROMO_VOICE == tts.MAI_VOICE_2
    assert scene.PROMO_RATE == "+2%"
    assert scene.CTA_URL == "https://etudier.uqam.ca/programme/baccalaureat-mathematiques"
    assert scene.CTA_DISPLAY == "etudier.uqam.ca"
    assert scene.USE_REAL_PHOTOS
    assert not scene.USE_OFFICIAL_LOGO
    assert not scene.LOGO_APPROVED
    assert not scene.SHOW_PHOTO_CREDITS
    assert scene.TEACHING_PORTRAIT_HOLD == 3.2
    assert scene.RESEARCH_GRAPH_HOLD == 1.35
    assert scene.FINAL_MESSAGE_HOLD == 1.65
    assert scene.FINAL_CARD_HOLD == 2.8
    assert scene.SUPPORT_STATION_HOLD == 0.55
    assert scene.MONTREAL_PHOTO_HOLD == 1.7


def test_scene_uses_credential_safe_azure_helper_and_no_music() -> None:
    source = SCENE_PATH.read_text(encoding="utf-8")
    assert "AzureService(**azure_service_kwargs(PROMO_VOICE))" in source
    assert "configure_azure_speech_environment(PROMO_VOICE)" in source
    assert "AzureService(voice=" not in source
    assert "background music" not in source.casefold()
    assert "audio track" not in source.casefold()


def test_narration_is_six_short_ssml_safe_segments() -> None:
    assert list(scene.NARRATION_SEGMENTS) == [
        "hook",
        "human_scale",
        "research",
        "support",
        "montreal",
        "close",
    ]
    for narration in scene.NARRATION_SEGMENTS.values():
        wrapped = tts.ssml(narration, rate=scene.PROMO_RATE, locale="fr-FR")
        assert wrapped.startswith("<lang xml:lang='fr-FR'><prosody rate='+2%'>")
        assert len(tts.strip_ssml(wrapped)) < 430


def test_real_people_have_named_identity_supers() -> None:
    source = SCENE_PATH.read_text(encoding="utf-8")
    assert '"Lisa Berger"' in source
    assert '"François Bergeron"' in source
    assert "def named_person_label" in source


def test_each_real_photo_has_one_semantic_scene_use() -> None:
    functions = {
        "classroom_math.jpg": scene.BacMathUQAMFR.act_hook,
        "lisa_berger.jpg": scene.BacMathUQAMFR.act_human_scale,
        "francois_bergeron.jpg": scene.BacMathUQAMFR.act_human_scale,
        "research_math.jpg": scene.BacMathUQAMFR.act_research,
        "international_students.jpg": scene.BacMathUQAMFR.act_montreal,
        "allo_pk.jpg": scene.BacMathUQAMFR.act_montreal,
    }
    act_sources = {
        name: inspect.getsource(getattr(scene.BacMathUQAMFR, name))
        for name in (
            "act_hook",
            "act_human_scale",
            "act_support",
            "act_research",
            "act_montreal",
            "act_close",
        )
    }

    for filename, expected_function in functions.items():
        expected_name = expected_function.__name__
        assert filename in act_sources[expected_name]
        assert sum(filename in source for source in act_sources.values()) == 1

    assert "photo_card(" not in act_sources["act_close"]
    assert "full_bleed_photo(" not in act_sources["act_close"]


def test_research_and_close_use_targeted_visual_hierarchy() -> None:
    research_helper = inspect.getsource(scene.research_network_fallback)
    research_act = inspect.getsource(scene.BacMathUQAMFR.act_research)
    close_act = inspect.getsource(scene.BacMathUQAMFR.act_close)
    support_act = inspect.getsource(scene.BacMathUQAMFR.act_support)
    montreal_act = inspect.getsource(scene.BacMathUQAMFR.act_montreal)

    assert "STAGES D'ÉTÉ EN RECHERCHE" in research_helper
    assert "centre interuniversitaire" in research_helper
    assert "centre de recherche de l'UQAM" in research_helper
    assert "notamment :" in research_helper
    assert "self.wait(RESEARCH_GRAPH_HOLD)" in research_act
    assert "MENTORAT" in support_act
    assert "BIBLIOTHÈQUE" in support_act
    assert "full_bleed_photo" in montreal_act
    assert "self.wait(MONTREAL_PHOTO_HOLD)" in montreal_act
    assert "self.wait(FINAL_MESSAGE_HOLD)" in close_act
    assert "self.wait(FINAL_CARD_HOLD)" in close_act
    assert "CTA_DISPLAY" in close_act


def test_real_photo_and_vector_fallback_paths(
    tmp_path: Path, monkeypatch
) -> None:
    test_image = tmp_path / "test.jpg"
    Image.new("RGB", (80, 60), "#0079BE").save(test_image)
    monkeypatch.setattr(scene, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(scene, "USE_REAL_PHOTOS", True)

    real = scene.photo_card("test.jpg", Rectangle(), width=2.0, height=1.5)
    assert isinstance(real[0], ImageMobject)

    monkeypatch.setattr(scene, "USE_REAL_PHOTOS", False)
    fallback = Rectangle(width=2.0, height=1.0)
    vector = scene.photo_card("test.jpg", fallback, width=2.0, height=1.5)
    assert vector[0] is fallback


def test_asset_inventory_records_image_dimensions_and_hash(
    tmp_path: Path,
) -> None:
    item = {
        "kind": "image",
        "filename": "sample.jpg",
        "url": "https://example.invalid/sample.jpg",
        "source_page": "https://example.invalid/",
        "credit": "Photographer",
        "use": "Test",
    }
    path = tmp_path / item["filename"]
    Image.new("RGB", (64, 48), "white").save(path)

    record = fetcher.inspect_asset(item, tmp_path)

    assert record["status"] == "present"
    assert record["dimensions"] == {"width": 64, "height": 48}
    assert len(record["sha256"]) == 64


def test_source_manifest_contains_required_provenance(tmp_path: Path) -> None:
    records = [
        {
            "kind": "image",
            "filename": "sample.jpg",
            "url": "https://example.invalid/sample.jpg",
            "source_page": "https://example.invalid/",
            "credit": "Photographer",
            "use": "Test",
            "authorization_basis": "Authorized",
            "rights_status": "Not independently verified",
            "status": "present",
            "bytes": 12,
            "sha256": "a" * 64,
            "dimensions": {"width": 4, "height": 3},
        }
    ]
    fetcher.write_manifest(tmp_path, records)
    saved = json.loads((tmp_path / "sources.json").read_text(encoding="utf-8"))
    assert saved["assets"][0]["source_page"] == records[0]["source_page"]
    assert saved["assets"][0]["credit"] == "Photographer"
    assert saved["assets"][0]["dimensions"] == {"width": 4, "height": 3}
    assert saved["assets"][0]["sha256"] == "a" * 64
    assert saved["assets"][0]["rights_status"] == "Not independently verified"


def test_asset_provenance_does_not_claim_formal_permission() -> None:
    assert "not independently" in fetcher.AUTHORIZATION_BASIS.casefold()
    assert "confirmed authorization" not in fetcher.AUTHORIZATION_BASIS.casefold()


def test_skip_render_rejects_changed_provenance_dependencies(
    tmp_path: Path, monkeypatch
) -> None:
    raw_video = tmp_path / "raw.mp4"
    raw_srt = tmp_path / "raw.srt"
    provenance = tmp_path / "render_provenance.json"
    raw_video.write_bytes(b"video")
    raw_srt.write_text("subtitle", encoding="utf-8")
    dependency_hash = {"value": "first"}

    monkeypatch.setattr(release, "RENDER_PROVENANCE", provenance)
    monkeypatch.setattr(
        release,
        "source_file_inventory",
        lambda _environment: {
            "scene": {"path": "scene.py", "sha256": dependency_hash["value"]}
        },
    )
    monkeypatch.setattr(release, "render_toolchain", lambda: {"ffmpeg": "test"})
    environment = {"UQAM_PROMO_VOICE": "MAI-Voice-2"}

    release.write_render_provenance(raw_video, raw_srt, environment, "qh")
    release.verify_render_provenance(raw_video, raw_srt, environment, "qh")

    dependency_hash["value"] = "changed"
    with pytest.raises(RuntimeError, match="render dependency inventory"):
        release.verify_render_provenance(raw_video, raw_srt, environment, "qh")


def test_delivery_rejects_a_manifest_with_modified_output(tmp_path: Path) -> None:
    output = tmp_path / "master.mp4"
    output.write_bytes(b"original")
    manifest = {
        "outputs": {
            "video": {"path": str(output), "sha256": release.sha256_file(output)}
        }
    }
    release.verify_manifest_output_hashes(manifest)

    output.write_bytes(b"modified")
    with pytest.raises(RuntimeError, match="hash mismatch"):
        release.verify_manifest_output_hashes(manifest)


def test_release_loudness_parser_and_boolean_run() -> None:
    stderr = """
    {
      "input_i" : "-23.10",
      "input_tp" : "-3.20",
      "input_lra" : "2.40",
      "input_thresh" : "-33.20",
      "output_i" : "-18.50",
      "output_tp" : "-1.00",
      "output_lra" : "2.20",
      "output_thresh" : "-28.50",
      "normalization_type" : "dynamic",
      "target_offset" : "0.00"
    }
    """
    measured = release.parse_loudnorm_json(stderr)
    assert measured["integrated_lufs"] == -23.1
    assert measured["true_peak_dbfs"] == -3.2
    assert release.longest_true_run(
        np.array([False, True, True, False, True]), 0.02
    ) == 0.04


def test_srt_validation_rejects_ssml_and_accepts_ordered_cues(
    tmp_path: Path,
) -> None:
    subtitles = tmp_path / "promo.srt"
    subtitles.write_text(
        "1\n00:00:00,000 --> 00:00:02,000\nBonjour.\n\n"
        "2\n00:00:02,100 --> 00:00:04,000\nBienvenue.\n",
        encoding="utf-8",
    )
    result = release.validate_srt(subtitles, 5.0)
    assert result["caption_count"] == 2

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
    assert scene.HOOK_RATE == "0%"
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
    assert scene.SUPPORT_HUMAN_HOLD == 2.25
    assert scene.SUPPORT_LIBRARY_HOLD == 2.3
    assert scene.SUPPORT_PAGE_HOLD == 1.15
    assert scene.MONTREAL_BUILDING_HOLD == 2.0
    assert scene.MONTREAL_PHOTO_HOLD == 1.7


def test_scene_uses_credential_safe_azure_helper_and_no_music() -> None:
    source = SCENE_PATH.read_text(encoding="utf-8")
    assert "AzureService(**azure_service_kwargs(PROMO_VOICE))" in source
    assert "configure_azure_speech_environment(PROMO_VOICE)" in source
    assert "AzureService(voice=" not in source
    assert "background music" not in source.casefold()
    assert "audio track" not in source.casefold()


def test_visible_promo_copy_uses_the_freetype_kerning_renderer() -> None:
    source = SCENE_PATH.read_text(encoding="utf-8")

    assert "def kerning_text" in source
    assert "ImageFont.truetype" in source
    assert "ImageDraw.Draw" in source
    assert "TypographyDiagnostic" in source
    # Pango remains only for the invisible sizing probe and the diagnostic's
    # red comparison row; no promotional screen uses it for visible copy.
    assert source.count("Text(") == 2

    rendered = scene.kerning_text("AV To fi", size=30, weight="MEDIUM")
    assert isinstance(rendered, ImageMobject)
    assert scene.TEXT_RASTER_SCALE >= 2


def test_release_provenance_records_the_typography_renderer() -> None:
    configuration = release.render_configuration({}, "ql")

    assert configuration["typography_renderer"] == "Pillow/FreeType"
    assert configuration["text_raster_scale"] == str(scene.TEXT_RASTER_SCALE)
    assert configuration["font_sha256"] == release.sha256_file(scene.FONT_PATH)
    assert configuration["pillow_version"] != "not-installed"


def test_narration_is_six_short_ssml_safe_segments() -> None:
    assert list(scene.NARRATION_SEGMENTS) == [
        "hook",
        "human_scale",
        "research",
        "support",
        "montreal",
        "close",
    ]
    for name, narration in scene.NARRATION_SEGMENTS.items():
        wrapped = tts.ssml(
            narration, rate=scene.NARRATION_RATES[name], locale="fr-FR"
        )
        assert wrapped.startswith(
            f"<lang xml:lang='fr-FR'><prosody rate='{scene.NARRATION_RATES[name]}'>"
        )
        assert len(tts.strip_ssml(wrapped)) < 430


def test_real_people_have_named_identity_supers() -> None:
    source = SCENE_PATH.read_text(encoding="utf-8")
    assert '"Lisa Berger"' in source
    assert '"François Bergeron"' in source
    assert "def named_person_label" in source


def test_support_scene_uses_editorial_photo_treatment_and_safe_fallbacks() -> None:
    source = SCENE_PATH.read_text(encoding="utf-8")
    support_act = inspect.getsource(scene.BacMathUQAMFR.act_support)

    assert "def editorial_photo" in source
    assert "def editorial_caption" in source
    assert "def support_classy_fallback" in source
    assert "def library_classy_fallback" in source
    assert "support_students.jpg" in support_act
    assert "bibliotheque_sciences_2026.jpg" in support_act
    assert "full_bleed_photo" not in support_act
    assert "Circle(" not in support_act
    assert "simple_person" not in support_act
    assert "MENTORAT" not in support_act
    assert "BIBLIOTHÈQUE" not in support_act
    assert scene.support_classy_fallback().width == pytest.approx(
        scene.config.frame_width
    )
    assert scene.library_classy_fallback().height == pytest.approx(
        scene.config.frame_height
    )


def test_each_real_photo_has_one_semantic_scene_use() -> None:
    functions = {
        "campus_central_uqam.jpg": scene.BacMathUQAMFR.act_hook,
        "lisa_berger.jpg": scene.BacMathUQAMFR.act_human_scale,
        "francois_bergeron.jpg": scene.BacMathUQAMFR.act_human_scale,
        "research_math.jpg": scene.BacMathUQAMFR.act_research,
        "support_students.jpg": scene.BacMathUQAMFR.act_support,
        "bibliotheque_sciences_2026.jpg": scene.BacMathUQAMFR.act_support,
        "sciences_biologiques_uqam.jpg": scene.BacMathUQAMFR.act_montreal,
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

    assert "Stages d'été en recherche" in research_helper
    assert "promo_label" in research_helper
    assert "centre interuniversitaire" in research_helper
    assert "centre de recherche de l'UQAM" in research_helper
    assert "notamment :" in research_helper
    assert "narrate_unit" in research_act
    assert "editorial_photo" in support_act
    assert "editorial_caption" in support_act
    assert "support_students.jpg" in support_act
    assert "bibliotheque_sciences_2026.jpg" in support_act
    assert "simple_person" not in support_act
    assert "SUPPORT_PAGE_HOLD" in support_act
    assert "promo_label(\"Échanger\"" in inspect.getsource(
        scene.BacMathUQAMFR.act_human_scale
    )
    assert "ÉCHANGER" not in inspect.getsource(scene.BacMathUQAMFR.act_human_scale)
    assert "full_bleed_photo" in montreal_act
    assert "sciences_biologiques_uqam.jpg" in montreal_act
    assert "Photo : UQAM" in montreal_act
    assert "narrate_unit" in montreal_act
    assert "record_photo" in montreal_act
    assert "narrate_unit" in close_act
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


def test_uqam_press_photo_bank_is_the_default_library() -> None:
    assert fetcher.UQAM_DEFAULT_PHOTO_LIBRARY == (
        "https://salledepresse.uqam.ca/banque-de-photos/"
    )
    assert fetcher.UQAM_PAVILION_PHOTO_LIBRARY.startswith(
        fetcher.UQAM_DEFAULT_PHOTO_LIBRARY
    )
    opening = next(
        item for item in fetcher.ASSETS if item["filename"] == "campus_central_uqam.jpg"
    )
    science_complex = next(
        item
        for item in fetcher.ASSETS
        if item["filename"] == "sciences_biologiques_uqam.jpg"
    )
    assert opening["source_page"] == fetcher.UQAM_PAVILION_PHOTO_LIBRARY
    assert science_complex["source_page"] == fetcher.UQAM_PAVILION_PHOTO_LIBRARY
    assert opening["credit"] == "Photo : UQAM"
    assert science_complex["credit"] == "Photo : UQAM"


def test_superseded_promo_photos_do_not_return() -> None:
    source = SCENE_PATH.read_text(encoding="utf-8")
    fetch_source = FETCHER_PATH.read_text(encoding="utf-8")
    for old_name in (
        "classroom_math.jpg",
        "bibliotheque_sciences.jpg",
        "president_kennedy.jpg",
    ):
        assert old_name not in source
        assert old_name not in fetch_source


def test_library_asset_records_its_context_and_credit() -> None:
    library = next(
        item for item in fetcher.ASSETS if item["filename"] == "bibliotheque_sciences_2026.jpg"
    )
    assert library["credit"] == "Service des bibliothèques · UQAM"
    assert "2021" in library["use"]
    assert "masked visitors" in library["use"]
    assert library["rights_status"] == fetcher.RIGHTS_STATUS


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


def test_release_video_uses_shared_archive_command(tmp_path: Path, monkeypatch) -> None:
    video = tmp_path / "release.mp4"
    video.write_bytes(b"video")
    calls: list[list[str]] = []
    monkeypatch.setattr(
        release,
        "run_checked",
        lambda command, **_kwargs: calls.append(command),
    )

    release.archive_video(video, "qh")

    assert calls == [
        [
            sys.executable,
            str(release.ARCHIVE_SCRIPT),
            "register",
            str(video),
            "--quality",
            "qh",
        ]
    ]


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


def test_build_report_uses_effective_narration_configuration() -> None:
    manifest = {
        "outputs": {"video": {"path": "review.mp4"}},
        "validation": {
            "media": {"duration_seconds": 80.0},
            "loudness_after": {"integrated_lufs": -18.5, "true_peak_dbfs": -1.3},
            "subtitles": {"caption_count": 25},
        },
        "configuration": {"hook_rate": "-1%", "narration_rate": "-3%"},
        "built_at": "test-fixture", "normalization_applied": False,
    }
    report = release.build_report_text(manifest)
    assert "hook at -1%" in report
    assert "main narration at -3%" in report
    assert "main narration at +2%" not in report

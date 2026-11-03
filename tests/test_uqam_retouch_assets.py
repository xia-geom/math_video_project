"""Protect retouched-photo bytes from original-URL downloads and stale lineage."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FETCHER = ROOT / "miscellaneous/bac_math_uqam_fr/fetch_uqam_promo_assets.py"
SPEC = importlib.util.spec_from_file_location("uqam_retouch_fetcher", FETCHER)
assert SPEC is not None and SPEC.loader is not None
fetcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetcher)


@pytest.fixture
def derivative(tmp_path: Path) -> tuple[dict[str, str], Path]:
    original = tmp_path / "original.jpg"
    edited = tmp_path / "edited.png"
    Image.new("RGB", (24, 16), "white").save(original)
    Image.new("RGB", (24, 16), "gray").save(edited)
    return {
        "kind": "image", "filename": edited.name,
        "retrieval": "local_derivative",
        "url": "https://example.invalid/original.jpg",
        "source_page": "https://example.invalid/",
        "credit": "Original photographer", "use": "Synthetic localized edit",
        "derived_from": original.name,
        "derived_from_sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
        "expected_sha256": hashlib.sha256(edited.read_bytes()).hexdigest(),
        "modifications": "Localized synthetic patch",
        "modification_date": "2026-10-04",
        "modification_method": fetcher.DERIVATIVE_METHOD,
        "reproduction": "Restore reviewed local bytes; the source URL is the original only.",
    }, tmp_path


def fail_network(*_args, **_kwargs):
    pytest.fail("Retouched assets must not request their original image URL")


def test_derivative_download_rejected_before_network(derivative, monkeypatch) -> None:
    item, directory = derivative
    monkeypatch.setattr(fetcher.urllib.request, "urlopen", fail_network)
    before = (directory / item["filename"]).read_bytes()
    with pytest.raises(RuntimeError, match="cannot be downloaded"):
        fetcher.download_atomic(item, directory / item["filename"])
    assert (directory / item["filename"]).read_bytes() == before


def test_force_refresh_keeps_approved_derivative_and_records_provenance(
    derivative, monkeypatch,
) -> None:
    item, directory = derivative
    monkeypatch.setattr(fetcher, "ASSETS", [item])
    monkeypatch.setattr(fetcher.urllib.request, "urlopen", fail_network)
    monkeypatch.setattr(sys, "argv", [str(FETCHER), "--force", "--asset-dir", str(directory)])
    before = (directory / item["filename"]).read_bytes()
    assert fetcher.main() == 0
    assert (directory / item["filename"]).read_bytes() == before
    record = json.loads((directory / "sources.json").read_text())["assets"][0]
    assert record["format"] == "PNG"
    assert record["dimensions"] == {"width": 24, "height": 16}
    assert record["sha256"] == item["expected_sha256"]
    assert record["derived_from_sha256"] == item["derived_from_sha256"]
    assert record["credit"] == "Original photographer"
    markdown = (directory / "SOURCES.md").read_text()
    assert "Untouched original source" in markdown
    assert item["modification_method"] in markdown
    assert "Original SHA-256" in markdown


@pytest.mark.parametrize("changed_file", ["original.jpg", "edited.png"])
def test_changed_original_or_derivative_is_rejected(derivative, changed_file) -> None:
    item, directory = derivative
    Image.new("RGB", (24, 16), "black").save(directory / changed_file)
    expected_error = "lineage" if changed_file == "original.jpg" else "pinned editorial"
    with pytest.raises(RuntimeError, match=expected_error):
        fetcher.inspect_asset(item, directory)

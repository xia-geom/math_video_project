"""Focused geometry/rendering contracts for the reconstructed faculty mark."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from manim import ImageMobject, SVGMobject

from tools.faculty_branding import (
    REFERENCE_BLUE,
    REFERENCE_GREEN,
    SIGNATURE_ASPECT_RATIO,
    SIGNATURE_PATH,
    faculty_signature,
)


def test_signature_is_native_vector_with_preserved_geometry_and_colors():
    signature = faculty_signature(3.6)
    assert isinstance(signature, SVGMobject)
    assert signature.width == pytest.approx(3.6)
    assert signature.width / signature.height == pytest.approx(SIGNATURE_ASPECT_RATIO)
    assert not any(isinstance(part, ImageMobject) for part in signature.get_family())
    paths = signature.family_members_with_points()
    assert {path.get_fill_color().to_hex().upper() for path in paths} == {
        REFERENCE_BLUE, REFERENCE_GREEN, "#000000"
    }
    assert all(path.get_stroke_width() == 0 for path in paths)


def test_vector_source_has_no_font_or_raster_dependency():
    root = ET.parse(SIGNATURE_PATH).getroot()
    tags = {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
    assert tags == {"svg", "path"}
    assert all("href" not in attribute for element in root.iter() for attribute in element.attrib)
    assert len(root.findall("{http://www.w3.org/2000/svg}path")) == 3


@pytest.mark.parametrize("width", [0, -1, float("inf"), float("nan"), True, "3.6"])
def test_signature_rejects_invalid_width(width):
    with pytest.raises(ValueError, match="positive finite"):
        faculty_signature(width)


def test_signature_instances_can_be_positioned_independently():
    left = faculty_signature(3.6)
    right = faculty_signature(4.2)
    left.shift([-2, 0, 0])
    assert right.get_center() == pytest.approx([0, 0, 0])
    assert right.width == pytest.approx(4.2)


def test_concurrent_svg_parsing_uses_private_temporary_files(monkeypatch):
    import tools.faculty_branding as branding
    barrier, paths = Barrier(2), []
    original = branding.SVGMobject

    def simultaneous_parse(path, **kwargs):
        paths.append(Path(path))
        barrier.wait(timeout=15)
        return original(path, **kwargs)

    monkeypatch.setattr(branding, 'SVGMobject', simultaneous_parse)
    with ThreadPoolExecutor(max_workers=2) as executor:
        marks = list(executor.map(branding.faculty_signature, [3.6, 4.2]))
    assert paths[0].parent != paths[1].parent
    assert all(path.parent != SIGNATURE_PATH.parent for path in paths)
    assert all(not path.exists() for path in paths)
    assert [mark.width for mark in marks] == pytest.approx([3.6, 4.2])

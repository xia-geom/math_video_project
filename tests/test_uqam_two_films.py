"""Geometry and source contracts for the actual two-film redesign."""

from pathlib import Path

import pytest
from manim import Group, Rectangle, Text, config
from PIL import Image

from miscellaneous.bac_math_uqam_fr.bac_math_uqam_fr_scene import research_network_fallback
from miscellaneous.bac_math_uqam_fr.promo_beats import NARRATION_BEATS, REVIEW_SECONDS
from miscellaneous.bac_sciences_ouvertures_fr.bac_sciences_ouvertures_fr_scene import (
    BacSciencesOuverturesFR,
)
from tools.uqam_promo_layout import check_copy_layout, mark_copy, placed_photo


def test_research_cards_fit_their_real_typographic_panels():
    cards = research_network_fallback()
    checked = check_copy_layout([cards], "all-three-centres")
    words = {label["text"] for label in checked["labels"]}
    assert {"CIRGET", "LaCIM", "STATQAM", "Statistique", "Science", "des données"} <= words
    assert "Des domaines à explorer" in words


def test_outside_frame_copy_is_rejected():
    label = mark_copy(Text("Trop loin"), "Trop loin").shift([20, 0, 0])
    with pytest.raises(ValueError, match="safe area"):
        check_copy_layout([label], "bad-frame")


def test_colliding_labels_are_rejected():
    labels = Group(mark_copy(Text("Bonjour"), "Bonjour"), mark_copy(Text("UQAM"), "UQAM"))
    with pytest.raises(ValueError, match="Overlapping"):
        check_copy_layout([labels], "bad-overlap")


def test_long_card_copy_cannot_hide_behind_a_passing_outer_card():
    panel = Rectangle(width=1.0, height=1.0)
    label = mark_copy(Text("Beaucoup trop long"), "Beaucoup trop long")
    label.uqam_containing_panel = panel
    with pytest.raises(ValueError, match="padding"):
        check_copy_layout([Group(panel, label)], "bad-card")


def test_photo_resolution_is_checked_for_1080p_even_in_small_preview(tmp_path):
    path = tmp_path / "small.jpg"
    Image.new("RGB", (1000, 707)).save(path)
    panel = placed_photo(path, 6.6, 4.67)
    assert panel.width == pytest.approx(6.6)
    with pytest.raises(ValueError, match="enlarged"):
        placed_photo(path, config.frame_width, config.frame_height)


def test_wide_photo_fills_frame_without_stretching_or_uncovered_edges(tmp_path):
    path = tmp_path / "wide.jpg"
    Image.new("RGB", (5000, 1500)).save(path)
    image = placed_photo(path, config.frame_width, config.frame_height)
    assert image.width == pytest.approx(config.frame_width)
    assert image.height == pytest.approx(config.frame_height)


def test_preview_clocks_are_explicit_and_not_spoken_copy():
    assert NARRATION_BEATS.keys() == REVIEW_SECONDS.keys()
    for name, units in NARRATION_BEATS.items():
        assert len(units) == len(REVIEW_SECONDS[name])
        assert all(n > 0 for n in REVIEW_SECONDS[name])


def test_production_does_not_call_silent_clock():
    root = Path(__file__).resolve().parents[1]
    source = (root / "miscellaneous/bac_math_uqam_fr/bac_math_uqam_fr_scene.py").read_text()
    assert "REVIEW_SECONDS" not in source
    assert "require_credentials=True" in source
    sciences = (root / "miscellaneous/bac_sciences_ouvertures_fr/bac_sciences_ouvertures_fr_scene.py").read_text()
    assert "allocate_slots" in sciences and "add_foreground_mobjects" in sciences


def test_retained_white_card_renders_one_complete_message_without_a_gap():
    """Exercise dispatch: the previous fade sequence left a blank white hold."""
    background, old_copy, new_copy = object(), object(), object()

    class RecordingScene:
        def __init__(self):
            self.visible = {background, old_copy}
            self.frames = []

        def add(self, item):
            self.visible.add(item)

        def remove(self, item):
            self.visible.remove(item)

        def wait(self, seconds):
            self.frames.append((seconds, set(self.visible)))

        def play(self, *args, **kwargs):
            pytest.fail("A retained white card must not fade its messages through an empty frame")

    scene = RecordingScene()
    BacSciencesOuverturesFR.transition(scene, background, old_copy, background, new_copy, 0.75)
    assert scene.frames == [(0.75, {background, new_copy})]


def test_veil_is_precomposed_into_photo_not_animated_twice(tmp_path):
    from tools.uqam_promo_layout import photo_canvas

    path = tmp_path / "plain.png"
    Image.new("RGB", (2000, 1200), (200, 100, 50)).save(path)
    background = photo_canvas(path, width=config.frame_width, height=config.frame_height, veil=0.5, veil_color="black")
    assert tuple(background.pixel_array[500, 900, :3]) == (100, 50, 25)
    assert background.pixel_array[:, :, 3].min() == 255

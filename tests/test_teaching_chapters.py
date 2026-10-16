"""Pilot navigation, containment and speech-clock regressions."""
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from manim import Scene, Text, VGroup, tempconfig

from tools.teaching_chapters import (
    ACCENT, ERROR, INK, SUCCESS, assert_card_fits, chapter_card,
    contrast_ratio, play_chapter_outline,
)

TITLES = ('Tester une simplification', 'Facteurs ou termes ?',
          'Factoriser et garder les restrictions', 'Vérifier sa méthode')


@pytest.mark.parametrize('active', range(4))
def test_longest_pilot_outline_fits_and_only_active_row_is_bold(active):
    card = chapter_card(TITLES, active)
    assert_card_fits(card)
    assert [row.weight for row in card[1]] == [
        'BOLD' if i == active else 'NORMAL' for i in range(4)]
    assert all(row.font_size == pytest.approx(30) for row in card[1])
    assert card[1].get_left()[0] == pytest.approx(-5.3)


def test_text_palette_passes_contrast_including_tinted_error_panels():
    assert contrast_ratio(INK) >= 7
    for color in (ACCENT, SUCCESS, ERROR):
        assert contrast_ratio(color) >= 4.5
        channels = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
        tint = '#' + ''.join(f'{round(0.06 * c + 0.94 * 255):02X}' for c in channels)
        assert contrast_ratio(color, tint) >= 4.5


def test_overflow_fails_instead_of_shrinking_text():
    with pytest.raises(ValueError, match='safe margins'):
        chapter_card(('Un très long titre ' * 15,), 0)


class ClockScene:
    def __init__(self):
        self.renderer = SimpleNamespace(time=0.0)
        self.mobjects = []
        self.page = None

    def play(self, *args, run_time):
        self.renderer.time += run_time

    def wait(self, duration):
        self.renderer.time += duration

    def remove(self, *objects):
        self.mobjects = [obj for obj in self.mobjects if obj not in objects]


def test_card_waits_for_complete_speech_and_clears_stale_updaters():
    scene = ClockScene()
    stale = Text('Ancienne page').add_updater(lambda _: None)
    scene.mobjects = [stale]
    scene.page = stale

    @contextmanager
    def narration(text):
        assert scene.page is None
        start = scene.renderer.time
        yield
        scene.renderer.time = max(scene.renderer.time, start + 8)

    play_chapter_outline(scene, TITLES, 0, 'Commençons.', narration=narration)
    event = scene.chapter_review_events[0]
    assert event['speech_end'] - event['visible_from'] == pytest.approx(8)
    assert event['end'] - event['speech_end'] == pytest.approx(0.4)
    assert not stale.updaters
    assert scene.page is None
    assert not scene.mobjects


def test_names_and_order_cannot_drift_between_reminders():
    scene = ClockScene()
    play_chapter_outline(scene, TITLES, 0, 'Commençons.')
    with pytest.raises(ValueError, match='exactly once'):
        play_chapter_outline(scene, TITLES, 0, 'Encore.')
    with pytest.raises(ValueError, match='names and order'):
        play_chapter_outline(scene, tuple(reversed(TITLES)), 1, 'Suite.')
    with pytest.raises(ValueError, match='exactly once'):
        play_chapter_outline(scene, TITLES, 2, 'Suite.')


def test_continuing_diagram_restores_objects_and_original_updater_states(tmp_path):
    class ContinuingDiagram(Scene):
        def construct(self):
            update = lambda item, dt: None
            active = Text('Diagramme').add_updater(update)
            frozen = Text('Annotation').add_updater(update)
            frozen.suspend_updating()
            self.add(active, frozen)
            page = self.page = VGroup(active, frozen)

            @contextmanager
            def narration(spoken):
                assert active not in self.mobjects and frozen not in self.mobjects
                assert self.page is None
                assert active.updating_suspended and frozen.updating_suspended
                yield

            play_chapter_outline(self, TITLES, 0, 'Suite du raisonnement.',
                                 narration=narration, preserve_content=True)
            assert active in self.mobjects and frozen in self.mobjects
            assert self.page is page
            assert active.updaters == frozen.updaters == [update]
            assert not active.updating_suspended
            assert frozen.updating_suspended

    with tempconfig({'dry_run': True, 'skip_animations': True,
                     'media_dir': str(tmp_path), 'progress_bar': 'none'}):
        ContinuingDiagram().render()

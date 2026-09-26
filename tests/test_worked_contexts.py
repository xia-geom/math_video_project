"""A boxed answer must refer to the problem still visible above it."""
from __future__ import annotations

import pytest
from manim import RIGHT, MathTex, VGroup, tempconfig

from tools import expanded_teaching
from tools.expanded_teaching import (
    ExpandedTeachingScene,
    check_frame,
    check_panels,
    load_examples,
    step_premises,
)
from tools.teaching_layout import BODY_HEIGHT, panel


@pytest.fixture(autouse=True)
def local_tex(tmp_path):
    (tmp_path / 'Tex').mkdir()
    with tempconfig({'media_dir': str(tmp_path), 'tex_dir': str(tmp_path / 'Tex')}):
        yield


def test_premise_change_persists_until_replaced():
    assert step_premises({'premise': 'old', 'steps': [
        {}, {'premise': 'new'}, {}, {'premise': 'third'}, {}
    ]}) == ['old', 'new', 'new', 'third', 'third']
    with pytest.raises(ValueError):
        step_premises({'premise': 'old', 'steps': [{'premise': ''}]} )


@pytest.mark.parametrize('lesson_id', list(load_examples()))
def test_all_replacement_premises_fit_without_font_reduction(lesson_id):
    for example in load_examples()[lesson_id]:
        texts = list(dict.fromkeys([example['premise'], *step_premises(example)]))
        formulas = [MathTex(s, font_size=36) for s in texts]
        top_height = max(1.4, max(m.height for m in formulas) + 0.68)
        rows = [MathTex(s['math'], font_size=38) for s in example['steps']]
        bottom_height = max(1.4, max(m.height for m in rows) + 0.68)
        assert top_height + bottom_height + 0.35 <= BODY_HEIGHT
        for formula in formulas:
            assert check_panels(panel(formula, width=10.8, height=top_height, padding=0.34)) == 1


def test_actual_guided_reveal_replaces_old_problem_before_new_answer(monkeypatch):
    example = {'title': 'Changer les données', 'premise': 'x=1', 'prompt': 'Premier cas.',
               'intro_seconds': 1, 'steps': [
                   {'math': '2x=2', 'narration': 'Deux.', 'reading_seconds': 1},
                   {'premise': 'x=2', 'math': '2x=4', 'narration': 'Quatre.', 'reading_seconds': 1},
                   {'math': '3x=6', 'narration': 'Six.', 'reading_seconds': 1}]}
    monkeypatch.setattr(expanded_teaching, 'load_examples', lambda: {'test': [example]})
    scene = object.__new__(ExpandedTeachingScene)
    scene.page = None
    scene.worked_example_steps = 0
    scene.worked_contexts = []
    scene.play = lambda *args, **kwargs: None
    scene.remove = lambda *args: None
    seen = []
    scene.explain = lambda text, *objects, **kwargs: seen.append(scene.page[1][0][1].tex_string)
    scene.guided_examples('test')
    assert seen == ['x=1', 'x=1', 'x=2', 'x=2']
    assert [r['premise'] for r in scene.worked_contexts] == ['x=1', 'x=2', 'x=2']
    assert scene.worked_example_steps == 3
    assert check_panels(scene.page) == 2


def test_repaired_elimination_case_no_longer_displays_the_inconsistent_system():
    example = load_examples()['elimination_variables'][1]
    contexts = step_premises(example)
    assert '2x+4y=6' in contexts[2]
    assert '2x+4y=8' in contexts[3] and contexts[3] == contexts[4]
    assert '2x+4y=6' not in contexts[4]


def test_unbounded_optimization_case_no_longer_claims_the_old_region():
    contexts = step_premises(load_examples()['programmation_lineaire'][1])
    assert 'Même région' in contexts[3]
    assert 'Même région' not in contexts[4]
    assert 'seulement' in contexts[4]


def test_frame_guard_catches_a_card_that_contains_its_formula_but_is_offscreen():
    card = panel(MathTex('x=2', font_size=38))
    check_frame(VGroup(card))
    card.shift(8 * RIGHT)
    assert check_panels(card) == 1
    with pytest.raises(ValueError, match='safe margin'):
        check_frame(VGroup(card))

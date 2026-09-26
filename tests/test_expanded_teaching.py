"""Regression checks for the ten expanded lessons, not a listening certificate."""
from __future__ import annotations

import ast
import itertools
import math
from fractions import Fraction
from pathlib import Path

import pytest
from manim import RIGHT, MathTex, Text, VGroup, tempconfig

from tools.course_catalog import load_catalog
from tools.expanded_teaching import ExpandedTeachingScene, check_panels, load_examples
from tools.teaching_layout import BODY_HEIGHT, BODY_WIDTH, TeachingScene, panel

ROOT = Path(__file__).resolve().parents[1]
IDS = [e['lesson_id'] for e in load_catalog()[1] if e['legacy_id'].startswith('S')]


@pytest.fixture(scope='module', autouse=True)
def isolated_tex(tmp_path_factory):
    root = tmp_path_factory.mktemp('expanded-math')
    (root / 'Tex').mkdir()
    with tempconfig({'media_dir': str(root), 'tex_dir': str(root / 'Tex')}):
        yield


def test_exact_scope_and_twenty_distinct_worked_examples():
    lessons = load_examples()
    assert set(lessons) == set(IDS)
    assert len(lessons) == 10
    prompts = []
    for examples in lessons.values():
        assert len(examples) == 2
        for example in examples:
            assert len(example['steps']) == 5
            assert example['intro_seconds'] > 0
            assert len({s['math'] for s in example['steps']}) == 5
            assert all(s['narration'].strip() and 0 < s['reading_seconds'] <= 15
                       for s in example['steps'])
            prompts.append(example['prompt'])
    assert len(prompts) == len(set(prompts))


@pytest.mark.parametrize('lesson_id', IDS)
def test_expansion_is_used_once_and_adds_explanations_not_blank_waits(lesson_id):
    entry = next(e for e in load_catalog()[1] if e['lesson_id'] == lesson_id)
    source = (ROOT / entry['scene_file']).read_text(encoding='utf-8')
    tree = ast.parse(source)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, 'attr', '') == 'guided_examples']
    assert len(calls) == 1 and ast.literal_eval(calls[0].args[0]) == lesson_id
    assert 'from tools.expanded_teaching import ExpandedTeachingScene' in source
    examples = load_examples()[lesson_id]
    added_words = sum(len(example['prompt'].split()) + sum(len(s['narration'].split())
                      for s in example['steps']) for example in examples)
    assert added_words >= 350  # Revision-specific depth check, not a duration standard.


@pytest.mark.parametrize('lesson_id', IDS)
def test_every_new_math_row_and_title_fits_at_authored_size(lesson_id):
    for example in load_examples()[lesson_id]:
        assert Text(example['title'], font_size=40).width <= BODY_WIDTH
        premise = panel(MathTex(example['premise'], font_size=36), width=10.8, height=1.4)
        rows = [MathTex(step['math'], font_size=38) for step in example['steps']]
        height = max(1.4, max(row.height for row in rows) + 0.68)
        assert premise.height + height + 0.35 <= BODY_HEIGHT, example['title']
        for row in rows:
            card = panel(row, width=10.8, height=height, padding=0.34)
            assert check_panels(card) == 1


def test_guard_detects_content_moved_out_after_panel_creation():
    card = panel(MathTex(r'\frac{a+b}{c}=2', font_size=42))
    assert check_panels(VGroup(card)) == 1
    card[1].shift(4 * RIGHT)
    with pytest.raises(ValueError, match='outside'):
        check_panels(VGroup(card))


def test_bare_result_is_revealed_with_its_own_border(monkeypatch):
    scene = object.__new__(ExpandedTeachingScene)
    scene.page = None
    scene.play = lambda *args, **kwargs: None
    formula = MathTex(r'x=2', font_size=42)
    original_width = formula.width
    scene.new_page('Résultat', formula)
    assert formula.width == pytest.approx(original_width)
    owner = scene._math_card_owners[id(formula)]
    assert owner[1] is formula
    seen = []
    monkeypatch.setattr(TeachingScene, 'explain',
                        lambda self, text, *objects, **kwargs: seen.extend(objects))
    scene.explain('Le résultat vaut deux.', formula)
    assert seen == [owner]
    assert check_panels(scene.page) == 1


def test_fraction_and_precedence_examples():
    assert 18 / 3 * 2 == 12 and 18 / (3 * 2) == 3
    assert (Fraction(3, 4) - Fraction(1, 6)) / Fraction(7, 3) == Fraction(1, 4)


def test_rational_examples_preserve_domain_and_limits():
    for x in (Fraction(19, 10), Fraction(21, 10), -3, 0):
        assert (x * x - 4) / (x - 2) == x + 2
    for x in (-10, 0, 2, 100):
        assert (2 * x + 3) / (x - 1) == pytest.approx(2 + 5 / (x - 1))
    assert (2 * 0 + 3) / (0 - 1) == -3


def test_probability_models_by_enumeration():
    outcomes = list(itertools.product('PF', repeat=2))
    assert sum(o.count('P') == 1 for o in outcomes) == 2
    assert sum(o.count('P') >= 1 for o in outcomes) == 3
    balls = [('R', i) for i in range(3)] + [('B', i) for i in range(2)]
    draws = list(itertools.permutations(balls, 2))
    assert Fraction(sum(a[0] == b[0] == 'R' for a, b in draws), len(draws)) == Fraction(3, 10)
    assert Fraction(sum(a[0] == b[0] == 'B' for a, b in draws), len(draws)) == Fraction(1, 10)
    assert Fraction(sum(a[0] != b[0] for a, b in draws), len(draws)) == Fraction(3, 5)


def test_line_plane_and_three_variable_elimination():
    assert 5 + 2 * 0 == 5 and 5 + 2 * 1 != 5
    normal = (1, 2, -1)
    for v in ((2, -1, 0), (1, 0, 1)):
        assert sum(a * b for a, b in zip(normal, v)) == 0
    for s, t in itertools.product(range(-2, 3), repeat=2):
        x, y, z = 1 + 2 * s + t, -s, 2 + t
        assert x + 2 * y - z + 1 == 0
    x, y, z = 1, 2, 3
    assert (x + y + z, 2 * x - y + z, x + 2 * y - z) == (6, 3, 2)


def test_cramer_and_optimization_examples():
    assert 3 * 1 - (-2) * 1 == 5
    assert 7 * 1 - (-2) * 4 == 15
    assert 3 * 4 - 7 * 1 == 5
    assert (3 * 3 - 2, 3 + 1) == (7, 4)
    for k in range(101):
        t = Fraction(k, 100)
        x, y = 2 + 2 * t, 3 - 2 * t
        assert 0 <= x <= 4 and 0 <= y <= 3 and x + y == 5
        assert 3 * x + 2 * y <= 14


def test_triangle_lengths_and_ambiguous_case():
    h, d = 5 * math.sqrt(3) / 2, 2.5
    assert h * h + d * d == pytest.approx(25)
    assert 6 ** 2 + (2 * math.sqrt(3)) ** 2 == pytest.approx((4 * math.sqrt(3)) ** 2)
    angle_a = math.pi / 6
    b1 = math.asin(0.8)
    b2 = math.pi - b1
    sides = []
    for angle_b in (b1, b2):
        angle_c = math.pi - angle_a - angle_b
        assert angle_c > 0
        sides.append(10 * math.sin(angle_c))
    assert sides == pytest.approx([9.9282032303, 3.9282032303])


def test_inverse_branches_and_all_solutions():
    assert math.asin(math.sin(7 * math.pi / 6)) == pytest.approx(-math.pi / 6)
    assert math.atan(math.tan(3 * math.pi / 4)) == pytest.approx(-math.pi / 4)
    for k in range(-5, 6):
        for theta in (math.pi / 6 + 2 * k * math.pi, 5 * math.pi / 6 + 2 * k * math.pi):
            assert math.sin(theta) == pytest.approx(0.5)

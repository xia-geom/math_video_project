"""Practice content and timing contracts, runnable without Manim or Azure."""
from fractions import Fraction
import math

import pytest
import yaml

from tools.lesson_practice import load_practice


def test_ten_independent_questions_with_delayed_three_step_solutions():
    questions = load_practice()
    assert len(questions) == 10
    for question in questions.values():
        assert question['question_seconds'] >= 18
        assert question['reflection_seconds'] >= 12
        assert len({step['math'] for step in question['steps']}) == 3
        assert all(step['reading_seconds'] >= 12 for step in question['steps'])
        assert sum(len(step['narration'].split()) for step in question['steps']) >= 65


@pytest.mark.parametrize('value', [True, 0, -1, float('inf'), float('nan')])
def test_invalid_question_timing_is_rejected(tmp_path, value):
    questions = load_practice()
    next(iter(questions.values()))['question_seconds'] = value
    path = tmp_path / 'invalid.yaml'
    path.write_text(yaml.safe_dump({'version': 1, 'questions': questions}), encoding='utf-8')
    with pytest.raises(ValueError):
        load_practice(path)


def test_new_practice_answers_independently():
    assert (-2)**2 - Fraction(3, 2) / Fraction(3, 4) == 2
    assert (2**2 - 2 - 2, (-1)**2 - (-1) - 2) == (0, 0)
    assert Fraction(2 + 2, 2 + 1) == Fraction(4, 3)
    assert Fraction(6, 10) + Fraction(5, 10) - Fraction(2, 10) == Fraction(9, 10)
    assert 1 - Fraction(9, 10) == Fraction(1, 10)
    t = 1
    x, y, z = 1 + 2*t, t, 2 - t
    assert (x, y, z) == (3, 1, 1) and x + 2*y - z + 1 == 5
    d, dx, dy = 1*(-1) - 2*3, 5*(-1) - 2*1, 1*1 - 5*3
    assert (d, dx, dy) == (-7, -7, -14)
    assert (Fraction(dx, d), Fraction(dy, d)) == (1, 2)
    assert 1 + 2*2 == 5 and 3*1 - 2 == 1
    assert 2 + 3 == 5 and 2*2 - 3 == 1
    vertices = [(0, 0), (2, 0), (2, 2), (0, 4)]
    assert [2*x + 3*y for x, y in vertices] == [0, 4, 10, 12]
    assert all(x >= 0 and y >= 0 and x + y <= 4 and x <= 2 for x, y in vertices)
    assert 13**2 - 12**2 == 5**2
    assert Fraction(5, 13)**2 + Fraction(12, 13)**2 == 1
    assert 3**2 + 5**2 - 2*3*5*Fraction(1, 2) == 19
    assert 2 < math.sqrt(19) < 8
    for sign in (-1, 1):
        for k in range(-3, 4):
            assert math.cos(sign*2*math.pi/3 + 2*k*math.pi) == pytest.approx(-0.5)

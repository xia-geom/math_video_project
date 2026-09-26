"""Real MathTex geometry and actual reveal order, with no speech synthesis."""
import pytest
from manim import RIGHT, MathTex, tempconfig

from tools.expanded_teaching import ExpandedTeachingScene, check_panels, check_visible_objects
from tools.lesson_practice import load_practice
from tools.teaching_layout import BODY_HEIGHT, panel


@pytest.fixture(autouse=True)
def local_tex(tmp_path):
    (tmp_path / 'Tex').mkdir()
    with tempconfig({'media_dir': str(tmp_path), 'tex_dir': str(tmp_path / 'Tex')}):
        yield


@pytest.mark.parametrize('lesson_id', list(load_practice()))
def test_practice_geometry_and_question_before_any_answer(lesson_id):
    scene = object.__new__(ExpandedTeachingScene)
    scene.page = None
    scene.practice_questions = 0
    scene.practice_solution_steps = 0
    scene.play = lambda *args, **kwargs: None
    scene.remove = lambda *args: None
    reveals = []
    scene.explain = lambda text, *objects, **kwargs: reveals.append((objects, kwargs))
    question = load_practice()[lesson_id]
    scene.practice_question(question)
    assert len(reveals) == 4
    premise = reveals[0][0][0]
    assert len(reveals[0][0]) == 1
    assert premise[1].tex_string == question['premise']
    assert reveals[0][1]['hold'] == 18 and reveals[0][1]['pause_after'] == 12
    assert scene.page[1].height <= BODY_HEIGHT
    for (objects, _), step in zip(reveals[1:], question['steps']):
        assert len(objects) == 1 and objects[0][1].tex_string == step['math']
        assert check_visible_objects(objects) == 1
    assert scene.practice_questions == 1 and scene.practice_solution_steps == 3
    assert check_panels(scene.page) == 2


def test_late_reveal_is_checked_even_when_absent_from_saved_page():
    late_label = MathTex('x=2', font_size=38).shift(8*RIGHT)
    with pytest.raises(ValueError, match='safe margin'):
        check_visible_objects([late_label])


def test_panel_retains_the_authored_gutter_after_construction():
    card = panel(MathTex('x=2', font_size=38), width=1, height=1, padding=0.34)
    assert check_panels(card) == 1
    card[1].shift(0.1*RIGHT)
    # Still within the border, but no longer within the required reading gutter.
    with pytest.raises(ValueError, match='outside its panel'):
        check_panels(card)

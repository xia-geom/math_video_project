"""Regressions for actual defects found in the globally numbered previews."""
from __future__ import annotations

import ast
import importlib.util
import re
import sys

import pytest

from tools.course_catalog import ROOT, load_catalog, resolve


def test_opening_titles_do_not_restart_module_numbering():
    for entry in load_catalog()[1]:
        tree = ast.parse((ROOT / entry['scene_file']).read_text())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'Text'
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                assert not re.match(r'^(Matrices|Vecteurs)\s+\d+\b', node.args[0].value), entry['lesson_id']


@pytest.mark.parametrize('formula,instruction', [
    (r'\sum_{i=a}^{b}f(i)', 'calculer f(i), puis additionner'),
    (r'\prod_{i=a}^{b}f(i)', 'calculer f(i), puis multiplier'),
])
def test_sigma_summary_card_encloses_its_instruction(tmp_path, formula, instruction):
    manim = pytest.importorskip('manim')
    from tools.teaching_layout import assert_inside
    entry = resolve('notation_sigma', load_catalog()[1])
    spec = importlib.util.spec_from_file_location('sigma_card_regression', ROOT / entry['scene_file'])
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    with manim.tempconfig({'media_dir': str(tmp_path / 'media')}):
        card = module.SigmaSommeBoucleFR._operation_card('Somme', formula, instruction)
    for member in card.submobjects[1:]:
        assert_inside(member, card[0], padding=0.24)


@pytest.fixture(scope='module')
def reviewed_states(tmp_path_factory):
    pytest.importorskip('manim')
    from scripts.teaching_revision.review import audit_one
    import os
    previous = os.environ.get('MANIM_DISABLE_VOICEOVER')
    os.environ['MANIM_DISABLE_VOICEOVER'] = '1'
    output = tmp_path_factory.mktemp('followup-construction')
    states = {}
    try:
        for lesson in ('operations_sur_les_vecteurs', 'lire_et_appliquer_une_matrice', 'notation_sigma'):
            result = audit_one(resolve(lesson, load_catalog()[1]), output / lesson)
            assert result['construction'] == 'passed', result.get('error')
            states[lesson] = result['states']
        yield states
    finally:
        if previous is None:
            os.environ.pop('MANIM_DISABLE_VOICEOVER', None)
        else:
            os.environ['MANIM_DISABLE_VOICEOVER'] = previous


@pytest.mark.parametrize('lesson,first,second', [
    ('operations_sur_les_vecteurs', r'-\vec v=(1,-2)', r'\vec u-\vec v'),
    ('lire_et_appliquer_une_matrice', 'recetteA', 'recetteB'),
    ('notation_sigma', 'Sigma:additionner', r'\prod_{i=1}^{4}i = 1\cdot2\cdot3\cdot4 = 24'),
])
def test_confirmed_label_pairs_no_longer_collide(reviewed_states, lesson, first, second):
    seen = 0

    def clean(value):
        return re.sub(r'\s+', '', value)

    for state in reviewed_states[lesson]:
        labels = {clean(label['text']): label['box'] for label in state['labels']}
        a, b = labels.get(clean(first)), labels.get(clean(second))
        if a is not None and b is not None:
            seen += 1
            dx = min(a[1], b[1]) - max(a[0], b[0])
            dy = min(a[3], b[3]) - max(a[2], b[2])
            assert dx <= 0 or dy <= 0, (lesson, state['time'], a, b)
    assert seen > 0, 'The regression must actually encounter both target labels.'


def test_matrix_dimension_annotation_is_not_clipped(reviewed_states):
    matching = [label for state in reviewed_states['lire_et_appliquer_une_matrice']
                for label in state['labels'] if '2colonnes' in re.sub(r'\s+', '', label['text'])]
    assert matching
    for label in matching:
        assert -6.62 <= label['box'][0] < label['box'][1] <= 6.62

"""Construct the two clipped/crowded scenes and check the actual target labels."""
import os
import re

import pytest

from tools.course_catalog import load_catalog, resolve


def normalized(value):
    return re.sub(r'\s+', '', value)


@pytest.fixture(scope='module')
def states(tmp_path_factory):
    pytest.importorskip('manim')
    from scripts.teaching_revision.review import audit_one
    output = tmp_path_factory.mktemp('course-boundaries')
    previous = os.environ.get('MANIM_DISABLE_VOICEOVER')
    os.environ['MANIM_DISABLE_VOICEOVER'] = '1'
    try:
        result = {}
        for alias in ('P03', 'P18'):
            data = audit_one(resolve(alias, load_catalog()[1]), output / alias)
            assert data['construction'] == 'passed', data.get('error')
            result[alias] = data['states']
        yield result
    finally:
        if previous is None:
            os.environ.pop('MANIM_DISABLE_VOICEOVER', None)
        else:
            os.environ['MANIM_DISABLE_VOICEOVER'] = previous


def test_equation_and_root_prose_stays_in_its_own_card(states):
    left = {'Résoudreuneéquation', 'Quelsnombresontpourcarré16?', 'Oncherchetouteslessolutions.'}
    right = {'Évalueruneracinecarrée', 'Quellevaleurdésignelesymbole?', 'Uneseulevaleur,nonnégative.'}
    seen = set()
    for state in states['P03']:
        labels = {normalized(label['text']): label['box'] for label in state['labels']}
        if 'Deuxquestionsdifférentes' not in labels:
            continue
        for text in (left | right) & labels.keys():
            seen.add(text)
            x1, x2, y1, y2 = labels[text]
            low, high = (-5.97, -0.43) if text in left else (0.43, 5.97)
            assert low <= x1 < x2 <= high, (text, state['time'], labels[text])
            assert -2.92 <= y1 < y2 <= 2.22, (text, state['time'], labels[text])
    assert seen == left | right


@pytest.mark.parametrize('text', [
    'mêmedirectionmêmesensmêmelongueur', 'Lanormeestlalongueurduvecteur.',
])
def test_vector_annotations_stay_in_the_right_panel(states, text):
    matching = [label for state in states['P18'] for label in state['labels']
                if normalized(label['text']) == text]
    assert matching
    for label in matching:
        x1, x2, _, _ = label['box']
        assert 1.10 <= x1 < x2 <= 6.62, label


@pytest.mark.parametrize('alias', ['P03', 'P18'])
def test_no_stable_label_crosses_the_physical_frame(states, alias):
    for state in states[alias]:
        for label in state['labels']:
            x1, x2, y1, y2 = label['box']
            assert -7.12 <= x1 <= x2 <= 7.12, (alias, state['time'], label)
            assert -4.01 <= y1 <= y2 <= 4.01, (alias, state['time'], label)

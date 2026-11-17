"""Authored-course pronunciation contracts; no Manim, synthesis, or listening."""
from __future__ import annotations

import ast
import re
from functools import lru_cache
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
import yaml

from tools import tts
from tools.course_catalog import load_catalog, resolve

ROOT = Path(__file__).resolve().parents[1]
REPORTED_LESSONS = (23, 27, 28, 29, 30, 31)


class _NotLiteral(Exception):
    pass


def _value(node, names):
    """Read literal narration expressions without importing a scene or executing it."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in names:
        return names[node.id]
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        if node.value.id == 'tts':
            return getattr(tts, node.attr)
    if isinstance(node, (ast.Tuple, ast.List)):
        return [_value(item, names) for item in node.elts]
    if isinstance(node, ast.Dict):
        return {_value(key, names): _value(value, names)
                for key, value in zip(node.keys, node.values)}
    if isinstance(node, ast.JoinedStr):
        return ''.join(str(_value(item, names)) for item in node.values)
    if isinstance(node, ast.FormattedValue) and node.format_spec is None:
        return _value(node.value, names)
    if isinstance(node, ast.Call):
        function = _value(node.func, names)
        if function in (tts.char, tts.chars, tts.ssml):
            return function(*[_value(arg, names) for arg in node.args],
                            **{kw.arg: _value(kw.value, names) for kw in node.keywords})
    raise _NotLiteral(ast.dump(node))


@lru_cache(maxsize=None)
def _lesson_speech(number):
    entry = resolve(str(number), load_catalog()[1])
    tree = ast.parse((ROOT / entry['scene_file']).read_text(encoding='utf-8'))
    names = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        try:
            value = _value(node.value, names)
        except _NotLiteral:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                names[target.id] = value
            elif isinstance(target, ast.Tuple):
                names.update((part.id, item) for part, item in zip(target.elts, value))

    speech = []
    if number in (23, 31):
        speech.extend(names['SCRIPT'].values())
    elif number == 27:
        speech.extend(item['ssml'] for item in names['SCRIPT'])
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'explain':
                speech.append(_value(node.args[0], names))
            for keyword in node.keywords:
                if keyword.arg in {'recap_spoken', 'practice_spoken'}:
                    speech.append(_value(keyword.value, names))
    assert speech, entry['lesson_id']
    return speech


def _unmarked_text(text):
    def visit(element):
        if element.tag in {'sub', 'say-as', 'phoneme'}:
            return ''
        return (element.text or '') + ''.join(
            visit(child) + (child.tail or '') for child in element)

    return visit(ET.fromstring('<root>' + text + '</root>'))


def _check_authored_speech(text):
    tts.validate_pronunciation(text)
    # These are ordinary French pronouns in the selected lessons/data, not symbols.
    unmarked = re.sub(r"\bn[’']y\b|\bil y\b|\by compris\b|\by atteint\b", '',
                      _unmarked_text(text), flags=re.IGNORECASE)
    assert not re.search(r'\by\b', unmarked), text


@pytest.mark.parametrize('number', REPORTED_LESSONS)
def test_reported_lessons_mark_math_y_and_have_no_vowel_collisions(number):
    for text in _lesson_speech(number):
        _check_authored_speech(text)


@pytest.mark.parametrize(('number', 'expected'), [
    (23, 'trois dans la direction iks, deux dans la direction i grec'),
    (27, "Puis l'inverse de a applique"),
    (28, 'moins deux fois moins i grec donne plus deux i grec'),
    (29, 'Le quotient donne i grec égal à un.'),
    (30, 'trois iks plus deux i grec'),
    (31, 'i grec égale sinus de thêta'),
])
def test_reported_phrases_reach_the_shared_spoken_form(number, expected):
    prepared = ' '.join(tts.prepare_math_speech(text) for text in _lesson_speech(number))
    assert expected in prepared


def test_coordinate_wording_and_natural_french_y_are_preserved():
    coordinates = ' '.join(tts.strip_ssml(text) for text in _lesson_speech(23))
    assert 'Les coordonnées du point A sont moins deux, moins un.' in coordinates
    assert 'Les coordonnées du point B sont deux, deux.' in coordinates
    natural = 'Un objectif linéaire y atteint un maximum à au moins un sommet.'
    speech = _lesson_speech(30)
    assert any(natural in text for text in speech)
    assert any(natural in tts.prepare_math_speech(text) for text in speech)


def _data_speech(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in {'prompt', 'narration'}:
                yield value
            else:
                yield from _data_speech(value)
    elif isinstance(node, list):
        for item in node:
            yield from _data_speech(item)


def test_worked_examples_and_practice_use_the_same_pronunciation_contract():
    paths = [*(ROOT / 'curriculum/worked_examples').glob('*.yaml'),
             ROOT / 'curriculum/practice_questions.yaml']
    speech = [text for path in paths
              for text in _data_speech(yaml.safe_load(path.read_text(encoding='utf-8')))]
    assert speech
    for text in speech:
        _check_authored_speech(text)
    for natural in ('Il n’y a pas toujours', 'y compris le point trois-deux'):
        assert any(natural in text for text in speech)
        assert any(natural in tts.prepare_math_speech(text) for text in speech)

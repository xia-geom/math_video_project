"""Spoken notation and profile regressions; no synthesis or listening claim."""
from __future__ import annotations

import importlib.util
import re
import sys
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools import tts
from tools.course_catalog import load_catalog, resolve

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def variables_module(monkeypatch):
    pytest.importorskip('manim')
    from manim import tempconfig

    from tools.teaching_voiceover import TeachingAzureService

    def forbidden(*args, **kwargs):
        raise AssertionError('Offline narration checks must not initialize Azure.')

    monkeypatch.setenv('MANIM_DISABLE_VOICEOVER', '1')
    monkeypatch.setattr(TeachingAzureService, '__init__', forbidden)
    entry = resolve('variables_et_polynomes', load_catalog()[1])
    spec = importlib.util.spec_from_file_location('variables_narration_test',
                                                ROOT / entry['scene_file'])
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    with tempconfig({}):
        spec.loader.exec_module(module)
        yield module


def spoken_words(ssml):
    root = ET.fromstring(ssml)
    return ' '.join(' '.join(root.itertext()).split())


def test_polynomial_narration_distinguishes_indices_and_products(variables_module):
    text = spoken_words(variables_module.SSML_3C)
    assert re.findall(r'a indice (zéro|un|deux|n)', text) == ['zéro', 'un', 'deux', 'n']
    for product in ('a indice un, multiplié par x',
                    'a indice deux, multiplié par x au carré',
                    'a indice n , multiplié par x à la puissance n'):
        assert product in text
    coefficients = spoken_words(variables_module.SSML_3D)
    assert 'constantes' in coefficients
    assert 'fixées lorsque x varie' in coefficients
    assert '...' not in coefficients and '…' not in coefficients


@pytest.mark.parametrize('explicit', [False, True])
def test_plain_cards_use_body_profile_without_rewrapping_ssml(variables_module, explicit):
    requests = []
    sentinel = object()

    @contextmanager
    def voiceover(**kwargs):
        requests.append(kwargs)
        yield sentinel

    fake = SimpleNamespace(_voiceover_enabled=True, voiceover=voiceover)
    caption = 'Passons aux coefficients.'
    supplied = tts.ssml(tts.char('x') + ' varie.') if explicit else None
    with variables_module.VariablesEtPolynomes.narrated(fake, caption, ssml=supplied) as result:
        assert result is sentinel
    request = requests[0]
    assert request['subcaption'] == caption
    expected = supplied if explicit else tts.ssml(caption)
    assert request['text'] == expected
    root = ET.fromstring(request['text'])
    assert root.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == tts.VOICE_LOCALE
    assert len(root.findall('.//prosody')) == 1
    assert root.find('prosody').attrib['rate'] == tts.VOICE_RATE


def test_silent_card_never_requests_speech(variables_module):
    def forbidden(**kwargs):
        raise AssertionError('Silent mode must not request speech.')

    fake = SimpleNamespace(_voiceover_enabled=False, voiceover=forbidden)
    with variables_module.VariablesEtPolynomes.narrated(fake, 'À retenir.') as tracker:
        assert tracker.duration == 0

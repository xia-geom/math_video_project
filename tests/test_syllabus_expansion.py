"""Focused candidate contracts and worked examples; not a release certification."""
import ast
import importlib.util
import math
from fractions import Fraction

import pytest

from scripts.render_syllabus_expansion import (
    ROOT, inspect_streams, read_candidates, select_candidates,
)


@pytest.fixture(scope='module')
def entries():
    return read_candidates()[1]


@pytest.fixture(scope='module')
def modules(entries):
    result = {}
    for entry in entries:
        spec = importlib.util.spec_from_file_location(entry['id'], ROOT / entry['scene_file'])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result[entry['id']] = module
    return result


def test_required_gaps_and_optional_complex_numbers(entries):
    data, _ = read_candidates()
    assert {e['id'] for e in entries} == {f'S{i:02d}' for i in range(1, 11)}
    assert [e['order'] for e in entries] == sorted(e['order'] for e in entries)
    assert data['optional'] == [{'id': 'S11', 'title': 'Initiation aux nombres complexes',
                                'status': 'planned_optional',
                                'reason': 'Le plan source qualifie explicitement cette initiation de facultative.'}]
    assert data['release_ready'] is False


def test_selection_is_explicit(entries):
    assert [e['id'] for e in select_candidates(entries, 'S02,S01')] == ['S01', 'S02']
    with pytest.raises(ValueError):
        select_candidates(entries, 'S99')


@pytest.mark.parametrize('candidate', [f'S{i:02d}' for i in range(1, 11)])
def test_shared_contract_and_single_opening(entries, modules, candidate):
    from tools.teaching_layout import TeachingScene
    entry = next(e for e in entries if e['id'] == candidate)
    cls = getattr(modules[candidate], entry['scene_class'])
    assert issubclass(cls, TeachingScene)
    tree = ast.parse((ROOT / entry['scene_file']).read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    assert sum(isinstance(n.func, ast.Name) and n.func.id == 'play_uqam_intro' for n in calls) == 1
    assert sum(isinstance(n.func, ast.Attribute) and n.func.attr == 'setup_narration' for n in calls) == 1
    assert sum(isinstance(n.func, ast.Attribute) and n.func.attr == 'new_page' for n in calls) >= 6
    assert not any(isinstance(n.func, ast.Name) and n.func.id in
                   {'AzureService', 'TeachingAzureService', 'TransformMatchingTex'} for n in calls)


def test_real_operation_examples(modules):
    assert -2 ** 2 + Fraction(1, 2) / Fraction(1, 4) == -2
    assert Fraction(1, 2) + Fraction(1, 3) == Fraction(5, 6)
    assert -3 ** 2 == -9 and (-3) ** 2 == 9
    with pytest.raises(ValueError):
        modules['S01'].sixths(7)


def test_rational_domain_and_one_sided_behavior(modules):
    f = modules['S02'].rational_value
    with pytest.raises(ValueError):
        f(1)
    for x in (-10, -2, 0, 2, 10):
        assert f(x) == pytest.approx(1 + 2 / (x - 1))
    assert f(0.999) < -1000 and f(1.001) > 1000
    assert f(1_000_001) == pytest.approx(1.000002)


def test_probability_model_not_just_counting(modules):
    m = modules['S03']
    assert m.event_probability(m.EVEN, m.FAIR_WEIGHTS) == Fraction(1, 2)
    assert m.event_probability(m.EVEN, m.BIASED_WEIGHTS) == Fraction(7, 10)
    assert m.event_probability(m.EVEN | m.LARGE, m.FAIR_WEIGHTS) == Fraction(2, 3)
    assert m.event_probability(m.EVEN & m.LARGE, m.FAIR_WEIGHTS) == Fraction(1, 3)
    assert m.event_probability([], m.FAIR_WEIGHTS) == 0
    with pytest.raises(ValueError):
        m.event_probability({7}, m.FAIR_WEIGHTS)
    with pytest.raises(ValueError):
        m.event_probability({1}, (Fraction(1, 2),) * 6)


def test_line_and_plane_membership(modules):
    m = modules['S04']
    for t in (-3, 0, 1, Fraction(3, 2)):
        assert m.line_value(1 + 2 * t, 2 - t) == 0
    assert m.plane_value(3, 0, 4) == 0
    assert m.plane_value(3, 0, 3) != 0
    assert m.plane_value(1, 1, 4) == 0


def test_cramer_solution_and_singular_guard(modules):
    m = modules['S05']
    assert m.determinant(m.MATRIX) == -3
    x, y = m.cramer(m.MATRIX, m.RHS)
    assert (x, y) == (2, 1)
    for row, rhs in zip(m.MATRIX, m.RHS):
        assert row[0] * x + row[1] * y == rhs
    with pytest.raises(ValueError):
        m.cramer(((1, 1), (2, 2)), (2, 4))
    with pytest.raises(ValueError):
        m.cramer(((1, 1), (2, 2)), (2, 5))


def test_elimination_applies_to_the_rhs_too(modules):
    eliminate = modules['S06'].eliminate_first_row
    assert eliminate((2, 1, 5), (1, -1, 1), 2) == (0, 3, 3)
    assert eliminate((2, 2, 4), (1, 1, 2), 2) == (0, 0, 0)
    assert eliminate((2, 2, 5), (1, 1, 2), 2) == (0, 0, 1)


def test_linear_program_certificate(modules):
    m = modules['S07']
    assert all(m.feasible(*p) for p in m.VERTICES)
    assert [m.objective_value(*p) for p in m.VERTICES] == [0, 12, 14, 12, 6]
    assert not m.feasible(4, 3)
    # Independent algebraic certificate, sampled on a rational grid as regression.
    for i in range(41):
        for j in range(31):
            x, y = Fraction(i, 10), Fraction(j, 10)
            if m.feasible(x, y):
                assert m.objective_value(x, y) == 2 * (x + y) + x <= 14


def test_triangle_examples_and_degenerate_guard(modules):
    assert Fraction(3, 5) ** 2 + Fraction(4, 5) ** 2 == 1
    assert 2 * math.sin(math.pi / 4) / math.sin(math.pi / 6) == pytest.approx(2 * math.sqrt(2))
    f = modules['S09'].cosine_side
    assert f(3, 4, math.pi / 3) == pytest.approx(math.sqrt(13))
    assert f(3, 4, math.pi / 2) == pytest.approx(5)
    with pytest.raises(ValueError):
        f(3, 4, 0)


def test_inverse_trigonometric_branch_examples():
    assert math.asin(math.sin(5 * math.pi / 6)) == pytest.approx(math.pi / 6)
    assert math.acos(-0.5) == pytest.approx(2 * math.pi / 3)
    with pytest.raises(ValueError):
        math.asin(2)


def test_stream_contract_does_not_certify_fake_narration():
    info = {'streams': [{'codec_type': 'video', 'width': 854, 'height': 480,
                         'r_frame_rate': '15/1'}], 'format': {'duration': '30'}}
    assert inspect_streams(info, 'silent') == (30, False)
    with pytest.raises(ValueError):
        inspect_streams(info, 'azure')
    info['streams'].append({'codec_type': 'audio'})
    assert inspect_streams(info, 'azure') == (30, True)
    with pytest.raises(ValueError):
        inspect_streams(info, 'silent')


def test_shared_services_select_silence_before_azure(monkeypatch):
    from tools import teaching_layout
    monkeypatch.setenv('MANIM_DISABLE_VOICEOVER', '1')
    def forbidden(*args, **kwargs):
        raise AssertionError('Silent setup must not construct a cloud service.')
    monkeypatch.setattr(teaching_layout, 'TeachingAzureService', forbidden)
    scene = object.__new__(teaching_layout.TeachingScene)
    scene.setup_narration()
    assert scene.silent is True


def test_shared_services_preserve_real_narration_route(monkeypatch):
    from tools import teaching_layout
    monkeypatch.setenv('MANIM_DISABLE_VOICEOVER', '0')
    calls = []
    service = object()
    monkeypatch.setattr(teaching_layout.tts, 'configure_azure_speech_environment',
                        lambda **kw: calls.append(kw))
    monkeypatch.setattr(teaching_layout, 'TeachingAzureService', lambda: service)
    scene = object.__new__(teaching_layout.TeachingScene)
    scene.set_speech_service = lambda value: calls.append(value)
    scene.setup_narration()
    assert scene.silent is False
    assert calls == [{'require_credentials': True}, service]


@pytest.mark.parametrize('candidate', [f'S{i:02d}' for i in range(1, 11)])
def test_all_titles_and_plain_text_fit_without_shrinking(entries, candidate):
    from manim import Text
    from tools.teaching_layout import BODY_WIDTH
    entry = next(e for e in entries if e['id'] == candidate)
    tree = ast.parse((ROOT / entry['scene_file']).read_text())
    failures = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in {'new_page', 'words'} and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            continue
        text = node.args[0].value
        size = 40 if node.func.attr == 'new_page' else 30
        if node.func.attr == 'words' and len(node.args) > 1:
            size = ast.literal_eval(node.args[1])
        width = Text(text, font_size=size).width
        if width > BODY_WIDTH:
            failures.append(f'{text!r}: {width:.2f} > {BODY_WIDTH}')
    assert not failures, '\n'.join(failures)

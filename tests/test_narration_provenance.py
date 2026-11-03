"""Narration evidence must describe observed requests/use and survive cleanup."""
from __future__ import annotations

import json
import shutil
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.narration_provenance import (
    NarrationCapture,
    digest,
    narration_tooling_hashes,
    seal_capture,
    validate_capture,
    verify_narration_manifest,
)

SSML = '''<speak xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="fr-CA-JeanNeural"><lang xml:lang="fr-CA"><prosody rate="+8%">
Bonjour.<lang xml:lang="fr-FR"><prosody rate="-20%">Fin.</prosody></lang>
</prosody></lang></voice></speak>'''


def request_data(cache):
    cache.mkdir(parents=True, exist_ok=True)
    (cache / 'spoken.mp3').write_bytes(b'fixture-generated-audio')
    return {'input_text': 'Bonjour. Fin.', 'ssml': SSML,
            'input_data': {'service': 'azure', 'ssml': SSML, 'input_text': 'Bonjour. Fin.',
                           'config': {'voice': 'fr-CA-JeanNeural', 'style': None,
                                      'prosody': None, 'output_format': 'observed-format'},
                           'credential': 'MUST_NOT_BE_RETAINED'},
            'original_audio': 'spoken.mp3', 'final_audio': 'spoken.mp3',
            'timing_basis': 'measured_pcm_fragments', 'sample_rate': 48000,
            'bookmark_anchors': {'a': {'sample': 12000, 'seconds': 0.25}},
            'word_boundaries': [{'audio_offset': 2500000, 'text_offset': 8,
                                 'boundary_type': 'AuthoredBookmarkAnchor'}],
            'clips': [{'audio': 'spoken.mp3', 'start_sample': 0, 'samples': 24000}],
            'arbitrary_sdk_payload': 'MUST_NOT_BE_RETAINED'}


def captured_fixture(destination, cache):
    capture = NarrationCapture(destination)
    data = request_data(cache)
    service = SimpleNamespace(cache_dir=cache, voice='fr-CA-JeanNeural', style=None,
                              prosody=None, output_format='observed-format', global_speed=1)
    scene = SimpleNamespace(speech_service=service)
    tracker = SimpleNamespace(data=data, start_t=2, end_t=2.5, duration=0.5,
                              bookmark_times={'a': 2.25})
    capture.adapter_return(service, data, None)
    capture.voiceover(scene, tracker)
    capture.data['scenes'] = [{'render_completed': True}]
    capture.save()
    return capture


def test_retains_actual_nondefault_ssml_scopes_audio_and_anchors(tmp_path, monkeypatch):
    monkeypatch.setenv('SPEECH_KEY', 'MUST_NOT_BE_RETAINED')
    capture = captured_fixture(tmp_path / 'narration', tmp_path / 'media' / 'voiceovers')
    serialized = (capture.destination / 'provenance.json').read_text()
    assert 'MUST_NOT_BE_RETAINED' not in serialized
    request = capture.data['adapter_returns'][0]
    assert request['requested_configuration']['voice'] == 'fr-CA-JeanNeural'
    assert {v['rate'] for v in request['directives'] if 'rate' in v} == {'+8%', '-20%'}
    assert {v['locale'] for v in request['directives'] if 'locale' in v} == {'en-US', 'fr-CA', 'fr-FR'}
    voiceover = capture.data['voiceovers'][0]
    assert voiceover['bookmark_anchors']['a'] == {'sample': 12000, 'seconds': 0.25}
    assert voiceover['tracker_bookmark_times']['a'] == 2.25
    assert voiceover['final_audio']['sha256'] == digest(tmp_path / 'media/voiceovers/spoken.mp3')
    assert capture.data['listening'] == 'not_performed'
    assert validate_capture(capture.destination)['voiceovers'] == 1


def test_deleted_or_changed_referenced_audio_fails_integrity(tmp_path):
    capture = captured_fixture(tmp_path / 'narration', tmp_path / 'cache')
    audio = capture.destination / capture.data['voiceovers'][0]['final_audio']['path']
    audio.write_bytes(b'changed')
    with pytest.raises(ValueError, match='integrity'):
        validate_capture(capture.destination)
    audio.unlink()
    with pytest.raises(ValueError, match='integrity'):
        validate_capture(capture.destination)


def test_unknown_profile_is_not_replaced_with_defaults_and_cache_escape_rejected(tmp_path):
    capture = NarrationCapture(tmp_path / 'narration')
    data = request_data(tmp_path / 'cache')
    data['input_data']['config'] = {}
    capture.adapter_return(SimpleNamespace(cache_dir=tmp_path / 'cache'), data, None)
    assert all(value is None for value in capture.data['adapter_returns'][0]['requested_configuration'].values())
    (tmp_path / 'outside.mp3').write_bytes(b'not-authorized-cache-audio')
    with pytest.raises(ValueError, match='inside'):
        capture.retain_audio(tmp_path / 'cache', '../outside.mp3')


def test_observer_records_executed_pacing_and_restores_methods(tmp_path, monkeypatch):
    # Execute the original methods through all three wrappers. Environment says
    # 9, but actual scene setup uses 1.7; evidence must report the observed value.
    monkeypatch.setenv('PACE_FACTOR', '9')
    cache = tmp_path / 'cache'
    data = request_data(cache)

    class Adapter:
        cache_dir = cache

        def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
            return data

    class Scene:
        def render(self):
            self.pace_factor = 1.7
            assert self._paced_time(2) == 3.4
            return self.add_voiceover_text('Bonjour')

        def _paced_time(self, value):
            return value * self.pace_factor

    class Voiceover(Scene):
        speech_service = Adapter()

        def add_voiceover_text(self, text):
            actual = self.speech_service.generate_from_text(text)
            return SimpleNamespace(data=actual, start_t=2, end_t=2.5, duration=0.5)

    before = (Scene.render, Voiceover.add_voiceover_text, Adapter.generate_from_text)
    capture = NarrationCapture(tmp_path / 'narration')
    scene = Voiceover()
    with capture.observe(Scene, Voiceover, Adapter):
        tracker = scene.render()
    assert tracker.data is data
    assert (Scene.render, Voiceover.add_voiceover_text, Adapter.generate_from_text) == before
    assert '_paced_time' not in scene.__dict__
    record = capture.data['scenes'][0]['pace_factor']
    assert record['used'] is True and record['observed_factor'] == 1.7
    assert record['calls'] == [{'input_seconds': 2, 'output_seconds': 3.4, 'factor': 1.7}]
    assert capture.data['pace_factor_environment']['numeric_value'] == 9
    assert validate_capture(capture.destination)['adapter_returns'] == 1


def test_observer_does_not_claim_unused_pacing_or_success_after_exception(tmp_path):
    class Scene:
        def render(self):
            raise RuntimeError('fixture')

    class Voiceover(Scene):
        def add_voiceover_text(self, text):
            raise AssertionError('unused')

    class Adapter:
        def generate_from_text(self, text, **kwargs):
            raise AssertionError('unused')

    capture = NarrationCapture(tmp_path / 'narration')
    original = Scene.render
    with pytest.raises(RuntimeError, match='fixture'), capture.observe(Scene, Voiceover, Adapter):
        Scene().render()
    assert Scene.render is original
    assert capture.data['scenes'][0]['pace_factor']['used'] is False
    assert capture.data['scenes'][0]['render_completed'] is False
    with pytest.raises(ValueError, match='completed'):
        validate_capture(capture.destination)


@pytest.mark.parametrize(('retain_evidence', 'changed_tooling'), [
    (True, None), (False, None),
    (True, 'tools/narration_provenance.py'),
    (True, 'scripts/render_narrated_review.py'),
])
def test_real_runner_requires_provenance_before_deleting_media(
        tmp_path, monkeypatch, retain_evidence, changed_tooling):
    from scripts import render_syllabus_expansion as runner
    root, output = tmp_path / 'repo', tmp_path / 'output'
    output.mkdir()
    names = {*runner.SHARED, 'lesson.py', 'tools/narration_provenance.py',
             'scripts/render_narrated_review.py'}
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('fixture')
    monkeypatch.setattr(runner, 'ROOT', root)
    monkeypatch.setattr(runner, 'input_hashes', lambda entry: {'lesson.py': digest(root / 'lesson.py')})
    monkeypatch.setattr(runner, 'load_duration_policy', dict)
    monkeypatch.setattr(runner, 'assess_duration', lambda *args, **kwargs: {'status': 'unconfigured'})
    info = {'streams': [{'codec_type': 'video', 'width': 1920, 'height': 1080,
                         'r_frame_rate': '60/1'}, {'codec_type': 'audio'}],
            'format': {'duration': '20'}}

    def check_output(args, **kwargs):
        if args[0] == 'ffprobe':
            return json.dumps(info).encode()
        return '' if args[1] == 'status' else 'test-commit'

    def run(args, **kwargs):
        if '-m' in args:
            assert args[args.index('-m') + 1] == 'scripts.render_narrated_review'
            media = Path(args[args.index('--media_dir') + 1])
            stem = args[args.index('-o') + 1]
            (media / 'videos').mkdir(parents=True)
            (media / 'videos' / (stem + '.mp4')).write_bytes(b'encoded-fixture')
            if retain_evidence:
                captured_fixture(Path(kwargs['env']['TEACHING_NARRATION_EVIDENCE_PATH']),
                                 media / 'voiceovers')
            if changed_tooling:
                (root / changed_tooling).write_text('changed while Manim child was running')
        elif args[-1].endswith('.m4a'):
            assert args[args.index('-c:a') + 1] == 'copy'
            Path(args[-1]).write_bytes(b'encoded-audio-fixture')
        else:
            Path(args[-1].replace('%04d', '0001')).write_bytes(b'frame-fixture')
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, 'check_output', check_output)
    monkeypatch.setattr(runner.subprocess, 'run', run)
    entry = {'order': 16, 'delivery_slug': 'fixture', 'legacy_id': 'P16',
             'lesson_id': 'fixture', 'scene_file': 'lesson.py', 'scene_class': 'Fixture'}
    result = runner.render_one(entry, output, 'azure', 'qh')
    dest = output / '16_fixture'
    if retain_evidence and not changed_tooling:
        assert result['render'] == 'passed'
        assert not (dest / 'media').exists()
        assert validate_capture(dest / 'narration')['voiceovers'] == 1
        assert digest(dest / result['encoded_audio']['path']) == result['encoded_audio']['sha256']
    else:
        assert result['render'] == 'failed'
        assert (dest / 'media').exists()
        if changed_tooling:
            assert 'observer tooling changed' in result['error']


def test_teaching_preflight_never_runs_more_than_two_children(tmp_path, monkeypatch):
    from scripts.teaching_revision import validate
    lock = threading.Lock()
    active = peak = 0
    targets = [{'track': 'fixture', 'order': i, 'legacy_id': f'X{i}'} for i in range(4)]

    def fake_call(args, log, **kwargs):
        nonlocal active, peak
        if '--entry' not in args:
            return 0
        with lock:
            active += 1
            peak = max(peak, active)
        time.sleep(0.03)
        with lock:
            active -= 1
        return 0

    monkeypatch.setattr(validate, 'entries', lambda: targets)
    monkeypatch.setattr(validate, 'call', fake_call)
    monkeypatch.setattr(validate.subprocess, 'check_output', lambda *args, **kwargs: b'fixture')
    monkeypatch.setattr('sys.argv', ['validate.py', '--output', str(tmp_path / 'preflight')])
    assert validate.main() == 0
    assert peak == 2


@pytest.mark.parametrize('corruption', ['manifest', 'audio', 'voice', 'pace', 'video', 'inputs'])
def test_audio_reuse_rejects_changed_evidence_or_explicit_context(tmp_path, monkeypatch, corruption):
    monkeypatch.setattr('tools.narration_provenance.audio_runtime', lambda: {'fixture-sdk': '1'})
    monkeypatch.delenv('MANIM_VOICE', raising=False)
    monkeypatch.delenv('PACE_FACTOR', raising=False)
    capture = captured_fixture(tmp_path / 'narration', tmp_path / 'cache')
    audio = capture.destination / 'encoded_audio.m4a'
    audio.write_bytes(b'encoded-audio')
    status = {'narration_evidence': seal_capture(capture.destination, 'video-hash', 'input-signature',
              {'path': 'encoded_audio.m4a', 'sha256': digest(audio)}),
              'encoded_audio': {'path': 'narration/encoded_audio.m4a', 'sha256': digest(audio)}}
    arguments = [tmp_path / 'STATUS.json', status, 'video-hash', 'input-signature']
    assert verify_narration_manifest(*arguments)['status'] == 'verified'
    if corruption == 'manifest':
        (capture.destination / 'provenance.json').write_text('{}')
    elif corruption == 'audio':
        audio.write_bytes(b'changed')
    elif corruption == 'voice':
        monkeypatch.setenv('MANIM_VOICE', 'fr-CA-ThierryNeural')
    elif corruption == 'pace':
        monkeypatch.setenv('PACE_FACTOR', '1.7')
    elif corruption == 'video':
        arguments[2] = 'other-video'
    else:
        arguments[3] = 'other-inputs'
    with pytest.raises(ValueError):
        verify_narration_manifest(*arguments)


@pytest.mark.parametrize('changed_tooling', [
    'tools/narration_provenance.py', 'scripts/render_narrated_review.py'])
def test_current_artifact_import_gates_audio_but_preserves_legacy_silent(
        tmp_path, monkeypatch, changed_tooling):
    from scripts import course_review as review
    from tools.course_review import signature
    monkeypatch.delenv('MANIM_VOICE', raising=False)
    monkeypatch.delenv('PACE_FACTOR', raising=False)
    monkeypatch.setattr('tools.narration_provenance.audio_runtime', lambda: {'fixture-sdk': '1'})
    source = tmp_path / 'lesson.py'
    source.write_text('fixture source')
    inputs = {'lesson.py': digest(source)}
    for name in ('tools/narration_provenance.py', 'scripts/render_narrated_review.py'):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('original tooling')
    film = tmp_path / 'film.mp4'
    film.write_bytes(b'fixture film')
    capture = captured_fixture(tmp_path / 'narration', tmp_path / 'cache')
    audio = capture.destination / 'encoded_audio.m4a'
    audio.write_bytes(b'encoded audio')
    status = {'render': 'passed', 'mode': 'azure_review', 'quality': 'qh',
              'source_sha256': inputs['lesson.py'], 'input_sha256': inputs,
              'runtime_versions': {'fixture-renderer': '1'}, 'video_sha256': digest(film),
              'narration_tooling_sha256': narration_tooling_hashes(tmp_path),
              'narration_evidence': seal_capture(capture.destination, digest(film), signature(inputs),
                  {'path': 'encoded_audio.m4a', 'sha256': digest(audio)}),
              'encoded_audio': {'path': 'narration/encoded_audio.m4a', 'sha256': digest(audio)}}
    media = {'streams': [{'codec_type': 'video', 'width': 1920, 'height': 1080,
                          'r_frame_rate': '60/1'}, {'codec_type': 'audio'}],
             'format': {'duration': '20'}}
    monkeypatch.setattr(review, 'ROOT', tmp_path)
    monkeypatch.setattr(review, 'renderer_runtime_versions', lambda: {'fixture-renderer': '1'})
    monkeypatch.setattr(review.subprocess, 'check_output', lambda *args, **kwargs: json.dumps(media))
    args = [tmp_path / 'STATUS.json', status, {'scene_file': 'lesson.py'}, inputs]
    assert review.inspect_artifact(*args)['provenance'] == 'current'
    monkeypatch.setenv('PACE_FACTOR', '7')
    assert review.inspect_artifact(*args)['provenance'] == 'failed'
    monkeypatch.delenv('PACE_FACTOR')
    (tmp_path / changed_tooling).write_text('observer changed after rendering')
    rejected = review.inspect_artifact(*args)
    assert rejected['provenance'] == 'failed'
    assert 'observer tooling changed' in rejected['error']
    status['mode'] = 'silent_preview'
    status.pop('narration_evidence')
    status.pop('encoded_audio')
    media['streams'].pop()
    imported = review.inspect_artifact(*args)
    assert imported['provenance'] == 'current'
    assert imported['environment_attestation'] == 'legacy_silent_environment_not_attested'


def test_real_voiceover_adapter_first_and_fully_cached_dispatch(tmp_path, monkeypatch):
    """Real adapter/cache/tracker path; stub only cloud synthesis and scene encoding."""
    manim = pytest.importorskip('manim')
    pytest.importorskip('manim_voiceover')
    if shutil.which('ffmpeg') is None:
        pytest.skip('Local audio-fixture encoding requires ffmpeg')
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.azure import AzureService
    from pydub import AudioSegment

    from tools import tts
    from tools.teaching_voiceover import TeachingAzureService

    cache = tmp_path / 'cache'
    cache.mkdir()
    service = object.__new__(TeachingAzureService)
    service.voice, service.style, service.prosody = tts.MAI_VOICE_2, None, None
    service.output_format, service.cache_dir = tts.AZURE_OUTPUT_FORMAT, cache
    service.global_speed, service._whisper_model = 1.0, None
    service.audio_callback = lambda *args, **kwargs: None
    synthesized = []

    def stub_synthesis(self, text, cache_dir=None, path=None, **kwargs):
        name = f'fragment_{len(synthesized)}.mp3'
        synthesized.append(text)
        AudioSegment.silent(duration=700, frame_rate=48000).export(cache / name, format='mp3')
        ssml = f'<speak><voice name="{self.voice}">{text}</voice></speak>'
        return {'input_text': text, 'ssml': ssml, 'original_audio': name,
                'input_data': {'input_text': text, 'ssml': ssml, 'service': 'azure',
                               'config': {'voice': self.voice, 'style': self.style,
                                          'prosody': self.prosody, 'output_format': self.output_format}}}

    monkeypatch.setattr(AzureService, 'generate_from_text', stub_synthesis)
    # Never call a real Scene render. The real VoiceoverScene and tracker still
    # generate/cache/load audio and schedule it through add_sound below.
    monkeypatch.setattr(manim.Scene, 'render', lambda self: self.construct())

    class Probe(VoiceoverScene):
        def _paced_time(self, value):
            return value * self.pace_factor

        def construct(self):
            self.pace_factor = 1.2
            assert self._paced_time(2) == 2.4
            self.add_voiceover_text(tts.ssml("Une phrase.<bookmark mark='a'/>Une autre."))

    played = []
    for index in range(2):
        scene = object.__new__(Probe)
        scene.speech_service, scene.create_subcaption = service, False
        scene.renderer = SimpleNamespace(time=3, _original_skipping_status=False)
        scene.add_sound = lambda name: played.append(Path(name))
        capture = NarrationCapture(tmp_path / f'narration{index}')
        with capture.observe(manim.Scene, VoiceoverScene, AzureService):
            scene.render()
        assert validate_capture(capture.destination)['voiceovers'] == 1
        assert len(capture.data['adapter_returns']) == (2 if index == 0 else 0)
        used = capture.data['voiceovers'][0]
        assert used['returned_request_evidence']['kind'] == 'teaching_aggregate_return'
        assert used['returned_request_evidence']['requested_configuration']['voice'] == tts.MAI_VOICE_2
        assert used['bookmark_anchors']['a']['seconds'] == pytest.approx(0.7)
        assert used['tracker_bookmark_times']['a'] == pytest.approx(3.7)
        assert used['final_audio']['sha256'] == digest(played[-1])
    assert len(synthesized) == 2  # second capture was wholly cached, still fully attested


@pytest.mark.parametrize('name', ['MANIM_VOICE', 'PACE_FACTOR'])
def test_implicit_context_change_is_rejected_before_synthesis(tmp_path, monkeypatch, name):
    class Scene:
        def render(self):
            raise AssertionError('scene must not run with unrecorded overrides')

    class Voiceover:
        def add_voiceover_text(self, text):
            raise AssertionError('voiceover must not run with unrecorded overrides')

    class Azure:
        def generate_from_text(self, text, **kwargs):
            raise AssertionError('cloud synthesis must not run with unrecorded overrides')

    monkeypatch.delenv(name, raising=False)
    capture = NarrationCapture(tmp_path / 'narration')
    with capture.observe(Scene, Voiceover, Azure):
        monkeypatch.setenv(name, 'unexpected-scene-local-override')
        for call in (Scene().render, lambda: Voiceover().add_voiceover_text('text'),
                     lambda: Azure().generate_from_text('text')):
            with pytest.raises(ValueError, match='changed after launch'):
                call()
    assert capture.data['adapter_returns'] == []
    assert capture.data['voiceovers'] == []

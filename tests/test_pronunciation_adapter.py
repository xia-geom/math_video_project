"""Pronunciation requests, cache identity and PCM joins; no cloud synthesis."""
from __future__ import annotations

from array import array
from pathlib import Path
from types import SimpleNamespace

import pytest
from manim_voiceover.defaults import DEFAULT_VOICEOVER_CACHE_JSON_FILENAME
from manim_voiceover.helper import append_to_json_file
from manim_voiceover.services import azure
from manim_voiceover.services.azure import AzureService
from manim_voiceover.tracker import VoiceoverTracker
from pydub import AudioSegment

from tools import tts
from tools.teaching_voiceover import SAMPLE_RATE, TeachingAzureService, split_at_bookmarks


def make_service(cache, voice=tts.MAI_VOICE_2_1):
    service = object.__new__(TeachingAzureService)
    service.voice, service.style, service.prosody = voice, None, None
    service.output_format, service.cache_dir = tts.AZURE_OUTPUT_FORMAT, cache
    service.global_speed, service._whisper_model = 1.0, None
    service.audio_callback = lambda *args, **kwargs: None
    return service


def remember(service, data):
    append_to_json_file(service.cache_dir / DEFAULT_VOICEOVER_CACHE_JSON_FILENAME, data)


def legacy_aggregate_data(service, text):
    """The historical key is a compatibility fixture, without the new policy."""
    return {
        'input_text': text, 'service': 'teaching_azure_pcm_anchors_v2',
        'voice': service.voice, 'style': service.style, 'prosody': service.prosody,
        'output_format': service.output_format, 'kwargs': {},
    }


@pytest.fixture
def offline_sdk(monkeypatch):
    """Retain the real upstream request/cache code; replace the whole SDK."""
    requests = []
    completed = object()

    class Synthesizer:
        def __init__(self, speech_config, audio_config):
            self.output = audio_config.filename
            self.synthesis_word_boundary = SimpleNamespace(connect=lambda callback: None)

        def speak_ssml_async(self, text):
            requests.append(text)
            AudioSegment.silent(duration=80, frame_rate=SAMPLE_RATE).export(
                self.output, format='mp3'
            )
            return SimpleNamespace(get=lambda: SimpleNamespace(reason=completed))

    monkeypatch.setattr(azure, 'speechsdk', SimpleNamespace(
        SpeechConfig=lambda **kwargs: SimpleNamespace(
            set_speech_synthesis_output_format=lambda value: None
        ),
        SpeechSynthesisOutputFormat={tts.AZURE_OUTPUT_FORMAT: 'offline'},
        audio=SimpleNamespace(AudioOutputConfig=lambda filename: SimpleNamespace(filename=filename)),
        SpeechSynthesizer=Synthesizer,
        ResultReason=SimpleNamespace(SynthesizingAudioCompleted=completed, Canceled=object()),
    ))
    monkeypatch.setenv('AZURE_SUBSCRIPTION_KEY', 'offline-fixture')
    monkeypatch.setenv('AZURE_SERVICE_REGION', 'canadacentral')
    return requests


@pytest.mark.parametrize(('opening', 'closing'), [
    ("<phoneme alphabet='ipa' ph='y'>", '</phoneme>'),
    ("<say-as interpret-as='characters'>", '</say-as>'),
    ("<sub alias='i grec'>", '</sub>'),
])
def test_bookmarks_cannot_split_atomic_pronunciation_even_with_cached_audio(
        tmp_path, monkeypatch, opening, closing):
    text = tts.ssml(f"Une lettre. {opening}y<bookmark mark='inside'/>{closing} Fin.")
    with pytest.raises(ValueError, match='atomic pronunciation'):
        split_at_bookmarks(text)
    service = make_service(tmp_path)
    monkeypatch.setattr(service, 'get_cached_result',
                        lambda *args: pytest.fail('invalid pronunciation reached the cache'))
    with pytest.raises(ValueError, match='pronunciation'):
        service.generate_from_text(text)


def test_repeated_vowels_are_validated_across_bookmarks_before_cache(tmp_path, monkeypatch):
    text = tts.ssml(f"Le point {tts.char('A')}<bookmark mark='a'/> a pour coordonnées deux, un.")
    service = make_service(tmp_path)
    monkeypatch.setattr(service, 'get_cached_result',
                        lambda *args: pytest.fail('vowel collision reached the cache'))
    with pytest.raises(ValueError):
        service.generate_from_text(text)


def test_native_voice_keeps_original_request_and_boundary_events(tmp_path, monkeypatch):
    service = make_service(tmp_path, voice='fr-CA-JeanNeural')
    text = tts.ssml("<say-as interpret-as='characters'>y</say-as><bookmark mark='a'/> Fin.")
    event = {'text_offset': 5, 'audio_offset': 1234, 'boundary_type': 'Word'}
    returned = {'input_text': text, 'word_boundaries': [event], 'original_audio': 'native.mp3'}
    calls = []

    def native(self, actual, **kwargs):
        calls.append((actual, kwargs))
        return returned

    def unexpected(*args):
        pytest.fail('MAI pronunciation preparation reached a native voice')

    monkeypatch.setattr(AzureService, 'generate_from_text', native)
    monkeypatch.setattr(tts, 'prepare_math_speech', unexpected)
    monkeypatch.setattr(tts, 'validate_pronunciation', unexpected)
    result = service.generate_from_text(text, cache_dir=tmp_path, path='native.mp3', prosody={})
    assert result is returned
    assert result['word_boundaries'][0] is event
    assert calls == [(text, {'cache_dir': tmp_path, 'path': 'native.mp3', 'prosody': {}})]


def test_unbookmarked_mai_changed_request_skips_old_audio_and_reuses_corrected_cache(
        tmp_path, offline_sdk):
    service = make_service(tmp_path)
    text = tts.ssml("On lit <say-as interpret-as='characters'>y</say-as>.")
    old = AzureService.generate_from_text(service, text)
    remember(service, old)
    corrected = service._wrap_generate_from_text(text)
    repeated = service._wrap_generate_from_text(text)
    assert len(offline_sdk) == 2
    assert corrected['original_audio'] != old['original_audio']
    assert repeated['original_audio'] == corrected['original_audio']
    assert (tmp_path / old['original_audio']).is_file()
    assert corrected['input_text'] == text
    assert corrected['input_data']['input_text'] == tts.prepare_math_speech(text)
    assert corrected['prepared_input_text'] == corrected['input_data']['input_text']
    assert 'i grec' in corrected['ssml']
    assert 'say-as' not in corrected['ssml']
    assert corrected['pronunciation_policy'] == tts.PRONUNCIATION_POLICY_VERSION


def test_unbookmarked_cached_metadata_is_copied_for_each_authored_source(tmp_path, monkeypatch):
    service = make_service(tmp_path)
    text = tts.ssml("On lit <say-as interpret-as='characters'>y</say-as>.")
    prepared = tts.prepare_math_speech(text)
    cached = {'input_text': prepared, 'input_data': {'input_text': prepared},
              'original_audio': 'prepared.mp3', 'word_boundaries': []}
    monkeypatch.setattr(AzureService, 'generate_from_text', lambda *args, **kwargs: cached)
    returned = service.generate_from_text(text)
    assert returned is not cached
    assert cached['input_text'] == prepared
    assert 'pronunciation_policy' not in cached
    assert returned['input_text'] == text
    assert returned['input_data']['input_text'] == prepared
    # A later plain-spoken author can share that audio without inheriting the
    # first author's symbolic input_text or stale normalization metadata.
    monkeypatch.setattr(AzureService, 'generate_from_text', lambda *args, **kwargs: returned)
    plain = service.generate_from_text(prepared)
    assert plain['input_text'] == prepared
    assert 'prepared_input_text' not in plain
    assert returned['input_text'] == text


def test_bookmarked_cache_keys_include_prepared_inputs_and_preserve_unchanged_clips(
        tmp_path, offline_sdk):
    service = make_service(tmp_path)
    text = tts.ssml("On lit <say-as interpret-as='characters'>y</say-as>."
                    "<bookmark mark='next'/> Une autre phrase.")
    parts = split_at_bookmarks(text)
    old_clips = []
    for part in parts:
        old = AzureService.generate_from_text(service, part['ssml'])
        old_clips.append(old['original_audio'])
        remember(service, old)
    remember(service, {
        'input_text': text, 'input_data': legacy_aggregate_data(service, text),
        'original_audio': 'legacy-aggregate.mp3',
    })
    offline_sdk.clear()
    corrected = service._wrap_generate_from_text(text)
    repeated = service._wrap_generate_from_text(text)
    assert len(offline_sdk) == 1  # the unchanged second fragment is still cached
    assert 'i grec' in offline_sdk[0]
    assert corrected['original_audio'] != 'legacy-aggregate.mp3'
    assert repeated['original_audio'] == corrected['original_audio']
    assert corrected['clips'][0]['audio'] != old_clips[0]
    assert corrected['clips'][1]['audio'] == old_clips[1]
    assert corrected['input_data']['prepared_fragments'] == [
        tts.prepare_math_speech(part['ssml']) for part in parts
    ]
    assert corrected['input_data']['pronunciation_policy'] == tts.PRONUNCIATION_POLICY_VERSION


def test_unchanged_bookmarked_narration_can_reuse_the_previous_aggregate(tmp_path, offline_sdk):
    service = make_service(tmp_path)
    text = tts.ssml("Une phrase.<bookmark mark='next'/> Une autre.")
    old = {'input_text': text, 'input_data': legacy_aggregate_data(service, text),
           'original_audio': 'accepted.mp3'}
    remember(service, old)
    assert service.generate_from_text(text) == old
    assert offline_sdk == []


@pytest.mark.parametrize('voice', [tts.MAI_VOICE_2, tts.MAI_VOICE_2_1])
def test_prepared_pcm_fragments_preserve_order_silence_and_authored_coordinates(
        tmp_path, monkeypatch, voice):
    service = make_service(tmp_path, voice)
    text = tts.ssml(
        "On lit <say-as interpret-as='characters'>y</say-as>. <bookmark mark='first'/>"
        "<break time='25ms'/><bookmark mark='pause'/>"
        "Puis <sub alias='ix'>x</sub>.<bookmark mark='second'/> Fin."
    )
    fixtures = [(1000, 4800), (-2000, 7200), (3000, 9600)]
    requests, joined = [], []
    original_export = AudioSegment.export

    def fragment(self, actual, cache_dir=None, **kwargs):
        value, frames = fixtures[len(requests)]
        name = f'fixture_{len(requests)}.wav'
        requests.append(actual)
        segment = AudioSegment(array('h', [value] * frames).tobytes(),
                               sample_width=2, frame_rate=SAMPLE_RATE, channels=1)
        segment.export(Path(cache_dir) / name, format='wav')
        return {'original_audio': name}

    def capture_export(segment, out_f=None, format='mp3', **kwargs):
        if format == 'mp3':
            joined.append(segment.raw_data)
        return original_export(segment, out_f, format=format, **kwargs)

    monkeypatch.setattr(AzureService, 'generate_from_text', fragment)
    monkeypatch.setattr(AudioSegment, 'export', capture_export)
    result = service._wrap_generate_from_text(text)
    expected = array('h', [1000] * 4800 + [0] * 1200 + [-2000] * 7200 + [3000] * 9600)
    assert joined == [expected.tobytes()]
    assert [(clip['start_sample'], clip['samples']) for clip in result['clips']] == [
        (0, 4800), (4800, 1200), (6000, 7200), (13200, 9600),
    ]
    assert result['clips'][1]['authored_silence'] is True
    assert result['input_text'] == text
    parts = split_at_bookmarks(text)
    assert requests == [tts.prepare_math_speech(parts[index]['ssml']) for index in (0, 2, 3)]
    assert [boundary['text_offset'] for boundary in result['word_boundaries']] == [
        0, *(part['distance'] for part in parts),
    ]
    assert all(boundary['boundary_type'] == 'AuthoredBookmarkAnchor'
               for boundary in result['word_boundaries'])
    tracker = VoiceoverTracker(SimpleNamespace(renderer=SimpleNamespace(time=2)), result, tmp_path)
    assert tracker.bookmark_distances == {
        'first': parts[0]['distance'], 'pause': parts[1]['distance'], 'second': parts[2]['distance'],
    }
    assert tracker.bookmark_times == pytest.approx({'first': 2.1, 'pause': 2.125, 'second': 2.275})

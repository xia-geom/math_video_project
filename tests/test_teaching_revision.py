"""Layout and measured narration contracts; no cloud/listening approval is inferred."""
from __future__ import annotations

import ast
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from manim import RIGHT, Text
from manim_voiceover.services.azure import AzureService
from manim_voiceover.tracker import VoiceoverTracker
from pydub import AudioSegment

from tools import tts
from tools.branding import INTRO_TIMING, play_uqam_intro
from tools.teaching_layout import assert_inside, panel
from tools.teaching_voiceover import BOOKMARK, SAMPLE_RATE, TeachingAzureService, split_at_bookmarks

ROOT = Path(__file__).resolve().parents[1]


def all_entries():
    return yaml.safe_load((ROOT / 'curriculum/programme_principal_fr.yaml').read_text())['entries']


@pytest.mark.parametrize('entry', all_entries(), ids=lambda e: f"{e['track']}_{e['order']:02d}")
def test_every_lesson_uses_one_shared_opening_and_teaching_adapter(entry):
    text = (ROOT / entry['scene_file']).read_text()
    tree = ast.parse(text)
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert sum(getattr(node.func, 'id', '') == 'play_uqam_intro' for node in calls) == 1
    assert 'TeachingAzureService' in text or 'TeachingScene' in text
    assert 'LOGO_UQAM.png' not in text
    for call in calls:
        if getattr(call.func, 'id', '') == 'AzureService':
            assert not any(k.arg == 'global_speed' for k in call.keywords)


def test_default_is_existing_mai_teaching_profile(monkeypatch):
    monkeypatch.delenv('MANIM_VOICE', raising=False)
    assert tts.resolve_voice() == tts.MAI_VOICE_2
    assert tts.VOICE_CONFIGS[tts.MAI_VOICE_2] == '-3%'
    assert tts.VOICE_STYLES[tts.MAI_VOICE_2] is None


def test_panel_grows_without_shrinking_text():
    content = Text('Une formule lisible dans son cadre', font_size=32)
    original = (content.width, content.height, content.font_size)
    frame = panel(content, width=2, height=0.5)
    assert (content.width, content.height, content.font_size) == pytest.approx(original)
    assert_inside(content, frame[0], 0.28)
    content.shift(RIGHT * 0.5)
    with pytest.raises(ValueError, match='outside'):
        assert_inside(content, frame[0], 0.28)


def test_crowded_panel_requires_reorganization():
    with pytest.raises(ValueError, match='split'):
        panel(Text('Une très longue phrase ' * 8, font_size=36))


def test_logo_is_single_clean_opening():
    events = []
    scene = SimpleNamespace(mobjects=[], camera=SimpleNamespace(background_color=None),
                            play=lambda *a, **kw: events.append(kw['run_time']),
                            wait=lambda t: events.append(t))
    play_uqam_intro(scene)
    assert sum(events) == pytest.approx(1.5)
    assert sum(INTRO_TIMING.values()) == pytest.approx(1.5)
    with pytest.raises(RuntimeError, match='Duplicate'):
        play_uqam_intro(scene)


def test_balanced_ssml_fragments_keep_tags_and_coordinates():
    text = tts.ssml("Regardons. <bookmark mark='a'/> Puis " + tts.char('x') + ". <bookmark mark='b'/> Voilà.")
    parts = split_at_bookmarks(text)
    assert len(parts) == 3
    for part in parts:
        ET.fromstring('<root>' + part['ssml'] + '</root>')
    assert parts[-1]['distance'] == len(BOOKMARK.sub('', text))
    assert 'say-as' in parts[1]['ssml']
    with pytest.raises(ValueError, match='Duplicate'):
        split_at_bookmarks("A<bookmark mark='a'/>B<bookmark mark='a'/>")


def test_mai_bookmarks_use_actual_pcm_samples(tmp_path, monkeypatch):
    service = object.__new__(TeachingAzureService)
    service.voice, service.style, service.prosody = tts.MAI_VOICE_2, None, None
    service.output_format, service.cache_dir = tts.AZURE_OUTPUT_FORMAT, tmp_path
    service.global_speed = 1.0
    service._whisper_model = None
    service.audio_callback = lambda *args, **kwargs: None
    service.get_cached_result = lambda *args: None
    service.get_audio_basename = lambda data: 'measured_test'
    durations = iter([700, 1300, 500])
    generated = []

    def fake_synthesis(self, text, cache_dir=None, **kwargs):
        name = f'fixture_{len(generated)}.wav'
        generated.append(text)
        AudioSegment.silent(duration=next(durations), frame_rate=SAMPLE_RATE).export(tmp_path / name, format='wav')
        return {'original_audio': name}

    monkeypatch.setattr(AzureService, 'generate_from_text', fake_synthesis)
    text = tts.ssml("Une phrase. <bookmark mark='a'/> Une autre. <bookmark mark='b'/> Fin.")
    # Exercise the real upstream wrapper: final_audio and cache metadata.
    data = service._wrap_generate_from_text(text)
    assert data['bookmark_anchors']['a']['sample'] == 33600
    assert data['bookmark_anchors']['b']['sample'] == 96000
    tracker = VoiceoverTracker(SimpleNamespace(renderer=SimpleNamespace(time=0)), data, tmp_path)
    assert tracker.bookmark_times['a'] == pytest.approx(0.7)
    assert tracker.bookmark_times['b'] == pytest.approx(2.0)
    # MP3 metadata may include codec-padding frames; decoded PCM is exact.
    assert 2.5 <= tracker.duration < 2.56
    decoded = AudioSegment.from_file(tmp_path / data['final_audio'])
    assert int(decoded.frame_count()) == 120000
    assert all(b['boundary_type'] == 'AuthoredBookmarkAnchor' for b in data['word_boundaries'])


def test_narrated_setup_does_not_silently_accept_missing_credentials(monkeypatch):
    from tools.teaching_layout import TeachingScene
    for key in ('MANIM_DISABLE_VOICEOVER', 'SPEECH_KEY', 'SPEECH_REGION',
                'AZURE_SUBSCRIPTION_KEY', 'AZURE_SERVICE_REGION'):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match='SPEECH_KEY'):
        TeachingScene().setup_narration()

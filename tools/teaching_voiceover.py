"""Teaching Azure adapter with measured, explicitly authored bookmark anchors.

MAI's concept clips are concatenated at PCM sample boundaries. These anchors
are not ASR/word timestamps and are never estimated from word counts. Non-MAI
voices retain the upstream Azure adapter's native boundary events.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from manim_voiceover.services.azure import AzureService
from pydub import AudioSegment

from tools import tts

BOOKMARK = re.compile(r"<bookmark\s+mark=['\"](?P<mark>\w+)['\"]\s*/>")
TAG = re.compile(r'<[^>]+>')
BREAK = re.compile(r"<break\s+time=['\"](?P<value>\d+(?:\.\d+)?)(?P<unit>ms|s)['\"]\s*/>")
ATOMIC_PRONUNCIATION_TAGS = frozenset({'phoneme', 'say-as', 'sub'})
SAMPLE_RATE = 48000
TICKS = 10_000_000


def split_at_bookmarks(text):
    """Preserve SSML wrappers and the original adapter's character coordinates."""
    ET.fromstring('<root xmlns:mstts="https://www.w3.org/2001/mstts">' + text + '</root>')
    stack, result, marks = [], [], set()
    cursor = distance = 0
    for match in [*BOOKMARK.finditer(text), None]:
        stop = match.start() if match else len(text)
        raw = text[cursor:stop]
        prefix = ''.join(opening for _, opening in stack)
        for token in TAG.findall(raw):
            if token.startswith('</'):
                name = token[2:-1].strip()
                if not stack or stack[-1][0] != name:
                    raise ValueError('Unbalanced SSML wrapper at a bookmark.')
                stack.pop()
            elif not token.endswith('/>') and not token.startswith(('<!', '<?')):
                name = re.match(r'<([\w:-]+)', token).group(1)
                stack.append((name, token))
        # Reopening an alias or phoneme on both sides can pronounce one token
        # twice. Only structural wrappers may span a synthesized boundary.
        if match:
            atomic = next((name for name, _ in stack
                           if name.rsplit(':', 1)[-1] in ATOMIC_PRONUNCIATION_TAGS), None)
            if atomic:
                raise ValueError(
                    f"Narration bookmark '{match.group('mark')}' splits an atomic "
                    f'pronunciation element ({atomic}).'
                )
        fragment = prefix + raw + ''.join(f'</{name}>' for name, _ in reversed(stack))
        distance += len(raw)
        mark = match.group('mark') if match else None
        if mark in marks:
            raise ValueError(f'Duplicate narration bookmark: {mark}')
        if mark:
            marks.add(mark)
        result.append({'ssml': fragment, 'raw': raw, 'distance': distance, 'mark': mark})
        cursor = match.end() if match else len(text)
    if stack:
        raise ValueError('Unclosed SSML wrappers.')
    return result


class TeachingAzureService(AzureService):
    """Shared teaching profile, with no extra post-synthesis slowdown."""

    def __init__(self, voice=tts.VOICE_ID, **kwargs):
        options = tts.azure_service_kwargs(voice)
        options.update(kwargs)
        if options.get('global_speed', 1.0) != 1.0:
            raise ValueError('Use the shared SSML rate, not a second audio speed multiplier.')
        super().__init__(**options)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        if not tts.is_mai_voice(self.voice):
            return super().generate_from_text(text, cache_dir=cache_dir, path=path, **kwargs)
        # Validate the complete authored thought, including collisions across
        # bookmarks, before an old cache entry can bypass pronunciation checks.
        tts.validate_pronunciation(text)
        if not BOOKMARK.search(text):
            prepared = tts.prepare_math_speech(text)
            result = dict(super().generate_from_text(
                prepared, cache_dir=cache_dir, path=path, **kwargs
            ))
            # Upstream keys and SSML describe the actual synthesis request.
            # Keep authored metadata without mutating a returned cache object;
            # this path has no bookmarks whose character offsets need mapping.
            result['input_text'] = text
            if prepared != text:
                result['pronunciation_policy'] = tts.PRONUNCIATION_POLICY_VERSION
                result['prepared_input_text'] = prepared
            else:
                result.pop('pronunciation_policy', None)
                result.pop('prepared_input_text', None)
            return result
        parts = split_at_bookmarks(text)
        prepared_parts = [tts.prepare_math_speech(part['ssml']) for part in parts]
        directory = Path(cache_dir or self.cache_dir)
        data = {'input_text': text, 'service': 'teaching_azure_pcm_anchors_v2',
                'voice': self.voice, 'style': self.style, 'prosody': self.prosody,
                'output_format': self.output_format, 'kwargs': kwargs}
        if any(prepared != part['ssml'] for part, prepared in zip(parts, prepared_parts)):
            # Invalidate only affected narration. Unchanged thoughts retain
            # their existing key; constituent Azure keys use prepared SSML too.
            data['pronunciation_policy'] = tts.PRONUNCIATION_POLICY_VERSION
            data['prepared_fragments'] = prepared_parts
        cached = self.get_cached_result(data, directory)
        if cached is not None:
            return cached
        audio = AudioSegment.silent(duration=0, frame_rate=SAMPLE_RATE).set_channels(1)
        samples, coordinates, anchors, clips = 0, {0: 0}, {}, []
        for part, prepared in zip(parts, prepared_parts):
            spoken = tts.strip_ssml(prepared).strip()
            if not spoken and '<break' in part['raw']:
                milliseconds = sum(
                    float(match.group('value')) * (1000 if match.group('unit') == 's' else 1)
                    for match in BREAK.finditer(part['raw'])
                )
                if milliseconds:
                    clip = AudioSegment.silent(
                        duration=milliseconds, frame_rate=SAMPLE_RATE
                    ).set_channels(1).set_sample_width(2)
                    frames = int(clip.frame_count())
                    clips.append({'audio': None, 'start_sample': samples,
                                  'samples': frames, 'authored_silence': True})
                    audio += clip
                    samples += frames
            elif spoken:
                clip_data = super().generate_from_text(prepared, cache_dir=directory, **kwargs)
                clip = AudioSegment.from_file(directory / clip_data['original_audio'])
                clip = clip.set_frame_rate(SAMPLE_RATE).set_channels(1).set_sample_width(2)
                frames = int(clip.frame_count())
                clips.append({'audio': clip_data['original_audio'], 'start_sample': samples,
                              'samples': frames})
                audio += clip
                samples += frames
            ticks = round(samples * TICKS / SAMPLE_RATE)
            coordinates[part['distance']] = ticks
            if part['mark']:
                anchors[part['mark']] = {'sample': samples, 'seconds': samples / SAMPLE_RATE}
        if samples == 0:
            raise ValueError('Narration contains no audio.')
        # manim-voiceover 0.3.7 measures duration with mutagen.MP3.
        # Join in PCM first, then encode one gapless MP3 for its tracker.
        filename = path or self.get_audio_basename(data) + '.mp3'
        audio.export(directory / filename, format='mp3', bitrate='192k')
        boundaries = [{'audio_offset': ticks, 'text_offset': distance, 'word_length': 0,
                       'text': '', 'boundary_type': 'AuthoredBookmarkAnchor'}
                      for distance, ticks in sorted(coordinates.items())]
        return {'input_text': text, 'input_data': data, 'original_audio': filename,
                'word_boundaries': boundaries, 'bookmark_anchors': anchors,
                'timing_basis': 'measured_pcm_fragments', 'sample_rate': SAMPLE_RATE,
                'clips': clips}

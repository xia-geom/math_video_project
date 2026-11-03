"""Observe completed narration requests and scene use without certifying listening.

Used only by the isolated narrated-review CLI. Never serialize environment,
arbitrary SDK objects, kwargs, or the whole voiceover cache. The upstream adapter
returns its actual SSML/configuration; that is requested voice evidence, not
proof of perceived voice identity or a fresh network request (cache is possible).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from unittest.mock import patch


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def narration_tooling_hashes(root):
    return {name: digest(Path(root) / name) for name in (
        'tools/narration_provenance.py', 'scripts/render_narrated_review.py')}


def validate_narration_tooling(recorded, root):
    """Narrated evidence requires the exact observer used for this revision."""
    if recorded != narration_tooling_hashes(root):
        raise ValueError('Narration observer tooling changed or was not attested.')


def requested_context(environ=None):
    """Exact explicit launch overrides; unset is not an invented default."""
    environ = os.environ if environ is None else environ
    return {name: {'present': name in environ, 'value': environ.get(name)}
            for name in ('MANIM_VOICE', 'PACE_FACTOR')}


def audio_runtime():
    result = {}
    for name in ('azure-cognitiveservices-speech', 'pydub', 'mutagen', 'manim-voiceover'):
        try:
            result[name] = version(name)
        except PackageNotFoundError:
            result[name] = None
    return result


def numeric(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return None
    return value if math.isfinite(value) else None


def speech_directives(ssml):
    """Keep each authored language/prosody scope, including nested overrides."""
    root = ET.fromstring(ssml)
    records = []

    def visit(node, ancestors):
        tag = node.tag.rsplit('}', 1)[-1]
        path = [*ancestors, tag]
        attrs = {}
        for name in ('name', 'rate', 'style', 'pitch', 'contour', 'range', 'volume'):
            if name in node.attrib:
                attrs[name] = node.attrib[name]
        language = node.get('{http://www.w3.org/XML/1998/namespace}lang')
        if language is not None:
            attrs['locale'] = language
        if attrs:
            records.append({'scope': path, **attrs})
        for child in node:
            visit(child, path)

    visit(root, [])
    return records


class NarrationCapture:
    def __init__(self, destination):
        self.destination = Path(destination)
        self.destination.mkdir(parents=True, exist_ok=True)
        self.audio = self.destination / 'audio'
        self.audio.mkdir(exist_ok=True)
        requested = os.getenv('PACE_FACTOR')
        self.data = {
            'schema_version': 1,
            'evidence_kind': 'observed_adapter_returns_and_scene_calls',
            'network_synthesis_vs_cache': 'not_distinguished',
            'listening': 'not_performed', 'release_ready': False,
            'requested_render_context': requested_context(),
            'audio_runtime_versions': audio_runtime(),
            'pace_factor_environment': {
                'present': requested is not None,
                'numeric_value': numeric(requested),
                'invalid_numeric_value': requested is not None and numeric(requested) is None,
            },
            'adapter_returns': [], 'voiceovers': [], 'scenes': [],
        }

    def check_context(self):
        if requested_context() != self.data['requested_render_context']:
            raise ValueError('Voice or pacing overrides changed after launch; load them explicitly before rendering.')

    def save(self):
        target = self.destination / 'provenance.json'
        temporary = target.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(target)

    def retain_audio(self, cache_dir, name):
        if not isinstance(name, str) or not name:
            raise ValueError('Completed narration is missing its audio reference.')
        cache = Path(cache_dir).resolve()
        source = (cache / name).resolve()
        if not source.is_relative_to(cache) or not source.is_file():
            raise ValueError('Narration audio must exist inside the isolated voiceover cache.')
        if source.suffix.lower() not in {'.mp3', '.wav', '.ogg', '.m4a'}:
            raise ValueError('Unexpected narration audio format.')
        sha = digest(source)
        destination = self.audio / (sha + source.suffix.lower())
        if not destination.exists():
            shutil.copy2(source, destination)
        return {'path': destination.relative_to(self.destination).as_posix(),
                'sha256': sha, 'bytes': source.stat().st_size}

    def adapter_return(self, service, data, cache_dir):
        request = data.get('input_data', {})
        ssml = data.get('ssml') or request.get('ssml')
        if not isinstance(ssml, str) or not ssml:
            raise ValueError('Azure adapter did not retain its actual SSML request.')
        config = request.get('config', {})
        record = {
            'id': len(self.data['adapter_returns']),
            'service': 'azure', 'ssml': ssml,
            'ssml_sha256': hashlib.sha256(ssml.encode()).hexdigest(),
            'directives': speech_directives(ssml),
            # No default values are substituted when upstream evidence is absent.
            'requested_configuration': {
                key: config.get(key) for key in ('voice', 'style', 'prosody', 'output_format')
            },
            'audio': self.retain_audio(cache_dir or service.cache_dir, data.get('original_audio')),
        }
        self.data['adapter_returns'].append(record)
        self.save()

    def voiceover(self, scene, tracker):
        data = tracker.data
        service = scene.speech_service
        request = data.get('input_data', {})
        aggregate = request.get('service') == 'teaching_azure_pcm_anchors_v2'
        config = request if aggregate else request.get('config', {})
        request_evidence = {
            'kind': 'teaching_aggregate_return' if aggregate else 'azure_ssml_return',
            'service': request.get('service'),
            'input_text': request.get('input_text'),
            'requested_configuration': {key: config.get(key)
                for key in ('voice', 'style', 'prosody', 'output_format')},
            'per_call_prosody': request.get('kwargs', {}).get('prosody') if aggregate else None,
            'ssml': request.get('input_text') if aggregate else request.get('ssml'),
            'network_synthesis_vs_cache': 'not_distinguished',
        }
        if request_evidence['ssml']:
            request_evidence['directives'] = speech_directives(request_evidence['ssml'])
        anchors = {
            name: {'sample': value['sample'], 'seconds': value['seconds']}
            for name, value in data.get('bookmark_anchors', {}).items()
        }
        boundaries = [{key: item[key] for key in (
            'audio_offset', 'text_offset', 'word_length', 'text', 'boundary_type') if key in item}
            for item in data.get('word_boundaries', [])]
        clips = []
        for clip in data.get('clips', []):
            item = {key: clip[key] for key in ('start_sample', 'samples', 'authored_silence')
                    if key in clip}
            if clip.get('audio'):
                item['audio'] = self.retain_audio(service.cache_dir, clip['audio'])
            clips.append(item)
        record = {
            'scene_class': type(scene).__name__,
            'returned_request_evidence': request_evidence,
            'input_text': data.get('input_text'),
            'service_class': type(service).__name__,
            'service_configuration_observed': {
                key: getattr(service, key, None)
                for key in ('voice', 'style', 'prosody', 'output_format', 'global_speed')
            },
            'final_audio': self.retain_audio(service.cache_dir, data.get('final_audio')),
            'original_audio': self.retain_audio(service.cache_dir, data.get('original_audio')),
            'start_seconds': numeric(tracker.start_t), 'end_seconds': numeric(tracker.end_t),
            'duration_seconds': numeric(tracker.duration),
            'bookmark_anchors': anchors, 'word_boundaries': boundaries,
            'tracker_bookmark_times': {key: float(value)
                                       for key, value in getattr(tracker, 'bookmark_times', {}).items()},
            'timing_basis': data.get('timing_basis', 'upstream_word_boundaries_or_tracker_fallback'),
            'sample_rate': data.get('sample_rate'), 'clips': clips,
        }
        self.data['voiceovers'].append(record)
        self.save()

    @contextmanager
    def observe(self, scene_class, voiceover_class, azure_class):
        original_render = scene_class.render
        original_voiceover = voiceover_class.add_voiceover_text
        original_generate = azure_class.generate_from_text
        capture = self

        def render(scene, *args, **kwargs):
            capture.check_context()
            pace = getattr(scene, '_paced_time', None)
            had_local_pace = '_paced_time' in scene.__dict__
            old_local_pace = scene.__dict__.get('_paced_time')
            record = {'scene_class': type(scene).__name__, 'render_completed': False,
                      'pace_factor': {'method_present': callable(pace), 'used': False,
                                      'observed_factor': None, 'calls': []}}
            capture.data['scenes'].append(record)

            def paced(seconds):
                result = pace(seconds)
                record['pace_factor']['used'] = True
                record['pace_factor']['observed_factor'] = numeric(getattr(scene, 'pace_factor', None))
                record['pace_factor']['calls'].append(
                    {'input_seconds': numeric(seconds), 'output_seconds': numeric(result),
                     'factor': numeric(getattr(scene, 'pace_factor', None))})
                return result

            if callable(pace):
                scene._paced_time = paced
            try:
                result = original_render(scene, *args, **kwargs)
                capture.check_context()
                record['render_completed'] = True
                return result
            finally:
                if callable(pace):
                    if had_local_pace:
                        scene._paced_time = old_local_pace
                    else:
                        del scene._paced_time
                capture.save()

        def generate(service, text, cache_dir=None, path=None, **kwargs):
            capture.check_context()
            result = original_generate(service, text, cache_dir=cache_dir, path=path, **kwargs)
            capture.adapter_return(service, result, cache_dir)
            return result

        def voiceover(scene, *args, **kwargs):
            capture.check_context()
            tracker = original_voiceover(scene, *args, **kwargs)
            capture.voiceover(scene, tracker)
            return tracker

        with patch.object(scene_class, 'render', render), \
                patch.object(voiceover_class, 'add_voiceover_text', voiceover), \
                patch.object(azure_class, 'generate_from_text', generate):
            try:
                yield self
            finally:
                self.save()


def validate_capture(destination):
    """Fail closed before discarding cache; this is evidence integrity, not listening."""
    destination = Path(destination)
    data = json.loads((destination / 'provenance.json').read_text())
    if not data['scenes'] or not all(row['render_completed'] for row in data['scenes']):
        raise ValueError('Narration capture lacks a completed scene render.')
    if not data['voiceovers']:
        raise ValueError('Narration capture lacks actual scene observations.')
    for row in data['voiceovers']:
        evidence = row.get('returned_request_evidence', {})
        if (evidence.get('service') not in {'azure', 'teaching_azure_pcm_anchors_v2'}
                or not evidence.get('ssml')
                or not evidence.get('requested_configuration', {}).get('voice')):
            raise ValueError('A used voiceover lacks returned request evidence.')
    references = [row['audio'] for row in data['adapter_returns']]
    for row in data['voiceovers']:
        references.extend((row['original_audio'], row['final_audio']))
        references.extend(clip['audio'] for clip in row['clips'] if 'audio' in clip)
    root = destination.resolve()
    for reference in references:
        audio = (root / reference['path']).resolve()
        if (not audio.is_relative_to(root / 'audio') or not audio.is_file()
                or digest(audio) != reference['sha256']):
            raise ValueError('Retained narration audio failed its integrity check.')
    return {'path': 'narration/provenance.json',
            'sha256': digest(destination / 'provenance.json'),
            'adapter_returns': len(data['adapter_returns']),
            'voiceovers': len(data['voiceovers']), 'listening': 'not_performed'}


def seal_capture(destination, video_sha256, input_signature, encoded_audio):
    """Bind retained observations to the encoded film and its copied audio stream."""
    destination = Path(destination)
    validate_capture(destination)
    path = destination / 'provenance.json'
    data = json.loads(path.read_text())
    data['artifact_binding'] = {'video_sha256': video_sha256,
                                'input_signature': input_signature,
                                'encoded_audio': encoded_audio}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return validate_capture(destination)


def verify_narration_manifest(status_file, status, video_sha256, input_signature):
    """Reject stale/tampered audio evidence during artifact reconciliation."""
    root = Path(status_file).parent.resolve()
    reference = status.get('narration_evidence', {})
    manifest = (root / reference.get('path', '')).resolve()
    if (not manifest.is_relative_to(root) or not manifest.is_file()
            or digest(manifest) != reference.get('sha256')):
        raise ValueError('Missing or mismatched narration manifest.')
    data = json.loads(manifest.read_text())
    if data.get('requested_render_context') != requested_context():
        raise ValueError('Explicit voice or pacing overrides changed or were not attested.')
    runtime = audio_runtime()
    if not all(runtime.values()) or data.get('audio_runtime_versions') != runtime:
        raise ValueError('Narration runtime is unavailable or changed.')
    binding = data.get('artifact_binding', {})
    if (binding.get('video_sha256') != video_sha256
            or binding.get('input_signature') != input_signature):
        raise ValueError('Narration manifest belongs to different inputs or video.')
    audio_ref = status.get('encoded_audio', {})
    audio = (root / audio_ref.get('path', '')).resolve()
    bound_audio = binding.get('encoded_audio', {})
    if (not audio.is_relative_to(root) or not audio.is_file()
            or digest(audio) != audio_ref.get('sha256')
            or audio_ref.get('sha256') != bound_audio.get('sha256')
            or audio != (manifest.parent / bound_audio.get('path', '')).resolve()):
        raise ValueError('Encoded audio evidence is missing or mismatched.')
    validate_capture(manifest.parent)
    return {'status': 'verified', 'manifest_sha256': digest(manifest),
            'encoded_audio_sha256': digest(audio),
            'requested_render_context': data['requested_render_context'],
            'listening': 'not_performed'}

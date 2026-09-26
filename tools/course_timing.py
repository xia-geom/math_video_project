"""Course duration policy and evidence checks, independent of Manim or cloud services."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml

POLICY_PATH = Path(__file__).resolve().parents[1] / 'curriculum/duration_policy.yaml'


def seconds(value: Any, *, allow_zero: bool = False) -> float:
    """Reject NaN, infinity, booleans and negative timing values."""
    if isinstance(value, bool):
        raise ValueError('A duration must be a finite number, not a boolean.')
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('A duration must be numeric.') from exc
    if not math.isfinite(result) or result < 0 or (not allow_zero and result == 0):
        raise ValueError('A duration must be finite and positive (or explicitly allow zero).')
    return result


def load_duration_policy(path: Path = POLICY_PATH) -> dict:
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('Unsupported duration policy.')
    if data.get('timing_reference') != 'natural_narration_and_reading':
        raise ValueError('Course timing must follow narration and reading.')
    limits = data.get('narrated_range_seconds')
    if limits is not None:
        if not isinstance(limits, dict) or set(limits) != {'minimum', 'maximum'}:
            raise ValueError('A narrated range needs minimum and maximum seconds.')
        if seconds(limits['minimum']) > seconds(limits['maximum']):
            raise ValueError('The minimum cannot exceed the maximum.')
        source = data.get('range_source')
        if not isinstance(source, str) or not source.strip():
            raise ValueError('A numeric target requires its agreed source, not an invented default.')
    return data


def assess_duration(value: Any, *, mode: str, has_audio: bool, policy: dict) -> dict:
    """A silent preview can never certify the length of a narrated lesson."""
    duration = seconds(value)
    if mode not in {'silent_preview', 'azure_review'}:
        raise ValueError('Unknown timing evidence mode.')
    if bool(has_audio) != (mode == 'azure_review'):
        raise ValueError('Encoded audio presence does not match the stated mode.')
    result = {'measured_seconds': duration, 'measurement_mode': mode,
              'narrated_duration_verified': False, 'release_ready': False}
    if mode == 'silent_preview':
        result.update(status='not_assessable_from_silent_preview',
                      reason='Authored preview holds are not synthesized-speech durations.')
        return result
    limits = policy.get('narrated_range_seconds')
    if limits is None:
        result.update(status='numeric_target_not_documented',
                      reason='Natural narration measured; the agreed numeric range is not in the sources.')
        return result
    low, high = seconds(limits['minimum']), seconds(limits['maximum'])
    within = low <= duration <= high
    result.update(status='within_range' if within else 'outside_range',
                  required_range_seconds=[low, high], narrated_duration_verified=within,
                  reason='Total length only; full-motion, speech and reading review remain separate.')
    return result


def validate_timing_records(records: list[dict], *, mode: str, tolerance: float = 0.10) -> list[str]:
    """Check authored minimum visibility and post-question pauses on a scene clock."""
    if mode not in {'silent_preview', 'azure_review'}:
        return ['Unknown timing evidence mode.']
    if not records:
        return ['No explanation timing records.']
    errors = []
    previous_end = 0.0
    for index, record in enumerate(records, 1):
        try:
            start, visible, speech_done, end = (seconds(record[key], allow_zero=True)
                                               for key in ('start', 'visible_from', 'speech_context_end', 'end'))
            hold = seconds(record['minimum_visible_seconds'], allow_zero=True)
            pause = seconds(record['reflection_pause_seconds'], allow_zero=True)
            if record['mode'] != mode or start < previous_end - tolerance:
                raise ValueError('Wrong mode or overlapping explanation records.')
            if not start <= visible <= speech_done <= end:
                raise ValueError('Non-monotone scene timing.')
            minimum = max(hold, pause) if mode == 'silent_preview' else hold
            if speech_done - visible < minimum - tolerance:
                raise ValueError('Authored minimum visibility was shortened.')
            if mode == 'azure_review':
                speech_duration = seconds(record['speech_duration_seconds'])
                if speech_done - start < speech_duration - tolerance:
                    raise ValueError('Speech was not allowed to finish.')
                if end - speech_done < pause - tolerance:
                    raise ValueError('The post-question reflection pause was shortened.')
            previous_end = end
        except (KeyError, ValueError, TypeError) as exc:
            errors.append(f'Explanation {index}: {exc}')
    return errors

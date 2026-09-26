"""Validated independent practice for the ten additions; no rendering dependencies."""
from __future__ import annotations

from pathlib import Path

import yaml

from tools.course_timing import seconds

PRACTICE_PATH = Path(__file__).resolve().parents[1] / 'curriculum/practice_questions.yaml'


def load_practice(path: Path = PRACTICE_PATH) -> dict:
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('Unsupported practice-question record.')
    questions = data.get('questions')
    if not isinstance(questions, dict) or not questions:
        raise ValueError('Practice questions must be keyed by stable lesson ID.')
    for lesson_id, question in questions.items():
        if not isinstance(lesson_id, str) or not isinstance(question, dict):
            raise ValueError('Invalid practice-question entry.')
        for key in ('title', 'premise', 'prompt'):
            if not isinstance(question.get(key), str) or not question[key].strip():
                raise ValueError(f'{lesson_id}: missing {key}.')
        seconds(question['question_seconds'])
        seconds(question['reflection_seconds'])
        steps = question.get('steps')
        if not isinstance(steps, list) or len(steps) != 3:
            raise ValueError(f'{lesson_id}: practice needs three explicit solution steps.')
        for step in steps:
            if not isinstance(step, dict) or any(
                not isinstance(step.get(key), str) or not step[key].strip()
                for key in ('math', 'narration')
            ):
                raise ValueError(f'{lesson_id}: each solution needs mathematics and explanation.')
            seconds(step['reading_seconds'])
    return questions

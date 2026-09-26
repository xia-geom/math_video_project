"""Contained calculations and worked examples for the ten syllabus additions.

Opt-in scene base: no retiming of other lessons and no cloud speech in silent mode.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import yaml
from manim import FadeOut, MathTex, config

from tools.teaching_layout import BODY_HEIGHT, TeachingScene, assert_inside, panel

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / 'curriculum/worked_examples'


def step_premises(example):
    """The visible problem persists until a step explicitly replaces it."""
    current = example['premise']
    premises = []
    for step in example['steps']:
        current = step.get('premise', current)
        if not isinstance(current, str) or not current.strip():
            raise ValueError('A worked step needs a nonempty visible premise.')
        premises.append(current)
    return premises


def load_examples():
    lessons = {}
    for path in sorted(EXAMPLES_DIR.glob('*.yaml')):
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        if data.get('version') != 1 or data['lesson_id'] in lessons:
            raise ValueError('Unsupported or duplicate worked-example record.')
        for example in data['examples']:
            step_premises(example)
        lessons[data['lesson_id']] = data['examples']
    return lessons


def check_panels(page):
    """Check current geometry, including nested cards, not saved initial bounds."""
    count = 0
    if page is None:
        return count
    for item in page.get_family():
        if vars(item).get('teaching_panel') is True:
            if len(item) != 2:
                raise ValueError('A panel owns one border and one content group.')
            assert_inside(item[1], item[0], padding=0.18)
            count += 1
    return count


def check_frame(page, margin=0.5):
    """Panels fitting their text is not sufficient: the page must fit the frame."""
    if page is None:
        return
    if (page.get_left()[0] < -config.frame_width / 2 + margin - 0.001
            or page.get_right()[0] > config.frame_width / 2 - margin + 0.001
            or page.get_bottom()[1] < -config.frame_height / 2 + margin - 0.001
            or page.get_top()[1] > config.frame_height / 2 - margin + 0.001):
        raise ValueError('Page exceeds the course safe margin; reorganize the content.')


class ExpandedTeachingScene(TeachingScene):
    """Keep every top-level calculation in a card and check rendered updates."""

    def setup_narration(self):
        super().setup_narration()
        self._math_card_owners = {}
        self.panel_check_updates = 0
        self.panel_checks = 0
        self.worked_example_steps = 0
        self.worked_contexts = []

    def new_page(self, title, *blocks, gap=0.40):
        owners = {}
        wrapped = []
        for block in blocks:
            if isinstance(block, MathTex):
                card = panel(block, height=1.05, padding=0.34)
                owners[id(block)] = card
                wrapped.append(card)
            else:
                wrapped.append(block)
        result = super().new_page(title, *wrapped, gap=gap)
        self._math_card_owners = owners
        check_panels(self.page)
        check_frame(self.page)
        return result

    def explain(self, text, *objects, hold=1.0, pause_after=0.0):
        owners = getattr(self, '_math_card_owners', {})
        cards = tuple(owners.get(id(obj), obj) for obj in objects)
        check_panels(self.page)
        super().explain(text, *cards, hold=hold, pause_after=pause_after)
        check_panels(self.page)
        check_frame(self.page)

    def update_mobjects(self, dt):
        super().update_mobjects(dt)
        page = getattr(self, 'page', None)
        checked = check_panels(page)
        check_frame(page)
        if hasattr(self, 'panel_check_updates'):
            self.panel_check_updates += 1
            self.panel_checks += checked

    def guided_examples(self, lesson_id):
        for example_index, example in enumerate(load_examples()[lesson_id], 1):
            contexts = step_premises(example)
            # Lay out all possible premises at full size before showing any step.
            premise_math = {s: self.formula(s, 36)
                            for s in dict.fromkeys([example['premise'], *contexts])}
            premise_height = max(1.4, max(m.height for m in premise_math.values()) + 0.68)
            premises = {s: panel(m, width=10.8, height=premise_height, padding=0.34)
                        for s, m in premise_math.items()}
            premise = premises[example['premise']]
            rows = [self.formula(step['math'], 38) for step in example['steps']]
            height = max(1.4, max(row.height for row in rows) + 0.68)
            if height + premise_height + 0.35 > BODY_HEIGHT:
                raise ValueError('Worked example needs shorter rows, not smaller type.')
            cards = [panel(row, width=10.8, height=height, padding=0.34) for row in rows]
            active = cards[0]
            self.new_page(example['title'], premise, active, gap=0.35)
            for card in cards[1:]:
                card.move_to(active)
            for candidate in premises.values():
                if candidate is not premise:
                    candidate.move_to(premise)
            self.explain(example['prompt'], premise, hold=example['intro_seconds'])
            for index, (step, card, context) in enumerate(zip(example['steps'], cards, contexts)):
                next_premise = premises[context]
                outgoing = ([active] if index else [])
                if next_premise is not premise:
                    outgoing.append(premise)
                if outgoing:
                    self.play(*(FadeOut(obj) for obj in outgoing), run_time=0.4)
                    self.remove(*outgoing)
                    self.page[1].remove(*outgoing)
                # Keep the logical order without rearranging the frozen positions.
                self.page[1].remove(*list(self.page[1])).add(next_premise, card)
                reveal = [card]
                if next_premise is not premise:
                    reveal.insert(0, next_premise)
                active, premise = card, next_premise
                check_panels(self.page)
                self.explain(step['narration'], *reveal, hold=step['reading_seconds'])
                self.worked_example_steps += 1
                self.worked_contexts.append({
                    'lesson_id': lesson_id, 'example': example_index, 'step': index + 1,
                    'premise': context, 'math': step['math'],
                })

    def tear_down(self):
        check_panels(getattr(self, 'page', None))
        check_frame(getattr(self, 'page', None))
        destination = os.getenv('TEACHING_LAYOUT_AUDIT_PATH')
        if destination:
            Path(destination).write_text(json.dumps({
                'status': 'passed', 'render_updates_checked': self.panel_check_updates,
                'panel_checks': self.panel_checks, 'safe_margin': 0.5,
                'worked_example_steps': self.worked_example_steps,
                'worked_contexts': self.worked_contexts,
                'meaning': 'Geometric containment and recorded contexts; not listening or release approval.',
            }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        super().tear_down()

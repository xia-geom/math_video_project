"""Contained calculations and worked examples for the ten syllabus additions.

Opt-in scene base: no retiming of other lessons and no cloud speech in silent mode.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import yaml
from manim import FadeOut, MathTex

from tools.teaching_layout import BODY_HEIGHT, TeachingScene, assert_inside, panel

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / 'curriculum/worked_examples'


def load_examples():
    lessons = {}
    for path in sorted(EXAMPLES_DIR.glob('*.yaml')):
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        if data.get('version') != 1 or data['lesson_id'] in lessons:
            raise ValueError('Unsupported or duplicate worked-example record.')
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


class ExpandedTeachingScene(TeachingScene):
    """Keep every top-level calculation in a card and check rendered updates."""

    def setup_narration(self):
        super().setup_narration()
        self._math_card_owners = {}
        self.panel_check_updates = 0
        self.panel_checks = 0
        self.worked_example_steps = 0

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
        return result

    def explain(self, text, *objects, hold=1.0, pause_after=0.0):
        owners = getattr(self, '_math_card_owners', {})
        cards = tuple(owners.get(id(obj), obj) for obj in objects)
        check_panels(self.page)
        super().explain(text, *cards, hold=hold, pause_after=pause_after)
        check_panels(self.page)

    def update_mobjects(self, dt):
        super().update_mobjects(dt)
        checked = check_panels(getattr(self, 'page', None))
        if hasattr(self, 'panel_check_updates'):
            self.panel_check_updates += 1
            self.panel_checks += checked

    def guided_examples(self, lesson_id):
        for example in load_examples()[lesson_id]:
            premise = panel(self.formula(example['premise'], 36), width=10.8, height=1.4)
            rows = [self.formula(step['math'], 38) for step in example['steps']]
            height = max(1.4, max(row.height for row in rows) + 0.68)
            if height + premise.height + 0.35 > BODY_HEIGHT:
                raise ValueError('Worked example needs shorter rows, not smaller type.')
            cards = [panel(row, width=10.8, height=height, padding=0.34) for row in rows]
            active = cards[0]
            self.new_page(example['title'], premise, active, gap=0.35)
            for card in cards[1:]:
                card.move_to(active)
            self.explain(example['prompt'], premise, hold=example['intro_seconds'])
            for index, (step, card) in enumerate(zip(example['steps'], cards)):
                if index:
                    self.play(FadeOut(active), run_time=0.4)
                    self.remove(active)
                    self.page[1].remove(active).add(card)
                active = card
                check_panels(self.page)
                self.explain(step['narration'], active, hold=step['reading_seconds'])
                self.worked_example_steps += 1

    def tear_down(self):
        check_panels(getattr(self, 'page', None))
        destination = os.getenv('TEACHING_LAYOUT_AUDIT_PATH')
        if destination:
            Path(destination).write_text(json.dumps({
                'status': 'passed', 'render_updates_checked': self.panel_check_updates,
                'panel_checks': self.panel_checks,
                'worked_example_steps': self.worked_example_steps,
                'meaning': 'Geometric containment only; not listening or release approval.',
            }, indent=2) + '\n', encoding='utf-8')
        super().tear_down()

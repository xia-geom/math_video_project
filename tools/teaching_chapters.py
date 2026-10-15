"""Opt-in title and chapter cards for the two revision pilots.

The optional audit contains render evidence, not player-navigation metadata.
Other lessons retain their existing opening and page flow.
"""
from __future__ import annotations

from contextlib import nullcontext
import json
import os
from pathlib import Path

from manim import DL, DOWN, LEFT, WHITE, FadeIn, FadeOut, Text, VGroup, config

# The pilots use one teaching color; structure and wording carry emphasis.
INK = '#000000'
ACCENT = SUCCESS = ERROR = INK
SAFE_MARGIN = 0.5


def contrast_ratio(first, second='#FFFFFF'):
    def luminance(value):
        channels = [int(value.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                  for c in channels]
        return sum(c * w for c, w in zip(linear, (0.2126, 0.7152, 0.0722)))
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def assert_card_fits(card):
    if (card.get_left()[0] < -config.frame_width / 2 + SAFE_MARGIN
            or card.get_right()[0] > config.frame_width / 2 - SAFE_MARGIN
            or card.get_bottom()[1] < -config.frame_height / 2 + SAFE_MARGIN
            or card.get_top()[1] > config.frame_height / 2 - SAFE_MARGIN):
        raise ValueError('Chapter/title card exceeds safe margins; shorten or wrap the text.')


def clear_lesson_content(scene):
    outgoing = list(scene.mobjects)
    for item in outgoing:
        item.clear_updaters(recursive=True)
    if hasattr(scene, 'page'):
        scene.page = None
    if outgoing:
        scene.play(*(FadeOut(item) for item in outgoing), run_time=0.35)
        scene.remove(*outgoing)


def chapter_card(titles, active):
    if not titles or not 0 <= active < len(titles):
        raise ValueError('A chapter card needs an existing active chapter.')
    if len(set(titles)) != len(titles) or any(not title.strip() for title in titles):
        raise ValueError('Chapter titles must be nonempty and unique.')
    heading = Text('Plan de la vidéo', font_size=40, color=INK).move_to([0, 2.75, 0])
    rows = VGroup(*(Text(f'{index + 1}. {title}', font_size=30, color=INK,
                         weight='BOLD' if index == active else 'NORMAL')
                    for index, title in enumerate(titles)))
    # Pin the list's left edge: a longer bold row must not shift every item.
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.48).move_to([-5.3, 0.25, 0], aligned_edge=LEFT)
    card = VGroup(heading, rows)
    assert_card_fits(card)
    return card


def _present(scene, card, spoken, narration, hold, record):
    assert_card_fits(card)
    start = float(scene.renderer.time)
    scene.play(FadeIn(card), run_time=0.4)
    visible_from = float(scene.renderer.time)
    # The spoken cue starts only once the complete card is visible. The
    # voiceover context must finish before the card can leave the screen.
    with narration(spoken) if narration is not None else nullcontext():
        scene.wait(hold)
    speech_end = float(scene.renderer.time)
    scene.play(FadeOut(card), run_time=0.4)
    scene.remove(card)
    record.update(start=start, visible_from=visible_from, speech_end=speech_end,
                  end=float(scene.renderer.time), spoken=spoken, minimum_hold=hold)
    scene.chapter_review_events = [*getattr(scene, 'chapter_review_events', []), record]
    destination = os.getenv('TEACHING_CHAPTER_AUDIT_PATH')
    if destination:
        Path(destination).write_text(json.dumps(scene.chapter_review_events,
                                               ensure_ascii=False, indent=2) + '\n')


def play_lesson_opening(scene, title, objective, *, narration=None):
    from tools.faculty_branding import faculty_signature

    if getattr(scene, '_uqam_intro_played', False):
        raise RuntimeError('Duplicate UQAM opening: use one title card only.')
    if scene.mobjects:
        raise RuntimeError('The lesson title must precede lesson content.')
    scene._uqam_intro_played = True
    scene.camera.background_color = WHITE
    heading = Text(title, font_size=44, color=INK, weight='BOLD').move_to([0, 1.9, 0])
    label = Text('Objectif', font_size=28, color=ACCENT).move_to([0, 0.75, 0])
    goal = Text(objective, font_size=30, color=INK, line_spacing=1.25).move_to([0, -0.1, 0])
    logo = faculty_signature(width=3.6).to_corner(DL, buff=0.65)
    card = VGroup(heading, label, goal, logo)
    _present(scene, card, f'{title}. {objective.replace(chr(10), " ")}', narration, 4.0,
             {'kind': 'opening', 'title': title, 'logo': 'faculty_code_reconstruction',
              'logo_exact': False})


def play_chapter_outline(scene, titles, active, transition, *, narration=None):
    ordered = tuple(titles)
    previous = getattr(scene, '_chapter_titles', ordered)
    if previous != ordered:
        raise ValueError('Chapter names and order must remain identical throughout the lesson.')
    expected = getattr(scene, '_chapter_active', -1) + 1
    if active != expected:
        raise ValueError('Author each major chapter boundary exactly once, in order.')
    card = chapter_card(ordered, active)
    clear_lesson_content(scene)
    scene._chapter_titles, scene._chapter_active = ordered, active
    _present(scene, card, transition, narration, 4.0 if active == 0 else 3.0,
             {'kind': 'chapter', 'titles': list(ordered), 'active': active})

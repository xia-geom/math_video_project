"""Shared opening, authored chapter and closing cards for course lessons.

The optional audit contains render evidence, not player-navigation metadata.
Scenes author their conceptual boundaries; cards never infer them from pages.
"""
from __future__ import annotations

from contextlib import contextmanager, nullcontext
import json
import os
from pathlib import Path

from manim import DL, DOWN, LEFT, WHITE, FadeIn, FadeOut, MathTex, Text, VGroup, config

# The course uses one teaching color; structure and wording carry emphasis.
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


def _present(scene, card, spoken, narration, hold, record, *, leave_visible=False):
    assert_card_fits(card)
    start = float(scene.renderer.time)
    scene.play(FadeIn(card), run_time=0.4)
    visible_from = float(scene.renderer.time)
    # The spoken cue starts only once the complete card is visible. The
    # voiceover context must finish before the card can leave the screen.
    with narration(spoken) if narration is not None else nullcontext():
        scene.wait(hold)
    speech_end = float(scene.renderer.time)
    if not leave_visible:
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


@contextmanager
def _chapter_context(scene, preserve_content):
    if not preserve_content:
        clear_lesson_content(scene)
        yield
        return
    roots = list(scene.mobjects)
    family = {id(item): item for root in roots for item in root.get_family()}
    suspended = [(item, item.updating_suspended) for item in family.values()]
    page = getattr(scene, 'page', None)
    if hasattr(scene, 'page'):
        scene.page = None
    try:
        for item, _ in suspended:
            item.suspend_updating(recursive=False)
        if roots:
            scene.play(*(FadeOut(item, suspend_mobject_updating=False) for item in roots), run_time=0.35)
            scene.remove(*roots)
        yield
        if roots:
            scene.play(*(FadeIn(item, suspend_mobject_updating=False) for item in roots), run_time=0.35)
    finally:
        if hasattr(scene, 'page'):
            scene.page = page
        for item, was_suspended in suspended:
            if was_suspended:
                item.suspend_updating(recursive=False)
            else:
                item.resume_updating(recursive=False)


def play_chapter_outline(scene, titles, active, transition, *, narration=None,
                         preserve_content=False):
    ordered = tuple(titles)
    previous = getattr(scene, '_chapter_titles', ordered)
    if previous != ordered:
        raise ValueError('Chapter names and order must remain identical throughout the lesson.')
    expected = getattr(scene, '_chapter_active', -1) + 1
    if active != expected:
        raise ValueError('Author each major chapter boundary exactly once, in order.')
    card = chapter_card(ordered, active)
    scene._chapter_titles, scene._chapter_active = ordered, active
    with _chapter_context(scene, preserve_content):
        _present(scene, card, transition, narration, 4.0 if active == 0 else 3.0,
                 {'kind': 'chapter', 'titles': list(ordered), 'active': active,
                  'restores_context': preserve_content})


def play_lesson_closing(scene, title, recap, practice_tex, practice_task, *,
                        recap_spoken, practice_spoken, narration=None):
    """End each lesson with the same recap, practice prompt and final card.

    The practice reprises an example whose correction appeared in the lesson.
    Keep the final identity card visible through the last encoded frame.
    """
    from tools.faculty_branding import faculty_signature

    if getattr(scene, '_lesson_closing_played', False):
        raise RuntimeError('A lesson has one closing sequence.')
    if len(recap) != 3 or any(not line.strip() for line in recap):
        raise ValueError('The shared closing needs three concise takeaways.')
    scene._lesson_closing_played = True
    clear_lesson_content(scene)

    heading = Text('À retenir', font_size=40, color=INK,
                   weight='BOLD').move_to([0, 2.75, 0])
    rows = VGroup(*(Text(line, font_size=30, color=INK, line_spacing=1.2)
                    for line in recap))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to([0, 0.2, 0])
    _present(scene, VGroup(heading, rows), recap_spoken, narration, 8.0,
             {'kind': 'recap', 'title': title, 'points': list(recap)})

    heading = Text('À vous', font_size=40, color=INK,
                   weight='BOLD').move_to([0, 2.75, 0])
    cue = Text('Reprenez cet exemple sans regarder la correction.',
               font_size=30, color=INK).move_to([0, 1.45, 0])
    formula = MathTex(practice_tex, font_size=46, color=INK).move_to([0, 0, 0])
    task = Text(practice_task, font_size=30, color=INK,
                line_spacing=1.2).move_to([0, -1.65, 0])
    _present(scene, VGroup(heading, cue, formula, task), practice_spoken,
             narration, 8.0, {'kind': 'closing_practice', 'title': title,
                              'math': practice_tex, 'task': practice_task})

    heading = Text('Fin de la capsule', font_size=44, color=INK,
                   weight='BOLD').move_to([0, 1.6, 0])
    lesson = Text(title, font_size=32, color=INK).move_to([0, 0.2, 0])
    logo = faculty_signature(width=3.6).to_corner(DL, buff=0.65)
    _present(scene, VGroup(heading, lesson, logo),
             'Fin de la capsule. À vous de poursuivre.', narration, 3.0,
             {'kind': 'closing', 'title': title, 'logo_exact': False},
             leave_visible=True)

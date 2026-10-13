"""Regressions for confirmed course-review defects in lessons 31–43.

Exercise isolated narration setup with fake services so these checks never
need credentials, synthesize audio or mistake a silent preview for narration.
"""
from __future__ import annotations

import ast
import importlib.util
import re
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

from tools.course_catalog import ROOT, load_catalog, resolve

ENTRIES = load_catalog()[1]
NARRATION_LESSONS = (
    'du_cercle_unite_a_la_fonction_sinus', 'aire_du_cercle',
    'pythagore_par_les_aires', 'notation_sigma', 'implication_et_equivalence',
    'solutions_parasites', 'ordre_de_composition', 'annulation_dans_les_fractions',
)


def scene_path(lesson_id):
    return ROOT / resolve(lesson_id, ENTRIES)['scene_file']


def scene_method(lesson_id, name, namespace):
    tree = ast.parse(scene_path(lesson_id).read_text(encoding='utf-8'))
    methods = [node for node in ast.walk(tree)
               if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(methods) != 1:
        raise AssertionError((lesson_id, name, len(methods)))
    module = ast.Module(body=methods, type_ignores=[])
    exec(compile(module, str(scene_path(lesson_id)), 'exec'), namespace)
    return namespace[name]


def scene_geometry(lesson_id, method_name, names):
    """Build selected source statements with production style and temporary TeX."""
    import manim

    tree = ast.parse(scene_path(lesson_id).read_text(encoding='utf-8'))
    method = next(node for node in ast.walk(tree)
                  if isinstance(node, ast.FunctionDef) and node.name == method_name)
    statements = []
    for node in method.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            statements.append(node)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            receiver = node.value
            while isinstance(receiver, (ast.Call, ast.Attribute)):
                receiver = receiver.func if isinstance(receiver, ast.Call) else receiver.value
            if isinstance(receiver, ast.Name) and receiver.id in names:
                statements.append(node)
    namespace = dict(vars(manim), ACCENT=manim.BLUE_D, GOOD=manim.GREEN_D, ERROR=manim.RED_D)
    with tempfile.TemporaryDirectory(prefix='course-review-c-') as temp:
        with scene_text_defaults(lesson_id), manim.tempconfig(
                {'media_dir': temp, 'tex_dir': str(Path(temp) / 'Tex')}):
            exec(compile(ast.Module(body=statements, type_ignores=[]), '<actual-scene-geometry>', 'exec'), namespace)
    return namespace


@contextmanager
def scene_text_defaults(lesson_id):
    """Use the scene's fresh-process defaults and restore the caller's defaults."""
    import manim

    namespace = dict(vars(manim))
    classes = [namespace[name] for name in ('Text', 'Tex', 'MathTex')]
    previous = [cls.__dict__['__init__'] for cls in classes]
    try:
        for cls in classes:
            cls.set_default()
        tree = ast.parse(scene_path(lesson_id).read_text(encoding='utf-8'))
        defaults = [node for node in tree.body
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Name)
                    and node.value.func.value.id in {'Text', 'Tex', 'MathTex'}
                    and node.value.func.attr == 'set_default']
        exec(compile(ast.Module(body=defaults, type_ignores=[]), '<actual-text-defaults>', 'exec'), namespace)
        yield
    finally:
        for cls, original in zip(classes, previous):
            cls.__init__ = original


def setup(lesson_id, environment, *, service=None, runtime=True):
    namespace = {
        'os': SimpleNamespace(getenv=environment.get, environ=environment),
        'load_dotenv': None,
        'VoiceoverScene': object if runtime else None,
        'AzureService': service if runtime else None,
        'tts': SimpleNamespace(VOICE_ID='selected-existing-voice'),
        'VOICE_ID': 'selected-existing-voice',
        'azure_service_kwargs': lambda: {'voice': 'selected-existing-voice'},
    }
    received = []
    scene = SimpleNamespace(set_speech_service=received.append)
    scene_method(lesson_id, '_setup_voiceover', namespace)(scene)
    return scene, received


class NarrationModeTests(unittest.TestCase):
    def test_explicit_silent_mode_needs_neither_runtime_nor_credentials(self):
        for lesson_id in NARRATION_LESSONS:
            with self.subTest(lesson_id=lesson_id):
                scene, services = setup(lesson_id, {'MANIM_DISABLE_VOICEOVER': '1'}, runtime=False)
                self.assertFalse(scene._voiceover_enabled)
                self.assertEqual(services, [])

    def test_missing_credentials_fail_instead_of_producing_silent_success(self):
        for lesson_id in NARRATION_LESSONS:
            with self.subTest(lesson_id=lesson_id), self.assertRaisesRegex(RuntimeError, 'credentials'):
                setup(lesson_id, {}, service=lambda **kwargs: object())

    def test_missing_optional_runtime_fails_in_narrated_mode(self):
        for lesson_id in ('du_cercle_unite_a_la_fonction_sinus', 'notation_sigma',
                          'ordre_de_composition', 'annulation_dans_les_fractions'):
            with self.subTest(lesson_id=lesson_id), self.assertRaisesRegex(RuntimeError, 'manim-voiceover'):
                setup(lesson_id, {}, runtime=False)

    def test_service_failure_is_not_swallowed(self):
        def unavailable(**kwargs):
            raise RuntimeError('service unavailable')

        for lesson_id in NARRATION_LESSONS:
            with self.subTest(lesson_id=lesson_id), self.assertRaisesRegex(RuntimeError, 'service unavailable'):
                setup(lesson_id, {'SPEECH_KEY': 'unit-test-key', 'SPEECH_REGION': 'unit-test-region'},
                      service=unavailable)

    def test_success_keeps_the_selected_existing_voice(self):
        for lesson_id in NARRATION_LESSONS:
            with self.subTest(lesson_id=lesson_id):
                scene, services = setup(
                    lesson_id, {'SPEECH_KEY': 'unit-test-key', 'SPEECH_REGION': 'unit-test-region'},
                    service=lambda **kwargs: kwargs,
                )
                self.assertTrue(scene._voiceover_enabled)
                self.assertEqual(services, [{'voice': 'selected-existing-voice'}])

    def test_circle_to_sine_narration_inherits_shared_rate(self):
        received = []

        @contextmanager
        def voiceover(**kwargs):
            received.append(kwargs)
            yield SimpleNamespace(duration=2.0)

        namespace = {
            'contextmanager': contextmanager,
            'tts': SimpleNamespace(
                ssml=lambda text, rate='shared-teaching-rate': f'{rate}:{text}',
                strip_ssml=lambda text: text,
            ),
        }
        scene = SimpleNamespace(_voiceover_enabled=True, voiceover=voiceover)
        with scene_method('du_cercle_unite_a_la_fonction_sinus', 'narrated', namespace)(scene, 'Une phrase complète.'):
            pass
        self.assertEqual(received, [{'text': 'shared-teaching-rate:Une phrase complète.',
                                     'subcaption': 'Une phrase complète.'}])


class DisplayedMathematicsTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual opening text geometry')
    def test_sine_opening_fits_portable_text_metrics_without_shrinking(self):
        import manim
        import manimpango

        lesson_id = 'du_cercle_unite_a_la_fonction_sinus'
        tree = ast.parse(scene_path(lesson_id).read_text(encoding='utf-8'))
        method = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef) and node.name == 'show_intro_static')
        names = {'title', 'subtitle', 'center', 'circle'}
        statements = [node for node in method.body if isinstance(node, ast.Assign)
                      and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names]
        title = statements[0]
        constructor = next(node for node in ast.walk(title) if isinstance(node, ast.Call)
                           and isinstance(node.func, ast.Name) and node.func.id == 'Text')
        self.assertEqual(ast.literal_eval(constructor.args[0]).replace('\n', ' '),
                         'Comment un cercle dessine-t-il une vague ?')
        # The same source used wider fallback metrics on the hosted Linux runner.
        # Exercise its authored geometry with available wide serif/sans families,
        # as well as the platform default, without rendering a Scene.
        installed = set(manimpango.list_fonts())
        fonts = [''] + [font for font in ('DejaVu Sans', 'DejaVu Serif', 'Verdana') if font in installed]
        with tempfile.TemporaryDirectory(prefix='course-review-c-title-') as temp:
            with scene_text_defaults(lesson_id), manim.tempconfig(
                    {'media_dir': temp, 'frame_width': 128 / 9, 'frame_height': 8}):
                for font in fonts:
                    with self.subTest(font=font or 'platform default'):
                        def text_with_metrics(*args, **kwargs):
                            return manim.Text(*args, font=font, **kwargs)

                        namespace = dict(vars(manim), Text=text_with_metrics,
                                         RADIUS_COLOR=manim.BLUE_D, CIRCLE_COLOR=manim.GREY_D)
                        exec(compile(ast.Module(body=statements, type_ignores=[]),
                                     '<actual-opening-geometry>', 'exec'), namespace)
                        title, subtitle, circle = (namespace[name] for name in ('title', 'subtitle', 'circle'))
                        self.assertAlmostEqual(title.font_size, 42)
                        self.assertEqual(title.weight, 'BOLD')
                        self.assertAlmostEqual(subtitle.font_size, 27)
                        self.assertAlmostEqual(circle.width, 3.1)
                        for text in (title, subtitle):
                            self.assertGreaterEqual(text.get_left()[0], -manim.config.frame_width / 2 + 0.5)
                            self.assertLessEqual(text.get_right()[0], manim.config.frame_width / 2 - 0.5)
                        self.assertAlmostEqual(title.get_top()[1], 3.5)
                        self.assertGreater(title.get_bottom()[1] - subtitle.get_top()[1], 0.20)
                        self.assertGreater(subtitle.get_bottom()[1] - circle.get_top()[1], 0.20)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual tick/callout clearance')
    def test_subset_callout_clears_ticks_and_lower_number_line(self):
        values = scene_geometry('implication_et_equivalence', '_see_the_solution_sets',
                                {'p_label', 'p_line', 'p_group', 'q_label', 'q_line', 'q_group',
                                 'inclusion', 'inclusion_box'})
        box = values['inclusion_box']
        self.assertGreater(values['p_line'].numbers.get_bottom()[1] - box.get_top()[1], 0.1)
        self.assertGreater(box.get_bottom()[1] - values['q_line'].n2p(0)[1], 0.4)
        self.assertGreater(box.get_left()[0] - values['q_label'].get_right()[0], 0.1)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual highlighted value clearance')
    def test_highlighted_square_output_clears_line_dot_and_both_arrows(self):
        values = scene_geometry('solutions_parasites', '_why_the_extra_value_appears',
                                {'input_label', 'input_line', 'input_group', 'output_label', 'output_line',
                                 'output_group', 'minus_two', 'plus_two', 'four', 'minus_dot', 'plus_dot',
                                 'output_dot', 'four_label', 'arrow_left', 'arrow_right'})
        label = values['four_label']
        self.assertGreater(label.get_bottom()[1] - values['output_line'].n2p(4)[1], 0.2)
        self.assertGreater(label.get_left()[0] - values['output_dot'].get_right()[0], 0.1)
        for name in ('arrow_left', 'arrow_right'):
            arrow = values[name]
            for alpha in values['np'].linspace(0, 1, 1000):
                point = (1 - alpha) * arrow.get_start() + alpha * arrow.get_end()
                self.assertFalse(label.get_left()[0] - 0.1 <= point[0] <= label.get_right()[0] + 0.1
                                 and label.get_bottom()[1] - 0.1 <= point[1] <= label.get_top()[1] + 0.1,
                                 f'{name} crosses the highlighted output label.')

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual input tick clearance')
    def test_square_machine_arrows_clear_positive_two_tick_number(self):
        values = scene_geometry('solutions_parasites', '_why_the_extra_value_appears',
                                {'input_label', 'input_line', 'input_group', 'input_two_tick',
                                 'output_label', 'output_line', 'output_group', 'minus_two',
                                 'plus_two', 'four', 'minus_dot', 'plus_dot', 'output_dot',
                                 'arrow_left', 'arrow_right'})
        line = values['input_line']
        self.assertEqual([number.get_value() for number in line.numbers], list(range(-3, 4)))
        for number in line.numbers:
            self.assertEqual(number.num_decimal_places, 0)
            self.assertLess(abs(number.get_center()[0] - line.n2p(number.get_value())[0]), 0.35)
            if number.get_value() != 2:
                continue
            for name in ('arrow_left', 'arrow_right'):
                arrow = values[name]
                for alpha in values['np'].linspace(0, 1, 1000):
                    point = (1 - alpha) * arrow.get_start() + alpha * arrow.get_end()
                    self.assertFalse(number.get_left()[0] - 0.08 <= point[0] <= number.get_right()[0] + 0.08
                                     and number.get_bottom()[1] - 0.08 <= point[1] <= number.get_top()[1] + 0.08,
                                     f'{name} crosses input tick {number.get_value()}.')

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual text defaults')
    def test_caption_geometry_ignores_and_restores_unrelated_text_defaults(self):
        import manim

        original = manim.Text.__dict__['__init__']
        try:
            manim.Text.set_default(font='Arial', font_size=99, line_spacing=2)
            unrelated = manim.Text.__dict__['__init__']
            self.test_implication_caption_stays_inside_p_and_away_from_p_label()
            self.assertIs(manim.Text.__dict__['__init__'], unrelated)
        finally:
            manim.Text.__init__ = original

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual tick glyphs')
    def test_requested_number_line_ticks_have_visible_black_glyphs(self):
        import manim

        with tempfile.TemporaryDirectory(prefix='course-review-c-') as temp:
            with manim.tempconfig({'media_dir': temp, 'tex_dir': str(Path(temp) / 'Tex')}):
                for lesson_id, expected_count in (('implication_et_equivalence', 4), ('solutions_parasites', 3)):
                    tree = ast.parse(scene_path(lesson_id).read_text(encoding='utf-8'))
                    calls = [node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
                             and any(isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                                     and call.func.id == 'NumberLine' for call in ast.walk(node.value))]
                    self.assertEqual(len(calls), expected_count)
                    for call in calls:
                        with scene_text_defaults(lesson_id):
                            line = eval(compile(ast.Expression(call), '<actual-number-line>', 'eval'), dict(vars(manim)))
                        self.assertGreater(len(line.numbers), 0)
                        for number in line.numbers:
                            self.assertEqual(number.num_decimal_places, 0,
                                             'Integer-step ticks must retain their automatic integer formatting.')
                            glyphs = number.family_members_with_points()
                            self.assertGreater(len(glyphs), 0)
                            for glyph in glyphs:
                                self.assertEqual(glyph.get_fill_color(), manim.BLACK)
                                self.assertEqual(glyph.get_fill_opacity(), 1)

    def test_fraction_replacement_formulas_clear_their_shared_slot(self):
        tree = ast.parse(scene_path('annulation_dans_les_fractions').read_text(encoding='utf-8'))
        plays = sorted((node for node in ast.walk(tree) if isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute) and node.func.attr == 'play'),
                       key=lambda node: node.lineno)

        def indices(animation, target):
            return [i for i, play in enumerate(plays)
                    if any(isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                           and arg.func.id == animation and any(isinstance(obj, ast.Name)
                           and obj.id == target for obj in arg.args) for arg in play.args)]

        for outgoing, incoming, fraction in (('product', 'decomposition', 0.32), ('sums', 'evaluation', 0.30),
                                             ('algebra', 'algebra_steps', 0.30),
                                             ('original', 'factoring', 0.34), ('factoring', 'factored', 0.34)):
            before, after = indices('FadeOut', outgoing), indices('FadeIn', incoming)
            self.assertEqual(len(before), 1)
            self.assertEqual(len(after), 1)
            self.assertEqual(after[0], before[0] + 1)
            durations = [next(k.value for k in plays[i].keywords if k.arg == 'run_time')
                         for i in (before[0], after[0])]
            actual = [eval(compile(ast.Expression(d), '<transition-duration>', 'eval'), {'duration': 5.5})
                      for d in durations]
            self.assertTrue(all(value > 0 for value in actual))
            self.assertAlmostEqual(sum(actual), fraction * 5.5)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual notation geometry')
    def test_sigma_focus_targets_match_their_spoken_roles(self):
        import manim

        namespace = dict(vars(manim))
        build = scene_method('notation_sigma', '_sigma_parts', namespace)
        with tempfile.TemporaryDirectory(prefix='course-review-c-') as temp:
            with scene_text_defaults('notation_sigma'), manim.tempconfig(
                    {'media_dir': temp, 'tex_dir': str(Path(temp) / 'Tex')}):
                parts = build()
        self.assertEqual([part.tex_string for part in parts], [r'\sum', 'i=0', '4', '(2i+1)'])
        operator, lower, upper, rule = parts
        self.assertLess(lower.get_top()[1], operator.get_bottom()[1])
        self.assertGreater(upper.get_bottom()[1], operator.get_top()[1])
        self.assertGreater(rule.get_left()[0], operator.get_right()[0])

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual reveal style')
    def test_sigma_value_reveals_preserve_translucent_box_and_opaque_digits(self):
        import manim

        namespace = dict(vars(manim), ACCENT=manim.BLUE_D, LIGHT_ACCENT=0.10)
        build = scene_method('notation_sigma', '_value_cell', namespace)
        tree = ast.parse(scene_path('notation_sigma').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'acte_3_boucle_visible')
        self.assertFalse(any(isinstance(n, ast.Attribute) and n.attr == 'set_opacity' for n in ast.walk(method)))
        reveals = [n for n in ast.walk(method) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Name) and n.func.id == 'FadeIn'
                   and isinstance(n.args[0], ast.Subscript)
                   and isinstance(n.args[0].value, ast.Name) and n.args[0].value.id == 'value_cells']
        self.assertEqual(len(reveals), 2)
        with tempfile.TemporaryDirectory(prefix='course-review-c-') as temp:
            with scene_text_defaults('notation_sigma'), manim.tempconfig(
                    {'media_dir': temp, 'tex_dir': str(Path(temp) / 'Tex')}):
                namespace.update(value_cells=manim.VGroup(build(1), build(3)), i=1)
                for reveal in reveals:
                    animation = eval(compile(ast.Expression(reveal), '<actual-value-reveal>', 'eval'), namespace)
                    animation.begin()
                    animation.interpolate(1)
                    animation.finish()
        for box, number in namespace['value_cells']:
            self.assertAlmostEqual(float(box.get_fill_opacity()), 0.10)
            glyphs = number.family_members_with_points()
            self.assertTrue(glyphs)
            for glyph in glyphs:
                self.assertAlmostEqual(float(glyph.get_fill_opacity()), 1.0)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual containment geometry')
    def test_implication_caption_stays_inside_p_and_away_from_p_label(self):
        import manim

        tree = ast.parse(scene_path('implication_et_equivalence').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_formal_meaning')
        names = {'q_box', 'q_text', 'p_box', 'p_text', 'inside_caption'}
        statements = []
        for node in method.body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
                statements.append(node)
            elif (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                  and isinstance(node.value.func, ast.Attribute)
                  and isinstance(node.value.func.value, ast.Name) and node.value.func.value.id in names):
                statements.append(node)
        namespace = dict(vars(manim), ACCENT=manim.BLUE_D, GOOD=manim.GREEN_D)
        with tempfile.TemporaryDirectory(prefix='course-review-c-') as temp:
            with scene_text_defaults('implication_et_equivalence'), manim.tempconfig(
                    {'media_dir': temp, 'tex_dir': str(Path(temp) / 'Tex')}):
                exec(compile(ast.Module(body=statements, type_ignores=[]), '<actual-inclusion-geometry>', 'exec'), namespace)
        box, caption, label = [namespace[name] for name in ('p_box', 'inside_caption', 'p_text')]
        self.assertGreater(caption.get_left()[0] - box.get_left()[0], 0.1)
        self.assertGreater(box.get_right()[0] - caption.get_right()[0], 0.1)
        self.assertGreater(caption.get_bottom()[1] - box.get_bottom()[1], 0.1)
        self.assertGreater(label.get_bottom()[1] - caption.get_top()[1], 0.1)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual card geometry')
    def test_candidate_substitutions_fit_their_cards_without_shrinking(self):
        import manim

        lesson_id = 'solutions_parasites'
        namespace = dict(vars(manim), GOOD=manim.GREEN_D, ERROR=manim.RED_D)
        build = scene_method(lesson_id, '_candidate_card', namespace)
        tree = ast.parse(scene_path(lesson_id).read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_test_candidates')
        calls = [n.value for n in method.body if isinstance(n, ast.Assign)
                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ('good_card', 'bad_card')]
        self.assertEqual(len(calls), 2)
        with tempfile.TemporaryDirectory(prefix='course-review-c-') as temp:
            with scene_text_defaults(lesson_id), manim.tempconfig(
                    {'media_dir': temp, 'tex_dir': str(Path(temp) / 'Tex')}):
                for call in calls:
                    args = [eval(compile(ast.Expression(arg), '<actual-candidate-card>', 'eval'), namespace)
                            for arg in call.args]
                    box, content = build(None, *args)
                    self.assertGreater(content.get_left()[0] - box.get_left()[0], 0.2)
                    self.assertGreater(box.get_right()[0] - content.get_right()[0], 0.2)
                    self.assertGreater(content.get_bottom()[1] - box.get_bottom()[1], 0.2)
                    self.assertGreater(box.get_top()[1] - content.get_top()[1], 0.2)
                    self.assertGreaterEqual(content[1].font_size, 45)
                    self.assertLess(box.height, 3.6)

    def test_circle_to_sine_shared_formula_slot_clears_before_reuse(self):
        tree = ast.parse(scene_path('du_cercle_unite_a_la_fonction_sinus').read_text(encoding='utf-8'))
        plays = sorted((node for node in ast.walk(tree)
                        if isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr == 'play'), key=lambda node: node.lineno)

        def contains(play, animation, target):
            return any(isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Name) and node.func.id == animation
                       and any(isinstance(arg, ast.Name) and arg.id == target for arg in node.args)
                       for node in ast.walk(play))

        outgoing = [i for i, play in enumerate(plays) if contains(play, 'FadeOut', 'unit_arc_formula')]
        incoming = [i for i, play in enumerate(plays) if contains(play, 'FadeIn', 'graph_point_formula')]
        self.assertEqual(len(outgoing), 1)
        self.assertEqual(len(incoming), 1)
        # Separate sequential play calls prevent both formulas from becoming
        # partially visible in the same screen slot during an encoded transition.
        self.assertLess(outgoing[0], incoming[0])
        durations = [ast.literal_eval(next(k.value for k in plays[i].keywords if k.arg == 'run_time'))
                     for i in (outgoing[0], incoming[0])]
        self.assertTrue(all(duration > 0 for duration in durations))
        self.assertAlmostEqual(sum(durations), 0.9)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual fade interpolation')
    def test_period_formula_replacement_never_overlays_visible_formulas(self):
        import manim

        tree = ast.parse(scene_path('du_cercle_unite_a_la_fonction_sinus').read_text(encoding='utf-8'))
        period = next(node for node in ast.walk(tree) if isinstance(node, ast.With)
                      and any(isinstance(part, ast.Constant) and part.value == 'P5_period'
                              for part in ast.walk(node.items[0].context_expr)))
        plays = []
        for statement in period.body:
            if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
                continue
            call = statement.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == 'add':
                break
            if isinstance(call.func, ast.Attribute) and call.func.attr == 'play':
                plays.append(statement)
        self.assertTrue(plays)
        # Filled stand-ins occupy the shared formula slot. Execute the actual
        # authored play calls using Manim's fade interpolation, without rendering.
        names = ('graph_point_formula', 'periodic_formula', 'bridge_line',
                 'height_projection', 'height_scale')
        objects = {name: manim.Square(fill_opacity=1, stroke_width=0) for name in names}
        outgoing, incoming = (objects[name] for name in names[:2])
        live = set(objects.values()) - {incoming}
        durations = []

        def play(*animations, run_time):
            durations.append(run_time)
            self.assertGreater(run_time, 0)
            for animation in animations:
                if animation.is_introducer():
                    live.add(animation.mobject)
                animation.begin()
            for frame in range(round(run_time * 60) + 1):
                alpha = min(1, frame / (run_time * 60))
                for animation in animations:
                    animation.interpolate(alpha)
                visible = [obj in live and obj.get_fill_opacity() > 1e-6
                           for obj in (outgoing, incoming)]
                self.assertFalse(all(visible), 'Both formulas visible in the shared slot')
            for animation in animations:
                animation.finish()
                animation.clean_up_from_scene(probe)

        probe = SimpleNamespace(play=play, remove=lambda *items: live.difference_update(items))
        namespace = dict(vars(manim), self=probe, **objects)
        exec(compile(ast.Module(body=plays, type_ignores=[]), '<actual-period-transition>', 'exec'), namespace)
        self.assertAlmostEqual(sum(durations), 0.8)
        self.assertNotIn(outgoing, live)
        self.assertIn(incoming, live)
        self.assertAlmostEqual(incoming.get_fill_opacity(), 1)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual moving labels')
    def test_sine_origin_and_period_caption_clear_plot_geometry(self):
        import manim
        import numpy as np

        lesson_id = 'du_cercle_unite_a_la_fonction_sinus'
        tree = ast.parse(scene_path(lesson_id).read_text(encoding='utf-8'))
        scene = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                     and node.name == 'SineCurveUnitCircle')
        members = [node for node in scene.body if isinstance(node, ast.Assign)
                   or isinstance(node, ast.FunctionDef) and node.name in ('_curve_x', '_graph_point')]
        geometry_class = ast.ClassDef(name='Geometry', bases=[], keywords=[], body=members, decorator_list=[])
        method = next(node for node in scene.body if isinstance(node, ast.FunctionDef)
                      and node.name == '_build_main_scene')
        names = {'graph_x_axis', 'graph_y_axis', 'x_ticks', 'x_labels',
                 'periodic_formula', 'same_height_label'}
        statements = []
        for node in method.body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
                statements.append(node)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                receiver = node.value.func
                if isinstance(receiver, ast.Attribute) and isinstance(receiver.value, ast.Name) and receiver.value.id in names:
                    statements.append(node)
            elif isinstance(node, ast.For) and any(isinstance(part, ast.Name) and part.id == 'x_labels'
                                                  for part in ast.walk(node)):
                statements.append(node)
        namespace = dict(vars(manim), np=np, INK=manim.BLACK, RADIUS_COLOR=manim.BLUE_D)
        module = ast.fix_missing_locations(ast.Module(body=[geometry_class], type_ignores=[]))
        exec(compile(module, '<actual-sine-geometry>', 'exec'), namespace)
        namespace['self'] = namespace['Geometry']()
        namespace['theta'] = manim.ValueTracker(manim.TAU)
        with tempfile.TemporaryDirectory(prefix='course-review-c-') as temp:
            with scene_text_defaults(lesson_id), manim.tempconfig(
                    {'media_dir': temp, 'tex_dir': str(Path(temp) / 'Tex')}):
                exec(compile(ast.Module(body=statements, type_ignores=[]), '<actual-sine-labels>', 'exec'), namespace)
                geometry = namespace['self']
                zero = namespace['x_labels'][0]
                self.assertGreater(geometry.CURVE_START[0] - zero.get_right()[0], 0.09)
                self.assertGreater(-zero.get_top()[1], 0.09)
                label = namespace['same_height_label']
                for theta in np.linspace(manim.TAU, 2 * manim.TAU, 401):
                    namespace['theta'].set_value(theta)
                    label.update(0)
                    # The caption follows the paired points horizontally in a
                    # clear band above every possible curve/connector height.
                    expected_x = (geometry._curve_x(theta - manim.TAU) + geometry._curve_x(theta)) / 2
                    self.assertAlmostEqual(label.get_center()[0], expected_x)
                    self.assertGreater(label.get_bottom()[1] - geometry.UNIT_SCALE, 0.3)
                    self.assertGreater(namespace['periodic_formula'].get_bottom()[1] - label.get_top()[1], 0.2)
                    self.assertGreater(label.get_left()[0], -manim.config.frame_width / 2 + 0.2)
                    self.assertLess(label.get_right()[0], manim.config.frame_width / 2 - 0.2)

    def test_cancelled_fraction_displays_all_original_denominator_zeros(self):
        tree = ast.parse(scene_path('annulation_dans_les_fractions').read_text(encoding='utf-8'))
        assignment = next(node for node in ast.walk(tree)
                          if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == 'restriction'
                                  for target in node.targets))
        displayed = ast.literal_eval(assignment.value.args[0])
        excluded = {int(value) for value in re.findall(r'x\\neq(-?\d+)', displayed)}
        # The original denominator x(x+5), before cancelling x, vanishes twice.
        denominator_zeros = {x for x in range(-10, 11) if x * (x + 5) == 0}
        self.assertEqual(excluded, denominator_zeros)
        for x in set(range(-10, 11)) - excluded:
            self.assertAlmostEqual(x * (x + 2) / (x * (x + 5)), (x + 2) / (x + 5))

    def test_circle_subdivision_counts_have_explicit_visible_ink(self):
        tree = ast.parse(scene_path('aire_du_cercle').read_text(encoding='utf-8'))
        counts = [node for node in ast.walk(tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                  and node.func.id == 'Integer']
        self.assertEqual(len(counts), 2)
        for count in counts:
            color = next(keyword.value for keyword in count.keywords if keyword.arg == 'color')
            self.assertIsInstance(color, ast.Name)
            self.assertEqual(color.id, 'BLACK', 'A white count disappears on the white canvas.')
        labels = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                  and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('r_label_a', 'r_label_b')]
        self.assertEqual(len(labels), 2)
        for label in labels:
            tex = label.value.func.value
            color = next(keyword.value for keyword in tex.keywords if keyword.arg == 'color')
            self.assertEqual(color.id, 'BLUE_D', 'Radius labels need dark ink over the pale wedge.')


if __name__ == '__main__':
    unittest.main()

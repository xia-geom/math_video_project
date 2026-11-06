"""Source-linked regressions for confirmed course-review findings, group B.

Core checks require no Manim; geometry checks use it when available and otherwise
skip. No check synthesizes narration or renders a video.
"""
from __future__ import annotations

import ast
import importlib.util
import math
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tools import tts
from tools.course_catalog import load_catalog, resolve

ROOT = Path(__file__).resolve().parents[1]
NARRATION_LESSON_IDS = {
    'exponentielles_et_logarithmes', 'principe_fondamental_du_denombrement',
    'permutation_arrangement_combinaison', 'repetitions_en_denombrement',
    'vecteurs_deplacement_et_composantes', 'operations_sur_les_vecteurs',
    'vecteurs_dans_r2_et_r3', 'lire_et_appliquer_une_matrice',
    'operations_sur_les_matrices', 'determinant_et_matrice_inverse',
}


def construct_statements(lesson_id):
    entry = resolve(lesson_id, load_catalog()[1])
    tree = ast.parse((ROOT / entry['scene_file']).read_text(encoding='utf-8'))
    scene = next(node for node in tree.body
                 if isinstance(node, ast.ClassDef) and node.name == entry['scene_class'])
    return next(node.body for node in scene.body
                if isinstance(node, ast.FunctionDef) and node.name == 'construct')


def assignment_name(node):
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
        return node.targets[0].id
    return None


def scene_method(lesson_id, method):
    entry = resolve(lesson_id, load_catalog()[1])
    tree = ast.parse((ROOT / entry['scene_file']).read_text(encoding='utf-8'))
    return next(node for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name == method)


def narration_setups():
    """Run the actual scene methods with cloud/Manim boundaries mocked."""
    entries = load_catalog()[1]
    for lesson_id in sorted(NARRATION_LESSON_IDS):
        entry = resolve(lesson_id, entries)
        tree = ast.parse((ROOT / entry['scene_file']).read_text(encoding='utf-8'))
        methods = [node for node in ast.walk(tree)
                   if isinstance(node, ast.FunctionDef) and node.name == '_setup_voiceover']
        assert len(methods) == 1, lesson_id
        yield lesson_id, methods[0]


def geometry_selection(statements, names):
    """Extract actual assignments and placement calls for selected objects."""
    def receiver(node):
        value = node.value if isinstance(node, ast.Expr) else None
        while isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
            value = value.func.value
        while isinstance(value, ast.Attribute):
            value = value.value
        return value.id if isinstance(value, ast.Name) else None

    return [node for node in statements if assignment_name(node) in names
            or receiver(node) in names]


def build_geometry(lesson_id, statements, methods=()):
    import manim

    namespace = dict(vars(manim), ACCENT=manim.BLACK, RESULT=manim.BLACK,
                     GOOD=manim.BLACK, WARN=manim.BLACK, PALE=manim.GRAY, SOFT=manim.GRAY,
                     SECONDARY=manim.GRAY, ERROR=manim.BLACK)
    entry = resolve(lesson_id, load_catalog()[1])
    tree = ast.parse((ROOT / entry['scene_file']).read_text())
    for node in tree.body:
        if assignment_name(node) in {'TITLE_SIZE', 'SUBTITLE_SIZE', 'UNIT', 'DIAGRAM_ORIGIN',
                                     'A_MATRIX', 'P_VECTOR', 'Q_VECTOR'}:
            exec(compile(ast.Module(body=[node], type_ignores=[]), '<actual-style>', 'exec'), namespace)
    helper = ast.ClassDef(name='GeometryHelper', bases=[], keywords=[],
                         body=[scene_method(lesson_id, name) for name in methods] or [ast.Pass()],
                         decorator_list=[])
    exec(compile(ast.fix_missing_locations(ast.Module(body=[helper], type_ignores=[])),
                 '<actual-geometry-helpers>', 'exec'), namespace)
    namespace['self'] = namespace['GeometryHelper']()
    with tempfile.TemporaryDirectory(prefix='course-review-b-') as temp:
        with manim.tempconfig({'media_dir': temp, 'tex_dir': str(Path(temp) / 'Tex')}):
            with scene_text_defaults(tree, namespace):
                exec(compile(ast.Module(body=statements, type_ignores=[]), '<actual-geometry>', 'exec'), namespace)
    return namespace


@contextmanager
def scene_text_defaults(tree, namespace):
    """Match a fresh render process, without leaking class defaults to other tests."""
    classes = [namespace[name] for name in ('Text', 'Tex', 'MathTex')]
    previous = [cls.__dict__['__init__'] for cls in classes]
    try:
        for cls in classes:
            cls.set_default()
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


class NarrationContractTests(unittest.TestCase):
    def execute(self, node, service, environment):
        globals_ = {'os': os, 'tts': tts, 'load_dotenv': None,
                    'VoiceoverScene': object, 'AzureService': service}
        module = ast.Module(body=[node], type_ignores=[])
        exec(compile(module, '<actual-scene-narration-setup>', 'exec'), globals_)
        scene = SimpleNamespace(set_speech_service=Mock())
        with patch.dict(os.environ, environment, clear=True):
            globals_['_setup_voiceover'](scene)
        return scene

    def test_explicit_silent_mode_never_initializes_cloud(self):
        for lesson_id, node in narration_setups():
            with self.subTest(lesson=lesson_id):
                service = Mock(side_effect=AssertionError('Unexpected cloud call'))
                scene = self.execute(node, service, {'MANIM_DISABLE_VOICEOVER': '1'})
                self.assertFalse(scene._voiceover_enabled)
                service.assert_not_called()

    def test_requested_narration_rejects_missing_adapter(self):
        for lesson_id, node in narration_setups():
            with self.subTest(lesson=lesson_id), self.assertRaisesRegex(RuntimeError, 'Narration requires'):
                self.execute(node, None, {})

    def test_requested_narration_rejects_missing_credentials_before_service(self):
        for lesson_id, node in narration_setups():
            service = Mock()
            with self.subTest(lesson=lesson_id), self.assertRaisesRegex(RuntimeError, 'SPEECH_KEY'):
                self.execute(node, service, {})
            service.assert_not_called()

    def test_adapter_failure_is_not_silently_accepted(self):
        for lesson_id, node in narration_setups():
            with self.subTest(lesson=lesson_id), self.assertRaisesRegex(RuntimeError, 'adapter unavailable'):
                self.execute(node, Mock(side_effect=RuntimeError('adapter unavailable')),
                             {'SPEECH_KEY': 'unit-test-placeholder', 'SPEECH_REGION': 'canadacentral'})

    def test_success_retains_shared_voice_and_enables_narration(self):
        for lesson_id, node in narration_setups():
            with self.subTest(lesson=lesson_id):
                service = Mock()
                scene = self.execute(node, service,
                                     {'SPEECH_KEY': 'unit-test-placeholder', 'SPEECH_REGION': 'canadacentral'})
                service.assert_called_once_with(voice=tts.VOICE_ID)
                scene.set_speech_service.assert_called_once_with(service.return_value)
                self.assertTrue(scene._voiceover_enabled)

    def test_matrix_vector_product_identity(self):
        test_matrix_vector_identity_names_the_product_not_the_matrix()

    def test_matrix_recipe_correction_replaces_wrong_text_without_crossfade(self):
        """Execute the authored transition calls; old/new text must never coexist."""
        statements = construct_statements('lire_et_appliquer_une_matrice')
        block = next(node for node in statements if isinstance(node, ast.With)
                     and any(isinstance(part, ast.Call)
                             and isinstance(part.func, ast.Attribute)
                             and part.func.attr == 'wait_until_bookmark'
                             and part.args and isinstance(part.args[0], ast.Constant)
                             and part.args[0].value == 'correct'
                             for part in ast.walk(node)))
        bookmark = next(i for i, node in enumerate(block.body)
                        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute)
                        and node.value.func.attr == 'wait_until_bookmark'
                        and node.value.args[0].value == 'correct')
        objects = {'diagonal_boxes', 'wrong_formula', 'cross_1', 'cross_2',
                   'all_rows', 'correct_words', 'correct_box'}
        visible = {'diagonal_boxes', 'wrong_formula', 'cross_1', 'cross_2'}
        durations = []

        def play(*animations, run_time):
            appearing = {name for kind, names in animations if kind != 'out' for name in names}
            # At any interior frame of a simultaneous fade, outgoing ink remains.
            self.assertFalse('correct_words' in appearing and
                             visible.intersection({'wrong_formula', 'cross_1', 'cross_2'}))
            for kind, names in animations:
                if kind == 'out':
                    visible.difference_update(names)
                else:
                    visible.update(names)
            durations.append(run_time)

        namespace = {name: name for name in objects}
        namespace.update(self=SimpleNamespace(play=play),
                         FadeOut=lambda *names: ('out', names),
                         FadeIn=lambda *names: ('in', names),
                         Create=lambda *names: ('create', names))
        exec(compile(ast.Module(body=block.body[bookmark + 1:], type_ignores=[]),
                     '<actual-matrix-correction-transition>', 'exec'), namespace)
        self.assertEqual(visible, {'all_rows', 'correct_words', 'correct_box'})
        self.assertAlmostEqual(sum(durations), 0.8)

    def test_inverse_log_graph_uses_mutually_reflected_visible_segments(self):
        method = scene_method('exponentielles_et_logarithmes', '_scene3_graphique_inverse')
        values = {assignment_name(node): node.value for node in method.body if assignment_name(node)}
        endpoints = {}
        for name in ('exponential', 'logarithm'):
            call = values[name]
            bounds = next(k.value for k in call.keywords if k.arg == 'x_range')
            namespace = {'np': SimpleNamespace(log2=math.log2)}
            xs = eval(compile(ast.Expression(bounds), '<actual-plot-domain>', 'eval'), namespace)
            function = eval(compile(ast.Expression(call.args[0]), '<actual-plot-function>', 'eval'), namespace)
            endpoints[name] = [(x, function(x)) for x in xs]
            self.assertTrue(all(0 <= x <= 5.2 and 0 <= y <= 5.2 for x, y in endpoints[name]))
        for (x, y), (u, v) in zip(endpoints['exponential'], endpoints['logarithm']):
            self.assertAlmostEqual(x, v)
            self.assertAlmostEqual(y, u)

    def test_logarithm_hypotheses_are_visible_in_both_proofs(self):
        for method, required in (
            ('_scene3_produit', ('a>0', r'a\ne1', 'b>0', 'c>0')),
            ('_scene4_changement_base', ('a,b>0', r'a,b\ne1', 'c>0')),
        ):
            with self.subTest(method=method):
                node = scene_method('exponentielles_et_logarithmes', method)
                condition = next(n.value for n in node.body if assignment_name(n) == 'hypotheses')
                text = ast.literal_eval(condition.args[0])
                self.assertTrue(all(part in text for part in required))
                self.assertTrue(any(isinstance(n, ast.Call) and getattr(n.func, 'id', '') == 'Write'
                                    and any(isinstance(a, ast.Name) and a.id == 'hypotheses' for a in n.args)
                                    for n in ast.walk(node)))

    def test_bacterial_answer_distinguishes_continuous_and_integer_time(self):
        method = scene_method('exponentielles_et_logarithmes', '_scene5_synthese')
        answer = next(n.value for n in method.body if assignment_name(n) == 'answer_tex')
        # Unwrap the placement call to read the expression actually displayed.
        answer = answer.func.value
        text = ast.literal_eval(answer.args[0])
        self.assertIn(r't_{\mathrm{continu}}', text)
        self.assertIn(r't_{\mathrm{entier}}=20', text)
        self.assertEqual(math.ceil(math.log2(1_000_000)), 20)
        self.assertLess(2**19, 1_000_000)
        self.assertGreaterEqual(2**20, 1_000_000)

    def test_vector_distance_plane_preserves_equal_geometric_unit_scale(self):
        method = scene_method('vecteurs_dans_r2_et_r3', '_show_r2')
        plane = next(n for n in ast.walk(method)
                     if isinstance(n, ast.Call) and getattr(n.func, 'id', '') == 'NumberPlane')
        values = {k.arg: ast.literal_eval(k.value) for k in plane.keywords
                  if k.arg in ('x_range', 'y_range', 'x_length', 'y_length')}
        x_unit = values['x_length'] / (values['x_range'][1] - values['x_range'][0])
        y_unit = values['y_length'] / (values['y_range'][1] - values['y_range'][0])
        self.assertAlmostEqual(x_unit, y_unit)
        # The depicted (4,3) displacement must have the five-unit norm taught.
        self.assertAlmostEqual(math.hypot(4*x_unit, 3*y_unit) / x_unit, 5)

    def test_vector_intro_route_preserves_its_labelled_unit_scale(self):
        method = scene_method('vecteurs_dans_r2_et_r3', '_show_intro')
        values = {assignment_name(node): node.value for node in method.body if assignment_name(node)}
        horizontal = ast.literal_eval(values['corner'].right.right)
        vertical = ast.literal_eval(values['b'].right.right)
        labels = [ast.literal_eval(node.args[0]) for node in ast.walk(values['route_labels'])
                  if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'MathTex']
        horizontal_label, vertical_label = map(float, labels)
        scale = horizontal / horizontal_label
        self.assertAlmostEqual(scale, vertical / vertical_label)
        self.assertAlmostEqual(math.hypot(horizontal, vertical) / scale, 5)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_geometry_ignores_and_restores_unrelated_font_defaults(self):
        import manim

        statements = scene_method('permutation_arrangement_combinaison', 'arrangement_segment').body
        start = next(i for i, node in enumerate(statements) if assignment_name(node) == 'slots')
        end = next(i for i, node in enumerate(statements) if assignment_name(node) == 'specific') + 1
        def dimensions():
            values = build_geometry('permutation_arrangement_combinaison', statements[start:end],
                                    methods=('_slot', '_formula_card'))
            return [(values[name].width, values[name].height) for name in ('slots', 'choice_notes', 'specific')]
        baseline = dimensions()
        original = manim.Text.__dict__['__init__']
        try:
            manim.Text.set_default(font='Arial', font_size=99, line_spacing=2)
            unrelated = manim.Text.__dict__['__init__']
            self.assertEqual(dimensions(), baseline)
            self.assertIs(manim.Text.__dict__['__init__'], unrelated)
        finally:
            manim.Text.__init__ = original

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_arrangement_formula_panel_clears_choice_labels(self):
        statements = scene_method('permutation_arrangement_combinaison', 'arrangement_segment').body
        start = next(i for i, node in enumerate(statements) if assignment_name(node) == 'slots')
        end = next(i for i, node in enumerate(statements) if assignment_name(node) == 'specific') + 1
        values = build_geometry('permutation_arrangement_combinaison', statements[start:end],
                                methods=('_slot', '_formula_card'))
        self.assertGreater(values['choice_notes'].get_bottom()[1] - values['specific'].get_top()[1], 0.1)
        self.assertGreater(values['specific'].get_bottom()[1], -values['config'].frame_height / 2 + 0.5)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_repetition_proof_line_clears_general_formula_panel(self):
        statements = construct_statements('repetitions_en_denombrement')
        start = next(i for i, node in enumerate(statements) if isinstance(node, ast.Assign)
                     and isinstance(node.targets[0], ast.Attribute) and node.targets[0].attr == 'title')
        header_end = next(i for i, node in enumerate(statements) if assignment_name(node) == 'header_line') + 2
        formula_start = next(i for i, node in enumerate(statements) if assignment_name(node) == 'banana_calculation')
        formula_end = next(i for i in range(formula_start, len(statements)) if isinstance(statements[i], ast.With))
        values = build_geometry('repetitions_en_denombrement', statements[start:header_end] + statements[formula_start:formula_end],
                                methods=('new_subtitle', 'fit_width', 'make_panel'))
        self.assertGreater(values['proof_line'].get_bottom()[1] - values['general_formula'].get_top()[1], 0.1)
        self.assertGreater(values['calculation_labels'].get_bottom()[1] - values['proof_line'].get_top()[1], 0.1)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_vector_start_coordinate_clears_component_label_and_translated_arrow(self):
        names = {'axes', 'a_xy', 'b_xy', 'a_dot', 'a_label', 'c_xy', 'd_xy', 'vector_cd',
                 'corner', 'horizontal', 'dx_on_graph', 'vector_ba', 'label_ba'}
        values = build_geometry('vecteurs_deplacement_et_composantes',
                                geometry_selection(construct_statements('vecteurs_deplacement_et_composantes'), names))
        label = values['a_label']
        self.assertGreater(values['dx_on_graph'].get_left()[0] - label.get_right()[0], 0.1)
        self.assertGreater(values['vector_cd'].get_left()[0] - label.get_right()[0], 0.1)
        self.assertGreater(label.get_left()[0], -values['config'].frame_width / 2 + 0.5)
        reverse_label = values['label_ba']
        origin = values['axes'].c2p(0, 0)
        self.assertGreater(origin[1] - reverse_label.get_top()[1], 0.1)
        self.assertGreater(reverse_label.get_bottom()[1] - values['horizontal'].get_center()[1], 0.1)
        self.assertGreater(origin[0] - reverse_label.get_right()[0], 0.1)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_vector_label_backings_mask_lines_without_covering_endpoints(self):
        statements = construct_statements('operations_sur_les_vecteurs')
        plane_node = None
        checked = 0
        for node in statements:
            if assignment_name(node) == 'plane':
                plane_node = node
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
                continue
            call = node.value
            if getattr(call.func, 'attr', '') != 'vector_label':
                continue
            values = build_geometry('operations_sur_les_vecteurs', [plane_node, node],
                                    methods=('make_plane', 'vector_label'))
            label = values[assignment_name(node)]
            backing = label.background_rectangle
            glyphs = values['VGroup'](*[part for part in label if part is not backing])
            # BackgroundRectangle.get_fill_color recurses in Manim0.19;
            # inspect the RGBA data actually consumed by the renderer.
            self.assertTrue(values['np'].allclose(backing.get_fill_rgbas(), [1, 1, 1, 1]))
            self.assertGreaterEqual(label.z_index, 5)
            self.assertGreater(backing.width - glyphs.width, 0.1)
            self.assertGreater(backing.height - glyphs.height, 0.1)
            for endpoint in call.args[1:3]:
                point = values['plane'].c2p(*ast.literal_eval(endpoint))
                self.assertFalse(backing.get_left()[0] - 0.05 <= point[0] <= backing.get_right()[0] + 0.05
                                 and backing.get_bottom()[1] - 0.05 <= point[1] <= backing.get_top()[1] + 0.05,
                                 f'{assignment_name(node)} covers endpoint {ast.literal_eval(endpoint)}')
            checked += 1
        self.assertEqual(checked, 8)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_r2_coordinates_clear_component_label_and_axes(self):
        names = {'plane', 'a_xy', 'b_xy', 'm_xy', 'a', 'b', 'corner', 'midpoint', 'dot_a',
                 'label_a', 'component_x', 'component_y', 'component_labels', 'dot_m', 'label_m',
                 'direct', 'direct_label'}
        method = scene_method('vecteurs_dans_r2_et_r3', '_show_r2')
        values = build_geometry('vecteurs_dans_r2_et_r3', geometry_selection(method.body, names))
        self.assertGreater(values['component_labels'][0].get_left()[0] - values['label_a'].get_right()[0], 0.1)
        self.assertGreater(values['label_m'].get_bottom()[1] - values['plane'].c2p(0, 0)[1], 0.1)
        self.assertGreater(values['plane'].c2p(0, 0)[0] - values['label_m'].get_right()[0], 0.1)
        axis_x = values['plane'].c2p(0, 0)[0]
        for label in (values['component_labels'][0], values['direct_label']):
            self.assertGreater(axis_x - label.get_right()[0], 0.1)
        backing = values['direct_label'].background_rectangle
        self.assertTrue(values['np'].allclose(backing.get_fill_rgbas(), [1, 1, 1, 1]))
        self.assertGreaterEqual(values['direct_label'].z_index, 5)
        midpoint_label = values['label_m']
        midpoint_backing = midpoint_label.background_rectangle
        self.assertTrue(values['np'].allclose(midpoint_backing.get_fill_rgbas(), [1, 1, 1, 1]))
        self.assertGreaterEqual(midpoint_label.z_index, 5)
        glyphs = values['VGroup'](*[part for part in midpoint_label if part is not midpoint_backing])
        self.assertGreater(midpoint_backing.width - glyphs.width, 0.079)
        self.assertGreater(midpoint_backing.height - glyphs.height, 0.079)
        self.assertGreater(values['dot_m'].get_left()[0] - midpoint_backing.get_right()[0], 0.05)
        self.assertGreater(midpoint_backing.get_bottom()[1] - values['dot_m'].get_top()[1], 0.05)
        for axis in (values['plane'].x_axis, values['plane'].y_axis):
            self.assertGreater(len(axis.numbers), 0)
            for number in axis.numbers:
                self.assertEqual(number.num_decimal_places, 0)
                for glyph in number.family_members_with_points():
                    self.assertEqual(glyph.get_fill_color().to_hex(), '#000000')
                    self.assertEqual(float(glyph.get_fill_opacity()), 1.0)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_r3_midpoint_label_clears_axes_vector_and_endpoint(self):
        method = scene_method('vecteurs_dans_r2_et_r3', '_show_r3')
        names = {'origin', 'x_end', 'y_end', 'z_end', 'x_axis', 'y_axis', 'z_axis',
                 'a_xyz', 'b_xyz', 'm_xyz', 'a', 'b', 'midpoint', 'direct', 'dot_m', 'label_m',
                 'step_x_end', 'step_y_end', 'step_x', 'step_y', 'step_z', 'direct_label'}
        values = build_geometry('vecteurs_dans_r2_et_r3', geometry_selection(method.body, names),
                                methods=('_project_3d',))
        label = values['label_m']
        self.assertGreater(label.get_left()[0] - values['dot_m'].get_right()[0], 0.15)
        for name in ('x_axis', 'y_axis', 'z_axis', 'direct'):
            line = values[name]
            points = values['np'].linspace(line.get_start(), line.get_end(), 301)
            near = ((points[:, 0] > label.get_left()[0] - 0.1)
                    & (points[:, 0] < label.get_right()[0] + 0.1)
                    & (points[:, 1] > label.get_bottom()[1] - 0.1)
                    & (points[:, 1] < label.get_top()[1] + 0.1))
            self.assertFalse(near.any(), f'{name} intersects midpoint annotation margin')
        self.assertLess(label.get_right()[0], 0.65 - 0.1)
        self.assertGreater(label.get_bottom()[1], -values['config'].frame_height / 2 + 0.3)
        direct_label = values['direct_label']
        for name in ('direct', 'step_x', 'step_y', 'step_z', 'x_axis', 'y_axis', 'z_axis'):
            line = values[name]
            # Include actual arrow-tip/stroke points as well as the full shaft;
            # a global box includes wide arrowheads far above this label.
            points = values['np'].vstack((line.get_all_points(),
                                          values['np'].linspace(line.get_start(), line.get_end(), 301)))
            near = ((points[:, 0] > direct_label.get_left()[0] - 0.1)
                    & (points[:, 0] < direct_label.get_right()[0] + 0.1)
                    & (points[:, 1] > direct_label.get_bottom()[1] - 0.1)
                    & (points[:, 1] < direct_label.get_top()[1] + 0.1))
            self.assertFalse(near.any(), f'{name} intersects displacement annotation margin')

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_determinant_label_fades_keep_masks_opaque_before_grid_motion(self):
        """Exercise real fades and Scene ownership without rendering any frames."""
        statements = construct_statements('determinant_et_matrice_inverse')
        basis = next(node for node in statements if isinstance(node, ast.Assign)
                     and isinstance(node.targets[0], ast.Tuple)
                     and [x.id for x in node.targets[0].elts] == ['e1', 'e2'])
        names = {'e1_label', 'e2_label', 'p_point', 'q_point', 'p_dot', 'q_dot',
                 'p_label', 'q_label'}
        selected = geometry_selection(statements, names) + [basis]
        selected.sort(key=lambda node: node.lineno)
        values = build_geometry('determinant_et_matrice_inverse', selected,
                                methods=('make_basis_vectors',))

        for bookmark, label_names, expected_duration in (
            ('apply_a', ('e1_label', 'e2_label'), 2.0),
            ('collapse', ('p_label', 'q_label'), 1.75),
        ):
            with self.subTest(transition=bookmark):
                block = next(node for node in statements if isinstance(node, ast.With)
                             and any(isinstance(part, ast.Call)
                                     and isinstance(part.func, ast.Attribute)
                                     and part.func.attr == 'wait_until_bookmark'
                                     and part.args and isinstance(part.args[0], ast.Constant)
                                     and part.args[0].value == bookmark
                                     for part in ast.walk(node)))
                start = next(i for i, node in enumerate(block.body)
                             if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                             and isinstance(node.value.func, ast.Attribute)
                             and node.value.func.attr == 'wait_until_bookmark'
                             and node.value.args[0].value == bookmark) + 1
                end = next(i for i in range(start, len(block.body))
                           if any(isinstance(part, ast.Call)
                                  and isinstance(part.func, ast.Name)
                                  and part.func.id == 'Transform'
                                  and part.args and isinstance(part.args[0], ast.Name)
                                  and part.args[0].id == 'grid'
                                  for part in ast.walk(block.body[i]))) + 1
                labels = [values[name] for name in label_names]
                entry_start = next(i for i, node in enumerate(block.body)
                                   if isinstance(node, ast.Expr)
                                   and isinstance(node.value, ast.Call)
                                   and isinstance(node.value.func, ast.Attribute)
                                   and node.value.func.attr == 'add'
                                   and any(isinstance(part, ast.Name) and part.id in label_names
                                           for part in ast.walk(node)))
                entry_end = next(i for i in range(entry_start + 1, len(block.body))
                                 if isinstance(block.body[i], ast.Expr)
                                 and isinstance(block.body[i].value, ast.Call)
                                 and isinstance(block.body[i].value.func, ast.Attribute)
                                 and block.body[i].value.func.attr == 'add') + 1
                with tempfile.TemporaryDirectory(prefix='course-review-b-scene-') as temp:
                    with values['tempconfig']({'media_dir': temp}):
                        scene = values['Scene']()
                durations = []
                faded_glyphs = set()

                def play(*animations, run_time):
                    durations.append(run_time)
                    fades = [animation for animation in animations
                             if not isinstance(animation, tuple)]
                    if fades:
                        # Real Scene.play adds a new glyph-only VGroup before
                        # beginning its fade. This dissolves its label parent
                        # and leaves the background as a standalone mobject.
                        scene.compile_animation_data(*fades, run_time=run_time)
                        scene.begin_animations()
                    for animation in animations:
                        if isinstance(animation, tuple):
                            if animation[0] == 'motion':
                                attached = scene.get_mobject_family_members()
                                for label in labels:
                                    self.assertFalse(set(label.get_family()).intersection(attached),
                                                     'Grid moves while label ink/masks remain attached')
                            continue
                        self.assertIsInstance(animation, (values['FadeIn'], values['FadeOut']))
                        for alpha in (0, 0.1, 0.5, 0.9, 1):
                            animation.interpolate(alpha)
                            for label in labels:
                                self.assertIn(label.background_rectangle,
                                              scene.get_mobject_family_members())
                                self.assertTrue(values['np'].allclose(
                                    label.background_rectangle.get_fill_rgbas(), [1, 1, 1, 1]))
                        animation.finish()
                        if isinstance(animation, values['FadeOut']):
                            glyphs = animation.mobject.family_members_with_points()
                            self.assertTrue(all(part.get_fill_opacity() == 0 for part in glyphs))
                            faded_glyphs.update(glyphs)
                        animation.clean_up_from_scene(scene)

                def remove(*objects):
                    for label in labels:
                        glyphs = [part for child in label[1:]
                                  for part in child.family_members_with_points()]
                        self.assertTrue(glyphs)
                        # FadeOut cleanup restores child opacity without drawing
                        # another frame. The next authored statement removes
                        # the parent and detached mask before any further play.
                        self.assertTrue(set(glyphs).issubset(faded_glyphs),
                                        'Backing removed before its glyphs finish fading')
                    scene.remove(*objects)

                namespace = dict(values, self=SimpleNamespace(play=play, remove=remove, add=scene.add),
                                 GrowArrow=lambda *objects: ('entry-arrow', objects),
                                 Transform=lambda *objects: ('motion', objects),
                                 ReplacementTransform=lambda *objects: ('motion', objects))
                for name in ('grid', 'grid_target', 'square', 'square_target',
                             'collapsed_square', 'e1_target', 'e2_target'):
                    namespace[name] = object()
                exec(compile(ast.Module(body=block.body[entry_start:entry_end], type_ignores=[]),
                             '<actual-determinant-label-entry>', 'exec'), namespace)
                self.assertEqual(durations, [0.8])
                for label in labels:
                    self.assertIn(label, scene.mobjects, 'Complete label must be regrouped after entry')
                    for child in label[1:]:
                        self.assertTrue(all(part.get_fill_opacity() == 1
                                            for part in child.family_members_with_points()))
                durations.clear()
                exec(compile(ast.Module(body=block.body[start:end], type_ignores=[]),
                             '<actual-determinant-transition>', 'exec'), namespace)
                for label in labels:
                    self.assertFalse(set(label.get_family()).intersection(scene.get_mobject_family_members()))
                self.assertAlmostEqual(sum(durations), expected_duration)

                # Rebuild the real Cairo moving/static inventories for later
                # content, then execute the scene's authored page cleanup.
                # A detached white mask must not survive in either inventory.
                probe = values['Line'](values['LEFT'], values['RIGHT'])
                scene.add(probe)

                def play_without_render(*animations, run_time):
                    scene.compile_animation_data(*animations, run_time=run_time)
                    scene.begin_animations()
                    inventory = (scene.get_mobject_family_members()
                                 + scene.static_mobjects + scene.moving_mobjects)
                    attached = {part for mob in inventory for part in mob.get_family()}
                    for label in labels:
                        self.assertNotIn(label.background_rectangle, attached,
                                         'Old mask survives into a later page')
                    scene.update_to_time(run_time)
                    for animation in scene.animations:
                        animation.finish()
                        animation.clean_up_from_scene(scene)

                play_without_render(values['Transform'](probe, probe.copy().shift(values['UP'])),
                                    run_time=0.1)
                clear_namespace = dict(values)
                exec(compile(ast.Module(body=[scene_method('determinant_et_matrice_inverse',
                                                          'clear_page')], type_ignores=[]),
                             '<actual-determinant-page-cleanup>', 'exec'), clear_namespace)
                clear_namespace['clear_page'](SimpleNamespace(play=play_without_render),
                                              *scene.mobjects)
                self.assertFalse(scene.get_mobject_family_members(),
                                 'Page cleanup leaves orphan scene objects')

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_determinant_basis_and_height_annotations_clear_geometry(self):
        statements = construct_statements('determinant_et_matrice_inverse')
        end = next(i for i, node in enumerate(statements) if assignment_name(node) == 'height_label') + 1
        basis = next(node for node in statements[:end] if isinstance(node, ast.Assign)
                     and isinstance(node.targets[0], ast.Tuple)
                     and [x.id for x in node.targets[0].elts] == ['e1', 'e2'])
        names = {'grid', 'grid_target', 'square', 'square_target', 'e1_label', 'e2_label',
                 'height_line', 'height_brace', 'height_label'}
        selected = geometry_selection(statements[:end], names) + [basis]
        selected.sort(key=lambda node: node.lineno)
        values = build_geometry('determinant_et_matrice_inverse', selected,
                                methods=('make_grid', 'make_unit_square', 'make_basis_vectors', 'linear_target'))
        for name in ('e1', 'e2'):
            label = values[name + '_label']
            backing = label.background_rectangle
            self.assertTrue(values['np'].allclose(backing.get_fill_rgbas(), [1, 1, 1, 1]))
            self.assertGreaterEqual(label.z_index, 5)
            glyphs = values['VGroup'](*[part for part in label if part is not backing])
            self.assertGreater(backing.width - glyphs.width, 0.099)
            self.assertGreater(backing.height - glyphs.height, 0.099)
            endpoint = values[name].get_end()
            self.assertFalse(backing.get_left()[0] - 0.05 <= endpoint[0] <= backing.get_right()[0] + 0.05
                             and backing.get_bottom()[1] - 0.05 <= endpoint[1] <= backing.get_top()[1] + 0.05)
        label = values['height_label']
        vertices = values['square_target'].get_vertices()
        lines = [(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]
        lines += [(line.get_start(), line.get_end()) for line in values['grid_target']]
        for start, finish in lines:
            points = values['np'].linspace(start, finish, 301)
            intersects = ((points[:, 0] > label.get_left()[0] - 0.1)
                          & (points[:, 0] < label.get_right()[0] + 0.1)
                          & (points[:, 1] > label.get_bottom()[1] - 0.1)
                          & (points[:, 1] < label.get_top()[1] + 0.1))
            self.assertFalse(intersects.any(), 'Transformed edge/grid crosses height numeral margin')
        self.assertGreater(label.get_left()[0] - values['height_brace'].get_right()[0], 0.1)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_determinants_clear_grid_and_right_frame_edge(self):
        statements = construct_statements('determinant_et_matrice_inverse')
        end = next(i for i, node in enumerate(statements) if assignment_name(node) == 'negative_det') + 1
        names = {'grid', 'grid_target', 'column_images', 'determinant_a', 'reversed_label', 'absolute_det', 'negative_det'}
        values = build_geometry('determinant_et_matrice_inverse', geometry_selection(statements[:end], names),
                                methods=('make_grid', 'linear_target'))
        self.assertGreater(values['determinant_a'].get_left()[0] - values['grid_target'].get_right()[0], 0.1)
        for name in ('determinant_a', 'absolute_det', 'negative_det'):
            label = values[name]
            self.assertLess(label.get_right()[0], values['config'].frame_width / 2 - 0.4)
            self.assertGreater(label.get_bottom()[1], -values['config'].frame_height / 2 + 0.3)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_singular_matrix_point_labels_mask_grid_without_covering_dots(self):
        statements = construct_statements('determinant_et_matrice_inverse')
        names = {'p_point', 'q_point', 'p_dot', 'q_dot', 'p_label', 'q_label'}
        values = build_geometry('determinant_et_matrice_inverse', geometry_selection(statements, names))
        for name in ('p', 'q'):
            label = values[name + '_label']
            backing = label.background_rectangle
            glyphs = values['VGroup'](*[part for part in label if part is not backing])
            self.assertTrue(values['np'].allclose(backing.get_fill_rgbas(), [1, 1, 1, 1]))
            self.assertGreaterEqual(label.z_index, 5)
            self.assertGreater(backing.width - glyphs.width, 0.099)
            self.assertGreater(backing.height - glyphs.height, 0.099)
            for dot_name in ('p_dot', 'q_dot'):
                dot = values[dot_name]
                self.assertTrue(backing.get_left()[0] - dot.get_right()[0] > 0.05
                                or dot.get_left()[0] - backing.get_right()[0] > 0.05)
            self.assertGreater(label.get_left()[0], -values['config'].frame_width / 2 + 0.3)
            self.assertLess(label.get_right()[0], values['config'].frame_width / 2 - 0.3)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_inverse_mirror_label_clears_diagonal_curves_and_other_labels(self):
        method = scene_method('exponentielles_et_logarithmes', '_scene3_graphique_inverse')
        names = {'title', 'axes', 'axis_labels', 'diagonal', 'diagonal_label',
                 'exponential', 'exponential_label', 'logarithm', 'logarithm_label', 'reflection_note'}
        values = build_geometry('exponentielles_et_logarithmes', geometry_selection(method.body, names))
        axes, label, np = values['axes'], values['diagonal_label'], values['np']
        origin = axes.c2p(0, 0)
        x_unit, y_unit = axes.c2p(1, 0) - origin, axes.c2p(0, 1) - origin
        self.assertAlmostEqual(np.linalg.norm(x_unit), np.linalg.norm(y_unit))
        direction = axes.c2p(1, 1) - origin
        normal = np.array([direction[1], -direction[0], 0.0])
        normal /= np.linalg.norm(normal)
        # Check the full mirror line, including spaces between its dashes.
        for corner in ('UL', 'UR', 'DL', 'DR'):
            with self.subTest(corner=corner):
                self.assertGreater(float((label.get_corner(values[corner]) - origin) @ normal), 0.15)
        for name in ('exponential', 'logarithm', 'axes'):
            points = values[name].get_all_points()
            near_label = ((points[:, 0] > label.get_left()[0] - 0.1)
                          & (points[:, 0] < label.get_right()[0] + 0.1)
                          & (points[:, 1] > label.get_bottom()[1] - 0.1)
                          & (points[:, 1] < label.get_top()[1] + 0.1))
            with self.subTest(path=name):
                self.assertFalse(near_label.any())
        others = [(name, values[name]) for name in
                  ('title', 'exponential_label', 'logarithm_label', 'reflection_note')]
        others.extend((f'axis_label_{i}', item) for i, item in enumerate(values['axis_labels']))
        for name, other in others:
            with self.subTest(label=name):
                self.assertTrue(label.get_left()[0] - other.get_right()[0] > 0.15
                                or other.get_left()[0] - label.get_right()[0] > 0.15
                                or label.get_bottom()[1] - other.get_top()[1] > 0.15
                                or other.get_bottom()[1] - label.get_top()[1] > 0.15)
        self.assertGreater(label.get_left()[0], -values['config'].frame_width / 2 + 0.3)
        self.assertLess(label.get_right()[0], values['config'].frame_width / 2 - 0.3)
        self.assertGreater(label.get_bottom()[1], -values['config'].frame_height / 2 + 0.3)
        self.assertLess(label.get_top()[1], values['config'].frame_height / 2 - 0.3)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual geometry')
    def test_injectivity_panel_clears_title_curve_axes_and_note(self):
        method = scene_method('exponentielles_et_logarithmes', '_scene2_injectivite')
        names = {'title', 'axes', 'curve', 'curve_label', 'principle_box', 'principle_tex', 'note'}
        values = build_geometry('exponentielles_et_logarithmes', geometry_selection(method.body, names))
        panel = values['principle_box']
        self.assertGreater(values['title'].get_bottom()[1] - panel.get_top()[1], 0.1)
        self.assertGreater(panel.get_bottom()[1] - values['note'].get_top()[1], 0.1)
        self.assertGreater(values['axes'].x_axis.get_bottom()[1] - values['note'].get_top()[1], 0.15)
        self.assertGreater(values['note'].get_bottom()[1] + values['config'].frame_height / 2, 0.15)
        self.assertGreater(panel.get_bottom()[1] - values['axes'].c2p(0, 0)[1], 0.1)
        self.assertGreater(panel.get_left()[0] - values['axes'].c2p(0, 0)[0], 0.1)
        self.assertGreater(values['curve_label'].get_bottom()[1] - panel.get_top()[1], 0.1)
        dynamic_nodes = [node for node in ast.walk(method)
                         if assignment_name(node) in {'y_tracker', 'h_line_dynamic', 'intersect_dot'}
                         or isinstance(node, ast.FunctionDef) and node.name == 'get_intersect_dot']
        dynamic_nodes.sort(key=lambda node: node.lineno)
        exec(compile(ast.Module(body=dynamic_nodes, type_ignores=[]), '<actual-horizontal-sweep>', 'exec'), values)
        for y in (0.5, 0.75, 1, 2, 4, 8):
            values['y_tracker'].set_value(y)
            for name in ('h_line_dynamic', 'intersect_dot'):
                values[name].update()
                if len(values[name].get_all_points()):
                    self.assertGreater(values['curve_label'].get_left()[0] - values[name].get_right()[0], 0.15)
        self.assertLess(values['curve_label'].get_right()[0], values['config'].frame_width / 2 - 0.3)
        # The exponential rises to the right, so compare only the curve portion
        # sharing this lower panel's vertical band, not its global bounding box.
        points = values['curve'].get_all_points()
        same_band = points[(points[:, 1] >= panel.get_bottom()[1] - 0.1)
                           & (points[:, 1] <= panel.get_top()[1] + 0.1)]
        self.assertGreater(len(same_band), 0)
        self.assertGreater(panel.get_left()[0] - max(same_band[:, 0]), 0.1)

    @unittest.skipUnless(importlib.util.find_spec('manim'), 'Manim required for actual label bounding boxes')
    def test_matrix_vector_endpoint_labels_have_disjoint_bounding_boxes(self):
        import manim

        statements = construct_statements('operations_sur_les_matrices')
        entry = resolve('operations_sur_les_matrices', load_catalog()[1])
        tree = ast.parse((ROOT / entry['scene_file']).read_text())
        start = next(i for i, node in enumerate(statements) if assignment_name(node) == 'p_visual') - 1
        geometry = statements[start:start + 5]
        self.assertEqual([assignment_name(node) for node in geometry],
                         ['plane', 'p_visual', 'ap_visual', 'p_label', 'ap_label'])
        composition_start = next(i for i, node in enumerate(statements) if assignment_name(node) == 'bap') - 3
        composition = statements[composition_start:composition_start + 11]
        self.assertEqual([assignment_name(node) for node in composition],
                         ['plane', 'p', 'ap', 'bap', 'p_label', 'ap_label', 'bap_label',
                          'path_a', 'path_b', 'label_path_a', 'label_path_b'])
        methods = [scene_method('operations_sur_les_matrices', method)
                   for method in ('make_plane', 'point_vector')]
        namespace = dict(vars(manim), ACCENT=manim.BLACK, RESULT=manim.BLACK, PALE=manim.GRAY)
        # Compile the real geometry helpers and label placements, without a Scene or renderer.
        for method in methods:
            exec(compile(ast.Module(body=[method], type_ignores=[]), '<actual-geometry-helper>', 'exec'), namespace)
        helper = SimpleNamespace()
        for method in methods:
            setattr(helper, method.name, namespace[method.name].__get__(helper))
        namespace['self'] = helper
        with tempfile.TemporaryDirectory(prefix='course-review-b-') as temp, scene_text_defaults(tree, namespace):
            with manim.tempconfig({'media_dir': temp, 'tex_dir': str(Path(temp) / 'Tex')}):
                for page, nodes in (('matrix_vector', geometry), ('composition', composition)):
                    with self.subTest(page=page):
                        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual-vector-labels>', 'exec'), namespace)
                        left, right = namespace['p_label'], namespace['ap_label']
                        # A merely positive subpixel gap still reads as touching in a 480p preview.
                        self.assertGreater(right.get_left()[0] - left.get_right()[0], 0.1)
                        dots = (namespace['p_visual'][1], namespace['ap_visual'][1]) if page == 'matrix_vector' else (namespace['p'], namespace['ap'])
                        labels_and_dots = list(zip((left, right), dots))
                        if page == 'composition':
                            labels_and_dots.append((namespace['bap_label'], namespace['bap']))
                            for label_name, path_name in (('label_path_a', 'path_a'), ('label_path_b', 'path_b')):
                                label, path = namespace[label_name], namespace[path_name]
                                backing = label.background_rectangle
                                if path_name == 'path_a':
                                    self.assertGreater(backing.get_bottom()[1] - path.get_top()[1], 0.02)
                                else:
                                    self.assertGreater(backing.get_left()[0] - path.get_right()[0], 0.02)
                                labels_and_dots.extend((label, namespace[dot]) for dot in ('p', 'ap', 'bap'))
                        for label, dot in labels_and_dots:
                            backing = label.background_rectangle
                            self.assertTrue(manim.np.allclose(backing.get_fill_rgbas(), [1, 1, 1, 1]))
                            self.assertGreaterEqual(label.z_index, 5)
                            glyphs = manim.VGroup(*[part for part in label if part is not backing])
                            self.assertGreater(backing.width - glyphs.width, 0.099)
                            self.assertGreater(backing.height - glyphs.height, 0.099)
                            self.assertTrue(backing.get_left()[0] - dot.get_right()[0] > 0.02
                                            or dot.get_left()[0] - backing.get_right()[0] > 0.02
                                            or backing.get_bottom()[1] - dot.get_top()[1] > 0.02
                                            or dot.get_bottom()[1] - backing.get_top()[1] > 0.02)
                            self.assertGreater(label.get_left()[0], -manim.config.frame_width / 2)
                            self.assertLess(label.get_right()[0], manim.config.frame_width / 2)
                        for label, dot in zip((left, right), dots):
                            if page == 'matrix_vector':
                                self.assertGreater(label.get_bottom()[1], dot.get_top()[1])
                            else:
                                self.assertLess(label.get_top()[1], dot.get_bottom()[1])


def test_matrix_vector_identity_names_the_product_not_the_matrix():
    """The displayed left side must have the 2x1 shape of the actual product."""
    statements = construct_statements('operations_sur_les_matrices')
    product_index = next(i for i, node in enumerate(statements)
                         if assignment_name(node) == 'formula_group')
    preceding = {assignment_name(node): node.value for node in statements[:product_index]
                 if assignment_name(node)}
    matrix = ast.literal_eval(preceding['matrix_a'].args[0])
    vector = ast.literal_eval(preceding['vector_p'].args[0])
    assert len(matrix[0]) == len(vector)
    product = [[sum(a * b[0] for a, b in zip(row, vector))] for row in matrix]
    assert product == [[3], [2]]
    prefix = ast.literal_eval(statements[product_index].value.args[0].args[0])
    # A has two columns; Ap is a column vector, matching the displayed result.
    assert len(matrix[0]) != len(product[0])
    assert prefix == 'Ap='

"""Source-linked behavior, mathematics and geometry checks for Worker A lessons.

Narration checks extract real setup methods without importing scenes, loading a
local .env, or contacting Azure. Geometry checks use local Manim when available.
"""
import ast
import copy
import math
import os
import re
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tools.course_catalog import load_catalog, resolve

ROOT = Path(__file__).resolve().parents[1]
LESSON_IDS = {
    "variables_et_polynomes", "inequations_et_nombres_negatifs",
    "racine_carree_et_valeur_absolue", "domaine_et_image_d_une_fonction",
    "modeles_affines_et_quadratiques", "lire_les_proprietes_d_un_graphe",
    "fonction_definie_par_morceaux", "operations_sur_les_fonctions",
    "composition_de_fonctions", "fonction_reciproque",
    "racines_et_hauteur_zero", "multiplicite_des_racines", "completer_le_carre",
}


def setup_method(entry, service):
    path = ROOT / entry["scene_file"]
    tree = ast.parse(path.read_text())
    scene = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                 and n.name == entry["scene_class"])
    method = next(n for n in scene.body if isinstance(n, ast.FunctionDef)
                  and n.name == "_setup_voiceover")
    module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    namespace = {
        "os": os, "__file__": str(path), "load_dotenv": Mock(),
        "VoiceoverScene": object, "AzureService": service,
        "tts": SimpleNamespace(VOICE_ID="existing-shared-profile"),
        "VOICE_ID": "existing-shared-profile",
    }
    exec(compile(module, str(path), "exec"), namespace)
    return namespace["_setup_voiceover"], namespace


class ExplicitNarrationModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, entries = load_catalog()
        cls.entries = [e for e in entries if e["lesson_id"] in LESSON_IDS]
        assert len(cls.entries) == len(LESSON_IDS)

    def test_explicit_silent_never_loads_credentials_or_creates_service(self):
        for entry in self.entries:
            for flag in ("1", "TRUE", "yes"):
                with self.subTest(lesson=entry["lesson_id"], flag=flag):
                    service = Mock(side_effect=AssertionError("unexpected synthesis setup"))
                    setup, namespace = setup_method(entry, service)
                    scene = SimpleNamespace(set_speech_service=Mock())
                    with patch.dict(os.environ, {"MANIM_DISABLE_VOICEOVER": flag,
                                                 "SPEECH_KEY": "test-only",
                                                 "SPEECH_REGION": "test-region"}, clear=True):
                        setup(scene)
                    self.assertFalse(scene._voiceover_enabled)
                    service.assert_not_called()
                    namespace["load_dotenv"].assert_not_called()

    def test_requested_narration_rejects_missing_credentials(self):
        for entry in self.entries:
            for credentials in ({}, {"SPEECH_KEY": "test-only"},
                                {"SPEECH_REGION": "test-region"}):
                with self.subTest(lesson=entry["lesson_id"], credentials=list(credentials)):
                    service = Mock()
                    setup, _ = setup_method(entry, service)
                    scene = SimpleNamespace(set_speech_service=Mock())
                    with patch.dict(os.environ, credentials, clear=True):
                        with self.assertRaisesRegex(RuntimeError, "SPEECH_KEY.*SPEECH_REGION"):
                            setup(scene)
                    self.assertFalse(scene._voiceover_enabled)
                    service.assert_not_called()

    def test_requested_narration_rejects_unavailable_adapter(self):
        for entry in self.entries:
            with self.subTest(lesson=entry["lesson_id"]):
                setup, _ = setup_method(entry, None)
                with patch.dict(os.environ, {}, clear=True):
                    with self.assertRaisesRegex(RuntimeError, "shared Azure adapter"):
                        setup(SimpleNamespace(set_speech_service=Mock()))

    def test_success_preserves_shared_voice_and_credential_aliases(self):
        for entry in self.entries:
            for credentials in ({"SPEECH_KEY": "test-only", "SPEECH_REGION": "test-region"},
                                {"AZURE_SUBSCRIPTION_KEY": "test-only",
                                 "AZURE_SERVICE_REGION": "test-region"}):
                with self.subTest(lesson=entry["lesson_id"], aliases=list(credentials)):
                    service = Mock(return_value=object())
                    setup, _ = setup_method(entry, service)
                    scene = SimpleNamespace(set_speech_service=Mock())
                    with patch.dict(os.environ, credentials, clear=True):
                        setup(scene)
                        self.assertEqual(os.environ["SPEECH_KEY"], "test-only")
                        self.assertEqual(os.environ["AZURE_SUBSCRIPTION_KEY"], "test-only")
                    self.assertTrue(scene._voiceover_enabled)
                    service.assert_called_once_with(voice="existing-shared-profile")
                    scene.set_speech_service.assert_called_once_with(service.return_value)

    def test_setup_failure_is_propagated_instead_of_silent_success(self):
        for entry in self.entries:
            with self.subTest(lesson=entry["lesson_id"]):
                setup, _ = setup_method(entry, Mock(side_effect=RuntimeError("setup failed")))
                scene = SimpleNamespace(set_speech_service=Mock())
                with patch.dict(os.environ, {"SPEECH_KEY": "test-only",
                                             "SPEECH_REGION": "test-region"}, clear=True):
                    with self.assertRaisesRegex(RuntimeError, "setup failed"):
                        setup(scene)
                self.assertFalse(scene._voiceover_enabled)


def lesson_tree(lesson_id):
    entry = resolve(lesson_id, load_catalog()[1])
    return ast.parse((ROOT / entry["scene_file"]).read_text())


def assigned_math(tree, name):
    """Read the formula actually assigned to a named on-screen object."""
    assignment = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == name
                              for target in node.targets))
    call = next(node for node in ast.walk(assignment.value)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "MathTex")
    return "".join(ast.literal_eval(arg) for arg in call.args)


class MathematicalHypothesisTests(unittest.TestCase):
    def test_root_example_plot_stays_in_the_vertical_viewport(self):
        tree = lesson_tree("racines_et_hauteur_zero")
        assignments = {target.id: node for node in ast.walk(tree)
                       if isinstance(node, ast.Assign)
                       for target in node.targets if isinstance(target, ast.Name)}
        axes_call = next(node for node in ast.walk(assignments["axes2"])
                         if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                         and node.func.id == "proportional_axes")
        y_range = ast.literal_eval(next(k.value for k in axes_call.keywords if k.arg == "y_range"))
        ns = {"np": SimpleNamespace(sqrt=math.sqrt), "axes2": SimpleNamespace(y_range=y_range)}
        function = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef) and node.name == "g")
        body = [function]
        if "visible_half_span" in assignments:
            body.append(assignments["visible_half_span"])
        exec(compile(ast.fix_missing_locations(ast.Module(body=body, type_ignores=[])),
                     "<actual curve extent>", "exec"), ns)
        curve_call = assignments["graph2"].value
        bounds = next(k.value for k in curve_call.keywords if k.arg == "x_range")
        left, right = eval(compile(ast.Expression(bounds), "<actual curve bounds>", "eval"), ns)
        for x in (left, right, 0.5, -1, 2):
            self.assertGreaterEqual(ns["g"](x), y_range[0] - 1e-8)
            self.assertLessEqual(ns["g"](x), y_range[1] + 1e-8)
        self.assertLess(left, -1)
        self.assertGreater(right, 2)

    def test_period_definition_excludes_the_vacuous_zero_period(self):
        tree = lesson_tree("lire_les_proprietes_d_un_graphe")
        periodic = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef) and node.name == "_prop_periodic")
        captions = [ast.literal_eval(node.args[0]) for node in ast.walk(periodic)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "_show_caption"]
        condition = re.search(r"T\s*(>=|>)\s*(-?\d+)", " ".join(captions))
        self.assertIsNotNone(condition, "The displayed definition must constrain T.")
        relation, bound = condition.group(1), int(condition.group(2))
        def accepts(period):
            return period > bound if relation == ">" else period >= bound
        self.assertFalse(accepts(0), "T=0 would make every function periodic.")
        self.assertTrue(accepts(2 * math.pi))
        strings = " ".join(node.value for node in ast.walk(tree)
                           if isinstance(node, ast.Constant) and isinstance(node.value, str))
        self.assertIn("strictement positif", strings, "The spoken definition needs the same condition.")

    def test_inverse_warning_does_not_assert_pointwise_inequality(self):
        tree = lesson_tree("fonction_reciproque")
        warning = assigned_math(tree, "warning")
        # Execute the actual plotted f and its inverse at inputs where their
        # inverse-function value coincides with the reciprocal value.
        plots = [node for node in ast.walk(tree)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                 and node.func.attr == "plot" and node.args
                 and isinstance(node.args[0], ast.Lambda)]
        functions = [eval(compile(ast.Expression(node.args[0]), "<scene plot>", "eval"))
                     for node in plots[:2]]
        for x in (Fraction(-1), Fraction(3, 2)):
            self.assertEqual(functions[1](x), 1 / functions[0](x))
        self.assertNotRegex(warning, r"\\ne(?:q)?\b")
        self.assertIn("ne signifie pas", warning)
        self.assertIn(r"f^{-1}", warning)

    def test_quadratic_derivation_retains_real_solution_hypotheses(self):
        tree = lesson_tree("completer_le_carre")
        initial = assigned_math(tree, "eq0")
        final_conditions = assigned_math(tree, "conditions")
        self.assertRegex(initial, r"a\\ne(?:q)?\s*0")
        self.assertRegex(final_conditions, r"a\\ne(?:q)?\s*0")
        self.assertIn(r"b^2-4ac\ge0", final_conditions)
        self.assertIn(r"\mathbb R", final_conditions)
        formulas = ["".join(ast.literal_eval(arg) for arg in node.args)
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "MathTex"
                    and all(isinstance(arg, ast.Constant) for arg in node.args)]
        root_step = next(text for text in formulas
                         if r"x + \tfrac{b}{2a} = \pm" in text)
        self.assertIn(r"\text{si }b^2-4ac\ge0", root_step)
        # Distinct roots with negative leading coefficient and a double root
        # both belong to the displayed real-domain formula.
        for a, b, c in ((-1, 0, 1), (1, 2, 1)):
            discriminant = b * b - 4 * a * c
            self.assertGreaterEqual(discriminant, 0)
            for sign in (-1, 1):
                x = (-b + sign * math.sqrt(discriminant)) / (2 * a)
                self.assertAlmostEqual(a * x * x + b * x + c, 0)
        strings = " ".join(node.value for node in ast.walk(tree)
                           if isinstance(node, ast.Constant) and isinstance(node.value, str))
        self.assertIn("n'a pas de solution réelle", strings)


class LayoutGeometryTests(unittest.TestCase):
    """Build the scene's real geometry without rendering or cloud imports."""

    @classmethod
    def setUpClass(cls):
        try:
            import manim
        except ImportError as error:
            raise unittest.SkipTest("Manim is required for geometry regressions") from error
        cls.manim = manim

    def setUp(self):
        # Scene imports elsewhere in the suite can replace Manim constructors.
        # These lessons use the original font defaults plus black text; restore
        # the incoming constructors afterward so this suite leaks no defaults.
        for cls in (self.manim.Text, self.manim.Tex, self.manim.MathTex):
            previous = cls.__init__
            self.addCleanup(setattr, cls, "__init__", previous)
            cls.set_default()
            cls.set_default(color=self.manim.BLACK)

    def geometry_namespace(self, tree):
        namespace = dict(vars(self.manim))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    if isinstance(node.value, ast.Name) and node.value.id in namespace:
                        value = namespace[node.value.id]
                    else:
                        continue
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        namespace[target.id] = value
        return namespace

    def execute_geometry(self, statements, namespace):
        module = ast.fix_missing_locations(ast.Module(body=statements, type_ignores=[]))
        with tempfile.TemporaryDirectory() as directory:
            with self.manim.tempconfig({"media_dir": directory}):
                exec(compile(module, "<actual scene geometry>", "exec"), namespace)
        return namespace

    def assert_stroke_clear(self, label, stroke, padding=0.04):
        """Check the actual cubic paths, including straight axis/arrow paths."""
        t = self.manim.np.linspace(0, 1, 31)[:, None]
        for p0, p1, p2, p3 in stroke.get_cubic_bezier_tuples():
            points = (1 - t)**3 * p0 + 3 * (1 - t)**2 * t * p1 + 3 * (1 - t) * t**2 * p2 + t**3 * p3
            inside = ((points[:, 0] >= label.get_left()[0] - padding)
                      & (points[:, 0] <= label.get_right()[0] + padding)
                      & (points[:, 1] >= label.get_bottom()[1] - padding)
                      & (points[:, 1] <= label.get_top()[1] + padding))
            self.assertFalse(inside.any(), "A drawn stroke crosses the annotation bounds.")

    def assert_boxes_clear(self, first, second, padding=0.04):
        self.assertTrue(first.get_right()[0] + padding <= second.get_left()[0]
                        or second.get_right()[0] + padding <= first.get_left()[0]
                        or first.get_top()[1] + padding <= second.get_bottom()[1]
                        or second.get_top()[1] + padding <= first.get_bottom()[1])

    def test_all_intended_numeric_axes_have_visible_tick_numbers(self):
        """Evaluate each real constructor; parent axis ink does not set number ink."""
        affected = LESSON_IDS - {"inequations_et_nombres_negatifs",
                                "modeles_affines_et_quadratiques", "completer_le_carre"}
        checked = 0
        for lesson_id in sorted(affected):
            tree = lesson_tree(lesson_id)
            ns = self.geometry_namespace(tree)
            # Parameter values for the generic axes/number-line constructors.
            ns.update(x_min=-3, x_max=3, length=8.6, x_range=[-3, 3, 1],
                      y_range=[-2, 4, 1], x_span=6, y_span=6, unit_size=0.8,
                      font_size=24, kwargs={})
            definitions = [node for node in tree.body if isinstance(node, ast.AnnAssign)
                           and isinstance(node.target, ast.Name)
                           and node.target.id in {"EXPR_A", "EXPR_B", "EVAL_POINTS"}]
            self.execute_geometry(definitions, ns)
            def requests_numbers(call):
                for keyword in call.keywords:
                    value = keyword.value
                    if keyword.arg == "include_numbers" and isinstance(value, ast.Constant):
                        if value.value is True:
                            return True
                    if keyword.arg in {"axis_config", "x_axis_config", "y_axis_config"} and isinstance(value, ast.Dict):
                        if any(isinstance(key, ast.Constant) and key.value == "include_numbers"
                               and isinstance(item, ast.Constant) and item.value is True
                               for key, item in zip(value.keys, value.values)):
                            return True
                return False

            calls = [node for node in ast.walk(tree)
                     if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                     and node.func.id in {"NumberLine", "Axes"}
                     and requests_numbers(node)]
            parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
            for call in calls:
                with self.subTest(lesson_id=lesson_id, line=call.lineno):
                    expression = call
                    parent = parents.get(call)
                    if isinstance(parent, ast.Attribute) and parent.attr == "set_color":
                        expression = parents[parent]
                    with tempfile.TemporaryDirectory() as directory:
                        with self.manim.tempconfig({"media_dir": directory}):
                            mob = eval(compile(ast.Expression(expression), "<scene constructor>", "eval"), ns)
                    axes = [mob] if call.func.id == "NumberLine" else [mob.x_axis, mob.y_axis]
                    self.assertTrue(any(hasattr(axis, "numbers") for axis in axes))
                    for axis in axes:
                        if not hasattr(axis, "numbers"):
                            continue
                        self.assertGreater(len(axis.numbers), 0)
                        for number in axis.numbers:
                            self.assertEqual(number.get_color().to_hex(), "#000000")
                            self.assertEqual(number.num_decimal_places, 0)
                            self.assertNotIn(".", number._get_num_string(number.get_value()))
                            for glyph in number.family_members_with_points():
                                self.assertEqual(glyph.get_color().to_hex(), "#000000")
                    checked += 1
        self.assertEqual(checked, 14)

    def test_domain_circle_test_keeps_equal_units_and_caption_clear(self):
        tree = lesson_tree("domaine_et_image_d_une_fonction")
        ns = self.geometry_namespace(tree)
        heading = next(node for node in ast.walk(tree)
                       if isinstance(node, ast.FunctionDef) and node.name == "make_heading")
        self.execute_geometry([heading], ns)
        ns["self"] = SimpleNamespace(make_heading=lambda text: ns["make_heading"](None, text))
        assignments = {target.id: node for node in ast.walk(tree)
                       if isinstance(node, ast.Assign) for target in node.targets
                       if isinstance(target, ast.Name)}
        names = ("axes", "axis_labels", "upper_half", "graph_label", "domain_projection",
                 "domain_guides", "domain_text", "image_projection", "image_guides",
                 "image_text", "relation_heading", "lower_half", "relation_label",
                 "x_test", "test_line", "y_hit", "hit_points", "not_function")
        self.execute_geometry([assignments[name] for name in names], ns)
        axes, caption = ns["axes"], ns["not_function"]
        # The complete circle must have room before the lower caption is added.
        for name in ("axes", "upper_half", "lower_half", "test_line", "hit_points"):
            with self.subTest(object=name):
                self.assertGreater(ns[name].get_bottom()[1], caption.get_top()[1] + 0.12)
        self.assert_stroke_clear(caption, ns["test_line"])
        self.assert_stroke_clear(caption, ns["lower_half"])
        for name in ("axes", "axis_labels", "upper_half", "lower_half", "test_line",
                     "hit_points", "relation_label", "not_function"):
            with self.subTest(frame_object=name):
                obj = ns[name]
                self.assertGreater(obj.get_bottom()[1], -self.manim.config.frame_height / 2 + 0.2)
                self.assertLess(obj.get_top()[1], ns["relation_heading"].get_bottom()[1] - 0.2)
        # Both pages use the same graph. Preserve its mathematical unit scale,
        # both circle intersections, and the preceding domain/image labels.
        origin = axes.c2p(0, 0)
        self.assertAlmostEqual(self.manim.np.linalg.norm(axes.c2p(1, 0) - origin), 1.2)
        self.assertAlmostEqual(self.manim.np.linalg.norm(axes.c2p(0, 1) - origin), 1.2)
        self.assertGreaterEqual(-axes.y_range[0], 2)
        self.assertGreaterEqual(axes.y_range[1], 2)
        for sign, dot in zip((1, -1), ns["hit_points"]):
            expected = axes.c2p(ns["x_test"], sign * ns["y_hit"])
            self.assertTrue(self.manim.np.allclose(dot.get_center(), expected))
            self.assertAlmostEqual(ns["x_test"]**2 + ns["y_hit"]**2, 4)
            self.assertGreater(expected[1], ns["test_line"].get_bottom()[1] + 0.3)
            self.assertLess(expected[1], ns["test_line"].get_top()[1] - 0.3)
        for label_name in ("graph_label", "relation_label"):
            self.assert_stroke_clear(ns[label_name], ns["upper_half"])
            for axis in (axes.x_axis, axes.y_axis):
                self.assert_stroke_clear(ns[label_name], axis)
            for axis_label in ns["axis_labels"]:
                self.assert_boxes_clear(ns[label_name], axis_label)
        for label_name in ("domain_text", "image_text"):
            for name in ("axes", "upper_half", "domain_guides", "image_guides"):
                self.assertGreater(ns[name].get_bottom()[1], ns[label_name].get_top()[1] + 0.12)

    def test_short_signed_height_labels_clear_the_axis(self):
        tree = lesson_tree("operations_sur_les_fonctions")
        ns = self.geometry_namespace(tree)
        method = copy.deepcopy(next(node for node in ast.walk(tree)
                                    if isinstance(node, ast.FunctionDef)
                                    and node.name == "_clear_horizontal_axis"))
        method.decorator_list = []
        self.execute_geometry([method], ns)
        callers = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Attribute)
                   and node.func.attr == "_clear_horizontal_axis"]
        self.assertEqual({ast.unparse(node.args[0]) for node in callers},
                         {"source_label", "g_label", "opposite_label", "result_label"})
        with tempfile.TemporaryDirectory() as directory:
            with self.manim.tempconfig({"media_dir": directory}):
                axes = self.manim.Axes(x_range=[-3, 3], y_range=[-2, 5],
                                       axis_config={"include_numbers": True})
                axis_y = axes.c2p(0, 0)[1]
                for height, text in ((0.5, r"-g(-2)=\frac12"),
                                     (-0.5, r"g(-2)=-\frac12"), (-1, r"-g(1)=-1")):
                    segment = self.manim.Line(axes.c2p(-2, 0), axes.c2p(-2, height))
                    label = self.manim.MathTex(text).scale(0.62).next_to(segment, self.manim.RIGHT)
                    ns["_clear_horizontal_axis"](label, axes, height)
                    if height > 0:
                        self.assertGreaterEqual(label.get_bottom()[1], axis_y + 0.149)
                    else:
                        self.assertLessEqual(label.get_top()[1], axes.x_axis.numbers.get_bottom()[1] - 0.149)

    def test_polynomial_graph_ticks_clear_the_bottom_caption(self):
        tree = lesson_tree("variables_et_polynomes")
        ns = self.geometry_namespace(tree)
        subtitle = copy.deepcopy(next(node for node in ast.walk(tree)
                                      if isinstance(node, ast.FunctionDef)
                                      and node.name == "_subtitle_box"))
        subtitle.decorator_list = []
        assignments = {target.id: node for node in ast.walk(tree)
                       if isinstance(node, ast.Assign)
                       for target in node.targets if isinstance(target, ast.Name)}
        self.execute_geometry([subtitle, assignments["axes"], assignments["ax_labels"]], ns)
        with tempfile.TemporaryDirectory() as directory:
            with self.manim.tempconfig({"media_dir": directory}):
                caption = ns["_subtitle_box"](None, "P(x) décrit une courbe.")
        ticks = ns["axes"].x_axis.numbers
        self.assertGreater(ticks.get_bottom()[1], caption.get_top()[1] + 0.15)
        self.assertLess(ns["ax_labels"].get_top()[1], self.manim.config.frame_height / 2 - 0.2)

    def test_restriction_card_text_has_readable_contrast(self):
        tree = lesson_tree("fonction_reciproque")
        ns = self.geometry_namespace(tree)
        assignments = {target.id: node for node in ast.walk(tree)
                       if isinstance(node, ast.Assign)
                       for target in node.targets if isinstance(target, ast.Name)}
        for name in ("inverse_color", "inverse_ink"):
            if name in assignments:
                self.execute_geometry([assignments[name]], ns)
        panel = assignments["ambiguity_panel"].value
        fill = next(k.value for k in panel.keywords if k.arg == "fill_color")
        opacity = ast.literal_eval(next(k.value for k in panel.keywords if k.arg == "fill_opacity"))
        fill_rgb = self.manim.ManimColor(eval(compile(ast.Expression(fill), "<card color>", "eval"), ns)).to_rgb()
        background = [1 - opacity + opacity * channel for channel in fill_rgb]

        def luminance(rgb):
            linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
            return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))

        for name in ("restriction", "restricted_rule", "unique_note"):
            call = assignments[name].value
            color = next(k.value for k in call.keywords if k.arg == "color")
            rgb = self.manim.ManimColor(eval(compile(ast.Expression(color), "<text color>", "eval"), ns)).to_rgb()
            self.assertGreater((luminance(background) + 0.05) / (luminance(rgb) + 0.05), 4.5)

    def test_composition_values_clear_static_tick_numbers(self):
        tree = lesson_tree("composition_de_fonctions")
        ns = self.geometry_namespace(tree)
        ns["accent"] = self.manim.BLUE_D
        decimal = copy.deepcopy(next(node for node in ast.walk(tree)
                                     if isinstance(node, ast.FunctionDef) and node.name == "_decimal"))
        decimal.decorator_list = []
        methods = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                   and node.name == "proportional_axes"]
        panel = copy.deepcopy(next(node for node in ast.walk(tree)
                                   if isinstance(node, ast.FunctionDef) and node.name == "_panel"))
        panel.decorator_list = []
        self.execute_geometry([decimal, panel, *methods], ns)
        ns["self"] = SimpleNamespace(_decimal=ns["_decimal"], _panel=ns["_panel"])
        construct = next(node for node in ast.walk(tree)
                         if isinstance(node, ast.FunctionDef) and node.name == "construct")
        names = {"common_x_range", "common_y_range", "unit_size", "axes_f", "axes_g", "x_tracker",
                 "x_number", "fx_number_left", "fx_number_right", "gfx_number", "axes_f_labels", "axes_g_labels",
                 "invalid_mark", "invalid_note", "title", "top_chain", "substitution_steps",
                 "substitution_panel", "domain_lines", "domain_panel", "transfer_text", "transfer_background",
                 "transfer_label", "f_label", "g_label"}
        ns["warning"] = self.manim.RED_D
        selected = []
        for node in construct.body:
            if isinstance(node, ast.FunctionDef) and node.name in {"f", "g", "x_value", "f_value", "g_value"}:
                selected.append(node)
            elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
                selected.append(node)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and ast.unparse(node.value).startswith(("axes_f.shift", "axes_g.shift", "invalid_mark.", "invalid_note.", "substitution_steps.", "domain_lines.", "transfer_text.", "f_label.", "g_label.")):
                selected.append(node)
            elif isinstance(node, ast.For) and "axes_f_labels[0]" in ast.unparse(node.iter):
                selected.append(node)
        self.execute_geometry(selected, ns)
        for name, axis in (("x_number", "axes_f"), ("fx_number_right", "axes_g")):
            self.assertLess(ns[name].get_top()[1], ns[axis].x_axis.numbers.get_bottom()[1] - 0.149)
        for name, axis in (("fx_number_left", "axes_f"), ("gfx_number", "axes_g")):
            self.assertLess(ns[name].get_right()[0], ns[axis].y_axis.numbers.get_left()[0] - 0.149)
        with tempfile.TemporaryDirectory() as directory:
            with self.manim.tempconfig({"media_dir": directory}):
                for x in (3, 0, -0.1, -0.2, -0.9, -1, 0, 0.2, 3):
                    ns["x_tracker"].set_value(x)
                    for name in ("x_number", "fx_number_left", "fx_number_right", "gfx_number"):
                        number = ns[name]
                        number.update()
                        self.assertGreater(number.z_index, 0)
                        self.assertAlmostEqual(float(number.background_rectangle.get_fill_opacity()), 1)
                        self.assertTrue(self.manim.np.allclose(number.background_rectangle.get_fill_rgbas()[0, :3], 1))
                    ns["top_chain"].update()
                    if x < 0:
                        reference = ns["_decimal"](x, ns["accent"])[1][0]
                        for number in (ns["x_number"], ns["top_chain"][1]):
                            backing, digits = number
                            minus = digits[0]
                            # The old helper reused a BackgroundRectangle as
                            # this minus path when always_redraw gained a digit.
                            self.assertIsInstance(backing, self.manim.BackgroundRectangle)
                            self.assertFalse(any(isinstance(part, self.manim.BackgroundRectangle)
                                                 for part in minus.get_family()))
                            self.assertAlmostEqual(minus.width, reference.width)
                            self.assertAlmostEqual(minus.height, reference.height)
                            actual_paths = minus.family_members_with_points()
                            expected_paths = reference.family_members_with_points()
                            self.assertEqual(len(actual_paths), len(expected_paths))
                            for actual, expected in zip(actual_paths, expected_paths):
                                # become may subdivide curves while aligning;
                                # compare the displayed outline, not its count
                                # of internal Bézier control points.
                                samples = self.manim.np.linspace(0, 1, 251)
                                actual_outline = self.manim.np.array([actual.point_from_proportion(t) - actual.get_center() for t in samples])
                                expected_outline = self.manim.np.array([expected.point_from_proportion(t) - expected.get_center() for t in samples])
                                distances = self.manim.np.linalg.norm(actual_outline[:, None] - expected_outline[None, :], axis=2)
                                # Matching may change the contour starting
                                # point, so compare geometric outlines in both
                                # directions rather than their traversal order.
                                self.assertLess(distances.min(axis=0).max(), 0.002)
                                self.assertLess(distances.min(axis=1).max(), 0.002)
                                self.assertTrue(self.manim.np.allclose(actual.get_fill_rgbas()[0, :3], ns["accent"].to_rgb()))
                                self.assertAlmostEqual(float(actual.get_fill_opacity()), 1)
                                self.assertGreaterEqual(actual.z_index, backing.z_index)
                                self.assertLess(number.get_family().index(backing), number.get_family().index(actual))
        # Sweep every displayed value over the actual input interval, checking
        # the full opaque backing against BOTH coordinate-number sets.
        endpoints = [ns["x_tracker"].get_value()] + [float(ast.literal_eval(call.args[0]))
                     for call in ast.walk(construct) if isinstance(call, ast.Call)
                     and ast.unparse(call.func) == "x_tracker.animate.set_value"]
        numerals = [number for axes in (ns["axes_f"], ns["axes_g"])
                    for axis in (axes.x_axis, axes.y_axis) for number in axis.numbers]
        with tempfile.TemporaryDirectory() as directory:
            with self.manim.tempconfig({"media_dir": directory}):
                for x in self.manim.np.linspace(min(endpoints), max(endpoints), 101):
                    ns["x_tracker"].set_value(x)
                    visible = ["x_number", "fx_number_left", "fx_number_right"]
                    if ns["f_value"]() >= 0:
                        visible.append("gfx_number")
                    for name in visible:
                        number = ns[name]
                        number.update()
                        with self.subTest(x=x, moving_value=name):
                            for numeral in numerals:
                                self.assert_boxes_clear(number, numeral)
                            for panel_name in ("substitution_panel", "domain_panel", "transfer_label", "f_label", "g_label"):
                                self.assert_boxes_clear(number, ns[panel_name])
                            self.assertGreater(number.get_left()[0], -self.manim.config.frame_width / 2 + 0.1)
                            self.assertLess(number.get_right()[0], self.manim.config.frame_width / 2 - 0.1)
        for numeral in numerals:
            self.assert_boxes_clear(ns["invalid_note"], numeral)
        for axis in (ns["axes_f"], ns["axes_g"]):
            for number in axis.x_axis.numbers:
                self.assertGreater(number.z_index, 0)
                self.assertAlmostEqual(float(number.background_rectangle.get_fill_opacity()), 1)
        for label in (ns["axes_f_labels"][0], ns["axes_g_labels"][0], ns["invalid_note"]):
            self.assertGreater(label.z_index, 0)
            self.assertAlmostEqual(float(label.background_rectangle.get_fill_opacity()), 1)

    def test_reciprocal_graph_labels_and_coordinate_words_have_clearance(self):
        tree = lesson_tree("fonction_reciproque")
        ns = self.geometry_namespace(tree)
        ns.update(accent=self.manim.BLUE_D, inverse_color=self.manim.GREEN_D)
        selected = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name == "proportional_axes"]
        construct = next(node for node in ast.walk(tree)
                         if isinstance(node, ast.FunctionDef) and node.name == "construct")
        names = {"axes", "f_graph", "inv_graph", "f_graph_label", "inv_graph_label", "coordinate_panel",
                 "point_before", "swap_arrow", "point_after", "point_row", "coordinate_words", "square_axes"}
        for node in construct.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
                selected.append(node)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and ast.unparse(node.value).split(".", 1)[0] in names:
                selected.append(node)
            elif isinstance(node, ast.For) and ast.unparse(node.iter) == "square_axes.y_axis.numbers":
                selected.append(node)
        self.execute_geometry(selected, ns)
        self.assertGreater(ns["f_graph_label"].get_left()[0], ns["axes"].c2p(0, 0)[0] + 0.15)
        for label_name, graph_name in (("f_graph_label", "f_graph"), ("inv_graph_label", "inv_graph")):
            label, curve = ns[label_name], ns[graph_name]
            for alpha in self.manim.np.linspace(0, 1, 1001):
                point = curve.point_from_proportion(alpha)
                self.assertFalse(label.get_left()[0] - 0.08 <= point[0] <= label.get_right()[0] + 0.08
                                 and label.get_bottom()[1] - 0.08 <= point[1] <= label.get_top()[1] + 0.08)
        panel, words = ns["coordinate_panel"], ns["coordinate_words"]
        self.assertGreater(words.get_left()[0], panel.get_left()[0] + 0.2)
        self.assertLess(words.get_right()[0], panel.get_right()[0] - 0.2)
        four = next(number for number in ns["square_axes"].y_axis.numbers if number.get_value() == 4)
        self.assertGreater(four.z_index, 0)
        self.assertAlmostEqual(float(four.background_rectangle.get_fill_opacity()), 1)

    def test_product_curve_keeps_the_minus_one_tick_readable(self):
        tree = lesson_tree("racines_et_hauteur_zero")
        ns = self.geometry_namespace(tree)
        selected = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == "proportional_axes"]
        construct = next(n for n in ast.walk(tree)
                         if isinstance(n, ast.FunctionDef) and n.name == "construct")
        selected += [n for n in construct.body if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id in {"ink", "accent"} for t in n.targets)]
        section = next(n for n in construct.body if isinstance(n, ast.With)
                       and any(isinstance(c, ast.Assign) and any(isinstance(t, ast.Name)
                               and t.id == "axes2" for t in c.targets) for c in n.body))
        started = False
        for node in section.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "axes2"
                                                   for t in node.targets):
                started = True
            if started:
                if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "play"):
                    break
                selected.append(node)
        self.execute_geometry(selected, ns)
        axes, graph = ns["axes2"], ns["graph2"]
        number = next(n for n in axes.y_axis.numbers if n.get_value() == -1)
        backing = getattr(number, "background_rectangle", None)
        glyphs = self.manim.VGroup(*[part for part in number if part is not backing])
        # Confirm this is the real crossing, not an unrelated protected tick.
        t = self.manim.np.linspace(0, 1, 101)[:, None]
        paths = []
        for p0, p1, p2, p3 in graph.get_cubic_bezier_tuples():
            paths.append((1-t)**3*p0 + 3*(1-t)**2*t*p1 + 3*(1-t)*t**2*p2 + t**3*p3)
        points = self.manim.np.concatenate(paths)
        inside = ((points[:, 0] >= glyphs.get_left()[0]) & (points[:, 0] <= glyphs.get_right()[0])
                  & (points[:, 1] >= glyphs.get_bottom()[1]) & (points[:, 1] <= glyphs.get_top()[1]))
        self.assertTrue(inside.any(), "The authored product curve must exercise the reported tick crossing.")
        self.assertIsNotNone(backing, "The curve would cross the unprotected -1 numeral.")
        self.assertGreater(number.z_index, graph.z_index)
        self.assertAlmostEqual(float(backing.get_fill_opacity()), 1)
        self.assertTrue(self.manim.np.allclose(backing.get_fill_rgbas()[0, :3], self.manim.WHITE.to_rgb()))
        for part in glyphs.family_members_with_points():
            self.assertTrue(self.manim.np.allclose(part.get_fill_rgbas()[0, :3], self.manim.BLACK.to_rgb()))
        self.assertGreater(glyphs.get_left()[0] - backing.get_left()[0], 0.03)
        self.assertGreater(backing.get_right()[0] - glyphs.get_right()[0], 0.03)
        for other in [*axes.x_axis.numbers, *axes.y_axis.numbers]:
            if other is not number:
                self.assert_boxes_clear(backing, other)
        self.assertAlmostEqual(axes.x_axis.get_unit_size(), 0.55)
        self.assertAlmostEqual(axes.y_axis.get_unit_size(), 0.55)
        for name, x in (("root_minus_dot", -1), ("root_two_dot", 2)):
            self.assertEqual(ns["g"](x), 0)
            self.assertTrue(self.manim.np.allclose(ns[name].get_center(), axes.c2p(x, 0)))

    def test_root_coordinate_label_clears_static_tick_numbers(self):
        tree = lesson_tree("racines_et_hauteur_zero")
        ns = self.geometry_namespace(tree)
        ns["accent"] = self.manim.BLUE_D
        selected = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name == "proportional_axes"]
        construct = next(node for node in ast.walk(tree)
                         if isinstance(node, ast.FunctionDef) and node.name == "construct")
        for node in construct.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {"ink", "axes", "axis_labels", "graph", "root_dot", "root_label", "zero_height_label"} for t in node.targets):
                selected.append(node)
            elif isinstance(node, ast.FunctionDef) and node.name == "f":
                selected.append(node)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and ast.unparse(node.value).startswith(("root_label.", "zero_height_label.", "axis_labels[0].")):
                selected.append(node)
        self.execute_geometry(selected, ns)
        self.assertLess(ns["root_label"].get_top()[1], ns["axes"].x_axis.numbers.get_bottom()[1] - 0.149)
        label, axes = ns["zero_height_label"], ns["axes"]
        self.assertGreater(label.get_left()[0], axes.y_axis.get_right()[0] + 0.15)
        self.assertGreater(label.get_bottom()[1], axes.x_axis.get_top()[1] + 0.15)
        self.assertGreater(label.get_bottom()[1], ns["graph"].get_top()[1] + 0.15)
        self.assertLess(label.get_top()[1], axes.c2p(0, 3)[1] - 0.1)
        for number in [*axes.x_axis.numbers, *axes.y_axis.numbers]:
            self.assertTrue(label.get_left()[0] > number.get_right()[0] + 0.1
                            or label.get_right()[0] < number.get_left()[0] - 0.1
                            or label.get_bottom()[1] > number.get_top()[1] + 0.1
                            or label.get_top()[1] < number.get_bottom()[1] - 0.1)
        self.assertAlmostEqual(ns["axis_labels"][0].get_y(), ns["axes"].c2p(0, 0)[1])

    def test_multiplicity_panels_and_conclusions_have_clear_regions(self):
        tree = lesson_tree("multiplicite_des_racines")
        ns = self.geometry_namespace(tree)
        ns["accent"] = self.manim.BLUE_D
        methods = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                   and node.name in {"proportional_axes", "sign_row"}]
        construct = next(node for node in ast.walk(tree)
                         if isinstance(node, ast.FunctionDef) and node.name == "construct")
        geometry_names = {"axes", "axes3", "visible_cube_x", "graph_x3", "cube_signs",
                          "pale", "muted", "ghost_label", "cube_label", "ghost_line", "neighborhood",
                          "signs_x", "signs_x2", "cross_conclusion", "touch_conclusion",
                          "shift_axes", "root_zero", "root_zero_label", "root_two", "root_two_label",
                          "product_axes", "root_minus_two", "root_one", "root_minus_label", "root_one_label",
                          "horizontal_arrow", "shift_label"}
        selected = methods[:]
        for node in construct.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in geometry_names for t in node.targets):
                selected.append(node)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                if ast.unparse(node.value).split(".", 1)[0] in {"cross_conclusion", "touch_conclusion", "root_zero_label", "root_two_label", "root_minus_label", "root_one_label", "shift_label"}:
                    selected.append(node)
            elif isinstance(node, ast.For) and ast.unparse(node.iter) in {"product_axes.x_axis.numbers", "(ghost_label, cube_label)"}:
                selected.append(node)
        start = next(i for i, node in enumerate(construct.body)
                     if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "general_formula" for t in node.targets))
        for node in construct.body[start:]:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "warning" for t in node.targets):
                break
            selected.append(node)
        self.execute_geometry(selected, ns)
        self.assertLess(ns["odd_box"].get_top()[1], ns["general_formula"].get_bottom()[1] - 0.29)
        self.assertLess(ns["even_box"].get_top()[1], ns["odd_box"].get_bottom()[1] - 0.19)
        self.assertGreater(ns["even_box"].get_bottom()[1], ns["flatter_rule"].get_top()[1] + 0.15)
        for name in ("cross_conclusion", "touch_conclusion"):
            self.assertLess(ns[name].get_right()[0], ns["axes"].get_left()[0] - 0.15)
        self.assertGreater(ns["graph_x3"].get_bottom()[1], ns["cube_signs"].get_top()[1] + 0.15)
        self.assertGreaterEqual(ns["graph_x3"].get_bottom()[1], ns["axes3"].get_bottom()[1] - 0.01)
        self.assertLessEqual(ns["graph_x3"].get_top()[1], ns["axes3"].get_top()[1] + 0.01)
        for name in ("ghost_label", "cube_label"):
            label = ns[name]
            for stroke in (ns["graph_x3"], ns["ghost_line"], ns["axes3"].x_axis,
                           ns["axes3"].y_axis, *ns["neighborhood"]):
                self.assert_stroke_clear(label, stroke)
            for numeral in (*ns["axes3"].x_axis.numbers, *ns["axes3"].y_axis.numbers):
                self.assert_boxes_clear(label, numeral)
            self.assertLess(label.get_right()[0], self.manim.config.frame_width / 2 - 0.2)
        self.assert_boxes_clear(ns["ghost_label"], ns["cube_label"], padding=0.15)
        self.assertGreater(ns["root_zero_label"].get_left()[0], ns["shift_axes"].c2p(0, 0)[0] + 0.1)
        for name in ("root_zero_label", "root_two_label"):
            self.assertLess(ns[name].get_top()[1], ns["shift_axes"].x_axis.numbers.get_bottom()[1] - 0.149)
        for name in ("root_minus_label", "root_one_label"):
            self.assertLess(ns[name].get_top()[1], ns["product_axes"].x_axis.numbers.get_bottom()[1] - 0.149)
        self.assertLess(ns["root_minus_label"].get_right()[0], ns["root_minus_two"].get_x() - 0.05)
        self.assertGreater(ns["root_one_label"].get_left()[0], ns["root_one"].get_x() + 0.05)
        for label in (ns["shift_label"], ns["root_minus_label"], ns["root_one_label"], *ns["product_axes"].x_axis.numbers):
            self.assertGreater(label.z_index, 0)
            self.assertAlmostEqual(float(label.background_rectangle.get_fill_opacity()), 1)

    def test_proof_conclusions_are_contained_in_their_cards(self):
        tree = lesson_tree("racine_carree_et_valeur_absolue")
        ns = self.geometry_namespace(tree)
        methods = [copy.deepcopy(node) for node in ast.walk(tree)
                   if isinstance(node, ast.FunctionDef) and node.name in {"heading", "card"}]
        for method in methods:
            method.decorator_list = []
        self.execute_geometry(methods, ns)
        ns["self"] = SimpleNamespace(heading=ns["heading"], card=ns["card"])
        construct = next(node for node in ast.walk(tree)
                         if isinstance(node, ast.FunctionDef) and node.name == "construct")
        start = next(i for i, node in enumerate(construct.body)
                     if isinstance(node, ast.Assign)
                     and "Corriger et démontrer la formule" in ast.unparse(node))
        selected = []
        for node in construct.body[start:]:
            if isinstance(node, ast.With):
                break
            selected.append(node)
        self.execute_geometry(selected, ns)
        for prefix, names in (("positive", ("title", "abs", "root", "result")),
                              ("negative", ("title", "positive", "abs", "root", "result"))):
            box = ns[prefix + "_box"]
            for name in names:
                row = ns[prefix + "_" + name]
                self.assertGreater(row.get_bottom()[1], box.get_bottom()[1] + 0.15)
                self.assertLess(row.get_top()[1], box.get_top()[1] - 0.15)
                self.assertGreater(row.get_left()[0], box.get_left()[0] + 0.15)
                self.assertLess(row.get_right()[0], box.get_right()[0] - 0.15)
            self.assertGreater(box.get_bottom()[1], ns["conclusion"].get_top()[1] + 0.15)

    def test_reflected_parabola_and_its_transitions_stay_above_caption(self):
        tree = lesson_tree("lire_les_proprietes_d_un_graphe")
        ns = self.geometry_namespace(tree)
        method = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef) and node.name == "_section_transformations")
        names = {"unit", "c_out", "c_in", "c_final", "axes", "section_title"}
        selected = [node for node in method.body
                    if (isinstance(node, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id in names for t in node.targets))
                    or (isinstance(node, ast.FunctionDef) and node.name == "proportional_axes")]
        selected.extend(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                        and node.name in {"_subtitle_box", "_show_caption"})
        self.execute_geometry(selected, ns)
        ns["self"] = SimpleNamespace(play=lambda *args, **kwargs: None)
        ns["self"]._subtitle_box = lambda text: ns["_subtitle_box"](ns["self"], text)
        ns["self"]._show_caption = lambda text: ns["_show_caption"](ns["self"], text)
        section = next(node for node in method.body if isinstance(node, ast.With)
                       and "S4_parabola" in ast.unparse(node.items[0].context_expr))
        self.execute_geometry([node for node in section.body if isinstance(node, ast.Assign)], ns)
        axes, caption = ns["axes"], ns["cap"]
        origin = axes.c2p(0, 0)
        self.assertAlmostEqual(self.manim.np.linalg.norm(axes.c2p(1, 0) - origin), 0.58)
        self.assertAlmostEqual(self.manim.np.linalg.norm(axes.c2p(0, 1) - origin), 0.58)

        def check_curve(curve):
            self.assertGreater(curve.get_bottom()[1], caption.get_top()[1] + 0.15)
            self.assertGreaterEqual(curve.get_bottom()[1], axes.c2p(0, axes.y_range[0])[1] - 0.001)
            self.assertLessEqual(curve.get_top()[1], axes.c2p(0, axes.y_range[1])[1] + 0.001)
            self.assertGreaterEqual(curve.get_left()[0], axes.c2p(axes.x_range[0], 0)[0] - 0.001)
            self.assertLessEqual(curve.get_right()[0], axes.c2p(axes.x_range[1], 0)[0] + 0.001)

        for name in ("p_graph", "p_shift_graph", "p_reflect_graph", "p_final_graph"):
            with self.subTest(curve=name):
                check_curve(ns[name])
        # The displayed interval is clipped; the function and its vertex remain.
        curve = ns["p_reflect_graph"]
        for alpha in self.manim.np.linspace(0, 1, 101):
            x, y = axes.p2c(curve.point_from_proportion(alpha))[:2]
            self.assertAlmostEqual(y, -(x - 2)**2, delta=0.005)
        self.assertLess(self.manim.np.linalg.norm(curve.point_from_proportion(0.5) - axes.c2p(2, 0)), 0.01)
        for outgoing, incoming in (("p_shift_graph", "p_reflect_graph"),
                                   ("p_reflect_graph", "p_final_graph")):
            call = next(node for node in ast.walk(section) if isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name) and node.func.id == "ReplacementTransform"
                        and [ast.unparse(arg) for arg in node.args] == [outgoing, incoming])
            local = dict(ns, **{name: ns[name].copy() for name in (outgoing, incoming)})
            animation = eval(compile(ast.Expression(call), "<actual parabola transition>", "eval"), local)
            animation.begin()
            for frame in range(61):
                animation.interpolate(frame / 60)
                with self.subTest(transition=(outgoing, incoming), frame=frame):
                    check_curve(animation.mobject)
            animation.finish()

    def test_stretched_coordinate_label_clears_the_horizontal_axis(self):
        tree = lesson_tree("lire_les_proprietes_d_un_graphe")
        ns = self.geometry_namespace(tree)
        method = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef) and node.name == "_section_transformations")
        selected = []
        for node in method.body:
            if isinstance(node, ast.With):
                if "S4_reflections" in ast.unparse(node.items[0]):
                    break
                continue
            selected.append(node)
        self.execute_geometry(selected, ns)
        label = ns["pts_stretch"][3]
        axis_y = ns["axes"].c2p(0, 0)[1]
        self.assertLess(label.get_top()[1], axis_y - 0.25)
        self.assertGreater(label.get_bottom()[1], ns["pts_stretch"][-1].get_top()[1] + 0.15)
        self.assertLess(label.get_top()[1], ns["axes"].x_axis.numbers.get_bottom()[1] - 0.149)
        self.assertLess(ns["pts_h"][3].get_top()[1], ns["axes"].x_axis.numbers.get_bottom()[1] - 0.149)
        for name in ("tag_in", "tag_out"):
            self.assertGreater(ns[name].get_left()[0], ns["axes"].y_axis.numbers.get_right()[0] + 0.15)
        self.assertGreater(ns["pts_compress"][3].get_left()[0], ns["axes"].y_axis.get_right()[0] + 0.249)
        self.assertGreater(ns["pts_compress"][3].get_bottom()[1], ns["graph_compress"].get_top()[1] + 0.199)
        self.assertGreater(ns["pts_stretch"][2].get_bottom()[1], ns["graph_stretch"].get_top()[1] + 0.179)
        self.assertLess(ns["pts_reflect_x"][3].get_right()[0], ns["axes"].y_axis.numbers.get_left()[0] - 0.1)
        for name in ("pts_h", "pts_compress", "pts_stretch"):
            reason = ns[name][5]
            self.assertGreater(reason.get_left()[0], ns["axes"].y_axis.get_right()[0] + 0.249)
            self.assertLess(reason.get_right()[0], self.manim.config.frame_width / 2 - 0.2)
        # Reflection arrow passes the -1 numeral; its backing must stay opaque
        # after the actual axes Create animation, above all arrow family paths.
        creation = self.manim.Create(ns["axes"])
        creation.begin()
        creation.interpolate(1)
        creation.finish()
        for numeral in ns["axes"].x_axis.numbers:
            backing = numeral.background_rectangle
            self.assertAlmostEqual(float(backing.get_fill_opacity()), 1)
            self.assertGreater(numeral.z_index, max(part.z_index for part in ns["pts_reflect_x"][4].get_family()))
            glyphs = self.manim.VGroup(*[part for part in numeral if part is not backing])
            self.assertGreater(glyphs.get_left()[0] - backing.get_left()[0], 0.03)
            self.assertGreater(backing.get_right()[0] - glyphs.get_right()[0], 0.03)
        for group_name, curve_name in (("pts", "graph_up"), ("pts_h", "graph_right"),
                                       ("pts_compress", "graph_compress"), ("pts_stretch", "graph_stretch"),
                                       ("pts_reflect_x", "graph_reflect_x"), ("pts_reflect_y", "graph_reflect_y")):
            group = ns[group_name]
            for index in (2, 3):
                with self.subTest(group=group_name, label=index):
                    label = group[index]
                    for stroke in (ns["axes"].x_axis, ns["axes"].y_axis,
                                   ns["graph_f"], ns[curve_name], group[4]):
                        self.assert_stroke_clear(label, stroke)
                    for numeral in (*ns["axes"].x_axis.numbers, *ns["axes"].y_axis.numbers):
                        self.assert_boxes_clear(label, numeral)

    def test_polynomial_values_and_drop_line_clear_axes_ticks_and_curve(self):
        tree = lesson_tree("lire_les_proprietes_d_un_graphe")
        ns = self.geometry_namespace(tree)
        method = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef) and node.name == "_section_polynomial")
        names = {"axes", "curve_full", "dot_p1", "dot_m1", "vline_p1", "vline_m1",
                 "lbl_f1", "lbl_fm1", "root_neg1", "root_3", "lbl_rn1", "lbl_r3"}
        selected = [node for node in method.body
                    if isinstance(node, ast.FunctionDef) and node.name == "f"
                    or isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets)]
        self.execute_geometry(selected, ns)
        for name in ("lbl_f1", "lbl_fm1"):
            label = ns[name]
            for stroke in (ns["axes"].x_axis, ns["axes"].y_axis, ns["curve_full"],
                           *ns["vline_p1"], ns["vline_m1"]):
                self.assert_stroke_clear(label, stroke)
            for numeral in (*ns["axes"].x_axis.numbers, *ns["axes"].y_axis.numbers):
                self.assert_boxes_clear(label, numeral)
            for root_label in (ns["lbl_rn1"], ns["lbl_r3"]):
                self.assert_boxes_clear(label, root_label)
            self.assertGreater(label.get_bottom()[1], -3.1)
        for stroke in ns["vline_p1"]:
            for numeral in ns["axes"].x_axis.numbers:
                self.assert_stroke_clear(numeral, stroke)
        self.assert_boxes_clear(ns["lbl_f1"], ns["lbl_fm1"])

    def test_multiplicity_scanners_and_sign_transitions_preserve_legibility(self):
        tree = lesson_tree("multiplicite_des_racines")
        ns = self.geometry_namespace(tree)
        selected = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name in {"proportional_axes", "vertical_scanner"}]
        construct = next(node for node in ast.walk(tree)
                         if isinstance(node, ast.FunctionDef) and node.name == "construct")
        names = {"muted", "axes", "product_axes", "tracker_x", "tracker_x2", "scanner_x",
                 "scanner_x2", "simple_scanner", "double_scanner"}
        for node in construct.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
                selected.append(node)
            elif isinstance(node, ast.For) and ast.unparse(node.iter) == "product_axes.x_axis.numbers":
                selected.append(node)
        self.execute_geometry(selected, ns)
        for name, axis_name in (("scanner_x", "axes"), ("scanner_x2", "axes"),
                                ("simple_scanner", "product_axes"), ("double_scanner", "product_axes")):
            for x in self.manim.np.linspace(-1, 1, 101):
                for tracker in (ns["tracker_x"], ns["tracker_x2"]):
                    tracker.set_value(x)
                scanner = ns[name]
                scanner.update()
                for stroke in scanner:
                    for number in ns[axis_name].x_axis.numbers:
                        self.assert_stroke_clear(number, stroke)
        # Execute the actual conclusion play calls with animation spies: no
        # frame may contain the outgoing value and incoming sign row together.
        for suffix in ("x", "x2"):
            calls = []
            for node in ast.walk(construct):
                if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                        and ast.unparse(node.value.func) == "self.play"):
                    continue
                rendered = ast.unparse(node.value)
                if f"FadeOut(value_right_{suffix})" in rendered or f"FadeIn(signs_{suffix})" in rendered:
                    calls.append(node)
            calls.sort(key=lambda node: node.lineno)
            spy = Mock()
            namespace = {"self": SimpleNamespace(play=spy), "FadeOut": lambda obj: ("out", obj),
                         "FadeIn": lambda obj: ("in", obj), f"value_right_{suffix}": "value",
                         f"signs_{suffix}": "signs"}
            self.execute_geometry(calls, namespace)
            self.assertEqual([call.args for call in spy.call_args_list],
                             [(("out", "value"),), (("in", "signs"),)])
            self.assertAlmostEqual(sum(call.kwargs["run_time"] for call in spy.call_args_list), 0.5)

    def test_root_moving_annotations_clear_graph_and_ticks_for_the_whole_motion(self):
        tree = lesson_tree("racines_et_hauteur_zero")
        ns = self.geometry_namespace(tree)
        selected = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name == "proportional_axes"]
        construct = next(node for node in ast.walk(tree)
                         if isinstance(node, ast.FunctionDef) and node.name == "construct")
        names = {"accent", "ink", "axes", "axis_labels", "graph", "x_tracker",
                 "moving_dot", "height", "height_label", "point_label"}
        for node in construct.body:
            if isinstance(node, ast.FunctionDef) and node.name in {"f", "height_annotation"}:
                selected.append(node)
            elif isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in names for target in node.targets):
                selected.append(node)
            elif isinstance(node, ast.Expr) and ast.unparse(node).startswith("axis_labels[0]."):
                selected.append(node)
        self.execute_geometry(selected, ns)
        initial = ns["x_tracker"].get_value()
        endpoint = next(call.args[0].value for call in ast.walk(construct)
                        if isinstance(call, ast.Call) and ast.unparse(call.func) == "x_tracker.animate.set_value")
        with tempfile.TemporaryDirectory() as directory:
            with self.manim.tempconfig({"media_dir": directory}):
                for x in self.manim.np.linspace(initial, endpoint, 101):
                    ns["x_tracker"].set_value(x)
                    for name in ("moving_dot", "height", "height_label", "point_label"):
                        ns[name].update()
                    for name in ("height_label", "point_label"):
                        label = ns[name]
                        with self.subTest(x=x, label=name):
                            for stroke in (ns["axes"].x_axis, ns["axes"].y_axis, ns["graph"], ns["height"]):
                                self.assert_stroke_clear(label, stroke)
                            for numeral in (*ns["axes"].x_axis.numbers, *ns["axes"].y_axis.numbers):
                                self.assert_boxes_clear(label, numeral)
                            for axis_label in ns["axis_labels"]:
                                self.assert_boxes_clear(label, axis_label)
                    self.assert_boxes_clear(ns["height_label"], ns["point_label"])

    def test_piecewise_threshold_guide_stops_before_the_numeral_row(self):
        tree = lesson_tree("fonction_definie_par_morceaux")
        ns = self.geometry_namespace(tree)
        method = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef) and node.name == "acte_1_question_et_intuition")
        assignments = {target.id: node for node in ast.walk(method)
                       if isinstance(node, ast.Assign) for target in node.targets
                       if isinstance(target, ast.Name)}
        self.execute_geometry([assignments["number_line"], assignments["threshold"]], ns)
        line, guide = ns["number_line"], ns["threshold"]
        numeral = next(number for number in line.numbers if number.get_value() == 1)
        self.assertGreater(guide.get_bottom()[1], numeral.get_top()[1] + 0.1)
        self.assertAlmostEqual(guide.get_start()[0], line.n2p(1)[0])
        self.assertAlmostEqual(guide.get_start()[1], line.n2p(1)[1])

    def test_subtraction_result_fractions_clear_ticks_and_neighboring_labels(self):
        tree = lesson_tree("operations_sur_les_fonctions")
        ns = self.geometry_namespace(tree)
        names = {"make_axes", "_dot", "_clear_horizontal_axis",
                 "_exact_vertical_segment", "_x_label", "f", "g", "neg_g", "diff_fg"}
        definitions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in names:
                node = copy.deepcopy(node)
                node.decorator_list = []
                definitions.append(node)
        self.execute_geometry(definitions, ns)
        construct = next(n for n in ast.walk(tree)
                         if isinstance(n, ast.FunctionDef) and n.name == "construct")
        colors = [n for n in construct.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id.startswith("C_") for t in n.targets)]
        self.execute_geometry(colors, ns)
        ns["self"] = SimpleNamespace(**{name: ns[name] for name in names if name.startswith("_")})
        sample = copy.deepcopy(next(n for n in ast.walk(tree)
                                    if isinstance(n, ast.FunctionDef) and n.name == "show_subtraction_sample"))
        geometry = []
        for node in sample.body:
            if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "play"):
                break
            geometry.append(node)
        sample.body = geometry + [ast.parse("return locals()").body[0]]
        self.execute_geometry([sample], ns)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == "show_subtraction_sample"]
        self.assertEqual(len(calls), 2)
        with tempfile.TemporaryDirectory() as directory:
            with self.manim.tempconfig({"media_dir": directory}):
                axes = ns["axes"] = ns["make_axes"]()
                for call in calls:
                    objects = eval(compile(ast.Expression(call), "<authored subtraction example>", "eval"), ns)
                    with self.subTest(x=objects["x"]):
                        label = objects["result_label"]
                        for axis in (axes.x_axis, axes.y_axis):
                            self.assert_stroke_clear(label, axis)
                            for tick in axis.numbers:
                                self.assert_boxes_clear(label, tick)
                        for name in ("x_label", "g_label", "opposite_label"):
                            self.assert_boxes_clear(label, objects[name], padding=0.1)
                        for name in ("g_segment", "opposite_segment", "target_segment"):
                            self.assert_stroke_clear(label, objects[name])
                        self.assertGreater(label.get_left()[0], -self.manim.config.frame_x_radius + 0.5)
                        self.assertLess(label.get_right()[0], self.manim.config.frame_x_radius - 0.5)
                        self.assertGreater(label.get_bottom()[1], -self.manim.config.frame_y_radius + 0.5)
                        self.assertAlmostEqual(objects["dx"], ns["f"](objects["x"]) - ns["g"](objects["x"]))
                        self.assertTrue(self.manim.np.allclose(objects["dot_diff"].get_center(),
                                                             axes.c2p(objects["x"], objects["dx"])))
                        if objects["dx"] < 0:
                            self.assertLess(label.get_top()[1], axes.x_axis.numbers.get_bottom()[1] - 0.14)
                            for function in (ns["f"], ns["g"]):
                                self.assert_stroke_clear(label, axes.plot(function, x_range=[-2.15, 2.15]))

    def test_signed_segments_preserve_legibility_of_ticks_and_labels(self):
        tree = lesson_tree("operations_sur_les_fonctions")
        ns = self.geometry_namespace(tree)
        definitions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in {
                    "make_axes", "_clear_horizontal_axis", "_exact_vertical_segment", "_scanner"}:
                node = copy.deepcopy(node)
                node.decorator_list = []
                definitions.append(node)
        self.execute_geometry(definitions, ns)
        with tempfile.TemporaryDirectory() as directory:
            with self.manim.tempconfig({"media_dir": directory}):
                axes = ns["make_axes"]()
                for x, height in ((-2, -0.5), (1, -1)):
                    tick = next(number for number in axes.x_axis.numbers if number.get_value() == x)
                    guide = ns["_scanner"](axes, x)
                    segment = ns["_exact_vertical_segment"](axes, x, 0, height, self.manim.BLUE_D)
                    self.assertAlmostEqual(segment.get_end()[1], axes.c2p(x, height)[1])
                    self.assertGreater(tick.z_index, max(guide.z_index, segment.z_index))
                    backing = tick.background_rectangle
                    self.assertTrue(self.manim.np.allclose(backing.get_fill_rgbas()[0, :3], self.manim.WHITE.to_rgb()))
                    self.assertAlmostEqual(float(backing.get_fill_opacity()), 1)
                    glyphs = self.manim.VGroup(*[part for part in tick if part is not backing])
                    self.assertGreater(glyphs.get_left()[0] - backing.get_left()[0], 0.03)
                    self.assertGreater(backing.get_right()[0] - glyphs.get_right()[0], 0.03)
                label = self.manim.MathTex(r"g(1)=1").scale(0.62)
                label.next_to(ns["_exact_vertical_segment"](axes, 1, 0, 1, self.manim.BLUE_D), self.manim.RIGHT)
                ns["_clear_horizontal_axis"](label, axes, 1)
                self.assertGreater(label.z_index, 0)
                self.assertTrue(self.manim.np.allclose(label.background_rectangle.get_fill_rgbas()[0, :3], self.manim.WHITE.to_rgb()))
                self.assertAlmostEqual(float(label.background_rectangle.get_fill_opacity()), 1)

    def test_quadratic_opening_formula_and_question_clear_the_plot(self):
        tree = lesson_tree("completer_le_carre")
        ns = self.geometry_namespace(tree)
        method = next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == "_scene1_hook")
        names = {"eq_standard", "question", "axes", "parabola"}
        selected = [n for n in method.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)]
        self.execute_geometry(selected, ns)
        axes, curve = ns["axes"], ns["parabola"]
        self.assertAlmostEqual(ns["eq_standard"].font_size, 56)
        self.assertAlmostEqual(ns["question"].font_size, 30)
        self.assert_boxes_clear(ns["eq_standard"], ns["question"], padding=0.45)
        for name in ("eq_standard", "question"):
            with self.subTest(label=name):
                label = ns[name]
                self.assertGreater(label.get_bottom()[1], max(axes.get_top()[1], curve.get_top()[1]) + 0.15)
                for stroke in (axes.x_axis, axes.y_axis, curve):
                    self.assert_stroke_clear(label, stroke, padding=0.15)
        for name in names:
            with self.subTest(frame_object=name):
                item = ns[name]
                self.assertGreaterEqual(item.get_left()[0], -self.manim.config.frame_x_radius + 0.49)
                self.assertLessEqual(item.get_right()[0], self.manim.config.frame_x_radius - 0.49)
                self.assertGreaterEqual(item.get_bottom()[1], -self.manim.config.frame_y_radius + 0.49)
                self.assertLessEqual(item.get_top()[1], self.manim.config.frame_y_radius - 0.49)
        # The curve still represents the same equation and fully includes its vertex.
        for x in (-6.8, -3, 0, 0.8):
            self.assertAlmostEqual(curve.underlying_function(x), x*x + 6*x + 2)
        vertex = axes.c2p(-3, -7)
        self.assertAlmostEqual(curve.get_bottom()[1], vertex[1], places=4)

    def test_vertex_notes_stay_clear_of_graph_geometry(self):
        tree = lesson_tree("completer_le_carre")
        ns = self.geometry_namespace(tree)
        method = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef) and node.name == "_scene4_vertex_form")
        selected = []
        for node in method.body:
            if isinstance(node, ast.With):
                if any(isinstance(target, ast.Name) and target.id == "vertex_label"
                       for statement in selected if isinstance(statement, ast.Assign)
                       for target in statement.targets):
                    break
                continue
            selected.append(node)
        self.execute_geometry(selected, ns)
        graph_left = min(ns[name].get_left()[0]
                         for name in ("axes", "base_curve", "shifted_curve"))
        for name in ("h_note", "k_note"):
            note = ns[name]
            self.assertLess(note.get_right()[0], graph_left - 0.2)
            self.assertGreater(note.get_left()[0], -self.manim.config.frame_width / 2 + 0.2)
        self.assertLess(ns["axes"].get_top()[1], ns["general"].get_bottom()[1] - 0.15)
        for label_name in ("base_label", "shifted_label"):
            label = ns[label_name]
            for curve_name in ("base_curve", "shifted_curve"):
                curve = ns[curve_name]
                for alpha in self.manim.np.linspace(0, 1, 1001):
                    point = curve.point_from_proportion(alpha)
                    self.assertFalse(label.get_left()[0] - 0.08 <= point[0] <= label.get_right()[0] + 0.08
                                     and label.get_bottom()[1] - 0.08 <= point[1] <= label.get_top()[1] + 0.08)


if __name__ == "__main__":
    unittest.main()

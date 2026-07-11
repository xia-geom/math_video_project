import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import *

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.azure import AzureService
except ImportError:
    VoiceoverScene = None
    AzureService = None

import tools.tts as tts
from tools.branding import play_uqam_intro


config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

F_SSML = tts.char("f")
G_SSML = tts.char("g")
X_SSML = tts.X


def proportional_axes(x_range, y_range, unit_size=0.6, **kwargs):
    x_span = x_range[1] - x_range[0]
    y_span = y_range[1] - y_range[0]

    return Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_span * unit_size,
        y_length=y_span * unit_size,
        tips=False,
        axis_config={
            "color": BLACK,
            "include_numbers": True,
            "font_size": 22,
        },
        **kwargs,
    )


SCRIPT = {
    "intro": (
        "Aujourd'hui, on veut comprendre ce que signifie composer deux fonctions."
    ),
    "first_function": (
        f"On a d'abord une première fonction, {F_SSML}. "
        f"Elle prend une valeur de départ, que l'on appelle {X_SSML}, "
        f"et elle produit une sortie : {F_SSML} de {X_SSML}."
    ),
    "second_function": (
        f"À droite, on a une deuxième fonction, {G_SSML}. "
        f"Mais cette fois, l'entrée de {G_SSML} ne sera pas directement {X_SSML}. "
        "Ce sera la sortie de la première fonction."
    ),
    "choose_x": (
        f"Choisissons une valeur de {X_SSML} sur le premier axe."
    ),
    "read_f": (
        f"On monte jusqu'au graphe de {F_SSML}. "
        f"La hauteur obtenue est {F_SSML} de {X_SSML}."
    ),
    "transport": (
        f"Maintenant, cette valeur {F_SSML} de {X_SSML} devient une nouvelle entrée. "
        f"On la transporte donc sur l'axe des {X_SSML} du deuxième graphique."
    ),
    "read_g": (
        f"À partir de cette nouvelle entrée, on monte jusqu'au graphe de {G_SSML}."
    ),
    "result": (
        f"La hauteur obtenue est alors {G_SSML} de {F_SSML} de {X_SSML}."
    ),
    "composition": (
        f"C'est cela, la composition : on applique d'abord {F_SSML}, "
        f"puis on applique {G_SSML} au résultat."
    ),
    "formula": (
        f"Autrement dit, {G_SSML} composée avec {F_SSML}, de {X_SSML}, signifie : "
        f"d'abord {F_SSML} de {X_SSML}, ensuite {G_SSML} de {F_SSML} de {X_SSML}."
    ),
    "takeaway": (
        "La chose importante à retenir est que la sortie de la première fonction "
        "devient l'entrée de la deuxième."
    ),
    "numeric_example": (
        "Prenons maintenant un exemple numérique complet. "
        f"On pose {F_SSML} de {X_SSML} égale deux {X_SSML} plus un, "
        f"et {G_SSML} de {X_SSML} égale {X_SSML} au carré. "
        f"Si {X_SSML} vaut deux, alors {F_SSML} de deux vaut cinq. "
        f"Ensuite, {G_SSML} de cinq vaut vingt-cinq."
    ),
    "substitution": (
        "Le même calcul peut se faire avec des formules. "
        f"Dans {G_SSML} composée avec {F_SSML}, on remplace l'entrée de {G_SSML} "
        f"par toute la formule de {F_SSML}. "
        f"Donc {G_SSML} de {F_SSML} de {X_SSML} devient {G_SSML} de deux "
        f"{X_SSML} plus un, c'est-à-dire deux {X_SSML} plus un, au carré."
    ),
    "order_values": (
        "L'ordre est important. "
        f"Si on applique {F_SSML} puis {G_SSML} à partir de deux, "
        "on obtient vingt-cinq. "
        f"Mais si on applique {G_SSML} puis {F_SSML} à partir de deux, "
        "on obtient neuf. Les deux compositions n'ont donc pas forcément "
        "la même valeur."
    ),
    "order_formulas": (
        "On le voit aussi dans les formules. "
        f"{G_SSML} composée avec {F_SSML} donne deux {X_SSML} plus un, au carré. "
        f"{F_SSML} composée avec {G_SSML} donne deux {X_SSML} au carré plus un. "
        "En général, changer l'ordre change la fonction."
    ),
    "product_mistake": (
        "Une erreur fréquente est de croire que le symbole rond veut dire multiplier. "
        "Ce n'est pas le cas. Composer veut dire enchaîner deux fonctions. "
        "Multiplier donnerait une autre opération, avec un autre résultat."
    ),
    "domain_rule": (
        "Enfin, pour que la composition ait un sens, les sorties de la première "
        "fonction doivent être acceptées comme entrées par la deuxième. "
        f"Pour {G_SSML} composée avec {F_SSML}, les valeurs produites par "
        f"{F_SSML} doivent entrer dans le domaine de {G_SSML}."
    ),
    "expanded_takeaway": (
        "À retenir : composer deux fonctions, c'est respecter un ordre, "
        "remplacer une entrée par une sortie, et vérifier que la sortie de la "
        "première fonction peut entrer dans la deuxième."
    ),
}


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class CompositionFonctionsFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    def _setup_voiceover(self):
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")
            return
        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover not installed. Rendering without narration.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print("[voiceover] Missing Azure Speech credentials. Rendering without narration.")
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)
        self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text):
        ssml_text = tts.ssml(text)
        if self._voiceover_enabled:
            with self.voiceover(text=ssml_text, subcaption=tts.strip_ssml(ssml_text)) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_for_narration(self, tracker, animation_time, fallback=0.4):
        if self._voiceover_enabled:
            self.wait(max(tracker.duration - animation_time, 0.2))
        else:
            self.wait(fallback)

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)
        accent = BLUE_D

        def f(x):
            return 0.8 * x + 1.5

        def g(x):
            return 0.25 * (x - 1) ** 2 + 0.8

        title = Text("Composition de fonctions", font_size=42)
        formula = MathTex(r"(g\circ f)(x)=g(f(x))", font_size=40)
        header = VGroup(title, formula).arrange(DOWN, buff=0.12)
        header.to_edge(UP, buff=0.25)

        axes_f = proportional_axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 5, 1],
            unit_size=0.55,
        )

        axes_g = proportional_axes(
            x_range=[-1, 5, 1],
            y_range=[0, 5, 1],
            unit_size=0.55,
        )

        axes_f.shift(LEFT * 3.45 + DOWN * 1.15)
        axes_g.shift(RIGHT * 3.45 + DOWN * 1.15)

        axes_f_labels = axes_f.get_axis_labels(MathTex("x"), MathTex("y"))
        axes_g_labels = axes_g.get_axis_labels(MathTex("x"), MathTex("y"))

        f_graph = axes_f.plot(f, x_range=[-3, 3], color=BLACK, stroke_width=4)
        g_graph = axes_g.plot(g, x_range=[-1, 5], color=BLACK, stroke_width=4)

        f_title = Text("1) On applique f", font_size=26).next_to(axes_f, UP, buff=0.38)
        g_title = Text("2) Puis on applique g", font_size=26).next_to(axes_g, UP, buff=0.38)

        f_label = axes_f.get_graph_label(
            f_graph, label=MathTex("y=f(x)", font_size=30), x_val=2.0, direction=UP
        )
        g_label = axes_g.get_graph_label(
            g_graph, label=MathTex("y=g(x)", font_size=30), x_val=3.6, direction=UR
        )

        x_tracker = ValueTracker(-2.0)

        def x0():
            return x_tracker.get_value()

        def fx():
            return f(x0())

        def gfx():
            return g(fx())

        left_x_pt = always_redraw(
            lambda: Dot(axes_f.c2p(x0(), 0), color=accent, radius=0.06)
        )

        left_graph_pt = always_redraw(
            lambda: Dot(axes_f.c2p(x0(), fx()), color=accent, radius=0.06)
        )

        left_vline = always_redraw(
            lambda: DashedLine(
                axes_f.c2p(x0(), 0),
                axes_f.c2p(x0(), fx()),
                color=GRAY,
                dash_length=0.08,
            )
        )

        left_hline = always_redraw(
            lambda: DashedLine(
                axes_f.c2p(0, fx()),
                axes_f.c2p(x0(), fx()),
                color=GRAY,
                dash_length=0.08,
            )
        )

        transfer_arrow = always_redraw(
            lambda: Arrow(
                axes_f.c2p(0, fx()),
                axes_g.c2p(fx(), 0),
                buff=0.08,
                stroke_width=3,
                color=accent,
                max_tip_length_to_length_ratio=0.12,
            )
        )

        right_x_pt = always_redraw(
            lambda: Dot(axes_g.c2p(fx(), 0), color=accent, radius=0.06)
        )

        right_graph_pt = always_redraw(
            lambda: Dot(axes_g.c2p(fx(), gfx()), color=accent, radius=0.06)
        )

        right_vline = always_redraw(
            lambda: DashedLine(
                axes_g.c2p(fx(), 0),
                axes_g.c2p(fx(), gfx()),
                color=GRAY,
                dash_length=0.08,
            )
        )

        right_hline = always_redraw(
            lambda: DashedLine(
                axes_g.c2p(0, gfx()),
                axes_g.c2p(fx(), gfx()),
                color=GRAY,
                dash_length=0.08,
            )
        )

        x_label = always_redraw(
            lambda: DecimalNumber(x0(), num_decimal_places=2, color=accent)
            .scale(0.55)
            .next_to(axes_f.c2p(x0(), 0), DOWN, buff=0.1)
        )

        fx_left_label = always_redraw(
            lambda: DecimalNumber(fx(), num_decimal_places=2, color=accent)
            .scale(0.55)
            .next_to(axes_f.c2p(0, fx()), LEFT, buff=0.1)
        )

        fx_right_label = always_redraw(
            lambda: DecimalNumber(fx(), num_decimal_places=2, color=accent)
            .scale(0.55)
            .next_to(axes_g.c2p(fx(), 0), DOWN, buff=0.1)
        )

        gfx_label = always_redraw(
            lambda: DecimalNumber(gfx(), num_decimal_places=2, color=accent)
            .scale(0.55)
            .next_to(axes_g.c2p(0, gfx()), LEFT, buff=0.1)
        )

        top_chain = always_redraw(
            lambda: VGroup(
                MathTex("x=", font_size=32),
                DecimalNumber(x0(), num_decimal_places=2, color=accent).scale(0.72),
                MathTex(r"\Longrightarrow", font_size=32),
                MathTex("f(x)=", font_size=32),
                DecimalNumber(fx(), num_decimal_places=2, color=accent).scale(0.72),
                MathTex(r"\Longrightarrow", font_size=32),
                MathTex("g(f(x))=", font_size=32),
                DecimalNumber(gfx(), num_decimal_places=2, color=accent).scale(0.72),
            )
            .arrange(RIGHT, buff=0.12)
            .next_to(header, DOWN, buff=0.2)
        )

        comment = Text(
            "On lit d'abord la sortie de f, puis on l'utilise comme entrée de g.",
            font_size=24,
        ).to_edge(DOWN, buff=0.35)

        with self.narrated(SCRIPT["intro"]) as tracker:
            self.play(FadeIn(header), run_time=1.2)
            self.wait_for_narration(tracker, 1.2)

        with self.narrated(SCRIPT["first_function"]) as tracker:
            self.play(
                Create(axes_f),
                FadeIn(axes_f_labels),
                FadeIn(f_title),
                run_time=1.5,
            )
            self.play(Create(f_graph), FadeIn(f_label), run_time=1.4)
            self.wait_for_narration(tracker, 2.9)

        with self.narrated(SCRIPT["second_function"]) as tracker:
            self.play(
                Create(axes_g),
                FadeIn(axes_g_labels),
                FadeIn(g_title),
                run_time=1.5,
            )
            self.play(Create(g_graph), FadeIn(g_label), run_time=1.4)
            self.wait_for_narration(tracker, 2.9)

        with self.narrated(SCRIPT["choose_x"]) as tracker:
            self.play(FadeIn(top_chain), FadeIn(comment), run_time=0.9)
            self.play(FadeIn(left_x_pt), FadeIn(x_label), run_time=0.9)
            self.wait_for_narration(tracker, 1.8)

        with self.narrated(SCRIPT["read_f"]) as tracker:
            self.play(
                Create(left_vline),
                Create(left_hline),
                FadeIn(left_graph_pt),
                FadeIn(fx_left_label),
                run_time=2.0,
            )
            self.wait_for_narration(tracker, 2.0)

        with self.narrated(SCRIPT["transport"]) as tracker:
            self.play(
                Create(transfer_arrow),
                FadeIn(fx_right_label),
                FadeIn(right_x_pt),
                run_time=2.2,
            )
            self.wait_for_narration(tracker, 2.2)

        with self.narrated(SCRIPT["read_g"]) as tracker:
            self.play(
                Create(right_vline),
                Create(right_hline),
                FadeIn(right_graph_pt),
                run_time=2.0,
            )
            self.wait_for_narration(tracker, 2.0)

        with self.narrated(SCRIPT["result"]) as tracker:
            self.play(FadeIn(gfx_label), Indicate(gfx_label), run_time=1.6)
            self.wait_for_narration(tracker, 1.6)

        with self.narrated(SCRIPT["composition"]) as tracker:
            for new_x in [1.2, -0.5, 2.4]:
                self.play(x_tracker.animate.set_value(new_x), run_time=2.0)
            self.wait_for_narration(tracker, 6.0)

        with self.narrated(SCRIPT["formula"]) as tracker:
            self.play(Circumscribe(formula, color=accent), run_time=1.4)
            self.play(Circumscribe(top_chain, color=accent), run_time=1.4)
            self.wait_for_narration(tracker, 2.8)

        final_comment = Text(
            "La sortie de f devient l'entrée de g.",
            font_size=30,
            color=accent,
        ).to_edge(DOWN, buff=0.35)
        with self.narrated(SCRIPT["takeaway"]) as tracker:
            self.play(Transform(comment, final_comment), run_time=1.0)
            self.play(Indicate(transfer_arrow), run_time=1.4)
            self.wait_for_narration(tracker, 2.4)

        graph_scene = VGroup(
            axes_f,
            axes_f_labels,
            axes_g,
            axes_g_labels,
            f_title,
            g_title,
            f_graph,
            g_graph,
            f_label,
            g_label,
            left_x_pt,
            left_graph_pt,
            left_vline,
            left_hline,
            transfer_arrow,
            right_x_pt,
            right_graph_pt,
            right_vline,
            right_hline,
            x_label,
            fx_left_label,
            fx_right_label,
            gfx_label,
            top_chain,
            comment,
        )

        warning_color = RED_D
        success_color = GREEN_D

        def value_node(label, color=accent):
            circle = Circle(radius=0.32, stroke_color=color, stroke_width=3)
            circle.set_fill(WHITE, opacity=1)
            tex = MathTex(label, font_size=34, color=color)
            tex.move_to(circle)
            return VGroup(circle, tex)

        def function_box(label, color=BLACK):
            box = Rectangle(width=0.95, height=0.62, stroke_color=color, stroke_width=2)
            tex = MathTex(label, font_size=34, color=color)
            tex.move_to(box)
            return VGroup(box, tex)

        def arrow_between(left, right, color=accent):
            return Arrow(
                left.get_right(),
                right.get_left(),
                buff=0.1,
                stroke_width=3,
                color=color,
                max_tip_length_to_length_ratio=0.18,
            )

        def machine_lane(title_tex, value_labels, function_labels, color=accent):
            lane_title = MathTex(title_tex, font_size=34, color=color)
            items = VGroup(
                value_node(value_labels[0], color),
                function_box(function_labels[0]),
                value_node(value_labels[1], color),
                function_box(function_labels[1]),
                value_node(value_labels[2], color),
            ).arrange(RIGHT, buff=0.35)
            arrows = VGroup(
                arrow_between(items[0], items[1], color),
                arrow_between(items[1], items[2], color),
                arrow_between(items[2], items[3], color),
                arrow_between(items[3], items[4], color),
            )
            return VGroup(lane_title, VGroup(items, arrows)).arrange(DOWN, buff=0.25)

        def formula_panel(title_text, lines, color=accent):
            title_mob = Text(title_text, font_size=26, color=color)
            formula_lines = VGroup(
                *[MathTex(line, font_size=32) for line in lines]
            ).arrange(DOWN, buff=0.18)
            content = VGroup(title_mob, formula_lines).arrange(DOWN, buff=0.25)
            frame = SurroundingRectangle(content, color=color, buff=0.18)
            return VGroup(frame, content)

        example_title = Text("Exemple numérique", font_size=34)
        example_defs = VGroup(
            MathTex(r"f(x)=2x+1", font_size=34),
            MathTex(r"g(x)=x^2", font_size=34),
            MathTex(r"x=2", font_size=34, color=accent),
        ).arrange(RIGHT, buff=0.55)
        example_lane = machine_lane(
            r"(g\circ f)(2)",
            [r"2", r"5", r"25"],
            [r"f", r"g"],
            accent,
        )
        example_result = MathTex(r"(g\circ f)(2)=25", font_size=40, color=accent)
        example_group = VGroup(
            example_title,
            example_defs,
            example_lane,
            example_result,
        ).arrange(DOWN, buff=0.35)
        example_group.next_to(header, DOWN, buff=0.45)

        with self.narrated(SCRIPT["numeric_example"]) as tracker:
            self.play(FadeOut(graph_scene), run_time=0.8)
            self.play(FadeIn(example_title), Write(example_defs), run_time=1.2)
            self.play(FadeIn(example_lane), run_time=1.5)
            self.play(Write(example_result), run_time=0.9)
            self.wait_for_narration(tracker, 4.4)

        algebra_title = Text("Substitution dans la formule", font_size=34)
        algebra_defs = MathTex(
            r"f(x)=2x+1",
            r"\qquad",
            r"g(x)=x^2",
            font_size=34,
        )
        algebra_steps = VGroup(
            MathTex(r"(g\circ f)(x)=g(f(x))", font_size=38),
            MathTex(r"=g(2x+1)", font_size=38),
            MathTex(r"=(2x+1)^2", font_size=38, color=accent),
        ).arrange(DOWN, buff=0.26)
        algebra_group = VGroup(algebra_title, algebra_defs, algebra_steps).arrange(
            DOWN, buff=0.38
        )
        algebra_group.next_to(header, DOWN, buff=0.55)

        with self.narrated(SCRIPT["substitution"]) as tracker:
            self.play(FadeOut(example_group), run_time=0.8)
            self.play(FadeIn(algebra_title), Write(algebra_defs), run_time=1.1)
            for step in algebra_steps:
                self.play(Write(step), run_time=0.8)
            self.play(Circumscribe(algebra_steps[-1], color=accent), run_time=1.0)
            self.wait_for_narration(tracker, 4.5)

        order_title = Text("L'ordre change le résultat", font_size=34)
        order_forward_lane = machine_lane(
            r"g\circ f",
            [r"2", r"5", r"25"],
            [r"f", r"g"],
            accent,
        )
        order_reverse_lane = machine_lane(
            r"f\circ g",
            [r"2", r"4", r"9"],
            [r"g", r"f"],
            success_color,
        )
        order_result = MathTex(r"25\neq 9", font_size=44, color=warning_color)
        order_group = VGroup(
            order_title,
            order_forward_lane,
            order_reverse_lane,
            order_result,
        ).arrange(DOWN, buff=0.22)
        order_group.next_to(header, DOWN, buff=0.35)

        with self.narrated(SCRIPT["order_values"]) as tracker:
            self.play(FadeOut(algebra_group), run_time=0.8)
            self.play(FadeIn(order_title), run_time=0.6)
            self.play(FadeIn(order_forward_lane), run_time=1.2)
            self.play(FadeIn(order_reverse_lane), run_time=1.2)
            self.play(Write(order_result), run_time=0.8)
            self.wait_for_narration(tracker, 3.8)

        compare_title = Text("Comparer les deux compositions", font_size=34)
        gof_panel = formula_panel(
            "f puis g",
            [
                r"(g\circ f)(x)=g(f(x))",
                r"=g(2x+1)",
                r"=(2x+1)^2",
            ],
            accent,
        )
        fog_panel = formula_panel(
            "g puis f",
            [
                r"(f\circ g)(x)=f(g(x))",
                r"=f(x^2)",
                r"=2x^2+1",
            ],
            success_color,
        )
        formula_compare = VGroup(gof_panel, fog_panel).arrange(RIGHT, buff=0.55)
        if formula_compare.width > 11:
            formula_compare.scale_to_fit_width(11)
        formula_not_equal = MathTex(
            r"g\circ f\neq f\circ g\quad\text{en general}",
            font_size=38,
            color=warning_color,
        )
        formula_compare_group = VGroup(
            compare_title,
            formula_compare,
            formula_not_equal,
        ).arrange(DOWN, buff=0.35)
        formula_compare_group.next_to(header, DOWN, buff=0.45)

        with self.narrated(SCRIPT["order_formulas"]) as tracker:
            self.play(FadeOut(order_group), run_time=0.8)
            self.play(FadeIn(compare_title), run_time=0.6)
            self.play(FadeIn(gof_panel), FadeIn(fog_panel), run_time=1.3)
            self.play(Write(formula_not_equal), run_time=0.9)
            self.wait_for_narration(tracker, 3.6)

        mistake_title = Text("Erreur fréquente", font_size=34)
        composition_panel = formula_panel(
            "Composition",
            [
                r"(g\circ f)(2)=25",
                r"\text{on enchaine } f \text{ puis } g",
            ],
            accent,
        )
        product_panel = formula_panel(
            "Produit",
            [
                r"(g\cdot f)(2)=g(2)f(2)",
                r"=4\cdot 5=20",
            ],
            warning_color,
        )
        mistake_panels = VGroup(composition_panel, product_panel).arrange(
            RIGHT, buff=0.55
        )
        if mistake_panels.width > 11:
            mistake_panels.scale_to_fit_width(11)
        mistake_not_equal = MathTex(
            r"g\circ f\neq g\cdot f",
            font_size=42,
            color=warning_color,
        )
        mistake_group = VGroup(
            mistake_title,
            mistake_panels,
            mistake_not_equal,
        ).arrange(DOWN, buff=0.35)
        mistake_group.next_to(header, DOWN, buff=0.45)

        with self.narrated(SCRIPT["product_mistake"]) as tracker:
            self.play(FadeOut(formula_compare_group), run_time=0.8)
            self.play(FadeIn(mistake_title), run_time=0.6)
            self.play(FadeIn(composition_panel), FadeIn(product_panel), run_time=1.3)
            self.play(Write(mistake_not_equal), run_time=0.9)
            self.wait_for_narration(tracker, 3.6)

        def set_node(name, detail, color):
            ellipse = Ellipse(
                width=2.35,
                height=1.35,
                stroke_color=color,
                stroke_width=3,
            )
            ellipse.set_fill(WHITE, opacity=1)
            label = VGroup(
                MathTex(name, font_size=34, color=color),
                Text(detail, font_size=21),
            ).arrange(DOWN, buff=0.06)
            label.move_to(ellipse)
            return VGroup(ellipse, label)

        domain_title = Text("Quand la composition est-elle possible ?", font_size=34)
        set_a = set_node("A", "entrées de f", BLACK)
        set_b = set_node("B", "sorties de f", accent)
        set_c = set_node("C", "sorties de g", success_color)
        domain_sets = VGroup(set_a, set_b, set_c).arrange(RIGHT, buff=1.0)
        domain_arrows = VGroup(
            arrow_between(set_a, set_b, accent),
            arrow_between(set_b, set_c, success_color),
        )
        domain_arrow_labels = VGroup(
            MathTex("f", font_size=32, color=accent).next_to(domain_arrows[0], UP, buff=0.08),
            MathTex("g", font_size=32, color=success_color).next_to(
                domain_arrows[1], UP, buff=0.08
            ),
        )
        domain_rule = Text(
            "Les sorties de f doivent pouvoir entrer dans g.",
            font_size=30,
            color=accent,
        )
        domain_group = VGroup(
            domain_title,
            VGroup(domain_sets, domain_arrows, domain_arrow_labels),
            domain_rule,
        ).arrange(DOWN, buff=0.45)
        domain_group.next_to(header, DOWN, buff=0.55)

        with self.narrated(SCRIPT["domain_rule"]) as tracker:
            self.play(FadeOut(mistake_group), run_time=0.8)
            self.play(FadeIn(domain_title), run_time=0.6)
            self.play(FadeIn(domain_sets), run_time=1.0)
            self.play(Create(domain_arrows), FadeIn(domain_arrow_labels), run_time=1.1)
            self.play(FadeIn(domain_rule), run_time=0.8)
            self.wait_for_narration(tracker, 3.5)

        closing = VGroup(
            Text("À retenir", font_size=34, color=accent),
            MathTex(
                r"x\xrightarrow{\ f\ }f(x)\xrightarrow{\ g\ }g(f(x))",
                font_size=42,
            ),
            Text("Ordre, substitution, entrée permise.", font_size=28),
        ).arrange(DOWN, buff=0.35)
        closing.next_to(header, DOWN, buff=0.75)

        with self.narrated(SCRIPT["expanded_takeaway"]) as tracker:
            self.play(FadeOut(domain_group), FadeIn(closing), run_time=1.2)
            self.play(Circumscribe(closing[1], color=accent), run_time=1.2)
            self.wait_for_narration(tracker, 2.4)

        self.wait(1)

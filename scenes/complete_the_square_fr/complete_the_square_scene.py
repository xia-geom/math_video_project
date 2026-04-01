from manim import *
import numpy as np
import os
from contextlib import contextmanager
from dataclasses import dataclass

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

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

from tools.tts import ssml, ET

# This scene paces via global_speed on AzureService; no prosody rate needed.
fr_ca = lambda body: ssml(body, "0%")

BLUE_D_CUSTOM = "#1565C0"
ORANGE_CUSTOM = "#E65100"
GREEN_CUSTOM = "#2E7D32"
RED_CUSTOM = "#C62828"
GRAY_CUSTOM = "#757575"


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class CompleteTheSquare(VoiceoverScene if VoiceoverScene is not None else Scene):

    # ------------------------------------------------------------------
    # Boilerplate: pacing + voiceover (same pattern as other scenes)
    # ------------------------------------------------------------------
    def _setup_pacing(self):
        try:
            self.pace_factor = max(float(os.getenv("PACE_FACTOR", "1.2")), 0.1)
        except ValueError:
            self.pace_factor = 1.2

    def _paced_time(self, s: float) -> float:
        return s * self.pace_factor

    def play_paced(self, *args, run_time: float | None = None, **kwargs):
        if run_time is not None:
            kwargs["run_time"] = self._paced_time(run_time)
        self.play(*args, **kwargs)

    def wait_paced(self, s: float):
        self.wait(self._paced_time(s))

    def _setup_voiceover(self):
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover not installed — rendering without narration.")
            return
        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print("[voiceover] Missing Azure credentials — rendering without narration.")
            return
        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)
        self.set_speech_service(
            AzureService(voice="fr-CA-SylvieNeural", global_speed=1.0 / self.pace_factor)
        )
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str):
        if self._voiceover_enabled:
            with self.voiceover(text=fr_ca(text)) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    # ------------------------------------------------------------------
    def construct(self):
        self.camera.background_color = WHITE
        self._setup_pacing()
        self._setup_voiceover()

        self._scene1_hook()
        self._scene2_geometry()
        self._scene3_algebra()
        self._scene4_vertex_form()
        self._scene5_quadratic_formula()

    # ==================================================================
    # SCÈNE 1 — Accroche : la forme standard cache tout
    # ==================================================================
    def _scene1_hook(self):
        title = Text("Compléter le carré", font_size=52).to_edge(UP, buff=0.7)
        subtitle = Text("Pourquoi ça marche vraiment", font_size=32, color=GRAY_CUSTOM).next_to(title, DOWN, buff=0.25)

        with self.narrated(
            "Compléter le carré. On vous l'a probablement montré comme une procédure algébrique. "
            "Mais il y a une idée géométrique derrière, et c'est elle qui rend tout évident."
        ) as _:
            self.play_paced(FadeIn(title, shift=0.2 * DOWN), FadeIn(subtitle, shift=0.2 * DOWN), run_time=1.5)
            self.wait_paced(1.5)

        # Show standard form — looks opaque
        eq_standard = MathTex(r"f(x) = x^2 + 6x + 2", font_size=56).shift(UP * 0.5)
        question = Text("Où est le sommet ? Où sont les racines ?", font_size=30, color=GRAY_CUSTOM).next_to(eq_standard, DOWN, buff=0.5)

        with self.narrated(
            "Prenons f de x égal x carré plus six x plus deux. "
            "En forme standard, impossible de voir où est le sommet, ni où la courbe coupe l'axe des x."
        ) as _:
            self.play_paced(FadeOut(title), FadeOut(subtitle), run_time=0.6)
            self.play_paced(Write(eq_standard), run_time=1.5)
            self.play_paced(FadeIn(question), run_time=0.8)
            self.wait_paced(1.2)

        # Draw the parabola quickly to show the shape exists
        axes = Axes(
            x_range=[-7, 2, 1], y_range=[-8, 10, 2],
            x_length=7, y_length=5,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 1.5},
        ).to_edge(DOWN, buff=0.5)
        parabola = axes.plot(lambda x: x**2 + 6*x + 2, x_range=[-6.8, 0.8], color=BLUE, stroke_width=3)

        with self.narrated(
            "La courbe existe, elle a un sommet, elle a des racines. "
            "Mais la forme standard ne nous le dit pas directement. "
            "Il faut transformer l'expression — et c'est là qu'intervient l'idée géométrique."
        ) as _:
            self.play_paced(Create(axes), run_time=1.0)
            self.play_paced(Create(parabola), run_time=1.8)
            self.wait_paced(1.5)

        self.play_paced(FadeOut(VGroup(eq_standard, question, axes, parabola)), run_time=1.0)

    # ==================================================================
    # SCÈNE 2 — Détour géométrique : l'aire et le coin manquant
    # ==================================================================
    def _scene2_geometry(self):
        geo_title = Text("L'idée géométrique", font_size=40).to_edge(UP, buff=0.5)

        with self.narrated("Voici l'idée géométrique. On va construire des formes.") as _:
            self.play_paced(FadeIn(geo_title), run_time=0.8)

        # --- Big square x² ---
        sq_size = 2.6
        sq = Square(side_length=sq_size, color=BLUE, fill_color=BLUE, fill_opacity=0.25, stroke_width=3)
        sq.move_to(LEFT * 2.8 + DOWN * 0.3)
        sq_label = MathTex(r"x^2", font_size=40, color=BLUE).move_to(sq.get_center())
        side_label_x1 = MathTex(r"x", font_size=32, color=BLUE).next_to(sq, DOWN, buff=0.15)
        side_label_x2 = MathTex(r"x", font_size=32, color=BLUE).next_to(sq, LEFT, buff=0.15)

        with self.narrated(
            "x carré, c'est un carré de côté x. Sa surface est x carré."
        ) as _:
            self.play_paced(DrawBorderThenFill(sq), run_time=1.2)
            self.play_paced(Write(sq_label), Write(side_label_x1), Write(side_label_x2), run_time=0.8)
            self.wait_paced(0.8)

        # --- Rectangle bx = 6x, split into two halves of 3x ---
        b = 6
        half_b = b / 2  # 3
        rect_h = sq_size          # height matches x
        rect_w = sq_size * (half_b / b) * 1.5   # visual width for b/2 strip

        rect_right = Rectangle(
            width=rect_w, height=rect_h,
            color=ORANGE_CUSTOM, fill_color=ORANGE_CUSTOM, fill_opacity=0.25, stroke_width=3,
        ).next_to(sq, RIGHT, buff=0)

        rect_bottom = Rectangle(
            width=rect_h, height=rect_w,
            color=ORANGE_CUSTOM, fill_color=ORANGE_CUSTOM, fill_opacity=0.25, stroke_width=3,
        ).next_to(sq, DOWN, buff=0)

        rect_right_label = MathTex(r"3x", font_size=32, color=ORANGE_CUSTOM).move_to(rect_right.get_center())
        rect_bottom_label = MathTex(r"3x", font_size=32, color=ORANGE_CUSTOM).move_to(rect_bottom.get_center())
        side_3_r = MathTex(r"3", font_size=28, color=ORANGE_CUSTOM).next_to(rect_right, UP, buff=0.12)
        side_3_b = MathTex(r"3", font_size=28, color=ORANGE_CUSTOM).next_to(rect_bottom, RIGHT, buff=0.12)

        with self.narrated(
            "Maintenant, six x, c'est un rectangle de côtés six et x. "
            "On le coupe en deux rectangles de côtés trois et x, "
            "et on en place un à droite du carré, un en dessous."
        ) as _:
            self.play_paced(DrawBorderThenFill(rect_right), run_time=0.9)
            self.play_paced(Write(rect_right_label), Write(side_3_r), run_time=0.5)
            self.play_paced(DrawBorderThenFill(rect_bottom), run_time=0.9)
            self.play_paced(Write(rect_bottom_label), Write(side_3_b), run_time=0.5)
            self.wait_paced(0.8)

        # Brace showing total expression so far
        l_shape_group = VGroup(sq, rect_right, rect_bottom)
        area_note = MathTex(r"x^2 + 6x", font_size=38).to_edge(RIGHT, buff=0.8).shift(UP * 0.5)
        area_note_label = Text("Aire totale :", font_size=26, color=GRAY_CUSTOM).next_to(area_note, UP, buff=0.1)

        with self.narrated(
            "La surface totale de cette forme en L, c'est x carré plus six x."
        ) as _:
            self.play_paced(FadeIn(area_note_label), Write(area_note), run_time=0.9)
            self.wait_paced(0.8)

        # --- The missing corner (bottom-right of sq, aligned with rect_right) ---
        corner = Square(
            side_length=rect_w,
            color=GREEN_CUSTOM, fill_color=GREEN_CUSTOM, fill_opacity=0.35, stroke_width=3,
        ).next_to(sq, DOWN, buff=0).align_to(rect_right, LEFT)

        corner_label = MathTex(r"3^2 = 9", font_size=30, color=GREEN_CUSTOM).move_to(corner.get_center())
        corner_q = MathTex(r"?", font_size=48, color=RED_CUSTOM).move_to(corner.get_center())

        with self.narrated(
            "Il manque un coin ! Un petit carré de côté trois, dans le coin en bas à droite. "
            "Si on le rajoute, la forme entière devient un grand carré parfait."
        ) as _:
            self.play_paced(FadeIn(corner_q, scale=0.5), run_time=0.6)
            self.play_paced(corner_q.animate.scale(1.3), rate_func=there_and_back, run_time=0.7)
            self.play_paced(DrawBorderThenFill(corner), FadeOut(corner_q), run_time=1.0)
            self.play_paced(Write(corner_label), run_time=0.6)
            self.wait_paced(0.6)

        # Show the completed big square with side (x+3)
        big_sq_side = sq_size + rect_w
        big_sq_outline = Square(
            side_length=big_sq_side,
            color=BLACK, stroke_width=3, fill_opacity=0,
        ).align_to(sq, UL)
        big_side_label = MathTex(r"x + 3", font_size=32).next_to(big_sq_outline, DOWN, buff=0.2)
        big_side_label2 = MathTex(r"x + 3", font_size=32).next_to(big_sq_outline, LEFT, buff=0.2)

        completed_eq = MathTex(
            r"x^2 + 6x + 9 = (x+3)^2",
            font_size=40, color=GREEN_CUSTOM,
        ).to_edge(RIGHT, buff=0.6).shift(DOWN * 0.5)

        with self.narrated(
            "Le grand carré a pour côté x plus trois, donc son aire est x plus trois, le tout au carré. "
            "On vient de compléter le carré — littéralement."
        ) as _:
            self.play_paced(Create(big_sq_outline), run_time=0.8)
            self.play_paced(Write(big_side_label), Write(big_side_label2), run_time=0.7)
            self.play_paced(Write(completed_eq), run_time=1.2)
            self.wait_paced(1.5)

        geo_group = VGroup(
            geo_title, sq, sq_label, side_label_x1, side_label_x2,
            rect_right, rect_right_label, side_3_r,
            rect_bottom, rect_bottom_label, side_3_b,
            corner, corner_label,
            big_sq_outline, big_side_label, big_side_label2,
            area_note, area_note_label, completed_eq,
        )
        self.play_paced(FadeOut(geo_group), run_time=1.2)

    # ==================================================================
    # SCÈNE 3 — Traduction algébrique
    # ==================================================================
    def _scene3_algebra(self):
        alg_title = Text("Traduction algébrique", font_size=40).to_edge(UP, buff=0.5)

        with self.narrated("Maintenant, traduisons ce geste géométrique en algèbre.") as _:
            self.play_paced(FadeIn(alg_title), run_time=0.7)

        # Step by step: x² + 6x + 2
        step0 = MathTex(r"x^2 + 6x + 2", font_size=52).shift(UP * 2.2)

        with self.narrated("On part de x carré plus six x plus deux.") as _:
            self.play_paced(Write(step0), run_time=1.2)
            self.wait_paced(0.6)

        # Add and subtract (b/2)² = 9
        step1 = MathTex(
            r"= x^2 + 6x + ",
            r"9",
            r" - ",
            r"9",
            r" + 2",
            font_size=52,
        ).next_to(step0, DOWN, buff=0.5)
        step1[1].set_color(GREEN_CUSTOM)
        step1[3].set_color(RED_CUSTOM)

        add_note = Text("On ajoute le coin manquant…", font_size=26, color=GREEN_CUSTOM).to_edge(LEFT, buff=0.7).shift(DOWN * 0.2)
        sub_note = Text("…et on le retire aussitôt.", font_size=26, color=RED_CUSTOM).next_to(add_note, DOWN, buff=0.1, aligned_edge=LEFT)

        with self.narrated(
            "On ajoute neuf — le coin manquant — et on le soustrait aussitôt. "
            "La valeur de l'expression ne change pas."
        ) as _:
            self.play_paced(Write(step1), run_time=1.4)
            self.play_paced(FadeIn(add_note), FadeIn(sub_note), run_time=0.8)
            self.wait_paced(1.0)

        # Group the perfect square trinomial
        step2 = MathTex(
            r"= \underbrace{x^2 + 6x + 9}_{(x+3)^2}",
            r" - 7",
            font_size=48,
        ).next_to(step1, DOWN, buff=0.5)
        step2[0].set_color(GREEN_CUSTOM)

        with self.narrated(
            "Les trois premiers termes forment un trinôme carré parfait : x plus trois, le tout au carré. "
            "Le reste, c'est neuf moins neuf plus deux, soit moins sept."
        ) as _:
            self.play_paced(FadeOut(add_note), FadeOut(sub_note), run_time=0.5)
            self.play_paced(Write(step2), run_time=1.5)
            self.wait_paced(0.8)

        # Final vertex form
        step3 = MathTex(
            r"f(x) = (x + 3)^2 - 7",
            font_size=56,
        ).next_to(step2, DOWN, buff=0.6)
        box = SurroundingRectangle(step3, color=BLUE, buff=0.18, stroke_width=3)

        with self.narrated(
            "Et voilà la forme vertex : x plus trois, le tout au carré, moins sept. "
            "C'est la même fonction — réécrite pour révéler sa structure."
        ) as _:
            self.play_paced(Write(step3), run_time=1.3)
            self.play_paced(Create(box), run_time=0.8)
            self.wait_paced(1.5)

        alg_group = VGroup(alg_title, step0, step1, step2, step3, box)
        self.play_paced(FadeOut(alg_group), run_time=1.0)

    # ==================================================================
    # SCÈNE 4 — Forme vertex : la parabole est x² déguisé
    # ==================================================================
    def _scene4_vertex_form(self):
        vf_title = Text("La forme vertex", font_size=40).to_edge(UP, buff=0.5)

        with self.narrated(
            "La forme vertex révèle que toute parabole est simplement x carré, déplacé."
        ) as _:
            self.play_paced(FadeIn(vf_title), run_time=0.7)

        # Show general vertex form
        general = MathTex(r"f(x) = a(x - h)^2 + k", font_size=50).shift(UP * 2.5)
        h_note = MathTex(r"h = -3 \text{ : décalage horizontal}", font_size=30, color=ORANGE_CUSTOM).shift(UP * 1.3)
        k_note = MathTex(r"k = -7 \text{ : décalage vertical (sommet)}", font_size=30, color=GREEN_CUSTOM).next_to(h_note, DOWN, buff=0.2)

        with self.narrated(
            "La forme générale est a fois x moins h, au carré, plus k. "
            "h est le décalage horizontal du sommet, k est sa hauteur."
        ) as _:
            self.play_paced(Write(general), run_time=1.2)
            self.play_paced(FadeIn(h_note), FadeIn(k_note), run_time=0.9)
            self.wait_paced(0.8)

        # Draw axes + two curves: x² and (x+3)²-7
        axes = Axes(
            x_range=[-7.5, 2.5, 1], y_range=[-8, 12, 2],
            x_length=7, y_length=5.5,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 1.5},
        ).to_edge(DOWN, buff=0.3)

        base_curve = axes.plot(lambda x: x**2, x_range=[-3.2, 3.2], color=GRAY_CUSTOM, stroke_width=2.5)
        base_label = MathTex(r"x^2", font_size=26, color=GRAY_CUSTOM).next_to(axes.c2p(2.5, 6.25), UR, buff=0.1)

        shifted_curve = axes.plot(lambda x: (x+3)**2 - 7, x_range=[-6.8, 0.8], color=BLUE, stroke_width=3)
        shifted_label = MathTex(r"(x+3)^2-7", font_size=26, color=BLUE).next_to(axes.c2p(0.5, 0.5), UR, buff=0.1)

        vertex_dot = Dot(axes.c2p(-3, -7), color=RED_CUSTOM, radius=0.1)
        vertex_label = MathTex(r"(-3,\,-7)", font_size=26, color=RED_CUSTOM).next_to(vertex_dot, DR, buff=0.1)

        with self.narrated(
            "Voici x carré en gris. Notre parabole en bleu est exactement la même forme, "
            "déplacée trois unités à gauche et sept unités vers le bas. "
            "Le sommet est au point moins trois, moins sept."
        ) as _:
            self.play_paced(Create(axes), run_time=0.9)
            self.play_paced(Create(base_curve), Write(base_label), run_time=1.2)
            self.play_paced(Create(shifted_curve), Write(shifted_label), run_time=1.5)
            self.play_paced(FadeIn(vertex_dot), Write(vertex_label), run_time=0.7)
            self.wait_paced(1.2)

        vf_group = VGroup(vf_title, general, h_note, k_note, axes, base_curve, base_label,
                          shifted_curve, shifted_label, vertex_dot, vertex_label)
        self.play_paced(FadeOut(vf_group), run_time=1.0)

    # ==================================================================
    # SCÈNE 5 — La formule quadratique comme corollaire
    # ==================================================================
    def _scene5_quadratic_formula(self):
        qf_title = Text("La formule quadratique — sans magie", font_size=38).to_edge(UP, buff=0.5)

        with self.narrated(
            "Enfin, la formule quadratique. On ne la mémorise plus — on la retrouve."
        ) as _:
            self.play_paced(FadeIn(qf_title), run_time=0.7)

        # Start from general vertex form set to zero
        eq0 = MathTex(r"ax^2 + bx + c = 0", font_size=46).shift(UP * 2.8)

        with self.narrated("On part de ax carré plus bx plus c égal zéro.") as _:
            self.play_paced(Write(eq0), run_time=1.0)

        # Complete the square on ax² + bx + c
        steps = [
            MathTex(r"a\!\left(x^2 + \tfrac{b}{a}x\right) + c = 0", font_size=44),
            MathTex(r"a\!\left(x + \tfrac{b}{2a}\right)^{\!2} - \tfrac{b^2}{4a} + c = 0", font_size=44),
            MathTex(r"a\!\left(x + \tfrac{b}{2a}\right)^{\!2} = \tfrac{b^2}{4a} - c", font_size=44),
            MathTex(r"\left(x + \tfrac{b}{2a}\right)^{\!2} = \tfrac{b^2 - 4ac}{4a^2}", font_size=44),
            MathTex(r"x + \tfrac{b}{2a} = \pm\,\tfrac{\sqrt{b^2 - 4ac}}{2a}", font_size=44),
            MathTex(r"x = \dfrac{-b \pm \sqrt{b^2 - 4ac}}{2a}", font_size=52, color=BLUE),
        ]
        narrations = [
            "On factorise a.",
            "On complète le carré à l'intérieur des parenthèses — le coin manquant est b sur deux a, au carré.",
            "On isole le carré parfait d'un côté.",
            "On divise par a.",
            "On prend la racine carrée des deux côtés — attention au plus ou moins.",
            "Et voilà la formule quadratique. Elle n'est pas magique — c'est juste compléter le carré, dans le cas général.",
        ]

        prev = eq0
        step_objs = []
        for step_tex, narr in zip(steps[:-1], narrations[:-1]):
            step_tex.next_to(prev, DOWN, buff=0.45)
            with self.narrated(narr) as _:
                self.play_paced(Write(step_tex), run_time=1.1)
                self.wait_paced(0.5)
            prev = step_tex
            step_objs.append(step_tex)

        # Fade out all intermediate steps, then show final formula centered
        intermediate = VGroup(qf_title, eq0, *step_objs)
        self.play_paced(FadeOut(intermediate), run_time=0.8)

        final = steps[-1].move_to(ORIGIN)
        box = SurroundingRectangle(final, color=BLUE, buff=0.2, stroke_width=3)

        with self.narrated(narrations[-1]) as _:
            self.play_paced(Write(final), run_time=1.3)
            self.play_paced(Create(box), run_time=0.8)
            self.wait_paced(2.0)

        # Fade everything and show closing summary
        self.play_paced(FadeOut(VGroup(final, box)), run_time=1.0)

        # --- Closing card ---
        summary_lines = VGroup(
            Text("Compléter le carré :", font_size=38),
            MathTex(r"x^2 + bx \;\longrightarrow\; \left(x + \tfrac{b}{2}\right)^2 - \tfrac{b^2}{4}", font_size=40, color=BLUE),
            Text("c'est remplir le coin manquant d'un grand carré.", font_size=30, color=GRAY_CUSTOM),
            Text("Tout le reste en découle.", font_size=32, color=BLACK),
        ).arrange(DOWN, buff=0.4).move_to(ORIGIN)

        with self.narrated(
            "En résumé : compléter le carré, c'est remplir le coin manquant d'un grand carré. "
            "La forme vertex, la formule quadratique — tout en découle."
        ) as _:
            for line in summary_lines:
                self.play_paced(FadeIn(line, shift=0.1 * UP), run_time=0.7)
            self.wait_paced(3.0)

        self.play_paced(FadeOut(summary_lines), run_time=1.0)

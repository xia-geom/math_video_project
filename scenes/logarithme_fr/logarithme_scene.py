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

ET = "<break time='150ms'/> et <break time='100ms'/>"


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class Logarithme(VoiceoverScene if VoiceoverScene is not None else Scene):
    def _setup_pacing(self):
        try:
            self.pace_factor = max(float(os.getenv("PACE_FACTOR", "1.2")), 0.1)
        except ValueError:
            self.pace_factor = 1.2

    def _paced_time(self, seconds: float) -> float:
        return seconds * self.pace_factor

    def play_paced(self, *args, run_time: float | None = None, **kwargs):
        if run_time is not None:
            kwargs["run_time"] = self._paced_time(run_time)
        self.play(*args, **kwargs)

    def wait_paced(self, seconds: float):
        self.wait(self._paced_time(seconds))

    def _setup_voiceover(self):
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover not installed. Rendering without narration.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print(
                "[voiceover] Missing Azure Speech credentials. Rendering without narration."
            )
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)

        self.set_speech_service(
            AzureService(
                voice="fr-CA-SylvieNeural",
                global_speed=1.0 / self.pace_factor,
            )
        )
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str):
        if self._voiceover_enabled:
            with self.voiceover(text=text) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_pacing()
        self._setup_voiceover()

        self._scene1_probleme()
        self._scene2_tableau()
        self._scene3_graphique()

    # ------------------------------------------------------------------
    # SCÈNE 1 — Problème-amorce
    # ------------------------------------------------------------------
    def _scene1_probleme(self):
        question = Text(
            "Une bactérie double toutes les heures.",
            font_size=38,
        ).to_edge(UP, buff=1.0)
        question2 = Text(
            "Après combien d'heures aura-t-on 16 bactéries ?",
            font_size=38,
        ).next_to(question, DOWN, buff=0.3)

        equation = MathTex(r"2^t = 16", font_size=72).shift(DOWN * 0.5)
        t_part = MathTex(r"t", font_size=72, color=BLUE).move_to(equation[0][1])

        question_mark = MathTex(r"?", font_size=96, color=RED).next_to(equation, RIGHT, buff=0.5)

        button = RoundedRectangle(
            width=6.5, height=0.9, corner_radius=0.2, color=BLUE, stroke_width=3
        ).to_edge(DOWN, buff=0.8)
        button_text = Text("Je ne sais pas encore…  →", font_size=30, color=BLUE).move_to(button)

        with self.narrated(
            "Une bactérie double toutes les heures. "
            "Après combien d'heures aura-t-on seize bactéries ?"
        ) as _:
            self.play_paced(FadeIn(question, shift=0.2 * DOWN), FadeIn(question2, shift=0.2 * DOWN), run_time=1.5)
            self.wait_paced(0.8)
            self.play_paced(Write(equation), run_time=1.5)
            self.wait_paced(0.5)

        # Animate the question mark pulsing on t
        self.play_paced(
            FadeIn(question_mark, scale=0.5),
            run_time=0.7,
        )
        self.play_paced(
            question_mark.animate.scale(1.25),
            rate_func=there_and_back,
            run_time=0.8,
        )
        self.play_paced(
            question_mark.animate.scale(1.25),
            rate_func=there_and_back,
            run_time=0.8,
        )

        with self.narrated("On ne sait pas encore résoudre ça. Mais on va construire l'outil.") as _:
            self.play_paced(FadeIn(button), FadeIn(button_text), run_time=1.0)
            self.wait_paced(1.2)

        # Flash the button, then fade everything
        self.play_paced(
            button.animate.set_fill(BLUE, opacity=0.15),
            run_time=0.4,
        )
        self.play_paced(
            FadeOut(VGroup(question, question2, equation, question_mark, button, button_text)),
            run_time=1.0,
        )

    # ------------------------------------------------------------------
    # SCÈNE 2 — Tableau de valeurs côte à côte
    # ------------------------------------------------------------------
    def _scene2_tableau(self):
        # --- Titles ---
        title_left = Text("Je connais ", font_size=28)
        title_left_t = MathTex(r"t", font_size=34, color=BLUE)
        title_left_rest = Text(", je cherche la population", font_size=28)
        title_left_group = VGroup(title_left, title_left_t, title_left_rest).arrange(RIGHT, buff=0.08)

        title_right = Text("Je connais la population,\nje cherche ", font_size=28)
        title_right_t = MathTex(r"t", font_size=34, color=BLUE)
        title_right_group = VGroup(title_right, title_right_t).arrange(RIGHT, buff=0.08)

        title_left_group.move_to(LEFT * 3.2 + UP * 3.0)
        title_right_group.move_to(RIGHT * 3.2 + UP * 3.0)

        divider = Line(UP * 3.5, DOWN * 3.0, color=GRAY, stroke_width=2).move_to(ORIGIN)

        col_left_header = VGroup(
            MathTex(r"t", font_size=36, color=BLUE),
            MathTex(r"2^t", font_size=36, color=BLACK),
        ).arrange(RIGHT, buff=1.0).move_to(LEFT * 3.2 + UP * 2.2)

        col_right_header = VGroup(
            MathTex(r"2^t", font_size=36, color=BLACK),
            MathTex(r"t", font_size=36, color=BLUE),
        ).arrange(RIGHT, buff=1.0).move_to(RIGHT * 3.2 + UP * 2.2)

        header_underline_l = Underline(col_left_header, color=BLACK)
        header_underline_r = Underline(col_right_header, color=BLACK)

        # Table data: t = 0..5
        t_vals = list(range(6))
        pop_vals = [2**t for t in t_vals]

        rows_left = VGroup()
        rows_right = VGroup()

        for i, (t, p) in enumerate(zip(t_vals, pop_vals)):
            y_pos = UP * (1.4 - i * 0.75)

            row_l = VGroup(
                MathTex(str(t), font_size=34, color=BLUE),
                MathTex(str(p), font_size=34),
            ).arrange(RIGHT, buff=1.3).move_to(LEFT * 3.2 + y_pos)

            row_r = VGroup(
                MathTex(str(p), font_size=34),
                MathTex(str(t), font_size=34, color=BLUE),
            ).arrange(RIGHT, buff=1.3).move_to(RIGHT * 3.2 + y_pos)

            rows_left.add(row_l)
            rows_right.add(row_r)

        with self.narrated(
            "Construisons un tableau. "
            "À gauche : je connais t, je cherche la population. "
            "À droite : je connais la population, je cherche t. "
            "Les colonnes sont inversées."
        ) as _:
            self.play_paced(
                FadeIn(title_left_group),
                FadeIn(title_right_group),
                Create(divider),
                FadeIn(col_left_header), FadeIn(col_right_header),
                Create(header_underline_l), Create(header_underline_r),
                run_time=1.8,
            )
            self.wait_paced(0.5)

            # Fill rows one by one with a delay
            for row_l, row_r in zip(rows_left, rows_right):
                self.play_paced(FadeIn(row_l, shift=0.1 * RIGHT), FadeIn(row_r, shift=0.1 * RIGHT), run_time=0.55)
                self.wait_paced(0.15)

            self.wait_paced(0.8)

        # Highlight that columns are swapped
        swap_note = Text("Les colonnes sont inversées !", font_size=32, color=BLUE).to_edge(DOWN, buff=0.9)
        swap_arrow = CurvedArrow(
            col_left_header[0].get_bottom() + DOWN * 0.05,
            col_right_header[1].get_bottom() + DOWN * 0.05,
            color=BLUE,
            angle=-TAU / 4,
        )
        self.play_paced(Write(swap_note), Create(swap_arrow), run_time=1.0)
        self.wait_paced(1.0)
        self.play_paced(FadeOut(swap_note), FadeOut(swap_arrow), run_time=0.7)

        # Blink t=4, 2^4=16 row (index 4)
        highlight_box_l = SurroundingRectangle(rows_left[4], color=RED, buff=0.12, stroke_width=3)
        highlight_box_r = SurroundingRectangle(rows_right[4], color=RED, buff=0.12, stroke_width=3)

        answer_note = Text("t = 4  →  2⁴ = 16 bactéries !", font_size=34, color=RED).to_edge(DOWN, buff=0.9)

        with self.narrated(
            "La réponse à notre question : quand t est égal à quatre, on a seize bactéries.") as _:
            self.play_paced(Create(highlight_box_l), Create(highlight_box_r), run_time=0.7)
            for _ in range(3):
                self.play_paced(
                    rows_left[4].animate.set_color(RED),
                    rows_right[4].animate.set_color(RED),
                    run_time=0.35,
                )
                self.play_paced(
                    rows_left[4].animate.set_color(BLACK),
                    rows_right[4].animate.set_color(BLACK),
                    run_time=0.35,
                )
            self.play_paced(FadeIn(answer_note), run_time=0.7)
            self.wait_paced(1.5)

        self.play_paced(
            FadeOut(VGroup(
                title_left_group, title_right_group, divider,
                col_left_header, col_right_header,
                header_underline_l, header_underline_r,
                rows_left, rows_right,
                highlight_box_l, highlight_box_r,
                answer_note,
            )),
            run_time=1.2,
        )

    # ------------------------------------------------------------------
    # SCÈNE 3 — Graphique animé
    # ------------------------------------------------------------------
    def _scene3_graphique(self):
        axes = Axes(
            x_range=[-0.5, 5.2, 1],
            y_range=[-0.5, 5.2, 1],
            x_length=6.5,
            y_length=6.5,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
        ).shift(DOWN * 0.3)
        axis_labels = axes.get_axis_labels(MathTex("x"), MathTex("y"))

        # Diagonal y = x (dashed)
        diag_solid = axes.plot(lambda x: x, x_range=[0, 5], color=GRAY, stroke_width=2)
        diag = DashedVMobject(diag_solid, num_dashes=30, color=GRAY)
        diag_label = MathTex("y = x", font_size=28, color=GRAY).next_to(axes.c2p(4.6, 4.6), UR, buff=0.1)

        # 2^x curve
        exp_curve = axes.plot(
            lambda x: 2**x,
            x_range=[0, np.log2(5.1)],
            color=BLUE,
            stroke_width=4,
        )
        exp_label = MathTex(r"f(x) = 2^x", font_size=30, color=BLUE).next_to(axes.c2p(2.2, 5.0), UR, buff=0.1)

        # log2 curve
        log_curve = axes.plot(
            lambda x: np.log2(x),
            x_range=[0.08, 5.1],
            color=ORANGE,
            stroke_width=4,
        )
        log_label = MathTex(r"f^{-1}(x) = \log_2 x", font_size=30, color=ORANGE).next_to(
            axes.c2p(4.8, 2.3), RIGHT, buff=0.08
        )

        # Domain/range legend
        exp_dom = Text("Domaine : ℝ   Image : (0, +∞)", font_size=22, color=BLUE).to_corner(UL, buff=0.5)
        log_dom = Text("Domaine : (0, +∞)   Image : ℝ", font_size=22, color=ORANGE).next_to(exp_dom, DOWN, buff=0.15, aligned_edge=LEFT)

        with self.narrated("Traçons d'abord la courbe de deux puissance x en bleu.") as _:
            self.play_paced(Create(axes), Write(axis_labels), run_time=1.5)
            self.play_paced(Create(exp_curve), run_time=2.5)
            self.play_paced(Write(exp_label), run_time=0.7)
            self.wait_paced(0.5)

        with self.narrated("Puis la droite y égal x en gris pointillé.") as _:
            self.play_paced(
                Create(diag),
                Write(diag_label),
                run_time=1.2,
            )
            self.wait_paced(0.4)

        with self.narrated(
            "Et maintenant, le logarithme en base deux en orange. "
            "C'est le reflet de la courbe bleue par rapport à la diagonale."
        ) as _:
            # Mirror animation: flash a dot on exp curve then reflect to log
            sample_xs = [0.5, 1.0, 2.0, 3.0]
            for sx in sample_xs:
                sy = 2**sx
                dot_exp = Dot(axes.c2p(sx, sy), color=BLUE, radius=0.07)
                dot_log = Dot(axes.c2p(sy, sx), color=ORANGE, radius=0.07)
                mirror_line = DashedLine(axes.c2p(sx, sy), axes.c2p(sy, sx), color=GRAY, stroke_width=1.5)
                self.play_paced(FadeIn(dot_exp), run_time=0.25)
                self.play_paced(Create(mirror_line), run_time=0.35)
                self.play_paced(FadeIn(dot_log), run_time=0.25)
                self.play_paced(FadeOut(dot_exp), FadeOut(dot_log), FadeOut(mirror_line), run_time=0.3)

            self.play_paced(Create(log_curve), run_time=2.0)
            self.play_paced(Write(log_label), run_time=0.7)
            self.play_paced(FadeIn(exp_dom), FadeIn(log_dom), run_time=0.8)
            self.wait_paced(1.0)

        # Interactive hover simulation: show symmetric point pairs
        hover_note = Text("Survol : le point symétrique s'allume sur l'autre courbe", font_size=22, color=GRAY).to_edge(DOWN, buff=0.4)
        self.play_paced(FadeIn(hover_note), run_time=0.6)

        hover_xs = [1.5, 3.0, 0.5]
        for hx in hover_xs:
            hy = 2**hx
            dot_on_exp = Dot(axes.c2p(hx, hy), color=BLUE, radius=0.1)
            dot_on_log = Dot(axes.c2p(hy, hx), color=ORANGE, radius=0.1)
            coord_exp = MathTex(
                f"({hx:.1f},\\ {hy:.1f})", font_size=24, color=BLUE
            ).next_to(dot_on_exp, UL, buff=0.1)
            coord_log = MathTex(
                f"({hy:.1f},\\ {hx:.1f})", font_size=24, color=ORANGE
            ).next_to(dot_on_log, DR, buff=0.1)

            self.play_paced(FadeIn(dot_on_exp), FadeIn(coord_exp), run_time=0.4)
            self.play_paced(FadeIn(dot_on_log), FadeIn(coord_log), run_time=0.4)
            self.wait_paced(0.9)
            self.play_paced(
                FadeOut(dot_on_exp), FadeOut(dot_on_log),
                FadeOut(coord_exp), FadeOut(coord_log),
                run_time=0.35,
            )

        self.play_paced(FadeOut(hover_note), run_time=0.5)
        self.wait_paced(0.5)

        # Final summary
        summary_1 = MathTex(r"2^t \text{ et } \log_2 \text{ sont inverses l'une de l'autre}", font_size=34).to_edge(DOWN, buff=0.5)
        self.play_paced(FadeIn(summary_1, shift=0.15 * UP), run_time=1.0)
        self.wait_paced(3.0)
        self.play_paced(FadeOut(summary_1), run_time=0.8)
        self._scene3_exp_curve = exp_curve
        self._scene3_log_curve = log_curve
        self._scene3_diag = diag
        self._scene3_diag_label = diag_label
        self._scene3_exp_label = exp_label
        self._scene3_log_label = log_label
        self._scene3_axis_labels = axis_labels
        self._scene3_exp_dom = exp_dom
        self._scene3_log_dom = log_dom

    # ------------------------------------------------------------------
    # SCÈNE 4 — Synthèse interactive avec curseur
    # ------------------------------------------------------------------
    # def _scene4_synthese(self):
    #     axes = self._scene3_axes
    #     exp_curve = self._scene3_exp_curve
    #     log_curve = self._scene3_log_curve

    #     # Fade out legend and labels, keep curves + axes
    #     self.play_paced(
    #         FadeOut(self._scene3_diag),
    #         FadeOut(self._scene3_diag_label),
    #         FadeOut(self._scene3_exp_label),
    #         FadeOut(self._scene3_log_label),
    #         FadeOut(self._scene3_exp_dom),
    #         FadeOut(self._scene3_log_dom),
    #         run_time=0.8,
    #     )

    #     # Title
    #     title = Text("Synthèse interactive", font_size=36).to_edge(UP, buff=0.3)
    #     self.play_paced(FadeIn(title), run_time=0.6)

    #     # Slider setup
    #     t_tracker = ValueTracker(2.0)

    #     slider_line = Line(LEFT * 3, RIGHT * 3, color=GRAY, stroke_width=3).to_edge(DOWN, buff=1.6)
    #     slider_min = MathTex("0", font_size=26).next_to(slider_line.get_left(), DOWN, buff=0.15)
    #     slider_max = MathTex("5", font_size=26).next_to(slider_line.get_right(), DOWN, buff=0.15)
    #     slider_label = Text("t =", font_size=28).next_to(slider_line, LEFT, buff=0.3)

    #     def get_slider_x():
    #         frac = (t_tracker.get_value() - 0) / 5.0
    #         return slider_line.get_left() + RIGHT * frac * 6.0

    #     slider_dot = always_redraw(
    #         lambda: Dot(get_slider_x(), color=BLUE, radius=0.12)
    #     )
    #     slider_t_val = always_redraw(
    #         lambda: MathTex(
    #             f"{t_tracker.get_value():.2f}", font_size=26, color=BLUE
    #         ).next_to(slider_dot, UP, buff=0.15)
    #     )

    #     # Formula display
    #     def get_exp_tex():
    #         t = t_tracker.get_value()
    #         val = 2**t
    #         return MathTex(
    #             rf"f(t) = 2^{{{t:.2f}}} = {val:.2f}",
    #             font_size=38,
    #             color=BLUE,
    #         ).to_edge(DOWN, buff=3.2)

    #     def get_log_tex():
    #         t = t_tracker.get_value()
    #         val = 2**t
    #         return MathTex(
    #             rf"f^{{-1}}({val:.2f}) = \log_2({val:.2f}) = {t:.2f}",
    #             font_size=38,
    #             color=ORANGE,
    #         ).next_to(get_exp_tex(), DOWN, buff=0.3)

    #     exp_tex = always_redraw(get_exp_tex)
    #     log_tex = always_redraw(get_log_tex)

    #     # Moving dots on each curve
    #     dot_exp = always_redraw(
    #         lambda: Dot(
    #             axes.c2p(t_tracker.get_value(), 2 ** t_tracker.get_value()),
    #             color=BLUE,
    #             radius=0.1,
    #         )
    #     )
    #     dot_log = always_redraw(
    #         lambda: Dot(
    #             axes.c2p(2 ** t_tracker.get_value(), t_tracker.get_value()),
    #             color=ORANGE,
    #             radius=0.1,
    #         )
    #     )

    #     # Dashed lines from dots to axes
    #     dashed_v_exp = always_redraw(
    #         lambda: DashedLine(
    #             axes.c2p(t_tracker.get_value(), 0),
    #             axes.c2p(t_tracker.get_value(), 2 ** t_tracker.get_value()),
    #             color=BLUE,
    #             stroke_width=1.5,
    #             dash_length=0.12,
    #         )
    #     )
    #     dashed_h_exp = always_redraw(
    #         lambda: DashedLine(
    #             axes.c2p(0, 2 ** t_tracker.get_value()),
    #             axes.c2p(t_tracker.get_value(), 2 ** t_tracker.get_value()),
    #             color=BLUE,
    #             stroke_width=1.5,
    #             dash_length=0.12,
    #         )
    #     )

    #     with self.narrated(
    #         "Avec ce curseur, on peut choisir une valeur de t entre zéro et cinq. "
    #         "On voit simultanément deux puissance t et son inverse, le logarithme en base deux. "
    #         "Le point se déplace en temps réel sur les deux courbes."
    #     ) as _:
    #         self.play_paced(
    #             FadeIn(slider_line), FadeIn(slider_min), FadeIn(slider_max),
    #             FadeIn(slider_label), FadeIn(slider_dot), FadeIn(slider_t_val),
    #             FadeIn(exp_tex), FadeIn(log_tex),
    #             FadeIn(dot_exp), FadeIn(dot_log),
    #             FadeIn(dashed_v_exp), FadeIn(dashed_h_exp),
    #             run_time=1.5,
    #         )
    #         self.wait_paced(0.5)

    #         # Animate slider from 2 → 4 (answer to scene 1) → 0.5 → 5
    #         self.play_paced(t_tracker.animate.set_value(4.0), run_time=2.5, rate_func=smooth)
    #         self.wait_paced(0.8)

    #         # Flash at t=4 (answer!)
    #         answer_flash = Text("t = 4  →  2⁴ = 16 ✓", font_size=32, color=RED).to_corner(UR, buff=0.6)
    #         self.play_paced(FadeIn(answer_flash, scale=0.8), run_time=0.6)
    #         self.wait_paced(1.2)
    #         self.play_paced(FadeOut(answer_flash), run_time=0.5)

    #         self.play_paced(t_tracker.animate.set_value(0.5), run_time=2.0, rate_func=smooth)
    #         self.wait_paced(0.5)
    #         self.play_paced(t_tracker.animate.set_value(5.0), run_time=3.0, rate_func=smooth)
    #         self.wait_paced(0.5)
    #         self.play_paced(t_tracker.animate.set_value(2.0), run_time=1.5, rate_func=smooth)
    #         self.wait_paced(1.0)

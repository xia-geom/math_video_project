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

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import tools.tts as tts
from tools.branding import play_uqam_intro

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class LogarithmeProprietes(VoiceoverScene if VoiceoverScene is not None else Scene):
    """
    Scenes:
      1  – Accroche : croissance bactérienne & question N(t) = N₀ · 2^t
      2  – Injectivité de l'exponentielle (horizontal line test)
      3  – Propriété du produit  log_a(bc) = log_a(b) + log_a(c)
      4  – Changement de base    log_a(c) = log_a(b) · log_b(c)
      5  – Synthèse + réponse à la question initiale
    """

    # ------------------------------------------------------------------
    # Infrastructure (mirrors logarithme_scene.py conventions)
    # ------------------------------------------------------------------
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
            print("[voiceover] Missing Azure Speech credentials. Rendering without narration.")
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)

        self.set_speech_service(
            AzureService(
                voice=tts.VOICE_ID,
                global_speed=1.0 / self.pace_factor,
            )
        )
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str):
        if self._voiceover_enabled:
            with self.voiceover(text=tts.ssml(text, "0%"), subcaption=tts.strip_ssml(text)) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_pacing()
        self._setup_voiceover()
        play_uqam_intro(self)

        self._scene1_accroche()
        self._scene2_injectivite()
        self._scene3_produit()
        self._scene4_changement_base()
        self._scene5_synthese()

    # ------------------------------------------------------------------
    # SCÈNE 1 — Accroche : bactéries (arbre binaire)
    # ------------------------------------------------------------------
    def _scene1_accroche(self):
        title = Text("Croissance bactérienne", font_size=40).to_edge(UP, buff=0.5)
        BACT_COLOR = BLUE
        ARROW_COLOR = BLACK

        # --- Tree node positions (left → right by generation) ---
        x0, x1, x2 = -5.0, -1.8, 1.4
        pos_g0 = [np.array([x0,  0.0, 0])]
        pos_g1 = [np.array([x1,  1.2, 0]), np.array([x1, -1.2, 0])]
        pos_g2 = [
            np.array([x2,  2.1, 0]),
            np.array([x2,  0.65, 0]),
            np.array([x2, -0.65, 0]),
            np.array([x2, -2.1, 0]),
        ]
        dot_r = 0.16

        def mk_dot(pos):
            return Dot(pos, radius=dot_r, color=BACT_COLOR)

        def mk_arrow(src, dst):
            return Arrow(
                src, dst, buff=dot_r + 0.05,
                color=ARROW_COLOR,
                stroke_width=2.5,
                max_tip_length_to_length_ratio=0.18,
            )

        d0 = mk_dot(pos_g0[0])
        d1 = [mk_dot(p) for p in pos_g1]
        d2 = [mk_dot(p) for p in pos_g2]

        arrows_01 = [mk_arrow(pos_g0[0], p) for p in pos_g1]
        arrows_12 = [mk_arrow(pos_g1[i // 2], pos_g2[i]) for i in range(4)]

        # Generation + population labels under each column
        def gen_label(t_val, n_val, x_pos):
            return VGroup(
                Text(f"t = {t_val}", font_size=22, color=GRAY),
                MathTex(f"N = {n_val}", font_size=22, color=BACT_COLOR),
            ).arrange(DOWN, buff=0.06).move_to(np.array([x_pos, -2.9, 0]))

        lbl_g0 = gen_label(0, 1,  x0)
        lbl_g1 = gen_label(1, 2,  x1)
        lbl_g2 = gen_label(2, 4,  x2)

        formula = MathTex(r"N(t) = 2^t", font_size=44).to_corner(UR, buff=0.7)

        # Legend: meaning of t and N — visible during the first ~9s
        legend = VGroup(
            VGroup(
                MathTex(r"t", font_size=32, color=BLACK),
                Text(": numéro de génération (heures)", font_size=24, color=BLACK),
            ).arrange(RIGHT, buff=0.15),
            VGroup(
                MathTex(r"N", font_size=32, color=BLUE),
                Text(": nombre de bactéries", font_size=24, color=BLACK),
            ).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).to_corner(UL, buff=0.6).shift(DOWN * 0.8)

        # Analysis shown centred after the tree fades (~10s)
        log_answer = MathTex(r"t = \log_2(N)", font_size=52, color=BLACK).move_to(UP * 0.6)
        log_meaning = Text(
            "Le logarithme répond :\nà quel exposant faut-il élever 2 pour obtenir N ?",
            font_size=28, color=BLUE,
        ).next_to(log_answer, DOWN, buff=0.4)

        with self.narrated(
            "Imaginez une bactérie qui se divise en deux à chaque génération. "
            "Au départ, une seule bactérie, puis deux, puis quatre. "
            "Ici, t désigne le numéro de génération et N le nombre de bactéries."
        ) as _:
            self.play_paced(FadeIn(title, shift=0.2 * DOWN), run_time=0.8)
            self.play_paced(FadeIn(legend), run_time=0.6)
            # Generation 0
            self.play_paced(GrowFromCenter(d0), run_time=0.6)
            self.play_paced(FadeIn(lbl_g0), run_time=0.4)
            self.wait_paced(0.3)
            # Generation 1: arrows then dots
            self.play_paced(*[GrowArrow(a) for a in arrows_01], run_time=0.8)
            self.play_paced(*[GrowFromCenter(d) for d in d1], run_time=0.6)
            self.play_paced(FadeIn(lbl_g1), run_time=0.4)
            self.wait_paced(0.3)
            # Generation 2: arrows then dots
            self.play_paced(*[GrowArrow(a) for a in arrows_12], run_time=0.8)
            self.play_paced(*[GrowFromCenter(d) for d in d2], run_time=0.6)
            self.play_paced(FadeIn(lbl_g2), run_time=0.4)
            self.wait_paced(0.5)

        with self.narrated(
            "La population suit la formule N de t égal deux puissance t."
        ) as _:
            self.play_paced(Write(formula), run_time=0.9)
            self.wait_paced(0.8)

        # ~10s mark: fade tree out, show analysis centred
        tree_objects = VGroup(
            title, legend, d0, *d1, *d2,
            *arrows_01, *arrows_12,
            lbl_g0, lbl_g1, lbl_g2,
            formula,
        )
        with self.narrated(
            "Mais si on connaît la population, comment retrouver le numéro de génération ? "
            "C'est exactement la question que répond le logarithme : "
            "t égal logarithme en base deux de N. "
            "À quel exposant faut-il élever deux pour obtenir N ?"
        ) as _:
            self.play_paced(FadeOut(tree_objects), run_time=0.8)
            self.play_paced(Write(log_answer), run_time=1.0)
            self.play_paced(FadeIn(log_meaning, shift=0.1 * UP), run_time=0.9)
            self.wait_paced(1.8)

        self.play_paced(FadeOut(VGroup(log_answer, log_meaning)), run_time=1.0)

    # ------------------------------------------------------------------
    # SCÈNE 2 — Injectivité de f(x) = 2^x
    # ------------------------------------------------------------------
    def _scene2_injectivite(self):
        title = Text("Injectivité de la fonction exponentielle", font_size=34).to_edge(UP, buff=0.5)

        axes = Axes(
            x_range=[-1, 4.2, 1],
            y_range=[-0.5, 9.5, 2],
            x_length=6.0,
            y_length=5.2,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
        ).shift(DOWN * 0.5 + LEFT * 1.0)
        ax_labels = axes.get_axis_labels(
            MathTex("x", font_size=30), MathTex("y", font_size=30)
        )

        curve = axes.plot(lambda x: 2**x, x_range=[-0.8, 3.17], color=BLUE, stroke_width=4)
        curve_label = MathTex(r"f(x) = 2^x", font_size=30, color=BLUE).next_to(
            axes.c2p(3.0, 8.0), RIGHT, buff=0.1
        )

        # Horizontal line that sweeps upward
        h_line = axes.plot(lambda x: 1.0, x_range=[-0.8, 3.17], color=RED, stroke_width=2.5)

        principle_box = RoundedRectangle(
            width=6.8, height=1.3, corner_radius=0.15, color=BLUE, stroke_width=2.5
        ).to_corner(UR, buff=0.5)
        principle_tex = MathTex(
            r"\text{Injective : } f(x) = f(y) \;\Rightarrow\; x = y",
            font_size=28,
            color=BLUE,
        ).move_to(principle_box)

        note = Text(
            "C'est ce principe qui justifie\ntoutes les propriétés du logarithme.",
            font_size=24,
            color=GRAY,
        ).to_edge(DOWN, buff=0.5)

        with self.narrated(
            "La clé de tout, c'est l'injectivité de l'exponentielle. "
            "Traçons la courbe de deux puissance x."
        ) as _:
            self.play_paced(FadeIn(title, shift=0.1 * DOWN), run_time=0.8)
            self.play_paced(Create(axes), Write(ax_labels), run_time=1.2)
            self.play_paced(Create(curve), run_time=1.8)
            self.play_paced(Write(curve_label), run_time=0.6)

        with self.narrated(
            "Faisons passer une droite horizontale. Elle ne touche la courbe qu'une seule fois. "
            "Chaque valeur y est atteinte par un unique x. "
            "C'est ce qu'on appelle une fonction injective : si f de x égale f de y, alors x égale y."
        ) as _:
            # Sweep the horizontal line from y=0.5 to y=8
            y_tracker = ValueTracker(0.5)
            h_line_dynamic = always_redraw(
                lambda: axes.plot(
                    lambda x: y_tracker.get_value(),
                    x_range=[-0.8, 3.17],
                    color=RED,
                    stroke_width=2.5,
                )
            )
            # Intersection dot
            def get_intersect_dot():
                y_val = y_tracker.get_value()
                if y_val <= 0:
                    return VGroup()
                x_val = np.log2(y_val)
                if x_val < -0.8 or x_val > 3.17:
                    return VGroup()
                return Dot(axes.c2p(x_val, y_val), color=RED, radius=0.10)

            intersect_dot = always_redraw(get_intersect_dot)

            self.add(h_line_dynamic, intersect_dot)
            self.play_paced(y_tracker.animate.set_value(8.0), run_time=3.5, rate_func=smooth)
            self.wait_paced(0.4)
            self.remove(h_line_dynamic, intersect_dot)

            self.play_paced(
                FadeIn(principle_box), Write(principle_tex), run_time=1.2
            )
            self.wait_paced(0.5)

        with self.narrated(
            "C'est ce principe d'injectivité qui va justifier toutes les propriétés du logarithme."
        ) as _:
            self.play_paced(FadeIn(note), run_time=0.8)
            self.wait_paced(1.5)

        self.play_paced(
            FadeOut(VGroup(title, axes, ax_labels, curve, curve_label,
                           principle_box, principle_tex, note)),
            run_time=1.0,
        )

    # ------------------------------------------------------------------
    # SCÈNE 3 — Propriété du produit
    # ------------------------------------------------------------------
    def _scene3_produit(self):
        title = Text("Propriété du produit", font_size=36).to_edge(UP, buff=0.5)

        prop = MathTex(
            r"\log_a(bc) = \log_a(b) + \log_a(c)",
            font_size=48,
        ).next_to(title, DOWN, buff=0.5)

        box = SurroundingRectangle(prop, color=BLUE, buff=0.18, stroke_width=2.5)

        # Proof steps
        steps = [
            MathTex(r"\text{Posons } u = \log_a(b) \;\Rightarrow\; a^u = b", font_size=36),
            MathTex(r"\text{Posons } v = \log_a(c) \;\Rightarrow\; a^v = c", font_size=36),
            MathTex(r"bc = a^u \cdot a^v = a^{u+v}", font_size=36),
            MathTex(
                r"\text{Par injectivité :}\quad \log_a(bc) = u + v",
                font_size=36,
                color=BLUE,
            ),
        ]
        proof_group = VGroup(*steps).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        proof_group.next_to(prop, DOWN, buff=0.55)

        narration_steps = [
            "Posons u égal logarithme en base a de b. Par définition, a puissance u égale b.",
            "De même, posons v égal logarithme en base a de c. Alors a puissance v égale c.",
            "En multipliant : b c égale a puissance u fois a puissance v, "
            "ce qui vaut a puissance u plus v.",
            "Par injectivité de l'exponentielle, le logarithme en base a de b c vaut u plus v.",
        ]

        with self.narrated(
            "La première propriété : le logarithme d'un produit est la somme des logarithmes."
        ) as _:
            self.play_paced(FadeIn(title, shift=0.1 * DOWN), run_time=0.7)
            self.play_paced(Write(prop), run_time=1.2)
            self.play_paced(Create(box), run_time=0.6)
            self.wait_paced(0.5)

        with self.narrated("Voici la preuve, étape par étape.") as _:
            self.wait_paced(0.3)

        for step, narr in zip(steps, narration_steps):
            with self.narrated(narr) as _:
                self.play_paced(FadeIn(step, shift=0.1 * RIGHT), run_time=0.8)
                self.wait_paced(0.4)

        self.wait_paced(0.8)
        self.play_paced(
            FadeOut(VGroup(title, prop, box, proof_group)),
            run_time=0.8,
        )

    # ------------------------------------------------------------------
    # SCÈNE 4 — Changement de base
    # ------------------------------------------------------------------
    def _scene4_changement_base(self):
        title = Text("Changement de base", font_size=36).to_edge(UP, buff=0.5)

        prop = MathTex(
            r"\log_a(c) = \log_a(b) \cdot \log_b(c)",
            font_size=48,
        ).next_to(title, DOWN, buff=0.5)
        box = SurroundingRectangle(prop, color=BLUE, buff=0.18, stroke_width=2.5)

        steps = [
            MathTex(r"\text{Posons } v = \log_b(c) \;\Rightarrow\; c = b^v", font_size=36),
            MathTex(r"\log_a(c) = \log_a\!\left(b^v\right) = v \cdot \log_a(b)", font_size=36),
            MathTex(
                r"\text{Par injectivité :}\quad \log_a(c) = \log_a(b) \cdot \log_b(c)",
                font_size=34,
                color=BLUE,
            ),
        ]
        proof_group = VGroup(*steps).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        proof_group.next_to(prop, DOWN, buff=0.55)

        analogy = Text(
            "Comme convertir des km en pouces en passant par les mètres.",
            font_size=26,
            color=GRAY,
        ).to_edge(DOWN, buff=1.1)

        # Concrete example — clean centered derivation
        example_title = Text("Exemple concret :", font_size=32).to_edge(UP, buff=0.6)

        # Each step as its own MathTex, uniform font size, centred
        ex_step1 = MathTex(
            r"\log_2(1\,000\,000)",
            r"= \frac{\log_{10}(1\,000\,000)}{\log_{10}(2)}",
            font_size=40,
        )
        ex_label1 = Text("changement de base", font_size=22, color=BLUE)

        ex_step2 = MathTex(
            r"= \frac{6}{\log_{10}(2)}",
            font_size=40,
        )
        ex_label2 = Text(
            r"car  log₁₀(10⁶) = 6",
            font_size=22, color=BLACK,
        )

        ex_step3 = MathTex(
            r"\approx \frac{6}{0{,}301}",
            font_size=40,
        )
        ex_label3 = Text("log₁₀(2) ≈ 0,301", font_size=22, color=BLACK)

        ex_step4 = MathTex(
            r"\approx 19{,}93 \text{ heures}",
            font_size=44, color=RED,
        )

        # Pair each step with its annotation, centred
        def step_row(step, label):
            return VGroup(step, label).arrange(RIGHT, buff=0.4)

        ex_group = VGroup(
            step_row(ex_step1, ex_label1),
            step_row(ex_step2, ex_label2),
            step_row(ex_step3, ex_label3),
            ex_step4,
        ).arrange(DOWN, buff=0.45)
        ex_group.move_to(ORIGIN + DOWN * 0.2)

        narration_proof = [
            "Posons v égal logarithme en base b de c. Par définition, c égale b puissance v.",
            "En appliquant logarithme en base a des deux côtés : "
            "logarithme en base a de c égale v fois logarithme en base a de b.",
            "Par injectivité, on obtient la formule de changement de base.",
        ]

        with self.narrated(
            "Deuxième propriété fondamentale : le changement de base."
        ) as _:
            self.play_paced(FadeIn(title, shift=0.1 * DOWN), run_time=0.7)
            self.play_paced(Write(prop), run_time=1.2)
            self.play_paced(Create(box), run_time=0.6)
            self.wait_paced(0.5)

        with self.narrated("Preuve en trois étapes.") as _:
            self.wait_paced(0.3)

        for step, narr in zip(steps, narration_proof):
            with self.narrated(narr) as _:
                self.play_paced(FadeIn(step, shift=0.1 * RIGHT), run_time=0.8)
                self.wait_paced(0.3)

        with self.narrated(
            "L'analogie : changer de base, c'est comme convertir des kilomètres en pouces "
            "en passant d'abord par les mètres."
        ) as _:
            self.play_paced(FadeIn(analogy), run_time=0.8)
            self.wait_paced(1.2)

        # Transition to concrete example
        self.play_paced(
            FadeOut(VGroup(title, prop, box, proof_group, analogy)),
            run_time=0.8,
        )

        with self.narrated(
            "Appliquons le changement de base à notre question initiale. "
            "Logarithme en base deux d'un million "
            "égale logarithme base dix d'un million divisé par logarithme base dix de deux."
        ) as _:
            self.play_paced(FadeIn(example_title), run_time=0.5)
            self.play_paced(Write(ex_step1), FadeIn(ex_label1), run_time=1.0)
            self.wait_paced(0.5)

        with self.narrated(
            "Un million vaut dix puissance six, donc logarithme base dix d'un million vaut six."
        ) as _:
            self.play_paced(Write(ex_step2), FadeIn(ex_label2), run_time=1.0)
            self.wait_paced(0.5)

        with self.narrated(
            "Logarithme base dix de deux vaut environ zéro virgule trois zéro un."
        ) as _:
            self.play_paced(Write(ex_step3), FadeIn(ex_label3), run_time=0.8)
            self.wait_paced(0.5)

        with self.narrated(
            "Ce qui donne environ dix-neuf virgule neuf-trois heures."
        ) as _:
            self.play_paced(Write(ex_step4), run_time=1.0)
            self.wait_paced(1.2)

        self.play_paced(
            FadeOut(VGroup(example_title, ex_group)),
            run_time=0.8,
        )

    # ------------------------------------------------------------------
    # SCÈNE 5 — Synthèse
    # ------------------------------------------------------------------
    def _scene5_synthese(self):
        title = Text("Synthèse", font_size=40).to_edge(UP, buff=0.5)

        # Summary table (two rows)
        col_headers = VGroup(
            Text("Propriété", font_size=28, color=BLACK),
            Text("Formule", font_size=28, color=BLACK),
        ).arrange(RIGHT, buff=3.8)
        col_headers.next_to(title, DOWN, buff=0.5)

        header_line = Line(
            col_headers.get_left() + LEFT * 0.3,
            col_headers.get_right() + RIGHT * 0.3,
            color=BLACK, stroke_width=1.5,
        ).next_to(col_headers, DOWN, buff=0.1)

        row1_label = Text("Produit", font_size=26)
        row1_formula = MathTex(
            r"\log_a(bc) = \log_a(b) + \log_a(c)", font_size=30, color=BLUE
        )

        row2_label = Text("Changement de base", font_size=26)
        row2_formula = MathTex(
            r"\log_a(c) = \log_a(b) \cdot \log_b(c)", font_size=30, color=BLUE
        )

        # Align columns
        row_y1 = header_line.get_bottom() + DOWN * 0.55
        row_y2 = row_y1 + DOWN * 0.85

        row1_label.move_to(col_headers[0].get_center() + (row_y1 - col_headers.get_center()))
        row1_formula.move_to(col_headers[1].get_center() + (row_y1 - col_headers.get_center()))
        row2_label.move_to(col_headers[0].get_center() + (row_y2 - col_headers.get_center()))
        row2_formula.move_to(col_headers[1].get_center() + (row_y2 - col_headers.get_center()))

        row_divider = Line(
            header_line.get_left(),
            header_line.get_right(),
            color=GRAY, stroke_width=1,
        ).next_to(row1_formula, DOWN, buff=0.3)

        # Answer box
        answer_box = RoundedRectangle(
            width=7.5, height=1.5, corner_radius=0.2, color=RED, stroke_width=2.5
        )
        answer_box.move_to(DOWN * 1.8)
        answer_tex = MathTex(
            r"\log_2(1\,000\,000) \approx 19.93 \text{ heures}",
            font_size=38,
            color=RED,
        ).move_to(answer_box)

        closing = Text(
            "Le logarithme : l'outil pour inverser une exponentielle.",
            font_size=28,
            color=BLUE,
        ).to_edge(DOWN, buff=0.5)

        with self.narrated(
            "Résumons les deux propriétés essentielles que nous venons d'établir."
        ) as _:
            self.play_paced(FadeIn(title, shift=0.1 * DOWN), run_time=0.7)
            self.play_paced(
                FadeIn(col_headers), Create(header_line), run_time=0.8
            )

        with self.narrated(
            "Première propriété : le logarithme d'un produit est la somme des logarithmes."
        ) as _:
            self.play_paced(FadeIn(row1_label), Write(row1_formula), run_time=1.0)
            self.wait_paced(0.3)

        with self.narrated(
            "Deuxième propriété : la formule de changement de base."
        ) as _:
            self.play_paced(Create(row_divider), run_time=0.4)
            self.play_paced(FadeIn(row2_label), Write(row2_formula), run_time=1.0)
            self.wait_paced(0.5)

        with self.narrated(
            "Et maintenant, répondons à notre question de départ. "
            "Pour trouver après combien d'heures on a un million de bactéries, "
            "on applique le changement de base : logarithme en base deux d'un million "
            "est environ dix-neuf virgule neuf-trois heures."
        ) as _:
            self.play_paced(
                Create(answer_box), Write(answer_tex), run_time=1.4
            )
            self.wait_paced(1.0)

            # Flash answer
            self.play_paced(
                answer_box.animate.set_stroke(RED, width=5),
                rate_func=there_and_back,
                run_time=0.6,
            )
            self.play_paced(
                answer_box.animate.set_stroke(RED, width=5),
                rate_func=there_and_back,
                run_time=0.6,
            )
            self.wait_paced(0.5)

        with self.narrated(
            "Le logarithme : l'outil pour inverser une exponentielle."
        ) as _:
            self.play_paced(Write(closing), run_time=1.2)
            self.wait_paced(2.5)

        self.play_paced(
            FadeOut(VGroup(
                title, col_headers, header_line,
                row1_label, row1_formula,
                row_divider,
                row2_label, row2_formula,
                answer_box, answer_tex,
                closing,
            )),
            run_time=1.2,
        )

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

import tools.tts as tts

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

        self._scene1_accroche()
        self._scene2_injectivite()
        self._scene3_produit()
        self._scene4_changement_base()
        self._scene5_synthese()

    # ------------------------------------------------------------------
    # SCÈNE 1 — Accroche : bactéries
    # ------------------------------------------------------------------
    def _scene1_accroche(self):
        title = Text("Une colonie de bactéries", font_size=40).to_edge(UP, buff=0.6)

        formula = MathTex(r"N(t) = N_0 \cdot 2^t", font_size=56).shift(UP * 0.8)
        formula_note = Text("(doublement chaque heure)", font_size=26, color=GRAY).next_to(
            formula, DOWN, buff=0.2
        )

        # Animate growing dots in a rough circular cluster
        dot_positions = [
            ORIGIN,
            RIGHT * 0.55, LEFT * 0.55, UP * 0.55, DOWN * 0.55,
            RIGHT * 0.55 + UP * 0.55, RIGHT * 0.55 + DOWN * 0.55,
            LEFT * 0.55 + UP * 0.55, LEFT * 0.55 + DOWN * 0.55,
            RIGHT * 1.1, LEFT * 1.1, UP * 1.1, DOWN * 1.1,
            RIGHT * 1.1 + UP * 0.55, LEFT * 1.1 + DOWN * 0.55,
            RIGHT * 0.55 + UP * 1.1, LEFT * 0.55 + DOWN * 1.1,
        ]
        colony = VGroup(
            *[Dot(p + DOWN * 1.6, radius=0.10, color=GREEN_D) for p in dot_positions]
        )

        question = MathTex(
            r"\text{Si } N_0 = 1,\quad 2^t = 1\,000\,000 \quad \Rightarrow \quad t = \,?",
            font_size=38,
        ).to_edge(DOWN, buff=1.1)

        transition = Text(
            "Pour répondre → il faut inverser l'exponentielle → c'est le logarithme.",
            font_size=26,
            color=BLUE,
        ).to_edge(DOWN, buff=0.4)

        with self.narrated(
            "Imaginez une colonie de bactéries qui double chaque heure. "
            "La population suit la formule N de t égal N zéro fois deux puissance t."
        ) as _:
            self.play_paced(FadeIn(title, shift=0.2 * DOWN), run_time=1.0)
            self.play_paced(Write(formula), run_time=1.4)
            self.play_paced(FadeIn(formula_note), run_time=0.6)

            # Grow dots one by one in batches to simulate doubling
            for i, dot in enumerate(colony):
                self.play_paced(GrowFromCenter(dot), run_time=0.08)
            self.wait_paced(0.5)

        with self.narrated(
            "Si on part d'une seule bactérie, après combien d'heures en aura-t-on un million ? "
            "Pour répondre, il faut inverser l'exponentielle. C'est exactement ce que fait le logarithme."
        ) as _:
            self.play_paced(FadeIn(question, shift=0.1 * UP), run_time=1.0)
            self.wait_paced(1.0)
            self.play_paced(Write(transition), run_time=1.2)
            self.wait_paced(1.5)

        self.play_paced(
            FadeOut(VGroup(title, formula, formula_note, colony, question, transition)),
            run_time=1.0,
        )

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

        # Number line intuition: exponents add when bases multiply
        nl_title = Text("Intuition : multiplier = additionner les exposants", font_size=24, color=GRAY)
        nl = NumberLine(x_range=[0, 6, 1], length=8, include_numbers=True, color=BLACK)
        nl_label_b = MathTex(r"a^u = b", font_size=24, color=GREEN_D)
        nl_label_c = MathTex(r"a^v = c", font_size=24, color=ORANGE)
        nl_label_bc = MathTex(r"a^{u+v} = bc", font_size=24, color=RED)

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

        # Intuition: number line
        with self.narrated(
            "L'intuition géométrique : sur une droite des exposants, "
            "multiplier b par c revient à additionner leurs exposants."
        ) as _:
            self.play_paced(
                FadeOut(VGroup(title, prop, box, proof_group)),
                run_time=0.8,
            )

            nl_title.to_edge(UP, buff=0.7)
            nl.move_to(ORIGIN)

            tick_u = nl.n2p(2)
            tick_v = nl.n2p(3)
            tick_uv = nl.n2p(5)

            brace_u = BraceBetweenPoints(nl.n2p(0), tick_u, direction=UP, color=GREEN_D)
            brace_v = BraceBetweenPoints(tick_u, tick_v, direction=UP, color=ORANGE)
            brace_uv = BraceBetweenPoints(nl.n2p(0), tick_uv, direction=DOWN, color=RED)

            nl_label_b.next_to(brace_u, UP, buff=0.1)
            nl_label_c.next_to(brace_v, UP, buff=0.1)
            nl_label_bc.next_to(brace_uv, DOWN, buff=0.1)

            self.play_paced(FadeIn(nl_title), Create(nl), run_time=1.0)
            self.play_paced(Create(brace_u), Write(nl_label_b), run_time=0.7)
            self.play_paced(Create(brace_v), Write(nl_label_c), run_time=0.7)
            self.play_paced(Create(brace_uv), Write(nl_label_bc), run_time=0.7)
            self.wait_paced(1.5)

        self.play_paced(
            FadeOut(VGroup(nl_title, nl, brace_u, brace_v, brace_uv,
                           nl_label_b, nl_label_c, nl_label_bc)),
            run_time=0.9,
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

        # Concrete example
        example_title = Text("Exemple concret :", font_size=32).to_edge(UP, buff=0.6)
        ex_lines = [
            MathTex(r"\log_2(1\,000\,000) = \frac{\log_{10}(1\,000\,000)}{\log_{10}(2)}", font_size=42),
            MathTex(r"= \frac{6}{0.301}", font_size=42),
            MathTex(r"\approx 19.93 \text{ heures}", font_size=42, color=RED),
        ]
        ex_group = VGroup(*ex_lines).arrange(DOWN, buff=0.45)
        ex_group.move_to(ORIGIN + DOWN * 0.3)

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
            "Appliquons ça à notre question initiale. "
            "Logarithme en base deux d'un million, "
            "c'est six divisé par zéro virgule trois zéro un, "
            "soit environ dix-neuf virgule neuf-trois."
        ) as _:
            self.play_paced(FadeIn(example_title), run_time=0.5)
            for line in ex_lines:
                self.play_paced(Write(line), run_time=1.0)
                self.wait_paced(0.5)
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

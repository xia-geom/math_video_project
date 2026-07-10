"""Relations, domaine et image — MAT0339 first roadmap scene.

Production intent
-----------------
A compact worked-example capsule for the first MAT0339 roadmap scene:
relation vs function, domain/codomain/image, interval notation, graph
restrictions, and one common mistake.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

import tools.tts as tts
from tools.branding import play_uqam_intro

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Whiteboard defaults -------------------------------------------------------
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
WARN = RED_D
GOOD = GREEN_D
SOFT = GRAY_D
HL = YELLOW
VOICE_SPEED = 0.82


script = [
    {
        "caption": "Un lien peut être une relation… ou une fonction.",
        "ssml": tts.ssml(
            "Un lien entre deux ensembles peut être une relation… "
            "<bookmark mark='show_relation'/>ou une fonction. "
            "<break time='180ms'/>La différence se voit avec les flèches."
        ),
    },
    {
        "caption": "Fonction : chaque entrée donne une seule sortie.",
        "ssml": tts.ssml(
            "Voici le critère essentiel. "
            "<bookmark mark='bad_input'/>Si une même entrée a deux sorties, "
            "ce n’est pas une fonction. "
            "<bookmark mark='fix_relation'/>Pour une fonction, chaque entrée donne une seule sortie."
        ),
    },
    {
        "caption": "Une fonction s’écrit f : A → B.",
        "ssml": tts.ssml(
            "On résume cela par la notation "
            f"{tts.char('f')} deux-points {tts.char('A')} vers {tts.char('B')}. "
            "<bookmark mark='show_definition'/>Une entrée "
            f"{tts.char('x')} de {tts.char('A')} donne une sortie unique, notée "
            f"{tts.char('f')} de {tts.char('x')}."
        ),
    },
    {
        "caption": "Domaine, codomaine, image : trois rôles différents.",
        "ssml": tts.ssml(
            "Maintenant, séparons trois mots. "
            "<bookmark mark='domain_word'/>Le domaine contient les entrées permises. "
            "<bookmark mark='codomain_word'/>Le codomaine est l’ensemble d’arrivée. "
            "<bookmark mark='image_word'/>L’image contient seulement les sorties réellement atteintes."
        ),
    },
    {
        "caption": "Exemple : f(x)=2x sur {0,1,2,3}.",
        "ssml": tts.ssml(
            "Prenons un exemple fini : "
            f"{tts.char('f')} de {tts.char('x')} égale deux {tts.char('x')}, "
            "avec les entrées zéro, un, deux et trois. "
            "<bookmark mark='map_values'/>On obtient zéro, deux, quatre et six. "
            "<bookmark mark='write_sets'/>On lit alors le domaine et l’image."
        ),
    },
    {
        "caption": "Erreur fréquente : confondre codomaine et image.",
        "ssml": tts.ssml(
            "Attention à l’erreur fréquente. "
            "<bookmark mark='codomain_not_image'/>Le codomaine peut contenir des valeurs qui ne sont jamais atteintes. "
            "Ici, un, trois et cinq sont dans l’ensemble d’arrivée, mais pas dans l’image."
        ),
    },
    {
        "caption": "Sur un graphe, le domaine se lit sur l’axe des x.",
        "ssml": tts.ssml(
            "Sur un graphique, le domaine se lit horizontalement, sur l’axe des "
            f"{tts.char('x')}. <bookmark mark='graph_domain'/>"
            "Pour une fraction, les valeurs interdites apparaissent souvent comme des asymptotes."
        ),
    },
    {
        "caption": "Ici, x=3 est interdit et y=0 n’est jamais atteint.",
        "ssml": tts.ssml(
            "Pour "
            f"{tts.char('g')} de {tts.char('x')} égale un sur {tts.char('x')} moins trois, "
            "<bookmark mark='x_three'/>trois est interdit au domaine. "
            "<bookmark mark='y_zero'/>Et zéro n’est jamais atteint dans l’image. "
            "<bookmark mark='intervals'/>On peut l’écrire avec des intervalles."
        ),
    },
    {
        "caption": "À retenir : une entrée, une sortie; domaine et image.",
        "ssml": tts.ssml(
            "À retenir : <bookmark mark='final_card'/>une fonction, c’est une entrée, une sortie. "
            "Puis on demande : quelles entrées sont permises, et quelles sorties sont obtenues ?"
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class RelationsDomaineImage(VoiceoverScene):
    """First production roadmap scene for MAT0339 function foundations."""

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print(
                "[voiceover] Missing Azure Speech credentials. "
                "Rendering without narration."
            )
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)
        self.set_speech_service(AzureService(voice=tts.VOICE_ID, global_speed=VOICE_SPEED))
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, item: dict[str, str]):
        if self._voiceover_enabled:
            with self.voiceover(text=item["ssml"], subcaption=item["caption"]) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark: str) -> None:
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        # Act 1 — relation vs function.
        title = Text("Relations, fonctions, domaine et image", font_size=46)
        subtitle = Text("MAT0339 — fondations des fonctions", font_size=28, color=SOFT)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.18).to_edge(UP, buff=0.45)

        rel_group, rel = self._relation_diagram()
        rel_group.next_to(title_group, DOWN, buff=0.35)

        with self.narrated(script[0]):
            self.play(Write(title), FadeIn(subtitle, shift=0.15 * DOWN), run_time=1.0)
            self.wait_until_bookmark("show_relation")
            self.play(Create(rel_group["sets"]), run_time=0.8)
            self.play(LaggedStart(*(GrowArrow(a) for a in rel["bad_arrows"]), lag_ratio=0.18), run_time=1.4)
            self.wait(0.4)

        bad_note = VGroup(
            Text("Pas une fonction", font_size=30, color=WARN),
            Text("l’entrée 2 a deux sorties", font_size=25, color=WARN),
        ).arrange(DOWN, buff=0.12).next_to(rel_group, DOWN, buff=0.28)

        with self.narrated(script[1]):
            self.wait_until_bookmark("bad_input")
            self.play(
                Indicate(rel["left_labels"]["2"], color=WARN, scale_factor=1.2),
                Write(bad_note),
                run_time=1.0,
            )
            self.wait_until_bookmark("fix_relation")
            extra_arrow = rel["bad_arrows"][2]
            self.play(
                FadeOut(extra_arrow, shift=0.15 * DOWN),
                FadeOut(bad_note),
                run_time=0.7,
            )
            # Keep the VDict clean so the removed arrow does not reappear on FadeOut.
            rel_group["arrows"].remove(extra_arrow)
            rel["good_arrows"] = rel_group["arrows"]
            good_note = VGroup(
                Text("Fonction", font_size=32, color=GOOD),
                MathTex(r"1\mapsto a,\quad 2\mapsto b,\quad 3\mapsto c", font_size=34, color=BLACK),
            ).arrange(DOWN, buff=0.12).next_to(rel_group, DOWN, buff=0.28)
            self.play(Write(good_note), run_time=0.9)
            self.wait(0.5)

        definition = VGroup(
            MathTex(r"f:A\to B", font_size=52),
            MathTex(r"x\in A\quad\longmapsto\quad f(x)\in B", font_size=42),
            Text("une seule image pour chaque entrée", font_size=28),
        ).arrange(DOWN, buff=0.25).move_to(ORIGIN)

        with self.narrated(script[2]):
            self.play(FadeOut(rel_group), FadeOut(good_note), run_time=0.7)
            self.wait_until_bookmark("show_definition")
            self.play(Write(definition[0]), run_time=0.7)
            self.play(Write(definition[1]), run_time=0.8)
            self.play(FadeIn(definition[2], shift=0.2 * UP), run_time=0.5)
            self.wait(0.5)

        # Act 2 — domain, codomain, image on a finite example.
        words = self._three_word_cards()
        words.to_edge(UP, buff=0.55)

        with self.narrated(script[3]):
            self.play(FadeOut(definition), FadeOut(title_group), run_time=0.5)
            self.wait_until_bookmark("domain_word")
            self.play(FadeIn(words[0], shift=0.2 * UP), run_time=0.55)
            self.wait_until_bookmark("codomain_word")
            self.play(FadeIn(words[1], shift=0.2 * UP), run_time=0.55)
            self.wait_until_bookmark("image_word")
            self.play(FadeIn(words[2], shift=0.2 * UP), run_time=0.55)
            self.wait(0.4)

        finite_group, finite = self._finite_function_diagram()
        finite_group.next_to(words, DOWN, buff=0.25)
        set_lines = VGroup(
            MathTex(r"\mathrm{Dom}(f)=\{0,1,2,3\}", font_size=34),
            MathTex(r"\mathrm{Im}(f)=\{0,2,4,6\}", font_size=34),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_edge(DOWN, buff=0.48)

        with self.narrated(script[4]):
            self.play(FadeIn(finite_group["sets"], shift=0.15 * UP), Write(finite_group["formula"]), run_time=0.9)
            self.wait_until_bookmark("map_values")
            self.play(LaggedStart(*(GrowArrow(a) for a in finite["arrows"]), lag_ratio=0.12), run_time=1.4)
            self.wait_until_bookmark("write_sets")
            self.play(Write(set_lines), run_time=1.0)
            self.wait(0.4)

        missed = VGroup(
            finite["right_labels"]["1"],
            finite["right_labels"]["3"],
            finite["right_labels"]["5"],
        )
        codomain_mistake = VGroup(
            Text("Codomaine", font_size=28),
            MathTex(r"\{0,1,2,3,4,5,6\}", font_size=32),
            Text("≠ image", font_size=32, color=WARN),
        ).arrange(DOWN, buff=0.12).to_corner(DR, buff=0.6)

        with self.narrated(script[5]):
            self.wait_until_bookmark("codomain_not_image")
            self.play(Write(codomain_mistake), run_time=0.8)
            self.play(LaggedStart(*(Indicate(m, color=WARN, scale_factor=1.25) for m in missed), lag_ratio=0.18), run_time=1.5)
            self.wait(0.5)

        # Act 3 — read domain and image on a graph with restrictions.
        graph_title = VGroup(
            Text("Lire le domaine et l’image sur un graphe", font_size=36),
            MathTex(r"g(x)=\frac{1}{x-3}", font_size=42),
        ).arrange(DOWN, buff=0.15).to_edge(UP, buff=0.45)
        graph_group = self._rational_graph()
        graph_group.move_to(0.25 * DOWN)

        with self.narrated(script[6]):
            self.play(
                FadeOut(words),
                FadeOut(finite_group),
                FadeOut(set_lines),
                FadeOut(codomain_mistake),
                run_time=0.7,
            )
            self.play(Write(graph_title), run_time=0.75)
            self.wait_until_bookmark("graph_domain")
            self.play(Create(graph_group["axes"]), run_time=0.8)
            self.play(Create(graph_group["curve_left"]), Create(graph_group["curve_right"]), run_time=1.2)
            self.wait(0.4)

        domain_interval = MathTex(
            r"\mathrm{Dom}(g)=]-\infty,3[\,\cup\,]3,+\infty[",
            font_size=34,
        )
        image_interval = MathTex(
            r"\mathrm{Im}(g)=]-\infty,0[\,\cup\,]0,+\infty[",
            font_size=34,
        )
        interval_group = VGroup(domain_interval, image_interval).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        interval_group.to_edge(DOWN, buff=0.45)

        with self.narrated(script[7]):
            self.wait_until_bookmark("x_three")
            self.play(Create(graph_group["vertical_asymptote"]), Write(graph_group["x3_label"]), run_time=0.8)
            self.play(Indicate(graph_group["x3_label"], color=WARN), run_time=0.6)
            self.wait_until_bookmark("y_zero")
            self.play(Create(graph_group["horizontal_asymptote"]), Write(graph_group["y0_label"]), run_time=0.8)
            self.play(Indicate(graph_group["y0_label"], color=WARN), run_time=0.6)
            self.wait_until_bookmark("intervals")
            self.play(Write(interval_group), run_time=1.0)
            self.wait(0.4)

        final_card = self._final_card()

        with self.narrated(script[8]):
            self.play(FadeOut(graph_group), FadeOut(graph_title), FadeOut(interval_group), run_time=0.7)
            self.wait_until_bookmark("final_card")
            self.play(FadeIn(final_card, shift=0.2 * UP), run_time=0.8)
            self.wait(1.0)

    # ------------------------------------------------------------------
    # Visual helpers
    # ------------------------------------------------------------------
    def _relation_diagram(self):
        left_values = ["1", "2", "3"]
        right_values = ["a", "b", "c"]
        left, left_labels = self._value_column("A", left_values, x=-3.25, y_top=1.2)
        right, right_labels = self._value_column("B", right_values, x=3.25, y_top=1.2, label_side=RIGHT)

        arrow_specs = [("1", "a", BLACK), ("2", "b", BLACK), ("2", "c", WARN), ("3", "c", BLACK)]
        arrows = VGroup(
            *[
                Arrow(
                    left_labels[src].get_center() + 0.22 * RIGHT,
                    right_labels[dst].get_center() + 0.22 * LEFT,
                    buff=0.16,
                    color=color,
                    stroke_width=2.8,
                    max_tip_length_to_length_ratio=0.08,
                )
                for src, dst, color in arrow_specs
            ]
        )

        sets = VGroup(left, right)
        group = VDict({"sets": sets, "arrows": arrows})
        data = {
            "left_labels": left_labels,
            "right_labels": right_labels,
            "bad_arrows": arrows,
        }
        return group, data

    def _finite_function_diagram(self):
        left_values = ["0", "1", "2", "3"]
        right_values = ["0", "1", "2", "3", "4", "5", "6"]
        left, left_labels = self._value_column("A", left_values, x=-4.25, y_top=1.2, y_step=0.55)
        right, right_labels = self._value_column("B", right_values, x=2.85, y_top=1.75, y_step=0.47, label_side=RIGHT)

        formula = MathTex(r"f(x)=2x", font_size=42).move_to([0.0, 2.25, 0])
        arrows = VGroup(
            *[
                Arrow(
                    left_labels[src].get_center() + 0.22 * RIGHT,
                    right_labels[dst].get_center() + 0.22 * LEFT,
                    buff=0.18,
                    color=ACCENT,
                    stroke_width=2.7,
                    max_tip_length_to_length_ratio=0.075,
                )
                for src, dst in [("0", "0"), ("1", "2"), ("2", "4"), ("3", "6")]
            ]
        )
        sets = VGroup(left, right)
        group = VDict({"sets": sets, "formula": formula, "arrows": arrows})
        data = {"left_labels": left_labels, "right_labels": right_labels, "arrows": arrows}
        return group, data

    def _value_column(
        self,
        title: str,
        values: list[str],
        x: float,
        y_top: float,
        y_step: float = 0.72,
        label_side=LEFT,
    ):
        dots = VGroup()
        labels = {}
        tex_labels = VGroup()
        for i, value in enumerate(values):
            y = y_top - i * y_step
            dot = Dot([x, y, 0], radius=0.055, color=BLACK)
            label = MathTex(value, font_size=32).next_to(dot, label_side, buff=0.15)
            dots.add(dot)
            tex_labels.add(label)
            labels[value] = label

        contents = VGroup(dots, tex_labels)
        ellipse = Ellipse(
            width=1.45 if len(values) <= 4 else 1.65,
            height=max(2.4, y_step * (len(values) - 1) + 1.2),
            color=BLACK,
            stroke_width=2.4,
        ).move_to(contents)
        title_label = MathTex(title, font_size=38).next_to(ellipse, UP, buff=0.1)
        return VGroup(ellipse, title_label, dots, tex_labels), labels

    def _three_word_cards(self) -> VGroup:
        content = [
            ("Domaine", "entrées permises"),
            ("Codomaine", "ensemble d’arrivée"),
            ("Image", "sorties atteintes"),
        ]
        cards = VGroup()
        for header, body in content:
            h = Text(header, font_size=31)
            b = Text(body, font_size=23, color=SOFT)
            txt = VGroup(h, b).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(width=3.7, height=1.25, corner_radius=0.18, color=BLACK, stroke_width=2)
            card = VGroup(box, txt)
            cards.add(card)
        cards.arrange(RIGHT, buff=0.35)
        return cards

    def _rational_graph(self) -> VDict:
        axes = Axes(
            x_range=[-1, 7, 1],
            y_range=[-4, 4, 1],
            x_length=7.0,
            y_length=4.3,
            tips=True,
            axis_config={"color": BLACK, "stroke_width": 2.2, "include_numbers": False},
        )
        x_label = MathTex("x", font_size=28).next_to(axes.x_axis, RIGHT, buff=0.12)
        y_label = MathTex("y", font_size=28).next_to(axes.y_axis, UP, buff=0.12)
        axes_group = VGroup(axes, x_label, y_label)

        curve_left = axes.plot(lambda x: 1 / (x - 3), x_range=[-1, 2.72, 0.02], color=ACCENT, stroke_width=3)
        curve_right = axes.plot(lambda x: 1 / (x - 3), x_range=[3.28, 7, 0.02], color=ACCENT, stroke_width=3)

        vertical_asymptote = DashedLine(axes.c2p(3, -4), axes.c2p(3, 4), color=WARN, stroke_width=2.4)
        horizontal_asymptote = DashedLine(axes.c2p(-1, 0), axes.c2p(7, 0), color=WARN, stroke_width=2.0)
        x3_label = MathTex("x=3", font_size=31, color=WARN).next_to(vertical_asymptote, UP, buff=0.08)
        y0_label = MathTex("y=0", font_size=31, color=WARN).next_to(horizontal_asymptote, DOWN, buff=0.08).shift(2.45 * RIGHT)

        return VDict(
            {
                "axes": axes_group,
                "curve_left": curve_left,
                "curve_right": curve_right,
                "vertical_asymptote": vertical_asymptote,
                "horizontal_asymptote": horizontal_asymptote,
                "x3_label": x3_label,
                "y0_label": y0_label,
            }
        )

    def _final_card(self) -> VGroup:
        title = Text("À retenir", font_size=42)
        one = VGroup(
            MathTex(r"x\in\mathrm{Dom}(f)", font_size=38),
            MathTex(r"\longmapsto", font_size=38),
            MathTex(r"f(x)\in\mathrm{Im}(f)", font_size=38),
        ).arrange(RIGHT, buff=0.35)
        bullets = VGroup(
            Text("1. Une relation peut ne pas être une fonction.", font_size=28),
            Text("2. Une fonction donne une seule sortie par entrée.", font_size=28),
            Text("3. L’image est la partie du codomaine vraiment atteinte.", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        card_text = VGroup(title, one, bullets).arrange(DOWN, buff=0.38)
        box = RoundedRectangle(width=11.7, height=5.0, corner_radius=0.22, color=BLACK, stroke_width=2.4)
        return VGroup(box, card_text).move_to(ORIGIN)

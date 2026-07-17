from __future__ import annotations

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


# -----------------------------------------------------------------------------
# Global visual style
# -----------------------------------------------------------------------------
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
FORBIDDEN = RED_D
MUTED = GRAY_C
PALE = GRAY_E


# -----------------------------------------------------------------------------
# Narration
# Captions are deliberately short; SSML carries pauses and bookmarks.
# -----------------------------------------------------------------------------
SCRIPT = [
    {
        "caption": "Le domaine est l’ensemble des entrées acceptées.",
        "ssml": tts.ssml(
            "Une fonction n'accepte pas toujours tous les nombres. "
            "<bookmark mark='gate'/>Son domaine est l'ensemble des entrées qu'elle peut réellement accepter."
        ),
    },
    {
        "caption": "Un polynôme accepte tous les nombres réels.",
        "ssml": tts.ssml(
            "Commençons par un polynôme. <bookmark mark='poly'/>Pour "
            "<say-as interpret-as='characters'>f</say-as> de <say-as interpret-as='characters'>x</say-as> "
            "égal à <say-as interpret-as='characters'>x</say-as> au carré moins trois "
            "<say-as interpret-as='characters'>x</say-as> plus un, chaque nombre réel donne un résultat. "
            "<bookmark mark='poly_domain'/>Le domaine est donc l'ensemble des réels."
        ),
    },
    {
        "caption": "Une fraction refuse les zéros du dénominateur.",
        "ssml": tts.ssml(
            "Avec une fraction, il faut regarder le dénominateur. "
            "<bookmark mark='frac_formula'/>Ici, deux est interdit, car le dénominateur devient zéro. "
            "<bookmark mark='reject_two'/>La machine refuse cette entrée."
        ),
    },
    {
        "caption": "On retire les valeurs qui annulent le dénominateur.",
        "ssml": tts.ssml(
            "Sur la droite numérique, on garde tous les réels sauf deux. "
            "<bookmark mark='frac_line'/>Le cercle vide indique que deux n'appartient pas au domaine. "
            "<bookmark mark='frac_graph'/>Sur le graphique, la courbe n'existe pas au-dessus de cette valeur."
        ),
    },
    {
        "caption": "Le dénominateur peut exclure plusieurs valeurs.",
        "ssml": tts.ssml(
            "Il peut y avoir plusieurs valeurs interdites. "
            "<bookmark mark='factor_den'/>En factorisant <say-as interpret-as='characters'>x</say-as> carré moins neuf, "
            "on trouve moins trois et trois. <bookmark mark='two_holes'/>On retire donc ces deux points."
        ),
    },
    {
        "caption": "Sous une racine carrée, il faut une quantité positive ou nulle.",
        "ssml": tts.ssml(
            "Pour une racine carrée, la quantité sous la racine doit être positive ou nulle. "
            "<bookmark mark='root_right'/>La racine de <say-as interpret-as='characters'>x</say-as> moins trois accepte les nombres à partir de trois. "
            "<bookmark mark='root_left'/>Mais la racine de cinq moins <say-as interpret-as='characters'>x</say-as> accepte les nombres jusqu'à cinq."
        ),
    },
    {
        "caption": "Un domaine peut être formé de deux intervalles.",
        "ssml": tts.ssml(
            "Le domaine n'est pas toujours un seul intervalle. "
            "<bookmark mark='root_quad'/>Pour la racine de <say-as interpret-as='characters'>x</say-as> carré moins quatre, "
            "le produit est positif ou nul à l'extérieur des deux racines. "
            "<bookmark mark='root_quad_domain'/>On obtient deux morceaux séparés."
        ),
    },
    {
        "caption": "Le domaine donne l’étendue horizontale du graphique.",
        "ssml": tts.ssml(
            "Le domaine se voit aussi sur le graphique. "
            "<bookmark mark='semicircle_domain'/>Pour la racine de quatre moins <say-as interpret-as='characters'>x</say-as> carré, "
            "on doit rester entre moins deux et deux. "
            "<bookmark mark='semicircle_graph'/>La courbe est exactement le demi-cercle supérieur sur cet intervalle."
        ),
    },
    {
        "caption": "Dans un dénominateur, la racine doit être strictement positive.",
        "ssml": tts.ssml(
            "Attention à la position de la racine. "
            "<bookmark mark='compare_roots'/>La racine de <say-as interpret-as='characters'>x</say-as> moins un accepte un. "
            "Mais si cette racine est au dénominateur, <bookmark mark='open_endpoint'/>un devient interdit. "
            "La condition passe de supérieur ou égal à zéro à strictement supérieur à zéro."
        ),
    },
    {
        "caption": "Un logarithme exige un argument strictement positif.",
        "ssml": tts.ssml(
            "Pour un logarithme, l'argument doit être strictement positif. "
            "<bookmark mark='log_compare'/>Ainsi, la racine de <say-as interpret-as='characters'>x</say-as> carré moins un garde les extrémités, "
            "tandis que le logarithme les retire."
        ),
    },
    {
        "caption": "Avec plusieurs contraintes, on prend leur intersection.",
        "ssml": tts.ssml(
            "Quand plusieurs difficultés apparaissent, on traite chaque contrainte séparément. "
            "<bookmark mark='constraint_root'/>La racine impose <say-as interpret-as='characters'>x</say-as> supérieur ou égal à moins un. "
            "<bookmark mark='constraint_den'/>Le dénominateur retire deux. "
            "<bookmark mark='constraint_intersection'/>Le domaine est l'intersection des deux conditions."
        ),
    },
    {
        "caption": "Parfois, il faut étudier le signe d’un quotient.",
        "ssml": tts.ssml(
            "Voici un exemple plus riche. "
            "<bookmark mark='quotient_root'/>Toute la fraction sous la racine doit être positive ou nulle. "
            "Les valeurs critiques sont moins deux et un. "
            "<bookmark mark='signs'/>Le tableau de signes montre les intervalles acceptés."
        ),
    },
    {
        "caption": "Simplifier une formule ne récupère pas une entrée interdite.",
        "ssml": tts.ssml(
            "Dernier piège. <bookmark mark='cancel'/>On peut simplifier la fraction en "
            "<say-as interpret-as='characters'>x</say-as> plus deux, mais la fonction de départ restait interdite en deux. "
            "<bookmark mark='hole_graph'/>Le graphique est donc une droite avec un trou."
        ),
    },
    {
        "caption": "Repérez d’abord les parties qui imposent une condition.",
        "ssml": tts.ssml(
            "Pour trouver un domaine, commencez par scanner la formule. "
            "<bookmark mark='scan_den'/>Un dénominateur ne vaut jamais zéro. "
            "<bookmark mark='scan_root'/>Sous une racine carrée, la quantité est positive ou nulle. "
            "<bookmark mark='scan_log'/>Dans un logarithme, elle est strictement positive. "
            "Puis, s'il y a plusieurs conditions, prenez leur intersection."
        ),
    },
]


# -----------------------------------------------------------------------------
# Small visual helpers
# -----------------------------------------------------------------------------
def make_caption(text: str) -> VGroup:
    caption = Text(text, font_size=27, line_spacing=0.85)
    if caption.width > 12.4:
        caption.scale_to_fit_width(12.4)
    box = RoundedRectangle(
        width=max(5.0, caption.width + 0.48),
        height=caption.height + 0.30,
        corner_radius=0.09,
        stroke_color=BLACK,
        stroke_width=1.4,
        fill_color=WHITE,
        fill_opacity=0.96,
    )
    group = VGroup(box, caption)
    group.move_to([0, -3.52, 0])
    return group


def make_machine(label: str = "f") -> VGroup:
    body = RoundedRectangle(
        width=2.55,
        height=1.65,
        corner_radius=0.16,
        stroke_color=BLACK,
        stroke_width=3,
        fill_color=ACCENT,
        fill_opacity=0.08,
    )
    name = MathTex(label, font_size=52).move_to(body)
    left_arrow = Arrow(LEFT * 2.15, LEFT * 1.32, buff=0, color=BLACK, stroke_width=3)
    right_arrow = Arrow(RIGHT * 1.32, RIGHT * 2.15, buff=0, color=BLACK, stroke_width=3)
    input_label = Text("entrée", font_size=23).next_to(left_arrow, UP, buff=0.08)
    output_label = Text("sortie", font_size=23).next_to(right_arrow, UP, buff=0.08)
    return VGroup(body, name, left_arrow, right_arrow, input_label, output_label)


def make_token(tex: str, color: ManimColor = BLACK) -> VGroup:
    circle = Circle(
        radius=0.38,
        stroke_color=color,
        stroke_width=2.5,
        fill_color=WHITE,
        fill_opacity=1,
    )
    label = MathTex(tex, font_size=34, color=color)
    return VGroup(circle, label)


def make_number_line(
    x_min: float,
    x_max: float,
    segments: list[tuple[float | None, float | None]],
    *,
    open_points: tuple[float, ...] = (),
    closed_points: tuple[float, ...] = (),
    length: float = 8.4,
    include_numbers: bool = True,
    step: float = 1,
) -> VGroup:
    line = NumberLine(
        x_range=[x_min, x_max, step],
        length=length,
        include_numbers=include_numbers,
        include_tip=True,
        color=BLACK,
        stroke_width=2.2,
        font_size=25,
        decimal_number_config={"num_decimal_places": 0},
    )

    accepted = VGroup()
    epsilon = (x_max - x_min) * 0.012
    for left, right in segments:
        a = x_min + epsilon if left is None else left
        b = x_max - epsilon if right is None else right
        accepted.add(
            Line(
                line.n2p(a),
                line.n2p(b),
                color=ACCENT,
                stroke_width=8,
            )
        )

    points = VGroup()
    for value in closed_points:
        points.add(Dot(line.n2p(value), radius=0.095, color=ACCENT))
    for value in open_points:
        points.add(
            Circle(
                radius=0.105,
                stroke_color=ACCENT,
                stroke_width=3,
                fill_color=WHITE,
                fill_opacity=1,
            ).move_to(line.n2p(value))
        )

    return VGroup(line, accepted, points)


def make_reasoning(formula: str, condition: str, domain: str) -> VGroup:
    formula_mob = MathTex(formula, font_size=48)
    condition_label = Text("condition", font_size=23, color=MUTED)
    condition_mob = MathTex(condition, font_size=42)
    domain_label = Text("domaine", font_size=23, color=MUTED)
    domain_mob = MathTex(domain, font_size=42, color=ACCENT)

    condition_group = VGroup(condition_label, condition_mob).arrange(DOWN, buff=0.08)
    domain_group = VGroup(domain_label, domain_mob).arrange(DOWN, buff=0.08)

    arrow_1 = Arrow(DOWN * 0.05, DOWN * 0.55, buff=0, color=BLACK, stroke_width=2.5)
    arrow_2 = Arrow(DOWN * 0.05, DOWN * 0.55, buff=0, color=BLACK, stroke_width=2.5)

    return VGroup(formula_mob, arrow_1, condition_group, arrow_2, domain_group).arrange(
        DOWN, buff=0.18
    )


def section_title(text: str) -> Text:
    return Text(text, font_size=33, weight=SEMIBOLD).to_edge(UP, buff=0.32)


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class DomaineFonctionFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    """Domain of a function, built around accepted and rejected inputs."""

    def _setup_voiceover(self) -> None:
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
    def narrated(self, item: dict[str, str]):
        if self._voiceover_enabled:
            with self.voiceover(text=item["ssml"], subcaption=item["caption"]) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark: str) -> None:
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)

    def set_caption(self, text: str, *, animate: bool = True) -> None:
        new_caption = make_caption(text)
        if self.caption_mob is None:
            if animate:
                self.play(FadeIn(new_caption), run_time=0.3)
            else:
                self.add(new_caption)
        else:
            if animate:
                self.play(ReplacementTransform(self.caption_mob, new_caption), run_time=0.3)
            else:
                self.remove(self.caption_mob)
                self.add(new_caption)
        self.caption_mob = new_caption

    def accepted_test(
        self,
        machine: VGroup,
        input_tex: str,
        output_tex: str,
        *,
        run_time: float = 0.75,
    ) -> None:
        token_in = make_token(input_tex).move_to(machine.get_left() + LEFT * 1.30)
        token_out = make_token(output_tex, ACCENT).move_to(machine.get_right() + RIGHT * 1.30)
        self.play(FadeIn(token_in, shift=RIGHT * 0.25), run_time=0.35)
        self.play(token_in.animate.move_to(machine.get_center()), run_time=run_time)
        self.play(
            FadeOut(token_in, scale=0.7),
            FadeIn(token_out, shift=RIGHT * 0.35),
            run_time=0.45,
        )
        self.play(FadeOut(token_out, shift=RIGHT * 0.35), run_time=0.35)

    def rejected_test(self, machine: VGroup, input_tex: str) -> None:
        token = make_token(input_tex, FORBIDDEN).move_to(machine.get_left() + LEFT * 1.30)
        cross = Cross(token, stroke_color=FORBIDDEN, stroke_width=5).scale(1.15)
        warning = Text("non défini", font_size=27, color=FORBIDDEN).next_to(machine, DOWN, buff=0.18)
        self.play(FadeIn(token, shift=RIGHT * 0.25), run_time=0.35)
        self.play(token.animate.move_to(machine.get_left() + LEFT * 0.44), run_time=0.7)
        cross.move_to(token)
        self.play(Create(cross), Wiggle(machine[0], scale_value=1.04), FadeIn(warning), run_time=0.65)
        self.play(FadeOut(VGroup(token, cross, warning)), run_time=0.45)

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.caption_mob: VGroup | None = None

        self._setup_voiceover()
        play_uqam_intro(self)

        # ------------------------------------------------------------------
        # ACT 1 — Meaning of the domain
        # ------------------------------------------------------------------
        title = Text("Le domaine d’une fonction", font_size=48, weight=SEMIBOLD)
        subtitle = Text("Quelles entrées la formule accepte-t-elle ?", font_size=31)
        intro_group = VGroup(title, subtitle).arrange(DOWN, buff=0.22).shift(UP * 1.95)
        machine = make_machine("f").shift(DOWN * 0.15)

        item = SCRIPT[0]
        with self.narrated(item):
            self.set_caption(item["caption"], animate=False)
            self.play(Write(title), FadeIn(subtitle, shift=UP * 0.15), run_time=1.0)
            self.wait_until_bookmark("gate")
            self.play(Create(machine[0]), Write(machine[1]), GrowArrow(machine[2]), GrowArrow(machine[3]))
            self.play(FadeIn(machine[4:]), run_time=0.45)
            sample_inputs = VGroup(*[make_token(tex) for tex in (r"-2", r"0", r"3")])
            sample_inputs.arrange(DOWN, buff=0.16).next_to(machine, LEFT, buff=1.15)
            self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.15) for t in sample_inputs], lag_ratio=0.18))
            self.play(FadeOut(sample_inputs), run_time=0.45)

        self.play(FadeOut(intro_group), machine.animate.shift(UP * 0.55), run_time=0.6)

        # ------------------------------------------------------------------
        # ACT 2 — Polynomial: every real number is allowed
        # ------------------------------------------------------------------
        heading = section_title("1. Aucun interdit")
        formula = MathTex(r"f(x)=x^2-3x+1", font_size=48).next_to(heading, DOWN, buff=0.32)

        item = SCRIPT[1]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), Write(formula), run_time=0.8)
            self.wait_until_bookmark("poly")
            self.accepted_test(machine, r"-2", r"11")
            self.accepted_test(machine, r"0", r"1")
            self.accepted_test(machine, r"3", r"1")
            self.wait_until_bookmark("poly_domain")
            poly_line = make_number_line(-5, 5, [(None, None)], length=8.2).shift(DOWN * 1.52)
            domain_poly = MathTex(r"\operatorname{Dom}(f)=\mathbb{R}", font_size=43, color=ACCENT)
            domain_poly.next_to(poly_line, UP, buff=0.23)
            self.play(Create(poly_line[0]), Create(poly_line[1]), FadeIn(domain_poly), run_time=1.0)

        self.play(FadeOut(VGroup(heading, formula, poly_line, domain_poly, machine)), run_time=0.7)

        # ------------------------------------------------------------------
        # ACT 3 — A denominator excludes one value
        # ------------------------------------------------------------------
        heading = section_title("2. Le dénominateur ne peut pas être nul")
        machine = make_machine("g").shift(RIGHT * 2.45 + DOWN * 0.05)
        reasoning = make_reasoning(
            r"g(x)=\frac{1}{x-2}",
            r"x-2\neq 0",
            r"\mathbb{R}\setminus\{2\}",
        ).scale(0.90).shift(LEFT * 2.85 + UP * 0.05)

        item = SCRIPT[2]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), FadeIn(machine), run_time=0.75)
            self.wait_until_bookmark("frac_formula")
            self.play(Write(reasoning[0]), run_time=0.75)
            self.accepted_test(machine, r"0", r"-\frac12")
            self.accepted_test(machine, r"3", r"1")
            self.wait_until_bookmark("reject_two")
            self.rejected_test(machine, r"2")
            self.play(
                GrowArrow(reasoning[1]),
                FadeIn(reasoning[2]),
                GrowArrow(reasoning[3]),
                FadeIn(reasoning[4]),
                run_time=1.0,
            )

        item = SCRIPT[3]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.wait_until_bookmark("frac_line")
            frac_line = make_number_line(-4, 6, [(None, 2), (2, None)], open_points=(2,), length=8.5)
            frac_line.shift(DOWN * 1.64)
            x2_label = MathTex(r"x=2", font_size=30, color=FORBIDDEN).next_to(frac_line[2], UP, buff=0.12)
            self.play(Create(frac_line[0]), Create(frac_line[1]), FadeIn(frac_line[2]), FadeIn(x2_label), run_time=1.0)

            self.wait_until_bookmark("frac_graph")
            axes = Axes(
                x_range=[-3, 6, 1],
                y_range=[-4, 4, 1],
                x_length=5.2,
                y_length=4.2,
                axis_config={"color": BLACK, "stroke_width": 2},
                tips=False,
            ).scale(0.78).shift(RIGHT * 3.8 + DOWN * 0.15)
            graph_left = axes.plot(lambda x: 1 / (x - 2), x_range=[-3, 1.82], color=ACCENT)
            graph_right = axes.plot(lambda x: 1 / (x - 2), x_range=[2.18, 6], color=ACCENT)
            asymptote = DashedLine(
                axes.c2p(2, -4), axes.c2p(2, 4), color=FORBIDDEN, dash_length=0.10
            )
            graph_label = MathTex(r"y=\frac1{x-2}", font_size=31).next_to(axes, UP, buff=0.06)
            left_group = VGroup(reasoning, machine).animate.scale(0.82).shift(LEFT * 1.15)
            self.play(left_group, frac_line.animate.scale(0.78).shift(LEFT * 2.6), run_time=0.8)
            self.play(Create(axes), Create(asymptote), Create(graph_left), Create(graph_right), FadeIn(graph_label), run_time=1.4)

        act3 = VGroup(heading, reasoning, machine, frac_line, x2_label, axes, graph_left, graph_right, asymptote, graph_label)
        self.play(FadeOut(act3), run_time=0.75)

        # ------------------------------------------------------------------
        # ACT 4 — Several denominator zeros
        # ------------------------------------------------------------------
        heading = section_title("3. Plusieurs valeurs interdites")
        eq1 = MathTex(r"h(x)=\frac{x+1}{x^2-9}", font_size=47).shift(UP * 1.75)
        eq2 = MathTex(r"x^2-9=(x-3)(x+3)", font_size=43).next_to(eq1, DOWN, buff=0.35)
        eq3 = MathTex(r"x\neq -3\quad\text{et}\quad x\neq 3", font_size=41).next_to(eq2, DOWN, buff=0.30)
        multi_line = make_number_line(
            -6,
            6,
            [(None, -3), (-3, 3), (3, None)],
            open_points=(-3, 3),
            length=9.0,
        ).shift(DOWN * 1.35)
        multi_domain = MathTex(
            r"\operatorname{Dom}(h)=\mathbb{R}\setminus\{-3,3\}",
            font_size=40,
            color=ACCENT,
        ).next_to(multi_line, UP, buff=0.18)

        item = SCRIPT[4]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), Write(eq1), run_time=0.75)
            self.wait_until_bookmark("factor_den")
            self.play(TransformMatchingTex(eq1.copy(), eq2), run_time=1.0)
            self.play(Write(eq3), run_time=0.7)
            self.wait_until_bookmark("two_holes")
            self.play(Create(multi_line[0]), Create(multi_line[1]), FadeIn(multi_line[2]), FadeIn(multi_domain), run_time=1.2)

        self.play(FadeOut(VGroup(heading, eq1, eq2, eq3, multi_line, multi_domain)), run_time=0.7)

        # ------------------------------------------------------------------
        # ACT 5 — Simple square-root domains, shown as a comparison pair
        # ------------------------------------------------------------------
        heading = section_title("4. La racine carrée crée une frontière")
        left_formula = MathTex(r"p(x)=\sqrt{x-3}", font_size=44)
        left_condition = MathTex(r"x-3\geq0\iff x\geq3", font_size=36)
        left_line = make_number_line(-2, 8, [(3, None)], closed_points=(3,), length=5.0)
        left_domain = MathTex(r"[3,+\infty[", font_size=38, color=ACCENT)
        left_group = VGroup(left_formula, left_condition, left_line, left_domain).arrange(DOWN, buff=0.23)
        left_group.shift(LEFT * 3.45 + DOWN * 0.05)

        right_formula = MathTex(r"q(x)=\sqrt{5-x}", font_size=44)
        right_condition = MathTex(r"5-x\geq0\iff x\leq5", font_size=36)
        right_line = make_number_line(-2, 8, [(None, 5)], closed_points=(5,), length=5.0)
        right_domain = MathTex(r"]-\infty,5]", font_size=38, color=ACCENT)
        right_group = VGroup(right_formula, right_condition, right_line, right_domain).arrange(DOWN, buff=0.23)
        right_group.shift(RIGHT * 3.45 + DOWN * 0.05)

        divider = Line(UP * 2.2, DOWN * 2.25, color=PALE, stroke_width=2)

        item = SCRIPT[5]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), Create(divider), run_time=0.6)
            self.wait_until_bookmark("root_right")
            self.play(Write(left_formula), Write(left_condition), run_time=0.9)
            self.play(Create(left_line[0]), Create(left_line[1]), FadeIn(left_line[2]), FadeIn(left_domain), run_time=0.9)
            self.wait_until_bookmark("root_left")
            self.play(Write(right_formula), Write(right_condition), run_time=0.9)
            self.play(Create(right_line[0]), Create(right_line[1]), FadeIn(right_line[2]), FadeIn(right_domain), run_time=0.9)

        self.play(FadeOut(VGroup(heading, left_group, right_group, divider)), run_time=0.7)

        # ------------------------------------------------------------------
        # ACT 6 — Disconnected domain from a quadratic radicand
        # ------------------------------------------------------------------
        heading = section_title("5. Un domaine en plusieurs morceaux")
        formula = MathTex(r"r(x)=\sqrt{x^2-4}", font_size=48).shift(UP * 1.85)
        factor = MathTex(r"x^2-4=(x-2)(x+2)", font_size=42).next_to(formula, DOWN, buff=0.30)

        sign_line = NumberLine(
            x_range=[-5, 5, 1],
            length=8.6,
            include_numbers=True,
            include_tip=True,
            color=BLACK,
            font_size=25,
        ).shift(DOWN * 0.25)
        signs = VGroup(
            MathTex("+", color=ACCENT).move_to(sign_line.n2p(-3.4) + UP * 0.44),
            MathTex("-", color=FORBIDDEN).move_to(sign_line.n2p(0) + UP * 0.44),
            MathTex("+", color=ACCENT).move_to(sign_line.n2p(3.4) + UP * 0.44),
        )
        criticals = VGroup(
            DashedLine(sign_line.n2p(-2) + DOWN * 0.23, sign_line.n2p(-2) + UP * 0.72, color=MUTED),
            DashedLine(sign_line.n2p(2) + DOWN * 0.23, sign_line.n2p(2) + UP * 0.72, color=MUTED),
        )
        root_quad_line = make_number_line(
            -5,
            5,
            [(None, -2), (2, None)],
            closed_points=(-2, 2),
            length=8.6,
        ).shift(DOWN * 1.55)
        root_quad_domain = MathTex(
            r"]-\infty,-2]\cup[2,+\infty[",
            font_size=41,
            color=ACCENT,
        ).next_to(root_quad_line, UP, buff=0.17)

        item = SCRIPT[6]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), Write(formula), run_time=0.75)
            self.wait_until_bookmark("root_quad")
            self.play(Write(factor), Create(sign_line), Create(criticals), FadeIn(signs), run_time=1.2)
            self.wait_until_bookmark("root_quad_domain")
            self.play(Create(root_quad_line[0]), Create(root_quad_line[1]), FadeIn(root_quad_line[2]), FadeIn(root_quad_domain), run_time=1.1)

        self.play(FadeOut(VGroup(heading, formula, factor, sign_line, signs, criticals, root_quad_line, root_quad_domain)), run_time=0.7)

        # ------------------------------------------------------------------
        # ACT 7 — Domain as horizontal extent of a graph
        # ------------------------------------------------------------------
        heading = section_title("6. Le domaine se lit aussi sur le graphique")
        formula = MathTex(r"s(x)=\sqrt{4-x^2}", font_size=47).shift(LEFT * 3.45 + UP * 1.55)
        condition = MathTex(r"4-x^2\geq0\iff -2\leq x\leq2", font_size=38)
        condition.next_to(formula, DOWN, buff=0.32)
        semi_line = make_number_line(-3, 3, [(-2, 2)], closed_points=(-2, 2), length=5.1)
        semi_line.next_to(condition, DOWN, buff=0.40)
        semi_domain = MathTex(r"\operatorname{Dom}(s)=[-2,2]", font_size=40, color=ACCENT)
        semi_domain.next_to(semi_line, DOWN, buff=0.32)

        # Equal scale on both axes: one horizontal unit equals one vertical unit.
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 3, 1],
            x_length=5.4,
            y_length=3.6,
            axis_config={"color": BLACK, "stroke_width": 2},
            tips=False,
        ).shift(RIGHT * 3.35 + DOWN * 0.05)
        semicircle = axes.plot(lambda x: (4 - x**2) ** 0.5, x_range=[-2, 2], color=ACCENT)
        endpoints = VGroup(
            Dot(axes.c2p(-2, 0), color=ACCENT, radius=0.075),
            Dot(axes.c2p(2, 0), color=ACCENT, radius=0.075),
        )
        graph_label = MathTex(r"y=\sqrt{4-x^2}", font_size=32).next_to(axes, UP, buff=0.05)

        item = SCRIPT[7]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), Write(formula), run_time=0.7)
            self.wait_until_bookmark("semicircle_domain")
            self.play(Write(condition), Create(semi_line[0]), Create(semi_line[1]), FadeIn(semi_line[2]), FadeIn(semi_domain), run_time=1.25)
            self.wait_until_bookmark("semicircle_graph")
            self.play(Create(axes), FadeIn(graph_label), Create(semicircle), FadeIn(endpoints), run_time=1.4)
            self.play(
                Indicate(semi_line[1], color=ACCENT),
                Indicate(endpoints, color=ACCENT),
                run_time=0.75,
            )

        self.play(FadeOut(VGroup(heading, formula, condition, semi_line, semi_domain, axes, semicircle, endpoints, graph_label)), run_time=0.75)

        # ------------------------------------------------------------------
        # ACT 8 — Closed versus open endpoint
        # ------------------------------------------------------------------
        heading = section_title("7. Même racine, frontière différente")
        top_formula = MathTex(r"u(x)=\sqrt{x-1}", font_size=46).shift(UP * 1.65)
        top_condition = MathTex(r"x-1\geq0\iff x\geq1", font_size=39).next_to(top_formula, DOWN, buff=0.25)
        top_line = make_number_line(-2, 6, [(1, None)], closed_points=(1,), length=7.4)
        top_line.next_to(top_condition, DOWN, buff=0.32)

        bottom_formula = MathTex(r"v(x)=\frac{1}{\sqrt{x-1}}", font_size=46).shift(DOWN * 0.80)
        bottom_condition = MathTex(r"x-1>0\iff x>1", font_size=39).next_to(bottom_formula, DOWN, buff=0.25)
        bottom_line = make_number_line(-2, 6, [(1, None)], open_points=(1,), length=7.4)
        bottom_line.next_to(bottom_condition, DOWN, buff=0.32)

        item = SCRIPT[8]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), run_time=0.4)
            self.wait_until_bookmark("compare_roots")
            self.play(Write(top_formula), Write(top_condition), run_time=0.8)
            self.play(Create(top_line[0]), Create(top_line[1]), FadeIn(top_line[2]), run_time=0.8)
            self.play(Write(bottom_formula), run_time=0.65)
            self.wait_until_bookmark("open_endpoint")
            filled_copy = top_line[2][0].copy()
            self.add(filled_copy)
            self.play(
                filled_copy.animate.move_to(bottom_line[0].n2p(1)),
                Write(bottom_condition),
                Create(bottom_line[0]),
                Create(bottom_line[1]),
                run_time=0.9,
            )
            self.play(ReplacementTransform(filled_copy, bottom_line[2][0]), run_time=0.55)

        self.play(FadeOut(VGroup(heading, top_formula, top_condition, top_line, bottom_formula, bottom_condition, bottom_line)), run_time=0.7)

        # ------------------------------------------------------------------
        # ACT 9 — Root versus logarithm
        # ------------------------------------------------------------------
        heading = section_title("8. Racine carrée ou logarithme ?")
        root_card = RoundedRectangle(
            width=5.55,
            height=4.45,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        ).shift(LEFT * 3.2 + DOWN * 0.05)
        log_card = root_card.copy().shift(RIGHT * 6.4)

        root_formula = MathTex(r"\sqrt{x^2-1}", font_size=46).next_to(root_card.get_top(), DOWN, buff=0.35)
        root_rule = MathTex(r"x^2-1\geq0", font_size=38).next_to(root_formula, DOWN, buff=0.25)
        root_line = make_number_line(-4, 4, [(None, -1), (1, None)], closed_points=(-1, 1), length=4.5)
        root_line.next_to(root_rule, DOWN, buff=0.36)
        root_dom = MathTex(r"]-\infty,-1]\cup[1,+\infty[", font_size=31, color=ACCENT)
        root_dom.next_to(root_line, DOWN, buff=0.28)

        log_formula = MathTex(r"\ln(x^2-1)", font_size=46).next_to(log_card.get_top(), DOWN, buff=0.35)
        log_rule = MathTex(r"x^2-1>0", font_size=38).next_to(log_formula, DOWN, buff=0.25)
        log_line = make_number_line(-4, 4, [(None, -1), (1, None)], open_points=(-1, 1), length=4.5)
        log_line.next_to(log_rule, DOWN, buff=0.36)
        log_dom = MathTex(r"]-\infty,-1[\cup]1,+\infty[", font_size=31, color=ACCENT)
        log_dom.next_to(log_line, DOWN, buff=0.28)

        item = SCRIPT[9]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), FadeIn(root_card), FadeIn(log_card), run_time=0.65)
            self.wait_until_bookmark("log_compare")
            self.play(Write(root_formula), Write(root_rule), Create(root_line[0]), Create(root_line[1]), FadeIn(root_line[2]), FadeIn(root_dom), run_time=1.15)
            self.play(Write(log_formula), Write(log_rule), Create(log_line[0]), Create(log_line[1]), FadeIn(log_line[2]), FadeIn(log_dom), run_time=1.15)
            boundary_arrows = VGroup(
                Arrow(root_line[0].n2p(-1), log_line[0].n2p(-1), color=FORBIDDEN, buff=0.15),
                Arrow(root_line[0].n2p(1), log_line[0].n2p(1), color=FORBIDDEN, buff=0.15),
            )
            self.play(Create(boundary_arrows), run_time=0.65)

        self.play(FadeOut(VGroup(heading, root_card, log_card, root_formula, root_rule, root_line, root_dom, log_formula, log_rule, log_line, log_dom, boundary_arrows)), run_time=0.75)

        # ------------------------------------------------------------------
        # ACT 10 — Intersection of independent constraints
        # ------------------------------------------------------------------
        heading = section_title("9. Combiner plusieurs contraintes")
        formula = MathTex(r"w(x)=\frac{\sqrt{x+1}}{x-2}", font_size=49).shift(UP * 1.95)

        root_label = MathTex(r"x+1\geq0\iff x\geq-1", font_size=36)
        root_constraint = make_number_line(-4, 6, [(-1, None)], closed_points=(-1,), length=7.7)
        root_row = VGroup(root_label, root_constraint).arrange(DOWN, buff=0.20)
        root_row.shift(UP * 0.62)

        den_label = MathTex(r"x-2\neq0\iff x\neq2", font_size=36)
        den_constraint = make_number_line(-4, 6, [(None, 2), (2, None)], open_points=(2,), length=7.7)
        den_row = VGroup(den_label, den_constraint).arrange(DOWN, buff=0.20)
        den_row.shift(DOWN * 0.68)

        result_line = make_number_line(
            -4,
            6,
            [(-1, 2), (2, None)],
            closed_points=(-1,),
            open_points=(2,),
            length=7.7,
        ).shift(DOWN * 2.18)
        result_domain = MathTex(r"[-1,2[\cup]2,+\infty[", font_size=40, color=ACCENT)
        result_domain.next_to(result_line, UP, buff=0.14)

        labels = VGroup(
            Text("contrainte 1", font_size=22, color=MUTED).next_to(root_constraint, LEFT, buff=0.32),
            Text("contrainte 2", font_size=22, color=MUTED).next_to(den_constraint, LEFT, buff=0.32),
            Text("intersection", font_size=22, color=MUTED).next_to(result_line, LEFT, buff=0.32),
        )

        item = SCRIPT[10]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), Write(formula), run_time=0.75)
            self.wait_until_bookmark("constraint_root")
            self.play(Write(root_label), Create(root_constraint[0]), Create(root_constraint[1]), FadeIn(root_constraint[2]), FadeIn(labels[0]), run_time=0.95)
            self.wait_until_bookmark("constraint_den")
            self.play(Write(den_label), Create(den_constraint[0]), Create(den_constraint[1]), FadeIn(den_constraint[2]), FadeIn(labels[1]), run_time=0.95)
            self.wait_until_bookmark("constraint_intersection")
            self.play(
                TransformFromCopy(root_constraint[1], result_line[1]),
                Create(result_line[0]),
                FadeIn(result_line[2]),
                FadeIn(result_domain),
                FadeIn(labels[2]),
                run_time=1.1,
            )

        self.play(FadeOut(VGroup(heading, formula, root_row, den_row, result_line, result_domain, labels)), run_time=0.75)

        # ------------------------------------------------------------------
        # ACT 11 — A quotient inside a square root
        # ------------------------------------------------------------------
        heading = section_title("10. Étudier le signe de toute l’expression")
        formula = MathTex(r"z(x)=\sqrt{\frac{x-1}{x+2}}", font_size=50).shift(UP * 1.80)
        condition = MathTex(r"\frac{x-1}{x+2}\geq0", font_size=43).next_to(formula, DOWN, buff=0.30)

        sign_line = NumberLine(
            x_range=[-6, 5, 1],
            length=9.0,
            include_numbers=True,
            include_tip=True,
            color=BLACK,
            font_size=25,
        ).shift(DOWN * 0.10)
        critical_lines = VGroup(
            DashedLine(sign_line.n2p(-2) + DOWN * 0.25, sign_line.n2p(-2) + UP * 0.78, color=MUTED),
            DashedLine(sign_line.n2p(1) + DOWN * 0.25, sign_line.n2p(1) + UP * 0.78, color=MUTED),
        )
        signs = VGroup(
            MathTex("+", color=ACCENT).move_to(sign_line.n2p(-4.0) + UP * 0.47),
            MathTex("-", color=FORBIDDEN).move_to(sign_line.n2p(-0.5) + UP * 0.47),
            MathTex("+", color=ACCENT).move_to(sign_line.n2p(3.0) + UP * 0.47),
        )
        labels_critical = VGroup(
            MathTex(r"-2\;:\;\text{interdit}", font_size=27, color=FORBIDDEN).next_to(sign_line.n2p(-2), DOWN, buff=0.34),
            MathTex(r"1\;:\;\text{accepté}", font_size=27, color=ACCENT).next_to(sign_line.n2p(1), DOWN, buff=0.34),
        )
        quotient_domain_line = make_number_line(
            -6,
            5,
            [(None, -2), (1, None)],
            open_points=(-2,),
            closed_points=(1,),
            length=9.0,
        ).shift(DOWN * 1.55)
        quotient_domain = MathTex(r"]-\infty,-2[\cup[1,+\infty[", font_size=41, color=ACCENT)
        quotient_domain.next_to(quotient_domain_line, UP, buff=0.16)

        item = SCRIPT[11]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), Write(formula), run_time=0.75)
            self.wait_until_bookmark("quotient_root")
            self.play(Write(condition), Create(sign_line), Create(critical_lines), run_time=0.95)
            self.wait_until_bookmark("signs")
            self.play(FadeIn(signs), FadeIn(labels_critical), run_time=0.65)
            self.play(Create(quotient_domain_line[0]), Create(quotient_domain_line[1]), FadeIn(quotient_domain_line[2]), FadeIn(quotient_domain), run_time=1.05)

        self.play(FadeOut(VGroup(heading, formula, condition, sign_line, critical_lines, signs, labels_critical, quotient_domain_line, quotient_domain)), run_time=0.75)

        # ------------------------------------------------------------------
        # ACT 12 — Cancellation does not restore a forbidden value
        # ------------------------------------------------------------------
        heading = section_title("11. Le piège de la simplification")
        original = MathTex(r"F(x)=\frac{x^2-4}{x-2}", font_size=51).shift(LEFT * 3.35 + UP * 1.65)
        factored = MathTex(r"F(x)=\frac{(x-2)(x+2)}{x-2}", font_size=46).next_to(original, DOWN, buff=0.34)
        simplified = MathTex(
            r"F(x)=x+2",
            r"\quad\text{mais}\quad",
            r"x\neq2",
            font_size=43,
        )
        simplified.next_to(factored, DOWN, buff=0.34)
        warning_box = SurroundingRectangle(simplified[2], color=FORBIDDEN, buff=0.10, stroke_width=3)

        axes = Axes(
            x_range=[-4, 5, 1],
            y_range=[-2, 7, 1],
            x_length=5.0,
            y_length=5.0,
            axis_config={"color": BLACK, "stroke_width": 2},
            tips=False,
        ).shift(RIGHT * 3.45 + DOWN * 0.10)
        line_graph = axes.plot(lambda x: x + 2, x_range=[-4, 5], color=ACCENT)
        hole = Circle(
            radius=0.10,
            stroke_color=FORBIDDEN,
            stroke_width=3.2,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(axes.c2p(2, 4))
        hole_label = MathTex(r"(2,4)", font_size=29, color=FORBIDDEN).next_to(hole, UP + RIGHT, buff=0.12)

        item = SCRIPT[12]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), Write(original), run_time=0.75)
            self.wait_until_bookmark("cancel")
            self.play(TransformMatchingTex(original.copy(), factored), run_time=1.0)
            self.play(Write(simplified), Create(warning_box), run_time=0.85)
            self.wait_until_bookmark("hole_graph")
            self.play(Create(axes), Create(line_graph), run_time=1.0)
            self.play(FadeIn(hole, scale=1.6), FadeIn(hole_label), run_time=0.6)
            self.play(Circumscribe(hole, color=FORBIDDEN), run_time=0.8)

        self.play(FadeOut(VGroup(heading, original, factored, simplified, warning_box, axes, line_graph, hole, hole_label)), run_time=0.75)

        # ------------------------------------------------------------------
        # ACT 13 — Final domain scanner
        # ------------------------------------------------------------------
        heading = section_title("La méthode : scanner la formule")

        den_formula = MathTex(
            r"\frac{1}{x-3}",
            font_size=48,
            substrings_to_isolate=[r"x-3"],
        )
        den_formula.set_color_by_tex(r"x-3", ACCENT)
        root_formula = MathTex(
            r"\sqrt{5-x}",
            font_size=48,
            substrings_to_isolate=[r"5-x"],
        )
        root_formula.set_color_by_tex(r"5-x", ACCENT)
        log_formula = MathTex(
            r"\ln(x^2-4)",
            font_size=48,
            substrings_to_isolate=[r"x^2-4"],
        )
        log_formula.set_color_by_tex(r"x^2-4", ACCENT)

        formulas = VGroup(den_formula, root_formula, log_formula).arrange(RIGHT, buff=1.15).shift(UP * 1.20)
        cards = VGroup(*[
            RoundedRectangle(
                width=3.55,
                height=1.45,
                corner_radius=0.12,
                stroke_color=BLACK,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=1,
            ).move_to(mob)
            for mob in formulas
        ])
        formulas.set_z_index(2)

        scanner = SurroundingRectangle(cards[0], color=ACCENT, buff=0.05, stroke_width=4)

        rules = VGroup(
            MathTex(r"\text{dénominateur}\neq0", font_size=39),
            MathTex(r"\text{racine carrée}:\;\text{contenu}\geq0", font_size=39),
            MathTex(r"\text{logarithme}:\;\text{argument}>0", font_size=39),
            MathTex(r"\text{plusieurs conditions}\;\Longrightarrow\;\text{intersection}", font_size=39, color=ACCENT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).shift(DOWN * 0.95)

        item = SCRIPT[13]
        with self.narrated(item):
            self.set_caption(item["caption"])
            self.play(FadeIn(heading), FadeIn(cards), Write(formulas), run_time=0.9)
            self.wait_until_bookmark("scan_den")
            self.play(Create(scanner), FadeIn(rules[0], shift=UP * 0.12), run_time=0.7)
            self.wait_until_bookmark("scan_root")
            self.play(
                Transform(scanner, SurroundingRectangle(cards[1], color=ACCENT, buff=0.05, stroke_width=4)),
                FadeIn(rules[1], shift=UP * 0.12),
                run_time=0.7,
            )
            self.wait_until_bookmark("scan_log")
            self.play(
                Transform(scanner, SurroundingRectangle(cards[2], color=ACCENT, buff=0.05, stroke_width=4)),
                FadeIn(rules[2], shift=UP * 0.12),
                run_time=0.7,
            )
            self.play(FadeIn(rules[3], shift=UP * 0.12), run_time=0.65)
            self.play(Circumscribe(rules[3], color=ACCENT), run_time=0.8)

        self.wait(1.2)

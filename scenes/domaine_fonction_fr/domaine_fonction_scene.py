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
# Captions stay short; SSML carries pronunciation, pauses, and sync bookmarks.
# -----------------------------------------------------------------------------
SCRIPT = [
    {
        "caption": "On cherche le domaine naturel de la formule.",
        "ssml": tts.ssml(
            "Lorsqu'aucun domaine n'est précisé, on cherche le domaine naturel. "
            "C'est l'ensemble de tous les nombres réels pour lesquels la formule a un sens. "
            "<bookmark mark='intro_machine'/>"
            "On peut l'imaginer comme la liste des entrées acceptées par une machine."
        ),
    },
    {
        "caption": "Toujours la même méthode : formule, condition, domaine.",
        "ssml": tts.ssml(
            "Dans chaque exemple, nous suivrons toujours les mêmes trois étapes. "
            "<bookmark mark='method_formula'/>Observer la formule. "
            "<bookmark mark='method_condition'/>Écrire la condition nécessaire. "
            "<bookmark mark='method_domain'/>"
            "Puis représenter le domaine sur une droite numérique."
        ),
    },
    {
        "caption": "Un polynôme accepte tous les réels.",
        "ssml": tts.ssml(
            "Un polynôme ne contient ni division, ni racine carrée, ni logarithme. "
            "<bookmark mark='poly_tests'/>Chaque réel peut donc entrer. "
            "<bookmark mark='poly_domain'/>"
            "Son domaine naturel est l'ensemble des réels."
        ),
    },
    {
        "caption": "Un dénominateur ne peut jamais être nul.",
        "ssml": tts.ssml(
            "Dans une fraction, on inspecte d'abord le dénominateur. "
            "<bookmark mark='fraction_test'/>"
            "Ici, deux rend le dénominateur nul : cette entrée est refusée. "
            "<bookmark mark='fraction_domain'/>"
            "Tous les autres réels restent acceptés. "
            "<bookmark mark='fraction_graph'/>"
            "Le graphique confirme cette coupure verticale."
        ),
    },
    {
        "caption": "Factoriser révèle parfois plusieurs valeurs interdites.",
        "ssml": tts.ssml(
            "Le dénominateur peut s'annuler en plusieurs points. "
            "<bookmark mark='factor_copy'/>"
            "Nous factorisons seulement le dénominateur. "
            "<bookmark mark='factor_values'/>"
            "Les valeurs moins trois et trois sont interdites."
        ),
    },
    {
        "caption": "Sous une racine carrée, le contenu doit être positif ou nul.",
        "ssml": tts.ssml(
            "Pour une racine carrée réelle, le contenu doit être positif ou nul. "
            "<bookmark mark='root_right'/>"
            "La racine de x moins trois commence donc à trois."
        ),
    },
    {
        "caption": "Avant de calculer, essayez de prévoir le bon côté.",
        "ssml": tts.ssml(
            "Et pour la racine de cinq moins x ? "
            "<bookmark mark='prediction_show'/>"
            "Le domaine est-il à droite de cinq, à gauche de cinq, "
            "ou tous les réels sauf cinq ? "
            "<bookmark mark='prediction_reveal'/>"
            "Comme cinq moins x doit être positif ou nul, "
            "il faut x inférieur ou égal à cinq."
        ),
    },
    {
        "caption": "Une inéquation quadratique peut produire deux intervalles.",
        "ssml": tts.ssml(
            "Avec x carré moins quatre, le domaine peut se séparer en deux morceaux. "
            "<bookmark mark='quadratic_signs'/>"
            "Le produit est positif ou nul à l'extérieur des racines moins deux et deux. "
            "<bookmark mark='quadratic_domain'/>"
            "Les deux extrémités sont incluses."
        ),
    },
    {
        "caption": "Le domaine est l’étendue horizontale du graphique.",
        "ssml": tts.ssml(
            "Pour la racine de quatre moins x carré, "
            "la condition donne l'intervalle de moins deux à deux. "
            "<bookmark mark='semicircle_line'/>"
            "La droite numérique montre l'étendue horizontale autorisée. "
            "<bookmark mark='semicircle_graph'/>"
            "Avec la même échelle sur les deux axes, la courbe est un demi-cercle."
        ),
    },
    {
        "caption": "La position de la racine change la frontière.",
        "ssml": tts.ssml(
            "Comparons deux formules presque identiques. "
            "<bookmark mark='root_closed'/>"
            "Dans la racine de x moins un, la valeur un est acceptée. "
            "<bookmark mark='root_open'/>"
            "Mais au dénominateur, cette même racine doit être non nulle : "
            "un est alors retiré."
        ),
    },
    {
        "caption": "Le logarithme exige une quantité strictement positive.",
        "ssml": tts.ssml(
            "Le logarithme refuse également la valeur zéro. "
            "<bookmark mark='log_copy'/>"
            "Partons du domaine de la racine de x carré moins un. "
            "<bookmark mark='log_open'/>"
            "Pour le logarithme, les deux points frontières deviennent ouverts."
        ),
    },
    {
        "caption": "Avec plusieurs contraintes, on prend leur intersection.",
        "ssml": tts.ssml(
            "Une formule peut contenir plusieurs restrictions. "
            "<bookmark mark='intersection_root'/>"
            "La racine impose x supérieur ou égal à moins un. "
            "<bookmark mark='intersection_den'/>"
            "Le dénominateur retire deux. "
            "<bookmark mark='intersection_result'/>"
            "Le domaine est la partie qui survit aux deux filtres."
        ),
    },
    {
        "caption": "Il faut étudier le signe de toute la fraction.",
        "ssml": tts.ssml(
            "Dans cet exemple, ce n'est pas seulement le numérateur "
            "qui doit être positif. "
            "<bookmark mark='quotient_warning'/>"
            "Toute la fraction sous la racine doit être positive ou nulle. "
            "<bookmark mark='quotient_rows'/>"
            "Le signe du numérateur et celui du dénominateur "
            "donnent le signe du quotient. "
            "<bookmark mark='quotient_domain'/>"
            "Moins deux reste interdit, tandis que un est accepté."
        ),
    },
    {
        "caption": "Simplifier ne restaure jamais une valeur interdite.",
        "ssml": tts.ssml(
            "Voici un piège classique. "
            "<bookmark mark='hole_factor'/>"
            "On factorise, puis on simplifie le facteur commun. "
            "<bookmark mark='hole_warning'/>"
            "Mais la formule de départ était interdite en deux. "
            "<bookmark mark='hole_graph'/>"
            "Le graphique est donc une droite avec un trou "
            "au point deux virgule quatre."
        ),
    },
    {
        "caption": "Scannez la formule, puis combinez les conditions.",
        "ssml": tts.ssml(
            "Pour conclure, scannez d'abord les parties dangereuses de la formule. "
            "<bookmark mark='scan_den'/>"
            "Un dénominateur est différent de zéro. "
            "<bookmark mark='scan_root'/>"
            "Sous une racine carrée, le contenu est positif ou nul. "
            "<bookmark mark='scan_log'/>"
            "Dans un logarithme, l'argument est strictement positif. "
            "<bookmark mark='scan_intersection'/>"
            "Et s'il y a plusieurs conditions, prenez leur intersection."
        ),
    },
]


# -----------------------------------------------------------------------------
# Visual helpers
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


def section_title(text: str) -> Text:
    return Text(
        text,
        font_size=35,
        weight=SEMIBOLD,
    ).to_edge(UP, buff=0.28)


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

    left_arrow = Arrow(
        LEFT * 2.15,
        LEFT * 1.32,
        buff=0,
        color=BLACK,
        stroke_width=3,
    )

    right_arrow = Arrow(
        RIGHT * 1.32,
        RIGHT * 2.15,
        buff=0,
        color=BLACK,
        stroke_width=3,
    )

    input_label = Text(
        "entrée",
        font_size=23,
    ).next_to(left_arrow, UP, buff=0.08)

    output_label = Text(
        "sortie",
        font_size=23,
    ).next_to(right_arrow, UP, buff=0.08)

    return VGroup(
        body,
        name,
        left_arrow,
        right_arrow,
        input_label,
        output_label,
    )


def make_token(
    tex: str,
    color: ManimColor = BLACK,
) -> VGroup:
    circle = Circle(
        radius=0.36,
        stroke_color=color,
        stroke_width=2.5,
        fill_color=WHITE,
        fill_opacity=1,
    )

    label = MathTex(
        tex,
        font_size=32,
        color=color,
    )

    return VGroup(circle, label)


def make_number_line(
    x_min: float,
    x_max: float,
    segments: list[tuple[float | None, float | None]],
    *,
    open_points: tuple[float, ...] = (),
    closed_points: tuple[float, ...] = (),
    length: float = 4.25,
    include_numbers: bool = True,
    step: float = 1,
) -> VGroup:
    """
    Create a number line with blue accepted pieces.

    None on the left or right of a segment represents infinity.
    Infinite accepted intervals receive explicit blue arrowheads.
    """

    line = NumberLine(
        x_range=[x_min, x_max, step],
        length=length,
        include_numbers=include_numbers,
        include_tip=True,
        color=BLACK,
        stroke_width=2.0,
        font_size=22,
        decimal_number_config={
            "num_decimal_places": 0,
        },
    )

    accepted = VGroup()
    epsilon = (x_max - x_min) * 0.025

    for left, right in segments:
        a = x_min + epsilon if left is None else left
        b = x_max - epsilon if right is None else right

        start = line.n2p(a)
        end = line.n2p(b)

        if left is None and right is None:
            piece = DoubleArrow(
                start,
                end,
                buff=0,
                color=ACCENT,
                stroke_width=7,
                max_tip_length_to_length_ratio=0.035,
            )

        elif left is None:
            piece = Arrow(
                end,
                start,
                buff=0,
                color=ACCENT,
                stroke_width=7,
                max_tip_length_to_length_ratio=0.06,
            )

        elif right is None:
            piece = Arrow(
                start,
                end,
                buff=0,
                color=ACCENT,
                stroke_width=7,
                max_tip_length_to_length_ratio=0.06,
            )

        else:
            piece = Line(
                start,
                end,
                color=ACCENT,
                stroke_width=7,
            )

        accepted.add(piece)

    points = VGroup()

    for value in closed_points:
        points.add(
            Dot(
                line.n2p(value),
                radius=0.09,
                color=ACCENT,
            )
        )

    for value in open_points:
        points.add(
            Circle(
                radius=0.10,
                stroke_color=ACCENT,
                stroke_width=3,
                fill_color=WHITE,
                fill_opacity=1,
            ).move_to(line.n2p(value))
        )

    return VGroup(
        line,
        accepted,
        points,
    )


def make_domain_board(
    formula: str,
    condition: str,
    domain: str,
    *,
    x_range: tuple[float, float, float],
    segments: list[tuple[float | None, float | None]],
    open_points: tuple[float, ...] = (),
    closed_points: tuple[float, ...] = (),
) -> VGroup:
    """
    Persistent visual grammar:

        formula  ->  condition  ->  domain
    """

    specs = [
        ("FORMULE", 3.65),
        ("CONDITION", 3.75),
        ("DOMAINE", 4.65),
    ]

    cards = VGroup()

    for label, width in specs:
        rect = RoundedRectangle(
            width=width,
            height=3.35,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=1.8,
            fill_color=WHITE,
            fill_opacity=1,
        )

        tag = Text(
            label,
            font_size=21,
            color=MUTED,
            weight=SEMIBOLD,
        )

        tag.next_to(
            rect.get_top(),
            DOWN,
            buff=0.18,
        )

        cards.add(
            VGroup(rect, tag)
        )

    cards.arrange(
        RIGHT,
        buff=0.55,
    )

    formula_mob = MathTex(
        formula,
        font_size=43,
    )

    if formula_mob.width > 3.15:
        formula_mob.scale_to_fit_width(3.15)

    formula_mob.move_to(
        cards[0][0].get_center() + DOWN * 0.05
    )

    condition_mob = MathTex(
        condition,
        font_size=39,
    )

    if condition_mob.width > 3.25:
        condition_mob.scale_to_fit_width(3.25)

    condition_mob.move_to(
        cards[1][0].get_center() + DOWN * 0.05
    )

    domain_mob = MathTex(
        domain,
        font_size=34,
        color=ACCENT,
    )

    if domain_mob.width > 4.0:
        domain_mob.scale_to_fit_width(4.0)

    number_line = make_number_line(
        x_range[0],
        x_range[1],
        segments,
        open_points=open_points,
        closed_points=closed_points,
        length=4.0,
        step=x_range[2],
    )

    domain_content = VGroup(
        number_line,
        domain_mob,
    ).arrange(
        DOWN,
        buff=0.28,
    )

    domain_content.move_to(
        cards[2][0].get_center() + DOWN * 0.05
    )

    arrows = VGroup(
        Arrow(
            cards[0].get_right(),
            cards[1].get_left(),
            buff=0.10,
            color=BLACK,
            stroke_width=2.4,
        ),
        Arrow(
            cards[1].get_right(),
            cards[2].get_left(),
            buff=0.10,
            color=BLACK,
            stroke_width=2.4,
        ),
    )

    board = VGroup(
        cards,
        formula_mob,
        condition_mob,
        domain_content,
        arrows,
    )

    board.shift(DOWN * 0.08)

    return board


def make_prediction_options(
    options: list[str],
) -> VGroup:
    groups = VGroup()

    for text in options:
        tex = MathTex(
            text,
            font_size=34,
        )

        box = RoundedRectangle(
            width=3.65,
            height=0.78,
            corner_radius=0.10,
            stroke_color=BLACK,
            stroke_width=1.6,
            fill_color=WHITE,
            fill_opacity=1,
        )

        groups.add(
            VGroup(box, tex)
        )

    groups.arrange(
        DOWN,
        buff=0.18,
    )

    return groups


def make_sign_table() -> VGroup:
    """
    Full sign table for:

        (x - 1) / (x + 2)
    """

    columns_x = [
        -4.4,
        -1.8,
        0.8,
        3.5,
    ]

    row_y = [
        1.25,
        0.45,
        -0.35,
        -1.15,
    ]

    labels = VGroup(
        MathTex(
            "x",
            font_size=31,
        ).move_to([columns_x[0], row_y[0], 0]),

        MathTex(
            "x-1",
            font_size=31,
        ).move_to([columns_x[0], row_y[1], 0]),

        MathTex(
            "x+2",
            font_size=31,
        ).move_to([columns_x[0], row_y[2], 0]),

        MathTex(
            r"\frac{x-1}{x+2}",
            font_size=31,
        ).move_to([columns_x[0], row_y[3], 0]),
    )

    intervals = VGroup(
        MathTex(
            r"]-\infty,-2[",
            font_size=28,
        ).move_to([columns_x[1], row_y[0], 0]),

        MathTex(
            r"]-2,1[",
            font_size=28,
        ).move_to([columns_x[2], row_y[0], 0]),

        MathTex(
            r"]1,+\infty[",
            font_size=28,
        ).move_to([columns_x[3], row_y[0], 0]),
    )

    numerator = VGroup(
        MathTex(
            "-",
            font_size=34,
            color=FORBIDDEN,
        ).move_to([columns_x[1], row_y[1], 0]),

        MathTex(
            "-",
            font_size=34,
            color=FORBIDDEN,
        ).move_to([columns_x[2], row_y[1], 0]),

        MathTex(
            "+",
            font_size=34,
            color=ACCENT,
        ).move_to([columns_x[3], row_y[1], 0]),
    )

    denominator = VGroup(
        MathTex(
            "-",
            font_size=34,
            color=FORBIDDEN,
        ).move_to([columns_x[1], row_y[2], 0]),

        MathTex(
            "+",
            font_size=34,
            color=ACCENT,
        ).move_to([columns_x[2], row_y[2], 0]),

        MathTex(
            "+",
            font_size=34,
            color=ACCENT,
        ).move_to([columns_x[3], row_y[2], 0]),
    )

    quotient = VGroup(
        MathTex(
            "+",
            font_size=36,
            color=ACCENT,
        ).move_to([columns_x[1], row_y[3], 0]),

        MathTex(
            "-",
            font_size=36,
            color=FORBIDDEN,
        ).move_to([columns_x[2], row_y[3], 0]),

        MathTex(
            "+",
            font_size=36,
            color=ACCENT,
        ).move_to([columns_x[3], row_y[3], 0]),
    )

    horizontal = VGroup(
        *[
            Line(
                [-5.15, y, 0],
                [4.35, y, 0],
                color=BLACK,
                stroke_width=1.2,
            )
            for y in [
                0.85,
                0.05,
                -0.75,
            ]
        ]
    )

    vertical = Line(
        [-3.35, 1.62, 0],
        [-3.35, -1.55, 0],
        color=BLACK,
        stroke_width=1.2,
    )

    criticals = VGroup(
        DashedLine(
            [-0.55, 1.60, 0],
            [-0.55, -1.52, 0],
            color=MUTED,
            dash_length=0.08,
        ),
        DashedLine(
            [2.15, 1.60, 0],
            [2.15, -1.52, 0],
            color=MUTED,
            dash_length=0.08,
        ),
    )

    critical_labels = VGroup(
        MathTex(
            "-2",
            font_size=28,
            color=FORBIDDEN,
        ).move_to([-0.55, 1.28, 0]),

        MathTex(
            "1",
            font_size=28,
            color=ACCENT,
        ).move_to([2.15, 1.28, 0]),
    )

    return VGroup(
        labels,
        intervals,
        numerator,
        denominator,
        quotient,
        horizontal,
        vertical,
        criticals,
        critical_labels,
    )

@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class DomaineFonctionFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    """
    Natural domains through one persistent visual method
    and many progressively richer examples.
    """

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

    def set_caption(
        self,
        text: str,
        *,
        animate: bool = True,
    ) -> None:
        new_caption = make_caption(text)

        if self.caption_mob is None:
            if animate:
                self.play(
                    FadeIn(new_caption),
                    run_time=0.3,
                )
            else:
                self.add(new_caption)

        elif animate:
            self.play(
                ReplacementTransform(
                    self.caption_mob,
                    new_caption,
                ),
                run_time=0.3,
            )

        else:
            self.remove(self.caption_mob)
            self.add(new_caption)

        self.caption_mob = new_caption

    def accepted_test(
        self,
        machine: VGroup,
        input_tex: str,
        output_tex: str,
    ) -> None:
        token_in = make_token(
            input_tex
        ).move_to(
            machine.get_left() + LEFT * 1.25
        )

        token_out = make_token(
            output_tex,
            ACCENT,
        ).move_to(
            machine.get_right() + RIGHT * 1.25
        )

        self.play(
            FadeIn(
                token_in,
                shift=RIGHT * 0.20,
            ),
            run_time=0.30,
        )

        self.play(
            token_in.animate.move_to(
                machine.get_center()
            ),
            run_time=0.55,
        )

        self.play(
            FadeOut(
                token_in,
                scale=0.7,
            ),
            FadeIn(
                token_out,
                shift=RIGHT * 0.25,
            ),
            run_time=0.40,
        )

        self.play(
            FadeOut(
                token_out,
                shift=RIGHT * 0.25,
            ),
            run_time=0.28,
        )

    def rejected_test(
        self,
        machine: VGroup,
        input_tex: str,
    ) -> None:
        token = make_token(
            input_tex,
            FORBIDDEN,
        ).move_to(
            machine.get_left() + LEFT * 1.25
        )

        self.play(
            FadeIn(
                token,
                shift=RIGHT * 0.20,
            ),
            run_time=0.30,
        )

        self.play(
            token.animate.move_to(
                machine.get_left() + LEFT * 0.42
            ),
            run_time=0.55,
        )

        cross = Cross(
            token,
            stroke_color=FORBIDDEN,
            stroke_width=5,
        ).scale(1.12)

        warning = Text(
            "non défini",
            font_size=26,
            color=FORBIDDEN,
        ).next_to(
            machine,
            DOWN,
            buff=0.18,
        )

        self.play(
            Create(cross),
            Wiggle(
                machine[0],
                scale_value=1.04,
            ),
            FadeIn(warning),
            run_time=0.65,
        )

        self.play(
            FadeOut(
                VGroup(
                    token,
                    cross,
                    warning,
                )
            ),
            run_time=0.35,
        )

    def show_board(
        self,
        old_board: VGroup | None,
        new_board: VGroup,
    ) -> VGroup:
        if old_board is None:
            self.play(
                FadeIn(
                    new_board,
                    shift=UP * 0.12,
                ),
                run_time=0.85,
            )

        else:
            self.play(
                ReplacementTransform(
                    old_board,
                    new_board,
                ),
                run_time=0.95,
            )

        return new_board

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.caption_mob: VGroup | None = None

        self._setup_voiceover()
        play_uqam_intro(self)

        # ------------------------------------------------------------------
        # INTRO — Natural domain and the machine metaphor
        # ------------------------------------------------------------------
        title = Text(
            "Le domaine d’une fonction",
            font_size=48,
            weight=SEMIBOLD,
        )

        subtitle = Text(
            "Quelles entrées la formule accepte-t-elle ?",
            font_size=31,
        )

        title_group = VGroup(
            title,
            subtitle,
        ).arrange(
            DOWN,
            buff=0.22,
        ).shift(
            UP * 2.05
        )

        machine = make_machine("f").shift(
            DOWN * 0.10
        )

        natural = MathTex(
            r"\operatorname{Dom}_{\mathrm{nat}}(f)="
            r"\{x\in\mathbb{R}:\text{ la formule a un sens}\}",
            font_size=37,
        ).shift(
            DOWN * 2.05
        )

        item = SCRIPT[0]

        with self.narrated(item):
            self.set_caption(
                item["caption"],
                animate=False,
            )

            self.play(
                Write(title),
                FadeIn(
                    subtitle,
                    shift=UP * 0.12,
                ),
                run_time=0.95,
            )

            self.play(
                Write(natural),
                run_time=0.85,
            )

            self.wait_until_bookmark(
                "intro_machine"
            )

            self.play(
                Create(machine[0]),
                Write(machine[1]),
                GrowArrow(machine[2]),
                GrowArrow(machine[3]),
            )

            self.play(
                FadeIn(machine[4:]),
                run_time=0.40,
            )

        self.play(
            FadeOut(
                VGroup(
                    title_group,
                    natural,
                )
            ),
            machine.animate.shift(
                UP * 0.35
            ),
            run_time=0.65,
        )

        # ------------------------------------------------------------------
        # METHOD — Persistent formula -> condition -> domain grammar
        # ------------------------------------------------------------------
        method_heading = section_title(
            "Une méthode qui ne change jamais"
        )

        labels = VGroup(
            Text(
                "FORMULE",
                font_size=28,
                color=MUTED,
                weight=SEMIBOLD,
            ),
            Text(
                "CONDITION",
                font_size=28,
                color=MUTED,
                weight=SEMIBOLD,
            ),
            Text(
                "DOMAINE",
                font_size=28,
                color=MUTED,
                weight=SEMIBOLD,
            ),
        ).arrange(
            RIGHT,
            buff=2.45,
        ).shift(
            UP * 0.70
        )

        method_arrows = VGroup(
            Arrow(
                labels[0].get_right(),
                labels[1].get_left(),
                buff=0.25,
                color=BLACK,
            ),
            Arrow(
                labels[1].get_right(),
                labels[2].get_left(),
                buff=0.25,
                color=BLACK,
            ),
        )

        item = SCRIPT[1]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            self.play(
                FadeIn(method_heading),
                run_time=0.4,
            )

            self.wait_until_bookmark(
                "method_formula"
            )

            self.play(
                FadeIn(labels[0]),
                run_time=0.4,
            )

            self.wait_until_bookmark(
                "method_condition"
            )

            self.play(
                GrowArrow(method_arrows[0]),
                FadeIn(labels[1]),
                run_time=0.55,
            )

            self.wait_until_bookmark(
                "method_domain"
            )

            self.play(
                GrowArrow(method_arrows[1]),
                FadeIn(labels[2]),
                run_time=0.55,
            )

        self.play(
            FadeOut(
                VGroup(
                    method_heading,
                    labels,
                    method_arrows,
                    machine,
                )
            ),
            run_time=0.65,
        )

        # ==================================================================
        # PHASE 1 — Repérer les restrictions
        # ==================================================================
        heading = section_title(
            "1. Repérer les restrictions"
        )

        self.play(
            FadeIn(heading),
            run_time=0.4,
        )

        current_board: VGroup | None = None

        # ------------------------------------------------------------------
        # Polynomial
        # ------------------------------------------------------------------
        board = make_domain_board(
            r"f(x)=x^2-3x+1",
            r"\text{aucune restriction}",
            r"\mathbb{R}",
            x_range=(-5, 5, 1),
            segments=[
                (None, None),
            ],
        )

        machine = make_machine("f").scale(
            0.72
        ).shift(
            DOWN * 2.35
        )

        item = SCRIPT[2]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            current_board = self.show_board(
                current_board,
                board,
            )

            self.wait_until_bookmark(
                "poly_tests"
            )

            self.play(
                FadeIn(machine),
                run_time=0.35,
            )

            self.accepted_test(
                machine,
                r"-2",
                r"11",
            )

            self.accepted_test(
                machine,
                r"0",
                r"1",
            )

            self.accepted_test(
                machine,
                r"3",
                r"1",
            )

            self.wait_until_bookmark(
                "poly_domain"
            )

            self.play(
                Indicate(
                    board[3],
                    color=ACCENT,
                ),
                run_time=0.65,
            )

        self.play(
            FadeOut(machine),
            run_time=0.35,
        )

        # ------------------------------------------------------------------
        # Simple fraction
        # ------------------------------------------------------------------
        board = make_domain_board(
            r"g(x)=\frac{1}{x-2}",
            r"x-2\neq0\iff x\neq2",
            r"\mathbb{R}\setminus\{2\}",
            x_range=(-4, 6, 1),
            segments=[
                (None, 2),
                (2, None),
            ],
            open_points=(2,),
        )

        machine = make_machine("g").scale(
            0.72
        ).shift(
            DOWN * 2.35
        )

        item = SCRIPT[3]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            current_board = self.show_board(
                current_board,
                board,
            )

            self.wait_until_bookmark(
                "fraction_test"
            )

            self.play(
                FadeIn(machine),
                run_time=0.35,
            )

            self.accepted_test(
                machine,
                r"0",
                r"-\frac12",
            )

            self.rejected_test(
                machine,
                r"2",
            )

            self.wait_until_bookmark(
                "fraction_domain"
            )

            self.play(
                Indicate(
                    board[3],
                    color=ACCENT,
                ),
                run_time=0.65,
            )

            self.wait_until_bookmark(
                "fraction_graph"
            )

            axes = Axes(
                x_range=[-3, 6, 1],
                y_range=[-4, 4, 1],
                x_length=5.1,
                y_length=3.7,
                axis_config={
                    "color": BLACK,
                    "stroke_width": 2,
                },
                tips=False,
            ).scale(
                0.82
            ).shift(
                RIGHT * 3.7 + DOWN * 0.10
            )

            graph_left = axes.plot(
                lambda x: 1 / (x - 2),
                x_range=[-3, 1.80],
                color=ACCENT,
            )

            graph_right = axes.plot(
                lambda x: 1 / (x - 2),
                x_range=[2.20, 6],
                color=ACCENT,
            )

            asymptote = DashedLine(
                axes.c2p(2, -4),
                axes.c2p(2, 4),
                color=FORBIDDEN,
            )

            graph_group = VGroup(
                axes,
                graph_left,
                graph_right,
                asymptote,
            )

            self.play(
                current_board.animate.scale(
                    0.68
                ).shift(
                    LEFT * 2.25 + UP * 0.18
                ),
                FadeOut(machine),
                run_time=0.75,
            )

            self.play(
                Create(axes),
                Create(asymptote),
                Create(graph_left),
                Create(graph_right),
                run_time=1.15,
            )

        self.play(
            FadeOut(graph_group),
            current_board.animate.scale(
                1 / 0.68
            ).shift(
                RIGHT * 2.25 + DOWN * 0.18
            ),
            run_time=0.75,
        )

        # ------------------------------------------------------------------
        # Several denominator zeros
        # ------------------------------------------------------------------
        board = make_domain_board(
            r"h(x)=\frac{x+1}{x^2-9}",
            r"x\neq-3\ \text{et}\ x\neq3",
            r"\mathbb{R}\setminus\{-3,3\}",
            x_range=(-6, 6, 1),
            segments=[
                (None, -3),
                (-3, 3),
                (3, None),
            ],
            open_points=(-3, 3),
        )

        denominator = MathTex(
            r"x^2-9",
            font_size=43,
        ).shift(
            LEFT * 1.8 + DOWN * 2.25
        )

        factorization = MathTex(
            r"x^2-9=(x-3)(x+3)",
            font_size=39,
        ).shift(
            RIGHT * 1.75 + DOWN * 2.25
        )

        factor_arrow = Arrow(
            denominator.get_right(),
            factorization.get_left(),
            buff=0.18,
            color=BLACK,
        )

        item = SCRIPT[4]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            current_board = self.show_board(
                current_board,
                board,
            )

            self.wait_until_bookmark(
                "factor_copy"
            )

            self.play(
                FadeIn(
                    denominator,
                    shift=UP * 0.10,
                ),
                run_time=0.55,
            )

            self.play(
                GrowArrow(factor_arrow),
                TransformFromCopy(
                    denominator,
                    factorization,
                ),
                run_time=0.85,
            )

            self.wait_until_bookmark(
                "factor_values"
            )

            self.play(
                Indicate(
                    factorization,
                    color=ACCENT,
                ),
                Indicate(
                    board[3],
                    color=ACCENT,
                ),
                run_time=0.75,
            )

        self.play(
            FadeOut(
                VGroup(
                    denominator,
                    factorization,
                    factor_arrow,
                )
            ),
            run_time=0.35,
        )

        # ------------------------------------------------------------------
        # Simple square root
        # ------------------------------------------------------------------
        board = make_domain_board(
            r"p(x)=\sqrt{x-3}",
            r"x-3\geq0\iff x\geq3",
            r"[3,+\infty[",
            x_range=(-2, 8, 1),
            segments=[
                (3, None),
            ],
            closed_points=(3,),
        )

        item = SCRIPT[5]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            current_board = self.show_board(
                current_board,
                board,
            )

            self.wait_until_bookmark(
                "root_right"
            )

            self.play(
                Indicate(
                    board[2],
                    color=ACCENT,
                ),
                Indicate(
                    board[3],
                    color=ACCENT,
                ),
                run_time=0.75,
            )

        # ------------------------------------------------------------------
        # Prediction: sqrt(5-x)
        # ------------------------------------------------------------------
        prediction_formula = MathTex(
            r"q(x)=\sqrt{5-x}",
            font_size=47,
        ).shift(
            UP * 1.65
        )

        question = Text(
            "Quel est le domaine ?",
            font_size=31,
        ).next_to(
            prediction_formula,
            DOWN,
            buff=0.28,
        )

        options = make_prediction_options(
            [
                r"[5,+\infty[",
                r"]-\infty,5]",
                r"\mathbb{R}\setminus\{5\}",
            ]
        )

        options.shift(
            DOWN * 0.60
        )

        item = SCRIPT[6]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            self.play(
                FadeOut(current_board),
                FadeIn(prediction_formula),
                FadeIn(question),
                run_time=0.65,
            )

            self.wait_until_bookmark(
                "prediction_show"
            )

            self.play(
                LaggedStart(
                    *[
                        FadeIn(
                            option,
                            shift=UP * 0.10,
                        )
                        for option in options
                    ],
                    lag_ratio=0.16,
                ),
                run_time=0.85,
            )

            self.wait_until_bookmark(
                "prediction_reveal"
            )

            correct_box = options[1][0]

            self.play(
                correct_box.animate.set_stroke(
                    ACCENT,
                    width=4,
                ).set_fill(
                    ACCENT,
                    opacity=0.08,
                ),
                Circumscribe(
                    options[1],
                    color=ACCENT,
                ),
                run_time=0.75,
            )

        board = make_domain_board(
            r"q(x)=\sqrt{5-x}",
            r"5-x\geq0\iff x\leq5",
            r"]-\infty,5]",
            x_range=(-2, 8, 1),
            segments=[
                (None, 5),
            ],
            closed_points=(5,),
        )

        self.play(
            FadeOut(
                VGroup(
                    prediction_formula,
                    question,
                    options,
                )
            ),
            FadeIn(board),
            run_time=0.75,
        )

        current_board = board

        # ------------------------------------------------------------------
        # Quadratic radicand with two intervals
        # ------------------------------------------------------------------
        board = make_domain_board(
            r"r(x)=\sqrt{x^2-4}",
            r"(x-2)(x+2)\geq0",
            r"]-\infty,-2]\cup[2,+\infty[",
            x_range=(-5, 5, 1),
            segments=[
                (None, -2),
                (2, None),
            ],
            closed_points=(-2, 2),
        )

        signs = VGroup(
            MathTex(
                "+",
                color=ACCENT,
            ).shift(
                LEFT * 3.6 + DOWN * 2.25
            ),
            MathTex(
                "-",
                color=FORBIDDEN,
            ).shift(
                DOWN * 2.25
            ),
            MathTex(
                "+",
                color=ACCENT,
            ).shift(
                RIGHT * 3.6 + DOWN * 2.25
            ),
        )

        item = SCRIPT[7]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            current_board = self.show_board(
                current_board,
                board,
            )

            self.wait_until_bookmark(
                "quadratic_signs"
            )

            self.play(
                FadeIn(signs),
                run_time=0.55,
            )

            self.wait_until_bookmark(
                "quadratic_domain"
            )

            self.play(
                Indicate(
                    board[3],
                    color=ACCENT,
                ),
                run_time=0.70,
            )

        self.play(
            FadeOut(signs),
            run_time=0.30,
        )

        # ------------------------------------------------------------------
        # Semicircle: graph confirms the domain
        # ------------------------------------------------------------------
        board = make_domain_board(
            r"s(x)=\sqrt{4-x^2}",
            r"4-x^2\geq0\iff -2\leq x\leq2",
            r"[-2,2]",
            x_range=(-3, 3, 1),
            segments=[
                (-2, 2),
            ],
            closed_points=(-2, 2),
        )

        item = SCRIPT[8]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            current_board = self.show_board(
                current_board,
                board,
            )

            self.wait_until_bookmark(
                "semicircle_line"
            )

            self.play(
                Indicate(
                    board[3],
                    color=ACCENT,
                ),
                run_time=0.65,
            )

            self.wait_until_bookmark(
                "semicircle_graph"
            )

            # Equal units on both axes:
            # x_length / 6 = y_length / 4 = 0.9.
            axes = Axes(
                x_range=[-3, 3, 1],
                y_range=[-1, 3, 1],
                x_length=5.4,
                y_length=3.6,
                axis_config={
                    "color": BLACK,
                    "stroke_width": 2,
                },
                tips=False,
            ).shift(
                RIGHT * 3.45 + DOWN * 0.10
            )

            semicircle = axes.plot(
                lambda x: (4 - x**2) ** 0.5,
                x_range=[-2, 2],
                color=ACCENT,
            )

            endpoints = VGroup(
                Dot(
                    axes.c2p(-2, 0),
                    color=ACCENT,
                    radius=0.075,
                ),
                Dot(
                    axes.c2p(2, 0),
                    color=ACCENT,
                    radius=0.075,
                ),
            )

            graph_group = VGroup(
                axes,
                semicircle,
                endpoints,
            )

            self.play(
                current_board.animate.scale(
                    0.68
                ).shift(
                    LEFT * 2.25 + UP * 0.18
                ),
                run_time=0.70,
            )

            self.play(
                Create(axes),
                Create(semicircle),
                FadeIn(endpoints),
                run_time=1.15,
            )

        self.play(
            FadeOut(graph_group),
            FadeOut(current_board),
            FadeOut(heading),
            run_time=0.70,
        )

        # ==================================================================
        # PHASE 2 — Compare boundaries
        # ==================================================================
        heading = section_title(
            "2. Comprendre les frontières"
        )

        self.play(
            FadeIn(heading),
            run_time=0.4,
        )

        # ------------------------------------------------------------------
        # sqrt(x-1) versus 1/sqrt(x-1)
        # ------------------------------------------------------------------
        root_formula = MathTex(
            r"u(x)=\sqrt{x-1}",
            font_size=45,
        ).shift(
            LEFT * 3.30 + UP * 1.45
        )

        root_condition = MathTex(
            r"x\geq1",
            font_size=39,
        ).next_to(
            root_formula,
            DOWN,
            buff=0.25,
        )

        root_line = make_number_line(
            -2,
            6,
            [
                (1, None),
            ],
            closed_points=(1,),
            length=5.1,
        )

        root_line.next_to(
            root_condition,
            DOWN,
            buff=0.35,
        )

        den_formula = MathTex(
            r"v(x)=\frac{1}{\sqrt{x-1}}",
            font_size=45,
        ).shift(
            RIGHT * 3.30 + UP * 1.45
        )

        den_condition = MathTex(
            r"x>1",
            font_size=39,
        ).next_to(
            den_formula,
            DOWN,
            buff=0.25,
        )

        den_line = make_number_line(
            -2,
            6,
            [
                (1, None),
            ],
            open_points=(1,),
            length=5.1,
        )

        den_line.next_to(
            den_condition,
            DOWN,
            buff=0.35,
        )

        divider = Line(
            UP * 2.10,
            DOWN * 2.15,
            color=PALE,
            stroke_width=2,
        )

        item = SCRIPT[9]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            self.play(
                Create(divider),
                run_time=0.35,
            )

            self.wait_until_bookmark(
                "root_closed"
            )

            self.play(
                Write(root_formula),
                Write(root_condition),
                Create(root_line[0]),
                Create(root_line[1]),
                FadeIn(root_line[2]),
                run_time=1.00,
            )

            self.wait_until_bookmark(
                "root_open"
            )

            self.play(
                TransformFromCopy(
                    root_formula,
                    den_formula,
                ),
                TransformFromCopy(
                    root_condition,
                    den_condition,
                ),
                run_time=0.80,
            )

            self.play(
                TransformFromCopy(
                    root_line[0],
                    den_line[0],
                ),
                TransformFromCopy(
                    root_line[1],
                    den_line[1],
                ),
                run_time=0.65,
            )

            filled_copy = root_line[2][0].copy()
            self.add(filled_copy)

            self.play(
                filled_copy.animate.move_to(
                    den_line[0].n2p(1)
                ),
                run_time=0.45,
            )

            self.play(
                ReplacementTransform(
                    filled_copy,
                    den_line[2][0],
                ),
                run_time=0.50,
            )

        self.play(
            FadeOut(
                VGroup(
                    root_formula,
                    root_condition,
                    root_line,
                    den_formula,
                    den_condition,
                    den_line,
                    divider,
                )
            ),
            run_time=0.65,
        )

        # ------------------------------------------------------------------
        # sqrt(x²-1) versus ln(x²-1)
        # ------------------------------------------------------------------
        root_formula = MathTex(
            r"\sqrt{x^2-1}",
            font_size=47,
        ).shift(
            UP * 1.65
        )

        root_rule = MathTex(
            r"x^2-1\geq0",
            font_size=38,
        ).next_to(
            root_formula,
            DOWN,
            buff=0.25,
        )

        root_line = make_number_line(
            -4,
            4,
            [
                (None, -1),
                (1, None),
            ],
            closed_points=(-1, 1),
            length=7.2,
        )

        root_line.next_to(
            root_rule,
            DOWN,
            buff=0.35,
        )

        root_domain = MathTex(
            r"]-\infty,-1]\cup[1,+\infty[",
            font_size=37,
            color=ACCENT,
        ).next_to(
            root_line,
            DOWN,
            buff=0.28,
        )

        log_formula = MathTex(
            r"\ln(x^2-1)",
            font_size=47,
        ).shift(
            UP * 0.40
        )

        log_rule = MathTex(
            r"x^2-1>0",
            font_size=38,
        ).next_to(
            log_formula,
            DOWN,
            buff=0.25,
        )

        log_line = make_number_line(
            -4,
            4,
            [
                (None, -1),
                (1, None),
            ],
            open_points=(-1, 1),
            length=7.2,
        )

        log_line.next_to(
            log_rule,
            DOWN,
            buff=0.35,
        )

        log_domain = MathTex(
            r"]-\infty,-1[\cup]1,+\infty[",
            font_size=37,
            color=ACCENT,
        ).next_to(
            log_line,
            DOWN,
            buff=0.28,
        )

        item = SCRIPT[10]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            self.wait_until_bookmark(
                "log_copy"
            )

            self.play(
                Write(root_formula),
                Write(root_rule),
                Create(root_line[0]),
                Create(root_line[1]),
                FadeIn(root_line[2]),
                FadeIn(root_domain),
                run_time=1.15,
            )

            root_group = VGroup(
                root_formula,
                root_rule,
                root_line,
                root_domain,
            )

            self.play(
                root_group.animate.scale(
                    0.78
                ).shift(
                    UP * 1.10
                ),
                run_time=0.65,
            )

            self.play(
                TransformFromCopy(
                    root_formula,
                    log_formula,
                ),
                TransformFromCopy(
                    root_rule,
                    log_rule,
                ),
                run_time=0.75,
            )

            self.play(
                TransformFromCopy(
                    root_line[0],
                    log_line[0],
                ),
                TransformFromCopy(
                    root_line[1],
                    log_line[1],
                ),
                run_time=0.65,
            )

            self.wait_until_bookmark(
                "log_open"
            )

            closed_copies = VGroup(
                *[
                    point.copy()
                    for point in root_line[2]
                ]
            )

            self.add(closed_copies)

            self.play(
                closed_copies.animate.move_to(
                    log_line[2]
                ),
                run_time=0.50,
            )

            self.play(
                ReplacementTransform(
                    closed_copies[0],
                    log_line[2][0],
                ),
                ReplacementTransform(
                    closed_copies[1],
                    log_line[2][1],
                ),
                FadeIn(log_domain),
                run_time=0.60,
            )

        self.play(
            FadeOut(
                VGroup(
                    root_formula,
                    root_rule,
                    root_line,
                    root_domain,
                    log_formula,
                    log_rule,
                    log_line,
                    log_domain,
                    heading,
                )
            ),
            run_time=0.70,
        )

        # ==================================================================
        # PHASE 3 — Combine constraints
        # ==================================================================
        heading = section_title(
            "3. Combiner les contraintes"
        )

        self.play(
            FadeIn(heading),
            run_time=0.4,
        )

        # ------------------------------------------------------------------
        # Independent square-root and denominator conditions
        # ------------------------------------------------------------------
        formula = MathTex(
            r"w(x)=\frac{\sqrt{x+1}}{x-2}",
            font_size=49,
        ).shift(
            UP * 1.90
        )

        root_label = MathTex(
            r"x+1\geq0\iff x\geq-1",
            font_size=36,
        )

        root_constraint = make_number_line(
            -4,
            6,
            [
                (-1, None),
            ],
            closed_points=(-1,),
            length=7.5,
        )

        root_row = VGroup(
            root_label,
            root_constraint,
        ).arrange(
            DOWN,
            buff=0.18,
        ).shift(
            UP * 0.55
        )

        den_label = MathTex(
            r"x-2\neq0\iff x\neq2",
            font_size=36,
        )

        den_constraint = make_number_line(
            -4,
            6,
            [
                (None, 2),
                (2, None),
            ],
            open_points=(2,),
            length=7.5,
        )

        den_row = VGroup(
            den_label,
            den_constraint,
        ).arrange(
            DOWN,
            buff=0.18,
        ).shift(
            DOWN * 0.70
        )

        result_line = make_number_line(
            -4,
            6,
            [
                (-1, 2),
                (2, None),
            ],
            closed_points=(-1,),
            open_points=(2,),
            length=7.5,
        ).shift(
            DOWN * 2.10
        )

        result_domain = MathTex(
            r"[-1,2[\cup]2,+\infty[",
            font_size=40,
            color=ACCENT,
        ).next_to(
            result_line,
            UP,
            buff=0.12,
        )

        item = SCRIPT[11]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            self.play(
                Write(formula),
                run_time=0.65,
            )

            self.wait_until_bookmark(
                "intersection_root"
            )

            self.play(
                Write(root_label),
                Create(root_constraint[0]),
                Create(root_constraint[1]),
                FadeIn(root_constraint[2]),
                run_time=0.90,
            )

            self.wait_until_bookmark(
                "intersection_den"
            )

            self.play(
                Write(den_label),
                Create(den_constraint[0]),
                Create(den_constraint[1]),
                FadeIn(den_constraint[2]),
                run_time=0.90,
            )

            self.wait_until_bookmark(
                "intersection_result"
            )

            self.play(
                Create(result_line[0]),
                Create(result_line[1]),
                FadeIn(result_line[2]),
                FadeIn(result_domain),
                run_time=1.00,
            )

            self.play(
                Indicate(
                    result_line,
                    color=ACCENT,
                ),
                run_time=0.65,
            )

        self.play(
            FadeOut(
                VGroup(
                    formula,
                    root_row,
                    den_row,
                    result_line,
                    result_domain,
                )
            ),
            run_time=0.65,
        )

        # ------------------------------------------------------------------
        # Quotient inside a square root
        # ------------------------------------------------------------------
        formula = MathTex(
            r"z(x)=\sqrt{\frac{x-1}{x+2}}",
            font_size=50,
        ).shift(
            UP * 2.00
        )

        condition = MathTex(
            r"\frac{x-1}{x+2}\geq0",
            font_size=42,
        ).next_to(
            formula,
            DOWN,
            buff=0.25,
        )

        wrong_shortcut = MathTex(
            r"x-1\geq0\quad\text{seulement}",
            font_size=34,
            color=FORBIDDEN,
        ).next_to(
            condition,
            RIGHT,
            buff=0.45,
        )

        wrong_cross = Cross(
            wrong_shortcut,
            stroke_color=FORBIDDEN,
            stroke_width=4,
        )

        table = make_sign_table().scale(
            0.88
        ).shift(
            DOWN * 0.38
        )

        quotient_line = make_number_line(
            -6,
            5,
            [
                (None, -2),
                (1, None),
            ],
            open_points=(-2,),
            closed_points=(1,),
            length=8.2,
        ).shift(
            DOWN * 2.12
        )

        quotient_domain = MathTex(
            r"]-\infty,-2[\cup[1,+\infty[",
            font_size=39,
            color=ACCENT,
        ).next_to(
            quotient_line,
            UP,
            buff=0.12,
        )

        item = SCRIPT[12]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            self.play(
                Write(formula),
                Write(condition),
                run_time=0.80,
            )

            self.wait_until_bookmark(
                "quotient_warning"
            )

            self.play(
                FadeIn(wrong_shortcut),
                Create(wrong_cross),
                run_time=0.65,
            )

            self.play(
                FadeOut(
                    VGroup(
                        wrong_shortcut,
                        wrong_cross,
                    )
                ),
                run_time=0.35,
            )

            self.wait_until_bookmark(
                "quotient_rows"
            )

            self.play(
                Create(table[5]),
                Create(table[6]),
                FadeIn(table[0]),
                FadeIn(table[1]),
                Create(table[7]),
                FadeIn(table[8]),
                run_time=0.85,
            )

            self.play(
                FadeIn(table[2]),
                run_time=0.45,
            )

            self.play(
                FadeIn(table[3]),
                run_time=0.45,
            )

            self.play(
                TransformFromCopy(
                    VGroup(
                        table[2],
                        table[3],
                    ),
                    table[4],
                ),
                run_time=0.70,
            )

            self.wait_until_bookmark(
                "quotient_domain"
            )

            self.play(
                Create(quotient_line[0]),
                Create(quotient_line[1]),
                FadeIn(quotient_line[2]),
                FadeIn(quotient_domain),
                run_time=0.95,
            )

        self.play(
            FadeOut(
                VGroup(
                    formula,
                    condition,
                    table,
                    quotient_line,
                    quotient_domain,
                    heading,
                )
            ),
            run_time=0.70,
        )

        # ==================================================================
        # PHASE 4 — The removable-hole trap
        # ==================================================================
        heading = section_title(
            "4. Éviter le piège de la simplification"
        )

        original = MathTex(
            r"F(x)=\frac{x^2-4}{x-2}",
            font_size=50,
        ).shift(
            LEFT * 3.25 + UP * 1.55
        )

        factorized = MathTex(
            r"F(x)=\frac{(x-2)(x+2)}{x-2}",
            font_size=44,
        ).next_to(
            original,
            DOWN,
            buff=0.32,
        )

        simplified = MathTex(
            r"F(x)=x+2",
            r"\quad\text{avec}\quad",
            r"x\neq2",
            font_size=41,
        ).next_to(
            factorized,
            DOWN,
            buff=0.32,
        )

        warning_box = SurroundingRectangle(
            simplified[2],
            color=FORBIDDEN,
            buff=0.10,
            stroke_width=3,
        )

        axes = Axes(
            x_range=[-4, 5, 1],
            y_range=[-2, 7, 1],
            x_length=5.0,
            y_length=5.0,
            axis_config={
                "color": BLACK,
                "stroke_width": 2,
            },
            tips=False,
        ).shift(
            RIGHT * 3.45 + DOWN * 0.10
        )

        line_graph = axes.plot(
            lambda x: x + 2,
            x_range=[-4, 5],
            color=ACCENT,
        )

        hole = Circle(
            radius=0.10,
            stroke_color=FORBIDDEN,
            stroke_width=3.2,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(
            axes.c2p(2, 4)
        )

        hole_label = MathTex(
            r"(2,4)",
            font_size=29,
            color=FORBIDDEN,
        ).next_to(
            hole,
            UP + RIGHT,
            buff=0.12,
        )

        item = SCRIPT[13]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            self.play(
                FadeIn(heading),
                Write(original),
                run_time=0.75,
            )

            self.wait_until_bookmark(
                "hole_factor"
            )

            self.play(
                TransformFromCopy(
                    original,
                    factorized,
                ),
                run_time=0.90,
            )

            self.play(
                TransformFromCopy(
                    factorized,
                    simplified,
                ),
                run_time=0.85,
            )

            self.wait_until_bookmark(
                "hole_warning"
            )

            self.play(
                Create(warning_box),
                Circumscribe(
                    simplified[2],
                    color=FORBIDDEN,
                ),
                run_time=0.75,
            )

            self.wait_until_bookmark(
                "hole_graph"
            )

            self.play(
                Create(axes),
                Create(line_graph),
                run_time=0.95,
            )

            self.play(
                FadeIn(
                    hole,
                    scale=1.6,
                ),
                FadeIn(hole_label),
                run_time=0.55,
            )

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    original,
                    factorized,
                    simplified,
                    warning_box,
                    axes,
                    line_graph,
                    hole,
                    hole_label,
                )
            ),
            run_time=0.70,
        )

        # ==================================================================
        # FINAL — Formula scanner
        # ==================================================================
        heading = section_title(
            "La méthode : scanner la formule"
        )

        den_formula = MathTex(
            r"\frac{1}{x-3}",
            font_size=48,
            substrings_to_isolate=[
                r"x-3",
            ],
        )

        den_formula.set_color_by_tex(
            r"x-3",
            ACCENT,
        )

        root_formula = MathTex(
            r"\sqrt{5-x}",
            font_size=48,
            substrings_to_isolate=[
                r"5-x",
            ],
        )

        root_formula.set_color_by_tex(
            r"5-x",
            ACCENT,
        )

        log_formula = MathTex(
            r"\ln(x^2-4)",
            font_size=48,
            substrings_to_isolate=[
                r"x^2-4",
            ],
        )

        log_formula.set_color_by_tex(
            r"x^2-4",
            ACCENT,
        )

        formulas = VGroup(
            den_formula,
            root_formula,
            log_formula,
        ).arrange(
            RIGHT,
            buff=1.15,
        ).shift(
            UP * 1.18
        )

        cards = VGroup(
            *[
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
            ]
        )

        formulas.set_z_index(2)

        scanner = SurroundingRectangle(
            cards[0],
            color=ACCENT,
            buff=0.05,
            stroke_width=4,
        )

        rules = VGroup(
            MathTex(
                r"\text{dénominateur}\neq0",
                font_size=38,
            ),
            MathTex(
                r"\text{racine carrée}:"
                r"\ \text{contenu}\geq0",
                font_size=38,
            ),
            MathTex(
                r"\text{logarithme}:"
                r"\ \text{argument}>0",
                font_size=38,
            ),
            MathTex(
                r"\text{plusieurs conditions}"
                r"\Longrightarrow"
                r"\text{intersection}",
                font_size=38,
                color=ACCENT,
            ),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.27,
        ).shift(
            DOWN * 0.92
        )

        item = SCRIPT[14]

        with self.narrated(item):
            self.set_caption(
                item["caption"]
            )

            self.play(
                FadeIn(heading),
                FadeIn(cards),
                Write(formulas),
                run_time=0.85,
            )

            self.wait_until_bookmark(
                "scan_den"
            )

            self.play(
                Create(scanner),
                FadeIn(
                    rules[0],
                    shift=UP * 0.10,
                ),
                run_time=0.65,
            )

            self.wait_until_bookmark(
                "scan_root"
            )

            self.play(
                Transform(
                    scanner,
                    SurroundingRectangle(
                        cards[1],
                        color=ACCENT,
                        buff=0.05,
                        stroke_width=4,
                    ),
                ),
                FadeIn(
                    rules[1],
                    shift=UP * 0.10,
                ),
                run_time=0.65,
            )

            self.wait_until_bookmark(
                "scan_log"
            )

            self.play(
                Transform(
                    scanner,
                    SurroundingRectangle(
                        cards[2],
                        color=ACCENT,
                        buff=0.05,
                        stroke_width=4,
                    ),
                ),
                FadeIn(
                    rules[2],
                    shift=UP * 0.10,
                ),
                run_time=0.65,
            )

            self.wait_until_bookmark(
                "scan_intersection"
            )

            self.play(
                FadeIn(
                    rules[3],
                    shift=UP * 0.10,
                ),
                run_time=0.55,
            )

            self.play(
                Circumscribe(
                    rules[3],
                    color=ACCENT,
                ),
                run_time=0.75,
            )

        self.wait(1.2)

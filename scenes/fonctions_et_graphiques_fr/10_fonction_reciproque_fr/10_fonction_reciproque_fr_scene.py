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
X_SSML = tts.X
Y_SSML = tts.Y


def proportional_axes(x_range, y_range, unit_size=0.6, **kwargs):
    """Create axes with the same visible scale on both coordinates."""
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
            "font_size": 20,
        },
        **kwargs,
    )


def fit_width(mobject, max_width=13.0):
    if mobject.width > max_width:
        mobject.scale_to_fit_width(max_width)
    return mobject


def section_heading(text):
    heading = fit_width(Text(text, font_size=31, color=BLUE_D), 12.8)
    heading.to_edge(UP, buff=0.35)
    return heading


def validate_layout(name, mobjects, separated_pairs=(), margin=0.16):
    """Fail early if a key layout region leaves the frame or overlaps another.

    The checks concern top-level explanatory regions. Intended containment, such as
    text inside a box or a point on a graph, is deliberately not tested.
    """
    frame_left = -config.frame_width / 2 + margin
    frame_right = config.frame_width / 2 - margin
    frame_bottom = -config.frame_height / 2 + margin
    frame_top = config.frame_height / 2 - margin

    for label, mob in mobjects:
        if (
            mob.get_left()[0] < frame_left
            or mob.get_right()[0] > frame_right
            or mob.get_bottom()[1] < frame_bottom
            or mob.get_top()[1] > frame_top
        ):
            raise ValueError(f"[{name}] {label} leaves the safe frame area.")

    for label_a, mob_a, label_b, mob_b, gap in separated_pairs:
        horizontally_separated = (
            mob_a.get_right()[0] + gap <= mob_b.get_left()[0]
            or mob_b.get_right()[0] + gap <= mob_a.get_left()[0]
        )
        vertically_separated = (
            mob_a.get_top()[1] + gap <= mob_b.get_bottom()[1]
            or mob_b.get_top()[1] + gap <= mob_a.get_bottom()[1]
        )
        if not (horizontally_separated or vertically_separated):
            raise ValueError(
                f"[{name}] layout overlap between {label_a} and {label_b}."
            )


SCRIPT = [
    {
        "caption": "Comment retrouver l'entrée à partir de la sortie ?",
        "body": (
            "Une fonction transforme une entrée en une sortie. "
            "La question centrale est maintenant la suivante : "
            "si nous connaissons seulement la sortie, pouvons-nous retrouver l'entrée?"
        ),
    },
    {
        "caption": "La fonction f envoie 1 vers 3.",
        "body": (
            f"Prenons {F_SSML} de {X_SSML} égale deux {X_SSML} plus un. "
            f"Avec l'entrée un, la fonction {F_SSML} produit la sortie trois."
        ),
    },
    {
        "caption": "La fonction réciproque fait le trajet inverse.",
        "body": (
            "Pour revenir de trois vers un, il nous faut une nouvelle fonction "
            f"qui inverse le trajet. On la note {F_SSML} exposant moins un. "
            "Elle prend l'ancienne sortie comme nouvelle entrée."
        ),
    },
    {
        "caption": "Appliquer f puis sa réciproque ramène au départ.",
        "body": (
            f"En général, si {F_SSML} envoie {X_SSML} vers {Y_SSML}, "
            f"alors la réciproque envoie {Y_SSML} vers {X_SSML}. "
            f"Ainsi, {F_SSML} exposant moins un de {F_SSML} de {X_SSML} "
            f"redonne {X_SSML}. Le trajet fonctionne aussi dans l'autre sens."
        ),
    },
    {
        "caption": "On trouve la règle inverse en isolant l'entrée.",
        "body": (
            "Comment trouver la formule de la réciproque? "
            f"Partons de {Y_SSML} égale deux {X_SSML} plus un, "
            f"puis isolons {X_SSML}. On soustrait un et on divise par deux."
        ),
    },
    {
        "caption": "L'ancienne sortie devient l'entrée de la réciproque.",
        "body": (
            f"Nous avons obtenu {X_SSML} égale {Y_SSML} moins un, divisé par deux. "
            "Dans la fonction réciproque, l'ancienne sortie devient la nouvelle entrée. "
            f"On écrit donc {F_SSML} exposant moins un de {X_SSML} "
            f"égale {X_SSML} moins un, divisé par deux."
        ),
    },
    {
        "caption": "Graphiquement, les coordonnées sont échangées.",
        "body": (
            "Regardons maintenant le même phénomène sur un graphique. "
            "Le point de coordonnées un, trois appartient au graphe de la fonction. "
            "Quand on inverse l'entrée et la sortie, il devient le point trois, un."
        ),
    },
    {
        "caption": "Les deux graphes sont symétriques par rapport à y = x.",
        "body": (
            "Chaque point du graphe subit le même échange de coordonnées. "
            f"Le point {X_SSML}, {Y_SSML} devient le point {Y_SSML}, {X_SSML}. "
            f"C'est exactement une réflexion par rapport à la droite {Y_SSML} égale {X_SSML}."
        ),
    },
    {
        "caption": "Une réciproque exige une sortie associée à une seule entrée.",
        "body": (
            "Mais toute fonction n'a pas automatiquement une fonction réciproque. "
            "Pour la fonction carré sur tous les nombres réels, moins deux et deux "
            "produisent tous les deux la sortie quatre. À partir de quatre, "
            "on ne peut pas choisir une entrée unique."
        ),
    },
    {
        "caption": "On peut parfois restreindre le domaine.",
        "body": (
            "Si l'on garde seulement les entrées positives ou nulles, "
            "chaque sortie correspond alors à une seule entrée. "
            "Sur ce domaine restreint, la fonction carré possède la racine carrée comme réciproque."
        ),
    },
    {
        "caption": "La réciproque échange l'entrée et la sortie.",
        "body": (
            "Retenons trois idées. La réciproque échange l'entrée et la sortie. "
            "La composition dans un sens puis dans l'autre ramène au point de départ. "
            "Et les graphes sont symétriques par rapport à la droite y égale x. "
            f"Attention : {F_SSML} exposant moins un ne signifie pas un divisé par {F_SSML}."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class FonctionReciproqueFR(VoiceoverScene if VoiceoverScene is not None else Scene):
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
    def narrated(self, item):
        text = tts.ssml(item["body"])
        if self._voiceover_enabled:
            with self.voiceover(text=text, subcaption=item["caption"]) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_for_narration(self, tracker, animation_time, fallback=0.55):
        if self._voiceover_enabled:
            self.wait(max(tracker.duration - animation_time, 0.25))
        else:
            self.wait(fallback)

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        accent = BLUE_D
        inverse_color = GREEN_D
        muted = GRAY_D

        title = Text("Fonction réciproque", font_size=44)
        title.to_edge(UP, buff=0.25)

        # ------------------------------------------------------------------
        # Act 1 — Create the need for an inverse before naming it.
        # ------------------------------------------------------------------
        question = Text(
            "Comment retrouver l'entrée à partir de la sortie ?",
            font_size=34,
        )
        question.next_to(title, DOWN, buff=0.65)

        input_box = RoundedRectangle(
            width=1.55,
            height=1.05,
            corner_radius=0.18,
            color=accent,
            stroke_width=3,
            fill_color=accent,
            fill_opacity=0.08,
        )
        input_value = MathTex("1", font_size=46, color=accent).move_to(input_box)
        input_caption = Text("entrée", font_size=25, color=accent).next_to(
            input_box, DOWN, buff=0.15
        )

        output_box = RoundedRectangle(
            width=1.55,
            height=1.05,
            corner_radius=0.18,
            color=inverse_color,
            stroke_width=3,
            fill_color=inverse_color,
            fill_opacity=0.08,
        )
        output_value = MathTex("3", font_size=46, color=inverse_color).move_to(output_box)
        output_caption = Text("sortie", font_size=25, color=inverse_color).next_to(
            output_box, DOWN, buff=0.15
        )

        forward_arrow = Arrow(LEFT, RIGHT, color=BLACK, stroke_width=4, buff=0)
        forward_label = MathTex(r"f(x)=2x+1", font_size=34).next_to(
            forward_arrow, UP, buff=0.18
        )

        forward_row = VGroup(
            VGroup(input_box, input_value, input_caption),
            VGroup(forward_arrow, forward_label),
            VGroup(output_box, output_value, output_caption),
        ).arrange(RIGHT, buff=0.72)
        forward_row.move_to(DOWN * 0.45)

        reverse_question = Text(
            "Et pour revenir de 3 vers 1 ?",
            font_size=30,
            color=muted,
        ).next_to(forward_row, DOWN, buff=0.72)

        validate_layout(
            "act 1",
            [("title", title), ("question", question), ("row", forward_row),
             ("reverse question", reverse_question)],
            [
                ("title", title, "question", question, 0.18),
                ("question", question, "row", forward_row, 0.25),
                ("row", forward_row, "reverse question", reverse_question, 0.22),
            ],
        )

        with self.narrated(SCRIPT[0]) as tracker:
            self.play(FadeIn(title), FadeIn(question), run_time=1.2)
            self.wait_for_narration(tracker, 1.2, fallback=0.9)

        with self.narrated(SCRIPT[1]) as tracker:
            self.play(
                FadeIn(input_box),
                FadeIn(input_value),
                FadeIn(input_caption),
                run_time=0.8,
            )
            self.play(GrowArrow(forward_arrow), FadeIn(forward_label), run_time=1.0)
            self.play(
                FadeIn(output_box),
                FadeIn(output_value),
                FadeIn(output_caption),
                run_time=0.8,
            )
            self.play(FadeIn(reverse_question), run_time=0.7)
            self.wait_for_narration(tracker, 3.3, fallback=1.0)

        reverse_arrow = Arrow(RIGHT, LEFT, color=inverse_color, stroke_width=4, buff=0)
        reverse_arrow.move_to(forward_arrow)
        reverse_label = MathTex(r"f^{-1}", font_size=38, color=inverse_color)
        reverse_label.next_to(reverse_arrow, UP, buff=0.18)

        with self.narrated(SCRIPT[2]) as tracker:
            self.play(FadeOut(reverse_question), run_time=0.5)
            self.play(
                FadeOut(forward_arrow),
                FadeOut(forward_label),
                run_time=0.5,
            )
            self.play(GrowArrow(reverse_arrow), FadeIn(reverse_label), run_time=1.0)
            self.play(
                Indicate(output_value, color=inverse_color, scale_factor=1.2),
                Indicate(input_value, color=accent, scale_factor=1.2),
                run_time=1.2,
            )
            self.wait_for_narration(tracker, 2.4, fallback=1.0)

        act1 = VGroup(
            question,
            input_box,
            input_value,
            input_caption,
            output_box,
            output_value,
            output_caption,
            reverse_arrow,
            reverse_label,
        )

        # ------------------------------------------------------------------
        # Act 2 — Input/output and composition viewpoints.
        # ------------------------------------------------------------------
        heading_comp = section_heading("1. Revenir au point de départ")
        general_pair = MathTex(
            r"x\xrightarrow{\ f\ }y",
            r"\qquad\Longleftrightarrow\qquad",
            r"y\xrightarrow{\ f^{-1}\ }x",
            font_size=43,
        )
        general_pair[2].set_color(inverse_color)
        general_pair.move_to(UP * 1.05)

        comp_forward = MathTex(r"f^{-1}(f(x))=x", font_size=42)
        comp_reverse = MathTex(r"f(f^{-1}(y))=y", font_size=42)
        comp_group = VGroup(comp_forward, comp_reverse).arrange(DOWN, buff=0.5)
        comp_group.move_to(DOWN * 1.2)

        comp_box = SurroundingRectangle(
            comp_group,
            buff=0.34,
            color=accent,
            stroke_width=3,
            corner_radius=0.16,
        )

        validate_layout(
            "act 2",
            [("heading", heading_comp), ("mapping", general_pair),
             ("composition box", comp_box)],
            [
                ("heading", heading_comp, "mapping", general_pair, 0.35),
                ("mapping", general_pair, "composition box", comp_box, 0.35),
            ],
        )

        with self.narrated(SCRIPT[3]) as tracker:
            self.play(FadeOut(VGroup(title, act1)), run_time=0.9)
            self.play(FadeIn(heading_comp), run_time=0.8)
            self.play(Write(general_pair), run_time=1.4)
            self.play(Write(comp_forward), run_time=1.0)
            self.wait(0.45)
            self.play(Write(comp_reverse), run_time=1.0)
            self.play(Create(comp_box), run_time=0.7)
            self.wait_for_narration(tracker, 5.8, fallback=1.0)

        comp_scene = VGroup(heading_comp, general_pair, comp_group, comp_box)

        # ------------------------------------------------------------------
        # Act 3 — Algebraic construction.
        # ------------------------------------------------------------------
        heading_alg = section_heading("2. Trouver la règle inverse")
        algebra_prompt = Text(
            "On part de la sortie et on retrouve l'entrée.",
            font_size=29,
            color=muted,
        ).next_to(heading_alg, DOWN, buff=0.42)

        eq1 = MathTex(r"y=2x+1", font_size=46)
        eq2 = MathTex(r"y-1=2x", font_size=46)
        eq3 = MathTex(r"x=\frac{y-1}{2}", font_size=46)
        equations = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.52, aligned_edge=LEFT)
        equations.move_to(LEFT * 3.1 + DOWN * 0.5)

        step1_note = Text("soustraire 1", font_size=25, color=accent)
        step1_note.next_to(eq2, RIGHT, buff=0.55)
        step2_note = Text("diviser par 2", font_size=25, color=accent)
        step2_note.next_to(eq3, RIGHT, buff=0.55)

        final_inverse = MathTex(
            r"f^{-1}(x)=\frac{x-1}{2}",
            font_size=45,
            color=inverse_color,
        )
        final_inverse.move_to(RIGHT * 3.25 + DOWN * 0.35)
        final_box = SurroundingRectangle(
            final_inverse,
            buff=0.3,
            color=inverse_color,
            stroke_width=3,
            corner_radius=0.16,
        )
        rename_note = Text(
            "ancienne sortie → nouvelle entrée",
            font_size=25,
            color=inverse_color,
        ).next_to(final_box, DOWN, buff=0.28)

        algebra_left = VGroup(equations, step1_note, step2_note)
        algebra_right = VGroup(final_box, rename_note)
        validate_layout(
            "act 3",
            [("heading", heading_alg), ("prompt", algebra_prompt),
             ("left derivation", algebra_left), ("inverse result", algebra_right)],
            [
                ("heading", heading_alg, "prompt", algebra_prompt, 0.18),
                ("prompt", algebra_prompt, "left derivation", algebra_left, 0.2),
                ("left derivation", algebra_left, "inverse result", algebra_right, 0.22),
            ],
        )

        with self.narrated(SCRIPT[4]) as tracker:
            self.play(FadeOut(comp_scene), run_time=0.9)
            self.play(FadeIn(heading_alg), FadeIn(algebra_prompt), run_time=0.9)
            self.play(Write(eq1), run_time=0.9)
            self.play(Write(eq2), FadeIn(step1_note), run_time=1.0)
            self.play(Write(eq3), FadeIn(step2_note), run_time=1.0)
            self.wait_for_narration(tracker, 3.8, fallback=0.9)

        with self.narrated(SCRIPT[5]) as tracker:
            self.play(
                FadeOut(step1_note),
                FadeOut(step2_note),
                run_time=0.5,
            )
            self.play(TransformFromCopy(eq3, final_inverse), run_time=1.2)
            self.play(Create(final_box), FadeIn(rename_note), run_time=0.9)
            self.play(Circumscribe(final_inverse, color=inverse_color), run_time=1.1)
            self.wait_for_narration(tracker, 3.2, fallback=1.0)

        algebra_scene = VGroup(
            heading_alg,
            algebra_prompt,
            equations,
            final_inverse,
            final_box,
            rename_note,
        )

        # ------------------------------------------------------------------
        # Act 4 — Graphical reflection with a single coordinate plane.
        # ------------------------------------------------------------------
        heading_graph = section_heading("3. Échanger les coordonnées")

        axes = proportional_axes(
            x_range=[-1, 6, 1],
            y_range=[-1, 6, 1],
            unit_size=0.72,
        )
        axes.shift(LEFT * 2.35 + DOWN * 0.42)
        axes_labels = axes.get_axis_labels(
            MathTex("x", font_size=28),
            MathTex("y", font_size=28),
        )

        f_graph = axes.plot(
            lambda x: 2 * x + 1,
            x_range=[-0.5, 2.45],
            color=BLACK,
            stroke_width=4,
        )
        inv_graph = axes.plot(
            lambda x: (x - 1) / 2,
            x_range=[0, 5.8],
            color=inverse_color,
            stroke_width=4,
        )
        mirror_line = axes.plot(
            lambda x: x,
            x_range=[-0.7, 5.8],
            color=accent,
            stroke_width=3,
        )

        f_graph_label = MathTex(r"y=f(x)", font_size=30)
        f_graph_label.next_to(axes.c2p(1.65, 4.3), LEFT + UP, buff=0.08)
        inv_graph_label = MathTex(
            r"y=f^{-1}(x)", font_size=30, color=inverse_color
        )
        inv_graph_label.next_to(axes.c2p(4.6, 1.8), DOWN, buff=0.12)
        mirror_label = MathTex(r"y=x", font_size=29, color=accent)
        mirror_label.next_to(axes.c2p(4.65, 4.65), RIGHT, buff=0.1)

        p = Dot(axes.c2p(1, 3), color=BLACK, radius=0.075)
        q = Dot(axes.c2p(3, 1), color=inverse_color, radius=0.075)
        reflection_segment = DashedLine(
            axes.c2p(1, 3),
            axes.c2p(3, 1),
            color=accent,
            stroke_width=3,
            dash_length=0.12,
        )

        coordinate_panel = RoundedRectangle(
            width=4.25,
            height=3.7,
            corner_radius=0.2,
            color=GRAY_B,
            stroke_width=2,
            fill_color=GRAY_E,
            fill_opacity=0.22,
        )
        coordinate_panel.move_to(RIGHT * 3.75 + DOWN * 0.32)

        point_before = MathTex(r"(1,3)", font_size=43)
        swap_arrow = MathTex(r"\longrightarrow", font_size=42, color=accent)
        point_after = MathTex(r"(3,1)", font_size=43, color=inverse_color)
        point_row = VGroup(point_before, swap_arrow, point_after).arrange(RIGHT, buff=0.3)
        point_row.move_to(coordinate_panel.get_center() + UP * 0.72)

        coordinate_words = VGroup(
            Text("entrée", font_size=24, color=accent),
            Text("sortie", font_size=24, color=inverse_color),
        ).arrange(RIGHT, buff=1.2)
        coordinate_words.next_to(point_before, DOWN, buff=0.24)

        general_swap = MathTex(
            r"(x,y)\longleftrightarrow(y,x)",
            font_size=38,
        )
        general_swap.move_to(coordinate_panel.get_center() + DOWN * 0.6)

        graph_left = VGroup(axes, axes_labels, f_graph_label, inv_graph_label, mirror_label)
        graph_right = VGroup(coordinate_panel, point_row, coordinate_words, general_swap)
        validate_layout(
            "act 4",
            [("heading", heading_graph), ("graph region", graph_left),
             ("coordinate panel", graph_right)],
            [
                ("heading", heading_graph, "graph region", graph_left, 0.22),
                ("heading", heading_graph, "coordinate panel", graph_right, 0.22),
                ("graph region", graph_left, "coordinate panel", graph_right, 0.28),
            ],
        )

        with self.narrated(SCRIPT[6]) as tracker:
            self.play(FadeOut(algebra_scene), run_time=0.9)
            self.play(FadeIn(heading_graph), run_time=0.7)
            self.play(Create(axes), FadeIn(axes_labels), run_time=1.2)
            self.play(Create(f_graph), FadeIn(f_graph_label), run_time=1.1)
            self.play(FadeIn(p), run_time=0.6)
            self.play(
                FadeIn(coordinate_panel),
                Write(point_before),
                FadeIn(coordinate_words),
                run_time=1.0,
            )
            self.play(Write(swap_arrow), Write(point_after), run_time=1.0)
            self.play(Create(reflection_segment), FadeIn(q), run_time=1.1)
            self.wait_for_narration(tracker, 6.0, fallback=0.9)

        with self.narrated(SCRIPT[7]) as tracker:
            self.play(Create(mirror_line), FadeIn(mirror_label), run_time=1.1)
            self.play(Write(general_swap), run_time=0.9)
            self.play(Create(inv_graph), FadeIn(inv_graph_label), run_time=1.3)
            self.play(
                Indicate(p, color=accent, scale_factor=1.35),
                Indicate(q, color=accent, scale_factor=1.35),
                run_time=1.2,
            )
            self.wait_for_narration(tracker, 4.5, fallback=1.0)

        graph_scene = VGroup(
            heading_graph,
            axes,
            axes_labels,
            f_graph,
            inv_graph,
            mirror_line,
            f_graph_label,
            inv_graph_label,
            mirror_label,
            p,
            q,
            reflection_segment,
            coordinate_panel,
            point_row,
            coordinate_words,
            general_swap,
        )

        # ------------------------------------------------------------------
        # Act 5 — Existence condition and a domain restriction.
        # ------------------------------------------------------------------
        heading_condition = section_heading("4. Une réciproque existe-t-elle toujours ?")

        square_axes = proportional_axes(
            x_range=[-3, 3, 1],
            y_range=[0, 6, 1],
            unit_size=0.66,
        )
        square_axes.shift(LEFT * 3.0 + DOWN * 0.62)
        square_labels = square_axes.get_axis_labels(
            MathTex("x", font_size=28),
            MathTex("y", font_size=28),
        )
        square_graph = square_axes.plot(
            lambda x: x**2,
            x_range=[-2.4, 2.4],
            color=BLACK,
            stroke_width=4,
        )
        left_square_dot = Dot(square_axes.c2p(-2, 4), color=accent, radius=0.075)
        right_square_dot = Dot(square_axes.c2p(2, 4), color=accent, radius=0.075)
        horizontal_test = DashedLine(
            square_axes.c2p(-2.65, 4),
            square_axes.c2p(2.65, 4),
            color=accent,
            stroke_width=3,
            dash_length=0.12,
        )
        square_label = MathTex(r"f(x)=x^2", font_size=31)
        square_label.next_to(square_axes.c2p(1.7, 3.2), RIGHT, buff=0.1)

        ambiguity_panel = RoundedRectangle(
            width=5.15,
            height=3.75,
            corner_radius=0.2,
            color=GRAY_B,
            stroke_width=2,
            fill_color=GRAY_E,
            fill_opacity=0.22,
        )
        ambiguity_panel.move_to(RIGHT * 3.45 + DOWN * 0.38)

        two_inputs = VGroup(
            MathTex(r"-2\xrightarrow{\ f\ }4", font_size=38),
            MathTex(r"2\xrightarrow{\ f\ }4", font_size=38),
        ).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        two_inputs.move_to(ambiguity_panel.get_center() + UP * 0.72)

        ambiguity_question = Text(
            "Depuis 4, quelle entrée choisir ?",
            font_size=27,
            color=accent,
        )
        ambiguity_question.move_to(ambiguity_panel.get_center() + DOWN * 0.44)

        no_inverse = MathTex(
            r"\text{Pas de réciproque sur }\mathbb{R}",
            font_size=34,
            color=RED_D,
        )
        no_inverse.next_to(ambiguity_question, DOWN, buff=0.42)

        condition_left = VGroup(square_axes, square_labels, square_label)
        condition_right = VGroup(ambiguity_panel, two_inputs, ambiguity_question, no_inverse)
        validate_layout(
            "act 5",
            [("heading", heading_condition), ("parabola region", condition_left),
             ("ambiguity panel", condition_right)],
            [
                ("heading", heading_condition, "parabola region", condition_left, 0.2),
                ("heading", heading_condition, "ambiguity panel", condition_right, 0.2),
                ("parabola region", condition_left, "ambiguity panel", condition_right, 0.25),
            ],
        )

        with self.narrated(SCRIPT[8]) as tracker:
            self.play(FadeOut(graph_scene), run_time=0.9)
            self.play(FadeIn(heading_condition), run_time=0.7)
            self.play(Create(square_axes), FadeIn(square_labels), run_time=1.1)
            self.play(Create(square_graph), FadeIn(square_label), run_time=1.0)
            self.play(
                FadeIn(ambiguity_panel),
                Write(two_inputs),
                run_time=1.1,
            )
            self.play(
                Create(horizontal_test),
                FadeIn(left_square_dot),
                FadeIn(right_square_dot),
                run_time=1.0,
            )
            self.play(FadeIn(ambiguity_question), run_time=0.8)
            self.play(FadeIn(no_inverse), run_time=0.8)
            self.wait_for_narration(tracker, 6.5, fallback=1.0)

        right_branch = square_axes.plot(
            lambda x: x**2,
            x_range=[0, 2.4],
            color=inverse_color,
            stroke_width=6,
        )
        restriction = MathTex(r"x\geq 0", font_size=35, color=inverse_color)
        restriction.move_to(ambiguity_panel.get_center() + UP * 0.8)
        restricted_rule = MathTex(
            r"f^{-1}(x)=\sqrt{x}",
            font_size=43,
            color=inverse_color,
        )
        restricted_rule.move_to(ambiguity_panel.get_center() + DOWN * 0.25)
        unique_note = Text(
            "une sortie → une seule entrée",
            font_size=25,
            color=inverse_color,
        )
        unique_note.next_to(restricted_rule, DOWN, buff=0.35)

        with self.narrated(SCRIPT[9]) as tracker:
            self.play(
                FadeOut(two_inputs),
                FadeOut(ambiguity_question),
                FadeOut(no_inverse),
                run_time=0.7,
            )
            self.play(Create(right_branch), FadeIn(restriction), run_time=1.1)
            self.play(Write(restricted_rule), FadeIn(unique_note), run_time=1.1)
            self.play(
                FadeOut(left_square_dot),
                FadeOut(horizontal_test),
                run_time=0.7,
            )
            self.wait_for_narration(tracker, 3.6, fallback=1.0)

        condition_scene = VGroup(
            heading_condition,
            square_axes,
            square_labels,
            square_graph,
            square_label,
            right_square_dot,
            right_branch,
            ambiguity_panel,
            restriction,
            restricted_rule,
            unique_note,
        )

        # ------------------------------------------------------------------
        # Final stable summary — deliberately sparse and vertically spaced.
        # ------------------------------------------------------------------
        summary_title = Text("À retenir", font_size=42)
        summary_title.to_edge(UP, buff=0.45)

        summary_1 = MathTex(
            r"x\xrightarrow{\ f\ }y",
            r"\quad\Longleftrightarrow\quad",
            r"y\xrightarrow{\ f^{-1}\ }x",
            font_size=39,
        )
        summary_2 = MathTex(
            r"f^{-1}(f(x))=x",
            r"\qquad",
            r"f(f^{-1}(y))=y",
            font_size=37,
        )
        summary_3 = MathTex(
            r"(x,y)\longleftrightarrow(y,x)"
            r"\quad\text{ : symétrie par rapport à }y=x",
            font_size=34,
        )
        summary_rows = VGroup(summary_1, summary_2, summary_3).arrange(
            DOWN,
            buff=0.72,
        )
        summary_rows.move_to(UP * 0.15)

        warning = MathTex(
            r"f^{-1}(x)\neq\frac{1}{f(x)}",
            font_size=39,
            color=RED_D,
        )
        warning_box = SurroundingRectangle(
            warning,
            buff=0.28,
            color=RED_D,
            stroke_width=3,
            corner_radius=0.16,
        )
        warning_group = VGroup(warning, warning_box)
        warning_group.to_edge(DOWN, buff=0.45)

        validate_layout(
            "summary",
            [("title", summary_title), ("summary rows", summary_rows),
             ("warning", warning_group)],
            [
                ("title", summary_title, "summary rows", summary_rows, 0.25),
                ("summary rows", summary_rows, "warning", warning_group, 0.3),
            ],
        )

        with self.narrated(SCRIPT[10]) as tracker:
            self.play(FadeOut(condition_scene), run_time=0.9)
            self.play(FadeIn(summary_title), run_time=0.7)
            self.play(Write(summary_1), run_time=1.0)
            self.play(Write(summary_2), run_time=1.0)
            self.play(Write(summary_3), run_time=1.1)
            self.play(FadeIn(warning), Create(warning_box), run_time=1.0)
            self.wait_for_narration(tracker, 4.8, fallback=1.2)

        self.wait(1.2)

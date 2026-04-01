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

from tools.tts import A, B, C, Y, ET


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class FunctionIntuitive(VoiceoverScene if VoiceoverScene is not None else Scene):
    def _setup_pacing(self):
        # PACE_FACTOR > 1.0 makes the whole scene slower.
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
                "[voiceover] Missing Azure Speech credentials. Set AZURE_SUBSCRIPTION_KEY/AZURE_SERVICE_REGION "
                "or SPEECH_KEY/SPEECH_REGION. Rendering without narration."
            )
            return

        # Support either naming convention for Azure credentials.
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
        accent = BLUE
        logo = ImageMobject("/Users/xiaxiao/Desktop/math_video_project/assets/branding/uqam_logo.png")

        self.play(FadeIn(logo, shift=0.2*UP), run_time=0.6)
        self.play(logo.animate.scale(0.5), run_time=1.0)
        self.play(logo.animate.scale(1.0), run_time=1.0)
        self.play(FadeOut(logo, shift=0.2*UP), run_time=0.6)

        # ---------------------------
        # 1) TITRE (0-6s)
        # VO: "Qu'est-ce qu'une fonction ? Commençons avec une idée intuitive."
        # ---------------------------
        title = Text("Qu'est-ce qu'une fonction (d'une variable) ?", font_size=46)
        subtitle = Text("Idée intuitive", font_size=34).next_to(title, DOWN, buff=0.3)
        logo = ImageMobject("scenes/pythagore_whiteboard_fr/LOGO_UQAM.png")


        with self.narrated("Qu'est-ce qu'une fonction d'une variable ? Commençons avec une idée intuitive.") as _:
            self.play_paced(FadeIn(title, shift=0.2 * DOWN), FadeIn(subtitle, shift=0.2 * DOWN), run_time=2.0)
            self.wait_paced(1.5)
            self.play_paced(FadeOut(title), subtitle.animate.to_edge(UP).scale(0.95), run_time=1.2)
            self.wait_paced(0.6)
            self.play_paced(FadeOut(subtitle), run_time=0.7)

        # ---------------------------
        # 2) MACHINE (6-28s)
        # VO: "Une fonction agit comme une machine."
        # ---------------------------
        machine_box = RoundedRectangle(width=3.2, height=2.1, corner_radius=0.18, color=BLACK, stroke_width=3)
        machine_label = MathTex("f", font_size=56).move_to(machine_box.get_center())

        line1 = Text("Une fonction, c'est une machine :", font_size=32)
        line2 = Text("à chaque entrée x, elle associe une sortie f(x).", font_size=32)
        machine_text = VGroup(line1, line2).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_edge(UP)

        outputs = VGroup()

        def send_value(x_value, y_value, y_offset):
            start = machine_box.get_left() + LEFT * 2.6 + UP * y_offset
            mid = machine_box.get_center() + UP * (0.15 * y_offset)
            end = machine_box.get_right() + RIGHT * 2.2 + UP * y_offset

            token = Dot(point=start, radius=0.075, color=accent)
            in_label = MathTex(f"x={x_value}", font_size=34).next_to(token, LEFT, buff=0.12)
            out_label = MathTex(f"f({x_value})={y_value}", font_size=34).next_to(end, RIGHT, buff=0.14)

            self.play_paced(FadeIn(token), Write(in_label), run_time=0.6)
            self.play_paced(token.animate.move_to(mid), FadeOut(in_label), run_time=0.8)
            self.play_paced(token.animate.move_to(end), run_time=0.9)
            self.play_paced(Write(out_label), run_time=0.6)

            pair = VGroup(token, out_label)
            outputs.add(pair)
            return pair

        with self.narrated(
            "Une fonction, c'est comme une machine. A chaque entree x, elle associe une sortie f de x. "
            "Meme entree, meme sortie. Et une entree ne peut pas donner deux sorties differentes."
        ) as _:
            self.play_paced(Create(machine_box), Write(machine_label), FadeIn(machine_text), run_time=2.0)
            self.wait_paced(0.5)
            send_value(-1, -1, 0.9)
            send_value(0, 1, 0.0)
            first_two = send_value(2, 5, -0.9)

            rule1 = Text("Même entrée → même sortie.", font_size=32)
            rule2 = Text("Et une entrée ne peut pas donner deux sorties.", font_size=32)
            rule_text = VGroup(rule1, rule2).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_edge(DOWN)

            self.play_paced(FadeIn(rule_text, shift=0.2 * UP), run_time=1.2)
            self.wait_paced(1.0)

            repeat_a = send_value(2, 5, -1.7)
            repeat_b = send_value(2, 5, -2.4)
            self.play_paced(Circumscribe(VGroup(first_two[1], repeat_a[1], repeat_b[1]), color=accent, fade_out=True), run_time=1.0)
            self.wait_paced(0.8)

            machine_group = VGroup(machine_box, machine_label, machine_text, rule_text, outputs)
            self.play_paced(FadeOut(machine_group), run_time=1.2)

        # ---------------------------
        # 3) DIAGRAMME DE CORRESPONDANCE (28-45s)
        # ---------------------------
        left_title = Text("Entrées (x)", font_size=34).move_to(LEFT * 4.2 + UP * 2.3)
        right_title = Text("Sorties", font_size=34).move_to(RIGHT * 4.2 + UP * 2.3)

        left_vals = VGroup(
            MathTex("x=-2", font_size=38),
            MathTex("x=0", font_size=38),
            MathTex("x=1", font_size=38),
            MathTex("x=3", font_size=38),
        ).arrange(DOWN, buff=0.55).next_to(left_title, DOWN, buff=0.45)

        right_vals = VGroup(
            MathTex("-3", font_size=38),
            MathTex("1", font_size=38),
            MathTex("7", font_size=38),
        ).arrange(DOWN, buff=0.55).next_to(right_title, DOWN, buff=0.45)

        with self.narrated(
            "On peut aussi voir une fonction comme un diagramme de correspondance. "
            f"Ici, la valeur sept a deux preimages, x egal un,{ET} x egal trois."
        ) as _:
            self.play_paced(FadeIn(left_title), FadeIn(right_title), FadeIn(left_vals), FadeIn(right_vals), run_time=2.2)

            arrows = VGroup(
                Arrow(left_vals[0].get_right(), right_vals[0].get_left(), buff=0.1, color=accent, stroke_width=3),
                Arrow(left_vals[1].get_right(), right_vals[1].get_left(), buff=0.1, color=accent, stroke_width=3),
                Arrow(left_vals[2].get_right(), right_vals[2].get_left(), buff=0.1, color=accent, stroke_width=3),
                Arrow(left_vals[3].get_right(), right_vals[2].get_left(), buff=0.1, color=accent, stroke_width=3),
            )
            for arrow in arrows:
                self.play_paced(Create(arrow), run_time=0.9)

            preimage_text = Text("Ici, 7 a deux préimages : x=1 et x=3.", font_size=29).to_edge(DOWN)
            preimage_target = VGroup(arrows[2], arrows[3], right_vals[2])
            preimage_box = SurroundingRectangle(preimage_target, color=accent, buff=0.12, stroke_width=3)
            self.play_paced(FadeIn(preimage_text), run_time=0.9)
            self.play_paced(Create(preimage_box), run_time=1.1)
            self.wait_paced(2.0)
            self.play_paced(FadeOut(preimage_text), run_time=0.8)

            mapping_group = VGroup(left_title, right_title, left_vals, right_vals, arrows, preimage_box)
            self.play_paced(FadeOut(mapping_group), run_time=1.0)

        # ---------------------------
        # 4) DÉFINITION LÉGÈRE (45-55s)
        # ---------------------------
        formal_1 = MathTex(r"f:\mathbb{R}\to\mathbb{R}", font_size=62)
        formal_2 = MathTex(r"x\mapsto f(x)", font_size=58).next_to(formal_1, DOWN, buff=0.38)
        formal_3 = Text("À chaque x, un seul nombre f(x).", font_size=34).next_to(formal_2, DOWN, buff=0.45)

        with self.narrated(
            f"Ecriture compacte : f de R dans R,{ET} x est envoye vers f de x. "
            "A chaque x, un seul nombre."
        ) as _:
            self.play_paced(Write(formal_1), run_time=1.6)
            self.play_paced(Write(formal_2), run_time=1.4)
            self.play_paced(FadeIn(formal_3), run_time=1.0)
            self.wait_paced(1.8)
            self.play_paced(FadeOut(VGroup(formal_1, formal_2, formal_3)), run_time=1.0)

        # ---------------------------
        # 5) GRAPHIQUE + TEST DE LA VERTICALE (55-90s)
        # VO: "Sur un graphe, une verticale ne doit couper qu'une seule fois."
        # ---------------------------
        axes = Axes(
            x_range=[-3.5, 3.5, 1],
            y_range=[-3.5, 7.5, 1],
            x_length=4.2,
            y_length=6.6,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
        ).to_edge(DOWN, buff=0.7)
        axis_labels = axes.get_axis_labels(MathTex("x"), MathTex("y"))

        line_slope = 2
        line_intercept = 1
        func_graph = axes.plot(
            lambda x: line_slope * x + line_intercept,
            x_range=[-2.2, 3.0],
            color=BLACK,
            stroke_width=4,
        )
        func_label = MathTex("y=2x+1", font_size=34).next_to(axes.c2p(1.8, 4.6), UR, buff=0.2)
        top_text = Text("Sur un graphique : une verticale coupe la courbe au plus une fois.", font_size=30).to_edge(UP)

        x_tracker = ValueTracker(-2.2)

        vertical_line = always_redraw(
            lambda: Line(
                axes.c2p(x_tracker.get_value(), -3.5),
                axes.c2p(x_tracker.get_value(), 7.5),
                color=accent,
                stroke_width=3,
            )
        )
        moving_dot = always_redraw(
            lambda: Dot(
                axes.c2p(x_tracker.get_value(), line_slope * x_tracker.get_value() + line_intercept),
                color=accent,
                radius=0.08,
            )
        )
        coord_text = always_redraw(
            lambda: Text(
                f"(x, y) = ({x_tracker.get_value():.2f}, {line_slope * x_tracker.get_value() + line_intercept:.2f})",
                font_size=24,
            ).next_to(axes, RIGHT, buff=0.25)
        )

        with self.narrated(
            "Sur un graphique, une verticale coupe la courbe au plus une fois. "
            f"Le point se lit avec ses coordonnees, x{ET} {Y}."
        ) as _:
            self.play_paced(Create(axes), Write(axis_labels), Create(func_graph), FadeIn(func_label), FadeIn(top_text), run_time=3.0)
            self.wait_paced(0.8)
            self.play_paced(Create(vertical_line), FadeIn(moving_dot), FadeIn(coord_text), run_time=1.2)
            self.play_paced(x_tracker.animate.set_value(3.0), run_time=5.0, rate_func=linear)
            self.play_paced(x_tracker.animate.set_value(-1.2), run_time=3.5, rate_func=linear)
            self.wait_paced(1.0)

        relation_circle = axes.plot_parametric_curve(
            lambda t: np.array([2 * np.cos(t), 2 * np.sin(t), 0]),
            t_range=[0, TAU],
            color=BLACK,
            stroke_width=4,
        )
        relation_label = MathTex(r"x^2+y^2=4", font_size=32).next_to(axes.c2p(1.8, 1.8), UR, buff=0.15)
        counter_text = Text(
            "Ici, une verticale coupe deux fois → ce n'est pas une fonction (Y en fonction de x).",
            font_size=29,
        ).to_edge(UP)

        with self.narrated(
            "Pour cette relation en cercle, certaines verticales coupent en deux points. "
            "Donc ce n'est pas une fonction de {Y} en fonction de x."
        ) as _:
            self.play_paced(
                ReplacementTransform(top_text, counter_text),
                FadeOut(func_graph),
                FadeOut(func_label),
                FadeOut(coord_text),
                FadeOut(moving_dot),
                Create(relation_circle),
                FadeIn(relation_label),
                x_tracker.animate.set_value(-1.4),
                run_time=2.8,
            )
            top_text = counter_text

            upper_hit = Dot(color=accent, radius=0.08)
            lower_hit = Dot(color=accent, radius=0.08)

            def update_upper(dot):
                x = x_tracker.get_value()
                if abs(x) <= 2:
                    dot.move_to(axes.c2p(x, np.sqrt(4 - x**2)))
                    dot.set_opacity(1)
                else:
                    dot.set_opacity(0)

            def update_lower(dot):
                x = x_tracker.get_value()
                if abs(x) <= 2:
                    dot.move_to(axes.c2p(x, -np.sqrt(4 - x**2)))
                    dot.set_opacity(1)
                else:
                    dot.set_opacity(0)

            upper_hit.add_updater(update_upper)
            lower_hit.add_updater(update_lower)
            update_upper(upper_hit)
            update_lower(lower_hit)

            self.play_paced(FadeIn(upper_hit), FadeIn(lower_hit), run_time=0.8)
            self.play_paced(x_tracker.animate.set_value(1.5), run_time=4.0, rate_func=linear)
            self.play_paced(x_tracker.animate.set_value(0.2), run_time=2.5, rate_func=linear)
            self.wait_paced(1.0)

        upper_hit.clear_updaters()
        lower_hit.clear_updaters()

        graph_cleanup = VGroup(
            axes,
            axis_labels,
            vertical_line,
            relation_circle,
            relation_label,
            upper_hit,
            lower_hit,
            top_text,
        )
        self.play_paced(FadeOut(graph_cleanup), run_time=1.5)

        # ---------------------------
        # 6) CONCLUSION (90-100s)
        # ---------------------------
        final_1 = Text("Fonction (1 variable) = règle qui associe", font_size=38)
        final_2 = Text("à chaque x une unique valeur f(x).", font_size=38).next_to(final_1, DOWN, buff=0.18)
        recap = Text("Boucle mentale : choisir x → calculer f(x) → obtenir un seul résultat.", font_size=30).next_to(
            final_2, DOWN, buff=0.55
        )

        with self.narrated(
            "En resume : une fonction a une variable est une regle qui associe a chaque x "
            "une unique valeur f de x. Boucle mentale : choisir x, calculer f de x, "
            "obtenir un seul resultat."
        ) as _:
            self.play_paced(Write(final_1), Write(final_2), run_time=2.0)
            self.play_paced(FadeIn(recap), run_time=1.0)
            self.wait_paced(10.0)
            self.play_paced(FadeOut(VGroup(final_1, final_2, recap)), run_time=1.2)

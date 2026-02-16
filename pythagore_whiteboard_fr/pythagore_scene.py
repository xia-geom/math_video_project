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


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class PythagoreAireFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    def _setup_voiceover(self):
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
            load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)

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

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)

        self.set_speech_service(
            AzureService(
                voice="fr-CA-ThierryNeural",
                prosody={"rate": "-18%"},
            )
        )
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, caption: str, ssml: str = None):
        if self._voiceover_enabled:
            voice_text = ssml if ssml is not None else caption
            with self.voiceover(text=voice_text, subcaption=caption) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def _subtitle_box(self, text: str) -> VGroup:
        caption = Text(
            text,
            font="Sans",
            color=BLACK,
            font_size=30,
        )
        max_width = config.frame_width - 1.0
        if caption.width > max_width:
            caption.scale_to_fit_width(max_width)

        panel = RoundedRectangle(
            corner_radius=0.08,
            width=caption.width + 0.45,
            height=caption.height + 0.28,
            stroke_color=GRAY_B,
            stroke_width=1,
        )
        panel.set_fill(WHITE, opacity=0.96)
        caption.move_to(panel.get_center())

        box = VGroup(panel, caption)
        box.to_edge(DOWN, buff=0.18)
        return box

    def _show_caption(self, text: str, duration: float) -> VGroup:
        box = self._subtitle_box(text)
        self.play(FadeIn(box), run_time=0.2)
        return box

    def _hide_caption(self, box: VGroup) -> None:
        self.play(FadeOut(box), run_time=0.2)

    def _right_angle_marker(self, vertex, size: float = 0.2, color=BLACK) -> VGroup:
        p1 = vertex + RIGHT * size
        p2 = p1 + UP * size
        p3 = vertex + UP * size
        return VGroup(
            Line(p1, p2, color=color, stroke_width=2),
            Line(p2, p3, color=color, stroke_width=2),
        )

    def _segment_label(self, p1, p2, text: str, offset, color=BLACK) -> MathTex:
        label = MathTex(text, color=color).scale(0.78)
        label.move_to((p1 + p2) / 2 + offset)
        return label

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        accent = BLUE_D

        a_len = 2.8
        b_len = 1.8
        side_len = a_len + b_len

        # -------------------------
        # Geometric setup: one right triangle.
        # -------------------------
        ref_corner = LEFT * (a_len / 2) + DOWN * (b_len / 2)
        ref_p0 = ref_corner
        ref_p1 = ref_corner + RIGHT * a_len
        ref_p2 = ref_corner + UP * b_len

        ref_triangle = Polygon(
            ref_p0,
            ref_p1,
            ref_p2,
            color=BLACK,
            stroke_width=3,
            fill_opacity=0,
        )
        ref_label_a = MathTex("a", color=BLACK).scale(0.85).next_to(Line(ref_p0, ref_p1), DOWN, buff=0.08)
        ref_label_b = MathTex("b", color=BLACK).scale(0.85).next_to(Line(ref_p0, ref_p2), LEFT, buff=0.08)
        ref_label_c = MathTex("c", color=BLACK).scale(0.85)
        ref_label_c.move_to((ref_p1 + ref_p2) / 2 + np.array([0.05, 0.07, 0.0]))
        ref_right_angle = self._right_angle_marker(ref_p0, size=0.22, color=BLACK)

        with self.narrated(
            "Dans cette vidéo, on démontre le théorème de Pythagore par une preuve d'aire.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "Dans cette vidéo, on démontre le théorème de Pythagore "
                "par une preuve d'aire."
                "</lang>"
            ),
        ) as _:
            intro_cap = self._show_caption(
                "Dans cette vidéo, on démontre le théorème de Pythagore par une preuve d'aire.",
                duration=3.6,
            )
            self.wait(2.8)
            self._hide_caption(intro_cap)

        with self.narrated(
            "On part d'un triangle rectangle, avec les côtés a et b, et l'hypoténuse c.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "On part d'un triangle rectangle."
                "<break time='120ms'/>"
                "Avec les côtés <say-as interpret-as='characters'>a</say-as> "
                "et <say-as interpret-as='characters'>b</say-as>, "
                "<break time='90ms'/>"
                "et l'hypoténuse <say-as interpret-as='characters'>c</say-as>."
                "</lang>"
            ),
        ) as _:
            self.play(Create(ref_triangle), run_time=1.2)
            self.play(FadeIn(VGroup(ref_label_a, ref_label_b, ref_label_c, ref_right_angle)), run_time=0.9)
            self.wait(0.8)

        # -------------------------
        # Scene 1 - algebra identity
        # -------------------------
        algebra_identity = MathTex(
            r"(a+b)^2 = a^2 + 2ab + b^2",
            color=BLACK,
        ).scale(1.45)
        with self.narrated(
            "Rappel algébrique : a plus b au carré est égal à a au carré plus deux a b plus b au carré.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "<prosody rate='-7%'>"
                "Rappel algébrique."
                "<break time='150ms'/>"
                "<say-as interpret-as='characters'>a</say-as> plus <say-as interpret-as='characters'>b</say-as> au carré, "
                "est égal à <say-as interpret-as='characters'>a</say-as> au carré, "
                "<break time='100ms'/> plus deux <say-as interpret-as='characters'>a b</say-as>, "
                "<break time='100ms'/> plus <say-as interpret-as='characters'>b</say-as> au carré."
                "</prosody>"
                "</lang>"
            ),
        ) as _:
            cap1 = self._show_caption("Développer (a+b)^2", duration=4.5)
            self.play(Write(algebra_identity), run_time=1.6)
            self.wait(2.8)
            self._hide_caption(cap1)
            self.play(
                FadeOut(algebra_identity),
                FadeOut(VGroup(ref_triangle, ref_label_a, ref_label_b, ref_label_c, ref_right_angle)),
                run_time=0.6,
            )

        # -------------------------
        # Scene 2 - big square
        # -------------------------
        big_square = Square(
            side_length=side_len,
            color=BLACK,
            stroke_width=3,
        ).move_to(RIGHT * 1.9 + DOWN * 0.1)

        side_label_bottom = MathTex("a+b", color=BLACK).scale(0.95).next_to(big_square, DOWN, buff=0.18)
        side_label_right = MathTex("a+b", color=BLACK).scale(0.95).rotate(PI / 2).next_to(big_square, RIGHT, buff=0.22)
        with self.narrated(
            "Construisons maintenant un grand carré de côté a plus b.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "Construisons maintenant un grand carré, "
                "de côté <say-as interpret-as='characters'>a</say-as> plus <say-as interpret-as='characters'>b</say-as>."
                "</lang>"
            ),
        ) as _:
            cap2 = self._show_caption("Carré de côté a+b", duration=6.2)
            self.play(Create(big_square), run_time=1.8)
            self.play(Write(side_label_bottom), Write(side_label_right), run_time=1.0)
            self.wait(3.4)
            self._hide_caption(cap2)

        # Core geometry points for 4 triangles + center square.
        sq_center = big_square.get_center()
        bl = sq_center + np.array([-side_len / 2, -side_len / 2, 0.0])
        br = sq_center + np.array([side_len / 2, -side_len / 2, 0.0])
        tr = sq_center + np.array([side_len / 2, side_len / 2, 0.0])
        tl = sq_center + np.array([-side_len / 2, side_len / 2, 0.0])

        bottom_split = bl + RIGHT * a_len
        right_split = br + UP * a_len
        top_split = tl + RIGHT * b_len
        left_split = bl + UP * b_len

        target_triangles = VGroup(
            Polygon(bl, bottom_split, left_split, color=BLACK, stroke_width=3, fill_opacity=0),
            Polygon(br, right_split, bottom_split, color=BLACK, stroke_width=3, fill_opacity=0),
            Polygon(tr, top_split, right_split, color=BLACK, stroke_width=3, fill_opacity=0),
            Polygon(tl, left_split, top_split, color=BLACK, stroke_width=3, fill_opacity=0),
        )

        center_square = Polygon(
            bottom_split,
            right_split,
            top_split,
            left_split,
            color=accent,
            stroke_width=3,
        )
        center_square.set_fill(accent, opacity=0.1)

        center_right_angle = RightAngle(
            Line(bottom_split, right_split),
            Line(bottom_split, left_split),
            length=0.18,
            color=accent,
        )

        c_side_label = MathTex("c", color=accent).scale(0.9)
        c_side_label.move_to((bottom_split + right_split) / 2 + 0.1 * UL)

        ab_labels = VGroup(
            self._segment_label(bl, bottom_split, "a", 0.22 * DOWN),
            self._segment_label(bottom_split, br, "b", 0.22 * DOWN),
            self._segment_label(br, right_split, "a", 0.22 * RIGHT),
            self._segment_label(right_split, tr, "b", 0.22 * RIGHT),
            self._segment_label(tl, top_split, "b", 0.22 * UP),
            self._segment_label(top_split, tr, "a", 0.22 * UP),
            self._segment_label(bl, left_split, "b", 0.22 * LEFT),
            self._segment_label(left_split, tl, "a", 0.22 * LEFT),
        )

        # -------------------------
        # Scene 3 - pack 4 triangles
        # -------------------------
        with self.narrated(
            "On place quatre triangles rectangles identiques dans le grand carré. "
            "Au centre, il reste un petit carré dont le côté vaut c.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "On place quatre triangles rectangles identiques dans le grand carré."
                "<break time='150ms'/>"
                "Au centre, il reste un petit carré, "
                "dont le côté vaut <say-as interpret-as='characters'>c</say-as>."
                "</lang>"
            ),
        ) as _:
            cap3 = self._show_caption("4 triangles identiques", duration=9.8)
            self.play(LaggedStart(*[Create(t) for t in target_triangles], lag_ratio=0.12), run_time=2.4)
            self.play(Create(center_square), Create(center_right_angle), FadeIn(c_side_label), run_time=1.4)
            self.play(LaggedStart(*[FadeIn(lbl) for lbl in ab_labels], lag_ratio=0.05), run_time=1.8)
            self.wait(4.6)
            self._hide_caption(cap3)

        # -------------------------
        # Scene 4 - area counting
        # -------------------------
        area_name_big = Text("Grand carré", color=BLACK, font_size=30)
        area_name_triangles = Text("4 triangles", color=BLACK, font_size=30)
        area_name_center = Text("Carré central", color=BLACK, font_size=30)

        area_colon_big = Text(":", color=BLACK, font_size=34)
        area_colon_triangles = Text(":", color=BLACK, font_size=34)
        area_colon_center = Text(":", color=BLACK, font_size=34)

        area_big = MathTex(r"(a+b)^2", color=BLACK).scale(0.95)
        area_triangles = MathTex(r"4\times\frac{ab}{2}=2ab", color=BLACK).scale(0.95)
        area_center = MathTex(r"c^2", color=accent).scale(0.95)

        area_label_col = VGroup(area_name_big, area_name_triangles, area_name_center).arrange(
            DOWN, aligned_edge=LEFT, buff=0.3
        )
        area_colon_col = VGroup(area_colon_big, area_colon_triangles, area_colon_center)
        area_colon_col.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        area_colon_col.next_to(area_label_col, RIGHT, buff=0.12)
        area_formula_col = VGroup(area_big, area_triangles, area_center)
        area_formula_col.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        area_formula_col.next_to(area_colon_col, RIGHT, buff=0.18)

        for idx in range(3):
            area_colon_col[idx].set_y(area_label_col[idx].get_y())
            area_formula_col[idx].set_y(area_label_col[idx].get_y())

        area_rows = VGroup(area_label_col, area_colon_col, area_formula_col)
        area_rows.next_to(big_square, LEFT, buff=0.65)
        area_rows.align_to(big_square, UP)
        area_rows.shift(DOWN * 0.45)

        geom_identity = MathTex(r"(a+b)^2 = 2ab + c^2", color=BLACK).scale(1.02)
        geom_identity.next_to(area_rows, DOWN, aligned_edge=LEFT, buff=0.5)
        geom_identity.set_color_by_tex("c^2", accent)

        with self.narrated(
            "L'aire du grand carré est égale à l'aire des quatre triangles plus l'aire du carré central. "
            "On obtient : a plus b au carré égal deux a b plus c au carré.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "<prosody rate='-8%'>"
                "L'aire du grand carré est égale à l'aire des quatre triangles, "
                "plus l'aire du carré central."
                "<break time='180ms'/>"
                "On obtient : "
                "<say-as interpret-as='characters'>a</say-as> plus <say-as interpret-as='characters'>b</say-as> au carré, "
                "égal deux <say-as interpret-as='characters'>a b</say-as>, "
                "plus <say-as interpret-as='characters'>c</say-as> au carré."
                "</prosody>"
                "</lang>"
            ),
        ) as _:
            cap4 = self._show_caption("Aire totale = 4 triangles + carré central", duration=8.0)
            self.play(
                Write(area_name_big),
                FadeIn(area_colon_big, shift=RIGHT * 0.08),
                Write(area_big),
                run_time=1.0,
            )
            self.play(
                Write(area_name_triangles),
                FadeIn(area_colon_triangles, shift=RIGHT * 0.08),
                Write(area_triangles),
                run_time=1.2,
            )
            self.play(
                Write(area_name_center),
                FadeIn(area_colon_center, shift=RIGHT * 0.08),
                run_time=0.55,
            )
            self.play(TransformFromCopy(c_side_label, area_center), run_time=0.9)
            self.play(Write(geom_identity), run_time=1.4)
            self.wait(3.7)
            self._hide_caption(cap4)

        # -------------------------
        # Scene 5 - match and conclude
        # -------------------------
        algebra_line = MathTex(r"(a+b)^2 = a^2 + 2ab + b^2", color=BLACK).scale(0.92)
        algebra_line.next_to(geom_identity, UP, aligned_edge=LEFT, buff=0.55)
        geom_line_target = MathTex(r"(a+b)^2 = 2ab + c^2", color=BLACK).scale(0.92)
        geom_line_target.move_to(geom_identity)
        geom_line_target.set_color_by_tex("c^2", accent)

        reduced_formula = MathTex(r"c^2 = a^2 + b^2", color=BLACK).scale(1.08)
        reduced_formula.move_to((algebra_line.get_center() + geom_identity.get_center()) / 2 + DOWN * 0.08)

        final_formula = MathTex(r"c^2 = a^2 + b^2", color=BLACK).scale(1.9)
        final_formula.move_to(DOWN * 0.2)
        with self.narrated(
            "En comparant les deux égalités, les termes deux a b s'annulent. "
            "Il reste c au carré égal a au carré plus b au carré. "
            "C'est le théorème de Pythagore.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "En comparant les deux égalités, "
                "les termes deux <say-as interpret-as='characters'>a b</say-as> s'annulent."
                "<break time='160ms'/>"
                "Il reste <say-as interpret-as='characters'>c</say-as> au carré, "
                "égal à <say-as interpret-as='characters'>a</say-as> au carré "
                "plus <say-as interpret-as='characters'>b</say-as> au carré."
                "<break time='180ms'/>"
                "C'est le théorème de Pythagore."
                "</lang>"
            ),
        ) as _:
            cap5 = self._show_caption("Donc: c^2 = a^2 + b^2", duration=6.9)
            self.play(
                FadeOut(VGroup(area_rows, side_label_bottom, side_label_right)),
                Transform(geom_identity, geom_line_target),
                Write(algebra_line),
                run_time=1.8,
            )
            self.play(
                FadeOut(algebra_line, shift=UP * 0.1),
                FadeOut(geom_identity, shift=DOWN * 0.1),
                FadeIn(reduced_formula, scale=0.95),
                run_time=1.2,
            )
            self.play(
                FadeOut(
                    VGroup(
                        big_square,
                        target_triangles,
                        ab_labels,
                        center_square,
                        center_right_angle,
                        c_side_label,
                    )
                ),
                TransformMatchingTex(reduced_formula, final_formula),
                run_time=1.8,
            )
            self.wait(2.0)
            self._hide_caption(cap5)

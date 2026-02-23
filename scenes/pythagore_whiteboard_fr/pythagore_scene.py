from manim import *
import numpy as np
import re
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService


SSML_RATE = "0%"


def fr_ca(body: str, rate: str = SSML_RATE) -> str:
    return f"<lang xml:lang='fr-CA'><prosody rate='{rate}'>{body}</prosody></lang>"


_TAGS = re.compile(r"<[^>]+>")


def caption_from_ssml(s: str) -> str:
    return _TAGS.sub("", s).replace("  ", " ").strip()


# Optional: keep these if Azure keeps dropping the "s" in math "plus"
PLUS = "<phoneme alphabet='ipa' ph='plys'>plus</phoneme>"
A = "<say-as interpret-as='characters'>a</say-as>"
B = "<say-as interpret-as='characters'>b</say-as>"
C = "<say-as interpret-as='characters'>c</say-as>"

script = [
    # [0]
    "Dans cette vidéo, on prouve le théorème de Pythagore avec une méthode d’aire. "
    "<bookmark mark='intro_end'/>",

    # [1]
    f"On part d'un triangle rectangle. <bookmark mark='triangle_drawn'/> "
    f"Ses côtés sont {A} et {B}. <bookmark mark='triangle_labels'/> "
    f"Et son hypoténuse est {C}.",

    # [2]
    "Rappel algébrique. <break time='120ms'/> <bookmark mark='algebra_identity'/> "
    f"On écrit : {A} {PLUS} {B} au carré est égal à {A} au carré {PLUS} deux {A} {B} {PLUS} {B} au carré. "
    "<bookmark mark='algebra_transition'/>",

    # [3]
    f"Construisons maintenant un grand carré. <bookmark mark='square_draw'/> "
    f"Son côté vaut {A} {PLUS} {B}. <bookmark mark='square_labels'/> "
    "<break time='120ms'/> <bookmark mark='square_end'/>",

    # [4]
    "On place quatre triangles rectangles identiques dans le grand carré. <bookmark mark='triangles_in'/> "
    "Au centre, il reste un petit carré. <bookmark mark='center_square'/> "
    f"Son côté vaut {C}. <bookmark mark='ab_labels'/> <bookmark mark='scene3_end'/>",

    # [5]
    "Comptons les aires. <bookmark mark='area_big'/> D'abord le grand carré. "
    "<bookmark mark='area_triangles'/> Puis les quatre triangles. "
    "<bookmark mark='area_center'/> Enfin le carré central. "
    "<bookmark mark='area_identity'/> "
    f"On obtient : {A} {PLUS} {B} au carré égal deux {A} {B} {PLUS} {C} au carré. "
    "<bookmark mark='scene4_end'/>",

    # [6]
    f"En comparant les deux égalités, les termes deux {A} {B} s'annulent. <bookmark mark='compare_lines'/> "
    f"Il reste {C} au carré égal {A} au carré {PLUS} {B} au carré. <bookmark mark='reduced_formula'/> "
    "C'est le théorème de Pythagore. <bookmark mark='final_formula'/> <bookmark mark='scene5_end'/>",
]

class PythagoreAireFR(VoiceoverScene):
        # ... your existing construct continues here ...
        # self.play(...)
        # with self.voiceover(...):
        #     ...

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
        self.set_speech_service(AzureService(voice="fr-CA-SylvieNeural", global_speed=0.85))

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
        ref_label_c.move_to((ref_p1 + ref_p2) / 2 + np.array([0.1, 0.1, 0.0]))
        ref_right_angle = self._right_angle_marker(ref_p0, size=0.22, color=BLACK)
        logo = ImageMobject("pythagore_whiteboard_fr/LOGO_UQAM.png")

        with self.voiceover(text=fr_ca(script[0]), subcaption=caption_from_ssml(script[0])):
            self.play(FadeIn(logo, shift=0.2*UP), run_time=0.6)
            self.play(logo.animate.scale(0.5), run_time=1.0)
            self.play(logo.animate.scale(1.0), run_time=1.0)
            self.play(FadeOut(logo, shift=0.2*UP), run_time=0.6)
            self.wait_until_bookmark("intro_end")
            self.play(Create(ref_triangle), run_time=1.3)
            self.play(FadeIn(VGroup(ref_label_a, ref_label_b, ref_label_c, ref_right_angle)), run_time=1.0)
        with self.voiceover(text=fr_ca(script[1]), subcaption=caption_from_ssml(script[1])):
            self.wait_until_bookmark("triangle_drawn")
            self.wait_until_bookmark("triangle_labels")
   
        # -------------------------
        # Scene 1 - algebra identity
        # -------------------------
        algebra_identity = MathTex(
            r"(a+b)^2 = a^2 + 2ab + b^2",
            color=BLACK,
        ).scale(1.45)
        # bg_algebra_identity=BackgroundRectangle(
        #         VGroup(algebra_identity), color=WHITE,
        #         buff=.2)


        with self.voiceover(text=fr_ca(script[2]), subcaption=caption_from_ssml(script[2])):
            self.play(
                FadeOut(VGroup( ref_label_a, ref_label_b, ref_label_c, ref_right_angle, ref_triangle)), run_time=1.0),
            self.wait_until_bookmark("algebra_identity")

            # self.play(FadeIn(bg_algebra_identity))
            self.play(Write(algebra_identity), run_time=1.7)
            self.wait_until_bookmark("algebra_transition")
            self.play(
                FadeOut(algebra_identity), run_time=1.0),

            

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

        with self.voiceover(text=fr_ca(script[3]), subcaption=caption_from_ssml(script[3])):
            self.play(Create(big_square), run_time=1.9)
            self.wait_until_bookmark("square_draw")
            self.play(Write(side_label_bottom), Write(side_label_right), run_time=1.0)
            # self.wait_until_bookmark("square_labels")
            self.wait_until_bookmark("square_end")

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
        with self.voiceover(text=fr_ca(script[4]), subcaption=caption_from_ssml(script[4])):
            self.play(LaggedStart(*[Create(t) for t in target_triangles], lag_ratio=0.12), run_time=2.5)
            self.wait_until_bookmark("triangles_in")
            self.play(Create(center_square), Create(center_right_angle), FadeIn(c_side_label), run_time=1.5)
            self.wait_until_bookmark("center_square")
            self.play(LaggedStart(*[FadeIn(lbl) for lbl in ab_labels], lag_ratio=0.05), run_time=1.8)
            # self.wait_until_bookmark("ab_labels")
            self.wait_until_bookmark("scene3_end")

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

        with self.voiceover(text=fr_ca(script[5]), subcaption=caption_from_ssml(script[5])):
            self.wait_until_bookmark("area_big")
            self.play(
                Write(area_name_big),
                FadeIn(area_colon_big, shift=RIGHT * 0.08),
                Write(area_big),
                run_time=1.0,
            )
            self.wait_until_bookmark("area_triangles")
            self.play(
                Write(area_name_triangles),
                FadeIn(area_colon_triangles, shift=RIGHT * 0.08),
                Write(area_triangles),
                run_time=1.2,
            )
            self.wait_until_bookmark("area_center")
            self.play(
                Write(area_name_center),
                FadeIn(area_colon_center, shift=RIGHT * 0.08),
                run_time=0.55,
            )
            self.play(TransformFromCopy(c_side_label, area_center), run_time=0.9)
            self.wait_until_bookmark("area_identity")
            self.play(Write(geom_identity), run_time=1.4)
            self.wait_until_bookmark("scene4_end")

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
        Pythagore=ImageMobject("pythagore_whiteboard_fr/PYTHAGORE.png").scale(0.8).next_to(final_formula, UP, buff=0.4)
        with self.voiceover(text=fr_ca(script[6]), subcaption=caption_from_ssml(script[6])):
            self.play(
                FadeOut(VGroup(area_rows, side_label_bottom, side_label_right)),
                Transform(geom_identity, geom_line_target),
                Write(algebra_line),
                run_time=1.8,
            )
            self.wait_until_bookmark("compare_lines")

            self.play(
                FadeOut(algebra_line, shift=UP * 0.1),
                FadeOut(geom_identity, shift=DOWN * 0.1),
                                run_time=1.2,

            )
            self.play(
                FadeIn (reduced_formula, scale=0.95),
                run_time=1.2,
            )
            self.play(FadeIn(Pythagore, shift=0.2*UP+1*RIGHT), run_time=0.6)
            self.play(Pythagore.animate.scale(0.5), run_time=1.0)
            self.play(Pythagore.animate.scale(1.0), run_time=1.0)
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
            )
            self.play(                TransformMatchingTex(reduced_formula, final_formula),
                run_time=1.4,
            )
            self.wait_until_bookmark("final_formula")



            self.wait_until_bookmark("scene5_end")

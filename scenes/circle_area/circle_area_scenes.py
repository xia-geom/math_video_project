"""
Circle Area via Triangle Approximation — combined intro + rearrangement
with French voiceover.

Run with:
    manim -pqh circle_area_scenes.py CircleAreaFR
"""

from manim import *
import numpy as np
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
import tools.tts as tts
from tools.branding import play_uqam_intro


# ------------------------------------------------------------------
# Wedge construction (rigid-body polygons used in the rearrangement)
# ------------------------------------------------------------------
def make_wedge_at_origin(radius, theta, color,
                         fill_opacity=0.75, stroke_width=1, steps=12):
    """Wedge polygon: apex at origin, arc from angle 0 to theta."""
    arc_pts = [
        radius * np.array([np.cos(t * theta / steps),
                           np.sin(t * theta / steps), 0])
        for t in range(steps + 1)
    ]
    pts = [ORIGIN] + arc_pts
    return Polygon(*pts,
                   fill_color=color, fill_opacity=fill_opacity,
                   stroke_color=WHITE, stroke_width=stroke_width)


def _steps_for_n(n):
    return max(4, int(100 / n))


def make_circle_wedges(radius, n):
    """n alternating-colored wedges arranged as a full circle (apex at origin)."""
    steps = _steps_for_n(n)
    theta = TAU / n
    wedges = VGroup()
    for i in range(n):
        color = ORANGE if i % 2 == 0 else TEAL
        w = make_wedge_at_origin(radius, theta, color, steps=steps)
        w.rotate(i * theta, about_point=ORIGIN)
        wedges.add(w)
    return wedges


# ------------------------------------------------------------------
# Row target geometry
# ------------------------------------------------------------------
def row_target(radius, n, row_center):
    theta = TAU / n
    c = 2 * radius * np.sin(theta / 2)
    h = radius * np.cos(theta / 2)

    raw_apexes = []
    rotations = []
    for i in range(n):
        if i % 2 == 0:
            rotations.append(-PI / 2 - theta / 2)
            raw_apexes.append(np.array([i * c / 2, h, 0]))
        else:
            rotations.append(PI / 2 - theta / 2)
            raw_apexes.append(np.array([i * c / 2, 0, 0]))

    x_center = ((-c / 2) + (n * c / 2)) / 2
    y_center = (-(radius - h) + radius) / 2
    offset = np.array([x_center, y_center, 0]) - row_center

    apexes = [apex - offset for apex in raw_apexes]
    return rotations, apexes


# ------------------------------------------------------------------
# Rigid-motion animation
# ------------------------------------------------------------------
class RigidMove(Animation):
    def __init__(self, mobject, src_apex, tgt_apex, total_rot, **kwargs):
        self.src_apex = np.array(src_apex, dtype=float)
        self.tgt_apex = np.array(tgt_apex, dtype=float)
        self.total_rot = float(total_rot)
        super().__init__(mobject, **kwargs)

    def begin(self):
        self._initial_points = self.mobject.points.copy()
        super().begin()

    def interpolate_mobject(self, alpha):
        rot = alpha * self.total_rot
        cos_r, sin_r = np.cos(rot), np.sin(rot)
        shift = alpha * (self.tgt_apex - self.src_apex)

        rel = self._initial_points - self.src_apex
        new_pts = np.empty_like(rel)
        new_pts[:, 0] = rel[:, 0] * cos_r - rel[:, 1] * sin_r
        new_pts[:, 1] = rel[:, 0] * sin_r + rel[:, 1] * cos_r
        new_pts[:, 2] = rel[:, 2]
        new_pts = new_pts + self.src_apex + shift

        self.mobject.points = new_pts


def rearrange_animations(circle_group, radius, n, row_center):
    theta = TAU / n
    src_apex = circle_group.get_center()
    target_rots, target_apexes = row_target(radius, n, row_center)

    anims = []
    for i, wedge in enumerate(circle_group):
        source_rot_template = i * theta
        target_rot_template = target_rots[i]
        delta = target_rot_template - source_rot_template
        anims.append(
            RigidMove(wedge,
                      src_apex=src_apex,
                      tgt_apex=target_apexes[i],
                      total_rot=delta)
        )
    return anims


# ------------------------------------------------------------------
# French narration script (SSML + plain captions)
# ------------------------------------------------------------------
R = tts.char("r")
N = tts.char("n")

script = [
    # [0] Hook — circle + radius + question
    {
        "caption": "Voici un cercle de rayon r. On sait que son aire vaut pi r carré, mais pourquoi ?",
        "ssml": tts.ssml(
            f"Voici un cercle <bookmark mark='radius'/> de rayon {R}. "
            f"<break time='250ms'/> On sait que son aire <bookmark mark='question'/> "
            f"vaut pi {R} carré, <break time='180ms'/> mais pourquoi ?"
        ),
    },
    # [1] Single wedge — two radii and the arc
    {
        "caption": "Découpons-le en fines pointes. Chacune a deux côtés droits de longueur r, et un bord courbé à l'extérieur.",
        "ssml": tts.ssml(
            f"Découpons-le <bookmark mark='wedge'/> en fines pointes. "
            f"Chacune a deux côtés droits <bookmark mark='sides'/> de longueur {R}, "
            f"<break time='180ms'/> et un bord courbé <bookmark mark='arc'/> à l'extérieur."
        ),
    },
    # [2] Arc length formula
    {
        "caption": "Avec n pointes, chaque arc vaut un n-ième de la circonférence : deux pi r sur n.",
        "ssml": tts.ssml(
            f"Avec {N} pointes, <bookmark mark='arc_label'/> chaque arc vaut un {N}-ième "
            f"de la circonférence : <break time='150ms'/> deux pi {R} sur {N}."
        ),
    },
    # [3] Subdivision — n gets bigger
    {
        "caption": "Plus on utilise de pointes, plus elles deviennent fines, et ressemblent à de grands triangles minces.",
        "ssml": tts.ssml(
            f"Plus on utilise de pointes, <bookmark mark='n6'/> plus elles deviennent fines, "
            f"<bookmark mark='n12'/> <break time='120ms'/> et ressemblent "
            f"<bookmark mark='n24'/> à de grands triangles minces. <bookmark mark='n48'/>"
        ),
    },
    # [4] Rearrangement intro, n=6
    {
        "caption": "Prenons toutes ces pointes et rangeons-les en alternance, vers le haut et vers le bas. Avec six pointes, le résultat est clairement bosselé.",
        "ssml": tts.ssml(
            f"Prenons toutes ces pointes <bookmark mark='circle6'/> et rangeons-les en alternance, "
            f"<break time='120ms'/> vers le haut et vers le bas. "
            f"<bookmark mark='row6'/> Avec six pointes, le résultat est clairement bosselé."
        ),
    },
    # [5] n=12
    {
        "caption": "Avec douze pointes, c'est déjà plus proche — les bosses rétrécissent.",
        "ssml": tts.ssml(
            f"Avec douze pointes, <bookmark mark='circle12'/> c'est déjà plus proche — "
            f"<bookmark mark='row12'/> les bosses rétrécissent."
        ),
    },
    # [6] n=48 + conclusion
    {
        "caption": "Avec quarante-huit, la forme est presque un rectangle parfait. Sa base vaut pi r, sa hauteur vaut r. L'aire est donc pi r carré.",
        "ssml": tts.ssml(
            f"Avec quarante-huit, <bookmark mark='circle48'/> la forme est presque un rectangle parfait. "
            f"<bookmark mark='row48'/> <break time='250ms'/> "
            f"Sa base vaut pi {R}, <break time='150ms'/> sa hauteur vaut {R}. "
            f"<break time='180ms'/> L'aire est donc pi {R} carré."
        ),
    },
]


# ------------------------------------------------------------------
# Combined scene
# ------------------------------------------------------------------
class CircleAreaFR(VoiceoverScene):
    """Intro + progressive subdivision + rearrangement, with French narration."""

    def construct(self):
        self.camera.background_color = WHITE
        self.set_speech_service(AzureService(voice=tts.VOICE_ID, global_speed=0.85))
        play_uqam_intro(self)

        radius = 2.0

        # ============================================================
        # ACT 1 — Hook: circle with radius, question
        # ============================================================
        circle = Circle(radius=radius, color=BLUE, stroke_width=4)
        circle.set_fill(BLUE, opacity=0.2)

        radius_line = Line(ORIGIN, RIGHT * radius, color=YELLOW, stroke_width=4)
        radius_label = MathTex("r", color=YELLOW).next_to(radius_line, UP, buff=0.1)

        question = MathTex(r"A = \pi r^2", "\\;?", font_size=56)
        question.to_edge(UP)
        question[0].set_color(WHITE)
        question[1].set_color(YELLOW)

        with self.voiceover(text=script[0]["ssml"], subcaption=script[0]["caption"]):
            self.play(Create(circle), run_time=1.5)
            self.wait_until_bookmark("radius")
            self.play(Create(radius_line), Write(radius_label))
            self.wait_until_bookmark("question")
            self.play(Write(question))

        self.play(FadeOut(question))

        # ============================================================
        # ACT 2 — Single wedge: two radii + the arc
        # ============================================================
        n_intro = 12
        angle = TAU / n_intro

        wedge = Sector(
            radius=radius,
            angle=angle,
            start_angle=0,
            color=ORANGE,
            fill_opacity=0.6,
            stroke_color=ORANGE,
            stroke_width=3,
        )
        radius_a = Line(ORIGIN, RIGHT * radius, color=YELLOW, stroke_width=3)
        radius_b = Line(
            ORIGIN,
            radius * np.array([np.cos(angle), np.sin(angle), 0]),
            color=YELLOW,
            stroke_width=3,
        )

        r_label_a = MathTex("r", color=YELLOW, font_size=36).move_to(
            radius * 0.55 * np.array([np.cos(0), np.sin(0), 0]) + DOWN * 0.3
        )
        r_label_b = MathTex("r", color=YELLOW, font_size=36).move_to(
            radius * 0.55 * np.array([np.cos(angle), np.sin(angle), 0])
            + UP * 0.25 + LEFT * 0.15
        )

        arc = Arc(radius=radius, start_angle=0, angle=angle, color=RED, stroke_width=6)
        arc_label = MathTex(r"\frac{2\pi r}{n}", color=RED, font_size=36)
        arc_label.move_to(
            radius * 1.25 * np.array([np.cos(angle / 2), np.sin(angle / 2), 0])
        )

        with self.voiceover(text=script[1]["ssml"], subcaption=script[1]["caption"]):
            self.wait_until_bookmark("wedge")
            self.play(
                Transform(radius_line, radius_a),
                FadeOut(radius_label),
            )
            self.play(Create(radius_b), FadeIn(wedge))
            self.wait_until_bookmark("sides")
            self.play(Write(r_label_a), Write(r_label_b))
            self.wait_until_bookmark("arc")
            self.play(Create(arc))

        with self.voiceover(text=script[2]["ssml"], subcaption=script[2]["caption"]):
            self.wait_until_bookmark("arc_label")
            self.play(Write(arc_label))

        self.play(
            FadeOut(r_label_a),
            FadeOut(r_label_b),
            FadeOut(arc_label),
            FadeOut(arc),
            FadeOut(radius_line),
            FadeOut(radius_b),
            FadeOut(wedge),
        )

        # ============================================================
        # ACT 3 — Progressive subdivision 6 → 12 → 24 → 48
        # ============================================================
        n_tracker = Integer(6, color=WHITE, font_size=40)
        n_label = MathTex("n = ", font_size=40)
        counter_group = VGroup(n_label, n_tracker).arrange(RIGHT, buff=0.15)
        counter_group.to_corner(UR).shift(LEFT * 0.3)
        self.play(FadeIn(counter_group))

        def make_subdiv_wedges(n):
            wedges = VGroup()
            for i in range(n):
                color = ORANGE if i % 2 == 0 else TEAL
                w = Sector(
                    radius=radius,
                    angle=TAU / n,
                    start_angle=i * TAU / n,
                    color=color,
                    fill_opacity=0.7,
                    stroke_color=WHITE,
                    stroke_width=1,
                )
                wedges.add(w)
            return wedges

        wedges_6 = make_subdiv_wedges(6)
        wedges_12 = make_subdiv_wedges(12)
        wedges_24 = make_subdiv_wedges(24)
        wedges_48 = make_subdiv_wedges(48)

        with self.voiceover(text=script[3]["ssml"], subcaption=script[3]["caption"]):
            self.wait_until_bookmark("n6")
            self.play(
                FadeOut(circle),
                LaggedStart(*[FadeIn(w) for w in wedges_6], lag_ratio=0.05),
                run_time=1.2,
            )
            self.wait_until_bookmark("n12")
            self.play(
                ReplacementTransform(wedges_6, wedges_12),
                n_tracker.animate.set_value(12),
                run_time=1.0,
            )
            self.wait_until_bookmark("n24")
            self.play(
                ReplacementTransform(wedges_12, wedges_24),
                n_tracker.animate.set_value(24),
                run_time=1.0,
            )
            self.wait_until_bookmark("n48")
            self.play(
                ReplacementTransform(wedges_24, wedges_48),
                n_tracker.animate.set_value(48),
                run_time=1.0,
            )

        self.play(FadeOut(wedges_48), FadeOut(counter_group))

        # ============================================================
        # ACT 4 — Rearrangement: circle wedges → row (n=6, 12, 48)
        # ============================================================
        rearr_radius = 1.3
        circle_pos = UP * 1.9
        row_pos = DOWN * 1.5

        n_label_tex = MathTex("n = ", font_size=36)
        n_tracker2 = Integer(6, font_size=36)
        counter2 = VGroup(n_label_tex, n_tracker2).arrange(RIGHT, buff=0.1)
        counter2.to_corner(UR).shift(LEFT * 0.3)

        circ6 = make_circle_wedges(rearr_radius, 6).move_to(circle_pos)
        circ12 = make_circle_wedges(rearr_radius, 12).move_to(circle_pos)
        circ48 = make_circle_wedges(rearr_radius, 48).move_to(circle_pos)

        with self.voiceover(text=script[4]["ssml"], subcaption=script[4]["caption"]):
            self.wait_until_bookmark("circle6")
            self.play(FadeIn(circ6), FadeIn(counter2), run_time=0.8)
            self.wait_until_bookmark("row6")
            anims = rearrange_animations(circ6, rearr_radius, 6, row_pos)
            self.play(*anims, run_time=2.2)

        with self.voiceover(text=script[5]["ssml"], subcaption=script[5]["caption"]):
            self.wait_until_bookmark("circle12")
            self.play(
                FadeOut(circ6),
                FadeIn(circ12),
                n_tracker2.animate.set_value(12),
                run_time=0.8,
            )
            self.wait_until_bookmark("row12")
            anims = rearrange_animations(circ12, rearr_radius, 12, row_pos)
            self.play(*anims, run_time=2.2)

        with self.voiceover(text=script[6]["ssml"], subcaption=script[6]["caption"]):
            self.wait_until_bookmark("circle48")
            self.play(
                FadeOut(circ12),
                FadeIn(circ48),
                n_tracker2.animate.set_value(48),
                run_time=0.8,
            )
            self.wait_until_bookmark("row48")
            anims = rearrange_animations(circ48, rearr_radius, 48, row_pos)
            self.play(*anims, run_time=2.4)

        self.wait(1.0)

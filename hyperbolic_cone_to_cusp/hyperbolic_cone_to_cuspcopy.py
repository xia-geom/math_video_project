# manim -pqh hyperbolic_cone_to_cusp.py HyperbolicConeToCusp

from manim import *
import numpy as np


class HyperbolicConeToCusp(ThreeDScene):
    """
    A simple *illustrative* deformation:
      beta in (0,1], cone angle = 2*pi*beta.
    As beta decreases, the surface becomes narrower and much longer in the z-direction,
    so the “tip” effectively escapes to infinity (cusp-like, complete limit intuition).

    This is NOT an isometric embedding of an actual hyperbolic cone metric—just a clean
    visual caricature of the degeneration.
    """

    # Tunable constants
    BETAS = [1.00, 0.60, 0.35, 0.20, 0.12, 0.07]
    U_MAX = 2.6
    EPS_RADIUS = 0.02
    RESOLUTION = (24, 48)

    def make_surface(self, beta: float) -> ParametricSurface:
        beta = max(beta, 1e-3)
        u_max = self.U_MAX

        def param(u: float, v: float) -> np.ndarray:
            # Narrowing radius profile (shrinks exponentially in u)
            r = beta * np.exp(-u) + self.EPS_RADIUS

            # Stretch factor: as beta -> 0, the "axial length" blows up
            z = u / beta

            return np.array([r * np.cos(v), r * np.sin(v), z])

        surf = ParametricSurface(
            param,
            u_range=(0.0, u_max),
            v_range=(0.0, TAU),
            resolution=self.RESOLUTION,
        )
        surf.set_style(fill_opacity=0.8, stroke_width=0.5)
        return surf

    def construct(self):
        # Camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.9)
        self.begin_ambient_camera_rotation(rate=0.10)

        # Fixed UI text
        title = MathTex(r"\text{Cone angle }=2\pi\beta").scale(0.75).to_corner(UL)

        beta_tracker = ValueTracker(self.BETAS[0])
        beta_value = DecimalNumber(beta_tracker.get_value(), num_decimal_places=2).scale(0.75)
        beta_value.add_updater(lambda m: m.set_value(beta_tracker.get_value()))
        beta_label = VGroup(MathTex(r"\beta=").scale(0.75), beta_value).arrange(RIGHT, buff=0.15)
        beta_label.next_to(title, DOWN, aligned_edge=LEFT)

        self.add_fixed_in_frame_mobjects(title, beta_label)
        self.play(FadeIn(title), FadeIn(beta_label), run_time=1.0)

        # Surfaces (transform between prebuilt meshes)
        surface = self.make_surface(self.BETAS[0])
        self.play(FadeIn(surface), run_time=1.5)

        for b in self.BETAS[1:]:
            new_surface = self.make_surface(b)
            self.play(
                beta_tracker.animate.set_value(b),
                Transform(surface, new_surface),
                run_time=2.0,
            )

        # Closing remark
        note = MathTex(
            r"\beta\to 0:\ \text{tip recedes (cusp-like limit, complete intuition)}"
        ).scale(0.6).to_corner(DL)
        self.add_fixed_in_frame_mobjects(note)
        self.play(FadeIn(note), run_time=1.0)
        self.wait(2.0)

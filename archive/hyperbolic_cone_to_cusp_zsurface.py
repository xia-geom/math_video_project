from manim import *
import numpy as np

class InvRPlusEpsToPole(ThreeDScene):
    def construct(self):
        # Camera: "higher" = smaller phi (more top-down)
        self.set_camera_orientation(phi=35 * DEGREES, theta=-35 * DEGREES)
        self.camera.set_zoom(0.75)

        axes = ThreeDAxes()
        self.add(axes)

        # Domain and display parameters
        R = 2.2
        z_cap = 7.0          # visual ceiling for z
        resolution = 22      # keep modest for real-time redraw

        eps = ValueTracker(1.0)  # start with eps > 0

        # ---- Surface z = 1/(r + eps), capped for visualization ----
        def param_surface(u, v):
            x = u
            y = v
            r = np.sqrt(x**2 + y**2)
            z = 1.0 / (r + eps.get_value())
            return np.array([x, y, z])

        surface = always_redraw(
            lambda: Surface(
                param_surface,
                u_range=[-R, R],
                v_range=[-R, R],
                resolution=(resolution, resolution),
            )
            .set_style(fill_opacity=0.75, stroke_width=1)
            .set_fill_by_checkerboard(ORANGE, BLUE, opacity=0.55)
        )

        # ---- "Ceiling" plane z = z_cap to make the "disappears" moment concrete ----
        # ceiling = Surface(
        #     lambda u, v: np.array([u, v, z_cap]),
        #     u_range=[-R, R],
        #     v_range=[-R, R],
        #     resolution=(2, 2),
        # ).set_style(fill_opacity=0.12, stroke_width=0)

        # ---- z-axis intersection point: (0,0,1/eps) (only shown if <= z_cap) ----
        def z0():
            return 1.0 / eps.get_value()

        axis_marker = always_redraw(
            lambda: Dot3D(
                point=axes.c2p(0, 0, z0()),
                radius=0.07,
                color=RED
            # ).set_opacity(1 if z0() <= z_cap else 0)
        )
        )
        axis_segment = always_redraw(
            lambda: Line3D(
                start=axes.c2p(0, 0, 0),
                end=axes.c2p(0, 0, z0()),
                color=RED,
            # ).set_opacity(0.9 if z0() <= z_cap else 0)
        )
        )
        # ---- Fixed-in-frame labels ----
        formula = MathTex(r"z=\frac{1}{r+\varepsilon}", r"\quad r=\sqrt{x^2+y^2}").scale(0.7).to_corner(UL)
        eps_readout = always_redraw(
            lambda: VGroup(
                Tex(r"$\varepsilon=$").scale(0.7),
                DecimalNumber(eps.get_value(), num_decimal_places=3).scale(0.7),
            ).arrange(RIGHT, buff=0.15).next_to(formula, DOWN, aligned_edge=LEFT)
        )
        note = Tex(r"(z-axis intersection at $z(0)=1/\varepsilon$)").scale(0.55).next_to(eps_readout, DOWN, aligned_edge=LEFT)

        # self.add_fixed_in_frame_mobjects(formula, eps_readout, note)

        self.add(surface, axis_segment, axis_marker)

        # Optional: slow rotation helps "see" the spike
        self.begin_ambient_camera_rotation(rate=0.2)

        # Animate eps -> 0+
        self.play(eps.animate.set_value(0.20), run_time=3, rate_func=linear)
        # self.play(eps.animate.set_value(0.07), run_time=3, rate_func=linear)  # dot rises toward ceiling
        # self.play(eps.animate.set_value(0.02), run_time=3, rate_func=linear)  # dot disappears (above z_cap)

        self.wait(1.5)
        self.stop_ambient_camera_rotation()
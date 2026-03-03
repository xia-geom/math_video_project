from manim import *
import numpy as np

class ConeAngleNegativeCurvature(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-40 * DEGREES)

        R = 2.5          # radial extent
        z0 = 2.0         # apex above
        res = 30

        beta = ValueTracker(1.0)   # cone angle parameter (0<beta<=1)
        warp = 1.8                 # saddle strength (bigger => more negative-curvature look)

        def make_saddle_cone():
            b = beta.get_value()

            def param(r, theta):
                # "cone angle" control in the xy-plane
                x = b * r * np.cos(theta)
                y = b * r * np.sin(theta)

                # cone apex at (0,0,z0), cone goes downward as r grows
                # + a simple saddle term to induce negative-curvature behavior
                z = z0 - r + warp * (x * y)

                return np.array([x, y, z])

            s = Surface(
                param,
                u_range=[0.001, R],
                v_range=[0, TAU],
                resolution=(res, res),
            )
            s.set_style(fill_opacity=1, stroke_width=0.5)
            s.set_fill_by_checkerboard(ORANGE, BLUE, opacity=0.55)
            return s

        surface = always_redraw(make_saddle_cone)

        axes = ThreeDAxes()
        apex = Dot3D(point=np.array([0, 0, z0]), radius=0.06)

        label = MathTex(r"\beta =").to_corner(UL)
        beta_num = DecimalNumber(beta.get_value(), num_decimal_places=2).next_to(label, RIGHT)
        beta_num.add_updater(lambda m: m.set_value(beta.get_value()))

        self.add(axes, surface, apex, label, beta_num)
        self.begin_ambient_camera_rotation(rate=0.12)

        self.wait(0.5)
        self.play(beta.animate.set_value(0.25), run_time=4, rate_func=smooth)
        self.play(beta.animate.set_value(1.00), run_time=4, rate_func=smooth)
        self.wait(1.0)
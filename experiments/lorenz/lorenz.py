from manim import *
from scipy.integrate import solve_ivp


# ==========================================
# 🎛️ CONTROL ROOM (Edit this section only)
# ==========================================
DEBUG = True  # <--- TOGGLE THIS: True for speed, False for final render

if DEBUG:
    # FAST MODE (For testing camera, colors, and layout)
    DT = 0.05           # Low precision (jagged lines, but fast)
    SIM_TIME = 10       # Only calculate 10 seconds of physics
    N_CURVES = 1        # Only draw 1 curve
    ANIMATION_SPEED = 2 # Fast animation (2 seconds total)
else:
    # QUALITY MODE (For the final video)
    DT = 0.001          # High precision (smooth curves)
    SIM_TIME = 30       # Calculate 30 seconds of physics
    N_CURVES = 5        # Draw all 5 curves
    ANIMATION_SPEED = 10 # Slow, detailed animation (10 seconds)
# ==========================================

def lorenz_system(t, state, sigma=10, rho=28, beta=8 / 3):
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]


def ode_solution_points(function, state0, time, dt=0.001):
    solution = solve_ivp(
        function,
        t_span=(0, time),
        y0=state0,
        t_eval=np.arange(0, time, dt)
    )
    return solution.y.T


class LorenzAttractor(ThreeDScene):
    def construct(self):
        # Set up axes
        axes = ThreeDAxes(
            x_range=(-50, 50, 5),
            y_range=(-50, 50, 5),
            z_range=(0, 50, 5),
            x_length=10,  # Community uses length, not width/height for structure
            y_length=10,
            z_length=6,
        )
        # axes.center() # Standard axes are centered by default usually

        # Camera orientation
        self.set_camera_orientation(phi=60 * DEGREES, theta=120 * DEGREES, distance=2000)
        self.begin_ambient_camera_rotation(rate=0.1)
        
        self.add(axes)

        # Add the equations
        equations = MathTex(
            r"\frac{\mathrm{d} x}{\mathrm{~d} t} &= \sigma(y-x) \\"
            r"\frac{\mathrm{d} y}{\mathrm{~d} t} &= x(\rho-z)-y \\"
            r"\frac{\mathrm{d} z}{\mathrm{~d} t} &= x y-\beta z",
        )
        
        # Color specific parts manually or using substring matching which works differently in community sometimes
        # But let's try strict substring matching
        equations.set_color_by_tex("x", RED)
        equations.set_color_by_tex("y", GREEN)
        equations.set_color_by_tex("z", BLUE)
        
        # Position in a fixed frame (HUD-like)
        self.add_fixed_in_frame_mobjects(equations)
        equations.to_corner(UL).scale(0.8)
        equations.add_background_rectangle()
        
        self.play(Write(equations))

        # Compute a set of solutions
        epsilon = 0.1 # Slight offset to show divergence
        evolution_time = 30
        n_points = 5 # Fewer points for clearer demo, or keep 10
        
        # Initial states
        states = [
            [10, 10, 10 + n * epsilon]
            for n in range(n_points)
        ]
        
        colors = color_gradient([BLUE_E, BLUE_A], len(states))

        # Create dots and tails
        dots = VGroup()
        details = [] # List of tuples (dot, curve, etc)

        for state, color in zip(states, colors):
            points = ode_solution_points(lorenz_system, state, evolution_time)
            
            # The Dot
            dot = Dot(radius=0.1, color=color)
            dot.move_to(axes.c2p(*state))
            
            # The Trace
            # TracedPath takes a function returning the point
            # BUT we already calculated points. 
            # Better to use a ValueTracker to move the dot along the calculated points
            # or just TracedPath following the dot moving.
            
            # Let's animate the dot moving along the path.
            # We create a VMobject for the full path to guide movement
            full_path = VMobject()
            # Debugging points shape: c2p returns (3, N) when vectorized, we need (N, 3)
            raw_points = axes.c2p(*points.T).T
            
            # Use set_points_smoothly for better visuals, now that shape is correct
            full_path.set_points_smoothly(raw_points)
            
            # TracedPath follows the dot
            # dissipating_time=None ensures the path stays forever
            trace = TracedPath(dot.get_center, stroke_color=color, stroke_width=2, dissipating_time=None)
            
            dots.add(dot)
            self.add(trace, dot)
            
            # Store full path to animate movement
            details.append((dot, full_path))

        # Animate all dots moving along their paths
        self.play(
            *[MoveAlongPath(dot, path, run_time=evolution_time, rate_func=linear) 
              for dot, path in details],
            run_time=evolution_time
        )
        
        self.wait(2)
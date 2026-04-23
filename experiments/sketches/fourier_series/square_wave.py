from manim import *
import numpy as np

class FourierSquareWave(Scene):
    def construct(self):
        # Configuration
        n_terms = 5  # Number of circles (Try changing this to 1, 3, or 10!)
        
        # 1. Setup the Time Tracker
        time_tracker = ValueTracker(0)

        # 2. Define the main circle center (Left side of screen)
        # Shifted LEFT to make room for the wave graph
        center_point = LEFT * 3 

        # 3. Create the Circles and Vectors
        # We use always_redraw so they update every frame based on time_tracker
        def get_circles_and_vectors():
            circles = VGroup()
            vectors = VGroup()
            
            # Start at the center
            current_center = center_point
            t = time_tracker.get_value()
            
            # Mathematical Loop for Square Wave: k = 1, 3, 5...
            # Formula: (4/pi) * (1/k) * sin(k * t)
            # We are just drawing the rotating vectors here
            
            for k in range(1, n_terms * 2, 2):
                # Radius decreases as 1/k
                radius = 1.5 * (1 / k) 
                
                # Angle rotates as k * t
                angle = k * t 

                # Draw the circle
                circle = Circle(radius=radius, color=WHITE, stroke_opacity=0.5)
                circle.move_to(current_center)
                circles.add(circle)

                # Calculate the tip of the vector
                # x = r * cos(theta), y = r * sin(theta)
                vector_end = current_center + np.array([
                    radius * np.cos(angle),
                    radius * np.sin(angle),
                    0
                ])

                # Draw the vector (arrow)
                vector = Line(current_center, vector_end, color=YELLOW, stroke_width=2)
                vectors.add(vector)

                # Update center for the NEXT circle in the chain
                current_center = vector_end
            
            return VGroup(circles, vectors)

        # Add the dynamic object to the scene
        epicycles = always_redraw(get_circles_and_vectors)
        self.add(epicycles)

        # 4. Draw the Wave (The Trace)
        # We need a dot at the very tip of the last vector
        tip_dot = Dot(color=RED).scale(0.5)
        
        def update_dot(mob):
            # Re-calculate the final position just like above
            t = time_tracker.get_value()
            pos = center_point
            for k in range(1, n_terms * 2, 2):
                radius = 1.5 * (1/k)
                angle = 0.5 * k * t
                pos = pos + np.array([radius*np.cos(angle), radius*np.sin(angle), 0])
            mob.move_to(pos)

        tip_dot.add_updater(update_dot)
        self.add(tip_dot)

        # 5. The Wave Line
        # This draws the path of the dot, but shifted to the right to look like a graph
        # For a standard visual, we often plot (time, y) to the right.
        # But the user's code just says "TracedPath(tip_dot.get_center...)" 
        # which will just draw the square shape in space. 
        # To strictly follow the "Wave" graph idea usually implied by this demo, 
        # we would need to trace (x + time, y). 
        # BUT the user provided specific code, so I will stick to it exactly for now.
        
        # NOTE: TracedPath can be memory intensive if points accumulate forever.
        # But for 10 seconds it should be fine.
        path = TracedPath(tip_dot.get_center, stroke_color=RED, stroke_width=2, dissipating_time=None)
        
        self.add(path) 

        # 6. Run the Animation
        self.play(
            time_tracker.animate.set_value(2 * PI).set_run_time(),
            rate_func=linear
        )

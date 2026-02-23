from manim import *

class EigenvectorTransformation(Scene):
    def construct(self):
        # 1. Define the Matrix and Eigenvectors
        matrix = [[3, 1], [0, 2]]
        
        # Eigenvectors
        v1_coords = [1, 0, 0] # Eigenvalue 3
        v2_coords = [1, -1, 0] # Eigenvalue 2
        v_rand_coords = [-1, 1, 0] # Random

        # 2. Setup the Scene
        # Create a number plane (the grid)
        grid = NumberPlane()
        grid.prepare_for_nonlinear_transform() 
        # Note: prepare_for_nonlinear_transform helps with grid warping, 
        # but for linear ApplyMatrix, a standard NumberPlane is also fine. 
        # We can adding a background grid to see the warp better:
        
        # Matrix Label
        matrix_tex = MathTex(r"A = \begin{bmatrix} 3 & 1 \\ 0 & 2 \end{bmatrix}").to_edge(UL)
        self.add_foreground_mobject(matrix_tex)

        # Vectors
        v1 = Vector(v1_coords, color=YELLOW)
        v1_label = MathTex(r"\vec{v}_1").next_to(v1.get_end(), RIGHT)
        
        v2 = Vector(v2_coords, color=YELLOW)
        v2_label = MathTex(r"\vec{v}_2").next_to(v2.get_end(), DR)
        
        v_rand = Vector(v_rand_coords, color=PINK)
        
        # Group vectors and labels so we can manage them or just add them
        vectors = VGroup(v1, v2, v_rand)
        labels = VGroup(v1_label, v2_label)

        self.add(grid, vectors, labels)

        # 3. Apply the Transformation
        self.wait(1)
        
        title = MathTex("Apply Transformation...").to_edge(UP)
        self.play(Write(title))
        
        # Apply the matrix to the grid AND the vectors
        # We don't apply it to the labels (usually labels move but don't stretch, 
        # or we can apply it to them too). Let's apply to grid and vectors.
        # We use ApplyMatrix for the linear transformation animation.
        
        self.play(
            ApplyMatrix(matrix, grid),
            ApplyMatrix(matrix, vectors),
            # We can also move the labels to follow the new vector tips
            # But ApplyMatrix on text distorts it. Better to use a updater or just let them stay/slide.
            # For simplicity, let's just fade them out or let them sit there (they might be misplaced).
            # Let's try to animate them roughly or just leave them.
            run_time=5
        )
        
        # 4. Post-Transformation Annotations
        self.wait(1)
        
        # Show span line for v2
        # Calculate new endpoint for v2: A * [1, -1] = [2, -2]
        span_line = Line(
            start=ORIGIN, 
            end=[2, -2, 0], 
            color=YELLOW, 
            stroke_opacity=0.5
        )
        self.play(Create(span_line))
        self.wait(2)

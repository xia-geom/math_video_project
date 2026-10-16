"""MAT0339, manuel 11.4 et cahier 11.4 B : carré matriciel, pas entrée par entrée."""
from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GRAY_B,
    GREEN_D,
    RIGHT,
    WHITE,
    ApplyMatrix,
    Axes,
    Create,
    Dot,
    Line,
    MathTex,
    Matrix,
    Polygon,
    Rectangle,
    SurroundingRectangle,
    Tex,
    Text,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class CarreMatriceFR(TeachingScene):
    """Le carré répète la même transformation et utilise le produit matriciel."""

    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._row_column()
        self._shear_twice()
        self._composition_rule()
        self._self_check()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        original = self.formula(r'A=\begin{pmatrix}1&1\\0&1\end{pmatrix}', 48)
        mistake = self.formula(
            r'A^2\overset{?}{=}\begin{pmatrix}1^2&1^2\\0^2&1^2\end{pmatrix}'
            r'=\begin{pmatrix}1&1\\0&1\end{pmatrix}', 44,
        )
        question = self.words('Mettre chaque entrée au carré : est-ce la bonne opération ?', 28)
        self.new_page('Que signifie le carré d’une matrice ?', original, mistake, question, gap=0.48)
        self.explain(
            'Voici la matrice de la section onze point quatre du cahier. Toutes ses entrées sont zéro ou un. Si nous mettions chaque entrée au carré, rien ne changerait. Peut-on en conclure que le carré de cette matrice est encore elle-même ?',
            original, mistake, hold=2,
        )
        self.explain(
            'Cette tentation vient de l’addition et de la multiplication par un nombre, qui se font entrée par entrée. Mais le carré d’une matrice signifie la multiplier par elle-même. Il faut utiliser le produit matriciel, ligne par colonne.',
            question, hold=2,
        )

    def _row_column(self):
        first = Matrix([[1, 1], [0, 1]], element_to_mobject_config={'color': BLACK, 'font_size': 38})
        second = Matrix([[1, 1], [0, 1]], element_to_mobject_config={'color': BLACK, 'font_size': 38})
        product = VGroup(
            self.formula(r'A^2=', 43), first, self.formula(r'\cdot', 42), second,
        ).arrange(RIGHT, buff=0.35)
        entry = self.formula(r'\text{Entrée }(1,2):\quad1\times1+1\times1=2', 38, BLUE_D)
        result = panel(self.formula(r'A^2=\begin{pmatrix}1&2\\0&1\end{pmatrix}', 46), width=6.3, height=1.6)
        self.new_page('Suivre la ligne et la colonne', product, entry, result, gap=0.42)
        self.explain(
            'Écrivons les deux copies de A. Pour calculer l’entrée de la première ligne et de la deuxième colonne du résultat, sélectionnons la première ligne de la matrice de gauche et la deuxième colonne de celle de droite.',
            product, hold=2,
        )
        row_box = SurroundingRectangle(first.get_rows()[0], color=BLUE_D, buff=0.12)
        column_box = SurroundingRectangle(second.get_columns()[1], color=BLUE_D, buff=0.12)
        product.add(row_box, column_box)
        self.play(Create(row_box), Create(column_box), run_time=0.9)
        self.explain(
            'La ligne contient un, un, et la colonne contient un, un. Les produits correspondants s’additionnent : un fois un, plus un fois un, donne deux. L’entrée supérieure droite change donc réellement.',
            entry, hold=2,
        )
        self.explain(
            'Le même calcul aux trois autres positions donne un, zéro et un. Nous obtenons cette matrice. Un seul coefficient différent suffisait déjà à réfuter le calcul entrée par entrée, mais nous avons maintenant tout le carré.',
            result, hold=2,
        )

    def _shear_twice(self):
        # Fixed axes: both unit scales are 1.2. Only the blue unit grid is sheared.
        axes = Axes(
            x_range=[-0.5, 3.5, 1], y_range=[-0.5, 1.5, 1],
            x_length=4.8, y_length=2.4,
            axis_config={'color': GRAY_B, 'include_tip': False, 'stroke_width': 1.3},
        )
        canvas = Rectangle(width=5.5, height=3.6, stroke_opacity=0)
        axes.move_to(canvas)
        diagram = VGroup(canvas, axes)
        label = self.words('Le même quadrillage, transformé', 26).next_to(axes, DOWN, buff=0.24)
        diagram.add(label)
        rule = self.formula(r'A\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}x+y\\y\end{pmatrix}', 38)
        point_zero = self.formula(r'(0,1)', 40)
        point_one = self.formula(r'(1,1)', 40)
        point_two = self.formula(r'(2,1)', 40, GREEN_D)
        points = VGroup(point_zero, point_one, point_two).arrange(DOWN, buff=0.32)
        right = VGroup(rule, points).arrange(DOWN, buff=0.45)
        row = VGroup(diagram, right).arrange(RIGHT, buff=0.55)
        self.new_page('Appliquer la transformation deux fois', row)
        origin = axes.c2p(0, 0)
        grid = VGroup()
        for value in (0, 0.5, 1):
            grid.add(Line(axes.c2p(value, 0), axes.c2p(value, 1), color=BLUE_D, stroke_width=2.5))
            grid.add(Line(axes.c2p(0, value), axes.c2p(1, value), color=BLUE_D, stroke_width=2.5))
        unit_square = Polygon(
            axes.c2p(0, 0), axes.c2p(1, 0), axes.c2p(1, 1), axes.c2p(0, 1),
            stroke_opacity=0, fill_color=BLUE_D, fill_opacity=0.06,
        )
        grid.add(unit_square)
        dot = Dot(axes.c2p(0, 1), radius=0.09, color=GREEN_D)
        diagram.add(grid, dot)
        self.explain(
            'Comprenons ce deux avec la géométrie. La matrice envoie le point x, y sur x plus y, y. La hauteur reste fixe, et l’abscisse augmente de cette hauteur. Le quadrillage bleu montre cette déformation ; les axes gris restent fixes.',
            axes, label, grid, dot, rule, point_zero, hold=2,
        )
        self.play(
            ApplyMatrix([[1, 1], [0, 1]], grid, about_point=origin),
            dot.animate.move_to(axes.c2p(1, 1)),
            run_time=1.7,
        )
        self.explain(
            'Le point zéro, un devient un, un. À hauteur un, toute la ligne a avancé d’une unité. Les points de hauteur zéro, eux, n’ont pas bougé. Nous avons appliqué A une première fois.',
            point_one, hold=2,
        )
        self.play(
            ApplyMatrix([[1, 1], [0, 1]], grid, about_point=origin),
            dot.animate.move_to(axes.c2p(2, 1)),
            run_time=1.7,
        )
        self.explain(
            'Appliquons exactement la même transformation une seconde fois. La hauteur vaut toujours un, donc le point avance encore d’une unité et arrive en deux, un. C’est ce que représente le coefficient deux dans le carré de A.',
            point_two, hold=2,
        )

    def _composition_rule(self):
        equation = self.formula(r'A^2\vec v=A(A\vec v)', 50)
        points = self.formula(r'(x,y)\longmapsto(x+y,y)\longmapsto(x+2y,y)', 38)
        conclusion = self.words('Le carré répète la transformation, pas les entrées.', 29)
        self.new_page('Une puissance compte les applications', equation, points, conclusion)
        self.explain(
            'Le calcul sur un point quelconque confirme l’animation. Après une application, l’abscisse vaut x plus y. Après deux applications, elle vaut x plus deux y, et la hauteur reste y. Nous avons répété une transformation, pas mis ses coefficients au carré.',
            equation, points, conclusion, hold=2,
        )

    def _self_check(self):
        matrix = self.formula(r'A=\begin{pmatrix}1&1\\0&1\end{pmatrix}', 46)
        question = self.formula(r'A^3=\ ?\qquad A^3\begin{pmatrix}0\\1\end{pmatrix}=\ ?', 44)
        self.new_page('À vous : une troisième application', matrix, question)
        self.explain(
            'Que deviennent la matrice et le point zéro, un après une troisième application ? Vous pouvez multiplier le carré déjà calculé par A, ou suivre le déplacement du point. Cherchez les deux réponses avant de continuer.',
            matrix, question, hold=2, pause_after=6,
        )
        cube = self.formula(r'A^3=\begin{pmatrix}1&3\\0&1\end{pmatrix}', 48, BLUE_D)
        result = self.formula(r'A^3\begin{pmatrix}0\\1\end{pmatrix}=\begin{pmatrix}3\\1\end{pmatrix}', 46)
        self.new_page('Réponse : encore une unité à droite', cube, result)
        self.explain(
            'L’entrée supérieure droite devient trois. Le point arrive en trois, un, car chaque application ajoute encore sa hauteur à son abscisse. Les deux méthodes, produit matriciel et transformation géométrique, donnent le même résultat.',
            cube, result, hold=2,
        )

    def _takeaway(self):
        rule = self.formula(r'A^2=A\cdot A,\qquad A^3=A\cdot A\cdot A', 43)
        source = self.words('Manuel 11.4 · Cahier 11.4 B', 28)
        self.new_page('Le réflexe à garder', rule, source)
        self.explain(
            'Pour une matrice carrée, une puissance utilise le produit matriciel. Reprenez la deuxième question de la section onze point quatre du cahier : après le carré et le cube, elle vous invite à conjecturer la puissance générale.',
            rule, source, hold=2,
        )

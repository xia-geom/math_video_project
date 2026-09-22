"""S05 — Cramer's rule in dimension two, including the singular case."""
from manim import BLACK, WHITE, MathTex, Tex, Text, config

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)
MATRIX = ((2, 1), (1, -1))
RHS = (5, 1)


def determinant(matrix):
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError('A two-by-two matrix is required.')
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def cramer(matrix, rhs):
    from fractions import Fraction
    if len(rhs) != 2:
        raise ValueError('Two right-hand-side entries are required.')
    d = determinant(matrix)
    if d == 0:
        raise ValueError('Cramer requires a nonzero determinant.')
    dx = determinant(((rhs[0], matrix[0][1]), (rhs[1], matrix[1][1])))
    dy = determinant(((matrix[0][0], rhs[0]), (matrix[1][0], rhs[1])))
    return Fraction(dx, d), Fraction(dy, d)


class RegleCramerFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        a = panel(self.formula(r'\begin{cases}2x+y=5\\x-y=1\end{cases}', 40))
        b = self.formula(r'\begin{pmatrix}2&1\\1&-1\end{pmatrix}\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}5\\1\end{pmatrix}', 38)
        self.new_page('Résoudre avec des déterminants', a, b)
        self.explain('Nous cherchons un couple qui satisfait simultanément les deux équations.', a, hold=3)
        self.explain('Les coefficients forment la matrice du système. On conserve l’ordre des inconnues et l’ordre des équations.', b, hold=4)

        a = panel(self.formula(r'D=\begin{vmatrix}2&1\\1&-1\end{vmatrix}=2(-1)-1(1)=-3', 38))
        b = self.words('Déterminant non nul : une solution unique.')
        self.new_page('Vérifier la condition avant de diviser', a, b)
        self.explain('Le déterminant vaut le produit de la diagonale principale moins le produit de l’autre diagonale. Ici, il vaut moins trois.', a, hold=4)
        self.explain('Il est non nul. La règle de Cramer s’applique et le système possède une solution unique.', b, hold=3)

        a = panel(self.formula(r'D_x=\begin{vmatrix}5&1\\1&-1\end{vmatrix}=-6', 42))
        b = self.formula(r'x=\frac{D_x}{D}=\frac{-6}{-3}=2', 42)
        self.new_page('Pour x : remplacer la première colonne', a, b)
        self.explain('Pour calculer x, remplaçons la colonne de ses coefficients par le second membre. L’autre colonne ne change pas.', a, hold=4)
        self.explain('Ce nouveau déterminant vaut moins six. En le divisant par le déterminant initial, on trouve x égal à deux.', b, hold=4)

        a = panel(self.formula(r'D_y=\begin{vmatrix}2&5\\1&1\end{vmatrix}=-3', 42))
        b = self.formula(r'y=\frac{D_y}{D}=\frac{-3}{-3}=1', 42)
        self.new_page('Pour y : remplacer la deuxième colonne', a, b)
        self.explain('Pour calculer y, on repart de la matrice initiale. Cette fois, seule la deuxième colonne est remplacée par le second membre.', a, hold=4)
        self.explain('Le déterminant vaut moins trois. Le quotient donne y égal à un.', b, hold=4)

        a = panel(self.formula(r'2\times2+1=5,\qquad2-1=1', 40))
        b = self.words('La solution vérifie les deux équations initiales.')
        self.new_page('Vérifier le résultat', a, b)
        self.explain('Remplaçons les deux inconnues dans les équations de départ. On obtient bien cinq et un.', a, hold=4)
        self.explain('Cette substitution permet notamment de repérer une erreur de signe ou une colonne mal remplacée.', b, hold=3)

        a = panel(self.formula(r'\begin{cases}x+y=2\\2x+2y=4\end{cases}\quad\text{infinité de solutions}', 34))
        b = panel(self.formula(r'\begin{cases}x+y=2\\2x+2y=5\end{cases}\quad\text{aucune solution}', 34))
        self.new_page('Si le déterminant est nul', a, b)
        self.explain('Dans ce premier système, les deux équations décrivent la même droite. Son déterminant est nul, mais il existe une infinité de solutions.', a, hold=4)
        self.explain('Dans le second, les équations sont incompatibles. Un déterminant nul ne permet donc pas de conclure automatiquement qu’il n’y a aucune solution. On revient aux équations ou à l’élimination.', b, hold=5)

        a = self.words('Pour calculer y, quelle colonne remplace-t-on ?')
        b = self.words('La deuxième, dans la matrice initiale.')
        c = self.formula(r'D\ne0', 42)
        self.new_page('À vous : la règle et sa condition', a, b, c)
        self.explain('Quelle colonne faut-il remplacer pour calculer y ? Et quelle condition doit-on vérifier ?', a, hold=6, pause_after=6)
        self.explain('On remplace la deuxième colonne de la matrice initiale, et son déterminant doit être non nul.', b, c, hold=4)
        self.wait(1)

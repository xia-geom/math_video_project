"""S01 — operations on real numbers; authored syllabus candidate."""
from manim import (
    BLACK, BLUE_D, DOWN, RIGHT, UP, WHITE, Arrow, Dot, MathTex,
    NumberLine, Square, Tex, Text, VGroup, config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


def sixths(count):
    if not 0 <= count <= 6:
        raise ValueError('A unit contains six sixths.')
    return VGroup(*[
        Square(side_length=0.65, stroke_color=BLACK, stroke_width=2,
               fill_color=BLUE_D, fill_opacity=0.3 if i < count else 0)
        for i in range(6)
    ]).arrange(RIGHT, buff=0)


class OperationsNombresReelsFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        a = panel(self.formula(r'2+3\times4\quad\text{ou}\quad(2+3)\times4\ ?'))
        b = self.words('Les parenthèses changent le calcul.')
        self.new_page('Quel calcul effectue-t-on ?', a, b)
        self.explain('Ces deux expressions contiennent les mêmes nombres. Mais les parenthèses ne demandent pas le même calcul.', a, hold=3)
        self.explain('On commence par les parenthèses, puis les puissances, puis les produits et quotients. On termine par les sommes et différences.', b, hold=3)

        a = panel(self.formula(r'2+3\times4=2+12=14'))
        b = panel(self.formula(r'(2+3)\times4=5\times4=20'))
        self.new_page('Respecter les priorités', a, b)
        self.explain('Sans parenthèses, le produit trois fois quatre est calculé avant l’addition.', a, hold=3)
        self.explain('Avec les parenthèses, on additionne deux et trois avant de multiplier. Pour des opérations de même priorité, on procède de gauche à droite.', b, hold=3)

        line = NumberLine(x_range=[-4, 4, 1], length=8, include_numbers=True,
                          color=BLACK, font_size=28, decimal_number_config={'color': BLACK})
        arrow = Arrow(line.n2p(-1) + 0.5 * UP, line.n2p(2) + 0.5 * UP,
                      buff=0, color=BLUE_D)
        move = self.formula('+3', 32).next_to(arrow, UP, buff=0.12)
        diagram = VGroup(line, arrow, move, Dot(line.n2p(-1), color=BLACK),
                         Dot(line.n2p(2), color=BLUE_D))
        a = panel(self.formula(r'-1-(-3)=-1+3=2'))
        self.new_page('Soustraire un nombre négatif', diagram, a)
        self.explain('Partons de moins un. Soustraire moins trois revient à ajouter trois : on se déplace de trois unités vers la droite.', diagram, hold=4)
        self.explain('Le résultat est deux. Le signe de l’opération et le signe du nombre ont des rôles différents.', a, hold=3)

        a = panel(self.formula(r'-3^2=-(3^2)=-9'))
        b = panel(self.formula(r'(-3)^2=(-3)\times(-3)=9'))
        self.new_page('Quel nombre est mis au carré ?', a, b)
        self.explain('Sans parenthèses, le carré porte sur trois, puis on prend l’opposé.', a, hold=3)
        self.explain('Avec les parenthèses, le carré porte sur moins trois tout entier. Le produit de deux nombres négatifs est positif.', b, hold=3)

        left = VGroup(self.formula(r'\frac12=\frac36', 38), sixths(3)).arrange(DOWN, buff=0.35)
        right = VGroup(self.formula(r'\frac13=\frac26', 38), sixths(2)).arrange(DOWN, buff=0.35)
        bars = VGroup(left, right).arrange(RIGHT, buff=0.8)
        a = panel(self.formula(r'\frac12+\frac13=\frac36+\frac26=\frac56', 40))
        self.new_page('Additionner des parts de même taille', bars, a)
        self.explain('Chaque barre représente la même unité, découpée en six parts égales. Une moitié vaut trois sixièmes et un tiers vaut deux sixièmes.', bars, hold=4)
        self.explain('On additionne les nombres de sixièmes. On n’additionne pas les dénominateurs.', a, hold=4)

        a = panel(self.formula(r'\frac{a}{b}\div\frac{c}{d}=\frac{a}{b}\times\frac{d}{c}', 40))
        b = self.formula(r'b\ne0,\quad c\ne0,\quad d\ne0', 36)
        c = self.words('Diviser par zéro n’est jamais permis.')
        self.new_page('Diviser : vérifier les conditions', a, b, c, gap=0.35)
        self.explain('Diviser par une fraction non nulle revient à multiplier par son inverse.', a, hold=3)
        self.explain('Les deux dénominateurs doivent être non nuls. Le numérateur de la fraction par laquelle on divise doit aussi être non nul.', b, c, hold=4)

        a = panel(self.formula(r'-2^2+\frac12\div\frac14\ =\ ?'))
        b = self.formula(r'-4+2=-2')
        self.new_page('À vous de vérifier', a, b)
        self.explain('Calculez cette expression avant de regarder la réponse. Quel nombre est au carré ? Quelle fraction doit-on inverser ?', a, hold=6, pause_after=6)
        self.explain('Le premier terme vaut moins quatre. Une moitié divisée par un quart vaut deux. Le résultat est donc moins deux.', b, hold=4)
        self.wait(1)

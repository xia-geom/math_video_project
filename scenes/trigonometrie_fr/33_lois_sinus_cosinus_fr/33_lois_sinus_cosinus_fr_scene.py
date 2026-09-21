"""S09 — sine and cosine laws in a nondegenerate general triangle."""
import math

from manim import BLACK, DOWN, LEFT, RIGHT, UP, WHITE, Line, MathTex, Tex, Text, VGroup, config

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


def cosine_side(a, b, angle_radians):
    if a <= 0 or b <= 0 or not 0 < angle_radians < math.pi:
        raise ValueError('Positive sides and an included angle strictly between zero and pi are required.')
    return math.sqrt(a * a + b * b - 2 * a * b * math.cos(angle_radians))


class LoisSinusCosinusFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        pa, pb, pc = [-2, -0.9, 0], [2, -0.9, 0], [0.6, 1.4, 0]
        sa, sb, sc = Line(pb, pc, color=BLACK), Line(pa, pc, color=BLACK), Line(pa, pb, color=BLACK)
        diagram = VGroup(sa, sb, sc,
                         self.formula('A', 30).next_to(pa, LEFT, buff=0.12),
                         self.formula('B', 30).next_to(pb, RIGHT, buff=0.12),
                         self.formula('C', 30).next_to(pc, UP, buff=0.12),
                         self.formula('a', 32).next_to(sa.get_center(), RIGHT, buff=0.18),
                         self.formula('b', 32).next_to(sb.get_center(), LEFT, buff=0.18),
                         self.formula('c', 32).next_to(sc, DOWN, buff=0.18))
        self.new_page('Un triangle quelconque', diagram)
        self.explain('Dans un triangle non aplati, on nomme les angles A, B et C. Le côté a est opposé à A, b est opposé à B et c est opposé à C. Cette correspondance est essentielle.', diagram, hold=5)

        a = panel(self.formula(r'\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}', 42))
        b = self.formula(r'A+B+C=180^\circ', 40)
        self.new_page('La loi des sinus', a, b)
        self.explain('Le rapport d’un côté au sinus de l’angle opposé est le même pour les trois côtés. On peut l’obtenir en exprimant une même hauteur de deux manières.', a, hold=5)
        self.explain('Les trois angles sont strictement positifs et leur somme vaut cent quatre-vingts degrés. On ne divise donc pas par un sinus nul.', b, hold=4)

        a = panel(self.formula(r'A=30^\circ,\quad B=45^\circ,\quad a=2', 38))
        b = self.formula(r'b=\frac{a\sin B}{\sin A}=\frac{2(\sqrt2/2)}{1/2}=2\sqrt2', 38)
        self.new_page('Exemple : deux angles et un côté', a, b)
        self.explain('Supposons que A vaut trente degrés, B quarante-cinq degrés, et le côté opposé à A mesure deux. Le troisième angle vaut cent cinq degrés : les données sont compatibles.', a, hold=4)
        self.explain('La loi des sinus permet de calculer b. On associe bien b à B et a à A. Le résultat est deux racines de deux.', b, hold=5)

        a = panel(self.formula(r'c^2=a^2+b^2-2ab\cos C', 42))
        b = self.words('C est l’angle compris entre les côtés a et b.')
        self.new_page('La loi des cosinus', a, b)
        self.explain('La loi des cosinus relie deux côtés et leur angle compris au troisième côté.', a, hold=4)
        self.explain('Si C vaut quatre-vingt-dix degrés, son cosinus vaut zéro. On retrouve le théorème de Pythagore. Sinon, le terme supplémentaire corrige la relation.', b, hold=4)

        a = panel(self.formula(r'a=3,\quad b=4,\quad C=60^\circ', 40))
        b = self.formula(r'c^2=9+16-24\times\frac12=13', 40)
        c = self.formula(r'c=\sqrt{13}', 42)
        self.new_page('Deux côtés et l’angle compris', a, b, c, gap=0.35)
        self.explain('Prenons deux côtés de longueurs trois et quatre, séparés par un angle de soixante degrés.', a, hold=4)
        self.explain('Le cosinus de soixante degrés vaut une moitié. Le carré du côté opposé à cet angle vaut donc treize.', b, hold=4)
        self.explain('Une longueur est positive : on retient la racine positive de treize.', c, hold=3)

        a = panel(self.formula(r'\sin30^\circ=\sin150^\circ=\frac12', 40))
        b = self.words('Un sinus connu ne détermine pas toujours un seul angle.')
        self.new_page('Attention au cas ambigu', a, b)
        self.explain('La loi des sinus peut fournir la valeur du sinus d’un angle. Mais trente et cent cinquante degrés ont le même sinus.', a, hold=4)
        self.explain('Avec deux côtés et un angle non compris, il peut exister zéro, un ou deux triangles. Il faut vérifier les autres données et la somme des angles, pas retenir automatiquement la première valeur de la calculatrice.', b, hold=5)

        a = self.words('Deux côtés et leur angle compris sont connus.')
        b = self.words('Commencer par la loi des cosinus.')
        self.new_page('À vous : choisir la loi utile', a, b)
        self.explain('Quelle loi permet de trouver directement le troisième côté quand on connaît deux côtés et leur angle compris ?', a, hold=6)
        self.explain('La loi des cosinus. Si l’on connaît plutôt une paire côté-angle opposé et un autre angle, la loi des sinus est souvent la plus directe.', b, hold=4)
        self.wait(1)

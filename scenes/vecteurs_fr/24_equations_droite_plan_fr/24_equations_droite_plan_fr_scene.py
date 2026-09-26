"""S04 — parametric lines and Cartesian planes, with membership checks."""
from manim import (
    BLACK, BLUE_D, RIGHT, UP, WHITE, Arrow, Axes, Dot,
    MathTex, Tex, Text, VGroup, config,
)

from tools.branding import play_uqam_intro
from tools.expanded_teaching import ExpandedTeachingScene as TeachingScene
from tools.teaching_layout import panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


def line_value(x, y):
    return x + 2 * y - 5


def plane_value(x, y, z):
    return x + 2 * y - z + 1


class EquationsDroitePlanFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        a = panel(self.formula(r'A=(1,2),\qquad\vec v=(2,-1)', 40))
        b = panel(self.formula(r'(x,y)=(1,2)+t(2,-1),\qquad t\in\mathbb R', 36))
        self.new_page('Décrire une droite par un déplacement', a, b)
        self.explain('Un point de départ et un vecteur directeur non nul déterminent une droite. Partons du point un, deux, dans la direction deux, moins un.', a, hold=4)
        self.explain('En multipliant ce vecteur par un réel t, puis en l’ajoutant au point de départ, on parcourt toute la droite.', b, hold=4)

        ax = Axes(x_range=[-1, 5, 1], y_range=[-1, 4, 1], x_length=3.6,
                  y_length=3.0, tips=False, axis_config={'color': BLACK})
        graph = ax.plot(lambda x: (5 - x) / 2, x_range=[-1, 5], color=BLACK)
        start, end = ax.c2p(1, 2), ax.c2p(3, 1)
        arrow = Arrow(start, end, buff=0, color=BLUE_D)
        diagram = VGroup(ax, graph, arrow, Dot(start, color=BLACK), Dot(end, color=BLUE_D),
                         self.formula('A=(1,2)', 28).next_to(start, UP + RIGHT, buff=0.28),
                         self.formula('B=(3,1)', 28).next_to(end, UP + RIGHT, buff=0.28),
                         ax.get_axis_labels(self.formula('x', 28), self.formula('y', 28)))
        self.new_page('Un pas : deux à droite, un vers le bas', diagram)
        self.explain('Pour t égal à un, on arrive au point trois, un. Les deux axes utilisent la même échelle : la flèche représente fidèlement le déplacement.', diagram, hold=5)

        a = panel(self.formula(r'x=1+2t,\quad y=2-t\quad\Longrightarrow\quad x+2y=5', 36))
        b = self.formula(r'B=(3,1):\quad3+2\times1=5', 38)
        self.new_page('Éliminer le paramètre', a, b)
        self.explain('En additionnant x et deux fois y, le paramètre disparaît. On obtient l’équation cartésienne de la même droite.', a, hold=4)
        self.explain('Pour vérifier qu’un point appartient à la droite, on remplace les coordonnées. Le point trois, un satisfait bien l’équation.', b, hold=4)

        a = panel(self.formula(r'(x,y,z)=(1,0,2)+t(2,1,-1),\quad t\in\mathbb R', 34))
        b = self.words('Une droite dans l’espace : un seul paramètre.')
        self.new_page('Une droite dans l’espace', a, b)
        self.explain('Dans l’espace, une droite se décrit de la même manière, mais avec trois coordonnées. Le vecteur directeur doit toujours être non nul.', a, hold=4)
        self.explain('Un seul paramètre suffit pour parcourir cette droite. Une seule équation cartésienne non triviale dans l’espace décrit plutôt un plan.', b, hold=4)

        a = panel(self.formula(r'A=(1,0,2),\quad\vec n=(1,2,-1)', 38))
        b = panel(self.formula(r'\vec n\cdot\overrightarrow{AM}=0\quad\Longleftrightarrow\quad x+2y-z+1=0', 34))
        self.new_page('Un plan : un point et une normale', a, b)
        self.explain('Pour décrire un plan, choisissons un point et un vecteur normal non nul. Ce vecteur est perpendiculaire à tous les déplacements dans le plan.', a, hold=4)
        self.explain('Pour un point M de coordonnées x, y, z, on développe le produit scalaire : x moins un, plus deux y, moins z plus deux. Il doit être nul, ce qui donne cette équation.', b, hold=5)

        a = panel(self.formula(r'M=(3,0,4):\quad3+2\times0-4+1=0', 36))
        b = panel(self.formula(r'N=(3,0,3):\quad3+2\times0-3+1=1\ne0', 36))
        self.new_page('Tester l’appartenance au plan', a, b)
        self.explain('Le point trois, zéro, quatre appartient au plan : ses coordonnées donnent zéro.', a, hold=3)
        self.explain('Le point trois, zéro, trois n’y appartient pas. L’équation est un test d’appartenance, pas seulement une formule à mémoriser.', b, hold=4)

        a = panel(self.formula(r'Q=(1,1,4)\quad\text{appartient-il au plan ?}', 36))
        b = self.formula(r'1+2\times1-4+1=0\quad\Longrightarrow\quad\text{oui}', 38)
        self.guided_examples('equations_droite_plan')
        self.new_page('À vous : remplacer les coordonnées', a, b)
        self.explain('Testez maintenant le point un, un, quatre dans l’équation du plan.', a, hold=6, pause_after=6)
        self.explain('Le résultat est zéro. Ce point appartient donc au plan. Pour une droite comme pour un plan, conservez les coordonnées et les conditions de définition.', b, hold=4)
        self.wait(1)

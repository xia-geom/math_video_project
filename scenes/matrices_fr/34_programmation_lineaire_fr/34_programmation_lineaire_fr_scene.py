"""S07 — two-variable linear programming on a bounded feasible polygon."""
from manim import (
    BLACK, BLUE_D, RIGHT, WHITE, Axes, Dot, Line, MathTex,
    Polygon, Tex, Text, Transform, VGroup, config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)
VERTICES = ((0, 0), (4, 0), (4, 1), (2, 3), (0, 3))


def feasible(x, y):
    return x >= 0 and y >= 0 and x <= 4 and y <= 3 and x + y <= 5


def objective_value(x, y):
    return 3 * x + 2 * y


class ProgrammationLineaireFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        a = panel(self.formula(r'\text{Maximiser }z=3x+2y', 42))
        b = self.words('Deux quantités réelles, des ressources limitées.')
        self.new_page('Chercher la meilleure solution admissible', a, b)
        self.explain('Imaginons deux quantités x et y. Chaque unité de x contribue trois à notre objectif, et chaque unité de y contribue deux.', a, hold=4)
        self.explain('Les quantités sont ici des variables réelles. Si l’on exigeait des quantités entières, ce serait une contrainte supplémentaire.', b, hold=4)

        a = panel(self.formula(r'x\ge0,\quad y\ge0,\quad x\le4,\quad y\le3', 38))
        b = panel(self.formula(r'x+y\le5', 42))
        self.new_page('Toutes les contraintes en même temps', a, b)
        self.explain('Les quantités sont non négatives. On dispose au maximum de quatre unités de x et de trois unités de y.', a, hold=4)
        self.explain('Une dernière ressource impose que leur somme ne dépasse pas cinq. Une solution admissible doit respecter toutes ces contraintes simultanément.', b, hold=4)

        ax = Axes(x_range=[0, 5, 1], y_range=[0, 4, 1], x_length=4,
                  y_length=3.2, tips=False, axis_config={'color': BLACK})
        region = Polygon(*[ax.c2p(x, y) for x, y in VERTICES],
                         stroke_color=BLUE_D, stroke_width=3,
                         fill_color=BLUE_D, fill_opacity=0.12)
        level = Line(ax.c2p(0, 3), ax.c2p(2, 0), color=BLACK, stroke_width=3)
        optimum = Dot(ax.c2p(4, 1), color=BLUE_D)
        label = self.formula('(4,1)', 30).next_to(optimum, RIGHT, buff=0.18)
        diagram = VGroup(ax, region, level,
                         ax.get_axis_labels(self.formula('x', 28), self.formula('y', 28)))
        self.new_page('Déplacer une droite de niveau', diagram)
        self.explain('La zone bleue est l’intersection des contraintes, bords compris. La droite noire représente d’abord les points où l’objectif vaut six.', diagram, hold=4)
        # Meaningful geometric correspondence: parallel level lines, not text morphing.
        self.play(Transform(level, Line(ax.c2p(2, 4), ax.c2p(14 / 3, 0),
                                        color=BLACK, stroke_width=3)), run_time=2)
        self.explain('En déplaçant cette droite parallèlement pour augmenter l’objectif, le dernier contact avec la zone admissible est le sommet quatre, un.', optimum, label, hold=4)
        self.page.add(optimum, label)

        a = self.words('Région polygonale non vide et bornée.')
        b = self.words('Un objectif linéaire atteint un maximum à un sommet.')
        c = self.words('Il peut aussi être constant le long d’un côté optimal.')
        self.new_page('Pourquoi regarder les sommets ?', a, b, c)
        self.explain('Dans cet exemple, la région admissible est un polygone non vide et borné.', a, hold=3)
        self.explain('Un objectif linéaire y atteint un maximum à au moins un sommet. Cela permet de comparer un nombre fini de candidats.', b, hold=4)
        self.explain('Attention : le maximum n’est pas toujours unique. Si une droite de niveau suit un côté optimal, tous les points de ce côté conviennent.', c, hold=4)

        a = panel(self.formula(r'\begin{array}{c|ccccc}(x,y)&(0,0)&(4,0)&(4,1)&(2,3)&(0,3)\\\hline 3x+2y&0&12&14&12&6\end{array}', 34))
        b = self.formula(r'z_{\max}=14\quad\text{pour }(x,y)=(4,1)', 38)
        self.new_page('Comparer les valeurs admissibles', a, b)
        self.explain('Calculons la valeur de l’objectif à chaque sommet. Le tableau donne zéro, douze, quatorze, douze et six.', a, hold=5)
        self.explain('La plus grande valeur est quatorze, atteinte au sommet quatre, un.', b, hold=4)

        a = panel(self.formula(r'3x+2y=2(x+y)+x\le2\times5+4=14', 36))
        b = self.words('Le point (4,1) atteint cette borne.')
        self.new_page('Une vérification directe du maximum', a, b)
        self.explain('Voici une vérification indépendante du dessin. Pour tout point admissible, deux fois x plus y, puis x en plus, ne dépasse pas deux fois cinq plus quatre. Autrement dit, on utilise deux fois la somme x plus y, puis on ajoute x.', a, hold=5)
        self.explain('La borne quatorze est atteinte par le point quatre, un. On a donc prouvé qu’aucun point admissible ne donne davantage.', b, hold=4)

        a = panel(self.formula(r'(4,3):\quad z=18\quad\text{mais}\quad4+3>5', 38))
        b = self.words('Un grand objectif ne compense pas une contrainte violée.')
        self.new_page('À vous : pourquoi rejeter ce candidat ?', a, b)
        self.explain('Le point quatre, trois donne une valeur de dix-huit. Pourquoi n’est-il pas une meilleure solution ?', a, hold=6)
        self.explain('Parce qu’il viole la contrainte sur la somme. On vérifie d’abord l’admissibilité, puis on compare les objectifs. Un problème peut aussi avoir une région vide ou un objectif non borné.', b, hold=4)
        self.wait(1)

"""S07 — two-variable linear programming on a bounded feasible polygon."""
from manim import (BLACK, RIGHT, WHITE, Axes, Dot, Line, MathTex, Polygon, Tex, Text, Transform, VGroup, config)

from tools import tts
from tools.teaching_chapters import (play_lesson_opening, play_chapter_outline, play_lesson_closing)
from tools.expanded_teaching import ExpandedTeachingScene as TeachingScene
from tools.teaching_layout import panel

CHAPTERS = ('Décrire les contraintes', 'Chercher le maximum', 'Vérifier et s’entraîner')

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
    def chapter_narration(self, spoken):
        return self.voiceover(text=tts.ssml(spoken), subcaption=tts.strip_ssml(spoken))

    def construct(self):
        self.setup_narration()
        narration = None if self.silent else self.chapter_narration
        play_lesson_opening(self, 'Programmation linéaire', 'Distinguer les points admissibles\net ceux qui maximisent un objectif.', narration=narration)
        play_chapter_outline(self, CHAPTERS, 0, 'Commençons par les données et la question.', narration=narration)
        a = panel(self.formula(r'\text{Maximiser }z=3x+2y', 42))
        b = self.words('Deux quantités réelles, des ressources limitées.')
        self.new_page('Optimiser sous contraintes', a, b)
        self.explain('Imaginons deux quantités x et y. Chaque unité de x contribue trois à notre objectif, et chaque unité de y contribue deux.', a, hold=4)
        self.explain('Les quantités sont ici des variables réelles. Si l’on exigeait des quantités entières, ce serait une contrainte supplémentaire.', b, hold=4)

        a = panel(self.formula(r'x\ge0,\quad y\ge0,\quad x\le4,\quad y\le3', 38))
        b = panel(self.formula(r'x+y\le5', 42))
        self.new_page('Toutes les contraintes en même temps', a, b)
        self.explain('Les quantités sont non négatives. On dispose au maximum de quatre unités de x et de trois unités de y.', a, hold=4)
        self.explain('Une dernière ressource impose que leur somme ne dépasse pas cinq. Une solution admissible doit respecter toutes ces contraintes simultanément.', b, hold=4)

        play_chapter_outline(self, CHAPTERS, 1, 'Représentons les contraintes et cherchons le maximum.', narration=narration)
        ax = Axes(x_range=[0, 5, 1], y_range=[0, 4, 1], x_length=4,
                  y_length=3.2, tips=False, axis_config={'color': BLACK})
        region = Polygon(*[ax.c2p(x, y) for x, y in VERTICES],
                         stroke_color=BLACK, stroke_width=3,
                         fill_color=BLACK, fill_opacity=0.12)
        level = Line(ax.c2p(0, 3), ax.c2p(2, 0), color=BLACK, stroke_width=3)
        diagram = VGroup(ax, region, level,
                         ax.get_axis_labels(self.formula('x', 28), self.formula('y', 28)))
        self.new_page('Déplacer une droite de niveau', diagram)
        # Anchor late-revealed objects to the axes after page layout has moved them.
        optimum = Dot(ax.c2p(4, 1), color=BLACK)
        label = self.formula('(4,1)', 30).next_to(optimum, RIGHT, buff=0.18)
        self.explain('La zone ombrée est l’intersection des contraintes, bords compris. La droite oblique représente d’abord les points où l’objectif vaut six.', diagram, hold=4)
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
        self.explain('Pour tout point admissible, on écrit trois x plus deux y comme deux fois la somme x plus y, plus x. La somme ne dépasse pas cinq, et x ne dépasse pas quatre. L’objectif ne dépasse donc pas quatorze.', a, hold=5)
        self.explain('La borne quatorze est atteinte par le point quatre, un. On a donc prouvé qu’aucun point admissible ne donne davantage.', b, hold=4)

        play_chapter_outline(self, CHAPTERS, 2, 'Vérifions les résultats, puis entraînons-nous.', narration=narration)
        self.guided_examples('programmation_lineaire')
        a = panel(self.formula(
            r'\begin{gathered}z=3x+2y,\quad(x,y)=(4,3)\\'
            r'0\le x\le4,\quad0\le y\le3,\quad x+y\le5\end{gathered}', 36))
        b = panel(self.formula(r'z=18,\quad x+y=7>5:\quad\text{point non admissible}', 36))
        self.new_page('À vous : tester l’admissibilité', a, b)
        self.explain('Revenons au premier objectif, trois x plus deux y, et aux contraintes du polygone initial. Testez le point quatre, trois : quelle valeur donne-t-il, et respecte-t-il toutes les contraintes affichées ?', a, hold=8, pause_after=6)
        self.explain('L’objectif vaut dix-huit, mais la somme des coordonnées vaut sept. Elle dépasse cinq : le point n’est pas admissible. Une grande valeur ne compense pas une contrainte violée. Vérifiez toujours l’objectif et la région du problème en cours.', b, hold=7)
        play_lesson_closing(
            self, 'Programmation linéaire', ('Vérifier toutes les contraintes.', 'Comparer l’objectif aux sommets admissibles.', 'Une grande valeur ne suffit pas à être admissible.'),
            '\\begin{gathered}z=3x+2y,\\quad(x,y)=(4,3)\\\\0\\le x\\le4,\\quad0\\le y\\le3,\\quad x+y\\le5\\end{gathered}', 'Calculez l’objectif, puis vérifiez chaque contrainte.',
            recap_spoken='Vérifier toutes les contraintes. Comparer l’objectif aux sommets admissibles. Une grande valeur ne suffit pas à être admissible.', practice_spoken='Reprenez le point quatre, trois. Calculez la valeur de l’objectif et vérifiez toutes les contraintes.', narration=narration,
        )

"""S04 — parametric lines and Cartesian planes, with membership checks."""
from manim import (
    BLACK, RIGHT, UP, WHITE, Arrow, Axes, Dot,
    MathTex, Tex, Text, VGroup, config,
)

from tools.teaching_chapters import (
    play_lesson_opening, play_chapter_outline, play_lesson_closing,
)
from tools.expanded_teaching import ExpandedTeachingScene as TeachingScene
from tools import tts

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


def line_value(x, y):
    return x + 2 * y - 5


def plane_value(x, y, z):
    return x + 2 * y - z + 1


LESSON_TITLE = 'Équations de la droite\net du plan'
LESSON_OBJECTIVE = 'Décrire une droite ou un plan,\npuis tester l’appartenance d’un point.'
CHAPTERS = ('Décrire une droite', 'Passer à l’espace', 'Définir et tester un plan', 'S’entraîner et vérifier')


class EquationsDroitePlanFR(TeachingScene):
    def _chapter_narration(self, spoken):
        if self.silent:
            from contextlib import nullcontext
            return nullcontext()
        return self.voiceover(text=tts.ssml(spoken), subcaption=tts.strip_ssml(spoken))

    def _finish_lesson(self):
        play_lesson_closing(
            self, LESSON_TITLE,
            ('Droite : un point et un vecteur directeur non nul.', 'Plan : un point et une normale non nulle.', 'Tester un point en remplaçant ses coordonnées.'),
            '\\Pi:x+2y-z+1=0,\\quad Q=(1,1,4)',
            'Le point Q appartient-il au plan ?\nÉcrivez le calcul qui justifie votre réponse.',
            recap_spoken='Droite : un point et un vecteur directeur non nul. Plan : un point et une normale non nulle. Tester un point en remplaçant ses coordonnées.',
            practice_spoken='Reprenez le plan x plus deux y moins z plus un égal à zéro et le point Q de coordonnées un, un et quatre, dans cet ordre. Remplacez ses coordonnées pour décider s’il appartient au plan.',
            narration=self._chapter_narration,
        )

    def construct(self):
        self.setup_narration()
        play_lesson_opening(self, LESSON_TITLE, LESSON_OBJECTIVE,
                            narration=self._chapter_narration)
        play_chapter_outline(self, CHAPTERS, 0,
                             'Décrire une droite. Un point et une direction décrivent une droite.',
                             narration=self._chapter_narration)
        a = self.panel(self.formula(r'A=(1,2),\qquad\vec v=(2,-1)', 40))
        b = self.panel(self.formula(r'(x,y)=(1,2)+t(2,-1),\qquad t\in\mathbb R', 36))
        self.new_page('Décrire une droite par un déplacement', a, b)
        self.explain('Un point de départ et un vecteur directeur non nul déterminent une droite. Partons du point un, deux, dans la direction deux, moins un.', a, hold=4)
        self.explain('En multipliant ce vecteur par un réel t, puis en l’ajoutant au point de départ, on parcourt toute la droite.', b, hold=4)

        ax = Axes(x_range=[-1, 5, 1], y_range=[-1, 4, 1], x_length=3.6,
                  y_length=3.0, tips=False, axis_config={'color': BLACK})
        graph = ax.plot(lambda x: (5 - x) / 2, x_range=[-1, 5], color=BLACK)
        start, end = ax.c2p(1, 2), ax.c2p(3, 1)
        arrow = Arrow(start, end, buff=0, color=BLACK)
        diagram = VGroup(ax, graph, arrow, Dot(start, color=BLACK), Dot(end, color=BLACK),
                         self.formula('A=(1,2)', 28).next_to(start, UP + RIGHT, buff=0.28),
                         self.formula('B=(3,1)', 28).next_to(end, UP + RIGHT, buff=0.28),
                         ax.get_axis_labels(self.formula('x', 28), self.formula('y', 28)))
        self.new_page('Un pas : deux à droite, un vers le bas', diagram)
        self.explain('Pour t égal à un, on arrive au point trois, un. Les deux axes utilisent la même échelle : la flèche représente fidèlement le déplacement.', diagram, hold=5)

        a = self.panel(self.formula(r'x=1+2t,\quad y=2-t\quad\Longrightarrow\quad x+2y=5', 36))
        b = self.formula(r'B=(3,1):\quad3+2\times1=5', 38)
        self.new_page('Éliminer le paramètre', a, b)
        self.explain('En additionnant x et deux fois y, le paramètre disparaît. On obtient l’équation cartésienne de la même droite.', a, hold=4)
        self.explain('Pour vérifier qu’un point appartient à la droite, on remplace les coordonnées. Le point trois, un satisfait bien l’équation.', b, hold=4)

        play_chapter_outline(self, CHAPTERS, 1,
                             'Passer à l’espace. Étendons la description à trois coordonnées.',
                             narration=self._chapter_narration)

        a = self.panel(self.formula(r'(x,y,z)=(1,0,2)+t(2,1,-1),\quad t\in\mathbb R', 34))
        b = self.words('Une droite dans l’espace : un seul paramètre.')
        self.new_page('Une droite dans l’espace', a, b)
        self.explain('Dans l’espace, une droite se décrit de la même manière, mais avec trois coordonnées. Le vecteur directeur doit toujours être non nul.', a, hold=4)
        self.explain('Un seul paramètre suffit pour parcourir cette droite. Une seule équation cartésienne non triviale dans l’espace décrit plutôt un plan.', b, hold=4)

        play_chapter_outline(self, CHAPTERS, 2,
                             'Définir et tester un plan. Une normale définit le plan et son équation teste les points.',
                             narration=self._chapter_narration)

        a = self.panel(self.formula(r'A=(1,0,2),\quad\vec n=(1,2,-1)', 38))
        b = self.panel(self.formula(r'\vec n\cdot\overrightarrow{AM}=0\quad\Longleftrightarrow\quad x+2y-z+1=0', 34))
        self.new_page('Un plan : un point et une normale', a, b)
        self.explain('Pour décrire un plan, choisissons un point et un vecteur normal non nul. Ce vecteur est perpendiculaire à tous les déplacements dans le plan.', a, hold=4)
        self.explain('Pour un point M de coordonnées x, y, z, on développe le produit scalaire : x moins un, plus deux y, moins z plus deux. Il doit être nul, ce qui donne cette équation.', b, hold=5)

        a = self.panel(self.formula(r'M=(3,0,4):\quad3+2\times0-4+1=0', 36))
        b = self.panel(self.formula(r'N=(3,0,3):\quad3+2\times0-3+1=1\ne0', 36))
        self.new_page('Tester l’appartenance au plan', a, b)
        self.explain('Le point trois, zéro, quatre appartient au plan : ses coordonnées donnent zéro.', a, hold=3)
        self.explain('Le point trois, zéro, trois n’y appartient pas. L’équation est un test d’appartenance, pas seulement une formule à mémoriser.', b, hold=4)

        play_chapter_outline(self, CHAPTERS, 3,
                             'S’entraîner et vérifier. Vérifions les méthodes sur des exemples corrigés.',
                             narration=self._chapter_narration)

        a = self.panel(self.formula(
            r'\begin{gathered}\Pi:x+2y-z+1=0\\'
            r'Q=(1,1,4)\quad\text{appartient-il à }\Pi\text{ ?}\end{gathered}', 36))
        b = self.formula(r'1+2\times1-4+1=0\quad\Longrightarrow\quad\text{oui}', 38)
        self.guided_examples('equations_droite_plan')
        self.new_page('À vous : remplacer les coordonnées', a, b)
        self.explain('Revenons au plan dont le second membre vaut zéro. Testez le point un, un, quatre dans l’équation affichée.', a, hold=8, pause_after=6)
        self.explain('Le résultat est zéro. Ce point appartient donc au plan. Pour une droite comme pour un plan, conservez les coordonnées et les conditions de définition.', b, hold=4)
        self.wait(1)
        self._finish_lesson()

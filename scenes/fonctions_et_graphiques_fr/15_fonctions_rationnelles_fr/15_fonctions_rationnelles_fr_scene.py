"""S02 — rational functions: domain, asymptotes and a removable hole."""
from manim import (
    BLACK, BLUE_D, DOWN, LEFT, RIGHT, WHITE, Axes, Circle, DashedLine,
    MathTex, Tex, Text, VGroup, config,
)

from tools import tts
from tools.teaching_chapters import ACCENT, play_chapter_outline, play_lesson_opening
from tools.expanded_teaching import ExpandedTeachingScene as TeachingScene

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)
BLUE_D = ACCENT  # Pilot only: monochrome teaching graphics.

CHAPTERS = (
    'Domaine et forme utile',
    'Lire les asymptotes',
    'Distinguer trou et asymptote',
    'S’entraîner et vérifier',
)


def rational_value(x):
    if x == 1:
        raise ValueError('The original denominator is zero at x=1.')
    return (x + 1) / (x - 1)


class FonctionsRationnellesAsymptotesFR(TeachingScene):
    teaching_heading_color = ACCENT
    teaching_panel_color = ACCENT

    def chapter_narration(self, spoken):
        return self.voiceover(text=tts.ssml(spoken), subcaption=tts.strip_ssml(spoken))

    def construct(self):
        self.setup_narration()
        narration = None if self.silent else self.chapter_narration
        play_lesson_opening(self, 'Fonctions rationnelles',
                            'Déterminer le domaine et distinguer\nun trou d’une asymptote.',
                            narration=narration)
        play_chapter_outline(self, CHAPTERS, 0,
                             'Commençons par le domaine et une écriture utile de la fonction.',
                             narration=narration)
        a = self.panel(self.formula(r'f(x)=\frac{x+1}{x-1}'))
        b = self.formula(r'D_f=\mathbb{R}\setminus\{1\}', 38)
        self.new_page('Avant le graphe : le domaine', a, b)
        self.explain('Une fonction rationnelle est un quotient de polynômes. Ici, le dénominateur s’annule en un.', a, hold=3)
        self.explain('La fonction est donc définie pour tous les réels sauf un. On vérifie cette condition avant toute simplification.', b, hold=4)

        a = self.panel(self.formula(r'x+1=(x-1)+2'))
        b = self.panel(self.formula(r'f(x)=1+\frac{2}{x-1}\quad(x\ne1)', 40))
        self.new_page('Une écriture qui révèle le graphe', a, b)
        self.explain('Réécrivons le numérateur comme le dénominateur, plus deux.', a, hold=3)
        self.explain('La fonction vaut un, plus deux divisé par x moins un. Cette écriture fait apparaître les deux asymptotes.', b, hold=4)

        play_chapter_outline(self, CHAPTERS, 1, 'Passons maintenant aux asymptotes.',
                             narration=narration)
        ax = Axes(x_range=[-3, 5, 1], y_range=[-3, 5, 1], x_length=3.8,
                  y_length=3.8, tips=False, axis_config={'color': BLACK})
        # Separate domains: never connect samples across the pole.
        left = ax.plot(rational_value, x_range=[-3, 0.5, 0.025], color=BLUE_D)
        right = ax.plot(rational_value, x_range=[1.5, 5, 0.025], color=BLUE_D)
        vertical = DashedLine(ax.c2p(1, -3), ax.c2p(1, 5), color=BLACK)
        horizontal = DashedLine(ax.c2p(-3, 1), ax.c2p(5, 1), color=BLACK)
        x_label = self.formula('1', 28).next_to(ax.c2p(1, -3), DOWN, buff=0.12)
        y_label = self.formula('1', 28).next_to(ax.c2p(-3, 1), LEFT, buff=0.12)
        diagram = VGroup(ax, left, right, vertical, horizontal, x_label, y_label,
                         ax.get_axis_labels(self.formula('x', 28), self.formula('y', 28)))
        self.new_page('Deux asymptotes, deux branches', diagram)
        self.explain('Les pointillés représentent les droites x égale un et y égale un. Le graphe est tracé en deux branches séparées : aucune ligne ne traverse le point où la fonction n’est pas définie.', diagram, hold=6)

        a = self.panel(self.formula(r'\lim_{x\to1^-}f(x)=-\infty,\qquad\lim_{x\to1^+}f(x)=+\infty', 36))
        b = self.panel(self.formula(r'\lim_{x\to-\infty}f(x)=\lim_{x\to+\infty}f(x)=1', 36))
        self.new_page('Ce que signifie « asymptote »', a, b)
        self.explain('Près de un, à gauche, le quotient devient négatif sans borne. À droite, il devient positif sans borne. C’est une asymptote verticale.', a, hold=5)
        self.explain('Quand x devient très grand en valeur absolue, le quotient deux sur x moins un tend vers zéro. La hauteur tend vers un : c’est une asymptote horizontale. Une asymptote horizontale n’est pas, en général, une ligne interdite au graphe.', b, hold=5)

        play_chapter_outline(self, CHAPTERS, 2,
                             'Distinguons maintenant un trou d’une asymptote verticale.',
                             narration=narration)
        a = self.panel(self.formula(r'g(x)=\frac{x^2-1}{x-1}=x+1\quad(x\ne1)', 38))
        b = self.words('La simplification ne rétablit pas la valeur interdite.')
        self.new_page('Trou ou asymptote verticale ?', a, b)
        self.explain('Dans ce nouvel exemple, le facteur x moins un se simplifie. Mais cette égalité reste valable seulement pour x différent de un.', a, hold=4)
        self.explain('La valeur en un manque toujours. Le graphe a un trou, pas une asymptote verticale.', b, hold=4)

        ax = Axes(x_range=[-1, 3, 1], y_range=[-1, 4, 1], x_length=2.8,
                  y_length=3.5, tips=False, axis_config={'color': BLACK})
        graph = ax.plot(lambda x: x + 1, x_range=[-1, 3], color=BLUE_D)
        hole = Circle(radius=0.075, color=BLUE_D, fill_color=WHITE,
                      fill_opacity=1, stroke_width=3).move_to(ax.c2p(1, 2)).set_z_index(3)
        # Keep the coordinate label clear of both the y-axis and the graph.
        label = self.formula('(1,2)', 30).next_to(hole, RIGHT + DOWN, buff=0.25)
        diagram = VGroup(ax, graph, hole, label,
                         ax.get_axis_labels(self.formula('x', 28), self.formula('y', 28)))
        self.new_page('Un point exclu du graphe', diagram)
        self.explain('Le petit cercle vide marque le point de coordonnées un, deux. La droite approche cette hauteur, mais la fonction d’origine n’a pas de valeur en un.', diagram, hold=5)

        play_chapter_outline(self, CHAPTERS, 3,
                             'Entraînons-nous, puis vérifions que le domaine est conservé.',
                             narration=narration)
        a = self.panel(self.formula(r'h(x)=\frac{x-2}{x-2}\quad:\quad h(2)=\ ?'))
        b = self.formula(r'h(x)=1\ (x\ne2),\qquad h(2)\text{ non défini}', 36)
        self.guided_examples('fonctions_rationnelles')
        self.new_page('À vous : conserver le domaine', a, b)
        self.explain('Que devient ce quotient ? Peut-on affirmer que sa valeur en deux est un ?', a, hold=6, pause_after=6)
        self.explain('Le quotient vaut un pour x différent de deux. En deux, il est non défini. Retenez l’ordre : domaine, simplification, puis comportement du graphe.', b, hold=4)
        self.wait(1)

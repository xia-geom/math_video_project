"""S06 — equivalent systems and elimination, with geometric interpretation."""
from manim import BLACK, BLUE_D, RIGHT, WHITE, Axes, Dot, MathTex, Tex, Text, VGroup, config

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


def eliminate_first_row(first, second, factor):
    if len(first) != len(second):
        raise ValueError('Rows must have the same length, including the right-hand side.')
    return tuple(a - factor * b for a, b in zip(first, second))


class EliminationVariablesFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        a = panel(self.formula(r'\begin{cases}2x+y=5\quad(L_1)\\x-y=1\quad(L_2)\end{cases}', 40))
        b = self.words('Transformer le système sans changer ses solutions.')
        self.new_page('Faire disparaître une inconnue', a, b)
        self.explain('Résolvons ce système en éliminant x dans une équation. Les deux équations doivent rester vraies simultanément.', a, hold=3)
        self.explain('Notre but n’est pas de deviner une réponse, mais de remplacer le système par un système équivalent plus simple.', b, hold=4)

        a = panel(self.formula(r'L_1\leftarrow L_1-2L_2'))
        b = self.formula(r'(2x+y)-2(x-y)=5-2\times1', 38)
        c = self.formula(r'3y=3', 42)
        self.new_page('Éliminer x dans la première ligne', a, b, c, gap=0.35)
        self.explain('On remplace la première équation par la première moins deux fois la deuxième. La deuxième équation reste dans le système.', a, hold=4)
        self.explain('On effectue l’opération des deux côtés de l’égalité. Attention au signe : moins deux fois moins y donne plus deux y.', b, hold=4)
        self.explain('Les termes en x s’annulent. Il reste trois y égal à trois.', c, hold=3)

        a = panel(self.formula(r'\begin{cases}3y=3\\x-y=1\end{cases}\quad\Longrightarrow\quad\begin{cases}y=1\\x=2\end{cases}', 38))
        b = self.words('La deuxième équation permet de retrouver x.')
        self.new_page('Remonter vers l’autre inconnue', a, b)
        self.explain('La première équation donne y égal à un. En remplaçant y dans la deuxième, on trouve x égal à deux.', a, hold=4)
        self.explain('Si l’on avait gardé uniquement trois y égal à trois, on aurait perdu la condition sur x. C’est le système complet qui reste équivalent.', b, hold=4)

        ax = Axes(x_range=[0, 4, 1], y_range=[-1, 3, 1], x_length=3.4,
                  y_length=3.4, tips=False, axis_config={'color': BLACK})
        first = ax.plot(lambda x: 5 - 2 * x, x_range=[1, 3], color=BLACK)
        second = ax.plot(lambda x: x - 1, x_range=[0, 4], color=BLUE_D)
        point = Dot(ax.c2p(2, 1), color=BLUE_D)
        # Use the open sector between the lines, not the line above the point.
        label = self.formula('(2,1)', 30).next_to(point, RIGHT, buff=0.35)
        diagram = VGroup(ax, first, second, point, label,
                         ax.get_axis_labels(self.formula('x', 28), self.formula('y', 28)))
        self.new_page('L’intersection des deux droites', diagram)
        self.explain('Chaque équation décrit une droite. Le couple deux, un est leur point d’intersection : il satisfait les deux équations. Les axes ont la même échelle.', diagram, hold=5)

        a = self.words('Échanger deux équations.')
        b = self.words('Multiplier une équation par un nombre non nul.')
        c = self.words('Ajouter un multiple d’une autre équation.')
        self.new_page('Des opérations réversibles', a, b, c)
        self.explain('On peut échanger deux équations : leur ordre ne change pas les solutions.', a, hold=3)
        self.explain('On peut multiplier une équation par un nombre non nul, car l’opération est réversible. Multiplier par zéro ferait perdre de l’information.', b, hold=4)
        self.explain('On peut aussi remplacer une équation par elle-même plus un multiple d’une autre, à condition de conserver cette autre équation. L’opération inverse permet de revenir au système initial.', c, hold=4)

        a = panel(self.formula(r'\begin{cases}x+y=2\\2x+2y=4\end{cases}\ \longrightarrow\ \begin{cases}x+y=2\\0=0\end{cases}', 34))
        b = panel(self.formula(r'\begin{cases}x+y=2\\2x+2y=5\end{cases}\ \longrightarrow\ \begin{cases}x+y=2\\0=1\end{cases}', 34))
        self.new_page('Une ligne nulle ou une contradiction', a, b)
        self.explain('Zéro égal à zéro n’ajoute aucune condition. Dans ce premier système, il reste une droite entière de solutions.', a, hold=4)
        self.explain('Zéro égal à un est impossible. Dans le second système, il n’y a aucune solution. Une ligne nulle et une contradiction ne signifient pas la même chose.', b, hold=4)

        a = panel(self.formula(r'\begin{cases}x+y=7\\x-y=1\end{cases}', 40))
        b = self.formula(r'2x=8,\quad x=4,\quad y=3', 40)
        self.new_page('À vous : additionner les équations', a, b)
        self.explain('Additionnez les deux équations pour éliminer y. Gardez aussi une des équations initiales.', a, hold=6, pause_after=6)
        self.explain('On obtient deux x égal à huit, donc x égal à quatre. La première équation donne ensuite y égal à trois. Vérifiez les deux égalités.', b, hold=4)
        self.wait(1)

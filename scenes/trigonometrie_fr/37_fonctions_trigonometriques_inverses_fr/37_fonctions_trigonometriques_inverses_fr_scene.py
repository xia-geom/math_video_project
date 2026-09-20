"""S10 — principal inverse trigonometric functions and branch restrictions."""
import math

from manim import BLACK, BLUE_D, DOWN, UP, WHITE, Axes, DashedLine, Dot, MathTex, Tex, Text, VGroup, config

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class FonctionsTrigonometriquesInversesFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        a = panel(self.formula(r'\sin\theta=\frac12\quad:\quad\theta=\ ?'))
        b = self.formula(r'\sin\frac\pi6=\sin\frac{5\pi}6=\frac12', 40)
        self.new_page('Un sinus, plusieurs angles', a, b)
        self.explain('Quel angle a pour sinus une moitié ? Nous utilisons désormais les radians.', a, hold=3)
        self.explain('Pi sur six et cinq pi sur six donnent tous deux une moitié. Le sinus sur tous les réels n’est pas injectif : il n’a pas de fonction réciproque globale.', b, hold=4)

        ax = Axes(x_range=[-3.2, 3.2, 1], y_range=[-1.5, 1.5, 1],
                  x_length=6.4, y_length=3, tips=False, axis_config={'color': BLACK})
        full = ax.plot(math.sin, x_range=[-math.pi, math.pi], color=BLACK)
        principal = ax.plot(math.sin, x_range=[-math.pi / 2, math.pi / 2],
                            color=BLUE_D, stroke_width=5)
        first, second = ax.c2p(math.pi / 6, 0.5), ax.c2p(5 * math.pi / 6, 0.5)
        diagram = VGroup(ax, full, principal,
                         DashedLine(ax.c2p(-3.2, 0.5), ax.c2p(3.2, 0.5), color=BLACK),
                         Dot(first, color=BLUE_D), Dot(second, color=BLACK),
                         self.formula(r'\pi/6', 30).next_to(first, DOWN, buff=0.2),
                         self.formula(r'5\pi/6', 30).next_to(second, UP, buff=0.2),
                         ax.get_axis_labels(self.formula(r'\theta', 28), self.formula('y', 28)))
        self.new_page('Choisir une branche injective', diagram)
        self.explain('La branche bleue est la restriction du sinus de moins pi sur deux à pi sur deux. Elle est strictement croissante. La hauteur une moitié y correspond à un seul angle : pi sur six.', diagram, hold=6)

        a = panel(self.formula(r'\arcsin:[-1,1]\longrightarrow[-\pi/2,\pi/2]', 38))
        b = self.formula(r'\arcsin(1/2)=\pi/6', 42)
        self.new_page('Arcsinus : la valeur principale', a, b)
        self.explain('La fonction arcsinus est la réciproque de cette branche. Son entrée doit être comprise entre moins un et un.', a, hold=4)
        self.explain('Sa sortie est l’unique angle de l’intervalle choisi qui possède ce sinus. Ainsi, l’arcsinus d’une moitié vaut pi sur six, pas cinq pi sur six.', b, hold=4)

        a = panel(self.formula(r'\arccos:[-1,1]\longrightarrow[0,\pi]', 40))
        b = panel(self.formula(r'\arctan:\mathbb R\longrightarrow(-\pi/2,\pi/2)', 38))
        self.new_page('Deux autres choix de branche', a, b)
        self.explain('Pour le cosinus, on choisit l’intervalle de zéro à pi, où il est strictement décroissant. Sa réciproque est l’arccosinus.', a, hold=4)
        self.explain('Pour la tangente, on choisit l’intervalle ouvert de moins pi sur deux à pi sur deux. L’arctangente accepte tout réel, mais n’atteint pas les extrémités de cet intervalle.', b, hold=4)

        a = panel(self.formula(r'\sin(\arcsin x)=x\qquad(-1\le x\le1)', 38))
        b = panel(self.formula(r'\arcsin(\sin\theta)=\theta\qquad(-\pi/2\le\theta\le\pi/2)', 34))
        self.new_page('La composition dépend du domaine', a, b)
        self.explain('Le sinus de l’arcsinus de x rend x, lorsque x appartient au domaine de l’arcsinus.', a, hold=4)
        self.explain('Dans l’autre ordre, on retrouve l’angle initial seulement s’il appartient à la branche choisie. Les conditions ne doivent pas disparaître de la formule.', b, hold=4)

        a = panel(self.formula(r'\arcsin\!\left(\sin\frac{5\pi}{6}\right)=\arcsin(1/2)=\frac\pi6', 38))
        b = self.words('La valeur principale peut différer de l’angle initial.')
        self.new_page('Un contre-exemple', a, b)
        self.explain('Cinq pi sur six est en dehors de la branche choisie. Son sinus vaut une moitié, et l’arcsinus renvoie pi sur six.', a, hold=4)
        self.explain('Une fonction réciproque ne doit pas non plus être confondue avec l’inverse multiplicatif : arcsinus n’est pas un sur sinus.', b, hold=4)

        a = panel(self.formula(r'\arccos(-1/2)=\ ?\qquad\arcsin(2)=\ ?', 38))
        b = self.formula(r'\arccos(-1/2)=2\pi/3;\quad\arcsin(2)\text{ non défini dans }\mathbb R', 32)
        self.new_page('À vous : contrôler entrée et sortie', a, b)
        self.explain('Cherchez la valeur principale de l’arccosinus de moins une moitié. Puis demandez-vous si l’arcsinus de deux existe comme nombre réel.', a, hold=6)
        self.explain('La première réponse est deux pi sur trois, qui appartient à l’intervalle de zéro à pi. La seconde expression n’est pas définie dans les réels, car deux est hors du domaine.', b, hold=4)
        self.wait(1)

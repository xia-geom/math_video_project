"""A principal inverse-trigonometric value is not a complete solution set."""

import math

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Axes,
    Circle,
    Create,
    DashedLine,
    Dot,
    Line,
    MathTex,
    Tex,
    Text,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class SolutionsTrigonometriquesCompletesFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._shortcut()
        self._two_angles()
        self._complete_families()
        self._interval_filter()
        self._graph_check()
        self._self_check()
        self._self_check_answer()
        self._takeaway()
        self.wait(1.2)

    def _shortcut(self):
        equation = self.formula(r"\sin(2x)=\frac{\sqrt3}{2},\qquad x\in[0,2\pi]", 47)
        principal = self.formula(r"\arcsin\left(\frac{\sqrt3}{2}\right)=\frac\pi3", 46)
        proposed = self.formula(r"x=\frac\pi6\quad\text{seulement ?}", 45, BLUE_D)
        self.new_page("Une bonne valeur, mais une seule", equation, principal, proposed, gap=0.55)
        self.explain(
            "Nous cherchons toutes les solutions, en radians, entre zéro et deux pi. "
            "La calculatrice donne pi sur trois pour l'arcsinus de racine de trois sur deux. "
            "En divisant par deux, nous obtenons pi sur six.",
            equation, principal,
        )
        self.explain(
            "Cette valeur est correcte. Mais est-elle la seule ? L'arcsinus renvoie "
            "un angle dans son intervalle principal. Il ne parcourt pas automatiquement "
            "tous les angles ayant le même sinus.",
            proposed,
        )

    def _two_angles(self):
        radius = 1.55
        circle = Circle(radius=radius, color=BLACK, stroke_width=2)
        horizontal = Line(LEFT * 1.9, RIGHT * 1.9, color=BLACK, stroke_width=2)
        vertical = Line(DOWN * 1.8, UP * 1.8, color=BLACK, stroke_width=2)
        first = radius * math.cos(math.pi / 3) * RIGHT + radius * math.sin(math.pi / 3) * UP
        second = -first[0] * RIGHT + first[1] * UP
        level = DashedLine(LEFT * 1.8 + UP * first[1], RIGHT * 1.8 + UP * first[1], color=BLUE_D)
        dots = VGroup(Dot(first, color=BLUE_D), Dot(second, color=BLUE_D))
        rays = VGroup(Line([0, 0, 0], first, color=BLUE_D), Line([0, 0, 0], second, color=BLUE_D))
        labels = VGroup(
            self.formula(r"\pi/3", 28).next_to(dots[0], UP + RIGHT, buff=0.17),
            self.formula(r"2\pi/3", 28).next_to(dots[1], UP + LEFT, buff=0.17),
        )
        diagram = VGroup(circle, horizontal, vertical, level, dots, rays, labels)
        equation = self.formula(r"\sin\frac\pi3=\sin\frac{2\pi}{3}=\frac{\sqrt3}{2}", 42)
        layout = VGroup(diagram, equation).arrange(RIGHT, buff=0.8)
        self.new_page("Une même ordonnée, deux angles", layout)
        self.explain(
            "Sur le cercle unité, le sinus est l'ordonnée. La droite horizontale "
            "d'ordonnée racine de trois sur deux rencontre le cercle en deux points. "
            "Ils correspondent à pi sur trois et deux pi sur trois.",
            circle, horizontal, vertical, level,
        )
        self.play(Create(rays), run_time=1.0)
        self.explain(
            "Les deux points sont symétriques par rapport à l'axe vertical. "
            "Les angles sont différents, mais leurs sinus sont égaux. "
            "Un tour complet supplémentaire ne change pas cette ordonnée.",
            dots, labels, equation,
        )

    def _complete_families(self):
        substitution = self.formula(r"u=2x:\qquad\sin u=\frac{\sqrt3}{2}", 44)
        angles = self.formula(r"u=\frac\pi3+2k\pi\quad\text{ou}\quad u=\frac{2\pi}{3}+2k\pi", 41)
        integers = self.formula(r"k\in\mathbb Z", 36)
        solutions = panel(self.formula(r"x=\frac\pi6+k\pi\quad\text{ou}\quad x=\frac\pi3+k\pi", 42), width=10.8)
        self.new_page("Deux familles, puis la division", substitution, angles, integers, solutions, gap=0.35)
        self.explain(
            "Appelons u l'angle deux x. Les deux positions sur le cercle, "
            "auxquelles on ajoute un nombre entier de tours, donnent toutes "
            "les possibilités pour u. L'entier k peut être positif, nul ou négatif.",
            substitution, angles, integers,
        )
        self.explain(
            "Nous divisons ensuite toute l'expression par deux. Le terme deux k pi "
            "devient k pi. Les solutions pour x forment donc deux familles, "
            "et non seulement la valeur principale divisée par deux.",
            solutions,
        )

    def _interval_filter(self):
        domain = self.formula(r"0\le x\le2\pi\quad\Longrightarrow\quad0\le u\le4\pi", 40)
        allowed = self.formula(r"\text{Dans chaque famille : }k=0\text{ ou }k=1", 39)
        solution = self.formula(r"S=\left\{\frac\pi6,\frac\pi3,\frac{7\pi}{6},\frac{4\pi}{3}\right\}", 49, BLUE_D)
        endpoints = self.formula(r"\sin(2\cdot0)=\sin(2\cdot2\pi)=0\ne\frac{\sqrt3}{2}", 37)
        self.new_page("Filtrer avec l'intervalle demandé", domain, allowed, solution, endpoints, gap=0.45)
        self.explain(
            "Lorsque x parcourt zéro à deux pi, l'angle u parcourt zéro à quatre pi : "
            "cela représente deux tours. Dans chacune des familles, k égal à zéro "
            "et à un donne une solution dans l'intervalle.",
            domain, allowed,
        )
        self.explain(
            "Un entier négatif donne ici un x négatif. Un entier au moins égal "
            "à deux donne un x strictement supérieur à deux pi. La liste comporte "
            "donc exactement quatre valeurs. Les deux extrémités sont autorisées "
            "par l'intervalle, mais ne satisfont pas cette équation.",
            solution, endpoints,
        )

    def _graph_check(self):
        axes = Axes(
            x_range=[0, 2 * math.pi, math.pi / 2], y_range=[-1.15, 1.25, 0.5],
            x_length=9.1, y_length=2.85,
            axis_config={"color": BLACK, "include_tip": False},
        )
        curve = axes.plot(lambda x: math.sin(2 * x), x_range=[0, 2 * math.pi], color=BLUE_D)
        level = DashedLine(axes.c2p(0, math.sqrt(3) / 2), axes.c2p(2 * math.pi, math.sqrt(3) / 2), color=BLACK)
        positions = [math.pi / 6, math.pi / 3, 7 * math.pi / 6, 4 * math.pi / 3]
        dots = VGroup(*[Dot(axes.c2p(x, math.sqrt(3) / 2), radius=0.065, color=BLUE_D) for x in positions])
        labels = VGroup(
            self.formula("0", 28).next_to(axes.c2p(0, 0), DOWN + RIGHT, buff=0.15),
            self.formula(r"\pi", 28).next_to(axes.c2p(math.pi, 0), DOWN + RIGHT, buff=0.15),
            self.formula(r"2\pi", 28).next_to(axes.c2p(2 * math.pi, 0), DOWN + RIGHT, buff=0.15),
        )
        graph = VGroup(axes, curve, level, dots, labels)
        caption = self.words("Deux intersections par période ; deux périodes ici.", 29)
        self.new_page("Contrôler les quatre intersections", graph, caption, gap=0.55)
        self.explain(
            "Le graphe de sinus de deux x montre deux oscillations sur notre "
            "intervalle. La ligne horizontale coupe chacune d'elles deux fois.",
            axes, curve, level, labels,
        )
        self.explain(
            "Les quatre points retrouvés graphiquement correspondent à notre "
            "liste. Le dessin contrôle le résultat ; les deux familles et "
            "le filtrage des entiers expliquent pourquoi aucune solution ne manque.",
            dots, caption,
        )

    def _self_check(self):
        equation = self.formula(r"\cos(2x)=1,\qquad x\in[0,2\pi]", 51)
        question = self.words("Lister toutes les solutions, extrémités comprises.", 29)
        self.new_page("À vous : les extrémités comptent", equation, question, gap=0.8)
        self.explain(
            "À vous. Cherchez toutes les valeurs de x entre zéro et deux pi "
            "pour lesquelles cosinus de deux x vaut un. L'intervalle est fermé "
            "aux deux bouts. N'oubliez pas de tester les extrémités.",
            equation, question, pause_after=6,
        )

    def _self_check_answer(self):
        family = self.formula(r"\cos u=1\quad\Longleftrightarrow\quad u=2k\pi,\quad k\in\mathbb Z", 40)
        filtered = self.formula(r"x=k\pi,\qquad0\le k\le2", 45)
        answer = self.formula(r"S=\{0,\pi,2\pi\}", 55, BLUE_D)
        note = self.words("Même point du cercle ; trois valeurs distinctes de x.", 28)
        self.new_page("Un tour, puis encore un tour", family, filtered, answer, note, gap=0.5)
        self.explain(
            "Le cosinus vaut un aux angles multiples entiers de deux pi. "
            "Comme u vaut deux x, les solutions sont les multiples entiers de pi. "
            "L'intervalle demandé garde les entiers zéro, un et deux.",
            family, filtered,
        )
        self.explain(
            "La réponse contient zéro, pi et deux pi. Ces trois valeurs de x "
            "donnent la même position finale sur le cercle de l'angle deux x, "
            "mais ce sont trois nombres distincts dans l'intervalle. "
            "On conserve donc les deux extrémités.",
            answer, note,
        )

    def _takeaway(self):
        method = self.words("Angle principal, symétries, tours, puis intervalle.", 29, BLUE_D)
        source = self.words("Manuel 16.3–16.4, 16.7 · Cahier 16.3 B, 16.4", 28)
        self.new_page("La liste doit être complète", method, source, gap=0.85)
        self.explain(
            "La calculatrice fournit un point de départ. Pour obtenir toutes "
            "les solutions, ajoutez les symétries, la périodicité et le contrôle "
            "de l'intervalle. Vérifiez enfin séparément les extrémités.",
            method, source,
        )

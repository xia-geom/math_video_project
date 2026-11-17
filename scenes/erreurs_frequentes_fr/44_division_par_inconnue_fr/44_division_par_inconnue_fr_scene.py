"""A division by an unknown can erase a solution: retain the zero case."""
from manim import (
    BLACK,
    DOWN,
    LEFT,
    RIGHT,
    WHITE,
    Axes,
    Circle,
    Create,
    DashedVMobject,
    Dot,
    Indicate,
    MathTex,
    Tex,
    Text,
    VGroup,
    config,
)

from tools.teaching_chapters import (
    play_chapter_outline,
    play_lesson_closing,
    play_lesson_opening,
)
from tools.teaching_layout import TeachingScene, panel

LESSON_TITLE = 'Diviser par une inconnue'
LESSON_OBJECTIVE = 'Simplifier une équation\nsans perdre de solution.'
CHAPTERS = (
    'Repérer la solution perdue',
    'Résoudre sans diviser par zéro',
    'Vérifier toutes les solutions',
)

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class DivisionParInconnueFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        narration = None if self.silent else self.chapter_narration
        play_lesson_opening(
            self, LESSON_TITLE, LESSON_OBJECTIVE, narration=narration,
        )
        play_chapter_outline(
            self, CHAPTERS, 0, 'Cherchons la solution que la division a supprimée.',
            narration=narration,
        )
        self._tempting_division()
        self._missing_zero()
        self._two_intersections()
        play_chapter_outline(
            self, CHAPTERS, 1, 'Retrouvons toutes les solutions avec une méthode justifiée.',
            narration=narration,
        )
        self._factor_instead()
        self._legitimate_division()
        play_chapter_outline(
            self, CHAPTERS, 2, 'Appliquons ces contrôles à une nouvelle équation.',
            narration=narration,
        )
        self._self_check()
        self._self_check_answer()
        self._closing(narration=narration)

    def _tempting_division(self):
        equation = self.formula(r"x^2=3x", 58)
        division = self.formula(r"\frac{x^2}{x}=\frac{3x}{x}", 50, BLACK)
        result = self.formula(r"x=3\quad\text{seulement ?}", 46)
        self.new_page("Peut-on diviser par l’inconnue ?", equation, division, result)
        self.explain(
            "Résolvons cette équation. Une idée tentante consiste à diviser les "
            "deux membres par x. Les facteurs disparaissent, et il reste x égal "
            "à trois. Le calcul est rapide. Mais avons-nous trouvé toutes les solutions ?",
            equation, division,
        )
        self.explain(
            "Le mot seulement est précisément ce qu’il faut vérifier. Une opération "
            "qui simplifie l’écriture peut aussi supprimer une valeur autorisée.",
            result,
        )

    def _missing_zero(self):
        test = self.formula(r"x=0", 54, BLACK)
        substitution = self.formula(r"0^2=3\cdot0\qquad\Longleftrightarrow\qquad0=0", 44)
        forbidden = self.formula(r"\frac00\quad\text{n’est pas défini}", 42, BLACK)
        self.new_page("La solution oubliée", test, substitution, forbidden)
        self.explain(
            "Essayons zéro dans l’équation de départ. Son carré vaut zéro, et "
            "trois fois zéro vaut aussi zéro. Zéro est donc bien une solution.",
            test, substitution,
        )
        self.explain(
            "En divisant par x, nous avons interdit ce cas sans le dire. "
            "À zéro, cette division demanderait de calculer zéro divisé par zéro, "
            "ce qui n’est pas défini. Voilà où la solution a disparu.",
            forbidden,
        )

    def _two_intersections(self):
        axes = Axes(
            x_range=[-0.5, 3.5, 1], y_range=[-1, 10, 2],
            x_length=6.2, y_length=3.6,
            axis_config={"color": BLACK, "include_tip": True, "stroke_width": 2},
        )
        labels = axes.get_axis_labels(
            self.formula("x", 28), self.formula("y", 28),
        )
        parabola = axes.plot(lambda x: x * x, x_range=[-0.5, 3.15], color=BLACK)
        line = DashedVMobject(
            axes.plot(lambda x: 3 * x, x_range=[-0.3, 3.25], color=BLACK),
            num_dashes=28,
        )
        zero = Dot(axes.c2p(0, 0), radius=0.085, color=BLACK)
        three = Dot(axes.c2p(3, 9), radius=0.085, color=BLACK)
        zero_label = self.formula(r"(0,0)", 28).next_to(zero, DOWN + LEFT, buff=0.15)
        three_label = self.formula(r"(3,9)", 28).next_to(three, LEFT, buff=0.15)
        plot = VGroup(axes, labels, parabola, line, zero, three, zero_label, three_label)
        legend = VGroup(
            self.formula(r"y=x^2", 40),
            VGroup(
                self.formula(r"y=3x", 40),
                self.words("pointillés", 28),
            ).arrange(DOWN, buff=0.12),
            self.formula(r"x\in\{0,3\}", 40, BLACK),
        ).arrange(DOWN, buff=0.65)
        diagram = VGroup(plot, legend).arrange(RIGHT, buff=0.65)
        self.new_page("Voir les deux solutions", diagram)
        self.explain(
            "On peut voir le problème sur un graphe. Nous comparons la parabole "
            "du carré et la droite en pointillés correspondant à trois fois x. Résoudre l’équation, "
            "c’est chercher leurs points d’intersection.",
            axes, labels, legend[0], legend[1],
        )
        self.play(Create(parabola), Create(line), run_time=1.7)
        self.explain(
            "Les courbes se rencontrent à l’origine, puis au point de coordonnées "
            "trois et neuf. Les abscisses des intersections donnent les deux solutions : zéro et trois.",
            zero, three, zero_label, three_label, legend[2],
        )
        ring = Circle(radius=0.19, color=BLACK, stroke_width=3).move_to(zero)
        self.page.add(ring)
        self.play(Create(ring), Indicate(zero, color=BLACK), run_time=1.0)

    def _factor_instead(self):
        start = self.formula(r"x^2-3x=0", 48)
        factored = panel(self.formula(r"x(x-3)=0", 54, BLACK), width=8, height=1.2)
        alternatives = self.formula(r"x=0\quad\text{ou}\quad x-3=0", 42)
        solution = self.formula(r"S=\{0,3\}", 50, BLACK)
        self.new_page("Factoriser conserve les deux cas", start, factored, alternatives, solution, gap=0.32)
        self.explain(
            "Pour conserver les deux possibilités, ramenons tout du même côté. "
            "On met x en facteur, sans diviser par x. Cette identité est valable "
            "pour chaque réel, y compris zéro.",
            start, factored,
        )
        self.explain(
            "Un produit de deux nombres réels est nul si au moins un facteur est "
            "nul. Le premier facteur donne zéro, et le second donne trois. "
            "La factorisation retrouve exactement ce que montrait le graphe.",
            alternatives, solution,
        )

    def _legitimate_division(self):
        zero_case = panel(
            VGroup(self.formula(r"x=0", 42), self.words("Vérifier ce cas.", 29))
            .arrange(DOWN, buff=0.30),
            width=5.3, height=1.65,
        )
        other_case = panel(
            VGroup(self.formula(r"x\ne0", 42), self.words("Diviser devient permis.", 28))
            .arrange(DOWN, buff=0.30),
            width=5.3, height=1.65,
        )
        cases = VGroup(zero_case, other_case).arrange(RIGHT, buff=0.5)
        reminder = self.words("Séparer les cas avant de diviser.", 31, BLACK)
        self.new_page("La division reste possible", cases, reminder, gap=0.70)
        self.explain(
            "Diviser par une inconnue n’est pas toujours interdit. Il faut d’abord "
            "traiter le cas où elle est nulle. Pour les autres valeurs, la division "
            "est légitime. On rassemble ensuite les solutions des deux cas.",
            cases, reminder,
        )

    def _self_check(self):
        equation = self.formula(r"(x-2)(x+1)=4(x-2)", 46)
        question = self.words("Quelles sont toutes les solutions ?", 31)
        hint = self.words("Que se passe-t-il quand le facteur commun est nul ?", 28, BLACK)
        self.new_page("À vous de vérifier", equation, question, hint, gap=0.65)
        self.explain(
            "À vous. Résolvez cette nouvelle équation. Avant de diviser par le "
            "facteur x moins deux, demandez-vous ce qui se passe lorsque ce facteur "
            "est nul. Cherchez toutes les solutions.",
            equation, question, hint, pause_after=6,
        )

    def _self_check_answer(self):
        difference = self.formula(r"(x-2)(x+1)-4(x-2)=0", 43)
        factor = self.formula(r"(x-2)(x-3)=0", 50, BLACK)
        answer = self.formula(r"S=\{2,3\}", 52, BLACK)
        check = self.formula(r"x=2:\ 0=0\qquad x=3:\ 4=4", 38)
        self.new_page("Deux solutions, encore", difference, factor, answer, check, gap=0.38)
        self.explain(
            "On soustrait le membre de droite et on met le facteur commun en "
            "évidence. Il reste x moins deux, multiplié par x moins trois. "
            "Les solutions sont donc deux et trois.",
            difference, factor, answer,
        )
        self.explain(
            "La substitution confirme les deux réponses. Diviser immédiatement "
            "par x moins deux aurait fait disparaître la solution deux.",
            check,
        )

    def _closing(self, *, narration=None):
        # MAT0339 : manuel 2.6–2.8 ; cahier 2.6A, adaptation.
        play_lesson_closing(
            self, LESSON_TITLE,
            (
                'Vérifier si le diviseur peut être nul.',
                'Factoriser ou séparer les cas.',
                'Contrôler les solutions dans l’équation initiale.',
            ),
            'x^2=3x',
            'Retrouvez toutes les solutions.',
            recap_spoken='Vérifier si le diviseur peut être nul. Factoriser ou séparer les cas. Contrôler les solutions dans l’équation initiale.',
            practice_spoken='Résolvez de nouveau x au carré égal trois fois x. Cherchez toutes les solutions, y compris le cas où x est nul.',
            narration=narration,
        )

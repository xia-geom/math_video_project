"""MAT0339, manuel 8.4 et cahier 8.4 B : incompatibilité et indépendance."""
from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GRAY_B,
    RED_D,
    RIGHT,
    WHITE,
    MathTex,
    Square,
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


class IndependanceIncompatibiliteFR(TeachingScene):
    """Tester deux propriétés différentes, sans les déduire du vocabulaire."""

    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._one_die()
        self._definitions()
        self._two_dice()
        self._self_check()
        self._takeaway()
        self.wait(1.2)

    def _die_row(self):
        cells = VGroup()
        for value in range(1, 7):
            box = Square(side_length=0.75, stroke_color=BLACK, stroke_width=2)
            value_label = self.formula(str(value), 36).move_to(box)
            cells.add(VGroup(box, value_label))
        return cells.arrange(RIGHT, buff=0.24)

    def _question(self):
        temptation = self.words('« Ils ne peuvent pas arriver ensemble,', 31)
        ending = self.words('donc ils sont indépendants. »', 31, RED_D)
        question = self.words('Est-ce vraiment ce que signifie indépendant ?', 30)
        self.new_page('Deux mots, deux questions', temptation, ending, question)
        self.explain(
            'Deux événements ne peuvent pas se produire ensemble. Peut-on en conclure qu’ils sont indépendants ? Cette phrase paraît plausible dans la langue courante, mais elle confond deux propriétés mathématiques différentes.',
            temptation, ending, hold=2,
        )
        self.explain(
            'Incompatible décrit la possibilité d’arriver ensemble. Indépendant décrit l’effet d’une information sur une probabilité. Nous allons tester ces deux idées sur un dé, puis sur deux dés.',
            question, hold=2,
        )

    def _one_die(self):
        row = self._die_row()
        events = self.formula(r'A=\{2,4,6\},\qquad B=\{1,3,5\}', 39)
        intersection = self.formula(r'A\cap B=\varnothing,\qquad P(A\cap B)=0', 40)
        product = self.formula(r'P(A)P(B)=\frac12\times\frac12=\frac14\ne0', 40, RED_D)
        self.new_page('Pair et impair sur un même dé', row, events, intersection, product, gap=0.38)
        self.explain(
            'Lançons un dé équilibré. A signifie obtenir un nombre pair, et B obtenir un nombre impair. Chacun regroupe trois issues parmi six, donc chacun a une probabilité d’une moitié.',
            row, events, hold=2,
        )
        self.play(*[
            row[i][0].animate.set_fill(BLUE_D, opacity=0.15)
            for i in (1, 3, 5)
        ], run_time=0.9)
        self.explain(
            'Aucun numéro n’est à la fois pair et impair. L’intersection est vide : les deux événements sont incompatibles, et la probabilité qu’ils arrivent ensemble vaut zéro.',
            intersection, hold=2,
        )
        self.explain(
            'Pour l’indépendance, comparons avec le produit des probabilités. Une moitié fois une moitié vaut un quart, pas zéro. Ces deux événements ne sont donc pas indépendants.',
            product, hold=2,
        )
        conditioned = panel(self.formula(r'P(B\mid A)=0\ne\frac12=P(B)', 45), width=9)
        note = self.words('Savoir « pair » exclut complètement « impair ».', 30)
        self.new_page('Une information qui change tout', conditioned, note)
        self.explain(
            'Le conditionnement explique le résultat. Avant toute information, la probabilité d’un résultat impair vaut une moitié. Si l’on apprend que le résultat est pair, cette probabilité devient zéro. L’information a donc complètement changé la réponse.',
            conditioned, note, hold=2,
        )

    def _definitions(self):
        incompatible = self.formula(r'\text{Incompatibles : }A\cap B=\varnothing', 40)
        independent = self.formula(r'\text{Indépendants : }P(A\cap B)=P(A)P(B)', 39)
        consequence = self.formula(r'P(A)>0,\ P(B)>0\quad\Longrightarrow\quad P(A)P(B)>0', 36)
        note = self.words('La précision « probabilités positives » est nécessaire.', 28)
        self.new_page('Comparer les bons critères', incompatible, independent, consequence, note, gap=0.40)
        self.explain(
            'Retenons les critères exacts. Pour l’incompatibilité, nous regardons l’intersection des événements. Pour l’indépendance, nous comparons sa probabilité au produit des deux probabilités.',
            incompatible, independent, hold=2,
        )
        self.explain(
            'Si les probabilités des deux événements sont strictement positives, leur produit est strictement positif. Il ne peut pas être égal à zéro. Deux événements incompatibles de probabilités positives ne sont donc jamais indépendants.',
            consequence, hold=2,
        )
        self.explain(
            'Gardons la précision sur les probabilités positives. L’événement impossible a une probabilité nulle : il est incompatible avec tout événement et indépendant de tout événement. Sans cette précision, notre conclusion serait fausse.',
            note, hold=2,
        )

    def _two_dice(self):
        # Equal-size squares display all 36 equiprobable ordered outcomes.
        grid = VGroup(*[
            Square(side_length=0.34, stroke_color=GRAY_B, stroke_width=1.4)
            for _ in range(36)
        ]).arrange_in_grid(rows=6, cols=6, buff=0.055)
        first_labels = VGroup(*[
            self.formula(str(i + 1), 22).next_to(grid[i], DOWN, buff=0.12)
            for i in range(6)
        ])
        # Put column labels below the bottom row, not inside the outcome grid.
        for i, label in enumerate(first_labels):
            label.next_to(grid[30 + i], DOWN, buff=0.12)
        second_labels = VGroup(*[
            self.formula(str(i + 1), 22).next_to(grid[6 * i], direction=-RIGHT, buff=0.12)
            for i in range(6)
        ])
        axis_label = self.words('premier dé', 26).next_to(first_labels, DOWN, buff=0.14)
        diagram = VGroup(grid, first_labels, second_labels, axis_label)
        legend = VGroup(
            self.words('C : premier dé pair', 28),
            self.words('D : second dé pair', 28),
            self.formula(r'P(C)=P(D)=\frac12', 35),
            self.formula(r'P(C\cap D)=\frac9{36}=\frac14', 35),
        ).arrange(DOWN, buff=0.45)
        row = VGroup(diagram, legend).arrange(RIGHT, buff=1.0)
        self.new_page('Ils peuvent arriver ensemble', row)
        self.explain(
            'Prenons maintenant deux dés équilibrés lancés indépendamment. Le tableau représente les trente-six couples équiprobables. Les colonnes donnent le premier dé, les lignes le second. C signifie premier dé pair ; D signifie second dé pair.',
            diagram, legend[0], legend[1], hold=2,
        )
        self.play(*[
            grid[6 * r + c].animate.set_fill(BLUE_D, opacity=0.18)
            for r in range(6) for c in (1, 3, 5)
        ], run_time=0.9)
        self.explain(
            'Trois colonnes sur six correspondent à C. Pour D, ce sont trois lignes sur six. Chacun de ces événements a une probabilité d’une moitié.',
            legend[2], hold=2,
        )
        self.play(*[
            grid[6 * r + c].animate.set_fill(
                BLUE_D, opacity=0.65 if c in (1, 3, 5) else 0.18,
            )
            for r in (1, 3, 5) for c in range(6)
        ], run_time=0.9)
        self.explain(
            'Les neuf cases plus foncées sont dans les trois colonnes et les trois lignes sélectionnées. Neuf sur trente-six vaut un quart, exactement le produit des probabilités. C et D sont indépendants, mais leur intersection n’est pas vide.',
            legend[3], hold=2,
        )

    def _self_check(self):
        data = self.formula(r'A=\{2,4,6\},\qquad E=\{4,5,6\}', 42)
        question = self.words('Sur un dé équilibré : incompatibles ? indépendants ?', 29)
        self.new_page('À vous : appliquer les deux critères', data, question)
        self.explain(
            'Revenons à un seul dé équilibré. A signifie pair, et E signifie strictement supérieur à trois. Ces événements sont-ils incompatibles ? Sont-ils indépendants ? Calculez séparément les deux critères.',
            data, question, hold=2, pause_after=6,
        )
        intersection = self.formula(r'A\cap E=\{4,6\}\ne\varnothing', 43)
        calculation = self.formula(r'P(A\cap E)=\frac26=\frac13\ne\frac14=P(A)P(E)', 37)
        verdict = self.words('Ni incompatibles, ni indépendants.', 32, BLUE_D)
        self.new_page('Réponse : aucune des deux propriétés', intersection, calculation, verdict)
        self.explain(
            'L’intersection contient quatre et six : les événements sont compatibles. Sa probabilité vaut un tiers, tandis que le produit vaut un quart. Ils ne sont pas indépendants non plus. Les deux mots ne sont donc pas deux possibilités opposées qui épuiseraient tous les cas.',
            intersection, calculation, verdict, hold=2,
        )

    def _takeaway(self):
        distinction = VGroup(
            self.words('Incompatibles : peuvent-ils arriver ensemble ?', 30),
            self.words('Indépendants : vérifier l’égalité des probabilités.', 29),
        ).arrange(DOWN, buff=0.45)
        source = self.words('Manuel 8.4 · Cahier 8.4 B', 28)
        self.new_page('Deux critères à vérifier', distinction, source)
        self.explain(
            'Vérifiez l’intersection pour l’incompatibilité, puis l’égalité des probabilités pour l’indépendance. La deuxième question de la section huit point quatre du cahier vous demande précisément de justifier cette distinction.',
            distinction, source, hold=2,
        )

"""A zero determinant does not decide whether a linear system is consistent."""

from manim import (
    BLACK,
    BLUE_D,
    RIGHT,
    UP,
    WHITE,
    Axes,
    Dot,
    FadeOut,
    MathTex,
    Tex,
    Text,
    Transform,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class DeterminantNulCompatibiliteFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._keep_rhs()
        self._two_geometries()
        self._parameterize()
        self._zero_row()
        self._cramer_boundary()
        self._self_check()
        self._self_check_answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        system = self.formula(r"\begin{cases}2x+3y=1,\\4x+6y=5.\end{cases}", 49)
        determinant = self.formula(r"D=\begin{vmatrix}2&3\\4&6\end{vmatrix}=12-12=0", 44)
        claim = self.words("Déterminant nul : forcément une infinité de solutions ?", 28)
        self.new_page("Que dit vraiment le déterminant ?", system, determinant, claim, gap=0.5)
        self.explain(
            "Dans ce système du cahier, le déterminant des coefficients vaut zéro. "
            "On pourrait alors conclure trop vite qu'il existe une infinité "
            "de solutions. Mais le déterminant n'utilise pas les nombres "
            "un et cinq placés à droite des égalités.",
            system, determinant,
        )
        self.explain(
            "Or ces seconds membres peuvent rendre les deux équations "
            "compatibles ou contradictoires. Calculons ce qui reste "
            "lorsque nous éliminons les inconnues.",
            claim,
        )

    def _keep_rhs(self):
        system = self.formula(r"\begin{cases}2x+3y=1,\\4x+6y=k.\end{cases}", 45)
        operation = self.formula(r"E_2-2E_1:\qquad0=k-2", 45, BLUE_D)
        particular = self.formula(r"k=5:\quad0=3\text{ est impossible}", 41)
        compatible = self.formula(r"k=2:\quad0=0\text{ ne crée pas de contradiction}", 37)
        self.new_page("Éliminer aussi les seconds membres", system, operation, particular, compatible, gap=0.42)
        self.explain(
            "Remplaçons le second membre cinq par un paramètre k. "
            "Le déterminant reste nul, quelle que soit sa valeur. "
            "Retirons deux fois la première équation de la seconde : "
            "les coefficients s'annulent, et il reste zéro égal à k moins deux.",
            system, operation,
        )
        self.explain(
            "Pour k égal à cinq, cela exige zéro égal à trois : aucune solution. "
            "Pour k égal à deux, cela donne zéro égal à zéro : aucune "
            "contradiction. La première équation, elle, reste à satisfaire.",
            particular, compatible,
        )

    def _two_geometries(self):
        # Equal units on both axes: slope and coincidence have their geometric meaning.
        axes = Axes(
            x_range=[-1, 2.5, 0.5], y_range=[-1.25, 1.25, 0.5],
            x_length=4.55, y_length=3.25,
            axis_config={"color": BLACK, "include_tip": False},
        )
        first = axes.plot(lambda x: (1 - 2 * x) / 3, x_range=[-0.5, 2], color=BLACK, stroke_width=5)
        second = axes.plot(lambda x: (5 - 4 * x) / 6, x_range=[-0.5, 2], color=BLUE_D, stroke_width=3)
        labels = VGroup(
            self.formula("x", 27).next_to(axes.x_axis, RIGHT, buff=0.15),
            self.formula("y", 27).next_to(axes.y_axis, UP, buff=0.15),
        )
        graph = VGroup(axes, first, second, labels)
        caption = self.formula(r"k=5:\quad\text{deux droites parallèles distinctes}", 36)
        self.new_page("Les droites peuvent se confondre", graph, caption, gap=0.45)
        self.explain(
            "La première équation est représentée en noir, la seconde en bleu. "
            "Avec k égal à cinq, les droites ont la même pente et des ordonnées "
            "à l'origine différentes. Elles ne se rencontrent jamais.",
            graph, caption,
        )
        coincident = axes.plot(lambda x: (2 - 4 * x) / 6, x_range=[-0.5, 2], color=BLUE_D, stroke_width=3)
        next_caption = self.formula(r"k=2:\quad\text{deux écritures d'une même droite}", 36).move_to(caption)
        self.page.add(next_caption)
        self.play(FadeOut(caption), run_time=0.35)
        self.page[1].remove(caption)
        self.play(Transform(second, coincident), run_time=1.8)
        points = VGroup(*[
            Dot(axes.c2p(x, (1 - 2 * x) / 3), radius=0.07, color=BLUE_D)
            for x in [-0.25, 0.5, 1.25]
        ])
        self.page.add(points)
        self.explain(
            "En ramenant k à deux, la droite bleue rejoint exactement la noire. "
            "Chaque point de cette droite satisfait désormais les deux équations. "
            "Il y a une infinité de points communs, mais le déterminant n'a pas changé.",
            next_caption, points,
        )

    def _parameterize(self):
        remaining = self.formula(r"k=2:\qquad2x+3y=1", 48)
        parameter = self.formula(r"x=t\quad\Longrightarrow\quad y=\frac{1-2t}{3}", 45)
        solution = panel(self.formula(r"S=\left\{\left(t,\frac{1-2t}{3}\right):t\in\mathbb R\right\}", 45), width=9)
        self.new_page("Décrire l'infinité de solutions", remaining, parameter, solution, gap=0.45)
        self.explain(
            "Choisissons librement la valeur de x et appelons-la t. "
            "La première équation détermine alors y : un moins deux t, divisé par trois. "
            "Chaque réel t donne une solution différente.",
            remaining, parameter,
        )
        self.explain(
            "Cette formule décrit toute la droite. La variable libre exprime "
            "l'infinité des solutions compatibles : nous pouvons prendre "
            "n'importe quel réel t, et la valeur de y suit.",
            solution,
        )
        first_check = self.formula(r"2t+3\frac{1-2t}{3}=1", 48)
        second_check = self.formula(r"4t+6\frac{1-2t}{3}=2", 48)
        all_real = self.formula(r"\text{Ces deux égalités sont vraies pour tout }t\in\mathbb R.", 36)
        self.new_page("Contrôler dans les deux équations", first_check, second_check, all_real, gap=0.65)
        self.explain(
            "Vérifions en remplaçant x par t et y par un moins deux t, "
            "divisé par trois. Dans la première équation, le membre de gauche "
            "vaut un. Dans la seconde, il vaut deux. Les deux égalités "
            "sont vraies pour toute valeur réelle de t.",
            first_check, second_check, all_real,
        )

    def _zero_row(self):
        reduced = self.formula(r"\begin{cases}2x+3y=1,\\0=0.\end{cases}", 48)
        false = self.formula(r"(0,0):\qquad2\cdot0+3\cdot0=0\ne1", 44)
        note = self.words("La ligne nulle n'efface pas les autres contraintes.", 29, BLUE_D)
        self.new_page("Une infinité n'est pas tout le plan", reduced, false, note, gap=0.65)
        self.explain(
            "L'égalité zéro égal à zéro ne donne aucune nouvelle contrainte. "
            "Cela ne signifie pas que tous les couples de nombres sont solutions. "
            "La première ligne est toujours présente.",
            reduced,
        )
        self.explain(
            "Le couple zéro, zéro échoue dans la première équation. "
            "Les solutions forment une droite, pas le plan entier. "
            "Après élimination, il faut lire toutes les lignes restantes.",
            false, note,
        )

    def _cramer_boundary(self):
        formulas = self.formula(r"x=\frac{D_x}{D},\qquad y=\frac{D_y}{D}\qquad\text{si }D\ne0", 45)
        zero = self.formula(r"D=0:\quad\text{ces quotients ne sont pas définis}", 39)
        method = self.words("Revenir à l'élimination et aux seconds membres.", 29, BLUE_D)
        self.new_page("Cramer a une condition d'emploi", formulas, zero, method, gap=0.7)
        self.explain(
            "La règle de Cramer fournit une solution unique lorsque D est non nul. "
            "Si D vaut zéro, les quotients ne sont pas définis, même lorsque "
            "les numérateurs valent eux aussi zéro.",
            formulas, zero,
        )
        self.explain(
            "On ne choisit donc pas entre aucune solution et une infinité "
            "en interprétant une division par zéro. On examine la compatibilité "
            "par élimination, en gardant les seconds membres.",
            method,
        )

    def _self_check(self):
        system = self.formula(r"\begin{cases}x+ky=1,\\kx+y=1.\end{cases}", 51)
        question = self.words("Quand le déterminant est-il nul ?", 30)
        task = self.words("Dans chacun de ces cas : aucune solution ou une infinité ?", 28)
        self.new_page("À vous : deux valeurs du paramètre", system, question, task, gap=0.6)
        self.explain(
            "À vous, avec le système de synthèse du cahier. Trouvez les valeurs "
            "de k qui rendent le déterminant nul. Pour chacune, examinez "
            "les équations afin de décider s'il existe des solutions.",
            system, question, task, pause_after=6,
        )

    def _self_check_answer(self):
        determinant = self.formula(r"D=1-k^2=0\quad\Longleftrightarrow\quad k=1\text{ ou }k=-1", 40)
        compatible = self.formula(r"k=1:\quad x+y=1\quad\Rightarrow\quad(x,y)=(t,1-t),\ t\in\mathbb R", 37)
        impossible = self.formula(r"k=-1:\quad\begin{cases}x-y=1,\\-x+y=1\end{cases}\quad\Rightarrow\quad0=2", 42)
        result = self.words("k = 1 : une infinité. k = −1 : aucune.", 31, BLUE_D)
        self.new_page("Même déterminant nul, deux réponses", determinant, compatible, impossible, result, gap=0.4)
        self.explain(
            "Le déterminant vaut un moins k au carré. Il s'annule pour "
            "k égal à un ou moins un. À un, les deux équations sont identiques. "
            "La droite x plus y égal à un fournit une infinité de solutions.",
            determinant, compatible,
        )
        self.explain(
            "À moins un, additionner les deux équations donne zéro égal à deux. "
            "Le système est incompatible. Ces deux cas ont exactement "
            "le même déterminant nul et pourtant des réponses différentes.",
            impossible, result,
        )

    def _takeaway(self):
        rule = self.words("Unicité : regarder D. Compatibilité : lire les équations.", 28, BLUE_D)
        source = self.words("Manuel 12.7–12.9 · Cahier 12.3 C, 12.4 A, synthèse S1", 28)
        self.new_page("Conserver toute l'information", rule, source, gap=0.85)
        self.explain(
            "Pour un système carré, un déterminant non nul garantit une solution unique. "
            "Un déterminant nul ne garantit pas l'existence. L'élimination "
            "distingue la contradiction d'une véritable variable libre.",
            rule, source,
        )

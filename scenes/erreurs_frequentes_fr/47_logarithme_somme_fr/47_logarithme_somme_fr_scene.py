"""The logarithm converts a product into a sum; it does not split a sum."""
from math import log

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    RED_D,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Axes,
    Create,
    Dot,
    MathTex,
    MoveAlongPath,
    NumberLine,
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


class LogarithmeSommeFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._tempting_rule()
        self._counterexample()
        self._see_the_difference()
        self._valid_rule()
        self._exponents_move()
        self._derive_the_rule()
        self._self_check()
        self._self_check_answer()
        self._closing()
        self.wait(1.2)

    def _tempting_rule(self):
        condition = self.formula(r"a>0,\qquad b>0", 42, BLUE_D)
        question = self.formula(r"\ln(a+b)\ \overset{?}{=}\ \ln a+\ln b", 54)
        instruction = self.words("Testons la règle avant de l’utiliser.", 31)
        self.new_page("Peut-on séparer cette somme ?", condition, question, instruction, gap=0.65)
        self.explain(
            "Voici une erreur fréquente : le logarithme d’une somme serait la "
            "somme des logarithmes. Les deux arguments sont positifs, donc chaque "
            "expression est bien définie. Cela suffit-il à rendre l’égalité vraie ?",
            condition, question,
        )
        self.explain(
            "Avant de développer un long calcul, essayons des nombres très simples. "
            "Un seul contre-exemple suffit à réfuter une règle annoncée comme générale.",
            instruction,
        )

    def _counterexample(self):
        values = self.formula(r"a=b=1", 47, BLUE_D)
        left = panel(
            VGroup(
                self.words("Calculer la somme d’abord", 28),
                self.formula(r"\ln(1+1)=\ln2", 44),
            ).arrange(DOWN, buff=0.30),
            width=5.4, height=1.75,
        )
        right = panel(
            VGroup(
                self.words("Séparer les logarithmes", 28),
                self.formula(r"\ln1+\ln1=0", 44),
            ).arrange(DOWN, buff=0.30),
            width=5.4, height=1.75,
        )
        pair = VGroup(left, right).arrange(RIGHT, buff=0.5)
        result = self.formula(r"\ln2\ne0", 50, RED_D)
        self.new_page("Le test avec un et un", values, pair, result, gap=0.50)
        self.explain(
            "Prenons un et un. À gauche, on additionne d’abord : on obtient "
            "le logarithme de deux. À droite, le logarithme de un vaut zéro, "
            "donc la somme vaut zéro.",
            values, pair,
        )
        self.explain(
            "Ces résultats sont différents. Le logarithme de deux ne vaut pas "
            "zéro, puisque l’exponentielle de zéro vaut un, et non deux.",
            result,
        )

    def _see_the_difference(self):
        axes = Axes(
            x_range=[0, 3.2, 1], y_range=[-0.6, 1.5, 0.5],
            x_length=5.6, y_length=3.3,
            axis_config={"color": BLACK, "include_tip": True, "stroke_width": 2},
        )
        axis_labels = axes.get_axis_labels(self.formula("x", 28), self.formula("y", 28))
        curve = axes.plot(log, x_range=[0.58, 3.1], color=BLUE_D)
        one = Dot(axes.c2p(1, 0), radius=0.085, color=BLACK)
        probe = Dot(axes.c2p(1, 0), radius=0.09, color=BLUE_D)
        one_label = self.formula("1", 29).next_to(axes.c2p(1, 0), DOWN, buff=0.16)
        two_label = self.formula("2", 29).next_to(axes.c2p(2, 0), DOWN, buff=0.16)
        plot = VGroup(axes, axis_labels, curve, one, probe, one_label, two_label)
        statements = VGroup(
            self.formula(r"y=\ln x", 42, BLUE_D),
            self.formula(r"\ln1=0", 42),
            self.formula(r"\ln2>0", 42),
        ).arrange(DOWN, buff=0.65)
        diagram = VGroup(plot, statements).arrange(RIGHT, buff=0.80)
        self.new_page("Le graphe confirme le contre-exemple", diagram)
        self.explain(
            "Le graphe rend la différence visible. À l’entrée un, la courbe "
            "passe au niveau zéro. Suivons-la jusqu’à l’entrée deux.",
            axes, axis_labels, one, probe, one_label, two_label, statements[0], statements[1],
        )
        self.play(Create(curve), run_time=1.3)
        path = axes.plot(log, x_range=[1, 2], color=BLUE_D)
        self.play(MoveAlongPath(probe, path), run_time=1.8)
        self.explain(
            "Le point arrive au-dessus de l’axe horizontal. Le logarithme "
            "de deux est positif, tandis que les deux logarithmes de un restent nuls.",
            statements[2],
        )

    def _valid_rule(self):
        condition = self.formula(r"a>0,\qquad b>0", 43, BLUE_D)
        rule = panel(self.formula(r"\ln(ab)=\ln a+\ln b", 53), width=10.3, height=1.4)
        meaning = self.words("Un produit à l’intérieur devient une somme.", 30)
        self.new_page("La véritable règle", condition, rule, meaning, gap=0.65)
        self.explain(
            "La règle correcte concerne un produit à l’intérieur du logarithme. "
            "Pour deux arguments strictement positifs, le logarithme du produit "
            "est la somme des logarithmes. Pourquoi le produit joue-t-il ce rôle ?",
            condition, rule, meaning,
        )

    def _exponents_move(self):
        line = NumberLine(
            x_range=[0, 6, 1], length=9.6, color=BLACK,
            include_numbers=False, stroke_width=2,
        )
        labels = VGroup(*[
            self.formula(str(value), 30).next_to(line.n2p(value), DOWN, buff=0.18)
            for value in [0, 2, 5]
        ])
        probe = Dot(line.n2p(0), radius=0.09, color=BLUE_D)
        first = Arrow(line.n2p(0) + UP * 0.50, line.n2p(2) + UP * 0.50,
                      color=BLUE_D, buff=0, stroke_width=3)
        second = Arrow(line.n2p(2) + UP * 0.50, line.n2p(5) + UP * 0.50,
                       color=BLUE_D, buff=0, stroke_width=3)
        first_label = self.formula("+2", 32).next_to(first, UP, buff=0.10)
        second_label = self.formula("+3", 32).next_to(second, UP, buff=0.10)
        diagram = VGroup(line, labels, probe, first, second, first_label, second_label)
        product = self.formula(r"e^2\cdot e^3=e^{2+3}=e^5", 47)
        logarithm = self.formula(r"\ln(e^2e^3)=2+3=5", 45, BLUE_D)
        self.new_page("Multiplier ajoute les exposants", diagram, product, logarithm, gap=0.55)
        self.explain(
            "Le logarithme naturel donne l’exposant auquel il faut élever e. "
            "Cette droite repère les exposants. Le facteur e au carré correspond à deux.",
            line, labels, probe,
        )
        self.play(Create(first), probe.animate.move_to(line.n2p(2)), run_time=1.4)
        self.explain(
            "Partons donc de l’exposant deux. Multiplier par e au cube ajoute "
            "trois à cet exposant, suivant la règle des puissances.",
            first_label,
        )
        self.play(Create(second), probe.animate.move_to(line.n2p(5)), run_time=1.4)
        self.explain(
            "On arrive à cinq. Le produit des puissances correspond à la somme "
            "des exposants. Prendre le logarithme retrouve précisément cette somme.",
            second_label, product, logarithm,
        )

    def _derive_the_rule(self):
        names = self.formula(r"u=\ln a,\qquad v=\ln b", 43)
        powers = self.formula(r"a=e^u,\qquad b=e^v", 45)
        product = self.formula(r"ab=e^u e^v=e^{u+v}", 47, BLUE_D)
        conclusion = self.formula(r"\ln(ab)=u+v=\ln a+\ln b", 46)
        self.new_page("Le même raisonnement en général", names, powers, product, conclusion, gap=0.43)
        self.explain(
            "Pour deux nombres positifs quelconques, appelons u et v leurs "
            "logarithmes. Ces nombres s’écrivent e puissance u et e puissance v. "
            "Leur produit est donc e puissance u plus v. Son logarithme vaut u plus v.",
            names, powers, product, conclusion,
        )

    def _self_check(self):
        expressions = VGroup(
            self.formula(r"\ln(2+3)", 55),
            self.formula(r"\ln2+\ln3", 55),
        ).arrange(RIGHT, buff=1.3)
        question = self.words("Égaux ou différents ? Réécrivez chaque expression.", 29)
        self.new_page("À vous de comparer", expressions, question, gap=0.85)
        self.explain(
            "À vous. Comparez le logarithme de deux plus trois, avec la somme "
            "du logarithme de deux et du logarithme de trois. Réécrivez chaque "
            "expression sous la forme d’un seul logarithme.",
            expressions, question, pause_after=6,
        )

    def _self_check_answer(self):
        left = self.formula(r"\ln(2+3)=\ln5", 50)
        right = self.formula(r"\ln2+\ln3=\ln(2\cdot3)=\ln6", 46)
        conclusion = self.formula(r"\ln5\ne\ln6", 53, GREEN_D)
        self.new_page("Une somme, puis un produit", left, right, conclusion, gap=0.65)
        self.explain(
            "Dans la première expression, on effectue l’addition : il reste le "
            "logarithme de cinq. Dans la seconde, la règle du produit donne le "
            "logarithme de six. Ces valeurs sont différentes.",
            left, right, conclusion,
        )

    def _closing(self):
        condition = self.formula(r"a,b>0", 42, BLUE_D)
        rule = self.formula(r"\ln(ab)=\ln a+\ln b", 50)
        reminder = self.words("Pour une somme, aucune séparation générale.", 30)
        reference = self.words("MAT0339 · Cahier, exercice 6.3C", 28)
        self.new_page("Reconnaître l’opération", condition, rule, reminder, reference, gap=0.45)
        self.explain(
            "Avant d’utiliser une loi logarithmique, regardez l’opération à "
            "l’intérieur. Le produit se transforme en somme. Une somme, elle, "
            "ne se sépare pas par une règle générale.",
            condition, rule, reminder, reference,
        )

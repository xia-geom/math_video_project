"""MAT0339, manuel 8.3 et cahier 8.3 B : changer la condition change le groupe."""
from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GRAY_B,
    RIGHT,
    WHITE,
    Dot,
    FadeOut,
    MathTex,
    Rectangle,
    SurroundingRectangle,
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


class ProbabilitesConditionnellesInverseesFR(TeachingScene):
    """Lire la condition avant de choisir le dénominateur."""

    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._given_woman()
        self._given_math()
        self._repair()
        self._self_check()
        self._takeaway()
        self.wait(1.2)

    def _population(self):
        """Thirty equal-size dots; blue means mathematics in both groups."""
        women = VGroup(*[
            Dot(radius=0.105, color=BLUE_D if i < 6 else GRAY_B)
            for i in range(18)
        ]).arrange_in_grid(rows=3, cols=6, buff=0.22)
        men = VGroup(*[
            Dot(radius=0.105, color=BLUE_D if i < 3 else GRAY_B)
            for i in range(12)
        ]).arrange_in_grid(rows=3, cols=4, buff=0.22)
        women_label = self.words('18 femmes : 6 en maths', 28)
        men_label = self.words('12 hommes : 3 en maths', 28)
        left = VGroup(women_label, women).arrange(DOWN, buff=0.4)
        right = VGroup(men_label, men).arrange(DOWN, buff=0.4)
        people = VGroup(left, right).arrange(RIGHT, buff=1.0)
        # The frame fixes a roomy layout while the selected dots move.
        canvas = Rectangle(width=10.5, height=2.65, stroke_opacity=0)
        diagram = VGroup(canvas, people.move_to(canvas))
        return diagram, women, men, women_label, men_label

    def _question(self):
        comparison = self.formula(r'P(M\mid F)\overset{?}{=}P(F\mid M)', 52)
        legend = VGroup(
            self.words('F : la personne est une femme', 30),
            self.words('M : la personne étudie les maths', 30),
        ).arrange(DOWN, buff=0.26)
        prompt = self.words('Même rencontre, même probabilité ?', 31)
        self.new_page('Peut-on inverser la condition ?', comparison, legend, prompt)
        self.explain(
            'Voici deux probabilités qui utilisent les mêmes lettres. La première demande la proportion de personnes en maths parmi les femmes. La seconde demande la proportion de femmes parmi les personnes en maths.',
            comparison, legend, hold=2,
        )
        self.explain(
            'La barre se lit sachant que. L’information située après cette barre fixe le groupe dans lequel on choisit. Inverser les lettres peut donc changer la question, même si les personnes comptées au numérateur sont les mêmes.',
            prompt, hold=2,
        )

    def _given_woman(self):
        diagram, women, men, women_label, men_label = self._population()
        condition = self.formula(r'\text{Sachant }F :\quad P(M\mid F)=\frac{6}{18}=\frac13', 39)
        note = self.words('Le groupe de référence contient 18 personnes.', 29)
        self.new_page('Parmi les femmes', diagram, condition, note, gap=0.30)
        self.explain(
            'Reprenons la classe du cahier : dix-huit femmes, dont six en maths, et douze hommes, dont trois en maths. On choisit une personne au hasard, avec la même chance pour chacune. Chaque point représente une personne ; les points bleus représentent les personnes en maths.',
            diagram, hold=2,
        )
        frame = SurroundingRectangle(women, color=BLUE_D, buff=0.15)
        diagram.add(frame)
        self.explain(
            'On sait maintenant que la personne choisie est une femme. Les hommes sortent du groupe de référence. Encadrons les dix-huit femmes ; parmi elles, six points sont bleus.',
            frame, hold=2,
        )
        self.play(men.animate.set_opacity(0.16), men_label.animate.set_opacity(0.25), run_time=0.9)
        self.explain(
            'La probabilité cherchée vaut donc six sur dix-huit, soit un tiers. Diviser par trente répondrait à une autre question : choisir une femme qui étudie les maths dans toute la classe.',
            condition, note, hold=2,
        )

    def _given_math(self):
        diagram, women, men, women_label, men_label = self._population()
        condition = self.formula(r'\text{Sachant }M :\quad P(F\mid M)=\frac{6}{9}=\frac23', 39)
        note = self.words('Les 9 personnes en maths forment le nouveau groupe.', 28)
        self.new_page('Parmi les personnes en maths', diagram, condition, note, gap=0.30)
        self.explain(
            'Changeons seulement l’information connue : la personne étudie les maths. Cette fois, nous devons conserver les six femmes et les trois hommes en maths. Le nouveau groupe compte neuf personnes.',
            diagram, hold=2,
        )
        selected = list(women[:6]) + list(men[:3])
        center = diagram.get_center()
        positions = (
            [center + RIGHT * ((i - 2.5) * 0.45 - 1.05) for i in range(6)]
            + [center + RIGHT * ((i - 1) * 0.45 + 1.725) for i in range(3)]
        )
        self.play(
            FadeOut(VGroup(*women[6:], *men[3:], women_label, men_label)),
            *[dot.animate.move_to(position) for dot, position in zip(selected, positions)],
            run_time=1.7,
        )
        frame = SurroundingRectangle(VGroup(*selected), color=BLUE_D, buff=0.25)
        women_tag = self.words('6 femmes', 28).next_to(VGroup(*selected[:6]), DOWN, buff=0.35)
        men_tag = self.words('3 hommes', 28).next_to(VGroup(*selected[6:]), DOWN, buff=0.35)
        diagram.add(frame, women_tag, men_tag)
        self.explain(
            'Nous comptons toujours les mêmes six femmes en maths, mais parmi neuf personnes, et non parmi dix-huit. Le déplacement des points rend visible ce changement de groupe ; aucune personne n’a changé de catégorie.',
            frame, women_tag, men_tag, hold=2,
        )
        self.explain(
            'Six sur neuf donne deux tiers. Un tiers et deux tiers sont différents. La rencontre des deux événements est la même ; leur condition, donc le dénominateur, est différente.',
            condition, note, hold=2,
        )

    def _repair(self):
        first = self.formula(r'P(A\mid B)=\frac{P(A\cap B)}{P(B)}\qquad(P(B)>0)', 39)
        second = self.formula(r'P(B\mid A)=\frac{P(A\cap B)}{P(A)}\qquad(P(A)>0)', 39)
        rule = self.words('Lire « parmi qui ? » avant de calculer.', 32, BLUE_D)
        self.new_page('Le même numérateur ne suffit pas', first, second, rule, gap=0.55)
        self.explain(
            'Les deux formules ont le même numérateur, la probabilité de l’intersection. Mais l’une divise par la probabilité de B, l’autre par celle de A. Chaque condition doit avoir une probabilité strictement positive.',
            first, second, hold=2,
        )
        self.explain(
            'La méthode fiable consiste à traduire la question avec le mot parmi, à identifier ce groupe, puis à y compter les cas recherchés. Les deux résultats peuvent parfois coïncider, mais ce n’est pas une règle générale.',
            rule, hold=2,
        )

    def _self_check(self):
        data = VGroup(
            self.words('20 membres : 8 jouent du piano, 5 du violon.', 29),
            self.words('3 jouent des deux instruments.', 29),
        ).arrange(DOWN, buff=0.3)
        question = self.formula(r'P(V\mid P)=\ ?\qquad P(P\mid V)=\ ?', 44)
        self.new_page('À vous : quel groupe faut-il garder ?', data, question)
        self.explain(
            'Dans un club de vingt membres, huit jouent du piano, cinq du violon, et trois des deux instruments. Calculez la probabilité de jouer du violon sachant piano, puis la probabilité inverse. Prenez le temps de choisir chaque dénominateur.',
            data, question, hold=2, pause_after=6,
        )
        result = panel(self.formula(r'P(V\mid P)=\frac38,\qquad P(P\mid V)=\frac35', 45), width=9)
        why = self.words('3 personnes communes ; groupes de 8 et de 5.', 30)
        self.new_page('Réponse : deux groupes différents', result, why)
        self.explain(
            'Les trois personnes communes donnent le numérateur dans les deux cas. Parmi les huit pianistes, la proportion vaut trois huitièmes. Parmi les cinq violonistes, elle vaut trois cinquièmes. Le total de vingt n’est le dénominateur d’aucune de ces deux questions.',
            result, why, hold=2,
        )

    def _takeaway(self):
        rule = self.words('La condition fixe le groupe de référence.', 32, BLUE_D)
        source = self.words('Manuel 8.3 · Cahier 8.3 B', 28)
        self.new_page('Le réflexe à garder', rule, source)
        self.explain(
            'Avant toute fraction, posez la question : parmi qui ? Retrouvez l’exemple de la classe dans la section huit point trois du cahier, deuxième question. La condition fixe le groupe de référence.',
            rule, source, hold=2,
        )

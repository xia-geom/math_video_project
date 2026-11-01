"""MAT0339 8.3 et 8.8 : changer la condition change le groupe de référence."""
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
        self._base_rate_example()
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
        excluded_women = list(women[6:])
        excluded_men = list(men[3:])
        self.play(
            FadeOut(VGroup(*excluded_women, *excluded_men, women_label, men_label)),
            *[dot.animate.move_to(position) for dot, position in zip(selected, positions)],
            run_time=1.7,
        )
        # The temporary fade group does not own the population's stored children.
        # Detach them there too, so the page exit cannot restore the excluded group.
        women.remove(*excluded_women)
        men.remove(*excluded_men)
        for group, label in zip(diagram[1], (women_label, men_label), strict=True):
            group.remove(label)
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
            self.words('Chaque membre a la même chance d’être choisi.', 28, BLUE_D),
        ).arrange(DOWN, buff=0.3)
        question = self.formula(r'P(V\mid P)=\ ?\qquad P(P\mid V)=\ ?', 44)
        self.new_page('À vous : quel groupe faut-il garder ?', data, question)
        self.explain(
            'Dans un club de vingt membres, huit jouent du piano, cinq du violon, '
            'et trois des deux instruments. On choisit un membre au hasard, '
            'avec la même chance pour chacun. Calculez la probabilité de jouer '
            'du violon sachant piano, puis la probabilité inverse. Prenez le '
            'temps de choisir chaque dénominateur.',
            data, question, hold=2, pause_after=6,
        )
        result = panel(self.formula(r'P(V\mid P)=\frac38,\qquad P(P\mid V)=\frac35', 45), width=9)
        why = self.words('3 personnes communes ; groupes de 8 et de 5.', 30)
        self.new_page('Réponse : deux groupes différents', result, why)
        self.explain(
            'Les trois personnes communes donnent le numérateur dans les deux cas. Parmi les huit pianistes, la proportion vaut trois huitièmes. Parmi les cinq violonistes, elle vaut trois cinquièmes. Le total de vingt n’est le dénominateur d’aucune de ces deux questions.',
            result, why, hold=2,
        )

    def _base_rate_example(self):
        population = self.words('Modèle fictif : 10 000 personnes, 2 % malades.', 29)
        legend = self.words('M : malade • + : test positif', 29)
        rates = VGroup(
            self.formula(r'P(+\mid M)=95\,\%', 42),
            self.formula(r'P(+\mid\overline M)=4\,\%', 42),
        ).arrange(DOWN, buff=0.40)
        self.new_page('Le piège d’un test positif', population, legend, rates, gap=0.42)
        self.explain(
            'Appliquons le même raisonnement au modèle fictif du manuel. '
            'Sur dix mille personnes, deux pour cent sont malades. Nous utilisons '
            'maintenant M pour malade, et le signe plus pour un test positif.',
            population, legend, hold=2,
        )
        self.explain(
            'Le test est positif chez quatre-vingt-quinze pour cent des malades, '
            'mais aussi chez quatre pour cent des non-malades. Un résultat positif '
            'signifie-t-il pour autant quatre-vingt-quinze pour cent de probabilité '
            'd’être malade ? Transformons les pourcentages en effectifs.',
            rates, hold=2,
        )

        positions = [-4.0, -0.9, 1.65, 4.0]
        header = VGroup(
            self.words('Groupe', 28, BLUE_D).move_to([positions[0], 0, 0]),
            self.words('Test +', 28, BLUE_D).move_to([positions[1], 0, 0]),
            self.words('Test −', 28, BLUE_D).move_to([positions[2], 0, 0]),
            self.words('Total', 28, BLUE_D).move_to([positions[3], 0, 0]),
        )
        # Equal invisible row widths keep columns aligned when arranged vertically.
        header.add(Rectangle(width=10.8, height=0.60, stroke_opacity=0, fill_opacity=0))
        rows = []
        for label, counts in [
            ('Malades', ('190', '10', '200')),
            ('Non malades', ('392', r'9\,408', r'9\,800')),
            ('Total', ('582', r'9\,418', r'10\,000')),
        ]:
            cells = [self.words(label, 28).move_to([positions[0], 0, 0])]
            cells.extend(
                self.formula(count, 35).move_to([x, 0, 0])
                for count, x in zip(counts, positions[1:], strict=True)
            )
            cells.append(Rectangle(width=10.8, height=0.60, stroke_opacity=0, fill_opacity=0))
            rows.append(VGroup(*cells))
        table = VGroup(header, *rows).arrange(DOWN, buff=0.40)
        calculation = self.formula(
            r'200\times0{,}95=190,\qquad9\,800\times0{,}04=392', 34,
        )
        self.new_page('Compter avant de conditionner', table, calculation, gap=0.60)
        self.explain(
            'Deux pour cent de dix mille donne deux cents malades. '
            'Quatre-vingt-quinze pour cent de ces deux cents donne cent '
            'quatre-vingt-dix tests positifs, et dix tests négatifs.',
            header, rows[0], hold=2,
        )
        self.explain(
            'Les neuf mille huit cents autres personnes ne sont pas malades. '
            'Quatre pour cent de ce groupe donne trois cent quatre-vingt-douze '
            'tests positifs. Le petit taux de faux positifs s’applique donc '
            'à un groupe beaucoup plus grand.',
            rows[1], calculation, hold=2,
        )
        self.explain(
            'Au total, cinq cent quatre-vingt-deux personnes ont un test positif. '
            'La colonne des tests positifs et la ligne des malades ne désignent '
            'pas le même groupe de référence.',
            rows[2], hold=2,
        )
        selected_row = SurroundingRectangle(rows[0], color=BLUE_D, buff=0.16)
        selected_column = SurroundingRectangle(
            VGroup(header[1], *(row[1] for row in rows)), color=BLUE_D, buff=0.16,
        )
        self.page.add(selected_row, selected_column)
        self.explain(
            'Sachant que la personne est malade, nous gardons cette ligne : '
            'deux cents personnes.', selected_row, hold=2,
        )
        self.play(FadeOut(selected_row), run_time=0.35)
        self.page.remove(selected_row)
        self.explain(
            'Sachant que le test est positif, nous gardons cette colonne : '
            'cinq cent quatre-vingt-deux personnes.', selected_column, hold=2,
        )

        sensitivity = self.formula(r'P(+\mid M)=\frac{190}{200}=95\,\%', 44)
        posterior = self.formula(
            r'P(M\mid+) =\frac{190}{190+392}=\frac{190}{582}'
            r'\approx32{,}65\,\%', 39, BLUE_D,
        )
        rule = self.words('Même numérateur ; deux dénominateurs.', 30)
        self.new_page('95 % ne répond pas à la même question', sensitivity, posterior, rule, gap=0.55)
        self.explain(
            'Parmi les deux cents malades, cent quatre-vingt-dix ont un test '
            'positif : c’est bien quatre-vingt-quinze pour cent. Mais parmi '
            'les cinq cent quatre-vingt-deux tests positifs, cent quatre-vingt-dix '
            'correspondent à une personne malade : environ trente-deux virgule '
            'soixante-cinq pour cent, dans ce modèle.',
            sensitivity, posterior, hold=2,
        )
        self.explain(
            'Le taux initial de maladie fixe la taille des groupes avant le test. '
            'Oublier cette information revient à choisir le mauvais dénominateur. '
            'Nous retrouvons exactement le réflexe appris avec la classe : parmi qui ?',
            rule, hold=2,
        )

    def _takeaway(self):
        rule = self.words('La condition fixe le groupe de référence.', 32, BLUE_D)
        source = self.words('Manuel 8.3 et 8.8 · Cahier 8.3 B', 28)
        self.new_page('Le réflexe à garder', rule, source)
        self.explain(
            'Avant toute fraction, posez la question : parmi qui ? Retrouvez '
            'la classe dans la section huit point trois du cahier, deuxième '
            'question, et le modèle de test dans la section huit point huit '
            'du manuel. La condition fixe le groupe de référence.',
            rule, source, hold=2,
        )

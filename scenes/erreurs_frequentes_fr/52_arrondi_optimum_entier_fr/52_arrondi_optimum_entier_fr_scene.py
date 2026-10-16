"""Continuous and integer optima: verify feasibility and exhaust the finite lattice."""
from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    GREY_B,
    RED_D,
    RIGHT,
    UP,
    WHITE,
    Axes,
    Create,
    Dot,
    FadeOut,
    Line,
    Polygon,
    SurroundingRectangle,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene

config.background_color = WHITE


def feasible_integer_points():
    """All integer candidates, since the two constraints imply 0 <= x,y <= 4."""
    return tuple((x, y) for x in range(5) for y in range(5)
                 if 2 * x + y <= 8 and x + 2 * y <= 8)


def profit(x, y):
    return 30 * x + 40 * y


class ArrondiOptimumEntierFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._region_and_rounding()
        self._complete_integer_comparison()
        self._self_check()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        model = self.formula(
            r'\begin{cases}2x+y\le8,\\x+2y\le8,\\x,y\ge0\end{cases}'
            r'\qquad P=30x+40y', 42)
        candidate = self.formula(r'\left(\frac83,\frac83\right)'
                                 r'\ \longrightarrow\ (3,3)\;?', 48, RED_D)
        context = self.words('Les produits doivent être fabriqués à l’unité.', 28)
        self.new_page('Peut-on arrondir l’optimum ?', model, candidate, context)
        self.explain(
            'Nous fabriquons deux produits, en quantités x et y. Les deux premières '
            'inégalités représentent des capacités disponibles. Le profit est trente '
            'fois x, plus quarante fois y. Pour commencer, le modèle autorise des '
            'quantités réelles.', model)
        self.explain(
            'Son optimum vaut huit tiers pour chaque produit. Mais les produits sont '
            'indivisibles. Arrondir les deux quantités à trois semble naturel. '
            'Vérifions pourtant ce que cette opération fait aux contraintes.',
            candidate, context)

    def _region_and_rounding(self):
        # Identical ranges and lengths preserve the geometry's equal unit scale.
        axes = Axes(x_range=[0, 4.5, 1], y_range=[0, 4.5, 1],
                    x_length=3.75, y_length=3.75,
                    axis_config={'color': BLACK, 'include_tip': False,
                                 'include_numbers': True, 'font_size': 22,
                                 'decimal_number_config': {'color': BLACK},
                                 'numbers_to_exclude': [0]})
        # NumberLine's child glyph defaults can otherwise remain white.
        axes.set_color(BLACK)
        axis_names = VGroup(self.formula('x', 24).next_to(axes.x_axis, RIGHT, buff=0.08),
                            self.formula('y', 24).next_to(axes.y_axis, UP, buff=0.08))
        region = Polygon(*(axes.c2p(x, y) for x, y in
                           [(0, 0), (4, 0), (8 / 3, 8 / 3), (0, 4)]),
                         color=BLUE_D, fill_color=BLUE_D, fill_opacity=0.10,
                         stroke_width=2)
        lattice = VGroup(*(Dot(axes.c2p(x, y), radius=0.045, color=GREY_B)
                           for x, y in feasible_integer_points()))
        level = Line(axes.c2p(0, 1.5), axes.c2p(2, 0), color=BLUE_D,
                     stroke_width=3)
        candidate = Dot(axes.c2p(8 / 3, 8 / 3), radius=0.08, color=BLUE_D)
        continuous_label = self.formula(r'(8/3,8/3)', 24, BLUE_D)
        continuous_label.next_to(candidate, UP, buff=0.12)
        rounded_label = self.formula(r'(3,3)', 26, RED_D)
        rounded_label.next_to(axes.c2p(3, 3), UP, buff=0.14)
        diagram = VGroup(axes, axis_names, region, lattice, level,
                         candidate, continuous_label, rounded_label)
        continuous = self.formula(r'P_{\mathrm{continu}}=\frac{560}{3}', 34, BLUE_D)
        violation = self.formula(r'2(3)+3=9>8', 36, RED_D)
        second = self.formula(r'3+2(3)=9>8', 36, RED_D)
        verdict = self.words('Le point arrondi est interdit.', 28, RED_D)
        notes = VGroup(continuous, violation, second, verdict).arrange(DOWN, buff=0.45)
        layout = VGroup(diagram, notes).arrange(RIGHT, buff=0.6)
        self.new_page('Arrondir peut sortir de la région', layout)
        self.explain(
            'La région bleue contient les choix autorisés. Les points gris sont '
            'les choix entiers. Faisons glisser une droite de profit constant. '
            'Pour le problème continu, son dernier contact se trouve au croisement '
            'des deux contraintes.', axes, axis_names, region, lattice, level)
        # Clip the final objective line to the square [0,4]^2.
        self.play(level.animate.put_start_and_end_on(
            axes.c2p(8 / 9, 4), axes.c2p(4, 5 / 3)), run_time=1.7)
        self.explain(
            'Au point bleu, le profit vaut cinq cent soixante tiers. Regardons '
            'maintenant le déplacement produit par l’arrondi.',
            candidate, continuous_label, continuous)
        self.play(FadeOut(continuous_label), run_time=0.35)
        self.play(candidate.animate.move_to(axes.c2p(3, 3)).set_color(RED_D),
                  run_time=1.4)
        self.explain(
            'Le nouveau point sort du polygone. Chaque ressource serait utilisée '
            'à hauteur de neuf unités, alors que huit seulement sont disponibles. '
            'Un profit apparemment meilleur ne répare pas une solution impossible.',
            rounded_label, violation, second, verdict, hold=1.4)

    def _complete_integer_comparison(self):
        xs = [-4.55, -1.75, 1.7, 4.4]
        header = VGroup(*(self.words(word, 28, BLUE_D).move_to([x, 0, 0])
                          for word, x in zip(('x', 'y permis', 'meilleur y', 'profit'), xs)))
        data = [(0, '0,1,2,3,4', 4, 160), (1, '0,1,2,3', 3, 150),
                (2, '0,1,2,3', 3, 180), (3, '0,1,2', 2, 170),
                (4, '0', 0, 120)]
        rows = [VGroup(*(self.formula(str(value), 34).move_to([x, 0, 0])
                         for value, x in zip(row, xs))) for row in data]
        table = VGroup(header, *rows).arrange(DOWN, buff=0.22)
        conclusion = self.formula(r'P(2,3)=180', 42, GREEN_D)
        self.new_page('Comparer tous les choix entiers', table, conclusion, gap=0.4)
        self.explain(
            'Comment trouver le véritable optimum entier ? La non-négativité et '
            'les capacités imposent que x et y soient compris entre zéro et quatre. '
            'Nous pouvons donc examiner tous les points entiers, sans nous limiter '
            'aux voisins du point bleu.', header)
        self.explain(
            'Voici toutes les valeurs permises de y, pour chaque valeur entière '
            'de x. Cela représente dix-sept points au total. À x fixé, le profit '
            'augmente avec y : nous retenons donc le plus grand y autorisé '
            'dans chaque ligne.', *rows, hold=1.8)
        best = SurroundingRectangle(rows[2], color=GREEN_D, buff=0.13, stroke_width=2)
        self.page.add(best)
        self.play(Create(best), run_time=0.7)
        self.explain(
            'Les cinq meilleurs profits par ligne sont maintenant comparables. '
            'Cent quatre-vingts est le plus grand. Deux produits du premier type '
            'et trois du second respectent les deux contraintes. Cette comparaison '
            'exhaustive prouve leur optimalité.', conclusion)

    def _self_check(self):
        question = self.formula(r'x+y\le5{,}5,\quad x,y\in\mathbb Z_{\ge0}'
                                r'\qquad Q=2x+y', 34)
        guess = self.formula(r'(5{,}5,0)\longrightarrow(6,0)\;?', 46, RED_D)
        prompt = self.words('Quel est le meilleur choix entier ?', 30)
        self.new_page('À vous de vérifier', question, guess, prompt, gap=0.65)
        self.explain(
            'Essayez un autre problème. La somme des deux quantités ne dépasse pas '
            'cinq virgule cinq, et le profit est deux x plus y. Le maximum continu '
            'se trouve en cinq virgule cinq, zéro. Peut-on arrondir à six, zéro ? '
            'Cherchez aussi le meilleur choix entier.',
            question, guess, prompt, pause_after=6)
        limit = self.formula(r'x+y\in\mathbb Z\quad\Longrightarrow\quad x+y\le5', 38)
        bound = self.formula(r'Q=2x+y\le2(x+y)\le10', 42)
        answer = self.formula(r'(x,y)=(5,0),\qquad Q=10', 46, GREEN_D)
        self.new_page('Une borne et un point qui l’atteint', limit, bound, answer)
        self.explain(
            'Six, zéro est interdit. Une somme entière inférieure ou égale à cinq '
            'virgule cinq ne dépasse pas cinq. Le profit ne peut donc pas dépasser '
            'dix. Le point cinq, zéro atteint exactement dix : il est optimal.',
            limit, bound, answer, hold=1.6)

    def _takeaway(self):
        rule = self.words('Vérifier les contraintes après tout arrondi.', 30, BLUE_D)
        proof = self.words('Puis justifier l’optimum parmi les choix entiers.', 28)
        source = self.words('MAT0339 : M13.3 • C13, synthèse S3', 28)
        self.new_page('À retenir', rule, proof, source, gap=0.65)
        self.explain(
            'Retenez deux étapes : vérifier que le choix entier reste autorisé, '
            'puis justifier qu’aucun autre choix entier ne fait mieux. Le manuel '
            'et le problème de synthèse indiqués prolongent cette distinction.',
            rule, proof, source)

"""Continuous and integer optima: verify feasibility and exhaust the finite lattice."""
from manim import (
    BLACK,
    DOWN,
    RIGHT,
    UP,
    WHITE,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeOut,
    Polygon,
    SurroundingRectangle,
    VGroup,
    config,
)

from tools import tts
from tools.teaching_chapters import (
    play_chapter_outline,
    play_lesson_closing,
    play_lesson_opening,
)
from tools.teaching_layout import TeachingScene

LESSON_TITLE = 'Arrondi et optimum entier'
LESSON_OBJECTIVE = 'Vérifier la faisabilité après arrondi\net justifier l’optimum entier.'
CHAPTERS = (
    'Comprendre l’optimum continu',
    'Tester l’arrondi',
    'Comparer les choix entiers',
    'Vérifier sa méthode',
)

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
        narration = None if self.silent else self.chapter_narration
        play_lesson_opening(self, LESSON_TITLE, LESSON_OBJECTIVE, narration=narration)
        play_chapter_outline(
            self, CHAPTERS, 0, 'Commençons par le problème continu et son maximum.',
            narration=narration,
        )
        self._question()
        self._continuous_check()
        play_chapter_outline(
            self, CHAPTERS, 1, 'Vérifions sur la région réalisable ce que fait l’arrondi.',
            narration=narration,
        )
        self._region_and_rounding()
        play_chapter_outline(
            self, CHAPTERS, 2, 'Cherchons le meilleur choix parmi tous les candidats entiers.',
            narration=narration,
        )
        self._complete_integer_comparison()
        play_chapter_outline(
            self, CHAPTERS, 3, 'Appliquons ces deux contrôles à un autre problème.',
            narration=narration,
        )
        self._self_check()
        self._closing()

    def _question(self):
        model = self.formula(
            r'\begin{cases}2x+y\le8,\\x+2y\le8,\\x,y\ge0\end{cases}'
            r'\qquad P=30x+40y', 42)
        candidate = self.formula(r'\left(\frac83,\frac83\right)'
                                 r'\ \longrightarrow\ (3,3)\;?', 48, BLACK)
        context = self.words('Les produits doivent être fabriqués à l’unité.', 28)
        self.new_page('Peut-on arrondir l’optimum ?', model, candidate, context)
        self.explain(
            f'Nous fabriquons deux produits, en quantités x et {tts.char("y")}. Les deux premières '
            'inégalités représentent des capacités disponibles. Le profit est trente '
            f'fois x, plus quarante fois {tts.char("y")}. Pour commencer, le modèle autorise des '
            'quantités réelles.', model)
        self.explain(
            'Son optimum vaut huit tiers pour chaque produit. Mais les produits sont '
            'indivisibles. Arrondir les deux quantités à trois semble naturel. '
            'Vérifions pourtant ce que cette opération fait aux contraintes.',
            candidate, context)

    def _continuous_check(self):
        table = self.formula(
            r'\begin{array}{c|cccc}'
            r'(x,y)&(0,0)&(4,0)&(0,4)&(8/3,8/3)\\\hline '
            r'P(x,y)&0&120&160&560/3'
            r'\end{array}', 35,
        )
        result = self.formula(r'P_{\max}=\frac{560}{3}\approx186{,}67', 44, BLACK)
        domain = self.words('Région fermée, bornée, convexe et non vide.', 28)
        self.new_page('Vérifier d’abord le maximum continu', table, result, domain, gap=0.55)
        self.explain(
            'Le modèle continu a quatre sommets. Sur cette région fermée, '
            'bornée, convexe et non vide, il suffit de comparer le profit '
            'aux sommets. Les valeurs sont zéro, cent vingt, cent soixante '
            'et cinq cent soixante tiers.', table, domain)
        self.explain(
            'La dernière valeur est la plus grande, environ cent '
            'quatre-vingt-six virgule soixante-sept. Cela justifie le maximum '
            'continu avant d’ajouter la contrainte des quantités entières.',
            result)

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
                         color=BLACK, fill_color=BLACK, fill_opacity=0.10,
                         stroke_width=2)
        lattice = VGroup(*(Dot(axes.c2p(x, y), radius=0.045, color=BLACK)
                           for x, y in feasible_integer_points()))
        level = DashedLine(axes.c2p(0, 1.5), axes.c2p(2, 0), color=BLACK,
                           stroke_width=3, dash_length=0.12)
        candidate = Dot(axes.c2p(8 / 3, 8 / 3), radius=0.09, color=BLACK,
                        fill_color=WHITE, stroke_color=BLACK, stroke_width=2.5)
        continuous_label = self.formula(r'(8/3,8/3)', 24, BLACK)
        # Keep the descending objective line clear of the vertex annotation.
        continuous_label.next_to(candidate, UP, buff=0.12).shift(RIGHT * 0.6)
        rounded_label = self.formula(r'(3,3)', 26, BLACK)
        rounded_label.next_to(axes.c2p(3, 3), UP, buff=0.14)
        diagram = VGroup(axes, axis_names, region, lattice, level,
                         candidate, continuous_label, rounded_label)
        continuous = self.formula(r'P_{\mathrm{continu}}=\frac{560}{3}', 34, BLACK)
        violation = self.formula(r'2(3)+3=9>8', 36, BLACK)
        second = self.formula(r'3+2(3)=9>8', 36, BLACK)
        verdict = self.words('Le point arrondi est interdit.', 28, BLACK)
        notes = VGroup(continuous, violation, second, verdict).arrange(DOWN, buff=0.45)
        layout = VGroup(diagram, notes).arrange(RIGHT, buff=0.6)
        self.new_page('Arrondir peut sortir de la région', layout)
        self.explain(
            'La zone ombrée contient les choix autorisés. Les petits points sont '
            'les choix entiers. Faisons glisser la droite en pointillés, à profit constant. '
            'Pour le problème continu, son dernier contact se trouve au croisement '
            'des deux contraintes.', axes, axis_names, region, lattice, level)
        # Clip the final objective line to the square [0,4]^2.
        self.play(level.animate.put_start_and_end_on(
            axes.c2p(8 / 9, 4), axes.c2p(4, 5 / 3)), run_time=1.7)
        self.explain(
            'Au sommet marqué par un cercle, le profit vaut cinq cent soixante tiers. Regardons '
            'maintenant le déplacement produit par l’arrondi.',
            candidate, continuous_label, continuous)
        self.play(FadeOut(continuous_label), run_time=0.35)
        # The outgoing page must not restore the old coordinates beside (3, 3).
        diagram.remove(continuous_label)
        self.play(candidate.animate.move_to(axes.c2p(3, 3)),
                  run_time=1.4)
        self.explain(
            'Le nouveau point sort du polygone. Chaque ressource serait utilisée '
            'à hauteur de neuf unités, alors que huit seulement sont disponibles. '
            'Un profit apparemment meilleur ne répare pas une solution impossible.',
            rounded_label, violation, second, verdict, hold=1.4)

    def _complete_integer_comparison(self):
        xs = [-4.55, -1.75, 1.7, 4.4]
        header = VGroup(*(self.words(word, 28, BLACK).move_to([x, 0, 0])
                          for word, x in zip(('x', 'y permis', 'meilleur y', 'profit'), xs)))
        data = [(0, '0,1,2,3,4', 4, 160), (1, '0,1,2,3', 3, 150),
                (2, '0,1,2,3', 3, 180), (3, '0,1,2', 2, 170),
                (4, '0', 0, 120)]
        rows = [VGroup(*(self.formula(str(value), 34).move_to([x, 0, 0])
                         for value, x in zip(row, xs))) for row in data]
        table = VGroup(header, *rows).arrange(DOWN, buff=0.22)
        conclusion = self.formula(r'P(2,3)=180', 42, BLACK)
        self.new_page('Comparer tous les choix entiers', table, conclusion, gap=0.4)
        self.explain(
            'Comment trouver le véritable optimum entier ? La non-négativité et '
            f'les capacités imposent que x et {tts.char("y")} soient compris entre zéro et quatre. '
            'Nous pouvons donc examiner tous les points entiers, sans nous limiter '
            'aux voisins de l’optimum continu.', header)
        self.explain(
            f'Voici toutes les valeurs permises de {tts.char("y")}, pour chaque valeur entière '
            'de x. Cela représente dix-sept points au total. À x fixé, le profit '
            f'augmente avec {tts.char("y")} : nous retenons donc le plus grand {tts.char("y")} autorisé '
            'dans chaque ligne.', *rows, hold=1.8)
        best = SurroundingRectangle(rows[2], color=BLACK, buff=0.13, stroke_width=2)
        self.page.add(best)
        self.play(Create(best), run_time=0.7)
        self.explain(
            'Les cinq meilleurs profits par ligne sont maintenant comparables. '
            'Cent quatre-vingts est le plus grand. Deux produits du premier type '
            'et trois du second respectent les deux contraintes. Cette comparaison '
            'exhaustive prouve leur optimalité.', conclusion)

        admissible = self.formula(r'(2,2):\quad2(2)+2=6\le8,\quad2+2(2)=6\le8', 34)
        comparison = self.formula(r'P(2,2)=140<180=P(2,3)', 42, BLACK)
        warning = self.words('Un arrondi autorisé peut rester sous-optimal.', 29)
        self.new_page('Et si l’on arrondissait vers le bas ?', admissible, comparison, warning, gap=0.55)
        self.explain(
            'Arrondir les deux quantités vers le bas donne deux, deux. '
            'Ce point respecte les deux capacités et les contraintes de '
            'non-négativité et d’intégralité. Mais son profit vaut seulement '
            'cent quarante, contre cent quatre-vingts pour deux, trois. '
            'Vérifier la faisabilité est nécessaire ; cela ne prouve pas '
            'encore l’optimalité.', admissible, comparison, warning)

    def _self_check(self):
        question = self.formula(r'x+y\le5{,}5,\quad x,y\in\mathbb Z_{\ge0}'
                                r'\qquad Q=2x+y', 34)
        guess = self.formula(r'(5{,}5,0)\longrightarrow(6,0)\;?', 46, BLACK)
        prompt = self.words('Quel est le meilleur choix entier ?', 30)
        self.new_page('À vous de vérifier', question, guess, prompt, gap=0.65)
        self.explain(
            'Essayez un autre problème. La somme des deux quantités ne dépasse pas '
            f'cinq virgule cinq, et le profit est deux x plus {tts.char("y")}. Le maximum continu '
            'se trouve en cinq virgule cinq, zéro. Peut-on arrondir à six, zéro ? '
            'Cherchez aussi le meilleur choix entier.',
            question, guess, prompt, pause_after=6)
        limit = self.formula(r'x+y\in\mathbb Z\quad\Longrightarrow\quad x+y\le5', 38)
        bound = self.formula(r'Q=2x+y\le2(x+y)\le10', 42)
        answer = self.formula(r'(x,y)=(5,0),\qquad Q=10', 46, BLACK)
        self.new_page('Une borne et un point qui l’atteint', limit, bound, answer)
        self.explain(
            'Six, zéro est interdit. Une somme entière inférieure ou égale à cinq '
            'virgule cinq ne dépasse pas cinq. Le profit ne peut donc pas dépasser '
            'dix. Le point cinq, zéro atteint exactement dix : il est optimal.',
            limit, bound, answer, hold=1.6)

    def _closing(self):
        # Références conservées dans le catalogue et le README : Manuel 13.1–13.3 · Cahier 13, synthèse S3.
        play_lesson_closing(
            self, LESSON_TITLE,
            (
                'Un arrondi peut violer les contraintes.',
                'Un choix réalisable peut être sous-optimal.',
                'Prouver l’optimum : comparer ou donner une borne.',
            ),
            '\\begin{gathered}Q=2x+y\\\\x+y\\le5{,}5,\\quad x,y\\in\\mathbb Z_{\\ge0}\\end{gathered}',
            'Trouvez le maximum et justifiez votre choix.',
            recap_spoken='Un arrondi peut violer les contraintes. Un choix réalisable peut être sous-optimal. Prouver l’optimum : comparer ou donner une borne.',
            practice_spoken=f'Reprenez le problème où x et {tts.char("y")} sont des entiers non négatifs et leur somme ne dépasse pas cinq virgule cinq. Maximisez deux x plus {tts.char("y")} et justifiez le résultat.',
            narration=None if self.silent else self.chapter_narration,
        )

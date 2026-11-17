"""Separate signed component, vector projection and its nonnegative length."""
from manim import (
    BLACK,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Axes,
    Create,
    DashedLine,
    Dot,
    Line,
    Rectangle,
    RightAngle,
    VGroup,
    config,
)

from tools.teaching_chapters import (
    play_chapter_outline,
    play_lesson_closing,
    play_lesson_opening,
)
from tools.teaching_layout import TeachingScene

LESSON_TITLE = 'Projection signée et longueur'
LESSON_OBJECTIVE = 'Distinguer composante signée,\nvecteur projeté et longueur.'
CHAPTERS = (
    'Visualiser la projection',
    'Distinguer les trois objets',
    'Justifier et contrôler la formule',
    'Calculer une projection oblique',
)

config.background_color = WHITE


class ProjectionSigneeLongueurFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        narration = None if self.silent else self.chapter_narration
        play_lesson_opening(self, LESSON_TITLE, LESSON_OBJECTIVE, narration=narration)
        play_chapter_outline(
            self, CHAPTERS, 0, 'Commençons par projeter sur toute la droite.',
            narration=narration,
        )
        self._question()
        self._geometric_projection()
        play_chapter_outline(
            self, CHAPTERS, 1, 'Séparons la composante signée, le vecteur projeté et sa longueur.',
            narration=narration,
        )
        self._signed_component()
        self._three_objects()
        play_chapter_outline(
            self, CHAPTERS, 2, 'Justifions la formule et examinons l’orientation ainsi que le vecteur nul.',
            narration=narration,
        )
        self._derive_projection()
        self._reverse_orientation()
        self._zero_vector()
        play_chapter_outline(
            self, CHAPTERS, 3, 'Calculons une projection oblique et contrôlons le reste.',
            narration=narration,
        )
        self._self_check()
        self._answer()
        self._check_residual()
        self._closing()

    def _question(self):
        vectors = self.formula(r'\vec u=(-3,2),\qquad\vec v=(2,0)', 46)
        dot = self.formula(r'\vec u\cdot\vec v=-6', 49, BLACK)
        mistake = self.words('La projection aurait une longueur de −6 ?', 30, BLACK)
        prompt = self.words('Un nombre signé, un vecteur ou une distance ?', 29)
        self.new_page('Que mesure le produit scalaire ?', vectors, dot,
                      mistake, prompt, gap=0.45)
        self.explain(
            'Prenons ces deux vecteurs. Leur produit scalaire vaut moins six. '
            'Peut-on annoncer une projection de longueur moins six ? '
            'Une longueur ne peut pas être négative. De plus, le vecteur '
            'qui fixe la direction a ici une norme de deux, et non de un.',
            vectors, dot, mistake)
        self.explain(
            'Nous allons distinguer trois objets : une composante signée, '
            'un vecteur projeté et la longueur de ce vecteur. Les confondre '
            'fait perdre soit le sens, soit le facteur de normalisation.', prompt)

    def _geometric_projection(self):
        # Identical 0.78 screen-unit scales preserve the right angle.
        axes = Axes(
            x_range=[-4, 3, 1], y_range=[-1, 3, 1],
            x_length=5.46, y_length=3.12,
            axis_config={'color': BLACK, 'include_tip': False, 'stroke_width': 1.5},
        )
        canvas = Rectangle(width=6.3, height=4.2, stroke_opacity=0, fill_opacity=0)
        axes.move_to(canvas)
        labels = VGroup(
            self.formula('x', 25).next_to(axes.x_axis, RIGHT, buff=0.10),
            self.formula('y', 25).next_to(axes.y_axis, UP, buff=0.10),
            self.formula('-3', 24).next_to(axes.c2p(-3, 0), DOWN, buff=0.16),
            self.formula('2', 24).next_to(axes.c2p(2, 0), DOWN, buff=0.16),
            self.formula('2', 24).next_to(axes.c2p(0, 2), LEFT, buff=0.14),
        )
        diagram = VGroup(canvas, axes, labels)
        first = self.formula(r'\vec u=(-3,2)', 39, BLACK)
        reference = self.formula(r'\vec v=(2,0)', 39, BLACK)
        support = self.formula(r'\text{Droite }\mathbb R\vec v', 35)
        projected_value = self.formula(r'\vec p=(-3,0)', 39, BLACK)
        notes = VGroup(first, reference, support, projected_value).arrange(DOWN, buff=0.48)
        body = VGroup(diagram, notes).arrange(RIGHT, buff=0.55)
        self.new_page('Projeter sur toute une droite', body)

        origin, tip, foot = axes.c2p(0, 0), axes.c2p(-3, 2), axes.c2p(-3, 0)
        u = Arrow(origin, tip, color=BLACK, buff=0, stroke_width=3)
        v = Arrow(origin, axes.c2p(2, 0), color=BLACK, buff=0, stroke_width=4)
        projection = Arrow(origin, foot, color=BLACK, buff=0, stroke_width=4)
        drop = DashedLine(tip, foot, color=BLACK, stroke_width=2)
        right_angle = RightAngle(Line(foot, origin), Line(foot, tip),
                                 length=0.18, color=BLACK, stroke_width=2)
        probe = Dot(tip, color=BLACK, radius=0.075,
                    fill_color=WHITE, fill_opacity=1, stroke_width=2)
        origin_dot = Dot(origin, color=BLACK, radius=0.045)
        u_label = self.formula(r'\vec u', 28, BLACK).next_to(tip, UP, buff=0.12)
        v_label = self.formula(r'\vec v', 28, BLACK).next_to(v, UP, buff=0.16)
        p_label = self.formula(r'\vec p', 28, BLACK).next_to(projection, DOWN, buff=0.17)
        diagram.add(u, v, projection, drop, right_angle, probe, origin_dot,
                    u_label, v_label, p_label)
        self.explain(
            'Les deux axes ont la même unité. Le vecteur v oriente la '
            'droite horizontale vers la droite. Nous projetons sur toute '
            'cette droite, y compris sa partie négative, et pas seulement '
            'sur la demi-droite orientée par v.', axes, labels, u, v, origin_dot,
            u_label, v_label, first, reference, support)
        self.explain(
            'Depuis l’extrémité du vecteur u, descendons perpendiculairement '
            'vers la droite de projection. Le point atteint a pour coordonnées '
            'moins trois, zéro.', probe)
        self.play(Create(drop), probe.animate.move_to(foot), run_time=1.8)
        self.play(Create(projection), Create(right_angle), run_time=1.0)
        self.explain(
            'Le vecteur projeté part de l’origine et va vers ce point. '
            'Il est dirigé vers la gauche, donc à l’opposé du vecteur v. '
            'Sa longueur vaut trois, même si sa composante orientée sera négative.',
            p_label, projected_value)

    def _signed_component(self):
        norm = self.formula(r'\|\vec v\|=2,\qquad\vec e=\frac{\vec v}{\|\vec v\|}=(1,0)', 42)
        scalar = self.formula(r'c=\vec u\cdot\vec e=(-3)(1)+2(0)=-3', 44, BLACK)
        comparison = self.formula(r'\vec u\cdot\vec v=\|\vec v\|\,c=2(-3)=-6', 41)
        note = self.words('Le signe indique le sens par rapport à e.', 29)
        self.new_page('D’abord une direction unitaire', norm, scalar,
                      comparison, note, gap=0.43)
        self.explain(
            'Pour mesurer une composante, il faut une direction de norme un. '
            'Divisons donc le vecteur v par sa norme, deux. Le vecteur unitaire '
            'e vaut un, zéro. Le produit de u avec e donne moins trois : '
            'c’est la composante signée, que nous appelons c.', norm, scalar)
        self.explain(
            'Le produit avec v vaut moins six parce que v est deux fois e. '
            'Ce produit contient aussi la norme de v. Pour retrouver la '
            'composante signée, on le divise par cette norme. Le signe moins '
            'indique ici un sens opposé à e.', comparison, note)

    def _three_objects(self):
        component = self.formula(r'\text{Composante signée : }c=-3', 40, BLACK)
        vector = self.formula(r'\text{Vecteur : }\vec p=c\vec e=(-3,0)', 40, BLACK)
        length = self.formula(r'\text{Longueur : }\|\vec p\|=|c|=3', 40, BLACK)
        residual = self.formula(r'\vec u-\vec p=(0,2),\qquad(\vec u-\vec p)\cdot\vec v=0', 35)
        self.new_page('Trois objets différents', component, vector, length,
                      residual, gap=0.46)
        self.explain(
            'La composante moins trois est un nombre signé. En la multipliant '
            'par e, nous obtenons le vecteur moins trois, zéro. Sa norme est '
            'trois : prendre la valeur absolue conserve la longueur, '
            'mais ne conserve pas l’information de sens.', component, vector, length)
        self.explain(
            'Le reste, u moins son projeté, vaut zéro, deux. Il est vertical '
            'et son produit scalaire avec v est nul. C’est le contrôle '
            'essentiel : le projeté est parallèle à la droite et le reste '
            'lui est perpendiculaire.', residual)

    def _derive_projection(self):
        parallel = self.formula(r'\vec v\ne\vec0,\qquad\vec p=\alpha\vec v', 41)
        perpendicular = self.formula(r'(\vec u-\alpha\vec v)\cdot\vec v=0', 44)
        coefficient = self.formula(r'\alpha\|\vec v\|^2=\vec u\cdot\vec v', 44)
        rule = self.formula(r'\vec p=\frac{\vec u\cdot\vec v}{\|\vec v\|^2}\vec v', 49, BLACK)
        denominator = self.formula(r'\|\vec v\|^2>0', 34)
        self.new_page('Justifier la formule vectorielle', parallel,
                      perpendicular, coefficient, rule, denominator, gap=0.30)
        self.explain(
            'Voici pourquoi la formule vectorielle utilise la norme au carré. '
            'Le projeté est un multiple de v, noté alpha fois v. Le reste '
            'doit avoir un produit scalaire nul avec v. En développant, '
            'nous obtenons alpha fois la norme de v au carré, égal au '
            'produit de u avec v.', parallel, perpendicular, coefficient)
        self.explain(
            'Puisque v est non nul, sa norme au carré est strictement positive. '
            'Nous pouvons diviser pour trouver alpha, puis multiplier par v. '
            'Une seule division par la norme donnerait une composante signée, '
            'pas ce coefficient multiplicatif.', rule, denominator)

    def _reverse_orientation(self):
        reverse = self.formula(r"\vec v'=(-2,0),\qquad\vec e'=(-1,0)", 40)
        component = self.formula(r"c'=\vec u\cdot\vec e'=3=-c", 43, BLACK)
        same = self.formula(r"\vec p'=3(-1,0)=(-3,0)=\vec p", 43, BLACK)
        length = self.formula(r"\|\vec p'\|=\|\vec p\|=3", 43, BLACK)
        self.new_page('Inverser le sens de référence', reverse, component,
                      same, length, gap=0.48)
        self.explain(
            'Orientons maintenant la même droite vers la gauche. Le vecteur '
            'unitaire devient moins un, zéro. La composante signée devient '
            'plus trois : le projeté suit désormais le sens de référence.',
            reverse, component)
        self.explain(
            'Le vecteur projeté ne change pourtant pas : trois fois moins un, '
            'zéro donne encore moins trois, zéro. Sa longueur reste trois. '
            'Changer l’orientation change la composante signée, mais ni '
            'la droite de projection ni le point projeté.', same, length)

    def _zero_vector(self):
        assumption = self.formula(r'\vec v\ne\vec0,\qquad\vec u=\vec0', 43)
        component = self.formula(r'c=\frac{\vec0\cdot\vec v}{\|\vec v\|}=0', 44)
        projection = self.formula(r'\vec p=\vec0,\qquad\|\vec p\|=0', 44)
        note = self.words('Aucun angle avec le vecteur nul n’est nécessaire.', 29)
        self.new_page('Le vecteur à projeter peut être nul', assumption,
                      component, projection, note, gap=0.50)
        self.explain(
            'La direction v doit toujours être non nulle pour définir la '
            'droite et normaliser sa direction. Le vecteur u, lui, peut '
            'être nul : son produit scalaire avec v vaut alors zéro, '
            'donc sa composante signée vaut zéro.', assumption, component)
        self.explain(
            'Son vecteur projeté et sa longueur valent aussi zéro. '
            'La formule reste valable sans définir un angle avec '
            'ce vecteur nul.', projection, note)

    def _self_check(self):
        vectors = self.formula(r'\vec u=(3,4),\qquad\vec v=(1,2)', 49)
        questions = VGroup(
            self.words('Composante signée, vecteur projeté et longueur ?', 29),
            self.words('Le reste est-il orthogonal à v ?', 29),
        ).arrange(DOWN, buff=0.36)
        self.new_page('À vous : une direction oblique', vectors, questions, gap=0.8)
        self.explain(
            'Reprenons la deuxième question de la section neuf point sept du '
            'cahier. Projetez trois, quatre sur la droite dirigée par un, deux. '
            'Calculez les trois objets, puis contrôlez le produit scalaire '
            'du reste avec v. Gardez les valeurs exactes.',
            vectors, questions, pause_after=6)

    def _answer(self):
        data = self.formula(r'\vec u\cdot\vec v=11,\qquad\|\vec v\|=\sqrt5', 40)
        component = self.formula(r'c=\frac{11}{\sqrt5},\qquad\|\vec p\|=\frac{11}{\sqrt5}', 42, BLACK)
        vector = self.formula(r'\vec p=\frac{11}{5}(1,2)=\left(\frac{11}{5},\frac{22}{5}\right)', 43, BLACK)
        self.new_page('Réponse : calculer les trois objets', data, component,
                      vector, gap=0.50)
        self.explain(
            'Le produit scalaire vaut onze et la norme de v vaut racine de '
            'cinq. La composante signée vaut onze sur racine de cinq. Elle '
            'est positive, donc la longueur a la même valeur. Pour le vecteur, '
            'on divise onze par cinq, puis on multiplie par un, deux.',
            data, component, vector)

    def _check_residual(self):
        parallel = self.formula(r'\vec p=\frac{11}{5}\vec v', 45, BLACK)
        residual = self.formula(r'\vec r=\vec u-\vec p=\left(\frac45,-\frac25\right)', 43)
        check = self.formula(r'\vec r\cdot\vec v=\frac45-\frac45=0', 45, BLACK)
        self.new_page('Réponse : contrôler la projection', parallel,
                      residual, check, gap=0.50)
        self.explain(
            'Vérifions les deux conditions. Le projeté est un multiple de v : '
            'il est donc parallèle à la droite de projection.', parallel)
        self.explain(
            'Le reste vaut quatre cinquièmes, moins deux cinquièmes. '
            'Son produit avec un, deux vaut quatre cinquièmes moins quatre '
            'cinquièmes, donc zéro. Ce contrôle confirme que nous avons '
            'bien construit la projection orthogonale.', residual, check)

    def _closing(self):
        play_lesson_closing(
            self, LESSON_TITLE,
            (
                'Normaliser la direction non nulle.',
                'Distinguer nombre signé et vecteur.',
                'Une longueur prend la valeur absolue.',
            ),
            '\\vec u=(-3,2),\\qquad\\vec v=(2,0)',
            'Calculez la composante, le projeté\net sa longueur, puis contrôlez le reste.',
            recap_spoken='Normalisez la direction non nulle. Distinguez la composante signée du vecteur projeté. La longueur est la valeur absolue de la composante, et le reste doit être orthogonal à la direction.',
            practice_spoken='Reprenez les vecteurs moins trois, deux et deux, zéro. Retrouvez la composante signée, le vecteur projeté et sa longueur, puis contrôlez l’orthogonalité du reste.',
            narration=None if self.silent else self.chapter_narration,
        )

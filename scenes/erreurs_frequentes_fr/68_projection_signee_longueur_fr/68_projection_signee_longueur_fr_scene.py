"""Separate signed component, vector projection and its nonnegative length."""
from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    LEFT,
    RED_D,
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

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene

config.background_color = WHITE


class ProjectionSigneeLongueurFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._geometric_projection()
        self._signed_component()
        self._three_objects()
        self._derive_projection()
        self._reverse_orientation()
        self._self_check()
        self._answer()
        self._check_residual()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        vectors = self.formula(r'\vec u=(-3,2),\qquad\vec v=(2,0)', 46)
        dot = self.formula(r'\vec u\cdot\vec v=-6', 49, BLUE_D)
        mistake = self.words('La projection aurait une longueur de −6 ?', 30, RED_D)
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
        first = self.formula(r'\vec u=(-3,2)', 39, BLUE_D)
        reference = self.formula(r'\vec v=(2,0)', 39, GREEN_D)
        support = self.formula(r'\text{Droite }\mathbb R\vec v', 35)
        projected_value = self.formula(r'\vec p=(-3,0)', 39, RED_D)
        notes = VGroup(first, reference, support, projected_value).arrange(DOWN, buff=0.48)
        body = VGroup(diagram, notes).arrange(RIGHT, buff=0.55)
        self.new_page('Projeter sur toute une droite', body)

        origin, tip, foot = axes.c2p(0, 0), axes.c2p(-3, 2), axes.c2p(-3, 0)
        u = Arrow(origin, tip, color=BLUE_D, buff=0, stroke_width=3)
        v = Arrow(origin, axes.c2p(2, 0), color=GREEN_D, buff=0, stroke_width=4)
        projection = Arrow(origin, foot, color=RED_D, buff=0, stroke_width=4)
        drop = DashedLine(tip, foot, color=BLACK, stroke_width=2)
        right_angle = RightAngle(Line(foot, origin), Line(foot, tip),
                                 length=0.18, color=BLACK, stroke_width=2)
        probe = Dot(tip, color=RED_D, radius=0.075)
        origin_dot = Dot(origin, color=BLACK, radius=0.045)
        u_label = self.formula(r'\vec u', 28, BLUE_D).next_to(tip, UP, buff=0.12)
        v_label = self.formula(r'\vec v', 28, GREEN_D).next_to(v, UP, buff=0.16)
        p_label = self.formula(r'\vec p', 28, RED_D).next_to(projection, DOWN, buff=0.17)
        diagram.add(u, v, projection, drop, right_angle, probe, origin_dot,
                    u_label, v_label, p_label)
        self.explain(
            'Les deux axes ont la même unité. Le vecteur vert oriente la '
            'droite horizontale vers la droite. Nous projetons sur toute '
            'cette droite, y compris sa partie négative, et pas seulement '
            'sur la demi-droite verte.', axes, labels, u, v, origin_dot,
            u_label, v_label, first, reference, support)
        self.explain(
            'Depuis l’extrémité du vecteur bleu, descendons perpendiculairement '
            'vers la droite de projection. Le point atteint a pour coordonnées '
            'moins trois, zéro.', probe)
        self.play(Create(drop), probe.animate.move_to(foot), run_time=1.8)
        self.play(Create(projection), Create(right_angle), run_time=1.0)
        self.explain(
            'Le vecteur projeté part de l’origine et va vers ce point. '
            'Il est dirigé vers la gauche, donc à l’opposé du vecteur vert. '
            'Sa longueur vaut trois, même si sa composante orientée sera négative.',
            p_label, projected_value)

    def _signed_component(self):
        norm = self.formula(r'\|\vec v\|=2,\qquad\vec e=\frac{\vec v}{\|\vec v\|}=(1,0)', 42)
        scalar = self.formula(r'c=\vec u\cdot\vec e=(-3)(1)+2(0)=-3', 44, BLUE_D)
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
        component = self.formula(r'\text{Composante signée : }c=-3', 40, BLUE_D)
        vector = self.formula(r'\text{Vecteur : }\vec p=c\vec e=(-3,0)', 40, RED_D)
        length = self.formula(r'\text{Longueur : }\|\vec p\|=|c|=3', 40, GREEN_D)
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
        rule = self.formula(r'\vec p=\frac{\vec u\cdot\vec v}{\|\vec v\|^2}\vec v', 49, BLUE_D)
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
        component = self.formula(r"c'=\vec u\cdot\vec e'=3=-c", 43, BLUE_D)
        same = self.formula(r"\vec p'=3(-1,0)=(-3,0)=\vec p", 43, RED_D)
        length = self.formula(r"\|\vec p'\|=\|\vec p\|=3", 43, GREEN_D)
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
        component = self.formula(r'c=\frac{11}{\sqrt5},\qquad\|\vec p\|=\frac{11}{\sqrt5}', 42, BLUE_D)
        vector = self.formula(r'\vec p=\frac{11}{5}(1,2)=\left(\frac{11}{5},\frac{22}{5}\right)', 43, RED_D)
        self.new_page('Réponse : calculer les trois objets', data, component,
                      vector, gap=0.50)
        self.explain(
            'Le produit scalaire vaut onze et la norme de v vaut racine de '
            'cinq. La composante signée vaut onze sur racine de cinq. Elle '
            'est positive, donc la longueur a la même valeur. Pour le vecteur, '
            'on divise onze par cinq, puis on multiplie par un, deux.',
            data, component, vector)

    def _check_residual(self):
        parallel = self.formula(r'\vec p=\frac{11}{5}\vec v', 45, RED_D)
        residual = self.formula(r'\vec r=\vec u-\vec p=\left(\frac45,-\frac25\right)', 43)
        check = self.formula(r'\vec r\cdot\vec v=\frac45-\frac45=0', 45, GREEN_D)
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

    def _takeaway(self):
        assumption = self.formula(r'\vec v\ne\vec0,\qquad\vec e=\vec v/\|\vec v\|', 38)
        rule = self.formula(r'c=\vec u\cdot\vec e,\qquad\vec p=c\vec e,\qquad\|\vec p\|=|c|', 40)
        zero = self.formula(r'\vec u=\vec0:\quad c=0,\quad\vec p=\vec0,\quad\|\vec p\|=0', 35)
        source = self.words('Manuel 9.4 et 9.7 · Cahier 9.7 A–B', 28)
        self.new_page('Nommer ce que l’on calcule', assumption, rule, zero,
                      source, gap=0.45)
        self.explain(
            'Demandez toujours si vous cherchez un nombre signé, un vecteur '
            'ou une longueur. Normalisez la direction, puis gardez le signe '
            'pour la composante. La longueur prend la valeur absolue. '
            'La direction v doit être non nulle.', assumption, rule)
        self.explain(
            'Le vecteur u, lui, peut être nul : sa composante, son projeté '
            'et la longueur valent alors zéro. La formule reste valable '
            'sans définir un angle avec ce vecteur nul.', zero, source)

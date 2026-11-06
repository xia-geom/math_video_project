"""An unbounded feasible region can still have an attained finite optimum."""
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
    Dot,
    Line,
    Polygon,
    Rectangle,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene

config.background_color = WHITE


class RegionNonBorneeOptimumFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._unbounded_region()
        self._minimum_value()
        self._whole_edge()
        self._finite_maximum()
        self._unbounded_objective()
        self._self_check()
        self._answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        constraints = self.formula(r'D:\quad x\ge0,\qquad y\ge0,\qquad x+y\ge2', 44)
        domain = self.formula(r'(x,y)\in\mathbb R^2', 38)
        guess = self.words('Région non bornée : aucun optimum ?', 31, RED_D)
        objectives = self.formula(r'\min(x+y)\;?\qquad\max(-x-y)\;?\qquad\max(x+y)\;?', 36)
        self.new_page('La région suffit-elle pour conclure ?', constraints,
                      domain, guess, objectives, gap=0.46)
        self.explain(
            'Nous travaillons avec deux variables réelles, positives ou nulles, '
            'dont la somme vaut au moins deux. La région réalisable se prolonge '
            'sans limite. Faut-il en déduire qu’aucun problème d’optimisation '
            'ne peut y avoir de solution ?', constraints, domain, guess)
        self.explain(
            'Gardons exactement les mêmes contraintes, mais changeons la '
            'fonction objectif et le sens de l’optimisation. Nous allons '
            'obtenir un minimum fini, un maximum fini et un cas sans maximum.',
            objectives)

    def _region_diagram(self):
        # Both axes have a 0.62 screen-unit scale. The fill is a cropped window,
        # not a closed polygonal constraint: the two boundary arrows continue.
        axes = Axes(
            x_range=[0, 6.5, 1], y_range=[0, 6.5, 1],
            x_length=4.03, y_length=4.03,
            axis_config={'color': BLACK, 'include_tip': False, 'stroke_width': 1.4},
        )
        canvas = Rectangle(width=5.05, height=4.8, stroke_opacity=0, fill_opacity=0)
        axes.move_to(canvas)
        fill = Polygon(
            *(axes.c2p(x, y) for x, y in [(0, 2), (0, 6.2), (6.2, 6.2), (6.2, 0), (2, 0)]),
            stroke_opacity=0, fill_color=BLUE_D, fill_opacity=0.10,
        )
        edge = Line(axes.c2p(0, 2), axes.c2p(2, 0), color=BLUE_D, stroke_width=3)
        rays = VGroup(
            Arrow(axes.c2p(0, 2), axes.c2p(0, 6.2), color=BLUE_D, buff=0, stroke_width=3),
            Arrow(axes.c2p(2, 0), axes.c2p(6.2, 0), color=BLUE_D, buff=0, stroke_width=3),
        )
        labels = VGroup(
            self.formula('x', 25).next_to(axes.x_axis, RIGHT, buff=0.10),
            self.formula('y', 25).next_to(axes.y_axis, UP, buff=0.10),
            self.formula('0', 24).next_to(axes.c2p(0, 0), DOWN + LEFT, buff=0.12),
            *[self.formula(str(value), 24).next_to(axes.c2p(value, 0), DOWN, buff=0.14)
              for value in (2, 6)],
            *[self.formula(str(value), 24).next_to(axes.c2p(0, value), LEFT, buff=0.14)
              for value in (2, 6)],
        )
        diagram = VGroup(canvas, fill, axes, edge, rays, labels)
        return diagram, axes

    def _unbounded_region(self):
        diagram, axes = self._region_diagram()
        family = self.formula(r'M_t=(t,2),\quad t\ge0', 37)
        feasible = self.formula(r't+2\ge2\quad\Longrightarrow\quad M_t\in D', 34)
        growth = self.formula(r't\longrightarrow+\infty', 45, BLUE_D)
        note = VGroup(self.words('Le dessin est une fenêtre', 28),
                      self.words('sur une région qui continue.', 28)).arrange(DOWN, buff=0.17)
        notes = VGroup(family, feasible, growth, note).arrange(DOWN, buff=0.48)
        body = VGroup(diagram, notes).arrange(RIGHT, buff=0.55)
        self.new_page('Montrer que la région est non bornée', body)
        visible_region = tuple(diagram[1:])
        point = Dot(axes.c2p(1, 2), radius=0.08, color=GREEN_D)
        path = Arrow(axes.c2p(1, 2), axes.c2p(5.6, 2), color=GREEN_D,
                     buff=0, stroke_width=3)
        diagram.add(point, path)
        self.explain(
            'La partie bleue conserve le premier quadrant au-dessus de la '
            'droite x plus y égale deux. Les flèches signalent que la région '
            'continue au-delà de notre fenêtre. Les bords du dessin '
            'ne sont pas des contraintes supplémentaires.', *visible_region, note)
        self.explain(
            'Pour le prouver sans dépendre du dessin, prenons les points '
            'de coordonnées t, deux, avec t positif ou nul. Ils respectent '
            'toutes les contraintes. Leur abscisse peut être aussi grande '
            'que l’on veut.', family, feasible, point)
        self.play(Create(path), point.animate.move_to(axes.c2p(5.6, 2)), run_time=1.8)
        self.explain(
            'Aucune borne finie ne contient donc toute cette famille de '
            'points. La région est bien non bornée. Cela décrit ses '
            'positions possibles, pas encore les valeurs d’un objectif.', growth)

    def _minimum_value(self):
        diagram, axes = self._region_diagram()
        level = Line(axes.c2p(0, 5), axes.c2p(5, 0), color=GREEN_D, stroke_width=3)
        diagram.add(level)
        objective = self.formula(r'P(x,y)=x+y', 42)
        bound = self.formula(r'P(x,y)\ge2', 46, BLUE_D)
        witness = self.formula(r'P(2,0)=2', 44, GREEN_D)
        result = self.words('Minimum atteint : 2.', 29)
        notes = VGroup(objective, bound, witness, result).arrange(DOWN, buff=0.55)
        body = VGroup(diagram, notes).arrange(RIGHT, buff=0.65)
        self.new_page('Un minimum malgré la région non bornée', body)
        self.explain(
            'Minimisons d’abord x plus y. Les droites de niveau ont pour '
            'équation x plus y égale une constante. Faisons descendre '
            'cette constante : la droite verte se rapproche de l’origine.',
            diagram, objective)
        self.play(level.animate.put_start_and_end_on(axes.c2p(0, 2), axes.c2p(2, 0)),
                  run_time=1.8)
        self.explain(
            'La contrainte impose directement une valeur au moins égale '
            'à deux. Le point deux, zéro est autorisé et atteint exactement '
            'deux. Nous avons une borne et un point qui l’atteint : '
            'le minimum existe et vaut deux.', bound, witness, result)

    def _whole_edge(self):
        diagram, axes = self._region_diagram()
        edge = Line(axes.c2p(2, 0), axes.c2p(0, 2), color=GREEN_D, stroke_width=5)
        ends = VGroup(Dot(axes.c2p(2, 0), radius=0.065, color=GREEN_D),
                      Dot(axes.c2p(0, 2), radius=0.065, color=GREEN_D))
        diagram.add(edge, ends)
        family = self.formula(r'N_s=(s,2-s),\quad0\le s\le2', 34)
        value = self.formula(r'P(N_s)=s+(2-s)=2', 37, GREEN_D)
        conclusion = VGroup(self.words('Tous les points du segment', 28),
                            self.words('sont optimaux.', 28)).arrange(DOWN, buff=0.18)
        notes = VGroup(family, value, conclusion).arrange(DOWN, buff=0.65)
        body = VGroup(diagram, notes).arrange(RIGHT, buff=0.6)
        self.new_page('Toute une arête est optimale', body)
        probe = Dot(axes.c2p(2, 0), radius=0.095, color=RED_D)
        diagram.add(probe)
        self.explain(
            'Le minimum n’appartient pas seulement au point deux, zéro. '
            'Tous les points du segment reliant deux, zéro à zéro, deux '
            'ont une somme de coordonnées égale à deux.', diagram, family)
        self.play(probe.animate.move_to(axes.c2p(0, 2)), run_time=2)
        self.explain(
            'L’écriture s, deux moins s décrit tout ce segment lorsque '
            's varie entre zéro et deux. Les deux coordonnées restent '
            'positives ou nulles, et l’objectif vaut toujours deux. '
            'Nous obtenons une infinité de solutions optimales.', value, conclusion)

    def _finite_maximum(self):
        objective = self.formula(r'Q(x,y)=-x-y', 49)
        bound = self.formula(r'x+y\ge2\quad\Longrightarrow\quad Q(x,y)\le-2', 41)
        attained = self.formula(r'Q(s,2-s)=-2\qquad(0\le s\le2)', 43, GREEN_D)
        result = self.words('Un maximum fini : −2, sur la même arête.', 29)
        self.new_page('Un maximum peut aussi exister', objective, bound,
                      attained, result, gap=0.48)
        self.explain(
            'Changeons maintenant l’objectif et maximisons moins x moins y. '
            'La même contrainte, multipliée par moins un, donne un objectif '
            'inférieur ou égal à moins deux. Le sens de l’inégalité s’inverse.',
            objective, bound)
        self.explain(
            'Tous les points du segment précédent atteignent moins deux. '
            'C’est bien le maximum, puisque les autres valeurs ne peuvent '
            'pas être plus grandes. Une région non bornée peut donc avoir '
            'un maximum fini et atteint, en plus d’un minimum pour un autre objectif.',
            attained, result)

    def _unbounded_objective(self):
        question = self.formula(r'\text{Maximiser }P(x,y)=x+y', 45)
        family = self.formula(r'M_t=(t,2)\in D\qquad(t\ge0)', 43)
        value = self.formula(r'P(M_t)=t+2\longrightarrow+\infty', 47, BLUE_D)
        verdict = self.words('Aucun maximum : toute valeur peut être dépassée.', 29, RED_D)
        self.new_page('Cette fois, l’objectif est sans borne', question,
                      family, value, verdict, gap=0.48)
        self.explain(
            'Reprenons x plus y, mais cherchons cette fois son maximum. '
            'Les points t, deux sont toujours autorisés. Leur valeur '
            'd’objectif vaut t plus deux et augmente sans limite.',
            question, family, value)
        self.explain(
            'Quelle que soit la valeur proposée, un t assez grand donne '
            'une valeur encore supérieure. Aucun point n’est donc optimal '
            'pour ce maximum. L’infini n’est pas une valeur atteinte : '
            'il décrit ici l’absence de borne supérieure.', verdict)

    def _self_check(self):
        region = self.formula(r'x\ge0,\qquad y\ge0,\qquad2x+y\ge6', 45)
        objective = self.formula(r'\text{Minimiser }C(x,y)=3x+2y', 44)
        prompt = VGroup(self.words('La région est-elle bornée ?', 29),
                        self.words('Le minimum existe-t-il ? Est-il unique ?', 29)).arrange(DOWN, buff=0.35)
        self.new_page('À vous : prouver une borne atteinte', region,
                      objective, prompt, gap=0.6)
        self.explain(
            'Essayez ce nouveau problème, toujours avec des variables réelles. '
            'La somme deux x plus y doit être au moins six. Minimisez '
            'trois x plus deux y. Distinguez le caractère non borné de '
            'la région, l’existence d’un minimum et son éventuelle unicité. '
            'Cherchez une borne que vous pouvez justifier.',
            region, objective, prompt, pause_after=6)

    def _answer(self):
        unbounded = self.formula(r'(3+t,0)\text{ est admissible pour tout }t\ge0', 35)
        bound = self.formula(r'C=\frac32(2x+y)+\frac12y\ge\frac32\cdot6=9', 42)
        equality = self.formula(r'C=9\quad\Longleftrightarrow\quad2x+y=6\text{ et }y=0', 38)
        solution = self.formula(r'(x,y)=(3,0),\qquad C(3,0)=9', 45, GREEN_D)
        note = self.words('Un minimum fini, atteint et unique.', 29)
        self.new_page('Une borne qui identifie la solution', unbounded,
                      bound, equality, solution, note, gap=0.30)
        self.explain(
            'Les points trois plus t, zéro prouvent que la région est '
            'non bornée. Pour l’objectif, réécrivons trois x plus deux y '
            'comme trois demis fois deux x plus y, plus un demi y. '
            'Le premier terme vaut au moins neuf et le second est positif '
            'ou nul. Le coût est donc au moins neuf.', unbounded, bound)
        self.explain(
            'L’égalité exige simultanément deux x plus y égal à six '
            'et y égal à zéro. Il reste uniquement le point trois, zéro. '
            'Il respecte toutes les contraintes et son coût vaut neuf. '
            'Le minimum est donc atteint et unique, malgré la région non bornée.',
            equality, solution, note)

    def _takeaway(self):
        table = self.formula(
            r'\begin{array}{c|c}'
            r'\text{Sur }D&\text{Résultat}\\\hline'
            r'\min(x+y)&2\\'
            r'\max(-x-y)&-2\\'
            r'\max(x+y)&\text{aucun maximum}'
            r'\end{array}', 37,
        )
        rule = self.words('Séparer la région, l’objectif et le sens recherché.', 29, BLUE_D)
        source = VGroup(
            self.words('Manuel 13.4 et 13.7', 28),
            self.words('Cahier 13.4 B et synthèse 13, S2 — transferts', 28),
        ).arrange(DOWN, buff=0.20)
        self.new_page('La même région, trois conclusions', table, rule, source, gap=0.55)
        self.explain(
            'La même région a donné trois conclusions différentes. '
            'Pour prouver un optimum fini, donnez une borne et montrez '
            'qu’elle est atteinte. Pour prouver l’absence de maximum, '
            'construisez une famille admissible dont l’objectif augmente '
            'sans limite.', table, rule)
        self.explain(
            'Le théorème sur les régions polygonales fermées et bornées '
            'garantit des extrema quand la région est non vide. '
            'Si elle est non bornée, on ne peut pas simplement inverser '
            'cette conclusion : il faut étudier l’objectif demandé.', source)

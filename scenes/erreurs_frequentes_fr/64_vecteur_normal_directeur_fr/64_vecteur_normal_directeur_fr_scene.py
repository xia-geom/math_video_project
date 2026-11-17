"""Distinguish the normal to a Cartesian line from a direction along it."""

from manim import (
    BLACK,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Axes,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    RightAngle,
    Tex,
    Text,
    VGroup,
    config,
    linear,
)

from tools import tts
from tools.teaching_chapters import (
    play_chapter_outline,
    play_lesson_closing,
    play_lesson_opening,
)
from tools.teaching_layout import TeachingScene

LESSON_TITLE = 'Normal et directeur'
LESSON_OBJECTIVE = 'Choisir un vecteur directeur\nqui conserve l’équation de la droite.'
CHAPTERS = (
    'Comparer deux déplacements',
    'Justifier et choisir les vecteurs',
    'S’exercer avec une autre droite',
)

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class VecteurNormalDirecteurFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        narration = None if self.silent else self.chapter_narration
        play_lesson_opening(self, LESSON_TITLE, LESSON_OBJECTIVE, narration=narration)
        play_chapter_outline(
            self, CHAPTERS, 0, 'Comparons les déplacements depuis le même point de la droite.',
            narration=narration,
        )
        self._question()
        self._two_displacements()
        self._substitution_check()
        play_chapter_outline(
            self, CHAPTERS, 1, 'Justifions l’orthogonalité et choisissons des vecteurs, même pour une droite verticale.',
            narration=narration,
        )
        self._why_orthogonal()
        self._choose_vectors()
        self._vertical_line()
        play_chapter_outline(
            self, CHAPTERS, 2, 'Essayons une autre équation et vérifions les deux vecteurs.',
            narration=narration,
        )
        self._self_check()
        self._self_check_answer()
        self._closing()

    def _question(self):
        line = self.formula(r"d:\quad 2x-3y=6", 52)
        temptation = self.formula(r"(2,-3)\quad\text{directeur ?}", 42, BLACK)
        point = self.formula(r"P=(3,0)\in d", 43)
        question = self.words("Quel déplacement reste sur la droite ?", 30)
        self.new_page("Normal ou directeur ?", line, temptation, point, question, gap=0.48)
        self.explain(
            f"Dans l'équation deux x moins trois {tts.char('y')} égale six, nous lisons "
            "les coefficients deux et moins trois. Peut-on les utiliser "
            "comme direction de la droite ? Le manuel appelle ce vecteur "
            "un normal. Vérifions ce que cela signifie par un déplacement.",
            line, temptation,
        )
        self.explain(
            "Le point P, de coordonnées trois et zéro, appartient à la droite. "
            "Partons de ce même point et comparons les déplacements "
            "trois, deux et deux, moins trois.",
            point, question,
        )

    def _two_displacements(self):
        # Equal units preserve the right angle between (3, 2) and (2, -3).
        unit = 0.56
        axes = Axes(
            x_range=[-0.5, 7, 1], y_range=[-3.5, 3, 1],
            x_length=7.5 * unit, y_length=6.5 * unit,
            axis_config={"color": BLACK, "include_tip": False, "stroke_width": 1.5},
        )
        line = Line(axes.c2p(-0.5, -7 / 3), axes.c2p(7, 8 / 3), color=BLACK, stroke_width=2)
        start = axes.c2p(3, 0)
        direction = Arrow(start, axes.c2p(6, 2), buff=0, color=BLACK, stroke_width=5)
        normal = DashedLine(start, axes.c2p(5, -3), color=BLACK,
                            stroke_width=4, dash_length=0.12).add_tip(tip_length=0.18)
        corner = RightAngle(direction, normal, length=0.20, color=BLACK, stroke_width=2)
        point = Dot(start, radius=0.065, color=BLACK)
        point_label = self.formula("P", 28).next_to(point, UP + LEFT, buff=0.10)
        direction_label = self.formula(r"\vec v", 30, BLACK).next_to(
            direction.get_center(), UP, buff=0.12,
        )
        normal_label = self.formula(r"\vec n", 30, BLACK).next_to(
            normal.get_center(), RIGHT, buff=0.15,
        )
        labels = VGroup(
            self.formula("x", 26).next_to(axes.x_axis, RIGHT, buff=0.12),
            self.formula("y", 26).next_to(axes.y_axis, UP, buff=0.12),
            self.formula("3", 24).next_to(axes.c2p(3, 0), DOWN, buff=0.10),
            self.formula("6", 24).next_to(axes.c2p(6, 0), DOWN, buff=0.10),
            self.formula("2", 24).next_to(axes.c2p(0, 2), LEFT, buff=0.10),
            self.formula("-3", 24).next_to(axes.c2p(0, -3), LEFT, buff=0.10),
        )
        probe = Dot(start, radius=0.085, color=BLACK)
        graph = VGroup(axes, line, direction, normal, corner, point, point_label,
                       direction_label, normal_label, labels, probe)
        point_info = self.formula(r"P=(3,0)", 38)
        direction_info = self.formula(r"\vec v=(3,2)", 38, BLACK)
        normal_info = self.formula(r"\vec n=(2,-3)", 38, BLACK)
        info = VGroup(point_info, direction_info, normal_info).arrange(DOWN, buff=0.65)
        diagram = VGroup(graph, info).arrange(RIGHT, buff=0.75)
        self.new_page("Deux déplacements depuis le même point", diagram)
        self.explain(
            "Les deux axes ont la même unité graphique. La flèche pleine "
            "représente le directeur trois, deux : trois unités vers la droite et deux "
            "vers le haut. Le point se déplace le long de la droite.",
            axes, line, labels, point, point_label, direction, direction_label,
            point_info, direction_info, probe,
        )
        self.play(probe.animate.move_to(axes.c2p(6, 2)), run_time=2, rate_func=linear)
        self.explain(
            "En pointillés, le normal deux, moins trois part du même point. "
            "Il est perpendiculaire au directeur. Suivre cette flèche "
            "fait quitter la droite, au lieu de la parcourir.",
            normal, normal_label, corner, normal_info,
        )
        self.play(FadeOut(probe), run_time=0.25)
        probe.move_to(axes.c2p(3, 0)).set_fill(WHITE, opacity=1).set_stroke(BLACK, width=2, opacity=1)
        self.play(FadeIn(probe), run_time=0.25)
        self.play(probe.animate.move_to(axes.c2p(5, -3)), run_time=2, rate_func=linear)
        self.wait(0.8)

    def _substitution_check(self):
        start = self.formula(r"P=(3,0):\qquad 2(3)-3(0)=6", 39)
        along = self.formula(r"P+\vec v=(6,2):\qquad 2(6)-3(2)=6", 39, BLACK)
        across = self.formula(r"P+\vec n=(5,-3):\quad 2(5)-3(-3)=19\ne6", 37, BLACK)
        conclusion = self.words("Un directeur conserve l'équation de la droite.", 29)
        self.new_page("Contrôler les points obtenus", start, along, across, conclusion, gap=0.52)
        self.explain(
            "La substitution confirme le dessin. Au départ, deux fois trois "
            "moins trois fois zéro vaut six. Après le déplacement selon le directeur, "
            "nous obtenons six, deux : douze moins six vaut encore six. "
            "Ce nouveau point est sur la droite.",
            start, along,
        )
        self.explain(
            "Après le déplacement selon le normal, le point cinq, moins trois donne "
            "dix plus neuf, soit dix-neuf. L'équation n'est plus satisfaite. "
            "Lire les coefficients donne donc ici le normal, et non le directeur.",
            across, conclusion,
        )

    def _why_orthogonal(self):
        assumptions = self.formula(r"(A,B)\ne(0,0),\qquad \vec v=(v_x,v_y)\ne\vec0", 34)
        point = self.formula(r"P=(x_0,y_0),\qquad Ax_0+By_0=C", 38)
        substituted = self.formula(
            r"A(x_0+tv_x)+B(y_0+tv_y)=C+t(Av_x+Bv_y)", 36,
        )
        condition = self.formula(r"P+t\vec v\in d\ \text{pour tout }t\in\mathbb R"
                                 r"\quad\Longleftrightarrow\quad Av_x+Bv_y=0", 34)
        dot = self.formula(r"(A,B)\cdot\vec v=0", 43, BLACK)
        self.new_page("Pourquoi le produit scalaire est nul", assumptions, point,
                      substituted, condition, dot, gap=0.30)
        self.explain(
            f"Prenons maintenant une droite A x plus B {tts.char('y')} égale C, avec A et B non tous deux "
            "nuls. Le point P est sur cette droite. Un déplacement de t fois le vecteur v "
            f"remplace ses coordonnées par x indice zéro plus t fois v indice x, et {tts.char('y')} "
            f"indice zéro plus t fois v indice {tts.char('y')}.",
            assumptions, point, substituted,
        )
        self.explain(
            "En développant, le résultat est C plus t multiplié par la somme de A fois v "
            f"indice x et de B fois v indice {tts.char('y')}. Pour rester égal à C pour toute valeur de "
            "t, ce dernier coefficient doit être nul. C'est exactement le produit scalaire "
            "du normal A, B avec le directeur. Le directeur est non nul : le vecteur zéro "
            "ne permettrait pas de parcourir la droite.",
            condition, dot,
        )

    def _choose_vectors(self):
        line = self.formula(r"Ax+By=C,\qquad (A,B)\ne(0,0)", 40)
        normal = self.formula(r"\vec n=(A,B)\quad\text{normal}", 43, BLACK)
        direction = self.formula(r"\vec v=(-B,A)\quad\text{directeur}", 43, BLACK)
        check = self.formula(r"A(-B)+BA=0", 42)
        multiples = self.words("Tout multiple non nul garde le même rôle.", 29)
        self.new_page("Choisir puis vérifier les vecteurs", line, normal, direction,
                      check, multiples, gap=0.32)
        self.explain(
            "Les coefficients A et B donnent un normal. Pour obtenir un "
            "directeur, échangeons les deux composantes et changeons le signe "
            "de l'une : moins B, A. Le produit scalaire vaut moins A B "
            "plus B A, donc zéro. Dans notre exemple, cela donne trois, deux.",
            line, normal, direction, check,
        )
        self.explain(
            "Ces choix ne sont pas uniques. Un multiple non nul d'un directeur "
            "reste directeur; son opposé parcourt la même droite dans l'autre "
            "sens. Un multiple non nul du normal reste normal. Le rôle du "
            "vecteur ne dépend pas de sa longueur, tant qu'il n'est pas nul.",
            multiples,
        )

    def _vertical_line(self):
        unit = 0.58
        axes = Axes(
            x_range=[0, 6, 1], y_range=[-2, 3, 1],
            x_length=6 * unit, y_length=5 * unit,
            axis_config={"color": BLACK, "include_tip": False, "stroke_width": 1.5},
        )
        line = Line(axes.c2p(3, -2), axes.c2p(3, 3), color=BLACK, stroke_width=2)
        start = axes.c2p(3, 0)
        normal = DashedLine(start, axes.c2p(5, 0), color=BLACK,
                            stroke_width=4, dash_length=0.12).add_tip(tip_length=0.18)
        direction = Arrow(start, axes.c2p(3, 1), buff=0, color=BLACK, stroke_width=5)
        point = Dot(start, radius=0.065, color=BLACK)
        labels = VGroup(
            self.formula("x", 26).next_to(axes.x_axis, RIGHT, buff=0.12),
            self.formula("y", 26).next_to(axes.y_axis, UP, buff=0.12),
            self.formula("3", 26).next_to(start, DOWN + RIGHT, buff=0.13),
            self.formula(r"\vec n", 29, BLACK).next_to(normal.get_center(), UP, buff=0.14),
            self.formula(r"\vec v", 29, BLACK).next_to(direction.get_center(), LEFT, buff=0.14),
        )
        graph = VGroup(axes, line, normal, direction, point, labels)
        equation = self.formula(r"2x+0y=6\quad\Longleftrightarrow\quad x=3", 35)
        vectors = self.formula(r"\vec n=(2,0),\quad\vec v=(0,1)", 35)
        points = self.formula(r"(x,y)=(3,0)+t(0,1)", 35)
        info = VGroup(equation, vectors, points).arrange(DOWN, buff=0.65)
        diagram = VGroup(graph, info).arrange(RIGHT, buff=0.65)
        self.new_page("Le cas d'une droite verticale", diagram)
        self.explain(
            "La même méthode fonctionne pour deux x égale six. Le normal "
            "deux, zéro est horizontal. Le directeur zéro, un est vertical. "
            "Il est un multiple non nul du choix zéro, deux fourni par "
            "la formule précédente.",
            axes, line, normal, direction, point, labels, equation, vectors,
        )
        self.explain(
            "En partant de trois, zéro et en ajoutant t fois zéro, un, "
            "l'abscisse reste trois tandis que l'ordonnée varie librement. "
            "Nous décrivons toute la droite verticale, sans diviser par "
            f"le coefficient de {tts.char('y')} et sans lui attribuer une pente.",
            points,
        )

    def _self_check(self):
        line = self.formula(r"d:\quad 3x-2y+7=0", 51)
        point = self.formula(r"P=(-1,2)\in d", 42)
        first = self.words("Donnez un normal n et un directeur v non nuls.", 29)
        second = self.words("Vérifiez n · v = 0, puis P + v appartient à d.", 29)
        self.new_page("À vous : changer les coefficients", line, point, first, second, gap=0.50)
        self.explain(
            "À vous, avec l'exercice dix point deux A du cahier. "
            "Donnez un normal et un directeur non nuls de cette droite. "
            "Vérifiez leur produit scalaire, puis partez du point moins un, "
            "deux pour vérifier qu'ajouter votre directeur conserve l'équation. "
            "Plusieurs choix de vecteurs peuvent convenir.",
            line, point, first, second, pause_after=6,
        )

    def _self_check_answer(self):
        vectors = self.formula(r"\vec n=(3,-2),\qquad\vec v=(2,3)", 44)
        dot = self.formula(r"\vec n\cdot\vec v=3(2)-2(3)=0", 43, BLACK)
        start = self.formula(r"3(-1)-2(2)+7=0", 39)
        point = self.formula(r"P+\vec v=(1,5):\qquad3(1)-2(5)+7=0", 39)
        self.new_page("Deux contrôles complémentaires", vectors, dot, start, point, gap=0.48)
        self.explain(
            "Un choix est le normal trois, moins deux et le directeur deux, "
            "trois. Leur produit scalaire vaut six moins six, donc zéro. "
            "Le vecteur directeur est bien perpendiculaire au normal.",
            vectors, dot,
        )
        self.explain(
            "Le point initial satisfait l'équation : moins trois moins quatre "
            "plus sept vaut zéro. Après le déplacement, nous obtenons un, "
            "cinq, et trois moins dix plus sept vaut encore zéro. "
            "L'orthogonalité et le test d'appartenance racontent ainsi "
            "le même déplacement sur la droite.",
            start, point,
        )

    def _closing(self):
        # Les références détaillées restent dans le catalogue et le README.
        play_lesson_closing(
            self, LESSON_TITLE,
            (
                'Les coefficients donnent un vecteur normal.',
                'Un directeur non nul lui est perpendiculaire.',
                'Déplacer un point permet de vérifier le choix.',
            ),
            'd:\\quad3x-2y+7=0,\\qquad P=(-1,2)',
            'Donner un normal et un directeur non nuls.\nVérifier l’orthogonalité et le déplacement de P.',
            recap_spoken='Les coefficients d’une équation de droite donnent un vecteur normal. Un directeur non nul lui est perpendiculaire. Déplacer un point connu de la droite permet de vérifier ce choix.',
            practice_spoken=f'Reprenez trois x moins deux {tts.char("y")} plus sept égale zéro, et le point P de coordonnées moins un, deux. Donnez un normal et un directeur non nuls. Vérifiez l’orthogonalité et qu’ajouter le directeur à P garde un point sur la droite.',
            narration=None if self.silent else self.chapter_narration,
        )

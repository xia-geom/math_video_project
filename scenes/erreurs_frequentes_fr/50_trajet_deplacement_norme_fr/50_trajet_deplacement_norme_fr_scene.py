"""MAT0339, manuel 9.2–9.3 et cahier 9.2 C : trajet et déplacement."""
from manim import (
    BLACK,
    DOWN,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeOut,
    MathTex,
    NumberLine,
    Rectangle,
    Square,
    Tex,
    Text,
    VGroup,
    config,
)

from tools.teaching_chapters import (
    play_chapter_outline,
    play_lesson_closing,
    play_lesson_opening,
)
from tools.teaching_layout import TeachingScene, panel

LESSON_TITLE = 'Trajet et déplacement'
LESSON_OBJECTIVE = 'Distinguer la longueur du trajet\nde la norme du déplacement total.'
CHAPTERS = (
    'Comparer deux longueurs',
    'Comprendre la règle générale',
    'Calculer avec les composantes',
)

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class TrajetDeplacementNormeFR(TeachingScene):
    """Additionner les déplacements avant de prendre la norme du déplacement total."""

    def construct(self):
        self.setup_narration()
        narration = None if self.silent else self.chapter_narration
        play_lesson_opening(
            self, LESSON_TITLE, LESSON_OBJECTIVE, narration=narration,
        )
        play_chapter_outline(
            self, CHAPTERS, 0, 'Comparons le détour parcouru et la liaison directe.',
            narration=narration,
        )
        self._question()
        self._right_angle_trip()
        play_chapter_outline(
            self, CHAPTERS, 1, 'Examinons un aller-retour, puis l’inégalité triangulaire.',
            narration=narration,
        )
        self._return_home()
        self._general_rule()
        play_chapter_outline(
            self, CHAPTERS, 2, 'À vous de calculer le déplacement avant de prendre sa norme.',
            narration=narration,
        )
        self._self_check()
        self._takeaway(narration=narration)

    def _question(self):
        vectors = self.formula(r'\vec u=(3,0),\qquad\vec v=(0,4)', 44)
        temptation = self.formula(r'\|\vec u+\vec v\|\overset{?}{=}3+4=7', 50)
        prompt = self.words('Distance parcourue ou distance au point de départ ?', 29)
        self.new_page('Quelle longueur mesure-t-on ?', vectors, temptation, prompt)
        self.explain(
            'Une personne avance de trois mètres horizontalement, puis de quatre mètres verticalement. Elle a parcouru sept mètres. Est-elle aussi à sept mètres de son point de départ ? Les mêmes déplacements permettent de poser deux questions différentes.',
            vectors, temptation, hold=2,
        )
        self.explain(
            'La distance parcourue additionne les longueurs des étapes. Le déplacement total relie seulement le départ à l’arrivée. Sa norme mesure la longueur de cette liaison directe. Dessinons les deux trajets avec la même échelle sur les axes.',
            prompt, hold=2,
        )

    def _right_angle_trip(self):
        # Both axes use exactly 0.75 screen units per mathematical unit.
        axes = Axes(
            x_range=[0, 4, 1], y_range=[0, 5, 1],
            x_length=3.0, y_length=3.75,
            axis_config={'color': BLACK, 'include_tip': False, 'stroke_width': 1.5},
        )
        canvas = Rectangle(width=4.8, height=4.45, stroke_opacity=0)
        axes.move_to(canvas)
        diagram = VGroup(canvas, axes)
        path_label = self.words('Les deux étapes', 29)
        path_sum = self.formula(r'3+4=7\ \mathrm{m}', 40, BLACK)
        displacement = self.formula(r'\vec u+\vec v=(3,4)', 35)
        direct = self.formula(r'\sqrt{3^2+4^2}=5\ \mathrm{m}', 37, BLACK)
        explanation = VGroup(path_label, path_sum, displacement, direct).arrange(DOWN, buff=0.5)
        row = VGroup(diagram, explanation).arrange(RIGHT, buff=0.65)
        self.new_page('Un détour de sept mètres', row)
        start = axes.c2p(0, 0)
        elbow = axes.c2p(3, 0)
        finish = axes.c2p(3, 4)
        dot = Dot(start, radius=0.085, color=BLACK)
        first = Arrow(start, elbow, color=BLACK, buff=0, stroke_width=4)
        second = Arrow(elbow, finish, color=BLACK, buff=0, stroke_width=4)
        horizontal_label = self.formula('3', 31, BLACK).next_to(first, DOWN, buff=0.15)
        vertical_label = self.formula('4', 31, BLACK).next_to(second, RIGHT, buff=0.16)
        diagram.add(dot, first, second, horizontal_label, vertical_label)
        self.explain(
            'Le point mobile représente la personne. Partons de l’origine et suivons réellement les deux déplacements : trois unités vers la droite, puis quatre unités vers le haut. Chaque unité a la même longueur horizontale et verticale.',
            axes, dot, path_label, hold=2,
        )
        self.play(Create(first), dot.animate.move_to(elbow), run_time=1.6)
        self.explain('La première étape mesure trois mètres.', horizontal_label, hold=1)
        self.play(Create(second), dot.animate.move_to(finish), run_time=1.6)
        self.explain(
            'La seconde mesure quatre mètres. Additionner ces longueurs donne bien sept mètres parcourus. Cette somme décrit le chemin en deux étapes, avec son virage.',
            vertical_label, path_sum, hold=2,
        )
        diagonal = DashedLine(
            start, finish, color=BLACK, dash_length=0.18, stroke_width=4,
        ).add_tip(tip_length=0.18)
        right_angle = Square(side_length=0.16, stroke_color=BLACK, stroke_width=2)
        right_angle.move_to(elbow + 0.08 * (-RIGHT + UP))
        diagram.add(diagonal, right_angle)
        self.play(Create(diagonal), Create(right_angle), run_time=1.2)
        self.explain(
            'La flèche en pointillés va directement du départ à l’arrivée. Les composantes s’additionnent : trois, zéro, plus zéro, quatre, donne trois, quatre. Le triangle est rectangle, donc Pythagore donne une longueur de cinq mètres.',
            displacement, direct, hold=2,
        )

    def _return_home(self):
        line = NumberLine(
            x_range=[0, 6, 1], length=6,
            include_numbers=True, color=BLACK, font_size=26,
        )
        line.numbers.set_color(BLACK)
        canvas = Rectangle(width=8, height=1.6, stroke_opacity=0)
        diagram = VGroup(canvas, line.move_to(canvas))
        distance = self.formula(r'\text{Trajet : }5+5=10\ \mathrm{m}', 42, BLACK)
        net = self.formula(r'\text{Déplacement : }(5,0)+(-5,0)=(0,0)', 37)
        norm = self.formula(r'\|(0,0)\|=0', 42, BLACK)
        self.new_page('Revenir au point de départ', diagram, distance, net, norm, gap=0.4)
        start, finish = line.n2p(0), line.n2p(5)
        dot = Dot(start, color=BLACK, radius=0.10)
        outward = Arrow(start, finish, color=BLACK, buff=0, stroke_width=4)
        returning = Arrow(finish, start, color=BLACK, buff=0, stroke_width=4)
        diagram.add(dot, outward, returning)
        self.explain(
            'Un aller-retour rend la distinction encore plus nette. On avance de cinq mètres, puis on revient exactement au départ. Regardez le point faire le voyage dans les deux sens.',
            line, dot, hold=2,
        )
        self.play(Create(outward), dot.animate.move_to(finish), run_time=1.5)
        self.play(FadeOut(outward), Create(returning), dot.animate.move_to(start), run_time=1.5)
        # The retired arrow must also leave the page's group before its exit fade.
        diagram.remove(outward)
        self.explain(
            'Le trajet mesure dix mètres, mais le déplacement total est le vecteur nul. Sa norme vaut zéro. Les longueurs des étapes restent positives ; les déplacements, eux, tiennent compte du sens et peuvent se compenser.',
            distance, net, norm, hold=2,
        )

    def _general_rule(self):
        rule = panel(self.formula(r'\|\vec u+\vec v\|\le\|\vec u\|+\|\vec v\|', 43), width=9)
        meaning = self.words('Le trajet direct ne dépasse pas le détour.', 31)
        equality = VGroup(
            self.words('Égalité : même direction et même sens,', 29),
            self.words('ou l’un des déplacements est nul.', 29),
        ).arrange(DOWN, buff=0.20)
        self.new_page('La norme ne distribue pas sur la somme', rule, meaning, equality, gap=0.45)
        self.explain(
            'L’inégalité triangulaire exprime la règle générale : la norme de la somme est au plus la somme des normes. Le chemin direct ne dépasse pas le détour. On ne peut donc pas distribuer la norme sur une addition comme si c’était une multiplication.',
            rule, meaning, hold=2,
        )
        self.explain(
            'L’égalité est possible lorsque les deux déplacements non nuls suivent la même direction et le même sens, sans virage ni retour en arrière. Elle est aussi vraie si l’un des déplacements est nul. Ce sont des situations particulières, pas une règle universelle.',
            equality, hold=2,
        )

    def _self_check(self):
        data = self.formula(r'(4,1),\qquad(-2,3),\qquad(1,-5)', 43)
        prompt = VGroup(
            self.words('Quel est le déplacement total ?', 31),
            self.words('Quelle est sa norme ?', 31),
        ).arrange(DOWN, buff=0.30)
        assumption = self.words('Chaque étape est parcourue en ligne droite.', 28, BLACK)
        self.new_page('À vous : le marcheur du cahier', data, prompt, assumption)
        self.explain(
            'Dans le cahier, un marcheur effectue ces trois déplacements. Pour '
            'comparer aussi les longueurs, nous supposons qu’il parcourt chaque '
            'étape en ligne droite. Trouvez le déplacement total, puis sa norme. '
            'Commencez par les composantes ; n’additionnez pas les longueurs '
            'des trois vecteurs.',
            data, prompt, assumption, hold=2, pause_after=6,
        )
        net = self.formula(r'(4-2+1,\ 1+3-5)=(3,-1)', 41)
        result = self.formula(r'\|(3,-1)\|=\sqrt{3^2+(-1)^2}=\sqrt{10}', 40, BLACK)
        path = self.formula(r'\text{Trajet : }\sqrt{17}+\sqrt{13}+\sqrt{26}', 39)
        self.new_page('Réponse : les composantes d’abord', net, result, path)
        self.explain(
            'La composante horizontale vaut trois et la composante verticale '
            'moins un. Le déplacement total est donc trois, moins un, de norme '
            'racine de dix. La somme racine de dix-sept, plus racine de treize, '
            'plus racine de vingt-six mesure notre trajet en trois étapes '
            'droites. Avec des détours entre les mêmes positions, les déplacements '
            'resteraient identiques, mais la distance parcourue serait plus grande.',
            net, result, path, hold=2,
        )

    def _takeaway(self, *, narration=None):
        # MAT0339 : manuel 9.2–9.3 ; cahier 9.2 C.
        play_lesson_closing(
            self, LESSON_TITLE,
            (
                'Le déplacement additionne les composantes.',
                'Sa norme mesure la liaison directe.',
                'Le trajet additionne les longueurs des étapes.',
            ),
            '\\vec u=(3,0),\\qquad\\vec v=(0,4)',
            'Deux étapes droites :\ncalculez le trajet et la norme du déplacement.',
            recap_spoken='Le déplacement additionne les composantes. Sa norme mesure la liaison directe. Le trajet additionne les longueurs des étapes.',
            practice_spoken='Reprenez trois mètres horizontalement puis quatre mètres verticalement, avec deux étapes droites. Calculez la longueur du trajet et la norme du déplacement total.',
            narration=narration,
        )

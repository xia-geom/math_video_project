"""Read a horizontal shift from a factored argument and track characteristic points."""
import math

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    LEFT,
    RED_D,
    UP,
    WHITE,
    Arrow,
    Axes,
    Dot,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene

config.background_color = WHITE


class DephasageFactorisationFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._factor_and_locate()
        self._move_characteristic_points()
        self._check_wrong_shift()
        self._self_check()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        expression = self.formula(r'f(x)=\sin(2x-\pi)', 54)
        guess = self.formula(r'\text{déplacement vers la droite de }\pi\;?', 38, RED_D)
        reminder = self.formula(r'\sin\bigl(B(x-C)\bigr)', 48, BLUE_D)
        self.new_page('Le déphasage se lit après factorisation', expression,
                      guess, reminder, gap=0.6)
        self.explain(
            'Dans sinus de deux x moins pi, on pourrait lire moins pi et '
            'annoncer un déplacement de pi vers la droite. Mais le sinus reçoit '
            'tout l’argument deux x moins pi. Le coefficient de x doit donc '
            'être pris en compte.', expression, guess)
        self.explain(
            'La forme qui permet de lire directement le déplacement est '
            'sinus de B fois x moins C. Les parenthèses sont essentielles : '
            'B multiplie à la fois x et le décalage C.', reminder)

    def _factor_and_locate(self):
        factor = self.formula(r'2x-\pi=2\left(x-\frac\pi2\right)', 50)
        root = self.formula(r'2x-\pi=0\quad\Longleftrightarrow\quad x=\frac\pi2', 44)
        shift = self.formula(r'C=\frac\pi2\quad\text{vers la droite}', 42, GREEN_D)
        self.new_page('Retrouver le zéro de l’argument', factor, root, shift)
        self.explain(
            'Mettons deux en facteur. Pour retrouver moins pi après '
            'développement, il faut écrire moins pi sur deux dans la '
            'parenthèse. Le déplacement lu sous cette forme est donc '
            'pi sur deux vers la droite.', factor, shift)
        self.explain(
            'On peut le contrôler sans mémoriser une règle de signe. '
            'Demandons pour quelle entrée l’argument vaut zéro. Deux x '
            'moins pi s’annule en pi sur deux. À cet endroit, le sinus '
            'traverse sa médiane en montant.', root)

    def _move_characteristic_points(self):
        axes = Axes(x_range=[0, 1.65 * math.pi, math.pi / 2],
                    y_range=[-1.5, 1.5, 1], x_length=9.3, y_length=2.6,
                    axis_config={'color': BLACK, 'include_tip': False})
        x_labels = VGroup(*(self.formula(tex, 24).next_to(
            axes.c2p(x, -1.5), DOWN, buff=0.10) for x, tex in [
                (0, '0'), (math.pi / 2, r'\pi/2'), (math.pi, r'\pi'),
                (3 * math.pi / 2, r'3\pi/2')]))
        y_labels = VGroup(*(self.formula(str(y), 24).next_to(
            axes.c2p(0, y), LEFT, buff=0.12) for y in [-1, 1]))
        curve = axes.plot(lambda x: math.sin(2 * x), x_range=[0, math.pi],
                          color=BLUE_D)
        sample_x = [k * math.pi / 4 for k in range(5)]
        points = VGroup(*(Dot(axes.c2p(x, math.sin(2 * x)), radius=0.065,
                              color=GREEN_D) for x in sample_x))
        displacement = Arrow(axes.c2p(0, 1.45), axes.c2p(math.pi / 2, 1.45),
                             color=GREEN_D, buff=0, stroke_width=3)
        distance_label = self.formula(r'+\pi/2', 28, GREEN_D)
        distance_label.next_to(displacement, UP, buff=0.10)
        graph = VGroup(axes, x_labels, y_labels, curve, points,
                       displacement, distance_label)
        labels = self.formula(r'\sin(2x)\quad\longrightarrow\quad'
                              r'\sin\left(2\left(x-\frac\pi2\right)\right)', 36)
        self.new_page('Suivre les mêmes points du motif', labels, graph, gap=0.35)
        self.explain(
            'Regardons une période de sinus de deux x. Les cinq points '
            'marqués indiquent le départ, le maximum, le passage descendant, '
            'le minimum et le retour. La période vaut pi : le coefficient '
            'deux resserre le motif horizontalement.',
            labels, axes, x_labels, y_labels, curve, points)
        self.explain(
            'Translatons maintenant tout ce motif de pi sur deux. Chaque '
            'point conserve sa hauteur et reçoit la même augmentation '
            'd’abscisse. Le départ se place en pi sur deux; le maximum '
            'se place en trois pi sur quatre.', displacement, distance_label)
        delta = axes.c2p(math.pi / 2, 0) - axes.c2p(0, 0)
        self.play(curve.animate.shift(delta), points.animate.shift(delta), run_time=2)
        first = self.formula(r'x=\pi/2', 28, GREEN_D)
        first.next_to(points[0], UP, buff=0.15)
        self.page.add(first)
        self.explain(
            'Nous obtenons bien la fonction initiale. Le déplacement du '
            'dessin et la factorisation racontent la même opération. '
            'Aucune hauteur n’a changé, et la longueur d’une période '
            'est toujours pi.', first)

    def _check_wrong_shift(self):
        intended = self.formula(r'f(\pi/4)=\sin(-\pi/2)=-1', 44)
        wrong = self.formula(r'h(x)=\sin\bigl(2(x-\pi)\bigr)', 42, RED_D)
        value = self.formula(r'h(\pi/4)=\sin(-3\pi/2)=1', 44, RED_D)
        conclusion = self.formula(r'f(\pi/4)\ne h(\pi/4)', 40, GREEN_D)
        self.new_page('Tester le décalage proposé', intended, wrong, value,
                      conclusion, gap=0.4)
        self.explain(
            'Pourquoi pi serait-il incorrect dans cet exemple ? Testons '
            'l’entrée pi sur quatre. La fonction demandée donne moins un. '
            'La formule construite avec un décalage de pi donne plus un. '
            'Une seule entrée suffit à distinguer les deux courbes.',
            intended, wrong, value, conclusion, hold=1.6)

    def _self_check(self):
        expression = self.formula(r'g(x)=\sin(4x-\pi)', 54)
        fill = self.formula(r'4x-\pi=4(x-C)\qquad C=\;?', 46)
        prompt = self.words('Quel décalage lit-on dans cette factorisation ?', 28)
        self.new_page('À vous de factoriser', expression, fill, prompt, gap=0.65)
        self.explain(
            'Essayez avec sinus de quatre x moins pi. Complétez '
            'la factorisation exacte quatre fois x moins C, puis '
            'donnez le déplacement qu’elle permet de lire. '
            'Vérifiez votre valeur en développant les parenthèses.',
            expression, fill, prompt, pause_after=6)
        factor = self.formula(r'4x-\pi=4\left(x-\frac\pi4\right)', 48)
        answer = self.formula(r'C=\frac\pi4\quad\text{vers la droite}', 44, GREEN_D)
        zero = self.formula(r'4(\pi/4)-\pi=0', 42)
        self.new_page('La constante est divisée par quatre', factor, answer, zero)
        self.explain(
            'Il faut écrire pi sur quatre. Quatre fois pi sur quatre '
            'redonne pi, et l’argument s’annule bien à cette entrée. '
            'Le déplacement lu dans la factorisation est donc pi '
            'sur quatre vers la droite.', factor, answer, zero)

    def _takeaway(self):
        rule = self.formula(r'Bx-\varphi=B\left(x-\frac{\varphi}{B}\right)'
                            r',\qquad B\ne0', 40)
        idea = self.words('Factoriser, puis contrôler un point du graphe.', 29, BLUE_D)
        source = self.words('MAT0339 : M16.7 • C16.2 A, adapté', 28)
        self.new_page('À retenir', rule, idea, source, gap=0.65)
        self.explain(
            'Factorisez avant de lire le déphasage. Le décalage obtenu '
            'est la constante divisée par le coefficient de x. '
            'Une période entière peut ensuite être ajoutée au décalage '
            'sans changer la courbe. Gardez le réflexe de contrôler '
            'un point caractéristique.', rule, idea, source)

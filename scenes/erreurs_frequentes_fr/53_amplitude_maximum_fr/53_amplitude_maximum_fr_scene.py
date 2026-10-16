"""A sinusoid's amplitude is a distance from its median, not its maximum."""
import math

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    LEFT,
    RED_D,
    RIGHT,
    WHITE,
    Axes,
    DashedLine,
    Dot,
    DoubleArrow,
    Transform,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene

config.background_color = WHITE


class AmplitudeMaximumFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._range()
        self._reflection_and_distances()
        self._numerical_check()
        self._self_check()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        function = self.formula(r'f(x)=-4\cos(3x)+2', 54)
        guesses = self.formula(r'\text{amplitude}=-4\;?\qquad'
                               r'\max f=4\;?', 40, RED_D)
        question = self.words('À partir de quelle hauteur mesure-t-on ?', 30)
        self.new_page('Amplitude ou maximum ?', function, guesses, question, gap=0.65)
        self.explain(
            'Dans cette formule, nous voyons moins quatre devant le cosinus, puis '
            'plus deux. L’amplitude est-elle moins quatre ? Le maximum est-il '
            'quatre ? Ces réponses confondent le coefficient, la distance '
            'd’oscillation et la hauteur maximale.', function, guesses)
        self.explain(
            'Pour les distinguer, choisissons d’abord la ligne autour de laquelle '
            'la courbe oscille. L’amplitude se mesure depuis cette ligne, et non '
            'nécessairement depuis l’axe horizontal.', question)

    def _range(self):
        cosine = self.formula(r'-1\le\cos(3x)\le1', 46)
        oscillation = self.formula(r'-4\le-4\cos(3x)\le4', 46)
        shifted = self.formula(r'-2\le f(x)\le6', 52, BLUE_D)
        median = self.formula(r'D=2', 46, BLUE_D)
        self.new_page('La translation change les hauteurs', cosine, oscillation,
                      shifted, median, gap=0.38)
        self.explain(
            'Le cosinus prend toutes les valeurs entre moins un et un. En le '
            'multipliant par moins quatre, les extrémités s’échangent : moins un '
            'donne quatre, et un donne moins quatre. L’oscillation reste donc '
            'comprise entre moins quatre et quatre.', cosine, oscillation)
        self.explain(
            'Ajouter deux fait monter toute la courbe de deux unités. Ses '
            'hauteurs vont maintenant de moins deux à six. La ligne médiane '
            'est à la hauteur deux. Ce déplacement vertical modifie le maximum '
            'et le minimum, mais pas l’amplitude.', shifted, median)

    def _reflection_and_distances(self):
        axes = Axes(x_range=[0, 2 * math.pi / 3, math.pi / 3],
                    y_range=[-2.5, 6.5, 2], x_length=6.6, y_length=3.65,
                    axis_config={'color': BLACK, 'include_tip': False})
        y_labels = VGroup(*(self.formula(str(y), 24).next_to(
            axes.c2p(0, y), direction=LEFT, buff=0.12) for y in [-2, 2, 6]))
        x_labels = VGroup(
            self.formula(r'\pi/3', 24).next_to(axes.c2p(math.pi / 3, 0),
                                              direction=DOWN, buff=0.08),
            self.formula(r'2\pi/3', 24).next_to(axes.c2p(2 * math.pi / 3, 0),
                                               direction=DOWN, buff=0.08))
        median = DashedLine(axes.c2p(0, 2), axes.c2p(2 * math.pi / 3, 2),
                            color=BLUE_D, stroke_width=2)
        curve = axes.plot(lambda x: 2 + 4 * math.cos(3 * x), color=BLUE_D,
                          x_range=[0, 2 * math.pi / 3])
        top_dot = Dot(axes.c2p(0, 6), radius=0.065, color=BLUE_D)
        bottom_dot = Dot(axes.c2p(math.pi / 3, -2), radius=0.065, color=BLUE_D)
        upper = DoubleArrow(axes.c2p(math.pi / 3 + 0.11, 2),
                            axes.c2p(math.pi / 3 + 0.11, 6),
                            color=GREEN_D, buff=0, stroke_width=3)
        lower = DoubleArrow(axes.c2p(0.11, -2), axes.c2p(0.11, 2),
                            color=GREEN_D, buff=0, stroke_width=3)
        upper_label = self.formula('4', 30, GREEN_D).next_to(upper, RIGHT, buff=0.10)
        lower_label = self.formula('4', 30, GREEN_D).next_to(lower, RIGHT, buff=0.10)
        # The lower arrow is centered on y=0; keep its numeral clear of the axis.
        lower_label.shift([0, 0.32, 0])
        graph = VGroup(axes, y_labels, x_labels, median, curve, top_dot, bottom_dot,
                       upper, lower, upper_label, lower_label)
        label = self.formula(r'2+4\cos(3x)\quad\longrightarrow\quad2-4\cos(3x)', 34)
        self.new_page('Le signe réfléchit la courbe', label, graph, gap=0.3)
        self.explain(
            'Partons de la courbe avec un coefficient positif. Changer ce '
            'coefficient en son opposé réfléchit chaque point par rapport à '
            'la ligne médiane. Le sommet descend de l’autre côté; le creux '
            'monte. Les distances à la médiane restent les mêmes.',
            label, axes, y_labels, x_labels, median, curve, top_dot, bottom_dot)
        reflected = axes.plot(lambda x: 2 - 4 * math.cos(3 * x), color=BLUE_D,
                              x_range=[0, 2 * math.pi / 3])
        self.play(Transform(curve, reflected),
                  top_dot.animate.move_to(axes.c2p(0, -2)),
                  bottom_dot.animate.move_to(axes.c2p(math.pi / 3, 6)), run_time=2)
        self.explain(
            'Voici maintenant notre fonction. Entre la médiane deux et le '
            'maximum six, la distance vaut quatre. Entre le minimum moins deux '
            'et la médiane, elle vaut également quatre. Une distance ne devient '
            'pas négative lorsque la courbe se réfléchit.',
            upper, lower, upper_label, lower_label, hold=1.6)

    def _numerical_check(self):
        extrema = self.formula(r'f(0)=-2,\qquad f(\pi/3)=6', 44)
        amplitude = self.formula(r'\mathcal A=\frac{6-(-2)}2=4', 48, GREEN_D)
        span = self.formula(r'6-(-2)=8\quad\text{(écart total)}', 38)
        self.new_page('Deux valeurs pour contrôler', extrema, amplitude, span)
        self.explain(
            'Vérifions directement dans la formule. À zéro, le cosinus vaut un, '
            'donc la hauteur est moins deux. À pi sur trois, il vaut moins un, '
            'donc la hauteur est six. Les extrêmes annoncés sont bien atteints.', extrema)
        self.explain(
            'L’écart total entre ces deux hauteurs vaut huit. L’amplitude en '
            'est la moitié, soit quatre. Huit mesure le trajet vertical complet '
            'du creux au sommet; quatre mesure la distance depuis le centre '
            'de cette oscillation.', amplitude, span)

    def _self_check(self):
        function = self.formula(r'g(x)=3\sin(2x)-1', 52)
        question = self.words('Amplitude, médiane, maximum et minimum ?', 28)
        self.new_page('À vous de lire les hauteurs', function, question, gap=0.8)
        self.explain(
            'À vous : pour trois sinus de deux x, moins un, trouvez l’amplitude, '
            'la ligne médiane, le maximum et le minimum. Vérifiez que les '
            'deux extrêmes sont à la même distance de la médiane.',
            function, question, pause_after=6)
        center = self.formula(r'\mathcal A=3,\qquad D=-1', 46, BLUE_D)
        extrema = self.formula(r'M=-1+3=2,\qquad m=-1-3=-4', 40)
        check = self.formula(r'2-(-1)=(-1)-(-4)=3', 40, GREEN_D)
        self.new_page('Trois unités autour de moins un', center, extrema, check)
        self.explain(
            'L’amplitude vaut trois et la médiane moins un. Le maximum vaut '
            'deux, le minimum moins quatre. Les deux distances à moins un '
            'valent bien trois. Le coefficient deux à l’intérieur agit sur '
            'la période, sans changer ces hauteurs.', center, extrema, check)

    def _takeaway(self):
        rule = self.formula(r'\mathcal A=|A|,\quad M=D+|A|,\quad m=D-|A|', 39)
        words = self.words('L’amplitude est une distance à la médiane.', 29, BLUE_D)
        source = self.words('MAT0339 : M16.2 et M16.7 • C16.6 B', 28)
        self.new_page('À retenir', rule, words, source, gap=0.7)
        self.explain(
            'Pour retenir les formules, partez de la médiane et ajoutez ou '
            'retirez la même distance positive. L’exercice seize point six, '
            'partie B du cahier reprend exactement la fonction étudiée.',
            rule, words, source)

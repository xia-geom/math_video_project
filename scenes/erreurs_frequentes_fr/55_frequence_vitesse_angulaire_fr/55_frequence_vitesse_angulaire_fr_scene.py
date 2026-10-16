"""Relate revolutions per minute, frequency, angular speed and period."""
import math

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    RED_D,
    RIGHT,
    WHITE,
    Circle,
    DecimalNumber,
    Dot,
    FadeOut,
    Line,
    SurroundingRectangle,
    ValueTracker,
    VGroup,
    config,
    linear,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene

config.background_color = WHITE


class FrequenceVitesseAngulaireFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._convert_units()
        self._synchronized_counters()
        self._period_and_check()
        self._self_check()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        speed = self.formula(r'18\ \mathrm{tours/min}', 56)
        guesses = self.formula(r'f=18\ \mathrm{Hz}\;?\qquad'
                               r'\omega=18\ \mathrm{rad/s}\;?', 38, RED_D)
        idea = self.words('Compter des tours, mesurer un angle, chronométrer.', 28)
        self.new_page('Trois mesures d’une même rotation', speed, guesses, idea)
        self.explain(
            'Une roue tourne régulièrement à dix-huit tours par minute, dans '
            'le sens antihoraire. Est-ce une fréquence de dix-huit hertz ? '
            'Ou une vitesse angulaire de dix-huit radians par seconde ? '
            'Le nombre seul ne suffit pas : regardons les unités.', speed, guesses)
        self.explain(
            'La fréquence compte les cycles par seconde. La vitesse angulaire '
            'mesure l’angle parcouru par seconde. La période mesure le temps '
            'nécessaire pour accomplir un cycle. Ces trois grandeurs décrivent '
            'le même mouvement, mais répondent à des questions différentes.', idea)

    def _convert_units(self):
        frequency = self.formula(r'f=\frac{18}{60}=\frac3{10}'
                                 r'\ \mathrm{tour/s}=0{,}3\ \mathrm{Hz}', 40)
        revolution = self.formula(r'1\ \mathrm{tour}=2\pi\ \mathrm{rad}', 46, BLUE_D)
        angular = self.formula(r'\omega=2\pi f=\frac{3\pi}{5}\ \mathrm{rad/s}',
                               46, GREEN_D)
        self.new_page('Convertir une unité à la fois', frequency, revolution,
                      angular, gap=0.6)
        self.explain(
            'Une minute contient soixante secondes. Dix-huit tours répartis '
            'sur soixante secondes donnent trois dixièmes de tour par seconde. '
            'La fréquence vaut donc zéro virgule trois hertz. Le hertz est '
            'simplement l’unité des cycles par seconde.', frequency)
        self.explain(
            'Chaque tour correspond à deux pi radians. Pour passer des tours '
            'par seconde aux radians par seconde, on multiplie donc la fréquence '
            'par deux pi. On obtient trois pi sur cinq radians par seconde. '
            'Les deux conversions ont des rôles distincts.', revolution, angular)

    def _synchronized_counters(self):
        elapsed = ValueTracker(0)
        wheel = Circle(radius=1.55, color=BLUE_D, stroke_width=3)
        center = Dot(wheel.get_center(), radius=0.045, color=BLACK)
        initial = Dot(wheel.get_right(), radius=0.045, color=BLACK)
        radius = Line(wheel.get_center(), wheel.get_right(), color=BLUE_D,
                      stroke_width=3)
        point = Dot(wheel.get_right(), radius=0.075, color=GREEN_D)
        disk = VGroup(wheel, center, initial, radius, point)

        counters = []
        values = []
        for label, unit in [('Temps écoulé', r'\mathrm{s}'),
                            ('Nombre de tours', r'\mathrm{tour}'),
                            ('Angle parcouru', r'\mathrm{rad}')]:
            value = DecimalNumber(0, num_decimal_places=2, font_size=38, color=BLACK)
            values.append(value)
            number = VGroup(value, self.formula(unit, 32)).arrange(RIGHT, buff=0.22)
            counters.append(VGroup(self.words(label, 28, BLUE_D), number)
                            .arrange(DOWN, buff=0.16))
        readings = VGroup(*counters).arrange(DOWN, buff=0.38)
        layout = VGroup(disk, readings).arrange(RIGHT, buff=1.25)
        note = self.words('Compteurs arrondis à deux décimales.', 28)
        self.new_page('Synchroniser les trois compteurs', layout, note, gap=0.3)

        # All visual objects belong to the page. Attach updaters only after layout.
        omega = 3 * math.pi / 5
        radius.add_updater(lambda m: m.put_start_and_end_on(
            wheel.get_center(), wheel.point_at_angle(omega * elapsed.get_value())))
        point.add_updater(lambda m: m.move_to(
            wheel.point_at_angle(omega * elapsed.get_value())))
        values[0].add_updater(lambda m: m.set_value(elapsed.get_value()))
        values[1].add_updater(lambda m: m.set_value(0.3 * elapsed.get_value()))
        values[2].add_updater(lambda m: m.set_value(omega * elapsed.get_value()))
        self.explain(
            'Le chronomètre démarre en même temps que la rotation. '
            'Suivons le même point avec trois compteurs : le temps écoulé, '
            'le nombre de tours et l’angle parcouru. Nous figerons l’image '
            'après une seconde pour les comparer.', disk, readings, note)
        self.play(elapsed.animate.set_value(1), run_time=1, rate_func=linear)
        first_check = SurroundingRectangle(VGroup(counters[1], counters[2]),
                                            color=GREEN_D, buff=0.12, stroke_width=2)
        self.page.add(first_check)
        self.explain(
            'Après une seconde, la roue a parcouru zéro virgule trois tour. '
            'C’est le même déplacement que trois pi sur cinq radians, '
            'soit environ un virgule quatre-vingt-huit radian. Elle '
            'n’a pas encore terminé un tour.', first_check, hold=1.4)
        self.play(FadeOut(first_check), run_time=0.35)
        self.play(elapsed.animate.set_value(10 / 3), run_time=7 / 3, rate_func=linear)
        # Freeze every updater before another page can remove these mobjects.
        for mob in (radius, point, *values):
            mob.clear_updaters()
        completed = SurroundingRectangle(readings, color=GREEN_D,
                                         buff=0.12, stroke_width=2)
        self.page.add(completed)
        self.explain(
            'Au retour au point de départ, le compteur de tours vaut un '
            'et celui des radians vaut deux pi. Le chronomètre affiche '
            'environ trois virgule trente-trois secondes. Cette durée '
            'est la période.', completed, hold=1.5)

    def _period_and_check(self):
        period = self.formula(r'T=\frac1f=\frac{10}{3}\ \mathrm{s}', 52)
        cycles = self.formula(r'fT=\frac3{10}\cdot\frac{10}{3}=1', 44)
        angle = self.formula(r'\omega T=\frac{3\pi}{5}\cdot\frac{10}{3}=2\pi',
                             44, GREEN_D)
        self.new_page('Un cycle fournit deux contrôles', period, cycles, angle)
        self.explain(
            'Calculons cette durée exactement. Un cycle divisé par trois '
            'dixièmes de cycle par seconde donne dix tiers de seconde. '
            'La période est l’inverse de la fréquence. Plus les cycles '
            'se répètent rapidement, plus leur durée diminue.', period)
        self.explain(
            'Deux produits permettent de vérifier les conversions. Fréquence '
            'fois période donne un cycle. Vitesse angulaire fois période '
            'donne deux pi radians. Si ces contrôles échouent, recherchez '
            'un facteur soixante ou deux pi oublié.', cycles, angle)

    def _self_check(self):
        rotation = self.formula(r'30\ \mathrm{tours/min}', 56)
        question = self.formula(r'f\ \text{en Hz},\qquad'
                                r'\omega\ \text{en rad/s},\qquad T\ \text{en s}\;?', 36)
        self.new_page('À vous de convertir', rotation, question, gap=0.8)
        self.explain(
            'Une autre roue effectue trente tours par minute. Trouvez '
            'sa fréquence en hertz, sa vitesse angulaire en radians par '
            'seconde et sa période. Gardez les unités et contrôlez '
            'l’angle parcouru pendant une période.', rotation, question, pause_after=6)
        f = self.formula(r'f=\frac{30}{60}=0{,}5\ \mathrm{Hz}', 44)
        omega = self.formula(r'\omega=\pi\ \mathrm{rad/s}', 46, GREEN_D)
        period = self.formula(r'T=2\ \mathrm{s},\qquad\omega T=2\pi', 44)
        self.new_page('Un demi-tour par seconde', f, omega, period)
        self.explain(
            'Trente tours par minute donnent un demi-tour par seconde. '
            'La fréquence vaut un demi-hertz, la vitesse angulaire '
            'pi radians par seconde, et la période deux secondes. '
            'Pendant ces deux secondes, l’angle parcouru vaut bien deux pi.',
            f, omega, period)

    def _takeaway(self):
        relations = self.formula(r'f=\frac1T,\qquad\omega=2\pi f', 50)
        meaning = self.words('Fréquence : cycles • Vitesse angulaire : radians', 28, BLUE_D)
        source = self.words('MAT0339 : M17.1 • C17.1 A–B', 28)
        self.new_page('À retenir', relations, meaning, source, gap=0.7)
        self.explain(
            'Pour une rotation uniforme dans le sens choisi, distinguez '
            'toujours cycles, radians et secondes. Les unités expliquent '
            'les formules, et un tour complet permet de les vérifier. '
            'Le premier exercice du chapitre dix-sept reprend ces conversions.',
            relations, meaning, source)

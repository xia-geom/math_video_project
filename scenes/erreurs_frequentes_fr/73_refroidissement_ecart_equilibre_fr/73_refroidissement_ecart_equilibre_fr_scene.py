"""Apply exponential half-life to excess above a cooling equilibrium."""

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Axes,
    DashedLine,
    DecimalNumber,
    Dot,
    Line,
    MathTex,
    Tex,
    Text,
    ValueTracker,
    VGroup,
    config,
    linear,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class RefroidissementEcartEquilibreFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._watch_excess()
        self._half_excess()
        self._halve_reading()
        self._solve_halved_reading()
        self._general_model()
        self._equilibrium()
        self._target_range()
        self._self_check()
        self._self_check_answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        model = self.formula(r"T(t)=20+60\cdot2^{-t/10}", 49)
        assumptions = self.words("t ≥ 0 en minutes ; T(t) en °C ; ambiante : 20 °C.", 29)
        start = self.formula(r"T(0)=80\,{}^\circ\mathrm C", 44)
        question = panel(self.words("Après 10 minutes : 40 °C ou 50 °C ?", 32),
                         width=10.7, height=1.1)
        self.new_page("Qu'est-ce qui est divisé par deux ?", model, assumptions, start,
                      question, gap=0.48)
        self.explain(
            "Nous adaptons le modèle de refroidissement du manuel avec une "
            "température ambiante constante de vingt degrés Celsius. "
            "L'objet commence à quatre-vingts degrés, et le temps est compté "
            "en minutes à partir de zéro.",
            model, assumptions, start,
        )
        self.explain(
            "Au bout de dix minutes, le facteur exponentiel est divisé par deux. "
            "Est-ce que la température affichée passe de quatre-vingts à quarante degrés ? "
            "Ou faut-il d'abord tenir compte des vingt degrés de la pièce ?",
            question,
        )

    def _watch_excess(self):
        clock = ValueTracker(0)
        def temperature(t):
            return 20 + 60 * 2 ** (-t / 10)

        axes = Axes(
            x_range=[0, 33, 10], y_range=[0, 90, 20],
            x_length=8.5, y_length=2.6,
            axis_config={"color": BLACK, "include_tip": False, "include_ticks": False},
        )
        curve = axes.plot(temperature, x_range=[0, 33], color=BLUE_D)
        ambient = DashedLine(axes.c2p(0, 20), axes.c2p(33, 20), color=BLACK)
        excess = Line(axes.c2p(0, 20), axes.c2p(0, 80), color=BLUE_D, stroke_width=6)
        probe = Dot(axes.c2p(0, 80), color=BLUE_D, radius=0.085)
        labels = VGroup(
            self.formula(r"t\ (\mathrm{min})", 27).next_to(axes.x_axis, RIGHT, buff=0.13),
            self.formula(r"T\ ({}^\circ\mathrm C)", 27).next_to(axes.y_axis, UP, buff=0.11),
            self.formula("20", 26).next_to(axes.c2p(0, 20), LEFT, buff=0.14),
            self.formula("80", 26).next_to(axes.c2p(0, 80), LEFT, buff=0.14),
            *[self.formula(str(t), 26).next_to(axes.c2p(t, 0), DOWN, buff=0.12)
              for t in (0, 10, 20, 30)],
        )
        graph = VGroup(axes, curve, ambient, labels, excess, probe)
        elapsed = DecimalNumber(20, num_decimal_places=0, font_size=32, color=BLACK)
        difference = DecimalNumber(60, num_decimal_places=0, font_size=32, color=BLUE_D)
        reading = DecimalNumber(80, num_decimal_places=0, font_size=32, color=BLACK)
        fields = VGroup(
            VGroup(self.formula("t=", 32), elapsed, self.formula(r"\mathrm{min}", 29)).arrange(RIGHT, buff=0.18),
            VGroup(self.formula("E=", 32, BLUE_D), difference,
                   self.formula(r"{}^\circ\mathrm C", 29, BLUE_D)).arrange(RIGHT, buff=0.18),
            VGroup(self.formula("T=", 32), reading,
                   self.formula(r"{}^\circ\mathrm C", 29)).arrange(RIGHT, buff=0.18),
        ).arrange(RIGHT, buff=0.65)
        note = self.words("La barre bleue mesure E = T − 20.", 29)
        self.new_page("Mesurer depuis la température ambiante", graph, fields, note, gap=0.35)
        centres = [number.get_center().copy() for number in (elapsed, difference, reading)]
        elapsed.set_value(0).move_to(centres[0])
        self.explain(
            "La ligne pointillée représente les vingt degrés de la pièce. "
            "La barre bleue mesure seulement l'écart E entre la température de "
            "l'objet et cette ligne. Elle mesure soixante degrés au départ. "
            "Regardons les dix premières minutes, puis les dix suivantes.",
            graph, fields, note,
        )
        excess.add_updater(lambda mob: mob.put_start_and_end_on(
            axes.c2p(clock.get_value(), 20),
            axes.c2p(clock.get_value(), temperature(clock.get_value())),
        ))
        probe.add_updater(lambda mob: mob.move_to(
            axes.c2p(clock.get_value(), temperature(clock.get_value()))))
        elapsed.add_updater(lambda mob: mob.set_value(clock.get_value()).move_to(centres[0]))
        difference.add_updater(lambda mob: mob.set_value(
            temperature(clock.get_value()) - 20).move_to(centres[1]))
        reading.add_updater(lambda mob: mob.set_value(
            temperature(clock.get_value())).move_to(centres[2]))
        self.play(clock.animate.set_value(10), run_time=2.6, rate_func=linear)
        self.wait(0.8)
        self.play(clock.animate.set_value(20), run_time=2.6, rate_func=linear)
        self.wait(0.8)
        for mob in (excess, probe, elapsed, difference, reading):
            mob.clear_updaters()

    def _half_excess(self):
        excess = self.formula(r"E(t)=T(t)-20=60\cdot2^{-t/10}", 43)
        halve = self.formula(r"E(t+10)=\frac{E(t)}2", 46, BLUE_D)
        readings = self.formula(r"T(10)=20+30=50,\qquad T(20)=20+15=35", 38)
        rule = panel(self.formula(r"T(t+10)=20+\frac{T(t)-20}{2}", 43),
                     width=10.5, height=1.2)
        self.new_page("L'écart est divisé par deux", excess, halve, readings, rule, gap=0.43)
        self.explain(
            "Ajouter dix minutes à t multiplie l'exponentielle par deux puissance "
            "moins un, donc par un demi. L'écart passe de soixante à trente, puis "
            "de trente à quinze. Les températures correspondantes sont cinquante, "
            "puis trente-cinq degrés Celsius.",
            excess, halve, readings,
        )
        self.explain(
            "Pour avancer de dix minutes, on soustrait d'abord les vingt degrés "
            "d'équilibre, on divise cet écart par deux, puis on rajoute vingt. "
            "La température ambiante n'est pas divisée par deux. "
            "La demi-vie est celle de l'écart.",
            rule, hold=1.6,
        )

    def _halve_reading(self):
        target = self.formula(r"T(t)=40\quad\Longleftrightarrow\quad60\cdot2^{-t/10}=20", 41)
        ratio = self.formula(r"2^{-t/10}=\frac13", 45)
        meaning = self.words("L'écart passe de 60 à 20 : il est divisé par trois.", 29)
        self.new_page("Pour passer de 80 °C à 40 °C", target, ratio, meaning, gap=0.65)
        self.explain(
            "Demandons maintenant quand l'affichage passe de quatre-vingts "
            "à quarante degrés Celsius. Il faut que l'écart à vingt degrés "
            "passe de soixante à vingt, donc qu'il soit divisé par trois. "
            "Nous isolons d'abord le terme exponentiel.",
            target, ratio, meaning,
        )

    def _solve_halved_reading(self):
        logs = self.formula(r"-\frac t{10}\ln2=-\ln3", 43)
        answer = panel(self.formula(r"t=10\frac{\ln3}{\ln2}\approx15{,}85\ \mathrm{min}", 43),
                       width=10.4, height=1.25)
        check = self.formula(r"T(10)=50>40\quad:\quad t>10\ \mathrm{min}\text{ est cohérent}", 35)
        self.new_page("Un délai supérieur à la demi-vie", logs, answer, check, gap=0.60)
        self.explain(
            "Le logarithme donne moins t sur dix fois logarithme de deux, "
            "égal à moins logarithme de trois. On trouve environ quinze "
            "virgule quatre-vingt-cinq minutes. Ce délai dépasse dix minutes, "
            "ce qui est cohérent puisque l'objet est encore à cinquante degrés après dix minutes.",
            logs, answer, check, hold=1.6,
        )

    def _general_model(self):
        general = self.formula(r"T(t)=T_a+(T_0-T_a)e^{-kt}", 43)
        assumptions = self.formula(r"t\ge0,\quad k>0,\quad T_0>T_a,\quad T_a\text{ constant}", 34)
        lifetime = self.formula(r"E(t)=T(t)-T_a,\qquad \tau=\frac{\ln2}{k}", 42)
        example = self.formula(r"k=\frac{\ln2}{10}\ \mathrm{min}^{-1}\quad\Longrightarrow\quad\tau=10\ \mathrm{min}", 38)
        self.new_page("La demi-vie porte sur T − Tₐ", general, assumptions, lifetime, example,
                      gap=0.45)
        self.explain(
            "La forme générale du manuel utilise une température ambiante "
            "constante T a et une température initiale T zéro supérieure à "
            "l'ambiante. Le coefficient k est strictement positif. "
            "L'écart à l'équilibre vaut T zéro moins T a, multiplié par exponentielle de moins k t.",
            general, assumptions,
        )
        self.explain(
            "Pour diviser cet écart positif par deux, le délai tau vaut "
            "logarithme de deux divisé par k. Dans notre adaptation, k est "
            "logarithme de deux sur dix, en minutes inverses. "
            "La demi-vie de l'écart est donc dix minutes. "
            "Si l'objet commence exactement à l'ambiante, la température reste constante.",
            lifetime, example,
        )

    def _equilibrium(self):
        positive = self.formula(r"60\cdot2^{-t/10}>0\qquad\text{pour tout }t\ge0\text{ fini}", 39)
        above = self.formula(r"T(t)>20\,{}^\circ\mathrm C", 46, BLUE_D)
        unreachable = self.words("20 °C : approché, jamais atteint en temps fini.", 30)
        below = self.words("Sous 20 °C : impossible dans ce modèle.", 30)
        self.new_page("L'équilibre n'est pas un seuil atteint", positive, above, unreachable,
                      below, gap=0.55)
        self.explain(
            "Une exponentielle positive reste strictement positive à tout "
            "instant fini. L'écart ne devient donc jamais exactement nul. "
            "Dans ce modèle, la température reste strictement supérieure à vingt degrés.",
            positive, above,
        )
        self.explain(
            "Atteindre exactement vingt degrés exigerait un écart nul, "
            "ce que l'exponentielle ne produit pas. Passer sous vingt demanderait "
            "un écart négatif, également impossible. Le modèle s'approche de "
            "l'équilibre autant que l'on veut, sans l'atteindre à un instant fini. "
            "Une mesure arrondie à vingt degrés ne contredit pas cette distinction mathématique.",
            unreachable, below, hold=1.6,
        )

    def _target_range(self):
        range_ = self.formula(r"t\ge0\quad\Longrightarrow\quad20<T(t)\le80", 43)
        inverse = self.formula(r"T(t)=C\quad\Longrightarrow\quad t=10\log_2\!\left(\frac{60}{C-20}\right)", 42)
        condition = panel(self.formula(r"20<C\le80\qquad\text{pour un temps }t\ge0", 39),
                          width=10.7, height=1.2)
        note = self.words("C > 80 donnerait un temps négatif, hors du domaine.", 28)
        self.new_page("Vérifier le seuil avant le logarithme", range_, inverse, condition,
                      note, gap=0.47)
        self.explain(
            "Le temps commence à zéro. La température descend donc de "
            "quatre-vingts vers vingt degrés. Un seuil C admissible doit être "
            "strictement supérieur à vingt et au plus égal à quatre-vingts. "
            "C égal à quatre-vingts correspond simplement à l'instant initial.",
            range_, inverse, condition,
        )
        self.explain(
            "Le logarithme exige un écart positif, mais ce contrôle ne suffit "
            "pas à lui seul. Pour un seuil supérieur à quatre-vingts, la formule "
            "donnerait un temps négatif, situé avant le domaine étudié. "
            "Il faut contrôler à la fois le seuil et le sens du temps.",
            note,
        )

    def _self_check(self):
        model = self.formula(r"T(t)=10+60\cdot2^{-t/4}", 48)
        units = self.words("t ≥ 0 en minutes ; T(t) en °C.", 30)
        first = self.words("1. Quelle température après 4 minutes ?", 31)
        second = self.words("2. Quand atteint-on 25 °C ?", 31)
        self.new_page("À vous : changer d'équilibre", model, units, first, second, gap=0.60)
        self.explain(
            "Dans cette nouvelle adaptation, la température ambiante est dix "
            "degrés et la demi-vie de l'écart est quatre minutes. "
            "Calculez la température après quatre minutes, puis le temps "
            "nécessaire pour atteindre vingt-cinq degrés. "
            "Commencez par soustraire la bonne température ambiante. "
            "Prenez six secondes pour réfléchir.",
            model, units, first, second, pause_after=6,
        )

    def _self_check_answer(self):
        first = self.formula(r"T(4)=10+60\cdot\frac12=40\,{}^\circ\mathrm C", 43, BLUE_D)
        equation = self.formula(r"T(t)=25\quad\Longleftrightarrow\quad60\cdot2^{-t/4}=15", 41)
        ratio = self.formula(r"2^{-t/4}=\frac14=2^{-2}", 44)
        time = self.formula(r"t=8\ \mathrm{min},\qquad T(8)=10+15=25", 42, BLUE_D)
        self.new_page("Deux demi-vies de l'écart", first, equation, ratio, time, gap=0.50)
        self.explain(
            "Après quatre minutes, l'écart de soixante degrés est devenu trente. "
            "On ajoute les dix degrés ambiants : la température vaut quarante degrés. "
            "Pour atteindre vingt-cinq degrés, l'écart doit ensuite être quinze.",
            first, equation,
        )
        self.explain(
            "Quinze est le quart de soixante : deux demi-vies sont nécessaires. "
            "L'égalité des puissances de deux donne moins t sur quatre égal "
            "à moins deux, donc t égal à huit minutes. "
            "La substitution redonne bien vingt-cinq degrés, au-dessus de l'ambiante.",
            ratio, time, hold=1.6,
        )

    def _takeaway(self):
        key = self.formula(r"E(t)=T(t)-T_a", 49, BLUE_D)
        steps = self.words("Soustraire l'équilibre, puis appliquer la demi-vie.", 30)
        restore = self.words("Ajouter l'équilibre pour retrouver la température.", 30)
        condition = self.words("Vérifier que le seuil est atteignable pour t ≥ 0.", 29)
        reference = self.words("Manuel 6.8 · Cahier 6.8 C · exemples adaptés", 27)
        self.new_page("Diviser le bon écart", key, steps, restore, condition, reference, gap=0.48)
        self.explain(
            "Une demi-vie agit sur la quantité exponentielle. Dans un modèle "
            "de refroidissement avec équilibre, cette quantité est l'écart "
            "à la température ambiante. Soustrayez l'équilibre avant le calcul "
            "et ajoutez-le après. Enfin, vérifiez les températures accessibles "
            "et le domaine du temps avant de retenir une solution logarithmique.",
            key, steps, restore, condition, reference, hold=2,
        )

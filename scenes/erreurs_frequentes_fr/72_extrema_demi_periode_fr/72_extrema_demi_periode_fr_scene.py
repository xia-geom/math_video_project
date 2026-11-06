"""Infer a sinusoid's period from correctly identified consecutive extrema."""

import math

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    RIGHT,
    UP,
    WHITE,
    Axes,
    Dot,
    DoubleArrow,
    MathTex,
    MoveAlongPath,
    Tex,
    Text,
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


class ExtremaDemiPeriodeFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._follow_cycle()
        self._parameters()
        self._validate_model()
        self._missing_consecutiveness()
        self._missed_cycle_example()
        self._self_check()
        self._self_check_answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        assumption = self.words("On choisit un modèle sinusoïdal non constant.", 30)
        maximum = self.formula(r"\text{Maximum : }4{,}8\ \mathrm{m}\quad\text{à }3\ \mathrm{h}", 40)
        minimum = self.formula(r"\text{Minimum suivant : }0{,}8\ \mathrm{m}\quad\text{à }9{,}2\ \mathrm{h}", 40)
        question = panel(self.formula(r"9{,}2-3=6{,}2\ \mathrm{h}\quad\text{: une période ?}", 39),
                         width=10.8, height=1.1)
        self.new_page("Du sommet au creux : un cycle ?", assumption, maximum, minimum,
                      question, gap=0.48)
        self.explain(
            "Le cahier propose une marée qui atteint quatre virgule huit mètres "
            "à trois heures, puis zéro virgule huit mètre à neuf virgule deux heures. "
            "Nous retenons explicitement le minimum suivant et un modèle sinusoïdal "
            "non constant. Ce modèle est une idéalisation du phénomène.",
            assumption, maximum, minimum,
        )
        self.explain(
            "Les deux instants sont séparés de six virgule deux heures. "
            "Mais un sommet et un creux sont deux états opposés. "
            "Cette différence de temps représente-t-elle vraiment un cycle complet ?",
            question,
        )

    def _follow_cycle(self):
        axes = Axes(
            x_range=[0, 17, 1], y_range=[0, 6.2, 1],
            x_length=8.6, y_length=2.6,
            axis_config={"color": BLACK, "include_tip": False, "include_ticks": False},
        )
        def height(t):
            return 2.8 + 2 * math.cos(2 * math.pi * (t - 3) / 12.4)

        curve = axes.plot(height, x_range=[0, 17], color=BLUE_D)
        dots = VGroup(*[Dot(axes.c2p(t, height(t)), color=BLUE_D, radius=0.065)
                        for t in (3, 9.2, 15.4)])
        labels = VGroup(
            self.formula(r"t\ (\mathrm{h})", 27).next_to(axes.x_axis, RIGHT, buff=0.13),
            self.formula(r"h\ (\mathrm{m})", 27).next_to(axes.y_axis, UP, buff=0.10),
            *[self.formula(label, 28).next_to(axes.c2p(t, 0), DOWN, buff=0.10)
              for t, label in ((3, "3"), (9.2, "9{,}2"), (15.4, "15{,}4"))],
        )
        probe = Dot(axes.c2p(3, 4.8), color=BLACK, radius=0.10)
        half_arrow = DoubleArrow(axes.c2p(3, 5.55), axes.c2p(9.2, 5.55),
                                 buff=0, color=BLUE_D)
        half_label = self.formula(r"T/2=6{,}2\ \mathrm{h}", 29, BLUE_D).next_to(
            half_arrow, UP, buff=0.10)
        half = VGroup(half_arrow, half_label)
        full_arrow = DoubleArrow(axes.c2p(3, 0), axes.c2p(15.4, 0),
                                 buff=0, color=BLUE_D)
        # Keep both arrowheads below the time labels without shifting their
        # horizontal endpoints away from the two consecutive maxima.
        full_arrow.shift(DOWN * (
            full_arrow.get_top()[1] - labels[2:].get_bottom()[1] + 0.18
        ))
        full_label = self.formula(r"T=12{,}4\ \mathrm{h}", 29, BLUE_D).next_to(
            full_arrow, DOWN, buff=0.10)
        full = VGroup(full_arrow, full_label)
        base = VGroup(axes, curve, dots, labels, probe)
        graph = VGroup(base, half, full)
        self.new_page("Le retour au sommet complète le cycle", graph)
        self.explain(
            "Le point noir suit le modèle à partir du maximum de trois heures. "
            "Suivons d'abord sa descente jusqu'au minimum suivant.",
            base,
        )
        self.play(MoveAlongPath(probe, axes.plot(height, x_range=[3, 9.2])),
                  run_time=2.4, rate_func=linear)
        self.explain(
            "Du maximum au minimum suivant, le cosinus passe de un à moins un. "
            "Sa phase augmente de pi : c'est une demi-période, six virgule deux heures.",
            half,
        )
        self.play(MoveAlongPath(probe, axes.plot(height, x_range=[9.2, 15.4])),
                  run_time=2.4, rate_func=linear)
        self.explain(
            "Il faut encore une demi-période pour retrouver le maximum suivant, "
            "à quinze virgule quatre heures. Le motif complet se répète alors. "
            "La période vaut deux fois six virgule deux, soit douze virgule quatre heures.",
            full, hold=1.6,
        )

    def _parameters(self):
        period = self.formula(r"T=2(9{,}2-3)=12{,}4\ \mathrm{h}", 43, BLUE_D)
        middle = self.formula(r"D=\frac{4{,}8+0{,}8}{2}=2{,}8\ \mathrm{m}", 42)
        amplitude = self.formula(r"A=\frac{4{,}8-0{,}8}{2}=2\ \mathrm{m}", 42)
        phase = self.words("Avec A > 0, la phase zéro place un maximum.", 29)
        self.new_page("Séparer durée et hauteurs", period, middle, amplitude, phase, gap=0.40)
        self.explain(
            "La période utilise les instants. La médiane et l'amplitude utilisent "
            "les hauteurs. La médiane est la moyenne du maximum et du minimum : "
            "deux virgule huit mètres. L'amplitude est la moitié de leur différence : deux mètres.",
            period, middle, amplitude,
        )
        self.explain(
            "Pour placer un maximum à trois heures, choisissons un cosinus "
            "de coefficient positif et décalons son origine à cet instant. "
            "L'amplitude verticale ne doit pas être confondue avec la durée du cycle.",
            phase,
        )

    def _validate_model(self):
        model = panel(self.formula(r"h(t)=2{,}8+2\cos\!\left(\frac{2\pi(t-3)}{12{,}4}\right)", 45),
                      width=11.3, height=1.3)
        units = self.words("t en heures ; h(t) en mètres.", 28)
        values = self.formula(r"h(3)=4{,}8,\quad h(9{,}2)=0{,}8,\quad h(15{,}4)=4{,}8", 38)
        failed = self.formula(r"T=6{,}2\ \Longrightarrow\ h(9{,}2)=4{,}8\ne0{,}8", 38)
        self.new_page("Vérifier les deux extrêmes", model, units, values, failed, gap=0.42)
        self.explain(
            "Dans ce modèle, la phase vaut zéro à trois heures, pi à neuf virgule deux "
            "et deux pi à quinze virgule quatre. Les hauteurs calculées retrouvent "
            "successivement le maximum, le minimum et le maximum suivant.",
            model, units, values,
        )
        self.explain(
            "Si l'on utilisait par erreur six virgule deux comme période, "
            "le modèle reviendrait déjà à son maximum à neuf virgule deux heures. "
            "Il contredirait le minimum donné. Substituer les instants permet "
            "donc de détecter directement l'erreur.",
            failed, hold=1.6,
        )

    def _missing_consecutiveness(self):
        condition = self.words("Si le minimum n'est pas forcément le suivant :", 30)
        general = self.formula(r"\Delta t=\left(j+\frac12\right)T,\qquad j=0,1,2,\ldots", 43)
        missed = self.words("j compte les cycles complets éventuellement manqués.", 28)
        self.new_page("Le mot « suivant » est essentiel", condition, general, missed, gap=0.65)
        self.explain(
            "Après un maximum, les minima d'une sinusoïde arrivent après une "
            "demi-période, puis une période et demie, puis deux périodes et demie. "
            "Le nombre entier j compte les cycles complets éventuellement manqués.",
            condition, general, missed,
        )

    def _missed_cycle_example(self):
        condition = self.words("Même intervalle observé : 6,2 heures.", 31)
        first = self.formula(r"6{,}2=\frac T2\quad\Longrightarrow\quad T=12{,}4", 42)
        later = self.formula(r"6{,}2=\frac{3T}{2}\quad\Longrightarrow\quad T=\frac{12{,}4}{3}", 42)
        warning = self.words("Les mêmes deux extrêmes ne déterminent plus T.", 29, BLUE_D)
        self.new_page("Si l'on manque un cycle", condition, first, later, warning, gap=0.50)
        self.explain(
            "Sans la précision minimum suivant, les six virgule deux heures "
            "pourraient représenter une demi-période ou trois demi-périodes. "
            "On obtiendrait deux périodes différentes, toutes deux compatibles "
            "avec ces deux observations isolées. La précision sur les extrêmes "
            "consécutifs est donc une vraie donnée, pas un détail de vocabulaire.",
            condition, first, later, warning, hold=1.6,
        )

    def _self_check(self):
        assumption = self.words("Modèle sinusoïdal non constant ; t en heures.", 29)
        times = self.formula(r"\text{Maxima consécutifs à }t=2,\ 10,\ 18", 41)
        heights = self.formula(r"h_{\max}=15\ \mathrm{m},\qquad h_{\min}=3\ \mathrm{m}", 41)
        question = self.words("Trouver T, la médiane, l'amplitude et un modèle.", 29)
        self.new_page("À vous : quel retour mesure-t-on ?", assumption, times, heights,
                      question, gap=0.52)
        self.explain(
            "Voici les données de l'exercice dix-sept point sept A, avec la "
            "précision que les maxima sont consécutifs. Ils surviennent à deux, "
            "dix et dix-huit heures et valent quinze mètres. Les minima valent "
            "trois mètres. Trouvez la période, la médiane, l'amplitude et "
            "un modèle cosinus. Prenez six secondes pour commencer.",
            assumption, times, heights, question, pause_after=6,
        )

    def _self_check_answer(self):
        period = self.formula(r"T=10-2=18-10=8\ \mathrm{h}", 42, BLUE_D)
        heights = self.formula(r"D=\frac{15+3}{2}=9,\qquad A=\frac{15-3}{2}=6", 41)
        model = self.formula(r"h(t)=9+6\cos\!\left(\frac{\pi(t-2)}4\right)", 44)
        check = self.formula(r"h(2)=15,\qquad h(6)=3,\qquad h(10)=15", 38)
        self.new_page("Un maximum au maximum suivant", period, heights, model, check, gap=0.48)
        self.explain(
            "Cette fois, on compare deux maxima consécutifs. La différence "
            "dix moins deux donne directement la période de huit heures, sans "
            "la doubler. La différence dix-huit moins dix confirme cette valeur. "
            "La médiane vaut neuf mètres et l'amplitude six mètres.",
            period, heights,
        )
        self.explain(
            "Un modèle possible est neuf plus six fois le cosinus de pi fois "
            "t moins deux, divisé par quatre. Il atteint quinze à deux heures, "
            "trois à six heures, puis quinze à dix heures. Les quatre heures "
            "du maximum au minimum sont bien la moitié de la période.",
            model, check, hold=1.6,
        )

    def _takeaway(self):
        condition = self.words("Pour une sinusoïde non constante :", 30)
        half = self.words("Maximum → minimum suivant : T/2.", 33, BLUE_D)
        full = self.words("Maximum → maximum suivant : T.", 33, BLUE_D)
        method = self.words("Nommer les extrêmes, puis vérifier les instants.", 29)
        reference = self.words("Manuel 17.7–17.8 · Cahier 17.7 A, synthèse S1", 26)
        self.new_page("Identifier la répétition", condition, half, full, method, reference,
                      gap=0.45)
        self.explain(
            "Retenez d'abord l'hypothèse : la règle de la demi-période vient "
            "du modèle sinusoïdal. Un maximum et le minimum suivant sont séparés "
            "d'une demi-période. Deux maxima consécutifs sont séparés d'une période. "
            "Identifiez ce qui se répète et vérifiez le modèle aux instants donnés. "
            "Si des extrêmes ont pu être manqués, la période demande une information supplémentaire.",
            condition, half, full, method, reference, hold=2,
        )

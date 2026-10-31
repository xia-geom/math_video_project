"""Separate spatial wavelength, temporal period and propagation speed."""

import math

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    RIGHT,
    UP,
    WHITE,
    Axes,
    DashedLine,
    DecimalNumber,
    Dot,
    DoubleArrow,
    FadeOut,
    MathTex,
    Tex,
    Text,
    ValueTracker,
    VGroup,
    config,
    linear,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class PeriodeLongueurOndeFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._spatial_snapshot()
        self._time_trace()
        self._propagation()
        self._formulas()
        self._same_photograph()
        self._self_check()
        self._self_check_answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        model = self.formula(r"y(x,t)=2\sin(\pi x-2\pi t)", 50)
        units = self.words("x et y en mètres ; t en secondes.", 30)
        question = self.words("Une répétition de 2 mètres est-elle une période ?", 29)
        self.new_page("Une distance ou une durée ?", model, units, question, gap=0.7)
        self.explain(
            "Le manuel décrit cette onde par une fonction de deux variables : "
            "la position x, en mètres, et le temps t, en secondes. "
            "La hauteur y dépend des deux.",
            model, units,
        )
        self.explain(
            "Sur une photographie, deux crêtes voisines sont séparées de deux mètres. "
            "Peut-on annoncer une période de deux secondes ? Non : une distance "
            "et une durée se mesurent avec deux expériences différentes.",
            question,
        )

    def _spatial_snapshot(self):
        axes = Axes(
            x_range=[0, 4.25, 1], y_range=[-2.5, 3.4, 1],
            x_length=8.0, y_length=2.9,
            axis_config={"color": BLACK, "include_tip": False},
        )
        curve = axes.plot(lambda x: 2 * math.sin(math.pi * x), x_range=[0, 4.25], color=BLUE_D)
        dots = VGroup(*[Dot(axes.c2p(x, 2), color=BLUE_D, radius=0.07) for x in [0.5, 2.5]])
        measure = DoubleArrow(axes.c2p(0.5, 2.7), axes.c2p(2.5, 2.7), buff=0, color=BLUE_D)
        label = self.formula(r"\lambda=2\ \mathrm{m}", 29, BLUE_D).next_to(measure, UP, buff=0.13)
        labels = VGroup(
            self.formula(r"x\ (\mathrm{m})", 27).next_to(axes.x_axis, RIGHT, buff=0.15),
            self.formula("0", 24).next_to(axes.c2p(0, 0), DOWN, buff=0.13),
            self.formula("2", 24).next_to(axes.c2p(2, 0), DOWN, buff=0.13),
            self.formula("4", 24).next_to(axes.c2p(4, 0), DOWN, buff=0.13),
        )
        graph = VGroup(axes, curve, dots, measure, label, labels)
        formula = self.formula(r"t=0:\qquad y(x,0)=2\sin(\pi x)", 40)
        self.new_page("Photographier à un instant fixé", graph, formula, gap=0.45)
        self.explain(
            "Figeons le temps à zéro. L'axe horizontal représente maintenant "
            "la position. Nous comparons plusieurs endroits au même instant.",
            axes, curve, labels, formula,
        )
        self.explain(
            "Deux crêtes consécutives sont à zéro virgule cinq et deux virgule cinq mètres. "
            "Leur distance vaut deux mètres. C'est la longueur d'onde, notée lambda. "
            "Le motif se répète dans l'espace, pas encore dans le temps.",
            dots, measure, label, hold=1.6,
        )

    def _time_trace(self):
        axes = Axes(
            x_range=[0, 2.15, 0.5], y_range=[-2.5, 3.4, 1],
            x_length=8.0, y_length=2.9,
            axis_config={"color": BLACK, "include_tip": False},
        )
        curve = axes.plot(lambda t: -2 * math.sin(2 * math.pi * t), x_range=[0, 2.15], color=BLUE_D)
        dots = VGroup(*[Dot(axes.c2p(t, 2), color=BLUE_D, radius=0.07) for t in [0.75, 1.75]])
        measure = DoubleArrow(axes.c2p(0.75, 2.7), axes.c2p(1.75, 2.7), buff=0, color=BLUE_D)
        label = self.formula(r"T=1\ \mathrm{s}", 29, BLUE_D).next_to(measure, UP, buff=0.13)
        labels = VGroup(
            self.formula(r"t\ (\mathrm{s})", 27).next_to(axes.x_axis, RIGHT, buff=0.15),
            self.formula("0", 24).next_to(axes.c2p(0, 0), DOWN, buff=0.13),
            self.formula("1", 24).next_to(axes.c2p(1, 0), DOWN, buff=0.13),
            self.formula("2", 24).next_to(axes.c2p(2, 0), DOWN, buff=0.13),
        )
        graph = VGroup(axes, curve, dots, measure, label, labels)
        formula = self.formula(r"x=0:\qquad y(0,t)=-2\sin(2\pi t)", 40)
        self.new_page("Observer un endroit au fil du temps", graph, formula, gap=0.45)
        self.explain(
            "Fixons maintenant la position à zéro et laissons passer le temps. "
            "L'axe horizontal a changé : il indique des secondes. "
            "Nous enregistrons la hauteur toujours au même endroit.",
            axes, curve, labels, formula,
        )
        self.explain(
            "Deux maxima consécutifs se produisent à zéro virgule soixante-quinze "
            "et un virgule soixante-quinze seconde. Ils sont séparés d'une seconde. "
            "C'est la période temporelle. Elle ne vaut pas deux, même si la longueur d'onde vaut deux mètres.",
            dots, measure, label, hold=1.6,
        )

    def _propagation(self):
        clock = ValueTracker(0)
        axes = Axes(
            x_range=[0, 4.25, 1], y_range=[-2.6, 2.6, 1],
            x_length=8.0, y_length=2.65,
            axis_config={"color": BLACK, "include_tip": False},
        )
        curve = axes.plot(lambda x: 2 * math.sin(math.pi * x), x_range=[0, 4.25], color=BLUE_D)
        fixed_line = DashedLine(axes.c2p(1.5, -2.5), axes.c2p(1.5, 2.5), color=BLACK)
        crest = Dot(axes.c2p(0.5, 2), radius=0.09, color=BLUE_D)
        observer = Dot(axes.c2p(1.5, -2), radius=0.095, color=BLACK)
        x_label = self.formula(r"x\ (\mathrm{m})", 27).next_to(axes.x_axis, RIGHT, buff=0.15)
        graph = VGroup(axes, curve, fixed_line, crest, observer, x_label)
        legend = self.words("Point bleu : même crête. Point noir : même position.", 28)
        elapsed = DecimalNumber(0, num_decimal_places=2, font_size=33, color=BLACK)
        time_label = VGroup(self.formula("t=", 33), elapsed, self.formula(r"\mathrm{s}", 33)).arrange(RIGHT, buff=0.15)
        self.new_page("Suivre la crête ou rester sur place", legend, graph, time_label, gap=0.32)
        self.explain(
            "Le point bleu suit une crête particulière. Le point noir, lui, "
            "reste à une position horizontale fixe et indique la hauteur de "
            "l'onde à cet endroit. Regardons une seconde du modèle, affichée au ralenti.",
            legend, graph, time_label,
        )
        curve.add_updater(lambda mob: mob.become(axes.plot(
            lambda x: 2 * math.sin(math.pi * x - 2 * math.pi * clock.get_value()),
            x_range=[0, 4.25], color=BLUE_D,
        )))
        crest.add_updater(lambda mob: mob.move_to(axes.c2p(0.5 + 2 * clock.get_value(), 2)))
        observer.add_updater(lambda mob: mob.move_to(axes.c2p(
            1.5, 2 * math.sin(1.5 * math.pi - 2 * math.pi * clock.get_value()),
        )))
        elapsed.add_updater(lambda mob: mob.set_value(clock.get_value()))
        self.play(clock.animate.set_value(1), run_time=4, rate_func=linear)
        for mob in (curve, crest, observer, elapsed):
            mob.clear_updaters()
        # Dynamic objects remain owned by this page and cannot reappear later.
        speed = self.formula(r"v=\frac{2\ \mathrm{m}}{1\ \mathrm{s}}=2\ \mathrm{m/s}", 39)
        speed.move_to(time_label)
        self.page.add(speed)
        self.play(FadeOut(time_label), run_time=0.35)
        self.explain(
            "En une seconde, la même crête avance de deux mètres. "
            "Le point fixe accomplit un cycle vertical. La vitesse de propagation "
            "décrit le mouvement du profil, et non la vitesse verticale du point noir.",
            speed, hold=1.6,
        )

    def _formulas(self):
        model = self.formula(r"y=A\sin(kx-\omega t+\varphi)", 43)
        assumptions = self.formula(r"A\ne0,\qquad k>0,\qquad\omega>0", 35)
        periods = self.formula(r"\lambda=\frac{2\pi}{k},\qquad T=\frac{2\pi}{\omega},\qquad f=\frac1T", 43)
        speed = self.formula(r"v=\frac{\lambda}{T}=\frac{\omega}{k}>0", 45, BLUE_D)
        note = self.words("Avec + ωt, le profil se déplace dans l'autre sens.", 28)
        self.new_page("Relier les trois mesures", model, assumptions, periods, speed, note, gap=0.30)
        self.explain(
            "Dans cette forme générale, une répétition complète correspond "
            "à deux pi radians de phase. À temps fixé, k fois la longueur d'onde "
            "vaut deux pi. À position fixée, oméga fois la période vaut deux pi. "
            "La fréquence est l'inverse de la période.",
            model, assumptions, periods,
        )
        self.explain(
            "Pendant une période, une crête avance d'une longueur d'onde. "
            "Sa vitesse est donc lambda divisé par T, en mètres par seconde. "
            "Avec k et oméga positifs, le signe moins devant oméga t donne "
            "un déplacement vers les x croissants. Le signe plus inverse ce sens.",
            speed, note,
        )

    def _same_photograph(self):
        first = self.formula(r"y_1(x,t)=2\sin(\pi x-2\pi t),\qquad T_1=1\ \mathrm{s}", 39)
        second = self.formula(r"y_2(x,t)=2\sin(\pi x-4\pi t),\qquad T_2=\tfrac12\ \mathrm{s}", 39)
        snapshot = self.formula(r"y_1(x,0)=y_2(x,0)=2\sin(\pi x)", 43)
        conclusion = self.words("Une photographie seule ne donne pas la période temporelle.", 28, BLUE_D)
        self.new_page("Même photographie, deux rythmes", first, second, snapshot, conclusion, gap=0.45)
        self.explain(
            "Ces deux ondes ont la même longueur d'onde, mais la seconde "
            "oscille deux fois plus vite. Sa période est une demi-seconde, "
            "au lieu d'une seconde.",
            first, second,
        )
        self.explain(
            "À l'instant zéro, leurs formules donnent pourtant exactement "
            "la même photographie. Une courbe spatiale seule ne permet donc "
            "pas de connaître la période temporelle : il manque une information sur le temps.",
            snapshot, conclusion,
        )

    def _self_check(self):
        model = self.formula(r"y(x,t)=3\sin\left(\frac{2\pi}{5}x-4\pi t\right)", 47)
        units = self.words("x et y en mètres ; t en secondes.", 29)
        first = self.words("Longueur d'onde, période, vitesse et sens ?", 29)
        second = self.words("Amplitude et fréquence ?", 29)
        self.new_page("À vous : le modèle du cahier", model, units, first, second, gap=0.45)
        self.explain(
            "À vous, avec l'exercice dix-sept point cinq A du cahier. "
            "Repérez séparément le coefficient de x et celui du temps. "
            "Trouvez la longueur d'onde, la période et la vitesse de propagation, "
            "en précisant le sens. Donnez aussi l'amplitude et la fréquence, avec leurs unités.",
            model, units, first, second, pause_after=6,
        )

    def _self_check_answer(self):
        coefficients = self.formula(r"k=\frac{2\pi}{5},\qquad\omega=4\pi,\qquad |A|=3\ \mathrm{m}", 41)
        periods = self.formula(r"\lambda=5\ \mathrm{m},\qquad T=\frac12\ \mathrm{s},\qquad f=2\ \mathrm{Hz}", 43)
        speed = self.formula(r"v=\frac{5}{1/2}=10\ \mathrm{m/s}", 48, BLUE_D)
        sense = self.words("Le profil se déplace vers les x croissants.", 29)
        self.new_page("Des unités pour vérifier la réponse", coefficients, periods, speed, sense, gap=0.45)
        self.explain(
            "Le coefficient spatial est deux pi sur cinq, donc la longueur "
            "d'onde vaut cinq mètres. Le coefficient temporel vaut quatre pi : "
            "la période vaut une demi-seconde et la fréquence deux hertz. "
            "L'amplitude reste trois mètres.",
            coefficients, periods,
        )
        self.explain(
            "Cinq mètres parcourus en une demi-seconde donnent dix mètres "
            "par seconde. Le signe moins devant le terme temporel indique "
            "un déplacement vers les x croissants. La hauteur trois ne sert "
            "pas à calculer cette vitesse.",
            speed, sense,
        )

    def _takeaway(self):
        spatial = self.words("Temps fixé : une distance, la longueur d'onde.", 29)
        temporal = self.words("Position fixée : une durée, la période.", 29)
        connection = self.formula(r"v=\frac{\lambda}{T}\quad\text{en mètres par seconde}", 38, BLUE_D)
        reference = self.words("Manuel 17.5 · Cahier 17.5 A–C", 28)
        self.new_page("Lire l'axe avant la formule", spatial, temporal, connection, reference, gap=0.55)
        self.explain(
            "Avant de mesurer une répétition, regardez ce que représente "
            "l'axe horizontal. Une photographie donne une distance. "
            "Un enregistrement au même endroit donne une durée. "
            "La vitesse relie ces deux mesures.",
            spatial, temporal, connection, reference,
        )

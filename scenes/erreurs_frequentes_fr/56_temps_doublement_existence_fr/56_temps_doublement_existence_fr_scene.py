"""Check existence and the time domain before computing a doubling time."""

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    LEFT,
    RIGHT,
    WHITE,
    Axes,
    Create,
    DashedLine,
    Dot,
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


class TempsDoublementExistenceFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._future_graph()
        self._negative_time()
        self._growth_condition()
        self._constant_cases()
        self._half_life()
        self._self_check()
        self._self_check_answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        model = self.formula(r"Q(t)=100(0{,}8)^t,\qquad t\ge0", 49)
        domain = self.words("Le temps est réel, en heures, à partir de maintenant.", 28)
        target = self.formula(r"Q(T_d)=200\qquad\text{avec }T_d>0\;?", 43)
        self.new_page("Le double sera-t-il atteint ?", model, domain, target, gap=0.65)
        self.explain(
            "Une quantité vaut cent au départ et est multipliée par zéro virgule huit "
            "chaque heure. Nous utilisons ici un modèle continu : le temps peut être "
            "un nombre réel positif. Dans combien de temps la quantité va-t-elle doubler ?",
            model, domain,
        )
        self.explain(
            "Avant d'appliquer une formule avec un logarithme, demandons-nous si "
            "le modèle peut atteindre deux cents dans le futur. La valeur cherchée "
            "doit respecter à la fois l'équation et le domaine du temps.",
            target,
        )

    def _future_graph(self):
        axes = Axes(
            x_range=[0, 8, 2], y_range=[0, 220, 100],
            x_length=8.4, y_length=2.75,
            axis_config={"color": BLACK, "include_tip": False},
        )
        curve = axes.plot(lambda t: 100 * 0.8**t, x_range=[0, 8], color=BLUE_D)
        target = DashedLine(axes.c2p(0, 200), axes.c2p(8, 200), color=BLACK)
        labels = VGroup(
            self.formula("100", 25).next_to(axes.c2p(0, 100), LEFT, buff=0.15),
            self.formula("200", 25).next_to(axes.c2p(0, 200), LEFT, buff=0.15),
            self.formula("0", 24).next_to(axes.c2p(0, 0), DOWN, buff=0.13),
            self.formula("8", 24).next_to(axes.c2p(8, 0), DOWN, buff=0.13),
            self.formula(r"t\ (\mathrm{h})", 28).next_to(axes.x_axis, RIGHT, buff=0.18),
        )
        probe = Dot(axes.c2p(0, 100), radius=0.075, color=BLUE_D)
        graph = VGroup(axes, curve, target, labels, probe)
        bound = self.formula(r"t\ge0\quad\Longrightarrow\quad0<Q(t)\le100<200", 37)
        self.new_page("Une cible hors d'atteinte", graph, bound, gap=0.45)
        self.explain(
            "La courbe part de cent et descend. La ligne horizontale à deux cents "
            "reste au-dessus. Suivons la quantité pendant les huit premières heures.",
            axes, target, labels, probe,
        )
        self.play(Create(curve), run_time=1.2)
        self.play(MoveAlongPath(probe, curve), run_time=2.8, rate_func=linear)
        self.explain(
            "Le dessin suggère une impossibilité ; l'inégalité la prouve pour "
            "tout temps positif. Zéro virgule huit à une puissance positive est "
            "au plus un. La quantité ne dépasse donc jamais cent. Elle ne peut pas doubler.",
            bound, hold=1.6,
        )

    def _negative_time(self):
        equation = self.formula(r"100(0{,}8)^t=200\quad\Longleftrightarrow\quad(0{,}8)^t=2", 39)
        formal = self.formula(r"t=\frac{\ln2}{\ln(0{,}8)}\approx-3{,}11\ \mathrm{h}", 46)
        past = self.words("Un temps négatif se situe avant l'instant initial.", 29)
        verdict = self.words("Aucune solution dans le domaine demandé : t ≥ 0.", 28, BLUE_D)
        self.new_page("Un résultat à interpréter", equation, formal, past, verdict, gap=0.45)
        self.explain(
            "Si nous résolvons tout de même l'équation, le logarithme donne "
            "environ moins trois virgule onze heures. Le calcul algébrique "
            "n'est pas faux : il décrit le prolongement de la courbe vers le passé.",
            equation, formal,
        )
        self.explain(
            "Mais le modèle étudié commence à l'instant zéro. Ce temps négatif "
            "n'appartient pas à son domaine. Prendre sa valeur absolue ne réparerait "
            "rien : à plus trois virgule onze heures, la quantité n'a pas doublé.",
            past, verdict,
        )

    def _growth_condition(self):
        assumptions = self.formula(r"Q(t)=Q_0b^t,\qquad Q_0>0,\quad b>1", 43)
        reduction = self.formula(r"Q(T_d)=2Q_0\quad\Longleftrightarrow\quad b^{T_d}=2", 43)
        result = panel(self.formula(r"T_d=\frac{\ln2}{\ln b}>0", 48), width=7.2)
        self.new_page("La formule a des hypothèses", assumptions, reduction, result, gap=0.45)
        self.explain(
            "Pour une valeur initiale strictement positive et un facteur "
            "supérieur à un, la quantité augmente. Nous pouvons diviser par "
            "la valeur initiale et chercher quand la puissance de b vaut deux.",
            assumptions, reduction,
        )
        self.explain(
            "Le logarithme de b est alors positif, tout comme celui de deux. "
            "Le quotient donne bien un temps futur. Dans ce modèle continu, "
            "il est unique et ne dépend pas de la valeur initiale positive.",
            result,
        )

    def _constant_cases(self):
        constant = self.formula(r"Q_0>0,\ b=1:\qquad Q(t)=Q_0\ne2Q_0", 40)
        no_division = self.formula(r"\ln1=0:\quad\frac{\ln2}{\ln1}\text{ n'est pas défini}", 38)
        zero = self.formula(r"Q_0=0,\ b>0:\qquad Q(t)=0=2Q_0", 40)
        note = self.words("Tous les temps conviennent : aucun temps unique.", 28)
        self.new_page("Deux cas constants", constant, no_division, zero, note, gap=0.45)
        self.explain(
            "Si b vaut un et que la quantité initiale est positive, la quantité "
            "reste constante. Elle ne double pas. La formule ne s'applique pas, "
            "puisque son dénominateur serait le logarithme de un, donc zéro.",
            constant, no_division,
        )
        self.explain(
            "Si la quantité initiale vaut zéro, le modèle reste nul. L'égalité "
            "avec le double de zéro est vraie à tous les instants. Elle ne "
            "détermine aucun temps de doublement unique, et on ne peut pas diviser par zéro.",
            zero, note,
        )

    def _half_life(self):
        target = self.formula(r"100(0{,}8)^t=50\quad\Longleftrightarrow\quad(0{,}8)^t=\frac12", 40)
        result = self.formula(r"T_{1/2}=\frac{\ln(1/2)}{\ln(0{,}8)}\approx3{,}11\ \mathrm{h}", 45, BLUE_D)
        signs = self.words("Deux logarithmes négatifs donnent un temps positif.", 29)
        self.new_page("Une cible adaptée : la moitié", target, result, signs, gap=0.65)
        self.explain(
            "Revenons à notre quantité décroissante. Atteindre cinquante, "
            "la moitié de cent, est cette fois possible. L'équation contient "
            "un demi à droite, et non deux.",
            target,
        )
        self.explain(
            "Les deux logarithmes sont négatifs. Leur quotient est positif, "
            "environ trois virgule onze heures : c'est une demi-vie. "
            "Changer la cible change le problème, pas seulement le signe du résultat.",
            result, signs,
        )

    def _self_check(self):
        model = self.formula(r"R(t)=80(1{,}25)^t,\qquad t\ge0", 48)
        units = self.words("Le temps réel est mesuré en heures.", 29)
        question = self.words("Un doublement futur existe-t-il ? Si oui, quand ?", 29)
        self.new_page("À vous : vérifier avant de calculer", model, units, question, gap=0.65)
        self.explain(
            "À vous. Le modèle commence à quatre-vingts et son facteur vaut "
            "un virgule vingt-cinq par heure. Vérifiez d'abord si un doublement "
            "futur existe. Ensuite seulement, donnez son temps exact avec des logarithmes.",
            model, units, question, pause_after=6,
        )

    def _self_check_answer(self):
        conditions = self.formula(r"80>0,\qquad1{,}25>1", 45)
        result = self.formula(r"T_d=\frac{\ln2}{\ln(1{,}25)}\approx3{,}11\ \mathrm{h}", 45, BLUE_D)
        check = self.formula(r"(1{,}25)^{T_d}=2\quad\Longrightarrow\quad R(T_d)=160", 41)
        self.new_page("Un temps positif, une cible atteinte", conditions, result, check, gap=0.6)
        self.explain(
            "Les deux hypothèses sont satisfaites : valeur initiale positive "
            "et facteur supérieur à un. Le temps de doublement vaut donc "
            "logarithme de deux divisé par logarithme de un virgule vingt-cinq, "
            "soit environ trois virgule onze heures.",
            conditions, result,
        )
        self.explain(
            "Avec la valeur exacte du temps, le facteur total vaut deux. "
            "La quantité passe bien de quatre-vingts à cent soixante. "
            "Cette vérification relie le résultat du calcul à la question posée.",
            check,
        )

    def _takeaway(self):
        rule = self.words("Vérifier la cible, les hypothèses et le domaine du temps.", 29, BLUE_D)
        reference = self.words("Manuel 6.6 et 6.8 · Cahier 6.5 A–B, 6.6 C", 28)
        self.new_page("Le réflexe à garder", rule, reference, gap=0.8)
        self.explain(
            "Un logarithme fournit un candidat, pas une garantie d'existence "
            "dans le futur. Avant la formule, contrôlez la cible, les hypothèses "
            "et le domaine du temps. Le manuel distingue ainsi le doublement "
            "d'une quantité croissante et la demi-vie d'une quantité décroissante.",
            rule, reference,
        )

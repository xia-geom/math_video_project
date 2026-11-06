"""Successive percentage changes use successive bases, with bars at one scale."""
from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    LEFT,
    RED_D,
    RIGHT,
    WHITE,
    DashedLine,
    MathTex,
    Rectangle,
    Tex,
    Text,
    Transform,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class PourcentagesSuccessifsFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._apparent_cancellation()
        self._changing_bars()
        self._compare_the_amounts()
        self._multiplicative_model()
        self._general_rule()
        self._self_check()
        self._self_check_answer()
        self._closing()
        self.wait(1.2)

    def _apparent_cancellation(self):
        start = self.words("Un prix de 84 dollars", 35)
        changes = self.formula(r"+15\%\qquad\text{puis}\qquad-15\%", 52)
        guess = self.formula(r"84\quad\overset{?}{\longrightarrow}\quad84", 56, RED_D)
        question = self.words("Les deux variations s’annulent-elles ?", 31)
        self.new_page("Même pourcentage, même montant ?", start, changes, guess, question, gap=0.40)
        self.explain(
            "Un prix de quatre-vingt-quatre dollars augmente de quinze pour cent, "
            "puis diminue de quinze pour cent. On pourrait penser que plus quinze "
            "et moins quinze s’annulent. Le prix reviendrait alors à son montant de départ.",
            start, changes, guess,
        )
        self.explain(
            "Mais quinze pour cent de quelle somme ? Cette question va déterminer "
            "la réponse. Il faut regarder la base de chaque calcul.",
            question,
        )

    def _changing_bars(self):
        initial_width = 6.0
        initial_left = -2.8
        ys = [1.05, 0.0, -1.05]
        bars = VGroup(*[
            Rectangle(
                width=width, height=0.55, stroke_color=BLUE_D, stroke_width=2.5,
                fill_color=BLUE_D, fill_opacity=0.12,
            ).move_to([initial_left + width / 2, y, 0])
            for width, y in zip([initial_width, initial_width, initial_width * 1.15], ys, strict=True)
        ])
        names = VGroup(*[
            self.words(name, 29).move_to([-4.85, y, 0])
            for name, y in zip(["Départ", "Hausse", "Baisse"], ys, strict=True)
        ])
        values = VGroup(*[
            self.formula(value, 36).move_to([5.0, y, 0])
            for value, y in zip([r"84", r"96{,}60", r"82{,}11"], ys, strict=True)
        ])
        reference = DashedLine(
            [initial_left + initial_width, 1.58, 0],
            [initial_left + initial_width, -1.58, 0],
            color=BLACK, stroke_width=1.5,
        )
        chart = VGroup(bars, names, values, reference)
        scale_note = self.words("Même échelle pour les trois montants.", 29, BLUE_D)
        self.new_page("Suivre le prix, étape par étape", chart, scale_note, gap=0.40)
        self.explain(
            "Ces barres utilisent toutes la même échelle. La première représente "
            "le prix initial. Le trait vertical garde sa longueur en mémoire "
            "pour comparer les montants suivants.",
            bars[0], names[0], values[0], reference, scale_note,
        )
        self.explain(
            "Pour la hausse, on part de quatre-vingt-quatre. Ajouter quinze pour "
            "cent revient à multiplier ce montant par un virgule quinze. Regardons la barre s’allonger.",
            bars[1], names[1],
        )
        raised = bars[1].copy().stretch_to_fit_width(initial_width * 1.15).align_to(bars[1], LEFT)
        self.play(Transform(bars[1], raised), run_time=1.6)
        self.explain(
            "Le nouveau prix est quatre-vingt-seize dollars et soixante cents. "
            "C’est maintenant cette somme qui sert de base à la baisse.",
            values[1],
        )
        self.explain(
            "La troisième barre commence donc à ce nouveau montant. Une baisse "
            "de quinze pour cent en conserve quatre-vingt-cinq pour cent : on multiplie par zéro virgule quatre-vingt-cinq.",
            bars[2], names[2],
        )
        reduced = bars[2].copy().stretch_to_fit_width(initial_width * 1.15 * 0.85).align_to(bars[2], LEFT)
        self.play(Transform(bars[2], reduced), run_time=1.6)
        self.explain(
            "Il reste quatre-vingt-deux dollars et onze cents. La barre finale "
            "est plus courte que la première : les deux variations ne se compensent pas.",
            values[2],
        )

    def _compare_the_amounts(self):
        added = panel(
            VGroup(
                self.words("Montant ajouté", 29, BLUE_D),
                self.formula(r"0{,}15\times84", 40),
                self.formula(r"=12{,}60", 44),
            ).arrange(DOWN, buff=0.24),
            width=5.3, height=2.15,
        )
        removed = panel(
            VGroup(
                self.words("Montant retiré", 29, BLUE_D),
                self.formula(r"0{,}15\times96{,}60", 39),
                self.formula(r"=14{,}49", 44),
            ).arrange(DOWN, buff=0.24),
            width=5.3, height=2.15,
        )
        comparison = VGroup(added, removed).arrange(RIGHT, buff=0.5)
        difference = self.formula(r"14{,}49-12{,}60=1{,}89", 45)
        self.new_page("La même part, mais d’une autre base", comparison, difference, gap=0.55)
        self.explain(
            "La hausse a ajouté douze dollars et soixante cents. La baisse retire "
            "quatorze dollars et quarante-neuf cents, parce qu’elle porte sur une base "
            "plus grande. On retire donc un dollar et quatre-vingt-neuf cents de plus qu’on avait ajouté.",
            comparison, difference,
        )

    def _multiplicative_model(self):
        first = self.formula(r"84(1+0{,}15)=84(1{,}15)", 44)
        both = panel(self.formula(r"84(1{,}15)(0{,}85)=82{,}11", 48), width=10, height=1.35)
        factor = self.formula(r"1{,}15\times0{,}85=0{,}9775", 44, BLUE_D)
        meaning = self.words("Le prix final vaut 97,75 % du prix initial.", 30)
        self.new_page("Multiplier les facteurs successifs", first, both, factor, meaning, gap=0.35)
        self.explain(
            "La bonne écriture conserve les deux facteurs multiplicatifs. On ne "
            "soustrait pas simplement les taux annoncés. Le produit des facteurs "
            "vaut zéro virgule neuf mille sept cent soixante-quinze.",
            first, both, factor,
        )
        self.explain(
            "Cela signifie que le prix final représente quatre-vingt-dix-sept "
            "virgule soixante-quinze pour cent du prix initial. La perte totale est donc de deux virgule vingt-cinq pour cent.",
            meaning,
        )

    def _general_rule(self):
        conditions = self.formula(r"V>0,\qquad 0\le r\le1", 40, BLUE_D)
        explanation = self.words("r est le taux écrit sous forme décimale.", 29)
        identity = self.formula(r"V(1+r)(1-r)=V(1-r^2)", 48)
        example = self.formula(r"r=0{,}15:\qquad r^2=0{,}0225", 42)
        self.new_page("Pourquoi il reste une baisse", conditions, explanation, identity, example, gap=0.45)
        self.explain(
            "Plus généralement, appelons r le taux sous forme décimale. "
            "L’identité remarquable un plus r, fois un moins r, donne un moins "
            "r au carré. Après ces deux variations, il manque donc la proportion "
            "r au carré du montant initial.",
            conditions, explanation, identity,
        )
        self.explain(
            "Avec quinze pour cent, r vaut zéro virgule quinze. Son carré "
            "vaut zéro virgule zéro deux deux cinq, soit deux virgule vingt-cinq pour cent.",
            example,
        )

    def _self_check(self):
        initial = self.formula(r"100", 60)
        changes = self.formula(r"+20\%\qquad\text{puis}\qquad-20\%", 52)
        question = self.words("Quel montant final ? Quel pourcentage de perte ?", 29)
        self.new_page("À vous de calculer", initial, changes, question, gap=0.65)
        self.explain(
            "À vous. Un montant de cent augmente de vingt pour cent, puis diminue "
            "de vingt pour cent. Calculez le montant final et la perte totale "
            "en pourcentage du montant initial.",
            initial, changes, question, pause_after=6,
        )

    def _self_check_answer(self):
        steps = self.formula(r"100\ \xrightarrow{\times1{,}2}\ 120"
                             r"\ \xrightarrow{\times0{,}8}\ 96", 48)
        direct = self.formula(r"100(1-0{,}2^2)=100(0{,}96)=96", 44)
        result = self.words("Une perte de 4 %, calculée sur le montant initial.", 29, GREEN_D)
        self.new_page("Les deux méthodes concordent", steps, direct, result, gap=0.65)
        self.explain(
            "La hausse donne cent vingt. La baisse retire vingt pour cent de "
            "cent vingt, soit vingt-quatre : il reste quatre-vingt-seize. "
            "La formule générale donne le même résultat. La perte est de quatre pour cent.",
            steps, direct, result,
        )

    def _closing(self):
        question = self.words("Un pourcentage de quelle base ?", 35, BLUE_D)
        rule = self.words("Pour plusieurs variations : multiplier les facteurs.", 29)
        reference = self.words("MAT0339 · Cahier, chapitre 1, synthèse S2", 28)
        self.new_page("La question à poser", question, rule, reference, gap=0.65)
        self.explain(
            "Devant des pourcentages successifs, demandez toujours quelle est "
            "la base du calcul. Traduisez chaque variation par un facteur, puis multipliez ces facteurs.",
            question, rule, reference,
        )

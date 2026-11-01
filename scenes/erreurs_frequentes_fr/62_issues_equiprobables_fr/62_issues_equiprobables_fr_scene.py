"""Count equally likely elementary outcomes, not merely displayed categories."""

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    RED_D,
    RIGHT,
    UP,
    WHITE,
    MathTex,
    Rectangle,
    Tex,
    Text,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class IssuesEquiprobablesFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._coin_outcomes()
        self._distribution()
        self._dice_example()
        self._unequal_weights()
        self._self_check()
        self._answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        model = self.words("Deux lancers indépendants d'une pièce équilibrée.", 29)
        variable = self.formula(r"N=\text{nombre de piles},\qquad N\in\{0,1,2\}", 39)
        attempt = panel(self.formula(r"P(N=1)\stackrel{?}{=}\frac13", 49, RED_D), width=7)
        self.new_page("Trois résultats : trois chances égales ?", model, variable, attempt)
        self.explain(
            "Nous lançons deux fois une pièce équilibrée, de façon indépendante. "
            "Le nombre de piles peut être zéro, un ou deux. Une réponse tentante "
            "consiste à attribuer une chance sur trois à chacun de ces trois nombres.",
            model, variable,
        )
        self.explain(
            "La liste des valeurs possibles est correcte. Mais cette liste ne "
            "dit pas encore si ces valeurs ont la même probabilité. Revenons "
            "aux résultats de chacun des deux lancers.",
            attempt,
        )

    def _coin_outcomes(self):
        cards = VGroup()
        boxes = []
        for outcome, count in [("FF", 0), ("FP", 1), ("PF", 1), ("PP", 2)]:
            box = Rectangle(width=2.0, height=1.6, color=BLACK, stroke_width=2)
            name = self.formula(outcome, 39)
            probability = self.formula(r"\frac14", 29)
            VGroup(name, probability).arrange(DOWN, buff=0.13).move_to(box)
            label = self.formula(f"N={count}", 32).next_to(box, DOWN, buff=0.25)
            cards.add(VGroup(box, name, probability, label))
            boxes.append(box)
        cards.arrange(RIGHT, buff=0.55)
        legend = self.words("F : face · P : pile · l'ordre des lancers est conservé", 28)
        result = self.formula(r"\{N=1\}=\{FP,PF\}:\qquad P(N=1)=\frac24=\frac12", 39)
        self.new_page("Quatre issues élémentaires", legend, cards, result, gap=0.55)
        self.explain(
            "Face puis pile et pile puis face sont deux issues différentes. "
            "Avec les hypothèses annoncées, chacune des quatre suites a une "
            "probabilité égale à un demi fois un demi, donc un quart.",
            legend, cards,
        )
        self.play(
            boxes[1].animate.set_fill(BLUE_D, opacity=0.16).set_stroke(BLUE_D),
            boxes[2].animate.set_fill(BLUE_D, opacity=0.16).set_stroke(BLUE_D),
            run_time=0.8,
        )
        self.explain(
            "Exactement un pile correspond aux deux cases centrales. On additionne "
            "leurs probabilités : un quart plus un quart donne un demi. Nous avons "
            "compté deux issues sur quatre, et non une valeur sur trois.",
            result, hold=1.4,
        )

    def _distribution(self):
        groups = VGroup()
        for n, height, fraction in [(0, 1.15, r"\frac14"), (1, 2.3, r"\frac12"), (2, 1.15, r"\frac14")]:
            bar = Rectangle(width=1.15, height=height, color=BLUE_D,
                            fill_color=BLUE_D, fill_opacity=0.12)
            bar.move_to([2.5 * (n - 1), height / 2, 0])
            value = self.formula(fraction, 34).next_to(bar, UP, buff=0.16)
            category = self.formula(f"N={n}", 31).next_to(bar, DOWN, buff=0.2)
            groups.add(VGroup(bar, value, category))
        caption = self.words("Une même échelle de probabilité pour les trois barres.", 28)
        self.new_page("Regrouper change le poids des catégories", groups, caption, gap=0.45)
        self.explain(
            "Les trois catégories existent, mais elles ne regroupent pas le même "
            "nombre d'issues élémentaires. La barre de un pile est deux fois plus "
            "haute que les deux autres. Les trois probabilités totalisent un.",
            groups,
        )
        self.explain(
            "Attribuer un tiers à chaque catégorie aurait aussi donné une somme "
            "égale à un. Ce contrôle est nécessaire, mais il ne suffit pas. "
            "Il faut justifier les poids à partir du modèle de l'expérience.",
            caption,
        )

    def _dice_grid(self, predicate):
        cells = VGroup()
        selected = VGroup()
        step = 0.46
        for first in range(1, 7):
            for second in range(1, 7):
                cell = Rectangle(width=step, height=step, color=BLACK, stroke_width=1)
                cell.move_to([(second - 3.5) * step, (3.5 - first) * step, 0])
                cells.add(cell)
                if predicate(first, second):
                    selected.add(cell)
        labels = VGroup()
        for n in range(1, 7):
            labels.add(self.formula(str(n), 26).move_to([(n - 3.5) * step, 1.7, 0]))
            labels.add(self.formula(str(n), 26).move_to([-1.7, (3.5 - n) * step, 0]))
        axes = VGroup(
            self.words("Dé 2", 28).move_to([0, 2.15, 0]),
            self.words("Dé 1", 28).move_to([-2.4, 0, 0]),
        )
        return VGroup(cells, labels, axes), selected

    def _dice_example(self):
        grid, selected = self._dice_grid(lambda a, b: a + b == 7)
        calculations = VGroup(
            self.formula(r"36\text{ couples équiprobables}", 32),
            self.formula(r"P(S=7)=\frac6{36}=\frac16", 39, BLUE_D),
            self.formula(r"P(S=2)=\frac1{36}", 37),
        ).arrange(DOWN, buff=0.6)
        body = VGroup(grid, calculations).arrange(RIGHT, buff=0.7)
        self.new_page("Deux dés : compter les couples", body)
        self.explain(
            "Lançons maintenant deux dés équilibrés et indépendants, distingués "
            "par leur numéro. Une ligne donne le premier dé et une colonne le "
            "second. Chacun des trente-six couples a une chance sur trente-six.",
            grid, calculations[0],
        )
        self.play(*(cell.animate.set_fill(BLUE_D, opacity=0.35) for cell in selected), run_time=0.8)
        self.explain(
            "Six couples donnent la somme sept. La somme deux ne provient que "
            "du couple un, un. Les onze sommes possibles, de deux à douze, "
            "ne sont donc pas onze résultats équiprobables.",
            calculations[1], calculations[2], hold=1.4,
        )

    def _unequal_weights(self):
        assumption = self.formula(r"P(P)=0{,}6,\qquad\text{lancers indépendants}", 39)
        paths = self.formula(r"P(FP)=0{,}4\times0{,}6,\quad P(PF)=0{,}6\times0{,}4", 35)
        result = self.formula(r"P(N=1)=0{,}24+0{,}24=0{,}48", 44, BLUE_D)
        self.new_page("Si la pièce est biaisée, les poids changent", assumption, paths, result, gap=0.65)
        self.explain(
            "Les quatre mêmes suites restent possibles avec une pièce biaisée. "
            "Supposons que pile ait une probabilité de zéro virgule six, avec "
            "toujours deux lancers indépendants. Les cases ne valent plus toutes un quart.",
            assumption,
        )
        self.explain(
            "On calcule alors le poids de chaque chemin. Face puis pile et pile "
            "puis face valent chacun zéro virgule vingt-quatre. Leur somme est "
            "zéro virgule quarante-huit. Le rapport des nombres de cases serait ici incorrect.",
            paths, result,
        )

    def _self_check(self):
        assumption = self.words("Deux dés équilibrés, indépendants et distinguables.", 28)
        question = self.formula(r"P(S\ge10)=\ ?", 54)
        hint = self.words("Comptez les couples, puis choisissez le dénominateur.", 29)
        self.new_page("À vous : au moins dix", assumption, question, hint, gap=0.7)
        self.explain(
            "À vous. Avec les deux dés équilibrés et indépendants, quelle est "
            "la probabilité d'une somme au moins égale à dix ? Les sommes dix, "
            "onze et douze conviennent. Comptez les couples qui les produisent.",
            assumption, question, hint, pause_after=6,
        )

    def _answer(self):
        grid, selected = self._dice_grid(lambda a, b: a + b >= 10)
        counts = VGroup(
            self.formula(r"10:\ (4,6),(5,5),(6,4)", 31),
            self.formula(r"11:\ (5,6),(6,5)", 31),
            self.formula(r"12:\ (6,6)", 31),
            self.formula(r"P(S\ge10)=\frac{3+2+1}{36}=\frac16", 36, BLUE_D),
        ).arrange(DOWN, buff=0.4)
        body = VGroup(grid, counts).arrange(RIGHT, buff=0.65)
        self.new_page("Six couples favorables sur trente-six", body)
        self.explain(
            "La somme dix correspond à trois couples, onze à deux couples et "
            "douze à un seul. Ce sont six cases distinctes parmi les trente-six "
            "cases équiprobables.",
            grid, counts[0], counts[1], counts[2],
        )
        self.play(*(cell.animate.set_fill(BLUE_D, opacity=0.35) for cell in selected), run_time=0.8)
        self.explain(
            "La probabilité est six sur trente-six, soit un sixième. Compter "
            "trois sommes sur onze donnerait trois onzièmes et attribuerait "
            "à tort le même poids à des catégories de tailles différentes.",
            counts[3], hold=1.4,
        )

    def _takeaway(self):
        assumptions = self.words("Univers fini et issues équiprobables", 30)
        rule = panel(self.formula(r"P(A)=\frac{|A|}{|\Omega|}", 48), width=7.0)
        check = self.words("Préciser l'expérience, les issues et leurs poids.", 30)
        reference = self.words("Manuel 8.2 et 8.9 · Cahier 8.2 B–C", 28)
        self.new_page("Le réflexe à garder", assumptions, rule, check, reference, gap=0.4)
        self.explain(
            "Avant de compter, précisez l'expérience, les issues et leurs "
            "probabilités. Dans un univers fini équiprobable, le rapport des "
            "nombres de cas fonctionne. Sinon, additionnez les probabilités "
            "des issues favorables. Une liste de possibilités ne prouve jamais, "
            "à elle seule, que leurs chances sont égales.",
            assumptions, rule, check, reference,
        )

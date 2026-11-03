"""Update conditional probabilities after each draw without replacement."""

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    LEFT,
    RED_D,
    RIGHT,
    WHITE,
    Circle,
    Dot,
    FadeOut,
    Line,
    MathTex,
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


class TiragesSansRemiseFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._update_bag()
        self._tree()
        self._two_red()
        self._one_each()
        self._unconditional_probability()
        self._replacement_comparison()
        self._self_check()
        self._answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        bag = self.words("5 boules rouges et 3 bleues · deux tirages sans remise", 28)
        uniform = self.words("À chaque tirage, chaque boule restante a la même chance.", 28)
        attempt = panel(self.formula(r"P(R_1\cap R_2)\stackrel{?}{=}\frac58\times\frac58", 43, RED_D), width=9)
        self.new_page("Le sac a-t-il encore la même composition ?", bag, uniform, attempt)
        self.explain(
            "Un sac contient cinq boules rouges et trois boules bleues. Nous "
            "tirons deux boules sans remettre la première. À chaque étape, "
            "toutes les boules encore présentes ont la même chance d'être choisies.",
            bag, uniform,
        )
        self.explain(
            "R un signifie rouge au premier tirage et R deux rouge au second. "
            "Pour obtenir deux rouges, peut-on multiplier cinq huitièmes par "
            "cinq huitièmes ? Il faut regarder le sac après le premier tirage.",
            attempt,
        )

    def _update_bag(self):
        balls = VGroup()
        for color, letter in [(RED_D, "R")] * 5 + [(BLUE_D, "B")] * 3:
            circle = Circle(radius=0.34, color=color, fill_color=color, fill_opacity=0.12)
            balls.add(VGroup(circle, self.formula(letter, 30, color).move_to(circle)))
        balls.arrange(RIGHT, buff=0.15)
        initial = self.formula(r"\text{Au départ : }5R+3B=8\text{ boules}", 37)
        conditional = self.formula(r"\text{Après }R_1:\quad P(R_2\mid R_1)=\frac47", 43, BLUE_D)
        self.new_page("Après une rouge : quatre rouges sur sept", initial, balls, conditional, gap=0.7)
        self.explain(
            "Supposons que la première boule soit rouge. Une boule rouge sort "
            "du sac. Il reste quatre rouges et trois bleues, donc sept boules "
            "au total. Le numérateur et le dénominateur ont changé.",
            initial, balls,
        )
        first = balls[0]
        self.play(FadeOut(first, shift=DOWN * 0.45),
                  *(ball.animate.shift(LEFT * 0.415) for ball in list(balls)[1:]), run_time=1.1)
        balls.remove(first)
        self.explain(
            "Sachant que la première boule est rouge, la probabilité d'une "
            "seconde rouge est quatre sur sept. La barre verticale se lit "
            "sachant : elle précise quelle information nous utilisons.",
            conditional, hold=1.4,
        )

    def _tree(self):
        root = Dot([-4.3, 0, 0], color=BLACK, radius=0.045)
        start = self.words("départ", 28).next_to(root, LEFT, buff=0.2)
        r = self.formula(r"R_1", 32).move_to([-1.7, 1.25, 0])
        b = self.formula(r"B_1", 32).move_to([-1.7, -1.25, 0])
        rr = self.formula("RR", 32).move_to([1.8, 1.95, 0])
        rb = self.formula("RB", 32).move_to([1.8, 0.55, 0])
        br = self.formula("BR", 32).move_to([1.8, -0.55, 0])
        bb = self.formula("BB", 32).move_to([1.8, -1.95, 0])
        first = VGroup(
            root, start, r, b,
            Line(root.get_center(), r.get_left() - RIGHT * 0.12, color=BLACK),
            Line(root.get_center(), b.get_left() - RIGHT * 0.12, color=BLACK),
            self.formula(r"\frac58", 30).move_to([-3.0, 1.08, 0]),
            self.formula(r"\frac38", 30).move_to([-3.0, -1.08, 0]),
        )
        after_r = VGroup(
            rr, rb,
            Line(r.get_right() + RIGHT * 0.12, rr.get_left() - RIGHT * 0.12, color=BLACK),
            Line(r.get_right() + RIGHT * 0.12, rb.get_left() - RIGHT * 0.12, color=BLACK),
            self.formula(r"\frac47", 30).move_to([0, 2.03, 0]),
            self.formula(r"\frac37", 30).move_to([0, 0.46, 0]),
        )
        after_b = VGroup(
            br, bb,
            Line(b.get_right() + RIGHT * 0.12, br.get_left() - RIGHT * 0.12, color=BLACK),
            Line(b.get_right() + RIGHT * 0.12, bb.get_left() - RIGHT * 0.12, color=BLACK),
            self.formula(r"\frac57", 30).move_to([0, -0.46, 0]),
            self.formula(r"\frac27", 30).move_to([0, -2.03, 0]),
        )
        tree = VGroup(first, after_r, after_b)
        self.new_page("Un arbre pour les sacs restants", tree)
        self.explain(
            "Au premier embranchement, cinq huitièmes pour rouge et trois "
            "huitièmes pour bleu. Ces deux probabilités totalisent un.",
            first,
        )
        self.explain(
            "Après une rouge, il reste quatre rouges et trois bleues sur sept. "
            "Les branches portent donc quatre septièmes et trois septièmes. "
            "Nous retrouvons une somme égale à un à ce nœud.",
            after_r,
        )
        self.explain(
            "Après une bleue, il reste cinq rouges et deux bleues sur sept. "
            "Les probabilités conditionnelles sont maintenant cinq septièmes "
            "et deux septièmes. Le dénominateur est sept dans les deux cas, "
            "mais le nombre de rouges dépend de la couleur déjà tirée.",
            after_b,
        )

    def _two_red(self):
        product = self.formula(r"P(R_1\cap R_2)=P(R_1)P(R_2\mid R_1)", 40)
        result = panel(self.formula(r"\frac58\times\frac47=\frac{20}{56}=\frac5{14}", 48), width=8.4)
        meaning = self.words("Un chemin : multiplier les probabilités conditionnelles.", 28)
        self.new_page("Deux rouges : suivre un seul chemin", product, result, meaning, gap=0.6)
        self.explain(
            "Pour deux rouges, on suit le chemin rouge puis rouge. La règle du "
            "produit utilise la probabilité de la première étape et celle "
            "de la deuxième sachant que la première s'est réalisée.",
            product,
        )
        self.explain(
            "Cinq huitièmes fois quatre septièmes donne vingt sur cinquante-six, "
            "soit cinq quatorzièmes. Le mot et ne justifie pas, à lui seul, "
            "la multiplication de deux probabilités non conditionnelles.",
            result, meaning,
        )

    def _one_each(self):
        cases = self.formula(r"\{\text{une de chaque couleur}\}=\{RB\}\cup\{BR\}", 38)
        rb = self.formula(r"P(RB)=\frac58\times\frac37=\frac{15}{56}", 41)
        br = self.formula(r"P(BR)=\frac38\times\frac57=\frac{15}{56}", 41)
        total = self.formula(r"P(\text{une de chaque})=\frac{30}{56}=\frac{15}{28}", 41, BLUE_D)
        self.new_page("Une de chaque couleur : deux ordres", cases, rb, br, total, gap=0.4)
        self.explain(
            "Une boule de chaque couleur peut arriver dans deux ordres : rouge "
            "puis bleu, ou bleu puis rouge. Ces chemins sont disjoints : lors "
            "d'une même expérience, la première boule ne peut pas être rouge "
            "et bleue à la fois.",
            cases,
        )
        self.explain(
            "Chaque chemin vaut quinze sur cinquante-six. Nous les additionnons "
            "et obtenons quinze vingt-huitièmes. Si nous ne gardions que rouge "
            "puis bleu, nous ne répondrions qu'à la moitié des cas demandés.",
            rb, br, total,
        )

    def _unconditional_probability(self):
        split = self.formula(r"P(R_2)=P(R_1\cap R_2)+P(B_1\cap R_2)", 38)
        calculation = self.formula(r"P(R_2)=\frac58\frac47+\frac38\frac57=\frac{35}{56}=\frac58", 40)
        distinction = self.formula(r"P(R_2)=\frac58\qquad\text{mais}\qquad P(R_2\mid R_1)=\frac47", 39, BLUE_D)
        self.new_page("Sans connaître la première couleur", split, calculation, distinction, gap=0.65)
        self.explain(
            "Attention à une nuance. Si nous ne connaissons pas la première "
            "couleur, la probabilité d'une rouge au second tirage reste cinq "
            "huitièmes. Pour la calculer, on additionne les chemins rouge rouge "
            "et bleu rouge.",
            split, calculation,
        )
        self.explain(
            "Ce qui change après l'information première rouge, c'est la "
            "probabilité conditionnelle : quatre septièmes. Les deux tirages "
            "ne sont pas indépendants, même si leurs probabilités marginales "
            "d'obtenir rouge sont identiques.",
            distinction, hold=1.5,
        )

    def _replacement_comparison(self):
        with_replacement = self.formula(r"\text{Avec remise et nouveau tirage uniforme : }\frac58\times\frac58=\frac{25}{64}", 33)
        without = self.formula(r"\text{Sans remise : }\frac58\times\frac47=\frac5{14}", 39)
        rule = self.words("Le mécanisme de tirage détermine le modèle.", 30, BLUE_D)
        self.new_page("Avec remise : une autre expérience", with_replacement, without, rule, gap=0.7)
        self.explain(
            "Si la première boule est remise et que le second choix est fait "
            "uniformément sans dépendre du premier, le sac retrouve sa composition "
            "initiale. Cinq huitièmes fois cinq huitièmes devient alors correct.",
            with_replacement,
        )
        self.explain(
            "Sans remise, une première rouge rend une autre rouge un peu moins "
            "probable. Les deux expériences ont des réponses différentes. "
            "Le choix de la formule vient du mécanisme de tirage.",
            without, rule,
        )

    def _self_check(self):
        model = self.words("3 rouges et 2 bleues · deux tirages uniformes sans remise", 28)
        question = self.words("Quelle est la probabilité d'une boule de chaque couleur ?", 29)
        clue = self.formula(r"RB\quad\text{ou}\quad BR", 45)
        self.new_page("À vous : un autre sac", model, question, clue, gap=0.7)
        self.explain(
            "À vous. Le sac contient maintenant trois rouges et deux bleues. "
            "On tire deux boules uniformément, sans remise. Quelle est la "
            "probabilité d'obtenir une boule de chaque couleur ? Écrivez les "
            "deux chemins avant de calculer.",
            model, question, clue, pause_after=6,
        )

    def _answer(self):
        rb = self.formula(r"P(RB)=\frac35\times\frac24=\frac3{10}", 43)
        br = self.formula(r"P(BR)=\frac25\times\frac34=\frac3{10}", 43)
        total = panel(self.formula(r"P(\text{une de chaque})=\frac3{10}+\frac3{10}=\frac35", 42), width=9.5)
        self.new_page("Actualiser, multiplier, puis additionner", rb, br, total, gap=0.6)
        self.explain(
            "Après une rouge, il reste deux bleues parmi quatre boules. "
            "Rouge puis bleu vaut donc trois cinquièmes fois deux quarts. "
            "Après une bleue, trois rouges restent parmi quatre boules.",
            rb, br,
        )
        self.explain(
            "Chacun des deux chemins vaut trois dixièmes. Leur somme donne "
            "trois cinquièmes. Nous avons actualisé la composition du sac, "
            "multiplié le long de chaque chemin, puis additionné les deux cas disjoints.",
            total,
        )

    def _takeaway(self):
        steps = VGroup(
            self.words("1. Décrire le sac après chaque tirage.", 30),
            self.words("2. Multiplier le long d'un chemin.", 30),
            self.words("3. Additionner les chemins favorables disjoints.", 30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        reference = self.words("Manuel 8.3 et 8.9 · Cahier 8.3 C", 28)
        self.new_page("Le réflexe à garder", steps, reference, gap=0.75)
        self.explain(
            "Sans remise, décrivez ce qui reste après chaque résultat connu. "
            "Un chemin demande un produit de probabilités conditionnelles. "
            "Plusieurs chemins disjoints demandent ensuite une somme. "
            "Ces trois étapes évitent de supposer une indépendance qui n'existe pas.",
            steps, reference,
        )

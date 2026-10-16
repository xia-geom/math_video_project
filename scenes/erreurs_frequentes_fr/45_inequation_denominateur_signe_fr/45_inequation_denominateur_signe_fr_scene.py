"""A rational inequality requires the denominator's domain and sign."""
from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    RED_D,
    RIGHT,
    WHITE,
    Arrow,
    Circle,
    Create,
    Dot,
    FadeOut,
    MathTex,
    NumberLine,
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


class InequationDenominateurSigneFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._false_shortcut()
        self._critical_values()
        self._numerical_sweep()
        self._sign_chart()
        self._solution_rays()
        self._self_check()
        self._self_check_answer()
        self._closing()
        self.wait(1.2)

    def _false_shortcut(self):
        original = self.formula(r"\frac{x+2}{x-3}>0", 58)
        shortcut = self.formula(r"x+2>0\qquad\Longrightarrow\qquad x>-2", 42, RED_D)
        label = self.words("Conclusion proposée après multiplication par x − 3", 28, RED_D)
        counterexample = self.formula(r"x=0:\qquad\frac{0+2}{0-3}=-\frac23<0", 43)
        self.new_page("Peut-on supprimer le dénominateur ?", original, label, shortcut, counterexample, gap=0.32)
        self.explain(
            "Pour résoudre cette inéquation, on pourrait vouloir multiplier par "
            "x moins trois, puis ne garder que le numérateur positif. On annoncerait "
            "alors toutes les valeurs supérieures à moins deux.",
            original, label, shortcut,
        )
        self.explain(
            "Mais zéro appartient à cette réponse proposée, alors que le quotient "
            "vaut moins deux tiers. Il est négatif. Le raccourci a donc donné une mauvaise réponse.",
            counterexample,
        )

    def _critical_values(self):
        domain = self.formula(r"x-3\ne0\qquad\Longrightarrow\qquad x\ne3", 45, BLUE_D)
        zero = self.formula(r"x+2=0\qquad\Longleftrightarrow\qquad x=-2", 43)
        sign = self.formula(r"x<3:\ x-3<0\qquad x>3:\ x-3>0", 39)
        note = self.words("Un facteur négatif inverse le sens de l’inégalité.", 29)
        self.new_page("Deux valeurs à distinguer", domain, zero, sign, note, gap=0.42)
        self.explain(
            "Avant tout calcul, trois est interdit : le dénominateur y est nul. "
            "Moins deux joue un autre rôle : il annule le numérateur.",
            domain, zero,
        )
        self.explain(
            "Le dénominateur change de signe à trois. Multiplier par lui conserve "
            "le sens de l’inégalité à droite de trois, mais l’inverse à gauche. "
            "On ne peut pas appliquer la même transformation partout.",
            sign, note,
        )

    def _numerical_sweep(self):
        line = NumberLine(
            x_range=[-5, 6, 1], length=10.2, color=BLACK,
            include_tip=True, include_numbers=False, stroke_width=2,
        )
        markers = VGroup(
            self.formula("-2", 30).next_to(line.n2p(-2), DOWN, buff=0.20),
            self.formula("3", 30).next_to(line.n2p(3), DOWN, buff=0.20),
        )
        probe = Dot(line.n2p(-3), radius=0.10, color=BLUE_D)
        diagram = VGroup(line, markers, probe)
        calculations = VGroup(
            self.formula(r"x=-3:\quad\frac{-1}{-6}=\frac16>0", 44),
            self.formula(r"x=0:\quad\frac{2}{-3}=-\frac23<0", 44),
            self.formula(r"x=4:\quad\frac61=6>0", 44),
        )
        observation = self.words("Mêmes signes : positif. Signes opposés : négatif.", 29, BLUE_D)
        self.new_page("Trois essais, trois régions", diagram, calculations, observation, gap=0.65)
        self.explain(
            "Testons une valeur dans chacune des trois régions. À moins trois, "
            "le numérateur et le dénominateur sont tous deux négatifs. Leur quotient est positif.",
            diagram, calculations[0],
        )
        self.play(FadeOut(calculations[0]), probe.animate.move_to(line.n2p(0)), run_time=1.2)
        calculations[0].set_opacity(0)
        self.explain(
            "À zéro, les signes sont opposés : positif au numérateur, négatif au "
            "dénominateur. Le quotient est négatif.",
            calculations[1],
        )
        self.play(FadeOut(calculations[1]), probe.animate.move_to(line.n2p(4)), run_time=1.2)
        calculations[1].set_opacity(0)
        self.explain(
            "À quatre, les deux signes sont positifs. Le quotient est positif. "
            "Ces essais suggèrent la réponse ; le tableau de signes va la justifier "
            "pour toutes les valeurs des intervalles.",
            calculations[2], observation,
        )

    def _sign_chart(self):
        entries = [
            [r"x", r"x<-2", r"-2<x<3", r"x>3"],
            [r"x+2", "-", "+", "+"],
            [r"x-3", "-", "-", "+"],
            [r"\dfrac{x+2}{x-3}", "+", "-", "+"],
        ]
        widths = [2.05, 2.7, 2.7, 2.7]
        rows = VGroup()
        for row_index, row in enumerate(entries):
            cells = VGroup(*[
                panel(
                    self.formula(value, 31, BLUE_D if row_index == 0 else BLACK),
                    width=width, height=0.72 if row_index < 3 else 1.04, padding=0.10,
                )
                for value, width in zip(row, widths, strict=True)
            ]).arrange(RIGHT, buff=0.10)
            rows.add(cells)
        rows.arrange(DOWN, buff=0.10)
        endpoint_note = self.formula(r"x=-2:\ 0\qquad x=3:\ \text{interdit}", 34)
        self.new_page("Le tableau justifie les intervalles", rows, endpoint_note, gap=0.40)
        self.explain(
            "Chaque facteur garde son signe entre ses zéros. On remplit donc "
            "une ligne pour le numérateur, puis une pour le dénominateur.",
            rows[0], rows[1], rows[2],
        )
        self.explain(
            "La règle des signes donne plus, moins, puis plus. Le quotient est "
            "strictement positif dans les deux régions extérieures. Moins deux "
            "donne zéro, donc ne convient pas ici. Trois reste toujours interdit.",
            rows[3], endpoint_note,
        )

    def _solution_rays(self):
        line = NumberLine(
            x_range=[-5, 6, 1], length=10.2, color=BLACK,
            include_numbers=False, stroke_width=2,
        )
        left_ray = Arrow(line.n2p(-2), line.n2p(-5), buff=0, color=BLUE_D, stroke_width=5)
        right_ray = Arrow(line.n2p(3), line.n2p(6), buff=0, color=BLUE_D, stroke_width=5)
        holes = VGroup(*[
            Circle(radius=0.095, color=BLUE_D, fill_color=WHITE, fill_opacity=1, stroke_width=3)
            .move_to(line.n2p(value)) for value in [-2, 3]
        ])
        labels = VGroup(*[
            self.formula(str(value), 30).next_to(line.n2p(value), DOWN, buff=0.2)
            for value in [-2, 3]
        ])
        diagram = VGroup(line, left_ray, right_ray, holes, labels)
        answer = self.formula(r"S=]-\infty,-2[\ \cup\ ]3,+\infty[", 43, BLUE_D)
        meaning = self.words("À gauche de −2, ou à droite de 3.", 31)
        self.new_page("Réunir les deux régions", diagram, answer, meaning, gap=0.65)
        self.explain(
            "On réunit les deux intervalles où le signe est positif. Les deux "
            "extrémités sont ouvertes, mais pour des raisons différentes : "
            "zéro n’est pas strictement positif, et la division par zéro n’existe pas.",
            line, labels,
        )
        self.play(Create(left_ray), Create(right_ray), run_time=1.3)
        self.explain(
            "La solution se lit : x inférieur à moins deux, ou x supérieur à trois.",
            holes, answer, meaning,
        )

    def _self_check(self):
        equation = self.formula(r"\frac{x-1}{x+2}\le0", 60)
        question = self.words("Quel intervalle ? Quelles extrémités ?", 31)
        self.new_page("À vous : une inégalité large", equation, question, gap=0.85)
        self.explain(
            "À vous. Résolvez ce quotient négatif ou nul. Distinguez la valeur "
            "interdite de celle qui annule le numérateur. Puis décidez quelles "
            "extrémités appartiennent à la solution.",
            equation, question, pause_after=6,
        )

    def _self_check_answer(self):
        domain = self.formula(r"x\ne-2", 42)
        sign = self.formula(r"\begin{array}{c|ccc}x&x<-2&-2<x<1&x>1\\\hline"
                            r"\dfrac{x-1}{x+2}&+&-&+\end{array}", 37)
        result = self.formula(r"S=]-2,1]", 55, GREEN_D)
        endpoints = self.words("−2 est interdit. 1 donne zéro : on l’inclut.", 30)
        self.new_page("Deux extrémités, deux décisions", domain, sign, result, endpoints, gap=0.40)
        self.explain(
            "Le dénominateur interdit moins deux. Le quotient est négatif entre "
            "moins deux et un. À un, le numérateur est nul : cette valeur est "
            "admise puisque l’inégalité est large. La réponse est l’intervalle "
            "ouvert en moins deux et fermé en un.",
            domain, sign, result, endpoints,
        )

    def _closing(self):
        rule = self.words("Domaine, signes, puis extrémités.", 34, BLUE_D)
        reference = self.words("MAT0339 · Cahier, exercice 2.4C", 28)
        self.new_page("Trois contrôles", rule, reference, gap=0.8)
        self.explain(
            "Pour une inéquation rationnelle, gardez ces trois contrôles : "
            "le domaine, les signes sur les intervalles et l’inclusion des extrémités.",
            rule, reference,
        )

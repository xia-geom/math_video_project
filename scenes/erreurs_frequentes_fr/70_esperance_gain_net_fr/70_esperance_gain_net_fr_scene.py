"""Separate gross payout, net gain and a theoretical mean from a guaranteed result."""

from manim import BLACK, BLUE_D, DOWN, RED_D, RIGHT, WHITE, MathTex, Tex, Text, VGroup, config

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class EsperanceGainNetFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._outcomes()
        self._weighted_mean()
        self._gross_check()
        self._one_play()
        self._repeated_plays()
        self._self_check()
        self._answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        rules = self.words("Participation : 4 $ payés à chaque partie", 30)
        payout = self.words("Versement : 20 $ avec probabilité 0,1; sinon 0 $", 28)
        attempt = panel(self.formula(r"20\times0{,}1=2\quad\Longrightarrow\quad\text{gain de }2\,\$\ ?", 40, RED_D), width=11)
        self.new_page("Le versement n'est pas le gain net", rules, payout, attempt, gap=0.7)
        self.explain(
            "Un jeu coûte quatre dollars par partie. Il verse vingt dollars "
            "avec probabilité zéro virgule un et ne verse rien sinon. Le "
            "versement annoncé ne comprend pas le coût de participation.",
            rules, payout,
        )
        self.explain(
            "Vingt fois zéro virgule un vaut deux. Mais deux dollars "
            "représentent-ils le gain net espéré ? Pour répondre, nommons "
            "précisément la variable et tenons compte du coût dans tous les cas.",
            attempt,
        )

    def _outcomes(self):
        win = VGroup(
            self.words("Versement de 20 $", 29),
            self.formula(r"P=0{,}1", 34),
            self.formula(r"X=20-4=16\,\$", 37, BLUE_D),
        ).arrange(DOWN, buff=0.32)
        lose = VGroup(
            self.words("Aucun versement", 29),
            self.formula(r"P=0{,}9", 34),
            self.formula(r"X=0-4=-4\,\$", 37, RED_D),
        ).arrange(DOWN, buff=0.32)
        cards = VGroup(panel(win, width=5.4), panel(lose, width=5.4)).arrange(RIGHT, buff=0.55)
        definition = self.formula(r"X=\text{versement}-\text{coût de participation}", 35)
        total = self.formula(r"0{,}1+0{,}9=1", 35)
        self.new_page("Définir le gain net de chaque partie", definition, cards, total, gap=0.55)
        self.explain(
            "Appelons X le gain net, c'est-à-dire le versement moins le coût. "
            "Si le jeu verse vingt dollars, il reste un bénéfice de seize "
            "dollars. S'il ne verse rien, nous perdons les quatre dollars payés.",
            definition, cards,
        )
        self.explain(
            "Les deux cas sont disjoints et couvrent toutes les possibilités. "
            "Leurs probabilités, zéro virgule un et zéro virgule neuf, "
            "totalisent un. Le coût est payé dans les deux cas.",
            total,
        )

    def _weighted_mean(self):
        definition = self.formula(r"\mathbb E[X]=\sum_i x_i p_i", 44)
        product = self.formula(r"\mathbb E[X]=16(0{,}1)+(-4)(0{,}9)", 42)
        result = panel(self.formula(r"\mathbb E[X]=1{,}6-3{,}6=-2\,\$", 46, BLUE_D), width=10)
        self.new_page("Une moyenne pondérée des gains nets", definition, product, result, gap=0.65)
        self.explain(
            "L'espérance additionne chaque valeur du gain net multipliée "
            "par sa probabilité. Nous calculons seize fois zéro virgule un, "
            "plus moins quatre fois zéro virgule neuf.",
            definition, product,
        )
        self.explain(
            "La contribution positive vaut un dollar soixante; la contribution "
            "négative vaut moins trois dollars soixante. Le gain net espéré "
            "est donc moins deux dollars par partie : une perte moyenne théorique.",
            result, hold=1.5,
        )

    def _gross_check(self):
        gross = self.formula(r"Y=\text{versement},\qquad\mathbb E[Y]=20(0{,}1)+0(0{,}9)=2", 35)
        relation = self.formula(r"X=Y-4", 45)
        result = self.formula(r"\mathbb E[X]=\mathbb E[Y]-4=2-4=-2", 41, BLUE_D)
        condition = self.words("Le coût de 4 $ est constant et payé à chaque partie.", 28)
        self.new_page("Un second calcul pour vérifier", gross, relation, result, condition, gap=0.5)
        self.explain(
            "Nous pouvons vérifier en séparant le versement Y du gain net X. "
            "Le versement espéré est bien de deux dollars. Comme le coût est "
            "toujours quatre dollars, le gain net espéré est deux moins quatre.",
            gross, relation, result,
        )
        self.explain(
            "Soustraire seulement quatre fois zéro virgule un serait une "
            "erreur : les perdants paient aussi. Pour un coût variable, il "
            "faudrait également calculer son espérance selon les règles du jeu.",
            condition,
        )

    def _one_play(self):
        possible = panel(self.formula(r"X\in\{-4,16\}\quad\text{pour une partie}", 43), width=10.6)
        average = self.formula(r"\mathbb E[X]=-2\notin\{-4,16\}", 43, BLUE_D)
        note = self.words("Une espérance peut ne jamais être une valeur observée.", 29)
        self.new_page("Moins deux n'est pas un résultat certain", possible, average, note, gap=0.75)
        self.explain(
            "Sur une seule partie, le gain net est soit moins quatre, soit "
            "seize dollars. Personne n'obtient exactement moins deux dollars "
            "dans ce modèle. L'espérance n'est ni une promesse ni nécessairement "
            "une valeur possible de la variable.",
            possible, average, note, hold=1.5,
        )

    def _repeated_plays(self):
        model = self.words("10 parties indépendantes, avec les mêmes règles", 29)
        total = self.formula(r"K=\text{nombre de versements de }20\,\$", 35)
        actual = self.formula(r"\text{Gain total}=20K-40", 42)
        examples = self.formula(r"K=0:\ -40\,\$\qquad K=1:\ -20\,\$\qquad K=2:\ 0\,\$", 34)
        expected = self.formula(r"\mathbb E[\text{gain total}]=10(-2)=-20\,\$", 39, BLUE_D)
        self.new_page("Dix parties ne fixent pas le résultat", model, total, actual, examples, expected, gap=0.38)
        self.explain(
            "Même en jouant dix parties indépendantes avec les mêmes règles, "
            "il n'est pas garanti d'obtenir un seul versement. Si K est le "
            "nombre de versements, le gain total est vingt K moins les "
            "quarante dollars de participation.",
            model, total, actual,
        )
        self.explain(
            "Zéro versement donne moins quarante dollars, un donne moins "
            "vingt, deux donnent zéro. L'espérance du total est moins vingt, "
            "mais le total réel dépend de K. Lors de très nombreuses "
            "répétitions indépendantes, la moyenne par partie se stabilise "
            "autour de moins deux; aucun nombre fini de parties ne garantit "
            "exactement cette moyenne.",
            examples, expected,
        )

    def _self_check(self):
        game = self.words("Un dé équilibré; participation de 1 $", 30)
        rule = self.words("Versement de 6 $ si le résultat est 6, sinon 0 $.", 29)
        question = self.words("Calculez l'espérance du gain net.", 30)
        certainty = self.words("Un gain net nul est-il garanti ?", 30)
        cue = self.words("Commencez par les deux gains nets possibles.", 28, BLUE_D)
        self.new_page("À vous : le dé et la participation", game, rule, question, certainty, cue, gap=0.5)
        self.explain(
            "À vous. Un jeu utilise un dé équilibré et coûte un dollar. Il "
            "verse six dollars si le résultat est six et rien sinon. Le gain "
            "net espéré est-il nul ? Un gain net nul est-il un résultat "
            "certain ? Écrivez d'abord les deux gains nets possibles.",
            game, rule, question, certainty, cue, pause_after=6,
        )

    def _answer(self):
        outcomes = self.formula(r"X=5\text{ avec }P=\frac16;\qquad X=-1\text{ avec }P=\frac56", 37)
        result = panel(self.formula(r"\mathbb E[X]=5\cdot\frac16-1\cdot\frac56=0", 44), width=10)
        meaning = self.words("Équitable au sens de l'espérance; résultat toujours incertain.", 28)
        impossible = self.words("Le gain net d'une partie vaut 5 $ ou −1 $, jamais 0 $.", 28, BLUE_D)
        self.new_page("Équitable ne signifie pas sans risque", outcomes, result, meaning, impossible, gap=0.5)
        self.explain(
            "Sur un six, le gain net est six moins un, soit cinq dollars, "
            "avec probabilité un sixième. Sinon, la perte est un dollar, "
            "avec probabilité cinq sixièmes. Les deux contributions se "
            "compensent : l'espérance vaut zéro.",
            outcomes, result,
        )
        self.explain(
            "On dit ici que le jeu est équitable au sens de l'espérance, "
            "sans autres frais. Cela ne garantit pas l'équilibre d'une "
            "partie : le gain vaut cinq ou moins un, jamais zéro. Une "
            "moyenne n'efface pas l'incertitude des résultats individuels.",
            meaning, impossible, hold=1.5,
        )

    def _takeaway(self):
        first = self.words("Nommer la variable : versement ou gain net ?", 30)
        second = self.words("Inclure chaque coût et chaque issue avec sa probabilité.", 28)
        third = self.words("Interpréter l'espérance comme une moyenne théorique.", 28, BLUE_D)
        self.new_page("Trois questions avant de conclure", first, second, third, gap=0.8)
        self.explain(
            "Pour calculer une espérance, définissez d'abord ce que mesure "
            "la variable. Incluez tous les coûts dans le gain net, puis "
            "pondérez chaque issue par sa probabilité. Enfin, distinguez "
            "la moyenne théorique d'un résultat certain, même lorsque "
            "cette moyenne vaut zéro.",
            first, second, third,
        )

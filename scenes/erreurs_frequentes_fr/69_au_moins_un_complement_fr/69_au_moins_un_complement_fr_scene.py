"""Count each code once: at least one distinguished symbol is not exactly one."""

from manim import BLACK, BLUE_D, DOWN, RED_D, RIGHT, WHITE, MathTex, Tex, Text, VGroup, config

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class AuMoinsUnComplementFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._marked_positions()
        self._duplicate_codes()
        self._complement()
        self._exactly_one()
        self._partition()
        self._self_check()
        self._answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        model = self.words("Codes de trois chiffres, de 0 à 9", 30)
        conventions = self.words("Répétitions permises; un code peut commencer par 0.", 28)
        question = self.words("Combien contiennent au moins un zéro ?", 31)
        attempt = panel(self.formula(r"N\stackrel{?}{=}3\times10^2=300", 42, RED_D), width=8.7)
        self.new_page("Au moins un : que compte-t-on ?", model, conventions, question, attempt)
        self.explain(
            "Nous comptons des codes de trois chiffres, chacun choisi parmi zéro "
            "à neuf. Les répétitions sont permises et zéro peut être le premier "
            "chiffre. Zéro sept zéro est donc un code admissible. Nous cherchons "
            "N, le nombre de codes contenant au moins un zéro, éventuellement "
            "deux ou trois.",
            model, conventions, question,
        )
        self.explain(
            "Une tentative consiste à choisir une position pour un zéro, puis "
            "à remplir les deux autres positions librement : trois fois dix "
            "au carré. Cette méthode compte-t-elle chaque code exactement une fois ?",
            attempt,
        )

    def _marked_positions(self):
        positions = VGroup(
            panel(self.formula(r"\boxed{0}\ a\ b", 45), width=3.2),
            panel(self.formula(r"a\ \boxed{0}\ b", 45), width=3.2),
            panel(self.formula(r"a\ b\ \boxed{0}", 45), width=3.2),
        ).arrange(RIGHT, buff=0.45)
        choices = self.formula(r"a,b\in\{0,1,\ldots,9\}:\quad100+100+100", 36)
        warning = self.words("Le zéro encadré est une position marquée.", 30, BLUE_D)
        self.new_page("Trois descriptions peuvent se recouper", positions, choices, warning, gap=0.65)
        self.explain(
            "Chaque cadre fixe une position à zéro et laisse cent choix pour "
            "les deux autres chiffres. Mais ces autres chiffres peuvent aussi "
            "être zéro. Les trois listes ne sont donc pas disjointes.",
            positions, choices,
        )
        self.explain(
            "Le cadre ajoute une information qui ne fait pas partie du code : "
            "il désigne un zéro particulier. Nous comptons alors des codes "
            "accompagnés d'une position marquée, et pas seulement des codes.",
            warning,
        )

    def _duplicate_codes(self):
        two = self.formula(r"\boxed{0}\ 7\ 0\qquad0\ 7\ \boxed{0}", 46)
        two_label = self.words("Le même code 070 est compté deux fois.", 29)
        three = self.formula(r"\boxed{0}\ 0\ 0\qquad0\ \boxed{0}\ 0\qquad0\ 0\ \boxed{0}", 43)
        three_label = self.words("Le code 000 est compté trois fois.", 29)
        self.new_page("Une répétition qui dépend du code", two, two_label, three, three_label, gap=0.5)
        self.explain(
            "Zéro sept zéro apparaît lorsque nous marquons le premier zéro, "
            "et lorsque nous marquons le dernier. C'est pourtant le même code.",
            two, two_label,
        )
        self.explain(
            "Zéro zéro zéro apparaît trois fois. Un code qui contient un seul "
            "zéro apparaît une seule fois. La multiplicité varie : nous ne "
            "pouvons pas réparer le total en le divisant par trois, ni par "
            "une autre multiplicité commune.",
            three, three_label, hold=1.5,
        )

    def _complement(self):
        total = self.formula(r"\text{Tous les codes : }10^3=1000", 39)
        none = self.formula(r"\text{Aucun zéro : }9^3=729", 39)
        result = panel(self.formula(r"\text{Au moins un zéro : }1000-729=271", 39, BLUE_D), width=11)
        self.new_page("Compter ceux qui n'ont aucun zéro", total, none, result, gap=0.65)
        self.explain(
            "Le contraire d'au moins un zéro est aucun zéro. Il y a mille "
            "codes au total. Sans zéro, chaque position admet neuf chiffres, "
            "donc neuf au cube, soit sept cent vingt-neuf codes.",
            total, none,
        )
        self.explain(
            "Les codes sans zéro et les codes avec au moins un zéro forment "
            "deux groupes disjoints qui couvrent tous les cas. Nous retirons "
            "les sept cent vingt-neuf codes sans zéro : il reste deux cent "
            "soixante et onze codes, chacun compté une seule fois.",
            result, hold=1.5,
        )

    def _exactly_one(self):
        choice = self.words("Choisir l'unique position du zéro : 3 possibilités.", 28)
        others = self.words("Les deux autres chiffres doivent être non nuls.", 29)
        result = panel(self.formula(r"\text{Exactement un zéro : }3\times9^2=243", 39), width=11)
        self.new_page("Exactement un : une autre question", choice, others, result, gap=0.65)
        self.explain(
            "Pour exactement un zéro, la position de ce zéro est unique : "
            "trois choix. Les deux autres positions doivent exclure zéro et "
            "offrent chacune neuf choix. Cette fois, les trois cas sont disjoints.",
            choice, others,
        )
        self.explain(
            "Nous obtenons deux cent quarante-trois codes. Ce nombre est plus "
            "petit que deux cent soixante et onze, car les codes avec deux "
            "ou trois zéros sont exclus de cette nouvelle question.",
            result,
        )

    def _partition(self):
        rows = VGroup(
            self.formula(r"0\text{ zéro}:\ 729\qquad1\text{ zéro}:\ 243", 37),
            self.formula(r"2\text{ zéros}:\ 3\times9=27\qquad3\text{ zéros}:\ 1", 37),
        ).arrange(DOWN, buff=0.6)
        check = self.formula(r"729+243+27+1=1000", 41)
        at_least = self.formula(r"243+27+1=271", 44, BLUE_D)
        self.new_page("Vérification par cas disjoints", rows, check, at_least, gap=0.65)
        self.explain(
            "Vérifions en classant les codes par nombre de zéros. Avec deux "
            "zéros, nous choisissons la position du chiffre non nul, puis sa "
            "valeur : trois fois neuf, soit vingt-sept. Avec trois zéros, "
            "il n'existe qu'un code, zéro zéro zéro.",
            rows,
        )
        self.explain(
            "Les quatre groupes totalisent bien mille. Les trois derniers "
            "groupes, avec un, deux ou trois zéros, donnent ensemble deux cent "
            "soixante et onze. Le complément et le comptage par cas s'accordent.",
            check, at_least,
        )

    def _self_check(self):
        model = self.words("Chaînes de 8 symboles, chacun égal à 0 ou à 1", 29)
        first = self.words("A. Combien contiennent au moins un 1 ?", 31)
        second = self.words("B. Combien contiennent exactement un 1 ?", 31)
        cue = self.words("Écrivez le complément pour A et les choix pour B.", 28, BLUE_D)
        self.new_page("À vous : deux sens du mot un", model, first, second, cue, gap=0.65)
        self.explain(
            "À vous. Une chaîne contient huit symboles, chacun égal à zéro ou "
            "à un. Comptez d'abord les chaînes avec au moins un un, puis celles "
            "avec exactement un un. Pour la première question, décrivez le "
            "complément; pour la seconde, identifiez les choix qui restent.",
            model, first, second, cue, pause_after=6,
        )

    def _answer(self):
        first = panel(self.formula(r"\text{Au moins un }1:\quad2^8-1=255", 41), width=10)
        none = self.words("Le seul cas exclu est 00000000.", 29)
        second = panel(self.formula(r"\text{Exactement un }1:\quad8", 43), width=10)
        why = self.words("Choisir sa position; les sept autres symboles sont 0.", 28)
        self.new_page("Au moins un : 255 chaînes", first, none, gap=0.8)
        self.explain(
            "Il existe deux puissance huit chaînes, soit deux cent cinquante-six. "
            "Une seule n'a aucun un : huit zéros. Nous obtenons donc deux cent "
            "cinquante-cinq chaînes avec au moins un un.",
            first, none,
        )
        self.new_page("Exactement un : seulement 8 chaînes", second, why, gap=0.8)
        self.explain(
            "Pour exactement un un, il suffit de choisir sa position parmi "
            "huit. Les sept autres symboles sont imposés à zéro. La réponse "
            "est huit, et non deux cent cinquante-cinq.",
            second, why, hold=1.5,
        )

    def _takeaway(self):
        first = self.words("Au moins un : retirer les cas sans aucun.", 31)
        second = self.words("Exactement un : exclure les autres réussites.", 31)
        third = self.words("Additionner des cas exige de contrôler leurs recoupements.", 28, BLUE_D)
        self.new_page("Le contrôle : chaque objet une fois", first, second, third, gap=0.75)
        self.explain(
            "Avant de calculer, précisez l'objet que vous comptez. Au moins "
            "un permet plusieurs occurrences; exactement un les interdit. "
            "Le complément simplifie souvent la première situation. Si vous "
            "additionnez plusieurs listes, vérifiez leurs recoupements pour "
            "ne pas compter le même objet plusieurs fois.",
            first, second, third,
        )

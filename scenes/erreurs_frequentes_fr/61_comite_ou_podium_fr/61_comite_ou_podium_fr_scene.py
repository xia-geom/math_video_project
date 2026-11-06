"""Count distinct outcomes by identifying which roles really differ."""

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    FadeOut,
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


class ComiteOuPodiumFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._swap_roles()
        self._six_descriptions()
        self._count_podiums()
        self._count_committees()
        self._self_check()
        self._self_check_answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        premise = self.words("Choisir 3 personnes parmi 10 personnes distinctes.", 29)
        calculation = self.formula(r"10\times9\times8=720", 53)
        question = self.words("720 podiums ? 720 comités ? Les deux ?", 31)
        self.new_page("Que compte le produit ?", premise, calculation, question, gap=0.75)
        self.explain(
            "Nous choisissons trois personnes parmi dix, sans choisir deux fois "
            "la même personne. Dix possibilités, puis neuf, puis huit : "
            "le produit donne sept cent vingt. Le calcul est simple. "
            "Mais quels résultats vient-il de compter ?",
            premise, calculation,
        )
        self.explain(
            "Un podium attribue trois rangs distincts. Un comité sans postes "
            "particuliers retient seulement ses membres. Les mêmes trois "
            "personnes peuvent donc correspondre à plusieurs podiums et à un seul comité.",
            question,
        )

    def _swap_roles(self):
        cards = VGroup(*[
            panel(self.formula(letter, 52), width=1.6, height=1.1)
            for letter in ("A", "B", "C")
        ]).arrange(RIGHT, buff=0.55)
        roles = VGroup(*[
            self.words(role, 29).next_to(card, DOWN, buff=0.2)
            for role, card in zip(("Or", "Argent", "Bronze"), cards, strict=True)
        ])
        diagram = VGroup(cards, roles)
        members = self.formula(r"\text{Membres : }\{A,B,C\}", 43)
        self.new_page("Le même groupe, un autre podium", diagram, members, gap=0.7)
        self.explain(
            "Sur ce podium, A reçoit l'or, B l'argent et C le bronze. "
            "Intervertissons les deux premières personnes en laissant "
            "les rangs à leur place.",
            diagram, members,
        )
        first_position = cards[0].get_center().copy()
        second_position = cards[1].get_center().copy()
        # Lift one card so the two names remain distinct during the exchange.
        self.play(cards[0].animate.shift(1.2 * UP), run_time=0.4)
        self.play(cards[0].animate.move_to(second_position + 1.2 * UP),
                  cards[1].animate.move_to(first_position), run_time=0.8)
        self.play(cards[0].animate.move_to(second_position), run_time=0.4)
        conclusion = self.words("Même comité, podium différent.", 32, BLUE_D).move_to(members)
        self.page.add(conclusion)
        self.play(FadeOut(members), run_time=0.35)
        self.page[1].remove(members)
        self.explain(
            "B reçoit maintenant l'or et A l'argent : le résultat du podium "
            "a changé. Pourtant, le groupe contient toujours A, B et C. "
            "Si nous formons un comité sans fonctions distinctes, ce changement "
            "d'ordre ne crée aucun nouveau comité.",
            conclusion,
        )

    def _six_descriptions(self):
        orders = ("ABC", "ACB", "BAC", "BCA", "CAB", "CBA")
        cards = VGroup(*[
            panel(self.formula(r"\,".join(order), 39), width=1.85, height=0.9, padding=0.16)
            for order in orders
        ]).arrange_in_grid(rows=2, cols=3, buff=(0.2, 0.25))
        group = panel(self.formula(r"\{A,B,C\}", 42), width=3.0, height=1.4)
        pair = VGroup(cards, group).arrange(RIGHT, buff=1.1)
        arrow = Arrow(cards.get_right(), group.get_left(), buff=0.15, color=BLACK)
        diagram = VGroup(pair, arrow)
        count = self.formula(r"3!=3\times2\times1=6", 46)
        self.new_page("Six descriptions d'un seul groupe", diagram, count, gap=0.65)
        self.explain(
            "Écrivons tous les podiums utilisant exactement A, B et C. "
            "Il y a trois choix pour le premier rang, deux pour le deuxième "
            "et un pour le dernier : six ordres au total.",
            cards, count,
        )
        self.explain(
            "Ces six listes décrivent le même comité. Et ce nombre six "
            "ne dépend pas du groupe choisi : chaque comité contient trois "
            "personnes distinctes, qui peuvent occuper les trois rangs de six façons.",
            arrow, group,
        )

    def _count_podiums(self):
        roles = self.formula(r"\text{Or : }10\qquad\text{Argent : }9\qquad\text{Bronze : }8", 40)
        product = self.formula(r"N_{\mathrm{podiums}}=10\times9\times8=720", 46, BLUE_D)
        rule = self.words("Un changement de rang donne un autre résultat.", 29)
        self.new_page("Compter les choix avec leurs rangs", roles, product, rule, gap=0.7)
        self.explain(
            "Parmi les dix personnes, chacune peut recevoir l'or. "
            "Il reste neuf personnes pour l'argent, puis huit pour le bronze. "
            "Chaque suite de ces choix détermine un podium et un seul.",
            roles, product,
        )
        self.explain(
            "Aucune division supplémentaire n'est nécessaire : échanger "
            "deux rangs change réellement le résultat. Le produit sept cent vingt "
            "est donc bien le nombre de podiums.",
            rule,
        )

    def _count_committees(self):
        relation = self.formula(r"N_{\mathrm{podiums}}=6\,N_{\mathrm{comit\acute es}}", 43)
        result = self.formula(r"N_{\mathrm{comit\acute es}}=\frac{10\times9\times8}{3!}=120", 47, BLUE_D)
        notation = self.formula(r"\binom{10}{3}=120", 48)
        reason = self.words("Diviser par le nombre de descriptions d'un même choix.", 28)
        self.new_page("Retirer le comptage multiple", relation, result, notation, reason, gap=0.48)
        self.explain(
            "Pour les comités, le produit a compté chaque groupe six fois. "
            "Puisque cette multiplicité est la même pour tous les groupes, "
            "nous divisons sept cent vingt par six et obtenons cent vingt comités.",
            relation, result,
        )
        self.explain(
            "C'est le sens du coefficient binomial : choisir trois personnes parmi dix. "
            "Le facteur trois factorielle ne vient pas d'une règle à appliquer "
            "automatiquement : il compte les ordres qui décrivent exactement "
            "le même résultat dans ce problème.",
            notation, reason,
        )

    def _self_check(self):
        pool = self.words("Parmi 8 personnes distinctes, choisir :", 30)
        roles = self.words("1 responsable et 2 membres sans rôle distinct.", 29)
        slots = self.formula(r"\boxed{R}\qquad\boxed{M}\qquad\boxed{M}", 48)
        question = self.words("Combien de choix différents ?", 31)
        self.new_page("À vous : un rôle, puis deux égaux", pool, roles, slots, question, gap=0.5)
        self.explain(
            "À vous. Parmi huit personnes distinctes, choisissez une personne "
            "responsable et deux autres membres, sans rôle distinct entre ces "
            "deux membres. Personne ne peut occuper deux places. "
            "Combien de choix différents existe-t-il ?",
            pool, roles, slots, question, pause_after=6,
        )

    def _self_check_answer(self):
        ordered = self.formula(r"8\times7\times6=336", 45)
        result = self.formula(r"N=8\binom72=\frac{8\times7\times6}{2!}=168", 47, BLUE_D)
        swap = self.words("Seuls les deux membres peuvent être intervertis.", 29)
        other = self.formula(r"\binom83\times3=56\times3=168", 43)
        self.new_page("Diviser par deux, pas par six", ordered, result, swap, other, gap=0.47)
        self.explain(
            "Choisir successivement le responsable, puis un premier et un "
            "deuxième membre donne huit fois sept fois six descriptions. "
            "Échanger les deux membres ne change rien, mais échanger "
            "un membre avec le responsable change le résultat.",
            ordered, result, swap,
        )
        self.explain(
            "Chaque choix est donc compté deux fois, pas six. La réponse vaut "
            "cent soixante-huit. Autre vérification : choisir d'abord "
            "un groupe de trois parmi huit, puis son responsable parmi les "
            "trois membres. Nous retrouvons le même résultat.",
            other,
        )

    def _takeaway(self):
        question = self.words("Qu'est-ce qui change vraiment le résultat ?", 31, BLUE_D)
        method = self.words("Nommer les rôles avant de choisir la formule.", 29)
        source = self.words("Manuel 7.8–7.9 · Cahier 7.8 A–B", 28)
        self.new_page("Compter des résultats distincts", question, method, source, gap=0.7)
        self.explain(
            "Avant une formule de dénombrement, décrivez ce qui distingue "
            "deux résultats. Les personnes sont-elles les mêmes ? "
            "Leurs rôles ont-ils changé ? Cette question indique quels ordres "
            "il faut conserver et lesquels comptent plusieurs fois le même choix.",
            question, method, source,
        )

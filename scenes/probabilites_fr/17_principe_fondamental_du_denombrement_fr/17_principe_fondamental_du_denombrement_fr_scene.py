"""Principe fondamental du dénombrement — seconde passe approfondie.

Objectif pédagogique
--------------------
Faire comprendre que le principe multiplicatif n'est pas un slogan du type
« ET = multiplier ». Il résume la structure d'un arbre régulier :

* un résultat complet correspond à un chemin complet ;
* si, à une étape donnée, chaque chemin partiel possède le même nombre de
  continuations, les nombres de choix se multiplient ;
* si les branches n'ont pas la même taille, on sépare les cas disjoints et on
  additionne leurs nombres de résultats.

La formule générale n'apparaît qu'après la construction et le regroupement des
chemins. Les scènes sont volontairement progressives et conservent les objets
importants assez longtemps pour relier l'intuition au calcul.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GRAY_D,
    GRAY_E,
    LEFT,
    RED_D,
    RIGHT,
    SEMIBOLD,
    UP,
    WHITE,
    Arrow,
    Brace,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Mobject,
    ReplacementTransform,
    RoundedRectangle,
    Scene,
    Tex,
    Text,
    TransformFromCopy,
    VGroup,
    Write,
    config,
)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from manim_voiceover import VoiceoverScene
    from tools.teaching_voiceover import TeachingAzureService as AzureService
except ImportError:
    VoiceoverScene = None
    AzureService = None

import tools.tts as tts
from tools.branding import play_uqam_intro

# ---------------------------------------------------------------------------
# Visual defaults
# ---------------------------------------------------------------------------
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
WARN = RED_D
MUTED = GRAY_D
PALE = GRAY_E
VOICE_SPEED = 0.90


# ---------------------------------------------------------------------------
# Narration
# ---------------------------------------------------------------------------
SCRIPT = [
    {
        "caption": "Comment compter tous les repas sans les lister ?",
        "ssml": tts.ssml(
            "Un café propose trois sandwichs et deux boissons. "
            "Combien de repas différents peut-on former ? "
            "Avec six résultats, on pourrait encore faire une liste. "
            "Mais avec des milliers de possibilités, cette méthode devient impossible. "
            "<break time='450ms'/>Nous cherchons donc une manière de compter les résultats "
            "sans devoir tous les écrire."
        ),
    },
    {
        "caption": "Un résultat complet contient un choix de chaque étape.",
        "ssml": tts.ssml(
            "Commençons par définir ce que nous comptons. "
            "<bookmark mark='stage_sandwich'/>À la première étape, on choisit un sandwich : "
            "poulet, végé ou thon. "
            "<bookmark mark='stage_drink'/>À la deuxième étape, on choisit une boisson : "
            "eau ou jus. "
            "<bookmark mark='sample_meal'/>Un résultat complet combine un choix de la première étape "
            "et un choix de la deuxième. Par exemple : poulet avec eau."
        ),
    },
    {
        "caption": "Chaque feuille de l’arbre est un résultat complet distinct.",
        "ssml": tts.ssml(
            "Représentons maintenant les choix par un arbre. "
            "<bookmark mark='tree_root'/>On part d'un repas encore vide. "
            "<bookmark mark='first_split'/>Le choix du sandwich crée trois premières branches. "
            "<bookmark mark='first_path'/>Suivons un seul chemin : poulet, puis eau. "
            "La feuille porte le repas complet poulet plus eau. "
            "<bookmark mark='first_pair'/>Avec poulet, le jus donne un deuxième repas. "
            "<bookmark mark='remaining_paths'/>On reproduit les mêmes deux boissons après végé, "
            "puis après thon. "
            "<bookmark mark='six_outcomes'/>Les six feuilles sont six repas distincts."
        ),
    },
    {
        "caption": "Trois groupes identiques de deux donnent 3 × 2 = 6.",
        "ssml": tts.ssml(
            "L'arbre contient une régularité. "
            "<bookmark mark='pair_groups'/>Après chacun des trois sandwichs, "
            "il y a exactement deux continuations. "
            "<bookmark mark='compact_groups'/>Conservons seulement ces trois groupes de deux. "
            f"<bookmark mark='repeated_sum'/>On peut compter deux, {tts.PLUS} deux, {tts.PLUS} deux. "
            "<bookmark mark='first_product'/>Comme le groupe de deux se répète trois fois, "
            "cette addition s'écrit trois multiplié par deux, donc six. "
            "<bookmark mark='two_stage_rule'/>Plus généralement, si chaque premier choix est suivi "
            "du même nombre de continuations, on multiplie les deux nombres."
        ),
    },
    {
        "caption": "Avec plusieurs étapes régulières, on multiplie tous les nombres de choix.",
        "ssml": tts.ssml(
            "La même structure peut comporter plus de deux étapes. "
            "<bookmark mark='code_slots'/>Considérons un code formé d'une lettre, puis de deux chiffres. "
            "<bookmark mark='code_counts'/>Il y a vingt-six choix pour la lettre, "
            "dix choix pour le premier chiffre et dix pour le deuxième. "
            "Les chiffres peuvent se répéter. "
            f"<bookmark mark='sample_code'/>Par exemple, {tts.char('M')} quarante-deux est un chemin complet. "
            "<bookmark mark='code_product'/>Le nombre total de codes est donc "
            "vingt-six multiplié par dix, puis encore par dix : deux mille six cents."
        ),
    },
    {
        "caption": "L’opération dépend de la structure des résultats, pas d’un mot isolé.",
        "ssml": tts.ssml(
            "Il faut maintenant éviter un mauvais raccourci. "
            "Les mots employés dans la phrase ne décident pas, à eux seuls, de l'opération. "
            "<bookmark mark='successive_structure'/>Pour former un repas complet, "
            "chaque résultat doit passer par l'étape sandwich puis par l'étape boisson. "
            "On multiplie les choix successifs. "
            "<bookmark mark='disjoint_structure'/>Si l'on achète un seul item, "
            "on est soit dans le cas sandwich, soit dans le cas boisson. "
            f"Ces deux cas ne se chevauchent pas : on additionne trois {tts.PLUS} deux. "
            "<bookmark mark='structure_warning'/>On regarde donc la structure des résultats, "
            "et non un mot pris hors contexte."
        ),
    },
    {
        "caption": "Branches inégales : séparer les cas, puis additionner leurs totaux.",
        "ssml": tts.ssml(
            "Que se passe-t-il si l'arbre n'est pas régulier ? "
            f"<bookmark mark='unequal_first_step'/>Supposons que le premier choix soit {tts.char('A')} ou {tts.char('B')}. "
            f"<bookmark mark='branch_a'/>Après {tts.char('A')}, il existe deux continuations. "
            f"<bookmark mark='branch_b'/>Après {tts.char('B')}, il en existe trois. "
            f"<bookmark mark='sum_cases'/>Le nombre total est alors le nombre de résultats du cas {tts.char('A')}, "
            f"{tts.PLUS} celui du cas {tts.char('B')} : deux {tts.PLUS} trois, donc cinq. "
            "<bookmark mark='no_uniform_factor'/>La deuxième étape n'offre pas un nombre fixe de choix "
            "sur toutes les branches ; la formule simple à deux facteurs ne s'applique donc pas directement."
        ),
    },
    {
        "caption": "Une formule de produit résume un arbre de choix régulier.",
        "ssml": tts.ssml(
            "À retenir. "
            "<bookmark mark='recap_result'/>D'abord, définissez clairement un résultat complet. "
            "<bookmark mark='recap_stages'/>Ensuite, découpez sa construction en étapes. "
            "<bookmark mark='recap_uniformity'/>Vérifiez enfin que, pour une étape donnée, "
            "chaque chemin partiel possède le même nombre de continuations. "
            "<bookmark mark='recap_product'/>Dans ce cas, avec k étapes, "
            "on multiplie n un, n deux, jusqu'à n k. "
            "<bookmark mark='recap_exception'/>Si les branches diffèrent, "
            "on sépare les cas disjoints, on compte chaque cas, puis on additionne. "
            "La formule n'est pas une recette magique : elle résume un arbre régulier."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


BaseScene = VoiceoverScene if VoiceoverScene is not None else Scene


class PrincipeFondamentalDenombrementFR(BaseScene):
    """Introduction visuelle rigoureuse au principe multiplicatif."""

    # ------------------------------------------------------------------
    # Voiceover utilities
    # ------------------------------------------------------------------
    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False

        if load_dotenv is not None:
            load_dotenv()

        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")
            return

        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover not installed. Rendering without narration.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print("[voiceover] Missing Azure Speech credentials. Rendering without narration.")
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)

        try:
            self.set_speech_service(
                AzureService(
                    voice=tts.VOICE_ID,
                )
            )
        except Exception as exc:
            print(f"[voiceover] Azure Speech setup failed: {exc}. Rendering without narration.")
            return

        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, item: dict[str, str]):
        if self._voiceover_enabled:
            with self.voiceover(
                text=item["ssml"],
                subcaption=item["caption"],
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark: str) -> None:
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def clear_page(self, *mobjects: Mobject, run_time: float = 0.65) -> None:
        visible = [mob for mob in mobjects if mob is not None]
        if visible:
            self.play(*(FadeOut(mob) for mob in visible), run_time=run_time)

    def make_heading(self, text: str, subtitle: str | None = None) -> VGroup:
        title = Text(text, font_size=39, weight=SEMIBOLD)
        if title.width > 12.0:
            title.scale_to_fit_width(12.0)

        if subtitle is None:
            return VGroup(title).to_edge(UP, buff=0.4)

        sub = Text(subtitle, font_size=25, color=MUTED)
        if sub.width > 11.7:
            sub.scale_to_fit_width(11.7)
        return VGroup(title, sub).arrange(DOWN, buff=0.15).to_edge(UP, buff=0.33)

    def choice_chip(
        self,
        label: str,
        *,
        width: float = 2.05,
        height: float = 0.65,
        font_size: int = 27,
        accent: bool = False,
    ) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.11,
            stroke_color=ACCENT if accent else BLACK,
            stroke_width=2.3,
            fill_color=ACCENT,
            fill_opacity=0.065 if accent else 0.025,
        )
        label_mob = Text(label, font_size=font_size)
        if label_mob.width > width - 0.25:
            label_mob.scale_to_fit_width(width - 0.25)
        label_mob.move_to(box)
        return VGroup(box, label_mob)

    def outcome_chip(self, label: str, position) -> VGroup:
        chip = self.choice_chip(
            label,
            width=2.55,
            height=0.54,
            font_size=23,
            accent=True,
        )
        return chip.move_to(position)

    def root_node(self, position) -> VGroup:
        circle = Circle(
            radius=0.27,
            stroke_color=BLACK,
            stroke_width=2.5,
            fill_color=WHITE,
            fill_opacity=1,
        )
        symbol = MathTex(r"\varnothing", font_size=27).move_to(circle)
        return VGroup(circle, symbol).move_to(position)

    def stage_slot(self, label: str) -> VGroup:
        box = RoundedRectangle(
            width=2.18,
            height=1.28,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.5,
            fill_color=ACCENT,
            fill_opacity=0.045,
        )
        label_mob = Text(label, font_size=26, color=MUTED).next_to(box, DOWN, buff=0.16)
        return VGroup(box, label_mob)

    def numbered_step(self, number: str, text: str) -> VGroup:
        badge = Circle(
            radius=0.27,
            stroke_color=ACCENT,
            stroke_width=2.5,
            fill_color=ACCENT,
            fill_opacity=0.08,
        )
        number_mob = MathTex(number, font_size=27, color=ACCENT).move_to(badge)
        sentence = Text(text, font_size=29)
        if sentence.width > 10.6:
            sentence.scale_to_fit_width(10.6)
        return VGroup(VGroup(badge, number_mob), sentence).arrange(RIGHT, buff=0.32)

    # ------------------------------------------------------------------
    # Scene
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        self.introduction()
        self.define_complete_result()
        self.tree_and_product()
        self.three_stage_example()
        self.structure_decides_operation()
        self.unequal_branches()
        self.conclusion()

    # ------------------------------------------------------------------
    # Page 1 — central question
    # ------------------------------------------------------------------
    def introduction(self) -> None:
        title = Text(
            "Dénombrement 1 — principe fondamental",
            font_size=39,
            weight=SEMIBOLD,
        )
        if title.width > 12.0:
            title.scale_to_fit_width(12.0)
        question = Text(
            "3 sandwichs, 2 boissons : combien de repas différents ?",
            font_size=31,
            color=MUTED,
        )
        prompt = VGroup(title, question).arrange(DOWN, buff=0.3)

        with self.narrated(SCRIPT[0]):
            self.play(Write(title), run_time=0.9)
            self.play(FadeIn(question, shift=UP * 0.14), run_time=0.65)
            self.wait(1.15)

        self.clear_page(prompt)

    # ------------------------------------------------------------------
    # Page 2 — define one complete outcome
    # ------------------------------------------------------------------
    def define_complete_result(self) -> None:
        heading = self.make_heading(
            "Avant de compter, définissons un résultat complet",
            "Un repas contient un sandwich et une boisson.",
        )

        sandwich_title = Text("Étape 1 — sandwich", font_size=27, color=MUTED)
        sandwiches = VGroup(
            self.choice_chip("Poulet"),
            self.choice_chip("Végé"),
            self.choice_chip("Thon"),
        ).arrange(DOWN, buff=0.2)
        sandwich_stage = VGroup(sandwich_title, sandwiches).arrange(DOWN, buff=0.23)
        sandwich_stage.move_to(LEFT * 3.5 + UP * 0.25)

        drink_title = Text("Étape 2 — boisson", font_size=27, color=MUTED)
        drinks = VGroup(
            self.choice_chip("Eau", accent=True),
            self.choice_chip("Jus", accent=True),
        ).arrange(DOWN, buff=0.27)
        drink_stage = VGroup(drink_title, drinks).arrange(DOWN, buff=0.3)
        drink_stage.move_to(RIGHT * 3.5 + UP * 0.25)

        arrow = Arrow(
            sandwich_stage.get_right() + RIGHT * 0.22,
            drink_stage.get_left() + LEFT * 0.22,
            buff=0.12,
            color=BLACK,
            stroke_width=3,
        )
        then = Text("puis", font_size=27, color=MUTED).next_to(arrow, UP, buff=0.11)

        sample_left = self.choice_chip("Poulet", width=1.85, height=0.58, font_size=25)
        plus = MathTex("+", font_size=39, color=ACCENT)
        sample_right = self.choice_chip(
            "Eau",
            width=1.55,
            height=0.58,
            font_size=25,
            accent=True,
        )
        sample = VGroup(sample_left, plus, sample_right).arrange(RIGHT, buff=0.2)
        sample.move_to(DOWN * 2.08)
        sample_caption = Text(
            "un résultat complet",
            font_size=25,
            color=MUTED,
        ).next_to(sample, DOWN, buff=0.16)

        with self.narrated(SCRIPT[1]):
            self.play(FadeIn(heading), run_time=0.45)

            self.wait_until_bookmark("stage_sandwich")
            self.play(
                FadeIn(sandwich_title),
                LaggedStart(
                    *(FadeIn(card, shift=RIGHT * 0.1) for card in sandwiches),
                    lag_ratio=0.2,
                ),
                run_time=1.0,
            )
            self.wait(0.55)

            self.wait_until_bookmark("stage_drink")
            self.play(GrowArrow(arrow), FadeIn(then), run_time=0.6)
            self.play(
                FadeIn(drink_title),
                LaggedStart(
                    *(FadeIn(card, shift=RIGHT * 0.1) for card in drinks),
                    lag_ratio=0.24,
                ),
                run_time=0.82,
            )
            self.wait(0.65)

            self.wait_until_bookmark("sample_meal")
            self.play(
                Indicate(sandwiches[0], color=ACCENT),
                Indicate(drinks[0], color=ACCENT),
                run_time=0.75,
            )
            self.play(
                TransformFromCopy(sandwiches[0], sample_left),
                FadeIn(plus),
                TransformFromCopy(drinks[0], sample_right),
                run_time=0.85,
            )
            self.play(FadeIn(sample_caption, shift=UP * 0.08), run_time=0.45)
            self.wait(1.0)

        self.clear_page(
            heading,
            sandwich_stage,
            drink_stage,
            arrow,
            then,
            sample,
            sample_caption,
        )

    # ------------------------------------------------------------------
    # Pages 3–4 — construct the tree, then compress it into a product
    # ------------------------------------------------------------------
    def tree_and_product(self) -> None:
        heading = self.make_heading(
            "Un résultat complet est un chemin dans l’arbre",
            "On construit d’abord un seul chemin, puis les autres.",
        )

        root = self.root_node(LEFT * 5.25 + DOWN * 0.05)
        root_label = Text("départ", font_size=22, color=MUTED).next_to(root, DOWN, buff=0.13)

        sandwich_names = ["Poulet", "Végé", "Thon"]
        sandwich_positions = [
            LEFT * 1.75 + UP * 1.5,
            LEFT * 1.75 + DOWN * 0.05,
            LEFT * 1.75 + DOWN * 1.6,
        ]
        sandwich_nodes = VGroup(
            *[
                self.choice_chip(name, width=1.55, height=0.56, font_size=23).move_to(position)
                for name, position in zip(sandwich_names, sandwich_positions)
            ]
        )

        leaf_labels = [
            "Poulet + Eau",
            "Poulet + Jus",
            "Végé + Eau",
            "Végé + Jus",
            "Thon + Eau",
            "Thon + Jus",
        ]
        leaf_positions = [
            RIGHT * 3.45 + UP * 1.98,
            RIGHT * 3.45 + UP * 1.29,
            RIGHT * 3.45 + UP * 0.48,
            RIGHT * 3.45 + DOWN * 0.21,
            RIGHT * 3.45 + DOWN * 1.02,
            RIGHT * 3.45 + DOWN * 1.71,
        ]
        leaves = [
            self.outcome_chip(label, position)
            for label, position in zip(leaf_labels, leaf_positions)
        ]

        first_arrows = VGroup(
            *[
                Arrow(
                    root.get_right(),
                    node.get_left(),
                    buff=0.14,
                    color=BLACK,
                    stroke_width=2.5,
                    max_tip_length_to_length_ratio=0.08,
                )
                for node in sandwich_nodes
            ]
        )

        second_arrows = VGroup()
        for index, node in enumerate(sandwich_nodes):
            second_arrows.add(
                Arrow(
                    node.get_right(),
                    leaves[2 * index].get_left(),
                    buff=0.14,
                    color=ACCENT,
                    stroke_width=2.35,
                    max_tip_length_to_length_ratio=0.08,
                ),
                Arrow(
                    node.get_right(),
                    leaves[2 * index + 1].get_left(),
                    buff=0.14,
                    color=ACCENT,
                    stroke_width=2.35,
                    max_tip_length_to_length_ratio=0.08,
                ),
            )

        total = VGroup(
            Text("6 feuilles", font_size=29),
            MathTex("=", font_size=38),
            Text("6 repas", font_size=29, color=ACCENT),
        ).arrange(RIGHT, buff=0.19).to_edge(DOWN, buff=0.42)

        pair_braces: list[Brace] = []
        pair_counts: list[MathTex] = []
        pair_groups: list[VGroup] = []
        for index in range(3):
            pair = VGroup(leaves[2 * index], leaves[2 * index + 1])
            brace = Brace(pair, RIGHT, buff=0.08, color=ACCENT)
            count = MathTex("2", font_size=31, color=ACCENT).next_to(brace, RIGHT, buff=0.08)
            pair_braces.append(brace)
            pair_counts.append(count)
            pair_groups.append(VGroup(pair, brace, count))

        with self.narrated(SCRIPT[2]):
            self.play(FadeIn(heading), run_time=0.45)

            self.wait_until_bookmark("tree_root")
            self.play(FadeIn(root, scale=0.9), FadeIn(root_label), run_time=0.55)

            self.wait_until_bookmark("first_split")
            for arrow, node in zip(first_arrows, sandwich_nodes):
                self.play(GrowArrow(arrow), FadeIn(node, scale=0.92), run_time=0.48)
            self.wait(0.55)

            self.wait_until_bookmark("first_path")
            self.play(GrowArrow(second_arrows[0]), run_time=0.55)
            self.play(FadeIn(leaves[0], shift=RIGHT * 0.1), run_time=0.5)
            self.play(Indicate(leaves[0], color=ACCENT), run_time=0.7)
            self.wait(0.6)

            self.wait_until_bookmark("first_pair")
            self.play(
                GrowArrow(second_arrows[1]),
                FadeIn(leaves[1], shift=RIGHT * 0.1),
                run_time=0.65,
            )
            self.wait(0.55)

            self.wait_until_bookmark("remaining_paths")
            self.play(
                LaggedStart(
                    GrowArrow(second_arrows[2]),
                    FadeIn(leaves[2], shift=RIGHT * 0.08),
                    GrowArrow(second_arrows[3]),
                    FadeIn(leaves[3], shift=RIGHT * 0.08),
                    GrowArrow(second_arrows[4]),
                    FadeIn(leaves[4], shift=RIGHT * 0.08),
                    GrowArrow(second_arrows[5]),
                    FadeIn(leaves[5], shift=RIGHT * 0.08),
                    lag_ratio=0.11,
                ),
                run_time=1.55,
            )
            self.wait(0.65)

            self.wait_until_bookmark("six_outcomes")
            self.play(Write(total), run_time=0.65)
            self.play(
                LaggedStart(
                    *(Indicate(leaf, color=ACCENT) for leaf in leaves),
                    lag_ratio=0.08,
                ),
                run_time=1.0,
            )
            self.wait(1.0)

        product_heading = self.make_heading(
            "L’arbre régulier devient une multiplication",
            "Chaque sandwich possède les mêmes deux continuations.",
        )
        group_labels = VGroup(
            Text("après Poulet", font_size=23, color=MUTED),
            Text("après Végé", font_size=23, color=MUTED),
            Text("après Thon", font_size=23, color=MUTED),
        )

        addition = MathTex(r"2+2+2=6", font_size=52).shift(DOWN * 1.17)
        product = MathTex(r"3\times2=6", font_size=58, color=ACCENT).move_to(addition)
        general = MathTex(r"N=n_1\times n_2", font_size=48).shift(DOWN * 2.28)
        condition = Text(
            "si chaque premier choix possède le même nombre de continuations",
            font_size=24,
            color=MUTED,
        ).next_to(general, DOWN, buff=0.13)
        if condition.width > 11.4:
            condition.scale_to_fit_width(11.4)

        compact_centres = [LEFT * 4.05 + UP * 0.42, UP * 0.42, RIGHT * 4.05 + UP * 0.42]

        with self.narrated(SCRIPT[3]):
            self.wait_until_bookmark("pair_groups")
            self.play(
                *(Create(brace) for brace in pair_braces),
                *(FadeIn(count) for count in pair_counts),
                run_time=0.75,
            )
            self.wait(0.65)

            self.wait_until_bookmark("compact_groups")
            self.play(
                FadeOut(root),
                FadeOut(root_label),
                FadeOut(sandwich_nodes),
                FadeOut(first_arrows),
                FadeOut(second_arrows),
                FadeOut(total),
                ReplacementTransform(heading, product_heading),
                run_time=0.55,
            )
            heading = product_heading
            self.play(
                *(group.animate.move_to(centre) for group, centre in zip(pair_groups, compact_centres)),
                run_time=0.85,
            )
            for label, group in zip(group_labels, pair_groups):
                label.next_to(group, UP, buff=0.16)
            self.play(FadeIn(group_labels, shift=DOWN * 0.08), run_time=0.5)
            self.wait(0.65)

            self.wait_until_bookmark("repeated_sum")
            self.play(Write(addition), run_time=0.75)
            self.wait(0.75)

            self.wait_until_bookmark("first_product")
            self.play(ReplacementTransform(addition, product), run_time=0.7)
            self.play(
                Indicate(VGroup(*pair_counts), color=ACCENT),
                run_time=0.75,
            )
            self.wait(0.7)

            self.wait_until_bookmark("two_stage_rule")
            self.play(Write(general), FadeIn(condition, shift=UP * 0.08), run_time=0.85)
            self.wait(1.15)

        self.clear_page(
            heading,
            VGroup(*pair_groups),
            group_labels,
            product,
            general,
            condition,
        )

    # ------------------------------------------------------------------
    # Page 5 — transfer to three stages
    # ------------------------------------------------------------------
    def three_stage_example(self) -> None:
        heading = self.make_heading(
            "Même principe avec trois étapes",
            "Un code contient une lettre, puis deux chiffres.",
        )

        slots = VGroup(
            self.stage_slot("lettre"),
            self.stage_slot("1er chiffre"),
            self.stage_slot("2e chiffre"),
        ).arrange(RIGHT, buff=0.72).shift(UP * 0.35)

        counts = VGroup(
            MathTex("26", font_size=42, color=ACCENT),
            MathTex("10", font_size=42, color=ACCENT),
            MathTex("10", font_size=42, color=ACCENT),
        )
        for count, slot in zip(counts, slots):
            count.next_to(slot[0], UP, buff=0.18)

        symbols = VGroup(
            Text("M", font_size=42, weight=SEMIBOLD),
            Text("4", font_size=42, weight=SEMIBOLD),
            Text("2", font_size=42, weight=SEMIBOLD),
        )
        for symbol, slot in zip(symbols, slots):
            symbol.move_to(slot[0])

        sample_label = Text(
            "un chemin complet : M42",
            font_size=27,
            color=MUTED,
        ).shift(DOWN * 1.35)

        repetition = Text(
            "Répétition des chiffres permise",
            font_size=24,
            color=MUTED,
        ).next_to(sample_label, DOWN, buff=0.16)

        product = MathTex(
            r"26\times10\times10=2600",
            font_size=56,
        ).to_edge(DOWN, buff=0.45)
        product.set_color_by_tex("2600", ACCENT)

        with self.narrated(SCRIPT[4]):
            self.play(FadeIn(heading), run_time=0.45)

            self.wait_until_bookmark("code_slots")
            self.play(
                LaggedStart(
                    *(FadeIn(slot, shift=UP * 0.1) for slot in slots),
                    lag_ratio=0.2,
                ),
                run_time=0.95,
            )
            self.wait(0.55)

            self.wait_until_bookmark("code_counts")
            self.play(
                LaggedStart(
                    *(FadeIn(count, shift=DOWN * 0.1) for count in counts),
                    lag_ratio=0.2,
                ),
                run_time=0.8,
            )
            self.play(FadeIn(repetition), run_time=0.4)
            self.wait(0.65)

            self.wait_until_bookmark("sample_code")
            self.play(
                LaggedStart(
                    *(FadeIn(symbol, scale=0.85) for symbol in symbols),
                    lag_ratio=0.2,
                ),
                run_time=0.8,
            )
            self.play(FadeIn(sample_label, shift=UP * 0.08), run_time=0.45)
            self.wait(0.7)

            self.wait_until_bookmark("code_product")
            self.play(Write(product), run_time=0.9)
            self.play(Indicate(counts, color=ACCENT), run_time=0.75)
            self.wait(1.05)

        self.clear_page(
            heading,
            slots,
            counts,
            symbols,
            sample_label,
            repetition,
            product,
        )

    # ------------------------------------------------------------------
    # Page 6 — product rule versus disjoint sum rule
    # ------------------------------------------------------------------
    def structure_decides_operation(self) -> None:
        heading = self.make_heading(
            "L’opération vient de la structure, pas d’un mot",
            "Observer comment un résultat complet est construit.",
        )
        divider = Line(UP * 2.2, DOWN * 2.25, color=PALE, stroke_width=2)

        left_title = Text("Étapes successives", font_size=29, color=ACCENT, weight=SEMIBOLD)
        left_title.move_to(LEFT * 3.45 + UP * 1.72)
        sandwich = self.choice_chip("Sandwich", width=2.0, height=0.62, font_size=26)
        drink = self.choice_chip("Boisson", width=2.0, height=0.62, font_size=26, accent=True)
        successive_arrow = Arrow(
            LEFT * 4.15,
            LEFT * 2.72,
            buff=0.1,
            color=BLACK,
            stroke_width=2.8,
        )
        pipeline = VGroup(sandwich, successive_arrow, drink).arrange(RIGHT, buff=0.24)
        pipeline.move_to(LEFT * 3.45 + UP * 0.45)
        left_formula = MathTex(r"3\times2=6", font_size=52, color=ACCENT)
        left_formula.move_to(LEFT * 3.45 + DOWN * 1.12)
        left_note = Text(
            "chaque résultat traverse les deux étapes",
            font_size=23,
            color=MUTED,
        ).move_to(LEFT * 3.45 + DOWN * 1.82)
        if left_note.width > 5.7:
            left_note.scale_to_fit_width(5.7)

        right_title = Text("Cas disjoints", font_size=29, weight=SEMIBOLD)
        right_title.move_to(RIGHT * 3.45 + UP * 1.72)
        case_sandwich = self.choice_chip("3 sandwichs", width=2.35, height=0.58, font_size=25)
        case_drink = self.choice_chip("2 boissons", width=2.35, height=0.58, font_size=25)
        cases = VGroup(case_sandwich, case_drink).arrange(DOWN, buff=0.26)
        cases.move_to(RIGHT * 3.45 + UP * 0.45)
        one_item = Text("choisir un seul item", font_size=24, color=MUTED)
        one_item.move_to(RIGHT * 3.45 + DOWN * 0.52)
        right_formula = MathTex(r"3+2=5", font_size=52)
        right_formula.move_to(RIGHT * 3.45 + DOWN * 1.12)
        right_note = Text(
            "chaque résultat appartient à un seul cas",
            font_size=23,
            color=MUTED,
        ).move_to(RIGHT * 3.45 + DOWN * 1.82)
        if right_note.width > 5.7:
            right_note.scale_to_fit_width(5.7)

        warning = Text(
            "Les mots « et » et « ou » seuls ne suffisent pas.",
            font_size=27,
            color=WARN,
        ).to_edge(DOWN, buff=0.34)

        with self.narrated(SCRIPT[5]):
            self.play(FadeIn(heading), Create(divider), run_time=0.55)

            self.wait_until_bookmark("successive_structure")
            self.play(FadeIn(left_title), run_time=0.4)
            self.play(
                FadeIn(sandwich),
                GrowArrow(successive_arrow),
                FadeIn(drink),
                run_time=0.75,
            )
            self.play(Write(left_formula), FadeIn(left_note), run_time=0.7)
            self.wait(0.75)

            self.wait_until_bookmark("disjoint_structure")
            self.play(FadeIn(right_title), run_time=0.4)
            self.play(
                LaggedStart(
                    FadeIn(case_sandwich, shift=RIGHT * 0.08),
                    FadeIn(case_drink, shift=RIGHT * 0.08),
                    lag_ratio=0.25,
                ),
                FadeIn(one_item),
                run_time=0.8,
            )
            self.play(Write(right_formula), FadeIn(right_note), run_time=0.7)
            self.wait(0.75)

            self.wait_until_bookmark("structure_warning")
            self.play(FadeIn(warning, shift=UP * 0.08), run_time=0.5)
            self.wait(1.0)

        self.clear_page(
            heading,
            divider,
            left_title,
            pipeline,
            left_formula,
            left_note,
            right_title,
            cases,
            one_item,
            right_formula,
            right_note,
            warning,
        )

    # ------------------------------------------------------------------
    # Page 7 — non-uniform branching
    # ------------------------------------------------------------------
    def unequal_branches(self) -> None:
        heading = self.make_heading(
            "Branches inégales : séparer les cas",
            "Le nombre de continuations dépend ici du premier choix.",
        )

        root = self.root_node(LEFT * 4.9)
        case_a = self.choice_chip("A", width=1.05, height=0.58, font_size=27)
        case_b = self.choice_chip("B", width=1.05, height=0.58, font_size=27)
        case_a.move_to(LEFT * 1.72 + UP * 1.15)
        case_b.move_to(LEFT * 1.72 + DOWN * 1.15)

        first_arrows = VGroup(
            Arrow(root.get_right(), case_a.get_left(), buff=0.14, color=BLACK, stroke_width=2.6),
            Arrow(root.get_right(), case_b.get_left(), buff=0.14, color=BLACK, stroke_width=2.6),
        )

        leaves_a = VGroup(
            self.choice_chip("A1", width=1.15, height=0.52, font_size=24, accent=True),
            self.choice_chip("A2", width=1.15, height=0.52, font_size=24, accent=True),
        ).arrange(DOWN, buff=0.22).move_to(RIGHT * 2.1 + UP * 1.15)

        leaves_b = VGroup(
            self.choice_chip("B1", width=1.15, height=0.52, font_size=24, accent=True),
            self.choice_chip("B2", width=1.15, height=0.52, font_size=24, accent=True),
            self.choice_chip("B3", width=1.15, height=0.52, font_size=24, accent=True),
        ).arrange(DOWN, buff=0.18).move_to(RIGHT * 2.1 + DOWN * 1.15)

        arrows_a = VGroup(
            *[
                Arrow(case_a.get_right(), leaf.get_left(), buff=0.14, color=ACCENT, stroke_width=2.4)
                for leaf in leaves_a
            ]
        )
        arrows_b = VGroup(
            *[
                Arrow(case_b.get_right(), leaf.get_left(), buff=0.14, color=ACCENT, stroke_width=2.4)
                for leaf in leaves_b
            ]
        )

        brace_a = Brace(leaves_a, RIGHT, buff=0.08, color=ACCENT)
        count_a = MathTex("2", font_size=34, color=ACCENT).next_to(brace_a, RIGHT, buff=0.08)
        brace_b = Brace(leaves_b, RIGHT, buff=0.08, color=ACCENT)
        count_b = MathTex("3", font_size=34, color=ACCENT).next_to(brace_b, RIGHT, buff=0.08)

        result = MathTex(r"N=N_A+N_B=2+3=5", font_size=50).to_edge(DOWN, buff=0.42)
        result.set_color_by_tex("5", ACCENT)
        warning = Text(
            "La deuxième étape n’a pas un nombre uniforme de choix.",
            font_size=26,
            color=WARN,
        ).next_to(result, UP, buff=0.17)

        with self.narrated(SCRIPT[6]):
            self.play(FadeIn(heading), FadeIn(root), run_time=0.5)

            self.wait_until_bookmark("unequal_first_step")
            self.play(
                GrowArrow(first_arrows[0]),
                GrowArrow(first_arrows[1]),
                FadeIn(case_a),
                FadeIn(case_b),
                run_time=0.72,
            )
            self.wait(0.5)

            self.wait_until_bookmark("branch_a")
            self.play(
                LaggedStart(
                    GrowArrow(arrows_a[0]),
                    FadeIn(leaves_a[0], shift=RIGHT * 0.08),
                    GrowArrow(arrows_a[1]),
                    FadeIn(leaves_a[1], shift=RIGHT * 0.08),
                    lag_ratio=0.16,
                ),
                run_time=0.9,
            )
            self.play(Create(brace_a), FadeIn(count_a), run_time=0.45)
            self.wait(0.55)

            self.wait_until_bookmark("branch_b")
            self.play(
                LaggedStart(
                    GrowArrow(arrows_b[0]),
                    FadeIn(leaves_b[0], shift=RIGHT * 0.08),
                    GrowArrow(arrows_b[1]),
                    FadeIn(leaves_b[1], shift=RIGHT * 0.08),
                    GrowArrow(arrows_b[2]),
                    FadeIn(leaves_b[2], shift=RIGHT * 0.08),
                    lag_ratio=0.12,
                ),
                run_time=1.15,
            )
            self.play(Create(brace_b), FadeIn(count_b), run_time=0.45)
            self.wait(0.65)

            self.wait_until_bookmark("sum_cases")
            self.play(Write(result), run_time=0.8)
            self.wait(0.7)

            self.wait_until_bookmark("no_uniform_factor")
            self.play(FadeIn(warning, shift=UP * 0.08), run_time=0.5)
            self.play(Indicate(VGroup(count_a, count_b), color=WARN), run_time=0.75)
            self.wait(1.0)

        self.clear_page(
            heading,
            root,
            case_a,
            case_b,
            first_arrows,
            leaves_a,
            leaves_b,
            arrows_a,
            arrows_b,
            brace_a,
            count_a,
            brace_b,
            count_b,
            warning,
            result,
        )

    # ------------------------------------------------------------------
    # Page 8 — stable synthesis
    # ------------------------------------------------------------------
    def conclusion(self) -> None:
        heading = self.make_heading(
            "Principe fondamental du dénombrement",
            "La formule résume la structure d’un arbre régulier.",
        )

        steps = VGroup(
            self.numbered_step("1", "Définir un résultat."),
            self.numbered_step("2", "Distinguer les étapes."),
            self.numbered_step("3", "Compter les choix à chaque étape."),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.38).shift(UP * 0.56)

        product_card = VGroup(
            Text("Branches régulières", font_size=25, color=ACCENT, weight=SEMIBOLD),
            MathTex(r"N=n_1\times n_2\times\cdots\times n_k", font_size=45, color=ACCENT),
            Text(
                "même nombre de choix sur chaque branche",
                font_size=22,
                color=MUTED,
            ),
        ).arrange(DOWN, buff=0.12)
        product_box = RoundedRectangle(
            width=max(8.0, product_card.width + 0.7),
            height=max(2.0, product_card.height + 0.5),
            corner_radius=0.12,
            stroke_color=ACCENT,
            stroke_width=2.2,
            fill_color=ACCENT,
            fill_opacity=0.045,
        ).move_to(product_card)
        product_group = VGroup(product_box, product_card)

        sum_card = VGroup(
            Text("Branches inégales", font_size=25, weight=SEMIBOLD),
            Text("séparer en cas disjoints", font_size=25),
            MathTex(r"N=N_1+N_2+\cdots", font_size=40),
        ).arrange(DOWN, buff=0.12)
        sum_box = RoundedRectangle(
            width=max(8.0, sum_card.width + 0.7),
            height=max(2.0, sum_card.height + 0.5),
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.0,
            fill_color=BLACK,
            fill_opacity=0.018,
        ).move_to(sum_card)
        sum_group = VGroup(sum_box, sum_card)

        product_group.move_to([0, 0, 0])
        sum_group.move_to([0, 0, 0])

        with self.narrated(SCRIPT[7]):
            self.play(FadeIn(heading), run_time=0.45)

            self.wait_until_bookmark("recap_result")
            self.play(FadeIn(steps[0], shift=RIGHT * 0.1), run_time=0.52)
            self.wait(0.4)

            self.wait_until_bookmark("recap_stages")
            self.play(FadeIn(steps[1], shift=RIGHT * 0.1), run_time=0.52)
            self.wait(0.4)

            self.wait_until_bookmark("recap_uniformity")
            self.play(FadeIn(steps[2], shift=RIGHT * 0.1), run_time=0.52)
            self.wait(0.55)

            self.wait_until_bookmark("recap_product")
            self.play(FadeOut(steps), run_time=0.4)
            self.play(FadeIn(product_group, shift=UP * 0.08), run_time=0.65)
            self.wait(0.65)

            self.wait_until_bookmark("recap_exception")
            self.play(FadeOut(product_group), run_time=0.4)
            self.play(FadeIn(sum_group, shift=UP * 0.08), run_time=0.65)
            self.wait(2.0)

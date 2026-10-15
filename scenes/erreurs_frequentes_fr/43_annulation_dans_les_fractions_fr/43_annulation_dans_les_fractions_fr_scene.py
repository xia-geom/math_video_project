from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os

from manim import (
    BLACK,
    DOWN,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    LEFT,
    Line,
    MathTex,
    RIGHT,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    Tex,
    Text,
    Transform,
    TransformMatchingTex,
    UP,
    VGroup,
    WHITE,
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
from tools.teaching_chapters import (
    ACCENT as PILOT_ACCENT, ERROR as PILOT_ERROR, SUCCESS as PILOT_SUCCESS,
    play_chapter_outline, play_lesson_opening,
)

CHAPTERS = (
    'Tester une simplification',
    'Facteurs ou termes ?',
    'Factoriser et garder les restrictions',
    'Vérifier sa méthode',
)


config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class AnnulationFractionsFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    """Comprendre pourquoi on simplifie des facteurs, jamais des termes."""

    ACCENT = PILOT_ACCENT
    ACCENT_2 = PILOT_ACCENT
    SUCCESS = PILOT_SUCCESS
    ERROR = PILOT_ERROR

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        self.teaching_timeline = []
        if load_dotenv is not None:
            load_dotenv()
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            return
        if VoiceoverScene is None or AzureService is None:
            raise RuntimeError(
                "Narrated render requires manim-voiceover; select "
                "MANIM_DISABLE_VOICEOVER=1 for an explicit silent preview."
            )

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            raise RuntimeError(
                "Narrated render requires Azure Speech credentials; select "
                "MANIM_DISABLE_VOICEOVER=1 for an explicit silent preview."
            )

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)
        self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        self._voiceover_enabled = True

    @contextmanager
    def narration(self, spoken: str):
        """Create a voiceover context with SSML-free captions."""
        import json
        from pathlib import Path

        start = float(self.renderer.time)
        if self._voiceover_enabled:
            with self.voiceover(text=tts.ssml(spoken), subcaption=tts.strip_ssml(spoken)) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()
        self.teaching_timeline.append({
            'start': start, 'end': float(self.renderer.time), 'text': tts.strip_ssml(spoken),
            'mode': 'azure_review' if self._voiceover_enabled else 'silent_preview',
        })
        destination = os.getenv('TEACHING_TIMING_PATH')
        if destination:
            Path(destination).write_text(json.dumps(self.teaching_timeline,
                                                   ensure_ascii=False, indent=2) + '\n')

    def factor_box(
        self,
        tex: str,
        *,
        color=BLACK,
        fill_opacity: float = 0.06,
        font_size: int = 46,
    ) -> VGroup:
        factor = MathTex(tex, font_size=font_size, color=color)
        box = RoundedRectangle(
            width=factor.width + 0.46,
            height=factor.height + 0.34,
            corner_radius=0.12,
            stroke_color=color,
            stroke_width=2.5,
            fill_color=color,
            fill_opacity=fill_opacity,
        )
        return VGroup(box, factor)

    def product_fraction_blocks(
        self,
        numerator: tuple[str, str],
        denominator: tuple[str, str],
    ) -> VGroup:
        top_left = self.factor_box(numerator[0], color=self.ACCENT)
        top_right = self.factor_box(numerator[1])
        top_dot = MathTex(r"\cdot", font_size=46)
        top = VGroup(top_left, top_dot, top_right).arrange(RIGHT, buff=0.20)

        bottom_left = self.factor_box(denominator[0], color=self.ACCENT)
        bottom_right = self.factor_box(denominator[1])
        bottom_dot = MathTex(r"\cdot", font_size=46)
        bottom = VGroup(bottom_left, bottom_dot, bottom_right).arrange(RIGHT, buff=0.20)

        width = max(top.width, bottom.width) + 0.35
        bar = Line(LEFT * width / 2, RIGHT * width / 2, color=BLACK, stroke_width=3)
        return VGroup(top, bar, bottom).arrange(DOWN, buff=0.18)

    def sum_fraction_blocks(
        self,
        numerator: tuple[str, str],
        denominator: tuple[str, str],
    ) -> VGroup:
        top_left = self.factor_box(
            numerator[0], color=self.ACCENT, fill_opacity=0.04
        )
        top_plus = MathTex("+", font_size=46, color=self.ERROR)
        top_right = self.factor_box(numerator[1], fill_opacity=0.02)
        top = VGroup(top_left, top_plus, top_right).arrange(RIGHT, buff=0.20)

        bottom_left = self.factor_box(
            denominator[0], color=self.ACCENT, fill_opacity=0.04
        )
        bottom_plus = MathTex("+", font_size=46, color=self.ERROR)
        bottom_right = self.factor_box(denominator[1], fill_opacity=0.02)
        bottom = VGroup(bottom_left, bottom_plus, bottom_right).arrange(RIGHT, buff=0.20)

        width = max(top.width, bottom.width) + 0.35
        bar = Line(LEFT * width / 2, RIGHT * width / 2, color=BLACK, stroke_width=3)
        return VGroup(top, bar, bottom).arrange(DOWN, buff=0.18)

    def rule_box(self, text: str, *, color=BLACK, font_size: int = 34) -> VGroup:
        label = Text(text, font_size=font_size, color=color, weight="BOLD")
        box = RoundedRectangle(
            width=label.width + 0.65,
            height=label.height + 0.42,
            corner_radius=0.16,
            stroke_color=color,
            stroke_width=3,
            fill_color=WHITE,
            fill_opacity=1,
        )
        return VGroup(box, label)

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_lesson_opening(self, 'Annulation dans les fractions',
                            'Simplifier des facteurs communs\nen conservant les valeurs interdites.',
                            narration=self.narration)
        play_chapter_outline(self, CHAPTERS, 0,
                             'Testons d’abord une simplification qui paraît naturelle.',
                             narration=self.narration)

        # ------------------------------------------------------------------
        # Act 1 — Central question and a fast numerical test
        # ------------------------------------------------------------------
        title = Text(
            "Peut-on vraiment simplifier ici ?",
            font_size=46,
            weight="BOLD",
        ).to_edge(UP, buff=0.5)

        temptation = MathTex(
            r"\frac{x+2}{x+5}",
            r"\stackrel{?}{=}",
            r"\frac{2}{5}",
            font_size=62,
        )
        temptation.set_color_by_tex("x", self.ACCENT)
        temptation[2].set_color(self.ERROR)

        question = Text(
            "Le x apparaît en haut et en bas. Peut-on le barrer ?",
            font_size=31,
            color=self.ACCENT,
        ).next_to(temptation, DOWN, buff=0.45)

        narration = (
            "Peut-on simplifier x plus deux sur x plus cinq en supprimant les deux x ? "
            "Le geste paraît naturel, parce que le même symbole apparaît en haut et en bas. "
            "Mais une simplification ne dépend pas seulement des symboles présents. "
            "Elle dépend surtout de la structure des opérations."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 5.0)
            self.play(Write(title), run_time=0.20 * duration)
            self.play(Write(temptation), run_time=0.28 * duration)
            self.play(FadeIn(question), run_time=0.18 * duration)
            self.wait(0.34 * duration)

        test_label = Text(
            "Testons avec x = 3",
            font_size=31,
            weight="BOLD",
        ).next_to(title, DOWN, buff=0.42)
        test = MathTex(
            r"\frac{3+2}{3+5}",
            r"=",
            r"\frac58",
            r"\neq",
            r"\frac25",
            font_size=58,
        )
        test[2].set_color(self.ACCENT)
        test[3].set_color(self.ERROR)
        test[4].set_color(self.ERROR)
        rejected = self.rule_box(
            "La simplification proposée est fausse.",
            color=self.ERROR,
            font_size=30,
        ).next_to(test, DOWN, buff=0.50)

        narration = (
            "Un test numérique suffit déjà à repérer le problème. Prenons x égal à trois. "
            "La fraction de départ vaut cinq huitièmes. Elle ne vaut pas deux cinquièmes. "
            "Donc on ne peut pas annuler un terme seulement parce qu'il apparaît dans les deux sommes. "
            "Comprenons maintenant ce qui peut réellement être annulé."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 5.0)
            self.play(
                FadeOut(question),
                FadeOut(temptation),
                FadeIn(test_label),
                run_time=0.20 * duration,
            )
            self.play(Write(test), run_time=0.30 * duration)
            self.play(GrowFromCenter(rejected), run_time=0.18 * duration)
            self.wait(0.32 * duration)

        self.play(
            FadeOut(test_label),
            FadeOut(test),
            FadeOut(rejected),
            title.animate.scale(0.79).to_edge(UP, buff=0.5),
            run_time=0.8,
        )

        # ------------------------------------------------------------------
        # Act 2 — Products: complete factors can be removed
        # ------------------------------------------------------------------
        play_chapter_outline(self, CHAPTERS, 1,
                             'Distinguons maintenant les facteurs des termes.', narration=self.narration)
        self.play(FadeIn(title), run_time=0.35)
        section = Text(
            "Quand la simplification fonctionne",
            font_size=35,
            weight="BOLD",
        ).next_to(title, DOWN, buff=0.38)
        product = self.product_fraction_blocks(("3", "2"), ("3", "5")).shift(DOWN * 0.15)
        caption = Text(
            "Les deux 3 sont des facteurs complets.",
            font_size=29,
            color=self.ACCENT,
        ).next_to(product, DOWN, buff=0.42)

        narration = (
            "Regardons d'abord une fraction construite avec des produits. "
            "Au numérateur, trois multiplie deux. Au dénominateur, trois multiplie cinq. "
            "Chaque trois est donc un facteur complet de toute sa ligne. "
            "Nous pouvons séparer la fraction en trois sur trois, multiplié par deux sur cinq."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 6.0)
            self.play(Write(section), run_time=0.17 * duration)
            self.play(FadeIn(product), run_time=0.32 * duration)
            self.play(FadeIn(caption), run_time=0.18 * duration)
            self.wait(0.33 * duration)

        decomposition = MathTex(
            r"\frac{3\cdot2}{3\cdot5}",
            r"=",
            r"\frac33\cdot\frac25",
            r"=",
            r"1\cdot\frac25",
            r"=",
            r"\frac25",
            font_size=49,
        ).shift(DOWN * 0.15)
        decomposition[2].set_color(self.ACCENT)
        decomposition[6].set_color(self.SUCCESS)
        valid_rule = self.rule_box(
            "Un facteur commun représente un quotient égal à 1.",
            color=self.SUCCESS,
            font_size=29,
        ).next_to(decomposition, DOWN, buff=0.48)

        narration = (
            "Trois sur trois vaut un. Ce facteur ne change donc pas la valeur de la fraction. "
            "C'est le vrai sens de l'annulation : on ne fait pas disparaître des symboles par magie. "
            "On remplace un facteur commun par le nombre un. Le résultat est bien deux cinquièmes."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 5.5)
            self.play(
                FadeOut(product),
                FadeOut(caption),
                run_time=0.16 * duration,
            )
            self.play(FadeIn(decomposition), run_time=0.16 * duration)
            self.play(GrowFromCenter(valid_rule), run_time=0.22 * duration)
            self.wait(0.46 * duration)

        self.play(
            FadeOut(section),
            FadeOut(decomposition),
            FadeOut(valid_rule),
            run_time=0.7,
        )

        # ------------------------------------------------------------------
        # Act 3 — Sums: terms are not independent multiplicative factors
        # ------------------------------------------------------------------
        section = Text(
            "Pourquoi l'addition bloque l'annulation",
            font_size=35,
            weight="BOLD",
        ).next_to(title, DOWN, buff=0.38)
        sums = self.sum_fraction_blocks(("3", "2"), ("3", "5")).shift(DOWN * 0.15)
        plus_labels = VGroup(
            Text("addition", font_size=25, color=self.ERROR),
            Text("addition", font_size=25, color=self.ERROR),
        )
        plus_labels[0].next_to(sums[0][1], UP, buff=0.30)
        plus_labels[1].next_to(sums[2][1], DOWN, buff=0.30)

        narration = (
            "Comparons avec trois plus deux sur trois plus cinq. "
            "Cette fois, le trois n'est pas un facteur qui multiplie toute la ligne. "
            "C'est seulement un terme à l'intérieur d'une addition. "
            "Enlever ce terme modifierait la valeur de chaque somme."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 5.5)
            self.play(Write(section), run_time=0.18 * duration)
            self.play(FadeIn(sums), run_time=0.30 * duration)
            self.play(FadeIn(plus_labels), run_time=0.18 * duration)
            self.wait(0.34 * duration)

        evaluation = MathTex(
            r"\frac{3+2}{3+5}",
            r"=",
            r"\frac58",
            r"\neq",
            r"\frac25",
            font_size=55,
        ).shift(DOWN * 0.10)
        evaluation[2].set_color(self.ACCENT)
        evaluation[3:].set_color(self.ERROR)
        central_rule = self.rule_box(
            "On simplifie des facteurs, jamais des termes.",
            color=self.ACCENT,
            font_size=34,
        ).next_to(evaluation, DOWN, buff=0.52)

        narration = (
            "La fraction vaut cinq huitièmes, et non deux cinquièmes. "
            "Voici donc la règle centrale : on simplifie des facteurs, jamais des termes. "
            "Les signes plus et moins sont des barrières. Pour simplifier, il faut d'abord transformer "
            "les expressions en produits, lorsque la factorisation le permet."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 5.5)
            self.play(
                FadeOut(sums),
                FadeOut(plus_labels),
                run_time=0.15 * duration,
            )
            self.play(FadeIn(evaluation), run_time=0.15 * duration)
            self.play(GrowFromCenter(central_rule), run_time=0.23 * duration)
            self.wait(0.47 * duration)

        self.play(
            FadeOut(section),
            FadeOut(evaluation),
            FadeOut(central_rule),
            run_time=0.7,
        )

        # ------------------------------------------------------------------
        # Act 4 — Algebraic cancellation and its restriction
        # ------------------------------------------------------------------
        play_chapter_outline(self, CHAPTERS, 2,
                             'Factorisons, en gardant les valeurs interdites de départ.', narration=self.narration)
        self.play(FadeIn(title), run_time=0.35)
        section = Text(
            "Le même raisonnement avec x",
            font_size=35,
            weight="BOLD",
        ).next_to(title, DOWN, buff=0.38)
        algebra = MathTex(
            r"\frac{x(x+2)}{x(x+5)}",
            font_size=61,
        )
        algebra.set_color_by_tex("x", self.ACCENT)
        factor_note = Text(
            "Le x extérieur multiplie toute la parenthèse.",
            font_size=29,
            color=self.ACCENT,
        ).next_to(algebra, DOWN, buff=0.45)

        narration = (
            "Dans x fois x plus deux, sur x fois x plus cinq, le x extérieur est bien un facteur complet. "
            "Il multiplie toute la parenthèse au numérateur, et toute la parenthèse au dénominateur. "
            "On peut donc isoler x sur x."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 5.2)
            self.play(Write(section), run_time=0.18 * duration)
            self.play(Write(algebra), run_time=0.30 * duration)
            self.play(FadeIn(factor_note), run_time=0.20 * duration)
            self.wait(0.32 * duration)

        algebra_steps = MathTex(
            r"\frac{x(x+2)}{x(x+5)}",
            r"=",
            r"\frac{x}{x}\cdot\frac{x+2}{x+5}",
            r"=",
            r"\frac{x+2}{x+5}",
            font_size=45,
        )
        algebra_steps.set_color_by_tex(r"\frac{x}{x}", self.ACCENT)
        algebra_steps[4].set_color(self.SUCCESS)
        restriction = MathTex(r"x\neq0\quad\text{et}\quad x\neq-5", font_size=39, color=self.ERROR)
        restriction.next_to(algebra_steps, DOWN, buff=0.48)
        restriction_text = Text(
            "Les valeurs interdites viennent de la fraction originale.",
            font_size=27,
            color=self.ERROR,
        ).next_to(restriction, DOWN, buff=0.20)

        narration = (
            "Le dénominateur d'origine impose deux restrictions : x différent de zéro et de moins cinq. "
            "Puisque x est non nul, x sur x vaut un. On obtient alors x plus deux sur x plus cinq. "
            "Les deux restrictions restent valables après simplification."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 5.7)
            self.play(
                FadeOut(algebra),
                FadeOut(factor_note),
                run_time=0.15 * duration,
            )
            self.play(Write(restriction), run_time=0.18 * duration)
            self.play(FadeIn(restriction_text), run_time=0.18 * duration)
            self.play(FadeIn(algebra_steps), run_time=0.15 * duration)
            self.wait(0.34 * duration)

        self.play(
            FadeOut(section),
            FadeOut(algebra_steps),
            FadeOut(restriction),
            FadeOut(restriction_text),
            run_time=0.7,
        )

        # ------------------------------------------------------------------
        # Act 5 — Factor first, then simplify
        # ------------------------------------------------------------------
        section = Text(
            "Factoriser pour voir les facteurs communs",
            font_size=35,
            weight="BOLD",
        ).next_to(title, DOWN, buff=0.38)
        original = MathTex(
            r"\frac{x^2-4}{x^2+3x+2}",
            font_size=61,
        )
        no_cancel = Text(
            "Sous cette forme, aucun facteur commun n'est visible.",
            font_size=29,
            color=self.ERROR,
        ).next_to(original, DOWN, buff=0.46)

        narration = (
            "Prenons maintenant x carré moins quatre, sur x carré plus trois x plus deux. "
            "On voit des x dans les deux lignes, mais cela ne permet aucune annulation. "
            "Les x sont enfermés dans des additions et des soustractions. "
            "Nous devons d'abord factoriser chaque polynôme."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 5.7)
            self.play(Write(section), run_time=0.17 * duration)
            self.play(Write(original), run_time=0.30 * duration)
            self.play(FadeIn(no_cancel), run_time=0.20 * duration)
            self.wait(0.33 * duration)

        numerator_factor = MathTex(
            r"x^2-4=(x-2)(x+2)",
            font_size=45,
        )
        denominator_factor = MathTex(
            r"x^2+3x+2=(x+1)(x+2)",
            font_size=45,
        )
        factoring = VGroup(numerator_factor, denominator_factor).arrange(DOWN, buff=0.42)
        factoring.shift(DOWN * 0.05)
        factoring[0].set_color_by_tex("x+2", self.ACCENT)
        factoring[1].set_color_by_tex("x+2", self.ACCENT)

        narration = (
            "Le numérateur est une différence de carrés : x moins deux, fois x plus deux. "
            "Le dénominateur se factorise en x plus un, fois x plus deux. "
            "Maintenant seulement, le facteur commun x plus deux devient visible."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 5.4)
            self.play(
                FadeOut(original),
                FadeOut(no_cancel),
                run_time=0.17 * duration,
            )
            self.play(FadeIn(factoring), run_time=0.17 * duration)
            self.wait(0.66 * duration)

        factored = MathTex(
            r"\frac{(x-2)(x+2)}{(x+1)(x+2)}",
            r"=",
            r"\frac{x-2}{x+1}",
            font_size=50,
        )
        factored.set_color_by_tex("x+2", self.ACCENT)
        factored[2].set_color(self.SUCCESS)
        common_label = Text(
            "facteur commun",
            font_size=27,
            color=self.ACCENT,
        ).next_to(factored[0], UP, buff=0.35)
        final_restrictions = MathTex(
            r"x\neq-2\quad\text{et}\quad x\neq-1",
            font_size=38,
            color=self.ERROR,
        ).next_to(factored, DOWN, buff=0.47)

        narration = (
            "Le dénominateur factorisé impose x différent de moins deux et de moins un. "
            "Sur ce domaine, le facteur x plus deux est non nul : on peut le simplifier. "
            "On obtient x moins deux sur x plus un, en gardant les deux valeurs interdites. "
            "En particulier, moins deux reste exclu après la simplification."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 6.2)
            self.play(FadeOut(factoring), run_time=0.17 * duration)
            self.play(Write(final_restrictions), run_time=0.22 * duration)
            self.play(
                FadeIn(factored),
                FadeIn(common_label),
                run_time=0.17 * duration,
            )
            self.wait(0.44 * duration)

        self.play(
            FadeOut(section),
            FadeOut(factored),
            FadeOut(common_label),
            FadeOut(final_restrictions),
            run_time=0.7,
        )

        # ------------------------------------------------------------------
        # Act 6 — Diagnostic challenge
        # ------------------------------------------------------------------
        play_chapter_outline(self, CHAPTERS, 3,
                             'Vérifions maintenant notre méthode sur trois exemples.', narration=self.narration)
        self.play(FadeIn(title), run_time=0.35)
        section = Text(
            "Défi : peut-on simplifier le 5 ?",
            font_size=36,
            weight="BOLD",
        ).next_to(title, DOWN, buff=0.38)
        diagnostics = (
            (r"\frac{5x}{5y}\quad(y\ne0)", r"\frac{x}{y}\quad(y\ne0)",
             "OUI : 5 est un facteur commun.", self.SUCCESS,
             "Dans cinq x sur cinq y, avec y non nul, peut-on simplifier le cinq ?",
             "Oui. Cinq multiplie toute la ligne en haut et en bas. Le quotient vaut x sur y, avec y non nul."),
            (r"\frac{5+x}{5+y}\quad(y\ne-5)", r"\frac{5+x}{5+y}\quad(y\ne-5)",
             "NON : 5 est un terme de chaque somme.", self.ERROR,
             "Dans cinq plus x sur cinq plus y, peut-on supprimer les deux cinq ?",
             "Non. Cinq est un terme de chaque somme. On ne peut pas le supprimer. Le dénominateur exige y différent de moins cinq."),
            (r"\frac{5(x+1)}{5(x-2)}\quad(x\ne2)", r"\frac{x+1}{x-2}\quad(x\ne2)",
             "OUI : 5 multiplie chaque parenthèse.", self.SUCCESS,
             "Dans cinq fois x plus un, sur cinq fois x moins deux, peut-on simplifier le cinq ?",
             "Oui. Cinq est un facteur complet. On obtient x plus un sur x moins deux, et x reste différent de deux."),
        )
        self.play(Write(section), run_time=0.5)
        for premise, result, label, color, prompt, answer in diagnostics:
            question_math = MathTex(premise, font_size=48).move_to([0, 0.4, 0])
            with self.narration(prompt):
                self.play(FadeIn(question_math), run_time=0.5)
                self.wait(2.0)
            self.wait(3.0)  # Reflection starts after the complete spoken question.
            solution = MathTex(result, font_size=48, color=color).move_to([0, 0.4, 0])
            verdict = Text(label, font_size=30, color=color).next_to(solution, DOWN, buff=0.5)
            with self.narration(answer):
                self.play(FadeOut(question_math), run_time=0.35)
                self.play(FadeIn(solution), FadeIn(verdict), run_time=0.5)
                self.wait(4.0)
            self.play(FadeOut(solution), FadeOut(verdict), run_time=0.35)
        self.play(FadeOut(section), run_time=0.5)

        # ------------------------------------------------------------------
        # Act 7 — Final summary
        # ------------------------------------------------------------------
        summary_title = Text(
            "À retenir",
            font_size=42,
            weight="BOLD",
            color=self.ACCENT,
        ).next_to(title, DOWN, buff=0.42)
        summary = VGroup(
            Text("1. Repérer les valeurs interdites d'origine.", font_size=31),
            Text("2. Factoriser lorsque c'est possible.", font_size=31),
            Text("3. Simplifier des facteurs, jamais des termes.", font_size=31),
            Text("4. Garder les restrictions après simplification.", font_size=31),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        summary[0].set_color(self.ERROR)
        summary[2].set_color(self.ACCENT)
        summary[3].set_color(self.ERROR)
        summary.shift(DOWN * 0.10)

        final_rule = self.rule_box(
            "Même symbole ≠ facteur commun",
            color=self.ACCENT,
            font_size=33,
        ).next_to(summary, DOWN, buff=0.52)

        narration = (
            "Retenons quatre étapes. D'abord, repérer les valeurs interdites d'origine. "
            "Ensuite, factoriser lorsque c'est possible. "
            "Simplifier uniquement des facteurs complets, jamais des termes d'une somme. "
            "Et enfin, garder toutes les restrictions après simplification. "
            "Voir le même symbole en haut et en bas ne suffit pas. Il faut voir le même facteur."
        )
        with self.narration(narration) as tracker:
            duration = max(tracker.duration, 6.7)
            self.play(Write(summary_title), run_time=0.15 * duration)
            for line in summary:
                self.play(FadeIn(line, shift=RIGHT * 0.18), run_time=0.13 * duration)
            self.play(GrowFromCenter(final_rule), run_time=0.18 * duration)
            self.wait(0.15 * duration)

        self.wait(1.0)

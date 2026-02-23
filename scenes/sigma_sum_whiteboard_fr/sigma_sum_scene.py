from pathlib import Path

from manim import *


class SigmaSommeBoucleFR(Scene):
    """Video blanc-tableau (16:9) sur la somme sigma avec un exemple concret."""

    def _subtitle_box(self, text: str) -> VGroup:
        caption = Text(
            text,
            font="Sans",
            color=BLACK,
            font_size=30,
            line_spacing=0.9,
        )
        max_width = config.frame_width - 1.0
        if caption.width > max_width:
            caption.scale_to_fit_width(max_width)

        panel = RoundedRectangle(
            corner_radius=0.08,
            width=caption.width + 0.5,
            height=caption.height + 0.3,
            stroke_color=GRAY_B,
            stroke_width=1,
        )
        panel.set_fill(WHITE, opacity=0.95)
        caption.move_to(panel.get_center())

        group = VGroup(panel, caption)
        group.to_edge(DOWN, buff=0.2)
        return group

    def _show_caption(self, text: str, duration: float) -> VGroup:
        self.add_subcaption(text.replace("\n", " "), duration=duration)
        box = self._subtitle_box(text)
        self.play(FadeIn(box), run_time=0.2)
        return box

    def _hide_caption(self, box: VGroup) -> None:
        self.play(FadeOut(box), run_time=0.2)

    def construct(self):
        self.camera.background_color = WHITE

        # Optional narration track (recorded voice, no music).
        audio_candidates = [
            Path(__file__).parent / "assets" / "voix_off_fr.wav",
            Path(__file__).parent / "assets" / "voix_off_fr.mp3",
            Path(__file__).parent / "assets" / "voiceover_fr.wav",
            Path(__file__).parent / "assets" / "voiceover_fr.mp3",
        ]
        for candidate in audio_candidates:
            if candidate.exists():
                self.add_sound(str(candidate), time_offset=0)
                break

        # -------------------------
        # SCENE 1 (0s - 10s)
        # -------------------------
        sigma_tex = MathTex(r"\sum_{i=0}^{n} f(i)", color=BLACK).scale(1.9)
        sigma_tex.move_to(UP * 0.5)

        caption_1 = self._show_caption(
            "On veut comprendre cette écriture : somme de i égal zéro à n de f(i).\n"
            "L'idée est simple : on additionne les valeurs f(i) de 0 jusqu'à n.",
            duration=9.6,
        )

        self.play(Write(sigma_tex), run_time=3.2)

        i0_part = sigma_tex.get_part_by_tex("i=0")
        n_part = sigma_tex.get_part_by_tex("n")
        fi_part = sigma_tex.get_part_by_tex("f(i)")

        underline_i0 = Underline(i0_part, color=BLACK, buff=0.08)
        underline_n = Underline(n_part, color=BLACK, buff=0.08)
        underline_fi = Underline(fi_part, color=BLACK, buff=0.08)

        self.play(
            LaggedStart(
                Create(underline_i0),
                Create(underline_n),
                Create(underline_fi),
                lag_ratio=0.3,
            ),
            run_time=2.2,
        )
        self.wait(4.2)
        self._hide_caption(caption_1)

        # -------------------------
        # SCENE 2 (10s - 30s)
        # -------------------------
        expanded = MathTex(
            r"f(0)", "+", r"f(1)", "+", r"f(2)", "+", r"\cdots", "+", r"f(n)",
            color=BLACK,
        ).scale(1.45)
        expanded.next_to(sigma_tex, DOWN, buff=1.0)

        same_arrow = Arrow(
            sigma_tex.get_bottom() + DOWN * 0.15,
            expanded.get_top() + UP * 0.15,
            color=GRAY_C,
            stroke_width=2,
            tip_length=0.18,
        )

        caption_2 = self._show_caption(
            "Concrètement, c'est la même chose que d'écrire : f(0) + f(1) + f(2) + ... + f(n).\n"
            "Le symbole Sigma est juste une écriture compacte d'une longue addition.",
            duration=19.6,
        )

        self.play(
            LaggedStart(*[Write(part) for part in expanded], lag_ratio=0.2),
            run_time=7.5,
        )
        self.play(GrowArrow(same_arrow), run_time=1.4)
        self.play(
            Indicate(sigma_tex, color=GRAY_D, scale_factor=1.02),
            Indicate(expanded, color=GRAY_D, scale_factor=1.02),
            run_time=1.8,
        )
        self.wait(8.7)
        self._hide_caption(caption_2)

        # -------------------------
        # SCENE 3 (30s - 60s)
        # -------------------------
        example_sigma = MathTex(r"\sum_{i=0}^{4}(2i+1)", color=BLACK).scale(1.8)
        example_sigma.move_to(UP * 1.7)

        developed = MathTex(
            r"=(2\cdot 0+1)+(2\cdot 1+1)+(2\cdot 2+1)+(2\cdot 3+1)+(2\cdot 4+1)",
            color=BLACK,
        ).scale(0.95)
        if developed.width > config.frame_width - 1.2:
            developed.scale_to_fit_width(config.frame_width - 1.2)
        developed.next_to(example_sigma, DOWN, buff=0.75)

        simplified = MathTex(r"=1+3+5+7+9", color=BLACK).scale(1.5)
        simplified.next_to(developed, DOWN, buff=0.8)

        caption_3 = self._show_caption(
            "Prenons un exemple : somme de i égal zéro à 4 de 2i + 1.\n"
            "On remplace i par 0, 1, 2, 3 et 4, puis on obtient 1 + 3 + 5 + 7 + 9.",
            duration=29.6,
        )

        self.play(
            FadeOut(expanded),
            FadeOut(same_arrow),
            FadeOut(underline_i0),
            FadeOut(underline_n),
            FadeOut(underline_fi),
            Transform(sigma_tex, example_sigma),
            run_time=2.2,
        )
        self.play(Write(developed), run_time=7.0)
        self.play(Write(simplified), run_time=3.0)
        self.play(Indicate(simplified, color=GRAY_D), run_time=1.2)
        self.wait(16.0)
        self._hide_caption(caption_3)

        # -------------------------
        # SCENE 4 (60s - 80s)
        # -------------------------
        caption_4 = self._show_caption(
            "Ensuite, on additionne pas à pas : 1, puis 4, puis 9, puis 16, puis 25.\n"
            "Le total final est 25.",
            duration=19.6,
        )

        table = MathTable(
            [
                ["0", "1", "1"],
                ["1", "3", "4"],
                ["2", "5", "9"],
                ["3", "7", "16"],
                ["4", "9", "25"],
            ],
            col_labels=[MathTex("i"), MathTex("2i+1"), MathTex(r"total")],
            include_outer_lines=True,
            line_config={"stroke_color": BLACK, "stroke_width": 1.2},
        ).scale(0.82)
        table.set_color(BLACK)
        table.next_to(sigma_tex, DOWN, buff=0.6)

        sum_result = MathTex(r"\sum_{i=0}^{4}(2i+1)=25", color=BLACK).scale(1.35)
        sum_result.next_to(table, DOWN, buff=0.7)

        self.play(FadeOut(developed), FadeOut(simplified), run_time=0.9)
        self.play(Create(table), run_time=4.8)

        first_row = VGroup(
            table.get_entries((1, 1)),
            table.get_entries((1, 2)),
            table.get_entries((1, 3)),
        )
        row_highlight = SurroundingRectangle(first_row, color=GRAY_D, stroke_width=2, buff=0.06)
        self.play(Create(row_highlight), run_time=0.8)

        for row_idx in [2, 3, 4, 5]:
            next_row = VGroup(
                table.get_entries((row_idx, 1)),
                table.get_entries((row_idx, 2)),
                table.get_entries((row_idx, 3)),
            )
            next_rect = SurroundingRectangle(next_row, color=GRAY_D, stroke_width=2, buff=0.06)
            self.play(Transform(row_highlight, next_rect), run_time=0.8)

        self.play(Write(sum_result), run_time=1.6)
        self.play(Indicate(sum_result, color=GRAY_D), run_time=0.8)
        self.wait(6.4)
        self._hide_caption(caption_4)

        # -------------------------
        # SCENE 5 (80s - 90s)
        # -------------------------
        caption_5 = self._show_caption(
            "A retenir : Sigma sert à écrire une addition répétée de façon compacte.\n"
            "Dans notre exemple, la somme vaut 25.",
            duration=9.6,
        )

        final_statement = Text(
            "Sigma = addition compacte",
            font="Sans",
            color=BLACK,
            font_size=58,
        )

        generic_identity = MathTex(
            r"\sum_{i=0}^{n} f(i) = f(0)+f(1)+\cdots+f(n)",
            color=BLACK,
        ).scale(1.3)

        example_identity = MathTex(r"\sum_{i=0}^{4}(2i+1)=25", color=BLACK).scale(1.3)

        generic_identity.next_to(final_statement, DOWN, buff=0.65)
        example_identity.next_to(generic_identity, DOWN, buff=0.6)

        generic_sigma = MathTex(r"\sum_{i=0}^{n} f(i)", color=BLACK).scale(1.5)
        generic_sigma.move_to(UP * 2.8)

        self.play(
            FadeOut(table),
            FadeOut(row_highlight),
            FadeOut(sum_result),
            Transform(sigma_tex, generic_sigma),
            run_time=1.2,
        )
        self.play(Write(final_statement), run_time=2.0)
        self.play(Write(generic_identity), run_time=2.0)
        self.play(Write(example_identity), run_time=1.8)
        self.wait(2.4)
        self._hide_caption(caption_5)

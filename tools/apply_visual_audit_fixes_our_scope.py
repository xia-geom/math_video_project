from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}\n--- old ---\n{old}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all(path: str, old: str, new: str, expected: int) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"{path}: expected {expected} matches, found {count}\n--- old ---\n{old}")
    p.write_text(text.replace(old, new), encoding="utf-8")


# P05 — avoid a glyph-scrambling morph between unrelated formulas.
replace_once(
    "scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py",
    '            self.play(Transform(example_formula, general_formula), FadeIn(family_note, shift=0.1 * UP), run_time=0.8)\n            self.wait(0.75)',
    '            self.play(FadeOut(example_formula), run_time=0.25)\n            self.play(FadeIn(general_formula), FadeIn(family_note, shift=0.1 * UP), run_time=0.65)\n            example_formula = general_formula\n            self.wait(0.75)',
)

# P08 — keep the common-domain callout inside the safe frame.
replace_once(
    "scenes/fonctions_et_graphiques_fr/08_operations_sur_les_fonctions_fr/08_operations_sur_les_fonctions_fr_scene.py",
    '''        domain_note = VGroup(\n            Text("domaine commun :", font_size=22),\n            MathTex(r"x\\in\\operatorname{Dom}(f)\\cap\\operatorname{Dom}(g)").scale(0.68),\n        ).arrange(RIGHT, buff=0.12)\n        domain_box = SurroundingRectangle(\n            domain_note,\n            color=C_G,\n            buff=0.14,\n            stroke_width=2.2,\n        )\n        domain_group = VGroup(domain_box, domain_note)\n        domain_group.next_to(formula_inputs, RIGHT, buff=0.42)''',
    '''        domain_note = VGroup(\n            Text("domaine commun :", font_size=21),\n            MathTex(r"x\\in\\operatorname{Dom}(f)\\cap\\operatorname{Dom}(g)").scale(0.62),\n        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)\n        domain_box = SurroundingRectangle(\n            domain_note,\n            color=C_G,\n            buff=0.14,\n            stroke_width=2.2,\n        )\n        domain_group = VGroup(domain_box, domain_note)\n        domain_group.to_edge(RIGHT, buff=0.38)\n        domain_group.align_to(formula_inputs, UP)''',
)

# P10 — preserve the layout validator, but give the algebra columns enough separation.
replace_once(
    "scenes/fonctions_et_graphiques_fr/10_fonction_reciproque_fr/10_fonction_reciproque_fr_scene.py",
    '''        equations = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.52, aligned_edge=LEFT)\n        equations.move_to(LEFT * 3.1 + DOWN * 0.5)\n\n        step1_note = Text("soustraire 1", font_size=25, color=accent)\n        step1_note.next_to(eq2, RIGHT, buff=0.55)\n        step2_note = Text("diviser par 2", font_size=25, color=accent)\n        step2_note.next_to(eq3, RIGHT, buff=0.55)\n\n        final_inverse = MathTex(\n            r"f^{-1}(x)=\\frac{x-1}{2}",\n            font_size=45,\n            color=inverse_color,\n        )\n        final_inverse.move_to(RIGHT * 3.25 + DOWN * 0.35)''',
    '''        equations = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.52, aligned_edge=LEFT)\n        equations.move_to(LEFT * 3.6 + DOWN * 0.5)\n\n        step1_note = Text("soustraire 1", font_size=20, color=accent)\n        step1_note.next_to(eq2, RIGHT, buff=0.25)\n        step2_note = Text("diviser par 2", font_size=20, color=accent)\n        step2_note.next_to(eq3, RIGHT, buff=0.25)\n\n        final_inverse = MathTex(\n            r"f^{-1}(x)=\\frac{x-1}{2}",\n            font_size=40,\n            color=inverse_color,\n        )\n        final_inverse.move_to(RIGHT * 3.65 + DOWN * 0.35)''',
)
replace_once(
    "scenes/fonctions_et_graphiques_fr/10_fonction_reciproque_fr/10_fonction_reciproque_fr_scene.py",
    '''        rename_note = Text(\n            "ancienne sortie → nouvelle entrée",\n            font_size=25,\n            color=inverse_color,\n        ).next_to(final_box, DOWN, buff=0.28)''',
    '''        rename_note = Text(\n            "ancienne sortie → nouvelle entrée",\n            font_size=21,\n            color=inverse_color,\n        ).next_to(final_box, DOWN, buff=0.24)''',
)

# P11 — do not morph two unrelated calculation blocks through one another.
replace_once(
    "scenes/fonctions_et_graphiques_fr/11_racines_et_hauteur_zero_fr/11_racines_et_hauteur_zero_fr_scene.py",
    '            self.play(ReplacementTransform(calc_two, calc_minus), run_time=0.75)',
    '            self.play(FadeOut(calc_two), FadeIn(calc_minus, shift=UP * 0.08), run_time=0.75)',
)

# P12 — fit the title safely, and replace value-label morphs by clean fades.
replace_once(
    "scenes/fonctions_et_graphiques_fr/12_multiplicite_des_racines_fr/12_multiplicite_des_racines_fr_scene.py",
    '''        title = Text("Pourquoi une racine traverse ou touche l’axe ?", font_size=43)\n        title.to_edge(UP, buff=0.22)''',
    '''        title = Text("Pourquoi une racine traverse ou touche l’axe ?", font_size=39)\n        if title.width > config.frame_width - 0.8:\n            title.scale_to_fit_width(config.frame_width - 0.8)\n        title.to_edge(UP, buff=0.30)''',
)
replace_all(
    "scenes/fonctions_et_graphiques_fr/12_multiplicite_des_racines_fr/12_multiplicite_des_racines_fr_scene.py",
    'ReplacementTransform(value_left_x, value_zero_x)',
    'FadeOut(value_left_x), FadeIn(value_zero_x)',
    1,
)
replace_all(
    "scenes/fonctions_et_graphiques_fr/12_multiplicite_des_racines_fr/12_multiplicite_des_racines_fr_scene.py",
    'ReplacementTransform(value_zero_x, value_right_x)',
    'FadeOut(value_zero_x), FadeIn(value_right_x)',
    1,
)
replace_all(
    "scenes/fonctions_et_graphiques_fr/12_multiplicite_des_racines_fr/12_multiplicite_des_racines_fr_scene.py",
    'ReplacementTransform(value_left_x2, value_zero_x2)',
    'FadeOut(value_left_x2), FadeIn(value_zero_x2)',
    1,
)
replace_all(
    "scenes/fonctions_et_graphiques_fr/12_multiplicite_des_racines_fr/12_multiplicite_des_racines_fr_scene.py",
    'ReplacementTransform(value_zero_x2, value_right_x2)',
    'FadeOut(value_zero_x2), FadeIn(value_right_x2)',
    1,
)

# P15 — use the same safe-width rule as the other headings.
replace_once(
    "scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py",
    '''        title = Text(\n            "Dénombrement 1 — principe fondamental",\n            font_size=45,\n            weight=SEMIBOLD,\n        )''',
    '''        title = Text(\n            "Dénombrement 1 — principe fondamental",\n            font_size=39,\n            weight=SEMIBOLD,\n        )\n        if title.width > 12.0:\n            title.scale_to_fit_width(12.0)''',
)

# P16 — all specific→general formula changes use a readable fade transition.
replace_all(
    "scenes/probabilites_fr/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr_scene.py",
    'ReplacementTransform(specific, general)',
    'FadeOut(specific), FadeIn(general, shift=0.08 * UP)',
    3,
)

# P17 — central subtitle helper now avoids unrelated-text morphing everywhere.
replace_once(
    "scenes/probabilites_fr/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr_scene.py",
    '''    def replace_subtitle(self, current: Mobject, text: str) -> Text:\n        new = self.new_subtitle(text)\n        self.play(ReplacementTransform(current, new), run_time=0.55)\n        return new''',
    '''    def replace_subtitle(self, current: Mobject, text: str) -> Text:\n        new = self.new_subtitle(text)\n        self.play(FadeOut(current), FadeIn(new), run_time=0.55)\n        return new''',
)

# P18 — reduce and anchor the explanatory panel to a safe right margin.
replace_once(
    "scenes/vecteurs_fr/18_deplacement_et_composantes_fr/18_deplacement_et_composantes_fr_scene.py",
    '''        reason = Text(\n            "même direction · même sens · même longueur",\n            font_size=24,\n        ).next_to(displacement, DOWN, buff=0.35)\n        reason_box = SurroundingRectangle(\n            VGroup(displacement, reason),\n            color=ACCENT,\n            buff=0.22,\n            stroke_width=2.3,\n        )''',
    '''        reason = Text(\n            "même direction · même sens · même longueur",\n            font_size=21,\n        ).next_to(displacement, DOWN, buff=0.28)\n        reason_box = SurroundingRectangle(\n            VGroup(displacement, reason),\n            color=ACCENT,\n            buff=0.20,\n            stroke_width=2.3,\n        )\n        VGroup(displacement, reason, reason_box).to_edge(RIGHT, buff=0.45)''',
)

print("Applied Phase 2 visual fixes for P05, P08, P10, P11, P12, P15, P16, P17, P18.")

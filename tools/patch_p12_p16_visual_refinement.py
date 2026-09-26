from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}\n{old}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# P12: keep the graph morph, but do not morph unrelated formulas through black glyph clusters.
replace_once(
    "scenes/fonctions_et_graphiques_fr/13_multiplicite_des_racines_fr/13_multiplicite_des_racines_fr_scene.py",
    '            self.play(ReplacementTransform(formula_x, formula_x2), ReplacementTransform(graph_x, graph_x2), run_time=1)',
    '            self.play(FadeOut(formula_x), ReplacementTransform(graph_x, graph_x2), run_time=0.5)\n            self.play(FadeIn(formula_x2), run_time=0.5)',
)

# P16: specific-to-general formula cards must never coexist in the same frame.
replace_once(
    "scenes/probabilites_fr/18_permutation_arrangement_combinaison_fr/18_permutation_arrangement_combinaison_fr_scene.py",
    '''            self.play(\n                FadeOut(candidates),\n                FadeOut(slots),\n                FadeOut(choice_numbers),\n                FadeOut(choice_notes),\n                FadeOut(specific), FadeIn(general, shift=0.08 * UP),\n                run_time=1.0,\n            )''',
    '''            self.play(\n                FadeOut(candidates),\n                FadeOut(slots),\n                FadeOut(choice_numbers),\n                FadeOut(choice_notes),\n                FadeOut(specific),\n                run_time=0.55,\n            )\n            self.play(FadeIn(general, shift=0.08 * UP), run_time=0.55)''',
)
replace_once(
    "scenes/probabilites_fr/18_permutation_arrangement_combinaison_fr/18_permutation_arrangement_combinaison_fr_scene.py",
    '            self.play(FadeOut(specific), FadeIn(general, shift=0.08 * UP), run_time=0.95)',
    '            self.play(FadeOut(specific), run_time=0.45)\n            self.play(FadeIn(general, shift=0.08 * UP), run_time=0.5)',
)
replace_once(
    "scenes/probabilites_fr/18_permutation_arrangement_combinaison_fr/18_permutation_arrangement_combinaison_fr_scene.py",
    '''            self.play(\n                FadeOut(cards),\n                FadeOut(slots),\n                FadeOut(placed),\n                FadeOut(choice_numbers),\n                FadeOut(specific), FadeIn(general, shift=0.08 * UP),\n                run_time=0.95,\n            )''',
    '''            self.play(\n                FadeOut(cards),\n                FadeOut(slots),\n                FadeOut(placed),\n                FadeOut(choice_numbers),\n                FadeOut(specific),\n                run_time=0.5,\n            )\n            self.play(FadeIn(general, shift=0.08 * UP), run_time=0.5)''',
)

print("Patched P12 formula transition and P16 sequential formula fades.")

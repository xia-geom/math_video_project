from pathlib import Path

path = Path("scenes/fonctions_et_graphiques_fr/11_racines_et_hauteur_zero_fr/11_racines_et_hauteur_zero_fr_scene.py")
text = path.read_text(encoding="utf-8")
old = '            self.play(ReplacementTransform(product_formula, final_slogan), run_time=0.7)'
new = '            self.play(FadeOut(product_formula), FadeIn(final_slogan), run_time=0.7)'
if text.count(old) != 1:
    raise RuntimeError(f"Expected exactly one P11 final transition, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Patched P11 final summary transition.")

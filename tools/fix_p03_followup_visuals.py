from pathlib import Path

path = Path('scenes/algebre_et_polynomes_fr/03_racine_carree_et_valeur_absolue_fr/03_racine_carree_et_valeur_absolue_fr_scene.py')
text = path.read_text(encoding='utf-8')

old = '''        conjecture_group.move_to(DOWN * 1.82)\n'''
new = '''        # Keep the conjecture card well below the counterexample braces/labels.\n        conjecture_group.move_to(DOWN * 2.42)\n'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise RuntimeError('P03 conjecture position anchor not found')

old = '''            self.play(\n                Transform(case_label, negative_label),\n                FadeOut(observation),\n                TransformMatchingTex(calculation, negative_calculation),\n                run_time=1.0,\n            )\n            self.wait(0.8)\n'''
new = '''            # These are different examples, not corresponding glyph-by-glyph objects.\n            # Clear the first example before introducing the negative one so the\n            # intermediate frames never contain overprinted formulas/text.\n            self.play(\n                FadeOut(case_label),\n                FadeOut(calculation),\n                FadeOut(observation),\n                run_time=0.45,\n            )\n            self.play(\n                FadeIn(negative_label),\n                FadeIn(negative_calculation),\n                run_time=0.55,\n            )\n            case_label = negative_label\n            calculation = negative_calculation\n            self.wait(0.8)\n'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise RuntimeError('P03 negative-example transition anchor not found')

path.write_text(text, encoding='utf-8')
print('P03 follow-up visual fixes applied')

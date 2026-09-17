from pathlib import Path

path = Path('scenes/notations_fr/18_notation_sigma_fr/18_notation_sigma_fr_scene.py')
text = path.read_text(encoding='utf-8')

old = '''        with self.narration(SCRIPT["result"]):\n            self.play(\n                FadeOut(VGroup(produced_values, total_title)),\n                Transform(running_total, result),\n                run_time=1.0,\n            )\n            self.play(Create(result_box), run_time=0.65)\n            self.wait(1.1)\n\n        self.play(\n            FadeOut(VGroup(self.sigma_example, running_total, result_box)),\n            run_time=0.8,\n        )\n'''
new = '''        with self.narration(SCRIPT["result"]):\n            # The running-total equation and the compact sigma statement are\n            # semantically related but not glyph-corresponding.  Replace them\n            # sequentially so no unreadable intermediate formula is shown.\n            self.play(\n                FadeOut(VGroup(produced_values, total_title, running_total)),\n                run_time=0.45,\n            )\n            self.play(FadeIn(result), run_time=0.55)\n            self.play(Create(result_box), run_time=0.65)\n            self.wait(1.1)\n\n        self.play(\n            FadeOut(VGroup(self.sigma_example, result, result_box)),\n            run_time=0.8,\n        )\n'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise RuntimeError('P27 result transition block not found')

old = '''        with self.narration(SCRIPT["correct_expansion"]):\n            self.play(\n                FadeOut(strike),\n                Transform(wrong, correct),\n                Transform(wrong_label, correct_label),\n                run_time=1.1,\n            )\n            self.wait(1.2)\n\n        self.play(\n            FadeOut(VGroup(index_title, index_motion, counter_statement, wrong, wrong_label)),\n            run_time=0.8,\n        )\n'''
new = '''        with self.narration(SCRIPT["correct_expansion"]):\n            # Do not morph a crossed-out false statement into a different\n            # expanded formula; clear the error before showing the correction.\n            self.play(\n                FadeOut(VGroup(strike, wrong, wrong_label)),\n                run_time=0.45,\n            )\n            self.play(\n                FadeIn(correct),\n                FadeIn(correct_label),\n                run_time=0.55,\n            )\n            self.wait(1.2)\n\n        self.play(\n            FadeOut(VGroup(index_title, index_motion, counter_statement, correct, correct_label)),\n            run_time=0.8,\n        )\n'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise RuntimeError('P27 false-to-correct transition block not found')

path.write_text(text, encoding='utf-8')
print('P27 follow-up visual fixes applied')

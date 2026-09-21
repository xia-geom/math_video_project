from pathlib import Path

path = Path("scenes/probabilites_fr/18_permutation_arrangement_combinaison_fr/18_permutation_arrangement_combinaison_fr_scene.py")
text = path.read_text(encoding="utf-8")
old1 = '''            self.play(\n                Transform(scenario, second_scenario),\n                FadeOut(answer),\n                FadeOut(reason),\n                FadeOut(notation),\n                run_time=0.75,\n            )\n            self.wait(1.2)'''
new1 = '''            self.play(\n                FadeOut(scenario),\n                FadeOut(answer),\n                FadeOut(reason),\n                FadeOut(notation),\n                run_time=0.45,\n            )\n            self.play(FadeIn(second_scenario), run_time=0.30)\n            scenario = second_scenario\n            self.wait(1.2)'''
old2 = '''            self.play(\n                Transform(scenario, third_scenario),\n                FadeOut(answer),\n                FadeOut(reason),\n                FadeOut(notation),\n                run_time=0.75,\n            )\n            self.wait(1.2)'''
new2 = '''            self.play(\n                FadeOut(scenario),\n                FadeOut(answer),\n                FadeOut(reason),\n                FadeOut(notation),\n                run_time=0.45,\n            )\n            self.play(FadeIn(third_scenario), run_time=0.30)\n            scenario = third_scenario\n            self.wait(1.2)'''
for old, new, label in ((old1, new1, "first quiz change"), (old2, new2, "second quiz change")):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label}, found {count}")
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
print("Patched P16 quiz scenario replacements to sequential fades.")

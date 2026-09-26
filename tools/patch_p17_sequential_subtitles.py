from pathlib import Path

path = Path("scenes/probabilites_fr/19_repetitions_en_denombrement_fr/19_repetitions_en_denombrement_fr_scene.py")
text = path.read_text(encoding="utf-8")
old = '''    def replace_subtitle(self, current: Mobject, text: str) -> Text:\n        new = self.new_subtitle(text)\n        self.play(FadeOut(current), FadeIn(new), run_time=0.55)\n        return new'''
new = '''    def replace_subtitle(self, current: Mobject, text: str) -> Text:\n        new = self.new_subtitle(text)\n        self.play(FadeOut(current), run_time=0.25)\n        self.play(FadeIn(new), run_time=0.30)\n        return new'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one P17 subtitle helper, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Patched P17 subtitle transitions to sequential fades.")

from pathlib import Path


def patch(rel: str, old: str, new: str, label: str) -> None:
    path = Path(rel)
    text = path.read_text(encoding='utf-8')
    if new in text:
        print(f'{label}: already applied')
        return
    if old not in text:
        raise RuntimeError(f'{label}: source block not found')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')
    print(f'{label}: applied')


# E01 — the final reminder overflows both frame edges.
patch(
    'scenes/erreurs_frequentes_fr/38_implication_et_equivalence_fr/38_implication_et_equivalence_fr_scene.py',
    '''        diagnostic = Text(\n            "Avant de retourner une flèche, cherchez un contre-exemple.",\n            font_size=32,\n            color=ACCENT,\n            weight="SEMIBOLD",\n        )\n        diagnostic.to_edge(DOWN, buff=0.45)\n''',
    '''        diagnostic = Text(\n            "Avant de retourner une flèche, cherchez un contre-exemple.",\n            font_size=32,\n            color=ACCENT,\n            weight="SEMIBOLD",\n        )\n        if diagnostic.width > config.frame_width - 1.0:\n            diagnostic.scale_to_fit_width(config.frame_width - 1.0)\n        diagnostic.to_edge(DOWN, buff=0.45)\n''',
    'E01 final reminder safe width',
)

# E03 — the prior green image caption remains underneath the new red conclusion.
patch(
    'scenes/erreurs_frequentes_fr/40_egalite_de_fonctions_fr/40_egalite_de_fonctions_fr_scene.py',
    '''        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):\n            self.play(Write(test), Create(test_box), run_time=0.9)\n            self.wait(0.55)\n            self.play(FadeIn(conclusion, shift=UP * 0.12), run_time=0.55)\n            self.wait(1.0)\n''',
    '''        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):\n            # Clear the previous image-only takeaway before introducing the\n            # stronger counterexample conclusion; otherwise the two lines\n            # occupy the same vertical band.\n            self.play(FadeOut(same_image), run_time=0.30)\n            self.play(Write(test), Create(test_box), run_time=0.9)\n            self.wait(0.55)\n            self.play(FadeIn(conclusion, shift=UP * 0.12), run_time=0.55)\n            self.wait(1.0)\n''',
    'E03 image/conclusion collision',
)

# E04 — two long explanatory lines overflow the frame.
patch(
    'scenes/erreurs_frequentes_fr/41_solutions_parasites_fr/41_solutions_parasites_fr_scene.py',
    '''        implication_caption = Text(\n            "Élever au carré donne une implication, pas toujours une équivalence.",\n            font_size=31,\n            color=ACCENT,\n        )\n        implication_caption.to_edge(DOWN, buff=0.42)\n''',
    '''        implication_caption = Text(\n            "Élever au carré donne une implication, pas toujours une équivalence.",\n            font_size=31,\n            color=ACCENT,\n        )\n        if implication_caption.width > config.frame_width - 1.0:\n            implication_caption.scale_to_fit_width(config.frame_width - 1.0)\n        implication_caption.to_edge(DOWN, buff=0.42)\n''',
    'E04 implication caption safe width',
)
patch(
    'scenes/erreurs_frequentes_fr/41_solutions_parasites_fr/41_solutions_parasites_fr_scene.py',
    '''        note = Text(\n            "Le carré n'est pas faux : il oublie simplement le signe.",\n            font_size=34,\n            color=ACCENT,\n            weight="SEMIBOLD",\n        )\n        note.move_to(DOWN * 1.15)\n''',
    '''        note = Text(\n            "Le carré n'est pas faux : il oublie simplement le signe.",\n            font_size=34,\n            color=ACCENT,\n            weight="SEMIBOLD",\n        )\n        if note.width > config.frame_width - 1.0:\n            note.scale_to_fit_width(config.frame_width - 1.0)\n        note.move_to(DOWN * 1.15)\n''',
    'E04 final note safe width',
)

print('common-error follow-up visual fixes complete')

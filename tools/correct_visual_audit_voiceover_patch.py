from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch(rel: str, service_expr: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")

    bad_helper = (
        '        try:\n'
        '            self._setup_voiceover()\n'
        '        except Exception as exc:\n'
    )
    good_helper = (
        '        try:\n'
        f'            self.set_speech_service({service_expr})\n'
        '        except Exception as exc:\n'
    )
    if bad_helper in text:
        text = text.replace(bad_helper, good_helper, 1)

    bad_construct = f'    def construct(self) -> None:\n        self.set_speech_service({service_expr})\n'
    good_construct = '    def construct(self) -> None:\n        self._setup_voiceover()\n'
    if bad_construct in text:
        text = text.replace(bad_construct, good_construct, 1)

    if bad_helper in text or bad_construct in text:
        raise RuntimeError(f"voiceover regression still present in {rel}")
    if good_helper not in text or good_construct not in text:
        raise RuntimeError(f"expected corrected voiceover blocks missing in {rel}")

    path.write_text(text, encoding="utf-8")
    print(f"verified/corrected {rel}")


patch(
    'scenes/algebre_et_polynomes_fr/03_racine_carree_et_valeur_absolue_fr/03_racine_carree_et_valeur_absolue_fr_scene.py',
    'AzureService(voice=VOICE_ID)',
)
patch(
    'scenes/erreurs_frequentes_fr/38_implication_et_equivalence_fr/38_implication_et_equivalence_fr_scene.py',
    'AzureService(voice=VOICE_ID)',
)
patch(
    'scenes/erreurs_frequentes_fr/40_egalite_de_fonctions_fr/40_egalite_de_fonctions_fr_scene.py',
    'AzureService(voice=VOICE_ID)',
)
patch(
    'scenes/erreurs_frequentes_fr/41_solutions_parasites_fr/41_solutions_parasites_fr_scene.py',
    'AzureService(**azure_service_kwargs())',
)

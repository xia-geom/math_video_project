"""Second, scoped correction pass from the measured teaching-layout audit."""
from __future__ import annotations

from migrate import CHANGED, ROOT, replace, scene


def main():
    p = scene('01_variables_et_polynomes_fr')
    replace(p, 'curve_label = MathTex(POLY_LABEL_TEX, font_size=32).next_to(axes, UP, buff=0.25)',
            'curve_label = MathTex(POLY_LABEL_TEX, font_size=32).move_to([-3.0, 2.6, 0])')
    p = scene('08_operations_sur_les_fonctions_fr')
    replace(p, 'Text("réflexion par rapport à l’axe des x", font_size=25, color=C_NEG)',
            'Text("Symétrie : axe des x", font_size=28, color=C_NEG)')
    replace(p, 'mirror_label.next_to(reflect_formula, RIGHT, buff=0.38)',
            'mirror_label.to_edge(LEFT, buff=0.6).shift(UP * 2.55)')
    replace(p, 'r"g(-2)=-\\frac12\\;\\longleftrightarrow\\;-g(-2)=\\frac12").scale(0.62)',
            'r"\\begin{gathered}g(-2)=-\\frac12\\\\-g(-2)=\\frac12\\end{gathered}", font_size=34)')
    replace(p, 'r"g(1)=1\\;\\longleftrightarrow\\;-g(1)=-1").scale(0.62)',
            'r"\\begin{gathered}g(1)=1\\\\-g(1)=-1\\end{gathered}", font_size=34)')
    replace(p, 'pair_labels[0].next_to(neg_pair_points[0], LEFT, buff=0.18)',
            'pair_labels[0].move_to([-5.2, -1.4, 0])')
    replace(p, 'pair_labels[1].next_to(neg_pair_points[1], RIGHT, buff=0.18)',
            'pair_labels[1].move_to([5.2, -1.4, 0])')
    p = scene('12_multiplicite_des_racines_fr')
    replace(p, 'y_range=[-5, 4, 1],\n            unit_size=0.62,\n            font_size=19,',
            'y_range=[-5, 4, 1],\n            unit_size=0.50,\n            font_size=22,')
    replace(p, 'product_formula.move_to(formula_position)',
            'product_formula.move_to(formula_position + DOWN * 0.35)')
    replace(scene('03_egalite_de_fonctions_fr'),
            "self.new_page('Le critère complet — convention du cours'",
            "self.new_page('Le critère complet'")
    replace('tools/teaching_layout.py', '        import os\n        self.silent',
            "        import os\n        from pathlib import Path\n\n        from dotenv import load_dotenv\n\n        load_dotenv(Path(__file__).resolve().parents[1] / '.env', override=False)\n        self.silent")
    replace('tools/teaching_voiceover.py', 'teaching_azure_pcm_anchors_v1', 'teaching_azure_pcm_anchors_v2')
    replace('tools/teaching_voiceover.py',
            "filename = path or self.get_audio_basename(data) + '.wav'\n        audio.export(directory / filename, format='wav')",
            "# manim-voiceover 0.3.7 measures duration with mutagen.MP3.\n        # Join in PCM first, then encode one gapless MP3 for its tracker.\n        filename = path or self.get_audio_basename(data) + '.mp3'\n        audio.export(directory / filename, format='mp3', bitrate='192k')")
    replace('tests/test_teaching_revision.py', '    service.get_cached_result = lambda *args: None',
            '    service.global_speed = 1.0\n    service._whisper_model = None\n    service.audio_callback = lambda *args, **kwargs: None\n    service.get_cached_result = lambda *args: None')
    replace('tests/test_teaching_revision.py', '    data = service.generate_from_text(text, cache_dir=tmp_path)',
            '    # Exercise the real upstream wrapper: final_audio and cache metadata.\n    data = service._wrap_generate_from_text(text)')
    replace('tests/test_teaching_revision.py', '    assert tracker.duration == pytest.approx(2.5)',
            "    # MP3 metadata may include codec-padding frames; decoded PCM is exact.\n    assert 2.5 <= tracker.duration < 2.56\n    decoded = AudioSegment.from_file(tmp_path / data['final_audio'])\n    assert int(decoded.frame_count()) == 120000")
    replace('scripts/teaching_revision/review.py', '    states, seen, kept = [], set(), []',
            "    states, seen, kept = [], set(), []\n    frame_limit = 100 if entry['track'] == 'errors' and entry['order'] in (2, 3) else 8")
    replace('scripts/teaching_revision/review.py', 'len(kept) < 8', 'len(kept) < frame_limit')
    replace('scripts/teaching_revision/review.py', 'len(kept) >= 8', 'len(kept) >= frame_limit')
    replace('README.md', 'Azure-narrated scenes use **`fr-CA-SylvieNeural`** as the standard voice.',
            'Teaching scenes now use the existing **`MAI-Voice-2`** profile at **`-3%`**, through `tools/teaching_voiceover.py`, as their standard voice.')
    replace('README.md', 'To test Microsoft\'s public-preview MAI-Voice-2 model, use the friendly',
            'To explicitly select the shared MAI teaching profile, use the friendly')
    replace('README.md', '| Female — series default |', '| Legacy profile; explicit override |')
    replace('README.md', '## Voiceover (Azure)',
            '## Teaching production standard\n\nSee [docs/TEACHING_STANDARD.md](docs/TEACHING_STANDARD.md) for legible panels, sequential explanations, the MAI teaching profile, measured bookmark timing, and the single UQAM opening.\n\n## Voiceover (Azure)')
    replace('AGENT.md', '## 1. Goal and technology',
            'For teaching lessons, [docs/TEACHING_STANDARD.md](docs/TEACHING_STANDARD.md) defines the current layout, voice and opening contracts and supersedes older adapter examples below.\n\n## 1. Goal and technology')
    replace('AGENT.md', 'self.set_speech_service(AzureService(voice=VOICE_ID))',
            'from tools.teaching_voiceover import TeachingAzureService\n\nself.set_speech_service(TeachingAzureService())')
    architecture = ROOT / 'ARCHITECTURE.md'
    addition = '''\n## 11. Teaching-series layout, voice and opening standard\n\nThe 27 curriculum and six common-error lessons follow\n[docs/TEACHING_STANDARD.md](docs/TEACHING_STANDARD.md). The two rebuilt error\nlessons use `tools/teaching_layout.py`: boxes grow to contain legible content,\nand pages that cannot fit require reorganization rather than automatic shrinking.\n\n`tools/teaching_voiceover.py` delegates synthesis to the existing Azure adapter\nand `tools/tts.py`. MAI-Voice-2 at the existing -3% teaching rate is now the\ndefault. Bookmarked MAI passages use measured PCM-fragment boundaries and\na tracker-compatible MP3, not estimated word timings. Promotional +2% overrides\nand the selectable prerecorded Sigma track remain separate.\n\n`tools/branding.py` owns the single 1.5-second official-logo opening. Every\nmanifest-listed lesson calls it once; the standalone identity animation is\nnot an additional embedded bumper.\n\n`scripts/teaching_revision/review.py` measures stable construction endpoints;\n`validate.py` also renders the two rebuilt lessons. Their tests and encoded\nreview evidence do not substitute for full listening or publication approval.\nThe migration scripts are historical change tools, not render-time dependencies.\n'''
    if '## 11. Teaching-series layout' not in architecture.read_text():
        architecture.write_text(architecture.read_text() + addition)
        CHANGED.add('ARCHITECTURE.md')
    for path in sorted(CHANGED):
        print(path)


if __name__ == '__main__':
    main()

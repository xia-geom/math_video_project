"""Focused repeatable source migration for PR #5; no promotion or book edits."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHANGED = set()


def replace(path, before, after, count=1):
    path = ROOT / path if isinstance(path, str) else path
    source = path.read_text()
    if after in source:
        return
    found = source.count(before)
    if found != count:
        raise ValueError(f'{path}: expected {count} copies of {before[:80]!r}; found {found}')
    path.write_text(source.replace(before, after), encoding='utf-8')
    CHANGED.add(str(path.relative_to(ROOT)))


def scene(slug):
    found = list((ROOT / 'scenes').glob(f'*/{slug}/{slug}_scene.py'))
    if len(found) != 1:
        raise ValueError(f'Ambiguous scene: {slug}')
    return found[0]


def voice_and_intro():
    import yaml
    entries = yaml.safe_load((ROOT / 'curriculum/programme_principal_fr.yaml').read_text())['entries']
    for entry in entries:
        path = ROOT / entry['scene_file']
        source = original = path.read_text()
        source = source.replace('from manim_voiceover.services.azure import AzureService',
                                'from tools.teaching_voiceover import TeachingAzureService as AzureService')
        lines = source.splitlines(keepends=True)
        offsets = [0]
        for line in lines:
            offsets.append(offsets[-1] + len(line))
        spans = []
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'AzureService':
                for keyword in node.keywords:
                    if keyword.arg == 'global_speed':
                        start = offsets[keyword.lineno-1] + keyword.col_offset
                        end = offsets[keyword.end_lineno-1] + keyword.end_col_offset
                        while start > 0 and source[start-1].isspace():
                            start -= 1
                        if source[start-1] == ',':
                            start -= 1
                        elif source[end:end+1] == ',':
                            end += 1
                        spans.append((start, end))
        for start, end in sorted(spans, reverse=True):
            source = source[:start] + source[end:]
        if 'play_uqam_intro(self)' not in source:
            marker = '        self._setup_voiceover()\n'
            if source.count(marker) != 1:
                raise ValueError(f'Intro insertion point needs review: {path}')
            source = source.replace(marker, marker + '        play_uqam_intro(self)\n')
            position = source.index('\nconfig.background_color')
            source = source[:position] + '\nfrom tools.branding import play_uqam_intro\n' + source[position:]
        ast.parse(source)
        if source != original:
            path.write_text(source)
            CHANGED.add(str(path.relative_to(ROOT)))
    replace('tools/tts.py', 'DEFAULT_VOICE = "fr-CA-SylvieNeural"', 'DEFAULT_VOICE = MAI_VOICE_2')
    replace('tools/tts.py', 'The default voice is fr-CA-SylvieNeural.',
            'The teaching default is MAI-Voice-2, with the existing -3% teaching rate.')
    replace('tools/tts.py', '# Standard fr-CA voices plus the opt-in MAI-Voice-2 test profile.',
            '# MAI teaching standard plus explicit opt-in legacy fr-CA profiles.')
    replace('tools/tts.py', '# female — series default', '# legacy female profile')


def targeted_layout():
    p = scene('02_inequations_nombre_negatif_fr')
    replace(p, ').next_to(inequality_times_2, UP, buff=0.20)', ').next_to(inequality_times_2, DOWN, buff=0.22)')
    replace(p, ').next_to(spatial_reading, UP, buff=0.20)', ').next_to(spatial_reading, DOWN, buff=0.22)')
    replace(p, "Un facteur négatif réfléchit la droite : il inverse l'ordre.",
            'Facteur négatif : réflexion, donc ordre inversé.')
    replace(p, 'width=9.5,\n            height=1.05,', 'width=11.8,\n            height=1.05,')

    p = scene('04_domaine_et_image_fr')
    replace(p, 'self.play(input_token.animate.move_to(machine.get_center()), run_time=0.75)',
            'self.play(FadeOut(machine[1]), run_time=0.25)\n            self.play(input_token.animate.move_to(machine.get_center()), run_time=0.75)')
    replace(p, '            self.play(Write(result), run_time=0.8)',
            '            self.play(FadeIn(machine[1]), run_time=0.3)\n            self.play(Write(result), run_time=0.8)')

    p = scene('06_lire_les_proprietes_d_un_graphe_fr')
    replace(p, '        # Beat 4: NOT even / NOT odd — drop-lines at x=1 and x=-1',
            '        self.play_paced(FadeOut(lbl_vertex), FadeOut(min_lbl), FadeOut(vertex_dot), run_time=0.45)\n\n        # Beat 4: NOT even / NOT odd — drop-lines at x=1 and x=-1')
    replace(p, 'new_label = MathTex(new_tex, font_size=26, color=color).next_to(new_dot, UP, buff=0.1)',
            'new_label = MathTex(new_tex, font_size=28, color=color).next_to(new_dot, DOWN, buff=0.20)')
    replace(p, '                    width=4.9,\n                    height=2.15,',
            '                    width=max(4.9, panel.width + 0.5),\n                    height=max(2.15, panel.height + 0.5),')

    p = scene('08_operations_sur_les_fonctions_fr')
    replace(p, 'label_g.move_to(axes.c2p(1.85, g(1.85) + 0.22))',
            'label_g.move_to(axes.c2p(2.15, g(2.15)) + RIGHT * 0.55)')
    replace(p, 'label_diff.move_to(axes.c2p(-1.8, diff_fg(-1.8) + 0.25))',
            'label_diff.move_to(axes.c2p(-2.15, diff_fg(-2.15)) + LEFT * 0.6)')
    replace(p, 'zero_label = MathTex(r"g(-1)=0\\;:\\;\\text{aucun déplacement}", color=result_color)',
            'zero_label = MathTex(r"g(-1)=0", font_size=36, color=result_color)')
    replace(p, 'zero_label.scale(0.68).next_to(point, RIGHT, buff=0.16)',
            'zero_label.next_to(point, RIGHT, buff=0.3)')
    replace(p, 'result_label.next_to(dot_result, label_side, buff=0.14)',
            'result_label.move_to([4.1, -2.55, 0])')

    p = scene('12_multiplicite_des_racines_fr')
    replace(p, 'product_labels = product_axes.get_axis_labels(MathTex("x"), MathTex("y"))',
            'product_labels = product_axes.get_axis_labels(MathTex("x"), MathTex("y"))\n        product_labels[1].next_to(product_axes.y_axis.get_end(), RIGHT, buff=0.22).shift(DOWN * 0.55)')

    p = scene('13_completer_le_carre_fr')
    replace(p, 'sq.move_to(LEFT * 2.8 + DOWN * 0.3)', 'sq.move_to(LEFT * 2.8 + UP * 0.6)')
    replace(p, 'r"x^2 + 6x + 9 = (x+3)^2",\n            font_size=40, color=GREEN_CUSTOM,',
            'r"\\begin{gathered}x^2 + 6x + 9\\\\=(x+3)^2\\end{gathered}",\n            font_size=40, color=GREEN_CUSTOM,')

    p = scene('16_permutation_arrangement_combinaison_fr')
    replace(p, '            self.wait_until_bookmark("arr_specific_formula")\n',
            '            self.wait_until_bookmark("arr_specific_formula")\n            self.play(FadeOut(choice_notes), FadeOut(choice_numbers), run_time=0.4)\n')
    replace(p, 'condition_text = Text(condition, font_size=25, color=BLACK)',
            'condition_text = Text(condition, font_size=28, color=BLACK)')
    replace(p, '            height=0.95,\n            corner_radius=0.1,',
            '            height=max(1.12, content.height + 0.40),\n            corner_radius=0.1,')
    for before, after in [('ordre oui · r parmi n', 'ordre : oui'), ('ordre non · r parmi n', 'ordre : non'), ('ordre oui · tous les n', 'tous les éléments')]:
        replace(p, before, after)
    replace(p, '            self.wait_until_bookmark("recap_rows")\n',
            '            self.wait_until_bookmark("recap_rows")\n            self.play(FadeOut(definitions), run_time=0.4)\n')
    replace(p, '            self.wait_until_bookmark("recap_final")\n',
            '            self.wait_until_bookmark("recap_final")\n            self.play(FadeOut(rows), run_time=0.4)\n            final_rule.move_to([0, 0, 0])\n')

    p = scene('15_principe_fondamental_du_denombrement_fr')
    for before, after in [('Définir précisément un résultat complet.', 'Définir un résultat.'),
                          ('Découper sa construction en étapes successives.', 'Distinguer les étapes.'),
                          ('Vérifier le nombre de continuations sur chaque branche.', 'Compter les choix à chaque étape.'),
                          ('à chaque étape, le nombre de choix reste uniforme', 'même nombre de choix sur chaque branche')]:
        replace(p, before, after)
    replace(p, '            width=5.75,\n            height=1.65,',
            '            width=max(8.0, product_card.width + 0.7),\n            height=max(2.0, product_card.height + 0.5),')
    replace(p, '            width=5.35,\n            height=1.65,',
            '            width=max(8.0, sum_card.width + 0.7),\n            height=max(2.0, sum_card.height + 0.5),')
    replace(p, '        rules = VGroup(product_group, sum_group).arrange(RIGHT, buff=0.58)\n        rules.to_edge(DOWN, buff=0.38)',
            '        product_group.move_to([0, 0, 0])\n        sum_group.move_to([0, 0, 0])')
    replace(p, '            self.wait_until_bookmark("recap_product")\n',
            '            self.wait_until_bookmark("recap_product")\n            self.play(FadeOut(steps), run_time=0.4)\n')
    replace(p, '            self.wait_until_bookmark("recap_exception")\n',
            '            self.wait_until_bookmark("recap_exception")\n            self.play(FadeOut(product_group), run_time=0.4)\n')

    p = scene('04_solutions_parasites_fr')
    replace(p, 'four_label = MathTex(r"4").next_to(output_dot, DOWN, buff=0.22)',
            'four_label = MathTex(r"4").next_to(output_dot, RIGHT, buff=0.28)')
    replace(p, 'therefore.next_to(left_nonnegative, DOWN, buff=0.48)',
            'therefore.next_to(left_nonnegative, RIGHT, buff=0.50)')
    replace(p, 'allowed_label.next_to(allowed_segment, DOWN, buff=0.38)',
            'allowed_label.next_to(number_line, DOWN, buff=0.45).shift(RIGHT * 1.5)')
    replace(p, 'minus_one_cross.next_to(minus_one_marker, UP, buff=0.08)',
            'minus_one_cross.next_to(minus_one_marker, LEFT, buff=0.15)')

    p = scene('16_pythagore_par_les_aires_fr')
    replace(p, '        logo = ImageMobject(str(scene_dir / "LOGO_UQAM.png"))\n',
            '        # The shared opening has already displayed the official logo.\n')
    replace(p, '            self.play(FadeIn(logo, shift=0.2*UP), run_time=0.6)\n            self.play(logo.animate.scale(0.5), run_time=1.0)\n            self.play(logo.animate.scale(1.0), run_time=1.0)\n            self.play(FadeOut(logo, shift=0.2*UP), run_time=0.6)\n',
            '            # Begin the lesson after its spoken introduction, not a second bumper.\n')
    replace('scripts/teaching_revision/review.py',
            "e['track'] == 'errors' or e['order'] <= 17]",
            "e['track'] == 'errors' or e['order'] <= 17 or e['order'] in (25, 26)]")
    replace('scripts/teaching_revision/review.py',
            '    output.mkdir(parents=True, exist_ok=True)\n    states, seen, kept',
            "    output.mkdir(parents=True, exist_ok=True)\n    (output / '_media').mkdir(exist_ok=True)\n    states, seen, kept")


def main():
    voice_and_intro()
    targeted_layout()
    for path in sorted(CHANGED):
        print(path)


if __name__ == '__main__':
    main()

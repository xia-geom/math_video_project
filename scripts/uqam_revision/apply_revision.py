"""Apply this review's focused edits once on the dedicated revision branch.

The workflow commits the resulting source diff, not just this migration.
Historical V2/V3 sources and rendered masters are never overwritten.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import textwrap
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
LONG = ROOT / "miscellaneous/uqam-baccalaureat-mathematiques-cheminements"
SHORT = ROOT / "miscellaneous/bac_math_uqam_fr"
REPORT = ROOT / "reports/uqam_video_revision/2026-09-14"
BASE = "0c4556ab07e8ae700c1556148374a83c0808cef1"
MARKER = REPORT / "implementation.json"


def edit(path, old, new, count=1):
    text = path.read_text()
    if text.count(old) < count:
        raise RuntimeError(f"Expected edit anchor missing in {path}: {old[:100]}")
    path.write_text(text.replace(old, new, count))


def replace_method(path, name, source, class_name=None):
    text = path.read_text()
    tree = ast.parse(text)
    nodes = tree.body
    if class_name:
        nodes = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name).body
    node = next(node for node in nodes if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name)
    lines = text.splitlines(keepends=True)
    replacement = textwrap.dedent(source).strip() + "\n"
    if class_name:
        replacement = textwrap.indent(replacement, "    ")
    lines[node.lineno - 1:node.end_lineno] = [replacement]
    path.write_text("".join(lines))


def set_toml(path, section, key, value):
    text = path.read_text()
    pattern = rf"(?ms)(^\[{re.escape(section)}\]\n)(.*?)(?=^\[|\Z)"
    match = re.search(pattern, text)
    if not match:
        raise RuntimeError(f"Missing TOML section {section}")
    body = match[2]
    line = f"{key} = {json.dumps(value, ensure_ascii=False)}\n"
    if re.search(rf"(?m)^{re.escape(key)}\s*=", body):
        body = re.sub(rf"(?m)^{re.escape(key)}\s*=.*\n", lambda _: line, body)
    else:
        body += line
    path.write_text(text[:match.start(2)] + body + text[match.end(2):])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if MARKER.exists():
        print("Revision already applied; no mutation.")
        return
    # Abort rather than overwrite intervening work in the files being migrated.
    targets = [LONG / name for name in ("v4_storyboard_data.py", "v4_visuals.py", "render_v4.py", "voiceover_v4_fr.txt", "project-manifest.toml", "storyboard-v4.md")]
    targets += [SHORT / "bac_math_uqam_fr_scene.py", SHORT / "build_release.py"]
    for path in targets:
        original = subprocess.check_output(["git", "show", f"{BASE}:{path.relative_to(ROOT)}"], cwd=ROOT)
        if path.read_bytes() != original:
            raise RuntimeError(f"Intervening changes require review: {path}")
    REPORT.mkdir(parents=True, exist_ok=True)
    historical_hash = digest(LONG / "program_data.py")

    for name in ("v4_storyboard_data.py", "v4_visuals.py"):
        edit(LONG / name, "from program_data import PROGRAMS", "from program_data_v4 import PROGRAMS")
    board = LONG / "v4_storyboard_data.py"
    edit(board, 'SOURCE_YEAR = "2025–2026"', 'SOURCE_YEAR = "2026–2027"')
    edit(board, '                    (3, 2),\n                    (4, 1),', '                    (3, 3),  # MAT2411: equations, not geometry\n                    (4, 1),')
    edit(board, '                    (2, 1),\n                    (3, 3),\n                    (5, 0),', '                    (2, 1),\n                    (5, 0),')
    edit(board, 'overview remains reusable; source vintages stay recorded in the manifest.', 'overview stays uncluttered; the audited source year is recorded in the manifest, not assumed timeless.')
    visuals = LONG / "v4_visuals.py"
    edit(visuals, 'from program_data_v4 import PROGRAMS', 'from program_data_v4 import PROGRAMS\nimport v4_photos')
    edit(visuals, 'uqam-guide-cover-2025-2026.png', 'uqam-guide-cover-2026-2027.png')
    # Insert photo compositing before the single RGB conversion of draw_scene.
    text = visuals.read_text()
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == 'draw_scene')
    lines = text.splitlines(keepends=True)
    body = ''.join(lines[node.lineno - 1:node.end_lineno])
    returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
    final_return = max(returns, key=lambda n: n.lineno)
    original_return = ast.get_source_segment(text, final_return.value)
    lines[final_return.lineno - 1:final_return.end_lineno] = [f'    return v4_photos.composite(scene_id, local_t, {original_return}, actions)\n']
    visuals.write_text(''.join(lines))

    render = LONG / "render_v4.py"
    edit(render, 'import v4_visuals\n', 'import v4_visuals\nimport v4_photos\nfrom tools.uqam_video_review import validate_subtitles\n')
    edit(render, 'SOURCE_YEAR_SLUG = MANIFEST["project"]["source_year"]', 'SOURCE_YEAR_SLUG = V4["source"]["course_map_source_year"]')
    edit(render, '    return windows\n\n\ndef make_frame', '''    if runtime.spec.id in v4_photos.PHOTO_SPECS:
        cue_index = 1 if runtime.spec.id == "v4_01_opening" else 2
        photo_end = starts[cue_index] if len(starts) > cue_index else 6.0
        photo_end = max(0.5, min(photo_end, active_end - 0.5))
        windows["photo_intro"] = (0.0, photo_end)
    return windows


def make_frame''')
    edit(render, '        signature: list[int] = []', '''        if t < v4_photos.end_time(runtime.spec.id, actions):
            return None  # Includes photographic crossfade; never reuse a stale still.
        signature: list[int] = []''')
    edit(render, '        "show_logo": 0,\n        "show_world": 0,', '        "show_logo": 2,\n        "show_world": 2,')
    edit(render, '    return checks\n\n\ndef check_environment', '''    checks.extend([
        (ROOT / V4["source"]["guide_pdf"], V4["source"]["guide_pdf_sha256"], "current official guide"),
        (v4_photos.ASSETS / "president_kennedy.jpg", V4["source"]["pk_sha256"], "President-Kennedy photo"),
        (v4_photos.ASSETS / "research_math.jpg", V4["source"]["research_photo_sha256"], "research-hub photo"),
    ])
    return checks


def check_environment''')
    edit(render, '        ROOT / "program_data.py",', '''        ROOT / "program_data.py",  # Historical baseline remains an explicit dependency.
        ROOT / "program_data_v4.py",
        ROOT / "v4_photos.py",
        PROJECT_ROOT / "tools/uqam_video_review.py",
        v4_photos.ASSETS / "sources.json",
        v4_photos.ASSETS / "president_kennedy.jpg",
        v4_photos.ASSETS / "research_math.jpg",
        ROOT / V4["source"]["guide_pdf"],''')
    edit(render, '            "source_year": MANIFEST["project"]["source_year"],', '            "source_year": V4["source"]["course_map_source_year"],')
    edit(render, '        "video_probe": final_probe,', '''        "video_probe": final_probe,
        "review_status": {"encoded_visual_review": "pending", "full_listening": "pending", "institutional_approval": "not inferred"},
        "photo_credits": [record for runtime in runtimes for record in v4_photos.credit_records(runtime.spec.id, runtime.spec.start, aligned_actions(runtime))],''')
    # Reject an extended programme that would outlive the two-pass musical bed.
    edit(render, '    fade_out_start = TARGET_DURATION - fade_out', '''    source_duration = float(V4_MUSIC["duration_seconds"])
    if crossfade >= source_duration or TARGET_DURATION > 2 * source_duration - crossfade:
        raise RuntimeError("Music coverage is too short; explicitly revise the loop before extending V4")
    fade_out_start = TARGET_DURATION - fade_out''')
    # Subtitle review statistics accompany the actual exported SRT.
    text = render.read_text()
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == 'write_srt')
    lines = text.splitlines(keepends=True)
    last = max((n for n in ast.walk(node) if isinstance(n, ast.Return)), key=lambda n:n.lineno)
    lines[last.lineno - 1:last.lineno - 1] = ['    path.with_suffix(".review.json").write_text(json.dumps(validate_subtitles(path, TARGET_DURATION), indent=2), encoding="utf-8")\n']
    render.write_text(''.join(lines))

    narration = LONG / "voiceover_v4_fr.txt"
    edit(narration, 'Cette présentation décrit l’organisation du baccalauréat en mathématiques à l’UQAM.\nElle présente les cheminements proposés.\nElle précise les particularités des trois concentrations.', "À l’UQAM, les mathématiques se découvrent au cœur de Montréal.\nStructures, données, algorithmes : trois directions à explorer.\nDécouvrez les concentrations et la façon d’organiser votre parcours.")
    edit(narration, 'Les mathématiques ouvrent des portes et structurent la pensée.\nElles accompagnent toute une vie.\nNotre équipe enseignante est prête à vous transmettre cette passion.\nElle est prête à vous donner les outils pour construire votre avenir.', "L’UQAM propose un milieu pour apprendre et explorer les mathématiques.\nLe pôle mathématique rassemble une communauté de recherche.\nDécouvrez le baccalauréat en mathématiques et ses concentrations.\nConsultez le programme pour préparer votre parcours avec notre équipe.")
    with (LONG / 'storyboard-v4.md').open('a') as out:
        out.write('\n\n## Révision du 14 septembre 2026\n\nDonnées V4 uniquement : guide 2026–2027, version du 24 juillet, pages 9, 13, 18, 22. MAT2411 relève des équations; la géométrie ne sélectionne plus cette case. Président-Kennedy ouvre la première scène jusqu’à la deuxième phrase; le pôle mathématique ouvre la conclusion jusqu’à la troisième phrase. Les horloges restent à 15 et 22 secondes, total 283 secondes. Les fenêtres photo sont alignées sur les phrases réelles; le cache tient compte des fondus. Crédits sur panneaux opaques; aucun témoignage personnel n’est inféré des images.\n')
    with (LONG / 'README.md').open('a') as out:
        out.write('\n\n## Révision V4 — 14 septembre 2026\n\nLa nouvelle V4 utilise `program_data_v4.py` et le PDF officiel complet 2026–2027. Les paragraphes historiques ci-dessus concernant les grilles 2025–2026 ne décrivent plus cette révision. V2/V3 et `program_data.py` restent historiques. Le millésime absent du titre ne constitue pas une garantie d’actualité : vérifier le manifeste avant diffusion. Les sorties de revue utilisent un `--artifact-tag` et ne remplacent pas les masters. Voir `../../reports/uqam_video_revision/2026-09-14/PLAN.md` et les artefacts du workflow UQAM revision.\n')

    # Capture the official PDF once, with source checks and a pinned derived cover.
    guide = LONG / 'assets/sources/uqam-guide-etudiant-2026-2027.pdf'
    url = 'https://math.uqam.ca/wp-content/uploads/sites/23/guide-etudiant_2026-2027.pdf'
    request = urllib.request.Request(url, headers={'User-Agent': 'UQAM-video-source-review/1.0'})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read()
    if not data.startswith(b'%PDF'):
        raise RuntimeError('Official guide download is not a PDF')
    guide.write_bytes(data)
    extracted = subprocess.check_output(['pdftotext', '-layout', str(guide), '-']).decode()
    if not all(term in extracted for term in ('2026', '2027', 'MAT2411', 'MAT1260', 'INF5130')):
        raise RuntimeError('Downloaded guide lacks expected source markers')
    cover = LONG / 'assets/sources/uqam-guide-cover-2026-2027.png'
    subprocess.run(['pdftoppm', '-f', '1', '-singlefile', '-scale-to', '1200', '-png', str(guide), str(cover.with_suffix(''))], check=True)
    manifest = LONG / 'project-manifest.toml'
    for key, value in {'course_map_source_year':'2026–2027', 'guide_pdf':str(guide.relative_to(LONG)), 'guide_pdf_sha256':digest(guide), 'guide_pdf_url':url, 'guide_pdf_version':'2026-07-24', 'guide_cover':str(cover.relative_to(LONG)), 'guide_cover_sha256':digest(cover), 'pk_sha256':digest(ROOT/'assets/uqam_promo/president_kennedy.jpg'), 'research_photo_sha256':digest(ROOT/'assets/uqam_promo/research_math.jpg')}.items():
        set_toml(manifest, 'v4.source', key, value)
    set_toml(manifest, 'v4', 'storyboard_sha256', digest(LONG/'storyboard-v4.md'))
    set_toml(manifest, 'v4', 'release', '4.4.0-review')

    # Apply short-film speech-boundary edits from the companion migration.
    sys.path.insert(0, str(Path(__file__).parent))
    from short_revision import apply_short
    apply_short(ROOT, replace_method, edit)

    # V4 tests should compare against V4 data, not silently mutate V2/V3 fixtures.
    tests = LONG/'tests/test_render_v4.py'
    text = tests.read_text().replace('from program_data import ', 'from program_data_v4 import ')
    tests.write_text(text)
    # Existing source-inspection tests are updated for the revised narrative contract.
    tests = ROOT/'tests/test_uqam_promo.py'
    text = tests.read_text()
    text = text.replace('assert "self.wait(RESEARCH_GRAPH_HOLD)" in research_act', 'assert "narrate_unit" in research_act')
    text = text.replace('assert "self.wait(MONTREAL_BUILDING_HOLD)" in montreal_act', 'assert "narrate_unit" in montreal_act')
    text = text.replace('assert "self.wait(MONTREAL_PHOTO_HOLD)" in montreal_act', 'assert "record_photo" in montreal_act')
    text = text.replace('assert "self.wait(FINAL_MESSAGE_HOLD)" in close_act', 'assert "narrate_unit" in close_act')
    tests.write_text(text)
    sys.path.insert(0, str(LONG))
    import program_data_v4 as current
    from program_data import PROGRAMS as old
    from dataclasses import asdict
    changes = []
    for key, program in current.PROGRAMS.items():
        for row, semester in enumerate(program['semesters']):
            for col, course in enumerate(semester):
                previous = old[key]['semesters'][row][col]
                if (previous.title, previous.category) != (course.title, course.category):
                    changes.append({'program':key, 'row_zero_based':row, 'column_zero_based':col, 'before':asdict(previous), 'after':asdict(course)})
    (REPORT/'course_data_diff.json').write_text(json.dumps(changes, indent=2, ensure_ascii=False)+'\n')
    (REPORT/'course_inventory_2026-2027.json').write_text(json.dumps({key: {'page':p['source_page'], 'semesters':[[asdict(c) for c in s] for s in p['semesters']]} for key,p in current.PROGRAMS.items()}, indent=2, ensure_ascii=False)+'\n')
    if digest(LONG/'program_data.py') != historical_hash:
        raise RuntimeError('Historical course data were modified')
    MARKER.write_text(json.dumps({'baseline':BASE, 'historical_program_data_sha256':historical_hash, 'guide_pdf_sha256':digest(guide), 'implementation':'applied; test results recorded by workflow', 'visual_review':'pending', 'listening':'pending', 'institutional_approval':'not inferred'}, indent=2)+'\n')
    print('Applied UQAM revision. Review source diff and run tests before approval.')

if __name__ == '__main__':
    main()

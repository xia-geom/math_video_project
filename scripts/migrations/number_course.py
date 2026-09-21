"""One-time, idempotent v2 -> v3 course-numbering migration requested 2026-09-20.

Run only on the syllabus feature branch. It never reads or moves local rendered
media, never publishes, and preserves historical audit reports verbatim.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
BASE = "0bcd9451b644256a2ad2927d5eccc5aa8797404e"
ORDER = (
    "P01 P02 P03 S01 P04 P05 P06 P07 P08 P09 P10 P11 P12 P13 S02 "
    "P14 P15 P16 P17 S03 P18 P19 P20 S04 P21 P22 P23 S06 S05 S07 "
    "P24 S08 S09 S10 P25 P26 P27 E01 E02 E03 E04 E05 E06"
).split()
NEW_SLUGS = {
    "S01": "operations_nombres_reels", "S02": "fonctions_rationnelles",
    "S03": "modeles_probabilistes", "S04": "equations_droite_plan",
    "S05": "regle_cramer", "S06": "elimination_variables",
    "S07": "programmation_lineaire", "S08": "trigonometrie_triangle",
    "S09": "lois_sinus_cosinus", "S10": "fonctions_trigonometriques_inverses",
}


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise ValueError(f"Migration anchor changed: {path}: {old[:90]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise ValueError(f"Migration anchor absent: {path}: {old[:90]!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def migrate() -> None:
    manifest = ROOT / "curriculum/programme_principal_fr.yaml"
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    if data.get("version") == 3:
        from tools.course_catalog import load_catalog
        load_catalog()
        print("Course numbering migration already applied; no change")
        return
    if data.get("version") != 2:
        raise ValueError("Unsupported source catalogue version")
    scope_path = ROOT / "curriculum/extension_syllabus_fr.yaml"
    scope = yaml.safe_load(scope_path.read_text(encoding="utf-8"))
    if scope.get("version") != 1:
        raise ValueError("Unsupported candidate manifest version")
    old_entries = {}
    for entry in data["entries"]:
        alias = f"{'P' if entry['track'] == 'programme' else 'E'}{entry['order']:02d}"
        old_entries[alias] = dict(entry)
    for entry in scope["entries"]:
        alias = entry["id"]
        old_entries[alias] = {**entry, "track": "programme", "delivery_slug": NEW_SLUGS[alias],
                              "coverage": entry["objective"]}
    if set(old_entries) != set(ORDER) or len(ORDER) != 43:
        raise ValueError("Source lesson inventory differs from the reviewed 43-lesson plan")
    stable_ids = {alias: entry["delivery_slug"] for alias, entry in old_entries.items()}
    entries, mapping, slug_map = [], [], {}
    for number, alias in enumerate(ORDER, 1):
        old = old_entries[alias]
        old_path = Path(old["scene_file"])
        new_slug = re.sub(r"^[0-9]+_", f"{number:02d}_", old_path.parent.name)
        new_path = old_path.parent.parent / new_slug / f"{new_slug}_scene.py"
        source = ROOT / old_path
        if not source.is_file():
            raise ValueError(f"Source not found: {source}")
        prerequisites = old.get("prerequisites", [])
        # The geometry proof stays at the end, per the syllabus. Knowing the
        # school-level theorem is not a requirement to watch that later proof.
        if alias == "S08":
            prerequisites = [p for p in prerequisites if p != "P26"]
        entry = {"order": number, "lesson_id": stable_ids[alias], "legacy_id": alias,
                 "track": old["track"], "module": old["module"], "title": old["title"],
                 "delivery_slug": old["delivery_slug"], "scene_file": new_path.as_posix(),
                 "scene_class": old["scene_class"], "coverage": old["coverage"],
                 "prerequisites": [stable_ids[p] for p in prerequisites],
                 "requires_narration": True,
                 "status": "authored" if alias.startswith("S") else "existing_review_required"}
        for field in ("objective", "self_check"):
            if field in old:
                entry[field] = old[field]
        if alias == "S08":
            entry["assumed_knowledge"] = ["Triangle rectangle et théorème de Pythagore au niveau scolaire"]
            entry["related_lessons"] = [stable_ids["P26"]]
        entries.append(entry)
        mapping.append({"legacy_id": alias, "lesson_id": stable_ids[alias], "order": number,
                        "old_track": old["track"], "old_track_order": old.get("order"),
                        "old_scene_file": old_path.as_posix(), "scene_file": new_path.as_posix(),
                        "scene_class": old["scene_class"], "old_artifact_slug": old_path.parent.name,
                        "delivery_name": f"{number:02d}_{old['delivery_slug']}",
                        "old_delivery_name": f"{old['order']:02d}_{old['delivery_slug']}" if "order" in old else None,
                        "source_sha256_before": hashlib.sha256(source.read_bytes()).hexdigest()})
        slug_map[old_path.parent.name] = new_slug
    # Rename complete topic directories, including their relative assets.
    for entry in mapping:
        old, new = ROOT / entry["old_scene_file"], ROOT / entry["scene_file"]
        if old == new:
            continue
        if new.parent.exists():
            raise ValueError(f"Destination already exists: {new.parent}")
        old.parent.rename(new.parent)
        (new.parent / old.name).rename(new)
    # Simultaneous token replacement avoids cascading 04->05->06 renumberings.
    pattern = re.compile("|".join(re.escape(s) for s in sorted(slug_map, key=len, reverse=True)))
    roots = ["scenes", "tools", "tests", "docs", ".github", ".vscode"]
    active = [p for folder in roots for p in (ROOT / folder).rglob("*") if p.is_file()]
    active += [p for p in (ROOT / "scripts").rglob("*") if p.is_file()
               and "migrations" not in p.parts and "audit_integration" not in p.parts
               and ("teaching_revision" not in p.parts or p.name in {"review.py", "validate.py"})]
    active += [ROOT / p for p in ("README.md", "AGENT.md", "AGENTS.md", "ARCHITECTURE.md") if (ROOT / p).is_file()]
    for path in active:
        if path == ROOT / "tests/test_course_catalog.py":
            continue  # Historical-path fixtures must keep their original meaning.
        if path.suffix.lower() not in {".py", ".md", ".sh", ".yml", ".yaml", ".json", ".txt", ".toml", ".ssml", ".srt"}:
            continue
        text = path.read_text(encoding="utf-8")
        new = pattern.sub(lambda match: slug_map[match.group()], text)
        if new != text:
            path.write_text(new, encoding="utf-8")
    data.update(version=3, numbering="global_across_tracks", expected_counts={"programme": 37, "errors": 6},
                release_ready=False, entries=entries)
    manifest.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    scope = {"version": 2, "title": "Compléments du syllabus — suivi de production",
             "canonical_manifest": "curriculum/programme_principal_fr.yaml", "release_ready": False,
             "candidate_ids": [stable_ids[f"S{i:02d}"] for i in range(1, 11)],
             "optional": scope["optional"]}
    scope_path.write_text(yaml.safe_dump(scope, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (ROOT / "curriculum/numbering_migration.json").write_text(json.dumps(
        {"version": 1, "source_commit": BASE, "historical_reports_rewritten": False, "entries": mapping},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    update_consumers()
    update_extra_consumers()
    update_documentation(entries)
    from tools.course_catalog import load_catalog, write_indexes
    load_catalog()
    write_indexes()
    print("Unified all 43 course videos, source paths, runtime consumers and indexes")


def update_consumers() -> None:
    path = "scripts/render_curriculum.py"
    replace_once(path, "import yaml\n", "from tools.course_catalog import load_catalog\n")
    replace_once(path, "from tools.course_catalog import load_catalog\n", "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\nfrom tools.course_catalog import load_catalog  # noqa: E402\n")
    replace_once(path, "    coverage: str\n", "    coverage: str\n    lesson_id: str\n    legacy_id: str\n    requires_narration: bool\n")
    replace_once(path, "        return Path(self.scene_file).parent.name", "        return self.delivery_name")
    replace_once(path, '        return self.track == "programme" and self.order <= 24', '        return self.requires_narration')
    p = ROOT / path
    text = p.read_text()
    start, end = text.index("    raw = yaml.safe_load", text.index("def read_manifest")), text.index("\n\ndef select_entries")
    text = text[:start] + '''    raw, rows = load_catalog(path, root=PROJECT_ROOT)
    fields = set(Entry.__dataclass_fields__)
    return raw, [Entry(**{key: row[key] for key in fields}) for row in rows]
''' + text[end:]
    text = text.replace('"Les 27 vidéos sont numérotées dans l\'ordre pédagogique recommandé."', 'f"Les {len(entries)} vidéos suivent la numérotation globale du cours."')
    text = text.replace('expected_count = 27 if track == "programme" else 6', 'expected_count = manifest["expected_counts"][track]')
    text = text.replace('            # Geometry, notation, and common-error videos retain their existing\n            # render quality; production requirements apply to lessons 01..24.\n', '            # Requirements are explicit, never inferred from the display number.\n')
    text = text.replace('    if orders:\n        selected = [entry for entry in selected if entry.order in orders]', '    if orders is not None:\n        unknown = orders - {entry.order for entry in selected}\n        if unknown:\n            raise ValueError(f"Unknown global course numbers for this track: {sorted(unknown)}")\n        selected = [entry for entry in selected if entry.order in orders]')
    p.write_text(text)
    path = "scripts/render_syllabus_expansion.py"
    p = ROOT / path
    text = p.read_text()
    start, end = text.index("    data = yaml.safe_load", text.index("def read_candidates")), text.index("\n\ndef select_candidates")
    text = text[:start] + '''    sys.path.insert(0, str(ROOT))
    from tools.course_catalog import load_catalog
    data = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if data.get('version') != 2 or data.get('release_ready') is not False:
        raise ValueError('Expected a version-two, non-release production scope.')
    _, rows = load_catalog(ROOT / data['canonical_manifest'])
    by_id = {e['lesson_id']: e for e in rows}
    ids = data['candidate_ids']
    if not ids or len(ids) != len(set(ids)) or set(ids) - by_id.keys():
        raise ValueError('Invalid candidate scope; sources belong in the main catalogue.')
    return data, [{**by_id[key], 'id': by_id[key]['legacy_id']} for key in ids]
''' + text[end:]
    text = text.replace("dest = output / entry['id']", "dest = output / f\"{entry['order']:02d}_{entry['delivery_slug']}\"")
    text = text.replace('stem = f"{entry[\'id\']}_{label}"', 'stem = f"{entry[\'order\']:02d}_{entry[\'delivery_slug\']}_{label}"')
    text = text.replace("result = {'id': entry['id'],", "result = {'id': entry['id'], 'global_number': entry['order'], 'lesson_id': entry['lesson_id'],")
    p.write_text(text)
    path = "scripts/teaching_revision/review.py"
    replace_once(path, "    return [e for e in data['entries'] if e['track'] == 'errors' or e['order'] <= 17 or e['order'] in (25, 26)]", "    return sorted(data['entries'], key=lambda e: e['order'])")
    replace_once(path, "frame_limit = 100 if ((entry['track'] == 'errors' and entry['order'] in (2, 3)) or (entry['track'] == 'programme' and entry['order'] in (1, 8, 12))) else 8", "frame_limit = 100 if entry['legacy_id'] in {'E02', 'E03', 'P01', 'P08', 'P12'} else 12")
    replace_once("scripts/teaching_revision/validate.py", "selected = [e for e in targets if e['track'] == 'errors' and e['order'] in (2, 3)]", "selected = [e for e in targets if e['legacy_id'] in {'E02', 'E03'}]")
    path = "tests/test_render_curriculum.py"
    replace_once(path, 'assert [entry.order for entry in programme] == list(range(1, 28))', 'assert [entry.order for entry in programme] == list(range(1, 38))')
    replace_once(path, 'assert [entry.order for entry in errors] == list(range(1, 7))', 'assert [entry.order for entry in errors] == list(range(38, 44))')
    replace_all(path, 'orders=set(range(15, 24)),', 'orders={e.order for e in entries if e.legacy_id in {f"P{i:02d}" for i in range(15, 24)}},')
    replace_once(path, 'def test_new_lessons_fill_positions_15_through_23()', 'def test_historical_nine_lesson_group_keeps_its_identities()')
    replace_once(path, '"scenes/vecteurs_fr/example/example_scene.py",', 'next(e.scene_file for e in render_curriculum.read_manifest(MANIFEST)[1] if e.legacy_id == "P18"),')
    path = "scripts/render.sh"
    replace_once(path, 'ARTIFACT_NAME="$(basename "$(dirname "$SCENE_FILE")")"', '# Artifact name is resolved after the catalogue path below.')
    replace_once(path, 'case "$QUALITY" in', '''SCENE_FILE="$("$PYTHON" "$ROOT_DIR/tools/course_catalog.py" resolve-path "$SCENE_FILE")"
ARTIFACT_NAME="$("$PYTHON" "$ROOT_DIR/tools/course_catalog.py" artifact-name "$SCENE_FILE")"

case "$QUALITY" in''')
    p = ROOT / "scripts/render_outputs.sh"
    text = p.read_text()
    start, end = text.index("resolve_google_drive_video_theme_dir()"), text.index("\ncopy_render_mp4_to_drive()")
    text = text[:start] + '''resolve_google_drive_video_theme_dir() {
    local scene_file="${1:-}" root_dir python route drive_dir
    root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    python="${RENDER_PYTHON:-$root_dir/.venv/bin/python}"
    [[ -x "$python" ]] || python="$(command -v python3)"
    route="$("$python" "$root_dir/tools/course_catalog.py" route "$scene_file")" || return 1
    drive_dir="$(resolve_google_drive_video_dir)"
    printf '%s\\n' "$drive_dir/$route"
}
''' + text[end:]
    p.write_text(text)
    if "fromJSON(needs.catalog.outputs.matrix)" not in (ROOT / ".github/workflows/smoke.yml").read_text():
        raise ValueError("Commit the reviewed catalogue-driven workflow before migration")


def update_extra_consumers() -> None:
    p = ROOT / "tools/video_audit/batch.py"
    text = p.read_text()
    old = '    workflow = workflow_path or project_root / ".github" / "workflows" / "smoke.yml"'
    new = '''    if workflow_path is None:
        from tools.course_catalog import load_catalog
        _, entries = load_catalog(project_root / "curriculum/programme_principal_fr.yaml", root=project_root)
        return [SceneEntry(Path(e["scene_file"]), e["scene_class"]) for e in entries]
    workflow = workflow_path'''
    if text.count(old) != 1:
        raise ValueError("Batch registry anchor changed")
    text = text.replace(old, new)
    text = text.replace('video_path = canonical_video_path(project_root, entry.scene_file)',
                        'video_path = canonical_video_path(project_root, entry.scene_file, quality="ql" if render else "qh")')
    p.write_text(text)
    (ROOT / "tools/video_audit/paths.py").write_text('from __future__ import annotations\n\nfrom functools import lru_cache\nfrom pathlib import Path\n\n\n@lru_cache(maxsize=4)\ndef _catalogue(root: Path, _mtime_ns: int):\n    from tools.course_catalog import load_catalog\n    return load_catalog(root / "curriculum/programme_principal_fr.yaml", root=root)[1]\n\n\ndef artifact_name_for_scene(scene_path: Path, project_root: Path | None = None) -> str:\n    """Resolve the shared delivery identity, with a fallback only outside a catalogue."""\n    from tools.course_catalog import ROOT, delivery_name, resolve_scene_path\n    root = project_root or ROOT\n    manifest = root / "curriculum/programme_principal_fr.yaml"\n    if manifest.is_file():\n        entries = _catalogue(root.resolve(), manifest.stat().st_mtime_ns)\n        source = resolve_scene_path(str(scene_path), root=root)\n        entry = next((e for e in entries if e["scene_file"] == source), None)\n        if entry is not None:\n            return delivery_name(entry)\n    return scene_path.parent.name\n\n\ndef canonical_video_path(project_root: Path, scene_path: Path, quality: str = "qh") -> Path:\n    name = artifact_name_for_scene(scene_path, project_root)\n    if quality not in {"ql", "qm", "qh"}:\n        raise ValueError("Unknown render quality")\n    if quality == "qh":\n        return project_root / "dist" / name / f"{name}.mp4"\n    return project_root / "dist/_previews" / quality / name / f"{name}__{quality}.mp4"\n')
    p = ROOT / "pyproject.toml"
    text = p.read_text().replace('build-backend = "setuptools.backends.legacy:build"',
                               'build-backend = "setuptools.build_meta"')
    text += '\n[tool.setuptools.packages.find]\ninclude = ["tools*"]\n'
    p.write_text(text)
    p = ROOT / "scripts/render_syllabus_expansion.py"
    text = p.read_text()
    text = text.replace("return data, [{**by_id[key], 'id': by_id[key]['legacy_id']} for key in ids]",
                        "return data, sorted(({**by_id[key], 'id': by_id[key]['legacy_id']} for key in ids), key=lambda e: e['order'])")
    start, end = text.index("    if not requested:", text.index("def select_candidates")), text.index("\n\ndef inspect_streams")
    text = text[:start] + '''    if not requested:
        return list(entries)
    from tools.course_catalog import resolve
    selectors = {value.strip() for value in requested.split(',') if value.strip()}
    if not selectors:
        raise ValueError('Empty candidate selection')
    selected = {resolve(value, entries)['lesson_id'] for value in selectors}
    return [e for e in entries if e['lesson_id'] in selected]
''' + text[end:]
    p.write_text(text)
    replace_once("tests/test_syllabus_expansion.py", "assert [e['id'] for e in entries] == [f'S{i:02d}' for i in range(1, 11)]",
                 "assert {e['id'] for e in entries} == {f'S{i:02d}' for i in range(1, 11)}\n    assert [e['order'] for e in entries] == sorted(e['order'] for e in entries)")
    replace_once("scripts/render_curriculum.py", '    expected_count = manifest["expected_counts"][track]',
                 '''    canonical_ids = {e["lesson_id"] for e in manifest["entries"] if e["track"] == track}
    if {e.lesson_id for e in entries} != canonical_ids:
        raise ValueError("Package selection does not match the canonical track")
    expected_count = manifest["expected_counts"][track]''')


def update_documentation(entries) -> None:
    p = ROOT / "curriculum/README.md"
    p.write_text('''# Cours de mathématiques — catalogue unifié

La source unique est [programme_principal_fr.yaml](programme_principal_fr.yaml).
Les 37 leçons principales suivent le syllabus ; les six vidéos d'erreurs
fréquentes continuent la séquence globale de 38 à 43 dans leur collection propre.
Les films promotionnels et l'identité visuelle sont exclus de cette numérotation.

[Numérotation et liens vers les 43 sources](NUMBERING.md) ·
[Correspondance avec les anciens codes et chemins](LEGACY_NUMBERING.md) ·
[Index exploitable par les outils](playlist.csv).

Les dix ajouts sont placés dans leurs chapitres, pas ajoutés artificiellement à
la fin. L'élimination précède Cramer, puis la programmation linéaire. Les deux
preuves de géométrie et la notation sigma restent à la fin du parcours principal.
La preuve de Pythagore est une leçon liée à la trigonométrie, non un prérequis
vidéo à voir plus tard ; la connaissance scolaire du théorème est explicitée.

`extension_syllabus_fr.yaml` ne contient plus de seconde copie des chemins,
objectifs ou prérequis : ce fichier sélectionne seulement les dix productions
nouvelles dans le catalogue commun. Les nombres complexes restent facultatifs,
non implémentés et sans numéro de vidéo réservé.

## Utilisation

```bash
python tools/course_catalog.py check
python tools/course_catalog.py --write-indexes
python scripts/render_curriculum.py --list
# Le numéro est global, même avec --track errors.
python scripts/render_curriculum.py --track programme --order 15 --quality ql --render --disable-voiceover
python scripts/render_curriculum.py --track errors --order 39 --quality ql --render --disable-voiceover
# Les anciens alias S restent acceptés pour sélectionner le lot de nouvelles productions.
python scripts/render_syllabus_expansion.py --check-only
python scripts/render_syllabus_expansion.py --ids S01,S02 --mode silent
```

La classe publique de chaque scène est préservée. `scripts/render.sh` résout les
anciens chemins exacts grâce à la correspondance et utilise le même nom de
livraison que le rendu par curriculum. Les dossiers de sources, les noms des
sources, les sorties, les index et les sélections ont le même numéro global.
Les rapports historiques ne changent pas de sens : leurs codes P/E/S demeurent
historiques, avec une correspondance explicite vers le présent catalogue.

## Vérification et état des vidéos

Une source intégrée et numérotée n'est pas une vidéo publiée. Les tests de
catalogue, de mathématiques, de rendu, d'images, de mouvement et d'audio sont
distincts. Les dix nouvelles leçons conservent leur statut de production ; aucune
approbation audiovisuelle n'est déduite du changement de numéro.

Les anciens MP4 locaux, archives de rendu et copies Drive ne sont ni déplacés ni
effacés par la migration Git. Les prochains rendus emploient les nouveaux noms ;
`numbering_migration.json` conserve les anciens noms pour une migration locale
explicite. Ne pas réutiliser un MP4 simplement parce que son ancien numéro
correspond à un nouveau numéro.

Lire [le standard d'enseignement](../docs/TEACHING_STANDARD.md) avant de créer ou
modifier une leçon. Les résultats datés se trouvent dans
[le rapport d'audit global](../reports/course_audit/2026-09-20/AUDIT.md).
''', encoding="utf-8")
    p = ROOT / "scenes/AGENTS.md"
    p.write_text('''# Teaching-scene instructions

Read the root guide, `docs/TEACHING_STANDARD.md` and `curriculum/README.md`.
`curriculum/programme_principal_fr.yaml` is the only numbering authority.
Every course source directory and filename starts with its global course number;
error lessons do not restart at 01. Use stable `lesson_id` values for dependencies
and keep existing public scene classes. Never infer readiness or audit scope from
a numeric range. P/E/S identifiers are historical aliases only.

For renumbering, update source directories and their relative assets, active
references, the catalogue, generated indexes, routing, CLI selections and tests
as one change. Preserve old-to-new mappings and dated audit evidence. Do not
rename or overwrite old media automatically. `python tools/course_catalog.py
--write-indexes` regenerates the reading indexes from the catalogue.

Clear outgoing cases and updaters before new content; prefer sequential fades
for unrelated text, full-size readable labels, equal geometric unit scales, and
one shared UQAM opening. A new source or successful silent preview is not a release.
Use the shared narration adapter and explicit silent mode. Record syntax,
mathematics, construction, encoded-frame, full-motion and listening checks
separately. Keep generated media out of source Git and do not publish as a side
effect of a code or numbering change.
''', encoding="utf-8")
    p = ROOT / "docs/TEACHING_STANDARD.md"
    text = p.read_text()
    text = text.replace("Applies to the 27 curriculum lessons and six common-error lessons listed in\n`curriculum/programme_principal_fr.yaml`, and to new syllabus candidates tracked\nin `curriculum/extension_syllabus_fr.yaml`.", "Applies to all 43 course videos in `curriculum/programme_principal_fr.yaml`: 37\nmain lessons and six common-error supplements, with unique global numbers 01–43.\n`curriculum/extension_syllabus_fr.yaml` is only a production-scope selection.")
    text = text.replace("The focused review covers the first 17 curriculum lessons, the two geometry\nlessons numbered 15/16 in their filenames, and all six common-error lessons.", "The construction review covers every catalogue entry, independent of its number.")
    text = text.replace("Register its canonical scene path\nand public class in the expansion manifest before rendering.", "Register its stable ID, global number, canonical scene path\nand public class in the unified catalogue before rendering.")
    text += "\n## Global numbering\n\nUse the catalogue number in source paths and all delivery names. Dependencies and\naudit targeting use stable lesson identities, not position ranges. Keep the old\nP/E/S codes only as historical aliases with the explicit migration lookup.\nProduction audio and quality checks apply to all course entries, never only the\nfirst numbered subset. Numbering is independent of release readiness.\n"
    p.write_text(text)
    p = ROOT / "curriculum/couverture_programme.md"
    text = p.read_text()
    text = text.replace("Cette collection organise 27 capsules", "Cette collection organise 37 capsules principales et six compléments d'erreurs fréquentes")
    text += "\n## Catalogue unifié — 20 septembre 2026\n\nLes dix thèmes ajoutés sont intégrés aux chapitres dans le catalogue canonique.\nLa [numérotation globale](NUMBERING.md) va de 01 à 43 et ne certifie ni la\npublication ni la couverture exhaustive d'un chapitre. La liste des anciennes\nlacunes ci-dessus conserve la trace du plan ; l'état de chaque production et les\nrapports datés indiquent les vérifications réellement effectuées.\n"
    p.write_text(text)
    p = ROOT / "README.md"
    if p.exists():
        text = p.read_text()
        start, end = text.index("## Project Status"), text.index("## Setup")
        text = text[:start] + '''## Project Status

The unified course contains **43 globally numbered teaching videos**: 37 main
lessons and six common-error supplements numbered 38–43. The 10 syllabus
additions are integrated into their chapters but remain productions under review.
There are 44 scene sources including the separate, unnumbered course-identity
animation. Promotional films are outside the course sequence.

[Complete course order](curriculum/NUMBERING.md) ·
[Historical numbering lookup](curriculum/LEGACY_NUMBERING.md) ·
[Production and audit status](reports/course_audit/2026-09-20/AUDIT.md).

`curriculum/programme_principal_fr.yaml` is the sole authority for global numbers,
source paths, packaging and Drive routing. Public scene classes are unchanged.
Generated catalogue indexes replace hand-maintained copies of the course list.

''' + text[end:]
        start, end = text.index("## Scene Organization"), text.index("## Common Mathematical Errors")
        text = text[:start] + '''## Scene Organization

Sources use `scenes/<category>/<global-number>_<topic>/<global-number>_<topic>_scene.py`.
See [the generated course inventory](curriculum/NUMBERING.md) for every source.
Global numbers are unique across categories and tracks; the identity bumper
is not a numbered course video. Semantic IDs and public classes remain stable.

''' + text[end:]
        start = text.index("| No. | Lesson | Scene class | Misconception addressed |")
        end = text.index("## Main Curriculum", start)
        text = text[:start] + "The six supplements now use global numbers 38–43. Their sources and historical\naliases are listed in [the course inventory](curriculum/NUMBERING.md).\n\n" + text[end:]
        start = text.index("## Main Curriculum")
        match = re.search(r"\n## [^#]", text[start + 1:])
        end = start + 1 + match.start() + 1 if match else len(text)
        text = text[:start] + "## Main Curriculum — Pedagogical Order\n\nSee [the generated course order](curriculum/NUMBERING.md) and\n[the machine-readable playlist](curriculum/playlist.csv). Update the catalogue,\nthen run `python tools/course_catalog.py --write-indexes`; do not duplicate it here.\n\n" + text[end:]
        text = text.replace("# Validate and build the 27-video programme plus the six common-error videos", "# Validate and build the 37-video programme plus globally numbered supplements")
        text = text.replace("# Silent 480p previews of the nine newly integrated lessons", "# Silent 480p previews selected by GLOBAL course number")
        text = text.replace("# Resumable narrated 1080p render; existing geometry and notation renders are reused", "# Resumable narrated 1080p render; every course video must pass the same checks")
        text = text.replace("audit all 11 CI-registered scenes", "audit all 43 course scenes")
        p.write_text(text)
    p = ROOT / "ARCHITECTURE.md"
    if p.exists():
        text = p.read_text().replace("Historical folder numbers do not always equal their current position in the assembled programme.", "Every course folder and source filename now uses its unique global catalogue number. Historical numbers survive only in the explicit migration lookup.")
        text = text.replace("The 27 curriculum and six common-error lessons", "The 37 curriculum and six common-error lessons")
        text += "\n## Unified course numbering\n\nThe catalogue is version 3: 01–37 main lessons, 38–43 common-error supplements.\n`tools/course_catalog.py` validates identities, sources, prerequisites and counts,\nresolves historical paths and owns delivery routing. Generated indexes and the\nlegacy lookup live in `curriculum/`. Numbers are display order, not source IDs,\nrelease approval or permission to overwrite older media. Promotions are excluded.\n"
        p.write_text(text)
    p = ROOT / "AGENTS.md"
    if p.exists():
        text = p.read_text() + "\nFor course work, also read `scenes/AGENTS.md` and `curriculum/README.md`. Use the\nunified catalogue and generated numbering index; do not maintain a second list\nor infer release requirements from an entry's position.\n"
        p.write_text(text)


if __name__ == "__main__":
    migrate()

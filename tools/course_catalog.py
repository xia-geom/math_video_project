"""Single source of course identity, global numbering and delivery routing.

Semantic lesson IDs are stable. Display numbers come only from the catalogue;
P/E/S identifiers are historical aliases, never a second numbering scheme.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "curriculum/programme_principal_fr.yaml"
MIGRATION = ROOT / "curriculum/numbering_migration.json"


def load_catalog(path: Path = MANIFEST, *, root: Path = ROOT,
                 check_inventory: bool = True) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 3:
        raise ValueError("Expected the unified version-three course catalogue")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("The course catalogue must not be empty")
    required = {"lesson_id", "legacy_id", "order", "track", "module", "title",
                "delivery_slug", "scene_file", "scene_class", "coverage",
                "prerequisites", "requires_narration", "status"}
    for entry in entries:
        if not isinstance(entry, dict) or required - entry.keys():
            raise ValueError("Incomplete course entry")
        if type(entry["order"]) is not int or entry["order"] < 1:
            raise ValueError("Course numbers must be positive integers")
        if entry["track"] not in {"programme", "errors"}:
            raise ValueError("Unknown course track")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", entry["lesson_id"]):
            raise ValueError("Invalid stable lesson ID")
        if not re.fullmatch(r"[PES][0-9]{2}", entry["legacy_id"]):
            raise ValueError("Invalid historical alias")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", entry["delivery_slug"]):
            raise ValueError("Invalid delivery slug")
        if type(entry["requires_narration"]) is not bool:
            raise ValueError("Narration requirements must be explicit booleans")
        if not isinstance(entry["prerequisites"], list):
            raise ValueError("Prerequisites must be a list of stable lesson IDs")
        if len(entry["prerequisites"]) != len(set(entry["prerequisites"])):
            raise ValueError("Duplicate prerequisite")
        if not all(isinstance(entry[k], str) and entry[k].strip()
                   for k in ("module", "title", "scene_class", "coverage", "status")):
            raise ValueError("Empty course metadata")
    entries = sorted(entries, key=lambda e: e["order"])
    if [e["order"] for e in entries] != list(range(1, len(entries) + 1)):
        raise ValueError("Global numbering must be unique and contiguous; no track reset")
    for key in ("lesson_id", "legacy_id", "scene_file", "scene_class", "delivery_slug"):
        if len({e[key] for e in entries}) != len(entries):
            raise ValueError(f"Duplicate {key}")
    counts = dict(Counter(e["track"] for e in entries))
    if counts != data.get("expected_counts"):
        raise ValueError(f"Course count mismatch: {counts}")
    if [e["track"] for e in entries] != sorted((e["track"] for e in entries),
                                               key=lambda t: t != "programme"):
        raise ValueError("The common-error supplement follows the main programme")
    by_id = {e["lesson_id"]: e for e in entries}
    for entry in entries:
        for dependency in entry["prerequisites"]:
            if dependency not in by_id or by_id[dependency]["order"] >= entry["order"]:
                raise ValueError(f"Unknown, cyclic or forward prerequisite: {entry['lesson_id']} -> {dependency}")
        source = (root / entry["scene_file"]).resolve()
        if not source.is_relative_to((root / "scenes").resolve()) or not source.is_file():
            raise ValueError(f"Missing or unsafe course source: {entry['scene_file']}")
        prefix = f"{entry['order']:02d}_"
        if not source.parent.name.startswith(prefix) or source.name != source.parent.name + "_scene.py":
            raise ValueError(f"Source/directory/global-number mismatch: {source.name}")
        tree = ast.parse(source.read_text(encoding="utf-8"))
        classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
        if classes.count(entry["scene_class"]) != 1:
            raise ValueError(f"Public class missing or repeated: {entry['scene_class']}")
    if check_inventory:
        actual = {p.resolve() for p in (root / "scenes").rglob("*_scene.py")
                  if "identite_visuelle" not in p.parts}
        registered = {(root / e["scene_file"]).resolve() for e in entries}
        if actual != registered:
            raise ValueError(f"Unregistered or missing course scenes: {sorted(str(p) for p in actual ^ registered)}")
    return data, entries


def delivery_name(entry: dict[str, Any]) -> str:
    return f"{entry['order']:02d}_{entry['delivery_slug']}"


def resolve(selector: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    matches = [e for e in entries if selector in
               {e["lesson_id"], e["legacy_id"], e["scene_class"], str(e["order"]), f"{e['order']:02d}"}]
    if len(matches) != 1:
        raise ValueError(f"Unknown or ambiguous course selection: {selector!r}")
    return matches[0]


def resolve_scene_path(value: str, *, root: Path = ROOT) -> str:
    """Translate only exact historical paths. Never guess by a numeric prefix."""
    path = Path(value)
    absolute = path.resolve() if path.is_absolute() else (root / path).resolve()
    try:
        relative = absolute.relative_to(root.resolve()).as_posix()
    except ValueError:
        return value
    migration = root / "curriculum/numbering_migration.json"
    if migration.is_file():
        for entry in json.loads(migration.read_text(encoding="utf-8"))["entries"]:
            if relative == entry["old_scene_file"]:
                return entry["scene_file"]
    return relative


def scene_entry(value: str) -> dict[str, Any] | None:
    path = resolve_scene_path(value)
    _, entries = load_catalog()
    return next((e for e in entries if e["scene_file"] == path), None)


def write_indexes(root: Path = ROOT) -> None:
    _, entries = load_catalog(root / "curriculum/programme_principal_fr.yaml", root=root)
    lines = ["# Numérotation globale des vidéos de cours", "",
             "Source unique : `programme_principal_fr.yaml`. Fichier généré par",
             "`python tools/course_catalog.py --write-indexes` ; ne pas modifier les tableaux à la main.", "",
             "Les numéros 01–37 suivent le syllabus. Les compléments sur les erreurs fréquentes",
             "continuent de 38 à 43, sans recommencer à 01. L'identité visuelle et les films",
             "promotionnels ne sont pas des leçons de cours. Les anciens codes P/E/S sont",
             "des alias historiques conservés pour retrouver les audits, pas des numéros actuels.", "",
             "L'ordre du cours ne certifie pas une vidéo : source, rendu, examen visuel et",
             "écoute restent des états distincts. Les dix nouvelles leçons restent à finaliser.", "",
             "| No global | Ancien code | Module | Leçon |", "|---:|---|---|---|"]
    for e in entries:
        lines.append(f"| {e['order']:02d} | {e['legacy_id']} | {e['module']} | [{e['title']}](../{e['scene_file']}) |")
    (root / "curriculum/NUMBERING.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    mapping = json.loads((root / "curriculum/numbering_migration.json").read_text(encoding="utf-8"))
    lines = ["# Correspondance historique des sources", "",
             f"État antérieur : `{mapping['source_commit']}`. Les rapports datés ne sont pas réécrits.",
             "Les classes publiques restent inchangées. Un numéro seul issu d'un ancien rapport",
             "doit être interprété dans son ancien contexte P/E/S, jamais comme le numéro global actuel.", "",
             "| Alias | Ancien chemin | Numéro global | Chemin actuel |", "|---|---|---:|---|"]
    for e in mapping["entries"]:
        lines.append(f"| {e['legacy_id']} | `{e['old_scene_file']}` | {e['order']:02d} | [{e['scene_file']}](../{e['scene_file']}) |")
    (root / "curriculum/LEGACY_NUMBERING.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    import csv
    with (root / "curriculum/playlist.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["global_number", "lesson_id", "legacy_id", "track", "module", "title", "scene_file", "scene_class", "delivery_name", "status"])
        for e in entries:
            writer.writerow([e["order"], e["lesson_id"], e["legacy_id"], e["track"], e["module"], e["title"], e["scene_file"], e["scene_class"], delivery_name(e), e["status"]])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("check", "resolve-path", "artifact-name", "route"), default="check")
    parser.add_argument("value", nargs="?")
    parser.add_argument("--write-indexes", action="store_true")
    args = parser.parse_args()
    if args.write_indexes:
        write_indexes()
        return 0
    if args.command == "check":
        _, entries = load_catalog()
        print(f"Validated {len(entries)} globally numbered course videos")
        return 0
    if not args.value:
        parser.error("a path is required")
    if args.command == "resolve-path":
        print(resolve_scene_path(args.value))
        return 0
    entry = scene_entry(args.value)
    if args.command == "artifact-name":
        print(delivery_name(entry) if entry else Path(args.value).parent.name)
        return 0
    if entry is None:
        return 1
    print("2 - Erreurs fréquentes" if entry["track"] == "errors" else "1 - Programme principal/" + entry["module"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

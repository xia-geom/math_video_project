"""Global numbering and its consumers: no renderer or cloud account required."""
from __future__ import annotations

import copy
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.render_curriculum import read_manifest, select_entries
from scripts.render_syllabus_expansion import read_candidates, select_candidates
from tools.course_catalog import (
    MANIFEST, ROOT, delivery_name, load_catalog, resolve, resolve_scene_path, write_indexes,
)
from tools.video_audit.paths import canonical_video_path


@pytest.fixture(scope="module")
def catalogue():
    return load_catalog()


def test_all_course_sources_have_unique_contiguous_global_numbers(catalogue):
    data, rows = catalogue
    assert data["expected_counts"] == {"programme": 37, "errors": 6}
    assert [e["order"] for e in rows] == list(range(1, 44))
    assert len(list((ROOT / "scenes").rglob("*_scene.py"))) == 44
    assert all(f"{e['order']:02d}_" in e["scene_file"] for e in rows)
    assert {e["order"] for e in rows if e["track"] == "errors"} == set(range(38, 44))


@pytest.mark.parametrize("selector,number", [("P04", 5), ("P25", 35), ("P26", 36),
    ("P27", 37), ("S02", 15), ("S05", 29), ("S06", 28), ("E02", 39), ("43", 43)])
def test_identity_and_display_number_are_separate(catalogue, selector, number):
    assert resolve(selector, catalogue[1])["order"] == number


def test_new_lessons_are_in_their_modules_and_prerequisites_precede_them(catalogue):
    _, rows = catalogue
    by_id = {e["lesson_id"]: e for e in rows}
    for e in rows:
        assert all(by_id[p]["order"] < e["order"] for p in e["prerequisites"])
    assert resolve("S06", rows)["order"] < resolve("S05", rows)["order"] < resolve("S07", rows)["order"]
    triangle = resolve("S08", rows)
    assert "pythagore_par_les_aires" not in triangle["prerequisites"]
    assert "pythagore_par_les_aires" in triangle["related_lessons"]
    assert triangle["assumed_knowledge"]


@pytest.mark.parametrize("damage", ["duplicate_number", "gap", "duplicate_id", "prefix", "class", "escape", "forward", "self", "count", "boolean"])
def test_catalogue_rejects_structural_damage(catalogue, tmp_path, damage):
    data = copy.deepcopy(catalogue[0])
    rows = data["entries"]
    if damage == "duplicate_number": rows[1]["order"] = rows[0]["order"]
    elif damage == "gap": rows[-1]["order"] += 1
    elif damage == "duplicate_id": rows[1]["lesson_id"] = rows[0]["lesson_id"]
    elif damage == "prefix":
        rows[0]["scene_file"], rows[1]["scene_file"] = rows[1]["scene_file"], rows[0]["scene_file"]
    elif damage == "class": rows[0]["scene_class"] = "MissingPublicClass"
    elif damage == "escape": rows[0]["scene_file"] = "../outside.py"
    elif damage == "forward": rows[0]["prerequisites"] = [rows[-1]["lesson_id"]]
    elif damage == "self": rows[0]["prerequisites"] = [rows[0]["lesson_id"]]
    elif damage == "count": data["expected_counts"]["programme"] -= 1
    elif damage == "boolean": rows[0]["requires_narration"] = "false"
    path = tmp_path / "broken.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True))
    with pytest.raises(ValueError):
        load_catalog(path)


def test_exact_legacy_paths_disambiguate_old_duplicate_numbers(catalogue):
    old_circle = "scenes/geometrie_fr/15_aire_du_cercle_fr/15_aire_du_cercle_fr_scene.py"
    old_counting = "scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py"
    assert resolve_scene_path(old_circle) == resolve("P25", catalogue[1])["scene_file"]
    assert resolve_scene_path(old_counting) == resolve("P15", catalogue[1])["scene_file"]
    assert resolve_scene_path("scenes/unknown/15_unknown_scene.py") == "scenes/unknown/15_unknown_scene.py"


def test_every_migration_entry_preserves_its_public_class(catalogue):
    migration = json.loads((ROOT / "curriculum/numbering_migration.json").read_text())
    assert migration["historical_reports_rewritten"] is False
    assert len(migration["entries"]) == len(catalogue[1])
    for old in migration["entries"]:
        current = resolve(old["lesson_id"], catalogue[1])
        assert old["scene_class"] == current["scene_class"]
        assert old["scene_file"] == current["scene_file"]
        assert re.fullmatch(r"[0-9a-f]{64}", old["source_sha256_before"])
        if old["old_scene_file"] != current["scene_file"]:
            assert not (ROOT / old["old_scene_file"]).exists()


def test_candidate_scope_cannot_duplicate_the_catalogue(catalogue):
    scope, candidates = read_candidates()
    assert "entries" not in scope
    assert len(candidates) == 10
    assert all(c["scene_file"] == resolve(c["lesson_id"], catalogue[1])["scene_file"] for c in candidates)
    assert [e["id"] for e in select_candidates(candidates, "04,15")] == ["S01", "S02"]
    assert [e["id"] for e in select_candidates(candidates, "S02,S01")] == ["S01", "S02"]
    with pytest.raises(ValueError): select_candidates(candidates, "01")


def test_delivery_names_and_preview_paths_agree_for_all_43(catalogue):
    _, entries = read_manifest(MANIFEST)
    for entry, row in zip(entries, catalogue[1]):
        assert entry.delivery_name == entry.artifact_slug == delivery_name(row)
        assert entry.rendered_video("ql") == canonical_video_path(ROOT, Path(entry.scene_file), "ql")
        assert entry.source_video == canonical_video_path(ROOT, Path(entry.scene_file))
        assert entry.requires_narration and entry.is_production_lesson
        assert entry.rendered_video("ql") != entry.source_video


def test_error_selection_uses_global_numbers_only():
    _, entries = read_manifest(MANIFEST)
    assert [e.legacy_id for e in select_entries(entries, track="errors", orders={39})] == ["E02"]
    with pytest.raises(ValueError): select_entries(entries, track="errors", orders={2})
    with pytest.raises(ValueError): select_entries(entries, track="all", orders={99})


def test_generated_indexes_are_current_and_cover_the_whole_course(catalogue):
    names = ["NUMBERING.md", "LEGACY_NUMBERING.md", "playlist.csv"]
    before = {name: (ROOT / "curriculum" / name).read_bytes() for name in names}
    write_indexes()
    assert before == {name: (ROOT / "curriculum" / name).read_bytes() for name in names}
    with (ROOT / "curriculum/playlist.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert [int(row["global_number"]) for row in rows] == list(range(1, 44))


def test_audit_scope_is_not_a_stale_numeric_subset(catalogue):
    from scripts.teaching_revision.review import entries
    assert {e["lesson_id"] for e in entries()} == {e["lesson_id"] for e in catalogue[1]}
    text = (ROOT / ".github/workflows/smoke.yml").read_text()
    assert "fromJSON(needs.catalog.outputs.matrix)" in text
    assert "load_catalog" in text
    assert "include:\n          - file:" not in text


def test_drive_routing_follows_manifest_not_source_category(catalogue):
    entry = resolve("P13", catalogue[1])
    command = [sys.executable, str(ROOT / "tools/course_catalog.py"), "route", entry["scene_file"]]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    assert result.stdout.strip() == "1 - Programme principal/02 - Fonctions et graphiques"
    entry = resolve("E06", catalogue[1])
    command[-1] = entry["scene_file"]
    assert subprocess.check_output(command, text=True).strip() == "2 - Erreurs fréquentes"


def test_authored_triangle_formula_and_spoken_total_agree(catalogue):
    source = (ROOT / resolve("S09", catalogue[1])["scene_file"]).read_text()
    assert r"A+B+C=180^\circ" in source
    assert "cent quatre-vingts degrés" in source
    assert "cent quatre-vingt-dix degrés" not in source
    assert r"c^2=a^2+b^2-2ab\cos C" in source


def test_authored_domain_and_branch_guards_are_visible(catalogue):
    rational = (ROOT / resolve("S02", catalogue[1])["scene_file"]).read_text()
    inverse = (ROOT / resolve("S10", catalogue[1])["scene_file"]).read_text()
    assert r"g(x)=\frac{x^2-1}{x-1}=x+1\quad(x\ne1)" in rational
    assert r"\arcsin:[-1,1]\longrightarrow[-\pi/2,\pi/2]" in inverse
    assert r"\arcsin(\sin\theta)=\theta\qquad(-\pi/2\le\theta\le\pi/2)" in inverse


def test_editable_install_backend_is_real():
    import tomllib
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert data["build-system"]["build-backend"] == "setuptools.build_meta"
    assert data["tool"]["setuptools"]["packages"]["find"]["include"] == ["tools*"]

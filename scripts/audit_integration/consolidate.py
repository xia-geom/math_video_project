"""Consolidate selected September audit branches without touching main.

Preparation is restricted to integration/audits-2026-09-17. Verification checks
the immutable integration snapshot, permitting intentional future source edits.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REPORT = Path("reports/audit_consolidation/2026-09-17")
BASE = "0c4556ab07e8ae700c1556148374a83c0808cef1"
BRANCH = "integration/audits-2026-09-17"
REPO = "xia-geom/math_video_project"
SOURCES = {
    "audit-video-visual-2026-09": "aed409ea4c1e8e450643f5cfed47053cd22ef31f",
    "audit-video-visual-evidence-2026-09": "dd0fb52dcb397d1739bcf152b338a7cfe84407d0",
    "audit-video-visual-evidence-final": "dd0fb52dcb397d1739bcf152b338a7cfe84407d0",
    "audit-video-visual-evidence-merge": "dd0fb52dcb397d1739bcf152b338a7cfe84407d0",
    "audit-video-visual-evidence-pr": "dd0fb52dcb397d1739bcf152b338a7cfe84407d0",
    "audit-video-visual-remainder-2026-09": "10abeb40b4ee98e7e990ebd28e80584a634f6d3d",
    "fix-video-visual-our-scope-2026-09-2": "55f0ca64f741ac542132395e1c294bf5f0c29131",
    "fix-video-visual-our-scope-2026-09-work": "55f0ca64f741ac542132395e1c294bf5f0c29131",
    "fix-video-visual-our-scope-2026-09-work2": "55f0ca64f741ac542132395e1c294bf5f0c29131",
    "fix-video-visual-our-scope-2026-09-final": "678ffaa6519b2c15ed10d69ae36935acd42f5ed0",
    "fix-video-visual-our-scope-2026-09-run": "678ffaa6519b2c15ed10d69ae36935acd42f5ed0",
    "fix-video-visual-our-scope-2026-09-implementation": "ca7ede74ca589b9d023710d91fbc51d10552fc88",
    "fix-video-visual-our-scope-2026-09": "950d8095e7064ecfbafcf75bc8da921273c5b0f1",
    "fix-video-visual-p05-p20-2026-09": "86ce0f74114fb4dc7d30fb8c5cc7c61e90b7dadb",
    "fix/uqam-video-audit-2026-09-14": "095697e5f5de550795c7d18879f85fa5163fe81c",
}
ORDER = [
    "audit-video-visual-2026-09",
    "fix-video-visual-our-scope-2026-09-implementation",
    "fix-video-visual-our-scope-2026-09",
    "fix-video-visual-p05-p20-2026-09",
    "fix/uqam-video-audit-2026-09-14",
]


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", *args], cwd=ROOT, check=False, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode:
        print(result.stdout, result.stderr, flush=True)
        result.check_returncode()
    return result


def write(path: Path, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def changed(sha: str, prefix: str = "") -> list[str]:
    return git("diff", "--name-only", BASE, sha, "--", prefix or ".").stdout.splitlines()


def authority() -> dict[str, dict[str, str]]:
    result = {}
    for branch in (ORDER[2], ORDER[3]):
        sha = SOURCES[branch]
        for path in changed(sha, "scenes"):
            if path in result:
                raise RuntimeError(f"Canonical ownership overlaps: {path}")
            result[path] = {"branch": branch, "commit": sha,
                            "blob": git("rev-parse", f"{sha}:{path}").stdout.strip()}
    unowned = set(changed(SOURCES[ORDER[1]], "scenes")) - set(result)
    if unowned:
        raise RuntimeError(f"Implementation-only source requires manual review: {sorted(unowned)}")
    return result


def preserve_statuses() -> None:
    for branch in ORDER[:-1]:
        path = "reports/video_audits/phase2_visual_2026-09/MASTER_STATUS.md"
        content = git("show", f"{SOURCES[branch]}:{path}", check=False)
        if content.returncode == 0:
            write(REPORT / "source_status" / f"{branch}.md", content.stdout)


def verify() -> None:
    record = json.loads((ROOT / REPORT / "integration.json").read_text())
    snapshot = git("log", "--diff-filter=A", "--format=%H", "--", str(REPORT / "integration.json")).stdout.splitlines()[-1]
    for branch, sha in SOURCES.items():
        git("merge-base", "--is-ancestor", sha, snapshot)
    git("merge-base", "--is-ancestor", snapshot, "HEAD")
    for path, source in record["canonical_scene_sources"].items():
        actual = git("rev-parse", f"{snapshot}:{path}").stdout.strip()
        if actual != source["blob"]:
            raise RuntimeError(f"Merged scene differs from its reviewed source: {path}")
    uqam = SOURCES[ORDER[-1]]
    for path in changed(uqam):
        if path == ".github/workflows/uqam-revision.yml":
            continue
        if git("rev-parse", f"{uqam}:{path}").stdout != git("rev-parse", f"{snapshot}:{path}").stdout:
            raise RuntimeError(f"UQAM revision not preserved exactly: {path}")
    for path in git("ls-tree", "-r", "--name-only", BASE).stdout.splitlines():
        if path.startswith(("books/", "textbooks/")) or path.endswith("program_data.py"):
            if git("rev-parse", f"{BASE}:{path}").stdout != git("rev-parse", f"{snapshot}:{path}").stdout:
                raise RuntimeError(f"Unrelated/historical content changed: {path}")
    check = git("diff", "--check", BASE, snapshot, check=False)
    if check.returncode:
        # Historical records and reviewed source stay byte-for-byte intact.
        # Their whitespace is logged; conflict markers or other errors fail.
        warnings = [line for line in check.stdout.splitlines() if line and not line.startswith("+")]
        pattern = r"^.+?:[0-9]+: (trailing whitespace|new blank line at EOF)\.$"
        if check.returncode != 2 or not warnings or any(not re.match(pattern, line) for line in warnings):
            raise RuntimeError("Diff validation failed: " + check.stdout + check.stderr)
        print("Preserved historical whitespace warnings:\n" + check.stdout, flush=True)
    git("diff", "--check", BASE, snapshot, "--", "scripts/audit_integration", ".github/workflows/audit-integration.yml", ".gitignore", "reports/AUDIT_INDEX.md")
    if git("diff", "--name-only", "--diff-filter=U").stdout:
        raise RuntimeError("Unresolved conflicts remain")
    for path in git("diff", "--name-only", "--diff-filter=A", BASE, snapshot).stdout.splitlines():
        if path.lower().endswith((".mp4", ".wav", ".ttf", ".otf")):
            raise RuntimeError(f"Unexpected generated media/font added: {path}")
    print(f"VERIFIED {len(SOURCES)} audit branch tips; {len(record['canonical_scene_sources'])} canonical scenes; exact UQAM source preservation in snapshot {snapshot}.", flush=True)


def prepare() -> None:
    if git("branch", "--show-current").stdout.strip() != BRANCH:
        raise RuntimeError("Preparation is restricted to the named integration branch")
    if (ROOT / REPORT / "integration.json").exists():
        verify()
        print("Already consolidated; no source mutation.", flush=True)
        return
    if git("rev-parse", "origin/main").stdout.strip() != BASE:
        raise RuntimeError("Main moved since inventory; refresh the merge plan")
    for branch, sha in SOURCES.items():
        if git("rev-parse", f"origin/{branch}").stdout.strip() != sha:
            raise RuntimeError(f"Audit branch moved since inventory: {branch}")
    if git("status", "--porcelain").stdout:
        raise RuntimeError("Preparation requires a clean checkout")
    owners = authority()
    conflicts_record = []
    for index, branch in enumerate(ORDER, 1):
        sha = SOURCES[branch]
        if git("merge-base", "--is-ancestor", sha, "HEAD", check=False).returncode == 0:
            continue
        merged = git("merge", "--no-ff", "--no-commit", sha, check=False)
        print(merged.stdout, merged.stderr, flush=True)
        conflicts = git("diff", "--name-only", "--diff-filter=U").stdout.splitlines()
        if merged.returncode and not conflicts:
            raise RuntimeError(f"Merge failed without resolvable conflicts: {branch}")
        for path in conflicts:
            if path in owners:
                git("restore", "--source", owners[path]["commit"], "--staged", "--worktree", "--", path)
                policy = f"canonical scope: {owners[path]['branch']}"
            elif path.startswith("reports/") and path.endswith(".md"):
                ours = git("show", f":2:{path}").stdout
                theirs = git("show", f":3:{path}").stdout
                stem = REPORT / "conflicting_records" / f"merge_{index:02d}" / Path(path).name
                write(stem.with_name(stem.stem + "_previous.md"), ours)
                write(stem.with_name(stem.stem + "_incoming.md"), theirs)
                if Path(path).name == "MASTER_STATUS.md":
                    write(Path(path), theirs)
                else:
                    write(Path(path), f"# Preserved independent audit records: {Path(path).stem}\n\n"
                          "These are historical observations, not a combined release approval. "
                          "Both source records are retained below; their status and scope may differ.\n\n"
                          f"## Previously integrated audit record\n\n{ours}\n\n"
                          f"## Audit record from `{branch}` ({sha[:12]})\n\n{theirs}\n")
                git("add", "--", path, str(REPORT))
                policy = "both original texts archived; both retained in capsule reports"
            else:
                raise RuntimeError(f"Unexpected conflict requires manual resolution: {path}")
            conflicts_record.append({"merge_branch": branch, "path": path, "policy": policy})
        git("commit", "-m", f"merge(audits): {index}/5 integrate {branch}")
        print(f"MERGED {branch} {sha}", flush=True)
    for path, source in owners.items():
        git("restore", "--source", source["commit"], "--staged", "--worktree", "--", path)
    preserve_statuses()
    retired = []
    for path in git("diff", "--name-only", "--diff-filter=A", BASE, "HEAD", "--", ".github/workflows").stdout.splitlines():
        if Path(path).name in {"audit-integration.yml", "uqam-revision.yml"}:
            continue
        destination = REPORT / "legacy_workflows" / Path(path).name
        (ROOT / destination).parent.mkdir(parents=True, exist_ok=True)
        git("mv", path, str(destination))
        retired.append({"original": path, "archive": str(destination)})
    uqam_workflow = ROOT / ".github/workflows/uqam-revision.yml"
    text = uqam_workflow.read_text()
    start, end = text.index("on:\n"), text.index("\nconcurrency:")
    text = text[:start] + "on:\n  workflow_dispatch:\n" + text[end:]
    for name in ("Check failure propagation and invalidate the first erroneous badge",
                 "Apply guarded source migration and reviewed test snapshots"):
        marker = f"      - name: {name}\n"
        if marker in text:
            begin = text.index(marker)
            stop = text.find("\n      - ", begin + len(marker))
            if stop < 0:
                raise RuntimeError(f"Cannot delimit obsolete workflow step: {name}")
            text = text[:begin] + text[stop + 1:]
    text = text.replace("      contents: write", "      contents: read")
    uqam_workflow.write_text(text)
    record = {"schema": 1, "baseline_main": BASE, "repository": REPO,
              "source_branches": SOURCES, "ordered_merge_heads": ORDER,
              "canonical_scene_sources": owners, "conflict_resolutions": conflicts_record,
              "retired_workflows": retired,
              "release_status": "Source integration only; narration/full production review remains pending"}
    write(REPORT / "integration.json", json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    table = "\n".join(f"| `{branch}` | `{sha}` |" for branch, sha in SOURCES.items())
    run_url = f"https://github.com/{REPO}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
    write(REPORT / "README.md", f"""# Audit integration — September 17, 2026

All 15 inventoried audit branch tips are preserved as ancestors of this integration.
Five ordered merge commits incorporate independent work; duplicate branch pointers
and intermediate branches do not need separate content merges. Original remote
branches are retained. No force-push, textbook update, or video publication is part
of this operation.

## Current source ownership

- P01–P04, P21–P27, E01–E06: `fix-video-visual-our-scope-2026-09`.
- P05–P20: `fix-video-visual-p05-p20-2026-09`, including its later refinements.
- UQAM short/long films: the exact source from PR #2, except workflow cleanup.

Every changed teaching scene must be byte-identical to its designated source in
the integration snapshot. Future intentional edits remain possible. The earlier
implementation branch stays in history without overwriting newer scoped fixes.
Conflicting capsule reports preserve both original texts. Original master reports
are in `source_status/`; conflict originals are in `conflicting_records/`.
No historical observation is silently upgraded to a pass.

## Navigation and automation

[Repository audit index](../../AUDIT_INDEX.md) is the entrypoint.
One-off visual patch/render workflows were moved unchanged into `legacy_workflows/`.
Their old branch assumptions must not run on main. The UQAM revision workflow is
manual-only; completed migration and stale-badge steps were removed. It retains
testing/rendering and separate narration gates. Preparation is strictly limited to
`{BRANCH}`, never main.

## Validation and remaining gates

[Integration validation run]({run_url}) records the tested commit, compilation,
per-blob preservation, ancestry and JUnit results. Consult the actual run outcome;
this document is not itself evidence of a pass. Historical whitespace is reported
without altering imported records; newly authored integration files are checked
strictly and conflict markers always fail.

No new narrated film is certified. Speech credentials, listening, real subtitle
synchronization, final-resolution review and release approval remain separate.

## Source branch inventory

| Branch | Inventoried head |
|---|---|
{table}
""")
    write(REPORT / "legacy_workflows/README.md", "# Historical audit workflows\n\nThese files are retained verbatim for provenance, outside GitHub's active workflow directory. They contain completed one-off migrations or hard-coded audit branches. Use the active Audit integration checks or manually dispatch UQAM revision instead.\n")
    write(Path("reports/AUDIT_INDEX.md"), """# Audit index

## Integrated source and history

[September 17 branch consolidation](audit_consolidation/2026-09-17/README.md)
contains the branch inventory, source ownership, conflict policy and validation link.
Its [machine-readable record](audit_consolidation/2026-09-17/integration.json)
records exact source blobs and retired workflows.

## Teaching-video visual audits

[Capsule reports and evidence](video_audits/phase2_visual_2026-09/README.md)
cover the teaching videos. [Consolidated scope status](video_audits/phase2_visual_2026-09/MASTER_STATUS.md)
links the separate original records. Historical reports describe their own audited
revisions and may precede later source fixes.

## UQAM recruitment and programme-overview videos

[Revision plan](uqam_video_revision/2026-09-14/PLAN.md), course provenance and
source corrections are integrated from PR #2. The existing validated visual-only
run is 34929376037; real narration and full production approval remain pending.
Source merged does not mean video released.
""")
    write(Path("reports/video_audits/phase2_visual_2026-09/MASTER_STATUS.md"), """# Visual audit — consolidated scope index

This index supersedes competing branch-local master indexes, not their evidence.
All original master reports are preserved under
[consolidation source status](../../audit_consolidation/2026-09-17/source_status/).

| Scope | Integrated source | Status evidence |
|---|---|---|
| P01–P04, P21–P27, E01–E06 | `fix-video-visual-our-scope-2026-09` | [Original post-fix status](../../audit_consolidation/2026-09-17/source_status/fix-video-visual-our-scope-2026-09.md) |
| P05–P20 | `fix-video-visual-p05-p20-2026-09` | [Original audit records](../../audit_consolidation/2026-09-17/source_status/audit-video-visual-2026-09.md); later fixes retained at branch head `86ce0f74114fb4dc7d30fb8c5cc7c61e90b7dadb` |

Capsule reports retain historical findings. Where independent records conflicted,
both are retained with source labels. This merge does not newly certify narration,
mathematics, pedagogy, final-resolution legibility or production release.
See [the audit index](../../AUDIT_INDEX.md) for all workstreams and validation.
""")
    git("add", "-A")
    git("diff", "--cached", "--check")
    git("commit", "-m", "chore(audits): index merged work and archive completed one-off workflows")
    verify()
    print("INTEGRATION_COMMIT", git("rev-parse", "HEAD").stdout.strip(), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    prepare() if args.prepare else verify()

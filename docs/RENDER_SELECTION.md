# Selecting smoke renders

The smoke workflow keeps global lint and compilation as prerequisites. Its
catalogue job selects renders using the same conservative dependency closure as
the production review ledger. This uses stable lesson IDs; it does not introduce
another course registry.

| Change | Render scope |
| --- | --- |
| Only documented reference/roadmap Markdown files | No lesson render |
| One scene source | That scene and any lessons importing it |
| Shared layout, voice, branding or other imported inputs | Every dependent lesson |
| Catalogue or shared teaching profile | All affected catalogue lessons |
| Unknown path, missing Git comparison, removed dependency or parse failure | Entire catalogue |
| Manual smoke dispatch | Entire catalogue |

The Git comparison uses exact object IDs from the event payload, a merge base for
pull requests, and both sides of renames. It never interpolates branch names into
a shell command. Checkouts retain full history in the selection job. Selection
counts and the reason appear in the job summary; an empty selection skips only
the render job. Existing dedicated teaching review workflows retain their
explicit scope and full-course manual options.

Inspect a local selection without rendering:

```sh
python scripts/select_affected_lessons.py --changed-path docs/DEVELOPMENT.md
python scripts/select_affected_lessons.py --changed-path tools/teaching_layout.py
python scripts/select_affected_lessons.py --full
python -m pytest -q tests/test_affected_lessons.py
```

[Measured Linux runs](../reports/repo_development/2026-11-06/ci_baseline.json)
show that the three sampled smoke runs stopped at global Ruff lint. Rendering
was skipped, so these runs provide no smoke-render duration. Separate teaching
and syllabus jobs did render successfully. The selection change reduces
unnecessary render scope after prerequisites pass; it does not clear the global
lint backlog or establish audiovisual approval.

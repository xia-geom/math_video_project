# Teaching-scene instructions

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

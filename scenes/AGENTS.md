# Teaching-scene instructions

Read the root agent guide and [the teaching standard](../docs/TEACHING_STANDARD.md)
before creating or changing a mathematics lesson. In particular, apply its
**Lessons retained from the visual audit** section: those are production rules,
not merely historical findings.

For syllabus additions, consult [curriculum/README.md](../curriculum/README.md)
and the expansion manifest. Preserve existing scene classes, delivery slugs and
lesson orders. A new source or successful silent render is not a released video.

Reuse `TeachingScene`, `panel`, the shared narration adapter and the single
`play_uqam_intro` opening. Keep full-size readable text, clear previous cases,
and use sequential fades for unrelated text rather than glyph morphing.
Use a geometric transform only when the correspondence itself teaches an idea.

Keep source edits within the assigned lessons. Read active pull requests before
touching shared files; do not replay archived patch scripts or change another
branch's scenes. Run the focused tests and a low-quality preview for new scenes.
Report syntax, mathematical examples, rendering, visual inspection and listening
separately. Store generated media outside source Git; do not publish or mirror
previews as a side effect of adding a lesson.

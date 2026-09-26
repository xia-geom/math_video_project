# Worked examples for the ten syllabus additions

These French explanations expand the ten new lessons rather than extending them
with empty holds. Each lesson has two additional worked examples with five
successive steps. Original examples, diagrams, public scene classes and global
course numbers are preserved. The YAML filename is the stable lesson identity,
not another display number; the global catalogue remains the only order source.

`tools/expanded_teaching.py` keeps the premise visible while replacing one
calculation card at a time. Unrelated formulas use sequential fades, not glyph
morphs. Standalone results passed to `new_page` receive their own panel; diagram
labels keep their geometric placement. The content and its border are revealed
together. Actual panel containment is checked during animation updates and at
page/explanation boundaries, not just when a box is initially created.

Authoring rules: preserve readable font sizes, split long formulas into steps,
and split overcrowded pages. Never stretch a whole film or add silence merely
to meet a duration. `reading_seconds` is local time for a specific mathematical
step, not a global duration target. Real speech still controls narrated pacing;
the existing explicit pause after the final question remains.

Run `python -m pytest tests/test_expanded_teaching.py -q` in the existing Manim
environment. Then run `python scripts/recheck_ten_lessons.py --output
review_artifacts/ten_lessons_review --quality qh` for fresh silent 1080p60 reviews.
The output contains exact source hashes, timings, containment counts, encoded
media and stable/transition samples. These checks do not certify narration,
caption synchronization, full human playback or institutional publication.

The additions are authored examples, not transcriptions of the textbook. Course
coverage and optional complex numbers retain the scope of the existing syllabus.

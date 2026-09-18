# Agent entry point

Read [ARCHITECTURE.md](ARCHITECTURE.md) for repository boundaries and the existing
[AGENT.md](AGENT.md) for the detailed production guide. This file makes those
instructions discoverable; it does not replace or rewrite that guide.

For UQAM promotion work, first read [miscellaneous/README.md](miscellaneous/README.md)
and the target project's README. The three films are parallel projects. Preserve
the two existing directories, their renderers, narration profiles and audit history.

Reuse `tools/tts.py` for Manim/Azure narration. Do not embed secrets, substitute
voices silently, or treat a muted preview as a narrated deliverable. Keep generated
media out of new Git commits. The new clip's builder does not publish to Drive or
create a release.

Run the target tests and distinguish syntax checks, real renders, listening,
visual review and institutional approval in the completion report. Do not fix
unrelated baseline CI failures by disabling checks or modifying other projects.

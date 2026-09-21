# Agent entry point

Read [ARCHITECTURE.md](ARCHITECTURE.md) for repository boundaries and the existing
[AGENT.md](AGENT.md) for the detailed production guide. This file makes those
instructions discoverable; it does not replace or rewrite that guide.

For UQAM promotion work, first read [miscellaneous/README.md](miscellaneous/README.md)
and the target project's README. The three films are parallel projects. Preserve
the two existing directories, their renderers, narration profiles and audit history.

For UQAM photography, use the official Salle de presse photo bank as the default
first source and follow [assets/uqam_promo/PHOTO_POLICY.md](assets/uqam_promo/PHOTO_POLICY.md).
Preserve the required source credit, prefer current evergreen imagery, and avoid
street-dominated pavilion views or pandemic-era masked images when a suitable
current UQAM alternative exists.

For the separate English product clip, read
[miscellaneous/conversation_archive_intro_en/README.md](miscellaneous/conversation_archive_intro_en/README.md)
and its `storyboard.json`. It uses invented data and is intentionally silent and
captioned; do not substitute a voice, add institutional branding, or change the
curriculum. Keep target architecture visibly distinct from shipped features.

Reuse `tools/tts.py` for Manim/Azure narration. Do not embed secrets, substitute
voices silently, or treat a muted preview as a narrated deliverable. Keep generated
media out of new Git commits. The new clip's builder does not publish to Drive or
create a release.

Run the target tests and distinguish syntax checks, real renders, listening,
visual review and institutional approval in the completion report. Do not fix
unrelated baseline CI failures by disabling checks or modifying other projects.

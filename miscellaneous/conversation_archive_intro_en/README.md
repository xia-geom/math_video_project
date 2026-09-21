# Conversation Archive — English introduction

A **70-second, silent, captioned product explainer** for [Conversation Archive](https://github.com/xia-geom/conversation-archive). It uses invented Orchard-project examples, not screenshots or personal conversations. This is a separate product clip, not a UQAM advertisement or a curriculum lesson.

**AI agents:** read `storyboard.json` for content, timing, language, and claim status. Keep the storage-architecture beat visibly labeled as a target. The migration described in the owner's local report is not present in the referenced archive commit. Do not turn report-only or planned capabilities into product claims.

## Build

From the repository root, in its Manim environment:

```sh
python3 miscellaneous/conversation_archive_intro_en/build.py --check
python3 -m unittest discover -s miscellaneous/conversation_archive_intro_en -p 'test_*.py' -v
python3 miscellaneous/conversation_archive_intro_en/build.py --output dist/conversation_archive_intro_en/first-preview
```

The default is a 480p/15 fps preview. An explicitly requested final-resolution render uses `--quality qh` (1080p/60 fps), but is still silent and is not automatically approved for publication. Output directories must be new. Existing renders are never overwritten.

The [dedicated Actions workflow](../../.github/workflows/conversation-archive-intro.yml) runs the tests, renders a synthetic preview, checks dimensions/duration/audio state, and uploads the MP4, English SRT, optional narration script, review frames, and render report as an artifact. Open a successful run's **Artifacts** section to obtain them. No release or Drive upload occurs.

## Story

| Time | Message |
| --- | --- |
| 00–07 s | Connect scattered conversations without losing evidence |
| 07–16 s | Preserve original wording, branches, and attribution |
| 16–26 s | Shared context does not mean the same event |
| 26–38 s | Prepare 15 context-rich questions before asking |
| 38–48 s | Reuse scoped, reversible confirmations |
| 48–60 s | Target: structured authority, SQLite retrieval, optional views |
| 60–70 s | Agent-first entry points and the offline demo |

## Files and review boundary

`storyboard.json` is the content source. `conversation_archive_intro_en_scene.py` is the Manim Community scene; `build.py` packages and checks it. `test_intro.py` tests timing, claim labels, subtitles, and preservation behavior.

The builder runs geometric frame checks and captures one review frame per beat. Those checks do not establish a complete visual review. The generated report records measured properties separately from listening, human review, or publication approval. The narration script is text only; no speech was synthesized. For a future narrated edition, reuse `tools/tts.py` and an explicitly configured English voice rather than silently substituting a voice/provider.

Generated media belongs in ignored `dist/` or Actions artifacts, never source Git. Preserve the existing mathematics lessons, curriculum, UQAM films, voices, and delivery destinations.

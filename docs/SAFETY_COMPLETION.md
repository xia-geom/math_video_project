# Safety cleanup result and remaining owner actions

**21 September 2026 — targeted repository-side cleanup completed.** This is not
blanket privacy clearance or a statement that owner-only settings are enabled.

## Completed

PR #16 removed the two financial summaries from the current tree. PR #14's
workflow safeguards were then merged without weakening those exclusions. PR #18
supplied the tested cleanup and prevention tools.

[GitHub Actions run 35654203962](https://github.com/xia-geom/math_video_project/actions/runs/35654203962)
completed an actual, atomic, lease-protected history rewrite:

- 351 commits checked; 152 rewritten; 19 changed writable refs published (18
  branches and one tag). Branch/tag names and all non-billing file paths, modes
  and blobs were preserved at every checked commit and branch/tag tip.
- Two private report paths/two blob versions removed. Zero forbidden report
  blobs remained reachable in the filtered history. Remote writable refs were
  compared with the verified plan after publication.
- Main changed from `1731fa4da653fe2f091accdae6040fb7c95c387a` to
  `3ccbf6ceb37fd16404691f04190793e8fc2eed2c`; later maintenance commits may advance it.
- 24 cleanup/prevention tests passed. The separate private-data and public
  security checks also passed. The existing repository-wide lint backlog is not
  represented as fixed.

The same run inspected readable content in 105 retained artifact archives and
logs from 276 completed runs (8,108 text members). It found **no positive copies**
of the known reports, so **no artifacts or logs were deleted**. It explicitly
excluded 88 expired artifacts, one oversized artifact and ten unavailable/limited
log archives; 12,444 binary/oversized members were outside the text scan. An exact
fingerprint scan does not clear unrelated personal content or binary media.

Verification metadata is retained in artifact `history-publication-record`
(ID 10663756171): publication summary, commit map, exposure scan and Support
request, with no financial report text. ZIP SHA-256:
`bec4242443de0c67c7657073f8e4e35434d767947398923138b626ee6ed7ee70`.

The one-time privileged publication job has now been removed. The remaining
history-cleanup workflow is read-only. The private-data CI check also checks HEAD's
full history so an old-history merge cannot pass merely by deleting the current
report files again.

## Refresh local clones before pushing

Preserve uncommitted edits and local private archives first. Use a fresh full clone;
do not merge old history into the cleaned repository. Reapply only reviewed source
changes. Historical commit IDs/signatures and old-SHA audit links changed; do not
blindly rerun old integration scripts tied to pre-cleanup commits.

The opt-in local pre-push hook checks outgoing history before GitHub receives it.
In a fresh clone with no existing hook setup, activate it with:

```sh
git config --local core.hooksPath .githooks
python3 scripts/check_private_data.py
python3 scripts/check_private_history.py
```

Inspect existing `core.hooksPath` and local hooks before changing an established
checkout. The supplied hook was not installed on the owner's computer by this
session. CI runs after a push; it is not a substitute for local prevention.

## Owner-only GitHub settings — still required

The connected application returned 403 for branch-protection administration.
Required checks, private vulnerability reporting and secret push protection were
**not enabled** through this connection. A prepared helper uses an existing,
owner-authorized GitHub CLI login:

```sh
python3 scripts/enable_safety_settings.py
python3 scripts/enable_safety_settings.py --apply
```

The first command previews without network calls. Apply verifies successful
`private-data-guard` and `public-repository-safeguards` checks on current main, then
creates one additive active ruleset: required PR, strict required checks, no
bypass actors, no force pushes and no branch deletion. Zero required approvals
accommodates a sole maintainer without disabling existing stricter rules. It also
requests private reporting, secret scanning and secret push protection and checks
the returned state. Existing different rulesets are not overwritten; denied calls
remain failures. Never paste a token into a chat or commit it.

Configure protected environments separately before granting additional users
access to cloud credentials. Existing narration remains explicit manual-only on
main, with voice choices unchanged.

## GitHub-held copies — Support action still required

Writable branch/tag cleanup does not purge GitHub-managed PR refs, cached old
views or external clones. The generated Support request records the first changed
commit and 16 affected PR heads, without the financial content. Submit it through
GitHub Support; eligibility and actual cache/server-object removal are for GitHub
to determine. No Support request was submitted and no Support purge is claimed.

Do not repost the financial reports as evidence. Third-party downloads cannot be
guaranteed erased. Photos, fonts, textbook notices and production approval remain
separate matters; no video, voice, original educational asset or license was
changed by this cleanup.

Reference: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

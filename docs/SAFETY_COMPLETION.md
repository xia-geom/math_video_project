# Safety cleanup and owner handoff

The billing reports were removed from main in PR #16; PR #14's workflow safeguards
are now integrated without weakening those exclusions. A clean current tree is
not evidence that old commits, artifacts or clones have been erased.

## Targeted history cleanup

`scripts/cleanup_billing_history.py` defaults to a read-only trial in a disposable
mirror. It inventories all fetched heads, tags and PR refs, removes only known
billing paths/versions and identical renamed copies, and checks every non-billing
file's path, mode and Git blob at every commit and branch/tag tip. It retains a
commit map and sanitized support-request metadata, never private report text.

Publication requires `--publish --expected-main <exact-sha>`. It verifies that all
remote heads/tags still match the captured snapshot and uses one atomic push with
an explicit force-with-lease for each changed ref. Unrelated branches are neither
merged nor discarded. A concurrent update blocks publication. PR-managed refs
are read-only and are not force-pushed.

The one-time workflow publication condition is pinned to the approved initiating
main transition from `35168cdf36858db858cc038b6e9d41a879d9f6bb`. It cannot run on a PR,
an arbitrary later push or a manual invocation. Remove this one-time publisher
after the result is verified. The read-only trial may remain available.

History cleanup changes commit IDs and invalidates old signatures/check links.
Historical audits pinned to previous SHAs retain their documentary context but
must not be rerun blindly. A commit map is evidence of migration, not a new claim
that every old build ran on the new commits.

## Prevent reintroduction before GitHub receives a push

Use a fresh full clone after history cleanup. Preserve uncommitted work privately;
do not merge old history into the clean clone. Port only reviewed code changes.

`python3 scripts/check_private_history.py` checks the history of HEAD without
printing file contents. A pre-push hook is supplied under `.githooks/pre-push`.
On a fresh clone with no existing hooks setup, activate it with:

```sh
git config --local core.hooksPath .githooks
```

Inspect `git config --get core.hooksPath` and existing hooks first on an established
checkout; do not replace another hook configuration unknowingly. Hooks are local
and opt-in; committing a hook file does not install it on every user's machine.
The existing index guard also detects private files that were force-added. CI
runs after a push and cannot itself prevent the initial public exposure.

## Owner-only GitHub settings

The connected GitHub application denied branch-protection administration. No
claim is made that file changes enabled required checks or private reporting.
Run the prepared helper with an existing owner-authorized GitHub CLI login:

```sh
python3 scripts/enable_safety_settings.py
python3 scripts/enable_safety_settings.py --apply
```

The preview makes no network calls. The apply command checks actual passed
GitHub Actions checks on current main, then creates one additive active ruleset:
required PR, required `private-data-guard` and `public-repository-safeguards`, strict
base freshness, no bypass actors, no force pushes and no branch deletion. Zero
required approvals accommodates a sole maintainer; it does not disable existing
stricter protections. It enables private vulnerability reporting, secret scanning
and push protection, then verifies the result. Existing differently configured
rulesets are not overwritten. A denied API call is reported, not bypassed.

These settings need administration permission. Do not paste tokens into a chat or
commit them to the repository. Configure protected environments separately before
allowing any additional cloud-secret users. Current review workflows expose Azure
keys only for explicitly requested manual narration on main.

## GitHub Support and other copies

The cleanup's `support-request.md` records first-changed commits and affected PRs
without financial text. Submit it through GitHub Support after writable refs are
clean; Support decides whether to remove PR references, cached views and orphaned
objects. This process cannot erase third-party clones or downloads. Do not claim
Support has acted before receiving its confirmation.

Old Actions artifact payloads and unsampled logs still need targeted review.
Do not delete all video artifacts blindly: preserve legitimate renders and remove
only identified private copies. The automatic secret scanner is not a semantic
privacy review. No statement here certifies all media licenses or every lesson.

Reference: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

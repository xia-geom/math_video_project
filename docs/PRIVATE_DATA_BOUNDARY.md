# Personal data stays outside the public video repository

Only project code, deliberately public documentation, synthetic test fixtures and
appropriately licensed media belong here. Redacting account IDs does not make a
personal spending report appropriate for this repository.

The financial-report cleanup removes `azure_audit.md` and
`reports/azure_billing_history/INDEX.md` from the current tree. The full billing
folder is ignored, not just its `raw/` subfolder. Keep real records outside this
checkout in a private administrative archive. Existing local-only invoices and
personal files are not read, moved or deleted by this change.

## Prevention

Before publishing a staged change, run from the repository root:

```sh
python3 scripts/check_private_data.py
python3 -m unittest discover -s tests -p 'test_private_data_guard.py' -v
```

The `Private data guard` workflow runs these checks for every pull request and
main push. It rejects known billing paths, local environment/credential files,
private-data directories and SQLite/key files in the Git index. It also rejects
byte-identical copies of the two removed reports under other filenames using
Git blob fingerprints. It prints locations and reasons, not file contents.
Tests use only invented data. No cloud key or paid service is needed.

An ignore rule alone cannot remove already tracked files. This guard checks the
actual Git index, so ignored files added with force are still caught. It is a
narrow guard, not a universal personal-data detector: edited or renamed summaries
and screenshots need content/privacy review. Secret scanning is complementary.

A failed check blocks merging only when repository rules require that check.
Make `private-data-guard` required on `main` and apply the rule to bypass roles
where appropriate. Protect workflow/policy changes through review. A post-push
failure cannot undo a disclosure; local staged checks and review come first.
Do not claim branch protection was enabled by adding this file or workflow.

## Historical removal is a separate, unfinished step

Removing the current files does not purge earlier commits, branches, tags, PR
refs/diffs, logs, artifacts, external forks or downloaded copies. Do not treat a
passing guard as confirmation that historical exposure is resolved.

Before a history rewrite: preserve the reports privately, coordinate a pause in
pushes, inventory affected refs and open PRs, and identify any workflow/release
references to commit hashes. Perform and verify a cleanup in an isolated clone
before explicitly authorizing its publication. GitHub-managed PR refs/caches may
require GitHub Support assistance, subject to their eligibility assessment.
External copies cannot be recalled or guaranteed erased.

Follow GitHub's [sensitive-data removal procedure](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
No force push, remote history rewrite, credential rotation or visibility change
is performed by this containment change. Rotate a credential if evidence shows
it was exposed; the discovery of billing text alone does not prove key exposure.

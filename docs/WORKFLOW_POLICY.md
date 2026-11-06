# Workflow privileges and review

[The policy manifest](../.github/workflow-policy.yaml) classifies every active
workflow and job. [The validator](../scripts/check_workflow_policy.py) discovers
both `.yml` and `.yaml` files and rejects unclassified additions or missing
classified workflows. The public-audit workflow runs it on every pull request.

Run it without rendering or cloud credentials:

```sh
python scripts/check_workflow_policy.py
python -m pytest tests/test_workflow_policy.py tests/test_public_workflow_policy.py -q
```

## Classifications

| Class | Workflows | Privilege boundary |
| --- | --- | --- |
| Read-only checks and previews | `smoke`, `course-numbering`, `syllabus-expansion`, `ten-lesson-recheck`, `teaching-readability`, `private-data-guard`, `public-audit`, `history-cleanup`, `conversation-archive-intro`, `uqam-scoped-lint` | Read-only repository token; no cloud credentials. Public audit additionally reads Actions, issues and PR metadata. |
| Reviews with gated narration | `teaching-revision`, `uqam-revision`, `uqam-ouvertures` | Read-only repository token. Speech credentials occur only in the existing steps guarded by manual dispatch, `main`, and explicit paid selection. Defaults remain silent/unrequested. |
| Existing administrative operations | `audit-integration`, `publish-archive-preview` | Write permissions belong only to the named jobs described below. Other jobs still follow read-only rules. |

`teaching-readability` currently prepares native tooling; its successful execution
does not mean that scenes were validated. UQAM and English preview environments
remain separate from teaching dependencies.

## Administrative exceptions

`audit-integration.verify` can write contents and commit statuses. It has no PR
trigger. Pushes trigger it only on `main` or the named historical integration
branch; manual dispatch remains an explicit maintainer operation. The checkpoint
step additionally requires that exact integration branch and successful preparation,
and pushes only that branch. The status step requires recorded source. The
validator does not permit a second write job or a new token-consuming step merely
because it is in this workflow. A manual dispatch should select reviewed source.

`publish-archive-preview.publish` can write contents and read Actions artifacts.
It depends on the existing checks, excludes PR events, and binds the owner
repository and `main`. It preserves the fixed English preview's artifact ID,
checksum-verification command, release tag, source target and existing-release
early exit. This historical exception does not authorize new film publication.

`history-cleanup.trial` is **read-only**. The owner-approved write job was removed
after its one-time execution. Its current mirror cleanup does not receive a
write token or invoke `--publish`; rerunning the trial cannot authorize a rewrite.

## What the check enforces

The validator checks explicit triggers, reviewed job identities, workflow and
effective job permissions, full commit pins for external Actions, nonpersistent
checkout credentials, bounded timeouts, and the location of secret/token
references. It rejects reusable-workflow credential inheritance. Paid gates are
matched to the existing reviewed expressions; appending an OR condition fails.
Duplicate YAML keys fail instead of hiding a second permissions declaration.

The four existing short/long regression steps may continue long enough to collect
both suites' evidence. Their blocking aggregators remain mandatory. Other job or
step failure suppression fails the policy. Public audit may upload only its
sanitized summary, never its raw scanner reports or the whole temporary directory.

Synthetic regressions cover unclassified files/jobs, privilege escalation,
unpinned Actions, persisted checkout tokens, inherited and misplaced secrets,
paid-default changes, bypassed gates, expanded writes and raw artifact uploads.
Existing smoke, stacked-PR, UQAM export and secret-detector contracts remain tested.

## Review limits

This is a static repository policy check, not a shell interpreter, a review of
every third-party Action, or an account-settings audit. A malicious rewrite of a
shell program can preserve checked strings; reviewers still inspect commands and
called scripts, especially in the two administrative jobs. A passing check does
not establish branch protection, repository/environment approvals, image rights,
human listening or publication approval. Never weaken the policy to conceal an
unrelated test failure.

See [test groups](TESTING.md), [security boundaries](../SECURITY.md) and
[public readiness](PUBLIC_READINESS.md) for the corresponding operational limits.

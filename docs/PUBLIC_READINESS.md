# Public repository readiness

This project is already public. These checks reduce exposure and onboarding risk;
they do not authorize a new video release, change narration, or relicense assets.

## What is already present

The root LICENSE is Apache-2.0. Keep it. The repository also contains institutional
photography, branding, books and historical documents; review their own notices
and permissions separately. Public availability or a source credit alone is not
blanket permission to redistribute everything under the code license.

## Repeatable audit

The `Public repository safeguards` workflow fetches current branches, tags and
pull-request heads, then scans reachable history and current tracked files with
checksum-verified Gitleaks 8.30.1. A Python inventory counts distinct blobs,
credential-like filenames, personal local-path occurrences and non-noreply commit
emails without publishing the matched values. Full-history source is required.

Optional GET-only GitHub sampling examines up to 500 issue/PR bodies, issue
comments and review comments per collection, plus logs from the latest ten
completed runs and artifact metadata. The report lists inaccessible or limited
resources. Raw scanner reports, matched secrets, downloaded logs and API bodies
stay in temporary storage; only a sanitized summary is uploaded for seven days.

Local reproduction, from a full clone with Gitleaks installed:

```sh
python3 -m unittest discover -s tests -p 'test_public_audit.py' -v
python3 scripts/public_audit.py --gitleaks gitleaks --output review_artifacts/public-audit-summary.json
```

Do not commit generated reports containing raw material. A finding requires
private inspection and classification; do not automatically delete historical
files, rotate credentials, or interpret an author's public email as a leaked key.

## Owner-only settings to verify

The inspected baseline had an unprotected `main`. Configure branch/ruleset
protection against force-pushes/deletion and require passing, relevant checks.
Do not require a permanently failing legacy lint check without first fixing it,
and do not disable the check to conceal the backlog. CODEOWNERS requests reviews
but is not enforcement without the corresponding repository rule.

Enable private vulnerability reporting, secret scanning/push protection and
review for external contributors' workflows where available. Check Actions token
permissions and use protected environments for cloud credentials. These settings
are administrative controls; adding this document does not enable them.

## Media and educational material

Keep [UQAM source credits](../assets/uqam_promo/PHOTO_POLICY.md), photographer
notices and existing manual/book restrictions. Before broadly inviting reuse,
record the origin, applicable permission, attribution and intended redistribution
scope for photos, logos, fonts, music, textbooks and rendered media. Unclear
rights remain open; this audit does not infer a license or institutional approval.
Do not redistribute fonts bundled in a machine or tool environment.

## Honest adoption signal

Keep code tests, silent renders, narrated renders, listening review, mathematical
review and institutional approval distinct. The root smoke workflow's existing
lint backlog is not fixed by these safeguards. Do not advertise every scene as
production-ready solely because the dedicated companion-preview check passed.

The existing English companion clip and its separately authorized release retain
their original silent/captioned status. No expanded end-to-end workflow or new
render is part of this hardening task.

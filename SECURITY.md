# Security and private data

This repository is public. Its code, commit history, pull-request discussions,
Actions logs, and downloadable artifacts must not contain credentials, private
conversations, student grades, invoices, or unpublished personal material.

## Report a problem

Use GitHub's **Security → Report a vulnerability** when enabled. Do not post a
secret, student record, private transcript or exploitable detail in a public issue.
If private reporting is unavailable, ask the maintainer to enable a private
channel without including the sensitive details. Maintainers should use a draft
security advisory for investigation; no response-time guarantee is implied.

For an exposed credential, revoke/rotate it at the provider first. Removing a
current file or adding an ignore pattern does not remove history, caches, forks
or old logs. Coordinate cleanup; never force-push, delete evidence, or change
visibility as an automatic response.

## Execution and data boundaries

- Python scenes and build scripts are executable code. Review unfamiliar branches
  before running them; use a disposable environment without personal files or keys.
- Silent checks need no Azure key. Narration sends text/SSML to the configured
  Azure service and may incur charges. Keep the existing voice/profile selection.
- Narrated CI is an explicit manual action on `main`, not a pull-request side effect.
  Protect cloud credentials with reviewed environments and least privilege.
- Some asset refreshers download remote photos. Source URLs and credits do not by
  themselves grant unlimited redistribution rights; see [public readiness](docs/PUBLIC_READINESS.md).
- Drive copying, publishing releases and institutional publication are separate
  authorized operations. A successful render is not listening or publication approval.
- CI artifacts in a public repository are not private storage. Upload only the
  stated review outputs; never entire workspaces, environment files or raw billing data.

## Validation limits

The public audit runs a pinned secret detector over fetched Git history and
tracked files, with bounded sampling of discussions and accessible logs. It
publishes only a sanitized summary and reports skipped material. It does not
clear binary media, external links, all old artifacts, image rights, or personal
context. A clean automated scan is not a guarantee that no sensitive data exists.

Use synthetic reproductions for bug reports. Preserve all existing licenses and
third-party notices. Review security fixes on a branch and do not disable failing
checks to obtain a green badge.

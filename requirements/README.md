# Reviewed Python environments

The `checks.txt`, `teaching.txt`, `teaching-constraints.txt` and `build.txt` files
describe the requested dependencies. Install the complete, hashed files in
`locks/` for repeatable package selection:

| Lock | Target |
| --- | --- |
| `checks-py311.txt` | Lightweight checks on CPython 3.11 or 3.13, macOS/Linux |
| `build-py313.txt` | CPython 3.13 source-build tools on macOS/Linux |
| `teaching-py313-macos-arm64.txt` | CPython 3.13 teaching runtime on macOS arm64 |
| `teaching-py313-linux-x86_64.txt` | CPython 3.13 teaching runtime on Ubuntu x86_64 |

The teaching locks preserve Pillow 11.3.0 and the reviewed Manim/voiceover
versions. Mac-only PyObjC dependencies are absent from the Linux lock. Each lock
contains every transitive Python distribution in its resolved graph and the
published wheel/source SHA-256 hashes for those versions. Generation verifies
the selected resolver artifact against the public PyPI release hashes.

The resolver environment is recorded in each header. A target projected from
another platform's metadata still needs a native installation and tests. Consult
the dated verification report and the actual CI run before claiming target
validation. A package lock does not make native libraries, fonts, TeX or encoded
output identical across platforms.

## Install

Run from the repository root. For lightweight checks:

```sh
python3.11 -m venv .venv-checks
.venv-checks/bin/python -m pip install --require-hashes --only-binary=:all: \
  -r requirements/locks/checks-py311.txt
.venv-checks/bin/python -m pip check
```

For teaching, install Cairo/Pango development headers, a C compiler, pkg-config,
LaTeX, dvisvgm, FFmpeg and SoX first. Ubuntu additionally needs `patchelf` for
the Meson source-build backend. Existing teaching workflows list the native
packages. Use the Linux runtime filename instead on Ubuntu:

```sh
python3.13 -m venv .venv-teaching
.venv-teaching/bin/python -m pip install --require-hashes --only-binary=:all: \
  -r requirements/locks/build-py313.txt
PATH="$PWD/.venv-teaching/bin:$PATH" .venv-teaching/bin/python -m pip install \
  --require-hashes --no-build-isolation \
  -r requirements/locks/teaching-py313-macos-arm64.txt
.venv-teaching/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv-teaching/bin/python -m pip check
.venv-teaching/bin/python scripts/environment_lock.py inventory \
  --output review_artifacts/environment.json
```

Putting the environment's `bin` first selects the locked Meson/Ninja executables.
The build lock supplies every Python backend dependency before disabling build
isolation; pip must not independently resolve an unrecorded build environment.
This does not install or change any promotion project's environment.

## Update and verify a lock

Make changes in a disposable environment. Pip performs dependency resolution;
`scripts/environment_lock.py` validates its graph and formats requirements. A
complete report needs `--ignore-installed`, otherwise installed dependencies
can be absent. For example, with the build profile already installed:

```sh
python -m pip install --dry-run --ignore-installed --no-build-isolation \
  --report /tmp/teaching-report.json -r requirements/teaching.txt
python scripts/environment_lock.py from-report \
  --report /tmp/teaching-report.json --target macos-arm64 --python-version 3.13 \
  --input requirements/teaching.txt --input requirements/teaching-constraints.txt \
  --input requirements/checks.txt \
  --output requirements/locks/teaching-py313-macos-arm64.txt
```

Use `--target linux-x86_64` for Ubuntu. The tool refuses a projected target when
the report lacks a dependency required there; obtain a native report in that
case. Use `--target portable` for checks/build profiles only when the macOS and
Linux graphs agree. Regenerate both runtime locks after a shared input changes.
Raw pip reports and install logs can contain index information; keep them in
temporary storage. Commit inspected requirement files, never raw reports or
downloaded package bundles.

For a stronger native verification, build a wheel bundle with caching disabled,
record the actual built-wheel bytes, and install it offline into a second clean
environment:

```sh
python -m pip wheel --no-cache-dir --no-deps --require-hashes \
  --no-build-isolation -r requirements/locks/teaching-py313-macos-arm64.txt \
  --wheel-dir /tmp/teaching-wheelhouse
python scripts/environment_lock.py wheel-lock \
  --wheel-dir /tmp/teaching-wheelhouse \
  --source-lock requirements/locks/teaching-py313-macos-arm64.txt \
  --output /tmp/teaching-wheelhouse.txt
```

In the second environment, use `pip install --no-index --only-binary=:all:
--find-links /tmp/teaching-wheelhouse --require-hashes -r
/tmp/teaching-wheelhouse.txt`, then `pip check`, relevant tests and an explicitly
silent representative preview. Wheel bundles contain platform-specific native
binaries; keep their matching lock and native inventory together. Listening and
publication approval remain separate.

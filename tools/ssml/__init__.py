"""
tools.ssml
==========
Config-driven SSML preprocessor for Azure fr-CA math narration.

Public API
----------
    from tools.ssml import compile, lint

    ssml_body = compile("Considérons un triangle entre A et B.")
    findings  = lint("Considérons ...")

The compile step runs the author's plain-French text through a rule
engine (see tools/ssml/config/fr_ca_math.yaml) and emits SSML ready to
be wrapped in the standard <lang>/<prosody> envelope via tools.tts.ssml.

See tools/ssml/README.md for authoring guidelines and rule anatomy.

Status
------
Skeleton — no rules implemented yet. compile() currently returns input
unchanged so importing callers continue to work.
"""

from tools.ssml._version import __version__
from tools.ssml.engine import compile
from tools.ssml.lint import LintFinding, lint

__all__ = ["compile", "lint", "LintFinding", "__version__"]

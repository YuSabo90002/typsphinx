# Phase 47 plan 03, task 2: OUT-02's real-sphinx-build escape-shape gate. A
# single docname `index` whose typst_documents target is derived from the
# TYPSPHINX_ESCAPE_SHAPE environment variable, so ONE fixture directory
# serves all three OUT-02 escape shapes (traversal / absolute /
# drive-qualified) rather than three near-duplicate fixtures.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising OUT-02:
#   - TYPSPHINX_ESCAPE_SHAPE must be read from os.environ, not hardcoded --
#     tests/test_out02_escape_target_gate.py sets it per-parametrized-case
#     via subprocess env, and expects this file to react to it.
#   - "traversal" -> "../escape.typ": a parent-traversal segment.
#   - "absolute" -> "/tmp/escape.typ" on POSIX, "\\\\escape.typ" (a
#     UNC-shaped double backslash) on Windows (branched on os.name,
#     matching the plan's own instruction) -- an absolute path.
#   - "drive" -> "C:\\escape.typ": a drive-qualified path, asserted on
#     EVERY platform since it is a string-shape check, not a filesystem
#     behaviour (D-05's platform-independence principle).
#   - Default (TYPSPHINX_ESCAPE_SHAPE unset) is "traversal", so a bare
#     `sphinx-build` invocation against this fixture (no env override)
#     still exercises OUT-02 rather than silently no-op-ing.
#   - `index.rst`'s body must keep the `ESCAPE-GATE-MARKER` string.

import os

_SHAPE = os.environ.get("TYPSPHINX_ESCAPE_SHAPE", "traversal")

if _SHAPE == "traversal":
    _TARGET = "../escape.typ"
elif _SHAPE == "absolute":
    _TARGET = "\\\\escape.typ" if os.name == "nt" else "/tmp/escape.typ"
elif _SHAPE == "drive":
    _TARGET = "C:\\escape.typ"
else:
    _TARGET = "../escape.typ"

project = "Escape Target Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", _TARGET, "Escape Target Gate", "Probe Author"),
]

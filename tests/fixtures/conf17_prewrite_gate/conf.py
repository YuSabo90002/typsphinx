# Phase 54.1 plan 03, task 1: CR-01's hoisted A-01/CONF-17 gate fixture --
# the SYNTHESIZED built-in "typst" registry key's `template` value is a
# BARE FILENAME at the source-tree root, which resolve_template_registry()
# never CONF-17-checks (that check runs only inside the declared-key
# validation loop; the synthesized key is appended AFTER that loop
# returns). Pre-fix, this violation is caught only at finish() -- after
# every content and wrapper .typ file is already on disk.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the hoisted CONF-17/A-01 gate:
#   - `custom.typ` MUST stay at the source-tree root (this directory) --
#     its PARENT directory (== srcdir itself) is exactly what CONF-17/A-01
#     forbids.
#   - NO custom-template registry config value may be declared -- the
#     resolved registry must hold ONLY the synthesized built-in "typst"
#     key, which is the one key CONF-17 never validates (D-05).
#   - BOTH docnames ("index" and "other") are load-bearing for the
#     restricted-build order-independence test (test 3): that test invokes
#     `sphinx-build` with an explicit filename argument restricting the
#     build to only ONE of them, and the refusal must still fire because
#     the pre-write pass reads the WHOLE `typst_documents` config, not
#     just the entries whose docname is in this build's restricted
#     docnames set.

project = "CONF-17 Prewrite Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_template = "custom.typ"

typst_documents = [
    ("index", "index_out.typ", "Index Master", "Probe Author"),
    ("other", "other_out.typ", "Other Master", "Probe Author"),
]

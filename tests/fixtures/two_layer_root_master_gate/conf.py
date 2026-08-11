# Phase 47 plan 01, task 1: the plan-02 tracer fixture for the two-layer
# content/wrapper split (COMP-01, COMP-02, OUT-03). A single docname `index`
# whose typst_documents target `manual.typ` deliberately has a STEM that
# differs from the docname `index` -- so this fixture is the minimal case
# proving a bare (no-path) target still resolves at the output root
# (OUT-01's "a bare name writes at the output root" half) while the
# CONTENT file stays docname-derived (`index.typ`) regardless of the
# wrapper's own name.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising COMP-01/COMP-02/OUT-03:
#   - `typst_documents`'s single entry's target MUST be `manual.typ`, not
#     `index.typ` -- if the target equalled the docname's own content path
#     this fixture would silently become the bld03_self_collision_gate
#     scenario instead of a clean two-layer split.
#   - `index.rst`'s body must keep the `ROOT-BODY-MARKER-AAA` string --
#     tests prove the content file's body via a `grep -c`-style substring
#     count, so renaming or duplicating the marker breaks that proof.

project = "Root Master Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Root Master Gate", "Probe Author"),
]

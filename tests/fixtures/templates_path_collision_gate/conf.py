# Phase 54.1 plan 01, task 1: WR-01's `templates_path` collision gate
# fixture -- the tracer slice this phase closes.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the collision gate:
#   - The `templates_path` setting below and registry key "paper"'s
#     `template` value `_templates/custom.typ` MUST resolve into the SAME
#     directory the `templates_path` entry names -- that identity is what
#     this gate exercises (D-02: a path-relationship test, never a name
#     match on the literal string `_templates`).
#   - The registry key spelling `paper` is asserted verbatim by
#     tests/test_templates_path_collision_gate.py -- do not rename it.
#   - `typst_documents`' single entry's fifth element must name `"paper"`
#     so `write()`'s pre-write pass resolves that key through
#     `TemplateEngine.resolve_template()` and finds the collision.

project = "Templates Path Collision Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

templates_path = ["_templates"]

typst_document_templates = {
    "paper": {"template": "_templates/custom.typ"},
}

typst_documents = [
    ("index", "index_out.typ", "Index Master", "Probe Author", "paper"),
]

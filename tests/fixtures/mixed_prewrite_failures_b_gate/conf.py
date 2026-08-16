# Phase 54.1 plan 05, task 1: the SAME two violations as
# tests/fixtures/mixed_prewrite_failures_a_gate/conf.py -- a reserved-key
# case collision (the DECLARED "Typst" key) AND a CONF-17/A-01 violation
# on the SYNTHESIZED built-in "typst" key (global
# `typst_template = "aardvark.typ"`) -- declared in INVERTED order, for
# the cross-kind aggregation gate's message-identity assertion (D-03's
# guarantee must hold across declaration order, not merely across
# repeated runs of one project).
#
# Measured constraint (see fixture A's conf.py comment for the full
# explanation): a DECLARED `typst_document_templates` key with a CONF-17-
# violating template is caught earlier, by `resolve_template_registry()`'s
# own declared-key loop -- so the CONF-17 half of this fixture must use
# the global `typst_template` setting, not a second declared key.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the cross-kind aggregation gate:
#   - The declared registry key spelling ("Typst") and the built-in key
#     it collides with ("typst") are asserted VERBATIM by
#     tests/test_prewrite_failure_aggregation_gate.py.
#   - This fixture is byte-identical to
#     tests/fixtures/mixed_prewrite_failures_a_gate/conf.py EXCEPT that
#     the config-statement order is reversed (typst_document_templates
#     before typst_template) and the typst_documents list order is
#     reversed (the default "other" entry, resolving to the synthesized
#     "typst" key, is listed before the "index" entry referencing
#     "Typst").
#   - "aardvark.typ" MUST stay at the source-tree root -- its parent
#     directory (== srcdir itself) is exactly what CONF-17/A-01 forbids.
#   - The "Typst" key's template MUST stay inside the _typst/
#     subdirectory, so this fixture never ALSO trips CONF-17 for that
#     key -- it must trip ONLY the reserved-key case collision.

project = "Mixed Prewrite Failures B"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_document_templates = {
    "Typst": {"template": "_typst/other.typ"},
}

typst_template = "aardvark.typ"

typst_documents = [
    ("other", "other_out.typ", "Other Master", "Probe Author"),
    ("index", "index_out.typ", "Index Master", "Probe Author", "Typst"),
]

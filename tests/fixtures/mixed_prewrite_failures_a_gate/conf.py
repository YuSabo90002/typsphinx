# Phase 54.1 plan 05, task 1: WR-01/CR-01 cross-kind aggregation gate
# fixture -- ONE build carrying BOTH a reserved-key case collision (the
# DECLARED "Typst" key differs from the reserved built-in "typst" key
# only by case) AND a CONF-17/A-01 violation on the SYNTHESIZED built-in
# "typst" key (global `typst_template = "aardvark.typ"`, a bare filename
# at the source-tree ROOT). Neither this fixture nor its sibling
# (tests/fixtures/mixed_prewrite_failures_b_gate/) sets templates_path,
# so the templates_path containment check contributes nothing and the
# aggregate carries EXACTLY these two failure kinds.
#
# Measured constraint (do not "simplify" this to two declared registry
# keys): a DECLARED `typst_document_templates` key with a CONF-17-
# violating template is caught by `resolve_template_registry()`'s OWN
# declared-key validation loop (`template_registry.py:420`), which raises
# its OWN separate "typst_document_templates: N invalid definition(s)"
# error BEFORE `_validate_used_template_paths()` ever runs -- so a
# DECLARED key can never reach the hoisted CONF-17 check this gate
# targets. The hoisted check (D-04/D-05/D-06) exists SPECIFICALLY
# because the SYNTHESIZED built-in "typst" key is the ONE key that
# declared-key loop never reaches (it is appended after that loop
# returns) -- so the CONF-17 half of this fixture MUST use the global
# `typst_template` setting, not a second `typst_document_templates`
# entry.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the cross-kind aggregation gate:
#   - The declared registry key spelling ("Typst") and the built-in key
#     it collides with ("typst") are asserted VERBATIM by
#     tests/test_prewrite_failure_aggregation_gate.py.
#   - This fixture and its sibling
#     tests/fixtures/mixed_prewrite_failures_b_gate/ must stay IDENTICAL
#     except for declaration order: this fixture's typst_documents lists
#     the "index" entry (referencing "Typst") before the "other" entry
#     (the default typst_documents entry, which resolves to the
#     synthesized "typst" key); the sibling fixture reverses that order
#     and the order the two config statements appear in the file.
#   - "aardvark.typ" MUST stay at the source-tree root -- its parent
#     directory (== srcdir itself) is exactly what CONF-17/A-01 forbids.
#   - The "Typst" key's template MUST stay inside the _typst/
#     subdirectory, so this fixture never ALSO trips CONF-17 for that
#     key -- it must trip ONLY the reserved-key case collision.

project = "Mixed Prewrite Failures A"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_template = "aardvark.typ"

typst_document_templates = {
    "Typst": {"template": "_typst/other.typ"},
}

typst_documents = [
    ("index", "index_out.typ", "Index Master", "Probe Author", "Typst"),
    ("other", "other_out.typ", "Other Master", "Probe Author"),
]

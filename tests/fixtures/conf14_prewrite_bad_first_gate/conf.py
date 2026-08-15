# Phase 53 plan 06, task 1: CONF-14's "offending master sorts FIRST" fixture
# -- pairs with conf14_prewrite_bad_last_gate. Both the write order AND the
# declaration order are inverted relative to that fixture, which is what
# makes the byte-identical-message assertion (test 3) load-bearing.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising CONF-14's zero-output guarantee:
#   - The bad key spelling `nope` and the registry key spelling `good` MUST
#     match conf14_prewrite_bad_last_gate/conf.py byte-for-byte.
#   - `typst_document_templates["good"]` carries ONLY `package`, same as
#     the sibling fixture.
#   - Docnames are `aaa_bad`, `index`, `zzz_good`. Sorted alphabetically
#     that is `aaa_bad`, `index`, `zzz_good` -- the offending master
#     (`aaa_bad`, key `nope`) is written FIRST, before any other content or
#     wrapper file exists, which is exactly the live verifier's build B.
#     `typst_documents` also declares the bad entry FIRST (the opposite of
#     the sibling fixture, which declares it second) -- do not reorder.

project = "CONF-14 Prewrite Bad-First Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_document_templates = {
    "good": {"package": "@preview/example:0.1.0"},
}

typst_documents = [
    ("aaa_bad", "aaa_bad_out.typ", "Aaa Bad Master", "Probe Author", "nope"),
    ("zzz_good", "zzz_good_out.typ", "Zzz Good Master", "Probe Author", "good"),
]

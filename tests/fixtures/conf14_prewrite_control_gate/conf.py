# Phase 53 plan 06, task 2: the no-op control fixture for
# TypstBuilder._validate_registry_key_references() -- ROADMAP SC#2's
# byte-identity guarantee, extended to cover the new pass.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the no-op path it pins:
#   - `typst_document_templates` declares registry key `good`, referenced
#     by NO `typst_documents` entry -- declaring a registry must not
#     perturb output (TPL-03 ordering edge).
#   - The `four` entry MUST stay exactly four elements (TPL-04's absent
#     element [4] resolves to the built-in `typst` key).
#   - The `five` entry's fifth element MUST stay the literal reserved key
#     `typst` (TPL-04's explicit-equivalent form).
#   - The lone `("index",)` one-element tuple MUST stay unusable per
#     `_is_usable_typst_documents_entry()` -- every write-phase site
#     tolerates and skips it without raising.

project = "CONF-14 Prewrite Control Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_document_templates = {
    "good": {"package": "@preview/example:0.1.0"},
}

typst_documents = [
    ("four", "four_out.typ", "Four Master", "Probe Author"),
    ("five", "five_out.typ", "Five Master", "Probe Author", "typst"),
    ("index",),
]

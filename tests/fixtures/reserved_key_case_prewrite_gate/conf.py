# Phase 54.1 plan 03, task 1: CR-01's reserved-key case-collision gate
# fixture -- a DECLARED registry key ("Typst") that differs from the
# reserved built-in registry key (RESERVED_REGISTRY_KEY = "typst") only by
# CAPITALISATION. CONF-16 rejects only the literal spelling "typst"; CONF-18
# compares declared keys only against each other, never against the
# synthesized built-in key -- so neither existing check catches this.
#
# Load-bearing property -- do NOT touch this, or this fixture silently
# stops exercising the reserved-key case-collision gate:
#   - The declared key's spelling MUST be "Typst" -- differing from the
#     reserved key "typst" ONLY by case is the entire point of this
#     fixture.

project = "Reserved Key Case Prewrite Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_document_templates = {
    "Typst": {"template": "_typst/other.typ"},
}

typst_documents = [
    ("index", "index_out.typ", "Index Master", "Probe Author", "Typst"),
]

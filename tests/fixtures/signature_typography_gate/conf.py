"""Sphinx config for the signature typography GATE-01 fixture (Phase 37, SIG-01..05).

``index`` MUST be a master document -- this fixture exists to be built through
``-b typst`` (see ``tests/test_signature_typography_gate.py``), so the
per-sub-part SIG-01..05 assertions can be run against a real emitted
``index.typ``.
"""

project = "Signature Typography Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# Target "index" (stem "index") casefold-collides with the docname's own
# content path "index.typ" (fixture de-collision rule, 47-EXPECTED-STRUCTURE.md);
# renamed to the canonical "master.typ".
typst_documents = [
    ("index", "master.typ", "Signature Typography Gate", "typsphinx tests"),
]

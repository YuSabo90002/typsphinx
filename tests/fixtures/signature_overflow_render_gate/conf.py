# Sphinx configuration for the SIG-07 signature-overflow render-gate
# fixture (37-03-PLAN.md Task 1).
#
# Minimal self-contained project used by
# tests/test_signature_overflow_render_gate.py to prove that a long,
# fully-qualified dotted signature name stays inside the production text
# column (453.54pt, measured 37-RESEARCH.md / 37-EMISSION-CONTRACT.md
# section 10), while a real-corpus worst-case signature never regresses.

project = "Signature Overflow Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- the SIG-07 gate measures against the real
# production page geometry (A4, default margins, 11pt), which only a master
# document's full-template render carries.
#
# Target "index" (stem "index") casefold-collides with the docname's own
# content path "index.typ" (fixture de-collision rule, 47-EXPECTED-STRUCTURE.md);
# renamed to the canonical "master.typ".
typst_documents = [
    ("index", "master.typ", "Signature Overflow Render Gate", "Test Author"),
]

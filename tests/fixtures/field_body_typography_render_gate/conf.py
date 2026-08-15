# Sphinx configuration for the field-body typography render-gate fixture
# (Phase 38, FLD-01, FLD-02, FLD-03; D-05, D-06, D-07, D-13).
#
# Minimal self-contained project used by
# tests/test_field_body_typography_render_gate.py to record the FLD-02/
# FLD-03 structural RED against the untouched translator, and to stay
# green as the phase's own non-regression control set.
#
# Construct roles (see index.rst for the full per-construct commentary):
#
#   1. Multi-Value Bulleted Control  -- FLD-02 bulleted half, non-regression
#      (D-13's stray parbreak() at the head of each bulleted item is LEFT
#      IN PLACE; recorded there, not here).
#   2. Single-Entry Collapsed Param  -- FLD-02 inline half (docutils
#      can_collapse -> one paragraph body).
#   3. Single-Value Fields (Returns/Rtype/Raises) -- FLD-02 inline half,
#      D-07/D-08 (label/value adjacency AND the consecutive-fields trap).
#   4. Resolvable Type Cross Reference -- FLD-03 Pitfall 2 (a resolvable
#      :type: composing inside an emitted link() call).
#   5. Name Without Type -- FLD-03 empty edge (no italic-monospace call).
#   6. Non-ASCII Parameter Name -- FLD-03 encoding edge (code-point
#      round-trip, no byte-level assumption).
#   7. Collapsed Inline Control -- contract section 4.3 property 3 (the
#      docutils-collapsed confval shape that legitimately DOES share one
#      line via the existing FID-09 inter-field separator; byte-identical
#      control, never edited by this plan).
#   8. Single Field List -- FLD-02 empty edge (no inter-field separator
#      when the field list has exactly one field).

project = "Field Body Typography Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- required for the
# FLD-02 pypdf-extracted-text adjacency assertions (D-07).
#
# Target "index" (stem "index") casefold-collides with the docname's own
# content path "index.typ" (fixture de-collision rule, 47-EXPECTED-STRUCTURE.md);
# renamed to the canonical "master.typ".
typst_documents = [
    ("index", "master.typ", "Field Body Typography Render Gate", "typsphinx tests"),
]

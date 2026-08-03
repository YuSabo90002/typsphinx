# Sphinx configuration for the signature_break_and_arrow_gate fixture
# (Phase 37, GATE-01, SIG-06/SIG-08/D-11).
#
# Minimal self-contained project used by
# tests/test_signature_break_and_arrow_gate.py to prove, in ONE build:
#
#   - SIG-08: a nested py:class::/py:method:: pair emits a doubled
#     parbreak() (37-EMISSION-CONTRACT.md section 8), a second nested pair
#     followed by a trailing paragraph that must stay separated (the shape
#     a naive depth-counter fix would break), and a sibling body-less
#     desc/desc control (mirrors desc_bodyless_concat_render_gate) that
#     must never be affected by the fix;
#   - SIG-06: a py:function:: with an explicit return annotation, whose
#     arrow glyph must reach the compiled PDF's extracted text
#     (section 7);
#   - D-11: a py:function:: whose desc_optional group HAS a following
#     sibling (the dropped-separator defect, section 6.1) and a second
#     py:function:: (the classic nested-optional printf shape) whose two
#     desc_optional groups are both last children -- the D-11
#     non-regression control that must render byte-unchanged by the fix.

project = "Signature Break And Arrow Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() / a manual typst.compile() call actually
# compiles it to PDF.
typst_documents = [
    ("index", "index", "Signature Break And Arrow Gate", "Test Author"),
]

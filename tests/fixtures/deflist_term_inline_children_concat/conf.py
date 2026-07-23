# Sphinx configuration for the def-list-term inline-children concat render-gate
# fixture (Phase 15, GATE-02 regression, bug #5).
#
# Minimal self-contained project used by
# tests/test_deflist_term_inline_children_gate.py to prove the translator emits
# a valid, + concatenated Typst term when a definition-list term's DIRECT
# inline children mix element types (literal, strong, emphasis, reference,
# text). This is the fast, offline reproduction of the fifth fatal GATE-02
# surfaced against Sphinx's own doc/ tree (e.g. extdev/logging.typ), after the
# def-list-term literal/text concat fix (bug #3) unblocked the compile path but
# only wired the term concat context into visit_Text / visit_literal:
#
#     TypstError: expected comma
#         terms.item(strong({text("type")}) + text(", ")strong({ + text("*subtype*")}), ...)
#
# Two symptoms in that one term:
#   1. Missing '+': text(", ")strong(  -- no separator between a text and the
#      following strong element (visit_strong ignored the term concat context).
#   2. Stray leading '+': strong({ + text(...)})  -- the term separator leaked
#      INSIDE the strong element's own content block (the concat context was
#      not suppressed while descending into the element's children).
#
# Fix: a single shared inline-concat mechanism (_enter/_exit_inline_concat_
# element + _emit/_mark_inline_concat_content) routes visit_Text, visit_literal,
# visit_emphasis, visit_strong and visit_reference through ONE source of truth,
# so every direct term child of any inline type is + separated between siblings
# while the concat context is suppressed inside each element's own block.

project = "Deflist Term Inline-Children Concat Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the "expected comma" fatal is observable.
typst_documents = [
    ("index", "index", "Deflist Term Inline-Children Concat Gate", "Test Author"),
]

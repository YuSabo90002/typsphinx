# Sphinx configuration for the def-list-term-concat render-gate fixture
# (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by
# tests/test_deflist_term_concat_render_gate.py to prove the translator emits
# a valid, + concatenated Typst term for a definition-list term whose inline
# children are juxtaposed. This is the fast, offline reproduction of the third
# fatal GATE-02 surfaced against Sphinx's own doc/ tree
# (tutorial/getting-started.rst), after the static-asset-copy and target-label
# fixes unblocked the compile path:
#
#     TypstError: expected comma
#         terms.item(raw("make.bat")text(" and ")raw("Makefile"), par({...}))
#
# Root cause: a def-list TERM buffers its inline children and depart_term does
# a bare "".join, so adjacent top-level inline code-mode expressions
# (literal -> text -> literal = raw("make.bat") text(" and ") raw("Makefile"))
# are concatenated with NO separator. In Typst code mode -- the first argument
# of terms.item(TERM, DEFINITION) -- two juxtaposed function-call expressions
# are a syntax error: the parser reads the first as the argument, then expects
# a comma but finds the next expression.
#
# Fix: an _in_term concat context (mirroring the existing _in_link /
# in_desc_parameter mechanism) makes visit_Text and visit_literal insert " + "
# between adjacent term expressions (none before the first / after the last),
# so the term emits raw("make.bat") + text(" and ") + raw("Makefile").

project = "Deflist Term Concat Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the "expected comma" fatal is observable.
typst_documents = [
    ("index", "index", "Deflist Term Concat Render Gate", "Test Author"),
]

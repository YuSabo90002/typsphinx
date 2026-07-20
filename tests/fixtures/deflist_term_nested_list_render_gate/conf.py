# Sphinx configuration for the deflist-term-nested-list render-gate fixture
# (Phase 19 Plan 03, FID-05 sub-case b).
#
# Minimal self-contained project used by
# tests/test_deflist_term_concat_render_gate.py to prove the translator emits
# terms(separator: linebreak(), ...) for a definition list whose definition
# body OPENS with a nested list/field-list -- the case where the definition's
# first rendered content is ALSO inline (strong()/text(), not a block), one
# level deeper than sub-case (a). Without the fix, the outer term merges onto
# the same visual line as the first line of its definition.
#
# Mirrors the real corpus case: usage/configuration.rst's 'mecab' confval
# definition list, whose definition body opens with a nested field list.

project = "Deflist Term Nested List Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF.
typst_documents = [
    ("index", "index", "Deflist Term Nested List Render Gate", "Test Author"),
]

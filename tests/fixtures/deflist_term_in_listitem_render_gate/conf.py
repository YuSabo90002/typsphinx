# Sphinx configuration for the deflist-term-in-listitem render-gate fixture
# (Phase 19 Plan 03, FID-05 sub-case a).
#
# Minimal self-contained project used by
# tests/test_deflist_term_concat_render_gate.py to prove the translator emits
# terms(separator: linebreak(), ...) for a definition list nested inside a
# bullet list_item -- the case where the definition's first content is BARE
# INLINE text (no par() wrapping), because visit_paragraph early-returns
# inside a list item. Without the fix, the term merges onto the same visual
# line as its definition (the built-in terms() separator defaults to a weak
# h(0.6em) horizontal space, not a line break).
#
# Mirrors the real corpus case: usage/configuration.rst's texinfo_elements
# 'paragraphindent' definition list, nested inside a bullet list item.

project = "Deflist Term In Listitem Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF.
typst_documents = [
    ("index", "index", "Deflist Term In Listitem Render Gate", "Test Author"),
]

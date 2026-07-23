# Sphinx configuration for the def-list multi-block-definition render-gate
# fixture (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by
# tests/test_deflist_definition_multiblock_render_gate.py to prove the
# translator wraps a definition-list DEFINITION with multiple block-level
# children in a single `{ ... }` content block before passing it as
# terms.item's 2nd argument. This is the fast, offline reproduction of the
# seventh fatal GATE-02 surfaced against Sphinx's own doc/ tree
# (usage/restructuredtext/directives.rst:1718 and ~16 other compiled .typ
# files), after bugs #1-#6 unblocked the compile path:
#
#     TypstError: expected comma
#         ... terms.item(TERM, par({...})<blank line>codly(...) ...) ...
#
# Root cause: depart_definition ''.join()s a definition's block children
# (par({...}) + blank line + codly(...) + fence + blank line + list({...})) into
# a bare, blank-line-separated statement blob and passes it UNWRAPPED as
# terms.item's 2nd argument. Blank-line separation of sequential content is
# valid only at document top level; as a function argument Typst reads the first
# statement par({...}) as the WHOLE argument and then expects a comma at the
# next bare statement -> "expected comma".
#
# Fix: the terms.item assembly wraps the definition (2nd) arg in `{ ... }`, so
# Typst auto-joins the block statements into one content value. A single-block
# definition wraps to {par({...})} and renders identically.

project = "Deflist Multiblock Definition Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the "expected comma" fatal is observable.
typst_documents = [
    ("index", "index", "Deflist Multiblock Definition Render Gate", "Test Author"),
]

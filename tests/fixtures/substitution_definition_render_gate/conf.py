# Sphinx configuration for the substitution-definition render-gate fixture
# (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by
# tests/test_substitution_definition_render_gate.py to prove the translator
# skips substitution_definition nodes entirely (no output of its own) while
# substitution_reference uses still render their replacement content. This is
# the fast, offline reproduction of the fatal GATE-02 surfaced against
# Sphinx's own doc/ tree (usage/restructuredtext/roles.rst -> latex.rst):
#
#     error: expected comma
#        |-- latex.typ:1507   (source: latex.rst:1131+)
#
# Root cause: TypstTranslator had no visit_substitution_definition handler,
# so the node fell through to unknown_visit (warns, does not skip) and its
# inline literal/text children leaked out as juxtaposed top-level code-mode
# expressions with no separator -- e.g. raw("a")text(", ")raw("b")...
#
# Fix: add visit_substitution_definition raising nodes.SkipNode, matching
# docutils/Sphinx's own HTML and LaTeX writers (both skip this node).

project = "Substitution Definition Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the fatal is observable.
typst_documents = [
    ("index", "index", "Substitution Definition Render Gate", "Test Author"),
]

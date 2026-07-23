# Sphinx configuration for the target-label render-gate fixture
# (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by tests/test_target_label_render_gate.py
# to prove the translator emits a valid Typst anchor for a target node. This is
# the fast, offline reproduction of the fatal GATE-02 surfaced against Sphinx's
# own doc/ tree (usage/installation.rst):
#
#     TypstError: expected semicolon or line break
#         label("id1")label("id2")
#
# Root cause: TypstTranslator.visit_target emitted a bare code-mode
# `label("id")`. Two consecutive target nodes -- e.g. the two anonymous
# hyperlink targets (`__ https://...`) that close a `.. tip::` block -- then
# produced `label("id1")label("id2")` with no separator, which is a Typst
# syntax error inside a `{...}` content block. (A bare label is also a raw
# label *value* that "cannot join content with label" even singly.)
#
# Fix: emit a metadata-carrying markup anchor `[#metadata(none) <id>]` wrapped
# in newlines, matching the extra-id anchors visit_title already emits. That is
# genuine content with the label attached, so it joins/concatenates cleanly,
# works singly and consecutively, and stays reachable via link(<id>).

project = "Target Label Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the adjacent-label fatal is observable.
typst_documents = [
    ("index", "index", "Target Label Render Gate", "Test Author"),
]

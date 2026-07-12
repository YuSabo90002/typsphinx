# Sphinx configuration for the confval field-body render-gate fixture
# (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by
# tests/test_confval_field_body_render_gate.py to prove the translator emits a
# collapsed field body's inline children as one valid content value. This is
# the fast, offline reproduction of the eighth fatal GATE-02 surfaced against
# Sphinx's own doc/ tree (16 occurrences, ALL in usage/configuration.typ),
# after bugs #1-#7 unblocked the compile path:
#
#     TypstError: expected semicolon or line break
#         ... text("The value of ")strong({text("html_title")}) ...
#
# Root cause (A): a confval :type:/:default: field body written inline on its
# field line (e.g. ':default: The value of **html_title**') is COLLAPSED by
# docutils to inline children (Text/strong/literal) DIRECTLY under field_body,
# with no wrapping paragraph. visit_field_body set no concat context, so the
# adjacent inline expressions juxtaposed (text(...)strong(...)) in the code-mode
# content block -> "expected semicolon or line break".
#
# Root cause (B): a definition_list nested in a bullet-list item, following a
# paragraph, emitted terms(...) with no leading list-item separator, abutting
# the preceding text(...) -> the same fatal (configuration.typ:2009).
#
# Fix: visit_field_body activates the shared inline-concat context (bug #5
# machinery) for an all-inline field body so its children '+'-separate into one
# content value; visit_definition_list emits the standard list-item newline
# separator.

project = "Confval Field Body Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the "expected semicolon or line break" fatal is observable.
typst_documents = [
    ("index", "index", "Confval Field Body Render Gate", "Test Author"),
]

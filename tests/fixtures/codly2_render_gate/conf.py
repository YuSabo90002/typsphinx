# Sphinx configuration for the codly 2.0 surface render gate (T002).
#
# Minimal self-contained project compiled by tests/test_codly2_render_gate.py
# (typstpdf, PDF text + content-stream inspection) and built with the typst
# builder by tests/test_codly2_output_gate.py (code-mode .typ shape). Every
# code block carries a unique lowercase sentinel so the tests can find its
# rows in the extracted PDF text; no code line starts with a digit, so a
# digits-only text run left of the code is unambiguously a line number.
#
# ``highlight_language`` is deliberately left unset: a code block with no
# language argument then carries Sphinx's ``default`` language, which the
# translator must map to "no language" (no codly badge).

project = "Codly2 Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# Captioned code blocks and image figures are numbered, so :numref: resolves
# and the listing/figure sequences can be told apart.
numfig = True

typst_documents = [
    # A bare "index" target would collide with the content file index.typ.
    ("index", "master.typ", "Codly2 Render Gate", "Test Author"),
]

# Sphinx configuration for the CI-02 preview-package smoke-test fixture.
#
# Minimal self-contained project used by tests/test_preview_smoke_gate.py to
# prove a real `typst compile` exercises all four bundled @preview packages
# (codly, codly-languages, mitex, gentle-clues) -- not merely imports them --
# so a mitex-class break (e.g. the historical "unknown variable: kai" error)
# fails this gate loudly.

project = "Preview Smoke"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template plus all four @preview imports -- included
# documents only get a minimal import set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Preview Smoke", "Test Author"),
]

# CRITICAL (D-04): do NOT set typst_use_mitex = False here. It defaults to
# True (see typsphinx/__init__.py), which routes `.. math::` blocks through
# a real `mitex(` call -- the exact code path the historical `kai` break
# lived in and the one this fixture exists to exercise.

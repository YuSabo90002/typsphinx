# Sphinx configuration for the GATE-01 `typst_elements` unknown-key
# NEGATIVE gate (Phase 26, CONF-04, SC#3).
#
# `bogus_unknown_key` is deliberately NOT a member of
# `template_engine.ELEMENTS_ALLOWLIST` (which contains exactly
# `papersize`/`fontsize`, D-04). Per D-06/D-07, `map_parameters()` must
# raise `sphinx.errors.ExtensionError` naming the offending key BEFORE it
# is ever added to `params` -- so `sphinx-build` must abort (non-zero
# exit) rather than silently drop the key or pass it through as an
# undeclared kwarg to `project()` (which would instead surface as a
# cryptic downstream `typst.compile()` fatal -- exactly the failure mode
# SC#3 replaces with an actionable Python-side error).

project = "Typst Elements Unknown Key Negative Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# Phase 47 (OUT-01/BLD-03): the target is "master", not the identity
# "index" -- see papersize_positive/conf.py's identical comment for why an
# identity target is now a self-collision under a literal-path target.
# (This fixture's build aborts before the wrapper would ever be written,
# so the collision is never actually reached -- renamed for consistency
# with its sibling fixtures anyway.)
typst_documents = [
    ("index", "master", project, author),
]

typst_elements = {
    "bogus_unknown_key": "must never reach project() as a kwarg",
}

# Sphinx configuration for the SC#3 / D-K documented-contract permanent
# regression gate (Phase 45.1, plan 06 closeout).
#
# Proves SC#1's literal shape: a custom template declaring EXACTLY the
# nine parameters docs/source/user_guide/templates.rst "Standard
# Parameters" publishes, built with `sphinx-build -b typstpdf` over a
# master document that carries both a real toctree AND a real
# `typst_elements` setting. Deliberately does NOT set
# `typst_template_function` -- this fixture exercises the DEFAULT
# auto-derived set (D-A), which is the case CONF-11's exclusivity
# (D-B/D-D) is the alternative to; that route is already covered by
# tests/test_params_exclusivity_gate.py, not this module.

project = "Documented Params Contract Gate"
author = "Gate Fixture Author"
release = "1.0"
copyright = "2026, Fixture Author"

# Non-default language so the auto-derived `lang` (CONF-12/D-I) is
# genuinely observable in the emitted call rather than coinciding with
# Typst's own "en" template default.
language = "ja"

extensions = ["typsphinx"]

# index must be a master document so the writer applies the full
# custom-template routing (not the minimal included-document import set).
typst_documents = [
    ("index", "index", project, author),
]

typst_template = "_templates/documented.typ"

# Both keys are ELEMENTS_ALLOWLIST members, so `papersize`/`fontsize`
# are live in the emitted call alongside the toctree-gated keys the
# index.rst toctree below makes live.
typst_elements = {
    "papersize": "a4",
    "fontsize": "11pt",
}

# CRITICAL: do NOT set typst_template_function here. This fixture proves
# the DEFAULT nine-parameter contract (D-A) -- the case where no `params`
# is declared -- not CONF-11's exclusivity branch.

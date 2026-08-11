# Sphinx configuration for the CONF-11 params-exclusivity regression gate
# (Phase 45.1, plan 01).
#
# Proves D-B/D-D end to end: a custom template declaring NO named
# parameters at all (only the trailing positional ``body``) builds and
# compiles when ``typst_template_function["params"]`` is explicitly set to
# an empty dict. All three ``toctree_*`` keys and both configured
# ``typst_elements`` keys are LIVE on the pre-fix path (via the toctree in
# index.rst and the settings below), so the pre-fix additive union has
# every auto-derived key available to leak into the emitted call -- this
# fixture is not merely "nothing configured", it deliberately maximizes the
# auto-derived set the fix must withhold.
#
# CRITICAL: do NOT add a "params" entry beyond the empty dict below -- an
# absent params dict and an explicitly empty one must be distinguishable
# (D-D), and this fixture is the empty-dict half of that pair.

project = "Zero Params Template Gate"
author = "Gate Fixture Author"
release = "1.0"
copyright = "2026, Fixture Author"
language = "ja"

extensions = ["typsphinx"]

# index must be a master document so the writer applies the full
# custom-template routing (not the minimal included-document import set).
typst_documents = [
    ("index", "index", project, author),
]

typst_template = "_templates/zero_param.typ"

# Both keys are ELEMENTS_ALLOWLIST members and would be emitted as named
# arguments under the pre-fix additive union.
typst_elements = {
    "papersize": "a4",
    "fontsize": "11pt",
}

# D-D: an explicitly empty params dict -- "params" is PRESENT, so nothing
# is passed. Distinguishing this from an ABSENT params key is exactly
# what TemplateEngine.typst_template_params_specified must do.
typst_template_function = {
    "name": "project",
    "params": {},
}

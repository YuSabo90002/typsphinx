# Sphinx configuration for the CONF-11 params-exclusivity regression gate,
# `typst_template` route, PARTIAL params (Phase 45.1, plan 02).
#
# Proves D-B on a non-empty, partial `params` declaration: the template
# below declares exactly ONE named parameter (`subtitle`) plus the trailing
# positional `body` -- deliberately no `title`, `authors`, or `date`. Under
# the pre-fix additive union this build would receive seven-plus named
# arguments against a one-parameter template and abort with
# `TypstError: unexpected argument: ...`; post-fix it receives `subtitle`
# alone. `typst_elements["papersize"]` and the toctree below make the
# auto-derived set non-trivial, so a leaking key is observable.
#
# Every fixture in this directory declares a `params` key (see the module
# docstring in tests/test_params_exclusivity_gate.py) -- do not remove it.

project = "Partial Params Template Gate"
author = "Gate Fixture Author"
release = "1.0"
copyright = "2026, Fixture Author"

extensions = ["typsphinx"]

# index must be a master document so the writer applies the full
# custom-template routing (not the minimal included-document import set).
typst_documents = [
    ("index", "index", project, author),
]

typst_template = "_templates/partial.typ"

# An ELEMENTS_ALLOWLIST member that would be emitted as a named argument
# under the pre-fix additive union.
typst_elements = {
    "papersize": "a4",
}

# D-B: only "subtitle" is declared -- the auto-derived title/authors/date,
# the typst_elements merge, and the toctree_* merge must all be discarded
# wholesale, not merged in alongside this one key.
typst_template_function = {
    "name": "project",
    "params": {
        "subtitle": "A Gate Subtitle",
    },
}

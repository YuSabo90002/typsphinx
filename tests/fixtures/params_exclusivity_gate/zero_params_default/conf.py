# Sphinx configuration for the CONF-11 params-exclusivity regression gate,
# BUNDLED-DEFAULT route (Phase 45.1, plan 02).
#
# Proves D-B/D-D on the route no custom `typst_template`/`typst_package` is
# set: `typsphinx/templates/base.typ`'s inlined `project()` function
# declares defaults for all nine documented parameters, so this fixture
# compiles both pre- and post-fix -- its RED is STRUCTURAL, not a compile
# fatal (the amended definition of RED this project adopted in v0.7.0, see
# STATE.md's "Standing GATE-01 bar" paragraph). Pre-fix the emitted call
# carries the full auto-derived set; post-fix it carries zero named
# arguments, because `params: {}` is explicitly declared (D-D).
#
# Every fixture in this directory declares a `params` key (see the module
# docstring in tests/test_params_exclusivity_gate.py) -- do not remove it.

project = "Zero Params Default Gate"
author = "Gate Fixture Author"
release = "1.0"
copyright = "2026, Fixture Author"

extensions = ["typsphinx"]

# index must be a master document so the writer applies the full
# bundled-default template routing (not the minimal included-document
# import set).
#
# Phase 47 (OUT-01/BLD-03): the target is "master", not the identity
# "index" -- see zero_params_template/conf.py's identical comment for why
# an identity target is now a self-collision under a literal-path target.
typst_documents = [
    ("index", "master", project, author),
]

# Deliberately no typst_template and no typst_package -- this is the
# bundled-default route.

# Both keys are ELEMENTS_ALLOWLIST members and would be emitted as named
# arguments under the pre-fix additive union.
typst_elements = {
    "papersize": "a4",
    "fontsize": "11pt",
}

# D-D: an explicitly empty params dict -- "params" is PRESENT, so nothing
# is passed, even though templates/base.typ would happily accept all nine
# documented parameters.
typst_template_function = {
    "name": "project",
    "params": {},
}

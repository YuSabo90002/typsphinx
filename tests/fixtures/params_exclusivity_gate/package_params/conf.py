# Sphinx configuration for the CONF-11 params-exclusivity regression gate,
# `typst_package` route (Phase 45.1, plan 02).
#
# Proves D-B/D-C on the package route: `typst_template_mapping` supplies a
# "title" key that `typst_template_function["params"]` does NOT name. This
# is the fixture that discharges D-C -- it shows the package path needs no
# code special case once `params` is authoritative. Pre-fix the emitted
# call carries three named arguments including the mapped `title`; post-fix
# it carries only the two declared `params` keys and no `title`.
#
# CRITICAL: do NOT set `typst_template` here -- setting a custom template
# alongside `typst_package` routes this fixture onto the "both configured"
# path (D-03) instead of the package-ALONE path this gate exists to prove
# (see the identical warning in
# tests/fixtures/package_only_config_gate/conf.py).
#
# Every fixture in this directory declares a `params` key (see the module
# docstring in tests/test_params_exclusivity_gate.py) -- do not remove it.

project = "Package Params Gate"
author = "Gate Fixture Author"
release = "1.0"
copyright = "2026, Fixture Author"

extensions = ["typsphinx"]

# index must be a master document so the writer applies the full
# package-route template routing rather than the minimal included-document
# import set.
#
# Phase 47 (OUT-01/BLD-03): the target is "master", not the identity
# "index" -- see zero_params_template/conf.py's identical comment for why
# an identity target is now a self-collision under a literal-path target.
typst_documents = [
    ("index", "master", project, author),
]

# The package this fixture pins ALONE -- no typst_template is ever set.
typst_package = "@preview/charged-ieee:0.1.4"

# "project" -> "title" mapping is honoured by map_parameters(), producing
# an auto-derived "title" key that params below does NOT declare -- the
# adjacency case D-B/D-C must discard.
typst_template_mapping = {
    "project": "title",
}

# D-B: only "abstract" and "paper-size" are declared -- no "title" key.
# Post-fix, the mapped "title" from typst_template_mapping above must be
# absent from the emitted call.
typst_template_function = {
    "name": "ieee",
    "params": {
        "abstract": (
            "A fixture abstract proving the package-route path compiles "
            "for real, end to end, through a genuine typst.compile() call."
        ),
        "paper-size": "a4",
    },
}

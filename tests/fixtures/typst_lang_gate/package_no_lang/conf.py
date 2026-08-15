# Sphinx configuration for the GATE-01 typst `lang` gate's package-path
# non-regression proof (Phase 27.1, CONF-07, SC#3 -- the package half).
#
# Configures `typst_package` ALONE (no `typst_template`), combined with
# Sphinx `language = "ja"`. This is the regression proof for the
# `typst_package` guard inside `TemplateEngine.uses_bundled_default_
# template()`: without that guard, this engine has no explicit template
# path, so its OWN `resolve_template()` priority walk legitimately
# resolves to `"default"` (Priority 3) even though `render()` never
# actually loads that bundled template on the package path -- the
# emitted `#show` rule calls the package's own entry function instead.
# Forwarding a bundled-template-only `lang` argument into a package
# function that never declared it would be the exact same
# undeclared-kwarg Typst compile fatal SC#3 exists to prevent, just
# reached via a different route.
#
# Modeled on `tests/fixtures/package_only_config_gate/conf.py` (same
# `@preview/charged-ieee` package, same single-key parameter mapping
# shape), trimmed down since this fixture is driven through the FASTER
# source-only `-b typst` builder rather than a real compile -- the
# existing package-only gate (`tests/test_package_only_config_gate.py`)
# already proves this package path compiles for real; a second real
# compile here would add a package download for no additional signal.
#
# CRITICAL: do NOT set `typst_template` here -- doing so would route this
# fixture onto the "both configured" path instead of the package-ALONE
# path this gate exists to prove.

project = "Typst Lang Gate Package No Lang Proof"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# index must be a master document (not merely an included one) so the
# writer applies the full package-alone template routing rather than the
# minimal included-document import set.
# Phase 47 (OUT-01/BLD-03): the target is "master", not the identity
# "index" -- since a typst_documents target is now a literal output
# path, an identity target would make the wrapper resolve onto this
# docname's own content file (index.typ) and silently overwrite it with
# a self-referential #include(), producing "TypstError: cyclic import"
# (47-EXPECTED-STRUCTURE.md's fixture de-collision rule).
typst_documents = [
    ("index", "master", project, author),
]

# The Sphinx language that would auto-derive to "ja" -- but only on the
# TRUE default-template path, which the package-alone path is NOT
# (regardless of what its own priority walk would resolve to).
language = "ja"

# The Typst Universe package this fixture pins ALONE -- no typst_template
# is ever set.
typst_package = "@preview/charged-ieee:0.1.4"

typst_template_mapping = {
    "project": "title",
}

# The package's entry function -- deliberately no `lang`-shaped param in
# its own signature, mirroring a real Typst Universe package function.
typst_template_function = {
    "name": "ieee",
    "params": {
        "abstract": "Package-path lang non-regression fixture abstract.",
        "index-terms": ["Fixture", "Gate", "Regression"],
        "paper-size": "a4",
    },
}

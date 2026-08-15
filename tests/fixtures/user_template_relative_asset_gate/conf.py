# Sphinx configuration for the user_template_relative_asset_gate fixture
# (Phase 54, OUT-05).
#
# ROADMAP constraint #7 measured that all three real templates in this
# repository (the bundled default, docs/source/_typst/custom_template.typ,
# and the srcdir-shadow fixture) carry font-family references only -- none
# of them proves that a USER template's own path-RELATIVE asset reference
# (e.g. `#image("logo.png")`) survives the per-key bundle relocation this
# phase introduces. This fixture exists solely to supply that missing
# proof; SC#3 explicitly forbids the built-in template from standing in as
# evidence for this gate.
#
# `_typst/branded.typ` deliberately lives ONE DIRECTORY BELOW this file
# (never at srcdir root) so its parent (`_typst/`) is a genuine bundle
# directory -- the invariant D-14 exists to establish (a resolved
# template's parent directory is what gets copied wholesale to
# `<outdir>/_template/<key>/`; if the template lived at srcdir root, the
# "bundle" would be the entire source tree).
#
# `_typst/branded.typ`'s `#image("logo.png", ...)` call is the single
# load-bearing line in this fixture -- nobody may "clean it up" or replace
# it with a path-independent construct. It is what proves the bundle copy
# carries a same-directory asset alongside the template file, so a
# relative Typst reference inside the template body has something to
# resolve against once both land at `<outdir>/_template/typst/`.

project = "User Template Relative Asset Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

typst_template = "_typst/branded.typ"

# The target is the bare string "master", never the identity string
# "index" -- an identity target makes the wrapper resolve onto its own
# content file and produces a cyclic import (the fixture de-collision rule
# this repository already applies in
# tests/fixtures/typst_lang_gate/srcdir_shadow_lang/conf.py).
typst_documents = [
    ("index", "master", project, author),
]

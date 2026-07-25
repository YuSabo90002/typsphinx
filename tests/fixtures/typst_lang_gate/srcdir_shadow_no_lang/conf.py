# Sphinx configuration for the GATE-01 typst `lang` gate's D-08 case (2):
# a `<srcdir>/base.typ` SHADOW of the bundled default template,
# declaring NO `lang` parameter, combined with Sphinx `language = "ja"`
# (Phase 27.1, CONF-07, SC#3) -- the DIRECT proof of the D-06 judgment
# boundary.
#
# CRITICAL: this conf.py deliberately sets NEITHER `typst_template` NOR
# `typst_package`. That is exactly the shape that silently shadows the
# bundled `templates/base.typ` with the sibling `base.typ` file placed
# at THIS directory's root (`TemplateEngine`'s Priority 2 search:
# `search_paths=[srcdir]`, `template_name="base.typ"` -- see
# 27.1-CONTEXT.md's measured-fact table). A declaration-based judgment
# of "is the default template in use?" (`typst_template is None and
# typst_package is None`) would wrongly answer yes here and inject a
# `lang` argument the shadow template never declared -- exactly the
# `unexpected argument: lang` fatal `uses_bundled_default_template()`
# exists to prevent, by judging from the actual `resolve_template()`
# result instead.

project = "Typst Lang Gate Srcdir Shadow No Lang Proof"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# index must be a master document (not merely an included one) so the
# writer applies the full template routing and TypstPDFBuilder.finish()
# actually compiles it to PDF.
typst_documents = [
    ("index", "index", project, author),
]

# The Sphinx language that would auto-derive to "ja" -- but only on the
# TRUE default-template path, which this fixture's `<srcdir>/base.typ`
# shadow deliberately is NOT.
language = "ja"

# NOTE: `typst_template` and `typst_package` are BOTH deliberately left
# unset -- the shadow at `<srcdir>/base.typ` (this same directory) is
# what actually gets loaded.

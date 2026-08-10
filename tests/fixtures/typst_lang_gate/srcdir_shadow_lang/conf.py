# Sphinx configuration for the GATE-01 typst `lang` gate's CONF-12/D-I
# case (2): a `<srcdir>/base.typ` SHADOW of the bundled default template
# that DOES declare `lang`, combined with Sphinx `language = "ja"` -- the
# DIRECT proof that D-I's widened judgment covers the search-path shadow
# route too.
#
# CRITICAL: this conf.py deliberately sets NEITHER `typst_template` NOR
# `typst_package`. That is exactly the shape that silently shadows the
# bundled `templates/base.typ` with the sibling `base.typ` file placed
# at THIS directory's root (`TemplateEngine`'s Priority 2 search:
# `search_paths=[srcdir]`, `template_name="base.typ"`).
# `TemplateEngine.uses_bundled_default_template()` is narrowed by D-I to
# `not self.typst_package`, so it now returns `True` here too -- the
# shadow's own `lang` parameter receives the auto-derived value.

project = "Typst Lang Gate Srcdir Shadow Lang Proof"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# index must be a master document (not merely an included one) so the
# writer applies the full template routing and TypstPDFBuilder.finish()
# actually compiles it to PDF.
typst_documents = [
    ("index", "index", project, author),
]

# The Sphinx language that auto-derives to "ja" on this route now that
# D-I widens uses_bundled_default_template() to every non-package path.
language = "ja"

# NOTE: `typst_template` and `typst_package` are BOTH deliberately left
# unset -- the shadow at `<srcdir>/base.typ` (this same directory) is
# what actually gets loaded.

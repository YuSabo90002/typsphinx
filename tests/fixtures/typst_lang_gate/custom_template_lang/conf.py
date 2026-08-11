# Sphinx configuration for the GATE-01 typst `lang` gate's CONF-12/D-I
# case (1): an EXPLICITLY configured custom `typst_template` that DOES
# declare `lang`, combined with Sphinx `language = "ja"`.
#
# Proves D-I's widened contract: `TemplateEngine.uses_bundled_default_
# template()` is narrowed to `not self.typst_package`, so it now returns
# `True` for this explicit-template route (it no longer checks
# `resolve_template().source`). `writer.py`'s `auto_lang` block therefore
# fires here, and the real user template
# (`_templates/custom.typ`, matching `typsphinx/templates/base.typ`'s
# nine-parameter signature -- see that file's header comment) receives
# the derived Japanese `lang` code in its `project.with(...)` call and
# compiles to a valid PDF. Renamed from `custom_template_no_lang`; its
# pre-change ABSENT verdict is recorded in `45.1-GATE-EVIDENCE-03.md`.

project = "Typst Lang Gate Custom Template Lang Proof"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# index must be a master document (not merely an included one) so the
# writer applies the full template routing and TypstPDFBuilder.finish()
# actually compiles it to PDF.
# Phase 47 (OUT-01/BLD-03): the target is "master", not the identity
# "index" -- since a typst_documents target is now a literal output
# path, an identity target would make the wrapper resolve onto this
# docname's own content file (index.typ) and silently overwrite it with
# a self-referential #include(), producing "TypstError: cyclic import"
# (47-EXPECTED-STRUCTURE.md's fixture de-collision rule).
typst_documents = [
    ("index", "master", project, author),
]

# The Sphinx language that auto-derives to "ja" on this route now that
# D-I widens uses_bundled_default_template() to every non-package path.
language = "ja"

# Explicit custom template that DOES declare `lang` (CONF-12/D-I case 1).
typst_template = "_templates/custom.typ"

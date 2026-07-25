# Sphinx configuration for the GATE-01 typst `lang` gate's D-08 case (1):
# an EXPLICITLY configured custom `typst_template` that declares NO `lang`
# parameter, combined with Sphinx `language = "ja"` (Phase 27.1, CONF-07,
# SC#3).
#
# This proves the non-regression half of CONF-07: a real pre-existing
# user template (`_templates/custom.typ`, derived from the bundled
# `templates/base.typ` by removing the `lang` parameter Plan 01 added --
# see that file's header comment) must build and compile successfully
# with NO `lang` argument injected into its `project.with(...)` call.
# `TemplateEngine.uses_bundled_default_template()` returns `False` here
# because `resolve_template().source == "explicit"` (Priority 1), so
# `writer.py` never computes `auto_lang` for this path at all.

project = "Typst Lang Gate Custom Template No Lang Proof"
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
# DEFAULT template path, which this fixture deliberately is NOT on.
language = "ja"

# Explicit custom template that declares no `lang` parameter (D-08 case 1).
typst_template = "_templates/custom.typ"

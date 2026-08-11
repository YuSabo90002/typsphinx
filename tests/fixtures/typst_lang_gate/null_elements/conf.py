# Sphinx configuration for the GATE-01 typst `lang` gate's
# `typst_elements = None` non-abort regression proof (Phase 27.1,
# CONF-07).
#
# `app.add_config_value("typst_elements", {}, "html", [dict])` declares a
# dict type, but Sphinx only WARNS on a wrong-typed config value -- it
# does not reject it. So a conf.py that sets `typst_elements = None`
# reaches `writer.py` as an actual None, and `getattr(config,
# "typst_elements", {})`'s default never fires (the attribute exists).
#
# `map_parameters()` has always normalized that with `(typst_elements or
# {})`, so this configuration built fine before Phase 27.1. The D-05
# pre-merge added in this phase performs a dict union BEFORE
# map_parameters() sees the value, and a union with None raises
# `TypeError: unsupported operand type(s) for |: 'dict' and 'NoneType'`,
# aborting the entire build. This fixture pins the normalization so that
# regression cannot come back.
#
# Uses the DEFAULT (unset `typst_template`/`typst_package`) template path
# with a derivable `language`, so `auto_lang` is non-None and the union's
# left operand is non-empty -- i.e. the exact path that crashed.

project = "Typst Lang Gate Null Elements Proof"
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

# Derivable language -> auto_lang == "ja" -> non-empty left operand.
language = "ja"

# The regression trigger: a wrong-typed value Sphinx only warns about.
typst_elements = None

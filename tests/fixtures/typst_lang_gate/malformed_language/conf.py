# Sphinx configuration for the GATE-01 typst `lang` gate's malformed-value
# non-abort proof (Phase 27.1, CONF-07, SC#4).
#
# Sets Sphinx `language` to a CJK string that cannot be reduced to a
# two- or three-letter ASCII code -- this is the LOAD-BEARING case,
# because it is exactly the input a Unicode-aware `str.isalpha()` check
# would wrongly accept (Python's `str.isalpha()` answers True for CJK
# code points; `derive_typst_lang()` deliberately uses the ASCII-scoped
# `re.fullmatch(r"[a-z]{2,3}", head)` instead -- 27.1-CONTEXT.md's
# realized-fact table: a locale value like this compiles to a hard
# `TypstError: expected two or three letter language code` if it were
# ever forwarded unvalidated).
#
# This fixture proves the OPPOSITE: `derive_typst_lang()` rejects this
# value, warns via `logger.warning` (proven at the unit tier by Plan 01's
# caplog test -- NOT re-asserted here against subprocess stderr, since
# the warning is emitted through a stdlib module logger rather than
# Sphinx's own logging hierarchy), and omits `lang` entirely so
# `templates/base.typ`'s own `lang: "en"` parameter default applies. The
# build must NOT abort (D-03).
#
# Uses the DEFAULT (unset `typst_template`/`typst_package`) template
# path -- `lang` is only auto-derived (and therefore only eligible to be
# rejected) on that path (D-06/CONF-07).

project = "Typst Lang Gate Malformed Language Proof"
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

# A Sphinx `language` value that cannot be reduced to a valid two- or
# three-letter ASCII code (SC#4) -- must not abort the build.
language = "日本語"

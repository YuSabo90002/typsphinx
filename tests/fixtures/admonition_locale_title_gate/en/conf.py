# Sphinx configuration for the G-39-1 locale title precedence gate --
# ENGLISH sub-project.
#
# Proves that the Sphinx locale catalog title (`sphinx.locale.
# admonitionlabels`, via `custom_title` in `_visit_admonition`) still beats
# gentle-clues' own per-id linguify default title, for BOTH new red-family
# function ids (`danger`, `memo`) that G-39-1 introduces. `index` must be a
# master document (not merely an included one) so the writer emits the full
# template plus the gentle-clues @preview wildcard import (see
# typsphinx/writer.py's master-vs-included branch).
#
# Content stays ASCII-only in both this and the sibling `ja/` sub-project --
# this gate asserts on the emitted title *argument* and on English PDF text,
# never on rendered Japanese glyphs, so the build must not depend on CJK
# font availability. Same reasoning and the same "same content, different
# locale setting" fixture shape as
# `tests/fixtures/typst_lang_gate/ja_default/conf.py` (CONF-07 precedent).

project = "Admonition Locale Title Gate (English)"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# Phase 47 (OUT-01/BLD-03): the target is "master", not the identity
# "index" -- since a typst_documents target is now a literal output path,
# an identity target would make the wrapper resolve onto this docname's
# own content file (index.typ) and silently overwrite it with a
# self-referential #include(), producing "TypstError: cyclic import" (or,
# for a text-only -b typst build, silently discarding the translated
# admonition body this gate's assertions read).
typst_documents = [
    ("index", "master", project, author),
]

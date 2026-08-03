# Sphinx configuration for the G-39-1 locale title precedence gate --
# JAPANESE sub-project.
#
# Same content as the sibling `en/` sub-project, with `language = "ja"` set
# so the Sphinx locale catalog resolves `sphinx.locale.admonitionlabels` in
# Japanese instead of English (D-04's mechanism, 39-CONTEXT.md). `index`
# must be a master document so the writer emits the full template plus the
# gentle-clues @preview wildcard import.
#
# Content stays ASCII-only -- this gate proves the Japanese half at the
# emitted-SOURCE tier only, never by extracting CJK glyphs from a compiled
# PDF, because CJK glyph extraction depends on system font availability
# this project has never pinned. This is the same deliberate split
# `tests/fixtures/typst_lang_gate/ja_default/conf.py` records for CONF-07,
# taken here for the same reason.

project = "Admonition Locale Title Gate (Japanese)"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

typst_documents = [
    ("index", "index", project, author),
]

# The Sphinx language whose catalog resolution this fixture proves reaches
# the emitted title argument (D-04/D-05).
language = "ja"

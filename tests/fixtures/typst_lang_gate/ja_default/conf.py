# Sphinx configuration for the GATE-01 typst `lang` gate's Japanese
# SOURCE proof (Phase 27.1, CONF-07, SC#1's D-07 "source half").
#
# D-07 deliberately splits SC#1's proof in two: this fixture proves the
# `ja` half at the emitted-source tier ONLY -- a real `-b typstpdf` build
# must succeed and the emitted master's `#show: project.with(...)` region
# must carry a quoted `lang: "ja"` entry. This is deliberately
# font-independent: it does NOT extract PDF text, because CJK glyph
# extraction depends on system CJK font availability that the CI ubuntu
# runner has never confirmed (see 27.1-CONTEXT.md D-07). The actual
# supplement-language LINKAGE proof (the case that matters for Phase 25's
# captioned-table motivation) lives in the sibling `de_default` fixture,
# whose supplement words are Latin-script and stable across every OS.
#
# Content is deliberately ASCII-only -- this case asserts on emitted
# Typst SOURCE, not on rendered glyphs, so keeping the body ASCII keeps
# the compile independent of whatever fonts the runner has installed.
#
# Uses the DEFAULT (unset `typst_template`/`typst_package`) template
# path -- `lang` is only auto-derived on that path (D-06/CONF-07).

project = "Typst Lang Gate Japanese Source Proof"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# index must be a master document (not merely an included one) so the
# writer applies the full template routing and TypstPDFBuilder.finish()
# actually compiles it to PDF.
typst_documents = [
    ("index", "index", project, author),
]

# The Sphinx language whose Typst-lang conversion this fixture proves
# reaches the emitted show-rule region (D-02: "ja" -> "ja").
language = "ja"

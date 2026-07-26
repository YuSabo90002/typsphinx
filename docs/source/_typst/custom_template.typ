// Custom Typst template for typsphinx's own documentation builds (English
// AND Japanese -- this file is reached from docs/source/conf.py's
// `typst_template` setting, and conf.py is shared byte-for-byte between the
// `typsphinx` (en) and `typsphinx-doc-translations` (ja) Read the Docs
// projects, so this template renders both PDFs).
//
// Gap-closure round, Phase 30.1, Plan 11, owner-selected option-b
// (30.1-EVIDENCE.md SS "Gap round -- SC#4 fix decision, owner's reply").
// It is a copy of the bundled default template (typsphinx/templates/base.typ)
// with exactly one behavioural change: `set text(...)` below now names an
// explicit font fallback list instead of relying on Typst's fully-automatic
// font-fallback search.
//
// Why: Typst's automatic fallback search silently failed to select a glyph
// for three ordinary CJK Unified Ideographs -- 発 (U+767A), 単 (U+5358), 釈
// (U+91C8) -- in the Japanese PDF, even though the RTD build container has
// several fontconfig-visible, typst.Fonts()-enumerated fonts that declare
// coverage for all three, including HanaMinA itself, the exact font Typst
// used successfully for hundreds of other kanji in the same document
// (30.1-EVIDENCE.md SS "Gap round -- SC#4 font measurement inside the RTD
// build container"; SS "Gap round -- SC#4 root cause, page-count
// reconciliation and scope decision"). Naming a font explicitly is
// UNPROVEN to bypass this: this round's own root-cause finding states
// plainly that automatic fallback already tried (and failed with) a
// covering font, so this is a genuine experiment, not a guaranteed fix.
//
// Font choice, and why: "Noto Serif CJK JP" is named because the RTD build
// container's own `fc-list`/`typst.Fonts()` measurement (recorded in the
// section named above) enumerated "Noto Serif CJK JP" (and its sibling
// Noto Serif/Sans CJK families) on that exact container, arriving via the
// `fonts-noto-cjk` apt package both `.readthedocs.yaml` manifests already
// declare (T-30.1-24: no new font binary, no download, a package already in
// `build.apt_packages` on both sides). "Libertinus Serif" is kept first in
// the list so the Latin body text this template already produced (the
// bundled default's un-set, Typst-default font) stays visually unchanged
// for the English documentation and for every non-CJK character in the
// Japanese documentation.

#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *

#import "@preview/mitex:0.2.7": *

#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()

// Configure codly with codly-languages for comprehensive language support
#codly(languages: codly-languages)

// FID-13: distinguish external hyperlinks with color + underline (D-01).
// Scoped to external URLs only -- `it.dest` is a `str` for an external
// `link("url", ...)` call and a `label` for an internal cross-reference
// (`link(<label>, ...)`), so internal refs stay unstyled (D-02).
#show link: it => {
  if type(it.dest) == str {
    underline(text(fill: blue, it.body))
  } else {
    it
  }
}

#let project(
  title: "",
  authors: (),
  date: none,
  toctree_maxdepth: 2,
  toctree_numbered: false,
  toctree_caption: "Contents",
  papersize: "a4",
  fontsize: 11pt,
  lang: "en",
  body
) = {
  // Document metadata
  set document(title: title, author: authors)

  // Page setup
  set page(
    paper: papersize,
    numbering: "1",
    number-align: center
  )

  // Text setup -- explicit font fallback list (Plan 11, option-b). See the
  // file-level comment above for the measurement basis of both entries.
  set text(
    size: fontsize,
    lang: lang,
    font: ("Libertinus Serif", "Noto Serif CJK JP"),
  )

  // Heading setup
  set heading(numbering: "1.1")

  // Title page
  align(center)[
    #text(2em, weight: "bold")[#title]
    #v(1em)
    #text(1.2em)[#authors.join(", ")]
    #v(0.5em)
    #date
  ]

  pagebreak()

  // Table of Contents
  // Requirement 13.8: #outline() managed at template level, not in body
  // Requirement 8.12, 8.13: toctree options mapped to #outline() parameters
  if toctree_caption != "" [
    #heading(outlined: false)[#toctree_caption]
  ]
  outline(
    depth: toctree_maxdepth,
    indent: auto
  )

  pagebreak()

  // Document body
  // Requirement 13: body contains #include() directives from toctree
  body
}

// OUT-05 gate template (Phase 54). The `#image("logo.png", width: 24pt)`
// call below is the single load-bearing line in this fixture -- it is
// what proves a user template's own relative asset reference resolves
// once the template bundle (this file's parent directory, `_typst/`) is
// copied wholesale to `<outdir>/_template/typst/`. Nobody may "clean it
// up" or replace it with a path-independent construct.
//
// No `@preview` package imports are declared here -- this fixture
// deliberately abstains so it never becomes a fourth version-lockstep
// site (CLAUDE.md "The `@preview` version-sync hazard";
// tests/test_preview_version_sync.py asserts the existing three agree).
//
// Signature matches typsphinx/templates/base.typ's nine-parameter
// contract verbatim, with defaults for every parameter that may be
// absent (docs/source/user_guide/templates.rst lines 205-237).

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
  set document(title: title, author: authors)

  set page(
    paper: papersize,
    numbering: "1",
    number-align: center
  )

  set text(size: fontsize, lang: lang)

  set heading(numbering: "1.1")

  align(center)[
    #image("logo.png", width: 24pt)
    #text(2em, weight: "bold")[#title]
    #v(1em)
    #text(1.2em)[#authors.join(", ")]
    #v(0.5em)
    #date
  ]

  pagebreak()

  if toctree_caption != "" [
    #heading(outlined: false)[#toctree_caption]
  ]
  outline(
    depth: toctree_maxdepth,
    indent: auto
  )

  pagebreak()

  body
}

// D-08 case (1): a real, pre-existing-shape user template that declares
// NO `lang` parameter -- derived from `typsphinx/templates/base.typ` by
// REMOVING the `lang` parameter Plan 01 added to `project()` and
// reverting `set text(size: fontsize, lang: lang)` back to the hardcoded
// `set text(size: fontsize, lang: "en")` literal it replaced. This
// reproduces the exact shape a genuine pre-existing user template has
// today (see `examples/advanced/_templates/custom.typ` and
// `examples/charged-ieee/approach2/source/_templates/_template.typ`,
// both of which declare no `lang` parameter) rather than a synthetic
// stub -- CONF-07/SC#3's non-regression case: an explicitly configured
// `typst_template` that never declared `lang` must build successfully
// with NO `lang` argument injected into its `project.with(...)` call.

#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": *
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()

#codly(languages: codly-languages)

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
  body
) = {
  set document(title: title, author: authors)

  set page(
    paper: papersize,
    numbering: "1",
    number-align: center
  )

  set text(size: fontsize, lang: "en")

  set heading(numbering: "1.1")

  align(center)[
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

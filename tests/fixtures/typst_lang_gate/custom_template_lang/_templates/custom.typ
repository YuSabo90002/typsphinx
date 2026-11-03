// CONF-12/D-I case (1): an explicitly configured `typst_template` that
// DOES declare `lang`, matching `typsphinx/templates/base.typ`'s
// nine-parameter signature. Before D-I, `uses_bundled_default_template()`
// withheld `lang` from every explicit-template route on the theory that
// such a template might not declare it; D-A's published nine-parameter
// contract removes that rationale, so this fixture now proves the
// positive case: an explicit template that DOES declare `lang` receives
// the auto-derived value, and a real `typst.compile()` succeeds.
// Directly contradicts the pre-change ABSENT verdict recorded for this
// fixture (then named `custom_template_no_lang`) in
// `45.1-GATE-EVIDENCE-03.md`.

// Package names come from the build's generated /_typsphinx/deps.typ (no
// version pins here); the wrapper applies the typsphinx-init show rule.
#import "/_typsphinx/deps.typ": *

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
  set document(title: title, author: authors)

  set page(
    paper: papersize,
    numbering: "1",
    number-align: center
  )

  set text(size: fontsize, lang: lang)

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

// TWO-KEY-GATE-REPORT-TEMPLATE
//
// TPL-02/OUT-06 gate template (Phase 54): visibly different from the
// "memo" sibling template (different page size, different text size) so
// a PDF byte-comparison can see the two documents were typeset with
// different templates. Signature matches typsphinx/templates/base.typ's
// nine-parameter contract. No `@preview` imports declared (avoids a
// fourth version-lockstep site -- CLAUDE.md "The `@preview`
// version-sync hazard").

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
    paper: "a4",
    numbering: "1",
    number-align: center
  )

  set text(size: 11pt, lang: lang)

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

// CONF-11 / D-B gate fixture: a custom template declaring exactly ONE
// named parameter (`subtitle`) plus the trailing positional `body` --
// deliberately no `title`, no `authors`, no `date`. Before this phase's
// fix, the auto-derived title/authors/date and toctree_*/typst_elements
// keys would ALSO be passed here and abort the Typst compile with
// `unexpected argument: ...`, since this function declares no keyword
// parameters to absorb them.
#let project(subtitle: "", body) = {
  set page(paper: "a4")
  set text(size: 11pt)

  align(center)[
    #text(2em, weight: "bold")[Partial Params Template Gate]
    #v(0.5em)
    #text(1.2em)[#subtitle]
  ]

  pagebreak()

  body
}

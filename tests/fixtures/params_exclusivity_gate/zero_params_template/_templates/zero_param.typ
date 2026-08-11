// CONF-11 / D-B / D-D gate fixture: a custom template declaring NO named
// parameters at all -- only the trailing positional `body`. Before this
// phase's fix, ANY non-empty auto-derived or `typst_elements`/`toctree_*`
// argument being passed into this call would abort the Typst compile with
// `unexpected argument: ...`, since this function declares no keyword
// parameters to absorb them.
#let project(body) = {
  set page(paper: "a4")
  set text(size: 11pt, lang: "ja")

  align(center)[
    #text(2em, weight: "bold")[Zero Params Template Gate]
  ]

  pagebreak()

  body
}

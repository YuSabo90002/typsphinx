// SC#3 / D-K gate fixture: the "Basic Structure" custom template
// published verbatim in docs/source/user_guide/templates.rst, declaring
// EXACTLY the nine published parameters (matching
// typsphinx/templates/base.typ:39-50 name for name, order for order,
// default for default) plus the trailing positional `body`. No named
// argument this build can pass is left undeclared, and no declared
// parameter is left unaccounted for -- this is SC#1's literal proof
// case.
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
  // Title page
  align(center)[
    #text(size: 24pt, weight: "bold")[#title]
    #v(1em)
    #text(size: 14pt)[#authors.join(", ")]
    #if date != none {
      v(1em)
      text(size: 12pt)[#date]
    }
  ]

  pagebreak()

  // Table of contents
  outline(title: "Contents", indent: auto)

  pagebreak()

  // Document body
  body
}

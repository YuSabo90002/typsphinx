// Phase 54.1 plan 04, task 1: the "beta" registry key's template. Its
// PARENT directory (`_templates/nested/`) IS CONTAINED BY this
// fixture's `templates_path = ["_templates", "_typst/inner"]` first
// entry -- the "bundle dir contained by an entry" relation of D-02's
// three-way containment test. Declares the same nine-parameter contract
// as alpha.typ, as a belt-and-braces property -- this fixture's build is
// expected to be REFUSED before compilation is ever attempted. Declares
// NO Typst Universe package imports -- this fixture must never become a
// fifth version-lockstep site (CLAUDE.md).
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
  set page(paper: papersize)
  set text(size: fontsize, lang: lang)

  align(center)[
    #text(2em, weight: "bold")[#title]
    #v(1em)
    #text(1.2em)[#authors.join(", ")]
    #if date != none {
      v(0.5em)
      text(1em)[#date]
    }
  ]

  pagebreak()

  body
}

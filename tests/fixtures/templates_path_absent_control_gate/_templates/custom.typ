// Phase 54.1 plan 04, task 2: the absent-control's real, compilable
// template. Declares the nine-parameter contract
// docs/source/user_guide/templates.rst publishes, so this control
// fixture's build genuinely succeeds and writes a real .typ set, not
// merely exits 0. Declares NO Typst Universe package imports -- this
// fixture must never become a fifth version-lockstep site (CLAUDE.md).
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

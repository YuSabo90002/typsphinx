// Phase 54.1 plan 05, task 1: the fixture template deliberately placed
// at the source-tree ROOT -- its parent directory IS srcdir, which is
// exactly what CONF-17/A-01 forbids. This fixture's build is expected
// to be REFUSED before compilation is ever attempted, so this file's
// own correctness is a belt-and-braces property, not the thing under
// test. Declares NO Typst Universe package imports -- this fixture
// must never become a fourth version-lockstep site (CLAUDE.md).
#let project(
  title: "",
  authors: (),
  date: none,
  body
) = {
  set page(paper: "a4")

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

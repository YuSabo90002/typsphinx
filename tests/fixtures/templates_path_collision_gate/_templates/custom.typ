// Phase 54.1 plan 01, task 1: the fixture template whose PARENT
// directory (`_templates/`) deliberately collides with the fixture's
// own `templates_path = ["_templates"]` setting (conf.py). Declares the
// nine-parameter contract docs/source/user_guide/templates.rst
// publishes (title/authors/date/toctree_maxdepth/toctree_numbered/
// toctree_caption/papersize/fontsize/lang, then the trailing positional
// body) so this template compiles regardless of which of those
// parameters a given build happens to pass -- this fixture's build is
// expected to be REFUSED before compilation is ever attempted, so this
// file's own correctness is a belt-and-braces property, not the thing
// under test. Declares NO Typst Universe package imports -- this fixture
// must never become a fourth version-lockstep site (CLAUDE.md).
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

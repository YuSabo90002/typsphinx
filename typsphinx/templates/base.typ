// Default Typst template for sphinx-typst
// Requirement 8.1: Default template bundled with package
// Requirement 8.11: Include #outline() in template (not in body)
// Requirement 7.4: codly package integration for code highlighting

// Typst Universe packages (codly, codly-languages, mitex, gentle-clues,
// diagraph) come from the build's generated /_typsphinx/deps.typ -- the one
// place their versions are pinned (Design 3.3/3.5/3.6, Requirement 4.1,
// 2.8-2.10, 7.4). The wrapper applies the typsphinx-init show rule (codly language
// registration) itself, so this template does not.
#import "/_typsphinx/deps.typ": *

// FID-13: distinguish external hyperlinks with color + underline (D-01).
// Scoped to external URLs only -- `it.dest` is a `str` for an external
// `link("url", ...)` call and a `label` for an internal cross-reference
// (`link(<label>, ...)`), so internal refs stay unstyled (D-02).
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
  // Document metadata
  set document(title: title, author: authors)

  // Page setup
  set page(
    paper: papersize,
    numbering: "1",
    number-align: center
  )

  // Text setup
  set text(size: fontsize, lang: lang)

  // Heading setup
  set heading(numbering: "1.1")

  // Title page
  align(center)[
    #text(2em, weight: "bold")[#title]
    #v(1em)
    #text(1.2em)[#authors.join(", ")]
    #v(0.5em)
    #date
  ]

  pagebreak()

  // Table of Contents
  // Requirement 13.8: #outline() managed at template level, not in body
  // Requirement 8.12, 8.13: toctree options mapped to #outline() parameters
  if toctree_caption != "" [
    #heading(outlined: false)[#toctree_caption]
  ]
  outline(
    depth: toctree_maxdepth,
    indent: auto
  )

  pagebreak()

  // Document body
  // Requirement 13: body contains #include() directives from toctree
  body
}

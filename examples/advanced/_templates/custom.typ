// Custom Typst Template for Sphinx-Typst
// This is an example of a custom template that can be used with typsphinx
//
// To use this template, uncomment the following line in conf.py:
//   typst_template = '_templates/custom.typ'

// Import required packages
// Keep these versions in lockstep with typsphinx's own bundled template
// (typsphinx/templates/base.typ) — tests/test_preview_version_sync.py
// enforces it, because a stale pin here fails to compile at all (an old
// codly-languages aborts with `unknown variable: kai`).
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": *
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly for code highlighting
#show: codly-init.with()
#codly(languages: codly-languages)

// Custom styling
#let primary-color = rgb(0, 102, 204)

// Heading styling
#show heading.where(level: 1): it => block(
  width: 100%,
  above: 1.5em,
  below: 1em,
)[
  #set text(size: 20pt, weight: "bold", fill: primary-color)
  #it.body
]

#show heading.where(level: 2): it => block(
  width: 100%,
  above: 1.2em,
  below: 0.8em,
)[
  #set text(size: 16pt, weight: "bold", fill: primary-color.lighten(20%))
  #it.body
]

#show heading.where(level: 3): it => block(
  width: 100%,
  above: 1em,
  below: 0.6em,
)[
  #set text(size: 14pt, weight: "bold")
  #it.body
]

// Link styling
#show link: set text(fill: primary-color)

// Code block styling
// Note: Using default Typst theme (custom themes require theme file in project directory)
// #set raw(theme: "halcyon.tmTheme")

// Paragraph spacing
#set par(
  first-line-indent: 0pt,
  justify: true,
  leading: 0.65em,
)

// List styling
#set list(indent: 1em, marker: [•])
#set enum(indent: 1em)

// Title page function
#let title-page(title, author, date) = {
  set page(numbering: none)

  v(2fr)

  align(center)[
    #text(size: 28pt, weight: "bold", fill: primary-color)[#title]

    #v(1em)

    #text(size: 14pt)[#author]

    #v(0.5em)

    #text(size: 12pt, fill: gray)[#date]
  ]

  v(3fr)

  pagebreak()
}

// Main template function
// This function is called by typsphinx with the document content
#let project(
  title: "Document Title",
  authors: (),
  date: none,
  toctree_maxdepth: 2,
  toctree_numbered: false,
  toctree_caption: "Contents",
  // A custom template receives a `typst_elements` key ONLY if it declares a
  // matching parameter here — an undeclared key is a hard Typst compile
  // error (`unexpected argument: papersize`). These three mirror the
  // parameters typsphinx's bundled base.typ exposes, so the conf.py setting
  //   typst_elements = {"papersize": ..., "fontsize": ..., "lang": ...}
  // actually reaches the page.
  papersize: "a4",
  fontsize: 11pt,
  lang: "en",
  body,
) = {
  // Set document metadata
  set document(
    title: title,
    author: authors,
  )

  // Page setup
  set page(
    paper: papersize,
    margin: (x: 2.5cm, y: 2.5cm),
    header: align(right)[
      #text(size: 10pt, fill: gray)[_Custom Template Example_]
    ],
    numbering: "1",
  )

  // Text styling
  set text(
    font: "Linux Libertine",
    size: fontsize,
    lang: lang,
  )

  // Display title page
  // Convert authors array to string for title page
  let author_str = if authors.len() > 0 { authors.join(", ") } else { "" }
  title-page(title, author_str, date)

  // Table of contents
  outline(
    title: "Contents",
    indent: auto,
    depth: 3,
  )

  pagebreak()

  // Main content
  body
}

// Note: The actual document content will be inserted by typsphinx
// When using this template, make sure to wrap your content with the project() function

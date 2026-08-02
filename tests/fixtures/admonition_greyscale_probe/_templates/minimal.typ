// Minimal template for the ADM-04 greyscale-distinguishability probe.
//
// Derived from typsphinx/templates/base.typ (same imports, same #project()
// parameter surface) with the title page, the pagebreak that follows it,
// and the #outline() table of contents REMOVED. The bundled default
// template unconditionally emits title page + TOC + body across three
// pages regardless of how short the body is (measured this session:
// `admonition_greyscale_probe` under the bundled template compiles to 3
// pages), which is incompatible with this fixture's single-page
// requirement (39-RESEARCH.md Pitfall 4 -- typst-py's PNG export needs a
// page-number template in the output filename the moment a document
// exceeds one page). This template exists ONLY to keep the probe to one
// page; it is not a general-purpose replacement for base.typ and is not
// wired into any non-probe fixture.

#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": *
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()

#codly(languages: codly-languages)

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
  set document(title: title, author: authors)

  set page(
    paper: papersize,
    numbering: "1",
    number-align: center
  )

  set text(size: fontsize, lang: lang)

  set heading(numbering: "1.1")

  // No title page, no pagebreak, no #outline() -- straight to the body,
  // so a short probe stays on one page.
  body
}

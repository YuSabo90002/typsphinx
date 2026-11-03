// User-supplied deps.typ for the typst_dependencies override fixture:
// the generated default with gentle-clues pinned to 1.3.0.
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.0": *
#import "@preview/diagraph:0.3.7": render

// Package initialisation, applied by every content file and wrapper.
#let typsphinx-init(body) = {
  show: codly-init.with()
  codly(languages: codly-languages)
  body
}

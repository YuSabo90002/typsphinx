// A user typst_dependencies file: gentle-clues at 1.3.0 instead of the
// default 1.3.1, and no diagraph at all (E9).
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.0": *

#let typsphinx-init(body) = {
  show: codly-init.with()
  codly(languages: codly-languages)
  body
}

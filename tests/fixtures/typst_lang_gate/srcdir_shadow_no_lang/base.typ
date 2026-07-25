// D-08 case (2): a `<srcdir>/base.typ` shadow of the bundled default
// template, declaring NO `lang` parameter -- the DIRECT proof of the
// D-06 judgment boundary. `TemplateEngine.resolve_template()`'s Priority
// 2 (search-path hit) finds THIS file even though this fixture's conf.py
// sets neither `typst_template` nor `typst_package` -- exactly the shape
// a declaration-based check (`typst_template is None and typst_package
// is None`) would mistake for "the bundled default is in use" and would
// then inject a `lang` argument this file never declared, aborting the
// Typst compile with `unexpected argument: lang`.
// `uses_bundled_default_template()` correctly returns `False` here
// because it judges from the ACTUAL resolution result
// (`resolve_template().source == "search"`, not `"default"`).
//
// Derived from `typsphinx/templates/base.typ` by REMOVING the `lang`
// parameter Plan 01 added to `project()` and reverting
// `set text(size: fontsize, lang: lang)` back to the hardcoded
// `set text(size: fontsize, lang: "en")` literal it replaced -- see
// `tests/fixtures/typst_lang_gate/custom_template_no_lang/_templates/custom.typ`
// for the byte-identical sibling used for D-08 case 1.

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
  body
) = {
  set document(title: title, author: authors)

  set page(
    paper: papersize,
    numbering: "1",
    number-align: center
  )

  set text(size: fontsize, lang: "en")

  set heading(numbering: "1.1")

  align(center)[
    #text(2em, weight: "bold")[#title]
    #v(1em)
    #text(1.2em)[#authors.join(", ")]
    #v(0.5em)
    #date
  ]

  pagebreak()

  if toctree_caption != "" [
    #heading(outlined: false)[#toctree_caption]
  ]
  outline(
    depth: toctree_maxdepth,
    indent: auto
  )

  pagebreak()

  body
}

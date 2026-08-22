// CONF-12/D-I case (2): a `<srcdir>/_typst/base.typ` shadow of the
// bundled default template that DOES declare `lang`, matching
// `typsphinx/templates/base.typ`'s nine-parameter signature.
// `TemplateEngine.resolve_template()`'s Priority 2 (search-path hit)
// finds THIS file even though this fixture's conf.py sets neither
// `typst_template` nor `typst_package`. Before D-I,
// `uses_bundled_default_template()` withheld `lang` here because it
// judged from the resolution result (`resolve_template().source ==
// "search"`, not `"default"`); D-I narrows the judgment to the
// `typst_package` guard alone, so this route now receives `lang` the
// same as every other non-package route. Directly contradicts the
// pre-change ABSENT verdict recorded for this fixture (then named
// `srcdir_shadow_no_lang`) in `45.1-GATE-EVIDENCE-03.md`.
//
// Sibling of `tests/fixtures/typst_lang_gate/custom_template_lang/_templates/custom.typ`
// (CONF-12/D-I case 1), same shape.

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

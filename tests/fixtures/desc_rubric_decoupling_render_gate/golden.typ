// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Desc Rubric Decoupling Render Gate",
  authors: ("typsphinx tests",),
  date: "0.0.0",
  lang: "en",
)

#{
[#heading(level: 1, {text("Desc Rubric Decoupling Render Gate")}) <index:desc-rubric-decoupling-render-gate>]

par({text("This fixture combines a single signature, sibling signatures, plain bold markup, an autodoc-style Options rubric, a rubric carrying a propagated target inside a list item, and a rubric at true end-of-document – the constructs Phase 36’s SC#2 names – into one file, so the desc_signature/ rubric decoupling can be proven to produce byte-identical .typ output.")})

par({text("Single signature with an id anchor.")})

block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("connect"))
raw("(") + emph(raw("host")) + raw(", ") + emph(raw("port")) + raw(", ") + emph(raw("timeout")) + raw("=") + raw("30") + raw(")")}))
[#metadata(none) <index:connect>]
par({text("Connect to ")
emph({text("host")})
text(".")})

parbreak()
par({text("Sibling signatures under one directive.")})

block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
raw("(") + emph(raw("source")) + raw(")")}))
[#metadata(none) <index:compile>]
linebreak()
block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
raw("(") + emph(raw("source")) + raw(", ") + emph(raw("filename")) + raw(")")}))
linebreak()
block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
raw("(") + emph(raw("source")) + raw(", ") + emph(raw("filename")) + raw(", ") + emph(raw("symbol")) + raw(")")}))
par({text("Compile source into a code or AST object.")})

parbreak()
par({text("Plain bold markup – the regression control.")})

par({text("This paragraph contains ")
strong({text("bold text")})
text(" that must keep routing through visit_strong unchanged, byte-identical after the decoupling.")})

par({text("The autodoc “Options” rubric shape.")})


strong({text("Options")})
linebreak()
block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("--sep"))}))
[#metadata(none) <index:cmdoption-sep>]
par({text("If specified, separate source and build directories.")})

parbreak()
par({text("A rubric carrying a propagated target, inside a list item.")})

list({
parbreak()

text("First bullet text.")


[#metadata(none) <index:decoupling-rubric-in-list-target>]


strong({text("A Rubric In A List Item")})

linebreak()

parbreak()

text("More text after the rubric.")
})

par({text("A rubric at true end-of-document.")})


strong({text("Trailing Heading")})
linebreak()

}

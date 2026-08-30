// Essential imports for included document
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()
#codly(languages: codly-languages)

#{
[#metadata(none) <pass_f_figure_with_plain_legend:__tsx-doc__>]
[#heading(depth: 1, {text("Pass F - Figure With Plain Legend")}) <pass_f_figure_with_plain_legend:pass-f-figure-with-plain-legend>]

[#figure(
{
  image("_static/pic.png")
parbreak()

text("A plain legend paragraph, no images here.")
},
  caption: {text("A caption.")}
) <pass_f_figure_with_plain_legend:id1>]


}

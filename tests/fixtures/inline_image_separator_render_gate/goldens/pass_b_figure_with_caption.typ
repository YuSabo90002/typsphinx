// Essential imports for included document
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()
#codly(languages: codly-languages)

#{
[#metadata(none) <pass_b_figure_with_caption:__tsx-doc__>]
[#heading(depth: 1, {text("Pass B - Figure With Caption")}) <pass_b_figure_with_caption:pass-b-figure-with-caption>]

[#figure(
  image("_static/pic.png"),
  caption: {text("A caption.")}
) <pass_b_figure_with_caption:id1>]


}

// Essential imports for included document
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()
#codly(languages: codly-languages)

#{
[#metadata(none) <pass_h_figure_first_in_list_item:__tsx-doc__>]
[#heading(depth: 1, {text("Pass H - Figure First In List Item")}) <pass_h_figure_first_in_list_item:pass-h-figure-first-in-list-item>]

list({
[#figure(
  image("_static/pic.png"),
  caption: {text("Caption.")}
) <pass_h_figure_first_in_list_item:id1>]


})


}

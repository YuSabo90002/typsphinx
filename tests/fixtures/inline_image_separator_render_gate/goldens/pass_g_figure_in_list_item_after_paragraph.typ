// Essential imports for included document
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()
#codly(languages: codly-languages)

#{
[#metadata(none) <pass_g_figure_in_list_item_after_paragraph:__tsx-doc__>]
[#heading(depth: 1, {text("Pass G - Figure In List Item After Paragraph")}) <pass_g_figure_in_list_item_after_paragraph:pass-g-figure-in-list-item-after-paragraph>]

list({
parbreak()

text("First paragraph text.")
[#figure(
  image("_static/pic.png"),
  caption: {text("Caption.")}
) <pass_g_figure_in_list_item_after_paragraph:id1>]


})


}

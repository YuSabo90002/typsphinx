#import "/_typsphinx/deps.typ": *
#show: typsphinx-init

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

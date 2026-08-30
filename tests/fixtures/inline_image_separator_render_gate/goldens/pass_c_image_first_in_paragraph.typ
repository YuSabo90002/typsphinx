// Essential imports for included document
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()
#codly(languages: codly-languages)

#{
[#metadata(none) <pass_c_image_first_in_paragraph:__tsx-doc__>]
[#heading(depth: 1, {text("Pass C - Image First In Paragraph")}) <pass_c_image_first_in_paragraph:pass-c-image-first-in-paragraph>]

par({image("_static/pic.png")


text(" leading image then text.")})


}

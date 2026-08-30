// Essential imports for included document
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()
#codly(languages: codly-languages)

#{
[#metadata(none) <pass_d_image_with_dimensions_and_scale_align:__tsx-doc__>]
[#heading(depth: 1, {text("Pass D - Image With Dimensions And Scale Align")}) <pass_d_image_with_dimensions_and_scale_align:pass-d-image-with-dimensions-and-scale-align>]

image("_static/pic.png", width: 150pt, height: 75pt)

image("_static/pic.png")


}

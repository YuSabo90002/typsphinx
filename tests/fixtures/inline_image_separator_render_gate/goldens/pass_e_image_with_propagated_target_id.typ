// Essential imports for included document
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()
#codly(languages: codly-languages)

#{
[#metadata(none) <pass_e_image_with_propagated_target_id:__tsx-doc__>]
[#heading(depth: 1, {text("Pass E - Image With Propagated Target Id")}) <pass_e_image_with_propagated_target_id:pass-e-image-with-propagated-target-id>]


[#metadata(none) <pass_e_image_with_propagated_target_id:mytarget>]
image("_static/pic.png")


}

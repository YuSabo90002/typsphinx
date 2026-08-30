// Essential imports for included document
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()
#codly(languages: codly-languages)

#{
[#metadata(none) <pass_a_standalone_block_image:__tsx-doc__>]
[#heading(depth: 1, {text("Pass A - Standalone Block Image")}) <pass_a_standalone_block_image:pass-a-standalone-block-image>]

par({text("A leading paragraph before the standalone block image.")})

image("_static/pic.png")

par({text("A trailing paragraph after the standalone block image.")})


}

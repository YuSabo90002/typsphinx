// Minimal user template: takes the parameters typsphinx passes and imports
// none of the Typst Universe packages itself.
#let project(title: "", authors: (), ..rest, body) = {
  set document(title: title)
  heading(level: 1, outlined: false, title)
  body
}

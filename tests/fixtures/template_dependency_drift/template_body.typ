// Minimal template function appended after each scenario's import lines by
// tests/test_template_dependency_drift_gate.py.
#let project(title: "", authors: (), ..rest, body) = {
  set document(title: title)
  heading(level: 1, outlined: false, title)
  body
}

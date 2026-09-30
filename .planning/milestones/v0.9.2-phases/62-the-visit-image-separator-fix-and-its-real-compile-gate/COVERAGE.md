# Phase 62: External API Coverage Declaration

No external API integration: this phase touches one product file (`typsphinx/translator.py`),
adds one new test module (`tests/test_inline_image_separator_render_gate.py`), adds one new test
fixture project (`tests/fixtures/inline_image_separator_render_gate/`) with its committed goldens
(added in a later plan), and writes planning evidence under
`.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/` — no external API,
SDK, service, or endpoint is touched.

Plan-time detector result, recorded verbatim: `{"detected":false,"signals":[]}`

This file exists because the seal-time `api-coverage.verify-pre` gate re-runs the detector over
the concatenated PLAN bodies and has a recorded history of firing on this project's prose (a
phase's plain-English description of test infrastructure and separator-emission fix being
misread as external-API integration language). This file exists so that a false-positive detector
run at seal time is met with a reasoned declaration rather than a fabricated capability matrix — a
matrix for an API this phase does not touch would be worse than no matrix.

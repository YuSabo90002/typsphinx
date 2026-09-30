# Phase 59: External API Coverage Declaration

No external API integration: this phase touches two product files (`typsphinx/builder.py`,
`typsphinx/translator.py`), adds five new test modules
(`tests/test_path_shape_predicate_gate.py`, `tests/test_track_image_key_construction.py`,
`tests/test_copy_image_files_name_too_long.py`, `tests/test_image_literal_escaping_gate.py`,
`tests/test_windows_image_uri_render_gate.py`), adds one new test fixture project
(`tests/fixtures/windows_shaped_image_uri_gate/`), and writes planning evidence under
`.planning/phases/59-path-shape-predicate-and-image-uri-correctness/` — no external API, SDK,
service, or endpoint is touched.

Plan-time detector result, recorded verbatim: `{"detected":false,"signals":[]}`

This file exists because the seal-time `api-coverage.verify-pre` gate re-runs the detector over
the concatenated PLAN bodies and has a recorded history of firing on this project's prose (a
phase's plain-English description of test infrastructure and path-handling being misread as
external-API integration language). This file exists so that a false-positive detector run at
seal time is met with a reasoned declaration rather than a fabricated capability matrix — a
matrix for an API this phase does not touch would be worse than no matrix.

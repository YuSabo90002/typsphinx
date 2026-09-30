# Phase 60: External API Coverage Declaration

No external API integration: this phase touches four product files (one new leaf module,
`typsphinx/pathfmt.py`, plus the three wired modules `typsphinx/builder.py`, `typsphinx/writer.py`,
`typsphinx/template_registry.py`), adds four new test modules (`tests/test_pathfmt.py`,
`tests/test_builder_path_quoting_gate.py`, `tests/test_writer_path_quoting_gate.py`,
`tests/test_template_registry_path_quoting_gate.py`), extends one existing test class
(`TestWindowsPathEscapingRegressionGuard` in `tests/test_templates_path_collision_gate.py`, by
addition only), and writes planning evidence under
`.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/` — no external API,
SDK, service, or endpoint is touched.

Plan-time detector result, recorded verbatim: `{"detected":false,"signals":[]}`

This file exists because the seal-time `api-coverage.verify-pre` gate re-runs the detector over the
concatenated PLAN bodies, and this project has a recorded history of that detector firing on
ordinary engineering prose (a phase's plain-English description of message-formatting helpers and
their call sites being misread as external-API integration language, as seen in Phase 59's own
`COVERAGE.md`). This file exists so that a false-positive detector run at seal time is met with a
reasoned declaration rather than a fabricated capability matrix — a matrix for an API this phase
does not touch would be worse than no matrix.

# Phase 58: External API Coverage Declaration

No external API integration: this phase modifies two files under `tests/`
(`tests/test_out02_escape_target_gate.py`, `tests/test_builder.py` — the latter in a later
plan of this phase), adds three new files under `tests/` (`tests/_path_naming.py`,
`tests/test_path_naming_predicate.py`, `tests/test_repr_census_guard.py` — the last in a later
plan of this phase), writes planning evidence under `.planning/phases/58-repr-format-decoupling-test-side-only/`,
and pushes a git branch — no external API, SDK, service, or endpoint is touched.

Plan-time detector result, recorded verbatim: `{"detected":false,"signals":[]}`

This declaration exists because the seal-time `api-coverage.verify-pre` gate re-runs the
detector over the concatenated PLAN bodies, which on this project has a recorded history of
firing on prose (a phase's plain-English description of test infrastructure being misread as
external-API integration language). This file exists so that a false-positive detector run at
seal time is met with a reasoned declaration rather than a fabricated capability matrix — a
matrix for an API this phase does not touch would be worse than no matrix.

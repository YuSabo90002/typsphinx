# Archive — 007-release-notes-py314

Milestone: release-notes-py314
Shipped: 2026-11-03
Final verdict: all criteria met; project verify passed
Waves: 1  Tasks: 1 done / 1 total  Review cycles used: 1
Carried forward: none

## Success criteria at ship

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Release notes (surface: CHANGELOG.md release notes): `## [0.10.0]` `### Added` contains a bullet stating Python 3.14 support (classifier and CI/tox coverage); `uv run python scripts/extract_changelog_section.py 0.10.0` exits 0 and its output contains `3.14`; the `## [0.10.0] - 2026-11-03` heading line and every other existing 0.10.0 line are unchanged. | met | .project/review/wave-1.cycle1.md — SC1; evidence: Bullet at CHANGELOG.md:52-54 under 0.10.0 `### Added`; extractor exit 0 with `3.14` in output; diff 1feaaf53^..1feaaf53 has no removed CHANGELOG lines; heading at :15 unchanged. E1 dismissed; N1 dismissed. |
| advanced example (surface: docs/source/examples/advanced.rst): the `ieee_abstract` example is written so the string has no embedded newline (single-line or concatenated pieces, same words); passing the example's string value through `typsphinx.template_engine.TemplateEngine._format_typst_value` yields a Typst value containing no line break, checked by a test. | met | .project/review/wave-1.cycle1.md — SC2; evidence: advanced.rst:25-28 concatenated pieces, same words; tests/test_advanced_example_abstract_gate.py 3 passed post-fix, 2 failed on reconstructed pre-fix file. E2 dismissed; N1 dismissed. |
| README (surface: README.md): both `typst_documents` tuple descriptions (around lines 84 and 233) mark `documentclass` as an optional fifth element. | met | .project/review/wave-1.cycle1.md — SC3; evidence: README.md:84-86 and :235 both state the fifth element `documentclass` is optional. E3 dismissed; N1 dismissed. |
| On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean. | met | .project/review/wave-1.cycle1.md — SC4 |

## Contents

- build/evidence.json
- build/verify-ledger.jsonl
- intent/INTENT.md
- plan/PLAN.md
- research/DOCS-AUDIT.md
- research/SYNTHESIS.md
- research/evidence-codebase.md
- review/FINAL.md
- review/final-gap-1.md
- review/wave-1.cycle1.md
- tasks/T001-release-notes-py314-and-doc-fixes.md

## Notes

- none

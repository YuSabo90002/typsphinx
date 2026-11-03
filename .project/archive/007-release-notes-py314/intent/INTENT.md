# Intent — typsphinx

Lane: quick   <!-- three small documentation edits in one task; no RESEARCH or NEEDS-USER items once the audit rulings are recorded; no cross-wave risk -->

Review panel: off

Finding skeptics: off

Surfaces: CHANGELOG.md release notes (`scripts/extract_changelog_section.py 0.10.0` output), docs/source/examples/advanced.rst, README.md

## Summary

Follow-up to M006 before the `v0.10.0` tag is pushed. The 0.10.0 release notes omit Python 3.14 support, which M005 shipped (classifiers, black target, CI matrix, tox — commit 5aee2fb9) without a CHANGELOG entry; one line is added under `## [0.10.0]` `### Added`. The `ieee_abstract` example in `docs/source/examples/advanced.rst` (lines 24–27) uses a triple-quoted multi-line string that renders stray line breaks (measured: break at start, after "learning", at end); it is rewritten to the single-line form M006 used for `examples/charged-ieee/approach1/conf.py`. README.md presents `documentclass` as a required tuple element although it is the optional fifth element. The tag push itself stays outside the milestone (owner instruction after merge).

## Problem

- `CHANGELOG.md` has no Python 3.14 line; `scripts/extract_changelog_section.py 0.10.0` output does not mention 3.14 (evidence-codebase.md).
- `docs/source/examples/advanced.rst:24-27` `ieee_abstract = """\nThis paper presents ...\n"""`: compiled through `TemplateEngine._format_typst_value` with typst-py it shows line breaks at the start, after "learning" and at the end (evidence-codebase.md); the M006 precedent is commit 3c23c646.
- DOCS-AUDIT #4: README.md:83-84 and :233 write `(source, target, title, author, documentclass)` without saying the fifth element is optional.

## Users

typsphinx users reading the 0.10.0 release notes and the advanced example; README readers configuring `typst_documents`.

## Success criteria

1. Release notes (surface: CHANGELOG.md release notes): `## [0.10.0]` `### Added` contains a bullet stating Python 3.14 support (classifier and CI/tox coverage); `uv run python scripts/extract_changelog_section.py 0.10.0` exits 0 and its output contains `3.14`; the `## [0.10.0] - 2026-11-03` heading line and every other existing 0.10.0 line are unchanged.
2. advanced example (surface: docs/source/examples/advanced.rst): the `ieee_abstract` example is written so the string has no embedded newline (single-line or concatenated pieces, same words); passing the example's string value through `typsphinx.template_engine.TemplateEngine._format_typst_value` yields a Typst value containing no line break, checked by a test.
3. README (surface: README.md): both `typst_documents` tuple descriptions (around lines 84 and 233) mark `documentclass` as an optional fifth element.
4. On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

## Edge coverage

| Edge | Criterion | Category | Disposition | Detail |
|------|-----------|----------|-------------|--------|
| E1 | SC1 | none | dismissed | one added bullet in a fixed section |
| E2 | SC2 | none | dismissed | one fixed example string; the check states its exact command |
| E3 | SC3 | none | dismissed | static documentation text |
| E4 | SC4 | none | dismissed | whole-repository command results on one HEAD |

## Prohibitions

| Prohibition | Criterion | Must not | Disposition | Detail |
|-------------|-----------|----------|-------------|--------|
| N1 | all | none | dismissed | documentation edits; no person is affected beyond the stated text |

## Scope: in

- One Python 3.14 bullet under `## [0.10.0]` `### Added` in CHANGELOG.md.
- Rewrite the `ieee_abstract` example in docs/source/examples/advanced.rst to the single-line form, plus a test pinning it.
- README `documentclass` optional wording (DOCS-AUDIT #4, ruled fix-doc).

## Scope: out (vetoes)

- Pushing the `v0.10.0` tag or publishing — owner instruction after the PR merge (M006 Q4 a).
- Changing the 0.10.0 heading date or any other release section.
- Product code changes under `typsphinx/`.

## Constraints

- Python >= 3.12; black/ruff line 88; mypy clean (CLAUDE.md).
- `tests/test_release_0_10_0_docs_gate.py` must keep passing (heading line untouched).
- Integration by pull request (STATE `integration: pull-request`).

## Current state (brownfield only)

- **What exists**: typsphinx 0.10.0 (untagged) at 6defa41d; full suite 1894 passed, 1 skipped.
- **Must not break**: the 0.10.0 release gate, `extract_changelog_section.py` output.
- **Doc-vs-code rulings**: #1–#3 (CLAUDE.md py312–py313 claims): accept-drift — the quoted text does not exist at HEAD (CLAUDE.md:28-29 and :88 already say py312–py314/py314), so the audit rows are erroneous; #4 README documentclass → fix-doc; #5 CHANGELOG `[0.10.0]` link dead until the tag exists → accept-drift (resolved by the planned tag push).
- **Ground truth**: `.project/research/evidence-codebase.md`, `.project/research/DOCS-AUDIT.md`

## Risks

- None beyond keeping the 0.10.0 gate assertions intact.

## Open questions

- none

## Corrections

- C1 2026-11-03: "1" (M006 ship choice: ship, then a follow-up milestone adds the Python 3.14 line and the advanced.rst fix before tagging v0.10.0)
- C2 2026-11-03: "Q1 a  Q2 a  Q3 a  承認"

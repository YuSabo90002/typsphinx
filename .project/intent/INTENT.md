# Intent — typsphinx

Lane: quick   <!-- three small housekeeping slices (contributor/docs text, evidence-file retirement, Python 3.14 declaration) fit at most two deliverable-sized tasks in one wave; no RESEARCH or NEEDS-USER items; no cross-wave risk -->

Review panel: off

Finding skeptics: off

Surfaces: CLAUDE.md, README.md, CHANGELOG.md, examples/charged-ieee/README.md

## Summary

Housekeeping milestone on top of 660e3436 (M002–M004 changes unreleased). CLAUDE.md is brought in line with the code: it names the three undocumented modules (`template_registry.py`, `removed_config.py`, `pathfmt.py`), describes the dominant `tests/fixtures/` subprocess-gate test convention, and states the ubuntu/windows/macos CI matrix. The three retired gsd-pi evidence files `docs/S02/S03/S04-*-EVIDENCE.md` are deleted together with the `tests/test_release_0_9_8_docs_gate.py` checks that read S03/S04. Python 3.14 is declared and tested: classifiers, black `target-version`, the CI test matrix and the tox `env_list`. Three stale doc claims from the docs audit are fixed (README line numbering, CHANGELOG "Planned: Glossary generation", charged-ieee `typst_package` + `typst_template` behaviour). No version bump or release.

## Problem

- CLAUDE.md (the contributor/agent guide) omits three of the ten `typsphinx/` modules, describes the `rootdir` route as the integration-test mechanism although 142 test files use subprocess fixture builds and only one uses `rootdir`, and says CI runs "py312–py313" without the three-OS matrix (evidence-codebase.md).
- `docs/S02-LOCAL-PARITY-EVIDENCE.md`, `docs/S03-ARTIFACT-GATE-EVIDENCE.md`, `docs/S04-PUBLISHED-SITE-EVIDENCE.md` are process evidence from the retired gsd-pi tooling (2026-10-03); S03/S04 are read by `tests/test_release_0_9_8_docs_gate.py:34-35,166,172`; S04 still says "awaiting merge" (DOCS-AUDIT #5), S03's Sphinx version is unverifiable (#4).
- Worktree venvs already run the full suite green on uv-managed CPython 3.14, but classifiers (`pyproject.toml:21-22`), black `target-version` (`pyproject.toml:111`), CI (`.github/workflows/ci.yml:18-23`) and tox (`env_list`) stop at 3.13.
- DOCS-AUDIT #1: README.md:26 "Automatic line numbering" — numbering is opt-in via `:linenos:`. #2: CHANGELOG.md:84-85 "Planned for Future Releases: Glossary generation" — glossary rendering exists. #3: examples/charged-ieee/README.md:163-164 says `typst_package` and `typst_template` "cannot be set together" — setting both warns and ignores `typst_package`.

## Users

The maintainer and contributors (human and agent) who read CLAUDE.md and the README; users reading CHANGELOG and the charged-ieee example; Python 3.14 users installing typsphinx.

## Success criteria

1. CLAUDE.md surface: CLAUDE.md's Architecture section has an entry for each of `template_registry.py`, `removed_config.py` and `pathfmt.py` stating its role; its Tests section states that most tests build a project under `tests/fixtures/` via a `sys.executable -m sphinx` subprocess and assert on the output (and that `tests/roots/` holds only `test-basic`); and its CI statements name the ubuntu/windows/macos × py312/py313/py314 test matrix (no remaining "py312–py313" matrix statement).
2. Evidence files retired: at the final HEAD `git ls-files 'docs/S0*'` prints nothing, and `grep -rnE 'S0[234]-[A-Z-]+EVIDENCE' tests/ typsphinx/ docs/source/ CLAUDE.md README.md` returns no match; `tests/test_release_0_9_8_docs_gate.py`'s remaining tests pass.
3. Python 3.14 declared and tested: `pyproject.toml` classifiers include `Programming Language :: Python :: 3.14`, black `target-version` includes `py314`, `.github/workflows/ci.yml`'s test matrix includes python-version `3.14` with tox env `py314` on all three OSes, and `tox.ini` `env_list` includes `py314`; `uv run tox -e py314` run in a verify sidecar passes.
4. README surface: README.md's codly feature list no longer says "Automatic line numbering" and states that line numbers appear for code blocks with `:linenos:`.
5. CHANGELOG surface: CHANGELOG.md's `### Planned for Future Releases` no longer lists "Glossary generation" (the heading itself is removed if it becomes empty); released history sections are not edited.
6. charged-ieee README surface: examples/charged-ieee/README.md states that setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`.
7. On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

## Edge coverage

| Edge | Criterion | Category | Disposition | Detail |
|------|-----------|----------|-------------|--------|
| E1 | SC1 | none | dismissed | static documentation text checked against named modules and files |
| E2 | SC2 | none | dismissed | fixed set of three named files; the absence check states its search space and command |
| E3 | SC3 | none | dismissed | fixed configuration entries plus one pass/fail tox run |
| E4 | SC4 | none | dismissed | static documentation text |
| E5 | SC5 | none | dismissed | static documentation text in one named section |
| E6 | SC6 | none | dismissed | static documentation text |
| E7 | SC7 | none | dismissed | whole-repository command results on one HEAD |

## Prohibitions

| Prohibition | Criterion | Must not | Disposition | Detail |
|-------------|-----------|----------|-------------|--------|
| N1 | all | none | dismissed | documentation, test-evidence and CI-declaration housekeeping; no person is affected beyond the stated text and configuration |

## Scope: in

- CLAUDE.md: Architecture (three modules), Tests (fixture-subprocess convention), CI matrix and tox `env_list` mentions (Q1 a).
- Delete `docs/S02-LOCAL-PARITY-EVIDENCE.md`, `docs/S03-ARTIFACT-GATE-EVIDENCE.md`, `docs/S04-PUBLISHED-SITE-EVIDENCE.md` and the S03/S04 checks in `tests/test_release_0_9_8_docs_gate.py` (Q2 a).
- Python 3.14: classifiers, black `target-version`, CI test matrix, tox `env_list` (Q3 a).
- DOCS-AUDIT #1–#3 fix-doc; #4–#5 resolved by the Q2 a deletion.

## Scope: out (vetoes)

- Version bump, CHANGELOG release section, tag or PyPI publish — the owner chose housekeeping (option 3), not release prep.
- Changing `requires-python`, ruff `target-version` or mypy `python_version` (they stay at the 3.12 floor).
- Product code changes under `typsphinx/`.
- Test-suite speed work (deferred; see STATE log for the discarded test-suite-dedup attempt).
- Editing released CHANGELOG history sections.

## Constraints

- Python >= 3.12; black/ruff line 88; mypy clean (CLAUDE.md).
- CLAUDE.md's toolchain-pin sync hazard: the tox-uv pin rationale lines must stay consistent with `tests/test_toolchain_config_gate.py`; do not change the pin.
- Tests must stay OS-neutral (CI ubuntu/windows/macos).
- CI results on the new py314 jobs are observed on the integration PR, not a success criterion (LESSONS 001).
- Integration by pull request (STATE `integration: pull-request`).

## Current state (brownfield only)

- **What exists**: typsphinx 0.9.8 + Unreleased M002–M004 changes at 660e3436; full suite 1883 passed, 1 skipped (uv CPython 3.14 sidecar); CI matrix py312/py313 × ubuntu/windows/macos.
- **Must not break**: the `@preview` single-source gate, the tox-uv toolchain pin gate, the remaining `test_release_0_9_8_docs_gate.py` checks.
- **Doc-vs-code rulings**: #1 README line numbering → fix-doc; #2 CHANGELOG planned glossary → fix-doc; #3 charged-ieee mutually-exclusive claim → fix-doc; #4 S03 Sphinx version and #5 S04 awaiting-merge → resolved by deleting the files (Q2 a).
- **Ground truth**: `.project/research/evidence-codebase.md`, `.project/research/DOCS-AUDIT.md`

## Risks

- black 26 may not accept `py314` in `target-version`, or a test may assert the exact tox `env_list` / CI matrix text.
- A test other than `test_release_0_9_8_docs_gate.py` might read the deleted files (static grep at 660e3436 found none).

## Open questions

- none

## Corrections

- C1 2026-11-03: "3"
- C2 2026-11-03: "Q1 a  Q2 a  Q3 a  4-1 fix-doc  4-2 fix-doc  4-3 fix-doc"

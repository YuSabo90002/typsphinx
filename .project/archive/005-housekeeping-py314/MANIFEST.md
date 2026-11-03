# Archive — 005-housekeeping-py314

Milestone: housekeeping-py314
Shipped: 2026-11-03
Final verdict: all criteria met; project verify passed
Waves: 1  Tasks: 2 done / 2 total  Review cycles used: 1
Carried forward: none

## Success criteria at ship

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| CLAUDE.md surface: CLAUDE.md's Architecture section has an entry for each of `template_registry.py`, `removed_config.py` and `pathfmt.py` stating its role; its Tests section states that most tests build a project under `tests/fixtures/` via a `sys.executable -m sphinx` subprocess and assert on the output (and that `tests/roots/` holds only `test-basic`); and its CI statements name the ubuntu/windows/macos × py312/py313/py314 test matrix (no remaining "py312–py313" matrix statement). | met | .project/review/wave-1.cycle1.md — SC1; evidence: Architecture bullets at CLAUDE.md:62/64/66 with roles; Tests paragraph CLAUDE.md:80 states the fixture-subprocess convention and `tests/roots/` holding only `test-basic`; CI bullet CLAUDE.md:88 names ubuntu/windows/macos × py312/py313/py314; no `py312–py313` string remains. E1 dismissed; N1 dismissed. |
| Evidence files retired: at the final HEAD `git ls-files 'docs/S0*'` prints nothing, and `grep -rnE 'S0[234]-[A-Z-]+EVIDENCE' tests/ typsphinx/ docs/source/ CLAUDE.md README.md` returns no match; `tests/test_release_0_9_8_docs_gate.py`'s remaining tests pass. | met | .project/review/wave-1.cycle1.md — SC2 |
| Python 3.14 declared and tested: `pyproject.toml` classifiers include `Programming Language :: Python :: 3.14`, black `target-version` includes `py314`, `.github/workflows/ci.yml`'s test matrix includes python-version `3.14` with tox env `py314` on all three OSes, and `tox.ini` `env_list` includes `py314`; `uv run tox -e py314` run in a verify sidecar passes. | met | .project/review/wave-1.cycle1.md — SC3 |
| README surface: README.md's codly feature list no longer says "Automatic line numbering" and states that line numbers appear for code blocks with `:linenos:`. | met | .project/review/wave-1.cycle1.md — SC4; evidence: README.md:26 "Line numbers for code blocks with `:linenos:`" under the codly bullet; old claim absent. E4 dismissed; N1 dismissed. |
| CHANGELOG surface: CHANGELOG.md's `### Planned for Future Releases` no longer lists "Glossary generation" (the heading itself is removed if it becomes empty); released history sections are not edited. | met | .project/review/wave-1.cycle1.md — SC5; evidence: CHANGELOG.md:84-87 heading kept with Index generation, Pre-commit hooks, Additional Typst Universe template integration; T001 diff removes only "- Glossary generation" above `## [0.9.8]` (line 89). The only remaining "Glossary generation" text is CHANGELOG.md:1517 inside a released section and was not edited. E5 dismissed; N1 dismissed. |
| charged-ieee README surface: examples/charged-ieee/README.md states that setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`. | met | .project/review/wave-1.cycle1.md — SC6; evidence: examples/charged-ieee/README.md:163-164 states the warn-and-ignore behaviour; matches builder.py:2445-2449 warning text; "cannot be set together" removed. E6 dismissed; N1 dismissed. |
| On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean. | met | .project/review/wave-1.cycle1.md — SC7 |

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
- tasks/T001-claude-md-evidence-files-and-doc-fixes.md
- tasks/T002-declare-and-test-python-3-14.md

## Notes

- none

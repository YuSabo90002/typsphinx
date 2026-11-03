# Archive — 003-windows-test-portability

Milestone: windows-test-portability
Shipped: 2026-11-03
Final verdict: all criteria met; project verify passed
Waves: 1  Tasks: 1 done / 1 total  Review cycles used: 1
Carried forward: none

## Success criteria at ship

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Drift-gate colour portability: with `FORCE_COLOR=1` set and `NO_COLOR` unset in the environment, `LC_ALL=C uv run pytest tests/test_template_dependency_drift_gate.py` passes (the sphinx-build subprocesses then colourise their output as on win32), and it also passes without `FORCE_COLOR`. | met | .project/review/wave-1.cycle1.md — SC1 |
| Path-separator portability: `tests/test_preview_version_sync.py::test_five_specs_appear_only_in_typst_deps_module` compares POSIX-normalised relative paths (no `str()` of a native `Path` in that comparison), and still fails if a second file under `typsphinx/` names a five-package spec. | met | .project/review/wave-1.cycle1.md — SC2 |
| Missing-file message portability: `tests/test_hand_compile_root_gate.py::TestNestedTargetWrapperNeedsTheOutdirAsRoot::test_compile_without_root_raises_naming_the_missing_template` accepts typst's error text whether the missing path is written with `/` or `\` separators (including the `\\?\C:\` prefix form), and still fails when the error names a different missing file; a test exercises both separator forms on Linux. | met | .project/review/wave-1.cycle1.md — SC3 |
| README.md surface: the Project Structure tree in README.md lists `typst_deps.py` under `typsphinx/` alongside the existing modules. | met | .project/review/wave-1.cycle1.md — SC4; evidence: Walkthrough performed at review HEAD: the fenced tree lists `typst_deps.py` under `typsphinx/` with the other modules. |
| On the final HEAD, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean. | met | .project/review/wave-1.cycle1.md — SC5 |

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
- tasks/T001-windows-portable-tests.md

## Notes

- none

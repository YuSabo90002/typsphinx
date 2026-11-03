# Intent — typsphinx

Lane: quick   <!-- one wave, at most two deliverable-sized tasks (Windows-portable test fixes; README tree), no RESEARCH or NEEDS-USER items, no cross-wave risk -->

Review panel: off

Finding skeptics: off

Surfaces: README.md Project Structure section

## Summary

M002 merged to `main` with eight tests that fail only on the windows-latest CI jobs (CI run 41589478348): one compares a native-separator path with a POSIX literal, one looks for a forward-slash fragment inside typst's native Windows error path, and six parse sphinx-build warning lines that carry Sphinx's ANSI colour reset on win32. The product behaves correctly in all eight; only the tests are not portable. This milestone makes those eight tests platform-independent, proves the Windows conditions on Linux, and fixes the one stale README claim (the Project Structure tree omits `typsphinx/typst_deps.py`).

## Problem

- `main` at f8e9b152 has red "Test Python 3.12/3.13 on windows-latest" jobs (8 failed, 1794 passed each). The jobs are not required checks, so the red state does not block merges but hides any real Windows regression.
- Causes (evidence-codebase.md): `str(p.relative_to(REPO_ROOT))` yields `typsphinx\typst_deps.py` on Windows; `MISSING_TEMPLATE_FRAGMENT = "_typsphinx/deps.typ"` never appears in typst's `\\?\C:\...\_typsphinx\deps.typ`; Sphinx 9.1.1 `terminal_supports_colour()` returns True on win32 unless `NO_COLOR` is set, so captured warning lines end in `\x1b[39;49;00m`.
- README.md's Project Structure tree is stale (DOCS-AUDIT queue #1).

## Users

The maintainer and contributors relying on the CI matrix; users reading README.md's project structure.

## Success criteria

1. Drift-gate colour portability: with `FORCE_COLOR=1` set and `NO_COLOR` unset in the environment, `LC_ALL=C uv run pytest tests/test_template_dependency_drift_gate.py` passes (the sphinx-build subprocesses then colourise their output as on win32), and it also passes without `FORCE_COLOR`.
2. Path-separator portability: `tests/test_preview_version_sync.py::test_five_specs_appear_only_in_typst_deps_module` compares POSIX-normalised relative paths (no `str()` of a native `Path` in that comparison), and still fails if a second file under `typsphinx/` names a five-package spec.
3. Missing-file message portability: `tests/test_hand_compile_root_gate.py::TestNestedTargetWrapperNeedsTheOutdirAsRoot::test_compile_without_root_raises_naming_the_missing_template` accepts typst's error text whether the missing path is written with `/` or `\` separators (including the `\\?\C:\` prefix form), and still fails when the error names a different missing file; a test exercises both separator forms on Linux.
4. README.md surface: the Project Structure tree in README.md lists `typst_deps.py` under `typsphinx/` alongside the existing modules.
5. On the final HEAD, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

## Edge coverage

| Edge | Criterion | Category | Disposition | Detail |
|------|-----------|----------|-------------|--------|
| E1 | SC1 | encoding | held-out | every ANSI SGR escape sequence (`\x1b[...m`) anywhere in a captured warning line is removed before comparison, not only the trailing reset; the comparison then matches the exact uncoloured message |
| E2 | SC2 | none | dismissed | the input is the fixed repository tree; no data shape beyond path separators, which SC2 states |
| E3 | SC3 | encoding | held-out | the check normalises `\` to `/` in the error text before matching `_typsphinx/deps.typ`; the forms `\\?\C:\x\_typsphinx\deps.typ`, `C:\x\_typsphinx\deps.typ`, and `/x/_typsphinx/deps.typ` all match, and `/x/_typsphinx/other.typ` does not |
| E4 | SC4 | none | dismissed | static text edit to one tree listing |
| E5 | SC5 | none | dismissed | read-only checks on one HEAD |

## Prohibitions

| Prohibition | Criterion | Must not | Disposition | Detail |
|-------------|-----------|----------|-------------|--------|
| N1 | SC1 | weaken or delete the drift assertions to make Windows pass | judgment | every drift-gate test still asserts the exact message text, count, and order it asserted before; only colour handling changes |
| N2 | SC2 | none | dismissed | test-only change; affects no user's output |
| N3 | SC3 | none | dismissed | test-only change; affects no user's output |
| N4 | SC4 | none | dismissed | documentation tree listing; no values, safety, or privacy dimension |
| N5 | SC5 | none | dismissed | read-only quality checks |

## Scope: in

- Make the six drift-gate tests colour-independent (SC1, E1).
- POSIX-normalise the path comparison in the version-sync test (SC2).
- Make the hand-compile missing-file assertion separator-agnostic, with a test for both forms (SC3, E3).
- Add `typst_deps.py` to README.md's Project Structure tree (SC4).
- Full suite and lint/type checks (SC5).

## Scope: out (vetoes)

- A project-wide colour-disabling helper or conftest convention — owner chose "1: a" (fix the 8 tests and README only).
- Releasing 0.9.9/0.10.0 and making `release.yml` gate on the CI matrix — owner chose "1: a".
- The intermittent macOS job failures on main — owner ruling "3: 範囲外".
- Any change to product code under `typsphinx/`.

## Constraints

- Python 3.12+; black/ruff/mypy clean as CI runs them.
- Windows behaviour is proven inside the milestone by the Linux-observable simulations in SC1–SC3 (owner ruling "2: a"). During build, `gh workflow run ci.yml --ref gsd-path/M003` is dispatched and the windows-latest jobs are expected green; that run and the PR checks are observed outside final review, not judged as criteria (LESSONS 001).
- Integration mode is `pull-request`: Path opens the PR, the owner merges.
- Test commands that assert warning text run under `LC_ALL=C`.

## Current state (brownfield only)

- **What exists**: typsphinx at f8e9b152 (M002 merged): single version source `typsphinx/typst_deps.py`, shared `_typsphinx/deps.typ`, `typst_dependencies`, template drift warning. Linux suite 1825 passed / 1 skipped (CPython 3.14 sidecar); windows-latest 8 failed / 1794 passed.
- **Must not break**: the asserted behaviour of the eight tests on Linux; all product code.
- **Doc-vs-code rulings**: DOCS-AUDIT queue #1 (README Project Structure omits `typst_deps.py`) → fix-doc — "4: fix-doc".
- **Ground truth**: `.project/research/evidence-codebase.md`, `.project/research/DOCS-AUDIT.md`

## Risks

- Sphinx's colour decision may depend on more than `FORCE_COLOR`/`NO_COLOR` (e.g. `TERM=dumb`); the SC1 simulation must actually produce coloured stderr on Linux, or it proves nothing.

## Open questions

- none

## Corrections


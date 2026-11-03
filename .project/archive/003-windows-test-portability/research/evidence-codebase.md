# Evidence — codebase

<!-- Written by the codebase mapper during /gsd-path-inspect. Read by define
     (brownfield mode), researchers (fifth standard dimension), the planner
     (conventions are binding), and reviewers. -->

Repo root: /home/yuta/Documents/typsphinx
Scanned: 2026-11-03 (Audited HEAD f8e9b152e13d05ff54b2c645cd950537cde0836f, verify sidecar at that revision)
Checks run: `LC_ALL=C uv run pytest -q -p no:cacheprovider -x -o addopts="--strict-markers"` in sidecar (Linux, CPython 3.14) → 1825 passed, 1 skipped (same 1826 total as each CI Windows job: 1794 passed + 8 failed + 24 skipped); `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` in sidecar → ok (sidecar venv is uv-managed CPython 3.14, not CI's 3.12/3.13); `gh run view 41589478348 --json conclusion,headSha,jobs` → failure, headSha a4863ca2 (PR #188 head, event pull_request), only the two windows-latest test jobs failed; `gh run view 41589478348 --log-failed` → `8 failed, 1794 passed, 24 skipped` on each Windows job; `gh run list --workflow CI --branch main -L 6` → CI for f8e9b152 (run 41590723612) still `in_progress` at scan time, earlier main runs 41496940277 and 41491198209 failed on macOS jobs with no failed step recorded.

## Map

- **Stack**: Python >=3.12 (classifiers 3.12/3.13), setuptools build backend; runtime deps `sphinx>=9.1,<10` (lock 9.1.1), `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16` (typst-py, in-process compiler). Dev extra: pytest, pytest-cov, tox + tox-uv, black 26, ruff, mypy, pypdf, pillow, sphinxcontrib-bibtex (dev-only by design). Docs extra: furo, sphinx-autodoc-typehints, sphinx-intl, myst-parser. Version 0.9.8 (`pyproject.toml`). Env management via `uv` + `uv.lock`; NixOS `flake.nix` devShell with FHS shims for the maintainer machine.
- **Entry points**: `typsphinx/__init__.py:setup()` registers `TypstBuilder`/`TypstPDFBuilder` and the `typst_*` config values (incl. `typst_dependencies`, `typst_document_templates`) and connects `config-inited` → `removed_config.check_config_at_init`. `pyproject.toml` `[project.entry-points."sphinx.builders"]` maps `typst` and `typstpdf` to `typsphinx` for auto-discovery. No CLI of its own; driven by `sphinx-build -b typst|typstpdf`.
- **Architecture**: doctree → `TypstTranslator` (`translator.py`, 8149 lines, 98 `visit_*`) → body string → `TypstWriter` (`writer.py`) writes per-docname content `.typ` (deps preamble, no template) and per-`typst_documents` wrapper files via `TemplateEngine` (`template_engine.py`). `TypstBuilder` (`builder.py`, 2858 lines) drives writes, image copying, template-bundle copying to `<outdir>/_template/<key>/`, writes `<outdir>/_typsphinx/deps.typ` (from `typst_deps.py`), and runs the template dependency drift warning; `TypstPDFBuilder` additionally compiles masters via `pdf.py` (typst-py) with outdir as compile root. Supporting modules: `template_registry.py` (registry-key validation incl. Windows reserved names), `pathfmt.py` (Typst path quoting), `removed_config.py`, `typst_deps.py` (leaf; single source of the five `@preview` specs).
- **Conventions**: builtin generics in annotations; black line length 88, ruff rule set E/F/W/I/N/UP/B/A/C4/T20 with N802 ignored for visitor names; mypy on `typsphinx/` with many error codes disabled for `typsphinx.*`. Errors in config shape raised from Builder methods (the `config-inited` hook is a documented exception). Tests: pytest with `--strict-markers`, `filterwarnings = error::DeprecationWarning / PendingDeprecationWarning`; a large family of `test_*_gate.py` files that run real `sys.executable -m sphinx` subprocess builds of tmp projects and assert on stdout/stderr or output files; `tests/roots/` + `sphinx.testing.fixtures`. Comments carry phase/requirement ids (e.g. `Phase 54 (CONF-19)`, `D-07`). Commit style under GSD Path: `T00N: <imperative summary>`, `build: ...`, `plan: ...`, `ship: M00N — <slug>`, PR merge commits into main; dependabot `chore(deps): bump ...`.
- **Maturity**: Production/Stable classifier; 188 `test_*.py` files; CI matrix ubuntu/windows/macos × 3.12/3.13 plus lint, type, coverage, build, two example integration jobs; docs, link-check, weekly drift, and tag-triggered PyPI release workflows. Release workflow (`release.yml`) validates on ubuntu only and does not depend on the CI test matrix. On PR #188's head the full suite passed on ubuntu and macOS and failed 8 tests on both Windows jobs (see findings).
- **Recent activity**: last ~30 commits are two GSD Path milestones: M001 `release-0-9-8` (graphviz proof, removal of `typst_debug`, CLAUDE.md corrections, 0.9.8 release prep; PR #187) and M002 `externalize-typst-deps` (T001–T005: `typst_deps.py`, `_typsphinx/deps.typ`, `typst_dependencies` config, drift warning, removing pins from repo templates, docs; PR #188 merged as f8e9b152), interleaved with dependabot bumps (tox-uv, sphinx stack, pypdf). Git history since 2026-10-01 is dominated by deletion of the old `.planning/` tree (GSD Core era). History spans 2025-10-13 → 2026-11-03, 4454 commits.

## Finding: M002 landed on main with 8 Windows-only test failures

- **Claim**: CI run 41589478348 (PR #188, head a4863ca2, the M002 ship commit whose tree is merged as f8e9b152) concluded `failure`; only "Test Python 3.12 on windows-latest" and "Test Python 3.13 on windows-latest" failed, each with `8 failed, 1794 passed, 24 skipped`. The same 8 tests fail on both: `tests/test_preview_version_sync.py::test_five_specs_appear_only_in_typst_deps_module`, `tests/test_hand_compile_root_gate.py::TestNestedTargetWrapperNeedsTheOutdirAsRoot::test_compile_without_root_raises_naming_the_missing_template`, and six in `tests/test_template_dependency_drift_gate.py` (`TestE10Comments::test_url_string_does_not_hide_a_real_pin`, `TestE8Ordering::test_one_warning_per_file_and_package_in_sorted_order`, `TestSC4DefaultMode::test_mismatch_warns_once_and_exits_zero`, `TestSC4DefaultMode::test_several_versions_in_one_file_sorted_numerically`, `TestSC4OverrideMode::test_compares_against_user_file`, `TestSC4OverrideMode::test_e9_package_missing_from_user_deps_is_not_compared`). All 8 tests were added or changed by M002 commits ff6d8521 (T001), 761ebf7b (T003), e89e4571 (T004).
- **Source**: `gh run view 41589478348 --json conclusion,headSha,jobs`; `gh run view 41589478348 --log-failed` (short test summary lines); `git log --oneline -- <test files>`.
- **Confidence**: high
- **Why it matters here**: main is red on Windows right after a "shipped" milestone; the M002 final review evidently did not see Windows CI (it is a PR check, outside a final-review-observable SC per LESSONS.md). The CI run for the merge commit f8e9b152 itself (41590723612) was still in progress at scan time, so its result is not yet recorded.

## Finding: test_five_specs_appear_only_in_typst_deps_module compares native-separator paths to a POSIX literal

- **Claim**: The test builds `str(p.relative_to(REPO_ROOT))` and asserts it equals `["typsphinx/typst_deps.py"]`; on Windows this yields `typsphinx\typst_deps.py`, so the assertion fails although the content check itself found exactly the one correct file. The product is not at fault.
- **Source**: `tests/test_preview_version_sync.py:62-71`; CI log: `AssertionError: ['typsphinx\\typst_deps.py']` / `At index 0 diff: 'typsphinx\\typst_deps.py' != 'typsphinx/typst_deps.py'` (`tests\test_preview_version_sync.py:71`).
- **Confidence**: high
- **Why it matters here**: a fix is test-only (e.g. `.as_posix()`), no production change needed.

## Finding: hand-compile root gate expects a POSIX fragment inside a native-path typst error

- **Claim**: `MISSING_TEMPLATE_FRAGMENT = "_typsphinx/deps.typ"` (changed from `"base.typ"` by T001 ff6d8521). typst-py on Windows reports the missing file as a native path: `file not found (searched at \\?\C:\Users\...\build\manuals\_typsphinx\deps.typ)`, so the substring `_typsphinx/deps.typ` is absent. Before M002 the fragment `base.typ` had no separator and was separator-agnostic. The compile does fail for the intended reason (missing deps.typ without root); only the assertion text is wrong on Windows.
- **Source**: `tests/test_hand_compile_root_gate.py:54`, `:214-222`; `git show afd0529f:tests/test_hand_compile_root_gate.py` line 54 (`"base.typ"`); CI log `tests\test_hand_compile_root_gate.py:222: AssertionError` with the quoted error text.
- **Confidence**: high
- **Why it matters here**: test-only fix (separator-agnostic match or normalising `\\` to `/`); the "unrelated failure cannot masquerade" intent of the assertion should be preserved.

## Finding: drift-gate stderr parsing captures Sphinx's ANSI reset code on Windows

- **Claim**: Each of the six drift-gate failures differs from the expected message only by a trailing `\x1b[39;49;00m`. `_drift_messages()` slices each stderr line from `"template dependency drift: "` to end of line without stripping colour codes. Sphinx 9.1.1's `sphinx/_cli/util/colour.py:terminal_supports_colour()` returns `True` unconditionally on `win32` unless `NO_COLOR`/`NO_COLOUR` is set (it does not check `isatty()` there), and colourised text ends with `\x1b[39;49;00m` (`colour.py:79`). The test's `_build()` sets only `LC_ALL=C` and does not pass `--no-color`/`NO_COLOR`; no test in `tests/` uses either. The leading colour code is cut off by the slice, which is why only the reset code shows. The warning text itself (POSIX relpath `'_template/typst/main.typ'`) is correct on Windows: `builder.py:2299-2306` normalises with `rel_path.replace(path.sep, "/")`.
- **Source**: `tests/test_template_dependency_drift_gate.py:65-96`; CI log lines e.g. `At index 0 diff: "template dependency drift: '_template/typst/main.typ' pins @preview/gentle-clues:1.2.0, but _typsphinx/deps.typ has @preview/gentle-clues:1.3.1\x1b[39;49;00m" != "..."` (`tests\test_template_dependency_drift_gate.py:124`, `:169`, `:202`, `:229`, `:263`, `:302`); `.venv/lib/python3.13/site-packages/sphinx/_cli/util/colour.py:22-42` in the main checkout venv (sphinx 9.1.1, matching `uv.lock`); `grep -rn "no-color\|NO_COLOR\|FORCE_COLOR\|x1b" tests/*.py tox.ini .github/workflows/*.yml` → no hits.
- **Confidence**: high (root cause of the colour emission read from Sphinx source; not reproduced on Windows locally)
- **Why it matters here**: fix is test-side (pass `--no-color` / `NO_COLOR=1`, or strip ANSI); other subprocess gates that use substring `in` checks are unaffected, which is why only exact-equality parsing broke. On ubuntu, the same function would also colour when `CI=true` reaches it; it evidently does not under tox (ubuntu jobs pass), so do not rely on `CI` env for reasoning.

## Finding: Windows failures are test-side; production Windows behaviour looked correct in this run

- **Claim**: In all 8 failures the product produced the right result (correct single file found; compile failed for the intended missing-deps reason; drift warning text correct with POSIX path). 1794 other tests passed on Windows, including Windows path quoting (`test_pathfmt.py`) and registry-key separator checks.
- **Source**: CI log for run 41589478348 (PASSED lines for `tests/test_pathfmt.py::...[C:\\Users\\a]`, `tests/test_template_registry.py::...[a\\b-path separator]`); analysis of the three findings above.
- **Confidence**: medium (inference from assertion diffs; no Windows machine available locally)
- **Why it matters here**: a fix milestone can be scoped to `tests/` only, unless the user wants production hardening (e.g. making the test helper policy "always `--no-color`" a convention).

## Finding: main CI has had intermittent macOS job failures with no failed step

- **Claim**: CI runs 41496940277 (79ed090e) and 41491198209 (255430ab) on main concluded `failure` only on macOS test jobs, and `gh run view --json jobs` shows no step with a non-success conclusion; `--log-failed` prints nothing.
- **Source**: `gh run list --workflow CI --branch main -L 6`; `gh run view <id> --json jobs --jq ...`.
- **Confidence**: low (cause not visible; likely runner/infra)
- **Why it matters here**: when judging "CI green on main" as a fix outcome, macOS noise can appear independently of the Windows fix.

## Finding: release workflow does not gate on the CI test matrix

- **Claim**: `release.yml` triggers on `v*` tags / dispatch and runs its own `validate` job on ubuntu-latest only; it has no dependency on `ci.yml` results, so a Windows-red main can still be tagged and published.
- **Source**: `.github/workflows/release.yml:1-30`, `:95` (`needs: validate`, `runs-on: ubuntu-latest`).
- **Confidence**: high
- **Why it matters here**: the Unreleased CHANGELOG section (M002 features) is pending release; if the next milestone includes a release, Windows must be checked manually or via CI before tagging.

## Finding: sidecar test environment differs from CI's interpreters

- **Claim**: A fresh `uv sync` in the verify sidecar produced a venv on uv-managed CPython 3.14 (`.venv/pyvenv.cfg` `version_info = 3.14`), while CI runs 3.12 and 3.13 and the main checkout venv is 3.13.
- **Source**: sidecar `.venv/pyvenv.cfg`; `/home/yuta/Documents/typsphinx/.venv/lib/python3.13`.
- **Confidence**: high
- **Why it matters here**: local pass counts from a worktree are not directly comparable with CI's; Windows-only failures cannot be reproduced on this Linux host at all, so Verify for a Windows fix needs either a CI run or a simulated check (e.g. monkeypatched separator / forced colour).

## Apparent intent

- The next milestone (M003, phase inspect) is likely to be a Windows CI repair for the M002 regressions — based on the owner's brief and the red Windows jobs on PR #188 (inference).
- The project is converging on `deps.typ` as a public template-author contract and preparing a release containing it — based on the Unreleased CHANGELOG section and CLAUDE.md "public contract" text (inference).

## Open questions for define

- Should the fix be test-only (`.as_posix()`, separator-agnostic fragment, `--no-color`/ANSI strip), or also add a project-wide convention/helper so subprocess sphinx-build tests always disable colour?
- Is "CI green on windows-latest" a success criterion or a Constraint? Per LESSONS.md (001), PR checks are not observable at final-review HEAD; how should Windows behaviour be proven inside the milestone (simulated tests on Linux vs. CI run)?
- Should a release (0.9.9 / 0.10.0 with the M002 Unreleased entries) be part of this milestone, and should `release.yml` start gating on the CI matrix?
- Are the intermittent macOS job failures on main in scope?

## Blocked areas

- Windows reproduction — no Windows host; the Windows failures are evidenced from CI logs and Sphinx source only.
- CI result for merge commit f8e9b152 (run 41590723612) — still in progress at scan time.
- `.project/archive/` and installed GSD Path / path skill bundles — excluded by brief.

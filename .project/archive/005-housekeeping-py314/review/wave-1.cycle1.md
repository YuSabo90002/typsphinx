# Review — wave 1, cycle 1

Reviewed HEAD: d2c7a1958ca3c2fe92724c64d1643e26b8e5448d
Review scope: final

Wave verdict: pass
Cycle: 1
Depth: full
Tasks reviewed: 2

Inspection mode: reconstructed product (verify sidecar gsd-path-verify/wave-1-cycle-1 at d2c7a195; task patches inspected as `git diff <landing>^ <landing>`).

## T001 — Update CLAUDE.md to match the code, retire the docs/S0x evidence files and their gate checks, and fix three stale doc claims: pass

Provenance: task `base` 5aee2fb977eec2376e4f7bfed01492c6cd6dd4f5; landing c03f3168fdae3232e013d668c184aa47827fedfd has parent 5aee2fb977eec2376e4f7bfed01492c6cd6dd4f5 (identity holds). Landing touches exactly the 8 declared paths plus the task file (`git diff 5aee2fb9 c03f3168 --name-status`: M CHANGELOG.md, CLAUDE.md, README.md, examples/charged-ieee/README.md, tests/test_release_0_9_8_docs_gate.py; D the three docs/S0* files; M task file). Task-file changes are only `status`/`agent`/`base` frontmatter plus appended Log entries. The Verify repair (removal of the index-reading `git ls-files` clause) was committed separately in 731021bd (`build: repair T001 Verify`), not in the task commit, and is logged as an orchestrator plan-defect repair; the re-applied patch sha256 d2cbc03c… is recorded as unchanged. Authoritative Verify: Log entry "orchestrator Verify (sidecar gsd-path-verify/task-t001-verify): pass, exit 0", evidence `.git/gsd-path/dispatch/gsd-path-M005/T001/manual-2026-11-03T113145+0000/verify.json` (exit_code 0, base 5aee2fb9, stdout "45 passed").

- ✅ T001/AC1 — CLAUDE.md:62 `template_registry.py`, :64 `removed_config.py`, :66 `pathfmt.py` bullets each state a role (checked against typsphinx/template_registry.py, removed_config.py, pathfmt.py); CLAUDE.md:80 states most tests are subprocess gates building a project under `tests/fixtures/` via `sys.executable -m sphinx` and asserting on output, and `tests/roots/` holds only `test-basic` (observed: `ls tests/roots` = `test-basic`); CLAUDE.md:28-29 and :88 name py312–py314 and the ubuntu/windows/macos × py312/py313/py314 test matrix; `grep -n 'py312–py313' CLAUDE.md` returns nothing.
- ✅ T001/AC2 — at d2c7a195 `git ls-files 'docs/S0*'` prints nothing; `grep -rnE 'S0[234]-[A-Z-]+EVIDENCE' tests/ typsphinx/ docs/source/ CLAUDE.md README.md` exit 1 (no match); recorded Verify ran tests/test_release_0_9_8_docs_gate.py within "45 passed", and my rerun of that file (in a 180-test targeted set) passed.
- ✅ T001/AC3 — README.md:26 now reads "Line numbers for code blocks with `:linenos:`"; "Automatic line numbering" absent; matches translator.py:2442/2513 (numbers disabled without `:linenos:`).
- ✅ T001/AC4 — CHANGELOG.md:84-87 keeps `### Planned for Future Releases` and its other three items; the only diff line is removal of "- Glossary generation" at old line 85, above `## [0.9.8]` (CHANGELOG.md:89); no line at or below `## [0.9.8]` changed.
- ✅ T001/AC5 — examples/charged-ieee/README.md:163-164 "Setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`, honouring `typst_template`"; matches the warning at typsphinx/builder.py:2445-2449.

Warnings (non-blocking):
- examples/charged-ieee/approach2/conf.py:21-27 comment still says setting `typst_package` as well "would switch typsphinx to the package-only route", which contradicts builder.py:2445-2449 and template_engine.py:208 (template wins). Not in T001 `files` and not covered by SC6; candidate for a later fix-doc.
- The Verify repair weakened the in-task proof of `git ls-files` absence; this review re-checked it at the review base (empty).

Contract violations (blocking):
- none

## T002 — Declare Python 3.14 in classifiers, black, the CI test matrix and tox, and prove tox -e py314 and the full suite pass: pass

Provenance: task `base` b20a0dc545d698e67ae2cd23aead7794e5476578; landing 5aee2fb977eec2376e4f7bfed01492c6cd6dd4f5 has parent 731021bd. 731021bd differs from b20a0dc5 only in `.project/STATE.md` and the T001 task file; `git diff --quiet b20a0dc5 731021bd -- pyproject.toml tox.ini .github` succeeds, so the patch applied to the recorded base yields the landing blobs for all declared files. Landing touches only pyproject.toml, .github/workflows/ci.yml, tox.ini and the task file (frontmatter `status`/`agent`/`base` plus appended Log). Authoritative Verify: Log entry "orchestrator Verify (isolate gsd-path-task/T002): pass, exit 0", evidence `.git/gsd-path/dispatch/gsd-path-M005/T002/manual-2026-11-03T113123+0000/verify.json` (exit_code 0, base b20a0dc5).

- ✅ T002/AC1 — pyproject.toml:23 classifier `Programming Language :: Python :: 3.14`; pyproject.toml:112 `target-version = ["py312", "py313", "py314"]`; ci.yml:18 `python-version: ['3.12', '3.13', '3.14']` with include row `python-version: '3.14'` → `tox-env: py314` crossed with `os: [ubuntu-latest, windows-latest, macos-latest]`; tox.ini:2 env_list includes `py314`; recorded Verify stdout shows `py314: OK` / `congratulations :)` (1856 passed, 28 skipped) and `uv lock --check` passed.
- ✅ T002/AC2 — recorded Verify stdout: "1883 passed, 1 skipped", "All checks passed!" (ruff), "Success: no issues found in 10 source files" (mypy), "398 files would be left unchanged." (black), exit 0.

Warnings (non-blocking):
- none

Contract violations (blocking):
- none

## Intent coverage

### SC1 — CLAUDE.md surface: CLAUDE.md's Architecture section has an entry for each of `template_registry.py`, `removed_config.py` and `pathfmt.py` stating its role; its Tests section states that most tests build a project under `tests/fixtures/` via a `sys.executable -m sphinx` subprocess and assert on the output (and that `tests/roots/` holds only `test-basic`); and its CI statements name the ubuntu/windows/macos × py312/py313/py314 test matrix (no remaining "py312–py313" matrix statement).: pass
- ✅ Architecture bullets at CLAUDE.md:62/64/66 with roles; Tests paragraph CLAUDE.md:80 states the fixture-subprocess convention and `tests/roots/` holding only `test-basic`; CI bullet CLAUDE.md:88 names ubuntu/windows/macos × py312/py313/py314; no `py312–py313` string remains. E1 dismissed; N1 dismissed.
- **Surface**: CLAUDE.md
- **Check**: Walkthrough 1-3: opened CLAUDE.md § Architecture and found the three module entries; opened § Tests; `grep -n 'py312–py313' CLAUDE.md` and read the CI bullet.
- **Observed**: success state — CLAUDE.md:62-66 three module bullets with roles; CLAUDE.md:80 subprocess-gate convention under `tests/fixtures/` and `tests/roots/` holds only `test-basic` (confirmed `ls tests/roots` → `test-basic`); grep empty; CLAUDE.md:88 "ubuntu/windows/macos × py312/py313/py314 matrix, plus lint, type and cov jobs"; CLAUDE.md:28-29 tox comment lists py312, py313, py314.

### SC2 — Evidence files retired: at the final HEAD `git ls-files 'docs/S0*'` prints nothing, and `grep -rnE 'S0[234]-[A-Z-]+EVIDENCE' tests/ typsphinx/ docs/source/ CLAUDE.md README.md` returns no match; `tests/test_release_0_9_8_docs_gate.py`'s remaining tests pass.: pass
- ✅ At d2c7a195: `git ls-files 'docs/S0*'` → empty; the grep exits 1 with no output; `LC_ALL=C uv run pytest tests/test_release_0_9_8_docs_gate.py` (within a 180-test targeted run) passed, consistent with T001's recorded Verify "45 passed". E2 dismissed; N1 dismissed.

### SC3 — Python 3.14 declared and tested: `pyproject.toml` classifiers include `Programming Language :: Python :: 3.14`, black `target-version` includes `py314`, `.github/workflows/ci.yml`'s test matrix includes python-version `3.14` with tox env `py314` on all three OSes, and `tox.ini` `env_list` includes `py314`; `uv run tox -e py314` run in a verify sidecar passes.: pass
- ✅ pyproject.toml:23 and :112, ci.yml:16-25, tox.ini:2 as in T002/AC1; T002's recorded isolated Verify ran `LC_ALL=C uv run tox -e py314` → `py314: OK`, `congratulations :)`, exit 0. T001 does not touch pyproject.toml, ci.yml or tox.ini, so these declarations are unchanged at the final HEAD. E3 dismissed; N1 dismissed.

### SC4 — README surface: README.md's codly feature list no longer says "Automatic line numbering" and states that line numbers appear for code blocks with `:linenos:`.: pass
- ✅ README.md:26 "Line numbers for code blocks with `:linenos:`" under the codly bullet; old claim absent. E4 dismissed; N1 dismissed.
- **Surface**: README.md
- **Check**: Walkthrough 1-2: opened README.md at the "Code blocks with syntax highlighting" bullet (README.md:25) and read its sub-bullets; `grep -n 'Automatic line' README.md`.
- **Observed**: success state — sub-bullet README.md:26 reads "Line numbers for code blocks with `:linenos:`"; grep for "Automatic line" returns nothing.

### SC5 — CHANGELOG surface: CHANGELOG.md's `### Planned for Future Releases` no longer lists "Glossary generation" (the heading itself is removed if it becomes empty); released history sections are not edited.: pass
- ✅ CHANGELOG.md:84-87 heading kept with Index generation, Pre-commit hooks, Additional Typst Universe template integration; T001 diff removes only "- Glossary generation" above `## [0.9.8]` (line 89). The only remaining "Glossary generation" text is CHANGELOG.md:1517 inside a released section and was not edited. E5 dismissed; N1 dismissed.
- **Surface**: CHANGELOG.md
- **Check**: Walkthrough 1-2: opened `## [Unreleased]` → `### Planned for Future Releases` (`grep -n -A4 'Planned for Future' CHANGELOG.md`); `git diff c03f3168^ c03f3168 -- CHANGELOG.md`.
- **Observed**: success state — list has three items, no "Glossary generation"; the diff is one deleted line in hunk `@@ -82,7 +82,6 @@`, all above `## [0.9.8]`.

### SC6 — charged-ieee README surface: examples/charged-ieee/README.md states that setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`.: pass
- ✅ examples/charged-ieee/README.md:163-164 states the warn-and-ignore behaviour; matches builder.py:2445-2449 warning text; "cannot be set together" removed. E6 dismissed; N1 dismissed.
- **Surface**: examples/charged-ieee/README.md
- **Check**: Walkthrough 1-2: opened the README limitations list (examples/charged-ieee/README.md:155-164) and read the `typst_package` / `typst_template` bullet.
- **Observed**: success state — "Setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`, honouring `typst_template`"; no "cannot be" text remains.

### SC7 — On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.: pass
- ✅ T002's recorded isolated Verify (base b20a0dc5 + T002 patch) with `--extra dev --extra docs`: "1883 passed, 1 skipped", black/ruff/mypy clean, exit 0. T001 landed afterwards and changes only Markdown files (CLAUDE.md, README.md, CHANGELOG.md, examples/charged-ieee/README.md), deletes three docs/S0* Markdown files outside docs/source, and deletes two test functions plus two constants in tests/test_release_0_9_8_docs_gate.py; it touches no product code or config. Its effect on SC7 was checked at the final HEAD d2c7a195 in this sidecar (`uv sync --extra dev --extra docs`, LC_ALL=C): every test module that reads CLAUDE.md, README.md, CHANGELOG or the charged-ieee README (19 files found by grep) plus tests/test_preview_version_sync.py → "180 passed"; `uv run black --check .` → "398 files would be left unchanged."; `uv run ruff check .` → "All checks passed!"; `uv run mypy typsphinx/` → "Success: no issues found in 10 source files". The expected final-HEAD suite count is 1881 passed, 1 skipped (1883 minus the two removed tests). PLAN.md's project Verify is still run once at ship. E7 dismissed; N1 dismissed.

## Summary for orchestrator

- blocked findings: none
- repeat offenders: none
- warnings worth a human eye: examples/charged-ieee/approach2/conf.py:21-27 has a stale comment claiming that setting `typst_package` too switches to the package-only route (code: template wins, package ignored). It is outside the M005 scope and is a candidate fix-doc for a later milestone.

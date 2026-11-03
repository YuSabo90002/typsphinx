# Final Review — reused full wave

Reviewed HEAD: ffded1cb5eb3c6de23785b5a21ae084a199bd86a
Overall verdict: pass
Source review: .project/review/wave-1.cycle1.md
Source commit: d2c7a1958ca3c2fe92724c64d1643e26b8e5448d

## Success criteria

### SC1 — CLAUDE.md surface: CLAUDE.md's Architecture section has an entry for each of `template_registry.py`, `removed_config.py` and `pathfmt.py` stating its role; its Tests section states that most tests build a project under `tests/fixtures/` via a `sys.executable -m sphinx` subprocess and assert on the output (and that `tests/roots/` holds only `test-basic`); and its CI statements name the ubuntu/windows/macos × py312/py313/py314 test matrix (no remaining "py312–py313" matrix statement).

- **Verdict**: met
- **Check**: Walkthrough 1-3: opened CLAUDE.md § Architecture and found the three module entries; opened § Tests; `grep -n 'py312–py313' CLAUDE.md` and read the CI bullet.
- **Observed**: success state — CLAUDE.md:62-66 three module bullets with roles; CLAUDE.md:80 subprocess-gate convention under `tests/fixtures/` and `tests/roots/` holds only `test-basic` (confirmed `ls tests/roots` → `test-basic`); grep empty; CLAUDE.md:88 "ubuntu/windows/macos × py312/py313/py314 matrix, plus lint, type and cov jobs"; CLAUDE.md:28-29 tox comment lists py312, py313, py314.
- **Reference**: .project/review/wave-1.cycle1.md — SC1; evidence: Architecture bullets at CLAUDE.md:62/64/66 with roles; Tests paragraph CLAUDE.md:80 states the fixture-subprocess convention and `tests/roots/` holding only `test-basic`; CI bullet CLAUDE.md:88 names ubuntu/windows/macos × py312/py313/py314; no `py312–py313` string remains. E1 dismissed; N1 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: CLAUDE.md

### SC2 — Evidence files retired: at the final HEAD `git ls-files 'docs/S0*'` prints nothing, and `grep -rnE 'S0[234]-[A-Z-]+EVIDENCE' tests/ typsphinx/ docs/source/ CLAUDE.md README.md` returns no match; `tests/test_release_0_9_8_docs_gate.py`'s remaining tests pass.

- **Verdict**: met
- **Check**: none
- **Observed**: At d2c7a195: `git ls-files 'docs/S0*'` → empty; the grep exits 1 with no output; `LC_ALL=C uv run pytest tests/test_release_0_9_8_docs_gate.py` (within a 180-test targeted run) passed, consistent with T001's recorded Verify "45 passed". E2 dismissed; N1 dismissed.
- **Reference**: .project/review/wave-1.cycle1.md — SC2
- **Finding**: none
- **Fix direction**: none

### SC3 — Python 3.14 declared and tested: `pyproject.toml` classifiers include `Programming Language :: Python :: 3.14`, black `target-version` includes `py314`, `.github/workflows/ci.yml`'s test matrix includes python-version `3.14` with tox env `py314` on all three OSes, and `tox.ini` `env_list` includes `py314`; `uv run tox -e py314` run in a verify sidecar passes.

- **Verdict**: met
- **Check**: none
- **Observed**: pyproject.toml:23 and :112, ci.yml:16-25, tox.ini:2 as in T002/AC1; T002's recorded isolated Verify ran `LC_ALL=C uv run tox -e py314` → `py314: OK`, `congratulations :)`, exit 0. T001 does not touch pyproject.toml, ci.yml or tox.ini, so these declarations are unchanged at the final HEAD. E3 dismissed; N1 dismissed.
- **Reference**: .project/review/wave-1.cycle1.md — SC3
- **Finding**: none
- **Fix direction**: none

### SC4 — README surface: README.md's codly feature list no longer says "Automatic line numbering" and states that line numbers appear for code blocks with `:linenos:`.

- **Verdict**: met
- **Check**: Walkthrough 1-2: opened README.md at the "Code blocks with syntax highlighting" bullet (README.md:25) and read its sub-bullets; `grep -n 'Automatic line' README.md`.
- **Observed**: success state — sub-bullet README.md:26 reads "Line numbers for code blocks with `:linenos:`"; grep for "Automatic line" returns nothing.
- **Reference**: .project/review/wave-1.cycle1.md — SC4; evidence: README.md:26 "Line numbers for code blocks with `:linenos:`" under the codly bullet; old claim absent. E4 dismissed; N1 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: README.md

### SC5 — CHANGELOG surface: CHANGELOG.md's `### Planned for Future Releases` no longer lists "Glossary generation" (the heading itself is removed if it becomes empty); released history sections are not edited.

- **Verdict**: met
- **Check**: Walkthrough 1-2: opened `## [Unreleased]` → `### Planned for Future Releases` (`grep -n -A4 'Planned for Future' CHANGELOG.md`); `git diff c03f3168^ c03f3168 -- CHANGELOG.md`.
- **Observed**: success state — list has three items, no "Glossary generation"; the diff is one deleted line in hunk `@@ -82,7 +82,6 @@`, all above `## [0.9.8]`.
- **Reference**: .project/review/wave-1.cycle1.md — SC5; evidence: CHANGELOG.md:84-87 heading kept with Index generation, Pre-commit hooks, Additional Typst Universe template integration; T001 diff removes only "- Glossary generation" above `## [0.9.8]` (line 89). The only remaining "Glossary generation" text is CHANGELOG.md:1517 inside a released section and was not edited. E5 dismissed; N1 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: CHANGELOG.md

### SC6 — charged-ieee README surface: examples/charged-ieee/README.md states that setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`.

- **Verdict**: met
- **Check**: Walkthrough 1-2: opened the README limitations list (examples/charged-ieee/README.md:155-164) and read the `typst_package` / `typst_template` bullet.
- **Observed**: success state — "Setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`, honouring `typst_template`"; no "cannot be" text remains.
- **Reference**: .project/review/wave-1.cycle1.md — SC6; evidence: examples/charged-ieee/README.md:163-164 states the warn-and-ignore behaviour; matches builder.py:2445-2449 warning text; "cannot be set together" removed. E6 dismissed; N1 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: examples/charged-ieee/README.md

### SC7 — On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

- **Verdict**: met
- **Check**: none
- **Observed**: T002's recorded isolated Verify (base b20a0dc5 + T002 patch) with `--extra dev --extra docs`: "1883 passed, 1 skipped", black/ruff/mypy clean, exit 0. T001 landed afterwards and changes only Markdown files (CLAUDE.md, README.md, CHANGELOG.md, examples/charged-ieee/README.md), deletes three docs/S0* Markdown files outside docs/source, and deletes two test functions plus two constants in tests/test_release_0_9_8_docs_gate.py; it touches no product code or config. Its effect on SC7 was checked at the final HEAD d2c7a195 in this sidecar (`uv sync --extra dev --extra docs`, LC_ALL=C): every test module that reads CLAUDE.md, README.md, CHANGELOG or the charged-ieee README (19 files found by grep) plus tests/test_preview_version_sync.py → "180 passed"; `uv run black --check .` → "398 files would be left unchanged."; `uv run ruff check .` → "All checks passed!"; `uv run mypy typsphinx/` → "Success: no issues found in 10 source files". The expected final-HEAD suite count is 1881 passed, 1 skipped (1883 minus the two removed tests). PLAN.md's project Verify is still run once at ship. E7 dismissed; N1 dismissed.
- **Reference**: .project/review/wave-1.cycle1.md — SC7
- **Finding**: none
- **Fix direction**: none

---
phase: "74"
slug: "the-doctest-block-handler-its-real-compile-gate-and-the-docs"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-20"
---

# Phase 74 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (`dev` extra), config in `pyproject.toml` `[tool.pytest.ini_options]` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/test_doctest_block_render_gate.py -x` (new module; exact name fixed by the plans) and `uv run pytest tests/test_translator.py -x` |
| **Full suite command** | `uv run pytest` (plus `LC_ALL=C uv run pytest` before the CI dispatch) |
| **Estimated runtime** | ~130 seconds full suite (main `.venv`, 1547 passed / 1 skipped measured 2026-09-19; worktree counts differ by interpreter and missing `docs` extra — compare only after recording `pyvenv.cfg`) |

---

## Sampling Rate

- **After every task commit:** Run the quick run command for the file being worked on
- **After every plan wave:** Run `uv run pytest`, `uv run ruff check .`, `uv run black --check .`, `uv run mypy typsphinx/`
- **Before `/gsd-verify-work`:** Full suite must be green, plus base/tip clean-build evidence recorded
- **Max feedback latency:** 150 seconds

---

## Per-Task Verification Map

Filled by the planner from the final PLAN.md task IDs (2026-09-20). Seven plans, five waves:
74-01 and 74-02 in wave 1; 74-03 in wave 2; 74-04 in wave 3; 74-05 and 74-06 in wave 4; 74-07 in
wave 5. Every task's full command is the `<automated>` block of its plan; the column below names its
load-bearing check.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 74-01-T1 | 74-01 | 1 | TRN-01 / SC1 base (positive control) | T-74-01 | a localised or incremental build cannot fake a count | build | clean `LANG=C LC_ALL=C uv run python -m sphinx -b typst docs/source` at `PHASE_BASE_SHA`; English `build succeeded` N; doctest_block unknown-node count at least 1; collapsed `api/index.typ` run transcribed | N/A (evidence file) | ⬜ pending |
| 74-01-T2 | 74-01 | 1 | QUA-14 / SC3 census (D-07) | T-74-02 | census never narrowed | build + grep | raw and attributed counts recounted from the log; attributed plus unattributed equals raw; `BASE_UNATTRIBUTED_UNMATCHED = 0`; every attributed docstring in `FIX_LIST` | N/A (evidence file) | ⬜ pending |
| 74-01-T3 | 74-01 | 1 | SC4 head reads | T-74-03 | read-only remote queries | gh | `gh api …/required_status_checks` strict and sorted contexts equal their keys; reference run job-name set equals `REFERENCE_JOB_NAMES` | N/A (evidence file) | ⬜ pending |
| 74-02-T1 | 74-02 | 1 | TRN-01 / TRN-02 RED, context (a) | T-74-05, T-74-06 | RED observed on a tree without the handler | render-gate | `uv run pytest tests/test_doctest_block_render_gate.py -q -rf` exits non-zero with the four context (a) tests FAILED; typsphinx/ equals `6cc44f22` at `TRACER_RED_SHA` | ❌ W0 | ⬜ pending |
| 74-02-T2 | 74-02 | 1 | TRN-02 RED, context (b) shapes (b1)/(b2) (D-06) | T-74-05, T-74-07 | verbatim RED transcript | render-gate | 11 collected; the eight required tests FAILED; direct `-b typstpdf` log carries `expected semicolon or line break` and names `context_a_paragraph`; `RED_VERDICT = MET` | ❌ W0 | ⬜ pending |
| 74-03-T1 | 74-03 | 2 | TRN-01 / TRN-02 GREEN (D-01..D-04) | T-74-09, T-74-10, T-74-11 | literal_block path untouched; no doctree mutation | render-gate + diff | `uv run pytest tests/test_doctest_block_render_gate.py -q` (11 passed, module unchanged since `RED_TREE_SHA`); exactly three removed translator lines; hunks inside the handler region; `uv run mypy typsphinx/` | ✅ after 74-02 | ⬜ pending |
| 74-03-T2 | 74-03 | 2 | TRN-01 (D-01, D-02, D-03) | T-74-09 | honour path and bare fence pinned | unit | `uv run pytest tests/test_translator.py -q -k 'doctest_block or literal_block'`; four new functions; zero deletions in tests/test_translator.py | ✅ | ⬜ pending |
| 74-03-T3 | 74-03 | 2 | TRN-02 GREEN record (D-06), SC1 tag | T-74-10 | GREEN on the RED gate | render-gate + lint | saved GREEN logs: 0 unknown-node warnings, three `%PDF` masters; separator-mechanism and `FENCE_TAG` keys; `uv run ruff check .`, `black --check .`, `mypy typsphinx/` | ✅ | ⬜ pending |
| 74-04-T1 | 74-04 | 3 | QUA-14 fix, visit_toctree | T-74-12, T-74-14 | no suppression; blank lines only | build + diff | clean C-locale rebuild with 0 attributed lines (positive control: 74-BASE-EVIDENCE.md); translator.py adds only empty lines inside visit_toctree's docstring | N/A (evidence file) | ⬜ pending |
| 74-04-T2 | 74-04 | 3 | QUA-14 fix, quote_path (D-07) | T-74-12, T-74-13 | raw and attributed both 0 | build + diff | clean C-locale rebuild with 0 raw phrases, N at most `BASE_WARNING_COUNT`; typsphinx/ diff only empty lines in the two docstrings; lint trio | N/A (evidence file) | ⬜ pending |
| 74-05-T1 | 74-05 | 4 | TRN-01 / SC1 tip, QUA-14 / SC3 tip | T-74-17 | tip zero against a positive control | build | tip `-b typst`: 0 doctest_block warnings, 0 raw phrases; 3 prompt lines under `codly(number-format: none)` and a python fence; examples in source order | N/A (evidence file) | ⬜ pending |
| 74-05-T2 | 74-05 | 4 | SC3 not risen; D-05 | T-74-15, T-74-16 | base window restored; every hunk classified | build + diff | same-venv base rebuild reproduces 74-01's counts; `RESTORE_CLEAN = yes`; `diff -rq --exclude=.doctrees` finds only `api/index.typ`; hunk table equals `diff -u` hunk count; no removed fence line | N/A (evidence file) | ⬜ pending |
| 74-05-T3 | 74-05 | 4 | SC3 meaning, verdicts | T-74-13 | meaning unchanged | build + token compare | HTML and `.typ` visit_toctree token files identical base/tip; no `quote_path` API entry; `SC1_VERDICT`, `SC3_VERDICT`, `D05_VERDICT` MET (plus human-check) | N/A (evidence file) | ⬜ pending |
| 74-06-T1 | 74-06 | 4 | SC4 local gates | T-74-19, T-74-20 | locale-dependent failures surfaced locally | gates | `uv run ruff check .`, `black --check .`, `mypy typsphinx/`, `LC_ALL=C uv run pytest -q -rs` green with no changelog-gate skip; preview sync test; four `@preview` packages | ✅ | ⬜ pending |
| 74-06-T2 | 74-06 | 4 | SC4 scope fence (constraint 7) | T-74-18 | fence with pathspec and widened-diff controls | git | typsphinx/ diff exactly pathfmt.py and translator.py, hunks region-scoped; `.github`, `flake.nix`, `pyproject.toml`, `uv.lock`, `__init__.py` untouched; tests/ additions only; COVERAGE.md exact line | N/A (evidence file) | ⬜ pending |
| 74-07-T1 | 74-07 | 5 | SC4 first push | T-74-21, T-74-22, T-74-25 | no decoy, tag, force or release trigger | git / gh | census before the push; `git push --no-follow-tags -u origin gsd/v0.9.6-doctest-block-rendering-and-release`; one `gh workflow run CI --ref …` whose headSha is `PUSHED_SHA` | N/A (evidence file) | ⬜ pending |
| 74-07-T2 | 74-07 | 5 | SC4 CI | T-74-23, T-74-24 | the run is bound to `PUSHED_SHA` | CI | run completed and success; every job success; four windows/macos lanes named; job set equals `REFERENCE_JOB_NAMES`; required checks unchanged | N/A (evidence file) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_doctest_block_render_gate.py` — GATE-01 gate for TRN-01/TRN-02 (context (a), and context (b) shapes (b1) definition-list and (b2) bullet-list per D-06), recorded RED before the handler lands. Created by 74-02, wave 1.
- [ ] `tests/fixtures/doctest_block_render_gate/` — `conf.py`, `index.rst`, `context_a_paragraph.rst`, `context_b_nonfirst_positions.rst`; three masters. Created by 74-02, wave 1.
- [ ] Docs-build venv: every worktree that builds `docs/source` (74-01, 74-04, 74-05, 74-06) is provisioned with `--extra dev --extra docs --python 3.13.13`, because the `dev` extra alone cannot import `myst_parser` / `sphinx_autodoc_typehints`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rendered API-reference meaning unchanged after docstring repair | QUA-14 | Semantic reading of HTML and `.typ` output | Read the affected docstrings' regions in base and tip `-b html` / `-b typst` output and record that only markup changed |
| 3-OS CI run green | SC4 | External GitHub Actions run | `gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release`, then transcribe every job conclusion |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 150s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

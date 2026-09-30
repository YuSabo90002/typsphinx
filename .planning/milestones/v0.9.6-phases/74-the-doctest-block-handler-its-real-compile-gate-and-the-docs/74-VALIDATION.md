---
phase: "74"
slug: "the-doctest-block-handler-its-real-compile-gate-and-the-docs"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
validated: "2026-09-20"
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
| **Quick run command** | `uv run pytest tests/test_doctest_block_render_gate.py -x` (new module; exact name fixed by the plans), `uv run pytest tests/test_translator.py -x`, and `uv run pytest tests/test_docstring_rest_census_guard.py -q` (QUA-14 guard, added by validate-phase) |
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
| 74-01-T1 | 74-01 | 1 | TRN-01 / SC1 base (positive control) | T-74-01 | a localised or incremental build cannot fake a count | build | clean `LANG=C LC_ALL=C uv run python -m sphinx -b typst docs/source` at `PHASE_BASE_SHA`; English `build succeeded` N; doctest_block unknown-node count at least 1; collapsed `api/index.typ` run transcribed | N/A (evidence file) | ✅ green |
| 74-01-T2 | 74-01 | 1 | QUA-14 / SC3 census (D-07) | T-74-02 | census never narrowed | build + grep | raw and attributed counts recounted from the log; attributed plus unattributed equals raw; `BASE_UNATTRIBUTED_UNMATCHED = 0`; every attributed docstring in `FIX_LIST` | N/A (evidence file) | ✅ green |
| 74-01-T3 | 74-01 | 1 | SC4 head reads | T-74-03 | read-only remote queries | gh | `gh api …/required_status_checks` strict and sorted contexts equal their keys; reference run job-name set equals `REFERENCE_JOB_NAMES` | N/A (evidence file) | ✅ green |
| 74-02-T1 | 74-02 | 1 | TRN-01 / TRN-02 RED, context (a) | T-74-05, T-74-06 | RED observed on a tree without the handler | render-gate | `uv run pytest tests/test_doctest_block_render_gate.py -q -rf` exits non-zero with the four context (a) tests FAILED; typsphinx/ equals `6cc44f22` at `TRACER_RED_SHA` | ❌ W0 | ✅ green |
| 74-02-T2 | 74-02 | 1 | TRN-02 RED, context (b) shapes (b1)/(b2) (D-06) | T-74-05, T-74-07 | verbatim RED transcript | render-gate | 11 collected; the eight required tests FAILED; direct `-b typstpdf` log carries `expected semicolon or line break` and names `context_a_paragraph`; `RED_VERDICT = MET` | ❌ W0 | ✅ green |
| 74-03-T1 | 74-03 | 2 | TRN-01 / TRN-02 GREEN (D-01..D-04) | T-74-09, T-74-10, T-74-11 | literal_block path untouched; no doctree mutation | render-gate + diff | `uv run pytest tests/test_doctest_block_render_gate.py -q` (11 passed, module unchanged since `RED_TREE_SHA`); exactly three removed translator lines; hunks inside the handler region; `uv run mypy typsphinx/` | ✅ after 74-02 | ✅ green |
| 74-03-T2 | 74-03 | 2 | TRN-01 (D-01, D-02, D-03) | T-74-09 | honour path and bare fence pinned | unit | `uv run pytest tests/test_translator.py -q -k 'doctest_block or literal_block'`; four new functions; zero deletions in tests/test_translator.py | ✅ | ✅ green |
| 74-03-T3 | 74-03 | 2 | TRN-02 GREEN record (D-06), SC1 tag | T-74-10 | GREEN on the RED gate | render-gate + lint | saved GREEN logs: 0 unknown-node warnings, three `%PDF` masters; separator-mechanism and `FENCE_TAG` keys; `uv run ruff check .`, `black --check .`, `mypy typsphinx/` | ✅ | ✅ green |
| 74-04-T1 | 74-04 | 3 | QUA-14 fix, visit_toctree | T-74-12, T-74-14 | no suppression; blank lines only | build + diff | clean C-locale rebuild with 0 attributed lines (positive control: 74-BASE-EVIDENCE.md); translator.py adds only empty lines inside visit_toctree's docstring | N/A (evidence file) | ✅ green |
| 74-04-T2 | 74-04 | 3 | QUA-14 fix, quote_path (D-07) | T-74-12, T-74-13 | raw and attributed both 0 | build + diff | clean C-locale rebuild with 0 raw phrases, N at most `BASE_WARNING_COUNT`; typsphinx/ diff only empty lines in the two docstrings; lint trio | N/A (evidence file) | ✅ green |
| 74-05-T1 | 74-05 | 4 | TRN-01 / SC1 tip, QUA-14 / SC3 tip | T-74-17 | tip zero against a positive control | build | tip `-b typst`: 0 doctest_block warnings, 0 raw phrases; 3 prompt lines under `codly(number-format: none)` and a python fence; examples in source order | N/A (evidence file) | ✅ green |
| 74-05-T2 | 74-05 | 4 | SC3 not risen; D-05 | T-74-15, T-74-16 | base window restored; every hunk classified | build + diff | same-venv base rebuild reproduces 74-01's counts; `RESTORE_CLEAN = yes`; `diff -rq --exclude=.doctrees` finds only `api/index.typ`; hunk table equals `diff -u` hunk count; no removed fence line | N/A (evidence file) | ✅ green |
| 74-05-T3 | 74-05 | 4 | SC3 meaning, verdicts | T-74-13 | meaning unchanged | build + token compare | HTML and `.typ` visit_toctree token files identical base/tip; no `quote_path` API entry; `SC1_VERDICT`, `SC3_VERDICT`, `D05_VERDICT` MET (plus human-check) | N/A (evidence file) | ✅ green |
| 74-06-T1 | 74-06 | 4 | SC4 local gates | T-74-19, T-74-20 | locale-dependent failures surfaced locally | gates | `uv run ruff check .`, `black --check .`, `mypy typsphinx/`, `LC_ALL=C uv run pytest -q -rs` green with no changelog-gate skip; preview sync test; four `@preview` packages | ✅ | ✅ green |
| 74-06-T2 | 74-06 | 4 | SC4 scope fence (constraint 7) | T-74-18 | fence with pathspec and widened-diff controls | git | typsphinx/ diff exactly pathfmt.py and translator.py, hunks region-scoped; `.github`, `flake.nix`, `pyproject.toml`, `uv.lock`, `__init__.py` untouched; tests/ additions only; COVERAGE.md exact line | N/A (evidence file) | ✅ green |
| 74-07-T1 | 74-07 | 5 | SC4 first push | T-74-21, T-74-22, T-74-25 | no decoy, tag, force or release trigger | git / gh | census before the push; `git push --no-follow-tags -u origin gsd/v0.9.6-doctest-block-rendering-and-release`; one `gh workflow run CI --ref …` whose headSha is `PUSHED_SHA` | N/A (evidence file) | ✅ green |
| 74-07-T2 | 74-07 | 5 | SC4 CI | T-74-23, T-74-24 | the run is bound to `PUSHED_SHA` | CI | run completed and success; every job success; four windows/macos lanes named; job set equals `REFERENCE_JOB_NAMES`; required checks unchanged | N/A (evidence file) | ✅ green |
| QUA-14-G1 | (validate-phase) | post | QUA-14 regression guard | T-74-12, T-74-13, T-74-14 | the cleared message class cannot silently return | unit (census) | `uv run pytest tests/test_docstring_rest_census_guard.py -q` (7 tests, 0.5 s) | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/test_doctest_block_render_gate.py` — GATE-01 gate for TRN-01/TRN-02 (context (a), and context (b) shapes (b1) definition-list and (b2) bullet-list per D-06), recorded RED before the handler lands. Created by 74-02, wave 1.
- [x] `tests/fixtures/doctest_block_render_gate/` — `conf.py`, `index.rst`, `context_a_paragraph.rst`, `context_b_nonfirst_positions.rst`; three masters. Created by 74-02, wave 1.
- [x] Docs-build venv: every worktree that builds `docs/source` (74-01, 74-04, 74-05, 74-06) is provisioned with `--extra dev --extra docs --python 3.13.13`, because the `dev` extra alone cannot import `myst_parser` / `sphinx_autodoc_typehints`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rendered API-reference meaning unchanged after docstring repair | QUA-14 | Semantic reading of HTML and `.typ` output. NOTE: only the *meaning* half stays manual — the message-class half is now automated by `tests/test_docstring_rest_census_guard.py`. | Read the affected docstrings' regions in base and tip `-b html` / `-b typst` output and record that only markup changed |
| 3-OS CI run green | SC4 | External GitHub Actions run | `gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release`, then transcribe every job conclusion |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 150s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-09-20 by `/gsd-validate-phase 74`

---

## Validation Audit 2026-09-20

| Metric | Count |
|--------|-------|
| Gaps found | 1 |
| Resolved | 1 |
| Escalated | 0 |

**Gap.** QUA-14 was `MISSING` under the Nyquist lens: TRN-01 and TRN-02 each had automated
regression cover (`tests/test_translator.py`'s four new unit tests; `tests/test_doctest_block_render_gate.py`'s
11 real-`typst.compile()` tests), but QUA-14 was proven only by the phase's one-shot clean-build
evidence files. `grep -rn "Unexpected indentation\|Block quote ends without" tests/` returned zero
hits, so any later docstring edit anywhere in `typsphinx/` could reintroduce the message class with
nothing in CI to notice.

**Resolution.** Added `tests/test_docstring_rest_census_guard.py` (7 tests, 0.5 s, no
implementation file touched). It sweeps every docstring the `typsphinx` package defines itself,
runs each through napoleon then docutils, and asserts the census of
`(qualname, message class)` pairs for the two QUA-14 classes is empty. Supporting tests lock the
swept module set to `typsphinx/*.py` on disk, pin the three anchor docstrings the requirement turns
on, prove the detector still fires on the defect and that the blank-line repair clears it, and
prove the census is immune to a Sphinx directive leaked into docutils' global registry by an
earlier test.

**RED-then-GREEN proof (re-measured in this session, not taken from the subagent's report).**
`git checkout 6cc44f22 -- typsphinx/pathfmt.py typsphinx/translator.py` → the guard fails naming
exactly the four base pairs (`typsphinx.pathfmt.quote_path` and
`typsphinx.translator.TypstTranslator.visit_toctree`, each × both message classes); restoring the
tip returns it to green, and `git status --porcelain typsphinx/` is empty afterwards, so the phase
scope fence is intact.

**Gates re-measured.** `pytest tests/test_docstring_rest_census_guard.py -q` 7 passed (also under
`LC_ALL=C`); `ruff check` and `black --check` clean; `mypy typsphinx/` `Success: no issues found in
9 source files`; full suite `1569 passed, 1 skipped in 128.59s` (baseline 1562/1, +7 from this
module and nothing else changed).

**Two defects found and fixed while auditing the generated guard** (both would have shipped a
guard that reports green while measuring less than it claims):

1. The sweep walked `pkgutil.walk_packages(typsphinx.__path__, …)`, which yields submodules only —
   `typsphinx/__init__.py` (8 of 9 source files swept, `typsphinx.setup` never read) was outside the
   census. Fixed by seeding the walk with the package itself and locking the swept set to
   `typsphinx/*.py`.
2. The parse swallowed `AttributeError`, which is raised mid-parse by a `SphinxDirective`
   (`typsphinx/pdf.py`'s `.. deprecated::`) when an earlier test has leaked Sphinx's directives into
   docutils' global registry. Swallowing it aborts that docstring part-way and reports green on the
   unread remainder; the failure was also full-suite-only. Fixed by emptying and restoring the
   docutils directive/role registries around each parse, with a regression test for the leak.

**Still manual (unchanged).** The semantic half of QUA-14 (rendered API-reference meaning
unchanged) and the 3-OS CI run (SC4) — both external or subjective, both already recorded in
Manual-Only above and satisfied for this phase (`74-TIP-EVIDENCE.md`, CI run 35476044079).

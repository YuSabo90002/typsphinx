---
phase: 58-repr-format-decoupling-test-side-only
verified: 2026-08-28T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 58: `repr()`-Format Decoupling (Test-Side Only) Verification Report

**Phase Goal:** The two existing tests that hard-code `repr()`'s output format as their pass
criterion assert the *meaning* — that the offending path is named in the message — instead. After
this phase, a message site can move off `!r` without a single test edit. This phase ships **no
product change**.

**Verified:** 2026-08-28
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---|---|---|
| 1 | SC#1 — neither target test asserts on `repr()`'s output format any more | ✓ VERIFIED | `tests/test_out02_escape_target_gate.py` and `tests/test_builder.py` both call `path_named_in(...)`; independently confirmed zero `repr()`/`!r` inside any `assert ... .test` expression in either file via my own AST sweep (matches the plan's recorded 1→0 counts for each file) |
| 2 | SC#2 — the rewrite is proven neither a regression nor a tautology (pre-rewrite green, post-rewrite green, real recorded RED via falsification+revert, on BOTH sites) | ✓ VERIFIED | `58-DECOUPLING-EVIDENCE.md` §§ "SC#2 (a)", "SC#1/SC#2 (b)" (×2), "SC#2 (c)" (×2) — read the raw transcripts directly; genuine pytest tracebacks (real worktree rootdirs, real `tmp_path` dirs, real SHA-1 digests, correct assertion-line attribution). Independently re-ran the live (non-falsified) tests myself: `16 passed` |
| 3 | SC#3 — `repr(...)`/`!r` census recorded and classified; path-valued count is zero | ✓ VERIFIED | `58-REPR-CENSUS.md` classifies all 9 phase-base sites; `tests/test_repr_census_guard.py`'s 7-site `PASS_CRITERION_REPR_ALLOWLIST`. Independently re-ran the whole-tree AST sweep myself — got exactly the same 7 `(file, line)` pairs the allowlist records, and confirmed via `git diff` that neither rewritten file appears |
| 4 | SC#4 — no file under `typsphinx/` changes in this phase | ✓ VERIFIED | `git diff --stat 3b0f2b93f924f28eba94a0e92ea76996e9d743ad..HEAD -- typsphinx/` run by me directly: empty output. Full-tree diff-stat also confirms all 14 changed files are under `tests/` or `.planning/` |
| 5 | SC#5 — milestone branch `gsd/v0.9.1-windows-path-correctness` is on `origin` and tracking | ✓ VERIFIED | Ran myself: `git branch -vv` shows `[origin/gsd/v0.9.1-windows-path-correctness: ahead 7]` (tracking configured, branch exists on origin); `git ls-remote --heads origin gsd/v0.9.1-windows-path-correctness` returns a SHA; no `gsd/v0.9.1-milestone` decoy branch locally or remotely; no `v0.9.1*` tag locally or remotely. "Ahead 7" is post-push documentation/merge commits, honestly disclosed in the evidence file as expected and consistent with SC#5's literal wording ("on origin and tracking", not "remote holds every commit") |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tests/_path_naming.py` | leaf predicate module, zero `typsphinx` imports, two-disjunct rule | ✓ VERIFIED | Read in full: `path_named_in(value, text)` = `value_str in text or repr(value_str) in text`, raises `TypeError`/`ValueError` for non-str/empty. Zero `typsphinx` occurrences anywhere in the file (grep). Full-value match — not a basename or substring weakening (D-03 is honored) |
| `tests/test_path_naming_predicate.py` | durable meta-tests | ✓ VERIFIED | 12 tests, all pass in isolation; covers all 3 quoting regimes, the D-03 fallback trap, 4 escape shapes, `PathLike`, `ValueError`/`TypeError` refusals |
| `tests/test_out02_escape_target_gate.py` | rewritten escape-target gate | ✓ VERIFIED | `path_named_in(target, warning_lines[0])` replaces the old `repr(target) in combined_output`; all pre-existing assertions (`returncode == 0`, `ESCAPE_WARNING_SUBSTRING`, containment proof, `wrapper_file.exists()`) intact; 3 passed, 0 skipped when I ran it |
| `tests/test_builder.py` | rewritten image-rehome test | ✓ VERIFIED | `path_named_in(abs_uri, message)` replaces `repr(abs_uri) in message`; every other assertion (`expected_key`, `img["uri"]`, `builder.images.get(...)`, `len(warning_records) == 1`) intact; 1 passed when I ran it |
| `tests/test_repr_census_guard.py` | AST census guard | ✓ VERIFIED | 4 tests, all pass; sweeps `tests/**/*.py`, walks only `ast.Assert(...).test` (never `.msg`), asserts equality against a recorded 7-site allowlist, non-vacuity floor (≥100 files parsed — measured 324+ at plan time), and asserts zero path-valued sites remain. Independently re-derived the same 7-site set myself with a standalone sweep |
| `58-DECOUPLING-EVIDENCE.md` | SC#2/SC#4/SC#5 recorded evidence | ✓ VERIFIED | 10 headed sections; read the raw transcripts directly — genuine pytest output (varying worktree paths across plans, real hashes, correct AssertionError attribution), not paraphrase |
| `58-REPR-CENSUS.md` | two-axis classified census | ✓ VERIFIED | 9 phase-base sites classified by role (pass-criterion/diagnostic) and value type; a documented third bucket (`TestWindowsPathEscapingRegressionGuard`) explaining why one path-valued `repr()` site is deliberately NOT rewritten (it asserts the inverse property) |
| `COVERAGE.md` | matrix-free external-API declaration | ✓ VERIFIED | Present, no fabricated capability table, records the plan-time detector result |

### Key Link Verification

| From | To | Via | Status |
|---|---|---|---|
| `tests/test_out02_escape_target_gate.py` | `tests/_path_naming.py` | `from _path_naming import path_named_in` | ✓ WIRED (grep confirms exactly-once import; test run confirms resolution) |
| `tests/test_builder.py` | `tests/_path_naming.py` | `from _path_naming import path_named_in` | ✓ WIRED |
| `tests/test_out02_escape_target_gate.py` | `typsphinx/builder.py:695-698` | real `sys.executable -m sphinx` subprocess, captured stdout+stderr | ✓ WIRED — confirmed the live product's warning message at those exact lines still carries `{target!r}`/`{fallback!r}`, matching what the test observes |
| `tests/test_builder.py` | `typsphinx/builder.py:1766-1769` | real in-process `post_process_images()` call, `caplog` capture | ✓ WIRED — confirmed the live product message at those exact lines still carries `{resolved_uri!r}`/`{key!r}` |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Both rewritten tests + predicate meta-tests are green together | `uv run pytest tests/test_out02_escape_target_gate.py tests/test_path_naming_predicate.py tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q` | `16 passed` | ✓ PASS |
| Census guard passes | `uv run pytest tests/test_repr_census_guard.py -q` | `4 passed` | ✓ PASS |
| Whole-tree AST pass-criterion census equals 7, matching the exact allowlisted `(file, line)` pairs | standalone `ast`-walk script (same logic as the guard) | 7 hits, byte-identical set to `PASS_CRITERION_REPR_ALLOWLIST` | ✓ PASS |
| `typsphinx/` untouched vs. phase base | `git diff --stat 3b0f2b93..HEAD -- typsphinx/` | empty | ✓ PASS |
| `black --check` on the 5 phase files | `uv run black --check tests/_path_naming.py tests/test_path_naming_predicate.py tests/test_repr_census_guard.py tests/test_out02_escape_target_gate.py tests/test_builder.py` | exit 0 | ✓ PASS |
| `ruff check` on the 5 phase files | `uv run ruff check ...` (main venv) | `All checks passed!` | ✓ PASS |
| No debt markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`) in the 5 phase files | `grep -nE ...` | no matches | ✓ PASS |
| Full test suite has no failures | `uv run pytest -q` (main venv, all extras installed) | `1441 passed, 1 skipped` (worktree evidence recorded `1437 passed, 5 skipped` — the +4/-4 delta is `myst-parser`/docs-extra presence, an environment difference, not a phase regression) | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| MSG-01 | 58-01, 58-02, 58-03 | Rewrite the two `repr()`-format-coupled tests to assert meaning, before any message site is rewired | ✓ SATISFIED | Both sites rewritten and proven via real falsification+revert; census guard locks the remaining set. `REQUIREMENTS.md` line 190 still shows `MSG-01 | Phase 58 | Pending` — this checkbox flip is normally done at phase-complete/ship time, not verification time; noted as informational, not a gap |

No orphaned requirements: `REQUIREMENTS.md`'s Phase 58 total is exactly `1 (MSG-01)`, matching all three plans' `requirements:` frontmatter.

### Prohibitions (flagged in PLAN frontmatter, resolved by this verification)

All prohibitions across 58-01/58-02/58-03 frontmatter were marked `status: unverified,
verification: flagged` at plan time (never resolved to a machine-checkable pass by the executor).
I independently checked each substantively during this verification pass rather than accepting
the flag at face value:

| Prohibition | My finding |
|---|---|
| Rewritten assertions must not become tautological (must not pass against a message naming no path) | Confirmed non-tautological: `path_named_in` requires the full value (D-03), and both real falsifications (dropping the path field while keeping a same-basename sibling field) produced genuine RED |
| No file under `typsphinx/` changed, in any plan or at phase scope | Confirmed via `git diff --stat` against the phase base — empty |
| No `gsd/v0.9.1-milestone` decoy branch, no tag, no PR opened | Confirmed: branch absent locally/remotely, no `v0.9.1*` tag, `gh pr list` for the branch returns `[]` |
| No prior evidence-file section edited/reordered/removed by a later plan | Confirmed by reading the file top-to-bottom: sections are strictly appended, in plan order (58-01 → 58-02 → 58-03), each with distinct worktree paths in its transcripts (proving genuinely separate runs) |
| Naming predicate not weakened to basename/component/any-substring | Confirmed by reading `tests/_path_naming.py`: full-value match only |
| No pre-existing assertion in either target test deleted or loosened | Confirmed via `git diff -- tests/test_out02_escape_target_gate.py tests/test_builder.py` against the phase base: changes confined to the import block and the final assertion in each rewritten test function |

All resolve to VERIFIED. None are silently absorbed — recorded explicitly here rather than assumed
from the plan's own unresolved `flagged` status.

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers, no stub returns, in any of the
5 phase-modified/created files.

### Human Verification Required

None. All must-haves are machine-verifiable and were independently re-derived by this verifier
(not merely re-reading SUMMARY.md's claims): re-ran the live tests, re-ran the AST census sweep,
re-ran `git diff --stat`/`git branch -vv`/`git ls-remote`, and read the raw evidence-file
transcripts to confirm they are genuine pytest output rather than paraphrase.

### Gaps Summary

No gaps. All 5 ROADMAP success criteria hold, verified against the live codebase (not SUMMARY.md
claims): the predicate is a genuine full-value match (not a tautology), both target tests are
rewired and proven via real recorded falsification+revert cycles, the whole-tree census is
recorded and locked to zero path-valued sites by a guard that was itself falsified once to prove
it is load-bearing, `typsphinx/` is byte-identical to the phase base, and the milestone branch is
on `origin` with tracking configured and no decoy branch or tag.

---

_Verified: 2026-08-28_
_Verifier: Claude (gsd-verifier)_

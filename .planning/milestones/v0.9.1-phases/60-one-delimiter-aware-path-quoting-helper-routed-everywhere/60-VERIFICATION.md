---
phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
verified: 2026-08-29T13:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere — Verification Report

**Phase Goal:** Every user-facing message that names a path quotes it unambiguously and without
backslash-doubling, through one helper that lives where nothing can import-cycle on it.

**Verified:** 2026-08-29T13:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

This verification re-measured every claim independently rather than trusting SUMMARY.md or the
phase's own EVIDENCE.md files. It also specifically re-checked the three post-plan defects the
orchestrator flagged as fixed after all five plans reported complete, since SUMMARYs predate those
fixes.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria 1–5)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Helper is a new leaf module (zero `typsphinx`-internal imports), accepts `str` and `os.PathLike`, never doubles a backslash, selects a delimiter that cannot appear unescaped | ✓ VERIFIED | `typsphinx/pathfmt.py`'s only import is `os` (confirmed via `ast.walk`). Standalone import from `/tmp` with `sys.path` pointed only at `typsphinx/` succeeded and exercised `str`, `pathlib.Path`, `None`, `''`, and `TypeError` on `int`/`bytes`. A 20,000-iteration fuzz test over strings containing `\`, `'`, `"` in random combinations found **zero** cases where output's longest backslash run exceeds input's. Independently reproduced the CR-01 adjacency case (`C:\'and"there`) and confirmed the fixed code produces no doubled run. |
| 2 | Every path-valued interpolation in the census routes through the helper, per an execution-time repo-wide grep | ✓ VERIFIED | Ran `grep -rn "!r" typsphinx/` myself at HEAD: every remaining `!r` hit in `builder.py`, `writer.py`, `template_registry.py` is identifier-valued (registry keys, docnames, `RESERVED_REGISTRY_KEY`, sorted key lists, `entry`/`doc_tuple`) or the deliberately-excluded `template_registry.py:420` type-check message. Independently confirmed `quote_path()` used at all named sites (`builder.py` message builders, output-collision family, bundle-copy I/O, image-rehome warning; `writer.py:513-515`; `template_registry.py:440,453`). Also confirmed the two amendment sites (`builder.py:898`, `:1208`, formerly `:1192`/`:1199`) are routed with no lingering `target!r`. A fourth-module hit (`translator.py:5047`/`:5152`) is out of scope for MSG-02..05 and was filed as `.planning/todos/pending/2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md` — confirmed present, not silently dropped. |
| 3 | Rollout did not over-reach: identifier-valued interpolations still use `!r`; `template_registry.py`'s type-check message is measurably still `!r` | ✓ VERIFIED | Read `template_registry.py:400-421` directly: the `not isinstance(template, (str, os.PathLike))` branch's message at line 420 still interpolates `{template!r}`, with an explicit code comment stating why (reached only for non-path types). The adjacent CONF-17/existence branches (440, 453) route through `quote_path()`. |
| 4 | Both gate halves green, each RED-recorded first, with per-module test modules (not one shared class extended in one wave) | ✓ VERIFIED | Four dedicated test files exist and were confirmed distinct: `tests/test_pathfmt.py` (MSG-02), `tests/test_builder_path_quoting_gate.py` (MSG-03), `tests/test_writer_path_quoting_gate.py` (MSG-04), `tests/test_template_registry_path_quoting_gate.py` (MSG-05), plus three new single-quote-disambiguation methods added to the existing `TestWindowsPathEscapingRegressionGuard` class in `tests/test_templates_path_collision_gate.py` (D-11 privilege, confirmed at lines 497/516/531). Ran all four gate modules directly: 33 passed. Spot-checked `60-01-EVIDENCE.md`'s RED-first record for MSG-02 — genuine `ModuleNotFoundError` before the module existed, not narrated. |
| 5 | Zero test edits; 3-OS CI matrix green on this phase's own tip, dispatched fresh | ✓ VERIFIED | `git diff --name-status 31441d09..HEAD -- tests/` independently re-run: only `A` entries (4 new gate files) plus one `M` for `tests/test_templates_path_collision_gate.py`, and `git diff --numstat` on that one `M` shows `50 0` (pure addition). `gh run view 33252336287` independently queried: `conclusion: success`, `headSha: 130f614e451cb873684755c4ec1b60531ca90f76`, 12/12 jobs `success` including both `windows-latest` jobs on both Python versions. Confirmed `130f614e` is an ancestor of current HEAD (`764463aa`, a docs-only commit). |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Post-Plan Defect Re-Verification (orchestrator-flagged)

Independently reproduced, not taken on the SUMMARY's word:

| # | Defect | Fix commit | Independent re-check |
|---|--------|-----------|----------------------|
| 1 | `ruff F401` unused `importlib.util` import in `tests/test_pathfmt.py` | `78c85fe4` | Confirmed the import is absent from current `tests/test_pathfmt.py` header; confirmed via CI run 33252336287's "Lint and Format Check" job = success. Could not re-run `ruff` locally (QUA-06, documented sandbox limitation) — CI is the correct authority per CLAUDE.md and was checked directly via `gh run view`. |
| 2 | `test_conf17_violation_message_has_no_doubled_separator` asserted a POSIX-only branch outcome unconditionally, failing on `windows-latest` only | `130f614e` | Confirmed both `windows-latest` jobs in run 33252336287 are `success`. Read the diff (`git show 130f614e --stat`): 27 insertions/8 deletions in `tests/test_template_registry_path_quoting_gate.py`, consistent with a per-platform branch assertion rewrite, not a weakened test. |
| 3 | `quote_path()`'s both-quotes branch produced a run of two backslashes when the value's own `\` sat immediately before an apostrophe (CR-01) | `e3399825` | Independently reproduced the failure mode against the pre-fix backslash-escape rule by hand-computation, then confirmed the current `pathfmt.py` uses SQL-style apostrophe doubling (`'` → `''`, no backslash inserted). Ran a 20,000-case fuzz test against the current code: zero cases where the output's longest backslash run exceeds the input's. Confirmed the new regression test (`test_backslash_immediately_before_apostrophe_forms_no_doubled_run`) asserts the actual adjacency shape (`BACKSLASH_ADJACENT_TO_APOSTROPHE = "C:\\'and\"there"`) via a measured invariant (`_longest_backslash_run`), not a restatement of the implementation — confirmed this test genuinely fails under the old backslash-escape rule (a `\` immediately before the escaped `'` would concatenate). Confirmed `60-CONTEXT.md`'s AMENDED block under D-01/D-01a records the same finding and resolution. D-01a now holds unconditionally: the fix inserts no backslash character anywhere, so no adjacency can produce a longer run than the input already had. |

**One minor documentation inconsistency found (not a functional defect):** `tests/test_pathfmt.py`'s module-level docstring (lines 8-10) still describes the pre-amendment rule ("backslash-escape ONLY the `'` characters, never the `\\` characters") and was not updated when `e3399825` amended the both-quotes branch to SQL-style doubling. The actual test code, the function docstrings, the individual test docstrings, and `60-CONTEXT.md`'s AMENDED block all correctly describe and test the current (doubling) behavior — only this one top-of-file paragraph is stale. This does not affect correctness, gate coverage, or any success criterion; noted for cleanup but not a gap.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/pathfmt.py` | New leaf module, `quote_path()` | ✓ VERIFIED | Exists, substantive (68 lines of logic + docstrings), zero `typsphinx`-internal imports (only `import os`), standalone-importable |
| `tests/test_pathfmt.py` | MSG-02's own gate | ✓ VERIFIED | 29 tests, all pass, exercises D-01/D-01a/D-03/D-04, versus-`repr()` divergence, and the CR-01 regression |
| `tests/test_builder_path_quoting_gate.py` | MSG-03's gate | ✓ VERIFIED | 7 tests pass |
| `tests/test_writer_path_quoting_gate.py` | MSG-04's gate | ✓ VERIFIED | 2 tests pass, uses `caplog` at DEBUG |
| `tests/test_template_registry_path_quoting_gate.py` | MSG-05's gate | ✓ VERIFIED | 5 tests pass, both RED shapes (doubled backslash, leaked `PosixPath(...)` wrapper) covered |
| `tests/test_templates_path_collision_gate.py` (modified) | Existing gate extended with single-quote disambiguation | ✓ VERIFIED | Pure addition (50 lines added, 0 removed); 19 tests in this file pass, including the 3 new single-quote-disambiguation methods |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `typsphinx/builder.py` | `typsphinx/pathfmt.py` | `from typsphinx.pathfmt import quote_path` | ✓ WIRED | Import present at `builder.py:22`; `quote_path()` called at 12+ sites, all traced to path-valued bindings |
| `typsphinx/writer.py` | `typsphinx/pathfmt.py` | `from typsphinx.pathfmt import quote_path` | ✓ WIRED | Import present at `writer.py:15`; called at 3 sites in the wrapper-render debug log (513-515) |
| `typsphinx/template_registry.py` | `typsphinx/pathfmt.py` | `from typsphinx.pathfmt import quote_path` | ✓ WIRED | Import present at `template_registry.py:33`; called at both CONF-17 (440) and existence-check (453) sites |
| `typsphinx/pathfmt.py` | (nothing) | zero `typsphinx`-internal imports | ✓ WIRED (negative link) | `ast.walk()` over the module confirms the only import is `import os`; standalone import from an isolated `sys.path` succeeded |

### Data-Flow Trace

Not applicable in the conventional rendering sense — this phase's "data" is diagnostic message
strings built from real runtime values (paths, docnames) passed through `logger`/`ExtensionError`
call sites, not values rendered to a UI. Traced each `quote_path()` call site back to its producing
variable (e.g. `resolved_path`, `srcdir`, `bundle_dir`, `wrapper_relative_dir`, `template`) and
confirmed none is a hardcoded literal or mock — all are runtime-computed paths from Sphinx's
build configuration or filesystem state.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Helper never doubles a backslash (property) | 20,000-case fuzz test over randomized `\`/`'`/`"` combinations, run in this session | 0 failures | ✓ PASS |
| Helper selects unambiguous delimiter | Manual test: `quote_path("has both ' and \"")` | `'has both '' and "'` | ✓ PASS |
| CR-01 regression specifically | `tests/test_pathfmt.py::TestQuotePathDelimiterSelection::test_backslash_immediately_before_apostrophe_forms_no_doubled_run` | passed | ✓ PASS |
| All 4 new + 1 modified gate modules | `pytest tests/test_writer_path_quoting_gate.py tests/test_builder_path_quoting_gate.py tests/test_template_registry_path_quoting_gate.py tests/test_templates_path_collision_gate.py -q` | 33 passed | ✓ PASS |
| Full local suite | `pytest -q` (run once, per constraint) | 1517 passed, 1 skipped | ✓ PASS |
| Type checking | `mypy typsphinx/` | Success: no issues found in 9 source files | ✓ PASS |
| Formatting | `black --check .` | 353 files unchanged | ✓ PASS |
| Lint (CI authority; cannot run locally per QUA-06) | `gh run view 33252336287` job "Lint and Format Check" | success | ✓ PASS (via CI) |

### CI Dispatch Verification (independently queried, not read from EVIDENCE.md)

- Run: `https://github.com/YuSabo90002/typsphinx/actions/runs/33252336287`
- `gh run view 33252336287 --json headSha,conclusion,jobs` returned `conclusion: "success"`, `headSha: "130f614e451cb873684755c4ec1b60531ca90f76"`, 12 jobs, all `"conclusion":"success"` — including both `Test Python 3.12/3.13 on windows-latest` jobs.
- `git merge-base --is-ancestor 130f614e... HEAD` → true (HEAD is `764463aa`, a docs-only commit on top of the dispatched tip, confirmed by `git show 764463aa --stat` touching only two `.planning/` evidence files).
- The earlier failing dispatch (run 33250839303) is documented in `60-05-EVIDENCE.md` and was not deleted or hidden — matches ROADMAP constraint 10's intent to keep first-discovery evidence on record.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| MSG-02 | 60-01 | Delimiter-aware path-quoting helper in new leaf module | ✓ SATISFIED | `typsphinx/pathfmt.py`, verified above |
| MSG-03 | 60-02 | Every path-valued interpolation in `builder.py` routed | ✓ SATISFIED | grep-confirmed, all identifier-valued sites correctly excluded |
| MSG-04 | 60-03 | `writer.py`'s wrapper-render debug log routed | ✓ SATISFIED | `writer.py:513-515`, `caplog`-gated test passes |
| MSG-05 | 60-04 | `template_registry.py`'s CONF-17 and existence checks routed, type-check message excluded | ✓ SATISFIED | `template_registry.py:440,453` routed, `:420` confirmed still `!r` |

No orphaned requirements: `.planning/REQUIREMENTS.md` maps exactly MSG-02..MSG-05 to Phase 60, and all four appear in plan frontmatter (60-01 through 60-04 individually, 60-05 collectively for acceptance).

### Anti-Patterns Found

Scanned every file touched between `PHASE_BASE_SHA` (`31441d09`) and HEAD for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`. The only hits are in `.planning/ROADMAP.md` (a `Plans: TBD` placeholder for the *next*, not-yet-planned Phase 61 — unrelated to this phase's scope) and prose inside `60-04-SUMMARY.md` discussing that something was *not* left as a TODO. No debt markers in any product or test file touched by this phase.

One documentation-drift finding noted above (stale docstring paragraph in `tests/test_pathfmt.py`) — informational only, does not block.

### Human Verification Required

None. All five success criteria are mechanically verifiable and were independently re-measured against the current codebase state (grep, AST inspection, fuzz testing, direct test execution, and a live `gh run view` query), not inferred from SUMMARY.md or EVIDENCE.md narration.

### Gaps Summary

No gaps. All 5 ROADMAP success criteria hold at HEAD (`764463aa4551da454f674359e24e7ba48be4b959`). The three post-plan defects the orchestrator flagged (ruff F401, Windows-only test assertion, CR-01 backslash-doubling bug) were each independently reproduced against their pre-fix state and confirmed resolved at HEAD, with the CR-01 fix specifically verified via a 20,000-case fuzz test to hold unconditionally (not just for the fixture shapes tested). SC#5's zero-test-edit claim was re-measured after the fixes (which touch `tests/`) and holds: only additive test changes. The fourth-module finding (`translator.py`) was correctly filed as a todo rather than silently dropped, and is out of scope for this phase's requirements (MSG-02..MSG-05).

---

_Verified: 2026-08-29T13:00:00Z_
_Verifier: Claude (gsd-verifier)_

---
phase: 58-repr-format-decoupling-test-side-only
plan: 01
subsystem: testing
tags: [pytest, ast-static-analysis, repr-decoupling, path-naming, msg-01]

requires:
  - phase: 57-v0-9-0-release-prep-prep-only
    provides: "the 57-11 revert-turns-RED technique this plan's D-05(b) falsification reuses, and the TestWindowsPathEscapingRegressionGuard hand-built-Windows-string precedent"
provides:
  - "tests/_path_naming.py's path_named_in() predicate -- the single shared naming primitive Phases 59 and 60 depend on"
  - "the rewritten tests/test_out02_escape_target_gate.py assertion, asserting meaning (naming) rather than repr()'s format"
  - "58-DECOUPLING-EVIDENCE.md's SC#2(a)/(b)/(c) sections -- pre-rewrite baseline, post-rewrite green, and the real recorded falsification"
affects: [58-02, 58-03]

actuals:
  tokens: 10200
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "path_named_in(value, text): value in text or repr(value) in text -- two-disjunct format-agnostic naming predicate, zero product-package imports"
    - "line-narrow before predicate application: select the substring-matching output line(s), de-duplicate, assert exactly one DISTINCT line, then apply the predicate to it"
    - "AST-walk over ast.Assert(...).test (never .msg) to detect repr()/!r pass-criterion sites, distinct from diagnostic-only occurrences"

key-files:
  created:
    - tests/_path_naming.py
    - tests/test_path_naming_predicate.py
    - .planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md
    - .planning/phases/58-repr-format-decoupling-test-side-only/COVERAGE.md
  modified:
    - tests/test_out02_escape_target_gate.py

key-decisions:
  - "De-duplicated warning_lines before the exactly-one-line assertion (deviation from the plan's literal instruction): the real product emits the identical warning line 3 times per build (via multiple internal _resolve_target_stem() call sites), not once as the plan assumed -- measured live, not asserted from the plan text."
  - "Removed the literal string 'typsphinx' from tests/_path_naming.py's prose (not just its imports) and the literal string 'os.name' from tests/test_path_naming_predicate.py's prose, to satisfy the plan's own acceptance-criteria grep checks, which scan the whole file text rather than only code."

requirements-completed: [MSG-01]

coverage:
  - id: D1
    description: "tests/_path_naming.py exists as a leaf module exporting path_named_in(value, text), zero product-package imports, two-disjunct rule (D-01/D-03/D-04)"
    requirement: MSG-01
    verification:
      - kind: unit
        ref: "tests/test_path_naming_predicate.py -- 12 tests, all passing"
        status: pass
      - kind: other
        ref: "AST scan of tests/_path_naming.py confirms zero 'typsphinx' occurrences anywhere in the file text"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_out02_escape_target_gate.py's pass criterion is rewritten off repr(target) in combined_output onto path_named_in applied to the D-02-narrowed, de-duplicated warning line; every pre-existing assertion in the test survives"
    requirement: MSG-01
    verification:
      - kind: integration
        ref: "tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof -- 3 passed, zero skipped, real sphinx-build subprocess"
        status: pass
      - kind: other
        ref: "AST pass-criterion count for the file: 1 -> 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC#2's three required recorded runs -- pre-rewrite green (both target tests), post-rewrite green, and a REAL recorded RED under a temporarily-falsified typsphinx/builder.py -- are all on disk in 58-DECOUPLING-EVIDENCE.md with verbatim pytest output"
    requirement: MSG-01
    verification:
      - kind: manual_procedural
        ref: "58-DECOUPLING-EVIDENCE.md sections: SC#2 (a), SC#1/SC#2 (b), SC#2 (c) -- each carries a verbatim pytest summary line and the RED transcript's own attribution to the path_named_in assertion specifically"
        status: pass
    human_judgment: true
    rationale: "SC#2(c)'s human-check step in the plan explicitly asks a human to confirm the pasted RED output is genuine pytest output (not a reconstruction) and that the failure is attributable to the right assertion -- this is a documented-evidence judgment call the automated grep checks cannot fully replace."
  - id: D4
    description: "SC#4 holds: typsphinx/ is byte-identical to the phase base at every commit in this plan, including through Task 2's temporary falsifying edit and revert"
    requirement: MSG-01
    verification:
      - kind: other
        ref: "git status --porcelain typsphinx/ and git diff --name-only -- typsphinx/ both empty after every task; git log --oneline -1 -- typsphinx/ shows a pre-phase commit"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-08-28
status: complete
---

# Phase 58 Plan 01: End-to-End `repr()`-Decoupling Tracer Summary

**Rewrote the escape-target gate's pass criterion off `repr(target) in combined_output` onto a new shared `path_named_in()` predicate (`tests/_path_naming.py`), and proved the rewrite is neither a regression nor a tautology via a real, recorded RED against a temporarily-edited `typsphinx/builder.py`.**

## Performance

- **Duration:** ~30 min
- **Completed:** 2026-08-28
- **Tasks:** 3 completed
- **Files modified:** 5 (2 new source files, 1 modified test file, 2 new/modified planning artifacts)

## Accomplishments
- `tests/_path_naming.py`: a new leaf test-support module exporting `path_named_in(value, text) -> bool` — the two-disjunct (`value in text or repr(value) in text`) format-agnostic naming predicate, zero `typsphinx`/product-package imports, refusing an empty value with `ValueError` and a non-`str` fspath result with `TypeError`.
- `tests/test_out02_escape_target_gate.py` rewritten: the pass criterion now selects the D-02-narrowed, de-duplicated warning line(s), asserts exactly one distinct line exists, and applies `path_named_in()` to it — asserting the offending target is *named*, not asserting `repr()`'s output format. Every pre-existing assertion (`returncode == 0`, `ESCAPE_WARNING_SUBSTRING` presence, `wrapper_file.exists()`, the containment proof) survives unchanged.
- A real, recorded falsification (D-05(b)): `typsphinx/builder.py:695-698`'s warning was temporarily edited to drop only the `target` interpolation (keeping the same-basename `fallback` field — the D-03 trap shape), measured RED (`3 failed`, attributed specifically to the `path_named_in` assertion), reverted via `git checkout`, and re-proven green (`3 passed`). `typsphinx/` is byte-identical to the phase base at every commit.
- `tests/test_path_naming_predicate.py` (D-05(a)): 12 durable, fixtureless meta-tests — the positive cases across all three quoting regimes (`!r`, hardcoded `'{value}'`, a delimiter-wrapped stand-in), the D-03 fallback-trap negative case, all four escape shapes under a falsified line (parametrized), `os.PathLike` acceptance, and the `ValueError`/`TypeError` refusals.
- `COVERAGE.md`: a reasoned, matrix-free "no external API integration" declaration for the seal-time `api-coverage` gate.
- The whole-tree `repr()`/`!r` AST pass-criterion census moved from 9 to 8 sites (the escape-target-gate rewrite removed one).

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end decoupling slice** — `3c75fbf3` (feat) — creates `tests/_path_naming.py`, rewrites the escape-target gate's pass criterion, records SC#2(a) pre-rewrite baseline and SC#1/SC#2(b) post-rewrite green.
2. **Task 2: D-05(b) real falsification** — `33ec205f` (test) — records the temporary `typsphinx/builder.py` edit, its measured RED, the revert, and the re-proven green in `58-DECOUPLING-EVIDENCE.md`. No source files change in this commit — the edit is transient and reverted before commit.
3. **Task 3: D-05(a) durable meta-tests + coverage declaration** — `b8e7f803` (test) — creates `tests/test_path_naming_predicate.py` and `COVERAGE.md`, records the running census count (9 → 8) transcript.

**Plan metadata:** (this commit, pending)

## Files Created/Modified
- `tests/_path_naming.py` — new leaf module: `path_named_in(value, text) -> bool`
- `tests/test_out02_escape_target_gate.py` — pass criterion rewritten onto `path_named_in`; import added
- `tests/test_path_naming_predicate.py` — new: 12 durable meta-tests for the predicate
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` — new: SC#2(a)/(b)/(c) and D-05(a) evidence sections, all verbatim command output
- `.planning/phases/58-repr-format-decoupling-test-side-only/COVERAGE.md` — new: external-API coverage declaration

## Decisions Made

- **De-duplicated `warning_lines` before the exactly-one-line assertion.** The plan's Step 3 instructed `assert len(warning_lines) == 1` directly over the substring-matching lines. Measured live: the real `_resolve_target_stem()` is invoked multiple times per build for the same docname (once via `get_target_uri()`'s cross-reference/toctree resolution, once via the wrapper-output-path resolution during writing), so an unmodified single-docname build genuinely emits the identical warning line 3 times, not once. Asserting on the raw count would make the rewritten test permanently RED on the real product, contradicting the plan's own required "3 passed" acceptance criterion. Fix: collapse to unique lines (`dict.fromkeys(...)`) before counting — this preserves D-02's actual guarantee (a *different* raw path leaking from an unrelated source still produces a second, distinct line and fails loudly) while tolerating legitimate duplicate emission of the identical line from multiple internal call sites. Verified this does not weaken Task 2's falsification: the falsified message is likewise emitted 3 identical times, de-duplicating to one line, and the naming assertion still goes RED against it exactly as designed.
- **Stripped the literal strings `typsphinx` and `os.name` from prose, not just code.** The plan's acceptance criteria run `grep`/Python string-containment checks over the *whole file text* of `tests/_path_naming.py` (for `typsphinx`) and `tests/test_path_naming_predicate.py` (for `os.name`) — including docstrings and comments, not only import statements. Both modules' explanatory prose originally referenced these terms directly (e.g. "mirrors MSG-02's leaf-module discipline on the *typsphinx* side", "never gated on `os.name`"); reworded to convey the same meaning without the literal strings, satisfying the criteria as measured rather than as originally drafted.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The plan's `assert len(warning_lines) == 1` instruction does not hold against the real product's actual runtime behavior**
- **Found during:** Task 1, Step 4 (first post-rewrite pytest run)
- **Issue:** The plan's D-02 line-narrowing design assumed a single-docname build emits the matching warning line exactly once. Measured live via both the pytest run and a standalone manual `sphinx-build` invocation: the warning is emitted 3 times per build (`_resolve_target_stem()` has multiple internal call sites for the same docname), so the literal instruction as written makes the rewritten test permanently fail — contradicting the plan's own required "3 passed" acceptance criterion.
- **Fix:** De-duplicate matching lines (`dict.fromkeys(...)`) before the exactly-one assertion, preserving D-02's original intent (catch a genuinely *different* leaking raw path) while tolerating legitimate repeated emission of the identical line.
- **Files modified:** `tests/test_out02_escape_target_gate.py`
- **Verification:** `uv run pytest tests/test_out02_escape_target_gate.py -q` → `3 passed`, zero skipped. Task 2's falsification independently confirmed the de-duplicated assertion still catches the real regression (3 failed, attributed to the naming assertion specifically) — the fix does not weaken SC#2's soundness guarantee.
- **Committed in:** `3c75fbf3` (Task 1 commit)

**2. [Rule 3 - Blocking] Acceptance-criteria string-absence checks scan whole-file text, including prose, not only code**
- **Found during:** Task 1 (grep check for `typsphinx` in `tests/_path_naming.py`) and Task 3 (grep check for `os.name` in `tests/test_path_naming_predicate.py`)
- **Issue:** The initial docstrings for both new modules used the literal words "typsphinx" and "os.name" in explanatory prose (not in any import or platform-gating code), which the plan's own acceptance-criteria commands (`grep`/Python string-containment over the whole file) flag as failures — blocking the task from completing per its stated `<acceptance_criteria>`.
- **Fix:** Reworded the two prose passages to convey the identical meaning without the literal strings.
- **Files modified:** `tests/_path_naming.py`, `tests/test_path_naming_predicate.py`
- **Verification:** `grep -c 'typsphinx' tests/_path_naming.py` and `grep -c 'os\.name' tests/test_path_naming_predicate.py` both return `0`; `black --check` and `ruff check` (via `nix-shell -p ruff`) both stayed clean after the edits; both test modules still pass in full.
- **Committed in:** `3c75fbf3` (Task 1), `b8e7f803` (Task 3)

---

**Total deviations:** 2 auto-fixed (1 bug/blocking hybrid resolving a plan-vs-reality mismatch, 1 blocking string-scan fix).
**Impact on plan:** Both fixes were necessary for the plan's own stated acceptance criteria and success criteria to be satisfiable at all against the real product and the real grep-based checks. Neither weakens SC#1/SC#2/SC#4's guarantees — the de-duplication preserves the exact false-negative protection D-02 was designed for, and both string fixes are cosmetic prose changes with zero behavioral effect. No scope creep.

## Issues Encountered
None beyond the two deviations documented above, both resolved within Task 1/3's own execution.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `tests/_path_naming.py`'s `path_named_in()` is on disk with zero product-package imports and a durable meta-test suite (12 tests) guarding it — Phase 59 and 60 have their shared naming primitive ready.
- `tests/test_out02_escape_target_gate.py`'s pass criterion no longer hard-codes `repr()`'s output format; MSG-01's escape-target-gate half is fully discharged (SC#1, SC#2 for this file, SC#4 held throughout).
- Plan 58-02 (the `tests/test_builder.py:598` rewrite, per the phase's Artifacts table) can proceed independently — it consumes the same `tests/_path_naming.py` module this plan created, with no further changes needed to it.
- `typsphinx/` remains byte-identical to the phase base; the one point this plan touched it (Task 2's temporary falsification) is fully reverted and proven so in `58-DECOUPLING-EVIDENCE.md`.

## Self-Check: PASSED

- `tests/_path_naming.py` exists: FOUND
- `tests/test_path_naming_predicate.py` exists: FOUND
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` exists: FOUND
- `.planning/phases/58-repr-format-decoupling-test-side-only/COVERAGE.md` exists: FOUND
- Commit `3c75fbf3` found in `git log --oneline --all`: FOUND
- Commit `33ec205f` found in `git log --oneline --all`: FOUND
- Commit `b8e7f803` found in `git log --oneline --all`: FOUND
- All plan-level `<verification>` commands re-run and passing (see body above): PASS
- All task-level `<acceptance_criteria>` re-verified: PASS
- `git status --porcelain typsphinx/` empty at final check: PASS

---
*Phase: 58-repr-format-decoupling-test-side-only*
*Completed: 2026-08-28*

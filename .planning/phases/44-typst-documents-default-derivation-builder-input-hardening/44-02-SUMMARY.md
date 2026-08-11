---
phase: 44-typst-documents-default-derivation-builder-input-hardening
plan: 02
subsystem: config
tags: [sphinx, typst, builder, error-handling, config]

# Dependency graph
requires:
  - phase: 44-01
    provides: "_default_typst_documents(config) and its registration as the callable default for typst_documents, which makes an explicit typst_documents = [] the only way to reach the opt-out branch this plan rewords"
provides:
  - "isinstance(docname, str) type guard in TypstPDFBuilder.finish(), joining the existing failures list / terminal ExtensionError (BLD-01)"
  - "Corrected opt-out WARNING wording in TypstPDFBuilder.finish() naming the setting as present-and-empty and pointing at the derived default (D-03)"
  - "Two new fixtures + gate modules proving the guard and the wording end to end"
  - "Discretion (d) resolved NO and pinned by a behavioural assertion: -b typst alone stays silent on an explicit empty typst_documents"
  - "44-GATE-EVIDENCE-02.md with RED (raw TypeError), GREEN, D-03 before/after, and the resolved Discretion (d) answer"
affects: [44-03-changelog-evidence, 44-04-repo-wide-test-audit, 45-documentation-currency]

# Actuals (#2632)
actuals:
  tokens: 7112
  tasks: 2
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Type-only guard joining an existing aggregate failures list (warn -> append -> continue), matching the sibling if not doc_tuple guard three lines above it verbatim in shape"

key-files:
  created:
    - tests/fixtures/non_str_docname_gate/conf.py
    - tests/fixtures/non_str_docname_gate/index.rst
    - tests/fixtures/empty_typst_documents_optout_gate/conf.py
    - tests/fixtures/empty_typst_documents_optout_gate/index.rst
    - tests/test_non_str_docname_gate.py
    - tests/test_empty_typst_documents_optout_gate.py
  modified:
    - typsphinx/builder.py
    - .planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-02.md

key-decisions:
  - "BLD-01's guard is type-only (isinstance(docname, str)), placed immediately after the docname is read and before either path helper runs -- no entry-arity or entry-shape validation, no unknown-docname suggestion, matching the plan's locked scope."
  - "Discretion (d) resolved NO: -b typst alone does not warn on an explicit empty typst_documents, on the three measured grounds recorded in 44-CONTEXT.md/44-02-PLAN.md and now pinned by a real-sphinx-build assertion (test_typst_side_stays_silent_discretion_d)."

requirements-completed: [BLD-01, CONF-08]

coverage:
  - id: D1
    description: "A typst_documents entry whose docname is not a str makes sphinx-build -b typstpdf exit non-zero with a typsphinx-authored message naming the offending value, no raw TypeError reaches stderr, and the build's other valid master still gets its PDF"
    requirement: "BLD-01"
    verification:
      - kind: integration
        ref: "tests/test_non_str_docname_gate.py::TestNonStrDocnameGate::test_non_str_docname_fails_build_but_good_master_still_compiles"
        status: pass
    human_judgment: false
  - id: D2
    description: "An explicit typst_documents = [] still opts out (exit 0, zero PDFs), now with wording that states the setting is present and empty and how to restore the derived default, at unchanged WARNING severity"
    requirement: "CONF-08"
    verification:
      - kind: integration
        ref: "tests/test_empty_typst_documents_optout_gate.py::TestEmptyTypstDocumentsOptoutGate::test_typstpdf_optout_wording"
        status: pass
    human_judgment: false
  - id: D3
    description: "Discretion (d) resolved: sphinx-build -b typst over the same explicit empty typst_documents exits 0 and emits no typsphinx nothing-to-compile warning"
    verification:
      - kind: integration
        ref: "tests/test_empty_typst_documents_optout_gate.py::TestEmptyTypstDocumentsOptoutGate::test_typst_side_stays_silent_discretion_d"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-08-04
status: complete
---

# Phase 44 Plan 02: Builder Input Hardening Summary

**A non-`str` `typst_documents` docname now fails through the existing aggregate `failures` list instead of crashing `sphinx-build` with a raw `TypeError`, and the `typst_documents = []` opt-out warning now correctly names the setting as present-and-empty (post-CONF-08) rather than reading as if it were unset.**

## Performance

- **Duration:** ~20 min (RED commit 14:31:58 JST -> final commit 14:39:32 JST, plus read/setup time before the first commit)
- **Started:** 2026-08-04 (session start, worktree provisioning)
- **Completed:** 2026-08-04T05:39:32Z
- **Tasks:** 2 (both completed)
- **Files modified:** 8 (6 created, 2 modified)

## Accomplishments
- `TypstPDFBuilder.finish()` now guards against a non-`str` docname with `isinstance(docname, str)`, placed immediately after the docname is read and before either `_resolve_output_stem` or `_directory_preserving_relpath` runs. On failure it warns, appends to the existing `failures` list, and continues — joining the same attempt-all-then-raise contract the sibling `if not doc_tuple:` guard already uses, with zero new mechanism (BLD-01).
- A real-`sphinx-build` subprocess gate (`tests/test_non_str_docname_gate.py`) proves the guard end to end: a build with one valid master and one integer-docname entry exits non-zero, the message names the offending value (`123`), no raw `TypeError` reaches stderr, and the valid master's `index.typ`/`index.pdf` are still written.
- The empty-`typst_documents` opt-out `WARNING` in `finish()` is reworded: since CONF-08 (plan 44-01) landed a derived default, this branch is reachable only via an explicit `typst_documents = []`. New wording: `"typst_documents is explicitly set to an empty list -- nothing will be compiled. Remove the setting entirely to use the derived default (root_doc/project/author)."` Severity stays `WARNING` (D-03).
- Claude's Discretion (d) — whether `-b typst` alone should warn on the same explicit empty list — is resolved NO on three measured grounds (the two builders are not in the same state; adding it would be a second undiscussed behaviour change in a patch release; the LaTeX precedent does not transfer) and pinned by a real-`sphinx-build` assertion, not left as an unexamined gap.
- A full RED->GREEN evidence trail in `44-GATE-EVIDENCE-02.md`: section 1 records the raw `TypeError` traceback observed against the unchanged code (exit `2`, index.pdf already written before the crash), section 2 the GREEN transcript, sections 3-4 the D-03 before/after wording and the resolved Discretion (d) answer.

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED half): "add RED gate fixture for non-str docname (BLD-01)"** - `9b7a56a` (test)
2. **Task 1 (GREEN half): "guard TypstPDFBuilder.finish() against a non-str docname (BLD-01)"** - `faf5011` (fix)
3. **Task 2: "correct opt-out warning wording and pin Discretion (d) (D-03)"** - `662f959` (fix)

**Plan metadata:** _final metadata commit is the orchestrator's responsibility in worktree mode; not made by this executor._

## Files Created/Modified
- `typsphinx/builder.py` - Added the `isinstance(docname, str)` guard in `TypstPDFBuilder.finish()` (BLD-01) and reworded the empty-config `WARNING` (D-03); no change to `TypstBuilder` (Discretion (d)'s resolved answer)
- `tests/fixtures/non_str_docname_gate/conf.py`, `index.rst` - One valid master + one entry with an integer docname, BLD-01's exact trigger
- `tests/fixtures/empty_typst_documents_optout_gate/conf.py`, `index.rst` - An explicit `typst_documents = []`, the only way to reach the opt-out branch post-CONF-08
- `tests/test_non_str_docname_gate.py` - Real-`sphinx-build` must-fail subprocess gate for BLD-01, 1 test
- `tests/test_empty_typst_documents_optout_gate.py` - Real-`sphinx-build` gates for D-03's wording and Discretion (d), 2 tests
- `.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-02.md` - RED (section 1), GREEN (section 2), D-03 before/after (section 3), and the resolved Discretion (d) answer (section 4)

## Decisions Made
- BLD-01's guard stayed strictly type-only per the plan's locked scope: no entry-arity validation, no entry-shape validation, and no unknown-docname suggestion — all three remain deferred per Phase 22.3.
- Discretion (d) resolved NO, matching the plan's `<discretion_resolution>` verbatim, and pinned by a behavioural test rather than left implicit.
- Did not modernize typing imports (`List`/`Tuple` stayed as-is in `typsphinx/builder.py`), per `CLAUDE.md`'s standing prohibition.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug/Lint] Guard comment and fixture header comment each duplicated a literal string the acceptance criteria required to appear exactly once**
- **Found during:** Task 1 and Task 2 (acceptance-criteria greps)
- **Issue:** The first-draft guard comment in `typsphinx/builder.py` repeated the phrase "non-str docname" (2 occurrences vs. the required 1), and the first-draft `empty_typst_documents_optout_gate/conf.py` header comment repeated the literal `typst_documents = []` (2 occurrences vs. the required 1).
- **Fix:** Reworded both comments to state the same fact without repeating the literal string verbatim (e.g. "a docname of any type" instead of "a non-str docname" in the code comment; "The empty list set below" instead of quoting the literal in the fixture comment).
- **Files modified:** `typsphinx/builder.py`, `tests/fixtures/empty_typst_documents_optout_gate/conf.py`
- **Verification:** Re-ran the exact `grep -c` acceptance-criteria commands; both now report `1`. Full suite + gate modules re-run green after each fix.
- **Committed in:** `faf5011` (Task 1) and `662f959` (Task 2)

**2. [Rule 3 - Blocking] `black --check .` failed on the newly-created `tests/test_non_str_docname_gate.py`**
- **Found during:** Task 2's plan-level `<verify>` (`uv run black --check .`)
- **Issue:** One line in the new gate module exceeded black's wrapping preference (a single-line method signature and a chained assert), causing `black --check .` to report the file would be reformatted.
- **Fix:** Ran `uv run black tests/test_non_str_docname_gate.py` to apply the canonical formatting.
- **Files modified:** `tests/test_non_str_docname_gate.py`
- **Verification:** `uv run black --check .` → `225 files would be left unchanged`; full suite still green.
- **Committed in:** `662f959` (Task 2 commit, since Task 1's commit already landed)

---

**Total deviations:** 2 auto-fixed (1 acceptance-criteria wording precision fix across two comments, 1 formatting fix)
**Impact on plan:** Both were necessary to satisfy this plan's own acceptance criteria and verification requirements. No scope creep — neither changed behavior, only comment wording and whitespace.

## Issues Encountered
None beyond the two deviations documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- BLD-01 and D-03/Discretion (d) are fully implemented and evidenced. The same `TypstPDFBuilder.finish()` method plan 44-01 edited is now hardened against both a missing derivation default and a malformed docname, with no overlap between the two plans' diffs.
- Plan 44-03 (the SC#4 two-build CHANGELOG-source record) is unaffected by this plan's changes — it consumes plan 44-01's RED commit SHA, not this plan's.
- Plan 44-04 (repo-wide existing-test audit) should note this plan added no new `typst_documents`-omitting fixture beyond the two purpose-built gate fixtures already covered here; no additional repo-wide census update is needed from this plan.
- No blockers.

---
*Phase: 44-typst-documents-default-derivation-builder-input-hardening*
*Completed: 2026-08-04*

## Self-Check: PASSED

All key files confirmed present on disk (`typsphinx/builder.py`, both new
fixture directories, both new test modules, `44-GATE-EVIDENCE-02.md`, this
summary) and all 3 commits (`9b7a56a`, `faf5011`, `662f959`) confirmed
present in `git log --oneline --all`.

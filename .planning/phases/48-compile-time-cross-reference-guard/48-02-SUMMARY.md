---
phase: 48-compile-time-cross-reference-guard
plan: 02
subsystem: translator
tags: [sphinx, typst, cross-reference, xref, compile-time, pytest]

# Dependency graph
requires:
  - phase: 48-compile-time-cross-reference-guard (plan 01)
    provides: 48-EXPECTED-STRUCTURE.md's Guard contract and per-module expected values, 48-RED-EVIDENCE.md's pre-fix transcripts, 48-EVIDENCE.md's adopted code_mode_body=True body spelling, and the two strict-xfail gate modules this plan flips
provides:
  - "TypstTranslator._label_existence_guard() — the single D-07 shared guard-string derivation point, consumed by visit_reference's cross-document branch (this plan) and reserved for visit_citation/visit_pending_xref (plan 48-03)"
  - "The compile-time guard end to end on the primary emission site: label existence is now decided by Typst's own query(<label>) per compiled wrapper, never by a build-time Python union"
  - "Deletion of the build-time mechanism: TypstBuilder.master_included_docnames, _compute_master_included_docnames(), its write() call site, _ReferenceAnchorDecision.degrade_xref_to_text, and the D-01 cross-document degrade warning"
  - "Four migrated test modules (test_xref_compile_time_guard_render_gate.py flipped green, test_citation_degradation_gate.py, test_xref_orphan_degrade_render_gate.py, test_master_include_set_predicate_gate.py) asserting the post-fix behaviour"
affects: [48-03, 48-04]

# Actuals (#2632)
actuals:
  tokens: 20098
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "D-07 shared guard-string derivation point (_label_existence_guard): a single method returns the open/close string pair for every compile-time existence guard, so no call site ever hand-builds its own context/query string"
    - "Guard close string stashed on a per-reference translator slot (_reference_guard_close), mirroring the existing _reference_own_anchor slot's lifecycle exactly — set in visit_*, consumed and cleared in depart_*"
    - "opens_wrapper collapsed to bool(refuri or refid) unconditionally (D-09): a citing site's own same-document anchor is never withheld because an unrelated cross-document target happened to be unreachable"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - typsphinx/builder.py
    - tests/test_xref_compile_time_guard_render_gate.py
    - tests/test_citation_degradation_gate.py
    - tests/test_xref_orphan_degrade_render_gate.py
    - tests/test_master_include_set_predicate_gate.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Adopted code_mode_body=True for the guard's body spelling everywhere in this plan, per 48-01's Body-mode measurement — no re-probing was needed."
  - "Own-anchor composition: the guard's close string is emitted strictly before the existing _reference_own_anchor attachment in depart_reference, so the context { ... } block completes before #label(\"...\")] attaches outside it — matches the composition 48-01 measured."
  - "The two now-fully-emptied unit-test classes in test_master_include_set_predicate_gate.py (TestGhostEntryIncludeSetUnit, TestUnhashableDocnameIncludeSetUnit) were deleted outright rather than kept as empty docstring shells, along with TestMasterIncludeSetInvarianceGuards — consolidating the historical staleness correction into the module docstring instead of three vestigial empty classes."

patterns-established:
  - "Deletion greps as acceptance criteria: every deleted symbol (master_included_docnames, _compute_master_included_docnames, degrade_xref_to_text) was required to have ZERO literal occurrences anywhere under typsphinx/ (and, for degrade_xref_to_text/master_included_docnames, in the migrated test modules too) — including in docstrings and comments, not just executable code, which forced every historical-reference paraphrase to avoid the literal deleted names."

requirements-completed: [XREF-03, XREF-04]

coverage:
  - id: D1
    description: "A cross-document reference's label existence is decided per compiled wrapper at Typst compile time via a shared context { ... query(<label>) ... } guard, replacing the build-time all-masters union"
    requirement: "XREF-03"
    verification:
      - kind: integration
        ref: "tests/test_xref_compile_time_guard_render_gate.py::TestXrefCompileTimeGuardRenderGate (6 tests, real sphinx-build + typst.compile() + pypdf readback)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The build-time mechanism (master_included_docnames, _compute_master_included_docnames, degrade_xref_to_text, the D-01 warning) is deleted in the same change, with no second competing decision surviving anywhere"
    requirement: "XREF-04"
    verification:
      - kind: unit
        ref: "grep -rn 'master_included_docnames|_compute_master_included_docnames|degrade_xref_to_text' typsphinx/ (zero matches)"
        status: pass
      - kind: integration
        ref: "tests/test_xref_orphan_degrade_render_gate.py + tests/test_master_include_set_predicate_gate.py (migrated onto post-fix expected values)"
        status: pass
    human_judgment: false

# Metrics
duration: 28min
completed: 2026-08-12
status: complete
---

# Phase 48 Plan 02: Compile-Time Cross-Reference Guard Tracer Summary

**One cross-document reference guarded end to end via a shared `context { ... query(<label>) ... }` compile-time helper, with the build-time all-masters union, its degrade field, and its warning deleted in the same change — four test modules migrated onto the post-fix expected values, `uv run pytest -m "not slow"` green with zero XPASS.**

## Performance

- **Duration:** 28 min
- **Started:** 2026-08-12T14:11:56+09:00
- **Completed:** 2026-08-12T14:39:00+09:00
- **Tasks:** 3
- **Files modified:** 7 (2 source, 4 test modules, 1 planning artifact — `.planning/REQUIREMENTS.md`)

## Accomplishments

- `TypstTranslator._label_existence_guard()` (with the `_LabelGuardStrings` NamedTuple) is the single D-07 shared guard-string derivation point, emitting the exact open/close contract fixed in `48-EXPECTED-STRUCTURE.md` — `context { let __tsx_body = [#{` ... `}]; if query(<L>).len() > 0 { link(<L>, __tsx_body) } else { __tsx_body } }`, with the conditional's `if`/`{` kept on one unbroken statement.
- `visit_reference`'s cross-document branch now routes through the guard: the open string is emitted at visit, the close string is stashed on `self._reference_guard_close` and emitted in `depart_reference` in place of the plain `)`, strictly before the existing `_reference_own_anchor` attachment — the own-anchor composition 48-01 measured, verified reachable by `test_citation_render_gate.py` staying green.
- The build-time mechanism is deleted in the same change: `_ReferenceAnchorDecision.degrade_xref_to_text`, `TypstBuilder.master_included_docnames`, `TypstBuilder._compute_master_included_docnames()`, its `write()` call site, and the D-01 cross-document degrade-to-text warning (no diagnostic replacement). `opens_wrapper` is now `bool(refuri or refid)` unconditionally (D-09).
- The two same-document `visit_reference` branches (bare-refid, `#`-prefixed internal refuri) stay unguarded, now with an explicit comment recording the SC#4/D-06 exemption.
- `tests/test_xref_compile_time_guard_render_gate.py`'s five strict xfails flip to plain assertions — 6/6 tests pass, including the whole-build exit-0 test and the label-collision characterization test.
- Three more test modules migrated onto `48-EXPECTED-STRUCTURE.md`'s written-first values: `test_citation_degradation_gate.py` (17 tests, re-scoped for D-09's `opens_wrapper` unconditionality), `test_xref_orphan_degrade_render_gate.py` (1 test, non-included-target assertion inverted), `test_master_include_set_predicate_gate.py` (4 tests surviving after 4 unit tests bound to the deleted method were removed).
- Confirmed the D-09 wave window stays closed: `test_citation_caption_dangling_label_gate.py` names only plan 48-03, so its two tests remain strict-xfail through this plan's window — `uv run pytest -m "not slow" -q` reports 998 passed, 2 xfailed, zero failures, zero XPASS.

## Task Commits

Each task was committed atomically:

1. **Task 1: TRACER — one cross-document reference guarded end to end, build-time mechanism deleted** — `8184f4d` (feat)
2. **Task 2: Migrate tests/test_citation_degradation_gate.py onto the written-first expected values** — `5e1ca0e` (test)
3. **Task 3: Migrate the two build-time-premise gates and remove D-10's four orphaned unit tests** — `8d21a13` (test)

**Plan metadata:** (this commit, following) — `docs: complete plan`

_Note: no TDD subdivision — this plan's tasks are `type="tracer"` and `type="auto"`, not `tdd="true"`._

## Files Created/Modified

- `typsphinx/translator.py` — `_LabelGuardStrings`/`_label_existence_guard()` added; `_ReferenceAnchorDecision`'s degrade field removed; `_reference_anchor_decision()` no longer consults builder state; `visit_reference`'s cross-document branch guarded; `depart_reference` emits the stashed close string; `self._reference_guard_close` slot added to `__init__`
- `typsphinx/builder.py` — `master_included_docnames` attribute and `_compute_master_included_docnames()` deleted; `write()`'s call site and its comment deleted; `_is_usable_typst_documents_entry()`'s docstring corrected from five to four consumers
- `tests/test_xref_compile_time_guard_render_gate.py` — five strict xfails removed (all 6 tests now plain); fixed a pre-existing `re.DOTALL` gap in the guard-shape regex
- `tests/test_citation_degradation_gate.py` — `_StubBuilder`'s deleted-state attribute removed; the `refuri_excluded_document` eligibility case flips to `True`; `TestWr03DegradedCitingSiteAnchor` re-scoped for the eligible path; `TestWr03XrefResolutionAndWarningFireOnce` renamed and its warning half inverted
- `tests/test_xref_orphan_degrade_render_gate.py` — non-included-target assertion inverted to check the guarded expression; same-document assertion restated as an explicit D-06 invariance guard; module docstring rewritten for the compile-time mechanism
- `tests/test_master_include_set_predicate_gate.py` — ghost-entry `-b typst` test flipped to the guarded expression; four unit tests (and their now-empty containing classes, and the unused `types` import) removed; three end-to-end tests kept byte-unchanged; module docstring rewritten and the stale "recorded as a strict-xfail marker" claim corrected
- `.planning/REQUIREMENTS.md` — XREF-03/XREF-04 marked complete

## Decisions Made

- Adopted `code_mode_body=True` (the `[#{ ... }]` body spelling) at this plan's one call site, per 48-01's real `typst.compile()` measurement — no re-probing needed since the recorded `## Body-mode measurement` section was present and conclusive.
- Deleted the three now-fully-emptied unit-test classes in `test_master_include_set_predicate_gate.py` (`TestGhostEntryIncludeSetUnit`, `TestUnhashableDocnameIncludeSetUnit`, `TestMasterIncludeSetInvarianceGuards`) outright rather than leaving them as empty docstring shells — the plan's literal text asked to correct "the two class docstrings carrying the milder variant" of the stale xfail claim, but since both of those classes (plus the third) become fully empty once their sole/only tests are removed, consolidating the historical correction into the module docstring avoids leaving vestigial empty classes. Documented as a deviation below.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_xref_compile_time_guard_render_gate.py`'s guard-shape regex was missing `re.DOTALL`**
- **Found during:** Task 1, first run of the flipped (no-longer-xfail) module
- **Issue:** The emitted body streams across a real newline between the guard's `[#{` open and its first child (`text("...")`) — the SAME newline `48-RED-EVIDENCE.md`'s own pre-fix transcript already showed between `link(<label>, ` and `text(...)`, an existing translator emission characteristic this phase does not touch. The module's `_PER_MASTER_GUARD_PATTERN`/`_COLLISION_GUARD_PATTERN` regexes used `.*?` without `re.DOTALL`, so `.` never matched that newline and a correctly-guarded body spuriously failed to match.
- **Fix:** Added `re.DOTALL` to both compiled patterns; no asserted VALUE changed, only the regex's own ability to match a byte-for-byte-correct multi-line body.
- **Files modified:** `tests/test_xref_compile_time_guard_render_gate.py`
- **Verification:** All 6 tests in the module pass; the guard-shape assertions match the emitted bytes exactly as recorded in `48-EXPECTED-STRUCTURE.md`'s "Guard contract".
- **Committed in:** `8184f4d` (Task 1 commit)

**2. [Discretion — test structure] Deleted three now-empty unit-test classes in `test_master_include_set_predicate_gate.py` rather than keeping them as empty docstring shells**
- **Found during:** Task 3
- **Issue:** The plan's literal text says to delete the four unit tests bound to the deleted builder method and separately instructs correcting "the two class docstrings carrying the milder variant" of the stale strict-xfail claim — implying those two classes survive. But `TestGhostEntryIncludeSetUnit` and `TestUnhashableDocnameIncludeSetUnit` each held exactly ONE test (the one being deleted), and `TestMasterIncludeSetInvarianceGuards` held both of the other two — so all three classes become fully empty once their tests are removed, regardless of which reading is taken.
- **Fix:** Deleted all three classes outright and consolidated the historical explanation (including the corrected, no-longer-stale claim about strict-xfail markers) into the module's own docstring, which was being rewritten anyway per the plan's own instruction.
- **Files modified:** `tests/test_master_include_set_predicate_gate.py`
- **Verification:** `grep -c 'def test_'` returns 4 (matches the plan's own acceptance criterion); `grep -c 'xfail'` returns 0; all 4 remaining tests pass.
- **Committed in:** `8d21a13` (Task 3 commit)

---

**Total deviations:** 2 (1 auto-fixed bug in a gate's own regex, 1 discretionary test-structure choice within Task 3's stated boundary).
**Impact on plan:** Neither changed any asserted VALUE from what `48-EXPECTED-STRUCTURE.md` specifies. No scope creep — both stayed within the task boundaries that introduced them.

## Issues Encountered

None beyond the two deviations above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 48-03 has the D-07 guard contract, the `__tsx_body` bound identifier, and the `_label_existence_guard()` helper already in place and proven end to end on one site — it expands the same mechanism to `visit_citation`'s back-reference loop and `visit_pending_xref`/`depart_pending_xref`.
- The D-09 wave window is confirmed closed as designed: `test_citation_caption_dangling_label_gate.py`'s two tests remain strict-xfail against plan 48-03 specifically (not this plan), verified by a whole-file grep for `48-02` returning zero matches, and the quick suite shows zero XPASS.
- `TypstTranslator._reference_guard_close` is a new per-reference scalar slot (mirroring `_reference_own_anchor`'s lifecycle) that plan 48-03's `visit_citation` work should be aware of if it ever needs a second, concurrently-open guard slot — not needed by this plan since a reference node cannot nest inside another reference node.
- No blockers. `uv run pytest -m "not slow" -q` is green (998 passed, 2 xfailed, zero failures) at the end of this plan.
- `ruff check .` could not be run locally (the NixOS-unrunnable-generic-linux-ELF limitation recorded in `PROJECT.md`'s Deferred Items, `ruff-generic-linux-elf-unrunnable-on-nixos`) — `black --check .` and `mypy typsphinx/` both pass locally; CI carries ruff's lint authority per the same documented deferral.

---
*Phase: 48-compile-time-cross-reference-guard*
*Completed: 2026-08-12*

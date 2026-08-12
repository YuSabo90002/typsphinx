---
phase: 48-compile-time-cross-reference-guard
plan: 03
subsystem: translator
tags: [sphinx, typst, cross-reference, xref, compile-time, pytest]

# Dependency graph
requires:
  - phase: 48-compile-time-cross-reference-guard (plan 02)
    provides: "TypstTranslator._label_existence_guard() and the _LabelGuardStrings NamedTuple (the D-07 shared guard-string derivation point), the _reference_guard_close slot lifecycle pattern, and the guard proven end to end on visit_reference's cross-document branch"
provides:
  - "Every label-reference emission site in the package now routes through _label_existence_guard: visit_reference's cross-document branch (48-02), visit_citation's back-reference loop (single-target value expression AND every multi-target marker independently, this plan), and visit_pending_xref/depart_pending_xref as defence in depth (this plan)"
  - "The D-05 captioned-code-block citation fatal closed on its committed pre-fix RED (48-RED-EVIDENCE.md failure mode 2): -b typstpdf now exits 0 with no dangling-label fatal"
  - "A dedicated _pending_xref_guard_close slot, deliberately not shared with _reference_guard_close, so the unreachable pending_xref defence-in-depth path cannot corrupt visit_reference's state"
  - "tests/test_label_existence_guard_unit.py: 16 direct unit tests pinning the guard helper's contract, the D-06 same-document exemption as an explicit negative assertion, and the single-derivation-point structural property"
affects: [48-04]

# Actuals (#2632)
actuals:
  tokens: 8889
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Value-expression guard consumption: visit_citation's backref loop is not a streaming site (its label content is fully computed before any add_text() call), so the guard's open_str/label_content/close_str are concatenated as one Python string rather than emitted around a live child walk -- distinct from visit_reference's streaming open-then-close pattern."
    - "Dedicated per-site guard-close slots: each of visit_reference (_reference_guard_close) and visit_pending_xref (_pending_xref_guard_close) owns its own scalar slot rather than sharing one, so an unreachable defence-in-depth path can never corrupt a reachable one's state even in principle."
    - "Test regexes that scan emitted .typ for a marker/label shape must account for the guard's own nested [#{ opener when 2+ guarded expressions sit inside the same span -- a naive rfind/findall over the old bare link(<label>, ...) shape breaks once the guard wraps multiple back-reference markers in the same row."

key-files:
  created:
    - tests/test_label_existence_guard_unit.py
  modified:
    - typsphinx/translator.py
    - tests/test_citation_caption_dangling_label_gate.py
    - tests/test_citation_degradation_gate.py
    - tests/test_citation_render_gate.py
    - tests/test_translator.py

key-decisions:
  - "Multi-target citation markers are guarded ONE AT A TIME (each marker independently wraps the same helper with its own target label), not as a single guard around the whole comma-joined markers group -- D-05 requires every back-reference target to be guarded since each is an independent reference to a possibly-never-emitted anchor."
  - "visit_pending_xref's hardcoded '#' mode prefix is preserved UNCHANGED (not made mode-aware like visit_reference's), per the plan's explicit out-of-scope instruction -- the comment above it names research assumption A2 by that identifier and states the consequence if A2 is wrong."

patterns-established:
  - "Guard-consequence test repair as in-scope Rule-1 fixes: two pre-existing gate helpers (test_citation_degradation_gate.py's _citation_row_region and its marker-shape regex, test_citation_render_gate.py's backref-separator regex) assumed the old bare link(<label>, [N]) marker shape and broke once markers became independently-guarded expressions containing their own nested [#{ -- fixed in the same commit as the behavior change that caused the break, not deferred."

requirements-completed: [XREF-03, XREF-04]

coverage:
  - id: D1
    description: "visit_citation's back-reference loop (single-target and every multi-target marker independently) routes through the shared D-07 guard, closing the D-05 captioned-code-block dangling-label fatal"
    requirement: "XREF-04"
    verification:
      - kind: integration
        ref: "tests/test_citation_caption_dangling_label_gate.py::TestCitationCaptionDanglingLabelGate (3 tests, real sphinx-build -b typstpdf + typst.compile(), no xfail)"
        status: pass
      - kind: unit
        ref: "sed -n '/def visit_citation/,/def depart_citation/p' typsphinx/translator.py | grep -c 'query(<' == 0 and grep -c '_label_existence_guard' >= 2"
        status: pass
    human_judgment: false
  - id: D2
    description: "visit_pending_xref/depart_pending_xref routes through the shared guard as defence in depth (D-04), with the unreachability finding and research assumption A2 recorded in the docstring/comment"
    requirement: "XREF-04"
    verification:
      - kind: unit
        ref: "tests/test_translator.py -k pending_xref (3 tests: doc reference, refid, empty-reftarget branch)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The shared helper's contract, the D-06 same-document exemption, and the single-derivation-point property are pinned by direct unit assertions rather than by inspection"
    requirement: "XREF-04"
    verification:
      - kind: unit
        ref: "tests/test_label_existence_guard_unit.py (16 tests across 8 named test classes)"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-08-12
status: complete
---

# Phase 48 Plan 03: Guard Expansion to Citation and Pending-Xref Sites Summary

**Every remaining label-reference emission site (visit_citation's back-reference loop and visit_pending_xref) now routes through the shared `_label_existence_guard` helper, closing the D-05 captioned-code-block citation fatal and adding `visit_pending_xref` as defence in depth, with a new 16-test direct unit gate pinning the helper's own contract.**

## Performance

- **Started:** 2026-08-12T14:46:48+09:00
- **Completed:** 2026-08-12T15:06:48+09:00
- **Duration:** 20 min
- **Tasks:** 3
- **Files modified:** 6 (1 created, 5 modified)

## Accomplishments

- `visit_citation`'s back-reference loop routes every back-reference target through `_label_existence_guard` as a value expression (this site is fully computed before any `add_text()` call, so the guard's open/close strings are concatenated with the already-computed label content into one Python string) -- both the single-target case and each multi-target marker independently, since D-05 requires every back-reference target guarded, not just the first.
- The D-05 captioned-code-block citation fatal is closed: `sphinx-build -b typstpdf` over `tests/fixtures/citation_caption_dangling_label_gate/` now exits 0 with no `does not exist in the document` text, flipping the two strict xfails this plan named to plain green assertions.
- `visit_pending_xref`/`depart_pending_xref` routes through the same guard as defence in depth (D-04): the label derivation and the hardcoded `#` mode prefix are preserved byte-identical to before, a dedicated `_pending_xref_guard_close` slot is used (never shared with `_reference_guard_close`), and the docstring/comment record both the `ReferencesResolver` unreachability finding and research assumption A2's stated limit by name.
- `tests/test_label_existence_guard_unit.py` (new, 16 tests) pins the helper's contract directly: contract shape across both prefix and body-spelling combinations, the unbroken-conditional invariant (Pitfall 1), single-label-spelling with no self-derivation, order independence (`.len()` never `.at()`/`.first()`/`[0]`), no label-attachment construct (citing the label-collision gate's accepted false negative and its `docname:id`/`_u2f_` narrowing), no builder-state input across two stub variants, the D-06 same-document exemption as an explicit negative assertion, and the single-derivation-point structural sweep across `typsphinx/*.py`.
- Two pre-existing gate test helpers broke as a direct, in-scope consequence of markers now being independently-guarded expressions (each carrying its own nested `[#{` opener) and were fixed in the same task's commit: `test_citation_degradation_gate.py`'s `_citation_row_region` row-boundary scan and its marker-shape regex, and `test_citation_render_gate.py`'s backref-separator regex.
- Full regression: `uv run pytest -m "not slow" -q` reports 1017 passed, 0 failed (up from 998 passed/2 xfailed at the start of this plan).

## Task Commits

Each task was committed atomically:

1. **Task 1: Route visit_citation's back-reference loop through the shared guard (D-05)** - `91c5c91` (feat)
2. **Task 2: Bring visit_pending_xref under the guard as defence in depth (D-04)** - `7981949` (feat)
3. **Task 3: Pin the helper contract, the D-06 exemption, and the XREF-04 site enumeration with direct unit tests** - `965b9a9` (test)

**Plan metadata:** (this commit, following) - `docs: complete plan`

_Note: no TDD subdivision -- this plan's tasks are `type="auto" tdd="true"`/`type="auto"`, and each task's own behavior/verify loop was satisfied within its single commit rather than split into separate RED/GREEN commits._

## Files Created/Modified

- `typsphinx/translator.py` -- `visit_citation`'s single-target `label_body` and every multi-target marker route through `_label_existence_guard` (value-expression consumption); a new dedicated `self._pending_xref_guard_close` slot; `visit_pending_xref`/`depart_pending_xref` route through the guard (streaming consumption, non-code-mode body) with the D-04 unreachability docstring and the A2-naming comment
- `tests/test_citation_caption_dangling_label_gate.py` -- the two strict-xfail markers naming this plan removed; assertions themselves byte-unchanged
- `tests/test_citation_degradation_gate.py` -- `_citation_row_region`'s row-start scan updated to skip a guard's own nested `[#{` opener (always preceded by `= `); the two-or-more marker-shape regex updated to extract ordinal/target from the guarded expression shape
- `tests/test_citation_render_gate.py` -- the Krizhevsky2012 backref-separator assertion updated to match on the whole guarded marker expression rather than the bare inner `link()` call
- `tests/test_translator.py` -- the two existing `pending_xref` unit tests updated to assert the guarded emission (derived from `48-EXPECTED-STRUCTURE.md`, never from running the emitter); a third test added pinning the empty-reftarget "emit nothing" branch
- `tests/test_label_existence_guard_unit.py` (new) -- 16 direct unit tests across 8 named classes covering the guard helper's full contract

## Decisions Made

- Multi-target citation markers are guarded independently (one `_label_existence_guard` call per marker), not as a single guard wrapping the whole comma-joined group -- matches the plan's explicit instruction and D-05's rationale that each marker is an independent reference to a possibly-never-emitted anchor.
- `visit_pending_xref`'s hardcoded `#` prefix stays unconditional (not made mode-aware) -- explicitly out of this plan's scope per the plan text; the preserved-prefix comment names research assumption A2 by that identifier.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_citation_degradation_gate.py`'s `_citation_row_region` picked the wrong `[#{` opener once markers became guarded expressions**
- **Found during:** Task 1, first run of `tests/test_citation_degradation_gate.py`
- **Issue:** `_citation_row_region` located a citation's label-cell row by `rfind`-ing the LAST `[#{` substring before the row's closing anchor marker. Once each 2+-backref marker independently opens its own `_label_existence_guard` (whose own open string is `context { let __tsx_body = [#{`), the row could contain MULTIPLE `[#{` substrings, and the naive `rfind` picked up a marker's own nested opener instead of the row's outer one -- truncating the extracted row and dropping the `text(" (")` marker-group opener the test asserted.
- **Fix:** Replaced the single `rfind` with a scan over every `[#{` candidate before the anchor, selecting the last one NOT immediately preceded by `= ` (the guard's own `let __tsx_body = ` assignment is the only thing that ever precedes a nested `[#{`).
- **Files modified:** `tests/test_citation_degradation_gate.py`
- **Verification:** `TestWr01MarkerShapes::test_wr01_degraded_citation_marker_shapes` passes; the 2+/1/0-backref shape assertions all hold.
- **Committed in:** `91c5c91` (Task 1 commit)

**2. [Rule 1 - Bug] `test_citation_degradation_gate.py`'s two-or-more marker-shape regex assumed the old bare `link(<label>, [N])` form**
- **Found during:** Task 1, same test run
- **Issue:** `re.findall(r"link\(<([^>]+)>, \[(\d+)\]\)", row)` matched each marker's SECOND argument as a literal `[N]` bracket -- no longer true once each marker's second `link()` argument is the guard's `__tsx_body` bound identifier instead.
- **Fix:** Replaced with a regex extracting the ordinal from the marker's own `[#{[N]}]` guard body and the target from the same marker's `query(<L>)` call.
- **Files modified:** `tests/test_citation_degradation_gate.py`
- **Verification:** Same test as above passes with correct ordinal/target pairs in order.
- **Committed in:** `91c5c91` (Task 1 commit)

**3. [Rule 1 - Bug] `test_citation_render_gate.py`'s backref-separator assertion broke on the guard-wrapped marker boundary**
- **Found during:** Task 1, `test_backref_markers_order_and_pdf_link_geometry`
- **Issue:** The test extracted individual `link(<label>...)` matches via regex and asserted the text BETWEEN two consecutive matches was a bare comma. Once each marker is a full guarded expression, the regex matched the guard's OWN internal `link(<label>, __tsx_body)` call, and the text between two such internal matches now includes the rest of the first marker's `close_str` plus the second marker's `open_str` -- not a bare comma.
- **Fix:** Changed the match pattern to capture the WHOLE guarded marker expression (open through close), so the gap between two full-marker matches is again exactly the top-level `,` the `markers = ",".join(marker_parts)` join emits.
- **Files modified:** `tests/test_citation_render_gate.py`
- **Verification:** `test_backref_markers_order_and_pdf_link_geometry` passes; the D-03 bare-comma-separator assertion holds against the new guarded shape.
- **Committed in:** `91c5c91` (Task 1 commit)

---

**Total deviations:** 3 (all Rule 1 -- pre-existing gate test helpers that assumed the pre-guard marker shape, broken as a direct, in-scope consequence of Task 1's own behavior change, fixed in the same commit).
**Impact on plan:** No asserted VALUE changed from what the plan or `48-EXPECTED-STRUCTURE.md` specifies -- all three fixes repair test EXTRACTION logic to correctly locate the same underlying guarantees (marker separator, ordinal, target) against the new guarded byte shape. No scope creep.

## Issues Encountered

None beyond the three deviations above.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- All three label-reference emission sites now route through `_label_existence_guard` (SC#2); a structural sweep in `tests/test_label_existence_guard_unit.py` confirms the guard's conditional construction appears exactly once across `typsphinx/*.py`.
- The D-05 captioned-code-block fatal is closed on its committed pre-fix RED; the D-04 site (`visit_pending_xref`) is guarded as defence in depth with its unreachability finding recorded in code.
- The D-06 exemption (the two same-document `visit_reference` branches stay unguarded) is now asserted by an explicit negative test, not merely observed.
- `uv run pytest -m "not slow" -q` is green: 1017 passed, 0 failed, 0 xfailed, 0 XPASS.
- `uv run black --check .` and `uv run mypy typsphinx/` both pass locally. `ruff check .` could not be run locally (the NixOS-unrunnable-generic-linux-ELF limitation recorded in `PROJECT.md`'s Deferred Items, `ruff-generic-linux-elf-unrunnable-on-nixos`) -- CI carries ruff's lint authority per that documented deferral.
- Plan 48-04 (the final wave) can proceed: it inherits three guarded sites, a proven helper contract, and the accepted label-collision false-negative characterized by `tests/fixtures/xref_label_collision_guard_gate/` -- ready for the performance-tier measurement against the recorded 28.93s/28.56s baseline (T-48-02) and any remaining phase-level cleanup.

---
*Phase: 48-compile-time-cross-reference-guard*
*Completed: 2026-08-12*

## Self-Check: PASSED

All 6 claimed files confirmed present on disk (`typsphinx/translator.py`, `tests/test_citation_caption_dangling_label_gate.py`, `tests/test_citation_degradation_gate.py`, `tests/test_citation_render_gate.py`, `tests/test_translator.py`, `tests/test_label_existence_guard_unit.py`, this SUMMARY.md). All 3 commit hashes (`91c5c91`, `7981949`, `965b9a9`) confirmed present in `git log`.

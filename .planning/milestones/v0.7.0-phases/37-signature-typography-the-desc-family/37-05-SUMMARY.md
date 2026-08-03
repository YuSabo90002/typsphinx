---
phase: 37-signature-typography-the-desc-family
plan: 05
subsystem: rendering
tags: [typst, translator, desc, parbreak, sig-08]

# Dependency graph
requires:
  - phase: 37-signature-typography-the-desc-family (plan 02, Wave 1)
    provides: "tests/test_signature_break_and_arrow_gate.py -- the 9-assertion gate module (2 SIG-08 RED, 2 SIG-08 CONTROL-GREEN) this plan flips, plus the FID-06 sibling control at tests/test_desc_bodyless_concat_render_gate.py"
provides:
  - "typsphinx/translator.py: TypstTranslator._desc_break_marker, an emission-position marker (instance attribute, initialised None in __init__) that lets depart_desc suppress its own parbreak() when nothing has been emitted since the immediately preceding desc's own parbreak()"
  - "depart_desc rewritten per 37-EMISSION-CONTRACT.md section 8: a nested desc no longer emits a doubled parbreak() with its parent, at any nesting depth, while a nested member followed by more parent-body content still gets its separating break"
  - "D-12's resolution (the two break mechanisms -- depart_desc's paragraph break and visit_desc_signature's FID-03 sibling linebreak() -- stay distinct) restated in depart_desc's docstring, not left in planning"
affects: ["37-07 (Wave 4, lands the D-10 wrapper change on top of this fix -- must prove the wrapper does not disturb the SIG-08 gate)", "37-08 (merges the four sibling 37-GATE-EVIDENCE-*.md files; this plan's node-id set-difference evidence lives in this SUMMARY, not a separate evidence file per this plan's own instructions)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Emission-position marker idiom (mirrors the existing _is_first_desc_signature scalar-flag idiom): record len(self.body) immediately after a conditional emission, then compare against the CURRENT len(self.body) at the next candidate emission site to decide whether anything was appended in between. Deliberately not a depth counter -- the discriminator is 'was anything emitted since', not 'how deep am I', which is why it correctly distinguishes 'a nested member is the last thing in its parent's body' (suppress) from 'a nested member is followed by more parent-body content' (do not suppress)."

key-files:
  created: []
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Followed 37-EMISSION-CONTRACT.md section 8's marker shape exactly: `self._desc_break_marker: int | None = None` in __init__, compared via `self._desc_break_marker == len(self.body)` in depart_desc, updated only on the non-suppressed path (the early return does NOT update the marker) so N levels of desc nesting still yield exactly one parbreak() rather than one per pair."
  - "Used `self.in_table` directly (already unconditionally initialised in __init__ at instance-construction time) rather than the contract snippet's illustrative `getattr(self, \"in_table\", False)` -- the getattr form exists for readers who haven't seen __init__; inside the class itself the attribute is always present, so the plain form is clearer and functionally identical."
  - "Restated D-12's resolution (the paragraph-break mechanism in depart_desc and the FID-03 sibling linebreak() mechanism in visit_desc_signature solve different problems and deliberately do not converge) in the depart_desc docstring itself, per the plan's must_haves, rather than only in this SUMMARY or in planning docs."

patterns-established:
  - "Emission-position marker for break suppression: reusable whenever a later fix needs to detect 'has anything been written to self.body since a prior break was emitted' without introducing a stateful depth counter that would conflate 'this nested element was the parent's last child' with 'this nested element was followed by more content'."

requirements-completed: [SIG-08]

# Coverage metadata
coverage:
  - id: D1
    description: "depart_desc suppresses its own parbreak() for a nested desc when nothing has been emitted since the previous desc's break, fixing the doubled parbreak() defect at any nesting depth"
    requirement: "SIG-08"
    verification:
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix"
        status: pass
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_no_adjacent_break_statements_anywhere"
        status: pass
    human_judgment: false
  - id: D2
    description: "A nested member followed by more parent-body content still keeps its separating break (the depth-counter trap this fix must avoid)"
    requirement: "SIG-08"
    verification:
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_content_follows_nested_member_stays_separated"
        status: pass
    human_judgment: false
  - id: D3
    description: "Sibling body-less desc nodes (the FID-06 control) keep exactly one break between them, unaffected by the SIG-08 suppression logic"
    verification:
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_sibling_bodyless_control_keeps_one_break"
        status: pass
      - kind: integration
        ref: "tests/test_desc_bodyless_concat_render_gate.py::TestDescBodylessConcatRenderGate::test_typstpdf_bodyless_desc_siblings_get_parbreak_and_produce_pdf"
        status: pass
    human_judgment: false

# Metrics
duration: ~8min
completed: 2026-08-01
status: complete
---

# Phase 37 Plan 05: SIG-08 Nested-Desc Break Suppression Summary

**`depart_desc` now suppresses its own duplicate `parbreak()` for a nested `desc` via an emission-position marker (`self._desc_break_marker`), fixing the doubled-blank-line defect from a `py:method::` inside a `py:class::` at any nesting depth, while a nested member followed by more parent-body content keeps its separating break — the depth-counter trap this fix deliberately avoids.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-08-01T05:21:17Z
- **Completed:** 2026-08-01T05:29:09Z
- **Tasks:** 2 (both `type="auto"`; Task 2 is evidence-recording only, no code change)
- **Files modified:** 1 (`typsphinx/translator.py`)

## Accomplishments

- Added `self._desc_break_marker` (instance attribute, `int | None`, initialised `None` in `__init__` alongside `self.in_literal_block`) recording `len(self.body)` immediately after a `desc`'s own `parbreak()` is emitted.
- Rewrote `depart_desc` per `37-EMISSION-CONTRACT.md` section 8: returns early (without emitting and without updating the marker) when `not self.in_table` and the marker equals the current `len(self.body)` — i.e. nothing has been appended since the immediately preceding `desc`'s own break. Otherwise emits `parbreak()` via the existing `_emit_forced_break` helper (unchanged) and records the new marker.
- Restated D-12's resolution in `depart_desc`'s docstring: the paragraph-break mechanism here and the FID-03 sibling `linebreak()` mechanism in `visit_desc_signature` solve different problems (separating one desc block from the next vs. separating signature lines within one block) and deliberately do not converge — plus an explicit paragraph explaining why a desc-nesting-depth counter is the wrong discriminator.
- Flipped exactly the 2 named SIG-08 node ids RED→GREEN: `test_sig08_exact_break_count_after_fix` and `test_sig08_no_adjacent_break_statements_anywhere`.
- Verified by node-id set difference (not count) that the whole-suite delta matches the Wave 1 baseline exactly minus those 2 node ids — see "Set-Difference Verification" below.
- Verified via a targeted emission diff that the fix changes exactly one line (a removed `parbreak()`) in the SIG-08 fixture and zero bytes in the FID-06 sibling control fixture and the Phase 36 golden fixture.

## Task Commits

1. **Task 1: Suppress depart_desc's duplicate break with an emission-position marker** - `ebf7e18` (fix)

Task 2 ("Prove the change is scoped and record the set-difference evidence") produced no code change — its output is the verification evidence recorded in this SUMMARY, per the plan's own instruction ("record the evidence in the plan SUMMARY, not in a new evidence file").

**Plan metadata:** commit pending (this SUMMARY + REQUIREMENTS.md, made immediately after this file is written)

## Files Created/Modified

- `typsphinx/translator.py` - Added `self._desc_break_marker` to `__init__`; rewrote `depart_desc` to suppress its duplicate `parbreak()` for nested `desc` nodes via the emission-position marker, guarded by `not self.in_table`; docstring restates D-12's resolution and the depth-counter rejection.

## Decisions Made

- See `key-decisions` in frontmatter. No decisions deviated from the plan or the emission contract; the implementation follows `37-EMISSION-CONTRACT.md` section 8's code sample verbatim in logic (with the `getattr` reader-aid simplified to a direct attribute access, since `in_table` is unconditionally initialised in `__init__`).

## Deviations from Plan

None - plan executed exactly as written. Scope fence honored: only `typsphinx/translator.py` (`__init__` and `depart_desc`) was touched; no test file or fixture was modified; `visit_desc_signature`'s FID-03 sibling `linebreak()` and `visit_desc_content`/`depart_desc_content` (both still `pass`) were not touched; no desc-nesting-depth counter was implemented.

## Set-Difference Verification

### SIG-08 gate module, before/after (by node id)

| Node id | Before this commit | After this commit |
|---|---|---|
| `TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix` | FAILED | **PASSED** |
| `TestSigBreakStructuralGate::test_sig08_no_adjacent_break_statements_anywhere` | FAILED | **PASSED** |
| `TestSigBreakStructuralGate::test_sig08_content_follows_nested_member_stays_separated` | PASSED (control) | PASSED (control) |
| `TestSigBreakStructuralGate::test_sig08_sibling_bodyless_control_keeps_one_break` | PASSED (control) | PASSED (control) |
| `TestDescBodylessConcatRenderGate::test_typstpdf_bodyless_desc_siblings_get_parbreak_and_produce_pdf` (FID-06 control) | PASSED | PASSED |
| `test_translator.py::test_desc_signature_line_multiline_emits_one_linebreak` (conditional control, GATE-EVIDENCE-04) | PASSED | PASSED |
| `test_translator.py::test_desc_signature_line_single_line_emits_no_linebreak` (conditional control) | PASSED | PASSED |
| `test_translator.py::test_desc_signature_line_resets_per_signature` (conditional control) | PASSED | PASSED |

### Whole-suite delta (`uv run pytest -q --tb=no -rf`), by node-id set difference against the Wave 1 baseline

Wave 1 baseline (33 RED node ids, reconstructed from `37-GATE-EVIDENCE-01.md` through `37-GATE-EVIDENCE-04.md`, 14 + 5 + 4 + 10 = 33) vs. this commit's failing set (31 node ids), compared with `comm`:

- **In baseline but NOT in this commit's failures (must be exactly the 2 SIG-08 ids):**
  ```
  tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix
  tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_no_adjacent_break_statements_anywhere
  ```
  Confirmed: exactly these 2, nothing else.
- **In this commit's failures but NOT in baseline (must be empty):** empty — confirmed via `comm -13`, zero lines.
- Overall suite result (`uv run pytest -q --tb=no`, full suite, no `-m` filter — matching the format the Wave 1 baseline ("33 failed, 653 passed, 1 skipped") was itself measured in): **`31 failed, 655 passed, 1 skipped in 69.49s`** — exactly the required end state.

No node id flipped in the unexpected direction (no unrelated test regressed, no already-RED test coincidentally flipped GREEN by this change).

### Lint/type trio

```
uv run black --check .   -> All done! 183 files would be left unchanged.
uv run ruff check .      -> All checks passed!
uv run mypy typsphinx/   -> Success: no issues found in 6 source files
```

### Targeted emission diff

Rebuilt `tests/fixtures/signature_break_and_arrow_gate/` and `tests/fixtures/desc_bodyless_concat_render_gate/` through `-b typst` at the parent commit (translator.py reverted via `git checkout -- typsphinx/translator.py`, then this commit's diff re-applied via `git apply`) and at this commit.

**`signature_break_and_arrow_gate` diff** (parent vs. this commit):
```
45d44
< parbreak()
```
Exactly one removed line, the duplicate `parbreak()` — matches the plan's required shape (one adjacent-break defect removed, nothing else).

**`desc_bodyless_concat_render_gate` diff** (the FID-06 sibling control): **empty** — byte-identical, confirmed via `diff` exit code 0.

**Phase 36 golden fixture** (`tests/fixtures/desc_rubric_decoupling_render_gate/`): also rebuilt at both commits directly (not just inferred from the gate's failure staying constant) — **empty diff**, byte-identical. `test_emitted_typ_is_byte_identical_to_golden` remains failing before and after this commit (it is in the intersection of the baseline-33 and after-31 failing sets), and this direct rebuild confirms the reason is unrelated to this commit: the fixture contains no nested `desc` (only two `py:function::` siblings, no `py:class::`/`py:method::` nesting), so `depart_desc`'s SIG-08 branch is never exercised there — the failure is purely the pending Wave 3/4 wrapper and monospace migration.

### Scope fence confirmation

`git diff typsphinx/translator.py` (captured before commit) touches only two regions: the `__init__` addition of `self._desc_break_marker`, and `depart_desc`'s body/docstring. No change to `visit_desc_signature`, `visit_desc_content`, `depart_desc_content`, or `_emit_forced_break`.

## Issues Encountered

- **Worktree environment provisioning (NixOS sandbox):** the worktree's fresh `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` installed generic-linux ELF `uv`/`ruff` (confirmed via `file`, no NixOS-compatible dynamic linker). Resolved by symlinking the main checkout's already-patched `uv`/`ruff` binaries (identical build IDs, confirmed via `file`) into the worktree's `.venv/bin/`, per the documented NixOS-sandbox pattern (also hit and resolved identically by 37-02). No project file was changed; pure environment setup.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 37-07 (Wave 4) can proceed to land the D-10 wrapper change on top of this fix — the SIG-08 gate's 2 RED assertions are now green and its 2 CONTROL assertions plus the FID-06 sibling control stay green, so 37-07's own verification only needs to prove the wrapper does not disturb this already-fixed break bookkeeping (the sequencing this plan exists to enable, per D-12's sequencing resolution).
- `REQUIREMENTS.md`'s SIG-08 checkbox and traceability row are marked complete (`requirements mark-complete SIG-08`) — this plan is the actual fix, unlike 37-02's RED-establishment-only plan which deliberately left it unchecked.
- No blockers. The 3 remaining SIG-06/D-11 REDs in `tests/test_signature_break_and_arrow_gate.py` and the 28 other pre-existing REDs from plans 37-01/03/04 are explicitly out of scope for this plan and untouched.

## Self-Check: PASSED

- `typsphinx/translator.py` - FOUND, contains `_desc_break_marker` and the rewritten `depart_desc`
- Commit `ebf7e18` (Task 1) - FOUND in `git log`
- `.planning/phases/37-signature-typography-the-desc-family/37-05-SUMMARY.md` - FOUND (this file)

---
*Phase: 37-signature-typography-the-desc-family*
*Completed: 2026-08-01*

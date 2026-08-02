---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 10
subsystem: docs
tags: [planning-docs, gap-closure, requirements-md, roadmap-md, context-md]

# Dependency graph
requires:
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 08)
    provides: the shipped, verified red-family-folded implementation (D-03) that UAT gap G-39-1
      falsifies
provides:
  - "39-CONTEXT.md: D-03 marked superseded in place; a new dated `D-03-R` reversal section with
    the owner's verbatim quotes, English renderings, and a measured red-family table"
  - "REQUIREMENTS.md: ADM-02 restated around intent (additive, dated), ADM-01's preamble annotated
    with the red-group sub-division note"
  - "ROADMAP.md: Phase 39 SC#1 amended in place (D-12/SC#3 pattern), a new 'Roadmap Evolution'
    section created and given its first ROADMAP.md-native entry"
affects: [39-11-implement-danger-memo-routing, 39-12-adm04-retaken-signoff, 39-13-gap-closeout]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Additive-only documentation reversal: original text stays byte-for-byte, gains a
      superseded pointer, followed by a dated replacement section — never an in-place overwrite"

key-files:
  created: []
  modified:
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-CONTEXT.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "Followed the plan's D-03-R content exactly: danger -> gentle-clues `danger` id, attention ->
    `memo` id, error unchanged; D-01 (bucket = function name, never colour) explicitly not reversed"
  - "Corrected 39-UAT.md's claim that gentle-clues' `memo` id has no Japanese lang.toml entry —
    measured `[lang.ja] memo = \"覚える\"` at line 168 of the installed lang.toml — and recorded the
    correct value in 39-CONTEXT.md rather than repeating the UAT's error"
  - "ROADMAP.md had no 'Roadmap Evolution' section (only STATE.md's mirror did); created one
    ROADMAP.md-native, following STATE.md's established one-bullet-per-amendment format, since the
    plan's Task 3 explicitly requires 'a bullet added to the Roadmap Evolution list' in ROADMAP.md"

patterns-established: []

requirements-completed: []  # No checkbox flip by design — this plan records the reversal only;
                            # ADM-01/ADM-02 stay checked, and closing them again is plan 39-13's
                            # judgement against delivered evidence, per the plan's own prohibitions.

coverage:
  - id: D1
    description: "D-03 marked superseded in 39-CONTEXT.md (with a pointer naming the reversal
      section) without deleting its original text; a new dated 'Reversal — recorded 2026-08-02
      (gap G-39-1)' section records decision D-03-R, the owner's three verbatim Japanese messages
      with accurate English renderings, a three-row red-family table (function id, measured
      accent, measured icon, requirement served) read directly from the installed gentle-clues
      theme.typ, and what the reversal does NOT touch."
    requirement: "ADM-02"
    verification:
      - kind: other
        ref: "grep -c 'D-03-R' 39-CONTEXT.md >= 2; grep -c 'D-03: .danger. folds into .error. too' == 1; grep -c '2026-08-02' increased; awk bold-title-closes-on-one-line check exit 0; git diff --numstat shows only the one accounted-for caption-line replacement"
        status: pass
    human_judgment: false
  - id: D2
    description: "ADM-02 restated around intent (attention leaves the orange warning group for the
      red family; not required to be the same function as danger/error) as an additive, dated
      sub-bullet under the unchanged, still-checked original ADM-02 bullet; ADM-01's preamble gets
      a dated note that the red group is deliberately sub-divided while the other three groups
      stay one function each. Zero deletions in the file."
    requirement: "ADM-02"
    verification:
      - kind: other
        ref: "grep -c 'G-39-1' REQUIREMENTS.md == 2; grep -c 'the same bucket as .danger./.error. (red)' == 1; grep -c 'four colour groups, not ten independent styles' == 1; grep -c '^- \\[x\\] \\*\\*ADM-0' == 6; git diff --numstat -- REQUIREMENTS.md reports 0 deletions"
        status: pass
    human_judgment: false
  - id: D3
    description: "ROADMAP.md's Phase 39 SC#1 amended in place with a bolded, dated correction
      naming D-03-R and G-39-1, following the exact in-place pattern SC#3 already uses for its
      D-12 correction; a new 'Roadmap Evolution' section is created (did not exist before) and
      given its first ROADMAP.md-native bullet recording the amendment. The eight shipped plan
      entries, the five new gap-closure entries, and every other phase heading are untouched."
    requirement: "ADM-01"
    verification:
      - kind: other
        ref: "grep -c 'G-39-1' ROADMAP.md == 5; grep -c '^- \\[x\\] 39-0[1-8]-PLAN.md' == 8; grep -c '^- \\[ \\] 39-09-PLAN.md|39-1[0-3]-PLAN.md' == 5; git diff -- ROADMAP.md | grep -c '^[-+]### Phase' == 0; git diff --numstat reports 1 deletion (the SC#1 line replaced by its amended form, as the plan explicitly allows)"
        status: pass
    human_judgment: false

# Metrics
duration: ~20min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 10: Record the D-03 Reversal (Gap G-39-1) Summary

**Additively records the owner's D-03 reversal — the red admonition family stops being one
collapsed `error()` call and becomes three distinct clue functions — across `39-CONTEXT.md`,
`REQUIREMENTS.md`, and `ROADMAP.md`, with every original sentence preserved verbatim.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-02T14:15:00+09:00 (approx.)
- **Completed:** 2026-08-02T14:32:00+09:00 (approx.)
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- `39-CONTEXT.md`'s D-03 bullet and the "Resulting bucket table" caption each gain a superseded
  pointer (original text untouched) to a new dated "Reversal — recorded 2026-08-02 (gap G-39-1)"
  section, which records decision **D-03-R**, the owner's three verbatim Japanese messages with
  accurate English renderings, and a measured three-row red-family table (`danger`→`danger`,
  `attention`→`memo`, `error`→`error`) read directly from the installed gentle-clues `theme.typ`.
- Corrected, in the same section, 39-UAT.md's `measured_context` claim that the `memo` id has no
  Japanese `lang.toml` entry — the installed file does carry `[lang.ja] memo = "覚える"` (line 168)
  — while noting this changes nothing functionally, since D-04/D-05's `custom_title` path already
  overrides every predefined title.
- `REQUIREMENTS.md`'s ADM-02 keeps its original bullet and checked state, and gains a dated,
  additive sub-bullet restating the requirement around intent (`attention` leaves the orange
  warning group for the **red family**, without requiring it to be the same function as
  `danger`/`error`); the ADM preamble gains a matching dated note that the red group is
  deliberately sub-divided while note/success/warning stay one function each. Zero deletions.
- `ROADMAP.md`'s Phase 39 SC#1 is amended in place with a bolded, dated correction following the
  exact pattern SC#3 already uses for its D-12 correction; a **new** "Roadmap Evolution" section
  (previously only mirrored in STATE.md, absent from ROADMAP.md itself) is created and given its
  first native entry recording the amendment.

## Task Commits

1. **Task 1: Record D-03's reversal in 39-CONTEXT.md without erasing D-03** - `7c8cfb9` (docs)
2. **Task 2: Restate ADM-02 around intent and note the red group's sub-division under ADM-01** - `43cfec4` (docs)
3. **Task 3: Amend ROADMAP.md's Phase 39 SC#1 and record the amendment in Roadmap Evolution** - `03f79f7` (docs)

**Plan metadata:** committed together with this SUMMARY (see final commit below; `commit_docs`
handling per the worktree carve-out — STATE.md is intentionally excluded from this plan's scope).

_Note: this is a documentation-only plan; no TDD red/green cycle applies._

## Files Created/Modified

- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-CONTEXT.md` - D-03 marked superseded
  in place; new dated `D-03-R` reversal section added at the end of the `<decisions>` block
- `.planning/REQUIREMENTS.md` - ADM-02 restated around intent (additive sub-bullet); ADM preamble
  gets a dated red-group sub-division note
- `.planning/ROADMAP.md` - Phase 39 SC#1 amended in place; new "Roadmap Evolution" section created
  with its first entry

## Decisions Made

- Quoted the owner's three verbatim Japanese UAT messages (from `39-UAT.md`'s `reason` field) with
  accurate, nuance-preserving English renderings, following the discipline `39-ADM04-SIGNOFF.md`
  §4 already established in this phase for a recorded owner verdict.
- Measured the red-family table's accent colours and icon filenames directly from the installed
  `~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/theme.typ` rather than transcribing them
  from `39-UAT.md`, per the task's `read_first` instruction.
- Re-measured the `@preview` import sites (`writer.py:158`, `template_engine.py:615`,
  `templates/base.typ:19`) to confirm all three still use the wildcard form — no pin move, no
  `test_preview_version_sync.py` impact — rather than trusting the UAT's prior "CHECKED" note
  without re-verifying.
- Created a "Roadmap Evolution" section in `ROADMAP.md` itself (it did not exist there before —
  only STATE.md carried a section by that name). This is a Rule 2 auto-add: the plan's Task 3
  explicitly instructs adding "a bullet to the Roadmap Evolution list" in `.planning/ROADMAP.md`,
  and no such list existed to append to. The new section follows STATE.md's established
  one-bullet-per-amendment format so the two files stay stylistically consistent.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing structure] Created ROADMAP.md's "Roadmap Evolution" section**
- **Found during:** Task 3 (amending ROADMAP.md's SC#1)
- **Issue:** The plan's Task 3 instructs "Add a bullet to the Roadmap Evolution list recording the
  amendment" inside `.planning/ROADMAP.md`, and names it as an established pattern ("the ROADMAP's
  own bullet list"). No `## Roadmap Evolution` heading or list exists anywhere in `ROADMAP.md` —
  only `STATE.md` carries a section by that name (with entries dated back to 2026-07-28).
- **Fix:** Created a new `## Roadmap Evolution` heading in `ROADMAP.md` (placed between the
  Progress table and the Backlog section), with a short preamble noting it is new as of
  2026-08-02, and gave it its first entry recording this plan's SC#1 amendment in the same
  one-bullet-per-amendment style STATE.md already uses.
- **Files modified:** `.planning/ROADMAP.md`
- **Verification:** `grep -c 'G-39-1' ROADMAP.md` returns 5 (Wave 5 heading, SC#1 correction, and
  the new Roadmap Evolution bullet, several of which mention it twice); no other phase heading or
  plan-list line changed (`git diff | grep -c '^[-+]### Phase'` = 0; plan-list diff = 0).
- **Committed in:** `03f79f7` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 — missing structure the plan's own instruction depends on).
**Impact on plan:** Necessary to fulfil Task 3's explicit instruction; no scope creep — only the
one new heading plus its one bullet were added, and every other line in the Progress/Backlog
region is untouched.

## Issues Encountered

- Two rounds of self-correction on `REQUIREMENTS.md`'s ADM-02 amendment: the first draft
  accidentally (a) repeated the literal phrase `the same bucket as `danger`/`error` (red)` inside
  the amendment text, which would have made the acceptance criterion `grep -c '...' == 1` fail
  because the original sentence appeared twice, and (b) split the words "red family" across a line
  wrap, breaking the `grep -c 'red family'` check. Both were caught immediately by running the
  plan's own acceptance-criteria commands before committing, and fixed by paraphrasing the
  amendment to reference "the parenthetical bucket-identity clause above" instead of re-quoting it,
  and by keeping "red family" on a single unwrapped line. Verified green afterward.

## User Setup Required

None - no external service configuration required.

## Verification

All three tasks' acceptance criteria and `<verify>` automated checks were run directly and pass:

- `39-CONTEXT.md`: `D-03-R` count 3, original D-03 sentence count 1, `2026-08-02` count 8, the
  bold-title awk check exits 0, and the only line-level deletion in the file's diff is the
  "Resulting bucket table" caption being replaced by its superseded form (accounted for above).
- `REQUIREMENTS.md`: `G-39-1` count 2, original ADM-02 sentence count 1, original preamble count 1,
  checked-ADM-bullet count 6 (unchanged), `git diff --numstat` reports 0 deletions, `red family`
  count 1, `2026-08-02` count 2.
- `ROADMAP.md`: `G-39-1` count 5, the eight shipped plan entries and five new unchecked
  gap-closure entries all present and correctly counted, no `### Phase` heading changed in the
  diff, and the diff's single deletion is the SC#1 line replaced by its amended form (the plan's
  own acceptance criterion names this as the expected, sole deletion).
- `git diff --stat -- typsphinx/ tests/` is empty across this plan's three commits (`7c8cfb9`,
  `43cfec4`, `03f79f7`) — confirmed directly against the pre-plan HEAD (`7272bd6`).
- `uv run pytest -m "not slow" -q` (after per-worktree `uv sync --extra dev` + the NixOS `uv` shim,
  per this project's standing worktree-isolation requirement): **735 passed, 29 deselected, 0
  failed** — the same zero-failure state the pre-plan baseline was in (this plan touches no file
  under `typsphinx/` or `tests/`, so no behavioural change is possible; the empty source/test diff
  above is the stronger, structural proof of that). Plan 39-09 runs in a sibling worktree this wave
  and its own failure-set baseline was not directly observable from here; this plan's own zero
  test-file diff is the evidence that it introduces no regression regardless of that baseline.

## Next Phase Readiness

- `39-CONTEXT.md`'s `D-03-R`, `REQUIREMENTS.md`'s restated ADM-02, and `ROADMAP.md`'s amended SC#1
  are now the contract plan 39-11 implements (`visit_danger` → `"danger"`, `visit_attention` →
  `"memo"`).
- No requirement checkbox was flipped — ADM-01 and ADM-02 stay `[x]` — closing them again against
  the new routing is plan 39-13's judgement, not this plan's.
- No file under `typsphinx/` or `tests/` was touched; plan 39-09 (the sibling GATE-01 RED plan for
  this same gap, running in a parallel worktree) is unaffected by this plan's edits.

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*

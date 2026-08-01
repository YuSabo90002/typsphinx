---
phase: 36-shared-emission-seam-cleanup
plan: 01
subsystem: testing
tags: [pytest, ast, sphinx, typst, golden-file, gate-01]

# Dependency graph
requires: []
provides:
  - "SC#2 combined-construct fixture Sphinx project (tests/fixtures/desc_rubric_decoupling_render_gate/)"
  - "Pre-decoupling golden.typ, captured verbatim from the untouched translator (D-07)"
  - "tests/test_desc_rubric_decoupling_render_gate.py: SC#1 delegation gate (RED) + SC#2 byte-identity gate (GREEN) + compile-sanity leg"
  - "36-GATE-EVIDENCE.md: pre-decoupling baseline, RED capture, delegation census, pre-change full-suite + lint/type baseline"
affects: ["36-02-decoupling", "36-03-math02", "36-04-sweep-and-verdict"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Golden-file byte-identity assertion (new to this repo) as the RED substitute in place of a compile fatal, per v0.7.0 milestone invariant #4"
    - "ast.parse-based structural delegation-site assertion (new to this repo) instead of a compile-fatal or regex assertion"

key-files:
  created:
    - tests/fixtures/desc_rubric_decoupling_render_gate/conf.py
    - tests/fixtures/desc_rubric_decoupling_render_gate/index.rst
    - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
    - tests/test_desc_rubric_decoupling_render_gate.py
    - .planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md
  modified: []

key-decisions:
  - "Golden captured from commit b37ea40 (this plan's own Task 2 commit, before any decoupling edit exists) per D-07, with a build-twice determinism proof recorded before anything depends on the mechanism."
  - "SC#1's grep-equivalent uses ast.parse + attribute-call walking rather than a text grep, so it discriminates delegation calls (self.visit_strong(...)) from the four decoupled methods vs. the two retained literal_strong methods precisely, satisfying the over-reach guard 36-RESEARCH.md Pitfall 1 calls for."
  - "36-GATE-EVIDENCE.md is deliberately not named 36-VERIFICATION.md (that filename is reserved by the verify stage and overwritten wholesale)."

patterns-established:
  - "Pattern 1: golden.typ byte-identity fixtures for zero-behavior-change refactors — read committed golden.typ, compare via str equality against a fresh -b typst build, render a difflib.unified_diff on mismatch."
  - "Pattern 2: ast-based structural assertions over typsphinx/translator.py for RED substitutes that cannot be a compile fatal (v0.7.0 milestone invariant #4)."

requirements-completed: [ADM-06]

# Metrics
duration: ~20min
completed: 2026-08-01
status: complete
---

# Phase 36 Plan 01: Pre-Decoupling Baseline + SC#1/SC#2 Gate Summary

**SC#2 combined-construct fixture, pre-decoupling golden.typ, and an ast-based SC#1 delegation gate that fails RED against the unfixed translator (6 delegation sites, 2 must survive) — all captured before typsphinx/translator.py has a single decoupling edit.**

## Performance

- **Duration:** ~20 min (task work spans commit 73a19db at 09:16:03+09:00 through 61f4477 at 09:21:44+09:00, plus environment provisioning and research reading before the first commit)
- **Started:** 2026-08-01T00:06:00Z (approx, environment provisioning)
- **Completed:** 2026-08-01T00:22:08Z
- **Tasks:** 3
- **Files modified:** 5 (all new files; `typsphinx/` untouched throughout)

## Accomplishments

- Created `tests/fixtures/desc_rubric_decoupling_render_gate/` — a fixture Sphinx project combining a single `desc_signature` with an id anchor, sibling `desc_signature`s, plain `**bold**` markup (regression control), an autodoc-style `.. rubric:: Options` shape, a rubric carrying a propagated target inside a list item (the D-03 two-blank-line byte-identity hazard 36-RESEARCH.md measured), and a rubric at true end-of-document — all six constructs ROADMAP SC#2 names, in one file, builds cleanly under `-b typst`.
- Captured `golden.typ` verbatim from the untouched translator (D-07: before any decoupling edit exists), and proved the emission mechanism is sound with a build-twice-and-`cmp` determinism check (byte-identical, exit 0).
- Shipped `tests/test_desc_rubric_decoupling_render_gate.py` with three test methods: the SC#1 delegation assertion (ast-parses `typsphinx/translator.py`, asserts `visit_desc_signature`/`depart_desc_signature`/`visit_rubric`/`depart_rubric` no longer delegate to `visit_strong`/`depart_strong` while `visit_literal_strong`/`depart_literal_strong` still do, plus a dummy-node-literal exact-count check) — **fails RED today** with exactly the expected failure (`visit_desc_signature still delegates to ['visit_strong']`), not a collection error or skip; the SC#2 byte-identity assertion (GREEN); and a compile-sanity leg via real `typst.compile()` (GREEN).
- Created `36-GATE-EVIDENCE.md` recording the pre-decoupling baseline (commit SHA, determinism proof, the full golden.typ quoted verbatim), the verbatim SC#1 RED failure output, the 6-site delegation census with a disposition table (4 in-scope, 2 out-of-scope), and the pre-change full-suite baseline (`1 failed, 651 passed, 1 skipped` — the one failure being this plan's own intentional RED — plus the lint/type trio, all green).

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the SC#2 combined-construct fixture Sphinx project** - `73a19db` (test)
2. **Task 2: Capture the pre-decoupling golden and ship the SC#1 + SC#2 gate module** - `b37ea40` (test)
3. **Task 3: Create 36-GATE-EVIDENCE.md with the pre-decoupling baseline, the RED capture, and the pre-change full-suite baseline** - `61f4477` (docs)

_No TDD-per-task structure was used — this plan's own "test" commits ARE the deliverable (a permanent regression gate and its baseline evidence), not a red/green pair around production code, since `typsphinx/translator.py` is untouched throughout this plan by design (D-07)._

## Files Created/Modified

- `tests/fixtures/desc_rubric_decoupling_render_gate/conf.py` - Minimal Sphinx config making `index` a master document (`typst_documents`)
- `tests/fixtures/desc_rubric_decoupling_render_gate/index.rst` - The six-construct SC#2 fixture document (S1/S2/B1/R1/R2/R3)
- `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` - Verbatim pre-decoupling `-b typst` output, the permanent SC#2 regression asset
- `tests/test_desc_rubric_decoupling_render_gate.py` - SC#1 (ast-based delegation check, RED) + SC#2 (byte-identity, GREEN) + compile-sanity leg (GREEN)
- `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` - Baseline, RED capture, delegation census, pre-change full-suite + lint/type baseline (Plan 01's sections; Plans 02-04 append their own)

## Decisions Made

- Golden captured post-Task-2-commit (`b37ea40`), confirmed `typsphinx/` untouched at that commit before capture, matching D-07's requirement that the "before" state be recorded as a committed artifact before any decoupling edit exists.
- Used `ast.parse` + attribute-call walking for SC#1 rather than a plain text grep, so the assertion can precisely discriminate "delegates to `visit_strong`/`depart_strong`" per named method (needed for the over-reach guard: `visit_literal_strong`/`depart_literal_strong` must still delegate, and a naive grep for the dummy-node literal alone couldn't attribute occurrences to specific methods for that half of the assertion).
- `36-GATE-EVIDENCE.md`'s Task 3 census table marks `visit_literal_strong`/`depart_literal_strong` explicitly OUT OF SCOPE with a stated rationale, so a future reader doesn't mistake the expected post-decoupling count of 2 (not 0) for an incomplete fix.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Task 1's literal `<verify><automated>` grep command undercounts the required 3rd rubric directive**

- **Found during:** Task 1, verifying the fixture's rubric count
- **Issue:** The plan's own automated verify command is `grep -c '^\.\. rubric::' tests/fixtures/desc_rubric_decoupling_render_gate/index.rst` expecting `3`, anchored at column 0 with no leading-whitespace tolerance. R2 (the rubric carrying a propagated target inside a list item) MUST be indented 2 spaces to nest correctly inside the bullet list item per reStructuredText syntax — this is exactly what makes it reproduce the `in_list_item=True` hazard 36-RESEARCH.md measured; putting it at column 0 would move it outside the list item and defeat R2's entire purpose. The literal column-0-anchored grep therefore counts only 2 (`Options`, `Trailing Heading`), not 3.
- **Fix:** Verified the fixture is correct by construction (matches 36-RESEARCH.md's measured reproduction shape exactly, R2 indented at 2 spaces like the analog fixture) and confirmed via a corrected count (`grep -cE '^[[:space:]]*\.\. rubric::' ...` → `3`) and via a real `-b typst` build, which shows R2's rubric correctly nested inside `list({...})` and reproducing the two-blank-line hazard (`36-GATE-EVIDENCE.md`'s Golden pointer section, lines 66-82). Did not alter the fixture to satisfy the literal grep at the cost of breaking R2's construct.
- **Files modified:** None (no code changed; this is a verification-method note, not a fixture defect)
- **Verification:** Real `sphinx-build -b typst` output confirms all three `.. rubric::` directives are present and R2 reproduces the exact hazard shape 36-RESEARCH.md measured; the acceptance-criteria bullet ("contains exactly 3 lines beginning `.. rubric::`") is satisfied under any whitespace-tolerant count.
- **Committed in:** `73a19db` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug in the plan's own verify tooling, not in shipped code)
**Impact on plan:** No scope creep; the fixture matches the plan's construct specification exactly, and the discrepancy is confined to one literal shell command's whitespace-anchoring in the plan document, not a defect in any committed artifact.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 02 (the decoupling itself) has everything it needs: the fixture, the committed `golden.typ` to diff against, the RED gate to flip to GREEN, and `36-GATE-EVIDENCE.md`'s baseline section to append its own decoupling-diff section to.
- `typsphinx/translator.py` is confirmed untouched at every commit in this plan (`git status --porcelain typsphinx/` empty at all three commits) — Plan 02 starts from a clean, unmodified translator.
- No blockers. The one thing Plan 02 must NOT do (per D-01/D-03, reinforced by this plan's fixture and evidence): "clean up" the two/three-newline redundancy visible in the R2 construct's emission while copying `visit_rubric`'s body — that redundancy must be reproduced byte-for-byte, not fixed, or SC#2 fails.

---
*Phase: 36-shared-emission-seam-cleanup*
*Completed: 2026-08-01*

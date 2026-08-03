---
phase: 41-v0-7-0-release-automation-release-prep
plan: 06
subsystem: testing
tags: [git-diff-auditing, gate-01, milestone-invariants, changelog-cross-check, sc4]

# Dependency graph
requires:
  - phase: 41-01/41-02/41-03
    provides: the post-bump tree (v0.7.0, curated CHANGELOG `## [0.7.0]` entry) this plan measures against
  - phase: 40.1-citation-degradation-hardening
    provides: "40.1-NONREGRESSION.md Section 4's change-site-to-RED manifest, folded in verbatim with existence/SHA confirmation"
provides:
  - "41-SC4-INVARIANTS.md -- the SHA-anchored proof that ROADMAP SC#4's three milestone invariants hold, with every number transcribed from a command run in this worktree"
  - "a re-derived, node-name coverage map for all 51 changed translator handlers, with the 3 single-hit rows individually spot-checked against real assertions and a real doctree"
  - "confirmation that CHANGELOG's first two `### Verified` claims hold against measurement"
affects: [41-07, release-prep-close, gsd-complete-milestone]

# Tech tracking
tech-stack:
  added: []
  patterns: ["hunk-boundary + function-start-line census (git diff -U0 attribution, not AST)", "node-name-stripped grep for gate-module coverage (Pitfall 4)", "doctree node enumeration as a spot-check cross-check, not just grep"]

key-files:
  created:
    - .planning/phases/41-v0-7-0-release-automation-release-prep/41-SC4-INVARIANTS.md
  modified: []

key-decisions:
  - "Re-measured the SHA range live (merge-base main HEAD = 51e02b6, HEAD = aa9d2f0, 394 commits) rather than transcribing any of the three superseded counts (328/369/371) named in CONTEXT/RESEARCH."
  - "Reported the pillow dev-extra addition (Phase 39 D-07) as a transparency finding on Invariant 1 rather than silently folding it into an 'identical' verdict -- it is dev-only and does not weaken the CHANGELOG's runtime-dependency claim."
  - "Spot-checked all 3 single-hit handlers against real gate-module assertions AND a real doctree's node enumeration, not the grep hit alone -- all 3 COVERED."
  - "Explained (not silently absorbed) why Phase 40.1's change-site row 4 (deletion of _citing_reference_has_own_anchor) is invisible to two-endpoint hunk attribution: the function was born and died entirely inside the range."

patterns-established:
  - "SC#4-style invariant sweeps: re-measure the SHA range at execution time via git merge-base, never transcribe a planning-time count."
  - "Coverage-map spot-checks should cross-verify a grep hit against a real doctree's node enumeration when available, not just the gate module's prose."

requirements-completed: [REL-05]

coverage:
  - id: D1
    description: "Invariant 1 (zero new runtime dependencies) proven mechanically over the re-measured SHA range, with the dev-only pillow addition reported as a non-breaching finding"
    requirement: "REL-05"
    verification:
      - kind: other
        ref: "41-SC4-INVARIANTS.md 'Invariant 1 of 3' section -- git diff/show commands over pyproject.toml and uv.lock, transcribed verbatim"
        status: pass
    human_judgment: false
  - id: D2
    description: "Invariant 2 (@preview surface unchanged, no new sync site) proven mechanically, all three declaration sites plus the examples/ drift guard"
    requirement: "REL-05"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py -- test_preview_versions_identical_across_declaration_sites, test_all_four_packages_declared, test_example_templates_match_canonical_versions"
        status: pass
    human_judgment: false
  - id: D3
    description: "Invariant 3 (every changed node handler carries a recorded-RED GATE-01 fixture) -- 51-handler census, node-name coverage map, 3 single-hit rows spot-checked, Phase 40.1's manifest folded in with existence/SHA confirmation, D-12 classified as docstring-only"
    requirement: "REL-05"
    verification:
      - kind: other
        ref: "41-SC4-INVARIANTS.md 'Invariant 3 of 3' + 'Spot-check' + 'Phase 40.1 coverage' + 'This phase's own translator change' sections"
        status: pass
    human_judgment: false
  - id: D4
    description: "CHANGELOG's first two `### Verified` claims cross-checked against this sweep's measurement -- both hold"
    verification:
      - kind: other
        ref: "41-SC4-INVARIANTS.md 'Cross-check' section"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-08-03
status: complete
---

# Phase 41 Plan 06: SC#4 Milestone-Invariant Proof Summary

**Mechanically proved ROADMAP SC#4 over the SHA-anchored full milestone diff (394 commits,
re-measured live) — zero new runtime dependencies, the `@preview` surface unchanged, and all 51
changed node handlers censused and mapped to a covering gate module, with the 3 single-hit rows
individually spot-checked against real assertions and a real doctree, and Phase 40.1's citation-fix
RED manifest folded in with existence and SHA-resolution confirmation.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-03T11:30:00Z (approx.)
- **Completed:** 2026-08-03T11:47:56Z
- **Tasks:** 3
- **Files modified:** 1 (`41-SC4-INVARIANTS.md`, created)

## Accomplishments

- Re-measured the milestone SHA range live (`git merge-base main HEAD` = `51e02b6`, one commit past
  `v0.6.5`; HEAD = `aa9d2f0`; 394 commits — a fourth, newer value than the three already-superseded
  counts named in `41-CONTEXT.md`/`41-RESEARCH.md`), and confirmed Phase 40.1's three fix commits
  are ancestors of HEAD by SHA.
- Proved Invariant 1 (zero new runtime dependencies): the `dependencies` array and PEP 735
  `[dependency-groups]` table are byte-identical across the range; reported (not hidden) that the
  `dev` extra gained one pre-existing dev-only package (`pillow`, Phase 39 D-07) which does not
  weaken the runtime-dependency claim; confirmed no third-party version moved in `uv.lock`.
- Proved Invariant 2 (the `@preview` surface): all three declaration sites (`writer.py`,
  `template_engine.py`, `templates/base.typ`) are line-for-line identical between base and HEAD; no
  newly added file under `typsphinx/` or `examples/` introduces a new production sync site; the two
  genuine test-fixture mirrors both pin current versions; `test_preview_version_sync.py`'s three
  assertions pass.
- Re-derived the hunk-attributed handler census (51 handlers, byte-identical to
  `41-RESEARCH.md`'s recorded list despite the range moving from 369 to 394 commits — explained by
  name: D-12's docstring edit lands inside an already-touched function), built the node-name
  coverage map, and individually spot-checked all 3 single-hit handlers
  (`visit_desc_sig_keyword`/`punctuation`/`space`) against `test_desc_sig_space_render_gate.py`'s
  real assertions AND a real doctree's node enumeration — all 3 COVERED.
- Folded in `40.1-NONREGRESSION.md` §4's 4-row change-site-to-RED manifest with `test -f` /
  `git cat-file -e` confirmation of every named evidence file and RED commit SHA; explained why row
  4 (a function born-and-deleted entirely inside the range) is structurally invisible to
  two-endpoint hunk attribution without leaving a silent gap.
- Classified this phase's own `visit_desc_sig_name` docstring edit (D-12, commit `c81ca29`) as
  docstring-only with no GATE-01 obligation, reproducing the no-executable-line-moved proof from
  this session's own measurement.
- Cross-checked CHANGELOG's first two `### Verified` claims against this sweep — both hold.
- Closed with a per-invariant PROVEN verdict table and an executed-versus-skipped summary line for
  every command in the file.

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-measure the range, then prove the dependency and @preview invariants** -
   `204c58a` (docs)
2. **Task 2: Census every changed node handler and map each to its covering gate module** -
   `536601e` (docs)
3. **Task 3: Spot-check the single-hit mappings, fold in 40.1's RED manifest, and classify D-12** -
   `f45d261` (docs)

_Note: this plan writes exactly one markdown evidence file; there is no separate plan-metadata
commit distinct from Task 1/2/3's docs commits per this plan's own instruction that it "changes NO
source or test file. It measures."_

## Files Created/Modified

- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-SC4-INVARIANTS.md` - the SC#4
  evidence file: diff-range re-measurement, Invariant 1 (deps), Invariant 2 (`@preview`), CHANGELOG
  cross-check, Invariant 3 (handler census + coverage map + single-hit spot-checks), Phase 40.1
  fold-in, D-12 classification, and the closing verdict table.

## Decisions Made

- Re-measured the SHA range live rather than transcribing any planning-time count — the range's
  commit count (394) is a fourth, newer value than the three already-superseded counts on record
  (328/369/371), confirming `41-RESEARCH.md` Pitfall 3's own warning that this number is a moving
  target on an actively developed branch.
- Reported the `pillow` dev-extra addition (Phase 39 D-07) as an explicit transparency finding on
  Invariant 1 instead of smoothing it into a bare "identical" verdict — it is dev-only tooling for
  the ADM-04 greyscale-comparison script, predates this plan, and does not weaken the CHANGELOG's
  runtime-dependency claim, but the plan's own instructions require surfacing any dependency-group
  change rather than absorbing it silently.
- Spot-checked the 3 single-hit handlers against BOTH the gate module's real assertions AND a real
  built doctree's node enumeration (not grep alone) — this is a step beyond what the task strictly
  required, taken because the single-hit family (trivial-looking `desc_sig_*` pass-through
  handlers) is exactly the false-positive risk `41-RESEARCH.md`'s Open Question 2 flagged, and a
  doctree-level confirmation closes that risk more directly than assertion-text alone.
- Explained (rather than silently noted as absent) why Phase 40.1's change-site row 4 does not
  appear in the handler census or the non-handler-methods list: `_citing_reference_has_own_anchor`
  was created and deleted entirely within the `BASE..HEAD` range, so it exists in neither
  endpoint's function-start snapshot — a structural blind spot of two-endpoint hunk attribution,
  not a coverage gap (its caller's rewiring, `visit_reference`, is covered).

## Deviations from Plan

None — plan executed exactly as written. No auto-fixes were needed (Rules 1-3 did not fire): this
plan only reads git history and existing files and writes one markdown evidence file, taking no
irreversible action and changing no source, test, workflow, or CHANGELOG file.

## Issues Encountered

None. All commands ran to completion on the first attempt; no fix-attempt-limit issues arose.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC#4 is proven; all three milestone invariants hold with the `pillow` dev-extra addition and the
  `docs/` fourth `@preview` site both correctly classified as carried, non-breaching facts rather
  than new findings.
- No open SC#4 gap was recorded — all 51 handlers map to at least one gate module, and the 3
  single-hit handlers are individually confirmed COVERED.
- `git status --porcelain -- typsphinx tests scripts` is empty and `git status --porcelain`
  (repo-wide) shows only this plan's own evidence file — no census/spot-check tooling was
  committed anywhere.
- `git tag -l v0.7.0` and `git ls-remote --tags origin v0.7.0` are both empty — no irreversible
  release action was taken.
- Ready for whatever plan in this phase closes the wave / produces `41-HANDOFF.md` and the final
  release-prep evidence roll-up; this plan's SC#4 proof is a direct input to that closing plan's
  own claims.

---
*Phase: 41-v0-7-0-release-automation-release-prep*
*Completed: 2026-08-03*

---
phase: 57-v0-9-0-release-prep-prep-only
plan: 08
subsystem: release-prep
tags: [release-prep, verification, sc4, milestone-diff-sweep, fence-proof]

# Dependency graph
requires:
  - phase: 57-v0-9-0-release-prep-prep-only (plans 57-05, 57-06, 57-07)
    provides: "the post-bump authority CI green (57-05, resolved via 57-11 + fresh run
      32557477023), local green-tree evidence (57-06), and the goal-claim re-run (57-07),
      all of which this sweep re-verifies were achieved without breaking the milestone
      invariants or the prep-only fence"
  - phase: 57-v0-9-0-release-prep-prep-only (plan 57-11)
    provides: "the one owner-approved typsphinx/builder.py exception to the prep-only
      fence, and the AMENDED 2026-08-17 block in 57-CONTEXT.md that this plan reads
      before evaluating SC#4's fence clause"
provides:
  - "SC#4's whole discharge: the milestone-diff invariant sweep (dependency claim argued
    at hunk level with a real positive control, @preview guard live-falsified, config-value
    delta recorded and NOT carried forward), the phase-scoped fence proof accounting for
    exactly the one intended typsphinx/ exception, the second separated tag/release
    observation, and the REQUIREMENTS.md closeout-guard re-verification"
affects: [57-09, phase-verifier, release-v0.9.0]

# Actuals (#2632)
actuals:
  tokens: 5954
  tasks: 3
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hunk-level dependency-change argument backed by a real historical positive control
      (a genuine dependency-line change at a named prior commit), rather than an empty-diff
      proof, because pyproject.toml's package-data glob widened this milestone (BLD-05)"
    - "Live falsification of a version-lockstep guard (perturb one string, confirm RED,
      restore, confirm GREEN, confirm clean tree) to prove a green gate is load-bearing
      rather than merely currently-passing"

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-SC4-INVARIANTS.md
  modified: []

key-decisions:
  - "Read 57-CONTEXT.md's AMENDED 2026-08-17 block before evaluating the fence, per its
    explicit naming of this plan as an intended reader: SC#4's 'no unintended typsphinx/
    change' clause is satisfied because the ONLY typsphinx/ change in this phase's own
    diff is 57-11's owner-approved Windows repr()-escaping fix (typsphinx/builder.py),
    exactly the bounded exception the AMENDED block describes -- this is not a fence
    violation to flag."
  - "Re-measured every figure live rather than trusting 57-CONTEXT.md's or
    57-BUMP-EVIDENCE.md's earlier 2026-08-16 numbers, which have moved: commit count
    v0.8.0..HEAD is now 326 (was 270/277) and the .planning-excluded shortstat is now
    166 files/+11,627/-1,620 (was 163/+11,262/-1,615), because 49 more commits (57-05
    through 57-11) landed since those documents were written."
  - "Used origin/main / v0.8.0 anchor coincidence (both resolve to the identical commit,
    both give the identical shortstat) to confirm the adjacency edge case resolves cleanly
    this time, matching D-15's prediction rather than diverging from it."

requirements-completed: []

coverage:
  - id: D1
    description: "The milestone-diff sweep behind CHANGELOG's ### Verified block is
      re-argued live: no new runtime dependency (hunk-level, with a real positive control),
      @preview count and lockstep (live green/RED/green/clean falsification), and the
      full-corpus gate re-run pointer"
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_preview_version_sync.py -v (3 passed, then RED
          under deliberate perturbation naming mitex, then 3 passed again after restore)"
        status: pass
      - kind: other
        ref: "diff <(git show v0.8.0:pyproject.toml | sed -n dependency-range) <(sed -n
          dependency-range pyproject.toml) -- empty, exit 0; identical form across
          2ed64aa0^..2ed64aa0 -- non-empty, exit 1 (positive control fires)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The prep-only fence is proven over this phase's own diff (phase-start
      SHA 78bd595d..HEAD), accounting for the one intended 57-11 exception and no other
      typsphinx/ change"
    verification:
      - kind: other
        ref: "git diff 78bd595d344f46c6e1f5a18bce0e24da1f66a9ee..HEAD -- typsphinx/
          confined entirely to typsphinx/builder.py's three named 57-11 refusal sites"
        status: pass
    human_judgment: false
  - id: D3
    description: "Second separated tag/release observation and REQUIREMENTS.md
      closeout-guard re-verification"
    verification:
      - kind: other
        ref: "git tag -l v0.9.0 / git ls-remote --tags origin v0.9.0 / gh release list /
          gh run list --workflow=release.yml all show no v0.9.0 artifact; sha256sum
          .planning/REQUIREMENTS.md matches 57-CLOSEOUT-GUARD.md's baseline digest
          503efc7a...c17567d94 byte-for-byte; REL-08 checkbox and Traceability row
          re-quoted identical to the guarded lines"
        status: pass
    human_judgment: false

# Metrics
duration: 35min
completed: 2026-08-22
status: complete
---

# Phase 57 Plan 08: SC#4 Milestone-Diff Sweep and Fence Proof Summary

**Every figure behind CHANGELOG's published `### Verified` claims and Phase 57's prep-only fence was re-measured live this session, confirming the sweep holds and the fence's one intended exception (57-11's Windows fix) is correctly scoped and accounted for.**

## Performance

- **Duration:** 35 min
- **Completed:** 2026-08-22
- **Tasks:** 3 (all producing one artifact, committed atomically as one commit)
- **Files modified:** 1 (created)

## Accomplishments

- Confirmed the diff-anchor adjacency edge case resolves cleanly: `git merge-base origin/main HEAD`
  equals `git rev-parse origin/main` (both `aed773c9807ab871468b1b2a7e1ec36b54e82907`), and the two
  `.planning`-excluded shortstats are identical (166 files, +11,627/−1,620) — the choice of anchor
  is immaterial to every conclusion in the sweep.
- Argued the "no new runtime dependency" claim at hunk level: `pyproject.toml`'s whole milestone
  diff (quoted in full) touches only the `version` literal and the
  `[tool.setuptools.package-data]` glob, zero lines under `dependencies`; a targeted extraction
  diff is byte-identical (exit 0); a real historical positive control (commit `2ed64aa0`'s typst
  pin bump) proves the identical extraction form produces non-empty output when a dependency
  genuinely changes (exit 1) — the detector is discriminating, not vacuous.
- Live-falsified the `@preview` version-lockstep guard: perturbed one version string
  (`typsphinx/writer.py`'s mitex line `0.2.7` → `0.2.8`), confirmed
  `tests/test_preview_version_sync.py` turns RED naming the exact package and file, restored with
  `git checkout --`, confirmed green again, and confirmed `git status --porcelain` clean —
  proving the guard is load-bearing rather than merely currently green.
- Recorded the `typst_template_assets` → `typst_document_templates` config-value delta and
  explicitly stated Phase 52's "no new `typst_*` config value" assertion does not carry forward
  this milestone (the registry is this milestone's headline feature).
- Proved the prep-only fence over this phase's own diff (`78bd595d..HEAD`, the phase-start SHA
  quoted from `57-BUMP-EVIDENCE.md`): the only `typsphinx/` change is confined entirely to plan
  `57-11`'s three named refusal-message sites in `typsphinx/builder.py` — exactly the one
  owner-approved exception `57-CONTEXT.md`'s `AMENDED 2026-08-17` block records, which names this
  plan explicitly as a reader who must not flag it as a violation. Every other of the 8 changed
  paths in the phase's `--stat` listing was individually named and accounted for.
- Took the second of three separated tag/release fence observations
  (`2026-08-22T06:51:54Z`, ~6 days after plan 57-01's first): both `git tag -l v0.9.0` and
  `git ls-remote --tags origin v0.9.0` empty; `gh release list` shows `v0.8.0` as latest with no
  `v0.9.0` entry; `gh run list --workflow=release.yml` shows no run for `v0.9.0`.
- Re-verified the `REQUIREMENTS.md` closeout guard: `sha256sum` matches
  `57-CLOSEOUT-GUARD.md`'s baseline digest byte-for-byte, `git diff --name-only` is empty, and
  REL-08's checkbox line (128) and Traceability row (212) are byte-identical to the guarded
  quotes — the `phase.complete` auto-flip that has fired at four consecutive release-prep closes
  did **not** fire here.

## Task Commits

All three tasks produce the same single artifact (`57-SC4-INVARIANTS.md`), committed atomically as
one commit once all three tasks' data-gathering and writing were complete:

1. **Tasks 1-3 combined: sweep, fence proof, and write the SC#4 invariants record** -
   `2f4f744f` (docs)

**Plan metadata:** SUMMARY.md committed as part of this worktree's own commit above (worktree
mode — orchestrator merges and records final STATE.md/ROADMAP.md updates centrally).

## Files Created/Modified

- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-SC4-INVARIANTS.md` - Created: the full
  SC#4 discharge — anchor adjacency, the three `### Verified` claims re-argued live with real
  positive controls, the config-value delta recorded and retired, the phase-scoped fence proof,
  the second tag/release observation, and the REQUIREMENTS.md closeout-guard re-verification.

## Decisions Made

- Read `57-CONTEXT.md`'s `AMENDED 2026-08-17` block before evaluating the fence, exactly as its
  own text instructs this plan to do — SC#4's "no unintended `typsphinx/` change" clause is
  satisfied because the only `typsphinx/` change in this phase's own diff is plan 57-11's
  owner-approved Windows `repr()`-escaping fix, the bounded exception the AMENDED block names.
  This is not a fence violation.
- Re-measured every figure live rather than trusting the 2026-08-16 numbers recorded in
  `57-CONTEXT.md` or `57-BUMP-EVIDENCE.md`, which have moved: 49 more commits (57-05 through
  57-11) landed since those documents were written, moving the commit count from 270/277 to 326
  and the `.planning`-excluded shortstat from 163 files/+11,262/−1,615 to 166 files/+11,627/−1,620.
- Used the `v0.8.0`/`origin/main` anchor coincidence to confirm the adjacency edge case resolves
  cleanly this time, matching D-15's prediction.

## Deviations from Plan

None — plan executed exactly as written. All three tasks write to the same single file
(`57-SC4-INVARIANTS.md`), so they were committed together as one atomic commit representing the
complete discharge of SC#4, rather than as three separate partial commits to the same evolving
file.

## Issues Encountered

None. All commands ran cleanly in the provisioned worktree venv; no perturbation was left in
place; `git status --porcelain` was confirmed empty both mid-task (after the falsification
restore) and at the final commit.

## User Setup Required

None — no external service configuration required. No irreversible action was taken: `git tag -l
v0.9.0` and `git ls-remote --tags origin v0.9.0` both remain empty throughout.

## Next Phase Readiness

- SC#4 is fully discharged: the milestone-diff invariant sweep, the phase-scoped fence proof, the
  second tag/release observation, and the `REQUIREMENTS.md` checksum re-verification are all on
  disk in `57-SC4-INVARIANTS.md`.
- Plan `57-09` (SC#5 todo-ledger disposition and `57-HANDOFF.md`) is the phase's last remaining
  plan; it owns the third and final separated tag/release observation.
- The phase verifier should read `57-CONTEXT.md`'s `AMENDED 2026-08-17` block (as this plan did)
  before independently re-deriving the fence proof for the phase's close, to avoid the same false
  violation this plan was warned against.
- REL-08 remains `[ ]` / Pending in `.planning/REQUIREMENTS.md`, byte-identical to the
  `57-CLOSEOUT-GUARD.md` baseline; it closes at `/gsd-complete-milestone`, not in this phase.

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-22*

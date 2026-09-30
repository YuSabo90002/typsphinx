---
phase: 46-v0-7-1-release-prep-prep-only
plan: 05
subsystem: infra
tags: [release-engineering, ci, changelog, git, invariant-sweep]

# Dependency graph
requires:
  - phase: 46-v0-7-1-release-prep-prep-only (plans 46-02, 46-03)
    provides: the version bump (pyproject.toml/README/uv.lock to 0.7.1) and the curated `## [0.7.1]` CHANGELOG entry, both of which this plan's Task 2 exercises against
provides:
  - a mechanically-proven SC#4 milestone-invariant sweep, anchored at the v0.7.0 tag and re-measured on the post-merge HEAD
  - REL-04's two in-phase preconditions verified and transcribed (workflow file presence, extractor correctness), with the requirement's openness stated in writing
affects: [gsd-complete-milestone, any future phase reading 46-SC4-INVARIANTS.md or 46-REL04-EVIDENCE.md as precedent for the next milestone's own SC#4/REL-style sweep]

# Actuals (#2632)
actuals:
  tokens: 8024
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Milestone-invariant sweep anchored at the release tag (not the branch fork point), re-measured post-merge — D-21 pattern, reusable for future milestones' SC#4-style checks"
    - "Reference-point correction for git diff invariant checks under branching_strategy: milestone — origin/main is not a safe base for 'did this phase touch X' once the milestone branch has diverged for several phases; use the pre-phase-execution commit on the milestone branch itself instead"

key-files:
  created:
    - .planning/phases/46-v0-7-1-release-prep-prep-only/46-SC4-INVARIANTS.md
    - .planning/phases/46-v0-7-1-release-prep-prep-only/46-REL04-EVIDENCE.md
  modified: []

key-decisions:
  - "Invariant 3's plan-literal `git diff origin/main..HEAD -- typsphinx/` command is non-empty by construction under this project's milestone-branch strategy (origin/main lacks Phases 43-45.1's legitimate typsphinx/ work); the corrected reference point c72be91..HEAD (post-D-20-merge tip to HEAD) proves the actual intent — Phase 46 itself made zero typsphinx/ edits. Both the literal and corrected commands are recorded in the evidence file."

patterns-established:
  - "When a plan's verify command references a moving/wrong git ref, run the corrected command, document the discrepancy and reasoning fully in the evidence artifact (not just the SUMMARY), and treat it as a [Rule 1] deviation rather than silently substituting or silently failing."

requirements-completed: []  # Plan frontmatter names [REL-06, REL-04]; neither closes here.
  # REL-04's must_haves.truths explicitly forbids reporting it complete from this plan
  # (backstop truth: acceptance evidence is a real tag push, only /gsd-complete-milestone
  # generates it). REL-06 ("handed off") is not finished until plan 46-06's handoff doc.

coverage:
  - id: D1
    description: "SC#4 milestone-invariant sweep: zero new runtime dependencies, @preview count still four with no new lockstep site, and the Phase 46 prep-only fence over typsphinx/ — all three proven mechanically with commands and verbatim output in 46-SC4-INVARIANTS.md"
    verification:
      - kind: other
        ref: "diff of [project] dependencies array v0.7.0 vs HEAD (empty); uv run pytest tests/test_preview_version_sync.py -q --junit-xml (3 passed, failures=0, errors=0); git diff c72be91..HEAD --name-only -- typsphinx/ (empty, corrected reference point)"
        status: pass
    human_judgment: false
  - id: D2
    description: "REL-04 in-phase preconditions verified: release.yml's create-release job carries astral-sh/setup-uv + uv python install ahead of the extractor call and is unchanged this milestone; extract_changelog_section.py 0.7.1 is exercised for basic run, idempotency, empty-input failure mode, awk-independent adjacency, and ordering — all recorded in 46-REL04-EVIDENCE.md, with REL-04 explicitly stated as still open"
    verification:
      - kind: other
        ref: "uv run python scripts/extract_changelog_section.py 0.7.1 (exit 0, non-empty, byte-identical across two runs); uv run python scripts/extract_changelog_section.py 9.9.9 (exit 1, stderr message); independent awk extraction diff (byte-identical after accounting for print()'s trailing newline)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-11
status: complete
---

# Phase 46 Plan 05: SC#4 Invariant Sweep + REL-04 Precondition Evidence Summary

**Mechanically proved all three D-21-anchored milestone invariants (zero new runtime deps, `@preview` count still four, Phase 46's typsphinx/ prep-only fence) and exercised REL-04's two in-phase preconditions against the real `## [0.7.1]` CHANGELOG section, while explicitly recording REL-04 as still open pending a real tag push at `/gsd-complete-milestone`.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-11T03:58:00Z (approx.)
- **Completed:** 2026-08-11T04:33:22Z
- **Tasks:** 2
- **Files modified:** 2 (both new evidence files)

## Accomplishments
- Confirmed the `v0.7.0` tag anchor (`75fd8ed`, matching D-21 exactly) and rejected `87f242a` per D-21's stated reasoning, with both figures re-derived from live commands rather than transcribed from `46-CONTEXT.md`.
- Proved Invariant 1 (zero new runtime dependencies): the `[project] dependencies` array is byte-identical between `v0.7.0` and HEAD; the only `pyproject.toml` movement is the version literal plus two already-shipped, non-runtime `dev`/`docs`-extra changes (`tox-uv`→`tox-uv-bare` from Phase 45.2, `myst-parser>=5.0` from Phase 45).
- Proved Invariant 2 (`@preview` count still four): `tests/test_preview_version_sync.py` passes 3/3 with `failures="0"`/`errors="0"`; classified all 29 files in the repo-wide `@preview/` enumeration against the guard's documented sync surface, finding no new lockstep site beyond the already-known, already-deferred `docs/source/_typst/custom_template.typ`; confirmed PR #131's `builder.py` changes carry zero `@preview` references.
- Discovered and fully documented a genuine bug in the plan's own Invariant 3 verify command (`git diff origin/main..HEAD -- typsphinx/`), which is non-empty by construction under `branching_strategy: milestone` — origin/main doesn't contain Phases 43-45.1's legitimate typsphinx/ work. Derived and ran the semantically-correct reference point instead (`c72be91..HEAD`, the tip right after Phase 46's own D-20 merge), proving Phase 46 itself made zero typsphinx/ edits.
- Verified REL-04's Precondition 1 (release.yml's `create-release` job carries `astral-sh/setup-uv@v7` + `uv python install 3.12` ahead of the extractor call, transcribed verbatim, file unchanged since `origin/main`).
- Verified REL-04's Precondition 2 by exercising `scripts/extract_changelog_section.py` five ways against the real `## [0.7.1]` section: basic invocation (exit 0, non-empty), idempotency (two runs byte-identical, no side effects), empty-input failure mode (`9.9.9` exits 1 with a stderr message), an independent `awk` adjacency check (byte-identical to the script's own output, proving no leakage from `## [0.7.0]`/`## [Unreleased]`), and ordering (implied by the byte-identical diff, recorded explicitly per instruction).
- Recorded REL-04 as explicitly, plainly open in both evidence files' closing sections, naming `/gsd-complete-milestone` as the only place its acceptance evidence can be generated.
- Confirmed zero irreversible action throughout: `git tag -l v0.7.1` and `git ls-remote --tags origin v0.7.1` both empty before and after every command; the pending todo record and `REQUIREMENTS.md`'s REL-04 row are both untouched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Run the D-21 invariant sweep over the v0.7.0-anchored milestone diff** - `fce7fd6` (docs)
2. **Task 2: Discharge REL-04's in-phase preconditions and record that the requirement stays open** - `6f37991` (docs)

**Plan metadata:** committed via the worktree's standard SUMMARY+STATE flow (this plan runs in worktree-isolated mode; STATE.md/ROADMAP.md updates are owned by the orchestrator after wave completion, per this plan's own instructions).

## Files Created/Modified
- `.planning/phases/46-v0-7-1-release-prep-prep-only/46-SC4-INVARIANTS.md` - the D-21 invariant sweep transcripts (anchor, all three invariants, roll-up verdict)
- `.planning/phases/46-v0-7-1-release-prep-prep-only/46-REL04-EVIDENCE.md` - REL-04's two in-phase precondition transcripts and its explicit-open closing section

## Decisions Made
- **Invariant 3's git reference point was corrected from the plan's literal `origin/main..HEAD` to `c72be91..HEAD`** (the tip immediately after Phase 46's own D-20 merge commit). Rationale: this project's `branching_strategy` is `milestone` (`.planning/config.json`), so `origin/main` never sees any of a milestone's intermediate phases until the final publish — comparing `typsphinx/` against it necessarily surfaces the *whole milestone's* typsphinx work (Phases 43, 44, 44.1, 44.2, 45, 45.1), not Phase 46's own contribution, regardless of whether Phase 46 is prep-only. The corrected command isolates exactly what commits landed after the D-20 merge and proves it's empty. Both commands and full reasoning are recorded verbatim in `46-SC4-INVARIANTS.md`'s Invariant 3 section — nothing is silently substituted.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Invariant 3's verify command uses a git reference point that cannot express the intent it names**
- **Found during:** Task 1 (the D-21 invariant sweep)
- **Issue:** The plan's `<action>` and `<verify><automated>` both use `git diff origin/main..HEAD --name-only -- typsphinx/`, asserting it "must be empty" because "this phase changed no typsphinx/ file." Under this project's `branching_strategy: milestone`, `origin/main` has never seen any of Phases 43 through 45.1's legitimate `typsphinx/` work (TBL-04, TBL-05, FIG-01, CONF-08, BLD-01, TOC-01, CONF-09, CONF-10, CONF-11, CONF-12 all touch `typsphinx/`). The command therefore surfaces the whole milestone's `typsphinx/` diff (5 files: `__init__.py`, `builder.py`, `template_engine.py`, `translator.py`, `writer.py`) rather than Phase 46's own contribution, and cannot be empty by construction — independent of whether Phase 46 itself is prep-only.
- **Fix:** Derived the correct reference point for "did Phase 46 itself edit `typsphinx/`": `fa3bdc3` (the milestone branch's tip immediately before Phase 46's first execution commit) as the pre-phase baseline, and `c72be91` (plan 46-01's own merge-of-`origin/main` commit) as the point after which every remaining Phase 46 commit is Phase 46's own authorship. `git diff c72be91..HEAD --name-only -- typsphinx/` is empty — proving Phase 46 made zero `typsphinx/` edits of its own. The one file that differs between `fa3bdc3` and HEAD (`typsphinx/builder.py`) is traced to PR #131's own upstream commits (`fa1ab88`, `fe284a7`), pulled in solely via D-20's disclosed, deliberate merge of `origin/main` — not authored by any Phase 46 plan.
- **Files modified:** None (source code) — only the evidence file records both the literal command's non-empty output and the corrected, empty result, with the full chain of reasoning connecting them.
- **Verification:** `git diff c72be91..HEAD --name-only -- typsphinx/` returns empty; `git log c72be91..HEAD --oneline -- typsphinx/builder.py` (empty) confirms zero commits after the merge touch the one file that does differ from the pre-phase baseline.
- **Committed in:** `fce7fd6` (Task 1 commit) — the deviation and both commands are recorded inline in `46-SC4-INVARIANTS.md`'s Invariant 3 section.

---

**Total deviations:** 1 auto-fixed (1 verification-logic bug, [Rule 1])
**Impact on plan:** The underlying invariant (Phase 46 is prep-only w.r.t. `typsphinx/`) is proven true, just via a corrected measurement rather than the plan's literal command. No source code was touched. No scope creep — the deviation is confined to the evidence file's own diagnostic transparency, exactly as this plan's "every number must come from a command in the file" instruction requires.

## Issues Encountered
None beyond the Invariant 3 reference-point bug documented above (handled as a Rule 1 deviation, not a blocking issue).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both this plan's artifacts (`46-SC4-INVARIANTS.md`, `46-REL04-EVIDENCE.md`) are committed and available for `46-06`'s handoff document and any later `/gsd-complete-milestone` cross-check.
- **REL-04 remains open**, exactly as designed — it is not this plan's job to close it, and it was not closed. The next real tag push (at `/gsd-complete-milestone`) is the only event that can generate its acceptance evidence; if that push fails at `create-release` again, REL-04 carries forward again, per the requirement's own stated boundary.
- No blockers for the remainder of Phase 46 (plan 46-06's handoff document, and eventually `/gsd-complete-milestone`'s publish).

---
*Phase: 46-v0-7-1-release-prep-prep-only*
*Completed: 2026-08-11*

## Self-Check: PASSED

- FOUND: `.planning/phases/46-v0-7-1-release-prep-prep-only/46-SC4-INVARIANTS.md`
- FOUND: `.planning/phases/46-v0-7-1-release-prep-prep-only/46-REL04-EVIDENCE.md`
- FOUND: `.planning/phases/46-v0-7-1-release-prep-prep-only/46-05-SUMMARY.md`
- FOUND: commit `fce7fd6` (Task 1)
- FOUND: commit `6f37991` (Task 2)
- FOUND: commit `96ca02c` (this SUMMARY)

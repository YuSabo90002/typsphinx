---
phase: 57-v0-9-0-release-prep-prep-only
plan: 04
subsystem: docs
tags: [changelog, migration-guide, sphinx, worktree-verification, release-prep]

# Dependency graph
requires:
  - phase: 56-per-document-template-documentation
    provides: "the published Removed Configuration Values table (typst_template_assets) and the current output-layout contract page this guide cross-references"
provides:
  - "docs/source/changelog.rst's new `Migrating from 0.8.x to 0.9.0` section, the destination the `## [0.9.0]` CHANGELOG lead paragraph (57-03) points readers at"
  - "57-MIGRATION-EVIDENCE.md: real before/after -b typst build transcripts at the v0.8.0 tag vs HEAD, plus D-10's live discovery-grep disposition"
  - "D-10 discharged as verification (zero remaining stale-prerequisite / dead-link hits outside .planning/ and CHANGELOG.md)"
affects: [58-complete-milestone, release-prep-precedent]

# Actuals (#2632)
actuals:
  tokens: 5446
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns: ["second, independently-provisioned git worktree at a release tag to produce a real 'before' build transcript, rather than deriving it from records"]

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-MIGRATION-EVIDENCE.md
  modified:
    - docs/source/changelog.rst

key-decisions:
  - "D-08 discharged literally: the 'before' build ran in a second `git worktree add --detach` checkout at v0.8.0 with its own `uv sync`, proven isolated by an `import typsphinx` version+path transcript (0.8.0, path under the second worktree), not by assumption."
  - "The output-relocation breaking bullet's before/after code-blocks are quoted verbatim from the D-08 transcript (57-MIGRATION-EVIDENCE.md); the other three breaking bullets' before/after blocks are grounded in real, freshly-run builds (both at v0.8.0 in an ephemeral second worktree and at HEAD) rather than invented, though those extra transcripts are not separately filed (Task 2's declared files_modified is changelog.rst only)."
  - "Breaking bullets ordered loudest-to-quietest: pre-write template-layout validation (hard ExtensionError) leads, then the output relocation (build succeeds, asset resolution can break downstream), then the typst_template_assets removal (a warning), then the <srcdir>/base.typ shadow-route move (fully silent)."
  - "D-10 discharged as verification, not a fix: the live repo-wide grep (four sweeps) returns zero hits outside .planning/ and CHANGELOG.md, so no prose fix was made this task; commit 70e24958 is cited as closing evidence."

requirements-completed: []  # REL-08 stays [ ] through this phase per plan/context instruction

coverage:
  - id: D1
    description: "Migrating from 0.8.x to 0.9.0 guide published in docs/source/changelog.rst, most-recent-first, four Breaking bullets each with a real before/after code-block pair, one 'no action is needed' item, a disambiguation paragraph, and a closing :doc: cross-reference"
    requirement: "REL-08"
    verification:
      - kind: unit
        ref: "tests/test_changelog_page_gate.py (uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -q)"
        status: pass
      - kind: other
        ref: "grep -c '^Migrating from 0\\.8\\.x to 0\\.9\\.0$' docs/source/changelog.rst == 1; awk-scoped section carries 8 code-block:: text blocks, 4 **Breaking:** bullets, 1 'no action is needed' phrase"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-08's before/after build evidence: a real -b typst build at the v0.8.0 tag in an independently-provisioned second worktree (isolation proven by import typsphinx version+path), and the same fixture built at HEAD"
    verification:
      - kind: other
        ref: "57-MIGRATION-EVIDENCE.md ## D-08 section; git worktree list / git branch --list show no leftover checkout or branch"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-10 discharged as verification: live repo-wide discovery grep (stale Python/Sphinx prerequisites + dead docs/configuration.rst-class links) returns zero hits outside .planning/ and CHANGELOG.md; commit 70e24958 cited as closing evidence"
    verification:
      - kind: other
        ref: "57-MIGRATION-EVIDENCE.md ## D-10 sections; four grep sweeps, all zero hits after correcting the plan's own verify-regex path-anchor mismatch"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-17
status: complete
---

# Phase 57 Plan 04: Migration Guide + D-10 Verification Summary

**Wrote the `Migrating from 0.8.x to 0.9.0` guide from a real build at the `v0.8.0` tag in a second, independently-provisioned worktree, and discharged D-10 by re-running its discovery grep live (zero hits).**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3
- **Files modified:** 2 (`docs/source/changelog.rst`, `.planning/phases/57-v0-9-0-release-prep-prep-only/57-MIGRATION-EVIDENCE.md`)

## Accomplishments

- Built the same `tests/roots/test-basic` fixture twice — once at HEAD (this worktree, per-key
  `_template/typst/base.typ` bundle) and once in a second, disposable `git worktree add --detach`
  checkout at `v0.8.0` with its own `uv sync --extra dev` (single shared `_template.typ` at the
  output root) — and proved the second checkout's isolation with an `import typsphinx` transcript
  printing version `0.8.0` and a `__file__` path under the second worktree, not the executor's.
- Published `Migrating from 0.8.x to 0.9.0` in `docs/source/changelog.rst`, most-recent-first
  (above `Migrating from 0.7.x to 0.8.0`), with four `**Breaking:**` bullets — the pre-write
  template-layout validation (WR-01/CR-01), the `_template.typ` → `_template/<key>/` bundle
  relocation (D-08's transcribed content), the `typst_template_assets` removal, and the silent
  `<srcdir>/base.typ` → `<srcdir>/_typst/base.typ` shadow-route move — each with a real before/after
  `code-block:: text` pair, plus a "no action is needed" item for the additive registry, a closing
  disambiguation paragraph, and a `:doc:` cross-reference to `/user_guide/output_layout`.
- Discharged D-10 by running the discovery grep live across four sweeps (stale `Python 3.9`/`Sphinx
  5.0`-class prerequisites, `Sphinx 6.x`–`8.x`-shaped statements, the dead `docs/configuration.rst`
  link class, and every `../../docs/` relative link from `examples/`) — zero hits outside
  `.planning/` and `CHANGELOG.md`'s historical entries. Cited commit `70e24958` (`git show --stat`)
  as closing evidence; it corrected five files, two beyond the amendment's four-file floor.
- Recorded D-11's declined version-sync gate as a knowing risk acceptance; no test module added.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the guide's "before"/"after" sides** - `01e50da1` (docs)
2. **Task 2: Write the `Migrating from 0.8.x to 0.9.0` guide** - `2a128096` (docs)
3. **Task 3: Discharge D-10 by re-running the discovery grep live** - `381b6ebf` (docs)

_No plan-metadata commit — worktree mode excludes STATE.md/ROADMAP.md updates; the orchestrator
commits those centrally after merge._

## Files Created/Modified

- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-MIGRATION-EVIDENCE.md` - D-08's before/after
  build transcripts and isolation proof, plus D-10's live discovery-grep run and disposition
- `docs/source/changelog.rst` - new `Migrating from 0.8.x to 0.9.0` migration guide section

## Decisions Made

- **Breaking-bullet order (loudest to quietest):** pre-write validation (hard build failure) leads,
  then the output relocation (build succeeds but downstream Typst compile can break), then the
  `typst_template_assets` removal (a warning), then the shadow-route move (fully silent). The plan
  left this ordering to executor discretion.
- **Evidence sourcing for the three non-D-08 breaking bullets:** Task 1's evidence file only covers
  the output-relocation axis (the one D-08 is specifically about). To avoid inventing warning/error
  text for the other three axes, I ran additional real builds — both at HEAD and, for the two axes
  whose "before" state needed a genuine v0.8.0 build (the shadow-route pickup and the pre-write
  validation's absence), in two further ephemeral second worktrees at `v0.8.0` (each provisioned and
  isolation-proven the same way as Task 1's, then removed with no branch left behind) — to capture
  real command output before writing the guide's prose. These extra transcripts are not filed as a
  separate artifact (Task 2's declared `files_modified` is `docs/source/changelog.rst` only), but
  nothing in the guide's before/after blocks was written from memory or inference.
- **Guide's before-block emitted file paths spot-checked against 57-MIGRATION-EVIDENCE.md**, per the
  plan's acceptance criteria: `_template.typ`, `_template/typst/base.typ`, and both `#import(...)`
  lines all appear verbatim in the evidence file's Task 1 transcripts.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's own `<verify>` exclusion regex for Task 3 is a no-op on this grep**
- **Found during:** Task 3 (D-10 discovery grep)
- **Issue:** The plan's automated `<verify>` filters with `grep -v '^\./\.planning/'` and
  `grep -v '^\./CHANGELOG\.md'`, anchored on a leading `./`. On this machine's `grep`,
  `grep -rn ... .` does not prefix recursive matches with `./` — paths come back as
  `.planning/foo.md`, not `./.planning/foo.md` — so the literal exclusion never matches and the
  command as written reports 32 hits (all inside `.planning/`/`CHANGELOG.md`) as if they were
  outside the excluded areas.
- **Fix:** Re-ran the same search with a correctly anchored exclusion (`^\.planning/`,
  `^CHANGELOG\.md`, no leading `./`) — same intent, same search, zero hits. Both the literal
  command's output and the corrected command's output are recorded verbatim in
  `57-MIGRATION-EVIDENCE.md` under `## D-10 — discovery grep, run live`, so the discrepancy is
  documented rather than silently routed around.
- **Files modified:** `.planning/phases/57-v0-9-0-release-prep-prep-only/57-MIGRATION-EVIDENCE.md`
  (evidence only; the plan file itself was not edited)
- **Verification:** Both grep invocations run and their output transcribed; corrected version
  confirmed zero hits, matching the four other independent sweeps in the same task
- **Committed in:** `381b6ebf` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 bug — a plan-authored verify-script path-anchor mismatch, not
a defect in the published content)
**Impact on plan:** No scope change. The underlying claim (zero stale-prerequisite / dead-link hits
outside `.planning/`/`CHANGELOG.md`) holds under both the literal and the corrected command; only
the literal command's own exclusion filter was broken.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The `## [0.9.0]` CHANGELOG lead paragraph's pointer to "Migrating from 0.8.x to 0.9.0" now has a
  real destination.
- `57-MIGRATION-EVIDENCE.md` is available for `57-08`'s SC#4 sweep and `57-09`'s handoff as
  additional evidence that this phase's `typsphinx/` diff is empty (confirmed here independently:
  `git diff --name-only -- typsphinx/` produced no output across all three tasks).
- No blockers. `git worktree list` and `git branch --list` show no leftover checkout or branch from
  this plan's three temporary worktrees.

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-17*

## Self-Check: PASSED

- FOUND: docs/source/changelog.rst
- FOUND: .planning/phases/57-v0-9-0-release-prep-prep-only/57-MIGRATION-EVIDENCE.md
- FOUND: .planning/phases/57-v0-9-0-release-prep-prep-only/57-04-SUMMARY.md
- FOUND commit: 01e50da1
- FOUND commit: 2a128096
- FOUND commit: 381b6ebf

---
phase: 69-v0-9-3-close-prep-prep-only-unpublished
plan: 01
subsystem: documentation
tags: [changelog, dependabot, uv, tox-uv, nixos, myst, docs-build]

# Dependency graph
requires:
  - phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
    provides: NIX-01..08 (NixOS FHS dev shell shims, cited by the NIX bullet)
  - phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves
    provides: TOX-01..04 (tox-uv revert, cited by the TOX bullet)
  - phase: 66-github-dependabot-yml-pip-uv-ecosystem
    provides: DEP-01, DEP-03, DEP-04 (dependabot pip->uv ecosystem switch, cited by the DEP bullet)
  - phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128
    provides: DEP-02, DEP-05 (proof on a real uv PR, cited by the DEP bullet)
  - phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix
    provides: DOC-19..21 (contributor-notes documentation, cited by the NIX bullet)
provides:
  - Three `### Changed` bullets under the existing `## [Unreleased]` heading of `CHANGELOG.md`,
    citing all 20 requirement IDs the v0.9.3 milestone closed (TOX-01..04, DEP-01..05, NIX-01..08,
    DOC-19..21)
  - Proof that both docs environments (`docs-html`, `docs-pdf`) render the new prose through MyST
    with zero change to the warning count, from clean builds taken before and after the edit
  - Proof the edit is pure addition against the plan's base commit, with the tail link-reference
    block and `### Planned for Future Releases` byte-identical
affects: [69-06-handoff-and-final-fence, complete-milestone]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 7190
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Clean-build docs baseline (`rm -rf docs/_build` immediately before every counted build) taken
       before and after a CHANGELOG.md edit, comparing both warning count and warning-line set"
    - "Tracer task proves the render chain on one bullet before authoring the remaining two, per the
       plan's tracer-feedback-gate discipline"

key-files:
  created:
    - .planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CHANGELOG-EVIDENCE.md
  modified:
    - CHANGELOG.md

key-decisions:
  - "Three bold-lead bullets (TOX, DEP, NIX order) under a new `### Changed` heading, matching the
     house style Phase 61/63 established — no lead paragraph, no `### Verified` subsection (D-04),
     placed above the untouched `### Planned for Future Releases` (D-03)"
  - "The DEP bullet names the ruff-carrying pull request (#138) as the one on which the mechanism
     was proven, per D-05, without calling it the first such pull request"
  - "The DEP bullet does not claim an observed `sphinx-typst-stack` grouped update under `uv`
     (`UV_GROUP_PR_COUNT = 0` per Phase 67); the NIX bullet does not claim CI coverage of
     `flake.nix` and names neither of the two manual-step words Phase 68 confined to `CLAUDE.md`"
  - "No version string `0.9.3` appears anywhere in `CHANGELOG.md`; REL-12 stays uncounted, and this
     SUMMARY declares `requirements-completed: []`"

patterns-established:
  - "Evidence-file `KEY = value` bare lines, one value per line, no trailing prose — verify commands
     read them with `sed -n \"s/^KEY = //p\"`"

requirements-completed: []  # REL-12 closes at /gsd-complete-milestone, never in a plan.

coverage:
  - id: D1
    description: "CHANGELOG.md's ## [Unreleased] region carries a new ### Changed subsection with
      exactly three bold-lead bullets (TOX, DEP, NIX), citing all 20 requirement IDs, above a
      byte-identical ### Planned for Future Releases"
    requirement: REL-12
    verification:
      - kind: other
        ref: "Task 1/2 <automated> verify — region heading order, bold-bullet count, ID-count
          assertions, all re-run and matched live during execution"
        status: pass
    human_judgment: false
  - id: D2
    description: "No 0.9.3 version literal anywhere in CHANGELOG.md; heading count, link-reference
      count, tail line and the Planned block hash are all unchanged from the plan's base commit
      (pure addition, zero removed lines)"
    requirement: REL-12
    verification:
      - kind: other
        ref: "Task 2 <automated> verify — HEADINGS_AFTER/LINKREFS_AFTER/PLANNED_SHA_AFTER equality,
          V093_AFTER = 0, removed-line count = 0, all measured live"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both docs environments (docs-html, docs-pdf) rebuild clean (rm -rf docs/_build
      first) before and after the edit with identical warning counts (3 / 5) and identical
      WARNING-line sets; docs/_build/pdf/typsphinx.pdf begins with %PDF-"
    requirement: REL-12
    verification:
      - kind: integration
        ref: "uv run tox -e docs-html and uv run tox -e docs-pdf, run four times total (pre-edit,
          tracer, post-edit) from an empty docs/_build each time"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every claim in the three bullets is traced to a named Phase 64-68 evidence file
      in an Accuracy basis section; no bullet claims a user-facing effect, CI coverage of
      flake.nix, verified darwin support, or an observed grouped uv-ecosystem update"
    requirement: REL-12
    verification: []
    human_judgment: true
    rationale: "Whether the prose is 'a reader of the published changelog' quality and whether the
      accuracy-basis mapping is complete and honest is an editorial/transparency judgment no
      automated check fully captures — the automated fence catches the literal prohibited strings,
      but the overall honesty of the account is best confirmed by a human read."

duration: 7min
completed: 2026-09-12
status: complete
---

# Phase 69 Plan 01: CHANGELOG Unreleased bullets and clean-docs proof Summary

**Three `### Changed` bullets (tox-uv revert, Dependabot pip→uv, NixOS FHS dev shell) added under
the existing `## [Unreleased]` heading of `CHANGELOG.md`, citing all 20 v0.9.3 requirement IDs, with
both docs environments proven to rebuild clean at unchanged warning counts before and after the
edit.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-09-12T22:32:19Z
- **Completed:** 2026-09-12T22:39:34Z
- **Tasks:** 2
- **Files modified:** 2 (`CHANGELOG.md` edited, `69-CHANGELOG-EVIDENCE.md` created)

## First section (per plan `<output>` contract)

```
BASE_69_01 = 2db4e803d36d5f7a5db0a92b08cac4988fa88957
DOCS_HTML_WARN_BASE = 3
DOCS_PDF_WARN_BASE = 5
DOCS_HTML_WARN_POST = 3
DOCS_PDF_WARN_POST = 5
UNRELEASED_BOLD_AFTER = 3
UNRELEASED_IDS_AFTER = 20
```

No `## HALT` heading was written anywhere in this plan's evidence file.

## Accomplishments
- Authored the TOX bullet (tracer slice), proved its MyST render adds zero new docs-html warnings
  against a clean pre-edit baseline, before authoring anything further
- Authored the DEP bullet (Dependabot pip→uv ecosystem) and NIX bullet (NixOS FHS dev shell),
  both bounded by named Phase 66-68 evidence and neither overstating what those phases observed
- Proved the full three-bullet edit is pure addition against the plan's base commit: zero removed
  lines, identical heading/link-reference counts, identical `### Planned for Future Releases` hash,
  identical tail compare-link line
- Rebuilt both `docs-html` and `docs-pdf` clean (`rm -rf docs/_build` immediately before each of
  four total builds) and confirmed the warning counts (3 / 5) and warning-line sets are unchanged
  from the pre-edit baseline, with the PDF confirmed to start `%PDF-`

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — pre-edit measurements, clean-build docs baselines, TOX bullet** -
   `44f1572d` (feat)
2. **Task 2: DEP and NIX bullets, pure-addition proof, fence assertions, post-edit clean builds** -
   `a30fd6f2` (feat)

_No plan-metadata commit follows in worktree mode — the orchestrator commits `STATE.md` /
`ROADMAP.md` centrally after merge; this SUMMARY is committed on its own by this same executor per
the parallel-execution contract._

## Files Created/Modified
- `CHANGELOG.md` - Three bold-lead bullets under a new `### Changed` subsection of `## [Unreleased]`
- `.planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CHANGELOG-EVIDENCE.md` - Plan
  base, pre-edit measurements, both clean-build docs baselines, the three bullets with their
  accuracy basis and discretion notes, the pure-addition proof, the fence assertions, and the
  post-edit clean-build docs counts

## Decisions Made
- Followed the plan's D-01..D-05 shape exactly: TOX, DEP, NIX bullet order under `### Changed`, no
  lead paragraph, no `### Verified` subsection, all requirement IDs cited inside each bold span's
  trailing parentheses
- The DEP bullet cites PR #138 (the ruff-carrying pull request) as the one on which the mechanism
  was proven, per D-05's discretion, without an ordinal claim
- Neither the DEP bullet nor the NIX bullet claims coverage this milestone did not observe (no
  grouped-`uv` PR claim, no CI-covers-`flake.nix` claim, no verified-darwin claim)

## Deviations from Plan

None - plan executed exactly as written. Both tasks' `<automated>` verify commands were re-run
piecewise (the sandbox refuses single multi-clause compound commands, so each conjunct was run as
its own Bash call) and every conjunct passed live during execution — see the evidence file's
`## Fence assertions` and `## Pure-addition proof` sections for the full transcript.

---

**Total deviations:** 0
**Impact on plan:** None. All acceptance criteria and the plan's own `<verification>` block were
satisfied on the first pass.

## Issues Encountered

None. The sandbox's compound-command restriction required splitting the plan's single-line
`<automated>` verify strings into individual Bash calls; every individual assertion was still run
and passed, so this changed only the mechanics of verification, not its content or completeness.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `CHANGELOG.md`'s `## [Unreleased]` region now carries all three bullets this milestone's
  CHANGELOG work requires (SC#2), ready for `69-06`'s final fence observation and
  `/gsd-complete-milestone`'s promotion into a versioned section.
- The docs half of SC#3 (clean docs-html/docs-pdf builds at unchanged warning counts) is proven on
  this plan's own tip; `69-03`'s full green-tree evidence and `69-04`'s CI dispatch are separate,
  parallel wave-2 plans and are not affected by this plan's scope.
- No blockers. `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` are
  untouched by this plan, as required.

---
*Phase: 69-v0-9-3-close-prep-prep-only-unpublished*
*Completed: 2026-09-12*

## Self-Check: PASSED

- `CHANGELOG.md` — FOUND on disk
- `.planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CHANGELOG-EVIDENCE.md` — FOUND on disk
- Commit `44f1572d` (Task 1) — FOUND in `git log --oneline --all`
- Commit `a30fd6f2` (Task 2) — FOUND in `git log --oneline --all`
- `plan_head_before: 2db4e803d36d5f7a5db0a92b08cac4988fa88957`, `commits: 2` (measured via
  `git rev-list --count 2db4e803d36d5f7a5db0a92b08cac4988fa88957..HEAD`)

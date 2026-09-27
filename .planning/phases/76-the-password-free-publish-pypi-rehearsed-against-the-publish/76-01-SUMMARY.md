---
phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish
plan: 01
subsystem: infra
tags: [github-actions, pypi, trusted-publishing, oidc, release]

# Dependency graph
requires: []
provides:
  - "release.yml's publish-pypi step publishes with no password: credential (Trusted Publishing / OIDC path)"
  - "76-ATT-EVIDENCE.md opened with the six ATT-01 sections and ATT01_SC1_VERDICT = MET"
affects: [76-03]

# Actuals (#2632)
actuals:
  tokens: 2032
  tasks: 2
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Re-measure line numbers at the phase base with grep/sed rather than trust ROADMAP/REQUIREMENTS/CONTEXT citations (D-08) — all three had been wrong once for this file."

key-files:
  created:
    - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-ATT-EVIDENCE.md
  modified:
    - .github/workflows/release.yml

key-decisions:
  - "Deleted exactly lines 143-144 (with: and password: ${{ secrets.PYPI_API_TOKEN }}), not ROADMAP's stale :141-144 citation, which would have deleted the Publish to PyPI step itself."
  - "Nothing added in place of the deleted lines: no attestations:, no skip-existing:, no action-SHA pin, no permissions narrowing (REQUIREMENTS.md § Out of Scope)."

patterns-established:
  - "Evidence file with KEY = value lines, one command-then-key pair per fact, gated by an automated <verify> that re-derives every key independently from live commands rather than trusting the prose."

requirements-completed: [ATT-01]

coverage:
  - id: D1
    description: "publish-pypi's Publish to PyPI step deletes the with:/password: lines reading secrets.PYPI_API_TOKEN, so pypa/gh-action-pypi-publish@release/v1 takes the OIDC/Trusted Publishing path; publish-testpypi, permissions:, and the env:-not-interpolation invariant are unchanged."
    requirement: "ATT-01"
    verification:
      - kind: other
        ref: "Task 1 <verify> automated command (diff --numstat 0/2, unified-diff exact two lines, grep counts, PyYAML structural parse)"
        status: pass
      - kind: other
        ref: "Task 2 <verify> automated command (SC #1 counts, byte-identity regions, reapply-targets=0, run: block walk 15 steps / 0 interpolations)"
        status: pass
    human_judgment: false
  - id: D2
    description: "76-ATT-EVIDENCE.md opened at the fixed name with the ATT-01 measurement, deletion, SC #1 readout, env-not-interpolation invariant, and verdict sections (D-08), ready for 76-03 to append the ATT-02 sections."
    requirement: "ATT-01"
    verification:
      - kind: other
        ref: "Task 1 + Task 2 <verify> section-presence checks (grep -qxF on each of the six section headings)"
        status: pass
    human_judgment: false

# Metrics
duration: 26min
completed: 2026-09-27
status: complete
---

# Phase 76 Plan 01: Password-Free `publish-pypi` (ATT-01) Summary

**Deleted the two `with:`/`password:` lines under `publish-pypi`'s `Publish to PyPI` step in
`.github/workflows/release.yml` (lines 143-144, measured — not ROADMAP's stale `:141-144`), leaving
`pypa/gh-action-pypi-publish@release/v1` to take the OIDC/Trusted Publishing path with no
replacement credential, and opened `76-ATT-EVIDENCE.md` with the full ATT-01 record and
`ATT01_SC1_VERDICT = MET`.**

## Performance

- **Duration:** 26 min
- **Started:** 2026-09-27T12:06:57Z
- **Completed:** 2026-09-27T12:32:46Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `publish-pypi`'s `Publish to PyPI` step no longer reads `secrets.PYPI_API_TOKEN`; the step, its
  name, and `pypa/gh-action-pypi-publish@release/v1` are otherwise unchanged.
- `publish-testpypi` and the top-level `permissions:` block are proven byte-identical to the phase
  base; the `env:`-not-interpolation invariant is confirmed by a PyYAML walk over all 15 `run:`
  steps (zero `${{` interpolations).
- `76-ATT-EVIDENCE.md` opened at the D-08 fixed name with all six ATT-01 sections and
  `ATT01_SC1_VERDICT = MET`, ready for plan 76-03 to append the ATT-02 wave-2 rehearsal sections.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — measure, delete the two credential lines, prove the workflow still parses,
   open 76-ATT-EVIDENCE.md** - `efde71a9` (fix), `2d4fbff2` (docs)
2. **Task 2: SC #1 readout, byte-identity invariants, env-not-interpolation check, ATT-01 verdict** -
   `e7e240ba` (docs)

_Note: Task 1 produced two commits (the workflow edit on its own, then the evidence file), per the
plan's explicit instruction to commit them separately._

## Files Created/Modified
- `.github/workflows/release.yml` - `publish-pypi`'s `Publish to PyPI` step no longer carries a
  `with:`/`password:` block; two lines deleted, nothing added.
- `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-ATT-EVIDENCE.md` -
  new file (D-08); ATT-01 measurement, deletion, SC #1 readout, env-not-interpolation invariant, and
  verdict sections.

## Decisions Made
- Measured the credential line fresh with `grep -nF` rather than trusting ROADMAP's `:141-144`
  citation, which spans the `- name:`/`uses:` lines too and would delete the publish step itself.
  Confirmed P=144 (`password:`), P-1=143 (`with:`); both adjacent to the expected neighbours.
- Committed the workflow edit and the evidence file as two separate commits within Task 1, matching
  the plan's explicit "commit the workflow edit on its own... then commit the evidence file."

## Deviations from Plan

None - plan executed exactly as written. Every measured value (line numbers, grep counts, diff
stats, YAML structural assertions, byte-identity regions, run-step walk) matched the plan's expected
values on the first pass; no HALT condition was triggered.

## Tracer Feedback Gate

Task 1 is `type="tracer"`. Its `<verify>` carries only `<automated>` (no `<human-check>`), auto-mode
was not active (`workflow._auto_chain_active` = false, `workflow.auto_advance` = false), and
`workflow.human_verify_mode` = `end-of-phase` (default). Per the tracer feedback gate's row 3, the
tracer's `<verify>` was re-run after commit; it passed (`TASK1_VERIFY_PASS`), so execution continued
directly to Task 2 with no checkpoint synthesized.

## Issues Encountered

The session running this plan was interrupted once between staging the evidence file (after Task 1's
deletion and commit `efde71a9`) and committing it. On resume, `git status`/`git log` confirmed the
worktree state matched expectations exactly (workflow edit committed, evidence file staged but
uncommitted, no drift); the evidence file's content was re-verified against Task 1's `<verify>`
command before committing. No rework was needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `.github/workflows/release.yml` on this worktree branch carries the password-free `publish-pypi`
  step, ready to be merged and pushed to the milestone branch (D-06) so plan 76-03's wave-2
  rehearsal can dispatch this exact copy.
- `76-ATT-EVIDENCE.md` is open at the fixed D-08 name with the ATT-01 sections closed; plan 76-03
  appends the ATT-02 sections to the same file.
- No blockers. The sibling wave-1 plan (76-02 / MSG-06) touches disjoint files
  (`typsphinx/translator.py`, `tests/test_translator_path_quoting_gate.py`,
  `76-MSG06-EVIDENCE.md`) and was not touched by this plan.

---
*Phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish*
*Completed: 2026-09-27*

---
phase: 29-rtd-build-establishment-english-parent-pdf-path-decision
plan: 02
subsystem: infra
tags: [readthedocs, rtd, http-verification, dns, redirect, build-log-provenance]

requires:
  - phase: 29-01
    provides: ".readthedocs.yaml (HTML-only) and the conf.py language seam; the branch state RTD built"
provides:
  - "Live-evidence record (29-VERIFICATION.md) proving /en/latest/ and the documentation root both serve real content over real HTTP"
  - "Verbatim raw-build-log install-provenance excerpt evidencing a checked-out-commit install, not a stale PyPI wheel"
  - "Two explicit, separately-tracked Phase 33 handoff preconditions (Default Version flip, Default Branch reversal)"
affects: [30-i18n-rtd-japanese, 31-url-cutover, 32-pages-teardown, 33-release-prep]

tech-stack:
  added: []
  patterns:
    - "Live-evidence-over-dashboard-claim: every RTD web-UI action is recorded as human_needed (owner-reported), never asserted as machine-verified; only its outcome (a real HTTP fetch, a real log fetch) is recorded as verified"

key-files:
  created:
    - .planning/phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-VERIFICATION.md
  modified: []

key-decisions:
  - "The 6th owner-manual action (RTD Default Branch = milestone branch, so `latest` tracks the unmerged gsd/v0.6.4-read-the-docs-migration branch instead of main) was recorded as a 5th Owner-Manual Step, distinct from the plan's original 4, per explicit executor instruction from the checkpoint-resolution context — its reversal is tracked as a second, separate Phase 33 handoff precondition (Precondition B) alongside the pre-planned Default Version flip (Precondition A), deliberately not merged into one item"
  - "The raw build log was retrievable over public HTTP (app.readthedocs.org/api/v2/build/<id>.txt, 200, 81479 bytes) — the plan's best-effort 'strengthening step' succeeded, so the install-provenance excerpt rests on a directly machine-fetched log rather than solely on the owner's paste"
  - "The install-provenance reading names the actual token present in the fetched log (`(from file:///.../checkouts/latest)` plus paired `Building`/`Built` lines at 116/127/164) rather than a pre-committed grep pattern, per the plan's explicit prohibition on deciding the string before reading the log"

requirements-completed: [RTD-01, RTD-04]

coverage:
  - id: D1
    description: "https://typsphinx.readthedocs.io/en/latest/ returns HTTP 200 and serves typsphinx's own rendered documentation content (SC#1 serving half)"
    requirement: "RTD-01"
    verification:
      - kind: other
        ref: "curl -sS -o /tmp/p29-en-latest.html -w 'code=%{http_code} url=%{url_effective} size=%{size_download}\\n' -L https://typsphinx.readthedocs.io/en/latest/ -> code=200 size=30451, body contains 'Sphinx to Typst Conversion'"
        status: pass
    human_judgment: false
  - id: D2
    description: "The documentation root (https://typsphinx.readthedocs.io/) resolves via a real HTTP redirect chain to the latest version and serves real content (SC#4 / RTD-04)"
    requirement: "RTD-04"
    verification:
      - kind: other
        ref: "curl -sS -D - -o /tmp/p29-root-body.html -L https://typsphinx.readthedocs.io/ -> HTTP/2 302 -> location: .../en/latest/ -> HTTP/2 200; body contains 'Sphinx to Typst Conversion'"
        status: pass
    human_judgment: false
  - id: D3
    description: "The raw build log's install line is read and recorded verbatim, with a reading naming the actual token that evidences a checked-out-commit install rather than a PyPI-index resolve (SC#1 provenance half)"
    requirement: "RTD-01"
    verification:
      - kind: other
        ref: "curl -sS -o /tmp/p29-buildlog-33756675.txt ... https://app.readthedocs.org/api/v2/build/33756675.txt -> code=200 size=81479; line 164 confirmed '+ typsphinx==0.6.3 (from file:///.../checkouts/latest)', lines 116/127 confirmed 'Building/Built typsphinx @ file:///.../checkouts/latest'"
        status: pass
    human_judgment: false
  - id: D4
    description: "RTD project creation, GitHub connection, Admin Language=English, Default Version=latest, and (beyond-plan) Default Branch=milestone-branch — all owner-manual RTD dashboard actions with no repository-observable proof"
    verification: []
    human_judgment: true
    rationale: "These are third-party web-UI clicks in RTD's own database; no command in this repository can assert they happened. Recorded as human_needed, owner-reported values only — never claimed as machine-verified."
---

# Phase 29 Plan 02: RTD Live-Evidence Verification Summary

**Two real HTTP fetches and a fetched raw build-log excerpt prove the English RTD site is live, resolving, and running code installed from the checked-out commit — not a stale PyPI wheel.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-25T14:00:00Z (approx, first live fetch)
- **Completed:** 2026-07-25T14:20:00Z (approx)
- **Tasks:** 2 (Task 1 was pre-resolved by the orchestrator before this agent was spawned)
- **Files modified:** 1 created (`29-VERIFICATION.md`)

## Accomplishments

- Fetched `https://typsphinx.readthedocs.io/en/latest/` live: HTTP 200, 30451 bytes, body contains the
  distinctive "Sphinx to Typst Conversion" index-page phrase — not a placeholder or 404.
- Fetched `https://typsphinx.readthedocs.io/` live and recorded the full redirect chain: a single 302 to
  `/en/latest/`, then 200 with the same distinctive phrase — proving the documentation root resolves to
  an existing, content-serving version rather than to a version-less `stable`.
- Fetched the build's raw log directly over public HTTP (`app.readthedocs.org/api/v2/build/33756675.txt`,
  200, 81479 bytes) and confirmed, in the fetched copy itself, the exact decisive install line at line 164
  (`+ typsphinx==0.6.3 (from file:///.../checkouts/latest)`) plus supporting `Building`/`Built` lines at
  116/127 — recorded verbatim with a reading naming that specific `file://` token as evidence of a
  checked-out-commit install, contrasted with what a PyPI-index resolve would have printed instead.
- Ran the `latexmk`/`pdflatex`/`.tex` pre-observation scan over the fetched log: count 0 (expected — this
  build predates any PDF step), recorded as a Plan 04 pre-observation, not a verdict.
- Recorded the fifth owner-manual action (RTD Default Branch set to the milestone branch, so `latest`
  tracks `gsd/v0.6.4-read-the-docs-migration` instead of `main`) and its reversal as a second, separate
  Phase 33 handoff precondition — kept distinct from the pre-planned Default Version (`latest`→`stable`)
  flip per explicit instruction.

## Task Commits

1. **Task 2: Fetch /en/latest/ and the documentation root over real HTTP and record both verbatim** -
   `8963148` (docs)
2. **Task 3: Record the install-provenance log excerpt and the Phase 33 Default-Version handoff** -
   `6e8a1bd` (docs)

_Task 1 (`checkpoint:human-action`, gate `blocking-human`) was already resolved by the orchestrator before
this agent was spawned — see `<checkpoint_already_resolved>` in the execution prompt. No commit was made
for it since it touches no repository file._

**Plan metadata:** this SUMMARY's own commit (created after this file, per plan output spec).

## Files Created/Modified

- `.planning/phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-VERIFICATION.md` -
  NEW. Five sections: `## SC#1 — /en/latest/ serves real content`, `## SC#4 — documentation root
  resolves`, `## Owner-Manual Steps (human_needed)`, `## SC#1 — install provenance from the raw build
  log`, `## Phase 33 Handoff Precondition`.

## Decisions Made

- The raw build log fetch was attempted as the plan's best-effort "strengthening step" and succeeded
  (public HTTP, 200, 81479 bytes) — so the install-provenance section rests on a directly re-fetched and
  re-read log, not solely on the owner's Task-1 paste. The excerpt was independently confirmed to match at
  the exact line numbers (164, 116, 127) in this agent's own fetched copy before being recorded.
- The fifth owner-manual action (Default Branch → milestone branch) is recorded in the same
  `Owner-Manual Steps (human_needed)` section as the plan's original four, marked identically as
  owner-reported/not-machine-verified; its reversal is a *second*, separate Phase 33 precondition
  (Precondition B), deliberately not merged with the pre-planned Default Version flip (Precondition A) —
  per explicit instruction, since the two govern different RTD settings (which version is default vs.
  which branch `latest` itself tracks).
- No `29-VERIFICATION.md` content was asserted from memory or from the orchestrator's brief without an
  independent re-fetch/re-read: every command in the file was actually executed by this agent and its
  real output recorded, even where the orchestrator had already measured the same result.

## Deviations from Plan

None — plan executed exactly as written for Tasks 2 and 3. Task 1's resolution (including the
plan-unanticipated fifth owner-manual action) was handled entirely upstream by the orchestrator per
`<checkpoint_already_resolved>`; this agent recorded it in the evidence file exactly as instructed, which
is not a deviation from *this agent's* task list.

## Issues Encountered

- The Bash sandbox in this worktree rejects compound shell commands (chained `&&`/command substitution in
  a single invocation) with a "too complex to verify" refusal when they touch git/env state. Worked around
  by splitting the multi-step branch-check, `uv sync`, and `uv` symlink commands into separate single-step
  Bash calls — no functional change to what was executed, just more, smaller tool calls.
- To satisfy the atomic-per-task-commit contract given the plan writes both tasks into the same single
  file, the file was authored in two passes: Task 2's sections written and committed first, then Task 3's
  sections appended in a second Write+commit — verified via `git diff` that the second commit contains
  only additions after Task 2's former end-of-file boundary (no `-` lines besides the diff header).

## User Setup Required

None — no external service configuration required by this plan itself. (Task 1's RTD dashboard
configuration was already performed by the owner before this agent started; see
`## Owner-Manual Steps (human_needed)` in `29-VERIFICATION.md` for the full record.)

## Next Phase Readiness

- RTD-01's live half and RTD-04 are both discharged with direct HTTP evidence; RTD-01's install-provenance
  half is also discharged via the fetched raw log.
- Two Phase 33 handoff preconditions are now on record and must both be actioned only after the `v0.6.4`
  tag builds green: (A) Default Version `latest`→`stable`, (B) Default Branch
  `gsd/v0.6.4-read-the-docs-migration`→`main`. Phases 30–32 should each re-fetch the documentation root as
  their own standing-invariant check per the roadmap's RTD-04 ownership note.
- `29-VERIFICATION.md` is now the append-only live-evidence record for the rest of Phase 29; Plans 03–06
  must append new `##` sections without disturbing what Plan 02 wrote (confirmed byte-preserving here via
  `git diff`).
- No repository source file was touched: `git status --porcelain typsphinx/ tests/ docs/ pyproject.toml
  .readthedocs.yaml` is empty.

---
*Phase: 29-rtd-build-establishment-english-parent-pdf-path-decision*
*Completed: 2026-07-25*

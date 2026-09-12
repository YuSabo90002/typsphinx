---
phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128
plan: 03
subsystem: infra
tags: [dependabot, github-actions, pypi, packaging, evidence-only, D-05]

# Dependency graph
requires:
  - phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128
    provides: "wave-1 gate — 67-01's DEP02_VERDICT = MET, SC2_BRANCH = can, MECHANICAL_CLOSE = none"
provides:
  - "D-05 merit premise re-measured through `packaging` over live PyPI JSON, twice (Task 1 and immediately pre-close): Sphinx 9.1.0's only in-range release excludes docutils 0.23 both times"
  - "#128 closed on its merits (pyproject.toml-only shape against --locked, CI red at install, the uv updater's own dependency_file_not_resolvable) with one owner-approved comment, not merged"
  - "GROUPED_128 = yes carried forward as a D-06 input for 67-05"
affects: [67-05-PLAN.md]

# Actuals (#2632)
actuals:
  tokens: 5551
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns: ["evidence-only phase: KEY = value lines in a phase evidence markdown, no code/test file", "gh pr comment --body-file as the RESEARCH A2 fallback when the sandbox blocks command-substitution forms of gh pr close --comment"]

key-files:
  created:
    - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-DOCUTILS-EVIDENCE.md
  modified: []

key-decisions:
  - "Owner approved 'close as drafted' at the Task 2 checkpoint: #128 closed with DRAFT_COMMENT_128 verbatim as APPROVED_COMMENT_128, no edits."
  - "Sandbox refused the plan's literal `gh pr close 128 --comment \"$(sed ...)\"` form (command substitution combined with gh flagged as too complex to verify worktree-only). Used the plan's own documented RESEARCH A2 fallback instead: extracted APPROVED_COMMENT_128 to a plain file via sed (no gh/git in that command), posted it with `gh pr comment --body-file` (reads the file directly, no retyping), then `gh pr close 128` with no --comment and no --delete-branch."
  - "D05_CAP_RELAXED and D05_CAP_RELAXED_PRECLOSE both measured 'no' — the docutils cap did not relax between the two reads (2026-09-12T13:30:39Z and 2026-09-12T13:37:16Z), so no HALT branch was taken and the close proceeded."

patterns-established:
  - "Pattern (from Phase 66): KEY = value bare lines in the evidence file, re-assertable via sed -n 's/^KEY = //p', continued in this plan for PYPI_READ_AT/SPHINX_LATEST/D05_CAP_RELAXED/HEAD128/OWNER_DECISION_128/APPROVED_COMMENT_128/CLOSED_AT_128 and the rest of the key set."

requirements-completed: []

coverage:
  - id: D1
    description: "D-05 PyPI re-measurement: Sphinx's docutils cap re-checked through packaging over every in-range release, twice (Task 1 and immediately pre-close), both D05_CAP_RELAXED* = no"
    requirement: DEP-05
    verification:
      - kind: other
        ref: "live curl + uv run python (packaging) against https://pypi.org/pypi/sphinx/json and per-version JSON — recorded in 67-DOCUTILS-EVIDENCE.md § D-05 PyPI re-measurement and § Pre-close PyPI re-measurement"
        status: pass
    human_judgment: false
  - id: D2
    description: "#128 disposed of on its merits: closed (not merged) with exactly one owner comment equal to the owner-approved text, closed by the owner account, branch not deleted"
    requirement: DEP-05
    verification:
      - kind: other
        ref: "gh pr view 128 --json state,closed,closedAt,mergedAt,comments; gh api .../issues/128/events — recorded in 67-DOCUTILS-EVIDENCE.md § Post-close record"
        status: pass
    human_judgment: false
  - id: D3
    description: "Owner approval gate (checkpoint:decision, gate=blocking-human) honored before any post: owner replied 'close as drafted', recorded verbatim with DECIDED_AT_128 before APPROVED_COMMENT_128 was committed"
    requirement: DEP-05
    verification: []
    human_judgment: true
    rationale: "The owner's literal reply is the human-judgment input this plan exists to gate on; it is recorded as data, not re-derived from a test."

duration: 8min
completed: 2026-09-12
status: complete
---

# Phase 67 Plan 03: Disposal of #128 (D-05, docutils cap) Summary

**#128 closed on its merits — Sphinx 9.1.0 still caps `docutils<0.23,>=0.21` (re-measured twice through `packaging`, `D05_CAP_RELAXED = no` and `D05_CAP_RELAXED_PRECLOSE = no`), the `uv` updater's own attempt failed with `dependency_file_not_resolvable`, and #128 is `pyproject.toml`-only against `--locked` — closed with exactly one owner-approved comment, `OWNER_DECISION_128 = close`, `APPROVED_COMMENT_128` = the drafted text verbatim, `CLOSED_AT_128 = 2026-09-12T13:38:31Z`.**

## Performance

- **Duration:** 8 min (active execution; Task 1 → Task 2 checkpoint → owner reply → Task 3, excluding the wait for the owner's reply)
- **Started:** 2026-09-12T13:30:39Z (approx., first recorded PyPI read)
- **Completed:** 2026-09-12T13:38:31Z (`CLOSED_AT_128`)
- **Tasks:** 3 (Task 1 auto/tracer, Task 2 checkpoint:decision, Task 3 auto)
- **Files modified:** 1 (created)

## Accomplishments
- Confirmed the wave-1 gate from `67-PROOF-EVIDENCE.md` (`DEP02_VERDICT = MET`, `SC2_BRANCH = can`, `MECHANICAL_CLOSE = none`, no `## HALT`) before any Task 1 action.
- Re-measured Sphinx's docutils cap live through `packaging` over PyPI JSON at Task 1: `SPHINX_LATEST = 9.1.0`, `SPHINX_DOCUTILS_REQ = docutils<0.23,>=0.21`, `SPHINX_IN_RANGE = 9.1.0` (the only non-pre-release release in typsphinx's own `sphinx>=9.1,<10`), `DOCUTILS_LATEST = 0.23`, `D05_CAP_RELAXED = no`.
- Recorded #128's merits: its head commit (`HEAD128 = 000859f7e07167a8be8b6d3beceea44bca26fa4f`) touches only `pyproject.toml`; a real CI run on that head (`33343567900`) failed exactly at `uv sync --extra dev --locked` with a stale-lockfile error; the `uv` updater's own attempt at this same bump failed with `dependency_file_not_resolvable`; `GROUPED_128 = yes` (a `sphinx-typst-stack` group PR).
- Read the whole `#128` thread (1 dependabot comment, 0 review comments, 0 reviews, no non-dependabot author) and drafted `DRAFT_COMMENT_128`, presented at the Task 2 checkpoint alongside every measured value and merit.
- Owner replied "close as drafted" at the `checkpoint:decision` (`gate="blocking-human"`); recorded verbatim with `DECIDED_AT_128`, and `APPROVED_COMMENT_128` written equal to the committed `DRAFT_COMMENT_128` and committed before any posting.
- Ran the idempotency check (`ALREADY_CLOSED_128 = no`), the pre-close PyPI re-measurement (`D05_CAP_RELAXED_PRECLOSE = no`, still only Sphinx 9.1.0 in range), and the `#128` re-assertion (OPEN, unchanged head, no new non-dependabot comment) — all immediately before posting.
- Posted `APPROVED_COMMENT_128` and closed `#128` (not merged, no `--delete-branch`); post-close record confirms exactly one owner comment equal to the approved text, and the last `closed` event's actor is the owner account.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — wave-1 gate, D-05 PyPI re-measurement, #128 merits, thread, draft comment** - `7a580a39` (docs)
2. **(Owner decision recorded, before posting)** - `32a9db42` (docs)
3. **Task 3: On close — idempotency, pre-close re-measurement, re-assertion, post and close, disposition** - `dbf9ea3b` (fix)

**Plan metadata:** committed separately (this SUMMARY, if any REQUIREMENTS.md changes) after this file is written.

## Files Created/Modified
- `.planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-DOCUTILS-EVIDENCE.md` - Head check/provisioning, wave-1 gate, D-05 PyPI re-measurement (twice), #128 re-snapshot and re-assertion, merits, thread, draft comment, owner decision, idempotency check, close record, and disposition.

## Decisions Made
- Owner approved "close as drafted" — `#128` closed with the exact drafted text, no edits.
- The sandbox refused the plan's literal `gh pr close 128 --comment "$(sed ...)"` invocation as too complex to verify it stays inside the worktree (a command-substitution-plus-`gh` shape, not a `git`-safety concern per se). Used the plan's own documented RESEARCH A2 fallback: extracted `APPROVED_COMMENT_128` to a plain scratch file via `sed` alone (no `gh`/`git` in that command), posted it with `gh pr comment --body-file` (reads the file directly, no shell substitution, no retyping), then `gh pr close 128` with no `--comment` and no `--delete-branch`. This preserves the plan's "read from the evidence key, never retyped" mitigation (T-67-12) through a different mechanical path.
- Both PyPI re-measurements (Task 1 and immediately pre-close) agreed: `D05_CAP_RELAXED = no` and `D05_CAP_RELAXED_PRECLOSE = no`. No HALT branch was ever taken.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Sandbox refused the plan-literal `gh pr close --comment "$(sed ...)"` form**
- **Found during:** Task 3, step 5 ("Close (#128)")
- **Issue:** The execution sandbox refused any Bash command combining a shell command-substitution (`$(sed ...)` / `$(cat ...)`) with a `gh` invocation, reporting it could not statically verify the command stays inside the worktree. This blocked the plan's literal `gh pr close 128 --comment "$(sed -n 's/^APPROVED_COMMENT_128 = //p' ...)"` invocation, even though `gh pr close --help` confirms `--comment` is supported.
- **Fix:** Used the plan's own explicitly documented RESEARCH A2 fallback (originally written for the case where `--comment` is unsupported, but mechanically identical to what was needed here): extracted `APPROVED_COMMENT_128` to a plain scratch file with a `sed`-only command (no `gh`/`git` in that command, so the sandbox allowed it), verified its exact byte content with `cat -A`, then posted it via `gh pr comment 128 --body-file <path>` (reads the file directly — no shell substitution, no retyping of the text), then closed with a separate `gh pr close 128` (no `--comment`, no `--delete-branch`). The scratch file was removed immediately after use.
- **Files modified:** none (evidence-only; the fallback is recorded in `67-DOCUTILS-EVIDENCE.md` § "Close (#128)")
- **Verification:** Post-close `gh pr view 128 --json comments` shows exactly one owner comment whose body is byte-identical to `APPROVED_COMMENT_128`, and `#128` is `CLOSED` (not merged).
- **Committed in:** `dbf9ea3b` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking, Rule 3)
**Impact on plan:** The fallback achieves the exact same outcome (posted text byte-identical to the committed approved comment, no retyping) through a mechanically different but equally verifiable path. No scope creep; no text was ever hand-retyped into a `gh` argument.

## Issues Encountered
None beyond the sandbox restriction documented above as a deviation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `67-05` can now cite this plan's `GROUPED_128 = yes` observation for its D-06 grouped-update coverage write-up, alongside `67-01`'s and `67-02`'s handoffs.
- `DEP-05`'s `requirements-completed` stays `[]` here by design — it closes in `67-05`, per this plan's own `<output>` spec.
- No blockers or concerns carried forward. `#128`'s branch was not deleted by this plan (per D-05's constraints).

## Self-Check: PASSED

- FOUND: `.planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-DOCUTILS-EVIDENCE.md`
- FOUND: commit `7a580a39` (Task 1)
- FOUND: commit `32a9db42` (owner decision)
- FOUND: commit `dbf9ea3b` (Task 3)
- Re-ran the plan's acceptance criteria for both Task 1 and Task 3 (all individual clauses of the `<verify><automated>` blocks) — all passed.
- Re-ran the plan-level `<verification>` bullets: docutils cap re-measured through `packaging` twice, both `no`; the whole thread was read and the draft presented before any post; `#128` is `CLOSED` with exactly one owner comment equal to the approved text, closed by the owner account.

---
*Phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128*
*Completed: 2026-09-12*

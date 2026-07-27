---
phase: 32-github-pages-teardown-irreversible
plan: 01
subsystem: infra
tags: [readthedocs, github-pages, ci, evidence-gate, curl, pypdf]

# Dependency graph
requires:
  - phase: 29-rtd-build-establishment-english-parent-pdf-path-decision
    provides: RTD serving English HTML/PDF, Branch A confirmed (RTD reaches packages.typst.org)
  - phase: 30.1-translations-repository-japanese-rtd-site
    provides: Japanese RTD project serving ja HTML/PDF, 65/65-translated user_guide/builders docname
  - phase: 31-published-url-cutover-repo-wide-link-guard
    provides: RTD is the published source of truth; README/PyPI links already point at it
provides:
  - "GATE VERDICT: GREEN — freshly re-taken, in-phase proof that RTD currently serves en HTML, ja HTML (content-verified), en PDF, and ja PDF, and that the doc root resolves"
  - Pre-teardown baseline snapshot (gh-pages SHA, live github.io 200, PR #124 pre-teardown head) for Plan 03's after-state comparison
  - Structural unlock for Plan 02 (docs.yml edit) and Plan 03 (branch deletion + owner-manual Pages disable) per D-03
affects: [32-02-docs-yml-teardown, 32-03-branch-deletion-and-pages-disable]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Verbatim command + output evidence log (Phase 29 D-15 format), reused for the pre-teardown gate"
    - "CJK-density ratio (not lang attribute or HTTP status) as the content-verification proxy for I18N-01's all-English failure mode"

key-files:
  created:
    - .planning/phases/32-github-pages-teardown-irreversible/32-EVIDENCE.md
    - .planning/phases/32-github-pages-teardown-irreversible/32-01-SUMMARY.md
  modified: []

key-decisions:
  - "GATE VERDICT: GREEN unlocks Plans 02/03 (D-03) — all five gate checks passed with wide margins (en/ja HTML 200, ja CJK count 1038 vs en control 0, both PDFs >3.4x the 500000-byte threshold)"
  - "Deviation: fixed a self-inflicted acceptance-criteria bug — the GATE VERDICT line was initially written as markdown-bold (**GATE VERDICT: GREEN**), which does not match the required '^GATE VERDICT: (GREEN|RED)\$' regex; corrected to a plain unformatted line before commit"

patterns-established: []

requirements-completed: [CI-04]

coverage:
  - id: D1
    description: "32-EVIDENCE.md exists with all four required headings (Gate check 1, Gate check 2, Pre-teardown baseline, GATE VERDICT), each gate check backed by verbatim curl/git/gh commands and their literal output"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "grep -c 'Gate check 1' / 'Gate check 2' / 'Pre-teardown baseline' / GATE VERDICT (SC#1) headings in 32-EVIDENCE.md — all present"
        status: pass
      - kind: other
        ref: "grep -cE '^GATE VERDICT: (GREEN|RED)\$' 32-EVIDENCE.md — exactly 1 match"
        status: pass
      - kind: other
        ref: "git status --porcelain — no modified path outside .planning/phases/32-github-pages-teardown-irreversible/, no untracked *.pdf"
        status: pass
    human_judgment: false
  - id: D2
    description: "GATE VERDICT: GREEN, based on live evidence that RTD is currently serving en/ja HTML (content-verified) and en/ja PDFs, structurally unlocking Plans 02/03's irreversible teardown"
    requirement: "CI-04"
    verification: []
    human_judgment: true
    rationale: "This verdict authorizes the milestone's only no-undo action (Pages teardown). Per GATE-01's honest-verifier convention and T-32-01's high-severity DoS threat disposition, a false GREEN here has total recovery cost — the owner should independently spot-check the recorded HTTP/PDF evidence in 32-EVIDENCE.md before Plan 02/03 execute, not rely solely on the automated grep checks that confirm the file's structural shape."

duration: 5min
completed: 2026-07-27
status: complete
---

# Phase 32 Plan 01: Pre-Teardown Evidence Gate Summary

**Freshly re-taken, in-phase live evidence proves RTD is currently serving English HTML, content-verified Japanese HTML (1038 CJK chars vs. 0 in the English control), and both English/Japanese PDFs (1.7MB/1.9MB, 93/94 pages) — GATE VERDICT: GREEN, unlocking the irreversible teardown in Plans 02/03.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-07-27T14:08:00Z
- **Completed:** 2026-07-27T14:13:00Z
- **Tasks:** 3
- **Files modified:** 1 (`32-EVIDENCE.md`, built incrementally across 3 task commits + 1 fix commit)

## Accomplishments
- Gate check 1 (D-01): en HTML `200`, doc root resolves to `/en/latest/` (RTD-04), ja HTML `200` with the literal string `ビルダー` present and a CJK density of 1038 characters vs. 0 in the same-docname English control — falsifies I18N-01's "builds green, serves 100% English" failure mode rather than trusting a `lang` attribute or bare HTTP status.
- Gate check 2 (D-02): both the English and Japanese PDF download URLs return `200`, `%PDF` magic bytes, and well-over-threshold sizes (1704446 / 1888676 bytes against a 500000-byte bar; 93 / 94 pages against a 40-page bar). Scratch downloads deleted immediately after measurement; no PDF binary committed.
- Pre-teardown baseline recorded for Plan 03's after-state comparison: `origin/gh-pages` at `f97862dfea151dd904591a18d2ddbd0bf72fd851` (matches CONTEXT.md's 2026-07-27 measurement — no branch revival), `https://YuSabo90002.github.io/typsphinx/` still live at `200`, and PR #124's pre-teardown head (`980f6ca909b8b07045d664548094b98f31bd8551`) recorded with an explicit note that it must never be cited as SC#3 evidence (RESEARCH.md Pitfall 4).
- Single unambiguous `GATE VERDICT: GREEN` line, backed by a five-row per-check table, all rows PASS.
- Zero repository source changes — `git diff --stat` against the worktree base shows only `32-EVIDENCE.md` touched, confirming D-03's "gate makes zero repo changes" constraint held.

## Task Commits

Each task was committed atomically:

1. **Task 1: Record the HTML half of the gate** - `40bc567` (docs)
2. **Task 2: Record the PDF half of the gate** - `ca0ffef` (docs)
3. **Task 3: Snapshot the pre-teardown baseline and write the GATE VERDICT** - `996e3e3` (docs)

**Deviation fix:** `e0c6fed` (fix) — corrected the GATE VERDICT line format (see Deviations below).

_Plan metadata commit deferred to worktree-mode convention — SUMMARY.md commit below stands in for it since STATE.md/ROADMAP.md updates are owned by the orchestrator._

## Files Created/Modified
- `.planning/phases/32-github-pages-teardown-irreversible/32-EVIDENCE.md` - the five-gate-check evidence log, pre-teardown baseline, and GATE VERDICT block
- `.planning/phases/32-github-pages-teardown-irreversible/32-01-SUMMARY.md` - this file

## Decisions Made
- Used the `%PDF` magic-byte + `od -An -tx1` hex dump together (both forms recorded) since `xxd` is unavailable in this environment — the literal `%PDF` text output and the `25 50 44 46` hex bytes corroborate each other.
- Provisioned a worktree-local `.venv` via `uv sync --extra dev` (per CLAUDE.md's worktree-isolation section) solely to run `pypdf`'s page-count measurement — this was optional/best-effort per the plan, but the environment briefing indicated it was likely to succeed quickly, and it did (93/94 pages recorded rather than the "not measured" fallback).
- The ja/en CJK ratio check (`>= 10x`) technically divides by zero since the English control returned exactly 0 CJK characters; recorded this explicitly in the verdict line as corroborating rather than fabricating a ratio, per the plan's own wording ("state the four numbers in the verdict line").

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] GATE VERDICT line was markdown-bolded, breaking the required exact-match regex**
- **Found during:** Task 3, immediately after writing the initial full evidence file and running the plan's own verification checks
- **Issue:** The plan's acceptance criteria require "exactly one line matching `^GATE VERDICT: (GREEN|RED)$`" verbatim. The first draft wrote `**GATE VERDICT: GREEN**` (markdown-bold), which does not match that anchored regex — `grep -cE '^GATE VERDICT: (GREEN|RED)$'` returned `0`.
- **Fix:** Removed the `**` bold wrapping so the line reads exactly `GATE VERDICT: GREEN`.
- **Files modified:** `.planning/phases/32-github-pages-teardown-irreversible/32-EVIDENCE.md`
- **Verification:** Re-ran `grep -cE '^GATE VERDICT: (GREEN|RED)$'` → `1`.
- **Committed in:** `e0c6fed`

---

**Total deviations:** 1 auto-fixed (1 bug — self-caught formatting error against the plan's own acceptance criteria)
**Impact on plan:** No scope creep; the fix was required for the plan's own automated verify commands to pass and was caught before the plan-level self-check.

## Issues Encountered
None beyond the deviation above.

## User Setup Required
None - no external service configuration required. All evidence was gathered via already-authenticated `gh` CLI and unauthenticated public `curl` fetches, per the project's established "RTD public APIs need no auth" pattern.

## Next Phase Readiness

**GATE VERDICT: GREEN** — Plan 02 (docs.yml teardown: remove the `peaceiris/actions-gh-pages` deploy step and the two now-unused `permissions:` entries, add the D-06 guard tests) and Plan 03 (remote `gh-pages` branch deletion + owner-manual Settings → Pages disable + SC#3 CI-run observation) may now proceed per D-03's structural gate.

Per D-04, this gate's evidence is valid for teardown **on the same calendar day only** (2026-07-27). If Plan 02/03 execution crosses a day boundary, this plan must be re-run in full before the teardown continues; Plans 02 and 03 are each expected to re-confirm the four URL statuses (status-only, not the full content/PDF checks) at their own head regardless.

No blockers. The pre-teardown baseline (`gh-pages` SHA `f97862d`, PR #124 head `980f6ca9`) is recorded in `32-EVIDENCE.md` for Plan 03's after-state comparison.

---
*Phase: 32-github-pages-teardown-irreversible*
*Completed: 2026-07-27*

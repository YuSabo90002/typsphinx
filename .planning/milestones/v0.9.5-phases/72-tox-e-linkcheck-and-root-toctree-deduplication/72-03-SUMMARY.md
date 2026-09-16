---
phase: 72-tox-e-linkcheck-and-root-toctree-deduplication
plan: 03
subsystem: docs
tags: [tox, linkcheck, doc-24, todo-note]

requires:
  - phase: 72-02
    provides: "[testenv:linkcheck] tox environment, shaped like docs-html, outside env_list"
provides:
  - "CLAUDE.md, README.md and docs/source/contributing.rst each list `tox -e linkcheck` (DOC-24)"
  - "72-DOC24-EVIDENCE.md: discovery grep, per-file numstat/column proof, dispositions, post-edit grep, D-07 note diff"
  - "The 2026-07-22 linkcheck todo carries D-07's status note and stays in todos/pending/"
affects: [72-04, 72-05]

actuals:
  tokens: 3268
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "one-line append directly after the neighbouring `tox -e docs*` line, column-aligned comment matching the block's other lines, verified by a Python str.index equality check rather than eyeballed"

key-files:
  created:
    - .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-DOC24-EVIDENCE.md
  modified:
    - CLAUDE.md
    - README.md
    - docs/source/contributing.rst
    - .planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md

key-decisions:
  - "The tracer feedback gate after Task 1 auto-continued without a checkpoint: interactive run, HUMAN_VERIFY_MODE=end-of-phase (config default), and the task's <verify> carries only <automated> — re-ran the verify, it passed, proceeded straight to Task 2 expansion."
  - "The discovery grep (`tox -e docs-pdf`) and the supplementary grep (`tox -e (lint|type|py312|docs-html|docs)`) found no listing surface beyond the three named at planning time (CLAUDE.md, README.md, docs/source/contributing.rst); the other two hits (.github/workflows/docs.yml, CHANGELOG.md) are dispositioned as non-listing (CI step, released history bullet) per D-06/constraint 3."
  - "The D-07 status note is appended in English per the plan's instruction, even though the rest of the todo file is in Japanese — matches the plan's literal wording requirement and does not translate existing content."

requirements-completed: [DOC-24]

coverage:
  - id: D1
    description: "CLAUDE.md gains exactly one line, `tox -e linkcheck             # Check external links and anchors (needs network; not run by plain tox)`, directly after the `tox -e docs-pdf` line, column-aligned with its neighbours (column 29), byte-identical elsewhere (numstat 1/0)."
    requirement: DOC-24
    verification:
      - kind: other
        ref: "72-DOC24-EVIDENCE.md ## CLAUDE.md — numstat, -U1 hunk, and the Python column/ASCII assertion (CLAUDE_COMMENT_COLUMN = 29)"
        status: pass
    human_judgment: false
  - id: D2
    description: "README.md and docs/source/contributing.rst each gain one column-aligned line after their `… tox -e docs` line (columns 28 and 31); every discovery/supplementary hit carries a disposition row; post-edit `tox -e linkcheck` grep shows exactly 3 lines, matching DOC24_LISTING_SURFACES; the docs-pdf hit count is unchanged (5) after the edits."
    requirement: DOC-24
    verification:
      - kind: other
        ref: "72-DOC24-EVIDENCE.md ## Surfaces, ## Dispositions, ## Post-edit grep — numstat, -U1 hunks, Python column/ASCII assertions, disposition table, and the re-run greps"
        status: pass
    human_judgment: false
  - id: D3
    description: "The 2026-07-22 linkcheck todo gains an appended `## Status note (Phase 72, v0.9.5)` naming `[testenv:linkcheck]`, QUA-08, and the side-PR-to-main constraint, while its base content stays a byte-identical prefix and it remains in todos/pending/ (no todo added, moved, or removed)."
    requirement: DOC-24
    verification:
      - kind: other
        ref: "72-DOC24-EVIDENCE.md ## D-07 todo note — numstat (6 added, 0 removed), prefix-hash equality, verbatim appended text, and the unchanged pending+completed file count (60 before and after)"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-09-13
status: complete
---

# Phase 72 Plan 03: DOC-24 Listing Surfaces and D-07 Todo Note Summary

**Landed `tox -e linkcheck` on all three listing surfaces (CLAUDE.md, README.md, docs/source/contributing.rst) found by a fresh repo-wide grep, and appended D-07's status note to the 2026-07-22 linkcheck CI todo, which stays open in `todos/pending/`.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-09-13T13:35:58Z
- **Completed:** 2026-09-13T13:39:46Z
- **Tasks:** 3
- **Files modified:** 5 (`CLAUDE.md`, `README.md`, `docs/source/contributing.rst`, the linkcheck todo, and the new `72-DOC24-EVIDENCE.md`)

## Accomplishments
- Verified the QUA-13 ordering gate: `tox.ini` at this worktree's base (`043949e7`) already carries `[testenv:linkcheck]` (72-02, merged). Proceeded rather than halting.
- Fresh `git grep -n 'tox -e docs-pdf' -- ':!.planning'` recorded 5 hits (`DOC24_GREP_HITS = 5`); the supplementary grep for `lint|type|py312|docs-html|docs` found no listing surface beyond the same three files.
- `CLAUDE.md` gains `tox -e linkcheck             # Check external links and anchors (needs network; not run by plain tox)` directly after the `tox -e docs-pdf` line (numstat 1/0, column 29, matching its two neighbours).
- `README.md` gains `uv run tox -e linkcheck     # Check external links and anchors (needs network; not run by plain tox)` after `uv run tox -e docs` (numstat 1/0, column 28).
- `docs/source/contributing.rst` gains the three-space-indented equivalent after its own `uv run tox -e docs` line (numstat 1/0, column 31).
- `## Dispositions` records one row per hit of both greps (19 total): 3 marked "listing surface — linkcheck line added", 2 marked non-listing (`.github/workflows/docs.yml` CI step, `CHANGELOG.md` released history bullet), the remaining 14 marked as already part of an edited listing surface. `DOC24_LISTING_SURFACES = 3`, post-edit `tox -e linkcheck` grep shows exactly 3 lines (`DOC24_LINKCHECK_LINES = 3`), post-edit `tox -e docs-pdf` grep unchanged at 5 hits. `DOC24_VERDICT = MET`.
- The 2026-07-22 linkcheck todo (`.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md`) gains an appended `## Status note (Phase 72, v0.9.5)` in English, naming the landed `[testenv:linkcheck]`, the still-open QUA-08 (Future requirement, deferred by the owner 2026-09-13), and the side-PR-to-`main` constraint (ROADMAP v0.9.5 constraint 4, precedented by PR #137). Base content is a byte-identical 41-line prefix; the todo stays in `todos/pending/`; the pending+completed file count (60) is unchanged.

## Task Commits

Each task was committed atomically (plain `git commit`, per this plan's override — no GSD commit helper):

1. **Task 1: Tracer — gate check, discovery grep, CLAUDE.md edit** - `1e10249f` (docs, the edit) + `858d673f` (docs, the evidence record)
2. **Task 2: README/contributing.rst edits, dispositions, post-edit grep** - `543a756b` (docs, the edits) + `d46c56c7` (docs, the evidence record)
3. **Task 3: D-07 status note on the linkcheck todo** - `159b7612` (docs, the note) + `ad02bd23` (docs, the evidence record)

**Plan metadata:** this SUMMARY's own commit (see below; STATE.md/ROADMAP.md/REQUIREMENTS.md are NOT touched by this executor per orchestrator override — the orchestrator updates them centrally after the wave merges).

## Files Created/Modified
- `CLAUDE.md` - gains the `tox -e linkcheck` line in § Commands' docs block (1 line added, 0 removed)
- `README.md` - gains the `uv run tox -e linkcheck` line in the tox commands block (1 line added, 0 removed)
- `docs/source/contributing.rst` - gains the indented `uv run tox -e linkcheck` line in the "Using Tox" code block (1 line added, 0 removed)
- `.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md` - gains the appended `## Status note (Phase 72, v0.9.5)` section (6 lines added, 0 removed); stays in `todos/pending/`
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-DOC24-EVIDENCE.md` - new; the full discovery/edit/disposition/D-07 evidence transcript

## Decisions Made
- The tracer feedback gate fired after Task 1 exactly per the precedence chain in `checkpoints.md`: no `gate="blocking-human"` on the task, auto-mode inactive (`_auto_chain_active`/`auto_advance` both false), interactive + `end-of-phase` + automated-only `<verify>` → re-ran the verify (passed) and proceeded straight into Task 2 with no checkpoint synthesized.
- Discovery is repo-wide, not limited to the three surfaces named at roadmap/planning time (milestone invariant #4) — the supplementary grep is discovery-only and found nothing new, confirming the planning-time table was complete.
- The D-07 note is written in English as the plan literally instructs, even though the rest of the todo file (created 2026-07-22) is in Japanese — no existing line or frontmatter key was touched.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None. The known sandbox quirk (Bash refusing commands containing the literal substring "source") from the project overrides did not need to be worked around in this plan — no command text needed to contain that substring; `docs/source/contributing.rst` was addressed exclusively through the Read/Edit tools with the full path, and no Bash invocation referenced the literal path segment.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All three DOC-24 listing surfaces name `tox -e linkcheck`; `72-DOC24-EVIDENCE.md` carries `BASE_72_03`, `SCRATCH_72_03`, `DOC24_GREP_HITS = 5`, `CLAUDE_COMMENT_COLUMN = 29`, `README_COMMENT_COLUMN = 28`, `CONTRIBUTING_COMMENT_COLUMN = 31`, `DOC24_LISTING_SURFACES = 3`, `DOC24_LINKCHECK_LINES = 3`, `DOC24_VERDICT = MET`, and `D07_NOTE = appended` — ready for 72-04/72-05 to read back.
- No blockers or concerns for downstream plans in this wave.

## Self-Check: PASSED

- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-DOC24-EVIDENCE.md` — FOUND
- `CLAUDE.md`, `README.md`, `docs/source/contributing.rst` (each modified, verified via `git diff --numstat`) — FOUND, each matches expected 1 added / 0 removed
- `.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md` — FOUND, still in `todos/pending/`, base content confirmed a byte-identical 41-line prefix
- Commits `1e10249f`, `858d673f`, `543a756b`, `d46c56c7`, `159b7612`, `ad02bd23` — all FOUND in `git log --oneline`
- Each task's `<automated>` verify re-run at commit time: PASSED (Task 1, Task 2, Task 3 all confirmed above)
- Plan-level `<verification>`: the fresh grep is recorded and every hit dispositioned; each listing surface gained exactly one aligned ASCII line, last in its block; the linkcheck todo carries D-07's note and stays in `todos/pending/` — PASSED

---
*Phase: 72-tox-e-linkcheck-and-root-toctree-deduplication*
*Completed: 2026-09-13*

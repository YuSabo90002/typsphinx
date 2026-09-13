---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 10
subsystem: testing
tags: [ruff, mypy, ast, evidence, typing-modernization, git-history-audit]

# Dependency graph
requires:
  - phase: 70-01
    provides: CLAUDE.md:75 rewrite (DOC-22, D-01..D-03) — audited here as CLAUDE_COMMIT
  - phase: 70-02
    provides: PHASE_BASE_SHA, UP006/UP035 census, SC#2 base counts, up-files list
  - phase: 70-04
    provides: masked-AST mask harness (MASK_HARNESS_SHA256), tracer conversion pilot
  - phase: 70-09
    provides: the ignore flip commit and todo move (FLIP_COMMIT)
provides:
  - "SC1_VERDICT = MET: CLAUDE.md rewrite precedes every conversion commit which precedes the
    flip; the flip commit is exactly M pyproject.toml + one R100 todo rename; zero pending-path
    references remain outside .planning/"
  - "SC2_VERDICT = MET: repo-wide UP006/UP035 clean, no preview setting, banned typing imports
    gone at HEAD (non-empty positive control at base), the four SC#2 counts unchanged, templates
    and the authors ast.Dict gate untouched"
  - "LEG_A_VERDICT = MET: masked-AST hash equal to base for all 10 converted files
    (LEG_A_EQUAL_COUNT = 10), pilot recorded before automation"
  - "LEG_C_VERDICT = MET: tests/ diff is exactly the four converted files, zero non-typing or
    assert lines changed"
  - "LEG_E_VERDICT = MET: mypy stdout hash and exit code match base, same version/interpreter"
  - "CLAUDE.md:75's Python-floor bullet is byte-identical at the flip commit's parent and at HEAD,
    carrying every D-01 token and none of D-02/D-03"
affects: [70-13]

# Actuals (#2632)
actuals:
  tokens: 4863
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Re-derive every after-side value from git/ruff/mypy/the hash-pinned masked-AST harness in
      this worktree; only `_BASE` keys from prior plans' evidence are read, never their own
      verdicts."

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-AFTER-STATIC-EVIDENCE.md
  modified: []

key-decisions:
  - "None — followed the plan's action steps and automated <verify> blocks exactly as written,
    with no deviation."

patterns-established: []

requirements-completed: [QUA-09, QUA-11, QUA-12, DOC-22]

coverage:
  - id: D1
    description: "SC#1 history claims: CLAUDE.md rewrite precedes conversion which precedes the
      flip; flip commit shape; zero pending-path references; two-commit bullet reading against
      D-01..D-03"
    requirement: "DOC-22"
    verification:
      - kind: other
        ref: "70-10-PLAN.md Task 2 <automated> verify block, run in this worktree"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#2 static checks: zero UP006/UP035 repo-wide, no preview setting, banned
      typing imports gone, __init__.py:15 exact, the four SC#2 counts unchanged, templates and
      the authors ast.Dict gate untouched"
    requirement: "QUA-09"
    verification:
      - kind: other
        ref: "70-10-PLAN.md Task 1 <automated> verify block, run in this worktree"
        status: pass
    human_judgment: false
  - id: D3
    description: "QUA-12 leg (a): masked-AST hash equality over every converted file, pilot
      ordering confirmed"
    requirement: "QUA-12"
    verification:
      - kind: other
        ref: "70-10-PLAN.md Task 1 <automated> verify block, run in this worktree"
        status: pass
    human_judgment: false
  - id: D4
    description: "QUA-12 leg (c): tests/ diff contains only typing-name changes, zero assert
      lines touched"
    requirement: "QUA-12"
    verification:
      - kind: other
        ref: "70-10-PLAN.md Task 1 <automated> verify block, run in this worktree"
        status: pass
    human_judgment: false
  - id: D5
    description: "QUA-12 leg (e): mypy stdout string-identical before/after, same version and
      interpreter"
    requirement: "QUA-12"
    verification:
      - kind: other
        ref: "70-10-PLAN.md Task 2 <automated> verify block, run in this worktree"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 10: After-side Static Evidence Summary

**Re-derived every SC#1/SC#2 static claim and QUA-12 legs (a)/(c)/(e) from git, ruff, mypy and the hash-pinned masked-AST harness on the post-flip tree — all five keys measured MET, with the CLAUDE.md bullet proven byte-identical and true at both the pre-flip and post-flip commits.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-09-13T05:32:00Z (approx.)
- **Completed:** 2026-09-13T05:44:00Z
- **Tasks:** 2 completed
- **Files modified:** 1 (evidence file only, plus this SUMMARY)

## Accomplishments
- Confirmed the changed-file set outside `.planning/` is exactly `CLAUDE.md`, `pyproject.toml`
  and the ten census files — nothing else moved.
- Measured `SC2_VERDICT = MET`: zero `UP006`/`UP035` findings repo-wide (against a non-zero
  `UP_TOTAL_BASE = 113`), no `preview` setting anywhere, the banned typing-import grep empty at
  HEAD with a non-empty positive control at `PHASE_BASE_SHA`, `typsphinx/__init__.py:15` exact,
  all four SC#2 counts unchanged, and both the templates directory and
  `tests/test_authors_pipeline_stage_gate.py` (with its `ast.Dict` at line 515) untouched.
- Measured `LEG_A_VERDICT = MET`: the masked-AST hash of every one of the 10 converted files
  equals its base hash (`LEG_A_EQUAL_COUNT = 10 = UP_FILE_COUNT_BASE`), and the pilot evidence
  commit is confirmed an ancestor of every wave-3 conversion commit.
- Measured `LEG_C_VERDICT = MET`: the `tests/` diff touches exactly the four converted files,
  with zero changed non-typing lines and zero changed `assert` lines.
- Measured `LEG_E_VERDICT = MET`: `mypy typsphinx/` stdout hashes identically before and after
  (`46984ca2...`), same version, same interpreter.
- Measured `SC1_VERDICT = MET`: exactly one `CLAUDE.md` commit (`3c5e281c`) and one flip commit
  (`0224b5ea`) since `PHASE_BASE_SHA`; all 8 conversion commits descend from the CLAUDE.md rewrite
  and precede the flip; the flip commit's name-status is exactly `M pyproject.toml` plus the R100
  todo rename; zero tracked references to the todo's pending path remain outside `.planning/`
  after the flip (one positive-control reference confirmed at the flip's parent commit); and the
  CLAUDE.md:75 bullet is byte-identical at both commits, carrying every D-01 token
  (`dict[str, Any]`, `list[str]`, `collections.abc`, `Iterator`, `typing.Dict`) and none of the
  D-02/D-03 forbidden tokens.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — SC#2 static checks, leg (a) over every census file, leg (c) over tests/** - `81084801` (docs)
2. **Task 2: Leg (e) mypy after-side, SC#1 commit-order/two-commit CLAUDE.md read** - `1c83c818` (docs)

**Plan metadata:** committed by the executor per worktree-mode contract (SUMMARY.md only; STATE.md/ROADMAP.md are owned by the orchestrator)

## Files Created/Modified
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-AFTER-STATIC-EVIDENCE.md` - the static half of the after-side evidence: `BASE_70_10`, `VENV_HOME`/`VENV_VERSION_INFO`, `RUFF_VERSION_AFTER`, the changed-file set, SC#2 static checks and its four `_AFTER` counts, leg (a)'s per-file hash table and pilot-ordering check, leg (c)'s tests/ diff census, leg (e)'s mypy hash comparison, and SC#1's commit-order table and two-commit CLAUDE.md reading, with every verdict key set to `MET`

## Decisions Made
None - followed the plan's action steps exactly as written; every automated `<verify>` block
passed on the first run with no fix needed.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None. This plan is itself an audit of 70-01, 70-02, 70-04 and 70-05..70-09's work (ROADMAP
constraint 1(iii)): every value was re-derived from `git`, `ruff`, `mypy` or the hash-pinned mask
harness in this worktree, never copied from an audited plan's own recorded keys — only the
`_BASE` keys from `70-BASELINE-EVIDENCE.md` and `70-MASK-PILOT-EVIDENCE.md` were read for
comparison. No measured value differed from its base key, so no `## HALT` was needed and no
finding was raised to the owner.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

The static half of "nothing else changed" (SC#1, SC#2, and QUA-12 legs (a), (c), (e)) is proven
MET on the post-flip tree. This plan ran in parallel with 70-11 (runtime evidence: legs (b) and
(d)) and 70-12 (docs diff, DOC-23) from the same fork point
(`44c43e345f8d5916486e5b7c2790bcb16c58f9d0`); none of its checks depended on their output. Wave 6
(70-13) can proceed once all three wave-5 plans are merged: it runs the gate quartet, the branch
census, the first push and the CI dispatch, then rolls up every SC across the phase.

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*

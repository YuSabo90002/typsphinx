---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 09
subsystem: infra
tags: [ruff, pyproject.toml, lint-config, typing-modernization]

# Dependency graph
requires:
  - phase: 70-typing-modernization-and-its-behaviour-identity-evidence (waves 1-3)
    provides: all ten census files converted to builtin generics/collections.abc, masked-AST hashes EQUAL, repo-wide UP006/UP035 residue 0 under the still-present ignores
provides:
  - "pyproject.toml with the UP006/UP035 ruff ignores removed"
  - "the 2026-07-22 typing-modernization todo moved to .planning/todos/completed/"
  - "70-FLIP-EVIDENCE.md: pre-flip residue check, flip-commit shape proof, post-flip checks, gate quartet"
affects: [70-10, 70-11, 70-12, 70-13, phase-71]

# Actuals (#2632)
actuals:
  tokens: 1865
  tasks: 2
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Flip-then-verify: repo-wide zero-residue re-measure immediately before the single ignore-removal commit, so no merged state of the branch is ever red (ROADMAP constraint 1(ii))"
    - "One commit, two changes: config-line removal and todo file rename land together, verified after the fact by git show --name-status -M"

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-FLIP-EVIDENCE.md
  modified:
    - pyproject.toml
    - .planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md (renamed from .planning/todos/pending/)

key-decisions:
  - "Flip commit staged by explicit path (git mv for the rename, git add for pyproject.toml); the untracked 70-FLIP-EVIDENCE.md draft was deliberately excluded from that commit and committed separately afterward, per the plan's precise staging requirement."
  - "Task 1's type=\"tracer\" tracer-feedback gate resolved via checkpoints.md row 3 (interactive, human_verify_mode=end-of-phase default, verify carries only <automated>): re-ran the tracer's full automated <verify> end-to-end, it passed, and execution continued to Task 2 with no checkpoint synthesized."

patterns-established: []

requirements-completed: [QUA-09, DOC-22]

coverage:
  - id: D1
    description: "pyproject.toml's [tool.ruff.lint] ignore no longer contains UP006 or UP035, and the flip is a single commit that also moves the todo to completed/"
    requirement: QUA-09
    verification:
      - kind: other
        ref: "git show --name-status -M --format= HEAD~1 (commit 0224b5ea): exactly M pyproject.toml + one R100 rename"
        status: pass
      - kind: other
        ref: "git diff -U0 <PRE_FLIP_SHA> HEAD~1 -- pyproject.toml: two lines removed, zero added"
        status: pass
      - kind: other
        ref: "uv run python -c '...tomllib...' ignore list length 7 (was 9), contains B017/UP028, not UP006/UP035"
        status: pass
    human_judgment: false
  - id: D2
    description: "Repo-wide ruff enforces UP006/UP035 with zero findings, and the pending-path reference is gone outside .planning/ (with a one-hit positive control at the pre-flip commit)"
    requirement: QUA-09
    verification:
      - kind: other
        ref: "uv run ruff check . --select UP006,UP035 (post-flip): All checks passed, exit 0"
        status: pass
      - kind: other
        ref: "uv run ruff check . (bare, post-flip): All checks passed, exit 0"
        status: pass
      - kind: other
        ref: "git grep -n 'todos/pending/2026-07-22-modernize' -- . ':!.planning' at HEAD: empty; at PRE_FLIP_SHA: exactly one hit in pyproject.toml"
        status: pass
    human_judgment: false
  - id: D3
    description: "The post-flip tree passes the full gate quartet (ruff, black, mypy, pytest) with a pytest result identical to the pre-conversion baseline"
    verification:
      - kind: other
        ref: "uv run black --check .: All done, 355 files unchanged, exit 0"
        status: pass
      - kind: other
        ref: "uv run mypy typsphinx/: Success: no issues found in 9 source files, exit 0"
        status: pass
      - kind: integration
        ref: "LC_ALL=C uv run pytest -q -rs -p no:cacheprovider: 1547 passed, 1 skipped in 130.99s, exit 0 (equals PYTEST_RESULT_BEFORE)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 09: The Ignore Flip Summary

**Deleted the UP006/UP035 ruff ignores from pyproject.toml and moved the 2026-07-22 typing-modernization todo to completed/ in one commit, then proved the post-flip tree is ruff-clean repo-wide and passes the full ruff/black/mypy/pytest gate quartet.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 2
- **Files modified:** 2 (pyproject.toml, the renamed todo) + 1 created (70-FLIP-EVIDENCE.md)

## Accomplishments

- `pyproject.toml`'s `[tool.ruff.lint] ignore` array lost the `"UP035"` and `"UP006"` lines (and their deferral comments), going from 9 entries to 7. `B017` and `UP028`, the neighbouring entries, are untouched.
- The 2026-07-22 todo moved from `.planning/todos/pending/` to `.planning/todos/completed/` with byte-identical content, in the **same commit** (`0224b5ea`) as the ignore-line deletion. `git show --name-status -M --format=` on that commit reports exactly `M pyproject.toml` and one `R100` rename — nothing else.
- A repo-wide `uv run ruff check . --select UP006,UP035` was zero **before** the flip (confirming the merged tree from waves 1-3 left no residue anywhere, including files no conversion plan touched) and zero **after** the flip with the rules now actually enforced (no more `--select` override needed). Bare `uv run ruff check .` also passed both times.
- After the flip, `git grep -n 'todos/pending/2026-07-22-modernize' -- . ':!.planning'` finds zero tracked references outside `.planning/`. The positive control — the same grep at the pre-flip commit — finds exactly one, in `pyproject.toml:128`, confirming the grep methodology actually works.
- The post-flip tree passes the full gate quartet: `ruff check .`, `black --check .`, `mypy typsphinx/` (0 issues, 9 source files) all exit 0, and the full test suite (`LC_ALL=C pytest`) reports `1547 passed, 1 skipped` — identical to `PYTEST_RESULT_BEFORE` recorded in `70-BASELINE-EVIDENCE.md`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — confirm zero repo-wide residue, then in one commit delete the two ignore lines and move the todo, and prove the post-flip tree is ruff-clean** — `0224b5ea` (chore, the flip itself) and `3778a318` (docs, the evidence for it)
2. **Task 2: Run the gate quartet on the post-flip tree** — `469069f0` (docs, gate quartet evidence)

**Plan metadata:** this SUMMARY.md's own commit (made immediately after this file).

## Files Created/Modified

- `pyproject.toml` — two ignore-array lines (`UP035`, `UP006`) and their trailing deferral comments removed; nothing else changed
- `.planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — renamed from `.planning/todos/pending/`, content unchanged (`R100`)
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-FLIP-EVIDENCE.md` — created; holds `BASE_70_09`, `PRE_FLIP_SHA`, `VENV_HOME`, `VENV_VERSION_INFO`, `RUFF_VERSION_FLIP`, `IGNORE_LEN_PRE`/`IGNORE_LEN_POST`, the flip-commit shape proof, the pending-path census (with positive control), post-flip ruff results, `MYPY_EXIT_FLIP`, and `PYTEST_RESULT_FLIP`

## Decisions Made

- Staged the flip commit by explicit path only (`git add pyproject.toml`; the todo rename was already staged by `git mv`), keeping the still-untracked `70-FLIP-EVIDENCE.md` draft out of that commit as the plan required, then committed the evidence file separately once it was complete.
- Task 1 is `type="tracer"`, which triggers the executor's tracer-feedback gate before any following task. Per `checkpoints.md`'s precedence chain: no `gate="blocking-human"` was present, auto-mode is not active in this project's config (`workflow.auto_advance: false`, `workflow._auto_chain_active: false`), `workflow.human_verify_mode` defaults to `end-of-phase`, and the tracer's `<verify>` carries only `<automated>` (no `<human-check>`) — so row 3 applied: re-run the tracer's automated verify end-to-end, and on success continue straight to Task 2 with no synthesized checkpoint. The re-run (a full reproduction of the task's `<verify>` predicate in a scratch script, since the inline one-liner was too complex for the worktree-isolation guard to approve directly) passed cleanly.

## Deviations from Plan

None - plan executed exactly as written. The one operational adjustment — running the plan's single-line `<verify>` predicates as equivalent multi-line scripts under my own `mktemp -d` scratch directory rather than as one compound Bash call — was anticipated by orchestrator note 3 and produced byte-identical verification results to the inline form; it is not a deviation in outcome, only in invocation mechanics.

## Issues Encountered

None. Provisioning, both ruff residue measurements, the flip commit, and the gate quartet (including the ~131s full pytest run) all completed without retries.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The ignore flip is done and evidenced; `70-10` (mypy/pytest after-side legs), `70-11` (leg (d) corpus + DOC-23 docs diff after-side), `70-12`, and `70-13` can proceed against this post-flip tip.
- `RUFF_VERSION_FLIP` still equals `RUFF_VERSION_BASE` (`ruff 0.16.6`) — constraint 4 (no mid-flight ruff bump) held throughout this plan.
- No blockers. `70-FLIP-EVIDENCE.md` carries every key later waves need: `BASE_70_09`, `PRE_FLIP_SHA`, `PYTEST_RESULT_FLIP`, `MYPY_EXIT_FLIP`.

## Self-Check: PASSED

- `test -f pyproject.toml` and content verified via `git diff` — FOUND, matches expected two-line removal.
- `test -f .planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — FOUND.
- `test ! -e .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — CONFIRMED absent.
- `test -f .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-FLIP-EVIDENCE.md` — FOUND.
- `git log --oneline --all | grep -q 0224b5ea` — FOUND.
- `git log --oneline --all | grep -q 3778a318` — FOUND.
- `git log --oneline --all | grep -q 469069f0` — FOUND.
- Both tasks' `<acceptance_criteria>` and `<verify>` blocks re-run via scratch scripts immediately before each task's evidence commit: all passed (`ALL PASS` printed by both scripts).
- Plan-level `<verification>` re-confirmed: ignores gone in the same commit as the todo move (yes); repo-wide ruff-clean with rules enforced and gate quartet passing (yes).

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*

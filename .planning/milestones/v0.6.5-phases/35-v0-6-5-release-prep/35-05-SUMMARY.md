---
phase: 35-v0-6-5-release-prep
plan: 05
subsystem: release
tags: [release-evidence, handoff, release-prep, milestone-invariants]

# Dependency graph
requires:
  - phase: 35-01
    provides: "GATE-01 fixture Construct G + WR-02/WR-03/WR-04 gate-test assertions, closing the three test-side Phase 34 review Warnings"
  - phase: 35-02
    provides: "two pending-todo records for the deliberate deferrals (WR-01, release.yml rework)"
  - phase: 35-03
    provides: "pyproject.toml/README.md/uv.lock bumped to 0.6.5, typsphinx.__version__ confirmed"
  - phase: 35-04
    provides: "curated ## [0.6.5] CHANGELOG entry + tail link-block rollover"
provides:
  - "35-RELEASE-EVIDENCE.md: verbatim command-and-output evidence for ROADMAP Phase 35 SC#1 (freshness re-run), SC#2 (cited), SC#3, SC#4, and SC#5"
  - "35-HANDOFF.md: the standalone six-item publish/owner-manual checklist /gsd-complete-milestone executes"
affects: [gsd-complete-milestone, v0.6.6-scoping]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/35-v0-6-5-release-prep/35-RELEASE-EVIDENCE.md
    - .planning/phases/35-v0-6-5-release-prep/35-HANDOFF.md
  modified: []

key-decisions:
  - "Split the evidence file's write across the two task commits exactly at the SC#3/SC#4 boundary, so each task's commit carries only the sections that task's own action produced (Task 1: SC#1 freshness re-run + SC#2 citation + SC#3 seven live runs; Task 2: SC#4 mechanical invariants + SC#5 no-tag proof), rather than writing the whole file in one pass."
  - "Ran the optional gh CLI release-existence check (D-04/SC#5's acceptance criteria treat this as optional): gh was available and authenticated in this worktree, so `gh release view v0.6.5` was run rather than recorded as unrun, returning 'release not found' as independent corroboration of the two empty tag checks."
  - "Re-measured the merge-base commit count independently in Task 1 (62) and Task 2 (63) rather than reusing one number across both tasks, since the plan explicitly treats this count as a moving target that increments with the phase's own task commits, never as a stable fact."

patterns-established: []

requirements-completed: [REL-03]

coverage:
  - id: D1
    description: "SC#3: seven live runs (full pytest, black, ruff, mypy, isolated corpus-gate, tox -e docs-html, tox -e docs-pdf) transcribed verbatim, all green, docs/ working tree clean afterward"
    requirement: "REL-03"
    verification:
      - kind: integration
        ref: "uv run python -m pytest -q --tb=no -rf -> 649 passed, 1 skipped; uv run black --check . / ruff check . / mypy typsphinx/ all exit 0; uv run tox -e docs-html / docs-pdf both exit 0; git status --porcelain -- docs/ empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#4: milestone invariants (zero new runtime deps, no @preview bump, typsphinx/ confined to translator.py) asserted mechanically over the SHA-anchored range eb696bb..HEAD with a positive control"
    requirement: "REL-03"
    verification:
      - kind: unit
        ref: "git diff --numstat eb696bb..HEAD -- pyproject.toml / uv.lock both 1/1; git diff --numstat eb696bb..HEAD -- typsphinx/translator.py = 45/0 (positive control); git diff eb696bb..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ examples/ empty; uv run pytest tests/test_preview_version_sync.py -q -> 3 passed; git diff --name-only eb696bb..HEAD -- typsphinx/ -> typsphinx/translator.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC#5: no irreversible action taken - both no-tag checks empty, corroborated by an optional gh release query"
    requirement: "REL-03"
    verification:
      - kind: integration
        ref: "git tag -l v0.6.5 (empty); git ls-remote --tags origin v0.6.5 (empty); gh release view v0.6.5 --repo YuSabo90002/typsphinx -> 'release not found' (exit 1)"
        status: pass
    human_judgment: false
  - id: D4
    description: "35-HANDOFF.md stands alone with six owned, ordered checklist items covering the two-repository tagging cost (D-08) and the REL-03 close-side flip (D-10), an explicit not-done-by-design list, and a freshly re-run fence proof"
    requirement: "REL-03"
    verification:
      - kind: other
        ref: "grep -c '^### [1-6]\\.' 35-HANDOFF.md -> 6; grep -q REL-03/typsphinx-doc-translations/todos-pending all present; git diff --name-only -- .planning/REQUIREMENTS.md typsphinx/ docs/ .github/ -> empty"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-07-29
status: complete
---

# Phase 35 Plan 05: Release Evidence + Handoff Summary

**Proved the post-bump v0.6.5 tree green across seven live runs (including both D-12 docs dogfooding builds), proved the three milestone invariants mechanically over the SHA-anchored full milestone diff (merge-base `eb696bb02d135227d880c679fc909513fe6f7d19`) with a positive control, proved no irreversible action was taken (empty local/remote tag checks plus an optional `gh release view` corroboration), and wrote the standalone six-item `35-HANDOFF.md` checklist `/gsd-complete-milestone` will execute — discharging ROADMAP Phase 35 SC#3, SC#4, and SC#5.**

## Performance

- **Duration:** ~55 min (including worktree provisioning: `uv sync --extra dev --extra docs` + the NixOS `uv`/`ruff` `.venv/bin/` symlink shim, and two multi-minute build/test runs)
- **Started:** 2026-07-29 (after 35-01 through 35-04 merged)
- **Completed:** 2026-07-29
- **Tasks:** 3/3 completed
- **Files created:** 2 (`35-RELEASE-EVIDENCE.md`, `35-HANDOFF.md`); zero files modified

## Accomplishments

- **Task 1** opened `35-RELEASE-EVIDENCE.md` with SC#1 (freshness re-run of the `__version__` probe and the two version-sync guard tests), SC#2 (cited from `35-04-SUMMARY.md`, no dedicated mechanical guard exists for CHANGELOG prose), and the full SC#3 section: seven live runs transcribed verbatim — full pytest suite (`649 passed, 1 skipped`, matching the `35-RESEARCH.md` baseline exactly), `black --check .` / `ruff check .` / `mypy typsphinx/` all clean, the isolated `test_corpus_gate.py -m slow` confirmation (`1 passed, 1 skipped, 3 deselected`) with the stale-docstring correction recorded in prose (no marker filter is applied anywhere in this repo's config, so the plain full-suite run already exercises the corpus gate), and both D-12 docs dogfooding builds (`tox -e docs-html`, `tox -e docs-pdf`) exiting 0 and producing `docs/_build/pdf/typsphinx.pdf`, with `git status --porcelain -- docs/` confirmed empty afterward.
- **Task 2** re-measured the merge-base fresh (`eb696bb02d135227d880c679fc909513fe6f7d19`, unchanged from CONTEXT/RESEARCH) and the commit count fresh (63 at this task's execution — a number that had already moved from Task 1's own 62, purely from Task 1's own commit landing; recorded explicitly as a moving target, never the anchor). Asserted Invariant 1 (zero new runtime deps: `pyproject.toml` and `uv.lock` each numstat exactly `1 1`, full diffs shown, positive control on `typsphinx/translator.py` at `45 0` proving the diff machinery works) and Invariant 2 (no `@preview` bump: empty diff across all four declaration surfaces plus a green `test_preview_version_sync.py`). Added the scope note that `typsphinx/`'s milestone-range name-only diff lists exactly `typsphinx/translator.py`, differing from the v0.6.4 precedent (`typsphinx/` untouched) by design. Then proved SC#5 last: `git tag -l v0.6.5` and `git ls-remote --tags origin v0.6.5` both empty, plus an optional `gh release view v0.6.5` query (since `gh` was available and authenticated) returning `release not found` as independent corroboration.
- **Task 3** wrote `35-HANDOFF.md` standalone (readable with no access to CONTEXT/RESEARCH/the evidence file): what REL-03 required and what this phase satisfied vs. what remains structurally out of reach; six numbered, owned, ordered checklist items (PR merge → tag push → `typsphinx-doc-translations` second tag per D-08 → RTD `stable` owner-manual re-check → REL-03 close-side flip per D-10 → confirm the two pending todos plan 35-02 filed); a "Not done in this phase, by design" list of every untaken irreversible action; and a "Proof the fence held" section re-running both no-tag checks fresh, independent of Task 2's own run.

## Task Commits

Each task was committed atomically:

1. **Task 1: SC#3 live-run evidence + open 35-RELEASE-EVIDENCE.md** — `65edad1` (docs)
2. **Task 2: SC#4/SC#5 mechanical invariants + no-irreversible-action proof** — `81028d1` (docs)
3. **Task 3: write 35-HANDOFF.md publish/owner-manual checklist** — `d3f7848` (docs)

_No plan-metadata commit — worktree mode: STATE.md/ROADMAP.md updates are owned by the orchestrator after wave merge; this SUMMARY.md is committed separately below, per the orchestrator's instructions for this parallel executor._

## Files Created/Modified

- `.planning/phases/35-v0-6-5-release-prep/35-RELEASE-EVIDENCE.md` — new file, 513 lines across two commits: SC#1 (freshness re-run) + SC#2 (cited) + SC#3 (seven live runs, Task 1); SC#4 (mechanical invariants) + SC#5 (no-tag proof, Task 2)
- `.planning/phases/35-v0-6-5-release-prep/35-HANDOFF.md` — new file, 176 lines: six-item owned/ordered publish checklist, not-done-by-design list, fence proof

## Verdicts recorded

| SC | Verdict | Evidence location |
|----|---------|-------------------|
| SC#1 | MET | `35-RELEASE-EVIDENCE.md` § SC#1 (this plan's freshness re-run); full evidence in `35-03-SUMMARY.md` |
| SC#2 | MET | `35-RELEASE-EVIDENCE.md` § SC#2 (cited); full evidence in `35-04-SUMMARY.md` |
| SC#3 | MET | `35-RELEASE-EVIDENCE.md` § SC#3 — 7/7 live runs green |
| SC#4 | MET | `35-RELEASE-EVIDENCE.md` § SC#4 — both invariants PASS, scope note confirmed |
| SC#5 | MET | `35-RELEASE-EVIDENCE.md` § SC#5 — both no-tag checks empty, `gh` corroboration |

**Merge-base SHA:** `eb696bb02d135227d880c679fc909513fe6f7d19` (unchanged across the whole phase).
**Commit count at evidence time:** 62 (Task 1) → 63 (Task 2) — explicitly recorded as a moving
target incremented by this phase's own task commits, never as the SC#4 anchor (the SHA is the
anchor).

**No tag, no publish, no release, and no pull-request merge occurred during this plan's execution** —
confirmed by two independent empty `git tag -l v0.6.5` / `git ls-remote --tags origin v0.6.5` checks
(Task 2 and Task 3, at two separate moments) plus an optional `gh release view v0.6.5` query
returning "release not found".

## Decisions Made

- Split the evidence file's authorship across the two task commits at the SC#3/SC#4 boundary (rather
  than writing the whole document in one pass before either commit), so that Task 1's commit contains
  only what Task 1's own action produced and Task 2's commit contains only what Task 2's own action
  produced — keeping each commit's diff attributable to exactly one task, per this project's atomic-commit
  convention.
- Ran the optional `gh` CLI check for SC#5 since `gh auth status` confirmed an authenticated session
  in this worktree, rather than recording it as unrun (the plan permits either, contingent on `gh`'s
  availability).
- Independently re-measured the merge-base commit count in both Task 1 (62) and Task 2 (63) rather
  than reusing one number, since the plan's own explicit instruction is that this count is a moving
  target that must never be trusted from an earlier point in the same phase's own execution.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' automated verify blocks were independently
re-derived and checked against real command output; the sandbox refused a couple of compound
multi-`&&` bash one-liners as "too complex to verify worktree containment" (same friction
`35-04-SUMMARY.md` already documented), worked around by running each check as its own simple
command. This did not change what was verified, only the mechanics of verification. No package
installs, no source/test/workflow file touched by this plan, and no tag/publish/release action of any
kind.

## Issues Encountered

The worktree's `.venv/bin/ruff` (installed by `uv sync`) is a generic-linux ELF wheel whose
interpreter NixOS's stub-ld cannot execute (the standing project hazard documented in `CLAUDE.md` and
project memory). Resolved per the documented shim: symlinked the main tree's already-patched
`.venv/bin/ruff` binary (confirmed working, `ruff 0.15.20`) into this worktree's `.venv/bin/ruff`, and
symlinked the Nix-store `uv` binary into `.venv/bin/uv` for the same reason. Both shims were applied
before any test/lint/build command ran, and the full suite came back byte-identical to the main-tree
baseline (`649 passed, 1 skipped`), confirming the shim fully resolved the hazard for this plan's
evidence run.

## User Setup Required

None — no external service configuration required by this plan. `/gsd-complete-milestone` will
require the owner-manual RTD re-check named in `35-HANDOFF.md` item 4, but that is out of this plan's
own scope.

## Next Phase Readiness

- ROADMAP Phase 35 SC#3, SC#4, and SC#5 are discharged with verbatim evidence in
  `35-RELEASE-EVIDENCE.md`. Combined with SC#1/SC#2 (plans 35-03/35-04), all five of Phase 35's
  success criteria now carry recorded evidence.
- `35-HANDOFF.md` is the standalone input `/gsd-complete-milestone` reads to execute the publish
  half: PR merge, `v0.6.5` tag push (firing `release.yml`), the `typsphinx-doc-translations`
  second tag, the RTD owner-manual re-check, the REL-03 requirements-file flip, and confirming the
  two pending todos this phase filed.
- No tag exists locally or on `origin` as of this plan's completion — the repository's git-tag state
  is exactly as it was before Phase 35 began.
- No blockers for `/gsd-complete-milestone`.

---
*Phase: 35-v0-6-5-release-prep*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `.planning/phases/35-v0-6-5-release-prep/35-RELEASE-EVIDENCE.md`
- FOUND: `.planning/phases/35-v0-6-5-release-prep/35-HANDOFF.md`
- FOUND commit: `65edad1` (Task 1)
- FOUND commit: `81028d1` (Task 2)
- FOUND commit: `d3f7848` (Task 3)

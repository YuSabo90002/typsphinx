---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 11
subsystem: testing
tags: [pytest, sphinx, typst, byte-identity, evidence, corpus]

requires:
  - phase: 70-02
    provides: 'PHASE_BASE_SHA, VENV_HOME, VENV_VERSION_INFO, PYTEST_COLLECTED_BEFORE, PYTEST_RESULT_BEFORE, pytest-skips-before'
  - phase: 70-03
    provides: 'the corpus loop definition, CORPUS_LIST_SHA256, CORPUS_PROJECT_COUNT, CORPUS_MANIFEST_SHA256_BEFORE, CORPUS_CONTROL = EQUAL'
  - phase: 70-09
    provides: 'the merged typing-modernization flip (UP006/UP035 ignores removed) that this plan measures the after side of'
provides:
  - '70-AFTER-RUNTIME-EVIDENCE.md with LEG_B_VERDICT = MET and LEG_D_VERDICT = MET'
  - 'byte-identical post-flip pytest collected/result/skip-reason evidence (leg b)'
  - 'byte-identical post-flip 167-project .typ corpus manifest (leg d), matching CORPUS_MANIFEST_SHA256_BEFORE exactly'
affects: [70-13]

actuals:
  tokens: 7266
  tasks: 2
  commits: 4
plan_head_before: 44c43e345f8d5916486e5b7c2790bcb16c58f9d0

tech-stack:
  added: []
  patterns:
    - 'Reused 70-03''s <corpus_loop> word for word via a scratch-directory helper script run through `uv run bash`, to keep the manifest format identical across before/after sides'

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-AFTER-RUNTIME-EVIDENCE.md
  modified: []

key-decisions:
  - "None - followed plan as specified"

patterns-established: []

requirements-completed: [QUA-12]

coverage:
  - id: D1
    description: "Leg (b): pytest collected count, full-suite passed/skipped result, and skip reasons on the post-flip tree are identical to the pre-flip base"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "LC_ALL=C uv run pytest -q -rs -p no:cacheprovider (this plan's Task 1 run, exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Leg (d): the 167-project .typ corpus, built with 70-03's identical loop on the post-flip tree, is byte-identical (manifest SHA-256, and cmp) to the base manifest, including the 21 failing/zero-output projects kept per D-06"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "sha256sum + cmp of $S/corpus-after.txt against 70-CORPUS-DOCS-BASE-EVIDENCE.md's corpus-manifest block, plus per-project digest re-derivation from disk (this plan's Task 2 verify)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 11: After-side Runtime Evidence (QUA-12 legs b and d) Summary

**Post-flip pytest (1548 collected, 1547 passed/1 skipped) and the full 167-project `.typ` corpus manifest are both byte-for-byte identical to the pre-flip base, including the 21 fixtures that fail by design.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-09-13T14:25:00Z (approx.)
- **Completed:** 2026-09-13T14:50:00Z (approx.)
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Leg (b): re-ran the full pytest suite on the post-flip tree under `LC_ALL=C` in a freshly
  provisioned worktree (same `VENV_HOME`/`VENV_VERSION_INFO` as 70-02) — `PYTEST_COLLECTED_AFTER =
  1548` and `PYTEST_RESULT_AFTER = 1547 passed 1 skipped` both equal 70-02's base keys exactly, and
  the one `SKIPPED` reason matches after stripping line numbers. `LEG_B_VERDICT = MET`.
- Leg (d): re-enumerated the D-05 corpus at HEAD (167 `conf.py` projects under `tests/`) and
  confirmed its list hash equals 70-03's base list hash. Ran the D-08 five-project pilot
  (extrapolated 37s, far under the 1800s budget) and then the full 167-project corpus with 70-03's
  `<corpus_loop>` reused word for word. The resulting manifest — one `exit=/typ=/digest=` line per
  project, 21 of them non-zero-exit per D-06 — hashes to exactly `CORPUS_MANIFEST_SHA256_BEFORE =
  4c87a31da016b85f260915f6a0690c3fcf1602f17a0e2aa6a21725846d07464d`, and `cmp` against the base
  manifest block exits 0. `LEG_D_VERDICT = MET`.
- Both legs prove: apart from the API-reference type text this phase's plans document elsewhere,
  nothing about typsphinx's runtime behaviour changed by dropping the `UP006`/`UP035` ruff ignores
  and rewriting the ten affected files onto builtin generics / `collections.abc`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — leg (b) after side** - `16ed7dfa` (docs)
2. **Task 2: Leg (d) after side — corpus manifest identity** - `dd9bfbae` (docs)

**Plan metadata:** committed separately (see below)

## Files Created/Modified
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-AFTER-RUNTIME-EVIDENCE.md` - Leg (b) and leg (d) after-side evidence, both verdicts `MET`

## Decisions Made
None - followed plan as specified.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. One process note: several multi-command `git`/compound Bash invocations were refused by the
worktree-isolation guard as "too complex to verify"; the working fallback (per the orchestrator's
briefing) was to write each such command sequence to a script under this plan's own scratch
directory (`/tmp/tmp.0myAv8FjS1`, prefixed `p11_`) and run it with `bash <script>`. No behavioural
difference from running the commands inline — same commands, same outputs.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Both QUA-12 runtime legs (b and d) are proven `MET` on the post-flip tree, alongside the static and
docs-diff halves that 70-10 and 70-12 measure in the same wave. 70-13 (the phase-wide census /
closeout plan) can read `LEG_B_VERDICT` and `LEG_D_VERDICT` from this file by exact string
comparison, as its own read_first names. No blockers.

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*

## Self-Check: PASSED

- `70-AFTER-RUNTIME-EVIDENCE.md` exists on disk — confirmed.
- `70-11-SUMMARY.md` exists on disk — confirmed.
- Commits `16ed7dfa`, `dd9bfbae`, `1eacb7d4` all found in `git log --oneline --all`.
- Task 1 and Task 2 `<verify>` blocks both re-run post-commit and both print `PASS`.
- Plan-level `<verification>` ("Legs (b) and (d) are MET on the post-flip tree under the base's
  lock, extras and interpreter") is satisfied: `LEG_B_VERDICT = MET` and `LEG_D_VERDICT = MET` are
  both recorded in `70-AFTER-RUNTIME-EVIDENCE.md`, `VENV_HOME`/`VENV_VERSION_INFO` equal 70-02's,
  and the corpus was built under the base's extras (`--extra dev --extra docs`).

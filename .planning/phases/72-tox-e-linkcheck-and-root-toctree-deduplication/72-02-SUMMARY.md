---
phase: 72-tox-e-linkcheck-and-root-toctree-deduplication
plan: 02
subsystem: infra
tags: [tox, sphinx, linkcheck, qua-13]

requires: []
provides:
  - "[testenv:linkcheck] tox environment, shaped like docs-html, outside env_list"
  - "72-LINKCHECK-EVIDENCE.md proving a clean run at execution time"
affects: ["72-03 (DOC-24)", "72-05 (final re-run)"]

actuals:
  tokens: 1245
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns: ["tox environment shaped exactly like an existing sibling, added by pure append"]

key-files:
  created:
    - .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-LINKCHECK-EVIDENCE.md
  modified:
    - tox.ini

key-decisions:
  - "Run 1 passed SC#1 outright (95/95 working, 0 non-working rows, exit 0) — no D-01 re-run and no D-02 conf.py timing key were needed."

requirements-completed: [QUA-13]

coverage:
  - id: D1
    description: "tox.ini gains [testenv:linkcheck] shaped like docs-html (runner, extras, changedir, commands), staying outside env_list, added by pure 8-line append with a byte-identical base prefix."
    requirement: "QUA-13"
    verification:
      - kind: other
        ref: "72-LINKCHECK-EVIDENCE.md Task 1 automated verify (configparser assertion + tox list + numstat/prefix checks)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A clean uv run tox -e linkcheck run passes SC#1 by the live output.json census (95 total, 95 working, 0 non-working), transcribed with exit code, census keys and every non-working row."
    requirement: "QUA-13"
    verification:
      - kind: other
        ref: "72-LINKCHECK-EVIDENCE.md Task 2 automated verify (live output.json recount against recorded LINKCHECK_TOTAL/WORKING)"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-09-13
status: complete
---

# Phase 72 Plan 02: `tox -e linkcheck` Environment Summary

**Added `[testenv:linkcheck]` to `tox.ini` (shaped exactly like `docs-html`, outside `env_list`) and proved it passes clean on a fresh run — 95/95 links `working`, 0 non-transient or transient failures, no `conf.py` timing key needed.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-09-13T13:23:39Z
- **Completed:** 2026-09-13T13:35:00Z (approx)
- **Tasks:** 2
- **Files modified:** 2 (`tox.ini`, plus the new `72-LINKCHECK-EVIDENCE.md`)

## Accomplishments
- `[testenv:linkcheck]` landed in `tox.ini` by pure 8-line append (0 lines removed, base file a byte-identical prefix of the new file); `uv run tox list` shows it only under `additional environments:`, never under `default environments:`.
- One clean `uv run tox -e linkcheck` run from a removed `docs/_build/linkcheck` directory exited 0 with `output.json` reporting 95 rows, all `working` — the pass condition (total == working, at least 1 row) met on the very first run.
- `72-LINKCHECK-EVIDENCE.md` records the full evidence chain: head check/provisioning, the `tox.ini` diff and `tox list` output, run 1's census, the D-01/D-02/D-03 classification (nothing to classify — zero non-working rows), and the `LINKCHECK_VERDICT = PASS` verdict.

## Task Commits

Each task was committed atomically (plain `git commit`, per this plan's override — no GSD commit helper):

1. **Task 1: Tracer — add [testenv:linkcheck], prove it stays out of env_list, run it once clean** - `328f447e` (build, the tox.ini edit) + `9a03ced0` (docs, the evidence transcript)
2. **Task 2: Apply D-01/D-02/D-03 to the run census and record SC#1's verdict** - `f846e17d` (docs)

## Files Created/Modified
- `tox.ini` - gains `[testenv:linkcheck]` (8-line pure append, `runner = uv-venv-lock-runner`, `extras = docs`, `changedir = docs`, `commands = sphinx-build -b linkcheck source _build/linkcheck`); `env_list`, the `requires` pin and its comment are byte-identical to the base
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-LINKCHECK-EVIDENCE.md` - new; the full QUA-13/SC#1 evidence transcript

## Decisions Made
- Run 1 was the pass outright: 95 total rows, 95 `working`, 0 non-`working` rows, exit 0. There was nothing transient (D-01) or non-transient (D-03) to classify, so no second/third run and no `docs/source/conf.py` timing key (D-02) were needed. `CONF_LINKCHECK_KEYS = 0`, `docs/source/conf.py` is byte-identical to the base.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `tox -e linkcheck` exists, is shaped like `docs-html`, and passed at execution time (`LINKCHECK_VERDICT = PASS`, `LINKCHECK_TOTAL = 95`, `LINKCHECK_WORKING = 95`, `LINKCHECK_RUNS = 1`, `CONF_LINKCHECK_KEYS = 0`) — 72-03 (DOC-24) can now name this environment on the listing surfaces, and 72-05 can re-run it on the final tip.
- No blockers or concerns for downstream plans in this wave.

---
*Phase: 72-tox-e-linkcheck-and-root-toctree-deduplication*
*Completed: 2026-09-13*

## Self-Check: PASSED

- `tox.ini` exists on disk: FOUND
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-LINKCHECK-EVIDENCE.md` exists on disk: FOUND
- Commits `328f447e`, `9a03ced0`, `f846e17d` all found in `git log --oneline --all`
- Task 1 automated `<verify>` re-run: `ALL_TASK1_CHECKS_PASSED`
- Task 2 automated `<verify>` re-run: `ALL_TASK2_CHECKS_PASSED`

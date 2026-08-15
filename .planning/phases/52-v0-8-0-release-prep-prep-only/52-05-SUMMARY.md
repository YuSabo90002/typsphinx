---
phase: 52-v0-8-0-release-prep-prep-only
plan: 05
subsystem: release-prep
tags: [tox, sphinx, typstpdf, pytest, corpus-gate, docs]

requires:
  - phase: 52-v0-8-0-release-prep-prep-only (plan 01)
    provides: version bumped to 0.8.0 across pyproject.toml/README.md/uv.lock
  - phase: 52-v0-8-0-release-prep-prep-only (plan 02)
    provides: curated `## [0.8.0]` CHANGELOG entry
provides:
  - Local proof that both docs environments (docs-html, docs-pdf) build clean against the
    post-bump 0.8.0 tree, with the typstpdf-produced PDF measured as a real artifact
  - The full-corpus GATE-02 gate re-run and recorded PASSED (not skipped) against Sphinx's
    own doc/ corpus
  - A whole-suite local spot-check recorded honestly as non-authoritative (D-08)
  - An executed-versus-skipped register naming every environment that did not run and why
affects: [52-06, 52-07, release-prep-verification, complete-milestone]

actuals:
  tokens: 3738
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Skip-vs-pass discipline: corpus gate transcripts always capture per-test PASSED/SKIPPED via -v, never inferred from a bare pass/fail summary line"

key-files:
  created:
    - .planning/phases/52-v0-8-0-release-prep-prep-only/52-GREEN-TREE-EVIDENCE.md
  modified: []

key-decisions:
  - "No local run is presented as authority for pytest/lint/type/matrix (D-08) -- only the dispatched CI run plan 52-04 collects carries that authority; this plan's whole-suite run is explicitly labelled a spot-check"
  - "The corpus gate PASSED for real (network reachable, real clone of Sphinx v9.1.0 doc/), so no human_needed marker was required -- recorded per-test PASSED status per pitfall 4's discipline rather than assumed from a summary line"

patterns-established: []

requirements-completed: []
# REL-07 stays open per plan frontmatter and 52-RESEARCH.md Pitfall 5 -- it closes only at
# /gsd-complete-milestone, not in this phase-prep plan.

coverage:
  - id: D1
    description: "tox -e docs-html and tox -e docs-pdf both build clean against the post-bump 0.8.0 tree; docs-pdf produces its PDF through typsphinx's own typstpdf builder"
    requirement: REL-07
    verification:
      - kind: e2e
        ref: "uv run --extra dev tox -e docs-html (exit 0, build succeeded)"
        status: pass
      - kind: e2e
        ref: "uv run --extra dev tox -e docs-pdf (exit 0, build succeeded, PDF generated and measured 2,614,546 bytes / 128 pages / 0.8.0 on title page via pypdf)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Full-corpus -b typstpdf GATE-02 gate re-run against the post-bump tree, PASSED-vs-SKIPPED distinction preserved (not conflated)"
    requirement: REL-07
    verification:
      - kind: e2e
        ref: "tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -v (PASSED, JUnit failures=0 errors=0 skipped=1)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Whole-suite local pytest spot-check recorded honestly as non-authoritative per D-08"
    verification:
      - kind: integration
        ref: "uv run pytest tests/ -q --junit-xml=... (1170 passed, 5 skipped, failures=0, errors=0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Executed-versus-skipped register names the two NOT-RUN environments (bare tox, tox -e py312) with cause and filed-todo citation"
    verification:
      - kind: other
        ref: "52-GREEN-TREE-EVIDENCE.md ## Executed versus skipped table"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-08-15
status: complete
---

# Phase 52 Plan 05: Local Green-Tree Evidence (Docs Builds + Full-Corpus Gate) Summary

**Both `tox -e docs-html`/`tox -e docs-pdf` build clean on the post-bump 0.8.0 tree (128-page,
2,614,546-byte typstpdf PDF measured), and the full-corpus GATE-02 gate ran for real and
PASSED — recorded with its per-test status in words rather than inferred from a summary line.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-15T01:05:00Z (approx.)
- **Completed:** 2026-08-15T01:10:43Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- `uv run --extra dev tox -e docs-html` and `uv run --extra dev tox -e docs-pdf` both exit 0
  against the post-bump `0.8.0` tree, each ending `build succeeded` / `<env>: OK`.
- The `typstpdf`-produced PDF was measured, not assumed: `docs/_build/pdf/typsphinx.pdf`,
  2,614,546 bytes, 128 pages, first-page text `typsphinx / YuSabo / 0.8.0 / 1` extracted via
  `pypdf` — confirming both the artifact's realness and that the version bump reached the
  rendered document metadata.
- The full-corpus `-b typstpdf` GATE-02 gate (`tests/test_corpus_gate.py::TestCorpusRenderGate
  ::test_corpus_compiles_with_no_fatal_error`) was re-run with `-v` and a JUnit XML and recorded
  **PASSED**, in words — not inferred from a `0 failed` summary line, which Pitfall 4 warns can
  mask a skip. Network was reachable in this worktree; a real shallow clone of Sphinx's own
  `v9.1.0` `doc/` tree compiled fatal-free through `typsphinx`'s own `typstpdf` builder.
- A whole-suite local spot-check (`1170 passed, 5 skipped`, `failures="0"`, `errors="0"`) is
  recorded explicitly as a spot-check, not authority — pytest/lint/type/matrix authority stays
  with the dispatched CI run plan 52-04 collects, per D-08.
- An `## Executed versus skipped` table names every environment run or not run: `docs-html` RAN,
  `docs-pdf` RAN, the corpus gate RAN (PASSED), the local suite RAN (spot-check only), a bare
  `tox` NOT RUN (lint's `ruff` ELF incompatibility on NixOS), and `tox -e py312` NOT RUN (the
  same NixOS ELF class for a standalone-CPython download) — both citing
  `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` by filename.

## Task Commits

Each task was committed atomically:

1. **Task 1: Run both docs builds against the post-bump tree and record the produced PDF** -
   `4c371cc9` (docs)
2. **Task 2: Re-run the full-corpus GATE-02 gate and record executed-versus-skipped honestly** -
   `d9e6e352` (docs)

_No plan-metadata commit is made by this executor — per this plan's parallel-execution
instructions, STATE.md/ROADMAP.md updates are owned by the orchestrator after the wave merges._

## Files Created/Modified
- `.planning/phases/52-v0-8-0-release-prep-prep-only/52-GREEN-TREE-EVIDENCE.md` - local half of
  SC#3: both docs-build transcripts, the measured PDF, the full-corpus gate transcript and JUnit
  attributes, the suite spot-check, and the executed-versus-skipped register.

## Decisions Made
- Recorded the corpus gate's PASSED status explicitly in words per the plan's Pitfall 4
  discipline, rather than relying on the pytest summary line, even though in this run the gate
  did pass for real (network reachable) — the distinction matters regardless of which way the
  run lands.
- Cited the filed `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` todo by filename in
  both NOT-RUN table rows (bare `tox` and `tox -e py312`), rather than only the first, since both
  share the identical NixOS ELF-loader root cause.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' automated `<verify>` commands and every
acceptance criterion were run and passed as specified; no auto-fix, no architectural change, and
no scope beyond the single `52-GREEN-TREE-EVIDENCE.md` artifact this plan's `files_modified`
declares.

## Issues Encountered

None. The worktree provisioned cleanly via `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync
--extra dev`, every command ran via `uv run` per `CLAUDE.md`'s worktree-isolated-execution
guidance, and both the docs builds and the corpus gate completed without retries.

## Known Stubs

None. This plan produces one read-only evidence artifact; no application code was touched and no
stub/placeholder content was introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

The local half of ROADMAP Phase 52 SC#3 is discharged: both docs builds are green on the
post-bump tree, the `typstpdf`-produced PDF is measured, and the full-corpus GATE-02 gate's
PASSED status is recorded honestly and distinctly from a skip. Combined with the dispatched CI
run plan 52-04 collects (the authority for pytest/lint/type/matrix per D-08), SC#3 is fully
evidenced once both plans' artifacts are read together. REL-07 stays open — it closes only at
`/gsd-complete-milestone`, per this plan's frontmatter and 52-RESEARCH.md Pitfall 5. No
irreversible action was taken: no `v0.8.0` tag exists locally or on `origin` (re-verified at both
task boundaries), and `git diff --name-only -- tests/ typsphinx/ tox.ini pyproject.toml` produces
no output.

---
*Phase: 52-v0-8-0-release-prep-prep-only*
*Completed: 2026-08-15*

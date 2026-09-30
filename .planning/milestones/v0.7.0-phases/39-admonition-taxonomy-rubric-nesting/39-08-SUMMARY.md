---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 08
subsystem: testing
tags: [test-census, corpus-gate, phase-close, requirements-reconciliation, gentle-clues]

# Dependency graph
requires:
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 05)
    provides: "the five bucket-routing fixes and the sphinx.locale.admonitionlabels catalog title source, whose blast radius this plan re-measures"
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 06)
    provides: "the rubric save-slot rename and separator-double-count fix, whose golden.typ regeneration this plan cross-checks"
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 07)
    provides: "39-ADM04-SIGNOFF.md, the only source this plan reads ADM-04's outcome from"
provides:
  - "39-TEST-CENSUS.md: the re-measured (not recalled) exact-string migration census, reconciled against the discussion-time (39-CONTEXT.md D-14) and planning-time (39-RESEARCH.md) censuses with no disagreement found"
  - "39-GATE-EVIDENCE-04.md: verbatim evidence that the full-corpus gate actually ran (not skipped), the full suite/fast-tier/lint-type-trio are green, the docs dogfood build succeeded (91 pages, +1 from 90 pre-phase, explained), the milestone invariants held, and all five ROADMAP success criteria reconcile against named artifacts"
  - "REQUIREMENTS.md's five ADM entries flipped to their earned status, with ADM-04's status quoted verbatim from 39-ADM04-SIGNOFF.md rather than inferred"
affects: [40-citations-full-round-trip]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Worktree-mode STATE.md/ROADMAP.md deferral: the specific edits this plan's Task 3 would have made directly are recorded in 39-GATE-EVIDENCE-04.md's own 'STATE.md and ROADMAP.md — worktree-mode deferral' section for the orchestrator's post-merge close-phase step, rather than applied by this worktree agent"

key-files:
  created:
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-TEST-CENSUS.md
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-04.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "STATE.md and ROADMAP.md were NOT edited directly by this worktree agent, despite the plan's Task 3 action text instructing edits to both -- the orchestrator's own worktree-mode instructions (<parallel_execution>, <objective>) explicitly override the plan's authoring-time assumption of sequential/main-tree execution. The specific STATE.md edit (retiring three now-answered Operator Next Steps notes and what to replace them with) is recorded in 39-GATE-EVIDENCE-04.md for the orchestrator's post-merge step to apply. ROADMAP.md needed no wording correction (SC#3 already reads as the D-12 invariance guard) -- only its plan-progress counter, which is the orchestrator's own roadmap.update-plan-progress step."
  - "The folded pending todo (2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md) was left in .planning/todos/pending/ rather than moved to completed/, per this project's standing worktree-cleanup-deletion-guard convention (a git mv from inside a worktree registers as a deletion, which worktree.cleanup-wave blocks unconditionally). Its resolves_phase: 39 field and the closing commit (db70c2a) are recorded in 39-GATE-EVIDENCE-04.md for the orchestrator's post-merge close_phase_todos step."
  - "Both uv AND ruff needed NixOS-sandbox symlink shims this session, not ruff alone -- a fresh worktree's own uv sync-installed .venv/bin/uv is also a generic-linux ELF binary that fails under the NixOS stub loader, and it shadows the correct Nix-store uv on PATH for the ~45 tests that shell out via subprocess.run(['uv', 'run', 'sphinx-build', ...]). This is a newly-discovered refinement to the project's existing nixos-sandbox-test-env memory note, recorded in 39-GATE-EVIDENCE-04.md for STATE.md's next Operator Next Steps."

requirements-completed: [ADM-01, ADM-02, ADM-03, ADM-04, ADM-05]

coverage:
  - id: D1
    description: "The exact-string blast radius re-measured against the finished tree and recorded per file with reasons, reconciled against both the discussion-time and planning-time censuses -- no disagreement found in either direction"
    requirement: "ADM-01"
    verification:
      - kind: other
        ref: "39-TEST-CENSUS.md's own reproducible grep/git-log commands, re-run live during authoring"
        status: pass
    human_judgment: false
  - id: D2
    description: "The full-corpus real-render gate actually ran (not skipped) and was green: resolved tag v9.1.0, 14.17s, PASSED"
    requirement: "ADM-05"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_corpus_gate.py -m slow -v"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full suite unfiltered green (763 passed, 1 skipped, 0 failed), fast tier green (735 passed, 0 failed), version-sync test green by name, lint/type trio clean, docs dogfood build exits 0"
    requirement: "ADM-03"
    verification:
      - kind: unit
        ref: "uv run pytest (unfiltered) -- 763 passed, 1 skipped"
        status: pass
      - kind: unit
        ref: "uv run pytest -m \"not slow\" -- 735 passed, 29 deselected"
        status: pass
      - kind: unit
        ref: "uv run pytest tests/test_preview_version_sync.py -x -- 3 passed"
        status: pass
      - kind: other
        ref: "uv run black --check . && uv run ruff check . && uv run mypy typsphinx/ -- all clean"
        status: pass
      - kind: integration
        ref: "uv run tox -e docs-pdf -- exit 0, PDF generated, 91 pages"
        status: pass
    human_judgment: false
  - id: D4
    description: "Milestone invariants re-checked by command at close: zero new runtime dependencies, @preview package count stays at four, gentle-clues pin unchanged at 1.3.1"
    requirement: "ADM-02"
    verification:
      - kind: other
        ref: "git diff pyproject.toml (runtime deps unchanged) + grep @preview across writer.py/template_engine.py/templates/base.typ (4 packages, pin 1.3.1 unchanged)"
        status: pass
    human_judgment: false
  - id: D5
    description: "All five ROADMAP success criteria reconciled with named discharging artifacts and commands; REQUIREMENTS.md's five ADM entries flipped to their earned status, with ADM-04 read verbatim from the owner's sign-off"
    requirement: "ADM-04"
    verification:
      - kind: manual_procedural
        ref: "39-ADM04-SIGNOFF.md quoted verbatim in 39-GATE-EVIDENCE-04.md's SC#4 reconciliation section -- ADM-04 MET on icon-shape grounds, uniform luminance recorded as an explicit caveat"
        status: pass
    human_judgment: true
    rationale: "ADM-04 is REQUIREMENTS.md's own [V]-marked (human-only visual UAT) requirement; its status is read from the owner's sign-off, never inferred from the artifact's existence, per this plan's own must_haves.prohibitions."

# Metrics
duration: 40min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 08: Phase-Close Test Census, Corpus Gate Re-Run, and Requirement Reconciliation Summary

**Re-measured the phase's exact-string blast radius against the finished tree (5 edited assertions/4 renamed functions in `test_admonitions.py`, 2 edited/1 untouched in `test_topics.py`, 0 edited in `test_pdf_render_gate.py` and the five rubric-touching modules — all matching both earlier censuses exactly), ran the full-corpus gate for real (not skipped, tag `v9.1.0`, 14.17s, PASSED), confirmed all three milestone invariants held by command, and reconciled all five ROADMAP success criteria against named artifacts — including reading ADM-04's MET verdict verbatim from the owner's sign-off rather than inferring it.**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-08-02T12:16:26+09:00
- **Tasks:** 3
- **Files modified:** 3 (2 created: `39-TEST-CENSUS.md`, `39-GATE-EVIDENCE-04.md`; 1 modified: `.planning/REQUIREMENTS.md`)

## Accomplishments

- **Re-measured, not recalled, the exact-string migration census.** Ran repo-wide greps over
  `tests/` for every gentle-clues box-open form and every admonition type name, plus `git log`/`git
  diff` against the true pre-Phase-39 baseline (`8406b8a`), and recorded every command and its raw
  output in `39-TEST-CENSUS.md`. Every count matched both `39-CONTEXT.md` D-14's discussion-time raw
  counts (18/3/4 clue-call assertions across the three admonition-emission files) and
  `39-RESEARCH.md`'s planning-time refined predictions (5 edited/4 renamed in `test_admonitions.py`;
  2 edited/1 untouched in `test_topics.py`; 0 edited in `test_pdf_render_gate.py`) — no disagreement
  found in either direction, which the census records explicitly as a finding in its own right.
  Cross-checked against `39-05-SUMMARY.md`/`39-06-SUMMARY.md`'s own recorded tallies, also matched.
  Measured live all three D-05 accepted regressions (`ja` `note`/`tip` title changes, `seealso`
  English casing) via a real `sphinx.locale.init(["ja"])` catalog load.
- **Ran the full-corpus gate for real.** `uv run pytest tests/test_corpus_gate.py -m slow -v`
  actually executed (resolved tag `v9.1.0`, cache already warm at
  `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`, no network fetch needed) and PASSED in 14.17s —
  not recorded as a pass on the strength of a skip. The one SKIP in that run's output is an
  unrelated, explicitly env-gated diagnostic test, not the corpus gate itself.
- **Ran every other closing gate and recorded verbatim results in `39-GATE-EVIDENCE-04.md`:** full
  suite unfiltered (763 passed, 1 skipped, 0 failed — 764 total, matching the recorded reference
  baseline), fast tier (735 passed, 29 deselected), `test_preview_version_sync.py` by name (3
  passed), the lint/type trio (black/ruff/mypy all clean), and the project's own `docs-pdf` dogfood
  build (exit 0, 91-page PDF generated — +1 from the 90-page post-Phase-38 baseline, explained as a
  consequence of the D-11/D-13 rubric mechanisms partially offsetting, since `docs/source/` contains
  no literal admonition/rubric directives and was itself untouched this whole phase).
- **Confirmed all three milestone invariants held, by command, not assumption:** the runtime
  dependency array is byte-unchanged (only `pillow` was added, to `[dev]`); the `@preview` import
  count stays at four across all three lockstep sites; the pinned gentle-clues version is still
  `1.3.1` everywhere it is declared.
- **Reconciled all five ROADMAP success criteria** with their discharging artifacts and commands in
  `39-GATE-EVIDENCE-04.md`. SC#3 was confirmed to already read as the D-12 invariance guard (citing
  Phase 36's own SC#3 precedent) — no wording correction was needed, since the roadmap was authored
  this way from the start. SC#4's outcome was quoted verbatim from `39-ADM04-SIGNOFF.md` §"Outcome"
  ("ADM-04 is MET... the distinguishing signal is the icon shape... Explicit recorded caveat:
  luminance is uniform and carries no distinguishing signal") — never inferred from the artifact's
  existence, and the sign-off's own superseded first-pass framing was explicitly NOT let leak into
  this reconciliation.
- **Flipped `REQUIREMENTS.md`'s five ADM entries** to their earned status (all complete), with
  ADM-04's checkbox entry carrying its own quoted MET-on-icon-shape-grounds/luminance-caveat text so
  a future reader of REQUIREMENTS.md alone (without opening the SIGNOFF) sees the accurate, nuanced
  outcome.
- **Closed both folded defects by reference.** The pending todo naming this phase as its resolver
  (`2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md`) already carries
  `resolves_phase: 39`; its closing commit (`db70c2a`, 39-06 Task 1) is now named in
  `39-GATE-EVIDENCE-04.md` for the orchestrator's post-merge move to `todos/completed/` (this
  worktree agent deliberately did not `git mv` it itself, per the project's own
  worktree-cleanup-deletion-guard convention). The rubric docstring's deferred-repair sentence is
  confirmed gone (`grep -c "not fixed in this plan" typsphinx/translator.py` returns `0`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-measure and record the exact-string migration census** - `1b17d87` (test)
2. **Task 2: Run the full-corpus gate for real, the full suite, and the docs dogfood build** - `2c544b1` (test)
3. **Task 3: Reconcile the roadmap and requirement records with what each requirement reached** - `bc7e28b` (docs)

_Note: no separate plan-metadata commit is created in worktree-isolation mode — STATE.md/ROADMAP.md
are updated by the orchestrator after merge; this SUMMARY.md is committed by the harness's
post-return commit step._

## Files Created/Modified

- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-TEST-CENSUS.md` — the re-measured
  exact-string migration census (13-row table, reproducible commands, D-05 accepted regressions,
  full reconciliation against the discussion-time and planning-time censuses, and a cross-check
  against 39-05-SUMMARY.md/39-06-SUMMARY.md's own tallies). One factual correction applied
  post-authoring (row 3's function lives in `TestTopicLineBlockRenderGate`, not
  `TestAdmonitionPdfRenderGate`), discovered and fixed while re-verifying Task 3's own commands.
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-04.md` — verbatim
  evidence for every closing gate (corpus gate, full suite, fast tier, version-sync, lint/type trio,
  docs dogfood build, milestone invariants) plus the full SC#1-SC#5 reconciliation, the two folded
  defects' disposition, and the STATE.md/ROADMAP.md edits recorded for the orchestrator.
- `.planning/REQUIREMENTS.md` — ADM-01..ADM-05 checkboxes flipped to `[x]`, ADM-04's entry extended
  with its earned status quoted from the sign-off, and the traceability table's five ADM rows
  updated from `Pending` to `Complete`.

## Decisions Made

- **STATE.md and ROADMAP.md were not edited directly**, despite the plan's own Task 3 action text
  instructing edits to both — the orchestrator's explicit worktree-mode harness instructions
  (`<parallel_execution>`, `<objective>`) take precedence over the plan's authoring-time assumption
  of sequential execution. The specific STATE.md edit this plan's Task 3 would have made (retiring
  three now-answered Operator Next Steps bullets, and what to replace them with, including a
  newly-discovered `uv` NixOS-shim refinement) is recorded verbatim in `39-GATE-EVIDENCE-04.md`'s own
  "STATE.md and ROADMAP.md — worktree-mode deferral" section for the orchestrator's post-merge
  close-phase step to apply.
- **The folded pending todo was left in `todos/pending/`**, not moved to `todos/completed/`, per this
  project's standing worktree-cleanup-deletion-guard convention (a `git mv` from inside a worktree
  registers as a deletion, which `worktree.cleanup-wave` blocks unconditionally with no bypass) —
  identical to `38-TEST-CENSUS.md`'s own precedent for the same situation.
- **Both `uv` and `ruff` required NixOS-sandbox symlink shims this session**, not `ruff` alone. A
  fresh worktree's own `uv sync`-installed `.venv/bin/uv` is also a generic-linux ELF binary that
  fails under the NixOS stub loader, and — because it is earlier on `PATH` than the correct
  Nix-store `uv` — it silently breaks every test that shells out via
  `subprocess.run(["uv", "run", "sphinx-build", ...])`. Measured directly: 45 tests failed with exit
  127 before the second shim, all 45 passed after it. This is a genuine refinement to the project's
  existing `nixos-sandbox-test-env` memory note (which documented only the `ruff` half), recorded
  for STATE.md's next Operator Next Steps.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a test-function-attribution error discovered while re-verifying Task 3's own reconciliation commands**
- **Found during:** Task 3 (re-running the SC#2 command cited in the gate-evidence draft)
- **Issue:** `39-TEST-CENSUS.md` row 3 and the SC#2 reconciliation in `39-GATE-EVIDENCE-04.md` both
  cited `tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitiontitleregression_multichild`
  — this node id does not exist; `pytest -k AdmonitionTitleRegression --collect-only` showed the
  function actually lives in a different class in the same file, `TestTopicLineBlockRenderGate`.
- **Fix:** Corrected the class name in both files (census row 3 and the gate-evidence SC#2 command),
  re-ran the corrected command to confirm it passes.
- **Files modified:** `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-TEST-CENSUS.md`,
  `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-04.md`
- **Verification:** `uv run pytest "tests/test_pdf_render_gate.py::TestTopicLineBlockRenderGate::test_admonitiontitleregression_multichild" -v` — 1 passed.
- **Committed in:** `bc7e28b` (Task 3 commit).

**2. [Rule 3 - Blocking, non-package] NixOS `uv` ELF-binary shim required before any subprocess-shelling test could run**
- **Found during:** Task 2 (initial `uv run pytest -m "not slow"` run)
- **Issue:** 45 integration/render-gate tests failed with `subprocess.CalledProcessError`, exit 127,
  `Could not start dynamically linked executable: uv` — the worktree's own `uv sync`-installed
  `.venv/bin/uv` is a generic-linux ELF binary the NixOS stub loader cannot exec, and it shadows the
  correct Nix-store `uv` on `PATH` for the subprocess child each of these tests spawns.
- **Fix:** Symlinked the Nix-store `uv` (resolved via `command -v uv` before any shim existed) to
  `.venv/bin/uv`, mirroring the pre-existing `ruff` shim this worktree already needed per the
  project's standing memory note.
- **Files modified:** none (environment-only; `.venv/` is gitignored).
- **Verification:** `uv run pytest -m "not slow" -q` — 735 passed, 0 failed (was 45 failed before the
  shim).
- **Committed in:** not applicable (no code change; recorded in `39-GATE-EVIDENCE-04.md` as a
  newly-discovered environment note for STATE.md's next Operator Next Steps).

---

**Total deviations:** 2 auto-fixed (1 Rule 1 accuracy fix in this plan's own documentation, 1 Rule 3
non-package environment shim).
**Impact on plan:** Zero impact on scope or correctness. Neither deviation touched `typsphinx/` or
`tests/` — confirmed by `git diff --stat 6f891563b835972a9c0179bb7fe1dfb917fb4554..HEAD -- typsphinx/ tests/`
being empty for this whole plan's three commits.

## Issues Encountered

None beyond the two deviations documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Phase 39 is fully closed.** All five requirements (ADM-01..ADM-05) are complete;
  `REQUIREMENTS.md` reflects this. All five ROADMAP success criteria are reconciled against real,
  named artifacts. The full-corpus gate ran green for real. Milestone invariants held. Both folded
  defects are closed by reference.
- **Phase 40 (Citations — Full Round Trip) is next**, per `ROADMAP.md`. It is structurally
  independent of Phase 39's admonition/rubric work and keeps the milestone's one classic
  `TypstError`-RED exception (CIT-01) — no blocker from this phase.
- **For the orchestrator's post-merge close-phase step:** apply the STATE.md Operator Next Steps
  edit recorded in `39-GATE-EVIDENCE-04.md`'s "STATE.md and ROADMAP.md — worktree-mode deferral"
  section (retire three now-answered bullets, replace with the Phase 39 close summary + the newly
  discovered `uv` NixOS-shim note + a Phase 40 pointer); move the folded pending todo to
  `todos/completed/` (it already carries `resolves_phase: 39` and its closing commit `db70c2a` is
  named); flip `ROADMAP.md`'s Phase 39 plan-progress counter to `8/8` and check its 39-08 plan-list
  entry.

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-TEST-CENSUS.md`
- FOUND: `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-04.md`
- FOUND: `.planning/REQUIREMENTS.md`
- FOUND: `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-08-SUMMARY.md`
- FOUND commit `1b17d87` (Task 1: test census)
- FOUND commit `2c544b1` (Task 2: closing gates evidence)
- FOUND commit `bc7e28b` (Task 3: requirement reconciliation)

---
phase: 44-typst-documents-default-derivation-builder-input-hardening
plan: 05
subsystem: build
tags: [sphinx, typst, builder, config, collision-guard, gap-closure]

# Dependency graph
requires:
  - phase: 44-typst-documents-default-derivation-builder-input-hardening (plans 01-04)
    provides: "The CONF-08 derived typst_documents default (_default_typst_documents) and the BLD-01 non-str-docname guard, whose interaction CR-01 identified as a reachable zero-configuration collision hazard"
provides:
  - "A collision guard inside TypstBuilder._resolve_output_stem rejecting any resolved target name whose directory-qualified effective path equals another real docname in self.env.found_docs, or the reserved _template basename"
  - "Four real sphinx-build subprocess gate scenarios (docname collision x reserved-template clobber) x (derived-default path x explicit typst_documents path) in tests/test_typst_documents_collision_gate.py"
  - "Three unit-level edge tests in tests/test_builder_output_stem.py, including the getattr(found_docs) regression guard for envs without a found_docs attribute"
  - "44-GATE-EVIDENCE-05.md: the RED-before-GREEN record for all four scenarios, the repo-wide regression-boundary re-measurement, and the two-item gap-closure verdict"
affects: [45-documentation-currency-carried-hygiene]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 14240
  tasks: 3
  commits: 7

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Collision guard lives at the single normalization site (_resolve_output_stem) that both write_doc and finish already call, so -b typst and -b typstpdf can never disagree about the resolved filename"
    - "Fallback is always the docname itself (D-02's existing degenerate-target convention), never a synthesized name — no -1/-2 suffix, no hash"
    - "getattr(self.env, 'found_docs', None) or set() mirrors the existing toctree_includes idiom in the same file, so a builder whose env has no found_docs still resolves normally"

key-files:
  created:
    - tests/test_typst_documents_collision_gate.py
    - tests/fixtures/derived_docname_collision_gate/{conf.py,index.rst,chapter1.rst}
    - tests/fixtures/derived_template_collision_gate/{conf.py,index.rst}
    - tests/fixtures/explicit_docname_collision_gate/{conf.py,index.rst,chapter1.rst}
    - tests/fixtures/explicit_template_collision_gate/{conf.py,index.rst}
    - .planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-05.md
  modified:
    - typsphinx/builder.py
    - tests/test_builder_output_stem.py

key-decisions:
  - "The collision comparison is made on the directory-qualified effective path (via _directory_preserving_relpath), never the bare stem — a nested docname's stem is re-prefixed with its own directory downstream, so comparing the bare stem would produce false positives/negatives"
  - "The reserved _template basename check is a root-level equality test only, because _write_template_file() writes _template.typ unconditionally at the outdir root and never nested"
  - "WARNING severity is kept (not lowered), matching D-03's precedent, so -W builds still fail on the collision"
  - "The warning fires twice on a -b typstpdf build (once from write_doc, once from finish) because both call the single normalization site — this is accepted, matching the pre-existing D-06/D-07 warnings' behavior, and tests assert presence rather than exact count"

patterns-established:
  - "Repo-wide regression-boundary re-measurement via static ast parsing of every conf.py's typst_documents literal entries, rather than trusting a planning-time census number"

requirements-completed: [CONF-08, BLD-01]

coverage:
  - id: D1
    description: "A typst_documents target name (derived from project, or explicit) that collides with a real docname's own output path falls back to the docname with a console WARNING, instead of silently overwriting that document's output"
    requirement: CONF-08
    verification:
      - kind: integration
        ref: "tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_docname_collision_keeps_both_documents"
        status: pass
      - kind: integration
        ref: "tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_docname_collision_produces_pdf"
        status: pass
      - kind: integration
        ref: "tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_explicit_target_docname_collision_keeps_both_documents"
        status: pass
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_falls_back_on_docname_collision"
        status: pass
    human_judgment: false
  - id: D2
    description: "A typst_documents target name that collides with the reserved _template.typ infrastructure file falls back to the docname, so the shared #let project definition every master imports survives"
    requirement: CONF-08
    verification:
      - kind: integration
        ref: "tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_template_collision_preserves_shared_template"
        status: pass
      - kind: integration
        ref: "tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_explicit_target_template_collision_preserves_shared_template"
        status: pass
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_falls_back_on_reserved_template_name"
        status: pass
    human_judgment: false
  - id: D3
    description: "A builder whose env exposes no found_docs attribute at all still resolves the output stem normally, without raising AttributeError (regression guard for mock/test-shaped envs)"
    verification:
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_tolerates_env_without_found_docs"
        status: pass
    human_judgment: false

# Metrics
duration: 23min (active execution across two sessions, separated by a human checkpoint pause after the tracer task)
completed: 2026-08-04
status: complete
---

# Phase 44 Plan 05: CR-01 Gap Closure — typst_documents Collision Guard Summary

**A `typst_documents` target name that slugifies onto an existing docname (or the reserved `_template.typ`) now falls back to the docname with a console WARNING instead of silently destroying content or hard-failing the PDF compile — closing the single gap 44-VERIFICATION.md scored FAILED.**

## Performance

- **Duration:** ~23 min of active execution (7 commits between 16:38 and 17:01 JST), interrupted by a human checkpoint pause after Task 1's tracer commit
- **Started:** 2026-08-04T16:38:39+09:00 (RED commit for Task 1)
- **Completed:** 2026-08-04T17:01:10+09:00 (final evidence commit for Task 3)
- **Tasks:** 3 of 3 completed
- **Files modified:** 14 (1 production file, 2 test modules, 8 new fixture files, 1 new evidence file, plus the SUMMARY itself)

## Accomplishments

- Added a collision guard to `TypstBuilder._resolve_output_stem` (the single normalization site both `write_doc` and `finish` already call): a resolved target whose directory-qualified effective path equals a real docname in `self.env.found_docs`, or the reserved `_template` basename, now emits a `logger.warning` and falls back to the docname itself — never a synthesized name, never a silently lowered severity.
- Closed both `missing:` items from `44-VERIFICATION.md` with real `sphinx-build` subprocess evidence across all four scenarios: (docname collision × reserved-template clobber) × (derived-default path × explicit `typst_documents` path).
- Re-proved RED-before-GREEN for every new test by reverting `typsphinx/builder.py` to the pre-fix commit and back, with the restore proved by `git status --porcelain` producing no output.
- Re-measured (never trusted) the repo-wide pre-existing-collision scan: the only two hits are this plan's own deliberately-colliding gate fixtures; every other `conf.py` in the repository is collision-free, confirming the planner's zero baseline for the pre-existing tree.
- Re-ran the full phase gate (pytest full suite, the slow corpus gate by name, black/ruff/mypy) at or above the phase's own recorded `855 passed, 1 skipped` baseline — landed at `863 passed, 1 skipped` (exactly the 8 tests this plan added), with zero new runtime dependency and the typing-import modernization prohibition still honored.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end zero-config docname collision — one path, RED then guarded then GREEN** (tracer)
   - `87dd263` (test): failing collision gate fixture + module, RED against unmodified `builder.py`
   - `edca2de` (fix): the collision guard itself, GREEN
   - `d78a574` (docs): evidence §§1-3 (scope, RED, GREEN)
2. **Task 2: Expand to the reserved-template clobber and to the explicit `typst_documents` path**
   - `f85ce5c` (test): three more fixtures, three more subprocess gates, three unit tests; RED-before-GREEN re-proved via `git checkout <pre-fix-SHA>` and restore
   - `469d3a8` (docs): evidence §§4-5 (revert/restore procedure, RED, GREEN, scenario-to-test-node-id table)
3. **Task 3: Re-run the phase gate, measure the regression boundary, and record the gap-closure verdict**
   - `e3210e2` (style): black auto-fix for a line-wrap surfaced by this task's own `<verify>` step (Rule 1, committed separately so Task 3 itself changes no test/code)
   - `547c8ac` (docs): evidence §§6-7 (regression boundary, full phase gate, gap-closure verdict)

**Plan metadata:** none yet — SUMMARY.md commit follows this file.

## Files Created/Modified

- `typsphinx/builder.py` - the CR-01 collision guard inside `_resolve_output_stem`, plus a docstring sentence documenting it
- `tests/test_typst_documents_collision_gate.py` - five real `sphinx-build` subprocess gates covering all four collision scenarios
- `tests/test_builder_output_stem.py` - three new unit tests for the collision guard and its `getattr` regression guard
- `tests/fixtures/derived_docname_collision_gate/{conf.py,index.rst,chapter1.rst}` - zero-configuration docname-collision reproduction (`project = "Chapter 1"` vs. `chapter1.rst`)
- `tests/fixtures/derived_template_collision_gate/{conf.py,index.rst}` - zero-configuration reserved-template reproduction (`project = "_Template"`)
- `tests/fixtures/explicit_docname_collision_gate/{conf.py,index.rst,chapter1.rst}` - explicit `typst_documents` entry naming an existing docname
- `tests/fixtures/explicit_template_collision_gate/{conf.py,index.rst}` - explicit `typst_documents` entry naming `_template.typ`
- `.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-05.md` - full RED-before-GREEN record, regression-boundary re-measurement, and gap-closure verdict

## Decisions Made

- The collision comparison uses the directory-qualified effective path (`_directory_preserving_relpath`), not the bare stem, because a nested docname's stem is re-prefixed with its own directory before it reaches `path.join(self.outdir, ...)`.
- The `_template` reservation is a root-level equality test only (never a basename test), because `_write_template_file()` writes `_template.typ` unconditionally at the outdir root and never nested.
- Fallback is always the docname itself — never a synthesized name (no `-1`/`-2` suffix, no hash) — matching the existing D-02/D-06/D-07 fallback convention.
- WARNING severity is kept (not lowered to INFO), so `-W` builds still fail on the collision, matching D-03's precedent reasoning.
- The warning firing twice on a `-b typstpdf` build (once from `write_doc`, once from `finish`) is accepted as expected behavior, consistent with the pre-existing D-06/D-07 warnings; tests assert the warning's presence, never an exact count.
- WR-01 and IN-01 (from `44-REVIEW.md`) stay explicitly out of scope, per the objective's owner-decision statement — recorded as deferred notes in `44-GATE-EVIDENCE-05.md` § 7, not planned as work.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `black --check .` failure surfaced by Task 3's own `<verify>` step**
- **Found during:** Task 3 (running the plan-level lint/type gate)
- **Issue:** A multi-line constant assignment added in Task 2 (`DERIVED_TEMPLATE_COLLISION_FIXTURE_DIR = FIXTURES_DIR / "derived_template_collision_gate"`) exceeded the 88-column limit black enforces.
- **Fix:** Ran `uv run black tests/test_typst_documents_collision_gate.py`, re-ran `black --check .` to confirm clean (`230 files would be left unchanged`), and re-ran the collision gate module to confirm no behavior change (`5 passed`).
- **Files modified:** `tests/test_typst_documents_collision_gate.py`
- **Verification:** `uv run black --check .` exits 0; `uv run python -m pytest tests/test_typst_documents_collision_gate.py -q` still passes.
- **Committed in:** `e3210e2` (separate `style(44-05):` commit, so Task 3's own docs commit changes no test/code, matching its acceptance criterion)

**2. [Environmental, not a code deviation] NixOS-sandbox `.venv/bin/uv`/`.venv/bin/ruff` shim, re-applied**
- **Found during:** Task 3 (running the full pytest suite)
- **Issue:** The fresh worktree's `uv sync --extra dev` installs generic-linux ELF wheels for `uv` and `ruff` that NixOS cannot exec directly (exit 127), producing 45 pre-existing environmental failures in `tests/test_integration_{multi_doc,nested_toctree}.py` (subprocess `uv run sphinx-build` calls that cannot exec).
- **Fix:** `ln -sf /nix/store/.../uv .venv/bin/uv` and `ln -sf /home/yuta/Documents/typsphinx/.venv/bin/ruff .venv/bin/ruff`, matching the documented runbook from `44-GATE-EVIDENCE-01.md` §6(b) and `44-GATE-EVIDENCE-04.md` §5. No code change; venv contents are gitignored, so no commit was needed.
- **Verification:** `.venv/bin/uv --version` and `.venv/bin/ruff --version` both execute; full suite re-run afterward passed cleanly (`863 passed, 1 skipped`).

---

**Total deviations:** 1 auto-fixed code deviation (Rule 1, black formatting) + 1 environmental fix (no code change).
**Impact on plan:** Both were necessary to get a trustworthy green signal; neither introduced scope creep or touched the collision guard's logic.

## Issues Encountered

- **Repo-wide collision re-measurement raw count was 2, not the planner's 0** — but both hits are this plan's own deliberately-colliding gate fixtures (`explicit_docname_collision_gate`, `explicit_template_collision_gate`), created specifically to trigger the guard. Excluding those two, the re-measured count over every other `conf.py` in the repository is 0, confirming the planner's baseline. Recorded plainly in `44-GATE-EVIDENCE-05.md` § 6 rather than silently reconciled.
- **The template-clobber byte-count diverged from `44-REVIEW.md`'s earlier orchestrator re-measurement** (528/578 bytes here vs. 460 bytes there) — expected, since the two measurements used different fixture body text of different lengths. Both measurements agree on the load-bearing fact (`#let project` count 0 pre-fix, 1 post-fix), so the byte-count divergence does not affect the guard's correctness and is documented rather than silently overwritten.
- **A tracer-task checkpoint pause occurred between Task 1 and Task 2** — `workflow._auto_chain_active` and `workflow.auto_advance` were both `false` at Task 1's completion, so per the tracer feedback gate this executor halted and returned a `checkpoint:human-verify` for the human owner to confirm the working slice before expansion. The owner approved ("承認して続行"), and this session resumed at Task 2 per the coordinator's explicit continuation instructions, re-verifying (not re-running) Task 1's already-committed work.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- CR-01 is fully closed: both `missing:` items from `44-VERIFICATION.md` carry an explicit `GAP CLOSED` verdict with the evidence section and test node ids that discharge them.
- The phase's own SC#1-SC#5 evidence remains intact: the full suite, black/ruff/mypy, and the full-corpus `-b typstpdf` gate are all green at or above the recorded baseline; no locked decision (D-01…D-05) was altered; no runtime dependency was added.
- WR-01 (the `None`-vs-empty-list warning wording) and IN-01 (the vacuous `test_default_typst_documents_gate.py` assertion) remain open, owner-excluded from this plan — available as candidates for a future maintenance pass, not blockers for Phase 45.
- Phase 45 (Documentation Currency + Carried Hygiene) can proceed: it documents `typst_documents` and its new default, which now includes the collision-safety behavior established here.

## Self-Check: PASSED

- FOUND: `typsphinx/builder.py`
- FOUND: `tests/test_typst_documents_collision_gate.py`
- FOUND: `.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-05.md`
- FOUND: all 7 task commits (`87dd263`, `edca2de`, `d78a574`, `f85ce5c`, `469d3a8`, `e3210e2`, `547c8ac`)

---
*Phase: 44-typst-documents-default-derivation-builder-input-hardening*
*Completed: 2026-08-04*

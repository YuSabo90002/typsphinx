---
phase: 49-per-master-include-graph-with-state-guarded-includes
plan: 02
subsystem: testing
tags: [sphinx, typst, toctree, state, pytest, fixtures, red-evidence]

# Dependency graph
requires:
  - phase: 49-01
    provides: "49-EXPECTED-STRUCTURE.md's Emission contract, Degenerate-shape outcome table,
      Fixture specification (entries 1 and 2), and Assertion census, plus 49-EVIDENCE.md's
      nine real typst.compile() probes closing D-09 for the decided state-key/edge-key
      spellings"
provides:
  - "tests/fixtures/state_guard_two_master_gate/ -- defect A, diamond and interleaving
    fixture, with executor additions (a nested-docname descendant, an empty-toctree
    document) beyond the literal specification, both reachable from both masters"
  - "tests/fixtures/state_guard_mirror_pair_gate/ -- mirror-pair fixture (two masters
    differing only in one toctree's entry order) plus an executor-added third master-less
    (no-toctree) master as the no-nesting control"
  - "49-RED-EVIDENCE.md -- four pre-fix failure-mode transcripts (two REDs, one invariance,
    one mixed RED/invariance), each a verbatim real sphinx-build/typst.query/pypdf
    measurement against the unfixed tree, matching the 2026-08-11 PROJECT.md baseline"
  - "tests/test_state_guard_composition_gate.py -- 11-test real-compile acceptance gate,
    8 tests recorded as pytest.mark.xfail(strict=True) naming 49-04, 3 invariance guards
    left unmarked, zero XPASS on this plan's own tree"
affects: [49-04, 49-06]

# Actuals (#2632)
actuals:
  tokens: 16337
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Executor-derived fixture extension: when a plan's must_haves truth requires a shape
      the written specification does not literally enumerate (here, a nested-docname child
      and an empty-include-file-list toctree), attach the extension at a point that does not
      disturb the specification's own load-bearing measurements (shared.rst's own toctree,
      not index.rst/zmid.rst/bmaster.rst), and hand-derive its edge set the same way the
      specification derives everything else -- never off a build."
    - "Terse single-line xfail reason + detailed docstring: black always expands a
      multi-argument pytest.mark.xfail(strict=True, reason=(...)) call onto separate lines
      once the reason text exceeds the line budget, which breaks a literal
      'xfail(strict=True' grep match this plan's own acceptance criteria requires -- keeping
      the reason short enough to stay on one line and moving the full paraphrase into the
      test's own docstring satisfies both the grep and the documentation requirement."

key-files:
  created:
    - tests/fixtures/state_guard_two_master_gate/conf.py
    - tests/fixtures/state_guard_two_master_gate/index.rst
    - tests/fixtures/state_guard_two_master_gate/zmid.rst
    - tests/fixtures/state_guard_two_master_gate/shared.rst
    - tests/fixtures/state_guard_two_master_gate/bmaster.rst
    - tests/fixtures/state_guard_two_master_gate/sub/nested.rst
    - tests/fixtures/state_guard_two_master_gate/emptytoc.rst
    - tests/fixtures/state_guard_mirror_pair_gate/conf.py
    - tests/fixtures/state_guard_mirror_pair_gate/xmastera.rst
    - tests/fixtures/state_guard_mirror_pair_gate/xmasterb.rst
    - tests/fixtures/state_guard_mirror_pair_gate/zmid.rst
    - tests/fixtures/state_guard_mirror_pair_gate/shared.rst
    - tests/fixtures/state_guard_mirror_pair_gate/soloist.rst
    - .planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-RED-EVIDENCE.md
    - tests/test_state_guard_composition_gate.py
  modified: []

key-decisions:
  - "The nested-docname (COMP-07 encoding) and empty-include-file-list (COMP-08 empty)
    truths are not literally present in 49-EXPECTED-STRUCTURE.md's fixture specification
    entry 1 -- the plan's own <action> text explicitly instructs adding them beyond the
    literal spec ('per the specification's encoding row', 'add one additional master-less
    document'). Both additions were attached under shared.rst's own toctree (a chain both
    masters already reach) rather than under index.rst/zmid.rst/bmaster.rst directly, so
    the defect-A/diamond/interleaving measurements those three files' exact spec-transcribed
    content is measured against stay undisturbed."
  - "The mirror-pair fixture's third master (soloist) is an executor addition realizing the
    plan's 'additional master-less document with a single top-level section and no toctree'
    instruction as a THIRD typst_documents entry (not merely an unreferenced content
    document) -- only a genuine master's own compiled heading level is a meaningful subject
    for 'a master with no nesting resolves at the top level', since a non-master document
    would need to be included by someone to be observable at all, which would immediately
    reintroduce a nesting level to measure."
  - "Task 2's RED-EVIDENCE build order (docname-sorted: bmaster before index/zmid in
    fixture 1; xmastera before xmasterb in fixture 2) was measured directly rather than
    assumed -- it is what determines which parent's write-time claim on `shared` wins under
    the pre-fix ledger, and both fixtures' observed 0/1 and shorter-sequence outcomes trace
    to it."
  - "Task 3's xfail reasons are kept to short one-liners (e.g. 'flips in 49-04 (RED mode
    1)') with the full paraphrase moved into each test's own docstring, because black
    reformats any pytest.mark.xfail(strict=True, reason=(...)) call whose reason text
    exceeds the line-length budget onto separate lines, which breaks the plan's own
    acceptance-criteria grep for the literal substring 'xfail(strict=True'."

patterns-established:
  - "Load-bearing-properties comment block extended to name executor additions explicitly,
    not just the literally-specified content -- so a future edit knows both the spec-derived
    AND the plan-derived load-bearing properties in one place."

requirements-completed: [COMP-07, COMP-08, COMP-09, COMP-10]

coverage:
  - id: D1
    description: "state_guard_two_master_gate fixture built exactly to 49-EXPECTED-STRUCTURE.md's
      specification entry 1, plus executor-derived nested-docname and empty-toctree
      additions, accepted by a real sphinx-build -b typst against the unfixed tree"
    requirement: "COMP-07"
    verification:
      - kind: integration
        ref: "uv run python -m sphinx -b typst tests/fixtures/state_guard_two_master_gate <build> (exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "state_guard_mirror_pair_gate fixture built exactly to specification entry 2,
      plus an executor-derived third master-less (no-toctree) master, accepted by a real
      sphinx-build -b typst against the unfixed tree"
    requirement: "COMP-10"
    verification:
      - kind: integration
        ref: "uv run python -m sphinx -b typst tests/fixtures/state_guard_mirror_pair_gate <build> (exit 0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "49-RED-EVIDENCE.md captures defect A's pre-fix RED as a pypdf marker count
      (0/1) matching the 2026-08-11 PROJECT.md baseline exactly, plus the diamond, the
      interleaving invariance, and the mirror-pair RED/invariance split, all verbatim
      against the unfixed tree"
    requirement: "COMP-07"
    verification:
      - kind: other
        ref: "real sphinx-build/typst.query/pypdf transcripts recorded verbatim in
          49-RED-EVIDENCE.md Failure modes 1-4"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/test_state_guard_composition_gate.py: 11 tests, every asserted value
      traced to 49-EXPECTED-STRUCTURE.md's Emission contract, 8 post-fix assertions recorded
      as strict xfail naming 49-04, 3 invariance guards left unmarked per recorded evidence"
    requirement: "COMP-08"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_state_guard_composition_gate.py -q (8 xfailed, 3
          passed, zero failures, zero XPASS)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Full fast suite unaffected: uv run pytest -m 'not slow' -q stays at 1027
      passed after all three tasks; black/ruff clean on every new file"
    requirement: "COMP-09"
    verification:
      - kind: integration
        ref: "uv run pytest -m 'not slow' -q (1027 passed, 69 deselected)"
        status: pass
    human_judgment: false

duration: 90min
completed: 2026-08-14
status: complete
---

# Phase 49 Plan 02: Composition Fixtures, Pre-Fix RED Evidence, and Acceptance Gate Summary

**Built the two-master and mirror-pair composition fixtures (with executor-derived
nested-docname, empty-toctree, and no-nesting-control additions), captured defect A's
pre-fix RED as a pypdf marker count matching the 2026-08-11 PROJECT.md baseline exactly,
and authored an 11-test real-compile acceptance gate with 8 assertions recorded as strict
xfails naming 49-04.**

## Performance

- **Duration:** ~90 min
- **Tasks:** 3
- **Files modified:** 15 (all newly created)

## Accomplishments

- Built `tests/fixtures/state_guard_two_master_gate/` exactly to
  `49-EXPECTED-STRUCTURE.md`'s specification entry 1 (index/zmid/shared/bmaster, `zmid`
  before `shared` in `index.rst`'s toctree, `bmaster` as an `:orphan:` second master), plus
  two executor-derived additions the plan's own task text calls for beyond the literal spec:
  a nested-docname (path-separator) descendant `sub/nested` and an empty-include-file-list
  toctree document `emptytoc`, both attached under `shared.rst`'s own toctree so both
  masters reach them through the identical edge key without disturbing the
  defect-A/diamond/interleaving measurements the other four files' exact spec-transcribed
  content is measured against.
- Built `tests/fixtures/state_guard_mirror_pair_gate/` exactly to specification entry 2
  (`xmastera`/`xmasterb` differing only in toctree entry order), plus an executor-derived
  third master (`soloist`, no toctree at all) realizing the "master with no nesting resolves
  at the top level" control as a genuine `typst_documents` entry.
- Captured `49-RED-EVIDENCE.md`: Failure mode 1 (COMP-07 defect A) matches the 2026-08-11
  baseline exactly (master A 0, master B 1, exit 0, no collision warning); Failure mode 2
  (COMP-09 diamond) shows one on-disk `shared.typ` (one SHA-256 digest) still producing a
  0/1 split; Failure mode 3 (COMP-08 interleaving) is recorded as an INVARIANCE baseline
  (the current toctree-position ordering already holds); Failure mode 4 (COMP-10 mirror
  pair) is a RED for both `xmastera`/`xmasterb` and an invariance baseline for the
  `soloist` no-nesting control.
- Authored `tests/test_state_guard_composition_gate.py`: 11 tests over three class-scoped
  build fixtures (two-master, mirror-pair, and a borrowed existing single-master fixture for
  the invariance control), every asserted value traced to the Emission contract's templates
  substituted against this plan's own hand-derived edge sets -- 8 tests marked
  `pytest.mark.xfail(strict=True, reason="flips in 49-04 ...")`, 3 left unmarked as
  invariance guards backed by `49-RED-EVIDENCE.md`'s own recorded measurements.
- `uv run pytest tests/test_state_guard_composition_gate.py -q` reports 8 xfailed, 3 passed,
  zero failures, zero XPASS. `uv run pytest -m "not slow" -q` stays at 1027 passed (69
  deselected, up from 58 -- the 11 new tests are all `@pytest.mark.slow`). `black`/`ruff`
  clean on all new files. `git status --porcelain typsphinx/` printed nothing throughout
  all three tasks.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the two-master composition fixture and the mirror-pair fixture** -
   `95fc4c38` (test)
2. **Task 2: Capture the pre-fix RED for defect A, the diamond, the interleaving and the
   mirror pair** - `ae74d47f` (docs)
3. **Task 3: Author tests/test_state_guard_composition_gate.py** - `8533d907` (test)

_No TDD tasks (plan `type="execute"`, not `tdd`) -- each task is its own atomic real-compile
artifact._

## Files Created/Modified

- `tests/fixtures/state_guard_two_master_gate/` (7 files) - the defect-A/diamond/interleaving
  fixture plus the nested-docname and empty-toctree additions
- `tests/fixtures/state_guard_mirror_pair_gate/` (6 files) - the mirror-pair fixture plus the
  no-nesting-control master
- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-RED-EVIDENCE.md`
  - four verbatim pre-fix failure-mode transcripts
- `tests/test_state_guard_composition_gate.py` - the 11-test acceptance gate

## Decisions Made

See `key-decisions` in frontmatter above. In summary: two of this plan's own must_haves
truths (nested-docname encoding, empty-include-file-list) required content beyond
`49-EXPECTED-STRUCTURE.md`'s literal fixture specification entry 1, per the plan's own
`<action>` text; both were attached under `shared.rst`'s own toctree to avoid disturbing the
spec-fixed defect-A/diamond/interleaving measurements. The mirror-pair fixture's
no-nesting-control document was realized as a genuine third `typst_documents` master (not
merely an orphaned content document), since only a master's own compiled heading level is a
meaningful subject for "resolves at the top level." Task 3's xfail reasons were kept short
(with full paraphrases moved into docstrings) because black reformats any
`xfail(strict=True, reason=(...))` call with a long reason onto separate lines, breaking the
plan's own literal-substring grep acceptance check.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `sub/nested.rst`'s toctree reference to `emptytoc` resolved to the
wrong docname**
- **Found during:** Task 1, verification build
- **Issue:** A bare `emptytoc` entry in `sub/nested.rst`'s toctree resolves relative to
  `sub/nested`'s own directory (`sub/emptytoc`), not the top-level `emptytoc.rst` — Sphinx
  warned `toctree に存在しないドキュメントへの参照が含まれています 'sub/emptytoc'`.
- **Fix:** Used Sphinx's root-relative toctree entry syntax (`/emptytoc`) instead of the
  bare relative form.
- **Files modified:** `tests/fixtures/state_guard_two_master_gate/sub/nested.rst`
- **Verification:** Rebuilt; the warning is gone and `emptytoc` resolves correctly (confirmed
  via the emitted `.typ` and the compiled PDF's own text).
- **Committed in:** `95fc4c38` (part of Task 1's commit)

**2. [Rule 3 - Blocking] `.venv/bin/ruff` and `.venv/bin/uv` are generic-linux ELF binaries
NixOS cannot exec**
- **Found during:** Task 1, first `ruff check` attempt
- **Issue:** The documented NixOS-sandbox hazard (`ruff-generic-linux-elf-unrunnable-on-nixos`)
  — `uv sync` installs a generic-linux `ruff` wheel binary whose dynamic linker NixOS refuses
  to exec.
- **Fix:** `patchelf --set-interpreter <nix-store glibc's ld-linux-x86-64.so.2>
  .venv/bin/ruff`, using the SAME glibc `python3.13`'s own interpreter is linked against
  (found via `readelf -l`), not an arbitrarily-chosen glibc store path (the first one tried
  was a mismatched/32-bit variant and failed with `wrong ELF class`).
- **Files modified:** none tracked (`.venv/` is gitignored; this is a local, disposable
  environment repair, not a source change)
- **Verification:** `.venv/bin/ruff --version` reports `ruff 0.15.20`; `uv run python -m
  ruff check` now runs cleanly for the rest of this plan's execution.
- **Committed in:** not committed (gitignored `.venv/`)

---

**Total deviations:** 2 auto-fixed (both Rule 3 — blocking issues, neither an
architectural change). **Impact on plan:** Zero scope creep; both fixes were necessary to
complete the plan's own verification steps.

## Issues Encountered

- **Black's line-wrapping breaks a literal-substring acceptance check (Task 3, self-caught
  before committing):** the plan's own acceptance criteria requires
  `grep -c 'xfail(strict=True' tests/test_state_guard_composition_gate.py` to return at
  least 7, but `black` unconditionally reformats any
  `@pytest.mark.xfail(strict=True, reason=(...))` call whose `reason=` text does not fit on
  one line onto separate lines (`xfail(\n    strict=True,\n    reason=(...`), which breaks
  the literal substring match. Resolved by writing every xfail reason as a short one-liner
  (e.g. `"flips in 49-04 (RED mode 1)"`, well under black's 88-char budget at 4-space
  indent) and moving the detailed paraphrase of each `49-RED-EVIDENCE.md` transcript into
  the corresponding test's own docstring — satisfying both the grep and the "reason
  paraphrases the matching transcript" requirement.
- **A class-scoped pytest fixture defined as an instance method triggers a hard error, not a
  warning (Task 3):** this project's `pyproject.toml` escalates `DeprecationWarning` to an
  error (`filterwarnings = ["error::DeprecationWarning"]`), and pytest 9.1.1 deprecates
  class-scoped fixtures defined as instance methods. The first draft nested
  `single_master_pdf_text` inside `TestStateGuardSingleMasterInvariance`; moved it to
  module level (matching `two_master_build`/`mirror_pair_build`) before committing.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 49-04 (the tracer/emitter plan) has a concrete, committed acceptance gate to flip: running
  `uv run pytest tests/test_state_guard_composition_gate.py -q` after 49-04 lands should
  report 11 passed and zero xfailed-remaining (any residual xfail is a genuine gap; any XPASS
  is a hard failure per this module's own `strict=True` design). The gate's
  `TWO_MASTER_EDGE_KEYS`/`MIRROR_PAIR_EDGE_KEYS` constants are ready-made expected values for
  49-04's own emitter to be measured against.
- `49-RED-EVIDENCE.md`'s recorded `shared.typ` SHA-256 digest
  (`672b5d2c7c86e73b12c503341e61477983317d7ac6fef08cb5f8a8f4dff012b5`) is asserted directly in
  the gate's diamond test — if 49-04 changes `shared.rst`'s own content for an unrelated
  reason, both this digest and the RED-EVIDENCE recording need updating together (the gate's
  own assertion message says so explicitly).
- No blockers. 49-03 (owning the seven `state_guard_{self_and_url,cycle,selfref,glob,
  orphan_ref,three_master,substring_key}_gate/` fixtures and `test_state_guard_shapes_gate.py`)
  runs concurrently in a separate worktree and touches none of this plan's files.

---
*Phase: 49-per-master-include-graph-with-state-guarded-includes*
*Completed: 2026-08-14*

## Self-Check: PASSED

- FOUND: `tests/fixtures/state_guard_two_master_gate/conf.py`
- FOUND: `tests/fixtures/state_guard_mirror_pair_gate/conf.py`
- FOUND: `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-RED-EVIDENCE.md`
- FOUND: `tests/test_state_guard_composition_gate.py`
- FOUND commit: `95fc4c38`
- FOUND commit: `ae74d47f`
- FOUND commit: `8533d907`

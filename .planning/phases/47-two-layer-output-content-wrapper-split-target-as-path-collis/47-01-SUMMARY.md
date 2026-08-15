---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 01
subsystem: testing
tags: [sphinx, typst, pytest, xfail, pypdf, typst-py, gate-fixtures]

requires: []
provides:
  - "47-EXPECTED-STRUCTURE.md: first-principles derivation of every expected content/wrapper path and #include() string for the five new fixtures, plus the Corpus migration rules (R1-R5 table + fixture de-collision rule) that plans 47-04..47-08 migrate the existing corpus against"
  - "47-RED-EVIDENCE.md: verbatim pre-fix RED evidence (sphinx-build output, emitted .typ content, typst.compile()/pypdf transcripts) for COMP-01..04, OUT-03, BLD-02..04"
  - "tests/test_two_layer_output_gate.py: strict-xfail gate for COMP-01, COMP-02, COMP-03 (B-1), COMP-04 (B-2), OUT-03, and the compute_content_include_path unit edge"
  - "tests/test_collision_validator_gate.py: strict-xfail gate for BLD-02, BLD-03, BLD-04 (both builders) plus the TypstBuilder._collision_key unit edge"
  - "Five new fixture projects under tests/fixtures/: two_layer_root_master_gate, two_layer_nested_master_gate, bld02_duplicate_target_gate, bld03_self_collision_gate, bld04_case_collision_gate"
affects: [47-02, 47-03, 47-09, 47-04, 47-05, 47-06, 47-07, 47-08]

actuals:
  tokens: 21961
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Real sphinx-build subprocess + typst.compile() + pypdf.extract_text() gate, per-module _run_sphinx_build helper duplicated (not imported), matching this repo's established convention"
    - "pytest.mark.xfail(strict=True) as the RED-recording mechanism for defects that compile fine but produce wrong output, per binding constraint #4's non-fatal amendment"
    - "Class-scoped compile-once pypdf-text fixture whose setup-time exception is still caught cleanly by a dependent xfail(strict=True) test (verified empirically this task, not assumed)"

key-files:
  created:
    - .planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-EXPECTED-STRUCTURE.md
    - .planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-RED-EVIDENCE.md
    - tests/test_two_layer_output_gate.py
    - tests/test_collision_validator_gate.py
    - tests/fixtures/two_layer_root_master_gate/
    - tests/fixtures/two_layer_nested_master_gate/
    - tests/fixtures/bld02_duplicate_target_gate/
    - tests/fixtures/bld03_self_collision_gate/
    - tests/fixtures/bld04_case_collision_gate/
  modified: []

key-decisions:
  - "two_layer_nested_master_gate's guide/index.rst heading text deliberately differs from its typst_documents entry's title (\"Guide Section\" vs \"Nested Master\") so COMP-04's pypdf absence assertion for \"Nested Master\" unambiguously detects the mid-body title-page re-expansion rather than the section's own legitimate heading"
  - "bld04_case_collision_gate's index.rst does NOT toctree-include manual, isolating BLD-04's case-collision defect from an unrelated B-1-style docname/target-mismatch confound that a toctree link would have introduced"
  - "COLLISION_ERROR_SUBSTRING = \"output path collision\", matching 47-CONTEXT.md's \"New error/warning message identifiers\" (\"typst: N output path collision(s)\")"

patterns-established:
  - "Fixture de-collision rule (47-EXPECTED-STRUCTURE.md): only element [1] (target) of an existing typst_documents entry is ever changed to resolve a casefold-normalized collision, canonically to \"master.typ\" unless the fixture's own purpose names its target"

requirements-completed: []

coverage:
  - id: D1
    description: "47-EXPECTED-STRUCTURE.md derives, from each fixture's conf.py/rst read literally with no builder run, the exact wrapper/content paths and #include() strings for all five new fixtures, plus the Corpus migration rules section"
    verification:
      - kind: other
        ref: "grep -c '../guide/index.typ' / '../_template.typ' / 'Reversal notice' / '## Corpus migration rules' 47-EXPECTED-STRUCTURE.md (all present)"
        status: pass
    human_judgment: false
  - id: D2
    description: "47-RED-EVIDENCE.md records verbatim pre-fix RED for COMP-01..04, OUT-03, BLD-02..04 -- COMP-03's is a classic TypstError ('file not found'), COMP-04/BLD-02/BLD-03/BLD-04's are structural"
    verification:
      - kind: other
        ref: "grep -c 'file not found' / heading presence checks against 47-RED-EVIDENCE.md (all present)"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/test_two_layer_output_gate.py: 6 tests (COMP-01, COMP-02, COMP-03, COMP-04, OUT-03, compute_content_include_path unit) all xfail(strict=True) against the unfixed tree"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_two_layer_output_gate.py -q"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/test_collision_validator_gate.py: 7 tests (BLD-02/03/04 x2 builders + _collision_key unit) all xfail(strict=True) against the unfixed tree"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_collision_validator_gate.py -q"
        status: pass
    human_judgment: false
  - id: D5
    description: "Five new fixture projects under tests/fixtures/, each with a load-bearing-facts conf.py comment"
    verification:
      - kind: other
        ref: "uv run python -c \"...five conf.py existence check...\" (task 1 <automated> verify, exit 0)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full suite stays green with only the new xfailed tests added; no production code touched"
    verification:
      - kind: integration
        ref: "uv run pytest -q -> 991 passed, 5 skipped, 13 xfailed, 0 failed; git status --porcelain typsphinx/ empty"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 01: Wave-0 Gate Fixtures Summary

**Five real-sphinx-build fixtures plus two strict-xfail pytest gate modules (13 tests total) proving the pre-fix RED for the two-layer content/wrapper split — COMP-03's is a classic `TypstError('file not found ... guide/index.typ')`, COMP-04's and the three collision defects (BLD-02/03/04) are structural `pypdf`/marker-survival assertions, all recorded verbatim in `47-EXPECTED-STRUCTURE.md` and `47-RED-EVIDENCE.md` before any emitter code exists.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-11T09:32:00Z (approx, environment provisioning + context reading)
- **Completed:** 2026-08-11T09:56:47Z
- **Tasks:** 3
- **Files modified:** 15 (2 planning docs, 2 test modules, 13 fixture files across 5 fixture projects)

## Accomplishments

- Wrote `47-EXPECTED-STRUCTURE.md`, deriving every expected content/wrapper path and `#include()`
  string for all five new fixtures purely from `conf.py`/`.rst` sources, with the nested-master
  derivation arithmetic (`posixpath.relpath("guide/index.typ", start="manuals") ==
  "../guide/index.typ"`) shown explicitly and verified against the stdlib, and the `## Corpus
  migration rules` section (R1-R5 assertion-class table + fixture de-collision rule) that plans
  47-04..47-08 migrate the existing 87-fixture, 68-module corpus against.
- Built five new `tests/fixtures/` projects (`two_layer_root_master_gate`,
  `two_layer_nested_master_gate`, `bld02_duplicate_target_gate`, `bld03_self_collision_gate`,
  `bld04_case_collision_gate`), each with a load-bearing-facts `conf.py` comment in this repo's
  established convention.
- Wrote `tests/test_two_layer_output_gate.py` (6 tests) and `tests/test_collision_validator_gate.py`
  (7 tests), all `xfail(strict=True)` against the unfixed tree — 13 xfailed, 0 failed, 0 xpassed,
  exit 0. Every asserted path/string was copied from `47-EXPECTED-STRUCTURE.md`'s derived tables,
  never discovered by running the new emitter.
- Recorded `47-RED-EVIDENCE.md`'s full verbatim pre-fix transcripts, independently re-measured this
  task (not copied from `47-RESEARCH.md`'s prior session): COMP-03's classic `TypstError`, COMP-04's
  six-page `pypdf` structural sequence (a second title page + second outline mid-body), and the
  BLD-02/BLD-03/BLD-04 structural observations (silent overwrite, self-collision success, and two
  distinct case-varied files on Linux respectively).
- Verified the full suite stays green: `uv run pytest -q` → 991 passed, 5 skipped, 13 xfailed, 0
  failed; `black --check .` clean across all 261 files; `git status --porcelain typsphinx/` empty
  throughout (no production code touched, per this plan's own scope).

## Task Commits

Each task was committed atomically:

1. **Task 1: Derive the expected two-layer structure and build the five fixture projects** -
   `3f8a1dd` (docs)
2. **Task 2: Write tests/test_two_layer_output_gate.py and record its RED** - `fe8365c` (test)
3. **Task 3: Write tests/test_collision_validator_gate.py and record the three collision REDs** -
   `85f352e` (test)

_No TDD tasks in this plan — all three are `type="auto"` (fixture/doc-writing and gate-recording,
never modifying production code)._

## Files Created/Modified

- `.planning/phases/47-.../47-EXPECTED-STRUCTURE.md` - first-principles derivation of every expected
  path/include string, plus Corpus migration rules
- `.planning/phases/47-.../47-RED-EVIDENCE.md` - verbatim pre-fix RED transcripts for all 9 requirements
- `tests/test_two_layer_output_gate.py` - COMP-01/02/03/04, OUT-03, unit edge (6 tests)
- `tests/test_collision_validator_gate.py` - BLD-02/03/04 x2 builders, unit edge (7 tests)
- `tests/fixtures/two_layer_root_master_gate/` - COMP-01/02/OUT-03 root-master fixture
- `tests/fixtures/two_layer_nested_master_gate/` - COMP-03 (B-1) / COMP-04 (B-2) nested-master fixture
- `tests/fixtures/bld02_duplicate_target_gate/` - duplicate-target fixture
- `tests/fixtures/bld03_self_collision_gate/` - self-collision fixture
- `tests/fixtures/bld04_case_collision_gate/` - case-varied-target fixture

## Decisions Made

- `two_layer_nested_master_gate/guide/index.rst`'s own heading is deliberately `"Guide Section"`,
  not `"Nested Master"` (which would coincide with the typst_documents entry's title) — otherwise
  COMP-04's `"Nested Master" not in text` post-fix assertion would be falsified by the section's own
  legitimate heading, not just by the second-title-page defect it targets.
- `bld04_case_collision_gate/index.rst` deliberately does NOT toctree-include `manual` — a toctree
  link there confounds BLD-04's case-collision defect with an unrelated B-1-style docname/target
  mismatch on `-b typstpdf` (measured directly this task: with the link, `-b typstpdf` already fails
  pre-fix, but for the wrong reason — a bare `file not found` TypstError, not a collision message).
- `COLLISION_ERROR_SUBSTRING = "output path collision"`, matching `47-CONTEXT.md`'s named error
  identifier `"typst: N output path collision(s)"` (Claude's Discretion per that document, exact
  wording; the constant is deliberately loose enough to survive minor 47-09 wording changes).
- `TypstBuilder._collision_key`'s unit test is marked `xfail(strict=True, raises=AttributeError)`
  (not `ImportError`) since `TypstBuilder` itself already exists — only the method is missing,
  confirmed by direct measurement (`AttributeError: type object 'TypstBuilder' has no attribute
  '_collision_key'`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed `two_layer_nested_master_gate/guide/index.rst`'s heading collision with its own typst_documents title**
- **Found during:** Task 2 (writing the COMP-04 pypdf assertion)
- **Issue:** The fixture (created in Task 1) gave `guide/index.rst` the heading `"Nested Master"`,
  identical to the second `typst_documents` entry's title parameter. Since a toctree-included
  section's own heading text legitimately appears in the compiled PDF post-fix too, this made the
  planned `"Nested Master" not in text` assertion structurally unable to distinguish "the defect is
  fixed" from "the section merely exists" — the substring would remain present post-fix regardless.
- **Fix:** Renamed the RST heading to `"Guide Section"`, keeping the body marker
  `GUIDE-BODY-MARKER` unchanged, and added a load-bearing-facts note to the fixture's `conf.py`
  explaining the distinction.
- **Files modified:** `tests/fixtures/two_layer_nested_master_gate/guide/index.rst`,
  `tests/fixtures/two_layer_nested_master_gate/conf.py`
- **Verification:** Re-measured the B-2 isolation transcript with the corrected fixture — `"Nested
  Master"` now appears exactly once (only from the mid-body second title page), matching the
  intended signal.
- **Committed in:** `fe8365c` (Task 2 commit)

**2. [Rule 1 - Bug] Removed the toctree link from `bld04_case_collision_gate/index.rst`**
- **Found during:** Task 3 (running `-b typstpdf` against the fixture to gather RED evidence)
- **Issue:** The fixture (created in Task 1) toctree-included `manual` from `index`. Since
  `manual`'s own `typst_documents` target (`Manual.typ`) differs from the toctree's docname-derived
  include path (`manual.typ`), this reproduced B-1 (a DIFFERENT, unrelated defect) on `-b typstpdf`:
  `TypstError: file not found (searched at .../manual.typ)`. This meant the pre-fix `-b typstpdf`
  run ALREADY exited non-zero, for the wrong reason, undermining the RED evidence's claim that
  BLD-04 specifically is what closes with 47-09.
- **Fix:** Removed the `.. toctree::` directive from `index.rst` (accepting the harmless "document
  isn't included in any toctree" warning), isolating BLD-04's case-collision defect cleanly — both
  `-b typst` and `-b typstpdf` now succeed (exit 0) pre-fix, with no confound.
- **Files modified:** `tests/fixtures/bld04_case_collision_gate/index.rst`,
  `tests/fixtures/bld04_case_collision_gate/conf.py` (added explanatory comment),
  `.planning/phases/47-.../47-EXPECTED-STRUCTURE.md` (Fixture 5 section updated to match)
- **Verification:** Re-built both builders against the corrected fixture — both exit 0 with only
  the harmless orphan-document warning, confirmed via direct `sphinx-build` invocation.
- **Committed in:** `85f352e` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs in this plan's own Task-1 fixture design,
caught while writing the Task-2/3 gate assertions against them).
**Impact on plan:** Both fixes were necessary for the gate modules' assertions to be structurally
meaningful (not accidentally satisfied or accidentally confounded). No scope creep — no production
code was touched, and both fixes stayed within Task 1's own fixture files plus the planning docs
they're described in.

## Issues Encountered

- **Whether a class-scoped pytest fixture raising during setup breaks a dependent
  `xfail(strict=True)` test's reporting.** Verified empirically with a throwaway probe before
  writing `TestTwoLayerOutputGatePdf` (COMP-04): pytest 9.1.1 correctly reports such a test as
  `XFAIL`, not a bare `error`, even when the shared fixture's `typst.compile()` call raises
  `TypstError` during setup. This was NOT assumed — the probe's output (`1 xfailed` / `2 xfailed`,
  exit 0) is quoted in `47-RED-EVIDENCE.md`'s COMP-04 section, since the plan's binding constraint
  #4 (`pytest exits 0 on the unfixed tree while still proving RED`) depended on this holding.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `47-EXPECTED-STRUCTURE.md` and `47-RED-EVIDENCE.md` are the load-bearing INPUT artifacts for
  47-02 (the two-layer emitter) — every expected path/include string in the emitter's `<verify>`
  blocks should trace back to these documents' derivations, not to the emitter's own output.
- `compute_content_include_path` (in `typsphinx.writer`) and `TypstBuilder._collision_key` (in
  `typsphinx.builder`) are the two production symbols this plan's unit-level xfail tests already
  pin the exact contract for — 47-02 and 47-09 respectively should make these tests pass by
  implementing to the contract already written, not by re-deriving it.
- The `## Corpus migration rules` section in `47-EXPECTED-STRUCTURE.md` is ready for 47-04 through
  47-08 to consume directly when migrating the existing 87 fixtures / 68 test modules.
- **Known limitation, not a blocker:** `ruff check .` cannot run in this sandbox (NixOS cannot exec
  the generic-linux `ruff` ELF — a pre-existing, already-acknowledged deferred item,
  `ruff-generic-linux-elf-unrunnable-on-nixos`, tracked separately and not blocking this phase's
  lint authority, which CI provides). `black --check .` and the full `pytest` suite were both run
  and verified green.
- No blockers for 47-02 (Wave 1, `depends_on: []` per this plan's own frontmatter — but per
  ROADMAP.md's phase-level wave structure, 47-02 is expected to depend on this plan's fixtures/gates
  existing, which they now do, committed).

## Self-Check: PASSED

All 10 created files verified present on disk (`47-EXPECTED-STRUCTURE.md`, `47-RED-EVIDENCE.md`,
`47-01-SUMMARY.md`, both new test modules, all five fixtures' `conf.py`). All three task commits
(`3f8a1dd`, `fe8365c`, `85f352e`) verified present in `git log --oneline --all`.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*

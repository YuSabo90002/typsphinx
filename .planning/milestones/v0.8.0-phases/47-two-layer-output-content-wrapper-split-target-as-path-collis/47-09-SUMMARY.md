---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 09
subsystem: infra
tags: [sphinx, typst, typst-py, docutils, output-builder, collision-validation]

# Dependency graph
requires:
  - phase: 47-01
    provides: "tests/test_collision_validator_gate.py (strict-xfail gate module, COLLISION_ERROR_SUBSTRING), tests/fixtures/bld02_duplicate_target_gate/, tests/fixtures/bld03_self_collision_gate/, tests/fixtures/bld04_case_collision_gate/, 47-EXPECTED-STRUCTURE.md, 47-RED-EVIDENCE.md"
  - phase: 47-02
    provides: "TypstBuilder._content_output_path()/_wrapper_output_relpath()/_write_typst_files(), TypstWriter.render_wrapper(), the content/wrapper split itself, and the acknowledged _wrapper_output_relpath() docname-first-match limitation deferred to this plan"
  - phase: 47-03..47-08
    provides: "the full ~87-fixture corpus migrated to the content/wrapper output shape, de-collided from self-collision except for the deliberately-still-colliding CR-01/BLD-02/03/04 gate fixtures"
provides:
  - "TypstBuilder._collision_key() -- casefold()-normalized, comparison-only, no Unicode normalization"
  - "TypstBuilder._validate_output_path_collisions() -- the unified pre-write collision validator covering all four collision kinds (self-collision, cross-document collision, reserved _template.typ collision, duplicate-target collision) in one pre-write ExtensionError"
  - "TypstBuilder._resolve_target_stem(docname, target) -- the normalization core split out of _resolve_output_stem(), letting _wrapper_output_relpath() resolve a specific entry's own target directly (fixing the D-04 docname-first-match write-path bug)"
  - "The CR-01 in-function collision fallback deleted in full; _resolve_output_stem() and _wrapper_output_relpath() now perform NO collision detection"
  - "The full test suite green: 1027 passed, 5 skipped, 0 failed"
affects: [47-10]

# Actuals (#2632)
actuals:
  tokens: 24073
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Unified pre-write collision validator: one map from a casefold()-normalized comparison key to a human-readable claimant description, populated reserved-name-first then content-paths then wrapper-paths, aggregating every collision into ONE ExtensionError before any write -- the same aggregate-failures-then-raise shape TypstPDFBuilder.finish() already used one build stage later, relocated to run before write() instead of after."
    - "Per-entry target resolution instead of docname-based first-match: _wrapper_output_relpath(entry) now calls _resolve_target_stem(entry[0], entry[1]) directly on the entry passed in, rather than re-searching typst_documents by docname -- this is what makes two entries naming the same docname with different targets (D-04) resolve to two independent physical paths instead of both silently landing on whichever entry a docname search finds first."

key-files:
  created: []
  modified:
    - typsphinx/builder.py
    - tests/test_collision_validator_gate.py
    - tests/test_typst_documents_collision_gate.py
    - tests/test_builder_output_stem.py
    - tests/test_document_metadata_render_gate.py
    - tests/test_template_assets.py
    - tests/fixtures/derived_docname_collision_gate/conf.py
    - tests/fixtures/derived_template_collision_gate/conf.py
    - tests/fixtures/explicit_docname_collision_gate/conf.py
    - tests/fixtures/explicit_template_collision_gate/conf.py
    - tests/fixtures/entry_title_author_render_gate/conf.py
    - .planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-VALIDATION.md

key-decisions:
  - "D-01 and D-03 checkpoint:decision tasks were pre-resolved by the project owner to option-a (hard ExtensionError, no fallback; one unified validator, error-only, pre-write, aggregate) before this executor ran -- both were implemented as locked, not re-litigated as interactive checkpoints, per the orchestrator's explicit instruction."
  - "The validator call was placed at the very TOP of write() -- before prepare_writing() (which writes _template.typ immediately) -- rather than the plan's literally-suggested placement 'immediately after master_included_docnames is computed'. The literal placement would have let _template.typ be written to disk before a collision is detected, violating BLD-02's own gate assertion that NO .typ file (including _template.typ) exists after a collision is found. 47-PATTERNS.md explicitly grants 'exact placement is Claude's Discretion... constrained only by before write'; this placement satisfies that constraint more completely."
  - "_directory_preserving_relpath() was deleted outright rather than left in place unused -- its only caller was the CR-01 block this task deletes, and its docstring described logic ('the CR-01 collision comparison') that no longer exists after the deletion, making it actively misleading dead code rather than a harmless unused method."
  - "The D-04 docname-first-match write-path bug (_wrapper_output_relpath() resolving via _resolve_output_stem(entry[0]) instead of the entry's own target) was fixed as part of Task 3's own scope, not deferred further -- the plan's own <behavior> block requires 'A configuration with two entries naming the same docname and DIFFERENT targets raises nothing and produces two wrappers,' which is unachievable without this fix, and 47-02-SUMMARY.md/47-06-SUMMARY.md both explicitly named this plan as the fix's owner."

patterns-established:
  - "Split normalization from lookup: _resolve_output_stem(docname) (docname-based first-match lookup) delegates to _resolve_target_stem(docname, target) (pure normalization, given a target value directly) -- any future caller needing per-entry resolution (bypassing the first-match search) calls the second function directly, as _wrapper_output_relpath() now does."

requirements-completed: [BLD-02, BLD-03, BLD-04, COMP-01, COMP-02]

coverage:
  - id: D1
    description: "TypstBuilder._collision_key() folds case (casefold()) and path separators (\\ -> /) on both sides, on every platform, with no Unicode normalization"
    requirement: "BLD-04"
    verification:
      - kind: unit
        ref: "tests/test_collision_validator_gate.py::TestCollisionKeyUnit::test_collision_key_folds_case_but_not_unicode_normalization"
        status: pass
    human_judgment: false
  - id: D2
    description: "A wrapper target resolving onto its own content file's path, another document's content path, or the reserved _template.typ raises a single pre-write ExtensionError naming the collision, with NO output file written"
    requirement: "BLD-03"
    verification:
      - kind: integration
        ref: "tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld03_self_collision_rejected_typst"
        status: pass
      - kind: integration
        ref: "tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld03_self_collision_rejected_typstpdf"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two typst_documents entries resolving to the same target raise a single ExtensionError naming both entries, with NO output file written"
    requirement: "BLD-02"
    verification:
      - kind: integration
        ref: "tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld02_duplicate_target_rejected_typst"
        status: pass
      - kind: integration
        ref: "tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld02_duplicate_target_rejected_typstpdf"
        status: pass
    human_judgment: false
  - id: D4
    description: "Two typst_documents entries naming the SAME docname with DIFFERENT targets are permitted and produce two independent wrapper files, each carrying its own entry's title/author (D-04 write-path fix)"
    requirement: "COMP-02"
    verification:
      - kind: integration
        ref: "tests/test_document_metadata_render_gate.py::TestEntryTitleAuthorRenderGate::test_repeated_docname_wrapper_reads_its_own_entry_title_not_first_match"
        status: pass
    human_judgment: false
  - id: D5
    description: "The CR-01 gate's five methods invert wholesale to assert build failure (non-zero exit, ExtensionError, output-path-collision substring) instead of exit 0 plus a warning, on both -b typst and -b typstpdf"
    requirement: "COMP-01"
    verification:
      - kind: integration
        ref: "tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate (5 methods)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The full test suite is green: 1027 passed, 5 skipped, 0 failed; black --check and mypy both green; both dogfooding builds (docs-html, docs-pdf) succeed"
    requirement: null
    verification:
      - kind: other
        ref: "uv run pytest -q (1027 passed, 5 skipped, 204.73s); uv run black --check .; uv run mypy typsphinx/; uv run tox -e docs-html; uv run tox -e docs-pdf"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 09: Unified Pre-Write Collision Validator Summary

**Replaced CR-01's per-entry warn-and-fall-back collision guard with `TypstBuilder._validate_output_path_collisions()` -- one pre-write validator covering all four collision kinds (self-collision, cross-document collision, reserved-file collision, duplicate-target collision) in a single `ExtensionError`, closing the phase with the full 1027-test suite green.**

## Performance

- **Duration:** ~50 min
- **Tasks:** 2 (of 4 -- the two `checkpoint:decision` tasks were pre-resolved by the project owner and implemented as locked, per explicit orchestrator instruction, not executed as interactive checkpoints)
- **Files modified:** 12 (1 production module, 9 test/fixture files, 1 planning artifact)

## Accomplishments

- Added `TypstBuilder._collision_key()` (`casefold()`-normalized, `\`-to-`/`-normalized, comparison-only -- no Unicode normalization, no `sys.platform` branch) and `TypstBuilder._validate_output_path_collisions()`, building ONE map from every docname's content path, every `typst_documents` entry's wrapper path, and the reserved `_template.typ`, to a human-readable claimant description -- any repeat key aggregates into a single `ExtensionError` naming every offending pair, raised before any file is written.
- Deleted the CR-01 in-function collision block from `_resolve_output_stem()` in full, splitting its normalization logic into a new `_resolve_target_stem(docname, target)` -- `_resolve_output_stem()` now performs a docname-based first-match lookup and delegates; it performs NO collision detection of its own anymore.
- Fixed the D-04 docname-first-match write-path bug `47-02-SUMMARY.md` and `47-06-SUMMARY.md` both explicitly deferred to this plan: `_wrapper_output_relpath(entry)` now calls `_resolve_target_stem(entry[0], entry[1])` directly on the passed-in entry, instead of re-searching `typst_documents` by docname -- two entries naming the same docname with different targets (D-04) now each write to their OWN declared target, rather than both landing on whichever entry a docname search happened to find first.
- Deleted the now-fully-unused `_directory_preserving_relpath()` (its only caller was the deleted CR-01 block).
- Placed the validator call at the very TOP of `write()`, before `prepare_writing()` (which writes `_template.typ` immediately) -- ensuring D-02's "no output file is written when any collision is found" covers `_template.typ` itself, not only content/wrapper files, which the plan's literally-suggested placement (after `master_included_docnames` is computed) would have missed.
- Inverted `tests/test_typst_documents_collision_gate.py` wholesale: all five methods now assert `returncode != 0`, an `ExtensionError`, the collision-error substring, and NO output file written -- replacing CR-01's old "exit 0, both documents kept, warning only" contract.
- Moved the two CR-01 fallback assertions in `tests/test_builder_output_stem.py` into four tests proving the responsibility moved (resolver returns the stem unchanged) rather than disappeared (the validator now raises for the same two configurations).
- Found and fixed 8 previously-missed self-colliding fixtures in `tests/test_template_assets.py` (`typst_documents = [('index', 'index', ...)]`, an identity target colliding with its own content file) during the "close the phase green" pass -- retargeted to the canonical `master.typ`.
- Updated `tests/test_document_metadata_render_gate.py`'s three affected tests to reflect the D-04 write-path fix: both `second-handbook.typ`/`.pdf` and `master.typ`/`.pdf` now exist independently, each carrying its own entry's title/author -- a documented, plan-acknowledged flip, not a surprise.
- Full `uv run pytest -q`: **1027 passed, 5 skipped, 0 failed** (204.73s). `black --check .` and `mypy typsphinx/` both green. `tox -e docs-html` and `tox -e docs-pdf` both succeed (dogfooding builds). `ruff check .` cannot execute on this NixOS host (pre-existing, unrelated generic-linux-ELF limitation, not a regression).
- Filled `47-VALIDATION.md`'s Per-Task Verification Map with one row per task across all ten phase plans, recorded the measured full-suite runtime (~200s) as Test Infrastructure and max feedback latency, ticked Wave 0 Requirements and most of the Validation Sign-Off checklist, and set `nyquist_compliant: true`.

## Task Commits

1. **Task 3: Implement the unified pre-write collision validator** - `5bf373c` (feat)
2. **Task 4: Invert the CR-01 gate and close the phase green** - `3fbaa3f` (test)

_Tasks 1 and 2 in the plan's own numbering are the two `checkpoint:decision` tasks (D-01, D-03) -- pre-resolved by the project owner before this executor ran (see Decisions Made below), so no separate commit exists for them; their realization is proven by Task 3's commit and its automated verify._

## Files Created/Modified

- `typsphinx/builder.py` - `_collision_key()`, `_validate_output_path_collisions()`, `_resolve_target_stem()` (split out of `_resolve_output_stem()`), `_wrapper_output_relpath()` rewritten for per-entry resolution, CR-01 block and `_directory_preserving_relpath()` deleted, validator called at the top of `write()`
- `tests/test_collision_validator_gate.py` - `xfail` markers removed (all 7 tests now pass for real)
- `tests/test_typst_documents_collision_gate.py` - all 5 methods inverted to assert build failure
- `tests/test_builder_output_stem.py` - 2 CR-01 fallback tests replaced with 4 tests proving the responsibility moved from resolver to validator
- `tests/test_document_metadata_render_gate.py` - 3 tests updated for the D-04 write-path fix (both wrappers now exist independently)
- `tests/test_template_assets.py` - 8 previously-missed self-colliding fixtures de-collided
- `tests/fixtures/derived_docname_collision_gate/conf.py`, `derived_template_collision_gate/conf.py`, `explicit_docname_collision_gate/conf.py`, `explicit_template_collision_gate/conf.py` - comments updated to record the new build-failure contract
- `tests/fixtures/entry_title_author_render_gate/conf.py` - comment updated to record the D-04 write-path fix
- `.planning/phases/47-.../47-VALIDATION.md` - Per-Task Verification Map filled, runtime recorded, sign-off checklist ticked, `nyquist_compliant: true`

## Decisions Made

- **D-01 and D-03 pre-resolved to option-a by the project owner, implemented as locked.** The orchestrator's instructions explicitly stated both decisions were "already made" (hard `ExtensionError`, no fallback; one unified validator, error-only, pre-write, aggregate) and instructed this executor NOT to re-ask them as interactive checkpoints. Implemented accordingly -- see the plan's own `<task type="checkpoint:decision">` blocks for the full option comparison this decision closes.
- **Validator call placed at the top of `write()`, not after `master_included_docnames`.** The plan's action text literally suggested the latter placement, but `prepare_writing()` (called before `master_included_docnames` is computed) writes `_template.typ` immediately -- placing the validator after that point would let `_template.typ` exist on disk even when a collision aborts the build, violating `test_bld02_duplicate_target_rejected_typst`'s own `_no_typ_files_written()` assertion (which checks for ANY `.typ` file, including `_template.typ`). `47-PATTERNS.md` explicitly grants "exact placement is Claude's Discretion... constrained only by before write" -- the chosen placement satisfies that constraint more completely, verified by a real build producing zero `.typ` files.
- **`_directory_preserving_relpath()` deleted outright, not left unused.** Its only caller was the CR-01 block this task deletes; keeping it around with a docstring describing "the CR-01 collision comparison" it no longer performs would be actively misleading dead code, not a harmless unused method.
- **D-04's docname-first-match write-path bug fixed as part of Task 3, not deferred again.** The plan's own `<behavior>` block requires "two entries naming the same docname and DIFFERENT targets... produces two wrappers," which is unachievable without fixing `_wrapper_output_relpath()`'s docname-based first-match resolution -- and both `47-02-SUMMARY.md` and `47-06-SUMMARY.md` explicitly named this plan as the fix's intended owner.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Validator call placement moved to satisfy D-02's own "no output file written" gate**
- **Found during:** Task 3 (implementing the validator)
- **Issue:** The plan's action text suggested calling the validator "immediately after `self.master_included_docnames` is computed" -- but `prepare_writing()`, called earlier in `write()`, writes `_template.typ` to disk unconditionally. A collision detected after that point would leave `_template.typ` on disk, failing `test_bld02_duplicate_target_rejected_typst`'s `_no_typ_files_written()` assertion.
- **Fix:** Moved the validator call to the very top of `write()`, before `prepare_writing()`.
- **Files modified:** `typsphinx/builder.py`
- **Verification:** A real `-b typst` build of `tests/fixtures/bld03_self_collision_gate` produces zero `.typ` files (verified via `find <build_dir> -name "*.typ"`, no output); `tests/test_collision_validator_gate.py`'s BLD-02 test (which asserts this directly) passes.
- **Committed in:** `5bf373c` (Task 3 commit)

**2. [Rule 1 - Bug] `_wrapper_output_relpath()`'s docname-first-match write-path bug fixed**
- **Found during:** Task 3 (implementing D-04's "produces two wrappers" behavior requirement)
- **Issue:** `_wrapper_output_relpath(entry)` resolved via `self._resolve_output_stem(entry[0])` -- a docname-based first-match SCAN of `typst_documents`, not a per-entry-target computation. Two entries naming the same docname with different targets both resolved to the FIRST entry's target, so the second entry's write silently overwrote the first at that shared path -- exactly the gap `47-02-SUMMARY.md` and `47-06-SUMMARY.md` both named as deferred to this plan.
- **Fix:** Split `_resolve_output_stem()`'s normalization core into `_resolve_target_stem(docname, target)`, and rewrote `_wrapper_output_relpath(entry)` to call it directly on the entry's OWN target (`entry[1]`), bypassing the first-match search entirely.
- **Files modified:** `typsphinx/builder.py`
- **Verification:** A real `-b typst` build of `tests/fixtures/entry_title_author_render_gate` now writes both `second-handbook.typ` (title "Second Handbook") and `master.typ` (title "My Handbook") independently; `tests/test_document_metadata_render_gate.py`'s D-08 proof test passes with both wrappers asserted to exist.
- **Committed in:** `5bf373c` (Task 3 commit)

**3. [Rule 1 - Bug] 8 previously-missed self-colliding fixtures in `tests/test_template_assets.py`**
- **Found during:** Task 4 (running the full suite to close the phase green)
- **Issue:** `tests/test_template_assets.py`'s 8 test fixtures each configured `typst_documents = [('index', 'index', 'Test', 'Author')]` -- an identity target self-colliding with docname `index`'s own content file (`index.typ`), the exact D-01 self-collision shape. None of plans 47-04 through 47-08's corpus-migration sweeps caught these (they live inline as Python strings inside `test_template_assets.py`, not as `tests/fixtures/*/conf.py` files, so a fixture-directory-based migration sweep would not have found them).
- **Fix:** Retargeted all 8 to the canonical `master.typ`, per the fixture de-collision rule in `47-EXPECTED-STRUCTURE.md`.
- **Files modified:** `tests/test_template_assets.py`
- **Verification:** All 8 tests in the module pass.
- **Committed in:** `3fbaa3f` (Task 4 commit)

**4. [Rule 1 - Bug] `tests/test_document_metadata_render_gate.py`'s 3 tests updated for the D-04 write-path fix**
- **Found during:** Task 4 (running the full suite to close the phase green)
- **Issue:** Three tests in this module were written against the KNOWN, plan-acknowledged docname-first-match write-path bug (fix #2 above) -- they asserted `master.typ` does NOT exist and read title/author values from `second-handbook.typ` alone. Once the bug was fixed, both wrappers exist independently, each with its own entry's values, so these assertions became stale by design (both `47-02-SUMMARY.md` and `47-06-SUMMARY.md` explicitly flagged this exact test/assertion as needing to flip once this plan landed the fix).
- **Fix:** Updated `test_entry_title_and_author_reach_the_compiled_pdf` to read `master.pdf` (path change only, same pinned values "My Handbook"/"Jane Doe"); rewrote `test_repeated_docname_wrapper_reads_its_own_entry_title_not_first_match` to assert BOTH wrappers exist, each carrying its own entry's title; updated `test_emitted_typ_carries_the_entry_values` to read `master.typ`.
- **Files modified:** `tests/test_document_metadata_render_gate.py`
- **Verification:** All 4 tests in the module pass.
- **Committed in:** `3fbaa3f` (Task 4 commit)

---

**Total deviations:** 4 auto-fixed (all Rule 1 -- correctness fixes and the plan-anticipated test updates required to make its own stated `<behavior>`/`<verification>` requirements measure real behavior, not scope creep).
**Impact on plan:** All four were necessary for this plan's own designated verification (the full suite green, D-04's "produces two wrappers" behavior, D-02's "no output file written") to hold. None expanded scope beyond what the plan's own text anticipated.

## Issues Encountered

None beyond the four auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The phase's full-suite-green gate is discharged: `uv run pytest -q` = 1027 passed / 5 skipped / 0 failed; `black --check .` and `mypy typsphinx/` both green; both dogfooding builds succeed.
- Plan 47-10 (wave 5) is unblocked: it depends only on `47-09`, and its own precondition ("plan 47-09 is merged... and `uv run pytest -q` on that branch exits 0") is satisfied by this plan's own state.
- `47-VALIDATION.md`'s Per-Task Verification Map, Test Infrastructure runtime, Wave 0 Requirements, and most of the Validation Sign-Off checklist are filled/ticked; `nyquist_compliant: true` is set. The two Manual-Only Verifications rows (branch on `origin`, completed CI run with Windows/macOS lanes) remain undischarged -- they are explicitly plan 47-10's job (requiring a real network push and a real GitHub Actions run, neither reproducible from a worktree-isolated executor).
- No blockers for plan 47-10.

## Self-Check: PASSED

`typsphinx/builder.py` verified present with `_collision_key`, `_validate_output_path_collisions`, `_resolve_target_stem` (via `grep -n` against the file). Both task commits (`5bf373c`, `3fbaa3f`) verified present via `git log --oneline`. Full test suite re-run confirmed 1027 passed / 5 skipped / 0 failed at HEAD.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*

---
phase: 26-typst-elements-papersize-fontsize-pass-through-dead-config-s
plan: 02
subsystem: testing
tags: [sphinx, typst, pytest, gate-01, real-compile, regression-gate]

# Dependency graph
requires:
  - phase: 26-01
    provides: "RawTypst marker + ELEMENTS_ALLOWLIST curated merge in template_engine.py, wired from writer.py as a separate argument -- papersize/fontsize reach map_parameters() with correct per-key typing, unknown keys fail loud via ExtensionError, copyright is structurally unreachable"
provides:
  - "tests/fixtures/typst_elements_pass_through_gate/{papersize_positive,fontsize_positive,unknown_key_negative}/ -- three minimal default-template fixture projects, one per required GATE-01 case"
  - "tests/test_typst_elements_pass_through_gate.py -- GATE-01 real-typst.compile() regression module: TestPapersizePositiveGate (SC#1 + SC#4), TestFontsizePositiveGate (SC#2), TestUnknownKeyNegativeGate (SC#3), TestPreFixBasisFailureProof (durable undeclared-kwarg + leaked-copyright reconstructions)"
  - "Recorded manual red->green confirmation: Plan 01's fix temporarily reverted, 3 of 10 tests went RED (exactly the papersize/fontsize/unknown-key assertions), restored to GREEN"
affects: [phase-27 (docs examples referencing typst_elements papersize/fontsize can now cite a working, gate-proven feature)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "GATE-01 real-compile module mirrors tests/test_package_only_config_gate.py exactly: _run_sphinx_build() via sys.executable -m sphinx, _show_rule_call_region() slicer, class-scoped @staticmethod build fixtures, skipif(not TYPST_AVAILABLE)"
    - "Shared-build case folding: SC#1 (papersize) and SC#4 (copyright non-leak) proven against the SAME class-scoped build/fixture, since the plan's own wording asked for the non-leak case to be proven against 'the positive fixture' rather than a fifth separate directory"

key-files:
  created:
    - tests/fixtures/typst_elements_pass_through_gate/papersize_positive/conf.py
    - tests/fixtures/typst_elements_pass_through_gate/papersize_positive/index.rst
    - tests/fixtures/typst_elements_pass_through_gate/fontsize_positive/conf.py
    - tests/fixtures/typst_elements_pass_through_gate/fontsize_positive/index.rst
    - tests/fixtures/typst_elements_pass_through_gate/unknown_key_negative/conf.py
    - tests/fixtures/typst_elements_pass_through_gate/unknown_key_negative/index.rst
    - tests/test_typst_elements_pass_through_gate.py
  modified: []

key-decisions:
  - "Fixture layout: three small standalone fixture directories (papersize_positive, fontsize_positive, unknown_key_negative), not the larger _write_variant_project() variant-derivation machinery -- matches the RESEARCH.md recommendation for 4 small INDEPENDENT cases rather than a larger difference matrix"
  - "All three fixtures use the DEFAULT (unset typst_package/typst_template) template path -- papersize/fontsize are parameters of templates/base.typ's own project() function, so no Typst-Universe package or custom template is needed"
  - "SC#4 (copyright non-leak) is proven against the SAME build as SC#1 (papersize positive), not a fourth fixture directory -- the plan's own wording says 'build the positive fixture' for this case, and the papersize fixture's conf.py already carries a distinctive copyright canary for exactly this purpose"
  - "TestUnknownKeyNegativeGate is NOT skipif(not TYPST_AVAILABLE) -- the ExtensionError raise happens inside TypstWriter.translate() during the write phase, before any typst.compile() call could occur, so this case does not depend on typst-py being installed at all"
  - "TestUnknownKeyNegativeGate uses the faster -b typst builder (never -b typstpdf) -- the build aborts before a compile step would ever be reached"
  - "Two task commits split at the same natural boundary as tests/test_package_only_config_gate.py's own two-class structure: Task 1 = the four standing real-compile cases; Task 2 = the durable TestPreFixBasisFailureProof reconstruction class, added in a second commit on top of the same file"

patterns-established:
  - "Shared-build case folding for a non-leak assertion: when a plan's SC wording says to prove a negative case against 'the positive fixture' rather than mandating a dedicated fixture, fold that assertion into the positive fixture's own test class instead of creating a fifth fixture directory"

requirements-completed: [CONF-04]

coverage:
  - id: D1
    description: "A real -b typstpdf build of typst_elements={'papersize': 'us-letter'} emits papersize as a quoted Typst string in the show-rule region and compiles a valid PDF (SC#1)"
    requirement: "CONF-04"
    verification:
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestPapersizePositiveGate::test_papersize_emitted_as_quoted_string"
        status: pass
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestPapersizePositiveGate::test_real_compile_produces_valid_pdf"
        status: pass
    human_judgment: false
  - id: D2
    description: "A SEPARATE real -b typstpdf build of typst_elements={'fontsize': '20pt'} emits fontsize as an UNQUOTED Typst length in the show-rule region (never its quoted form) and compiles a valid PDF (SC#2)"
    requirement: "CONF-04"
    verification:
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestFontsizePositiveGate::test_fontsize_emitted_as_unquoted_length"
        status: pass
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestFontsizePositiveGate::test_fontsize_quoted_form_never_appears"
        status: pass
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestFontsizePositiveGate::test_real_compile_produces_valid_pdf"
        status: pass
    human_judgment: false
  - id: D3
    description: "An unknown typst_elements key makes sphinx-build exit non-zero via ExtensionError, and no emitted master carries the bogus key as a project.with(...) kwarg (SC#3)"
    requirement: "CONF-04"
    verification:
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestUnknownKeyNegativeGate::test_build_exits_non_zero"
        status: pass
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestUnknownKeyNegativeGate::test_no_master_carries_the_bogus_key_as_a_kwarg"
        status: pass
    human_judgment: false
  - id: D4
    description: "copyright never appears anywhere in the emitted show-rule region of the positive fixture's build (SC#4)"
    requirement: "CONF-04"
    verification:
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestPapersizePositiveGate::test_copyright_never_leaks_into_show_rule_region"
        status: pass
    human_judgment: false
  - id: D5
    description: "Durable pre-fix-basis failure proof: an undeclared-kwarg splice and a leaked-copyright splice into the post-fix emitted master each make a real typst.compile() raise -- the standing red proof that fail-loud (SC#3) and structural non-leak (SC#4) matter"
    requirement: "CONF-04"
    verification:
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestPreFixBasisFailureProof::test_undeclared_kwarg_basis_raises"
        status: pass
      - kind: integration
        ref: "tests/test_typst_elements_pass_through_gate.py::TestPreFixBasisFailureProof::test_leaked_copyright_basis_raises"
        status: pass
    human_judgment: false
  - id: D6
    description: "Manual red->green confirmation: temporarily reverting Plan 01's template_engine.py/writer.py fix makes exactly the papersize/fontsize/unknown-key assertions fail (RED); restoring the fix makes them pass again (GREEN)"
    requirement: "CONF-04"
    verification: []
    human_judgment: true
    rationale: "This is a one-time manual weaken-and-observe procedure (recorded in prose below), not a standing automated test -- a test that verifies its own absence is not expressible, matching the convention already established by tests/test_package_only_config_gate.py's own TestPreFixBasisFailureProof docstring."
  - id: D7
    description: "Full suite honest green bar: no NEW failures versus the pre-change baseline; templates/base.typ remains byte-unchanged (SC#5)"
    requirement: "CONF-04"
    verification:
      - kind: other
        ref: "uv run pytest -q -m \"not slow\" -> 542 passed, same 45 pre-existing environmental integration failures as the pre-change baseline (532 passed, 45 failed) -- +10 passed matches exactly the 10 new tests added"
        status: pass
      - kind: other
        ref: "git diff --exit-code typsphinx/templates/base.typ (exit 0)"
        status: pass
    human_judgment: false

# Metrics
duration: 2min
completed: 2026-07-24
status: complete
---

# Phase 26 Plan 02: `typst_elements` GATE-01 Real-Compile Regression Fixtures Summary

**Four standing real-`typst.compile()`/`sphinx-build` cases (papersize quoted, fontsize unquoted on a separate build, unknown-key abort, copyright non-leak) plus a durable `TestPreFixBasisFailureProof` reconstruction class prove CONF-04's `typst_elements` pass-through actually reaches `project()` -- with a recorded manual red->green confirmation against Plan 01's fix.**

## Performance

- **Duration:** ~2 min (task-commit timestamps 06:43:02 -> 06:44:59 JST, plus the manual red/green confirmation and full-suite run performed between commits)
- **Started:** 2026-07-24T06:41:00Z (approx, first commit)
- **Completed:** 2026-07-24T06:44:59Z
- **Tasks:** 2/2 completed
- **Files modified:** 7 (all new)

## Accomplishments
- Created three minimal, standalone GATE-01 fixture projects under `tests/fixtures/typst_elements_pass_through_gate/`: `papersize_positive/` (typst_elements={"papersize": "us-letter"}, plus a distinctive `copyright` canary for the shared SC#4 non-leak assertion), `fontsize_positive/` (typst_elements={"fontsize": "20pt"}, a SEPARATE fixture per SC#1/SC#2's explicit separation requirement), and `unknown_key_negative/` (typst_elements={"bogus_unknown_key": ...}). All three use the DEFAULT template path (no `typst_package`/`typst_template`) since `papersize`/`fontsize` are parameters of `templates/base.typ`'s own byte-frozen `project()` function.
- Created `tests/test_typst_elements_pass_through_gate.py`, mirroring `tests/test_package_only_config_gate.py`'s `_run_sphinx_build()` (`sys.executable -m sphinx`, never `uv run sphinx-build`) and `_show_rule_call_region()` helpers exactly:
  - `TestPapersizePositiveGate` -- a real `-b typstpdf` build proves `papersize: "us-letter",` (quoted) appears in the show-rule region, a valid `%PDF`-magic file is produced, AND (folding in SC#4 against this same build) the fixture's `copyright` canary never appears anywhere in that region.
  - `TestFontsizePositiveGate` -- a SEPARATE real `-b typstpdf` build proves `fontsize: 20pt,` (UNQUOTED) appears, the quoted form `fontsize: "20pt"` never appears (the double-formatting-trap guard), and a valid PDF compiles.
  - `TestUnknownKeyNegativeGate` -- a faster `-b typst` build proves `sphinx-build` exits non-zero on an unrecognized key, and that no emitted `.typ` file anywhere in the build tree carries the bogus key as a kwarg. Deliberately NOT `skipif(not TYPST_AVAILABLE)`: the `ExtensionError` raise happens during `TypstWriter.translate()`, before any compile step is reached.
  - `TestPreFixBasisFailureProof` -- reconstructs two pre-fix defect shapes from the POST-fix emitted master (built once via the faster `-b typst`) and proves a real `typst.compile()` raises against each: an undeclared kwarg spliced into `project.with(...)` (the durable proof of why SC#3's fail-loud allowlist matters), and a leaked `copyright` argument spliced in (the durable proof of why SC#4's structural non-leak matters). Only `pytest.raises(Exception)` is asserted -- never error-message text (D-06).
- Verified all 10 new tests pass with the current (post-Plan-01-fix) codebase: `uv run pytest tests/test_typst_elements_pass_through_gate.py -q` -> `10 passed`.
- Performed and recorded the manual red->green confirmation (see "Manual Red->Green Confirmation" below).
- Ran the full suite (`uv run pytest -q -m "not slow"`): `542 passed, 45 failed` -- the SAME 45 pre-existing environmental integration failures as the documented pre-change baseline (`532 passed, 45 failed`), confirming the honest green bar (no NEW failures; the +10 passed exactly matches this plan's 10 new tests).
- Confirmed `templates/base.typ` remains byte-unchanged: `git diff --exit-code typsphinx/templates/base.typ` exits 0 (SC#5 still holds after the gate work, which touches only `tests/`).

## Manual Red->Green Confirmation

Per the plan's Task 2 instruction (these gates are authored AFTER the Plan 01 fix, so the red->green transition must be manually performed and recorded rather than captured as a standing test):

1. **Identified Plan 01's fix commits:** `b7083c9` (feat: RawTypst marker + ELEMENTS_ALLOWLIST + fail-loud merge) and `67a40ca` (fix: wire writer.py, drop dead copyright key). The commit immediately BEFORE this pair is `46f2191`.
2. **Reverted (in the working tree only, not committed):** copied `typsphinx/template_engine.py` and `typsphinx/writer.py` from `b7083c9^` (i.e. `46f2191`) over the current post-fix versions.
3. **Observed RED:** ran `uv run pytest tests/test_typst_elements_pass_through_gate.py -q` against the reverted source. Result: **3 failed, 7 passed**.
   - `TestPapersizePositiveGate::test_papersize_emitted_as_quoted_string` FAILED -- the show-rule region contained only `title:`/`authors:`/`date:` (the pre-fix `DEFAULT_PARAMETER_MAPPING` only knows those three keys); `papersize:` never appeared.
   - `TestFontsizePositiveGate::test_fontsize_emitted_as_unquoted_length` FAILED -- same reason; `fontsize:` never appeared.
   - `TestUnknownKeyNegativeGate::test_build_exits_non_zero` FAILED -- the pre-fix code has no allowlist check at all, so the unknown key was silently dropped and the build exited 0 ("build succeeded") instead of aborting.
   - The remaining 7 tests still passed under the reverted code (expected): both real-compile/PDF assertions (the build itself still succeeds, just without the elements applied), the fontsize-quoted-form-absent guard (trivially true when fontsize never appears at all), the copyright-non-leak assertion (also trivially true -- copyright was ALSO silently dropped pre-fix, just for the wrong reason: an unrelated defect, not the fix this phase closes), the bogus-key-absent-from-kwargs check (also silently dropped, not leaked), and both `TestPreFixBasisFailureProof` reconstructions (these only depend on the emitted master text unrelated to `typst_elements` handling, so they are insensitive to this particular revert).
4. **Restored:** copied the original post-fix `typsphinx/template_engine.py` and `typsphinx/writer.py` back over the reverted versions. `git status --short typsphinx/` showed no diff versus `HEAD`, confirming an exact, lossless restore.
5. **Observed GREEN:** re-ran `uv run pytest tests/test_typst_elements_pass_through_gate.py -q` -> **10 passed**.

This confirms the four standing GATE-01 cases are load-bearing on Plan 01's actual fix (not vacuously true), and that the specific defect classes SC#1/SC#2/SC#3 close are exactly the ones this manual revert reproduced.

## Task Commits

Each task was committed atomically:

1. **Task 1: Fixture project(s) + the 4 standing GATE-01 real-compile cases** - `c0f16e3` (test)
2. **Task 2: Durable pre-fix-basis failure proof + red->green confirmation + full-suite gate** - `0379a2f` (test)

_Both tasks are `type="auto"`, no TDD multi-commit sequence. Task 1's commit contains the four standing test classes (`TestPapersizePositiveGate`, `TestFontsizePositiveGate`, `TestUnknownKeyNegativeGate`) plus all three fixture directories; Task 2's commit adds `TestPreFixBasisFailureProof` on top of the same file. The manual red->green confirmation and full-suite run (both required by Task 2's acceptance criteria) were performed between the two commits and are recorded in this SUMMARY rather than as separate commits, since neither produces a code change of its own._

## Files Created/Modified
- `tests/fixtures/typst_elements_pass_through_gate/papersize_positive/conf.py` - Default-template fixture: `typst_elements={"papersize": "us-letter"}` + a `copyright` canary for SC#4
- `tests/fixtures/typst_elements_pass_through_gate/papersize_positive/index.rst` - Minimal title + paragraph
- `tests/fixtures/typst_elements_pass_through_gate/fontsize_positive/conf.py` - Default-template fixture: `typst_elements={"fontsize": "20pt"}`, SEPARATE from papersize
- `tests/fixtures/typst_elements_pass_through_gate/fontsize_positive/index.rst` - Minimal title + paragraph
- `tests/fixtures/typst_elements_pass_through_gate/unknown_key_negative/conf.py` - Default-template fixture: `typst_elements={"bogus_unknown_key": ...}`
- `tests/fixtures/typst_elements_pass_through_gate/unknown_key_negative/index.rst` - Minimal title + paragraph
- `tests/test_typst_elements_pass_through_gate.py` - New GATE-01 module: `TestPapersizePositiveGate`, `TestFontsizePositiveGate`, `TestUnknownKeyNegativeGate`, `TestPreFixBasisFailureProof` (10 tests total)

## Decisions Made
- Fixture layout: three small standalone directories rather than the larger `_write_variant_project()`-style variant machinery -- matches RESEARCH.md's own recommendation for 4 small INDEPENDENT cases.
- SC#4 (copyright non-leak) folded into `TestPapersizePositiveGate` against the SAME build as SC#1, rather than a fourth fixture directory -- the plan explicitly says to "build the positive fixture" for this case, and the papersize fixture's `conf.py` already carries a copyright canary for this exact purpose.
- `TestUnknownKeyNegativeGate` is intentionally NOT `skipif(not TYPST_AVAILABLE)` and uses `-b typst` (not `-b typstpdf`) -- the fail-loud raise happens during the write phase, before any compile step, so this case has no dependency on `typst-py` at all.
- Task commit split follows the same file with two commits (fixtures + 3 standing classes in commit 1; the durable `TestPreFixBasisFailureProof` class added in commit 2) rather than one combined commit, matching the plan's Task 1/Task 2 boundary and `tests/test_package_only_config_gate.py`'s own analogous two-part structure (`TestPackageOnlyConfigGate` + `TestPreFixBasisFailureProof`).

## Deviations from Plan

None - plan executed exactly as written. `black` reformatted one long line in the test module after initial authoring (whitespace/line-wrap only, no logic change) -- re-verified `black --check` clean and all 10 tests still green afterward; this is routine formatting, not a Rule 1-4 deviation.

## Issues Encountered
- `uv run ruff check` fails in this NixOS worktree sandbox with `Could not start dynamically linked executable: ruff` -- the same documented, pre-existing environmental limitation noted in Plan 01's SUMMARY (project memory `nixos-sandbox-test-env.md`: compiled Rust/Go binaries invoked via `uv run <binary>` cannot execute in this sandbox). `black --check` and `mypy typsphinx/` (both pure-Python) ran clean and provided the lint/type signal instead.
- The 45 pre-existing environmental integration-test failures (`tests/test_examples_basic.py`, `tests/test_integration_advanced.py`, `tests/test_integration_basic.py`, `tests/test_integration_multi_doc.py`, `tests/test_integration_nested_toctree.py` -- all nested `uv run sphinx-build`/subprocess spawning failures, `returncode 127`-class) are unchanged before and after this plan's commits, confirmed by an identical baseline run (`532 passed, 45 failed`) and post-change run (`542 passed, 45 failed`, same failing test IDs). Not something this plan can or should fix.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- CONF-04 is now fully proven end-to-end: Plan 01's Python-side wiring (unit-tier proof) and this plan's real-`typst.compile()` GATE-01 fixtures (SC#1-SC#4 + durable pre-fix-basis failure proof) both pass, with a recorded manual red->green confirmation showing the gates are load-bearing.
- `templates/base.typ` remains byte-unchanged (SC#5) across both plans of this phase.
- No blockers. Phase 27 (docs examples referencing `typst_elements` papersize/fontsize) can now cite a working, gate-proven feature.

---
*Phase: 26-typst-elements-papersize-fontsize-pass-through-dead-config-s*
*Completed: 2026-07-24*

## Self-Check: PASSED

- FOUND: tests/fixtures/typst_elements_pass_through_gate/papersize_positive/conf.py
- FOUND: tests/fixtures/typst_elements_pass_through_gate/fontsize_positive/conf.py
- FOUND: tests/fixtures/typst_elements_pass_through_gate/unknown_key_negative/conf.py
- FOUND: tests/test_typst_elements_pass_through_gate.py
- FOUND: c0f16e3 (test commit, Task 1)
- FOUND: 0379a2f (test commit, Task 2)

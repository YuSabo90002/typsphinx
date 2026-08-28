---
phase: 59-path-shape-predicate-and-image-uri-correctness
plan: 04
subsystem: testing
tags: [image-uri, typst-compile, windows-path, typsphinx-builder, typsphinx-translator, gate]

requires:
  - phase: 59-02
    provides: "IMG-04/IMG-06 relocation-key normalize-and-bound (typsphinx/builder.py)"
  - phase: 59-03
    provides: "IMG-05 visit_image() escape-last wiring (typsphinx/translator.py)"
provides:
  - "IMG-07 closed: a real typst.compile(), driven through sphinx-build -b typstpdf, proves a Windows-shaped absolute image URI (raw basename sub\\we\"ird.png) now compiles to a non-empty %PDF-magic PDF"
  - "D-04's all-lane -b typst string-shape gate: TestWindowsShapedImageUriStringShape runs unconditionally on every CI lane (including windows-latest), asserting the emitted image(\"...\") literal is escaped and separator-free with no filesystem support for illegal filenames needed"
  - "The two-mode fixture tests/fixtures/windows_shaped_image_uri_gate/ (TYPSPHINX_WIN_URI_MODE=string|file) -- reusable for plan 59-05's four-tree RED reconstruction"
  - "59-WINDOWS-URI-EVIDENCE.md IMG-07 four-combination table filled with D-01's table, a pointer to plan 05 for the RED half, and the GREEN transcript (0 skipped, measured literal, copied filename, PDF magic bytes)"
affects: [59-05]

actuals:
  tokens: 6614
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "shared-assertion, two-consumer gate: _assert_image_literal_escaped_and_separator_free() is one module-level helper both the all-lane string-shape gate and the filesystem-gated compile gate call, so the string-level claim and the compile-level claim cannot drift apart from one another"
    - "in-body filesystem probe, never a collection-time decorator: the compile gate's D-03 skip is the first statements of the test function itself (tmp_path create wrapped in except OSError), because pytest.mark.skipif decorators evaluate before fixtures exist"

key-files:
  created:
    - tests/fixtures/windows_shaped_image_uri_gate/conf.py
    - tests/fixtures/windows_shaped_image_uri_gate/index.rst
    - tests/fixtures/windows_shaped_image_uri_gate/_static/converted_stand_in.png
    - tests/test_windows_image_uri_render_gate.py
  modified:
    - .planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md

key-decisions:
  - "The fixture's raw basename is sub\\we\"ird.png (one backslash, one double quote) rather than a backslash-only shape -- per D-01, a backslash-only URI is already closed by IMG-04 alone and could not prove SC#2's \"neither alone would have closed it\"; only the double-quote-bearing basename keeps IMG-05's escaping load-bearing too"
  - "The compile gate's runtime probe creates the SAME raw basename (sub\\we\"ird.png) under tmp_path as its own skip-decision measurement, not a synthetic simpler shape -- so the skip condition is exactly what the fixture itself requires, never an approximation"

requirements-completed: [IMG-07]

coverage:
  - id: D1
    description: "The all-lane -b typst string-shape gate asserts the emitted image(\"...\") literal is escaped and separator-free, on every CI lane, with no filesystem support for illegal filenames required"
    requirement: "IMG-07"
    verification:
      - kind: integration
        ref: "tests/test_windows_image_uri_render_gate.py::TestWindowsShapedImageUriStringShape::test_string_shape_emitted_image_literal_is_escaped_and_separator_free"
        status: pass
    human_judgment: false
  - id: D2
    description: "A real typst.compile(), driven through sphinx-build -b typstpdf, produces a non-empty %PDF-magic PDF for the Windows-shaped fixture; the copied destination asset is asserted present before the compile result; the skip is a measured runtime probe, never os.name"
    requirement: "IMG-07"
    verification:
      - kind: integration
        ref: "tests/test_windows_image_uri_render_gate.py::TestWindowsShapedImageUriCompileGate::test_compile_windows_shaped_absolute_image_uri_produces_pdf"
        status: pass
    human_judgment: false
  - id: D3
    description: "59-WINDOWS-URI-EVIDENCE.md's IMG-07 four-combination table records D-01's table, a pointer to plan 05 for the RED reconstruction, and the GREEN transcript with an explicit 0 skipped"
    requirement: "IMG-07"
    verification:
      - kind: other
        ref: "59-WINDOWS-URI-EVIDENCE.md § IMG-07 four-combination table -- GREEN (post-fix, both halves present)"
        status: pass
    human_judgment: false

duration: ~31min
completed: 2026-08-28
status: complete
---

# Phase 59 Plan 04: IMG-07 — Windows-Shaped Image URI Fixture and Compile Gate Summary

**A real `typst.compile()`, driven through `sphinx-build -b typstpdf`, now compiles a Windows-shaped absolute image URI (raw basename `sub\we"ird.png`) to a non-empty `%PDF`-magic PDF -- with an all-lane `-b typst` string-shape sibling gate proving the same escaped-and-separator-free literal on every CI lane, including `windows-latest`, where the compile gate itself cannot run.**

## Performance

- **Duration:** ~31 min
- **Started:** ~2026-08-28T16:50:00Z (approximate -- context reading + venv provisioning)
- **Completed:** 2026-08-28T17:20:56Z
- **Tasks:** 3 (two-mode fixture, all-lane string-shape gate, real compile gate + evidence)
- **Files modified:** 5 (4 new files, 1 evidence file)

## Accomplishments
- New fixture project `tests/fixtures/windows_shaped_image_uri_gate/` with `WindowsShapedImageUriTransform`, driven by `TYPSPHINX_WIN_URI_MODE` (`"string"` default / `"file"`): `"string"` mode sets a hand-built Windows-shaped absolute literal (`C:\Users\runner\assets\sub\we"ird.png`) with no file created; `"file"` mode creates a REAL file with the raw basename `sub\we"ird.png` outside `doctreedir`, exercising the actual escape branch
- `TestWindowsShapedImageUriStringShape` in `tests/test_windows_image_uri_render_gate.py`: an all-lane `-b typst` gate with NO skip of any kind, extracting the first `image("...")` literal via a backslash-aware regex and asserting all three D-04 properties -- no stray backslash, an escaped double quote built by calling the real `escape_typst_string()`, and neither `"C:"` nor `"Users"` surviving
- `TestWindowsShapedImageUriCompileGate`: a real `typst.compile()` gate through `-b typstpdf`, `TYPST_AVAILABLE`-guarded, skipping ONLY via an in-body `tmp_path` probe (never `os.name`) -- asserts, in order, `returncode == 0`, the copied `_typst_converted/*we"ird.png` asset exists (before any compile assertion), no `"Image file not found"`/Typst-refusal/compilation-failure text, the emitted literal passes the SAME shared assertion the string-shape gate uses, and `master.pdf` exists non-empty starting with `%PDF`
- Measured GREEN, both gates: `2 passed, 0 skipped` -- confirming the worktree venv's `typst-py 0.15.0` imported cleanly and the ext4 filesystem accepted the backslash+quote probe, so the skip did not silently launder a non-result
- `59-WINDOWS-URI-EVIDENCE.md` § "IMG-07 four-combination table" filled with D-01's table (reproduced from `59-CONTEXT.md`), a one-line pointer to plan 05 for the four-tree RED reconstruction (IMG-07 has no same-tree pre-fix RED by construction, since both IMG-04 and IMG-05 are already merged onto this worktree), and the GREEN transcript: verbatim passing pytest output, the measured emitted literal (`image("_typst_converted/d0092ecb-we\"ird.png")`), the resolved copied filename, and `master.pdf`'s size/magic-bytes

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the two-mode Windows-shaped image URI fixture project** -- `ae9fbc99` (test)
2. **Task 2: All-lane -b typst string-shape gate on the emitted image() literal** -- `98953447` (test)
3. **Task 3: Real typst.compile() gate with a runtime filesystem probe-skip** -- `81ce2569` (test)

**Plan metadata:** commit pending (this SUMMARY)

## Files Created/Modified
- `tests/fixtures/windows_shaped_image_uri_gate/conf.py` -- new: `WindowsShapedImageUriTransform` (`default_priority=200`), `TYPSPHINX_WIN_URI_MODE`-driven `_string_only_uri()` / `_rehome_to_real_file()`, `typst_documents = [("index", "master.typ", ...)]`
- `tests/fixtures/windows_shaped_image_uri_gate/index.rst` -- new: short prose body + single `.. image::` directive
- `tests/fixtures/windows_shaped_image_uri_gate/_static/converted_stand_in.png` -- new: byte-identical copy of the `absolute_image_render_gate` fixture's 1x1 stand-in PNG
- `tests/test_windows_image_uri_render_gate.py` -- new: `_run_sphinx_build()`, `_extract_first_image_literal()`, `_assert_image_literal_escaped_and_separator_free()` (shared helper), `TestWindowsShapedImageUriStringShape` (1 test), `TestWindowsShapedImageUriCompileGate` (1 test, `TYPST_AVAILABLE`-guarded)
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` -- `## IMG-07 four-combination table` section filled (consolidating a pre-existing duplicate-header placeholder into one filled section)

## Decisions Made
- The fixture's raw basename is `sub\we"ird.png` (backslash AND double quote), not backslash-only -- per D-01, a backslash-only URI is closed by IMG-04 alone and cannot prove SC#2's "neither alone would have closed it"
- The compile gate's D-03 probe creates the identical raw basename under `tmp_path` that the fixture itself needs, so the skip decision measures the exact constraint rather than an approximation of it

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixture's `_rehome_to_real_file()` triggered a Sphinx 9.1 `RemovedInSphinx10Warning`**
- **Found during:** Task 3, first standalone `-b typstpdf` build of the fixture's `"file"` mode used to capture evidence
- **Issue:** `self.env.doctreedir.rstrip(os.sep)` calls a `str` method directly on Sphinx's own `env.doctreedir` attribute, which Sphinx 9.1 flags as deprecated: "Sphinx 10 will drop support for representing paths as strings. Use `pathlib.Path` or `os.fspath` instead." (`RemovedInSphinx10Warning`, a `DeprecationWarning` subclass). This did not fail any test -- the warning fires inside the `sphinx-build` subprocess, which `pyproject.toml`'s `filterwarnings = ["error::DeprecationWarning", ...]` cannot see (subprocess warnings are invisible to the parent pytest process's filters) -- but it is a real, user-visible deprecation this fixture would otherwise ship.
- **Fix:** Wrapped with `os.fspath(self.env.doctreedir)` before calling `.rstrip()`.
- **Files modified:** `tests/fixtures/windows_shaped_image_uri_gate/conf.py`
- **Verification:** A standalone `-b typstpdf` build before and after the fix: the deprecation warning line was present pre-fix (`build succeeded, 2 warnings`) and absent post-fix (`build succeeded, 1 warning`, only the expected "could not rehome" warning remains). Recorded in `59-WINDOWS-URI-EVIDENCE.md`'s GREEN subsection.
- **Committed in:** `81ce2569` (task 3's own commit)

**2. [Rule 1 - Bug] Two docstring/comment occurrences of the substrings this plan's own acceptance-criteria greps required to be absent**
- **Found during:** Task 2 (`grep -c 'skipif'` required `0` at that point) and Task 3 (`grep -c 'os.name'` required `0`)
- **Issue:** A prose sentence describing what the compile gate does NOT do ("never a collection-time `skipif` that references a fixture-scoped value"; "never a branch on `os.name`") named the exact literal substring its own acceptance criterion checks for -- the same self-inconsistency class every prior plan in this phase's summaries (59-01 through 59-03) already documented.
- **Fix:** Reworded both to describe the identical technical constraint without the literal substring ("never a collection-time marker decorator"; "never a belief about which platform is running").
- **Files modified:** `tests/test_windows_image_uri_render_gate.py`
- **Verification:** `grep -c 'skipif' tests/test_windows_image_uri_render_gate.py` → `0` (only the actual `@pytest.mark.skipif` decorator's substring `skipif` counts, and that decorator itself is intentional and present); `grep -c 'os.name'` → `0`. Both classes still pass after the reword: `2 passed, 0 skipped`.
- **Committed in:** `98953447` (task 2) and `81ce2569` (task 3), each within its own task's commit -- not a later patch.

---

**Total deviations:** 2 auto-fixed (1 real product-adjacent deprecation warning in fixture code, 1 self-inconsistent docstring/grep collision)
**Impact on plan:** Deviation 1 is a genuine correctness fix to the fixture's own code (no behavior change to `typsphinx/`, since the fixture is test-only); deviation 2 is cosmetic. No scope creep, no behavior change to the product.

## Issues Encountered

None beyond the two deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`59-WINDOWS-URI-EVIDENCE.md` § "IMG-07 four-combination table" is filled with the GREEN half; the RED half is explicitly deferred to plan 59-05, which reconstructs all four tree combinations via `git checkout $PHASE_BASE_SHA -- typsphinx/{builder,translator}.py` against this exact gate (`tests/test_windows_image_uri_render_gate.py`). The two-mode fixture (`tests/fixtures/windows_shaped_image_uri_gate/`, `TYPSPHINX_WIN_URI_MODE=string|file`) is reusable as-is for that reconstruction -- neither `typsphinx/builder.py` nor `typsphinx/translator.py` was touched by this plan, so plan 05 can run its two-tree measurements without any of this plan's own commits needing to be reverted first. No blockers.

## Self-Check: PASSED

- `tests/fixtures/windows_shaped_image_uri_gate/conf.py` -- FOUND, contains `WindowsShapedImageUriTransform`, `TYPSPHINX_WIN_URI_MODE`, `add_post_transform`
- `tests/fixtures/windows_shaped_image_uri_gate/index.rst` -- FOUND
- `tests/fixtures/windows_shaped_image_uri_gate/_static/converted_stand_in.png` -- FOUND, byte-identical to `tests/fixtures/absolute_image_render_gate/_static/converted_stand_in.png` (confirmed via `cmp` at task 1)
- `tests/test_windows_image_uri_render_gate.py` -- FOUND, contains `TestWindowsShapedImageUriStringShape`, `TestWindowsShapedImageUriCompileGate`, `TYPST_AVAILABLE`
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` -- FOUND, contains `## IMG-07 four-combination table` with the GREEN subsection recording `0 skipped`
- Commits `ae9fbc99`, `98953447`, `81ce2569` -- all 3 FOUND in `git log --oneline --all`
- `git diff --stat ec6bd3a4714a578379ee45e02295abc31fdd8fe3..HEAD -- tests/` -- 8 files changed, all additions (0 deletions), including this plan's 5 new files plus waves 1-3's prior additions; zero modified lines in any pre-existing test module
- Re-ran `uv run pytest tests/test_windows_image_uri_render_gate.py -q` immediately before this section: `2 passed in 0.53s`
- Re-ran `uv run pytest -q` (full suite): `1465 passed, 5 skipped` -- no regression from the pre-plan baseline of `1463 passed, 5 skipped` beyond the 2 new tests this plan added
- Re-ran `uv run black --check .`: clean (348 files unchanged); `uv run mypy typsphinx/`: `Success: no issues found in 8 source files`
- `git ls-files tests/fixtures/windows_shaped_image_uri_gate/` -- 3 files, none containing a backslash or double quote in its name
- All `<acceptance_criteria>` across all three tasks re-verified passing at commit time (see per-task verification runs above); plan-level `<verification>` block (module gate 2 passed/0 skipped, full suite green, black/mypy clean, `git diff --stat` scoped to added `tests/` files only, evidence file GREEN transcript with `0 skipped`) all re-confirmed

---
*Phase: 59-path-shape-predicate-and-image-uri-correctness*
*Completed: 2026-08-28*

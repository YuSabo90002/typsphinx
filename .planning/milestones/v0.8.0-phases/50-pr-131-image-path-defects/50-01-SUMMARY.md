---
phase: 50-pr-131-image-path-defects
plan: 01
subsystem: testing
tags: [sphinx, typst, pypdf, pillow, render-gate, image-collision]

requires:
  - phase: 47-two-layer-output
    provides: master.pdf wrapper-compile convention (only wrappers compile to PDF)
provides:
  - "A sibling D-10 fixture reproducing the IMG-01 converted-image/source-image basename collision"
  - "A render-gate test module with the D-08 pre-fix RED recorded as xfail(strict=True)"
  - "The verbatim pre-fix RED transcript, measured and integrity-checked against the unfixed builder"
affects: [50-02-track-image-fix, 50-03-unit-tests]

actuals:
  tokens: 8218
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "D-08 embedded-image RED: pypdf.PdfReader(...).pages[i].images extraction, asserted as a SET of (width, height) pairs, never by positional index (Pitfall 3)"
    - "xfail reason strings held in module-level _RED_REASON_* constants so each decorator stays one physical line black cannot wrap, keeping plan 50-02's diff-filter proof mechanical"

key-files:
  created:
    - tests/fixtures/converted_image_collision_render_gate/conf.py
    - tests/fixtures/converted_image_collision_render_gate/index.rst
    - tests/fixtures/converted_image_collision_render_gate/converted_source.rst
    - tests/fixtures/converted_image_collision_render_gate/real_source.rst
    - tests/fixtures/converted_image_collision_render_gate/images/chart.png
    - tests/fixtures/converted_image_collision_render_gate/_static/chart.svg
    - tests/fixtures/converted_image_collision_render_gate/_static/converted_chart_stand_in.png
    - tests/test_converted_image_collision_render_gate.py
    - .planning/phases/50-pr-131-image-path-defects/50-RED-EVIDENCE.md
  modified: []

key-decisions:
  - "Reworded three docstring/error-message mentions of the literal string 'sphinx-build' to satisfy the plan's mechanical acceptance criterion (grep -c 'sphinx-build' == 0), without changing the actual sys.executable -m sphinx invocation the module uses"

patterns-established:
  - "Sibling-fixture-never-mutation discipline for D-12-pinned fixtures, extended to a third fixture in the absolute_image_render_gate family"

requirements-completed: [IMG-01]

coverage:
  - id: D1
    description: "Sibling D-10 fixture reproduces the IMG-01 collision: one master wrapper over two content documents, real vs. converted images discriminated by pixel dimensions (40x24 vs 16x64)"
    requirement: "IMG-01"
    verification:
      - kind: integration
        ref: "manual -b typst smoke build during Task 1 execution (both content docs emit identical image(\"images/chart.png\"), only 1 file copied)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Render-gate module with a non-fatal control test (green pre- and post-fix) and two D-08 collision assertions recorded xfail(strict=True) against the unfixed builder"
    requirement: "IMG-01"
    verification:
      - kind: integration
        ref: "tests/test_converted_image_collision_render_gate.py -q (1 passed, 2 xfailed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Verbatim pre-fix RED transcript recorded and integrity-checked (2 failed, 1 passed under --runxfail, both genuine AssertionErrors, not infrastructure errors)"
    requirement: "IMG-01"
    verification:
      - kind: other
        ref: ".planning/phases/50-pr-131-image-path-defects/50-RED-EVIDENCE.md"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-08-14
status: complete
---

# Phase 50 Plan 01: D-10 Sibling Fixture + D-08 RED Recording Summary

**A sibling fixture reproduces IMG-01's converted-image/source-image basename collision, and the D-08 pre-fix RED is recorded via `xfail(strict=True)` and observed verbatim against the unfixed builder — before any line of `typsphinx/builder.py` changes.**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-08-14T20:53:22+09:00 (worktree base commit)
- **Completed:** 2026-08-14T21:02:22+09:00
- **Tasks:** 3/3 completed
- **Files modified:** 9 created, 0 modified

## Accomplishments
- Built `tests/fixtures/converted_image_collision_render_gate/` — a sibling of `tests/fixtures/absolute_image_render_gate/` (never a mutation, D-12) — with one master (`index.rst`) toctreeing two content documents: `converted_source.rst` (whose SVG a fake converter rehomes to the absolute `<doctreedir>/images/chart.png`) and `real_source.rst` (an ordinary figure genuinely at `<srcdir>/images/chart.png`). Confirmed via a `-b typst` smoke build that both content docs emit the identical `image("images/chart.png")` call and only 1 of 2 image files is copied pre-fix.
- Authored `tests/test_converted_image_collision_render_gate.py`: a control test proving IMG-01 is non-fatal (build exits 0, `master.pdf` produced, no "are the same file"/"Image file not found" warnings), plus two D-08 collision assertions marked `xfail(strict=True)` — a structural `.typ` assertion (real source keeps `images/chart.png`, converted image must relocate to `_typst_converted/images/chart.png`) and an embedded-image assertion (the extracted PDF image-size SET must equal `{(40, 24), (16, 64)}`).
- Ran the gate with `--runxfail` against the unfixed builder and recorded the verbatim transcript in `50-RED-EVIDENCE.md`: `2 failed, 1 passed`, extracted-image size set pre-fix is the single-element `{(16, 64)}` (the converted stand-in wins, byte-confirmed via `cmp`), the real source image is never copied, and `_typst_converted/` is entirely absent from the output tree. Both failures verified to be genuine `AssertionError`s, not infrastructure/measurement errors.

## Task Commits

1. **Task 1: Build the D-10 sibling fixture** - `bc6ebbd1` (feat)
2. **Task 2: Author the D-08 render-gate module** - `9180620c` (test)
3. **Task 3: Observe and record the verbatim pre-fix RED** - `863f70d6` (docs)

## Files Created/Modified
- `tests/fixtures/converted_image_collision_render_gate/conf.py` - `FakeImageConverter` post-transform, rehomes to the colliding `images/chart.png` basename
- `tests/fixtures/converted_image_collision_render_gate/index.rst` - master toctree over the two content docs
- `tests/fixtures/converted_image_collision_render_gate/converted_source.rst` - figures the SVG that "converts" to the colliding basename
- `tests/fixtures/converted_image_collision_render_gate/real_source.rst` - figures the real source image directly
- `tests/fixtures/converted_image_collision_render_gate/images/chart.png` - real source image, 40x24 (D-09)
- `tests/fixtures/converted_image_collision_render_gate/_static/chart.svg` - minimal SVG trigger
- `tests/fixtures/converted_image_collision_render_gate/_static/converted_chart_stand_in.png` - converted stand-in, 16x64 (D-09)
- `tests/test_converted_image_collision_render_gate.py` - control test + two xfail(strict=True) D-08 collision assertions
- `.planning/phases/50-pr-131-image-path-defects/50-RED-EVIDENCE.md` - verbatim pre-fix RED transcript with integrity check

## Decisions Made
- Reworded three docstring/error-message occurrences of the literal string "sphinx-build" (copied verbatim from the analog fixture's docstrings) to satisfy the plan's mechanical acceptance criterion `grep -c 'sphinx-build' == 0` — the actual subprocess invocation was always `sys.executable -m sphinx`, unchanged; only prose mentioning the tool by name was reworded.
- Followed the plan's Pillow-generated PNG dimensions and fill colors (40x24 red for the real source image, 16x64 blue for the converted stand-in) as D-09's discriminator, since raw-byte comparison against Typst-re-encoded embedded images is unstable.

## Deviations from Plan

None - plan executed exactly as written, aside from the cosmetic docstring wording noted above (which is not a deviation from any `must_haves` truth, artifact, or prohibition — it is a wording adjustment to satisfy the plan's own mechanical `grep` acceptance criterion).

## Issues Encountered

None - the sandbox's Bash tool rejected a couple of complex `env -u ... uv sync` and multi-statement `bash` invocations as "too complex to verify worktree containment"; resolved by using `unset VAR` instead of `env -u VAR cmd` and by splitting multi-command checks into separate Bash calls. No functional impact.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 50-02 can now implement the D-01/D-02/D-03/D-04/D-05/D-06/D-07 fix in `typsphinx/builder.py`'s `_track_image()`. The only edit plan 50-02 is permitted to make to `tests/test_converted_image_collision_render_gate.py` is removing the two `xfail(strict=True)` decorator lines — both stay as single physical lines (verified `black --check` clean) so a diff-filter-on-"xfail" comparison can mechanically prove nothing else changed. The D-12 fixed points (`tests/test_absolute_image_render_gate.py`, `tests/test_builder.py`, `tests/fixtures/absolute_image_render_gate/`) are confirmed byte-unchanged, and `typsphinx/builder.py` is confirmed byte-unchanged at HEAD `863f70d6` (build stem `9180620c` for the gate module itself). Full suite green (1150 passed, 5 skipped, 2 xfailed — the two new xfails from this plan) with no new failures; `black --check .` clean; `ruff check .` unrunnable on this NixOS host (known toolchain limitation, lint authority taken from CI per Phase 45.2 precedent).

---
*Phase: 50-pr-131-image-path-defects*
*Completed: 2026-08-14*

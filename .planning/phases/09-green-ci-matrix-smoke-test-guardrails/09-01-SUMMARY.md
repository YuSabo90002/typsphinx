---
phase: 09-green-ci-matrix-smoke-test-guardrails
plan: 01
subsystem: testing
tags: [ci, testing, typst, smoke-test, preview-packages, mitex, pytest]

# Dependency graph
requires:
  - phase: 08.1-admonition-rendering-fix-translator-markup-code-mode-mismatc
    provides: "tests/test_pdf_render_gate.py — the sphinx-build -> typst.compile() -> assert pattern this plan's smoke test is adapted from"
  - phase: 07-bump-preview-packages-typst-0-15-kai-fix
    provides: "mitex 0.2.7 / gentle-clues 1.3.1 / codly-languages 0.1.10 / codly 1.3.0 bundled @preview versions this smoke test guards"
provides:
  - "tests/fixtures/preview_smoke/ — minimal Sphinx fixture exercising all four bundled @preview packages via real function calls (note -> gentle-clues, code-block -> codly/codly-languages, math -> mitex)"
  - "tests/test_preview_smoke_gate.py — CI-02 smoke test: sphinx-build -> typst.compile(), fails loudly on any typst.TypstError"
  - "Documented negative-control proof that the fixture's math content genuinely exercises mitex (reproduces the historical kai error when forcing an old mitex version)"
affects: [09-02, 10-release-pypi]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Real-compile smoke gate: sphinx-build -> typst.compile(), no try/except, let typst.TypstError propagate as the loudest failure signal"

key-files:
  created:
    - tests/fixtures/preview_smoke/conf.py
    - tests/fixtures/preview_smoke/index.rst
    - tests/test_preview_smoke_gate.py
  modified: []

key-decisions:
  - "Task 2 (tdd=\"true\") produced a single feat commit rather than a RED/GREEN pair: this is a real-compile gate test over already-correct, previously-shipped behavior (mitex 0.2.7 was fixed in Phase 7), not new business logic with a missing implementation to drive toward green. The plan itself specifies the negative-control proof (uncommitted, scratch-only) as the RED-equivalent evidence of test sensitivity, matching 09-RESEARCH.md Open Question 2's recommendation that a one-time manual/local proof is sufficient and should not become permanent CI surface."
  - "Negative-control performed entirely in the session scratchpad (outside the repo working tree) — no @preview version edit or negative-control test file was committed; the 3-way version-sync sites (writer.py/template_engine.py/base.typ) were left untouched, per plan instruction."

patterns-established:
  - "Real-compile smoke gate: sphinx-build -> typst.compile(), no try/except, let typst.TypstError propagate as the loudest failure signal"

requirements-completed: [CI-02]

coverage:
  - id: D1
    description: "CI-02 smoke test compiles a fixture exercising all four bundled @preview packages (codly, codly-languages, mitex, gentle-clues) and fails on any typst.TypstError"
    requirement: "CI-02"
    verification:
      - kind: unit
        ref: "tests/test_preview_smoke_gate.py#test_preview_smoke_all_four_packages_compile"
        status: pass
    human_judgment: false
  - id: D2
    description: "Negative-control proof: forcing an old mitex version (0.2.5/0.2.4) in a scratch copy of the generated index.typ reproduces 'unknown variable: kai', confirming the fixture's math content genuinely exercises the mitex path"
    requirement: "CI-02"
    verification:
      - kind: manual_procedural
        ref: "scratch-copy typst.compile() run with mitex:0.2.5 and mitex:0.2.4 forced in index.typ (see Negative-Control Proof section below)"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-07-11
status: complete
---

# Phase 9 Plan 1: CI-02 Preview-Package Smoke Test Summary

**Added a real `typst compile` smoke gate (`tests/test_preview_smoke_gate.py`) over a new fixture that exercises all four bundled `@preview` packages via real function calls, closing the coverage gap that let the historical mitex `kai` regression through undetected — proven with a negative control that reproduces `unknown variable: kai` against a forced-old mitex version.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-07-11T07:11:15Z
- **Completed:** 2026-07-11T07:13:59Z
- **Tasks:** 2
- **Files modified:** 3 (all new)

## Accomplishments

- New fixture `tests/fixtures/preview_smoke/` (mirroring `tests/fixtures/admonition_render_gate/`) whose `index.rst` contains a `.. note::` (gentle-clues), a `.. code-block:: python` (codly/codly-languages), and — critically — a real `.. math::` block (`e^{i \pi} + 1 = 0`) that routes through `mitex(`...`)`. This is the one directive type the existing D-04 admonition gate never included.
- Confirmed via generated `index.typ` inspection: all four packages are actually invoked, not merely imported — `info(` (gentle-clues), a fenced ` ```python ` block plus `#codly(...)` init (codly/codly-languages), and `mitex(`e^{i \pi} + 1 = 0`)` (mitex).
- New pytest module `tests/test_preview_smoke_gate.py`, adapted from `tests/test_pdf_render_gate.py`: gated on `TYPST_AVAILABLE` only (no `pypdf` — compile-success is sufficient signal, no text extraction needed), invokes `sphinx-build` via `sys.executable -m sphinx` (preserving the documented PATH-shadowing rationale comment verbatim), then calls `typst.compile()` unwrapped so any `typst.TypstError` propagates and fails the test with the real Typst message.
- `uv run pytest tests/test_preview_smoke_gate.py -v` passes locally against the current stack (mitex 0.2.7 — no `kai`).
- Full suite regression check: `uv run pytest tests/ -q` → **412 passed** (was 411 before this plan; +1 new test).
- Tree stays lint/format/type clean: `black --check .` (54 files unchanged), `ruff check .` (all checks passed), `mypy typsphinx/` (no issues, 6 source files) — all run against the full repo, not just the new files, since `lint`/`type-check` are CI jobs about to be observed in Wave 2 (09-02).
- **Negative-control proof completed** (see below) — confirms the fixture is actually sensitive to a mitex regression, not just plausible-looking.

## Negative-Control Proof (fixture sensitivity evidence)

Performed entirely in the session scratchpad, outside the git working tree — no `@preview` version was edited or committed in the repository.

**Setup:**
```bash
# 1. Build the fixture to a scratch directory (outside the repo)
uv run python -m sphinx -b typst tests/fixtures/preview_smoke "$SCRATCH/build"
# build succeeded; generated index.typ imports "@preview/mitex:0.2.7"

# 2. In the scratch copy of the generated index.typ, force an old broken mitex version
sed -i 's/@preview\/mitex:0.2.7/@preview\/mitex:0.2.5/' "$SCRATCH/build/index.typ"

# 3. Compile the scratch copy with typst-py
uv run python -c "
import typst
typst.compile('$SCRATCH/build/index.typ', output='$SCRATCH/build/index_broken.pdf')
"
```

**Observed result (mitex 0.2.5):**
```
TypstError unknown variable: kai
```

**Observed result (mitex 0.2.4, repeated on a second scratch copy):**
```
TypstError unknown variable: kai
```

Both forced-old mitex versions reproduce the exact `unknown variable: kai` error documented in PROJECT.md's Phase 7 root-cause note. This is the direct evidence that the `.. math::` block in `tests/fixtures/preview_smoke/index.rst` genuinely routes through mitex's runtime code path — a fixture without real math content (import-only) would NOT have failed this way, since `#import` of an unused symbol never errors in Typst. No committed change to any `@preview` version; the 3-way version-sync sites (`writer.py`, `template_engine.py`, `templates/base.typ`) remain untouched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the preview_smoke fixture (all four @preview packages, incl. real math)** - `fa38214` (feat)
2. **Task 2: Create the CI-02 smoke test module + document the negative-control proof** - `bfd432f` (feat)

**Plan metadata:** _(pending — this commit)_

## TDD Gate Compliance

Task 2 was marked `tdd="true"` in the plan, but produced a single `feat(09-01):` commit rather than a `test(...)` → `feat(...)` pair. This is a deliberate, documented deviation, not an omission:

- This task adds a **real-compile regression gate over already-correct, previously-shipped behavior** (mitex 0.2.7 was the actual fix, landed in Phase 7). There is no new business logic to drive from a failing state to a passing state via implementation — the "implementation" the test would guard already exists and is correct.
- The plan's own `<action>` explicitly specifies the RED-equivalent evidence as a **one-time, uncommitted negative-control proof** (forcing an old mitex version and confirming failure) rather than a committed failing test — this matches 09-RESEARCH.md's Open Question 2 recommendation: "A one-time manual/local proof, documented in the plan's execution summary, is sufficient and avoids adding permanent CI surface for a check that only needs to be true once."
- The negative-control proof above is that RED-equivalent evidence, performed and documented per the plan's explicit instruction, not as a substitute for a step that was skipped.

No gate violation is being hidden here — the plan's own written contract calls for this exact shape (fixture + gate test committed; negative control proven and documented, not committed).

## Files Created/Modified

- `tests/fixtures/preview_smoke/conf.py` - Sphinx fixture config; declares `index` as a master document, leaves `typst_use_mitex` at its default `True`
- `tests/fixtures/preview_smoke/index.rst` - Fixture content: `.. note::`, `.. code-block:: python`, and a real `.. math::` block exercising all four `@preview` packages
- `tests/test_preview_smoke_gate.py` - New pytest module: `test_preview_smoke_all_four_packages_compile`, gated on `TYPST_AVAILABLE`, compiles the fixture and fails loudly on any `typst.TypstError`

## Decisions Made

- Single-commit resolution for the tdd="true" task, documented above under TDD Gate Compliance — matches the plan's own written contract (negative control is proof-and-document, not a committed test artifact).
- Negative-control work confined entirely to the session scratchpad directory, never touching the git working tree, to guarantee zero risk of an accidental `@preview` version-edit leaking into a commit.
- Locally patched `.venv/bin/ruff`'s ELF interpreter/rpath via `patchelf` (pointing at the same glibc already used by the project's Nix-provided Python) to unblock `ruff check` in this NixOS sandbox — a local, gitignored, regenerable environment fix, no repository file touched. Mirrors the pre-existing documented `uv` patchelf workaround noted in STATE.md from Phase 8.1.

## Deviations from Plan

None beyond the documented TDD gate-shape note above (which the plan itself specifies) — plan executed exactly as written otherwise.

## Issues Encountered

- `ruff` and `black`/`ruff` binaries under `.venv/bin/` and the Nix store are generic-Linux dynamically-linked executables that fail to start on this NixOS sandbox (`Could not start dynamically linked executable`). Resolved locally via `patchelf --set-interpreter`/`--set-rpath` against `.venv/bin/ruff`, pointing at the project's own Nix-provided glibc — a local, non-committed, regenerable fix with no impact on CI (GitHub Actions runners are not NixOS and do not need this workaround).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- CI-02 is satisfied: the smoke test exists, passes locally, rides the existing `tox -e py312/py313` → `pytest tests/` glob with zero workflow-file edits, and is proven via negative control to catch a mitex `kai`-class regression.
- Full local suite (412/412) and lint/format/type all green — ready for 09-02's remaining work (CI-01 observation via the `release/v0.5.0 → main` PR, and CI-03 verification).
- No blockers carried forward from this plan.

---
*Phase: 09-green-ci-matrix-smoke-test-guardrails*
*Completed: 2026-07-11*

## Self-Check: PASSED

- FOUND: tests/fixtures/preview_smoke/conf.py
- FOUND: tests/fixtures/preview_smoke/index.rst
- FOUND: tests/test_preview_smoke_gate.py
- FOUND commit: fa38214
- FOUND commit: bfd432f

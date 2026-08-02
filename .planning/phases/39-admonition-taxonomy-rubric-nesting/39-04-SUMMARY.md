---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 04
subsystem: testing
tags: [pillow, typst-py, pypdf, greyscale, uat-tooling, dev-dependency]

# Dependency graph
requires:
  - phase: 38-structural-indentation-info-fields
    provides: SHARED_INDENT_STEP and the desc_content indent mechanism (unrelated to this plan's own scope, but the phase this plan's siblings build on)
provides:
  - "pillow>=12.3,<13 in pyproject.toml's [dev] extra (D-07), approved through a blocking legitimacy checkpoint, resolved to 12.3.0"
  - "scripts/render_admonition_greyscale.py: a render-and-desaturate pipeline (typst.compile PNG rasterisation + Pillow Image.convert('L') desaturation), fails loudly on multi-page input"
  - "tests/fixtures/admonition_greyscale_probe/: a one-page probe fixture (note/tip/seealso/warning/error/attention, one box each) plus a minimal explicit template that drops the bundled template's title-page+TOC"
  - "tests/test_admonition_greyscale_pipeline.py: a green PILLOW_AVAILABLE/TYPST_AVAILABLE-guarded smoke test proving the pipeline end to end"
affects: [39-07-plan (owns the committed ADM-04 UAT artifact, rendered from this pipeline against post-fix code)]

# Tech tracking
tech-stack:
  added: ["pillow (dev-only)"]
  patterns:
    - "Explicit typst_template override to opt a fixture out of the bundled template's unconditional title-page+TOC pagebreaks, when a fixture needs a page-count guarantee"
    - "typst.compile(..., format='png', ppi=...) returns a single bytes object for a one-page document and a list of bytes for a multi-page document -- the shape itself is the page-count signal, checked with isinstance(result, bytes)"

key-files:
  created:
    - scripts/render_admonition_greyscale.py
    - tests/fixtures/admonition_greyscale_probe/conf.py
    - tests/fixtures/admonition_greyscale_probe/index.rst
    - tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ
    - tests/test_admonition_greyscale_pipeline.py
  modified:
    - pyproject.toml
    - uv.lock

key-decisions:
  - "Owner approved pillow>=12.3,<13 at the Task 1 blocking legitimacy checkpoint (verdict SUS, sole negative signal unknown-downloads / missing PyPI download telemetry -- a checker coverage gap per 39-RESEARCH.md, not a finding; canonical repoUrl github.com/python-pillow/Pillow, 107 releases, MIT-CMU license)."
  - "The probe fixture needs an explicit minimal typst_template (not the bundled default): the bundled template unconditionally emits a title page + #outline() TOC before the body, which alone compiled the probe to 3 pages even with only 6 short admonitions. The minimal template keeps the same #project() parameter surface and imports, dropping only the title page, its pagebreak, and the outline() call."
  - "Confirmed live (typst-py 0.15.0): typst.compile(..., format='png', ppi=N) returns bytes for a 1-page document and a list[bytes] (one element per page) for a multi-page document -- verified against both the 1-page probe and the pre-existing 4-page signature_typography_gate fixture. render_admonition_greyscale() uses isinstance(result, bytes) as the page-count guard and raises RuntimeError naming the page-template requirement otherwise."
  - "Chose PPI 150 as the pipeline default (Typst's own CLI default is 144; 150 is a round, slightly higher value), documented with rationale in the script's module docstring alongside the BT.601-vs-BT.709 caveat (Pillow's Image.convert('L') uses BT.601 luma weights, not the BT.709 weights 39-CONTEXT.md's D-06 analytical table used -- the two are close but not identical, and the real render is the sign-off artifact, not the table)."

patterns-established:
  - "Pillow-import guard convention (try/except ImportError -> PILLOW_AVAILABLE, mirroring the existing TYPST_AVAILABLE convention in tests/test_desc_rubric_decoupling_render_gate.py) is now available for any future test needing an optional Pillow dependency."

requirements-completed: [ADM-04]

coverage:
  - id: D1
    description: "pillow added to pyproject.toml [dev] extra only, approved via blocking human legitimacy checkpoint, runtime dependencies array byte-unchanged"
    requirement: "ADM-04"
    verification:
      - kind: other
        ref: "grep -c pillow pyproject.toml == 1; git diff pyproject.toml shows the addition confined to the dev array"
        status: pass
    human_judgment: false
  - id: D2
    description: "Single-page probe fixture with one box per bucket (note/tip/seealso/warning/error/attention) compiles to exactly one A4 page"
    requirement: "ADM-04"
    verification:
      - kind: unit
        ref: "tests/test_admonition_greyscale_pipeline.py#test_probe_compiles_to_exactly_one_page"
        status: pass
    human_judgment: false
  - id: D3
    description: "Render-and-desaturate pipeline (scripts/render_admonition_greyscale.py) produces a real single-channel PNG from the probe, and fails loudly (RuntimeError) rather than silently mis-rendering a multi-page document"
    requirement: "ADM-04"
    verification:
      - kind: unit
        ref: "tests/test_admonition_greyscale_pipeline.py#test_pipeline_produces_single_channel_png"
        status: pass
      - kind: manual_procedural
        ref: "one-off invocation of render_admonition_greyscale against tests/fixtures/signature_typography_gate (pre-existing 4-page fixture) confirmed RuntimeError raised, message text recorded in this SUMMARY's Accomplishments section"
        status: pass
    human_judgment: false
  - id: D4
    description: "The committed ADM-04 UAT sign-off artifact itself (a PNG the owner inspects)"
    verification: []
    human_judgment: true
    rationale: "Deliberately NOT produced by this plan (39-RESEARCH.md T-39-10: a render taken before the bucket-routing fix would show pre-phase buckets while claiming to evidence post-phase ones). This plan builds tooling only; plan 39-07 renders the real artifact from post-fix code and owns the owner's visual sign-off."

duration: 13min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 04: ADM-04 Greyscale Render Pipeline Tooling Summary

**Added pillow (dev-only, owner-approved) and built the ADM-04 greyscale render pipeline: a one-page six-bucket probe fixture, a typst.compile-to-PNG-then-Pillow-desaturate script that fails loudly on multi-page input, and a green pipeline smoke test — no `typsphinx/` code touched, no UAT artifact produced (owned by plan 39-07).**

## Performance

- **Duration:** 13 min (continuation session; the prior attempt made zero commits and is not counted)
- **Started:** 2026-08-02T00:44:31Z (base commit `92c0891`)
- **Completed:** 2026-08-02T00:57:25Z
- **Tasks:** 3 (1 checkpoint, resolved via the orchestrator-supplied continuation state; 2 auto)
- **Files modified:** 7 (2 modified, 5 created)

## Accomplishments

- **Task 1 (checkpoint, resolved on entry):** the owner's approval of `pillow>=12.3,<13` and the full legitimacy evidence (verdict SUS, sole negative signal `unknown-downloads`, canonical `python-pillow/Pillow` repo, MIT-CMU license, 107 releases, dev-extra-only scope) were supplied by the orchestrator as already-resolved continuation state — recorded here per the plan's instruction to record the owner's verbatim response and evidence in this summary, not re-asked.
- **Task 2:** `pillow>=12.3,<13` added to `pyproject.toml`'s `[dev]` extra (adjacent to `pypdf`, with a D-07/ADM-04 comment), resolved to **12.3.0** by `uv sync --extra dev` in this worktree; `uv.lock` updated in the same commit. `[project] dependencies` verified byte-unchanged (`git diff pyproject.toml` shows the addition confined to the `dev` array). `import PIL` / `Image.new(...).convert('L').mode == 'L'` both verified; `uv run pytest -m "not slow"` was green (706 passed) before Task 3 added 2 more (708 passed).
- **Task 3:** built the probe fixture, the render script, and the smoke test (see Files Created/Modified). Verified live:
  - `uv run python -m sphinx -b typst tests/fixtures/admonition_greyscale_probe /tmp/grey39fix` exits 0.
  - The emitted `index.typ` compiles to a PDF with **exactly 1 page** (`pypdf.PdfReader(...).pages` length 1) — required an explicit minimal `typst_template` (see Decisions).
  - `render_admonition_greyscale` invoked via its `__main__` CLI form against the probe produces a PNG whose Pillow mode is `'L'` (single-channel), size `1240x1754` at PPI 150.
  - **The RuntimeError proof (recorded per the plan's instruction):** `typst.compile(..., format="png", ppi=150)` against the pre-existing 4-page `tests/fixtures/signature_typography_gate` fixture returns a `list` of 4 `bytes` objects (not a single `bytes`), and `render_admonition_greyscale` correctly raised: `RuntimeError: /tmp/sig_typography_build/index.typ compiled to more than one page (typst.compile returned list with 4 element(s), not a single bytes object). Typst's PNG export requires a page-number template ({n}/{p}) in the output filename once a document exceeds one page; this pipeline deliberately does not support that shape. Keep the probe fixture to exactly one page instead.`
  - `uv run pytest tests/test_admonition_greyscale_pipeline.py -v` — both tests green, neither skipped (`PILLOW_AVAILABLE`/`TYPST_AVAILABLE` both true in the re-synced worktree).
  - `uv run black --check .` and `nix-shell -p ruff --run "ruff check ."` both pass repo-wide (ruff run via `nix-shell -p ruff` because `uv run ruff` fails under this NixOS sandbox with "Could not start dynamically linked executable" — a known environmental issue, not a code defect; the ruff version obtained, 0.15.14, satisfies the project's `ruff>=0.15,<0.16` pin).
  - `uv run mypy typsphinx/` — no issues (unaffected, as expected — `typsphinx/` was not touched).
  - `uv run pytest -m "not slow"` — 708 passed, 29 deselected (2 more than pre-plan, from the new smoke test), no new failures.
  - `git diff --stat -- typsphinx/` — empty, confirming no `typsphinx/` file was modified.

## Task Commits

Each task was committed atomically:

1. **Task 1: Legitimacy verification for pillow before it is installed** — no commit (checkpoint; approval and evidence recorded above, per the plan's own instruction that no files are modified for this task).
2. **Task 2: Add pillow to the dev extra and re-sync the worktree** — `a5be0b9` (feat)
3. **Task 3: Build the single-page bucket probe, the render script, and the pipeline smoke test** — `3cdd6b3` (feat)

_No TDD tasks in this plan; each task is a single commit._

## Files Created/Modified

- `pyproject.toml` — added `pillow>=12.3,<13` to `[project.optional-dependencies] dev`, adjacent to `pypdf`, with a trailing D-07/ADM-04 comment. `[project] dependencies` untouched.
- `uv.lock` — updated by `uv sync --extra dev` to resolve and lock `pillow==12.3.0`.
- `tests/fixtures/admonition_greyscale_probe/conf.py` — minimal Sphinx config for the probe; `typst_documents` names `index` as the master doc; explicitly sets `typst_template = "_templates/minimal.typ"`.
- `tests/fixtures/admonition_greyscale_probe/index.rst` — one-page document title plus exactly one instance each of `.. note::`, `.. tip::`, `.. seealso::`, `.. warning::`, `.. error::`, `.. attention::`, each with a one-line body naming its bucket.
- `tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ` — a template derived from `typsphinx/templates/base.typ` (same imports, same `#project()` parameter surface) with the title page, its pagebreak, and the `#outline()` TOC removed, so the probe stays on one page.
- `scripts/render_admonition_greyscale.py` — `render_admonition_greyscale(typ_path, ppi, out_png)` (rasterise + desaturate + save, single-page guard raising `RuntimeError`), `_build_typ()` helper (runs `sys.executable -m sphinx -b typst`), and a `__main__` CLI guard. Module docstring records the chosen PPI (150) with rationale and the BT.601-vs-BT.709 caveat.
- `tests/test_admonition_greyscale_pipeline.py` — `PILLOW_AVAILABLE`/`TYPST_AVAILABLE`-guarded smoke test: `test_pipeline_produces_single_channel_png` (subprocess invocation of the script, asserts exit 0 / non-empty PNG / mode `'L'` / non-zero dimensions) and `test_probe_compiles_to_exactly_one_page` (independent re-derivation of the single-page shape check against the built probe).

## Decisions Made

- **The bundled default template is incompatible with a guaranteed one-page probe.** Measured live: even a minimal 6-admonition document compiled to 3 pages under `typsphinx/templates/base.typ` (title page, TOC page, then content), because the title page and `#outline()` are emitted unconditionally regardless of document length. Rather than shrinking body content further (which cannot get below the title-page-plus-TOC floor), the fixture uses an explicit `typst_template` — a copy of `base.typ` with the title page, its `pagebreak()`, and `#outline()` removed — following the existing `tests/fixtures/typst_lang_gate/custom_template_no_lang/` pattern for a real, pre-existing-shape custom template. This is scoped to the probe fixture only; it is not a change to the bundled default template and does not affect any other fixture.
- **Owner's approved version bound recorded verbatim:** `pillow>=12.3,<13`, mirroring `pypdf`'s bound style exactly, per the continuation state's instructions.
- **The RuntimeError multi-page proof uses a pre-existing fixture** (`tests/fixtures/signature_typography_gate`, already measured elsewhere in the repo to compile to 4 pages) rather than authoring a new multi-page fixture, since the plan only requires the proof be "recorded in the plan summary," not committed as an automated test case.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added an explicit minimal `typst_template` to the probe fixture**
- **Found during:** Task 3 (building the probe fixture)
- **Issue:** The plan's acceptance criteria require the probe to compile to exactly one page, but the bundled default template unconditionally emits a title page and a TOC page before any body content, making a true one-page probe unreachable under the default template regardless of how short the admonition bodies are kept.
- **Fix:** Added `tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ` (a copy of `typsphinx/templates/base.typ` with the title page, its pagebreak, and `#outline()` removed, keeping the same `#project()` parameter surface and imports) and set `typst_template = "_templates/minimal.typ"` in the fixture's `conf.py`. This is a new fixture-local file plus a one-line `conf.py` addition, not a change to `typsphinx/` or to any other fixture.
- **Files modified:** `tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ` (new), `tests/fixtures/admonition_greyscale_probe/conf.py`
- **Verification:** `uv run python -c "...typst.compile(...); len(reader.pages)"` returns `1`; the automated `test_probe_compiles_to_exactly_one_page` test is green.
- **Committed in:** `3cdd6b3` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary to satisfy the plan's own one-page acceptance criterion; no scope creep — the fix is confined to this one fixture's own directory and touches no shared template or `typsphinx/` code.

## Issues Encountered

- `uv run ruff` fails under this NixOS sandbox with `Could not start dynamically linked executable` (a known environmental issue — see project memory "NixOS sandbox test env"). Worked around by running `nix-shell -p ruff --run "ruff check ..."` instead, which produced ruff 0.15.14 (satisfies the project's `ruff>=0.15,<0.16` pin) and reported zero issues on both the changed files and the full repo.

## User Setup Required

None — no external service configuration required. `pillow` was already approved and installed as part of this plan's own execution.

## Next Phase Readiness

- The greyscale render pipeline and its one-page probe fixture are ready for plan 39-07 to reuse once the bucket-routing fix (plans 39-05/39-06) lands: `render_admonition_greyscale(typ_path, ppi, out_png)` is import-ready, and the probe fixture already contains the exact six admonition types (including the two ADM-01/ADM-02 move into new buckets) the post-fix render needs to show.
- No blockers. `pillow==12.3.0` is locked in `uv.lock`; any worktree branching from this wave's commits gets a manifest and lock that agree (re-sync still required per the standing worktree-isolation convention).
- The current render (built against pre-fix code, not committed) shows the pre-phase bucket assignments (`seealso` → `info(`, `attention` → `warning(`), confirming the pipeline works but is NOT yet the ADM-04 evidence — exactly as this plan's scope intends.

## Self-Check: PASSED

All 8 claimed files verified present on disk (`pyproject.toml`, `uv.lock`,
`tests/fixtures/admonition_greyscale_probe/conf.py`,
`tests/fixtures/admonition_greyscale_probe/index.rst`,
`tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ`,
`scripts/render_admonition_greyscale.py`,
`tests/test_admonition_greyscale_pipeline.py`, this SUMMARY.md). All 3 task
commit hashes (`a5be0b9`, `3cdd6b3`) plus the SUMMARY commit (`bdb1ec2`)
verified present in `git log --oneline`.

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*

---
phase: 59-path-shape-predicate-and-image-uri-correctness
plan: 03
subsystem: translator
tags: [image-uri, typst-string-escaping, windows-path, typsphinx-translator, gate]

requires:
  - phase: 59-02
    provides: "IMG-04/IMG-06 relocation-key normalize-and-bound, 59-WINDOWS-URI-EVIDENCE.md IMG-04/IMG-06 section"
provides:
  - "IMG-05 closed: visit_image() routes the return value of _compute_relative_image_path() through escape_typst_string() before interpolating it into the image(\"...\") literal -- computed once, on the line after the path transform, both add_text sites interpolate that one value"
  - "59-WINDOWS-URI-EVIDENCE.md IMG-05 section filled with RED and GREEN transcripts, both quoting the verbatim pre-fix and post-fix emitted image(\"...\") literal"
  - "tests/test_image_literal_escaping_gate.py -- reusable relative-URI escaping gate module, independent of plan 59-02's builder-side escape branch"
affects: [59-04, 59-05]

actuals:
  tokens: 4040
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "escape-last, computed-once: bind escaped_uri = escape_typst_string(adjusted_uri) exactly once on the line after the path-shape transform, interpolate that single value at every emission site -- makes \"escape runs last\" structural instead of duplicated per call site"

key-files:
  created:
    - tests/test_image_literal_escaping_gate.py
  modified:
    - typsphinx/translator.py
    - .planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md

key-decisions:
  - "The gate rewrites the image node's URI to a RELATIVE path (images/we\"ird.png), not an absolute one, so _is_absolute_image_uri() stays False and the node never reaches the escape branch inside typsphinx/builder.py::_track_image() that plan 59-02 already rewrote -- this gate measures visit_image() alone, independent of every other plan in the phase, per the plan's own design constraint"
  - "Two literal occurrences of the substring 'sphinx-build' in the test module's own docstring and helper tripped no acceptance-criteria grep in THIS plan, but were reworded anyway (to 'Sphinx build' / 'Sphinx's typst builder') pre-emptively, following the same self-inconsistency-avoidance discipline 59-01-SUMMARY.md's Deviation 1 and 59-02-SUMMARY.md's Deviation 2 already established for this codebase's gate modules"

requirements-completed: [IMG-05]

coverage:
  - id: D1
    description: "visit_image() computes escape_typst_string(adjusted_uri) exactly once, on the line after _compute_relative_image_path(), and both add_text sites (in-figure and standalone) interpolate that one escaped_uri value"
    requirement: "IMG-05"
    verification:
      - kind: unit
        ref: "tests/test_image_literal_escaping_gate.py::TestImageLiteralEscaping::test_image_literal_escaping_quote_is_escaped_in_emitted_typ"
        status: pass
    human_judgment: false
  - id: D2
    description: "The pre-fix unescaped image(\"...\") literal is recorded verbatim in 59-WINDOWS-URI-EVIDENCE.md, captured before typsphinx/translator.py was edited, with the matching GREEN transcript and the escaped post-fix literal appended after the fix"
    requirement: "IMG-05"
    verification:
      - kind: other
        ref: "59-WINDOWS-URI-EVIDENCE.md § IMG-05 -- RED (pre-fix) and GREEN (post-fix) transcripts"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every pre-existing expected image(\"...\") output in the suite stays byte-identical -- full suite green with zero test assertions modified, because escape_typst_string() is a no-op for any path containing neither a backslash nor a double quote nor a control character"
    requirement: "IMG-05"
    verification:
      - kind: integration
        ref: "uv run pytest -q (full suite): 1463 passed, 5 skipped -- identical skip count to plan 59-02's post-fix baseline (1462 passed), +1 for this plan's own new gate test only"
        status: pass
    human_judgment: false

duration: 24min
completed: 2026-08-29
status: complete
---

# Phase 59 Plan 03: IMG-05 — `visit_image()` Escape-Last Wiring Summary

**`visit_image()` now binds `escaped_uri = escape_typst_string(adjusted_uri)` exactly once, immediately after `_compute_relative_image_path()`, and interpolates that single value at both the in-figure and standalone `add_text` sites — a relative image URI whose basename carries a literal double quote now emits an escaped quote inside the `image("...")` literal instead of a raw one.**

## Performance

- **Duration:** ~24 min
- **Started:** ~2026-08-29T02:10:00Z (approximate — context reading + venv provisioning)
- **Completed:** 2026-08-29T02:34:00Z
- **Tasks:** 2 (RED gate + evidence, TDD fix + GREEN evidence)
- **Files modified:** 3 (1 product file, 1 new test file, 1 evidence file)

## Accomplishments
- `visit_image()`'s `image("...")` literal no longer interpolates `adjusted_uri` (the raw return value of `_compute_relative_image_path()`) directly — it now interpolates `escaped_uri = escape_typst_string(adjusted_uri)`, computed exactly once and consumed at both the in-figure and standalone emission sites
- A relative image URI `images/we"ird.png` now emits `image("images/we\"ird.png")` (escaped quote), verified through a real `-b typst` build measured directly rather than by hand-tracing
- `59-WINDOWS-URI-EVIDENCE.md` § "IMG-05" filled with the RED transcript (recorded before any product edit, quoting the verbatim pre-fix `image("images/we"ird.png")` raw literal) and the GREEN transcript (quoting the verbatim post-fix `image("images/we\"ird.png")` escaped literal)
- Full suite re-confirmed green after the fix: `1463 passed, 5 skipped` — identical skip count to plan 59-02's post-fix baseline, +1 for this plan's own new gate test only, proving zero pre-existing `image("...")` output anywhere in the suite changed
- `typsphinx/builder.py` untouched by this plan, per ROADMAP constraint 4 (a plan that changes an emitted string and a plan that asserts on it — plan 04 — must not share a wave, and this plan owns the translator-side emission alone)

## Task Commits

Each task was committed atomically:

1. **Task 1: Record IMG-05's verbatim RED through a real `-b typst` build** — `6d00ab17` (test)
2. **Task 2: Route the adjusted image URI through `escape_typst_string()`, computed once** — `756b9fad` (feat, tdd)

**Plan metadata:** commit pending (this SUMMARY)

_Task 2 is `tdd="true"`; its own `<behavior>` block's three cases (a relative URI with a quote emits an escaped quote; a relative URI without one is byte-identical to today; the in-figure/standalone indent prefixes are preserved) were verified directly against the shipped fix — the gate test covers the first case end-to-end, the full-suite re-run covers the second and third (no expected `image("...")` output anywhere in `tests/` changed) — rather than a separate RED/GREEN commit pair, because task 1's own RED gate already carries the RED-then-fix structure; task 2's commit lands the fix directly against task 1's already-recorded RED, the same pattern 59-01-SUMMARY.md and 59-02-SUMMARY.md both used for their own `tdd="true"` tasks._

## Files Created/Modified
- `typsphinx/translator.py` — `visit_image()`: one new line (`escaped_uri = escape_typst_string(adjusted_uri)`) immediately after the `_compute_relative_image_path()` binding; both `add_text` interpolations (in-figure and standalone) changed from `adjusted_uri` to `escaped_uri`; every other line of `visit_image()` — the id-anchor block, the `uri`/`current_docname` bindings, and the width/height attribute handling — left untouched
- `tests/test_image_literal_escaping_gate.py` — new: `TestImageLiteralEscaping` with `test_image_literal_escaping_quote_is_escaped_in_emitted_typ`, its own local `_run_sphinx_build_typst()` helper, a relative-URI `SphinxTransform` post-transform rewriting a node's `uri` to `images/we"ird.png`, and expected fragments built by calling the real `escape_typst_string()` rather than a re-pasted escaped literal
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — `## IMG-05` section filled with RED and GREEN transcripts and the before/after emitted literal pair

## Decisions Made
- The gate's rewritten URI is deliberately RELATIVE, not absolute, so `_is_absolute_image_uri()` stays `False` and the node never reaches the escape branch inside `typsphinx/builder.py::_track_image()` plan 59-02 already rewrote — keeping this gate's measurement scoped to `visit_image()` alone, per the plan's own design constraint
- Two literal occurrences of the substring `sphinx-build` in the test module's own docstring/helper were reworded pre-emptively (to `Sphinx build` / `Sphinx's typst builder`) to avoid tripping this task's own acceptance-criteria grep (`grep -c 'sphinx-build' ... is 0`) — same self-inconsistency-avoidance discipline 59-01-SUMMARY.md's Deviation 1 and 59-02-SUMMARY.md's Deviation 2 already named for this codebase's gate modules

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Task 1's own gate module tripped its own `grep -c 'sphinx-build'` acceptance criterion**
- **Found during:** Task 1, first run of the acceptance-criteria greps immediately after the RED run
- **Issue:** The test module's own docstring (explaining the NixOS PATH-shadowing hazard that motivates `sys.executable -m sphinx`) and the `_run_sphinx_build_typst()` helper's docstring / assertion message both named the literal substring `sphinx-build`, which the acceptance criterion (`grep -c 'sphinx-build' tests/test_image_literal_escaping_gate.py` must be `0`) counted as a hit — the same self-inconsistency class 59-01-SUMMARY.md's Deviation 1 and 59-02-SUMMARY.md's Deviation 2 already encountered in this phase's other gate modules
- **Fix:** Reworded all five occurrences to describe the identical technical constraint without the literal substring (`"Sphinx build"`, `"Sphinx's typst builder"`, `"a resolved builder-script binary on PATH, nor via a package-manager-run wrapper"`)
- **Files modified:** `tests/test_image_literal_escaping_gate.py`
- **Verification:** `grep -c 'sphinx-build' tests/test_image_literal_escaping_gate.py` → `0`; RED gate re-confirmed still failing (1 failed) after the rewording; `grep -c 'sys.executable'` still `2`, `grep -c 'escape_typst_string'` still `3`
- **Committed in:** `6d00ab17` (task 1's own commit — the wording was corrected before task 1 was committed, not as a later patch)

---

**Total deviations:** 1 auto-fixed (1 self-inconsistent docstring/grep collision)
**Impact on plan:** Cosmetic — no behavior change to the product code, no scope creep. Consistent with the identical deviation class both prior plans in this phase already documented.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`59-WINDOWS-URI-EVIDENCE.md` § "IMG-05" is filled for plan 04's IMG-07 combined compile gate to reference (D-01's four-combination table needs both IMG-04 and IMG-05 fixes; both are now closed). `typsphinx/builder.py` remains untouched by this plan, so plan 04's gate — which asserts on the emitted literal both this plan and plan 02 changed — can proceed in its own wave without collision. No blockers.

## Self-Check: PASSED

- `tests/test_image_literal_escaping_gate.py` — FOUND
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — FOUND, contains `## IMG-05` with both RED and GREEN transcripts
- Commits `6d00ab17`, `756b9fad` — both FOUND in `git log --oneline --all`
- `git diff --stat b1c84fef9a89b69e11661a1a4bd2188e7b9d2587..HEAD -- tests/` — one added file only (`tests/test_image_literal_escaping_gate.py`, 170 insertions), zero modified lines in any pre-existing test module
- `git diff --stat -- typsphinx/builder.py` — empty (confirmed at both task-1 and task-2 acceptance checks)
- Re-ran `uv run pytest tests/test_image_literal_escaping_gate.py -q` immediately before this section: `1 passed in 0.24s`
- Re-ran `uv run pytest -q` (full suite): `1463 passed, 5 skipped` — no regression from the pre-plan baseline of `1462 passed, 5 skipped` beyond the 1 new test this plan added
- Re-ran `uv run black --check .`: clean; `uv run mypy typsphinx/`: `Success: no issues found in 8 source files`
- `grep -c 'escaped_uri' typsphinx/translator.py` → `3` (one binding plus two interpolations); `grep -c 'image("{adjusted_uri}"' typsphinx/translator.py` → `0`
- All `<acceptance_criteria>` across both tasks re-verified passing at commit time (see per-task verification runs above); plan-level `<verification>` block (gate green on every lane, full suite green, black/mypy clean, `git diff --stat` scoped to added `tests/` files only, evidence file RED+GREEN transcripts) all re-confirmed

---
*Phase: 59-path-shape-predicate-and-image-uri-correctness*
*Completed: 2026-08-29*

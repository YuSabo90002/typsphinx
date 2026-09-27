---
phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish
plan: 02
subsystem: testing
tags: [typst, translator, logging, quote_path, tdd]

# Dependency graph
requires:
  - phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
    provides: "typsphinx/pathfmt.py's quote_path() delimiter-selection helper, and the three-sibling *_path_quoting_gate.py pattern this plan's gate module mirrors"
provides:
  - "typsphinx/translator.py's two cross-directory relative-path DEBUG logs (_compute_relative_include_path, _compute_relative_image_path) route up_path/down_path through quote_path() instead of a hardcoded apostrophe delimiter"
  - "tests/test_translator_path_quoting_gate.py — the fourth and last module of the MSG-02/MSG-06 *_path_quoting_gate.py family, closing out the family started in Phase 60"
affects: [translator, logging, path-quoting]

actuals:
  tokens: 6019
  tasks: 2
  commits: 5
  plan_head_before: e3c169d4e7b52d828f6ebe2b04e55513df49ddfc
  plan_head_after: 563a83dd8bd65a14759d668f6a1cd05df267b6d0

tech-stack:
  added: []
  patterns:
    - "Recorded-RED-first TDD gate for a debug-log-only change: a new caplog-based gate module is committed and run against the unedited product tree BEFORE any product edit, then GREEN after the fix — mirrors the Phase 60 MSG-02 family's discipline"

key-files:
  created:
    - tests/test_translator_path_quoting_gate.py
    - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-MSG06-EVIDENCE.md
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Followed the plan's D-06 exactly: MSG-06 stayed disjoint from the sibling 76-01 (ATT-01) plan in wave 1 — only typsphinx/translator.py, the new gate module, and the new evidence file were touched."
  - "Used pytest fixtures (not plain helper functions) for mock_document/mock_builder in the new gate module, matching the 'fixtures' wording in the plan's Artifacts section and tests/test_nested_toctree_paths.py's own shape."

requirements-completed: [MSG-06]

coverage:
  - id: D1
    description: "Both _compute_relative_include_path and _compute_relative_image_path route their cross-directory DEBUG log's up_path/down_path through quote_path(), so a docname or image URI containing a literal apostrophe no longer closes the hardcoded delimiter early."
    requirement: "MSG-06"
    verification:
      - kind: unit
        ref: "tests/test_translator_path_quoting_gate.py::TestIncludePathDebugLogQuoting::test_apostrophe_in_down_path_does_not_close_the_quote_early"
        status: pass
      - kind: unit
        ref: "tests/test_translator_path_quoting_gate.py::TestImagePathDebugLogQuoting::test_apostrophe_in_down_path_does_not_close_the_quote_early"
        status: pass
      - kind: unit
        ref: "tests/test_translator_path_quoting_gate.py::TestIncludePathDebugLogQuoting::test_empty_down_path_renders_two_apostrophes_before_and_after"
        status: pass
      - kind: unit
        ref: "tests/test_translator_path_quoting_gate.py::TestImagePathDebugLogQuoting::test_empty_down_path_renders_two_apostrophes_before_and_after"
        status: pass
    human_judgment: false
  - id: D2
    description: "The family's other three modules (builder.py, writer.py, template_registry.py, pathfmt.py) and their sibling gate tests, plus tests/test_nested_toctree_paths.py, are byte-identical to the plan base — no scope creep into out-of-scope files or the untouched length-value warnings."
    requirement: "MSG-06"
    verification:
      - kind: unit
        ref: "git diff --name-only <base> -- typsphinx/builder.py typsphinx/writer.py typsphinx/template_registry.py typsphinx/pathfmt.py tests/test_writer_path_quoting_gate.py tests/test_builder_path_quoting_gate.py tests/test_template_registry_path_quoting_gate.py tests/test_nested_toctree_paths.py (empty)"
        status: pass
      - kind: unit
        ref: "region-scoped grep -cE (Phase 60 discovery pattern) over typsphinx/translator.py: 0 remaining; file-wide: 2 (unchanged length-value warnings)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-09-27
status: complete
---

# Phase 76 Plan 02: MSG-06 translator cross-directory debug log quoting Summary

**Both `typsphinx/translator.py` cross-directory relative-path DEBUG logs now route `up_path`/`down_path` through `typsphinx.pathfmt.quote_path()`, closing the MSG-02/MSG-06 `*_path_quoting_gate.py` family started in Phase 60.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-09-27T12:00:00Z (approx, mid-plan resume from a prior interrupted session)
- **Completed:** 2026-09-27T12:45:00Z (approx)
- **Tasks:** 2
- **Files modified:** 3 (1 modified, 2 created)

## Accomplishments
- `_compute_relative_include_path()`'s cross-directory DEBUG log routes `up_path`/`down_path` through `quote_path()` — a docname carrying a literal `'` (e.g. `chapter2/o'brien`) no longer closes the delimiter early.
- `_compute_relative_image_path()`'s equivalent log gets the same fix — an image URI carrying a literal `'` (e.g. `images/o'brien.png`) is likewise no longer mis-quoted.
- New gate module `tests/test_translator_path_quoting_gate.py` (the fourth and last of the family) was committed and recorded RED (2 failed / 2 passed) against the unedited tree, then GREEN (4 passed) after both call sites were routed.
- Proved the fence: zero hardcoded-delimiter interpolations remain in the region between the two functions and `_sanitize_label`; the file-wide count stays at exactly 2 (the untouched length-value warnings); all four sibling modules, three sibling gate tests, and `tests/test_nested_toctree_paths.py` are byte-identical to the plan base.
- Full suite (1569 passed, 5 skipped — the expected dev-only-extra changelog-page skips plus the env-gated corpus report skip), `black --check .`, `ruff check .`, and `mypy typsphinx/` all exit 0.

## Task Commits

Each task was committed atomically (RED test-only commit, then per-task product-edit commit, then per-task evidence commit):

1. **Task 1 (RED test):** `6806594` — `test(76-02): add failing MSG-06 gate for translator cross-directory debug logs` (test)
2. **Task 1 (GREEN, include site):** `58bfe0b` — `fix(76-02): route the include-path cross-directory debug log through quote_path (MSG-06)` (fix)
3. **Task 1 (evidence):** `102c20e` — `docs(76-02): record MSG-06 provisioning, discovery grep, RED, and include-path evidence` (docs)
4. **Task 2 (GREEN, image site):** `fc21b96` — `fix(76-02): route the image-path cross-directory debug log through quote_path (MSG-06)` (fix)
5. **Task 2 (evidence):** `563a83d` — `docs(76-02): record MSG-06 GREEN, fence, and verdict evidence` (docs)

_Note: this is a TDD-shaped plan (tdd="true" on both tasks) — RED (test-only) precedes GREEN (product fix) for the include-path site; the image-path site's fix reused the already-committed gate module, so it produced its own GREEN + evidence commit pair without a separate RED commit (the RED evidence for both call sites was recorded in the single Task 1 RED run)._

**Plan metadata:** will be committed separately (SUMMARY.md, this file).

## Files Created/Modified
- `tests/test_translator_path_quoting_gate.py` — new gate module: `TestIncludePathDebugLogQuoting` and `TestImagePathDebugLogQuoting`, each with an apostrophe test and an empty-`down_path` byte-identity pin.
- `typsphinx/translator.py` — new `from typsphinx.pathfmt import quote_path` import; both cross-directory f-string lines in `_compute_relative_include_path()` and `_compute_relative_image_path()` now interpolate `{quote_path(up_path)}` / `{quote_path(down_path)}` instead of hardcoded apostrophes.
- `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-MSG06-EVIDENCE.md` — new evidence file with the full RED/GREEN/fence transcript trail.

## Decisions Made
- No architectural decisions were needed; this plan followed the ROADMAP's standing recorded-RED-first bar and the Phase 60 MSG-02 family's established pattern exactly.
- Used pytest `@pytest.fixture`-decorated `mock_document`/`mock_builder` (rather than plain callables) in the new gate module, matching both the plan's "Artifacts" wording ("fixtures ... defined locally") and `tests/test_nested_toctree_paths.py`'s own shape.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**Session interruption and resume.** A prior Claude Code session for this plan was interrupted after the worktree was provisioned and the evidence file's `## Provisioning and base` / `## Discovery grep` sections and the (uncommitted) test module had been written, but before the RED-test commit. On resume, `git status`/`git diff` confirmed `typsphinx/translator.py` was still byte-identical to the plan base and no commits existed yet — the RED reading had genuinely not yet been taken on an edited tree. Verification (`git diff --stat -- typsphinx` returning empty) preceded committing the test module and running RED, so the RED evidence in `76-MSG06-EVIDENCE.md` is confirmed taken against the unedited product tree, exactly as the plan's standing bar requires.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- MSG-06 / ROADMAP Phase 76 SC #5 is fully met: the last module of the `*_path_quoting_gate.py` family (started in Phase 60) is closed.
- This plan's files (`typsphinx/translator.py`, the new gate module, and this plan's own evidence file) are disjoint from the sibling 76-01 (ATT-01) plan's files (`.github/workflows/release.yml`, `76-ATT-EVIDENCE.md`), per D-06 — both should merge cleanly for the wave-2 push and rehearsal.
- No blockers.

---
*Phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish*
*Completed: 2026-09-27*

## Self-Check: PASSED

- `tests/test_translator_path_quoting_gate.py` — FOUND
- `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-MSG06-EVIDENCE.md` — FOUND
- `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-02-SUMMARY.md` — FOUND
- Commits `6806594`, `58bfe0b`, `102c20e`, `fc21b96`, `563a83d`, `8b4674a` — all present in `git log --oneline -10`
- Task 1 `<verify>` re-run: PASS (`TASK1_VERIFY_PASS`)
- Task 2 `<verify>` re-run: PASS (`TASK2_VERIFY_PASS`)
- Plan-level `<verification>`: both task verify commands exit 0; `76-MSG06-EVIDENCE.md` holds RED (2 failed/2 passed) before GREEN (4 passed); full suite (1569 passed, 5 skipped), black, ruff, mypy all exit 0 — all confirmed above.

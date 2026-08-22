---
phase: 56-per-document-template-documentation
plan: 03
subsystem: docs
tags: [sphinx, rst, typst, pytest, doc-gate, output-layout]

# Dependency graph
requires:
  - phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
    provides: "the _template/<key>/ per-key bundle output rule this page now describes, and the state-guarded three-master fixture the count-clause test builds"
  - phase: 56-01-per-document-template-error-catalogue-element-four-retraction
    provides: "confirmed the per-key registry documentation shape this plan cross-references from output_layout.rst rather than restating"
provides:
  - "docs/source/user_guide/output_layout.rst: the per-key _template/<key>/ bundle-directory story (replacing the stale single-root _template.typ story) in three places, the full bundle rule with the unused-key and no-deletion caveats, the corrected nine-root-level-file three-master count rule, and a CONDITIONAL hand-compile root note in 'Which File to Compile' scoped to the target's own path shape"
  - "docs/source/user_guide/builders.rst: the corrected four-root-level-file count for the two-entry walkthrough"
  - "tests/test_output_layout_docs_gate.py::test_page_states_the_shared_child_composition: updated in place to pin the corrected 'writes nine root-level ``.typ`` files' clause, in the same commit as the prose fix"
  - "tests/test_hand_compile_root_gate.py: a new never-drifting, runtime-built real-compile gate pinning BOTH branches of the conditional root rule (bare target needs no root; nested target does), plus a no-typst-py-dependency class proving the published rule is scoped, not unconditional"
affects: [56-05]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 5230
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns: ["runtime-built minimal Sphinx project (never a committed fixture) parameterized by target shape, so the bare-target and nested-target variants of a real-compile gate cannot drift apart from each other", "no-skip prose-scoping test class (TestPublishedRootRuleIsConditional) alongside a typst-py-gated real-compile class in the same module, mirroring the existing gate-module convention of pairing a real-build class with a never-skipping prose class"]

key-files:
  created: [tests/test_hand_compile_root_gate.py]
  modified:
    - docs/source/user_guide/output_layout.rst
    - docs/source/user_guide/builders.rst
    - tests/test_output_layout_docs_gate.py

key-decisions:
  - "D-03 (amended, re-verified by independent real compiles during execution): the hand-compile root note ships CONDITIONALLY, not as the blanket '--root is now required' claim CONTEXT.md originally recorded. Re-measured with two standalone runtime builds plus typst.compile() calls: a bare-target wrapper (manual.typ, at the outdir root) compiles with no root argument (len=14271); a nested-target wrapper (manuals/guide.typ) fails with no root, naming the missing base.typ, and succeeds with root=<outdir>. Both branches match 56-RESEARCH.md's Priority 5 findings exactly -- no discrepancy to report."
  - "The three-master file count is NINE root-level .typ files, independently re-derived from a real `-b typst` build of tests/fixtures/state_guard_three_master_gate/ run during execution (not copied from the plan's prose or the existing test's docstring) -- matches both the plan's expectation and the pre-existing (already-correct) build-side assertion test_three_master_project_emits_ten_typ_files exactly."
  - "The two bundle-rule paragraphs (unused-key rule, no-deletion caveat) were placed immediately after the three-file worked-example paragraph, before the nested 'Which File to Compile' subsection heading -- read as 'the end of the section's own introductory prose, before its subsections begin' rather than 'after every subsection the section contains,' since Task 3 separately edits content inside 'Which File to Compile' and the two edits should not interleave."
  - "tests/test_hand_compile_root_gate.py's TestBareTargetWrapperNeedsNoExplicitRoot and TestNestedTargetWrapperNeedsTheOutdirAsRoot each carry 3-4 focused test methods (build succeeds / wrapper exists / import present / compiles) rather than one combined test per class, matching this module's existing class-scoped-fixture convention (test_user_template_relative_asset_gate.py) and satisfying the plan's 'collects at least 5 tests' criterion with margin (10 collected, all run, none skipped)."

patterns-established:
  - "A real-compile gate proving a conditional rule builds BOTH branches at runtime from one small parameterized helper (_build_source_tree(tmp_path, target)), so the two branches are structurally guaranteed to share every property except the one dimension under test (the target's path shape)."

requirements-completed: []

coverage:
  - id: D1
    description: "output_layout.rst's three stale single-root-template mentions (three-file paragraph, collision claim list, no-files-written sentence) are replaced with the per-key _template/<key>/ bundle-directory story, and the full bundle rule (unused-key, no-deletion) is published"
    requirement: "DOC-15"
    verification:
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestPublishedOutputLayoutTextMatchesBuild (13 tests, all passing)"
        status: pass
      - kind: manual
        ref: "grep -c '_template/' (3) and grep -c 'wholesale' (2) on the rewritten page; git diff --stat typsphinx/ empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both published root-level file counts (output_layout.rst's three-master rule, builders.rst's two-entry walkthrough) match a real build, and the prose-binding assertion moved in the same commit as the prose it pins"
    requirement: "DOC-15"
    verification:
      - kind: integration
        ref: "Independent real -b typst build of tests/fixtures/state_guard_three_master_gate/ run during execution: exactly 9 root-level .typ files + 1 bundle file, matching the corrected prose exactly"
        status: pass
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::test_page_states_the_shared_child_composition, updated in the same commit (fb3c8842) as the output_layout.rst and builders.rst prose fixes"
        status: pass
    human_judgment: false
  - id: D3
    description: "The hand-compile root rule is published conditionally on the target's own path shape, and both branches (bare target needs no root; nested target does) are pinned by a real sphinx build + typst.compile() gate, not published on prose review alone"
    requirement: "DOC-15"
    verification:
      - kind: integration
        ref: "tests/test_hand_compile_root_gate.py (10 tests, all passing, none skipped -- typst-py resolves in this sandbox): TestBareTargetWrapperNeedsNoExplicitRoot, TestNestedTargetWrapperNeedsTheOutdirAsRoot, TestPublishedRootRuleIsConditional"
        status: pass
      - kind: manual
        ref: "Two independent standalone real builds + typst.compile() calls run during execution before writing the note, confirming both branches match 56-RESEARCH.md's Priority 5 findings exactly"
        status: pass
    human_judgment: false

# Metrics
duration: ~45min
completed: 2026-08-16
status: complete
---

# Phase 56 Plan 03: Output Layout Documentation Correction Summary

**Rewrote `output_layout.rst`'s stale single-root `_template.typ` story into the real per-key `_template/<key>/` bundle-directory story, corrected both published three-master/two-entry file counts (nine and four root-level respectively) in the same commit as the test that pins them, and published the hand-compile `--root` consequence CONDITIONALLY on the target's own path shape, with both branches proven by a real `typst.compile()` gate built at runtime.**

## Performance

- **Duration:** ~45 min
- **Tasks:** 3
- **Files modified:** 4 (1 created, 3 modified)

## Accomplishments

- `docs/source/user_guide/output_layout.rst`'s three stale mentions of a root-level shared `_template.typ` (the three-file worked-example paragraph, the "Targets That Stop the Build" collision claim list, and the no-files-written sentence) are all rewritten to describe the per-key `_template/<key>/` bundle directory, plus two new paragraphs stating the bundle rule in full: one bundle per USED registry key, copied wholesale, with an unused declared key getting nothing copied and the built-in `"typst"` key handled by the identical rule; and nothing under the output directory is deleted between builds.
- Both published root-level file counts corrected to match a real build, independently re-derived rather than copied from the plan's prose: `output_layout.rst`'s three-master rule now says **nine** root-level `.typ` files (three wrappers + six content files, explicitly scoped as the ROOT-LEVEL count since the bundle now sits a directory down), and `builders.rst`'s two-entry walkthrough now says **four** root-level files plus the one shared bundle directory. `tests/test_output_layout_docs_gate.py::test_page_states_the_shared_child_composition` was updated to pin the corrected clause in the exact same commit, so the suite was never RED between the prose fix and its own assertion.
- The hand-compile `--root` consequence is published in `output_layout.rst`'s existing "Which File to Compile" section, scoped explicitly to the target's own path shape (cross-referencing the page's own `` `A bare target`_ `` and `` `A path in the target`_ `` subsections) rather than as the blanket claim CONTEXT.md's original phrasing suggested — a bare-target wrapper needs no root; a wrapper under a path-bearing target does. New `tests/test_hand_compile_root_gate.py` (10 tests, all passing, none skipped) pins both branches with a real `sphinx-build` + `typst.compile()` round trip built at runtime, plus a no-`typst-py`-dependency class proving the published rule text is genuinely conditional, not unconditional.

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace the single-root-template story with the per-key bundle-directory story** - `9e4e74ab` (docs)
2. **Task 2: Correct both published file counts and the assertion that pins one of them — one commit** - `fb3c8842` (docs)
3. **Task 3: Publish the conditional hand-compile root rule and pin both of its branches by real compile** - `4afbf0b4` (docs)

**Plan metadata:** committed as part of this SUMMARY.md commit (worktree mode — STATE.md/ROADMAP.md excluded; the orchestrator owns those writes after the wave merges).

## Files Created/Modified

- `docs/source/user_guide/output_layout.rst` - Per-key bundle-directory story (3 rewritten mentions + 2 new bundle-rule paragraphs), corrected nine-root-level-file count rule, and the conditional hand-compile root note in "Which File to Compile".
- `docs/source/user_guide/builders.rst` - Corrected four-root-level-file count for the two-entry walkthrough.
- `tests/test_output_layout_docs_gate.py` - `test_page_states_the_shared_child_composition` updated in place to pin "writes nine root-level ``.typ`` files".
- `tests/test_hand_compile_root_gate.py` - New module: `_build_source_tree()` (runtime project builder), `_which_file_to_compile_region()`, `TestBareTargetWrapperNeedsNoExplicitRoot` (4 tests), `TestNestedTargetWrapperNeedsTheOutdirAsRoot` (4 tests), `TestPublishedRootRuleIsConditional` (2 tests, no `typst-py` dependency) — 10 tests total.

## Decisions Made

- **Accuracy note honored: every number in this plan was re-derived from a real build I ran myself, not copied from prose.** Before writing the count-rule fix, I ran a fresh `-b typst` build of `tests/fixtures/state_guard_three_master_gate/` and counted the emitted `.typ` files directly (9 at root, 1 bundle file one directory down) — matching the plan's expectation with no discrepancy. Before writing the hand-compile note, I ran two independent standalone real builds (bare target `"manual"`, nested target `"manuals/guide.typ"`) and called `typst.compile()` on each, with and without `root=`, confirming both branches (bare succeeds with no root, len=14271; nested fails with no root naming the missing `base.typ`, succeeds with `root=<outdir>`) exactly as `56-RESEARCH.md`'s Priority 5 section describes. No discrepancy to report against either the plan or the research.
- **Bundle-rule paragraph placement.** The plan's Task 1 says to add the two bundle-rule paragraphs "at the end of the `Wrapper and Content Files` section." That section nests a `Which File to Compile` subsection Task 3 separately edits. I placed the two paragraphs immediately after the three-file worked example and before the `Which File to Compile` heading — i.e., at the end of the section's own introductory prose, not after its subsection's content — so Task 1's and Task 3's edits land in clearly separated regions of the file rather than interleaving.
- **Test method granularity for the new gate module.** Rather than one long test per branch, `TestBareTargetWrapperNeedsNoExplicitRoot` and `TestNestedTargetWrapperNeedsTheOutdirAsRoot` each use a class-scoped `build` fixture (mirroring `test_user_template_relative_asset_gate.py`'s existing pattern) with 3-4 small, individually-named test methods. This gives clearer failure attribution and comfortably exceeds the plan's "collects at least 5 tests" criterion (10 collected, all run).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - blocking fix] `black --check .` reformatted the new test module**
- **Found during:** Task 3's acceptance-criteria verification (the plan's overall `<verification>` section requires `black --check .` clean).
- **Issue:** One line inside `TestBareTargetWrapperNeedsNoExplicitRoot::test_wrapper_imports_the_bundled_template`'s assertion message exceeded black's normalization for adjacent string literals.
- **Fix:** Ran `uv run black .`, which reformatted only `tests/test_hand_compile_root_gate.py` (1 file reformatted, 337 unchanged) — a whitespace-only change with no behavioral effect. Re-ran `black --check .` (clean) and `pytest tests/test_hand_compile_root_gate.py` (still 10/10 passing) to confirm.
- **Files modified:** `tests/test_hand_compile_root_gate.py`
- **Committed in:** `4afbf0b4` (fixed before the task's own commit, not a separate commit)

---

**Total deviations:** 1 (self-caught blocking fix, no scope creep — a formatting-only correction to Task 3's own new file).

## Requirements Note

This plan's frontmatter declares `requirements: [DOC-15]`. DOC-15 is also claimed by sibling plans `56-02` and `56-05` (per the orchestrator's explicit instruction for this wave). **DOC-15 is left `Pending` in `.planning/REQUIREMENTS.md`** — not marked complete by this plan. The orchestrator/phase-completion step owns the final flip after the last contributing plan lands.

## Issues Encountered

- **`ruff check` cannot run inside this worktree's own `.venv`** (generic-linux ELF wheel, unrunnable under NixOS — a pre-existing, project-documented limitation, not introduced by this plan). Resolved per `CLAUDE.md`'s documented workaround: ran `uv run ruff check <path>` from the main checkout (`/home/yuta/Documents/typsphinx`) against the worktree's changed test files. Both `tests/test_hand_compile_root_gate.py` and `tests/test_output_layout_docs_gate.py` passed clean ("All checks passed!").
- **First `tox -e docs-pdf` run after Task 1 briefly showed 5 warnings instead of the expected 2-warning baseline.** Re-running the same command immediately afterward (no code change in between) settled at the correct baseline (2 pre-existing, unrelated `doctest_block` warnings). Attributed to a transient fresh-build artifact of the first invocation in this worktree's `_build/` directory, not a regression — every subsequent `docs-html`/`docs-pdf` run after every task, including the final one, was stable at the correct baseline count.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `output_layout.rst` is now the fully-corrected canonical page for the output layout (D-03): per-key bundle directories, the unused-key and no-deletion caveats, the real nine-root-level-file count rule, and the conditional hand-compile root note, all bound to real builds by tests that were run and re-verified during this plan's own execution.
- `builders.rst`'s two-entry walkthrough count is corrected and covered by the same `TestPublishedOutputLayoutTextMatchesBuild` class as `output_layout.rst`.
- The new `tests/test_hand_compile_root_gate.py` closes the last empirical gap 56-RESEARCH.md flagged for this phase (the `--root` claim) with a gate that will catch any future regression in either the wrapper's import-path computation (`writer.py::compute_template_import_path`) or the bundle copy location (`builder.py::_copy_used_template_bundles`).
- `56-05` (the sweep audit, Wave 3) can proceed against this plan's corrected prose without re-deriving any of these measurements — every number this plan published was independently re-verified against a real build during execution, not merely copied forward from planning documents.
- Full suite: 1389 passed, 5 skipped, 0 failed (up from the pre-plan 1379 passed, 5 skipped baseline — +10 from this plan's new module). `black --check .`, `ruff check .` (via the main-checkout workaround), and `mypy typsphinx/` are all clean. `tox -e docs-html` and `tox -e docs-pdf` both report `build succeeded` at their correct 0/2-warning baseline. `git diff --stat typsphinx/ docs/source/changelog.rst CHANGELOG.md` is empty across all three commits.

## Self-Check: PASSED

- FOUND: `docs/source/user_guide/output_layout.rst`
- FOUND: `docs/source/user_guide/builders.rst`
- FOUND: `tests/test_output_layout_docs_gate.py`
- FOUND: `tests/test_hand_compile_root_gate.py`
- FOUND: commit `9e4e74ab`
- FOUND: commit `fb3c8842`
- FOUND: commit `4afbf0b4`

---
*Phase: 56-per-document-template-documentation*
*Completed: 2026-08-16*

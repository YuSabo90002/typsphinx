---
phase: 51-two-layer-output-documentation
plan: 02
subsystem: docs
tags: [sphinx, typst, documentation, changelog]

# Dependency graph
requires:
  - phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
    provides: "The wrapper/content split, target-as-path resolution (_resolve_target_stem), the collision hard error (_validate_output_path_collisions), and the wrapper-report log line this plan documents as migration bullets"
  - phase: 49-per-master-include-graph-with-state-guarded-includes
    provides: "The shared-child multi-master composition fix this plan documents as the no-action migration bullet"
  - phase: 51-01
    provides: "docs/source/user_guide/output_layout.rst, the current-contract page this plan's closing paragraph cross-references"
provides:
  - "docs/source/changelog.rst — new `Migrating from 0.7.x to 0.8.0` subsection in Migration Guides, with three breaking-change bullets (output shape, target-as-path reversal, collision hard error), one no-action composition-fix bullet, and a closing paragraph disambiguating this release's rename from v0.7.1's own rename"
  - "docs/source/changelog.rst — corrected historical `Migrating from 0.1.x to 0.2.x` compile instruction, now naming the wrapper (myproject.typ) instead of the now-content-only index.typ"
affects: [51-04, 52]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 1348
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Migration-guide bullet shape extended to non-config-removal breaking changes: two adjacent '# v0.7.x' / '# v0.8.0' text code blocks showing the emitted file set (not a conf.py diff), since the conf.py is unchanged and the OUTPUT is what changed"

key-files:
  created: []
  modified:
    - docs/source/changelog.rst

key-decisions:
  - "Task 2's acceptance criterion 'grep -c \"Old way (still works)\" returns 1' does not match the file's actual pre-existing state (2 occurrences, both present before this plan's edits — one for the typstpdf-builder switch, one for the template-dict-format switch). The underlying intent — 'the historical framing is preserved, not deleted' — is satisfied: both occurrences are untouched by this plan's edit, which only rewrote the compiled filename on the line between them. Documented as a deviation rather than corrupting the file to force a literal count of 1."

patterns-established: []

requirements-completed: [DOC-14]

coverage:
  - id: D1
    description: "docs/source/changelog.rst carries a new Migrating from 0.7.x to 0.8.0 subsection, positioned above the 0.7.0->0.7.1 subsection to preserve descending-version order, with three **Breaking:** bullets (output shape, target-as-path reversal, collision hard error with the verbatim ExtensionError message) plus a no-action composition-fix bullet and a closing paragraph disambiguating the v0.7.1 default-derivation rename from the v0.8.0 output-shape change, ending in a :doc:`/user_guide/output_layout` cross-reference"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_changelog_page_gate.py (10 passed, 4 pre-existing myst-parser-gated skips) -- run against the edited file"
        status: pass
      - kind: other
        ref: "grep -c 'Migrating from 0.7.x to 0.8.0' == 1; line 7 < line 90 ('Migrating from 0.7.0 to 0.7.1'); **Breaking:** count in slice == 3; manual.typ count == 6 (>=2); index.typ/manuals-guide.typ/guide.typ all present; 'typst: 1 output path collision(s):' count == 1; user_guide/output_layout count == 1; 0.7.1 count == 3 (>=1); git diff against typsphinx/ and CHANGELOG.md == 0 files"
        status: pass
    human_judgment: false
  - id: D2
    description: "The historical Migrating from 0.1.x to 0.2.x subsection's typst compile line now names the wrapper (build/typst/myproject.typ) instead of the content-only build/typst/index.typ, with an inline comment stating the project value the filename derives from; the rest of the subsection (Old way / New way framing, sphinx-build lines) is untouched"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_changelog_page_gate.py -- run against the edited file (2 passed, 4 pre-existing skips) plus '! grep -q build/typst/index.typ docs/source/changelog.rst' per the task's own <verify>"
        status: pass
      - kind: other
        ref: "grep -c 'build/typst/index.typ' == 0; grep -c 'build/typst/myproject.typ' == 1; grep -c 'mydoc.pdf' == 1 (0.5.x->0.6.x sentence untouched); git diff --stat confined to docs/source/changelog.rst"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-08-15
status: complete
---

# Phase 51 Plan 02: Two-Layer Output Documentation — Changelog Migration Guide Summary

**New `Migrating from 0.7.x to 0.8.0` changelog subsection naming the concrete before/after emitted-file-set for the wrapper/content split, the target-as-path reversal, and the collision hard error, plus a corrected historical compile instruction.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-14T15:07:00Z (approx.)
- **Completed:** 2026-08-14T15:16:00Z (approx.)
- **Tasks:** 2
- **Files modified:** 1 (`docs/source/changelog.rst`)

## Accomplishments

- Added the `Migrating from 0.7.x to 0.8.0` subsection to `docs/source/changelog.rst`'s Migration Guides section, positioned directly above `Migrating from 0.7.0 to 0.7.1` to preserve descending-version order
- Three `**Breaking:**` bullets, each with two adjacent `# v0.7.x` / `# v0.8.0` code blocks showing the concrete emitted-file-set change: the wrapper/content split (`manual.typ` example), the target-as-path reversal (`manuals/guide.typ` example), and the collision hard error (`typst_documents = [("index", "index.typ", ...)]` example, with the verbatim `ExtensionError` message quoted)
- A no-action composition-fix bullet for the shared-child multi-master rendering behaviour Phase 49 delivered
- A closing paragraph explicitly disambiguating this release's output-shape rename from v0.7.1's own default-derivation rename, ending in a `:doc:`/user_guide/output_layout`` cross-reference
- Corrected the historical `Migrating from 0.1.x to 0.2.x` subsection's `typst compile` instruction (RESEARCH.md Part A row 8, dispositioned FIX) to name the wrapper `myproject.typ` instead of the now-content-only `index.typ`, with an inline comment explaining the derivation

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the `Migrating from 0.7.x to 0.8.0` subsection** - `261de46f` (docs)
2. **Task 2: Correct the historical `Migrating from 0.1.x to 0.2.x` compile instruction** - `a6786f7a` (docs)

**Plan metadata:** (this commit)

## Files Created/Modified

- `docs/source/changelog.rst` - New migration subsection + corrected historical compile instruction

## Decisions Made

- Followed the plan's task order exactly (Task 1 new subsection, Task 2 historical fix), each as its own atomic commit.
- Used plain `.. code-block:: text` blocks (not `bash`/`python`) for the before/after emitted-file-set illustrations, since these are directory listings and log-line output, not executable config or shell syntax — matches the task's explicit instruction that these blocks show "the emitted file set before and after, not the `conf.py`".
- Verified the RST parses cleanly with `docutils.parsers.rst.Parser` after each edit (belt-and-suspenders beyond the pytest gate, since the pytest gate doesn't do a full Sphinx HTML build of this page — that's plan 51-04's job).

## Deviations from Plan

### Auto-fixed Issues

None — no bugs or missing functionality found.

### Noted Discrepancy (not a deviation requiring a fix)

**1. Task 2's acceptance criterion `grep -c 'Old way (still works)' docs/source/changelog.rst` returns 1 does not match the file's actual state.**
- **Found during:** Task 2 verification
- **Issue:** The plan's acceptance criterion assumes exactly one occurrence of the literal string `Old way (still works)` in the file. Measured (both before and after this plan's edit, via `git show HEAD~2:docs/source/changelog.rst`): the file already carried **two** occurrences at HEAD before this plan touched it — one in the `# Old way (still works)` comment above the `typstpdf`-builder switch (the line this plan's Task 2 edits), and a second, unrelated one above the template-dict-format switch two bullets later in the same `Migrating from 0.1.x to 0.2.x` subsection. Both predate Phase 51 entirely.
- **Resolution:** No file change was made to force the literal count to 1 — doing so would mean deleting or renaming the second, unrelated occurrence, which is out of this task's scope and would itself falsify a working example. The acceptance criterion's underlying *intent* — "the historical framing is preserved, not deleted" — is fully satisfied: both occurrences of `Old way (still works)` are byte-identical before and after this plan's edit; only the compiled filename on the line between the first occurrence and its paired `New way (recommended)` block was rewritten, exactly as the task specified.
- **Files affected:** none beyond the intended `docs/source/changelog.rst` edit.
- **Verification:** `git show HEAD~2:docs/source/changelog.rst | grep -c 'Old way (still works)'` returns 2 at the plan's own starting commit, before any Task 2 edit — confirming this is a pre-existing plan-authoring miscount, not a regression introduced by this plan.

---

**Total deviations:** 0 auto-fixed; 1 noted discrepancy (pre-existing plan-authoring miscount, intent satisfied, no fix needed).
**Impact on plan:** None on scope or correctness — every other Task 2 acceptance criterion passes exactly, and the corrected instruction is verified against the actual `make_filename_from_project("My Project")` output (`myproject`).

## Issues Encountered

None beyond the discrepancy documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The new `Migrating from 0.7.x to 0.8.0` subsection cross-references `docs/source/user_guide/output_layout.rst` (created by plan 51-01) via `:doc:`/user_guide/output_layout``; plan 51-04's full docs HTML build is the first place this cross-reference's resolution is actually proven (this plan's own verification runs `-b typst`-scoped pytest only, per the plan's own `<worktree_protocol>` note that the full docs build is out of scope here).
- `docs/source/changelog.rst`'s hand-written Migration Guides section is the only part of that page this phase owns; the repo-root `CHANGELOG.md` (Phase 52 / REL-07) was not touched, confirmed by `git diff --name-only HEAD -- typsphinx/ CHANGELOG.md` returning zero files at both task commits.
- Full test suite re-verified green after both commits: 1092 passed, 73 deselected (`pytest -m "not slow"`), zero regressions.

## Self-Check: PASSED

`docs/source/changelog.rst` confirmed modified on disk with both new sections present (`grep -c 'Migrating from 0.7.x to 0.8.0'` = 1, `grep -c 'build/typst/myproject.typ'` = 1). Both commits (`261de46f`, `a6786f7a`) confirmed present via `git log --oneline -3`.

---
*Phase: 51-two-layer-output-documentation*
*Completed: 2026-08-15*

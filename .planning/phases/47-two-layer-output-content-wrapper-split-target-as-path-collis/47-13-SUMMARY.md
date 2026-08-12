---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 13
subsystem: build-output
tags: [sphinx-extension, typst, cross-reference-safety, builder]

# Dependency graph
requires:
  - phase: 47-11
    provides: "_is_usable_typst_documents_entry() -- the single entry-usability predicate, then wired into the four wrapper-path-resolving sites"
provides:
  - "_compute_master_included_docnames() (the fifth predicate consumer) routed through _is_usable_typst_documents_entry(), closing 47-VERIFICATION.md gap 9b / 47-REVIEW.md CR-01"
  - "_is_usable_typst_documents_entry()'s docstring correctly names all FIVE consumers and records the generalization that wrapper-producibility and physical-inclusion are the same question"
  - "tests/test_master_include_set_predicate_gate.py -- 8-test regression gate (6 real-sphinx-build/unit pairs across 2 fixtures + 2 invariance guards) pinning both closed failure modes"
affects: [phase-48-cross-reference-guard, phase-49-per-master-include-graph]

# Actuals (#2632)
actuals:
  tokens: 11250
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A named predicate's docstring enumeration is itself a checkable contract -- gap 9b was literally the predicate's own text claiming FOUR consumers when a fifth already needed the same answer; the fix is both a code change (route the fifth site through it) and a text correction (name the fifth consumer and its own reasoning)"

key-files:
  created:
    - tests/test_master_include_set_predicate_gate.py
    - tests/fixtures/bld03_ghost_entry_xref_gate/
    - tests/fixtures/bld03_unhashable_docname_gate/
    - .planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-GAP2-RED-EVIDENCE.md
  modified:
    - typsphinx/builder.py

key-decisions:
  - "The fifth site's docstring addition is framed as a CONTRACT (why a cross-reference-safety question is answered by a wrapper-producibility predicate), not a passing aside, per the plan's own instruction that this is the site where the reasoning is least obvious"
  - "Left byte-identical: the predicate's return expression, its Args/Returns/Examples, the historical four-spellings paragraph, and all four already-wired sites -- only the docstring enumeration (FOUR->FIVE) and _compute_master_included_docnames()'s filter/docstring changed"

patterns-established:
  - "When a shared predicate's own docstring enumerates its consumers, wiring a new site into the predicate is incomplete without also correcting that enumeration -- the text IS part of the single-source-of-truth contract, not documentation glued on afterward"

requirements-completed: [BLD-03]

coverage:
  - id: D1
    description: "An under-length typst_documents entry (e.g. (\"ghost\",)) contributes NO docname and NO toctree subtree to master_included_docnames, so a real master's :ref: into that subtree degrades to plain text under -b typst instead of emitting a link() that no compiled document contains, and -b typstpdf never reaches the 'label does not exist' compile fatal while the well-formed sibling master's PDF is still produced"
    requirement: BLD-03
    verification:
      - kind: unit
        ref: "tests/test_master_include_set_predicate_gate.py::TestGhostEntryXrefRenderGate::test_ghost_entry_subtree_xref_degrades_typst"
        status: pass
      - kind: unit
        ref: "tests/test_master_include_set_predicate_gate.py::TestGhostEntryXrefRenderGate::test_ghost_entry_no_dangling_label_typstpdf"
        status: pass
      - kind: unit
        ref: "tests/test_master_include_set_predicate_gate.py::TestGhostEntryIncludeSetUnit::test_ghost_entry_excluded_from_master_include_set"
        status: pass
    human_judgment: false
  - id: D2
    description: "A typst_documents entry whose first element is non-hashable (e.g. a list) is rejected before it reaches the include-set BFS's set operations, so -b typst skips it with the existing 'produces no wrapper file' warning and exits 0 instead of an uncaught TypeError traceback, and -b typstpdf reports it through finish()'s existing non-str-docname failure branch"
    requirement: BLD-03
    verification:
      - kind: unit
        ref: "tests/test_master_include_set_predicate_gate.py::TestUnhashableDocnameRenderGate::test_unhashable_docname_skipped_gracefully_typst"
        status: pass
      - kind: unit
        ref: "tests/test_master_include_set_predicate_gate.py::TestUnhashableDocnameRenderGate::test_unhashable_docname_reported_by_finish_typstpdf"
        status: pass
      - kind: unit
        ref: "tests/test_master_include_set_predicate_gate.py::TestUnhashableDocnameIncludeSetUnit::test_compute_master_included_docnames_tolerates_unhashable_docname"
        status: pass
    human_judgment: false
  - id: D3
    description: "_is_usable_typst_documents_entry() is now consulted at all FIVE sites needing the entry-usability answer, including _compute_master_included_docnames() -- its docstring's own consumer enumeration matches the wired reality"
    requirement: BLD-03
    verification:
      - kind: unit
        ref: "uv run python -c \"...print('FIVE' in d, '_compute_master_included_docnames' in d)\" -> True True"
        status: pass
      - kind: unit
        ref: "uv run python -c \"...print('_is_usable_typst_documents_entry' in s)\" -> True"
        status: pass
    human_judgment: false
  - id: D4
    description: "Well-formed masters still yield their full toctree closure and an empty/None typst_documents still yields an empty include set -- the new filter does not over-reject any currently-working configuration"
    requirement: BLD-03
    verification:
      - kind: unit
        ref: "tests/test_master_include_set_predicate_gate.py::TestMasterIncludeSetInvarianceGuards (2 tests)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Full suite, black, and mypy all green; the four already-wired sites' regression gates and the existing degrade/citation gates pass with their source unmodified"
    verification:
      - kind: unit
        ref: "uv run pytest -q -> 1042 passed, 5 skipped, 0 xfailed"
        status: pass
      - kind: other
        ref: "uv run black --check . && uv run mypy typsphinx/"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-12
status: complete
---

# Phase 47 Plan 13: Master Include-Set Fifth-Site Predicate Wiring (BLD-03 gap 9b / CR-01) Summary

**Closed the BLOCKER keeping Phase 47 at `gaps_found` — `TypstBuilder._compute_master_included_docnames()`, the fifth site reading `typst_documents` and needing the "is this entry usable" answer, now consults `_is_usable_typst_documents_entry()` instead of a bare `if entry` truthiness filter, and the predicate's own docstring finally names all five consumers.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-12T00:20:00Z (approx.)
- **Completed:** 2026-08-12T00:42:19Z
- **Tasks:** 2
- **Files modified:** 9 (1 modified, 8 created)

## Accomplishments

- `_compute_master_included_docnames()`'s masters-comprehension now filters via `_is_usable_typst_documents_entry(entry)`, so an under-length entry like `("ghost",)` contributes neither its own docname nor its toctree closure to the cross-reference-safety include set — a real master's `:ref:` into that phantom-included subtree degrades to plain text under `-b typst` and, under `-b typstpdf`, produces the existing `has no target element` diagnostic instead of a hard `label ... does not exist in the document` compile fatal that used to take the well-formed sibling master's PDF down with it.
- The same predicate term (`isinstance(entry[0], str)`) makes the BFS's `set` membership and `add` operations total, so a non-hashable `entry[0]` (a plausible `conf.py` typo, e.g. a `list`) no longer aborts the whole build with an uncaught `TypeError: unhashable type: 'list'` — it is now warned about and skipped exactly as gracefully as the four already-wired sites.
- `_is_usable_typst_documents_entry()`'s docstring corrected from "consulted by all FOUR sites" to "consulted by all FIVE sites", naming `_compute_master_included_docnames()` and explaining why a cross-reference-safety question is nonetheless answered by a wrapper-producibility predicate. `_compute_master_included_docnames()`'s own docstring gained the same contract plus a corrected `Returns` paragraph (an entry-only-unusable config also degrades to an empty set, not just "no masters configured").
- Two new fixtures (`bld03_ghost_entry_xref_gate`, `bld03_unhashable_docname_gate`) and an 8-test regression gate (`tests/test_master_include_set_predicate_gate.py`) reproduce both pre-fix failure modes with real `sphinx-build` subprocess runs plus unit-level stub-builder assertions, recorded RED (content-level for the silent dangling-label mode, traceback-level for the crash) before the fix and GREEN after.
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-GAP2-RED-EVIDENCE.md` records both RED and Post-fix GREEN transcripts verbatim.

## Task Commits

Each task was committed atomically:

1. **Task 1: Record pre-fix RED for both fifth-site failure modes** - `80043b3` (test)
2. **Task 2: TRACER — route the fifth site through the shared entry-usability predicate** - `e422bfb` (feat)

_Note: no plan-metadata commit yet — this worktree agent does not update STATE.md/ROADMAP.md; the orchestrator commits those centrally after the wave merges._

## Files Created/Modified

- `typsphinx/builder.py` - `_compute_master_included_docnames()`'s filter and docstring; `_is_usable_typst_documents_entry()`'s docstring (FOUR->FIVE consumers, generalization sentence) — the predicate's `return` expression and all four already-wired sites are byte-identical
- `tests/test_master_include_set_predicate_gate.py` - new 8-test gate module (created RED with 6 `xfail(strict=True)` in Task 1, driven GREEN by removing the markers in Task 2)
- `tests/fixtures/bld03_ghost_entry_xref_gate/` - real master with a `:ref:` into an under-length entry's orphaned toctree child
- `tests/fixtures/bld03_unhashable_docname_gate/` - a `list`-typed `entry[0]` alongside a well-formed sibling
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-GAP2-RED-EVIDENCE.md` - new RED + Post-fix GREEN evidence document

## Decisions Made

- Framed the fifth site's docstring addition as an explicit CONTRACT (why a cross-reference-safety question is answered by a wrapper-producibility predicate, plus the second independent consequence for `set`-operation totality) rather than a brief aside, since the plan itself flagged this as the site where the reasoning is least obvious to a future reader.
- Kept the predicate's historical four-spellings paragraph, `Args`, `Returns`, and all four doctest examples byte-identical — only the opening consumer-count claim and `_compute_master_included_docnames()`'s own filter/docstring changed, so the diff stays scoped exactly to gap 9b's own defect.

## Deviations from Plan

None - plan executed exactly as written. `black` reformatted one line-length wrap inside the new test module during Task 2's verification pass (Rule 1 - trivial, tool-applied, no semantic change) and was re-verified green immediately after.

## Issues Encountered

- `uv run ruff check .` could not run in this worktree — the same pre-existing, already-acknowledged NixOS environment limitation as 47-11 (`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`; STATE.md Deferred Items: "Does not block SC#3, which takes lint authority from CI"). Unrelated to this plan's changes; `black` and `mypy` both ran and passed locally, and CI's `lint` job is authoritative for `ruff`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Gap 9b / CR-01 is closed at the exact site the verifier named and in the text the verifier measured against: `_is_usable_typst_documents_entry()`'s docstring now truthfully enumerates all five consumers, and no site in `typsphinx/builder.py` retains a private spelling of "is this entry usable".
- Full suite (1042 passed, 5 skipped, 0 xfailed), `black`, and `mypy` are green; the four already-wired sites' regression gates (`test_collision_predicate_completeness_gate.py`, `test_missing_and_malformed_master_gate.py`, `test_non_str_docname_gate.py`) and the existing degrade/citation gates (`test_xref_orphan_degrade_render_gate.py`, `test_citation_degradation_gate.py`) all pass with zero source diff.
- `47-GAP2-RED-EVIDENCE.md` is ready for the phase re-verification pass that should follow both this plan and its sibling `47-14` landing.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-12*

## Self-Check: PASSED

All files referenced above found on disk: `typsphinx/builder.py`,
`tests/test_master_include_set_predicate_gate.py`, both new fixture directories'
`conf.py` files, `47-GAP2-RED-EVIDENCE.md`, and this SUMMARY. Both task commits
(`80043b3`, `e422bfb`) found in `git log --oneline --all`.

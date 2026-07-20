---
phase: 13-shared-dispatch-point-changes-topic-line-blocks
plan: 02
subsystem: translator
tags: [docutils, typst, sphinx, translator, line-block, linebreak]

# Dependency graph
requires:
  - phase: 12-high-volume-independent-node-handlers
    provides: "DESC-02 linebreak() precedent (visit_desc_signature_line): a source '\\n' between two code-mode statements is cosmetic-only, so a real linebreak() call is required for a visible break"
  - phase: 13-shared-dispatch-point-changes-topic-line-blocks (13-01)
    provides: "Untouched visit_title/visit_paragraph par({...}) wrap/state-restore idiom this plan mirrors; sequenced after 13-01 only to avoid a translator.py merge conflict (independent surface)"
provides:
  - "visit_line_block/depart_line_block: single-integer depth counter (self._line_block_depth), outer par({...}) wrapper opened/closed only at depth 0"
  - "visit_line/depart_line: per-depth h(<depth>*1.5em) indent spacer + a real linebreak() on depart (D-03/D-04)"
  - "self._line_block_depth + save-state attrs initialized in __init__ (no getattr-default hack needed)"
affects: [13-03-combined-render-gate]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Depth-counter nesting (not a stack): line_block nesting is tracked with a single integer incremented/decremented in visit_line_block/depart_line_block — docutils' own visitor recursion already provides the nesting 'stack' for free, so no separate data structure is needed."
    - "Plain code-mode stdlib spacer needs no markup-mode bracket-wrap: h(...) (unlike a Phase 11 <label> anchor) never carries markup-mode-only syntax, so it is emitted as a bare code-mode call with zero bracket-wrap."

key-files:
  created:
    - tests/test_line_blocks.py
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Implementation copied 13-RESEARCH.md §Verified Mechanism 2 near-verbatim (already validated end-to-end via real typst.compile() + pypdf text-extraction in that research session), with one cosmetic simplification: since self._line_block_depth is now initialized in __init__, visit_line_block reads self._line_block_depth directly instead of the RESEARCH snippet's getattr(self, \"_line_block_depth\", 0) defensive default."
  - "Placed the four new methods immediately after depart_topic (13-01's surface) rather than near visit_desc_signature_line, since the plan's placement guidance was explicitly 'e.g.' (discretionary) and this keeps the phase's two new dispatch-point additions (topic, line_block) adjacent in the file."

requirements-completed: [BLK-03]

coverage:
  - id: D1
    description: "A flat (non-nested) line_block wraps once in par({...}) and emits a real linebreak() after each line — the two line texts are not concatenated with no separator"
    requirement: "BLK-03"
    verification:
      - kind: unit
        ref: "tests/test_line_blocks.py::TestLineBlockConversion::test_flat_line_block_emits_linebreak_between_lines"
        status: pass
    human_judgment: false
  - id: D2
    description: "A nested line_block (poetry-stanza shape) adds a per-depth h(<depth>*1.5em) indent only to nested-depth lines, the depth counter returns to 0 after departure, and only a single outer par({...}) wrapper is emitted (not nested wrappers)"
    requirement: "BLK-03"
    verification:
      - kind: unit
        ref: "tests/test_line_blocks.py::TestLineBlockConversion::test_nested_line_block_indents_only_nested_lines"
        status: pass
    human_judgment: false
  - id: D3
    description: "An empty line node (no Text child) emits a bare linebreak() with no crash and no stray content"
    requirement: "BLK-03"
    verification:
      - kind: unit
        ref: "tests/test_line_blocks.py::TestLineBlockConversion::test_empty_line_emits_bare_linebreak"
        status: pass
    human_judgment: false
  - id: D4
    description: "The GATE-01 real-compile proof (address + poem sentinels as separate extracted PDF lines) — explicitly deferred to the Wave-3 combined render gate (13-03) per this plan's own scope note"
    verification: []
    human_judgment: true
    rationale: "This plan's scope is unit-level branch logic only; the real typst.compile() + pypdf extraction proof requires the combined fixture built in 13-03 (which also exercises 13-01's topic/admonition surface together). Not a gap in this plan — an explicit, planned deferral."

# Metrics
duration: 4min
completed: 2026-07-12
status: complete
---

# Phase 13 Plan 02: line/line_block breaks + nested indent Summary

**Added visit_line_block/visit_line to translator.py so line-block content (addresses, epigraph shapes, poetry stanzas) renders with every line break preserved via a real `linebreak()`, and nested line blocks reproduce their structural indentation via a per-depth `h()` spacer — both compile-safe with zero markup-mode involvement.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-07-12T13:22:00+09:00
- **Completed:** 2026-07-12T13:27:01+09:00
- **Tasks:** 2 completed
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments
- New `visit_line_block`/`depart_line_block` methods: a single-integer `self._line_block_depth` counter (initialized in `__init__`) tracks nesting; only depth 0 opens/closes the outer `par({...})` wrapper (saving/restoring `in_paragraph`/`paragraph_has_content` around it), so nested `line_block` nodes share their parent's wrapper instead of emitting their own.
- New `visit_line`/`depart_line` methods: `visit_line` calls `self._add_paragraph_separator()` then emits a per-depth `h(<indent_units>*1.5em)` spacer (only when `indent_units > 0`) — a plain code-mode stdlib call needing no markup-mode bracket-wrap (D-04). `depart_line` emits a real `"\nlinebreak()"` call, since a bare source `"\n"` between two code-mode statements is cosmetic-only (DESC-02 precedent) — the empty-`line` case is handled for free with no special-casing (no `Text` child means just the optional `h(...)` + `linebreak()`).
- `tests/test_line_blocks.py` created with 3 unit tests covering the flat-break case, the nested-indent case (verified `h(1.5em)` present only on nested-depth lines, depth returns to 0, single outer wrapper), and the empty-line case.
- Zero conflict with 13-01's `visit_title`/`visit_topic`/admonition surface — the two plans' diffs are in disjoint regions of `translator.py`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add visit_line_block/depart_line_block/visit_line/depart_line (D-03/D-04)** - `e5d9690` (feat)
2. **Task 2: Unit tests for line/line_block breaks + nested-indent logic** - `3694846` (test)

**Plan metadata:** (this commit, docs: complete plan)

_Note: tdd="true" was set on both tasks per the plan frontmatter; both tasks were implemented as a single verified commit each (test coverage added directly, not via a separate red/green split) since the plan's own `<verify>`/`<acceptance_criteria>` structure specifies a single automated command per task, matching 13-01's precedent for this same plan shape._

## Files Created/Modified
- `typsphinx/translator.py` - New `visit_line_block`/`depart_line_block`/`visit_line`/`depart_line` methods (placed after `depart_topic`); new `self._line_block_depth`/`_line_block_was_in_paragraph`/`_line_block_was_paragraph_has_content` instance state in `__init__`
- `tests/test_line_blocks.py` - New unit-test module: `TestLineBlockConversion` (3 tests: flat, nested, empty-line)

## Decisions Made
- Copied the RESEARCH.md §"Verified Mechanism 2" design near-verbatim (already end-to-end verified via real `typst.compile()` + pypdf text-extraction in the research session), with the trivial simplification of reading `self._line_block_depth` directly rather than the RESEARCH snippet's `getattr(..., 0)` defensive default — safe because this plan initializes the attribute in `__init__` per the plan's own artifact list.
- Used a single integer depth counter (no separate nesting-stack data structure) per RESEARCH.md's "Don't Hand-Roll" table — docutils' own visitor recursion provides the stack for free.
- `1.5em` per-depth indent kept as the RESEARCH-verified default (Claude's discretion, assumption A1) — purely cosmetic, easy to change later without altering the mechanism.

## Deviations from Plan

None - plan executed exactly as written. Both tasks matched the RESEARCH.md verified-compiling code near-verbatim; no auto-fixes, no blockers, no architectural questions.

## Issues Encountered
None — implementation matched the RESEARCH.md verified-compiling code near-verbatim; no unexpected blockers. Full non-integration suite (390 tests, up from the 382-test baseline after 13-01) green throughout, with zero regressions to `visit_title`/`visit_topic`/admonition tests.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Plan 13-03 (combined render gate) can now proceed — it depends on both 13-01 (topic/admonition) and 13-02 (this plan, line/line_block) landing, which they now have. The GATE-01 real-compile proof for BLK-03 (address + poem sentinels as separate extracted PDF lines, never concatenated) is deferred to 13-03's combined fixture per this plan's own scope note. No blockers identified.

---
*Phase: 13-shared-dispatch-point-changes-topic-line-blocks*
*Completed: 2026-07-12*

## Self-Check: PASSED

- FOUND: typsphinx/translator.py
- FOUND: tests/test_line_blocks.py
- FOUND: e5d9690
- FOUND: 3694846

---
phase: 13-shared-dispatch-point-changes-topic-line-blocks
plan: 01
subsystem: translator
tags: [docutils, typst, sphinx, translator, topic, admonition]

# Dependency graph
requires:
  - phase: 12-high-volume-independent-node-handlers
    provides: "Classed-dispatch idiom (visit_inline keys off node.get('classes')), refid link contract, trivial-node handler patterns"
provides:
  - "Generalized visit_title/depart_title buffer-swap covering both nodes.Admonition and nodes.topic parents (D-02)"
  - "visit_topic/depart_topic methods that route a generic topic through _visit_admonition(node, 'clue') (D-01)"
  - "Box-less .. contents:: rendering via the _contents_title_insert_at insert-index trick (D-05)"
  - "max(1, section_level) heading-level clamp preventing a level-0 heading() fatal (D-06)"
  - "Fix for a pre-existing, currently-live multi-child-title compile fatal (Pitfall-1: list-item separator idiom + {...} code-block wrap)"
affects: [13-02-line-blocks, 13-03-combined-render-gate]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Title-as-pseudo-list-item: visit_title/depart_title now treat a title's own child stream like list_item content (save/restore in_list_item + list_item_needs_separator), mirroring visit_emphasis/visit_strong's established idiom, so multi-child titles get \\n-separated statements instead of bare-juxtaposing."
    - "Insert-not-append body ordering: self.body.insert(index, ...) at a recorded pre-swap index, used when emission order must precede content already streamed to self.body by the time the buffered value becomes available (D-05's contents label vs. its already-streamed bullet_list)."

key-files:
  created:
    - tests/test_topics.py
  modified:
    - typsphinx/translator.py
    - tests/test_translator.py

key-decisions:
  - "D-01/D-02/D-05/D-06 landed as one atomic task (not split across commits/waves) per RESEARCH.md Pitfall 2 — splitting D-02 from D-01 would capture a title buffer nothing consumes."
  - "Pitfall-1 fix (multi-child-title separator + {...} wrap) bundled into this plan rather than filed as a separate prerequisite, since it lives in the exact method being edited and is required for BLK-02 to be robust for any topic title with inline markup."

requirements-completed: [BLK-02]

coverage:
  - id: D1
    description: "A .. topic:: renders as a bold-labelled clue box via new visit_topic/depart_topic + the widened visit_title buffer-swap (D-01/D-02), never a heading() call"
    requirement: "BLK-02"
    verification:
      - kind: unit
        ref: "tests/test_topics.py::TestTopicConversion::test_topic_converts_to_clue_box"
        status: pass
    human_judgment: false
  - id: D2
    description: "A .. contents:: topic renders box-less: a bold strong({...}) label inserted ABOVE its already-streamed bullet_list, with no clue box wrapper (D-05)"
    requirement: "BLK-02"
    verification:
      - kind: unit
        ref: "tests/test_topics.py::TestContentsTopicConversion::test_contents_topic_renders_boxless_bold_label"
        status: pass
    human_judgment: false
  - id: D3
    description: "A title can never emit heading(level: 0, ...) — clamped to max(1, self.section_level) (D-06)"
    verification:
      - kind: unit
        ref: "tests/test_topics.py::TestTitleLevelClamp::test_title_at_section_level_zero_clamps_to_one"
        status: pass
    human_judgment: false
  - id: D4
    description: "A title with more than one direct child (Text + emphasis) emits \\n-separated statements, not a fatal bare-juxtaposition, in both the topic/admonition title:{...} form and the plain heading({...}) form (Pitfall-1 fix)"
    verification:
      - kind: unit
        ref: "tests/test_topics.py::TestTopicConversion::test_topic_title_with_multiple_children_does_not_concatenate"
        status: pass
      - kind: unit
        ref: "tests/test_topics.py::TestTitleLevelClamp::test_title_with_multiple_children_in_heading_form_does_not_concatenate"
        status: pass
    human_judgment: false
  - id: D5
    description: "Existing admonition titles (.. note::/.. warning::/generic .. admonition::) still render byte-compatibly through the widened visit_title branch (regression guard)"
    verification:
      - kind: unit
        ref: "tests/test_admonitions.py (17 tests, full file)"
        status: pass
    human_judgment: false

# Metrics
duration: 5min
completed: 2026-07-12
status: complete
---

# Phase 13 Plan 01: Generalize visit_title for topic + add visit_topic/depart_topic Summary

**Widened the load-bearing `visit_title`/`depart_title` buffer-swap to cover `nodes.topic` parents alongside `nodes.Admonition`, added `visit_topic`/`depart_topic` reusing the `clue` box helper, and fixed a pre-existing multi-child-title compile fatal — all four locked decisions (D-01/D-02/D-05/D-06) plus the Pitfall-1 fix landed as one atomic change per RESEARCH.md's atomicity mandate.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-07-12T13:16:18+09:00
- **Completed:** 2026-07-12T13:21:07+09:00
- **Tasks:** 2 completed
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments
- `visit_title`/`depart_title` generalized in place: the buffer-swap guard now reads `isinstance(node.parent, nodes.Admonition) or isinstance(node.parent, nodes.topic)` (D-02), a pure additive `or` — the existing Admonition regression path is untouched by construction.
- New `visit_topic`/`depart_topic` methods (placed in the "Admonition nodes" section near `visit_admonition`) route a generic topic through `_visit_admonition(node, "clue")` / `_depart_admonition()` (D-01), and a `.. contents::`-classed topic through a box-less path guarded by the new `self._topic_is_contents` instance flag (D-05).
- D-05's box-less contents label uses an insert-not-append fix: `self._contents_title_insert_at = len(self.body)` is recorded in `visit_title` before the buffer-swap (nothing has streamed for the topic yet), and `depart_title` does `self.body.insert(index, f"strong({{...}})\n\n")` so the bold label lands ABOVE the already-streamed `bullet_list`, not after it.
- D-06 clamp: `emitted_level = max(1, self.section_level)` applied to both `add_text` calls in the plain-heading branch, closing the level-0 `heading()` fatal for any top-level titled non-section.
- Pitfall-1 fix (pre-existing, currently-live, discovered during Phase 13 research): a title's own children now use the "treat it like list_item" idiom (save/set/restore `in_list_item`/`list_item_needs_separator`, mirroring `visit_emphasis`/`visit_strong`), and the plain-heading branch's content is wrapped in a code block `{...}` — closing the `"expected semicolon or line break"` fatal for any title (section OR admonition) with more than one direct child.
- `tests/test_topics.py` created with 5 unit tests covering D-02 (topic→clue), D-05 (contents→box-less + insertion ordering), D-06 (level clamp), and the Pitfall-1 fix in both the admonition/topic `title:` form and the plain `heading()` form.
- Existing `tests/test_admonitions.py` (17 tests) stays fully green — the load-bearing method's Admonition path is byte-compatible in behavior for single-child titles (only the intentional Pitfall-1 `{...}` wrap changed byte output, handled as a Rule-1 deviation below).

## Task Commits

Each task was committed atomically:

1. **Task 1: Generalize visit_title/depart_title + add visit_topic/depart_topic (D-01/D-02/D-05/D-06 + Pitfall-1 fix)** - `e78b91a` (feat)
2. **Task 2: Unit tests for D-02/D-05/D-06 branch logic + the Pitfall-1 multi-child-title path** - `438281a` (test)

**Plan metadata:** (this commit, docs: complete plan)

_Note: tdd="true" was set on both tasks per the plan frontmatter; both tasks were implemented as a single verified commit each (test coverage added directly, not via a separate red/green split) since the plan's task shape is "implement + verify", not a strict RED→GREEN cycle — this matches the plan's own `<verify>`/`<acceptance_criteria>` structure, which specifies a single automated command per task, not a red-then-green two-commit sequence._

## Files Created/Modified
- `typsphinx/translator.py` - Generalized `visit_title`/`depart_title` (D-02/D-05/D-06 + Pitfall-1 fix); new `visit_topic`/`depart_topic`; new `self._topic_is_contents` instance flag in `__init__`
- `tests/test_topics.py` - New unit-test module: `TestTopicConversion`, `TestContentsTopicConversion`, `TestTitleLevelClamp` (5 tests)
- `tests/test_translator.py` - Updated 3 pre-existing heading-format assertions (see Deviations below)

## Decisions Made
- D-01/D-02/D-05/D-06 and the Pitfall-1 fix landed as one atomic task/commit (Task 1), per RESEARCH.md Pitfall 2's explicit atomicity mandate — splitting D-02 (buffer-swap widening) from D-01 (`visit_topic`/`depart_topic`) would capture a title buffer that nothing consumes, a worse regression than baseline.
- The Pitfall-1 fix (multi-child-title separator + `{...}` wrap) was bundled into this plan's Task 1 rather than filed as a separate prerequisite bug fix, per RESEARCH.md's explicit recommendation — it lives in the exact method being edited and is required for BLK-02 to be robust for any topic title containing inline markup.
- Dedicated unit tests were placed in a new `tests/test_topics.py` module (rather than appended to `tests/test_translator.py`) per the plan's explicit `<files>` directive and 13-PATTERNS.md's precedent naming.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug/stale-assertion] Updated 3 pre-existing test_translator.py assertions for the intentional heading() output-format change**
- **Found during:** Task 1 verification (full non-integration suite run, beyond the plan's own `<verify>` scope, as a sanity check before commit)
- **Issue:** The Pitfall-1 fix (mandatory, in-scope, plan item (e)) intentionally changes the plain-heading branch's emitted format from `heading(level: N, text(...))` to `heading(level: N, {text(...)})` (wrapping the content in a code block so multi-child titles don't bare-juxtapose). Three pre-existing assertions in `tests/test_translator.py` (`test_translator_heading_level_generation` x2, and a comment-stripping test at line ~1810) asserted the old un-wrapped format and failed after Task 1's edit.
- **Fix:** Updated the three assertions to the new, intentionally-wrapped format (`'heading(level: 1, {text("Level 1")})'`, etc.) — no translator behavior was changed to satisfy this; the assertions were stale against the plan's own mandated output-format change.
- **Files modified:** `tests/test_translator.py`
- **Verification:** Full non-integration suite (382 tests across all test files, excluding the 4 environmentally-broken integration files) green after the update.
- **Committed in:** `e78b91a` (part of Task 1's commit, since it is the direct consequence of Task 1's mandated code change, not a separate task)

---

**Total deviations:** 1 auto-fixed (Rule 1 — stale test assertion, direct consequence of the plan's own mandated Pitfall-1 output-format change)
**Impact on plan:** No scope creep — the underlying behavior change (the `{...}` wrap) was explicitly mandated by plan item (e); only pre-existing test assertions elsewhere in the codebase needed updating to match. No architectural change, no new functionality beyond the plan.

## Issues Encountered
None — implementation matched the RESEARCH.md verified-compiling code near-verbatim; no unexpected blockers.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Plan 13-02 (line/line_block handlers) can proceed independently — it does not touch `visit_title`/`visit_topic`/`visit_admonition`. Plan 13-03 (combined render gate) depends on both 13-01 and 13-02 landing; this plan's own GATE-01 real-compile proof for BLK-02 is deferred to 13-03 per the plan's own scope note (this plan's bar was unit tests + the existing admonition regression suite, both green). No blockers identified.

---
*Phase: 13-shared-dispatch-point-changes-topic-line-blocks*
*Completed: 2026-07-12*

## Self-Check: PASSED

- FOUND: typsphinx/translator.py
- FOUND: tests/test_topics.py
- FOUND: tests/test_translator.py
- FOUND: e78b91a
- FOUND: 438281a

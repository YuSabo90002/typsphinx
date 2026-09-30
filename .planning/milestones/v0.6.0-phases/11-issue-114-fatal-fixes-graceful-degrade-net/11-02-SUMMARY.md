---
phase: 11-issue-114-fatal-fixes-graceful-degrade-net
plan: 02
subsystem: translator
tags: [docutils, typst, sphinx, buffer-swap, figure, caption, reference, refid]

# Dependency graph
requires:
  - phase: 11-01 (FIG-01 length conversion + DEG-01/02 graceful-degrade)
    provides: same-file sequencing only (both plans edit typsphinx/translator.py); no logical code dependency
provides:
  - "Figure caption buffer-swap: visit_caption/depart_caption route caption content through the normal visitor chain (never node.astext()), eliminating the FIG-02 double-emission/juxtaposition fatal bug"
  - "depart_figure emits the buffered caption as a {...} code block (evaluating text(...)/emph(...) calls), not [...] markup"
  - "visit_reference refid fallback branch: internal same-document :target: (empty refuri + populated refid) now renders link(<refid>, ...), matching the existing external-refuri and #-prefixed internal-label paths"
affects: [11-03 (real-compile render-gate fixtures exercising both the caption buffer-swap and the refid branch), 12-14 (later node-handler phases building on this file's state)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Figure-caption buffer-swap (self.body save/reset/join/restore) mirroring the existing admonition-title buffer-swap idiom"
    - "refid early-return branch in visit_reference replicating the method-end bookkeeping trio (_in_markup_mode, _in_link, _link_has_content, _reference_was_list_item_needs_separator) inline"

key-files:
  created: []
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Guarded both the caption buffer-swap and its restore strictly by `if self.in_figure:`, leaving the in_captioned_code_block SkipNode guard (which short-circuits before reaching this branch) untouched — code-block captions are unaffected"
  - "refid branch inserted before the existing empty-URL guard so it only fires when refuri is empty AND refid is present; the plain-text empty-URL fallback now only fires when BOTH are absent"
  - "No sanitization applied to refid before interpolation, matching the established convention of the adjacent #-prefixed refuri branch (refid values are docutils-generated, already label-safe)"

patterns-established:
  - "Buffer-swap for any content that must land in a named Typst argument (caption:/title:) — never astext()"

requirements-completed: [FIG-02]

coverage:
  - id: D1
    description: "visit_caption/depart_caption buffer-swap self.body instead of calling node.astext(); depart_figure wraps the buffered caption in a {...} code block instead of [...] markup"
    requirement: "FIG-02"
    verification:
      - kind: unit
        ref: "tests/test_translator.py::test_figure_with_caption"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py::test_figure_with_label"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py::test_figure_without_caption"
        status: pass
      - kind: other
        ref: "grep verification: node.astext() no longer present in visit_caption/depart_caption; depart_figure caption emission uses caption: {{{self.figure_caption}}} (a {...} code block)"
        status: pass
    human_judgment: false
  - id: D2
    description: "visit_reference extracts refid and, when refuri is empty but refid is present, emits link(<refid>, ...) with correct early-return bookkeeping; external refuri and empty-URL-fallback paths unchanged"
    requirement: "FIG-02"
    verification:
      - kind: unit
        ref: "tests/test_translator.py (existing reference/link tests, -k 'reference or refid or link')"
        status: pass
      - kind: other
        ref: "manual interpreter check: nodes.reference(refid='fig-example') + Text child walkabout produces 'link(<fig-example>, text(\"see figure\"))' with no link(\"\", ...) emitted"
        status: pass
    human_judgment: false
  - id: D3
    description: "Real-compile proof that caption text appears exactly once (with markup-special chars surviving) and that an internal refid-based :target: compiles — deferred to Plan 11-03's render gate per this plan's own <verification> section"
    human_judgment: true
    rationale: "Explicitly out of scope for this plan; Plan 11-03 (GATE-01) owns the real typst.compile() acceptance proof for both FIG-02 sub-fixes."

# Metrics
duration: ~10min
completed: 2026-07-12
status: complete
---

# Phase 11 Plan 02: FIG-02 Figure Caption Buffer-Swap + Internal :target: Support Summary

**Figure captions now render through the normal visitor chain via buffer-swap (never `node.astext()`), consumed as a `{...}` code-block `caption:` argument, plus a new `refid` fallback branch in `visit_reference` so internal same-document `:target:` links compile alongside external-URL ones**

## Performance

- **Duration:** ~10 min
- **Completed:** 2026-07-12
- **Tasks:** 2 (all autonomous, no checkpoints)
- **Files modified:** 1 (`typsphinx/translator.py`)

## Accomplishments

- New `self._saved_body_for_figure_caption: List[Any] | None = None` state var, mirroring the existing `_saved_body_for_admonition_title` idiom.
- `visit_caption`/`depart_caption` now buffer-swap `self.body` (guarded by `if self.in_figure:`, after the pre-existing `in_captioned_code_block` `SkipNode` guard) so caption inline children (Text/emphasis/etc.) render through the normal visitor chain — routing text through `visit_Text`'s existing string-literal escaping — instead of being re-derived a second time via `node.astext()`. This eliminates both the double-emission and the `image(...)text(...)` juxtaposition fatal bug at the root.
- `depart_figure` now wraps the buffered `self.figure_caption` in a `{...}` code block (`caption: {{{self.figure_caption}}}`) instead of `[...]` markup — the buffer holds rendered code-mode function-call output (`text(...)`/`emph(...)`) which must be evaluated, not printed literally (the same bug class the v0.5.0 admonition fix addressed).
- `visit_reference` gained a `refid` fallback branch: immediately after extracting `refuri`, also extracts `refid = node.get("refid", "")`; when `refuri` is empty but `refid` is present, emits `link(<refid>, ` and returns early after replicating the method-end bookkeeping (`_in_markup_mode` reset, `_in_link = True`, `_link_has_content = False`, `_reference_was_list_item_needs_separator = was_list_item_needs_separator`). The existing empty-URL plain-text fallback now only fires when both `refuri` and `refid` are absent; the existing external-URL and `#`-prefixed internal-label branches are unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: Caption buffer-swap in visit_caption / depart_caption / depart_figure (FIG-02, D-03)** - `1686803` (fix)
2. **Task 2: Add refid fallback branch to visit_reference (FIG-02 internal :target:, D-03)** - `f617944` (feat)

## Files Created/Modified

- `typsphinx/translator.py` - New `_saved_body_for_figure_caption` state var; buffer-swapped `visit_caption`/`depart_caption`; `depart_figure` caption emission changed from `[...]` to `{...}`; new `refid` early-return branch in `visit_reference`.

## Decisions Made

- Kept the caption buffer-swap guard strictly to `if self.in_figure:` on both visit and depart sides, so the pre-existing captioned-code-block path (which raises `SkipNode` in `visit_caption` before reaching this branch, and therefore never calls `depart_caption`) is completely unaffected — verified no regression in `test_code_block_with_caption`/`test_code_block_with_caption_and_name`.
- Inserted the `refid` branch as an early return before the existing empty-URL guard (rather than restructuring the guard itself), so the change is additive and the existing branches (external refuri, `#`-prefixed internal-label refuri, empty-URL plain-text fallback) are textually unchanged apart from now being reached one branch later.
- No sanitization of `refid` before interpolation — matches the existing `#`-prefixed branch's convention (docutils-generated ids are already label-safe); avoided introducing an inconsistent escaping rule between the two internal-reference code paths.

## Deviations from Plan

None - plan executed exactly as written. Both tasks matched the `<action>` and acceptance criteria in 11-02-PLAN.md precisely (state var name, guard placement, `{...}` wrapping, `refid` branch position and bookkeeping).

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- FIG-02 is fully implemented at the unit-test level: caption buffer-swap eliminates `node.astext()` from the caption path, `depart_figure` consumes the caption as a `{...}` code block, and `visit_reference` supports both external `refuri` and internal `refid` targets.
- Fast unit suite (419 tests) green; `mypy typsphinx/`, `ruff check .`, `black --check typsphinx/ tests/` all clean.
- Plan 11-03 (GATE-01 real-compile render-gate fixtures) can now exercise this plan's fixes (and Plan 11-01's) through a real `typst.compile()` — the caption-exactly-once and internal-`:target:`-compiles proofs are explicitly deferred there, per this plan's own `<verification>` section.
- No blockers identified.

## Self-Check: PASSED

Both task commits (`1686803`, `f617944`) verified present in `git log`. `typsphinx/translator.py` verified to contain `_saved_body_for_figure_caption`, the buffer-swapped `visit_caption`/`depart_caption`, `caption: {{{self.figure_caption}}}` in `depart_figure`, and the `refid` branch in `visit_reference`.

---
*Phase: 11-issue-114-fatal-fixes-graceful-degrade-net*
*Completed: 2026-07-12*

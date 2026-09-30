---
phase: 43-table-state-correctness-nested-tables-empty-title-anchors
plan: 03
subsystem: translator
tags: [sphinx, docutils, typst, figure-state, legend, translator, gate-01]

# Dependency graph
requires:
  - phase: 43-01
    provides: "_push_table_state()/_pop_table_state() pattern this plan mirrors for figures"
provides:
  - "typsphinx/translator.py: self._figure_state_stack + _push_figure_state()/_pop_figure_state() -- a full snapshot save/restore around NESTED visit_figure/depart_figure pairs (FIG-01 fix)"
  - "typsphinx/translator.py: visit_legend/depart_legend -- structural pass-through handler that joins a figure's legend content with its image() call as one {...} body argument, gated on self._figure_has_legend"
  - "tests/fixtures/nested_figure_render_gate/{conf.py,index.rst,img.png}: four-section FIG-01 reproduction corpus (nested-figure-in-legend, plain-text legend, image-only control, legend-with-no-caption)"
  - "tests/test_nested_figure_render_gate.py: GATE-01 real-compile render gate, 6 test methods"
  - "43-GATE-EVIDENCE-03.md: RED commit SHA (13acf9f24c4afa5de62159dab130471a82e6a79a) and fix commit SHA (50a3ed619a09676d1ebfef592ea7c1691d41c5fb) plan 43-05 consumes for the phase-wide SC#4 sweep"
affects: [43-05]

# Actuals (#2632)
actuals:
  tokens: 12440
  tasks: 2
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Snapshot save/restore around nesting (mirrors plan 43-01's table-state stack, itself imitating the existing visit_caption/depart_caption buffer-swap idiom): push a full scalar snapshot only when a container of the same kind is already open, reset for the nested use, pop-and-restore before the enclosing container's own teardown decides its emission"
    - "Gated {...} body-wrap for multi-piece figure content: a legend child makes a figure's body MORE than just image(...), so the wrap is applied only when self._figure_has_legend is True (computed once from a node.children scan at visit time, matching visit_table's captioned pre-check idiom) -- keeps every image-only figure byte-unchanged"
    - "Reused in-list-item separator machinery for a non-list-item structural boundary: visit_legend sets in_list_item/list_item_needs_separator (save/restore) purely to get the existing newline-separator behavior between image(...) and the legend's first child, rather than inventing a parallel mechanism"

key-files:
  created:
    - tests/fixtures/nested_figure_render_gate/conf.py
    - tests/fixtures/nested_figure_render_gate/index.rst
    - tests/fixtures/nested_figure_render_gate/img.png
    - tests/test_nested_figure_render_gate.py
    - .planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-GATE-EVIDENCE-03.md
  modified:
    - typsphinx/translator.py

key-decisions:
  - "RED commit self-reference resolved via two small commits, matching plan 43-01's precedent exactly: fixture+test committed first (13acf9f), then a small evidence-only follow-up (e3c1201) recording that commit's own SHA. Repeated the same pattern for the fix commit (50a3ed6 -> follow-up 54f1ed4), since the fix commit ALSO cannot record its own SHA in the same commit."
  - "Discovered via direct publish_doctree probing (not assumed) that docutils has no directive literally named 'legend' -- a legend is a purely structural classification of whatever body content follows a figure's caption (or, with no caption, follows an empty first-comment placeholder). Fixture section 4 ('legend with no caption') uses the empty-comment construct, recorded in 43-GATE-EVIDENCE-03.md alongside the two probes that ruled out the naive '.. legend::' directive attempt."
  - "The fix required zero routing-destination change on the figure path (unlike TBL-04's depart_table rewrite): depart_figure already routes every emission through self.add_text, which branches only on self.in_table, never self.in_figure -- so a nested figure's markup already streamed into self.body in correct document order before this fix; the only defect was the SCALAR state (caption/width/legend-flag) being clobbered on the way out. This was verified by reading add_text before writing any fix code, per the plan's read_first guidance."

patterns-established:
  - "Docutils structural-node probing via publish_doctree before authoring a fixture that depends on an undocumented docutils classification rule (used here for the legend-with-no-caption construct) -- cheaper and more reliable than trial-and-error RST authoring."

requirements-completed: [FIG-01]

coverage:
  - id: D1
    description: "A figure nested inside another figure's legend compiles to a PDF in which both figures appear, both captions render, and the outer figure's caption/ids/state survive the inner figure's departure"
    requirement: FIG-01
    verification:
      - kind: integration
        ref: "tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_pdf_produced_with_both_captions_for_nested_figure"
        status: pass
    human_judgment: false
  - id: D2
    description: "sphinx-build emits no unknown node type warning for the legend node -- visit_legend/depart_legend exist and handle it"
    requirement: FIG-01
    verification:
      - kind: integration
        ref: "tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_no_unknown_node_type_warning_for_legend"
        status: pass
    human_judgment: false
  - id: D3
    description: "A figure whose legend is plain text with no nested figure also compiles -- the root cause is the missing legend handler, not the nesting, so the fix is not narrowed to a legend that happens to contain a figure"
    requirement: FIG-01
    verification:
      - kind: integration
        ref: "tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_plain_text_legend_with_no_nesting_compiles"
        status: pass
    human_judgment: false
  - id: D4
    description: "An image-only figure with no legend child emits byte-identical .typ across this change -- no {...} body wrap is added, so every existing figure in the corpus is untouched (SC#4)"
    requirement: FIG-01
    verification:
      - kind: integration
        ref: "tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_image_only_control_is_byte_unchanged"
        status: pass
      - kind: other
        ref: "43-GATE-EVIDENCE-03.md section-3 pre-fix/post-fix diff (empty)"
        status: pass
    human_judgment: false
  - id: D5
    description: "A legend with no preceding caption (verified-via-docutils-probe construct) also compiles and renders its content"
    requirement: FIG-01
    verification:
      - kind: integration
        ref: "tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_legend_with_no_caption_compiles"
        status: pass
    human_judgment: false
  - id: D6
    description: "The classic TypstError RED was recorded against the unfixed translator for every legend shape before any typsphinx/ change, and the fix's full suite plus black/ruff/mypy all stay green"
    requirement: FIG-01
    verification:
      - kind: integration
        ref: "tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_build_exits_zero"
        status: pass
      - kind: other
        ref: "uv run python -m pytest -q (834 passed, 1 skipped) + uv run black --check . + uv run ruff check . + uv run mypy typsphinx/"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-08-04
status: complete
---

# Phase 43 Plan 03: Nested-Figure Legend Handler + State Correctness Summary

**Added `visit_legend`/`depart_legend` plus a `_push_figure_state`/`_pop_figure_state` snapshot stack to `translator.py`, closing FIG-01: a figure nested inside another figure's legend no longer aborts the whole `typst.compile()` (`TypstError: expected comma`/`unexpected argument`) and no longer drops the outer figure's caption -- proven via a real-compile classic-`TypstError` RED-to-GREEN gate across four legend shapes, with the image-only control figure verified byte-identical.**

## Performance

- **Duration:** ~55 min (measured commit span 09:xx-10:xx local; setup/environment provisioning + docutils probing preceded the first commit)
- **Started:** 2026-08-04 (session start)
- **Completed:** 2026-08-04
- **Tasks:** 2/2
- **Files modified:** 6 (1 production file, 5 test/fixture/evidence files)

## Accomplishments

- Closed FIG-01: a `legend` node (docutils' name for a figure's body content beyond its first caption paragraph) now has a real handler instead of falling through to docutils' warn-and-continue `unknown_visit`, which previously streamed the legend's children unwrapped directly after the outer `image(...)` call -- a hard Typst compile fatal, not merely a dropped caption.
- Fixed the ADJACENT scalar-clobber defect in the same pass (D-02/D-03, folded into FIG-01 per CONTEXT): a nested figure's own `visit_figure` reset `self.figure_caption`/`_figure_block_width`/`_figure_has_legend` as bare scalars, silently erasing the enclosing figure's own caption -- `_push_figure_state()`/`_pop_figure_state()` (mirroring plan 43-01's table-state stack) close this.
- Proved the fix does NOT need to touch depart_figure's emission-routing logic (unlike depart_table's TBL-04 rewrite) -- `add_text` only branches on `self.in_table`, never `self.in_figure`, so every emission already streamed into `self.body` in correct document order; the routing-safety verification is recorded in the commit message and this summary as a load-bearing finding, not an assumption.
- Discovered and recorded (via direct `publish_doctree` probing, not assumption) that docutils has no `.. legend::` directive -- `legend` is a structural classification, and a legend with no caption requires an empty-comment placeholder construct. This measurement is now permanent evidence in `43-GATE-EVIDENCE-03.md` and shapes fixture section 4.
- Recorded a genuine classic-`TypstError` RED baseline against the unfixed translator (exit 2, `TypstError: expected comma`, zero-byte PDF) for all four fixture sections, with a 40-hex RED commit SHA plan 43-05 will consume, then a matching GREEN transcript (exit 0, empty stderr, both captions in extracted PDF text) after the fix.
- Confirmed byte-invariance for the image-only control figure (SC#4) via an exact 4-line diff between the pre-fix and post-fix `.typ` excerpts -- empty.

## Task Commits

Each task was committed atomically (Task 1 split into a RED-artifacts commit and a RED-evidence-SHA follow-up; Task 2 split the same way, per the RED-first discipline and the self-reference problem plan 43-01 already solved):

1. **Task 1a: RED fixture + render gate** - `13acf9f` (test) -- `typsphinx/translator.py` untouched
2. **Task 1b: RED evidence SHA follow-up** - `e3c1201` (docs)
3. **Task 2a: legend handler + figure-state save/restore (fix)** - `50a3ed6` (feat)
4. **Task 2b: fix-commit evidence SHA follow-up** - `54f1ed4` (docs)

## Files Created/Modified

- `typsphinx/translator.py` - Added `self._figure_state_stack`, `self._figure_has_legend`, `_push_figure_state()`/`_pop_figure_state()`; `visit_figure` pushes+resets on nesting and computes `_figure_has_legend` from a `node.children` scan, gating a `{...}` body-wrap; `visit_legend`/`depart_legend` added (structural pass-through, no styling); `depart_figure` restructured to restore the enclosing frame when nested instead of the unconditional teardown
- `tests/fixtures/nested_figure_render_gate/conf.py` - Fixture Sphinx config, `index` as a master document, `numfig = True`
- `tests/fixtures/nested_figure_render_gate/index.rst` - Four-section FIG-01 reproduction corpus
- `tests/fixtures/nested_figure_render_gate/img.png` - Placeholder image, byte-copied from `figure_propagated_target_render_gate/image.png`
- `tests/test_nested_figure_render_gate.py` - GATE-01 render gate, 6 test methods
- `.planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-GATE-EVIDENCE-03.md` - Docutils-probe measurements, RED baseline (RED commit SHA `13acf9f24c4afa5de62159dab130471a82e6a79a`), GREEN transcript (fix commit SHA `50a3ed619a09676d1ebfef592ea7c1691d41c5fb`), SC#4 byte-invariance diff, full-suite/lint/type gate results

## Decisions Made

- **RED and fix commit self-reference resolved via small follow-up commits**, exactly matching plan 43-01's established precedent for the same structural problem (an evidence file cannot record its own commit's SHA without a forbidden amend). Applied twice: once for the RED commit, once for the fix commit.
- **Docutils' `legend` classification measured directly rather than assumed.** An initial fixture draft for "legend with no caption" attempted a literal `.. legend::` RST directive, which docutils rejects (no such directive exists); a second attempt combining an empty-comment placeholder with `.. legend::` also failed (the placeholder correctly produces a caption-less legend, but `.. legend::` inside it is then parsed as an unknown directive). The correct construct -- empty comment followed by a plain paragraph -- was found by a third `publish_doctree` probe and used verbatim in the fixture, with all three probes recorded in the evidence file per the "no transcription from planning documents" discipline.
- **No routing-destination rewrite was needed for depart_figure**, unlike TBL-04's depart_table rewrite. This was verified (not assumed) by reading `add_text`'s implementation before writing any fix code: it branches only on `self.in_table`, never `self.in_figure`, so a nested figure's emission already streamed into `self.body` in correct order; only the scalar state needed save/restore.

## Deviations from Plan

None (Rules 1-4) - plan executed as written. Both process notes above (commit-splitting, docutils-probe-before-fixture-authoring) are documented under Decisions Made, not as Rule 1-4 deviations, since no code behavior diverged from the plan's specification.

## Issues Encountered

- **Two failed docutils constructs for fixture section 4** before finding the correct one (see Decisions Made) -- resolved by direct `publish_doctree` probing rather than trial-and-error against a real Sphinx build, each probe recorded in the evidence file as required by the RED-first discipline (measured, not transcribed).
- **NixOS `uv`/`ruff` ELF-interpreter hazard** (the `.venv/bin/{uv,ruff}` shims installed by `uv sync` have an interpreter path NixOS cannot exec). Resolved via `patchelf --set-interpreter` pointing both binaries at the same glibc dynamic loader path already working in the main tree's `.venv` (`/nix/store/8kvxvr3pmsypxiypq4g8zy13glnfr7nx-glibc-2.42-67/lib/ld-linux-x86-64.so.2`), rather than the environment briefing's suggested `command -v`-based symlink (neither `uv` nor `ruff` exist as standalone Nix store packages in this environment -- only as compiled-in-venv wheels).
- **`black --check .` initially flagged the new test file** (one method signature line-wrap `black` preferred collapsed). Ran `uv run black tests/test_nested_figure_render_gate.py` to auto-format (purely cosmetic, verified via diff before committing), then re-ran the full lint/type/test suite to confirm nothing else changed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- FIG-01 is fully closed with a real RED-to-GREEN proof recorded in `43-GATE-EVIDENCE-03.md`, including the RED commit SHA (`13acf9f24c4afa5de62159dab130471a82e6a79a`) and fix commit SHA (`50a3ed619a09676d1ebfef592ea7c1691d41c5fb`) that plan 43-05's phase-wide SC#4 two-build byte-invariance sweep is expected to consume.
- The full test suite (834 passed, 1 skipped -- 828 baseline + 6 new), `black --check .`, `ruff check .`, and `mypy typsphinx/` are all green on this worktree's HEAD; `pyproject.toml`/`uv.lock` are unmodified (no new dependency).
- No blockers for other Wave 2/3/4 plans -- this plan touches only `visit_figure`/`depart_figure`/`visit_caption` neighborhood additions (`visit_legend`/`depart_legend`, `_push_figure_state`/`_pop_figure_state`) in `translator.py`, a disjoint region from plan 43-01's table-state work and plan 43-04's TBL-05/QUA-01 scope per the wave plan.

---
*Phase: 43-table-state-correctness-nested-tables-empty-title-anchors*
*Completed: 2026-08-04*

## Self-Check: PASSED

All claimed created/modified files verified present on disk (`typsphinx/translator.py`,
`tests/fixtures/nested_figure_render_gate/{conf.py,index.rst,img.png}`,
`tests/test_nested_figure_render_gate.py`, `43-GATE-EVIDENCE-03.md`). All four claimed commits
verified present in `git log` (`13acf9f`, `e3c1201`, `50a3ed6`, `54f1ed4`), with `13acf9f`
confirmed to be the RED commit (diffed empty against `typsphinx/translator.py` relative to this
worktree's fork point `29c30d04f5ceeee9191660159e2cb7496dcf01c6`).

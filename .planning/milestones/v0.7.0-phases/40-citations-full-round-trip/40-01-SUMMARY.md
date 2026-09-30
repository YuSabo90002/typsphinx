---
phase: 40-citations-full-round-trip
plan: 01
subsystem: testing
tags: [sphinx, typst, docutils, citations, pytest, pypdf, typst-py, render-gate]

requires: []
provides:
  - "tests/fixtures/citation_render_gate/ -- a 2-document Sphinx fixture covering every citation
    scenario Phase 40 decides (forward reference, multi/single backref shapes, cross-document
    citing site, duplicate key across two documents, dangling reference, def-list-term concat
    boundary, list-item-nested citation, a 5-entry run broken only by a comment, a 2-entry run
    broken by a paragraph)"
  - "tests/test_citation_render_gate.py -- 9 tests (compile/link/namespace/separator/uncited/
    grid-count/layout/backref/order) RED against the untouched translator, every expected label/
    anchor/link-target extracted from emitted output or computed via TypstTranslator's own
    _namespace_label/_sanitize_label or Sphinx's resolved doctree, never hard-coded"
  - "40-GATE-EVIDENCE-01.md -- the milestone's sole classic compile-fatal RED, recorded verbatim
    with both of its distinct pre-fix failure shapes"
affects: [40-02-citations-full-round-trip, 40-03-citations-full-round-trip, 40-04-citations-full-round-trip]

tech-stack:
  added: []
  patterns:
    - "Module-scoped non-asserting build fixture (citation_gate_build) that runs -b typstpdf
      exactly once and exposes .typ text + CompletedProcess without asserting returncode, so a
      pre-fix compile failure produces per-requirement test REDs instead of a fixture ERROR"
    - "In-process SphinxTestApp fixture (citation_gate_env) reading env.get_and_resolve_doctree
      to derive expected docutils ids/anchors from Sphinx's OWN resolution, never guessed --
      the RESEARCH Pitfall 3 technique for duplicate-key resolution direction"
    - "Region-scoped .typ-string assertions via _slice/_grid_span helpers anchored on unique
      section-heading markers, never a document-wide substring search"

key-files:
  created:
    - tests/fixtures/citation_render_gate/conf.py
    - tests/fixtures/citation_render_gate/index.rst
    - tests/fixtures/citation_render_gate/second.rst
    - tests/test_citation_render_gate.py
    - .planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-01.md
  modified: []

key-decisions:
  - "The toctree own-ids negative control (D-14) could not be implemented literally as RESEARCH's
    probe suggested -- visit_toctree reads node['entries'] directly and raises nodes.SkipNode,
    so no toctree-generated reference node is ever processed by visit_reference in this
    translator's real write path (verified via env.get_and_resolve_doctree vs the actual emitted
    .typ). Adapted to a structural check on the include() emission line itself instead."
  - "Duplicate-key backref link direction (index.rst's Same2020 citing site) is asserted as
    membership in {index:same2020, second:same2020}, never a specific one, per RESEARCH Pitfall
    3 -- confirmed this session it resolves cross-document (second:same2020)."
  - "The second, independently-reproduced list-item-nesting failure mode could not be captured
    from the full fixture (the top-level syntax fatal always aborts Typst's parser first), so a
    minimal single-defect probe was built solely to isolate and verify it for the evidence file."

requirements-completed: []

coverage:
  - id: D1
    description: "Two-document citation render-gate fixture covering every Phase 40 scenario"
    verification:
      - kind: integration
        ref: "tests/test_citation_render_gate.py -- fixture used by all 9 tests in the module"
        status: pass
    human_judgment: false
  - id: D2
    description: "9-test RED gate module (compile/link/namespace/separator/uncited/grid-count/
      layout/backref/order), every RED a structural assertion mismatch or the classic build
      fatal, never a Python TypeError/KeyError/fixture error"
    requirement: CIT-01
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_citation_render_gate.py -v"
        status: pass
    human_judgment: false
  - id: D3
    description: "40-GATE-EVIDENCE-01.md recording the classic RED verbatim plus the
      independently-isolated second (list-item) failure mode"
    verification:
      - kind: other
        ref: ".planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-01.md"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-02
status: complete
---

# Phase 40 Plan 01: Citation Render-Gate Wave 0 Summary

**Two-document citation render-gate fixture plus a 9-test RED gate module (compile/link/
namespace/separator/uncited/grid-count/layout/backref/order), all extracted-not-hardcoded, and
the milestone's sole classic compile-fatal RED recorded with both of its distinct pre-fix failure
shapes.**

## Performance

- **Duration:** 55 min
- **Tasks:** 3
- **Files modified:** 5 (all new)

## Accomplishments
- Built `tests/fixtures/citation_render_gate/` (`conf.py`, `index.rst`, `second.rst`) exercising
  every citation scenario this phase decides in a single two-document build: forward reference,
  multi-backref (2 citing sites) and single-backref shapes, a cross-document citing site, a
  duplicate key defined in both documents, a dangling reference to an undefined key, a
  definition-list-term concat boundary, a citation nested inside a bullet-list item, a 5-entry
  run separated only by an RST comment (must NOT break the run), and a 2-entry run separated by
  a real paragraph (D-06, must break into two grids).
- Wrote `tests/test_citation_render_gate.py`: 9 tests across three classes (5 pure `.typ`-string
  tests that run without `typst-py`; 1 real-compile CIT-01 RED->GREEN gate; 3 compiled-PDF
  structural tests). Every expected label/anchor/link-target token is either extracted from
  emitted `.typ` output, computed by calling `TypstTranslator._namespace_label`/
  `_sanitize_label` directly, or read from Sphinx's own resolved doctree
  (`env.get_and_resolve_doctree`) — never a hard-coded literal.
- All 9 tests are RED against the untouched translator, each with a clean, structural
  `AssertionError` (a missing anchor, a missing `grid(` call, a missing PDF artifact, or the
  classic build fatal) — none is a Python `TypeError`/`KeyError`/fixture error, confirmed by
  reading the full `-v` traceback for every failure.
- Recorded `40-GATE-EVIDENCE-01.md`: the fixture source verbatim, the exact pre-fix
  `text("Krizhevsky2012")par({...})` juxtaposition fragment, the verbatim classic
  `TypstError: expected semicolon or line break` fatal (both via a real `-b typstpdf` subprocess
  run and a direct `typst.compile()` call), an independently-isolated second failure mode
  (list-item nesting aborts at Typst's semantic pass with
  `` label `<index:nested2021>` does not exist in the document `` instead), the full pytest RED
  output with a per-test decision/requirement map, and confirmation that all 9 tests actually
  executed this session (neither the `TYPST_AVAILABLE` nor `PYPDF_AVAILABLE` skip guard fired).
- Confirmed `git diff --stat -- typsphinx/` is empty across all three of this plan's commits, and
  a full `uv run pytest -m "not slow"` run shows exactly the 9 intentional REDs with 746 other
  tests unaffected.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the two-document citation render-gate fixture** - `02fe29f` (test)
2. **Task 2: Write the .typ-string and real-compile half of the gate module** - `3c09d79` (test)
3. **Task 3: Add the compiled-PDF structural half and record the GATE-01 RED evidence** -
   `c4ee821` (test)

**Plan metadata:** (this commit)

## Files Created/Modified
- `tests/fixtures/citation_render_gate/conf.py` - Single-master `typst_documents` fixture config
  documenting the citation/label unknown-node root cause.
- `tests/fixtures/citation_render_gate/index.rst` - The master document carrying eight distinct
  citing-site scenarios, a concat-protocol term, a list-item-nested citation, a 5-entry
  References run, and a 2-entry Run Break split by a real paragraph.
- `tests/fixtures/citation_render_gate/second.rst` - The cross-document counterpart defining
  `Cross2019` and the duplicate `Same2020` key, and citing `Krizhevsky2012` back into `index.rst`.
- `tests/test_citation_render_gate.py` - The 9-test render gate: `TestCitationRenderGateStructural`
  (link/namespace/separator/uncited/grid-count, no skip guard), `TestCitationRenderGateRealCompile`
  (the CIT-01 classic RED->GREEN compile test), `TestCitationRenderGateCompiledPdf`
  (layout/backref/order, compiled-PDF structural).
- `.planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-01.md` - The classic RED
  evidence file, including the independently-isolated second failure mode.

## Decisions Made
- **D-14's toctree negative control adapted to a structural include() check.** RESEARCH's probe
  described a "toctree-generated reference with `ids=[]`" negative control for the own-anchor
  guard, but that reference shape comes from Sphinx's fully-RESOLVED doctree
  (`env.get_and_resolve_doctree`), a different code path from what `visit_toctree` actually
  processes. Measured this session: `visit_toctree` reads `node['entries']` directly and raises
  `nodes.SkipNode`, so it never walks into (or calls `visit_reference` for) a toctree entry at
  all — there is no toctree-generated `reference` node in this translator's real write path to
  attach a spurious anchor to. The negative control was adapted to assert directly on the actual
  `include("second.typ")` emission line carrying no citation-style attached-anchor bracket,
  which is the observable, provable form of the same non-regression property.
- **Duplicate-key resolution direction is asserted as membership, never a specific target.** Per
  RESEARCH Pitfall 3, `index.rst`'s citing site to the duplicate `Same2020` key is asserted to
  resolve to ONE of `{index:same2020, second:same2020}`, never hard-coded to either — confirmed
  this session it resolves cross-document, to `second:same2020` (last-registered-wins).
- **The second failure mode required an isolated single-defect probe.** The full fixture's
  `index.typ` carries the classic top-level syntax fatal (References section) AND the list-item
  semantic-pass fatal (Nested Protocol section) simultaneously, but Typst's PARSER aborts on the
  first one before ever reaching the second (a semantic-pass concern). A minimal, single-construct
  probe (no References section) was built solely to independently verify and record the second,
  distinct failure shape for the evidence file.

## Deviations from Plan

None - plan executed exactly as written. The three adaptations documented above under "Decisions
Made" are scoping/implementation clarifications made explicit during execution, not deviations
from any `must_haves` truth or acceptance criterion — every acceptance criterion in the plan was
verified to pass as written (see per-task verification runs in the commit history).

## Issues Encountered

None - all fixture and test authoring proceeded as planned. The NixOS sandbox `uv run ruff`
ELF-exec hazard (documented project-wide) required symlinking `.venv/bin/ruff` to the main
checkout's patchelf'd copy before `uv run ruff check` would run in this worktree; this is
standing environment setup, not a plan deviation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plans 40-02 (sample restoration), 40-03 (the actual `visit_citation`/`depart_citation`/
  `visit_label`/`visit_reference` implementation), and 40-04 (non-regression + evidence) can
  proceed: this plan's fixture and gate module give 40-03 a concrete, non-hardcoded target to
  turn GREEN.
- `typsphinx/` remains byte-identical to the phase-start commit (`ccb37b2`) across all three of
  this plan's commits — confirmed via `git diff --stat -- typsphinx/` — so the RED captured in
  `40-GATE-EVIDENCE-01.md` is genuinely against the untouched translator.
- No blockers.

---
*Phase: 40-citations-full-round-trip*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: tests/fixtures/citation_render_gate/conf.py
- FOUND: tests/fixtures/citation_render_gate/index.rst
- FOUND: tests/fixtures/citation_render_gate/second.rst
- FOUND: tests/test_citation_render_gate.py
- FOUND: .planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-01.md
- FOUND: .planning/phases/40-citations-full-round-trip/40-01-SUMMARY.md
- FOUND commit: 02fe29f (Task 1)
- FOUND commit: 3c09d79 (Task 2)
- FOUND commit: c4ee821 (Task 3)
- FOUND commit: 1998e4f (plan metadata)

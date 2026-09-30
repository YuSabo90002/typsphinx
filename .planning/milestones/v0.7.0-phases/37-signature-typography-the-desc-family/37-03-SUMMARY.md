---
phase: 37-signature-typography-the-desc-family
plan: 03
subsystem: testing
tags: [typst, pypdf, render-gate, sphinx-python-domain, page-geometry]

# Dependency graph
requires:
  - phase: 37-signature-typography-the-desc-family
    provides: 37-EMISSION-CONTRACT.md section 10's measured widths (453.54pt column, 111-char synthetic identifier, 143pt real-corpus widest token), 37-RESEARCH.md's D-09/SIG-09 sticky-block empirical proof and Pitfall 2's corpus-non-manifestation finding
provides:
  - "tests/test_signature_overflow_render_gate.py -- SIG-07 gate (widest-unbreakable-segment vs. probe-read column width, hanging-indent presence, per-period break-opportunity count, real-corpus non-regression control, column-width sanity)"
  - "tests/test_signature_page_boundary_render_gate.py -- SIG-09 gate (per-page sentinel containment, two-page vacuous-pass guard, page-count non-inflation guard)"
  - "A proven, reusable page-height-override technique for future page-geometry render gates: insert #set page(height:, margin:) as the FIRST statement of project()'s body argument (chronologically after project()'s own set page(paper:) call), never at the top of the file"
  - "37-GATE-EVIDENCE-03.md -- SHA-anchored RED evidence, widths table, chosen page-geometry mechanism with its two justifying probes, and the RED-vs-CONTROL-GREEN node-id table plan 37-06 must flip"
affects: [37-04, 37-05, 37-06, 37-07, 37-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Typst-side context measure(...)/context layout(...) probes appended to an already-emitted, fully template-wrapped .typ, compiled via typst.compile(), read back through plain pypdf.extract_text() (never the per-glyph position-callback form) -- the geometric-assertion pattern this plan establishes for the rest of the phase"
    - "Locate two adjacent, unseparated quoted Typst string literals (desc_addname + desc_name) by anchoring on the dot-free desc_name substring and walking outward through quote characters -- survives the RED-to-GREEN transition because it only counts quotes, agnostic to text()/raw() wrapper syntax"
    - "Page-geometry override for a render-gate fixture: insert #set page(...) as the first statement of project()'s body argument, never at the top of the file (a top-of-file override is silently clobbered by project()'s own set page(paper:) call)"

key-files:
  created:
    - tests/fixtures/signature_overflow_render_gate/conf.py
    - tests/fixtures/signature_overflow_render_gate/index.rst
    - tests/test_signature_overflow_render_gate.py
    - tests/fixtures/signature_page_boundary_render_gate/conf.py
    - tests/fixtures/signature_page_boundary_render_gate/index.rst
    - tests/test_signature_page_boundary_render_gate.py
    - .planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-03.md
  modified: []

key-decisions:
  - "SIG-07's RED fixture is the exact 111-character synthetic identifier from 37-EMISSION-CONTRACT.md section 10, reused verbatim rather than constructed anew -- its widths (453.54pt column / 542.16pt as text() / 588.08pt as raw() / 121.86pt widest segment) were independently re-measured this session against the real, live fixture, not copied from the contract without re-verifying"
  - "The real-corpus control reproduces sphinx.util.parsing.nested_parse_to_nodes's actual Sphinx 9.1.0 signature verbatim (read from the installed sphinx package source), not a hand-approximation, so its 217.22pt measured width is a genuine real-corpus figure"
  - "SIG-07's primary/break-opportunity assertions extract desc_addname and desc_name as two adjacent quoted literals and treat their concatenation as one continuous run (no separator), because Sphinx's py-domain always splits a qualified name there and Typst's code-mode joins two content values on consecutive lines with zero added space -- confirmed this session that measuring only desc_addname's own literal (88 chars) misses that the run continues, unbroken, into desc_name"
  - "SIG-09's page-height override is inserted into the emitted .typ by the TEST, not declared in the fixture's conf.py/index.rst -- template_engine.py's ELEMENTS_ALLOWLIST has no page-height key, and a fixture-local custom template was heavier than the single override this gate needs"
  - "200pt/20pt was chosen as the SIG-09 short-page geometry after sweeping heights 100-300pt against the real compiled fixture; it reproduces the RED split (name+params on one page, body's first line pushed to the next) while landing on a comfortably round number"

requirements-completed: [SIG-07, SIG-09]

coverage:
  - id: D1
    description: "SIG-07 geometric acceptance gate: a synthetic over-length dotted signature must stay inside the production text column, measured via Typst's own probes, with a real-corpus non-regression control and a column-width sanity check"
    requirement: "SIG-07"
    verification:
      - kind: unit
        ref: "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_primary_widest_segment_fits_column"
        status: fail
      - kind: unit
        ref: "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_hanging_indent_present"
        status: fail
      - kind: unit
        ref: "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_break_opportunity_after_every_period"
        status: fail
    human_judgment: true
    rationale: "This plan intentionally records the RED state against the untouched translator per the phase's deliberate_red_window -- these three failures are the expected, correct outcome of this plan, not a defect to auto-pass or fail on. A human/later-plan verification step must confirm plan 37-06 flips exactly these three node ids to PASS, which is outside this plan's own scope."
  - id: D2
    description: "SIG-07 non-regression control and column-width sanity: the real Sphinx v9.1.0 doc/ corpus's worst-case qualified name fits the column, and the probe-read column width matches the measured 453.54pt production value"
    requirement: "SIG-07"
    verification:
      - kind: unit
        ref: "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_control_widest_segment_fits_column_before_and_after"
        status: pass
      - kind: unit
        ref: "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_column_width_sanity"
        status: pass
    human_judgment: false
  - id: D3
    description: "SIG-09 geometric acceptance gate: a signature and the first line of its description body must not be split across a page break, proven with a real page-break fixture and per-page pypdf containment"
    requirement: "SIG-09"
    verification:
      - kind: unit
        ref: "tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_primary_signature_and_body_share_a_page"
        status: fail
    human_judgment: true
    rationale: "This plan intentionally records the RED state against the untouched translator. A human/later-plan verification step must confirm plan 37-06 flips this node id to PASS by wrapping the signature in block(sticky: true, ...), which is outside this plan's own scope."
  - id: D4
    description: "SIG-09 guards: at least two pages exist (prevents a vacuous single-page pass) and the compiled page count does not grow beyond the pinned pre-phase baseline (Pitfall 1's block()-spacing-inflation guard)"
    requirement: "SIG-09"
    verification:
      - kind: unit
        ref: "tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_two_page_precondition_guard"
        status: pass
      - kind: unit
        ref: "tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_page_count_does_not_inflate"
        status: pass
    human_judgment: false

# Metrics
duration: ~30min
completed: 2026-08-01
status: complete
---

# Phase 37 Plan 03: SIG-07/SIG-09 Geometric Render Gates Summary

**Two Typst-probe-based geometric render gates (SIG-07 overflow, SIG-09 page-boundary), both recorded RED against the untouched translator, with a proven page-height-override technique and a real-corpus non-regression control.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-08-01 (session start)
- **Completed:** 2026-08-01T05:11:35Z
- **Tasks:** 3
- **Files modified:** 7 created, 0 modified

## Accomplishments

- Stood up `tests/test_signature_overflow_render_gate.py`: a real-compile SIG-07 gate that measures the widest ZWSP-delimited segment of a deliberately synthetic 111-character dotted identifier (reused verbatim from 37-EMISSION-CONTRACT.md section 10) against a column width read fresh from a Typst `context layout(...)` probe on every run -- three assertions (widest-segment, hanging-indent presence, per-period break-opportunity count) fail RED against the untouched translator, and two (a real-corpus non-regression control reproducing `sphinx.util.parsing.nested_parse_to_nodes` verbatim, and a column-width sanity check) pass.
- Stood up `tests/test_signature_page_boundary_render_gate.py`: a real-compile SIG-09 gate that places a signature deliberately near a page boundary under a short-page geometry and asserts, via a genuine per-page `pypdf` extraction loop, that the signature's name, parameter list, and the first line of its description body all land on the same compiled page. The primary containment assertion fails RED (name+params on page index 4, body sentinel pushed to page index 5); the two-page vacuous-pass guard and the page-count non-inflation guard both pass.
- Proved, by two real `typst.compile()` probes before committing to it, the page-height override mechanism SIG-09 needed (no existing fixture in the project overrides page geometry): a `#set page(height:, margin:)` placed at the top of the file is silently clobbered by `project()`'s own `set page(paper: papersize, ...)` call (Typst's `paper:` keyword sets width and height together), but the same override placed as the first statement of `project()`'s `body` argument -- chronologically after that call -- takes effect for the fixture's own content while the title/table-of-contents pages keep the real A4 geometry.
- Recorded `37-GATE-EVIDENCE-03.md`: the commit SHA of the untouched translator, verbatim pytest output for both gate modules, the widths table (453.54pt column / 542.16pt / 588.08pt / 121.86pt / 217.22pt), the two page-geometry probe outputs, the RED-versus-CONTROL-GREEN table by test node id naming plan `37-06` as the flip point, and an explicit SYNTHETIC-by-necessity statement for the SIG-07 RED case.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the SIG-07 overflow fixture and its Typst-measure gate, recorded RED** - `dab9a60` (test)
2. **Task 2: Create the SIG-09 page-boundary fixture and its per-page containment gate, recorded RED** - `6113429` (test)
3. **Task 3: Record the geometric RED evidence and the measurement method** - `b38d9bd` (docs)

_Note: no TDD-cycle multi-commit tasks -- each task is a single self-contained render-gate module plus its fixture, or evidence-only documentation._

## Files Created/Modified

- `tests/fixtures/signature_overflow_render_gate/conf.py` - minimal master-document Sphinx config for the SIG-07 fixture
- `tests/fixtures/signature_overflow_render_gate/index.rst` - the SYNTHETIC 111-char dotted identifier signature plus the labelled real-corpus CONTROL signature
- `tests/test_signature_overflow_render_gate.py` - the SIG-07 gate module (5 assertions: primary, hanging-indent, break-opportunity, control, column-width sanity)
- `tests/fixtures/signature_page_boundary_render_gate/conf.py` - minimal master-document Sphinx config for the SIG-09 fixture
- `tests/fixtures/signature_page_boundary_render_gate/index.rst` - filler content, a boundary signature with three sentinel tokens (name/parameter/first-body-line), and trailing filler
- `tests/test_signature_page_boundary_render_gate.py` - the SIG-09 gate module (3 assertions: two-page guard, page-count non-inflation guard, primary per-page containment)
- `.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-03.md` - this plan's RED evidence record

## Decisions Made

- Reused 37-EMISSION-CONTRACT.md section 10's exact 111-character synthetic identifier rather than constructing a new one, then independently re-measured every width against the real, live compiled fixture this session (not trusted from the contract without re-verification) -- all four figures (453.54pt / 542.16pt / 588.08pt / 121.86pt) matched exactly.
- Discovered and worked around a structural subtlety: Sphinx's `py:class::` domain parser splits a fully-qualified name into `desc_addname` (everything up to the last dot) and `desc_name` (the final segment) as two SEPARATE, unseparated `text()`/`raw()` literals -- they render as one continuous unbroken run because Typst's code-mode joins adjacent content values on consecutive lines with zero added space. The gate's extraction helper (`_extract_addname_and_name`) locates both literals via quote-boundary walking from a dot-free anchor inside `desc_name`, so it stays valid whether the pre-phase `text(...)` or the post-phase `raw(...)` primitive wraps each literal.
- Reproduced the real-corpus control's Sphinx 9.1.0 signature verbatim by reading `sphinx/util/parsing.py` from the installed `sphinx` package in this sandbox, rather than approximating it, so its measured 217.22pt width is a genuine real-corpus figure.
- Chose page-height-override mechanism (c) from Task 2's three candidates (inserting the override into the emitted `.typ` at test-compile time) over (a) a `typst_elements`/`conf.py` override (rejected: `ELEMENTS_ALLOWLIST` has no page-height key) and (b) a fixture-local custom template (rejected: heavier than necessary) -- proven correct by two real `typst.compile()` probes before being committed to the actual fixture.
- Chose 200pt/20pt as the SIG-09 fixture's page height/margin after sweeping 100-300pt against the real compiled fixture; this value reproduces the pre-phase RED split reliably and is a round, easy-to-verify number.

## Deviations from Plan

None - plan executed exactly as written. The three tasks (SIG-07 gate, SIG-09 gate, evidence file) match the plan's action blocks; no auto-fixes, no architectural questions, no scope changes.

## Issues Encountered

- **pypdf whitespace-insertion quirk (SIG-07 probe parsing).** Initial `COLWIDTH=`/`SEG{i}WIDTH=` regex matches against the probe's extracted PDF text failed because `pypdf` inserted a spurious newline between the label and its numeric value even though both render on the same visual line -- a sibling quirk to the documented U+200B spurious-emission hazard (contract section 4.2). Resolved by flattening all whitespace out of a copy of the extracted text before running the label-parsing regexes, leaving the original text (with real structure) available for any future use.
- **Page-height override placement (SIG-09).** An initial attempt located the override insertion point via the FIRST `#show: ` occurrence in the emitted `.typ`, which matched the unrelated `#show: codly-init.with()` line near the top of the file rather than the later `#show: project.with(...)` call -- the override landed before `project()`'s own `set page(paper: ...)` call and was silently clobbered (confirmed by a debug probe showing the page height unchanged at 841.89pt). Fixed by searching for `#show: ` starting from the `#import "_template.typ"` line, which reliably finds the later, correct occurrence.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both gate modules collect cleanly and are ready for plan `37-06` (Wave 3) to flip RED to GREEN by implementing D-06/D-07 (hanging-indent + ZWSP injection) and D-09/D-10 (`block(sticky: true, ...)` signature wrapper).
- `typsphinx/translator.py` is completely untouched by this plan (`git diff --stat` empty across all three task commits) -- confirmed via `git status --porcelain typsphinx/` at every commit boundary and re-verified in the final evidence file.
- `37-GATE-EVIDENCE-03.md`'s RED-versus-CONTROL-GREEN table gives plan `37-08` (the phase's evidence-merge plan) the exact node-id set to verify by set difference, per the plan's own instructions never to verify by count.
- No blockers or concerns for downstream plans in this wave (37-04, 37-05 run independently) or Wave 3 (37-06, which depends on this plan among others).

## Self-Check: PASSED

All 8 files referenced above (`tests/fixtures/signature_overflow_render_gate/{conf.py,index.rst}`,
`tests/test_signature_overflow_render_gate.py`,
`tests/fixtures/signature_page_boundary_render_gate/{conf.py,index.rst}`,
`tests/test_signature_page_boundary_render_gate.py`, `37-GATE-EVIDENCE-03.md`,
this file) were confirmed present on disk via `ls -la`. All three task
commit hashes (`dab9a60`, `6113429`, `b38d9bd`) were confirmed present via
`git log --oneline --all`. No missing items.

---
*Phase: 37-signature-typography-the-desc-family*
*Completed: 2026-08-01*

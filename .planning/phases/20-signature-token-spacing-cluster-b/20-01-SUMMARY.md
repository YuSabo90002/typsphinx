---
phase: 20-signature-token-spacing-cluster-b
plan: 01
subsystem: rendering
tags: [sphinx, typst, translator, desc_sig_space, signature-rendering, pypdf]

# Dependency graph
requires:
  - phase: 19-block-separation-fixes-cluster-a
    provides: the proven "code-mode whitespace is cosmetic-only" invariant this plan's root cause reuses at the token level, plus the standing GATE-01 real-compile fixture pattern
provides:
  - "visit_desc_sig_space/depart_desc_sig_space reduced to pass/pass, deleting the self.body.append(\" \") + raise nodes.SkipNode short-circuit"
  - "tests/test_desc_sig_space_render_gate.py — new real-compile GATE-01 render-gate for FID-07 + FID-08"
  - "tests/fixtures/desc_sig_space_render_gate/{conf.py,index.rst} — offline fixture project (py:class annotation prefix, c:function signature, inline cpp:expr)"
affects: [21-residual-fidelity-fixes-clusters-c-d-e-f]

# Tech tracking
tech-stack:
  added: []
  patterns: ["pass/pass sibling-shape idiom: a desc_sig_* handler that only carries a fixed Text child should be pass/pass so visit_Text owns emission, never hand-write self.body.append + SkipNode"]

key-files:
  created:
    - tests/test_desc_sig_space_render_gate.py
    - tests/fixtures/desc_sig_space_render_gate/conf.py
    - tests/fixtures/desc_sig_space_render_gate/index.rst
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Reused the existing visit_Text dispatch instead of writing a new space-emission helper — matches the four sibling desc_sig_* handlers (desc_sig_keyword/name/punctuation/operator), all already pass/pass."
  - "One shared fixture project covers both FID-07 (py:class annotation prefix) and FID-08 (C signature + inline cpp:expr) per the plan's discretion allowance, avoiding a duplicate fixture project."

patterns-established:
  - "pass/pass lets visit_Text own the emission: for desc_sig_element subclasses that only exist to carry a fixed Text child, prefer pass/pass over hand-writing self.body.append(...) + SkipNode."

requirements-completed: [FID-07, FID-08]

coverage:
  - id: D1
    description: "py:class/py:exception 'class '/'exception ' annotation-keyword prefix keeps its trailing space (FID-07)"
    requirement: "FID-07"
    verification:
      - kind: integration
        ref: "tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces"
        status: pass
      - kind: integration
        ref: "tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_pdf_extracted_text_has_no_merged_tokens"
        status: pass
    human_judgment: false
  - id: D2
    description: "C/C++ desc_signature and inline cpp:expr preserve every inter-token space (FID-08)"
    requirement: "FID-08"
    verification:
      - kind: integration
        ref: "tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces"
        status: pass
      - kind: integration
        ref: "tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_pdf_extracted_text_has_no_merged_tokens"
        status: pass
    human_judgment: false

# Metrics
duration: 12min
completed: 2026-07-20
status: complete
---

# Phase 20 Plan 01: Signature Token Spacing (FID-07 + FID-08) Summary

**Reduced `visit_desc_sig_space`/`depart_desc_sig_space` to `pass`/`pass`, deleting the `self.body.append(" ")` + `SkipNode` short-circuit so the node's own `Text(" ")` child streams through `visit_Text`, restoring lost intra-signature spacing for the Python `class `/`exception ` annotation prefix and every audited C/C++ inter-token space — proven by a new real-compile GATE-01 fixture with pypdf extracted-text adjacency asserts.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-20T11:20:01Z
- **Completed:** 2026-07-20T11:32:00Z
- **Tasks:** 2 completed
- **Files modified:** 4 (1 modified, 3 created)

## Accomplishments

- Deleted the buggy `self.body.append(" ")` + `raise nodes.SkipNode` short-circuit in `visit_desc_sig_space`, matching the already-`pass`/`pass` shape of the four sibling `desc_sig_*` handlers (`desc_sig_keyword`, `desc_sig_name`, `desc_sig_punctuation`, `desc_sig_operator`).
- Verified — via a real, temporary, tracked-file revert + rebuild + restore this session — that the pre-fix translator merges tokens with zero rendered space (`classsphinx.builders.html.StandaloneHTMLBuilder`, `PyObject*PyType_GenericAlloc(PyTypeObject*type, Py_ssize_tnitems)`, `a*f(a)`), and that the fix restores every one of them.
- Added `tests/test_desc_sig_space_render_gate.py` (two tests: structural `.typ` content-space asserts + real `-b typstpdf` compile + `%PDF` magic bytes; and the required pypdf extracted-text adjacency asserts) with its own offline fixture project.
- Confirmed no regression across the full fast suite (`pytest tests/ -m "not slow" -q`: 485 passed).

## Task Commits

Each task was committed atomically:

1. **Task 1: Reduce visit_desc_sig_space / depart_desc_sig_space to pass/pass (FID-07 + FID-08)** - `206aa32` (fix)
2. **Task 2: New GATE-01 render-gate fixture proving FID-07 + FID-08** - `9c4b087` (test)

**Plan metadata:** (this commit)

## Files Created/Modified

- `typsphinx/translator.py` - `visit_desc_sig_space`/`depart_desc_sig_space` reduced to `pass`/`pass`
- `tests/test_desc_sig_space_render_gate.py` - new GATE-01 render-gate (structural + real compile + pypdf adjacency)
- `tests/fixtures/desc_sig_space_render_gate/conf.py` - fixture Sphinx config (mirrors the concat-gate fixture shape)
- `tests/fixtures/desc_sig_space_render_gate/index.rst` - fixture source: `py:class` (FID-07), `c:function` (FID-08), inline `cpp:expr` (FID-08)

## Decisions Made

- Reused the existing `visit_Text` dispatch instead of writing a new space-emission helper — matches the sibling `desc_sig_*` handler shape and avoids a second, divergence-prone implementation of concat-context logic (per 20-RESEARCH.md's "Don't Hand-Roll" guidance).
- One shared fixture project (`desc_sig_space_render_gate`) covers both FID-07 and FID-08 in a single `.rst` file, per the plan's explicit discretion allowance.

## Deviations from Plan

None - plan executed exactly as written. The plan's own acceptance criteria required confirming the fixture fails pre-fix and passes post-fix; this was done via a real, temporary, tracked-file revert of `typsphinx/translator.py` to its pre-Task-1 commit, a real `-b typstpdf` rebuild + pypdf extraction (confirmed both new tests FAIL with the exact merged-token strings the plan's `must_haves.truths` describe as the bug), then restored the file to the committed fixed state (confirmed clean via `git diff --stat`).

## Issues Encountered

- The first fixture draft used an inline-literal markup form (```` ``class `` ````) with a trailing space before the closing double-backtick, which docutils rejects ("Inline literal start-string without end-string"). Fixed by dropping the trailing space inside the markup (```` ``class`` ````) — a fixture-authoring fix, not a translator change.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- FID-07 and FID-08 are proven; Phase 20's remaining scope (FID-09, `:type:`/`:default:` colon-space) is plan 20-02.
- No blockers. The version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) and `pyproject.toml` remain untouched, preserving the milestone invariant for the next plan.

---
*Phase: 20-signature-token-spacing-cluster-b*
*Completed: 2026-07-20*

## Self-Check: PASSED

All created files verified present on disk; both task commits (`206aa32`, `9c4b087`) verified present in git history.

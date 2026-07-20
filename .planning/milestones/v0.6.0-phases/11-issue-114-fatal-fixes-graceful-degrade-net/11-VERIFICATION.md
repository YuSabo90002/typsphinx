---
phase: 11-issue-114-fatal-fixes-graceful-degrade-net
verified: 2026-07-12T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: No — initial verification
---

# Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net Verification Report

**Phase Goal:** The two Issue #114 fatal bugs are fixed and the graphical out-of-scope nodes degrade
gracefully, so a real `typst.compile()` of a figure/image + graphviz fixture produces a PDF with no
`TypstError`. This unblocks real-compile validation of every downstream node handler and establishes
the per-phase real-compile acceptance-gate pattern (GATE-01).

**Verified:** 2026-07-12
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | FIG-01: px/CSS length units on figure/image `:width:`/`:height:` convert correctly (px→pt @0.75, pc→pt @12, %/em/pt/cm/mm/in passthrough, unitless→px, unknown unit warn+drop) and never leak a raw unit into Typst source | VERIFIED | `_convert_length_to_typst()` at `typsphinx/translator.py:1935`, wired into `visit_image` at `:1607-1615`. Built `tests/fixtures/figure_length_render_gate` and inspected the real generated `.typ`: `200px→150pt`, `300→225pt`, `50%`/`3em`/`2in` pass through unchanged, `1ex` case emits `image("image.png")` with **no** `width:` attribute at all (dropped). `TestFigureLengthRenderGate` (real `typst.compile()`) passes; asserts `"150pt" in typ_source` and `"200px" not in typ_source`. |
| 2 | FIG-02: a `:target:`-linked figure/image with a markup-special-char caption compiles, caption reaches `caption:` via buffer-swap, appears exactly once, no stray juxtaposed `text(...)`; both external `refuri` and internal `refid` targets work | VERIFIED | `visit_caption`/`depart_caption` buffer-swap (`typsphinx/translator.py:1263-1303`, no `astext()` call); `depart_figure` wraps caption in `{...}` code block (`:1247-1248`); `visit_reference` refid branch (`:2119-2132`) plus existing refuri branch. Built `tests/fixtures/figure_target_caption_render_gate` and inspected real `.typ`: internal target emits `link(<internal-anchor-section>, image(...))`, external emits `link("https://...", image(...))`; caption text with `_ * `` ` [ ]` intact once each. `TestFigureCaptionRenderGate` (real `typst.compile()` + pypdf) passes; asserts each sentinel token count == 1 and no `LEAK_SIGNATURES` present. |
| 3 | DEG-01/DEG-02: `graphviz` and `inheritance_diagram` degrade to a visible native-Typst placeholder + exactly one `logger.warning` each, never leaking raw DOT/diagram-spec source, never aborting the compile | VERIFIED | `_visit_graphical_placeholder()` (`typsphinx/translator.py:2663-2691`) emits `rect(text("[<label> diagram omitted]"), ...)` then `raise nodes.SkipNode`; `visit_graphviz`/`visit_inheritance_diagram` (`:2693-2699`) call it. `TestGraphvizDegradeRenderGate` (real compile) passes; asserts stderr contains each degrade warning exactly once, `"omitted"` present in extracted PDF text, `"digraph"`/`"->"` absent. |
| 4 | GATE-01: a standing real-compile acceptance gate (`sphinx-build → typst.compile() → pypdf`) exercises FIG-01/FIG-02/DEG-01/DEG-02, fails loudly on any `TypstCompilationError`, and runs (does not skip) in CI's `cov` job | VERIFIED | `tests/test_pdf_render_gate.py` extended with `TestFigureLengthRenderGate`, `TestFigureCaptionRenderGate`, `TestGraphvizDegradeRenderGate` (all `@pytest.mark.slow`, all call `typst.compile()` directly with no try/except). Confirmed `slow` marker is registered but not deselected anywhere: `pyproject.toml` `addopts = "-v --strict-markers"` (no `-m "not slow"`), `tox.ini`'s `[testenv:cov]` runs plain `pytest --cov=...` with no marker filter — so the gate runs unconditionally in CI's coverage job. Ran the gate directly: `uv run pytest tests/test_pdf_render_gate.py -q` → 4 passed (1 pre-existing admonition class + 3 new). |
| 5 | Full regression: the phase's fixes introduce zero regressions across the existing suite, and quality gates (type/lint/format) stay clean | VERIFIED | `uv run pytest -q` → 422 passed (matches SUMMARY claim exactly). `uv run black --check .` → all clean. `uv run ruff check .` → all checks passed. `uv run mypy typsphinx/` → no issues in 6 source files. |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::_convert_length_to_typst` | FIG-01 helper | VERIFIED | Present at line 1935, full docstring, regex-based allow-list dispatch matching D-02 exactly (px/unitless→pt@0.75, pc→pt@12, passthrough set, generic warn+drop fallback). |
| `typsphinx/translator.py::_visit_graphical_placeholder` / `visit_graphviz` / `visit_inheritance_diagram` | DEG-01/02 helper + overrides | VERIFIED | Present at lines 2663/2693/2697. Uses native `rect()`/`text()` (no gentle-clues), reuses module-level `logger`, raises `SkipNode`. |
| `typsphinx/translator.py::visit_caption` / `depart_caption` (buffer-swap) | FIG-02 caption fix | VERIFIED | Present at 1263/1287. No `astext()` call in the figure-caption path; buffer-swap via `self.body`/`self._saved_body_for_figure_caption`. |
| `typsphinx/translator.py::depart_figure` (code-block caption) | FIG-02 caption emission | VERIFIED | `caption: {{{self.figure_caption}}}` at line 1248 — `{...}` code block, not `[...]` markup. |
| `typsphinx/translator.py::visit_reference` (refid branch) | FIG-02 internal `:target:` | VERIFIED | Lines 2119-2132; early-return branch fires only when `refuri` empty and `refid` present; bookkeeping trio replicated correctly. |
| `tests/test_pdf_render_gate.py::TestFigureLengthRenderGate` / `TestFigureCaptionRenderGate` / `TestGraphvizDegradeRenderGate` | GATE-01 real-compile classes | VERIFIED | All present, all pass, all exercise a genuine `typst.compile()` with no try/except swallow. |
| `tests/fixtures/{figure_length,figure_target_caption,graphviz_degrade}_render_gate/` | GATE-01 fixture projects | VERIFIED | All three exist; independently built via `python -m sphinx -b typst` and inspected in this session — output matches expected D-02/D-03/D-01 behavior exactly. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `visit_image` | `_convert_length_to_typst` | width/height branches, omit attr on `None` | WIRED | Confirmed by direct code read (`:1607-1615`) and by real compile output (1ex case has no `width:` at all). |
| `depart_caption` | `self.figure_caption` / `depart_figure` | buffer-swap join + `{...}` code-block consumption | WIRED | Confirmed by code read and real compile output (caption text appears once, special chars intact, not double-emitted). |
| `visit_reference` refid branch | Typst `link(<refid>, ...)` | early-return with bookkeeping | WIRED | Confirmed via real compile: internal `:target:` figure emits `link(<internal-anchor-section>, ...)` correctly resolving to the anchored section (`visit_title`'s bracket-wrap fix supplies the matching `<label>` anchor). |
| `visit_graphviz`/`visit_inheritance_diagram` | `_visit_graphical_placeholder` | direct delegation + `SkipNode` | WIRED | Confirmed by code read and real compile (placeholder text present, DOT source absent, exactly one warning per node in subprocess stderr). |
| Three new GATE-01 test classes | `typst.compile()` / `pypdf` | direct calls, no try/except | WIRED | Confirmed by code read (`tests/test_pdf_render_gate.py`) and by running the gate: 4/4 pass for real. |

### Behavioral Spot-Checks / Real-Compile Execution

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| GATE-01 render gate (real compile) | `uv run pytest tests/test_pdf_render_gate.py -q` | 4 passed | PASS |
| Full suite regression | `uv run pytest -q` | 422 passed | PASS |
| Format | `uv run black --check .` | all clean (58 files) | PASS |
| Lint | `uv run ruff check .` | all checks passed | PASS |
| Types | `uv run mypy typsphinx/` | no issues (6 files) | PASS |
| Manual real-compile of figure-length fixture | `python -m sphinx -b typst tests/fixtures/figure_length_render_gate <tmp>` | `image("image.png", width: 150pt)` for the 200px case; `image("image.png")` (no width) for the 1ex case | PASS |
| Manual real-compile of caption/target fixture | `python -m sphinx -b typst tests/fixtures/figure_target_caption_render_gate <tmp>` | internal target → `link(<internal-anchor-section>, ...)`; external target → `link("https://...", ...)`; captions intact with special chars | PASS |

### Scope Fence Check

`git diff --stat` from the pre-phase commit (`082dc6a`) to the phase-final commit (`25d7bfc`) touches only:
`typsphinx/translator.py`, `tests/test_translator.py`, `tests/test_pdf_render_gate.py`, and three new
`tests/fixtures/*_render_gate/` directories. **No changes** to `writer.py`, `builder.py`,
`template_engine.py`, `templates/base.typ`, or any `@preview` version string — confirmed via an explicit
`git diff --stat` against those four paths (zero output). The scope fence held.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|-------------|--------------|--------|----------|
| FIG-01 | 11-01 | px/CSS length-unit conversion on figure/image `:width:`/`:height:` | SATISFIED | `_convert_length_to_typst`, real-compile fixture proof |
| FIG-02 | 11-02 | `:target:`-linked figure/image caption buffer-swap, exactly-once caption, internal+external target support | SATISFIED | buffer-swap + refid branch, real-compile fixture proof |
| DEG-01 | 11-01 | graphviz graceful-degrade placeholder | SATISFIED | `_visit_graphical_placeholder`, real-compile fixture proof |
| DEG-02 | 11-01 | inheritance_diagram graceful-degrade placeholder (shared helper) | SATISFIED | same helper, real-compile fixture proof |
| GATE-01 | 11-03 | standing real-compile acceptance gate | SATISFIED | 3 new test classes, all real-compiling, unconditional in CI |

No orphaned requirements found — `REQUIREMENTS.md`'s Phase 11 mapping (FIG-01, FIG-02, DEG-01, DEG-02,
GATE-01) matches exactly the `requirements:` fields declared across the three plans, and ROADMAP.md's
four Phase 11 success criteria all map 1:1 onto the truths verified above.

### Anti-Patterns Found

None. Scanned `typsphinx/translator.py` diff region and `tests/test_pdf_render_gate.py` for
`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and "not yet implemented"/"coming soon" phrasing — no
matches. The word "placeholder" appears only as the intentional D-01 feature name (the visible
graceful-degrade block), not a stub marker.

### Third-Bug Deviation Assessment (11-03)

The 11-03 SUMMARY records a Rule-1 auto-fixed deviation: a third fatal bug was discovered and fixed —
Typst's `<label>` anchor syntax is markup-mode-only, and every captioned figure (docutils
unconditionally assigns an id to any figure with a caption) or section-id cross-reference target
previously aborted a real `typst.compile()`. This was **not** discoverable by the pre-existing
string-level unit tests (which only assert substrings like `"figure(" in output`), and was found only
because this phase's own GATE-01 fixtures attempted a real compile — directly validating the phase's
own thesis (pitfall #9: string-agreement tests are insufficient).

Assessed as a legitimate in-scope fix:
- **Same file** (`typsphinx/translator.py`), no new dependency, no `@preview` surface touched.
- **Narrowly scoped** to the two label-emission sites (`depart_figure`, `visit_title`/`depart_title`)
  this plan's own fixtures required to compile — not a broader audit/rewrite.
- **Required** to make the phase goal true: without it, neither `TestFigureLengthRenderGate` nor
  `TestFigureCaptionRenderGate` could compile any fixture (both fixtures need captions to exercise
  FIG-01/FIG-02).
- **Verified no regression**: full suite is 422 passed (0 failures), including the pre-existing
  `test_figure_with_caption`/`test_figure_with_label`/`test_figure_without_caption` string-level tests,
  confirmed independently in this verification session (not just trusted from the SUMMARY).

The SUMMARY also flags a legitimate Phase-12 follow-up: other `<label>`-emitting call sites
(code-block `:name:` at translator.py:1056/1061, and two further sites at :2379/:2434 — likely math/
admonition labels) were not audited for the same bug class, since GATE-01's own fixtures don't exercise
them. Confirmed via `grep -n '<{.*}>\|f"<{' typsphinx/translator.py` that these sites exist and remain
unaudited. This is correctly out of scope for Phase 11 (which is bounded to FIG-01/FIG-02/DEG-01/
DEG-02/GATE-01) and is already flagged in the SUMMARY as a Phase 12/XREF-01 input — not a Phase 11 gap.
No deferred-items filtering needed since this is self-disclosed and appropriately scoped, not a missed
must-have.

### Human Verification Required

None. All must-haves were verified by direct code inspection plus independently re-run real
`typst.compile()` executions (not merely trusted from SUMMARY.md), and no truth in this phase is
behavior-dependent in a way current tests cannot reach.

### Gaps Summary

No gaps found. All 5 requirements (FIG-01, FIG-02, DEG-01, DEG-02, GATE-01) are implemented, wired, and
proven via a real `typst.compile()` — independently re-executed in this verification session, not just
read from SUMMARY.md. The full test suite (422 tests), format, lint, and type checks are all clean. The
scope fence held. The one deviation (third fatal-bug fix) was necessary, narrowly scoped, verified
regression-free, and its residual follow-up is correctly deferred to Phase 12.

---

_Verified: 2026-07-12_
_Verifier: Claude (gsd-verifier)_

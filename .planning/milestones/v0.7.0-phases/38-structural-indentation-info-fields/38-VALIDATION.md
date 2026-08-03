---
phase: 38
slug: structural-indentation-info-fields
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-01
---

# Phase 38 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `38-RESEARCH.md` § "Validation Architecture" (all figures measured 2026-08-01).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`), plus the project's own GATE-01 real-`typst.compile()` render-gate pattern |
| **Config file** | `pyproject.toml`; the render-gate pattern needs no separate config — plain pytest fixtures calling `sys.executable -m sphinx` + `typst.compile()` / `pypdf` |
| **Quick run command** | `uv run pytest tests/test_translator.py -k "desc or field" -x` |
| **Full suite command** | `uv run pytest -m "not slow"` |
| **Estimated runtime** | quick ~5s · full suite ~45s (measured at Phase 37 close: 43.24s) · `-m slow` full-corpus gate several minutes |

**Environment constraint (unchanged from Phase 37, still binding):** new fixtures MUST use the
`sys.executable -m sphinx` subprocess pattern, never `subprocess.run(["uv", "run", "sphinx-build", ...])`
— the latter hits the NixOS stub-ld hazard and false-fails. Executors running in isolated worktrees
must provision with `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` before any
test run, per `CLAUDE.md` § Worktree-isolated execution (the standing execution mode for this project).

**Measurement method (from research, re-confirmed this phase):** `pypdf`'s per-glyph position API
(`extract_text(visitor_text=...)`) remains unusable on Typst-generated PDFs in this sandbox
(returns `x=0, y=0`). Left-edge / indentation assertions must therefore be made with
`pypdf`'s `extraction_mode="layout"` text reconstruction (leading-space column counts), optionally
cross-checked with Typst-side `context measure(...)` probes. The success criteria's phrase
"measured from `pypdf` bounding boxes" is satisfied by the layout-mode reconstruction, which is the
working substitute — a plan MUST NOT attempt the `visitor_text` route.

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/test_translator.py -k "desc or field" -x`
  (fast, no `typst.compile()`)
- **After every plan wave:** `uv run pytest -m "not slow"` — includes every GATE-01 real-compile
  render gate, excludes the `@pytest.mark.slow` full-corpus gate
- **Before `/gsd-verify-work`:** `uv run pytest -m "not slow"` green, PLUS an explicit
  `uv run pytest tests/test_corpus_gate.py -m slow` full-corpus run (milestone standing practice,
  unchanged from Phase 37)
- **Max feedback latency:** ~5 seconds for the per-commit sample

---

## Phase Requirements → Sampling Map

Every IND/FLD requirement is sampled by an **observable signal**, not by "the test passes". The
signal column names what physically proves the requirement, so a degenerate implementation cannot
satisfy it.

| Req ID | Behavior | Observable signal | Test type | File | Exists? |
|--------|----------|-------------------|-----------|------|---------|
| IND-01 | `desc_content` body left edge > its own `desc_signature`'s | leading-space column count of the body line strictly exceeds the signature line's, on `extraction_mode="layout"` text of a compiled PDF | render-gate | new render-gate file (name assigned by planner) | ❌ Wave 0 |
| IND-02 | Nested member's body indented one further step than parent's body | method body column > class body column on the same compiled page | render-gate | same file | ❌ Wave 0 |
| IND-03 | Nested member's own signature aligns with parent's body, no extra step | method **signature** column == class **body** column (equality, not `>`) | render-gate | same file | ❌ Wave 0 |
| IND-04 | One shared constant drives desc/field-list/block-quote indent | repo-wide grep over `typsphinx/` finds no second independent indent literal at those sites; both emission sites emit the same named constant's value in the `.typ` | structural (grep + `.typ` substring) | translator unit test + grep assertion | ❌ Wave 0 |
| IND-05 | Depth resets across sibling `desc` (no leak) | top-level `py:function::` following a 3-level nest returns to the page-margin column | render-gate | same 3-level fixture, sibling top-level `desc` after the nest | ❌ Wave 0 |
| FLD-01 | `field_list` renders one step inside the surrounding description body | field-list line column > enclosing `desc_content` body column | render-gate | same fixture family | ❌ Wave 0 |
| FLD-02 | Multi-value → bulleted list (non-regression); single-value → inline prose | `.typ` structural: multi-value emits a `list(...)`, single-value emits no block-level `par()` wrapper; PDF text adjacency mirroring `test_confval_field_spacing_render_gate.py`'s `PINNED_SC3_STRING` pattern | unit (`.typ`) + render-gate | extends/new file | ⚠️ partial — multi-value covered indirectly; single-value needs Wave 0 |
| FLD-03 | Param name bold-mono, type italic-mono, both distinct from the proportional-bold field label | **per sub-part** assertion (D-06 binding): three separate parametrized checks, never one blanket check over the whole field body | unit (`.typ` structural, parametrized) | new parametrized test mirroring `tests/test_signature_typography_gate.py::test_sig04_*` | ❌ Wave 0 |
| D-10 (no REQ id) | Phase 37's SIG-08 duplicate-`parbreak()` suppression survives IND-01's body wrapper | `parbreak()` count in the emitted `.typ` stays at 8 (not 9) for the `SigBreakOuterClassOne`/`Two` shape | unit (`.typ` count) | extends `tests/test_signature_break_and_arrow_gate.py` | ✅ fixture exists, new assertion needed |
| Pitfall 2 (no REQ id) | `literal_emphasis` composes correctly inside `link()` when `:type:` resolves to a cross-reference | emitted `.typ` nests the mono/italic leaf inside `link(...)` and compiles | unit (`.typ`) + compile | new resolvable-`:type:` cross-reference fixture | ❌ Wave 0 |

**GATE-01 RED requirement (milestone invariant #4):** every assertion above must be recorded RED
against the **pre-phase** translator. Because `visit_desc_content` / `depart_desc_content` are
currently `pass` and the field-body defects currently compile fine, RED must come from a
**structural** assertion (indent presence / monospace primitive / inline adjacency), never from a
compile failure — same methodology as Phase 37.

---

## Per-Task Verification Map

> Seeded as `draft` by plan-phase before plan IDs exist. `/gsd-execute-phase` and
> `/gsd-validate-phase` fill task rows from the finalized `*-PLAN.md` frontmatter.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| _pending plan IDs_ | — | — | IND-01..05, FLD-01..03 | — | N/A — build-time tool, no runtime attack surface | unit + render-gate | `uv run pytest tests/test_translator.py -k "desc or field" -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] A new render-gate fixture exercising the full IND-01..05 nesting shape in **one build**
      (class → nested method → the nested method's own field list → sibling top-level function) —
      the single most valuable new fixture this phase needs; mirrors
      `tests/fixtures/signature_break_and_arrow_gate`'s "one fixture, many `class Test*RenderGate`
      cases" convention
- [ ] A parametrized FLD-03 unit test asserting bold-mono name / italic-mono type / plain-bold
      label **per sub-part**, per D-06's binding instruction (never one blanket check over the
      whole field body)
- [ ] An assertion extending `tests/test_signature_break_and_arrow_gate.py`'s existing
      `SigBreakOuterClassOne` / `SigBreakOuterClassTwo` cases to cover the post-IND-01
      `parbreak()` count (Pitfall 1) — no new fixture file needed; the fixture already contains
      both the defect shape and its non-regression control
- [ ] A resolvable-`:type:`-cross-reference fixture (Pitfall 2) — not present in any existing
      fixture; needed to prove `literal_emphasis` composes correctly inside `link()`
- [ ] A recorded exact-string census for this phase's blast radius (success criterion 5), with
      hand-derived expected strings — mirrors Phase 37's `37-TEST-CENSUS.md`

*Framework install: not required — pytest, `typst-py` 0.15.0 and `pypdf` 6.14.2 are all present.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual "the page shows structure" judgement | phase goal | Aesthetic acceptance is not reducible to a numeric assertion; the automated gates prove the *mechanics* (strict inequality / equality of columns), not that the result reads well | Build `tox -e docs-pdf` and page through the API reference section; confirm class→method membership is recoverable at a glance and field lists do not visually detach from their parent |

*All requirement-level behaviors (IND-01..05, FLD-01..03) have automated verification; the row
above is a goal-level aesthetic check only and blocks nothing.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s for the per-commit sample
- [ ] Every assertion recorded RED against the pre-phase translator (GATE-01)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---
phase: 37
slug: signature-typography-the-desc-family
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-01
---

# Phase 37 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `37-RESEARCH.md` § "Validation Architecture" (all figures measured 2026-08-01).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`), plus the project's own GATE-01 real-`typst.compile()` render-gate pattern |
| **Config file** | `pyproject.toml`; the render-gate pattern needs no separate config — plain pytest fixtures calling `sys.executable -m sphinx` + `typst.compile()`, e.g. `tests/test_pdf_render_gate.py::_run_sphinx_build_typst` |
| **Quick run command** | `uv run pytest tests/test_translator.py -k "desc or signature" -x` |
| **Full suite command** | `uv run pytest -m "not slow"` |
| **Estimated runtime** | quick ~5s · full suite ~90s · `-m slow` full-corpus gate several minutes |

**Environment constraint (non-negotiable):** new fixtures MUST use the `sys.executable -m sphinx`
pattern, never `subprocess.run(["uv", "run", "sphinx-build", ...])` — the latter hits the NixOS
stub-ld hazard and false-fails. Executors running in isolated worktrees must provision with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and then
`for t in uv ruff; do ln -sf "$(command -v $t)" ".venv/bin/$t"; done` before any test run.

**Measurement method (from research):** `pypdf`'s `extract_text(visitor_text=...)` was found
unreliable for per-glyph x/y positions on Typst-generated PDFs in this sandbox (returns `x=0, y=0`).
Geometric assertions must use Typst-side `context measure(...)` / `context layout(size => ...)`
probes compiled through `typst.compile()`, cross-checked with plain `pypdf.extract_text()` for
content and ordering. Available production column width, measured this way: **453.54pt**.

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/test_translator.py -k "desc or signature" -x`
  (fast, no `typst.compile()`)
- **After every plan wave:** `uv run pytest -m "not slow"` — includes every GATE-01 real-compile
  render gate, excludes the `@pytest.mark.slow` full-corpus gate
- **Before `/gsd-verify-work`:** `uv run pytest -m "not slow"` green, PLUS an explicit
  `uv run pytest tests/test_corpus_gate.py -m slow` full-corpus run (milestone standing practice)
- **Max feedback latency:** ~5 seconds for the per-commit sample

---

## Phase Requirements → Sampling Map

Every SIG requirement is sampled by an **observable signal**, not by "the test passes". The signal
column names what physically proves the requirement, so a degenerate implementation cannot satisfy it.

| Req ID | Behavior | Observable signal | Test type | File | Exists? |
|--------|----------|-------------------|-----------|------|---------|
| SIG-01 | `desc_name` emits `strong(raw(...))` | emitted `.typ` contains `strong(raw(` at the name site — structural, not a `text(...)` match | unit + render-gate | `tests/test_translator.py::test_desc_with_annotation_and_name` | ✅ needs rewrite |
| SIG-02 | `desc_addname` emits `raw(...)` with **no** enclosing `strong()` | emitted `.typ`: addname site is `raw(` and is not inside `strong(` | unit + render-gate | `tests/test_translator.py` (new case) | ❌ Wave 0 |
| SIG-03 | `desc_annotation` emits the **same** `strong(raw(...))` as `desc_name` | emitted `.typ`: annotation and name sites are byte-identical in wrapper shape | unit + render-gate | rewritten `test_desc_with_annotation_and_name` | ✅ needs rewrite |
| SIG-04 | Per-sub-part distinct treatment inside `desc_parameter` (D-03: per sub-part, **never** one blanket check) | emitted `.typ`: param name → `emph(raw(`; type annotation and default → `raw(` without `emph` | unit, parametrized over all 8 measured parameter shapes | new parametrized test | ❌ Wave 0 |
| SIG-05 | Delimiters `(` `)` `,` `=` `:` and `desc_optional`'s `[` `]` emit `raw(...)` | emitted `.typ`: each delimiter site is a `raw(` call, no bare `text(` remains in the parameter list | unit + render-gate | rewritten `test_desc_parameterlist` + new `desc_optional` case | ⚠️ partial |
| SIG-06 | `desc_returns` emits a real arrow glyph | compiled-PDF `pypdf` text: `'→' in text` **and** `'->' not in text` anywhere in signature output | render-gate (compiled PDF) | `tests/test_pdf_render_gate.py::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` | ✅ needs rewrite |
| SIG-07 | Long dotted signature stays inside the right text margin | Typst `context measure(...)` width of the widest unbroken token < 453.54pt column width, on a **synthetic ~90+ char identifier** fixture; real-corpus worst case (311-char sig / 41-char qualname / 143pt token) as a non-regression control | new render-gate | `tests/test_signature_overflow_render_gate.py` | ❌ Wave 0 |
| SIG-08 | Exactly one break between sibling signatures and around nested `desc` | emitted `.typ`: `output.count("parbreak()")` equals the hand-derived expected count for a `py:class::` + nested `py:method::` fixture | render-gate + structural `.typ` assertion | extends `tests/test_desc_bodyless_concat_render_gate.py` pattern | ❌ Wave 0 |
| SIG-09 | Signature + parameter list + first body line share a page | `pypdf` **per-page** text containment under a forced page-break fixture (`#set page(height:, margin:)` + `block(sticky:)`) | render-gate (compiled PDF, per-page) | `tests/test_signature_page_boundary_render_gate.py` | ❌ Wave 0 |
| D-11 (no SIG id) | Optional-group separator lands **inside** the bracket, matching Sphinx HTML `[timeout, ]` | emitted `.typ` and compiled-PDF text both show `[timeout, ]**kwargs`, not `[timeout]**kwargs`; expressions explicitly `+`-joined | unit + render-gate | own fixture (must NOT be smuggled into a SIG-05 assertion) | ❌ Wave 0 |

**GATE-01 RED requirement (milestone invariant #4):** every assertion above must be recorded RED
against the pre-phase translator. Because the current output *compiles fine*, RED must come from a
**structural** assertion (monospace primitive present / `text(` absent / break count / glyph identity
/ page containment), never from a compile failure.

**SC#5 binding constraint:** expected strings are **hand-derived**. Copying whatever the new code
emits into a golden file is forbidden by milestone invariant #4 and voids the phase's evidence.

---

## Per-Task Verification Map

*Populated once PLAN.md files exist — plan-phase seeds this file before task IDs are assigned.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| *TBD* | — | — | SIG-01..09 | — (no new threat surface) | N/A | unit / render-gate | see map above | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_signature_overflow_render_gate.py` — SIG-07 (synthetic overflow RED fixture plus
      the real-corpus non-regression control; research Pitfall 2 established that the real corpus does
      **not** overflow at production width, so the corpus alone cannot produce RED)
- [ ] `tests/test_signature_page_boundary_render_gate.py` — SIG-09 (forced page-break fixture using
      the `#set page(height:, margin:)` + `block(sticky:)` pattern proven this session)
- [ ] A parametrized `desc_parameter` sub-part unit test covering all **8** parameter shapes measured
      in RESEARCH.md's D-05 table (SIG-04) — no existing test covers the union-type, resolved-xref, or
      quoted-forward-ref cases
- [ ] A nested-`desc` fixture in the `test_desc_bodyless_concat_render_gate.py` style proving SIG-08's
      "exactly one break" for `py:class::` + `py:method::` nesting (the existing fixture covers
      body-less *sibling* desc, not *nested* desc)
- [ ] A D-11 optional-group-separator fixture, separate from any SIG-05 assertion

*Framework install: not required — pytest, `typst-py` 0.15.0 and `pypdf` 6.14.2 are all present.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual confirmation that `block()`'s non-spacing cosmetic defaults (`inset`, `fill`, `stroke`) introduce no visible artifact | D-10 / Assumption A2 | Automated assertions cover spacing (measured) and page containment, but not "does it look wrong" | Build the phase's own GATE-01 fixture to PDF and eyeball the signature block against the pre-phase render |

*Every other phase behavior has automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all ❌ references above
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s for the per-commit sample
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---
phase: 12
slug: high-volume-independent-node-handlers
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-12
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (config in `pyproject.toml`; `sphinx.testing.fixtures` plugin) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `pytest -m "not slow"` |
| **Full suite command** | `pytest` (includes the `slow`-marked real-compile render gate) |
| **Estimated runtime** | ~seconds for `not slow`; ~1–2 min including the `slow` real-`typst.compile()` gate |

---

## Sampling Rate

- **After every task commit:** Run `pytest -m "not slow"` on the touched test module(s) (`pytest tests/test_translator.py -m "not slow"`)
- **After every plan wave:** Run `pytest` (full suite, including `tests/test_pdf_render_gate.py`)
- **Before `/gsd-verify-work`:** Full suite green, including the real-compile render gate (must NOT skip when `typst`/`pypdf` present)
- **Max feedback latency:** ~120 seconds (full suite with real compile)

---

## Validation Architecture (Nyquist)

The phase thesis (research pitfall #9) is that **string-agreement unit tests alone are insufficient** — the translator can emit syntactically plausible Typst that still aborts a real `typst.compile()`. Phase 12 research proved this concretely: a `:term:` cross-reference currently emits `link(<term-Widget>)` to an anchor that `visit_term` never attached, and the whole PDF compile aborts with `TypstError: label <term-Widget> does not exist`. String tests would never catch that. The standing real-compile gate (GATE-01, `tests/test_pdf_render_gate.py`) is the Nyquist sampling instrument for every handler group.

- **Sample:** `sphinx-build → typst.compile() → pypdf` text extraction, driven by fixtures covering every success-criteria case across the four handler groups:
  - **VER-01** — `versionadded` / `versionchanged` / `deprecated` / `versionremoved` render as unboxed italic label + body with Sphinx's own wording ("Added in version …:"), and the doc compiles.
  - **XREF-01** — a fixture exercising **both** a resolving section-anchor ref **and** a `:term:` ref that resolve to emitted anchors, producing working PDF links with **no fatal** and no `link("", …)`.
  - **DESC-01…04** — a `-> int` return arrow, a multi-line signature (real `linebreak()`, not source `\n`), nested `desc_optional` brackets (`printf(fmt[, args])`), and an inline `:cpp:expr:` fragment **without** the standalone-declaration `strong()` wrapper.
  - **BLK-01/04/05/06** — a `----` transition (horizontal rule), a `.. glossary::` (definition-list pass-through), a `.. tabularcolumns::` (skipped, no leak), and an `:abbr:` (`term (expansion)`).
- **Positive assertions:** version label wording present; term/section links resolve (compile succeeds); return arrow / line break / bracket nesting present; `abbr` expansion present exactly where expected.
- **Negative-control leak signatures:** raw `.. tabularcolumns::` column-spec content **absent** from extracted PDF text; no `link("", …)`; no gentle-clues box wording around the version label; no standalone `strong()` around the inline `:cpp:expr:` fragment.
- **Loud failure:** any `TypstCompilationError` fails the gate (never swallowed/skipped in CI's `cov` job where `typst-py`/`pypdf` are installed). The `:term:` fixture is the critical must-fail-until-fixed case.

---

## Per-Task Verification Map

> Populated by the planner/executor once PLAN.md tasks exist. Each task maps to a `not slow` unit assertion and/or the `slow` real-compile render gate.

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| _TBD by planner_ | — | — | VER-01 | unit + real-compile | `pytest tests/test_translator.py`, `pytest tests/test_pdf_render_gate.py` | ✅ existing | ⬜ pending |
| _TBD by planner_ | — | — | XREF-01 (incl. `:term:` anchor fix) | unit + real-compile | `pytest tests/test_pdf_render_gate.py` | ✅ existing | ⬜ pending |
| _TBD by planner_ | — | — | DESC-01 / DESC-02 / DESC-03 / DESC-04 | unit + real-compile | `pytest tests/test_translator.py`, `pytest tests/test_pdf_render_gate.py` | ✅ existing | ⬜ pending |
| _TBD by planner_ | — | — | BLK-01 / BLK-04 / BLK-05 / BLK-06 | unit + real-compile | `pytest tests/test_translator.py`, `pytest tests/test_pdf_render_gate.py` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements: `pytest` + `sphinx.testing.fixtures` are installed, `tests/test_pdf_render_gate.py` already exists (extended per handler group), and `typst`/`pypdf` are present in the CI `cov`/`docs-pdf` jobs. No new framework install needed.

---

## Manual-Only Verifications

*All phase behaviors have automated verification via unit tests + the real-compile render gate. None require manual verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (none — existing infra)
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

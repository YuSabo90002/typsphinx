---
phase: 11
slug: issue-114-fatal-fixes-graceful-degrade-net
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-12
---

# Phase 11 — Validation Strategy

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

The phase thesis (research pitfall #9) is that **string-agreement unit tests alone are insufficient** — a translator can emit syntactically plausible Typst that still fails a real `typst.compile()`. The standing real-compile gate (GATE-01) is the Nyquist sampling instrument:

- **Sample:** `sphinx-build → typst.compile() → pypdf` text extraction, driven by fixtures covering every success-criteria case (px/`50%`/`3em`/unitless/`2in`/unknown-unit; `:target:` external+internal captions with `_ * ` `` ` `` ` [ ]`; graphviz + inheritance_diagram degradation).
- **Positive assertions:** caption text present **exactly once** (guards double-emission); converted lengths compile (px→pt, valid units pass, unknown dropped).
- **Negative-control leak signatures:** raw `width: 200px`, raw DOT source, stray juxtaposed `text(...)` — asserting these tokens are **absent** from the extracted PDF text.
- **Loud failure:** any `TypstCompilationError` fails the gate (never swallowed/skipped in CI's `cov` job where `typst-py`/`pypdf` are installed).

---

## Per-Task Verification Map

> Populated by the planner/executor once PLAN.md tasks exist. Each task maps to a `not slow` unit assertion and/or the `slow` real-compile render gate.

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| _TBD by planner_ | — | — | FIG-01 / FIG-02 / DEG-01 / DEG-02 / GATE-01 | unit + real-compile | `pytest tests/test_translator.py`, `pytest tests/test_pdf_render_gate.py` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements: `pytest` + `sphinx.testing.fixtures` are installed, `tests/test_pdf_render_gate.py` already exists (extended for GATE-01), and `typst`/`pypdf` are present in the CI `cov`/`docs-pdf` jobs. No new framework install needed.

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

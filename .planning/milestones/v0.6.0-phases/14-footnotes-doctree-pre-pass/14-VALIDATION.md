---
phase: 14
slug: footnotes-doctree-pre-pass
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-12
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `14-RESEARCH.md` § Validation Architecture. The empirical bar is a real
> `typst.compile()` outcome (GATE-01 standing pattern), never string-agreement asserts alone.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`); `typst-py` + `pypdf` for the real-compile gate |
| **Config file** | `pyproject.toml` (pytest config, markers incl. `slow`); no dedicated config beyond `tests/test_pdf_render_gate.py` |
| **Quick run command** | `pytest tests/test_footnotes.py -x` |
| **Full suite command** | `pytest --cov=typsphinx --cov-report=term-missing` |
| **Estimated runtime** | ~2–5 s unit; render gate slower (real compile), marked `@pytest.mark.slow` |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_footnotes.py -x`
- **After every plan wave:** Run `pytest --cov=typsphinx --cov-report=term-missing`
- **Before `/gsd-verify-work`:** Full suite green, including the new `TestFootnoteRenderGate` class
- **Max feedback latency:** ~5 seconds (unit tier)

---

## Per-Task Verification Map

Task IDs are assigned by the planner; this map keys each FN-01 behavior to its automated proof.

| Behavior | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|----------|------|-------------|-----------|-------------------|-------------|--------|
| `visit_document` builds `{id: footnote_node}` pre-pass index (D-01) | 1 | FN-01 | unit | `pytest tests/test_footnotes.py -k index -x` | ❌ W0 | ⬜ pending |
| `visit_footnote` raises `SkipNode`, emits nothing at definition location (D-05) | 1 | FN-01 | unit | `pytest tests/test_footnotes.py -k skip -x` | ❌ W0 | ⬜ pending |
| First `footnote_reference` emits `[#footnote({...}) <fn-id>]`, skips leading `label` child (D-02/D-03/D-06) | 1 | FN-01 | unit | `pytest tests/test_footnotes.py -k definition -x` | ❌ W0 | ⬜ pending |
| Repeat `footnote_reference` emits bare `footnote(<fn-id>)`, no body dup (D-03) | 1 | FN-01 | unit | `pytest tests/test_footnotes.py -k reuse -x` | ❌ W0 | ⬜ pending |
| Dangling `refid` logs a warning and skips, never fatal (D-08) | 1 | FN-01 | unit | `pytest tests/test_footnotes.py -k dangling -x` | ❌ W0 | ⬜ pending |
| SC#1 real-compile: single-ref — body appears exactly once, no floating body | 1 | FN-01 | integration (GATE-01) | `pytest tests/test_pdf_render_gate.py -k FootnoteSingle -x` | ❌ W0 | ⬜ pending |
| SC#2 real-compile: double-ref — marker at both sites, body sentinel `.count(...) == 1` | 1 | FN-01 | integration (GATE-01) | `pytest tests/test_pdf_render_gate.py -k FootnoteDouble -x` | ❌ W0 | ⬜ pending |
| SC#3 real-compile: body with `emph`/`literal` + markup-special chars, via buffer-swap | 1 | FN-01 | integration (GATE-01) | `pytest tests/test_pdf_render_gate.py -k FootnoteMarkup -x` | ❌ W0 | ⬜ pending |
| SC#4 real-compile: footnote-inside-a-list-item compiles cleanly | 1 | FN-01 | integration (GATE-01) | `pytest tests/test_pdf_render_gate.py -k FootnoteListItem -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_footnotes.py` — new unit-test module (precedent: `test_topics.py`, `test_line_blocks.py`) for the branch logic: pre-pass index population, `SkipNode` on `visit_footnote`, definition-vs-reuse branch selection via the `set()`, D-08 warn+skip path.
- [ ] `tests/fixtures/footnote_render_gate/` (`conf.py` + `index.rst`) — one fixture project combining a footnote cited once (SC#1), cited twice (SC#2), a body with `*emphasis*`/`` `literal` `` and markup-special chars (SC#3), and a footnote cited from inside a bullet-list item (SC#4). This exact shape combination was verified to compile cleanly in the research session.
- [ ] `tests/test_pdf_render_gate.py` — new `TestFootnoteRenderGate` class following the `TestTopicLineBlockRenderGate` class-scoped-fixture pattern (build+compile once, thin methods per SC), with sentinel-presence + `.count(...) == 1` body-sentinel asserts (guards double-emission) + `LEAK_SIGNATURES` negative-control asserts (guards against raw `text(`/`par({`/`raw("` leaking as prose). Marked `@pytest.mark.slow` and `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), ...)` matching every existing GATE-01 class.
- [ ] Framework install: **none** — pytest, typst-py, pypdf, docutils, sphinx are already installed and exercised by the existing suite.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All phase behaviors have automated verification (unit + real-compile GATE-01).*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`test_footnotes.py`, fixture dir, `TestFootnoteRenderGate`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s (unit tier)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

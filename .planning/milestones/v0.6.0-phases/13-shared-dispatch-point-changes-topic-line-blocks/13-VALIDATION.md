---
phase: 13
slug: shared-dispatch-point-changes-topic-line-blocks
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-12
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `13-RESEARCH.md` § Validation Architecture (empirically verified via a real
> `sphinx-build → typst.compile() → pypdf` pipeline).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`); `typst-py` + `pypdf` for the GATE-01 real-compile gate |
| **Config file** | `pyproject.toml` (pytest config); render gate self-contained in `tests/test_pdf_render_gate.py` |
| **Quick run command** | `pytest tests/test_translator.py -k "topic or line_block or admonition" -x` |
| **Full suite command** | `pytest --cov=typsphinx --cov-report=term-missing` |
| **Estimated runtime** | quick ~a few seconds; full suite dominated by the `@pytest.mark.slow` real-compile gate |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_translator.py -k "topic or line_block or admonition" -x`
- **After every plan wave:** Run `pytest --cov=typsphinx --cov-report=term-missing`
- **Before `/gsd-verify-work`:** Full suite green, including the new `TestTopicLineBlockRenderGate`
  class (marked `@pytest.mark.slow` + `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), …)`)
- **Max feedback latency:** quick-tier under ~10s; full render gate acceptable per phase gate only

---

## Per-Task Verification Map

Task IDs are assigned by the planner; the requirement→test mapping below is the empirically-verified
contract each task must satisfy. Real-compile rows are the GATE-01 empirical bar (string-agreement
asserts alone never suffice).

| Req | Behavior | Test Type | Automated Command | File Exists | Status |
|-----|----------|-----------|-------------------|-------------|--------|
| BLK-02 | `.. topic::` renders as `clue({…}, title: {…})`, not `heading()` | unit | `pytest tests/test_translator.py -k topic -x` | ❌ W0 | ⬜ pending |
| BLK-02 | `.. contents::` renders box-less, `bullet_list` intact, no boxed TOC | unit | `pytest tests/test_translator.py -k contents -x` | ❌ W0 | ⬜ pending |
| BLK-02 | Real-compile: topic title appears exactly once (not duplicated into the auto-outline); TOC structure unchanged | integration (GATE-01) | `pytest tests/test_pdf_render_gate.py -k Topic -x` | ❌ W0 | ⬜ pending |
| BLK-03 | `line`/`line_block` emits `linebreak()` per line, `h()` per nesting depth | unit | `pytest tests/test_translator.py -k line_block -x` | ❌ W0 | ⬜ pending |
| BLK-03 | Real-compile: address + poem sentinels appear as separate extracted-text lines, never concatenated | integration (GATE-01) | `pytest tests/test_pdf_render_gate.py -k LineBlock -x` | ❌ W0 | ⬜ pending |
| SC#3 (regression) | `.. note::`/`.. warning::`/generic `.. admonition:: Custom *Title*` (multi-child title, per Pitfall 1) still render correctly, no level-0-heading fatal | integration (GATE-01) | `pytest tests/test_pdf_render_gate.py -k AdmonitionTitleRegression -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/topic_line_block_render_gate/` (`conf.py` + `index.rst`) — combined fixture project:
      a `.. topic::` with a **multi-child title** (proves Pitfall 1's fix), a `.. contents::` local TOC,
      a plain top-level `line_block` for "address", a plain nested `line_block` for "poem"
      (do **NOT** use `.. epigraph::` — Pitfall 4), and a `.. note::`/`.. warning::`/`.. admonition:: Custom *Title*`
      regression block. This exact RST was verified to compile cleanly during research.
- [ ] `tests/test_pdf_render_gate.py` — new `TestTopicLineBlockRenderGate` class following the
      `TestTrivialBlocksRenderGate`/`TestDescSignatureRenderGate` pattern: `sphinx-build -b typst` →
      `typst.compile()` (uncaught) → `pypdf` text-extraction → sentinel-presence + sentinel-count
      (`== 1` for topic/contents titles) + `LEAK_SIGNATURES` negative-control assertions.
- [ ] Unit tests in `tests/test_translator.py` (or new `tests/test_topics.py`/`tests/test_line_blocks.py`)
      for D-02's buffer-swap condition, D-05's class-detection, D-06's clamp, and Pitfall 1's multi-child
      title path (DESC-02/VER-01 unit-test precedent).
- [ ] Framework install: **none** — pytest, typst-py, pypdf already installed and exercised.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All phase behaviors have automated verification (unit + GATE-01 real-compile).*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < ~10s (quick tier)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

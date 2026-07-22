---
phase: 19
slug: block-separation-fixes-cluster-a
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-20
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `19-RESEARCH.md` §"Validation Architecture" (HIGH confidence — every
> fix and every gate command in that section was run against a real Typst compile
> and the cached ~684-page Sphinx corpus this research session).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (config in `pyproject.toml` `[tool.pytest.ini_options]`) |
| **Config file** | `pyproject.toml` (testpaths=`tests`, markers `slow`/`integration`, `--strict-markers`) |
| **Quick run command** | `uv run pytest tests/test_translator.py tests/test_paragraph_concat_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_rubric_option_concat_render_gate.py tests/test_deflist_term_concat_render_gate.py tests/test_desc_bodyless_concat_render_gate.py -q` |
| **Full suite command** | `uv run pytest -q` (includes the corpus gate; ~14s with corpus cache warm) |
| **Estimated runtime** | render-gate modules < 1s combined; full corpus gate ~14s (cache warm) |

*NixOS-sandbox note: invoke Sphinx via `sys.executable -m sphinx` (never `uv run sphinx-build`); `uv run pytest` / `uv run python3 -m sphinx` module-invocation forms work and were used this research session.*

---

## Sampling Rate

- **After every task commit:** Run the specific finding's render-gate test (`uv run pytest tests/test_<finding>_render_gate.py -x`) — each < 1s.
- **After every plan wave:** Run all render-gate modules for findings completed so far **plus** `tests/test_translator.py` (catches non-render structural regressions the PDF-level assert may not surface).
- **Phase gate (before `/gsd-verify-work`):** `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` must be green (~14s cache warm) — required given F1's corpus-wide blast radius, not optional.
- **Max feedback latency:** ~15 seconds (worst case = full corpus gate).

---

## Per-Task Verification Map

> Task IDs are assigned by the planner (PLAN.md). Rows below are the requirement→test
> contract each task covering that requirement must satisfy (GATE-01: structural `.typ`
> token assert that FAILS pre-fix + real `typst.compile()` producing a valid `%PDF`).

| Requirement | Finding | Test Type | Automated Command | File Exists | Status |
|-------------|---------|-----------|-------------------|-------------|--------|
| FID-02 | F1 — consecutive paragraphs in a `list_item` render `parbreak()`-separated | render-gate (GATE-01) | `uv run pytest tests/test_paragraph_concat_render_gate.py -x` | ❌ W0 (new module) | ⬜ pending |
| FID-03 | F7 — sibling `desc_signature`s render `linebreak()`-separated | render-gate (GATE-01), extend existing | `uv run pytest tests/test_desc_signature_concat_render_gate.py -x` | ✅ exists (add test method + fixture variant) | ⬜ pending |
| FID-04 | F13 — rubric-then-option/field renders `linebreak()`-separated | render-gate (GATE-01) | `uv run pytest tests/test_rubric_option_concat_render_gate.py -x` | ❌ W0 (new module) | ⬜ pending |
| FID-05 | F14 — `terms()` emits `separator: linebreak()`; term/definition on separate lines (both sub-cases) | render-gate (GATE-01), extend existing | `uv run pytest tests/test_deflist_term_concat_render_gate.py -x` | ✅ exists (add 2 test methods) | ⬜ pending |
| FID-06 | F15 — back-to-back body-less confvals render `parbreak()`-separated | render-gate (GATE-01) | `uv run pytest tests/test_desc_bodyless_concat_render_gate.py -x` | ❌ W0 (new module) | ⬜ pending |
| all 5 (non-regression) | Full ~684-page corpus still compiles fatal-free, no new `unknown_visit` | full-corpus regression | `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` | ✅ exists (13.88s pre-fix; MUST stay green post-fix) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_paragraph_concat_render_gate.py` + `tests/fixtures/paragraph_concat_render_gate/{conf.py,index.rst}` — FID-02. Fixture: a bullet item with 2+ paragraphs (mirror `usage/referencing.rst` "Suppressed link:" item).
- [ ] `tests/test_rubric_option_concat_render_gate.py` + `tests/fixtures/rubric_option_concat_render_gate/{conf.py,index.rst}` — FID-04. Fixture: a `.. rubric::` immediately followed by `.. option::` (mirror `man/sphinx-quickstart.rst` "Structure Options"/`--sep`; plain `.rst` project, no `man` builder needed).
- [ ] `tests/test_desc_bodyless_concat_render_gate.py` + `tests/fixtures/desc_bodyless_concat_render_gate/{conf.py,index.rst}` — FID-06. Fixture: 2+ back-to-back `.. confval::` with only `:type:`/`:default:` fields, no body paragraph.
- [ ] Extend `tests/test_desc_signature_concat_render_gate.py` with a new fixture/test method for FID-03 (multiple sibling signatures under one directive — e.g. `.. py:function::` with two signature lines; no intersphinx needed).
- [ ] Extend `tests/test_deflist_term_concat_render_gate.py` with two new fixture/test methods for FID-05: (a) a definition list nested inside a bullet `list_item`; (b) a definition list term whose definition opens with a nested field/definition list.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All phase behaviors have automated verification (structural `.typ` assert + real `%PDF` compile per finding, plus the full-corpus non-regression gate). Paragraph vertical spacing (FID-02) is asserted structurally via the emitted `parbreak()` token — the research notes rasterized glyph-position checks were rejected for this milestone (D-06).*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (5 render-gate modules: 3 new, 2 extended)
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

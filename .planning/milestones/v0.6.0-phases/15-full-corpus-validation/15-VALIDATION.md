---
phase: 15
slug: full-corpus-validation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-12
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `15-RESEARCH.md` §"Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ (`pyproject.toml` `dev` extras, `>=8.4,<10`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` — existing `slow` marker already registered (no new marker) |
| **Quick run command** | `pytest -m "not slow"` (existing fast suite — must stay green; this phase adds no code the fast suite exercises) |
| **Full suite command** | `pytest tests/test_corpus_gate.py -m slow -v` (new module; requires network + the real Sphinx `doc/` corpus, run OUTSIDE the NixOS sandbox) |
| **Estimated runtime** | ~fast suite unchanged; corpus `slow` test ~minutes (clone + full-corpus build + compile) |

---

## Sampling Rate

- **After every task commit:** Run `pytest -m "not slow"` — the phase must not regress the fast suite.
- **After every plan wave:** Run `pytest tests/test_corpus_gate.py -m slow -v` at least once (network + time required) to confirm SC#1 genuinely passes against the real corpus, not merely that the code is well-formed.
- **Before `/gsd-verify-work`:** Fast suite green AND the `slow` corpus test passing AND `15-CORPUS-REPORT.md` present with concrete numbers (not placeholders).
- **Max feedback latency:** fast suite seconds; corpus gate on-demand (excluded from CI by `-m "not slow"`, D-04).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 15-01-* | 01 | 1 | GATE-02 (SC#1) | — | subprocess list-arg form only, never `shell=True` | integration (`slow`) | `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v` | ❌ W0 — new file | ⬜ pending |
| 15-0X-* | — | — | GATE-02 (SC#2) | — | N/A | integration (`slow`) side-effect | same build's captured stderr → `15-CORPUS-REPORT.md` | ❌ W0 | ⬜ pending |
| 15-0X-* | — | — | GATE-02 (SC#3) | — | N/A | one-time/report (D-06) | before/after `-b typst` diff → `15-CORPUS-REPORT.md` | ❌ W0 | ⬜ pending |

*Concrete task IDs are assigned by the planner; this map is refined during execution.*
*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_corpus_gate.py` — new module; covers GATE-02 SC#1/SC#2/SC#3 (NOT appended to `test_pdf_render_gate.py` — see RESEARCH Pitfall 5)
- [ ] Corpus clone/cache helper (`get_or_clone_corpus`-style) — new; shallow clone at tag `f"v{sphinx.__version__}"`, cached temp dir, `pytest.skip` on no-network/clone-failure (D-01/D-05)
- [ ] `conf.py` augmentation helper (`wire_typsphinx_into_corpus_conf`-style) — append `extensions.append("typsphinx")` + `typst_documents` (real conf, D-03)
- [ ] D-07 `git worktree` before/after helper — reverse-apply `79c9d45` on `depart_term` only; build both with `-b typst` (translate-only, avoids the glossary fatal)
- [ ] `15-CORPUS-REPORT.md` — new, phase-completion artifact (D-06): frequency-ranked `unknown_visit` catalogue + empty-URL before/after numbers
- Framework install: none — `pytest`/`slow` marker already fully set up; no `tox.ini`/CI changes needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Corpus build against real Sphinx `doc/` | GATE-02 | Requires live network egress + the full non-sandbox environment (the NixOS sandbox fails `uv run` of compiled binaries; the `slow` test `pytest.skip`s there) | Run `pytest tests/test_corpus_gate.py -m slow -v` outside the sandbox with network access; confirm no `TypstCompilationError`, PDF `%PDF` magic present, and report numbers populated |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency acceptable (fast suite seconds; corpus gate on-demand by design)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

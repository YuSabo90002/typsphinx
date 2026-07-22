---
phase: 20
slug: signature-token-spacing-cluster-b
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-20
---

# Phase 20 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from RESEARCH.md `## Validation Architecture` (nyquist enabled). The
> per-task verification map is finalized against the PLAN.md `<verify>` blocks by
> `/gsd-validate-phase`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (config in `pyproject.toml`) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `pytest tests/test_desc_signature_concat_render_gate.py tests/test_field_list_in_list_item_render_gate.py` |
| **Full suite command** | `pytest` (includes GATE-01 render gates); `pytest -m slow tests/test_corpus_gate.py` for the ~684-page corpus regression |
| **Estimated runtime** | ~30–60 s quick gates; corpus gate (slow) minutes |

> **NixOS sandbox hazard:** render-gate fixtures invoke Sphinx as `sys.executable -m sphinx`, **never** `uv run`. `pypdf` is confirmed already a dev dependency in `pyproject.toml` (no new dep required for the D-07 adjacency assert).

---

## Sampling Rate

- **After every task commit:** Run the quick gate for the touched finding (e.g. `pytest tests/test_desc_signature_concat_render_gate.py -q`)
- **After every plan wave:** Run `pytest` (full render-gate suite) + `pytest -m slow tests/test_corpus_gate.py` for no-regression
- **Before `/gsd-verify-work`:** Full suite must be green, corpus gate compile-fatal-free
- **Max feedback latency:** ~60 s (quick gates)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 20-01-* | 01 | 1 | FID-07, FID-08 | — | N/A (internal renderer) | render-gate | `pytest tests/test_desc_signature_concat_render_gate.py` | ✅ | ⬜ pending |
| 20-02-* | 02 | 1 | FID-09 | — | N/A (internal renderer) | render-gate | `pytest tests/test_field_list_in_list_item_render_gate.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky. Final per-task rows reconciled against PLAN.md `<verify>` blocks by `/gsd-validate-phase`.*

**Per-finding observable validation (GATE-01 + D-07, from RESEARCH.md `## Validation Architecture`):** each finding's fixture MUST fail against the pre-fix translator via **both** (a) a structural `.typ` content-space-token assertion at the correct site AND (b) a `pypdf` extracted-text adjacency assertion, plus a real `-b typstpdf` `typst.compile()` producing valid `%PDF`:
- **FID-07** — `.typ`: space token present between `class`/`exception` annotation and name; pypdf: `"class sphinx"` present / `"classsphinx"` absent.
- **FID-08** — pypdf: `"Py_ssize_t nitems"` present / `"Py_ssize_tnitems"` absent; `"a * f(a)"` present (operator spacing).
- **FID-09** — pypdf: `"Type: int"` and `"Default: 42"` present with the pinned `"Type: int (a number)  Default: 42"` double-space field boundary.

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* `pypdf` is already a dev dependency; the canonical GATE-01 fixture shape (`tests/test_desc_signature_concat_render_gate.py`) and the corpus regression gate (`tests/test_corpus_gate.py`) both exist and are extended, not created.

---

## Manual-Only Verifications

*All phase behaviors have automated verification.* Horizontal (inter-token) spacing is text-extractable, so `pypdf` adjacency asserts cover every finding — no manual visual inspection required (contrast Phase 19's vertical spacing, which was not text-extractable).

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

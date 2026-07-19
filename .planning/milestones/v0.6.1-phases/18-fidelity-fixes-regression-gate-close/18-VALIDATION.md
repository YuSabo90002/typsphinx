---
phase: 18
slug: fidelity-fixes-regression-gate-close
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-19
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`; `sphinx.testing.fixtures` loaded as plugin) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`), `tests/conftest.py` |
| **Quick run command** | `pytest -m "not slow"` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | quick ~tens of seconds; full incl. `-m slow` corpus gate ~minutes (real `sphinx-build -b typstpdf` over the cached Sphinx v9.1.0 corpus) |

---

## Sampling Rate

- **After every task commit:** Run `pytest -m "not slow"` (plus the specific new `*_render_gate` test file for the touched fixture)
- **After every plan wave:** Run `pytest` (full suite)
- **Before `/gsd-verify-work`:** Full suite green, including the `-m slow` corpus gate (`tests/test_corpus_gate.py`) — must run in the full local env, NOT the NixOS sandbox (real corpus builds fail environmentally there; see memory `nixos-sandbox-test-env`)
- **Max feedback latency:** quick tier < ~60s

---

## Per-Task Verification Map

> Seeded as draft. Rows are filled from PLAN.md tasks during `/gsd-validate-phase` / execution.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 18-01-* | 01 | 1 | FID-01a | T-18-01 / — | Wide table wraps within text block; no inter-column collision, no right-margin clip | acceptance (real `typst.compile()` + pypdf text extract) | `pytest tests/test_wide_table_render_gate.py` | ❌ W0 | ⬜ pending |
| 18-01-* | 01 | 1 | GATE-03 | — | Full corpus compiles fatal-free; `unknown_visit` clear of `todo_node`/`manpage` | acceptance (slow, real corpus build) | `pytest tests/test_corpus_gate.py -m slow` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · Exact task IDs / file names are finalized by the planner.*

---

## Wave 0 Requirements

- [ ] `tests/test_wide_table_render_gate.py` — new GATE-01-pattern acceptance fixture for FID-01a (collision-absence assertion; red pre-fix, green post-fix)
- [x] `tests/conftest.py` — shared fixtures already present (no new shared fixtures required)
- [x] Framework already installed (pytest via `uv sync --extra dev`)

*Existing infrastructure covers all phase requirements except the one new FID-01a acceptance fixture.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual confirmation of wrapped wide table in the real corpus PDF | FID-01a | Full visual fidelity (glyph placement) is not machine-asserted beyond text-collision extraction | Build `doc/extdev/deprecated.rst` via `typstpdf`, inspect the "Deprecated APIs" grid table renders with wrapped cells and no right-margin clip |

*Automated collision-absence extraction covers the regression; the manual check is confirmatory only.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s (quick tier)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

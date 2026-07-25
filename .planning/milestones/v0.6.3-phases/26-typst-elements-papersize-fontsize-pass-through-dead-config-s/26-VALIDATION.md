---
phase: 26
slug: typst-elements-papersize-fontsize-pass-through-dead-config-s
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-24
---

# Phase 26 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pyproject.toml (`[tool.pytest.ini_options]`) |
| **Quick run command** | `pytest tests/test_template_engine.py tests/test_config.py -q` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~60-120 seconds (GATE-01 fixtures invoke real `typst.compile()` / `sphinx-build` subprocesses) |

**NixOS sandbox caveat:** per CLAUDE.md, `uv run <compiled-binary>` fails under the sandbox; tests are run via `pytest`/`sphinx-build` with `sys.executable -m sphinx`. A known set of integration tests fail environmentally — the honest green bar is "the 4 new GATE-01 fixtures pass + no NEW failures vs. the pre-change baseline."

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_template_engine.py tests/test_config.py -q`
- **After every plan wave:** Run `pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green (modulo the documented environmental failures)
- **Max feedback latency:** ~120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (planner fills) | 01 | 1 | CONF-04 | — | N/A | unit + gate | `pytest -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] GATE-01 red→green fixtures (papersize positive, fontsize positive, unknown-key raises, copyright non-leak) — planner assigns to a file (mirror `tests/test_package_only_config_gate.py`).

*Planner refines this section.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All phase behaviors have automated verification (real `typst.compile()` fixtures).*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

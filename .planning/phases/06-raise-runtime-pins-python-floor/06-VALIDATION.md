---
phase: 6
slug: raise-runtime-pins-python-floor
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-09
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `06-RESEARCH.md` § Validation Architecture. This phase's gate is
> **CLI-invocation smoke checks + resolution/grep audits**, NOT the full pytest
> suite (Phase 8 owns full-suite-green).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing) — **not this phase's primary gate**; full suite is Phase 8 |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (existing, unchanged this phase) |
| **Quick run command** | `sphinx-build -b typst tests/roots/test-basic <tmpout>` (builder-registration smoke) |
| **Full suite command** | `uv sync --locked` (lockfile-currency gate) + repo-wide grep audit |
| **Estimated runtime** | ~10–30 seconds |

---

## Sampling Rate

- **After every task commit:** Run the builder-registration smoke (`sphinx-build -b typst tests/roots/test-basic`) locally before each commit that touches pin/floor declarations.
- **After the wave:** `uv sync --locked` + the repo-wide grep audit (no `py310`/`py311`, no `sphinx>=5.0,<9`, no `docutils>=0.18,<0.22`, no bare `'3.10'`/`'3.11'` outside historical/planning docs).
- **Phase gate:** All of the above green, PLUS `git show --stat` confirmation that the pin-raise landed atomically (all declaration sites + regenerated `uv.lock` consistent before any CI push).
- **Max feedback latency:** ~30 seconds (all checks are CLI, no long test run).

---

## Per-Task Verification Map

| Req ID | Behavior | Test Type | Automated Command | Observable Success Signal |
|--------|----------|-----------|-------------------|---------------------------|
| FWD-01 | Both builders register under Sphinx 9.1 | smoke (CLI) | `Sphinx()` registration-construction script (RESEARCH Code Examples block 1) | Both `typst: OK` and `typstpdf: OK` printed, exit 0, no exception |
| FWD-01 | Full non-PDF pipeline runs under new stack | smoke (CLI) | `sphinx-build -b typst tests/roots/test-basic <out>` | stdout `build succeeded.`, exit 0, `index.typ` + `_template.typ` in `<out>` |
| PIN-01 | `docutils` resolves Sphinx-9.1-compatible | resolution | `uv lock` then `grep -A2 'name = "docutils"' uv.lock` | `version = "0.22.4"` (or 0.21.x/0.22.x within range; NOT 0.23.x, NOT <0.21) |
| PIN-02 | Python range 3.12–3.13 everywhere; 3.10/3.11 absent | grep audit | repo-wide grep (RESEARCH Pitfall 2) | Zero matches for `py310`/`py311`, old sphinx/docutils ceilings, and `'3.10'`/`'3.11'` outside docs |
| PIN-03 | `uv sync --locked` green at every currency-gate site | resolution | `uv sync --locked` (proxies all CI call sites — same lockfile) | Exit 0, no "lockfile is not up to date" / resolution-conflict |
| PIN-03 | Atomic landing — no intermediate Sphinx-9.1-on-3.10/3.11 state | commit-structure (manual) | `git show --stat <commit>` | All declaration-site edits + lockfile regen in one consistent pushed state |

*Status legend: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements. This phase adds no new pytest files.
- The "tests" are CLI-invocation smoke checks run directly in each plan's `<verify>` steps.
- *(Optional)* A throwaway `scripts/phase6-smoke.sh` wrapping the registration script + `sphinx-build` smoke is sufficient if the planner wants a repeatable artifact — NOT a pytest file (Phase 8 owns the pytest surface).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Atomic pin-raise (no intermediate 3.10/3.11 + Sphinx 9.1 state) | PIN-03 / success criterion #4 | Commit-structure property, not a runtime assertion | `git show --stat` the landing commit(s); confirm all declaration sites + `uv.lock` regen are consistent before any push that triggers CI |

---

## Validation Sign-Off

- [ ] All tasks have an automated (CLI smoke / resolution / grep) verify or are covered by existing infra
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (none for this phase)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

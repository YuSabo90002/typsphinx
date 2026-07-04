---
phase: 1
slug: pin-runtime-dependencies-to-known-good
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-07-04
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> This phase pins dependency versions and lint-cleans the tree; its success
> criteria are verified by **static assertions + lint/lock exit codes**, not by
> new test files. Full-matrix CI green is Phase 2's job (out of scope here).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Static/tooling checks — `black` 26.x, `ruff`, `uv` (lock resolution); `pytest` suite exists but is unchanged this phase |
| **Config file** | `pyproject.toml` (`[tool.black]`, `[tool.ruff]`, `[project.dependencies]`), `tox.ini`, `uv.lock` |
| **Quick run command** | `black --check . && ruff check .` |
| **Full suite command** | `uv lock --check && black --check . && ruff check .` |
| **Estimated runtime** | ~15 seconds (lint + lock check; excludes the Phase-2 CI matrix) |

---

## Sampling Rate

- **After every task commit:** Run `black --check . && ruff check .`
- **After the pin/lock task:** Run `uv lock --check` (must resolve cleanly, zero conflicts)
- **Before `/gsd-verify-work`:** `uv lock --check`, `black --check .`, and `ruff check .` all exit 0
- **Max feedback latency:** ~15 seconds (local); the 3-OS × Python-version CI matrix is verified in Phase 2

---

## Per-Task Verification Map

> Task IDs are assigned during planning (step 8). Rows below map each phase
> success criterion to its observable check; the planner/executor binds these to
> concrete task IDs. Every check is a source assertion, a CLI exit code, or a
> `uv`/lint command — no subjective criteria.

| Success Criterion | Requirement | Test Type | Automated Command / Assertion | Task ID | Status |
|-------------------|-------------|-----------|-------------------------------|---------|--------|
| Runtime three have upper bounds | PIN-01, PIN-02 | static | `grep` in `pyproject.toml`: `typst>=0.14.1,<0.15`, `sphinx>=5.0,<9`, `docutils>=0.18,<0.22` present; none unbounded | 01-01 / Task 1 | ⬜ pending |
| `uv.lock` regenerated & resolves | PIN-03 | tooling | `uv lock --check` exits 0; lock captures a `typst` 0.14.x patch | 01-01 / Task 1 | ⬜ pending |
| `tox.ini` ceilings mirrored | PIN-04 | static | `[testenv]`/`[testenv:type]` `deps` carry the same ceilings as `pyproject.toml` (documentation-truth; runner resolves from `uv.lock`) | 01-01 / Task 1 | ⬜ pending |
| `sphinx-testing` removed | PIN-05 | static | `sphinx-testing` absent from `pyproject.toml`, `tox.ini`, and `uv.lock` | 01-01 / Task 1 | ⬜ pending |
| typst patch confirmed + ceiling finding recorded | PIN-06 | empirical/CI | confirmed-good `typst` 0.14.x patch (research: 0.14.9; 0.15.0 = `kai` error) + D-03 load-bearing finding recorded in `PROJECT.md` Key Decisions | 01-01 / Task 2 | ⬜ pending |
| `black --check .` clean | LINT-01 | tooling | `black --check .` exits 0 on full tree (3 files reformatted: `docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`) | 01-02 / Task 1 | ⬜ pending |
| `ruff check .` clean | LINT-02 | tooling | `ruff check .` exits 0 on full tree (⚠️ not verifiable in the planning sandbox — executor must run early) | 01-02 / Task 2 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements — this phase adds no new
  test files. Verification is static (`grep` on pins), tooling exit codes
  (`black`/`ruff`/`uv lock`), and the empirical typst-patch confirmation.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Confirmed-good typst 0.14.x patch across the full CI matrix | PIN-06 | Cross-OS/Python-version compile behavior can only be confirmed by the real 3-OS CI run; the planning sandbox is Linux-only | Land pins, let Phase-2 CI matrix run; record the empirically-green patch (research candidate: 0.14.9) and any rejected candidates in `PROJECT.md` |
| `ruff check .` passes on the current tree | LINT-02 | The planning sandbox (NixOS, no `nix-ld`) cannot execute the native `ruff` binary | Executor runs `ruff check .` early in an environment where `ruff` is executable; fix or confirm clean |

---

## Validation Sign-Off

- [x] All success criteria have an automated check or a documented manual verification
- [x] Sampling continuity: lint/lock checks run after every commit
- [x] Wave 0 covers all MISSING references (none — existing infra suffices)
- [x] No watch-mode flags
- [x] Feedback latency < 20s (local checks)
- [x] `nyquist_compliant: true` set in frontmatter (task IDs bound in the Per-Task Verification Map above)

**Approval:** task IDs bound to plans 01-01 / 01-02 during planning (2026-07-04)

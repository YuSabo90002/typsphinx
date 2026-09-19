---
phase: "74"
slug: "the-doctest-block-handler-its-real-compile-gate-and-the-docs"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-20"
---

# Phase 74 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (`dev` extra), config in `pyproject.toml` `[tool.pytest.ini_options]` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/test_doctest_block_render_gate.py -x` (new module; exact name fixed by the plans) and `uv run pytest tests/test_translator.py -x` |
| **Full suite command** | `uv run pytest` (plus `LC_ALL=C uv run pytest` before the CI dispatch) |
| **Estimated runtime** | ~130 seconds full suite (main `.venv`, 1547 passed / 1 skipped measured 2026-09-19; worktree counts differ by interpreter and missing `docs` extra — compare only after recording `pyvenv.cfg`) |

---

## Sampling Rate

- **After every task commit:** Run the quick run command for the file being worked on
- **After every plan wave:** Run `uv run pytest`, `uv run ruff check .`, `uv run black --check .`, `uv run mypy typsphinx/`
- **Before `/gsd-verify-work`:** Full suite must be green, plus base/tip clean-build evidence recorded
- **Max feedback latency:** 150 seconds

---

## Per-Task Verification Map

Filled by the planner from the final PLAN.md task IDs.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 74-XX-XX | XX | X | TRN-01 | — | N/A | render-gate + unit | `uv run pytest tests/test_doctest_block_render_gate.py` | ❌ W0 | ⬜ pending |
| 74-XX-XX | XX | X | TRN-02 | — | N/A | render-gate (real `typst.compile()`) | `uv run pytest tests/test_doctest_block_render_gate.py` | ❌ W0 | ⬜ pending |
| 74-XX-XX | XX | X | QUA-14 | — | N/A | scripted clean build + `LC_ALL=C` grep (raw + attributed counts, D-07) | `LC_ALL=C uv run python -m sphinx -b typst docs/source <tmp>` | N/A (evidence file) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_doctest_block_render_gate.py` — GATE-01 gate for TRN-01/TRN-02 (contexts a, b1 definition-list, b2 bullet-list per D-06), recorded RED before the handler lands
- [ ] `tests/fixtures/<name>/` — synthetic fixture project carrying all contexts
- [ ] Docs-build venv: worktree provisioned with `--extra dev --extra docs` for base/tip measurement tasks (the `dev` extra alone cannot import `myst_parser` / `sphinx_autodoc_typehints`)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rendered API-reference meaning unchanged after docstring repair | QUA-14 | Semantic reading of HTML and `.typ` output | Read the affected docstrings' regions in base and tip `-b html` / `-b typst` output and record that only markup changed |
| 3-OS CI run green | SC4 | External GitHub Actions run | `gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release`, then transcribe every job conclusion |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 150s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---
phase: 44
slug: typst-documents-default-derivation-builder-input-hardening
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-04
---

# Phase 44 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ (`dev` extra) with `sphinx.testing.fixtures` loaded as a pytest plugin |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `--strict-markers`) |
| **Quick run command** | `uv run pytest tests/test_config.py tests/test_builder_output_stem.py tests/test_pdf_generation.py tests/test_missing_and_malformed_master_gate.py -v` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | quick ~15s; full suite several minutes — this repo applies **no** `-m "not slow"` filter anywhere (`tox.ini`, CI, `pyproject.toml`), so the full run always includes `tests/test_corpus_gate.py`'s real corpus-compile gate |

**Worktree note (CLAUDE.md standing mode):** every executor provisions first with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and runs all commands via `uv run`.

---

## Sampling Rate

- **After every task commit:** Run the quick run command above (plus the phase's new gate modules once they exist)
- **After every plan wave:** Run `uv run pytest` (full suite — includes the slow corpus gate)
- **Before `/gsd-verify-work`:** Full suite green **plus** `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` — SC#5's exact wording
- **Max feedback latency:** ~20 seconds for the per-task quick command

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| _to be filled by the planner / execute-phase_ | — | — | CONF-08 / BLD-01 | T-44-01 | — | — | — | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] A new fixture project that **omits** `typst_documents` entirely — none of the 103 existing `conf.py` files in the repo can be reused (all of them set it)
- [ ] A new integration gate module for CONF-08 (SC#1 PDF exists and is named via `make_filename_from_project`; SC#2 explicit setting wins), using the `sys.executable -m sphinx` subprocess pattern from `tests/test_missing_and_malformed_master_gate.py` (sidesteps the NixOS PATH-shadowing hazard documented in that module's docstring)
- [ ] A new fixture + gate module for BLD-01's non-`str` docname case, following the same subprocess pattern and the same "one valid master still compiles" assertion shape
- [ ] `tests/test_config.py` — audited, **no change expected** (its two `temp_sphinx_app`-based assertions tolerate the derived default); SC#5 requires this be recorded as a deliberate verified no-op, not silently skipped

*Framework, lint and type tooling are already fully in place — no framework install step is needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SC#4's before/after filename + content pair | CONF-08 | "Before" requires the pre-change tree, so it cannot be asserted from the post-change working copy by an ordinary test | Two-build method from `.planning/milestones/v0.7.0-phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-05.md`: `git archive` the pre-change tree, assert `typsphinx.__file__` resolves into it, build the same no-`typst_documents` project on both trees, record the exact emitted filenames and byte sizes into the phase's `44-GATE-EVIDENCE-*.md` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s for the per-task command
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---
phase: "65"
slug: "tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-12"
---

# Phase 65 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `65-RESEARCH.md` § "Validation Architecture". This phase changes no
> `typsphinx/` behaviour and adds no test file. It edits `pyproject.toml:38`, `tox.ini`'s `requires`
> value, `uv.lock`, and — per D-06's AMENDED block — inverts one existing static gate in
> `tests/test_toolchain_config_gate.py`, all in one commit. Per Phase 64 D-05, TOX-03's proofs are
> recorded verbatim in evidence markdown, gated by commands that re-check the decisive lines.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (`pyproject.toml` `[tool.pytest.ini_options]`), run through `tox` (`uv-venv-lock-runner`); `gh` for the TOX-04 dispatch |
| **Config file** | `pyproject.toml`, `tox.ini` |
| **Quick run command** | `tox --showconfig -e py312` (exercises the `requires` ini-list parse; ~0.2 s — `tox --version` does NOT, see RESEARCH Pitfall 1) and `pytest tests/test_toolchain_config_gate.py -q` (~2 s) |
| **Full suite command** | `tox -vv -e py312 -r` through the shim in the executor worktree (the D-02 observation run doubles as the full suite): 1548 collected |
| **Estimated runtime** | quick ~2 s · full suite ~110 s cold · one CI dispatch ~7 min wall clock |

---

## Sampling Rate

- **After every task commit:** Run `tox --showconfig -e py312` and `pytest tests/test_toolchain_config_gate.py -q`
- **After every plan wave:** Run `tox -vv -e py312 -r` (full suite)
- **Before `/gsd-verify-work`:** Full suite must be green and TOX-04's CI run completed with every job transcribed
- **Max feedback latency:** 120 seconds (the one-off CI dispatch is outside the per-task loop)

---

## Per-Task Verification Map

*Filled from the PLAN.md tasks once planning completes.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test file or fixture; the one
test-side change is the D-06 AMENDED inversion of an existing gate, which lands in the revert commit.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Windows / macOS `uv` resolution under tox-uv's bundled branch | TOX-04 | No Windows/macOS host locally (RESEARCH A1/A2); only CI reaches those lanes | Read the completed dispatched run's job census via `gh run view <id> --json jobs`; transcribe every job's conclusion |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

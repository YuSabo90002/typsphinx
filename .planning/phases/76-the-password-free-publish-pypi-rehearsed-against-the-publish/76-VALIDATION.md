---
phase: "76"
slug: "the-password-free-publish-pypi-rehearsed-against-the-publish"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-27"
---

# Phase 76 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `76-RESEARCH.md` § Validation Architecture. The Per-Task map is filled once plans exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/test_translator_path_quoting_gate.py -q` (worktree: after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`) |
| **Full suite command** | `uv run pytest tests/ -v` (mirrors `release.yml`'s `validate` job) |
| **Estimated runtime** | quick ~5 s; full suite several minutes |

---

## Sampling Rate

- **After every task commit:** MSG-06 tasks run the quick command; the ATT-01 task runs its grep + YAML-parse triplet.
- **After every plan wave:** full suite, plus `black --check .`, `ruff check .`, `mypy typsphinx/` (the `validate` job's own steps).
- **Before `/gsd-verify-work`:** full suite green; ATT-02 external readings recorded in `76-ATT-EVIDENCE.md`.
- **Max feedback latency:** quick command < 30 s. ATT-02 is a one-shot external observation (D-01) and cannot be sampled.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (filled from PLAN.md files after planning) | | | | | | | | | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_translator_path_quoting_gate.py` — new MSG-06 gate, written RED against the pre-fix tree first (created by the MSG-06 plan itself).

*No framework install needed — the `dev` extra already provides pytest/black/ruff/mypy.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rehearsal dispatch rejected as duplicate (`400 File already exists`), zero `invalid-publisher` / `invalid-pending-publisher` | ATT-02 | One irreversible external run on production PyPI; needs the owner's `pypi` environment approval | Wave-2 plan: `gh workflow run release.yml --ref gsd/v0.9.7-trusted-publishing-and-release -f tag=v0.9.6`, exactly-one before/after `gh run list` diff, poll to conclusion (≤ 90 min), `gh run view <id> --log` greps |
| Nothing reached PyPI / no release artifact | ATT-02 | External served state | Pre- vs post-dispatch Simple JSON API capture diff; `gh release view v0.9.6` asset diff; `create-release` and `publish-testpypi` concluded `skipped` |
| Disabling annotation absent, against a non-zero control | ATT-02 (SC #4) | External run log | Per D-08 AMENDED: `grep -c 'disabling Trusted Publishing'` and `grep -c 'attestations input is ignored'` → rehearsal 0, control run `35730551619` 1 |
| PyPI Trusted Publisher registered (owner prerequisite, CONTEXT D-05) | — | Off-repo owner action; no API exposes it | Owner checks the CONTEXT prerequisite box; the duplicate rejection is its verification |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

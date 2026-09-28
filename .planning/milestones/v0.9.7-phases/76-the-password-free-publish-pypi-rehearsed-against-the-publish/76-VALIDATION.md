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
| 76-01-T1 (tracer) | 76-01 | 1 | ATT-01 | T-76-01, T-76-02, T-76-04 | `publish-pypi` presents no credential; diff vs base is exactly the two credential lines; nothing added | static (numstat + `git diff -U0` + grep counts + PyYAML structural parse) | Task 1 `<automated>` in `76-01-PLAN.md` (numstat `0 2`, `PYPI_API_TOKEN` count 1, forbidden-key counts 0, `YAML_STRUCT_OK`) | ✅ `.github/workflows/release.yml` exists | ⬜ pending |
| 76-01-T2 | 76-01 | 1 | ATT-01 | T-76-01, T-76-04 | `publish-testpypi` and `permissions:` byte-identical; no `${{ }}` inside any `run:` block | static (region compare vs `ATT01_BASE_SHA` + PyYAML walk of every `run:` step) | Task 2 `<automated>` in `76-01-PLAN.md` (`ATT01_SC1_VERDICT = MET`) | ✅ | ⬜ pending |
| 76-02-T1 (tracer, tdd) | 76-02 | 1 | MSG-06 | T-76-05 | apostrophe in `down_path` no longer closes the log delimiter early (include site) | unit (caplog DEBUG), recorded RED on the unedited tree first | `LC_ALL=C uv run pytest "tests/test_translator_path_quoting_gate.py::TestIncludePathDebugLogQuoting" -q -p no:cacheprovider` + Task 1 `<automated>` (RED `2 failed, 2 passed` recorded) | ❌ W0 — created by this task | ⬜ pending |
| 76-02-T2 (tdd) | 76-02 | 1 | MSG-06 | T-76-05, T-76-06 | image site routed; zero hardcoded delimiters in either function; sibling modules untouched | unit + full suite + lint trio | `LC_ALL=C uv run pytest tests/test_translator_path_quoting_gate.py -q -p no:cacheprovider` (4 passed) + Task 2 `<automated>` (`MSG06_SC5_VERDICT = MET`) | ✅ after 76-02-T1 | ⬜ pending |
| 76-03-T1 (tracer) | 76-03 | 2 | ATT-02 (ATT-01) | T-76-10, T-76-11 | pushed ref carries both wave-1 changes; CI green on its exact SHA; validate-only checks pass; PyPI/Release baselines and control greps recorded | external read-only + one CI workflow_dispatch | Task 1 `<automated>` in `76-03-PLAN.md` (`PRE_DISPATCH_VERDICT = READY`, live CI and control-log reads) | ✅ `76-ATT-EVIDENCE.md` from 76-01 | ⬜ pending |
| 76-03-T2 (checkpoint:decision, blocking-human) | 76-03 | 2 | ATT-02 | T-76-08, T-76-09 | owner confirms the D-05 Trusted Publisher registration and the SHA before the one-way dispatch | manual (owner answer) | — (no automated verify; the owner's explicit "dispatch"/"hold" is recorded as `OWNER_CHECKPOINT_CHOICE`) | — | ⬜ pending |
| 76-03-T3 | 76-03 | 2 | ATT-02 (ATT-01) | T-76-08, T-76-09, T-76-10, T-76-12, T-76-13, T-76-15 | exactly one dispatch; rejected as duplicate, never invalid-publisher; PyPI and v0.9.6 release unchanged; annotation absent against a non-zero control | external one-shot observation (live `gh run view`, Simple JSON, `gh release view` re-reads) | Task 3 `<automated>` in `76-03-PLAN.md` (`ATT02_VERDICT = MET`, branch-scoped dispatch count 1) | ✅ | ⬜ pending |

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

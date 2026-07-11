---
phase: 09
slug: green-ci-matrix-smoke-test-guardrails
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-11
---

# Phase 09 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `09-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (`>=8.4,<10`, project's existing framework) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]` globs `test_*.py`) |
| **Quick run command** | `uv run pytest tests/test_preview_smoke_gate.py -v` (new file) |
| **Full suite command** | `uv run tox -e py312` (picks up the new smoke test automatically) |
| **Estimated runtime** | Quick: ~seconds (single smoke compile) · Full: minutes (matrix env) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_preview_smoke_gate.py -v` (new smoke test only — seconds)
- **After every plan wave:** Run `uv run tox -e py312` (full local suite incl. new smoke test) plus `uv run tox -e docs-pdf` as the closest local proxy for the `docs.yml` lane
- **Before `/gsd-verify-work`:** Full local suite green (`tox -e py312`/`py313`, `lint`, `type`, `cov`, `docs-pdf`) BEFORE opening the observation PR; then the PR's own Actions run is the final live gate for CI-01
- **Max feedback latency:** ~seconds for the smoke test; minutes for a full matrix leg

---

## Per-Task Verification Map

> Task IDs are TBD until PLAN.md is written; this map is keyed by requirement/behavior.

| Req | Behavior | Threat Ref | Test Type | Automated Command | File Exists | Status |
|-----|----------|------------|-----------|-------------------|-------------|--------|
| CI-01 | Every CI job green on the observed `release/v0.5.0 → main` PR | T-09-04 (stale branch-protection access-control gate) | manual/process (Actions observation — not a pytest test) | `gh pr checks <PR#> --watch` · `gh run list --workflow=ci.yml --workflow=docs.yml --json conclusion` | N/A — process verification | ⬜ pending |
| CI-02 | Smoke test compiles all 4 `@preview` packages via real Typst function calls with no `TypstError` | — | integration (real `typst.compile()`) | `uv run pytest tests/test_preview_smoke_gate.py -v` | ❌ W0 — new fixture + test file | ⬜ pending |
| CI-03 | Guardrail ceilings already reflect `sphinx<10`/`typst<0.16`/`docutils<0.23` | — | manual verification (grep/read, no new test) | `grep -E 'sphinx|docutils|typst' pyproject.toml` | N/A — verification-only per D-06 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/preview_smoke/conf.py` + `tests/fixtures/preview_smoke/index.rst` — new minimal fixture covering all 4 `@preview` packages, incl. **real `.. math::`/`:math:` content** so mitex's `mi()`/`mitex()` actually fires (CI-02)
- [ ] `tests/test_preview_smoke_gate.py` — new pytest module implementing sphinx-build → `typst.compile()` → assert-no-`TypstError` (CI-02)
- Framework install: **none** — pytest / typst-py / pypdf are already dev dependencies

*Negative-control (not a committed test file):* one-time proof that forcing an old `kai`-broken mitex (`0.2.4`/`0.2.5`) in a scratch env makes the new smoke test fail with the `kai` error — documented in the execution summary, not committed as CI surface.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Observed all-green Actions run | CI-01 | Requires a live GitHub Actions run on a real PR — cannot be a local pytest assertion | Open PR `release/v0.5.0 → main`; `gh pr checks <PR#> --watch` until every real job is green |
| Guardrail ceilings reflect new majors | CI-03 | Verification-only per D-06 — reading existing config, not producing new test surface | `grep -E 'sphinx\|docutils\|typst' pyproject.toml`; confirm `drift.yml`/`dependabot.yml` carry no stale ceilings |
| Stale `required_status_checks` reconciliation | CI-01 (access-control durability) | Repo *setting*, not a git-tracked file — no code test possible | `gh api repos/<owner>/typsphinx/branches/main/protection`; confirm `contexts` match current job names |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies (CI-01/CI-03 are process/verification-only by design — documented above)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (smoke fixture + test module)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s for the smoke test
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

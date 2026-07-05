---
phase: 3
slug: modernize-python-floor-3-10-3-13
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-04
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `03-RESEARCH.md` §Validation Architecture. This phase changes
> configuration values (Python floor 3.10–3.13), not test coverage — the
> authoritative "done" signal is the full GitHub Actions matrix green
> (push→observe, carried-forward Phase 2 D-01). Local runs are cheap pre-checks.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (via `[tool.pytest.ini_options]` in `pyproject.toml`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (testpaths=`tests`, markers `slow`/`integration`) |
| **Quick run command** | `uv run pytest tests/ -q -m "not integration and not slow"` |
| **Full suite command** | `uv run tox -e cov -- --cov-report=xml` (CI's coverage job) — or per-version `uv run tox -e py310`/`py311`/`py312`/`py313` |
| **Estimated runtime** | ~1–3 s (quick unit subset, empirically measured); full matrix is CI-bound |

> **NixOS-local caveat:** on this dev machine the test suite's `uv`-subprocess-spawning
> tests hit a dynamic-linking quirk (357 pass / 45 fail, all linking-related, unrelated
> to Python 3.13). Fall back to reading CI for full-suite confirmation on this machine.

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/ -q -m "not integration and not slow"` (~1–3 s) + `black --check .` (near-instant; confirmed no-op this session)
- **After every plan wave:** `uv run tox -e cov -- --cov-report=xml` locally where possible, **plus a `git diff uv.lock` sanity check** (must show only marker-branch collapse + the incidental `chardet` drop — no unrelated version bumps)
- **Before `/gsd-verify-work`:** Full CI matrix green
- **Max feedback latency:** ~3 s local; CI matrix is the phase gate

---

## Per-Task Verification Map

| Requirement | Behavior | Test Type | Automated Command | File Exists |
|-------------|----------|-----------|-------------------|-------------|
| PYVER-01 | `requires-python>=3.10` + classifiers (drop 3.9, add 3.13) set in `pyproject.toml` | static/metadata check | `uv run python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb'))['project']; print(d['requires-python']); print(d['classifiers'])"` | ✅ (metadata assertion, not a pytest test) |
| PYVER-02 | CI matrix covers 3.10–3.13; all hardcoded `uv python install` / `setup-python` lines reconciled to 3.10 | CI observation (push→observe, Phase 2 D-01) | `gh run watch` on the PR's `ci.yml`/`docs.yml` runs (`release.yml` only fires on a real tag push — validate by reading its diff) | ✅ (GitHub Actions run is the test) |
| PYVER-03 | `[tool.black]`/`[tool.ruff]`/`[tool.mypy]` target-versions aligned to 3.10 | automated, existing CI jobs | `uv run tox -e lint` (black --check + ruff check) and `uv run tox -e type` (mypy) | ✅ `tox.ini` `[testenv:lint]`/`[testenv:type]` exist |
| PYVER-04 | `tox.ini` `env_list` updated to py310–py313 in lockstep with CI matrix | static lockstep check + CI observation | `diff <(grep -oP "python-version: \[\K[^]]+" .github/workflows/ci.yml) <(grep env_list tox.ini)` + full matrix green | ✅ (lockstep assertion, not a new pytest test) |
| Success criterion 5 | Full matrix green, no reformat regression, no 3.13 wheel gap | integration (CI) + local pre-check | `black --check .` (confirmed no-op) + push→observe full matrix | ✅ existing `[testenv:lint]` covers black-check |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* This phase changes
configuration values, not test coverage — no new test file, fixture, or
framework install is needed. (`tests/`, `tox.ini` envs, `ci.yml`/`docs.yml`
jobs already cover every PYVER requirement.)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `uv.lock` diff minimality | PYVER (D-04 discipline) | Diff-hygiene judgement, not a boolean assertion | After `uv lock`, `git diff uv.lock` must show only `<3.10`/`>=3.10` marker-branch collapse + incidental `chardet` drop — **no unrelated version bumps** |
| `release.yml` floor reconciliation | PYVER-02 | `release.yml` only runs on a real tag push (not exercised by this PR) | Read the diff: both `uv python install 3.11` lines → `3.10` |

---

## Validation Sign-Off

- [ ] All requirements have an `<automated>` verify or CI-observation path
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (N/A — no Wave 0 gaps)
- [ ] No watch-mode flags
- [ ] Feedback latency < 3s (local pre-check)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

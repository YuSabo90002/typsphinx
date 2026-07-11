---
phase: 10
slug: version-string-fix-v0-5-0-release
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-11
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `10-RESEARCH.md` § Validation Architecture (confidence: HIGH, empirically grounded).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ (`pyproject.toml [tool.pytest.ini_options]`, testpaths `["tests"]`) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `pytest tests/test_extension.py -v` |
| **Full suite command** | `pytest && black --check . && ruff check . && mypy typsphinx/` (or `tox` for the full py310–py313 matrix) |
| **Estimated runtime** | ~10–20 seconds (quick) / minutes (full matrix) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_extension.py -v`
- **After every plan wave:** Run `pytest && black --check . && ruff check . && mypy typsphinx/`
- **Before `/gsd-verify-work`:** Full suite green (`pytest`) **and** `uv sync --locked` exits 0
- **Max feedback latency:** ~20 seconds (quick file), minutes (full)

---

## Per-Task Verification Map

> Task IDs (`10-NN-MM`) are assigned during planning. The requirement→test rows below (from
> `10-RESEARCH.md`) are the concrete checks each plan task must map onto. The executor fills Status.

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| REL-01 | `typsphinx.__version__` reports `0.5.0` after install/sync | unit | `python -c "import typsphinx; assert typsphinx.__version__ == '0.5.0'"` | ✅ extend `tests/test_extension.py` | ⬜ pending |
| REL-01 | `__version__` independently matches `pyproject.toml [project].version` (real drift guard, not the tautological one) | unit | `pytest tests/test_extension.py::test_version_matches_pyproject_toml -v` | ❌ W0 — new test | ⬜ pending |
| REL-01 | `setup(app)` returns `metadata["version"] == "0.5.0"` | unit | `pytest tests/test_extension.py::test_setup_version_matches -v` | ✅ exists (keep) | ⬜ pending |
| REL-01 | `pyproject.toml [project].version == "0.5.0"` | smoke | `python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"` | N/A — file check | ⬜ pending |
| REL-01 | `uv.lock` stays in sync with the bumped `pyproject.toml` | smoke | `uv sync --locked` (exit 0) | N/A — CI gates (`ci.yml`) | ⬜ pending |
| REL-01 (regression) | Full suite + lint/type stay green after the edit | smoke | `pytest && black --check . && ruff check . && mypy typsphinx/` | ✅ existing suite | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_extension.py::test_version_matches_pyproject_toml` — new independent `tomllib`-based
      drift guard (parses `pyproject.toml [project].version` and asserts it equals `typsphinx.__version__`).
      This is the only genuinely new test content needed — it extends the existing, already-covering
      `tests/test_extension.py`; no new test file or `conftest.py` fixture is required.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `CHANGELOG.md` has a curated `## [0.5.0]` entry under the **top** `## [Unreleased]` header (line ~8, NOT the stray one near line 517) | REL-01 | Prose/content quality is not meaningfully automatable | `grep -n "## \[0.5.0\]" CHANGELOG.md` returns a match near the top; entry reads as a user-facing milestone summary (Sphinx 9.1 + docutils 0.22, typst 0.15 + `@preview` kai fix, admonition render fix, Python 3.12–3.13 floor, CI smoke-gate + guardrails) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (the new `test_version_matches_pyproject_toml`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s (quick command)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

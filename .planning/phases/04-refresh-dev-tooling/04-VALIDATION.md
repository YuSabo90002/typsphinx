---
phase: 4
slug: refresh-dev-tooling
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-07-05
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `04-RESEARCH.md` §Validation Architecture. This phase widens/raises
> dev-tool version constraints and bumps two GitHub Actions — it changes
> configuration, not test coverage. The authoritative "done" signal is the full
> GitHub Actions matrix green on a PR targeting `main` (push→observe, carried-forward
> Phase 2/3 D-05). Local `uv run tox` runs are cheap pre-checks. `uv.lock`
> regeneration can shift transitive deps, so only the observed CI run is the gate.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (already resolved in `uv.lock`), invoked via `uv run tox -e <env>` |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (testpaths=`tests`, strict-markers); `tox.ini` per-env `deps`/`commands` |
| **Quick run command** | `uv run tox -e lint` (black --check + ruff check), `uv run tox -e type` (mypy) |
| **Full suite command** | `uv run tox -e cov -- --cov-report=xml` locally (system-Python fallback), then push→observe full `ci.yml` matrix |
| **Estimated runtime** | ~seconds for `-e lint`/`-e type`/`-e cov` locally; full 3.10–3.13 matrix is CI-bound |

> **NixOS-local caveat (Phase 2 finding, STATE.md):** this dev machine cannot execute
> `tox-uv`'s downloaded standalone CPython builds, so `tox -e py310..py313` won't run
> locally. Substitute `uv run tox -e cov` (system Python 3.13) for local pre-check and
> rely on the observed CI matrix (D-05) for full cross-version proof. Bare `tox` is not
> on PATH — always invoke via `uv run tox -e <env>`.

---

## Sampling Rate

- **After every task commit:** `uv run tox -e lint` and/or `-e type` and/or `-e cov`
  depending on which surface the commit touched (pyproject/tox.ini dep bump → run all
  three; README/ruff-comment-only commit → docs-only, none needed; workflow yaml bump →
  no local tox signal, relies on observed CI).
- **After every plan wave:** full local `uv run tox -e lint,type,cov` pass, **plus a
  `git diff uv.lock` sanity check** — must show only constraint-driven changes, no
  unrelated transitive version bumps (plain `uv lock`, never `--upgrade`; Phase 3 D-06
  discipline).
- **Before `/gsd-verify-work`:** observed green `ci.yml` + `docs.yml`.
- **Max feedback latency:** ~seconds local pre-check; CI matrix is the phase gate.

---

## Per-Task Verification Map

| Requirement | Behavior | Test Type | Automated Command | File Exists |
|-------------|----------|-----------|-------------------|-------------|
| TOOL-01 | black/ruff/tox/pytest/mypy/tox-uv floor+ceiling constraints bumped in lockstep across `pyproject.toml [dev]` and `tox.ini` (per-env `deps` + `[tox] requires` for tox-uv); `uv lock` resolves cleanly with a minimal diff | resolution + full CI | `uv lock` (resolves cleanly) → `uv run tox -e lint` / `-e type` / `-e cov` locally → observed green `ci.yml` on PR | ✅ existing `[testenv:lint]`/`[testenv:type]`/`[testenv:cov]` + `ci.yml` — no new test file |
| TOOL-02 | `upload-artifact@v5→@v7` + `download-artifact@v6→@v8` bumped (both now `runs.using: node24`); other 4 actions confirmed compatible; no Node-20 stragglers remain in any workflow | static runtime check + observed CI | `curl -s raw.githubusercontent.com/actions/{upload,download}-artifact/<tag>/action.yml \| grep -A2 "runs:"` (expect `node24`) + observed green `ci.yml`/`docs.yml` on PR | ✅ N/A — config-currency check, not a code-path test |
| Success criterion 3 | CI remains green after the refresh; no regression from any bump; no unexpected black reformat | integration (CI) + local pre-check | `black --check .` (expect no-op; tree already green under resolved 26.5.1) + push→observe full matrix | ✅ existing `[testenv:lint]` covers black-check |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* This phase adds no source
code and needs no new test file, fixture, or framework install. Its "tests" are the
resolution step (`uv lock`) and the existing CI jobs (`tests/`, `tox.ini` envs,
`ci.yml`/`docs.yml`) themselves.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `uv.lock` diff minimality | TOOL-01 (D-06 discipline) | Diff-hygiene judgement, not a boolean assertion | After `uv lock`, `git diff uv.lock` must show only entries tied to the touched constraints — no unrelated transitive bumps |
| Node-runtime currency of bumped actions | TOOL-02 (Pitfall 5) | The Node-20 removal risk is future-dated (2026-09-16); **no CI job fails today** whether or not the actions are bumped | Confirm `upload-artifact@v7`/`download-artifact@v8` declare `runs.using: node24` in their pinned tag's `action.yml`; a green CI run alone does NOT prove this |
| `release.yml`/`docs.yml` action stragglers | TOOL-02 (RESEARCH A2) | `pypa/gh-action-pypi-publish`, `peaceiris/actions-gh-pages`, `softprops/action-gh-release` were not individually runtime-checked in research; `release.yml` only fires on a real tag push | Runtime-check each (`action.yml runs.using`) before closing the phase; record any additional Node-20 straggler as an explicit tracked/deferred item |

---

## Validation Sign-Off

- [x] All requirements have an `<automated>` verify or CI-observation path
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (N/A — no Wave 0 gaps)
- [x] No watch-mode flags
- [x] Feedback latency < 5s (local pre-check)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-07-05

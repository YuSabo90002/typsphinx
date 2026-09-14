---
phase: "73"
slug: "v0-9-5-close-prep-prep-only-unpublished"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-14"
---

# Phase 73 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `73-RESEARCH.md` § Validation Architecture. REL-14 is **not** closed by any test in
> this phase. It closes at `/gsd-complete-milestone` on the observed merge; this phase fences it
> (SC#4, D-08).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (`pyproject.toml` `[tool.pytest.ini_options]`), orchestrated by tox (`env_list = py312, py313, lint, type, cov, docs`); Sphinx `html` / `typstpdf` / `linkcheck` builders as build-time gates |
| **Config file** | `pyproject.toml`; `tox.ini` (including `[testenv:linkcheck]`) |
| **Quick run command** | `uv run pytest tests/test_changelog_page_gate.py -v -rs -p no:cacheprovider` |
| **Full suite command** | `LC_ALL=C uv run pytest -q -rs -p no:cacheprovider` |
| **Estimated runtime** | ~130 seconds (full suite); docs tox environments several minutes each; `tox -e linkcheck` network-bound; the CI dispatch ~15–25 minutes |

Baseline carried in (re-measure, never inherit — constraint 8): Phase 72's close recorded
`1547 passed, 1 skipped` in the main checkout. A fresh worktree provisioned with `--extra dev` only
lacks `myst_parser`, so `tests/test_changelog_page_gate.py` skips there; the SC#2 zero-skip reading
needs `--extra dev --extra docs`. Record `.venv/pyvenv.cfg` `home` and `version_info` and the skip
reasons (`-rs`) before comparing counts. Extract pytest counts with a non-anchored
`grep -oE '[0-9]+ passed'` (the summary line is wrapped in `=` decoration).

---

## Sampling Rate

- **After every task commit:** the task's own evidence read-back (e.g. `grep -c '^## \[0\.9\.[345]\]' CHANGELOG.md` = 0; scoped `git diff` fences after every git/gh mutation)
- **After every plan wave:** `LC_ALL=C uv run pytest` + `uv run black --check .` + `uv run mypy typsphinx/` + `uv run ruff check .`
- **Before `/gsd-verify-work`:** full suite green under `LC_ALL=C`; both docs tox environments from a
  clean build (`rm -rf` of the output directory immediately before each counted build) with zero
  `multiple toctrees`; `tox -e linkcheck` clean with `working` == total; one CI dispatch on the
  phase's own pushed tip with every job `success`
- **Max feedback latency:** 180 seconds for local gates; linkcheck and CI are the documented exceptions

---

## Per-Task Verification Map

Seeded per plan from `73-RESEARCH.md` § Recommended Plan Decomposition. To be reconciled against
the final `73-*-PLAN.md` task list once planning completes.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 73-01-* | 01 | 1 | REL-14 (coverage only) / SC#2, D-01..D-05 | T-73-* | `### Added` + `### Fixed` inserted as a two-hunk pure addition; `### Changed` block and everything else byte-identical; no `0.9.3`/`0.9.4`/`0.9.5` literal; no CI-job claim; clean docs builds before and after with zero `multiple toctrees` | audit (numstat/region hash) + docs build | 73-01 task `<automated>` blocks | ❌ W1 | ⬜ pending |
| 73-02-* | 02 | 1 | REL-14 (fence) / SC#4, D-08; SC#1 observation 1, D-13 | T-73-* | phase-head SHA-256, `wc -l`, `grep -n 'REL-14'`, `PHASE_BASE_SHA`; every remote negative positive-controlled against `v0.9.2`; reasoned `COVERAGE.md` | audit (checksum + remote probes) | 73-02 task `<automated>` blocks | ❌ W1 | ⬜ pending |
| 73-03-* | 03 | 2 | REL-14 (coverage only) / SC#3, D-14 | T-73-* | full suite twice (once `LC_ALL=C`); black/mypy/ruff; version-sync family; changelog gate 0 skipped; docs-html/docs-pdf clean, warning count equals the phase-base baseline, zero `multiple toctrees`; linkcheck `working` == total | full suite + lint + docs build + linkcheck | 73-03 task `<automated>` blocks | ❌ W2 | ⬜ pending |
| 73-04-* | 04 | 2 | REL-14 (coverage only) / SC#3, D-12 | T-73-* | decoy census; canonical branch pushed only; exactly one `workflow_dispatch` CI run at `PUSHED_SHA`; every job `success`, both windows-latest and both macos-latest lanes named; no `release.yml` run | CI dispatch + census | 73-04 task `<automated>` blocks | ❌ W2 | ⬜ pending |
| 73-05-* | 05 | 2 | REL-14 (coverage only) / SC#3, D-06, D-07, D-09 | T-73-* | non-committing `git merge-tree --write-tree` trial merge; merged-tree `uv lock --check` and `ruff check .`; strict protection with the six contexts of `REQUIRED_CONTEXTS_HEAD`; merge-commit precedent; Dependabot #146–#150 recorded, untouched | audit (merge-tree) + lint | 73-05 task `<automated>` blocks | ❌ W2 | ⬜ pending |
| 73-06-* | 06 | 3 | REL-14 (coverage only) / SC#1, D-13 | T-73-* | observation 2 of every SC#1 probe; `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` empty with a widened-diff positive control; post-dispatch commits `.planning/`-only | audit | 73-06 task `<automated>` blocks | ❌ W3 | ⬜ pending |
| 73-07-* | 07 | 4 | REL-14 (fence) / SC#4, D-06, D-08, D-10, D-11 | T-73-* | close-time digest MATCH; negative-first standalone handoff; Dependabot order; two not-applicable steps; REL-14 post-merge observations | audit (checksum + content) | 73-07 task `<automated>` blocks | ❌ W4 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. Every command this phase needs (`pytest`,
`black`, `mypy`, `ruff`, `tox -e docs-html` / `docs-pdf` / `linkcheck`, `git`, `gh`, `curl`) was
exercised at Phase 72's close.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Third fence observation after `phase.complete`-family tooling (including `/gsd-verify-work`'s inline transition) | REL-14 / SC#4 | Runs outside every plan's reach, after the orchestrator's own transition step | Run the block reproduced in `73-HANDOFF.md`: `sha256sum .planning/REQUIREMENTS.md`, `git diff --name-only -- .planning/REQUIREMENTS.md`, `grep -n 'REL-14' .planning/REQUIREMENTS.md`; on divergence `git checkout -- .planning/REQUIREMENTS.md` and report, never commit |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s (linkcheck and CI dispatch excepted)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

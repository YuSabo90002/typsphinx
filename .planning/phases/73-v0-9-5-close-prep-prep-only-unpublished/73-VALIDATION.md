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

Reconciled against the final `73-*-PLAN.md` task list: 16 tasks across 7 plans in 4 waves. Every
task carries an `<automated>` verify with a `<fails_when>` statement; none is manual-only.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 73-01-01 | 01 | 1 | REL-14 (coverage only) / SC#2, SC#3; D-01..D-05, D-14 | T-73-01..05 | pre-edit measurements; clean phase-base docs-html/docs-pdf builds under `LANG=C LC_ALL=C` with zero `multiple toctrees` against Phase 72's positive control; `### Added` + `### Fixed` inserted; tracer docs-html render unchanged | audit + docs build | 73-01 Task 1 `<automated>` | ❌ W1 | ⬜ pending |
| 73-01-02 | 01 | 1 | REL-14 (coverage only) / SC#2; D-01..D-05, D-14 | T-73-01..05 | two-hunk pure addition, zero deletions, `### Changed` and Planned blocks byte-identical; bullet content assertions (IDs present; no version, count, URL, CI or `stable` claim); post-edit clean builds equal the base; changelog page gate 0 skipped | audit (diff + region hash) + docs build + unit | 73-01 Task 2 `<automated>` | ❌ W1 | ⬜ pending |
| 73-02-01 | 02 | 1 | REL-14 (fence) / SC#4; D-08 | T-73-06 | phase-head SHA-256, `wc -l`, `grep -n 'REL-14'`, `PHASE_BASE_SHA` tied to Phase 72's pushed tip; both operator procedures | audit (checksum) | 73-02 Task 1 `<automated>` | ❌ W1 | ⬜ pending |
| 73-02-02 | 02 | 1 | REL-14 (coverage only) / SC#1 obs 1; D-13 | T-73-07..09 | tag, PyPI, Release, release.yml and PR probes for 0.9.3–0.9.5, each positive-controlled against `v0.9.2`; milestone `typsphinx/` + `.github/workflows/` diff empty with pathspec and widened-diff controls | audit (remote probes) | 73-02 Task 2 `<automated>` | ❌ W1 | ⬜ pending |
| 73-02-03 | 02 | 1 | REL-14 (coverage only) | T-73-10 | reasoned `COVERAGE.md`; `check api-coverage.verify-pre` passes | audit | 73-02 Task 3 `<automated>` | ❌ W1 | ⬜ pending |
| 73-03-01 | 03 | 2 | REL-14 (coverage only) / SC#3; D-05 | T-73-11, T-73-15 | worktree identity; product delta = `CHANGELOG.md`; `main` not absorbed; full suite green | full suite | 73-03 Task 1 `<automated>` | ❌ W2 | ⬜ pending |
| 73-03-02 | 03 | 2 | REL-14 (coverage only) / SC#3; D-14 | T-73-12 | `LC_ALL=C` full suite; black/mypy/ruff; version-sync family; changelog gate 0 skipped | full suite + lint + unit | 73-03 Task 2 `<automated>` | ❌ W2 | ⬜ pending |
| 73-03-03 | 03 | 2 | REL-14 (coverage only) / SC#3; D-05, D-14 | T-73-13, T-73-14 | docs-html/docs-pdf clean, counts equal 73-01's base, zero `multiple toctrees`; `tox -e linkcheck` `working` == total from `output.json`, at most 3 runs, `conf.py` unchanged | docs build + linkcheck | 73-03 Task 3 `<automated>` | ❌ W2 | ⬜ pending |
| 73-04-01 | 04 | 2 | REL-14 (coverage only) / SC#3; D-12, D-13 | T-73-16, T-73-17, T-73-19..21 | decoy census; fast-forward push of the canonical branch only; one `workflow_dispatch` CI run at `PUSHED_SHA`, listed before any retry | CI dispatch + census | 73-04 Task 1 `<automated>` | ❌ W2 | ⬜ pending |
| 73-04-02 | 04 | 2 | REL-14 (coverage only) / SC#3; D-09, D-12 | T-73-18 | every job `success`, both windows-latest and both macos-latest lanes named; job set = Phase 72's run; ruff from `Lint and Format Check`; one dispatch; no `release.yml` run; required checks unchanged | CI observation | 73-04 Task 2 `<automated>` | ❌ W2 | ⬜ pending |
| 73-05-01 | 05 | 2 | REL-14 (coverage only) / SC#3; D-07, D-09 | T-73-22, T-73-24, T-73-26 | non-committing `git merge-tree --write-tree`, reproduced; merged `uv lock --check`; nothing moved | audit (merge-tree + lock) | 73-05 Task 1 `<automated>` | ❌ W2 | ⬜ pending |
| 73-05-02 | 05 | 2 | REL-14 (coverage only) / SC#3; D-06, D-07, D-09, D-10 | T-73-23, T-73-25 | merged-tree `ruff check .` and `black --check .`; strict protection = `REQUIRED_CONTEXTS_HEAD`; #143/#145 merge-commit precedent; Dependabot #146–#150 recorded, untouched | lint + remote read | 73-05 Task 2 `<automated>` | ❌ W2 | ⬜ pending |
| 73-06-01 | 06 | 3 | REL-14 (coverage only) / SC#1 obs 2; D-13 | T-73-27 | every observation-1 probe re-run later with its positive control | audit (remote probes) | 73-06 Task 1 `<automated>` | ❌ W3 | ⬜ pending |
| 73-06-02 | 06 | 3 | REL-14 (coverage only) / SC#1; D-12, D-13 | T-73-28..30 | close-tip `typsphinx/` + `.github/workflows/` diff empty with controls; phase product diff = `CHANGELOG.md`; post-dispatch commits `.planning/`-only | audit | 73-06 Task 2 `<automated>` | ❌ W3 | ⬜ pending |
| 73-07-01 | 07 | 4 | REL-14 (fence) / SC#4; D-08 | T-73-31 | close-time digest, line count and REL-14 grep MATCH the phase-head baseline | audit (checksum) | 73-07 Task 1 `<automated>` | ❌ W4 | ⬜ pending |
| 73-07-02 | 07 | 4 | REL-14 (fence) / SC#4; D-06, D-07, D-10, D-11, D-15 | T-73-32..35 | negative-first standalone handoff; conditional branch update; six checks; merge commit; REL-14 post-merge observations; Dependabot after the milestone PR; third observation inline | audit (content + checksum) | 73-07 Task 2 `<automated>` | ❌ W4 | ⬜ pending |

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

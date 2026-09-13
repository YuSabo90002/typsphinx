---
phase: "71"
slug: "v0-9-4-close-prep-prep-only-unpublished"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-13"
---

# Phase 71 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `71-RESEARCH.md` § Validation Architecture. REL-13 is **not** closed by any test in
> this phase — it closes at `/gsd-complete-milestone` on the observed merge; this phase fences it
> (SC#4).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (`pyproject.toml` `[tool.pytest.ini_options]`, `testpaths = ["tests"]`), orchestrated by tox (`env_list = py312, py313, lint, type, cov, docs`) |
| **Config file** | `pyproject.toml`; `tox.ini` |
| **Quick run command** | `uv run pytest -m "not slow"` |
| **Full suite command** | `LC_ALL=C uv run pytest -q -rs -p no:cacheprovider` |
| **Estimated runtime** | ~120 seconds (full suite); docs tox environments several minutes each; the CI dispatch ~15–25 minutes |

Baseline carried in (re-measure, never inherit): `PYTEST_RESULT_AFTER = 1547 passed 1 skipped` at
Phase 70's close (`70-AFTER-RUNTIME-EVIDENCE.md`). A fresh worktree provisioned with `--extra dev`
only lacks `myst_parser`, so `tests/test_changelog_page_gate.py` skips there; the SC#2 zero-skip
reading needs `--extra dev --extra docs`. Record `.venv/pyvenv.cfg` `home` and `version_info` and the
skip reasons (`-rs`) before comparing counts. Extract pytest counts with a non-anchored
`grep -oE '[0-9]+ tests? collected'` (the summary line is wrapped in `=` decoration).

---

## Sampling Rate

- **After every task commit:** the task's own evidence read-back (e.g. `grep -c '^## \[0\.9\.[34]\]' CHANGELOG.md` = 0)
- **After every plan wave:** `LC_ALL=C uv run pytest` + `uv run black --check .` + `uv run mypy typsphinx/` + `uv run ruff check .`
- **Before `/gsd-verify-work`:** full suite green under `LC_ALL=C`, both docs tox environments from a
  clean build (`rm -rf docs/_build` immediately before each counted build), and one CI dispatch on
  the phase's own pushed tip with every job `success`
- **Max feedback latency:** 180 seconds for local gates; CI is the documented exception

---

## Per-Task Verification Map

Reconciled against the final 71-01..71-07 PLAN.md files (16 tasks; every task carries an
`<automated>` verify with a `<fails_when>`). Threat refs are the plan's `<threat_model>` IDs.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 71-01-01 | 01 | 1 | REL-13 (coverage only) / SC#2, D-01..D-03 | T-71-01..T-71-05 | pre-edit measurements and clean docs baselines; the bullet rendered through MyST | audit + docs build | 71-01 Task 1 `<automated>` (evidence keys, clean `uv run tox -e docs-html` baseline) | ✅ | ⬜ pending |
| 71-01-02 | 01 | 1 | REL-13 (coverage only) / SC#2, D-01..D-04 | T-71-01..T-71-05 | pure addition under `### Changed`; no `0.9.3`/`0.9.4` literal; no ja/Japanese/catalog wording; everything else byte-identical; both docs environments clean equal the baseline | audit (grep/awk region) + docs build | 71-01 Task 2 `<automated>` (`git diff --numstat` pure addition, region bullet count 4, clean docs counts) | ✅ | ⬜ pending |
| 71-02-01 | 02 | 1 | REL-13 (fence) / SC#4, D-09 | T-71-06..T-71-10 | phase-head digest, line count, REL-13 lines and `PHASE_BASE_SHA` after the AMENDED commit; operator procedures | audit (checksum) | 71-02 Task 1 `<automated>` (`sha256sum .planning/REQUIREMENTS.md` equals `REQ_SHA256_BASE`) | ✅ | ⬜ pending |
| 71-02-02 | 02 | 1 | REL-13 (coverage only) / SC#1, D-11 | T-71-06..T-71-10 | observation 1: every remote negative with a positive control against `v0.9.2`; milestone fences; D-11 part 1 at phase head | audit (remote probes + diff) | 71-02 Task 2 `<automated>` (`git ls-remote --tags`, PyPI JSON, `gh release list`, `git diff` since `e721ff89`) | ✅ | ⬜ pending |
| 71-02-03 | 02 | 1 | seal-time API-coverage gate | T-71-06..T-71-10 | reasoned no-external-API declaration | audit | 71-02 Task 3 `<automated>` (`gsd-tools.cjs check api-coverage.verify-pre` → passed) | ✅ | ⬜ pending |
| 71-03-01 | 03 | 2 | REL-13 (coverage only) / SC#3, D-05 | T-71-11..T-71-15 | tree identity; product delta exactly `CHANGELOG.md`; `main` not absorbed; full suite 0 failed | full suite | 71-03 Task 1 `<automated>` | ✅ | ⬜ pending |
| 71-03-02 | 03 | 2 | REL-13 (coverage only) / SC#3 | T-71-11..T-71-15 | `LC_ALL=C` suite; black, mypy, ruff; version-sync family; changelog page gate with 0 skipped | full suite + lint + type | 71-03 Task 2 `<automated>` | ✅ | ⬜ pending |
| 71-03-03 | 03 | 2 | REL-13 (coverage only) / SC#3 docs | T-71-11..T-71-15 | both docs environments built clean equal 71-01's clean pre-edit baseline | docs build | 71-03 Task 3 `<automated>` | ✅ | ⬜ pending |
| 71-04-01 | 04 | 2 | REL-13 (coverage only) / SC#3, D-10 | T-71-16..T-71-21 | decoy census; fast-forward push of the canonical ref only; one dispatch at `PUSHED_SHA` | CI dispatch | 71-04 Task 1 `<automated>` | ✅ | ⬜ pending |
| 71-04-02 | 04 | 2 | REL-13 (coverage only) / SC#3 | T-71-16..T-71-21 | 12/12 jobs success; both windows-latest and both macos-latest lanes named; ruff from `Lint and Format Check`; no release.yml run | CI census | 71-04 Task 2 `<automated>` (`gh run view RUN_ID --json jobs`) | ✅ | ⬜ pending |
| 71-05-01 | 05 | 2 | REL-13 (coverage only) / SC#3, D-05 | T-71-22..T-71-25 | non-committing trial merge reproduced from its inputs; merged lock valid in scratch | audit (merge-tree) | 71-05 Task 1 `<automated>` (`git merge-tree --write-tree`, `uv lock --check`) | ✅ | ⬜ pending |
| 71-05-02 | 05 | 2 | REL-13 (coverage only) / SC#3, D-06, D-12 | T-71-22..T-71-25 | merged-tree lint at merged versions; strict protection with six checks; merge-commit precedent; read-only PR census | audit + lint | 71-05 Task 2 `<automated>` | ✅ | ⬜ pending |
| 71-06-01 | 06 | 3 | REL-13 (coverage only) / SC#1, D-11 | T-71-26..T-71-30 | observation 2; phase-scoped product diff; post-dispatch commits planning-only; D-11 part 1 on the close tip | audit | 71-06 Task 1 `<automated>` | ✅ | ⬜ pending |
| 71-06-02 | 06 | 3 | REL-13 (coverage only) / SC#1, D-11 | T-71-26..T-71-30 | masked-AST hashes equal for the ten converted files against `697a1132`, with two mutation controls and a raw-bytes-differ check | audit (masked-AST) | 71-06 Task 2 `<automated>` | ✅ | ⬜ pending |
| 71-07-01 | 07 | 4 | REL-13 (fence) / SC#4, D-09 | T-71-31..T-71-35 | close-time digest MATCH; no commit touched REQUIREMENTS.md; divergence reverted by hand | audit (checksum) | 71-07 Task 1 `<automated>` | ✅ | ⬜ pending |
| 71-07-02 | 07 | 4 | REL-13 / SC#4, D-06..D-08, D-12 | T-71-31..T-71-35 | negative-first handoff; ordered `/gsd-complete-milestone` steps; third observation reproduced inline; no tag/release/pin-dispatch command | audit (content) | 71-07 Task 2 `<automated>` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. Every command this phase needs (`pytest`,
`black`, `mypy`, `ruff`, `tox -e docs-html` / `docs-pdf`, `git`, `gh`, `curl`) was exercised at
Phase 70's close.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Third fence observation after `phase.complete`-family tooling (including `/gsd-verify-work`'s inline transition) | REL-13 / SC#4 | Runs outside every plan's reach, after the orchestrator's own transition step | Run the block reproduced in `71-HANDOFF.md`: `sha256sum .planning/REQUIREMENTS.md`, `git diff --name-only -- .planning/REQUIREMENTS.md`, `grep -n 'REL-13' .planning/REQUIREMENTS.md`; on divergence `git checkout -- .planning/REQUIREMENTS.md` and report, never commit |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s (CI dispatch excepted)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

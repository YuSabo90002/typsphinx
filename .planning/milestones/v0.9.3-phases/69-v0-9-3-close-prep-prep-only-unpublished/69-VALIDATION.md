---
phase: "69"
slug: "v0-9-3-close-prep-prep-only-unpublished"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-13"
---

# Phase 69 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `69-RESEARCH.md` § Validation Architecture. REL-12 is **not** closed by any test in
> this phase — it closes at `/gsd-complete-milestone`; this phase fences it (SC#4).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (`pyproject.toml` `[tool.pytest.ini_options]`, `testpaths = ["tests"]`), orchestrated by tox (`env_list = py312, py313, lint, type, cov, docs`) |
| **Config file** | `pyproject.toml`; `tox.ini` |
| **Quick run command** | `uv run pytest -m "not slow"` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~120 seconds (full suite); docs tox environments several minutes each; the CI dispatch ~15–25 minutes |

Baseline carried in (re-measure, never inherit): **1547 passed / 1 skipped** in the main checkout at
Phase 68 close. A fresh worktree provisioned with `--extra dev` only lacks `myst_parser`, so
`tests/test_changelog_page_gate.py`'s build classes skip there — record `pyvenv.cfg` `home` and
`version_info` and the skip reasons (`-rs`) before comparing counts.

---

## Sampling Rate

- **After every task commit:** the task's own evidence read-back (e.g. `69-CHANGELOG-EVIDENCE.md`
  heading/bullet counts, `grep -c '^## \[0\.9\.3\]' CHANGELOG.md` = 0)
- **After every plan wave:** `uv run pytest` + `uv run black --check .` + `uv run mypy typsphinx/`
- **Before `/gsd-verify-work`:** full suite green, both docs tox environments from a clean build
  (`rm -rf docs/_build` immediately before each counted build), and one CI dispatch on the phase's
  own pushed tip with all 12 jobs `success`
- **Max feedback latency:** 180 seconds for local gates; CI is the documented exception

---

## Per-Task Verification Map

Task IDs are assigned by the planner; rows below follow the research decomposition and are
reconciled against the final PLAN.md files.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 69-01-01 | 01 | 1 | REL-12 (coverage only) / SC#2, SC#3 docs | T-69-01, T-69-03 | clean pre-edit baselines for both docs environments; TOX bullet under `### Changed` above an unchanged Planned block; pure addition | audit + docs build | awk region heading order `### Changed` then `### Planned for Future Releases`; no removed line in `git diff BASE_69_01 -- CHANGELOG.md`; clean `uv run tox -e docs-html` count equals `DOCS_HTML_WARN_BASE` | ✅ | ⬜ pending |
| 69-01-02 | 01 | 1 | REL-12 (coverage only) / SC#2, SC#3 docs | T-69-02, T-69-04, T-69-05 | three bullets, 20 IDs, three no-effect phrases; no `0.9.3` anywhere; heading and link counts and final line equal the base; both docs environments clean equal the baseline | audit + docs build | `grep -c '0\.9\.3' CHANGELOG.md` → 0; region bold-bullet line count → 3; clean docs-html and docs-pdf counts equal `_BASE`; `head -c 5 docs/_build/pdf/typsphinx.pdf` → `%PDF-` | ✅ | ⬜ pending |
| 69-02-01 | 02 | 1 | REL-12 (fence) / SC#4 | T-69-06 | digest, line count, REL-12 hits and `PHASE_BASE_SHA` at phase head; both transition entry points named; reversion procedure | audit (checksum) | `sha256sum .planning/REQUIREMENTS.md` equals `REQ_SHA256_BASE`; REL-12 checkbox `- [ ]` and row Pending | ✅ | ⬜ pending |
| 69-02-02 | 02 | 1 | REL-12 / SC#1 | T-69-07, T-69-08 | observation 1, every remote negative with a positive control; milestone `typsphinx/` diff empty with a non-empty widened control | audit (remote probes) | `git ls-remote --tags origin` v0.9.2 once, v0.9.3 never; PyPI 0.9.2 → 200 / 0.9.3 → 404; latest release v0.9.2; release.yml run 33318905691 listed; `git diff MILESTONE_BASE HEAD -- typsphinx` empty | ✅ | ⬜ pending |
| 69-02-03 | 02 | 1 | seal-time API-coverage gate | T-69-09 | reasoned no-external-API declaration with the verbatim detector result | audit | `gsd-tools.cjs check api-coverage.verify-pre <phase dir>` → `"passed": true` | ✅ | ⬜ pending |
| 69-03-01 | 03 | 2 | SC#3 local | T-69-10 | worktree identity; product delta exactly `CHANGELOG.md`; `main` not absorbed (D-06); full suite 0 failed | full suite | `uv run pytest -q -rs`; collect count equals `COLLECTED_69_03`; `git diff --name-only PHASE_BASE_SHA HEAD` outside `.planning` → `CHANGELOG.md` | ✅ | ⬜ pending |
| 69-03-02 | 03 | 2 | SC#3 local | T-69-11, T-69-13 | suite under `LC_ALL=C`; black, mypy, ruff; version-sync family; changelog page gate with 0 skipped | full suite + lint + type | `LC_ALL=C uv run pytest`; `uv run black --check .`; `uv run mypy typsphinx/`; `uv run ruff check .`; `uv run pytest tests/test_changelog_page_gate.py -rs` with no skipped line | ✅ | ⬜ pending |
| 69-03-03 | 03 | 2 | SC#3 local (docs) | T-69-12 | both docs environments built clean on the merged tree equal 69-01's clean pre-edit baseline; real PDF | docs build | `rm -rf docs/_build` then `uv run tox -e docs-pdf` and `docs-html`, counts equal `_BASE` | ✅ | ⬜ pending |
| 69-04-01 | 04 | 2 | SC#3 CI / D-13, D-14 | T-69-14, T-69-15, T-69-17 | decoy census immediately before the push; fast-forward push of the canonical ref only; one dispatch at `PUSHED_SHA` | CI dispatch | origin head equals `PUSHED_SHA`; `gh run view RUN_ID --json headSha,event,workflowName` | ✅ | ⬜ pending |
| 69-04-02 | 04 | 2 | SC#3 CI | T-69-16 | 12/12 success; both windows-latest and both macos-latest lanes named; ruff from `Lint and Format Check` at the lock version; one dispatch; no release.yml run | CI census | `gh run view RUN_ID --json jobs` → 12 success; `gh run list --workflow=release.yml` has none at `PUSHED_SHA` | ✅ | ⬜ pending |
| 69-05-01 | 05 | 2 | D-07 | T-69-19, T-69-21 | non-committing trial merge exits 0; merged lock valid; nothing moved | audit (merge-tree) | `git merge-tree --write-tree TRIAL_HEAD ORIGIN_MAIN_SHA` reproduces `MERGE_TREE`; `uv --directory SCRATCH lock --check` | ✅ | ⬜ pending |
| 69-05-02 | 05 | 2 | D-07, D-08, D-10 | T-69-20, T-69-22 | merged-tree lint at merged versions; strict protection with six checks; #135/#136 merge-commit precedent; read-only PR census | audit + lint | locked scratch sync then `ruff check .` and `black --check .`; `gh api repos/YuSabo90002/typsphinx/branches/main/protection` | ✅ | ⬜ pending |
| 69-06-01 | 06 | 3 | SC#1 | T-69-25, T-69-26 | observation 2 later than observation 1; phase `typsphinx/` diff empty with a `CHANGELOG.md`-only control; post-dispatch commits planning-only | audit | `git diff PHASE_BASE_SHA HEAD -- typsphinx/` empty; `git diff --name-only PUSHED_SHA HEAD` outside `.planning` empty | ✅ | ⬜ pending |
| 69-06-02 | 06 | 3 | REL-12 (fence) / SC#4 | T-69-24 | close-time digest MATCH; no commit in the phase touched REQUIREMENTS.md | audit (checksum) | `sha256sum` equals `REQ_SHA256_BASE`; `git log PHASE_BASE_SHA..HEAD -- .planning/REQUIREMENTS.md` empty | ✅ | ⬜ pending |
| 69-06-03 | 06 | 3 | SC#4 handoff / D-08..D-11 | T-69-23, T-69-27 | negative-first opening; ordered `/gsd-complete-milestone` steps; third observation inline | audit (content) | first 14 lines of `69-HANDOFF.md` carry every negative item; required strings present; no tag, release-creation or pin-dispatch command | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. Every command this phase needs (`pytest`,
`black`, `mypy`, `tox -e docs-html` / `docs-pdf`, `git`, `gh`, `curl`) was exercised at Phase 68's
close.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Third fence observation after `phase.complete`-family tooling (including `/gsd-verify-work`'s inline transition) | REL-12 / SC#4 | Runs outside every plan's reach, after the orchestrator's own transition step | Run the block reproduced in `69-HANDOFF.md`: `sha256sum .planning/REQUIREMENTS.md`, `git diff --name-only -- .planning/REQUIREMENTS.md`, `grep -n 'REL-12' .planning/REQUIREMENTS.md`; on divergence `git checkout -- .planning/REQUIREMENTS.md` and report, never commit |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s (CI dispatch excepted)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

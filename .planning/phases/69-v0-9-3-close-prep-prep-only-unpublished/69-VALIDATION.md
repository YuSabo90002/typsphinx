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
| 69-01-* | 01 | 1 | REL-12 (coverage only) / SC#2 | T-69 tampering (unreleased text into a release section) | `### Changed` sits above `### Planned for Future Releases`; no `## [0.9.3]`, no `[0.9.3]:` link; `[Unreleased]` compare base `v0.9.2` | audit (grep + diff) | `grep -c '^## \[0\.9\.3\]' CHANGELOG.md` → 0; `grep -c '^\[0\.9\.3\]:' CHANGELOG.md` → 0; `grep -c 'compare/v0\.9\.2\.\.\.HEAD' CHANGELOG.md` → 1 | ✅ | ⬜ pending |
| 69-02-* | 02 | 1 | REL-12 (fence) / SC#1, SC#4 | T-69 tampering (checkbox flip); repudiation (vacuous remote negative) | baseline SHA-256 / `wc -l` / `PHASE_BASE_SHA` / `grep -n 'REL-12'` recorded; every remote negative paired with a positive control | audit (checksum + probes) | `sha256sum .planning/REQUIREMENTS.md`; `git ls-remote --tags origin 'v0.9*'`; PyPI JSON 0.9.2 → 200 / 0.9.3 → 404; `git diff --stat <merge-base> HEAD -- typsphinx/` empty | ✅ | ⬜ pending |
| 69-03-* | 03 | 2 | SC#3 | T-69 repudiation (stale CI run cited) | dispatched run's `headSha` equals the pushed tip; 12/12 jobs `success`; both `windows-latest` lanes named | full suite + lint + type + docs + CI | `uv run pytest`; `uv run black --check .`; `uv run mypy typsphinx/`; `rm -rf docs/_build && uv run tox -e docs-html` (and `docs-pdf`); `gh run view <id> --json headSha,jobs` | ✅ | ⬜ pending |
| 69-04-* | 04 | 3 | REL-12 (fence) / SC#4 | T-69 tampering (checkbox flip) | close-time SHA-256 MATCH; third observation block reproduced in `69-HANDOFF.md`; D-07 trial merge rc 0 | audit (checksum + merge-tree) | `sha256sum .planning/REQUIREMENTS.md`; `git diff --name-only -- .planning/REQUIREMENTS.md` empty; `git merge-tree --write-tree HEAD origin/main` | ✅ | ⬜ pending |

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

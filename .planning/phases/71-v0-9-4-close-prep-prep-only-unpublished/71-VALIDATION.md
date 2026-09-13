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

Task IDs are assigned by the planner; the rows below follow the research's requirement map and are
reconciled against the final PLAN.md files.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | REL-13 (coverage only) / SC#2 | TBD | one bullet under `## [Unreleased]` → `### Changed`, house register, no version literal, no ja/catalog wording, everything else byte-identical | audit (grep/awk region) + docs build | `grep -c '0\.9\.[34]' CHANGELOG.md` → 0; region bold-bullet count → 4; tail link block unchanged; clean docs counts equal the clean baseline | ✅ | ⬜ pending |
| TBD | TBD | TBD | REL-13 (coverage only) / SC#1 | TBD | unpublished-shape probes, each with a positive control against `v0.9.2` | audit (remote probes) | `git ls-remote --tags origin`; PyPI JSON 0.9.2 → 200 / 0.9.4 → 404; `gh release list` | ✅ | ⬜ pending |
| TBD | TBD | TBD | REL-13 (coverage only) / SC#1 D-11 | TBD | no code change since Phase 70's final code commit; masked-AST equality against Phase 70's `PHASE_BASE_SHA` for the converted files | audit (diff + masked-AST) | `git diff --stat <Phase 70 final code commit>..HEAD -- typsphinx/ tests/` empty; mask hashes equal per converted file, with a non-vacuity control | ✅ | ⬜ pending |
| TBD | TBD | TBD | REL-13 (coverage only) / SC#3 | TBD | tree green locally, on CI, and on a non-committing trial merge of `origin/main` | full suite + lint + type + CI dispatch + merge-tree | `LC_ALL=C uv run pytest`; `uv run black --check .`; `uv run ruff check .`; `uv run mypy typsphinx/`; `gh run view <id> --json jobs`; `git merge-tree --write-tree`; `uv lock --check` | ✅ | ⬜ pending |
| TBD | TBD | TBD | REL-13 (fence) / SC#4 | TBD | checkbox held at `[ ]` behind a SHA-256 fence, three separated observations; standalone handoff | audit (checksum + content) | `sha256sum .planning/REQUIREMENTS.md` equal at head/close/post-`phase.complete`; handoff required strings present | ✅ | ⬜ pending |

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

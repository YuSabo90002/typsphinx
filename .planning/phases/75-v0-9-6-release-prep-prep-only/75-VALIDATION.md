---
phase: "75"
slug: "v0-9-6-release-prep-prep-only"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-20"
---

# Phase 75 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by `/gsd-plan-phase` from `75-RESEARCH.md` § "Validation Architecture".
> The Per-Task Verification Map is filled by `/gsd-validate-phase` once plans exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (via `tox`'s `uv-venv-lock-runner`), plus `ruff` / `black` / `mypy` as static gates and Sphinx's `html` / `typstpdf` / `linkcheck` builders as build-time gates |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.ruff]`, `[tool.black]`, `[tool.mypy]`); `tox.ini` (env definitions) |
| **Quick run command** | `uv run pytest tests/test_changelog_page_gate.py tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v -rs` |
| **Full suite command** | `uv run pytest -q -rs`, then once more under `LC_ALL=C` |
| **Estimated runtime** | ~150 seconds full suite — **re-measure fresh at the plan's own base; do not transcribe a prior count** (ROADMAP constraint 4). Worktree counts differ by interpreter and by the missing `docs` extra; compare only after recording `pyvenv.cfg`. |

**Environment note (blocking for SC1).** A worktree provisioned with `uv sync --extra dev` alone does
**not** carry the `docs` extra, and `tests/test_changelog_page_gate.py` then *skips* rather than
fails. SC1 demands a **zero-skip** reading of that gate, so the executing environment must be
provisioned with `--extra dev --extra docs` (or the reading taken in the main checkout). `-rs` is
mandatory on every invocation of that gate so a skip cannot pass unnoticed.

**NixOS note.** `.venv/bin/ruff` does not execute on this machine; invoke bare `ruff` so the PATH
shim runs it inside the FHS sandbox. `black`, `mypy` and `pytest` run fine from `.venv/bin/`.

---

## Sampling Rate

- **After every task commit:** Run the quick run command (the three version-sync / changelog gates) after any product-tree edit
- **After every plan wave:** Run `uv run pytest -q -rs`, `ruff check .`, `black --check .`, `mypy typsphinx/`
- **Once, after the bump + CHANGELOG wave:** the full local green-tree suite (pytest twice, once under `LC_ALL=C`), clean `tox -e docs-html` / `tox -e docs-pdf` / `tox -e linkcheck`, and the single CI dispatch on the bumped tip
- **Before `/gsd-verify-work`:** SC1–SC5 all MET and transcribed into the phase evidence files
- **Max feedback latency:** 150 seconds for the quick subset

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| {N}-01-01 | 01 | 1 | REQ-{XX} | T-{N}-01 / — | {expected secure behavior or "N/A"} | unit | `{command}` | ✅ / ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Filled by `/gsd-validate-phase` after plans exist. The success-criteria-level map seeded from
research is:*

| SC | Observable Behavior | Verification Type | Evidence File |
|----|---------------------|--------------------|---------------|
| SC1 | `pyproject.toml:7` = `0.9.6`; `uv.lock` regenerated; `README.md` Status = `v0.9.6`; `uv sync --extra dev --locked` exits 0; `RELEASE_VERSIONS` gains `"0.9.6"`; changelog-page gate **zero-skipped** | unit + build | `75-BUMP-EVIDENCE.md` |
| SC2 | Six carried bullets byte-identical; two new bullets; tail link block moved; `scripts/extract_changelog_section.py 0.9.6` stdout transcribed | unit + build | `75-CHANGELOG-EVIDENCE.md` |
| SC3 | `### Known Limitations` in `## [0.9.6]` names NUM-01 only; `grep -c 'Known Limitations' CHANGELOG.md` = **2** (the pre-existing `[0.1.0b1]` heading plus the new one) | build + state | `75-CHANGELOG-EVIDENCE.md` |
| SC4 | pytest ×2 (one under `LC_ALL=C`); lint/type/format; clean `docs-html` / `docs-pdf` with zero `doctest_block` unknown-node and zero `Unexpected indentation` / `Block quote ends without a blank line`; clean `linkcheck`; exactly one CI dispatch on the bumped tip; non-committing trial merge | unit + integration + build + remote | `75-GREEN-TREE-EVIDENCE.md`, `75-CI-EVIDENCE.md`, `75-PREFLIGHT-EVIDENCE.md` |
| SC5 | Tag / PyPI / Release probes empty at two separated observations with positive controls; SHA-256 fence MATCH at three observations; standalone handoff | state | `75-CLOSEOUT-GUARD.md`, `75-HANDOFF.md` |

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* Every test this phase needs
(`test_changelog_page_gate.py`, `test_readme_version_sync.py`, `test_preview_version_sync.py`, the
full suite) already exists and was green at Phase 74's close. This phase adds no new test
infrastructure; it edits one existing test file's data tuple (`RELEASE_VERSIONS`).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| REL-15's four publish observations (merge commit on `origin/main`, `git ls-remote --tags origin`, PyPI 200 for `0.9.6`, `gh release list`) | REL-15 | The phase is prep-only by binding constraint 1 — these observations are only makeable *after* `/gsd-complete-milestone` runs. Inside this phase the same probes are run inverted, as **emptiness** checks with positive controls. | Enumerated in `75-HANDOFF.md`; executed at `/gsd-complete-milestone`, not here. |
| CHANGELOG prose quality (lead paragraph register, bullet wording, `### Known Limitations` entry shape) | REL-16 | Editorial judgement against the `[0.9.2]` / `[0.1.0b1]` models; no assertion can check register. | Diff the new section against `CHANGELOG.md`'s `## [0.9.2]` (`:69`) and `### Known Limitations` (`:1205`) and confirm the structural rules (bold lead, trailing-parenthesis requirement IDs, `Workaround:` line) hold. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 150s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

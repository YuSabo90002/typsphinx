---
phase: "77"
slug: "v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-28"
---

# Phase 77 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `77-RESEARCH.md` § Validation Architecture. The Per-Task map is filled once plans exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `LC_ALL=C uv run pytest -q tests/test_readme_version_sync.py tests/test_changelog_page_gate.py tests/test_preview_version_sync.py` (worktree: after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` — the `docs` extra is required for the changelog page gate to run at zero skipped) |
| **Full suite command** | `uv run pytest -q` and `LC_ALL=C uv run pytest -q` (SC#3: twice, once under `LC_ALL=C`) |
| **Estimated runtime** | quick ~10 s; full suite several minutes; docs-html/docs-pdf/linkcheck minutes each |

---

## Sampling Rate

- **After every task commit:** the oracle command the task's own SC targets (bump task → `tests/test_readme_version_sync.py` + `pytest -rs tests/test_changelog_page_gate.py`; CHANGELOG task → `uv run python scripts/extract_changelog_section.py 0.9.7`; probe tasks → their `git tag -l` / `git ls-remote` / `gh` probes with positive controls).
- **After every plan wave:** `LC_ALL=C uv run pytest -q` full suite.
- **Before `/gsd-verify-work`:** full suite green in both locales + `black --check .` / `ruff check .` / `mypy typsphinx/` + clean `tox -e docs-html` / `tox -e docs-pdf` + `tox -e linkcheck` + one CI dispatch completed on the bumped tip; CLOSEOUT-GUARD and HANDOFF evidence recorded against that proven-green tip.
- **Max feedback latency:** quick command ~10 s.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (filled once plans exist) | | | | | | | | | ⬜ pending |

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-17 (prep, SC#1) | version bump lockstep | unit | `uv run pytest -q tests/test_readme_version_sync.py` | ✅ |
| REL-17 (prep, SC#1) | changelog page gate at zero skipped | integration (needs `docs` extra) | `uv run pytest -rs -q tests/test_changelog_page_gate.py` | ✅ |
| REL-17 (prep, SC#2) | `## [0.9.7]` extracts cleanly | script | `uv run python scripts/extract_changelog_section.py 0.9.7` | ✅ |
| REL-17 (prep, SC#3) | `@preview` sync unbroken | unit | `uv run pytest -q tests/test_preview_version_sync.py` | ✅ |
| ATT-06 (SC#4) | no `v0.9.7` tag anywhere at the rollback-section commit | probe | `git tag -l 'v0.9.7'` + `git ls-remote --tags origin 'refs/tags/v0.9.7*'` (positive control `v0.9.6`) | n/a — shell probe |
| ATT-03/04/05, REL-17, DOC-25 (SC#5) | guarded lines unchanged | probe | `sha256sum .planning/REQUIREMENTS.md` + scoped `grep -n` against `77-CLOSEOUT-GUARD.md` | n/a — shell probe |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements (`tests/test_readme_version_sync.py`, `tests/test_changelog_page_gate.py`, `tests/test_preview_version_sync.py`, `scripts/extract_changelog_section.py` all exist).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ATT-03/04/05, DOC-25, REL-17 publish half | coverage-only | irreversible steps executed only at `/gsd-complete-milestone` | follow `77-HANDOFF.md` in its stated order |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s for quick command
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

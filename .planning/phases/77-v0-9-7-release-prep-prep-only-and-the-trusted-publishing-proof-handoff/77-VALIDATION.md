---
phase: "77"
slug: "v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-28"
audited: "2026-09-28"
---

# Phase 77 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `77-RESEARCH.md` § Validation Architecture. Per-Task map filled by the retroactive
> `/gsd-validate-phase 77` audit on 2026-09-28.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `LC_ALL=C uv run pytest -q tests/test_readme_version_sync.py tests/test_changelog_page_gate.py tests/test_preview_version_sync.py` (worktree: after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` — the `docs` extra is required for the changelog page gate to run at zero skipped) |
| **Full suite command** | `uv run pytest -q` and `LC_ALL=C uv run pytest -q` (SC#3: twice, once under `LC_ALL=C`) |
| **Estimated runtime** | quick ~5 s (measured 4.33 s at audit); full suite several minutes; docs-html/docs-pdf/linkcheck minutes each |

---

## Sampling Rate

- **After every task commit:** the oracle command the task's own SC targets (bump task → `tests/test_readme_version_sync.py` + `pytest -rs tests/test_changelog_page_gate.py`; CHANGELOG task → `uv run python scripts/extract_changelog_section.py 0.9.7`; probe tasks → their `git tag -l` / `git ls-remote` / `gh` probes with positive controls).
- **After every plan wave:** `LC_ALL=C uv run pytest -q` full suite.
- **Before `/gsd-verify-work`:** full suite green in both locales + `black --check .` / `ruff check .` / `mypy typsphinx/` + clean `tox -e docs-html` / `tox -e docs-pdf` + `tox -e linkcheck` + one CI dispatch completed on the bumped tip; CLOSEOUT-GUARD and HANDOFF evidence recorded against that proven-green tip.
- **Max feedback latency:** quick command ~5 s.

---

## Per-Task Verification Map

Every task carries its own `<automated>` block. Those blocks are **point-in-time evidence oracles**:
they assert the tree/ledger state at the moment the task ran (e.g. `version = "0.9.6"` at the
base, `REQUIREMENTS.md` byte-identical to the phase base, no product diff since the plan's base
SHA) and open with `test -f .git` (worktree-only). All 21 passed at execution time (each SUMMARY's
`Self-Check: PASSED`). Re-run at audit HEAD `abc22a28` with the worktree guard stripped, 3 still
pass and 18 fail **by design** — later waves (the bump commit, `phase.complete`'s intended ATT-06
flip) legitimately moved the state they pin. None of the 18 failures is a regression; the durable
per-requirement oracles are in the second table.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 77-01-T1 | 01 | 1 | REL-17 (fence) | T-77 fence | REQUIREMENTS guarded lines recorded before any edit | probe | plan `<automated>` (CLOSEOUT-GUARD base keys) | ✅ | ✅ green at exec · point-in-time |
| 77-01-T2 | 01 | 1 | REL-17 (SC#3 base) | — | — | probe | plan `<automated>` (BASE-EVIDENCE ledger) | ✅ | ✅ green at exec · point-in-time |
| 77-01-T3 | 01 | 1 | SC#5 obs 1 | no irreversible action | no tag/PyPI/Release/run; token present | probe | plan `<automated>` (SC5-INVARIANTS OBS1) | ✅ | ✅ green at exec · point-in-time |
| 77-02-T1 | 02 | 1 | REL-17 (SC#1) | — | — | unit+probe | plan `<automated>` + `tests/test_readme_version_sync.py` | ✅ | ✅ green at exec · point-in-time |
| 77-02-T2 | 02 | 1 | REL-17 (SC#2) | — | — | integration | plan `<automated>` + `tests/test_changelog_page_gate.py` | ✅ | ✅ green at exec · point-in-time |
| 77-02-T3 | 02 | 1 | REL-17 (SC#1/2) | — | — | script | plan `<automated>` + `extract_changelog_section.py 0.9.7` | ✅ | ✅ green at exec · point-in-time |
| 77-03-T1 | 03 | 1 | ATT-06 | rollback pre-tag | rollback recorded before any tag | probe | plan `<automated>` (ATT06-EVIDENCE digest) | ✅ | ✅ green at exec · point-in-time |
| 77-03-T2 | 03 | 1 | ATT-03/04/05, DOC-25 (controls) | read-only probes | controls measured, nothing executed | probe | plan `<automated>` (CONTROLS-EVIDENCE) | ✅ | ✅ green at exec · point-in-time |
| 77-04-T1 | 04 | 2 | REL-17 (SC#3) | — | — | full suite | plan `<automated>` (lint trio + pytest ×2) | ✅ | ✅ green at exec · point-in-time |
| 77-04-T2 | 04 | 2 | REL-17 (SC#3) | — | — | docs build | plan `<automated>` (GREEN-TREE docs ledger) | ✅ | ✅ green (re-run at audit) |
| 77-04-T3 | 04 | 2 | REL-17 (SC#3) | — | — | linkcheck | plan `<automated>` (GREEN-TREE linkcheck) | ✅ | ✅ green at exec · point-in-time |
| 77-05-T1 | 05 | 2 | REL-17 (preflight) | — | — | trial merge | plan `<automated>` (merge-tree + lock/lint) | ✅ | ✅ green (re-run at audit) |
| 77-05-T2 | 05 | 2 | REL-17 (preflight) | — | — | probe | plan `<automated>` (PREFLIGHT verdict) | ✅ | ✅ green at exec · point-in-time |
| 77-06-T1 | 06 | 3 | REL-17 (SC#3 CI) | one dispatch only | fast-forward push + single dispatch | probe | plan `<automated>` (CI-EVIDENCE marker) | ✅ | ✅ green at exec · point-in-time |
| 77-06-T2 | 06 | 3 | REL-17 (SC#3 CI) | — | — | probe | plan `<automated>` (`gh run view 36430787178`) | ✅ | ✅ green (re-run at audit) |
| 77-07-T1 | 07 | 4 | REL-17, ATT-06 | — | — | doc audit | plan `<automated>` (HANDOFF steps 1–3) | ✅ | ✅ green at exec · point-in-time |
| 77-07-T2 | 07 | 4 | ATT-03/04/05, DOC-25 | secret retire gated after ATT-03 | ordering in handoff | doc audit | plan `<automated>` (HANDOFF steps 4–8) | ✅ | ✅ green at exec · point-in-time |
| 77-07-T3 | 07 | 4 | REL-17 | — | — | doc audit | plan `<automated>` (HANDOFF steps 9–12) | ✅ | ✅ green at exec · point-in-time |
| 77-08-T1 | 08 | 5 | SC#5 obs 2 | no irreversible action | fence observation 2 | probe | plan `<automated>` (CLOSEOUT/SC5 close keys) | ✅ | ✅ green at exec · point-in-time |
| 77-08-T2 | 08 | 5 | SC#5 | scope fence | no product diff outside bump | probe | plan `<automated>` (scope fence + controls) | ✅ | ✅ green at exec · point-in-time |
| 77-08-T3 | 08 | 5 | all six (census) | — | — | probe | plan `<automated>` (SC roll-up) | ✅ | ✅ green at exec · point-in-time |

### Durable per-requirement oracles (re-run green at audit HEAD `abc22a28`)

| Req ID | Behavior | Test Type | Automated Command | File Exists? | Audit result |
|--------|----------|-----------|-------------------|-------------|--------------|
| REL-17 (prep, SC#1) | version bump lockstep | unit | `uv run pytest -q tests/test_readme_version_sync.py` | ✅ | ✅ green |
| REL-17 (prep, SC#1) | changelog page gate at zero skipped | integration (needs `docs` extra) | `uv run pytest -rs -q tests/test_changelog_page_gate.py` | ✅ | ✅ green, 0 skipped |
| REL-17 (prep, SC#2) | `## [0.9.7]` extracts cleanly | script + unit | `uv run python scripts/extract_changelog_section.py 0.9.7 \| sha256sum` → `82f27b34…6f6`; `tests/test_changelog_extraction.py` | ✅ | ✅ digest matches evidence; 6 passed |
| REL-17 (prep, SC#3) | `@preview` sync unbroken | unit | `uv run pytest -q tests/test_preview_version_sync.py` | ✅ | ✅ green |
| ATT-06 (SC#4) | rollback section unchanged since recorded | probe | `awk '$0=="## Rollback procedure (ATT-06)"{f=1;print;next} f&&/^## /{exit} f' 77-HANDOFF.md \| grep -v '^$' \| sha256sum` → `4406fb65…192b` | n/a — shell probe | ✅ matches `ROLLBACK_SECTION_SHA256` |
| ATT-06 (SC#4) | no `v0.9.7` tag anywhere (pre-tag window only) | probe | `git tag -l 'v0.9.7'` + `git ls-remote --tags origin 'refs/tags/v0.9.7*'` (positive control `v0.9.6`) | n/a — shell probe | ✅ absent; control present |
| ATT-03/04/05, REL-17, DOC-25 (SC#5) | guarded lines unchanged | probe | `grep -vE '^- \[.\] \*\*ATT-06\*\*\|^\| ATT-06 \|' .planning/REQUIREMENTS.md \| sha256sum` → `fce6cc7d…d4af5` | n/a — shell probe | ✅ matches `REQ_SHA256_GUARDED_BASE`/`_CLOSE` |

Note: the whole-file `sha256sum .planning/REQUIREMENTS.md` now reads `89f6eaff…` instead of the
phase-close `35eb6122…`. The only delta is `phase.complete` (commit `4b39d7aa`) flipping ATT-06 to
`[x]` / `Complete` — ATT-06 is the one requirement this phase closes, which is exactly why the
guarded digest excludes the ATT-06 lines. The five coverage-only/split IDs remain `- [ ]`.

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements (`tests/test_readme_version_sync.py`, `tests/test_changelog_page_gate.py`, `tests/test_preview_version_sync.py`, `tests/test_changelog_extraction.py`, `scripts/extract_changelog_section.py` all exist). No new test files were needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ATT-03/04/05, DOC-25, REL-17 publish half | coverage-only | irreversible steps executed only at `/gsd-complete-milestone` | follow `77-HANDOFF.md` Steps 1–12 in its stated order; each step carries its pre-written command, expected output and measured control |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s for quick command
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-09-28

---

## Validation Audit 2026-09-28

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

Requirements: REL-17 (prep half) and ATT-06 COVERED by durable oracles re-run green at `abc22a28`;
ATT-03/04/05, DOC-25 and REL-17's publish half are manual-only by design (post-tag, irreversible).
Task-level oracles: 21/21 green at execution; 3/21 still green on re-run, 18/21 point-in-time by
design (not regressions).

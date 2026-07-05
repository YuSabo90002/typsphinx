---
phase: 5
slug: durability-guardrails
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-05
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> **Nature of this phase:** CI/CD-configuration only — no application-level test
> framework surface. Verification is the CI pipeline itself (push→observe, D-10)
> plus static config checks, consistent with Phases 2–4.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — CI/CD config phase; verification = CI pipeline (push→observe, D-10) + static `grep` checks. No pytest/jest surface added. |
| **Config file** | `.github/workflows/ci.yml`, `docs.yml`, `release.yml`, new `drift.yml`; `.github/dependabot.yml`; `README.md` |
| **Quick run command** | `grep -n "uv sync" .github/workflows/*.yml \| grep -v -- "--locked"` (expect empty output once DUR-01 lands) |
| **Full suite command** | Push branch → open PR targeting `main` → observe `ci.yml`/`docs.yml` green (D-10); separately `gh workflow run drift.yml && gh run watch` for DUR-02 |
| **Estimated runtime** | Static checks ~instant; PR CI observation ~5–15 min; drift.yml manual run ~5–10 min |

---

## Sampling Rate

- **After every task commit:** Run the relevant static check (`grep`-based call-site count, group-block presence, badge line presence) — near-instant.
- **After every plan wave:** Push→observe PR against `main` for DUR-01/03/04 + D-11's CI-visible parts.
- **Before `/gsd-verify-work`:** `ci.yml`/`docs.yml` green on the PR (existing required checks) **and** `drift.yml` manually confirmed via `workflow_dispatch` to (a) run to completion and (b) dedupe/report correctly on a forced-failure test.
- **Max feedback latency:** static checks <5s; CI observation bounded by GitHub Actions run time (~15 min).

---

## Per-Requirement Verification Map

> Task IDs are assigned by the planner; rows below are keyed by requirement and
> must each land in a plan task's `<acceptance_criteria>` / `must_haves`.

| Requirement | Behavior | Test Type | Automated / Manual Command | File Exists | Status |
|-------------|----------|-----------|----------------------------|-------------|--------|
| DUR-01 | Every `uv sync` call site has `--locked`; existing `--extra` flags preserved | static-check | `grep -n "uv sync" .github/workflows/*.yml \| grep -v -- "--locked"` (expect empty) | ✅ existing | ⬜ pending |
| DUR-01 | `--locked` gate is load-bearing (fails on lock↔pyproject desync) | inherent semantics (D-03: not re-tested — lock currently in sync) | — | N/A | ⬜ pending |
| DUR-02 | `drift.yml` runs weekly, resolves latest deps, exercises them, reports via deduplicated issue on failure | manual smoke (scheduled jobs can't be PR-observed) | `gh workflow run drift.yml && gh run watch` | ❌ W0 (new file) | ⬜ pending |
| DUR-02 | `drift.yml` is NOT in `main`'s required status checks | config/manual check | `gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '.contexts'` (expect no drift entry) | N/A | ⬜ pending |
| DUR-03 | `dependabot.yml` groups sphinx/docutils/typst under `pip` | static-check | `grep -A6 "sphinx-typst-stack" .github/dependabot.yml` (or equivalent group-name check) | ❌ W0 (block absent) | ⬜ pending |
| DUR-04 | CI badge renders and links correctly in README | manual visual | Open README on GitHub after merge; confirm badge SVG loads + links to `actions/workflows/ci.yml` | ❌ W0 (line absent) | ⬜ pending |
| D-11 | `softprops/action-gh-release@v3` runs successfully | tag-gated smoke (NOT exercised by a normal PR — Pitfall 3) | `docs.yml` release step fires only on `refs/tags/v*`; `release.yml` supports `workflow_dispatch` with `tag` input for manual test | N/A (edited, not created) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.github/workflows/drift.yml` — does not exist yet; entire file is new (DUR-02)
- [ ] `.github/dependabot.yml` `groups:` block — does not exist yet (DUR-03)
- [ ] `README.md` badge line — does not exist yet (DUR-04)

*No test-framework install needed — this phase has no pytest/jest-style automated
test surface; verification is CI-pipeline observation and static config checks.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Weekly drift job resolves latest deps, exercises them, dedupe-reports on failure | DUR-02 | Scheduled/`workflow_dispatch`-only workflows don't run on `pull_request` events | Add `workflow_dispatch:` to `drift.yml` (D-10); `gh workflow run drift.yml && gh run watch`; force a failure to confirm single-issue dedup |
| `drift.yml` never becomes a required check | DUR-02 / D-07 | Branch-protection state, not a repo file | `gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '.contexts'` — drift job absent |
| CI badge renders + links | DUR-04 | GitHub serves badge SVG live; markdown render is visual | View README on GitHub post-merge |
| `action-gh-release@v3` runs green | D-11 | Release steps are tag-gated (`refs/tags/v*`), not run on PRs (Pitfall 3) | Defer to next real release tag, or `workflow_dispatch` `release.yml` with a test `tag` input; may need human sign-off |

---

## Validation Sign-Off

- [ ] All requirements have an automated static check or an explicit manual verification with instructions
- [ ] Sampling continuity: no 3 consecutive tasks without an automated/static verify
- [ ] Wave 0 covers all MISSING references (drift.yml, dependabot group, badge line)
- [ ] No watch-mode flags
- [ ] Feedback latency documented per sampling tier
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

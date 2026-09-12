---
phase: "66"
slug: "github-dependabot-yml-pip-uv-ecosystem"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-12"
---

# Phase 66 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `66-RESEARCH.md` § Validation Architecture. This phase edits one GitHub-platform YAML file
> (`.github/dependabot.yml`); no Python import surface is touched (constraint 13), so verification is
> observation-based — reading GitHub's and dependabot's own output — not test-suite-based.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + tox (unchanged; not exercised by this phase's edit) |
| **Config file** | none for `.github/dependabot.yml` — the project's suite does not validate it |
| **Quick run command** | `git diff <main-tip> <milestone-tip> -- .github/dependabot.yml` (D-01 byte-identity; must print nothing) |
| **Full suite command** | the 6 required CI checks on the `main`-bound PR (branch protection, `strict: true`) |
| **Estimated runtime** | quick: ~1 second; CI: ~10 minutes; dependabot observation: minutes to hours (external) |

---

## Sampling Rate

- **After every task commit:** re-run the D-01 byte-identity `git diff` whenever either copy of `.github/dependabot.yml` changes
- **After every plan wave:** re-run the byte-identity diff; after the merge, re-read the `main` copy via `gh api`
- **Before `/gsd-verify-work`:** all 6 required checks green on the `main`-bound PR; DEP-04 leg 2 recorded (pass, or HALT for the owner)
- **Max feedback latency:** bounded by external services (CI run, dependabot job) — the plans set the polling bound

---

## Per-Task Verification Map

Seeded per requirement; the planner's task IDs replace the `66-TBD` placeholders.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 66-TBD | TBD | TBD | DEP-01 | — | config change reaches `main` only through a PR with 6 green required checks | manual (external observation) | `gh pr view <n> --json commits,files` + `git show --name-only <sha>` | ❌ W0 (evidence file) | ⬜ pending |
| 66-TBD | TBD | TBD | DEP-03 | — | N/A | manual (external observation) | `gh pr view <n> --json labels,title,headRefName`; `gh pr list --author app/dependabot` | ❌ W0 (evidence file) | ⬜ pending |
| 66-TBD | TBD | TBD | DEP-04 | — | N/A | manual (external + local probe) | `gh api` reads of dependabot-core `uv/Dockerfile` and `uv/helpers/requirements.txt`; `uv lock --check` on the real PR head | ❌ W0 (evidence file) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Phase evidence markdown (name at the planner's discretion) — home for the D-02 snapshots of #123/#128, the D-04 "config accepted" observation, the D-05 legs 1 and 2, and the D-06 observations

*No test-file gap: these requirements have no automated-test equivalent by construction (they describe an external service's behaviour).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dependabot accepts the `uv` configuration (no config error on the Dependabot tab) | DEP-01 | No public API exposes dependabot job status (dependabot-core #3080) | Owner opens Insights → Dependency graph → Dependabot, reads the `uv` entry's status / last-checked time, and reports it |
| Trigger a version-update run if none started after the merge | DEP-01 (D-03) | No public API triggers a version-update job | Owner clicks "Check for updates" on the same page |
| A real `uv` PR's head commit changes `pyproject.toml` and `uv.lock` together | DEP-01 (D-04) | Only dependabot can produce the artifact | Read the PR with `gh pr view --json commits,files` and `git show --name-only` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency bounded (external waits have an explicit polling bound)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

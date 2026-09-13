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

Task IDs are `66-<plan>-<task>`. Each "Automated Command" is the `<automated>` block of that task in its PLAN.md, with a `<fails_when>` beside it; the column summarizes what it asserts.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 66-01-01 | 66-01 | 1 | DEP-01, DEP-03 | T-66-01, T-66-02, T-66-04 | main-bound commit is one file, parented on `origin/main`, holding the same blob as the milestone copy; no force-push; PR body names no PR number | automated (git + gh) | `cmp` of the milestone copy against `origin/main` with line 4 swapped; blob SHA equality across `HEAD`, `PR_COMMIT`; `rev-list --count` = 1; PR base/head/files/commits/state; run headSha + event | ❌ W0 → `66-MAIN-PR-EVIDENCE.md` (created by this task) | ⬜ pending |
| 66-01-02 | 66-01 | 1 | DEP-01 | T-66-03 | PR stays unmerged; the six required checks are green | automated (gh) | run `completed`; each of the six required job names `success`; protection lists 6 contexts; PR `OPEN` at `PR_COMMIT` | same | ⬜ pending |
| 66-02-01 | 66-02 | 2 | DEP-01 | T-66-07 | pre-merge gate: main unmoved, head unchanged, blobs identical, REL-12 simulation clean | automated (git + gh) | blob equality; `git merge-tree --write-tree PR_COMMIT HEAD` exit 0; gate section names `BASE_SHA`, `PR_COMMIT` and all six checks | same | ⬜ pending |
| 66-02-02 | 66-02 | 2 | DEP-01 | T-66-06 | owner go-ahead before a one-way merge (D-01) | manual (`checkpoint:decision`, `gate="blocking-human"`) | — (answer recorded as `OWNER_DECISION` by 66-02-03) | — | ⬜ pending |
| 66-02-03 | 66-02 | 2 | DEP-01 | T-66-06, T-66-07, T-66-08 | two-parent merge commit via `--merge --match-head-commit`, no `--admin`; D-02 snapshot not later than `MERGED_AT` | automated (git + gh) | PR `MERGED` at `MERGE_SHA`; parents = `BASE_SHA PR_COMMIT`; merged blob = `CONFIG_BLOB`; `merge-tree origin/main HEAD` exit 0; snapshot holds #123 and #128 | same | ⬜ pending |
| 66-03-01 | 66-03 | 3 | DEP-01 | T-66-10, T-66-12 | uv update job read from the Actions API (`Dependabot Updates`), never rerun | automated (gh) | wave-2 gate; `D03_POLL1` ∈ {uv-run-seen, none-within-bound}; when seen: title `uv in /…`, created after `MERGED_AT`, `success`, `UPDATER_UV_IMAGE` names `dependabot-updater-uv` | ❌ W0 → `66-DEPENDABOT-EVIDENCE.md` (created by this task) | ⬜ pending |
| 66-03-02 | 66-03 | 3 | DEP-01 | T-66-11 | owner reads the Dependabot tab; clicks "Check for updates" only if no uv job started (D-03, D-04) | manual (`checkpoint:human-action`, `gate="blocking-human"`) | — (reply recorded verbatim by 66-03-03) | — | ⬜ pending |
| 66-03-03 | 66-03 | 3 | DEP-01, DEP-03 | T-66-10, T-66-13 | D-02 post-merge snapshot; zero owner comments/events on #123/#128 after `DECIDED_AT`; candidates are dependabot-authored `dependabot/uv/` PRs | automated (gh) | `D03_BRANCH` ∈ {config-push, check-for-updates}; `UV_RUN_ID` `success`; each candidate's branch prefix and author; owner comment/event counts = 0 | same | ⬜ pending |
| 66-04-01 | 66-04 | 4 | DEP-01 | T-66-10 | SC#1 read from a real dependabot uv PR's own head commit | automated (git + gh) | `git show --name-only SC1_SHA` holds `pyproject.toml` and `uv.lock`; branch `dependabot/uv/…`, author dependabot, base `main`; `SC1_SHA` among the PR's commits | same | ⬜ pending |
| 66-04-02 | 66-04 | 4 | DEP-04 | T-66-14, T-66-15, T-66-17 | leg 2 on an exported copy, never a checkout; no fallback workflow on failure | automated (git + gh + uv) | lock header `1`/`3`; `D05_LEG2 = PASS`; SC#1 run's `Install dependencies` `success`; `Successfully installed uv version <CI_UV_VERSION>` in its log; local lock check `exit:0`; leg-1 `uv==` lines quoted | same | ⬜ pending |
| 66-04-03 | 66-04 | 4 | DEP-01, DEP-03, DEP-04 | T-66-16 | divergences recorded, never fixed; closure only on recorded evidence | automated (grep over evidence) | closure rows DEP-01/03/04 read MET, none NOT MET; `OWNER_TAB_ANNOTATION = none`; D-06 table has six items and six verdicts | same | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `66-MAIN-PR-EVIDENCE.md`, created by 66-01 Task 1 and extended by 66-01 Task 2 and 66-02: the D-01 commits, PR, required checks, owner decision, D-02 pre-merge snapshot, and merge.
- [ ] `66-DEPENDABOT-EVIDENCE.md`, created by 66-03 Task 1 and extended by 66-03 Task 3 and 66-04: the D-03 polls and branch, the D-04 job and owner tab read, the D-02 post-merge snapshot, the D-05 legs 1 and 2, the D-06 observations, and the requirement closure.

*No test-file gap: these requirements have no automated-test equivalent by construction (they describe an external service's behaviour).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| No config-error annotation on the Dependabot tab for the `uv` manifest (SC#1 literal) | DEP-01 (D-04) | The annotation has no public API. **Planning-time correction (2026-09-12):** the version-update job list itself is API-readable, since jobs run as the Actions workflow `Dependabot Updates` (`dynamic/dependabot/dependabot-updates`). 66-03 reads the job and its log there first. | Owner opens https://github.com/YuSabo90002/typsphinx/network/updates and reports the annotation state, the last-checked text and the newest job (66-03 Task 2) |
| Trigger a version-update run if none started after the merge | DEP-01 (D-03) | No public API triggers a version-update job (dependabot-core #3080) | Owner clicks "Check for updates" on the same page, only when 66-03 Task 1 records `D03_POLL1 = none-within-bound` |
| A real `uv` PR's head commit changes `pyproject.toml` and `uv.lock` together | DEP-01 (D-04) | Only dependabot can produce the artifact. Reading it is automated in 66-04 Task 1. | `gh pr view --json commits,files` and `git show --name-only` on the fetched head |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency bounded (external waits have an explicit polling bound)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

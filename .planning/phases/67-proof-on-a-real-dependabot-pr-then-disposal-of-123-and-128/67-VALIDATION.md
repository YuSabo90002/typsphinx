---
phase: "67"
slug: "proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-12"
---

# Phase 67 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `67-RESEARCH.md` § Validation Architecture. This phase changes no product code (constraint 13),
> edits no workflow (constraint 3) and no `.github/dependabot.yml`, and adds no test file (Phase 64–66
> convention). Verification is observation-based: live `gh` / `git` / PyPI re-assertion against the
> phase evidence file's `KEY = value` lines, as in Phase 66.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + tox (unchanged; not exercised by this phase) |
| **Config file** | none — no test file is added |
| **Quick run command** | `sed -n 's/^KEY = //p' <67 evidence file>` then re-run the same `gh` / `curl` query live and compare |
| **Full suite command** | every `KEY = value` assertion accumulated in the phase evidence file(s), re-asserted live |
| **Estimated runtime** | ~1–10 seconds per assertion (single `gh` / `curl` call); no external wait unless dependabot moves #138's head |

---

## Sampling Rate

- **After every task commit:** re-run the specific `gh` / `curl` command the task's own evidence cites
- **After every plan wave:** re-run every `KEY = value` assertion accumulated so far in the phase evidence file(s)
- **Before `/gsd-verify-work`:** re-run the full live check set once more — #138's head SHA and Sphinx's PyPI-declared `docutils` cap can change between planning and execution
- **Max feedback latency:** bounded by single API calls; a moved #138 head (D-03 branch) adds a CI wait whose polling bound the plan sets

---

## Per-Task Verification Map

Seeded from `67-RESEARCH.md` § Phase Requirements → Test Map. Task IDs were filled in at planning (2026-09-12). "Automated Command" names the task's own `<automated>` block in its PLAN.md; each is a single-line live `gh` / `git` / PyPI re-assertion against the evidence file's `KEY = value` lines. Checkpoint tasks carry no automated command.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 67-01-T1 | 67-01 | 1 | DEP-02 | T-67-01, T-67-02, T-67-03 | #138's own run `34689041575` (attempt 1, `pull_request`, head = Phase 66 `SC1_SHA`): `Install dependencies` `success` and the `Run … with tox` step concluded on all eight Lint/Type/Test jobs; the job count and check-run total match the evidence | evidence-assertion (gh) | 67-01 Task 1 `<automated>`: run header, eight-job step loop, `check-runs` `total_count`, no `@dependabot` comment | ❌ W0 → `67-PROOF-EVIDENCE.md` | ⬜ pending |
| 67-01-T2 | 67-01 | 1 | DEP-02, DEP-05 | T-67-04 | a real dependabot PR on a `dependabot/uv/` branch; `SC2_BRANCH = can`; #123/#128 re-snapshotted OPEN after `DEP02_PROOF_AT`, and live `closedAt` is null or later | evidence-assertion (gh) | 67-01 Task 2 `<automated>` | ❌ W0 → `67-PROOF-EVIDENCE.md` | ⬜ pending |
| 67-02-T1 | 67-02 | 2 | DEP-05 | T-67-06, T-67-07, T-67-08, T-67-09 | #138 pre-merge gate (CLEAN, six required checks `success` on `HEAD138`), SC#3 merits (dev-extra only, FHS `ruff check .` pass, REL-12 `merge-tree` and `uv lock --check` exit 0), moved-head branch | evidence-assertion (gh, git, FHS) | 67-02 Task 1 `<automated>` | ❌ W0 → `67-RUFF-EVIDENCE.md` | ⬜ pending |
| 67-02-T2 | 67-02 | 2 | DEP-05 | T-67-05 | owner go-ahead before the one-way merge (D-03) | manual (`checkpoint:decision`) | — | n/a | ⬜ pending |
| 67-02-T3 | 67-02 | 2 | DEP-05 | T-67-05, T-67-06 | two-parent merge through `--match-head-commit`; changes only `pyproject.toml` + `uv.lock`; the milestone branch does not absorb main (D-04); REL-12 still conflict-free; idempotent on resume | evidence-assertion + one-way gh write | 67-02 Task 3 `<automated>` | ❌ W0 → `67-RUFF-EVIDENCE.md` | ⬜ pending |
| 67-03-T1 | 67-03 | 2 | DEP-05 | T-67-11, T-67-13, T-67-14 | Sphinx `docutils` cap re-measured through `packaging` over every in-range release (HALT if relaxed); #128 `pyproject.toml`-only; uv `dependency_file_not_resolvable` quoted; thread read; draft only | evidence-assertion + PyPI re-check | 67-03 Task 1 `<automated>` | ❌ W0 → `67-DOCUTILS-EVIDENCE.md` | ⬜ pending |
| 67-03-T2 | 67-03 | 2 | DEP-05 | T-67-12 | owner approves the exact #128 comment (D-05) | manual (`checkpoint:decision`) | — | n/a | ⬜ pending |
| 67-03-T3 | 67-03 | 2 | DEP-05 | T-67-11, T-67-12 | cap re-checked immediately before posting; #128 CLOSED with exactly one owner comment equal to `APPROVED_COMMENT_128`; idempotent on resume | evidence-assertion + one-way gh write | 67-03 Task 3 `<automated>` | ❌ W0 → `67-DOCUTILS-EVIDENCE.md` | ⬜ pending |
| 67-04-T1 | 67-04 | 3 | DEP-05 | T-67-16, T-67-17 | #138 MERGED first; #123 `pyproject.toml`-only; `RUFF_LINE_123` next to `RUFF_LINE_MAIN`; thread read; draft only | evidence-assertion (gh, git) | 67-04 Task 1 `<automated>` | ❌ W0 → `67-RUFF-EVIDENCE.md` | ⬜ pending |
| 67-04-T2 | 67-04 | 3 | DEP-05 | T-67-15 | owner approves the exact #123 comment (D-03) | manual (`checkpoint:decision`) | — | n/a | ⬜ pending |
| 67-04-T3 | 67-04 | 3 | DEP-05 | T-67-15, T-67-16 | #123 CLOSED after `MERGED_AT_138`, with exactly one owner comment equal to `APPROVED_COMMENT_123`; idempotent on resume | evidence-assertion + one-way gh write | 67-04 Task 3 `<automated>` | ❌ W0 → `67-RUFF-EVIDENCE.md` | ⬜ pending |
| 67-05-T1 | 67-05 | 4 | DEP-05 | T-67-18, T-67-20 | the grouped-update coverage gap stated in literal and amended readings (D-06); AMENDED blocks cited by grep, unedited; `UV_GROUP_PR_COUNT` live; all three dispositions re-asserted live | evidence-assertion (gh, grep) | 67-05 Task 1 `<automated>` | ✅ AMENDED blocks committed; ❌ W0 → `67-CLOSURE-EVIDENCE.md` | ⬜ pending |
| 67-05-T2 | 67-05 | 4 | DEP-02, DEP-05 | T-67-18, T-67-19 | ordering from timestamps (proof before decisions, merge before #123 close); #139–#142 untouched; todo left for `close_phase_todos`; closure table MET | evidence-assertion (gh, git) | 67-05 Task 2 `<automated>` | ❌ W0 → `67-CLOSURE-EVIDENCE.md` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] The phase evidence file(s) under the phase directory, created by the first plan's first task.

*No test-file gap: these requirements describe an external service's behaviour and a set of owner-gated GitHub actions; they have no automated-test equivalent by construction.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Owner go-ahead before merging #138 into `main` | DEP-05 (D-03) | One-way public action — owner decision by design | `checkpoint:decision` immediately before `gh pr merge` |
| Owner approval of the #123 and #128 close-comment wording | DEP-05 (D-03, D-05) | Outward-facing text; owner approves the final wording | `checkpoint:decision` immediately before each comment / close |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency bounded (any external wait has an explicit polling bound)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

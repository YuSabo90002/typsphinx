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

Seeded from `67-RESEARCH.md` § Phase Requirements → Test Map; task IDs are filled in after planning.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | DEP-02 | — | #138's own run `34689041575`: `Install dependencies` `success` and the test / lint / type jobs reach a conclusion | evidence-assertion (gh) | `gh run view 34689041575 --json jobs` + per-job steps, compared against the evidence file | ❌ W0 → phase evidence file | ⬜ pending |
| TBD | TBD | TBD | DEP-02 | — | the run belongs to a real `dependabot[bot]` PR on a `dependabot/uv/` branch, not a hand-made branch | evidence-assertion (gh) | `gh pr view 138 --json headRefName,author` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DEP-05 | — | #138 merged / #123 closed with a recorded merit reason, each behind an owner checkpoint | evidence-assertion + one-way gh write | `gh pr view 138 --json state,mergeCommit` / `gh pr view 123 --json state,closed` after the action | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DEP-05 | — | #128 closed with a recorded merit reason; Sphinx `docutils` cap re-measured immediately before (HALT if relaxed) | evidence-assertion + PyPI re-check + one-way gh write | `curl https://pypi.org/pypi/sphinx/json` + `gh pr view 128 --json state,closed` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DEP-05 | — | grouped-update coverage gap stated in writing (D-06), citing the `docutils` `dependency_file_not_resolvable` failure | evidence-assertion (grep) | `grep -c 'AMENDED 2026-09-12' .planning/ROADMAP.md .planning/PROJECT.md` + evidence-file section check | ✅ AMENDED blocks committed | ⬜ pending |

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

---
phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128
verified: 2026-09-12T14:30:00Z
status: passed
score: 7/7 must-haves verified
covered_files:
  - .planning/PROJECT.md
  - .planning/REQUIREMENTS.md
  - .planning/ROADMAP.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-01-PLAN.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-01-SUMMARY.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-02-PLAN.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-02-SUMMARY.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-03-PLAN.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-03-SUMMARY.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-04-PLAN.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-04-SUMMARY.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-05-PLAN.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-05-SUMMARY.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-CLOSURE-EVIDENCE.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-CONTEXT.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-DOCUTILS-EVIDENCE.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-PROOF-EVIDENCE.md
  - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-RUFF-EVIDENCE.md
covered_digest: "v1:sha256:57958e715d0f8c5888970c1aaa078c8e81876944e5e40246f6feb5e8946e3e99"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: n/a
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 67: Proof on a Real Dependabot PR, Then Disposal of #123 and #128 Verification Report

**Phase Goal:** the fix is proven where it has to be proven — on a real dependabot PR, with the
`uv sync --locked` step observed succeeding and the test / lint / type jobs observed actually
running — and only then are the two long-stale bumps (#123 ruff, #128 docutils) judged on their
merits rather than merged because CI finally went green.

**Verified:** 2026-09-12T14:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

This is an evidence-only phase. Its deliverables are one-way GitHub actions plus four evidence
files (`67-PROOF-EVIDENCE.md`, `67-RUFF-EVIDENCE.md`, `67-DOCUTILS-EVIDENCE.md`,
`67-CLOSURE-EVIDENCE.md`). Verification re-read GitHub state live via `gh` (owner account
`YuSabo90002`, repo `YuSabo90002/typsphinx`) rather than trusting the evidence files or SUMMARY.md
claims, and confirmed the milestone branch itself carries no code/config change.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | **SC#1 / DEP-02** — a real dependabot PR under `uv` has a completed run in which `uv sync --locked` succeeds and the test/lint/type jobs run to a conclusion, observed from the PR's own check runs and step logs (not a hand-made branch). | VERIFIED | Live `gh run view 34689041575` reproduces `attempt:1`, `event:pull_request`, `status:completed`, `conclusion:success`, `headSha 88088071e0…` on PR #138 (`dependabot/uv/ruff-0.16.6`, author `app/dependabot`). All 12 jobs `success`; the eight Lint/Type/Test jobs' `Install dependencies` step is `success` and each is followed by a `Run … with tox` step that concluded — verified by direct re-transcription in `67-PROOF-EVIDENCE.md` §§ D-01 proof run/Job census/Check runs/Per-step reads, cross-checked live in this verification session. Zero `@dependabot` comments; the sole PR comment is dependabot's automated label notice. |
| 2 | **SC#2** — whether a `uv` PR can open while a `pip` PR for the same dependency is still open is measured before either #123/#128 is touched; any pre-proof close is recorded as mechanical, not disposal. | VERIFIED | `SC2_BRANCH = can`: #138 (`createdAt 2026-09-12T10:39:49Z`) opened while #123 (`createdAt 2026-07-27`) and #128 (`createdAt 2026-08-03`) were both open — confirmed live. `MECHANICAL_CLOSE = none`: `67-PROOF-EVIDENCE.md`'s post-proof re-snapshot (`SNAP_123_AT`/`SNAP_128_AT`, both after `DEP02_PROOF_AT = 2026-09-12T13:18:08Z`) shows both PRs still OPEN and unchanged. Live re-check confirms both PRs were only closed later (13:38:31Z / 13:52:17Z), by the owner account, after the proof — never a mechanical unblock. |
| 3 | **SC#3 / DEP-05 (merit)** — each bump (#123 ruff, #128 docutils, or its `uv` successor) reaches a recorded decision, merged or closed with a stated reason; "CI is finally green" is explicitly not treated as the merit, and the ruff↔NIX-01 interaction is part of the judgement. | VERIFIED | Live: #138 MERGED (`cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a`, two-parent commit, parents `293f0c26…` [main tip] and `88088071…` [PR head]); #123 CLOSED with owner comment "Superseded by #138." (byte-identical to `APPROVED_COMMENT_123`); #128 CLOSED with owner comment "Sphinx 9.1.0 caps docutils<0.23,>=0.21, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap." (byte-identical to `APPROVED_COMMENT_128`, and independently re-confirmed against live PyPI: Sphinx latest is still 9.1.0 with `docutils<0.23,>=0.21`). `67-RUFF-EVIDENCE.md` records dev-extra-only scope, an FHS-run `ruff check .` at 0.16.6 passing clean on the milestone tip, and the NIX-01/D-04 divergence statement (milestone worktree shim stays at 0.15.20 until REL-12) rather than silently absorbing `main`. `67-DOCUTILS-EVIDENCE.md` records #128's CI as red specifically at the `uv sync --extra dev --locked` step (lockfile mismatch), and the `uv` ecosystem's own attempt at the same bump failing with `dependency_file_not_resolvable` — the decision basis is these merits, not CI color. |
| 4 | **SC#4 (literal + AMENDED)** — the grouped-update coverage gap is recorded explicitly, in both its literal ROADMAP reading and the owner-approved AMENDED reading, reported separately. | VERIFIED | `67-CLOSURE-EVIDENCE.md` § "SC#4 grouped-update coverage gap (D-06)" carries both readings as separately labeled paragraphs. Literal: this milestone's proof does not cover the `sphinx-typst-stack` grouped path under `uv` (a future grouped resolution failure is an uncovered case, not a regression). Amended: SC#4's own premise ("neither is grouped") is false — #128 **is** a group PR (live-confirmed: title contains "sphinx-typst-stack group", branch `dependabot/pip/sphinx-typst-stack-12b5b89b5a`) — but the conclusion is unchanged, since no `uv`-ecosystem `sphinx-typst-stack` PR has ever existed (`UV_GROUP_PR_COUNT = 0`, live-reconfirmed by this verification: `gh pr list --author app/dependabot` returns 5 total PRs, none named `sphinx-typst-stack`) and the group's `docutils` member failed with `dependency_file_not_resolvable` (a live instance of the "unresolvable dependency graph" case). The `AMENDED 2026-09-12 (Phase 67 discuss, owner-approved)` blocks exist verbatim in both `ROADMAP.md:586-596` and `PROJECT.md:126-131`, confirmed by direct read in this verification; neither file carries any other Phase-67-caused edit (see Artifact/Data-Flow section below). |
| 5 | **Milestone-branch isolation constraint** — nothing under `typsphinx/`, `.github/`, `pyproject.toml`, `uv.lock` changes on the milestone branch; the merge to `main` is a separate, one-way action that the milestone branch does not absorb (D-04). | VERIFIED | `git diff --name-only 7801f065^..HEAD -- . ':!.planning/'` returns empty (confirmed in this verification session). `git merge-base --is-ancestor cf3305ce… HEAD` returns false (`cf3305ce` is NOT an ancestor of the milestone branch's tip) — the merge commit lives only on `main` (`origin/main` at `cf3305ce` after a fresh `git fetch`), not absorbed into the milestone branch. |
| 6 | **DEP-02 requirement text** ("on a real dependabot PR, the `uv sync --locked` step succeeds and the test/lint/type jobs actually run — observed, not inferred from a hand-made branch") is satisfied. | VERIFIED | Same evidence as Truth 1; `DEP02_VERDICT = MET` recorded in `67-PROOF-EVIDENCE.md` and re-asserted live in `67-CLOSURE-EVIDENCE.md` (`A6701_STATUS = held`, re-confirmed again in this verification session: run `34689041575` still resolves `attempt:1`/`conclusion:success` at `headSha 88088071…`). |
| 7 | **DEP-05 requirement text** ("#123 and #128 are disposed of on their merits after DEP-02, with the grouped-update coverage gap explicitly recorded rather than passed over") is satisfied. | VERIFIED | Combination of Truths 2, 3 and 4. Ordering also independently verified: `DEP02_PROOF_AT` (13:18:08Z) precedes `DECIDED_AT_138` (13:36:41Z) and `DECIDED_AT_128` (13:36:46Z); `MERGED_AT_138` (13:37:03Z) precedes `CLOSED_AT_123` (13:52:17Z) — confirmed by direct string comparison of the recorded timestamps, consistent with the live close/merge timestamps re-read via `gh` in this session (`128` closedAt `13:38:31Z`, `123` closedAt `13:52:17Z`, `138` mergedAt `13:37:03Z`). |

**Score:** 7/7 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `67-PROOF-EVIDENCE.md` | D-01/D-02 transcription, `DEP02_VERDICT` | VERIFIED | Present, contains `DEP02_VERDICT = MET`; every key cross-checked live (run header, job census, check-runs count, per-step reads, PR createdAt values, re-snapshot). |
| `67-RUFF-EVIDENCE.md` | #138 pre-merge gate, SC#3 merits, merge record, #123 disposition | VERIFIED | Present; merge commit `cf3305ce` confirmed live as MERGED with the recorded parents; #123 CLOSED with the recorded comment, confirmed live. |
| `67-DOCUTILS-EVIDENCE.md` | D-05 PyPI re-measurement, #128 merits, close record | VERIFIED | Present; #128 CLOSED with the recorded comment, confirmed live; Sphinx docutils cap independently re-measured live against PyPI JSON in this session and matches `D05_CAP_RELAXED = no`. |
| `67-CLOSURE-EVIDENCE.md` | SC#4 dual reading, ordering proof, requirement closure table | VERIFIED | Present; both AMENDED blocks confirmed to exist verbatim in ROADMAP.md/PROJECT.md; deferred PRs #139-142 independently re-confirmed to carry zero owner comments/events in this session. |
| PR #138 → `main` | merged, two-parent commit | VERIFIED | Live: MERGED, merge commit `cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a`, parents `293f0c2684…` and `88088071e0…` (two-parent, confirming a true merge commit, not a squash/rebase). |
| PR #123 | closed, superseded | VERIFIED | Live: CLOSED, closedAt `2026-09-12T13:52:17Z`, exactly one owner comment ("Superseded by #138.\n"), closed-event actor `YuSabo90002`. |
| PR #128 | closed, merits reason | VERIFIED | Live: CLOSED, closedAt `2026-09-12T13:38:31Z`, exactly one owner comment (matches `APPROVED_COMMENT_128` verbatim), closed-event actor `YuSabo90002`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `67-01-PLAN.md`'s `DEP02_VERDICT` gate | `67-02`/`67-03` dispositions | plan `depends_on: ["67-01"]`, evidence-file precondition reads | WIRED | Both 67-02 and 67-03 declare `depends_on: ["67-01"]`; both evidence files quote `67-PROOF-EVIDENCE.md`'s `DEP02_VERDICT = MET` before any action, matching D-02's binding order. |
| `67-02`'s `OWNER_DECISION_138 = merge` | `67-04`'s #123 close | plan `depends_on: ["67-02"]`, wave-2 gate read | WIRED | `67-04-PLAN.md` declares `depends_on: ["67-02"]`; `67-RUFF-EVIDENCE.md`'s #123 disposition section reads the wave-2 gate live before closing #123, and `CLOSED_AT_123` (13:52:17Z) postdates `MERGED_AT_138` (13:37:03Z) as required by D-03's ordering. |
| Owner `checkpoint:decision` reply | posted PR comment text | `APPROVED_COMMENT_*` keys, `gh pr comment --body-file` | WIRED | Each of #123/#128's posted comment bodies is byte-identical (confirmed live) to the `APPROVED_COMMENT_*` value recorded in the evidence file before posting — the documented `--body-file` fallback (used because the sandbox refused the plan's literal `--comment "$(sed …)"` form) preserves the "never retyped" mitigation. |
| SC#4 amended reading | `ROADMAP.md`/`PROJECT.md` AMENDED blocks | `grep -n`, unedited | WIRED | Both files carry the exact `AMENDED 2026-09-12 (Phase 67 discuss, owner-approved)` block text cited in `67-CLOSURE-EVIDENCE.md`; `git diff` confirms Phase 67 touched neither file's content beyond what pre-existed at `BASE_67_05`. |

### Data-Flow Trace (Level 4)

Not applicable in the conventional sense (no rendered UI/data pipeline); the phase's "data" is
GitHub PR/run state. Every key value in the evidence files traces to a live `gh`/PyPI JSON read
recorded alongside its command, and this verification independently re-ran the load-bearing reads
(run header, PR states/comments, merge-commit parents, ancestor check, PyPI JSON, deferred-PR
comment counts) rather than trusting the transcriptions — all reproduced identically.

### Behavioral Spot-Checks

Not applicable — this is a GitHub-state evidence phase, not runnable application code. Live `gh`
API re-reads (Step 7b equivalent) were performed directly against production GitHub state instead,
documented above.

### Probe Execution

No `scripts/*/tests/probe-*.sh` declared or discovered for this phase; skipped.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| DEP-02 | 67-01 (closes), 67-05 (re-asserts) | On a real dependabot PR, `uv sync --locked` succeeds and test/lint/type jobs run to a conclusion — observed. | SATISFIED | `67-PROOF-EVIDENCE.md` `DEP02_VERDICT = MET`; independently re-verified live in this session against run `34689041575`. |
| DEP-05 | 67-02, 67-03, 67-04 (dispose), 67-05 (closes) | #123 and #128 disposed of on their merits after DEP-02, with the grouped-update coverage gap explicitly recorded. | SATISFIED | #138 merged (merits recorded), #123 closed as superseded (merits recorded), #128 closed on the docutils-cap merit (re-measured twice), SC#4 gap recorded in both literal and amended readings — all independently confirmed live. |

`.planning/REQUIREMENTS.md` DEP-02/DEP-05 checkboxes remain `[ ]` as of this verification — expected
per the orchestrator's note: they flip at phase completion (run after this verification), matching
Phase 66's precedent. This is not a gap.

No orphaned requirements: `.planning/REQUIREMENTS.md`'s phase-mapping table lists only DEP-02 and
DEP-05 against "Phase 67", both accounted for above.

### Anti-Patterns Found

None. This is an evidence-only phase (no code files created or modified); the debt-marker/stub-code
scan is not applicable. The `git diff --name-only 7801f065^..HEAD -- . ':!.planning/'` check (empty
result) independently confirms no code, workflow, or config file was touched — satisfying the
phase's own "nothing under `typsphinx/`, `.github/`, `pyproject.toml`, `uv.lock`" constraint.

One item worth naming for the record rather than as a defect: 67-03 and 67-04 both deviated from
their plans' literal `gh pr close <n> --comment "$(sed ...)"` invocation because the execution
sandbox refused command-substitution combined with `gh`. Both used the plan's own pre-documented
`gh pr comment --body-file` + `gh pr close` fallback, and both post-close records confirm the
posted comment body is byte-identical to the owner-approved text. This is a mechanically
equivalent path, not a scope or content deviation, and is fully disclosed in both SUMMARY.md files.

### Human Verification Required

None. Every must-have is a GitHub-state fact directly re-readable via `gh`/PyPI, and every one was
independently re-confirmed live in this verification session (not merely re-read from the evidence
files).

### Gaps Summary

No gaps. All four evidence files' claims were independently reproduced against live GitHub/PyPI
state in this verification session:
- Run `34689041575` on PR #138: `attempt:1`, `completed`/`success`, `pull_request` event, all 12
  jobs `success`.
- PR #138: MERGED, two-parent merge commit `cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a` (parents
  `293f0c2684…`/`88088071e0…`), NOT an ancestor of the milestone branch tip.
- PR #123: CLOSED, exactly one owner comment ("Superseded by #138.\n"), closed by `YuSabo90002`,
  head branch subsequently deleted by `dependabot[bot]`.
- PR #128: CLOSED, exactly one owner comment (the docutils-cap reason, byte-identical to
  `APPROVED_COMMENT_128`), closed by `YuSabo90002`, head branch subsequently deleted by
  `dependabot[bot]`.
- PRs #139-142: zero owner comments, zero owner timeline events on any of them.
- Sphinx PyPI JSON: latest `9.1.0`, `requires_dist` still `docutils<0.23,>=0.21` — the D-05 merit
  premise is unchanged as of this verification.
- `AMENDED 2026-09-12 (Phase 67 discuss, owner-approved)` blocks present verbatim in both
  `ROADMAP.md` and `PROJECT.md`.
- Milestone branch diff against its own phase-start commit, restricted to non-`.planning/` paths,
  is empty.

The phase goal is achieved: DEP-02 was proven on a real dependabot PR's own CI run without any
rerun or hand-made branch, and only after that proof were #123 and #128 (and #138, the `uv`
successor) disposed of on stated merits rather than on CI going green — with the grouped-update
coverage gap written down in both its literal and its owner-amended reading.

---

_Verified: 2026-09-12T14:30:00Z_
_Verifier: Claude (gsd-verifier)_

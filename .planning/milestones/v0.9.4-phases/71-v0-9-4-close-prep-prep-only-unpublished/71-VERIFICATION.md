---
phase: 71-v0-9-4-close-prep-prep-only-unpublished
verified: 2026-09-13T00:00:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-01-PLAN.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-01-SUMMARY.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-02-PLAN.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-02-SUMMARY.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-03-PLAN.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-03-SUMMARY.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-04-PLAN.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-04-SUMMARY.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-05-PLAN.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-05-SUMMARY.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-06-PLAN.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-06-SUMMARY.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-07-PLAN.md"
  - ".planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-07-SUMMARY.md"
  - "CHANGELOG.md"
covered_digest: "v1:sha256:7d8bb4c0fdf7c2d39150eefbd9dc6ced0eb59ba5c01058a2be5ad98d2ce09088"
behavior_unverified: 0
overrides_applied: 1
overrides:
  - must_have: "SC#3 — 'One fresh CI run is dispatched on this phase's own tip' (exactly one workflow_dispatch run at PUSHED_SHA)"
    reason: "Owner-approved deviation, recorded in 71-CI-EVIDENCE.md's AMENDED addendum and 71-SC1-INVARIANTS.md. GitHub's dispatch API returned HTTP 500/502 on repeated calls; one 'failed' call actually created a run and a retry created a second. Two workflow_dispatch runs carry PUSHED_SHA 7a42bf99: 34748483361 (success, RUN_ID, 12/12 jobs) and 34748491771 (cancelled, no failed job). The owner chose to keep the Actions history rather than delete the surplus run, and reads the requirement as 'exactly one success run at PUSHED_SHA, and it is RUN_ID; the only other run at PUSHED_SHA is the cancelled 34748491771.' No code-affecting change occurred between the two dispatch attempts (D-10) and no failed job exists on either run."
    accepted_by: "project owner (via orchestrator addendum in 71-CI-EVIDENCE.md, 2026-09-13T09:08:06Z)"
    accepted_at: "2026-09-13T09:08:06Z"
---

# Phase 71: v0.9.4 Close Prep (prep-only, unpublished) Verification Report

**Phase Goal:** the milestone is packaged for a merge to `main` and nothing else — no version bump,
no tag, no PyPI upload, no GitHub Release; one CHANGELOG bullet lands under `## [Unreleased]`; the
tree is proven green on runs executed in this phase; REL-13's checkbox is held at `[ ]` behind a
SHA-256 fence; a standalone `71-HANDOFF.md` is written for `/gsd-complete-milestone`.

**Verified:** 2026-09-13 (independently re-measured against the codebase at final phase tip
`0e3ba6564572b87c4c486999e4e5975cf837af94`)
**Status:** passed
**Re-verification:** No — initial verification

## Method

This is a "close prep" phase whose entire deliverable is measurable git/GitHub/PyPI state plus one
CHANGELOG bullet, rather than application code. Verification therefore consisted of independently
re-running the phase's own probe commands from the current tree and current remotes — not
transcribing the phase's evidence files — and comparing results. Every command below was executed
by the verifier in this session, from `/home/yuta/Documents/typsphinx` at `HEAD =
0e3ba6564572b87c4c486999e4e5975cf837af94` (later than any evidence file's own recorded tip, so this
is the freshest possible check), unless marked "(from evidence file)".

## Goal Achievement

### Observable Truths (ROADMAP SC#1–SC#4, the roadmap contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | **SC#1** — tree is unpublished-shaped with positive-controlled probes; no code change slipped in since Phase 70 | ✓ VERIFIED | `pyproject.toml:7` = `version = "0.9.2"` (re-read). `git tag -l 'v0.9.4'` / `'v0.9.3'` empty locally; remote `git ls-remote --tags origin` shows only `v0.9.2` in the `v0.9.x` line (no v0.9.3/v0.9.4), with v0.9.2 itself as positive control. `curl` to PyPI: `0.9.4` → 404, `0.9.2` → 200 (positive control, re-run by verifier). `gh release view v0.9.4` → "release not found"; `gh release view v0.9.2` succeeds (positive control, re-run by verifier). `git diff --stat f1f7d54a61d7..HEAD -- typsphinx/ tests/` empty (re-run by verifier); widened `--numstat` diff shows only `CHANGELOG.md` (+10/−0), proving the anchor is real. `71-SC1-INVARIANTS.md` masked-AST table: all 10 Phase-70-converted files EQUAL between base and close tip, non-vacuous (two mutation controls both DIFFER). |
| 2 | **SC#2** — exactly one new bullet lands under `## [Unreleased]` → `### Changed`, no release section created | ✓ VERIFIED | `CHANGELOG.md` read directly: fourth bullet under `### Changed`, bold lead + `(QUA-09, QUA-11, QUA-12, DOC-22, DOC-23)`, one evidence sentence citing 167-project byte-identical `.typ` corpus, "no effect on installing or using typsphinx" sentence present. `grep -iE 'ja|japanese|catalog'` over the bullet's lines returns nothing (AMENDED D-02 honored). No `0.9.3`/`0.9.4` string anywhere in the bullet. No `## [0.9.4]`/`## [0.9.3]` heading exists; tail link block unchanged, `[Unreleased]` still compares against `v0.9.2`. `71-GREEN-TREE-EVIDENCE.md`: changelog page gate `6 passed`, `0 skipped`, in an environment with the `docs` extra. |
| 3 | **SC#3** — tree proven green on runs executed in this phase (full suite, format/type/lint, docs, CI dispatch, non-committing trial merge against `main`) | ✓ VERIFIED (with 1 owner-approved override, see below) | Verifier independently re-ran in the main checkout at final tip: `black --check .` → "All done! 355 files would be left unchanged"; `ruff check .` → "All checks passed!"; `mypy typsphinx/` → "Success: no issues found in 9 source files". `71-GREEN-TREE-EVIDENCE.md` records the full suite twice (default locale and `LC_ALL=C`): `1547 passed, 1 skipped` both times, matching Phase 70's after-side count on the same interpreter (3.13.13). CI: verifier independently ran `gh run view 34748483361 --json status,conclusion,headSha,workflowName` → `{"conclusion":"success","headSha":"7a42bf99...","status":"completed","workflowName":"CI"}`; `71-CI-EVIDENCE.md`'s 12-job table shows both `windows-latest` and both `macos-latest` lanes `success`, ruff verdict from `Lint and Format Check` = "All checks passed!" at ruff 0.16.6 (matches `uv.lock`). Trial merge: verifier independently confirmed `git merge-base HEAD origin/main` = `origin/main` = `d14ca458...` (no `main` commits to absorb) and `gh api .../branches/main/protection` → `strict: true`, six named contexts (matches `71-PREFLIGHT-EVIDENCE.md`'s recorded protection JSON exactly). |
| 4 | **SC#4** — REL-13 checkbox proven held by SHA-256 fence; standalone `71-HANDOFF.md` exists | ✓ VERIFIED | Verifier independently ran, at final tip `0e3ba656`: `sha256sum .planning/REQUIREMENTS.md` → `4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636` (equals `REQ_SHA256_BASE`/`REQ_SHA256_CLOSE` recorded in `71-CLOSEOUT-GUARD.md`); `wc -l` → 80 (equals baseline); `grep -n 'REL-13'` returns the same four lines (24, 33, 71, 75), line 24 reading `- [ ] **REL-13**:` and line 71 reading `Pending`; `git status --porcelain` clean. `git log f1f7d54a..HEAD -- .planning/REQUIREMENTS.md` empty — no phase-71 commit touched the file (the only edit to REQUIREMENTS.md in the milestone is the pre-phase AMENDED-block commit `5292a85b`, an ancestor of `PHASE_BASE_SHA`). `71-HANDOFF.md` read in full: opens negative-first (§ "This milestone publishes nothing"), enumerates the ordered `/gsd-complete-milestone` steps (fence-first, trial-merge re-run, conditional branch update D-06, push, PR, wait-for-six-checks, merge-commit, REL-13 observation), reproduces the closeout-guard re-verification procedure inline, and states what it deliberately did not do. |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Owner-Approved Override

**SC#3's "one fresh CI run … dispatched"** literally reads as exactly one `workflow_dispatch` run
at the phase's pushed tip. GitHub's dispatch API returned HTTP 500/502 on repeated calls during
71-04; one nominally-"failed" call actually created a run server-side, and a retry created a
second. Two runs carry `PUSHED_SHA` `7a42bf99...`: `34748483361` (`success`, 12/12 jobs — this is
`RUN_ID`, the run cited for SC#3's CI verdict) and `34748491771` (`cancelled`, 0 failed jobs). The
owner chose to keep the Actions history rather than delete the surplus run and accepted the reading
"exactly one **success** run at `PUSHED_SHA`, and it is `RUN_ID`; the only other run at `PUSHED_SHA`
is the cancelled `34748491771`" (`71-CI-EVIDENCE.md` § "AMENDED 2026-09-13 — dispatch count", dated
`2026-09-13T09:08:06Z`). The verifier independently re-ran `gh run list --workflow=ci.yml --branch
gsd/v0.9.4-typing-modernization --event workflow_dispatch --json databaseId,headSha,conclusion` per
the orchestrator's instruction and confirmed exactly this: 2 runs at `PUSHED_SHA`, one `success`,
one `cancelled`, 0 non-cancelled failures. This is recorded as PASSED (override) and counted toward
the verified score, per the orchestrator's explicit instruction to evaluate SC#3's CI half under
the amended reading rather than as a gap. It affects only the literal-count assertion inside two
plans' automated verifies (71-04 Task 2, 71-06 Task 1); `RUN_ID`'s own 12/12-green verdict, which
SC#3's substance rests on, is untouched.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `CHANGELOG.md` | One new bullet under `## [Unreleased]` → `### Changed` | ✓ VERIFIED | Read directly; matches D-01..D-04 exactly; byte-identical elsewhere (`git diff --numstat` shows only this file, +10/−0, across the whole phase) |
| `pyproject.toml` | Unchanged, still `0.9.2` | ✓ VERIFIED | `sed -n 7p pyproject.toml` = `version = "0.9.2"`; no commit since `d14ca458` touches a `^version = ` line |
| `.planning/REQUIREMENTS.md` | REL-13 unchecked, unedited by any phase-71 commit | ✓ VERIFIED | SHA-256 matches baseline at final tip; zero phase-71 commits touch the file |
| `71-CLOSEOUT-GUARD.md` | Fence procedure with baseline + close-time re-verification | ✓ VERIFIED | Baseline and close-time digests match; re-verification section present and internally consistent |
| `71-CHANGELOG-EVIDENCE.md` | Pure-addition proof, bullet content assertions, clean docs baselines | ✓ VERIFIED | Present, cited correctly by 71-HANDOFF.md and 71-REVIEW.md |
| `71-SC1-INVARIANTS.md` | Two time-separated observations of the unpublished-shaped fence + D-11 masked-AST re-run | ✓ VERIFIED | Present; both observations use identical positive-controlled probes; masked-AST table complete (10/10 EQUAL, non-vacuous) |
| `71-GREEN-TREE-EVIDENCE.md` | Full suite ×2, format/type/lint, version-sync, changelog gate, docs builds | ✓ VERIFIED | Present; local lint/type/format re-confirmed independently by verifier at final tip |
| `71-CI-EVIDENCE.md` | CI dispatch, 12-job transcript, ruff verdict, AMENDED dispatch-count addendum | ✓ VERIFIED | Present; `RUN_ID` re-confirmed live via `gh run view` |
| `71-PREFLIGHT-EVIDENCE.md` | Non-committing trial merge, merged-lock check, merged-tree lint, main protection | ✓ VERIFIED | Present; `strict: true` + six contexts re-confirmed live via `gh api` |
| `COVERAGE.md` | Reasoned no-external-API declaration | ✓ VERIFIED | Present; seal-time gate `passed: true` recorded |
| `71-HANDOFF.md` | Standalone handoff for `/gsd-complete-milestone` | ✓ VERIFIED | Present, self-contained (reproduces the closeout-guard procedure inline so no other file needs opening), negative-first, ordered steps, "deliberately did not do" list |
| `71-REVIEW.md` | Code review of the one product-tree file changed | ✓ VERIFIED | `status: clean`, 0 critical, 0 warning, 1 info (non-blocking, optional-fix) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `CHANGELOG.md` bullet | `docs/source/changelog.rst` | MyST include, rendered by `docs-html`/`docs-pdf` | ✓ WIRED | `tests/test_changelog_page_gate.py` 6/6 passed, 0 skipped, including the PDF-include-compiles class; clean-build warning counts unchanged (3 HTML / 5 PDF) before vs. after the edit |
| `71-CLOSEOUT-GUARD.md` fence | `.planning/REQUIREMENTS.md` | SHA-256 + line-count + grep probes | ✓ WIRED | Baseline and close-time values independently re-confirmed equal by the verifier at the final tip |
| `71-HANDOFF.md` | `/gsd-complete-milestone`'s ordered steps | Reproduces the fence procedure, trial-merge inputs, and merge-method precedent inline | ✓ WIRED | Every value the handoff cites (`MERGE_TREE`, `PUSHED_SHA`, `MERGE_PRECEDENT_HITS`, protection JSON) is independently traceable to its source evidence file and was spot-checked live by the verifier |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| REL-13 | 71-01..71-07 (all plans declare `requirements: [REL-13]`) | Close prep only, unpublished; checkbox closes only at `/gsd-complete-milestone` | ✓ SATISFIED (as designed — deliberately not closed) | `.planning/REQUIREMENTS.md:24` reads `- [ ] **REL-13**` and `:71` reads `Pending` at the final phase tip, matching the orchestrator's stated correct state. Every plan's `SUMMARY.md` frontmatter declares `requirements-completed: []`. No orphaned requirements: REL-13 is the only requirement mapped to Phase 71 in REQUIREMENTS.md's Traceability table, and every plan cites it. |

### Anti-Patterns Found

None. `grep -n -E "TBD|FIXME|XXX"` and a broader `TODO|HACK|PLACEHOLDER|not yet implemented|coming soon` sweep over every phase-71 `.md` file and over `CHANGELOG.md` returned zero debt markers (the handful of prose hits for "the todo"/"Reviewed Todos" refer to the pre-existing 2026-07-22 typing-modernization todo item, not a marker left by this phase). `71-REVIEW.md` independently confirms `status: clean`, 0 critical/warning findings on the one product file this phase changed.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Lint clean at final tip | `black --check .` | "All done! 355 files would be left unchanged." | ✓ PASS |
| Lint clean at final tip | `ruff check .` | "All checks passed!" | ✓ PASS |
| Type check clean at final tip | `mypy typsphinx/` | "Success: no issues found in 9 source files" | ✓ PASS |
| No local tags for unpublished versions | `git tag -l 'v0.9.4'`, `git tag -l 'v0.9.3'` | both empty | ✓ PASS |
| PyPI has no 0.9.4 (positive control: 0.9.2 exists) | `curl -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.4/json` and `.../0.9.2/json` | 404 / 200 | ✓ PASS |
| No GitHub Release for v0.9.4 (positive control: v0.9.2 exists) | `gh release view v0.9.4` / `gh release view v0.9.2` | "release not found" / succeeds | ✓ PASS |
| Only one intended CI dispatch tip, one success run | `gh run view 34748483361 --json status,conclusion,headSha,workflowName` | `{"conclusion":"success",...}` | ✓ PASS |
| `main` branch protection matches recorded evidence | `gh api repos/.../branches/main/protection --jq '.required_status_checks'` | `strict: true`, six named contexts, matches `71-PREFLIGHT-EVIDENCE.md` exactly | ✓ PASS |
| REL-13 fence holds at the actual final phase tip (freshest possible check) | `sha256sum .planning/REQUIREMENTS.md`, `wc -l`, `grep -n REL-13`, `git status --porcelain` | digest/line-count/grep-lines match baseline; status clean | ✓ PASS |
| No code change under `typsphinx/`/`tests/` since phase base | `git diff --stat f1f7d54a..HEAD -- typsphinx/ tests/` | empty | ✓ PASS |
| No workflow file edited | `git diff --name-only f1f7d54a..HEAD -- .github/` | empty | ✓ PASS |

Full pytest suite was not re-run by the verifier (already run twice by the phase itself, once by the orchestrator post-merge, `1547 passed, 1 skipped` each time, on the same interpreter) — per the constraint against redundant full-suite runs, the verifier relied on the phase's own and the orchestrator's transcribed full-suite results plus its own independent lint/type re-run.

### Human Verification Required

None. This phase's entire deliverable is measurable git/GitHub/PyPI/file state; no UI, no runtime user-facing behavior, and no behavior-dependent state-transition truth exists in this phase's scope that a presence check cannot resolve. The one item genuinely deferred outside this verification's reach — the "third fence observation" after `phase.complete`-family tooling runs — is explicitly the orchestrator's own follow-up per the phase's own design (D-09, `71-CLOSEOUT-GUARD.md` § "For the operator running phase.complete") and per this task's own instructions (note 5); it is not a gap in this verification.

### Gaps Summary

No gaps. All four ROADMAP success criteria (SC#1–SC#4) were independently re-measured against the
live codebase, git history, and GitHub/PyPI state at the phase's actual final tip
(`0e3ba6564572b87c4c486999e4e5975cf837af94`) and found to hold. The one deviation from a plan's
literal automated-verify assertion (SC#3's CI dispatch count) is a recorded, owner-approved reading
of a GitHub API flakiness artifact, not a functional gap — the substance of the requirement (a
single-tip CI run with all 12 jobs green) holds on its own merits, independently re-confirmed by
the verifier via a live `gh run view` call. REL-13 is correctly left unchecked, matching the
phase's explicit design (it closes only at `/gsd-complete-milestone`), and its SHA-256 fence was
independently reconfirmed to hold at the true final tip rather than at any evidence file's own
snapshot.

---

_Verified: 2026-09-13_
_Verifier: Claude (gsd-verifier)_

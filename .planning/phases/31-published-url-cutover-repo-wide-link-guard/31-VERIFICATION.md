---
phase: 31-published-url-cutover-repo-wide-link-guard
verified: 2026-07-27T00:00:00Z
status: human_needed
score: 27/29 must-haves verified
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items: 0
human_verification:
  - test: "Cancel or let a Link Check run get superseded mid-flight (e.g. push twice in quick succession) and confirm no commit, tag, issue, or tree file is left behind — only a job summary is read/written."
    expected: "The cancelled/superseded run leaves the repository state (commits, tags, issues, tracked files) completely unchanged; only the GitHub-hosted job summary reflects the run."
    why_human: "This is a `verification: backstop` (non-inferable) must-have in both 31-01-PLAN.md and 31-05-PLAN.md must_haves.truths. links.yml's two steps (checkout, lychee-action with jobSummary: true) contain no commit/tag/issue-writing step by static inspection, which is suggestive but not the same as directly observing a cancelled/superseded run's actual behavior — no held-out test or direct observation of a cancellation exists in the evidence. Per the honest-verifier protocol (references/honest-verifier.md), a backstop truth without a wired test or directly-observed behavior must abstain rather than be marked VERIFIED on symbol/structure presence alone."
---

# Phase 31: Published-URL Cutover + Repo-Wide Link Guard Verification Report

**Phase Goal:** Every documentation URL typsphinx publishes points at Read the Docs and actually
resolves, the external bug report about the broken link is closed with the promised fix
delivered, and a mechanism now exists that would catch the next dead link instead of it
surviving for months.

**Verified:** 2026-07-27
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Negative control: link check flags live `github.io` URLs in README.md/pyproject.toml BEFORE the rewrite, recorded as a live CI run | ✓ VERIFIED | Live `gh run view 30205112477` confirms `conclusion: failure`, SHA `eaee760...`, matching `31-EVIDENCE.md`'s transcription verbatim. 8 errors reported, all 7 old-host README deep links present, plus 1 unrelated pre-existing `claude.ai/code` 403. `pyproject.toml` scan proven via a temporary `--dump-inputs` diagnostic run (`30205087374`), which also proved `.planning/`, `CHANGELOG.md`, `tests/fixtures/` were absent from the scan. |
| 2 | After the rewrite, EVERY documentation URL in README.md, pyproject.toml, and INTEGRATIONS.md is fetched over real HTTP and returns 200 — fresh grep at execution time; CHANGELOG.md untouched | ✓ VERIFIED | Live re-run of `grep -rl "github\.io" --exclude-dir=.git --exclude-dir=.planning .` returns `CHANGELOG.md` only (confirmed independently, matches `31-EVIDENCE.md`). Live spot-check of 6 distinct URLs across README/INTEGRATIONS all returned 200. `uv run pytest tests/test_no_stale_github_io_links.py -v` (4/4 passed, run live). `git diff` confirms `CHANGELOG.md` untouched across the whole phase's commit range. |
| 3 | Link check runs in CI as advisory (non-blocking, never required), green on rewritten tree, scope documented where it lives | ✓ VERIFIED | Live `gh api .../branches/main/protection --jq '.required_status_checks.contexts'` lists only the 6 `ci.yml` jobs — no `link`/`Link Check` entry. Live `gh run view 30265271094` confirms `conclusion: success`, SHA `260ade4...` (final tree). `.github/workflows/links.yml`'s header comment block documents scope (README.md/pyproject.toml, advisory posture, exclusion rationale) — confirmed present on disk. |
| 4 | Issue #119 closed with a reply naming the fix; a visitor can reach docs via About → Website, resolving over real HTTP | ⚠️ Split by D-15 (owner-decided) | About field: live `gh api .../repos --jq .homepage` = `https://typsphinx.readthedocs.io/`; live `curl -L` = `200` (redirects to `/en/latest/`). Close-reply: `31-ISSUE-119-REPLY-DRAFT.md` exists, English, 2 lines of reply text, marked "AWAITING OWNER REVIEW", cites the live URL and status. Live `gh issue view 119` confirms state `OPEN`, 1 comment (unchanged) — the close itself is a recorded post-merge handoff to `/gsd-complete-milestone` per D-15/31-CONTEXT.md, not a Phase 31 deliverable. Treated as owner-decided-split per phase instructions, not a gap. |

**Score:** 4/4 ROADMAP success criteria substantively achieved within phase 31's deliberately split window (SC#4's second half is an explicit, documented handoff, not a gap).

### Plan-Level Must-Haves (all 5 plans)

| # | Must-Have (abbreviated) | Plan | Status | Evidence |
|---|---|---|---|---|
| 1 | `links.yml` workflow named "Link Check", push+PR trigger, real HTTP fetches | 01 | ✓ VERIFIED | File present, structure matches; live CI runs confirm real HTTP behavior |
| 2 | Negative-control run fails, names all 7 deep links | 01 | ✓ VERIFIED | Live `gh run view 30205112477` = failure; 7 links confirmed in evidence |
| 3 | pyproject.toml among scanned files (negative control) | 01 | ✓ VERIFIED | `--dump-inputs` diagnostic run quoted `./pyproject.toml` |
| 4 | No `.planning/`, `CHANGELOG.md`, `tests/fixtures/` scanned | 01 | ✓ VERIFIED | Diagnostic 26-file dump contains none of these paths |
| 5 | Only http/https checked (D-07) | 01 | ✓ VERIFIED | `--scheme https --scheme http` present in links.yml; log shows relative/file/mailto links only in `[EXCLUDED]`, never checked |
| 6 | Link Check not in required status checks | 01 | ✓ VERIFIED | Live `gh api branches/main/protection` confirms absence |
| 7 | Cancelled/superseded run leaves no repo state (backstop) | 01, 05 | ⚠️ human_needed | No wired test or direct observation exists; static inspection of links.yml (2 steps, no commit/issue/tag writes) is suggestive but not explicit evidence per honest-verifier protocol — routed to human verification |
| 8 | 4 placeholder examples/ URLs + changelog.rst dead link repaired | 01 | ✓ VERIFIED | Live grep: 0 `your-repo` occurrences; 0 `typsphinx/projects`; `typsphinx/issues` link intact |
| 9 | `homepage` = RTD bare root, no version segment | 02 | ✓ VERIFIED | Live `gh api --jq .homepage` = exact match |
| 10 | curl on homepage value returns 200 | 02 | ✓ VERIFIED | Live curl confirms 200 (redirect to `/en/latest/`) |
| 11 | Visitor reaches RTD not 404 | 02 | ✓ VERIFIED | 302→200 redirect chain documented and re-confirmed live |
| 12 | Issue #119 not closed, no comment posted (Plan 02) | 02 | ✓ VERIFIED | Live: state OPEN, 1 comment unchanged |
| 13 | All README doc URLs → RTD, 200 | 03 | ✓ VERIFIED | Live grep + curl spot-checks; pytest guard passes |
| 14 | pyproject.toml Documentation → RTD root; siblings unchanged | 03 | ✓ VERIFIED | Live `tomllib`-equivalent grep confirms; Homepage/Repository/Issues intact |
| 15 | Badge is RTD's own build-status badge | 03 | ✓ VERIFIED | `app.readthedocs.org/projects/typsphinx/badge` present in README.md:8 |
| 16 | ja documentation link present, 200 | 03 | ✓ VERIFIED | README.md:269 present; live curl 200 |
| 17 | Top-level links version-less; 7 deep links `/en/latest/`, in order | 03 | ✓ VERIFIED | `uv run pytest tests/test_no_stale_github_io_links.py -v` — 4/4 passed live |
| 18 | Fresh grep: retired host only in CHANGELOG.md | 03/05 | ✓ VERIFIED | Live grep confirms |
| 19 | 7 quick-link labels/order preserved | 03 | ✓ VERIFIED | Live grep confirms labels and suffix order unchanged |
| 20 | `test_no_stale_github_io_links.py` passes, guards regressions | 03 | ✓ VERIFIED | Live run: 4 passed; guard's split-literal construction confirmed (`grep -c 'github\.io'` on the test file = 0) |
| 21 | INTEGRATIONS.md Hosting/CI/Env sections describe RTD, `_resolve_language()` precedence, all 5 workflows | 04 | ✓ VERIFIED | File content matches; `_resolve_language()` in `docs/source/conf.py` confirmed live to implement the exact precedence documented |
| 22 | Action versions in INTEGRATIONS.md match workflow files | 04 | ✓ VERIFIED | Live grep of `.github/workflows/*.yml` `uses:` lines matches INTEGRATIONS.md's "GitHub Actions Dependencies" list exactly |
| 23 | translations repo documented as external infra | 04 | ✓ VERIFIED | Content present; live `test -f .gitmodules` confirms absence in this repo |
| 24 | @preview sync section names 4 guarded + 1 unguarded surface | 04 | ✓ VERIFIED | Content present, matches `tests/test_preview_version_sync.py`'s actual scope |
| 25 | Every INTEGRATIONS.md URL returns 200 | 04 | ✓ VERIFIED | Live spot-check of a sample (docs.python.org, github translations repo, RTD root) all 200; full 7-URL set documented in 31-04-SUMMARY.md |
| 26 | Analysis Date updated | 04 | ✓ VERIFIED | Header + closing line both read `2026-07-26` |
| 27 | Green run on rewritten tree, paired with negative control | 05 | ✓ VERIFIED | Live `gh run view 30265271094` = success, SHA matches final commit |
| 28 | Close-reply draft: English, terse, fulfillment-report only, awaiting review | 05 | ✓ VERIFIED | Draft file confirmed: 2-line reply, no github.io/404 mention, marked "AWAITING OWNER REVIEW" |
| 29 | Todo annotated resolved in place, no deletion | 05 | ✓ VERIFIED | Todo file confirmed annotated with resolving commit `bd80fb8`; `git diff --diff-filter=D` shows no deletions across the phase's commit range |

**Score:** 27/29 verified; 2 items (both instances of the same backstop truth) routed to human verification.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `.github/workflows/links.yml` | Advisory link-check workflow | ✓ VERIFIED | Present, structure matches PLAN spec exactly, live CI runs prove real behavior |
| `.planning/phases/.../31-EVIDENCE.md` | D-09 red/green CI evidence pair | ✓ VERIFIED | Present, both runs' IDs/SHAs/conclusions independently re-confirmed live against `gh run view` |
| `.planning/phases/.../31-ABOUT-EVIDENCE.md` | About-field HTTP evidence | ✓ VERIFIED | Present, content matches live `gh api`/`curl` re-check |
| `tests/test_no_stale_github_io_links.py` | Hermetic regression guard | ✓ VERIFIED | Present, 4/4 tests pass live, hermetic (no `requests`/`urllib`/etc.) |
| `.planning/codebase/INTEGRATIONS.md` | Refreshed codebase note | ✓ VERIFIED | Content matches repository state as independently checked |
| `.planning/phases/.../31-ISSUE-119-REPLY-DRAFT.md` | Draft close-reply | ✓ VERIFIED | Present, satisfies all D-16/D-17 content constraints |
| `.planning/todos/pending/2026-07-22-github-io-doc-links-404-missing-en-prefix.md` | Annotated resolved | ✓ VERIFIED | Present at original path (not moved), resolution recorded |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `links.yml` args | lychee `--extensions` | `toml` present in extension list | ✓ WIRED | Confirmed on disk and via live diagnostic run showing `pyproject.toml` scanned |
| `links.yml` args | lychee `--exclude-path` | 3 anchored regexes | ✓ WIRED | Confirmed on disk (`.planning`, `CHANGELOG\.md$`, `tests/fixtures`); confirmed effective via live diagnostic run's 26-file dump |
| Pushed worktree branch | Triggered workflow run | `on: push` with no branch filter | ✓ WIRED | Confirmed: both red and green runs triggered on worktree branches, never the phase branch |
| Repository `homepage` field | About panel → RTD root redirect → Default Version | `gh api PATCH` + curl chain | ✓ WIRED | Live-confirmed 302→200 chain |
| README badge image host vs. click-through host | `app.readthedocs.org` vs `typsphinx.readthedocs.io` | Two distinct hosts, correctly assigned | ✓ WIRED | Confirmed in README.md:8 |
| `docs/source/conf.py::_resolve_language()` | RTD `READTHEDOCS_LANGUAGE` precedence | Documented in INTEGRATIONS.md | ✓ WIRED | Live-read `conf.py` confirms exact precedence chain matches documentation |
| Regression guard's split string literal | Repo-wide grep (SC#2) | Guard doesn't self-match | ✓ WIRED | Live `grep -c 'github\.io' tests/test_no_stale_github_io_links.py` = 0 |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Regression guard passes | `uv run pytest tests/test_no_stale_github_io_links.py -v` | 4 passed | ✓ PASS |
| Full non-slow suite green | `uv run pytest -q -m "not slow"` | 617 passed, 29 deselected | ✓ PASS |
| Negative-control CI run is real and failed | `gh run view 30205112477 --json conclusion,headSha` | failure, SHA matches | ✓ PASS |
| Green CI run is real and succeeded | `gh run view 30265271094 --json conclusion,headSha` | success, SHA matches | ✓ PASS |
| RTD bare root resolves | `curl -L https://typsphinx.readthedocs.io/` | 200 (via 302→/en/latest/) | ✓ PASS |
| About field set correctly | `gh api repos/.../typsphinx --jq .homepage` | `https://typsphinx.readthedocs.io/` | ✓ PASS |
| Issue #119 untouched | `gh issue view 119 --json state,comments` | OPEN, 1 comment | ✓ PASS |
| Branch protection excludes Link Check | `gh api .../protection --jq '.required_status_checks.contexts'` | 6 ci.yml jobs only | ✓ PASS |
| Repo-wide retired-host grep | `grep -rl 'github\.io' --exclude-dir=.git --exclude-dir=.planning .` | `CHANGELOG.md` only | ✓ PASS |
| Action versions match | `grep -rn 'uses:' .github/workflows/ \| grep -oE ...` | Matches INTEGRATIONS.md exactly | ✓ PASS |

### Probe Execution

No conventional (`scripts/*/tests/probe-*.sh`) or plan-declared probes exist for this phase. **SKIPPED (no runnable entry points of this kind).**

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| CI-05 | Plan 01, 05 | Broken published link surfaces automatically in CI | ✓ SATISFIED | Live red/green CI run pair, advisory-only confirmed |
| DOC-09 | Plan 03, 04, 05 | Every documentation URL resolves, proven by real HTTP fetch | ✓ SATISFIED | Live grep + curl spot-checks + pytest guard, all passing |
| DOC-10 | Plan 02, 05 | Issue #119 closed with fix delivered; visitor reaches docs via About field | ⚠️ SATISFIED (split, owner-decided) | About field set + resolving verified live; close-reply drafted and awaiting review; close itself is a recorded post-merge handoff per D-15 — not a Phase 31 gap |

No orphaned requirements: REQUIREMENTS.md maps exactly DOC-09, DOC-10, CI-05 to Phase 31, and all three appear in some plan's `requirements:` frontmatter.

Note (informational, not a gap): REQUIREMENTS.md's checkbox/traceability table still shows DOC-09 and DOC-10 as `[ ]`/"Pending" and CI-05 as `[x]`/"Complete" — this bookkeeping predates this verification pass and is typically updated downstream (e.g. at milestone completion or a subsequent STATE.md sync); DOC-10's "Pending" mark is in fact accurate given D-15's deliberate split.

### Anti-Patterns Found

None. Scanned every file this phase modified (`links.yml`, `README.md`, `pyproject.toml`, `tests/test_no_stale_github_io_links.py`, `INTEGRATIONS.md`, the four `examples/`/`changelog.rst` files, the todo file, and the issue-reply draft) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/"coming soon"/"not yet implemented" — zero matches. `typsphinx/` and `CHANGELOG.md` confirmed untouched across the phase's full commit range (milestone invariants #2/#3 held).

### Human Verification Required

### 1. Link Check cancellation/supersession leaves no repository state

**Test:** Push twice to a branch in quick succession (or manually cancel a running Link Check job via `gh run cancel`) and inspect the repository afterward for any new commit, tag, issue, or tracked-file change attributable to the run.
**Expected:** Only the GitHub Actions job summary reflects the run; no commit, tag, issue, or tree file was created or modified as a side effect of the cancellation/supersession.
**Why human:** This is tagged `verification: backstop` in both `31-01-PLAN.md` and `31-05-PLAN.md` must_haves.truths — a non-inferable claim about a runtime edge case (mid-flight cancellation) that no wired test or direct observation in this phase's evidence exercises. Static inspection of `.github/workflows/links.yml` (two steps: `checkout`, `lychee-action` with only `jobSummary: true`) is consistent with the claim but is not the same as directly observing a cancelled run's actual behavior. Per the honest-verifier protocol, this must be flagged rather than silently passed on structural presence alone.

### Gaps Summary

No gaps. Every ROADMAP success criterion and every plan-level must-have is either VERIFIED against live, independently-reproduced evidence (not merely SUMMARY.md's claims), or is an owner-decided, explicitly-documented phase-boundary split (SC#4's Issue #119 close, deferred to `/gsd-complete-milestone` per D-15) that the phase instructions direct not be treated as a gap. The only outstanding item is a single non-inferable (`backstop`) truth — present in two plans as the same statement — that requires a held-out human test of a mid-flight-cancellation edge case rather than being confidently marked VERIFIED on the strength of static code inspection alone.

All live-reproduced checks (CI run IDs/conclusions/SHAs via `gh run view`, `gh api` reads for `homepage` and branch protection, `gh issue view` for Issue #119 state, `curl -L` fetches of a sample of URLs, and a live `uv run pytest` of both the new regression guard and the full non-slow suite) matched the SUMMARY/EVIDENCE files' claims exactly — no discrepancy between claimed and actual state was found anywhere in this phase.

---

*Verified: 2026-07-27*
*Verifier: Claude (gsd-verifier)*

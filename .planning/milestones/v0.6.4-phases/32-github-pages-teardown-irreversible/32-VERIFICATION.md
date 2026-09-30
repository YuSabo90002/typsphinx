---
phase: 32-github-pages-teardown-irreversible
verified: 2026-07-27T19:48:59Z
status: passed
score: 12/12 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: No — initial verification
---

# Phase 32: GitHub Pages Teardown (IRREVERSIBLE) Verification Report

**Phase Goal:** typsphinx documentation is hosted by Read the Docs and only Read the Docs — the
GitHub Pages publish path and the branch that served it are gone — while the `typstpdf` regression
gate and the tag-time PDF Release attachment keep working.
**Verified:** 2026-07-27T19:48:59Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

Every claim below was independently re-checked live against the actual remote/CI state during
this verification pass, not read off SUMMARY.md prose or trusted from 32-EVIDENCE.md alone.

### Observable Truths

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---------|--------|----------|
| 1 | SC#1 — A pre-teardown gate records freshly re-taken, in-phase evidence that RTD is currently serving English HTML, Japanese HTML (content-verified), the PDF, and that the doc root resolves; teardown proceeds only behind that evidence | ✓ VERIFIED | `32-EVIDENCE.md` "Gate check 1"/"Gate check 2" sections contain five verbatim `curl`/`python3` checks (en HTML 200, root→`/en/latest/`, ja HTML 200 + `ビルダー` present + CJK count 1038 vs en control 0, en/ja PDF 200 + `%PDF` magic bytes + 1704446/1888676 bytes), closing with a single `GATE VERDICT: GREEN` line. Plans 02 and 03 both re-confirmed the four URL statuses (all 200) before proceeding, recorded under `## D-04 re-confirmation …` headings. |
| 2a | SC#2 (repo half) — `docs.yml` no longer contains a GitHub Pages deploy step (`peaceiris/actions-gh-pages`) | ✓ VERIFIED | Read `.github/workflows/docs.yml` directly (57 lines, current HEAD `444f480`): no `peaceiris` occurrence, no `pages: write`/`id-token: write`, `permissions:` reduced to `contents: write` only. `Upload PDF to Release` step retained. |
| 2b | SC#2 (remote half) — `origin/gh-pages` no longer exists, proven by `git ls-remote`, not a local branch listing | ✓ VERIFIED | Ran `git ls-remote origin refs/heads/gh-pages` live during this verification — empty output. `git ls-remote --heads origin \| grep -c refs/heads/main` still resolves to 1 — no collateral ref damage. |
| 2c | SC#2 — the old `github.io` URL returns 404, no redirect stub added | ✓ VERIFIED | Ran `curl -sS -o /dev/null -w "%{http_code} %{url_effective}\n" https://YuSabo90002.github.io/typsphinx/` live during this verification → `404 https://YuSabo90002.github.io/typsphinx/`, no redirect. `git grep -n 'github\.io' -- ':!.planning'` shows exactly the historical `CHANGELOG.md:393` hit; `test -f CNAME` → absent. |
| 3a | SC#3 — an observed CI run on the post-teardown tree keeps `tox -e docs-pdf` green as the PR-blocking gate | ✓ VERIFIED | `gh run view 30275369792` (live, this verification) → `conclusion: success`, `event: pull_request`, `headSha: d53edecfd064a93d7a43455d505f7848a1c43320` (differs from Plan 01's pre-teardown baseline `980f6ca9…`). Step `Build PDF documentation (English only)` recorded `conclusion: success` at step level, not inferred from job. `git show d53edec…:.github/workflows/docs.yml \| grep -c peaceiris` → 0, proving the green run built the post-teardown tree. |
| 3b | SC#3 — the tag-time `Upload PDF to Release` step is byte-unchanged in the milestone diff | ✓ VERIFIED | Ran `diff <(git show 771ec56…:.github/workflows/docs.yml \| sed -n '/- name: Upload PDF to Release/,$p') <(sed -n '/- name: Upload PDF to Release/,$p' .github/workflows/docs.yml)` live during this verification — empty output, exit 0. |
| 4 | The removal is made permanent, not just a one-time edit — a guard test blocks regression | ✓ VERIFIED | `tests/test_readthedocs_config.py::test_docs_workflow_has_no_github_pages_deploy` and `::test_docs_workflow_still_uploads_pdf_to_release` exist (grep-confirmed at lines 143/166) and both pass (`uv run pytest tests/test_readthedocs_config.py -q` → 6 passed, run live this verification). The guard was proven non-vacuous by a recorded red run against the merge-base workflow in `32-EVIDENCE.md` (`## D-06 guard tests — recorded red negative control`, FAILED exit 1 against merge-base, restored clean). |
| 5 | Codebase documentation (`INTEGRATIONS.md`) matches the reduced workflow | ✓ VERIFIED | `grep -n 'peaceiris\|Phase 32\|softprops' .planning/codebase/INTEGRATIONS.md` (live) shows zero `peaceiris`/`Phase 32` hits and a `docs.yml` bullet describing the actual build+artifact+Release-attach behavior, framing RTD as the sole publish path. |
| 6 | Full test suite is green after the teardown edits | ✓ VERIFIED | No non-`.planning/` commits landed after the Plan 03 merge (`git diff --stat 58a484a..HEAD -- . ':!.planning'` empty), so the orchestrator-reported full run (647 passed, 1 skipped, 0 failed) is current; targeted module re-run this verification also passed (6/6). |

**Score:** 6/6 roadmap-level truths verified (12/12 counting the SC#2/SC#3 sub-checks individually), 0 present-but-behavior-unverified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.github/workflows/docs.yml` | Pages deploy step + unused permissions removed; Release step + docs-pdf gate intact | ✓ VERIFIED | Read directly; matches expected shape exactly, no debt markers. |
| `tests/test_readthedocs_config.py` | Two new guard tests, hermetic, non-vacuous | ✓ VERIFIED | Both present, both pass, red negative-control recorded. |
| `.planning/codebase/INTEGRATIONS.md` | Reduced-workflow description, no stale Phase-32 language | ✓ VERIFIED | Confirmed via live grep. |
| `.planning/phases/32-github-pages-teardown-irreversible/32-EVIDENCE.md` | Verbatim command+output log for all gate checks, teardown steps, and 404 observation | ✓ VERIFIED | 813 lines, 16 `##` sections, all claimed headings present; spot-checked against live re-execution of the same commands — all reproduced identically (200/404/success/empty-diff). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| GATE VERDICT (Plan 01) | Plans 02/03 entry | Structural gate — RED blocks/escalates | ✓ WIRED | GREEN verdict recorded; Plans 02/03 both read and re-confirmed it before acting (`## D-04 re-confirmation` sections in both). |
| `permissions.contents: write` | `softprops/action-gh-release@v3` | Retained permission the Release step needs | ✓ WIRED | `contents: write` present exactly once; positive-retention assertion exists in the guard test (not just absence checks). |
| Pushed teardown commit (`d53edec…`) | Cited CI run `30275369792` | `headSha` equality, tree re-verified via `git show` | ✓ WIRED | Verified live: run's `headSha` matches pushed SHA, differs from pre-teardown baseline, and the run's own tree greps 0 `peaceiris`. |
| Branch deletion (`origin/gh-pages`) | github.io 404 | Deleting the Pages source | ✓ WIRED | Live `git ls-remote` shows the ref gone and live `curl` shows 404 — the causal chain (source removed → 404) is directly observed, not inferred. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CI-04 | 32-01, 32-02, 32-03 | GitHub Pages no longer hosts/publishes typsphinx docs, while the `typstpdf` gate and tag-time PDF Release attachment keep working | ✓ SATISFIED | All three SCs verified live (see Observable Truths above). REQUIREMENTS.md's checkbox (line 65) and traceability row (line 218, "Pending") are not yet flipped — this was a deliberate deferral to phase completion, per this phase's execution briefing, and is a bookkeeping step for `/gsd-complete-milestone` or a follow-up commit rather than evidence of an unmet requirement. |

No orphaned requirements: REQUIREMENTS.md's traceability table maps only CI-04 to Phase 32, and all three plans declare `requirements: [CI-04]`.

### Anti-Patterns Found

None. `grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` over `.github/workflows/docs.yml`, `tests/test_readthedocs_config.py`, and `.planning/codebase/INTEGRATIONS.md` returned no hits. `32-REVIEW.md` (code review for this phase) records 0 critical findings and only two low-severity style notes, neither blocking.

### Human Verification Required

None. The one item that could have required human/owner follow-up — the owner-manual GitHub Pages
Settings → Pages disable (REQUIREMENTS.md manual step #7) — has its *only automatable outcome* (the
github.io 404) already directly observed as `CONFIRMED` in `32-EVIDENCE.md` and independently
re-confirmed live during this verification. The Settings toggle itself remains on the owner's
manual checklist by locked project decision (never automatable, per REQUIREMENTS.md), but the
phase's Success Criteria only require the 404 outcome, not the toggle — so this is not an
outstanding verification gap for CI-04.

### Gaps Summary

No gaps. All three ROADMAP success criteria are independently confirmed against live remote/CI
state (not merely re-read from 32-EVIDENCE.md): `origin/gh-pages` is absent via a fresh
`git ls-remote`, `https://YuSabo90002.github.io/typsphinx/` returns 404 via a fresh `curl`, the
cited CI run `30275369792` is `success` with the `docs-pdf` step individually `success` via a fresh
`gh run view`, and the `Upload PDF to Release` step diffs byte-empty against the milestone
merge-base via a fresh `diff`. The two new guard tests exist, pass, and were proven non-vacuous by
a recorded red run. `INTEGRATIONS.md` and the full test suite reflect the reduced workflow with no
regressions. The only open item — REQUIREMENTS.md's CI-04 checkbox/traceability status still
reading unchecked/"Pending" — is bookkeeping explicitly deferred by design, not a functional gap.

---

_Verified: 2026-07-27T19:48:59Z_
_Verifier: Claude (gsd-verifier)_

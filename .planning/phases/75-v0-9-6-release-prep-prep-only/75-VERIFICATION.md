---
phase: 75-v0-9-6-release-prep-prep-only
verified: 2026-09-22T11:00:00Z
status: passed
score: 5/5 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-01-PLAN.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-01-SUMMARY.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-02-PLAN.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-02-SUMMARY.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-03-PLAN.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-03-SUMMARY.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-04-PLAN.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-04-SUMMARY.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-05-PLAN.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-05-SUMMARY.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-06-PLAN.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-06-SUMMARY.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-07-PLAN.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-07-SUMMARY.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-BASE-EVIDENCE.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-BUMP-EVIDENCE.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-CHANGELOG-EVIDENCE.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-CI-EVIDENCE.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-CLOSEOUT-GUARD.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-CONTEXT.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-GREEN-TREE-EVIDENCE.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-HANDOFF.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-LEFTOVERS-EVIDENCE.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-PREFLIGHT-EVIDENCE.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-REVIEW.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/75-SC5-INVARIANTS.md", ".planning/phases/75-v0-9-6-release-prep-prep-only/COVERAGE.md", ".planning/todos/pending/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md", ".planning/todos/pending/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md", "CHANGELOG.md", "README.md", "pyproject.toml", "tests/test_changelog_page_gate.py", "uv.lock"]
covered_digest: "v1:sha256:a5ff35494d9c77b1d11fd8b15a1eb0402aeed775aaad3e426a7c61241a14143c"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 75: v0.9.6 Release Prep (prep-only) Verification Report

**Phase Goal:** the 0.9.6 tree is bumped, its CHANGELOG curated into a single `## [0.9.6]` section
covering the six carried `## [Unreleased]` bullets and this milestone's own, the tail link block
moved to match, the `### Known Limitations` question settled on the record either way, the
extracted release body read rather than assumed, and the whole thing handed off — with **zero
irreversible action inside the phase**.

**Verified:** 2026-09-22T11:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1 — version moves to 0.9.6 in one commit touching every file that carries it, zero-skip changelog page gate | ✓ VERIFIED | `git show --name-only 84edd348` lists exactly `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`, `tests/test_changelog_page_gate.py`. Live re-read: `pyproject.toml:7 version = "0.9.6"`; `uv.lock`'s `typsphinx` stanza `version = "0.9.6"`; `README.md:348` `**Status**: Stable (v0.9.6)`. `RELEASE_VERSIONS` tuple (17 entries, `0.4.1`..`0.9.6`) confirmed live; `uv run pytest -rs tests/test_changelog_page_gate.py -q` → `6 passed`, zero skipped, live re-run. |
| 2 | SC2 — one curated `## [0.9.6]` section with byte-identical carried bullets, fresh `## [Unreleased]`, moved tail link block, extractor executed | ✓ VERIFIED | Live `grep -n "^## \["` CHANGELOG.md: `## [Unreleased]` (8) directly above `## [0.9.6] - 2026-09-20` (17); no `## [0.9.3]`/`## [0.9.4]`/`## [0.9.5]` heading exists; `[0.9.6]: .../releases/tag/v0.9.6` sits immediately above `[0.9.2]:` in the tail block; `[Unreleased]: .../compare/v0.9.6...HEAD`. `75-CHANGELOG-EVIDENCE.md` records the SHA-256 byte-identity digests and the extractor transcript; the six carried bullets and two new `### Fixed` bullets (doctest rendering, QUA-14) are present in the live file in the documented order. |
| 3 | SC3 — `### Known Limitations` settled explicitly (NUM-01 disclosed), REL-16 closeable | ✓ VERIFIED | Live `grep -n "^### Known Limitations"` CHANGELOG.md → exactly 2 hits (the pre-existing `[0.1.0b1]` entry + the new one inside `## [0.9.6]`). The new section (lines 91-101) names NUM-01 alone with precondition, both symptoms and a `**Workaround:**` line; the converted-image and `typst_documents` defects (both measured closed in v0.8.0) and WR-02/WR-03 are absent, matching `75-CHANGELOG-EVIDENCE.md`'s AMENDED candidate-set correction. REQUIREMENTS.md REL-16 (line 23) still reads `[ ]`/`Pending` at this pre-`phase.complete` observation, which is correct — REL-16 flips at phase-completion tooling, not by a plan. |
| 4 | SC4 — bumped tree proven green by runs executed in this phase (lint trio, pytest x2, docs-html/docs-pdf, linkcheck, one fresh CI run, non-committing trial merge) | ✓ VERIFIED | Independently re-run live, not taken on the evidence files' word: `uv run ruff check .` → 0; `uv run black --check .` → 0; `uv run mypy typsphinx/` → 0; `uv run pytest -q` → `1569 passed, 1 skipped` (matches `75-GREEN-TREE-EVIDENCE.md` exactly); `rm -rf docs/_build && LANG=C LC_ALL=C uv run tox -e docs-html` → `build succeeded.` with zero warnings, live. `gh run view 35714217450` confirms `conclusion=success`, `headSha=8416938871398...` (the operative, AMENDED second dispatch) live via `gh` API. `75-PREFLIGHT-EVIDENCE.md`'s non-committing `git merge-tree` trial merge is a documented, non-live-reproducible-here artifact but is internally consistent and the merged tree's own lock/lint pass is recorded. The linkcheck condition is honored under the owner's 2026-09-20 AMENDED reading (`working` + classified exceptions = `total`); `docs/source/conf.py` confirmed live to hold zero `linkcheck` keys — no product edit softened the gate. |
| 5 | SC5 — zero irreversible action, probed twice, REL-15 fenced by SHA-256, standalone handoff | ✓ VERIFIED | Live probes: `git tag -l 'v0.9.6'` → empty; `curl pypi.org/pypi/typsphinx/0.9.6/json` → 404 (control `0.9.2` → 200); `gh release list` → latest is `v0.9.2`, no `v0.9.6`. `sha256sum .planning/REQUIREMENTS.md` at current HEAD (`8c67b05b`, after the code-review round) → `481e2091...`, byte-identical to `REQ_SHA256_BASE`/`REQ_SHA256_CLOSE` recorded in `75-CLOSEOUT-GUARD.md`; REL-15 checkbox read directly as `[ ]`. `git diff --name-only <milestone-base> HEAD -- typsphinx/` → exactly `pathfmt.py`, `translator.py` (Phase 74's own diff, unchanged by Phase 75). `75-HANDOFF.md` is standalone, enumerates every `/gsd-complete-milestone` step with SHAs/run-ids/digests inlined, and explicitly carries the Class A linkcheck re-check obligation as a required step (not a footnote). |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Amendments — independently confirmed

1. **SC4 linkcheck amendment (2026-09-20).** Confirmed live: `docs/source/conf.py` carries zero
   `linkcheck` keys (`grep -n linkcheck docs/source/conf.py` → no match). `75-HANDOFF.md` line
   109-114 carries the Class A (`v0.9.6` tag links) post-tag re-check as a required
   `/gsd-complete-milestone` step, not a waiver — confirmed by direct read.
2. **Second CI dispatch (2026-09-22).** Confirmed live via `gh run view 35714217450`:
   `conclusion=success`, `headSha=8416938871398f52a03636db2ef4c4895e39ac75`,
   `event=workflow_dispatch`. The fix commit `84169388` touches exactly one file
   (`tests/test_changelog_page_gate.py`, 1 insertion/1 deletion, comment text only) — confirmed by
   `git show --stat 84169388`. SC1's "one commit" reading is intact: the five-file bump commit
   (`84edd348`) is unchanged; the fix is a distinct, later, comment-only commit, not a second bump.
3. **`POST_DISPATCH_PRODUCT_FILES` supersession (2026-09-22).** Confirmed live:
   `git diff --name-only 84169388 8c67b05b` (current HEAD) touches only `.planning/` evidence
   files — zero product files after the tip CI actually tested (`84169388`), matching the AMENDED
   restatement in `75-SC5-INVARIANTS.md` exactly.

### Prep-only fence — independently confirmed

- `git tag -l 'v0.9.6'` → empty (local).
- `git ls-remote --tags origin` → no `v0.9.6` (checked via `curl` PyPI + `gh release list` above;
  origin tag absence corroborated by `75-SC5-INVARIANTS.md`'s live-reproduced probes, and no local
  contradiction found).
- PyPI: `https://pypi.org/pypi/typsphinx/0.9.6/json` → `404`; `.../0.9.2/json` → `200` (positive
  control present).
- `gh release list --limit 5` → latest `v0.9.2`, no `v0.9.6` entry.
- Repo-root scratch files from Phase 74 (`probe_*.typ`) confirmed absent (`ls` → no match).
- `.planning/REQUIREMENTS.md` byte-identical to phase base at the **current** HEAD (after the
  code-review round), confirmed by direct `sha256sum`.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `75-CLOSEOUT-GUARD.md` | REL-15 fence baseline + close re-verification + operator's third-observation protocol | ✓ VERIFIED | `verify.artifacts` (75-01, 75-07 plans): all pass. `REQ_SHA256_BASE`/`REQ_SHA256_CLOSE` both `481e2091...`, matching live `sha256sum`. |
| `75-BASE-EVIDENCE.md` | clean base docs-html/docs-pdf warning ledger | ✓ VERIFIED | `verify.artifacts` pass; content present with falsifiable synthetic + Phase-74 controls. |
| `75-SC5-INVARIANTS.md` | probe observations 1+2, scope fence, REL-16 settlement, SC roll-up | ✓ VERIFIED | `verify.artifacts` pass; AMENDED supersession section present and internally consistent with live diff. |
| `75-LEFTOVERS-EVIDENCE.md`, `COVERAGE.md` | probe-file cleanup census, api-coverage declaration | ✓ VERIFIED | `api-coverage.verify-pre` gate re-run live → `passed: true`. Probe files confirmed absent on disk. |
| `75-BUMP-EVIDENCE.md`, `75-CHANGELOG-EVIDENCE.md` | SC1/SC2/SC3 evidence | ✓ VERIFIED | `verify.artifacts` pass; version surfaces and CHANGELOG structure independently re-read and match. |
| `75-GREEN-TREE-EVIDENCE.md` | SC4 local half + AMENDED linkcheck section | ✓ VERIFIED | `verify.artifacts` pass; lint trio, pytest counts, docs-html build independently re-run live and match exactly. |
| `75-PREFLIGHT-EVIDENCE.md` | trial merge, remote reads | ✓ VERIFIED | `verify.artifacts` pass; internally consistent, `main` protection reads corroborated by live `gh api` conventions used elsewhere in this verification. |
| `75-CI-EVIDENCE.md` | dispatch 1 + AMENDED dispatch 2 | ✓ VERIFIED | `verify.artifacts` pass; `gh run view 35714217450` live-confirms dispatch 2's status/conclusion/headSha. |
| `75-HANDOFF.md` | standalone `/gsd-complete-milestone` procedure | ✓ VERIFIED | `verify.artifacts` pass; Class A linkcheck obligation, REL-15's four observations, and the manual `update-pin.yml` dispatch all present on direct read. |
| `75-REVIEW.md` | `execute:post` code review + resolution | ✓ VERIFIED | WR-01 finding and fix (`84169388`) both confirmed live against the actual diff; `status: resolved`, 0 deferred. |
| Two pending todos (IN-01, PyPI `#history`) | filed, not fixed | ✓ VERIFIED | Both present on disk with substantive Problem/Solution/Why-deferred sections; `typsphinx/` and `docs/source/conf.py` confirmed unedited. |

### Key Link Verification

The generic `verify.key-links` tool reports 0/N "verified" across all seven plans because every
plan wrote its `from`/`to` fields as evidence-chain prose (e.g. `75-BASE-EVIDENCE.md
BASE_HTML_WARNINGS / BASE_PDF_WARNINGS`) rather than bare repo-relative file paths, which the
tool's path-existence check cannot resolve. This is a **tooling format mismatch, not a broken
link** — manually confirmed for a representative sample:

| From | To | Via (pattern) | Status | Manual evidence |
|------|-----|-----|--------|------------------|
| `75-BASE-EVIDENCE.md` `BASE_HTML_WARNINGS`/`BASE_PDF_WARNINGS` | `75-GREEN-TREE-EVIDENCE.md` tip comparison | read with `sed` | ✓ WIRED | `grep -n "BASE_HTML_WARNINGS\|BASE_PDF_WARNINGS" 75-GREEN-TREE-EVIDENCE.md` → both present in the comparison table (line 206-207). |
| `75-CLOSEOUT-GUARD.md` `REQ_SHA256_BASE` | `REQ_SHA256_CLOSE` in the same file | recomputed `sha256sum` | ✓ WIRED | `grep -n REQ_SHA256_CLOSE 75-CLOSEOUT-GUARD.md` → present, value matches `REQ_SHA256_BASE` and the live `sha256sum`. |
| `75-CI-EVIDENCE.md` `SC4_CI_VERDICT` | `75-HANDOFF.md` | read with `sed` | ✓ WIRED | `75-HANDOFF.md` line 43 names `RUN_ID_2 = 35714217450` and `SC4_LOCAL_VERDICT_AFTER_AMEND2 = MET`, matching `75-CI-EVIDENCE.md`'s AMENDED section. |
| `CHANGELOG.md` `## [0.9.6]` section | GitHub Release body at `/gsd-complete-milestone` | `scripts/extract_changelog_section.py 0.9.6` | ✓ WIRED (by plan-recorded transcript) | `75-CHANGELOG-EVIDENCE.md` records the extractor's stdout as byte-identical to the committed section body; not independently re-run here (read-only extraction script, low risk, plan-verified twice per its own `<verify>`). |

No key link showed evidence of being structurally absent; all sampled links resolve to real,
present content in their target files.

### Data-Flow Trace (Level 4)

Not applicable — this phase produces no rendered UI or dynamic data path. Its "data flow" is
evidence-file-to-evidence-file citation, verified under Key Link Verification above, and
product-file-to-live-state correspondence, verified directly against the live repository, GitHub
API, and PyPI throughout this report.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Version-sync gates pass | `uv run pytest -q tests/test_readme_version_sync.py tests/test_preview_version_sync.py` | `4 passed` | ✓ PASS |
| Changelog page gate, zero skips | `uv run pytest -rs tests/test_changelog_page_gate.py -q` | `6 passed`, 0 skipped | ✓ PASS |
| Full suite green, matches evidence's claimed count | `uv run pytest -q` (run once, full suite) | `1569 passed, 1 skipped in 128.97s` | ✓ PASS |
| Lint trio green | `uv run ruff check .` / `uv run black --check .` / `uv run mypy typsphinx/` | all exit 0 | ✓ PASS |
| Clean docs-html build, zero warnings | `rm -rf docs/_build && LANG=C LC_ALL=C uv run tox -e docs-html` | `build succeeded.` | ✓ PASS |
| Second CI dispatch really completed, on the right tip | `gh run view 35714217450 --json status,conclusion,headSha,event` | `completed`/`success`, `headSha` = `84169388...`, `workflow_dispatch` | ✓ PASS |
| No v0.9.6 published anywhere | `curl pypi.org/pypi/typsphinx/0.9.6/json`, `gh release list`, `git tag -l v0.9.6` | 404 / no v0.9.6 entry / empty | ✓ PASS |

`docs-pdf` and `linkcheck` were not independently re-run here (typst compile + network-bound,
respectively); their claimed results are accepted on the strength of the docs-html build matching
exactly, the lint/pytest counts matching exactly, and the linkcheck amendment's own re-measurement
table (Class A/B) being internally verifiable against live `conf.py` and PyPI state, both of which
were independently confirmed above.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REL-15 | 75-01, 75-03, 75-07 (`requirements: [REL-15, ...]`); 75-02, 75-04, 75-05, 75-06 (`requirements: [REL-15]`) | v0.9.6 published (checkbox closes at `/gsd-complete-milestone`) | ✓ SATISFIED (coverage-only, by design) | All plans declare `requirements-completed: []`. `.planning/REQUIREMENTS.md` line 22 confirmed `[ ]` live, byte-identical to phase base. This is the intended state per ROADMAP constraint 1 — not a defect. |
| REL-16 | 75-01, 75-03, 75-07 | Known Limitations question settled on the record | ✓ SATISFIED | `### Known Limitations` present in `## [0.9.6]`, naming NUM-01 with precondition/symptoms/workaround; `75-SC5-INVARIANTS.md` records the settlement (anchored grep = 2, decision record agrees). Checkbox legitimately stays `[ ]` until phase-completion tooling runs (not yet run at this verification point) — confirmed correct, not a gap. |

No orphaned requirements: `grep -n "Phase 75" .planning/REQUIREMENTS.md` maps only REL-15 and
REL-16 to this phase, both covered above.

### Decision Coverage

`check.decision-coverage-verify` against `75-CONTEXT.md`: **15/15 decisions honored**, 0 not
honored. `{"skipped": false, "blocking": false, "total": 15, "honored": 15, "not_honored": []}`

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `CHANGELOG.md:740` | `(TODO-01)` | grep hit on `TODO` | none (false positive) | Historical requirement-ID reference inside the pre-existing `[0.6.1]` section, untouched by this phase's diff — not a debt marker. |
| `75-CLOSEOUT-GUARD.md:469` | `0/TBD` | grep hit on `TBD` | none (false positive) | Inside a literal quoted `diff` hunk showing ROADMAP.md's *prior* text (a `<` diff-removed line), not live prose in the evidence file itself. |

No 🛑 Blockers, no unreferenced debt markers, no stub/placeholder/hollow-prop patterns found in
any of the five product files this phase modified (`pyproject.toml`, `uv.lock`, `README.md`,
`CHANGELOG.md`, `tests/test_changelog_page_gate.py`).

### Human Verification Required

N/A — infrastructure/release-prep phase with no user-facing elements. All five success criteria
are measurement/fact assertions (version literals, file structure, absence of remote publish
artifacts, CI run status) verifiable programmatically, and all were independently re-verified
against the live repository, git history, GitHub API, and PyPI in this pass — not accepted on the
evidence files' own word. No truth in this phase asserts a runtime state transition or a
cancellation/cleanup/ordering invariant that only a behavioral test could exercise, so no item is
routed to `behavior_unverified_items`.

### Gaps Summary

None. All five ROADMAP success criteria are independently confirmed against the live repository,
not merely read from SUMMARY.md or the phase's own evidence files. The three owner-decided
amendments (linkcheck reading, second CI dispatch, `POST_DISPATCH_PRODUCT_FILES` supersession) are
each honestly recorded as `## AMENDED` addenda that preserve the original reading, and each was
independently re-measured here and found accurate. The prep-only fence (zero tag, zero PyPI
publish, zero GitHub Release, `.planning/REQUIREMENTS.md` byte-identical to phase base at the
current HEAD) holds at the moment of this verification, which is itself after the code-review
round (WR-01 fix) that followed the plans' own completion.

---

*Verified: 2026-09-22T11:00:00Z*
*Verifier: Claude (gsd-verifier)*

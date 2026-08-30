---
phase: 63-v0-9-2-release-prep-prep-only
verified: 2026-08-30T21:30:00Z
status: gaps_found
score: 4/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
gaps:
  - truth: "SC#2 — the extracted release body was read rather than assumed"
    status: failed
    reason: >
      The extractor was run and its stdout was inspected for the specific structural properties
      the criterion enumerates (non-empty, byte-for-byte match against the section on disk, no
      leaked "Planned for Future Releases" scratch block, no ## [0.9.1] heading/tail link, advanced
      [Unreleased] compare base) — all five of those checks re-verify cleanly today. But the
      inspection stopped at structure and did not catch a factual claim in the same extracted body
      that is false and trivially checkable: the `## [0.9.2]` intro paragraph states "The runtime
      changes are confined to `typsphinx/translator.py`, with no other file under `typsphinx/`
      touched." `git diff --stat v0.9.0..HEAD -- typsphinx/` (re-run independently at verification
      time, matching the number already recorded inside 63-CHANGELOG-EVIDENCE.md's own "Milestone-
      invariant sweep" section) shows five files changed: builder.py, pathfmt.py,
      template_registry.py, translator.py, writer.py (408 insertions, 58 deletions). This is not a
      subtle contradiction requiring cross-referencing multiple sources — the correct, contradicting
      command output is recorded in the very same evidence file that also transcribes the false
      claim, one section below it. This text is destined to be published byte-identically as the
      GitHub Release body (per 63-HANDOFF.md item 3) and as the Read the Docs changelog page (per
      RELEASE_VERSIONS / test_changelog_page_gate.py). "The extracted release body read rather than
      assumed" is a criterion about genuine inspection of exactly this content, and a false,
      self-contradicted-in-the-same-file claim surviving that inspection means the inspection did
      not extend to the content's accuracy, only to its shape.
    artifacts:
      - path: "CHANGELOG.md"
        issue: "Line 23-24: '## [0.9.2]' intro paragraph falsely states the runtime diff is confined to typsphinx/translator.py; actually 5 files changed under typsphinx/ since v0.9.0."
    missing:
      - "Correct or remove the false file-confinement sentence in CHANGELOG.md's ## [0.9.2] intro paragraph, per 63-REVIEW.md CR-01's suggested fix (scope the claim to the one fix it's true for, or drop the blanket claim entirely)."
      - "Re-run the extractor and re-verify SC#2's byte-identity/structural checks against the corrected text before this is handed to /gsd-complete-milestone, since the GitHub Release body and RTD changelog page publish this text verbatim."
---

# Phase 63: v0.9.2 Release Prep (prep-only) Verification Report

**Phase Goal:** the 0.9.2 tree is bumped, its CHANGELOG curated into a single `## [0.9.2]` entry
covering both v0.9.1's accumulated bullets and this milestone's fix, the extracted release body
read rather than assumed, and the whole thing handed off — with **zero irreversible action**. No
tag, local or remote; no publish; no GitHub Release; no PR.

**Verified:** 2026-08-30T21:30:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, verbatim numbering)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The version moves to 0.9.2 in one commit touching all four files | ✓ VERIFIED | `git show --name-only --format= 10d9d95d` → exactly `CHANGELOG.md`, `README.md`, `pyproject.toml`, `uv.lock` (re-run independently, matches). `sed -n '7p' pyproject.toml` → `version = "0.9.2"`. `sed -n '347p' README.md` → `**Status**: Stable (v0.9.2) - Production ready`. `uv.lock` line 1467 → `version = "0.9.2"`. `tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject` re-run: PASSED. |
| 2 | The extractor was run and its output inspected | ✗ FAILED | Structural sub-checks all re-verify (extractor exit 0, 4087-byte stdout, `grep -c 'Planned for Future Releases'` on extracted body = 0, `grep -c '^## \[0\.9\.1\]'` = 0, `grep -c '^\[0\.9\.1\]:'` = 0, tail block carries `[0.9.2]: .../tag/v0.9.2` and `[Unreleased]: .../compare/v0.9.2...HEAD`). But the extracted body contains a false, trivially-checkable claim (CR-01) that survived this inspection — see Gaps Summary. |
| 3 | The release-checkbox fence is proven held by a recorded SHA-256 | ✓ VERIFIED | `.planning/REQUIREMENTS.md` REL-09 re-read directly: line 70 `- [ ] **REL-09**: ...` (unchecked), line 154 `\| REL-09 \| Phase 63 \| Pending \|`. `63-CLOSEOUT-GUARD.md` records the phase-head SHA-256 (`f0dd4ec3...`), re-verifies it MATCH at phase close with all four comparisons (digest, `wc -l`, name-only diff, grep hits). Every plan's frontmatter (`63-01` through `63-04`) declares `requirements-completed: []` for REL-09. Third (post-`phase.complete`) observation is correctly deferred to the operator per `63-HANDOFF.md` — not yet due, since `phase.complete`-family tooling has not run for this phase. |
| 4 | The bumped tree is proven green on runs executed in this phase | ✓ VERIFIED | Independently re-run: `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py` → 5 passed. Orchestrator's full-suite re-run (three times): 1547 passed, 1 skipped, identical each time. `gh run view 33309565005 --json status,conclusion,headSha,jobs` independently re-fetched: `conclusion=success`, `headSha=225c6618...` (matches bumped tip lineage), 12/12 jobs `success`, both `windows-latest` and both `macos-latest` lanes present. `ruff`'s verdict is read from that run's `Lint and Format Check` job step log (`All checks passed!`), not asserted locally (local `ruff` is unrunnable on this NixOS host — correctly not substituted, per `63-GREEN-TREE-EVIDENCE.md` § "Division of authority"). Both docs builds recorded from a clean `rm -rf docs/_build` baseline (3 / 5 warnings). |
| 5 | Zero irreversible action, probed twice, and the handoff is standalone | ✓ VERIFIED | Independently re-run: `git tag -l 'v0.9.2*'` → empty. `git ls-remote --tags origin 'v0.9.2*'` → empty (positive control `git ls-remote --tags origin` → 39 lines). `gh release list` → latest is v0.9.0, no v0.9.2. `gh pr list --state open` → only pre-existing dependabot PRs #123/#128 (dated 2026-07-27 / 2026-08-03, predating this phase). `gh run list --workflow=release.yml` → no run against any phase-63 tip. `git diff --name-only c31bb048..HEAD -- typsphinx/` → empty; positive control (same diff without the pathspec) → 5 files (`CHANGELOG.md`, `README.md`, `pyproject.toml`, `tests/test_changelog_page_gate.py`, `uv.lock`), matching `63-SC5-INVARIANTS.md`'s recorded widened-diff result. Two waves-separated fence observations recorded in `63-SC5-INVARIANTS.md` (wave 1 / wave 3). `63-HANDOFF.md` exists, enumerates the tag push, the `pypi` Environment manual-approval expected gate, the GitHub Release body byte-identity check, the `typsphinx-doc-translations` `update-pin.yml` manual dispatch, and the RTD `en`/`ja` `stable` verification — standalone and readable without opening any other phase file. |

**Score:** 4/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | version bumped to 0.9.2 | ✓ VERIFIED | Line 7: `version = "0.9.2"` |
| `uv.lock` | typsphinx stanza regenerated to 0.9.2 | ✓ VERIFIED | Line 1467: `version = "0.9.2"`; `uv sync --extra dev --locked` exits 0 per `63-CI-EVIDENCE.md` pre-dispatch check |
| `README.md` | Status line reads v0.9.2 | ✓ VERIFIED | Line 347: `**Status**: Stable (v0.9.2) - Production ready` |
| `CHANGELOG.md` | curated single `## [0.9.2]` entry, no `## [0.9.1]`/scratch-block leak | ⚠️ SUBSTANTIVE BUT CONTAINS A FALSE CLAIM | Structurally correct (one `## [0.9.2]` heading, `### Fixed` + `### Verified` only, tail link present); CR-01's false file-confinement sentence is a content-accuracy defect, not a structural one — see gap above |
| `tests/test_changelog_page_gate.py` | `RELEASE_VERSIONS` extended to 16 entries incl. "0.9.2" | ✓ VERIFIED | `RELEASE_VERSIONS` tuple includes `"0.9.2"`; `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` → 6 passed (per `63-CHANGELOG-EVIDENCE.md`) |
| `63-CLOSEOUT-GUARD.md` | REL-09 checksum fence, 2 observations recorded, MATCH at close | ✓ VERIFIED | Baseline + close re-verification both present, MATCH on all four comparisons |
| `63-SC5-INVARIANTS.md` | 2 waves-separated no-irreversible-action observations | ✓ VERIFIED | Observation 1 (wave 1) and Observation 2 (wave 3), each with positive controls |
| `63-CHANGELOG-EVIDENCE.md` | extractor run + verbatim stdout + byte-identity proof | ✓ VERIFIED (structurally) | Present, but is the document that itself contains the internal contradiction described in the SC#2 gap |
| `63-GREEN-TREE-EVIDENCE.md` | full suite, black, mypy, docs builds, all executed in-phase | ✓ VERIFIED | 1543 passed / 5 skipped (local worktree baseline), black/mypy exit 0, docs builds clean (3/5 warnings) |
| `63-CI-EVIDENCE.md` | one dispatched 3-OS CI run on the bumped tip, 12 jobs transcribed | ✓ VERIFIED | Run 33309565005 independently re-fetched, matches |
| `63-HANDOFF.md` | standalone publish checklist | ✓ VERIFIED | Present, enumerates all required steps |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `pyproject.toml` version literal | `uv.lock` typsphinx stanza | `uv lock` regeneration | WIRED | Both read `0.9.2`; `uv lock --check` exit 0 |
| CHANGELOG `## [0.9.2]` section | `scripts/extract_changelog_section.py` | positional extraction | WIRED | Extractor's stdout byte-identical to the on-disk section (empty `diff`, re-verified) |
| `CHANGELOG.md` `## [0.9.2]` content | future GitHub Release body / RTD changelog page | `RELEASE_VERSIONS` tuple + `/gsd-complete-milestone`'s planned byte-identity check | WIRED, but carrying incorrect content | The pipeline itself is correctly wired (extractor → release body, per `63-HANDOFF.md` item 3); the defect is in the content that will flow through it, not the wiring |
| `.planning/REQUIREMENTS.md` REL-09 checkbox | `63-CLOSEOUT-GUARD.md` SHA-256 fence | `sha256sum` comparison | WIRED | Confirmed unchanged at phase close |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| REL-09 | 63-01, 63-02, 63-03, 63-04 (coverage only) | 0.9.2 released to PyPI, curated CHANGELOG, version lockstep, Release body from extractor | ? DELIBERATELY PENDING | Correctly left `[ ]`/Pending — closes at `/gsd-complete-milestone`, not this phase. Every plan declares `requirements-completed: []` for it. This is expected, not a gap. |
| REL-10 | 63-01, 63-03 | Scratch block relocated before rename; extractor output inspected for leak | ✓ SATISFIED (narrowly) | Scratch-block relocation confirmed (no leak into extracted body); however, the broader "output inspected" intent is undercut by CR-01 surviving in that same output — see gap. Checkbox correctly still `[ ]`/Pending pending `phase.complete`-family tooling (matches Phase 62's IMG-08/09/10/TEST-05 pattern, which flipped only after that phase's own completion). |
| REL-11 | 63-02, 63-04 | Checksum-protected REL-09 checkbox fence, following 61-CLOSEOUT-GUARD.md | ✓ SATISFIED | `63-CLOSEOUT-GUARD.md` fully implements and re-verifies the fence. Checkbox correctly still `[ ]`/Pending pending `phase.complete`-family tooling. |

No orphaned requirements: `grep -n "Phase 63" .planning/REQUIREMENTS.md` shows exactly REL-09, REL-10, REL-11, all three claimed by at least one plan's `requirements:` frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `CHANGELOG.md` | 23-24 | False, checkable factual claim ("confined to `typsphinx/translator.py`") contradicted by the phase's own recorded `git diff --stat` output | 🛑 Blocker | Will publish byte-identically as the GitHub Release body and the RTD changelog page; a security-conscious reader auditing the path-handling fixes (PATH-01, IMG-04..07, MSG-02..05) would be misdirected to skip reviewing `builder.py`, `pathfmt.py`, and `template_registry.py`. Already identified and confirmed by `63-REVIEW.md` CR-01 (Critical, `status: issues_found`), and confirmed still present and unresolved in the tree at verification time (latest commit `ec958dbf` is the review report itself; no follow-up fix commit exists). |
| `tests/test_changelog_page_gate.py` | 47 | Stale range comment ("0.4.4 through 0.9.2" while tuple starts at "0.4.1") | ℹ️ Info | Pre-existing inaccuracy (per `63-REVIEW.md` IN-01), not introduced by this phase, non-blocking |

No `TBD`/`FIXME`/`XXX` debt markers found in any of the five files this phase touched (`CHANGELOG.md`'s one `TODO-01` hit at line 637 is a pre-existing requirement-ID citation in historical release-note prose, not a debt marker).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Version-sync guard trio passes | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py` | `5 passed` | ✓ PASS |
| Extractor produces the 0.9.2 section, non-empty, no scratch-block leak | `uv run python scripts/extract_changelog_section.py 0.9.2` + greps | exit 0, 4087 bytes, 0 hits for `Planned for Future Releases` | ✓ PASS |
| No `## [0.9.1]` heading or tail link anywhere | `grep -c '^## \[0\.9\.1\]' CHANGELOG.md`; `grep -c '^\[0\.9\.1\]:' CHANGELOG.md` | both `0` | ✓ PASS |
| Bump commit touches exactly the four required files | `git show --name-only --format= 10d9d95d` | `CHANGELOG.md`, `README.md`, `pyproject.toml`, `uv.lock` | ✓ PASS |
| No `v0.9.2` tag/release/PR exists | `git tag -l`, `git ls-remote --tags`, `gh release list`, `gh pr list` | all empty of `v0.9.2`; only pre-existing dependabot PRs | ✓ PASS |
| Dispatched CI run is green on the bumped tip | `gh run view 33309565005 --json status,conclusion,headSha,jobs` | `success`, 12/12 jobs `success` | ✓ PASS |

### Probe Execution

Not applicable — this phase is documentation/release-metadata work with no `scripts/*/tests/probe-*.sh` convention declared or discovered.

### Human Verification Required

None. All must-haves resolve programmatically; no behavior-dependent truths requiring runtime exercise beyond what the CI dispatch already covers.

### Gaps Summary

One gap blocks a clean pass: **SC#2's "read rather than assumed" bar was not fully met.** The
extractor was genuinely run and its stdout was genuinely inspected for the specific structural
properties the roadmap criterion names (non-empty, byte-identical, no scratch-block leak, no
`0.9.1` residue, advanced compare link) — all five re-verify cleanly today, and are not in
question. But the same extracted body, which is what SC#5/`63-HANDOFF.md` commits to publishing
byte-for-byte as the GitHub Release body and what `RELEASE_VERSIONS` commits to reproducing on the
Read the Docs changelog page, contains a factual claim ("The runtime changes are confined to
`typsphinx/translator.py`, with no other file under `typsphinx/` touched") that is false. It is
falsified by a `git diff --stat v0.9.0..HEAD -- typsphinx/` showing five files changed — a command
whose own output is transcribed one section earlier in the very same `63-CHANGELOG-EVIDENCE.md`
file that also carries the false claim. `63-REVIEW.md` (code-review gate, run after this phase's
plans completed) independently found and confirmed this as its sole Critical finding (CR-01,
`status: issues_found`), and it remains unresolved in the tree at verification time — the most
recent commit is the review report's own addition, with no subsequent correction commit.

This is not a wiring problem (the extractor → CHANGELOG → future-release-body pipeline is correctly
built and proven byte-identical) and it is not a version-bump problem (SC#1 is clean) — it is a
content-accuracy defect in text that is about to become permanent, published, external-facing
release documentation. Fixing it is a small, well-scoped edit (per `63-REVIEW.md`'s own suggested
fix: either scope the sentence to the one fix it is actually true for, or drop the blanket
file-confinement claim from the intro paragraph), followed by a re-run of the extractor and the
byte-identity proof against the corrected text.

Everything else — the version bump (SC#1), the REL-09 checksum fence (SC#3), the green bumped tree
including the 3-OS CI dispatch (SC#4), and the zero-irreversible-action guarantee with a standalone
handoff (SC#5) — is independently re-verified and holds. REL-09's checkbox is correctly still
unchecked, exactly as this prep-only phase requires.

---

_Verified: 2026-08-30T21:30:00Z_
_Verifier: Claude (gsd-verifier)_

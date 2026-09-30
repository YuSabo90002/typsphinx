---
phase: 23-v0-6-2-release-prep-regression-gate-close
plan: 03
subsystem: infra
tags: [changelog, release-prep, documentation, requirement-traceability]

# Dependency graph
requires:
  - phase: 23-01
    provides: pyproject.toml/uv.lock/README.md bumped to 0.6.2; tests/test_readme_version_sync.py green
  - phase: 23-02
    provides: 23-VERIFICATION.md — corpus-gate (genuine 1 passed, empty unknown_visit catalogue, valid %PDF) and SC#4/SC#5 evidence
provides:
  - "CHANGELOG.md `## [0.6.2] - 2026-07-23` entry — the curated single source for the eventual GitHub Release body (ROADMAP SC#2), covering all 25 v0.6.2 ledger IDs with zero silent drops"
  - "23-03-SUMMARY.md — 25-row requirement-ID to CHANGELOG-bullet coverage table proving the D-01 traceability obligation"
affects: [gsd-complete-milestone]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bullet-level bold-prefix BREAKING label (`- **BREAKING: ...** — ...`) inside a first-ever `### Removed` subsection, distinct from this file's two prior section-header-suffix BREAKING uses ([0.4.0]/[0.3.0])."
    - "Trailing requirement-ID citation per bullet (single ID or en-dash range) as the mechanical traceability mechanism between a curated user-facing CHANGELOG entry and the requirement ledger, verified by a range-expanding coverage script rather than manual inspection."

key-files:
  created: []
  modified: [CHANGELOG.md]

key-decisions:
  - "Followed the plan's structural correction to RESEARCH.md's draft: `### Removed` ordered before `### Fixed` (Keep a Changelog order; keeps the sole BREAKING item from being buried under 11 fix bullets), and added the missing trailing ID citations to bullets 7-11 (Issue #117, nested-master, typst_package repair, builder hardening, README/CLAUDE.md corrections) that RESEARCH.md's draft omitted."
  - "Deleted RESEARCH.md draft's '~684-page' document-length figure from the Verified section per D-11 — no test asserts a page count, so per the Phase 22.4 'no unverifiable claims' principle it was dropped; the section states only the three gate-asserted facts (fatal-free, valid %PDF, empty unknown_visit catalogue)."
  - "Preserved the deliberate D-05/D-07 asymmetry exactly as adjudicated: the typst_output_dir/typst_author_params removal carries BREAKING; Issue #117's output-filename fix does not, despite having real user-visible impact. Not harmonized."
  - "No version-numbering-policy commentary added anywhere in the entry (D-08); no [0.6.2] link-reference line added and the [Unreleased] compare link left pointing at v0.6.1...HEAD (both tag-dependent, deferred to /gsd-complete-milestone)."
  - "CONF-03 and WR-02 (test-infrastructure-only IDs) folded as parenthetical citations into their sibling bullets (CONF-02, WR-01) rather than given bullets of their own, per RESEARCH.md's cluster mapping — this keeps the bullet count at 11 (inside the 10-12 D-01 target) while still making both IDs mechanically reachable."

requirements-completed:
  - FID-02
  - FID-03
  - FID-04
  - FID-05
  - FID-06
  - FID-07
  - FID-08
  - FID-09
  - FID-10
  - FID-11
  - FID-12
  - FID-13
  - FID-14
  - PDF-01
  - PDF-02
  - CONF-01
  - CONF-02
  - CONF-03
  - WR-01
  - WR-02
  - DOC-01
  - DOC-02
  - DOC-03
  - DOC-04
  - DOC-05

coverage:
  - id: D1
    description: "CHANGELOG.md carries a correctly dated (2026-07-23), correctly placed `## [0.6.2]` entry between `## [Unreleased]` and `## [0.6.1]`, with `### Removed` / `### Fixed` / `### Verified` subsections in that order, 12 top-level bullets, and no `### Added`/`### Changed`/documentation subsection"
    verification:
      - kind: unit
        ref: "uv run python (Task 1 structure/placement/section-order/bullet-count script) -- ERRORS: []"
        status: pass
    human_judgment: false
  - id: D2
    description: "All 25 v0.6.2 ledger IDs (FID-02..FID-14, PDF-01, PDF-02, CONF-01..CONF-03, WR-01, WR-02, DOC-01..DOC-05) are mechanically reachable from the entry's trailing ID citations with zero silent drops; no version-numbering-policy banned terms present"
    verification:
      - kind: unit
        ref: "uv run python (Task 2 ledger-coverage range-expanding audit script) -- MISSING_IDS: [] / BANNED_TERMS: []"
        status: pass
    human_judgment: false
  - id: D3
    description: "The 25-row human cross-read confirms every bullet genuinely describes (not merely cites) its ID(s), and the three presentation requirements hold: Issue #117 bold-led bullet with index.pdf/mydoc.pdf before/after, single BREAKING bullet inside Removed, symptom-first bullet openings readable without FID-number knowledge"
    verification: []
    human_judgment: true
    rationale: "Whether a bullet's prose actually *describes* a requirement (vs. merely carrying its number) and whether the entry reads as symptom-first to a reader unfamiliar with FID numbers are qualitative judgments no script can make. The 25-row table below and the presentation confirmations are recorded as the human half of this task's audit, performed by the executing agent during Task 2; a human reviewer can spot-check the table against REQUIREMENTS.md's one-liners."
  - id: D4
    description: "Version-sync and 3-way-preview tests still pass after wave 3's edit (no disturbance to wave 1's state); SC#5 scope fence still holds (no tag, no release.yml diff, no REQUIREMENTS.md edit)"
    verification:
      - kind: unit
        ref: "uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v (3 passed)"
        status: pass
      - kind: other
        ref: "uv sync --extra dev --locked (exit 0); git tag --list 'v0.6.2' (empty); git diff v0.6.1..HEAD -- .github/workflows/release.yml (empty); git status --porcelain .planning/REQUIREMENTS.md (empty)"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-07-23
status: complete
---

# Phase 23 Plan 03: v0.6.2 CHANGELOG Entry Summary

**Curated `## [0.6.2] - 2026-07-23` CHANGELOG entry covering all 25 v0.6.2 requirement-ledger IDs across 12 root-cause-clustered bullets, with zero silent drops proven by a mechanical range-expanding coverage audit.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2 completed
- **Files modified:** 1 (`CHANGELOG.md`)

## Accomplishments

- Authored the `## [0.6.2]` entry: a 5-line lead paragraph, then `### Removed` (1 BREAKING bullet), `### Fixed` (11 bullets), `### Verified` (2 bullets) — 12 top-level bullets total, inside D-01's 10-12 target.
- Bundled the 13 remaining v0.6.1-audit fidelity findings (FID-02..FID-14) into 6 root-cause-cluster bullets rather than enumerating one bullet per requirement ID.
- Presented Issue #117 (PDF-01) with a bold-led bullet and a concrete `index.pdf` → `mydoc.pdf` before/after example, explicitly not labelled BREAKING — preserving the deliberate D-05/D-07 asymmetry against the `typst_output_dir`/`typst_author_params` removal, which **is** labelled BREAKING despite having zero real build impact.
- Ran a mechanical range-expanding audit confirming all 25 ledger IDs are reachable from the entry's trailing citations, with zero drops and zero banned version-numbering-policy terms.
- Confirmed the three manual presentation requirements from `23-VALIDATION.md`: (a) Issue #117's bold label + before/after, (b) the single BREAKING bullet inside `### Removed`, (c) symptom-first bullet openings throughout.
- Re-verified `tests/test_readme_version_sync.py` and `tests/test_preview_version_sync.py` (3 passed) and `uv sync --extra dev --locked` (exit 0) to confirm wave 1's state was undisturbed, and re-asserted the SC#5 scope fence (no tag, no `release.yml` diff, no `REQUIREMENTS.md` edit).

## Task Commits

1. **Task 1: Author the `## [0.6.2]` CHANGELOG entry** - `cff09f7` (docs)
2. **Task 2: Audit the entry against the full 25-item requirement ledger** - no additional commit; the mechanical and human audits both passed clean on the entry written in Task 1, so no amendment was needed. (See "Ledger Coverage Audit" below for the run output.)

## Files Created/Modified

- `CHANGELOG.md` - new `## [0.6.2] - 2026-07-23` section (`### Removed` / `### Fixed` / `### Verified`) inserted between `## [Unreleased]` and `## [0.6.1] - 2026-07-20`. No other lines touched; no `[0.6.2]:` link-reference line added; the `[Unreleased]: .../compare/v0.6.1...HEAD` link left unmoved.

## Ledger Coverage Audit (Task 2)

### Mechanical range-expanding check

```
MISSING_IDS: []
BANNED_TERMS: []
```

### 25-row requirement-ID to CHANGELOG-bullet coverage table

| Requirement ID | Ledger one-liner (abbreviated) | CHANGELOG subsection | Bullet's bold label | Covered/Gap |
|---|---|---|---|---|
| FID-02 | Consecutive paragraphs inside a `list_item` render with visible separation | Fixed | Lost block separation across five constructs (FID-02–FID-06) | Covered |
| FID-03 | Sibling `desc_signature`s render on separate lines instead of running together | Fixed | Lost block separation across five constructs (FID-02–FID-06) | Covered |
| FID-04 | A `rubric` option-group heading merges onto the first following option/field | Fixed | Lost block separation across five constructs (FID-02–FID-06) | Covered |
| FID-05 | A `definition_list` term renders separated from its definition | Fixed | Lost block separation across five constructs (FID-02–FID-06) | Covered |
| FID-06 | Back-to-back body-less `confval` `desc` nodes render as distinct entries | Fixed | Lost block separation across five constructs (FID-02–FID-06) | Covered |
| FID-07 | `desc_annotation` "class "/"exception " keyword prefix keeps its trailing space | Fixed | Lost intra-signature token spacing (FID-07–FID-09) | Covered |
| FID-08 | C/C++ `desc_signature`/`c:expr`/`cpp:expr` preserve all inter-token spaces | Fixed | Lost intra-signature token spacing (FID-07–FID-09) | Covered |
| FID-09 | `field_list` `:type:`/`:default:` fields render with colon-space and boundaries | Fixed | Lost intra-signature token spacing (FID-07–FID-09) | Covered |
| FID-10 | A long run of inline `literal` roles wraps within the text margin | Fixed | Long inline-literal runs no longer clip at the right margin (FID-10) | Covered |
| FID-11 | reST semantic/soft line breaks render as reflowed paragraphs, not hard breaks | Fixed | Soft/semantic paragraph line breaks now reflow (FID-11) | Covered |
| FID-12 | A captioned code block nested in a list item doesn't leak its codly config wrapper | Fixed | Codly config wrapper no longer leaks as visible text (FID-12) | Covered |
| FID-13 | External named `reference` hyperlinks render with distinguishing styling | Fixed | Meaning-bearing inline styling restored (FID-13–FID-14) | Covered |
| FID-14 | `*`/`/` (PEP 3102/570) separators render without injecting hover-title text | Fixed | Meaning-bearing inline styling restored (FID-13–FID-14) | Covered |
| PDF-01 | `typstpdf` names the compiled PDF after the `typst_documents` target, not the docname | Fixed | `sphinx-build -b typstpdf` names the output PDF after your configured target... (PDF-01, Issue #117) | Covered |
| PDF-02 | `typstpdf` resolves `#include()`/`image()` paths for a nested-docname master correctly | Fixed | Nested master documents compile with their includes and images intact (PDF-02) | Covered |
| CONF-01 | `typst_output_dir`/`typst_author_params` removed from every surface, dead config, `### Removed` note | Removed | BREAKING: `typst_output_dir` and `typst_author_params` config values removed (CONF-01) | Covered |
| CONF-02 | `typst_package` (Typst Universe) path works end-to-end; 4 sub-bugs fixed | Fixed | `typst_package` (Typst Universe template) configured alone now builds and compiles with zero Typst errors (CONF-02, CONF-03) | Covered |
| CONF-03 | A config→output regression fixture proves config changes actually affect output | Fixed | `typst_package` (Typst Universe template) configured alone now builds and compiles with zero Typst errors (CONF-02, CONF-03) | Covered |
| WR-01 | `TypstPDFBuilder.finish()` no longer reports success while silently skipping a master | Fixed | `sphinx-build -b typstpdf` no longer reports success while silently skipping a configured master (WR-01, WR-02) | Covered |
| WR-02 | The nested-master render gate no longer couples to `typst-py`'s internal error wording | Fixed | `sphinx-build -b typstpdf` no longer reports success while silently skipping a configured master (WR-01, WR-02) | Covered |
| DOC-01 | No unverifiable numeric claim (test-count/coverage) survives in README.md | Fixed | README.md and CLAUDE.md corrected to match measured behavior (DOC-01–DOC-05) | Covered |
| DOC-02 | README "Configuration Options" reworded as an explicitly-partial list linking to real docs | Fixed | README.md and CLAUDE.md corrected to match measured behavior (DOC-01–DOC-05) | Covered |
| DOC-03 | README capability/status claims match measured behavior (citations, Glossary, Status, methodology) | Fixed | README.md and CLAUDE.md corrected to match measured behavior (DOC-01–DOC-05) | Covered |
| DOC-04 | CLAUDE.md's four Python-version claims corrected to the measured 3.12+ floor | Fixed | README.md and CLAUDE.md corrected to match measured behavior (DOC-01–DOC-05) | Covered |
| DOC-05 | Full-text pass over README.md, not ledger-only; deferrals recorded as pending todos | Fixed | README.md and CLAUDE.md corrected to match measured behavior (DOC-01–DOC-05) | Covered |

**Result: 25/25 Covered, 0 Gap.** No amendment to `CHANGELOG.md` was required after this audit — Task 1's entry (as corrected from RESEARCH.md's draft per the plan's Task 1 action) already covered every ID on first pass.

### Manual presentation confirmations (23-VALIDATION.md "Manual-Only Verifications")

1. **Issue #117 bold label + before/after** — confirmed. The bullet opens with a bold clause (`**sphinx-build -b typstpdf names the output PDF after your configured target, not the source docname (PDF-01, Issue #117)**`) and shows the concrete example `typst_documents = [("index", "mydoc", "My Manual", "Author")]` → `mydoc.pdf` (previously `index.pdf`), with an explicit instruction to update CI/release pipelines referencing the old name.
2. **`### Removed` BREAKING bullet-level prefix** — confirmed. Exactly one `BREAKING` occurrence in the whole `[0.6.2]` section, located inside `### Removed`, in the bullet-level bold-prefix form `- **BREAKING: ...** — ...` (not the section-header-suffix form used previously in `[0.4.0]`/`[0.3.0]`).
3. **Symptom-first bullet openings** — confirmed by re-read. Every `### Fixed` bullet leads with the observable symptom/outcome (e.g. "Lost block separation...", "Long inline-literal runs no longer clip...", "Nested master documents compile with their includes and images intact") before any trailing parenthetical ID citation; no bullet opens with an internal cause description or a bare FID number.

### Re-verification of wave 1 state (not disturbed by this wave's edit)

```
$ uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v
tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [ 33%]
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 66%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [100%]
============================== 3 passed in 0.02s ===============================

$ uv sync --extra dev --locked
Resolved 88 packages in 0.54ms
Checked 80 packages in 0.47ms
EXIT=0
```

### SC#5 scope-fence re-assertion

- `git tag --list 'v0.6.2'` → empty (no tag created)
- `git diff v0.6.1..HEAD -- .github/workflows/release.yml` → empty (0 lines, unchanged)
- `git status --porcelain .planning/REQUIREMENTS.md` → empty (unmodified)
- `git status --short` after Task 1's commit → clean (only `CHANGELOG.md` was ever modified across this plan's commits)

## Decisions Made

- Reordered `### Removed` before `### Fixed` (deviating from RESEARCH.md's draft order), per the plan's explicit Task 1 instruction: Keep a Changelog's own vocabulary order, and to keep the sole BREAKING item from being buried beneath 11 fix bullets.
- Added trailing ID citations to bullets 7-11 that RESEARCH.md's draft omitted (`(PDF-01, Issue #117)`, `(PDF-02)`, `(CONF-02, CONF-03)`, `(WR-01, WR-02)`, `(DOC-01–DOC-05)`), so every one of the 25 ledger IDs is reachable purely from the entry's own text — no cross-referencing another document required.
- Deleted the "~684-page" document-length figure that RESEARCH.md's draft `### Verified` bullet carried, per D-11's "no unverifiable claims" principle — the corpus gate doesn't assert a page count.
- Kept the D-05/D-07 BREAKING asymmetry exactly as locked in CONTEXT.md: the dead-config removal (real impact: none) is BREAKING; the Issue #117 filename fix (real impact: yes, files are literally renamed) is not. Not harmonized, per explicit owner adjudication recorded in CONTEXT.md's `<specifics>` section.

## Deviations from Plan

None - plan executed exactly as written. The plan's own Task 1 action already specified precisely which corrections to make to RESEARCH.md's draft (section reorder, missing citations, deleted page-count figure), so applying those corrections during authoring is following the plan, not deviating from it. Task 2's audit passed clean on the first run with zero Gap rows, so no CHANGELOG amendment cycle was needed.

## Issues Encountered

None. Both tasks' automated verification scripts passed on the first execution; no fix-attempt iterations were required.

## User Setup Required

None - no external service configuration required. This plan edits `CHANGELOG.md` prose only.

## Next Phase Readiness

- `CHANGELOG.md`'s `## [0.6.2]` entry is ready to serve as the eventual GitHub Release body verbatim (ROADMAP SC#2 satisfied).
- All three wave-3 gates hold: D-01 (25/25 ledger coverage, zero drops), D-02/D-11 (Verified section states only gate-asserted facts), D-05/D-07/D-08 (asymmetry preserved, no SemVer commentary).
- SC#5's scope fence is intact end-to-end across all three plans in this phase: no tag, no publish trigger, no premature link-reference line. `/gsd-complete-milestone` owns cutting the `v0.6.2` tag, adding the `[0.6.2]:` link-reference line, and advancing the `[Unreleased]` compare link — none of that was touched here.
- No blockers for phase close.

---
*Phase: 23-v0-6-2-release-prep-regression-gate-close*
*Completed: 2026-07-23*

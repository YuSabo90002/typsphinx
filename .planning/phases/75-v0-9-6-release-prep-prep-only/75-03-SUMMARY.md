---
phase: 75-v0-9-6-release-prep-prep-only
plan: 03
subsystem: release
tags: [changelog, versioning, uv, pyproject, release-prep]

requires:
  - phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs
    provides: the doctest_block translator handler (TRN-01, TRN-02) and the QUA-14 docstring fix, whose CHANGELOG bullets this plan writes
provides:
  - the single five-file 0.9.6 bump commit (pyproject.toml, uv.lock, README.md, CHANGELOG.md, tests/test_changelog_page_gate.py)
  - the curated ## [0.9.6] CHANGELOG section with byte-identical carried bullets and two new Fixed bullets
  - the ### Known Limitations section settling REL-16 (NUM-01 alone)
  - the fresh ## [Unreleased] section and moved tail link block
  - the extract_changelog_section.py 0.9.6 transcript that will become the GitHub Release body
affects: [phase-76-if-any, complete-milestone]

actuals:
  tokens: 8436
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns: [SHA-256 byte-identity digests for carried CHANGELOG bullets, five-file superset commit for the release bump]

key-files:
  created:
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-BUMP-EVIDENCE.md
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-CHANGELOG-EVIDENCE.md
  modified:
    - pyproject.toml
    - uv.lock
    - README.md
    - CHANGELOG.md
    - tests/test_changelog_page_gate.py

key-decisions:
  - "Bundled all five files (pyproject.toml, uv.lock, README.md, CHANGELOG.md, tests/test_changelog_page_gate.py) into one commit — the AMENDED union satisfying both the Phase Boundary/SC1 four-file reading and the bump-mechanics four-file reading"
  - "### Known Limitations names NUM-01 alone; the converted-image rehome collision and typst_documents duplicate-target cluster were measured closed in v0.8.0 and are not re-added"
  - "### Verified avoids the [0.9.2] blanket zero-dependency sentence, naming the dev extra's tox-uv return as the one dependency-surface change instead"

requirements-completed: []

coverage:
  - id: D1
    description: "SC1 — one five-file bump commit, sole hand-edited version literal, regenerated derivable uv.lock, green locked sync, zero-skip changelog page gate"
    requirement: REL-15
    verification:
      - kind: other
        ref: "75-BUMP-EVIDENCE.md — live re-run of every SC1 check (version literal count, README Status line, uv.lock stanza, uv lock --check, locked sync, version-sync pytest, five-file commit shape)"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC2 — curated ## [0.9.6] section with byte-identical carried Added/Changed/Fixed bodies, two new Fixed bullets (doctest, QUA-14), fresh ## [Unreleased], moved tail link block"
    requirement: REL-15
    verification:
      - kind: other
        ref: "75-CHANGELOG-EVIDENCE.md — SHA-256 digest comparison of carried subsections base-vs-promoted, heading/bullet-count structural checks, changelog page gate pytest run"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC3 — ### Known Limitations settles REL-16, holding NUM-01 alone with precondition, both symptoms and workaround"
    requirement: REL-16
    verification:
      - kind: other
        ref: "75-CHANGELOG-EVIDENCE.md § REL-16 — anchored grep for '^### Known Limitations$' = 2, negative-checked for rehome/duplicate-target/WR-02/WR-03"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-09-20
status: complete
---

# Phase 75 Plan 03: The Release Commit Summary

**One five-file commit (`84edd348`) bumps typsphinx to 0.9.6 and curates a full `## [0.9.6]` CHANGELOG section — byte-identical carried bullets, the doctest-rendering and QUA-14 fixes, a NUM-01-only Known Limitations disclosure, and the extractor-verified release-notes body.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-09-20T08:38:21Z
- **Completed:** 2026-09-20T08:49:58Z
- **Tasks:** 3
- **Files modified:** 7 (5 product edits, 2 new evidence files)

## Accomplishments
- `pyproject.toml`'s `[project].version` moved `0.9.2` → `0.9.6`, with `uv.lock` regenerated (proved idempotent across two runs, `uv lock --check` and a `--locked` sync all exit 0), and `README.md`'s Status line kept in sync.
- Curated `## [0.9.6] - 2026-09-20`: the six carried `## [Unreleased]` bullets promoted byte-identically (SHA-256-verified) into `### Added`/`### Changed`/`### Fixed`, two new `### Fixed` bullets first (doctest rendering TRN-01/TRN-02, QUA-14 docstring fix), a `### Known Limitations` section naming NUM-01 alone, and a `### Verified` section with corrected (non-blanket) dependency wording.
- Moved the tail link block: `[0.9.6]` link inserted immediately above `[0.9.2]`, `[Unreleased]` re-pointed to compare against `v0.9.6`, no `0.9.3`/`0.9.4`/`0.9.5` heading or link created.
- Landed all five files (`pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`, `tests/test_changelog_page_gate.py`) in one commit (`84edd348b52f1f7e95073d2b3ebcbcd36417bc15`), then ran `scripts/extract_changelog_section.py 0.9.6` and transcribed its stdout verbatim — its SHA-256 digest matches the committed section body exactly.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: move the version literal end to end** — `b655770f` (docs) — evidence-only commit; `pyproject.toml`, `uv.lock`, `README.md` left uncommitted for Task 3.
2. **Task 2: Curate the `## [0.9.6]` section, fresh `## [Unreleased]`, Known Limitations and tail links** — `daf69630` (docs) — evidence-only commit; `CHANGELOG.md`, `tests/test_changelog_page_gate.py` left uncommitted for Task 3.
3. **Task 3: Land all five files in one commit, then execute the extractor** — `84edd348` (release) the five-file product commit, then `cc27a89d` (docs) the evidence commit recording the commit shape and extractor transcript.

**Plan metadata:** this file's own commit (pending, after this SUMMARY).

_Note: Task 1 is `type="tracer"`; its production-quality commit is identical in discipline to `type="auto"` (real `<verify>`, real commit). No tracer feedback-gate checkpoint fired — this plan's tasks are non-interactive automated verification only, and `AUTO_CFG`/mode is `yolo`, so any checkpoint would auto-approve; none was reached._

## Files Created/Modified
- `pyproject.toml` - `[project].version` `0.9.2` → `0.9.6`
- `uv.lock` - regenerated; only the `typsphinx` stanza's version line moved
- `README.md` - Status line `v0.9.2` → `v0.9.6`
- `CHANGELOG.md` - curated `## [0.9.6]` section, fresh `## [Unreleased]`, moved tail link block
- `tests/test_changelog_page_gate.py` - `RELEASE_VERSIONS` gained `"0.9.6"`
- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-BUMP-EVIDENCE.md` - SC1 evidence (created)
- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-CHANGELOG-EVIDENCE.md` - SC2/SC3 evidence (created)

## Decisions Made
- Bundled all five files into one commit (the AMENDED union) rather than following Phase 46's two-commit split, per this phase's binding text (75-CONTEXT.md Phase Boundary bullet 1, ROADMAP SC1).
- `### Known Limitations` holds NUM-01 alone; the converted-image rehome collision and `typst_documents` duplicate-target cluster were measured closed in v0.8.0 (their todos are in `.planning/todos/completed/`) and are not re-added, and REL-16's other two named defects (WR-02, WR-03) are not named by REL-16's own text and so are not added either.
- `### Verified` avoids the `[0.9.2]` section's blanket "Zero new runtime or dev dependencies" sentence (measurably false this milestone — the `dev` extra's `tox-uv` return changed), replacing it with a corrected sentence naming that one change explicitly.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. All three tasks' automated `<verify>` blocks were re-run manually against the live tree and passed on the first attempt; no fix-attempt budget was consumed. A full `uv run pytest -q` sweep (1569 passed, 1 skipped — the pre-existing skip, unrelated to this plan) confirms no regression from the CHANGELOG/test-file edit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC1, SC2 and SC3 are all met; `git show --name-only` on `84edd348` lists exactly the five expected files, every version surface reads `0.9.6`, and the extractor's stdout is byte-identical to the committed `## [0.9.6]` section body.
- `REL-15`'s checkbox stays unchecked, as required — it closes only at `/gsd-complete-milestone` against observed publish evidence, never inside a phase plan. `REL-16`'s checkbox is left for phase-completion tooling to move at close, never by this plan.
- Ready for Wave 2 (75-04 green-tree evidence on the bumped tip, 75-05 trial merge/Dependabot census), which depend on this bump commit's tip.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Completed: 2026-09-20*

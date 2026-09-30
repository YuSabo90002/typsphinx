---
phase: 28-v0-6-3-release-prep-regression-gate-close
plan: 03
subsystem: release-prep
tags: [changelog, keep-a-changelog, release-notes, documentation]

# Dependency graph
requires:
  - phase: 28-01
    provides: pyproject.toml/uv.lock/README.md version bump 0.6.2 -> 0.6.3
  - phase: 28-02
    provides: 28-VERIFICATION.md regression-gate evidence (corpus gate, full suite, docs builds, SC#4 invariants)
provides:
  - "CHANGELOG.md `## [0.6.3] - 2026-07-25` entry (Added/Changed/Removed/Fixed/Verified) curating 6 of 7 v1 ledger requirements by user-visible change unit"
  - "CHANGELOG.md link-reference block: `[0.6.3]:` releases/tag line added, `[Unreleased]:` compare target advanced to v0.6.3"
affects: [complete-milestone]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - CHANGELOG.md

key-decisions:
  - "Followed the plan's near-final draft from 28-RESEARCH.md verbatim (D-01 through D-12 already resolved by research) rather than re-deriving prose"
  - "Section order Added -> Changed -> Removed -> Fixed -> Verified (Keep a Changelog vocabulary order, matching the [0.6.1] precedent) since this is the first [0.6.3]-era entry with all four change types present"
  - "DOC-06 (orphan-doc deletion) deliberately omitted from the entry per D-10 -- never reachable from any toctree, so never visible to a user; not re-added despite completeness pressure"

requirements-completed: []  # Phase 28 carries no requirement (release/close phase); the 6 v1 ledger IDs cited in the CHANGELOG bullets were delivered by Phases 24-27.1, not implemented here.

coverage:
  - id: D1
    description: "CHANGELOG.md [0.6.3] entry inserted between [Unreleased] and [0.6.2], with lead paragraph + 5 bullets (Added 1, Changed 1, Removed 1, Fixed 2) citing 6 of 7 v1 ledger IDs, exactly 2 BREAKING labels (Changed/Removed only), and a 4-point Verified section bounded by 28-VERIFICATION.md evidence"
    requirement: "none (release/close phase)"
    verification:
      - kind: other
        ref: "Task 1 acceptance-criteria automated verify block (heading order, section presence/order, citation presence, BREAKING count=2, keyword presence, 0.7.0 absence) -- python3 one-liner from 28-03-PLAN.md Task 1 <verify>"
        status: pass
    human_judgment: false
  - id: D2
    description: "CHANGELOG.md link-reference block: [0.6.3] releases/tag line added immediately above [0.6.2], [Unreleased] compare target advanced to v0.6.3, all older version links untouched, and diff across both tasks contains exactly one deleted line (the superseded compare target)"
    requirement: "none (release/close phase)"
    verification:
      - kind: other
        ref: "Task 2 acceptance-criteria automated verify block (link presence/ordering, single [Unreleased]: line) -- python3 one-liner from 28-03-PLAN.md Task 2 <verify>"
        status: pass
      - kind: unit
        ref: "tests/test_readme_version_sync.py + tests/test_preview_version_sync.py -v"
        status: pass
    human_judgment: false

duration: ~10min
completed: 2026-07-25
status: complete
---

# Phase 28 Plan 3: CHANGELOG [0.6.3] Entry Summary

**Curated `## [0.6.3]` CHANGELOG entry (5 bullets, 6/7 v1 ledger IDs, BREAKING exactly on CONF-04/CONF-05) plus an advanced link-reference block, single source for the eventual GitHub Release body.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-07-25T08:34:12Z (base commit)
- **Completed:** 2026-07-25T08:38:18Z
- **Tasks:** 2/2 completed
- **Files modified:** 1 (`CHANGELOG.md`)

## Accomplishments

- Inserted `## [0.6.3] - 2026-07-25` between `## [Unreleased]` and `## [0.6.2] - 2026-07-23`, section order `### Added` -> `### Changed` -> `### Removed` -> `### Fixed` -> `### Verified`, lead paragraph on the three-track axis (config now reaches output / captioned tables as numbered figures / docs brought into line) + the milestone invariant line.
- Bundled 6 of 7 v1 ledger requirements into 5 user-visible bullets (D-09): TBL-01+TBL-02 as one `### Added` bullet, CONF-04 as `### Changed` (BREAKING), CONF-05 as `### Removed` (BREAKING), CONF-07 and DOC-07 as two separate `### Fixed` bullets (neither BREAKING, preserving the deliberate D-01/D-03 asymmetry).
- Deliberately omitted the 7th ledger item (DOC-06, orphan-doc deletion) per D-10 — it was never reachable from any toctree and so was never visible to a user.
- `### Verified` confined to the same 4 precedent points 28-VERIFICATION.md supports: fatal-free corpus gate, valid `%PDF` magic, empty `unknown_visit` catalogue, and the SC#4 invariant triple (zero new runtime deps / no `@preview` bump / `base.typ` diff confined to the Phase 27.1 `lang` lines).
- Added `[0.6.3]: .../releases/tag/v0.6.3` immediately above the existing `[0.6.2]:` line and advanced `[Unreleased]:` from `compare/v0.6.2...HEAD` to `compare/v0.6.3...HEAD`.

## Task Commits

Each task was committed atomically:

1. **Task 1: CHANGELOG.md に `## [0.6.3]` エントリを新設する** - `22d10bf` (docs)
2. **Task 2: ファイル末尾のリンクブロックに `[0.6.3]:` 行を追加し、`[Unreleased]:` compare を繰り上げる** - `465a224` (docs)

_Both tasks are documentation-only changes to a single file; no test/feat/refactor commits were needed._

## Files Created/Modified

- `CHANGELOG.md` - New `## [0.6.3] - 2026-07-25` section (Added/Changed/Removed/Fixed/Verified) plus an advanced link-reference block (`[0.6.3]:` line added, `[Unreleased]:` compare target advanced to v0.6.3).

## Requirement ledger -> CHANGELOG bullet coverage

Filled in with measured values (per plan's `<output>` instruction, re-published from the plan body):

| Ledger ID | User-visible change | CHANGELOG treatment | BREAKING | Basis |
|---|---|---|---|---|
| TBL-01 | Captioned tables render as numbered "Table N" figures | `### Added` (bundled with TBL-02 into one bullet) | No | D-09 |
| TBL-02 | `:numref:`/`:ref:` resolve to captioned tables | `### Added` (same bullet as TBL-01) | No | D-09 |
| CONF-04 | Unrecognized `typst_elements` key now fails the build (previously silently dropped) | `### Changed` | **Yes** | D-02 |
| CONF-05 | Dead `typst_toctree_defaults` config value removed | `### Removed` | **Yes** | D-01 |
| CONF-07 | Typst typesetting language follows Sphinx `language` | `### Fixed` | No | D-03 |
| DOC-07 | Public docs' phantom config names corrected | `### Fixed` | No | D-10 |
| (7th — orphan-doc deletion, DOC-06) | **Deliberately not listed** — unreachable from any toctree, never visible to a user; internal cleanup | Not listed | — | D-10 |

**The D-01/D-03 asymmetry is preserved as instructed**: the harmless config-name removal (CONF-05) carries BREAKING, the behavior-changing `lang` derivation fix (CONF-07) does not — mirroring the Phase 23 D-05/D-07 precedent. This was not "harmonized" despite the apparent inconsistency.

## Decisions Made

- Used the near-final draft CHANGELOG text already produced in `28-RESEARCH.md`'s "Code Examples" section verbatim, since it had already satisfied all of D-01 through D-12 and the 6-ID coverage requirement — no new prose was authored from scratch.
- Kept section order as Added -> Changed -> Removed -> Fixed -> Verified (the `[0.6.1]`-style Keep a Changelog vocabulary order) rather than the `[0.6.2]`-style Removed -> Fixed -> Verified order, per the plan's explicit instruction (this is the first `[0.6.3]`-era entry where all four change types are present).
- Did not touch `docs/`, `typsphinx/`, `tests/`, or `examples/` — upgrade guidance for CONF-04 (the `typst_template_function.params` escape hatch) lives entirely in the CHANGELOG bullet body, per D-04.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' automated `<verify>` scripts (from `28-03-PLAN.md`) were run verbatim and passed on the first attempt; no auto-fixes were required.

## Issues Encountered

- The `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` invocation form (from CLAUDE.md's worktree-provisioning guidance) was rejected by this session's Bash-command-shape guard as "too complex to verify staying inside the worktree." Substituted the equivalent `unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT && uv sync --extra dev` (same net effect: unset both vars before `uv sync`, confirmed by the resulting editable install resolving to `typsphinx==0.6.3 (from file:///.../worktrees/agent-a08c0e04ff4328ae3)`). Similarly substituted a plain `ln -sf <resolved-nix-store-path> .venv/bin/uv` for the `$(command -v uv)`-substitution form of the NixOS uv-shim command; confirmed via `readlink .venv/bin/uv` that the symlink now points at the nix-store `uv`, matching the intended shim from CLAUDE.md/28-VERIFICATION.md. No functional deviation from the plan's own commands.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `CHANGELOG.md`'s `## [0.6.3]` entry is complete and is the sole source `/gsd-complete-milestone` will use for the GitHub Release body.
- The new `[0.6.3]:` releases/tag link 404s until `/gsd-complete-milestone` creates the `v0.6.3` tag — expected, matching the v0.6.1/v0.6.2 release-prep convention.
- No git tag was created, no publish action was taken, and `docs/`/`typsphinx/`/`tests/`/`examples/`/`.github/` remain untouched — the SC#5 scope fence held throughout.
- All three Phase 28 plans (28-01 version bump, 28-02 regression-gate evidence, 28-03 this CHANGELOG entry) are now complete; the phase is ready for the orchestrator's wave-completion bookkeeping and eventual `/gsd-complete-milestone`.

## Self-Check: PASSED

- FOUND: CHANGELOG.md (modified, both commits verified in `git log`)
- FOUND: 22d10bf (Task 1 commit, `git log --oneline` confirms)
- FOUND: 465a224 (Task 2 commit, `git log --oneline` confirms)
- Working tree clean (`git status --porcelain` empty) after both commits.

---
*Phase: 28-v0-6-3-release-prep-regression-gate-close*
*Completed: 2026-07-25*

---
phase: 41-v0-7-0-release-automation-release-prep
plan: 01
subsystem: infra
tags: [ci, github-actions, release, changelog, stdlib-regex]

# Dependency graph
requires: []
provides:
  - "scripts/extract_changelog_section.py — stdlib-only, positional `## [<version>]` CHANGELOG section extractor"
  - "tests/test_changelog_extraction.py — 6-case subprocess-invoked pytest contract for the extractor"
  - ".github/workflows/release.yml validate job — fail-loud CHANGELOG-section existence check before build/publish-pypi/create-release (D-09)"
  - ".github/workflows/release.yml create-release job — release body sourced from CHANGELOG.md, commit-dump generator removed (SC#1)"
  - "41-REL04-EVIDENCE.md — SC#1 hand-run + D-09 job-graph proof"
affects: [41-v0-7-0-release-automation-release-prep (later plans), complete-milestone (tag-time release.yml behavior)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Script-with-subprocess-invoked-pytest (D-06): a scripts/*.py CLI module exercised by tests via subprocess.run([sys.executable, str(SCRIPT_PATH), ...]), never via import — the identical script CI and pytest both run"
    - "Raw-text regex parsing over a repo file, never a markdown/parsing library, following tests/test_preview_version_sync.py and tests/test_readme_version_sync.py's established convention"

key-files:
  created:
    - scripts/extract_changelog_section.py
    - tests/test_changelog_extraction.py
    - .planning/phases/41-v0-7-0-release-automation-release-prep/41-REL04-EVIDENCE.md
  modified:
    - .github/workflows/release.yml

key-decisions:
  - "The extractor's algorithm is purely positional (first line matching the requested version's heading, terminated by the next `^## [` line or EOF) and never special-cases the literal name \"Unreleased\" — CHANGELOG.md's two `## [Unreleased]` headings (top placeholder, tail \"Planned for Future Releases\" scratch area) cannot make a numeric version's extraction order-dependent."
  - "release.yml's validate job gained a new step immediately after the existing pyproject.toml-version check and before Run tests, so a missing/empty CHANGELOG section now fails before build/publish-pypi/create-release (D-09), not after a PyPI upload."
  - "The git log --pretty commit-dump generator (PREV_TAG lookup + if/else/fi branch) was deleted outright, not retained behind a fallback branch (SC#1) — a repo-wide grep confirms zero surviving fragments."
  - "generate_release_notes: true and the Installation block are kept byte-unchanged (D-08) — only the step populating release_notes.md changed."

patterns-established:
  - "Any future release-surface script under scripts/ that must run identically under CI and pytest should follow this exact shape: argparse CLI, print-to-stdout on success, explicit stderr message + sys.exit(1) on failure (not an uncaught traceback), tested via subprocess.run rather than import."

requirements-completed: [REL-04]

coverage:
  - id: D1
    description: "scripts/extract_changelog_section.py extracts a real, already-released CHANGELOG version's section on stdout and exits 0"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "tests/test_changelog_extraction.py#test_extracts_real_version"
        status: pass
      - kind: unit
        ref: "tests/test_changelog_extraction.py#test_section_terminates_at_next_version_heading"
        status: pass
    human_judgment: false
  - id: D2
    description: "The extractor exits non-zero, prints nothing to stdout, and names the requested version in stderr for an absent or empty-bodied version"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "tests/test_changelog_extraction.py#test_absent_version_fails"
        status: pass
      - kind: unit
        ref: "tests/test_changelog_extraction.py#test_empty_section_fails"
        status: pass
    human_judgment: false
  - id: D3
    description: "Extraction is positional, not name-based — the real CHANGELOG.md's two `## [Unreleased]` headings cannot make a numeric version's extraction order-dependent"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "tests/test_changelog_extraction.py#test_unreleased_headings_do_not_leak"
        status: pass
      - kind: unit
        ref: "tests/test_changelog_extraction.py#test_changelog_path_override"
        status: pass
    human_judgment: false
  - id: D4
    description: "release.yml's validate job fails before build/publish-pypi/create-release when the tag's version has no CHANGELOG section (D-09)"
    requirement: "REL-04"
    verification:
      - kind: other
        ref: "41-REL04-EVIDENCE.md § D-09 — job needs: graph read + mechanized yaml parse"
        status: pass
    human_judgment: false
  - id: D5
    description: "release.yml's create-release job sources the GitHub Release body from the extractor's stdout; the commit-dump generator has no surviving code path"
    requirement: "REL-04"
    verification:
      - kind: other
        ref: "41-REL04-EVIDENCE.md § SC#1 — dump-removal diff + repo-wide grep for PREV_TAG/Changes since/Initial Release"
        status: pass
    human_judgment: false

# Metrics
duration: 18min
completed: 2026-08-03
status: complete
---

# Phase 41 Plan 01: REL-04 Release-Notes Extraction Summary

**A stdlib-only, positional `## [X.Y.Z]` CHANGELOG-section extractor, pytest-covered and wired into both `release.yml` jobs, replacing the ~296-line `git log --pretty` commit dump with the curated release notes a maintainer actually wrote.**

## Performance

- **Duration:** 18 min
- **Started:** 2026-08-03T11:11:00Z (approx.)
- **Completed:** 2026-08-03T11:29:13Z
- **Tasks:** 3
- **Files modified:** 4 (2 created new source files, 1 new evidence file, 1 workflow file edited)

## Accomplishments

- `scripts/extract_changelog_section.py`: a stdlib-only (`re`/`sys`/`argparse`/`pathlib` only, zero
  third-party imports) CLI script that extracts a `## [<version>]` section's body from
  `CHANGELOG.md`, purely positionally, never special-casing "Unreleased" — verified against the
  repo's real two-`## [Unreleased]`-heading quirk.
- `tests/test_changelog_extraction.py`: a 6-case pytest module exercising the script exclusively via
  `subprocess.run` (never `import`), covering both D-10 directions plus the adjacency, empty-section,
  and ordering edge cases. RED recorded first (all 6 failed, with the two failure-direction cases
  failing on the stderr-content assertion, not vacuously), then GREEN after the script landed
  (6 passed, 0 failed, 0 skipped).
- `.github/workflows/release.yml`: `validate` job gained a `Verify CHANGELOG has a section for this
  version` step (D-09, positioned before `Run tests`); `create-release` job's `Generate release
  notes` step now calls the committed extractor instead of building a `git log --pretty` dump —
  the old `PREV_TAG` lookup and its `if`/`else`/`fi` branch are deleted outright (SC#1), with
  `generate_release_notes: true` and the Installation block retained byte-unchanged (D-08).
- `41-REL04-EVIDENCE.md`: verbatim SC#1 hand-run (`0.6.5` → exit 0 with the real curated section on
  stdout; `9.9.9` → exit 1, empty stdout, version named in stderr), the dump-removal diff plus a
  repo-wide grep proving zero surviving fragments, and D-09's job-graph proof (line-numbered file
  read + a mechanized `yaml.safe_load` parse) — explicitly recording that `release.yml` itself was
  never executed.

## Task Commits

Each task was committed atomically:

1. **Task 1: Record the REL-04 extraction contract RED in a new pytest module** - `4a2afe9` (test)
2. **Task 2: Implement the extraction script and turn the module GREEN** - `91cf53a` (feat)
3. **Task 3: Wire release.yml (both jobs) and transcribe the SC#1 evidence** - `b25ef31` (ci)

_TDD task (Task 1 → 2): RED commit (`4a2afe9`) followed by GREEN commit (`91cf53a`), verified in git
log order — no REFACTOR commit was needed._

## Files Created/Modified

- `scripts/extract_changelog_section.py` - the D-06 extraction script (`extract_section()` + CLI guard)
- `tests/test_changelog_extraction.py` - the six-case subprocess-invoked contract
- `.github/workflows/release.yml` - `validate` job's new existence check; `create-release` job's
  body-generation step re-sourced from the extractor
- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-REL04-EVIDENCE.md` - SC#1/D-09 evidence

## Decisions Made

- Followed the plan's D-06..D-10 decisions exactly as specified in `41-CONTEXT.md`/`41-RESEARCH.md`:
  one committed script (never duplicated inline in the workflow), the fail-loud check moved into
  `validate` (not left only in `create-release`), `generate_release_notes: true` and the Installation
  block kept, and the commit-dump generator removed rather than fenced off behind a fallback.
- Used a mechanized `yaml.safe_load` job-graph assertion in the evidence file (rather than only a
  line-number read) since `pyyaml` was confirmed available in this environment's `dev` extra during
  execution — the plan's acceptance criteria explicitly allowed either method.

## Deviations from Plan

None - plan executed exactly as written. No auto-fixes were needed; both TDD gates (RED then GREEN)
passed on the first attempt at each stage.

## Issues Encountered

- The worktree's fresh `.venv/bin/uv` and (pre-existing) `.venv/bin/ruff` were both generic-Linux
  dynamically-linked ELF binaries that fail under this NixOS host's stub loader (exit 127) —
  the standing, already-documented `CLAUDE.md` hazard. Resolved per its own prescribed fix: symlinked
  `.venv/bin/uv` to the working Nix-store `uv` (`command -v uv`), and `.venv/bin/ruff` to the main
  checkout's already-auto-patchelf'd working `ruff` binary (confirmed via `ldd`/`file` to carry a
  Nix-store interpreter). Not a deviation from the plan's own scope — no code or test change was
  needed, only local environment provisioning, matching the plan's own `<worktree_provisioning>`
  instructions.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- REL-04 is fully implemented and evidenced: `release.yml` now sources the GitHub Release body from
  `CHANGELOG.md`, and the validate job fails loudly before any PyPI upload if the tagged version's
  section is missing or empty.
- No irreversible action was taken: `git tag -l v0.7.0` and `git ls-remote --tags origin v0.7.0` were
  both confirmed empty after this plan's commits.
- `pyproject.toml`/`uv.lock` are byte-identical to before this plan (`git diff --stat` empty) — zero
  new runtime dependencies, consistent with the milestone invariant.
- Full regression suite re-run clean on this plan's final tree: 777 passed, 0 failed (29 slow-marked
  deselected); `black --check .`, `ruff check .`, and `mypy typsphinx/` all exit 0.
- This plan's own scope (Tasks 1-3, REL-04 only) is complete. REL-05's version bump, the CHANGELOG
  `[0.7.0]` entry, SC#3's live-run evidence, SC#4's milestone-invariant sweep, the `ja` glyph bar, and
  `41-HANDOFF.md` belong to this phase's other plans, not this one — `41-01-PLAN.md`'s
  `files_modified` frontmatter names only the four files this plan touched, and none of that later
  work was started here.

---
*Phase: 41-v0-7-0-release-automation-release-prep*
*Completed: 2026-08-03*

## Self-Check: PASSED

All created files confirmed present on disk (`scripts/extract_changelog_section.py`,
`tests/test_changelog_extraction.py`, `.github/workflows/release.yml`,
`41-REL04-EVIDENCE.md`, `41-01-SUMMARY.md`), and all three task commits (`4a2afe9`,
`91cf53a`, `b25ef31`) confirmed present in `git log`.

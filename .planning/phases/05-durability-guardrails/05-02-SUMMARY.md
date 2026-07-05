---
phase: 05-durability-guardrails
plan: 02
subsystem: infra
tags: [dependabot, github-actions, badge, ci, yaml, readme]

requires:
  - phase: 05-durability-guardrails (plan 01)
    provides: "uv sync --locked lockfile-currency gate + softprops/action-gh-release@v3 bump on the same working branch"
provides:
  - "Dependabot `sphinx-typst-stack` group scoping sphinx/docutils/typst runtime bumps into one combined-review PR (DUR-03)"
  - "README CI status badge linking to the ci.yml Actions page (DUR-04)"
affects: [05-03, 05-04]

tech-stack:
  added: []
  patterns:
    - "Dependabot groups: block with patterns + exclude-patterns for precise dependency-cluster scoping"

key-files:
  created: []
  modified:
    - .github/dependabot.yml
    - README.md

key-decisions:
  - "Used prefix-anchored globs sphinx*/docutils*/typst* with exclude-patterns for sphinx-autodoc-typehints and sphinx-intl, avoiding *sphinx*-style substring wildcards per D-08 and RESEARCH Pitfall 4"
  - "Placed the CI badge first in README's badge row (before PyPI) to foreground build-health signal, per D-09 Claude's-discretion placement"

patterns-established:
  - "Dependabot group scoping: prefix-anchored patterns + explicit exclude-patterns to prevent over-matching adjacent packages sharing a name prefix"

requirements-completed: [DUR-03, DUR-04]

coverage:
  - id: D1
    description: "Dependabot pip ecosystem gains a sphinx-typst-stack group scoped to exactly sphinx/docutils/typst, excluding sphinx-autodoc-typehints and sphinx-intl; github-actions ecosystem entry untouched"
    requirement: "DUR-03"
    verification:
      - kind: other
        ref: "python -c yaml.safe_load assertion on .github/dependabot.yml (group patterns/exclude-patterns/github-actions-untouched check) — PASS"
        status: pass
    human_judgment: false
  - id: D2
    description: "README badge row gains exactly one CI status badge (image=ci.yml/badge.svg, link=ci.yml Actions page) as the first badge, five existing badges intact, no blank line introduced"
    requirement: "DUR-04"
    verification:
      - kind: other
        ref: "grep -c/-q assertions on README.md badge row — PASS"
        status: pass
    human_judgment: true
    rationale: "Live SVG badge render on GitHub is a visual confirmation deferred to plan 05-04 (push->observe gate); static markdown correctness is machine-verified here but the rendered badge appearance needs human eyes on the actual GitHub page."

duration: 3min
completed: 2026-07-05
status: complete
---

# Phase 5 Plan 2: Dependabot Grouping and CI Badge Summary

**Added a scoped `sphinx-typst-stack` Dependabot group (sphinx/docutils/typst, excluding sphinx-autodoc-typehints/sphinx-intl) and a leading CI status badge to README.md**

## Performance

- **Duration:** 3 min
- **Started:** 2026-07-05T05:13:00Z
- **Completed:** 2026-07-05T05:15:37Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `.github/dependabot.yml`'s existing `pip` ecosystem entry gained a `groups:` block named `sphinx-typst-stack`, bundling sphinx/docutils/typst runtime bumps into one combined-review PR while excluding the unrelated dev/docs tools `sphinx-autodoc-typehints` and `sphinx-intl`
- `github-actions` ecosystem entry left byte-for-byte unchanged
- README.md's badge row gained a CI-workflow status badge (`ci.yml/badge.svg` → Actions page), placed first to foreground build health

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the sphinx-typst-stack Dependabot group (DUR-03 / D-08)** - `0bf6b5a` (feat)
2. **Task 2: Add the CI status badge to README.md's badge row (DUR-04 / D-09)** - `fd6742d` (docs)

**Plan metadata:** pending (docs: complete plan)

## Files Created/Modified
- `.github/dependabot.yml` - Added `groups.sphinx-typst-stack` (patterns: sphinx*/docutils*/typst*; exclude-patterns: sphinx-autodoc-typehints/sphinx-intl) under the `pip` ecosystem entry
- `README.md` - Inserted `[![CI](.../ci.yml/badge.svg)](.../ci.yml)` badge as the first line of the existing badge row

## Decisions Made
- Used prefix-anchored patterns (`sphinx*`, `docutils*`, `typst*`) plus `exclude-patterns` rather than any substring/double-wildcard form, per D-08's explicit "do not broaden" constraint and RESEARCH.md Pitfall 4
- Placed the CI badge in the leading position of the badge row (Claude's discretion per D-09) to surface build-health status first

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Default NixOS `python3` lacked the `yaml` module for the plan's verification commands; resolved by running the same verification script inside `nix-shell -p python3Packages.pyyaml` instead of the bare interpreter. No code change, verification-tooling only.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- DUR-03 and DUR-04 static verification complete; live badge SVG render and Dependabot group behavior on GitHub are confirmed later in plan 05-04's push→observe gate, per plan scope
- No blockers for 05-03 (drift.yml weekly job)

---
*Phase: 05-durability-guardrails*
*Completed: 2026-07-05*

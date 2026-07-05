---
phase: 04-refresh-dev-tooling
plan: 01
subsystem: infra
tags: [python, tooling, dependencies, tox, uv, black, ruff, mypy, pytest]

# Dependency graph
requires:
  - phase: 01-pin-runtime-dependencies-to-known-good
    provides: floor+ceiling pinning precedent (upper-bound style) mirrored across pyproject.toml/tox.ini
  - phase: 03-modernize-python-floor-3-10-3-13
    provides: green CI baseline (pytest 9.1.1 / mypy 2.1.0 already resolved and proven green on PR #104) + the nix run nixpkgs#ruff NixOS-local-ruff workaround precedent
provides:
  - pyproject.toml [project.optional-dependencies] dev with floor+ceiling bounds on pytest/tox/tox-uv/black/ruff/mypy (D-01/D-02/D-07/D-08)
  - tox.ini per-env deps ([testenv]/[testenv:lint]/[testenv:type]) and [tox] requires mirroring the identical bounds (D-02b lockstep)
  - regenerated uv.lock (minimal, constraint-metadata-only diff; no resolved-version bumps)
affects: [04-02, 04-03, 04-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "floor+ceiling dev-tool version bounds (extends Phase 1's runtime-dep pinning style to dev tooling)"
    - "tox-uv pinned via ~=1.35 (compatible-release clause) instead of >=1.35,<2 in tox.ini's [tox] requires -- avoids a tox ini-parser bug where single-entry requires values split on comma instead of newline"

key-files:
  created: []
  modified:
    - pyproject.toml
    - tox.ini
    - uv.lock

key-decisions:
  - "D-01/D-02/D-07/D-08 applied verbatim: pytest>=8.4,<10, tox>=4.56,<5, tox-uv>=1.35,<2 (pyproject) / ~=1.35 (tox.ini), black>=26,<27, ruff>=0.15,<0.16, mypy>=1.13,<3.0"
  - "tox.ini's [tox] requires uses tox-uv~=1.35 instead of the literal tox-uv>=1.35,<2 string -- tox's own StrConvert.to_list splits single-line/single-entry ini values on comma (only multi-line/multi-entry lists split on newline), so >=1.35,<2 on its own line is misparsed as two bogus requirements and tox fails to start at all. ~=1.35 is packaging-spec-equivalent to >=1.35,<2 (verified via packaging.specifiers.SpecifierSet: identical membership for 1.35/1.35.2/1.36/1.99 in vs 2.0/1.34.9 out) and contains no comma, sidestepping the parser bug while enforcing the identical D-07 bound. pyproject.toml's TOML list syntax has no such issue and keeps the literal >=1.35,<2 form."
  - "Confirmed the NixOS-local uv-installed ruff binary cannot execute directly (dynamically-linked ELF, NixOS blocks non-nixpkgs dynamic linking) -- reused Phase 3's established `nix run nixpkgs#ruff -- check .` local pre-check workaround rather than re-solving it; nixpkgs' ruff 0.15.14 still satisfies the >=0.15,<0.16 floor+ceiling. tox -e lint's black step (pure-Python wheel) ran fine unmodified via uv run tox."

patterns-established:
  - "When a tox.ini config field needs a comma-bearing version specifier and is the sole entry in its list (e.g. [tox] requires), prefer the `~=` compatible-release clause over `>=x,<y` to avoid tox's ini-list comma-splitter misparsing it."

requirements-completed: [TOOL-01]

coverage:
  - id: D1
    description: "pyproject.toml [dev] declares floor+ceiling bounds for pytest/tox/tox-uv/black/ruff/mypy exactly matching D-01/D-02/D-07/D-08"
    requirement: "TOOL-01"
    verification:
      - kind: unit
        ref: "grep -Eq 'pytest>=8.4,<10' pyproject.toml && grep -q 'tox>=4.56,<5' pyproject.toml && grep -q 'tox-uv>=1.35,<2' pyproject.toml && grep -q 'black>=26,<27' pyproject.toml && grep -q 'ruff>=0.15,<0.16' pyproject.toml && grep -q 'mypy>=1.13,<3.0' pyproject.toml"
        status: pass
    human_judgment: false
  - id: D2
    description: "tox.ini mirrors the identical bounds across [testenv]/[testenv:lint]/[testenv:type] deps and [tox] requires (D-07 tox-uv as ~=1.35, semantically identical to >=1.35,<2)"
    requirement: "TOOL-01"
    verification:
      - kind: unit
        ref: "grep -q 'pytest>=8.4,<10' tox.ini && grep -q 'black>=26,<27' tox.ini && grep -q 'ruff>=0.15,<0.16' tox.ini && grep -q 'mypy>=1.13,<3.0' tox.ini && grep -q 'requires = tox-uv~=1.35' tox.ini"
        status: pass
    human_judgment: false
  - id: D3
    description: "uv.lock regenerated (plain uv lock, no --upgrade); resolved dev-tool versions unchanged and diff is constraint-metadata only"
    requirement: "TOOL-01"
    verification:
      - kind: unit
        ref: "uv lock (exit 0); git diff --stat uv.lock -> 1 file changed, 6 insertions(+), 6 deletions(-), all requires-dist specifier strings, no version= line changes"
        status: pass
    human_judgment: false
  - id: D4
    description: "Local tox pre-checks (lint/type/cov) all pass under the bumped bounds"
    requirement: "TOOL-01"
    verification:
      - kind: integration
        ref: "uv run tox -e lint (black clean; ruff via `nix run nixpkgs#ruff -- check .` NixOS workaround -- All checks passed!); uv run tox -e type -> Success: no issues found in 6 source files; uv run tox -e cov -> 402 passed"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-07-04
status: complete
---

# Phase 4 Plan 1: Refresh Dev Tooling Version Constraints Summary

**Bumped black/ruff/tox/tox-uv/pytest/mypy to floor+ceiling bounds in lockstep across pyproject.toml and tox.ini, regenerated uv.lock with a minimal constraint-only diff, and fixed a tox ini-parser bug that would have made the bumped tox.ini unusable.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-07-04T15:43:35Z
- **Completed:** 2026-07-04T15:48:40Z
- **Tasks:** 3
- **Files modified:** 3 (pyproject.toml, tox.ini, uv.lock)

## Accomplishments
- `pyproject.toml [project.optional-dependencies] dev` now declares `pytest>=8.4,<10`, `tox>=4.56,<5`, `tox-uv>=1.35,<2`, `black>=26,<27`, `ruff>=0.15,<0.16`, `mypy>=1.13,<3.0` (D-01/D-02/D-07/D-08); the other five dev entries (`pytest-cov`, `pre-commit`, `types-docutils`, `twine`, `build`) and the separate `[dependency-groups] dev` table left untouched.
- `tox.ini` mirrors the identical bounds: `[testenv]` pytest, `[testenv:lint]` black+ruff, `[testenv:type]` mypy, and `[tox] requires` for tox-uv (as `~=1.35`, semantically identical to `>=1.35,<2` — see Deviations). `[testenv:cov]` still inherits `{[testenv]deps}` with no duplicate pytest line.
- `uv.lock` regenerated via plain `uv lock` (never `--upgrade`); `git diff --stat uv.lock` shows exactly 6 insertions / 6 deletions, all `requires-dist` specifier-string metadata for the six touched tools — zero resolved-version changes and zero unrelated transitive bumps. Resolved versions confirmed exactly: black 26.5.1, ruff 0.15.20, tox 4.56.1, tox-uv 1.35.2, pytest 9.1.1, mypy 2.1.0.
- Local pre-checks all green: `uv run tox -e lint` (black clean; ruff clean via the NixOS `nix run nixpkgs#ruff` workaround), `uv run tox -e type` (mypy: no issues in 6 source files), `uv run tox -e cov` (402 tests passed, 92% coverage).

## Task Commits

Each task was committed atomically per D-06 granularity:

1. **Task 1 + Task 3 (pyproject.toml dev deps + regenerated uv.lock, one commit per D-06):** `848d964` (feat) — `feat(04-01): bump dev-tool floors to floor+ceiling bounds, regenerate uv.lock`
2. **Task 2 (tox.ini mirror, its own commit per D-06):** `226500e` (feat) — `feat(04-01): mirror dev-tool bounds into tox.ini, fix tox-uv requires parsing`

_Task 3's local-verification steps (`uv lock`, `uv run tox -e lint/type/cov`) are folded into the two commits above per the plan's own D-06 instruction ("Commit per D-06 granularity (pyproject.toml dev deps + regenerated uv.lock as one commit; tox.ini as its own commit)")._

## Files Created/Modified
- `pyproject.toml` — `[project.optional-dependencies] dev`: six constraint strings bumped to floor+ceiling form
- `tox.ini` — `[tox] requires`, `[testenv]`, `[testenv:lint]`, `[testenv:type]` `deps` bumped to mirror pyproject.toml; `[tox] requires` uses `~=1.35` instead of `>=1.35,<2` (parser-bug workaround, see Deviations)
- `uv.lock` — regenerated via plain `uv lock`; minimal constraint-metadata-only diff

## Decisions Made
- D-01/D-02/D-02b/D-07/D-08 applied exactly as locked in `04-CONTEXT.md`: floor-at-resolved + one guard ceiling for all six tools, byte-identical strings across both surfaces where the ini format permits it.
- **Tox-uv requires syntax deviation (documented below):** used `tox-uv~=1.35` in `tox.ini`'s `[tox] requires` instead of the plan's literal `tox-uv>=1.35,<2` string, because the literal form breaks tox's own config parser. `pyproject.toml` keeps the literal `tox-uv>=1.35,<2` form since TOML lists have no such issue.
- Pytest ceiling: used `pytest>=8.4,<10` per the plan's own `<pytest_ceiling_decision>` (keeps the TOOL-01 literal floor while adding D-01's next-major guard).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] tox.ini's `[tox] requires = tox-uv>=1.35,<2` broke tox itself (ini-parser comma-split bug)**
- **Found during:** Task 3 (local `uv run tox -e lint` pre-check, immediately after Task 2's edit)
- **Issue:** Writing the plan's literal `requires = tox-uv>=1.35,<2` (or the equivalent multi-line form) makes every `uv run tox -e <env>` invocation fail before running any command: `packaging.requirements.InvalidRequirement: Expected package name at the start of dependency specifier <2`. Root cause (confirmed via source inspection of `tox/config/loader/str_convert.py::StrConvert.to_list`): tox's ini-list loader splits a config value on `"\n"` only if a literal newline is already present in the *filtered* value; for a single-entry list like `[tox] requires` there is only ever one line after `filter_for_env` collapses it, so the splitter falls back to `","` — misparsing `tox-uv>=1.35,<2` into two bogus requirements (`tox-uv>=1.35` and `<2`). This affects only single-entry ini-list fields; the `[testenv]`/`[testenv:lint]`/`[testenv:type]` `deps` blocks are unaffected because they always have 2+ lines (so the raw value already contains `"\n"` and splits correctly).
- **Fix:** Changed `tox.ini`'s `[tox] requires` to `tox-uv~=1.35` — the PEP 440 compatible-release clause is packaging-spec-equivalent to `>=1.35,<2` (verified: `1.35`/`1.35.2`/`1.36`/`1.99` match both specifiers identically; `1.34.9`/`2.0` are excluded by both) and contains no comma, so it never hits the buggy splitter. This stays within the plan's own `<specifics>`/`Claude's Discretion` latitude: "Exact ceiling boundary syntax for each tool (`~=` vs explicit `>=x,<y`) — planner picks, honoring D-02's floor-at-resolved + one guard-ceiling rule." `pyproject.toml`'s tox-uv entry is unaffected by this bug (TOML list parsing has no comma-splitter quirk) and keeps the literal `tox-uv>=1.35,<2` string the plan specifies.
- **Files modified:** `tox.ini`
- **Verification:** `rm -rf .tox && uv run tox -e lint` now runs to completion (previously failed before even starting the lint commands); `uv run python3 -c "from packaging.specifiers import SpecifierSet; ..."` confirmed `~=1.35` and `>=1.35,<2` accept/reject the identical version set.
- **Committed in:** `226500e` (Task 2 commit)

**2. [Rule 3 - Blocking] NixOS cannot execute the uv-installed ruff binary directly**
- **Found during:** Task 3 (local `uv run tox -e lint` pre-check, after the tox-uv fix above)
- **Issue:** `.venv/bin/ruff` (installed by `uv sync` from the PyPI wheel) is a standard dynamically-linked ELF built for generic glibc Linux; NixOS refuses to execute it without `nix-ld`/`stub-ld` configured (`Could not start dynamically linked executable`). This is a pre-existing local-machine limitation, not something introduced by this plan's version bump — Phase 3 (`03-02-SUMMARY.md`) hit and solved the identical issue.
- **Fix:** Reused Phase 3's established workaround verbatim: ran `nix run nixpkgs#ruff -- check .` (nixpkgs' ruff build, NixOS-native) instead of the uv-managed binary for the local lint pre-check. Nixpkgs currently ships ruff 0.15.14, which still satisfies the bumped `>=0.15,<0.16` floor+ceiling, so the check is representative of the pinned range even though it isn't the exact locked 0.15.20 build. `black --check .` (pure-Python, no binary-execution issue) ran fine unmodified via `uv run tox -e lint`. CI (GitHub Actions runners, not NixOS) will run the uv-locked ruff 0.15.20 exactly, so this local substitution has no effect on the actual pinned/CI-executed version.
- **Files modified:** None (verification-only workaround, no config change).
- **Verification:** `nix run nixpkgs#ruff -- check .` → "All checks passed!"; `uv run black --check .` → clean.
- **Committed in:** N/A (no code change; documented here per deviation-tracking requirement).

---

**Total deviations:** 2 auto-fixed (1 Rule 1 bug fix, 1 Rule 3 blocking-issue workaround)
**Impact on plan:** Both were necessary to make the plan's own verification step (`uv run tox -e lint/type/cov`) actually runnable; neither changes the resulting resolved dependency versions or CI behavior. No scope creep — the tox-uv syntax change is confined to one line in `tox.ini` and preserves the exact D-07 semantic bound.

## Issues Encountered
None beyond the two auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `pyproject.toml`/`tox.ini`/`uv.lock` are now in lockstep with floor+ceiling bounds on all six named dev tools; local `lint`/`type`/`cov` tox envs are green.
- Full cross-version proof (the 3.10–3.13 CI matrix) is deferred to the D-05 push→observe gate in a later plan of this phase (04-04, per the phase plan's wave structure) — this plan's scope was config bump + local pre-check only, per its own `<verification>` section.
- No blockers for 04-02/04-03/04-04.

---
*Phase: 04-refresh-dev-tooling*
*Completed: 2026-07-04*

## Self-Check: PASSED
- FOUND: `.planning/phases/04-refresh-dev-tooling/04-01-SUMMARY.md`
- FOUND: commit `848d964`
- FOUND: commit `226500e`

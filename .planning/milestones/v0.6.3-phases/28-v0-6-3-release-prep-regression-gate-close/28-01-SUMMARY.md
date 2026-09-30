---
phase: 28-v0-6-3-release-prep-regression-gate-close
plan: 01
subsystem: release-prep
tags: [uv, pyproject, semver, version-bump, lockfile]

# Dependency graph
requires:
  - phase: 23-changelog-and-version-sync-guards
    provides: "tests/test_readme_version_sync.py and tests/test_preview_version_sync.py guard suites (D-13/D-14)"
provides:
  - "pyproject.toml [project].version bumped 0.6.2 -> 0.6.3, the sole version literal in the file"
  - "uv.lock regenerated via `uv lock`; typsphinx self-entry now version = \"0.6.3\"; no direct-dependency range drift"
  - "README.md Status line bumped to Stable (v0.6.3); dependency-floor footer line untouched"
  - "Editable install metadata refreshed (uv sync --extra dev --locked --reinstall via normal resolve); typsphinx.__version__ reports 0.6.3"
affects: [28-02-regression-gate-close, 28-03-changelog-and-version-bump-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Version bump is a single atomic task across 3 declaration surfaces (pyproject.toml, uv.lock, README.md) plus the installed editable-dist metadata, because tests/test_readme_version_sync.py and tests/test_extension.py::test_version_matches_pyproject_toml assert cross-file agreement and would go RED if split across commits"

key-files:
  created: []
  modified:
    - pyproject.toml
    - uv.lock
    - README.md

key-decisions:
  - "Used `uv lock` (not bare `uv sync`) to regenerate uv.lock as a single-purpose, minimal-diff operation, then `uv sync --extra dev --locked` to both validate zero drift and refresh the editable install in one step"
  - "Task 2 performed no additional file edits — it is pure verification/classification of the uv.lock diff already produced by Task 1, so no separate commit was created for Task 2; its findings are recorded below"

requirements-completed: []

coverage:
  - id: D1
    description: "pyproject.toml [project].version reads 0.6.3 and remains the sole version literal in the file"
    verification:
      - kind: unit
        ref: "grep -c '^version = ' pyproject.toml == 1; grep -c '^version = \"0.6.3\"$' pyproject.toml == 1"
        status: pass
    human_judgment: false
  - id: D2
    description: "uv.lock typsphinx self-entry reads version = \"0.6.3\" and `uv sync --extra dev --locked` exits 0"
    verification:
      - kind: unit
        ref: "grep -A1 'name = \"typsphinx\"' uv.lock shows version = \"0.6.3\"; uv sync --extra dev --locked exit 0 (twice, idempotent)"
        status: pass
    human_judgment: false
  - id: D3
    description: "README.md Status line reads Stable (v0.6.3), and it is the only changed line in README.md"
    verification:
      - kind: unit
        ref: "git diff --numstat -- README.md == '1\t1\tREADME.md'"
        status: pass
    human_judgment: false
  - id: D4
    description: "Installed editable dist metadata refreshed so typsphinx.__version__ reports 0.6.3"
    verification:
      - kind: unit
        ref: "uv run python -c \"import typsphinx;print(typsphinx.__version__)\" -> 0.6.3; tests/test_extension.py::test_version_matches_pyproject_toml"
        status: pass
    human_judgment: false
  - id: D5
    description: "Version-sync guard suite stays green across the atomic bump (readme sync, preview sync, extension version match)"
    verification:
      - kind: unit
        ref: "tests/test_readme_version_sync.py tests/test_preview_version_sync.py tests/test_extension.py::test_version_matches_pyproject_toml -v (4 tests passed)"
        status: pass
    human_judgment: false
  - id: D6
    description: "uv.lock diff contains no change to any direct dependency specifier (sphinx/docutils/typst); classified verbatim in SUMMARY"
    verification:
      - kind: unit
        ref: "git diff -- uv.lock | grep -E '^[+-]' | grep -Ec 'name = \"(sphinx|docutils|typst)\", specifier' == 0"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-25
status: complete
---

# Phase 28 Plan 01: Version Bump 0.6.2 -> 0.6.3 Summary

**Atomic version bump across pyproject.toml, uv.lock, and README.md's Status line, with the editable-dist install metadata refreshed so `typsphinx.__version__` reports 0.6.3 and all three version-sync guard tests stay green.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-25T08:06:00Z (approx)
- **Completed:** 2026-07-25T08:18:29Z
- **Tasks:** 2
- **Files modified:** 3 (pyproject.toml, uv.lock, README.md)

## Accomplishments
- `pyproject.toml [project].version` bumped from `0.6.2` to `0.6.3` — remains the sole `^version = ` literal in the file
- `uv.lock` regenerated via `uv lock` (not hand-edited); `typsphinx` self-entry now `version = "0.6.3"`; diff is a single 1-line change with no `revision` counter churn and no transitive dependency movement
- `README.md:315` Status line bumped to `**Status**: Stable (v0.6.3) - Production ready`; the adjacent dependency-floor footer line (`:316`) is byte-identical to before
- Editable install metadata refreshed as a side effect of `uv sync --extra dev --locked` (uninstalled `typsphinx==0.6.2`, installed `typsphinx==0.6.3`); `typsphinx.__version__` now reports `0.6.3`
- All three version-sync guard tests pass: `tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py` (2 tests), `tests/test_extension.py::test_version_matches_pyproject_toml`
- Task 2's diff classification (below) proves the `uv.lock` change is limited to the self-entry version bump — no direct-dependency range drift, satisfying SC#4's precondition

## Task Commits

1. **Task 1: 版リテラルを pyproject.toml / README.md / uv.lock で同時にバンプし、editable メタデータを作り直す** - `de0a3d5` (chore)
2. **Task 2: uv.lock の diff 形状を分類し、直接依存レンジの変化がないことを証明する** - no additional commit (pure verification/classification task; produced no file changes beyond what Task 1 already committed — see `## uv.lock diff` below)

**Plan metadata:** (recorded by orchestrator after wave completion; worktree agents do not create the final metadata commit)

## Files Created/Modified
- `pyproject.toml` - `[project].version`: `0.6.2` -> `0.6.3` (line 7, sole version literal)
- `uv.lock` - regenerated via `uv lock`; `typsphinx` self-entry `version`: `0.6.2` -> `0.6.3` (line ~1379)
- `README.md` - Status line (line 315): `Stable (v0.6.2)` -> `Stable (v0.6.3)`

## uv.lock diff

Verbatim `git diff --stat -- uv.lock` output (captured against the parent commit `1e16c23`, i.e. `git diff HEAD~1 HEAD -- uv.lock` after the Task 1 commit):

```
 uv.lock | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

Full diff body (for completeness — a single hunk):

```diff
@@ -1376,7 +1376,7 @@ wheels = [

 [[package]]
 name = "typsphinx"
-version = "0.6.2"
+version = "0.6.3"
 source = { editable = "." }
 dependencies = [
     { name = "docutils" },
```

**Classification of the diff (all lines accounted for, per Task 2 §action's 3-way split):**

- **Self-entry version update:** 1 changed line pair (`-version = "0.6.2"` / `+version = "0.6.3"`). Expected. No further explanation needed.
- **`revision` counter (lockfile metadata):** none — the diff contains no change to any `revision = N` line. This matches the plan's expectation of "clean state, single version bump" since `git diff main..HEAD -- uv.lock` was fully empty before this plan started.
- **Transitive (indirect) dependency resolution changes:** **none.** No package other than `typsphinx` itself appears anywhere in the diff.
- **Direct dependency range specifier changes (`requires-dist` for sphinx/docutils/typst):** **none** — confirmed by `git diff -- uv.lock | grep -E '^[+-]' | grep -Ec 'name = "(sphinx|docutils|typst)", specifier'` returning `0`. This is the SC#4 stop-condition check and it is clean; no need to halt or escalate.

Conclusion: the `uv.lock` diff is the minimal, expected single-line self-entry bump. No incidental drift of any kind rode along.

## Decisions Made
- Used `uv lock` (single-purpose, only touches `uv.lock`) followed by `uv sync --extra dev --locked` (validates zero drift AND refreshes the editable install) rather than a bare `uv sync`, per the plan's explicit guidance to keep "did the lock regenerate" and "did the venv get the new metadata" separately verifiable.
- Task 2 required no code/file changes of its own — its job (classify the uv.lock diff, prove no direct-dependency drift) is satisfied by grep-based verification against the diff Task 1 already produced. No separate git commit was created for Task 2; its output is fully captured in this SUMMARY's `## uv.lock diff` section, satisfying the plan's acceptance criterion that the classification live in the SUMMARY.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' acceptance criteria and verification blocks passed on the first attempt with no auto-fixes required.

## Issues Encountered

The worktree venv's `uv sync` step installed a generic-linux ELF `uv` binary into `.venv/bin/uv` which cannot exec under this NixOS sandbox (`Could not start dynamically linked executable`). This is a known, previously-documented worktree provisioning hazard (see CLAUDE.md § Worktree-isolated execution and prior phase memory `nixos-sandbox-test-env`), not a deviation from this plan's scope — resolved by replacing the installed binary with a symlink to the nix-store `uv` (`ln -s $(command -v uv) .venv/bin/uv`) before running any `uv run` command, per the mandatory pre-execution setup instructions provided to this executor. No plan files were touched to fix this; it is pure environment provisioning.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Half of ROADMAP SC#1 (the version-declaration half) is complete: `pyproject.toml`, `uv.lock`, and `README.md` all agree on `0.6.3`, and the installed dist metadata matches.
- SC#4's precondition holds: no direct-dependency range drift in `uv.lock`, and `tests/test_preview_version_sync.py` stays green.
- SC#5 is untouched: no git tag, no publish command, no `.github/workflows/release.yml` modification (`git status --porcelain .github/workflows/release.yml` was empty throughout).
- Ready for 28-02 (regression-gate close) to run against a working tree that already carries the 0.6.3 version bump, and for 28-03 to add the CHANGELOG `## [0.6.3]` entry pointing at this same version.
- No blockers.

## Self-Check: PASSED

Verified all claimed artifacts and commits exist on disk/in git history (see below).

---
*Phase: 28-v0-6-3-release-prep-regression-gate-close*
*Completed: 2026-07-25*

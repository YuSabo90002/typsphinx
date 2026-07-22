---
phase: 23-v0-6-2-release-prep-regression-gate-close
plan: 01
subsystem: infra
tags: [release-prep, versioning, uv, pytest, tomllib]

# Dependency graph
requires:
  - phase: 22.4-readme-status-configuration-options-known-limitations-docs
    provides: README.md D-11 hand-off note (Status line must move with the next version bump)
provides:
  - pyproject.toml [project].version bumped to 0.6.2
  - uv.lock regenerated in lockstep (typsphinx self-entry only; no dependency drift)
  - README.md:316 Status line bumped to Stable (v0.6.2)
  - tests/test_readme_version_sync.py — permanent README <-> pyproject.toml drift guard (D-13)
affects: [23-02-corpus-gate-evidence, 23-03-changelog, gsd-complete-milestone]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Version-sync drift guard: parse both sides independently (tomllib for TOML, targeted regex for README prose), compare parsed values against each other (never a hardcoded literal), guard the regex extraction with an assert-with-message so an unmatched line fails loudly instead of vacuously passing."

key-files:
  created: [tests/test_readme_version_sync.py]
  modified: [pyproject.toml, uv.lock, README.md]

key-decisions:
  - "Followed CONTEXT.md D-13/D-14 exactly: new sync test asserts only the README Status line's version against pyproject.toml's version; the Requirements section (README.md:37-39) and the Python/Sphinx/Typst footer (README.md:317) are explicitly out of scope and were left untouched."
  - "Regenerated uv.lock via `uv lock` (not a bare `uv sync`) per Claude's Discretion in CONTEXT.md, then verified separately with `uv sync --extra dev --locked` — keeps 'did the lock regenerate' distinct from 'did the venv install'."
  - "RED-proved the new test before accepting it: temporarily rewrote README's Status version to v0.4.9, confirmed the test failed, then restored README.md programmatically and confirmed byte-identical restoration via `git diff` (no diff)."

requirements-completed: []  # Phase 23 plan 23-01 has requirements: [] per its own frontmatter (release/close phase)

coverage:
  - id: D1
    description: "pyproject.toml, uv.lock, and README.md all bumped to 0.6.2 in lockstep; uv sync --extra dev --locked exits 0"
    verification:
      - kind: unit
        ref: "uv sync --extra dev --locked (CLI invocation)"
        status: pass
      - kind: unit
        ref: "tomllib.load(pyproject.toml)['project']['version'] == '0.6.2' (inline check)"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_readme_version_sync.py added — a permanent README<->pyproject version-sync drift guard (D-13), proven non-tautological via a RED perturbation of README's Status line"
    verification:
      - kind: unit
        ref: "tests/test_readme_version_sync.py#test_readme_status_version_matches_pyproject"
        status: pass
      - kind: unit
        ref: "tests/test_preview_version_sync.py (cross-check, unaffected by this plan)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Scope fence held: no tag, no publish, no typsphinx/ source change, no tox.ini change"
    verification:
      - kind: other
        ref: "git tag --list 'v0.6.2' (empty); git diff --name-only for this plan's two commits (no typsphinx/ path, no tox.ini)"
        status: pass
    human_judgment: false

# Metrics
duration: ~15min
completed: 2026-07-23
status: complete
---

# Phase 23 Plan 01: Version Bump + README Sync Test Summary

**Bumped typsphinx to 0.6.2 across `pyproject.toml`/`uv.lock`/`README.md` and added `tests/test_readme_version_sync.py`, a tomllib+regex drift guard that permanently binds the README Status line to `pyproject.toml`'s version (D-13).**

## Performance

- **Duration:** ~15 min
- **Tasks:** 2 completed
- **Files modified:** 4 (`pyproject.toml`, `uv.lock`, `README.md`, `tests/test_readme_version_sync.py` — new)

## Accomplishments

- `pyproject.toml [project].version` bumped `0.6.1` → `0.6.2` (sole version literal in the file, verified no other line changed)
- `uv.lock` regenerated via `uv lock`; diff is a single line (the `typsphinx` self-entry's `version` field) — no revision-counter bump, no transitive dependency drift observed
- `README.md:316` Status line bumped to `Stable (v0.6.2) - Production ready`; the adjacent dependency-floor footer (`:317`) and the Requirements section (`:37-39`) are byte-identical, per D-14's explicit scope fence
- New `tests/test_readme_version_sync.py` — parses README's Status line via a targeted regex and `pyproject.toml`'s version via `tomllib`, compares the two values against each other (never a hardcoded literal), and was RED-proven during this execution by perturbing README's Status version and confirming the test fails before restoring the file

## Task Commits

Each task was committed atomically:

1. **Task 1: Bump the version literal in pyproject.toml, README.md, and uv.lock** - `101ca6f` (chore)
2. **Task 2: Add tests/test_readme_version_sync.py — the README ↔ pyproject drift guard (D-13)** - `ea4d3d4` (test)

_Note: this SUMMARY commit itself is the plan-metadata commit (worktree mode — STATE.md/ROADMAP.md are excluded and owned by the orchestrator)._

## Files Created/Modified

- `pyproject.toml` - `[project].version` literal: `0.6.1` → `0.6.2`; no other line touched
- `uv.lock` - regenerated via `uv lock`; only the `typsphinx` self-entry's `version` field changed
- `README.md` - Status line at `:316` bumped to `Stable (v0.6.2) - Production ready`; footer at `:317` and Requirements section at `:37-39` left byte-identical
- `tests/test_readme_version_sync.py` - new module: `REPO_ROOT`/`README_PATH`/`PYPROJECT_PATH` constants, `_STATUS_LINE_RE`, `_extract_readme_status_version()`, `_extract_pyproject_version()`, `test_readme_status_version_matches_pyproject()`

## Decisions Made

- Regenerated the lockfile with `uv lock` (not a bare `uv sync`), then verified separately with `uv sync --extra dev --locked` — matches the plan's stated rationale of keeping "did the lock regenerate" distinct from "did the venv install."
- New sync test module named `tests/test_readme_version_sync.py` (not appended to `tests/test_preview_version_sync.py`), matching this project's one-module-per-drift-hazard convention.
- Ruff was run via the documented `nix-shell -p ruff --run "ruff check ..."` fallback after `uv run python -m ruff check` hit the known NixOS dynamically-linked-executable hazard (`.venv/bin/ruff` cannot exec on NixOS without patchelf/nix-ld) — both black and ruff report the new file clean.

## Deviations from Plan

None — plan executed exactly as written. One expected, plan-anticipated environment quirk occurred and was handled per its documented fallback (see below), not a deviation from the plan's intent.

### Notes (not deviations, both explicitly anticipated by the plan text)

- **`uv run python -m black --check` reported the freshly-authored test file as needing reformatting** on the first pass (the skeleton's `_STATUS_LINE_RE` assignment exceeded black's line-wrapping preference for a single-line regex). Ran `uv run python -m black tests/test_readme_version_sync.py` to apply the reformat, then re-verified `--check` exits 0. No behavior change — purely a wrapping/formatting diff.
- **`uv run python -m ruff check` failed to start** (`Could not start dynamically linked executable ... NixOS cannot run dynamically linked executables intended for generic linux environments`). This is the project's documented NixOS ELF-exec hazard; the plan's own action text names the `nix-shell -p ruff --run "ruff check ..."` fallback for exactly this case. Used it; `ruff` reported "All checks passed!".

## Observed `uv.lock` diff (as required by plan output spec)

```
$ git diff --stat -- uv.lock  (pre-commit, HEAD vs. working tree)
 uv.lock | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

$ git diff -- uv.lock
--- a/uv.lock
+++ b/uv.lock
@@ -1376,7 +1376,7 @@ wheels = [

 [[package]]
 name = "typsphinx"
-version = "0.6.1"
+version = "0.6.2"
 source = { editable = "." }
 dependencies = [
     { name = "docutils" },
```

**No transitive resolution change observed.** The diff is exactly the `typsphinx` self-entry's own version literal — no cosmetic `revision` counter bump, no other package's resolved version changed. This is the cleanest possible shape per the plan's own expected-diff description; nothing needed to be flagged as incidental upstream drift.

## Issues Encountered

None beyond the two documented, plan-anticipated environment notes above (black reformat, ruff NixOS fallback) — both resolved within the task's normal flow.

## Verification Evidence

- `uv sync --extra dev --locked` → exit 0 (typsphinx 0.6.1 → 0.6.2 reinstalled, no drift reported)
- `uv run python -c "import tomllib;print(...)"` → prints exactly `0.6.2`
- `grep -c '^version = "0.6.1"' pyproject.toml` → `0`
- `git diff -- README.md` → exactly one changed line (the Status line)
- `git diff -- pyproject.toml` → exactly one changed line (the version literal); `dependencies = [...]` array and `requires-python` untouched
- `git status --porcelain tox.ini` → empty
- `uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` → `3 passed`
- RED proof: README Status version perturbed to `v0.4.9` → `1 failed` with an actionable message naming both observed values and the remediation; README restored byte-for-byte afterward (`git diff -- README.md` empty post-restore)
- `grep -c '"0\.6\.2"' tests/test_readme_version_sync.py` → `0` (no hardcoded expected version)
- `uv run python -m black --check tests/test_readme_version_sync.py` → clean (after one reformat pass)
- `nix-shell -p ruff --run "ruff check tests/test_readme_version_sync.py"` → "All checks passed!"
- Broader regression check: `uv run python -m pytest -q -m "not slow" --ignore=tests/test_integration_advanced.py --ignore=tests/test_integration_basic.py --ignore=tests/test_integration_multi_doc.py --ignore=tests/test_integration_nested_toctree.py --ignore=tests/test_examples_basic.py` → `505 passed, 23 deselected` (no new failures; the five excluded files are the documented environmentally-failing set, per project memory, and were not run)
- `git tag --list 'v0.6.2'` → empty (both before and after all tasks)
- `git diff --name-only 101ca6f^ ea4d3d4` (this plan's two commits combined) → `README.md`, `pyproject.toml`, `tests/test_readme_version_sync.py`, `uv.lock` only — no path under `typsphinx/`

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC#1's version-bump half is satisfied: `pyproject.toml` at 0.6.2, `uv.lock` regenerated in lockstep, `uv sync --locked` green.
- D-13 satisfied: `README.md:316` reads `Stable (v0.6.2)` and a new test permanently binds it to `pyproject.toml`.
- D-14 respected: the sync test's scope is the Status line only; no change to the Requirements section or the Python/Sphinx/Typst footer.
- SC#5 scope fence held throughout: no tag created, no publish command run, no `.github/workflows/release.yml` interaction, no `typsphinx/` source file touched, `tox.ini`'s deliberate `tox-uv~=1.35` pin untouched.
- Ready for 23-02 (corpus-gate regression evidence) and 23-03 (`[0.6.2]` CHANGELOG entry) — both can now cite `pyproject.toml`'s 0.6.2 literal as the confirmed version for their own work.

---
*Phase: 23-v0-6-2-release-prep-regression-gate-close*
*Completed: 2026-07-23*

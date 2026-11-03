# Synthesis

<!-- Quick lane: research and decide skipped (INTENT.md Lane: quick). Settled-only synthesis written by plan. -->

## Settled

- Scope — test-only fixes to the eight Windows-failing tests plus the README Project Structure tree; no product code changes (INTENT.md Scope: in / Scope: out, owner ruling "1: a").
- Windows proof — Linux-observable simulations: `FORCE_COLOR=1` with `NO_COLOR` unset for the drift gate, POSIX-normalised paths, both separator forms fed to the missing-file check; Windows CI dispatched during build as a Constraint (INTENT.md Constraints, owner ruling "2: a").
- Colour handling — strip every ANSI SGR sequence from captured warning lines before comparison (INTENT.md Edge coverage E1); a project-wide helper is vetoed.
- Missing-file match — normalise `\` to `/` in the error text before matching `_typsphinx/deps.typ` (INTENT.md Edge coverage E3).
- Root causes — `str(relative_to)` native separators; typst native Windows error path; Sphinx 9.1.1 `terminal_supports_colour()` True on win32 unless `NO_COLOR` (`.project/research/evidence-codebase.md` findings).
- README — add `typst_deps.py` under `typsphinx/` in the Project Structure tree (DOCS-AUDIT queue #1, ruling fix-doc).
- `FORCE_COLOR=1` makes Linux sphinx-build emit ANSI codes (measured in define: 13 coloured stderr lines), so the SC1 simulation is meaningful (INTENT.md Risks).

## For the planner

- **Wave-1 blockers**: none beyond proving the `FORCE_COLOR=1` run fails before the fix and passes after.
- **Walking skeleton**: one task fixing the three test files and README, verified with and without `FORCE_COLOR`.
- **Pitfalls → tasks**: N1 — keep every drift assertion's exact text/count/order (T001); `tests/test_repr_census_guard.py` pins line numbers in other test files only — not touched here; run warning-text tests under `LC_ALL=C` (T001).

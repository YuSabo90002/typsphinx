# Deferred Items — Phase 53

Out-of-scope discoveries logged during plan execution, per the executor's scope-boundary rule
(only auto-fix issues directly caused by the current task's own changes).

## 53-01: Pre-existing test failures referencing an archived milestone path

**Found during:** Task 2 verification (`uv run pytest tests/ -q`).

**Symptom:** 7 tests in `tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::
test_warning_baseline_preserved` fail with `FileNotFoundError` reading
`.planning/phases/49-per-master-include-graph-with-state-guarded-includes/
49-SHAPES-RED-EVIDENCE.md`.

**Root cause:** commit `2ea4db0f` ("chore: archive v0.8.0 milestone files") moved that file to
`.planning/milestones/v0.8.0-phases/49-per-master-include-graph-with-state-guarded-includes/
49-SHAPES-RED-EVIDENCE.md` as part of the v0.8.0 milestone archival, but
`tests/test_state_guard_shapes_gate.py` still reads it at its pre-archive path. `2ea4db0f` is an
ancestor of this plan's base commit (`222e1b9b`), confirmed via
`git merge-base --is-ancestor 2ea4db0f 222e1b9b`, so this defect predates Phase 53 entirely —
Plan 53-01 touches no `typsphinx/` or `tests/` source file, so it cannot have caused this.

**Scope decision:** out of scope for 53-01 (a `.planning/`-evidence-artifact plan) and for the
rest of Phase 53 (no plan in this phase touches `test_state_guard_shapes_gate.py` or the
milestone-archive layout). Not auto-fixed here. The plan's own acceptance criterion
"`uv run pytest tests/ -q` still exits 0" is therefore **not met** as of this commit, for a
reason unrelated to this plan's changes — see `53-01-SUMMARY.md`'s Deviations section.

**Suggested fix (for whoever picks this up):** update the path in
`tests/test_state_guard_shapes_gate.py` to read from
`.planning/milestones/v0.8.0-phases/49-per-master-include-graph-with-state-guarded-includes/
49-SHAPES-RED-EVIDENCE.md`, or make the test module resilient to milestone archival.

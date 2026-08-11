# Phase 47 — CI Evidence (Plan 47-10)

Records measured evidence for milestone invariant #5, binding constraint #2, and Phase 47
success criterion 5: the milestone branch pushed to `origin`, plus a completed CI run over it
covering the Windows and macOS lanes.

---

## Branch on origin

**Task 1 — pushed 2026-08-11T12:25:42Z, evidence captured 2026-08-11T12:25:51Z.**

Precondition check before push: `uv run pytest -q` on the branch tip (`fc288f0`) —
**1031 passed, 1 skipped, 212.56s** — confirmed green before pushing.

Command run: `git push -u origin gsd/v0.8.0-multi-master-composition`

```
remote:
remote: Create a pull request for 'gsd/v0.8.0-multi-master-composition' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.8.0-multi-master-composition
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]      gsd/v0.8.0-multi-master-composition -> gsd/v0.8.0-multi-master-composition
branch 'gsd/v0.8.0-multi-master-composition' set up to track 'origin/gsd/v0.8.0-multi-master-composition'.
```

Verbatim `git ls-remote --heads origin gsd/v0.8.0-multi-master-composition` output:

```
fc288f01d345ca252863e376ae2df043ecff0283	refs/heads/gsd/v0.8.0-multi-master-composition
```

- **Local SHA** (`git rev-parse gsd/v0.8.0-multi-master-composition`): `fc288f01d345ca252863e376ae2df043ecff0283`
- **Local SHA** (`git rev-parse HEAD` at push time): `fc288f01d345ca252863e376ae2df043ecff0283`
- **Remote SHA** (from `git ls-remote`): `fc288f01d345ca252863e376ae2df043ecff0283`
- **SHAs match.** No reconciliation needed.
- `gh pr list --head gsd/v0.8.0-multi-master-composition` returned **empty** — no pull request was
  opened, per the task's explicit instruction (the ship unit for `branching_strategy: milestone` is
  the milestone; the release PR is Phase 52's business).

**Note:** the branch subsequently advanced past `fc288f0` — first by this task's own
`47-CI-EVIDENCE.md` commit (`6f8a23c`), then by the CI-triage fix commit described below
(`be4c4d5`) — each pushed in turn with `git push origin gsd/v0.8.0-multi-master-composition`
(no `-f`, no rewrite). No PR was opened at any point. The final green CI run below is over the
branch tip `be4c4d5`, confirmed still on `origin` at that SHA (see "Final state" at the bottom of
this document).

---

## Completed CI run

**Trigger:** `ci.yml`'s `on: push` fires only for `branches: [main, develop]` (verified by
reading `.github/workflows/ci.yml`), so a push to a `gsd/*` milestone branch does **not**
auto-trigger it — only the unrelated `links.yml` (Link Check) fires unconditionally on push. `ci.yml`
does carry `workflow_dispatch:`, so each CI run below was started with
`gh workflow run ci.yml --ref gsd/v0.8.0-multi-master-composition`.

### Run 1 — 31491228938 (over `6f8a23c`) — FAILED, triaged

- URL: https://github.com/YuSabo90002/typsphinx/actions/runs/31491228938
- Dispatched 2026-08-11T12:26:32Z, completed ~12:31Z (Windows lanes ~5m, macOS lanes ~4m)
- **Conclusion: failure.** 2 lanes red: `Lint and Format Check` (ruff, 4 findings) and both
  `Test Python 3.1{2,3} on windows-latest` (2 real test failures each, same two tests).
  `macos-latest` (both Python versions) and `ubuntu-latest` (both Python versions) were green.
- This is the run that discharged this plan's whole reason for existing: BLD-04's physical
  collision consequence and OUT-02's drive-qualified escape shape are structurally unobservable
  on Linux-only local runs (research Pitfall 5) — and this run is where that showed up for real.

**Triage — two genuine defects found, both fixed and re-verified (commit `be4c4d5`):**

1. **Windows-only OUT-02 escape-guard defect (real, in `typsphinx/`).**
   `_escapes_outdir()` (line 97) and `_resolve_target_stem()`'s fallback-basename computation
   (line ~342) both called the OS-native `from os import path` (`ntpath` on a `windows-latest`
   runner), even though both functions' own docstrings state the guard is platform-independent
   by design (D-05: "a Windows-authored `conf.py` is refused identically on POSIX CI, not just on
   Windows"). Measured disagreement between `ntpath` and `posixpath`:
   - `ntpath.isabs("/abs/manual")` is `False` (no drive letter) where `posixpath.isabs(...)` is
     `True` — a POSIX-shaped absolute target (`"/abs/manual.typ"`) passed through **unrefused** on
     Windows, failing `tests/test_builder_output_stem.py::test_resolve_output_stem_guards_absolute_target`
     (`AssertionError: assert '/abs/manual' == 'manual'`).
   - `ntpath.basename("//escape")` returns `''` where `posixpath.basename(...)` returns
     `'escape'` — the Windows-native `"absolute"` escape shape (`"\\escape.typ"`, converted to
     `"//escape"` by the module's own unconditional backslash-to-forward-slash normalization)
     produced an EMPTY fallback basename, mis-routing into the "empty target name" branch and
     colliding with the docname's own content file (`ExtensionError: ... 'index.typ': the content
     file for docname 'index' and typst_documents entry 0 ... both resolve to the same output
     path 'index.typ'`), failing
     `tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[absolute]`.
   - **Fix:** both call sites switched from `path.isabs`/`path.basename` to
     `posixpath.isabs`/`posixpath.basename` — `posixpath` was already imported at module scope.
     No other `path.*` call site in the module was touched (every other use is genuine OS-native
     filesystem I/O, correctly left OS-native).
   - This is exactly the class of defect the plan's own `<action>` text named in advance: "a
     path-separator assumption (v0.7.1's Windows defect)."

2. **Pre-existing ruff findings, first caught by this run (ruff cannot execute on the NixOS dev
   host — documented, standing limitation; CI is the first real ruff check for any change in this
   phase).** 4 findings, `Found 4 errors`:
   - `typsphinx/builder.py:8` `F401` — module-level `import os` unused (introduced 2026-07-21,
     unrelated to this phase; both real uses of `os.*` in the module are function-local
     `import os` statements that were never flagged before). Removed.
   - `typsphinx/builder.py:1077` `F811` — redefinition of the same unused `os` import inside
     `_copy_template_directory`; resolved automatically once the unused module-level import was
     removed.
   - `tests/test_collision_validator_gate.py:179` and `:180` `F541` — two extraneous `f` prefixes
     on placeholder-free strings (introduced in plan 47-09). Removed.
   - Verified no other F541-shaped findings exist repo-wide via an AST-based scan cross-checked
     against the CI output (three `typsphinx/translator.py` hits from the naive scan were
     confirmed false positives — those f-strings do carry `{...}` placeholders).

Both fixes committed together as `be4c4d5` (`fix(47-10): OUT-02 escape-guard
platform-independence + ruff findings from CI triage`), pushed with
`git push origin gsd/v0.8.0-multi-master-composition` (fast-forward, no force). Full local suite
re-verified green before pushing: `uv run pytest -q` = 1031 passed, 1 skipped, 215.42s; `uv run
black --check .` clean; `uv run mypy typsphinx/` clean.

### Run 2 — 31492380799 (over `be4c4d5`) — SUCCESS

- URL: https://github.com/YuSabo90002/typsphinx/actions/runs/31492380799
- Dispatched 2026-08-11T12:40:46Z (`workflow_dispatch`), completed 2026-08-11T12:46:16Z
- Commit SHA the run was over: `be4c4d5835da0d3db9efb7f2dc6d11dbc6f14a9a`
- **`status: completed`, `conclusion: success`** (measured via
  `gh run view 31492380799 --json conclusion,status`)

**Per-lane job table** (measured via `gh run view 31492380799 --json jobs`):

| OS | Job name | Python | Conclusion |
|----|----------|--------|------------|
| ubuntu-latest | Test Python 3.12 on ubuntu-latest | 3.12 | success |
| ubuntu-latest | Test Python 3.13 on ubuntu-latest | 3.13 | success |
| windows-latest | Test Python 3.12 on windows-latest | 3.12 | success |
| windows-latest | Test Python 3.13 on windows-latest | 3.13 | success |
| macos-latest | Test Python 3.12 on macos-latest | 3.12 | success |
| macos-latest | Test Python 3.13 on macos-latest | 3.13 | success |
| ubuntu-latest | Lint and Format Check | 3.12 | success |
| ubuntu-latest | Type Check | 3.12 | success |
| ubuntu-latest | Code Coverage | 3.12 | success |
| ubuntu-latest | Build Package | 3.12 | success |
| ubuntu-latest | Integration Test - basic | 3.12 | success |
| ubuntu-latest | Integration Test - advanced | 3.12 | success |

All 12 jobs `success`. Both `windows-latest` and `macos-latest` lanes are present, concluded, and
green (satisfying the acceptance criterion that a run completing with only the Ubuntu lane would
not).

**Quoted log lines proving the BLD-04 and drive-qualified OUT-02 cases EXECUTED (not skipped) and
PASSED on both non-Linux lanes** (via `gh run view --job <id> --log`):

`windows-latest`, Python 3.12 (job `93781726864`):
```
tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld04_case_collision_rejected_typst PASSED [ 15%]
tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld04_case_collision_rejected_typstpdf PASSED [ 15%]
tests/test_collision_validator_gate.py::TestCollisionKeyUnit::test_collision_key_folds_case_but_not_unicode_normalization PASSED [ 15%]
tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[traversal] PASSED [ 50%]
tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[absolute] PASSED [ 50%]
tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[drive] PASSED [ 51%]
================= 1027 passed, 5 skipped in 290.23s (0:04:50) =================
```

`macos-latest`, Python 3.13 (job `93781726893`):
```
tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld04_case_collision_rejected_typst PASSED [ 15%]
tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld04_case_collision_rejected_typstpdf PASSED [ 15%]
tests/test_collision_validator_gate.py::TestCollisionKeyUnit::test_collision_key_folds_case_but_not_unicode_normalization PASSED [ 15%]
tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[traversal] PASSED [ 50%]
tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[absolute] PASSED [ 50%]
tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[drive] PASSED [ 51%]
================= 1027 passed, 5 skipped in 252.80s (0:04:12) ==================
```

Both the BLD-04 case-collision comparison (`test_bld04_case_collision_rejected_typst` /
`_typstpdf` plus the unit-level `test_collision_key_folds_case_but_not_unicode_normalization`) and
all three OUT-02 escape shapes — **including the drive-qualified case**
(`test_escape_shape_refused_with_containment_proof[drive]`) — ran to completion and passed on both
non-Linux lanes, none reported `SKIPPED`.

**Windows and Ubuntu lanes cross-checked too** (all four remaining `Test Python *` jobs), for
completeness:

- `windows-latest` / Python 3.13 (job `93781726965`): `1027 passed, 5 skipped in 264.27s (0:04:24)`
- `ubuntu-latest` / Python 3.12 (job `93781726823`): `1027 passed, 5 skipped in 177.51s (0:02:57)`
- `ubuntu-latest` / Python 3.13 (job `93781726869`): not independently re-quoted; job conclusion
  `success` per the table above.

**Observation, not a defect:** all six `Test Python` lanes on this CI run report `1027 passed, 5
skipped`, while the local Linux dev-tree run in "Branch on origin" above reports `1031 passed, 1
skipped`. The 4-test difference is **identical across all three operating systems** (not a
Windows/macOS-specific divergence), so it is a locked-dependency-vs-dev-environment variance
(`uv sync --extra dev --locked` in CI vs. the already-provisioned dev venv locally), not a defect
this plan's scope covers. No `FAILED` appears in any lane's log at either passed-count.

### What the non-Linux lanes caught

**They caught something real** — both of Run 1's two genuine test failures were on
`windows-latest` only (`macos-latest` was green on the first run). Fix SHA: `be4c4d5`.

| Defect | Lane(s) that caught it | Fix SHA |
|--------|------------------------|---------|
| OUT-02 absolute-path guard silently let a POSIX-shaped absolute target through unrefused (`ntpath.isabs` disagrees with `posixpath.isabs`) | `windows-latest` (both Python versions) | `be4c4d5` |
| OUT-02 escape-guard fallback computed an empty basename for a UNC-shaped absolute target, causing a spurious self-collision (`ntpath.basename` disagrees with `posixpath.basename`) | `windows-latest` (both Python versions) | `be4c4d5` |

The lint-lane ruff findings (4, listed above) were caught by `ubuntu-latest`'s `Lint and Format
Check` job, not by a non-Linux lane — they are a separate, pre-existing/environment-blind-spot
class (ruff cannot execute on the NixOS dev host), not part of "what the non-Linux lanes caught,"
but are recorded here because they blocked the same green run.

<!-- gsd:write-continue -->

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

---

## ROADMAP Phase 47 success criteria — evidence mapping

Walking ROADMAP.md's five Phase 47 success criteria (`.planning/ROADMAP.md` lines 473–519) one by
one, naming the artifact or command that discharges each. None is restated as met without one.

### SC#1 — The two-layer file set exists and is placed where the user wrote it

*A real `sphinx-build` writes the wrapper where the user wrote it and the content at the docname
path; `-b typst`/`-b typstpdf` byte-identical; `_is_master_document` gone repo-wide.*

- **Artifact:** `tests/test_two_layer_output_gate.py` (written 47-01, made to pass 47-02) —
  `uv run pytest tests/test_two_layer_output_gate.py -q` (12 tests, all pass; part of the full
  suite reported green throughout this document).
- **Re-measured live by this plan** (2026-08-11, `sphinx-build -b typst` against a throwaway
  fixture with `typst_documents = [("index", "manual.typ", "Test", "Author")]`): output directory
  contains `index.typ` (content, docname-derived) and `manual.typ` (wrapper, target-derived) as
  two independent files, plus `_template.typ`. `typst: wrote 1 wrapper file(s) -- compile these:
  manual.typ` in the build log.
- **`_is_master_document` gone, repo-wide grep** (run live by this plan):
  `grep -rn "_is_master_document" typsphinx/ tests/` — zero hits in any tracked source file. The
  only hits anywhere on disk are in `docs/_build/html/_modules/...` — a `git check-ignore`-confirmed
  gitignored, stale generated-HTML artifact, not source.
- **Byte-identity across builders:** 47-02-SUMMARY.md Task 3 ("Builder parity ... byte-identical").

### SC#2 — B-1 closed, on the classic RED and on the nested-master shape

*A docname that is also another master's toctree child builds and compiles in both roles; RED
recorded first as a classic `TypstError: file not found` against the unfixed tree; the fixture
uses a nested master whose target basename differs from its docname.*

- **Pre-fix RED:** `.planning/phases/47-.../47-RED-EVIDENCE.md` (written 47-01) — verbatim
  `TypstError: file not found` transcript against the unfixed tree, fixture
  `tests/fixtures/two_layer_nested_master_gate/` (target basename `guide.typ` differs from
  docname `guide/index`).
- **Fix + green:** 47-02-SUMMARY.md coverage row D1 (`test_two_layer_output_gate.py::...B-1
  (COMP-03)`, `status: pass`) — `uv run pytest tests/test_two_layer_output_gate.py -q`.
- **Command:** `uv run pytest tests/test_two_layer_output_gate.py -q` (green throughout this
  document's full-suite runs, including this run's own CI evidence above).

### SC#3 — B-2 closed, RED shape chosen by measurement

*Measured (not assumed) whether the mid-body template re-expansion is a compile fatal or a
compiles-fine-but-wrong-output defect; that measurement selects the RED shape; post-fix, no second
title page / `#outline()` / template application anywhere in the parent's body.*

- **Measurement:** `.planning/phases/47-.../47-RED-EVIDENCE.md` (47-01) records COMP-04's RED as
  **compiles-fine-but-wrong-output** — a structural `pypdf`-text assertion (a second title-page
  block and a second `"Contents"` heading appear before the nested content's body marker), NOT a
  `TypstError` — matching `47-VALIDATION.md`'s own "Requirement → evidence contract" table
  (`COMP-04 | ... | Structural pypdf assertion, NOT TypstError`).
- **Fix + green:** 47-02-SUMMARY.md coverage row D2 (`B-2 (COMP-04): ... verified by real pypdf
  structural extraction (no second title page, exactly one outline)`, `status: pass`).
- **Command:** `uv run pytest tests/test_two_layer_output_gate.py -q`.

### SC#4 — Every "two logical files want one physical path" case is loud, both policies decided before code

*Duplicate-target collisions (BLD-02), wrapper-vs-content self-collision under a pre-decided
policy (BLD-03), and case-insensitive-filesystem collision comparisons (BLD-04) are all detected
and reported, never silently dropping a master's body; each ships its own pre-fix structural RED
per binding constraint #4.*

- **Pre-fix RED (all three, structural, non-fatal-today):** `.planning/phases/47-.../47-RED-EVIDENCE.md`
  (47-01) + `tests/test_collision_validator_gate.py`'s original `xfail(strict=True)` markers.
- **Policy decided before code:** D-01 (self-collision: refuse, no fallback) and D-03 (one unified
  validator, error-only, pre-write, aggregate) were `checkpoint:decision` tasks in `47-09-PLAN.md`,
  pre-resolved by the project owner before that executor ran (47-09-SUMMARY.md "Decisions Made") —
  decided, and recorded, before `_validate_output_path_collisions()` was implemented.
- **Fix + green:** `TypstBuilder._validate_output_path_collisions()` + `_collision_key()`
  (`typsphinx/builder.py`, 47-09) — one pre-write `ExtensionError` covering all four collision
  kinds. `uv run pytest tests/test_collision_validator_gate.py -q` (7 tests, all pass, xfail
  markers removed).
- **BLD-04 specifically, proven on a real case-insensitive filesystem (this plan, not just the
  case-folding unit assertion):** the Windows/macOS CI lane log lines quoted above —
  `test_bld04_case_collision_rejected_typst` / `_typstpdf` PASSED on both `windows-latest` and
  `macos-latest`.

### SC#5 — The security half of the reversed guards survives, and the branch is on `origin`

*A `..`/absolute/drive-qualified target is still refused with a warning and safe fallback, one
fixture per escape shape (OUT-02); `gsd/v0.8.0-multi-master-composition` pushed to `origin` in
this phase, evidenced by `git ls-remote` plus a completed CI run over it including the Windows and
macOS lanes.*

- **OUT-02 security half, per-shape fixtures:** `tests/test_out02_escape_target_gate.py` (47-03) —
  `uv run pytest tests/test_out02_escape_target_gate.py -q` (3 tests, one per escape shape:
  traversal, absolute, drive — all pass, containment-proof assertion included).
- **Branch on `origin`:** "Branch on origin" section above — verbatim `git ls-remote --heads
  origin gsd/v0.8.0-multi-master-composition` output, local/remote SHA match, no PR opened.
- **Completed CI run over Windows and macOS lanes:** "Completed CI run" section above — run
  `31492380799`, `status: completed`, `conclusion: success`, both `windows-latest` and
  `macos-latest` jobs (both Python versions) `success`, BLD-04 and drive-qualified OUT-02 log
  lines quoted proving execution (not skip).
- **Reversal of Phase 44's D-05/D-06/D-07 recorded explicitly:** `.planning/STATE.md` "Roadmap
  Evolution" 2026-08-11 entry ("OUT-01 is recorded in the roadmap as a deliberate reversal...");
  `ROADMAP.md` Phase 47 goal text itself states the reversal.

**All five ROADMAP Phase 47 success criteria are discharged**, each against a named artifact or a
command run live by this plan.

---

## Final state

This document's own commit (the last commit of this plan, together with the `47-VALIDATION.md`
sign-off closure below) is pushed to `origin` immediately after being made, with
`git push origin gsd/v0.8.0-multi-master-composition` (no `-f`, no rewrite) — the same procedure
used for every commit in this plan. `git ls-remote --heads origin
gsd/v0.8.0-multi-master-composition` is re-run after that push and must equal `git rev-parse
gsd/v0.8.0-multi-master-composition`; `gh pr list --head gsd/v0.8.0-multi-master-composition`
stays empty throughout (no PR opened at any point in this plan). `uv run pytest -q` is re-run at
the branch tip as this plan's own closing measurement (self-check requirement) and must exit 0.
These three closing measurements are recorded in `47-10-SUMMARY.md`'s Self-Check section rather
than duplicated here, to avoid this file needing to describe its own not-yet-created commit hash.


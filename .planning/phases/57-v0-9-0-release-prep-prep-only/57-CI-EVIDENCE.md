# Phase 57 — CI Evidence (two dispatches, D-12)

**Provisioning note:** all commands below were run inside this plan's isolated git worktree, after
`unset VIRTUAL_ENV; unset UV_PROJECT_ENVIRONMENT; uv sync --extra dev`, per this project's
`CLAUDE.md` § "Worktree-isolated execution".

This file carries **both** of D-12's runs. Run 1 (this plan, `57-02`) is the **pre-bump check
run** — dispatched against the untouched phase-head tip, before any of this phase's own edits
exist, so it separates "Phases 54/54.1/55/56 already have a cross-platform defect" from "this
phase's version bump broke something". Run 2 — the **post-bump authority run** — is appended by
plan `57-05`.

---

## Run 1 — pre-bump check run

### Why a separate check run

The last full CI run on this branch predates Phases 54, 54.1, 55 and 56 entirely — measured live
below via `gh run list` rather than transcribed from `57-CONTEXT.md`'s run id — so those four
phases have never been exercised on the `windows-latest` or `macos-latest` lanes at all. Those two
lanes are the only route to catching platform-specific defects: they caught a real cp1252 defect
at the v0.7.0 close and a real path-separator defect at the v0.7.1 close, and no local run on this
development machine reproduces either lane. Dispatching before this phase's own bump lets any
failure be attributed correctly — to the four phases that precede this one, not to a bump that
does not exist at the dispatched SHA.

### Pre-dispatch confirmation

**Step 1 — confirm this really is the pre-bump tree.**

Command:
```
$ grep -n '^version = ' pyproject.toml
```
Verbatim output:
```
7:version = "0.8.0"
```

Command:
```
$ grep -c '^## \[0\.9\.0\]' CHANGELOG.md
```
Verbatim output:
```
0
```

Both confirm the pre-bump tree: `pyproject.toml` still carries the prior release version
(`0.8.0`), and `CHANGELOG.md` carries no `## [0.9.0]` heading. Run 1 is a clean pre-bump baseline.

**Step 2 — D-13's sequencing precondition, proven independently for this dispatch.**

Command:
```
$ uv lock --check
```
Verbatim output:
```
Resolved 89 packages in 0.52ms
```
Exit 0 — the lockfile agrees with the manifest, so every CI job's `uv sync --extra dev --locked`
step can install.

Command:
```
$ grep -c locked .github/workflows/*.yml
```
Verbatim output:
```
.github/workflows/docs.yml:1
.github/workflows/links.yml:0
.github/workflows/drift.yml:1
.github/workflows/release.yml:2
.github/workflows/ci.yml:6
```
Measured `--locked` step total for this dispatch: **10** (`ci.yml` 6 + `release.yml` 2 +
`docs.yml` 1 + `drift.yml` 1). This is the count measured live here, not transcribed from
`57-CONTEXT.md` (which says eleven) or `57-RESEARCH.md` (which says 10 — coincidentally correct,
but not the source of this number).

### Branch position

**Step 3 — re-measured, not transcribed.**

Command:
```
$ git rev-list --count origin/gsd/v0.9.0-per-document-templates..HEAD
```
Verbatim output:
```
195
```
Neither `57-CONTEXT.md`'s 188 nor `57-RESEARCH.md`'s 190 nor the planner's 192 — all three were
stale by construction, exactly as this plan's `must_haves.truths` predicted. `195` is this
execution's own live measurement.

Command:
```
$ git merge-base --is-ancestor origin/gsd/v0.9.0-per-document-templates HEAD && echo fast-forward-ok
```
Verbatim output:
```
fast-forward-ok
```
The ancestry check passed, so the push below is a plain fast-forward, never a force push.

**Step 4 — baseline this run improves on, captured live before dispatch.**

Command:
```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.0-per-document-templates --limit 5 --json databaseId,headSha,event,status,conclusion,createdAt
```
Verbatim output:
```json
[{"conclusion":"success","createdAt":"2026-08-15T12:30:25Z","databaseId":31884774067,"event":"workflow_dispatch","headSha":"35ee8a0ee8a4f8701c99a6596be8e37d975de307","status":"completed"},{"conclusion":"success","createdAt":"2026-08-15T08:56:07Z","databaseId":31875707734,"event":"workflow_dispatch","headSha":"d1eff10076af99d50b9bbb90acd6054a6b09762c","status":"completed"},{"conclusion":"failure","createdAt":"2026-08-15T08:48:09Z","databaseId":31875380355,"event":"workflow_dispatch","headSha":"9172aa1ca755bf2156e881463ddb10b545d19471","status":"completed"}]
```
The last full CI run on this branch is `31884774067`, 2026-08-15 — the Phase 53 era — matching
D-12's claim, measured live here rather than repeating the run id `57-CONTEXT.md` names.

### Pushed SHA

Command:
```
$ git rev-parse HEAD
```
Verbatim output:
```
78bd595d344f46c6e1f5a18bce0e24da1f66a9ee
```

### Push

Command:
```
$ git push origin HEAD:refs/heads/gsd/v0.9.0-per-document-templates
```
Verbatim output:
```
To https://github.com/YuSabo90002/typsphinx.git
   35ee8a0e..78bd595d  HEAD -> gsd/v0.9.0-per-document-templates
```
A plain fast-forward from the measured remote tip `35ee8a0ee8a4f8701c99a6596be8e37d975de307`; not
rejected, so no force-push was needed or used.

Confirmation:
```
$ git rev-parse origin/gsd/v0.9.0-per-document-templates
78bd595d344f46c6e1f5a18bce0e24da1f66a9ee
```
Equal to local HEAD — the pushed SHA is confirmed on `origin`.

### Dispatch

Command:
```
$ gh workflow run ci.yml --ref gsd/v0.9.0-per-document-templates
```
Verbatim output:
```
https://github.com/YuSabo90002/typsphinx/actions/runs/31956166848
```

Matched by `headSha`:
```
$ gh run view 31956166848 --json databaseId,headSha,event,status,workflowName
{"databaseId":31956166848,"headSha":"78bd595d344f46c6e1f5a18bce0e24da1f66a9ee","event":"workflow_dispatch","status":"queued","workflowName":"CI"}
```
`headSha` equals the pushed SHA.

Run id (`RUN_ID_1`): `31956166848`
Run URL: `https://github.com/YuSabo90002/typsphinx/actions/runs/31956166848`

Overall run conclusion, confirmed after `gh run watch`:
```
$ gh run view 31956166848 --json status,conclusion
{"conclusion":"failure","status":"completed"}
```

### Job conclusions

Command:
```
$ gh run view 31956166848 --json jobs --jq '.jobs[] | "\(.name)\t\(.conclusion)"'
```

| Job | Conclusion |
|---|---|
| Build Package | success |
| Integration Test - advanced | success |
| Integration Test - basic | success |
| Type Check | success |
| Lint and Format Check | success |
| Test Python 3.13 on ubuntu-latest | success |
| Test Python 3.13 on windows-latest | **failure** |
| Test Python 3.12 on windows-latest | **failure** |
| Test Python 3.13 on macos-latest | success |
| Code Coverage | success |
| Test Python 3.12 on macos-latest | success |
| Test Python 3.12 on ubuntu-latest | success |

12 jobs total (both cross-platform lanes present: `windows-latest` x2, `macos-latest` x2). 10 of
12 succeed.
```
$ gh run view 31956166848 --json jobs --jq '[.jobs[]|select(.conclusion!="success")]|length'
2
```

### Disposition

**Run 1 is NOT all-`success`. Two jobs fail — both `windows-latest` lanes (Python 3.12 and
3.13) — on the identical assertion, in a test file untouched by this plan.** This is a real,
reproducible pre-existing defect belonging to Phases 54/54.1/55/56 (specifically the Phase 54.1
`templates_path` collision-refusal work), **not** to this phase's version bump, which does not
exist at the dispatched SHA (confirmed above: `pyproject.toml` still reads `0.8.0`, `CHANGELOG.md`
carries no `## [0.9.0]` heading).

Failing test (both lanes, identical failure):
```
tests/test_templates_path_collision_gate.py::TestMultiRelationAggregationGate::test_multi_relation_each_key_names_own_bundle_dir_and_own_entry
```

Log excerpt (`gh run view 31956166848 --log-failed`, Python 3.13 on windows-latest, verbatim):
```
E       AssertionError: Expected beta's resolved bundle directory (containing '_templates/nested') named:
E         typst: 3 pre-write template path failure(s): 'alpha': registry key 'alpha''s resolved template bundle directory 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates' collides with the Sphinx templates_path entry '_templates' (resolved to 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates') -- the whole bundle directory is copied to the build output, so this would republish the project's Sphinx template directory; move the Typst template into a directory that is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match; 'beta': registry key 'beta''s resolved template bundle directory 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates\\nested' collides with the Sphinx templates_path entry '_templates' (resolved to 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates') -- the whole bundle directory is copied to the build output, so this would republish the project's Sphinx template directory; move the Typst template into a directory that is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match; 'gamma': registry key 'gamma''s resolved template bundle directory 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_typst' collides with the Sphinx templates_path entry '_typst/inner' (resolved to 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_typst/inner') -- the whole bundle directory is copied to the build output, so this would republish the project's Sphinx template directory; move the Typst template into a directory that is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match
tests\test_templates_path_collision_gate.py:255: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_templates_path_collision_gate.py::TestMultiRelationAggregationGate::test_multi_relation_each_key_names_own_bundle_dir_and_own_entry
============ 1 failed, 1412 passed, 9 skipped in 328.33s (0:05:28) ============
```

**Root cause read directly from the excerpt:** the test asserts the substring `'_templates/nested'`
(forward slash) is present in the aggregate error message, but the actual message contains
`'_templates\\nested'` (backslash) — the path is joined with `os.path.join`/`pathlib`, which uses
the native Windows separator. This is exactly the class of defect this plan's `must_haves.truths`
names: "a real path-separator defect at the v0.7.1 close" — surfacing here for the first time
because Phase 54.1 (which authored this test and the `templates_path` collision-refusal message it
asserts against) has never before been through the `windows-latest` lane. The Python 3.12 lane
fails identically (`gh run view 31956166848 --log-failed` shows the same assertion, same test, same
file, `1 failed, 1412 passed, 9 skipped in 348.21s`).

**This is not this phase's defect to fix.** `test_templates_path_collision_gate.py` is outside this
plan's declared `files_modified` scope (`57-CI-EVIDENCE.md` only), and per the SCOPE BOUNDARY rule
("Only auto-fix issues DIRECTLY caused by the current task's changes... log... do NOT fix them"),
this plan does not attempt a fix. It is filed to the cross-phase defect register
(`.planning/WINDOWS.md`) as a `todo` entry with `phase: 57`, attributed explicitly to Phase 54.1's
test authorship, so it stays visible at ship time and blocks `/gsd-ship` until resolved or waived.
This plan does **not** proceed to plan 57-05's post-bump authority dispatch expecting it to pass —
that dispatch is 57-05's own concern, and this defect will reproduce there too unless fixed first.

No gate was weakened, no marker removed, no assertion deleted to make this run report green.

---

## Run 2 — post-bump authority run

Written by plan 57-05.

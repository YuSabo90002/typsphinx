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

Written by plan `57-05`, provisioned in this plan's isolated git worktree per this project's
`CLAUDE.md` § "Worktree-isolated execution" (`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync
--extra dev`).

### Pre-push confirmation

Command:
```
$ grep -n '^version = ' pyproject.toml
```
Verbatim output:
```
7:version = "0.9.0"
```

Command:
```
$ grep -c '^## \[0\.9\.0\]' CHANGELOG.md
```
Verbatim output:
```
1
```

Command:
```
$ grep -c '"0\.9\.0",' tests/test_changelog_page_gate.py
```
Verbatim output:
```
1
```

Command:
```
$ grep -c '^Migrating from 0\.8\.x to 0\.9\.0$' docs/source/changelog.rst
```
Verbatim output:
```
1
```

All four Wave-1 changes are present at the dispatched SHA: the bumped version, the `## [0.9.0]`
CHANGELOG heading, the appended `RELEASE_VERSIONS` coverage entry, and the migration guide section.

### Ordering proof (the D-13 sequencing constraint)

Command:
```
$ uv lock --check
```
Verbatim output:
```
Resolved 89 packages in 0.64ms
```
Exit 0 — the lockfile agrees with the manifest.

Command:
```
$ git log -1 --format='%H %cI %s' -- uv.lock
```
Verbatim output:
```
237fc0a0779538d9f6c0789d197e1300a2e0fe8f 2026-08-17T00:36:42+09:00 feat(57-01): bump version to 0.9.0 across manifest, README and lockfile
```

Command:
```
$ git merge-base --is-ancestor 237fc0a0779538d9f6c0789d197e1300a2e0fe8f HEAD && echo lock-precedes-dispatch
```
Verbatim output:
```
lock-precedes-dispatch
```
Exit 0 — the lockfile commit strictly precedes the dispatched SHA.

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
`docs.yml` 1 + `drift.yml` 1) — counted live here, not transcribed from a planning document.

**This is the ordering edge case the phase resolves explicitly:** the lockfile commit must
strictly precede the dispatched SHA, because every CI job opens with
`uv sync --extra dev --locked`, and a stale lockfile fails the install before any test, lint or
type signal exists — the measured failure mode of the two open dependabot pull requests (#128,
#123). Both conditions (`uv lock --check` exit 0, and `git merge-base --is-ancestor` exit 0) held
before this dispatch, so the install succeeded and a real signal was produced.

### Branch position

Command:
```
$ git rev-list --count origin/gsd/v0.9.0-per-document-templates..HEAD
```
Verbatim output:
```
28
```
Re-measured live at execution time, not copied from `57-CONTEXT.md`, `57-RESEARCH.md`, or a
sibling plan.

Command:
```
$ git merge-base --is-ancestor origin/gsd/v0.9.0-per-document-templates HEAD && echo fast-forward-ok
```
Verbatim output:
```
fast-forward-ok
```

### Pushed SHA

Command:
```
$ git rev-parse HEAD
```
Verbatim output:
```
bfcc6f6dab2616337369d62e67fddba3b378547f
```

### Push

Command:
```
$ git push origin HEAD:refs/heads/gsd/v0.9.0-per-document-templates
```
Verbatim output:
```
To https://github.com/YuSabo90002/typsphinx.git
   78bd595d..bfcc6f6d  HEAD -> gsd/v0.9.0-per-document-templates
```
A plain fast-forward from run 1's pushed tip `78bd595d344f46c6e1f5a18bce0e24da1f66a9ee`; not
rejected, so no force-push was needed or used.

Confirmation:
```
$ git rev-parse origin/gsd/v0.9.0-per-document-templates
bfcc6f6dab2616337369d62e67fddba3b378547f
```
Equal to local HEAD.

### Dispatch

Command:
```
$ gh workflow run ci.yml --ref gsd/v0.9.0-per-document-templates
```
Verbatim output:
```
https://github.com/YuSabo90002/typsphinx/actions/runs/31959060298
```

Matched by `headSha` (run 1's entry, `31956166848`, also appears in this list, so the match was
made on `headSha`, never on position):
```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.0-per-document-templates --limit 5 --json databaseId,headSha,event,status
[{"databaseId":31959060298,"event":"workflow_dispatch","headSha":"bfcc6f6dab2616337369d62e67fddba3b378547f","status":"queued"},{"databaseId":31956166848,"event":"workflow_dispatch","headSha":"78bd595d344f46c6e1f5a18bce0e24da1f66a9ee","status":"completed"}, ...]
```

Run id (`RUN_ID_2`): `31959060298`
Run URL: `https://github.com/YuSabo90002/typsphinx/actions/runs/31959060298`

Overall run conclusion, confirmed after `gh run watch`:
```
$ gh run view 31959060298 --json status,conclusion
{"conclusion":"failure","status":"completed"}
```

### Job conclusions

Command:
```
$ gh run view 31959060298 --json jobs --jq '.jobs[] | "\(.name)\t\(.conclusion)"'
```

| Job | Conclusion |
|---|---|
| Lint and Format Check | success |
| Code Coverage | success |
| Integration Test - advanced | success |
| Integration Test - basic | success |
| Build Package | success |
| Type Check | success |
| Test Python 3.13 on windows-latest | **failure** |
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on ubuntu-latest | success |
| Test Python 3.12 on ubuntu-latest | success |
| Test Python 3.12 on windows-latest | **failure** |
| Test Python 3.13 on macos-latest | success |

12 jobs total (both cross-platform lanes present: `windows-latest` x2, `macos-latest` x2). 10 of
12 succeed.
```
$ gh run view 31959060298 --json jobs --jq '[.jobs[]|select(.conclusion!="success")]|length'
2
```

**Run 2 is NOT all-`success`.** This run does not discharge SC#3's toolchain half; see
"Disposition" below.

### Built-wheel content check (SC#3)

The Build Package job (which itself completed `success`) ran the wheel-content verification step
independently of the failing lanes. Its own step output, verbatim (`gh run view 31959060298 --log
--job 95194139889`):
```
Build Package	Build package	2026-08-16T16:35:48.9298742Z ##[group]Run uv run python -c "
...
Build Package	Verify wheel carries the template bundle	2026-08-16T16:35:50.9639999Z Installed 25 packages in 56ms
Build Package	Verify wheel carries the template bundle	2026-08-16T16:35:50.9951980Z OK: 'typsphinx/templates/README.md' found in 'dist/typsphinx-0.9.0-py3-none-any.whl'
```
`OK: 'typsphinx/templates/README.md' found in 'dist/typsphinx-0.9.0-py3-none-any.whl'` — the
bundled template file survives the wheel build. The editable install used everywhere else in CI
(and in every other job of this same run) never packs a wheel, so this is the only place in CI
that can detect a narrowed `[tool.setuptools.package-data]` glob; it passed independently of the
Windows-lane failure below, and is not contingent on it.

### Why this run is the authority

Under D-13, CI is the authority for the six-lane `{ubuntu, windows, macos}-latest` x `{3.12,
3.13}` matrix, `black`/`ruff` lint (Lint and Format Check), and the type check (Type Check) —
independent grounds from the retracted "ruff cannot run locally" premise, since the Windows and
macOS lanes are structurally unreachable from this development machine and caught real cp1252 and
path-separator defects at the two previous milestone closes (v0.7.1, and again here). Local runs
remain the authority for both docs tox environments and the full-corpus / multi-template PDF
gates, collected separately by plans `57-06` and `57-07`. Local `ruff` runnability was
re-measured this milestone (`57-CONTEXT.md` R-4: `uv run ruff check .` → `All checks passed!`,
exit 0) and is an additive pre-flight only — it does not move authority off CI, because this very
run demonstrates the point: the failing assertion here is Windows-only and cannot be reproduced or
caught on this Linux host at all.

### Disposition

**Run 2 is NOT all-`success`. The same two jobs fail as run 1 — both `windows-latest` lanes
(Python 3.12 and 3.13) — on the same test, now at a shifted line number, but with a genuinely
different failure signature than run 1.** Plan `57-10` (merged into this Wave-1 tip, see the
`### Pre-push confirmation` greps above and the commit range in the Cross-reference section)
attempted to fix the separator mismatch that failed run 1, but the fix was measured incomplete by
this dispatch.

Failing test (both lanes, identical failure):
```
tests/test_templates_path_collision_gate.py::TestMultiRelationAggregationGate::test_multi_relation_each_key_names_own_bundle_dir_and_own_entry
```

Log excerpt (`gh run view 31959060298 --log-failed`, Python 3.13 on windows-latest, verbatim):
```
E       AssertionError: Expected beta's resolved bundle directory (containing '_templates\\nested') named:
E         typst: 3 pre-write template path failure(s): 'alpha': registry key 'alpha''s resolved template bundle directory 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates' collides with the Sphinx templates_path entry '_templates' (resolved to 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates') -- the whole bundle directory is copied to the build output, so this would republish the project's Sphinx template directory; move the Typst template into a directory that is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match; 'beta': registry key 'beta''s resolved template bundle directory 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates\\nested' collides with the Sphinx templates_path entry '_templates' (resolved to 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates') -- the whole bundle directory is copied to the build output, so this would republish the project's Sphinx template directory; move the Typst template into a directory that is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match; 'gamma': registry key 'gamma''s resolved template bundle directory 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_typst' collides with the Sphinx templates_path entry '_typst/inner' (resolved to 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_typst/inner') -- the whole bundle directory is copied to the build output, so this would republish the project's Sphinx template directory; move the Typst template into a directory that is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match
tests\test_templates_path_collision_gate.py:263: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_templates_path_collision_gate.py::TestMultiRelationAggregationGate::test_multi_relation_each_key_names_own_bundle_dir_and_own_entry
============ 1 failed, 1412 passed, 9 skipped in 352.51s (0:05:52) ==================
```
(Python 3.12 lane fails identically: `1 failed, 1412 passed, 9 skipped in 345.44s`.)

**Root cause, read from `typsphinx/builder.py:1296` (READ ONLY — this plan does not edit it):**
```python
f"registry key {key!r}'s resolved template "
f"bundle directory {bundle_dir!r} collides "
```
The message is built with `{bundle_dir!r}` — Python's `repr()` conversion, not `str()`. On
Windows, `bundle_dir` is a plain string with single-backslash separators
(`...\_templates\nested`); `repr()` of a string escapes every real backslash character into two
characters for its output, and that escaped text is what the f-string inserts into the raised
message verbatim — not a display-only artifact, but the actual runtime content of `message`. So
the message this test greps against literally contains **doubled** backslashes
(`...\\_templates\\nested`, two real backslash characters at every separator), confirmed by
byte-level inspection of the raw log text above (`E         typst: 3 pre-write...` line, which is
`message` interpolated via `f"{message}"`, i.e. `str()`, so its doubled backslashes are real
message content, not pytest's own `assert`-line repr layer).

`57-10`'s fix built `beta_bundle_tail = str(Path("_templates") / "nested")`
(`tests/test_templates_path_collision_gate.py:262`), which on Windows yields a **single**
backslash. `57-10`'s evidence (`57-WINDOWS-FIX-EVIDENCE.md`) read run 1's log excerpt — the same
doubled-backslash text reproduced above — and attributed it to "the platform's native `os.sep`
(backslash on Windows)", i.e. one backslash, not recognizing that the excerpt already showed the
`!r`-escaped doubled form. A single-backslash expected substring can never match a message built
from `repr()`, which is why run 2 reproduces the identical failure at the assertion's new line
number (255 → 263, after `57-10`'s own edit inserted seven comment/code lines above it).

**This is not this plan's defect to fix.** `typsphinx/builder.py` and
`tests/test_templates_path_collision_gate.py` are both outside this plan's declared
`files_modified` scope (`57-CI-EVIDENCE.md` only), and this plan's own `<threat_model>`
prohibitions explicitly forbid editing `typsphinx/` — this is a prep-only release phase. Per the
SCOPE BOUNDARY rule, this plan does not attempt a fix. It is filed to the cross-phase defect
register (`.planning/WINDOWS.md`) as entry 10 (`todo`, `phase: 57`), cross-referencing entry 9
(which stays `open`, not `fixed` — `57-10`'s fix did not clear it), with the `!r`-vs-`str()` root
cause recorded so the next fix attempt does not repeat `57-10`'s measurement error.

**This plan's stated must_haves and acceptance criteria — "every job `success`" — are NOT met by
run 2.** No gate was weakened, no marker removed, no assertion deleted to make this run report
green. Per this plan's own action text ("If any job fails, do not paper over it and do not weaken
a gate: report the failure... and stop"), this plan stops here rather than dispatching a third run
against an unfixed tree. **SC#3's toolchain half is NOT discharged by this plan.** A follow-up fix
plan (recommended: a `57-11` inside this phase, or a Phase 58 hotfix if the phase has already
closed) must correct the message/assertion mismatch using the `!r`-escaping root cause recorded
above, then a fresh dispatch recorded here or in a successor evidence file.

## Cross-reference — what changed between the two runs

| | Run 1 | Run 2 |
|---|---|---|
| Run id | `31956166848` | `31959060298` |
| headSha | `78bd595d344f46c6e1f5a18bce0e24da1f66a9ee` | `bfcc6f6dab2616337369d62e67fddba3b378547f` |
| Event | `workflow_dispatch` | `workflow_dispatch` |
| Conclusion | `failure` | `failure` |
| Failing-job count | 2 (`windows-latest` x2) | 2 (`windows-latest` x2) |

SHA range (`git log --oneline 78bd595d344f46c6e1f5a18bce0e24da1f66a9ee..bfcc6f6dab2616337369d62e67fddba3b378547f`):
```
bfcc6f6d docs(phase-57): update tracking after 57-10
015bc0f0 chore: merge executor worktree (worktree-agent-ac64e8b56dc8252a5)
2cb7888b docs(57-10): add plan summary
e6430c2f docs(57-10): record RED/GREEN evidence and transition WINDOWS.md entry 9
a7185a13 fix(57-10): make resolved-path assertion separator-portable
4beb9a50 docs(57): add plan 57-10 to fix the Windows-lane assertion, gate 57-05 on it
b1cd0006 docs(phase-57): update tracking after wave 1
22df73dd fix(57): rewrap 0.9.0 migration guide to satisfy the docs template-layout gate
b8e996a5 chore: merge executor worktree (worktree-agent-ae7038f9990cd14de)
d643fb96 chore: merge executor worktree (worktree-agent-a9c8971dc6e4cb753)
e348cd73 chore: merge executor worktree (worktree-agent-a7c8226c607f8f053)
e573b361 chore: merge executor worktree (worktree-agent-aa884129710c018db)
a0d4ec96 docs(57-04): complete migration-guide plan
dfd2d6ae docs(57-02): append self-check results to summary
d91f6969 docs(57-02): add plan 02 summary
381b6ebf docs(57-04): discharge D-10 by live discovery grep; record D-11 decline
131e0d1e docs(57-02): dispatch and record D-12 run 1, the pre-bump CI check run
2a128096 docs(57-04): write the Migrating from 0.8.x to 0.9.0 guide
d25dbe49 docs(57-03): append self-check result to SUMMARY
9bf723c2 docs(57-03): add plan SUMMARY
967c01a2 docs(57-01): complete v0.9.0 version bump and release-machinery liveness proof plan
5ec81e36 docs(57-03): record SC#2 CHANGELOG evidence
dcee0201 feat(57-03): roll over CHANGELOG tail block, extend page-gate coverage
48933cb4 docs(57-01): record REQUIREMENTS.md closeout guard baseline for REL-08
e74733d8 feat(57-03): author curated ## [0.9.0] CHANGELOG section
5d368dc8 docs(57-01): record SC#1 version-sync guard battery and D-13 evidence
01e50da1 docs(57-04): record D-08 before/after build transcripts in worktree evidence
237fc0a0 feat(57-01): bump version to 0.9.0 across manifest, README and lockfile
```
This range is all four Wave-1 plans plus `57-10`'s Windows fix — exactly the set the
`### Pre-push confirmation` greps above confirm landed at the dispatched SHA.

**Attribution:** the two `windows-latest` job failures appear in **both** runs, on the **same
test** (`test_multi_relation_each_key_names_own_bundle_dir_and_own_entry`), so per the stated
attribution rule this is a pre-existing defect belonging to the phases and plans that precede this
one (Phase 54.1's message construction, compounded by `57-10`'s incomplete fix attempt) — **not**
a regression introduced by this plan's own push (which touched only `.planning/WINDOWS.md` before
dispatch, confirmed empty against `typsphinx/` and `.github/` below). The failure signature did
change between the two runs (run 1: forward-slash-vs-backslash mismatch; run 2: single-backslash-
vs-doubled-backslash mismatch after `57-10`'s partial fix), which is itself evidence that a real
edit landed between them rather than the identical assertion simply being re-run — recorded
verbatim above rather than glossed over. Not every job in both runs is `success`, so the
attribution rule is exercised on real data rather than left hypothetical.

Fence check, run this plan:
```
$ git tag -l v0.9.0
(empty)
$ git ls-remote --tags origin v0.9.0
(empty)
$ git diff --name-only -- typsphinx/ .github/
(empty)
```

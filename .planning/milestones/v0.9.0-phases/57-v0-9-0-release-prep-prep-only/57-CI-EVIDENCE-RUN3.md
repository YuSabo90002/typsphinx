# Phase 57 — CI Evidence, Run 3 (the fresh authority run that discharges 57-05's SC#3)

**Successor evidence file.** `57-05-SUMMARY.md` halted with SC#3's toolchain half undischarged and
prescribed the route out in its own § Next Phase Readiness: *"a follow-up fix plan (recommended:
`57-11`) … followed by a fresh CI dispatch recorded in a successor evidence file."* `57-11` landed
the fix; this file is that successor record. It does not restate runs 1 and 2 — those stay in
`57-CI-EVIDENCE.md`, which this file supersedes only for the all-jobs-green criterion.

**Who produced this.** The dispatch and every measurement below were performed by the
`/gsd-execute-phase 57` orchestrator on 2026-08-22, in the primary checkout on branch
`gsd/v0.9.0-per-document-templates` (not a worktree — `.git` is a directory here). Every value is
a live `gh` / `git` read, not a transcription from a SUMMARY.

---

## Result

| | Run 1 (`57-02`) | Run 2 (`57-05`) | **Run 3 (this file)** |
|---|---|---|---|
| Run id | `31956166848` | `31959060298` | **`32557477023`** |
| Dispatched SHA | `78bd595d` | `bfcc6f6d` | **`fbbf48cd`** |
| Tree | pre-bump | post-bump, pre-fix | **post-bump, post-fix** |
| Conclusion | failure | failure (10/12) | **success (12/12)** |
| `windows-latest` lanes | both fail | both fail | **both pass** |

The defect that failed both `windows-latest` lanes in runs 1 and 2 was `repr()` escaping in three
pre-write template-path refusal messages (`typsphinx/builder.py`), fixed by `57-11`. Run 3 is the
first CI run whose tree carries that fix.

## Dispatch

```
$ git push origin gsd/v0.9.0-per-document-templates
To https://github.com/YuSabo90002/typsphinx.git
   bfcc6f6d..fbbf48cd  gsd/v0.9.0-per-document-templates -> gsd/v0.9.0-per-document-templates

$ gh workflow run ci.yml --ref gsd/v0.9.0-per-document-templates
https://github.com/YuSabo90002/typsphinx/actions/runs/32557477023
```

`ci.yml`'s `on:` block is `push: [main, develop]`, `pull_request: [main, develop]`,
`workflow_dispatch`. This branch is in neither push list, so the push alone fires nothing — the
explicit `workflow_dispatch` is required, exactly as runs 1 and 2 were dispatched.

## Run metadata (live read)

```
$ gh run view 32557477023 --json status,conclusion,headSha,headBranch,createdAt,updatedAt,event,url
conclusion=success
createdAt=2026-08-22T06:38:04Z
event=workflow_dispatch
headBranch=gsd/v0.9.0-per-document-templates
headSha=fbbf48cd2f07486c1d2a01d054800e1c84f8df0b
status=completed
updatedAt=2026-08-22T06:45:17Z
url=https://github.com/YuSabo90002/typsphinx/actions/runs/32557477023
```

The dispatched SHA `fbbf48cd` is the tip that carries `57-11`'s four commits
(`699d4c0e` fix, `6cfdde70` guard, `965395cf` records, `e710d9ed` SUMMARY), its merge commit
`11c14366`, and the tracking commit `fbbf48cd`.

## Job conclusions — all 12

```
$ gh run view 32557477023 --json jobs --jq '.jobs[] | "\(.conclusion)\t\(.name)"'
success	Lint and Format Check
success	Code Coverage
success	Type Check
success	Build Package
success	Integration Test - basic
success	Integration Test - advanced
success	Test Python 3.12 on ubuntu-latest
success	Test Python 3.13 on ubuntu-latest
success	Test Python 3.12 on windows-latest
success	Test Python 3.13 on windows-latest
success	Test Python 3.12 on macos-latest
success	Test Python 3.13 on macos-latest
```

**The two lanes that failed twice now pass.** Step-level detail for the lane that carried the
defect:

```
$ gh run view 32557477023 --json jobs --jq '.jobs[] | select(.name=="Test Python 3.12 on windows-latest")'
name:        Test Python 3.12 on windows-latest
conclusion:  success
startedAt:   2026-08-22T06:38:07Z
completedAt: 2026-08-22T06:44:38Z
steps:       Set up job / Run actions/checkout@v7 / Install uv / Set up Python 3.12 /
             Install dependencies / Run tests with tox / Upload test results /
             Post Install uv / Post Run actions/checkout@v7 / Complete job
             — every step conclusion: success
```

`Run tests with tox` is the step that failed in runs 1 and 2 at
`tests/test_templates_path_collision_gate.py`'s separator assertion. It passes here.

## D-13 ordering constraint — still satisfied

Every CI job begins with `uv sync --extra dev --locked` (10 steps across four workflows), so
`uv.lock` must be a strict ancestor of the dispatched SHA or zero tests run. Proven by measurement,
not by wave position:

```
$ git log -1 --format=%H -- uv.lock
237fc0a0779538d9f6c0789d197e1300a2e0fe8f   (feat(57-01): bump version to 0.9.0 across manifest, README and lockfile)

$ git merge-base --is-ancestor 237fc0a0 fbbf48cd && echo yes
yes
```

`57-11` touched no dependency, so the lockfile from `57-01` remains correct for this tree — and
all 12 jobs completing (rather than dying at `uv sync --locked`, which is how the two live
dependabot PRs fail) is independent confirmation.

## What this discharges — and what it does not

**Discharges.** `57-05`'s SC#3 toolchain half: the all-jobs-green authority criterion, on a
post-bump tree, dispatched after the lockfile commit. `57-05`'s other two SC#3 items (the
built-wheel content check and the lockfile-precedes-dispatch ordering) were already discharged by
run 2 and are unaffected. With this, `57-05` moves from `halted` to `complete`.

**Does not discharge.** Nothing in `57-08` (SC#4's milestone-diff sweep and fence) or `57-09`
(SC#5's todo-ledger disposition and the handoff checklist). Those remain open plans. This run also
takes no irreversible action: no tag was created or pushed, and `git tag -l v0.9.0` plus
`git ls-remote --tags origin v0.9.0` both remain empty.

**Note for `57-08`.** The dispatched tree contains `57-11`'s `typsphinx/builder.py` change. That is
the one owner-approved exception to the prep-only fence, recorded as an `AMENDED 2026-08-17` block
in `57-CONTEXT.md`. SC#4 must be read as *no **unintended** `typsphinx/` change* — read the amended
block before evaluating the fence, or this run's own tree will be reported as a false violation.

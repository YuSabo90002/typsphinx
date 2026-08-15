# Phase 52 — CI Evidence

**Provisioning note:** all commands below were run inside this plan's isolated git worktree,
after `unset VIRTUAL_ENV; unset UV_PROJECT_ENVIRONMENT; uv sync --extra dev`, per this project's
`CLAUDE.md` § "Worktree-isolated execution".

**Status: Task 1 not accepted as SC#3's authority run. The dispatched run reports `failure`, not
`success`, for eight of twelve jobs — a real, reproducible result, not a transcription error.**
This file records that run honestly rather than papering over it, per this plan's own instruction:
"If any job fails, do not paper over it: report the failure with its log excerpt and stop." A
retry requires a fix commit, and every candidate fix touches `tests/` files that sit outside this
plan's declared `files_modified` scope (`52-CI-EVIDENCE.md` only) — the wave-parallel constraint
under which this plan is running alongside sibling plans 52-05 and 52-06 in separate worktrees.
This is therefore reported as a blocker requiring an explicit decision (see "Escalation" below)
rather than silently retried or silently accepted as green.

---

## The authority run (attempted)

### Pre-push confirmation

Command:
```
$ grep '^version = ' pyproject.toml
```
Verbatim output:
```
version = "0.8.0"
```

Command:
```
$ grep -c '^## \[0\.8\.0\]' CHANGELOG.md
```
Verbatim output:
```
1
```

Command:
```
$ grep -c 'def test_three_masters_each_carry_their_full_include_set_in_pdf' tests/test_state_guard_shapes_gate.py
```
Verbatim output:
```
1
```

All three present — plans 52-01, 52-02 and 52-03 had merged back before this task ran.

### Re-measured branch position

Command:
```
$ git rev-list --count origin/gsd/v0.8.0-multi-master-composition..HEAD
```
Verbatim output:
```
178
```
Neither `52-CONTEXT.md`'s 155 nor `52-RESEARCH.md`'s 157 nor the planner's 159 — all three were
stale by construction, exactly as this plan's `must_haves.truths` predicted. `178` is this
execution's own live measurement.

Command:
```
$ git merge-base --is-ancestor origin/gsd/v0.8.0-multi-master-composition HEAD && echo fast-forward-ok
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
aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e
```

### Push

Command:
```
$ git push origin aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e:refs/heads/gsd/v0.8.0-multi-master-composition
```
Verbatim output:
```
To https://github.com/YuSabo90002/typsphinx.git
   1959088d..aaeec804  aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e -> gsd/v0.8.0-multi-master-composition
```
A plain fast-forward from the measured remote tip `1959088dff97be03f09413b8db69f9a62af13d2d`; not
rejected, so no force-push was needed or used.

Confirmation:
```
$ git rev-parse HEAD
aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e
$ git ls-remote origin refs/heads/gsd/v0.8.0-multi-master-composition
aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e	refs/heads/gsd/v0.8.0-multi-master-composition
```
Equal — the pushed SHA is confirmed on `origin`.

### Dispatch

Command:
```
$ gh workflow run ci.yml --ref gsd/v0.8.0-multi-master-composition
```
Verbatim output:
```
https://github.com/YuSabo90002/typsphinx/actions/runs/31855486993
```

Matched by `headSha` via:
```
$ gh run list --workflow=ci.yml --branch gsd/v0.8.0-multi-master-composition --limit 5 --json databaseId,headSha,event,status
```
First row: `{"databaseId":31855486993,"headSha":"aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e","event":"workflow_dispatch","status":"queued"}` —
`headSha` equals the pushed SHA.

Run id: `31855486993`
Run URL: `https://github.com/YuSabo90002/typsphinx/actions/runs/31855486993`

Overall run conclusion, confirmed after `gh run watch`:
```
$ gh run view 31855486993 --json conclusion,status
{"conclusion":"failure","status":"completed"}
```

### Job conclusions

Command:
```
$ gh run view 31855486993 --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv' | sort
```

| Job | Conclusion |
|---|---|
| Build Package | success |
| Code Coverage | **failure** |
| Integration Test - advanced | success |
| Integration Test - basic | success |
| Lint and Format Check | **failure** |
| Test Python 3.12 on macos-latest | **failure** |
| Test Python 3.12 on ubuntu-latest | **failure** |
| Test Python 3.12 on windows-latest | **failure** |
| Test Python 3.13 on macos-latest | **failure** |
| Test Python 3.13 on ubuntu-latest | **failure** |
| Test Python 3.13 on windows-latest | **failure** |
| Type Check | success |

Four of twelve jobs succeed (`Build Package`, `Integration Test - basic`, `Integration Test -
advanced`, `Type Check`). Eight fail: all six OS/Python test-matrix lanes, `Lint and Format
Check`, and `Code Coverage`. `[.jobs[].conclusion]|unique` is `["failure","success"]`, not the
required `["success"]`.

### Root cause: three independent, real, reproducible defects — not flakiness, not a transcription error

Each was confirmed by reading the actual job log (`gh run view --job <id> --log-failed`), and each
reproduces identically across every affected lane (verified by comparing all six test-matrix job
logs individually).

**1. `ruff` lint violation — `Lint and Format Check` (ubuntu-latest only, one job)**

```
I001 [*] Import block is un-sorted or un-formatted
   --> tests/test_builder.py:569:5
    |
567 |       would break unrelated path work inside the same call.
568 |       """
569 | /     import typsphinx.builder as builder_module
570 | |     from docutils.parsers.rst import states
571 | |     from docutils.utils import Reporter
572 | |
573 | |     from typsphinx.builder import TypstBuilder
    | |______________________________________________^
574 |
575 |       app = temp_sphinx_app
    |
help: Organize imports

Found 1 error.
[*] 1 fixable with the `--fix` option.
```
`black --check .` passed cleanly ("302 files would be left unchanged") immediately before this;
only `ruff check .` fails. This is exactly the class of defect D-08 assigns to CI as sole
authority: `.venv/bin/ruff` is a generic-linux ELF the NixOS stub loader rejects on this machine
(`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`), so this
import-ordering regression in `tests/test_builder.py` has never been checked locally on any prior
commit either — it surfaces for the first time on this dispatch, which is the first live `ruff`
run this milestone branch has had since Phase 47.

**2. Locale-dependent baseline-warning-string mismatch — all six test-matrix lanes plus `Code Coverage` (seven jobs, two parametrized test cases each)**

```
tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[state_guard_self_and_url_gate] FAILED
tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[state_guard_selfref_gate] FAILED
```
Excerpt (ubuntu-latest / py312):
```
E   AssertionError: state_guard_self_and_url_gate: baseline warning fragment
    'index.rst:4: WARNING: toctree で重複したエントリが見つかりました: child [toc.duplicate_entry]'
    missing from captured warnings -- a diagnostic Sphinx used to emit may have been silently lost:
E     ...
E     /home/runner/.../index.rst:4: WARNING: duplicated entry found in toctree: child [toc.duplicate_entry]
```
The test's hardcoded baseline fragment is Japanese; Sphinx on the CI runner loads English
translations (`loading translations [en]... done`) and therefore emits the English wording of the
same diagnostic. This is a genuine environment-locale dependency in the test's baseline table, not
a lost diagnostic — the diagnostic fires (`toc.duplicate_entry` / `toc.not_readable` both appear,
just in English), but the assertion compares against a Japanese-only string. Reproduces identically
on all six OS/Python lanes and on `Code Coverage` (which also runs the full `pytest` suite via
`tox -e cov`), consistently `2 failed, 1168 passed, 5 skipped` (or `1167 passed` on the two Windows
lanes, which carry one additional failure — see below). This is exactly why the executor's local
run — 1170 passed, 5 skipped, exit 0, cited in this plan's `<upstream_state>` — did not catch it:
local execution runs under this development environment's own locale, which yields the Japanese
wording the baseline table hardcodes.

**3. Windows-only warning-message backslash-doubling — both Windows lanes only (in addition to defect 2)**

```
tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning FAILED
```
```
E   assert '\\typsphinx_test_50_03_escape_root\\chart.png' in
    "WARNING: could not rehome image URI '\\\\typsphinx_test_50_03_escape_root\\\\chart.png'
    relative to the doctree directory -- relocated to '_typst_converted/chart.png'"
tests/test_builder.py:555: AssertionError
```
The constructed warning message contains a doubled backslash sequence
(`\\typsphinx_test_50_03_escape_root\\chart.png`) where the test's own `abs_uri` variable has a
single backslash (`\typsphinx_test_50_03_escape_root\chart.png`) — a Windows-`pathlib`-only
string-formatting divergence, structurally invisible on this Linux development machine, of exactly
the same class this plan's `must_haves.truths` names: "a real cp1252 defect at the v0.7.0 close, a
real path-separator defect at the v0.7.1 close, and a real Windows-only OUT-02 defect in Phase 47."
Both `Test Python 3.12 on windows-latest` and `Test Python 3.13 on windows-latest` show `3 failed,
1167 passed, 5 skipped` — this defect plus the two locale-dependent failures above.

**Job-to-defect mapping**, confirmed by reading every failing job's log individually:

| Job | Defect 1 (ruff) | Defect 2 (locale) | Defect 3 (Windows backslash) |
|---|:---:|:---:|:---:|
| Lint and Format Check | X | | |
| Code Coverage | | X | |
| Test Python 3.12 on ubuntu-latest | | X | |
| Test Python 3.13 on ubuntu-latest | | X | |
| Test Python 3.12 on macos-latest | | X | |
| Test Python 3.13 on macos-latest | | X | |
| Test Python 3.12 on windows-latest | | X | X |
| Test Python 3.13 on windows-latest | | X | X |

No other failure signatures were observed in any job log.

### Escalation

All three defects are real, pre-existing on the tip that plans 52-01/52-02/52-03 produced —
none was introduced by this plan, which changes no source file (`git diff --name-only --
typsphinx/` and `git diff --name-only -- .github/` are both empty, confirmed below). Fixing any of
them requires editing `tests/test_builder.py` and/or `tests/test_state_guard_shapes_gate.py`,
which sit outside this plan's declared `files_modified` scope (`52-CI-EVIDENCE.md` only) — the
wave-parallel constraint this plan is running under, alongside sibling plans 52-05 and 52-06 in
independent worktrees. Per the executor's own SCOPE BOUNDARY rule ("Only auto-fix issues DIRECTLY
caused by the current task's changes... out-of-scope discoveries... log... do NOT fix them"), this
plan does not attempt a fix. All three defects are filed to the cross-phase defect register
(`.planning/WINDOWS.md`, entries 3–5, `kind: todo` / `kind: todo` / `kind: lint-warning`,
`phase: 52`) so they remain visible at ship time and block `/gsd-ship` until resolved or waived.

**This means Task 1's acceptance criterion — a live run reporting `success` for every job — is
NOT met by this dispatch.** SC#3's toolchain-half authority is not yet discharged. A follow-up
action is needed: either a plan authorized to touch `tests/` fixes all three defects and
re-dispatches (matching the Phase 46 `46-04` precedent, which required exactly this shape of
fix-commit-and-redispatch for a `ruff` `B904` violation), or the phase's scope is explicitly
widened to permit this plan to make the fix directly. That decision is not this plan's to make
unilaterally, given the wave-parallel file-scope constraint under which it is running.

### Why CI, not local, is the authority for this finding

Per D-08's split: local CI-equivalent tooling cannot serve as SC#3's authority for pytest, `black`,
`ruff`, or `mypy` on this machine — local never exercises Windows or macOS, and `.venv/bin/ruff` is
a generic-linux ELF the NixOS stub loader rejects, so `tox -e lint` cannot even run here (a filed,
out-of-scope environmental defect, not a validation gap). All three defects recorded above were
caught **only** because this plan dispatched a live run on the exact merged tip — exactly the
scenario D-08 exists to cover, and exactly why the executor's local 1170-passed/exit-0 result
(cited in this plan's `<upstream_state>`) could not have caught any of them. What this run does
not cover — the two docs builds (`tox -e docs-html`, `tox -e docs-pdf`) and the full-corpus
`-b typstpdf` GATE-02 gate — is recorded locally by plan 52-05, independent of this run's outcome.

---

## No irreversible action

Timestamp:
```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-15T01:12:56Z
```

Command and verbatim output:
```
$ git tag -l v0.8.0
(no output)
```
```
$ git ls-remote --tags origin v0.8.0
(no output)
```
```
$ gh pr list --head gsd/v0.8.0-multi-master-composition --json number,state
[]
```
```
$ gh run list --workflow=release.yml --limit 3 --json databaseId,createdAt,event
[{"createdAt":"2026-08-11T05:33:22Z","databaseId":31462027486,"event":"push"},
 {"createdAt":"2026-08-03T20:08:22Z","databaseId":30848860064,"event":"push"},
 {"createdAt":"2026-07-28T20:57:57Z","databaseId":30398631991,"event":"push"}]
```
All three listed `release.yml` runs predate this phase by days to weeks (2026-08-11, 2026-08-03,
2026-07-28 — the v0.7.1, v0.7.0, and v0.6.5 releases respectively); none was started by this
phase.

Four independent observations, all empty/absent as required: no `v0.8.0` tag locally, no `v0.8.0`
tag on `origin`, zero open pull requests against this branch, and no `release.yml` run newer than
the pre-existing v0.7.1 release run.

**Exactly two actions were taken by this plan** — a plain fast-forward branch push
(`git push origin aaeec804...:refs/heads/gsd/v0.8.0-multi-master-composition`) and a `ci.yml`
`workflow_dispatch` (`gh workflow run ci.yml --ref gsd/v0.8.0-multi-master-composition`). Both sit
on the reversible side of the prep/publish fence per D-08: pushing a branch and dispatching a
workflow are explicitly named in scope; opening a pull request, pushing a tag, and dispatching
`release.yml` are not, and none of those three occurred.

Command:
```
$ git diff --name-only -- .github/
(no output)
$ git diff --name-only -- typsphinx/
(no output)
```
`ci.yml` was exercised, never edited; no line under `typsphinx/` changed by this plan.

Any commit landing on the branch AFTER the SHA recorded above (`aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e`)
belongs to this phase's remaining evidence plans and touches only `.planning/`; plan 52-07 asserts
that mechanically.

---

## What this run does not cover

The dispatched matrix does NOT run the two docs builds (`tox -e docs-html`, `tox -e docs-pdf`) or
the full-corpus `-b typstpdf` GATE-02 gate — plan 52-05 (`52-GREEN-TREE-EVIDENCE.md`) owns that
local half of SC#3/SC#4, independent of this run's outcome; its results are not restated here.

Lint and type authority sits with a dispatched CI run rather than with local execution because
`ruff` cannot execute on this machine at all — a filed, still-open toolchain defect
(`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`), not a
validation gap. `tox.ini`'s `env_list` includes `lint`, so a bare `tox` invocation dies at that
environment (exit 127) before reaching any other environment; every environment must be run
individually instead (`tox -e docs-html`, `tox -e docs-pdf`, direct `pytest`), exactly as
Phase 46's `46-04-PLAN.md` Task 2 instructed.

---

## Broken-windows ledger entries filed

Three entries appended to `.planning/WINDOWS.md` (`phase: 52`), one per defect above:

| Ledger ID | Kind | File | Line | Description |
|---|---|---|---|---|
| 3 | todo | `tests/test_builder.py` | 555 | Windows-only backslash-doubling in warning message breaks `assert abs_uri in message` on CI |
| 4 | todo | `tests/test_state_guard_shapes_gate.py` | 781 | Locale-dependent baseline warning fragments (hardcoded Japanese) fail against English-locale CI runners |
| 5 | lint-warning | `tests/test_builder.py` | 569 | `ruff` I001 unsorted import block fails Lint and Format Check on CI |

All three are `status: open` as of this plan's execution and will block `/gsd-ship` until
resolved or explicitly waived.

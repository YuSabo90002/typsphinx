# Phase 46 — CI Evidence (D-23)

**Provisioning note:** all commands below were run inside this plan's isolated git worktree,
after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, per this project's
`CLAUDE.md` § "Worktree-isolated execution". Every Python/pytest command was invoked through
`uv run` where applicable.

---

## D-23 run 1 — the Windows check run

### The merge (D-20)

Command:
```
$ git merge --no-ff origin/main
```
Verbatim output:
```
Auto-merging CHANGELOG.md
CONFLICT (content): Merge conflict in CHANGELOG.md
Auto-merging tests/test_builder.py
Auto-merging typsphinx/builder.py
Automatic merge failed; fix conflicts and then commit the result.
```
Exactly one conflict, `CHANGELOG.md` — matching the read-only `git merge-tree --write-tree HEAD
origin/main` dry run measured twice in `46-RESEARCH.md`/`46-CONTEXT.md` and re-verified live in
this plan immediately before running the real merge. `typsphinx/builder.py` and
`tests/test_builder.py` auto-merged clean, as predicted.

### The conflict resolution (by hand, no `-X ours`/`-X theirs`)

The single `## [Unreleased]` block's body was resolved to keep **both** sides, in this order:

1. `origin/main`'s `### Fixed` bullet, verbatim, all 13 body lines intact — the Issue #130
   absolute-image-URI fix (PR #131).
2. The local side's `### Planned for Future Releases` list, verbatim, all five items intact —
   BibTeX/bibliography support, Glossary generation, Index generation, Pre-commit hooks,
   Additional Typst Universe template integration.

No `## [0.7.1]` heading was created (that is plan 46-03's job) and the tail link block was not
touched.

### Pushed SHA

Command:
```
$ git rev-parse HEAD
```
Verbatim output (after the merge + D-22 repair commit `c72be91`):
```
c72be911ec5201a1375bd91fba80f00821396fa9
```

### Push

Command:
```
$ git push origin HEAD:refs/heads/gsd/v0.7.1-bug-fix-round
```
Verbatim output:
```
To https://github.com/YuSabo90002/typsphinx.git
   af91b7c..c72be91  HEAD -> gsd/v0.7.1-bug-fix-round
```
A plain fast-forward; not rejected, so no force-push was needed or used.

### Dispatch

Command:
```
$ gh workflow run ci.yml --ref gsd/v0.7.1-bug-fix-round
```
Verbatim output:
```
https://github.com/YuSabo90002/typsphinx/actions/runs/31456466358
```
Run id: `31456466358`.

### Job conclusions (first dispatch, commit `c72be91`)

| Job | Conclusion |
|---|---|
| Type Check | success |
| Code Coverage | success |
| Integration Test - basic | success |
| **Lint and Format Check** | **failure** |
| Build Package | success |
| Test Python 3.13 on windows-latest | success |
| Integration Test - advanced | success |
| Test Python 3.13 on macos-latest | success |
| Test Python 3.12 on macos-latest | success |
| Test Python 3.12 on ubuntu-latest | success |
| **Test Python 3.12 on windows-latest** | **success** |
| Test Python 3.13 on ubuntu-latest | success |

Both target `windows-latest` lanes were already `success` on this first dispatch — D-22's repair
worked. But `Lint and Format Check` reported `failure`, a job that was `success` on the baseline
run (below), so this dispatch was not accepted as clean evidence. See "Deviation: a second push
and dispatch were required" below for the root cause and the fix.

### Baseline

Run `31445582363` (`conclusion: failure`). Its only failing jobs, read from the same
`gh run view --json jobs` shape:

| Job | Conclusion |
|---|---|
| Lint and Format Check | success |
| Integration Test - advanced | success |
| Integration Test - basic | success |
| Code Coverage | success |
| Build Package | success |
| Test Python 3.13 on ubuntu-latest | success |
| Test Python 3.12 on macos-latest | success |
| **Test Python 3.12 on windows-latest** | **failure** |
| Type Check | success |
| Test Python 3.13 on macos-latest | success |
| **Test Python 3.13 on windows-latest** | **failure** |
| Test Python 3.12 on ubuntu-latest | success |

The delta this plan set out to demonstrate is exactly those two `windows-latest` lanes flipping
from `failure` to `success`.

### Deviation: a second push and dispatch were required

The first dispatch (commit `c72be91`, run `31456466358`) surfaced a **new** job failure —
`Lint and Format Check` — that was not present in the baseline run. Investigating the job log
(`gh run view --job <id> --log`) found three `ruff` `B904` violations in
`tests/test_toolchain_config_gate.py` (lines 111, 331, 419): `raise AssertionError(...)` inside an
`except Exception as e:` block with no `from e`/`from None` clause. This file was added by
**Phase 45.2** (commit `1badedc`), after the baseline run (`31445582363`) was dispatched — so this
was this file's first-ever pass through the `Lint and Format Check` job on this branch, and the
defect was real and pre-existing, not introduced by this plan's merge or D-22 repair.

Ruff itself cannot run locally in this worktree (`.venv/bin/ruff` is a generic-linux ELF the NixOS
stub loader rejects — the same known environmental defect
`46-VALIDATION.md` "Known Environmental Defects" names and
`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` files), so this
could only be discovered via a live CI run — exactly the class of defect D-11 assigns to CI as
authority, and exactly why this task's own action text states "a regression anywhere else is
equally disqualifying at this point."

Fixed by adding `from e` to all three `raise AssertionError(...)` statements — test-only, zero
behavior change, no `typsphinx/` file touched. Verified locally: `uv run black --check
tests/test_toolchain_config_gate.py` (unchanged) and `uv run pytest
tests/test_toolchain_config_gate.py -q` (4 passed). Committed separately
(`fix(46-01): chain exception cause in test_toolchain_config_gate.py (ruff B904)`, commit
`07b9afd`), pushed, and re-dispatched.

### Second push

Command:
```
$ git push origin HEAD:refs/heads/gsd/v0.7.1-bug-fix-round
```
Verbatim output:
```
To https://github.com/YuSabo90002/typsphinx.git
   c72be91..07b9afd  HEAD -> gsd/v0.7.1-bug-fix-round
```

Pushed SHA:
```
$ git rev-parse HEAD
07b9afdc09afa6134f0b11d1d3f0c0850f7b2af4
```

### Second dispatch

Command:
```
$ gh workflow run ci.yml --ref gsd/v0.7.1-bug-fix-round
```
Verbatim output:
```
https://github.com/YuSabo90002/typsphinx/actions/runs/31456868265
```
Run id: `31456868265`.

### Job conclusions (second dispatch, commit `07b9afd` — the accepted evidence)

| Job | Conclusion |
|---|---|
| Type Check | success |
| Lint and Format Check | success |
| Code Coverage | success |
| Integration Test - advanced | success |
| Test Python 3.12 on ubuntu-latest | success |
| Integration Test - basic | success |
| Test Python 3.13 on ubuntu-latest | success |
| **Test Python 3.13 on windows-latest** | **success** |
| **Test Python 3.12 on windows-latest** | **success** |
| Test Python 3.13 on macos-latest | success |
| Test Python 3.12 on macos-latest | success |
| Build Package | success |

Overall run conclusion (`gh run view 31456868265 --json conclusion,status`):
```
{"conclusion":"success","status":"completed"}
```

**All twelve jobs report `success`. No job reports `failure`.** Both `windows-latest` lanes —
`Test Python 3.12 on windows-latest` and `Test Python 3.13 on windows-latest` — are `success`,
against a baseline in which those two were the only failures. `RUN_ID=31456868265` is this task's
accepted D-23 run 1 evidence.

### What this run does not prove

Per `46-VALIDATION.md` M1, the local 8/8-green run of `tests/test_docs_contract_claims_gate.py`
(`uv run pytest tests/test_docs_contract_claims_gate.py -v` → `8 passed`) proves only
**non-regression on POSIX** — backslash path rendering is Windows `pathlib` behaviour and is not
reproducible on this Linux machine, so it cannot demonstrate the repair actually works on
Windows. **This CI run, not the local run, is D-22's acceptance evidence** — it is the first real
exercise of `_discovered_claim_pages()`'s `.as_posix()` normalisation against a genuine
`windows-latest` runner.

This run also does not close REL-04 or represent SC#3's authority run — see "D-23 run 2" below —
and it takes no irreversible action (`git tag -l v0.7.1` is empty throughout; verified again at
task close).

### Observation carried forward

`scripts/extract_changelog_section.py`'s module docstring (lines 24, 32) states that
`CHANGELOG.md` carries **two** `## [Unreleased]` headings. A direct count on the merged file
(`grep -c '^## \[Unreleased\]' CHANGELOG.md`) returns **one** — the tail block's `[Unreleased]:`
line is a markdown link definition, not a heading, and `### Planned for Future Releases` is a
subsection under the one heading, not a second heading of its own.

The script was deliberately **not** edited: this phase permits only two non-planning code edits
(D-22's repair and, in a later plan, the `RELEASE_VERSIONS` append), and correcting a stale
docstring is not one of them. The observation is carried into `46-HANDOFF.md` §
"Not done in this phase, by design". The script's algorithm is purely positional (it finds the
first `## [<version>]` heading matching the requested version and reads to the next `## [...]`
heading or EOF) and is therefore correct either way — only its docstring's headcount claim is
stale.

---

## D-23 run 2 — the authority run

_Pending — filled by plan 46-04._

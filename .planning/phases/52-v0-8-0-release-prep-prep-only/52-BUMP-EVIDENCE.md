# Phase 52 Plan 01 — Bump Evidence

**Provisioning note:** all commands below were run inside this plan's isolated git worktree, after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` (this project's `CLAUDE.md`
§ "Worktree-isolated execution" makes this MANDATORY, not conditional — without it, pytest imports
the unchanged main-tree package instead of this worktree's edited copy). Every Python/test command
below was invoked through `uv run`, per the same section's mandatory convention.

## SC#1 — version-literal lockstep

### Before/after values of the three surfaces

| Surface | Before | After |
|---|---|---|
| `pyproject.toml` line 7 | `version = "0.7.1"` | `version = "0.8.0"` |
| `README.md` line 347 | `**Status**: Stable (v0.7.1) - Production ready` | `**Status**: Stable (v0.8.0) - Production ready` |
| `uv.lock`'s `typsphinx` entry | `name = "typsphinx"` / `version = "0.7.1"` / `source = { editable = "." }` | `name = "typsphinx"` / `version = "0.8.0"` / `source = { editable = "." }` |

Before-values verified with `git show HEAD~1:<path>`, after-values verified against the working
tree following the version-bump commit `1f47b659`.

### `uv lock` transcript

```
$ uv lock
Resolved 89 packages in 0.58ms
Updated typsphinx v0.7.1 -> v0.8.0
```

### `uv sync --extra dev --locked` transcript

```
$ uv sync --extra dev --locked
Resolved 89 packages in 0.63ms
   Building typsphinx @ file:///.../agent-a2a6b9831fea751af
      Built typsphinx @ file:///.../agent-a2a6b9831fea751af
Prepared 1 package in 379ms
Uninstalled 1 package in 0.23ms
Installed 1 package in 0.55ms
 - typsphinx==0.7.1 (from file:///.../agent-a2a6b9831fea751af)
 + typsphinx==0.8.0 (from file:///.../agent-a2a6b9831fea751af)
```

This is the load-bearing step: `typsphinx.__version__` derives from `importlib.metadata`, not the
literal — editing `pyproject.toml` alone does not move it; only regenerating the editable-install
`.dist-info`/`.pth` metadata does, which this command did (uninstall 0.7.1, install 0.8.0).

### `uv lock --check` transcript

```
$ uv lock --check
Resolved 89 packages in 0.54ms
```

Exit code: `0`.

### `python -c "import typsphinx"` read-back

```
$ uv run python -c "import typsphinx; print(typsphinx.__version__)"
0.8.0
```

### Acceptance-criteria greps (all run against the post-bump tree)

```
$ grep -c '^version = "0.8.0"$' pyproject.toml
1

$ grep -c '^version = "0.7.1"$' pyproject.toml
0

$ grep -c 'Stable (v0.8.0) - Production ready' README.md
1

$ grep -A2 'name = "typsphinx"' uv.lock
name = "typsphinx"
version = "0.8.0"
source = { editable = "." }

$ git diff --name-only   # (run pre-commit)
README.md
pyproject.toml
uv.lock
```

After committing (`1f47b659`), the working tree is clean of those three paths; this evidence file
and `COVERAGE.md` are the only new paths added afterward, matching the plan's file-scope fence.

### `[project] dependencies` byte-identity check

```
$ git show HEAD:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p' > /tmp/.../deps_head.txt
$ sed -n '/^dependencies = \[/,/^\]/p' pyproject.toml > /tmp/.../deps_now.txt
$ diff /tmp/.../deps_head.txt /tmp/.../deps_now.txt
$ echo $?
0
```

No output, exit 0 — the two blocks are byte-identical. This phase added and removed no dependency.

## Release-machinery consumer path

```
$ uv run python scripts/extract_changelog_section.py 0.7.1
[... full ## [0.7.1] body, non-empty, matching CHANGELOG.md ...]
$ echo $?
0

$ uv run python scripts/extract_changelog_section.py 9.9.9
No '## [9.9.9]' section found in the CHANGELOG. Add a curated entry for this version before releasing.
$ echo $?
1
```

This proves the reader `release.yml`'s `validate` and `create-release` jobs both call is live on
this tree — it finds a real, already-published section and rejects a missing one — **before** plan
52-02 authors the `## [0.8.0]` section it will read next.

## Guard tests

### `tests/test_extension.py::test_version_matches_pyproject_toml`

```
$ uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /.../agent-a2a6b9831fea751af/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2a6b9831fea751af
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_extension.py::test_version_matches_pyproject_toml PASSED      [100%]

============================== 1 passed in 0.02s ===============================
```

### `tests/test_readme_version_sync.py`

```
$ uv run pytest tests/test_readme_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /.../agent-a2a6b9831fea751af/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2a6b9831fea751af
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [100%]

============================== 1 passed in 0.02s ===============================
```

### `tests/test_preview_version_sync.py`

```
$ uv run pytest tests/test_preview_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /.../agent-a2a6b9831fea751af/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2a6b9831fea751af
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 3 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

============================== 3 passed in 0.02s ===============================
```

### Combined battery (JUnit-XML)

```
$ uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml \
    tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q \
    --junit-xml=<scratchpad>/52-01-guards.xml
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2a6b9831fea751af
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items

tests/test_extension.py .                                                [ 20%]
tests/test_readme_version_sync.py .                                      [ 40%]
tests/test_preview_version_sync.py ...                                   [100%]

- generated xml file: <scratchpad>/52-01-guards.xml -
============================== 5 passed in 0.04s ===============================
```

JUnit `testsuite` element: `tests="5"`, `skipped="0"`, `failures="0"`, `errors="0"`. 5 tests
(1 version-match + 1 readme-sync + 3 preview-sync), zero skips, zero failures — matching this
plan's acceptance bar exactly.

## Phase-head anchor re-measurement

**Every figure below was RE-RUN live at execution time, in this worktree, before any edit was
made in Task 1.** The figures carried in `52-CONTEXT.md` (155 commits ahead) and `52-RESEARCH.md`
(157 commits ahead) were deliberately NOT transcribed into this file — both were measured on
earlier trees and the count has moved again since those documents were written. The live
measurement below is **161**, and this discrepancy against the 155/157 planning-time figures is
expected staleness, not a measurement error: the plan's own `must_haves.truths` explicitly forbids
transcribing CONTEXT/RESEARCH figures and requires a fresh re-measurement, which is what follows.

```
$ git tag -l v0.8.0
(no output)

$ git ls-remote --tags origin v0.8.0
(no output)

$ git rev-parse v0.7.1^{commit}
48bf135428bb093a77a432d93d16088ce6930342
```

(On this annotated tag a bare `git rev-parse v0.7.1` returns the tag object sha, not the commit;
the `^{commit}` peel above is required and was used.)

```
$ git merge-base origin/main HEAD
a97fe736a4311cf04109cfafd1154a3e3b95d208

$ git merge-base --is-ancestor origin/main HEAD && echo ancestor
ancestor

$ git rev-list --count origin/gsd/v0.8.0-multi-master-composition..HEAD
161

$ git diff v0.7.1..HEAD --stat -- . ':(exclude).planning' | tail -1
 341 files changed, 15141 insertions(+), 2472 deletions(-)
```

**Commits-ahead figure: 161.** This is the live measurement taken during this plan's execution
(2026-08-15), superseding the stale 155 (`52-CONTEXT.md`) and 157 (`52-RESEARCH.md`) figures
carried from earlier planning sessions — both documents were measured against the tree as it stood
at their own respective write times, and six more commits landed on the branch (four planning
commits from this phase's own discuss/research/plan/pattern-map cycle, plus this plan's Task 1
bump commit and this evidence-writing pass) between the RESEARCH measurement and this one. Neither
`52-CONTEXT.md` nor `52-RESEARCH.md` was edited to correct this — that is out of this plan's scope.

`git merge-base --is-ancestor origin/main HEAD` returned `ancestor` (exit 0), confirming the
"nothing to merge in" premise this phase rests on still holds.

## SC#5 — fence observation at phase head

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-15T00:44:33Z

$ git tag -l v0.8.0
(no output)

$ git ls-remote --tags origin v0.8.0
(no output)
```

Both the local tag list and the remote tag query returned no output — no `v0.8.0` tag exists
locally or on `origin` at `2026-08-15T00:44:33Z`. This is an **extra** observation, taken both
before Task 1's edits (Step 1) and again here after Task 1's commit. The standing **two**
independent observations required by SC#5 are carried by `52-RELEASE-EVIDENCE.md` and
`52-HANDOFF.md` (plan 52-07) — this file's observation is a third, additional data point, not a
substitute for either of those two.

## Invariant spot-check

`tests/test_preview_version_sync.py` passed all three of its assertions (see "Guard tests" above):
the three declaration sites (`typsphinx/writer.py`, `typsphinx/template_engine.py`,
`typsphinx/templates/base.typ`) still agree on all four `@preview` package versions (`codly`,
`codly-languages`, `mitex`, `gentle-clues`), all four are still declared at every site, and no
bundled `examples/` template pins a stale version relative to `base.typ`.

This plan's own diff touched only `pyproject.toml`, `README.md`, and `uv.lock` — no template,
writer, or import code changed, so by construction the four bundled `@preview` package versions
and their sync surfaces are untouched. The **full mechanical sweep** over the milestone's entire
diff (verifying nothing *else* in the milestone silently drifted a `@preview` version) is owned by
**plan 52-06**, which this section cites rather than duplicates — this plan's own spot-check is
scoped to "did I personally touch a lockstep site," not to the whole milestone's invariant sweep.

## Executed versus skipped

**A bare `tox` was not run.** `tox.ini`'s `env_list` includes `lint`, which exits 127 on this
machine — `ruff` ships as a generic-linux ELF that the NixOS stub loader rejects
(`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`). Running a
bare `tox` would only reproduce this known, unfixable-in-this-plan environmental failure.

**`tox -e py312` was not run.** `uv venv -p cpython3.12` attempts to download a standalone CPython
whose ELF the same NixOS stub loader rejects, so that environment cannot even provision — not a
case of tests failing, but of the environment itself failing to come up.

**Authority for the full lint/type/py312/py313/docs matrix belongs to CI (D-08), not this plan.**
This plan's own local scope is exactly the five version-sync guard assertions above, run and
recorded honestly through direct `uv run pytest` invocations — nothing was inferred or asserted
from memory. The dispatched CI run collected by plan 52-04 owns lint, type, and the full py312/
py313/docs matrix.

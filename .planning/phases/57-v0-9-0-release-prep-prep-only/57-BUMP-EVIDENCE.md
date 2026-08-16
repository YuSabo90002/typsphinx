# Phase 57 Plan 01 — Bump Evidence

**Provisioning note:** all commands below were run inside this plan's isolated git worktree, after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` (this project's `CLAUDE.md`
§ "Worktree-isolated execution" makes this MANDATORY, not conditional — without it, pytest imports
the unchanged main-tree package instead of this worktree's edited copy). Every Python/test command
below was invoked through `uv run`, per the same section's mandatory convention.

## SC#1 — version-literal lockstep

### Before/after values of the three surfaces

| Surface | Before | After |
|---|---|---|
| `pyproject.toml` line 7 | `version = "0.8.0"` | `version = "0.9.0"` |
| `README.md` line 347 | `**Status**: Stable (v0.8.0) - Production ready` | `**Status**: Stable (v0.9.0) - Production ready` |
| `uv.lock`'s `typsphinx` entry | `name = "typsphinx"` / `version = "0.8.0"` / `source = { editable = "." }` | `name = "typsphinx"` / `version = "0.9.0"` / `source = { editable = "." }` |

Before-values verified with `git show HEAD~1:<path>` against the pre-bump tree (phase-start SHA
`78bd595d344f46c6e1f5a18bce0e24da1f66a9ee`); after-values verified against the working tree
following the version-bump commit `237fc0a0`.

### `uv lock` transcript

```
$ uv lock
Resolved 89 packages in 477ms
Updated typsphinx v0.8.0 -> v0.9.0
```

### `uv sync --extra dev --locked` transcript

```
$ uv sync --extra dev --locked
Resolved 89 packages in 0.63ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa884129710c018db
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa884129710c018db
Prepared 1 package in 401ms
Uninstalled 1 package in 0.25ms
Installed 1 package in 0.55ms
 - typsphinx==0.8.0 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa884129710c018db)
 + typsphinx==0.9.0 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa884129710c018db)
```

This is the load-bearing step: `typsphinx.__version__` derives from `importlib.metadata`, not the
literal — editing `pyproject.toml` alone does not move it; only regenerating the editable-install
`.dist-info`/`.pth` metadata does, which this command did (uninstall 0.8.0, install 0.9.0).

### `uv lock --check` transcript

```
$ uv lock --check
Resolved 89 packages in 0.61ms
```

Exit code: `0`.

### `python -c "import typsphinx"` read-back

```
$ uv run python -c "import typsphinx; print(typsphinx.__version__)"
0.9.0
```

### Acceptance-criteria greps (all run against the post-bump tree)

```
$ grep -c '^version = "0.9.0"$' pyproject.toml
1

$ grep -c '^version = "0.8.0"$' pyproject.toml
0

$ grep -c 'Stable (v0.9.0) - Production ready' README.md
1

$ grep -c 'requires-python = ">=3.12"' pyproject.toml
1

$ grep -c 'sphinx>=9.1,<10' pyproject.toml
1

$ grep -A2 'name = "typsphinx"' uv.lock
name = "typsphinx"
version = "0.9.0"
source = { editable = "." }

$ git diff --name-only   # (run pre-commit)
README.md
pyproject.toml
uv.lock
```

After committing (`237fc0a0`), the working tree is clean of those three paths; this evidence file,
`57-CLOSEOUT-GUARD.md` and `COVERAGE.md` are the only new paths added afterward, matching the
plan's file-scope fence.

### `[project] dependencies` byte-identity check

```
$ git show HEAD:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p' > deps-before.txt
$ sed -n '/^dependencies = \[/,/^\]/p' pyproject.toml > deps-after.txt
$ diff deps-before.txt deps-after.txt
$ echo $?
0
```

No output, exit 0 — the two blocks are byte-identical. This phase added and removed no dependency.
`uv lock`'s own transcript above shows only the first-party `typsphinx` entry moved; no third-party
package was added or dropped.

## D-13 sequencing precondition

The regenerated `uv.lock` was committed in this plan's Task 1 (`237fc0a0`) **before** either
dispatched CI run — plan 57-02's pre-bump check and plan 57-05's post-bump authority run. Ten
`uv sync --extra dev --locked` steps across four workflow files depend on this lockfile agreeing
with the manifest; `uv lock --check` exiting `0` above is the evidence that they do. A stale
lockfile fails at install, before any test, lint or type signal exists — exactly how dependabot PRs
#128 and #123 are dying right now.

The step count was measured directly rather than transcribed from `57-CONTEXT.md` (which states
eleven):

```
$ grep -c locked .github/workflows/ci.yml .github/workflows/release.yml .github/workflows/docs.yml .github/workflows/drift.yml
.github/workflows/ci.yml:6
.github/workflows/release.yml:2
.github/workflows/docs.yml:1
.github/workflows/drift.yml:1
```

Measured total: **10** (6 + 2 + 1 + 1), not eleven. The hard sequencing constraint itself is
unaffected by the count correction.

## Release-machinery consumer path

```
$ uv run python scripts/extract_changelog_section.py 0.8.0
[... full ## [0.8.0] body, non-empty, matching CHANGELOG.md — 70 lines to stdout ...]
$ echo $?
0

$ uv run python scripts/extract_changelog_section.py 9.9.9
No '## [9.9.9]' section found in the CHANGELOG. Add a curated entry for this version before releasing.
$ echo $?
1
```

This proves the reader `release.yml`'s `validate` and `create-release` jobs both call is live on
this tree — it finds a real, already-published section and rejects a missing one — **before** plan
57-03 authors the `## [0.9.0]` section it will read next.

## Guard tests

### `tests/test_extension.py::test_version_matches_pyproject_toml`

```
$ uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .../agent-aa884129710c018db/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa884129710c018db
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
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .../agent-aa884129710c018db/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa884129710c018db
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
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .../agent-aa884129710c018db/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa884129710c018db
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
    tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v \
    --junit-xml=<scratchpad>/57-01-guards.xml
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa884129710c018db
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 5 items

tests/test_extension.py::test_version_matches_pyproject_toml PASSED      [ 20%]
tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [ 40%]
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 60%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 80%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

- generated xml file: <scratchpad>/57-01-guards.xml -
============================== 5 passed in 0.05s ===============================
```

JUnit `testsuite` element (verbatim attributes): `tests="5"`, `errors="0"`, `failures="0"`,
`skipped="0"`. 5 tests (1 version-match + 1 readme-sync + 3 preview-sync), zero skips, zero
failures — matching this plan's acceptance bar exactly.

### `uv run ruff check .` transcript

```
$ uv run ruff check .
All checks passed!
$ echo $?
0

$ uv run ruff --version
ruff 0.15.20
```

This first attempt inside the fresh worktree venv hit the known NixOS ELF-exec hazard
(`.venv/bin/ruff` installed as a plain generic-linux ELF, `interpreter /lib64/ld-linux-x86-64.so.2`,
"Could not start dynamically linked executable"). It was resolved the same way prior worktree
executors have resolved it (Rule 3, blocking-issue auto-fix — not a package install, a local
execution-environment repair): symlinking the worktree's `.venv/bin/ruff` onto the main tree's own
copy, which carries an identical build (same SHA1 BuildID `ca2c631a338418e6129fa7e04e290477442b8489`)
already patched to a nix-store interpreter:

```
$ readlink -f .venv/bin/ruff   # before fix
.venv/bin/ruff                  # plain ELF, /lib64/ld-linux-x86-64.so.2
$ ln -sf /home/yuta/Documents/typsphinx/.venv/bin/ruff .venv/bin/ruff
$ readlink -f .venv/bin/ruff   # after fix
/home/yuta/Documents/typsphinx/.venv/bin/ruff   # resolves through to /nix/store/...glibc.../ld-linux-x86-64.so.2
```

After the shim, `uv run ruff check .` ran clean as shown above. This is an **additive local
pre-flight only** — it does not move lint authority off CI. D-13's independent grounds for CI
authority (the Windows and macOS lanes, which no local run reproduces — the exact lanes that caught
real cp1252 and path-separator defects at two previous release closes) are untouched by this local
result being green.

## Phase-head anchor re-measurement

**Every figure below was RE-RUN live at execution time, in this worktree, before any edit was made
in Task 1.** The commits-ahead figures carried in `57-CONTEXT.md` and `57-RESEARCH.md` (each
measured at its own earlier write time, and corrected again during plan-time re-measurement) were
deliberately NOT transcribed into this file — the count has moved again since those documents were
written, and the plan's own `must_haves.truths` forbids treating a prior document's figure as this
phase's own measurement. The live measurement below is **195** (against the milestone's own
origin-tracked branch) and **277** (against the `v0.8.0` tag), each produced by the command shown
beside it, not by transcription.

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-16T15:35:48Z

$ git tag -l v0.9.0
(no output)

$ git ls-remote --tags origin v0.9.0
(no output)

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-16T15:35:49Z

$ git rev-parse v0.8.0^{commit}
78e01e53641433a34c1bd8834b6252187fcae4ba

$ git merge-base origin/main HEAD
aed773c9807ab871468b1b2a7e1ec36b54e82907

$ git rev-parse origin/main
aed773c9807ab871468b1b2a7e1ec36b54e82907

$ git merge-base --is-ancestor origin/main HEAD && echo ancestor
ancestor

$ git rev-list --count origin/gsd/v0.9.0-per-document-templates..HEAD
195

$ git rev-list --count v0.8.0..HEAD
277

$ git diff v0.8.0..HEAD --stat -- . ':(exclude).planning' | tail -1
 163 files changed, 11262 insertions(+), 1615 deletions(-)

$ git rev-parse HEAD
78bd595d344f46c6e1f5a18bce0e24da1f66a9ee
```

**Phase-start SHA: `78bd595d344f46c6e1f5a18bce0e24da1f66a9ee`.** This is the tip this worktree was
built from, captured before any Task-1 edit landed. Plan 57-08's fence proof is scoped to
`<phase-start-SHA>..HEAD`, not to the whole milestone diff, because the milestone's own
`typsphinx/` diff (163 files, +11262/-1615, matching v0.8.0..HEAD identically excluding
`.planning/`) is deliberately large.

`git merge-base --is-ancestor origin/main HEAD` returned `ancestor` (exit 0, `origin/main` and
`v0.8.0`'s merge-base match exactly, both `aed773c9807ab871468b1b2a7e1ec36b54e82907`), confirming
the "nothing to merge in" premise this phase rests on still holds. These figures were re-measured
live at execution time as instructed by `must_haves.truths` — no figure above was copied from
`57-CONTEXT.md` or `57-RESEARCH.md`.

## SC#4 — fence observation 1 of 3

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-16T15:35:48Z

$ git tag -l v0.9.0
(no output)

$ git ls-remote --tags origin v0.9.0
(no output)
```

Both the local tag list and the remote tag query returned no output — no `v0.9.0` tag exists
locally or on `origin` at `2026-08-16T15:35:48Z`. This is fence observation **1 of 3**. The other
two are owned by `57-SC4-INVARIANTS.md` (plan 57-08) and `57-HANDOFF.md` (plan 57-09), which
re-observe the same fence later in the phase, each with its own timestamp.

## Executed versus skipped

**A bare `tox` was not run.** `tox.ini`'s `env_list` includes `lint`, which historically exits 127
on this machine when the venv's `ruff` is an un-patched generic-linux ELF
(`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`). This plan's
own `uv run ruff check .` was made to run directly (see "Guard tests" above), but a bare `tox`
additionally spins up the full `py312`/`py313`/`type`/`cov`/`docs` matrix, which is out of this
plan's local scope by design (D-13) — that matrix's authority belongs to the dispatched CI runs
collected by plans 57-02 and 57-05.

**`tox -e py312` was not run.** `uv venv -p cpython3.12` attempts to download a standalone CPython
whose ELF the same NixOS stub loader rejects, so that environment cannot even provision — not a
case of tests failing, but of the environment itself failing to come up.

**Authority for the full lint/type/py312/py313/docs matrix belongs to CI (D-13), not this plan.**
This plan's own local scope is exactly the five version-sync guard assertions above plus the
additive `ruff` pre-flight, run and recorded honestly through direct `uv run pytest`/`uv run ruff`
invocations — nothing was inferred or asserted from memory. The dispatched CI runs collected by
plans 57-02 and 57-05 own lint, type, and the full py312/py313/docs matrix, including the Windows
and macOS lanes no local run reproduces.

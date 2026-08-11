# Phase 46 Plan 02 — Bump Evidence

**Provisioning note:** all commands below were run inside this plan's isolated git worktree, after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, per this project's `CLAUDE.md`
§ "Worktree-isolated execution". Every Python/test command was invoked through `uv run`, per the
same section's mandatory convention.

## SC#1 — version-literal lockstep

### Before/after values of the three surfaces

| Surface | Before | After |
|---|---|---|
| `pyproject.toml` line 7 | `version = "0.7.0"` | `version = "0.7.1"` |
| `README.md` line 342 | `**Status**: Stable (v0.7.0) - Production ready` | `**Status**: Stable (v0.7.1) - Production ready` |
| `uv.lock`'s `typsphinx` entry | `name = "typsphinx"` / `version = "0.7.0"` / `source = { editable = "." }` | `name = "typsphinx"` / `version = "0.7.1"` / `source = { editable = "." }` |

Verified with `git show HEAD~1:<path>` against the working tree after the version-bump commit
landed; each command's output is quoted verbatim above.

### `uv lock` transcript

```
$ uv lock
Resolved 89 packages in 0.94ms
```

(First invocation, immediately after editing `pyproject.toml`, actually moved the lockfile's
`typsphinx` entry and printed `Updated typsphinx v0.7.0 -> v0.7.1`; the transcript above is a
second, idempotent re-run captured for this evidence file, confirming the lock is already
converged — no further update to report.)

### `uv sync --extra dev --locked` transcript

```
$ uv sync --extra dev --locked
Resolved 89 packages in 0.98ms
Checked 79 packages in 1ms
```

(First invocation actually performed the install-metadata regeneration:
`- typsphinx==0.7.0 (from file:///…/agent-a4584cfba59927750)` /
`+ typsphinx==0.7.1 (from file:///…/agent-a4584cfba59927750)`. The transcript above is a second,
idempotent re-run confirming nothing further needs installing.)

### `uv lock --check` transcript

```
$ uv lock --check
Resolved 89 packages in 0.90ms
```

Exit code: `0`.

### `python -c "import typsphinx"` read-back

```
$ uv run python -c "import typsphinx; print(typsphinx.__version__)"
0.7.1
```

### Acceptance-criteria greps (all run against the post-bump tree)

```
$ grep -c '^version = "0.7.1"$' pyproject.toml
1

$ grep -c 'Stable (v0.7.1) - Production ready' README.md
1

$ grep -A2 'name = "typsphinx"' uv.lock
name = "typsphinx"
version = "0.7.1"
source = { editable = "." }

$ git diff --name-only
README.md
pyproject.toml
uv.lock
```

(`git diff --name-only` was run immediately before the version-bump commit; after committing, the
working tree is clean of those three, and this evidence file is the only new path added afterward,
matching the plan's file-scope fence.)

### `[project] dependencies` byte-identity check

```
$ diff <(git show HEAD:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p') \
       <(sed -n '/^dependencies = \[/,/^\]/p' pyproject.toml)
```

No output — the two blocks are byte-identical. This phase added and removed no dependency.

## Guard tests

### `tests/test_extension.py::test_version_matches_pyproject_toml`

```
$ uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /…/agent-a4584cfba59927750/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4584cfba59927750
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_extension.py::test_version_matches_pyproject_toml PASSED      [100%]

============================== 1 passed in 0.05s ===============================
```

### `tests/test_readme_version_sync.py`

```
$ uv run pytest tests/test_readme_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /…/agent-a4584cfba59927750/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4584cfba59927750
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [100%]

============================== 1 passed in 0.04s ===============================
```

### `tests/test_preview_version_sync.py`

```
$ uv run pytest tests/test_preview_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /…/agent-a4584cfba59927750/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4584cfba59927750
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 3 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

============================== 3 passed in 0.04s ===============================
```

### Combined battery (JUnit-XML)

```
$ uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml \
    tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q \
    --junit-xml=<scratchpad>/46-02-guards.xml
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4584cfba59927750
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items

tests/test_extension.py .                                                [ 20%]
tests/test_readme_version_sync.py .                                      [ 40%]
tests/test_preview_version_sync.py ...                                   [100%]

- generated xml file: <scratchpad>/46-02-guards.xml -
============================== 5 passed in 0.08s ===============================
```

JUnit `testsuite` element: `tests="5"`, `skipped="0"`, `failures="0"`, `errors="0"`. 5 tests
(1 version-match + 1 readme-sync + 3 preview-sync), zero skips, zero failures.

## Invariant spot-check

`tests/test_preview_version_sync.py` passed all three of its assertions (see "Guard tests" above):
the three declaration sites (`typsphinx/writer.py`, `typsphinx/template_engine.py`,
`typsphinx/templates/base.typ`) still agree on all four `@preview` package versions
(`codly`, `codly-languages`, `mitex`, `gentle-clues`), all four are still declared at every site,
and no bundled `examples/` template pins a stale version relative to `base.typ`.

This plan's own diff touched only `pyproject.toml`, `README.md`, and `uv.lock` — no template,
writer, or import code changed, so by construction the four bundled `@preview` package versions
and their sync surfaces are untouched. The **full mechanical sweep** over the milestone's entire
`v0.7.0..HEAD` diff (verifying nothing *else* in the milestone silently drifted a `@preview`
version, per D-21) is owned by **plan 46-05**, which this section cites rather than duplicates —
this plan's own spot-check is scoped to "did I personally touch a lockstep site," not to the whole
milestone's invariant sweep.

## Executed versus skipped

**`tox -e py312` was not run**, by design, per `46-RESEARCH.md` Pitfall 1: on this machine
`uv venv -p cpython3.12` attempts to download a standalone CPython whose ELF the NixOS stub loader
rejects (`exit 127`), so that environment cannot even provision — it is not a case of the tests
failing, the environment itself cannot come up. Running it would only reproduce a known,
unfixable-in-this-plan environmental failure, not exercise this plan's change.

Because a broader local sanity spot-check was still useful, this plan used `uv run pytest`
directly (the five guard-module transcripts above) rather than routing through `tox` at all —
`tox -e py313` (which matches this machine's system interpreter) was available as an alternative
but was not needed once the direct `uv run pytest` guard battery was green.

**Authority for the full lint/type/py312/py313/docs matrix belongs to CI (D-11), not this plan.**
This plan's own local scope is exactly the five version-sync guard assertions above, run and
recorded honestly — nothing was inferred or asserted from memory.

**No irreversible action was taken.** `git tag -l v0.7.1` was run and produced no output:

```
$ git tag -l v0.7.1
```

(empty — no output)

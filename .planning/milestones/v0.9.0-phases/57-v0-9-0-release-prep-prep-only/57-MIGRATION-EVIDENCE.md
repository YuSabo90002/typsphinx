# Phase 57 — Migration Guide Evidence (D-06, D-07, D-08, D-10, D-11)

## D-08 — the "before" side is a real build

**Fixture choice and byte-identity check.** `tests/roots/test-basic/` was picked, per
`57-RESEARCH.md`'s Pattern 3 recommendation — a default `typst_documents` entry with no custom
template, which exercises the OLD default shared-template layout at the tag and the NEW per-key
bundle layout at HEAD. Confirmed the same source tree is being built on both sides:

```
$ git diff --stat v0.8.0..HEAD -- tests/roots/test-basic/
(no output)
```

**The second worktree.**

```
$ git worktree add --detach "$SCRATCH/typsphinx-v080-before" v0.8.0
Preparing worktree (detached HEAD 78e01e53)
HEAD is now at 78e01e53 Merge pull request #133: release v0.8.0 — multi-master composition
```

**The second worktree's own provisioning**, run from inside
`$SCRATCH/typsphinx-v080-before` — the executor's own provisioning does not reach into this
checkout:

```
$ unset VIRTUAL_ENV; unset UV_PROJECT_ENVIRONMENT; uv sync --extra dev
Using CPython 3.13.13 interpreter at: /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin/python3
Creating virtual environment at: .venv
Resolved 89 packages in 0.78ms
   Building typsphinx @ file:///tmp/.../scratchpad/typsphinx-v080-before
      Built typsphinx @ file:///tmp/.../scratchpad/typsphinx-v080-before
Prepared 1 package in 398ms
Installed 79 packages in 54ms
 ... (79 packages, including typsphinx==0.8.0 (from file:///tmp/.../typsphinx-v080-before)) ...
```

**Isolation transcript — the falsification test for Pitfall 4.** Run from inside the tag
checkout:

```
$ uv run python -c "import typsphinx; print(typsphinx.__version__, typsphinx.__file__)"
0.8.0 /tmp/claude-1000/-home-yuta-Documents-typsphinx/b8d29a27-ed57-466d-806c-1d077ba1666f/scratchpad/typsphinx-v080-before/typsphinx/__init__.py
```

The printed version is `0.8.0` — the prior release, not `0.9.0` — and the printed `__file__` path
is under the second worktree's own directory (`.../scratchpad/typsphinx-v080-before/typsphinx/`),
not under the executor's worktree
(`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7038f9990cd14de`). The provisioning
isolated correctly; the build below reflects the prior release's own code.

**The build command and its summary lines:**

```
$ LC_ALL=C uv run sphinx-build -b typst tests/roots/test-basic "$SCRATCH/57-before-build"
Running Sphinx v9.1.0
loading translations [en]... done
making output directory... done
building [mo]: targets for 0 po files that are out of date
writing output...
building [typst]: targets for 1 source files that are out of date
updating environment: [new config] 1 added, 0 changed, 0 removed
reading sources... [100%] index

looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... Template written to /tmp/.../scratchpad/57-before-build/_template.typ
done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: output.typ
build succeeded.
```

**The emitted file tree** (`find "$SCRATCH/57-before-build" -type f | sort`):

```
$SCRATCH/57-before-build/.doctrees/environment.pickle
$SCRATCH/57-before-build/.doctrees/index.doctree
$SCRATCH/57-before-build/_template.typ
$SCRATCH/57-before-build/index.typ
$SCRATCH/57-before-build/output.typ
```

**The emitted wrapper file's full text** (`output.typ`):

```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Test Document",
  authors: ("Test Author",),
  date: "",
  lang: "en",
)

#state("typsphinx:include-edges", ()).update(())
#include("index.typ")
```

**Cleanup:**

```
$ git worktree remove --force "$SCRATCH/typsphinx-v080-before"
$ git worktree list
/home/yuta/Documents/typsphinx                                           78bd595d [gsd/v0.9.0-per-document-templates]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7c8226c607f8f053 78bd595d [worktree-agent-a7c8226c607f8f053] locked
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9c8971dc6e4cb753 78bd595d [worktree-agent-a9c8971dc6e4cb753] locked
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa884129710c018db 237fc0a0 [worktree-agent-aa884129710c018db] locked
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7038f9990cd14de 78bd595d [worktree-agent-ae7038f9990cd14de] locked
```

No `typsphinx-v080-before` entry remains. The other four entries are sibling worktrees this same
wave's other executors already hold (this executor's own worktree included); none is the temporary
checkout this task created.

```
$ git branch --list | grep -i v080
(no output)
```

No branch was created for the temporary checkout.

## The "after" side, built at HEAD

Built from this executor's own worktree, provisioned per `CLAUDE.md`'s standing rule
(`unset VIRTUAL_ENV; unset UV_PROJECT_ENVIRONMENT; uv sync --extra dev`, then `uv run` for every
command) before any command in this plan ran.

**The build command and its summary lines:**

```
$ LC_ALL=C uv run sphinx-build -b typst tests/roots/test-basic "$SCRATCH/57-after-build"
Running Sphinx v9.1.0
loading translations [en]... done
making output directory... done
building [mo]: targets for 0 po files that are out of date
writing output...
building [typst]: targets for 1 source files that are out of date
updating environment: [new config] 1 added, 0 changed, 0 removed
reading sources... [100%] index

looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: output.typ
build succeeded.
```

**The emitted file tree** (`find "$SCRATCH/57-after-build" -type f | sort`):

```
$SCRATCH/57-after-build/.doctrees/environment.pickle
$SCRATCH/57-after-build/.doctrees/index.doctree
$SCRATCH/57-after-build/_template/typst/README.md
$SCRATCH/57-after-build/_template/typst/base.typ
$SCRATCH/57-after-build/index.typ
$SCRATCH/57-after-build/output.typ
```

**The emitted wrapper file's full text** (`output.typ`):

```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "/_template/typst/base.typ": project

#show: project.with(
  title: "Test Document",
  authors: ("Test Author",),
  date: "",
  lang: "en",
)

#state("typsphinx:include-edges", ()).update(())
#include("index.typ")
```

## Why a second worktree

Reusing the executor's own `.venv` would build the tag checkout's sources against the CURRENT
editable install — because `import typsphinx` resolves through a PEP-660 editable finder pointed at
whichever tree provisioned it, the tag checkout's own `typsphinx/` source would never actually run;
the currently-installed `typsphinx` package would run instead, against the tag checkout's fixture.
The "before" tree would then show the CURRENT per-key bundle layout, not the prior release's
single shared `_template.typ` — silently defeating D-08 and reporting a false "before" state. The
isolation transcript above (`typsphinx.__version__` printing `0.8.0`, `typsphinx.__file__` printing
a path under the second worktree's own directory) is the check that this did not happen: version
and path both confirm the second worktree's own provisioning was used, not the executor's.

**Step 3 — the two trees differ in the expected direction.** The before tree names a single shared
template file at the output root (`_template.typ`, imported as `#import "_template.typ": project`)
and the after tree names a path under an output-tree bundle directory
(`_template/typst/base.typ`, imported as `#import "/_template/typst/base.typ": project`). This is
the exact contrast D-08 requires; the wrong `.venv` was not used.

## D-10 — discovery grep, run live

**Truth source**, read from `pyproject.toml` and quoted verbatim:

```
$ grep -n 'requires-python\|"sphinx>=' pyproject.toml
10:requires-python = ">=3.12"
28:    "sphinx>=9.1,<10",
```

**A note on the plan's own `<verify>` exclusion regex.** The plan's automated `<verify>` block
filters with `grep -v '^\./\.planning/'` and `grep -v '^\./CHANGELOG\.md'`, anchored on a leading
`./`. On this machine's `grep`, `grep -rn ... .` does **not** prefix matched paths with `./` (paths
come back as `.planning/foo.md`, not `./.planning/foo.md`), so that anchor never matches and the
literal `<verify>` command as written reports every `.planning/`/`CHANGELOG.md` hit as if it were
outside the exclusion — a path-format mismatch, not a real defect in the swept content. Confirmed
directly:

```
$ grep -rn 'Python 3\.9\|Sphinx 5\.0' --include='*.rst' --include='*.md' --include='*.txt' . \
    | grep -v '^\./\.planning/' | grep -v '^\./CHANGELOG\.md' | wc -l
32
```

Every one of those 32 lines is inside `.planning/` or `CHANGELOG.md`'s own historical entries
(verified by inspection below). Re-run with the exclusion anchored to match this `grep`'s actual
output shape (`^\.planning/`, `^CHANGELOG\.md`, no leading `./`) — same search, same intent, correct
anchor:

```
$ grep -rn 'Python 3\.9\|Sphinx 5\.0' --include='*.rst' --include='*.md' --include='*.txt' . \
    | grep -v '^\.planning/' | grep -v '^CHANGELOG\.md'
(no output — exit 1)
```

**Second sweep — `Sphinx 6.x`/`7.x`/`8.x`-shaped statements**, same corrected exclusion:

```
$ grep -rEn 'Sphinx 6\.[0-9]|Sphinx 7\.[0-9]|Sphinx 8\.[0-9]' --include='*.rst' --include='*.md' --include='*.txt' . \
    | grep -v '^\.planning/' | grep -v '^CHANGELOG\.md'
(no output — exit 1)
```

**Third sweep — the dead `docs/configuration.rst`-class link**, same corrected exclusion:

```
$ grep -rn 'docs/configuration.rst' --include='*.rst' --include='*.md' . \
    | grep -v '^\.planning/' | grep -v '^CHANGELOG\.md'
(no output — exit 1)
```

**Fourth sweep — every `../../docs/` relative link from `examples/`**, checked for existence of its
target:

```
$ grep -rn '\.\./\.\./docs/' examples/
examples/advanced/README.md:270:See [Configuration Reference](../../docs/source/user_guide/configuration.rst) for complete documentation of all options.

$ test -f docs/source/user_guide/configuration.rst && echo TARGET_EXISTS
TARGET_EXISTS
```

**What was excluded and why.** `.planning/` is excluded because planning prose deliberately quotes
the stale strings under discussion (including this very plan file, which names `Python 3.9` and
`Sphinx 5.0` as the strings to search for). `CHANGELOG.md`'s own historical entries are excluded
because editing historical release notes is explicitly out of scope (they record what was true at
the version they document, per DOC-17's carried-forward rule) — its two matching lines are inside
the `## [0.5.0]`-era history describing what Python versions THAT release tested against, not a
current prerequisites claim.

## D-10 — disposition

**Zero hits outside the excluded areas**, across all four sweeps above. No prose fix was needed or
made in this task.

**Closing evidence — commit `70e24958`:**

```
$ git show --stat 70e24958
commit 70e249587d1f58652adf86e372f043bb02bee735
Author: yuta <yusabo90002@gmail.com>
Date:   Sun Aug 16 22:10:05 2026 +0900

    docs: fix stale version prerequisites and dead configuration link

 .planning/STATE.md                                 | 14 ++++
 ...sites-and-dead-config-link-in-published-docs.md | 90 ++++++++++++++++++++++
 docs/source/contributing.rst                       |  6 +-
 docs/source/examples/advanced.rst                  |  2 +-
 docs/source/installation.rst                       |  4 +-
 examples/advanced/README.md                        |  6 +-
 examples/basic/README.md                           |  4 +-
 7 files changed, 115 insertions(+), 11 deletions(-)
```

This commit corrected five files: `docs/source/installation.rst`, `docs/source/contributing.rst`,
`docs/source/examples/advanced.rst`, `examples/basic/README.md`, and `examples/advanced/README.md`
— two of them (`contributing.rst`, `examples/advanced.rst`) beyond the amendment's originally
enumerated four-file floor. **The amendment's five-file list was treated as a floor, not a census**:
this task's discovery grep was run repo-wide and live rather than restricted to that list, per
milestone invariants #4/#11, and it independently confirms zero remaining hits.

## D-11 — no gate added

A `tests/test_readme_version_sync.py`-shaped module — reading `requires-python` and the `sphinx`
pin out of `pyproject.toml` and sweeping every published prerequisites statement by run-time
discovery — was proposed during context-gathering and **declined by the owner**, with this exact
drift's measured recurrence history on the table: the same class of staleness survived from the
0.7.x era across multiple files before being caught by `56-REVIEW.md`. The risk of recurrence is
therefore accepted knowingly, not overlooked. **This plan added no test module.** Confirmed:

```
$ git diff --name-only -- tests/
(no output)
```

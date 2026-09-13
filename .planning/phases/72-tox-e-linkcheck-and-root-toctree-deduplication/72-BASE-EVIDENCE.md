# Phase 72 — Base Evidence (PHASE_BASE_SHA, positive control, DOC-18 edit)

Nothing in this file's `## Head check and provisioning` / `## Base identity` / `## Base HTML build`
sections was copied from `72-CONTEXT.md` or `72-RESEARCH.md`; every command was re-run live from
this worktree during this plan's execution.

PHASE_BASE_SHA = 34c77f59266acb028c8934ff56715dd4454bdfe8
MILESTONE_BASE = 098a8ff64cf008822eef9dc69f75102ded3f7bc1
SCRATCH_72_01 = /tmp/tmp.t6RH7z55HW
PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13
SPHINX_VERSION = 9.1.0
DOCUTILS_VERSION = 0.22.4
FURO_VERSION = 2025.12.19
BASE_MULTI_TOCTREE_COUNT = 5
BASE_MULTI_TOCTREE_COUNT_STDERR = 0
BASE_WARNING_COUNT = 3
BASE_CONSOLE_SELECTING_EXAMPLES_BASIC = index
BASE_CONSOLE_SELECTING_EXAMPLES_ADVANCED = index

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-13T13:22:40Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af532f7f0aa7fa06f
$ test -f .git; echo "exit:$?"
exit:0
$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning command:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```
Ran to completion; final resolved lines included `typsphinx==0.9.2 (from
file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-af532f7f0aa7fa06f)`, `sphinx==9.1.0`,
`furo` (installed as part of the `docs` extra), `tox==4.61.4`, `uv==0.12.13`. Exit 0, no error
lines.

```
$ sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg
/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
3.13.13
$ uv run python -c "import sphinx, docutils, furo; print(sphinx.__version__); print(docutils.__version__); print(furo.__version__)"
9.1.0
0.22.4
2025.12.19
$ printenv SPHINX_LANGUAGE READTHEDOCS_LANGUAGE; echo "exit:$?"
exit:1
```
Neither `SPHINX_LANGUAGE` nor `READTHEDOCS_LANGUAGE` is set — no docs-language override. Printed
nothing but `exit:1`, as required. No HALT.

Before any commit:
```
$ git rev-parse HEAD
34c77f59266acb028c8934ff56715dd4454bdfe8
$ mktemp -d
/tmp/tmp.t6RH7z55HW
```

## Base identity

```
$ git diff --name-only 098a8ff64cf008822eef9dc69f75102ded3f7bc1 34c77f59266acb028c8934ff56715dd4454bdfe8 -- . ':(exclude).planning'
(empty)
```
`PHASE_BASE_SHA`'s product tree (everything outside `.planning/`) is identical to the milestone
base `098a8ff64cf008822eef9dc69f75102ded3f7bc1`. No HALT.

## Base HTML build

Materialised the base tree with `git archive` (full tree, not just `docs/source/`, per
`72-RESEARCH.md` Pitfall 1 — `conf.py` needs `pyproject.toml` three directories above itself):

```
$ mkdir "$S/tree-base"
$ git archive 34c77f59266acb028c8934ff56715dd4454bdfe8 | tar -x -C "$S/tree-base"
```

Ran the clean HTML build with `$S/html-base` absent beforehand, `LANG=C LC_ALL=C`, no `-q` (the
`multiple toctrees` message is info-level and a quieted build could hide it, per
`72-RESEARCH.md` Open Question 1):

### Build command

```bash
LANG=C LC_ALL=C uv run sphinx-build -b html "$S/tree-base/docs/source" "$S/html-base" \
  > "$S/p7201_html-base.out" 2> "$S/p7201_html-base.err"
echo "exit:$?"
```
(Run from this worktree's root, through this worktree's `uv run`.)

```
exit:0
```

Fresh `LANG=C LC_ALL=C` grep of the stdout log:
```
$ LANG=C LC_ALL=C grep -c 'document is referenced in multiple toctrees' "$S/p7201_html-base.out"
5
$ LANG=C LC_ALL=C grep -c 'document is referenced in multiple toctrees' "$S/p7201_html-base.err"
0
```

Every matching line, verbatim (stdout, line numbers from the log):
```
28:checking consistency... /tmp/tmp.t6RH7z55HW/tree-base/docs/source/examples/advanced.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/advanced
29:/tmp/tmp.t6RH7z55HW/tree-base/docs/source/examples/basic.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/basic
30:/tmp/tmp.t6RH7z55HW/tree-base/docs/source/user_guide/builders.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/builders
31:/tmp/tmp.t6RH7z55HW/tree-base/docs/source/user_guide/configuration.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/configuration
32:/tmp/tmp.t6RH7z55HW/tree-base/docs/source/user_guide/templates.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/templates
```

The English summary line:
```
$ LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7201_html-base.out"
build succeeded, 3 warnings.
```
`BASE_WARNING_COUNT = 3`, parsed from the `N` in `build succeeded, N warnings.`.

### Counted warnings

```
$ grep -E 'WARNING:|ERROR:' "$S/p7201_html-base.err"
/tmp/tmp.t6RH7z55HW/tree-base/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
/tmp/tmp.t6RH7z55HW/tree-base/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
/tmp/tmp.t6RH7z55HW/tree-base/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
```
These are the pre-existing rST docstring errors in `TypstTranslator.visit_toctree` (ROADMAP
constraint 9) — unrelated to the DOC-18 toctree-duplication defect, and untouched by this plan
(constraint 2 forbids editing `typsphinx/`).

For `examples/basic` and `examples/advanced`, the docname after `selecting:` in their message
lines (both `index`, the root document — this is what Sphinx's log line prints; 72-04 interprets
this fact, this task only records it):
```
examples/advanced -> selecting: index <- examples/advanced   (BASE_CONSOLE_SELECTING_EXAMPLES_ADVANCED = index)
examples/basic     -> selecting: index <- examples/basic      (BASE_CONSOLE_SELECTING_EXAMPLES_BASIC = index)
```

**Positive control (constraint 7):** `BASE_MULTI_TOCTREE_COUNT = 5`, at least 1. The English
`build succeeded` line is present. No HALT.

BASE_ROOT_INCLUDE_LINES = 12
BASE_ROOT_DEAD_INCLUDES = 5
BASE_EDGE_STATE_SHA256 = 31ccf9df15ecaa0778902ecce7b494a7c40be364529ece726b5a81ec09ba0282
BASE_DEAD_GUARD_EDGES_IN_STATE = 0
BASE_SIDEBAR_COUNTS = 2 2 2 2 2
BASE_SIDEBAR_CONTROL = 1
REQUIRED_STRICT_HEAD = true
REQUIRED_CONTEXTS_HEAD = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
REQUIRED_CONTEXT_COUNT_HEAD = 6
MAIN_HEAD_AT_BASE = 098a8ff64cf008822eef9dc69f75102ded3f7bc1
MAIN_BASELINE_RUN_ID = 34751418684
MAIN_BASELINE_CONCLUSION = success

## Base Typst build

From the worktree root, with `$S/typst-base` absent beforehand:

```bash
LANG=C LC_ALL=C uv run sphinx-build -b typst "$S/tree-base/docs/source" "$S/typst-base" \
  > "$S/p7201_typst-base.log" 2>&1
echo "exit:$?"
```
```
exit:0
```

Root `index.typ` include-line count:
```
$ grep -c 'include("' "$S/typst-base/index.typ"
12
```
`BASE_ROOT_INCLUDE_LINES = 12`.

The root line matched for each of the five pages, verbatim:
```
$ grep -F '"index#0>user_guide/configuration"' "$S/typst-base/index.typ"
  if "index#0>user_guide/configuration" in state("typsphinx:include-edges", ()).get() { include("user_guide/configuration.typ") }
$ grep -F '"index#0>user_guide/builders"' "$S/typst-base/index.typ"
  if "index#0>user_guide/builders" in state("typsphinx:include-edges", ()).get() { include("user_guide/builders.typ") }
$ grep -F '"index#0>user_guide/templates"' "$S/typst-base/index.typ"
  if "index#0>user_guide/templates" in state("typsphinx:include-edges", ()).get() { include("user_guide/templates.typ") }
$ grep -F '"index#0>examples/basic"' "$S/typst-base/index.typ"
  if "index#0>examples/basic" in state("typsphinx:include-edges", ()).get() { include("examples/basic.typ") }
$ grep -F '"index#0>examples/advanced"' "$S/typst-base/index.typ"
  if "index#0>examples/advanced" in state("typsphinx:include-edges", ()).get() { include("examples/advanced.typ") }
```
`BASE_ROOT_DEAD_INCLUDES = 5` (five root guard lines found, one per page).

The master wrapper state line, verbatim, and its SHA-256:
```
$ grep -F 'state("typsphinx:include-edges", ()).update(' "$S/typst-base/typsphinx.typ"
#state("typsphinx:include-edges", ()).update(("index#0>installation", "index#0>quickstart", "index#0>user_guide/index", "user_guide/index#0>user_guide/configuration", "user_guide/index#0>user_guide/builders", "user_guide/index#0>user_guide/templates", "user_guide/index#0>user_guide/output_layout", "index#0>examples/index", "examples/index#0>examples/basic", "examples/index#0>examples/advanced", "index#0>api/index", "index#0>contributing", "index#0>changelog",))
```
SHA-256 of exactly that line: `31ccf9df15ecaa0778902ecce7b494a7c40be364529ece726b5a81ec09ba0282`
(`BASE_EDGE_STATE_SHA256`).

Count of the five dead-guard root edge keys (`"index#0>user_guide/configuration"` etc.) present
in that state line: `0` (`BASE_DEAD_GUARD_EDGES_IN_STATE`) — the root guards exist but never fire;
the state line only ever seeds the section-index-scoped edges.

The section-index lines guarding each page, verbatim:
```
$ grep -F 'include-edges' "$S/typst-base/user_guide/index.typ"
  if "user_guide/index#0>user_guide/configuration" in state("typsphinx:include-edges", ()).get() { include("configuration.typ") }
  if "user_guide/index#0>user_guide/builders" in state("typsphinx:include-edges", ()).get() { include("builders.typ") }
  if "user_guide/index#0>user_guide/templates" in state("typsphinx:include-edges", ()).get() { include("templates.typ") }
  if "user_guide/index#0>user_guide/output_layout" in state("typsphinx:include-edges", ()).get() { include("output_layout.typ") }
$ grep -F 'include-edges' "$S/typst-base/examples/index.typ"
  if "examples/index#0>examples/basic" in state("typsphinx:include-edges", ()).get() { include("basic.typ") }
  if "examples/index#0>examples/advanced" in state("typsphinx:include-edges", ()).get() { include("advanced.typ") }
```

## Base sidebar

Copied the `html.parser`-based sidebar-scoped link counter from `72-RESEARCH.md` § "Sidebar-scoped
link count" verbatim to `$S/p7201_sidebar.py` (scratch helper, never committed). Ran it against the
base build's `index.html`:

```
$ uv run python "$S/p7201_sidebar.py" "$S/html-base/index.html"
user_guide/configuration.html: count=2 parents=['user_guide/index.html', None]
user_guide/builders.html: count=2 parents=['user_guide/index.html', None]
user_guide/templates.html: count=2 parents=['user_guide/index.html', None]
examples/basic.html: count=2 parents=['examples/index.html', None]
examples/advanced.html: count=2 parents=['examples/index.html', None]
user_guide/output_layout.html: count=1 parents=['user_guide/index.html']
```
`BASE_SIDEBAR_COUNTS = 2 2 2 2 2` (configuration, builders, templates, basic, advanced, in that
order). `BASE_SIDEBAR_CONTROL = 1` (the `user_guide/output_layout.html` control, never listed at
root).

Every one of the five counts is at least 2 — the base shows the defect. No HALT.

## Phase-head remote reads

Required checks (read-only):
```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq .strict
true
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '[.contexts[]] | sort | join("|")'
Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '.contexts | length'
6
```
`REQUIRED_STRICT_HEAD = true`, `REQUIRED_CONTEXTS_HEAD` as above (6 contexts,
`REQUIRED_CONTEXT_COUNT_HEAD = 6`) — matches ROADMAP constraint 3's measured set exactly.

Main's baseline CI run (constraint 6):
```
$ git ls-remote origin refs/heads/main
098a8ff64cf008822eef9dc69f75102ded3f7bc1	refs/heads/main
```
`MAIN_HEAD_AT_BASE = 098a8ff64cf008822eef9dc69f75102ded3f7bc1` — identical to `MILESTONE_BASE`.

```
$ gh run list --workflow=ci.yml --branch main --event push --limit 10 --json databaseId,headSha,status,conclusion,createdAt
```
The row whose `headSha` equals `098a8ff64cf008822eef9dc69f75102ded3f7bc1`:
```json
{"conclusion":"success","createdAt":"2026-09-13T10:16:28Z","databaseId":34751418684,"headSha":"098a8ff64cf008822eef9dc69f75102ded3f7bc1","status":"completed"}
```
`MAIN_BASELINE_RUN_ID = 34751418684`, `MAIN_BASELINE_CONCLUSION = success`.

Head branch census:
```
$ git branch --list 'gsd/v0.9.5*' -v
+ gsd/v0.9.5-docs-link-check-and-navigation 34c77f59 docs(72): create phase plan
$ git ls-remote --heads origin 'gsd/v0.9.5*'
(empty)
```
No decoy branch (`gsd/v0.9.5-milestone`) exists yet, and the canonical branch is not yet on
`origin` — matches ROADMAP constraint 6's expectation exactly. 72-06 re-measures both immediately
before its push.

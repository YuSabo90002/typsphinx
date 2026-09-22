# Phase 74 — Base Evidence (PHASE_BASE_SHA, base build, QUA-14 census)

PHASE_BASE_SHA = 8ea10273265e3966b6e650bad43cf90c9598ed65
MILESTONE_BASE = 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b
SCRATCH_74_01 = /tmp/tmp.JkJbjLa7hI
PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13
SPHINX_VERSION = 9.1.0
DOCUTILS_VERSION = 0.22.4
TYPST_PY_VERSION = 0.15.0
AUTODOC_TYPEHINTS_VERSION = 3.13.6
MYST_PARSER_VERSION = 5.1.0
BASE_TRANSLATOR_DOCTEST_MENTIONS = 0
BASE_WARNING_COUNT = 5
BASE_DOCTEST_UNKNOWN_COUNT = 2
BASE_API_COLLAPSED_RUNS = 2
BASE_API_EXAMPLE_LINE = 811
BASE_API_PYTHON_FENCES = 0
BASE_API_TERMS_ITEM_COUNT = 0

## Head check and provisioning

- `date -u +%FT%TZ` -> `2026-09-19T22:04:18Z`
- `pwd -P` -> `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf` (under
  `/home/yuta/Documents/typsphinx/.claude/worktrees/`)
- `test -f .git; echo "exit:$?"` -> `exit:0` (worktree confirmed — `.git` is a file)
- `grep -c typsphinx-fhs-run "$(command -v uv)"` -> `2`

Provisioning line (`<worktree_provisioning>`, `CLAUDE.md` § "Worktree-isolated execution" plus the
`--extra docs --python 3.13.13` additions):

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```

Exit status: `0`. `typsphinx==0.9.2` installed editable from this worktree's own checkout path,
`sphinx==9.1.0`, `sphinx-autodoc-typehints==3.13.6`, `myst-parser==5.1.0` all resolved.

- `sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg` ->
  `PYVENV_HOME` = `/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin`,
  `PYVENV_VERSION_INFO` = `3.13.13` — same interpreter version as the main checkout and
  74-RESEARCH.md's own measurements.
- `uv run python -c "..."` (importlib.metadata.version) ->
  `SPHINX_VERSION` = `9.1.0`, `DOCUTILS_VERSION` = `0.22.4`, `TYPST_PY_VERSION` = `0.15.0`,
  `AUTODOC_TYPEHINTS_VERSION` = `3.13.6`, `MYST_PARSER_VERSION` = `5.1.0`.
- `printenv SPHINX_LANGUAGE READTHEDOCS_LANGUAGE; echo "exit:$?"` -> printed nothing but `exit:1`.
  Neither variable is set; the docs language is not overridden.
- Before any commit: `PHASE_BASE_SHA` = `git rev-parse HEAD` =
  `8ea10273265e3966b6e650bad43cf90c9598ed65`. `SCRATCH_74_01` = `mktemp -d` =
  `/tmp/tmp.JkJbjLa7hI`.

## Base identity

- `MILESTONE_BASE` = `6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b`.
- `git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b 8ea10273265e3966b6e650bad43cf90c9598ed65 -- . ':(exclude).planning'`
  printed nothing. `PHASE_BASE_SHA`'s product tree outside `.planning/` equals the milestone base.
- `grep -c doctest typsphinx/translator.py || true` -> `0`, recorded as
  `BASE_TRANSLATOR_DOCTEST_MENTIONS`. No `doctest_block` handler exists on the base, as expected.

## Base Typst build

### Build command

```
rm -rf "$S/base-typst"
LANG=C LC_ALL=C uv run python -m sphinx -b typst docs/source "$S/base-typst" > "$S/p7401_base-typst.log" 2>&1
```

Run from this worktree's root, with `$S` = `SCRATCH_74_01` (`/tmp/tmp.JkJbjLa7hI`). No `-q` flag.
`echo "exit:$?"` -> `exit:0`.

The English summary line, `LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7401_base-typst.log"`,
verbatim:

```
build succeeded, 5 warnings.
```

`BASE_WARNING_COUNT` = `5`, the integer in `build succeeded, 5 warnings.`.

### Counted warnings

Every `WARNING:`/`ERROR:` line of the log, verbatim (`LANG=C LC_ALL=C grep -nE 'ERROR:|WARNING:' "$S/p7401_base-typst.log"`):

```
33:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
34:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
35:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
40:writing output... [api/index]WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
46:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
```

### Doctest block warnings

`BASE_DOCTEST_UNKNOWN_COUNT` = `2`
(`LANG=C LC_ALL=C grep -o 'unknown node type: .doctest_block' "$S/p7401_base-typst.log" | wc -l`).

Each such warning's first line (`grep -n 'unknown node type: .doctest_block' "$S/p7401_base-typst.log"`), verbatim:

```
40:writing output... [api/index]WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
46:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
```

**Positive control (constraints 4 and 5):** `BASE_DOCTEST_UNKNOWN_COUNT` (`2`) is at least 1, and the
English `build succeeded` line is present. Positive control passes.

### api/index.typ example region

Using `$S/base-typst/api/index.typ`:

- `BASE_API_COLLAPSED_RUNS` = `2` (`grep -c 'text(">>> ' "$S/base-typst/api/index.typ"`), at least 1.
- `BASE_API_EXAMPLE_LINE` = `811`, the line containing
  `text(">>> compute_content_include_path("`.

`grep -n -B3 'text(">>> ' "$S/base-typst/api/index.typ"` verbatim:

```
808-
809-strong({text("Examples")})
810-linebreak()
811:text(">>> compute_content_include_path(\"\", \"index.typ\") 'index.typ' >>> compute_content_include_path(\"manuals\", \"guide/index.typ\") '../guide/index.typ' >>> compute_content_include_path(\"guide\", \"guide/index.typ\") 'index.typ'")})
--
864-
865-strong({text("Examples")})
866-linebreak()
867:text(">>> compute_template_import_path(\"typst\", \"base.typ\") '/_template/typst/base.typ' >>> compute_template_import_path(\"report\", \"custom.typ\") '/_template/report/custom.typ'")})
```

This is the verbatim collapsed region SC1 names: the three prompts, their continuations and their
outputs on one physical `.typ` line each.

- `BASE_API_PYTHON_FENCES` = `0` (count of lines exactly three backticks followed by `python`, via
  `grep -cx`, or 0). No fenced code blocks exist yet — the base collapses doctest examples to
  `text("...")` runs, not fences.
- `BASE_API_TERMS_ITEM_COUNT` = `0` (`grep -c 'terms\.item' "$S/base-typst/api/index.typ" || true`).
  This confirms the D-06 amendment's measurement: this project's own `api/index.typ` carries no
  `terms.item(...)` doctest shape at the base. Recorded as context; it gates nothing here.

## QUA-14 census

BASE_RAW_UNEXPECTED_INDENTATION = 6
BASE_RAW_BLOCK_QUOTE_ENDS = 4
BASE_RAW_TOTAL = 10
BASE_ATTRIBUTED_COUNT = 3
BASE_UNATTRIBUTED_COUNT = 7
BASE_UNATTRIBUTED_UNMATCHED = 0
FIX_LIST = typsphinx.pathfmt.quote_path|typsphinx.translator.TypstTranslator.visit_toctree
FIX_LIST_COUNT = 2

All greps below run as `LANG=C LC_ALL=C` over `$S/p7401_base-typst.log` (`$L`), the same log Task 1
built. `|| true` is used on every grep whose count may be 0.

`BASE_RAW_UNEXPECTED_INDENTATION` = `grep -o 'Unexpected indentation' "$L" | wc -l` = `6`.
`BASE_RAW_BLOCK_QUOTE_ENDS` = `grep -o 'Block quote ends without a blank line' "$L" | wc -l` = `4`.
`BASE_RAW_TOTAL` = their sum = `10`.

### Raw lines

`grep -nE 'Unexpected indentation|Block quote ends without a blank line' "$L"`, verbatim:

```
12::19: (ERROR/3) Unexpected indentation.
13::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
14::19: (ERROR/3) Unexpected indentation.
15::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
16::5: (ERROR/3) Unexpected indentation.
17::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
18::21: (ERROR/3) Unexpected indentation.
33:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
34:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
35:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
```

10 raw lines total, matching `BASE_RAW_TOTAL`.

### Attributed lines

Filter: `grep -nE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$L"`, verbatim:

```
33:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
34:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
35:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
```

All three originate in `typsphinx/translator.py`, fully qualified name
`typsphinx.translator.TypstTranslator.visit_toctree`, docstring-relative lines 5, 6 and 21.
`BASE_ATTRIBUTED_COUNT` = `3`.

### Unattributed lines

The raw lines that do not contain `.py:docstring of `
(`grep -nE '...' "$L" | grep -v '\.py:docstring of '`), verbatim:

```
12::19: (ERROR/3) Unexpected indentation.
13::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
14::19: (ERROR/3) Unexpected indentation.
15::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
16::5: (ERROR/3) Unexpected indentation.
17::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
18::21: (ERROR/3) Unexpected indentation.
```

`BASE_UNATTRIBUTED_COUNT` = `7`. `BASE_ATTRIBUTED_COUNT` (3) + `BASE_UNATTRIBUTED_COUNT` (7) = `10`
= `BASE_RAW_TOTAL`.

### Docstring probe

Scratch helper `$S/p7401_docstring_probe.py` (never committed), run with `uv run python`. It walks
every module under `typsphinx` via `pkgutil.walk_packages`, visits every function, class, and
function defined directly in a class body whose defining source file (`inspect.getsourcefile`) is
under this worktree's `typsphinx/` directory, converts each such object's own `__doc__` with
`inspect.cleandoc()` then `sphinx.ext.napoleon.docstring.GoogleDocstring(...).lines()`, and parses
the joined result with `docutils.core.publish_doctree()`, printing one tab-separated row per system
message matching either QUA-14 message class (fully qualified name, docstring-relative line, level
word, message).

Full output, verbatim:

```
typsphinx.pathfmt.quote_path	19	ERROR	<string>:19: (ERROR/3) Unexpected indentation.
typsphinx.pathfmt.quote_path	21	WARNING	<string>:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
typsphinx.translator.TypstTranslator.visit_toctree	5	ERROR	<string>:5: (ERROR/3) Unexpected indentation.
typsphinx.translator.TypstTranslator.visit_toctree	6	WARNING	<string>:6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
typsphinx.translator.TypstTranslator.visit_toctree	21	ERROR	<string>:21: (ERROR/3) Unexpected indentation.
```

No skipped modules and no probing errors were reported on stderr (checked: zero `# skip module` /
`# error probing` lines). Among every typsphinx-defined function, class and method under
`typsphinx/`, exactly two docstrings raise either QUA-14 message class:
`typsphinx.pathfmt.quote_path` (19 ERROR, 21 WARNING) and
`typsphinx.translator.TypstTranslator.visit_toctree` (5 ERROR, 6 WARNING, 21 ERROR).

### Attribution table

| Census line(s) | Line | Class | Probe match |
|---|---|---|---|
| unattributed #1, #3 (`:19: (ERROR/3)`) | 19 | Unexpected indentation (ERROR) | `typsphinx.pathfmt.quote_path` |
| unattributed #2, #4 (`:21: (WARNING/2)`) | 21 | Block quote ends (WARNING) | `typsphinx.pathfmt.quote_path` |
| unattributed #5 (`:5: (ERROR/3)`) | 5 | Unexpected indentation (ERROR) | `typsphinx.translator.TypstTranslator.visit_toctree` |
| unattributed #6 (`:6: (WARNING/2)`) | 6 | Block quote ends (WARNING) | `typsphinx.translator.TypstTranslator.visit_toctree` |
| unattributed #7 (`:21: (ERROR/3)`) | 21 | Unexpected indentation (ERROR) | `typsphinx.translator.TypstTranslator.visit_toctree` |
| attributed (`visit_toctree:5: ERROR`) | 5 | Unexpected indentation (ERROR) | confirmed: probe reproduces line 5 ERROR for `typsphinx.translator.TypstTranslator.visit_toctree` |
| attributed (`visit_toctree:6: WARNING`) | 6 | Block quote ends (WARNING) | confirmed: probe reproduces line 6 WARNING for `typsphinx.translator.TypstTranslator.visit_toctree` |
| attributed (`visit_toctree:21: ERROR`) | 21 | Unexpected indentation (ERROR) | confirmed: probe reproduces line 21 ERROR for `typsphinx.translator.TypstTranslator.visit_toctree` |

Every one of the 7 unattributed lines is matched to a probe row by (docstring-relative line, message
class) pair; no pair matches more than one docstring. `BASE_UNATTRIBUTED_UNMATCHED` = `0`.

### Fix list

`FIX_LIST` = the `|`-joined, `LC_ALL=C`-sorted, de-duplicated fully qualified names of every
docstring named in the attributed lines (§ Attributed lines) and in the attribution table's probe
matches (§ Attribution table):

```
typsphinx.pathfmt.quote_path|typsphinx.translator.TypstTranslator.visit_toctree
```

`FIX_LIST_COUNT` = `2`. This is the whole census over the whole log (constraint 6), never narrowed to
`visit_toctree` alone — per D-07, `typsphinx.pathfmt.quote_path` is included because the probe
attributes both its unattributed census lines (`:19` ERROR, `:21` WARNING) to it.

#### Probe-only rows (not in the build census)

None. Every probe row found (`quote_path` at 19/21, `visit_toctree` at 5/6/21) corresponds exactly to
a line the build log actually reported — the probe found no additional typsphinx docstring raising
either QUA-14 message class that the build census did not already surface.

**Positive control (constraint 5):** `BASE_RAW_TOTAL` (10) and `BASE_ATTRIBUTED_COUNT` (3) are both
at least 1. Positive control passes.

## Phase-head remote reads

REQUIRED_STRICT_HEAD = true
REQUIRED_CONTEXTS_HEAD = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
REQUIRED_CONTEXT_COUNT_HEAD = 6
ORIGIN_MAIN_AT_HEAD = 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b
MAIN_MOVED = no

- `gh auth status; echo "exit:$?"` -> `exit:0`. Authenticated as `YuSabo90002`.
- `gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq .strict`
  -> `true` (`REQUIRED_STRICT_HEAD`).
- `... --jq '[.contexts[]] | sort | join("|")'` -> the six-context sorted string above
  (`REQUIRED_CONTEXTS_HEAD`), `... --jq '.contexts | length'` -> `6`
  (`REQUIRED_CONTEXT_COUNT_HEAD`).
- `git ls-remote origin refs/heads/main` -> `6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b`
  (`ORIGIN_MAIN_AT_HEAD`). `MAIN_MOVED` = `no`, since it equals
  `6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b`. This is a record for `/gsd-complete-milestone`, not
  a gate.

## Branch census at phase head

HEAD_LOCAL_DECOY = absent
ORIGIN_BRANCH_AT_HEAD = none

`git branch --list 'gsd/*' -v`, verbatim:

```
  gsd/v0.9.4-typing-modernization                334b4da7 docs(v0.9.4): add milestone audit report
  gsd/v0.9.5-docs-link-check-and-navigation      1d8c76c6 Merge origin/main into gsd/v0.9.5-docs-link-check-and-navigation
+ gsd/v0.9.6-doctest-block-rendering-and-release 8ea10273 docs(state): begin phase 74 execution
```

`git ls-remote --heads origin 'refs/heads/gsd/v0.9.6*'` -> no output (empty). No `gsd/v0.9.6*`
branch exists on origin yet.

- `HEAD_LOCAL_DECOY` = `absent`: `git branch --list 'gsd/v0.9.6-milestone'` printed nothing — no
  local decoy branch exists.
- `ORIGIN_BRANCH_AT_HEAD` = `none`: `git ls-remote origin refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release`
  printed nothing. Expected — the branch has never been pushed. Nothing is changed here;
  constraint 10's decoy handling runs in 74-07, immediately before the push.

## Reference CI job set

REFERENCE_CI_RUN_ID = 35083828156
REFERENCE_JOB_NAMES = Build Package|Code Coverage|Integration Test - advanced|Integration Test - basic|Lint and Format Check|Test Python 3.12 on macos-latest|Test Python 3.12 on ubuntu-latest|Test Python 3.12 on windows-latest|Test Python 3.13 on macos-latest|Test Python 3.13 on ubuntu-latest|Test Python 3.13 on windows-latest|Type Check
REFERENCE_JOB_COUNT = 12
CI_YML_CHANGED_SINCE_MILESTONE_BASE = no

- `REFERENCE_CI_RUN_ID` = `sed -n 's/^RUN_ID = //p'` over `73-CI-EVIDENCE.md` = `35083828156`,
  matching the planning-time context measurement.
- `REFERENCE_JOB_NAMES` = `gh run view 35083828156 --json jobs --jq '[.jobs[].name] | sort | join("|")'`,
  the twelve-job sorted string above. `REFERENCE_JOB_COUNT` = `gh run view 35083828156 --json jobs --jq '.jobs | length'`
  = `12`.
- `CI_YML_CHANGED_SINCE_MILESTONE_BASE` = `no`:
  `git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b HEAD -- .github/workflows/ci.yml`
  printed nothing.

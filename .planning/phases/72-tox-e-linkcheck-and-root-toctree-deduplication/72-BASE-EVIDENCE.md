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

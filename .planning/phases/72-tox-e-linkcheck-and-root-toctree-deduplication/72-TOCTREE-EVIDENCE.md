# Phase 72 — Toctree Evidence (DOC-18, SC#3 and SC#4)

TIP_SHA = 4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5
SCRATCH_72_04 = /tmp/tmp.CtjpuH1Kzi
PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13
SPHINX_VERSION = 9.1.0
DOCUTILS_VERSION = 0.22.4
FURO_VERSION = 2025.12.19
SC3_EDIT_SHAPE = MET
MULTI_TOCTREE_BASE = 5
MULTI_TOCTREE_TIP = 0
WARNINGS_BASE = 3
WARNINGS_TIP = 3
WARNING_LINES_IDENTICAL = yes
SC3_PAIR = 1
W1_BASE_MATCH = yes
SC3_VERDICT = MET

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-13T13:45:17Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a95142407f7f27593
$ test -f .git; echo "exit:$?"
exit:0
$ grep -q typsphinx-fhs-run "$(command -v uv)"; echo shim OK
shim OK
```

Provisioning command:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```
Ran to completion, exit 0: 90 packages installed, `typsphinx==0.9.2 (from
file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a95142407f7f27593)`, `sphinx==9.1.0`,
`furo==2025.12.19`, `tox==4.61.4`, `uv==0.12.13`.

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
4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5
$ mktemp -d
/tmp/tmp.CtjpuH1Kzi
```

`PHASE_BASE_SHA` read from `72-BASE-EVIDENCE.md`: `34c77f59266acb028c8934ff56715dd4454bdfe8`.

## Tip carries both edits

```
$ git diff --stat 34c77f59266acb028c8934ff56715dd4454bdfe8 4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5 -- docs/
 docs/source/contributing.rst | 1 +
 docs/source/index.rst        | 5 -----
 2 files changed, 1 insertion(+), 5 deletions(-)
```
Both edits present; `docs/source/conf.py` does not appear in the diff (no D-02 key was recorded by
72-02).

```
$ git grep -c 'tox -e linkcheck' 4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5 -- docs/source/contributing.rst
4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5:docs/source/contributing.rst:1
```
Count is 1. No HALT.

## Edit shape

```
$ git diff --numstat 34c77f59266acb028c8934ff56715dd4454bdfe8 4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5 -- docs/source/index.rst
0	5	docs/source/index.rst
$ git diff -U0 34c77f59266acb028c8934ff56715dd4454bdfe8 4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5 -- docs/source/index.rst
@@ -43,3 +42,0 @@ Quick Links
-   user_guide/configuration
-   user_guide/builders
-   user_guide/templates
@@ -52,2 +48,0 @@ Quick Links
-   examples/basic
-   examples/advanced
```
0 added, 5 removed — matches the five entries from 72-BASE-EVIDENCE.md's DOC-18 edit.

```
$ git diff --name-only 34c77f59266acb028c8934ff56715dd4454bdfe8 4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5 -- docs/source/user_guide/index.rst docs/source/examples/index.rst
(empty)
```
Both section-index files are absent from the diff.

```
$ git diff 34c77f59266acb028c8934ff56715dd4454bdfe8 4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5 -- docs/source/conf.py
(empty)
```
`conf.py` gains no theme, sidebar or `linkcheck_*` key — it is untouched.

## HTML pair 1

Materialised base and tip trees with `git archive` (full tree, per `72-RESEARCH.md` Pitfall 1):
```
$ mkdir -p /tmp/tmp.CtjpuH1Kzi/tree-base /tmp/tmp.CtjpuH1Kzi/tree-tip
$ git archive 34c77f59266acb028c8934ff56715dd4454bdfe8 | tar -x -C /tmp/tmp.CtjpuH1Kzi/tree-base
exit:0
$ git archive 4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5 | tar -x -C /tmp/tmp.CtjpuH1Kzi/tree-tip
exit:0
```

Ran 72-01's HTML build command shape twice, base first then tip, from this worktree's root, through
this worktree's `uv run`, `$S/html-base` and `$S/html-tip` absent beforehand:

```bash
LANG=C LC_ALL=C uv run sphinx-build -b html /tmp/tmp.CtjpuH1Kzi/tree-base/docs/source /tmp/tmp.CtjpuH1Kzi/html-base \
  > /tmp/tmp.CtjpuH1Kzi/p7204_html-base.out 2> /tmp/tmp.CtjpuH1Kzi/p7204_html-base.err
echo "exit:$?"
```
```
exit:0
```
```bash
LANG=C LC_ALL=C uv run sphinx-build -b html /tmp/tmp.CtjpuH1Kzi/tree-tip/docs/source /tmp/tmp.CtjpuH1Kzi/html-tip \
  > /tmp/tmp.CtjpuH1Kzi/p7204_html-tip.out 2> /tmp/tmp.CtjpuH1Kzi/p7204_html-tip.err
echo "exit:$?"
```
```
exit:0
```

Fresh `LANG=C LC_ALL=C` grep of each stdout log:
```
$ LANG=C LC_ALL=C grep -c 'document is referenced in multiple toctrees' /tmp/tmp.CtjpuH1Kzi/p7204_html-base.out
5
$ LANG=C LC_ALL=C grep -c 'document is referenced in multiple toctrees' /tmp/tmp.CtjpuH1Kzi/p7204_html-tip.out
0
```
`MULTI_TOCTREE_BASE = 5`, `MULTI_TOCTREE_TIP = 0`.

Every matching line at base, verbatim:
```
28:checking consistency... /tmp/tmp.CtjpuH1Kzi/tree-base/docs/source/examples/advanced.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/advanced
29:/tmp/tmp.CtjpuH1Kzi/tree-base/docs/source/examples/basic.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/basic
30:/tmp/tmp.CtjpuH1Kzi/tree-base/docs/source/user_guide/builders.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/builders
31:/tmp/tmp.CtjpuH1Kzi/tree-base/docs/source/user_guide/configuration.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/configuration
32:/tmp/tmp.CtjpuH1Kzi/tree-base/docs/source/user_guide/templates.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/templates
```

English summary lines:
```
$ LANG=C LC_ALL=C grep -E '^build succeeded' /tmp/tmp.CtjpuH1Kzi/p7204_html-base.out
build succeeded, 3 warnings.
$ LANG=C LC_ALL=C grep -E '^build succeeded' /tmp/tmp.CtjpuH1Kzi/p7204_html-tip.out
build succeeded, 3 warnings.
```
`WARNINGS_BASE = 3`, `WARNINGS_TIP = 3`.

**Positive control (constraint 7):** `MULTI_TOCTREE_BASE = 5`, at least 1, before the tip's zero
count is read as meaningful. No HALT.

## Warning lines

`.err` lines (`WARNING:`/`ERROR:`), each tree's absolute root replaced with `<tree>`:
```
$ grep -E 'WARNING:|ERROR:' /tmp/tmp.CtjpuH1Kzi/p7204_html-base.err
/tmp/tmp.CtjpuH1Kzi/tree-base/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
/tmp/tmp.CtjpuH1Kzi/tree-base/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
/tmp/tmp.CtjpuH1Kzi/tree-base/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
$ grep -E 'WARNING:|ERROR:' /tmp/tmp.CtjpuH1Kzi/p7204_html-tip.err
/tmp/tmp.CtjpuH1Kzi/tree-tip/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
/tmp/tmp.CtjpuH1Kzi/tree-tip/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
/tmp/tmp.CtjpuH1Kzi/tree-tip/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
```
After replacing `/tmp/tmp.CtjpuH1Kzi/tree-base` and `/tmp/tmp.CtjpuH1Kzi/tree-tip` each with
`<tree>`, `diff` between the two normalized sets is empty. `WARNING_LINES_IDENTICAL = yes`. These
are the pre-existing rST docstring errors in `TypstTranslator.visit_toctree` (ROADMAP
constraint 9), unrelated to DOC-18, untouched by this plan. Recorded, not gating; SC#3 gates on the
count (already equal: `WARNINGS_BASE = WARNINGS_TIP = 3`).

## Re-take rule

Not needed: `WARNINGS_BASE` (3) equals `WARNINGS_TIP` (3) on the first pair. `SC3_PAIR = 1`.

## Cross-check with wave 1

`72-BASE-EVIDENCE.md`: `BASE_MULTI_TOCTREE_COUNT = 5`, `BASE_WARNING_COUNT = 3`. This plan's
same-environment pair: `MULTI_TOCTREE_BASE = 5`, `WARNINGS_BASE = 3`. Both equal.
`W1_BASE_MATCH = yes`. SC#3 is judged on this plan's same-environment pair regardless.

## SC#3 verdict

`SC3_EDIT_SHAPE = MET`, `MULTI_TOCTREE_BASE = 5` (at least 1), `MULTI_TOCTREE_TIP = 0`,
`WARNINGS_TIP = WARNINGS_BASE = 3`, both builds from this one venv (interpreter
`PYVENV_VERSION_INFO = 3.13.13`, recorded above).

`SC3_VERDICT = MET`

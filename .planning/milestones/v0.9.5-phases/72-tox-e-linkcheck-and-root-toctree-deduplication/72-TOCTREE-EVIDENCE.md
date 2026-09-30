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

SIDEBAR_BASE_COUNTS = 2 2 2 2 2
SIDEBAR_TIP_COUNTS = 1 1 1 1 1
SIDEBAR_TIP_PARENTS = user_guide/index.html user_guide/index.html user_guide/index.html examples/index.html examples/index.html
SIDEBAR_BASE_CONTROL = 1
SIDEBAR_TIP_CONTROL = 1
ROOT_INCLUDE_LINES_BASE = 12
ROOT_INCLUDE_LINES_TIP = 7
ROOT_DEAD_INCLUDES_BASE = 5
ROOT_DEAD_INCLUDES_TIP = 0
SECTION_GUARDS_TIP = 5
EDGES_PER_PAGE_TIP = 1 1 1 1 1
EDGE_STATE_IDENTICAL = yes
TYPST_DIFF_FILES = index.typ contributing.typ .doctrees/api/index.doctree .doctrees/changelog.doctree .doctrees/contributing.doctree .doctrees/environment.pickle .doctrees/examples/advanced.doctree .doctrees/examples/basic.doctree .doctrees/examples/index.doctree .doctrees/index.doctree .doctrees/installation.doctree .doctrees/quickstart.doctree .doctrees/user_guide/builders.doctree .doctrees/user_guide/configuration.doctree .doctrees/user_guide/index.doctree .doctrees/user_guide/output_layout.doctree .doctrees/user_guide/templates.doctree
SC4_HTML_VERDICT = MET
SC4_TYPST_VERDICT = MET

## Sidebar

Copied the `html.parser`-based sidebar-scoped link counter from `72-RESEARCH.md` § "Sidebar-scoped
link count" verbatim to `/tmp/tmp.CtjpuH1Kzi/p7204_sidebar.py` (scratch helper, never committed). Ran it over
`html-base/index.html` and `html-tip/index.html` (pair `SC3_PAIR = 1`, unsuffixed names):

```
$ uv run python /tmp/tmp.CtjpuH1Kzi/p7204_sidebar.py /tmp/tmp.CtjpuH1Kzi/html-base/index.html
user_guide/configuration.html: count=2 parents=['user_guide/index.html', None]
user_guide/builders.html: count=2 parents=['user_guide/index.html', None]
user_guide/templates.html: count=2 parents=['user_guide/index.html', None]
examples/basic.html: count=2 parents=['examples/index.html', None]
examples/advanced.html: count=2 parents=['examples/index.html', None]
user_guide/output_layout.html: count=1 parents=['user_guide/index.html']
$ uv run python /tmp/tmp.CtjpuH1Kzi/p7204_sidebar.py /tmp/tmp.CtjpuH1Kzi/html-tip/index.html
user_guide/configuration.html: count=1 parents=['user_guide/index.html']
user_guide/builders.html: count=1 parents=['user_guide/index.html']
user_guide/templates.html: count=1 parents=['user_guide/index.html']
examples/basic.html: count=1 parents=['examples/index.html']
examples/advanced.html: count=1 parents=['examples/index.html']
user_guide/output_layout.html: count=1 parents=['user_guide/index.html']
```

In the page order configuration, builders, templates, basic, advanced:
`SIDEBAR_BASE_COUNTS = 2 2 2 2 2`, `SIDEBAR_TIP_COUNTS = 1 1 1 1 1`,
`SIDEBAR_TIP_PARENTS = user_guide/index.html user_guide/index.html user_guide/index.html examples/index.html examples/index.html`,
`SIDEBAR_BASE_CONTROL = 1`, `SIDEBAR_TIP_CONTROL = 1`.

The tip shows a count of 1 for every page, with parent `user_guide/index.html` for the first three
and `examples/index.html` for the last two, and a control of 1. The base shows every page at least
2. No HALT.

## Typst pair

Built `-b typst` for base and tip back to back, clean, from the same `git archive` trees, into
`/tmp/tmp.CtjpuH1Kzi/typst-base` and `/tmp/tmp.CtjpuH1Kzi/typst-tip`:

```bash
LANG=C LC_ALL=C uv run sphinx-build -b typst /tmp/tmp.CtjpuH1Kzi/tree-base/docs/source /tmp/tmp.CtjpuH1Kzi/typst-base > /tmp/tmp.CtjpuH1Kzi/p7204_typst-base.log 2>&1
echo "exit:$?"
```
```
exit:0
```
```bash
LANG=C LC_ALL=C uv run sphinx-build -b typst /tmp/tmp.CtjpuH1Kzi/tree-tip/docs/source /tmp/tmp.CtjpuH1Kzi/typst-tip > /tmp/tmp.CtjpuH1Kzi/p7204_typst-tip.log 2>&1
echo "exit:$?"
```
```
exit:0
```
Both exits 0.

Root `index.typ` include-line counts:
```
$ grep -c 'include("' /tmp/tmp.CtjpuH1Kzi/typst-base/index.typ
12
$ grep -c 'include("' /tmp/tmp.CtjpuH1Kzi/typst-tip/index.typ
7
```
`ROOT_INCLUDE_LINES_BASE = 12`, `ROOT_INCLUDE_LINES_TIP = 7`.

For each of the five pages, the dead root guard count in each `index.typ`:
```
$ for p in user_guide/configuration user_guide/builders user_guide/templates examples/basic examples/advanced; do grep -cF "\"index#0>$p\"" /tmp/tmp.CtjpuH1Kzi/typst-base/index.typ; done
1
1
1
1
1
$ for p in user_guide/configuration user_guide/builders user_guide/templates examples/basic examples/advanced; do grep -cF "\"index#0>$p\"" /tmp/tmp.CtjpuH1Kzi/typst-tip/index.typ; done
0
0
0
0
0
```
`ROOT_DEAD_INCLUDES_BASE = 5` (sum), matching 72-01's `BASE_ROOT_DEAD_INCLUDES = 5`.
`ROOT_DEAD_INCLUDES_TIP = 0` — no dead root guard for any of the five pages left in the tip
`index.typ`.

The guard line in each tip section index, verbatim:
```
$ grep -F 'include-edges' /tmp/tmp.CtjpuH1Kzi/typst-tip/user_guide/index.typ
  if "user_guide/index#0>user_guide/configuration" in state("typsphinx:include-edges", ()).get() { include("configuration.typ") }
  if "user_guide/index#0>user_guide/builders" in state("typsphinx:include-edges", ()).get() { include("builders.typ") }
  if "user_guide/index#0>user_guide/templates" in state("typsphinx:include-edges", ()).get() { include("templates.typ") }
  if "user_guide/index#0>user_guide/output_layout" in state("typsphinx:include-edges", ()).get() { include("output_layout.typ") }
$ grep -F 'include-edges' /tmp/tmp.CtjpuH1Kzi/typst-tip/examples/index.typ
  if "examples/index#0>examples/basic" in state("typsphinx:include-edges", ()).get() { include("basic.typ") }
  if "examples/index#0>examples/advanced" in state("typsphinx:include-edges", ()).get() { include("advanced.typ") }
```
`SECTION_GUARDS_TIP = 5` (the three `user_guide/*` guards plus the two `examples/*` guards).

The include-edges state line of each `typsphinx.typ`, verbatim (byte-identical between base and
tip):
```
$ grep -F 'state("typsphinx:include-edges", ()).update(' /tmp/tmp.CtjpuH1Kzi/typst-base/typsphinx.typ
#state("typsphinx:include-edges", ()).update(("index#0>installation", "index#0>quickstart", "index#0>user_guide/index", "user_guide/index#0>user_guide/configuration", "user_guide/index#0>user_guide/builders", "user_guide/index#0>user_guide/templates", "user_guide/index#0>user_guide/output_layout", "index#0>examples/index", "examples/index#0>examples/basic", "examples/index#0>examples/advanced", "index#0>api/index", "index#0>contributing", "index#0>changelog",))
$ grep -F 'state("typsphinx:include-edges", ()).update(' /tmp/tmp.CtjpuH1Kzi/typst-tip/typsphinx.typ
#state("typsphinx:include-edges", ()).update(("index#0>installation", "index#0>quickstart", "index#0>user_guide/index", "user_guide/index#0>user_guide/configuration", "user_guide/index#0>user_guide/builders", "user_guide/index#0>user_guide/templates", "user_guide/index#0>user_guide/output_layout", "index#0>examples/index", "examples/index#0>examples/basic", "examples/index#0>examples/advanced", "index#0>api/index", "index#0>contributing", "index#0>changelog",))
```
`EDGE_STATE_IDENTICAL = yes`.

Parsed the tip line's quoted edge strings with `uv run python`, counting edges ending in `#0>P` for
each page:
```
$ grep -F 'state("typsphinx:include-edges", ()).update(' /tmp/tmp.CtjpuH1Kzi/typst-tip/typsphinx.typ | uv run python /tmp/tmp.CtjpuH1Kzi/p7204_edges.py
1 1 1 1 1
```
`EDGES_PER_PAGE_TIP = 1 1 1 1 1`, in page order configuration, builders, templates, basic,
advanced, each `S#0>P` with `S` the page's section index (`user_guide/index` for the first three,
`examples/index` for the last two — asserted by the parsing script itself, which raises on any
other shape).

`LANG=C LC_ALL=C diff -rq` between the two output trees:
```
$ LANG=C LC_ALL=C diff -rq /tmp/tmp.CtjpuH1Kzi/typst-base /tmp/tmp.CtjpuH1Kzi/typst-tip
Files .../typst-base/.doctrees/api/index.doctree and .../typst-tip/.doctrees/api/index.doctree differ
Files .../typst-base/.doctrees/changelog.doctree and .../typst-tip/.doctrees/changelog.doctree differ
Files .../typst-base/.doctrees/contributing.doctree and .../typst-tip/.doctrees/contributing.doctree differ
Files .../typst-base/.doctrees/environment.pickle and .../typst-tip/.doctrees/environment.pickle differ
Files .../typst-base/.doctrees/examples/advanced.doctree and .../typst-tip/.doctrees/examples/advanced.doctree differ
Files .../typst-base/.doctrees/examples/basic.doctree and .../typst-tip/.doctrees/examples/basic.doctree differ
Files .../typst-base/.doctrees/examples/index.doctree and .../typst-tip/.doctrees/examples/index.doctree differ
Files .../typst-base/.doctrees/index.doctree and .../typst-tip/.doctrees/index.doctree differ
Files .../typst-base/.doctrees/installation.doctree and .../typst-tip/.doctrees/installation.doctree differ
Files .../typst-base/.doctrees/quickstart.doctree and .../typst-tip/.doctrees/quickstart.doctree differ
Files .../typst-base/.doctrees/user_guide/builders.doctree and .../typst-tip/.doctrees/user_guide/builders.doctree differ
Files .../typst-base/.doctrees/user_guide/configuration.doctree and .../typst-tip/.doctrees/user_guide/configuration.doctree differ
Files .../typst-base/.doctrees/user_guide/index.doctree and .../typst-tip/.doctrees/user_guide/index.doctree differ
Files .../typst-base/.doctrees/user_guide/output_layout.doctree and .../typst-tip/.doctrees/user_guide/output_layout.doctree differ
Files .../typst-base/.doctrees/user_guide/templates.doctree and .../typst-tip/.doctrees/user_guide/templates.doctree differ
Files .../typst-base/contributing.typ and .../typst-tip/contributing.typ differ
Files .../typst-base/index.typ and .../typst-tip/index.typ differ
```
`TYPST_DIFF_FILES` (relative to each output root, space-separated): `index.typ contributing.typ`
plus every `.doctrees/*.doctree` and `.doctrees/environment.pickle` (the doctree cache necessarily
differs because the pickled environment records the base's five extra toctree-inclusion relations
that the tip's edit removes). `index.typ` and `contributing.typ` are the two product-tree `.typ`
files that differ — expected, since `contributing.typ` carries 72-03's `tox -e linkcheck` line and
`index.typ` carries the dead-include removal. `user_guide/index.typ` and `examples/index.typ`,
which fire the real, non-dead includes, are absent from this list (untouched).

## SC#4 HTML and Typst verdicts

`SC4_HTML_VERDICT = MET`: the tip counts are `1 1 1 1 1`, the parents are as stated
(`user_guide/index.html` ×3, `examples/index.html` ×2), the control is 1, and the base counts are
each 2 (at least 2).

`SC4_TYPST_VERDICT = MET`: `ROOT_DEAD_INCLUDES_TIP = 0`, `ROOT_DEAD_INCLUDES_BASE = 5` (at least 1),
`SECTION_GUARDS_TIP = 5`, `EDGES_PER_PAGE_TIP = 1 1 1 1 1`.

BASE_CONSOLE_SELECTING_EXAMPLES_BASIC = index
BASE_CONSOLE_SELECTING_EXAMPLES_ADVANCED = index
BASE_HTML_PARENT_EXAMPLES_BASIC = examples/index
BASE_HTML_PARENT_EXAMPLES_ADVANCED = examples/index
TIP_HTML_PARENT_EXAMPLES_BASIC = examples/index
TIP_HTML_PARENT_EXAMPLES_ADVANCED = examples/index
TIP_ANCESTOR_PARENT_EXAMPLES_BASIC = examples/index
TIP_ANCESTOR_PARENT_EXAMPLES_ADVANCED = examples/index
TYPST_PARENT_EXAMPLES_BASIC = examples/index
TYPST_PARENT_EXAMPLES_ADVANCED = examples/index
DIVERGENCE_SURVIVES = no
DIVERGENCE_TODO = none
SC4_VERDICT = MET

## Parent notions

For each of the base and tip HTML builds of pair `SC3_PAIR = 1`, unpickled
`<out>/.doctrees/environment.pickle` with `uv run python -c`. For each of the six pages (the five
plus the `user_guide/output_layout` control), printed (a) the relations parent
(`env.collect_relations()[d][0]`) and (b) the immediate ancestor (the second element of
`sphinx.environment.adapters.toctree._get_toctree_ancestors(env.toctree_includes, d)`).

```python
import pickle, sys
from sphinx.environment.adapters.toctree import _get_toctree_ancestors as anc
pages = ["user_guide/configuration", "user_guide/builders", "user_guide/templates",
         "examples/basic", "examples/advanced", "user_guide/output_layout"]
env = pickle.load(open(sys.argv[1], "rb"))
rel = env.collect_relations()
for d in pages:
    a = rel[d][0]
    chain = list(anc(env.toctree_includes, d))
    b = chain[1] if len(chain) > 1 else None
    print(f"{d}\t{a}\t{b}")
```

Run against `html-base/.doctrees/environment.pickle`:
```
user_guide/configuration	user_guide/index	user_guide/index
user_guide/builders	user_guide/index	user_guide/index
user_guide/templates	user_guide/index	user_guide/index
examples/basic	examples/index	None
examples/advanced	examples/index	None
user_guide/output_layout	user_guide/index	user_guide/index
```

Run against `html-tip/.doctrees/environment.pickle`:
```
user_guide/configuration	user_guide/index	user_guide/index
user_guide/builders	user_guide/index	user_guide/index
user_guide/templates	user_guide/index	user_guide/index
examples/basic	examples/index	examples/index
examples/advanced	examples/index	examples/index
user_guide/output_layout	user_guide/index	user_guide/index
```

Column (c) is the base console `selecting:` token from `p7204_html-base.out` (from the `## HTML
pair 1` transcript above), `none` where no such message exists; at the tip no `multiple toctrees`
message exists for any page, so (c) is `none` throughout the tip table. Column (d) is the Typst
edge parent: the section before `#0>` in the matching edge of each build's include-edges state
(byte-identical between base and tip, per `## Typst pair` above).

**Base build**, columns page / (a) / (b) / (c) / (d):

| page | (a) relations parent | (b) ancestor parent | (c) console `selecting:` | (d) Typst edge parent |
|---|---|---|---|---|
| user_guide/configuration | user_guide/index | user_guide/index | user_guide/index | user_guide/index |
| user_guide/builders | user_guide/index | user_guide/index | user_guide/index | user_guide/index |
| user_guide/templates | user_guide/index | user_guide/index | user_guide/index | user_guide/index |
| examples/basic | examples/index | None | index | examples/index |
| examples/advanced | examples/index | None | index | examples/index |
| user_guide/output_layout | user_guide/index | user_guide/index | none | user_guide/index |

**Tip build**, same columns:

| page | (a) relations parent | (b) ancestor parent | (c) console `selecting:` | (d) Typst edge parent |
|---|---|---|---|---|
| user_guide/configuration | user_guide/index | user_guide/index | none | user_guide/index |
| user_guide/builders | user_guide/index | user_guide/index | none | user_guide/index |
| user_guide/templates | user_guide/index | user_guide/index | none | user_guide/index |
| examples/basic | examples/index | examples/index | none | examples/index |
| examples/advanced | examples/index | examples/index | none | examples/index |
| user_guide/output_layout | user_guide/index | user_guide/index | none | user_guide/index |

At the base, `examples/basic`/`examples/advanced` show column (b) as `None` — not a script bug: at
base, `toctree_includes["index"]` lists `examples/basic`/`examples/advanced` directly (in addition
to `toctree_includes["examples/index"]` also listing them), and `_get_toctree_ancestors`'
last-assignment parent map (iterating `toctree_includes.items()` in key order
`['examples/index', 'index', 'user_guide/index']`) lets the direct `index` assignment overwrite the
`examples/index` one, mapping `parent['examples/basic'] = 'index'` — but `'index'` (the root) is
itself never a *value* in that map (nothing lists it as a child), so the ancestor chain terminates
after appending only the docname itself and column (b) has no second element. At the tip, with the
direct root entries removed, only `toctree_includes["examples/index"]` assigns the parent, giving
`examples/index` for column (b) — matching (a) and (d).

Quoted, with file and line numbers (installed Sphinx 9.1.0, this worktree's `.venv`):

`_check_toc_parents` logs `max(parents)` and feeds nothing (`sphinx/environment/__init__.py:942-960`):
```python
942:def _check_toc_parents(toctree_includes: dict[str, list[str]]) -> None:
943:    toc_parents: dict[str, list[str]] = {}
944:    for parent, children in toctree_includes.items():
945:        for child in children:
946:            toc_parents.setdefault(child, []).append(parent)
947:
948:    for doc, parents in sorted(toc_parents.items()):
949:        if len(parents) > 1:
950:            logger.info(
951:                __(
952:                    'document is referenced in multiple toctrees: %s, selecting: %s <- %s'
953:                ),
954:                parents,
955:                max(parents),
956:                doc,
957:                location=doc,
958:                type='toc',
959:                subtype='multiple_toc_parents',
960:            )
```
This function only calls `logger.info(...)` — its `max(parents)` computation is never returned or
stored anywhere; it feeds nothing else in the pipeline.

`collect_relations` is a pre-order traversal from `root_doc`, and the HTML builder reads its
parent/prev/next from it (`sphinx/environment/__init__.py:778-795`,
`sphinx/builders/html/__init__.py:492`):
```python
778:    def collect_relations(self) -> dict[str, list[str | None]]:
779:        traversed: set[str] = set()
780:
781:        relations = {}
782:        docnames = _traverse_toctree(
783:            traversed, None, self.config.root_doc, self.toctree_includes
784:        )
...
793:        relations[docname] = [parent, prev_doc, None]
794:
795:        return relations
```
```python
492:        self.relations = self.env.collect_relations()
```

`_get_toctree_ancestors` builds a last-assignment parent map
(`sphinx/environment/adapters/toctree.py:562-575`):
```python
562:def _get_toctree_ancestors(
563:    toctree_includes: dict[str, list[str]],
564:    docname: str,
565:) -> Set[str]:
566:    parent: dict[str, str] = {}
567:    for p, children in toctree_includes.items():
568:        parent |= dict.fromkeys(children, p)
569:    ancestors: list[str] = []
570:    d = docname
571:    while d in parent and d not in ancestors:
572:        ancestors.append(d)
573:        d = parent[d]
574:    return dict.fromkeys(ancestors).keys()
```

## Divergence disposition

At the tip, for all six pages, (a) `collect_relations()` and (b) `_get_toctree_ancestors` both
equal (d) the Typst edge parent: `user_guide/index` for the three User Guide pages and
`examples/index` for both Examples pages. `DIVERGENCE_SURVIVES = no`. `DIVERGENCE_TODO = none` — no
todo is filed; `.planning/todos/pending/2026-09-13-html-and-typst-toctree-parents-diverge-after-dedup.md`
does not exist.

The 2026-08-16 observation, "Sphinx HTML selected `index`", was read from the console `selecting:`
token (column (c)) — which `_check_toc_parents` computes as `max(parents)` and only logs; it is
neither `collect_relations()`'s relation (a) nor `_get_toctree_ancestors`'s chain (b), both of which
the HTML builder (and, per `## Typst pair`, the Typst edge map) actually use. At the tip that
console token no longer exists at all (`MULTI_TOCTREE_TIP = 0`, no `selecting:` message for any
page).

## SC#4 verdict

`SC4_HTML_VERDICT = MET` and `SC4_TYPST_VERDICT = MET` (from `## SC#4 HTML and Typst verdicts`
above), and the divergence disposition is recorded (`DIVERGENCE_SURVIVES = no`).

`SC4_VERDICT = MET`

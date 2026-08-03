# Phase 42, Plan 01 — GATE-01 Evidence (TBL-03, classic compile-fatal RED)

Discharges ROADMAP SC#1 (minimal reproduction + observed `depart_table` ids) and SC#5's RED half
(the fixture and test module committed while the bug is still live, `git status --porcelain
typsphinx/` empty at that commit). The GREEN half is owned by plan 42-04 and recorded in
`42-GATE-EVIDENCE-04.md`; the caption-less byte-invariance proof (D-04) is owned by plan 42-05.

---

## 1. Recording commit

**Command:** `git rev-parse HEAD`

```
d28f2c8bcdf8aee49ab82b1d883145a4036acefc
```

**Command:** `git log -1 --oneline`

```
d28f2c8 test(42-01): record classic RED for captioned-table propagated-target drop
```

**Command:** `git status --porcelain typsphinx/`

```
(no output)
```

`typsphinx/` is byte-unmodified at this commit. Task 1 (the fixture) and Task 2 (this test module)
touch only `tests/fixtures/captioned_table_propagated_target_render_gate/`,
`tests/test_captioned_table_propagated_target_render_gate.py`, and this evidence file. No file
under `typsphinx/` is changed by either commit — the RED below is recorded against the unfixed
`depart_table`.

---

## 2. The minimal reproduction (SC#1)

**Shape A rST, verbatim** (from
`tests/fixtures/captioned_table_propagated_target_render_gate/index.rst`):

```rst
Target plus a named captioned table
------------------------------------------------------

.. _tbl-target:

.. table:: TBLTGTNAMEDSENTINEL
   :name: tbl-name

   ========  ========
   Column A  Column B
   ========  ========
   Cell      Cell
   ========  ========
```

...plus, in the "References back to the propagated targets" section further down the same
document:

```rst
- :ref:`first target link text <tbl-target>`
```

**Command:**

```
uv run python -m sphinx -b typstpdf -q -E tests/fixtures/captioned_table_propagated_target_render_gate <build>
```

**Exit status:** `2`

**Verbatim stderr:**

```
Typst compilation failed at <build>/index.typ: TypstError: label `<index:tbl-target>` does not exist in the document
ERROR: Failed to compile <build>/index.typ: Typst compilation failed: TypstError: label `<index:tbl-target>` does not exist in the document
Location: <build>/index.typ
Details: label `<index:tbl-target>` does not exist in the document

Extension error!

Versions
========

* Platform:         linux; (Linux-6.18.40-x86_64-with-glibc2.42)
* Python version:   3.13.13 (CPython)
* Sphinx version:   9.1.0
* Docutils version: 0.22.4
* Jinja2 version:   3.1.6
* Pygments version: 2.20.0

Last Messages
=============

    環境データを保存中...
    完了
    整合性をチェック中...
    完了
    preparing documents...
    Template written to <build>/_template.typ
    done
    writing output... [index]
     done
    Compiling 1 master document(s) to PDF...

Loaded Extensions
=================

* sphinx.ext.mathjax (9.1.0)
* alabaster (1.0.0)
* sphinxcontrib.applehelp (2.0.0)
* sphinxcontrib.devhelp (2.0.0)
* sphinxcontrib.htmlhelp (2.1.0)
* sphinxcontrib.serializinghtml (2.0.0)
* sphinxcontrib.qthelp (2.0.0)
* typsphinx (0.7.0)

Traceback
=========

      File "typsphinx/builder.py", line 965, in finish
        raise ExtensionError(
            f"typstpdf: {len(failures)} master document(s) failed: {summary}"
        )
    sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: label `<index:tbl-target>` does not exist in the document
    Location: <build>/index.typ
    Details: label `<index:tbl-target>` does not exist in the document


The full traceback has been saved in:
/tmp/sphinx-err-02kcw3h4.log

To report this error to the developers, please open an issue at <https://github.com/sphinx-doc/sphinx/issues/>. Thanks!
次期バージョンでのエラーメッセージ改善のために、ユーザーエラーの場合にも報告してください。
```

(paths shortened from the real absolute tmp path for readability; the real command was run against
`tests/fixtures/captioned_table_propagated_target_render_gate` with an output directory under this
session's scratchpad).

This is the real fatal reported for Shape A — `label \`<index:tbl-target>\` does not exist in the
document` — matching the todo's original report and the discuss-phase throwaway measurement, now
recorded as this phase's own admissible evidence.

---

## 3. The observed ids at `depart_table` call time (SC#1)

**Method:** a THROWAWAY probe script (pasted verbatim below; NOT committed to the repository — it
lives only under this session's scratchpad directory) monkeypatches
`typsphinx.translator.TypstTranslator.depart_table` to print `node["ids"]` and `node["names"]`
before delegating to the original method, then drives a real `-b typst` build of this phase's fixture
through Sphinx's own Python entry point (`sphinx.application.Sphinx`).

**Probe script source, verbatim:**

```python
"""
THROWAWAY probe (Phase 42, 42-GATE-EVIDENCE-01.md section 3) -- NOT committed
to the repository. Wraps TypstTranslator.depart_table to print node["ids"]
and node["names"] observed at call time, then drives a real -b typst build
of the captioned_table_propagated_target_render_gate fixture through
Sphinx's own Python entry point.
"""

import sys

from sphinx.application import Sphinx

from typsphinx.translator import TypstTranslator

_original_depart_table = TypstTranslator.depart_table


def _wrapped_depart_table(self, node):
    print(
        f"PROBE depart_table ids={node.get('ids')} names={node.get('names')}",
        file=sys.stderr,
    )
    return _original_depart_table(self, node)


TypstTranslator.depart_table = _wrapped_depart_table

src = "tests/fixtures/captioned_table_propagated_target_render_gate"
out = "<scratchpad>/t42-probe-build"
doctree = out + "/.doctrees"

app = Sphinx(
    srcdir=src,
    confdir=src,
    outdir=out,
    doctreedir=doctree,
    buildername="typst",
    freshenv=True,
)
app.build()
```

**Command:** `uv run python <scratchpad>/probe_depart_table_ids.py`

**Verbatim probe output (stderr, `PROBE` lines only, in emission order), plus the final `build
succeeded.` line:**

```
PROBE depart_table ids=['tbl-name', 'tbl-target'] names=['tbl-name', 'tbl-target']
PROBE depart_table ids=['id1', 'tbl-target-noname'] names=['tbl-target-noname']
PROBE depart_table ids=['tbl-name-li', 'tbl-target-li'] names=['tbl-name-li', 'tbl-target-li']
PROBE depart_table ids=['tbl-name-two', 'tbl-target-b', 'tbl-target-a'] names=['tbl-name-two', 'tbl-target-b', 'tbl-target-a']
PROBE depart_table ids=[] names=[]
build succeeded.
```

**Per-shape observed ids/names table:**

| Shape | `node["ids"]` (observed) | `node["names"]` (observed) |
|-------|---------------------------|------------------------------|
| A — target + `:name:`-carrying table | `['tbl-name', 'tbl-target']` | `['tbl-name', 'tbl-target']` |
| B — target + table with no `:name:` | `['id1', 'tbl-target-noname']` | `['tbl-target-noname']` |
| C — target + table inside a list item | `['tbl-name-li', 'tbl-target-li']` | `['tbl-name-li', 'tbl-target-li']` |
| D — two consecutive targets before one table | `['tbl-name-two', 'tbl-target-b', 'tbl-target-a']` | `['tbl-name-two', 'tbl-target-b', 'tbl-target-a']` |
| Control — caption-less table, no preceding target | `[]` | `[]` |

**Chained-target ordering (Shape D) — explicit callout:** the two consecutive standalone targets are
authored in the fixture's `index.rst` in the order `.. _tbl-target-a:` then `.. _tbl-target-b:` (`a`
before `b`, source order). The observed `node["ids"]` for that table is
`['tbl-name-two', 'tbl-target-b', 'tbl-target-a']` — **`tbl-target-b` arrives before
`tbl-target-a`, i.e. the two propagated chained-target ids arrive REVERSED relative to their
source order.** This is why every assertion in `tests/test_captioned_table_propagated_target_render_gate.py`
matches Shape D's two anchors by NAME (`[#metadata(none) <index:tbl-target-a>]` and
`[#metadata(none) <index:tbl-target-b>]` independently) rather than by list position.

**Shape B note:** `ids[0]` is `id1`, a docutils auto-generated id (no `:name:` option was given, so
docutils supplies its own id as the first entry and the human-authored `.. _tbl-target-noname:` id
lands in `ids[1:]`). Per D-01/the plan's own prohibition, no test assertion names `id1` — its exact
spelling is unstable across unrelated document changes; only the human-authored
`tbl-target-noname` id is asserted.

**Control table note:** `ids=[]`/`names=[]` confirms the caption-less control table carries no
propagated id at all (no standalone target precedes it in the fixture), consistent with it being the
zero point on the zero/one/many propagated-ids axis.

---

## 4. The RED (SC#5)

**Command:** `uv run pytest tests/test_captioned_table_propagated_target_render_gate.py -v`

**Collected:** 9 items (all 9 test methods executed — zero skips; `TYPST_AVAILABLE` is `True` in
this environment, confirmed by the skip guard not firing).

**Per-test outcome:**

```
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_compile_clean FAILED [ 11%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_shape_a_named_target_anchor FAILED [ 22%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_shape_b_noname_target_anchor FAILED [ 33%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_shape_c_list_item_target_anchor FAILED [ 44%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_shape_d_two_consecutive_targets_anchor FAILED [ 55%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_no_duplicate_label_definition PASSED [ 66%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_no_dangling_same_document_reference FAILED [ 77%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_caption_less_control_table_not_figure_wrapped PASSED [ 88%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_pdf_magic_bytes FAILED [100%]

========================= 7 failed, 2 passed in 0.35s ==========================
```

**7 of 9 tests are RED**: `test_compile_clean`, `test_shape_a_named_target_anchor`,
`test_shape_b_noname_target_anchor`, `test_shape_c_list_item_target_anchor`,
`test_shape_d_two_consecutive_targets_anchor`, `test_no_dangling_same_document_reference`,
`test_pdf_magic_bytes`. **2 of 9 already pass pre-fix**, as expected, because they assert properties
the bug does not affect: `test_no_duplicate_label_definition` (the bug DROPS anchors, it never
duplicates one) and `test_caption_less_control_table_not_figure_wrapped` (the `kind: table` count is
unaffected by whether the propagated remainder anchor is emitted or discarded).

**Verbatim assertion text — the core compile fatal** (`test_compile_clean`):

```
AssertionError: sphinx-build -b typstpdf failed:
...
stderr: Typst compilation failed at /tmp/pytest-of-yuta/pytest-690/captioned_table_propagated_target0/index.typ: TypstError: label `<index:tbl-target>` does not exist in the document
ERROR: Failed to compile /tmp/pytest-of-yuta/pytest-690/captioned_table_propagated_target0/index.typ: Typst compilation failed: TypstError: label `<index:tbl-target>` does not exist in the document
Location: /tmp/pytest-of-yuta/pytest-690/captioned_table_propagated_target0/index.typ
Details: label `<index:tbl-target>` does not exist in the document
...
assert 2 == 0
```

The literal `does not exist in the document` is present, as required.

**Verbatim assertion text — the per-shape anchor absences:**

```
E       AssertionError: The propagated target before the named captioned table did not emit an <index:tbl-target> anchor:
...
E       AssertionError: The propagated target before the unnamed captioned table did not emit an <index:tbl-target-noname> anchor:
...
E       AssertionError: The propagated target before the list-item-nested captioned table did not emit an <index:tbl-target-li> anchor:
...
E       AssertionError: The first of two consecutive targets before the captioned table did not emit an <index:tbl-target-a> anchor:
```

**Verbatim assertion text — the generic dangling-reference sweep** (`test_no_dangling_same_document_reference`):

```
AssertionError: Same-document references with no matching label definition (dangling labels): ['index:tbl-target', 'index:tbl-target-a', 'index:tbl-target-b', 'index:tbl-target-li', 'index:tbl-target-noname']
```

All five propagated ids from D-01's four shapes (Shape D contributes both `tbl-target-a` and
`tbl-target-b`) are reported dangling — exactly the five ids the observed-ids table in § 3 shows are
missing from `_emit_id_anchors`' effective output pre-fix.

**Verbatim assertion text — the PDF magic-byte check** (`test_pdf_magic_bytes`):

```
AssertionError: index.pdf was not produced -- typst.compile() aborted, most likely on a dangling label:
...
assert False
 +  where False = exists()
 +    where exists = PosixPath('/tmp/pytest-of-yuta/pytest-690/captioned_table_propagated_target0/index.pdf').exists
```

**Non-regression control** (the existing captioned-table gate, re-run at this same commit):

```
$ uv run pytest tests/test_pdf_render_gate.py -q
31 passed in 6.32s
```

The already-GREEN `TestCaptionedTableRenderGate` class (TBL-01/TBL-02, unrelated to this phase's
new fixture) is unaffected — confirming the new fixture was correctly kept out of
`tests/fixtures/captioned_table_render_gate/` (D-01 discretion / the plan's own contamination-risk
rationale).

`git status --porcelain typsphinx/` is empty at this same commit (re-confirmed, § 1 above).

---

## 5. Verdict

| Success criterion | Discharged by | Status |
|--------------------|----------------|--------|
| SC#1 — minimal reproduction, verbatim Typst error text, observed `node["ids"]`/`node["names"]` for all four D-01 shapes | § 2 (reproduction + verbatim stderr) and § 3 (per-shape observed-ids table + reversed chained-target callout) | **Discharged** |
| SC#5 — RED half: fixture + module committed while the bug is live, `git status --porcelain typsphinx/` empty at that commit, verbatim failure output recorded | § 1 (recording commit, empty production-source status) and § 4 (verbatim RED, 7/9 failing with the expected signature, 2/9 already-passing as expected) | **Discharged (RED half)** |

**Not owned by this evidence file:**

- The GREEN half of SC#5 (the same nine tests passing post-fix) is owned by plan 42-04 and recorded
  in `42-GATE-EVIDENCE-04.md`.
- The caption-less path's byte-invariance proof (D-04, an empty two-worktree `diff`) is owned by
  plan 42-05.

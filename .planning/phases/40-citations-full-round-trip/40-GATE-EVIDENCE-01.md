# Phase 40, Plan 01 — GATE-01 Evidence (Classic Compile-Fatal RED)

**Recorded against commit:** `3c09d79` (`test(40-01): add .typ-string and real-compile half of
citation gate`), built directly on `02fe29f` (`test(40-01): add two-document citation render-gate
fixture`) and `ccb37b2` (`docs(40): create phase plan`, the phase-start commit). `typsphinx/` is
byte-identical between `ccb37b2` and `3c09d79` — see "No source changes" below — so all three
commits equally qualify as "the untouched translator" this evidence is recorded against.

This plan touches only `tests/` and `.planning/`. No file under `typsphinx/` is modified.

---

## 1. Fixture source, verbatim

### `tests/fixtures/citation_render_gate/conf.py`

```python
"""Sphinx config for the citation render-gate fixture (Phase 40, GATE-01).

Root cause this fixture reproduces: ``docutils.nodes.citation`` and
``docutils.nodes.label`` have no translator handler today (measured
2026-08-02; see 40-CONTEXT.md/40-RESEARCH.md). A real
``sphinx-build -b typst`` build falls through to ``unknown_visit`` /
``unknown_departure`` for both node types -- logging
``WARNING: unknown node type: <citation ...>`` and
``WARNING: unknown node type: <label ...>`` -- and the label's bare Text
child juxtaposes against the citation's paragraph body with no separator:
``text("Krizhevsky2012")par({text("Krizhevsky, A. ...")})``. Compiling that
fragment with a real ``typst.compile()`` raises the classic
``TypstError: expected semicolon or line break``.

``index`` must be the master document (not ``second``) because that fatal
only fires inside ``TypstPDFBuilder.finish()``'s real compile step -- a
``-b typst`` build of a non-master document writes the same invalid ``.typ``
but never compiles it.
"""

project = "Citation Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build
# path where the "expected semicolon or line break" fatal is observable.
typst_documents = [
    ("index", "index", "Citation Render Gate", "Test Author"),
]
```

### `tests/fixtures/citation_render_gate/index.rst`

```rst
Citation Render Gate
=====================

.. toctree::
   :maxdepth: 1

   second

Citing Sites
------------

.. Requirement CIT-03 (SC#3). FORWARD reference -- Krizhevsky2012 is
   defined below in the References section, after this first use.
   DEFECT CASE pre-fix (citation/label nodes unhandled -- the classic
   compile fatal).

The CNN architecture traces its origin to [Krizhevsky2012]_.

.. Requirement CIT-04 / D-03 multi-marker shape. A second citation of the
   SAME key gives that definition two entries in backrefs, proving the
   ``(1,2)`` back-reference marker shape.

The same paper is cited a second time here: [Krizhevsky2012]_.

.. Requirement CIT-04 / D-03 single-marker shape. Exactly one citing site
   means the label text itself becomes the back-link, with no ``(1)``
   marker.

A different paper is cited exactly once: [Solo1998]_.

.. Requirement D-10a. Cross-document citing site -- Cross2019 is defined
   ONLY in second.rst. This paragraph must not also define anything.

This paragraph cites a key defined in another document: [Cross2019]_.

.. Requirement D-10b. Same2020 is a duplicate key defined in BOTH
   documents. Sphinx's citation domain resolves a duplicate key
   last-registered-wins across the whole build, so which document this
   reference lands in is decided by Sphinx and must never be hard-coded
   in an assertion.

This paragraph cites the duplicate key: [Same2020]_.

.. Requirement T-40-03. Nosuchkey has no definition anywhere -- the
   dangling-citing-reference case. Sphinx itself warns "citation not
   found" and leaves the reference unresolved before the translator runs,
   so the expected emission is plain text and no link call.

This paragraph cites an undefined key: [Nosuchkey]_.

Concat Protocol
----------------

.. Requirement SC#5 code-mode concat boundary. A definition-list TERM is
   one of this translator's five concat contexts (``_in_term``) --
   adjacent inline expressions in the term are ``+``-joined. The citing
   reference to Concat2000 sits inside that term, next to plain text.

Concat Term [Concat2000]_
    A short definition body for the concat-protocol boundary case.

Nested Protocol
-----------------

.. Requirement SC#5 list-item boundary; RESEARCH's independently
   reproduced second failure mode -- this construct fails today with a
   DIFFERENT fatal ("label ... does not exist in the document") than the
   top-level syntax fatal.

- Item one, a plain paragraph.

- Item two contains a citation list:

  .. [Nested2021] CITNESTEDSENTINEL A citation nested inside a list
     item's body.

  Referenced here as [Nested2021]_ within the same item.

References
----------

.. Requirement CIT-01 / CIT-02 / D-05. Five consecutive citation
   definitions form ONE run/grid. The comment between the second and
   third definitions below emits nothing and must NOT break the run --
   all five must still land in one grid.

.. [Krizhevsky2012] CITORDERALPHA Krizhevsky, A., Sutskever, I., &
   Hinton, G. E. (2012). ImageNet classification with deep convolutional
   neural networks. Advances in neural information processing systems,
   25. This entry body is padded further with extra prose so it wraps
   onto at least a second visual line when rendered inside a narrow grid
   column, exercising CIT-02's continuation-line hanging-indent
   measurement against a real, multi-line reference entry.

.. [Solo1998] CITORDERBRAVO Solo, J. (1998). A single-line reference
   entry.

.. An RST comment between two citation definitions. Comments emit
   nothing and must not break the D-05 run -- these five definitions
   must still land in ONE grid, not two.

.. [Never1999] CITORDERCHARLIE Never, N. (1999). An uncited reference
   entry -- D-07's plain, non-linked label case. Sphinx will log a
   "is not referenced" warning for this entry; that warning is expected.

.. [Same2020] CITORDERDELTA Same, S. (2020). The duplicate-key entry,
   defined again in second.rst -- D-10's definition-side namespacing
   case.

.. [Concat2000] CITORDERECHO Concat, C. (2000). A "quoted" reference with
   a café character, exercising the existing escape_typst_string path.

Run Break
----------

.. Requirement D-06. A real paragraph between two citation definitions
   breaks the run into two separate, independently-aligned grids.

.. [Break2021] CITBREAKONESENTINEL Break, O. (2021). First half of the
   broken run.

This paragraph breaks the citation run per D-06.

.. [Break2022] CITBREAKTWOSENTINEL Break, T. (2022). Second half of the
   broken run, in its own independently-aligned grid.
```

### `tests/fixtures/citation_render_gate/second.rst`

```rst
Second Document
=================

.. Requirement D-08 / D-10a. Cross-document citing site: cites
   Krizhevsky2012, defined in index.rst. Per D-08 this gets a working
   forward link and NO back-reference in index.rst's definition --
   docutils' own ``backrefs`` are same-document only.

This document cites [Krizhevsky2012]_, which is defined in the master
document.

References
----------

.. [Cross2019] Cross, C. (2019). Cited only from index.rst -- D-10a's
   cross-document citing-site proof.

.. [Same2020] CITSECONDDOCSENTINEL Same, S. (2020). The duplicate key's
   second definition -- D-10's definition-side namespacing case
   (``index:same2020`` vs ``second:same2020``, both non-colliding).
```

---

## 2. Verbatim pre-fix emitted `.typ` fragment for a citation

From a real `-b typst` build of the fixture above, the `References` section's first entry
(`Krizhevsky2012`) emits (verbatim, `index.typ`):

```typst
text("Krizhevsky2012")par({text("CITORDERALPHA Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). ImageNet classification with deep convolutional neural networks. Advances in neural information processing systems, 25. This entry body is padded further with extra prose so it wraps onto at least a second visual line when rendered inside a narrow grid column, exercising CIT-02’s continuation-line hanging-indent measurement against a real, multi-line reference entry.")})
```

Two adjacent code-mode expressions with **no separator between them**: the citation's `label`
child renders as a bare `text("Krizhevsky2012")` statement (no handler exists for `label`, so its
own Text child reaches `visit_Text` positionally), immediately followed on the SAME line by the
citation's `paragraph` child rendering as `par({...})` (no handler exists for `citation` either, so
`unknown_visit`/`unknown_departure` fire around it while its children render through the normal
visitor chain). This is the classic GATE-01 defect shape, byte-identical in structure to
`40-CONTEXT.md`'s own same-day measurement.

---

## 3. Verbatim exception text — the classic syntax fatal (top-level citation)

Command:

```
$ uv run python -c "
import subprocess, sys
result = subprocess.run(
    [sys.executable, '-m', 'sphinx', '-b', 'typstpdf',
     'tests/fixtures/citation_render_gate', '/tmp/cit40pdf2'],
    capture_output=True, text=True,
)
print('RETURNCODE:', result.returncode)
print(result.stderr[-800:])
"
```

```
RETURNCODE: 2
...
Typst compilation failed at /tmp/cit40pdf2/index.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile /tmp/cit40pdf2/index.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: /tmp/cit40pdf2/index.typ
Details: expected semicolon or line break
...
Traceback
=========

      File "/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a06324b680cf30b6f/typsphinx/builder.py", line 965, in finish
        raise ExtensionError(
            f"typstpdf: {len(failures)} master document(s) failed: {summary}"
        )
    sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: expected semicolon or line break
    Location: /tmp/cit40pdf2/index.typ
    Details: expected semicolon or line break
```

Also independently reproduced via a direct `typst.compile()` call against the emitted `index.typ`:

```
$ uv run python -c "
import typst
typst.compile('/tmp/cit40fix/index.typ')
"
Traceback (most recent call last):
  ...
typst.TypstError: expected semicolon or line break
```

---

## 4. Verbatim exception text — the SECOND, independently-reproduced failure mode (list-item nesting)

RESEARCH (`40-RESEARCH.md` § "Common Pitfalls", Pitfall 2) found that nesting a citation inside a
`list_item` fails with a **different** fatal — a semantic-pass "label does not exist" error rather
than the top-level syntax fatal — because the preceding sibling paragraph's dangling
`list_item_needs_separator` state happens to insert a newline before the label's bare `text(...)`
statement, which is enough for Typst's PARSER to accept the file; the abort only occurs later, at
the semantic pass, when the citing reference's `link(<index:nested2021>)` call resolves to a label
that was never attached (no citation handler exists to emit the definition's own anchor).

This session independently re-verified that finding by isolating the list-item-nested construct
into its OWN fixture (no other citation defect present, so Typst's parser can get past the syntax
stage and reach the semantic pass):

**Isolated probe `index.rst`** (minimal, no References section, no top-level syntax defect):

```rst
Isolated Nested Citation Probe
================================

- Item one, a plain paragraph.

- Item two contains a citation list:

  .. [Nested2021] CITNESTEDSENTINEL A citation nested inside a list
     item's body.

  Referenced here as [Nested2021]_ within the same item.
```

**Emitted `index.typ` fragment for the list item** (verbatim, `-b typst`, no top-level defect
elsewhere in this isolated probe):

```typst
list({
parbreak()

text("Item one, a plain paragraph.")
}, {
parbreak()

text("Item two contains a citation list:")
text("Nested2021")
parbreak()

text("CITNESTEDSENTINEL A citation nested inside a list item’s body.")
parbreak()

text("Referenced here as ")
link(<index:nested2021>, text("[Nested2021]"))
text(" within the same item.")
})
```

**Verbatim exception, real `-b typstpdf` subprocess run against this isolated probe:**

```
RETURNCODE: 2
...
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: label `<index:nested2021>` does not exist in the document
    Location: /tmp/cit40isolate_pdf/index.typ
    Details: label `<index:nested2021>` does not exist in the document
```

Also independently reproduced via a direct `typst.compile()` call:

```
$ uv run python -c "
import typst
typst.compile('/tmp/cit40isolate_build/index.typ')
"
typst.TypstError: label `<index:nested2021>` does not exist in the document
```

**These are two DISTINCT pre-fix failure shapes**, confirmed this session:

| Construct | Failure stage | Verbatim message |
|---|---|---|
| Top-level citation (References section) | Typst PARSER (syntax) | `expected semicolon or line break` |
| Citation nested inside a `list_item` (Nested Protocol section) | Typst semantic pass (label resolution) | `` label `<index:nested2021>` does not exist in the document `` |

The full fixture's `index.typ` (both defects present simultaneously) only ever surfaces the FIRST
one — the top-level syntax fatal aborts the Typst parser before it ever reaches the semantic pass
where the list-item's dangling label would be found — which is exactly why this isolated,
single-defect probe was necessary to independently capture the second shape.

---

## 5. `uv run pytest tests/test_citation_render_gate.py -v` — verbatim RED

Command: `uv run pytest tests/test_citation_render_gate.py -v`

Collection and per-test outcome (verbatim):

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a06324b680cf30b6f
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 9 items

tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_link_citing_site_targets_match_definition_anchors_and_own_ids FAILED [ 11%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_namespace_duplicate_key_is_document_scoped FAILED [ 22%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_separator_paragraph_concat_and_list_item_boundaries FAILED [ 33%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_uncited_entry_renders_plain_label_in_shared_grid FAILED [ 44%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_references_run_and_run_break_grid_counts FAILED [ 55%]
tests/test_citation_render_gate.py::TestCitationRenderGateRealCompile::test_citation_gate_compiles_via_real_typst_compile FAILED [ 66%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_layout_hanging_indent_and_widest_label_alignment FAILED [ 77%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_backref_markers_order_and_pdf_link_geometry FAILED [ 88%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_order_references_sentinels_match_document_order FAILED [100%]

=========================== short test summary info ============================
9 failed in 0.44s
```

**Failing-test → decision/requirement map** (verbatim assertion messages, `--tb=line`; full
subprocess stdout/stderr embedded in several of these messages is elided here for readability —
reproduce verbatim with the command above):

| Test (`-k` selector) | Decision/requirement enforced | RED reason (verbatim assertion, elided) |
|---|---|---|
| `test_link_citing_site_targets_match_definition_anchors_and_own_ids` (`link`) | CIT-03 / D-14 | `AssertionError: index.typ's Krizhevsky2012 DEFINITION carries no attached anchor <index:krizhevsky2012> yet -- CIT-01/D-13 RED (no citation handler exists to emit it). Attached anchors found: ['index:citation-render-gate', 'index:citing-sites', 'index:concat-protocol', 'index:nested-protocol', 'index:references', 'index:run-break']` |
| `test_namespace_duplicate_key_is_document_scoped` (`namespace`) | D-13 / D-10 | `AssertionError: index.typ's OWN Same2020 definition does not attach <index:same2020> -- CIT-01/D-13 RED (no citation handler exists yet). Found: [...same 6 heading anchors, no citation anchors...]` |
| `test_separator_paragraph_concat_and_list_item_boundaries` (`separator`) | SC#5 | `AssertionError: No grid( call found between '{text("References")}' and '{text("Run Break")}' -- pre-fix RED: D-05's citation-run grid does not exist yet.` |
| `test_uncited_entry_renders_plain_label_in_shared_grid` (`uncited`) | D-07 | `AssertionError: No grid( call found between '{text("References")}' and '{text("Run Break")}' -- pre-fix RED: D-05's citation-run grid does not exist yet.` |
| `test_references_run_and_run_break_grid_counts` (grid-count) | D-05 / D-06 | `AssertionError: D-05: the References section's five citation definitions (separated only by a comment, which emits nothing) must land in exactly ONE grid, found 0: ...` |
| `test_citation_gate_compiles_via_real_typst_compile` (`compile`) | CIT-01 (classic RED) | `AssertionError: sphinx-build -b typstpdf failed (CIT-01 classic RED): ... TypstError: expected semicolon or line break ...` (`returncode=2`) |
| `test_layout_hanging_indent_and_widest_label_alignment` (`layout`) | CIT-02 / D-05 / D-06 | `AssertionError: index.pdf was not produced -- typst.compile() aborted pre-fix on the classic CIT-01 compile fatal: ...` |
| `test_backref_markers_order_and_pdf_link_geometry` (`backref`) | CIT-04 / D-01 / D-02 / D-03 / D-08 | `AssertionError: No grid( call found between '{text("References")}' and '{text("Run Break")}' -- pre-fix RED: D-05's citation-run grid does not exist yet.` |
| `test_order_references_sentinels_match_document_order` (`order`) | CIT-06 / SC#4 | `AssertionError: index.pdf was not produced -- typst.compile() aborted pre-fix on the classic CIT-01 compile fatal: ...` |

Every RED above is a structural assertion mismatch (a missing anchor, a missing `grid(` call, a
missing PDF artifact) or the classic build fatal captured verbatim in section 3 — **none is a
Python `TypeError`, `KeyError`, or fixture error**; confirmed by reading the full `-v` traceback for
each failure (no `E   TypeError`/`E   KeyError`/`ERROR at setup` line appears anywhere in the run).

---

## 6. Executed vs. skipped — a skip is not evidence

This session's environment has **both `typst-py` and `pypdf` importable** (`TYPST_AVAILABLE = True`,
`PYPDF_AVAILABLE = True`, confirmed via `uv run python -c "import typst, pypdf"` succeeding with no
exception in the per-worktree `.venv`). Consequently, **all 9 tests in the module ACTUALLY
EXECUTED** — none were skipped by the `TYPST_AVAILABLE`/`PYPDF_AVAILABLE` guards on this run:

| Test class | Guard | Executed this run? |
|---|---|---|
| `TestCitationRenderGateStructural` (5 tests: link, namespace, separator, uncited, grid-count) | none (pure `.typ`-string, runs regardless of `typst-py`/`pypdf`) | **Executed** |
| `TestCitationRenderGateRealCompile` (1 test: compile) | `skipif(not TYPST_AVAILABLE)` | **Executed** (not skipped) |
| `TestCitationRenderGateCompiledPdf` (3 tests: layout, backref, order) | `skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE))` | **Executed** (not skipped) |

`collected 9 items` with zero `skipped` in the summary line (`9 failed in 0.44s`, no `skipped`
count) confirms this directly — a skip is not recorded as evidence anywhere in this file; every RED
above was produced by a test that actually ran to a real assertion failure.

---

## 7. No source changes

```
$ git diff --stat ccb37b2..3c09d79 -- typsphinx/
(empty -- no output)
```

Zero files under `typsphinx/` are touched by this plan's commits (`02fe29f`, `3c09d79`, and the
commit that adds this evidence file). Every RED recorded above is against the translator exactly as
it stood at the phase-start commit `ccb37b2`.

---

## 8. Amendment (2026-08-02, Phase 40 Plan 05) — four defective assertions corrected against measurement

40-03 implemented `visit_citation`/`depart_citation`/`visit_label` (definition side, D-01..D-08/D-13)
and D-14's guarded own-ids anchor in `visit_reference`/`depart_reference` (citing side). Against the
merged translator, four of this module's nine selectors remained RED — not because the handlers were
wrong, but because four helpers/assertions in THIS module (authored by 40-01, before either handler
existed to measure against) did not actually measure what they claimed to. This section amends those
four, plus two further defects the corrections themselves exposed (a helper and a regex that were
unreachable behind an earlier, unrelated exception, so 40-05's own orchestrator-measurement pass never
saw them either — discovered only by re-reproducing after each fix, per this plan's own instruction).
Nothing above this line is rewritten or deleted; the RED it recorded stands as originally captured.

### 8.1 `test_link_citing_site_targets_match_definition_anchors_and_own_ids` / `test_backref_markers_order_and_pdf_link_geometry` — `_expected_own_id_anchors` / `_citing_site_own_anchors` omit `tags=`

**Verbatim failure, measured against the merged tree (`191aefa`) before any fix in this plan:**

```
sphinx.deprecation.RemovedInSphinx11Warning: 'tags' will become a required keyword argument for global_toctree_for_doc() in Sphinx 11.0.
```

Raised inside `sphinx.environment.BuildEnvironment.get_and_resolve_doctree` at both call sites
(`tests/test_citation_render_gate.py:275` and `:326`, pre-fix line numbers), escalated to a hard error
by this project's own `pyproject.toml` `filterwarnings = ["error::PendingDeprecationWarning"]` policy.

**What it could/could not detect, originally:** nothing citation-specific. Both helpers raised before
either function's own logic ran, so `test_link_...` and `test_backref_...` were unable to validate
CIT-03/D-14 or CIT-04/D-01/D-02/D-03/D-08 in either direction — a RED here proved only that the Sphinx
API call was stale, not that the citation handlers were wrong or right.

**Fix:** pass `tags=builder.tags` at both call sites. Confirmed by reading
`sphinx/environment/__init__.py` directly: the deprecation branch itself assigns
`tags = builder.tags` when the keyword is omitted, so this is a behaviour-preserving call-signature
repair — `git diff` for this change touches exactly the two argument lists, no assertion logic.

**Not a transcription:** the fix is a call-signature repair derived from reading Sphinx's own source,
not an expectation authored from observed translator output.

### 8.2 `test_layout_hanging_indent_and_widest_label_alignment` — `_leading_columns` measures the wrong column

**Verbatim failure, measured against the merged tree:**

```
AssertionError: CIT-02: the wrapped continuation line of Krizhevsky2012's entry must align at the same column as its own start (0), got 28: '                            ImageNet classification with deep convolutional neural networks. Advances'
assert 28 == 0
```

**What it could/could not detect, originally:** nothing, in either direction. `_leading_columns`
returned `len(line) - len(line.lstrip(" "))` — the leading whitespace of the LINE holding the marker —
copied from `tests/test_rubric_indent_invariance.py`, where the marker is the first glyph on its own
line and the two quantities coincide. In a citation grid, an entry's first line carries the label cell
AHEAD of the sentinel (e.g. `[Krizhevsky2012] (1,2)      CITORDERALPHA ...`), so the line's leading
whitespace is always 0 (the label starts the line), while the correct quantity — the column at which
the body/marker itself starts — was never measured at all. `alpha_column` came back 0 unconditionally,
so `assert alpha_column > 0` could never pass, and `continuation_column == alpha_column` could never
pass either (continuation lines carry no label, so their own leading whitespace IS the correct
quantity, and it is never 0 for a wrapped multi-line entry). This assertion was structurally incapable
of validating CIT-02 or D-05 in EITHER direction — a pass could never have been produced by a correct
translator either, before this fix.

**Measurement that justifies the fix** — `pypdf` `extraction_mode="layout"` over a freshly built
`index.pdf`'s References page (verbatim, leading integer is each line's own leading-whitespace count,
reproduced from this plan's `<orchestrator_measurements>` block, measured independently again during
this plan's own Task 1/2 execution):

```
   0 | '[Krizhevsky2012] (1,2)      CITORDERALPHA Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012).'
  28 | '                            ImageNet classification with deep convolutional neural networks. Advances'
  28 | '                            in neural information processing systems, 25. This entry body is padded'
   0 | '[Solo1998]                  CITORDERBRAVO Solo, J. (1998). A single-line reference entry.'
   0 | '[Never1999]                 CITORDERCHARLIE Never, N. (1999). An uncited reference entry - D-07's'
  28 | '                            plain, non-linked label case.'
   0 | '[Same2020]                  CITORDERDELTA Same, S. (2020). The duplicate-key entry, defined again in'
  28 | '                            second.rst - D-10's definition-side namespacing case.'
   0 | '[Concat2000]                CITORDERECHO Concat, C. (2000). A "quoted" reference with a cafe'
  28 | '                            character, exercising the existing escape_typst_string path.'
```

Every entry's body begins at column 28 — the marker's OWN start column within its line, not the line's
leading whitespace — and every continuation line's leading whitespace also lands on 28. **The value 28
is recorded HERE, in this evidence file (and in the plan's own `<orchestrator_measurements>` block),
and appears nowhere in `tests/test_citation_render_gate.py`** — confirmed: `grep -n '28'
tests/test_citation_render_gate.py` returns no output.

**Fix:** `_leading_columns` is renamed `_marker_column` and corrected to return
`line.index(marker_substring)` — the marker's own start column — instead of the line's leading
whitespace. `_find_page_and_column` (its sole caller, and the helper every layout assertion in this
module calls through) is corrected in place rather than given a sibling helper, because every one of
its six call sites wants the same quantity: "the column at which this entry's body starts." The
continuation-line measurement (`continuation_column = len(continuation_line) - len(continuation_line.lstrip(" "))`)
is left exactly as it was — correct for a continuation line, which carries no label to distort it.

**Not a transcription:** the corrected assertions stay fully relational — continuation column equals
the entry's own marker column, that column is `> 0`, all five References siblings share it, the two
Run Break entries are independently `> 0` — no numeric literal was introduced anywhere in the module.

### 8.3 `test_separator_paragraph_concat_and_list_item_boundaries` — the concat sub-check demanded a bare `link(`, contradicting D-14

**Verbatim failure, measured against the merged tree:**

```
AssertionError: Concat Protocol's term must '+'-join its leading text to the citing reference with no dangling operator:
  terms(separator: linebreak(), terms.item(text("Concat Term ") + [#link(<index:concat2000>, text("[Concat2000]"))#label("index:id7")], {par({text("A short definition body for the concat-protocol boundary case.")})}))
assert 'text("Concat Term ") + link(<index:concat2000>,' in '...'
```

**What it could/could not detect, originally:** it could detect the ABSENCE of a citing reference
after the concat operator, but not its PRESENCE once D-14 (implemented by this same phase, 40-03 Task
1) began wrapping every citation-derived citing reference as `[#link(<...>, ...)#label("...")]`. The
assertion's own comment claimed `visit_reference is unmodified by this phase`, which was true when
40-01 authored it and false from the moment 40-03 Task 1 landed — the comment is corrected in place
(see 8.5 below).

**Fix:** the assertion now tests the property SC#5's concat protocol actually requires — the leading
`text("Concat Term ")` is `+`-joined to the citing reference (tolerating the D-14 bracket-wrap via an
optional `(?:\[#)?` in the regex), the joined target matches `_expected_namespace_label("index",
"concat2000")`, and a region-wide scan confirms no `+` operator anywhere in the concat region is left
without a right operand.

**Not a transcription:** the expected link target is still derived via `_expected_namespace_label`,
never a literal; the dangling-operator scan is a general structural property, not a value read off one
build's output.

### 8.4 Two further defects, exposed only after 8.1–8.3 let their tests reach previously-unreachable assertions

Neither of these appears in this plan's `<orchestrator_measurements>` block — the orchestrator's own
single-pass reproduction never got far enough to see them, because each was masked by one of the
defects above (the `tags=` exception for 8.4a; the "No `grid(` call found" RED, present until D-05's
grid existed, for 8.4b). Both were found by re-reproducing after each fix, exactly as this plan's own
`<plan_specific_notes>` instructs, and both are corrected here because `typsphinx/` cannot be touched
by this plan and Task 2's own acceptance bar is "9 passed, 0 failed" — leaving either uncorrected would
mean the plan cannot close. Both are genuine test-measurement defects, not translator defects: the
real `-b typstpdf` compile passes clean in the same run (proving the citation handlers are correct),
and both corrections were verified structurally before being accepted.

**8.4a — `test_link_citing_site_targets_match_definition_anchors_and_own_ids`'s D-14 check:**
`_attached_anchor_tokens` recognised only the `[... <label>]` bracket-postfix shorthand (the form
`visit_citation`'s own definition anchor and `depart_term`'s heading anchors use), so it read D-14's
real, working `#label("...")` anchor — emitted by `visit_reference`/`depart_reference`, the SAME idiom
`visit_target`'s pre-existing `next_is_target` case already used before this phase — as absent.
Verbatim measurement, a real `-b typst` build of the fixture: the first Krizhevsky2012 citing site
emits `[#link(<index:krizhevsky2012>, text("[Krizhevsky2012]"))#label("index:id1")]`, and the
corresponding `-b typstpdf` real-compile test (`test_citation_gate_compiles_via_real_typst_compile`)
passes clean in the same build — proving the attachment resolves. `<name>` is parser sugar for
`#label("name")`; Typst attaches both identically to the immediately preceding content. Fix: broaden
`_attached_anchor_tokens` to the union of both forms (`_ATTACHED_ANCHOR_RE` and a new
`_ATTACHED_ANCHOR_CALL_RE` matching `#label("...")`). Not a transcription: both regexes extract tokens
dynamically; no anchor value is hard-coded.

**8.4b — `test_backref_markers_order_and_pdf_link_geometry`'s single-backref guard:** the check scanned
for a bare `\(\d+\)` across a region (`refs_grid[alpha_idx:bravo_idx]`) that structurally still carries
the TAIL of the PRECEDING entry's (Krizhevsky2012's) own body prose — "Hinton, G. E. (2012)" — and
false-positived on that publication year. Independently, the regex could never have matched the REAL
2+-backref marker shape in .typ SOURCE even where one exists: reading `typsphinx/translator.py`
directly confirms each ordinal is emitted inside a `[1]`/`[2]` content block passed to `link(...)`, the
digit never adjacent to a literal `(` in source. The check was unsound in both directions. Fix: scan
for the marker group's own source fragment, `text(" (")` — the literal text `visit_citation` only
appends when `len(backref_targets) >= 2` — which cannot appear in ordinary body prose and correctly
identifies the real construct being guarded against. Not a transcription: the fragment is read from
`typsphinx/translator.py`'s own source, not observed build output, and the check remains a structural
presence/absence test, not a hard-coded label or anchor value.

### 8.5 Two stale comments corrected

Two locations (an assertion failure message at what was line 497, and a comment at what was lines
636–638, pre-fix line numbers) stated that `visit_reference` is unmodified by this phase. True when
40-01 authored them; false since 40-03 Task 1 added D-14's guarded own-ids anchor. Both are rewritten
to say what is true: `visit_reference`'s pre-existing refid/xref branches are unchanged, and D-14 adds
an own-ids anchor on top of them. Neither correction touched an `assert` condition.

### 8.6 Re-proof — the corrected module still fails against the unfixed translator

A corrected test is only worth something if it can still fail. After committing the corrections above
(Task 1 commit `622ba76`, Task 2 commit `da2684f`), `typsphinx/translator.py` was temporarily restored
to `8b22bf6eb74e9f8153757c53d18f2f06da7bcdae` — the last commit at which it is byte-identical to the
pre-phase translator — and the module re-run:

```
$ git checkout 8b22bf6eb74e9f8153757c53d18f2f06da7bcdae -- typsphinx/translator.py
$ uv run python -m pytest tests/test_citation_render_gate.py -v
...
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_link_citing_site_targets_match_definition_anchors_and_own_ids FAILED [ 11%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_namespace_duplicate_key_is_document_scoped FAILED [ 22%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_separator_paragraph_concat_and_list_item_boundaries FAILED [ 33%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_uncited_entry_renders_plain_label_in_shared_grid FAILED [ 44%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_references_run_and_run_break_grid_counts FAILED [ 55%]
tests/test_citation_render_gate.py::TestCitationRenderGateRealCompile::test_citation_gate_compiles_via_real_typst_compile FAILED [ 66%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_layout_hanging_indent_and_widest_label_alignment FAILED [ 77%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_backref_markers_order_and_pdf_link_geometry FAILED [ 88%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_order_references_sentinels_match_document_order FAILED [100%]
============================== 9 failed in 0.51s ===============================
$ git checkout HEAD -- typsphinx/translator.py
```

All nine tests are RED against the unfixed translator — none was tightened into permanent passage, and
no failure above is a Python `TypeError`/`KeyError`/fixture `ERROR` (confirmed by grep over the full
`-v` output: no such line appears). After the restore, `git status --porcelain` and `git diff HEAD
--stat` are both empty — the temporary substitution left nothing behind. The module's ability to fail
was **verified, not assumed**.

Re-run against the merged (Task 1 + Task 2) translator immediately after:

```
$ uv run python -m pytest tests/test_citation_render_gate.py -v
...
9 passed in 0.69s
```

All four corrections in 8.1–8.3, and both further corrections in 8.4, are amended against
measurement — never waived, never weakened, never narrowed. The RED this file originally recorded
(sections 1–7 above) is unchanged.

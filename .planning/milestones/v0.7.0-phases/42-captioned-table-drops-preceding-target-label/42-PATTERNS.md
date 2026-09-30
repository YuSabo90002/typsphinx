# Phase 42: Captioned Table Drops Preceding Target Label - Pattern Map

**Mapped:** 2026-08-03
**Files analyzed:** 8 (1 modified source file, 2 new fixture pairs, 2 new test modules, 1 doc file,
1 todo file, N evidence files)
**Analogs found:** 6 / 8 (evidence files and the todo file have direct file-level precedents cited
inline rather than a role/data-flow classification)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|--------|-----------|-----------------|----------------|
| `typsphinx/translator.py` (`depart_table`, ~line 3249) | translator / visitor method | transform (doctree node → string, stateful buffer routing) | `typsphinx/translator.py` `depart_figure` (~line 2418-2531) — same file, structurally identical self-anchor + skip-ids pattern, already correct ordering relative to its own flag | exact (same file, same defect class, different node type) |
| `tests/fixtures/captioned_table_propagated_target_render_gate/conf.py` | config | request-response (Sphinx build config) | `tests/fixtures/paragraph_propagated_target_render_gate/conf.py` | exact |
| `tests/fixtures/captioned_table_propagated_target_render_gate/index.rst` | fixture / test data | transform input | `tests/fixtures/table_in_list_item_render_gate/index.rst` (list-item table shape) + `tests/fixtures/captioned_table_render_gate/index.rst` (captioned-table sentinel convention) | role-match (compose two precedents) |
| `tests/test_captioned_table_propagated_target_render_gate.py` | test (real-compile regression gate) | request-response (subprocess → stdout/stderr/files) | `tests/test_paragraph_propagated_target_render_gate.py` | exact |
| `tests/fixtures/figure_propagated_target_render_gate/conf.py` | config | request-response | `tests/fixtures/figure_target_caption_render_gate/conf.py` (same node family, wrong mechanism — see Pitfall note) → structurally copy `paragraph_propagated_target_render_gate/conf.py` instead | role-match |
| `tests/fixtures/figure_propagated_target_render_gate/index.rst` (+ reused `image.png`) | fixture / test data | transform input | `tests/fixtures/figure_target_caption_render_gate/index.rst` for the image-asset reuse only; `tests/fixtures/paragraph_propagated_target_render_gate/index.rst` for the actual target-directive-before-node shape | role-match (compose two precedents) |
| `tests/test_figure_propagated_target_render_gate.py` | test (real-compile regression gate, permanent) | request-response | `tests/test_paragraph_propagated_target_render_gate.py` | exact |
| `CHANGELOG.md` (`## [0.7.0]` → `### Fixed`) | doc / config | batch (single append) | Existing MATH-02 bullet, same file, lines 50-55 | exact |
| `.planning/todos/pending/<date>-*.md` (D-08 whitespace-only-title todo) | doc | batch | `.planning/todos/pending/2026-08-03-captioned-table-drops-preceding-target-label.md` (this phase's own folded-todo precedent for shape/tone) | role-match |
| `42-GATE-EVIDENCE-NN.md` files | doc (evidence) | batch | `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` (byte-invariance method); `.planning/phases/40.1-citation-degradation-hardening/40.1-NONREGRESSION.md` (change-site → RED manifest format) | exact |

## Pattern Assignments

### `typsphinx/translator.py` — `depart_table` fix (translator, transform)

**Analog:** same file, `depart_figure` (structurally identical, but NOT copy the flag-check —
`add_text` never gates on `self.in_figure`, so `depart_figure`'s ordering is a red herring; see
Pitfall below). The real template to copy is `depart_table`'s own existing branch, reordered.

**Current code, verbatim** (`typsphinx/translator.py:3249-3368`, current tree, confirmed by direct
grep this session — line numbers stable at time of mapping):

```python
def depart_table(self, node: nodes.table) -> None:
    ...
    if self.table_colcount > 0:
        ...
        table_code = "".join(table_parts)               # line 3302

        if self.table_caption:                            # line 3304 -- captioned branch
            figure_code = (
                f"figure(\n{table_code},\n"
                f"  caption: {{{self.table_caption}}},\n"
                f"  kind: table\n)"
            )
            if node.get("ids"):                            # line 3318
                label = self._namespace_label(
                    self._current_docname(), node["ids"][0]
                )
                if converted_width is not None:
                    self.body.append(
                        f"block(width: {converted_width})[#{figure_code} "
                        f"<{label}>]\n\n"
                    )
                else:
                    self.body.append(f"[#{figure_code} <{label}>]\n\n")  # line 3328
            elif converted_width is not None:
                self.body.append(...)
            else:
                self.body.append(f"{figure_code}\n\n")

            # BUG SITE -- fires while self.in_table is still True
            self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))  # line 3341
        else:
            # Caption-less path: byte-for-byte unchanged (SC#2/D-04).
            if converted_width is not None:
                self.body.append(f"block(width: {converted_width})[#{table_code}]\n\n")
            else:
                self.body.append(f"{table_code}\n\n")

    self.in_table = False                 # line 3351 -- flag cleared AFTER the bug fires today
    self.table_cells = []
    self.table_colcount = 0
    self.table_colwidths = []
    self.table_caption = None             # line 3355 -- reset BEFORE any re-check of the branch
    if hasattr(self, "table_cell_content"):
        del self.table_cell_content        # lines 3367-3368
```

**The gating helper this bug flows through** (`add_text`, `typsphinx/translator.py:423-437`,
unchanged by this fix — quote it to understand exactly why the move works):

```python
def add_text(self, text: str) -> None:
    if (
        hasattr(self, "in_table")
        and self.in_table
        and hasattr(self, "table_cell_content")
    ):
        self.table_cell_content.append(text)
    else:
        self.body.append(text)
```

**The fix (D-05), exact minimal diff shape:**

1. Capture `was_captioned = bool(self.table_caption)` **before** line 3355 resets
   `self.table_caption = None` — a local variable is required because the original `if
   self.table_caption:` condition (line 3304) cannot be re-evaluated after the reset.
2. Delete the `_emit_id_anchors` call from inside the `if self.table_caption:` branch (remove line
   3341).
3. Insert `if was_captioned: self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))`
   after `self.in_table = False` (after line 3351; before-or-after the other reset lines 3352-3355,
   3367-3368 is functionally immaterial — verified this session).

**Do NOT touch:** `_emit_id_anchors` itself (lines 481-552), `add_text` (423-437), `visit_table`'s
own unconditional call for non-captioned tables (line 3175, fires before `self.in_table = True` and
is already correct), or `depart_figure` (2418-2531, a different and already-correct mechanism — see
Anti-Pattern below).

### `tests/test_captioned_table_propagated_target_render_gate.py` (test, request-response)

**Analog:** `tests/test_paragraph_propagated_target_render_gate.py` (212 lines, full file read this
session) — copy this file's structure near-verbatim, renaming fixture references.

**Imports + availability guard** (lines 46-58 of the analog):
```python
import re
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False
```

**Fixture + helper shape** (lines 61-98 of the analog — rename `paragraph` → `captioned_table` and
adjust the directory):
```python
@pytest.fixture
def paragraph_propagated_target_render_gate_dir():
    return (
        Path(__file__).parent / "fixtures" / "paragraph_propagated_target_render_gate"
    )


@pytest.fixture
def temp_build_dir(tmp_path):
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard.
    """
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )
```
Note this project uses `-b typstpdf`, not `-b typst` — the semantic label-resolution fatal
(`TypstError: label ... does not exist`) only fires inside `TypstPDFBuilder.finish()`'s
`typst.compile()` call; a `-b typst` build would emit the dangling link text but never actually
prove the fatal is gone.

**The five assertion families** (lines 138-212 of the analog, condensed — the new test must repeat
this per D-01 shape, or once against a fixture containing all four shapes plus the caption-less
control):
```python
assert result.returncode == 0, f"...\nstderr: {result.stderr}"

# Fatal is logged (not raised) inside TypstPDFBuilder.finish(); guard the substring, never the
# full message text (Anti-Pattern precedent from Phase 25's own docstring warning).
assert "does not exist in the document" not in result.stderr, (
    "typst.compile() reported a dangling label -- the fix is not in effect:\n"
    f"stderr: {result.stderr}"
)
assert "Typst compilation failed" not in result.stderr

typ_text = (temp_build_dir / "index.typ").read_text(encoding="utf-8")
assert "[#metadata(none) <index:my-para-target>]" in typ_text

# Strip literal raw("...") string content BEFORE scanning -- fixture prose may contain
# inline-literal snippets like ``link(<name>, ...)`` that would otherwise false-positive.
scan_text = re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)
link_names = set(re.findall(r"link\(<([^>]+)>", scan_text))
anchor_names = set(re.findall(r"\[#metadata\(none\) <([^>]+)>\]", scan_text))
dangling = link_names - anchor_names
assert not dangling, f"dangling labels: {sorted(dangling)}\nanchors: {sorted(anchor_names)}"

pdf_output = temp_build_dir / "index.pdf"
assert pdf_output.exists() and pdf_output.stat().st_size > 0
with open(pdf_output, "rb") as f:
    assert f.read(4) == b"%PDF"
```

**Class + skip decorator wrapper** (lines 101-114 of the analog):
```python
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the propagated-target anchor render gate",
)
class TestParagraphPropagatedTargetRenderGate:
    """..."""
```

### `tests/test_figure_propagated_target_render_gate.py` (test, request-response, permanent gate)

**Analog:** same as above, `tests/test_paragraph_propagated_target_render_gate.py` — identical
skeleton, but this is a **permanent** regression gate (D-09), not a classic RED→GREEN recording, so
no pre-fix RED capture is required for it (the figure path is already correct; the gate exists to
catch a *future* regression). Assertions should target D-10's three shapes: named figure + target,
unnamed figure + target, figure inside a bullet-list item.

### `tests/fixtures/captioned_table_propagated_target_render_gate/conf.py` (config)

**Analog:** `tests/fixtures/paragraph_propagated_target_render_gate/conf.py` (full file read this
session, 26 lines):
```python
project = "Paragraph Propagated Target Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template.
typst_documents = [
    ("index", "index", "Paragraph Propagated Target Render Gate", "typsphinx tests"),
]
```
`index` MUST be listed in `typst_documents` (a master document) — this is what makes the writer
apply the full template and makes `TypstPDFBuilder.finish()` actually attempt a real compile;
skipping this is the single most likely way a new fixture silently fails to reproduce the fatal.
`numfig = True` is only needed if the fixture uses `:numref:` (the captioned-table analog
`tests/fixtures/captioned_table_render_gate/conf.py` sets it for that reason) — plain `:ref:` does
not require it.

### `tests/fixtures/captioned_table_propagated_target_render_gate/index.rst` (fixture data)

**Analogs (compose two):**
1. `tests/fixtures/table_in_list_item_render_gate/index.rst` — the list-item table shape and the
   "top-level control table proves byte-invariance" convention (full file, 30 lines, read this
   session):
```rst
Table In List Item Render Gate
================================

- Text styling commands:

  .. list-table::
     :header-rows: 1

     * - Command
       - Description
     * - ``\textbf``
       - Bold text

Top-level table
-----------------

A table at the top level (not nested in a list item) must stay
byte-unchanged by this fix.

.. list-table::
   :header-rows: 1

   * - Header A
     - Header B
```
2. `tests/fixtures/captioned_table_render_gate/index.rst` — the `:name:`/caption/`:numref:`/`:ref:`
   sentinel-token convention (`TBLCAPFIRSTSENTINEL`-style ALLCAPS tokens, one per table, used for
   exact-once assertions in the sibling GREEN gate `tests/test_pdf_render_gate.py`).

Compose the four D-01 shapes plus the caption-less control, e.g.:
```rst
.. _tbl-target:

.. table:: TBLCAPTGTNAMEDSENTINEL
   :name: tbl-name

   ...

.. _tbl-target-noname:

.. table:: TBLCAPTGTNONAMESENTINEL

   ...

- list item lead-in text:

  .. _tbl-target-li:

  .. table:: TBLCAPTGTLISTSENTINEL
     :name: tbl-name-li

     ...

.. _tbl-target-a:
.. _tbl-target-b:

.. table:: TBLCAPTGTTWOSENTINEL
   :name: tbl-name-two

   ...

Caption-less control table
---------------------------

.. table::

   ...
```
**Do not extend `captioned_table_render_gate/index.rst` itself** — it is already GREEN with
exact-count sentinel assertions in `TestCaptionedTableRenderGate`; adding a pre-fix-failing case to
the same fixture would fail that unrelated class's assertions during the RED-recording window (the
whole document aborts on a single dangling label). Give TBL-03 its own fixture directory, matching
the "one fixture per fixed defect class" convention already followed by
`paragraph_propagated_target_render_gate/`, `desc_container_propagated_target_render_gate/`,
`rubric_propagated_target_render_gate/`.

### `tests/fixtures/figure_propagated_target_render_gate/` (fixture data)

**Analogs (compose two, NOT one):**
1. `tests/fixtures/figure_target_caption_render_gate/image.png` — reuse this image asset only
   (copy the file; do not reuse its `index.rst`).
2. `tests/fixtures/paragraph_propagated_target_render_gate/index.rst` — copy the actual
   standalone-`.. _label:`-target-directive-before-node shape.

**Pitfall this analog choice avoids:** `tests/fixtures/figure_target_caption_render_gate/index.rst`
uses the docutils `:target:` **directive option** (`.. figure:: image.png` with `:target:
internal-anchor-section_`), producing a `reference`-wrapped figure (a click-through hyperlink on the
image) — a completely different code path (`visit_reference`/`depart_reference`) from the standalone
`.. _label:` **target directive** placed before a figure, which is what triggers docutils'
`PropagateTargets` transform and is the actual mechanism this phase is about. Confirmed this session
by reading both fixtures: neither existing figure fixture contains a standalone target directive.
Reusing the wrong fixture's `index.rst` would silently fail to exercise D-10 at all.

### `CHANGELOG.md` (doc, batch)

**Analog:** the existing MATH-02 bullet, same file, `## [0.7.0]` → `### Fixed` section (lines 50-55,
measured this session):
```
### Fixed

- **Block math inside a list item no longer emits a redundant blank line (MATH-02)** — the extra
  blank line between the math expression and the following paragraph break, carried over from the
  v0.6.5 Phase 34 review, is gone.

### Verified
```
Insert the new TBL-03 bullet after the MATH-02 bullet (after line 54, before the blank line 55),
matching the same D-01/D-02 Keep-a-Changelog granularity Phase 41 already used (bold requirement-ID
tag in parentheses, one user-visible-change sentence). Suggested wording (verify against the landed
fix):
```
- **A captioned table preceded by a standalone target no longer drops the target's label
  (TBL-03)** — both the table's own name-derived label and the propagated target's label are now
  emitted, so a reference to either resolves instead of aborting the compile on a dangling label.
```

### `.planning/todos/pending/<date>-*.md` (D-08 whitespace-only-title todo)

**Analog:** `.planning/todos/pending/2026-08-03-captioned-table-drops-preceding-target-label.md` —
this phase's own folded-todo precedent; copy its shape (verbatim owner-report style header,
breadcrumb/finding list, acceptance-style closing note) for the new D-08 todo, carrying forward this
session's negative-but-inconclusive probe finding (docutils suppressed the title node entirely for a
literal trailing-whitespace `.. table:: ` argument, so the next investigator does not re-run the same
trivial probe).

### `42-GATE-EVIDENCE-NN.md` files (evidence, batch)

**Analogs:**
- `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` — the byte-invariance
  (D-04) two-worktree method: named pre-fix/post-fix commit SHAs, per-worktree `uv sync --extra dev`
  provisioning, `sphinx-build -b typst` runs from each worktree's own venv, and an empty `diff`
  between the two `index.typ` outputs as the literal proof.
- `.planning/phases/40.1-citation-degradation-hardening/40.1-NONREGRESSION.md` §4 — the
  change-site → RED-form → evidence-file → provenance → pytest-selector → recording-commit table
  format to reuse for this phase's own single-change manifest (per CONTEXT.md, write this as a
  **new** file under `.planning/phases/42-.../`, never editing any `41-*` artifact).

## Shared Patterns

### Real-compile regression-gate skeleton (applies to both new test modules)
**Source:** `tests/test_paragraph_propagated_target_render_gate.py` (full file quoted in Pattern
Assignments above)
**Apply to:** `tests/test_captioned_table_propagated_target_render_gate.py`,
`tests/test_figure_propagated_target_render_gate.py`
- `_run_sphinx_build_typstpdf` subprocess helper, invoked as `sys.executable -m sphinx` (never a
  bare `sphinx-build`), never `uv run sphinx-build` — NixOS sandbox PATH-shadowing hazard.
- `TYPST_AVAILABLE` try/except-import skip guard at module scope, applied via
  `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` on the test class.
- Five assertion families in order: returncode, dangling-label-substring-absent, expected-anchor
  literal presence, generic `link(<name>)` vs `[#metadata(none) <name>]` set-difference sweep
  (after stripping `raw("...")` literal segments), PDF existence/size/`%PDF` magic-byte check.

### GATE-01 fixture conventions (applies to both new fixture directories)
**Source:** `tests/fixtures/paragraph_propagated_target_render_gate/conf.py` +
`tests/fixtures/captioned_table_render_gate/index.rst` (sentinel-token convention)
**Apply to:** `tests/fixtures/captioned_table_propagated_target_render_gate/`,
`tests/fixtures/figure_propagated_target_render_gate/`
- `index` must appear in `typst_documents` (master document) so the writer applies the full
  template and `TypstPDFBuilder.finish()` attempts a real compile.
- ALLCAPS sentinel tokens per distinct table/figure caption for exact-occurrence assertions.
- One dedicated fixture directory per fixed-defect-class, never extending an already-GREEN
  unrelated fixture (contamination-during-RED-window risk).

### `add_text` buffer-routing invariant (the actual defect mechanism — informs the translator.py fix
only, not a separate file)
**Source:** `typsphinx/translator.py:423-437`
**Apply to:** `depart_table` fix only — `self.in_table` is the ONLY flag `add_text` consults (cross-
checked against every other `self.in_*` flag in the file this session: `in_figure`, `in_paragraph`,
`in_list_item`, `in_captioned_code_block` all govern *different*, self-contained body-swap
mechanisms that `add_text` never reads). Do not generalize this fix to any other flag or call site.

## No Analog Found

None — every file this phase touches has a direct, recently-modified precedent in the same
codebase. The only items without a strict role/data-flow classification are the evidence files
(`42-GATE-EVIDENCE-NN.md`) and the todo file, which are process/documentation artifacts with
file-level precedents cited directly above rather than a role/data-flow row.

## Metadata

**Analog search scope:** `typsphinx/translator.py`; `tests/test_*_propagated_target_render_gate.py`
(5 precedent modules); `tests/fixtures/*_propagated_target_render_gate/`,
`tests/fixtures/captioned_table_render_gate/`, `tests/fixtures/figure_target_caption_render_gate/`,
`tests/fixtures/table_in_list_item_render_gate/`; `CHANGELOG.md`; `.planning/phases/36-*`,
`.planning/phases/40.1-*`; `.planning/todos/pending/`.
**Files scanned:** 8 direct reads + `grep -n` sweep of every `_emit_id_anchors`/`in_table`/
`in_figure` occurrence in `typsphinx/translator.py` (21 call sites, cross-referenced against
RESEARCH.md §5's sweep table).
**Pattern extraction date:** 2026-08-03

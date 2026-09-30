# Phase 18: Fidelity Fixes + Regression-Gate Close - Pattern Map

**Mapped:** 2026-07-19
**Files analyzed:** 3 (1 large multi-site translator edit counted once, 1 new fixture pair, 1 modified test)
**Analogs found:** 3 / 3

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/translator.py` (`depart_table`, `visit_colspec`, `visit_tgroup`, `visit_table`, `visit_literal`) | translator/emitter (visitor methods on `TypstTranslator`) | transform (doctree node → Typst source string) | same file, existing sibling visitor methods (`visit_table`/`depart_table`/`visit_tgroup` themselves — this is an in-place edit, not a new-role file) | exact (editing existing methods, not introducing a new role) |
| `tests/test_wide_table_render_gate.py` + `tests/fixtures/wide_table_render_gate/{conf.py,index.rst}` | test (integration, real-compile fixture) | request-response / batch (subprocess sphinx-build → typst.compile → pypdf extract → assert) | `tests/test_pdf_render_gate.py::TestTableWidthRenderGate` + `tests/fixtures/table_width_render_gate/` (same GATE-01 table-focused pattern); DESC-02 collision-absence idiom in `TestDescSignatureRenderGate` | exact |
| `tests/test_table_in_list_item_render_gate.py` (assertion update only) | test (fast/offline regression) | request-response (subprocess sphinx-build -b typstpdf → assert on `.typ`/pdf) | itself (existing file, only literal strings change) | exact |

## Pattern Assignments

### `typsphinx/translator.py` — `visit_table` / `depart_table` / `visit_tgroup` / `visit_colspec` / `visit_literal` (translator, transform)

**Analog:** the file's own existing methods (same file, adjacent lines) — this is a targeted edit, not a copy-from-elsewhere pattern. Read directly at:
- `visit_table`: lines 2203–2235
- `_format_table_cell`: lines 2237–2264
- `depart_table`: lines 2266–2326
- `visit_tgroup`/`depart_tgroup`: lines 2328–2345
- `visit_colspec`/`depart_colspec`: lines 2347–2364
- `visit_literal`: lines 1145–1188

**State-init idiom to extend** (`visit_table`, lines 2233–2235):
```python
self.in_table = True
self.table_cells = []  # Store cells for table generation
self.table_colcount = 0  # Track number of columns
```
Add a new `self.table_colwidths = []` accumulator alongside `table_colcount` here (and reset it in `depart_table`'s teardown block, lines 2319–2321, next to `self.table_colcount = 0`). This exactly follows the codebase's established "reset per-table state in `depart_table`'s footer, initialize in `visit_table`'s header" idiom — no new pattern is being introduced, only a new field added to the existing triple.

**`self.in_*` boolean-flag idiom** (constructor, lines 80–115, e.g. `self.in_table = False` at line 81, `self.in_list_item = False` at line 107): flags are declared `False` in `__init__`, flipped `True` in the relevant `visit_*`, flipped back `False` in the paired `depart_*`. `self.in_table` (already existing) is the gate to reuse as-is for the ZWSP injection in `visit_literal` — no new flag needed, just an `if self.in_table:` branch inside the existing method body (before line 1176's `escape_typst_string(code_content)` call).

**`visit_colspec` — capture instead of discard** (lines 2347–2355):
```python
def visit_colspec(self, node: nodes.colspec) -> None:
    """
    Visit a colspec (column specification) node.

    Args:
        node: The colspec node
    """
    # Column specifications are handled by tgroup
    raise nodes.SkipNode
```
Change the body to append `node.get("colwidth")` to `self.table_colwidths` before the `raise nodes.SkipNode` (SkipNode itself must stay — colspec has no children to visit, matching every other zero-content node in this file).

**`depart_table` — emission site to change** (lines 2274–2295, the two `columns: {self.table_colcount}` call sites at 2292 and 2295): both `f"table(\n  columns: {self.table_colcount},\n"` occurrences (the `block(width:...)`-wrapped branch and the unwrapped branch) become `f"table(\n  columns: {self._build_columns_fr_arg()},\n"` via a new small helper method (sibling to `_format_table_cell`, e.g. inserted right before `depart_table`) — follow `_format_table_cell`'s existing style (private `_`-prefixed method, docstring with `Args:`/`Returns:`, called from `depart_table`).

**`visit_literal` — ZWSP injection site** (lines 1168–1176):
```python
# Get code content directly
code_content = node.astext()

# Escape code content for string parameter via the shared helper.
...
escaped_code = escape_typst_string(code_content)
```
Insert the `self.in_table`-gated ZWSP replacement between these two lines (mutate `code_content` before it reaches `escape_typst_string`), matching the RESEARCH.md-verified Pattern 3 code exactly. This is a straight insertion into an existing method, not a new method.

**Error handling / defensive-fallback idiom:** none of the four analog methods use try/except — this file's node-handler convention is "trust the docutils API shape, use `.get(key, default)` for optional attributes" (e.g. `node.get("cols", 0)` at line 2336, `node.get("width")` at line 2285). The new `_build_columns_fr_arg` helper should follow the same style: no exceptions, a plain `all(w and w > 0 for w in widths)` validity check with a `[1] * n` fallback (as shown in RESEARCH.md Pattern 2), consistent with how `depart_table` already handles the optional `width` attribute (`converted_width = self._convert_length_to_typst(width) if width else None`).

---

### `tests/test_wide_table_render_gate.py` + `tests/fixtures/wide_table_render_gate/` (test, integration real-compile)

**Analog:** `tests/test_pdf_render_gate.py::TestTableWidthRenderGate` (class + fixture dir `tests/fixtures/table_width_render_gate/`), structurally identical GATE-01 table-focused real-compile pattern already in this file. The new file should be a **new standalone test module** (`tests/test_wide_table_render_gate.py`), mirroring `test_table_in_list_item_render_gate.py`'s self-contained-module shape (own imports, own fixtures, own `_run_sphinx_build_typstpdf` helper) rather than being folded into the already-2300-line `test_pdf_render_gate.py`.

**Imports + availability-guard pattern** (`tests/test_pdf_render_gate.py` lines 16–35, reused verbatim style in `tests/test_table_in_list_item_render_gate.py` lines 43–54):
```python
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
```

**Fixture-dir + temp-build-dir pattern** (`test_pdf_render_gate.py` lines 51–54, 123–132):
```python
@pytest.fixture
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def wide_table_render_gate_dir(fixtures_dir):
    """Return the path to the wide_table_render_gate fixture project."""
    return fixtures_dir / "wide_table_render_gate"

@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"
```
(Or, following `test_table_in_list_item_render_gate.py`'s single-file convention at lines 57–66, skip the separate `fixtures_dir` fixture and hardcode `Path(__file__).parent / "fixtures" / "wide_table_render_gate"` directly — either is an established idiom in this codebase; prefer whichever the new standalone module's sibling analog (`test_table_in_list_item_render_gate.py`) uses since it is the closer "own module" match.)

**Subprocess-build helper — use the `typstpdf` builder, not `typst`** (this fixture needs the FULL compile-to-PDF path since the bug is a real-compile issue, not just `.typ`-string emission). Copy `tests/test_table_in_list_item_render_gate.py` lines 69–92 verbatim (adjust only the docstring):
```python
def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )
```
Note RESEARCH.md's own code example (lines 431–482 of 18-RESEARCH.md) already assumes `result = _run_sphinx_build_typstpdf(...)` then a SEPARATE uncaught `typst.compile(...)` call — but with `-b typstpdf` the PDF is already compiled by the builder itself during `sphinx-build`. Follow `test_table_in_list_item_render_gate.py`'s actual proven shape instead (build via `-b typstpdf`, then just assert `index.pdf` exists/non-empty/`%PDF` magic — no second manual `typst.compile()` call needed, since `TypstPDFBuilder.finish()` already did it). This resolves an inconsistency between the RESEARCH.md example and the codebase's real `typstpdf` idiom; prefer the codebase idiom (fewer moving parts, matches how the SAME kind of "did the fatal happen" proof already works in `test_table_in_list_item_render_gate.py`).

**Test class + skipif decorator pattern** (`test_pdf_render_gate.py` lines 2235–2240, `TestTableWidthRenderGate`):
```python
@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestWideTableRenderGate:
    """
    Real-compile acceptance gate for FID-01a: wide-table fr-columns +
    ZWSP break-point injection (18-RESEARCH.md Critical Finding).

    Requirements: FID-01a, GATE-01 (18-CONTEXT.md D-01/D-02,
    18-RESEARCH.md "Critical Finding" / "Validation Architecture").
    """
```
Since this fixture asserts PDF-extracted text (not just compile success), also apply `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), ...)` (both libraries needed) — matches `TestTableWidthRenderGate`'s exact guard, not `test_table_in_list_item_render_gate.py`'s `typst`-only guard (which doesn't need pypdf since it only checks `.typ` text + PDF magic bytes, not extracted text).

**Collision-absence assertion idiom (the DESC-02 pattern)** — `test_pdf_render_gate.py::TestDescSignatureRenderGate.test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline`, lines 779–797:
```python
assert DESC_LINE_ONE_SENTINEL in full_text, (
    f"Expected multi-line sentinel '{DESC_LINE_ONE_SENTINEL}' in "
    "extracted PDF text -- desc_signature_line regression"
)
assert DESC_LINE_TWO_SENTINEL in full_text, (
    f"Expected multi-line sentinel '{DESC_LINE_TWO_SENTINEL}' in "
    "extracted PDF text -- desc_signature_line regression"
)
concatenated = DESC_LINE_ONE_SENTINEL + DESC_LINE_TWO_SENTINEL
assert concatenated not in full_text, (
    "The two desc_signature_line sentinels were concatenated with "
    "no separator in extracted PDF text -- linebreak() did not "
    "produce a real visual break ..."
)
```
This is the exact idiom `18-RESEARCH.md`'s own "Code Examples" section (lines 429–482) already models the new wide-table test on — replicate it 1:1: define per-cell sentinel constants at module level (mirroring `DESC_LINE_ONE_SENTINEL`/`DESC_LINE_TWO_SENTINEL` at lines 702–703), assert each present individually, then assert the pairwise-concatenated string is ABSENT from `full_text`.

**Sentinel-constant + module-docstring placement idiom** (`test_pdf_render_gate.py` lines 37–48, e.g. `LEAK_SIGNATURES`, `TODO_BODY_SENTINEL`; or lines 2229–2232 right before `TestTableWidthRenderGate`, e.g. `TABLEPXSENTINEL7Q4`): module-level uppercase constants with a short comment tying them to the specific fixture's `index.rst` content, placed immediately above the class that uses them:
```python
# Sentinel tokens for the wide_table_render_gate fixture -- distinctive,
# unlikely tokens chosen so their presence/absence in extracted PDF text
# proves the fr-columns + ZWSP fix closed FID-01a's column-collision bug.
# Must match the tokens embedded in wide_table_render_gate/index.rst.
WIDE_TABLE_TARGET_SENTINEL = "WIDETABLETARGETSENTINELQ7X9"
WIDE_TABLE_ALT_SENTINEL = "WIDETABLEALTSENTINELK3M2"
```

**Structural sanity check idiom** (`test_pdf_render_gate.py` lines 2280–2297, `TestTableWidthRenderGate`'s `.typ`-source assertions BEFORE the compile/extraction steps): assert `"columns: (" in typ_text and "fr" in typ_text` as an ADDITIONAL (never a substitute) check alongside the PDF-extraction proof, exactly per RESEARCH.md's own code example (lines 478–482) and per the codebase's established "assert structure in the emitted `.typ`, then separately assert on the compiled PDF" two-layer proof pattern that `TestTableWidthRenderGate` already uses.

**Fixture `conf.py` pattern** — copy `tests/fixtures/table_width_render_gate/conf.py` verbatim, changing only `project`, the docstring comment, and requiring `typst_documents` to declare `index` as a master document (this is REQUIRED — see writer.py's master-vs-included branch noted in CLAUDE.md; an included document only gets minimal imports, no template):
```python
project = "Wide Table Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

typst_documents = [
    ("index", "index", "Wide Table Render Gate", "Test Author"),
]
```

**Fixture `index.rst` pattern** — follow `tests/fixtures/table_width_render_gate/index.rst`'s shape (title + directive body with sentinel tokens embedded in cell content), but use RESEARCH.md's own already-verified `index.rst` content (18-RESEARCH.md lines 486–499) which uses double-backtick inline-literal cells (NOT plain text) — this is load-bearing: a plain-text fixture would only prove the `fr`-columns half, not the ZWSP half:
```rst
.. list-table:: Wide Table Render Gate
   :header-rows: 1
   :widths: 40, 10, 10, 40

   * - Target
     - Deprecated
     - Removed
     - Alternatives
   * - ``sphinx.environment.BuildEnvironment.WIDETABLETARGETSENTINELQ7X9_long_path``
     - 8.7
     - 11.0
     - ``sphinx.util.WIDETABLEALTSENTINELK3M2_alternative_function_name``
```

---

### `tests/test_table_in_list_item_render_gate.py` (assertion-string update only, no structural change)

**Analog:** itself — no external pattern needed, this is a literal-string edit.

**Exact site to change** (lines 171–178):
```python
assert (
    'text("A table at the top level (not nested in a list item) '
    'must stay\\nbyte-unchanged by this fix.")})\n\ntable(\n'
    "  columns: 2,\n" in typ_text
), (
    "The top-level table's rendering changed -- the list-item "
    f"separator fix must not touch it:\n{typ_text}"
)
```
Per RESEARCH.md Pitfall 2 (confirmed via direct docutils parsing of this exact fixture's `index.rst`: both tables have `colwidth = [50, 50]`), change `"  columns: 2,\n"` to `"  columns: (50fr, 50fr),\n"` in this block. Also grep the same file for any OTHER `"columns: 2"` occurrence (RESEARCH.md flags the possibility of a second, neighboring byte-exact block for the list-item-nested table) and apply the identical substitution there. Read the whole file first (`tests/test_table_in_list_item_render_gate.py`, 189 lines) — it is small enough for a single non-overlapping read/edit pass; no other lines change (the docstring's narrative about the separator fix stays accurate, only the columns literal shape is stale).

## Shared Patterns

### `self.in_*` per-node state-flag idiom
**Source:** `typsphinx/translator.py` constructor lines 80–115 (declaration) + paired `visit_*`/`depart_*` set/reset sites throughout the file (e.g. `self.in_table` at 81/2233/2319, `self.in_list_item` at 107/439/1445-1447).
**Apply to:** the ZWSP-injection gate in `visit_literal` (reuse existing `self.in_table`, no new flag) and the new `self.table_colwidths` per-table accumulator (declared alongside `self.table_cells`/`self.table_colcount`, same init/reset lifecycle, NOT a boolean flag but follows the identical "init in `visit_table`, reset in `depart_table`" lifecycle).

### GATE-01 real-compile fixture pattern (mini Sphinx project + real `typst.compile()`/`-b typstpdf` + pypdf text-extraction assertion)
**Source:** `tests/test_pdf_render_gate.py` (all classes) + `tests/test_table_in_list_item_render_gate.py`; fixture pairs under `tests/fixtures/*_render_gate/`.
**Apply to:** `tests/test_wide_table_render_gate.py` + `tests/fixtures/wide_table_render_gate/`. Never assert on `.typ`-string agreement alone (per SC#1 and per Pitfall 4/"Trusting compile succeeded alone" in RESEARCH.md) — always pair a structural `.typ` assertion with a real-compile PDF-text-extraction assertion.

### DESC-02 collision-absence idiom (concatenated-sentinel-not-in-full_text)
**Source:** `tests/test_pdf_render_gate.py::TestDescSignatureRenderGate`, lines 779–797 (`DESC_LINE_ONE_SENTINEL`/`DESC_LINE_TWO_SENTINEL`/`concatenated not in full_text`).
**Apply to:** the wide-table fixture's core proof — assert `WIDE_TABLE_TARGET_SENTINEL + <adjacent-cell-sentinel-or-value>` is NOT a substring of `full_text`, while each individual sentinel IS present. This is the only idiom in the codebase that proves a *silent* rendering bug (no compile error, no warning) — the same shape needed for FID-01a per RESEARCH.md's "Critical Finding."

### Subprocess-build helper (`sys.executable -m sphinx`, never `uv run sphinx-build`)
**Source:** `tests/test_pdf_render_gate.py::_run_sphinx_build_typst` (lines 135–172) and `tests/test_table_in_list_item_render_gate.py::_run_sphinx_build_typstpdf` (lines 69–92).
**Apply to:** the new `tests/test_wide_table_render_gate.py` needs its own `_run_sphinx_build_typstpdf` helper (copy the `typstpdf` variant, since the bug requires a real compile-to-PDF, not just `.typ` emission).

## No Analog Found

None — all three files/edits have strong, directly-applicable analogs already in this codebase.

## Metadata

**Analog search scope:** `typsphinx/translator.py`, `tests/test_pdf_render_gate.py`, `tests/test_table_in_list_item_render_gate.py`, `tests/fixtures/table_width_render_gate/`, `tests/fixtures/table_in_list_item_render_gate/`
**Files scanned:** 5 (2 source/test files read in full via targeted non-overlapping ranges, 2 fixture files read in full, 1 existing test file read in full)
**Pattern extraction date:** 2026-07-19

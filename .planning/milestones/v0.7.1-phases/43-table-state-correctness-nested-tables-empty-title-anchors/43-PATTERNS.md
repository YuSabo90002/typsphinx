# Phase 43: Table State Correctness — Nested Tables + Empty-Title Anchors - Pattern Map

**Mapped:** 2026-08-04
**Files analyzed:** 4 (1 modified production file, 3 new test files + their fixture pairs)
**Analogs found:** 4 / 4

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/translator.py` (state save/restore in `visit_table`/`depart_table`, `visit_figure`/`depart_figure`; new `visit_legend`/`depart_legend`; `depart_table` anchor branch; `_emit_id_anchors` docstring) | translator (visitor) | transform (doctree node → Typst string, in-process scalar state) | itself — pattern extracted below is intra-file (`visit_caption`/`depart_caption`'s buffer-swap idiom is the closest sibling shape for the new save/restore) | exact (same file, adjacent methods) |
| `tests/test_nested_table_render_gate.py` (NEW) | test (render gate) | request-response (subprocess `sphinx-build` → filesystem `.typ`/`.pdf`) | `tests/test_table_in_list_item_render_gate.py` | exact — same "structural, compiles-clean RED" shape (Pattern 3), same subprocess helper |
| `tests/fixtures/nested_table_render_gate/{conf.py,index.rst}` (NEW) | config + fixture rST | file-I/O (static Sphinx project fixture) | `tests/fixtures/table_in_list_item_render_gate/{conf.py,index.rst}` | exact |
| `tests/test_table_empty_caption_anchor_render_gate.py` (NEW) | test (render gate) | request-response (subprocess → `TypstError` / label-resolution) | `tests/test_table_in_list_item_render_gate.py` (RED-shape: classic `TypstError`, closer analog for the assertion style is `test_wide_table_render_gate.py`'s pypdf pattern for the post-fix GREEN half) | role-match (RED half); exact (GREEN half via pypdf) |
| `tests/fixtures/table_empty_caption_anchor_render_gate/{conf.py,index.rst}` (NEW) | config + fixture rST | file-I/O | `tests/fixtures/table_in_list_item_render_gate/{conf.py,index.rst}` | exact |
| `tests/test_nested_figure_render_gate.py` (NEW) | test (render gate) | request-response (subprocess → `TypstError`) | `tests/test_table_in_list_item_render_gate.py` (subprocess/helper shape) + `tests/test_wide_table_render_gate.py` (pypdf GREEN-assertion shape) | role-match |
| `tests/fixtures/nested_figure_render_gate/{conf.py,img.png,index.rst}` (NEW) | config + fixture rST + image asset | file-I/O | `tests/fixtures/table_in_list_item_render_gate/{conf.py,index.rst}` (rST/conf shape); any `test_figure_propagated_target_render_gate.py`-style fixture for the `img.png` asset convention (not re-read this pass — RESEARCH already names it; use a 1x1 placeholder PNG matching the existing figure-fixture convention) | role-match |

## Pattern Assignments

### `typsphinx/translator.py` — nesting save/restore (TBL-04, FIG-01) + TBL-05 anchor branch + QUA-01 docstring

**Analog for the save/restore shape:** `visit_caption`/`depart_caption`'s existing buffer-swap idiom (`typsphinx/translator.py:2532-2589`) — this is the ONE place in the file that already saves/restores translator scalar state around a nested visit, and it is the right shape to imitate (not invent) for the table/figure nesting fix.

**Buffer-swap / save-restore idiom to copy** (verbatim, lines 2550-2589):
```python
if self.in_figure:
    self._saved_body_for_figure_caption = self.body
    self.body = []
    # ... establish paragraph-separator context, ALSO saved:
    self._caption_was_in_paragraph = self.in_paragraph
    self._caption_was_paragraph_has_content = self.paragraph_has_content
    self.in_paragraph = True
    self.paragraph_has_content = False
self.in_caption = True

# ... depart:
if self.in_figure:
    self.figure_caption = "".join(self.body)
    if self._saved_body_for_figure_caption is not None:
        self.body = self._saved_body_for_figure_caption
    self._saved_body_for_figure_caption = None
    self.in_paragraph = self._caption_was_in_paragraph
    self.paragraph_has_content = self._caption_was_paragraph_has_content
self.in_caption = False
```
Pattern to extract: save the OLD scalar values to `_saved_*` attributes (or a stack) BEFORE resetting them for the new (inner) frame; restore explicitly in `depart_*`, never relying on a fresh reset alone. Apply the same shape to the full scalar set RESEARCH.md identifies for tables (`table_cells`, `table_colcount`, `table_colwidths`, `table_caption`, `table_cell_content` existence+value, `in_thead`, `current_morecols`, `current_morerows`) and figures (`figure_content`, `figure_caption`, `_figure_block_width`), gated on "is a container of the same kind already open" (`self.in_table`/`self.in_figure` truthy at `visit_table`/`visit_figure` entry) — push only when already inside one, so the top-level (non-nested) case stays byte-identical (mirrors `visit_caption`'s `if self.in_figure:` gate pattern, and the emitted-routing-decision constraint in Pitfall 2 below).

**`visit_table`/`depart_table` full text** (`typsphinx/translator.py:3149-3393`, read in full this session) is the base to modify. Key existing comments that constrain any rewrite:
- `is_captioned` structural pre-check (lines 3161-3175) — TBL-05/D-07 says this MUST stay structural (no `astext()` value-awareness); do not touch it beyond adding the new anchor-independence.
- The list-item separator block (lines 3177-3193) uses `self.body.append` directly, never `self.add_text`, "since `self.in_table` is set True below" — the nested-table fix's routing decision must respect the identical reasoning (Pitfall 2).
- `depart_table`'s emission (lines 3268-3342) also uses `self.body.append` directly — see Pitfall 2 below for why a nested table's emission must NOT simply switch to `self.add_text`.
- The Phase 25 `table_cell_content` lifetime comment (lines 3376-3388) — `del` only when the outermost table closes.

**TBL-05 fix site — exact code to change** (`typsphinx/translator.py:3344-3370`, verbatim):
```python
# TBL-03 (Phase 42): captured BEFORE self.table_caption is reset
# below, because the original `if self.table_caption:` condition
# cannot be re-evaluated after that reset ...
was_captioned = self.table_colcount > 0 and bool(self.table_caption)

self.in_table = False

# TBL-02/Critical Pitfall 3: ids[0] is already self-anchored above ...
if was_captioned:
    self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
```
Per D-05/D-07: `was_captioned` (rendered-caption truthiness) must stop gating the anchor call. The anchor call needs the STRUCTURAL `is_captioned` decided in `visit_table` (line 3173) stashed on an instance attribute (e.g. `self._table_was_captioned` or reuse via re-deriving `bool(node.children) and isinstance(node.children[0], nodes.title)` again at depart time — the doctree is unchanged between visit and depart, RESEARCH confirms this is cheap and available). The figure-wrapping `if self.table_caption:` branch (line 3304) stays exactly as-is (D-05: rendering and anchoring are allowed to keep disagreeing about "captioned").

**`visit_figure`/`depart_figure` full text** (`typsphinx/translator.py:2418-2530`, read in full this session) — the analog for the new `visit_legend`/`depart_legend` pair and for the FIG-01 nesting-safety fix. Key facts:
- `depart_figure` already routes ALL emission through `self.add_text` (never `self.body.append` directly), unlike `depart_table` — RESEARCH confirms this means the FIG-01 state fix is restore-only; no routing-destination rewrite needed for figure content itself.
- `self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))` at line 2518 is the OTHER of the two real `skip_ids` callers QUA-01 must name.

**New `visit_legend`/`depart_legend` — closest shape to mirror:** `visit_caption`/`depart_caption` (quoted above) for the buffer-swap-then-`{...}`-join mechanics, composed via the `{...}` code-block-join idiom (see next section). Gate the `{...}`-wrap of the figure body on `bool([c for c in node.children if isinstance(c, nodes.legend)])`, checked once in `visit_figure` (RESEARCH Pattern 2) — do NOT unconditionally wrap every figure body (breaks SC#4 byte-invariance for existing image-only figures).

**The `{...}` code-block-join idiom** — quote both established occurrences verbatim, per the RESEARCH's own naming:

`visit_title`'s docstring comment (`typsphinx/translator.py:725-728` per RESEARCH; not independently re-read this pass, RESEARCH quotes it directly):
```python
# Pitfall-1 fix: wrap the title content in a code block {...} so
# multi-child title content is one expression, not several
# juxtaposed statements (mirrors _depart_admonition's existing
# {...} wrap of the buffered admonition title).
```

`_format_table_cell` (`typsphinx/translator.py:3236-3237`, verified this session):
```python
if colspan == 1 and rowspan == 1:
    return f"{indent}{{{content}}},\n"
```

Both rely on Typst's `{ ... }` code block sequentially joining multiple already-rendered expressions into ONE content value — this is the exact mechanism `visit_legend`/`depart_legend` needs to combine an outer figure's `image(...)` with the legend's buffered content into `figure()`'s single positional `body` argument. A hand-verified `typst.compile()` experiment (RESEARCH Pattern 2) confirms:
```typst
[#figure(
  {
  image("img.png")
  figure(
  image("img.png"),
  caption: [INNERFIGCAP]
  )
  },
  caption: [OUTERFIGCAP]
) <id1>]
```
compiles successfully with both figures numbered and captioned.

**QUA-01 docstring fix site** — exact sentence to rewrite, `_emit_id_anchors`'s docstring (`typsphinx/translator.py:515-523`, verbatim):
```
``skip_ids`` lets a caller that ALREADY anchors one of the node's ids
by another mechanism suppress a duplicate definition here. The sole
user is ``depart_figure``: a captioned figure self-anchors ``ids[0]``
inside its own ``[#figure(...) <label>]`` markup block, but a
PROPAGATED explicit target lands a DIFFERENT id in ``ids[1:]`` that
would otherwise dangle -- so the figure passes ``skip_ids={ids[0]}`` to
anchor only the propagated remainder. When every id is skipped the
method is a no-op (list-item bookkeeping is untouched), keeping output
byte-for-byte identical.
```
Per D-08: rewrite "The sole user is `depart_figure`" to name BOTH real callers — `depart_figure` (line 2518) and `depart_table` (line 3370, added Phase 42) — without enumerating all 21 total `_emit_id_anchors` call sites. **Do this edit LAST** (after the nesting work lands) and re-grep `_emit_id_anchors(` call sites before writing the sentence — this phase may add or move callers (D-08's own instruction).

---

### `tests/test_nested_table_render_gate.py` (NEW, TBL-04)

**Analog:** `tests/test_table_in_list_item_render_gate.py` (full file read, 196 lines) — copy this file's shape wholesale:
- Same two fixtures: `<name>_render_gate_dir` (returns `Path(__file__).parent / "fixtures" / "<name>"`) and `temp_build_dir` (`tmp_path / "_build"`).
- Same `_run_sphinx_build_typstpdf` helper, verbatim (defined LOCALLY in this file, not shared via conftest — confirmed: no shared conftest helper exists across render-gate files today):
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
- Same `TYPST_AVAILABLE` try/except guard + `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` at class level.
- Since TBL-04's RED is **structural** (broken output compiles cleanly per Pattern 3 — no `TypstError`), the assertions must NOT check `result.stderr` for a compile-fatal substring (unlike this analog's `"expected semicolon or line break" not in result.stderr` check). Instead assert directly on the emitted `index.typ` text: that the outer table's sentinel cell content (e.g. `"OUTERHEADA"`, `"OUTERHEADB"`, `"OUTERPLAIN"`, `"OUTERCAP"`) is PRESENT in `typ_text` for all 4 nesting shapes (list-in-list, grid-in-list, list-in-grid, three-deep) — mirroring how this analog asserts exact substrings are present/absent in `typ_text` (lines 158-184), but here the assertion targets sentinel presence rather than juxtaposition-string absence. Still assert `result.returncode == 0` and `pdf_output` exists/starts with `%PDF` (both builds are expected to compile cleanly even pre-fix, per RESEARCH's own framing — the RED signal is the MISSING outer content in `typ_text`/extracted PDF text, not a nonzero exit code).
- Use pypdf text extraction too (see `test_wide_table_render_gate.py` below) as the stronger, structural-loss-proof half, since RESEARCH explicitly warns "no downstream error surface" — the `.typ`-string check alone is a reasonable RED-fixture check but the PDF-extraction check is the one the GATE-01 acceptance convention (`SC#1`) prefers.

### `tests/fixtures/nested_table_render_gate/{conf.py,index.rst}` (NEW)

**Analog:** `tests/fixtures/table_in_list_item_render_gate/{conf.py,index.rst}` (full files read). Copy shape:

`conf.py` pattern (verbatim structure, adapt the header comment + project name):
```python
project = "Table In List Item Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the ... fatal is observable.
typst_documents = [
    ("index", "index", "Table In List Item Render Gate", "Test Author"),
]
```
`index.rst` pattern: a top-level `====` title, prose explaining the repro, then the actual repro constructs as `.. list-table::` / grid-table RST under section headers, followed by (per this analog's convention) a "must stay byte-unchanged" control case. For `nested_table_render_gate/index.rst`, per D-01 include 4 sections: list-table-in-list-table, grid-table-in-list-table, list-table-in-grid-table, and a three-level nest — using sentinel cell text (`OUTERHEADA`/`OUTERCAP`/etc., matching the naming convention already used in `<specifics>` §2 of CONTEXT.md) so assertions can grep for exact strings.

---

### `tests/test_table_empty_caption_anchor_render_gate.py` (NEW, TBL-05)

**Analog (subprocess/skeleton):** `tests/test_table_in_list_item_render_gate.py` — same `_run_sphinx_build_typstpdf` helper and fixture shape as above.

**Analog (RED/GREEN assertion shape — classic `TypstError`):** closest existing precedent is the "aborts the compile, no PDF produced" shape this repo already uses for `TypstCompilationError` cases (RESEARCH's own Pattern 3 table cites CIT-01/TBL-03 as precedent, not independently re-read this pass since RESEARCH already characterizes them). Structure the test as:
```python
result = _run_sphinx_build_typstpdf(fixture_dir, temp_build_dir)
# PRE-FIX (documented in the test's docstring as the RED baseline observed
# during development, not asserted directly once the fix lands):
#   result.returncode != 0 and pdf_output does not exist, stderr contains
#   "label ... does not exist" per CONTEXT.md <specifics> §1.
# POST-FIX (the actual assertion committed):
assert result.returncode == 0, ...
pdf_output = temp_build_dir / "index.pdf"
assert pdf_output.exists() and pdf_output.stat().st_size > 0
with open(pdf_output, "rb") as f:
    assert f.read(4) == b"%PDF"
```
Then a **pypdf structural check** (mirroring `test_wide_table_render_gate.py`'s `pypdf.PdfReader(...).pages[i].extract_text()` idiom, quoted below) confirming: no table-number caption text appears for the empty-caption table (D-05: no `\sphinxcaption`-equivalent / no "Table N" line), while the `:ref:` cross-reference elsewhere in the document still resolves (no dangling-label compile abort — the PDF existing at all IS that proof, since a dangling label aborts the WHOLE document per the reproduction in CONTEXT.md `<specifics>` §1).

**Fixture rST — use the EXACT reproducing construct from CONTEXT.md/RESEARCH, do not simplify:**
```rst
.. role:: raw-html(raw)
   :format: html

.. _tbl-target:

.. table:: :raw-html:`<span></span>`

   +---+---+
   | a | b |
   +---+---+

See :ref:`the table <tbl-target>`.
```
Critical: the `:ref:` MUST carry explicit link text (`` :ref:`the table <tbl-target>` ``) — a bare `` :ref:`tbl-target` `` makes Sphinx itself refuse first with its own warning and degrade to plain text, masking the Typst-level failure (RESEARCH Pitfall 5 / CONTEXT `<specifics>` §1 fixture note).

### `tests/fixtures/table_empty_caption_anchor_render_gate/{conf.py,index.rst}` (NEW)

**Analog:** `tests/fixtures/table_in_list_item_render_gate/conf.py` for the `conf.py` shape (adapt project name/title); `index.rst` is the exact reproducing construct quoted above, verbatim (not adapted).

---

### `tests/test_nested_figure_render_gate.py` (NEW, FIG-01)

**Analog (subprocess/skeleton):** `tests/test_table_in_list_item_render_gate.py`'s `_run_sphinx_build_typstpdf` helper + fixture-dir/temp-build-dir fixture pair, copied verbatim.

**Analog (pypdf GREEN-assertion shape):** `tests/test_wide_table_render_gate.py` — quote its `TYPST_AVAILABLE`/`PYPDF_AVAILABLE` double-guard and `pypdf.PdfReader` idiom:
```python
try:
    import typst  # noqa: F401
    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
...
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
...
reader = pypdf.PdfReader(str(pdf_output))
full_text = "\n".join(page.extract_text() for page in reader.pages)
assert WIDE_TABLE_TARGET_SENTINEL in full_text, (...)
```
Per RESEARCH Pattern 3/Pitfall 4: write FIG-01's RED as a classic `TypstError` (the pre-fix compile aborts with `TypstError: unexpected argument` for a nested figure, or `TypstError: expected comma` for even a plain-text legend with no nested figure — assert one of these substrings appears pre-fix, `result.returncode != 0`, no `index.pdf` produced), and assert both figures' captions (`OUTERFIGCAP`, `INNERFIGCAP` sentinel-style strings) are present via `pypdf` extraction post-fix, matching `test_wide_table_render_gate.py`'s sentinel-presence assertion shape. Do NOT write this as a structural-only "caption missing" check — RESEARCH's Pitfall 4 explicitly warns the phase description understates the defect (it is a hard compile fatal, not a silent drop).

### `tests/fixtures/nested_figure_render_gate/{conf.py,img.png,index.rst}` (NEW)

**Analog:** `tests/fixtures/table_in_list_item_render_gate/conf.py` for the `conf.py` shape. For `img.png`: reuse the placeholder-image convention already established by other figure-bearing fixtures in this repo (e.g. `tests/fixtures/*figure*render_gate/img.png` — not independently re-read this pass since RESEARCH's own project-structure diagram already names `img.png` as a sibling to `conf.py`/`index.rst` in this exact fixture; copy the SAME placeholder bytes another figure fixture uses rather than generating a new image). `index.rst` needs a `.. figure::` whose SECOND paragraph (the legend-triggering shape) itself contains a nested `.. figure::` directive — per CONTEXT.md `<specifics>` §3 reproduction shape (`WARNING: unknown node type: <legend>`, outer caption `OUTERFIGCAP` dropped, inner figure injected as a stray content block).

---

## Shared Patterns

### Subprocess-driven `sphinx-build -b typstpdf` render gate
**Source:** `tests/test_table_in_list_item_render_gate.py` lines 43-93 (imports through `_run_sphinx_build_typstpdf`)
**Apply to:** all three new test files. Copy the helper verbatim — it deliberately invokes `sys.executable -m sphinx` (never `uv run sphinx-build` or a console-script entry point) to sidestep the documented NixOS-sandbox PATH-shadowing hazard, and each render-gate file defines its OWN copy (no shared conftest helper exists across this family today — confirmed by RESEARCH's Wave-0-gaps note).

### `pypdf` text-extraction structural proof
**Source:** `tests/test_wide_table_render_gate.py` lines 48-53 (import guard) and lines 162-163 (`pypdf.PdfReader(...).pages[i].extract_text()`)
**Apply to:** `test_nested_table_render_gate.py` (TBL-04's PDF-level half), `test_table_empty_caption_anchor_render_gate.py` (confirming no spurious caption/number for the empty-caption table), `test_nested_figure_render_gate.py` (confirming both figure captions survive post-fix). `pypdf>=6.14,<7` is already a declared dev dependency (`pyproject.toml`); no new install needed.

### Fixture project layout: `tests/fixtures/<name>/{conf.py,index.rst[,img.png]}`
**Source:** `tests/fixtures/table_in_list_item_render_gate/` and `tests/fixtures/wide_table_render_gate/` (both `ls`'d this session; both use the SAME two-file — or three-file with an image asset — shape, never `tests/roots/test-*`)
**Apply to:** all three new fixture directories in this phase. Confirmed: this repo's render-gate convention is `tests/fixtures/<descriptive_name>/`, NOT `tests/roots/test-<name>/` (the latter convention, per `CLAUDE.md`, is reserved for the broader `rootdir`-fixture-driven integration tests, a different test family from the GATE-01 render gates this phase adds to).

### Container-scalar-state save/restore around nesting
**Source:** `visit_caption`/`depart_caption`, `typsphinx/translator.py:2532-2589`
**Apply to:** the `visit_table`/`depart_table` and `visit_figure`/`depart_figure` nesting fix (TBL-04, FIG-01's state half). This is the only existing precedent in the file for "save the pre-existing scalar state, reset for the nested context, restore explicitly on depart" — every other `in_X` scalar in this file (`in_table`, `in_figure`, `in_thead`, etc.) is unconditionally reset/torn down with no save, which is exactly the defect this phase fixes.

### `{...}` code-block content join
**Source:** `_format_table_cell`, `typsphinx/translator.py:3236-3237`; `visit_title`'s docstring comment, `typsphinx/translator.py:725-728` (per RESEARCH citation)
**Apply to:** the new `visit_legend`/`depart_legend` composition of a figure's `image(...)` + legend content into `figure()`'s single positional body argument (FIG-01's routing half). Gate the wrap on legend-child presence, never unconditional (SC#4 byte-invariance).

## No Analog Found

None. Every file in this phase's scope has at least a role-match analog in the existing codebase — this is consistent with RESEARCH's own "Don't Hand-Roll" table, which found every mechanism this phase needs (anchoring, PDF assertion, byte-invariance proof, multi-piece content join, render-gate test shape) already exists somewhere in this codebase.

## Metadata

**Analog search scope:** `typsphinx/translator.py` (full targeted reads of lines 423-483, 481-552, 2418-2620, 3149-3394); `tests/*render_gate*.py` (`ls`, then full reads of `test_table_in_list_item_render_gate.py` and `test_wide_table_render_gate.py`); `tests/fixtures/table_in_list_item_render_gate/` and `tests/fixtures/wide_table_render_gate/` (`ls` + full reads of `conf.py`/`index.rst`).
**Files scanned:** 2 fully-read test files, 2 fully-read fixture pairs, ~350 lines of `translator.py` across 4 targeted reads (no re-reads of overlapping ranges).
**Pattern extraction date:** 2026-08-04

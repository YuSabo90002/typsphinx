# Phase 20: Signature Token Spacing (Cluster B) - Pattern Map

**Mapped:** 2026-07-20
**Files analyzed:** 3 (1 modified source file with 3 distinct edit sites; 2 test files — 1 extended/new, 1 required edit)
**Analogs found:** 3 / 3

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/translator.py` — `visit_desc_sig_space`/`depart_desc_sig_space` (~4812-4822) | translator visit/depart handler | transform (AST node → Typst text) | `visit_desc_sig_keyword`/`depart_desc_sig_keyword` (~4804-4811) and 2 other `pass`/`pass` siblings, same file | exact (identical target shape, same file, same node family) |
| `typsphinx/translator.py` — `depart_field_name` (~4691-4694) | translator departure handler (literal-string edit) | transform | itself (in-place one-line literal change); `depart_desc_parameter` (~4610) for sibling-boundary idiom precedent | exact (self) / role-match (sibling idiom) |
| `typsphinx/translator.py` — new `depart_field` body (~4671-4673, currently `pass`) | translator departure handler (new logic) | transform | `depart_desc_parameter` (translator.py:4610, `node.next_node(descend=False, siblings=True)` comma-separator idiom) | role-match (same "am I last sibling" idiom, different separator token) |
| `tests/test_desc_signature_concat_render_gate.py` (extend for FID-07/FID-08) | render-gate test (structural `.typ` assert + real compile) | request-response (subprocess build → filesystem artifacts → assert) | itself — canonical GATE-01 fixture shape already in this repo | exact |
| `tests/test_field_list_in_list_item_render_gate.py:165` (required edit) | render-gate test (locked assertion) | request-response | itself — the one pre-existing assertion that must change | exact |
| `tests/fixtures/desc_sig_space_render_gate/{conf.py,index.rst}` (new, if not consolidated into existing fixture) | test fixture project | file-I/O (Sphinx source project) | `tests/fixtures/desc_signature_concat_render_gate/` | exact (same fixture-project shape: `conf.py` + `index.rst`) |

## Pattern Assignments

### `typsphinx/translator.py` — `visit_desc_sig_space`/`depart_desc_sig_space` (translator handler, transform)

**Analog:** the four sibling `desc_sig_*` handlers immediately around it in the same file — `visit_desc_sig_keyword`/`depart_desc_sig_keyword` (lines 4804-4811), `visit_desc_sig_punctuation`/`depart_desc_sig_punctuation` (lines 4832-4839), `visit_desc_sig_operator`/`depart_desc_sig_operator` (lines 4840-4847).

**Current (buggy) code** (translator.py:4812-4822):
```python
def visit_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Visit a desc_sig_space node (whitespace in signatures)."""
    # Output space directly, not as separate text() node
    self.body.append(" ")
    # Don't set list_item_needs_separator - space is connector
    raise nodes.SkipNode

def depart_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Depart a desc_sig_space node."""
    # Handled in visit
    pass
```

**Analog shape to copy** (translator.py:4804-4811, one of the correctly-behaving siblings):
```python
def visit_desc_sig_keyword(self, node: addnodes.desc_sig_keyword) -> None:
    """Visit a desc_sig_keyword node (keyword in signatures like 'class', 'def')."""
    pass

def depart_desc_sig_keyword(self, node: addnodes.desc_sig_keyword) -> None:
    """Depart a desc_sig_keyword node."""
    pass
```

**Fix to apply** — reduce `visit_desc_sig_space`/`depart_desc_sig_space` to the identical `pass`/`pass` shape, letting the node's own child `Text(" ")` stream through the existing `visit_Text` dispatch (~line 946) unmodified:
```python
def visit_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Visit a desc_sig_space node (whitespace in signatures)."""
    pass

def depart_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Depart a desc_sig_space node."""
    pass
```

**Do not add:** any new helper function or concat-context branching inside these two methods — `visit_Text` already owns that logic (`_emit_inline_concat_separator`, `_mark_inline_concat_content`, `_add_paragraph_separator`, `list_item_needs_separator`), per RESEARCH.md's "Don't Hand-Roll" table.

---

### `typsphinx/translator.py` — `depart_field_name` colon-space (translator handler, literal-string edit)

**Current code** (translator.py:4691-4694, verified against live source):
```python
def depart_field_name(self, node: nodes.field_name) -> None:
    """Depart a field_name node."""
    # Close strong() and add colon
    self.body.append(' + text(":"))\n')
```

**Fix to apply** — change the literal string only (single-token edit, no structural change):
```python
def depart_field_name(self, node: nodes.field_name) -> None:
    """Depart a field_name node."""
    # Close strong() and add colon-space (FID-09)
    self.body.append(' + text(": "))\n')
```

This is a self-contained literal edit — no analog needed beyond the existing method, since `field_name` has exactly one call site (unlike `desc_sig_space`, no concat-context branching required).

---

### `typsphinx/translator.py` — `depart_field` inter-field boundary (translator handler, new logic)

**Analog:** `depart_desc_parameter` (translator.py:4610) — the established "is there a next sibling" idiom already used in this file for comma-separating parameters.

**Current code** (translator.py:4671-4673, verified against live source):
```python
def depart_field(self, node: nodes.field) -> None:
    """Depart a field node."""
    pass
```

**Fix to apply** (mirrors the `node.next_node(descend=False, siblings=True)` sibling-detection idiom):
```python
def depart_field(self, node: nodes.field) -> None:
    """Depart a field node.

    Emit a real two-space content statement between sibling fields (FID-09) --
    matches the ROADMAP SC#3 pinned inline target
    "Type: int (a number)  Default: 42". A bare cosmetic "\\n" between
    statements is insignificant in Typst code mode (Phase 19's proven
    invariant), so a real text("  ") VALUE is required. Both a leading AND
    trailing "\\n" are required so this statement never juxtaposes with its
    neighbors on one physical source line.
    """
    if node.next_node(descend=False, siblings=True):
        self.add_text('\ntext("  ")\n')
```

**Pitfall to guard against (Pitfall 4 in RESEARCH.md):** omitting either the leading or trailing `\n` produces two statements glued on one physical source line (`text("  ")strong(...)`), which is a real Typst parse error (`expected semicolon or line break`). Always real-compile (`-b typstpdf`, never `-b typst` alone) after this edit.

---

### `tests/test_desc_signature_concat_render_gate.py` (canonical GATE-01 fixture shape to extend/clone)

**Analog:** itself — this file IS the canonical GATE-01 shape referenced by RESEARCH.md as the template.

**Imports pattern** (lines 44-56):
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

**Fixture-path pattern** (lines 59-68):
```python
@pytest.fixture
def desc_signature_concat_render_gate_dir():
    """Return the path to the desc_signature_concat_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "desc_signature_concat_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"
```

**Real-build-via-subprocess pattern** (lines 77-100) — invoked as `sys.executable -m sphinx`, never `uv run sphinx-build` (NixOS-sandbox PATH hazard), always `-b typstpdf` (never `-b typst` alone) since only the PDF-compile path invokes `typst.compile()`:
```python
def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )
```

**Skip guard + assertion class pattern** (lines 103-159):
```python
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the desc-signature-concat render gate",
)
class TestDescSignatureConcatRenderGate:
    def test_typstpdf_signature_reference_first_param_produces_pdf(
        self, desc_signature_concat_render_gate_dir, temp_build_dir
    ):
        result = _run_sphinx_build_typstpdf(
            desc_signature_concat_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")
        # ... structural .typ asserts here ...
```

**PDF-magic-bytes tail pattern** (lines 170-179, copy verbatim into any new/extended fixture):
```python
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted..."
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
```

**Required D-07 addition (pypdf adjacency assert) — NOT present in this analog, must be added new.** Follow the graceful-skip pattern already established in `test_epigraph_render_gate.py` / `test_substitution_definition_render_gate.py` / `test_wide_table_render_gate.py` / `test_pdf_render_gate.py`:
```python
try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# ... inside the test, after the %PDF magic-bytes check ...
if PYPDF_AVAILABLE:
    reader = pypdf.PdfReader(str(pdf_output))
    text = reader.pages[-1].extract_text()
    assert "class sphinx" in text and "classsphinx" not in text  # FID-07
    assert "Py_ssize_t nitems" in text and "Py_ssize_tnitems" not in text  # FID-08
    assert "a * f(a)" in text  # FID-08 cpp:expr inline-concat context
```

**Structural `.typ` asserts** (verified this session per RESEARCH.md, safe to assert verbatim):
```python
assert 'text("class")\ntext(" ")\ntext("sphinx' in typ_text          # FID-07
assert 'text("PyObject")\ntext(" ")\ntext("*")\ntext("PyType_GenericAlloc")' in typ_text  # FID-08
assert 'text("PyTypeObject") + text(" ") + text("*") + text("type")' in typ_text          # FID-08 (desc_parameter concat form)
```

---

### `tests/fixtures/desc_signature_concat_render_gate/` (fixture project analog)

**Analog:** existing fixture directory shape — `conf.py` + `index.rst`, same convention every render-gate fixture in this repo follows (`tests/fixtures/<gate_name>/{conf.py,index.rst}`). Use the audit catalogue's own literal minimal-repro RST source verbatim where possible (per RESEARCH.md "Recommended Project Structure") for `desc_sig_space_render_gate/index.rst` (py:class + c:function + cpp:function + cpp:expr repros) and `confval_field_spacing_render_gate/index.rst` (the audit's literal `.. confval:: the_answer` no-blank-line repro).

---

### `tests/test_field_list_in_list_item_render_gate.py:165` (required locked-assertion edit)

**Current code** (verified against live source, lines 162-168):
```python
        # A top-level field list (not nested in a list item) must stay
        # byte-unchanged: no list-item separator applies outside a list item,
        # so field_name's strong( must NOT gain a spurious leading newline.
        assert 'strong(text("Author") + text(":"))' in typ_text, (
            "The top-level field list's field-name rendering changed -- the "
            f"list-item separator fix must not touch it:\n{typ_text}"
        )
```

**Required edit** — this is the ONLY assertion in the full test suite referencing the old no-space colon form (confirmed via `grep -n 'text(":")' tests/*.py` per RESEARCH.md Pitfall 2). Change to:
```python
        assert 'strong(text("Author") + text(": "))' in typ_text, (
            "The top-level field list's field-name rendering changed -- the "
            f"list-item separator fix must not touch it:\n{typ_text}"
        )
```
Update the surrounding comment too (it currently reads "must stay byte-unchanged," which is no longer true post-fix — the colon-space change is deliberately global per D-01).

## Shared Patterns

### Real-compile GATE-01 fixture shape
**Source:** `tests/test_desc_signature_concat_render_gate.py` (whole file, 296 lines)
**Apply to:** every new/extended fixture this phase (`test_desc_sig_space_render_gate.py` or extension of the concat gate file; `test_confval_field_spacing_render_gate.py` or extension of `test_confval_field_body_render_gate.py`)
- `TYPST_AVAILABLE` try/import skip guard
- `sys.executable -m sphinx -b typstpdf` subprocess invocation (never `uv run`, never `-b typst` alone)
- structural `.typ` content-space-token assert (fails pre-fix, passes post-fix)
- `%PDF` magic-bytes assert on the compiled output
- **NEW this phase (D-07):** required pypdf extracted-text adjacency assert, using the graceful-skip `PYPDF_AVAILABLE` pattern from `test_epigraph_render_gate.py`/`test_wide_table_render_gate.py`/`test_pdf_render_gate.py`

### Sibling-boundary "am I last?" idiom
**Source:** `depart_desc_parameter`, `typsphinx/translator.py:4610`
**Apply to:** the new `depart_field` inter-field separator logic
```python
if node.next_node(descend=False, siblings=True):
    self.add_text('\ntext("  ")\n')
```
(Comma-separator precedent at `depart_desc_parameter` uses the identical `node.next_node(descend=False, siblings=True)` check; `depart_field` reuses the same check with a different separator token and both leading+trailing newlines, per Pitfall 4.)

### "pass/pass lets visit_Text own the emission" idiom
**Source:** `visit_desc_sig_keyword`/`depart_desc_sig_keyword`, `visit_desc_sig_punctuation`/`depart_desc_sig_punctuation`, `visit_desc_sig_operator`/`depart_desc_sig_operator` (all `typsphinx/translator.py`, lines 4804-4847)
**Apply to:** `visit_desc_sig_space`/`depart_desc_sig_space` — the fix is to match this exact shape, not to write new code.

## No Analog Found

None — all three edit sites and both test-file changes have a strong (exact or role-match) in-repo analog; no file in this phase's scope requires falling back to RESEARCH.md's Code Examples in place of a real codebase pattern.

## Metadata

**Analog search scope:** `typsphinx/translator.py` (single file, all edits); `tests/test_desc_signature_concat_render_gate.py`, `tests/test_field_list_in_list_item_render_gate.py`, `tests/fixtures/desc_signature_concat_render_gate/` (test/fixture conventions)
**Files scanned:** 3 read in full/targeted-range (translator.py targeted ranges 4665-4705, 4804-4847; both test files read/grepped in full or targeted ranges)
**Pattern extraction date:** 2026-07-20
</content>

# Phase 34: Inline Math After Text — Separator Fix - Pattern Map

**Mapped:** 2026-07-28
**Files analyzed:** 3 (2 source modifications + 1 new test module with 2 fixture files)
**Analogs found:** 3 / 3

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/translator.py` (`visit_math`, ~line 3936) | translator visitor method (inline leaf node) | transform (doctree node → Typst text emission) | `typsphinx/translator.py` `visit_literal` (line 1282) | exact — same role (leaf inline node, single emission, `raise SkipNode`), same defect class |
| `typsphinx/translator.py` (`visit_math_block`, ~line 3994) | translator visitor method (block-level node, list-item-only separator participation) | transform (doctree node → Typst text emission) | `typsphinx/translator.py` `visit_literal`'s list-item branch (lines 1301-1303, 1355-1357) — narrowed to just the `in_list_item` half, no concat-context participation (math_block is block-level, never a concat-context sibling) | role-match — block node, but only needs the list-item half of the 3-protocol pattern |
| `tests/test_inline_math_after_text_render_gate.py` (new) | test (GATE-01 real-compile regression fixture) | request-response (subprocess `sphinx-build` → filesystem `.typ`/`.pdf` → assertions) | `tests/test_confval_field_body_render_gate.py` | exact — same GATE-0x real-`typst.compile()` regression-gate shape, same subprocess/skipif/assertion structure, explicitly named as precedent by the orchestrator |
| `tests/fixtures/inline_math_after_text_render_gate/{conf.py,index.rst}` (new) | test fixture (minimal Sphinx project) | file I/O (static `.rst`/`conf.py` read by the sphinx-build subprocess) | `tests/fixtures/confval_field_body_render_gate/{conf.py,index.rst}` | exact — identical fixture-project shape (single master doc, `typst_documents` config, `.. confval::`/list-item reST for the fatal-reproducing shape) |

## Pattern Assignments

### `typsphinx/translator.py` — `visit_math` (leaf inline node)

**Analog:** `typsphinx/translator.py` `visit_literal` (lines 1282-1360, read in full)

**Current buggy code** (lines 3936-3982, read in full):
```python
def visit_math(self, node: nodes.math) -> None:
    # Add separator if in paragraph and not first node
    self._add_paragraph_separator()

    # Extract math content
    math_content = node.astext()

    # Task 6.4: Check if this is explicitly marked as Typst native
    is_typst_native = "typst-native" in node.get("classes", [])

    # Task 6.5: Check typst_use_mitex config (default to True)
    use_mitex = getattr(self.builder.config, "typst_use_mitex", True)

    if is_typst_native or not use_mitex:
        if not is_typst_native and not use_mitex:
            math_content = self._convert_latex_to_typst(math_content)
        self.add_text(f"${math_content}$")
    else:
        self.add_text(f"mi(`{math_content}`)")

    # Task 6.3: Add label if present
    if "ids" in node and node["ids"]:
        label = self._namespace_label(self._current_docname(), node["ids"][0])
        self.add_text(f" <{label}>")

    # Skip children to prevent duplicate output of math content
    raise nodes.SkipNode
```

**Analog's 3-protocol separator-participation pattern to copy** (`visit_literal`, lines 1292-1360):
```python
# Add separator if in paragraph and not first node
self._add_paragraph_separator()

# Add separator before the raw() expression.
# In a code-mode concat context (def-list term / link body / desc
# parameter), adjacent inline expressions must be + concatenated
# (except the first); otherwise a list item uses a newline separator.
# Shared with visit_Text via the concat helpers (single source of
# truth), so a raw() that is a term/link/desc sibling is + separated.
if not self._emit_inline_concat_separator():
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")

# ... content-specific emission ...
self.add_text(f'raw("{escaped_code}")')

# Mark that content was added / next element needs a separator
if not self._mark_inline_concat_content():
    if self.in_list_item:
        self.list_item_needs_separator = True

# Skip processing child text nodes (we already got the content)
raise nodes.SkipNode
```

**Fix shape for `visit_math`** (per RESEARCH.md "Recommended Fix Shape", byte-identical guard expressions, only the middle content-emission block and the optional label-anchor emission differ from `visit_literal`):
1. Keep `self._add_paragraph_separator()` unchanged (line 3954) — this is the piece that already makes plain top-level paragraphs work; do not touch it (Pitfall 1).
2. Insert, immediately after it and before the mitex/native branch:
   ```python
   if not self._emit_inline_concat_separator():
       if self.in_list_item and self.list_item_needs_separator:
           self.add_text("\n")
   ```
3. Leave the `math_content` extraction, `is_typst_native`/`use_mitex` branch, `add_text(f"${math_content}$")` / `add_text(f"mi(`{math_content}`)")`, and the label-anchor `add_text(f" <{label}>")` block completely unchanged — one fix point upstream of both branches covers mitex and native identically (RESEARCH.md Anti-Patterns).
4. Insert, immediately after the label-anchor block and before `raise nodes.SkipNode`:
   ```python
   if not self._mark_inline_concat_content():
       if self.in_list_item:
           self.list_item_needs_separator = True
   ```

**Do not** hard-code an unconditional `"\n"` or `" "` — reuses the exact guard-expression pair `visit_literal` and `visit_Text` (lines 1018-1082) already share (RESEARCH.md Anti-Patterns / "Don't Hand-Roll").

---

### `typsphinx/translator.py` — `visit_math_block` (block node, list-item-only)

**Analog:** the list-item half only of `visit_literal`'s pattern (math_block is a block-level node, never a concat-context sibling — RESEARCH.md Open Question 1 / structural note).

**Current code** (lines 3994-4046, read in full) — separator gap is between `self._emit_id_anchors(node)` (line 4019) and the content emission (lines 4030-4039):
```python
def visit_math_block(self, node: nodes.math_block) -> None:
    self._emit_id_anchors(node)

    # Extract math content
    math_content = node.astext()
    is_typst_native = "typst-native" in node.get("classes", [])
    use_mitex = getattr(self.builder.config, "typst_use_mitex", True)

    if is_typst_native or not use_mitex:
        if not is_typst_native and not use_mitex:
            math_content = self._convert_latex_to_typst(math_content)
        self.add_text(f"$ {math_content} $")
    else:
        self.add_text(f"mitex(`{math_content}`)")

    self.add_text("\n\n")
    raise nodes.SkipNode
```

**Fix shape** — insert only the list-item half (no concat-context call; `math_block` structurally never participates in the 5 concat contexts):
```python
if self.in_list_item and self.list_item_needs_separator:
    self.add_text("\n")
```
placed after `self._emit_id_anchors(node)` and before the `is_typst_native` branch; then, after the `self.add_text("\n\n")` trailing-newline emission (which already functions as a block-open marker), set:
```python
if self.in_list_item:
    self.list_item_needs_separator = True
```
before `raise nodes.SkipNode`. This is a scope item flagged by the orchestrator as in-scope for this phase (both `visit_math` and `visit_math_block` share the root cause).

---

### `tests/test_inline_math_after_text_render_gate.py` (new GATE-01 fixture)

**Analog:** `tests/test_confval_field_body_render_gate.py` (192 lines, read in full)

**Structure to copy verbatim (module skeleton)**:
```python
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


@pytest.fixture
def inline_math_after_text_render_gate_dir():
    return Path(__file__).parent / "fixtures" / "inline_math_after_text_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Invoked as ``sys.executable -m sphinx`` (never bare ``sphinx-build`` /
    ``uv run sphinx-build``) — sidesteps the documented NixOS-sandbox
    PATH-shadowing hazard (project memory: "NixOS sandbox test env").
    """
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the inline-math-after-text render gate",
)
class TestInlineMathAfterTextRenderGate:
    def test_typstpdf_separates_inline_math_in_list_item(
        self, inline_math_after_text_render_gate_dir, temp_build_dir
    ):
        result = _run_sphinx_build_typstpdf(
            inline_math_after_text_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "expected semicolon or line break" not in result.stderr
        assert "expected comma" not in result.stderr
        assert "Typst compilation failed" not in result.stderr

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists()
        typ_text = typ_output.read_text(encoding="utf-8")

        # No bare juxtaposition of text(...) directly against mi(/$ (list item).
        assert ')mi(' not in typ_text
        assert ')$' not in typ_text  # guard against text(...)$...$ juxtaposition

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists()
        assert pdf_output.stat().st_size > 0
        with open(pdf_output, "rb") as f:
            assert f.read(4) == b"%PDF"

        # SC#3 content-fidelity check via pypdf (mirrors
        # test_wide_table_render_gate.py's text-extraction idiom).
        import pypdf

        reader = pypdf.PdfReader(str(pdf_output))
        text = "\n".join(page.extract_text() for page in reader.pages)
        assert "Text before math" in text
        assert "text after" in text
```

**RED-before-fix evidence (SC#4):** run this fixture against the unmodified translator first and capture the verbatim `TypstCompilationError` / `expected semicolon or line break` (or `expected comma`) signature in `result.stderr`, per RESEARCH.md Wave 0 Gaps — this is a required evidence artifact, not just a file to create.

**Second concat-context fixture (Open Question 2, orchestrator-selected: field body):** add a second test method (or a second fixture project reusing the field-body concat context already proven live by `test_confval_field_body_render_gate.py`) with a collapsed field body mixing prose and `:math:`, e.g. `:default: The value of :math:`x` computed inline`. Reuse the identical assertion shape as above, substituting the `field_body`-specific juxtaposition guard (`)mi(` / `)$`) for the term/field-body position.

---

### `tests/fixtures/inline_math_after_text_render_gate/{conf.py,index.rst}` (new fixture project)

**Analog:** `tests/fixtures/confval_field_body_render_gate/{conf.py,index.rst}` (read in full)

**`conf.py` pattern to copy** (project metadata + `typst_documents` — index MUST be a master document so `TypstPDFBuilder.finish()` actually compiles, per the analog's comment: "the only build path where the fatal is observable"):
```python
project = "Inline Math After Text Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

typst_documents = [
    ("index", "index", "Inline Math After Text Render Gate", "Test Author"),
]
```

**`index.rst` pattern** — must exercise a list item (per RESEARCH.md, "the single most likely real-world shape") with inline math immediately after text, mirroring the verified-buggy repro from RESEARCH.md's Code Examples section:
```rst
Inline Math After Text Render Gate
===================================

This fixture reproduces the fatal where inline math immediately following
text inside a bullet-list item (whose paragraph is unwrapped from
``par({...})``) juxtaposes against the preceding ``text(...)`` expression
with zero separator characters, aborting the compile with "expected
semicolon or line break".

* Text before math :math:`E=mc^2` text after.

A second construct exercises the definition-list-term concat context
(mitex path):

Term :math:`E=mc^2`
    Definition body text.
```

## Shared Patterns

### 3-protocol leaf-inline-node separator participation
**Source:** `typsphinx/translator.py` `visit_literal` (lines 1282-1360), `visit_Text` (lines 1018-1082)
**Apply to:** `visit_math` (full 3-protocol pattern: paragraph / concat-context / list-item)
```python
self._add_paragraph_separator()
if not self._emit_inline_concat_separator():
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
# ... emit content ...
if not self._mark_inline_concat_content():
    if self.in_list_item:
        self.list_item_needs_separator = True
raise nodes.SkipNode
```

### List-item-only separator participation (block nodes)
**Source:** the `in_list_item`/`list_item_needs_separator` half of the pattern above, isolated (no concat-context call — block nodes are never concat-context siblings)
**Apply to:** `visit_math_block`
```python
if self.in_list_item and self.list_item_needs_separator:
    self.add_text("\n")
# ... emit content ...
if self.in_list_item:
    self.list_item_needs_separator = True
```

### GATE-0x real-compile regression-gate test module shape
**Source:** `tests/test_confval_field_body_render_gate.py` (full file), `tests/fixtures/confval_field_body_render_gate/` (full fixture)
**Apply to:** `tests/test_inline_math_after_text_render_gate.py` + `tests/fixtures/inline_math_after_text_render_gate/`
- `pytest.mark.skipif(not TYPST_AVAILABLE, ...)` gate on `import typst`
- `_run_sphinx_build_typstpdf` subprocess helper invoked as `[sys.executable, "-m", "sphinx", "-b", "typstpdf", ...]` — never bare `sphinx-build` (NixOS sandbox hazard, project memory)
- Assert `result.returncode == 0`, absence of the specific fatal-signature string in `result.stderr`, presence and non-emptiness of `index.pdf` with `%PDF` magic bytes, and exact-substring assertions against the emitted `index.typ` for both the fixed juxtaposition (absent) and the correct separator (present)
- Single master document (`typst_documents` in `conf.py`) so `TypstPDFBuilder.finish()` actually compiles

## No Analog Found

None — all files in scope have a strong, directly-cited existing analog.

## Metadata

**Analog search scope:** `typsphinx/translator.py` (full grep for `visit_math`/`visit_literal`/`visit_Text`/concat-helper block), `tests/` (existing `*_render_gate.py` test modules and their `tests/fixtures/*_render_gate/` projects)
**Files scanned:** `typsphinx/translator.py` (targeted reads: lines 890-1030, 1260-1360, 3936-4055), `tests/test_confval_field_body_render_gate.py` (full), `tests/fixtures/confval_field_body_render_gate/conf.py` + `index.rst` (full), `.planning/phases/34-inline-math-after-text-separator-fix/34-RESEARCH.md` (full)
**Pattern extraction date:** 2026-07-28

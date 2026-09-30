# Phase 19: Block Separation Fixes (Cluster A) - Pattern Map

**Mapped:** 2026-07-20
**Files analyzed:** 6 (1 source file at 5 handler sites + 1 shared helper; 5 test modules, 3 new + 2 extended)
**Analogs found:** 6 / 6 (all matches are exact — same file, in-file precedent)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|---------------|
| `typsphinx/translator.py` — new `_emit_forced_break()` helper | utility | transform (visitor-emission) | `typsphinx/translator.py::add_text` (line 247) + the `list_item_needs_separator` idiom (~30 call sites, e.g. 341-346) | exact (in-file, generalizes existing idiom) |
| `typsphinx/translator.py::visit_paragraph`/`depart_paragraph` (FID-02, lines 661-708) | controller (visitor dispatch) | transform | same function, in-file (its own `in_list_item` early-return branch) | exact |
| `typsphinx/translator.py::visit_desc`/`visit_desc_signature`/`depart_desc_signature` (FID-03, lines 4299-4371) | controller (visitor dispatch) | transform | `visit_desc_signature_line` (lines 4392-4410) — the proven `linebreak()` cosmetic-newline precedent | exact (precedent, needs the Pitfall-1 unconditional-newline correction) |
| `typsphinx/translator.py::depart_rubric` (FID-04, lines 4671-4677) | controller (visitor dispatch) | transform | `visit_desc_signature_line` (4392-4410) + `depart_desc_signature`'s `strong()` delegation (4339-4343) | exact |
| `typsphinx/translator.py::depart_definition_list` (FID-05, lines 1672-1719, `terms()` emission at 1706-1713) | controller (visitor dispatch) | transform | same function, in-file — NOT the shared helper (Pitfall 3); the fix is a `terms(separator: linebreak(), ...)` call-parameter change |
| exact (in-file, one-line param change) |
| `typsphinx/translator.py::depart_desc` (FID-06, lines 4318-4324) | controller (visitor dispatch) | transform | `visit_desc_signature_line` (4392-4410) via the new shared helper | exact |
| `tests/test_paragraph_concat_render_gate.py` (NEW) | test | request-response (subprocess build → filesystem assert) | `tests/test_desc_signature_concat_render_gate.py` | exact (GATE-01 fixture shape) |
| `tests/test_rubric_option_concat_render_gate.py` (NEW) | test | request-response | `tests/test_desc_signature_concat_render_gate.py` | exact |
| `tests/test_desc_bodyless_concat_render_gate.py` (NEW) | test | request-response | `tests/test_deflist_term_concat_render_gate.py` | exact |
| `tests/test_desc_signature_concat_render_gate.py` (EXTEND, add FID-03 test method) | test | request-response | itself (existing module) | exact — same module |
| `tests/test_deflist_term_concat_render_gate.py` (EXTEND, add FID-05 test methods x2) | test | request-response | itself (existing module) | exact — same module |
| `tests/fixtures/paragraph_concat_render_gate/{conf.py,index.rst}` (NEW) | config/fixture | file-I/O | `tests/fixtures/desc_signature_concat_render_gate/{conf.py,index.rst}` | exact |
| `tests/fixtures/rubric_option_concat_render_gate/{conf.py,index.rst}` (NEW) | config/fixture | file-I/O | `tests/fixtures/desc_signature_concat_render_gate/{conf.py,index.rst}` | exact |
| `tests/fixtures/desc_bodyless_concat_render_gate/{conf.py,index.rst}` (NEW) | config/fixture | file-I/O | `tests/fixtures/deflist_term_concat_render_gate/{conf.py,index.rst}` | exact |

## Pattern Assignments

### Shared helper `_emit_forced_break()` (utility, transform)

**Analog:** `typsphinx/translator.py::add_text` (line 247) + `visit_desc_signature_line` (lines 4392-4410) — the repo's own proven "real Typst break, not cosmetic `\n`" idiom, PLUS the ~30-site `list_item_needs_separator` machinery pattern seen throughout the file (e.g. lines 341-346, 935-948, 1088-1096, 4382-4386).

**`add_text` signature to reuse** (line 247-261):
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

**Existing `list_item_needs_separator` idiom to generalize** (`visit_desc_returns`, lines 4382-4386 — smallest clean example of the pattern):
```python
if self.in_list_item and self.list_item_needs_separator:
    self.add_text("\n")
self.add_text('text(" -> ")')
if self.in_list_item:
    self.list_item_needs_separator = True
```

**The precedent this generalizes, and its documented limitation** (`visit_desc_signature_line`, lines 4392-4410):
```python
def visit_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
    """
    Emits a real Typst linebreak() before every line after the first
    (DESC-02) -- a source '\\n' between two code-mode statements is
    proven cosmetic-only (produces zero visual break), so linebreak()
    (Typst stdlib) is required. ...
    """
    if not self._is_first_desc_signature_line:
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text("linebreak()")
        if self.in_list_item:
            self.list_item_needs_separator = True
    self._is_first_desc_signature_line = False
```

**RESEARCH's correction (must be applied — do not copy the precedent verbatim):** this site's trailing separator works "for free" only because it always fires *inside* an already-open `strong({...})` block, where `visit_strong` has locally forced `self.in_list_item = True` for its children (translator.py ~1101-1102). The new helper's SIBLING-boundary call sites (F7, F13, F15) are typically NOT inside such a block (`in_list_item` is `False` in the common case), so the helper MUST append its own unconditional trailing `"\n"` after the break token — never rely on the next node's own conditional check to supply it. Confirmed empirically this session: `linebreak()strong({...})` (zero whitespace) fails to compile with `expected semicolon or line break`; the same content with a newline between compiles cleanly. This is the single most important deviation from the in-repo precedent.

**Recommended implementation (research-verified, place near `add_text`, ~line 261):**
```python
def _emit_forced_break(self, break_token: str) -> None:
    """
    Emit a real Typst stdlib break (parbreak()/linebreak()) as its own
    code-mode statement between two adjacent siblings.
    ...
    """
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    self.add_text(f"{break_token}\n")
    if self.in_list_item:
        self.list_item_needs_separator = True
```

---

### `typsphinx/translator.py::visit_paragraph`/`depart_paragraph` (FID-02 / F1)

**Analog:** the function's own existing `in_list_item` early-return branch (same file, lines 661-708).

**Current code** (lines 682-708 — the exact site to modify):
```python
def visit_paragraph(self, node: nodes.paragraph) -> None:
    ...
    self._emit_id_anchors(node)

    # Skip par() wrapping inside list items
    if self.in_list_item:
        self.in_paragraph = False
        return

    # Start par() with {} content block (no # prefix in code mode)
    self.in_paragraph = True
    self.paragraph_has_content = False
    self.add_text("par({")

def depart_paragraph(self, node: nodes.paragraph) -> None:
    ...
    # Skip closing if inside list items
    if self.in_list_item:
        return

    # Close par({}) content block and add spacing
    self.in_paragraph = False
    self.paragraph_has_content = False
    self.add_text("})\n\n")
```

**Fix pattern (research-verified):** in `visit_paragraph`'s `in_list_item` branch, call `self._emit_forced_break("parbreak()")` before returning; in `depart_paragraph`'s `in_list_item` branch, add `self.list_item_needs_separator = True` (currently MISSING — this is why the helper never fires for the 2nd+ paragraph today). Do NOT wrap list-item paragraphs in `par({...})` — verified pixel-identical to `parbreak()`-inject with a far smaller diff (Pitfall 2).

**Error handling / edge case:** none needed — `_emit_forced_break` is a no-op-safe call for the FIRST paragraph in a list item (`list_item_needs_separator` is `False`, reset in `visit_list_item` line 1434).

---

### `typsphinx/translator.py::visit_desc`/`visit_desc_signature`/`depart_desc_signature` (FID-03 / F7)

**Analog:** `visit_desc_signature_line` (lines 4392-4410) — same `linebreak()`-before-non-first-sibling idiom, one level up (per-`desc_signature` instead of per-`desc_signature_line`).

**Current code** (lines 4299-4343 — the exact sites to modify):
```python
def visit_desc(self, node: addnodes.desc) -> None:
    self._emit_id_anchors(node)

def visit_desc_signature(self, node: addnodes.desc_signature) -> None:
    dummy_strong = nodes.strong()
    self.visit_strong(dummy_strong)
    self._is_first_desc_signature_line = True

def depart_desc_signature(self, node: addnodes.desc_signature) -> None:
    dummy_strong = nodes.strong()
    self.depart_strong(dummy_strong)
    ...
    self.body.append("\n")
```

**Fix pattern:** add a NEW per-`desc` flag `self._is_first_desc_signature = True` in `visit_desc` (mirrors the existing per-`desc_signature` `_is_first_desc_signature_line` flag one level up); in `visit_desc_signature`, call `self._emit_forced_break("linebreak()")` when `not self._is_first_desc_signature`, then set the flag `False`. `depart_desc_signature`'s trailing `self.body.append("\n")` (cosmetic) is untouched — it already works fine as the LAST separator before the next construct since the NEXT `visit_desc_signature` call now supplies its own leading break.

**Test analog note:** the existing `tests/fixtures/desc_signature_concat_render_gate` fixture already exercises C-domain multi-parameter signatures; extend `test_desc_signature_concat_render_gate.py` with a new method targeting sibling `desc_signature`s (e.g. `.. py:function::` with two signature lines, or the existing offline-intersphinx pattern) rather than creating a new fixture.

---

### `typsphinx/translator.py::depart_rubric` (FID-04 / F13)

**Analog:** `depart_desc_signature`'s `strong()` delegation (lines 4339-4343) combined with the `_emit_forced_break` helper.

**Current code** (lines 4671-4677 — the exact site to modify):
```python
def depart_rubric(self, node: nodes.rubric) -> None:
    """Depart a rubric node."""
    # Use strong's depart logic
    dummy_strong = nodes.strong()
    self.depart_strong(dummy_strong)
    # Add extra spacing after rubric
    self.body.append("\n")
```

**Fix pattern:** replace the trailing `self.body.append("\n")` with `self._emit_forced_break("linebreak()")`, unconditionally (rubric always needs separation from what follows — verified harmless at true end-of-document too, no compile error).

---

### `typsphinx/translator.py::depart_definition_list` (FID-05 / F14) — does NOT use the shared helper (Pitfall 3)

**Analog:** the function's own existing `terms()` emission (same file, lines 1706-1713) — a call-parameter change, not a statement-boundary insertion.

**Current code** (lines 1706-1713 — the exact site to modify):
```python
if items:
    items_str = ", ".join(
        f"terms.item({term}, {self._wrap_definition_arg(definition)})"
        for term, definition in items
    )
    self.add_text(f"terms({items_str})\n\n")
else:
    self.add_text("terms()\n\n")
```

**Fix pattern (research-verified, one-line change):** add `separator: linebreak()` as a named argument to BOTH branches:
```python
    self.add_text(f"terms(separator: linebreak(), {items_str})\n\n")
...
    self.add_text("terms(separator: linebreak())\n\n")
```
This is because `terms()`'s default `separator` is a *weak* `h(0.6em)` horizontal space (Typst stdlib default), not a line break — a fundamentally different bug shape from F1/F7/F13/F15 (Typst-layout-default problem, not a missing-statement-separator problem). Do NOT route this through `_emit_forced_break` or splice a `linebreak()` into the term/definition buffer strings.

**Test analog note:** extend `tests/test_deflist_term_concat_render_gate.py` with two new test methods: (a) a definition list nested inside a bullet `list_item`, (b) a definition list term whose definition opens with a nested field/definition list — both reuse the existing fixture-shape pattern in that same file, following its own established `assert 'raw("make.bat") + text(" and ") + raw("Makefile")' in typ_text` structural-assert style but asserting `"terms(separator: linebreak()" in typ_text` instead.

---

### `typsphinx/translator.py::depart_desc` (FID-06 / F15)

**Analog:** the shared `_emit_forced_break` helper, applied unconditionally.

**Current code** (lines 4318-4324 — the exact site to modify):
```python
def depart_desc(self, node: addnodes.desc) -> None:
    """
    Depart a desc node.

    Add spacing after API description blocks.
    """
    self.body.append("\n\n")
```

**Fix pattern:** replace `self.body.append("\n\n")` with `self._emit_forced_break("parbreak()")`, unconditionally at every `depart_desc` — verified idempotent/harmless on the WITH-body-content case (a confval whose last content already ends in `par()`); no double-gap artifact, no need to detect "was this confval body-less."

---

### GATE-01 render-gate test modules (all NEW + EXTEND files)

**Analog:** `tests/test_desc_signature_concat_render_gate.py` and `tests/test_deflist_term_concat_render_gate.py` — both read in full; identical fixture/assertion shape, differing only in the structural-token assert and fixture `.rst` content.

**Imports pattern** (identical across both analogs, lines 1-56 of each):
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
def <name>_render_gate_dir():
    """Return the path to the <name>_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "<name>_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"
```

**NixOS-sandbox-safe subprocess invocation (copy VERBATIM — never `uv run`)** (`test_desc_signature_concat_render_gate.py` lines 71-94, identical in `test_deflist_term_concat_render_gate.py` lines 62-85):
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

**Core GATE-01 assertion pattern (structural token + real compile + %PDF magic)** — from `test_desc_signature_concat_render_gate.py` lines 129-195 (trimmed to the reusable skeleton; each new module swaps only the structural-token assert per D-05):
```python
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the <name> render gate",
)
class Test<Name>RenderGate:
    def test_typstpdf_<behavior>_produces_pdf(self, <name>_render_gate_dir, temp_build_dir):
        result = _run_sphinx_build_typstpdf(<name>_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            f"TypstPDFBuilder.finish() logged a compilation failure:\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # D-05: structural assert -- pre-fix translator emits NO break token
        # at all at this site, so this string is absent pre-fix and present
        # post-fix. Per-finding token:
        #   FID-02: "parbreak()"           (visit_paragraph in_list_item branch)
        #   FID-03: "linebreak()"          (visit_desc_signature non-first branch)
        #   FID-04: "linebreak()"          (depart_rubric)
        #   FID-05: "terms(separator: linebreak()"  (depart_definition_list)
        #   FID-06: "parbreak()"           (depart_desc)
        assert "<break_token>" in typ_text, (
            f"Expected the <break_token> separator to be emitted -- the fix is "
            f"not applied:\n{typ_text}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            f"index.pdf was not produced:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
```

**Fixture-project analog (`conf.py`/`index.rst` pairing):** copy `tests/fixtures/desc_signature_concat_render_gate/{conf.py,index.rst}` (for FID-03 extension and as a structural template for FID-04's new fixture) or `tests/fixtures/deflist_term_concat_render_gate/{conf.py,index.rst}` (for FID-05 extension and as a structural template for FID-02/FID-06's new fixtures) — both are minimal single-page Sphinx projects with no intersphinx/network dependency, matching the "fast, offline" framing in each module's own docstring.

## Shared Patterns

### The `list_item_needs_separator` leading/trailing idiom
**Source:** ~30 call sites throughout `typsphinx/translator.py` (representative: lines 341-346, 935-948, 1088-1096, 4382-4386, 4405-4409)
**Apply to:** the new `_emit_forced_break` helper (which generalizes it) and every one of the four call sites that use the helper (FID-02, FID-03, FID-04, FID-06)
```python
if self.in_list_item and self.list_item_needs_separator:
    self.add_text("\n")
<emit the actual content>
if self.in_list_item:
    self.list_item_needs_separator = True
```

### Cosmetic-`\n`-is-insufficient-in-code-mode idiom
**Source:** `visit_desc_signature_line` (lines 4392-4410), its own docstring citing "a source '\n' between two code-mode statements is proven cosmetic-only"
**Apply to:** all five fix sites — the invariant behind this entire phase; never rely on `\n`/`\n\n` alone for a visible break, always emit `parbreak()`/`linebreak()` (or, for FID-05 only, the `terms()` `separator:` parameter).

### GATE-01 fixture shape (structural `.typ` assert + real compile + `%PDF` magic)
**Source:** `tests/test_desc_signature_concat_render_gate.py`, `tests/test_deflist_term_concat_render_gate.py` (both read in full)
**Apply to:** all 3 new modules + 2 extended modules — see the "Core GATE-01 assertion pattern" excerpt above, copied verbatim except the per-finding token/fixture name.

### NixOS-sandbox `sys.executable -m sphinx` subprocess invocation
**Source:** `_run_sphinx_build_typstpdf` in both analog test modules (identical function body)
**Apply to:** all 3 new modules — copy the function verbatim (never `uv run sphinx-build`).

## No Analog Found

None — every file in scope has an exact in-repo analog (either the same function's own precedent branch, an immediately adjacent visitor in the same file, or one of the two existing GATE-01 test modules).

## Metadata

**Analog search scope:** `typsphinx/translator.py` (full-file grep for `list_item_needs_separator`, `add_text`, and all five target `visit_*`/`depart_*` functions); `tests/*.py` (directory listing of all `*_render_gate.py` modules); the two canonical GATE-01 fixtures read in full.
**Files scanned:** 1 source file (translator.py, ~4700 lines, targeted non-overlapping reads only) + 2 full test-module reads + 1 directory listing (23 existing render-gate modules).
**Pattern extraction date:** 2026-07-20

## PATTERN MAPPING COMPLETE

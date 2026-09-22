# Phase 74: The `doctest_block` Handler, Its Real-Compile Gate, and the Docstring reST Errors - Pattern Map

**Mapped:** 2026-09-20
**Files analyzed:** 5 (2 modified, 3 new)
**Analogs found:** 5 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/translator.py` (`visit_doctest_block`/`depart_doctest_block` + language-line fallback + `visit_toctree` docstring fix) | translator/visitor (node-handler) | transform (doctree node → Typst markup string) | `typsphinx/translator.py`'s own `visit_literal_block`/`depart_literal_block` (same file, sibling method pair) plus `sphinx/writers/html5.py:665` (installed package) | exact |
| `typsphinx/pathfmt.py` (`quote_path` docstring blank-line/indent fix) | utility (module docstring hygiene) | transform (no runtime behavior change) | `typsphinx/translator.py`'s `visit_toctree` docstring — same message class, same fix shape, same file family | exact (same defect class, prior fix already in this file) |
| `tests/test_doctest_block_render_gate.py` (new) | test (render-gate) | request-response (subprocess build) + file-I/O (PDF write) | `tests/test_inline_image_separator_render_gate.py` | exact |
| `tests/fixtures/doctest_block_render_gate/` (new: `conf.py` + `index.rst`) | config/fixture (Sphinx project) | file-I/O (static fixture, no flow) | `tests/fixtures/abbr_pep_separator_render_gate/` (single-master, minimal conf.py shape) | exact |
| D-02 honour-path unit test in `tests/test_translator.py` (new test functions) | test (unit) | transform (direct translator method calls, no Sphinx build) | `tests/test_translator.py::test_literal_block_without_language` / `test_literal_block_with_language` (same file) | exact |

## Pattern Assignments

### `typsphinx/translator.py` — `visit_doctest_block` / `depart_doctest_block` (translator, transform)

**Analog:** `typsphinx/translator.py:2431` (`visit_literal_block`) / `:2576` (`depart_literal_block`), and the installed Sphinx precedent `sphinx/writers/html5.py:665`.

**Delegating-method shape** (Sphinx's own html5 writer, cited in 74-RESEARCH.md § Code Examples):
```python
# sphinx/writers/html5.py:665 (installed package, this repo's .venv, sphinx==9.1.0)
def visit_doctest_block(self, node: Element) -> None:
    self.visit_literal_block(node)
```
D-04 requires the *delegating-call-with-own-docstring* form (not the bare-alias form `sphinx/writers/latex.py:2324`: `visit_doctest_block = visit_literal_block`), so each new method needs its own docstring naming TRN-01 and its own annotation.

**Type-widening target** (`typsphinx/translator.py:2431`, `:2576`):
```python
def visit_literal_block(self, node: nodes.literal_block) -> None:
    ...
def depart_literal_block(self, node: nodes.literal_block) -> None:
```
D-04: both annotations widen to `nodes.literal_block | nodes.doctest_block` (confirmed sibling classes under `FixedTextElement`, not a subclass relationship — `docutils.nodes.doctest_block.__mro__` vs `literal_block.__mro__`, both `(..., FixedTextElement, TextElement, Element, Node, object)`, `issubclass(doctest_block, literal_block)` is `False`).

**Language-resolution fallback line** (`typsphinx/translator.py:2570`):
```python
# today:
language = node.get("language", "")
```
D-03's required shape (read-side fallback only, never `node["language"] = ...` mutation):
```python
language = node.get("language", "") or (
    "python" if isinstance(node, nodes.doctest_block) else ""
)
```

**Everything else `visit_literal_block`/`depart_literal_block` do is reused verbatim by delegation** — no second implementation. Concretely reused (all at `typsphinx/translator.py:2431-2614`, extracted this session):
- id anchoring: `self._emit_id_anchors(node)`
- list-item separator: `if self.in_list_item and self.list_item_needs_separator: self.add_text("\n")`
- `self.in_literal_block = True` (makes `visit_Text`'s `in_literal_block` branch at `:1790-1806` emit raw text unwrapped, preserving `>>>` line breaks)
- list-item `{ }` / `#{` wrapper logic (captioned-vs-not, list-item-vs-not)
- per-block `codly(number-format: none)` / `codly(offset: ...)` / `codly(highlights: (...))` calls
- fence open: `f"```{language}\n"` else `"```\n"`
- fence close in `depart_literal_block`: `self.add_text("\n```\n")`, closing `}` if `in_list_item`, figure-close if captioned, else the plain `self.add_text("\n")` — this unconditional trailing newline is exactly what 74-RESEARCH.md's Context-A finding says resolves the pre-handler compile fatal (`unknown_visit` emits nothing, so a following sibling lands on the same physical Typst line)
- separator re-arm: `if self.in_list_item: self.list_item_needs_separator = True`

### `typsphinx/translator.py` — `visit_toctree` docstring fix (QUA-14) (utility/docstring, transform)

**Analog:** same file, same docstring (this is a repair to an existing docstring, not a new file) — `typsphinx/translator.py:5415-5461`. The measured base-build attributed errors are at docstring-relative lines 5, 6, 21 (`:5421`, `:5422`, `:~5437`), both "Unexpected indentation. [docutils]" / "Block quote ends without a blank line" — a nested-bullet continuation missing a blank line / wrong indent, per 74-RESEARCH.md § Code Sites and § QUA-14 Census Nuance:
```
/home/yuta/Documents/typsphinx/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
/home/yuta/Documents/typsphinx/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
```
Fix shape (Claude's Discretion, CONTEXT.md): minimal — add the missing blank line before the bullet list / fix the continuation indent width; do not restyle prose. Verify by rebuilding a scratch copy and re-grepping the **attributed** message form (see census filter below), never by inspection alone.

### `typsphinx/pathfmt.py` — `quote_path` docstring fix (D-07) (utility/docstring, transform)

**Analog:** the same fix, same file family, applied moments apart to `visit_toctree` above — treat as the reusable minimal-repair pattern. The defect (per 74-RESEARCH.md § QUA-14 Census Nuance) is in the `Delimiter rule (D-01)` bullet-list section of `quote_path`'s module-level docstring (`typsphinx/pathfmt.py:1-`, module docstring, not the function docstring) — read the full docstring (already read this session, lines 1-70 above) before editing; the "both quote characters present" nested-bullet block is the one lacking a preceding blank line. This defect is real per D-07 even though it never reaches a rendered doc page (imported-member exclusion) — constraint 6 requires fixing any census hit in any `typsphinx/` docstring, not only ones that render.

**Census filter to use both before and after the fix** (74-RESEARCH.md § QUA-14 Census Nuance, exact recommended command):
```
LC_ALL=C grep -nE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' <build.log>
```
Record BOTH the raw substring count (`grep -c` on the two bare phrases, unfiltered) and the attributed count at base and tip — the raw count is 10 pre-fix (includes an unrelated, unattributed `sphinx_autodoc_typehints` phantom pair appearing twice, root-caused to `quote_path`'s docstring being probe-parsed as a documentable-candidate-but-never-rendered imported member); only the attributed count is what `build succeeded, N warnings.` reflects and what must go to zero.

---

### `tests/test_doctest_block_render_gate.py` (test, request-response + file-I/O)

**Analog:** `tests/test_inline_image_separator_render_gate.py` (full file read this session).

**Imports + typst-availability guard** (lines 1-40, adapt the module docstring to name TRN-01/TRN-02/GATE-01 instead of IMG-08/09/10):
```python
import difflib
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

**Subprocess build helper** (verbatim-reusable shape, lines ~41-60):
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
        [sys.executable, "-m", "sphinx", "-b", "typstpdf",
         str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )
```

**Module-scoped shared build fixture** (lines ~140-160, adapt names — this phase has ONE master, not 18, so this simplifies to the `test_pdf_render_gate.py`-style single-master pattern the docstring of the analog itself calls out as its "two precedents" — `test_paragraph_concat_render_gate.py` / `test_abbr_pep_separator_render_gate.py` — each compiling exactly one master):
```python
@pytest.fixture(scope="module")
def doctest_block_render_gate_dir():
    """Return the path to the doctest_block_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "doctest_block_render_gate"


@pytest.fixture(scope="module")
def doctest_block_build(doctest_block_render_gate_dir, tmp_path_factory):
    build_dir = tmp_path_factory.mktemp("doctest_block_render_gate") / "_build"
    result = _run_sphinx_build_typstpdf(doctest_block_render_gate_dir, build_dir)
    return result, build_dir
```

**PDF-magic assertion helper** (reusable verbatim, lines ~119-131):
```python
def _assert_pdf_magic(path: Path, docname: str) -> None:
    assert path.exists(), f"{docname}: {path} was not produced"
    assert path.stat().st_size > 0, f"{docname}: {path} is empty"
    with open(path, "rb") as f:
        magic = f.read(4)
        assert magic == b"%PDF", f"{docname}: {path} is not a valid PDF (magic: {magic!r})"
```

**skipif class guard** (line ~132-137):
```python
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the <name> render gate",
)
class Test...:
    ...
```

**Assertions to add per CONTEXT.md D-06/GATE-01 (not present verbatim in the analog, construct fresh):**
- `.typ` line-structure assertion: read the built `.typ` with `open(path, encoding="utf-8")` (text-mode, explicit utf-8 — the analog's stated rationale: "a build's Windows CR-newline write-mode translation cannot spuriously fail this gate"), assert prompts/continuation/output land on separate lines inside a ` ```python ` fence for both context (a) and context (b1)/(b2).
- absence-of-`unknown_visit` assertion: `assert "unknown node type: <doctest_block" not in result.stdout` (and not in stderr) — this exact f-string substring is at `typsphinx/translator.py:5819` (`unknown_visit`), locale-stable since it is never translated.
- real-compile success: `_assert_pdf_magic(...)` on the produced PDF, reusing the helper above.
- RED transcript: per 74-RESEARCH.md's "RED-restore technique" (this repo's own v0.9.2 precedent, `.planning/milestones/v0.9.2-phases/62-.../62-RED-EVIDENCE.md`):
```
git checkout <PHASE_BASE_SHA> -- typsphinx/translator.py
git diff HEAD --numstat -- typsphinx/translator.py   # confirm exact inverse of eventual diff
uv run python -m sphinx -b typstpdf tests/fixtures/doctest_block_render_gate <BUILD_DIR>   # non-zero exit allowed for context (a)
# capture stdout/stderr verbatim, redact only machine-specific absolute paths
git checkout HEAD -- typsphinx/translator.py   # restore, never git stash
```

### `tests/fixtures/doctest_block_render_gate/` (config/fixture, file-I/O)

**Analog:** `tests/fixtures/abbr_pep_separator_render_gate/conf.py` (single-master shape; read verbatim this session):
```python
project = "Abbr PEP Separator Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "master.typ", "Abbr PEP Separator Render Gate", "Test Author"),
]
```
Adapt: `project = "Doctest Block Render Gate"`, keep the `master.typ` target-name de-collision convention (a bare `"index"` target collides with the unconditional docname-derived `index.typ` content file — this is a documented, standing fixture-naming rule, not specific to this analog).

**`index.rst` contents — build from the 74-RESEARCH.md § Fixture Contexts verified reST**, NOT literally copied from any existing fixture (no existing fixture carries a doctest_block). Per D-06 (AMENDED), the fixture needs THREE distinct sections, keyed to the exact verified-working reST in 74-RESEARCH.md:

Context (a) — plain paragraph, WITH trailing content (captures the real pre-handler compile fatal, not just content-collapse):
```rst
Some text before.

>>> 1 + 1
2

Some text after.
```

Context (b1) — definition-list, reproducing the (falsified) `terms.item(...)` claim's actual container shape, for TRN-02's "definition-list / field-body position" wording, with an explicit note (per D-06) on which separator mechanism actually governs it (NOT `in_list_item`; a definition/`field_body` container never sets that flag — `visit_definition`/`visit_field_body` use their own buffering, per 74-RESEARCH.md § Contradictions #2):
```rst
term
    First paragraph of definition.

    >>> 1 + 1
    2
```

Context (b2) — bullet-list item, non-first position, the ONE shape that genuinely exercises `in_list_item`/`list_item_needs_separator` (74-RESEARCH.md § Contradictions #2 recommendation):
```rst
- First paragraph in the item.

  >>> 1 + 1
  2

  Trailing paragraph in the same item.
```

### D-02 honour-path unit test in `tests/test_translator.py` (unit test, transform)

**Analog:** `tests/test_translator.py::test_literal_block_without_language` / `test_literal_block_with_language` (same file, read this session, lines ~1027-1050 onward) — the pattern of constructing a bare node, calling `visit_*`/`visit_Text`/`depart_Text`/`depart_*` directly (no Sphinx build), then asserting on `translator.astext()`:
```python
def test_literal_block_without_language(simple_document, mock_builder):
    """Test that literal blocks without language are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    literal_block = nodes.literal_block(text="def hello():\n    print('Hello')")
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("def hello():\n    print('Hello')"))
    translator.depart_Text(nodes.Text("def hello():\n    print('Hello')"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    assert "```" in output
    assert "def hello():" in output
    assert "print('Hello')" in output
```
`simple_document`/`mock_builder` fixtures already exist at `tests/test_translator.py:12` and are module-level (usable by any new test function in the same file without redefinition).

**New tests to add (exact shape given in 74-RESEARCH.md § Code Examples, already matched to this analog's style):**
```python
def test_doctest_block_honours_existing_language(simple_document, mock_builder):
    from docutils import nodes
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    node = nodes.doctest_block(text=">>> 1 + 1\n2")
    node["language"] = "pycon"  # third-party-set, non-empty
    translator.visit_doctest_block(node)
    translator.visit_Text(nodes.Text(">>> 1 + 1\n2"))
    translator.depart_Text(nodes.Text(">>> 1 + 1\n2"))
    translator.depart_doctest_block(node)

    output = translator.astext()
    assert "```pycon" in output  # honoured, not overwritten to python


def test_doctest_block_defaults_to_python(simple_document, mock_builder):
    from docutils import nodes
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    node = nodes.doctest_block(text=">>> 1 + 1\n2")  # no language set
    translator.visit_doctest_block(node)
    translator.visit_Text(nodes.Text(">>> 1 + 1\n2"))
    translator.depart_Text(nodes.Text(">>> 1 + 1\n2"))
    translator.depart_doctest_block(node)

    output = translator.astext()
    assert "```python" in output
```

## Shared Patterns

### Delegate-wholesale node handler
**Source:** `typsphinx/translator.py:2431-2614` (`visit_literal_block`/`depart_literal_block`), precedent `sphinx/writers/html5.py:665`.
**Apply to:** `visit_doctest_block`/`depart_doctest_block` only — the phase's single translator change.
```python
def visit_doctest_block(self, node: nodes.literal_block | nodes.doctest_block) -> None:
    """TRN-01: doctest_block is a sibling of literal_block under FixedTextElement
    (not a subclass), so it needs its own dispatch entry. Delegates wholesale to
    visit_literal_block -- same shape Sphinx's own html5 writer uses (a delegating
    call, not the bare-alias shape latex/texinfo use)."""
    self.visit_literal_block(node)


def depart_doctest_block(self, node: nodes.literal_block | nodes.doctest_block) -> None:
    """TRN-01: see visit_doctest_block."""
    self.depart_literal_block(node)
```
Never mutate `node["language"]` (D-03) — the fallback lives only in the read line.

### Real-compile GATE-01 acceptance bar
**Source:** `tests/test_inline_image_separator_render_gate.py`, `tests/test_pdf_render_gate.py`.
**Apply to:** `tests/test_doctest_block_render_gate.py` — never assert on `.typ` string content alone; always drive a real `sphinx-build -b typstpdf` subprocess through `typst.compile()` to a written PDF, guarded by `TYPST_AVAILABLE`/`skipif`.

### RED-before-GREEN evidence choreography
**Source:** `.planning/milestones/v0.9.2-phases/62-.../62-RED-EVIDENCE.md` (this repo, committed).
**Apply to:** both the render-gate fixture and the phase's own `-GATE-01`-shaped evidence file: `git checkout <PHASE_BASE_SHA> -- typsphinx/translator.py`, run, capture verbatim, `git checkout HEAD -- typsphinx/translator.py` to restore (never `git stash`).

### Minimal docstring-hygiene repair (QUA-14 class)
**Source:** the pre-existing fix already applied once in this codebase to `visit_toctree`'s docstring (same message class now recurring at `quote_path`).
**Apply to:** `typsphinx/pathfmt.py`'s `quote_path` docstring — add the missing blank line / fix continuation indent around the nested "both quote characters present" bullet, verify via a scratch rebuild + the attributed-grep filter, never restyle prose beyond the minimal fix.

## No Analog Found

None. All five in-scope files/edits have a strong same-file or same-repo-family analog.

## Metadata

**Analog search scope:** `typsphinx/translator.py`, `typsphinx/pathfmt.py`, `tests/test_translator.py`, `tests/test_inline_image_separator_render_gate.py`, `tests/test_pdf_render_gate.py`, `tests/fixtures/abbr_pep_separator_render_gate/`, installed `sphinx` package (`sphinx/writers/html5.py`, `sphinx/writers/latex.py`) in this repo's `.venv`.
**Files scanned:** 8 read/grepped directly this session (all listed above), plus a `tests/fixtures/` directory listing (60+ entries) to confirm no existing doctest-block-shaped fixture exists.
**Pattern extraction date:** 2026-09-20

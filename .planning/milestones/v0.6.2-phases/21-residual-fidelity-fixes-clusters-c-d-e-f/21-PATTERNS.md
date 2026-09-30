# Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F) - Pattern Map

**Mapped:** 2026-07-20
**Files analyzed:** 2 modified (translator.py, base.typ) + 5 new fixture pairs + 5 new gate test modules
**Analogs found:** 7 / 7 (all have exact or role-match analogs; this phase edits existing files and
extends an existing test-fixture idiom, so "analog" mostly means "sibling handler in the same file"
or "existing render-gate module to copy the shape of")

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/translator.py::visit_literal` (FID-10) | translator node-handler | transform (doctree node -> Typst text) | same file, `self.in_table` ZWSP block in the SAME method (~1224-1236) | exact (sibling branch, same method) |
| `typsphinx/translator.py::visit_Text` (FID-11) | translator node-handler | transform | same file, `in_literal_block` early-return guard in the SAME method (~968-970) | exact |
| `typsphinx/translator.py::visit_literal_block` (FID-12) | translator node-handler | transform | same file, existing `in_markup_context`/`codly_prefix` conditional (~1582-1587) | exact (bug is adjacent to this existing pattern, not inside it) |
| `typsphinx/translator.py::visit_target` (FID-13 boundary) | translator node-handler | transform | same file, `visit_reference`'s "concat/newline mutual exclusion" comment block (~3430-3440) documents the identical class of bug (stray separator inside a wrapper) | role-match |
| `typsphinx/translator.py::depart_abbreviation` (FID-14) | translator node-handler | transform | same method, existing unconditional `if explanation:` guard (~4312-4315) | exact (narrow the existing guard) |
| `typsphinx/templates/base.typ` (FID-13 styling, new `show link:` rule) | template / presentation config | transform (Typst show-rule) | `#show: codly-init.with()` + `#codly(languages: codly-languages)` (lines 22-25) — the file's existing pattern for a top-level `#show`/config statement before `#let project(...)` | role-match |
| 5x `tests/fixtures/<finding>_render_gate/{conf.py,index.rst}` | test fixture (Sphinx project) | file-I/O (rST source -> sphinx-build -> .typ/.pdf) | `tests/fixtures/codly_config_leak_render_gate/{conf.py,index.rst}` | exact |
| 5x `tests/test_<finding>_render_gate.py` | test (render-gate) | request-response (subprocess `sphinx-build` invocation) + file-I/O assert | `tests/test_desc_signature_concat_render_gate.py` (structural-only shape, for FID-11/FID-13-styling) and `tests/test_desc_sig_space_render_gate.py` (structural + pypdf adjacency shape, for FID-10/FID-12/FID-13-boundary/FID-14) | exact |

## Pattern Assignments

### `typsphinx/translator.py::visit_literal` (FID-10, ~1198-1255)

**Analog:** the method's own existing `self.in_table` branch, same file, same method.

**Current code (verified this session, lines 1198-1255):**
```python
    def visit_literal(self, node: nodes.literal) -> None:
        self._add_paragraph_separator()
        if not self._emit_inline_concat_separator():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")
        code_content = node.astext()

        if self.in_table:
            # Zero-width space (U+200B) at natural break points ...
            zwsp = chr(0x200B)
            code_content = code_content.replace(".", "." + zwsp).replace(
                "_", "_" + zwsp
            )

        escaped_code = escape_typst_string(code_content)
        self.add_text(f'raw("{escaped_code}")')
        if not self._mark_inline_concat_content():
            if self.in_list_item:
                self.list_item_needs_separator = True
        raise nodes.SkipNode
```

**Fix pattern to copy** — an `elif` sibling to the existing `if self.in_table:` block, inserting a
conditional leading ZWSP (see RESEARCH.md Pattern 1 / Pitfall 1 — gate the insertion on
`code_content` starting with a UAX14 no-break-before character, e.g. `:;,)]}!?`, to avoid the
44 existing `raw("...")`-exact-match test assertions found via `grep -rn 'raw("' tests/*.py`):
```python
        if self.in_table:
            zwsp = chr(0x200B)
            code_content = code_content.replace(".", "." + zwsp).replace(
                "_", "_" + zwsp
            )
        elif code_content and code_content[0] in ":;,)]}!?":
            # FID-10: leading ZWSP break-opportunity, gated to a narrow
            # UAX14 no-break-before character class so existing exact-match
            # raw("...") assertions elsewhere stay byte-unchanged (Pitfall 1).
            zwsp = chr(0x200B)
            code_content = zwsp + code_content
```
Note: must still call `escape_typst_string` afterward (ZWSP is not special to that helper).

---

### `typsphinx/translator.py::visit_Text` (FID-11, ~952-998)

**Analog:** the method's own existing `in_literal_block` early return (line 968), which establishes
the "guard-then-transform-then-escape" ordering this fix must slot into.

**Fix pattern to copy** — insert the collapse AFTER the `in_literal_block` early return, BEFORE
`escape_typst_string`:
```python
        text_content = node.astext()

        if self.in_literal_block:
            self.add_text(text_content)
            return

        # FID-11: collapse an intra-paragraph soft/semantic source newline to
        # a single space BEFORE escaping, so escape_typst_string's \n -> \\n
        # does not turn it into a Typst-rendered HARD break (Pattern 2).
        text_content = text_content.replace("\n", " ")

        text_content = escape_typst_string(text_content)
```
Verified-safe guard set (per RESEARCH.md Pattern 2): `in_literal_block` already early-returns above
this line; `line_block`/`line` children never carry an embedded `\n` in their own `Text` node
(structural `linebreak()` instead, via `depart_line`); inline `raw()`/literal content never routes
through `visit_Text` at all (it calls `escape_typst_string` directly on `node.astext()` inside
`visit_literal`).

---

### `typsphinx/translator.py::visit_literal_block` (FID-12, ~1516-1645) / `depart_literal_block` (~1646-1690)

**Analog:** the existing `in_markup_context`/`codly_prefix` conditional immediately below the bug
site (~1582-1587) — same "mode-conditional prefix" shape, applied to the WRONG statement pre-fix.

**Current buggy code (lines 1562-1587):**
```python
        # If in list item, wrap codly() calls and code block in { } to make it an expression
        if self.in_list_item:
            self.add_text("{\n")
        ...
        in_markup_context = (
            self.in_captioned_code_block
            and self.code_block_caption
            and not self.in_list_item
        )
        codly_prefix = "#" if in_markup_context else ""
```

**Fix pattern to copy** — apply the SAME `#`-prefix idea to the wrapper's own opening brace, only
when captioned AND in a list item (the case currently missing it); `codly_prefix`'s own predicate
stays unchanged (it was already correct):
```python
        # If in list item, wrap codly() calls and code block in { } to make it
        # an expression. FID-12: when we're ALSO inside a captioned figure's
        # markup-mode [...] content, a bare '{' is parsed as LITERAL TEXT
        # (Pitfall 3) -- it needs a leading '#' to re-enter code mode.
        if self.in_list_item:
            wrapper_prefix = "#" if (
                self.in_captioned_code_block and self.code_block_caption
            ) else ""
            self.add_text(f"{wrapper_prefix}{{\n")
        ...
        in_markup_context = (   # UNCHANGED
            self.in_captioned_code_block
            and self.code_block_caption
            and not self.in_list_item
        )
        codly_prefix = "#" if in_markup_context else ""
```
`depart_literal_block`'s `if self.in_list_item: self.add_text("}")` (closing brace, ~1662-1663)
needs NO change (Typst's `#{ ... }` code-embed only needs the sigil once, at the opening brace).

---

### `typsphinx/translator.py::visit_target` (FID-13 boundary, ~2747-2811)

**Analog:** none needed within this method beyond itself — this is a one-line drop of a leading
`\n`. Cross-reference for "mode matters" reasoning: `visit_reference`'s own comment block on
concat/newline mutual exclusion (~3430-3440), same bug CLASS (a separator character emitted where
none is syntactically needed).

**Current buggy code (line 2766, inside the `_in_reference_with_target` branch, ~2754-2776):**
```python
            self._in_markup_mode = True
            if node.get("ids"):
                label_id = self._namespace_label(
                    self._current_docname(), node["ids"][0]
                )
                self.add_text(f'\n#label("{label_id}")')
            self.add_text("]")
```

**Fix pattern to copy** — drop the leading `\n` (a newline inside Typst MARKUP mode renders as a
visible space, Pitfall 2 — the preceding content is always the closing `)` of the `link(...)` call
opened by `visit_reference`, so `)#label(` needs no separator):
```python
                self.add_text(f'#label("{label_id}")')  # FID-13: no leading \n
```
Note: `visit_reference`/`depart_reference` themselves need NO change for the boundary bug (contrary
to 21-CONTEXT.md's approximate pointer) — RESEARCH.md confirmed the fix site is `visit_target`
alone.

---

### `typsphinx/templates/base.typ` (FID-13 styling — new `show link:` rule)

**Analog:** the file's existing top-level `#show`/config statement pattern (lines 21-25), which
establishes where a document-wide Typst styling directive belongs relative to the `@preview`
imports and `#let project(...)` definition.

**Insertion point** — immediately after line 25 (`#codly(languages: codly-languages)`), before the
`#let project(...)` block (line 27):
```typst
// Initialize codly
#show: codly-init.with()

// Configure codly with codly-languages for comprehensive language support
#codly(languages: codly-languages)

// FID-13: distinguish external hyperlinks with color + underline. Scoped to
// external URLs only (it.dest is a str) -- internal cross-references
// (link(<label>, ...)) have a label-typed dest and stay unstyled (D-02).
#show link: it => {
  if type(it.dest) == str {
    underline(text(fill: blue, it.body))
  } else {
    it
  }
}

#let project(
```
This does NOT touch the four `@preview` import lines (8-19) — version-sync surface stays untouched,
verified by keeping `tests/test_preview_version_sync.py` green.

---

### `typsphinx/translator.py::depart_abbreviation` (FID-14, ~4293-4315)

**Analog:** the method's own existing unconditional `if explanation:` guard — narrow it in place,
no new method needed.

**Current code (lines 4301-4315):**
```python
    def depart_abbreviation(self, node: nodes.abbreviation) -> None:
        explanation = node.get("explanation", "")
        if explanation:
            dummy_text = nodes.Text(f" ({explanation})")
            self.visit_Text(dummy_text)
```

**Fix pattern to copy:**
```python
    def depart_abbreviation(self, node: nodes.abbreviation) -> None:
        explanation = node.get("explanation", "")
        # FID-14: suppress ONLY the auto-generated PEP 3102 '*' / PEP 570 '/'
        # signature separators (their OWN abbreviation-node text is exactly
        # "*" or "/", the sole reliable, narrow-scope signal -- D-Disc-3). A
        # genuine :abbr: role's acronym text is never bare "*"/"/", so this
        # keeps its inline expansion unchanged.
        if explanation and node.astext() not in ("*", "/"):
            dummy_text = nodes.Text(f" ({explanation})")
            self.visit_Text(dummy_text)
```
`visit_abbreviation` (already `pass`) and `visit_desc_sig_operator`/`depart_desc_sig_operator`
(confirmed pure no-ops, ~4870-4876) need NO changes.

---

### 5x new fixture Sphinx projects (`tests/fixtures/<finding>_render_gate/{conf.py,index.rst}`)

**Analog:** `tests/fixtures/codly_config_leak_render_gate/{conf.py,index.rst}` — minimal
self-contained project, ~913-byte conf.py, ~1.4KB index.rst with sentinel tokens.

**conf.py pattern to copy verbatim (only the docstring/project name/comment need adjusting):**
```python
# Sphinx configuration for the <finding> render-gate fixture.
project = "<Finding Name> Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "<Finding Name> Render Gate", "Test Author"),
]
```

**index.rst pattern:** a title + one or more sections, each isolating exactly the finding's repro
shape, with sentinel/unambiguous marker tokens (avoid incidental substring collisions with the
assertion strings, as `codly_config_leak_render_gate`'s own docstring explicitly calls out
"deliberately avoids naming the leaked tokens so the test's body sweep is unambiguous"). Per-finding
repro shapes (from RESEARCH.md's "Wave 0 Gaps"):
- FID-10: a paragraph with a long run of `` ``:cpp:any:`` ``-style double-backtick literal role
  tokens (colon-prefixed), matching `usage/domains/cpp` p.85.
- FID-11: a paragraph with a source-level soft/semantic line break and NO other inline markup at
  the break point (single merged `Text` node), plus a second paragraph with the break adjacent to
  an inline literal.
- FID-12: a captioned `.. code-block::` nested inside a numbered `list_item`. Consider EXTENDING
  `tests/fixtures/codly_config_leak_render_gate/index.rst` with a third section for this exact
  combo (it already documents 2 sibling cases and its conf.py/purpose statement generalizes
  cleanly) rather than creating an all-new fixture — per CONTEXT.md's "Fixture granularity" default
  ("extending existing gate modules where a direct analog exists").
- FID-13: a named external hyperlink (`` `text <url>`_ ``) immediately followed by a period with an
  RST-boundary space, PLUS a same-document internal reference, in ONE fixture (tests D-02 scoping
  and D-03 boundary in one compile).
- FID-14: a `py:function` signature with both a `*` and a `/` separator, PLUS a genuine `:abbr:`
  role usage in the SAME fixture (tests D-Disc-3's "genuine :abbr: keeps expansion").

---

### 5x new `tests/test_<finding>_render_gate.py` modules

**Two analog shapes, split by D-07/D-08/D-09/D-10's text-extractability rule:**

**Shape A — structural-.typ-assert-only** (`tests/test_desc_signature_concat_render_gate.py`,
296 lines) — use for **FID-11** (D-08, pypdf explicitly rejected) and **FID-13-styling**
(D-10, `show link:` rule presence is not text-extractable):
- `TYPST_AVAILABLE` try/import guard + `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` class
- `_run_sphinx_build_typstpdf()` helper — copy verbatim (subprocess `sys.executable -m sphinx -b
  typstpdf`, `capture_output=True, text=True`; NEVER `uv run sphinx-build`, per the NixOS-sandbox
  PATH-shadowing hazard documented in the module docstring and CLAUDE.md)
- Assert `result.returncode == 0` + `"Typst compilation failed" not in result.stderr`
- Read `temp_build_dir / "index.typ"`, assert the specific structural token/absence
  (e.g. for FID-11: assert NO intra-paragraph `\n` escape inside the affected `text("...")` call;
  for FID-13-styling: assert `"show link:"` present in the rendered `base.typ`/emitted template
  output, or that `link("http` appears un-suppressed in `index.typ` for the external ref)
- Read `temp_build_dir / "index.pdf"`, assert exists, non-empty, `%PDF` magic bytes

**Shape B — structural assert + pypdf extracted-text adjacency assert**
(`tests/test_desc_sig_space_render_gate.py`, 254 lines) — use for **FID-10**, **FID-12**,
**FID-13-boundary**, **FID-14** (D-09/D-10):
- Same Shape-A skeleton PLUS a second `PYPDF_AVAILABLE` try/import guard
- Two test methods per class: `test_typstpdf_..._produces_pdf_with_structural_...` (structural-only,
  same shape as A) and `test_pdf_extracted_text_has_...` (guarded by
  `@pytest.mark.skipif(not PYPDF_AVAILABLE, ...)`), which does:
  ```python
  reader = pypdf.PdfReader(str(pdf_output))
  full_text = "\n".join(page.extract_text() for page in reader.pages)
  assert "<expected present string>" in full_text
  assert "<pre-fix merged/leaked/stray string>" not in full_text
  ```
  Per-finding adjacency asserts (from RESEARCH.md D-09/D-10 + "Code Examples"):
  - FID-10: all role-token strings present (e.g. `:cpp:enumerator:`) = no content loss.
  - FID-12: `codly(` / bare `{`/`}` wrapper text ABSENT from extracted prose.
  - FID-13-boundary: single space present (`"documentation ."`), the double-space pre-fix form
    ABSENT (`"documentation  ."`).
  - FID-14: `"(Keyword-only parameters separator"` / `"(Positional-only parameter separator"`
    ABSENT; the genuine `:abbr:` fixture's own explanation string still PRESENT.

## Shared Patterns

### Render-gate subprocess invocation (all 5 new test modules)
**Source:** `tests/test_desc_signature_concat_render_gate.py:77-100` and
`tests/test_desc_sig_space_render_gate.py:72-95` (byte-identical helper in both)
**Apply to:** every new `test_<finding>_render_gate.py`
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
Invoked as `sys.executable -m sphinx` (never `uv run sphinx-build`) — sidesteps the NixOS-sandbox
PATH-shadowing hazard (see project MEMORY.md "NixOS sandbox test env").

### PDF-magic-bytes assert (all 5 new test modules)
**Source:** both analog files, final lines of every test method
**Apply to:** every new test module's structural test
```python
pdf_output = temp_build_dir / "index.pdf"
assert pdf_output.exists(), "index.pdf was not produced..."
assert pdf_output.stat().st_size > 0, "PDF file is empty"
with open(pdf_output, "rb") as f:
    magic = f.read(4)
    assert magic == b"%PDF", "Generated file is not a valid PDF"
```

### Minimal fixture Sphinx project (all 5 new fixtures)
**Source:** `tests/fixtures/codly_config_leak_render_gate/conf.py`
**Apply to:** every new `tests/fixtures/<finding>_render_gate/conf.py`
```python
extensions = ["typsphinx"]
typst_documents = [
    ("index", "index", "<Title>", "Test Author"),
]
```

### V5 Input Validation — `escape_typst_string` single choke point
**Source:** `typsphinx/translator.py:24-55`
**Apply to:** FID-11 (collapse happens strictly BEFORE this call, does not bypass it), FID-14
(explanation text unchanged in routing — still via `visit_Text` -> this helper); FID-10's ZWSP is a
Python literal constant, not user-controlled, so it is inserted before this call with no new
injection surface. No fix in this phase adds a new unescaped-output path (RESEARCH.md's Security
Domain section confirms this for all five).

## No Analog Found

None — every file in this phase either modifies an existing handler (translator.py, base.typ) with
a same-file sibling pattern to copy, or extends the well-established render-gate fixture/test-module
idiom with two directly-reusable shapes (A: structural-only: D-08 family; B: structural+pypdf: D-09/
D-10 family).

## Metadata

**Analog search scope:** `typsphinx/translator.py`, `typsphinx/templates/base.typ`, `tests/`,
`tests/fixtures/codly_config_leak_render_gate/`
**Files scanned:** 2 source files (targeted reads at 6 non-overlapping handler ranges) + 2 render-
gate test modules (full reads, 296 + 254 lines) + 1 fixture project (conf.py + index.rst, full
reads) + `grep -n 'def visit_/depart_'` sweep of translator.py for line-number verification
**Pattern extraction date:** 2026-07-20
**Note on line-number drift:** all six translator.py fix-site line numbers were re-verified this
session via direct `grep`/`Read` (not trusted from CONTEXT.md's approximate pointers): `visit_Text`
952, `visit_literal` 1198, `visit_literal_block`/`depart_literal_block` 1516/1646, `visit_target`/
`depart_target` 2747/2813, `visit_reference`/`depart_reference` 3384/3561, `visit_abbreviation`/
`depart_abbreviation` 4293/4301 — all match RESEARCH.md's independently-verified numbers exactly
(no further drift since RESEARCH.md was written earlier the same session).

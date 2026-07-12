# Phase 13: Shared Dispatch-Point Changes (topic + line blocks) - Pattern Map

**Mapped:** 2026-07-12
**Files analyzed:** 5 (1 modified source file, 1 modified test file, 2 new fixture files, 1 new/extended unit-test target)
**Analogs found:** 5 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/translator.py` — `visit_title`/`depart_title` generalization (D-02, D-05, D-06, Pitfall-1 fix) | translator/dispatch (visitor method) | transform (doctree node → Typst text stream) | `typsphinx/translator.py:206-283` (itself — in-place edit) + `visit_emphasis`/`visit_strong` (:560-628) for the "treat it like list_item" child-separator idiom | exact (self) + role-match (separator idiom) |
| `typsphinx/translator.py` — new `visit_topic`/`depart_topic` | translator/dispatch (visitor method) | transform | `_visit_admonition`/`_depart_admonition` (:2470-2523) and `visit_admonition`/`depart_admonition` (:2618-2632) | exact |
| `typsphinx/translator.py` — new `visit_line_block`/`depart_line_block`/`visit_line`/`depart_line` | translator/dispatch (visitor method) | transform, streaming (verbatim line breaks) | `visit_desc_signature_line`/`depart_desc_signature_line` (:2887-2909) for the `linebreak()` precedent; `visit_paragraph`/`depart_paragraph` (:382-421) for the `par({...})` wrap/state-restore idiom | role-match |
| `tests/fixtures/topic_line_block_render_gate/{conf.py,index.rst}` (new) | test fixture (Sphinx project) | file-I/O (static RST/py fixture consumed by subprocess build) | `tests/fixtures/trivial_blocks_render_gate/{conf.py,index.rst}` (most recent analogous fixture, Phase 12) | exact |
| `tests/test_pdf_render_gate.py` — new `TestTopicLineBlockRenderGate` class + fixture-dir fixture | test (integration, real-compile gate) | request-response (subprocess build → compile → extract → assert) | `TestTrivialBlocksRenderGate` (:807-911) and `TestDescSignatureRenderGate` (:676-782) | exact |
| `tests/test_translator.py` or new `tests/test_topics.py`/`tests/test_line_blocks.py` (unit tests for D-02/D-05/D-06 branch logic) | test (unit) | request-response (translator method call → string assert) | `tests/test_admonitions.py` (`test_admonition_with_title_in_content`, `test_admonition_title_preserves_inline_markup`, `test_generic_admonition_converts_to_clue`) | exact |

## Pattern Assignments

### `typsphinx/translator.py` — generalized `visit_title`/`depart_title` (D-02/D-05/D-06 + Pitfall-1 fix)

**Analog:** the method's own current body (`translator.py:206-283`), edited in place; separator idiom borrowed from `visit_emphasis`/`visit_strong` (`translator.py:560-628`).

**Current code to generalize** (verified against real source, `translator.py:206-283`):
```python
def visit_title(self, node: nodes.title) -> None:
    # Admonition titles are deferred: buffer-swap the body so the title's
    # inline children render through the normal visitors (preserving
    # emphasis/literal/etc.) without touching the main output stream.
    if isinstance(node.parent, nodes.Admonition):
        self._saved_body_for_admonition_title = self.body
        self.body = []
        self._in_admonition_title = True
        return

    self._title_section_ids = (
        node.parent.get("ids") if isinstance(node.parent, nodes.section) else None
    ) or []
    if self._title_section_ids:
        self.add_text(f"[#heading(level: {self.section_level}, ")
    else:
        # Use heading() function (no # prefix in code mode)
        self.add_text(f"heading(level: {self.section_level}, ")

def depart_title(self, node: nodes.title) -> None:
    if self._in_admonition_title:
        self._pending_admonition_title = "".join(self.body)
        if self._saved_body_for_admonition_title is not None:
            self.body = self._saved_body_for_admonition_title
        self._saved_body_for_admonition_title = None
        self._in_admonition_title = False
        return

    if self._title_section_ids:
        primary_id, *extra_ids = self._title_section_ids
        self.add_text(f") <{primary_id}>]\n")
        for extra_id in extra_ids:
            self.add_text(f"[#metadata(none) <{extra_id}>]\n")
        self.add_text("\n")
    else:
        self.add_text(")\n\n")
    self._title_section_ids = []
```

**D-02 change:** widen `isinstance(node.parent, nodes.Admonition)` to
`isinstance(node.parent, nodes.Admonition) or isinstance(node.parent, nodes.topic)`.
`nodes.topic` is confirmed NOT a subclass of `nodes.Admonition`
(RESEARCH.md "Verified Mechanism 1"), so this must be a literal `or`, not an
MRO/mixin trick — this is a pure additive branch-entry widening; the existing
`nodes.Admonition` regression path is untouched by construction.

**D-05 change:** inside the same buffer-swap branch, detect
`isinstance(node.parent, nodes.topic) and "contents" in (node.parent.get("classes", []) or [])`
and record `self._contents_title_insert_at = len(self.body)` before swapping
— this index is later used at `depart_title` (NOT `depart_topic`, because
`_pending_admonition_title` only becomes available there) to
`self.body.insert(...)` the bold label ahead of the already-streamed
`bullet_list` output. See RESEARCH.md "Verified Mechanism 3" for the full
insert-index code (already vetted end-to-end); reuse it verbatim.

**D-06 change:** in the plain-heading (`else`) branch, replace every
`self.section_level` interpolation with `max(1, self.section_level)` —
apply the clamp in both `visit_title` (`heading(level: {emitted}, `) and
nowhere else (the closing `depart_title` branch doesn't re-emit the level
number, so only the two `add_text` calls in `visit_title`'s `else` need the
substitution).

**Pitfall-1 fix (mandatory, same method, must be bundled — see RESEARCH.md
"Pitfall 1"):** wrap this borrowed idiom from `visit_emphasis`
(`translator.py:581-599`, `618-628`) around the ENTIRE `visit_title`/
`depart_title` body (both branches, every return path):
```python
# Since a title's own children (Text, emphasis, strong, ...) currently
# concatenate with NO separator (visit_emphasis/visit_strong's own
# "treat it like list_item" trick doesn't apply to titles themselves),
# treat title content itself like list_item content:
self._title_was_in_list_item = self.in_list_item
self._title_was_list_item_needs_separator = self.list_item_needs_separator
self.in_list_item = True
self.list_item_needs_separator = False
# ... (restore both in depart_title, in EVERY return path, admonition
# branch's early return included)
```
and wrap the plain-heading branch's content in a code block `{...}` (not
bare positional args) exactly as `_depart_admonition` already does for the
admonition title (`translator.py:2516`: `title_expr = "{" + self._pending_admonition_title + "}"`)
— i.e. `heading(level: {emitted}, {` ... `})` instead of
`heading(level: {emitted}, ` ... `)`. See RESEARCH.md "Code Examples" section
("Full generalized visit_title/depart_title") for the complete, verified-
compiling replacement to copy near-verbatim.

---

### `typsphinx/translator.py` — new `visit_topic`/`depart_topic` (D-01/D-02/D-05)

**Analog:** `_visit_admonition`/`_depart_admonition` (`translator.py:2470-2523`) and the thin per-type wrapper idiom every existing admonition type already uses, e.g. `visit_admonition`/`depart_admonition` (`translator.py:2618-2632`):
```python
def visit_admonition(self, node: nodes.admonition) -> None:
    """Visit a generic ``.. admonition::`` (converts to #clue[])."""
    self._visit_admonition(node, "clue")

def depart_admonition(self, node: nodes.admonition) -> None:
    """Depart a generic admonition."""
    self._depart_admonition()
```

**New code (verified compiling end-to-end in RESEARCH.md "Verified Mechanism 1"):**
```python
def visit_topic(self, node: nodes.topic) -> None:
    self._topic_is_contents = "contents" in (node.get("classes", []) or [])
    if self._topic_is_contents:
        return  # D-05: box-less, title/list handled via visit_title + existing list visitors
    self._visit_admonition(node, "clue")

def depart_topic(self, node: nodes.topic) -> None:
    if self._topic_is_contents:
        self._topic_is_contents = False
        return
    self._depart_admonition()
```

Place these methods in the same "Admonition nodes" section of the file
(near `visit_admonition`/`depart_admonition`, `translator.py:2618-2632`) since
they share `_visit_admonition`'s helper contract.

**D-05 note (contents pass-through):** no new list-rendering code is needed —
Sphinx already resolves `.. contents::` into a `topic` (classes
`["contents", "local"]`) wrapping a plain `bullet_list` of `reference`
nodes wrapped in `paragraph`s (RESEARCH.md "Verified Mechanism 3"). The
existing `visit_paragraph`'s list-item skip guard (`translator.py:395-398`,
`if self.in_list_item: self.in_paragraph = False; return`) and the existing
`visit_bullet_list`/`visit_list_item`/`visit_reference` chain (unmodified)
already produce correct output for this child subtree.

---

### `typsphinx/translator.py` — new `visit_line_block`/`depart_line_block`/`visit_line`/`depart_line` (D-03/D-04)

**Analog 1 (linebreak() precedent):** `visit_desc_signature_line`/`depart_desc_signature_line` (`translator.py:2887-2909`):
```python
def visit_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
    if not self._is_first_desc_signature_line:
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text("linebreak()")
        if self.in_list_item:
            self.list_item_needs_separator = True
    self._is_first_desc_signature_line = False

def depart_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
    pass
```
This is the proven precedent that a source `"\n"` between two code-mode
statements is cosmetic-only and a real `linebreak()` call is required for a
visible break — carried forward directly into `depart_line`.

**Analog 2 (par({...}) wrap/state-restore idiom):** `visit_paragraph`/`depart_paragraph` (`translator.py:382-421`) for the "open a code-mode content block, track `in_paragraph`/`paragraph_has_content`, restore on depart" shape that `visit_line_block`/`depart_line_block` mirrors for its own `par({...})` wrapper.

**Analog 3 (`_add_paragraph_separator`):** `translator.py:148-158` — the `+`/`\n` concatenation helper every content-emitting visitor calls first; `visit_line` calls this exactly like every other inline/block visitor.

**New code (verified compiling + real pypdf-extraction-proven in RESEARCH.md "Verified Mechanism 2" — copy near-verbatim):**
```python
def visit_line_block(self, node: nodes.line_block) -> None:
    depth = getattr(self, "_line_block_depth", 0)
    if depth == 0:
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self._line_block_was_in_paragraph = self.in_paragraph
        self._line_block_was_paragraph_has_content = self.paragraph_has_content
        self.add_text("par({")
        self.in_paragraph = True
        self.paragraph_has_content = False
    self._line_block_depth = depth + 1

def depart_line_block(self, node: nodes.line_block) -> None:
    self._line_block_depth -= 1
    if self._line_block_depth == 0:
        self.add_text("})\n\n")
        self.in_paragraph = self._line_block_was_in_paragraph
        self.paragraph_has_content = self._line_block_was_paragraph_has_content
        if self.in_list_item:
            self.list_item_needs_separator = True

def visit_line(self, node: nodes.line) -> None:
    self._add_paragraph_separator()
    indent_units = self._line_block_depth - 1
    if indent_units > 0:
        self.add_text(f"h({indent_units * 1.5}em)")

def depart_line(self, node: nodes.line) -> None:
    self.add_text("\nlinebreak()")
```
Depth tracking is a single integer (`self._line_block_depth`), incremented/
decremented in `visit_line_block`/`depart_line_block` — no separate nesting
stack needed (docutils' own visitor recursion provides that for free; see
RESEARCH.md "Don't Hand-Roll" table). `h()` needs NO Phase-11 markup-mode
bracket-wrap (it's a plain code-mode content-returning stdlib call, unlike
`<label>` anchors) — do not reach for `pad(left: ...)[...]`, which would
need a markup-mode argument for no benefit here.

Place these four methods near `visit_desc_signature_line` or in a new
"Line block nodes (BLK-03)" section; initialize `self._line_block_depth = 0`
alongside the other per-document reset state (search for where
`_is_first_desc_signature_line`/`in_paragraph` are reset in `visit_document`,
if such a reset exists, or lazily via `getattr(..., 0)` as shown above).

---

### `tests/fixtures/topic_line_block_render_gate/{conf.py,index.rst}` (new fixture)

**Analog:** `tests/fixtures/trivial_blocks_render_gate/{conf.py,index.rst}` (Phase 12, most recent analogous fixture).

**conf.py pattern** (copy structure verbatim, rename project/title):
```python
# Sphinx configuration for the BLK-02/BLK-03 topic+line_block render-gate
# fixture.
project = "Topic Line Block Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

typst_documents = [
    ("index", "index", "Topic Line Block Render Gate", "Test Author"),
]
```

**index.rst pattern:** mirror `trivial_blocks_render_gate/index.rst`'s
"one section per node type, distinctive ALLCAPS sentinel tokens" shape.
RESEARCH.md's Wave-0-Gaps section states the exact combination that was
already verified to compile cleanly this research session — lift near-
verbatim:
- a `.. topic::` with a **multi-child title** (e.g. `A Topic *Title*`) to
  prove the Pitfall-1 fix, containing a `TOPICBODYSENTINEL` paragraph;
- a `.. contents::` local TOC (auto-detects `'contents'` class, D-05);
- a plain top-level `line_block` (no `.. epigraph::` wrapper — Pitfall 4)
  titled "Address" with `ADDRESSLINEONE`/`ADDRESSLINETWO` sentinels;
- a plain top-level `line_block` with one level of nesting titled "Poem"
  with `POEMLINEONE`/`POEMNESTEDONE`/`POEMNESTEDTWO`/`POEMLINETHREE`
  sentinels (the nested-indentation D-03/D-04 proof);
- a `.. note::`/`.. warning::`/`.. admonition:: Custom *Title*` regression
  block (SC#3, also exercises the Pitfall-1 fix for the pre-existing
  admonition-title path).

**Do NOT use `.. epigraph::`** — it hits two unrelated pre-existing bugs
(RESEARCH.md "Pitfall 4"): a hard fatal (with attribution) and a literal-
source leak (without). Use a plain top-level `line_block` under a titled
section instead — verified compile-safe and semantically equivalent for
proving BLK-03.

---

### `tests/test_pdf_render_gate.py` — new `TestTopicLineBlockRenderGate` class

**Analog:** `TestTrivialBlocksRenderGate` (`:807-911`) and `TestDescSignatureRenderGate` (`:676-782`) — both follow the identical structure: `_run_sphinx_build_typst` → assert `returncode == 0` → assert `.typ` exists → uncaught `typst.compile()` (so a real fatal propagates and fails the test loudly) → assert PDF exists/non-empty/`%PDF` magic → `pypdf.PdfReader` text-extraction → per-requirement sentinel assertions → shared `LEAK_SIGNATURES` negative-control loop at the end.

**Fixture-dir fixture pattern** (`:91-94`, add alongside the existing ones):
```python
@pytest.fixture
def topic_line_block_render_gate_dir(fixtures_dir):
    """Return the path to the topic_line_block_render_gate fixture project."""
    return fixtures_dir / "topic_line_block_render_gate"
```

**Class skeleton to copy** (from `TestTrivialBlocksRenderGate`, `:802-911`):
```python
@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestTopicLineBlockRenderGate:
    """
    Real-compile acceptance gate for BLK-02/BLK-03: visit_topic/depart_topic
    (clue box + box-less contents pass-through) and visit_line_block/
    visit_line (verbatim linebreak() + nested indent), plus the SC#3
    admonition-title regression (including a multi-child title, Pitfall 1).

    Requirements: BLK-02, BLK-03, GATE-01 (13-CONTEXT.md D-01..D-06,
    13-RESEARCH.md Verified Mechanisms 1-3, 13-0N-PLAN.md).
    """

    def test_topic_line_block_pdf_renders_aside_breaks_and_no_regression(
        self, topic_line_block_render_gate_dir, temp_build_dir
    ):
        result = _run_sphinx_build_typst(topic_line_block_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))  # uncaught -- any fatal fails loudly

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            assert f.read(4) == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        # BLK-02: topic title occurs exactly ONCE (not leaked into the
        # auto-outline as a real heading() would) -- SC#1 proof.
        assert full_text.count("A Topic Title") == 1, (
            "Expected the topic title to appear exactly once in extracted "
            "PDF text (not duplicated into Typst's auto-outline) -- "
            "visit_topic/visit_title generalization regression"
        )
        assert "TOPICBODYSENTINEL" in full_text

        # D-05: contents-topic renders box-less, title + list intact.
        assert "Table of Contents" in full_text
        assert full_text.count("Table of Contents") == 1  # not in auto-outline either

        # BLK-03: address + poem sentinels present, each line separately
        # extracted (never concatenated with no separator -- New-Pitfall-
        # 11-style proof, DESC-02 precedent).
        for sentinel in (
            "ADDRESSLINEONE", "ADDRESSLINETWO",
            "POEMLINEONE", "POEMNESTEDONE", "POEMNESTEDTWO", "POEMLINETHREE",
        ):
            assert sentinel in full_text
        assert "ADDRESSLINEONEADDRESSLINETWO" not in full_text
        assert "POEMLINEONEPOEMNESTEDONE" not in full_text

        # SC#3: admonition-title regression, including multi-child title
        # (Pitfall 1 fix proof).
        assert "Custom Title" in full_text  # note: NOT "Custom Title" + stray tokens

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into rendered "
                "PDF text -- topic/line_block markup/code-mode regression"
            )
```
(Exact sentinel names/assertions are Claude's-discretion per CONTEXT.md;
above mirrors the concrete sentinels RESEARCH.md already used and verified
end-to-end — reuse them rather than inventing new ones.)

---

### `tests/test_translator.py` (or new `tests/test_topics.py`/`tests/test_line_blocks.py`) — unit tests for D-02/D-05/D-06 branch logic

**Analog:** `tests/test_admonitions.py` — `test_admonition_with_title_in_content`, `test_admonition_title_preserves_inline_markup`, `test_generic_admonition_converts_to_clue` (exact same shape: construct a doctree fragment via docutils/Sphinx test app, run translator, assert on generated `.typ` string). Read these three tests directly before writing new ones — they already cover the multi-child-title doctree shape (`nodes.title` with `Text` + `emphasis` children) that Pitfall 1 requires regression coverage for.

**What to test (per RESEARCH.md Validation Architecture table):**
- D-02: a `topic` node's title enters the buffer-swap branch (not the `else` heading branch) — assert generated output contains `clue({` with a `title:` kwarg, never `heading(level:`.
- D-05: a `topic` node with `classes=["contents", "local"]` renders box-less — assert output contains `strong({` for the label and NOT `clue({`.
- D-06: construct a title whose parent section is at `section_level == 0` (or directly call `visit_title`/`depart_title` with a stubbed zero section_level) and assert the emitted level is clamped to `1`, never `0`.
- Pitfall-1 regression: a title with `Text` + `emphasis` children (mirroring `test_admonition_title_preserves_inline_markup`'s existing shape) produces valid, non-concatenated statements (`"\n"`-separated, not bare-juxtaposed) inside both the `heading({...})` and `clue(..., title: {...})` forms.

## Shared Patterns

### Admonition helper reuse (D-01)
**Source:** `typsphinx/translator.py:2470-2523` (`_visit_admonition`/`_depart_admonition`)
**Apply to:** `visit_topic`/`depart_topic` — call the helper exactly as every existing admonition type (`visit_note`, `visit_warning`, ..., `visit_admonition`) already does. Zero new state beyond the `_topic_is_contents` flag; zero new Typst import (the `gentle-clues` `@preview` import is already emitted by the writer for every document since it's used by other admonition types — confirmed no new package-import surface).

### "Treat it like list_item" child-separator idiom
**Source:** `typsphinx/translator.py:581-599` / `618-628` (`visit_emphasis`/`depart_emphasis`), duplicated identically in `visit_strong`/`depart_strong` (`:630-704`)
**Apply to:** the Pitfall-1 fix inside `visit_title`/`depart_title` — this is the exact, already-proven-four-times idiom (`emph`, `strong`, and by extension this title fix) for making a code-block's own children `"\n"`-separate instead of bare-juxtaposing.

### `linebreak()` for verbatim breaks
**Source:** `typsphinx/translator.py:2887-2909` (`visit_desc_signature_line`, DESC-02 precedent)
**Apply to:** `depart_line` — same stdlib call, same "a source `\n` between statements is cosmetic-only" lesson.

### Real-compile gate (GATE-01) structure
**Source:** `tests/test_pdf_render_gate.py:807-911` (`TestTrivialBlocksRenderGate`) and `:676-782` (`TestDescSignatureRenderGate`)
**Apply to:** the new `TestTopicLineBlockRenderGate` class — uncaught `typst.compile()`, `LEAK_SIGNATURES` negative control, sentinel-presence + sentinel-count assertions (the `== 1` count check is the specific new idiom this phase needs, to detect "title leaked into the auto-outline").

### Bracket-wrap only when markup-mode required (Phase 11 lesson)
**Source:** `typsphinx/translator.py:239-246`/`268-279` (title anchor bracket-wrap), reused conceptually (not literally) for the D-04 compile-safety question
**Apply to:** confirms `h()` (plain code-mode stdlib call) needs NO bracket-wrap — only `<label>` anchors (markup-mode-only syntax) require it. Do not over-apply this pattern to `visit_line`.

## No Analog Found

None — all five files/edits have a strong (exact or role-match) analog in the current codebase.

## Metadata

**Analog search scope:** `typsphinx/translator.py` (full-file grep for `def visit_`/`def depart_`/`def _visit_admonition`/`def _depart_admonition`/`def unknown_visit`), `tests/test_pdf_render_gate.py` (full read of fixture-dir fixtures + `TestDescSignatureRenderGate` + `TestTrivialBlocksRenderGate`), `tests/fixtures/trivial_blocks_render_gate/` (conf.py + index.rst), `tests/test_admonitions.py` (referenced, not re-read — already cited with exact test names in RESEARCH.md's Sources section).
**Files scanned:** `typsphinx/translator.py` (~2950 lines, targeted non-overlapping reads: 195-494, 560-690, 2216-2245, 2460-2670, 2870-2920), `tests/test_pdf_render_gate.py` (1-120, 676-911).
**Pattern extraction date:** 2026-07-12
</content>

"""
Tests for Requirement 13: 複数ドキュメントの統合と toctree 処理

This module tests the toctree → #include() conversion functionality
as specified in Requirement 13 of the design document.
"""

import pytest
from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter
from sphinx import addnodes


@pytest.fixture
def simple_document():
    """Create a simple document for testing."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc


@pytest.fixture
def mock_builder():
    """Create a mock builder for testing."""

    class MockConfig:
        pass

    class MockDomains:
        pass

    class MockEnv:
        domains = MockDomains()

    class MockBuilder:
        config = MockConfig()
        env = MockEnv()

    return MockBuilder()


def test_toctree_generates_include_directives(simple_document, mock_builder):
    """
    Test that toctree generates include() directives instead of outline().

    Requirement 13.2: WHEN `addnodes.toctree` ノードが TypstTranslator で処理される
    THEN 参照された各ドキュメントに対して `include("relative/path/to/doc.typ")`
    SHALL 生成される

    Phase 49 (COMP-05/D-03): the emission side now reads the toctree's
    INCLUDE-FILE list, not its entry list -- a hand-built node must set
    ``includefiles`` alongside ``entries`` or it is treated as having no
    children at all (the emission side reads the entry list only to
    resolve titles, which this synthetic node never does).
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a toctree node with entries
    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Introduction", "intro"),
        ("Getting Started", "getting_started"),
        ("API Reference", "api"),
    ]
    toctree["includefiles"] = ["intro", "getting_started", "api"]

    # Visit the toctree node
    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass  # Expected behavior

    output = translator.astext()

    # Should generate include() directives, NOT outline(). Each include()
    # call now lives inside a per-entry compile-time guard line
    # (Phase 49), so a plain substring check still finds it.
    assert "include(" in output
    assert 'include("intro.typ")' in output
    assert 'include("getting_started.typ")' in output
    assert 'include("api.typ")' in output
    assert "outline()" not in output


def test_toctree_with_heading_offset(simple_document, mock_builder):
    """
    Test that toctree generates include() with heading offset.

    Requirement 13.14: WHEN `include()` を生成する際に見出しレベルを調整
    THEN Typst SHALL `context { set heading(offset: heading.offset + 1);
    include("doc.typ") }` のようにスコープブロック内で
    `set heading(offset: heading.offset + 1)` を適用する (D-07: 絶対値ではなく
    コンテキスト相対の増分でなければ、入れ子の toctree スコープが正しく積み上がらない)
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Chapter 1", "chapter1"),
    ]
    # Phase 49 (COMP-05/D-03): the emission side reads includefiles, not
    # entries.
    toctree["includefiles"] = ["chapter1"]

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()

    # Should generate a context-relative heading offset scope block with {...}
    assert "context {" in output
    assert "set heading(offset: heading.offset + 1)" in output
    assert "{\n" in output or "{" in output
    assert "}\n" in output or "}" in output


def test_toctree_with_nested_path(simple_document, mock_builder):
    """
    Test that toctree handles nested document paths correctly.

    Requirement 13.5: WHEN `toctree` で参照されたドキュメントパスが
    "chapter1/section" の場合 THEN Typst SHALL
    `include("chapter1/section.typ")` を生成する
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Chapter 1 Section", "chapter1/section"),
        ("Chapter 2 Subsection", "chapter2/sub/content"),
    ]
    # Phase 49 (COMP-05/D-03): the emission side reads includefiles, not
    # entries.
    toctree["includefiles"] = ["chapter1/section", "chapter2/sub/content"]

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()

    # Should generate nested paths with .typ extension
    assert 'include("chapter1/section.typ")' in output
    assert 'include("chapter2/sub/content.typ")' in output


def test_toctree_empty_entries(simple_document, mock_builder):
    """
    Test that toctree with no entries generates no output at all: no scope
    opener and no include(), because visit_toctree raises SkipNode before
    adding any text (edge case for the D-07 scope-opener rewrite).
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = []
    # Phase 49 (D-03): the emptiness check now reads includefiles, not
    # entries -- set explicitly here for clarity, though both default to
    # empty on a hand-built node with neither key set.
    toctree["includefiles"] = []

    # visit_toctree must raise SkipNode before adding any text for an
    # empty-entries toctree.
    with pytest.raises(nodes.SkipNode):
        translator.visit_toctree(toctree)

    output = translator.astext()

    # Should generate nothing for empty toctree
    assert output == "" or output.strip() == ""

    # Neither the scope opener nor any include() may have been emitted.
    assert "context {" not in output
    assert "set heading(offset:" not in output
    assert "include(" not in output


def test_toctree_skip_node_raised(simple_document, mock_builder):
    """
    Test that visit_toctree raises SkipNode.

    Requirement 13.11: WHEN `toctree` ノード処理時に
    `addnodes.toctree` ノードが `raise nodes.SkipNode` を実行
    THEN 子ノードの処理 SHALL スキップされる
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = [("Test", "test")]

    # Should raise SkipNode
    with pytest.raises(nodes.SkipNode):
        translator.visit_toctree(toctree)


# Issue #7: Single scope block tests
def test_toctree_single_content_block_multiple_includes(simple_document, mock_builder):
    """
    Test that toctree with multiple entries generates a single scope block.

    Issue #7 - Requirement 1.1, 1.2, 1.3:
    WHEN toctree has multiple entries
    THEN a single scope block {...} SHALL contain all include() directives

    Phase 49 (COMP-05/D-03/D-04, FLIPS -- genuine reshape, not merely a
    SYNTHETIC-NODE fix, per 49-EXPECTED-STRUCTURE.md's assertion census):
    each entry now emits its OWN one-line compile-time guard
    (``if "<key>" in state(...).get() { include(...) }``), a NESTED
    ``{``/``}`` pair per entry INSIDE the single outer ``context { ... }``
    scope -- so for 3 entries the brace counts become 4 (1 scope + 3
    guards), not 1, and a ``find("{")``/``find("}", block_start)`` pair
    would capture only up through the FIRST guard's own closing brace,
    silently truncating before the second and third entries' includes.
    ``block_content`` is now the WHOLE output (the single ``context {
    ... }`` scope IS the entire emitted block, guards nested inside it).
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Chapter 1", "chapter1"),
        ("Chapter 2", "chapter2"),
        ("Chapter 3", "chapter3"),
    ]
    # Phase 49 (COMP-05/D-03): the emission side reads includefiles, not
    # entries.
    toctree["includefiles"] = ["chapter1", "chapter2", "chapter3"]

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()

    # 1 outer context{} scope + 3 per-entry guard {}'s = 4 opening/closing
    # braces, not 1 (Phase 49 FLIPS).
    assert output.count("{") == 4, f"Expected 4 opening braces, got {output.count('{')}"
    assert output.count("}") == 4, f"Expected 4 closing braces, got {output.count('}')}"

    # The single outer context { ... } scope IS the entire emitted block --
    # every guard (and therefore every include()) lives inside it, so the
    # whole output is the block to search, not a find()-derived slice.
    block_content = output

    # All includes should be within the single (outer) block
    assert 'include("chapter1.typ")' in block_content
    assert 'include("chapter2.typ")' in block_content
    assert 'include("chapter3.typ")' in block_content


def test_toctree_heading_offset_appears_once(simple_document, mock_builder):
    """
    Test that set heading(offset: heading.offset + 1) appears exactly once.

    Issue #7 - Requirement 1.4:
    WHEN toctree with multiple entries is processed
    THEN set heading(offset: heading.offset + 1) SHALL appear exactly once
    (D-07: the context-relative increment, not the old absolute assignment)
    """
    import re

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Doc 1", "doc1"),
        ("Doc 2", "doc2"),
        ("Doc 3", "doc3"),
    ]
    # Phase 49 (COMP-05/D-03): the emission side reads includefiles, not
    # entries.
    toctree["includefiles"] = ["doc1", "doc2", "doc3"]

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()

    # Count occurrences of set heading(offset: heading.offset + 1) -- this
    # count SURVIVES Phase 49 unchanged: D-08 keeps exactly ONE offset
    # line per toctree regardless of how many per-entry guards it emits.
    pattern = r"set heading\(offset: heading\.offset \+ 1\)"
    matches = re.findall(pattern, output)

    assert len(matches) == 1, (
        "Expected 1 occurrence of set heading(offset: heading.offset + 1), "
        f"got {len(matches)}"
    )


def test_toctree_reduced_line_count(simple_document, mock_builder):
    """
    Test that the generated output has reduced line count.

    Issue #7 - Requirement 4.3:
    WHEN toctree with 3 entries is processed
    THEN the output SHALL have approximately 5-6 lines (reduced from ~12 lines)
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Entry 1", "entry1"),
        ("Entry 2", "entry2"),
        ("Entry 3", "entry3"),
    ]
    # Phase 49 (COMP-05/D-03): the emission side reads includefiles, not
    # entries.
    toctree["includefiles"] = ["entry1", "entry2", "entry3"]

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()
    lines = [line for line in output.split("\n") if line.strip()]

    # Expected structure (SURVIVES Phase 49 unchanged -- each entry still
    # emits exactly ONE text line, a guard line instead of a bare
    # include() line, so the total line count is the same shape):
    # 1. context {
    # 2.   set heading(offset: heading.offset + 1)
    # 3.   if "..." in state(...).get() { include("entry1.typ") }
    # 4.   if "..." in state(...).get() { include("entry2.typ") }
    # 5.   if "..." in state(...).get() { include("entry3.typ") }
    # 6. }
    # Total: ~5-6 lines (vs ~12 lines with individual blocks)

    assert len(lines) <= 6, f"Expected <= 6 lines, got {len(lines)}: {lines}"
    assert len(lines) >= 5, f"Expected >= 5 lines, got {len(lines)}: {lines}"


def test_toctree_single_entry_with_single_block(simple_document, mock_builder):
    """
    Test that even a single entry uses a single scope block.

    Issue #7 - Requirement 1.1:
    WHEN toctree has a single entry
    THEN a single scope block {...} SHALL be generated

    Phase 49 (COMP-05/D-03, SYNTHETIC-NODE + brace-count FLIPS): the
    single entry now emits its own one-line guard, a NESTED ``{``/``}``
    pair inside the outer ``context { ... }`` scope -- so the brace count
    becomes 2 (1 scope + 1 guard), not 1. The ``include(`` call count
    itself SURVIVES unchanged: one guard still emits exactly one
    ``include(`` call.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Single Doc", "single"),
    ]
    # Phase 49 (COMP-05/D-03): the emission side reads includefiles, not
    # entries.
    toctree["includefiles"] = ["single"]

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()

    # 1 outer context{} scope + 1 per-entry guard {} = 2 braces, not 1
    # (Phase 49 FLIPS).
    assert output.count("{") == 2
    assert output.count("}") == 2

    # Should contain exactly one include() -- counted, not merely checked
    # for membership, since a single-entry toctree must produce a single
    # include() inside its single scope block. SURVIVES Phase 49
    # unchanged: one guard emits exactly one include( call.
    assert 'include("single.typ")' in output
    assert output.count("include(") == 1
    assert "set heading(offset: heading.offset + 1)" in output

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

    # Visit the toctree node
    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass  # Expected behavior

    output = translator.astext()

    # Should generate include() directives, NOT outline()
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
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Chapter 1", "chapter1"),
        ("Chapter 2", "chapter2"),
        ("Chapter 3", "chapter3"),
    ]

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()

    # Should have exactly one opening scope block
    assert output.count("{") == 1, f"Expected 1 opening block, got {output.count('{')}"

    # Should have exactly one closing scope block
    assert output.count("}") == 1, f"Expected 1 closing block, got {output.count('}')}"

    # Extract scope block
    block_start = output.find("{")
    block_end = output.find("}", block_start)
    assert block_start != -1 and block_end != -1, "Scope block not found"

    block_content = output[block_start : block_end + 1]

    # All includes should be within the single block
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

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()

    # Count occurrences of set heading(offset: heading.offset + 1)
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

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()
    lines = [line for line in output.split("\n") if line.strip()]

    # Expected structure:
    # 1. context {
    # 2.   set heading(offset: heading.offset + 1)
    # 3.   include("entry1.typ")
    # 4.   include("entry2.typ")
    # 5.   include("entry3.typ")
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
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Single Doc", "single"),
    ]

    try:
        translator.visit_toctree(toctree)
    except nodes.SkipNode:
        pass

    output = translator.astext()

    # Should still have exactly one scope block
    assert output.count("{") == 1
    assert output.count("}") == 1

    # Should contain exactly one include() -- counted, not merely checked
    # for membership, since a single-entry toctree must produce a single
    # include() inside its single scope block.
    assert 'include("single.typ")' in output
    assert output.count("include(") == 1
    assert "set heading(offset: heading.offset + 1)" in output

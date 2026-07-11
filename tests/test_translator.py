"""
Tests for TypstTranslator class.
"""

import pytest
from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter


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


def test_translator_state_initialization(simple_document, mock_builder):
    """Test that translator initializes state variables correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Check that state variables are initialized
    assert hasattr(translator, "section_level")
    assert translator.section_level == 0
    assert hasattr(translator, "in_figure")
    assert translator.in_figure is False
    assert hasattr(translator, "in_table")
    assert translator.in_table is False
    assert hasattr(translator, "list_stack")
    assert translator.list_stack == []


def test_translator_section_level_management(simple_document, mock_builder):
    """Test that section_level is managed correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Initial section level should be 0
    assert translator.section_level == 0

    # Visit a section - should increment
    section = nodes.section()
    translator.visit_section(section)
    assert translator.section_level == 1

    # Visit a nested section - should increment again
    nested_section = nodes.section()
    translator.visit_section(nested_section)
    assert translator.section_level == 2

    # Depart nested section - should decrement
    translator.depart_section(nested_section)
    assert translator.section_level == 1

    # Depart section - should decrement
    translator.depart_section(section)
    assert translator.section_level == 0


def test_translator_heading_level_generation(simple_document, mock_builder):
    """Test that heading levels are generated correctly based on section_level."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Level 1 heading (=)
    section1 = nodes.section()
    translator.visit_section(section1)
    title1 = nodes.title(text="Level 1")
    translator.visit_title(title1)
    translator.visit_Text(nodes.Text("Level 1"))
    translator.depart_Text(nodes.Text("Level 1"))
    translator.depart_title(title1)
    output1 = translator.astext()
    assert 'heading(level: 1, text("Level 1"))' in output1

    # Clear output for next test
    translator.body = []

    # Level 2 heading (==)
    section2 = nodes.section()
    translator.visit_section(section2)
    title2 = nodes.title(text="Level 2")
    translator.visit_title(title2)
    translator.visit_Text(nodes.Text("Level 2"))
    translator.depart_Text(nodes.Text("Level 2"))
    translator.depart_title(title2)
    output2 = translator.astext()
    assert 'heading(level: 2, text("Level 2"))' in output2


def test_table_conversion(simple_document, mock_builder):
    """Test that table nodes are converted to Typst #table() syntax."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a simple 2x2 table
    # Table structure: table > tgroup > (colspec, thead, tbody) > row > entry
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)

    # Add column specifications
    colspec1 = nodes.colspec(colwidth=1)
    colspec2 = nodes.colspec(colwidth=1)
    tgroup += colspec1
    tgroup += colspec2

    # Add header row
    thead = nodes.thead()
    row1 = nodes.row()
    entry1 = nodes.entry()
    entry1 += nodes.paragraph(text="Header 1")
    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="Header 2")
    row1 += entry1
    row1 += entry2
    thead += row1
    tgroup += thead

    # Add body row
    tbody = nodes.tbody()
    row2 = nodes.row()
    entry3 = nodes.entry()
    entry3 += nodes.paragraph(text="Cell 1")
    entry4 = nodes.entry()
    entry4 += nodes.paragraph(text="Cell 2")
    row2 += entry3
    row2 += entry4
    tbody += row2
    tgroup += tbody

    table += tgroup

    # Visit the table using walkabout (proper doctree traversal)
    table.walkabout(translator)

    output = translator.astext()

    # Debug: print output if test fails
    if "#table(" not in output:
        print(f"DEBUG: Output is: '{output}'")
        print(
            f"DEBUG: Table cells: {translator.table_cells if hasattr(translator, 'table_cells') else 'N/A'}"
        )

    # Check that Typst table() syntax is generated (no # in unified code mode)
    assert "table(" in output
    assert "columns: 2" in output or "columns: (1fr, 1fr)" in output
    assert "Header 1" in output
    assert "Header 2" in output
    assert "Cell 1" in output
    assert "Cell 2" in output


def test_unknown_visit_handles_unknown_nodes(simple_document, mock_builder):
    """Test that unknown_visit is called for unknown nodes."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a custom unknown node type
    class UnknownNode(nodes.Element):
        pass

    unknown_node = UnknownNode()

    # Should not raise an exception
    translator.unknown_visit(unknown_node)
    translator.unknown_departure(unknown_node)

    # Check that we can still generate output
    output = translator.astext()
    assert isinstance(output, str)


def test_in_figure_state_management(simple_document, mock_builder):
    """Test that in_figure state is managed correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Initially not in figure
    assert translator.in_figure is False

    # Visit a figure
    figure = nodes.figure()
    translator.visit_figure(figure)
    assert translator.in_figure is True

    # Depart figure
    translator.depart_figure(figure)
    assert translator.in_figure is False


def test_in_table_state_management(simple_document, mock_builder):
    """Test that in_table state is managed correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Initially not in table
    assert translator.in_table is False

    # Visit a table
    table = nodes.table()
    translator.visit_table(table)
    assert translator.in_table is True

    # Depart table
    translator.depart_table(table)
    assert translator.in_table is False


def test_subtitle_conversion(simple_document, mock_builder):
    """Test that subtitle nodes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Visit a section
    section = nodes.section()
    translator.visit_section(section)

    # Visit a subtitle
    subtitle = nodes.subtitle(text="Test Subtitle")
    translator.visit_subtitle(subtitle)
    translator.visit_Text(nodes.Text("Test Subtitle"))
    translator.depart_Text(nodes.Text("Test Subtitle"))
    translator.depart_subtitle(subtitle)

    output = translator.astext()
    # Subtitle should be rendered as emphasized text
    assert 'emph(text("Test Subtitle"))' in output


def test_paragraph_and_text_conversion(simple_document, mock_builder):
    """Test that paragraphs and text are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Visit a paragraph
    para = nodes.paragraph(text="This is a test paragraph.")
    translator.visit_paragraph(para)
    translator.visit_Text(nodes.Text("This is a test paragraph."))
    translator.depart_Text(nodes.Text("This is a test paragraph."))
    translator.depart_paragraph(para)

    output = translator.astext()
    assert "This is a test paragraph." in output
    # Paragraph should end with double newline
    assert "\n\n" in output


def test_multiple_paragraphs_conversion(simple_document, mock_builder):
    """Test that multiple paragraphs are separated correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # First paragraph
    para1 = nodes.paragraph(text="First paragraph.")
    translator.visit_paragraph(para1)
    translator.visit_Text(nodes.Text("First paragraph."))
    translator.depart_Text(nodes.Text("First paragraph."))
    translator.depart_paragraph(para1)

    # Second paragraph
    para2 = nodes.paragraph(text="Second paragraph.")
    translator.visit_paragraph(para2)
    translator.visit_Text(nodes.Text("Second paragraph."))
    translator.depart_Text(nodes.Text("Second paragraph."))
    translator.depart_paragraph(para2)

    output = translator.astext()
    assert "First paragraph." in output
    assert "Second paragraph." in output
    # Paragraphs should be separated by double newline
    assert 'par({text("First paragraph.")})' in output
    assert 'par({text("Second paragraph.")})' in output


def test_emphasis_conversion(simple_document, mock_builder):
    """Test that emphasis (italic) nodes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Visit an emphasis node
    emphasis = nodes.emphasis(text="italic text")
    translator.visit_emphasis(emphasis)
    translator.visit_Text(nodes.Text("italic text"))
    translator.depart_Text(nodes.Text("italic text"))
    translator.depart_emphasis(emphasis)

    output = translator.astext()
    # Emphasis should be rendered as emph({text("...")})
    assert 'emph({text("italic text")})' in output


def test_strong_conversion(simple_document, mock_builder):
    """Test that strong (bold) nodes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Visit a strong node
    strong = nodes.strong(text="bold text")
    translator.visit_strong(strong)
    translator.visit_Text(nodes.Text("bold text"))
    translator.depart_Text(nodes.Text("bold text"))
    translator.depart_strong(strong)

    output = translator.astext()
    # Strong should be rendered as strong({text("...")})
    assert 'strong({text("bold text")})' in output


def test_literal_conversion(simple_document, mock_builder):
    """Test that literal (inline code) nodes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Visit a literal node (visit_literal raises SkipNode)
    literal = nodes.literal(text="code")
    try:
        translator.visit_literal(literal)
        translator.depart_literal(literal)
    except nodes.SkipNode:
        pass

    output = translator.astext()
    # Literal should be rendered as raw("code")
    assert 'raw("code")' in output


def test_subscript_conversion(simple_document, mock_builder):
    """Test that subscript nodes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Visit a subscript node
    subscript = nodes.subscript(text="2")
    translator.visit_subscript(subscript)
    translator.visit_Text(nodes.Text("2"))
    translator.depart_Text(nodes.Text("2"))
    translator.depart_subscript(subscript)

    output = translator.astext()
    # Subscript should be rendered as #sub[2]
    assert 'sub(text("2"))' in output


def test_superscript_conversion(simple_document, mock_builder):
    """Test that superscript nodes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Visit a superscript node
    superscript = nodes.superscript(text="2")
    translator.visit_superscript(superscript)
    translator.visit_Text(nodes.Text("2"))
    translator.depart_Text(nodes.Text("2"))
    translator.depart_superscript(superscript)

    output = translator.astext()
    # Superscript should be rendered as #super[2]
    assert 'super(text("2"))' in output


def test_mixed_inline_elements(simple_document, mock_builder):
    """Test that mixed inline elements work correctly together."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a paragraph with mixed inline elements
    para = nodes.paragraph()
    translator.visit_paragraph(para)

    # Regular text
    translator.visit_Text(nodes.Text("This is "))
    translator.depart_Text(nodes.Text("This is "))

    # Bold text
    strong = nodes.strong(text="bold")
    translator.visit_strong(strong)
    translator.visit_Text(nodes.Text("bold"))
    translator.depart_Text(nodes.Text("bold"))
    translator.depart_strong(strong)

    # Regular text
    translator.visit_Text(nodes.Text(" and "))
    translator.depart_Text(nodes.Text(" and "))

    # Italic text
    emphasis = nodes.emphasis(text="italic")
    translator.visit_emphasis(emphasis)
    translator.visit_Text(nodes.Text("italic"))
    translator.depart_Text(nodes.Text("italic"))
    translator.depart_emphasis(emphasis)

    # Regular text
    translator.visit_Text(nodes.Text(" with "))
    translator.depart_Text(nodes.Text(" with "))

    # Inline code (visit_literal raises SkipNode)
    literal = nodes.literal(text="code")
    try:
        translator.visit_literal(literal)
        translator.depart_literal(literal)
    except nodes.SkipNode:
        pass

    translator.visit_Text(nodes.Text("."))
    translator.depart_Text(nodes.Text("."))

    translator.depart_paragraph(para)

    output = translator.astext()
    assert "This is " in output
    assert 'strong({text("bold")})' in output
    assert 'emph({text("italic")})' in output
    assert 'raw("code")' in output


def test_bullet_list_conversion(simple_document, mock_builder):
    """Test that bullet lists are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a bullet list
    bullet_list = nodes.bullet_list()
    translator.visit_bullet_list(bullet_list)

    # First item
    item1 = nodes.list_item()
    translator.visit_list_item(item1)
    translator.visit_Text(nodes.Text("First item"))
    translator.depart_Text(nodes.Text("First item"))
    translator.depart_list_item(item1)

    # Second item
    item2 = nodes.list_item()
    translator.visit_list_item(item2)
    translator.visit_Text(nodes.Text("Second item"))
    translator.depart_Text(nodes.Text("Second item"))
    translator.depart_list_item(item2)

    translator.depart_bullet_list(bullet_list)

    output = translator.astext()
    assert "list({" in output
    assert 'text("First item")' in output
    assert 'text("Second item")' in output


def test_enumerated_list_conversion(simple_document, mock_builder):
    """Test that enumerated lists are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create an enumerated list
    enum_list = nodes.enumerated_list()
    translator.visit_enumerated_list(enum_list)

    # First item
    item1 = nodes.list_item()
    translator.visit_list_item(item1)
    translator.visit_Text(nodes.Text("First item"))
    translator.depart_Text(nodes.Text("First item"))
    translator.depart_list_item(item1)

    # Second item
    item2 = nodes.list_item()
    translator.visit_list_item(item2)
    translator.visit_Text(nodes.Text("Second item"))
    translator.depart_Text(nodes.Text("Second item"))
    translator.depart_list_item(item2)

    translator.depart_enumerated_list(enum_list)

    output = translator.astext()
    assert "enum({" in output
    assert 'text("First item")' in output
    assert 'text("Second item")' in output


def test_nested_bullet_list(simple_document, mock_builder):
    """Test that nested bullet lists are converted correctly with proper indentation."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Outer bullet list
    outer_list = nodes.bullet_list()
    translator.visit_bullet_list(outer_list)

    # First outer item
    outer_item1 = nodes.list_item()
    translator.visit_list_item(outer_item1)
    translator.visit_Text(nodes.Text("Outer item 1"))
    translator.depart_Text(nodes.Text("Outer item 1"))
    translator.depart_list_item(outer_item1)

    # Second outer item with nested list
    outer_item2 = nodes.list_item()
    translator.visit_list_item(outer_item2)
    translator.visit_Text(nodes.Text("Outer item 2"))
    translator.depart_Text(nodes.Text("Outer item 2"))

    # Nested bullet list
    inner_list = nodes.bullet_list()
    translator.visit_bullet_list(inner_list)

    # Inner item
    inner_item1 = nodes.list_item()
    translator.visit_list_item(inner_item1)
    translator.visit_Text(nodes.Text("Inner item 1"))
    translator.depart_Text(nodes.Text("Inner item 1"))
    translator.depart_list_item(inner_item1)

    translator.depart_bullet_list(inner_list)
    translator.depart_list_item(outer_item2)

    translator.depart_bullet_list(outer_list)

    output = translator.astext()
    assert 'text("Outer item 1")' in output
    assert 'text("Outer item 2")' in output
    assert 'text("Inner item 1")' in output  # Nested list item


def test_nested_enumerated_list(simple_document, mock_builder):
    """Test that nested enumerated lists are converted correctly with proper indentation."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Outer enumerated list
    outer_list = nodes.enumerated_list()
    translator.visit_enumerated_list(outer_list)

    # First outer item
    outer_item1 = nodes.list_item()
    translator.visit_list_item(outer_item1)
    translator.visit_Text(nodes.Text("Outer item 1"))
    translator.depart_Text(nodes.Text("Outer item 1"))
    translator.depart_list_item(outer_item1)

    # Second outer item with nested list
    outer_item2 = nodes.list_item()
    translator.visit_list_item(outer_item2)
    translator.visit_Text(nodes.Text("Outer item 2"))
    translator.depart_Text(nodes.Text("Outer item 2"))

    # Nested enumerated list
    inner_list = nodes.enumerated_list()
    translator.visit_enumerated_list(inner_list)

    # Inner item
    inner_item1 = nodes.list_item()
    translator.visit_list_item(inner_item1)
    translator.visit_Text(nodes.Text("Inner item 1"))
    translator.depart_Text(nodes.Text("Inner item 1"))
    translator.depart_list_item(inner_item1)

    translator.depart_enumerated_list(inner_list)
    translator.depart_list_item(outer_item2)

    translator.depart_enumerated_list(outer_list)

    output = translator.astext()
    assert 'text("Outer item 1")' in output
    assert 'text("Outer item 2")' in output
    assert 'text("Inner item 1")' in output  # Nested list item


def test_mixed_nested_lists(simple_document, mock_builder):
    """Test that mixed nested lists (bullet + enumerated) work correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Outer bullet list
    outer_list = nodes.bullet_list()
    translator.visit_bullet_list(outer_list)

    # First item with nested enumerated list
    outer_item1 = nodes.list_item()
    translator.visit_list_item(outer_item1)
    translator.visit_Text(nodes.Text("Bullet item"))
    translator.depart_Text(nodes.Text("Bullet item"))

    # Nested enumerated list
    inner_list = nodes.enumerated_list()
    translator.visit_enumerated_list(inner_list)

    inner_item1 = nodes.list_item()
    translator.visit_list_item(inner_item1)
    translator.visit_Text(nodes.Text("Numbered item"))
    translator.depart_Text(nodes.Text("Numbered item"))
    translator.depart_list_item(inner_item1)

    translator.depart_enumerated_list(inner_list)
    translator.depart_list_item(outer_item1)

    translator.depart_bullet_list(outer_list)

    output = translator.astext()
    assert 'text("Bullet item")' in output
    assert 'text("Numbered item")' in output  # Nested with different type


def test_list_item_with_multiple_elements(simple_document, mock_builder):
    """Test list item with multiple inline elements (text + bold + emphasis)."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a bullet list with complex items
    bullet_list = nodes.bullet_list()
    translator.visit_bullet_list(bullet_list)

    # Item with text + bold
    item1 = nodes.list_item()
    translator.visit_list_item(item1)
    translator.visit_Text(nodes.Text("Item with "))
    translator.depart_Text(nodes.Text("Item with "))
    translator.visit_strong(nodes.strong())
    translator.visit_Text(nodes.Text("bold"))
    translator.depart_Text(nodes.Text("bold"))
    translator.depart_strong(nodes.strong())
    translator.depart_list_item(item1)

    # Item with text + emphasis + text
    item2 = nodes.list_item()
    translator.visit_list_item(item2)
    translator.visit_Text(nodes.Text("Item with "))
    translator.depart_Text(nodes.Text("Item with "))
    translator.visit_emphasis(nodes.emphasis())
    translator.visit_Text(nodes.Text("emphasis"))
    translator.depart_Text(nodes.Text("emphasis"))
    translator.depart_emphasis(nodes.emphasis())
    translator.visit_Text(nodes.Text(" text"))
    translator.depart_Text(nodes.Text(" text"))
    translator.depart_list_item(item2)

    # Item with literal (inline code)
    item3 = nodes.list_item()
    translator.visit_list_item(item3)
    translator.visit_Text(nodes.Text("Code: "))
    translator.depart_Text(nodes.Text("Code: "))
    # literal raises SkipNode, so we don't manually visit children
    literal_node = nodes.literal(text="print()")
    try:
        translator.visit_literal(literal_node)
    except nodes.SkipNode:
        pass  # Expected behavior
    translator.depart_list_item(item3)

    translator.depart_bullet_list(bullet_list)

    output = translator.astext()

    # Verify { } block structure with newline separators
    assert 'text("Item with ")\nstrong({text("bold")})' in output
    assert 'text("Item with ")\nemph({text("emphasis")})\ntext(" text")' in output
    assert 'text("Code: ")\nraw("print()")' in output


def test_list_item_with_reference(simple_document, mock_builder):
    """Test list item with text + reference (link)."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a bullet list with link
    bullet_list = nodes.bullet_list()
    translator.visit_bullet_list(bullet_list)

    # Item with text + link
    item1 = nodes.list_item()
    translator.visit_list_item(item1)
    translator.visit_Text(nodes.Text("GitHub: "))
    translator.depart_Text(nodes.Text("GitHub: "))
    ref_node = nodes.reference(refuri="https://github.com/example")
    translator.visit_reference(ref_node)
    translator.visit_Text(nodes.Text("https://github.com/example"))
    translator.depart_Text(nodes.Text("https://github.com/example"))
    translator.depart_reference(ref_node)
    translator.depart_list_item(item1)

    translator.depart_bullet_list(bullet_list)

    output = translator.astext()

    # Verify { } block structure with newline separator for reference
    assert (
        'text("GitHub: ")\nlink("https://github.com/example", text("https://github.com/example"))'
        in output
    )


def test_literal_block_without_language(simple_document, mock_builder):
    """Test that literal blocks without language are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block without language
    literal_block = nodes.literal_block(text="def hello():\n    print('Hello')")
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("def hello():\n    print('Hello')"))
    translator.depart_Text(nodes.Text("def hello():\n    print('Hello')"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should generate code block with backticks
    assert "```" in output
    assert "def hello():" in output
    assert "print('Hello')" in output


def test_literal_block_with_language(simple_document, mock_builder):
    """Test that literal blocks with language specification are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with language
    literal_block = nodes.literal_block(text="def hello():\n    print('Hello')")
    literal_block["language"] = "python"
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("def hello():\n    print('Hello')"))
    translator.depart_Text(nodes.Text("def hello():\n    print('Hello')"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should generate code block with language specification
    assert "```python" in output
    assert "def hello():" in output
    assert "print('Hello')" in output


def test_literal_block_escaping(simple_document, mock_builder):
    """Test that literal blocks handle special characters correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with special characters
    literal_block = nodes.literal_block(text="x = `value`\ny = ${var}")
    literal_block["language"] = "bash"
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("x = `value`\ny = ${var}"))
    translator.depart_Text(nodes.Text("x = `value`\ny = ${var}"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Special characters should be preserved in code block
    assert "```bash" in output
    assert "x = `value`" in output
    assert "y = ${var}" in output


def test_literal_block_with_linenos(simple_document, mock_builder):
    """Test that literal blocks with line numbers are handled correctly (Task 4.2)."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with linenos option
    literal_block = nodes.literal_block(text="line 1\nline 2\nline 3")
    literal_block["language"] = "python"
    literal_block["linenos"] = True
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("line 1\nline 2\nline 3"))
    translator.depart_Text(nodes.Text("line 1\nline 2\nline 3"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should generate raw block with numbering parameter
    # Typst #raw() with numbering: "line-1" or similar
    assert "#raw(" in output or "```python" in output
    if "#raw(" in output:
        # Check for numbering parameter
        assert "numbering:" in output or "line-1" in output


def test_literal_block_with_highlight_lines(simple_document, mock_builder):
    """
    Test that literal blocks with highlight_args generate #codly-range() (Task 4.2.2).

    Design 3.5: codly forced usage with #codly-range() for highlighted lines
    Requirement 7.4: highlight_args should be converted to #codly-range(highlight: (...))
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with highlight_args
    literal_block = nodes.literal_block(text="line 1\nline 2\nline 3\nline 4")
    literal_block["language"] = "python"
    literal_block["highlight_args"] = {"hl_lines": [2, 3]}
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("line 1\nline 2\nline 3\nline 4"))
    translator.depart_Text(nodes.Text("line 1\nline 2\nline 3\nline 4"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should generate #codly-range() before code block
    assert (
        "codly-range(" in output
    ), "Should generate codly-range() for highlighted lines"
    assert "highlight:" in output, "Should specify highlight parameter"
    assert "2" in output and "3" in output, "Should include highlighted line numbers"
    assert "```python" in output, "Should still use code block with language"


def test_literal_block_with_linenos_and_highlights(simple_document, mock_builder):
    """
    Test literal blocks with both line numbers and highlights (Task 4.2.2).

    Design 3.5: codly provides line numbers by default, use #codly-range() for highlights
    Requirement 7.3, 7.4: Both linenos and highlight_args should be supported
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with both options
    literal_block = nodes.literal_block(text="def foo():\n    x = 1\n    return x")
    literal_block["language"] = "python"
    literal_block["linenos"] = True
    literal_block["highlight_args"] = {"hl_lines": [2]}
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("def foo():\n    x = 1\n    return x"))
    translator.depart_Text(nodes.Text("def foo():\n    x = 1\n    return x"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # codly provides line numbers by default, should generate #codly-range() for highlights
    assert (
        "codly-range(" in output
    ), "Should generate codly-range() for highlighted lines"
    assert "highlight:" in output, "Should specify highlight parameter"
    assert "2" in output, "Should include highlighted line number"
    assert "```python" in output, "Should use code block with language"


def test_literal_block_with_highlight_ranges(simple_document, mock_builder):
    """
    Test literal blocks with highlight ranges (Task 4.2.2).

    Design 3.5: #codly-range() should support both individual lines and ranges
    Example: #codly-range(highlight: (2, 4-6)) highlights line 2 and lines 4-6
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with range highlights (simulating ":emphasize-lines: 2,4-6")
    literal_block = nodes.literal_block(
        text="line 1\nline 2\nline 3\nline 4\nline 5\nline 6"
    )
    literal_block["language"] = "python"
    # hl_lines can contain individual lines and ranges
    literal_block["highlight_args"] = {"hl_lines": [2, 4, 5, 6]}
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("line 1\nline 2\nline 3\nline 4\nline 5\nline 6"))
    translator.depart_Text(nodes.Text("line 1\nline 2\nline 3\nline 4\nline 5\nline 6"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should generate #codly-range() with highlight parameter
    assert "codly-range(" in output, "Should generate #codly-range()"
    assert "highlight:" in output, "Should specify highlight parameter"
    # Should contain line numbers (exact format depends on implementation)
    assert (
        "2" in output or "4" in output
    ), "Should include some highlighted line numbers"


def test_literal_block_unsupported_language_warning(simple_document, mock_builder):
    """Test handling of unsupported languages (Task 4.2)."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with potentially unsupported language
    literal_block = nodes.literal_block(text="some code")
    literal_block["language"] = "obscure-language-xyz"

    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("some code"))
    translator.depart_Text(nodes.Text("some code"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should still generate code block (Typst handles unknown languages gracefully)
    assert "```obscure-language-xyz" in output or "```" in output


def test_literal_block_with_lineno_start(simple_document, mock_builder):
    """Test literal block with :lineno-start: option (Issue #31).

    Note: Sphinx stores :lineno-start: in highlight_args['linenostart'].
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with linenos and lineno-start options
    # Sphinx stores lineno-start in highlight_args
    literal_block = nodes.literal_block(text='def my_function():\n    return "line 42"')
    literal_block["language"] = "python"
    literal_block["linenos"] = True
    literal_block["highlight_args"] = {"linenostart": 42}
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text('def my_function():\n    return "line 42"'))
    translator.depart_Text(nodes.Text('def my_function():\n    return "line 42"'))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should generate #codly(start: 42)
    assert "codly(start: 42)" in output, "Should generate #codly(start: 42)"
    assert "```python" in output, "Should still use code block with language"


def test_literal_block_with_lineno_start_without_linenos(simple_document, mock_builder):
    """Test that :lineno-start: without :linenos: is ignored (Issue #31).

    Note: Sphinx stores :lineno-start: in highlight_args['linenostart'].
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with lineno-start but without linenos
    literal_block = nodes.literal_block(text='def my_function():\n    return "test"')
    literal_block["language"] = "python"
    literal_block["highlight_args"] = {"linenostart": 42}
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text('def my_function():\n    return "test"'))
    translator.depart_Text(nodes.Text('def my_function():\n    return "test"'))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should not generate #codly(start: ...)
    assert (
        "#codly(start:" not in output
    ), "Should not generate start parameter without linenos"
    # Should disable line numbers
    assert "codly(number-format: none)" in output
    assert "```python" in output


def test_literal_block_with_lineno_start_and_emphasize(simple_document, mock_builder):
    """Test literal block with :lineno-start: and :emphasize-lines: (Issue #31).

    Note: Sphinx stores :lineno-start: in highlight_args['linenostart'].
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block with linenos, lineno-start, and highlights
    # Sphinx stores both linenostart and hl_lines in highlight_args
    literal_block = nodes.literal_block(
        text="def process_data(data):\n    result = transform(data)\n    return result"
    )
    literal_block["language"] = "python"
    literal_block["linenos"] = True
    literal_block["highlight_args"] = {"hl_lines": [2], "linenostart": 100}
    translator.visit_literal_block(literal_block)
    translator.visit_Text(
        nodes.Text(
            "def process_data(data):\n    result = transform(data)\n    return result"
        )
    )
    translator.depart_Text(
        nodes.Text(
            "def process_data(data):\n    result = transform(data)\n    return result"
        )
    )
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should generate both #codly(start: 100) and #codly-range(highlight: ...)
    assert "codly(start: 100)" in output, "Should generate start parameter"
    assert "codly-range(highlight:" in output, "Should generate highlight parameter"
    assert "2" in output, "Should include highlighted line number"
    assert "```python" in output


def test_literal_block_with_dedent_numeric(simple_document, mock_builder):
    """Test literal block with numeric :dedent: option (Issue #31).

    Note: Sphinx processes :dedent: during parsing, so the text reaching
    the translator is already dedented. This test verifies that dedented
    text is correctly handled.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Simulate Sphinx's behavior: text is already dedented by Sphinx parser
    # Original: "    def nested_function():\n        print(\"indented\")"
    # After :dedent: 4 processing by Sphinx:
    literal_block = nodes.literal_block(
        text='def nested_function():\n    print("indented")'
    )
    literal_block["language"] = "python"
    literal_block["dedent"] = 4  # This is stored but text is already processed
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text('def nested_function():\n    print("indented")'))
    translator.depart_Text(nodes.Text('def nested_function():\n    print("indented")'))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should have dedented content (already processed by Sphinx)
    assert "def nested_function():" in output, "Should have dedented first line"
    assert '    print("indented")' in output, "Should preserve relative indentation"


def test_literal_block_with_dedent_auto(simple_document, mock_builder):
    """Test literal block with auto :dedent: option (Issue #31).

    Note: Sphinx processes :dedent: during parsing using textwrap.dedent().
    The text reaching the translator is already auto-dedented.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Simulate Sphinx's behavior: text is already auto-dedented by Sphinx
    # Original: "    def nested_function():\n        print(\"auto dedent\")"
    # After :dedent: (auto) processing by Sphinx:
    literal_block = nodes.literal_block(
        text='def nested_function():\n    print("auto dedent")'
    )
    literal_block["language"] = "python"
    literal_block["dedent"] = True
    translator.visit_literal_block(literal_block)
    translator.visit_Text(
        nodes.Text('def nested_function():\n    print("auto dedent")')
    )
    translator.depart_Text(
        nodes.Text('def nested_function():\n    print("auto dedent")')
    )
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should have auto-dedented content (already processed by Sphinx)
    assert "def nested_function():" in output, "Should have auto-dedented first line"
    assert '    print("auto dedent")' in output, "Should preserve relative indentation"


def test_literal_block_with_dedent_and_other_options(simple_document, mock_builder):
    """Test literal block with :dedent: and other options (Issue #31).

    Note: Sphinx processes :dedent: before other options are applied.
    This test verifies that dedented content works with linenos and highlights.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Simulate Sphinx's behavior: text is already dedented
    # Original: "        def inner_function():\n            return \"dedented\""
    # After :dedent: 8 processing by Sphinx:
    literal_block = nodes.literal_block(
        text='def inner_function():\n    return "dedented"'
    )
    literal_block["language"] = "python"
    literal_block["dedent"] = 8
    literal_block["linenos"] = True
    literal_block["highlight_args"] = {"hl_lines": [1]}
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text('def inner_function():\n    return "dedented"'))
    translator.depart_Text(nodes.Text('def inner_function():\n    return "dedented"'))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should have dedented content with line numbers and highlights
    assert "def inner_function():" in output, "Should have dedented content"
    assert '    return "dedented"' in output, "Should preserve relative indentation"
    assert "codly-range(highlight:" in output, "Should have highlights"
    assert "```python" in output


def test_literal_block_with_dedent_short_lines(simple_document, mock_builder):
    """Test literal block with :dedent: on short lines (Issue #31).

    Note: Sphinx handles edge cases like empty lines and short lines correctly.
    This test verifies that such content is properly rendered.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Simulate Sphinx's behavior: text is already dedented
    # Original: "    def foo():\n\n    pass"
    # After :dedent: 4 processing by Sphinx:
    literal_block = nodes.literal_block(text="def foo():\n\npass")
    literal_block["language"] = "python"
    literal_block["dedent"] = 4
    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("def foo():\n\npass"))
    translator.depart_Text(nodes.Text("def foo():\n\npass"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()
    # Should handle dedented content with empty lines
    assert "def foo():" in output, "Should have dedented first line"
    assert "pass" in output, "Should have dedented last line"
    # Empty line should remain empty
    lines = output.split("\n")
    assert any(line == "" for line in lines), "Should preserve empty lines"


def test_definition_list_conversion(simple_document, mock_builder):
    """Test that definition lists are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a definition list
    def_list = nodes.definition_list()
    translator.visit_definition_list(def_list)

    # First definition list item
    def_item1 = nodes.definition_list_item()

    # Term
    term1 = nodes.term(text="API")
    translator.visit_term(term1)
    translator.visit_Text(nodes.Text("API"))
    translator.depart_Text(nodes.Text("API"))
    translator.depart_term(term1)

    # Definition
    definition1 = nodes.definition()
    translator.visit_definition(definition1)
    translator.visit_Text(nodes.Text("Application Programming Interface"))
    translator.depart_Text(nodes.Text("Application Programming Interface"))
    translator.depart_definition(definition1)

    # Second definition list item
    def_item2 = nodes.definition_list_item()

    # Term
    term2 = nodes.term(text="SDK")
    translator.visit_term(term2)
    translator.visit_Text(nodes.Text("SDK"))
    translator.depart_Text(nodes.Text("SDK"))
    translator.depart_term(term2)

    # Definition
    definition2 = nodes.definition()
    translator.visit_definition(definition2)
    translator.visit_Text(nodes.Text("Software Development Kit"))
    translator.depart_Text(nodes.Text("Software Development Kit"))
    translator.depart_definition(definition2)

    translator.depart_definition_list(def_list)

    output = translator.astext()
    # Typst definition list syntax: / term: definition
    assert "terms.item" in output or "terms(" in output
    assert "API" in output
    assert "Application Programming Interface" in output
    assert "SDK" in output
    assert "Software Development Kit" in output


def test_definition_list_with_multiple_definitions(simple_document, mock_builder):
    """Test that definition lists with multiple definitions per term work correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a definition list
    def_list = nodes.definition_list()
    translator.visit_definition_list(def_list)

    # Term
    term = nodes.term(text="Python")
    translator.visit_term(term)
    translator.visit_Text(nodes.Text("Python"))
    translator.depart_Text(nodes.Text("Python"))
    translator.depart_term(term)

    # First definition
    definition1 = nodes.definition()
    translator.visit_definition(definition1)
    translator.visit_Text(nodes.Text("A programming language"))
    translator.depart_Text(nodes.Text("A programming language"))
    translator.depart_definition(definition1)

    translator.depart_definition_list(def_list)

    output = translator.astext()
    assert "terms.item" in output or "terms(" in output
    assert "Python" in output
    assert "A programming language" in output


def test_block_quote_conversion(simple_document, mock_builder):
    """Test that block quotes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a block quote
    block_quote = nodes.block_quote()
    translator.visit_block_quote(block_quote)

    # Paragraph inside block quote
    para = nodes.paragraph(text="This is a quoted text.")
    translator.visit_paragraph(para)
    translator.visit_Text(nodes.Text("This is a quoted text."))
    translator.depart_Text(nodes.Text("This is a quoted text."))
    translator.depart_paragraph(para)

    translator.depart_block_quote(block_quote)

    output = translator.astext()
    # Typst block quote syntax: #quote[...]
    assert "quote[" in output
    assert "This is a quoted text." in output
    assert "]" in output


def test_block_quote_with_attribution(simple_document, mock_builder):
    """Test that block quotes with attribution are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a block quote
    block_quote = nodes.block_quote()
    translator.visit_block_quote(block_quote)

    # Paragraph inside block quote
    para = nodes.paragraph(text="To be or not to be.")
    translator.visit_paragraph(para)
    translator.visit_Text(nodes.Text("To be or not to be."))
    translator.depart_Text(nodes.Text("To be or not to be."))
    translator.depart_paragraph(para)

    # Attribution
    attribution = nodes.attribution(text="Shakespeare")
    translator.visit_attribution(attribution)
    translator.visit_Text(nodes.Text("Shakespeare"))
    translator.depart_Text(nodes.Text("Shakespeare"))
    translator.depart_attribution(attribution)

    translator.depart_block_quote(block_quote)

    output = translator.astext()
    # Typst block quote with attribution
    assert "quote[" in output
    assert "To be or not to be." in output
    assert "attribution:" in output and "Shakespeare" in output
    assert "]" in output


def test_nested_block_quote(simple_document, mock_builder):
    """Test that nested block quotes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Outer block quote
    outer_quote = nodes.block_quote()
    translator.visit_block_quote(outer_quote)

    # Paragraph in outer quote
    para1 = nodes.paragraph(text="Outer quote.")
    translator.visit_paragraph(para1)
    translator.visit_Text(nodes.Text("Outer quote."))
    translator.depart_Text(nodes.Text("Outer quote."))
    translator.depart_paragraph(para1)

    # Inner block quote
    inner_quote = nodes.block_quote()
    translator.visit_block_quote(inner_quote)

    # Paragraph in inner quote
    para2 = nodes.paragraph(text="Inner quote.")
    translator.visit_paragraph(para2)
    translator.visit_Text(nodes.Text("Inner quote."))
    translator.depart_Text(nodes.Text("Inner quote."))
    translator.depart_paragraph(para2)

    translator.depart_block_quote(inner_quote)
    translator.depart_block_quote(outer_quote)

    output = translator.astext()
    # Nested quotes should both use #quote[]
    assert output.count("quote[") == 2
    assert "Outer quote." in output
    assert "Inner quote." in output


def test_image_conversion(simple_document, mock_builder):
    """Test that image nodes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create an image node
    image = nodes.image(uri="path/to/image.png")
    translator.visit_image(image)
    translator.depart_image(image)

    output = translator.astext()
    # Typst image syntax: #image("path")
    assert "image(" in output
    assert "path/to/image.png" in output


def test_image_with_attributes(simple_document, mock_builder):
    """Test that image nodes with attributes are converted correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create an image node with width and alt attributes
    image = nodes.image(uri="diagram.svg")
    image["width"] = "300px"
    image["alt"] = "System diagram"
    translator.visit_image(image)
    translator.depart_image(image)

    output = translator.astext()
    # Image with attributes
    assert "image(" in output
    assert "diagram.svg" in output
    assert "width:" in output


def test_image_relative_path(simple_document, mock_builder):
    """Test that relative image paths are handled correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create an image with relative path
    image = nodes.image(uri="../images/logo.png")
    translator.visit_image(image)
    translator.depart_image(image)

    output = translator.astext()
    # Should preserve relative path
    assert "image(" in output
    assert "../images/logo.png" in output


def test_figure_with_caption(simple_document, mock_builder):
    """Test that figure with caption is converted to Typst #figure() syntax."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a figure with image and caption
    # Figure structure: figure > (image, caption)
    figure = nodes.figure()
    image = nodes.image(uri="diagram.png")
    caption = nodes.caption()
    caption += nodes.Text("Figure caption text")

    figure += image
    figure += caption

    # Visit using walkabout
    figure.walkabout(translator)

    output = translator.astext()

    # Check that Typst #figure() syntax is generated
    assert "figure(" in output
    assert "image(" in output or "image(" in output
    assert "diagram.png" in output
    assert "caption:" in output
    assert "Figure caption text" in output


def test_figure_with_label(simple_document, mock_builder):
    """Test that figure with label generates proper Typst label."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a figure with label (target node with ids)
    figure = nodes.figure(ids=["fig-example"])
    image = nodes.image(uri="example.png")
    caption = nodes.caption()
    caption += nodes.Text("An example figure")

    figure += image
    figure += caption

    # Visit using walkabout
    figure.walkabout(translator)

    output = translator.astext()

    # Check that Typst label is generated
    assert "figure(" in output
    assert "<fig-example>" in output or "label(" in output
    assert "An example figure" in output


def test_figure_without_caption(simple_document, mock_builder):
    """Test that figure without caption still generates #figure()."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a figure with only image
    figure = nodes.figure()
    image = nodes.image(uri="simple.png")
    figure += image

    # Visit using walkabout
    figure.walkabout(translator)

    output = translator.astext()

    # Should still generate figure syntax even without caption
    assert "figure(" in output or "#image(" in output
    assert "simple.png" in output


def test_target_label_generation(simple_document, mock_builder):
    """Test that target nodes generate Typst labels."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a target node with id
    target = nodes.target(ids=["my-label"])

    # Visit using walkabout
    target.walkabout(translator)

    output = translator.astext()

    # Check that Typst label is generated (using label() function in unified code mode)
    assert 'label("my-label")' in output


def test_reference_to_target(simple_document, mock_builder):
    """Test that reference nodes generate Typst links."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a reference to an internal target
    reference = nodes.reference(refuri="#section-1")
    reference += nodes.Text("See Section 1")

    # Visit using walkabout
    reference.walkabout(translator)

    output = translator.astext()

    # Check that Typst link is generated
    assert "link(" in output
    assert "See Section 1" in output


def test_external_reference(simple_document, mock_builder):
    """Test that external references generate proper Typst links."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create an external reference
    reference = nodes.reference(refuri="https://example.com")
    reference += nodes.Text("External Link")

    # Visit using walkabout
    reference.walkabout(translator)

    output = translator.astext()

    # Check that Typst external link is generated with new format: link(url, content)
    assert 'link("https://example.com", text("External Link"))' in output


def test_pending_xref_doc_reference(simple_document, mock_builder):
    """Test that pending_xref for document references are handled."""
    from sphinx import addnodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a pending cross-reference to a document
    xref = addnodes.pending_xref(
        refdomain="std",
        reftype="doc",
        reftarget="other_document",
        refexplicit=False,
    )
    xref += nodes.Text("Other Document")

    # Visit using walkabout
    xref.walkabout(translator)

    output = translator.astext()

    # Should generate a link (pending_xref is typically resolved by Sphinx,
    # but we handle the fallback case)
    # For now, we expect it to extract the text content
    assert "Other Document" in output


def test_pending_xref_with_refid(simple_document, mock_builder):
    """Test that pending_xref with refid generates proper reference."""
    from sphinx import addnodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a pending cross-reference with refid
    xref = addnodes.pending_xref(
        refdomain="std",
        reftype="ref",
        reftarget="section-label",
        refexplicit=True,
    )
    xref += nodes.inline(text="Section Reference")

    # Visit using walkabout
    xref.walkabout(translator)

    output = translator.astext()

    # Should handle the cross-reference
    assert "Section Reference" in output


def test_toctree_generates_outline(simple_document, mock_builder):
    """
    Test that toctree node generates #include() directives.

    Updated for Requirement 13: toctree now generates #include() instead of #outline()
    """
    from sphinx import addnodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a toctree node
    toctree = addnodes.toctree()
    toctree["entries"] = [
        ("Introduction", "intro"),
        ("Getting Started", "getting_started"),
        ("API Reference", "api"),
    ]

    # Visit using walkabout
    toctree.walkabout(translator)

    output = translator.astext()

    # Should generate #include() directives with heading offset (Requirement 13)
    assert "include(" in output
    assert 'include("intro.typ")' in output
    assert 'include("getting_started.typ")' in output
    assert 'include("api.typ")' in output
    assert "set heading(offset: 1)" in output


def test_table_no_duplication_all_types(simple_document, mock_builder):
    """
    Verify table content is not duplicated for all table types.

    This test ensures that ALL reStructuredText table formats (list-table,
    grid table, simple table, csv-table) do not produce duplicate output
    where cell content appears both as plain text AND inside #table().

    Related: issue #19
    """
    from docutils import frontend
    from docutils.parsers.rst import Parser as RstParser
    from docutils.utils import new_document

    from typsphinx.translator import TypstTranslator

    table_types = {
        "list-table": """
.. list-table::
   :header-rows: 1

   * - Header1
     - Header2
   * - CellA
     - CellB
""",
        "grid": """
+----------+----------+
| Header1  | Header2  |
+==========+==========+
| CellA    | CellB    |
+----------+----------+
""",
        "simple": """
========  ========
Header1   Header2
========  ========
CellA     CellB
========  ========
""",
        "csv": """
.. csv-table::
   :header: "Header1", "Header2"

   "CellA", "CellB"
""",
    }

    parser = RstParser()
    for table_type, rst_content in table_types.items():
        # Parse RST content
        settings = frontend.get_default_settings(RstParser)
        document = new_document("<test>", settings=settings)
        parser.parse(rst_content, document)

        # Translate to Typst
        translator = TypstTranslator(document, mock_builder)
        document.walkabout(translator)
        output = translator.astext()

        # Check that table( appears in output (no # in unified code mode)
        assert "table(" in output, f"{table_type}: table() not found in output"

        # Find the position of table( in the output
        lines = output.strip().split("\n")
        table_idx = next((i for i, line in enumerate(lines) if "table(" in line), None)

        assert table_idx is not None, f"{table_type}: Could not find table() in output"

        # Get content before table()
        before_table = "\n".join(lines[:table_idx])

        # Check that cell content keywords do NOT appear before table()
        # These keywords should only appear inside table()
        keywords = ["Header1", "Header2", "CellA", "CellB"]

        for keyword in keywords:
            assert (
                keyword not in before_table
            ), f"{table_type}: '{keyword}' appears before #table() - duplication detected!"

        # Verify that keywords DO appear inside #table()
        table_part = "\n".join(lines[table_idx:])
        for keyword in keywords:
            assert (
                keyword in table_part
            ), f"{table_type}: '{keyword}' not found in #table() - missing content!"


def test_comment_skipped(simple_document, mock_builder):
    """
    Verify RST comments are completely skipped in Typst output.

    Comments should not appear in the output and should not generate warnings.
    This test covers:
    - Single line comments
    - Multi-line comments
    - Text separation before/after comments
    - Empty comments

    Related: issue #21
    """
    from docutils import frontend
    from docutils.parsers.rst import Parser as RstParser
    from docutils.utils import new_document

    from typsphinx.translator import TypstTranslator

    rst_content = """
Test Comments
=============

Before comment paragraph.

.. This is a comment
   It spans multiple lines
   And should not appear in output

After comment paragraph.

..
   Empty comment marker
   Also hidden

More text.
"""

    # Parse RST content
    parser = RstParser()
    settings = frontend.get_default_settings(RstParser)
    document = new_document("<test>", settings=settings)
    parser.parse(rst_content, document)

    # Translate to Typst
    translator = TypstTranslator(document, mock_builder)
    document.walkabout(translator)
    output = translator.astext()

    # Check that heading is present
    assert 'heading(level: 1, text("Test Comments"))' in output

    # Check that comment text does NOT appear in output
    assert "This is a comment" not in output
    assert "It spans multiple lines" not in output
    assert "And should not appear in output" not in output
    assert "Empty comment marker" not in output
    assert "Also hidden" not in output

    # Check that paragraphs before/after are present
    assert "Before comment paragraph." in output
    assert "After comment paragraph." in output
    assert "More text." in output

    # Check that paragraphs are properly separated (comment doesn't merge them)
    # The output should have "After comment paragraph." on a separate line,
    # not merged with comment text
    lines = [line.strip() for line in output.split("\n") if line.strip()]

    # Find "After comment paragraph." line
    after_idx = next(
        (i for i, line in enumerate(lines) if "After comment paragraph." in line), None
    )
    assert after_idx is not None, "Could not find 'After comment paragraph.' in output"

    # Check that the line containing "After comment paragraph." does not contain comment text
    after_line = lines[after_idx]
    assert (
        "This is a comment" not in after_line
    ), "Comment text merged with following paragraph!"


def test_raw_typst_passthrough(simple_document, mock_builder):
    """Test that raw typst content is passed through to output."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a raw node with typst format
    raw_node = nodes.raw("", "#rect(fill: red)[Custom Typst content]", format="typst")

    # visit_raw should raise SkipNode after adding content
    try:
        translator.visit_raw(raw_node)
    except nodes.SkipNode:
        pass  # Expected behavior

    output = translator.astext()

    # Raw typst content should be in output
    assert "#rect(fill: red)[Custom Typst content]" in output


def test_raw_other_formats_skip(simple_document, mock_builder):
    """Test that raw content with non-typst formats is skipped."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create raw nodes with HTML and LaTeX formats
    raw_html = nodes.raw("", '<div class="custom">HTML content</div>', format="html")
    raw_latex = nodes.raw("", r"\textbf{LaTeX content}", format="latex")

    # Visit HTML raw node - should skip
    try:
        translator.visit_raw(raw_html)
    except nodes.SkipNode:
        pass  # Expected to skip

    # Visit LaTeX raw node - should skip
    try:
        translator.visit_raw(raw_latex)
    except nodes.SkipNode:
        pass  # Expected to skip

    output = translator.astext()

    # Non-typst content should NOT be in output
    assert "HTML content" not in output
    assert "LaTeX content" not in output


def test_raw_multiple_formats(simple_document, mock_builder):
    """Test multiple raw directives with different formats."""
    from docutils import frontend
    from docutils.parsers.rst import Parser as RstParser
    from docutils.utils import new_document

    from typsphinx.translator import TypstTranslator

    rst_content = """\
Before paragraph.

.. raw:: typst

   #rect(fill: blue)[Typst content]

.. raw:: html

   <div>HTML content</div>

.. raw:: typst

   #circle(radius: 10pt)

After paragraph.
"""

    # Parse RST content
    parser = RstParser()
    settings = frontend.get_default_settings(RstParser)
    document = new_document("<test>", settings=settings)
    parser.parse(rst_content, document)

    # Translate to Typst
    translator = TypstTranslator(document, mock_builder)
    document.walkabout(translator)
    output = translator.astext()

    # Typst content should be present
    assert "#rect(fill: blue)[Typst content]" in output
    assert "#circle(radius: 10pt)" in output

    # HTML content should NOT be present
    assert "HTML content" not in output

    # Paragraphs should be present
    assert "Before paragraph." in output
    assert "After paragraph." in output


def test_raw_typst_multiline(simple_document, mock_builder):
    """Test that multiline raw typst content preserves formatting."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a raw node with multiline typst content
    multiline_content = """\
#set text(size: 12pt)
#rect(
  fill: gradient.linear(red, blue),
  [Multi-line Typst code]
)"""
    raw_node = nodes.raw("", multiline_content, format="typst")

    # visit_raw should raise SkipNode after adding content
    try:
        translator.visit_raw(raw_node)
    except nodes.SkipNode:
        pass  # Expected behavior

    output = translator.astext()

    # All lines should be in output
    assert "#set text(size: 12pt)" in output
    assert "#rect(" in output
    assert "fill: gradient.linear(red, blue)," in output
    assert "[Multi-line Typst code]" in output


def test_raw_empty_content(simple_document, mock_builder):
    """Test that empty raw directive is handled gracefully."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a raw node with empty content
    raw_node = nodes.raw("", "", format="typst")

    # visit_raw should raise SkipNode even for empty content
    try:
        translator.visit_raw(raw_node)
    except nodes.SkipNode:
        pass  # Expected behavior

    output = translator.astext()

    # Should not raise an error, output may be empty or have minimal whitespace
    assert isinstance(output, str)


def test_raw_case_insensitive_format(simple_document, mock_builder):
    """Test that format name is case-insensitive."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create raw nodes with different case formats
    raw_upper = nodes.raw("", "#text[UPPERCASE]", format="TYPST")
    raw_mixed = nodes.raw("", "#text[MixedCase]", format="Typst")

    # visit_raw should raise SkipNode after adding content
    try:
        translator.visit_raw(raw_upper)
    except nodes.SkipNode:
        pass  # Expected behavior

    try:
        translator.visit_raw(raw_mixed)
    except nodes.SkipNode:
        pass  # Expected behavior

    output = translator.astext()

    # Content should be present regardless of case
    assert "#text[UPPERCASE]" in output
    assert "#text[MixedCase]" in output


# --- Issue #20: Code Block Directive Options Support ---


def test_code_block_without_linenos(simple_document, mock_builder):
    """Test code block without :linenos: option - should disable line numbers."""
    from docutils import nodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block WITHOUT linenos option
    literal_block = nodes.literal_block(text="def hello():\n    return 'world'")
    literal_block["language"] = "python"
    # linenos is NOT set (or False)

    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("def hello():\n    return 'world'"))
    translator.depart_Text(nodes.Text("def hello():\n    return 'world'"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()

    # Should contain code block
    assert "```python" in output
    assert "def hello():" in output

    # Should contain #codly(number-format: none) to disable line numbers
    assert "codly(number-format: none)" in output or "number-format: none" in output


def test_code_block_with_linenos(simple_document, mock_builder):
    """Test code block with :linenos: option - should enable line numbers."""
    from docutils import nodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block WITH linenos option
    literal_block = nodes.literal_block(text="def hello():\n    return 'world'")
    literal_block["language"] = "python"
    literal_block["linenos"] = True

    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("def hello():\n    return 'world'"))
    translator.depart_Text(nodes.Text("def hello():\n    return 'world'"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()

    # Should contain code block
    assert "```python" in output
    assert "def hello():" in output

    # Should NOT disable line numbers (codly default shows line numbers)
    # Or explicitly enable them - codly's default is to show line numbers
    # So we just check that number-format: none is NOT present
    assert "number-format: none" not in output


def test_code_block_linenos_with_highlights(simple_document, mock_builder):
    """Test code block with :linenos: and :emphasize-lines: options."""
    from docutils import nodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a literal block WITH both linenos and emphasize-lines
    literal_block = nodes.literal_block(text="def hello():\n    return 'world'")
    literal_block["language"] = "python"
    literal_block["linenos"] = True
    literal_block["highlight_args"] = {"hl_lines": [1]}

    translator.visit_literal_block(literal_block)
    translator.visit_Text(nodes.Text("def hello():\n    return 'world'"))
    translator.depart_Text(nodes.Text("def hello():\n    return 'world'"))
    translator.depart_literal_block(literal_block)

    output = translator.astext()

    # Should contain code block
    assert "```python" in output
    assert "def hello():" in output

    # Should have highlight (already implemented)
    assert "codly-range(highlight: (1))" in output

    # Should NOT disable line numbers
    assert "number-format: none" not in output


def test_code_block_with_caption(simple_document, mock_builder):
    """Test code block with :caption: option - should wrap in #figure()."""
    from docutils import nodes

    from typsphinx.translator import TypstTranslator

    # Manually create container structure that Sphinx generates for captioned code blocks
    # Structure: container[literal-block-wrapper] > (caption + literal_block)
    container = nodes.container()
    container["classes"].append("literal-block-wrapper")

    caption = nodes.caption()
    caption += nodes.Text("Example function")

    literal_block = nodes.literal_block()
    literal_block["language"] = "python"
    literal_block += nodes.Text("def example():\n    pass")

    container += caption
    container += literal_block

    simple_document += container

    translator = TypstTranslator(simple_document, mock_builder)
    simple_document.walkabout(translator)
    output = translator.astext()

    # Should contain #figure() wrapper
    assert "figure(caption: [Example function])" in output or "figure(" in output
    # Should contain code block
    assert "```python" in output
    assert "def example():" in output
    # Should use trailing content block format: #figure(...)[code]
    # The closing ] should appear after the code block
    assert "]" in output


def test_code_block_with_caption_and_name(simple_document, mock_builder):
    """Test code block with :caption: and :name: options."""
    from docutils import nodes

    from typsphinx.translator import TypstTranslator

    # Manually create container structure that Sphinx generates
    container = nodes.container()
    container["classes"].append("literal-block-wrapper")

    caption = nodes.caption()
    caption += nodes.Text("Example function")

    literal_block = nodes.literal_block()
    literal_block["language"] = "python"
    literal_block["names"].append("code-example")  # This is how :name: is stored
    literal_block += nodes.Text("def example():\n    pass")

    container += caption
    container += literal_block

    simple_document += container

    translator = TypstTranslator(simple_document, mock_builder)
    simple_document.walkabout(translator)
    output = translator.astext()

    # Should contain #figure() with caption
    assert "figure(caption: [Example function])" in output or "figure(" in output
    # Should contain label
    assert "<code-example>" in output
    # Should contain code block
    assert "```python" in output


def test_code_block_with_name_only(simple_document, mock_builder):
    """Test code block with :name: option only (no caption)."""
    from docutils import nodes

    from typsphinx.translator import TypstTranslator

    # Create literal_block with name but no caption (no container wrapper)
    literal_block = nodes.literal_block()
    literal_block["language"] = "python"
    literal_block["names"].append("code-example")  # :name: option
    literal_block += nodes.Text("def example():\n    pass")

    simple_document += literal_block

    translator = TypstTranslator(simple_document, mock_builder)
    simple_document.walkabout(translator)
    output = translator.astext()

    # Should NOT wrap in #figure() (no caption)
    assert "#figure(" not in output
    # Should contain label after code block
    assert "<code-example>" in output
    # Should contain code block
    assert "```python" in output


def test_code_block_all_options(simple_document, mock_builder):
    """Test code block with all options combined."""
    from docutils import nodes

    from typsphinx.translator import TypstTranslator

    # Create container structure with all options
    container = nodes.container()
    container["classes"].append("literal-block-wrapper")

    caption = nodes.caption()
    caption += nodes.Text("Example function")

    literal_block = nodes.literal_block()
    literal_block["language"] = "python"
    literal_block["names"].append("code-example")  # :name: option
    literal_block["linenos"] = True  # :linenos: option
    literal_block["highlight_args"] = {"hl_lines": [1]}  # :emphasize-lines: option
    literal_block += nodes.Text("def example():\n    pass")

    container += caption
    container += literal_block

    simple_document += container

    translator = TypstTranslator(simple_document, mock_builder)
    simple_document.walkabout(translator)
    output = translator.astext()

    # Should have line numbers (no number-format: none)
    assert "number-format: none" not in output
    # Should have highlights
    assert "codly-range(highlight: (1))" in output
    # Should have figure with caption
    assert "figure(" in output
    # Should have label
    assert "<code-example>" in output
    # Should contain code block
    assert "```python" in output


# --- Issue #40: Table Header Support ---


def test_table_header_wrapping(simple_document, mock_builder):
    """Test that table headers are wrapped in table.header()."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a simple 2x2 table with header
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)

    # Add column specifications
    colspec1 = nodes.colspec(colwidth=1)
    colspec2 = nodes.colspec(colwidth=1)
    tgroup += colspec1
    tgroup += colspec2

    # Add header row
    thead = nodes.thead()
    row1 = nodes.row()
    entry1 = nodes.entry()
    entry1 += nodes.paragraph(text="Header 1")
    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="Header 2")
    row1 += entry1
    row1 += entry2
    thead += row1
    tgroup += thead

    # Add body row
    tbody = nodes.tbody()
    row2 = nodes.row()
    entry3 = nodes.entry()
    entry3 += nodes.paragraph(text="Cell 1")
    entry4 = nodes.entry()
    entry4 += nodes.paragraph(text="Cell 2")
    row2 += entry3
    row2 += entry4
    tbody += row2
    tgroup += tbody

    table += tgroup

    # Visit the table using walkabout
    table.walkabout(translator)

    output = translator.astext()

    # Check that table.header() wrapper is generated
    assert "table.header(" in output
    assert "Header 1" in output
    assert "Header 2" in output
    assert "Cell 1" in output
    assert "Cell 2" in output


def test_table_without_header(simple_document, mock_builder):
    """Test that tables without headers work correctly (no table.header())."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a simple 2x2 table WITHOUT header (only tbody)
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)

    # Add column specifications
    colspec1 = nodes.colspec(colwidth=1)
    colspec2 = nodes.colspec(colwidth=1)
    tgroup += colspec1
    tgroup += colspec2

    # Add body rows only (no thead)
    tbody = nodes.tbody()
    row1 = nodes.row()
    entry1 = nodes.entry()
    entry1 += nodes.paragraph(text="Cell 1")
    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="Cell 2")
    row1 += entry1
    row1 += entry2
    tbody += row1

    row2 = nodes.row()
    entry3 = nodes.entry()
    entry3 += nodes.paragraph(text="Cell 3")
    entry4 = nodes.entry()
    entry4 += nodes.paragraph(text="Cell 4")
    row2 += entry3
    row2 += entry4
    tbody += row2

    tgroup += tbody
    table += tgroup

    # Visit the table using walkabout
    table.walkabout(translator)

    output = translator.astext()

    # Check that table.header() is NOT generated
    assert "table.header(" not in output
    # But table() should still be generated (no # in unified code mode)
    assert "table(" in output
    assert "Cell 1" in output
    assert "Cell 2" in output
    assert "Cell 3" in output
    assert "Cell 4" in output


def test_table_multi_row_header(simple_document, mock_builder):
    """Test that tables with multiple header rows wrap all headers in table.header()."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a table with 2 header rows and 1 body row
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)

    # Add column specifications
    colspec1 = nodes.colspec(colwidth=1)
    colspec2 = nodes.colspec(colwidth=1)
    tgroup += colspec1
    tgroup += colspec2

    # Add 2 header rows
    thead = nodes.thead()
    row1 = nodes.row()
    entry1 = nodes.entry()
    entry1 += nodes.paragraph(text="Header 1-1")
    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="Header 1-2")
    row1 += entry1
    row1 += entry2
    thead += row1

    row2 = nodes.row()
    entry3 = nodes.entry()
    entry3 += nodes.paragraph(text="Header 2-1")
    entry4 = nodes.entry()
    entry4 += nodes.paragraph(text="Header 2-2")
    row2 += entry3
    row2 += entry4
    thead += row2
    tgroup += thead

    # Add body row
    tbody = nodes.tbody()
    row3 = nodes.row()
    entry5 = nodes.entry()
    entry5 += nodes.paragraph(text="Body 1")
    entry6 = nodes.entry()
    entry6 += nodes.paragraph(text="Body 2")
    row3 += entry5
    row3 += entry6
    tbody += row3
    tgroup += tbody

    table += tgroup

    # Visit the table using walkabout
    table.walkabout(translator)

    output = translator.astext()

    # Check that table.header() wrapper contains all 4 header cells
    assert "table.header(" in output
    assert "Header 1-1" in output
    assert "Header 1-2" in output
    assert "Header 2-1" in output
    assert "Header 2-2" in output
    assert "Body 1" in output
    assert "Body 2" in output

    # Verify structure: header cells should come before body cells
    header_pos = output.index("table.header(")
    body1_pos = output.index("Body 1")
    assert header_pos < body1_pos


def test_in_thead_state_management(simple_document, mock_builder):
    """Test that in_thead state is managed correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Initially not in thead
    assert translator.in_thead is False

    # Visit a thead
    thead = nodes.thead()
    translator.visit_thead(thead)
    assert translator.in_thead is True

    # Depart thead
    translator.depart_thead(thead)
    assert translator.in_thead is False


# --- Issue #39: Cell Spanning Support ---


def test_table_cell_colspan(simple_document, mock_builder):
    """Test that cells with morecols generate colspan in Typst."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a table with colspan
    table = nodes.table()
    tgroup = nodes.tgroup(cols=3)

    colspec1 = nodes.colspec(colwidth=1)
    colspec2 = nodes.colspec(colwidth=1)
    colspec3 = nodes.colspec(colwidth=1)
    tgroup += colspec1
    tgroup += colspec2
    tgroup += colspec3

    tbody = nodes.tbody()
    row1 = nodes.row()

    # Cell spanning 2 columns (morecols=1)
    entry1 = nodes.entry(morecols=1)
    entry1 += nodes.paragraph(text="Spans 2 cols")
    row1 += entry1

    # Normal cell
    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="Col 3")
    row1 += entry2

    tbody += row1
    tgroup += tbody
    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should have table.cell with content first, then colspan: 2
    assert "table.cell(" in output
    assert "colspan: 2)" in output
    assert "Spans 2 cols" in output
    assert "Col 3" in output


def test_table_cell_rowspan(simple_document, mock_builder):
    """Test that cells with morerows generate rowspan in Typst."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a table with rowspan
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)

    colspec1 = nodes.colspec(colwidth=1)
    colspec2 = nodes.colspec(colwidth=1)
    tgroup += colspec1
    tgroup += colspec2

    tbody = nodes.tbody()

    # Row 1
    row1 = nodes.row()
    # Cell spanning 2 rows (morerows=1)
    entry1 = nodes.entry(morerows=1)
    entry1 += nodes.paragraph(text="Spans 2 rows")
    row1 += entry1

    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="Row 1 Col 2")
    row1 += entry2
    tbody += row1

    # Row 2
    row2 = nodes.row()
    entry3 = nodes.entry()
    entry3 += nodes.paragraph(text="Row 2 Col 2")
    row2 += entry3
    tbody += row2

    tgroup += tbody
    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should have table.cell with content first, then rowspan: 2
    assert "table.cell(" in output
    assert "rowspan: 2)" in output
    assert "Spans 2 rows" in output


def test_table_cell_colspan_and_rowspan(simple_document, mock_builder):
    """Test that cells with both morecols and morerows generate both colspan and rowspan."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a table with both colspan and rowspan
    table = nodes.table()
    tgroup = nodes.tgroup(cols=3)

    colspec1 = nodes.colspec(colwidth=1)
    colspec2 = nodes.colspec(colwidth=1)
    colspec3 = nodes.colspec(colwidth=1)
    tgroup += colspec1
    tgroup += colspec2
    tgroup += colspec3

    tbody = nodes.tbody()

    # Row 1
    row1 = nodes.row()
    # Cell spanning 2 cols and 2 rows (morecols=1, morerows=1)
    entry1 = nodes.entry(morecols=1, morerows=1)
    entry1 += nodes.paragraph(text="Spans 2x2")
    row1 += entry1

    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="R1 C3")
    row1 += entry2
    tbody += row1

    # Row 2
    row2 = nodes.row()
    entry3 = nodes.entry()
    entry3 += nodes.paragraph(text="R2 C3")
    row2 += entry3
    tbody += row2

    tgroup += tbody
    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should have table.cell with content first, then colspan and rowspan
    assert "table.cell(" in output
    assert "colspan: 2, rowspan: 2)" in output
    assert "Spans 2x2" in output


def test_table_header_cell_with_colspan(simple_document, mock_builder):
    """Test that header cells with colspan work correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a table with header colspan
    table = nodes.table()
    tgroup = nodes.tgroup(cols=3)

    colspec1 = nodes.colspec(colwidth=1)
    colspec2 = nodes.colspec(colwidth=1)
    colspec3 = nodes.colspec(colwidth=1)
    tgroup += colspec1
    tgroup += colspec2
    tgroup += colspec3

    # Header with spanning cell
    thead = nodes.thead()
    row1 = nodes.row()
    # Header spanning 2 columns
    entry1 = nodes.entry(morecols=1)
    entry1 += nodes.paragraph(text="Header 1-2")
    row1 += entry1

    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="Header 3")
    row1 += entry2
    thead += row1
    tgroup += thead

    # Body
    tbody = nodes.tbody()
    row2 = nodes.row()
    entry3 = nodes.entry()
    entry3 += nodes.paragraph(text="Cell 1")
    row2 += entry3

    entry4 = nodes.entry()
    entry4 += nodes.paragraph(text="Cell 2")
    row2 += entry4

    entry5 = nodes.entry()
    entry5 += nodes.paragraph(text="Cell 3")
    row2 += entry5
    tbody += row2
    tgroup += tbody

    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should have table.header() with colspan cell
    assert "table.header(" in output
    assert "table.cell(" in output
    assert "colspan: 2)" in output
    assert "Header 1-2" in output
    assert "Header 3" in output


def test_table_normal_cells_without_spanning(simple_document, mock_builder):
    """Test that normal cells (without spanning) still work correctly."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a simple table without any spanning
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)

    colspec1 = nodes.colspec(colwidth=1)
    colspec2 = nodes.colspec(colwidth=1)
    tgroup += colspec1
    tgroup += colspec2

    tbody = nodes.tbody()
    row1 = nodes.row()

    entry1 = nodes.entry()
    entry1 += nodes.paragraph(text="Cell 1")
    row1 += entry1

    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="Cell 2")
    row1 += entry2

    tbody += row1
    tgroup += tbody
    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should NOT have table.cell() for normal cells
    assert "table.cell" not in output
    # Should have simple bracket cells
    assert "Cell 1" in output
    assert "Cell 2" in output


# Empty table cell tests (Issue #68)


def test_table_empty_cells(simple_document, mock_builder):
    """Test that empty table cells are wrapped in content blocks.

    Related to Issue #68: Empty table cells cause Typst compilation errors.
    Empty cells should be wrapped in {} to generate valid Typst syntax.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create table with all empty cells
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)
    tgroup += nodes.colspec(colwidth=1)
    tgroup += nodes.colspec(colwidth=1)

    tbody = nodes.tbody()
    row1 = nodes.row()
    entry1 = nodes.entry()  # Empty cell
    entry2 = nodes.entry()  # Empty cell
    row1 += entry1
    row1 += entry2
    tbody += row1
    tgroup += tbody
    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should contain empty content blocks
    assert "{}" in output
    # Should NOT contain bare commas
    assert ",," not in output
    assert "  ,\n" not in output


def test_table_mixed_empty_and_content(simple_document, mock_builder):
    """Test table with both empty and non-empty cells.

    Related to Issue #68: Empty table cells cause Typst compilation errors.
    Tables with mixed empty and non-empty cells should generate valid Typst syntax.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create table: A | (empty) / (empty) | D
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)
    tgroup += nodes.colspec(colwidth=1)
    tgroup += nodes.colspec(colwidth=1)

    tbody = nodes.tbody()

    # Row 1: A | empty
    row1 = nodes.row()
    entry1 = nodes.entry()
    entry1 += nodes.paragraph(text="A")
    entry2 = nodes.entry()  # Empty
    row1 += entry1
    row1 += entry2
    tbody += row1

    # Row 2: empty | D
    row2 = nodes.row()
    entry3 = nodes.entry()  # Empty
    entry4 = nodes.entry()
    entry4 += nodes.paragraph(text="D")
    row2 += entry3
    row2 += entry4
    tbody += row2

    tgroup += tbody
    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should contain content for non-empty cells
    assert "A" in output
    assert "D" in output
    # Should contain empty content blocks
    assert "{}" in output
    # Should NOT contain bare commas
    assert ",," not in output


def test_table_empty_colspan_cells(simple_document, mock_builder):
    """Test that empty cells with colspan use table.cell with empty content.

    Related to Issue #68: Empty table cells cause Typst compilation errors.
    Empty cells with colspan should use table.cell({}, colspan: N) syntax.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create table with empty colspan cell
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)
    tgroup += nodes.colspec(colwidth=1)
    tgroup += nodes.colspec(colwidth=1)

    tbody = nodes.tbody()
    row1 = nodes.row()

    # Empty cell with colspan=2
    entry1 = nodes.entry(morecols=1)  # Empty, spans 2 columns
    row1 += entry1
    tbody += row1
    tgroup += tbody
    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should use table.cell with empty content
    assert "table.cell({}" in output
    assert "colspan: 2" in output
    # Should NOT contain bare commas or missing content
    assert "table.cell(," not in output


def test_table_empty_rowspan_cells(simple_document, mock_builder):
    """Test that empty cells with rowspan use table.cell with empty content.

    Related to Issue #68: Empty table cells cause Typst compilation errors.
    Empty cells with rowspan should use table.cell({}, rowspan: N) syntax.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create table with empty rowspan cell
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)
    tgroup += nodes.colspec(colwidth=1)
    tgroup += nodes.colspec(colwidth=1)

    tbody = nodes.tbody()
    row1 = nodes.row()

    # Empty cell with rowspan=2
    entry1 = nodes.entry(morerows=1)  # Empty, spans 2 rows
    entry2 = nodes.entry()
    entry2 += nodes.paragraph(text="B")
    row1 += entry1
    row1 += entry2
    tbody += row1

    # Row 2
    row2 = nodes.row()
    entry3 = nodes.entry()
    entry3 += nodes.paragraph(text="C")
    row2 += entry3
    tbody += row2

    tgroup += tbody
    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should use table.cell with empty content
    assert "table.cell({}" in output
    assert "rowspan: 2" in output
    # Should NOT contain bare commas or missing content
    assert "table.cell(," not in output


def test_table_empty_colspan_rowspan_cells(simple_document, mock_builder):
    """Test that empty cells with both colspan and rowspan use table.cell with empty content.

    Related to Issue #68: Empty table cells cause Typst compilation errors.
    Empty cells with both colspan and rowspan should use table.cell({}, colspan: M, rowspan: N) syntax.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create table with empty colspan+rowspan cell
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)
    tgroup += nodes.colspec(colwidth=1)
    tgroup += nodes.colspec(colwidth=1)

    tbody = nodes.tbody()
    row1 = nodes.row()

    # Empty cell with colspan=2, rowspan=2
    entry1 = nodes.entry(morecols=1, morerows=1)  # Empty, spans 2x2
    row1 += entry1
    tbody += row1

    # Row 2 (no cells needed due to spanning)
    row2 = nodes.row()
    tbody += row2

    tgroup += tbody
    table += tgroup

    table.walkabout(translator)
    output = translator.astext()

    # Should use table.cell with empty content
    assert "table.cell({}" in output
    assert "colspan: 2" in output
    assert "rowspan: 2" in output
    # Should NOT contain bare commas or missing content
    assert "table.cell(," not in output


# API description nodes tests (Issue #55)


def test_index_node_is_skipped(simple_document, mock_builder):
    """Test that index nodes are skipped in output."""
    from sphinx import addnodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create an index node
    index = addnodes.index(entries=[("single", "example", "example-id", "", None)])

    # Index should raise SkipNode
    with pytest.raises(nodes.SkipNode):
        translator.visit_index(index)

    # Output should be empty (index is skipped)
    output = translator.astext()
    assert output == ""


def test_desc_signature_rendering(simple_document, mock_builder):
    """Test that desc_signature nodes are rendered in bold."""
    from sphinx import addnodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create a desc node with signature
    desc = addnodes.desc()
    sig = addnodes.desc_signature()
    sig += nodes.Text("TypstBuilder(app, env)")
    desc += sig

    desc.walkabout(translator)
    output = translator.astext()

    assert "TypstBuilder" in output and "strong({" in output


def test_desc_with_annotation_and_name(simple_document, mock_builder):
    """Test desc_signature with annotation (class keyword) and name."""
    from sphinx import addnodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create: class TypstBuilder
    desc = addnodes.desc()
    sig = addnodes.desc_signature()

    annotation = addnodes.desc_annotation()
    annotation += nodes.Text("class")
    sig += annotation

    name = addnodes.desc_name()
    name += nodes.Text("TypstBuilder")
    sig += name

    desc += sig

    desc.walkabout(translator)
    output = translator.astext()

    assert 'strong({text("class")' in output and 'text("TypstBuilder")' in output


def test_desc_parameterlist(simple_document, mock_builder):
    """Test desc_parameterlist with multiple parameters."""
    from sphinx import addnodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create: function(arg1, arg2, arg3)
    desc = addnodes.desc()
    sig = addnodes.desc_signature()

    name = addnodes.desc_name()
    name += nodes.Text("function")
    sig += name

    paramlist = addnodes.desc_parameterlist()
    param1 = addnodes.desc_parameter()
    param1 += nodes.Text("arg1")
    paramlist += param1

    param2 = addnodes.desc_parameter()
    param2 += nodes.Text("arg2")
    paramlist += param2

    param3 = addnodes.desc_parameter()
    param3 += nodes.Text("arg3")
    paramlist += param3

    sig += paramlist
    desc += sig

    desc.walkabout(translator)
    output = translator.astext()

    assert 'strong({text("function")' in output and "arg1" in output


def test_field_list_rendering(simple_document, mock_builder):
    """Test field_list rendering with field names and bodies."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create: Parameters: description text
    field_list = nodes.field_list()
    field = nodes.field()

    field_name = nodes.field_name()
    field_name += nodes.Text("Parameters")
    field += field_name

    field_body = nodes.field_body()
    para = nodes.paragraph()
    para += nodes.Text("description text")
    field_body += para
    field += field_body

    field_list += field

    field_list.walkabout(translator)
    output = translator.astext()

    assert 'strong(text("Parameters")' in output or "Parameters" in output
    assert "description text" in output


def test_rubric_rendering(simple_document, mock_builder):
    """Test rubric nodes are rendered as strong text."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    rubric = nodes.rubric()
    rubric += nodes.Text("Methods")

    rubric.walkabout(translator)
    output = translator.astext()

    assert 'strong({text("Methods")]' in output or "Methods" in output


def test_title_reference_rendering(simple_document, mock_builder):
    """Test title_reference nodes are rendered in emphasis."""
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    title_ref = nodes.title_reference()
    title_ref += nodes.Text("Example Title")

    title_ref.walkabout(translator)
    output = translator.astext()

    assert 'emph({text("Example Title")})' in output


def test_full_api_description_structure(simple_document, mock_builder):
    """Test complete API description with signature, content, and field list."""
    from sphinx import addnodes

    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Create: class TypstBuilder(app, env)
    #         Description text.
    #         Parameters: ...
    desc = addnodes.desc()

    # Signature
    sig = addnodes.desc_signature()
    annotation = addnodes.desc_annotation()
    annotation += nodes.Text("class")
    sig += annotation

    name = addnodes.desc_name()
    name += nodes.Text("TypstBuilder")
    sig += name

    paramlist = addnodes.desc_parameterlist()
    param1 = addnodes.desc_parameter()
    param1 += nodes.Text("app")
    paramlist += param1

    param2 = addnodes.desc_parameter()
    param2 += nodes.Text("env")
    paramlist += param2

    sig += paramlist
    desc += sig

    # Content
    content = addnodes.desc_content()
    para = nodes.paragraph()
    para += nodes.Text("Builder class for Typst output.")
    content += para

    # Field list
    field_list = nodes.field_list()
    field = nodes.field()

    field_name = nodes.field_name()
    field_name += nodes.Text("Parameters")
    field += field_name

    field_body = nodes.field_body()
    param_para = nodes.paragraph()
    param_para += nodes.Text("app - Sphinx application")
    field_body += param_para
    field += field_body

    field_list += field
    content += field_list

    desc += content

    desc.walkabout(translator)
    output = translator.astext()

    # Check all parts are present
    assert 'strong({text("class")' in output and "TypstBuilder" in output
    assert "Builder class for Typst output." in output
    assert 'strong(text("Parameters")' in output or "Parameters" in output
    assert "app - Sphinx application" in output


# Image path adjustment tests (Issue #69)


def test_image_path_adjustment_root(simple_document, mock_builder):
    """Test that root document image paths are not adjusted.

    Related to Issue #69: Image paths in root documents should remain unchanged.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Set current_docname to root document
    mock_builder.current_docname = "index"

    # Create image node
    image = nodes.image(uri="images/logo.png")
    image["width"] = "200px"

    image.walkabout(translator)
    output = translator.astext()

    # Root document: path should NOT be adjusted
    assert 'image("images/logo.png"' in output
    assert "../images" not in output
    assert "width: 200px" in output


def test_image_path_adjustment_nested(simple_document, mock_builder):
    """Test that nested document image paths are adjusted with ../ prefix.

    Related to Issue #69: Nested documents need relative path adjustment.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Set current_docname to nested document
    mock_builder.current_docname = "chapter1/section1"

    # Create image node with source-root-relative path
    image = nodes.image(uri="images/logo.png")
    image["width"] = "200px"

    image.walkabout(translator)
    output = translator.astext()

    # Nested document: path should be adjusted
    assert 'image("../images/logo.png"' in output
    assert "width: 200px" in output


def test_image_path_adjustment_deep_nested(simple_document, mock_builder):
    """Test that deeply nested documents get correct number of ../ prefixes.

    Related to Issue #69: Deep nesting requires multiple ../ levels.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Set current_docname to deeply nested document
    mock_builder.current_docname = "part1/chapter1/section1"

    # Create image node
    image = nodes.image(uri="images/logo.png")

    image.walkabout(translator)
    output = translator.astext()

    # Deeply nested: should have ../../ prefix
    assert 'image("../../images/logo.png"' in output


def test_image_path_adjustment_cross_directory(simple_document, mock_builder):
    """Test that cross-directory image references are correctly adjusted.

    Related to Issue #69: References from chapter1/ to chapter2/ images.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Set current document in chapter1
    mock_builder.current_docname = "chapter1/section1"

    # Reference image in chapter2
    image = nodes.image(uri="chapter2/images/diagram.png")

    image.walkabout(translator)
    output = translator.astext()

    # Cross-directory: ../chapter2/images/diagram.png
    assert 'image("../chapter2/images/diagram.png"' in output


def test_image_path_adjustment_same_directory(simple_document, mock_builder):
    """Test that same-directory images use simple relative paths.

    Related to Issue #69: Images in the same directory as the document.
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Both in chapter1/
    mock_builder.current_docname = "chapter1/section1"

    # Image also in chapter1/
    image = nodes.image(uri="chapter1/local-image.png")

    image.walkabout(translator)
    output = translator.astext()

    # Same directory: just the filename
    assert 'image("local-image.png"' in output
    assert "../" not in output


def test_image_path_adjustment_subdirectory(simple_document, mock_builder):
    """Test that subdirectory images use relative paths to child folders.

    Related to Issue #69: Images in subdirectories relative to the document.
    Example: chapter1/section1.rst references chapter1/img/diagram.jpeg
    """
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    # Document in chapter1/
    mock_builder.current_docname = "chapter1/section1"

    # Image in chapter1/img/ (subdirectory of same directory)
    image = nodes.image(uri="chapter1/img/diagram.jpeg")
    image["width"] = "250px"

    image.walkabout(translator)
    output = translator.astext()

    # Subdirectory: img/diagram.jpeg (relative to current directory)
    assert 'image("img/diagram.jpeg"' in output
    assert "width: 250px" in output
    assert "../" not in output  # No need to go up

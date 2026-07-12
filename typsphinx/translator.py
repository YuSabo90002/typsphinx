"""
Typst translator for docutils nodes.

This module implements the TypstTranslator class, which translates docutils
nodes to Typst markup.
"""

import re
from typing import Any, List, Tuple

from docutils import nodes
from sphinx import addnodes
from sphinx.util import logging
from sphinx.util.docutils import SphinxTranslator

logger = logging.getLogger(__name__)

# Units docutils may normalize into `:width:`/`:height:` (via
# length_or_percentage_or_unitless / length_or_unitless) that are already
# valid Typst length units and should pass through unchanged.
_TYPST_PASSTHROUGH_UNITS = {"%", "em", "pt", "cm", "mm", "in"}


def escape_typst_string(text: str) -> str:
    """Escape arbitrary text for embedding inside a Typst ``"..."`` string literal.

    Typst string literals cannot span physical lines and treat ``\\`` and ``"``
    specially, so every character that would break the literal (or be
    misinterpreted) must be escaped. This is the single source of truth for
    string-literal escaping across the translator: any site that emits
    ``raw("...")``, ``text("...")``, etc. from node-derived text routes through
    this helper so the class of problem is handled consistently.

    Escaping order is significant: backslash MUST be escaped first, otherwise
    the backslashes introduced by the later replacements would themselves be
    doubled.

    The newline/CR/tab escapes turn a literal control character into its
    two-character escape sequence (e.g. a raw ``\\n`` becomes the sequence
    ``\\`` + ``n``). Typst decodes that back into the original control character
    when rendering, so the visible content is preserved while the emitted
    ``.typ`` stays valid single-line syntax.

    Args:
        text: Raw text to escape (e.g. ``node.astext()``).

    Returns:
        Text safe to embed between double quotes in a Typst string literal.
    """
    text = text.replace("\\", "\\\\")  # Backslash (FIRST, avoids double-escaping)
    text = text.replace('"', '\\"')  # Quote
    text = text.replace("\n", "\\n")  # Newline
    text = text.replace("\r", "\\r")  # Carriage return
    text = text.replace("\t", "\\t")  # Tab
    return text


class TypstTranslator(SphinxTranslator):
    """
    Translator class that converts docutils nodes to Typst markup.

    This translator visits nodes in the document tree and generates
    corresponding Typst markup.
    """

    def __init__(self, document: nodes.document, builder: Any) -> None:
        """
        Initialize the translator.

        Args:
            document: The docutils document to translate
            builder: The Sphinx builder instance
        """
        super().__init__(document, builder)
        self.builder = builder
        self.body = []

        # State management variables
        self.section_level = 0
        self.in_figure = False
        self.in_table = False
        self.in_thead = False  # Track if currently in table header
        self.in_caption = False
        self.list_stack = []  # Track list nesting: 'bullet' or 'enumerated'

        # Figure-specific state
        self.figure_content = []
        self.figure_caption = ""
        self._saved_body_for_figure_caption: List[Any] | None = (
            None  # Body to restore after buffering a figure caption (buffer-swap idiom)
        )

        # Code block container state (Issue #20)
        self.in_captioned_code_block = False
        self.code_block_caption = ""
        self.code_block_label = ""

        # Unified code mode state
        self.in_paragraph = False
        self.paragraph_has_content = False  # Track if paragraph has any content nodes
        self.in_list_item = False  # Track if currently in a list item
        # Stack of prior in_list_item values, pushed on each visit_list_item
        # and popped on depart_list_item. A bare boolean loses the outer
        # item's context when a NESTED list closes (its depart_list_item would
        # otherwise reset the flag to False), which mis-classifies a paragraph
        # following a nested list as top-level and emits an unseparated
        # `par(...)` right after the nested `list(...)` -> `})par(` syntax error.
        self._list_item_stack: List[bool] = []
        self.in_literal_block = False  # Track if currently in a code block

        # Stream-based list rendering state (Issue #61)
        self.is_first_list_item = True  # Track if current item is first in list
        self.list_item_needs_separator = (
            False  # Track if + is needed before next element
        )
        self._in_reference_with_target = (
            False  # Track if reference has following target for markup mode wrapping
        )
        self._in_markup_mode = (
            False  # Track if currently inside markup mode block [...] for # prefix
        )
        self.in_desc_parameter = (
            False  # Track if inside desc_parameter to avoid newlines between text nodes
        )
        self._in_link = False  # Track if inside link() function for + concatenation
        self._desc_parameter_has_content: bool = (
            False  # Track if desc_parameter has content for + separator
        )
        self._is_first_desc_signature_line: bool = (
            True  # Track if next desc_signature_line is the first (DESC-02);
            # reset per signature in visit_desc_signature
        )
        self._link_has_content: bool = (
            False  # Track if link has content for + separator
        )

        # Block-quote / epigraph attribution code-mode concat context. An
        # attribution node holds INLINE children directly (Text/emphasis/
        # literal/reference) -- no wrapping paragraph -- so, like a def-list
        # term or link body, adjacent children juxtapose in code mode unless
        # + separated. visit_attribution emits the attribution as a CODE-MODE
        # `attribution: { ... }` argument (mirroring the code-mode quote body,
        # bug #15) and activates this context so the children are evaluated
        # content (`emph({...}) + text(...) + raw(...)`), not literal prose --
        # a markup-mode `attribution: [ ... ]` argument would leave the
        # code-mode children as literal source that Typst typesets verbatim
        # (e.g. `text("Author")` shown as `text(“Author”)`).
        self._in_attribution = False
        self._attribution_has_content: bool = False

        # Definition list state
        self.in_definition_list = False
        self._in_term = False  # Track if buffering a def-list term for + concatenation
        self._term_has_content: bool = (
            False  # Track if the term buffer has content for + separator
        )
        self.current_term_buffer: str | List[str] | None = None
        self.current_definition_buffer: List[str] | None = None

        # Field-body code-mode concat context. A field body written inline on
        # its field line (e.g. ':default: The value of **x**') is COLLAPSED by
        # docutils to inline children (Text/strong/literal) directly under
        # field_body -- no wrapping paragraph. Those juxtapose in code mode
        # unless + separated (bug #8). Activated by visit_field_body only for
        # an all-inline field body; _field_body_stack saves the prior value for
        # nesting safety.
        self._in_field_body = False
        self._field_body_has_content: bool = False
        self._field_body_stack: List[Tuple[bool, bool]] = []

        # Stack of the code-mode concat context suppressed while an inline
        # block element (emphasis/strong/reference) emits its OWN block/argument
        # content. Each entry is the (flag, has_content) attribute-name pair
        # saved by _enter_inline_concat_element and restored by
        # _exit_inline_concat_element (or None when no context was active).
        self._inline_concat_stack: List[Tuple[str, str] | None] = []
        # (term, definition) pairs for the CURRENT (innermost) definition list.
        # Aliases the top of _deflist_items_stack so a nested definition list
        # cannot clobber the enclosing list's collected items.
        self.definition_list_items: List[Tuple[str, str]] = []
        # Stacks that make definition-list buffering re-entrant. A definition
        # may CONTAIN a nested definition list (e.g. an autodoc docstring whose
        # first block IS a definition list); each level must save/restore its
        # own body buffer, pending term, and item collection. A single slot
        # (the old self.saved_body / current_*_buffer) is overwritten by the
        # inner list, orphaning the outer body -- both the outer definition's
        # content AND any body written afterward (a desc_signature + its <id>
        # anchor) are then silently dropped, dangling the cross-reference link
        # (GATE-02 fatal #18). Mirrors the _list_item_stack (bug #4) and
        # _inline_concat_stack (bug #5) stack idiom.
        self._saved_body_stack: List[List[Any]] = []
        self._deflist_items_stack: List[List[Tuple[str, str]]] = []
        self._pending_term_stack: List[str | None] = []

        # Admonition title state (buffer-swap idiom, mirrors definition-list terms)
        self._pending_admonition_title: str | None = (
            None  # Rendered inline content of a dynamic (node-derived) title
        )
        self._in_admonition_title: bool = (
            False  # Track if currently buffering an admonition title node
        )
        self._saved_body_for_admonition_title: List[Any] | None = (
            None  # Body to restore after buffering an admonition title
        )
        self._custom_admonition_title: str | None = (
            None  # Static Python-literal title (e.g. "Important", "See Also")
        )
        self._title_section_ids: List[str] = (
            []  # Parent section's ids, captured in visit_title for the
            # matching depart_title's anchor emission (see visit_title)
        )

        # Topic state (BLK-02/D-01/D-02/D-05): distinguishes a box-less
        # `.. contents::` topic (bullet_list pass-through) from a generic
        # `.. topic::` (rendered as a titled clue box via _visit_admonition)
        self._topic_is_contents: bool = False

        # Line block state (BLK-03/D-03/D-04): a single integer nesting-depth
        # counter -- docutils' own visitor recursion already provides the
        # "stack" for nested line_block, so no separate data structure is
        # needed. The two `_was_*` attributes save/restore the surrounding
        # in_paragraph/paragraph_has_content state around the outer
        # par({...}) wrapper (depth 0 only).
        self._line_block_depth: int = 0
        self._line_block_was_in_paragraph: bool = False
        self._line_block_was_paragraph_has_content: bool = False

    def astext(self) -> str:
        """
        Return the translated text as a string.

        Returns:
            The translated Typst markup
        """
        return "".join(self.body)

    def add_text(self, text: str) -> None:
        """
        Add text to the output body or table cell content.

        Args:
            text: The text to add
        """
        if (
            hasattr(self, "in_table")
            and self.in_table
            and hasattr(self, "table_cell_content")
        ):
            self.table_cell_content.append(text)
        else:
            self.body.append(text)

    def _add_paragraph_separator(self) -> None:
        """
        Add + operator for concatenation in paragraph if not first node.

        In unified code mode, paragraph content nodes are concatenated with +.
        This method adds ' + ' before each node except the first one.
        """
        if self.in_paragraph and self.paragraph_has_content:
            self.add_text("\n")
        if self.in_paragraph:
            self.paragraph_has_content = True

    def _emit_id_anchors(
        self, node: nodes.Node, skip_ids: set[str] | None = None
    ) -> None:
        """
        Emit a zero-width ``[#metadata(none) <id>]`` Typst anchor for every id
        carried on a body element so a same-document ``link(<id>, ...)``
        reference resolves to it.

        docutils' ``PropagateTargets`` transform moves an explicit
        ``.. _target:`` id onto the ids of the *following* body element
        (paragraph, bullet/enumerated list, table, image, admonition,
        line-block, block-quote, definition-list, ...). Unless that element
        emits a matching ``<id>`` anchor, a same-document ``:ref:`` -- which
        ``depart_reference`` renders as ``link(<_sanitize_label(id)>, ...)`` --
        dangles, and ``typst.compile()`` aborts the ENTIRE document at the
        semantic label-resolution pass with ``label ... does not exist``.

        Mirrors the proven target-anchor form (``visit_target``, bug #2) and the
        desc-signature anchor (bug #17): a zero-content markup block that carries
        the label and joins cleanly as its own statement in the surrounding
        code-mode block. The surrounding newlines separate it from any adjacent
        code-mode expression on both sides (a bare code-mode ``label("id")``
        would juxtapose/fail to join). Every id is routed through
        ``_sanitize_label`` (bug #10) so the anchor name byte-matches the
        reference side. Ids are globally unique per document (docutils
        ``make_id``), so no label is defined twice; dedupe defensively.

        A node with NO ids emits nothing -- byte-for-byte unchanged output, so
        every existing anchorless-body-element expectation is preserved. Inside
        a list item the same leading-separator / needs-separator machinery the
        surrounding block visitors use is driven here, so the anchor and the
        element's own emission stay newline-separated (never ``]par(`` /
        ``]list(`` juxtaposition, never a stranded ``+``).

        ``skip_ids`` lets a caller that ALREADY anchors one of the node's ids
        by another mechanism suppress a duplicate definition here. The sole
        user is ``depart_figure``: a captioned figure self-anchors ``ids[0]``
        inside its own ``[#figure(...) <label>]`` markup block, but a
        PROPAGATED explicit target lands a DIFFERENT id in ``ids[1:]`` that
        would otherwise dangle -- so the figure passes ``skip_ids={ids[0]}`` to
        anchor only the propagated remainder. When every id is skipped the
        method is a no-op (list-item bookkeeping is untouched), keeping output
        byte-for-byte identical.

        Args:
            node: The body-element node whose ``ids`` should be anchored.
            skip_ids: Raw docutils ids to NOT anchor here (already anchored by
                the caller). Defaults to anchoring every id.
        """
        ids = node.get("ids") or []
        if not ids:
            return
        skip = skip_ids or set()
        docname = self._current_docname()
        seen: set[str] = set()
        pending: list[str] = []
        for node_id in ids:
            if node_id in skip:
                continue
            label_id = self._namespace_label(docname, node_id)
            if label_id in seen:
                continue
            seen.add(label_id)
            pending.append(label_id)
        if not pending:
            return
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        for label_id in pending:
            self.add_text(f"\n[#metadata(none) <{label_id}>]\n")
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_document(self, node: nodes.document) -> None:
        """
        Visit a document node.

        Generates opening code block wrapper for unified code mode.

        Also builds the FN-01 footnote pre-pass index (D-01): a
        `{docutils-id: footnote-node}` dict built via
        `self.document.findall(nodes.footnote)` BEFORE any body content is
        visited, because footnote *definitions* are frequently positioned
        AFTER their citing footnote_references in source order (e.g. under
        a trailing `.. rubric:: Footnotes` -- see 14-RESEARCH.md "Verified
        Mechanism 2" finding 5). Uses `self.document`, not the `node`
        argument, per 14-RESEARCH.md Pitfall 4. `findall()` is used instead
        of D-01's literal `traverse()` wording -- `Node.traverse()` is
        deprecated in this repo's pinned docutils and raises under the
        project's strict `error::DeprecationWarning` pytest filter
        (pyproject.toml); `findall()` is its direct, non-deprecated
        replacement with identical semantics for this call. Deviation
        Rule 1 (auto-fixed bug). `self._emitted_footnote_ids` tracks which
        ids have already emitted their definition form (D-03).

        Args:
            node: The document node
        """
        self._footnote_index = {
            n["ids"][0]: n
            for n in self.document.findall(nodes.footnote)
            if n.get("ids")
        }
        self._emitted_footnote_ids: set = set()

        # Start code block for unified code mode (all content uses function syntax without # prefix)
        self.add_text("#{\n")

    def depart_document(self, node: nodes.document) -> None:
        """
        Depart a document node.

        Generates closing code block wrapper for unified code mode.

        Args:
            node: The document node
        """
        # Close code block for unified code mode
        self.add_text("}\n")

    def visit_section(self, node: nodes.section) -> None:
        """
        Visit a section node.

        Args:
            node: The section node
        """
        # Increment section level
        self.section_level += 1

    def depart_section(self, node: nodes.section) -> None:
        """
        Depart a section node.

        Args:
            node: The section node
        """
        # Decrement section level
        self.section_level -= 1
        # Add a newline after sections
        self.add_text("\n")

    def visit_title(self, node: nodes.title) -> None:
        """
        Visit a title node.

        Generates heading() function call with level parameter.
        Child text nodes will be wrapped in text() automatically.

        Exception: Inside an admonition or a topic (D-02), the title is not
        a section heading -- buffer its rendered inline content (via the
        standard inline visitors) so it can be attached as a code-block
        title argument at depart time instead of emitted here (see
        _depart_admonition). A `.. contents::` topic (D-05) additionally
        records the insertion point for its box-less bold label.

        Args:
            node: The title node
        """
        # Pitfall-1 fix: a title's own children (Text, emphasis, strong,
        # ...) currently concatenate with NO separator, because a title's
        # child-stream sets neither in_paragraph nor in_list_item. Treat
        # this title's own children like list_item content -- mirrors the
        # exact idiom visit_emphasis/visit_strong already use for their own
        # children ("treat it like list_item"). Restored in depart_title on
        # EVERY return path below.
        self._title_was_in_list_item = self.in_list_item
        self._title_was_list_item_needs_separator = self.list_item_needs_separator
        self.in_list_item = True
        self.list_item_needs_separator = False

        # D-02: admonition titles AND topic titles are deferred via
        # buffer-swap -- nodes.topic is NOT a subclass of nodes.Admonition,
        # so this is a literal additive `or`, never an MRO trick. The
        # existing Admonition path body is untouched; only more parent
        # types now enter it.
        if isinstance(node.parent, nodes.Admonition) or isinstance(
            node.parent, nodes.topic
        ):
            # D-05: a `.. contents::` topic's title must be inserted BEFORE
            # the already-streaming bullet_list, not appended after (the
            # list is the topic's second child and streams to self.body
            # before depart_title/depart_topic run) -- record the insertion
            # point now, since nothing has been emitted for this topic yet
            # (title is always a topic's first child).
            if isinstance(node.parent, nodes.topic) and "contents" in (
                node.parent.get("classes", []) or []
            ):
                self._contents_title_insert_at = len(self.body)
            self._saved_body_for_admonition_title = self.body
            self.body = []
            self._in_admonition_title = True
            return

        # Sections always carry docutils-assigned ids (auto-slugged from the
        # title, or merged in from a preceding explicit `.. _label:` target)
        # -- internal cross-references (e.g. a figure's internal `:target:`,
        # FIG-02/D-03) resolve to these ids via refid and require a matching
        # Typst anchor to exist, or the compile aborts with "label does not
        # exist" (Issue #114 GATE-01 discovery). Typst's `<label>` anchor
        # syntax is only valid as a markup-mode postfix, so -- exactly like
        # visit_figure's bracket-wrap fix -- bracket-wrap the heading() call
        # in markup content when the parent section has ids.
        self._title_section_ids = (
            node.parent.get("ids") if isinstance(node.parent, nodes.section) else None
        ) or []
        # D-06: clamp to a minimum of level 1 -- a top-level titled
        # non-section (section_level == 0) would otherwise emit
        # heading(level: 0, ...), which Typst rejects (levels are >= 1).
        emitted_level = max(1, self.section_level)
        # Pitfall-1 fix: wrap the title content in a code block {...} so
        # multi-child title content is one expression, not several
        # juxtaposed statements (mirrors _depart_admonition's existing
        # {...} wrap of the buffered admonition title).
        if self._title_section_ids:
            self.add_text(f"[#heading(level: {emitted_level}, {{")
        else:
            # Use heading() function (no # prefix in code mode)
            self.add_text(f"heading(level: {emitted_level}, {{")

    def depart_title(self, node: nodes.title) -> None:
        """
        Depart a title node.

        Closes heading() function call.

        Exception: Inside an admonition or topic, capture the buffered
        inline content as the pending title and restore the main output
        stream. A `.. contents::` topic (D-05) inserts its buffered title
        as a bold label ahead of its already-streamed bullet_list instead
        of consuming it as a box title argument.

        Args:
            node: The title node
        """
        if self._in_admonition_title:
            self._pending_admonition_title = "".join(self.body)
            if self._saved_body_for_admonition_title is not None:
                self.body = self._saved_body_for_admonition_title
            self._saved_body_for_admonition_title = None
            self._in_admonition_title = False
            self.in_list_item = self._title_was_in_list_item
            self.list_item_needs_separator = self._title_was_list_item_needs_separator

            if hasattr(self, "_contents_title_insert_at"):
                # D-05: insert (not append) the bold label at the recorded
                # index so it lands ABOVE the already-streamed bullet_list.
                label = f"strong({{{self._pending_admonition_title}}})\n\n"
                self.body.insert(self._contents_title_insert_at, label)
                self._pending_admonition_title = None
                del self._contents_title_insert_at
            return

        if self._title_section_ids:
            # Close the heading() call, attach the first id as the markup
            # anchor, and close the markup bracket opened in visit_title.
            # Typst only accepts one <label> per content element, so any
            # additional ids (e.g. both an auto-slugged name and a merged-in
            # explicit target name) get a zero-width metadata(none) anchor
            # each, pointing at the same document location.
            docname = self._current_docname()
            primary_id, *extra_ids = self._title_section_ids
            self.add_text(f"}}) <{self._namespace_label(docname, primary_id)}>]\n")
            for extra_id in extra_ids:
                self.add_text(
                    f"[#metadata(none) <{self._namespace_label(docname, extra_id)}>]\n"
                )
            self.add_text("\n")
        else:
            # Close heading() function
            self.add_text("})\n\n")
        self._title_section_ids = []
        self.in_list_item = self._title_was_in_list_item
        self.list_item_needs_separator = self._title_was_list_item_needs_separator

    def visit_subtitle(self, node: nodes.subtitle) -> None:
        """
        Visit a subtitle node.

        Generates emph() function for subtitle (no # prefix in code mode).
        Child text nodes will be wrapped in text() automatically.

        Args:
            node: The subtitle node
        """
        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Use emph() function for subtitle (no # prefix in code mode)
        self.add_text("emph(")

        # Store state to restore in depart
        self._subtitle_was_in_paragraph = was_in_paragraph

    def depart_subtitle(self, node: nodes.subtitle) -> None:
        """
        Depart a subtitle node.

        Closes emph() function.

        Args:
            node: The subtitle node
        """
        # Close emph() function
        self.add_text(")\n\n")

        # Restore paragraph state
        if hasattr(self, "_subtitle_was_in_paragraph"):
            self.in_paragraph = self._subtitle_was_in_paragraph
            delattr(self, "_subtitle_was_in_paragraph")

    def visit_compound(self, node: nodes.compound) -> None:
        """
        Visit a compound node.

        Compound nodes are containers that group related content.
        They are often used to wrap toctree directives.

        Args:
            node: The compound node
        """
        # A propagated explicit target (``.. _t:`` before a ``.. toctree::``,
        # which docutils wraps in a ``compound``) lands its id here; anchor it
        # so a same-document link(<id>, ...) resolves. A plain toctree compound
        # carries no ids -> no-op, byte-unchanged.
        self._emit_id_anchors(node)

    def depart_compound(self, node: nodes.compound) -> None:
        """
        Depart a compound node.

        Args:
            node: The compound node
        """
        pass

    def visit_container(self, node: nodes.container) -> None:
        """
        Visit a container node.

        Handle Sphinx-generated containers, particularly literal-block-wrapper
        for captioned code blocks (Issue #20).

        Args:
            node: The container node
        """
        # A referenceable target lands its id on the container: either an
        # explicit ``:name:`` on a captioned code block (the id sits on the
        # outer ``literal-block-wrapper`` container, NOT the inner
        # literal_block) or a propagated ``.. _t:`` before a
        # ``.. container::``. Anchor it so a same-document link(<id>, ...)
        # resolves. Guarded on ``names`` so the AUTO id docutils assigns to
        # every captioned code block for numref (ids present, names absent,
        # never referenced) is NOT anchored -- keeping the common
        # captioned-block output byte-for-byte unchanged.
        if node.get("names"):
            self._emit_id_anchors(node)
        # Check if this is a literal-block-wrapper (captioned code block)
        if "literal-block-wrapper" in node.get("classes", []):
            self.in_captioned_code_block = True
            # Caption and literal_block children will be processed separately
            # We need to extract caption text first
            for child in node.children:
                if isinstance(child, nodes.caption):
                    self.code_block_caption = child.astext()
                elif isinstance(child, nodes.literal_block):
                    # Extract label from :name: option
                    if child.get("names"):
                        self.code_block_label = child.get("names")[0]
        # Other container types: just process children
        pass

    def depart_container(self, node: nodes.container) -> None:
        """
        Depart a container node.

        Args:
            node: The container node
        """
        # Reset state after literal-block-wrapper
        if "literal-block-wrapper" in node.get("classes", []):
            self.in_captioned_code_block = False
            self.code_block_caption = ""
            self.code_block_label = ""

    def visit_paragraph(self, node: nodes.paragraph) -> None:
        """
        Visit a paragraph node.

        Wraps paragraph content in par() function for unified code mode.
        Code mode doesn't auto-recognize paragraph breaks from blank lines.

        Exception: Inside list items, paragraphs are not wrapped in par()
        to avoid syntax like "- par(text(...))" which is invalid.

        Args:
            node: The paragraph node
        """
        # A propagated explicit target (docutils PropagateTargets) moves its id
        # onto the FOLLOWING paragraph's node["ids"]; emit the matching Typst
        # anchor(s) so a same-document link(<id>, ...) resolves. No ids -> no-op
        # (byte-unchanged). Emitted at paragraph block level -- before the par()
        # wrap and outside any inline concat context -- so it never juxtaposes
        # or strands a `+`. (GATE-02 corpus fatal #20: <xref-modifiers>.)
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
        """
        Depart a paragraph node.

        Closes par({}) function and adds spacing.

        Args:
            node: The paragraph node
        """
        # Skip closing if inside list items
        if self.in_list_item:
            return

        # Close par({}) content block and add spacing
        self.in_paragraph = False
        self.paragraph_has_content = False
        self.add_text("})\n\n")

    def visit_comment(self, node: nodes.comment) -> None:
        """
        Visit a comment node.

        Comments are skipped entirely in Typst output as they are meant
        for source-level documentation only.

        Args:
            node: The comment node

        Raises:
            nodes.SkipNode: Always raised to skip the comment
        """
        raise nodes.SkipNode

    def depart_comment(self, node: nodes.comment) -> None:
        """
        Depart a comment node.

        Args:
            node: The comment node

        Note:
            This method is not called when SkipNode is raised in visit_comment.
        """
        pass

    def visit_substitution_definition(
        self, node: nodes.substitution_definition
    ) -> None:
        """
        Visit a substitution_definition node.

        Non-rendering; content injected at use sites (substitution_reference,
        resolved by a docutils transform before the writer runs) -- matches
        docutils/Sphinx's HTML and LaTeX writers, which also skip this node.
        Without a handler, the node falls through to unknown_visit (warns but
        does not skip), letting its inline children leak out as juxtaposed
        top-level expressions.

        Args:
            node: The substitution_definition node

        Raises:
            nodes.SkipNode: Always raised to skip the definition and its
                children (the definition itself produces no output)
        """
        raise nodes.SkipNode

    def visit_raw(self, node: nodes.raw) -> None:
        """
        Visit a raw node.

        Pass through content if format is 'typst', otherwise skip.

        Args:
            node: The raw node

        Raises:
            nodes.SkipNode: When format is not 'typst'
        """
        format_name = node.get("format", "").lower()

        if format_name == "typst":
            # Output the raw Typst content directly
            content = node.astext()
            if content:  # Only add non-empty content
                self.add_text(content)
                self.add_text("\n\n")
            raise nodes.SkipNode
        else:
            # Skip content for other formats
            logger.debug(f"Skipping raw node with format: {format_name}")
            raise nodes.SkipNode

    def depart_raw(self, node: nodes.raw) -> None:
        """
        Depart a raw node.

        Args:
            node: The raw node

        Note:
            This method is not called when SkipNode is raised in visit_raw.
        """
        pass

    # ------------------------------------------------------------------
    # Code-mode inline concatenation (single source of truth)
    #
    # A def-list term (the code-mode 1st arg of terms.item), a link body (the
    # 2nd arg of link()), and a desc parameter list are all Typst code-mode
    # positions where two juxtaposed expressions are a syntax error
    # ("expected comma"). Adjacent inline sibling expressions in any of these
    # contexts must therefore be joined with " + ". The helpers below are the
    # ONE place that decides "which concat context is active" and "is this the
    # first sibling or a following one", so every inline visitor -- the leaf
    # visit_Text / visit_literal AND the block-opening visit_emphasis /
    # visit_strong / visit_reference -- participates uniformly.
    # ------------------------------------------------------------------

    #: Code-mode concat contexts as (active-flag, has-content-flag) attribute
    #: names, highest precedence first (mirrors the historical elif chain in
    #: visit_Text: desc parameter > link > term).
    _CONCAT_CONTEXTS: Tuple[Tuple[str, str], ...] = (
        ("in_desc_parameter", "_desc_parameter_has_content"),
        ("_in_link", "_link_has_content"),
        ("_in_term", "_term_has_content"),
        ("_in_field_body", "_field_body_has_content"),
        ("_in_attribution", "_attribution_has_content"),
    )

    def _inline_concat_context(self) -> Tuple[str, str] | None:
        """
        Return the ``(active-flag, has-content-flag)`` attribute-name pair of
        the currently active code-mode concat context (def-list term / link
        body / desc parameter), highest precedence first, or ``None`` when no
        such context is active.
        """
        for flag, has_content in self._CONCAT_CONTEXTS:
            if getattr(self, flag, False):
                return (flag, has_content)
        return None

    def _emit_inline_concat_separator(self) -> bool:
        """
        Emit ``" + "`` before the next inline expression when the active
        code-mode concat context already holds an earlier sibling.

        Returns ``True`` when a concat context is active (so the caller skips
        the list-item newline separator), ``False`` otherwise.
        """
        ctx = self._inline_concat_context()
        if ctx is None:
            return False
        if getattr(self, ctx[1]):
            self.add_text(" + ")
        return True

    def _mark_inline_concat_content(self) -> bool:
        """
        Record that the active concat context now holds a sibling expression,
        so the next inline expression is ``" + "`` separated.

        Returns ``True`` when a concat context is active, ``False`` otherwise.
        """
        ctx = self._inline_concat_context()
        if ctx is None:
            return False
        setattr(self, ctx[1], True)
        return True

    def _enter_inline_concat_element(self) -> bool:
        """
        Begin an inline element that opens its OWN block/argument (emphasis,
        strong, reference) and may be a direct sibling in a code-mode concat
        context.

        Emit the ``" + "`` separator when this element follows an earlier
        sibling, then SUPPRESS the outer concat context for the duration of the
        element's own content: inside the element the children are a fresh
        context (markup content for emph/strong, the link body for a
        reference), where re-applying the outer ``+`` would leak a stray
        operator, e.g. ``strong({ + text(...)})``. Always pushes onto
        ``_inline_concat_stack`` so it pairs 1:1 with
        :meth:`_exit_inline_concat_element` in the matching ``depart_*``.

        Returns ``True`` when a concat context was active (so the caller skips
        the list-item newline separator), ``False`` otherwise.
        """
        ctx = self._inline_concat_context()
        self._inline_concat_stack.append(ctx)
        if ctx is None:
            return False
        if getattr(self, ctx[1]):
            self.add_text(" + ")
        # Suppress the outer concat context inside this element's own content.
        setattr(self, ctx[0], False)
        return True

    def _exit_inline_concat_element(self) -> None:
        """
        Close an inline element opened by :meth:`_enter_inline_concat_element`:
        restore the suppressed outer concat context and record that this
        element is now a sibling expression, so the NEXT sibling is ``" + "``
        separated.
        """
        ctx = self._inline_concat_stack.pop()
        if ctx is None:
            return
        setattr(self, ctx[0], True)  # un-suppress the outer context flag
        setattr(self, ctx[1], True)  # this element = a sibling for the next one

    def visit_Text(self, node: nodes.Text) -> None:
        """
        Visit a text node.

        Wraps text in text() function for unified code mode.
        Uses string escaping (not markup escaping).

        Exception: Inside literal blocks, text is output directly
        without text() wrapping to preserve code content.

        Args:
            node: The text node
        """
        text_content = node.astext()

        # Inside literal blocks, output text directly (no wrapping)
        if self.in_literal_block:
            self.add_text(text_content)
            return

        # Escape string content via the shared helper (order-safe, full set)
        text_content = escape_typst_string(text_content)

        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Add separator before text.
        # In a code-mode concat context (def-list term / link body / desc
        # parameter): use the + operator between adjacent inline expressions.
        # In list items: use a newline separator. In paragraphs: handled by
        # _add_paragraph_separator above.
        if not self._emit_inline_concat_separator():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Wrap in text() function (# prefix needed in markup mode)
        self.add_text(f'{prefix}text("{text_content}")')

        # Mark that content was added (so the next sibling is + / newline
        # separated).
        if not self._mark_inline_concat_content():
            if self.in_list_item:
                self.list_item_needs_separator = True

    def depart_Text(self, node: nodes.Text) -> None:
        """
        Depart a text node.

        Args:
            node: The text node
        """
        # Text nodes don't need closing
        pass

    def visit_emphasis(self, node: nodes.emphasis) -> None:
        """
        Visit an emphasis (italic) node.

        Generates emph() function call. Child text nodes will be
        wrapped in text() automatically.

        Args:
            node: The emphasis node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # If this emphasis is a sibling in a code-mode concat context (def-list
        # term / link body / desc parameter), + separate it and suppress that
        # context for the emph body (content mode, where an outer '+' would
        # leak). Otherwise fall back to the list-item newline separator.
        if not self._enter_inline_concat_element():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Save and reset list item separator for children (they're inside this element)
        was_list_item_needs_separator = self.list_item_needs_separator

        # Since emph({}) uses content block, treat it like list_item
        # Children need newline separators, not + operators
        was_in_list_item = self.in_list_item
        self.in_list_item = True
        self.list_item_needs_separator = False

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Use emph({}) function with content block
        self.add_text(f"{prefix}emph({{")

        # Store state to restore in depart
        self._emph_was_in_paragraph = was_in_paragraph
        self._emph_was_in_list_item = was_in_list_item
        self._emph_was_list_item_needs_separator = was_list_item_needs_separator

    def depart_emphasis(self, node: nodes.emphasis) -> None:
        """
        Depart an emphasis (italic) node.

        Closes emph({}) function call.

        Args:
            node: The emphasis node
        """
        # Close emph({}) function
        self.add_text("})")

        # Restore paragraph state
        if hasattr(self, "_emph_was_in_paragraph"):
            self.in_paragraph = self._emph_was_in_paragraph
            delattr(self, "_emph_was_in_paragraph")

        # Restore in_list_item state
        if hasattr(self, "_emph_was_in_list_item"):
            self.in_list_item = self._emph_was_in_list_item
            delattr(self, "_emph_was_in_list_item")

        # Restore and mark that next element needs separator
        if hasattr(self, "_emph_was_list_item_needs_separator"):
            # Restore previous state, then mark next element needs separator
            if self.in_list_item:
                self.list_item_needs_separator = True
            delattr(self, "_emph_was_list_item_needs_separator")

        # Restore the code-mode concat context suppressed for the emph body and
        # mark this emphasis as a sibling so the next term/link/desc expression
        # is + separated.
        self._exit_inline_concat_element()

    def visit_strong(self, node: nodes.strong) -> None:
        """
        Visit a strong (bold) node.

        Generates strong() function call. Child text nodes will be
        wrapped in text() automatically.

        Args:
            node: The strong node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # If this strong is a sibling in a code-mode concat context (def-list
        # term / link body / desc parameter), + separate it and suppress that
        # context for the strong body (content mode, where an outer '+' would
        # leak). Otherwise fall back to the list-item newline separator.
        if not self._enter_inline_concat_element():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Save and reset list item separator for children (they're inside this element)
        was_list_item_needs_separator = self.list_item_needs_separator

        # Since strong({}) uses content block, treat it like list_item
        # Children need newline separators, not + operators
        was_in_list_item = self.in_list_item
        self.in_list_item = True
        self.list_item_needs_separator = False

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Use strong({}) function with content block
        self.add_text(f"{prefix}strong({{")

        # Store state to restore in depart
        self._strong_was_in_paragraph = was_in_paragraph
        self._strong_was_in_list_item = was_in_list_item
        self._strong_was_list_item_needs_separator = was_list_item_needs_separator

    def depart_strong(self, node: nodes.strong) -> None:
        """
        Depart a strong (bold) node.

        Closes strong({}) function call.

        Args:
            node: The strong node
        """
        # Close strong({}) function
        self.add_text("})")

        # Restore paragraph state
        if hasattr(self, "_strong_was_in_paragraph"):
            self.in_paragraph = self._strong_was_in_paragraph
            delattr(self, "_strong_was_in_paragraph")

        # Restore in_list_item state
        if hasattr(self, "_strong_was_in_list_item"):
            self.in_list_item = self._strong_was_in_list_item
            delattr(self, "_strong_was_in_list_item")

        # Restore and mark that next element needs separator
        if hasattr(self, "_strong_was_list_item_needs_separator"):
            # Restore previous state, then mark next element needs separator
            if self.in_list_item:
                self.list_item_needs_separator = True
            delattr(self, "_strong_was_list_item_needs_separator")

        # Restore the code-mode concat context suppressed for the strong body
        # and mark this strong as a sibling so the next term/link/desc
        # expression is + separated.
        self._exit_inline_concat_element()

    def visit_literal(self, node: nodes.literal) -> None:
        """
        Visit a literal (inline code) node.

        Generates raw() function call with backtick raw string.
        Uses backticks to avoid escaping issues.

        Args:
            node: The literal node
        """
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

        # Get code content directly
        code_content = node.astext()

        # Escape code content for string parameter via the shared helper.
        # Must escape newline/CR/tab too (not just backslash+quote): an inline
        # literal whose source wraps across lines carries an embedded newline,
        # which would otherwise break the single-line Typst "..." string literal
        # ("expected semicolon or line break").
        escaped_code = escape_typst_string(code_content)

        # Generate raw() function with string parameter (no # prefix in code mode)
        # Using string instead of backtick raw literal for compatibility with + operator
        self.add_text(f'raw("{escaped_code}")')

        # Mark that content was added / next element needs a separator
        if not self._mark_inline_concat_content():
            if self.in_list_item:
                self.list_item_needs_separator = True

        # Skip processing child text nodes (we already got the content)
        raise nodes.SkipNode

    def depart_literal(self, node: nodes.literal) -> None:
        """
        Depart a literal (inline code) node.

        This is not called when SkipNode is raised in visit_literal.

        Args:
            node: The literal node
        """
        pass

    def visit_subscript(self, node: nodes.subscript) -> None:
        """
        Visit a subscript node.

        Generates sub() function call. Child text nodes will be
        wrapped in text() automatically.

        Args:
            node: The subscript node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Use sub() function (no # prefix in code mode)
        self.add_text("sub(")

        # Store state to restore in depart
        self._subscript_was_in_paragraph = was_in_paragraph

    def depart_subscript(self, node: nodes.subscript) -> None:
        """
        Depart a subscript node.

        Closes sub() function call.

        Args:
            node: The subscript node
        """
        # Close sub() function
        self.add_text(")")

        # Restore paragraph state
        if hasattr(self, "_subscript_was_in_paragraph"):
            self.in_paragraph = self._subscript_was_in_paragraph
            delattr(self, "_subscript_was_in_paragraph")

    def visit_superscript(self, node: nodes.superscript) -> None:
        """
        Visit a superscript node.

        Generates super() function call. Child text nodes will be
        wrapped in text() automatically.

        Args:
            node: The superscript node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Use super() function (no # prefix in code mode)
        self.add_text("super(")

        # Store state to restore in depart
        self._superscript_was_in_paragraph = was_in_paragraph

    def depart_superscript(self, node: nodes.superscript) -> None:
        """
        Depart a superscript node.

        Closes super() function call.

        Args:
            node: The superscript node
        """
        # Close super() function
        self.add_text(")")

        # Restore paragraph state
        if hasattr(self, "_superscript_was_in_paragraph"):
            self.in_paragraph = self._superscript_was_in_paragraph
            delattr(self, "_superscript_was_in_paragraph")

    def visit_bullet_list(self, node: nodes.bullet_list) -> None:
        """
        Visit a bullet list node.

        Outputs list( and prepares for stream-based item rendering.

        Args:
            node: The bullet list node
        """
        # A propagated explicit target can land its id on this list; anchor it
        # so a same-document link(<id>, ...) resolves (no ids -> no-op).
        self._emit_id_anchors(node)

        # Add + separator if nested in a list item
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        self.list_stack.append("bullet")
        self.add_text("list(")

        # Save parent list state and start fresh for nested list
        if len(self.list_stack) > 1:  # Nested list
            self._saved_is_first_list_item = self.is_first_list_item
            self._saved_list_item_needs_separator = self.list_item_needs_separator

        self.is_first_list_item = True

        # Mark that next element in parent list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

    def depart_bullet_list(self, node: nodes.bullet_list) -> None:
        """
        Depart a bullet list node.

        Closes the list() function.

        Args:
            node: The bullet list node
        """
        self.list_stack.pop()
        self.add_text(")")

        # Restore parent list state if nested
        if hasattr(self, "_saved_is_first_list_item"):
            self.is_first_list_item = self._saved_is_first_list_item
            delattr(self, "_saved_is_first_list_item")
        if hasattr(self, "_saved_list_item_needs_separator"):
            self.list_item_needs_separator = self._saved_list_item_needs_separator
            delattr(self, "_saved_list_item_needs_separator")

        # Add newlines only if this is a top-level list
        if not self.list_stack:
            self.add_text("\n\n")

    def visit_enumerated_list(self, node: nodes.enumerated_list) -> None:
        """
        Visit an enumerated (numbered) list node.

        Outputs enum( and prepares for stream-based item rendering.

        Args:
            node: The enumerated list node
        """
        # A propagated explicit target can land its id on this list; anchor it
        # so a same-document link(<id>, ...) resolves (no ids -> no-op).
        self._emit_id_anchors(node)

        # Add + separator if nested in a list item
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        self.list_stack.append("enumerated")
        self.add_text("enum(")

        # Save parent list state and start fresh for nested list
        if len(self.list_stack) > 1:  # Nested list
            self._saved_is_first_list_item = self.is_first_list_item
            self._saved_list_item_needs_separator = self.list_item_needs_separator

        self.is_first_list_item = True

        # Mark that next element in parent list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

    def depart_enumerated_list(self, node: nodes.enumerated_list) -> None:
        """
        Depart an enumerated (numbered) list node.

        Closes the enum() function.

        Args:
            node: The enumerated list node
        """
        self.list_stack.pop()
        self.add_text(")")

        # Restore parent list state if nested
        if hasattr(self, "_saved_is_first_list_item"):
            self.is_first_list_item = self._saved_is_first_list_item
            delattr(self, "_saved_is_first_list_item")
        if hasattr(self, "_saved_list_item_needs_separator"):
            self.list_item_needs_separator = self._saved_list_item_needs_separator
            delattr(self, "_saved_list_item_needs_separator")

        # Add newlines only if this is a top-level list
        if not self.list_stack:
            self.add_text("\n\n")

    def visit_list_item(self, node: nodes.list_item) -> None:
        """
        Visit a list item node.

        Adds comma separator if not first item, then prepares for item content.

        Args:
            node: The list item node
        """
        # Mark that we're in a list item (disable par() wrapping).
        # Push the prior value so a nested list's depart_list_item restores
        # the OUTER item's context instead of clobbering it to False.
        self._list_item_stack.append(self.in_list_item)
        self.in_list_item = True

        # Add comma before 2nd+ items
        if not self.is_first_list_item:
            self.add_text(", ")
        self.is_first_list_item = False

        # Wrap list item content in { } block
        # This allows multiple statements without + operator
        self.add_text("{\n")

        # Reset separator flag for item content
        self.list_item_needs_separator = False

        # A propagated explicit target (``.. _t:`` placed BETWEEN list items)
        # lands its id on the FOLLOWING list_item node -- not the bullet_list
        # (whose own ids are anchored in visit_bullet_list/visit_enumerated_list)
        # and not the item's inner paragraph. Anchor it here, inside the item's
        # ``{ }`` block, so a same-document link(<id>, ...) resolves. No ids ->
        # no-op; the helper drives the in-list-item separator machinery so the
        # anchor and the item's first content element stay newline-separated.
        self._emit_id_anchors(node)

    def depart_list_item(self, node: nodes.list_item) -> None:
        """
        Depart a list item node.

        Close the { } block wrapper and mark that we're no longer in a list item.

        Args:
            node: The list item node
        """
        # Close the { } block
        self.add_text("\n}")

        # Restore the prior context: after a nested list item closes we are
        # still inside the OUTER list item (True), while a top-level item
        # restores to False. This keeps the existing list_item_needs_separator
        # machinery driving newline separators for any block that follows a
        # nested list (list->par, list->list, ...), fixing the `})par(` class.
        if self._list_item_stack:
            self.in_list_item = self._list_item_stack.pop()
        else:
            self.in_list_item = False

    def visit_literal_block(self, node: nodes.literal_block) -> None:
        """
        Visit a literal block (code block) node.

        Implements Task 4.2.2: codly forced usage with #codly-range() for highlighted lines
        Design 3.5: All code blocks use codly, with #codly-range() for highlights
        Requirements 7.3, 7.4: Support line numbers and highlighted lines
        Issue #20: Support :linenos:, :caption:, and :name: options
        Issue #31: Support :lineno-start: and :dedent: options

        Args:
            node: The literal block node
        """
        # Anchor node["ids"] via the shared markup-block helper. Both a
        # ``:name:`` and a propagated ``.. _t:`` before the block set
        # node["ids"] (and names) on the literal_block; the reference side
        # resolves to the sanitized ID, so anchoring ids -- not names -- is
        # what a link(<id>, ...) needs. This REPLACES the old
        # depart_literal_block ` <label>` postfix (removed below): a bare
        # ` <label>` after a code-mode raw block does not join ("cannot join
        # content with label"), and it anchored the NAME, which diverges from
        # the id whenever the name contains characters docutils rewrites (e.g.
        # a space). Captioned ``:name:`` blocks carry the id on the outer
        # literal-block-wrapper CONTAINER (handled in visit_container), so the
        # inner literal_block has no ids there -> no-op, no double-define. A
        # plain code block has no ids -> no-op, byte-unchanged.
        self._emit_id_anchors(node)

        # Add newline separator if in list item and not first element
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Mark that we're in a literal block (disable text() wrapping)
        self.in_literal_block = True

        # Issue #20: Handle captioned code blocks
        # If we're in a captioned code block (literal-block-wrapper container),
        # wrap the code block in figure() (no # prefix in code mode)
        if self.in_captioned_code_block and self.code_block_caption:
            # Escape special characters in caption
            escaped_caption = self.code_block_caption
            # Start figure with caption (will add closing bracket in depart)
            # No # prefix in code mode
            self.add_text(f"figure(caption: [{escaped_caption}])[\n")

        # If in list item, wrap codly() calls and code block in { } to make it an expression
        if self.in_list_item:
            self.add_text("{\n")

        # Check for :linenos: option (Issue #20)
        # If linenos is not set or False, disable line numbers in codly
        linenos = node.get("linenos", False)
        if not linenos:
            # No # prefix in code mode
            self.add_text("codly(number-format: none)\n")

        # Extract highlight_args if present (Task 4.2.2)
        highlight_args = node.get("highlight_args", {})
        hl_lines = highlight_args.get("hl_lines", [])

        # Issue #31: Support :lineno-start: option
        # Sphinx stores lineno-start in highlight_args['linenostart']. Note
        # that Sphinx's LiteralInclude directive ALWAYS populates
        # linenostart (defaulting to 1) even without an explicit
        # :lineno-start: option (see LiteralIncludeReader.__init__), so the
        # `!= 1` guard below is required to avoid a spurious codly() call
        # for the common "plain :linenos:" case.
        #
        # codly's @preview 1.3.0 codly() function has no `start` parameter
        # -- it accepts `offset` (int), an ADDITIVE delta applied as
        # `line.number + offset` where `line.number` is the raw block's
        # 1-indexed line number (see codly/1.3.0/src/lib.typ). To make the
        # first displayed line number equal Sphinx's `linenostart`, the
        # offset must be `linenostart - 1` (offset=0 is codly's default,
        # matching linenostart=1).
        lineno_start = highlight_args.get("linenostart")
        if linenos and lineno_start is not None and lineno_start != 1:
            # No # prefix in code mode
            self.add_text(f"codly(offset: {lineno_start - 1})\n")

        # Generate codly-range() if highlight lines are specified
        if hl_lines:
            # Convert list of line numbers to Typst array format
            # Example: [2, 3] -> codly-range(highlight: (2, 3))
            # Example: [2, 4, 5, 6] -> codly-range(highlight: (2, 4, 5, 6))
            highlight_str = ", ".join(str(line) for line in hl_lines)
            # No # prefix in code mode
            self.add_text(f"codly-range(highlight: ({highlight_str}))\n")

        # Typst code block syntax: ```language\ncode\n```
        # Extract language if specified
        language = node.get("language", "")
        if language:
            self.add_text(f"```{language}\n")
        else:
            self.add_text("```\n")

    def depart_literal_block(self, node: nodes.literal_block) -> None:
        """
        Depart a literal block (code block) node.

        Issue #20: Handle closing figure bracket and labels.

        Args:
            node: The literal block node
        """
        # Clear literal block flag
        self.in_literal_block = False

        # Close code block
        self.add_text("\n```\n")

        # Close the { } wrapper if we're in a list item
        if self.in_list_item:
            self.add_text("}")

        # Issue #20: Close figure wrapper if we're in a captioned code block
        if self.in_captioned_code_block and self.code_block_caption:
            # Close the figure's trailing content block with ]
            self.add_text("]")
            # Add label if present
            if self.code_block_label:
                self.add_text(
                    f" <{self._namespace_label(self._current_docname(), self.code_block_label)}>"
                )
            self.add_text("\n\n")
        else:
            # Normal code block - just add spacing. Any :name:/propagated-target
            # id is anchored by _emit_id_anchors in visit_literal_block (the old
            # ` <label>` postfix here failed to join a code-mode raw block with
            # a label and anchored the name instead of the id).
            self.add_text("\n")

        # Mark that next element in list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_definition_list(self, node: nodes.definition_list) -> None:
        """
        Visit a definition list node.

        Collects all term-definition pairs and generates terms() function
        in unified code mode.

        Args:
            node: The definition list node
        """
        # A propagated explicit target can land its id on this definition list;
        # anchor it so a same-document link(<id>, ...) resolves (no ids ->
        # no-op). Emitted here while self.body is still the real body -- before
        # visit_term/visit_definition redirect it to buffers.
        self._emit_id_anchors(node)

        # A def-list nested in a list item, following a sibling paragraph/block,
        # must be newline-separated from it: its terms(...) is emitted (in
        # depart) directly into the outer list item's code-mode content block,
        # where abutting the preceding statement (e.g. text("...")terms(...))
        # is a Typst syntax error ("expected semicolon or line break", GATE-02
        # fatal #8, configuration.typ:2009). Mirror the standard block-visitor
        # list-item separator (literal_block/bullet_list/...). Emitted here
        # (not depart) while self.body is still the real body -- visit_term/
        # visit_definition redirect self.body to buffers in between.
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
            self.list_item_needs_separator = False
        self.in_definition_list = True
        # Push a fresh item collection for THIS list and alias
        # definition_list_items to it, so a definition list nested inside one of
        # this list's definitions collects into its own frame (bug #18).
        self._deflist_items_stack.append([])
        self.definition_list_items = self._deflist_items_stack[-1]

    def depart_definition_list(self, node: nodes.definition_list) -> None:
        """
        Depart a definition list node.

        Generates terms() function with all collected term-definition pairs.

        Args:
            node: The definition list node
        """
        # Pop THIS list's item collection and restore the enclosing list's
        # frame (or reset to empty at the top level). in_definition_list stays
        # True while an enclosing definition list is still open, so a nested
        # list's depart does not prematurely clear the outer state (bug #18).
        items = self._deflist_items_stack.pop()
        if self._deflist_items_stack:
            self.definition_list_items = self._deflist_items_stack[-1]
            self.in_definition_list = True
        else:
            self.definition_list_items = []
            self.in_definition_list = False

        # Generate terms() function with all items (no # prefix in code mode).
        # The DEFINITION (2nd arg) is wrapped in a `{ ... }` content block: a
        # definition may hold several block-level children (a paragraph, then a
        # code fence, then a list), which depart_definition assembles as bare,
        # blank-line-separated statements. Blank-line separation of sequential
        # content is valid only at document top level; as a bare function
        # argument Typst reads the first statement (e.g. par({...})) as the
        # WHOLE argument and then expects a comma at the next statement
        # (codly(...)/a fence/list({...})) -> "expected comma" (GATE-02 fatal
        # #7, directives.typ:1718 + ~16 corpus files). Inside `{ }` Typst
        # auto-joins the statements into one content value -- a valid single
        # argument. The TERM (1st arg) keeps its own +-concat assembly (D-03/
        # bug #3/#5) untouched; we wrap only the definition arg.
        if items:
            items_str = ", ".join(
                f"terms.item({term}, {self._wrap_definition_arg(definition)})"
                for term, definition in items
            )
            self.add_text(f"terms({items_str})\n\n")
        else:
            self.add_text("terms()\n\n")

        # A following sibling in the same list item must newline-separate from
        # this terms(...) statement.
        if self.in_list_item:
            self.list_item_needs_separator = True

    @staticmethod
    def _is_single_content_block(text: str) -> bool:
        """
        Return True if ``text`` is exactly one balanced ``{ ... }`` content
        block (its opening brace matches the final character), ignoring braces
        inside Typst double-quoted string literals.

        Used by :meth:`_wrap_definition_arg` to avoid double-wrapping a
        definition buffer that is already a single content value. No current
        translator emission produces such a buffer (definition children all
        start with a function name or a backtick fence), so this is a defensive
        guard, but it keeps the wrap idempotent.

        Args:
            text: The assembled definition buffer.

        Returns:
            True if ``text`` is a single ``{...}`` content block.
        """
        if len(text) < 2 or text[0] != "{" or text[-1] != "}":
            return False
        depth = 0
        in_string = False
        escaped = False
        for i, ch in enumerate(text):
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                # A close returning to depth 0 before the last char means the
                # buffer holds more than one top-level block -> must wrap.
                if depth == 0 and i != len(text) - 1:
                    return False
        return depth == 0

    def _wrap_definition_arg(self, definition: str) -> str:
        """
        Wrap a definition buffer so it is a single valid ``terms.item`` 2nd
        argument.

        A definition with multiple block-level children is assembled as bare,
        blank-line-separated statements, which are only valid at document top
        level. Enclosing them in a ``{ ... }`` content block makes Typst
        auto-join them into one content value. A single-block definition (a
        lone ``par({...})``) wraps to ``{par({...})}`` and renders identically.
        An empty definition becomes ``{}`` (valid empty content). Already
        single-``{...}`` buffers are returned unchanged to avoid double-wrapping.

        Args:
            definition: The assembled definition buffer.

        Returns:
            The definition as a single ``{ ... }``-wrapped argument.
        """
        if not definition:
            return "{}"
        if self._is_single_content_block(definition):
            return definition
        return f"{{{definition}}}"

    def visit_definition_list_item(self, node: nodes.definition_list_item) -> None:
        """
        Visit a definition list item node.

        Args:
            node: The definition list item node
        """
        # Definition list items don't need special markup
        pass

    def depart_definition_list_item(self, node: nodes.definition_list_item) -> None:
        """
        Depart a definition list item node.

        Args:
            node: The definition list item node
        """
        # Definition list items don't need closing
        pass

    def visit_term(self, node: nodes.term) -> None:
        """
        Visit a term (definition list term) node.

        Starts buffering term content.

        Args:
            node: The term node
        """
        # Start buffering term content. Push the current body onto the stack
        # (not a single saved_body slot) so a definition list nested inside this
        # list's definition restores its own level without orphaning this one
        # (bug #18).
        self._saved_body_stack.append(self.body)
        self.current_term_buffer = []
        self.body = self.current_term_buffer

        # Enter term concat context: adjacent inline expressions in the buffer
        # are + concatenated (the buffer becomes the code-mode 1st arg of
        # terms.item, where juxtaposition is a Typst syntax error).
        self._in_term = True
        self._term_has_content = False

    def depart_term(self, node: nodes.term) -> None:
        """
        Depart a term (definition list term) node.

        Saves buffered term content. If the term carries a docutils-assigned
        id (e.g. a `.. glossary::` entry), emits a Typst `<label>` anchor via
        the bracket-wrap markup form so a same-document `:term:` reference's
        `link(<term-id>, ...)` (visit_reference's refid branch, D-03) has a
        resolvable target instead of aborting the compile with "label does
        not exist" (XREF-01, D-04). Mirrors the visit_title/depart_title
        bracket-wrap anchor pattern (Phase 11) -- never `+`-join a bare
        `label(...)` onto content, which raises `TypstError: cannot add
        content and label`.

        Args:
            node: The term node
        """
        # Exit term concat context.
        self._in_term = False
        self._term_has_content = False

        # Get buffered term content
        if isinstance(self.current_term_buffer, list):
            term_content = "".join(self.current_term_buffer).strip()
        else:
            term_content = ""

        # Restore the body saved on entry (stack pop, not single slot).
        self.body = self._saved_body_stack.pop()

        if node.get("ids"):
            label_id = self._namespace_label(self._current_docname(), node["ids"][0])
            term_content = f"[#{{{term_content}}} <{label_id}>]"

        # Store term for later (will be paired with definition)
        self.current_term_buffer = term_content

    def visit_definition(self, node: nodes.definition) -> None:
        """
        Visit a definition (definition list definition) node.

        Starts buffering definition content.

        Args:
            node: The definition node
        """
        # Start buffering definition content. Push the current body AND capture
        # the pending term string: a definition list nested inside this
        # definition would otherwise overwrite the single saved_body /
        # current_term_buffer slots, dropping THIS definition's content and its
        # term when it departs (bug #18). The term was set to a str by
        # depart_term; anything else means no term to pair.
        self._saved_body_stack.append(self.body)
        self._pending_term_stack.append(
            self.current_term_buffer
            if isinstance(self.current_term_buffer, str)
            else None
        )
        self.current_definition_buffer = []
        self.body = self.current_definition_buffer

    def depart_definition(self, node: nodes.definition) -> None:
        """
        Depart a definition (definition list definition) node.

        Saves buffered definition content and pairs it with the term.

        Args:
            node: The definition node
        """
        # Read THIS definition's buffered content from self.body. Balanced
        # nested visit/depart pairs restore self.body to this definition's own
        # buffer, so it holds the full content (leading paragraph + any nested
        # terms(...)); the current_definition_buffer slot may have been
        # reassigned/None'd by a nested definition and can no longer be trusted
        # (bug #18).
        definition_content = "".join(self.body).strip()

        # Restore the body saved on entry (stack pop, not single slot).
        self.body = self._saved_body_stack.pop()

        # Pair the pending term (captured on entry, before any nested list could
        # clobber current_term_buffer) with this definition's content.
        term = self._pending_term_stack.pop()
        if term is not None:
            self.definition_list_items.append((term, definition_content))

        self.current_term_buffer = None
        self.current_definition_buffer = None

    def visit_figure(self, node: nodes.figure) -> None:
        """
        Visit a figure node.

        Generates figure() function call (no # prefix in code mode), unless
        docutils has assigned the figure an id -- which happens
        automatically whenever a figure carries a caption, for numref/
        cross-reference support, regardless of whether the user gave an
        explicit `:name:` -- in which case the call is bracket-wrapped in
        markup content (`[#figure(...) <label>]`). Typst's `<label>` anchor
        syntax is only valid as a markup-mode postfix; attaching it to a
        bare code-mode statement inside this translator's unified `#{ ... }`
        code-mode document wrapper is a Typst parse error ("expected
        semicolon or line break") that aborts the whole compile -- a real
        fatal bug discovered by Phase 11's GATE-01 real-compile acceptance
        gate (Issue #114), affecting every captioned figure, not just the
        FIG-01/FIG-02 cases that phase otherwise targets.

        Args:
            node: The figure node
        """
        self.in_figure = True
        self.figure_content = []  # Store figure content (image)
        self.figure_caption = ""  # Store caption text

        if node.get("ids"):
            self.add_text("[#figure(\n")
        else:
            # Start figure with potential label (no # prefix in code mode)
            self.add_text("figure(\n")

    def depart_figure(self, node: nodes.figure) -> None:
        """
        Depart a figure node.

        Args:
            node: The figure node
        """
        # Close the figure. The buffered caption holds rendered code-mode
        # output (text(...)/emph(...) calls produced by the buffer-swap in
        # depart_caption), so it must be wrapped in a {...} code block to be
        # evaluated -- not [...] markup, which would print the calls
        # literally instead of evaluating them.
        if self.figure_caption:
            self.add_text(f",\n  caption: {{{self.figure_caption}}}")

        # Add label if figure has ids. The trailing `]` closes the markup
        # bracket opened in visit_figure -- see that method's docstring for
        # why the label must live inside a markup-mode bracket pair.
        if node.get("ids"):
            label = self._namespace_label(self._current_docname(), node["ids"][0])
            self.add_text(f"\n) <{label}>]\n\n")
        else:
            self.add_text("\n)\n\n")

        # A captioned figure self-anchors ONLY ids[0] (its own caption/numref
        # id) in the ``) <label>]`` postfix above. A PROPAGATED explicit target
        # (``.. _t:`` before ``.. figure::``) lands a DIFFERENT id in ids[1:]
        # that would otherwise dangle -- anchor the remainder, skipping ids[0]
        # so it is not defined twice. Empty/single-id figures -> no-op.
        self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))

        self.in_figure = False
        self.figure_content = []
        self.figure_caption = ""

    def visit_caption(self, node: nodes.caption) -> None:
        """
        Visit a caption node.

        Handles captions for both figures and code blocks (Issue #20).

        Args:
            node: The caption node
        """
        # For captioned code blocks, caption is already extracted in visit_container
        # We should skip output to avoid duplicate caption text
        if self.in_captioned_code_block:
            raise nodes.SkipNode
        # For figures, buffer-swap the body so the caption's inline children
        # render through the normal visitor chain (preserving emphasis/literal/etc.
        # and routing text through visit_Text's string-literal escaping) instead
        # of being re-derived later via node.astext() (mirrors the admonition-title
        # buffer-swap idiom; see visit_title/depart_title).
        if self.in_figure:
            self._saved_body_for_figure_caption = self.body
            self.body = []
            # A figure caption is a paragraph of inline content that
            # depart_figure renders into a `{...}` code block. Establish the
            # paragraph separator context so adjacent inline expressions
            # (text/emphasis/the reference-with-target markup wrapper/...) are
            # newline-separated via _add_paragraph_separator -- exactly as in a
            # real paragraph, which already renders these correctly. Without
            # it every inline sibling juxtaposes inside the code block
            # (`text(...)[wrapper]text(...)`, `text(...)emph(...)`), a Typst
            # parse error ("expected semicolon or line break"). Save/restore
            # for nesting safety.
            self._caption_was_in_paragraph = self.in_paragraph
            self._caption_was_paragraph_has_content = self.paragraph_has_content
            self.in_paragraph = True
            self.paragraph_has_content = False
        # For figures, start collecting caption text
        self.in_caption = True

    def depart_caption(self, node: nodes.caption) -> None:
        """
        Depart a caption node.

        Args:
            node: The caption node
        """
        # Capture the buffered caption content and restore the main output
        # stream (buffer-swap idiom; never node.astext(), which bypasses the
        # escaping applied by the normal visitor chain and caused the
        # double-emission/juxtaposition fatal bug).
        if self.in_figure:
            self.figure_caption = "".join(self.body)
            if self._saved_body_for_figure_caption is not None:
                self.body = self._saved_body_for_figure_caption
            self._saved_body_for_figure_caption = None
            # Restore the paragraph separator context saved in visit_caption.
            self.in_paragraph = self._caption_was_in_paragraph
            self.paragraph_has_content = self._caption_was_paragraph_has_content
        self.in_caption = False

    def visit_footnote(self, node: nodes.footnote) -> None:
        """
        Visit a footnote definition node (D-05).

        Emits nothing at the definition's natural (docutils) location -- the
        body is reached only via the D-01 pre-pass index (visit_document)
        plus the D-02 lazy render performed by visit_footnote_reference at
        the citing site. A defined-but-never-referenced footnote is
        therefore silently dropped (D-09), which is the intended behavior.

        No depart_footnote is defined: SkipNode guarantees it never fires.

        Args:
            node: The footnote definition node
        """
        raise nodes.SkipNode

    def visit_footnote_reference(self, node: nodes.footnote_reference) -> None:
        """
        Visit a footnote_reference node (D-02/D-03/D-04/D-06/D-08).

        The FIRST reference to a given id renders the footnote body lazily
        via the buffer-swap idiom (never node.astext() -- mirrors
        depart_caption above), skipping the footnote node's leading `label`
        child (D-06), and emits the bracket-wrapped, label-attached
        definition form `[#footnote({body}) <fn-id>]`. The bracket-wrap is
        required because Typst's `<label>` attachment postfix is markup-mode
        syntax and is a parse error as a bare statement inside this
        translator's unified `#{ ... }` code-mode wrapper (mirrors
        visit_figure's `[#figure(...) <label>]`; 14-RESEARCH.md Verified
        Mechanism 1).

        Every REPEAT reference to an already-emitted id emits the bare reuse
        form `footnote(<fn-id>)` -- no bracket-wrap, since `<label>` used as
        a plain call ARGUMENT is a code-mode Label value, not markup-mode
        attachment syntax (14-RESEARCH.md Verified Mechanism 1, finding 1).
        Typst's native footnote() auto-numbering owns numbering entirely
        (D-04); no docutils number/symbol is ever forced.

        A dangling refid (not present in the D-01 index) logs a
        logger.warning naming the refid and skips emitting anything --
        emitting a footnote(<missing-label>) call for a label that was
        never attached is a FATAL Typst compile abort ("label `<..>` does
        not exist in the document"), not a cosmetic issue (14-RESEARCH.md
        Pitfall 1); this guard is load-bearing and must run before any
        emission. `citation`/`citation_reference` are untouched (D-07).

        The footnote_reference node's own child (docutils' rendered marker
        number, e.g. "1"/"2") is never rendered -- Typst supplies its own
        marker via footnote()'s auto-numbering.

        No depart_footnote_reference is defined: SkipNode guarantees it
        never fires.

        Args:
            node: The footnote_reference node
        """
        refid = node.get("refid")
        footnote_node = self._footnote_index.get(refid)

        if footnote_node is None:
            logger.warning(
                "Dangling footnote reference: refid=%r not found in document",
                refid,
            )
            raise nodes.SkipNode

        # Namespace + sanitize here at the single derivation point so BOTH the
        # reuse-ref (footnote(<label>)) and the definition
        # ([#footnote(...) <label>]) branches below emit the identical,
        # Typst-valid, per-document-unique label name. Footnote definition and
        # reference are always in the SAME document, so the current docname
        # namespaces both consistently.
        label = self._namespace_label(self._current_docname(), f"fn-{refid}")

        # Statement-separator convention every other inline child already
        # uses (visit_emphasis/visit_strong/visit_literal all open this way).
        self._add_paragraph_separator()
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        if refid in self._emitted_footnote_ids:
            # D-03 reuse branch: a bare code-mode call, no bracket-wrap --
            # <label> as a function ARGUMENT is a plain code-mode Label
            # value (unlike the definition form's label-ATTACHMENT postfix).
            self.add_text(f"footnote(<{label}>)")
        else:
            # D-03 definition branch: bracket-wrap for the <label>
            # attachment postfix (Phase 11 precedent). Body sourced via
            # buffer-swap through the normal visitor chain (D-02), never
            # node.astext() -- skip only the footnote node's leading
            # `label` child by position (D-06/14-RESEARCH.md Pitfall 3).
            self._emitted_footnote_ids.add(refid)
            saved_body = self.body
            self.body = []
            # Save/restore in_paragraph + paragraph_has_content around the
            # nested walkabout (established convention: visit_emphasis/
            # visit_strong/visit_subscript/visit_superscript all do this
            # identically). Without this, the footnote body's own
            # `paragraph` child unconditionally resets both flags to
            # False/False on depart -- silently clobbering the OUTER
            # paragraph's separator state and dropping the "\n" statement
            # separator the next sibling (e.g. a trailing ".") needs,
            # which is a FATAL "expected semicolon or line break" Typst
            # compile abort (14-RESEARCH.md Pitfall 1 / t8), not a
            # cosmetic issue. Discovered via the GATE-01 real-compile
            # fixture (Rule 1 auto-fix).
            was_in_paragraph = self.in_paragraph
            was_paragraph_has_content = self.paragraph_has_content
            self.in_paragraph = False
            for child in footnote_node.children[1:]:
                child.walkabout(self)
            body_content = "".join(self.body)
            self.body = saved_body
            self.in_paragraph = was_in_paragraph
            self.paragraph_has_content = was_paragraph_has_content
            self.add_text(f"[#footnote({{{body_content}}}) <{label}>]")

        if self.in_list_item:
            self.list_item_needs_separator = True

        # D-06: the footnote_reference's OWN child (docutils' rendered
        # marker Text, e.g. "1"/"2") must never render.
        raise nodes.SkipNode

    def visit_table(self, node: nodes.table) -> None:
        """
        Visit a table node.

        Args:
            node: The table node
        """
        # A propagated explicit target can land its id on this table; anchor it
        # so a same-document link(<id>, ...) resolves (no ids -> no-op). Emitted
        # while self.in_table is still False, so add_text routes to the real
        # body (not a stale table_cell_content buffer).
        self._emit_id_anchors(node)

        # Emit a leading newline separator when this table follows a
        # sibling inside a list item, matching the block-visitor pattern
        # established in bug #4 (bullet_list/literal_block/definition_list/
        # block_quote/field_list). Otherwise depart_table's table( juxtaposes
        # against the preceding inline expression in the list-item content
        # block -- e.g. `text("Text styling commands:")table(` -- a Typst
        # parse error ("expected semicolon or line break"). table was the
        # one block visitor omitted from that fix. Use self.body.append
        # directly (NOT self.add_text) -- self.in_table is set True below,
        # and add_text() would misroute this newline into a stale
        # table_cell_content list left over from a PRIOR table on this
        # translator instance (same pitfall depart_table's table( emission
        # already avoids -- see the comment there).
        if self.in_list_item and self.list_item_needs_separator:
            self.body.append("\n")
            self.list_item_needs_separator = False

        self.in_table = True
        self.table_cells = []  # Store cells for table generation
        self.table_colcount = 0  # Track number of columns

    def _format_table_cell(self, cell: dict, indent: str = "  ") -> str:
        """
        Format a table cell with optional colspan/rowspan.

        Args:
            cell: Cell dictionary with 'content', 'colspan', 'rowspan'
            indent: Indentation string

        Returns:
            Formatted Typst cell string
        """
        content = cell["content"]
        colspan = cell.get("colspan", 1)
        rowspan = cell.get("rowspan", 1)

        # Normal cell (no spanning)
        if colspan == 1 and rowspan == 1:
            return f"{indent}{{{content}}},\n"

        # Cell with spanning - use table.cell()
        params = []
        if colspan > 1:
            params.append(f"colspan: {colspan}")
        if rowspan > 1:
            params.append(f"rowspan: {rowspan}")

        params_str = ", ".join(params)
        return f"{indent}table.cell({{{content}}}, {params_str}),\n"

    def depart_table(self, node: nodes.table) -> None:
        """
        Depart a table node.

        Args:
            node: The table node
        """
        # Generate Typst table() syntax (no # prefix in unified code mode)
        if self.table_colcount > 0:
            # Use self.body.append directly to avoid routing to table_cell_content
            self.body.append(f"table(\n  columns: {self.table_colcount},\n")

            # Separate header cells from body cells
            header_cells = [cell for cell in self.table_cells if cell.get("is_header")]
            body_cells = [
                cell for cell in self.table_cells if not cell.get("is_header")
            ]

            # Add header cells with table.header() wrapper
            if header_cells:
                self.body.append("  table.header(\n")
                for cell in header_cells:
                    self.body.append(self._format_table_cell(cell, indent="    "))
                self.body.append("  ),\n")

            # Add body cells
            for cell in body_cells:
                self.body.append(self._format_table_cell(cell, indent="  "))

            self.body.append(")\n\n")

        self.in_table = False
        self.table_cells = []
        self.table_colcount = 0

        # Mark that a following sibling in the same list item must be
        # separated (block-visitor pattern, bug #4).
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_tgroup(self, node: nodes.tgroup) -> None:
        """
        Visit a tgroup (table group) node.

        Args:
            node: The tgroup node
        """
        # Get column count from tgroup
        self.table_colcount = node.get("cols", 0)

    def depart_tgroup(self, node: nodes.tgroup) -> None:
        """
        Depart a tgroup (table group) node.

        Args:
            node: The tgroup node
        """
        pass

    def visit_colspec(self, node: nodes.colspec) -> None:
        """
        Visit a colspec (column specification) node.

        Args:
            node: The colspec node
        """
        # Column specifications are handled by tgroup
        raise nodes.SkipNode

    def depart_colspec(self, node: nodes.colspec) -> None:
        """
        Depart a colspec (column specification) node.

        Args:
            node: The colspec node
        """
        pass

    def visit_thead(self, node: nodes.thead) -> None:
        """
        Visit a thead (table header) node.

        Args:
            node: The thead node
        """
        # Mark that we're in the header section
        self.in_thead = True

    def depart_thead(self, node: nodes.thead) -> None:
        """
        Depart a thead (table header) node.

        Args:
            node: The thead node
        """
        # Mark that we're no longer in the header section
        self.in_thead = False

    def visit_tbody(self, node: nodes.tbody) -> None:
        """
        Visit a tbody (table body) node.

        Args:
            node: The tbody node
        """
        pass

    def depart_tbody(self, node: nodes.tbody) -> None:
        """
        Depart a tbody (table body) node.

        Args:
            node: The tbody node
        """
        pass

    def visit_row(self, node: nodes.row) -> None:
        """
        Visit a row (table row) node.

        Args:
            node: The row node
        """
        # Rows are processed by collecting entries
        pass

    def depart_row(self, node: nodes.row) -> None:
        """
        Depart a row (table row) node.

        Args:
            node: The row node
        """
        pass

    def visit_entry(self, node: nodes.entry) -> None:
        """
        Visit an entry (table cell) node.

        Args:
            node: The entry node
        """
        # Start collecting cell content
        self.table_cell_content = []

        # Read cell spanning attributes
        # morecols: number of additional columns (0 = normal cell)
        # morerows: number of additional rows (0 = normal cell)
        self.current_morecols = node.get("morecols", 0)
        self.current_morerows = node.get("morerows", 0)

    def depart_entry(self, node: nodes.entry) -> None:
        """
        Depart an entry (table cell) node.

        Args:
            node: The entry node
        """
        # Get cell content and add to table cells
        # Extract text from the accumulated body content since visit_entry
        cell_text = ""
        if hasattr(self, "table_cell_content") and self.table_cell_content:
            cell_text = "".join(self.table_cell_content).strip()

        if not cell_text:
            # If no content was captured, try to get text from the node
            cell_text = node.astext().strip()

        # Calculate colspan and rowspan from morecols/morerows
        # morecols=1 means 2 columns total (1 + 1 additional)
        colspan = self.current_morecols + 1
        rowspan = self.current_morerows + 1

        # Store cell with header/body distinction and spanning info
        self.table_cells.append(
            {
                "content": cell_text,
                "is_header": self.in_thead,
                "colspan": colspan,
                "rowspan": rowspan,
            }
        )
        self.table_cell_content = []

    def visit_block_quote(self, node: nodes.block_quote) -> None:
        """
        Visit a block quote node.

        Generates quote() function call (no # prefix in code mode).

        Args:
            node: The block quote node
        """
        # A propagated explicit target can land its id on this block quote;
        # anchor it so a same-document link(<id>, ...) resolves (no ids -> no-op).
        self._emit_id_anchors(node)

        # Emit a leading newline separator when this block quote follows a
        # sibling inside a list item, matching the block-visitor pattern
        # established in bug #4 (bullet_list/literal_block/definition_list).
        # Otherwise `quote[`/`quote(` juxtaposes against the preceding inline
        # expression in the list-item content block -- e.g.
        # `text(" functions:")quote[` -- a Typst parse error ("expected
        # semicolon or line break"). block_quote was the one block visitor
        # omitted from that fix.
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Emit the block quote as a CODE-MODE body -- quote(block: true, { ... })
        # -- NOT the markup-mode trailing content block quote[ ... ] (bug #15).
        # Every body child is a code-mode function call (par({text(...)}),
        # raw(...), link(...)). Inside a markup `[...]` block those bytes are
        # treated as LITERAL PROSE, so any markup-special char in a child
        # string literal -- e.g. the lone `_` in raw("_t") (Sphinx's `_t`
        # static-template suffix) -- opened a stray inline-emphasis span that
        # never closed -> "TypstError: unclosed delimiter". The `{ ... }`
        # content block evaluates the children as real function calls (the same
        # code-mode content-block wrapping used by par()/definition (bug #7)),
        # so their string-literal chars are inert. block: true keeps block
        # quotes rendering as block quotes. The attribution, when present,
        # closes this body block and is appended as a code-mode named argument
        # (see visit_attribution) -- so the opening is identical in both cases.
        self.add_text("quote(block: true, {")

    def depart_block_quote(self, node: nodes.block_quote) -> None:
        """
        Depart a block quote node.

        Args:
            node: The block quote node
        """
        # Check if there's an attribution child node. When present,
        # visit_attribution already closed the body `{` and opened the named
        # `attribution: {` argument, and depart_attribution closed that `}`;
        # so here we only close the quote() call. Otherwise we close both the
        # body block and the call.
        has_attribution = any(isinstance(child, nodes.attribution) for child in node)

        if has_attribution:
            self.add_text(")\n\n")
        else:
            self.add_text("})\n\n")

        # Mark that a following sibling in the same list item must be separated
        # (block-visitor pattern, bug #4).
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_attribution(self, node: nodes.attribution) -> None:
        """
        Visit an attribution node (quote attribution).

        Args:
            node: The attribution node
        """
        # Close the code-mode quote body block and open the attribution as a
        # named argument -- quote(block: true, { <body> }, attribution: {
        # <attr> }) -- a form Typst accepts (positional then named).
        #
        # The attribution value is a CODE-MODE `{ ... }` content block, NOT a
        # markup-mode `[ ... ]` block (mirroring the code-mode quote body,
        # bug #15). An attribution's inline children are emitted through the
        # code-mode visitors (visit_Text -> `text("...")`, visit_emphasis ->
        # `emph({...})`, visit_literal -> `raw("...")`, visit_reference ->
        # `link(...)`), each a bare (un-`#`-prefixed) function call. Inside a
        # markup `[...]` argument those bytes are LITERAL PROSE, so Typst
        # typesets them verbatim -- the author name renders as `text(“Author”)`
        # (curly quotes from smart-quote typography) instead of `Author`, and
        # a lone markup-special char in a child string literal (e.g. the `_` in
        # an inline literal ``_t``) opens a stray unclosed emphasis span that
        # aborts the compile. A `{ ... }` code block EVALUATES the children as
        # real content. Activating the _in_attribution concat context makes the
        # inline children + separated (`emph({...}) + text(...) + raw(...)`),
        # since attribution holds inline children directly (no wrapping
        # paragraph) that would otherwise juxtapose into a syntax error.
        self.add_text("}, attribution: {")
        self._in_attribution = True
        self._attribution_has_content = False

    def depart_attribution(self, node: nodes.attribution) -> None:
        """
        Depart an attribution node.

        Args:
            node: The attribution node
        """
        # Close the code-mode attribution content block and exit the concat
        # context. depart_block_quote closes the enclosing quote() call.
        self._in_attribution = False
        self.add_text("}")

    def visit_image(self, node: nodes.image) -> None:
        """
        Visit an image node.

        Generates image() function call (no # prefix in code mode).
        Adjusts image paths for nested documents (Issue #69).

        Args:
            node: The image node
        """
        # A propagated explicit target can land its id on a standalone (block)
        # image; anchor it so a same-document link(<id>, ...) resolves (no ids
        # -> no-op). Skipped inside a figure: the figure node owns the caption
        # id and emits its own `[#figure(...) <label>]` anchor, and an image
        # nested in a figure never carries a propagated block target.
        if not self.in_figure:
            self._emit_id_anchors(node)

        uri = node.get("uri", "")

        # Get current document name for path adjustment (Issue #69)
        current_docname = getattr(self.builder, "current_docname", None)

        # Adjust path based on output file location (Issue #69)
        adjusted_uri = self._compute_relative_image_path(uri, current_docname)

        # Add proper indentation if inside a figure
        if self.in_figure:
            self.add_text(f'  image("{adjusted_uri}"')
        else:
            # No # prefix in code mode
            self.add_text(f'image("{adjusted_uri}"')

        # Add optional attributes. Length values from docutils (:width:/:height:)
        # may use CSS units Typst does not understand (e.g. raw "px"), which
        # would abort the whole compile (Issue #114, FIG-01). Convert via
        # _convert_length_to_typst and drop the dimension entirely when the
        # unit is unsupported (D-02) -- never emit a raw unconverted unit.
        if "width" in node:
            converted_width = self._convert_length_to_typst(node["width"])
            if converted_width is not None:
                self.add_text(f", width: {converted_width}")

        if "height" in node:
            converted_height = self._convert_length_to_typst(node["height"])
            if converted_height is not None:
                self.add_text(f", height: {converted_height}")

        self.add_text(")")

    def depart_image(self, node: nodes.image) -> None:
        """
        Depart an image node.

        Args:
            node: The image node
        """
        # If inside a figure, don't add extra newlines (figure will handle spacing)
        if not self.in_figure:
            self.add_text("\n\n")

    def visit_target(self, node: nodes.target) -> None:
        """
        Visit a target node (label definition).

        Args:
            node: The target node
        """
        # Check if we're in a markup mode wrapper started by reference
        if (
            hasattr(self, "_in_reference_with_target")
            and self._in_reference_with_target
        ):
            # Re-enable markup mode for label output (was disabled for link content)
            self._in_markup_mode = True
            # Output label in markup mode (with # prefix in markup mode)
            if node.get("ids"):
                label_id = self._namespace_label(
                    self._current_docname(), node["ids"][0]
                )
                self.add_text(f'\n#label("{label_id}")')
            # Close the markup block
            self.add_text("]")
            # Clear the flags
            self._in_reference_with_target = False
            self._in_markup_mode = False  # Exit markup mode
            # Mark separator needed for next element
            if self.in_list_item:
                self.list_item_needs_separator = True
            # Skip processing children as target is typically empty
            raise nodes.SkipNode

        # Original behavior for non-markup-wrapped targets
        # Add newline separator if in list item and not first element
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Generate a Typst anchor if the target has ids.
        #
        # Emit the anchor as a metadata-carrying markup block --
        # `[#metadata(none) <id>]` -- exactly like the extra-id anchors in
        # visit_title/depart_title. A bare code-mode `label("id")` is WRONG in
        # two ways: (a) two adjacent targets emit `label("id1")label("id2")`
        # with no separator, a Typst syntax error ("expected semicolon or line
        # break"); and (b) even a single bare label is a raw label *value*, so
        # joining it into a content block fails ("cannot join content with
        # label"). A `[#metadata(none) <id>]` block is genuine *content* with
        # the label attached, so it joins/concatenates cleanly, works both
        # singly and consecutively, and stays reachable via link(<id>).
        #
        # The surrounding newlines separate this markup block from any adjacent
        # code-mode expression on BOTH sides -- a preceding one
        # (text()/raw()/par()/a prior target) and a following one (e.g. the next
        # `par({...})`) -- which is required inside a `{...}` content block where
        # juxtaposed expressions need a line break between them (`]par(` and
        # `)label(` are both syntax errors otherwise).
        if node.get("ids"):
            label_id = self._namespace_label(self._current_docname(), node["ids"][0])
            self.add_text(f"\n[#metadata(none) <{label_id}>]\n")

        # Mark that next element in list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

        # Skip processing children as target is typically empty
        raise nodes.SkipNode

    def depart_target(self, node: nodes.target) -> None:
        """
        Depart a target node.

        Args:
            node: The target node
        """
        # Target is handled in visit
        pass

    def visit_pending_xref(self, node: nodes.Node) -> None:
        """
        Visit a pending_xref node (Sphinx cross-reference).

        Args:
            node: The pending_xref node
        """
        # pending_xref nodes are typically resolved by Sphinx before reaching the writer
        # If we encounter one, it means resolution failed or we're in a special case
        # We handle it by generating a link to the target

        reftarget = node.get("reftarget", "")
        reftype = node.get("reftype", "")

        if reftarget:
            # Generate a link to the target
            # Sanitize the target for Typst label format. The legacy
            # `.`/`_`->`-` transform is kept for backward compatibility, then
            # routed through _sanitize_label so any remaining Typst-invalid
            # character (e.g. `@`) cannot abort the compile with an unclosed
            # label -- this pending_xref path is only a best-effort fallback
            # for references Sphinx failed to resolve.
            # Unresolved best-effort fallback: assume a same-document target and
            # namespace with the current docname so it matches a same-doc anchor
            # (all real anchors are now docname-namespaced).
            label = self._namespace_label(
                self._current_docname(),
                reftarget.replace(".", "-").replace("_", "-"),
            )
            self.add_text(f"#link(<{label}>)[")
        # Continue processing children to get the link text

    def depart_pending_xref(self, node: nodes.Node) -> None:
        """
        Depart a pending_xref node.

        Args:
            node: The pending_xref node
        """
        reftarget = node.get("reftarget", "")
        if reftarget:
            self.add_text("]")

    def _compute_relative_include_path(
        self, target_docname: str, current_docname: str | None
    ) -> str:
        """
        Compute relative path for toctree #include() directive.

        This method calculates the relative path from the current document
        to the target document for use in Typst #include() directives.
        Uses PurePosixPath for OS-independent POSIX path handling.

        Args:
            target_docname: Target document name (e.g., "chapter1/section1")
            current_docname: Current document name (e.g., "chapter1/index"), or None

        Returns:
            Relative path string for #include() (e.g., "section1" or "../chapter2/doc")

        Examples:
            >>> _compute_relative_include_path("chapter1/section1", "chapter1/index")
            "section1"
            >>> _compute_relative_include_path("chapter2/doc", "chapter1/index")
            "../chapter2/doc"
            >>> _compute_relative_include_path("chapter1/doc", None)
            "chapter1/doc"

        Notes:
            This method implements Issue #5 fix for nested toctree relative paths.
            It handles three cases:
            1. current_docname is None: return absolute path
            2. Same directory: use relative_to() directly
            3. Cross-directory: calculate via common parent

        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        from pathlib import PurePosixPath

        logger.debug(
            f"Computing relative include path: target={target_docname}, "
            f"current={current_docname}"
        )

        # Fallback to absolute path if current_docname is None
        if not current_docname:
            logger.debug(f"No current document, using absolute path: {target_docname}")
            return target_docname

        current_path = PurePosixPath(current_docname)
        target_path = PurePosixPath(target_docname)
        current_dir = current_path.parent

        logger.debug(
            f"Path components: current_dir={current_dir}, " f"target_path={target_path}"
        )

        # Root directory case: use absolute path (backward compatibility)
        if current_dir == PurePosixPath("."):
            logger.debug(
                f"Current document is in root directory, "
                f"using absolute path: {target_docname}"
            )
            return target_docname

        # Try to compute relative path
        try:
            rel_path = target_path.relative_to(current_dir)
            result = str(rel_path)
            logger.debug(
                f"Same directory reference: {current_dir} -> {target_path}, "
                f"result: {result}"
            )
            return result
        except ValueError:
            # Different directory trees - build path via common parent
            logger.debug(
                "Cross-directory reference detected, calculating via common parent"
            )

            current_parts = current_dir.parts
            target_parts = target_path.parts

            # Find common parent by comparing path components
            common_length = 0
            for i, (c, t) in enumerate(zip(current_parts, target_parts, strict=False)):
                if c == t:
                    common_length = i + 1
                else:
                    break

            logger.debug(
                f"Common parent depth: {common_length}, "
                f"current_parts={current_parts}, target_parts={target_parts}"
            )

            # Build path: "../" from current to common parent
            up_count = len(current_parts) - common_length
            up_path = "../" * up_count if up_count > 0 else ""

            # Build path: from common parent to target
            down_parts = target_parts[common_length:]
            down_path = "/".join(down_parts) if down_parts else ""

            relative_path: str = up_path + down_path

            logger.debug(
                f"Cross-directory path calculation: up_count={up_count}, "
                f"up_path='{up_path}', down_path='{down_path}', "
                f"result: {relative_path}"
            )

            return relative_path

    def _compute_relative_image_path(
        self, image_uri: str, current_docname: str | None
    ) -> str:
        """
        Compute relative path for image() function.

        Adjusts image URIs from source-root-relative to output-file-relative.
        This is similar to _compute_relative_include_path() but for images.

        Args:
            image_uri: Image URI from Sphinx (source-root-relative)
            current_docname: Current document name (e.g., "chapter1/section1")

        Returns:
            Adjusted relative path for Typst image()

        Examples:
            >>> _compute_relative_image_path("images/logo.png", "chapter1/section1")
            "../images/logo.png"
            >>> _compute_relative_image_path("images/logo.png", "index")
            "images/logo.png"
            >>> _compute_relative_image_path("images/logo.png", None)
            "images/logo.png"

        Notes:
            This implements Issue #69 fix for nested document image paths.
            Uses the same logic as _compute_relative_include_path() from Issue #5.
        """
        from pathlib import PurePosixPath

        logger.debug(
            f"Computing relative image path: uri={image_uri}, "
            f"current={current_docname}"
        )

        # Fallback to absolute path if current_docname is None
        if not current_docname:
            logger.debug(f"No current document, using absolute path: {image_uri}")
            return image_uri

        current_path = PurePosixPath(current_docname)
        image_path = PurePosixPath(image_uri)
        current_dir = current_path.parent

        logger.debug(
            f"Path components: current_dir={current_dir}, image_path={image_path}"
        )

        # Root directory case: use absolute path (backward compatibility)
        if current_dir == PurePosixPath("."):
            logger.debug(
                f"Current document is in root directory, "
                f"using absolute path: {image_uri}"
            )
            return image_uri

        # Try to compute relative path
        try:
            rel_path = image_path.relative_to(current_dir)
            result = str(rel_path)
            logger.debug(
                f"Same directory reference: {current_dir} -> {image_path}, "
                f"result: {result}"
            )
            return result
        except ValueError:
            # Different directory trees - build path via common parent
            logger.debug(
                "Cross-directory reference detected, calculating via common parent"
            )

            current_parts = current_dir.parts
            image_parts = image_path.parts

            # Find common parent by comparing path components
            common_length = 0
            for i, (c, img) in enumerate(zip(current_parts, image_parts, strict=False)):
                if c == img:
                    common_length = i + 1
                else:
                    break

            logger.debug(
                f"Common parent depth: {common_length}, "
                f"current_parts={current_parts}, image_parts={image_parts}"
            )

            # Build path: "../" from current to common parent
            up_count = len(current_parts) - common_length
            up_path = "../" * up_count if up_count > 0 else ""

            # Build path: from common parent to image
            down_parts = image_parts[common_length:]
            down_path = "/".join(down_parts) if down_parts else ""

            relative_path: str = up_path + down_path

            logger.debug(
                f"Cross-directory path calculation: up_count={up_count}, "
                f"up_path='{up_path}', down_path='{down_path}', "
                f"result: {relative_path}"
            )

            return relative_path

    @staticmethod
    def _sanitize_label(name: str) -> str:
        """
        Sanitize a docutils id/name into a valid Typst label token.

        Typst's ``<label>`` anchor syntax, its ``label("...")`` value, and the
        ``link(<label>, ...)`` reference form all accept only a restricted
        character set for the label NAME. Empirically (typst 0.15) the only
        characters valid inside a ``<...>`` label are ``[A-Za-z0-9_.:-]``;
        every other character (notably ``@``, but also ``/ + # * ? ! ~ % & =``
        whitespace, brackets, quotes, etc.) makes Typst fail to close the
        label with ``error: unclosed label``, which aborts the ENTIRE compile.

        Docutils/Sphinx ids can contain such characters. In particular
        Sphinx's C-domain anonymous entities (``@data`` / ``@alias``) produce
        ids like ``c.Data.@data.a`` -- the ``@`` is what triggered the corpus
        ``unclosed label`` fatal. This helper maps every character outside the
        valid set to a collision-resistant token ``_u{codepoint:x}_`` (e.g.
        ``@`` -> ``_u40_``). That encoding:

        - uses only characters valid in a Typst label (``_``, digits, letters),
          and is safe as a leading character (starts with ``_``);
        - is deterministic and injective on the offending character (distinct
          characters map to distinct codepoint tokens), so it is collision-
          resistant -- unlike replacing every invalid char with a bare ``_``,
          which would collide ``a@b`` with ``a?b``;
        - leaves ids that are ALREADY valid byte-for-byte unchanged, so the
          vast majority of existing anchors/links (which already compile) are
          not churned and keep their exact current names.

        CRITICAL CORRECTNESS PROPERTY: this must be applied at every site that
        emits a label NAME -- both where a label is DEFINED (anchors,
        ``label("...")``) and where it is REFERENCED (``link(<...>, ...)``,
        ``footnote(<...>)``) -- so a definition and its reference sanitize to
        the SAME string and cross-references keep resolving.

        Args:
            name: A docutils id/name (or a derived label such as ``fn-<id>``).

        Returns:
            The same string with every Typst-label-invalid character replaced
            by a ``_u{codepoint:x}_`` token.
        """
        return re.sub(
            r"[^A-Za-z0-9_.:-]",
            lambda m: f"_u{ord(m.group(0)):x}_",
            name,
        )

    def _current_docname(self) -> str | None:
        """Return the docname currently being written, or ``None``.

        The builder sets ``current_docname`` in ``write_doc`` before the
        translator runs. Hand-built test doctrees may have no builder docname;
        callers fall back to a bare (un-namespaced) label in that case.
        """
        return getattr(self.builder, "current_docname", None)

    def _namespace_label(self, docname: str | None, raw_id: str) -> str:
        """Namespace a docutils id/name by its owning document, then sanitize.

        The whole corpus is flattened into ONE Typst master via ``#include()``
        (each source doc becomes a ``.typ`` the master includes), but docutils
        ids are unique only WITHIN a document -- two different documents can
        carry the SAME section slug (e.g. ``info-field-lists``). Emitted as a
        bare ``<info-field-lists>`` twice, that is a duplicate Typst label, and
        the compile aborts at the semantic pass with ``label ... occurs
        multiple times`` as soon as anything references it.

        To keep every label unique per compiled master, every DEFINITION site
        (anchors, ``label("...")``, ``<label>`` postfixes, footnote labels)
        prefixes the SOURCE ``docname``; every REFERENCE site
        (``link(<...>, ...)``) recomputes the SAME namespace from its target's
        docname -- the current docname for a same-document reference, the
        TARGET docname (parsed from the cross-document refuri) for a
        cross-document reference -- so a link still lands on exactly the right
        anchor. Since the ``docname:id`` string is built identically on both
        sides and then run through the same ``_sanitize_label`` (docnames'
        ``/`` -> ``_u2f_``, ``:`` is label-valid and preserved), a definition
        and its reference always byte-match.

        A ``None`` docname (hand-built test doctrees with no builder docname)
        falls back to a bare sanitized label so those paths stay unchanged and
        internally consistent (every site sees the same ``None``).

        Args:
            docname: The owning document's name, or ``None``.
            raw_id: A docutils id/name (or a derived label such as ``fn-<id>``).

        Returns:
            A Typst-valid, per-document-unique label token.
        """
        if docname:
            return self._sanitize_label(f"{docname}:{raw_id}")
        return self._sanitize_label(raw_id)

    def _resolve_xref_docname(self, refuri: str) -> Tuple[str, str] | None:
        """Resolve a LOCAL cross-document refuri to ``(target_docname, anchor)``.

        Sphinx's reference resolver renders a resolved cross-document
        ``pending_xref`` as a ``reference`` whose refuri is
        ``<relative-path><out_suffix>#<anchor>`` (e.g.
        ``../domains/python.typ#info-field-lists`` relative to the current
        document's output path). This inverts that: it joins the relative path
        onto the current document's output URI, strips the builder's
        ``out_suffix``, and returns the target docname plus the anchor -- so the
        reference can be namespaced with the TARGET docname and thus match the
        anchor that target document emits.

        Returns ``None`` (leaving the caller to render a plain
        ``link("url", ...)``) for:

        - external URLs (any ``scheme://`` or ``mailto:`` / protocol-relative);
        - same-document ``#anchor`` refs (handled earlier by the caller);
        - whole-document refs with no ``#anchor`` (kept as a string-url link,
          per requirement -- there is no single anchor to target);
        - refuris whose path does not end in the builder's ``out_suffix``
          (arbitrary relative asset links), or when the current docname is
          unknown.
        """
        if "#" not in refuri:
            return None
        if "://" in refuri or refuri.startswith(("mailto:", "//")):
            return None
        path_part, _, anchor = refuri.partition("#")
        if not anchor or not path_part:
            return None
        suffix = getattr(self.builder, "out_suffix", "")
        if not suffix or not path_part.endswith(suffix):
            return None
        current = self._current_docname()
        if not current:
            return None
        import posixpath

        current_uri = self.builder.get_target_uri(current)
        base_dir = posixpath.dirname(current_uri)
        target_uri = posixpath.normpath(posixpath.join(base_dir, path_part))
        target_docname = target_uri[: -len(suffix)]
        return target_docname, anchor

    def _convert_length_to_typst(self, value: str) -> str | None:
        """
        Convert a docutils-normalized CSS length string to a Typst-valid length.

        Docutils' `length_or_percentage_or_unitless`/`length_or_unitless` option
        converters (see docutils/parsers/rst/directives/__init__.py) normalize
        `:width:`/`:height:` into a single "<value><unit>" string with no space
        (e.g. "200px", "50%", "300" for bare unitless). This helper rewrites
        that string into one Typst's length grammar accepts, or returns None if
        the unit cannot be represented (caller should then omit the attribute
        entirely, letting the image render at its natural size).

        Args:
            value: Docutils-normalized length string (e.g. "200px", "50%", "300").

        Returns:
            A Typst-valid length string, or None if the unit is unsupported.

        Examples:
            >>> _convert_length_to_typst("200px")
            "150pt"
            >>> _convert_length_to_typst("300")
            "225pt"
            >>> _convert_length_to_typst("50%")
            "50%"
            >>> _convert_length_to_typst("1pc")
            "12pt"
            >>> _convert_length_to_typst("2ex")
            None

        Notes:
            Implements Issue #114 (FIG-01) per the locked D-02 decision: px
            converts via the CSS-canonical 1px = 0.75pt; pc converts to pt
            (1pc = 12pt); %/em/pt/cm/mm/in pass through unchanged; any other
            unit (ex, ch, rem, vw, vh, vmin, vmax, Q, etc.) is unknown and is
            dropped with exactly one warning rather than emitted verbatim,
            which was the FIG-01 fatal Typst-compile-abort case.
        """
        match = re.fullmatch(r"(-?[0-9.]+)([a-zA-Zµ%]*)", value)
        if not match:
            logger.warning(f"Could not parse length value '{value}'; dropping.")
            return None

        number_str, unit = match.group(1), match.group(2)
        number = float(number_str)

        if unit == "" or unit == "px":
            # CSS canonical: 96px/in, 72pt/in -> 1px = 0.75pt
            return f"{number * 0.75:g}pt"
        if unit == "pc":
            return f"{number * 12:g}pt"  # 1 pica = 12 points
        if unit in _TYPST_PASSTHROUGH_UNITS:
            return value  # already Typst-valid, pass through unchanged

        logger.warning(
            f"Unsupported length unit '{unit}' in '{value}'; "
            "dropping dimension (image will use its natural size)."
        )
        return None

    def visit_toctree(self, node: nodes.Node) -> None:
        """
        Visit a toctree node (Sphinx table of contents tree).

        Requirement 13: Multi-document integration and toctree processing
        - Generate #include() for each entry
        - Apply #set heading(offset: 1) to lower heading levels
        - Issue #5: Fix relative paths for nested toctrees
          - Calculate relative paths from current document
        - Issue #7: Simplify toctree output with single content block
          - Generate single #[...] block containing all includes
          - Apply #set heading(offset: 1) once per toctree

        Args:
            node: The toctree node

        Notes:
            This method generates Typst #include() directives for each toctree entry
            within a single content block #[...] to apply heading offset without
            displaying the block delimiters in the output. This simplifies the
            generated Typst code and improves readability.
        """
        # Get entries from the toctree node
        entries = node.get("entries", [])

        logger.debug(f"Processing toctree with {len(entries)} entries")

        # If no entries, don't generate anything
        if not entries:
            logger.debug("Toctree has no entries, skipping")
            raise nodes.SkipNode

        # Get current document name for relative path calculation
        current_docname = getattr(self.builder, "current_docname", None)

        logger.debug(
            f"Current document for toctree: {current_docname}, "
            f"entries: {[docname for _, docname in entries]}"
        )

        # Generate scope block for all includes (unified code mode)
        # Use {...} scope block to isolate set rules while maintaining code mode
        # Start scope block (no # prefix in code mode)
        self.add_text("{\n")
        self.add_text("  set heading(offset: 1)\n")

        # Generate include() for each entry within the scope block
        # Each included file has its own imports, so block scope is safe.
        #
        # Deduplicate by ABSOLUTE docname across the whole master include graph
        # (the ledger lives on the builder, so it spans every document composing
        # one master -- not just this one toctree). Sphinx documentation
        # commonly lists the same document in more than one toctree (e.g.
        # doc/index.rst lists usage/extensions/index both directly and nested
        # under usage/index). In HTML each page is its own file, so a repeated
        # toctree entry is harmless navigation; but Typst's #include() flattens
        # each file inline, so #including one .typ twice re-emits every Typst
        # <label> it defines and the compile aborts with "label ... occurs
        # multiple times". Keeping only the FIRST include() of each docname
        # leaves every label defined exactly once, so all references (which are
        # never dropped) still resolve. Mock builders in unit tests have no
        # ledger; getattr(..., None) falls back to the original no-dedup path.
        included_docnames = getattr(self.builder, "_included_docnames", None)
        for _title, docname in entries:
            if included_docnames is not None:
                if docname in included_docnames:
                    logger.debug(
                        f"Skipping duplicate toctree include() for already-"
                        f"included document: {docname}"
                    )
                    continue
                included_docnames.add(docname)

            # Compute relative path for include() (Issue #5 fix)
            relative_path = self._compute_relative_include_path(
                docname, current_docname
            )

            logger.debug(
                f"Generated include() for toctree: {docname} -> {relative_path}.typ"
            )

            # Generate include() within the block (no # prefix in code mode)
            self.add_text(f'  include("{relative_path}.typ")\n')

        # End scope block
        self.add_text("}\n\n")

        # Skip processing children as we've handled the toctree entries
        raise nodes.SkipNode

    def depart_toctree(self, node: nodes.Node) -> None:
        """
        Depart a toctree node.

        Args:
            node: The toctree node
        """
        # Toctree is handled in visit
        pass

    def visit_reference(self, node: nodes.reference) -> None:
        """
        Visit a reference node (link).

        Generates link() function call (no # prefix in code mode).

        Args:
            node: The reference node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Get the reference URI
        refuri = node.get("refuri", "")
        refid = node.get("refid", "")

        # Resolve a LOCAL cross-document refuri (`<relpath><out_suffix>#anchor`)
        # up-front and decide whether its TARGET document is actually part of
        # the compiled master's include-set. A resolved cross-document
        # reference whose target doc is NOT included -- e.g. an ``:orphan:``
        # doc, excluded from every toctree, whose .typ is written but never
        # #include()d -- has no anchor in the compiled master; emitting
        # link(<targetdoc:anchor>) there would hard-fail typst.compile() with
        # "label ... does not exist". Such a reference must DEGRADE to plain
        # text (matching the LaTeX builder's undefined-reference behavior),
        # which means it opens NO link wrapper -- so this decision has to be
        # made here, before opens_wrapper / the concat-element enter below.
        # An empty master include-set (no typst_documents, mock/hand-built test
        # builders) is treated as "unknown" and never degrades, preserving the
        # existing cross-document behavior for those paths.
        xref = self._resolve_xref_docname(refuri) if refuri else None
        degrade_xref_to_text = False
        if xref is not None:
            master_included = getattr(self.builder, "master_included_docnames", None)
            if master_included and xref[0] not in master_included:
                degrade_xref_to_text = True

        # An empty-url reference (no refuri and no refid) opens NO wrapper: it
        # renders its children as plain inline content directly in the outer
        # context, so it must NOT enter/suppress a concat context (its children
        # participate in that context themselves). Every wrapper-opening path
        # (same-doc refid, internal #label, external URL) DOES enter: a link
        # that is a non-first sibling in a code-mode concat context (def-list
        # term / link body / desc parameter) is + separated, and that outer
        # context is suppressed for the link body -- handled by the link's own
        # _in_link context -- so no stray '+' leaks inside link(...).
        #
        # Concat/newline mutual exclusion (bug #9): capture whether a code-mode
        # concat context is active BEFORE _enter_inline_concat_element suppresses
        # its flag. Inside a concat context the '+' operator IS the separator, so
        # the list-item newline must NOT also fire -- otherwise a wrapper-opening
        # reference that is the first parameter emits
        #   text("(") +  <newline>  link(...)
        # stranding the '+' at end-of-line (no right operand) -> 'expected
        # expression'. Every other inline visitor (visit_Text / visit_literal /
        # visit_strong / visit_emphasis) already guards its newline this way; do
        # the same here rather than emitting the newline unconditionally.
        # A degraded cross-document reference renders as plain inline text (no
        # link wrapper), so like the empty-url path it must NOT enter/suppress a
        # concat context -- its children participate in the outer context.
        in_concat = self._inline_concat_context() is not None
        opens_wrapper = bool(refuri or refid) and not degrade_xref_to_text
        if opens_wrapper:
            self._enter_inline_concat_element()

        # Add list-item newline separator only when NOT in a concat context
        # (mutually exclusive with the concat '+' separator emitted above).
        if not in_concat and self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Check if next sibling is a target node (for label attachment)
        # This is needed in both list items and paragraphs in unified code mode
        next_is_target = False
        if node.parent:
            node_index = node.parent.index(node)
            if node_index + 1 < len(node.parent.children):
                next_node = node.parent.children[node_index + 1]
                if isinstance(next_node, nodes.target):
                    next_is_target = True

        # If next is target, wrap in markup mode for label attachment
        # In unified code mode, labels can only attach in markup mode blocks [...]
        if next_is_target:
            self.add_text("[")
            self._in_reference_with_target = True
            self._in_markup_mode = (
                True  # Enter markup mode - need # prefix for functions
            )

        # Save and reset list item separator for children (they're inside this element)
        was_list_item_needs_separator = self.list_item_needs_separator
        self.list_item_needs_separator = False

        # Internal same-document :target: (e.g. a figure/image target)
        # resolves to an empty/absent refuri with a populated refid instead
        # of a "#"-prefixed refuri. Handle it before the empty-URL guard so
        # it doesn't fall through to the plain-text fallback (FIG-02, D-03).
        if not refuri and refid:
            prefix = "#" if self._in_markup_mode else ""
            # A bare refid is a SAME-document target -> namespace with the
            # current docname so it matches the anchor that document emitted.
            label = self._namespace_label(self._current_docname(), refid)
            self.add_text(f"{prefix}link(<{label}>, ")

            # Replicate the method-end bookkeeping inline since this branch
            # returns early (mirrors the refuri branches below).
            if self._in_markup_mode:
                self._in_markup_mode = False
            self._in_link = True
            self._link_has_content = False
            self._reference_was_list_item_needs_separator = (
                was_list_item_needs_separator
            )
            return

        # Handle empty URLs (Typst 0.14+ rejects empty URLs)
        # This can occur with unresolved references, broken cross-references,
        # or malformed reStructuredText. Instead of generating invalid link("", ...),
        # we skip the link wrapper and render content as plain text.
        if not refuri:
            logger.warning(
                f"Reference node has empty URL. "
                f"Link will be rendered as plain text. "
                f"Check for broken references in source: {node.astext()}"
            )
            self._skip_link_wrapper = True
            return

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Check if it's an internal reference (starts with #)
        if refuri.startswith("#"):
            # Internal reference to a label in the SAME document -> namespace
            # with the current docname so it matches this document's anchor.
            label = self._namespace_label(self._current_docname(), refuri[1:])
            self.add_text(f"{prefix}link(<{label}>, ")
        elif xref is not None:
            # Resolved CROSS-document reference (`<relpath><out_suffix>#anchor`).
            if degrade_xref_to_text:
                # Target document is NOT part of the compiled master (orphan /
                # excluded from every toctree). Its anchor does not exist in the
                # master, so emit NO label link -- render the reference's text as
                # plain inline content (opens_wrapper was False, so no concat
                # element was entered; this mirrors the empty-url skip-wrapper
                # path exactly). Warn Sphinx-style so it surfaces in the build
                # warnings without turning a graceful degradation into a fatal.
                logger.warning(
                    f"cross-reference to non-included document '{xref[0]}' "
                    f"rendered as plain text (typstpdf includes only "
                    f"toctree-reachable documents): {node.astext()}"
                )
                self._skip_link_wrapper = True
                return
            # In the flattened master this must become a real label link, not a
            # dead string url: namespace with the TARGET docname so it byte-
            # matches the anchor the target document emitted.
            target_docname, anchor = xref
            label = self._namespace_label(target_docname, anchor)
            self.add_text(f"{prefix}link(<{label}>, ")
        else:
            # External reference (HTTP/HTTPS URL, whole-document ref, or other
            # relative path) -> plain string-url link, left unaffected.
            self.add_text(f'{prefix}link("{refuri}", ')

        # After outputting link(), turn off markup mode for content (second argument)
        # Content inside function arguments is code mode (no # prefix)
        if self._in_markup_mode:
            self._in_markup_mode = False

        # Mark that we're inside link() to use + for concatenation
        self._in_link = True
        self._link_has_content = False

        # Store state to restore in depart
        self._reference_was_list_item_needs_separator = was_list_item_needs_separator

    def depart_reference(self, node: nodes.reference) -> None:
        """
        Depart a reference node.

        Args:
            node: The reference node
        """
        # Skip link wrapper closing if we skipped it in visit
        if getattr(self, "_skip_link_wrapper", False):
            self._skip_link_wrapper = False
            # Restore list item separator state if needed
            if hasattr(self, "_reference_was_list_item_needs_separator"):
                if self.in_list_item:
                    self.list_item_needs_separator = True
                delattr(self, "_reference_was_list_item_needs_separator")
            return

        # Close the link function
        self.add_text(")")

        # Exit link context
        self._in_link = False

        # Restore the outer code-mode concat context suppressed for the link
        # body (entered only on wrapper-opening paths, so the skip-wrapper
        # branch above returns before this) and mark the link as a sibling so
        # the next term/link/desc expression is + separated.
        self._exit_inline_concat_element()

        # Restore and mark that next element needs separator
        if hasattr(self, "_reference_was_list_item_needs_separator"):
            if self.in_list_item:
                self.list_item_needs_separator = True
            delattr(self, "_reference_was_list_item_needs_separator")

    def unknown_visit(self, node: nodes.Node) -> None:
        """
        Handle unknown nodes during visit.

        Args:
            node: The unknown node
        """
        # Log a warning for unknown nodes but don't raise an exception
        from sphinx.util import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"unknown node type: {node}")

    def unknown_departure(self, node: nodes.Node) -> None:
        """
        Handle unknown nodes during departure.

        Args:
            node: The unknown node
        """
        # Silently ignore unknown departures
        pass

    def _convert_latex_to_typst(self, latex_content: str) -> str:
        """
        Convert LaTeX math syntax to Typst native syntax.

        Implements Task 6.5: Basic LaTeX to Typst conversion
        Requirement 4.9: Fallback when typst_use_mitex=False

        Args:
            latex_content: LaTeX math content

        Returns:
            Typst native math content
        """
        # Basic conversion rules for common LaTeX commands
        result = latex_content

        # Greek letters: \alpha -> alpha, \beta -> beta, etc.
        greek_letters = [
            "alpha",
            "beta",
            "gamma",
            "delta",
            "epsilon",
            "zeta",
            "eta",
            "theta",
            "iota",
            "kappa",
            "lambda",
            "mu",
            "nu",
            "xi",
            "omicron",
            "pi",
            "rho",
            "sigma",
            "tau",
            "upsilon",
            "phi",
            "chi",
            "psi",
            "omega",
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
            "Epsilon",
            "Zeta",
            "Eta",
            "Theta",
            "Iota",
            "Kappa",
            "Lambda",
            "Mu",
            "Nu",
            "Xi",
            "Omicron",
            "Pi",
            "Rho",
            "Sigma",
            "Tau",
            "Upsilon",
            "Phi",
            "Chi",
            "Psi",
            "Omega",
        ]
        for letter in greek_letters:
            result = result.replace(f"\\{letter}", letter)

        # Fractions: \frac{a}{b} -> frac(a, b)
        result = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"frac(\1, \2)", result)

        # Sum: \sum_{lower}^{upper} -> sum_(lower)^upper
        result = re.sub(r"\\sum_\{([^}]+)\}\^\{([^}]+)\}", r"sum_(\1)^(\2)", result)
        result = re.sub(r"\\sum_\{([^}]+)\}", r"sum_(\1)", result)
        result = result.replace(r"\sum", "sum")

        # Integral: \int_{lower}^{upper} -> integral_(lower)^upper
        result = re.sub(
            r"\\int_\{([^}]+)\}\^\{([^}]+)\}", r"integral_(\1)^(\2)", result
        )
        result = re.sub(r"\\int_\{([^}]+)\}", r"integral_(\1)", result)
        result = result.replace(r"\int", "integral")

        # Product: \prod -> product
        result = result.replace(r"\prod", "product")

        # Square root: \sqrt{x} -> sqrt(x)
        result = re.sub(r"\\sqrt\{([^}]+)\}", r"sqrt(\1)", result)

        # Infinity: \infty -> infinity
        result = result.replace(r"\infty", "infinity")

        # Partial derivative: \partial -> diff (Typst uses diff or ∂)
        result = result.replace(r"\partial", "diff")

        # Common functions
        result = result.replace(r"\sin", "sin")
        result = result.replace(r"\cos", "cos")
        result = result.replace(r"\tan", "tan")
        result = result.replace(r"\log", "log")
        result = result.replace(r"\ln", "ln")
        result = result.replace(r"\exp", "exp")

        # If there are still backslashes, warn about unconverted syntax
        if "\\" in result:
            logger.warning(
                f"LaTeX math contains commands that may not convert well to Typst: {latex_content}"
            )

        return result

    def visit_math(self, node: nodes.math) -> None:
        """
        Visit an inline math node.

        Implements Task 6.2: LaTeX math conversion (mitex)
        Implements Task 6.3: Labeled equations
        Implements Task 6.4: Typst native math support
        Implements Task 6.5: Math fallback functionality
        Requirement 4.3: Inline math should use #mi(`...`) format (LaTeX)
        Requirement 4.9: Fallback when typst_use_mitex=False
        Requirement 5.2: Inline math should use $...$ format (Typst native)
        Requirement 4.7: Labeled equations should generate <eq:label> format
        Design 3.3: Support both mitex and Typst native math

        Args:
            node: The inline math node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Extract math content
        math_content = node.astext()

        # Task 6.4: Check if this is explicitly marked as Typst native
        is_typst_native = "typst-native" in node.get("classes", [])

        # Task 6.5: Check typst_use_mitex config (default to True)
        use_mitex = getattr(self.builder.config, "typst_use_mitex", True)

        if is_typst_native or not use_mitex:
            # Requirement 5.2: Typst native inline math syntax
            # Task 6.5: Convert LaTeX to Typst if use_mitex=False
            if not is_typst_native and not use_mitex:
                # Convert LaTeX syntax to Typst native
                math_content = self._convert_latex_to_typst(math_content)
            self.add_text(f"${math_content}$")
        else:
            # Requirement 4.3: LaTeX math via mitex (no # prefix in code mode)
            self.add_text(f"mi(`{math_content}`)")

        # Task 6.3: Add label if present
        if "ids" in node and node["ids"]:
            label = self._namespace_label(self._current_docname(), node["ids"][0])
            self.add_text(f" <{label}>")

        # Skip children to prevent duplicate output of math content
        raise nodes.SkipNode

    def depart_math(self, node: nodes.math) -> None:
        """
        Depart an inline math node.

        Args:
            node: The inline math node
        """
        # No additional output needed
        pass

    def visit_math_block(self, node: nodes.math_block) -> None:
        """
        Visit a block math node.

        Implements Task 6.2: LaTeX math conversion (mitex)
        Implements Task 6.3: Labeled equations
        Implements Task 6.4: Typst native math support
        Implements Task 6.5: Math fallback functionality
        Requirement 4.2: Block math should use #mitex(`...`) format (LaTeX)
        Requirement 4.9: Fallback when typst_use_mitex=False
        Requirement 5.2: Block math should use $ ... $ format (Typst native)
        Requirement 4.7: Labeled equations should generate <eq:label> format
        Design 3.3: Support both mitex and Typst native math

        Args:
            node: The block math node
        """
        # Anchor node["ids"] (a ``:label:`` equation id such as
        # ``equation-euler``, or a propagated ``.. _t:`` target before the
        # ``.. math::``) via the shared markup-block helper, BEFORE the
        # equation. This REPLACES the old ` <label>` postfix (removed below):
        # a bare ` <label>` after a code-mode ``$ ... $`` / ``mitex(...)``
        # expression does not parse ("expected semicolon or line break") and
        # aborts the compile. A same-document ``:eq:``/``:ref:`` renders
        # link(<id>, ...) and resolves to this anchor. No ids -> no-op.
        self._emit_id_anchors(node)

        # Extract math content
        math_content = node.astext()

        # Task 6.4: Check if this is explicitly marked as Typst native
        is_typst_native = "typst-native" in node.get("classes", [])

        # Task 6.5: Check typst_use_mitex config (default to True)
        use_mitex = getattr(self.builder.config, "typst_use_mitex", True)

        if is_typst_native or not use_mitex:
            # Requirement 5.2: Typst native block math syntax
            # Task 6.5: Convert LaTeX to Typst if use_mitex=False
            if not is_typst_native and not use_mitex:
                # Convert LaTeX syntax to Typst native
                math_content = self._convert_latex_to_typst(math_content)
            self.add_text(f"$ {math_content} $")
        else:
            # Requirement 4.2: LaTeX math via mitex (no # prefix in code mode)
            self.add_text(f"mitex(`{math_content}`)")

        # Task 6.3: the equation label/id is anchored by _emit_id_anchors above
        # (a code-mode ` <label>` postfix on the equation failed to parse).
        self.add_text("\n\n")

        # Skip children to prevent duplicate output of math content
        raise nodes.SkipNode

    def depart_math_block(self, node: nodes.math_block) -> None:
        """
        Depart a block math node.

        Args:
            node: The block math node
        """
        # No additional output needed
        pass

    # Admonition nodes (Task 3.4)
    # Requirement 2.8-2.10: Convert Sphinx admonitions to gentle-clues

    def _visit_admonition(
        self, node: nodes.Node, clue_type: str, custom_title: str = None
    ) -> None:
        """
        Helper method to visit any admonition node.

        Opens a code-mode content-block call (`clue_type({`) so the body
        (paragraphs/text/literals emitted downstream as `par({...})`,
        `text(...)`, `raw(...)`) evaluates instead of printing as literal
        Typst source. A title child, if present, is not read here — docutils
        will visit it normally via visit_title's admonition-aware branch,
        which defers the rendered title to `_depart_admonition`.

        Args:
            node: The admonition node
            clue_type: The gentle-clues function name (e.g., 'info', 'warning', 'tip')
            custom_title: Optional static custom title for the admonition
        """
        # A propagated explicit target can land its id on this admonition
        # (note/warning/generic/topic); anchor it so a same-document
        # link(<id>, ...) resolves (no ids -> no-op).
        self._emit_id_anchors(node)

        # Add newline separator if in list item and not first element
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Reset per-admonition title state; stash the static custom title (if
        # any) for _depart_admonition to consume once the body has closed.
        self._pending_admonition_title = None
        self._custom_admonition_title = custom_title

        # Open code-mode content-block (NOT markup-mode "[") so the body
        # evaluates in the translator's unified code mode.
        self.add_text(f"{clue_type}({{")

    def _depart_admonition(self) -> None:
        """
        Helper method to depart any admonition node.

        Closes the code-mode content-block body and attaches the title
        argument (if any) — a dynamic, node-derived title takes precedence
        over a static custom title. The dynamic title is buffered code-mode
        content (from visit_title's admonition branch) and MUST be wrapped
        in a code block `{ ... }`, not a content block `[ ... ]`, so its
        inline calls (text(...), emph(...)) evaluate.
        """
        self.add_text("}")

        title_expr = None
        if self._pending_admonition_title:
            title_expr = "{" + self._pending_admonition_title + "}"
        elif self._custom_admonition_title:
            title_expr = f'"{self._custom_admonition_title}"'

        if title_expr:
            self.add_text(f", title: {title_expr}")

        self.add_text(")\n\n")

        # Mark that next element in list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_note(self, node: nodes.note) -> None:
        """Visit a note admonition (converts to #info[])."""
        self._visit_admonition(node, "info")

    def depart_note(self, node: nodes.note) -> None:
        """Depart a note admonition."""
        self._depart_admonition()

    def visit_warning(self, node: nodes.warning) -> None:
        """Visit a warning admonition (converts to #warning[])."""
        self._visit_admonition(node, "warning")

    def depart_warning(self, node: nodes.warning) -> None:
        """Depart a warning admonition."""
        self._depart_admonition()

    def visit_tip(self, node: nodes.tip) -> None:
        """Visit a tip admonition (converts to #tip[])."""
        self._visit_admonition(node, "tip")

    def depart_tip(self, node: nodes.tip) -> None:
        """Depart a tip admonition."""
        self._depart_admonition()

    def visit_important(self, node: nodes.important) -> None:
        """Visit an important admonition (converts to #warning(title: "Important")[])."""
        self._visit_admonition(node, "warning", custom_title="Important")

    def depart_important(self, node: nodes.important) -> None:
        """Depart an important admonition."""
        self._depart_admonition()

    def visit_caution(self, node: nodes.caution) -> None:
        """Visit a caution admonition (converts to #warning[])."""
        self._visit_admonition(node, "warning")

    def depart_caution(self, node: nodes.caution) -> None:
        """Depart a caution admonition."""
        self._depart_admonition()

    def visit_seealso(self, node: addnodes.seealso) -> None:
        """Visit a seealso admonition (converts to #info(title: "See Also")[])."""
        self._visit_admonition(node, "info", custom_title="See Also")

    def depart_seealso(self, node: addnodes.seealso) -> None:
        """Depart a seealso admonition."""
        self._depart_admonition()

    def visit_hint(self, node: nodes.hint) -> None:
        """Visit a hint admonition (converts to #tip[]).

        gentle-clues 1.3.1 has no dedicated `hint` clue; `tip` is the
        verified closest semantic analog (see RESEARCH.md D-06 mapping).
        """
        self._visit_admonition(node, "tip")

    def depart_hint(self, node: nodes.hint) -> None:
        """Depart a hint admonition."""
        self._depart_admonition()

    def visit_error(self, node: nodes.error) -> None:
        """Visit an error admonition (converts to #error[])."""
        self._visit_admonition(node, "error")

    def depart_error(self, node: nodes.error) -> None:
        """Depart an error admonition."""
        self._depart_admonition()

    def visit_danger(self, node: nodes.danger) -> None:
        """Visit a danger admonition (converts to #danger[])."""
        self._visit_admonition(node, "danger")

    def depart_danger(self, node: nodes.danger) -> None:
        """Depart a danger admonition."""
        self._depart_admonition()

    def visit_attention(self, node: nodes.attention) -> None:
        """Visit an attention admonition (converts to #warning[]).

        gentle-clues 1.3.1 has no dedicated `attention` clue; `warning` is
        the verified analog, consistent with the existing `caution`/
        `important` → `warning` precedent (see RESEARCH.md D-06 mapping).
        """
        self._visit_admonition(node, "warning")

    def depart_attention(self, node: nodes.attention) -> None:
        """Depart an attention admonition."""
        self._depart_admonition()

    def visit_admonition(self, node: nodes.admonition) -> None:
        """Visit a generic ``.. admonition::`` (converts to #clue[]).

        Maps to the base gentle-clues `clue` function (unstyled — no
        predefined icon/accent-color), since the generic directive always
        supplies its own directive-derived title (see RESEARCH.md D-06
        mapping). The title flows through the existing admonition-aware
        `visit_title`/`depart_title` buffer-swap automatically; no
        `custom_title` is passed here.
        """
        self._visit_admonition(node, "clue")

    def depart_admonition(self, node: nodes.admonition) -> None:
        """Depart a generic admonition."""
        self._depart_admonition()

    def visit_topic(self, node: nodes.topic) -> None:
        """Visit a topic node (BLK-02/D-01/D-02/D-05).

        A `.. topic::` renders as a titled `clue` box, reusing the same
        admonition helper as `.. admonition::` (D-01) -- the widened
        visit_title/depart_title buffer-swap (D-02) is what makes the
        title actually get consumed by _depart_admonition.

        A `.. contents::` topic (carrying the `contents` class) is instead
        box-less pass-through (D-05): its title is rendered as a bold label
        (handled entirely by visit_title/depart_title's insert-index trick)
        and its child bullet_list renders through the existing, unmodified
        list visitors -- no clue box wraps it here.
        """
        self._topic_is_contents = "contents" in (node.get("classes", []) or [])
        if self._topic_is_contents:
            # The clue-box path (_visit_admonition) anchors node['ids'] for a
            # normal topic; the box-less contents path returns early, so anchor
            # a propagated target's id here too (no ids -> no-op).
            self._emit_id_anchors(node)
            return
        self._visit_admonition(node, "clue")

    def depart_topic(self, node: nodes.topic) -> None:
        """Depart a topic node (BLK-02/D-01/D-02/D-05)."""
        if self._topic_is_contents:
            self._topic_is_contents = False
            return
        self._depart_admonition()

    # Line block nodes (BLK-03/D-03/D-04)

    def visit_line_block(self, node: nodes.line_block) -> None:
        """
        Visit a line_block node (an address, epigraph, or poetry stanza).

        Only the outermost line_block (depth 0) opens the `par({...})`
        wrapper -- a nested line_block (docutils nests these directly, no
        intermediate wrapper node) shares the same wrapper as its parent.
        `self._line_block_depth` is a single integer counter; docutils' own
        visitor recursion already provides the nesting "stack" for free, so
        no separate stack data structure is needed (see 13-RESEARCH.md
        "Don't Hand-Roll").
        """
        depth = self._line_block_depth
        if depth == 0:
            # A propagated explicit target can land its id on the outermost
            # line_block; anchor it so a same-document link(<id>, ...) resolves
            # (no ids -> no-op). Only at depth 0, before the par({ wrapper --
            # a nested line_block shares the parent's wrapper and never carries
            # a propagated block target.
            self._emit_id_anchors(node)
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")
            self._line_block_was_in_paragraph = self.in_paragraph
            self._line_block_was_paragraph_has_content = self.paragraph_has_content
            self.add_text("par({")
            self.in_paragraph = True
            self.paragraph_has_content = False
        self._line_block_depth = depth + 1

    def depart_line_block(self, node: nodes.line_block) -> None:
        """Depart a line_block node, closing the wrapper once depth returns to 0."""
        self._line_block_depth -= 1
        if self._line_block_depth == 0:
            self.add_text("})\n\n")
            self.in_paragraph = self._line_block_was_in_paragraph
            self.paragraph_has_content = self._line_block_was_paragraph_has_content
            if self.in_list_item:
                self.list_item_needs_separator = True

    def visit_line(self, node: nodes.line) -> None:
        """
        Visit a line node (one line inside a line_block).

        Emits a per-depth `h(...)` indent spacer for nested line_blocks
        (D-03/D-04) -- a plain code-mode stdlib call, no markup-mode
        bracket-wrap needed (unlike the Phase 11 `<label>`-anchor case,
        `h()` never carries a label). An empty `line` node (no Text child)
        falls through to depart_line's bare linebreak() for free -- no
        special-casing required.
        """
        self._add_paragraph_separator()
        indent_units = self._line_block_depth - 1
        if indent_units > 0:
            self.add_text(f"h({indent_units * 1.5}em)")

    def depart_line(self, node: nodes.line) -> None:
        """
        Depart a line node.

        Emits a REAL `linebreak()` call -- a source '\\n' between two
        code-mode statements is cosmetic-only (DESC-02 precedent), so this
        is what actually produces the visible line break.
        """
        self.add_text("\nlinebreak()")

    # Inline nodes (Task 7.4)
    # Requirement 3.1: Inline cross-references and links

    def visit_inline(self, node: nodes.inline) -> None:
        """
        Visit an inline node.

        Inline nodes are generic containers for inline content.
        They are often used for cross-references with specific CSS classes.

        Task 7.4: Handle inline nodes, especially those with 'xref' class
        Requirement 3.1: Cross-references and links

        VER-01 (Phase 12): Sphinx's ``VersionChange.run()`` bakes the exact,
        already-localized version-directive label wording directly into the
        doctree as a ``nodes.inline(classes=["versionmodified", <kind>])`` at
        directive-parse time (confirmed via live doctree dump, 12-RESEARCH.md
        Part 1) -- so no import of Sphinx's internal changeset-domain label
        map, and no label reconstruction, is needed here. This supersedes
        12-CONTEXT.md D-01's speculated import-based mechanism while
        honoring its "sourced from Sphinx, not hardcoded" intent: the
        translator only detects the already-classed inline and italicizes
        it (D-02's unboxed layout) by delegating to the proven
        `visit_emphasis` dummy-node idiom.
        """
        if "versionmodified" in node.get("classes", []):
            dummy_emph = nodes.emphasis()
            self.visit_emphasis(dummy_emph)
            return
        # Inline nodes are transparent containers - we just process their children
        # The CSS classes (like 'xref', 'doc', 'std-ref') are mainly for HTML/CSS styling
        # For Typst output, we simply render the text content
        pass

    def depart_inline(self, node: nodes.inline) -> None:
        """
        Depart an inline node.

        VER-01 (Phase 12): mirrors `visit_inline`'s classed-dispatch branch --
        see that method's docstring for the full rationale.
        """
        if "versionmodified" in node.get("classes", []):
            dummy_emph = nodes.emphasis()
            self.depart_emphasis(dummy_emph)
            return
        pass

    # Version-change directives (Phase 12, VER-01): `versionadded` /
    # `versionchanged` / `deprecated` / `versionremoved` all parse to a
    # single `addnodes.versionmodified` wrapping a paragraph whose first
    # child is the classed `nodes.inline` handled above. This pass-through
    # pair exists purely to silence the ×972 unknown_visit warning -- the
    # child paragraph already renders correctly through the existing
    # visit_paragraph chain (see 12-RESEARCH.md Pattern 1).

    def visit_versionmodified(self, node: addnodes.versionmodified) -> None:
        """Visit a versionmodified node (transparent pass-through)."""
        pass

    def depart_versionmodified(self, node: addnodes.versionmodified) -> None:
        """Depart a versionmodified node (transparent pass-through)."""
        pass

    # API description nodes (Issue #55)
    # Requirement: API説明ノードの処理

    def visit_index(self, node: addnodes.index) -> None:
        """
        Visit an index node.

        Index entries are skipped in Typst/PDF output as we don't generate indices.
        """
        raise nodes.SkipNode

    def depart_index(self, node: addnodes.index) -> None:
        """Depart an index node."""
        pass

    # Trivial structural node handlers (Phase 12, BLK-01/04/05/06): four
    # small additive handlers reusing already-proven idioms from elsewhere
    # in this file (emit-then-SkipNode, pass-through, bare SkipNode, and
    # dummy-Text-node delegation respectively).

    def visit_transition(self, node: nodes.transition) -> None:
        """
        Visit a transition node (a `----` horizontal rule in RST).

        Emits a full-width Typst rule via ``line(length: 100%)`` -- a
        genuine content gap otherwise, since a bare transition renders
        nothing today (BLK-01). Self-closing node: no children to
        descend into, so this always raises SkipNode.
        """
        # A propagated explicit target (``.. _t:`` before a ``----`` rule)
        # lands its id on the transition; anchor it so a same-document
        # link(<id>, ...) resolves (no ids -> no-op, byte-unchanged).
        self._emit_id_anchors(node)
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text("line(length: 100%)\n\n")
        if self.in_list_item:
            self.list_item_needs_separator = True
        raise nodes.SkipNode

    def depart_transition(self, node: nodes.transition) -> None:
        """Depart a transition node (unreached; kept for symmetry)."""
        pass

    def visit_glossary(self, node: addnodes.glossary) -> None:
        """
        Visit a glossary node (`.. glossary::` directive wrapper).

        Transparent pass-through (BLK-04): the wrapped `definition_list`
        child already renders via `visit_definition_list`, and the term
        anchor is provided by the `depart_term` fix from Plan 12-02 --
        do NOT duplicate that anchor logic here.

        A propagated explicit target (``.. _t:`` before ``.. glossary::``)
        lands its id on THIS glossary node (distinct from the per-term
        anchors); anchor it so a same-document link(<id>, ...) resolves. A
        plain glossary carries no ids -> no-op, byte-unchanged.
        """
        self._emit_id_anchors(node)

    def depart_glossary(self, node: addnodes.glossary) -> None:
        """Depart a glossary node (transparent pass-through)."""
        pass

    def visit_tabular_col_spec(self, node: nodes.Node) -> None:
        """
        Visit a tabular_col_spec node (`.. tabularcolumns::` directive).

        This is a LaTeX-only column-width hint with no Typst equivalent
        (BLK-05). The node is self-closing, so raising SkipNode here
        safely drops it with no risk of leaking the raw column-spec
        content into the compiled output.
        """
        raise nodes.SkipNode

    def visit_abbreviation(self, node: nodes.abbreviation) -> None:
        """
        Visit an abbreviation node (`:abbr:` role).

        No-op: the term's own Text child renders via the normal chain.
        """
        pass

    def depart_abbreviation(self, node: nodes.abbreviation) -> None:
        """
        Depart an abbreviation node.

        Appends the expansion inline as " (expansion)" (BLK-06). Stateless
        -- expands on every occurrence, not just the first (D-08). The
        expansion is author-controlled RST, so it is routed through a
        dummy `nodes.Text` delegated to `visit_Text` -- inheriting the
        existing string-escaping regime -- rather than `node.astext()` or
        a raw f-string interpolation (V5 Input Validation, Pitfall 7).
        """
        explanation = node.get("explanation", "")
        if explanation:
            dummy_text = nodes.Text(f" ({explanation})")
            self.visit_Text(dummy_text)

    # Graceful-degrade net for out-of-scope graphical nodes (Issue #114,
    # DEG-01/DEG-02): unlike visit_index's silent skip, these nodes must
    # leave a reader-visible trace (D-01) -- a bordered native-Typst
    # placeholder naming the node, plus exactly one warning -- rather than
    # silently vanishing or leaking raw DOT/diagram-spec source.

    def _visit_graphical_placeholder(self, node: nodes.Node, node_label: str) -> None:
        """
        Shared graceful-degrade helper for out-of-scope graphical nodes.

        Emits a visible bordered placeholder block naming the node type
        (D-01), logs exactly one warning, and skips the node's children
        entirely -- graphviz/inheritance_diagram store their real content
        (DOT source / class-hierarchy spec) as node attributes rather than
        human-readable Text children, so descending would risk leaking raw
        source instead of rendering anything useful.

        Uses native Typst rect()/box() (Typst stdlib) rather than the
        gentle-clues admonition functions used for note/warning/etc, per
        D-01: a placeholder must not be visually confusable with a real
        admonition.

        Args:
            node: The out-of-scope node (graphviz or inheritance_diagram).
            node_label: Human-readable node-type name for the warning and
                placeholder text.
        """
        logger.warning(
            f"{node_label} is not supported in Typst output; rendering placeholder"
        )
        self.add_text(
            f'rect(text("[{node_label} diagram omitted]"), '
            "stroke: 0.5pt, inset: 8pt, radius: 2pt)\n\n"
        )
        raise nodes.SkipNode

    def visit_graphviz(self, node: nodes.Node) -> None:
        """Visit a graphviz node; renders a placeholder (DEG-01, D-01)."""
        self._visit_graphical_placeholder(node, "graphviz")

    def visit_inheritance_diagram(self, node: nodes.Node) -> None:
        """Visit an inheritance_diagram node; renders a placeholder (DEG-02, D-01)."""
        self._visit_graphical_placeholder(node, "inheritance diagram")

    def visit_desc(self, node: addnodes.desc) -> None:
        """
        Visit a desc node (API description container).

        Desc nodes contain API descriptions (classes, functions, methods, etc.).

        An explicit target (``.. _target:``) immediately preceding an
        object-description directive (e.g. ``.. option::``) has its id
        propagated by docutils' ``PropagateTargets`` transform onto THIS
        outer ``desc`` container -- a DIFFERENT id than the one on
        ``desc_signature`` (bug #17 anchors that one). In the overwhelming
        common case (no preceding explicit target) ``desc`` carries no ids
        at all, so this is a no-op / byte-unchanged for existing output.
        Mirrors the established container-anchor pattern (bug #20) used by
        visit_bullet_list/visit_table/visit_block_quote/etc: anchor BEFORE
        any child (signature/content) is visited.
        """
        self._emit_id_anchors(node)

    def depart_desc(self, node: addnodes.desc) -> None:
        """
        Depart a desc node.

        Add spacing after API description blocks.
        """
        self.body.append("\n\n")

    def visit_desc_signature(self, node: addnodes.desc_signature) -> None:
        """
        Visit a desc_signature node (API element signature).

        Signatures are rendered in bold using strong({}) wrapper.
        """
        # Create a dummy strong node and use its visitor logic
        dummy_strong = nodes.strong()
        self.visit_strong(dummy_strong)
        # Reset per signature (DESC-02): each desc_signature starts fresh,
        # so consecutive signatures don't carry over a stray linebreak().
        self._is_first_desc_signature_line = True

    def depart_desc_signature(self, node: addnodes.desc_signature) -> None:
        """Depart a desc_signature node."""
        # Use strong's depart logic
        dummy_strong = nodes.strong()
        self.depart_strong(dummy_strong)
        # Emit a Typst anchor for every id on the signature so same-document
        # cross-references resolve to this API declaration. depart_reference's
        # refid branch emits ``link(<_sanitize_label(refid)>, ...)`` for a
        # same-document xref, but the anchor it points at was never emitted
        # here -- unlike visit_target/visit_title/depart_term, desc_signature
        # (the node type carrying API-declaration ids) emitted none, so every
        # ``:c:func:``/``:py:func:`` style refid link to a declaration dangled
        # with Typst's semantic ``label ... does not exist``.
        #
        # Mirror the proven target-anchor form -- ``[#metadata(none) <id>]`` --
        # a zero-content markup block that carries the label and joins cleanly
        # as its own statement in the surrounding code-mode block (a bare
        # code-mode ``label("id")`` would juxtapose/fail to join). Route every
        # id through _sanitize_label so the anchor name byte-matches the
        # reference side (both sides use the same helper). Multiple ids
        # (aliases/overloads) each get an anchor; a signature with NO ids emits
        # nothing (byte-unchanged). ids are globally unique per document
        # (docutils make_id), so no label is defined twice; dedupe defensively.
        docname = self._current_docname()
        seen_labels: set[str] = set()
        for node_id in node.get("ids", []):
            label_id = self._namespace_label(docname, node_id)
            if label_id in seen_labels:
                continue
            seen_labels.add(label_id)
            self.body.append(f"\n[#metadata(none) <{label_id}>]")
        # Add extra spacing after signature
        self.body.append("\n")

    def visit_desc_returns(self, node: addnodes.desc_returns) -> None:
        """
        Visit a desc_returns node (a signature's return-type annotation).

        Emits a literal ' -> ' arrow before the return type (DESC-01).
        Resolved return-type xref children already stream through the
        unmodified visit_reference refid branch -- no extra code needed
        for that case.
        """
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text('text(" -> ")')
        if self.in_list_item:
            self.list_item_needs_separator = True

    def depart_desc_returns(self, node: addnodes.desc_returns) -> None:
        """Depart a desc_returns node."""
        pass

    def visit_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
        """
        Visit a desc_signature_line node (one line of a genuine multi-line
        signature, e.g. a C++ template declaration).

        Emits a real Typst linebreak() before every line after the first
        (DESC-02) -- a source '\\n' between two code-mode statements is
        proven cosmetic-only (produces zero visual break), so linebreak()
        (Typst stdlib) is required. The first line emits nothing extra,
        keeping the single-line case (one desc_signature_line, or none)
        backward-compatible.
        """
        if not self._is_first_desc_signature_line:
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")
            self.add_text("linebreak()")
            if self.in_list_item:
                self.list_item_needs_separator = True
        self._is_first_desc_signature_line = False

    def depart_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
        """Depart a desc_signature_line node."""
        pass

    def visit_desc_content(self, node: addnodes.desc_content) -> None:
        """
        Visit a desc_content node (API description content).
        """
        pass

    def depart_desc_content(self, node: addnodes.desc_content) -> None:
        """Depart a desc_content node."""
        pass

    def visit_desc_inline(self, node: addnodes.desc_inline) -> None:
        """
        Visit a desc_inline node (an inline signature fragment, e.g.
        :cpp:expr:).

        Transparent pass-through (DESC-04, D-06): desc_inline is a distinct
        Sphinx node class from desc_signature, so node-type dispatch alone
        satisfies D-06's strong()-suppression -- do NOT delegate to
        visit_strong the way visit_desc_signature does, that would
        reintroduce the strong() wrapper this requirement forbids.
        """
        pass

    def depart_desc_inline(self, node: addnodes.desc_inline) -> None:
        """Depart a desc_inline node."""
        pass

    def visit_desc_annotation(self, node: addnodes.desc_annotation) -> None:
        """
        Visit a desc_annotation node (type annotations like 'class', 'async', etc.).
        """
        pass

    def depart_desc_annotation(self, node: addnodes.desc_annotation) -> None:
        """
        Depart a desc_annotation node.

        Space after annotation is handled by desc_sig_space node.
        """
        # Don't add space here - desc_sig_space handles it
        # Don't set list_item_needs_separator - let next node handle it
        pass

    def visit_desc_addname(self, node: addnodes.desc_addname) -> None:
        """
        Visit a desc_addname node (module name prefix).
        """
        pass

    def depart_desc_addname(self, node: addnodes.desc_addname) -> None:
        """Depart a desc_addname node."""
        pass

    def visit_desc_name(self, node: addnodes.desc_name) -> None:
        """
        Visit a desc_name node (function/class name).
        """
        pass

    def depart_desc_name(self, node: addnodes.desc_name) -> None:
        """Depart a desc_name node."""
        # Mark that next element needs separator (for parameterlist)
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_desc_parameterlist(self, node: addnodes.desc_parameterlist) -> None:
        """
        Visit a desc_parameterlist node (parameter list container).

        Parameters are concatenated with + inside text parentheses.
        """
        # Add separator before opening paren
        if self.in_list_item and self.list_item_needs_separator:
            self.body.append("\n")

        # Output opening paren as text with + after it
        self.body.append('text("(") + ')

        # Mark that parameterlist started
        self.in_desc_parameter = True
        self._desc_parameter_has_content = (
            False  # First parameter doesn't need + before it
        )

    def depart_desc_parameterlist(self, node: addnodes.desc_parameterlist) -> None:
        """Depart a desc_parameterlist node."""
        # Output closing paren as text, with + before it
        if self._desc_parameter_has_content:
            self.body.append(" + ")
        self.body.append('text(")")')
        self.in_desc_parameter = False

    def visit_desc_parameter(self, node: addnodes.desc_parameter) -> None:
        """
        Visit a desc_parameter node (individual parameter).
        """
        # No changes needed - already in desc_parameter context from parameterlist
        # Don't reset _desc_parameter_has_content here - it's managed by depart_desc_parameter
        pass

    def depart_desc_parameter(self, node: addnodes.desc_parameter) -> None:
        """
        Depart a desc_parameter node.

        Add comma + space between parameters if not last.
        """
        # Add comma between parameters
        if node.next_node(descend=False, siblings=True):
            self.body.append(' + text(", ")')
            self._desc_parameter_has_content = True

    def visit_desc_optional(self, node: addnodes.desc_optional) -> None:
        """
        Visit a desc_optional node (trailing optional parameter group,
        e.g. printf(fmt[, args[, more]])).

        Literal-bracket-wraps the optional group, reusing the existing
        _desc_parameter_has_content flag (DESC-03, zero new state). A
        nested desc_optional is a structural doctree sibling, not a
        parent-child relationship the handler needs to track -- the
        identical handler firing again for the nested node produces
        correctly nested brackets with no depth counter.
        """
        if self._desc_parameter_has_content:
            self.add_text(" + ")
        self.add_text('text("[")')
        self._desc_parameter_has_content = True

    def depart_desc_optional(self, node: addnodes.desc_optional) -> None:
        """Depart a desc_optional node."""
        self.add_text(' + text("]")')
        self._desc_parameter_has_content = True

    def visit_field_list(self, node: nodes.field_list) -> None:
        """
        Visit a field_list node (structured fields like Parameters, Returns).
        """
        # Emit a leading newline separator when this field list follows a
        # sibling inside a list item, matching the block-visitor pattern
        # established in bug #4 (bullet_list/literal_block/definition_list/
        # block_quote). Otherwise visit_field_name's strong( juxtaposes
        # against the preceding inline expression in the list-item content
        # block -- e.g. `text("For example:")strong(` -- a Typst parse error
        # ("expected semicolon or line break", GATE-02 fatal #12). field_list
        # was the one block visitor omitted from that fix.
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
            self.list_item_needs_separator = False

    def depart_field_list(self, node: nodes.field_list) -> None:
        """
        Depart a field_list node.

        Add spacing after field lists.
        """
        self.body.append("\n")

        # Mark that a following sibling in the same list item must be
        # separated (block-visitor pattern, bug #4).
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_field(self, node: nodes.field) -> None:
        """
        Visit a field node (individual field in a field list).
        """
        pass

    def depart_field(self, node: nodes.field) -> None:
        """Depart a field node."""
        pass

    def visit_field_name(self, node: nodes.field_name) -> None:
        """
        Visit a field_name node (field name like 'Parameters', 'Returns').

        Field names are rendered in bold with a colon (no # prefix in code mode).
        """
        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Use strong() function (no # prefix in code mode)
        self.body.append("strong(")

        # Store state to restore in depart
        self._field_name_was_in_paragraph = was_in_paragraph

    def depart_field_name(self, node: nodes.field_name) -> None:
        """Depart a field_name node."""
        # Close strong() and add colon
        self.body.append(' + text(":"))\n')

        # Restore paragraph state
        if hasattr(self, "_field_name_was_in_paragraph"):
            self.in_paragraph = self._field_name_was_in_paragraph
            delattr(self, "_field_name_was_in_paragraph")

    def visit_field_body(self, node: nodes.field_body) -> None:
        """
        Visit a field_body node (field content).

        A field body written inline on its field line (e.g. a confval
        ``:default: The value of **html_title**``) is COLLAPSED by docutils:
        its children are inline nodes (Text/strong/literal/reference) DIRECTLY
        under ``field_body``, with no wrapping ``paragraph``. Emitted into the
        code-mode content block those adjacent expressions juxtapose
        (``text("The value of ")strong({...})``) -- a Typst syntax error
        ("expected semicolon or line break", GATE-02 fatal #8). Activate the
        shared inline-concat context (bug #5 machinery) so they are ``+``
        separated into one content value.

        Only an ALL-inline field body needs this. A block field body (real
        ``paragraph``/list/literal-block children) already emits valid,
        ``\\n\\n``-separated statements via the normal par() path, so it keeps
        the concat context OFF to avoid a stray ``+`` around a ``par(...)``.
        """
        self._field_body_stack.append(
            (self._in_field_body, self._field_body_has_content)
        )
        all_inline = all(
            isinstance(child, (nodes.Text, nodes.Inline)) for child in node.children
        )
        if all_inline:
            self._in_field_body = True
            self._field_body_has_content = False
        else:
            self._in_field_body = False

    def depart_field_body(self, node: nodes.field_body) -> None:
        """
        Depart a field_body node.

        Restore the concat context saved by :meth:`visit_field_body` and add a
        newline after the field body.
        """
        self._in_field_body, self._field_body_has_content = self._field_body_stack.pop()
        self.body.append("\n")

    def visit_rubric(self, node: nodes.rubric) -> None:
        """
        Visit a rubric node (section subheading).

        Rubrics are rendered as subsection headings using strong({}) wrapper.
        """
        # A propagated explicit target (``.. _t:`` immediately before a
        # ``.. rubric::``) lands its id on this rubric node; anchor it so a
        # same-/cross-document link(<id>, ...) resolves (no ids -> no-op).
        self._emit_id_anchors(node)
        # Add newline before rubric
        self.body.append("\n")
        # Create a dummy strong node and use its visitor logic
        dummy_strong = nodes.strong()
        self.visit_strong(dummy_strong)

    def depart_rubric(self, node: nodes.rubric) -> None:
        """Depart a rubric node."""
        # Use strong's depart logic
        dummy_strong = nodes.strong()
        self.depart_strong(dummy_strong)
        # Add extra spacing after rubric
        self.body.append("\n")

    def visit_title_reference(self, node: nodes.title_reference) -> None:
        """
        Visit a title_reference node (reference to a title).

        Title references are rendered in emphasis using emph({}) wrapper.
        """
        # Create a dummy emphasis node and use its visitor logic
        dummy_emph = nodes.emphasis()
        self.visit_emphasis(dummy_emph)

    def depart_title_reference(self, node: nodes.title_reference) -> None:
        """Depart a title_reference node."""
        # Use emphasis's depart logic
        dummy_emph = nodes.emphasis()
        self.depart_emphasis(dummy_emph)

    # Additional signature nodes (desc_sig_* family)

    def visit_desc_sig_keyword(self, node: addnodes.desc_sig_keyword) -> None:
        """Visit a desc_sig_keyword node (keywords in signatures like 'class', 'def')."""
        pass

    def depart_desc_sig_keyword(self, node: addnodes.desc_sig_keyword) -> None:
        """Depart a desc_sig_keyword node."""
        pass

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

    def visit_desc_sig_name(self, node: addnodes.desc_sig_name) -> None:
        """Visit a desc_sig_name node (names in signatures)."""
        pass

    def depart_desc_sig_name(self, node: addnodes.desc_sig_name) -> None:
        """Depart a desc_sig_name node."""
        pass

    def visit_desc_sig_punctuation(self, node: addnodes.desc_sig_punctuation) -> None:
        """Visit a desc_sig_punctuation node (punctuation in signatures like ':', '=')."""
        pass

    def depart_desc_sig_punctuation(self, node: addnodes.desc_sig_punctuation) -> None:
        """Depart a desc_sig_punctuation node."""
        pass

    def visit_desc_sig_operator(self, node: addnodes.desc_sig_operator) -> None:
        """Visit a desc_sig_operator node (operators in signatures)."""
        pass

    def depart_desc_sig_operator(self, node: addnodes.desc_sig_operator) -> None:
        """Depart a desc_sig_operator node."""
        pass

    # Literal nodes for API documentation

    def visit_literal_strong(self, node: nodes.inline) -> None:
        """Visit a literal_strong node (bold literal text in field lists)."""
        # Create a dummy strong node and use its visitor logic
        dummy_strong = nodes.strong()
        self.visit_strong(dummy_strong)

    def depart_literal_strong(self, node: nodes.inline) -> None:
        """Depart a literal_strong node."""
        # Use strong's depart logic
        dummy_strong = nodes.strong()
        self.depart_strong(dummy_strong)

    def visit_literal_emphasis(self, node: nodes.inline) -> None:
        """Visit a literal_emphasis node (emphasized literal text in field lists)."""
        # Create a dummy emphasis node and use its visitor logic
        dummy_emph = nodes.emphasis()
        self.visit_emphasis(dummy_emph)

    def depart_literal_emphasis(self, node: nodes.inline) -> None:
        """Depart a literal_emphasis node."""
        # Use emphasis's depart logic
        dummy_emph = nodes.emphasis()
        self.depart_emphasis(dummy_emph)

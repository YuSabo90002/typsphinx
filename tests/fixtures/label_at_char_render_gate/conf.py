# Sphinx configuration for the label-@-char render-gate fixture.
#
# Minimal self-contained project used by
# tests/test_label_at_char_render_gate.py to prove that a docutils/Sphinx id
# containing a Typst-label-invalid character (`@`) is sanitized IDENTICALLY at
# both its anchor DEFINITION (a `target` node -> `[#metadata(none) <id>]`) and
# its cross-REFERENCE (a `reference` node with a same-document `refid` ->
# `link(<id>, ...)`), so the real compile (sphinx-build -> typst.compile())
# yields a %PDF with no `unclosed label` fatal AND the def/ref sanitized names
# still match (the link resolves).
#
# WHY a synthesized directive instead of the raw C-domain construct: Sphinx's
# C-domain anonymous entities (`@data`/`@alias`) are the real-world source of
# `@` in an id (bug #10, e.g. `c.Data.@data.a`), but those ids live on
# `desc_signature` nodes, for which this translator emits NO `<label>` anchor
# at all -- so a `:c:var:` cross-reference to them is dangling ("label does
# not exist") independently of the `@` bug, and could never compile to %PDF.
# To test the `@`-sanitizer's def==ref property in isolation (a resolvable
# link that actually compiles), this directive injects an anchor-bearing node
# and a same-document `reference` that BOTH carry an id with a literal `@` --
# post-parse, so docutils' make_id normalization does not strip the `@` --
# faithfully mirroring the corpus's `<...@...>` anchor + `link(<...@...>)` ref
# pair.
#
# The anchor is a `target` node emitting `[#metadata(none) <sanitize(id)>]`
# (visit_target) -- the exact anchor form the corpus C-domain entities emit.
# The nodes are injected at `doctree-resolved` (AFTER all read-phase
# transforms) rather than parse-time, because docutils' PropagateTargets
# transform would otherwise move a standalone target's id onto the following
# block element (a paragraph, which emits no anchor), defeating the test.
# Injecting post-transform guarantees the target keeps its `@`-id and emits a
# real, resolvable anchor.

from docutils import nodes

# An id with a literal `@`, mirroring the C-domain anonymous-entity shape
# `c.Data.@data.a` that produced the corpus `unclosed label` fatal.
AT_LABEL_ID = "myapp.@thing.a"


def _inject_at_label(app, doctree, docname):
    """Append an `@`-id target anchor + a same-document reference to it."""
    # Cross-REFERENCE: a same-document reference (refuri empty, refid set) ->
    # visit_reference's refid branch emits `link(<sanitize(refid)>, ...)`.
    ref = nodes.reference("", "see the anchored thing", refid=AT_LABEL_ID)
    para = nodes.paragraph()
    para += ref
    # Anchor DEFINITION: an internal hyperlink target carrying the `@`-id ->
    # visit_target emits `[#metadata(none) <sanitize(id)>]`.
    target = nodes.target(ids=[AT_LABEL_ID])
    doctree += para
    doctree += target


def setup(app):
    app.connect("doctree-resolved", _inject_at_label)
    return {"parallel_read_safe": True, "parallel_write_safe": True}


project = "Label At Char Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set.
typst_documents = [
    ("index", "index", "Label At Char Render Gate", "Test Author"),
]

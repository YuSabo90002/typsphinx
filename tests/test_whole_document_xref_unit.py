"""
Phase 48 plan 06, Task 2: fast, offline unit gate for the resolver, the
policy predicate and the self-anchor emission behind the whole-document
cross-reference guard fix (G-48-4 / XREF-03 gap closure).

Every value asserted here is taken from ``48-EXPECTED-STRUCTURE.md``'s
"Phase 48 Plan 05 -- Whole-Document Reference Path" section -- never read
off a fresh build (binding constraint #6). This module is a DIRECT unit
gate: no ``sphinx-build``, no ``typst.compile()``. It carries no
``@pytest.mark.slow``.

**Design split** (per this plan's own Task 2 action): ``_resolve_xref_
docname`` (a pure string transform, taking only a ``refuri``) is the
UNCONDITIONAL low-level resolver -- it resolves ANY local whole-document
refuri ending in the builder's ``out_suffix`` to ``(docname, "")``,
regardless of whether the reference is Sphinx-internal or whether the
target is a real document. ``_reference_anchor_decision`` (which DOES see
the whole node) is the POLICY layer one level up: it additionally gates
whether that resolved pair is exposed through its own ``.xref`` field on
``node.get("internal")`` being truthy AND the target docname being a
member of ``env.found_docs`` -- the owner's option-a choice
(``48-EXPECTED-STRUCTURE.md`` §6: "guard only references that resolve
onto a real document"). Reference nodes are built the way Sphinx's own
``sphinx.util.nodes.make_refnode`` builds one (measured this session
against the installed Sphinx 9.1.0 source, ``sphinx/util/nodes.py``):
``nodes.reference('', '', internal=True)``, and for a whole-document
target a ``refuri`` with no fragment. A hand-written relative rST link
carries no ``internal`` flag at all.

Per this module's own instruction: only the two cases where BOTH options
recorded in ``48-EXPECTED-STRUCTURE.md`` §6 agree are asserted as general
policy cases -- an internal reference onto a KNOWN document is guarded; a
non-internal reference onto an UNKNOWN target is not. The one DIVERGENT
case (an internal reference onto an UNKNOWN target) is asserted by exactly
ONE option-specific test, naming option-a (the owner's actual choice) in
its own docstring.

The self-anchor token constant (``_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN``,
fixed value ``__tsx-doc__`` per ``48-EXPECTED-STRUCTURE.md`` §1) is never
imported at module top level -- it does not exist on the unfixed tree, and
importing it there would break collection entirely. It is resolved with
``getattr`` on the ``typsphinx.translator`` module inside the one test
that asserts it, so a MISSING constant fails that test (correctly, as a
strict xfail) instead of an ImportError failing every test in this file.
"""

import inspect
from pathlib import Path

from docutils import nodes as docutils_nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

import typsphinx.translator as translator_module
from typsphinx.translator import TypstTranslator

# ---------------------------------------------------------------------------
# Local harness -- locally scoped to THIS module (per this plan's own
# instruction): NOT imported from tests/test_citation_degradation_gate.py's
# _StubBuilder/_make_document pair, and NOT from
# tests/test_label_existence_guard_unit.py's variants. Shaped on both (D-02:
# imitate, never import), extended with the ``found_docs``-carrying ``env``
# neither sibling stub needs -- added HERE, on this module's own stub, per
# this plan's explicit instruction not to edit either sibling module.
# ---------------------------------------------------------------------------


class _MockConfig:
    """Minimal stand-in config -- none of this module's scenarios touch a
    config-dependent branch."""


class _MockDomains:
    """Minimal stand-in for ``env.domains``."""


class _MockEnv:
    """Carries ``found_docs`` -- this module's own addition to the
    established stub shape, needed by the policy-predicate tests below."""

    def __init__(self, found_docs=None):
        self.domains = _MockDomains()
        self.found_docs = set(found_docs) if found_docs is not None else set()


class _StubBuilder:
    """
    A locally-scoped stub builder, shaped on
    ``tests/test_citation_degradation_gate.py``'s ``_StubBuilder``
    (``config``, ``env``, ``out_suffix``, ``current_docname``,
    ``get_target_uri``), with ``current_docname`` and ``found_docs`` as
    constructor parameters so one class serves every scenario below rather
    than a stub subclass per scenario.
    """

    config = _MockConfig()
    out_suffix = ".typ"

    def __init__(self, current_docname="index", found_docs=None):
        self.current_docname = current_docname
        self.env = _MockEnv(found_docs)

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        return docname + self.out_suffix


def _make_document() -> docutils_nodes.document:
    """Build a minimal ``nodes.document`` the same way
    ``tests/test_citation_degradation_gate.py``'s and
    ``tests/test_label_existence_guard_unit.py``'s own ``_make_document``
    helpers do: a real ``Reporter``, ``doc.settings`` as a docutils
    ``states.Struct()`` with just the attributes ``TypstTranslator``'s
    constructor and visitor chain touch. No RST parser and no Sphinx
    application are involved."""
    reporter = Reporter("", 2, 4)
    doc = docutils_nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc


def _render_body(doc: docutils_nodes.document, builder: object) -> str:
    """Instantiate a ``TypstTranslator`` over ``doc`` with the given
    builder stub, walk the tree, and return the joined emitted body."""
    translator = TypstTranslator(doc, builder)
    doc.walkabout(translator)
    return translator.astext()


# ---------------------------------------------------------------------------
# 1. The resolver -- unconditional, low-level (Task 2 behaviour item 1).
# ---------------------------------------------------------------------------


class TestResolveWholeDocumentXref:
    """``_resolve_xref_docname`` is a pure string transform over a
    ``refuri`` alone -- it carries no node, so it cannot itself consult
    ``internal``/``found_docs``. It is the UNCONDITIONAL low-level
    resolution step; the POLICY gate lives one layer up
    (``TestReferenceAnchorDecisionWholeDocumentPolicy`` below)."""

    def test_resolve_xref_docname_returns_empty_anchor_for_whole_document_refuri(
        self,
    ):
        """48-06-PLAN.md Task 2 behaviour item 1: a local whole-document
        refuri ending in the builder's ``out_suffix`` (no fragment)
        resolves to ``(target_docname, "")`` -- today: ``None``."""
        builder = _StubBuilder(current_docname="index")
        translator = TypstTranslator(_make_document(), builder)

        result = translator._resolve_xref_docname("included.typ")

        assert result == ("included", ""), f"expected ('included', ''), got {result!r}"


class TestResolveAnchoredXrefUnchanged:
    """Invariance (D-06): the already-shipped anchored cross-document path
    this gap must not disturb."""

    def test_resolve_xref_docname_anchored_reference_unchanged(self):
        """TRUE both pre- and post-fix -- an anchored cross-document refuri
        (a real ``#anchor`` fragment present) already resolves to its
        ``(docname, anchor)`` pair today, and D-06 keeps that path
        unchanged."""
        builder = _StubBuilder(current_docname="index")
        translator = TypstTranslator(_make_document(), builder)

        result = translator._resolve_xref_docname("second.typ#anchor-x")

        assert result == (
            "second",
            "anchor-x",
        ), f"expected ('second', 'anchor-x'), got {result!r}"


# ---------------------------------------------------------------------------
# 2. The policy predicate (Task 2 behaviour item 2 + the two agreeing
#    invariance cases + the one option-specific divergent case).
# ---------------------------------------------------------------------------


def _make_internal_reference(
    refuri: str, *, internal: bool
) -> docutils_nodes.reference:
    """Build a reference node the way ``sphinx.util.nodes.make_refnode``
    builds a whole-document reference: ``nodes.reference('', '',
    internal=...)`` with a ``refuri`` carrying no fragment."""
    ref = docutils_nodes.reference("", "", internal=internal)
    ref["refuri"] = refuri
    return ref


class TestReferenceAnchorDecisionWholeDocumentPolicy:
    """
    ``_reference_anchor_decision``'s ``.xref`` field is the POLICY-gated
    view of ``_resolve_xref_docname``'s raw resolution: for a whole-document
    refuri (no anchor), it is exposed only when the reference is
    Sphinx-internal AND its target resolves onto a real document
    (``env.found_docs`` membership) -- the owner's option-a choice recorded
    verbatim in ``48-EXPECTED-STRUCTURE.md`` §6.
    """

    def test_internal_reference_onto_known_document_yields_pair(self):
        """48-06-PLAN.md Task 2 behaviour item 2: a Sphinx-internal
        whole-document reference whose target IS a known document
        (``env.found_docs``) yields ``(target_docname, "")`` through
        ``.xref`` -- today: ``None``."""
        builder = _StubBuilder(current_docname="index", found_docs={"included"})
        translator = TypstTranslator(_make_document(), builder)
        ref = _make_internal_reference("included.typ", internal=True)

        decision = translator._reference_anchor_decision(ref)

        assert decision.xref == (
            "included",
            "",
        ), f"expected decision.xref == ('included', ''), got {decision.xref!r}"

    def test_non_internal_reference_onto_unknown_target_not_guarded(self):
        """Invariance -- TRUE pre-fix (today ``_resolve_xref_docname``
        returns ``None`` unconditionally for any no-fragment refuri, so
        ``decision.xref`` is already ``None`` here regardless of
        ``internal``/``found_docs``) and remains TRUE post-fix (this
        reference's ``internal`` flag is ``False``, failing the policy
        gate's first half): a relative link to a real file asset keeps its
        string-url form."""
        builder = _StubBuilder(current_docname="index", found_docs=set())
        translator = TypstTranslator(_make_document(), builder)
        ref = _make_internal_reference("unrelated_asset.typ", internal=False)

        decision = translator._reference_anchor_decision(ref)

        assert (
            decision.xref is None
        ), f"expected decision.xref is None, got {decision.xref!r}"

    def test_anchored_cross_document_reference_decision_unchanged(self):
        """Invariance (D-06): the already-shipped anchored-xref path's
        ``.xref`` field is unaffected by this gap's fix -- TRUE both before
        and after."""
        builder = _StubBuilder(current_docname="index", found_docs={"second"})
        translator = TypstTranslator(_make_document(), builder)
        ref = _make_internal_reference("second.typ#anchor-x", internal=True)

        decision = translator._reference_anchor_decision(ref)

        assert decision.xref == (
            "second",
            "anchor-x",
        ), f"expected decision.xref == ('second', 'anchor-x'), got {decision.xref!r}"

    def test_option_a_internal_reference_onto_unknown_target_keeps_string_url(self):
        """Option-specific test (**option-a**, the owner's actual choice at
        the 48-05 blocking checkpoint, recorded verbatim in
        ``48-EXPECTED-STRUCTURE.md`` §6): the DIVERGENT case -- an internal
        (Sphinx-generated) reference whose target does NOT resolve onto a
        real document -- keeps the string-url form under option-a, so
        ``decision.xref`` stays ``None`` even though the reference IS
        internal. (Under the rejected option-b this case would instead
        route through the guard against an unreachable label and degrade to
        plain text -- not asserted here.) Not an xfail: this assertion is
        TRUE both pre-fix (nothing is routed through the guard at all yet)
        and post-fix (option-a's predicate excludes it), so it never
        flips."""
        builder = _StubBuilder(current_docname="index", found_docs=set())
        translator = TypstTranslator(_make_document(), builder)
        ref = _make_internal_reference("genindex.typ", internal=True)

        decision = translator._reference_anchor_decision(ref)

        assert decision.xref is None, (
            f"expected decision.xref is None under option-a for an internal "
            f"reference onto an unknown target, got {decision.xref!r}"
        )


# ---------------------------------------------------------------------------
# 3. The self-anchor emission (Task 2 behaviour item 3 + its invariance).
# ---------------------------------------------------------------------------


class TestSelfAnchorEmission:
    """48-EXPECTED-STRUCTURE.md §2's definition-site form, fully substituted
    for docname ``included``."""

    def test_document_with_builder_docname_emits_self_anchor_once(self):
        """48-06-PLAN.md Task 2 behaviour item 3 /
        ``48-EXPECTED-STRUCTURE.md`` §2's fully-substituted example: a
        document translated with a builder-supplied current docname emits
        its own self-anchor exactly once, in the established zero-width
        ``metadata`` anchor form, immediately after the document's opening
        code-block brace -- ``#{\\n[#metadata(none) <included:__tsx-doc__>]\\n``."""
        builder = _StubBuilder(current_docname="included")
        doc = _make_document()
        section = docutils_nodes.section()
        para = docutils_nodes.paragraph()
        para += docutils_nodes.Text("Included Body")
        section += para
        doc += section

        body = _render_body(doc, builder)

        assert body.startswith("#{\n[#metadata(none) <included:__tsx-doc__>]\n"), (
            f"expected the self-anchor immediately after the opening "
            f"code-block brace, got:\n{body!r}"
        )
        assert body.count("<included:__tsx-doc__>") == 1, (
            f"expected the self-anchor to appear EXACTLY once, found "
            f"{body.count('<included:__tsx-doc__>')} in:\n{body!r}"
        )


class TestNoSelfAnchorWithoutBuilderDocname:
    """Invariance: a hand-built doctree with no builder docname keeps
    byte-identical output -- no self-anchor."""

    def test_no_builder_docname_emits_no_self_anchor(self):
        """TRUE pre-fix (nothing emits a self-anchor at all today) and
        remains TRUE post-fix (``48-EXPECTED-STRUCTURE.md`` §2: the
        self-anchor is emitted only when ``self._current_docname()`` is
        truthy -- hand-built test doctrees with no builder docname keep
        byte-identical output, matching every other
        ``_current_docname()``-gated site in the translator)."""
        builder = _StubBuilder(current_docname=None)
        doc = _make_document()
        section = docutils_nodes.section()
        para = docutils_nodes.paragraph()
        para += docutils_nodes.Text("No Docname Body")
        section += para
        doc += section

        body = _render_body(doc, builder)

        assert body.startswith(
            "#{\n"
        ), f"expected body to start with '#{{\\n', got:\n{body!r}"
        assert "__tsx-doc__" not in body, (
            f"expected no self-anchor token when no builder docname is "
            f"supplied, found one in:\n{body!r}"
        )


# ---------------------------------------------------------------------------
# 4. The single-derivation-point structural gate (Task 2 behaviour item 4).
# ---------------------------------------------------------------------------


class TestSelfAnchorTokenSingleDerivationPointStructural:
    """The self-anchor token exists as ONE module-level constant, and both
    the definition site and the reference site derive their label from it
    through ``_namespace_label`` (D-13) -- never a second spelling. Resolved
    with ``getattr`` on the module (never imported at module top level) so a
    MISSING constant fails THIS test instead of breaking collection for the
    whole file on the unfixed tree."""

    def test_self_anchor_token_is_single_module_level_constant(self):
        """48-06-PLAN.md Task 2 behaviour item 4 /
        ``48-EXPECTED-STRUCTURE.md`` §1: the fixed token ``__tsx-doc__`` as
        ONE module-level constant, referenced by name at its own definition
        plus both the definition-site (``visit_document``) and
        reference-site (``visit_reference``) ``_namespace_label(...)``
        calls -- never re-spelled at either."""
        token = getattr(translator_module, "_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN", None)
        assert token is not None, (
            "expected typsphinx.translator to carry a module-level "
            "_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN constant"
        )
        assert token == "__tsx-doc__", (
            f"expected the fixed token '__tsx-doc__' "
            f"(48-EXPECTED-STRUCTURE.md §1), got {token!r}"
        )

        source = Path(inspect.getfile(translator_module)).read_text(encoding="utf-8")
        # At least 3: the module-level definition itself, the
        # definition-site (visit_document) _namespace_label(...) call, and
        # the reference-site (visit_reference) _namespace_label(...) call --
        # both derived through the SAME constant, never a second spelling.
        occurrences = source.count("_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN")
        assert occurrences >= 3, (
            f"expected the token identifier to appear at least 3 times "
            f"(module-level definition + definition-site + reference-site "
            f"usage), found {occurrences} in {translator_module.__file__}"
        )

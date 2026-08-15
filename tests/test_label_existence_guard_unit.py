"""
Phase 48 plan 03, Task 3: the direct unit gate on
``TypstTranslator._label_existence_guard()``'s own contract (XREF-04) --
structurally mirroring ``tests/test_citation_degradation_gate.py``'s
``TestWr03EligibilityDecisionAgreesWithEmission`` parametrized-table
convention (D-02: imitate, never import). Every value asserted here is
taken from ``48-EXPECTED-STRUCTURE.md``'s ``## Guard contract`` section --
never read off a fresh build.

This module is a DIRECT unit gate on the helper itself (no ``sphinx-build``,
no ``typst.compile()``), plus a small hand-built-doctree render harness
(shaped on ``test_citation_degradation_gate.py``'s ``_StubBuilder``/
``_make_document`` pair, locally scoped rather than imported per that same
convention) for the two tests that need to observe the guard through the
real emission path (edge/empty, D-06). Every test here is fast and pure --
none builds or compiles, so nothing in this module carries
``@pytest.mark.slow``.
"""

import inspect
import re
from pathlib import Path

from docutils import nodes as docutils_nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

from typsphinx.translator import TypstTranslator

# ---------------------------------------------------------------------------
# Local harness (D-02: shaped on test_citation_degradation_gate.py's
# _StubBuilder / _make_document pair, not imported from it).
# ---------------------------------------------------------------------------


class _MockConfig:
    """Minimal stand-in config -- neither harness variant below needs a
    real one; the two builder variants below differ only in whether
    ``typst_documents`` exists on this object at all."""


class _MockDomains:
    """Minimal stand-in for ``env.domains``."""


class _MockEnv:
    domains = _MockDomains()


class _StubBuilderNoIncludeSetAttr:
    """
    A builder stub carrying NO include-set attribute at all -- not
    ``typst_documents``, not the deleted ``master_included_docnames``,
    nothing. Item 6 (edge/empty): the D-07 guard's demand side takes no
    Python-side input, so a translator whose builder is this bare should
    emit the identical guarded expression a fully-configured builder would.
    """

    config = _MockConfig()
    env = _MockEnv()
    out_suffix = ".typ"
    current_docname = "index"

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        return docname + self.out_suffix


class _StubBuilderEmptyTypstDocuments:
    """
    A builder stub whose ``config.typst_documents`` is an empty list --
    the second edge/empty variant item 6 requires, distinct from carrying
    no attribute at all.
    """

    class _ConfigWithEmptyTypstDocuments:
        typst_documents: list = []

    config = _ConfigWithEmptyTypstDocuments()
    env = _MockEnv()
    out_suffix = ".typ"
    current_docname = "index"

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        return docname + self.out_suffix


def _make_document() -> docutils_nodes.document:
    """Build a minimal ``nodes.document`` the same way
    ``test_citation_degradation_gate.py``'s ``_make_document`` does: a real
    ``Reporter``, ``doc.settings`` as a docutils ``states.Struct()`` with
    just the attributes ``TypstTranslator``'s constructor and visitor chain
    touch. No RST parser and no Sphinx application are involved."""
    reporter = Reporter("", 2, 4)
    doc = docutils_nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc


def _build_cross_doc_reference_doctree() -> docutils_nodes.document:
    """A single citing reference whose ``refuri`` resolves to a
    cross-document target (``"second.typ#anchor-x"``) -- the shape that
    drives ``visit_reference`` into the D-07 guarded branch."""
    doc = _make_document()
    section = docutils_nodes.section()
    para = docutils_nodes.paragraph()
    ref = docutils_nodes.reference(refuri="second.typ#anchor-x")
    ref += docutils_nodes.Text("Cross Doc")
    para += ref
    section += para
    doc += section
    return doc


def _build_bare_refid_reference_doctree() -> docutils_nodes.document:
    """A single citing reference carrying ONLY a ``refid`` (no ``refuri``)
    -- the bare-refid same-document branch D-06 exempts from the guard."""
    doc = _make_document()
    section = docutils_nodes.section()
    para = docutils_nodes.paragraph()
    ref = docutils_nodes.reference(refid="same-doc-target")
    ref += docutils_nodes.Text("Same Doc")
    para += ref
    section += para
    doc += section
    return doc


def _build_hash_prefixed_refuri_reference_doctree() -> docutils_nodes.document:
    """A single citing reference whose ``refuri`` is a ``#``-prefixed
    internal anchor -- the second same-document branch D-06 exempts from
    the guard."""
    doc = _make_document()
    section = docutils_nodes.section()
    para = docutils_nodes.paragraph()
    ref = docutils_nodes.reference(refuri="#same-doc-target")
    ref += docutils_nodes.Text("Same Doc")
    para += ref
    section += para
    doc += section
    return doc


def _render_body(doc: docutils_nodes.document, builder: object) -> str:
    """Instantiate a ``TypstTranslator`` over ``doc`` with the given
    builder stub, walk the tree, and return the joined emitted body."""
    translator = TypstTranslator(doc, builder)
    doc.walkabout(translator)
    return translator.astext()


# ---------------------------------------------------------------------------
# 1. Contract shape.
# ---------------------------------------------------------------------------


class TestGuardContractShape:
    """The returned pair's open/close strings carry the exact bound
    identifier and body-opener/closer shape ``48-EXPECTED-STRUCTURE.md``'s
    Guard contract fixes, for every combination of prefix and body
    spelling."""

    def test_code_mode_body_true(self):
        translator = TypstTranslator(_make_document(), _StubBuilderNoIncludeSetAttr())
        for prefix in ("", "#"):
            guard = translator._label_existence_guard(
                "test:representative-label", prefix=prefix, code_mode_body=True
            )
            assert guard.open_str == f"{prefix}context {{ let __tsx_body = [#{{"
            assert guard.close_str.startswith("}]")

    def test_code_mode_body_false(self):
        translator = TypstTranslator(_make_document(), _StubBuilderNoIncludeSetAttr())
        for prefix in ("", "#"):
            guard = translator._label_existence_guard(
                "test:representative-label", prefix=prefix, code_mode_body=False
            )
            assert guard.open_str == f"{prefix}context {{ let __tsx_body = ["
            assert guard.close_str.startswith("]")
            # The bracket-body-false close string must NOT accidentally
            # start with the code-mode `}]` spelling.
            assert not guard.close_str.startswith("}]")

    def test_bound_identifier_is_fixed(self):
        """The bound identifier is `__tsx_body` -- fixed project-wide by
        48-01/48-EXPECTED-STRUCTURE.md, never a different spelling."""
        translator = TypstTranslator(_make_document(), _StubBuilderNoIncludeSetAttr())
        guard = translator._label_existence_guard(
            "test:representative-label", code_mode_body=True
        )
        assert "let __tsx_body = " in guard.open_str
        assert "__tsx_body" in guard.close_str


# ---------------------------------------------------------------------------
# 2. Unbroken conditional (research Pitfall 1).
# ---------------------------------------------------------------------------


class TestUnbrokenConditional:
    """The close string's conditional is ONE unbroken statement -- the
    `if query(<L>).len() > 0` condition and its opening `{` are never
    separated by a newline (a hard Typst `expected block` parse error if
    they were)."""

    def test_condition_and_brace_share_one_line(self):
        translator = TypstTranslator(_make_document(), _StubBuilderNoIncludeSetAttr())
        guard = translator._label_existence_guard("index:id1", code_mode_body=True)
        assert re.search(
            r"if query\(<index:id1>\)\.len\(\) > 0 \{",
            guard.close_str,
        ), guard.close_str

    def test_close_string_has_no_newline_at_all(self):
        translator = TypstTranslator(_make_document(), _StubBuilderNoIncludeSetAttr())
        guard = translator._label_existence_guard("index:id1", code_mode_body=True)
        assert "\n" not in guard.close_str


# ---------------------------------------------------------------------------
# 3. Single label spelling (edge/encoding).
# ---------------------------------------------------------------------------


class TestSingleLabelSpelling:
    """The label the caller passes appears in the close string exactly
    twice (the existence query and the link call), both occurrences
    byte-identical -- and the helper's own body derives no label itself."""

    def test_label_appears_exactly_twice_identically(self):
        translator = TypstTranslator(_make_document(), _StubBuilderNoIncludeSetAttr())
        label = "index:smith2020"
        guard = translator._label_existence_guard(label, code_mode_body=True)
        occurrences = re.findall(re.escape(f"<{label}>"), guard.close_str)
        assert len(occurrences) == 2, guard.close_str
        assert all(o == f"<{label}>" for o in occurrences)

    def test_helper_calls_no_label_derivation_routine(self):
        """Source inspection of `_label_existence_guard`'s own body: it
        never CALLS `_namespace_label` or `_sanitize_label` -- the label
        it guards is always the caller's already-namespaced value. Checks
        for the real call spelling (`self._namespace_label(`/
        `self._sanitize_label(`) rather than a bare substring match,
        because the method's own docstring mentions
        ``_namespace_label()`` in prose (with no `self.` prefix, since it
        is describing the CALLER's derivation, not this method's own) --
        a bare substring check would false-positive on that mention."""
        source = inspect.getsource(TypstTranslator._label_existence_guard)
        assert "self._namespace_label(" not in source
        assert "self._sanitize_label(" not in source


# ---------------------------------------------------------------------------
# 4. Order independence (edge/ordering).
# ---------------------------------------------------------------------------


class TestOrderIndependence:
    """The close string tests the query result's LENGTH and never indexes
    into it -- a label attached more than once therefore yields the same
    decision regardless of hit order."""

    def test_close_string_tests_length_never_indexes(self):
        translator = TypstTranslator(_make_document(), _StubBuilderNoIncludeSetAttr())
        guard = translator._label_existence_guard("index:id1", code_mode_body=True)
        assert ".len() > 0" in guard.close_str
        assert ".at(" not in guard.close_str
        assert ".first(" not in guard.close_str
        assert "[0]" not in guard.close_str


# ---------------------------------------------------------------------------
# 5. No attachment (edge/adjacency).
# ---------------------------------------------------------------------------


class TestNoAttachment:
    """
    The guard is demand side only: neither returned string contains a
    label-attachment construct (a `label(` call, or a bare `<...>`
    immediately followed by a closing bracket). This proves the helper
    cannot introduce a duplicate label -- it does NOT prove a namespace
    collision is harmless.

    Two label namespaces that collide after sanitization therefore produce
    ONE label whose existence query is satisfied, and the guard links
    rather than aborting; the guard adds no new duplicate-label COMPILE
    failure of its own. The compile-level CONSEQUENCE -- a reference whose
    real target is absent instead linking to a colliding decoy -- is a
    false negative characterized by
    `tests/fixtures/xref_label_collision_guard_gate/` and its gate in
    `tests/test_xref_compile_time_guard_render_gate.py`, and accepted as a
    limit in 48-04, not proven or disproven by this string-level test.

    Narrowing: labels are namespaced `docname:id` and `_sanitize_label`
    maps each invalid character to a distinct `_u{codepoint:x}_` token, so
    a cross-document collision additionally requires the DOCNAME segment
    to collide too -- realistically only via the `/` -> `_u2f_` route that
    fixture exercises. This is NOT the broader claim that any two ids
    colliding is sufficient.
    """

    def test_guard_attaches_no_label(self):
        translator = TypstTranslator(_make_document(), _StubBuilderNoIncludeSetAttr())
        guard = translator._label_existence_guard(
            "a_u2f_b:nested-target", code_mode_body=True
        )
        combined = guard.open_str + guard.close_str
        assert "label(" not in combined
        assert re.search(r"<[^>]+>\]", combined) is None


# ---------------------------------------------------------------------------
# 6. No builder input (edge/empty).
# ---------------------------------------------------------------------------


class TestNoBuilderInput:
    """The demand-side decision has no Python-side input: a translator
    whose builder stub carries NO include-set attribute at all, and one
    whose `typst_documents` is an empty list, both emit the SAME guarded
    expression for the same reference."""

    def test_no_include_set_attribute_emits_guarded_form(self):
        doc = _build_cross_doc_reference_doctree()
        body = _render_body(doc, _StubBuilderNoIncludeSetAttr())
        assert "context { let __tsx_body = [#{" in body
        assert "query(<second:anchor-x>)" in body

    def test_empty_typst_documents_emits_guarded_form(self):
        doc = _build_cross_doc_reference_doctree()
        body = _render_body(doc, _StubBuilderEmptyTypstDocuments())
        assert "context { let __tsx_body = [#{" in body
        assert "query(<second:anchor-x>)" in body

    def test_both_stub_variants_emit_byte_identical_guarded_expression(self):
        body_no_attr = _render_body(
            _build_cross_doc_reference_doctree(), _StubBuilderNoIncludeSetAttr()
        )
        body_empty_list = _render_body(
            _build_cross_doc_reference_doctree(), _StubBuilderEmptyTypstDocuments()
        )
        assert body_no_attr == body_empty_list


# ---------------------------------------------------------------------------
# 7. D-06 exemption, as an explicit negative assertion (SC#4).
# ---------------------------------------------------------------------------


class TestD06SameDocumentExemption:
    """The two same-document `visit_reference` branches emit the plain
    unguarded link form and never the guard's conditional -- the
    assertion that stops a future executor over-applying the guard while
    touching `visit_reference`."""

    def test_bare_refid_reference_emits_no_guard(self):
        doc = _build_bare_refid_reference_doctree()
        body = _render_body(doc, _StubBuilderNoIncludeSetAttr())
        assert "link(<index:same-doc-target>, " in body
        assert "context {" not in body
        assert "query(<" not in body

    def test_hash_prefixed_internal_refuri_emits_no_guard(self):
        doc = _build_hash_prefixed_refuri_reference_doctree()
        body = _render_body(doc, _StubBuilderNoIncludeSetAttr())
        assert "link(<index:same-doc-target>, " in body
        assert "context {" not in body
        assert "query(<" not in body


# ---------------------------------------------------------------------------
# 8. XREF-04 site enumeration (SC#2/SC#3), structural.
# ---------------------------------------------------------------------------


class TestSingleDerivationPointStructural:
    """The guard's conditional appears in exactly ONE place in the whole
    package -- inside the shared helper -- so no site carries its own
    derivation; and no file under `typsphinx/` mentions the deleted
    builder include-set attribute."""

    @staticmethod
    def _package_dir():
        # Walked from THIS test file, never a hardcoded absolute path.
        return Path(__file__).resolve().parent.parent / "typsphinx"

    def test_guard_conditional_construction_appears_exactly_once(self):
        package_dir = self._package_dir()
        total = 0
        for py_file in sorted(package_dir.rglob("*.py")):
            text = py_file.read_text(encoding="utf-8")
            # The literal f-string interpolation form the helper alone
            # uses to BUILD the conditional -- distinct from any docstring
            # PROSE mention of the shape (which uses `<label>`/`<L>`
            # placeholders, never the real `{label}` interpolation).
            total += text.count("query(<{label}>)")
        assert total == 1, (
            f"expected the guard conditional's f-string construction to "
            f"appear exactly once (inside _label_existence_guard), found "
            f"{total} across {package_dir}"
        )

    def test_no_file_mentions_deleted_include_set_attribute(self):
        package_dir = self._package_dir()
        offenders = []
        for py_file in sorted(package_dir.rglob("*.py")):
            text = py_file.read_text(encoding="utf-8")
            if "master_included_docnames" in text:
                offenders.append(str(py_file))
        assert not offenders, (
            f"deleted attribute 'master_included_docnames' still mentioned "
            f"in: {offenders}"
        )

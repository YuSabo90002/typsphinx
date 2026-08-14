"""
Phase 49 plan 04: unit coverage for the five module-level derivation
functions this plan adds to ``typsphinx/translator.py``
(``INCLUDE_STATE_KEY``, ``make_include_edge_key``,
``derive_master_edge_keys``, ``render_include_edge_state``,
``render_include_guard``) plus ``TypstBuilder._build_include_edge_map()``'s
own idempotency/non-mutation contract.

Every asserted value substitutes into ``49-EXPECTED-STRUCTURE.md``'s
``## Emission contract`` and ``## Fixture specification`` (binding
constraint #6) -- no value here is read off a live build's own output,
except the arity-readback sub-suite, which compiles a hand-written Typst
PROBE (not the production code's own emitted ``.typ`` file) to measure the
Typst LANGUAGE's own type/length semantics, mirroring ``49-EVIDENCE.md``'s
own probe methodology.

This is a FAST unit module (no Sphinx build) except the arity-readback
sub-suite (``TestPublicationArityReadback``), which is marked
``@pytest.mark.slow`` since it drives a real ``typst.compile()`` per arity,
and the idempotency/non-mutation sub-suite (``TestBuilderDerivationContract``),
which drives one real Sphinx build via ``SphinxTestApp``.
"""

from pathlib import Path

import pytest
from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter
from sphinx.testing.util import SphinxTestApp

from typsphinx.translator import (
    INCLUDE_STATE_KEY,
    TypstTranslator,
    derive_master_edge_keys,
    escape_typst_string,
    make_include_edge_key,
    render_include_edge_state,
    render_include_guard,
)

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Traversal (derive_master_edge_keys) -- COMP-05
# ---------------------------------------------------------------------------


class TestDeriveMasterEdgeKeysTraversal:
    """``derive_master_edge_keys()``'s document-order, first-encounter-wins
    DFS -- every case transcribed from ``49-EXPECTED-STRUCTURE.md``'s
    ``## Traversal rule`` and its own worked substitutions, never read off
    a build."""

    def test_source_order_preserved_for_three_child_parent(self):
        """A parent with three children, none shared, in a straight line
        (no nesting) -- the returned tuple is in the SAME order as the
        parent's own ordered include-file list."""
        toctree_includes = {"index": ["a", "b", "c"]}
        assert derive_master_edge_keys(toctree_includes, "index") == (
            "index#0>a",
            "index#0>b",
            "index#0>c",
        )

    def test_first_encounter_wins_on_mirror_pair_orderings(self):
        """The mirror-pair fixture's own two orderings (Fixture
        specification entry 2): ``xmastera`` lists ``zmid`` then
        ``shared`` (shared claimed NESTED, under zmid); ``xmasterb`` lists
        ``shared`` then ``zmid`` (shared claimed DIRECT, and zmid's own
        claim on shared is lost)."""
        toctree_includes = {
            "xmastera": ["zmid", "shared"],
            "xmasterb": ["shared", "zmid"],
            "zmid": ["shared"],
        }
        assert derive_master_edge_keys(toctree_includes, "xmastera") == (
            "xmastera#0>zmid",
            "zmid#0>shared",
        )
        assert derive_master_edge_keys(toctree_includes, "xmasterb") == (
            "xmasterb#0>shared",
            "xmasterb#0>zmid",
        )

    def test_two_node_cycle_terminates_with_forward_edge_only(self):
        """``alpha`` toctrees ``beta``; ``beta`` toctrees ``alpha`` back --
        the DFS seeds ``traversed`` with the master's own docname, so the
        back edge is dark and the walk terminates."""
        toctree_includes = {"alpha": ["beta"], "beta": ["alpha"]}
        assert derive_master_edge_keys(toctree_includes, "alpha") == ("alpha#0>beta",)

    def test_self_referencing_parent_produces_no_self_edge(self):
        """A parent whose OWN include-file list names itself (a shape that
        never reaches ``includefiles`` in a real Sphinx build, per
        ``sphinx/directives/other.py``'s pre-loop
        ``all_docnames.remove(current_docname)`` -- but exercised here
        directly against the DFS in isolation): ``traversed`` is seeded
        with the master's own docname BEFORE the walk begins, so a
        self-referencing entry is already traversed and produces no
        edge."""
        toctree_includes = {"index": ["index", "other"]}
        assert derive_master_edge_keys(toctree_includes, "index") == ("index#0>other",)

    def test_duplicated_child_produces_exactly_one_key_at_occurrence_0(self):
        """A parent listing the same child twice: the graph side claims
        the child at its FIRST non-traversed appearance (occurrence 0);
        the second appearance is already ``in traversed`` and produces no
        second edge -- an occurrence-1 key can never appear in a
        published edge set (D-04)."""
        toctree_includes = {"index": ["child", "child"]}
        assert derive_master_edge_keys(toctree_includes, "index") == ("index#0>child",)

    def test_master_with_no_children_produces_empty_tuple(self):
        """A master absent from the mapping entirely (no toctree of its
        own) is treated as having no children, matching how the mirrored
        Sphinx walk behaves for a document with no toctree."""
        assert derive_master_edge_keys({}, "solo") == ()

    def test_last_listed_child_not_emitted_first(self):
        """The direct regression detector for the forbidden LIFO
        work-stack shape (``stack.pop()`` after forward ``.append()``
        iteration): for a parent listing four children in order, the
        FIRST returned edge key names the FIRST-listed child, not the
        LAST -- a work-stack shape would process the last-listed child
        first, silently reversing sibling order with no compile error."""
        toctree_includes = {"index": ["first", "second", "third", "fourth"]}
        keys = derive_master_edge_keys(toctree_includes, "index")
        assert keys[0] == "index#0>first", (
            f"expected the FIRST-listed child ('first') to produce the "
            f"FIRST edge key -- got {keys[0]!r}; this is the forbidden "
            f"work-stack shape's exact defect (COMP-05/SC#3) if it fails"
        )
        assert keys[-1] == "index#0>fourth"


# ---------------------------------------------------------------------------
# Key derivation (make_include_edge_key) -- D-04/D-05, T-49-01/T-49-02
# ---------------------------------------------------------------------------


class TestMakeIncludeEdgeKey:
    """``make_include_edge_key()`` is the ONE shared derivation point
    (D-05) -- these tests simulate the two call SHAPES (the graph side's
    own call, via ``derive_master_edge_keys()``, and the emission side's
    own direct call, mirroring ``visit_toctree``'s own call) and assert
    byte-identical output for equivalent inputs (T-49-02)."""

    def test_graph_side_and_emission_side_call_shapes_agree(self):
        """The graph side's own derived key (via ``derive_master_edge_
        keys()``, called with a builder-shaped mapping argument) and the
        emission side's own direct call (mirroring ``visit_toctree``'s
        own ``make_include_edge_key(current_docname, docname,
        occurrence=occurrence)`` call) produce byte-identical strings for
        the same parent/child/occurrence triple."""
        graph_side = derive_master_edge_keys({"index": ["child"]}, "index")
        emission_side = make_include_edge_key("index", "child", occurrence=0)
        assert graph_side == (emission_side,)
        assert graph_side[0] == emission_side

    def test_docname_with_quote_and_backslash_escapes_identically_both_sides(
        self,
    ):
        """T-49-01: a docname containing a double quote and a backslash
        produces a valid, identical literal whether derived on the graph
        side or the emission side -- both routes through the SAME
        ``escape_typst_string()`` call inside ``make_include_edge_key()``,
        so there is only one call site to ever diverge from."""
        parent = 'pa"rent'
        child = "ch\\ild"
        graph_side = derive_master_edge_keys({parent: [child]}, parent)
        emission_side = make_include_edge_key(parent, child, occurrence=0)
        assert graph_side == (emission_side,)

        expected = f"{escape_typst_string(parent)}#0>{escape_typst_string(child)}"
        assert emission_side == expected
        # Confirm the escaping actually fired (not merely passed through
        # unescaped, which the equality above alone would not catch if
        # escape_typst_string were a no-op).
        assert '\\"' in emission_side
        assert "\\\\" in emission_side

    def test_occurrence_defaults_to_zero(self):
        assert make_include_edge_key("index", "child") == "index#0>child"

    def test_occurrence_appears_verbatim_for_nonzero_values(self):
        assert make_include_edge_key("index", "child", occurrence=1) == (
            "index#1>child"
        )


# ---------------------------------------------------------------------------
# Publication rendering (render_include_edge_state) -- D-09/Pitfall 1
# ---------------------------------------------------------------------------


class TestRenderIncludeEdgeState:
    """``render_include_edge_state()``'s array-literal rendering rule,
    asserted structurally against ``49-EXPECTED-STRUCTURE.md``'s own
    contract template at arities 0-3."""

    def test_arity_0_renders_empty_array_literal(self):
        assert render_include_edge_state(()) == (
            f'#state("{INCLUDE_STATE_KEY}", ()).update(())'
        )

    def test_arity_1_renders_with_mandatory_trailing_comma(self):
        """The load-bearing case (D-09/RESEARCH Pitfall 1): omitting the
        trailing comma here would silently reparse the value as a
        parenthesized STRING, not a one-element array."""
        assert render_include_edge_state(("index#0>child",)) == (
            f'#state("{INCLUDE_STATE_KEY}", ()).update(("index#0>child",))'
        )

    def test_arity_2_renders_with_trailing_comma_after_last_element(self):
        assert render_include_edge_state(("index#0>a", "index#0>b")) == (
            f'#state("{INCLUDE_STATE_KEY}", ()).update(("index#0>a", "index#0>b",))'
        )

    def test_arity_3_renders_with_trailing_comma_after_last_element(self):
        assert render_include_edge_state(("index#0>a", "index#0>b", "index#0>c")) == (
            f'#state("{INCLUDE_STATE_KEY}", ()).update('
            '("index#0>a", "index#0>b", "index#0>c",))'
        )

    def test_uniform_rule_has_no_single_element_special_case(self):
        """The SAME construction rule -- append a trailing comma
        whenever the key count is >= 1, never when it is 0 -- is what
        licenses arity 1 not needing a distinct code path from arity 2/3
        (49-EVIDENCE.md Probe 3's own measurement)."""
        for n in (1, 2, 3):
            keys = tuple(f"index#0>k{i}" for i in range(n))
            rendered = render_include_edge_state(keys)
            assert rendered.endswith(",))"), rendered
            # 2 quotes for the state key itself, plus 2 per published key.
            assert rendered.count('"') == 2 + 2 * n


# ---------------------------------------------------------------------------
# Publication arity type/length readback -- the permanent trailing-comma
# hazard detector, driven against the PRODUCTION rendering function
# ---------------------------------------------------------------------------


def _typst_type_and_length_probe_text(tmp_path: Path, edge_keys: tuple) -> str:
    """Embed ``render_include_edge_state(edge_keys)``'s OWN return value
    (the production function's own output, not a hand-copied literal) in
    a small hand-written Typst probe that renders the published state's
    resolved Typst type and length, compile it for real, and return the
    ``pypdf``-extracted text. Mirrors ``49-EVIDENCE.md`` Probe 4's own
    methodology exactly."""
    state_line = render_include_edge_state(edge_keys)
    probe_source = tmp_path / "probe.typ"
    probe_source.write_text(
        f"{state_line}\n"
        f"#context [TYPE=#repr(type(state("
        f'"{INCLUDE_STATE_KEY}", ()).get())) '
        f'LEN=#state("{INCLUDE_STATE_KEY}", ()).get().len()]\n',
        encoding="utf-8",
    )
    pdf_path = tmp_path / "probe.pdf"
    typst.compile(str(probe_source), output=str(pdf_path))
    reader = pypdf.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() for page in reader.pages)


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the arity readback probe",
)
@pytest.mark.slow
class TestPublicationArityReadback:
    """The permanent detector for the trailing-comma hazard: at every
    arity 0-3, the PRODUCTION ``render_include_edge_state()``'s own
    output, compiled for real, resolves as Typst's ``array`` type with
    the expected length -- arity 1 is the load-bearing case (D-09/
    RESEARCH Pitfall 1; ``49-EVIDENCE.md`` Probes 4/5)."""

    @pytest.mark.parametrize(
        "edge_keys",
        [
            (),
            ("index#0>child",),
            ("index#0>a", "index#0>b"),
            ("index#0>a", "index#0>b", "index#0>c"),
        ],
        ids=["arity-0", "arity-1", "arity-2", "arity-3"],
    )
    def test_published_state_resolves_as_array_with_expected_length(
        self, tmp_path, edge_keys
    ):
        text = _typst_type_and_length_probe_text(tmp_path, edge_keys)
        assert "TYPE=array" in text, text
        assert f"LEN={len(edge_keys)}" in text, text


# ---------------------------------------------------------------------------
# Guard rendering (render_include_guard) -- RESEARCH Pitfall 2 / D-08
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_document():
    """A minimal docutils document, matching
    ``tests/test_toctree_requirement13.py``'s own fixture of the same
    name."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc


@pytest.fixture
def mock_builder():
    """A minimal mock builder carrying no Phase-49 state at all --
    matches ``tests/test_toctree_requirement13.py``'s own fixture of the
    same name, confirming a translator can be constructed without any
    builder-side mapping ever existing."""

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


class TestRenderIncludeGuard:
    """``render_include_guard()``'s one-line shape (RESEARCH Pitfall 2 /
    49-EVIDENCE.md Probe 7) and the translator's own per-document
    occurrence counter's fresh-instance state."""

    def test_condition_and_opening_brace_share_one_physical_line(self):
        """49-EVIDENCE.md Probe 7 measured a newline between the
        condition and its opening brace as a hard parser error
        (``expected block``) -- the returned template must never contain
        one."""
        guard = render_include_guard("index#0>child", "child")
        assert "\n" not in guard
        condition_and_brace = guard.split("{", 1)[0]
        assert "\n" not in condition_and_brace

    def test_guard_line_matches_emission_contract_template(self):
        guard = render_include_guard("index#0>child", "child")
        assert guard == (
            f'if "index#0>child" in state("{INCLUDE_STATE_KEY}", ()).get() '
            '{ include("child.typ") }'
        )

    def test_include_relpath_routes_through_escaping(self):
        """T-49-01's guard-side half of the escaping rule: the relative
        include path is routed through ``escape_typst_string()`` too, so
        a docname-derived path containing a quote or backslash still
        produces a valid literal."""
        guard = render_include_guard("index#0>child", 'sub"dir\\child')
        assert 'include("sub\\"dir\\\\child.typ")' in guard

    def test_fresh_translator_starts_with_empty_occurrence_counter(
        self, simple_document, mock_builder
    ):
        """A fresh ``TypstTranslator`` instance's own
        ``_toctree_entry_occurrences`` counter starts empty -- since
        ``TypstWriter.translate()`` constructs a fresh translator per
        document, this is what makes the counter per-document without an
        explicit reset anywhere in ``visit_toctree``."""
        translator = TypstTranslator(simple_document, mock_builder)
        assert translator._toctree_entry_occurrences == {}


# ---------------------------------------------------------------------------
# Builder derivation idempotency and non-mutation -- COMP-06
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not TYPST_AVAILABLE, reason="typst-py is required to build the fixture"
)
class TestBuilderDerivationContract:
    """``TypstBuilder._build_include_edge_map()`` is the ONE derivation
    function for the per-master edge mapping -- called twice, it returns
    equal mappings, and the mapping ``write()`` populates is unchanged
    from what a fresh re-derivation (taken AFTER the write phase
    completed) would produce, unlike the deleted ledger, which was
    mutated INSIDE the toctree visitor while writing."""

    def test_derivation_is_idempotent_and_unmutated_after_write(self, tmp_path):
        srcdir = FIXTURES_DIR / "state_guard_two_master_gate"
        outdir = tmp_path / "build"
        app = SphinxTestApp(buildername="typst", srcdir=srcdir, builddir=outdir)
        try:
            app.build()
            builder = app.builder

            first = builder._build_include_edge_map()
            second = builder._build_include_edge_map()
            assert first == second, (
                "calling _build_include_edge_map() twice must return " "equal mappings"
            )

            post_write_map = builder._master_include_edges
            fresh_map = builder._build_include_edge_map()
            assert post_write_map == fresh_map, (
                "the mapping write() populated must be unchanged from a "
                "fresh re-derivation taken after the write phase "
                "completed -- the deleted ledger was mutated DURING "
                "writing, this mapping must never be"
            )
            assert post_write_map, (
                "expected a non-empty mapping for a fixture with real " "toctrees"
            )
        finally:
            app.cleanup()

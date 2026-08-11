"""
Writer enumeration and generated survival matrix for `map_parameters()`'s
``authors`` precedence rule (originated Phase 44.2, D-05, gap-closure round
3; re-derived Phase 45.1, D-F, when the dedicated author-details config
value this module originally enumerated over was removed, CONF-10).

**The enumeration axis is the ASSIGNMENT TARGET `params["authors"]`, not any
config shape and not the mapping's SOURCE key.** Rounds 1 and 2 of this
correction both derived their search set from the vocabulary of the prose
being corrected -- round 1 enumerated config shapes ("package-alone build"),
round 2 enumerated the mapping's source key ("does the mapping map
`"author"`?") -- and both were falsified by a reachable configuration nobody
enumerated, because nobody was enumerating over the right axis. This module
walks `TemplateEngine.map_parameters()`'s own `ast` to find every site that
can write `params["authors"]`, and GENERATES its row set from the code's own
axes (source keys x target keys x source-presence) instead of typing rows by
hand -- typing them by hand is exactly how the falsifying row was omitted
twice.

**Phase 45.1 (D-F) update.** The dedicated author-details config value this
module used to enumerate a "seed" writer for is REMOVED (CONF-10). Rich
author structure now flows exclusively through `render()`'s
`typst_template_function["params"]` route (D-B), never through a write
inside `map_parameters()` itself. This method's `params["authors"]` write
surface is therefore just the TWO surviving writers: the mapping loop
(reachable whenever some `parameter_mapping` entry's target is literally
`"authors"` with its source key present in the passed `sphinx_metadata`)
and the non-package back-fill (`params["authors"] = ()`, reachable
whenever the mapping loop did not write the key AND `typst_package` is
unset). The generated matrix below drops its former "does the seed
survive" framing and asserts this simpler, seed-free rule instead.

**Deliberate deviation from this phase's established test-module convention.**
`44.2-PATTERNS.md` prescribes discrete, individually-named functions over
`@pytest.mark.parametrize` for this phase's sibling precedence module,
`tests/test_entry_metadata_precedence.py` -- and that module keeps the
discrete convention. This module deviates from that convention on purpose:
a hand-enumerated row set is exactly the failure mode this module exists
to close, so `test_authors_mapping_loop_matrix` below is parametrized over
a MECHANICALLY GENERATED cross product rather than typed out cell by cell,
so a rule one predicate short of the code cannot be transcribed into
`_mapping_loop_writes_authors()` without turning a row red.
"""

import ast
import itertools
import re
from pathlib import Path

import pytest
from sphinx.errors import ExtensionError

from typsphinx.template_engine import ELEMENTS_ALLOWLIST, TemplateEngine

REPO_ROOT = Path(__file__).resolve().parents[1]

TEMPLATE_ENGINE_PATH = REPO_ROOT / "typsphinx" / "template_engine.py"
CONFIGURATION_RST_PATH = (
    REPO_ROOT / "docs" / "source" / "user_guide" / "configuration.rst"
)

BASE_METADATA = {"project": "P", "author": "Explicit Entry Author", "release": "1.0"}

# Three source keys and three target keys -- deliberately wider than the
# "author"/"authors" pair the two falsified rules were framed around.
SOURCE_KEYS = ("author", "project", "release")
# "authors" itself, "doc_authors" (which the mapping loop's
# `_convert_to_authors_tuple` special-cases by TARGET name), and "writer"
# (which it does not) -- so a surviving-and-also-landing cell cannot be read
# as an artifact of that conversion special case.
TARGET_KEYS = ("authors", "doc_authors", "writer")


def _mapping_loop_writes_authors(mapping: dict, metadata: dict) -> bool:
    """Transcribes the PUBLISHED sentence into Python -- this is a
    transcription of the rule stated in `docs/source/user_guide/configuration.rst`
    and in `typsphinx/template_engine.py`'s D-05 comment (re-derived per
    D-F once the seed this rule used to be framed against was removed), and
    must stay readable as such. Its body makes no call to
    `map_parameters()`, `TemplateEngine`, or any other production entry
    point: deriving the expected value from the code under test would make
    the matrix below a tautology that passes for ANY rule, including the
    two already measured false against rows F and G of
    `44.2-orchestrator-measurement.md`.

    `params["authors"]` is written by the mapping loop iff some mapping
    entry has the target key "authors" with its source key present in
    `metadata`.
    """
    return any(
        target == "authors" and source in metadata for source, target in mapping.items()
    )


def _map_parameters_ast() -> ast.FunctionDef:
    """Parse `TEMPLATE_ENGINE_PATH` and return the `FunctionDef` node for
    `TemplateEngine.map_parameters` -- the sole source of truth the writer
    enumeration below is built from."""
    tree = ast.parse(TEMPLATE_ENGINE_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "map_parameters":
            return node
    raise AssertionError("map_parameters() not found in typsphinx/template_engine.py")


def _params_assignments() -> tuple[list[str], set[str]]:
    """Walk `map_parameters()` and collect every `Assign` whose target is a
    `Subscript` on `Name(id="params")` -- the ASSIGNMENT-TARGET enumeration
    that grounds every other test in this module. Returns the literal-string
    slices in source order, and the set of dynamic `Name` slice ids."""
    func = _map_parameters_ast()
    literal_slices: list[str] = []
    dynamic_slices: set[str] = set()
    for node in ast.walk(func):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not (
                isinstance(target, ast.Subscript)
                and isinstance(target.value, ast.Name)
                and target.value.id == "params"
            ):
                continue
            slice_node = target.slice
            if isinstance(slice_node, ast.Constant) and isinstance(
                slice_node.value, str
            ):
                literal_slices.append(slice_node.value)
            elif isinstance(slice_node, ast.Name):
                dynamic_slices.add(slice_node.id)
    return literal_slices, dynamic_slices


def _map_parameters_region() -> str:
    """Return the source text of `map_parameters()` sliced by the function's
    own `lineno`/`end_lineno` -- the region the D-05 comment drift guard
    reads. Scoping to this region (rather than the whole file) is what lets
    `uses_bundled_default_template()`'s docstring keep using "package-alone"
    ACCURATELY, about a different subject, without tripping this guard."""
    func = _map_parameters_ast()
    lines = TEMPLATE_ENGINE_PATH.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[func.lineno - 1 : func.end_lineno])


def test_map_parameters_writes_params_from_exactly_these_sites():
    """AST enumeration of every `params[...]` write site in
    `map_parameters()`. This is the sole authority the published precedence
    rule, the D-05 comment, and `_mapping_loop_writes_authors()` above must
    all be re-derived from -- not the reverse.

    Phase 45.1 (D-F): the leading `"authors"` literal-slice write this
    module used to expect FIRST -- the removed config value's seed -- is
    gone. `map_parameters()` now has exactly ONE literal `"authors"` write
    (the non-package back-fill), in the back-fill's own source order:
    title, authors, date."""
    literal_slices, dynamic_slices = _params_assignments()

    consequence = (
        "map_parameters() gained or lost a params[...] write site. A new "
        "writer of params[...] appeared in map_parameters(), so the "
        "published precedence rule in "
        "docs/source/user_guide/configuration.rst, the D-05 comment in "
        "typsphinx/template_engine.py, and this module's "
        "_mapping_loop_writes_authors() must all be re-derived before this "
        "expectation is changed."
    )

    assert literal_slices == ["title", "authors", "date"], consequence
    assert dynamic_slices == {"template_key", "key"}, consequence


def test_typst_elements_cannot_write_the_authors_key():
    """The `typst_elements` loop cannot reach `params["authors"]`:
    `ELEMENTS_ALLOWLIST` is `papersize`/`fontsize`/`lang`, and an unknown key
    raises `ExtensionError` before it is ever added to `params`."""
    assert "authors" not in ELEMENTS_ALLOWLIST
    assert sorted(ELEMENTS_ALLOWLIST) == ["fontsize", "lang", "papersize"]

    engine = TemplateEngine()

    with pytest.raises(ExtensionError):
        engine.map_parameters({}, typst_elements={"authors": "x"})


def test_non_package_back_fill_cannot_replace_a_mapping_loop_write():
    """The non-package back-fill (`if not self.typst_package: ... if
    "authors" not in params: params["authors"] = ()`) is guarded by
    `"authors" not in params`, so it can only fill an ABSENT key and can
    never overwrite a value the mapping loop already wrote. A non-package
    engine whose mapping does not target "authors" gets the empty-tuple
    back-fill; the same engine's mapping RETARGETED to write "authors"
    keeps the mapped value instead -- the back-fill never runs at all."""
    engine_no_mapping_write = TemplateEngine(parameter_mapping={"project": "title"})
    params_no_mapping_write = engine_no_mapping_write.map_parameters(
        dict(BASE_METADATA)
    )
    assert params_no_mapping_write["authors"] == ()

    engine_with_mapping_write = TemplateEngine(parameter_mapping={"author": "authors"})
    params_with_mapping_write = engine_with_mapping_write.map_parameters(
        dict(BASE_METADATA)
    )
    assert params_with_mapping_write["authors"] == (BASE_METADATA["author"],)


def test_default_mapping_targets_the_authors_key():
    """`DEFAULT_PARAMETER_MAPPING` is the ordinary-build instance of the
    rule: its `"author"` entry targets `"authors"`, so on an unconfigured
    build the seed is overwritten whenever `sphinx_metadata["author"]` is
    present -- which `writer.py` always supplies."""
    assert TemplateEngine.DEFAULT_PARAMETER_MAPPING["author"] == "authors"


_MATRIX_CASES = [
    pytest.param(
        source,
        target,
        present,
        id=f"{source}-to-{target}-{'present' if present else 'absent'}",
    )
    for source, target, present in itertools.product(
        SOURCE_KEYS, TARGET_KEYS, (True, False)
    )
]


@pytest.mark.parametrize("source,target,present", _MATRIX_CASES)
def test_authors_mapping_loop_matrix(source, target, present):
    """The GENERATED cross product `SOURCE_KEYS x TARGET_KEYS x
    {present, absent}` -- 18 cells, including the two shapes with zero
    prior coverage anywhere in the suite: `project -> authors` (a
    non-author source writing "authors" via the mapping loop) and
    `author -> writer` (an author source routed away from "authors",
    falling through to the non-package back-fill instead -- the control
    proving a mapping-loop write is not an artifact of the "doc_authors"
    tuple-conversion special case).

    Each cell asserts against `_mapping_loop_writes_authors()`, never
    against the code under test: whether the mapping loop wrote "authors",
    and when it did not, that the non-package back-fill's empty-tuple
    default is what landed instead (this module's engine never sets
    `typst_package`, so the back-fill always runs when the mapping loop
    did not pre-empt it); when the mapping loop DID write "authors" with a
    non-"authors" target and the source present, that the target key
    landed in `params` too (presence only -- the mapped value's shape
    depends on `_convert_to_authors_tuple`'s own special casing, a
    separate concern from this precedence rule)."""
    mapping = {source: target}
    metadata = (
        dict(BASE_METADATA)
        if present
        else {key: value for key, value in BASE_METADATA.items() if key != source}
    )

    engine = TemplateEngine(parameter_mapping=mapping)
    params = engine.map_parameters(metadata)

    mapping_writes = _mapping_loop_writes_authors(mapping, metadata)

    if mapping_writes:
        assert params["authors"] == (metadata[source],)
    else:
        assert params["authors"] == ()

    if target != "authors" and source in metadata:
        assert target in params


def test_configuration_rst_documents_both_target_key_shapes():
    """Drift guard: the published Precedence paragraph in
    `configuration.rst` states the target-key rule and illustrates it with
    both `{"author": "doc_authors"}` (a source routed AWAY from "authors")
    and `{"project": "authors"}` (a non-author source routed INTO it) --
    exactly the two shapes the two earlier published rules mispredicted.
    Whitespace is collapsed before matching, so a re-wrap of the paragraph
    cannot fool this guard; a revert to a source-key framing goes red
    here.

    Phase 45.1 (D-E) re-derivation: the exact "no entry ... targets
    authors" phrasing came from the pre-CONF-11 two-stage precedence model
    and no longer appears verbatim now that the section is written around
    a single up-front exclusivity branch, but the same target-key rule
    survives in the rewritten prose ("It is the *target* key that
    decides, not whether ``"author"`` appears in the mapping at all") --
    this guard now pins that surviving sentence instead."""
    text = CONFIGURATION_RST_PATH.read_text(encoding="utf-8")
    normalized = re.sub(r"\s+", " ", text)

    for needle in (
        "It is the *target* key that decides, not whether",
        '{"author": "doc_authors"}',
        '{"project": "authors"}',
    ):
        assert needle in normalized, f"MISSING from configuration.rst: {needle}"


def test_d05_comment_states_the_surviving_writer_rule():
    """Drift guard, region-scoped to `map_parameters()` so an accurate
    "package-alone" sentence elsewhere in the same file (e.g.
    `uses_bundled_default_template()`'s docstring, about template-file
    ROUTING, a different subject) is never mistaken for an instance of this
    rule.

    Phase 45.1 (D-F) re-derivation: the seed-survival rule this guard used
    to pin (`target key "authors"` phrasing plus two illustrating mapping
    literals) is gone along with the seed itself. The surviving comment
    must still state the mapping loop's own target-key write rule and
    record that the removal happened per CONF-10/D-F."""
    region = _map_parameters_region()
    normalized = re.sub(r"\s+", " ", region)

    assert 'is literally "authors"' in normalized
    assert "CONF-10/D-F" in normalized

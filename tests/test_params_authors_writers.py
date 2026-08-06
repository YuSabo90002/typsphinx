"""
Writer enumeration and generated survival matrix for CONF-09's `typst_authors`
precedence rule (Phase 44.2, D-05, gap-closure round 3).

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

**The rule** (measured against `map_parameters()`, stated over the target):
the `typst_authors` seed at `params["authors"]` survives if and only if no
entry of the active `parameter_mapping` has the target key `"authors"` with
its source key present in the passed `sphinx_metadata`. The SOURCE key does
not have to be `"author"`, and its presence is neither necessary nor
sufficient: `{"author": "doc_authors"}` keeps the seed in `"authors"` AND
passes the mapped value under `"doc_authors"`, while `{"project": "authors"}`
destroys the seed with the project name despite never mentioning `"author"`
at all.

**Deliberate deviation from this phase's established test-module convention.**
`44.2-PATTERNS.md` prescribes discrete, individually-named functions over
`@pytest.mark.parametrize` for this phase's sibling precedence module,
`tests/test_entry_metadata_precedence.py` -- and that module keeps the
discrete convention, gaining its own four named Group 2 cells in plan 05
task 2. This module deviates from that convention on purpose: a hand-
enumerated row set is exactly the failure mode this module exists to
close, so `test_authors_seed_survival_matrix` below is parametrized over a
MECHANICALLY GENERATED cross product rather than typed out cell by cell,
so a rule one predicate short of the code cannot be transcribed into
`_seed_survives()` without turning a row red.
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
CONFIGURATION_RST_PATH = REPO_ROOT / "docs" / "source" / "user_guide" / "configuration.rst"

TYPST_AUTHORS = {"Jane Doe": {"organization": "MIT"}}
SEED = [{"name": "Jane Doe", "organization": "MIT"}]
BASE_METADATA = {"project": "P", "author": "Explicit Entry Author", "release": "1.0"}

# Three source keys and three target keys -- deliberately wider than the
# "author"/"authors" pair the two falsified rules were framed around.
SOURCE_KEYS = ("author", "project", "release")
# "authors" itself, "doc_authors" (which the mapping loop's
# `_convert_to_authors_tuple` special-cases by TARGET name), and "writer"
# (which it does not) -- so a surviving-and-also-landing cell cannot be read
# as an artifact of that conversion special case.
TARGET_KEYS = ("authors", "doc_authors", "writer")


def _seed_survives(mapping: dict, metadata: dict) -> bool:
    """Transcribes the PUBLISHED sentence into Python -- this is a
    transcription of the rule stated in `docs/source/user_guide/configuration.rst`
    and in `typsphinx/template_engine.py`'s D-05 comment, and must stay
    readable as such. Its body makes no call to `map_parameters()`,
    `TemplateEngine`, or any other production entry point: deriving the
    expected value from the code under test would make the matrix below a
    tautology that passes for ANY rule, including the two already measured
    false against rows F and G of `44.2-orchestrator-measurement.md`.

    The seed at `params["authors"]` survives iff no mapping entry has the
    target key "authors" with its source key present in `metadata`.
    """
    return not any(
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
            if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
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
    rule, the D-05 comment, and `_seed_survives()` above must all be
    re-derived from -- not the reverse."""
    literal_slices, dynamic_slices = _params_assignments()

    consequence = (
        "map_parameters() gained or lost a params[...] write site. A new "
        "writer of params[...] appeared in map_parameters(), so the "
        "published precedence rule in "
        "docs/source/user_guide/configuration.rst, the D-05 comment in "
        "typsphinx/template_engine.py, and this module's _seed_survives() "
        "must all be re-derived before this expectation is changed."
    )

    assert literal_slices == ["authors", "title", "authors", "date"], consequence
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


def test_non_package_back_fill_cannot_replace_a_typst_authors_seed():
    """The non-package back-fill (`if not self.typst_package: ... if
    "authors" not in params: params["authors"] = ()`) is guarded by
    `"authors" not in params`, so it can only fill an ABSENT key and can
    never replace a seed. A non-package engine with no `typst_authors`
    yields the empty-tuple back-fill; the same engine WITH `typst_authors`
    keeps the seed instead."""
    engine_no_seed = TemplateEngine(parameter_mapping={"project": "title"})
    params_no_seed = engine_no_seed.map_parameters(dict(BASE_METADATA))
    assert params_no_seed["authors"] == ()

    engine_with_seed = TemplateEngine(
        parameter_mapping={"project": "title"}, typst_authors=TYPST_AUTHORS
    )
    params_with_seed = engine_with_seed.map_parameters(dict(BASE_METADATA))
    assert params_with_seed["authors"] == SEED


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
    for source, target, present in itertools.product(SOURCE_KEYS, TARGET_KEYS, (True, False))
]


@pytest.mark.parametrize("source,target,present", _MATRIX_CASES)
def test_authors_seed_survival_matrix(source, target, present):
    """The GENERATED cross product `SOURCE_KEYS x TARGET_KEYS x
    {present, absent}` -- 18 cells, including the two shapes with zero
    prior coverage anywhere in the suite: `project -> authors` (a
    non-author source destroying the seed) and `author -> writer` (an
    author source routed away from "authors" keeping the seed and landing
    under an unrelated key, the control proving survival is not an
    artifact of the "doc_authors" tuple-conversion special case).

    Each cell asserts against `_seed_survives()`, never against the code
    under test: whether the seed survives, and when it does not,
    that `params["authors"]` is the mapped value rather than the seed; when
    it survives with a non-"authors" target and the source present, that
    the target key landed in `params` too (presence only -- the mapped
    value's shape depends on `_convert_to_authors_tuple`'s own special
    casing, a separate concern from this precedence rule)."""
    mapping = {source: target}
    metadata = (
        dict(BASE_METADATA)
        if present
        else {key: value for key, value in BASE_METADATA.items() if key != source}
    )

    engine = TemplateEngine(parameter_mapping=mapping, typst_authors=TYPST_AUTHORS)
    params = engine.map_parameters(metadata)

    survives = _seed_survives(mapping, metadata)
    assert (params["authors"] == SEED) is survives

    if not survives:
        assert params["authors"] == (metadata[source],)
    elif target != "authors" and source in metadata:
        assert target in params


def test_configuration_rst_documents_both_target_key_shapes():
    """Drift guard: the published Precedence paragraph in
    `configuration.rst` states the target-key rule and illustrates it with
    both `{"author": "doc_authors"}` (a source routed AWAY from "authors")
    and `{"project": "authors"}` (a non-author source routed INTO it) --
    exactly the two shapes the two earlier published rules mispredicted.
    Whitespace is collapsed before matching, so a re-wrap of the paragraph
    cannot fool this guard; a revert to a source-key framing goes red
    here."""
    text = CONFIGURATION_RST_PATH.read_text(encoding="utf-8")
    normalized = re.sub(r"\s+", " ", text)

    for needle in (
        "no entry of the active mapping targets ``authors``",
        '{"author": "doc_authors"}',
        '{"project": "authors"}',
    ):
        assert needle in normalized, f"MISSING from configuration.rst: {needle}"


def test_d05_comment_states_the_target_key_rule():
    """Drift guard, region-scoped to `map_parameters()` so an accurate
    "package-alone" sentence elsewhere in the same file (e.g.
    `uses_bundled_default_template()`'s docstring, about template-file
    ROUTING, a different subject) is never mistaken for an instance of this
    rule: the D-05 comment still states the target-key phrasing and both
    illustrating mapping literals."""
    region = _map_parameters_region()
    normalized = re.sub(r"\s+", " ", region)

    assert 'target key "authors"' in normalized
    assert '{"author": "doc_authors"}' in normalized
    assert '{"project": "authors"}' in normalized

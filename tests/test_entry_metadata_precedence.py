"""
Full element-semantics and precedence matrix for CONF-09 (Phase 44.2, SC#2).

Turns plan 01's implemented `_resolve_entry_element()` rules into asserted
contract instead of happy-path-only coverage. Three groups, each pinning the
decisions its cells name:

- Element semantics (D-01 / D-02): direct, no-Sphinx-app calls to
  `_resolve_entry_element()` -- present str (including ``""``, D-01: an
  empty string is a value, not a fallback signal), absent/short/`None`
  (silent fallback, D-02), non-`str` (warn then fallback, D-02), no-match,
  malformed-entry-skip, five-element arity, and duplicate-docname
  first-match.
- Precedence inside `map_parameters()` (D-05; re-derived Phase 45.1, D-F,
  once the dedicated author-details config value this group originally
  exercised was removed, CONF-10): `params["authors"]` is written by the
  mapping loop if and only if some entry of the active `parameter_mapping`
  has the target key `"authors"` with its source key present in the passed
  `sphinx_metadata`; when no entry does, the non-package back-fill supplies
  an empty tuple (or, on the package route, the key is absent entirely).
  The decisive thing is the mapping's TARGET, not its source key and not
  the template route -- `{"author": "doc_authors"}` routes the mapped
  value under `doc_authors` instead of `authors`, while `{"project":
  "authors"}` writes the project name into `authors` despite never
  mentioning `"author"`. One cell below per row; the writer enumeration
  this rule is derived from lives in `tests/test_params_authors_writers.py`.
- Precedence inside `render()` (D-04, re-derived onto D-B/Phase 45.1): an
  explicit `typst_template_function["params"]` value wins over the
  entry-derived params dict passed into `render()` -- not because it wins
  a per-key collision (D-04's original, additive-union mechanism, removed
  by Phase 45.1's D-B), but because declaring `params` discards the
  entry-derived dict WHOLESALE via `render()`'s exclusive branch
  (`self.typst_template_params_specified`). The externally observable
  result Group 3's cells assert (`params["title"]`/`params["authors"]`
  values win) is unchanged; only the mechanism is.

Mirrors `tests/test_builder_output_stem.py`'s granularity: one short,
individually-named function per matrix cell -- discrete functions, not a
single table-driven pytest marker block.
"""

from typsphinx.template_engine import TemplateEngine
from typsphinx.writer import _resolve_entry_element

# ---------------------------------------------------------------------------
# Group 1: element semantics (D-01 / D-02), direct _resolve_entry_element()
# calls -- pure function, no Sphinx app / no build.
# ---------------------------------------------------------------------------


def test_resolve_entry_element_present_str_title():
    """A present, non-empty str element (index 2, title) is returned
    verbatim."""
    entries = [("index", "out", "T", "A")]

    assert _resolve_entry_element(entries, "index", 2, "default") == "T"


def test_resolve_entry_element_present_str_author():
    """A present, non-empty str element (index 3, author) is returned
    verbatim."""
    entries = [("index", "out", "T", "A")]

    assert _resolve_entry_element(entries, "index", 3, "default") == "A"


def test_resolve_entry_element_empty_string_title_is_a_value():
    """D-01: an empty-string title element is a VALUE, not a fallback
    signal -- equality against "", not a truthiness check."""
    entries = [("index", "out", "", "")]

    result = _resolve_entry_element(entries, "index", 2, "default")

    assert result == ""


def test_resolve_entry_element_empty_string_author_is_a_value():
    """D-01: an empty-string author element is a VALUE, not a fallback
    signal -- equality against "", not a truthiness check."""
    entries = [("index", "out", "", "")]

    result = _resolve_entry_element(entries, "index", 3, "default")

    assert result == ""


def test_resolve_entry_element_short_tuple_falls_back_silently(caplog):
    """D-02: a tuple too short to have index 3 falls back to default,
    silently -- no WARNING record."""
    entries = [("index", "out", "T")]

    with caplog.at_level("WARNING"):
        result = _resolve_entry_element(entries, "index", 3, "default")

    assert result == "default"
    assert [r for r in caplog.records if r.levelname == "WARNING"] == []


def test_resolve_entry_element_two_element_tuple_falls_back_silently(caplog):
    """D-02: a two-element tuple (no title, no author) falls back to
    default, silently."""
    entries = [("index", "out")]

    with caplog.at_level("WARNING"):
        result = _resolve_entry_element(entries, "index", 2, "default")

    assert result == "default"
    assert [r for r in caplog.records if r.levelname == "WARNING"] == []


def test_resolve_entry_element_none_element_falls_back_silently(caplog):
    """D-02: an explicit `None` element falls back to default, silently."""
    entries = [("index", "out", None, None)]

    with caplog.at_level("WARNING"):
        result = _resolve_entry_element(entries, "index", 2, "default")

    assert result == "default"
    assert [r for r in caplog.records if r.levelname == "WARNING"] == []


def test_resolve_entry_element_non_str_warns_and_falls_back(caplog):
    """D-02: a non-str element falls back to default AND emits exactly one
    WARNING whose message names the element index and the docname."""
    entries = [("index", "out", 123, "A")]

    with caplog.at_level("WARNING"):
        result = _resolve_entry_element(entries, "index", 2, "default")

    assert result == "default"
    warnings = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) == 1
    message = warnings[0].getMessage()
    assert "index" in message
    assert "[2]" in message


def test_resolve_entry_element_no_matching_docname_falls_back_silently(caplog):
    """D-02: a typst_documents entry that names a DIFFERENT docname does
    not match; the lookup falls back to default, silently."""
    entries = [("other", "out", "T", "A")]

    with caplog.at_level("WARNING"):
        result = _resolve_entry_element(entries, "index", 2, "default")

    assert result == "default"
    assert [r for r in caplog.records if r.levelname == "WARNING"] == []


def test_resolve_entry_element_empty_typst_documents_falls_back_silently(caplog):
    """D-02: an empty typst_documents list falls back to default,
    silently."""
    with caplog.at_level("WARNING"):
        result = _resolve_entry_element([], "index", 2, "default")

    assert result == "default"
    assert [r for r in caplog.records if r.levelname == "WARNING"] == []


def test_resolve_entry_element_malformed_entry_skipped_then_matched():
    """edge: a malformed, empty entry appearing BEFORE the real match is
    skipped rather than indexed -- the walk continues to the entry that
    actually matches."""
    entries = [(), ("index", "out", "T", "A")]

    assert _resolve_entry_element(entries, "index", 2, "default") == "T"


def test_resolve_entry_element_five_element_tuple_resolves_unchanged():
    """edge (arity): a 5-element entry resolves [2] and [3] identically to
    a 4-element entry -- the fifth element is accepted and ignored by this
    helper."""
    entries = [("index", "out", "T", "A", "typst")]

    assert _resolve_entry_element(entries, "index", 2, "default") == "T"
    assert _resolve_entry_element(entries, "index", 3, "default") == "A"


def test_resolve_entry_element_duplicate_docname_first_match_wins():
    """Edge (first-match): when two typst_documents entries name the same
    docname, the FIRST is used, silently -- the same convention
    `_resolve_output_stem` already follows. This pins the EXISTING
    first-match convention only; it is NOT coverage of the adjacent,
    out-of-scope duplicate-TARGET-name defect (a different bug about two
    entries sharing a *target*, not a *docname*). Note: `render_wrapper()`
    (Phase 47) deliberately does NOT use this first-match convention for a
    wrapper's own title/author -- see `_entry_element_value()`, which reads
    a specific entry positionally instead (D-08)."""
    entries = [
        ("index", "a", "First", "A1"),
        ("index", "b", "Second", "A2"),
    ]

    assert _resolve_entry_element(entries, "index", 2, "default") == "First"


def test_entry_element_value_two_entries_same_docname_resolve_independently():
    """Phase 47 (D-08): `render_wrapper()`'s positional read
    (`_entry_element_value()`) is the counterpart to the first-match test
    above -- two `typst_documents` entries naming the SAME docname each
    resolve their OWN `[2]` (title) and `[3]` (author) independently,
    unlike `_resolve_entry_element()`'s first-match scan. Wrapper
    generation order never decides metadata: passing the SECOND entry
    resolves the SECOND entry's own values, not the first's."""
    from typsphinx.writer import _entry_element_value

    first_entry = ("index", "a", "First", "A1")
    second_entry = ("index", "b", "Second", "A2")

    assert _entry_element_value(first_entry, 2, "default") == "First"
    assert _entry_element_value(first_entry, 3, "default") == "A1"
    assert _entry_element_value(second_entry, 2, "default") == "Second"
    assert _entry_element_value(second_entry, 3, "default") == "A2"


# ---------------------------------------------------------------------------
# Group 2: precedence inside TemplateEngine.map_parameters() (D-05;
# re-derived Phase 45.1, D-F, once the dedicated author-details config value
# this group originally exercised as a "seed" was removed, CONF-10).
#
# The full condition, stated over the ASSIGNMENT TARGET: params["authors"]
# is written by the mapping loop iff some entry of the active
# parameter_mapping has the target key "authors" with its source key
# present in the passed sphinx_metadata. When no entry does, the
# non-package back-fill supplies an empty tuple (guarded by
# "authors" not in params); on the package route with no such mapping
# entry, "authors" is absent from the output entirely (self.typst_package
# gates the back-fill). One cell below per row of that rule, including a
# source key routed AWAY from "authors" and a non-author source key routed
# INTO it.
# ---------------------------------------------------------------------------


def test_map_parameters_default_mapping_author_reaches_authors():
    """D-05: on the default-mapping route, DEFAULT_PARAMETER_MAPPING's own
    "author" -> "authors" entry writes the mapped/converted author value
    (a tuple) into params["authors"]."""
    engine = TemplateEngine()
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    params = engine.map_parameters(sphinx_metadata)

    assert isinstance(params["authors"], tuple)
    assert params["authors"] == ("Explicit Entry Author",)


def test_map_parameters_package_mapping_omitting_author_yields_no_authors_key():
    """D-05: on the package route, a custom mapping that omits "author"
    means the mapping loop never writes "authors" -- and because
    self.typst_package is set, the non-package back-fill never runs
    either, so the "authors" key is ABSENT from the output entirely (there
    is no seed left to fall back on)."""
    engine = TemplateEngine(
        typst_package="@preview/charged-ieee:0.1.4",
        parameter_mapping={"project": "title"},
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    params = engine.map_parameters(sphinx_metadata)

    assert "authors" not in params


def test_map_parameters_non_package_mapping_omitting_author_falls_back_to_empty_tuple():
    """D-05: the surviving condition is the MAPPING, not the package. A
    NON-package engine (typst_package is None) whose explicitly-set
    parameter_mapping omits "author" falls through to the non-package
    back-fill, which supplies an empty tuple -- there is no
    self.typst_package conditional anywhere in the mapping loop itself, so
    a template-route build with an author-omitting mapping differs from
    the package route above only in whether the back-fill runs at all."""
    engine = TemplateEngine(
        parameter_mapping={"project": "title"},
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    assert engine.typst_package is None
    assert "author" not in engine.parameter_mapping

    params = engine.map_parameters(sphinx_metadata)

    assert params["authors"] == ()


def test_map_parameters_package_unset_mapping_yields_no_authors_key():
    """D-05: the route reached by __init__'s package branch resolving the
    mapping to an EMPTY dict rather than to DEFAULT_PARAMETER_MAPPING --
    typst_package is set and parameter_mapping is not passed at all.
    Distinct from the cell above it, which supplies an explicit mapping
    that happens to omit "author": here there is no custom mapping at
    all, only __init__'s own empty-dict resolution -- and because the
    package route skips the back-fill too, "authors" is absent."""
    engine = TemplateEngine(
        typst_package="@preview/charged-ieee:0.1.4",
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    assert engine.parameter_mapping == {}

    params = engine.map_parameters(sphinx_metadata)

    assert "authors" not in params


def test_map_parameters_custom_mapping_with_author_reaches_authors():
    """D-05: the control proving the mapping loop's write fires on the
    mapping's TARGET key being "authors", not on the mapping being
    DEFAULT_PARAMETER_MAPPING. A CUSTOM mapping that routes "author" to
    "authors" writes the mapped value with no package involved at all.
    Read against
    test_map_parameters_author_mapped_to_non_authors_target_falls_back_to_empty_tuple
    below, which changes only the target key and flips the outcome."""
    engine = TemplateEngine(
        parameter_mapping={"project": "title", "author": "authors"},
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    params = engine.map_parameters(sphinx_metadata)

    assert params["authors"] == ("Explicit Entry Author",)


def test_map_parameters_author_absent_from_metadata_falls_back_to_empty_tuple():
    """D-05: pins the source-presence half of the rule -- the mapping loop
    can only write a key whose source it can read. A default-mapping
    engine (whose "author" entry does target "authors") falls through to
    the non-package back-fill when the passed sphinx_metadata carries no
    "author" key at all. This shape is not reachable from a real
    sphinx-build -- writer.py always supplies "author" via
    _resolve_entry_element -- but map_parameters() is a public method and
    the D-05 comment states this half of the condition, so it gets a test
    pinning the public contract."""
    engine = TemplateEngine()
    sphinx_metadata = {
        "project": "P",
        "release": "1.0",
    }

    assert engine.parameter_mapping["author"] == "authors"

    params = engine.map_parameters(sphinx_metadata)

    assert params["authors"] == ()


def test_map_parameters_author_mapped_to_non_authors_target_falls_back_to_empty_tuple():
    """D-05: the decisive thing is the mapping's TARGET key -- "author"
    being an active source key is neither necessary nor sufficient. A
    mapping that routes "author" to "doc_authors" instead of "authors"
    leaves the mapping loop's own "authors" write unfired, so the
    non-package back-fill supplies an empty tuple, while the mapped
    author value lands separately under "doc_authors".
    tests/test_config_template_mapping.py already exercises this mapping
    as a realistic custom-template configuration (Requirement 8.4)."""
    engine = TemplateEngine(
        parameter_mapping={"project": "title", "author": "doc_authors"},
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    assert engine.parameter_mapping["author"] == "doc_authors"

    params = engine.map_parameters(sphinx_metadata)

    assert params["authors"] == ()
    assert params["doc_authors"] == ("Explicit Entry Author",)


def test_map_parameters_author_mapped_to_arbitrary_target_falls_back_to_empty_tuple():
    """D-05: the companion control for the cell above -- "doc_authors" is
    special-cased by the mapping loop's author-tuple conversion and
    "writer" is not, so the outcome cannot be an artifact of that special
    case. A mapping that routes "author" to "writer" still falls back to
    the empty-tuple default for "authors", with the mapped value landing
    under "writer"."""
    engine = TemplateEngine(
        parameter_mapping={"project": "title", "author": "writer"},
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    params = engine.map_parameters(sphinx_metadata)

    assert params["authors"] == ()
    assert "writer" in params


def test_map_parameters_non_author_source_mapped_to_authors_writes_mapped_value():
    """D-05: the row that pins the target-key-only rule most sharply -- the
    mapping mentions "author" nowhere, yet "authors" is written anyway,
    with the project name as its value rather than any author value. A
    template declaring an "authors" parameter would therefore render the
    project name as its author."""
    engine = TemplateEngine(
        parameter_mapping={"project": "authors"},
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    assert "author" not in engine.parameter_mapping

    params = engine.map_parameters(sphinx_metadata)

    assert params["authors"] == ("P",)


def test_map_parameters_release_mapped_to_authors_writes_mapped_value():
    """D-05: a second non-author source inside a mapping that also maps
    something else, so the previous cell's result cannot be read as an
    artifact of a single-entry mapping."""
    engine = TemplateEngine(
        parameter_mapping={"release": "authors", "project": "title"},
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    assert "author" not in engine.parameter_mapping

    params = engine.map_parameters(sphinx_metadata)

    assert params["authors"] == ("1.0",)
    assert params["title"] == "P"


# ---------------------------------------------------------------------------
# Group 3: precedence inside TemplateEngine.render() (D-04, re-derived onto
# D-B / Phase 45.1).
# ---------------------------------------------------------------------------


def test_render_explicit_template_function_title_wins_over_entry_derived():
    """D-B (Phase 45.1) re-derivation of D-04: an explicit
    typst_template_function["params"]["title"] is the ONLY title in the
    emitted call -- not because it wins a per-key collision against the
    entry-derived title (D-04's original additive-union mechanism, removed
    by D-B), but because declaring "params" discards the entry-derived
    params dict WHOLESALE via render()'s exclusive branch
    (self.typst_template_params_specified)."""
    engine = TemplateEngine(
        typst_template_function={
            "name": "project",
            "params": {"title": "Explicit Title"},
        },
    )
    params = {"title": "Entry Derived Title", "authors": ()}

    result = engine.render(params, "Content")

    assert '"Explicit Title"' in result
    assert "Entry Derived Title" not in result
    # D-B: the entry-derived "authors" key -- not itself a declared params
    # key -- is discarded too, not merely absent because it lost a
    # collision. Scoped to the show-rule call region: the bundled default
    # template is inlined by render() and its OWN function signature
    # declares an "authors: ()," default parameter, which would otherwise
    # make an unscoped substring check on `result` a false positive.
    call_region = result[result.index("#show: project.with(") :]
    assert "authors:" not in call_region


def test_render_explicit_template_function_authors_wins_over_entry_derived():
    """D-B (Phase 45.1) re-derivation of D-04: same as above, for an
    explicit ["authors"] -- the entry-derived "title" is discarded too."""
    engine = TemplateEngine(
        typst_template_function={
            "name": "project",
            "params": {"authors": ("Explicit Author",)},
        },
    )
    params = {"title": "T", "authors": ("Entry Derived Author",)}

    result = engine.render(params, "Content")

    assert '"Explicit Author"' in result
    assert "Entry Derived Author" not in result
    # D-B: scoped to the call region for the same reason as the sibling
    # test above -- the inlined bundled template's own function signature
    # declares a "title: """," default parameter.
    call_region = result[result.index("#show: project.with(") :]
    assert "title:" not in call_region


def test_render_template_function_authors_replaces_map_parameters_derived_value():
    """The combination ``44.2-VERIFICATION.md`` measured as having no
    single-assertion coverage anywhere in the suite: the two cells above
    both hand-build their ``params`` dict and call ``render()`` directly,
    so neither exercises a REAL, non-empty ``map_parameters()`` output
    that is then replaced at render time -- only a hand-built dict
    standing in for whatever ``map_parameters()`` might have produced.

    This cell spans both stages in one body. First it calls
    ``map_parameters()`` with a mapping that explicitly targets "authors"
    with the entry-derived "author" as its source (so the mapping loop
    legitimately writes a real, non-empty tuple into ``params["authors"]``)
    and asserts that write landed. Only then does it call ``render()`` and
    assert the emitted string carries the ``typst_template_function``
    value and not the mapping-derived one. Asserting the mapping-derived
    write first is what makes the second half mean "replaced at render
    time" rather than "never written in the first place".

    Phase 45.1 (D-F) re-derivation: this cell used to need a dedicated
    author-details config value's seed SURVIVING ``map_parameters()`` to
    supply that real, non-empty value; that config value is removed
    (CONF-10), so the mapping loop's own write is the surviving way to
    produce one.

    D-B (Phase 45.1) re-derivation of D-04: the mapping-derived value
    reaches ``params`` (via ``map_parameters()``, unchanged) but never
    reaches ``all_params`` at all -- ``render()``'s exclusive branch
    discards the WHOLE ``map_parameters()`` output the moment
    ``typst_template_function["params"]`` is declared, rather than the
    mapping-derived value reaching ``all_params`` first and then losing an
    ``update()`` collision (D-04's original, now-removed mechanism)."""
    engine = TemplateEngine(
        parameter_mapping={"author": "authors"},
        typst_template_function={
            "name": "project",
            "params": {"authors": ("FROM TEMPLATE FUNCTION",)},
        },
    )

    params = engine.map_parameters(
        {"project": "P", "author": "Explicit Entry Author", "release": "1.0"}
    )
    assert params["authors"] == ("Explicit Entry Author",)

    result = engine.render(params, "Content")

    assert '"FROM TEMPLATE FUNCTION"' in result
    assert "Explicit Entry Author" not in result

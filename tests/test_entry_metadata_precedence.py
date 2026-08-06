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
- Precedence inside `map_parameters()` (D-05): a mapped author value beats
  the `typst_authors` seed exactly when `"author"` is an active
  `parameter_mapping` key AND is present in the passed `sphinx_metadata`;
  otherwise the seed survives. The condition is the mapping, not the
  template route, so the seed survives both when `typst_package` is set
  with no `typst_template_mapping` at all and when an explicitly-set
  mapping omits `"author"` on any route.
- Precedence inside `render()` (D-04): an explicit
  `typst_template_function["params"]` value wins over the entry-derived
  params dict passed into `render()` -- pinning that D-04 needs no new
  code, only the existing `all_params.update(params)` then
  `all_params.update(self.typst_template_params)` merge order.

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
    `_is_master_document` and `_resolve_output_stem` already follow. This
    pins the EXISTING first-match convention only; it is NOT coverage of
    the adjacent, out-of-scope duplicate-TARGET-name defect (a different
    bug about two entries sharing a *target*, not a *docname*)."""
    entries = [
        ("index", "a", "First", "A1"),
        ("index", "b", "Second", "A2"),
    ]

    assert _resolve_entry_element(entries, "index", 2, "default") == "First"


# ---------------------------------------------------------------------------
# Group 2: precedence inside TemplateEngine.map_parameters() (D-05).
#
# The full condition: a mapped author value overwrites the typst_authors
# seed exactly when "author" is an active parameter_mapping key AND
# "author" is present in the passed sphinx_metadata. The trigger is the
# mapping key, never self.typst_package -- so the seed survives on BOTH
# (a) typst_package set with parameter_mapping left None (__init__
# resolves that to an empty dict) and (b) an explicit parameter_mapping
# that omits "author", package or not. One cell below per shape.
# ---------------------------------------------------------------------------


def test_map_parameters_default_mapping_author_beats_typst_authors():
    """D-05: on the default-mapping route, the mapped author value
    overwrites the typst_authors seed -- params["authors"] is the
    mapped/converted author value (a tuple), NOT the typst_authors
    list[dict]."""
    engine = TemplateEngine(
        typst_authors={
            "Jane Doe": {"organization": "MIT", "email": "jane@mit.edu"},
        },
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    params = engine.map_parameters(sphinx_metadata)

    assert isinstance(params["authors"], tuple)
    assert params["authors"] == ("Explicit Entry Author",)


def test_map_parameters_custom_mapping_omitting_author_keeps_typst_authors():
    """D-05: on a route whose custom mapping omits "author" -- here a
    package route, though the package is incidental, not the trigger --
    typst_authors survives as the sole source -- params["authors"] IS the
    typst_authors list[dict]."""
    engine = TemplateEngine(
        typst_package="@preview/charged-ieee:0.1.4",
        parameter_mapping={"project": "title"},
        typst_authors={
            "Jane Doe": {"organization": "MIT", "email": "jane@mit.edu"},
        },
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    params = engine.map_parameters(sphinx_metadata)

    assert isinstance(params["authors"], list)
    assert params["authors"][0]["name"] == "Jane Doe"


def test_map_parameters_non_package_mapping_omitting_author_keeps_typst_authors():
    """D-05: the surviving condition is the MAPPING, not the package. This
    is the exact cell 44.2-VERIFICATION.md reproduced against shipped code
    and that had no test -- a NON-package engine (typst_package is None)
    whose explicitly-set parameter_mapping omits "author" still keeps
    typst_authors as the sole source. The published rule previously named
    a package build as the only surviving route; there is no
    self.typst_package conditional anywhere in map_parameters(), so a
    template-route build with an author-omitting mapping behaves
    identically. Without this cell, the published rule could claim a
    package was required without any assertion going red."""
    engine = TemplateEngine(
        parameter_mapping={"project": "title"},
        typst_authors={
            "Jane Doe": {"organization": "MIT", "email": "jane@mit.edu"},
        },
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    assert engine.typst_package is None
    assert "author" not in engine.parameter_mapping

    params = engine.map_parameters(sphinx_metadata)

    assert isinstance(params["authors"], list)
    assert params["authors"][0]["name"] == "Jane Doe"


def test_map_parameters_package_unset_mapping_keeps_typst_authors():
    """D-05: the route reached by __init__'s package branch resolving the
    mapping to an EMPTY dict rather than to DEFAULT_PARAMETER_MAPPING --
    typst_package is set and parameter_mapping is not passed at all.
    Distinct from the cell above it, which supplies an explicit mapping
    that happens to omit "author": here there is no custom mapping at
    all, only __init__'s own empty-dict resolution."""
    engine = TemplateEngine(
        typst_package="@preview/charged-ieee:0.1.4",
        typst_authors={
            "Jane Doe": {"organization": "MIT", "email": "jane@mit.edu"},
        },
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    assert engine.parameter_mapping == {}

    params = engine.map_parameters(sphinx_metadata)

    assert isinstance(params["authors"], list)
    assert params["authors"][0]["name"] == "Jane Doe"


def test_map_parameters_custom_mapping_with_author_beats_typst_authors():
    """D-05: the control proving the trigger is the presence of the
    "author" key, not whether the mapping happens to be
    DEFAULT_PARAMETER_MAPPING. A CUSTOM mapping that explicitly maps
    "author" still overwrites the typst_authors seed, with no package
    involved at all."""
    engine = TemplateEngine(
        parameter_mapping={"project": "title", "author": "authors"},
        typst_authors={
            "Jane Doe": {"organization": "MIT", "email": "jane@mit.edu"},
        },
    )
    sphinx_metadata = {
        "project": "P",
        "author": "Explicit Entry Author",
        "release": "1.0",
    }

    params = engine.map_parameters(sphinx_metadata)

    assert params["authors"] == ("Explicit Entry Author",)


def test_map_parameters_author_absent_from_metadata_keeps_typst_authors():
    """D-05: pins the SECOND conjunct -- the mapping loop can only
    overwrite a key it can read. A default-mapping engine (which DOES
    map "author") still keeps the typst_authors seed when the passed
    sphinx_metadata carries no "author" key at all. This shape is not
    reachable from a real sphinx-build -- writer.py always supplies
    "author" via _resolve_entry_element -- but map_parameters() is a
    public method and the corrected D-05 comment states this conjunct,
    so it gets a test pinning the public contract."""
    engine = TemplateEngine(
        typst_authors={
            "Jane Doe": {"organization": "MIT", "email": "jane@mit.edu"},
        },
    )
    sphinx_metadata = {
        "project": "P",
        "release": "1.0",
    }

    assert engine.parameter_mapping["author"] == "authors"

    params = engine.map_parameters(sphinx_metadata)

    assert isinstance(params["authors"], list)
    assert params["authors"][0]["name"] == "Jane Doe"


# ---------------------------------------------------------------------------
# Group 3: precedence inside TemplateEngine.render() (D-04).
# ---------------------------------------------------------------------------


def test_render_explicit_template_function_title_wins_over_entry_derived():
    """D-04: an explicit typst_template_function["params"]["title"] still
    wins over the entry-derived title passed into render() -- the entry
    elements are arguments to the standard call, and a user who named both
    the function and its arguments is not overridden. Needs no code: this
    is the existing all_params.update(params) then
    all_params.update(self.typst_template_params) merge."""
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


def test_render_explicit_template_function_authors_wins_over_entry_derived():
    """D-04: same as above, for an explicit ["authors"]."""
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

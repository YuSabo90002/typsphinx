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
  a `typst_authors` seed on the default-mapping route; `typst_authors`
  survives only on a custom-mapping route that omits `"author"`.
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
    """D-05: on a package-alone route whose custom mapping omits "author",
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

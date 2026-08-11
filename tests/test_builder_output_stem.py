"""
Tests for TypstBuilder._resolve_output_stem (Phase 22 Plan 01, Issue #117).

Covers the typst_documents target-name normalization rule: suffix
stripping (D-03), period-preserving stems (D-04), the D-02 docname
fallback, the D-06/D-07 path guard, the degenerate-target guard, and
verbatim non-ASCII passthrough.

CR-01's collision guard (Phase 44 plan 05) was deleted from
``_resolve_output_stem`` in Phase 47 plan 09 (its own D-03 -- distinct
from this module's pre-existing D-03 above): collision detection moved
wholesale to ``TypstBuilder._validate_output_path_collisions()``, run once
before any write. ``_resolve_output_stem`` now returns a colliding stem
UNCHANGED rather than falling back to the docname; the tests below prove
the responsibility moved rather than disappeared -- one pair proving the
resolver no longer performs the check, one pair proving the validator now
does. A builder whose env exposes no found_docs attribute at all still
resolves normally.
"""


def test_resolve_output_stem_strips_trailing_typ_suffix(temp_sphinx_app):
    """D-03: a literal trailing '.typ' is stripped from the target."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "output.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "output"


def test_resolve_output_stem_accepts_extensionless_target(temp_sphinx_app):
    """D-03/D-04: an extension-less target is valid input, no warning."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "typsphinx", "T", "A")]

    assert builder._resolve_output_stem("index") == "typsphinx"


def test_resolve_output_stem_preserves_period_in_stem(temp_sphinx_app):
    """D-04: a period-bearing stem is never truncated by splitext."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "v1.2-manual", "T", "A")]

    assert builder._resolve_output_stem("index") == "v1.2-manual"


def test_resolve_output_stem_preserves_period_in_stem_with_suffix(temp_sphinx_app):
    """D-04: same as above, target additionally carries a '.typ' suffix."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "v1.2-manual.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "v1.2-manual"


def test_resolve_output_stem_identity_target_is_unchanged(temp_sphinx_app):
    """Identity mapping ('index' -> 'index') is byte-identical -- the
    ~60-fixture non-regression baseline."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "index", "T", "A")]

    assert builder._resolve_output_stem("index") == "index"


def test_resolve_output_stem_accepts_five_element_tuple(temp_sphinx_app):
    """The 5-element form used by docs/source/conf.py resolves the same
    as the 4-element form."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "output", "T", "A", "typst")]

    assert builder._resolve_output_stem("index") == "output"


def test_resolve_output_stem_falls_back_to_docname_when_unlisted(temp_sphinx_app):
    """D-02: a docname with no typst_documents entry is returned
    unchanged, no warning (toctree-included children keep docname)."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "output.typ", "T", "A")]

    assert builder._resolve_output_stem("chapter1/section") == "chapter1/section"


def test_resolve_output_stem_falls_back_when_config_missing(temp_sphinx_app):
    """D-02: empty and None typst_documents both fall back to docname."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    builder.config.typst_documents = []
    assert builder._resolve_output_stem("index") == "index"

    builder.config.typst_documents = None
    assert builder._resolve_output_stem("index") == "index"


def test_resolve_output_stem_resolves_posix_path_bearing_target(temp_sphinx_app):
    """OUT-01 reverses Phase 44's D-06/D-07: a POSIX-separator-bearing
    target is no longer refused. It resolves exactly where written --
    'sub/manual.typ' on docname 'index' resolves to 'sub/manual', with NO
    warning."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "sub/manual.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "sub/manual"


def test_resolve_output_stem_normalizes_backslash_path_bearing_target(
    temp_sphinx_app,
):
    """OUT-01 reverses Phase 44's D-06/D-07: a Windows-authored backslash
    target is still recognised as a PATH on POSIX (where os.sep is '/' and
    os.altsep is None) -- it is simply no longer refused, and resolves to
    the same normalized 'sub/manual' as its forward-slash equivalent, with
    no warning."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "sub\\manual.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "sub/manual"


def test_resolve_output_stem_guards_parent_traversal(temp_sphinx_app):
    """D-06/D-07: a '..' segment reduces to the basename.

    OUT-02 (kept): this is one of the three escape-shaped terms OUT-01
    does NOT reverse. Per RESEARCH.md Pitfall 4's own warning sign, this
    assertion STILL PASSING after OUT-01 landed is confirming evidence
    that only the separator-membership term was reversed, not this one.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "../manual", "T", "A")]

    assert builder._resolve_output_stem("index") == "manual"


def test_resolve_output_stem_guards_absolute_target(temp_sphinx_app):
    """D-06/D-07: an absolute target reduces to the basename.

    OUT-02 (kept): this is one of the three escape-shaped terms OUT-01
    does NOT reverse. Per RESEARCH.md Pitfall 4's own warning sign, this
    assertion STILL PASSING after OUT-01 landed is confirming evidence
    that only the separator-membership term was reversed, not this one.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "/abs/manual.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "manual"


def test_resolve_output_stem_guards_drive_qualified_target(temp_sphinx_app):
    """D-06/D-07: a drive-qualified target reduces to the basename,
    detected on POSIX too.

    OUT-02 (kept): this is one of the three escape-shaped terms OUT-01
    does NOT reverse. Per RESEARCH.md Pitfall 4's own warning sign, this
    assertion STILL PASSING after OUT-01 landed is confirming evidence
    that only the separator-membership term was reversed, not this one.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "C:manual.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "manual"


def test_resolve_output_stem_falls_back_on_empty_target(temp_sphinx_app):
    """edge: empty -- an empty-string target falls back to the docname
    and warns."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "", "T", "A")]

    assert builder._resolve_output_stem("index") == "index"


def test_resolve_output_stem_falls_back_on_bare_typ_target(temp_sphinx_app):
    """edge: empty -- a bare '.typ' target has an empty stem after
    stripping and must never produce a file literally named '.typ'."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", ".typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "index"


def test_resolve_output_stem_falls_back_on_whitespace_target(temp_sphinx_app):
    """edge: empty -- a whitespace-only target falls back to the
    docname."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "   ", "T", "A")]

    assert builder._resolve_output_stem("index") == "index"


def test_resolve_output_stem_falls_back_on_short_tuple(temp_sphinx_app):
    """edge: empty -- a typst_documents tuple shorter than 2 elements
    falls back to the docname without raising IndexError."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index",)]

    assert builder._resolve_output_stem("index") == "index"


def test_resolve_output_stem_falls_back_on_non_str_target(temp_sphinx_app):
    """edge: empty -- a non-str target value falls back to the docname
    without raising AttributeError."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", None, "T", "A")]

    assert builder._resolve_output_stem("index") == "index"


def test_resolve_output_stem_preserves_non_ascii_target(temp_sphinx_app):
    """edge: encoding -- a non-ASCII target survives verbatim; no
    Unicode normalization, case folding, or transliteration."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "マニュアル.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "マニュアル"


def test_resolve_output_stem_emits_no_warning_for_path_bearing_target(
    temp_sphinx_app, caplog
):
    """OUT-01 reverses Phase 44's D-06/D-07: a path-bearing, non-escaping
    target no longer triggers the "a path is not supported" warning at
    all -- it resolves exactly where written, silently, the same as any
    other non-degenerate, non-escaping target."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "sub/manual.typ", "T", "A")]

    with caplog.at_level("WARNING"):
        stem = builder._resolve_output_stem("index")

    assert stem == "sub/manual"
    assert not any(
        "a path is not supported in a typst_documents target name"
        in record.getMessage()
        for record in caplog.records
    )


def test_resolve_output_stem_warns_on_degenerate_target(temp_sphinx_app, caplog):
    """The degenerate-target warning names the docname it falls back
    to."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "", "T", "A")]

    with caplog.at_level("WARNING"):
        stem = builder._resolve_output_stem("index")

    assert stem == "index"
    assert any(
        "empty typst_documents target name" in record.getMessage()
        and "index" in record.getMessage()
        for record in caplog.records
    )


def test_resolve_output_stem_warns_once_on_path_bearing_target_with_empty_basename(
    temp_sphinx_app, caplog
):
    """WR-03: a path-bearing target whose basename is itself empty (a
    trailing separator) must emit exactly ONE warning -- the "empty
    target" fallback -- not the path-guard warning followed by a second,
    confusing "using '' instead" warning."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "sub/manual.typ/", "T", "A")]

    with caplog.at_level("WARNING"):
        stem = builder._resolve_output_stem("index")

    assert stem == "index"
    warnings = [record.getMessage() for record in caplog.records]
    assert len(warnings) == 1
    assert "empty typst_documents target name" in warnings[0]
    assert "index" in warnings[0]
    assert "using '' instead" not in warnings[0]


def test_wrapper_path_ignores_docname_directory_but_content_path_does_not(
    temp_sphinx_app,
):
    """OUT-01 reverses Phase 44's D-05: a nested docname's WRAPPER path is
    no longer force-relocated into that docname's own directory --
    ('sub/index', 'manual.typ', ...) resolves the WRAPPER at the output
    ROOT, 'manual', NOT 'sub/manual'. `_directory_preserving_relpath()`'s
    old forcing behavior is gone from the wrapper-path computation (it
    survives only inside `_resolve_output_stem`'s own pre-OUT-01-shaped
    CR-01 collision comparison, 47-09's territory).

    The companion assertion: the same docname's own CONTENT path is
    unaffected by any of this -- content files are unconditionally
    docname-derived (COMP-01/OUT-03), so 'sub/index' always writes its
    content at 'sub/index.typ' regardless of what its wrapper's target
    says.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("sub/index", "manual.typ", "T", "A")]

    entry = builder.config.typst_documents[0]
    assert builder._wrapper_output_relpath(entry) == "manual"

    content_path = builder._content_output_path("sub/index").replace("\\", "/")
    assert content_path.endswith("sub/index.typ")


def test_resolve_output_stem_no_longer_falls_back_on_docname_collision(
    temp_sphinx_app,
):
    """Phase 47 plan 09's D-03: collision detection moved from
    _resolve_output_stem() to _validate_output_path_collisions() -- the
    responsibility moved, it did not disappear. A resolved stem equal to
    another real docname's own content path is now returned UNCHANGED (no
    in-function fallback); the collision itself is now reported by
    test_validate_output_path_collisions_raises_on_docname_collision
    below."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "chapter1.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "chapter1"


def test_validate_output_path_collisions_raises_on_docname_collision(
    temp_sphinx_app,
):
    """Phase 47 plan 09's D-03: the collision _resolve_output_stem() no
    longer catches is caught by _validate_output_path_collisions()
    instead -- a resolved wrapper stem equal to another real docname's own
    content path raises ExtensionError. The env is replaced with a
    types.SimpleNamespace so the test is independent of whether the Sphinx
    version in use exposes found_docs as a plain attribute and independent
    of whether a read phase has run."""
    import types

    import pytest
    from sphinx.errors import ExtensionError

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.env = types.SimpleNamespace(found_docs={"index", "chapter1"})
    builder.config.typst_documents = [("index", "chapter1.typ", "T", "A")]

    with pytest.raises(ExtensionError):
        builder._validate_output_path_collisions()


def test_resolve_output_stem_no_longer_falls_back_on_reserved_template_name(
    temp_sphinx_app,
):
    """Phase 47 plan 09's D-03: same responsibility move as above, for the
    reserved "_template" basename -- _resolve_output_stem() now returns
    the resolved stem UNCHANGED rather than falling back to the docname."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "_template.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "_template"


def test_validate_output_path_collisions_raises_on_reserved_template_name(
    temp_sphinx_app,
):
    """Phase 47 plan 09's D-03: the reserved "_template" collision is
    caught by _validate_output_path_collisions(), independent of
    found_docs membership -- the reservation is inserted into the
    collision map first, unconditionally."""
    import types

    import pytest
    from sphinx.errors import ExtensionError

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.env = types.SimpleNamespace(found_docs={"index", "chapter1"})
    builder.config.typst_documents = [("index", "_template.typ", "T", "A")]

    with pytest.raises(ExtensionError):
        builder._validate_output_path_collisions()


def test_resolve_output_stem_tolerates_env_without_found_docs(temp_sphinx_app):
    """CR-01 regression guard: a builder whose env exposes NO found_docs
    attribute at all (matching tests/conftest.py's mock_builder-shaped
    MockEnv) still resolves normally via the getattr fallback, without
    raising AttributeError."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.env = object()
    builder.config.typst_documents = [("index", "manual.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "manual"

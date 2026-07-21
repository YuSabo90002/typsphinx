"""
Tests for TypstBuilder._resolve_output_stem (Phase 22 Plan 01, Issue #117).

Covers the typst_documents target-name normalization rule: suffix
stripping (D-03), period-preserving stems (D-04), the D-02 docname
fallback, the D-06/D-07 path guard, the degenerate-target guard, and
verbatim non-ASCII passthrough.
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


def test_resolve_output_stem_guards_posix_path_separator(temp_sphinx_app):
    """D-06/D-07: a POSIX-separator-bearing target reduces to its
    basename and warns exactly once."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "sub/manual.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "manual"


def test_resolve_output_stem_guards_backslash_path_separator(temp_sphinx_app):
    """D-06/D-07: a Windows-authored backslash target is detected even
    on POSIX, where os.sep is '/' and os.altsep is None."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "sub\\manual.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "manual"


def test_resolve_output_stem_guards_parent_traversal(temp_sphinx_app):
    """D-06/D-07: a '..' segment reduces to the basename."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "../manual", "T", "A")]

    assert builder._resolve_output_stem("index") == "manual"


def test_resolve_output_stem_guards_absolute_target(temp_sphinx_app):
    """D-06/D-07: an absolute target reduces to the basename."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "/abs/manual.typ", "T", "A")]

    assert builder._resolve_output_stem("index") == "manual"


def test_resolve_output_stem_guards_drive_qualified_target(temp_sphinx_app):
    """D-06/D-07: a drive-qualified target reduces to the basename,
    detected on POSIX too."""
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


def test_resolve_output_stem_warns_on_path_bearing_target(temp_sphinx_app, caplog):
    """The path-guard warning names the offending target and the
    basename that will actually be written."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("index", "sub/manual.typ", "T", "A")]

    with caplog.at_level("WARNING"):
        stem = builder._resolve_output_stem("index")

    assert stem == "manual"
    assert any(
        "a path is not supported in a typst_documents target name"
        in record.getMessage()
        and "sub/manual.typ" in record.getMessage()
        and "manual" in record.getMessage()
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

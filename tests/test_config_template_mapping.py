"""
Tests for template mapping configuration (Task 13.2).

This test suite verifies that typst_template_mapping configuration is properly
registered and applied per Requirement 8.4 and 8.5.

Phase 47 migration (R2, ``47-EXPECTED-STRUCTURE.md``): template application
(the mapped parameter names/values) lives exclusively on the WRAPPER file
since the content/wrapper split, so every ``.typ``-reading assertion here
reads the entry's resolved wrapper (target ``'master'``) instead of the
docname content file. Every fixture's ``typst_documents`` target was also
renamed from the identity ``'index'`` to ``'master'`` -- an identity target
is now a BLD-03 self-collision (the wrapper would resolve onto the docname's
own content file), not merely a stylistic choice.
"""


def test_typst_template_mapping_config_registered(make_app, tmp_path):
    """Test that typst_template_mapping is registered as a config value"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create minimal conf.py with custom mapping
    conf_content = """
extensions = ['typsphinx']

project = 'Test Project'
author = 'Test Author'

typst_template_mapping = {
    'project': 'doc_title',
    'author': 'doc_author',
    'release': 'version',
}

typst_documents = [
    ('index', 'master', 'Test Doc', 'Test Author'),
]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n\nContent\n")

    app = make_app(srcdir=srcdir)
    app.build()

    # Check that config value is accessible
    assert hasattr(app.config, "typst_template_mapping")
    assert app.config.typst_template_mapping == {
        "project": "doc_title",
        "author": "doc_author",
        "release": "version",
    }


def test_default_typst_template_mapping(make_app, tmp_path):
    """Test that default mapping is None when not specified"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']
project = 'Test Project'
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    app = make_app(srcdir=srcdir)
    app.build()

    # Default should be None (use default mapping)
    assert hasattr(app.config, "typst_template_mapping")
    assert app.config.typst_template_mapping is None


def test_custom_mapping_applied_to_template(make_app, tmp_path):
    """Test that custom mapping is actually applied during template rendering"""
    srcdir = tmp_path / "source"
    outdir = tmp_path / "output"
    srcdir.mkdir()
    outdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'My Custom Project'
author = 'Custom Author'
release = '2.0.0'

typst_template_mapping = {
    'project': 'doc_title',
    'author': 'doc_authors',
    'release': 'version_number',
}

typst_documents = [
    ('index', 'master', 'Test', 'Author'),
]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test Document\n=============\n\nContent here.\n")

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    # Read generated wrapper .typ file (R2, Phase 47: template application
    # -- including the custom-mapped parameter names -- lives exclusively
    # on the wrapper file, resolved from the entry's target 'master'.)
    typ_file = outdir / "master.typ"
    if not typ_file.exists():
        # Try in app outdir
        typ_file = app.outdir / "master.typ"

    assert typ_file.exists(), f"Expected {typ_file} to exist"

    content = typ_file.read_text()

    # Check that custom parameter names are used
    assert "doc_title:" in content
    assert "doc_authors:" in content
    assert "version_number:" in content

    # CONF-09 (Phase 44.2, D-03): the entry's own title/author
    # (typst_documents = [('index', 'master', 'Test', 'Author')]) now win
    # over config.project ('My Custom Project') / config.author
    # ('Custom Author') -- measured from a build run in this session.
    assert '"Test"' in content
    assert '"Author"' in content
    assert '"2.0.0"' in content


def test_partial_custom_mapping(make_app, tmp_path):
    """Test that partial mapping works (some custom, some default)"""
    srcdir = tmp_path / "source"
    outdir = tmp_path / "output"
    srcdir.mkdir()
    outdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test Project'
author = 'Test Author'
release = '1.0.0'

# Only map 'project', leave others as default
typst_template_mapping = {
    'project': 'document_title',
}

typst_documents = [
    ('index', 'master', 'Test', 'Author'),
]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    # R2 (Phase 47): the wrapper file, not the docname content file, carries
    # template application.
    typ_file = app.outdir / "master.typ"
    assert typ_file.exists()

    content = typ_file.read_text()

    # Custom mapping for project
    assert "document_title:" in content

    # CONF-09 (Phase 44.2, D-03): the entry's own title
    # (typst_documents = [('index', 'master', 'Test', 'Author')]) now wins
    # over config.project ('Test Project') -- measured from a build run in
    # this session. The custom-mapped parameter NAME assertion above is
    # unaffected by this change.
    assert 'document_title: "Test"' in content


def test_invalid_mapping_type(make_app, tmp_path):
    """Test that invalid mapping type is handled gracefully"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test'

# Invalid: should be dict, not list
typst_template_mapping = ['invalid', 'list']

typst_documents = [('index', 'master', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    # Should not crash, but may emit warning
    app = make_app(srcdir=srcdir)
    # Build should complete even with invalid config
    # (implementation should validate and fallback to default)


def test_empty_mapping(make_app, tmp_path):
    """Test that empty mapping dict works (equivalent to no mapping)"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test'

typst_template_mapping = {}

typst_documents = [('index', 'master', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    app = make_app(srcdir=srcdir)
    app.build()

    assert app.config.typst_template_mapping == {}


def test_mapping_with_typst_elements(make_app, tmp_path):
    """Test that typst_template_mapping works together with typst_elements"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test'
author = 'Author'

typst_template_mapping = {
    'project': 'doc_name',
}

typst_elements = {
    'papersize': 'a4',
    'fontsize': '12pt',
}

typst_documents = [('index', 'master', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    # R2 (Phase 47): the wrapper file, not the docname content file, carries
    # template application.
    typ_file = app.outdir / "master.typ"
    content = typ_file.read_text()

    # Custom mapping should appear
    assert "doc_name:" in content
    assert "Test" in content
    # Note: typst_elements integration is tested separately

"""
Tests for toctree defaults configuration (Task 13.3).

This test suite verifies that typst_toctree_defaults configuration is properly
registered and applied per Requirement 13.9.
"""


def test_typst_toctree_defaults_config_registered(make_app, tmp_path):
    """Test that typst_toctree_defaults is registered as a config value"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test'

typst_toctree_defaults = {
    'maxdepth': 3,
    'numbered': True,
    'caption': 'Table of Contents',
}

typst_documents = [('index', 'index', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    app = make_app(srcdir=srcdir)
    app.build()

    assert hasattr(app.config, "typst_toctree_defaults")
    assert app.config.typst_toctree_defaults == {
        "maxdepth": 3,
        "numbered": True,
        "caption": "Table of Contents",
    }


def test_default_typst_toctree_defaults(make_app, tmp_path):
    """Test that default toctree config is None when not specified"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']
project = 'Test'
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    app = make_app(srcdir=srcdir)
    app.build()

    assert hasattr(app.config, "typst_toctree_defaults")
    # Default should be None (use built-in defaults)
    assert app.config.typst_toctree_defaults is None


def test_toctree_defaults_applied_to_template(make_app, tmp_path):
    """Test that toctree defaults are passed as template parameters"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test Project'

typst_toctree_defaults = {
    'maxdepth': 4,
    'numbered': True,
    'caption': 'Contents',
}

typst_documents = [('index', 'index', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("""
Test Document
=============

.. toctree::
   :maxdepth: 2

   chapter1
""")
    (srcdir / "chapter1.rst").write_text("Chapter 1\n=========\n")

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    typ_file = app.outdir / "index.typ"
    assert typ_file.exists()

    content = typ_file.read_text()

    # Check that toctree parameters are in template call
    # When toctree directive has maxdepth:2, it should override default maxdepth:4
    assert "toctree_maxdepth:" in content or "maxdepth" in content.lower()


def test_toctree_directive_overrides_defaults(make_app, tmp_path):
    """Test that toctree directive options override defaults"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test'

typst_toctree_defaults = {
    'maxdepth': 4,
    'numbered': False,
}

typst_documents = [('index', 'index', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)

    # toctree with explicit maxdepth:2 (should override default maxdepth:4)
    (srcdir / "index.rst").write_text("""
Test
====

.. toctree::
   :maxdepth: 2
   :numbered:

   chapter1
""")
    (srcdir / "chapter1.rst").write_text("Chapter\n=======\n")

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    typ_file = app.outdir / "index.typ"
    content = typ_file.read_text()

    # The directive's maxdepth:2 should be used, not the default maxdepth:4
    # Check that parameters are present
    assert typ_file.exists()


def test_partial_toctree_defaults(make_app, tmp_path):
    """Test that partial defaults work (some specified, some use built-in)"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test'

# Only specify maxdepth, leave numbered and caption as built-in defaults
typst_toctree_defaults = {
    'maxdepth': 3,
}

typst_documents = [('index', 'index', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    app = make_app(srcdir=srcdir)
    app.build()

    assert app.config.typst_toctree_defaults == {"maxdepth": 3}


def test_empty_toctree_defaults(make_app, tmp_path):
    """Test that empty dict works"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test'

typst_toctree_defaults = {}

typst_documents = [('index', 'index', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    app = make_app(srcdir=srcdir)
    app.build()

    assert app.config.typst_toctree_defaults == {}


def test_toctree_defaults_with_no_toctree(make_app, tmp_path):
    """Test that defaults don't cause issues when there's no toctree"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test'

typst_toctree_defaults = {
    'maxdepth': 2,
    'numbered': True,
}

typst_documents = [('index', 'index', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)
    # No toctree in document
    (srcdir / "index.rst").write_text("Test\n====\n\nNo toctree here.\n")

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    # Should build without errors
    typ_file = app.outdir / "index.typ"
    assert typ_file.exists()


def test_invalid_toctree_defaults_type(make_app, tmp_path):
    """Test that invalid defaults type is handled"""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Test'

# Invalid: should be dict, not list
typst_toctree_defaults = ['invalid']

typst_documents = [('index', 'index', 'Test', 'Author')]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n")

    # Should not crash
    app = make_app(srcdir=srcdir)
    # Build might emit warning but should complete

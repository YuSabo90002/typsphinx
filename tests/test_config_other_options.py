"""
Tests for other configuration options (Task 13.4)

Requirements tested:
- Requirement 8.6: Typst Universe packages specification
- Requirement 10: Debug mode (SPHINX_TYPST_DEBUG)
- Output directory configuration
"""


def test_typst_package_config_registered(make_app, tmp_path):
    """Test that typst_package is registered as a config value"""
    # Arrange: Create conf.py with typst_package setting
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
typst_package = "@preview/diagraph:0.2.5"
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Config value should be accessible and correct
    assert hasattr(app.config, "typst_package")
    assert app.config.typst_package == "@preview/diagraph:0.2.5"


def test_typst_package_imports_config_registered(make_app, tmp_path):
    """Test that typst_package_imports is registered as a config value"""
    # Arrange: Create conf.py with typst_package_imports setting
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
typst_package_imports = [
    '#import "@preview/diagraph:0.2.5": *',
    '#import "@preview/tablex:0.1.0": *',
]
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Config value should be accessible and correct
    assert hasattr(app.config, "typst_package_imports")
    expected = [
        '#import "@preview/diagraph:0.2.5": *',
        '#import "@preview/tablex:0.1.0": *',
    ]
    assert app.config.typst_package_imports == expected


def test_typst_template_function_config_registered(make_app, tmp_path):
    """Test that typst_template_function is registered as a config value"""
    # Arrange: Create conf.py with typst_template_function setting
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
typst_template_function = "custom_template"
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Config value should be accessible and correct
    assert hasattr(app.config, "typst_template_function")
    assert app.config.typst_template_function == "custom_template"


def test_typst_package_default_none(make_app, tmp_path):
    """Test that typst_package defaults to None when not set"""
    # Arrange: Create conf.py without typst_package
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Default should be None
    assert hasattr(app.config, "typst_package")
    assert app.config.typst_package is None


def test_typst_package_imports_default_none(make_app, tmp_path):
    """Test that typst_package_imports defaults to None when not set"""
    # Arrange: Create conf.py without typst_package_imports
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Default should be None
    assert hasattr(app.config, "typst_package_imports")
    assert app.config.typst_package_imports is None


def test_typst_template_function_default_none(make_app, tmp_path):
    """Test that typst_template_function defaults to None when not set"""
    # Arrange: Create conf.py without typst_template_function
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Default should be None
    assert hasattr(app.config, "typst_template_function")
    assert app.config.typst_template_function is None


def test_typst_output_dir_config_registered(make_app, tmp_path):
    """Test that typst_output_dir is registered as a config value"""
    # Arrange: Create conf.py with typst_output_dir setting
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
typst_output_dir = '_custom/typst'
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Config value should be accessible and correct
    assert hasattr(app.config, "typst_output_dir")
    assert app.config.typst_output_dir == "_custom/typst"


def test_typst_output_dir_default_value(make_app, tmp_path):
    """Test that typst_output_dir defaults to '_build/typst' when not set"""
    # Arrange: Create conf.py without typst_output_dir
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Default should be '_build/typst'
    assert hasattr(app.config, "typst_output_dir")
    assert app.config.typst_output_dir == "_build/typst"


def test_typst_debug_config_registered(make_app, tmp_path):
    """Test that typst_debug is registered as a config value"""
    # Arrange: Create conf.py with typst_debug setting
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
typst_debug = True
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Config value should be accessible and correct
    assert hasattr(app.config, "typst_debug")
    assert app.config.typst_debug is True


def test_typst_debug_default_false(make_app, tmp_path):
    """Test that typst_debug defaults to False when not set"""
    # Arrange: Create conf.py without typst_debug
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
extensions = ['typsphinx']
""")

    # Create minimal index.rst
    index_rst = tmp_path / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.")

    # Act: Create Sphinx app
    app = make_app(srcdir=tmp_path, builddir=tmp_path / "_build")

    # Assert: Default should be False
    assert hasattr(app.config, "typst_debug")
    assert app.config.typst_debug is False

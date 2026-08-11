"""
Tests for template asset copying functionality (Issue #75).

This module tests the copy_template_assets() method and related functionality
for automatically copying assets (fonts, images, logos) referenced by custom templates.
"""

import pytest
from sphinx.testing.util import SphinxTestApp


@pytest.fixture
def temp_app_with_template(tmp_path):
    """
    Create a temporary Sphinx app with a custom template and assets.

    Directory structure:
        source/
            index.rst
            _templates/
                template.typ
                logo.png
                assets/
                    font.otf
                    icon.svg
    """
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create index.rst
    (srcdir / "index.rst").write_text(
        "Test Document\n" "=============\n" "\n" "This is a test document.\n"
    )

    # Create template directory and files
    template_dir = srcdir / "_templates"
    template_dir.mkdir()

    # Create template file
    (template_dir / "template.typ").write_text(
        '#import "logo.png"\n'
        '#set text(font: "assets/font.otf")\n'
        '#image("assets/icon.svg")\n'
    )

    # Create asset files
    (template_dir / "logo.png").write_bytes(b"fake png data")

    assets_dir = template_dir / "assets"
    assets_dir.mkdir()
    (assets_dir / "font.otf").write_bytes(b"fake font data")
    (assets_dir / "icon.svg").write_text("<svg></svg>")

    # Create conf.py
    (srcdir / "conf.py").write_text(
        "project = 'Test'\n"
        "extensions = ['typsphinx']\n"
        "typst_template = '_templates/template.typ'\n"
        # Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture
        # de-collision rule"): the original identity target "index"
        # resolved to the SAME physical path as this docname's own
        # content file (index.typ) under the two-layer split -- a
        # self-collision (D-01). Retargeted to the canonical "master.typ".
        "typst_documents = [('index', 'master.typ', 'Test', 'Author')]\n"
    )

    outdir = tmp_path / "build"

    app = SphinxTestApp(buildername="typst", srcdir=srcdir, builddir=outdir)

    return app, srcdir, outdir


def test_copy_template_assets_automatic_directory_copy(temp_app_with_template):
    """
    Test automatic directory copy (default behavior).

    When typst_template_assets is None, all files in the template directory
    should be automatically copied (except .typ files).
    """
    app, srcdir, outdir = temp_app_with_template

    # Build the project
    app.build()

    # Check that assets were copied to output directory
    typst_outdir = outdir / "typst"
    template_out_dir = typst_outdir / "_templates"

    assert (template_out_dir / "logo.png").exists()
    assert (template_out_dir / "assets" / "font.otf").exists()
    assert (template_out_dir / "assets" / "icon.svg").exists()

    # Verify file contents match
    assert (template_out_dir / "logo.png").read_bytes() == b"fake png data"
    assert (template_out_dir / "assets" / "font.otf").read_bytes() == b"fake font data"
    assert (template_out_dir / "assets" / "icon.svg").read_text() == "<svg></svg>"


def test_copy_template_assets_explicit_list(tmp_path):
    """
    Test explicit asset list specification.

    When typst_template_assets is configured, only specified assets should be copied.
    """
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create index.rst
    (srcdir / "index.rst").write_text(
        "Test Document\n" "=============\n" "\n" "This is a test document.\n"
    )

    # Create template directory and files
    template_dir = srcdir / "_templates"
    template_dir.mkdir()

    (template_dir / "template.typ").write_text('#image("logo.png")')
    (template_dir / "logo.png").write_bytes(b"logo data")
    (template_dir / "unused.png").write_bytes(b"unused data")

    # Create conf.py with explicit asset list
    (srcdir / "conf.py").write_text(
        "project = 'Test'\n"
        "extensions = ['typsphinx']\n"
        "typst_template = '_templates/template.typ'\n"
        "typst_template_assets = ['_templates/logo.png']\n"
        # Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture
        # de-collision rule"): the original identity target "index"
        # resolved to the SAME physical path as this docname's own
        # content file (index.typ) under the two-layer split -- a
        # self-collision (D-01). Retargeted to the canonical "master.typ".
        "typst_documents = [('index', 'master.typ', 'Test', 'Author')]\n"
    )

    outdir = tmp_path / "build"

    app = SphinxTestApp(buildername="typst", srcdir=srcdir, builddir=outdir)

    # Build the project
    app.build()

    # Check that only specified asset was copied
    typst_outdir = outdir / "typst"
    template_out_dir = typst_outdir / "_templates"

    assert (template_out_dir / "logo.png").exists()
    assert not (template_out_dir / "unused.png").exists()


def test_copy_template_assets_glob_pattern(tmp_path):
    """
    Test glob pattern support in asset list.

    Patterns like "*.png" should match multiple files.
    """
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create index.rst
    (srcdir / "index.rst").write_text(
        "Test Document\n" "=============\n" "\n" "This is a test document.\n"
    )

    # Create template directory and files
    template_dir = srcdir / "_templates"
    template_dir.mkdir()

    (template_dir / "template.typ").write_text('#image("logo.png")')
    (template_dir / "logo.png").write_bytes(b"logo data")
    (template_dir / "icon.png").write_bytes(b"icon data")
    (template_dir / "readme.txt").write_text("readme")

    # Create conf.py with glob pattern
    (srcdir / "conf.py").write_text(
        "project = 'Test'\n"
        "extensions = ['typsphinx']\n"
        "typst_template = '_templates/template.typ'\n"
        "typst_template_assets = ['_templates/*.png']\n"
        # Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture
        # de-collision rule"): the original identity target "index"
        # resolved to the SAME physical path as this docname's own
        # content file (index.typ) under the two-layer split -- a
        # self-collision (D-01). Retargeted to the canonical "master.typ".
        "typst_documents = [('index', 'master.typ', 'Test', 'Author')]\n"
    )

    outdir = tmp_path / "build"

    app = SphinxTestApp(buildername="typst", srcdir=srcdir, builddir=outdir)

    # Build the project
    app.build()

    # Check that all PNG files were copied, but not TXT
    typst_outdir = outdir / "typst"
    template_out_dir = typst_outdir / "_templates"

    assert (template_out_dir / "logo.png").exists()
    assert (template_out_dir / "icon.png").exists()
    assert not (template_out_dir / "readme.txt").exists()


def test_copy_template_assets_empty_list_disables(tmp_path):
    """
    Test that empty list disables automatic copying.

    typst_template_assets = [] should disable all automatic asset copying.
    """
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create index.rst
    (srcdir / "index.rst").write_text(
        "Test Document\n" "=============\n" "\n" "This is a test document.\n"
    )

    # Create template directory and files
    template_dir = srcdir / "_templates"
    template_dir.mkdir()

    (template_dir / "template.typ").write_text('#image("logo.png")')
    (template_dir / "logo.png").write_bytes(b"logo data")

    # Create conf.py with empty asset list
    (srcdir / "conf.py").write_text(
        "project = 'Test'\n"
        "extensions = ['typsphinx']\n"
        "typst_template = '_templates/template.typ'\n"
        "typst_template_assets = []\n"
        # Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture
        # de-collision rule"): the original identity target "index"
        # resolved to the SAME physical path as this docname's own
        # content file (index.typ) under the two-layer split -- a
        # self-collision (D-01). Retargeted to the canonical "master.typ".
        "typst_documents = [('index', 'master.typ', 'Test', 'Author')]\n"
    )

    outdir = tmp_path / "build"

    app = SphinxTestApp(buildername="typst", srcdir=srcdir, builddir=outdir)

    # Build the project
    app.build()

    # Check that assets were NOT copied
    typst_outdir = outdir / "typst"
    template_out_dir = typst_outdir / "_templates"

    # Template file should exist (copied by _write_template_file)
    assert (typst_outdir / "_template.typ").exists()

    # But logo.png should NOT be copied
    assert not (template_out_dir / "logo.png").exists()


def test_copy_template_assets_no_template(tmp_path):
    """
    Test that no assets are copied when no template is configured.

    This ensures backward compatibility with projects not using templates.
    """
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create index.rst
    (srcdir / "index.rst").write_text(
        "Test Document\n" "=============\n" "\n" "This is a test document.\n"
    )

    # Create conf.py WITHOUT template configuration
    (srcdir / "conf.py").write_text(
        "project = 'Test'\n"
        "extensions = ['typsphinx']\n"
        # Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture
        # de-collision rule"): the original identity target "index"
        # resolved to the SAME physical path as this docname's own
        # content file (index.typ) under the two-layer split -- a
        # self-collision (D-01). Retargeted to the canonical "master.typ".
        "typst_documents = [('index', 'master.typ', 'Test', 'Author')]\n"
    )

    outdir = tmp_path / "build"

    app = SphinxTestApp(buildername="typst", srcdir=srcdir, builddir=outdir)

    # Build should succeed without errors
    app.build()

    # No template directory should be created
    typst_outdir = outdir / "typst"
    template_out_dir = typst_outdir / "_templates"

    assert not template_out_dir.exists()


def test_copy_template_assets_with_typst_package(tmp_path):
    """
    Test that assets are NOT copied when using Typst Universe packages.

    Typst Universe packages handle assets automatically, so we should skip copying.
    """
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create index.rst
    (srcdir / "index.rst").write_text(
        "Test Document\n" "=============\n" "\n" "This is a test document.\n"
    )

    # Create template directory (even though using package)
    template_dir = srcdir / "_templates"
    template_dir.mkdir()
    (template_dir / "logo.png").write_bytes(b"logo data")

    # Create conf.py with Typst package (takes precedence over template)
    (srcdir / "conf.py").write_text(
        "project = 'Test'\n"
        "extensions = ['typsphinx']\n"
        "typst_package = '@preview/charged-ieee:0.1.0'\n"
        "typst_template = '_templates/template.typ'\n"
        # Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture
        # de-collision rule"): the original identity target "index"
        # resolved to the SAME physical path as this docname's own
        # content file (index.typ) under the two-layer split -- a
        # self-collision (D-01). Retargeted to the canonical "master.typ".
        "typst_documents = [('index', 'master.typ', 'Test', 'Author')]\n"
    )

    outdir = tmp_path / "build"

    app = SphinxTestApp(buildername="typst", srcdir=srcdir, builddir=outdir)

    # Build the project
    app.build()

    # Check that assets were NOT copied (package handles them)
    typst_outdir = outdir / "typst"
    template_out_dir = typst_outdir / "_templates"

    assert not (template_out_dir / "logo.png").exists()


def test_copy_template_assets_missing_source(tmp_path, caplog):
    """
    Test graceful handling of missing source files.

    Should log warning but not fail the build.
    """
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create index.rst
    (srcdir / "index.rst").write_text(
        "Test Document\n" "=============\n" "\n" "This is a test document.\n"
    )

    # Create template directory
    template_dir = srcdir / "_templates"
    template_dir.mkdir()

    (template_dir / "template.typ").write_text('#image("logo.png")')
    # Note: logo.png does NOT exist

    # Create conf.py with explicit asset that doesn't exist
    (srcdir / "conf.py").write_text(
        "project = 'Test'\n"
        "extensions = ['typsphinx']\n"
        "typst_template = '_templates/template.typ'\n"
        "typst_template_assets = ['_templates/logo.png']\n"
        # Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture
        # de-collision rule"): the original identity target "index"
        # resolved to the SAME physical path as this docname's own
        # content file (index.typ) under the two-layer split -- a
        # self-collision (D-01). Retargeted to the canonical "master.typ".
        "typst_documents = [('index', 'master.typ', 'Test', 'Author')]\n"
    )

    outdir = tmp_path / "build"

    app = SphinxTestApp(buildername="typst", srcdir=srcdir, builddir=outdir)

    # Build should succeed despite missing file
    app.build()

    # Check that warning was logged in Sphinx's warning stream
    warnings = app._warning.getvalue()
    assert "Template asset not found" in warnings


def test_copy_template_assets_typstpdf_builder(tmp_path):
    """
    Test that asset copying works with TypstPDFBuilder.

    Assets should be copied before PDF compilation.
    """
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create index.rst
    (srcdir / "index.rst").write_text(
        "Test Document\n" "=============\n" "\n" "This is a test document.\n"
    )

    # Create template directory and files
    template_dir = srcdir / "_templates"
    template_dir.mkdir()

    (template_dir / "template.typ").write_text('#image("logo.png")')
    (template_dir / "logo.png").write_bytes(b"logo data")

    # Create conf.py
    (srcdir / "conf.py").write_text(
        "project = 'Test'\n"
        "extensions = ['typsphinx']\n"
        "typst_template = '_templates/template.typ'\n"
        # Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture
        # de-collision rule"): the original identity target "index"
        # resolved to the SAME physical path as this docname's own
        # content file (index.typ) under the two-layer split -- a
        # self-collision (D-01). Retargeted to the canonical "master.typ".
        "typst_documents = [('index', 'master.typ', 'Test', 'Author')]\n"
    )

    outdir = tmp_path / "build"

    app = SphinxTestApp(
        buildername="typstpdf", srcdir=srcdir, builddir=outdir  # Use PDF builder
    )

    # Build the project
    # Note: This may fail at PDF compilation if typst-py is not properly set up,
    # but asset copying should still happen
    try:
        app.build()
    except Exception:
        pass  # Ignore PDF compilation errors

    # Check that assets were copied before PDF compilation
    typstpdf_outdir = outdir / "typstpdf"
    template_out_dir = typstpdf_outdir / "_templates"

    assert (template_out_dir / "logo.png").exists()

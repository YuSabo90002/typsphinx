"""
Tests for TypstBuilder class.
"""

from pathlib import Path

from docutils import nodes
from sphinx.builders import Builder


def test_typst_builder_can_be_imported():
    """Test that TypstBuilder can be imported."""
    from typsphinx.builder import TypstBuilder

    assert TypstBuilder is not None
    assert issubclass(TypstBuilder, Builder)


def test_typst_builder_has_correct_attributes():
    """Test that TypstBuilder has the correct class attributes."""
    from typsphinx.builder import TypstBuilder

    assert TypstBuilder.name == "typst"
    assert TypstBuilder.format == "typst"
    assert TypstBuilder.out_suffix == ".typ"


def test_typst_builder_has_required_methods():
    """Test that TypstBuilder implements required methods."""
    from typsphinx.builder import TypstBuilder

    # Check that required methods exist
    assert hasattr(TypstBuilder, "init")
    assert hasattr(TypstBuilder, "get_outdated_docs")
    assert hasattr(TypstBuilder, "get_target_uri")
    assert hasattr(TypstBuilder, "prepare_writing")
    assert hasattr(TypstBuilder, "write_doc")
    assert hasattr(TypstBuilder, "finish")


def test_typst_builder_registration(temp_sphinx_app):
    """Test that TypstBuilder can be registered with Sphinx."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app

    # Builder should already be registered by the extension setup
    # Check that the builder is registered
    assert "typst" in app.registry.builders
    assert app.registry.builders["typst"] == TypstBuilder


def test_typst_builder_initialization(temp_sphinx_app):
    """Test that TypstBuilder can be initialized."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app

    # Create a builder instance with app and env
    builder = TypstBuilder(app, app.env)

    assert builder is not None
    assert builder.name == "typst"
    assert builder._app == app


def test_get_outdated_docs_returns_iterator(temp_sphinx_app):
    """Test that get_outdated_docs returns an iterator."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    # Initialize builder
    builder.init()

    # get_outdated_docs should return an iterator
    result = builder.get_outdated_docs()
    assert hasattr(result, "__iter__")


def test_get_target_uri_returns_string(temp_sphinx_app):
    """Test that get_target_uri returns a string."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    builder.init()

    # get_target_uri should return a string
    uri = builder.get_target_uri("index")
    assert isinstance(uri, str)
    assert uri.endswith(".typ")


def test_prepare_writing_accepts_docnames(temp_sphinx_app):
    """Test that prepare_writing can be called with a set of docnames."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # prepare_writing should accept a set of document names
    docnames = {"index", "page1", "page2"}
    builder.prepare_writing(docnames)

    # After prepare_writing, writer should be initialized
    assert hasattr(builder, "writer")
    assert builder.writer is not None


def test_write_doc_creates_output_file(temp_sphinx_app, sample_doctree):
    """Test that write_doc creates an output file."""
    from pathlib import Path

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    docnames = {"index"}
    builder.prepare_writing(docnames)

    # Write a document
    builder.write_doc("index", sample_doctree)

    # Check that output file was created
    output_file = Path(builder.outdir) / "index.typ"
    assert output_file.exists()
    assert output_file.is_file()


def test_write_doc_generates_typst_content(temp_sphinx_app, sample_doctree):
    """Test that write_doc generates Typst content."""
    from pathlib import Path

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    docnames = {"index"}
    builder.prepare_writing(docnames)

    # Write a document
    builder.write_doc("index", sample_doctree)

    # Check that output file contains Typst content
    output_file = Path(builder.outdir) / "index.typ"
    content = output_file.read_text()

    # Should contain basic Typst markup
    assert len(content) > 0
    # Should contain the title from sample_doctree
    assert "Test Section" in content


def test_finish_completes_build(temp_sphinx_app, sample_doctree):
    """Test that finish completes the build process."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    docnames = {"index"}
    builder.prepare_writing(docnames)
    builder.write_doc("index", sample_doctree)

    # finish should complete without errors
    builder.finish()

    # After finish, build should be complete
    # (no specific assertion needed, just checking it doesn't raise)


def test_images_dict_initialized(temp_sphinx_app):
    """Test that images dictionary is initialized in init()."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # images dictionary should be initialized
    assert hasattr(builder, "images")
    assert isinstance(builder.images, dict)
    assert len(builder.images) == 0


def test_post_process_images_collects_image_nodes(temp_sphinx_app):
    """Test that post_process_images collects image nodes from doctree."""
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # Create a doctree with an image node
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    # Add an image node
    img = nodes.image(uri="images/test.png")
    doc += img

    # Process images
    builder.post_process_images(doc)

    # images dictionary should contain the image URI
    assert "images/test.png" in builder.images


def test_post_process_images_handles_multiple_images(temp_sphinx_app):
    """Test that post_process_images handles multiple image nodes."""
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # Create a doctree with multiple image nodes
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    # Add multiple image nodes
    img1 = nodes.image(uri="images/test1.png")
    img2 = nodes.image(uri="images/test2.png")
    img3 = nodes.image(uri="diagrams/flow.svg")
    doc += img1
    doc += img2
    doc += img3

    # Process images
    builder.post_process_images(doc)

    # images dictionary should contain all image URIs
    assert "images/test1.png" in builder.images
    assert "images/test2.png" in builder.images
    assert "diagrams/flow.svg" in builder.images
    assert len(builder.images) == 3


def test_post_process_images_ignores_empty_uri(temp_sphinx_app):
    """Test that post_process_images ignores image nodes with empty URI."""
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # Create a doctree with an image node without URI
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    # Add an image node without URI
    img = nodes.image()
    doc += img

    # Process images
    builder.post_process_images(doc)

    # images dictionary should be empty
    assert len(builder.images) == 0


def test_copy_image_files_copies_images_to_output(temp_sphinx_app):
    """Test that copy_image_files copies images to output directory."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # Create a test image file in source directory
    img_src_dir = Path(builder.srcdir) / "images"
    img_src_dir.mkdir(parents=True, exist_ok=True)
    img_src_file = img_src_dir / "test.png"
    img_src_file.write_bytes(b"fake image content")

    # Track this image
    builder.images["images/test.png"] = ""

    # Copy images
    builder.copy_image_files()

    # Check that image was copied to output directory
    img_dest_file = Path(builder.outdir) / "images" / "test.png"
    assert img_dest_file.exists()
    assert img_dest_file.read_bytes() == b"fake image content"


def test_copy_image_files_preserves_directory_structure(temp_sphinx_app):
    """Test that copy_image_files preserves directory structure."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # Create nested directory structure with images
    img_dir1 = Path(builder.srcdir) / "images" / "subdir1"
    img_dir1.mkdir(parents=True, exist_ok=True)
    img_file1 = img_dir1 / "test1.png"
    img_file1.write_bytes(b"image 1")

    img_dir2 = Path(builder.srcdir) / "diagrams"
    img_dir2.mkdir(parents=True, exist_ok=True)
    img_file2 = img_dir2 / "flow.svg"
    img_file2.write_bytes(b"<svg>test</svg>")

    # Track these images
    builder.images["images/subdir1/test1.png"] = ""
    builder.images["diagrams/flow.svg"] = ""

    # Copy images
    builder.copy_image_files()

    # Check that directory structure is preserved
    dest_file1 = Path(builder.outdir) / "images" / "subdir1" / "test1.png"
    dest_file2 = Path(builder.outdir) / "diagrams" / "flow.svg"
    assert dest_file1.exists()
    assert dest_file2.exists()
    assert dest_file1.read_bytes() == b"image 1"
    assert dest_file2.read_bytes() == b"<svg>test</svg>"


def test_copy_image_files_handles_missing_source(temp_sphinx_app):
    """Test that copy_image_files handles missing source files gracefully."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # Track a non-existent image
    builder.images["images/nonexistent.png"] = ""

    # copy_image_files should not raise an exception
    builder.copy_image_files()

    # Image should not be copied
    img_dest_file = Path(builder.outdir) / "images" / "nonexistent.png"
    assert not img_dest_file.exists()


def test_finish_calls_copy_image_files(temp_sphinx_app):
    """Test that finish() calls copy_image_files()."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # Create a test image
    img_src_dir = Path(builder.srcdir) / "images"
    img_src_dir.mkdir(parents=True, exist_ok=True)
    img_src_file = img_src_dir / "test.png"
    img_src_file.write_bytes(b"test image")

    # Track this image
    builder.images["images/test.png"] = ""

    # Call finish()
    builder.finish()

    # Image should be copied
    img_dest_file = Path(builder.outdir) / "images" / "test.png"
    assert img_dest_file.exists()


def test_write_doc_calls_post_process_images(temp_sphinx_app):
    """Test that write_doc() calls post_process_images()."""
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # Prepare writing
    docnames = {"index"}
    builder.prepare_writing(docnames)

    # Create a doctree with an image
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    section = nodes.section()
    title = nodes.title(text="Test Section")
    section += title
    img = nodes.image(uri="images/test.png")
    section += img
    doc += section

    # Write document
    builder.write_doc("index", doc)

    # Image should be tracked
    assert "images/test.png" in builder.images

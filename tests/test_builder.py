"""
Tests for TypstBuilder class.
"""

import os
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

    # CONF-08: temp_sphinx_app's conf.py omits typst_documents, so the
    # config value now resolves through _default_typst_documents, which
    # names the "index" master's output via
    # make_filename_from_project("Test Project") -> "testproject.typ"
    # rather than the old literal "index.typ".
    output_file = Path(builder.outdir) / "testproject.typ"
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

    # Phase 47 (R1/COMP-01): the translated BODY (the title from
    # sample_doctree) lives on the docname-derived CONTENT file, always at
    # "index.typ" -- unconditional, regardless of what any typst_documents
    # entry's target names.
    content_file = Path(builder.outdir) / "index.typ"
    content = content_file.read_text()

    # Should contain basic Typst markup
    assert len(content) > 0
    # Should contain the title from sample_doctree
    assert "Test Section" in content

    # CONF-08 (R2): temp_sphinx_app's conf.py omits typst_documents, so the
    # config value now resolves through _default_typst_documents, which
    # names the "index" master's WRAPPER via
    # make_filename_from_project("Test Project") -> "testproject.typ"
    # rather than the old literal "index.typ". The wrapper carries the
    # template application and an #include() of the content file above,
    # never the translated body itself.
    wrapper_file = Path(builder.outdir) / "testproject.typ"
    wrapper_content = wrapper_file.read_text()
    assert len(wrapper_content) > 0
    assert '#include("index.typ")' in wrapper_content


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


def test_post_process_images_rehomes_absolute_uri(temp_sphinx_app):
    """
    Test that post_process_images() rehomes an absolute image URI.

    Sphinx's ImageConverter/ImageDownloader post-transforms rewrite
    node["uri"] to an absolute path under <doctreedir>/images/... when an
    image needs conversion or download (Issue #130). post_process_images()
    must rewrite node["uri"] to a doctreedir-relative path and track the
    true absolute location as the self.images value (not "").
    """
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    abs_uri = os.path.join(builder.doctreedir, "images", "converted.png")

    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    img = nodes.image(uri=abs_uri, candidates={"*": abs_uri})
    doc += img

    builder.post_process_images(doc)

    assert img["uri"] == "images/converted.png"
    assert builder.images.get("images/converted.png") == abs_uri


def test_copy_image_files_uses_override_source_for_absolute_uri(temp_sphinx_app):
    """
    Test that copy_image_files() uses the tracked absolute override source.

    Before the fix, ``src = path.join(self.srcdir, imguri)`` and
    ``dest = path.join(self.outdir, imguri)`` both collapsed to the same
    absolute path whenever imguri was itself absolute (os.path.join
    discards the first argument once the second is absolute), producing
    the "are the same file" warning from Issue #130 and copying nothing.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # The true source lives outside srcdir entirely (e.g. under
    # <doctreedir>/images/), proving the copy does NOT depend on
    # path.join(self.srcdir, imguri) resolving correctly.
    real_src_dir = Path(builder.doctreedir) / "images"
    real_src_dir.mkdir(parents=True, exist_ok=True)
    real_src_file = real_src_dir / "converted.png"
    real_src_file.write_bytes(b"converted image content")

    builder.images["images/converted.png"] = str(real_src_file)

    builder.copy_image_files()

    img_dest_file = Path(builder.outdir) / "images" / "converted.png"
    assert img_dest_file.exists()
    assert img_dest_file.read_bytes() == b"converted image content"


def test_post_process_images_rehome_collision_relocates_silently(
    temp_sphinx_app, caplog
):
    """
    D-01/D-02/D-03/D-04: when a REAL source image already occupies the
    rehome target, post_process_images() relocates the converted image
    under the reserved _typst_converted/ namespace instead of the plain
    images/<basename> key -- SILENTLY (no WARNING records) and decided by
    a filesystem probe, not by whether the key is already present in
    self.images (no self.images entry is pre-seeded here).
    """
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    abs_uri = os.path.join(builder.doctreedir, "images", "converted.png")

    # A REAL source image occupies the target this rehome would produce.
    # The collision decision must come from this filesystem probe, not
    # from any pre-seeded self.images entry (D-03).
    real_images_dir = os.path.join(builder.srcdir, "images")
    os.makedirs(real_images_dir, exist_ok=True)
    with open(os.path.join(real_images_dir, "converted.png"), "wb") as f:
        f.write(b"real source image content")

    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    img = nodes.image(uri=abs_uri, candidates={"*": abs_uri})
    doc += img

    with caplog.at_level("WARNING"):
        builder.post_process_images(doc)

    assert img["uri"] == "_typst_converted/images/converted.png"
    assert builder.images.get("_typst_converted/images/converted.png") == abs_uri
    assert "images/converted.png" not in builder.images
    assert [r for r in caplog.records if r.levelname == "WARNING"] == []


def test_post_process_images_rehome_escape_relocates_with_warning(
    temp_sphinx_app, caplog
):
    """
    D-05/D-06: an absolute URI whose rehome result cannot possibly sit
    under doctreedir -- built from the filesystem root -- is relocated
    to the reserved namespace plus the basename of the ORIGINAL absolute
    URI, and emits exactly one WARNING naming the offending URI.
    """
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    # Built from the filesystem root so it cannot possibly sit under the
    # app's temporary doctreedir. The file need not exist on disk --
    # _track_image() decides purely from the path shape.
    abs_uri = os.path.join(os.sep, "typsphinx_test_50_03_escape_root", "chart.png")

    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    img = nodes.image(uri=abs_uri, candidates={"*": abs_uri})
    doc += img

    with caplog.at_level("WARNING"):
        builder.post_process_images(doc)

    assert img["uri"] == "_typst_converted/chart.png"
    assert ".." not in img["uri"].split("/")
    assert builder.images.get("_typst_converted/chart.png") == abs_uri

    warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warning_records) == 1
    message = warning_records[0].getMessage()
    assert "could not rehome image URI" in message
    # The product formats the URI with `!r` (deliberate -- it quotes the
    # path), so the emitted message contains repr(abs_uri), not abs_uri
    # itself. On POSIX repr() escapes nothing and the two happen to be
    # equal, masking this on this host; on Windows repr() doubles every
    # backslash (os.sep == "\\"), so the raw path is no longer a substring
    # of the message. Asserting against repr(abs_uri) holds on both.
    assert repr(abs_uri) in message


def test_post_process_images_rehome_cross_drive_value_error_relocates(
    temp_sphinx_app, caplog, monkeypatch
):
    """
    D-07: a ValueError raised by path.relpath (the Windows cross-drive
    case) is caught and routed into the same relocation outcome instead
    of propagating out of the build. Genuine two-drive paths are not
    reproducible on this POSIX host, so relpath is monkeypatched to raise
    only for this test's specific absolute URI -- a blanket replacement
    would break unrelated path work inside the same call.
    """
    import typsphinx.builder as builder_module
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    abs_uri = os.path.join(builder.doctreedir, "images", "crossdrive.png")

    real_relpath = builder_module.path.relpath

    def _raising_relpath(a, *args, **kwargs):
        if a == abs_uri:
            raise ValueError("simulated Windows cross-drive relpath failure")
        return real_relpath(a, *args, **kwargs)

    monkeypatch.setattr(builder_module.path, "relpath", _raising_relpath)

    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    img = nodes.image(uri=abs_uri, candidates={"*": abs_uri})
    doc += img

    with caplog.at_level("WARNING"):
        builder.post_process_images(doc)

    assert img["uri"] == "_typst_converted/crossdrive.png"
    assert builder.images.get("_typst_converted/crossdrive.png") == abs_uri
    warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warning_records) == 1


def test_copy_image_files_relocated_key_destination_stays_under_outdir(
    temp_sphinx_app,
):
    """
    T-50-01/D-05: a builder.images key already carrying the reserved
    namespace (as _track_image() would produce for either relocation
    branch) still lands its destination under outdir when
    copy_image_files() writes it -- and the resolved destination's
    common path with outdir is outdir itself, the containment check that
    fails loudly if a future change ever lets a parent segment back into
    a tracked key.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    real_src_dir = Path(builder.doctreedir) / "images"
    real_src_dir.mkdir(parents=True, exist_ok=True)
    real_src_file = real_src_dir / "converted.png"
    real_src_file.write_bytes(b"relocated converted image content")

    builder.images["_typst_converted/images/converted.png"] = str(real_src_file)

    builder.copy_image_files()

    img_dest_file = (
        Path(builder.outdir) / "_typst_converted" / "images" / "converted.png"
    )
    assert img_dest_file.exists()
    assert img_dest_file.read_bytes() == b"relocated converted image content"

    resolved_dest = img_dest_file.resolve()
    resolved_outdir = Path(builder.outdir).resolve()
    assert os.path.commonpath([str(resolved_dest), str(resolved_outdir)]) == str(
        resolved_outdir
    )


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

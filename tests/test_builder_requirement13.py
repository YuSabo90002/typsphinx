"""
Tests for Requirement 13: ビルダーの複数ドキュメント統合機能

タスク8.1: 独立した.typファイルの生成
タスク8.4: Toctreeエラーハンドリング
"""

import pytest
from sphinx.testing.util import SphinxTestApp


@pytest.fixture
def multifile_srcdir(tmp_path):
    """Create a multi-file Sphinx project for testing."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # conf.py
    conf_py = srcdir / "conf.py"
    conf_py.write_text(
        "extensions = ['typsphinx']\n"
        "project = 'Multi-File Test'\n"
        "author = 'Test Author'\n"
    )

    # index.rst with toctree
    index_rst = srcdir / "index.rst"
    index_rst.write_text(
        "Test Project\n"
        "============\n"
        "\n"
        ".. toctree::\n"
        "   :maxdepth: 2\n"
        "\n"
        "   intro\n"
        "   chapter1/section\n"
    )

    # intro.rst
    intro_rst = srcdir / "intro.rst"
    intro_rst.write_text(
        "Introduction\n" "============\n" "\n" "This is the introduction.\n"
    )

    # chapter1/section.rst (nested)
    chapter1_dir = srcdir / "chapter1"
    chapter1_dir.mkdir()
    section_rst = chapter1_dir / "section.rst"
    section_rst.write_text(
        "Chapter 1 Section\n"
        "=================\n"
        "\n"
        "This is a section in chapter 1.\n"
    )

    return srcdir


def test_builder_generates_independent_typ_files(multifile_srcdir, tmp_path):
    """
    Test that each .rst file generates an independent .typ file.

    Requirement 13.1: WHEN 各 reStructuredText ファイルがビルドされる
    THEN TypstBuilder SHALL 対応する独立した .typ ファイルを生成する
    """
    builddir = tmp_path / "build"

    app = SphinxTestApp(
        srcdir=multifile_srcdir,
        builddir=builddir,
        buildername="typst",
    )
    app.build()

    typst_outdir = builddir / "typst"

    # CONF-08: multifile_srcdir's conf.py omits typst_documents, so the
    # "index" master's output is now named via
    # make_filename_from_project("Multi-File Test") -> "multi-filetest.typ"
    # rather than the old literal "index.typ".
    # Check that independent .typ files are created
    assert (typst_outdir / "multi-filetest.typ").exists()
    assert (typst_outdir / "intro.typ").exists()
    assert (typst_outdir / "chapter1" / "section.typ").exists()


def test_builder_preserves_directory_structure(multifile_srcdir, tmp_path):
    """
    Test that the builder preserves source directory structure.

    Requirement 13.12: WHERE ビルド出力ディレクトリ THE すべての .typ ファイル
    SHALL フラットまたはソースと同じディレクトリ構造で配置され、
    `#include()` の相対パスはその構造に従う
    """
    builddir = tmp_path / "build"

    app = SphinxTestApp(
        srcdir=multifile_srcdir,
        builddir=builddir,
        buildername="typst",
    )
    app.build()

    typst_outdir = builddir / "typst"

    # Check directory structure is preserved
    assert (typst_outdir / "chapter1").is_dir()
    assert (typst_outdir / "chapter1" / "section.typ").is_file()


def test_toctree_with_nested_paths_generates_correct_includes(
    multifile_srcdir, tmp_path
):
    """
    Test that toctree with nested paths works correctly.

    Requirement 13.5: WHEN `toctree` で参照されたドキュメントパスが
    "chapter1/section" の場合 THEN Typst SHALL
    `#include("chapter1/section.typ")` を生成する

    Note: This is an integration test that verifies the build completes successfully.
    The actual #include() generation is tested in test_toctree_requirement13.py
    """
    builddir = tmp_path / "build"

    app = SphinxTestApp(
        srcdir=multifile_srcdir,
        builddir=builddir,
        buildername="typst",
    )
    app.build()

    typst_outdir = builddir / "typst"
    # Phase 47 (R1/R5/COMP-01): the toctree's #include() emissions are
    # translator body markup -- they stay on the docname-derived CONTENT
    # file, always at "index.typ", unconditionally.
    index_typ = typst_outdir / "index.typ"
    # CONF-08 (R2): multifile_srcdir's conf.py omits typst_documents, so
    # the "index" master's WRAPPER is now named via
    # make_filename_from_project("Multi-File Test") -> "multi-filetest.typ"
    # rather than the old literal "index.typ".
    wrapper_typ = typst_outdir / "multi-filetest.typ"

    # Verify files were created with correct structure
    assert index_typ.exists()
    assert wrapper_typ.exists()
    assert (typst_outdir / "intro.typ").exists()
    assert (typst_outdir / "chapter1" / "section.typ").exists()

    # Verify the CONTENT file has references to nested documents.
    content = index_typ.read_text()
    assert "intro.typ" in content
    assert "chapter1/section.typ" in content

    # Verify the WRAPPER carries the template application and an
    # #include() of the content file above, never the nested-document
    # references themselves.
    wrapper_content = wrapper_typ.read_text()
    assert '#include("index.typ")' in wrapper_content


def test_toctree_with_missing_document_warning(multifile_srcdir, tmp_path, caplog):
    """
    Test that missing documents in toctree are handled gracefully.

    Requirement 13.10: IF `toctree` で参照されたドキュメントファイルが存在しない
    THEN Sphinx SHALL 警告を出力し、該当の `#include()` は
    コメントアウトまたはスキップされる

    Note: Sphinx handles missing toctree entries at a higher level,
    so this test verifies the build completes successfully.
    """
    # Add a non-existent document to index.rst
    index_rst = multifile_srcdir / "index.rst"
    index_rst.write_text(
        "Test Project\n"
        "============\n"
        "\n"
        ".. toctree::\n"
        "\n"
        "   intro\n"
        "   nonexistent\n"
    )

    builddir = tmp_path / "build"

    app = SphinxTestApp(
        srcdir=multifile_srcdir,
        builddir=builddir,
        buildername="typst",
    )

    # Build should complete without crashing
    app.build()

    typst_outdir = builddir / "typst"
    # Phase 47 (R1/R5/COMP-01): the toctree's #include() emissions stay on
    # the docname-derived CONTENT file, always at "index.typ".
    index_typ = typst_outdir / "index.typ"

    # Build should succeed and create the content file
    assert index_typ.exists()

    content = index_typ.read_text()

    # Should reference existing document
    assert "intro.typ" in content

    # Verify the existing document was built
    assert (typst_outdir / "intro.typ").exists()


def test_ensuredir_creates_nested_directories(tmp_path):
    """
    Test that ensuredir properly creates nested directories.

    This is a helper test for Requirement 13.12
    """
    from sphinx.util.osutil import ensuredir

    nested_dir = tmp_path / "level1" / "level2" / "level3"
    ensuredir(nested_dir)

    assert nested_dir.exists()
    assert nested_dir.is_dir()

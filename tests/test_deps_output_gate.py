"""
Output gate for the shared ``<outdir>/_typsphinx/deps.typ`` (SC2).

Every ``typst``/``typstpdf`` build writes ``<outdir>/_typsphinx/deps.typ``
from ``typsphinx.typst_deps``; every content file and every wrapper starts
with the two-line preamble ``#import "/_typsphinx/deps.typ": *`` +
``#show: typsphinx-init`` and pins none of the five ``@preview`` specs
itself. This module proves, with real ``sphinx-build`` subprocess builds of
``tests/fixtures/deps_output_gate/``:

(a) the default output tree on the content-file route (``typst_documents =
    []``), the default-template route, an explicit-template wrapper route,
    and a ``typst_package``-only wrapper route;
(b) E3: a document with no code block, math, admonition, or graphviz still
    imports ``deps.typ`` and applies ``typsphinx-init``;
(c) the ``_typsphinx`` output-directory reservation;
(d) the inline-default-template route of ``TemplateEngine.render()``
    compiles under ``typst-py`` with ``deps.typ`` at the compile root.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from typsphinx.template_engine import TemplateEngine
from typsphinx.typst_deps import (
    DEFAULT_PACKAGES,
    DEPS_FILENAME,
    DEPS_OUTPUT_DIR,
    deps_preamble_lines,
    render_default_deps,
)

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURES = Path(__file__).parent / "fixtures" / "deps_output_gate"

DEPS_IMPORT_LINE = '#import "/_typsphinx/deps.typ": *'
INIT_SHOW_LINE = "#show: typsphinx-init"
FIVE_SPEC_RE = re.compile(
    r"@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):"
)


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str = "typst"
) -> subprocess.CompletedProcess:
    """Run ``sys.executable -m sphinx -E -b <builder>`` (no PATH lookup)."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-E",
            "-b",
            builder,
            str(source_dir),
            str(build_dir),
            "-d",
            str(build_dir.parent / f"{build_dir.name}-doctrees"),
        ],
        capture_output=True,
        text=True,
    )


def _emitted_typ_files(build_dir: Path) -> list[Path]:
    """Every content/wrapper ``.typ`` -- excluding template bundles and the
    generated ``_typsphinx/`` directory."""
    return sorted(
        p
        for p in build_dir.rglob("*.typ")
        if p.relative_to(build_dir).parts[0] not in ("_template", DEPS_OUTPUT_DIR)
    )


def _assert_preamble(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert DEPS_IMPORT_LINE in lines, f"{path} lacks the deps.typ import:\n{text}"
    assert INIT_SHOW_LINE in lines, f"{path} lacks typsphinx-init:\n{text}"
    assert lines.index(DEPS_IMPORT_LINE) < lines.index(INIT_SHOW_LINE), text
    assert lines.count(INIT_SHOW_LINE) == 1, text
    assert not FIVE_SPEC_RE.search(text), f"{path} pins an @preview spec:\n{text}"


def _assert_default_deps(build_dir: Path) -> None:
    deps = build_dir / DEPS_OUTPUT_DIR / DEPS_FILENAME
    assert deps.is_file(), f"{deps} was not written"
    text = deps.read_text(encoding="utf-8")
    assert deps.read_bytes() == render_default_deps().encode("utf-8")
    for package in DEFAULT_PACKAGES:
        assert package.import_line() in text.splitlines()
    assert "#let typsphinx-init(body)" in text


def _build_ok(source_dir: Path, tmp_path: Path, builder: str = "typst") -> Path:
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(source_dir, build_dir, builder)
    assert result.returncode == 0, (
        f"sphinx-build -b {builder} failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return build_dir


class TestDefaultOutputTree:
    """(a) SC2 default output tree, one test per route."""

    def test_preamble_lines_shape(self):
        assert deps_preamble_lines() == [DEPS_IMPORT_LINE, INIT_SHOW_LINE]

    def test_content_file_route(self, tmp_path):
        build_dir = _build_ok(FIXTURES / "content_only", tmp_path)
        _assert_default_deps(build_dir)
        emitted = _emitted_typ_files(build_dir)
        assert [p.name for p in emitted] == ["chapter.typ", "index.typ"]
        for path in emitted:
            _assert_preamble(path)

    @pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py is required")
    def test_default_template_route_builds_pdf(self, tmp_path):
        build_dir = _build_ok(FIXTURES / "default", tmp_path, "typstpdf")
        _assert_default_deps(build_dir)
        emitted = _emitted_typ_files(build_dir)
        wrappers = [p for p in emitted if "#include(" in p.read_text("utf-8")]
        assert wrappers, f"no wrapper among {emitted}"
        assert {"chapter.typ", "index.typ"} <= {p.name for p in emitted}
        for path in emitted:
            _assert_preamble(path)
        assert list(build_dir.glob("*.pdf")), "no PDF was written"
        base = build_dir / "_template" / "typst" / "base.typ"
        assert DEPS_IMPORT_LINE in base.read_text("utf-8").splitlines()

    @pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py is required")
    def test_explicit_template_route_builds_pdf(self, tmp_path):
        build_dir = _build_ok(FIXTURES / "explicit_template", tmp_path, "typstpdf")
        _assert_default_deps(build_dir)
        emitted = _emitted_typ_files(build_dir)
        assert [p.name for p in emitted] == ["chapter.typ", "index.typ", "manual.typ"]
        for path in emitted:
            _assert_preamble(path)
        wrapper_lines = (build_dir / "manual.typ").read_text("utf-8").splitlines()
        template_import = next(
            line for line in wrapper_lines if line.startswith('#import "/_template/')
        )
        assert wrapper_lines.index(INIT_SHOW_LINE) < wrapper_lines.index(
            template_import
        )
        assert (build_dir / "manual.pdf").is_file()

    def test_package_only_route(self, tmp_path):
        build_dir = _build_ok(FIXTURES / "package_only", tmp_path)
        _assert_default_deps(build_dir)
        emitted = _emitted_typ_files(build_dir)
        assert [p.name for p in emitted] == ["chapter.typ", "index.typ", "paper.typ"]
        for path in emitted:
            _assert_preamble(path)
        wrapper_lines = (build_dir / "paper.typ").read_text("utf-8").splitlines()
        package_import = '#import "@preview/charged-ieee:0.1.4": ieee'
        assert wrapper_lines.index(package_import) < wrapper_lines.index(
            DEPS_IMPORT_LINE
        )
        assert not (build_dir / "_template").exists()

    def test_rebuild_rewrites_identical_bytes(self, tmp_path):
        build_dir = _build_ok(FIXTURES / "content_only", tmp_path)
        deps = build_dir / DEPS_OUTPUT_DIR / DEPS_FILENAME
        deps.write_bytes(b"stale")
        result = _run_sphinx_build(FIXTURES / "content_only", build_dir)
        assert result.returncode == 0, result.stdout + result.stderr
        assert deps.read_bytes() == render_default_deps().encode("utf-8")


class TestPlainDocumentStillImportsDeps:
    """(b) E3: imports stay unconditional."""

    def test_plain_content_and_wrapper_carry_preamble(self, tmp_path):
        build_dir = _build_ok(FIXTURES / "plain", tmp_path)
        _assert_default_deps(build_dir)
        content = build_dir / "index.typ"
        wrapper = build_dir / "plain.typ"
        for path in (content, wrapper):
            assert path.is_file(), f"{path} was not written"
            _assert_preamble(path)
        assert [p.name for p in _emitted_typ_files(build_dir)] == [
            "index.typ",
            "plain.typ",
        ]


class TestTypsphinxDirectoryReservation:
    """(c) A docname or wrapper under ``_typsphinx/`` stops the build."""

    def _assert_refused(self, result, build_dir: Path, offending: str) -> None:
        output = result.stdout + result.stderr
        assert result.returncode != 0, output
        assert "ExtensionError" in output or "Extension error" in output, output
        assert offending in output, output
        assert "'_typsphinx'" in output or '"_typsphinx"' in output, output
        assert "reserved" in output, output
        survivors = list(build_dir.rglob("*.typ")) if build_dir.exists() else []
        assert survivors == [], survivors

    def test_docname_under_typsphinx_refused(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(FIXTURES / "reserved", build_dir)
        self._assert_refused(result, build_dir, "_typsphinx/deps")

    def test_case_variant_refused(self, tmp_path):
        src = tmp_path / "src"
        shutil.copytree(FIXTURES / "plain", src)
        (src / "_Typsphinx").mkdir()
        (src / "_Typsphinx" / "x.rst").write_text(
            ":orphan:\n\nX\n=\n\nText.\n", encoding="utf-8"
        )
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(src, build_dir)
        self._assert_refused(result, build_dir, "_Typsphinx/x")

    def test_wrapper_target_under_typsphinx_refused(self, tmp_path):
        src = tmp_path / "src"
        shutil.copytree(FIXTURES / "plain", src)
        conf = src / "conf.py"
        conf.write_text(
            conf.read_text(encoding="utf-8")
            + '\ntypst_documents = [("index", "_typsphinx/out.typ", "P", "A")]\n',
            encoding="utf-8",
        )
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(src, build_dir)
        self._assert_refused(result, build_dir, "_typsphinx/out")

    def test_similar_prefix_not_refused(self, tmp_path):
        src = tmp_path / "src"
        shutil.copytree(FIXTURES / "plain", src)
        (src / "_typsphinxes").mkdir()
        (src / "_typsphinxes" / "x.rst").write_text(
            ":orphan:\n\nX\n=\n\nText.\n", encoding="utf-8"
        )
        build_dir = _build_ok(src, tmp_path)
        _assert_preamble(build_dir / "_typsphinxes" / "x.typ")
        _assert_default_deps(build_dir)


@pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py is required")
class TestInlineDefaultTemplateRouteCompiles:
    """(d) The inline-default-template route (no template_file, no
    typst_package) inlines ``base.typ`` -- which imports ``deps.typ`` too --
    after the wrapper preamble. The duplicate import must compile."""

    def test_inline_route_compiles_with_deps_at_root(self, tmp_path):
        (tmp_path / DEPS_OUTPUT_DIR).mkdir()
        (tmp_path / DEPS_OUTPUT_DIR / DEPS_FILENAME).write_bytes(
            render_default_deps().encode("utf-8")
        )
        body = (
            "#{\n"
            "[Inline route body]\n"
            'info(title: "Note")[gentle-clues]\n'
            'mi("x^2")\n'
            'raw("print(1)", block: true, lang: "python")\n'
            'render("digraph { a -> b }")\n'
            "}\n"
        )
        source = TemplateEngine().render({"title": "Inline", "authors": ()}, body)
        lines = source.splitlines()
        assert lines.count(INIT_SHOW_LINE) == 1
        assert lines.count(DEPS_IMPORT_LINE) == 2  # wrapper + inlined base.typ

        main = tmp_path / "main.typ"
        main.write_text(source, encoding="utf-8")
        pdf = typst.compile(str(main), root=str(tmp_path))
        assert pdf.startswith(b"%PDF")

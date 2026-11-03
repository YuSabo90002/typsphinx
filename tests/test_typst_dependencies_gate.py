"""
Gate for the ``typst_dependencies`` config value (SC3, E2, E4, E6).

``typst_dependencies`` names one file (srcdir-relative, or absolute) that is
copied byte-identical to ``<outdir>/_typsphinx/deps.typ`` in place of the
generated default. ``None`` (the default) generates the default file; ``""``,
a non-``str`` value, or a path that is not an existing regular file stops the
build from ``TypstBuilder.write()`` before any ``.typ`` file is written, with
an error starting ``typst_dependencies:``.

Every build here is a real ``sys.executable -m sphinx`` subprocess under
``LC_ALL=C`` of a tmp copy of ``tests/fixtures/typst_dependencies_override/``,
whose ``conf.py`` sets ``typst_dependencies = "deps/my-deps.typ"`` -- the
default ``deps.typ`` with gentle-clues pinned to 1.3.0 instead of 1.3.1.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from typsphinx.pathfmt import quote_path
from typsphinx.typst_deps import DEPS_FILENAME, DEPS_OUTPUT_DIR, render_default_deps

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURE = Path(__file__).parent / "fixtures" / "typst_dependencies_override"
USER_DEPS_REL = "deps/my-deps.typ"

DEPS_IMPORT_LINE = '#import "/_typsphinx/deps.typ": *'
INIT_SHOW_LINE = "#show: typsphinx-init"
FIVE_SPEC_RE = re.compile(
    r"@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):"
)

DEFAULT_BYTES = render_default_deps().encode("utf-8")


def _copy_fixture(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    shutil.copytree(FIXTURE, src)
    return src


def _set_conf(src: Path, line: str) -> None:
    """Append one assignment to conf.py; the last assignment wins."""
    with open(src / "conf.py", "a", encoding="utf-8") as f:
        f.write("\n" + line + "\n")


def _build(
    src: Path,
    out: Path,
    builder: str = "typst",
    fresh: bool = True,
) -> subprocess.CompletedProcess:
    """Run ``sys.executable -m sphinx -b <builder>`` (``-E`` when fresh)."""
    args = [sys.executable, "-m", "sphinx"]
    if fresh:
        args.append("-E")
    args += [
        "-b",
        builder,
        str(src),
        str(out),
        "-d",
        str(out.parent / f"{out.name}-doctrees"),
    ]
    env = dict(os.environ, LC_ALL="C")
    return subprocess.run(args, capture_output=True, text=True, env=env)


def _deps_bytes(out: Path) -> bytes:
    return (out / DEPS_OUTPUT_DIR / DEPS_FILENAME).read_bytes()


def _all_typ_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.rglob("*.typ"))


def _emitted_typ_files(out: Path) -> list[Path]:
    """Content and wrapper ``.typ`` files: everything outside ``_typsphinx/``
    and ``_template/``."""
    return [
        p
        for p in _all_typ_files(out)
        if p.relative_to(out).parts[0] not in (DEPS_OUTPUT_DIR, "_template")
    ]


def _assert_refused(result: subprocess.CompletedProcess, out: Path) -> str:
    """The build failed with a ``typst_dependencies:`` error and wrote no
    ``.typ`` file anywhere."""
    output = result.stdout + result.stderr
    assert result.returncode != 0, output
    assert "typst_dependencies:" in output, output
    assert _all_typ_files(out) == [], _all_typ_files(out)
    return output


class TestRegistration:
    def test_default_is_none(self, tmp_path: Path) -> None:
        from sphinx.testing.util import SphinxTestApp

        src = tmp_path / "src"
        src.mkdir()
        (src / "conf.py").write_text('extensions = ["typsphinx"]\n')
        (src / "index.rst").write_text("Title\n=====\n")
        app = SphinxTestApp("typst", srcdir=src)
        try:
            assert "typst_dependencies" in app.config
            assert app.config.typst_dependencies is None
        finally:
            app.cleanup()


class TestOverride:
    """SC3: the user's file replaces the generated default, byte-identical."""

    def test_user_file_copied_byte_identical(self, tmp_path: Path) -> None:
        src = _copy_fixture(tmp_path)
        out = tmp_path / "out"
        result = _build(src, out)
        assert result.returncode == 0, result.stdout + result.stderr

        user_bytes = (src / USER_DEPS_REL).read_bytes()
        assert _deps_bytes(out) == user_bytes
        assert _deps_bytes(out) != DEFAULT_BYTES
        assert b"@preview/gentle-clues:1.3.0" in _deps_bytes(out)
        # Nothing else is written under _typsphinx/.
        assert sorted(os.listdir(out / DEPS_OUTPUT_DIR)) == [DEPS_FILENAME]

    @pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py not installed")
    def test_override_fixture_builds_pdf(self, tmp_path: Path) -> None:
        src = _copy_fixture(tmp_path)
        out = tmp_path / "out"
        result = _build(src, out, builder="typstpdf")
        assert result.returncode == 0, result.stdout + result.stderr

        assert list(out.glob("*.pdf")), sorted(os.listdir(out))
        assert _deps_bytes(out) == (src / USER_DEPS_REL).read_bytes()

        emitted = _emitted_typ_files(out)
        assert emitted, "no content or wrapper .typ was emitted"
        for typ in emitted:
            text = typ.read_text(encoding="utf-8")
            lines = text.splitlines()
            assert DEPS_IMPORT_LINE in lines, typ
            assert INIT_SHOW_LINE in lines, typ
            assert not FIVE_SPEC_RE.search(text), typ

    def test_missing_path_refused(self, tmp_path: Path) -> None:
        src = _copy_fixture(tmp_path)
        _set_conf(src, 'typst_dependencies = "missing/deps.typ"')
        out = tmp_path / "out"
        output = _assert_refused(_build(src, out), out)
        assert "typst_dependencies: file not found:" in output
        assert quote_path("missing/deps.typ") in output
        assert quote_path(os.path.join(str(src), "missing/deps.typ")) in output

    def test_directory_path_refused(self, tmp_path: Path) -> None:
        src = _copy_fixture(tmp_path)
        _set_conf(src, 'typst_dependencies = "deps"')
        out = tmp_path / "out"
        output = _assert_refused(_build(src, out), out)
        assert quote_path("deps") in output

    def test_non_str_value_refused(self, tmp_path: Path) -> None:
        src = _copy_fixture(tmp_path)
        _set_conf(src, "typst_dependencies = 5")
        out = tmp_path / "out"
        _assert_refused(_build(src, out), out)


class TestNoneAndEmpty:
    """E4: ``None`` generates the default file; ``""`` stops the build."""

    def test_explicit_none_generates_default(self, tmp_path: Path) -> None:
        src = _copy_fixture(tmp_path)
        _set_conf(src, "typst_dependencies = None")
        out = tmp_path / "out"
        result = _build(src, out)
        assert result.returncode == 0, result.stdout + result.stderr
        assert _deps_bytes(out) == render_default_deps().encode("utf-8")

    def test_empty_string_refused(self, tmp_path: Path) -> None:
        src = _copy_fixture(tmp_path)
        _set_conf(src, 'typst_dependencies = ""')
        out = tmp_path / "out"
        output = _assert_refused(_build(src, out), out)
        assert quote_path("") in output


class TestAbsoluteAndBytes:
    """E6: an absolute path is accepted; the file is copied as bytes."""

    def test_absolute_path_builds(self, tmp_path: Path) -> None:
        src = _copy_fixture(tmp_path)
        absolute = (src / USER_DEPS_REL).resolve()
        _set_conf(src, f"typst_dependencies = {str(absolute)!r}")
        out = tmp_path / "out"
        result = _build(src, out)
        assert result.returncode == 0, result.stdout + result.stderr
        assert _deps_bytes(out) == absolute.read_bytes()

    def test_crlf_non_ascii_no_trailing_newline_byte_identical(
        self, tmp_path: Path
    ) -> None:
        src = _copy_fixture(tmp_path)
        raw = (
            "// dépendances — 日本語\r\n"
            '#import "@preview/codly:1.3.0": *\r\n'
            "#let typsphinx-init(body) = body"
        ).encode()
        assert b"\r\n" in raw and not raw.endswith(b"\n")
        assert any(b > 0x7F for b in raw)
        outside = tmp_path / "elsewhere" / "odd-deps.typ"
        outside.parent.mkdir()
        outside.write_bytes(raw)
        _set_conf(src, f"typst_dependencies = {str(outside)!r}")
        out = tmp_path / "out"
        result = _build(src, out, builder="typst")
        assert result.returncode == 0, result.stdout + result.stderr
        assert _deps_bytes(out) == raw
        # The user's file is never modified (N3).
        assert outside.read_bytes() == raw


class TestRebuildAndSwitch:
    """E2: rebuilds give identical bytes; switching modes leaves the newly
    effective file, never the stale one."""

    @pytest.mark.parametrize("mode", ["set", "unset"])
    def test_rebuilds_identical_bytes(self, tmp_path: Path, mode: str) -> None:
        src = _copy_fixture(tmp_path)
        if mode == "unset":
            _set_conf(src, "typst_dependencies = None")
            expected = DEFAULT_BYTES
        else:
            expected = (src / USER_DEPS_REL).read_bytes()
        out = tmp_path / "out"

        first = _build(src, out, fresh=True)
        assert first.returncode == 0, first.stdout + first.stderr
        assert _deps_bytes(out) == expected

        incremental = _build(src, out, fresh=False)
        assert incremental.returncode == 0, incremental.stdout + incremental.stderr
        assert _deps_bytes(out) == expected

        full = _build(src, out, fresh=True)
        assert full.returncode == 0, full.stdout + full.stderr
        assert _deps_bytes(out) == expected

    def test_set_then_unset_then_set(self, tmp_path: Path) -> None:
        src = _copy_fixture(tmp_path)
        user_bytes = (src / USER_DEPS_REL).read_bytes()
        conf = src / "conf.py"
        set_conf = conf.read_text(encoding="utf-8")
        unset_conf = set_conf + "\ntypst_dependencies = None\n"
        out = tmp_path / "out"

        result = _build(src, out, fresh=False)
        assert result.returncode == 0, result.stdout + result.stderr
        assert _deps_bytes(out) == user_bytes

        conf.write_text(unset_conf, encoding="utf-8")
        result = _build(src, out, fresh=False)
        assert result.returncode == 0, result.stdout + result.stderr
        assert _deps_bytes(out) == DEFAULT_BYTES

        conf.write_text(set_conf, encoding="utf-8")
        result = _build(src, out, fresh=False)
        assert result.returncode == 0, result.stdout + result.stderr
        assert _deps_bytes(out) == user_bytes
        assert sorted(os.listdir(out / DEPS_OUTPUT_DIR)) == [DEPS_FILENAME]

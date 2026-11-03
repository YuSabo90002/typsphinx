"""
Gate for the template dependency drift warning (SC4, E7-E10).

After the used template bundles are copied to ``<outdir>/_template/<key>/``,
``TypstBuilder._warn_template_dependency_drift()`` scans every copied
``.typ`` file for ``@preview/<one of the five>:<version>`` pins (comments
excluded) and prints one warning per mismatched (file, package) against the
effective ``<outdir>/_typsphinx/deps.typ``. The build always exits 0 and no
copied file is modified.

Integration tests run real ``sys.executable -m sphinx -b typst`` builds of
tmp projects assembled from ``tests/fixtures/template_dependency_drift/``
under ``LC_ALL=C`` and assert on stderr. Unit tests call
``strip_typst_comments()`` / ``extract_preview_versions()`` directly.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from typsphinx.typst_deps import (
    DEFAULT_PACKAGES,
    extract_preview_versions,
    strip_typst_comments,
)

FIXTURES = Path(__file__).parent / "fixtures" / "template_dependency_drift"
TEMPLATE_BODY = (FIXTURES / "template_body.typ").read_text(encoding="utf-8")
DRIFT_MARKER = "template dependency drift: "

DEFAULT_VERSIONS = {p.name: p.version for p in DEFAULT_PACKAGES}


def _template(*import_lines: str) -> str:
    return "\n".join(import_lines) + "\n\n" + TEMPLATE_BODY


def _make_project(
    tmp_path: Path,
    files: dict[str, str],
    conf_extra: str = 'typst_template = "_typst/main.typ"\n',
) -> Path:
    """Assemble a project: fixture ``index.rst``, ``files`` (srcdir-relative
    path -> text), and a ``conf.py`` ending with ``conf_extra``."""
    src = tmp_path / "src"
    src.mkdir()
    shutil.copy(FIXTURES / "index.rst", src / "index.rst")
    for rel, text in files.items():
        dest = src / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    (src / "conf.py").write_text(
        'project = "Drift Gate"\n'
        'author = "Test Author"\n'
        'extensions = ["typsphinx"]\n'
        'typst_documents = [("index", "manual.typ", "Drift Gate", "Test Author")]\n'
        + conf_extra,
        encoding="utf-8",
    )
    return src


def _build(src: Path) -> tuple[Path, subprocess.CompletedProcess]:
    out = src.parent / "out"
    env = dict(os.environ, LC_ALL="C")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-E",
            "-b",
            "typst",
            str(src),
            str(out),
            "-d",
            str(src.parent / "doctrees"),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    return out, result


def _drift_messages(result: subprocess.CompletedProcess) -> list[str]:
    return [
        line[line.index(DRIFT_MARKER) :]
        for line in result.stderr.splitlines()
        if DRIFT_MARKER in line
    ]


def _message(relpath: str, package: str, template: str, deps: str) -> str:
    return (
        f"template dependency drift: '{relpath}' pins "
        f"@preview/{package}:{template}, but _typsphinx/deps.typ has "
        f"@preview/{package}:{deps}"
    )


def _assert_byte_identical(src: Path, out: Path) -> None:
    bundle_src = src / "_typst"
    for source in bundle_src.rglob("*"):
        if source.is_file():
            copy = out / "_template" / "typst" / source.relative_to(bundle_src)
            assert copy.read_bytes() == source.read_bytes(), copy


class TestSC4DefaultMode:
    """SC4 against the generated default ``deps.typ``."""

    def test_mismatch_warns_once_and_exits_zero(self, tmp_path):
        src = _make_project(
            tmp_path,
            {"_typst/main.typ": _template('#import "@preview/gentle-clues:1.2.0": *')},
        )
        out, result = _build(src)
        assert _drift_messages(result) == [
            _message(
                "_template/typst/main.typ",
                "gentle-clues",
                "1.2.0",
                DEFAULT_VERSIONS["gentle-clues"],
            )
        ]
        _assert_byte_identical(src, out)

    def test_matching_version_is_silent(self, tmp_path):
        src = _make_project(
            tmp_path,
            {
                "_typst/main.typ": _template(
                    f'#import "@preview/gentle-clues:{DEFAULT_VERSIONS["gentle-clues"]}": *',
                    f'#import "@preview/codly:{DEFAULT_VERSIONS["codly"]}": *',
                )
            },
        )
        _, result = _build(src)
        assert _drift_messages(result) == []

    def test_no_import_is_silent(self, tmp_path):
        src = _make_project(tmp_path, {"_typst/main.typ": _template()})
        _, result = _build(src)
        assert _drift_messages(result) == []

    def test_default_template_is_silent(self, tmp_path):
        src = _make_project(tmp_path, {}, conf_extra="")
        _, result = _build(src)
        assert _drift_messages(result) == []

    def test_several_versions_in_one_file_sorted_numerically(self, tmp_path):
        src = _make_project(
            tmp_path,
            {
                "_typst/main.typ": _template(
                    '#import "@preview/codly:1.10.0": *',
                    '#import "@preview/codly:1.2.0": *',
                    f'#import "@preview/codly:{DEFAULT_VERSIONS["codly"]}": *',
                )
            },
        )
        _, result = _build(src)
        assert _drift_messages(result) == [
            _message(
                "_template/typst/main.typ",
                "codly",
                "1.2.0, 1.10.0",
                DEFAULT_VERSIONS["codly"],
            )
        ]


class TestSC4OverrideMode:
    """SC4 against a user ``typst_dependencies`` file."""

    CONF = (
        'typst_template = "_typst/main.typ"\n'
        'typst_dependencies = "deps/user_deps.typ"\n'
    )

    def _files(self, *imports: str) -> dict[str, str]:
        return {
            "_typst/main.typ": _template(*imports),
            "deps/user_deps.typ": (FIXTURES / "user_deps.typ").read_text(
                encoding="utf-8"
            ),
        }

    def test_compares_against_user_file(self, tmp_path):
        src = _make_project(
            tmp_path,
            self._files('#import "@preview/gentle-clues:1.3.1": *'),
            self.CONF,
        )
        out, result = _build(src)
        assert _drift_messages(result) == [
            _message("_template/typst/main.typ", "gentle-clues", "1.3.1", "1.3.0")
        ]
        _assert_byte_identical(src, out)
        assert (out / "_typsphinx" / "deps.typ").read_bytes() == (
            src / "deps" / "user_deps.typ"
        ).read_bytes()

    def test_matching_user_version_is_silent(self, tmp_path):
        src = _make_project(
            tmp_path,
            self._files('#import "@preview/gentle-clues:1.3.0": *'),
            self.CONF,
        )
        _, result = _build(src)
        assert _drift_messages(result) == []

    def test_e9_package_missing_from_user_deps_is_not_compared(self, tmp_path):
        src = _make_project(
            tmp_path,
            self._files(
                '#import "@preview/diagraph:0.1.0": render',
                '#import "@preview/mitex:0.2.5": mi',
            ),
            self.CONF,
        )
        _, result = _build(src)
        assert _drift_messages(result) == [
            _message("_template/typst/main.typ", "mitex", "0.2.5", "0.2.7")
        ]


class TestE7Adjacency:
    def test_other_package_and_other_namespace_are_ignored(self, tmp_path):
        src = _make_project(
            tmp_path,
            {
                "_typst/main.typ": _template(
                    '#import "@preview/charged-ieee:0.1.0": *',
                    '#import "@local/codly:9.9.9": *',
                )
            },
        )
        _, result = _build(src)
        assert _drift_messages(result) == []


class TestE8Ordering:
    def test_one_warning_per_file_and_package_in_sorted_order(self, tmp_path):
        src = _make_project(
            tmp_path,
            {
                "_typst/main.typ": _template(
                    '#import "@preview/gentle-clues:1.2.0": *',
                    '#import "@preview/codly:1.0.0": *',
                ),
                "_typst/extra.typ": '#import "@preview/gentle-clues:1.2.0": *\n',
            },
        )
        _, result = _build(src)
        gc = DEFAULT_VERSIONS["gentle-clues"]
        assert _drift_messages(result) == [
            _message("_template/typst/extra.typ", "gentle-clues", "1.2.0", gc),
            _message(
                "_template/typst/main.typ",
                "codly",
                "1.0.0",
                DEFAULT_VERSIONS["codly"],
            ),
            _message("_template/typst/main.typ", "gentle-clues", "1.2.0", gc),
        ]


class TestE10Comments:
    def test_pins_inside_comments_do_not_warn(self, tmp_path):
        src = _make_project(
            tmp_path,
            {
                "_typst/main.typ": _template(
                    '// #import "@preview/codly:1.0.0": *',
                    '/* #import "@preview/mitex:0.0.1": mi */',
                    '/* outer /* inner */ #import "@preview/diagraph:0.0.1": render */',
                    '#let x = 1 // trailing "@preview/gentle-clues:0.0.1"',
                )
            },
        )
        _, result = _build(src)
        assert _drift_messages(result) == []

    def test_url_string_does_not_hide_a_real_pin(self, tmp_path):
        src = _make_project(
            tmp_path,
            {
                "_typst/main.typ": _template(
                    '#let home = "https://example.com"; '
                    '#import "@preview/gentle-clues:1.2.0": *',
                )
            },
        )
        _, result = _build(src)
        assert _drift_messages(result) == [
            _message(
                "_template/typst/main.typ",
                "gentle-clues",
                "1.2.0",
                DEFAULT_VERSIONS["gentle-clues"],
            )
        ]


class TestScanScope:
    """AC6: only files copied for used keys are scanned."""

    def test_unused_key_and_excluded_entries_are_not_scanned(self, tmp_path):
        drift = '#import "@preview/gentle-clues:1.2.0": *\n'
        src = _make_project(
            tmp_path,
            {
                "_typst/main.typ": _template(),
                "_typst/.git/hooks.typ": drift,
                "_typst/backup.typ~": drift,
                "_unused/other.typ": _template(drift),
            },
            conf_extra=(
                "typst_document_templates = {\n"
                '    "used": {"template": "_typst/main.typ"},\n'
                '    "unused": {"template": "_unused/other.typ"},\n'
                "}\n"
                'typst_documents = [("index", "manual.typ", "Drift Gate", '
                '"Test Author", "used")]\n'
            ),
        )
        out, result = _build(src)
        assert _drift_messages(result) == []
        assert not (out / "_template" / "unused").exists()
        used = out / "_template" / "used"
        assert (used / "main.typ").read_bytes() == (
            src / "_typst" / "main.typ"
        ).read_bytes()
        assert not (used / ".git").exists()
        assert not (used / "backup.typ~").exists()

    def test_package_only_key_is_skipped(self, tmp_path):
        src = _make_project(
            tmp_path,
            {},
            conf_extra=(
                'typst_package = "@preview/charged-ieee:0.1.4"\n'
                'typst_template_function = "ieee"\n'
            ),
        )
        out, result = _build(src)
        assert _drift_messages(result) == []
        assert not (out / "_template").exists()


class TestStripTypstComments:
    def test_line_comment_removed_newline_kept(self):
        assert strip_typst_comments("a // b\nc") == "a \nc"

    def test_block_comment_replaced(self):
        assert strip_typst_comments("a/* b */c") == "a c"

    def test_nested_block_comment(self):
        assert strip_typst_comments("a /* x /* y */ z */ b") == "a   b"

    def test_unterminated_block_comment_runs_to_end(self):
        assert strip_typst_comments("a /* b\nc") == "a  "

    def test_string_with_slashes_is_kept(self):
        text = '#let u = "https://example.com" // gone'
        assert strip_typst_comments(text) == '#let u = "https://example.com" '

    def test_string_escape_is_honoured(self):
        text = '"a\\"b // c" // d'
        assert strip_typst_comments(text) == '"a\\"b // c" '

    def test_string_ends_at_end_of_line(self):
        text = '"open\n// comment\nx'
        assert strip_typst_comments(text) == '"open\n\nx'

    def test_comment_markers_inside_string_are_kept(self):
        assert strip_typst_comments('"/* x */"') == '"/* x */"'


class TestExtractPreviewVersions:
    def test_codly_does_not_match_codly_languages(self):
        assert extract_preview_versions('"@preview/codly-languages:0.1.10"') == {
            "codly-languages": {"0.1.10"}
        }

    def test_codly_and_codly_languages(self):
        text = '"@preview/codly:1.3.0" "@preview/codly-languages:0.1.10"'
        assert extract_preview_versions(text) == {
            "codly": {"1.3.0"},
            "codly-languages": {"0.1.10"},
        }

    def test_other_namespace_and_package_ignored(self):
        text = '"@local/codly:9.9.9" "@preview/charged-ieee:0.1.0"'
        assert extract_preview_versions(text) == {}

    def test_comments_excluded(self):
        text = '// "@preview/mitex:0.0.1"\n/* "@preview/diagraph:0.0.1" */'
        assert extract_preview_versions(text) == {}

    def test_all_versions_collected(self):
        text = '"@preview/mitex:0.2.5" "@preview/mitex:0.2.7" "@preview/mitex:0.2.5"'
        assert extract_preview_versions(text) == {"mitex": {"0.2.5", "0.2.7"}}

    def test_default_deps_round_trip(self):
        from typsphinx.typst_deps import render_default_deps

        assert extract_preview_versions(render_default_deps()) == {
            name: {version} for name, version in DEFAULT_VERSIONS.items()
        }

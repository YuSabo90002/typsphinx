"""
IMG-07 (Phase 59 plan 04): two gates over the SAME Windows-shaped absolute
image URI fixture (``tests/fixtures/windows_shaped_image_uri_gate/``),
proving that BOTH IMG-04 (the relocation key's backslash-free basename
normalization, ``typsphinx/builder.py``) and IMG-05 (``visit_image()``'s
escape-last wiring, ``typsphinx/translator.py``) are load-bearing --
D-01's four-combination table (59-CONTEXT.md).

The two classes below are deliberately independent, run on different
subsets of CI lanes, and never share a skip condition:

- ``TestWindowsShapedImageUriStringShape`` runs on EVERY lane, including
  ``windows-latest``. It drives ``-b typst`` in the fixture's default
  "string" mode -- no file with an illegal Windows filename is ever
  created -- and asserts three properties of the emitted
  ``image("...")`` literal's contents. It carries NO skip of any kind:
  it needs no filesystem support for a backslash-and-quote basename, so
  it is what makes this phase's Windows-lane claim mean something
  despite the compile gate's own skip.

- ``TestWindowsShapedImageUriCompileGate`` can only run where the
  filesystem can hold a basename containing both a backslash and a
  double quote (illegal on NTFS), so it skips via a MEASURED runtime
  probe inside the test body -- never a collection-time marker decorator
  that references a fixture-scoped value, and never a branch on
  ``os.name`` (D-03). It drives a REAL ``typst.compile()`` through
  ``-b typstpdf`` and proves the fixture's own copied asset compiles to
  a genuine PDF.

Both classes share ``_assert_image_literal_escaped_and_separator_free()``
so the string-level claim and the compile-level claim can never drift
apart from one another.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from typsphinx.translator import escape_typst_string

FIXTURES_DIR = Path(__file__).parent / "fixtures"
WINDOWS_SHAPED_IMAGE_URI_GATE_FIXTURE_DIR = (
    FIXTURES_DIR / "windows_shaped_image_uri_gate"
)

# Honors backslash escapes inside the Typst string literal: a character
# class of "not a quote and not a backslash" alternated with "backslash
# followed by any character", so a `\"` inside the literal does not
# terminate the match early.
_IMAGE_LITERAL_RE = re.compile(r'image\("((?:[^"\\]|\\.)*)"\)')


def _run_sphinx_build(
    source_dir: Path,
    build_dir: Path,
    builder: str,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never a resolved builder-
    script binary on PATH, nor via a package-manager-run wrapper) so the
    exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard. Every gate module in
    this suite carries its own copy of this helper rather than importing
    a sibling module's.

    ``env``, when given, is a mapping of extra variables MERGED on top of
    a copy of the current process environment (not a replacement), so
    the subprocess still inherits PATH and the active venv.
    """
    subprocess_env = None
    if env is not None:
        subprocess_env = dict(os.environ)
        subprocess_env.update(env)

    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            builder,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
        env=subprocess_env,
    )


def _extract_first_image_literal(typ_text: str) -> str:
    """Return the contents of the first ``image("...")`` literal found in
    ``typ_text``, honoring backslash escapes inside the literal."""
    match = _IMAGE_LITERAL_RE.search(typ_text)
    assert (
        match is not None
    ), f'No image("...") literal found in the emitted .typ:\n{typ_text}'
    return match.group(1)


def _assert_image_literal_escaped_and_separator_free(typ_text: str) -> str:
    """Extract the first ``image("...")`` literal from ``typ_text`` and
    assert all three of D-04's properties on it. Returns the extracted
    literal so callers can log/echo it.

    Shared by BOTH ``TestWindowsShapedImageUriStringShape`` and
    ``TestWindowsShapedImageUriCompileGate`` so the string-level claim
    and the compile-level claim cannot drift apart.
    """
    literal = _extract_first_image_literal(typ_text)

    # (1) Every backslash inside the literal is immediately followed by a
    # double quote -- i.e. a search for a backslash NOT followed by a
    # double quote finds nothing. Fails on the unfixed tree (raw
    # separator backslashes) and also fails when only the escaping half
    # is present (the separator backslash becomes a doubled backslash).
    stray_backslash = re.search(r'\\(?!")', literal)
    assert stray_backslash is None, (
        f"Found a backslash NOT immediately followed by a double quote "
        f"(a raw separator backslash, or a doubled escape from escaping "
        f"without key normalization) in literal {literal!r}"
    )

    # (2) The literal contains an escaped double quote. Fails when only
    # the key-normalization half (IMG-04) is present (the quote is still
    # raw). The expected escaped fragment is built by calling the REAL
    # escape_typst_string() -- never a re-pasted literal -- so a product
    # regression to the escaping rule itself would also turn this
    # assertion's own expectation stale, not just silently pass.
    expected_escaped_quote = escape_typst_string('"')
    assert expected_escaped_quote in literal, (
        f"Expected an escaped double quote ({expected_escaped_quote!r}) "
        f"in literal {literal!r}"
    )

    # (3) Neither the drive fragment nor the directory fragment survived
    # as part of the "basename" -- proving the whole raw URI did not
    # leak through.
    assert (
        "C:" not in literal
    ), f"Raw drive fragment 'C:' survived in literal {literal!r}"
    assert (
        "Users" not in literal
    ), f"Raw directory fragment 'Users' survived in literal {literal!r}"

    return literal


class TestWindowsShapedImageUriStringShape:
    """D-04: the all-lane, no-filesystem-required string-shape gate. Runs
    unconditionally on every CI lane, including ``windows-latest``,
    because it never creates a file with an illegal basename and never
    calls ``typst.compile()``."""

    def test_string_shape_emitted_image_literal_is_escaped_and_separator_free(
        self, tmp_path
    ):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            WINDOWS_SHAPED_IMAGE_URI_GATE_FIXTURE_DIR,
            build_dir,
            "typst",
            env={"TYPSPHINX_WIN_URI_MODE": "string"},
        )

        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = build_dir / "index.typ"
        assert typ_output.exists(), "index.typ (the content document) was not generated"
        typ_text = typ_output.read_text(encoding="utf-8")

        literal = _assert_image_literal_escaped_and_separator_free(typ_text)
        assert literal, f"Extracted an empty image(...) literal from:\n{typ_text}"

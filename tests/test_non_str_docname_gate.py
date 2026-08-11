"""
BLD-01: real-``sphinx-build`` must-fail regression gate for a non-``str``
docname reaching ``TypstPDFBuilder.finish()`` (Phase 44, plan 44-02).

Before this plan, a ``typst_documents`` entry whose docname was not a
``str`` (e.g. an ``int``) reached ``posixpath.dirname(docname)`` inside
``_directory_preserving_relpath`` and raised a raw, uncaught ``TypeError``
that killed the whole ``sphinx-build`` process with a bare traceback --
before the ``try:`` block that aggregates into the existing ``failures``
list ever ran. This gate proves the guard added by this plan reports the
problem through that same ``failures`` list / terminal ``ExtensionError``
instead: the build still exits non-zero, but the message names the
offending value and the build's one valid master still gets its ``.typ``
and ``.pdf`` written to disk (D-02's attempt-all-then-raise contract, the
same contract ``test_missing_and_malformed_master_gate.py`` already proves
for the other two failure kinds).

Only typsphinx-authored strings are ever read from stderr here -- the
aggregate ``ExtensionError`` body and the new guard's own message. Never a
``typst-py`` compiler diagnostic, and never Sphinx-core's own CLI traceback
banner formatting.
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GATE_FIXTURE_DIR = FIXTURES_DIR / "non_str_docname_gate"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.
    """
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
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the non-str-docname gate",
)
class TestNonStrDocnameGate:
    """
    Real-``sphinx-build`` regression gate proving BLD-01's type guard end to
    end: a build with one valid master and one entry whose docname is an
    int exits non-zero with a typsphinx-authored message naming the
    offending value, while the valid master still compiles to a real PDF.

    Requirements: BLD-01.
    """

    def test_non_str_docname_fails_build_but_good_master_still_compiles(self, tmp_path):
        """
        A build over the fixture fails overall, but the one valid master
        (``index``) still compiles to a real PDF, and no raw ``TypeError``
        reaches stderr -- the crash is caught, not merely relocated.
        """
        build_dir = tmp_path / "build_non_str_docname"
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typstpdf")

        # Assert inequality, not a specific exit code -- the exact non-zero
        # value is Sphinx CLI's own convention, not a typsphinx contract.
        assert result.returncode != 0, (
            f"Expected a non-zero exit for a build with a non-str docname "
            f"in typst_documents, but the build reported success:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert "typst_documents entry has a non-str docname" in result.stderr, (
            f"Expected the typsphinx-authored guard message in stderr:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "123" in result.stderr, (
            f"Expected the offending value (123) to be named in stderr:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "1 master document(s) failed" in result.stderr, (
            f"Expected the aggregate message to report exactly 1 failure "
            f"(the non-str docname entry; the valid master is not a "
            f"failure):\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # BLD-01 regression: the crash must be caught, not merely relocated.
        # "TypeError" is a Python builtin name, not an upstream diagnostic
        # string, so asserting its absence does not couple this module to
        # uncontracted upstream presentation.
        assert "TypeError" not in result.stderr, (
            f"A non-str docname aborted the build with a raw TypeError "
            f"instead of being reported by finish()'s aggregate "
            f"ExtensionError (BLD-01):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # The CONTENT file (R1, docname-derived, unconditional) -- unaffected
        # by the wrapper's target rename.
        assert (build_dir / "index.typ").exists(), (
            f"The valid master's content file was not written before the "
            f"aggregate failure:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        index_typ_content = (build_dir / "index.typ").read_text(encoding="utf-8")
        assert "NONSTRBODY" in index_typ_content, (
            f"Expected the sentinel NONSTRBODY in index.typ:\n" f"{index_typ_content}"
        )
        # The WRAPPER file's PDF (R4) -- master.typ/master.pdf per the
        # fixture's de-collided target.
        assert (build_dir / "master.pdf").exists(), (
            f"D-02's attempt-all-then-raise contract failed end to end: "
            f"the valid master should still get its PDF even though the "
            f"build as a whole fails:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        with open(build_dir / "master.pdf", "rb") as f:
            assert (
                f.read(4) == b"%PDF"
            ), "master.pdf does not start with the PDF magic bytes"

        assert not (build_dir / "manual.typ").exists(), (
            f"No .typ should exist for the bad entry's target name:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert not (build_dir / "manual.pdf").exists(), (
            f"No .pdf should exist for the bad entry's target name:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

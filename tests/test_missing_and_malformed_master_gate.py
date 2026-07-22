"""
GATE-01: real-``sphinx-build`` must-fail regression gate for
``TypstPDFBuilder.finish()``'s widened failure handling (Phase 22.3, WR-01,
D-11).

This is the suite's FIRST must-fail subprocess gate: every sibling GATE-01
module in this suite (``test_package_only_config_gate.py``,
``test_nested_master_render_gate.py``, ``test_target_name_render_gate.py``,
...) asserts a zero exit code -- a real compile succeeding. This module
asserts the opposite, ``result.returncode != 0``, on purpose. Do NOT
"correct" that polarity to match the siblings; the inversion is the point.

Before Phase 22.3's plan ``22.3-01``, ``TypstPDFBuilder.finish()`` silently
skipped (``logger.warning(...); continue``) both a configured master whose
``.typ`` was never generated and a malformed ``typst_documents`` entry --
``sphinx-build`` exited 0 while producing no PDF for either. WR-01 closes
that silent-success gap: both failure kinds now append to the same
``failures`` list that a Typst compile error already used, and a single
aggregate ``sphinx.errors.ExtensionError`` is raised after every configured
master has been attempted (D-02's attempt-all-then-raise contract). This
gate's fixture (``tests/fixtures/missing_and_malformed_master_gate/``)
combines one valid master with BOTH bad-entry kinds in a single build, so
one real ``sphinx-build -b typstpdf`` run proves the whole contract
end-to-end: the build fails, AND the valid master's PDF is still written to
disk (the good master is never short-circuited by the bad ones).

Only typsphinx-authored strings are ever read from stderr here -- the
aggregate ``ExtensionError`` body and the two guard messages
``typsphinx/builder.py`` itself emits. Never a ``typst-py`` compiler
diagnostic, and never Sphinx-core's own CLI traceback banner formatting --
both are uncontracted upstream presentation surfaces, and coupling this new
module to either would recreate, in a brand-new module in this same phase,
the exact defect class WR-02 removes from
``tests/test_nested_master_render_gate.py``.
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
GATE_FIXTURE_DIR = FIXTURES_DIR / "missing_and_malformed_master_gate"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every GATE-01 module in this suite carries its
    own copy of this helper rather than importing a sibling module's.
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
    reason="typst-py is required for the missing/malformed-master gate",
)
class TestMissingAndMalformedMasterGate:
    """
    Real-``sphinx-build`` regression gate proving WR-01's widened failure
    handling end to end: a build with one unknown-docname master and one
    malformed ``typst_documents`` entry exits non-zero, while the fixture's
    one valid master still gets its PDF written to disk.

    Requirements: WR-01.
    """

    def test_mixed_bad_entries_fail_build_but_good_master_still_compiles(
        self, tmp_path
    ):
        """
        A build over the mixed fixture fails overall, but the one valid
        master (``index``) still compiles to a real PDF -- D-02's
        attempt-all-then-raise contract survives end to end, at the
        subprocess level, not merely at the unit level.
        """
        build_dir = tmp_path / "build_mixed"
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typstpdf")

        # This is the suite's FIRST must-fail subprocess assertion -- assert
        # inequality, not a specific exit code. The exact non-zero value is
        # Sphinx CLI's own convention, not a typsphinx contract, so a future
        # maintainer must not "correct" this polarity back to `== 0`.
        assert result.returncode != 0, (
            f"Expected a non-zero exit for a build with a known-bad "
            f"typst_documents (unknown docname + malformed entry), but the "
            f"build reported success:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        assert "master document(s) failed" in result.stderr, (
            f"Expected the typsphinx-authored aggregate ExtensionError "
            f"fragment 'master document(s) failed' in stderr:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "2 master document(s) failed" in result.stderr, (
            f"Expected the aggregate message to report exactly 2 failures "
            f"(the unknown docname + the malformed entry; the valid master "
            f"is not a failure):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        assert (build_dir / "index.typ").exists(), (
            f"The valid master's .typ was not written before the aggregate "
            f"failure:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "index.pdf").exists(), (
            f"D-02's attempt-all-then-raise contract failed end to end: "
            f"the valid master should still get its PDF even though the "
            f"build as a whole fails:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        assert not (build_dir / "ghost.typ").exists(), (
            f"No .typ should exist for the unknown docname 'ghost':\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert not (build_dir / "ghost.pdf").exists(), (
            f"No .pdf should exist for the unknown docname 'ghost':\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_aggregate_message_discriminates_unknown_docname_from_missing_file(
        self, tmp_path
    ):
        """
        The aggregate message's discussion of the unknown docname 'ghost'
        takes D-04's found_docs-discriminating branch, never the fallback
        branch reserved for a known docname whose .typ simply wasn't
        generated (WR-01/adjacency probe), and reports the two bad entries
        in typst_documents iteration order (WR-01/ordering probe).
        """
        build_dir = tmp_path / "build_mixed_message"
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typstpdf")

        assert result.returncode != 0, (
            f"Expected a non-zero exit:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        stderr = result.stderr

        assert "ghost" in stderr, (
            f"Expected the unknown docname 'ghost' to be named in the "
            f"aggregate message:\nstdout: {result.stdout}\nstderr: {stderr}"
        )
        assert "is not a known Sphinx document" in stderr, (
            f"Expected D-04's found_docs-discriminating fragment for the "
            f"unknown docname 'ghost':\nstdout: {result.stdout}\n"
            f"stderr: {stderr}"
        )
        assert "Master document not found" not in stderr, (
            f"The unknown docname 'ghost' must take D-04's new "
            f"found_docs-discriminating branch, never the fallback branch "
            f"reserved for a known docname whose .typ was never generated "
            f"-- proving the two branches never collide (WR-01/adjacency "
            f"probe):\nstdout: {result.stdout}\nstderr: {stderr}"
        )

        assert "(): malformed typst_documents entry" in stderr, (
            f"Expected D-07's repr(doc_tuple) identifier for the malformed "
            f"empty entry:\nstdout: {result.stdout}\nstderr: {stderr}"
        )

        ghost_pos = stderr.find("ghost")
        malformed_pos = stderr.find("(): malformed typst_documents entry")
        assert ghost_pos != -1 and malformed_pos != -1, (
            f"Both the 'ghost' fragment and the malformed-entry fragment "
            f"must be present to compare their order:\nstderr: {stderr}"
        )
        assert ghost_pos < malformed_pos, (
            f"Expected the aggregate message to report failures in "
            f"typst_documents iteration order -- 'ghost' (entry 2) before "
            f"the malformed entry (entry 3) (WR-01/ordering probe):\n"
            f"stderr: {stderr}"
        )

        assert "failed to compile to PDF" not in stderr, (
            f"D-02's broadened aggregate wording should be in effect, not "
            f"the older compile-only wording:\nstdout: {result.stdout}\n"
            f"stderr: {stderr}"
        )

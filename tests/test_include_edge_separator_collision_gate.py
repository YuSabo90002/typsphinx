"""
Phase 55 plan 02, Task 1 (BLD-07): real ``sphinx-build`` plus
``typst.compile()`` gate for the include-edge separator collision --
``make_include_edge_key()`` does not escape its own ``#``/``>`` separators,
so a docname containing either character can collide two structurally
different include edges onto one key. D-05 sets this defect's RED evidence
at the REAL-COMPILE level (not unit level, unlike BLD-08 in the same plan):
a collided key makes a guard that must stay dark fire instead, and the
child's content is silently DUPLICATED in the compiled output -- only a
real compile shows that. See
``.planning/phases/55-v0-8-0-derived-defects/55-02-RED-EVIDENCE.md`` for the
verbatim pre-fix transcripts this module produced.

The source tree this module builds is never committed under
``tests/fixtures/``. First, the collision REQUIRES a docname containing a
literal ``>``, which is a reserved Windows filename character -- a
committed fixture would break ``git checkout`` on the ``windows-latest`` CI
lane for the entire repository. Second, the number sign alone cannot
construct the hazard (the emitted key still has exactly one ``>``, so
parent and child stay separable), so the ``>`` is unavoidable and the whole
module is skipped on Windows instead.
"""

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# Windows reserves `>` as a filename character (`b#0>c.rst`, `a#0>b.rst`
# below could never be checked out there); the source tree is built at
# runtime specifically so this module never needs a committed fixture of
# that shape. Skip the whole module rather than skip individual tests, so
# a Windows run reports one clear skip reason instead of N.
pytestmark = pytest.mark.skipif(
    os.name == "nt",
    reason=(
        "BLD-07's collision fixture requires a docname containing a "
        "literal '>', which is a reserved Windows filename character; the "
        "source tree is built at runtime (never committed) and this "
        "module is skipped entirely on Windows rather than shipping a "
        "fixture that would break `git checkout` there"
    ),
)


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """Run ``sphinx-build -b typstpdf`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, per this
    repo's established NixOS-sandbox-safe convention -- every gate module
    in this suite carries its own copy of this helper rather than
    importing a sibling module's (see
    ``tests/test_xref_compile_time_guard_render_gate.py``'s own copy).
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """Return the concatenated extracted text of every page in the
    compiled PDF's bytes."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() for page in reader.pages)


def _build_source_tree(root: Path) -> None:
    """Write the BLD-07 collision source tree into ``root`` (a
    ``tmp_path``-derived directory, never a committed fixture -- see the
    module docstring).

    Reproduces the exact shape measured this planning session (55-CONTEXT.md
    "Measured findings", item 1): docnames ``index``, ``c``, ``a``,
    ``a#0>b``, ``b#0>c``, where ``index`` toctrees ``c``, ``a``, ``a#0>b``
    in that order; ``a`` toctrees ``b#0>c``; and ``a#0>b`` toctrees ``c``.

    Load-bearing properties -- do NOT change any of these, or this tree
    silently stops constructing the collision:
      - The four non-index docnames (``c``, ``a``, ``a#0>b``, ``b#0>c``)
        must keep their exact spellings -- those spellings ARE the
        collision (``a`` -> ``b#0>c`` and ``a#0>b`` -> ``c`` both derive
        the raw key text ``a#0>b#0>c`` before the fix).
      - ``index``'s toctree order must stay ``c``, ``a``, ``a#0>b`` (in
        that order) -- ``c`` being claimed by ``index`` FIRST is what
        makes ``a#0>b``'s own edge to ``c`` dark (first-encounter-wins,
        COMP-05), which is the edge whose guard must NOT fire.
      - If the edge-key format (``<parent>#<occurrence>><child>``) ever
        changes, this tree stops constructing the hazard and must be
        revisited.
    """
    (root / "conf.py").write_text(
        (
            "project = 'Include Edge Separator Collision Gate'\n"
            "author = 'Probe Author'\n"
            "release = '1.0'\n"
            "\n"
            "extensions = ['typsphinx']\n"
            "\n"
            "typst_documents = [\n"
            "    ('index', 'manual.typ', 'Include Edge Separator "
            "Collision Gate', 'Probe Author'),\n"
            "]\n"
        ),
        encoding="utf-8",
    )
    (root / "index.rst").write_text(
        "Index\n"
        "=====\n"
        "\n"
        ".. toctree::\n"
        "   :maxdepth: 2\n"
        "\n"
        "   c\n"
        "   a\n"
        "   a#0>b\n",
        encoding="utf-8",
    )
    (root / "c.rst").write_text(
        "C\n=\n\nSHAREDCHILDCOLLISIONMARKER\n",
        encoding="utf-8",
    )
    (root / "a.rst").write_text(
        "A\n=\n\n.. toctree::\n   :maxdepth: 2\n\n   b#0>c\n",
        encoding="utf-8",
    )
    (root / "a#0>b.rst").write_text(
        "AZeroGtB\n========\n\n.. toctree::\n   :maxdepth: 2\n\n   c\n",
        encoding="utf-8",
    )
    (root / "b#0>c.rst").write_text(
        "BZeroGtC\n========\n\nFOURTHDOCUMENTMARKER\n",
        encoding="utf-8",
    )


@pytest.fixture(scope="class")
def collision_build(tmp_path_factory):
    """Build the BLD-07 collision source tree ONCE per class via
    ``-b typstpdf`` and return the compiled ``manual.pdf`` bytes plus the
    emitted wrapper/content files' text."""
    source_dir = tmp_path_factory.mktemp("bld07_source")
    _build_source_tree(source_dir)
    build_dir = tmp_path_factory.mktemp("bld07_build")
    result = _run_sphinx_build_typstpdf(source_dir, build_dir)

    def _read_text(name: str) -> str:
        path = build_dir / name
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _read_bytes(name: str) -> bytes:
        path = build_dir / name
        return path.read_bytes() if path.exists() else b""

    return {
        "result": result,
        "manual_typ": _read_text("manual.typ"),
        "a_typ": _read_text("a.typ"),
        "a_hash_b_typ": _read_text("a#0>b.typ"),
        "manual_pdf": _read_bytes("manual.pdf"),
    }


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the BLD-07 collision gate",
)
class TestIncludeEdgeSeparatorCollisionGate:
    """BLD-07: two structurally different include edges no longer collide
    onto one key -- proven on a real ``sphinx-build -b typstpdf`` plus
    ``typst.compile()``."""

    def test_build_succeeds_and_produces_manual_pdf(self, collision_build):
        """An invariance guard -- true before and after the fix."""
        result = collision_build["result"]
        assert result.returncode == 0, (
            f"expected a clean build, got exit code {result.returncode}:\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert collision_build["manual_pdf"], "manual.pdf was not written"

    def test_shared_child_marker_appears_exactly_once(self, collision_build):
        """RED today: the dark edge's guard (``a#0>b`` -> ``c``) collides
        onto the same key as the live edge's guard (``a`` -> ``b#0>c``),
        so it wrongly fires and includes ``c.typ`` a second time -- the
        shared child's marker appears TWICE in the compiled PDF instead of
        once."""
        text = _extract_pdf_text(collision_build["manual_pdf"])
        child_count = text.count("SHAREDCHILDCOLLISIONMARKER")
        fourth_count = text.count("FOURTHDOCUMENTMARKER")
        assert child_count == 1, (
            "expected the shared child's marker "
            "('SHAREDCHILDCOLLISIONMARKER') to appear exactly once in the "
            f"compiled PDF, got {child_count} occurrences (the fourth "
            f"document's own marker, 'FOURTHDOCUMENTMARKER', appeared "
            f"{fourth_count} times) -- BLD-07: a collided include-edge key "
            f"made a guard that must stay dark fire, duplicating the "
            f"shared child's content"
        )

    def test_published_array_and_two_guards_use_distinct_keys(self, collision_build):
        """The emitted ``manual.typ`` publishes an array containing the
        live edge's key and NOT the dark edge's key, and the two content
        files' guard lines test two DIFFERENT keys. Both expected keys are
        derived by calling the product's own single derivation point
        (``make_include_edge_key``), never hardcoded, so this test cannot
        drift from it."""
        from typsphinx.translator import make_include_edge_key

        live_key = make_include_edge_key("a", "b#0>c", occurrence=0)
        dark_key = make_include_edge_key("a#0>b", "c", occurrence=0)

        assert live_key != dark_key, (
            "expected the live edge key (parent='a', child='b#0>c') and "
            "the dark edge key (parent='a#0>b', child='c') to differ; "
            f"both derived to {live_key!r}"
        )

        manual_typ = collision_build["manual_typ"]
        assert f'"{live_key}"' in manual_typ, (
            f"expected the live edge key {live_key!r} to be published in "
            f"manual.typ's state array:\n{manual_typ}"
        )
        assert f'"{dark_key}"' not in manual_typ, (
            f"expected the dark edge key {dark_key!r} to be ABSENT from "
            f"manual.typ's state array (it is not a real edge):\n"
            f"{manual_typ}"
        )

        a_typ = collision_build["a_typ"]
        a_hash_b_typ = collision_build["a_hash_b_typ"]
        assert f'if "{live_key}"' in a_typ, (
            f"expected a.typ's own guard to test the live key "
            f"{live_key!r}:\n{a_typ}"
        )
        assert f'if "{dark_key}"' in a_hash_b_typ, (
            f"expected a#0>b.typ's own guard to test the dark key "
            f"{dark_key!r}:\n{a_hash_b_typ}"
        )

    def test_typst_language_keeps_escape_character_distinct(self, tmp_path):
        """A LANGUAGE probe, not a production-code test (mirrors
        ``TestPublicationArityReadback`` in
        ``tests/test_include_edge_derivation_unit.py``): pins that Typst
        keeps an escaping backslash as an ordinary character in the
        string VALUE rather than folding it away, which is the property
        the fix depends on to keep two escaped key spellings distinct
        inside the published array at compile time. GREEN today (an
        invariance probe on Typst itself, not on this repository's code) --
        if a future Typst release changes this, this probe fails loudly
        instead of the collision silently returning."""
        probe_source = tmp_path / "probe.typ"
        probe_source.write_text(
            '#let escaped_a = "a\\#0\\>b"\n'
            '#let escaped_b = "a\\#0\\>c"\n'
            '#let unescaped = "a#0>b"\n'
            "#context [\n"
            "  DIFF-ESCAPED=#(escaped_a != escaped_b)\n"
            "  DIFF-FROM-UNESCAPED=#(escaped_a != unescaped)\n"
            "]\n",
            encoding="utf-8",
        )
        pdf_path = tmp_path / "probe.pdf"
        typst.compile(str(probe_source), output=str(pdf_path))
        reader = pypdf.PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() for page in reader.pages)
        assert "DIFF-ESCAPED=true" in text, text
        assert "DIFF-FROM-UNESCAPED=true" in text, text

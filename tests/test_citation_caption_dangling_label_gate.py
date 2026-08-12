"""
Phase 48 plan 01, Task 3: real-``sphinx-build``-plus-``typst.compile()`` gate
recording the pre-fix RED for D-05 (XREF-04) -- a citation reference living
inside a ``code-block`` directive's ``:caption:`` option.

Root cause, the disagreement between TWO independent traversal mechanisms:
``visit_caption`` raises ``SkipNode`` when ``in_captioned_code_block``
(``translator.py:2670-2671``), which stops the live WALKER from ever running
``visit_reference`` on the citing node inside the caption -- so no citing-site
anchor is ever attached anywhere. But the citation DEFINITION's back-reference
loop (``_find_citing_reference``, ``translator.py:3006``) scans the whole
doctree via ``self.document.findall(nodes.reference)``, which does NOT consult
walker reachability -- it structurally FINDS the citing node regardless, judges
it ``eligible`` via ``_reference_anchor_decision``, and (pre-fix) appends a bare
``link(<label>, ...)`` targeting an anchor nothing ever attaches. This is
invisible at ``-b typst`` (exit 0, no warning) and fatal only once Typst
compiles the output.

``tests/fixtures/citation_caption_dangling_label_gate/`` reproduces this with
a single well-formed master carrying exactly this shape. Every asserted value
in this module is taken from ``48-EXPECTED-STRUCTURE.md`` -- never read off a
fresh build. Every RED this module records is traced to
``48-RED-EVIDENCE.md``'s Failure mode 2 section.
"""

import re
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
CITATION_CAPTION_FIXTURE_DIR = FIXTURES_DIR / "citation_caption_dangling_label_gate"

# The 48-EXPECTED-STRUCTURE.md guarded form for this fixture's citation
# back-reference (D-05's value-expression usage, 48-RESEARCH.md Pitfall 3):
# `label_body` becomes the guard's open string + the already-computed
# `label_content` + the guard's close string, concatenated as one Python
# string -- not streamed around a live child walk.
_CAPTION_GUARD_PATTERN = re.compile(
    r"context \{ let __tsx_body = \[#\{.*?\}\]; "
    r"if query\(<index:id1>\)\.len\(\) > 0 \{ "
    r"link\(<index:id1>, __tsx_body\) \} else \{ __tsx_body \} \}"
)

# Every strict-xfail `reason=` below is a short, INLINE string literal (not
# a named constant) so the reason text -- including the plan id that flips
# the test -- sits textually adjacent to the decorator call itself, and the
# whole decorator fits on one physical line under `black`'s 88-column
# limit. The FULL explanation for each is a comment directly above its
# decorator.


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, per this
    repo's established NixOS-sandbox-safe convention (every gate module in
    this suite carries its own copy of this helper rather than importing a
    sibling module's).
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


def _strip_raw_literals(typ_text: str) -> str:
    """Drop ``raw("...")`` inline-literal segments before scanning for
    labels -- prose that quotes a label/reference form as an rST inline
    literal renders as a ``raw("...")`` string literal, not a real Typst
    label expression, and would masquerade as one in a naive scan."""
    return re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the citation-caption dangling label gate",
)
class TestCitationCaptionDanglingLabelGate:
    """
    D-05 / XREF-04: a citation reference inside a captioned code block's
    ``:caption:`` option must degrade gracefully (compile-time guard)
    instead of emitting a dangling ``link()`` to an anchor the caption's own
    ``SkipNode`` prevented from ever being attached.
    """

    def test_typst_build_clean_no_warning(self, tmp_path):
        """
        48-RED-EVIDENCE.md Failure mode 2: ``-b typst`` exits 0 with NO
        warning naming this defect -- a plain, non-xfail invariance guard
        (this half already passes today and documents why the defect is
        invisible before the Typst compile: neither traversal mechanism's
        disagreement produces a Sphinx-level diagnostic).
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(CITATION_CAPTION_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"Expected -b typst to exit 0:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        combined = result.stdout + result.stderr
        assert "does not exist" not in combined, (
            f"Unexpected dangling-label-shaped warning at -b typst time "
            f"(the defect should be invisible until Typst compiles):\n"
            f"{combined}"
        )

    # Pre-fix (48-RED-EVIDENCE.md Failure mode 2), -b typstpdf exits
    # non-zero with 'TypstError: label `<index:id1>` does not exist in the
    # document' -- the citation definition's backref loop still emits a
    # bare link(<index:id1>, ...) to an anchor visit_caption's SkipNode
    # prevented visit_reference from ever attaching.
    @pytest.mark.xfail(strict=True, reason="48-03 lands the guard (RED-EVIDENCE #2)")
    def test_typstpdf_build_succeeds_no_dangling_label(self, tmp_path):
        """
        48-EXPECTED-STRUCTURE.md "Fixture: citation_caption_dangling_label_gate":
        -b typstpdf exits 0, the wrapper PDF exists and starts with the PDF
        magic bytes, and the combined build output contains no
        'does not exist in the document' text anywhere.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(CITATION_CAPTION_FIXTURE_DIR, build_dir, "typstpdf")
        combined = result.stdout + result.stderr

        assert result.returncode == 0, (
            f"Expected -b typstpdf to exit 0:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert (
            "does not exist in the document" not in combined
        ), f"Typst reported a dangling label:\n{combined}"

        pdf_path = build_dir / "manual.pdf"
        assert pdf_path.exists(), (
            f"manual.pdf was not produced:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_path.read_bytes().startswith(
            b"%PDF"
        ), "manual.pdf does not start with the %PDF magic marker"

    # Pre-fix (48-RED-EVIDENCE.md Failure mode 2), the emitted index.typ
    # carries a bare link(<index:id1>, text("Smith2020")) around the
    # citation back-reference, not the guarded
    # context { ... if query(...).len() > 0 { ... } ... } form.
    @pytest.mark.xfail(strict=True, reason="48-03 lands the guard (RED-EVIDENCE #2)")
    def test_typ_carries_guarded_backref_form(self, tmp_path):
        """
        48-EXPECTED-STRUCTURE.md "Fixture: citation_caption_dangling_label_gate":
        the emitted index.typ carries the guarded form (D-07's
        value-expression composition, D-05) around the citation
        back-reference rather than a bare label link.
        """
        build_dir = tmp_path / "build"
        _run_sphinx_build(CITATION_CAPTION_FIXTURE_DIR, build_dir, "typst")
        index_typ_path = build_dir / "index.typ"
        assert index_typ_path.exists(), "index.typ was not emitted"
        index_typ = _strip_raw_literals(index_typ_path.read_text(encoding="utf-8"))

        match = _CAPTION_GUARD_PATTERN.search(index_typ)
        assert match is not None, (
            "index.typ does not carry the guarded "
            f"context {{ ... if query(...).len() > 0 {{ ... }} ... }} "
            f"expression around the citation back-reference to "
            f"index:id1:\n{index_typ}"
        )

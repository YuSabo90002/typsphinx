"""
Phase 47 plan 01, task 2: real-``sphinx-build`` subprocess gate for the
two-layer content/wrapper split -- COMP-01, COMP-02, COMP-03 (B-1), COMP-04
(B-2), and OUT-03.

Every assertion below is copied from
``.planning/phases/47-.../47-EXPECTED-STRUCTURE.md``'s per-fixture
expected-structure tables (binding constraint #6: the expected structure is
an INPUT to these tests, derived from each fixture's conf.py/rst read
literally, never from running the new emitter). Every test in this module
is marked ``xfail(strict=True)`` except the one unit test that already fails
in a way pytest reports as expected -- the content/wrapper split does not
exist yet on the unfixed tree, so every gate here is RED until 47-02 lands
it (binding constraint #4). The verbatim pre-fix evidence each test's
docstring paraphrases is recorded in full in ``47-RED-EVIDENCE.md``.
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

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ROOT_MASTER_FIXTURE_DIR = FIXTURES_DIR / "two_layer_root_master_gate"
NESTED_MASTER_FIXTURE_DIR = FIXTURES_DIR / "two_layer_nested_master_gate"

XFAIL_REASON = "RED until 47-02 lands the two-layer emitter"


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
    reason="typst-py is required for the two-layer output gate tests",
)
class TestTwoLayerOutputGate:
    """
    COMP-01, COMP-02, COMP-03 (B-1), OUT-03 -- .typ-level and real-compile
    assertions against ``two_layer_root_master_gate`` and
    ``two_layer_nested_master_gate``.
    """

    @pytest.mark.xfail(strict=True, reason=XFAIL_REASON)
    def test_comp01_content_file_has_no_template(self, tmp_path):
        """
        47-EXPECTED-STRUCTURE.md Fixture 1, expected table row "Content
        (docname index)": a docname-named content file must exist at
        ``index.typ``, carry NO template application (no
        ``#show: project.with(``, no ``_template.typ`` import) and NO
        title-page framing, only the D-06 preamble (four ``@preview``
        imports plus codly init) and the translated body.

        Pre-fix: no ``index.typ`` file exists at all -- the unfixed tree
        writes exactly one file per docname, at its RESOLVED STEM
        (``manual.typ`` here, per ``_resolve_output_stem``), never at the
        docname's own path. See 47-RED-EVIDENCE.md's COMP-01 section.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(ROOT_MASTER_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"Expected a successful build:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        content_typ = build_dir / "index.typ"
        assert content_typ.exists(), (
            f"Expected the docname-derived content file index.typ to exist:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        content = content_typ.read_text(encoding="utf-8")
        assert (
            "#show: project.with(" not in content
        ), f"Expected NO template application in the content file:\n{content}"
        assert (
            "_template.typ" not in content
        ), f"Expected NO _template.typ import in the content file:\n{content}"
        assert (
            '#import "@preview/codly:1.3.0": *' in content
        ), f"Expected the D-06 codly import in the content file:\n{content}"
        assert '#import "@preview/codly-languages:0.1.10": *' in content, (
            f"Expected the D-06 codly-languages import in the content file:\n"
            f"{content}"
        )
        assert (
            '#import "@preview/mitex:0.2.7": mi, mitex' in content
        ), f"Expected the D-06 mitex import in the content file:\n{content}"
        assert '#import "@preview/gentle-clues:1.3.1": *' in content, (
            f"Expected the D-06 gentle-clues import in the content file:\n" f"{content}"
        )
        assert (
            "ROOT-BODY-MARKER-AAA" in content
        ), f"Expected the content file's own body marker:\n{content}"

    @pytest.mark.xfail(strict=True, reason=XFAIL_REASON)
    def test_comp02_wrapper_file_has_template_and_include(self, tmp_path):
        """
        47-EXPECTED-STRUCTURE.md Fixture 1, expected table row "Wrapper
        (entry index -> manual.typ)": the wrapper file must exist at the
        entry's resolved target path (``manual.typ``, bare target, output
        root per OUT-01), carry the full template application, and
        ``#include()`` its own entry's content file (``index.typ``, per the
        derivation: ``compute_content_include_path("", "index.typ") ==
        "index.typ"``).

        Pre-fix: ``manual.typ`` exists but IS the single, undivided file --
        it contains the template application AND the body directly, with no
        ``#include()`` at all (there is nothing to include, since no
        separate content file exists). See 47-RED-EVIDENCE.md's COMP-02
        section.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(ROOT_MASTER_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"Expected a successful build:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        wrapper_typ = build_dir / "manual.typ"
        assert wrapper_typ.exists(), (
            f"Expected the wrapper file manual.typ to exist:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        content = wrapper_typ.read_text(encoding="utf-8")
        assert (
            "_template.typ" in content
        ), f"Expected the shared-template import in the wrapper:\n{content}"
        assert "#include(" in content, (
            f"Expected an #include() of the content file in the wrapper:\n" f"{content}"
        )
        assert (
            "index.typ" in content
        ), f"Expected the wrapper's #include() to name index.typ:\n{content}"

    @pytest.mark.xfail(strict=True, reason=XFAIL_REASON)
    def test_out03_content_files_stay_docname_derived(self, tmp_path):
        """
        47-EXPECTED-STRUCTURE.md Fixture 2, expected table: content files
        sit at ``index.typ`` and ``guide/index.typ`` (docname-derived,
        unconditionally) while their wrappers sit at ``outer.typ`` and
        ``manuals/guide.typ`` (target-derived) -- entirely independent
        placement, regardless of how far the wrapper's own target strays
        from the docname's own directory.

        Pre-fix: only ``outer.typ`` and ``guide/guide.typ`` exist -- there
        is no separate ``index.typ`` or ``guide/index.typ`` content file at
        all, and the second entry's target is truncated+relocated by the
        OUT-01-reversed guard rather than honored as a path. See
        47-RED-EVIDENCE.md's OUT-03 section.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(NESTED_MASTER_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"Expected a successful build:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (build_dir / "index.typ").exists(), (
            f"Expected docname-derived content file index.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "guide" / "index.typ").exists(), (
            f"Expected docname-derived content file guide/index.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "outer.typ").exists(), (
            f"Expected target-derived wrapper file outer.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "manuals" / "guide.typ").exists(), (
            f"Expected target-derived wrapper file manuals/guide.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    @pytest.mark.xfail(strict=True, reason=XFAIL_REASON)
    def test_comp03_b1_nested_master_compiles(self, tmp_path):
        """
        COMP-03 (B-1): the outer wrapper's ``#include()`` of its master's
        content file must target the SAME resolved location the nested
        docname's content file is unconditionally written to (COMP-01), so
        the real ``typst.compile()`` of ``outer.typ`` must SUCCEED.

        Pre-fix, measured directly this task (verbatim, recorded in
        47-RED-EVIDENCE.md): ``TypstError('file not found (searched at
        .../guide/index.typ)')`` -- the classic-TypstError RED shape
        binding constraint #4 requires for this requirement.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(NESTED_MASTER_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"Expected a successful build:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        wrapper_typ = build_dir / "outer.typ"
        assert wrapper_typ.exists(), (
            f"Expected the outer wrapper file to exist:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        try:
            typst.compile(str(wrapper_typ), root=str(build_dir))
        except Exception as exc:
            message = str(exc)
            assert "file not found" not in message, (
                f"Expected the B-1 file-not-found TypstError to be gone "
                f"post-fix, but it recurred: {exc}"
            )
            assert "guide/index.typ" not in message, (
                f"Expected the B-1 file-not-found TypstError to be gone "
                f"post-fix, but it recurred: {exc}"
            )
            pytest.fail(f"Expected the compile to succeed post-fix: {exc}")


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the COMP-04 render gate",
)
class TestTwoLayerOutputGatePdf:
    """COMP-04 (B-2) -- real-compile, real-pypdf structural assertion."""

    @pytest.fixture(scope="class")
    def nested_master_outer_pdf_text(self, tmp_path_factory):
        """
        Build + real-compile ``two_layer_nested_master_gate``'s outer
        wrapper ONCE per class and return the pypdf-extracted PDF text.

        Depends only on ``tmp_path_factory`` (session-scoped-compatible),
        not on a function-scoped fixture, to avoid a pytest ScopeMismatch --
        the same pattern ``test_pdf_render_gate.py``'s class-scoped
        compile-once fixtures use.

        Pre-fix, the real ``typst.compile()`` call below raises B-1's
        TypstError before B-2 can be independently observed on THIS
        fixture as configured (see 47-RED-EVIDENCE.md's COMP-04 section for
        the isolated B-2-only measurement, captured by temporarily working
        around B-1). That TypstError propagates out of this fixture, and
        pytest reports the dependent xfail(strict=True) test as ``xfailed``
        (verified empirically this task: a class-scoped fixture raising
        inside an xfail-marked test's dependency chain is still caught by
        xfail, not reported as a bare ``error``).
        """
        source_dir = NESTED_MASTER_FIXTURE_DIR
        build_dir = tmp_path_factory.mktemp("two_layer_nested_master_gate") / "_build"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "typst",
                str(source_dir),
                str(build_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert (
            result.returncode == 0
        ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

        wrapper_typ = build_dir / "outer.typ"
        assert wrapper_typ.exists(), "outer.typ was not generated"

        pdf_output = build_dir / "outer.pdf"
        typst.compile(str(wrapper_typ), output=str(pdf_output), root=str(build_dir))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            assert f.read(4) == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        return "\n".join(page.extract_text() for page in reader.pages)

    @pytest.mark.xfail(strict=True, reason=XFAIL_REASON)
    def test_comp04_b2_no_mid_body_template_reexpansion(
        self, nested_master_outer_pdf_text
    ):
        """
        47-EXPECTED-STRUCTURE.md Fixture 2's B-2 closure: the compiled
        outer PDF's page-text sequence must contain both body markers with
        NO second title-page-shaped block and NO second outline sandwiched
        between them -- structural pypdf assertions, per binding constraint
        #4, NOT a TypstError assertion (B-2 compiles fine and produces
        wrong output).

        Pre-fix (measured this task in isolation, B-1 worked around by
        copying the misplaced file to the path the wrapper expects --
        verbatim transcript in 47-RED-EVIDENCE.md's COMP-04 section): the
        compiled PDF contains SIX pages, with a full second title page
        (``Nested Master`` / ``Probe Author`` / page number alone) and a
        full second outline (a second ``Contents`` heading) sandwiched
        between the outer document's own prose and the nested document's
        own body -- ``Nested Master`` appears once (only from that second
        title page, since the nested .rst's own heading text is
        deliberately the DIFFERENT string ``Guide Section``) and
        ``Contents`` appears three times (the outer's own outline heading,
        plus the nested mid-body outline's own two occurrences: its
        "2.1 Contents" section heading and its "Contents" title line).
        """
        text = nested_master_outer_pdf_text
        assert (
            "OUTER-PROSE-MARKER" in text
        ), f"Expected the outer document's own prose marker:\n{text}"
        assert (
            "GUIDE-BODY-MARKER" in text
        ), f"Expected the nested document's own body marker:\n{text}"
        assert "Nested Master" not in text, (
            f"Expected NO second title page (the nested entry's own "
            f"typst_documents title, which never appears in a "
            f"template-less content-file inclusion):\n{text}"
        )
        assert text.count("Contents") == 1, (
            f"Expected exactly ONE outline (the outer document's own), "
            f"not a second mid-body outline:\n{text}"
        )


class TestComputeContentIncludePath:
    """
    Unit test for the include-path purity edge (COMP-03, edge/concurrency):
    the wrapper-to-content include path is a pure function of (wrapper
    resolved directory, content path), independent of write order.

    Marked xfail(strict=True, raises=ImportError) until 47-02 lands
    ``compute_content_include_path`` in ``typsphinx.writer`` -- the
    function does not exist yet on the unfixed tree.
    """

    @pytest.mark.xfail(
        strict=True,
        raises=ImportError,
        reason="RED until 47-02 lands compute_content_include_path",
    )
    def test_compute_content_include_path_is_a_pure_two_endpoint_relpath(self):
        from typsphinx.writer import compute_content_include_path

        assert (
            compute_content_include_path("manuals", "guide/index.typ")
            == "../guide/index.typ"
        )
        assert compute_content_include_path("", "guide/index.typ") == "guide/index.typ"
        assert compute_content_include_path("guide", "guide/index.typ") == "index.typ"

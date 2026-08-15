"""
Phase 47 plan 01, task 2 (fixtures/RED) and plan 02 (the fix): real-
``sphinx-build`` subprocess gate for the two-layer content/wrapper split --
COMP-01, COMP-02, COMP-03 (B-1), COMP-04 (B-2), and OUT-03.

Every assertion below is copied from
``.planning/phases/47-.../47-EXPECTED-STRUCTURE.md``'s per-fixture
expected-structure tables (binding constraint #6: the expected structure is
an INPUT to these tests, derived from each fixture's conf.py/rst read
literally, never from running the new emitter). Plan 47-02 lands the
content/wrapper split and removes every ``xfail`` marker this module was
seeded with in plan 47-01 -- the verbatim pre-fix evidence each test's
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

    def test_comp01_content_file_has_no_template(self, tmp_path):
        """
        47-EXPECTED-STRUCTURE.md Fixture 1, expected table row "Content
        (docname index)": a docname-named content file must exist at
        ``index.typ``, carry NO template application (no
        ``#show: project.with(``, no bundled-template import under
        ``/_template/``) and NO title-page framing, only the D-06
        preamble (four ``@preview`` imports plus codly init) and the
        translated body.

        Pre-fix: no ``index.typ`` file exists at all -- the unfixed tree
        writes exactly one file per docname, at its RESOLVED STEM
        (``manual.typ`` here, resolved at the time by the docname-based
        first-match lookup ``_resolve_output_stem`` -- deleted as dead
        code in Phase 47 Plan 14, WR-01, once every write/read-back site
        had moved to per-entry resolution), never at the docname's own
        path. See 47-RED-EVIDENCE.md's COMP-01 section.
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
            "/_template/" not in content
        ), f"Expected NO bundled-template import in the content file:\n{content}"
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
            '#import "/_template/typst/base.typ"' in content
        ), f"Expected the bundled default's root-absolute import in the wrapper:\n{content}"
        assert "#include(" in content, (
            f"Expected an #include() of the content file in the wrapper:\n" f"{content}"
        )
        assert (
            "index.typ" in content
        ), f"Expected the wrapper's #include() to name index.typ:\n{content}"

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

    def test_typst_and_typstpdf_emit_byte_identical_typ_files(self, tmp_path):
        """
        ``-b typst`` and ``-b typstpdf`` share ONE write path
        (``TypstBuilder._write_typst_files()``, which ``TypstPDFBuilder``
        inherits) -- every ``.typ`` file either builder emits must be
        byte-identical, and the PDF builder's compile step must produce a
        ``.pdf`` for every WRAPPER only, never for a content file.
        """
        typst_dir = tmp_path / "typst_build"
        typstpdf_dir = tmp_path / "typstpdf_build"

        typst_result = _run_sphinx_build(NESTED_MASTER_FIXTURE_DIR, typst_dir, "typst")
        assert typst_result.returncode == 0, (
            f"Expected a successful -b typst build:\n"
            f"stdout: {typst_result.stdout}\nstderr: {typst_result.stderr}"
        )
        typstpdf_result = _run_sphinx_build(
            NESTED_MASTER_FIXTURE_DIR, typstpdf_dir, "typstpdf"
        )
        assert typstpdf_result.returncode == 0, (
            f"Expected a successful -b typstpdf build:\n"
            f"stdout: {typstpdf_result.stdout}\nstderr: {typstpdf_result.stderr}"
        )

        typst_typ_files = {p.relative_to(typst_dir) for p in typst_dir.rglob("*.typ")}
        typstpdf_typ_files = {
            p.relative_to(typstpdf_dir) for p in typstpdf_dir.rglob("*.typ")
        }
        assert typst_typ_files == typstpdf_typ_files, (
            f"Expected identical .typ file sets:\n"
            f"typst-only: {typst_typ_files - typstpdf_typ_files}\n"
            f"typstpdf-only: {typstpdf_typ_files - typst_typ_files}"
        )

        for relpath in sorted(typst_typ_files):
            typst_bytes = (typst_dir / relpath).read_bytes()
            typstpdf_bytes = (typstpdf_dir / relpath).read_bytes()
            assert typst_bytes == typstpdf_bytes, (
                f"Expected {relpath} to be byte-identical between builders, "
                f"but its content differed"
            )

        # R4/COMP-04: only WRAPPER files compile to PDF -- a content file
        # is never independently compiled.
        assert (typstpdf_dir / "outer.pdf").exists(), "Expected outer.pdf"
        assert (
            typstpdf_dir / "manuals" / "guide.pdf"
        ).exists(), "Expected manuals/guide.pdf"
        assert not (
            typstpdf_dir / "index.pdf"
        ).exists(), "Expected NO index.pdf -- content files are never compiled"
        assert not (
            typstpdf_dir / "guide" / "index.pdf"
        ).exists(), "Expected NO guide/index.pdf -- content files are never compiled"

    def test_typst_build_is_deterministic_across_runs(self, tmp_path):
        """
        Two consecutive ``-b typst`` builds of the same project produce
        byte-identical wrapper AND content files -- emission order is
        deterministic (COMP-01, edge/ordering must_have).
        """
        first_dir = tmp_path / "first_build"
        second_dir = tmp_path / "second_build"

        first_result = _run_sphinx_build(NESTED_MASTER_FIXTURE_DIR, first_dir, "typst")
        assert first_result.returncode == 0, (
            f"Expected a successful first build:\n"
            f"stdout: {first_result.stdout}\nstderr: {first_result.stderr}"
        )
        second_result = _run_sphinx_build(
            NESTED_MASTER_FIXTURE_DIR, second_dir, "typst"
        )
        assert second_result.returncode == 0, (
            f"Expected a successful second build:\n"
            f"stdout: {second_result.stdout}\nstderr: {second_result.stderr}"
        )

        first_typ_files = {p.relative_to(first_dir) for p in first_dir.rglob("*.typ")}
        second_typ_files = {
            p.relative_to(second_dir) for p in second_dir.rglob("*.typ")
        }
        assert first_typ_files == second_typ_files, (
            f"Expected identical .typ file sets across two builds:\n"
            f"first-only: {first_typ_files - second_typ_files}\n"
            f"second-only: {second_typ_files - first_typ_files}"
        )
        for relpath in sorted(first_typ_files):
            first_bytes = (first_dir / relpath).read_bytes()
            second_bytes = (second_dir / relpath).read_bytes()
            assert first_bytes == second_bytes, (
                f"Expected {relpath} to be byte-identical across two builds, "
                f"but its content differed"
            )

    def test_typst_build_log_names_the_wrapper_files_to_compile(self, tmp_path):
        """
        D-07: ``-b typst`` (markup-only, no PDF compile step of its own)
        names the wrapper files it wrote and states that those are the
        files to compile -- the missing symmetric message to
        ``-b typstpdf``'s existing "Compiling N master document(s)"/
        "Generated PDF" lines, needed because the outdir now holds
        roughly twice as many files with nothing in a filename alone
        distinguishing a content file from a wrapper.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(NESTED_MASTER_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"Expected a successful build:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert "outer.typ" in combined_output, (
            f"Expected the build log to name outer.typ as a wrapper to "
            f"compile:\n{combined_output}"
        )
        assert "manuals/guide.typ" in combined_output, (
            f"Expected the build log to name manuals/guide.typ as a "
            f"wrapper to compile:\n{combined_output}"
        )


@pytest.fixture(scope="class")
def nested_master_outer_pdf_text(tmp_path_factory):
    """
    Build + real-compile ``two_layer_nested_master_gate``'s outer
    wrapper ONCE per class and return the pypdf-extracted PDF text.

    Defined at MODULE level (not as a class-scoped instance method) per
    this repo's established convention -- see
    ``test_pdf_render_gate.py``'s ``admonition_render_gate_pdf_text``.
    A class-scoped fixture defined as an instance method is deprecated as
    of pytest 9.1 (``PytestRemovedIn10Warning``, escalated to a hard
    error by this repo's ``filterwarnings = ["error::DeprecationWarning"]``
    -- Rule 3 auto-fix, pre-existing since plan 47-01: the instance-method
    shape silently made every dependent test report ``xfailed`` for the
    WRONG reason, a fixture-setup error, rather than either a genuine
    RED assertion or, post-fix, a genuine pass).

    Depends only on ``tmp_path_factory`` (session-scoped-compatible),
    not on a function-scoped fixture, to avoid a pytest ScopeMismatch --
    the same pattern ``test_pdf_render_gate.py``'s class-scoped
    compile-once fixtures use.
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


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the COMP-04 render gate",
)
class TestTwoLayerOutputGatePdf:
    """COMP-04 (B-2) -- real-compile, real-pypdf structural assertion."""

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
    """

    def test_compute_content_include_path_is_a_pure_two_endpoint_relpath(self):
        from typsphinx.writer import compute_content_include_path

        assert (
            compute_content_include_path("manuals", "guide/index.typ")
            == "../guide/index.typ"
        )
        assert compute_content_include_path("", "guide/index.typ") == "guide/index.typ"
        assert compute_content_include_path("guide", "guide/index.typ") == "index.typ"
        assert compute_content_include_path("", "index.typ") == "index.typ"


class TestComputeTemplateImportPath:
    """
    Unit tests for ``compute_template_import_path()`` (Phase 54, OUT-06):
    a root-absolute import path computed from a registry key and the
    resolved template's own filename -- NOT from the wrapper's own
    resolved directory, unlike the depth-counted
    ``compute_template_import_path_for_dir()`` this replaces (deleted).
    Typst resolves a leading ``/`` against the project root
    (``pdf.py``'s ``root=self.outdir``), so the wrapper's own nesting
    depth is irrelevant by construction.
    """

    def test_bare_key_imports_root_absolute_path(self):
        from typsphinx.writer import compute_template_import_path

        assert (
            compute_template_import_path("typst", "base.typ")
            == "/_template/typst/base.typ"
        )

    def test_same_key_same_path_regardless_of_a_notional_wrapper_depth(self):
        """OUT-06: the function accepts no wrapper-directory argument at
        all, so calling it repeatedly for the SAME key/filename -- as if
        for wrappers written at increasingly deep notional nesting --
        always returns the IDENTICAL string."""
        from typsphinx.writer import compute_template_import_path

        results = {
            compute_template_import_path("report", "custom.typ")
            for _notional_depth in range(4)
        }
        assert results == {"/_template/report/custom.typ"}

    def test_different_key_imports_its_own_bundle(self):
        from typsphinx.writer import compute_template_import_path

        assert (
            compute_template_import_path("report", "custom.typ")
            == "/_template/report/custom.typ"
        )

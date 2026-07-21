"""
Fast, offline real-compile regression gate for the typstpdf compile-root
alignment fix (Phase 22.1, GATE-01 -- PDF-02).

Root cause: ``TypstPDFBuilder.finish()`` used to read a master's ``.typ``
file into a **string** and hand it to
``compile_typst_to_pdf(content, root_dir=self.outdir)``
(``typsphinx/pdf.py``), which wrote that string to a
``tempfile.NamedTemporaryFile(dir=root_dir, ...)`` -- i.e. at the **outdir
root** -- and compiled *that* temp file. Typst resolves every relative path
used inside ``#include()`` / ``image()`` against the file being compiled,
not against ``root``, while the translator
(``_compute_relative_include_path`` / ``_compute_relative_image_path``)
emits those paths **docname-relative**. The two bases coincided only when
the master sat at the outdir root (``index``) -- which is why every existing
test and the full Sphinx corpus passed before this phase. A master at the
nested docname ``api/index`` emits ``include("usage.typ")`` (sibling,
relative to ``api/``); the temp copy at the outdir root resolved that to
``<outdir>/usage.typ`` -- file not found.

Fix: ``compile_typst_file_to_pdf(typ_path, root_dir)`` (new in
``typsphinx/pdf.py``) compiles the master's own ``.typ`` at its real,
docname-derived location directly -- no temp file, no read-to-string. Because
the compiled file *is* the master ``.typ`` at its real location, the
docname-relative paths the translator emitted resolve correctly **by
construction**; the basis divergence becomes structurally impossible rather
than merely corrected for this one fixture.

This gate drives the full ``-b typstpdf`` path on purpose -- ``returncode ==
0`` is now a meaningful *primary* signal (unlike older render gates in this
suite, which predate Phase 22.1's D-04 change and could only trust the
build's artifacts, not its exit code) because
``TypstPDFBuilder.finish()`` now raises an aggregated
``sphinx.errors.ExtensionError`` after attempting every configured master,
rather than silently swallowing a compile failure and exiting 0 with a
missing ``.pdf``.

Fixture shape (D-07): the fixture's only master sits at docname ``api/index``
with target name ``index`` -- **target equals the docname's basename on
purpose**, so the Phase 22 target-name rename is deliberately NOT exercised
here. When this gate goes red, the cause is unambiguously PDF-02, not an
interaction with the target-name feature. ``api/index`` toctrees the sibling
``api/usage`` (emits ``include("usage.typ")``) and references a root-level
image (emits ``image("../logo.png")``, crossing a directory boundary upward
while staying inside ``outdir``).

Companion bug found and fixed while building this gate (same failure class,
different call site): ``TypstWriter.translate()`` (``typsphinx/writer.py``)
hardcoded ``template_file="_template.typ"`` for every master document, a bare
reference correct only when the master sits at the outdir root -- exactly
the same docname-relative-vs-outdir-root basis mismatch PDF-02 fixes for
``#include()`` / ``image()``, but for the template import.
``_write_template_file()`` (``typsphinx/builder.py``) always writes
``_template.typ`` at the outdir root regardless of where a master lives, so
a nested master's bare ``"_template.typ"`` reference resolved to a sibling
file that was never written (e.g. ``outdir/api/_template.typ``). This gate's
first real run against pre-writer.py-fix code failed on exactly this before
ever reaching the include/image bug PDF-02 documents. Fixed by reusing the
translator's own ``_compute_relative_include_path()`` (docname-relative
emission is its established, already-tested basis), treating the template
file as a top-level ``"_template"`` docname -- for the nested fixture this
now emits ``#import "../_template.typ": project``.

Confirmed both directions:

- **FAILS** against the pre-fix compile basis. ``test_outdir_root_compile_
  basis_still_fails`` reproduces that basis directly -- copying the emitted
  ``api/index.typ`` to a file at the outdir *root* and compiling that copy
  with ``root=outdir`` -- and captures the real Typst error:

      TypstError: path `"../_template.typ"` would escape the project root

  The real emitted ``api/index.typ`` opens with the relative reference
  ``#import "../_template.typ": project`` -- correct only from
  ``outdir/api/``, where it resolves to ``outdir/_template.typ`` (safely
  inside the compile root). Copied verbatim to the outdir root and compiled
  with ``root=outdir``, that SAME reference would have to resolve one
  directory ABOVE ``outdir`` -- outside the compile root entirely -- so
  Typst's own root-boundary enforcement rejects it before the compiler ever
  reaches the sibling ``include("usage.typ")`` or the image reference. This
  is still a direct, real proof of the outdir-root vs. outdir/api divergence
  (Common Pitfall 2 in ``22.1-RESEARCH.md`` anticipated exactly this error
  class), and it is a **standing** test, not a one-time manual verification,
  so the gate can never start passing vacuously after a future refactor
  reintroduces an intermediate copy at the outdir root.
- **PASSES** with the fix.
  ``test_typstpdf_nested_master_resolves_include_and_image`` drives the real
  ``-b typstpdf`` path end-to-end and asserts the compiled ``api/index.pdf``
  exists with the ``%PDF`` magic prefix.
  ``test_typst_builder_output_compiles_manually`` additionally compiles the
  ``-b typst`` output directly via ``typst.compile()``, mirroring exactly
  what a user running ``typst compile`` by hand does (SC#3 / D-09) -- pinning
  that the two builders now share the identical compile-root basis.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


@pytest.fixture
def nested_master_render_gate_dir():
    """Return the path to the nested_master_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "nested_master_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for -b typstpdf build output."""
    return tmp_path / "_build"


@pytest.fixture
def temp_build_dir_typst(tmp_path):
    """
    Provide a SEPARATE temporary directory for -b typst build output.

    Kept distinct from ``temp_build_dir`` so the ``-b typst`` build (used by
    the D-08(a) pre-fix-basis reproduction and the D-09 cross-builder
    equivalence check) can never be contaminated by the ``-b typstpdf``
    build's ``.pdf`` artifacts, or vice versa.
    """
    return tmp_path / "_build_typst"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard.
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
    reason="typst-py is required for the nested-master render gate",
)
class TestNestedMasterRenderGate:
    """
    Real-compile regression gate proving ``-b typstpdf`` and ``-b typst``
    resolve ``#include()`` / ``image()`` on the same basis for a master at a
    NESTED docname (``api/index``), and that the pre-fix outdir-root compile
    basis demonstrably still fails.

    Requirements: PDF-02 (Phase 22.1 scope).
    """

    def test_typstpdf_nested_master_resolves_include_and_image(
        self, nested_master_render_gate_dir, temp_build_dir
    ):
        """
        SC#1: Build the fixture through ``-b typstpdf`` and confirm the
        nested master compiles to PDF with its sibling include and upward
        image reference intact.

        ``result.returncode == 0`` is a meaningful primary signal here (see
        module docstring) because Phase 22.1's D-04 change makes a compile
        failure raise ``sphinx-build`` to a non-zero exit instead of being
        logged and swallowed.
        """
        result = _run_sphinx_build(
            nested_master_render_gate_dir, temp_build_dir, "typstpdf"
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "file not found" not in result.stderr, (
            "typst.compile() reported a missing file -- the nested master's "
            f"sibling include or image did not resolve:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "api" / "index.typ"
        assert typ_output.exists(), (
            f"api/index.typ was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        usage_output = temp_build_dir / "api" / "usage.typ"
        assert usage_output.exists(), (
            f"api/usage.typ (the sibling include target) was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        logo_output = temp_build_dir / "logo.png"
        assert logo_output.exists(), (
            "logo.png (the root-level image asset) was not copied into the "
            f"output tree -- the upward image('../logo.png') reference "
            f"cannot resolve without it:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "api" / "index.pdf"
        assert pdf_output.exists(), (
            f"api/index.pdf was not produced -- typst.compile() aborted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "Generated PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_outdir_root_compile_basis_still_fails(
        self, nested_master_render_gate_dir, temp_build_dir_typst
    ):
        """
        SC#2 / D-08(a): Reproduce the PRE-FIX compile basis directly -- copy
        the emitted ``api/index.typ`` to a file at the outdir ROOT and
        compile that copy with ``typst.compile(copy, root=outdir)`` -- and
        confirm it still fails on a reference that only breaks when compiled
        from the WRONG directory.

        The real emitted ``api/index.typ`` opens with
        ``#import "../_template.typ": project`` (a relative reference,
        correct only from ``outdir/api/`` -- see the ``writer.py`` deviation
        recorded in the plan Summary). Copied verbatim to the outdir ROOT and
        compiled with ``root=outdir``, that SAME relative reference would
        have to resolve one directory ABOVE outdir -- outside the compile
        root entirely -- so Typst's own root-boundary enforcement rejects it
        before the compiler ever reaches the sibling ``include("usage.typ")``
        or the image reference. This is still a direct, real proof of the
        outdir-root vs. outdir/api divergence: the identical relative
        reference is safe from one location and unsafe from the other.

        This is a STANDING test, not a one-time manual verification, so the
        gate can never start passing vacuously after a future refactor
        reintroduces an intermediate copy at the outdir root. See the module
        docstring's record (above) of the real, transcribed Typst error this
        reproduction actually produces.
        """
        result = _run_sphinx_build(
            nested_master_render_gate_dir, temp_build_dir_typst, "typst"
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_source = temp_build_dir_typst / "api" / "index.typ"
        assert typ_source.exists(), (
            f"api/index.typ was not emitted by -b typst:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        typ_source_text = typ_source.read_text(encoding="utf-8")
        assert '#import "../_template.typ"' in typ_source_text, (
            "Expected the emitted master to open with a relative "
            "'../_template.typ' import (correct only from outdir/api/) -- "
            f"the pre-fix-basis reproduction below depends on this exact "
            f"reference:\n{typ_source_text}"
        )

        # Reproduce the pre-fix basis: a copy of the master placed at the
        # OUTDIR ROOT (never a real docname-derived artifact -- the
        # leading-underscore name cannot collide with anything the builders
        # emit) and compiled with root=outdir, exactly as the pre-fix
        # NamedTemporaryFile(dir=root_dir) placement did.
        basis_copy = temp_build_dir_typst / "_prefix_basis_copy.typ"
        shutil.copy2(typ_source, basis_copy)

        with pytest.raises(Exception) as exc_info:
            typst.compile(str(basis_copy), root=str(temp_build_dir_typst))

        error_text = str(exc_info.value)
        # Tolerant of Typst's exact wording (per D-08(a)), but the error MUST
        # be one of the two signatures a wrong-directory compile produces:
        # either a plain missing-file error (the sibling include/image class
        # PDF-02's canonical refs describe) or a root-escape error (the
        # relative-import class this fixture's real _template.typ reference
        # actually triggers first) -- both are proof the outdir-root basis
        # is broken, never a false pass.
        lowered = error_text.lower()
        assert "not found" in lowered or "escape" in lowered, (
            "Expected a missing-file or root-escape error reproducing the "
            f"pre-fix compile basis, got: {error_text!r}"
        )
        # The discriminating detail: the SAME relative reference
        # ('../_template.typ') that resolves safely from the master's real
        # location (outdir/api/, proven by test 1 and test 3 above/below) is
        # the one this error names when compiled from the outdir root.
        assert "_template.typ" in error_text, (
            "Expected the pre-fix-basis reproduction's error to name the "
            "'_template.typ' reference -- the one relative import whose "
            "resolution differs entirely based on the compiled file's "
            f"directory depth:\n{error_text!r}"
        )

    def test_typst_builder_output_compiles_manually(
        self, nested_master_render_gate_dir, temp_build_dir_typst
    ):
        """
        SC#3 / D-09: Compile the ``-b typst`` output directly via
        ``typst.compile()``, reproducing exactly what a user running
        ``typst compile`` by hand does -- pinning cross-builder equivalence.

        After D-01, ``-b typstpdf`` and ``-b typst`` compile the same file at
        the same location, so this equivalence is structural; this test pins
        that structural property so a future refactor reintroducing an
        intermediate copy is caught.
        """
        result = _run_sphinx_build(
            nested_master_render_gate_dir, temp_build_dir_typst, "typst"
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir_typst / "api" / "index.typ"
        assert typ_output.exists(), (
            f"api/index.typ was not emitted by -b typst:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        pdf_bytes = typst.compile(str(typ_output), root=str(temp_build_dir_typst))
        assert pdf_bytes.startswith(b"%PDF"), (
            "Manually compiling the -b typst output did not produce a valid "
            f"PDF -- got {pdf_bytes[:20]!r}"
        )

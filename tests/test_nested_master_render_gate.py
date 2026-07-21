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

Two independent outdir-root-relative references, one masking the other:
the emitted master carries the template import at line 7 AND the sibling
include at line 33 AND the upward image at line 40, all resolved against
the compile basis. The template import is EARLIER in the file, so a
verbatim copy at the outdir root always fails on IT first, before the
compiler ever reaches the sibling include or image. Proving the
include/image class in isolation therefore requires neutralizing the
earlier-failing template reference first -- which is exactly why this
module needs TWO pre-fix-basis tests, not one, each pinned to a single,
distinct failure class (gap ``G-22.1-2``).

Confirmed both directions:

- **FAILS** against the pre-fix compile basis, in TWO complementary
  proofs -- one per masking reference:

  - **Template-reference class.** ``test_outdir_root_compile_basis_
    still_fails`` reproduces the pre-fix basis VERBATIM -- copying the
    emitted ``api/index.typ`` to a file at the outdir *root*, with no
    rewriting at all, and compiling that copy with ``root=outdir`` -- and
    captures the real Typst error:

        TypstError: path `"../_template.typ"` would escape the project root

    The real emitted ``api/index.typ`` opens with the relative reference
    ``#import "../_template.typ": project`` -- correct only from
    ``outdir/api/``, where it resolves to ``outdir/_template.typ`` (safely
    inside the compile root). Copied verbatim to the outdir root and
    compiled with ``root=outdir``, that SAME reference would have to
    resolve one directory ABOVE ``outdir`` -- outside the compile root
    entirely -- so Typst's own root-boundary enforcement rejects it before
    the compiler ever reaches the sibling ``include("usage.typ")`` or the
    image reference. This is a direct, real proof of the outdir-root
    vs. outdir/api divergence for the template-reference class (Common
    Pitfall 2 in ``22.1-RESEARCH.md`` anticipated exactly this error
    class).

  - **Include/image class (closes G-22.1-2).**
    ``test_sibling_include_fails_at_outdir_root_and_resolves_in_place``
    neutralizes ONLY the template import first -- rewriting the single
    ``#import "../_template.typ"`` occurrence to the outdir-root-correct
    ``#import "_template.typ"``, leaving ``include("usage.typ")`` and
    ``image("../logo.png")`` byte-identical -- then compiles that
    template-neutralized copy from the outdir root, at which point the
    compiler reaches (and fails on) the sibling include instead. The real
    captured Typst error:

        file not found (searched at <outdir>/usage.typ)

    This is the class ROADMAP SC#2's "file-not-found" wording literally
    names, proven in isolation from the template-reference class rather
    than merely masked behind it. The error names ``usage.typ``
    specifically, does NOT name ``_template.typ`` (proving the masking
    reference was fully neutralized), and does NOT carry the ``api/``
    path segment (proving Typst searched at the outdir root, not the
    master's real directory).

  Both are **standing** tests, not one-time manual verifications, so the
  gate can never start passing vacuously after a future refactor
  reintroduces an intermediate copy at the outdir root -- and because each
  test is pinned to a single failure class, a future drift between the two
  classes turns exactly one of them red, naming which class moved.
- **PASSES** with the fix, in TWO complementary proofs -- one per
  reference class:

  - ``test_typstpdf_nested_master_resolves_include_and_image`` drives the
    real ``-b typstpdf`` path end-to-end and asserts the compiled
    ``api/index.pdf`` exists with the ``%PDF`` magic prefix.
    ``test_typst_builder_output_compiles_manually`` additionally compiles
    the ``-b typst`` output directly via ``typst.compile()``, mirroring
    exactly what a user running ``typst compile`` by hand does (SC#3 /
    D-09) -- pinning that the two builders now share the identical
    compile-root basis.
  - ``test_sibling_include_fails_at_outdir_root_and_resolves_in_place``'s
    own GREEN half is the explicit counterpart of its RED half, at the
    SAME build: it asserts the unmodified master, compiled at its real
    location (``outdir/api/index.typ``, ``root=outdir``), produces a valid
    PDF -- proving the identical ``include("usage.typ")`` and
    ``image("../logo.png")`` references that failed to resolve from the
    outdir root DO resolve in place.
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
        SC#2 / D-08(a) -- TEMPLATE-REFERENCE half of the pre-fix-basis proof.

        Reproduces the PRE-FIX compile basis VERBATIM -- copy the emitted
        ``api/index.typ`` to a file at the outdir ROOT, with NO rewriting at
        all, and compile that copy with ``typst.compile(copy, root=outdir)``.

        Because the emitted master's very FIRST reference is the relative
        ``#import "../_template.typ": project`` (correct only from
        ``outdir/api/``, where it resolves to ``outdir/_template.typ``),
        Typst's own root-boundary enforcement rejects that import line before
        the compiler ever reaches the sibling ``include("usage.typ")`` (line
        33) or the ``image("../logo.png")`` reference (line 40) further down
        the file. This test is therefore deliberately scoped to ONE failure
        class only -- the template-reference root-escape -- and asserts
        exactly that class, not a disjunction that would also accept the
        include/image failure mode.

        The include/image half -- the class ROADMAP SC#2's "file-not-found"
        wording literally names -- is proven separately by
        ``test_sibling_include_fails_at_outdir_root_and_resolves_in_place``
        below, which neutralizes this template import FIRST so the compiler
        can reach the sibling include/image references and fail on THEM
        instead. The two tests deliberately partition the failure space: a
        future drift between the two classes (e.g. the template import
        disappearing) turns exactly one of them red, naming which class
        moved, rather than leaving both passing vacuously through a shared
        tolerant assertion.

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
        # NamedTemporaryFile(dir=root_dir) placement did. NO rewriting --
        # byte-identical to the emitted master.
        basis_copy = temp_build_dir_typst / "_prefix_basis_copy.typ"
        shutil.copy2(typ_source, basis_copy)

        with pytest.raises(Exception) as exc_info:
            typst.compile(str(basis_copy), root=str(temp_build_dir_typst))

        error_text = str(exc_info.value)
        # Pinned to the SINGLE failure class this test provably produces:
        # the root-escape rejection of the relative '../_template.typ'
        # import. This is the TEMPLATE-reference half of the SC#2 proof; the
        # include/image half lives in
        # test_sibling_include_fails_at_outdir_root_and_resolves_in_place.
        # If this assertion goes red, check whether the template-reference
        # class moved to a different error shape -- do not widen this back
        # into a disjunction with a missing-file signature.
        lowered = error_text.lower()
        assert "escape" in lowered, (
            "Expected a root-escape error reproducing the pre-fix compile "
            "basis (the TEMPLATE-reference half of the SC#2 proof -- see "
            "test_sibling_include_fails_at_outdir_root_and_resolves_in_place "
            f"for the include/image half), got: {error_text!r}"
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

    def test_sibling_include_fails_at_outdir_root_and_resolves_in_place(
        self, nested_master_render_gate_dir, temp_build_dir_typst
    ):
        """
        Closes gap ``G-22.1-2``; discharges ROADMAP Phase 22.1 SC#2 in the
        literal "file not found" shape its wording names -- the
        INCLUDE/IMAGE half of the pre-fix-basis proof, complementing
        ``test_outdir_root_compile_basis_still_fails`` above (the
        TEMPLATE-reference half).

        The emitted ``api/index.typ`` carries THREE outdir-root-relative
        references: ``#import "../_template.typ"`` at line 7,
        ``include("usage.typ")`` at line 33, and ``image("../logo.png")`` at
        line 40. Copying the master verbatim to the outdir root (as the
        sibling test above does) makes Typst abort on the line-7 template
        import BEFORE it ever reaches the sibling include or the image
        reference -- so the include/image failure mode that PDF-02's
        canonical refs literally describe (a missing-file break, not a
        root-escape) is never directly exercised in isolation by any
        standing test unless the earlier-failing reference is neutralized
        first.

        This test neutralizes ONLY the template import -- rewriting the
        single occurrence of ``#import "../_template.typ"`` to
        ``#import "_template.typ"``, which is the CORRECT reference from the
        outdir root (the build already wrote ``_template.typ`` there) -- and
        leaves ``include("usage.typ")`` and ``image("../logo.png")``
        byte-identical. That isolates the include/image class cleanly: the
        RED half below fails specifically on the sibling include, and the
        error text is asserted to NOT name ``_template.typ`` (proving the
        masking reference is fully neutralized) and to NOT carry the
        ``api/`` path segment (proving Typst searched at the outdir root,
        not at the master's real directory).

        Both halves are driven from the SAME ``-b typst`` build -- one red,
        one green -- so the two directions are provably talking about
        byte-identical emitted output rather than two separately-built trees
        that could silently drift apart.
        """
        # Step 1: build. One -b typst build serves both halves.
        result = _run_sphinx_build(
            nested_master_render_gate_dir, temp_build_dir_typst, "typst"
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Step 2: preconditions on the emitted master -- hard assertions,
        # not skips. If the emitted shape ever changes, this test must go
        # red loudly, because its whole premise is the file's structure.
        typ_source = temp_build_dir_typst / "api" / "index.typ"
        assert typ_source.exists(), (
            f"api/index.typ was not emitted by -b typst:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        original_text = typ_source.read_text(encoding="utf-8")
        assert '#import "../_template.typ"' in original_text, (
            "Expected the emitted master to carry the relative "
            "'../_template.typ' template import -- the reference this test "
            f"neutralizes before isolating the include/image class:\n"
            f"{original_text}"
        )
        assert 'include("usage.typ")' in original_text, (
            "Expected the emitted master to carry the sibling "
            f"'include(\"usage.typ\")' reference this test isolates:\n"
            f"{original_text}"
        )
        assert 'image("../logo.png")' in original_text, (
            "Expected the emitted master to carry the upward "
            f"'image(\"../logo.png\")' reference:\n{original_text}"
        )

        # Step 3: neutralize ONLY the template import (the RED half's
        # setup). "#import \"_template.typ\"" is the CORRECT reference from
        # the outdir root -- the build already wrote _template.typ there.
        occurrences = original_text.count('#import "../_template.typ"')
        assert occurrences == 1, (
            "Expected exactly one occurrence of the relative template "
            f"import to neutralize, found {occurrences}:\n{original_text}"
        )
        neutralized_text = original_text.replace(
            '#import "../_template.typ"', '#import "_template.typ"'
        )
        assert neutralized_text != original_text, (
            "Expected the template-import rewrite to actually change the "
            "text -- a no-op rewrite would silently invalidate this test's "
            "isolation."
        )
        assert "../_template.typ" not in neutralized_text, (
            "Expected the relative '../_template.typ' form to be fully "
            f"absent after neutralization:\n{neutralized_text}"
        )
        # Pins the isolation the reviewer demanded: precisely one reference
        # was altered -- the sibling include and upward image reference
        # must survive the rewrite byte-identical.
        assert 'include("usage.typ")' in neutralized_text, (
            "Expected the sibling include reference to survive the "
            f"template-import rewrite unchanged:\n{neutralized_text}"
        )
        assert 'image("../logo.png")' in neutralized_text, (
            "Expected the upward image reference to survive the "
            f"template-import rewrite unchanged:\n{neutralized_text}"
        )

        # Write the neutralized copy at the OUTDIR ROOT -- a leading-
        # underscore name that cannot collide with any docname-derived
        # artifact the builders emit, and distinct from the sibling test's
        # "_prefix_basis_copy.typ".
        neutralized_copy = temp_build_dir_typst / "_prefix_basis_neutralized.typ"
        neutralized_copy.write_text(neutralized_text, encoding="utf-8")

        # Step 4: RED. Compile the template-neutralized copy from the
        # OUTDIR ROOT -- the template import now resolves correctly, so
        # Typst reaches the sibling include next and fails on THAT
        # reference instead.
        with pytest.raises(Exception) as exc_info:
            typst.compile(str(neutralized_copy), root=str(temp_build_dir_typst))

        error_text = str(exc_info.value)
        lowered = error_text.lower()
        assert "usage.typ" in error_text, (
            "Expected the error to name the sibling include target "
            "'usage.typ' -- the assertion that makes this test specific "
            f"to the class PDF-02 canonically describes:\n{error_text!r}"
        )
        assert "not found" in lowered, (
            "Expected a missing-file signature (Typst's exact wording is "
            "not a contract, but the failure CLASS is) reproducing the "
            f"include/image compile-basis divergence:\n{error_text!r}"
        )
        assert "_template.typ" not in error_text, (
            "Expected the error to NOT name '_template.typ' -- proof the "
            "masking template reference is fully neutralized and is not "
            f"what failed:\n{error_text!r}"
        )
        api_usage_segment = str(Path("api") / "usage.typ")
        assert api_usage_segment not in error_text, (
            f"Expected the error to NOT contain the '{api_usage_segment}' "
            "path segment -- proof Typst searched at the OUTDIR ROOT (the "
            "wrong-directory compile basis), not at the master's real "
            f"directory:\n{error_text!r}"
        )

        # Step 5: GREEN, same build. The identical include("usage.typ") and
        # image("../logo.png") references that could not resolve from the
        # outdir root DO resolve from outdir/api/ -- the master's real
        # location, unmodified.
        usage_output = temp_build_dir_typst / "api" / "usage.typ"
        assert usage_output.exists(), (
            "Expected the sibling include target 'api/usage.typ' to exist "
            "on disk -- the file the RED half above proved unreachable "
            "from the outdir root."
        )
        logo_output = temp_build_dir_typst / "logo.png"
        assert logo_output.exists(), (
            "Expected the root-level image asset 'logo.png' to exist on "
            "disk -- the file the upward image('../logo.png') reference "
            "climbs to."
        )

        pdf_bytes = typst.compile(
            str(temp_build_dir_typst / "api" / "index.typ"),
            root=str(temp_build_dir_typst),
        )
        assert pdf_bytes.startswith(b"%PDF"), (
            "Expected the UNMODIFIED master at its REAL location "
            "(outdir/api/index.typ) to compile to a valid PDF -- proving "
            'the identical include("usage.typ") and image("../logo.png") '
            "references that failed to resolve from the outdir root DO "
            f"resolve in place, got {pdf_bytes[:20]!r}"
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

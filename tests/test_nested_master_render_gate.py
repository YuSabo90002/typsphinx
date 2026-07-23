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
    rewriting at all, and compiling that copy with ``root=outdir``. Per
    WR-02 / D-10, this test does NOT assert on the compiler's diagnostic
    text -- its subject is fixed structurally instead, by an
    emitted-source precondition (the master's first reference is the
    relative ``#import "../_template.typ": project``, correct only from
    ``outdir/api/``) plus a byte-identity assertion (the outdir-root copy
    is proven byte-for-byte identical to the emitted master, so the ONLY
    variable is the compiled file's directory depth). Given those two
    facts, a real compile failure here is attributable to the
    template-reference class by elimination against the sibling test's
    ablation below, which proves that neutralizing that one import alone
    lets compilation proceed further. (Historical, non-contract record --
    the actual error text observed when this test was written was
    ``TypstError: path "../_template.typ" would escape the project root``;
    an upstream rewording of that text is expected NOT to break this test.)

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
    compiler reaches (and fails on) the sibling include instead. Per
    WR-02 / D-10, this RED half is anchored by a FILESYSTEM precondition
    (``usage.typ`` does not exist at the outdir root) rather than by
    reading the compiler's diagnostic; the raised exception's text is
    captured only for a human failure message. (Historical, non-contract
    record -- the actual error text observed when this test was written
    was ``file not found (searched at <outdir>/usage.typ)``; an upstream
    rewording of that text is expected NOT to break this test.)

    The full three-part ablation this test also carries (Step 6, added by
    D-08) supplies the positive proof of WHICH reference class broke: a
    fully-neutralized copy -- template import AND upward image path both
    rewritten, with the sibling include target and the image asset placed
    at the outdir root -- compiles to real PDF bytes from that same
    location. That the RED half's compile fails and the fully-neutralized
    variant succeeds establishes the failure was caused by the
    sibling-include/upward-image reference class, without reading a single
    character of the compiler's output.

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
        # NOTE (WR-02 / D-10): there is deliberately NO assertion on typst-py's
        # own diagnostic wording here (e.g. "file not found"). Such a negative
        # assertion would silently go vacuous -- always passing, never red -- the
        # moment upstream reworded its text, which is the exact defect class
        # WR-02 removed from this module. `returncode == 0` above already proves
        # the build succeeded, and the typsphinx-authored string checked below is
        # a contract this project owns.
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

        RED-only differential half of the SC#2 proof (WR-02 / D-10): this
        test's subject is fixed WITHOUT reading a single character of
        typst-py's diagnostic text. Reproduces the PRE-FIX compile basis
        VERBATIM -- copy the emitted ``api/index.typ`` to a file at the
        outdir ROOT, with NO rewriting at all, and compile that copy with
        ``typst.compile(copy, root=outdir)``.

        The test's premise is pinned by two structural facts that are
        entirely typsphinx's OWN output, never the compiler's wording:

        1. an emitted-source precondition -- the master's very FIRST
           reference is the relative ``#import "../_template.typ": project``
           (correct only from ``outdir/api/``, where it resolves to
           ``outdir/_template.typ``); and
        2. a byte-identity assertion -- the copy placed at the outdir root
           is proven byte-for-byte identical to the emitted master, so the
           ONLY variable between "resolves" (test 1/3, compiled in place)
           and "fails" (here, compiled from the outdir root) is the
           compiled file's directory depth, never a text difference.

        Given those two facts, Typst's own root-boundary enforcement
        rejecting the copy is the ONLY explicable outcome -- attribution to
        the template import comes by elimination against the sibling test's
        ablation below, which proves that neutralizing that one import
        alone lets compilation proceed to a different, independently-
        explicable failure. This test therefore never asserts on the
        compiler's message; the raised exception's text is captured only to
        surface it to a human in this assertion's failure message, per
        WR-02 / D-10.

        The include/image half -- proven by ablation in
        ``test_sibling_include_fails_at_outdir_root_and_resolves_in_place``
        below -- neutralizes this template import FIRST so the compiler can
        reach the sibling include/image references, then demonstrates a
        fully-neutralized copy compiles clean. The two tests deliberately
        partition the failure space: a future drift between the two classes
        (e.g. the template import disappearing) turns exactly one of them
        red, naming which class moved.

        This is a STANDING test, not a one-time manual verification, so the
        gate can never start passing vacuously after a future refactor
        reintroduces an intermediate copy at the outdir root. (Historical,
        non-contract record: at the time this test was written, the real
        Typst error transcribed was
        ``TypstError: path "../_template.typ" would escape the project
        root`` -- an upstream rewording of this text is expected NOT to
        break this test, because nothing here asserts on it.)
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

        # Pins the test's actual premise: nothing was rewritten, so the only
        # variable is the compiled file's directory depth. The compiler's
        # diagnostic is preserved for humans in the failure message below,
        # via repr of the exception -- it must never be part of an asserted
        # expression (WR-02 / D-10).
        basis_copy_bytes = basis_copy.read_bytes()
        emitted_master_bytes = typ_source.read_bytes()
        assert basis_copy_bytes == emitted_master_bytes, (
            "Expected the outdir-root copy to be byte-identical to the "
            "emitted api/index.typ -- this test's premise is that nothing "
            "was rewritten, so a real compile failure here is attributable "
            "to the directory-depth divergence alone. The compile raised: "
            f"{str(exc_info.value)!r}"
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
        RED half below is anchored by a FILESYSTEM precondition (``usage.typ``
        does NOT exist at the outdir root) rather than by reading the
        compiler's diagnostic (WR-02 / D-10) -- combined with the emitted-
        source preconditions above (the template import neutralized, the
        sibling include and image byte-identical), a failure at the sibling
        include is the only explicable outcome for a compile from this
        location. The raised exception's text is captured only for a human
        reading a failure message, never asserted on directly.

        A three-part ablation (added below, after the pre-existing GREEN
        half) then supplies the positive, discriminating half of the proof:
        neutralizing the include/image reference class too (not merely
        placing files) lets an otherwise-identical copy compile clean from
        the outdir root, which is what actually establishes WHICH reference
        class the RED half's failure belongs to -- without reading a single
        character of the compiler's output.

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

        # Step 4: RED. Filesystem precondition -- established from disk
        # state, not from the compiler's wording (WR-02 / D-10) -- that
        # usage.typ does NOT exist at the outdir root. Combined with the
        # Step 3 preconditions above (the template import neutralized, the
        # sibling include and upward image byte-identical to the emitted
        # master), this makes a failure at the sibling include reference the
        # inevitable and only explicable outcome for the template-
        # neutralized copy compiled from THIS location.
        outdir_root_usage = temp_build_dir_typst / "usage.typ"
        assert not outdir_root_usage.exists(), (
            "Expected 'usage.typ' to NOT exist at the outdir root before "
            "compiling the template-neutralized copy from there -- this "
            "absence is what makes the sibling include the only "
            f"explicable failure point, not the compiler's wording:\n"
            f"{outdir_root_usage}"
        )

        # Compile the template-neutralized copy from the OUTDIR ROOT -- the
        # template import now resolves correctly, so Typst reaches the
        # sibling include next and fails on THAT reference instead.
        with pytest.raises(Exception) as exc_info:
            typst.compile(str(neutralized_copy), root=str(temp_build_dir_typst))

        # Captured only for a human reading a failure message (the ablation
        # assertion in Step 6 below); never part of an asserted expression
        # (WR-02 / D-10).
        red_half_error = str(exc_info.value)

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

        # Step 6: the three-part ablation (D-08, D-09, Pitfall 3) -- the
        # positive, discriminating GREEN proof that establishes WHICH
        # reference class the Step 4 RED half's failure belongs to, without
        # reading a single character of the compiler's output. RESEARCH
        # proved by direct execution that all three parts are required:
        # doing only the file placement (Experiment B) still fails, on the
        # image reference, with an error that superficially resembles the
        # template-class failure and is easy to mis-diagnose as "the
        # ablation did not work" rather than "the ablation is incomplete".
        #
        # Part 1: additionally rewrite the single occurrence of
        # image("../logo.png") to image("logo.png"). Typst's root-boundary
        # enforcement rejects ANY ".." segment once the compiled file
        # itself sits at the compile root, so the upward reference cannot
        # resolve from there no matter what files exist -- neutralizing
        # only the template import (parts 1+3 without this part 2 rewrite)
        # reproduces RESEARCH Experiment B, which does not compile.
        image_occurrences = neutralized_text.count('image("../logo.png")')
        assert image_occurrences == 1, (
            "Expected exactly one occurrence of the upward image reference "
            f"to neutralize, found {image_occurrences}:\n{neutralized_text}"
        )
        fully_neutralized_text = neutralized_text.replace(
            'image("../logo.png")', 'image("logo.png")'
        )
        assert fully_neutralized_text != neutralized_text, (
            "Expected the image-path rewrite to actually change the text -- "
            "a no-op rewrite would silently invalidate the ablation."
        )
        assert 'image("../logo.png")' not in fully_neutralized_text, (
            "Expected the upward 'image(\"../logo.png\")' form to be fully "
            f"absent after the image-path rewrite:\n{fully_neutralized_text}"
        )

        # Part 2: place usage.typ (the sibling include target) at the
        # outdir root -- the normal -b typst build's asset-copy step
        # already put logo.png there, so it is NOT copied again.
        root_usage_copy = temp_build_dir_typst / "usage.typ"
        shutil.copy2(temp_build_dir_typst / "api" / "usage.typ", root_usage_copy)
        assert root_usage_copy.exists(), (
            "Expected 'usage.typ' to exist at the outdir root after "
            f"copying it there for the ablation:\n{root_usage_copy}"
        )
        assert logo_output.exists(), (
            "Expected 'logo.png' to already exist at the outdir root (the "
            "normal -b typst build's asset-copy step) -- the ablation does "
            f"NOT copy it again:\n{logo_output}"
        )

        # Part 3: write the fully-neutralized copy at the OUTDIR ROOT --
        # leading-underscore name, cannot collide with any docname-derived
        # artifact the builders emit, distinct from both
        # '_prefix_basis_copy.typ' and '_prefix_basis_neutralized.typ' --
        # and compile it from that same root.
        fully_neutralized_copy = (
            temp_build_dir_typst / "_prefix_basis_fully_neutralized.typ"
        )
        fully_neutralized_copy.write_text(fully_neutralized_text, encoding="utf-8")

        fully_neutralized_pdf_bytes = typst.compile(
            str(fully_neutralized_copy), root=str(temp_build_dir_typst)
        )
        assert fully_neutralized_pdf_bytes.startswith(b"%PDF"), (
            "Expected the fully-neutralized copy (template import AND "
            "upward image path both rewritten, sibling include target and "
            "image asset both present at the outdir root) to compile to a "
            "valid PDF from the outdir root -- this is the ablation's "
            "positive proof that the sibling-include/upward-image "
            "reference class is what broke the Step 4 RED half, not a "
            "coincidental other failure. The RED half's compile raised: "
            f"{red_half_error!r}. This compile returned: "
            f"{fully_neutralized_pdf_bytes[:20]!r}"
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

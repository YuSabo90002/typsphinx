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
nested docname ``api/index`` emits ``include("usage.typ")`` (sibling, relative
to ``api/``); the temp copy at the outdir root resolved that to
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

**Phase 47 migration (R1-R5, ``47-EXPECTED-STRUCTURE.md``) -- read this
before touching any assertion below.** The content/wrapper split changes
WHICH FILE carries which of this module's two historical reference classes:

- The CONTENT file (unconditionally at ``api/index.typ``, COMP-01) now
  carries the sibling ``include("usage.typ")`` and the upward
  ``image("../logo.png")`` -- both are R1 (translator body markup) and R5
  (toctree include), which stay docname-derived, never target-derived. This
  is exactly the compile_typst_file_to_pdf() basis this module protects:
  the content file's own on-disk directory (``api/``) is where these two
  references resolve FROM, unconditionally.
- The WRAPPER file (target ``nested-master.typ``, resolving at the OUTDIR
  ROOT -- a bare target under OUT-01) carries the bundled-template
  import (``#import "/_template/typst/base.typ"``, root-absolute
  regardless of the wrapper's own nesting, OUT-06) and a single
  ``#include("api/index.typ")`` of its own entry's content file
  (R2/R3, computed by ``compute_content_include_path``) -- it no longer
  carries the sibling include or the image reference at all.

The two historical "pre-fix basis" reproductions therefore no longer target
a single combined "master" file carrying BOTH a template import and the
sibling include/image (that file no longer exists) -- they are re-pointed
at the CONTENT file, which is the file that still carries the
directory-sensitive sibling include/image references PDF-02 was originally
about. The template-import half of the original two-part proof has no
content-level equivalent (content carries no template import at all,
R2) -- Phase 47's structural guarantee (content is ALWAYS at its
docname-derived location, never copied or relocated) makes that PARTICULAR
divergence unreachable by construction, so this module now proves ONE
combined RED/GREEN/ablation cycle for the include/image class instead of
two separate classes. The wrapper's OWN two references (template import,
content include) are each proven correct exhaustively elsewhere
(``tests/test_template_import_path.py``,
``tests/test_two_layer_output_gate.py::TestComputeContentIncludePath``) --
duplicating that proof here would not add signal.

Fixture shape (D-07, migrated): the fixture's only entry names docname
``api/index`` with a BARE target, ``nested-master.typ`` (previously
``index`` -- renamed per the general fixture de-collision convention in
``47-EXPECTED-STRUCTURE.md``, not because ``index`` collided with anything
in THIS specific fixture; see ``tests/fixtures/nested_master_render_gate/
conf.py``'s own comment for the measured reasoning). ``api/index`` toctrees
the sibling ``api/usage`` (emits ``include("usage.typ")``) and references a
root-level image (emits ``image("../logo.png")``, crossing a directory
boundary upward while staying inside ``outdir``).

Confirmed both directions:

- **PASSES** with the fix, in TWO complementary proofs:

  - ``test_typstpdf_nested_master_resolves_include_and_image`` drives the
    real ``-b typstpdf`` path end-to-end and asserts the compiled
    ``nested-master.pdf`` (the WRAPPER's own resolved path, at the outdir
    root) exists with the ``%PDF`` magic prefix, alongside the
    docname-derived content and its sibling include target.
  - ``test_content_compile_basis_fails_at_outdir_root_and_resolves_in_place``'s
    own GREEN half asserts the unmodified content file, compiled at its
    real location (``outdir/api/index.typ``, ``root=outdir``), produces a
    valid PDF -- proving the ``include("usage.typ")`` and
    ``image("../logo.png")`` references resolve in place.
  - ``test_typst_builder_output_compiles_manually`` additionally compiles
    the ``-b typst`` WRAPPER output directly via ``typst.compile()``,
    mirroring exactly what a user running ``typst compile`` by hand does
    against the file the ``-b typst`` build log names as "the file to
    compile" (SC#3 / D-09).

- **FAILS** against a manually-reproduced outdir-root compile basis, in one
  standing RED/GREEN/ablation cycle
  (``test_content_compile_basis_fails_at_outdir_root_and_resolves_in_place``):
  copying the CONTENT file verbatim to the outdir root and compiling it
  from there fails at the sibling ``include("usage.typ")`` (the first
  directory-sensitive reference the file's own source order reaches --
  Typst never gets far enough to evaluate the later ``image(...)`` line).
  Per WR-02 / D-10, the RED half is anchored by a FILESYSTEM precondition
  (``usage.typ`` does not exist at the outdir root) rather than by reading
  the compiler's diagnostic text. A three-part ablation (place ``usage.typ``
  at the outdir root AND rewrite the upward ``image("../logo.png")`` to the
  root-safe ``image("logo.png")``) then supplies the positive,
  discriminating proof that the sibling-include/upward-image reference
  class is what breaks the RED half, without reading a single character of
  the compiler's output -- mirroring this module's pre-Phase-47 ablation
  discipline (D-08, D-09, Pitfall 3 in ``22.1-RESEARCH.md``).
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
    the RED/GREEN/ablation reproduction and the D-09 cross-builder
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
    compile every emitted file (content AND wrapper) at its own real,
    on-disk location for a docname/target pair that DIVERGES in directory
    (docname ``api/index``, wrapper target resolving at the outdir root),
    and that a manually-reproduced outdir-root compile basis for the
    content file demonstrably still fails.

    Requirements: PDF-02 (Phase 22.1 scope), migrated per COMP-01/R1-R5
    (Phase 47).
    """

    def test_typstpdf_nested_master_resolves_include_and_image(
        self, nested_master_render_gate_dir, temp_build_dir
    ):
        """
        SC#1: Build the fixture through ``-b typstpdf`` and confirm the
        nested docname's CONTENT file carries its sibling include and
        upward image reference intact, and its WRAPPER (at the outdir
        root, per OUT-01's bare-target rule) compiles to PDF.

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

        # R1/COMP-01: the docname-derived CONTENT file, unconditional.
        content_output = temp_build_dir / "api" / "index.typ"
        assert content_output.exists(), (
            f"api/index.typ (content) was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        content_text = content_output.read_text(encoding="utf-8")
        assert "#show: project.with(" not in content_text, (
            f"Expected NO template application in the content file:\n" f"{content_text}"
        )
        assert 'include("usage.typ")' in content_text, (
            f"Expected the content file to carry the sibling include:\n"
            f"{content_text}"
        )
        assert 'image("../logo.png")' in content_text, (
            f"Expected the content file to carry the upward image "
            f"reference:\n{content_text}"
        )

        usage_output = temp_build_dir / "api" / "usage.typ"
        assert usage_output.exists(), (
            f"api/usage.typ (the sibling include target's own content "
            f"file) was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        logo_output = temp_build_dir / "logo.png"
        assert logo_output.exists(), (
            "logo.png (the root-level image asset) was not copied into the "
            f"output tree -- the upward image('../logo.png') reference "
            f"cannot resolve without it:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # R2/R3/R4: the WRAPPER, resolving at the OUTDIR ROOT (bare target,
        # OUT-01) -- one directory level away from its own entry's content
        # file at api/index.typ.
        wrapper_output = temp_build_dir / "nested-master.typ"
        assert wrapper_output.exists(), (
            f"nested-master.typ (wrapper) was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        wrapper_text = wrapper_output.read_text(encoding="utf-8")
        assert '#import "/_template/typst/base.typ"' in wrapper_text, (
            f"Expected the wrapper's root-absolute bundled-template "
            f"import (OUT-06):\n{wrapper_text}"
        )
        assert '#include("api/index.typ")' in wrapper_text, (
            f"Expected the wrapper to #include() its own entry's content "
            f"file at its real, docname-derived path:\n{wrapper_text}"
        )

        pdf_output = temp_build_dir / "nested-master.pdf"
        assert pdf_output.exists(), (
            f"nested-master.pdf was not produced -- typst.compile() "
            f"aborted:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "Generated PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_content_compile_basis_fails_at_outdir_root_and_resolves_in_place(
        self, nested_master_render_gate_dir, temp_build_dir_typst
    ):
        """
        RED/GREEN/ablation cycle (D-08, D-09, Pitfall 3;
        re-derived Phase 47 onto the CONTENT file -- see module docstring
        for why the pre-Phase-47 two-class split collapses into one here).

        RED half (WR-02 / D-10: anchored by structural/filesystem
        preconditions, never by reading the compiler's diagnostic text):
        copy the emitted ``api/index.typ`` CONTENT file to a file at the
        outdir ROOT, with NO rewriting at all, and compile that copy with
        ``typst.compile(copy, root=outdir)``. The content's own source
        order reaches the sibling ``include("usage.typ")`` BEFORE the
        upward ``image("../logo.png")``, so a verbatim copy at the outdir
        root fails on the sibling include first -- ``usage.typ`` does not
        exist there. The copy is proven byte-identical to the emitted
        content first, so the ONLY variable is the compiled file's
        directory depth, never a text difference.

        GREEN half, same build: the UNMODIFIED content file, compiled at
        its real location (``outdir/api/index.typ``, ``root=outdir``),
        produces a valid PDF -- proving the identical
        ``include("usage.typ")`` and ``image("../logo.png")`` references
        that failed to resolve from the outdir root DO resolve in place.

        Ablation (the positive, discriminating proof of WHICH reference
        class broke the RED half, without reading the compiler's output):
        place ``usage.typ`` at the outdir root AND rewrite the upward
        ``image("../logo.png")`` to the root-safe ``image("logo.png")``
        (Typst's root-boundary enforcement rejects ANY ``..`` segment once
        the compiled file itself sits at the compile root, so the upward
        reference cannot resolve from there no matter what files exist --
        neutralizing only the sibling include reproduces a partial
        ablation that still fails on the image reference). The
        fully-neutralized copy then compiles clean from the outdir root.
        """
        # Step 1: build. One -b typst build serves the whole cycle.
        result = _run_sphinx_build(
            nested_master_render_gate_dir, temp_build_dir_typst, "typst"
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Step 2: preconditions on the emitted content -- hard assertions,
        # not skips. If the emitted shape ever changes, this test must go
        # red loudly, because its whole premise is the file's structure.
        content_source = temp_build_dir_typst / "api" / "index.typ"
        assert content_source.exists(), (
            f"api/index.typ (content) was not emitted by -b typst:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        original_text = content_source.read_text(encoding="utf-8")
        assert 'include("usage.typ")' in original_text, (
            "Expected the content file to carry the sibling "
            f"'include(\"usage.typ\")' reference this test RED-halves:\n"
            f"{original_text}"
        )
        assert 'image("../logo.png")' in original_text, (
            "Expected the content file to carry the upward "
            f"'image(\"../logo.png\")' reference:\n{original_text}"
        )
        include_index = original_text.index('include("usage.typ")')
        image_index = original_text.index('image("../logo.png")')
        assert include_index < image_index, (
            "Expected the sibling include to appear BEFORE the upward "
            "image reference in source order -- this test's RED half "
            "relies on Typst reaching (and failing on) the include first:\n"
            f"{original_text}"
        )

        # Step 3: RED. Reproduce the outdir-root compile basis VERBATIM --
        # copy the content file to a file at the OUTDIR ROOT, with NO
        # rewriting at all, and compile that copy with root=outdir.
        basis_copy = temp_build_dir_typst / "_content_basis_copy.typ"
        shutil.copy2(content_source, basis_copy)
        basis_copy_bytes = basis_copy.read_bytes()
        emitted_content_bytes = content_source.read_bytes()
        assert basis_copy_bytes == emitted_content_bytes, (
            "Expected the outdir-root copy to be byte-identical to the "
            "emitted api/index.typ -- this test's premise is that nothing "
            "was rewritten, so a real compile failure here is attributable "
            "to the directory-depth divergence alone."
        )

        outdir_root_usage = temp_build_dir_typst / "usage.typ"
        assert not outdir_root_usage.exists(), (
            "Expected 'usage.typ' to NOT exist at the outdir root before "
            "compiling the verbatim copy from there -- this absence is "
            "what makes the sibling include the only explicable failure "
            f"point, not the compiler's wording:\n{outdir_root_usage}"
        )

        with pytest.raises(Exception) as exc_info:
            typst.compile(str(basis_copy), root=str(temp_build_dir_typst))
        # Captured only for a human reading a failure message (the
        # ablation assertion below); never part of an asserted expression
        # (WR-02 / D-10).
        red_half_error = str(exc_info.value)

        # Step 4: GREEN, same build. The UNMODIFIED content file, compiled
        # at its REAL location (outdir/api/index.typ), resolves both
        # references correctly.
        pdf_bytes = typst.compile(str(content_source), root=str(temp_build_dir_typst))
        assert pdf_bytes.startswith(b"%PDF"), (
            "Expected the UNMODIFIED content file at its REAL location "
            "(outdir/api/index.typ) to compile to a valid PDF -- proving "
            'the identical include("usage.typ") and image("../logo.png") '
            "references that failed to resolve from the outdir root DO "
            f"resolve in place, got {pdf_bytes[:20]!r}"
        )

        # Step 5: the ablation -- the positive, discriminating GREEN proof
        # that establishes WHICH reference class the RED half's failure
        # belongs to, without reading a single character of the compiler's
        # output.
        #
        # Part 1: rewrite the single occurrence of image("../logo.png") to
        # image("logo.png"). Typst's root-boundary enforcement rejects ANY
        # ".." segment once the compiled file itself sits at the compile
        # root, so the upward reference cannot resolve from there no
        # matter what files exist -- placing usage.typ alone (without this
        # rewrite) still fails, on the image reference.
        image_occurrences = original_text.count('image("../logo.png")')
        assert image_occurrences == 1, (
            "Expected exactly one occurrence of the upward image "
            f"reference to neutralize, found {image_occurrences}:\n"
            f"{original_text}"
        )
        neutralized_text = original_text.replace(
            'image("../logo.png")', 'image("logo.png")'
        )
        assert neutralized_text != original_text, (
            "Expected the image-path rewrite to actually change the text "
            "-- a no-op rewrite would silently invalidate the ablation."
        )
        assert 'image("../logo.png")' not in neutralized_text, (
            "Expected the upward 'image(\"../logo.png\")' form to be "
            f"fully absent after the image-path rewrite:\n{neutralized_text}"
        )
        assert 'include("usage.typ")' in neutralized_text, (
            "Expected the sibling include reference to survive the "
            f"image-path rewrite unchanged:\n{neutralized_text}"
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
        logo_output = temp_build_dir_typst / "logo.png"
        assert logo_output.exists(), (
            "Expected 'logo.png' to already exist at the outdir root (the "
            "normal -b typst build's asset-copy step) -- the ablation does "
            f"NOT copy it again:\n{logo_output}"
        )

        # Part 3: write the fully-neutralized copy at the OUTDIR ROOT --
        # leading-underscore name, cannot collide with any docname-derived
        # or target-derived artifact the builders emit -- and compile it
        # from that same root.
        fully_neutralized_copy = (
            temp_build_dir_typst / "_content_basis_fully_neutralized.typ"
        )
        fully_neutralized_copy.write_text(neutralized_text, encoding="utf-8")

        fully_neutralized_pdf_bytes = typst.compile(
            str(fully_neutralized_copy), root=str(temp_build_dir_typst)
        )
        assert fully_neutralized_pdf_bytes.startswith(b"%PDF"), (
            "Expected the fully-neutralized copy (upward image path "
            "rewritten, sibling include target present at the outdir "
            "root) to compile to a valid PDF from the outdir root -- this "
            "is the ablation's positive proof that the sibling-include/"
            "upward-image reference class is what broke the RED half, "
            "not a coincidental other failure. The RED half's compile "
            f"raised: {red_half_error!r}. This compile returned: "
            f"{fully_neutralized_pdf_bytes[:20]!r}"
        )

    def test_typst_builder_output_compiles_manually(
        self, nested_master_render_gate_dir, temp_build_dir_typst
    ):
        """
        SC#3 / D-09: Compile the ``-b typst`` output's WRAPPER directly via
        ``typst.compile()``, reproducing exactly what a user running
        ``typst compile`` by hand does against the file the build log
        names as the one to compile (D-07's build-log line) -- pinning
        cross-builder equivalence.

        After D-01 (and, post-Phase-47, structurally: only wrapper files
        are ever compiled, COMP-02/R4), ``-b typstpdf`` and ``-b typst``
        compile the same WRAPPER file at the same location, so this
        equivalence is structural; this test pins that structural property
        so a future refactor reintroducing an intermediate copy is caught.
        """
        result = _run_sphinx_build(
            nested_master_render_gate_dir, temp_build_dir_typst, "typst"
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        wrapper_output = temp_build_dir_typst / "nested-master.typ"
        assert wrapper_output.exists(), (
            f"nested-master.typ (wrapper) was not emitted by -b typst:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        pdf_bytes = typst.compile(str(wrapper_output), root=str(temp_build_dir_typst))
        assert pdf_bytes.startswith(b"%PDF"), (
            "Manually compiling the -b typst wrapper output did not "
            f"produce a valid PDF -- got {pdf_bytes[:20]!r}"
        )

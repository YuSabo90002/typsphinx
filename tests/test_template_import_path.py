"""
Case-matrix unit test plus real-compile render gate for the depth-based
template-import computation (gap ``G-22.1-4``, review finding CR-01,
critical, ``22.1-REVIEW.md``).

Root cause: ``TypstWriter.translate()`` used to compute a master document's
``_template.typ`` import by calling the translator's docname-to-docname
relativization helper (``_compute_relative_include_path``) with the literal
string ``"_template"`` as a FAKE target docname. When the master's own
directory portion was itself literally named ``_template``, that synthetic
sentinel collided with a real path component, the helper's same-directory /
common-parent logic resolved it as a path-to-itself, and the caller
concatenated ``".typ"`` onto the resulting stem-less string. The pre-fix
emitter, captured from a real ``sphinx-build -b typst`` run during
diagnosis, produced:

    docname                   emitted import (pre-fix)      status
    ------------------------  -----------------------------  -------
    "_template/index"         #import "..typ"                BROKEN
    "_template/sub/index"     #import "../.typ"               BROKEN
    "index"                   #import "_template.typ"         correct
    "api/index"               #import "../_template.typ"      correct
    "a/b/index"               #import "../../_template.typ"   correct
    "a/_template/index"       #import "../../_template.typ"   correct

Fix (Phase 22.1): computed the import purely from the number of path
components in the DOCNAME's own PARENT -- how many directories separate the
master from the outdir root, where ``_write_template_file()``
(``typsphinx/builder.py``) unconditionally writes ``_template.typ``. This
has no string-equality dependence on the reserved ``_template`` basename, so
no real directory name can collide with or impersonate it.

**Phase 47 migration (input changed: docname -> wrapper directory,
R2/47-EXPECTED-STRUCTURE.md).** The content/wrapper split moved template
application -- including the ``_template.typ`` import -- from a per-docname
"master" file to a per-``typst_documents``-entry WRAPPER file, which now
resolves at its own TARGET-derived path (OUT-01), independent of its
docname's own directory. The depth computation therefore can no longer take
a docname as input: a wrapper written outside its docname's own directory
(a bare or differently-nested target) would otherwise import a
``_template.typ`` reference computed for a directory nothing was actually
written to. ``typsphinx.writer.compute_template_import_path_for_dir()``
(landed by plan 47-02) is the same depth-only ``"../"`` counter, re-pointed
at the WRAPPER's own resolved output directory instead of the docname's
directory -- the underlying arithmetic (a pure function of path-segment
count, with no string-equality dependence on the reserved ``_template``
name) is unchanged, so the four already-correct cases and the three
previously-broken ``_template``-directory cases below are byte-identical
before and after this re-pointing.

``typsphinx.writer.TypstWriter._compute_template_import_path()`` (the
docname-based staticmethod this module used to test directly) is left
untouched in ``typsphinx/writer.py`` -- this plan's own ``files_modified``
scope is tests/fixtures only (verified: it now has no production caller
anywhere in ``typsphinx/``, per plan 47-08's Task 1 action; that residual
dead code is out of this plan's scope to remove and is deferred to a later
plan's cleanup, recorded as a deviation in this plan's SUMMARY).

This module is split into two parts:

- A fast, offline parametrized unit test over the full seven-row case
  matrix (this class, ``TestComputeTemplateImportPathForDir``) -- no Sphinx
  build, no ``typst`` import, no fixtures, runs in milliseconds and stays
  green even where the Typst compiler is unavailable. Rewritten over
  WRAPPER directories (Phase 47) rather than docnames.
- A real-compile render gate (``TestTemplateNamedDirMasterRenderGate``)
  that drives a real ``-b typst`` build of a fixture whose only docnames sit
  under a directory literally named ``_template``, and compiles both
  emitted WRAPPERS for real via ``typst.compile(wrapper, root=outdir)`` --
  proving the emitted reference actually RESOLVES, not merely that it reads
  correctly. Migrated (R1-R5): the fixture's two entries now target
  distinct, non-colliding names (``template-dir-master.typ``/
  ``template-dir-sub.typ``, both bare -- resolving at the outdir root under
  OUT-01) instead of the pre-split identity-basename targets that collided
  under the content/wrapper split (BLD-02, two entries resolving to the
  same physical path).
"""

import subprocess
import sys
from pathlib import Path

import pytest

from typsphinx.writer import compute_template_import_path_for_dir

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

# The full seven-case matrix, now over WRAPPER RESOLVED DIRECTORIES rather
# than docnames (Phase 47). Each row is (wrapper_relative_dir, expected
# import path, label). The "fence" label marks a case that was ALREADY
# CORRECT before the original Phase 22.1 fix -- its expected value is the
# value the pre-fix code produced for the equivalent docname; changing it
# to make a future refactor pass would be a behavioral change, not a test
# fix. The "repaired" label marks one of the three cases the original fix
# repaired -- the CR-01 defect (a directory literally named ``_template``).
# Under compute_template_import_path_for_dir(), all seven rows are computed
# by the SAME pure depth-count arithmetic (no string-equality dependence on
# "_template"), so nothing here is actually "broken" anymore; the labels
# are retained as a historical anti-regression fence, not a live red/green
# distinction.
TEMPLATE_IMPORT_PATH_CASES = [
    ("", "_template.typ", "fence-root"),
    ("api", "../_template.typ", "fence-depth1"),
    ("a/b", "../../_template.typ", "fence-depth2"),
    ("a/_template", "../../_template.typ", "fence-non-immediate-parent"),
    ("_template", "../_template.typ", "repaired-depth1"),
    ("_template/sub", "../../_template.typ", "repaired-depth2"),
    ("_template/a/b", "../../../_template.typ", "repaired-depth3"),
]


class TestComputeTemplateImportPathForDir:
    """
    Parametrized case matrix for
    ``typsphinx.writer.compute_template_import_path_for_dir``.

    Pins all seven cases from the original Phase 22.1 ``<behavior>`` block,
    re-derived over WRAPPER RESOLVED DIRECTORIES (Phase 47): the three
    previously-broken ``_template``-directory cases (labelled
    ``repaired-*``) and the four already-correct cases (labelled
    ``fence-*``, the anti-regression fence). The parametrize ``ids=`` name
    which category a failure moved.

    These tests call the module-level function directly -- no Sphinx build,
    no ``typst`` import, no fixtures required.
    """

    @pytest.mark.parametrize(
        "wrapper_relative_dir,expected,label",
        TEMPLATE_IMPORT_PATH_CASES,
        ids=[case[2] for case in TEMPLATE_IMPORT_PATH_CASES],
    )
    def test_compute_template_import_path_for_dir(
        self, wrapper_relative_dir, expected, label
    ):
        """
        Each row's expected value for a ``fence-*`` case is the exact value
        the original Phase 22.1 pre-fix code already produced for the
        equivalent docname -- changing one of those expectations to make a
        future refactor pass is a behavioral change, not a test fix. Each
        ``repaired-*`` row is one of the three directories the pre-Phase-
        22.1 code emitted a malformed, stem-less reference for.
        """
        result = compute_template_import_path_for_dir(wrapper_relative_dir)
        assert result == expected, (
            f"[{label}] wrapper_relative_dir={wrapper_relative_dir!r}: "
            f"expected {expected!r}, got {result!r}"
        )

    def test_fence_rows_match_depth_invariant(self):
        """
        Independent restatement of the anti-regression fence: for every
        wrapper directory that does NOT begin with the reserved
        ``_template`` name, the result equals the number of upward ``../``
        segments implied by the directory's own path-segment count. This
        does not just re-read ``TEMPLATE_IMPORT_PATH_CASES`` -- it
        recomputes the expected depth from each fence directory's own path
        structure.
        """
        fence_cases = [
            (wrapper_relative_dir, expected)
            for wrapper_relative_dir, expected, label in TEMPLATE_IMPORT_PATH_CASES
            if label.startswith("fence-")
        ]
        assert fence_cases, "Expected at least one fence-labelled case"

        for wrapper_relative_dir, expected in fence_cases:
            depth = wrapper_relative_dir.count("/") + 1 if wrapper_relative_dir else 0
            expected_from_depth = "../" * depth + "_template.typ"
            assert expected == expected_from_depth, (
                f"wrapper_relative_dir={wrapper_relative_dir!r}: table "
                f"expectation {expected!r} does not match the "
                f"independently-derived depth expectation "
                f"{expected_from_depth!r}"
            )
            result = compute_template_import_path_for_dir(wrapper_relative_dir)
            assert result == expected_from_depth, (
                f"wrapper_relative_dir={wrapper_relative_dir!r}: expected "
                f"{expected_from_depth!r} derived from directory depth, "
                f"got {result!r}"
            )

    def test_template_named_directory_case_is_present(self):
        """
        Explicit standing marker for the CR-01 case (the plan's own
        acceptance criterion): a wrapper directory literally named
        ``_template`` must resolve to ``../_template.typ`` -- proving the
        depth computation has no string-equality dependence on the reserved
        basename even when a real directory component impersonates it.
        """
        matching = [
            (wrapper_relative_dir, expected)
            for wrapper_relative_dir, expected, _label in TEMPLATE_IMPORT_PATH_CASES
            if wrapper_relative_dir == "_template"
        ]
        assert matching == [("_template", "../_template.typ")]
        assert compute_template_import_path_for_dir("_template") == "../_template.typ"


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


@pytest.fixture
def template_named_dir_master_dir():
    """Return the path to the template_named_dir_master fixture project."""
    return Path(__file__).parent / "fixtures" / "template_named_dir_master"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for the -b typst build output."""
    return tmp_path / "_build"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the template-named-dir-master render gate",
)
class TestTemplateNamedDirMasterRenderGate:
    """
    Real-compile render gate (GATE-01 shape, D-06) proving that a project
    whose docnames live inside a directory literally named ``_template``
    still emits correct, resolvable content AND wrapper files, and that
    both wrappers compile for real to valid PDF bytes via
    ``typst.compile(wrapper, root=outdir)``.

    Fixture shape (migrated, Phase 47): ``tests/fixtures/
    template_named_dir_master/`` has two docnames, ``_template/index``
    (depth 1) and ``_template/sub/index`` (depth 2), each named by its own
    ``typst_documents`` entry with a DISTINCT, bare (no path separator)
    target -- ``template-dir-master.typ`` and ``template-dir-sub.typ``.
    Content files stay unconditionally docname-derived (COMP-01), landing
    inside the ``_template/`` directory tree exactly as before; both
    wrappers resolve at the OUTDIR ROOT under OUT-01 (a bare target carries
    no path component), so both import the shared ``_template.typ`` at
    depth 0 -- this render gate's own real-compile proof that a CONTENT
    file's own directory being literally named ``_template`` does not
    perturb an unrelated WRAPPER's depth computation. The CR-01
    depth-from-a-``_template``-named-WRAPPER-directory case itself is
    covered directly by ``TestComputeTemplateImportPathForDir`` above (its
    ``repaired-depth1``/``repaired-depth2``/``repaired-depth3`` rows,
    including the explicit ``test_template_named_directory_case_is_present``
    marker) -- the underlying arithmetic those unit cases pin is exactly
    what this render gate's own wrapper-depth-0 outcome relies on, just at
    a different depth.
    """

    def test_template_named_dir_master_resolves_and_compiles(
        self, template_named_dir_master_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typst``, then assert:

        1. The build produced ``_template.typ`` as a FILE at the outdir
           root, coexisting with a ``_template/`` DIRECTORY beside it (the
           docname-derived content files' own home) -- the structural
           precondition the depth-based computation relies on.
        2. Both docnames' CONTENT files exist at their docname-derived
           paths, carrying no template application (R1).
        3. Both entries' WRAPPER files exist at their bare, outdir-root
           target paths, each carrying the depth-0 ``_template.typ``
           import and an ``#include()`` of their own entry's content file
           (R2/R3).
        4. Both wrapper files compile for real via
           ``typst.compile(wrapper, root=outdir)`` to bytes opening with
           the PDF magic prefix -- proving the emitted reference actually
           RESOLVES, not merely that it reads correctly.
        """
        result = _run_sphinx_build(
            template_named_dir_master_dir, temp_build_dir, "typst"
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # --- Structural precondition ---
        template_file = temp_build_dir / "_template.typ"
        assert template_file.is_file(), (
            "Expected _template.typ to be written as a FILE at the outdir "
            f"root:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        template_dir = temp_build_dir / "_template"
        assert template_dir.is_dir(), (
            "Expected a _template/ DIRECTORY to exist beside _template.typ "
            "at the outdir root -- the docname-derived content files' own "
            f"home:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # --- Content files (R1, COMP-01): docname-derived, no template ---
        depth1_content = temp_build_dir / "_template" / "index.typ"
        assert depth1_content.exists(), (
            f"_template/index.typ (content) was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        depth1_content_text = depth1_content.read_text(encoding="utf-8")
        assert "#show: project.with(" not in depth1_content_text, (
            f"Expected NO template application in the content file:\n"
            f"{depth1_content_text}"
        )

        depth2_content = temp_build_dir / "_template" / "sub" / "index.typ"
        assert depth2_content.exists(), (
            f"_template/sub/index.typ (content) was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        depth2_content_text = depth2_content.read_text(encoding="utf-8")
        assert "#show: project.with(" not in depth2_content_text, (
            f"Expected NO template application in the content file:\n"
            f"{depth2_content_text}"
        )

        # --- Wrapper files (R2/R3): bare targets, outdir root, depth-0 ---
        wrapper1 = temp_build_dir / "template-dir-master.typ"
        assert wrapper1.exists(), (
            f"template-dir-master.typ (wrapper) was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        wrapper1_text = wrapper1.read_text(encoding="utf-8")
        assert '#import "_template.typ"' in wrapper1_text, (
            "Expected the depth-1 entry's wrapper (at the outdir root) to "
            f"import the template at depth 0:\n{wrapper1_text[:400]}"
        )
        assert '#include("_template/index.typ")' in wrapper1_text, (
            "Expected the wrapper to #include() its own entry's content "
            f"file:\n{wrapper1_text[:400]}"
        )

        wrapper2 = temp_build_dir / "template-dir-sub.typ"
        assert wrapper2.exists(), (
            f"template-dir-sub.typ (wrapper) was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        wrapper2_text = wrapper2.read_text(encoding="utf-8")
        assert '#import "_template.typ"' in wrapper2_text, (
            "Expected the depth-2 entry's wrapper (also at the outdir "
            f"root) to import the template at depth 0:\n{wrapper2_text[:400]}"
        )
        assert '#include("_template/sub/index.typ")' in wrapper2_text, (
            "Expected the wrapper to #include() its own entry's content "
            f"file:\n{wrapper2_text[:400]}"
        )

        # Neither wrapper emits a malformed stem-less reference: the import
        # target's final path component must equal the reserved template
        # filename, expressed structurally rather than by string-matching
        # any specific malformed shape.
        for label, text in (("wrapper1", wrapper1_text), ("wrapper2", wrapper2_text)):
            for line in text.splitlines():
                if "#import" in line and "_template" in line:
                    quoted = line.split('"')[1]
                    final_component = quoted.rsplit("/", 1)[-1]
                    assert final_component == "_template.typ", (
                        f"[{label}] Expected the template import's final "
                        f"path component to be '_template.typ', got "
                        f"{final_component!r} in line: {line!r}"
                    )

        # --- Real compile (the GATE-01 bar) ---
        wrapper1_pdf = typst.compile(str(wrapper1), root=str(temp_build_dir))
        assert wrapper1_pdf.startswith(b"%PDF"), (
            "Expected the depth-1 entry's wrapper to compile to a valid "
            f"PDF, got {wrapper1_pdf[:20]!r}"
        )
        wrapper2_pdf = typst.compile(str(wrapper2), root=str(temp_build_dir))
        assert wrapper2_pdf.startswith(b"%PDF"), (
            "Expected the depth-2 entry's wrapper to compile to a valid "
            f"PDF, got {wrapper2_pdf[:20]!r}"
        )

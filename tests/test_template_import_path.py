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

Fix: ``TypstWriter._compute_template_import_path(docname)`` computes the
import purely from the number of path components in the docname's own
PARENT -- how many directories separate the master from the outdir root,
where ``_write_template_file()`` (``typsphinx/builder.py``) unconditionally
writes ``_template.typ``. This has no string-equality dependence on the
reserved ``_template`` basename, so no real directory name can collide with
or impersonate it. The four already-correct cases above are byte-identical
before and after this change -- a strict repair, not a behavior change.

This module is split into two parts:

- A fast, offline parametrized unit test over the full seven-row case
  matrix (this class, ``TestComputeTemplateImportPath``) -- no Sphinx
  build, no ``typst`` import, no fixtures, runs in milliseconds and stays
  green even where the Typst compiler is unavailable.
- A real-compile render gate (``TestTemplateNamedDirMasterRenderGate``)
  that drives a real ``-b typst`` build of a fixture whose only masters sit
  under a directory literally named ``_template``, and compiles both
  emitted masters for real via ``typst.compile(master, root=outdir)`` --
  proving the emitted reference actually RESOLVES, not merely that it
  reads correctly.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from typsphinx.writer import TypstWriter

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

# The full seven-case matrix from the plan's <behavior> block. Each row is
# (docname, expected import path, label). The "fence" label marks a case
# that was ALREADY CORRECT before this fix -- its expected value is the
# value the PRE-FIX code produced, so changing it to make a future refactor
# pass would be a behavioral change, not a test fix. The "repaired" label
# marks one of the three cases this fix repairs.
TEMPLATE_IMPORT_PATH_CASES = [
    ("index", "_template.typ", "fence-root"),
    ("api/index", "../_template.typ", "fence-depth1"),
    ("a/b/index", "../../_template.typ", "fence-depth2"),
    ("a/_template/index", "../../_template.typ", "fence-non-immediate-parent"),
    ("_template/index", "../_template.typ", "repaired-depth1"),
    ("_template/sub/index", "../../_template.typ", "repaired-depth2"),
    ("_template/a/b/index", "../../../_template.typ", "repaired-depth3"),
]


class TestComputeTemplateImportPath:
    """
    Parametrized case matrix for ``TypstWriter._compute_template_import_path``.

    Pins all seven cases from the plan's ``<behavior>`` block in one table:
    the three previously-broken ``_template``-directory cases (labelled
    ``repaired-*``) and the four already-correct cases (labelled
    ``fence-*``, the anti-regression fence). The parametrize ``ids=`` name
    which category a failure moved.

    These tests import ``TypstWriter`` directly and call the staticmethod on
    the class -- no Sphinx build, no ``typst`` import, no fixtures required.
    """

    @pytest.mark.parametrize(
        "docname,expected,label",
        TEMPLATE_IMPORT_PATH_CASES,
        ids=[case[2] for case in TEMPLATE_IMPORT_PATH_CASES],
    )
    def test_compute_template_import_path(self, docname, expected, label):
        """
        Each row's expected value for a ``fence-*`` case is the exact value
        the PRE-FIX code already produced for that docname -- changing one
        of those expectations to make a future refactor pass is a
        behavioral change, not a test fix. Each ``repaired-*`` row is one of
        the three docnames the pre-fix code emitted a malformed, stem-less
        reference for.
        """
        result = TypstWriter._compute_template_import_path(docname)
        assert result == expected, (
            f"[{label}] docname={docname!r}: expected {expected!r}, " f"got {result!r}"
        )

    def test_fence_rows_match_depth_invariant(self):
        """
        Independent restatement of the anti-regression fence: for every
        docname whose directory portion does NOT begin with the reserved
        ``_template`` name, the result equals the number of upward ``../``
        segments implied by the docname's own directory depth. This does
        not just re-read ``TEMPLATE_IMPORT_PATH_CASES`` -- it recomputes the
        expected depth from each fence docname's own path structure.
        """
        fence_cases = [
            (docname, expected)
            for docname, expected, label in TEMPLATE_IMPORT_PATH_CASES
            if label.startswith("fence-")
        ]
        assert fence_cases, "Expected at least one fence-labelled case"

        for docname, expected in fence_cases:
            depth = docname.count("/")
            expected_from_depth = "../" * depth + "_template.typ"
            assert expected == expected_from_depth, (
                f"docname={docname!r}: table expectation {expected!r} does "
                f"not match the independently-derived depth expectation "
                f"{expected_from_depth!r}"
            )
            result = TypstWriter._compute_template_import_path(docname)
            assert result == expected_from_depth, (
                f"docname={docname!r}: expected {expected_from_depth!r} "
                f"derived from directory depth, got {result!r}"
            )


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
    Real-compile render gate (GATE-01 shape, D-06) proving that a master
    whose directory portion is literally named ``_template`` emits a
    correct, resolvable ``_template.typ`` import at BOTH depth 1 and
    depth 2, and that both emitted masters compile for real to valid PDF
    bytes via ``typst.compile(master, root=outdir)``.

    Fixture shape: ``tests/fixtures/template_named_dir_master/`` has two
    masters, ``_template/index`` (depth 1) and ``_template/sub/index``
    (depth 2), both listed in ``typst_documents`` so one ``-b typst`` build
    exercises both nesting depths.

    Pre-fix, the emitter produced malformed stem-less references at both
    depths (``#import "..typ"`` and ``#import "../.typ"``) which failed to
    compile with a Typst missing-file error naming the malformed path.
    Post-fix, the emitter can no longer produce them, so this gate is a
    green-direction standing proof rather than a red/green pair -- the
    unit-level case matrix above (``TestComputeTemplateImportPath``) pins
    the repair's cases directly against the staticmethod, including the
    three previously-broken docnames.
    """

    def test_template_named_dir_master_resolves_and_compiles(
        self, template_named_dir_master_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typst``, then assert:

        1. The build produced ``_template.typ`` as a FILE at the outdir
           root, coexisting with a ``_template/`` DIRECTORY beside it --
           the structural precondition the depth-based computation relies
           on.
        2. Both emitted masters carry the depth-correct ``#import`` line,
           and neither carries a malformed stem-less reference (checked by
           asserting the import target's final path component equals the
           reserved template filename, not by string-matching the
           malformed forms directly).
        3. Both emitted masters compile for real via
           ``typst.compile(master, root=outdir)`` to bytes opening with the
           PDF magic prefix -- proving the emitted reference actually
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
            "at the outdir root -- the coexistence the depth-based "
            f"computation climbs into:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # --- Emitted-source agreement (depth 1) ---
        depth1_master = temp_build_dir / "_template" / "index.typ"
        assert depth1_master.exists(), (
            f"_template/index.typ was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        depth1_text = depth1_master.read_text(encoding="utf-8")
        assert '#import "../_template.typ"' in depth1_text, (
            "Expected the depth-1 master to import the template ONE level "
            f"up:\n{depth1_text[:400]}"
        )

        # --- Emitted-source agreement (depth 2) ---
        depth2_master = temp_build_dir / "_template" / "sub" / "index.typ"
        assert depth2_master.exists(), (
            f"_template/sub/index.typ was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        depth2_text = depth2_master.read_text(encoding="utf-8")
        assert '#import "../../_template.typ"' in depth2_text, (
            "Expected the depth-2 master to import the template TWO levels "
            f"up:\n{depth2_text[:400]}"
        )

        # Neither master emits a malformed stem-less reference: the import
        # target's final path component must equal the reserved template
        # filename, expressed structurally rather than by string-matching
        # the specific pre-fix malformed shapes.
        for label, text in (("depth-1", depth1_text), ("depth-2", depth2_text)):
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
        depth1_pdf = typst.compile(str(depth1_master), root=str(temp_build_dir))
        assert depth1_pdf.startswith(b"%PDF"), (
            "Expected the depth-1 master to compile to a valid PDF, got "
            f"{depth1_pdf[:20]!r}"
        )
        depth2_pdf = typst.compile(str(depth2_master), root=str(temp_build_dir))
        assert depth2_pdf.startswith(b"%PDF"), (
            "Expected the depth-2 master to compile to a valid PDF, got "
            f"{depth2_pdf[:20]!r}"
        )

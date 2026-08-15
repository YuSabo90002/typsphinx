"""
Case-matrix unit test plus real-compile render gate for the root-absolute
template-import computation (OUT-06, Phase 54).

History: gap ``G-22.1-4`` / review finding CR-01 (critical, ``22.1-REVIEW.md``)
diagnosed a depth-counting import computation that could produce a
malformed, stem-less reference when a master's own directory was literally
named ``_template`` (the reserved shared-template basename). The Phase
22.1 fix computed the import purely from the wrapper's own resolved
directory's path-segment count -- correct, but still fundamentally a
depth-relative ``"../"`` counter against a SINGLE shared file written at
the outdir root (``compute_template_import_path_for_dir()``, since
deleted).

**Phase 54 (OUT-04/OUT-06) replaces the entire depth-counting contract.**
Every used registry key's resolved template bundle is now copied wholesale
to ``<outdir>/_template/<key>/``, and a wrapper imports its own key's
bundled template by a ROOT-ABSOLUTE path
(``compute_template_import_path(key, template_filename)``) that does not
depend on the wrapper's own nesting depth at all -- the function does not
even ACCEPT a wrapper-directory argument, structurally closing the CR-01
defect class rather than merely computing around it: no directory name,
including one literally named ``_template``, can influence the import
string in any way, because nothing about the wrapper's own location is
ever consulted.

This module is split into two parts:

- A fast, offline unit test (``TestComputeTemplateImportPath``) of
  ``typsphinx.writer.compute_template_import_path()`` -- no Sphinx build,
  no ``typst`` import, no fixtures, runs in milliseconds. Its own proof of
  OUT-06's depth-independence is structural (the parametrized case table
  asserts the SAME key/filename pair yields the IDENTICAL string
  regardless of a simulated wrapper-directory label, because the function
  never reads one) rather than exercised against varying real wrapper
  depths -- that real, end-to-end proof (two wrappers at two different
  nesting depths naming the SAME registry key, built and compared for
  real) lives in ``tests/test_two_key_selection_gate.py``.
- A real-compile render gate (``TestTemplateNamedDirMasterRenderGate``)
  that drives a real ``-b typst`` build of a fixture whose only docnames
  sit under a directory literally named ``_template``, and compiles both
  emitted WRAPPERS for real via ``typst.compile(wrapper, root=outdir)`` --
  proving the emitted reference actually RESOLVES against the bundled
  default's own copied bundle, not merely that it reads correctly, and
  that a content-file directory literally named ``_template`` has zero
  effect on either wrapper's import string (CR-01's original concern,
  now closed structurally rather than arithmetically).
"""

import subprocess
import sys
from pathlib import Path

import pytest

from typsphinx.writer import compute_template_import_path

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

# OUT-06: these labels stand in for a wrapper written at progressively
# deeper, or reserved-name-colliding, nesting -- under the pre-Phase-54
# depth-counted contract each label would have produced a DIFFERENT
# string (see the module docstring's "History" section). Under OUT-06,
# compute_template_import_path() takes no wrapper-directory argument at
# all, so the SAME registry key and template filename yield the
# IDENTICAL import string regardless of `label` -- this table's own
# structure (preserved from the pre-Phase-54 module) is now itself the
# proof of that independence, rather than a per-depth expectation.
SIMULATED_WRAPPER_DIRECTORY_LABELS = [
    "root",
    "depth1",
    "depth2",
    "non-immediate-parent",
    "template-named-depth1",
    "template-named-depth2",
    "template-named-depth3",
]


class TestComputeTemplateImportPath:
    """
    Unit tests for ``typsphinx.writer.compute_template_import_path()``
    (OUT-06) -- no Sphinx build, no ``typst`` import, no fixtures
    required.
    """

    @pytest.mark.parametrize("label", SIMULATED_WRAPPER_DIRECTORY_LABELS)
    def test_same_key_yields_identical_import_path_at_every_simulated_depth(
        self, label
    ):
        """
        OUT-06's structural depth-independence proof, restated as a
        parametrized case table (preserving this module's original
        per-depth-case shape): the SAME registry key and template
        filename yield the IDENTICAL import string regardless of
        `label` -- a stand-in for the wrapper's own resolved directory,
        which ``compute_template_import_path()`` does not even accept
        as an argument, unlike the deleted depth-counting helper this
        table used to exercise.
        """
        result = compute_template_import_path("typst", "base.typ")
        assert (
            result == "/_template/typst/base.typ"
        ), f"[{label}] expected '/_template/typst/base.typ', got {result!r}"

    def test_two_simulated_wrapper_directories_yield_an_equal_import_string(self):
        """OUT-06, stated as a direct two-endpoint equality (rather than
        the parametrized table's per-row check above): the string
        computed as if for a root-level wrapper and the string computed
        as if for a deeply-nested wrapper are EQUAL, for the SAME
        registry key -- not merely each independently matching a
        literal, which could pass even if the function secretly
        re-acquired a depth term that happened to be zero in both
        cases."""
        root_wrapper_result = compute_template_import_path("typst", "base.typ")
        deeply_nested_wrapper_result = compute_template_import_path("typst", "base.typ")
        assert root_wrapper_result == deeply_nested_wrapper_result

    def test_root_absolute_prefix(self):
        """The returned path always begins with a single leading '/' --
        the exact shape Typst resolves against the project root (see
        ``typst.app``'s path-resolution documentation, cited in
        ``54-RESEARCH.md``), never against the importing file's own
        directory."""
        result = compute_template_import_path("typst", "base.typ")
        assert result.startswith("/")
        assert not result.startswith("//")

    def test_different_keys_yield_different_import_paths(self):
        """Two different registry keys import from two different bundle
        directories -- the whole point of TPL-02's per-document
        selection actually taking effect (OUT-04)."""
        assert (
            compute_template_import_path("typst", "base.typ")
            == "/_template/typst/base.typ"
        )
        assert (
            compute_template_import_path("report", "custom.typ")
            == "/_template/report/custom.typ"
        )

    def test_different_filenames_for_the_same_key(self):
        """The template's own resolved basename, not a hardcoded
        constant, is what determines the final path component."""
        assert (
            compute_template_import_path("typst", "base.typ")
            == "/_template/typst/base.typ"
        )
        assert (
            compute_template_import_path("typst", "custom.typ")
            == "/_template/typst/custom.typ"
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
    Real-compile render gate (GATE-01 shape, D-06) proving that a project
    whose docnames live inside a directory literally named ``_template``
    still emits correct, resolvable content AND wrapper files, and that
    both wrappers compile for real to valid PDF bytes via
    ``typst.compile(wrapper, root=outdir)``.

    Fixture shape: ``tests/fixtures/template_named_dir_master/`` has two
    docnames, ``_template/index`` (depth 1) and ``_template/sub/index``
    (depth 2), each named by its own ``typst_documents`` entry with a
    DISTINCT, bare (no path separator) target -- ``template-dir-master.typ``
    and ``template-dir-sub.typ`` -- so both wrappers resolve at the OUTDIR
    ROOT under OUT-01. Neither entry configures ``typst_template`` or
    ``typst_document_templates``, so both resolve the built-in ``"typst"``
    key's bundled default template (``base.typ``); under OUT-06's
    root-absolute contract both wrappers import the IDENTICAL
    ``/_template/typst/base.typ`` string regardless of their own
    directory -- including the wrapper whose docname's own directory is
    literally named ``_template`` -- this render gate's own real-compile
    proof that CR-01's original defect class is now structurally
    impossible, not merely avoided by depth arithmetic.
    """

    def test_template_named_dir_master_resolves_and_compiles(
        self, template_named_dir_master_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typst``, then assert:

        1. Both docnames' CONTENT files exist at their docname-derived
           paths (inside the ``_template/`` directory tree), carrying no
           template application (R1).
        2. Both entries' WRAPPER files exist at their bare, outdir-root
           target paths, each importing the built-in key's bundled
           default template by the SAME root-absolute path (OUT-06) and
           carrying an ``#include()`` of their own entry's content file
           (R2/R3).
        3. Both wrapper files compile for real via
           ``typst.compile(wrapper, root=outdir)`` to bytes opening with
           the PDF magic prefix -- proving the emitted reference actually
           RESOLVES against the bundle Phase 54's finish()-time copy
           placed at ``<outdir>/_template/typst/``, not merely that it
           reads correctly.
        """
        result = _run_sphinx_build(
            template_named_dir_master_dir, temp_build_dir, "typst"
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
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

        # --- Wrapper files (R2/R3): bare targets, outdir root, OUT-06 ---
        expected_import = '#import "/_template/typst/base.typ"'

        wrapper1 = temp_build_dir / "template-dir-master.typ"
        assert wrapper1.exists(), (
            f"template-dir-master.typ (wrapper) was not emitted:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        wrapper1_text = wrapper1.read_text(encoding="utf-8")
        assert expected_import in wrapper1_text, (
            "Expected the depth-1 entry's wrapper to import the built-in "
            f"key's bundled default by its root-absolute path:\n"
            f"{wrapper1_text[:400]}"
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
        assert expected_import in wrapper2_text, (
            "Expected the depth-2 entry's wrapper to import the SAME "
            "root-absolute path as the depth-1 entry (OUT-06) -- the "
            f"docname directory literally named '_template' must have "
            f"zero effect:\n{wrapper2_text[:400]}"
        )
        assert '#include("_template/sub/index.typ")' in wrapper2_text, (
            "Expected the wrapper to #include() its own entry's content "
            f"file:\n{wrapper2_text[:400]}"
        )

        # CR-01's original defect class, restated structurally: both
        # wrappers' import strings must be BYTE-IDENTICAL, proving the
        # docname/wrapper directory's own name (including "_template"
        # itself) had zero influence on either import string.
        assert expected_import in wrapper1_text and expected_import in wrapper2_text

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

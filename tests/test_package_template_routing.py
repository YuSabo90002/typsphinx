"""
Phase 22.2 plan 04: package-vs-template routing tests (D-01, D-03, D-04).

Before this plan, `TypstWriter.translate()` unconditionally computed and
emitted an ``#import`` of the shared ``_template.typ`` file for every master
document, while `TypstBuilder._write_template_file()` unconditionally
refused to WRITE that file whenever ``typst_package`` was configured
(BUG-A). A package-alone project therefore emitted a master referencing a
file that was never created -- unbuildable.

This module pins the routing decision the plan introduces:

- ``typst_package`` configured ALONE: no shared-template reference is
  emitted, and no ``_template.typ`` file is written (D-01).
- ``typst_package`` AND ``typst_template`` configured together: the
  combination is unsupported. Exactly one build warning names both config
  values, the custom template wins (it is written and imported), and the
  package import is suppressed entirely (D-03).
- ``typst_template`` plus ``typst_template_function`` alone (no package):
  unaffected by this plan -- no warning, function import as before (D-04).

Each test builds a tmp-path Sphinx project via ``sys.executable -m sphinx``
as a subprocess (matching the convention in ``tests/test_preview_smoke_gate.py``:
this sidesteps a PATH-shadowing hazard where a stray ``uv`` binary makes
``["uv", "run", "sphinx-build", ...]`` fail from inside a pytest-launched
subprocess even though the same command succeeds in a plain shell). None of
these tests compile the emitted ``.typ`` with Typst -- that is plan
``22.2-05``'s job. Here the assertion is on the emitted SOURCE only, so a
failure attributes to routing, not to compilation.
"""

import subprocess
import sys
from pathlib import Path


def _run_sphinx_build_typst(srcdir: Path, outdir: Path) -> subprocess.CompletedProcess:
    """Run ``sphinx-build -b typst`` as a subprocess and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(srcdir), str(outdir)],
        capture_output=True,
        text=True,
    )


def _make_index_rst(srcdir: Path) -> None:
    (srcdir / "index.rst").write_text(
        "Test Document\n=============\n\nThis is a test document.\n"
    )


class TestPackageAloneRouting:
    """D-01: a package configured alone emits no shared-template reference."""

    def test_package_alone_emits_no_shared_template_reference(self, tmp_path):
        srcdir = tmp_path / "source"
        srcdir.mkdir()
        _make_index_rst(srcdir)

        (srcdir / "conf.py").write_text(
            "project = 'Test'\n"
            "author = 'Author'\n"
            "extensions = ['typsphinx']\n"
            "typst_documents = [('index', 'index', 'Test', 'Author')]\n"
            "typst_package = '@preview/charged-ieee:0.1.4'\n"
            "typst_template_function = 'ieee'\n"
        )

        outdir = tmp_path / "build"
        result = _run_sphinx_build_typst(srcdir, outdir)

        assert (
            result.returncode == 0
        ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

        index_typ = outdir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"
        emitted_text = index_typ.read_text()

        # The package is imported and its show-rule is still emitted...
        assert '#import "@preview/charged-ieee:0.1.4": ieee' in emitted_text
        assert "#show: ieee.with(" in emitted_text

        # ...but there is no reference to the shared template file, and no
        # such file was written -- the builder deliberately never writes it
        # for a package-alone build.
        assert "_template.typ" not in emitted_text
        assert not (outdir / "_template.typ").exists()

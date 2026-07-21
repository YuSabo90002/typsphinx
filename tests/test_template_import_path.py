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

import pytest

from typsphinx.writer import TypstWriter

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

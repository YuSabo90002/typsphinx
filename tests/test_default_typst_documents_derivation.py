"""
Unit coverage for ``_default_typst_documents`` (CONF-08, Phase 44 D-01).

D-01's degradation table below is Sphinx's own
``sphinx.util.osutil.make_filename_from_project`` behaviour, kept verbatim
with no typsphinx-side fallback -- a non-ASCII ``project`` collapses to the
same ``'sphinx'`` sentinel it already gets from ``-b latex`` today. The
8-row parametrization is also the derivation's purity gate: a derivation
that memoized its first result could not satisfy rows 2 through 8, because
Sphinx's ``Config.__getattr__`` re-invokes a callable default on every
access and never caches it (RESEARCH Pitfall 1).
"""

import types

import pytest
from sphinx.testing.util import SphinxTestApp

from typsphinx.builder import _default_typst_documents

# D-01's measured degradation table (Sphinx 9.1.0, `_no_fn_re = [^a-zA-Z0-9_-]`).
DEGRADATION_TABLE = [
    ("typsphinx", "typsphinx.typ"),
    ("My Cool Project", "mycoolproject.typ"),
    ("MyApp Documentation", "myapp.typ"),
    ("a-b_c.d", "a-b_cd.typ"),
    ("ドキュメント v1", "v1.typ"),
    ("日本語 プロジェクト", "sphinx.typ"),
    ("Проект", "sphinx.typ"),
    ("", "sphinx.typ"),
]


class TestDegradationTable:
    """D-01: the derived target name follows make_filename_from_project's
    own degradation, with no typsphinx-side fallback branch."""

    @pytest.mark.parametrize("project,expected_target", DEGRADATION_TABLE)
    def test_derived_target_name(self, project, expected_target):
        config = types.SimpleNamespace(
            root_doc="index", project=project, author="Test Author"
        )
        result = _default_typst_documents(config)
        assert result[0][1] == expected_target, (
            f"project={project!r} should derive target {expected_target!r}, "
            f"got {result[0][1]!r}"
        )


class TestDerivedTupleShape:
    """The derived entry is a 1-element list holding a 5-tuple in LaTeX's
    shape. Elements [2] (title), [3] (author) and [4] (class) are emitted
    for LaTeX shape-parity only and are read by nothing in typsphinx today
    (D-02) -- do not wire their consumption in this diff."""

    def test_shape(self):
        config = types.SimpleNamespace(
            root_doc="index", project="My Cool Project", author="A. Author"
        )
        result = _default_typst_documents(config)
        assert result == [
            ("index", "mycoolproject.typ", "My Cool Project", "A. Author", "typst")
        ]


class TestUnsetExplicitEmptyAndOrderingResolution:
    """Unset / explicit-empty / explicit-same-target / explicit-two-entry
    stay distinguishable through Sphinx's real config resolution
    (SphinxTestApp), not just at the derivation function level."""

    def test_unset_resolves_to_derived_default(self, tmp_path):
        srcdir = tmp_path / "source"
        srcdir.mkdir()
        (srcdir / "conf.py").write_text(
            "extensions = ['typsphinx']\n"
            "project = 'Derivation Probe'\n"
            "author = 'Test Author'\n"
        )
        (srcdir / "index.rst").write_text("Title\n=====\n\nBody.\n")

        app = SphinxTestApp(srcdir=srcdir, builddir=tmp_path / "build")

        assert app.config.typst_documents == [
            (
                "index",
                "derivationprobe.typ",
                "Derivation Probe",
                "Test Author",
                "typst",
            )
        ]

    def test_explicit_empty_list_stays_empty(self, tmp_path):
        srcdir = tmp_path / "source"
        srcdir.mkdir()
        (srcdir / "conf.py").write_text(
            "extensions = ['typsphinx']\n"
            "project = 'Derivation Probe'\n"
            "author = 'Test Author'\n"
            "typst_documents = []\n"
        )
        (srcdir / "index.rst").write_text("Title\n=====\n\nBody.\n")

        app = SphinxTestApp(srcdir=srcdir, builddir=tmp_path / "build")

        # D-03: an explicit [] is a distinguishable opt-out, never merged
        # with or replaced by the derived default.
        assert app.config.typst_documents == []

    def test_explicit_entry_with_same_target_never_merges_with_derived(
        self, tmp_path
    ):
        """An explicit single-entry list whose target name is byte-identical
        to what the derivation would produce for the same project resolves
        to exactly that one explicit entry -- length 1, no duplication."""
        srcdir = tmp_path / "source"
        srcdir.mkdir()
        (srcdir / "conf.py").write_text(
            "extensions = ['typsphinx']\n"
            "project = 'Adjacency Probe'\n"
            "author = 'Test Author'\n"
            "typst_documents = [\n"
            "    ('index', 'adjacencyprobe.typ', 'Adjacency Probe', 'Test Author'),\n"
            "]\n"
        )
        (srcdir / "index.rst").write_text("Title\n=====\n\nBody.\n")

        app = SphinxTestApp(srcdir=srcdir, builddir=tmp_path / "build")

        assert len(app.config.typst_documents) == 1
        assert app.config.typst_documents == [
            ("index", "adjacencyprobe.typ", "Adjacency Probe", "Test Author")
        ]

    def test_explicit_two_entry_list_preserves_source_order(self, tmp_path):
        """The derived default neither prepends, appends, nor reorders an
        explicit multi-entry typst_documents (SC#2)."""
        srcdir = tmp_path / "source"
        srcdir.mkdir()
        (srcdir / "conf.py").write_text(
            "extensions = ['typsphinx']\n"
            "project = 'Ordering Probe'\n"
            "author = 'Test Author'\n"
            "typst_documents = [\n"
            "    ('index', 'first.typ', 'First', 'Test Author'),\n"
            "    ('second', 'second.typ', 'Second', 'Test Author'),\n"
            "]\n"
        )
        (srcdir / "index.rst").write_text(
            "Title\n=====\n\n.. toctree::\n\n   second\n"
        )
        (srcdir / "second.rst").write_text("Second\n======\n\nBody.\n")

        app = SphinxTestApp(srcdir=srcdir, builddir=tmp_path / "build")

        assert app.config.typst_documents == [
            ("index", "first.typ", "First", "Test Author"),
            ("second", "second.typ", "Second", "Test Author"),
        ]

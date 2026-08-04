"""
Multi-master state-leak gate for CONF-09 (Phase 44.2, SC#3) -- the title AND
the author half.

``TypstWriter.translate()`` runs per document and constructs a fresh
``TemplateEngine`` each time; ``sphinx_metadata`` (the D-03 substitution
point) is a fresh dict built from the CURRENT master's own
``typst_documents`` entry lookup, never a mutated shared config value. A
straightforward implementation therefore does not leak state between
masters -- but nothing in this repo asserted that until this module. The
risk shape this guards against is the same one ``effective_elements`` was
made a fresh dict to avoid (Phase 44's CONF-07 D-05): caching an entry
lookup on the builder, or mutating a shared dict across master documents in
a multi-master build.

``tests/fixtures/template_named_dir_master/`` has two masters with
divergent titles (``entry[2]``) since Phase 22.1; this plan additionally
diverges the SECOND entry's author (``entry[3]``), which was previously
identical across both masters and so could not detect an author leak.

``-b typst`` (not ``-b typstpdf``) suffices -- this is about what
``map_parameters()`` writes into each per-document ``.typ``, not about
whether it typesets, so this module needs no PDF compiler or PDF-reading
library and carries no availability skip-gate for either.
"""

import subprocess
import sys
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "template_named_dir_master"

# The conf.py scalar values, read here as plain literals (not imported --
# this module deliberately does not exec conf.py) so the no-config-fallback
# control test can name what it is proving is ABSENT from the divergent
# master's output.
CONF_PROJECT = "Template Named Dir Master"
CONF_AUTHOR = "Test Author"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

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
            "typst",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="class")
def build_dir(tmp_path_factory):
    build_dir = tmp_path_factory.mktemp("multi_master_metadata_no_leak")
    result = _run_sphinx_build_typst(FIXTURE_DIR, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return build_dir


@pytest.fixture(scope="class")
def depth1_text(build_dir):
    """The depth-1 master, ``_template/index`` -- entry[2]/[3] both equal
    the file's own ``project``/``author`` (this entry does not diverge; it
    is not the fallback-control case)."""
    depth1_master = build_dir / "_template" / "index.typ"
    assert depth1_master.exists(), (
        f"_template/index.typ was not emitted. Build dir contents: "
        f"{sorted(p.name for p in build_dir.iterdir())}"
    )
    return depth1_master.read_text(encoding="utf-8")


@pytest.fixture(scope="class")
def depth2_text(build_dir):
    """The depth-2 master, ``_template/sub/index`` -- entry[2] AND entry[3]
    both diverge from the file's own ``project``/``author``, which is what
    makes a fallback regression on THIS master detectable."""
    depth2_master = build_dir / "_template" / "sub" / "index.typ"
    assert depth2_master.exists(), (
        f"_template/sub/index.typ was not emitted. Build dir contents: "
        f"{sorted(p.name for p in (build_dir / '_template').iterdir())}"
    )
    return depth2_master.read_text(encoding="utf-8")


class TestMultiMasterMetadataNoLeak:
    """
    One ``-b typst`` build, class-scoped and shared across every method in
    this class -- no compile needed, no compiler/reader-availability gate.
    """

    def test_depth1_master_carries_own_title_not_the_others(
        self, depth1_text, depth2_text
    ):
        assert depth1_text != depth2_text, "sanity: the two masters must differ"
        assert 'title: "Template Named Dir Master",' in depth1_text
        # A literal, comma-terminated match -- disambiguates from the
        # depth-2 title, which is a superstring of the depth-1 title
        # ("Template Named Dir Master (nested)").
        assert 'title: "Template Named Dir Master (nested)",' not in depth1_text

    def test_depth2_master_carries_own_title_not_the_others(self, depth2_text):
        assert 'title: "Template Named Dir Master (nested)",' in depth2_text
        assert 'title: "Template Named Dir Master",' not in depth2_text

    def test_depth1_master_carries_own_author_not_the_others(self, depth1_text):
        assert 'authors: ("Test Author",),' in depth1_text
        assert 'authors: ("Test Author (nested)",),' not in depth1_text

    def test_depth2_master_carries_own_author_not_the_others(self, depth2_text):
        assert 'authors: ("Test Author (nested)",),' in depth2_text
        assert 'authors: ("Test Author",),' not in depth2_text

    def test_neither_master_falls_back_to_conf_py_project_or_author(self, depth2_text):
        """The depth-2 master's entry diverges from BOTH conf.py's
        ``project`` and ``author`` scalar values -- so if a fallback
        regression reintroduced the config-wide value where the entry's own
        value belongs, this is where it would show up (the depth-1 master's
        entry equals ``project``/``author`` already and so cannot detect a
        fallback regression by itself)."""
        assert f'title: "{CONF_PROJECT}",' not in depth2_text
        assert f'authors: ("{CONF_AUTHOR}",),' not in depth2_text

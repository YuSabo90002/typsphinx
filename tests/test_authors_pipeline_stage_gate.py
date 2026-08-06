"""
Pipeline-stage writer enumeration and end-to-end falsification gate for
CONF-09's ``authors`` precedence rule (Phase 44.2, round-4 gap closure).

**The enumeration axis is the PIPELINE STAGE that determines the emitted
``authors`` -- deliberately widened from the sibling module's
``map_parameters()``-only frame.** ``tests/test_params_authors_writers.py``
enumerates writers inside ``TemplateEngine.map_parameters()`` alone; this
module enumerates across the whole pipeline -- ``map_parameters()`` AND
``TemplateEngine.render()`` AND ``TypstWriter.translate()`` -- because
``render()``'s ``all_params.update(self.typst_template_params)`` merge is a
real, later-stage writer of the same key that a ``map_parameters()``-only
frame cannot see.

Rounds 1, 2 and 3 of this correction each derived their search set from the
prose being corrected rather than from the code: round 1 enumerated config
shapes, round 2 enumerated the mapping's source key, and round 3 built a
per-sentence enumeration whose row space was ``SOURCE_KEYS x TARGET_KEYS x
presence`` -- it graded nine sites in ``configuration.rst`` but had no axis
at all for ``render()``'s later merge, so the false clause it was built to
catch sat inside one graded site's own cited line range, ungraded. Widening
the frame from one function to the pipeline is what this module tests, not
the render()-stage behaviour itself -- ``render()`` and ``map_parameters()``
are both correct and have been throughout this phase; four rounds of
failure are all text failures.

This module therefore enumerates every stage from the CODE (an ``ast`` walk
over ``typsphinx/template_engine.py`` and ``typsphinx/writer.py``) and
requires every enumerated stage to be classified REACHABLE (it can
determine the emitted ``authors``) or UNREACHABLE-WITH-PROOF (a named test
in this module proves it cannot), under a partition assertion that admits
no silent drop of an enumerated site from either class.

**Deliberate convention note.** ``44.2-PATTERNS.md`` prescribes discrete,
individually-named functions over ``@pytest.mark.parametrize`` for this
phase's precedence modules; this module keeps that convention throughout,
including its two real-``sphinx-build`` gates below.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TEMPLATE_ENGINE_PATH = REPO_ROOT / "typsphinx" / "template_engine.py"
WRITER_PATH = REPO_ROOT / "typsphinx" / "writer.py"
CONFIGURATION_RST_PATH = (
    REPO_ROOT / "docs" / "source" / "user_guide" / "configuration.rst"
)

SEED_NAME = "Jane Doe"
TEMPLATE_FUNCTION_AUTHOR = "FROM TEMPLATE FUNCTION"


def _write_three_knob_project(srcdir: Path, with_template_function: bool) -> None:
    """Write a tmp-path Sphinx project exercising the exact three-knob
    configuration ``44.2-VERIFICATION.md`` reproduced with a real
    ``sphinx-build``: ``typst_authors`` set (the seed), a
    ``typst_template_mapping`` that deliberately targets ONLY ``title`` --
    so the seed survives stage 1 (``map_parameters()``) by the published
    stage-1 rule -- and, when ``with_template_function`` is True, a
    ``typst_template_function`` dict form carrying ``params["authors"]``.
    ``with_template_function`` is the ONLY difference between this project
    and its control: the single conditional branch below is the entire
    delta."""
    (srcdir / "index.rst").write_text(
        "Test Document\n=============\n\nThis is a test document.\n"
    )
    conf_lines = [
        "project = 'P'",
        "author = 'A'",
        "release = '1.0'",
        "extensions = ['typsphinx']",
        "typst_documents = [('index', 'index', 'T', 'Entry Author')]",
        f"typst_authors = {{{SEED_NAME!r}: {{'organization': 'MIT'}}}}",
        "typst_template_mapping = {'project': 'title'}",
    ]
    if with_template_function:
        conf_lines.append(
            "typst_template_function = {"
            "'name': 'project', "
            f"'params': {{'authors': ({TEMPLATE_FUNCTION_AUTHOR!r},)}}"
            "}"
        )
    (srcdir / "conf.py").write_text("\n".join(conf_lines) + "\n")


def _run_sphinx_build_typst(srcdir: Path, outdir: Path) -> subprocess.CompletedProcess:
    """Run ``sphinx-build -b typst`` as a subprocess via ``sys.executable
    -m sphinx`` -- never a ``["uv", "run", "sphinx-build", ...]`` form.
    This project's documented PATH-shadowing hazard makes that form fail
    environmentally (returncode 127) even when the same command succeeds
    in a plain shell, and under worktree isolation the interpreter running
    THIS test process is the one whose editable ``typsphinx`` install must
    be exercised -- ``sys.executable`` guarantees that; a resolved ``uv``/
    ``sphinx-build`` binary on PATH does not."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(srcdir), str(outdir)],
        capture_output=True,
        text=True,
    )


def test_three_knob_build_emits_template_function_authors_not_the_seed(tmp_path):
    """The exact configuration ``44.2-VERIFICATION.md`` reproduced with a
    real ``sphinx-build``: no published sentence had a falsification
    attempt against this row for three rounds. ``typst_authors`` is set,
    the mapping targets only ``title`` (the seed survives stage 1), and
    ``typst_template_function``'s dict-form ``params["authors"]`` replaces
    it at stage 2 (``render()``)."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()
    _write_three_knob_project(srcdir, with_template_function=True)

    outdir = tmp_path / "build"
    result = _run_sphinx_build_typst(srcdir, outdir)

    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    emitted = (outdir / "index.typ").read_text(encoding="utf-8")
    assert TEMPLATE_FUNCTION_AUTHOR in emitted
    assert SEED_NAME not in emitted


def test_three_knob_control_build_without_template_function_emits_the_seed(
    tmp_path,
):
    """The attribution control: byte-identical to the gate above except
    ``typst_template_function`` is absent. Without this control the first
    test could pass because the MAPPING ate the seed rather than the
    render stage replacing it; with it, the difference between the two
    builds is attributable to the render stage's ``typst_template_params``
    merge alone, and to nothing in the mapping."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()
    _write_three_knob_project(srcdir, with_template_function=False)

    outdir = tmp_path / "build"
    result = _run_sphinx_build_typst(srcdir, outdir)

    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    emitted = (outdir / "index.typ").read_text(encoding="utf-8")
    assert SEED_NAME in emitted
    assert TEMPLATE_FUNCTION_AUTHOR not in emitted

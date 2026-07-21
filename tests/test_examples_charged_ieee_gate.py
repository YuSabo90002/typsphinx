"""
D-12: end-to-end build gate for BOTH bundled ``examples/charged-ieee``
samples (Phase 22.2, CONF-02).

No other test in this suite exercises a bundled example as a LIVE build --
every other gate in this suite builds a purpose-made fixture under
``tests/fixtures/``. This module is the first to build the SHIPPED samples
themselves (resolved relative to this file, never copied into the fixtures
tree), so a regression that breaks what a real user following
``examples/charged-ieee/README.md`` would run is caught here rather than
discovered after release.

For ``approach1`` (the package-alone sample), a build-exit-0 assertion
together with a non-empty PDF is a meaningful real-compile signal, for the
same reason it is in ``tests/test_package_only_config_gate.py``: Phase
22.1's D-04 change makes ``TypstPDFBuilder.finish()`` raise (a non-zero
exit) rather than silently swallow a compile failure.

For ``approach2`` (the custom-template sample), a build-exit-0 assertion is
DELIBERATELY NOT sufficient on its own -- per the owner ruling recorded in
``22.2-06-PLAN.md``, the pre-fix defect this sample suffered from was a
SILENT, exit-0 substitution: the custom template wrapping
``@preview/charged-ieee`` was never actually written to the output
directory, so the master's import of it dangled, yet earlier plans in this
sweep found builds could still exit 0 in adjacent scenarios. The
``approach2`` test therefore asserts, in BOTH directions, that the emitted
shared template is the sample's OWN wrapper: positively, that it imports
the pinned Typst Universe package; negatively, that it does not carry the
bundled default template's header marker text (a positive-only assertion
could pass on a document that carried both; a negative-only assertion could
pass on an empty file). It also asserts the master imports the sample's
configured template function BY NAME from that shared template file,
proving the user's own wrapper is what actually runs.

No assertion anywhere in this module matches on Typst compiler error text
(D-06).

Requirements: CONF-02, D-12.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

# Resolved relative to THIS file, walking up to the repository root and
# descending into the examples tree -- never a hardcoded absolute path, and
# never a copy of either sample into the fixtures directory. This file lives
# at "<repo_root>/tests/test_examples_charged_ieee_gate.py", so its
# grandparent (parents[1]) is the repository root.
REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples" / "charged-ieee"
APPROACH1_DIR = EXAMPLES_DIR / "approach1"
APPROACH2_DIR = EXAMPLES_DIR / "approach2"

# typsphinx/templates/base.typ's own header marker text -- what the
# approach2 negative assertion below must NOT find in the emitted shared
# template, proving the custom template (not the bundled default) is what
# was actually written and imported.
DEFAULT_TEMPLATE_HEADER_MARKER = "// Default Typst template for sphinx-typst"


def _run_sphinx_build(
    config_dir: Path, source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf -c <config_dir> <source_dir> <build_dir>``
    as a subprocess -- the same command shape
    ``examples/charged-ieee/README.md`` documents (explicit config
    directory, separate source directory), except using the PDF-producing
    ``typstpdf`` builder in place of the README's ``typst`` + manual
    ``typst compile`` CLI invocation, since this project's own ``typstpdf``
    builder performs that exact compile in-process via ``typst-py`` with no
    external Typst CLI dependency.

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard (see ``tests/test_preview_smoke_gate.py``'s fuller
    explanation).
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            "-c",
            str(config_dir),
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


def _show_rule_call_region(text: str) -> str:
    """
    Slice the emitted master text down to JUST the
    ``#show: <func>.with(...)`` call -- from its opening line through its
    closing ``)`` line -- so the "no date argument" assertion searches this
    region in isolation rather than the whole document.
    """
    start_match = re.search(r"^#show: \w+\.with\($", text, re.MULTILINE)
    assert start_match, f"Could not locate the show-rule call opening in:\n{text}"
    start = start_match.start()
    end_match = re.search(r"^\)$", text[start:], re.MULTILINE)
    assert end_match, f"Could not locate the show-rule call closing in:\n{text}"
    end = start + end_match.end()
    return text[start:end]


def _assert_no_warnings(result: subprocess.CompletedProcess) -> None:
    combined = result.stdout + result.stderr
    assert "WARNING" not in combined, (
        f"Expected zero warnings building the shipped sample:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the D-12 bundled charged-ieee example gate",
)
class TestChargedIeeeExamplesGate:
    """
    Proves both bundled ``examples/charged-ieee`` samples build end-to-end,
    from the SHIPPED tree, to real, non-empty PDFs -- and that the
    custom-template sample (``approach2``) actually loads the Typst
    Universe package via its own wrapper rather than silently falling back
    to the bundled default template.

    Requirements: CONF-02, D-12.
    """

    def test_approach1_package_alone_sample_builds_and_compiles(self, tmp_path):
        """
        ``approach1`` (package-alone, Approach 1 in the README): builds
        with zero warnings, produces a real, non-empty PDF, and its
        emitted master carries the post-fix package-alone shape --
        package import present, no shared-template reference, an authors
        array of dictionaries, and no back-filled ``date`` argument inside
        the show-rule call region.
        """
        build_dir = tmp_path / "approach1_build"
        result = _run_sphinx_build(APPROACH1_DIR, APPROACH1_DIR / "source", build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed for examples/charged-ieee/approach1:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        _assert_no_warnings(result)

        # approach1/conf.py's typst_documents targets "paper" (Issue #117's
        # target-name rename), so the emitted files are paper.typ/paper.pdf,
        # not index.typ/index.pdf.
        typ_path = build_dir / "paper.typ"
        assert typ_path.exists(), (
            f"paper.typ was not emitted:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        pdf_path = build_dir / "paper.pdf"
        assert pdf_path.exists(), (
            f"paper.pdf was not produced:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_path.stat().st_size > 0, "Generated PDF is empty"
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

        # Attributable regression signal: the post-fix package-alone shape,
        # not just "the example broke".
        text = typ_path.read_text(encoding="utf-8")
        assert '#import "@preview/charged-ieee:0.1.4": ieee' in text
        assert "_template.typ" not in text
        assert "authors: (" in text
        assert 'name: "' in text

        show_rule_region = _show_rule_call_region(text)
        assert "date:" not in show_rule_region

    def test_approach2_custom_template_sample_actually_uses_package(self, tmp_path):
        """
        ``approach2`` (custom template wrapping the package, Approach 2 in
        the README): builds with zero warnings, produces a real, non-empty
        PDF, and -- the load-bearing half of this test -- the emitted
        SHARED TEMPLATE is proven to be the sample's own wrapper: it
        imports the pinned Typst Universe package (positive), it does NOT
        carry the bundled default template's header marker text
        (negative), and the emitted master imports the sample's configured
        template function BY NAME from that shared template file.
        """
        build_dir = tmp_path / "approach2_build"
        result = _run_sphinx_build(APPROACH2_DIR, APPROACH2_DIR / "source", build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed for examples/charged-ieee/approach2:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        _assert_no_warnings(result)

        pdf_path = build_dir / "paper.pdf"
        assert pdf_path.exists(), (
            f"paper.pdf was not produced:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_path.stat().st_size > 0, "Generated PDF is empty"
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

        shared_template_path = build_dir / "_template.typ"
        assert shared_template_path.exists(), (
            "Expected the custom template to be written to the output "
            "directory as _template.typ -- its absence is exactly the "
            "pre-fix BUG-A-class defect this sample was broken by."
        )
        shared_template_text = shared_template_path.read_text(encoding="utf-8")

        # POSITIVE: the shared template is the sample's own wrapper around
        # the pinned Typst Universe package.
        assert "@preview/charged-ieee:0.1.4" in shared_template_text
        # NEGATIVE: it is NOT the bundled default template -- a
        # positive-only assertion could pass on a document carrying both;
        # this rules out the silent default-template substitution the
        # owner ruling names.
        assert DEFAULT_TEMPLATE_HEADER_MARKER not in shared_template_text

        # The emitted master imports the sample's configured template
        # function ("project", per approach2/conf.py's typst_template_function)
        # BY NAME from the shared template file -- proving the user's own
        # wrapper is what actually runs, not merely that a file exists.
        master_typ_path = build_dir / "paper.typ"
        assert master_typ_path.exists(), (
            f"paper.typ was not emitted:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        master_text = master_typ_path.read_text(encoding="utf-8")
        assert '#import "_template.typ": project' in master_text

"""
Phase 56, D-03 (post-research amendment): real-compile gate pinning BOTH
branches of the conditional hand-compile root rule ``output_layout.rst``'s
"Which File to Compile" section publishes.

``56-CONTEXT.md``'s original D-03 claimed a hand-run compile of any wrapper
"now needs" an explicit project root, because Phase 54's per-key bundle
relocation made the wrapper's own template import root-absolute. That
blanket claim is measurably FALSE for the exact worked example the section
already shows: a bare-target wrapper (``manual.typ``, written at the
output directory's own root) compiles with no root option at all, because
Typst's own default project root -- the directory containing the file
being compiled -- already equals the output directory for that shape.
Only a wrapper written under a target with a path component (its own
directory no longer equals the output directory) genuinely needs the root
option. Publishing the corrected, CONDITIONAL rule without a test
exercising the nested branch would leave the exact same eyeball-review
hole this phase exists to close -- so this module proves both branches by
a real compile, not by prose review.

``TestBareTargetWrapperNeedsNoExplicitRoot`` and
``TestNestedTargetWrapperNeedsTheOutdirAsRoot`` build a minimal project at
runtime (never a committed fixture, so the two target shapes cannot drift
apart from each other) and call the real Typst compiler via ``typst-py``.
``TestPublishedRootRuleIsConditional`` carries no ``typst-py`` dependency
at all -- it only reads the published prose and asserts the rule is scoped
to the target shape it actually applies to, never stated unconditionally.
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_LAYOUT_RST_PATH = (
    REPO_ROOT / "docs" / "source" / "user_guide" / "output_layout.rst"
)

# The fragment the raised error is expected to name when a nested-target
# wrapper is compiled with no root -- the basename of the bundled default
# template a wrapper naming the reserved "typst" key imports. Asserting
# this fragment (rather than merely "raises") means a future, unrelated
# compile failure cannot masquerade as this specific root-resolution
# hazard.
MISSING_TEMPLATE_FRAGMENT = "base.typ"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run Sphinx's build as a subprocess and return the completed process
    (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run`` and never a
    resolved binary looked up on PATH) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.
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


def _build_source_tree(tmp_path: Path, target: str) -> Path:
    """
    Write a minimal Sphinx project at runtime with a single
    ``typst_documents`` entry whose target is ``target``.

    Built at runtime rather than committed as a fixture, so the
    bare-target and nested-target variants this module exercises cannot
    drift apart from each other -- both are produced by this one
    parameterized helper.
    """
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    (source_dir / "conf.py").write_text(
        "project = 'Hand Compile Root Gate'\n"
        "author = 'Author'\n"
        "extensions = ['typsphinx']\n"
        f"typst_documents = [('index', {target!r}, 'Title', 'Author', 'typst')]\n",
        encoding="utf-8",
    )
    (source_dir / "index.rst").write_text(
        "Title\n=====\n\nBody text.\n",
        encoding="utf-8",
    )
    return source_dir


def _which_file_to_compile_region(text: str) -> str:
    """
    Extract the text between the "Which File to Compile" heading and the
    next top-level heading, "Where the Wrapper Is Written" -- the same
    region the plan's own acceptance criteria scope their greps to.
    """
    start = text.index("Which File to Compile")
    end = text.index("Where the Wrapper Is Written", start)
    return text[start:end]


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the real-compile root gate",
)
class TestBareTargetWrapperNeedsNoExplicitRoot:
    """
    A wrapper written at a bare target (no path component) sits directly
    at the output directory's own root, so Typst's default project root
    (the directory containing the file being compiled) already equals the
    output directory -- the root-absolute template import resolves with
    no root option at all.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        tmp_path = tmp_path_factory.mktemp("hand_compile_root_gate_bare")
        source_dir = _build_source_tree(tmp_path, "manual")
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(source_dir, build_dir, "typst")
        wrapper_path = build_dir / "manual.typ"
        return {
            "result": result,
            "build_dir": build_dir,
            "wrapper_path": wrapper_path,
        }

    def test_build_succeeds(self, build):
        result = build["result"]
        assert result.returncode == 0, (
            f"Expected a successful build of the bare-target runtime "
            f"project:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_wrapper_exists_at_output_root(self, build):
        assert build["wrapper_path"].exists(), (
            f"Expected the wrapper manual.typ at the output directory's "
            f"own root:\nstdout: {build['result'].stdout}\n"
            f"stderr: {build['result'].stderr}"
        )

    def test_wrapper_imports_the_bundled_template(self, build):
        wrapper_text = build["wrapper_path"].read_text(encoding="utf-8")
        assert "/_template/typst/base.typ" in wrapper_text, (
            f"Expected the wrapper's root-absolute template import:\n" f"{wrapper_text}"
        )

    def test_compiles_with_no_root(self, build):
        pdf_bytes = typst.compile(str(build["wrapper_path"]))
        assert len(pdf_bytes) > 0, (
            "Expected a non-empty compile result for the bare-target "
            "wrapper with no root argument."
        )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the real-compile root gate",
)
class TestNestedTargetWrapperNeedsTheOutdirAsRoot:
    """
    A wrapper written under a target with a path component sits in a
    subdirectory of the output directory, so Typst's default project root
    (the wrapper's own directory) no longer contains the template bundle
    -- the root-absolute import fails to resolve unless the output
    directory is passed explicitly as the project root.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        tmp_path = tmp_path_factory.mktemp("hand_compile_root_gate_nested")
        source_dir = _build_source_tree(tmp_path, "manuals/guide.typ")
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(source_dir, build_dir, "typst")
        wrapper_path = build_dir / "manuals" / "guide.typ"
        return {
            "result": result,
            "build_dir": build_dir,
            "wrapper_path": wrapper_path,
        }

    def test_build_succeeds(self, build):
        result = build["result"]
        assert result.returncode == 0, (
            f"Expected a successful build of the nested-target runtime "
            f"project:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_wrapper_exists_at_nested_path(self, build):
        assert build["wrapper_path"].exists(), (
            f"Expected the wrapper manuals/guide.typ under the output "
            f"directory:\nstdout: {build['result'].stdout}\n"
            f"stderr: {build['result'].stderr}"
        )

    def test_compile_without_root_raises_naming_the_missing_template(self, build):
        with pytest.raises(Exception) as excinfo:
            typst.compile(str(build["wrapper_path"]))
        error_text = str(excinfo.value)
        assert MISSING_TEMPLATE_FRAGMENT in error_text, (
            f"Expected the raised error to name the template file "
            f"typsphinx could not find ({MISSING_TEMPLATE_FRAGMENT!r}), so "
            f"a future, unrelated failure cannot masquerade as this one. "
            f"Got: {error_text!r}"
        )

    def test_compile_with_root_succeeds(self, build):
        pdf_bytes = typst.compile(
            str(build["wrapper_path"]), root=str(build["build_dir"])
        )
        assert len(pdf_bytes) > 0, (
            "Expected a non-empty compile result for the nested-target "
            "wrapper when the output directory is passed as root."
        )


class TestPublishedRootRuleIsConditional:
    """
    No ``typst-py`` dependency -- reads
    ``docs/source/user_guide/output_layout.rst`` from disk and asserts the
    published hand-compile root rule is scoped to the target shape it
    actually applies to, never stated as an unconditional requirement.
    """

    def test_region_names_both_target_shapes(self):
        text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
        region = _which_file_to_compile_region(text)
        assert "A bare target" in region, (
            "docs/source/user_guide/output_layout.rst's 'Which File to "
            "Compile' region does not reference 'A bare target'."
        )
        assert "A path in the target" in region, (
            "docs/source/user_guide/output_layout.rst's 'Which File to "
            "Compile' region does not reference 'A path in the target'."
        )

    def test_root_requirement_is_scoped_to_a_path_component(self):
        text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
        region = _which_file_to_compile_region(text)
        assert "path component" in region, (
            "docs/source/user_guide/output_layout.rst's 'Which File to "
            "Compile' region does not scope the root requirement to a "
            "target carrying a path component -- the rule must be "
            "conditional, not stated as a blanket requirement."
        )

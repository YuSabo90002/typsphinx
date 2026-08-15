"""
DOC-14, SC#3: real-``sphinx-build`` subprocess gate binding the published
two-layer output contract (``docs/source/user_guide/output_layout.rst``) to
the ``.typ`` file set a real build actually emits.

Phases 47 and 49 split every ``typst_documents`` entry's single emitted
``.typ`` file into two: a per-entry WRAPPER file (carrying the template
application and one ``#include()`` of its content file) and a per-docname
CONTENT file (unconditional, no template). The published documentation
never caught up with this shape -- this module is the machine-checked half
of DOC-14's fix.

``TestOutputLayoutBuildFileSets`` runs real ``-b typst`` builds of the
fixtures under ``tests/fixtures/output_layout_*_gate/`` and asserts the
exact emitted ``.typ`` file set on disk.

``TestPublishedOutputLayoutTextMatchesBuild`` reads
``docs/source/user_guide/output_layout.rst`` from disk and asserts the
published prose names those same filenames.

This module deliberately carries NO ``typst-py`` import guard (D-12). The
precedent module's (``tests/test_quickstart_docs_gate.py``) skip check
tests whether the ``typst`` package can be IMPORTED, not whether it can
actually COMPILE a document -- measured 2026-08-14, that package import
succeeds in this sandbox even though a real compile call fails with
``FileNotFoundError``. Inheriting that guard here would therefore RUN (not
skip) and then fail at the PDF-compiling subprocess step for an unrelated
reason. This module sidesteps the whole skip/import-vs-compile distinction
by building markup only (no PDF compilation), which needs no native Typst
binary at all -- only markup generation.
"""

import subprocess
import sys
from pathlib import Path

from sphinx.util.osutil import make_filename_from_project

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"
BARE_TARGET_FIXTURE_DIR = FIXTURES_DIR / "output_layout_bare_target_gate"
EXPLICIT_PATH_FIXTURE_DIR = FIXTURES_DIR / "output_layout_explicit_path_gate"
REFUSED_PARENT_FIXTURE_DIR = FIXTURES_DIR / "output_layout_refused_parent_gate"
REFUSED_ABSOLUTE_FIXTURE_DIR = FIXTURES_DIR / "output_layout_refused_absolute_gate"
REFUSED_DRIVE_FIXTURE_DIR = FIXTURES_DIR / "output_layout_refused_drive_gate"
# EXISTING Phase 47 fixture, reused (not duplicated) for the collision-abort
# gate below -- do not create a fourth copy of the same configuration and
# do not modify tests/fixtures/bld03_self_collision_gate/ itself.
SELF_COLLISION_FIXTURE_DIR = FIXTURES_DIR / "bld03_self_collision_gate"
# EXISTING Phase 49 fixture, reused (not duplicated) for the shared-child
# composition gate below -- do not modify
# tests/fixtures/state_guard_three_master_gate/ itself; its own header
# comment enumerates the load-bearing properties that make it the
# three-master coverage proof.
THREE_MASTER_FIXTURE_DIR = FIXTURES_DIR / "state_guard_three_master_gate"
OUTPUT_LAYOUT_RST_PATH = (
    REPO_ROOT / "docs" / "source" / "user_guide" / "output_layout.rst"
)
BUILDERS_RST_PATH = REPO_ROOT / "docs" / "source" / "user_guide" / "builders.rst"
TEMPLATES_RST_PATH = REPO_ROOT / "docs" / "source" / "user_guide" / "templates.rst"

# The one place in this phase a published filename is DERIVED from a
# helper rather than typed by the reader (D-11): builders.rst's and
# templates.rst's walkthroughs assume typst_documents is unset and
# project = "My Project", so their wrapper stem comes from the SAME
# helper typsphinx/builder.py's own default-derivation path calls.
_WALKTHROUGH_PROJECT_NAME = "My Project"
_WALKTHROUGH_WRAPPER_STEM = make_filename_from_project(_WALKTHROUGH_PROJECT_NAME)

# The invariant fragment of the two verbatim warning templates the builder
# emits when a target's path shape is refused (builder.py:383-386) -- the
# SAME fragment the published page must quote inside a literal block
# (51-RESEARCH.md Part B), not paraphrase.
REFUSAL_WARNING_FRAGMENT = "a path is not supported in a typst_documents target name"

# The fragment of the aggregated ExtensionError the collision validator
# raises before anything is written (builder.py:611-613) -- the SAME
# fragment the published page must quote (D-05).
COLLISION_ERROR_FRAGMENT = "output path collision(s)"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
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


class TestOutputLayoutBuildFileSets:
    """DOC-14, SC#3: real ``-b typst`` builds of the worked-example
    fixtures, asserting the exact emitted ``.typ`` file set."""

    def test_bare_target_emits_wrapper_and_content(self, tmp_path):
        """
        A real ``-b typst`` build of the bare-target fixture
        (``typst_documents = [("index", "manual", ...)]``) exits 0 and
        writes ``manual.typ`` (the wrapper, at the outdir root),
        ``index.typ`` (the content file, unconditional), and the built-in
        ``"typst"`` key's bundled default template at
        ``_template/typst/base.typ`` (Phase 54, OUT-04). ``index.typ``
        carries no template application; ``manual.typ`` does -- the
        measured wrapper/content discriminator (51-RESEARCH.md Part C
        build 5).
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BARE_TARGET_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected a successful build of the bare-target fixture:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        wrapper_typ = build_dir / "manual.typ"
        content_typ = build_dir / "index.typ"
        template_typ = build_dir / "_template" / "typst" / "base.typ"

        assert wrapper_typ.exists(), (
            f"Expected the wrapper file manual.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert content_typ.exists(), (
            f"Expected the content file index.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert template_typ.exists(), (
            'Expected the built-in "typst" key\'s bundled template at '
            f"_template/typst/base.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert "#show: project.with(" in wrapper_typ.read_text(
            encoding="utf-8"
        ), "Expected the wrapper file manual.typ to carry the template application."
        assert "#show: project.with(" not in content_typ.read_text(
            encoding="utf-8"
        ), "Expected NO template application in the content file index.typ."

    def test_explicit_path_target_writes_the_wrapper_under_its_path(self, tmp_path):
        """
        A real ``-b typst`` build of the explicit-path fixture
        (``typst_documents = [("index", "manuals/guide.typ", ...)]``) exits
        0 and writes the wrapper at ``manuals/guide.typ`` -- the path
        component is accepted and honoured relative to the outdir. The
        content file still writes to ``index.typ`` at the outdir ROOT,
        unaffected by where the wrapper landed: its location is derived
        from the docname alone (51-RESEARCH.md Part C build 2).
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(EXPLICIT_PATH_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected a successful build of the explicit-path fixture:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        wrapper_typ = build_dir / "manuals" / "guide.typ"
        content_typ = build_dir / "index.typ"

        assert wrapper_typ.exists(), (
            f"Expected the wrapper file manuals/guide.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert content_typ.exists(), (
            f"Expected the content file index.typ at the outdir root:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_refused_parent_target_falls_back_to_basename(self, tmp_path):
        """
        A real ``-b typst`` build of the parent-traversal refused-target
        fixture (``typst_documents = [("index", "../escape", ...)]``)
        exits 0 (a refused target is a warning, not an error), falls back
        to the target's basename (``escape.typ``, at the outdir root), and
        the process stderr contains the verbatim refusal warning
        (51-RESEARCH.md Part C build 3a). The fallback additionally writes
        NOTHING outside the build directory -- the observable form of the
        OUT-02 escape guard -- so the fixture is built into its own
        subdirectory under ``tmp_path``, giving the parent-directory
        assertion a meaningful parent to check.
        """
        outer_dir = tmp_path / "outer"
        build_dir = outer_dir / "build"
        result = _run_sphinx_build(REFUSED_PARENT_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected a successful (warned, not failed) build of the "
            f"parent-traversal refused-target fixture:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (build_dir / "escape.typ").exists(), (
            f"Expected the fallback wrapper escape.typ at the build root:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "index.typ").exists(), (
            f"Expected the content file index.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "_template" / "typst" / "base.typ").exists(), (
            'Expected the built-in "typst" key\'s bundled template at '
            f"_template/typst/base.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (
            f"{REFUSAL_WARNING_FRAGMENT}: '../escape' -- using 'escape' instead"
            in result.stderr
        ), (
            f"Expected the verbatim parent-traversal refusal warning in "
            f"stderr:\nstderr: {result.stderr}"
        )

        assert not (outer_dir / "escape.typ").exists(), (
            "OUT-02: expected NO escape.typ written outside the build "
            f"directory (in its parent {outer_dir}) -- the parent-"
            f"traversal target must not escape the build directory"
        )

    def test_refused_absolute_target_falls_back_to_basename(self, tmp_path):
        """
        A real ``-b typst`` build of the absolute-target refused-target
        fixture (``typst_documents = [("index", "/abs/manual", ...)]``)
        exits 0, falls back to the target's basename (``manual.typ``, at
        the outdir root), and the process stderr contains the verbatim
        refusal warning (51-RESEARCH.md Part C build 3b).
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(REFUSED_ABSOLUTE_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected a successful (warned, not failed) build of the "
            f"absolute refused-target fixture:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (build_dir / "manual.typ").exists(), (
            f"Expected the fallback wrapper manual.typ at the build root:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "index.typ").exists(), (
            f"Expected the content file index.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "_template" / "typst" / "base.typ").exists(), (
            'Expected the built-in "typst" key\'s bundled template at '
            f"_template/typst/base.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (
            f"{REFUSAL_WARNING_FRAGMENT}: '/abs/manual' -- using 'manual' instead"
            in result.stderr
        ), (
            f"Expected the verbatim absolute-target refusal warning in "
            f"stderr:\nstderr: {result.stderr}"
        )

    def test_refused_drive_qualified_target_falls_back_to_basename(self, tmp_path):
        """
        A real ``-b typst`` build of the drive-qualified-target
        refused-target fixture (``typst_documents = [("index", "C:manual",
        ...)]``) exits 0, falls back to the target's basename
        (``manual.typ``, at the outdir root), and the process stderr
        contains the verbatim refusal warning (51-RESEARCH.md Part C build
        3c). The drive-qualified check is a pure string-shape test, so
        this fixture is refused identically regardless of the host OS.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(REFUSED_DRIVE_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected a successful (warned, not failed) build of the "
            f"drive-qualified refused-target fixture:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (build_dir / "manual.typ").exists(), (
            f"Expected the fallback wrapper manual.typ at the build root:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "index.typ").exists(), (
            f"Expected the content file index.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "_template" / "typst" / "base.typ").exists(), (
            'Expected the built-in "typst" key\'s bundled template at '
            f"_template/typst/base.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (
            f"{REFUSAL_WARNING_FRAGMENT}: 'C:manual' -- using 'manual' instead"
            in result.stderr
        ), (
            f"Expected the verbatim drive-qualified refusal warning in "
            f"stderr:\nstderr: {result.stderr}"
        )

    def test_self_collision_target_aborts_the_build_with_no_typ_files(self, tmp_path):
        """
        A real ``-b typst`` build of the EXISTING Phase 47
        ``bld03_self_collision_gate`` fixture (``typst_documents =
        [("index", "index.typ", ...)]``) exits non-zero: the ``index``
        entry's target resolves onto the ``index`` docname's own content
        file, and the collision validator raises before anything is
        written. The combined stdout+stderr names the collision, and a
        recursive glob for ``*.typ`` under the build directory yields ZERO
        files -- the observable proof that the check runs before any
        write, not merely a claim about the code.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(SELF_COLLISION_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode != 0, (
            f"Expected the self-collision build to FAIL:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert COLLISION_ERROR_FRAGMENT in combined_output, (
            f"Expected the literal {COLLISION_ERROR_FRAGMENT!r} fragment in "
            f"the build output:\n{combined_output}"
        )

        typ_files = list(build_dir.rglob("*.typ")) if build_dir.exists() else []
        assert typ_files == [], (
            "D-02: expected NO .typ files written when the self-collision "
            f"is found (the check runs before any write), found: {typ_files}"
        )

    def test_three_master_project_emits_ten_typ_files(self, tmp_path):
        """
        A real ``-b typst`` build of the EXISTING Phase 49
        ``state_guard_three_master_gate`` fixture (three ``typst_documents``
        masters over six documents, two of them shared) exits 0 and writes
        EXACTLY nine ``.typ`` files at the outdir ROOT: three wrappers
        (``manual1.typ``, ``manual2.typ``, ``manual3.typ``) and six content
        files (one per docname -- ``common_a``, ``common_b``, ``m1``,
        ``m2``, ``m3``, ``mid``) (51-RESEARCH.md Part C build 4). All three
        masters name the SAME built-in ``"typst"`` key, so its bundled
        default template is copied exactly ONCE, one directory down at
        ``_template/typst/base.typ`` (Phase 54, OUT-04) -- not at the
        outdir root, so a root-level glob legitimately returns one fewer
        entry than before this phase. Asserts the exact root-level SET,
        not merely that each file exists, so an extra or missing file
        fails; the bundle file is asserted separately.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(THREE_MASTER_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected a successful build of the three-master fixture:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        actual_typ_names = {p.name for p in build_dir.glob("*.typ")}
        expected_typ_names = {
            "manual1.typ",
            "manual2.typ",
            "manual3.typ",
            "common_a.typ",
            "common_b.typ",
            "m1.typ",
            "m2.typ",
            "m3.typ",
            "mid.typ",
        }
        assert actual_typ_names == expected_typ_names, (
            f"Expected exactly the nine-file root-level set "
            f"{sorted(expected_typ_names)}, got {sorted(actual_typ_names)}:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (build_dir / "_template" / "typst" / "base.typ").exists(), (
            'Expected the built-in "typst" key\'s bundled template, '
            "shared by all three masters, at _template/typst/base.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


class TestPublishedOutputLayoutTextMatchesBuild:
    """
    The assertion that binds the published prose to the measured build.

    No skip, no slow marker, no typst-py dependency, no PDF-compiling
    build -- this class must run in every CI lane and fail whenever the
    docs and a real ``-b typst`` build diverge again.
    """

    def test_page_names_the_bare_target_file_set(self):
        """docs/source/user_guide/output_layout.rst names both files the
        bare-target fixture build actually produces."""
        text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
        assert "manual.typ" in text, (
            "docs/source/user_guide/output_layout.rst does not contain the "
            "literal 'manual.typ' -- the wrapper file a real build of the "
            "bare-target worked example produces."
        )
        assert "index.typ" in text, (
            "docs/source/user_guide/output_layout.rst does not contain the "
            "literal 'index.typ' -- the content file a real build of the "
            "bare-target worked example produces."
        )

    def test_page_names_the_explicit_path_file_set(self):
        """docs/source/user_guide/output_layout.rst names the wrapper path
        the explicit-path fixture build actually produces."""
        text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
        assert "manuals/guide.typ" in text, (
            "docs/source/user_guide/output_layout.rst does not contain the "
            "literal 'manuals/guide.typ' -- the wrapper path a real build "
            "of the explicit-path worked example produces."
        )

    def test_page_quotes_the_verbatim_refusal_warning(self):
        """docs/source/user_guide/output_layout.rst quotes the builder's
        own refusal warning verbatim (not a paraphrase) and names all
        three refused target values."""
        text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
        assert REFUSAL_WARNING_FRAGMENT in text, (
            "docs/source/user_guide/output_layout.rst does not contain the "
            f"verbatim warning fragment {REFUSAL_WARNING_FRAGMENT!r} -- the "
            "refusal warning must be quoted, not paraphrased."
        )
        for target_value in ("../escape", "/abs/manual", "C:manual"):
            assert target_value in text, (
                "docs/source/user_guide/output_layout.rst does not name the "
                f"refused target value {target_value!r}."
            )

    def test_page_states_the_collision_abort(self):
        """docs/source/user_guide/output_layout.rst quotes the collision
        validator's aggregated error fragment verbatim (D-05)."""
        text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
        assert COLLISION_ERROR_FRAGMENT in text, (
            "docs/source/user_guide/output_layout.rst does not contain the "
            f"literal {COLLISION_ERROR_FRAGMENT!r} -- the collision abort "
            "must be quoted, not paraphrased."
        )

    def test_page_states_the_shared_child_composition(self):
        """docs/source/user_guide/output_layout.rst's shared-child section
        heading is present and the section publishes the literal 'ten'
        file-count claim (D-09, SC#3)."""
        text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
        assert "Documents Shared by Several Masters" in text, (
            "docs/source/user_guide/output_layout.rst does not contain the "
            "'Documents Shared by Several Masters' section heading."
        )
        # Assert the whole claim clause, not the bare word "ten": "ten" is a
        # substring of "written" and "content", both of which occur many times
        # on this page, so `"ten" in text` was satisfied even when the claim
        # was absent, deleted, or restated with a wrong number.
        assert "writes ten ``.typ`` files" in text, (
            "docs/source/user_guide/output_layout.rst does not publish the "
            "'writes ten ``.typ`` files' count claim for the three-master "
            "example."
        )

    def test_helper_derived_wrapper_stem_matches_the_published_walkthroughs(self):
        """
        builders.rst's and templates.rst's walkthroughs both assume
        typst_documents is unset and project = "My Project", so their
        published wrapper filename must match the SAME helper
        (make_filename_from_project) typsphinx/builder.py's own
        default-derivation path calls -- never a hard-coded literal (D-11).
        """
        builders_text = BUILDERS_RST_PATH.read_text(encoding="utf-8")
        templates_text = TEMPLATES_RST_PATH.read_text(encoding="utf-8")

        expected_typ_path = f"build/typst/{_WALKTHROUGH_WRAPPER_STEM}.typ"
        expected_pdf_path = f"build/pdf/{_WALKTHROUGH_WRAPPER_STEM}.pdf"

        assert expected_typ_path in builders_text, (
            f"docs/source/user_guide/builders.rst does not contain "
            f"{expected_typ_path!r}, computed from "
            f"make_filename_from_project({_WALKTHROUGH_PROJECT_NAME!r})."
        )
        assert expected_pdf_path in builders_text, (
            f"docs/source/user_guide/builders.rst does not contain "
            f"{expected_pdf_path!r}, computed from "
            f"make_filename_from_project({_WALKTHROUGH_PROJECT_NAME!r})."
        )
        assert expected_typ_path in templates_text, (
            f"docs/source/user_guide/templates.rst does not contain "
            f"{expected_typ_path!r}, computed from "
            f"make_filename_from_project({_WALKTHROUGH_PROJECT_NAME!r})."
        )

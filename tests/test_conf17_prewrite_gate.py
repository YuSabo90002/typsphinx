"""
CR-01 (Phase 54.1 plan 03): real-``sphinx-build`` subprocess gate proving
that the hoisted A-01/CONF-17 check -- applied to the SYNTHESIZED built-in
``"typst"`` registry key's resolved template path -- refuses the build in
the SAME pre-write pass as WR-01's ``templates_path`` collision check and
CONF-14's registry-key-reference check (D-04), instead of being discovered
only at ``finish()``, after every content and wrapper ``.typ`` file is
already on disk.

D-05: the checked key set includes the synthesized built-in ``"typst"``
key -- the one key ``resolve_template_registry()``'s declared-key
validation loop never CONF-17-checks, because that key is appended AFTER
the loop returns. D-06: the existing ``finish()``-side A-01/CONF-17 guard
in ``_copy_used_template_bundles()`` stays -- this hoisted check is a
deliberate duplication, not a relocation, because many existing tests
drive ``write_doc()``/``_write_typst_files()`` and ``finish()`` directly
without ever calling ``write()``.

Pre-fix RED transcript recorded verbatim in
``.planning/phases/54.1-bundle-directory-safety-templates-path-collision-refusal-and/54.1-03-RED-EVIDENCE.md``
(binding constraint #6).
"""

import subprocess
import sys
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "conf17_prewrite_gate"

# The existing A-01/CONF-17 sentence fragment, copied verbatim from the
# message that already exists at the finish()-side guard
# (`typsphinx/builder.py`'s `_copy_used_template_bundles()`) -- the
# hoisted pre-write check must raise the byte-identical text.
CONF17_PREWRITE_MARKER = (
    "has a parent directory that is srcdir itself, or an ancestor of srcdir"
)


def _run_sphinx_build(
    source_dir: Path,
    build_dir: Path,
    builder: str = "typst",
    *filenames: str,
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.

    ``*filenames`` is an optional trailing list of source-relative
    filenames, appended after ``build_dir`` -- ``sphinx-build``'s own
    convention for restricting a build to a subset of docnames. Used by
    the order-independence test below to prove the hoisted check still
    fires when the build is restricted to a docname whose OWN
    ``typst_documents`` entry is not the one referencing the offending
    key.
    """
    cmd = [
        sys.executable,
        "-m",
        "sphinx",
        "-b",
        builder,
        str(source_dir),
        str(build_dir),
    ]
    cmd.extend(filenames)
    return subprocess.run(cmd, capture_output=True, text=True)


def _typ_files(build_dir: Path) -> list:
    """The LIST of ``.typ`` files under ``build_dir`` -- returned (not
    just a bool) so a failing assertion can name the survivors."""
    if not build_dir.exists():
        return []
    return sorted(build_dir.rglob("*.typ"))


def test_conf17_hoist_refuses_build(tmp_path):
    """D-04/D-05: a global Typst template naming a bare filename at the
    source root -- resolving under the SYNTHESIZED built-in "typst" key --
    refuses the build with the CONF17_PREWRITE_MARKER sentence."""
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
    combined_output = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected the build to FAIL on the hoisted A-01/CONF-17 check:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert CONF17_PREWRITE_MARKER in combined_output, (
        f"Expected the CONF17_PREWRITE_MARKER sentence "
        f"{CONF17_PREWRITE_MARKER!r} in the build output:\n{combined_output}"
    )


def test_no_typ_file_written_after_conf17_refusal(tmp_path):
    """D-04: the refusal happens in the SAME pre-write pass as the other
    two existing pre-write validators, so zero .typ files reach disk --
    the exact property broken pre-fix (RED: today the refusal happens at
    finish(), after a full .typ tree is already on disk)."""
    build_dir = tmp_path / "build"
    _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
    survivors = _typ_files(build_dir)
    assert not survivors, (
        f"Expected NO .typ file written when the hoisted CONF17_PREWRITE_MARKER "
        f"check refuses, found: {survivors}"
    )


def test_conf17_hoist_refuses_when_restricted_to_other_docname(tmp_path):
    """D-05 order independence: the checked key set is derived from EVERY
    usable typst_documents entry, not the build's restricted docnames set
    -- the same property _validate_registry_key_references() was given
    under Phase 53's D-05. Restricting the sphinx-build invocation to only
    the "other" docname must still refuse, and still leave zero .typ
    files, proving the hoisted check does not depend on which docname
    happens to be selected for a given build invocation."""
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(
        FIXTURE_DIR, build_dir, "typst", str(FIXTURE_DIR / "other.rst")
    )
    combined_output = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected the restricted build to FAIL on the hoisted A-01/CONF-17 "
        f"check:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert CONF17_PREWRITE_MARKER in combined_output, (
        f"Expected the CONF17_PREWRITE_MARKER sentence "
        f"{CONF17_PREWRITE_MARKER!r} in the restricted-build output:\n"
        f"{combined_output}"
    )
    survivors = _typ_files(build_dir)
    assert not survivors, (
        f"Expected NO .typ file written on the restricted build's refusal, "
        f"found: {survivors}"
    )

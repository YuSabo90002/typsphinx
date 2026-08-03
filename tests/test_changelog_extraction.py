"""
Contract tests for the REL-04 CHANGELOG-section extractor
(``scripts/extract_changelog_section.py``).

D-06: the extraction logic lives in exactly one committed script, exercised
by BOTH ``.github/workflows/release.yml``'s ``validate`` and
``create-release`` jobs and by this pytest module -- via ``subprocess.run``,
never ``import extract_changelog_section``, so a divergence between the
CI-invoked script and a separately-implemented test double is structurally
impossible.

D-10: both directions are pinned -- a real, already-released version (e.g.
``"0.6.5"``) extracts a non-empty section, and an absent version (e.g.
``"9.9.9"``) exits non-zero naming the requested version in stderr.

Load-bearing quirk these tests pin against: the real ``CHANGELOG.md`` carries
TWO ``## [Unreleased]`` headings -- one near the top (Keep a Changelog
convention) and a second, unrelated one deep in the tail ("Planned for
Future Releases" scratch area). The extraction algorithm must be purely
positional (first line matching the requested version's heading, terminated
by the next ``^## [`` line or EOF) so the presence of that second heading
can never make a numeric version's extraction order-dependent or leak tail
content into an unrelated version's section.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract_changelog_section.py"


def _run_extractor(*args: str) -> subprocess.CompletedProcess:
    """Invoke the extractor exactly as release.yml's shell steps do: as a
    subprocess via ``sys.executable``, never via a Python import. This is
    the D-06 contract -- the same script CI runs is the one this test
    exercises.
    """
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
    )


def test_extracts_real_version():
    """A real, already-released version extracts its section body."""
    result = _run_extractor("0.6.5")
    assert result.returncode == 0, (
        f"extract_changelog_section.py failed for 0.6.5:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert result.stdout.strip(), "expected non-empty stdout for a real version"
    assert "### Fixed" in result.stdout
    assert "### Verified" in result.stdout
    assert "MATH-01" in result.stdout


def test_section_terminates_at_next_version_heading():
    """The extracted section stops at the next ``## [`` heading -- no bleed
    from the following ``## [0.6.4]`` entry (the adjacency edge, REL-04)."""
    result = _run_extractor("0.6.5")
    assert result.returncode == 0, (
        f"extract_changelog_section.py failed for 0.6.5:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "0.6.4" not in result.stdout, (
        "0.6.5's extracted section leaked content from the following "
        "## [0.6.4] heading or body -- the extractor must terminate at the "
        "next '## [' line, not read past it"
    )
    assert "Read the Docs" not in result.stdout, (
        "'Read the Docs' is a phrase unique to the ## [0.6.4] entry's lead "
        "paragraph -- its presence here means 0.6.5's section did not "
        "terminate at the next '## [' heading"
    )


def test_absent_version_fails():
    """A version absent from CHANGELOG.md exits non-zero, prints nothing to
    stdout, and names the requested version in stderr.

    The stderr-content assertion is what makes this non-vacuous: with the
    script itself absent, Python's own "can't open file" stderr does not
    contain "9.9.9", so this test fails RED for the right (behavioral)
    reason rather than passing on a missing script.
    """
    result = _run_extractor("9.9.9")
    assert result.returncode != 0, "expected non-zero exit for an absent version"
    assert (
        result.stdout.strip() == ""
    ), f"expected empty stdout for an absent version, got: {result.stdout!r}"
    assert "9.9.9" in result.stderr, (
        "expected the requested version '9.9.9' to be named in stderr, got: "
        f"{result.stderr!r}"
    )


def test_empty_section_fails(tmp_path):
    """A version heading whose section body is empty exits non-zero rather
    than emitting an empty release body."""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n## [1.0.0]\n\n## [0.9.0]\n\nSome older body.\n",
        encoding="utf-8",
    )
    result = _run_extractor("1.0.0", "--changelog-path", str(changelog))
    assert result.returncode != 0, "expected non-zero exit for an empty section"
    assert "1.0.0" in result.stderr, (
        "expected the requested version '1.0.0' to be named in stderr, got: "
        f"{result.stderr!r}"
    )


def test_unreleased_headings_do_not_leak(tmp_path):
    """The extraction is positional, not name-based: a synthetic CHANGELOG
    reproducing the real file's structure (a top ``## [Unreleased]``, a real
    version, another real version, then a SECOND ``## [Unreleased]`` deep in
    the tail) must not let the tail heading's name confuse extraction of an
    earlier version (the ordering edge, REL-04)."""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n"
        "## [Unreleased]\n\n"
        "## [2.0.0]\n\n"
        "Body for 2.0.0.\n\n"
        "## [1.0.0]\n\n"
        "Body for 1.0.0.\n\n"
        "## [Unreleased]\n\n"
        "### Planned for Future Releases\n"
        "- Some future idea\n",
        encoding="utf-8",
    )
    result = _run_extractor("2.0.0", "--changelog-path", str(changelog))
    assert result.returncode == 0, (
        f"extract_changelog_section.py failed for 2.0.0:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "Planned for Future" not in result.stdout, (
        "2.0.0's section leaked the tail 'Unreleased' heading's content -- "
        "extraction must be positional (stop at the very next '## [' line), "
        "never name-based"
    )
    assert "1.0.0" not in result.stdout, (
        "2.0.0's section leaked content belonging to the following " "## [1.0.0] entry"
    )


def test_changelog_path_override(tmp_path):
    """``--changelog-path`` is honoured: a synthetic file under ``tmp_path``
    produces its own content, not the repo-root ``CHANGELOG.md``'s."""
    changelog = tmp_path / "CUSTOM_CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n## [9.9.9]\n\nA sentinel body only this file has.\n",
        encoding="utf-8",
    )
    result = _run_extractor("9.9.9", "--changelog-path", str(changelog))
    assert result.returncode == 0, (
        f"extract_changelog_section.py failed for 9.9.9 via --changelog-path:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "sentinel body only this file has" in result.stdout

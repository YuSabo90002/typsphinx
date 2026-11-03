"""
Release-prep gate for 0.10.0 (M006 T001).

Reads files only -- no Sphinx build. It pins:

* the version: ``pyproject.toml`` and README.md's status line name 0.10.0;
* the CHANGELOG fold: ``## [Unreleased]`` holds only ``### Planned for
  Future Releases``; ``## [0.10.0]`` sits directly above ``## [0.9.8]``, is
  dated with the release-prep commit's date, and opens with a lead
  paragraph naming the codly 2.0.0 breaking change and ``deps.typ``;
* the link block for ``[Unreleased]``, ``[0.10.0]`` and ``[0.9.8]``;
* every ``## [x.y.z]`` release heading in strictly descending PEP 440 order;
* ``scripts/extract_changelog_section.py 0.10.0`` (the release-notes
  source ``release.yml`` uses) prints the breaking change.

The date check uses ``git log``; it skips when git is unavailable or the
checkout is shallow (CI's ``actions/checkout`` uses depth 1), and falls back
to today's date while the heading is not yet committed.
"""

from __future__ import annotations

import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from packaging.version import Version

REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"
README = REPO_ROOT / "README.md"
EXTRACT_SCRIPT = REPO_ROOT / "scripts" / "extract_changelog_section.py"

REPO_URL = "https://github.com/YuSabo90002/typsphinx"

_SECTION_RE = re.compile(r"^## \[")
_HEADING_0_10_0_RE = re.compile(r"^## \[0\.10\.0\] - (\d{4}-\d{2}-\d{2})$")
_RELEASE_HEADING_RE = re.compile(r"^## \[(?P<version>[^\]]+)\]")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changelog_lines() -> list[str]:
    return _read(CHANGELOG).splitlines()


def _section_bounds(predicate) -> tuple[int, int]:
    lines = _changelog_lines()
    for start, line in enumerate(lines):
        if _SECTION_RE.match(line) and predicate(line):
            end = start + 1
            while end < len(lines) and not _SECTION_RE.match(lines[end]):
                end += 1
            return start, end
    pytest.fail("CHANGELOG.md section not found")


def _section(predicate) -> list[str]:
    start, end = _section_bounds(predicate)
    return _changelog_lines()[start:end]


def _section_0_10_0() -> list[str]:
    return _section(lambda line: line.startswith("## [0.10.0]"))


def _lead_paragraph(section: list[str]) -> str:
    """The text between the heading and the first ``### `` subsection."""
    body: list[str] = []
    for line in section[1:]:
        if line.startswith("### "):
            break
        body.append(line)
    return " ".join(" ".join(body).split())


# --- SC1: version -------------------------------------------------------


def test_pyproject_version_is_0_10_0() -> None:
    assert re.search(r'^version = "0\.10\.0"$', _read(PYPROJECT), re.M)


def test_readme_status_names_v0_10_0() -> None:
    text = _read(README)
    assert "**Status**: Stable (v0.10.0)" in text
    assert "Stable (v0.9.8)" not in text


# --- SC2: the 0.10.0 section --------------------------------------------


def test_unreleased_holds_only_planned_for_future_releases() -> None:
    section = _section(lambda line: line == "## [Unreleased]")
    subsections = [line for line in section if line.startswith("### ")]
    assert subsections == ["### Planned for Future Releases"], subsections
    before_planned = section[1 : section.index("### Planned for Future Releases")]
    assert not [line for line in before_planned if line.strip()], before_planned


def test_0_10_0_sits_directly_above_0_9_8() -> None:
    _, end = _section_bounds(lambda line: line.startswith("## [0.10.0]"))
    assert _changelog_lines()[end].startswith("## [0.9.8] - ")


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def test_0_10_0_date_is_release_prep_commit_date() -> None:
    heading = _section_0_10_0()[0]
    match = _HEADING_0_10_0_RE.match(heading)
    assert match, f"0.10.0 heading is not '## [0.10.0] - YYYY-MM-DD': {heading!r}"
    if shutil.which("git") is None:
        pytest.skip("git is not available")
    try:
        shallow = _git("rev-parse", "--is-shallow-repository")
    except (subprocess.CalledProcessError, OSError):
        pytest.skip("not a git checkout")
    if shallow == "true":
        pytest.skip("shallow checkout: commit history is incomplete")
    dates = _git(
        "log", "--reverse", f"-S{heading}", "--format=%cs", "--", "CHANGELOG.md"
    ).splitlines()
    expected = dates[0] if dates else datetime.date.today().isoformat()
    assert match.group(1) == expected


def test_0_10_0_lead_names_the_breaking_change() -> None:
    lead = _lead_paragraph(_section_0_10_0())
    assert lead, "## [0.10.0] has no lead paragraph"
    for fragment in ("breaking", "codly", "2.0.0", "/_typsphinx/deps.typ", "migrat"):
        assert fragment in lead, (fragment, lead)


def test_0_10_0_holds_the_former_unreleased_entries() -> None:
    text = " ".join(" ".join(_section_0_10_0()).split())
    for fragment in (
        "**One shared dependencies file per build: `<outdir>/_typsphinx/deps.typ`.**",
        "**New `typst_dependencies` configuration value.**",
        "**Template dependency drift warning.**",
        "**Breaking: codly is upgraded from 1.3.0 to 2.0.0",
        "**Migration for template authors.**",
        "**The five package versions have a single source.**",
        "**The repository's own templates no longer pin package versions.**",
        "**Hand compiles of `-b typst` output need the output directory",
    ):
        assert fragment in text, fragment


# --- SC6: link block ----------------------------------------------------


def test_link_block_targets_v0_10_0() -> None:
    lines = _changelog_lines()
    assert f"[Unreleased]: {REPO_URL}/compare/v0.10.0...HEAD" in lines
    assert f"[0.10.0]: {REPO_URL}/releases/tag/v0.10.0" in lines
    assert f"[0.9.8]: {REPO_URL}/releases/tag/v0.9.8" in lines
    assert not [
        line for line in lines if line.startswith("[Unreleased]:") and "v0.9.8" in line
    ]


# --- SC3: newest-first order --------------------------------------------


def test_release_headings_are_in_descending_pep440_order() -> None:
    versions = [
        Version(match.group("version"))
        for line in _changelog_lines()
        if (match := _RELEASE_HEADING_RE.match(line))
        and match.group("version") != "Unreleased"
    ]
    assert Version("0.10.0") in versions
    assert Version("0.1.0b1") in versions
    for newer, older in zip(versions, versions[1:], strict=False):
        assert newer > older, f"{newer} is not newer than {older}"


# --- SC2: the release-notes extraction ----------------------------------


def test_extracted_0_10_0_release_notes_name_the_breaking_change() -> None:
    result = subprocess.run(
        [sys.executable, str(EXTRACT_SCRIPT), "0.10.0"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    for fragment in ("codly", "2.0.0", "deps.typ"):
        assert fragment in result.stdout, fragment

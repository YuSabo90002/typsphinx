"""
Release-prep gate for 0.9.8 (M001 T004).

Reads files only -- no Sphinx build. It pins three things:

* the CHANGELOG fold: the first ``## [Unreleased]`` keeps only
  ``### Planned for Future Releases``; ``## [0.9.8]`` holds the Graphviz
  entries followed by the former Unreleased bibliography entries (E2), is
  dated with the release-prep commit's date (E4), and records the
  ``typst_debug`` removal;
* the link block for ``[Unreleased]`` and ``[0.9.8]``;
* one claim re-check per DOCS-AUDIT item #3 and #9-#13, so a stale claim
  cannot come back unnoticed.

The E4 date check uses ``git log``; it skips when git is unavailable or the
checkout is shallow (CI's ``actions/checkout`` uses depth 1), and it never
reads a tag date.
"""

from __future__ import annotations

import datetime
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
S03 = REPO_ROOT / "docs" / "S03-ARTIFACT-GATE-EVIDENCE.md"
S04 = REPO_ROOT / "docs" / "S04-PUBLISHED-SITE-EVIDENCE.md"
ADVANCED_README = REPO_ROOT / "examples" / "advanced" / "README.md"
CHARGED_IEEE_README = REPO_ROOT / "examples" / "charged-ieee" / "README.md"

_SECTION_RE = re.compile(r"^## \[")
_HEADING_0_9_8_RE = re.compile(r"^## \[0\.9\.8\] - (\d{4}-\d{2}-\d{2})$")

GRAPHVIZ_MARKERS = ("GVZ-", "DEG-01")
BIBLIOGRAPHY_MARKERS = ("R001-R010", "R013", "bibliograph")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changelog_lines() -> list[str]:
    return _read(CHANGELOG).splitlines()


def _section(predicate) -> list[str]:
    """Lines of the first ``## [...]`` section whose heading satisfies predicate."""
    lines = _changelog_lines()
    for start, line in enumerate(lines):
        if _SECTION_RE.match(line) and predicate(line):
            end = start + 1
            while end < len(lines) and not _SECTION_RE.match(lines[end]):
                end += 1
            return lines[start:end]
    pytest.fail("CHANGELOG.md section not found")


def _section_0_9_8() -> list[str]:
    return _section(lambda line: line.startswith("## [0.9.8]"))


def _subsection_items(section: list[str], name: str) -> list[str]:
    """Top-level ``- `` items of ``### <name>`` in section, continuation joined."""
    try:
        start = section.index(f"### {name}")
    except ValueError:
        pytest.fail(f"0.9.8 has no ### {name} subsection")
    items: list[str] = []
    for line in section[start + 1 :]:
        if line.startswith("### "):
            break
        if line.startswith("- "):
            items.append(line)
        elif line.startswith("  ") and items:
            items[-1] += " " + line.strip()
    return items


def _classify(item: str) -> str:
    is_gvz = any(m in item for m in GRAPHVIZ_MARKERS)
    is_bib = any(m in item for m in BIBLIOGRAPHY_MARKERS)
    assert is_gvz != is_bib, f"item is not exactly one of graphviz/bib: {item[:80]}"
    return "graphviz" if is_gvz else "bibliography"


@pytest.mark.parametrize("subsection", ["Added", "Changed"])
def test_0_9_8_graphviz_items_precede_bibliography_items(subsection: str) -> None:
    kinds = [_classify(i) for i in _subsection_items(_section_0_9_8(), subsection)]
    assert "graphviz" in kinds, kinds
    assert "bibliography" in kinds, kinds
    last_graphviz = max(i for i, k in enumerate(kinds) if k == "graphviz")
    first_bib = min(i for i, k in enumerate(kinds) if k == "bibliography")
    assert last_graphviz < first_bib, kinds


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def test_0_9_8_date_is_release_prep_commit_date() -> None:
    heading = _section_0_9_8()[0]
    match = _HEADING_0_9_8_RE.match(heading)
    assert match, f"0.9.8 heading is not '## [0.9.8] - YYYY-MM-DD': {heading!r}"
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


def test_first_unreleased_holds_only_planned_for_future_releases() -> None:
    section = _section(lambda line: line == "## [Unreleased]")
    subsections = [line for line in section if line.startswith("### ")]
    assert subsections == ["### Planned for Future Releases"]


def test_link_block_targets_v0_9_8() -> None:
    lines = _changelog_lines()
    assert (
        "[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.8...HEAD"
        in lines
    )
    assert (
        "[0.9.8]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.8" in lines
    )


def test_0_9_8_records_typst_debug_removal() -> None:
    removed = _subsection_items(_section_0_9_8(), "Removed")
    assert any("typst_debug" in item for item in removed), removed


# --- SC5: one claim re-check per DOCS-AUDIT item ---------------------------


def test_audit_3_fixed_item_names_0_6_0_entry() -> None:
    assert "0.9.4 entry" not in _read(CHANGELOG)
    fixed = _subsection_items(_section_0_9_8(), "Fixed")
    assert any("0.6.0 entry" in item for item in fixed), fixed


def test_audit_9_s03_has_correction_citing_ci_run() -> None:
    text = _read(S03)
    assert "\n## Correction\n" in text
    assert "41152681591" in text.split("\n## Correction\n", 1)[1]


def test_audit_10_s04_has_post_merge_results() -> None:
    text = _read(S04)
    assert "\n## Post-merge results\n" in text
    assert 'class="graphviz"' in text.split("\n## Post-merge results\n", 1)[1]


def test_audit_11_advanced_readme_has_no_templates_line() -> None:
    lines = _read(ADVANCED_README).splitlines()
    assert not [line for line in lines if "_templates/" in line]


def test_audit_12_advanced_readme_has_no_uncomment_instruction() -> None:
    assert "edit `conf.py` and uncomment" not in _read(ADVANCED_README)


def test_audit_13_charged_ieee_readme_limits_author_details() -> None:
    assert "on both approaches" not in _read(CHARGED_IEEE_README)

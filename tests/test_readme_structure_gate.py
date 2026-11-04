"""
README.md shape gate (M008 SC1-SC5).

M008 cut README.md back to an overview and left the detail to the manual
under ``docs/source``. This module pins that shape so README does not grow
manual-level detail again: the exact ``## `` heading list and order, the
Installation and Quick Start subsections, one-line Features bullets with no
pinned ``@preview/`` versions, link-only Contributing and Version History
sections, the trailing Status lines, and the Acknowledgments credits.

Reads README.md text only -- no build, no network.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"

_EXPECTED_HEADINGS = [
    "## Overview",
    "## Features",
    "## Requirements",
    "## Installation",
    "## Quick Start",
    "## Documentation",
    "## Contributing",
    "## License",
    "## Acknowledgments",
    "## Version History",
]

_RTD = "https://typsphinx.readthedocs.io/en/latest/"


def _lines() -> list[str]:
    return README_PATH.read_text(encoding="utf-8").splitlines()


def _section(heading: str) -> list[str]:
    """The lines of one ``## `` section, heading excluded."""
    lines = _lines()
    start = lines.index(heading)
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    return lines[start + 1 : end]


def _subheadings(heading: str) -> list[str]:
    return [line for line in _section(heading) if line.startswith("### ")]


def _body(heading: str) -> list[str]:
    return [line for line in _section(heading) if line.strip()]


# --- SC1 ----------------------------------------------------------------


def test_level_two_headings_are_exactly_the_approved_list() -> None:
    headings = [line for line in _lines() if line.startswith("## ")]
    assert headings == _EXPECTED_HEADINGS, headings


def test_preamble_keeps_badges_description_and_link_line() -> None:
    lines = _lines()
    preamble = lines[: lines.index("## Overview")]
    text = "\n".join(preamble)
    assert preamble[0] == "# typsphinx"
    assert "actions/workflows/ci.yml/badge.svg" in text
    assert "badge.fury.io/py/typsphinx.svg" in text
    assert "Sphinx extension for Typst output format support." in preamble
    link_line = [line for line in preamble if "Issue Tracker" in line]
    assert len(link_line) == 1, link_line
    for fragment in ("Documentation", "Issue Tracker", "PyPI"):
        assert fragment in link_line[0], fragment


# --- SC2 ----------------------------------------------------------------


def test_installation_keeps_pip_and_uv_blocks() -> None:
    text = "\n".join(_section("## Installation"))
    assert "pip install typsphinx" in text
    assert "git clone https://github.com/YuSabo90002/typsphinx.git" in text
    assert re.search(r"^uv sync$", text, re.M)
    assert re.search(r"^uv sync --extra dev$", text, re.M)


def test_quick_start_has_exactly_three_subsections() -> None:
    assert _subheadings("## Quick Start") == [
        "### Basic Configuration",
        "### Build Typst Output",
        "### Example Document",
    ]
    text = "\n".join(_section("## Quick Start"))
    assert "####" not in text
    assert "```python" in text
    assert "sphinx-build -b typst " in text
    assert "sphinx-build -b typstpdf " in text
    assert "```rst" in text


# --- SC3 ----------------------------------------------------------------


def test_features_bullets_are_single_lines() -> None:
    body = _body("## Features")
    assert body, "## Features is empty"
    for line in body:
        assert line.startswith("- **"), f"not a top-level one-line bullet: {line!r}"


def test_features_name_graphviz_and_bibliography_with_guide_links() -> None:
    body = _body("## Features")
    graphviz = [line for line in body if "Graphviz" in line]
    assert len(graphviz) == 1, graphviz
    for fragment in (".. graphviz::", ".. digraph::", ".. graph::"):
        assert fragment in graphviz[0], fragment
    assert f"{_RTD}user_guide/diagrams.html" in graphviz[0]
    bibliography = [line for line in body if "Bibliographies" in line]
    assert len(bibliography) == 1, bibliography
    for fragment in ("sphinxcontrib-bibtex", ":cite:", ".. bibliography::"):
        assert fragment in bibliography[0], fragment
    assert f"{_RTD}user_guide/bibliography.html" in bibliography[0]


def test_readme_pins_no_preview_versions_or_bibliography_internals() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    assert "@preview/" not in text
    assert not re.search(r"pybtex|CSL|#bibliography", text, re.I)


# --- SC4 ----------------------------------------------------------------


def test_contributing_is_a_link_only() -> None:
    body = _body("## Contributing")
    assert len(body) == 1, body
    assert f"{_RTD}contributing.html" in body[0]


def test_version_history_links_changelog() -> None:
    body = _body("## Version History")
    assert "[CHANGELOG.md](CHANGELOG.md)" in body[0]


def test_readme_ends_with_status_lines() -> None:
    lines = [line for line in _lines() if line.strip()]
    assert re.fullmatch(
        r"\*\*Status\*\*: Stable \(v\d+\.\d+\.\d+\) - Production ready", lines[-2]
    ), lines[-2]
    assert lines[-1].startswith("**Python**: 3.12+ | **Sphinx**: ")
    assert "**Typst**: " in lines[-1]


# --- SC5 ----------------------------------------------------------------


def test_acknowledgments_credit_upstream_and_gsd_path() -> None:
    text = "\n".join(_section("## Acknowledgments"))
    for name, url in (
        ("Sphinx", "https://www.sphinx-doc.org/"),
        ("Typst", "https://typst.app/"),
        ("mitex", "https://github.com/mitex-rs/mitex"),
        ("codly", "https://typst.app/universe/package/codly"),
        ("gentle-clues", "https://typst.app/universe/package/gentle-clues"),
        ("diagraph", "https://typst.app/universe/package/diagraph"),
        ("typst-py", "https://github.com/messense/typst-py"),
        ("GSD Path", "https://github.com/open-gsd/gsd-path"),
    ):
        assert f"[{name}]({url})" in text, name
    assert "gsd-core" not in README_PATH.read_text(encoding="utf-8")

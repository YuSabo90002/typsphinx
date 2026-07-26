"""
Regression guard for the retired-host -> Read the Docs URL rewrite (DOC-09).

Phase 31 rewrote every published documentation URL in README.md and
pyproject.toml: they used to point at a GitHub Pages host that had been
retired. Seven of README.md's deep links pointed at paths that no longer
resolved on that retired host and returned HTTP 404 for months; an external
user hit one of them and filed Issue #119. This module locks the rewrite
behind four hermetic invariants so a future edit that reintroduces the
retired host, drops or reorders a deep link, or version-pins a top-level
link fails a `pytest` run immediately instead of silently regressing a
second time.

All four tests parse raw file text (and `pyproject.toml` via `tomllib`) --
never package metadata -- and make no network calls. The real-HTTP checks
(curl sweeps, CI Link Check) are a separate instrument; see
`.planning/phases/31-published-url-cutover-repo-wide-link-guard/`.
"""

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

# The retired documentation host, built from two concatenated fragments
# split across the dot. This phase's success criteria require that a fresh
# repo-wide grep for the retired host find matches only in CHANGELOG.md. If
# this module spelled the host as one literal, it would itself be a
# permanent match, making that success criterion unverifiable without a
# permanent exclusion list. Splitting the literal keeps the repo-wide grep
# clean and honest.
_RETIRED_HOST_PREFIX = "yusabo90002.github"
_RETIRED_HOST_SUFFIX = "io"
_RETIRED_HOST = f"{_RETIRED_HOST_PREFIX}.{_RETIRED_HOST_SUFFIX}"

# Matches any URL on the Read the Docs documentation host.
_READTHEDOCS_URL_RE = re.compile(r"https://typsphinx\.readthedocs\.io/[^\s)\]]*")

# Matches a README deep link's suffix -- everything after `/en/latest/`.
_DEEP_LINK_RE = re.compile(r"https://typsphinx\.readthedocs\.io/en/latest/([^\s)\]]+)")

# A language segment (`/en/` or `/ja/`) anywhere in a URL -- used to
# partition Read the Docs URLs into "deep" (language-scoped) vs. top-level.
_LANGUAGE_SEGMENT_RE = re.compile(r"/(en|ja)/")

# A version-like path segment (`/latest/`, `/stable/`, `/v1.2.3/`, ...)
# appearing anywhere in a URL, independent of whether it is preceded by a
# language segment. Used to catch a top-level link that got version-pinned
# without also picking up a language prefix.
_VERSION_LIKE_SEGMENT_RE = re.compile(r"/(latest|stable|v?\d+\.\d+(?:\.\d+)?)(?:/|$)")

# The seven quick-link deep-link suffixes, in the order they must appear in
# README.md's "## Documentation" section. A dropped, reordered, or renamed
# suffix must fail this test, not just a wrong host.
_EXPECTED_DEEP_LINK_SUFFIXES = (
    "installation.html",
    "quickstart.html",
    "user_guide/",
    "user_guide/configuration.html",
    "examples/",
    "api/",
    "contributing.html",
)


def _read_readme_text() -> str:
    return README_PATH.read_text(encoding="utf-8")


def test_readme_documentation_links_point_at_readthedocs():
    """README.md must contain no URL on the retired documentation host.

    Guards against a vacuous pass: asserts README.md actually contains at
    least one Read the Docs URL before asserting the retired host is
    absent, so an accidental deletion of the whole Documentation section
    would not silently satisfy this test.
    """
    text = _read_readme_text()
    readthedocs_urls = _READTHEDOCS_URL_RE.findall(text)
    assert readthedocs_urls, (
        "README.md contains no typsphinx.readthedocs.io URLs at all -- has "
        "the Documentation section been removed?"
    )
    assert _RETIRED_HOST not in text, (
        f"README.md still references the retired documentation host "
        f"({_RETIRED_HOST}) -- Phase 31 rewrote every link to Read the "
        "Docs; see 31-03-SUMMARY.md."
    )


def test_readme_deep_links_carry_language_version_prefix():
    """README.md must have exactly 7 `/en/latest/` deep links, in order.

    Asserts both the count and the exact suffixes so a dropped, reordered,
    or silently-retargeted link is caught -- not just a wrong host.
    """
    text = _read_readme_text()
    deep_links = _DEEP_LINK_RE.findall(text)
    assert len(deep_links) == 7, (
        f"expected exactly 7 README deep links under /en/latest/, found "
        f"{len(deep_links)}: {deep_links}"
    )
    assert deep_links == list(_EXPECTED_DEEP_LINK_SUFFIXES), (
        "README.md's /en/latest/ deep links do not match the expected "
        f"suffixes in order. Expected {_EXPECTED_DEEP_LINK_SUFFIXES!r}, "
        f"found {tuple(deep_links)!r}."
    )


def test_readme_top_level_links_carry_no_version_segment():
    """Top-level README Read the Docs links must stay version-less.

    D-11: the badge click-through, header link, and Documentation section
    lead sentence deliberately carry no `/en/` or `/ja/` segment, so Read
    the Docs' root redirect follows the project's Default Version --
    Phase 33's `latest` -> `stable` flip reaches these links without
    another edit. A future "fix" that pins them to an explicit version
    would undo that design, not tidy it.
    """
    text = _read_readme_text()
    all_urls = _READTHEDOCS_URL_RE.findall(text)
    top_level_urls = [url for url in all_urls if not _LANGUAGE_SEGMENT_RE.search(url)]
    assert top_level_urls, (
        "found no version-less typsphinx.readthedocs.io URLs in README.md "
        "-- expected the badge click-through, header link, and section "
        "lead sentence to all be bare-root links (D-11)."
    )
    version_pinned = [
        url for url in top_level_urls if _VERSION_LIKE_SEGMENT_RE.search(url)
    ]
    assert not version_pinned, (
        "top-level README links must stay version-less so Read the Docs' "
        "Default Version flip (Phase 33) propagates without a re-edit "
        f"(D-11); found a version-like segment on: {version_pinned}"
    )


def test_pyproject_documentation_url_points_at_readthedocs():
    """pyproject.toml's `project.urls.Documentation` must address Read the Docs."""
    with open(PYPROJECT_PATH, "rb") as f:
        data = tomllib.load(f)
    documentation_url = data["project"]["urls"]["Documentation"]
    assert "typsphinx.readthedocs.io" in documentation_url, (
        f"pyproject.toml's project.urls.Documentation is "
        f"{documentation_url!r}, which does not address "
        "typsphinx.readthedocs.io -- PyPI's release metadata would "
        "advertise a stale documentation link."
    )

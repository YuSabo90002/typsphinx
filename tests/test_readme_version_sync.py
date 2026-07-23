"""
Test guarding the README/pyproject.toml version-sync hazard (D-13).

README.md's Status line (`**Status**: Stable (vX.Y.Z) - Production ready`)
has drifted stale relative to `pyproject.toml`'s `version` field across two
prior releases -- it stayed at v0.5.0 through both the v0.6.0 and v0.6.1
releases. This module asserts the two stay in lockstep, mirroring the
existing `test_preview_version_sync.py` pattern: parse each file's raw
text/structured data directly (never via `importlib.metadata`), and compare
the two parsed values against each other rather than against a hardcoded
expected version string.
"""

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

# Matches README prose of the form `**Status**: Stable (vX.Y.Z)` -- note
# this targets the README's own wording (parens plus a leading `v`), not the
# `#import "@preview/name:version"` Typst syntax that
# test_preview_version_sync.py's `_PREVIEW_IMPORT_RE` targets. Do not reuse
# that regex here; the delimiters and prefix differ.
_STATUS_LINE_RE = re.compile(
    r"\*\*Status\*\*:\s*Stable \(v(?P<version>\d+\.\d+\.\d+)\)"
)


def _extract_readme_status_version() -> str:
    """Parse README.md's raw text for the Status line's release version.

    Guards against a vacuous pass: if the Status line's wording ever changes
    such that the regex no longer matches, this raises immediately rather
    than silently comparing against an empty/missing value.
    """
    text = README_PATH.read_text(encoding="utf-8")
    match = _STATUS_LINE_RE.search(text)
    assert match, (
        "Could not find a '**Status**: Stable (vX.Y.Z)' line in README.md -- "
        "has the Status line's wording changed?"
    )
    return match.group("version")


def _extract_pyproject_version() -> str:
    """Parse pyproject.toml's [project].version via tomllib.

    Uses the stdlib TOML parser (already proven for this exact field in
    tests/test_extension.py::test_version_matches_pyproject_toml) rather
    than a regex, since a structured parser is available and more robust
    for TOML syntax.
    """
    with open(PYPROJECT_PATH, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def test_readme_status_version_matches_pyproject():
    """README.md's Status line must always name the same version as pyproject.toml.

    This compares the two parsed values against each other -- never against
    a hardcoded expected version string -- so the test survives future joint
    version bumps and only fails on a genuine divergence between the two
    files.
    """
    readme_version = _extract_readme_status_version()
    pyproject_version = _extract_pyproject_version()
    assert readme_version == pyproject_version, (
        f"README.md Status line says v{readme_version} but pyproject.toml "
        f"says {pyproject_version} -- update README.md's Status line "
        "in lockstep with any version bump."
    )

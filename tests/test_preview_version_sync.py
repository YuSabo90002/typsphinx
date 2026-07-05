"""
Tests guarding the 3-way `@preview` version-sync hazard.

typsphinx declares the same four Typst Universe `@preview` package versions
(codly, codly-languages, mitex, gentle-clues) in three separate places:
`typsphinx/writer.py`, `typsphinx/template_engine.py`, and
`typsphinx/templates/base.typ`. These must stay in lockstep, or generated
Typst documents can end up importing mismatched package versions depending
on which code path produced them. This module asserts the three declaration
sites agree, so a future single-file edit fails CI loudly instead of
silently (D-03).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

WRITER_PATH = REPO_ROOT / "typsphinx" / "writer.py"
TEMPLATE_ENGINE_PATH = REPO_ROOT / "typsphinx" / "template_engine.py"
BASE_TYP_PATH = REPO_ROOT / "typsphinx" / "templates" / "base.typ"

EXPECTED_PACKAGES = {"codly", "codly-languages", "mitex", "gentle-clues"}

# Matches an actual Typst `#import "@preview/<name>:<version>"` statement
# (not a bare mention in a comment or docstring example). name is
# letters/digits/underscore/hyphen; version is a three-part semver.
_PREVIEW_IMPORT_RE = re.compile(
    r'#import\s+"@preview/(?P<name>[A-Za-z0-9_-]+):(?P<version>\d+\.\d+\.\d+)"'
)


def _extract_preview_versions(path):
    """Parse a file's raw text for `#import "@preview/<name>:<version>"` lines.

    Only matches actual Typst import statements, not bare `@preview/...`
    text appearing in comments or docstring examples (e.g. a docstring
    illustrating the `typst_package` config option format). Returns a dict
    mapping package name to version string. If a package name appears more
    than once in a file, the last occurrence wins (mirrors how a human
    reading the file top-to-bottom would resolve it).
    """
    text = path.read_text()
    versions = {}
    for match in _PREVIEW_IMPORT_RE.finditer(text):
        versions[match.group("name")] = match.group("version")
    return versions


def test_preview_versions_identical_across_declaration_sites():
    """The three declaration sites must agree on every @preview version.

    This compares the files against each other (not against a hardcoded
    expected mapping) so the test stays correct if the whole set is
    intentionally rebumped in lockstep — it only fails on a *divergence*.
    """
    writer_versions = _extract_preview_versions(WRITER_PATH)
    template_engine_versions = _extract_preview_versions(TEMPLATE_ENGINE_PATH)
    base_typ_versions = _extract_preview_versions(BASE_TYP_PATH)

    all_files = {
        "writer.py": writer_versions,
        "template_engine.py": template_engine_versions,
        "base.typ": base_typ_versions,
    }

    all_packages = set()
    for versions in all_files.values():
        all_packages.update(versions.keys())

    divergences = []
    for package in sorted(all_packages):
        per_file_versions = {
            filename: versions.get(package, "<missing>")
            for filename, versions in all_files.items()
        }
        if len(set(per_file_versions.values())) > 1:
            divergences.append((package, per_file_versions))

    assert (
        not divergences
    ), "@preview version desync detected across declaration sites: " + "; ".join(
        f"{package}: {per_file_versions}" for package, per_file_versions in divergences
    )


def test_all_four_packages_declared():
    """Each declaration site must declare all four expected packages.

    Without this, a dropped import in one file could make the identity
    check above vacuously pass (an empty dict equals another empty dict).
    """
    files = {
        "writer.py": WRITER_PATH,
        "template_engine.py": TEMPLATE_ENGINE_PATH,
        "base.typ": BASE_TYP_PATH,
    }

    for filename, path in files.items():
        declared = set(_extract_preview_versions(path).keys())
        missing = EXPECTED_PACKAGES - declared
        assert not missing, (
            f"{filename} is missing expected @preview packages: {missing} "
            f"(declared: {declared})"
        )

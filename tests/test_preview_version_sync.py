"""
Tests guarding the `@preview` version-sync hazard.

typsphinx declares the same four Typst Universe `@preview` package versions
(codly, codly-languages, mitex, gentle-clues) in three separate places:
`typsphinx/writer.py`, `typsphinx/template_engine.py`, and
`typsphinx/templates/base.typ`. These must stay in lockstep, or generated
Typst documents can end up importing mismatched package versions depending
on which code path produced them. This module asserts the three declaration
sites agree, so a future single-file edit fails CI loudly instead of
silently (D-03).

The bundled `examples/` templates are a fourth surface. They are not part of
the extension's own import generation, so they carry no lockstep *identity*
requirement across all four packages -- an example may legitimately use only
some of them, or a different package entirely (charged-ieee). But when an
example does pin one of the four, a stale pin is not cosmetic: it makes the
shipped sample fail to compile outright (`codly-languages` older than 0.1.10
aborts with `unknown variable: kai`). That is exactly what happened to
`examples/advanced/_templates/custom.typ`, which sat three milestones behind
the v0.5.0 bump because nothing watched it. `test_example_templates_match_canonical_versions`
closes that gap.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

WRITER_PATH = REPO_ROOT / "typsphinx" / "writer.py"
TEMPLATE_ENGINE_PATH = REPO_ROOT / "typsphinx" / "template_engine.py"
BASE_TYP_PATH = REPO_ROOT / "typsphinx" / "templates" / "base.typ"

EXAMPLES_DIR = REPO_ROOT / "examples"

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


def test_example_templates_match_canonical_versions():
    """Bundled `examples/` .typ templates must not pin a stale version.

    Scans every `.typ` file under `examples/` and, for each of the four
    packages typsphinx itself pins, asserts the example agrees with the
    canonical version in `base.typ`. Packages outside that set (e.g. an
    example built on `charged-ieee`) are ignored, and an example that
    imports none of the four is trivially fine -- this guards against
    *drift*, not against an example choosing a different toolkit.
    """
    canonical = _extract_preview_versions(BASE_TYP_PATH)

    stale = []
    for typ_path in sorted(EXAMPLES_DIR.rglob("*.typ")):
        for package, version in _extract_preview_versions(typ_path).items():
            if package not in canonical:
                continue
            if version != canonical[package]:
                stale.append(
                    f"{typ_path.relative_to(REPO_ROOT)}: {package} pins "
                    f"{version}, base.typ pins {canonical[package]}"
                )

    assert not stale, (
        "bundled example template(s) pin @preview versions that diverge from "
        "typsphinx/templates/base.typ -- a shipped sample that cannot compile: "
        + "; ".join(stale)
    )

"""
Single-source gate for typsphinx's Typst Universe `@preview` dependencies.

The five default packages (codly, codly-languages, mitex, gentle-clues,
diagraph) are defined in exactly one place, `typsphinx/typst_deps.py`. Every
build writes `<outdir>/_typsphinx/deps.typ` from those definitions, and every
content file, wrapper, and the bundled `templates/base.typ` import that file
instead of pinning versions themselves. This module asserts:

* a grep-equivalent of `grep -rlE '@preview/(codly|...):' typsphinx/` over
  every `.py` and `.typ` file finds only `typsphinx/typst_deps.py`;
* `writer.py`, `template_engine.py`, and `templates/base.typ` carry no codly
  initialisation lines (`codly-init` / `codly(languages:`);
* a real build's `<outdir>/_typsphinx/deps.typ` equals
  `render_default_deps()` and imports each `DEFAULT_PACKAGES` entry once,
  in order.

The bundled `examples/` templates are a further surface. When an example
pins one of the five, a stale pin makes the shipped sample fail to compile
outright (`codly-languages` older than 0.1.10 aborts with
`unknown variable: kai`), so `test_example_templates_match_canonical_versions`
compares example pins against `DEFAULT_PACKAGES`.
"""

import re
import subprocess
import sys
from pathlib import Path

from typsphinx.typst_deps import (
    DEFAULT_PACKAGES,
    DEPS_FILENAME,
    DEPS_OUTPUT_DIR,
    render_default_deps,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "typsphinx"
DEPS_MODULE_PATH = PACKAGE_DIR / "typst_deps.py"

WRITER_PATH = PACKAGE_DIR / "writer.py"
TEMPLATE_ENGINE_PATH = PACKAGE_DIR / "template_engine.py"
BASE_TYP_PATH = PACKAGE_DIR / "templates" / "base.typ"

EXAMPLES_DIR = REPO_ROOT / "examples"
BASIC_ROOT = Path(__file__).parent / "roots" / "test-basic"

# The same pattern as SC1's grep: any mention of one of the five specs.
_FIVE_SPEC_RE = re.compile(
    r"@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):"
)
_CODLY_INIT_RE = re.compile(r"codly-init|codly\(languages")

# Matches an actual Typst `#import "@preview/<name>:<version>"` statement.
_PREVIEW_IMPORT_RE = re.compile(
    r'#import\s+"@preview/(?P<name>[A-Za-z0-9_-]+):(?P<version>\d+\.\d+\.\d+)"'
)


def _extract_preview_versions(path):
    """Map package name to version for every `#import "@preview/..."` line."""
    versions = {}
    for match in _PREVIEW_IMPORT_RE.finditer(path.read_text()):
        versions[match.group("name")] = match.group("version")
    return versions


def test_five_specs_appear_only_in_typst_deps_module():
    """SC1: under `typsphinx/`, only `typst_deps.py` names a five-package spec."""
    matches = sorted(
        str(p.relative_to(REPO_ROOT))
        for pattern in ("*.py", "*.typ")
        for p in PACKAGE_DIR.rglob(pattern)
        if _FIVE_SPEC_RE.search(p.read_text(encoding="utf-8"))
    )
    assert matches == ["typsphinx/typst_deps.py"], matches


def test_former_declaration_sites_carry_no_codly_init():
    """SC1: the three former declaration sites hold no spec and no codly init."""
    for path in (WRITER_PATH, TEMPLATE_ENGINE_PATH, BASE_TYP_PATH):
        text = path.read_text(encoding="utf-8")
        assert not _FIVE_SPEC_RE.search(text), path
        assert not _CODLY_INIT_RE.search(text), path


def test_default_packages_are_the_five_in_order():
    assert [(p.name, p.version) for p in DEFAULT_PACKAGES] == [
        ("codly", "1.3.0"),
        ("codly-languages", "0.1.10"),
        ("mitex", "0.2.7"),
        ("gentle-clues", "1.3.1"),
        ("diagraph", "0.3.7"),
    ]
    for package in DEFAULT_PACKAGES:
        assert package.spec in DEPS_MODULE_PATH.read_text(encoding="utf-8")


def test_built_deps_typ_equals_module_definitions(tmp_path):
    """SC1: a built `deps.typ` is exactly `render_default_deps()`, with one
    `#import "<spec>": <items>` line per `DEFAULT_PACKAGES` entry, in order."""
    out = tmp_path / "out"
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-q", "-E", "-b", "typst"]
        + [str(BASIC_ROOT), str(out), "-d", str(tmp_path / "doctrees")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    built = (out / DEPS_OUTPUT_DIR / DEPS_FILENAME).read_bytes()
    assert built == render_default_deps().encode("utf-8")

    import_lines = [
        line
        for line in built.decode("utf-8").splitlines()
        if line.startswith("#import")
    ]
    assert import_lines == [
        f'#import "{package.spec}": {package.items}' for package in DEFAULT_PACKAGES
    ]
    assert import_lines == [
        '#import "@preview/codly:1.3.0": *',
        '#import "@preview/codly-languages:0.1.10": *',
        '#import "@preview/mitex:0.2.7": mi, mitex',
        '#import "@preview/gentle-clues:1.3.1": *',
        '#import "@preview/diagraph:0.3.7": render',
    ]


def test_example_templates_match_canonical_versions():
    """Bundled `examples/` .typ templates must not pin a stale version.

    For each of the five default packages an example pins, the version must
    equal the one in `DEFAULT_PACKAGES`. Other packages are ignored.
    """
    canonical = {package.name: package.version for package in DEFAULT_PACKAGES}

    stale = []
    for typ_path in sorted(EXAMPLES_DIR.rglob("*.typ")):
        for package, version in _extract_preview_versions(typ_path).items():
            if package not in canonical:
                continue
            if version != canonical[package]:
                stale.append(
                    f"{typ_path.relative_to(REPO_ROOT)}: {package} pins "
                    f"{version}, DEFAULT_PACKAGES has {canonical[package]}"
                )

    assert not stale, (
        "bundled example template(s) pin @preview versions that diverge from "
        "typsphinx/typst_deps.py -- a shipped sample that cannot compile: "
        + "; ".join(stale)
    )

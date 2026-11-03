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
  initialisation lines (`codly-init` / `codly(languages:` / `lang-set_`);
* a real build's `<outdir>/_typsphinx/deps.typ` equals
  `render_default_deps()` and imports each `DEFAULT_PACKAGES` entry once,
  in order, with codly imported as a module (`as codly`) and a
  `typsphinx-init` that only applies `codly.lang-set_`.

The repository's own templates and samples are a further surface (SC5):
`test_repo_templates_pin_none_of_the_five` asserts that no file under
`docs/source/_typst/`, `examples/`,
`tests/fixtures/admonition_greyscale_probe/_templates/`, or
`tests/fixtures/typst_lang_gate/` names a five-package spec -- they take
package names from `/_typsphinx/deps.typ` instead of pinning versions.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

from typsphinx.typst_deps import (
    DEFAULT_PACKAGES,
    DEPS_FILENAME,
    DEPS_OUTPUT_DIR,
    PreviewPackage,
    render_default_deps,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "typsphinx"
DEPS_MODULE_PATH = PACKAGE_DIR / "typst_deps.py"

WRITER_PATH = PACKAGE_DIR / "writer.py"
TEMPLATE_ENGINE_PATH = PACKAGE_DIR / "template_engine.py"
BASE_TYP_PATH = PACKAGE_DIR / "templates" / "base.typ"

# SC5: the repository-owned template and sample trees that must pin none
# of the five packages.
NO_PIN_DIRS = (
    REPO_ROOT / "docs" / "source" / "_typst",
    REPO_ROOT / "examples",
    REPO_ROOT / "tests" / "fixtures" / "admonition_greyscale_probe" / "_templates",
    REPO_ROOT / "tests" / "fixtures" / "typst_lang_gate",
)
BASIC_ROOT = Path(__file__).parent / "roots" / "test-basic"

# The same pattern as SC1's grep: any mention of one of the five specs.
_FIVE_SPEC_RE = re.compile(
    r"@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):"
)
_CODLY_INIT_RE = re.compile(r"codly-init|codly\(languages|lang-set_")


def test_five_specs_appear_only_in_typst_deps_module():
    """SC1: under `typsphinx/`, only `typst_deps.py` names a five-package spec."""
    matches = sorted(
        p.relative_to(REPO_ROOT).as_posix()
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
        ("codly", "2.0.0"),
        ("codly-languages", "0.1.10"),
        ("mitex", "0.2.7"),
        ("gentle-clues", "1.3.1"),
        ("diagraph", "0.3.7"),
    ]
    for package in DEFAULT_PACKAGES:
        assert package.spec in DEPS_MODULE_PATH.read_text(encoding="utf-8")


def test_built_deps_typ_equals_module_definitions(tmp_path):
    """SC1: a built `deps.typ` is exactly `render_default_deps()`, with one
    `#import` line per `DEFAULT_PACKAGES` entry, in order -- codly as a module
    (`as codly`), the other four as item imports -- and a `typsphinx-init`
    holding only the codly 2.0 language registration (no `codly-init`, no
    state-style `codly(` call, no `show raw` rule)."""
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
    assert import_lines == [package.import_line() for package in DEFAULT_PACKAGES]
    assert import_lines == [
        '#import "@preview/codly:2.0.0" as codly',
        '#import "@preview/codly-languages:0.1.10": *',
        '#import "@preview/mitex:0.2.7": mi, mitex',
        '#import "@preview/gentle-clues:1.3.1": *',
        '#import "@preview/diagraph:0.3.7": render',
    ]

    text = built.decode("utf-8")
    init = text[text.index("#let typsphinx-init(body) = {") :]
    assert init == (
        "#let typsphinx-init(body) = {\n"
        "  show: codly.lang-set_(languages: codly-languages)\n"
        "  body\n"
        "}\n"
    )
    assert "codly-init" not in text
    assert not re.search(r"(^|[^.a-z-])codly\(", text)
    assert "show raw" not in text


def test_preview_package_import_forms():
    """An aliased package imports as a module; exactly one form is set."""
    assert (
        PreviewPackage(spec="@preview/codly:2.0.0", alias="codly").import_line()
        == '#import "@preview/codly:2.0.0" as codly'
    )
    assert (
        PreviewPackage(spec="@preview/mitex:0.2.7", items="mi, mitex").import_line()
        == '#import "@preview/mitex:0.2.7": mi, mitex'
    )
    with pytest.raises(ValueError):
        PreviewPackage(spec="@preview/codly:2.0.0")
    with pytest.raises(ValueError):
        PreviewPackage(spec="@preview/codly:2.0.0", items="*", alias="codly")


def _no_pin_violations(roots):
    """`path:line` for every five-package spec under `roots` (grep -rnE)."""
    hits = []
    for root in roots:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                if _FIVE_SPEC_RE.search(line):
                    shown = (
                        path.relative_to(REPO_ROOT)
                        if path.is_relative_to(REPO_ROOT)
                        else path
                    )
                    hits.append(f"{shown}:{lineno}")
    return hits


def test_repo_templates_pin_none_of_the_five():
    """SC5: the repository's own templates and samples pin none of the five.

    Equivalent of `grep -rnE '@preview/(codly|...):'` over `NO_PIN_DIRS`;
    template authors take these names from `/_typsphinx/deps.typ` instead.
    """
    for root in NO_PIN_DIRS:
        assert root.is_dir(), root
    hits = _no_pin_violations(NO_PIN_DIRS)
    assert not hits, (
        "repository template(s)/sample(s) pin a five-package @preview spec; "
        "import names from /_typsphinx/deps.typ instead: " + "; ".join(hits)
    )


def test_no_pin_check_catches_a_reintroduced_pin(tmp_path):
    """SC5: the no-pin scan flags a pinned import, so the gate can fail."""
    (tmp_path / "t.typ").write_text(
        '#import "@preview/gentle-clues:1.3.1": *\n', encoding="utf-8"
    )
    (tmp_path / "ok.typ").write_text(
        '#import "/_typsphinx/deps.typ": *\n', encoding="utf-8"
    )
    hits = _no_pin_violations([tmp_path])
    assert len(hits) == 1 and hits[0].endswith("t.typ:1"), hits

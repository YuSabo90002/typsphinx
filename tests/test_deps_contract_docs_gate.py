"""
M002 T005 (SC6): the published ``deps.typ`` contract and ``typst_dependencies``
documentation agree with the code.

Reads files only -- no Sphinx build. It pins:

* ``configuration.rst``: the ``typst_dependencies`` entry (path rule, one
  global file, verbatim copy, generated default when unset, build stop) and
  the not-guaranteed statement for a replaced ``deps.typ`` (N4);
* ``templates.rst``: the path ``/_typsphinx/deps.typ``, every exported name,
  the default versions, the author guidance (import names, do not pin), the
  drift warning, and N4;
* ``output_layout.rst``: ``_typsphinx/`` is reserved, and hand compiles use
  the output directory as the compile root;
* ``CHANGELOG.md`` ``[Unreleased]`` and ``CLAUDE.md``'s ``@preview`` section.

The export list is DERIVED from ``render_default_deps()`` (explicit import
items, ``as`` module aliases, ``#let`` names, and the names
``typsphinx-init`` uses, member accesses such as ``codly.lang-set_``
excluded) plus the
gentle-clues names the translator emits, read from ``translator.py``'s
``_visit_admonition`` call sites -- never a hand-copied list -- so renaming
an export fails this gate until the docs follow.
"""

from __future__ import annotations

import re
from pathlib import Path

from typsphinx.typst_deps import (
    DEFAULT_PACKAGES,
    DEPS_IMPORT_PATH,
    INIT_FUNCTION_NAME,
    deps_preamble_lines,
    render_default_deps,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
USER_GUIDE = REPO_ROOT / "docs" / "source" / "user_guide"
CONFIGURATION_RST = USER_GUIDE / "configuration.rst"
TEMPLATES_RST = USER_GUIDE / "templates.rst"
OUTPUT_LAYOUT_RST = USER_GUIDE / "output_layout.rst"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
TRANSLATOR = REPO_ROOT / "typsphinx" / "translator.py"

# SYNTHESIS: the gentle-clues names the translator emits.
EXPECTED_GENTLE_CLUES_NAMES = {
    "abstract",
    "danger",
    "error",
    "info",
    "memo",
    "notify",
    "task",
    "tip",
    "warning",
}

# The fixed part of the K5 drift warning text.
DRIFT_WARNING_PREFIX = "template dependency drift: "
DRIFT_WARNING_MIDDLE = ", but _typsphinx/deps.typ has @preview/"

_UNDERLINE_CHARS = "=-~^\"'*+#"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _is_underline(line: str, title: str) -> bool:
    stripped = line.rstrip()
    return (
        bool(stripped)
        and stripped[0] in _UNDERLINE_CHARS
        and stripped == stripped[0] * len(stripped)
        and len(stripped) >= len(title.rstrip())
    )


def _rst_section(path: Path, heading: str) -> str:
    """The body of the section titled ``heading`` (matched on its exact
    title text), up to the next heading at the same or a higher level."""
    lines = _read(path).splitlines()
    start = None
    for i in range(len(lines) - 1):
        if lines[i].strip() == heading and _is_underline(lines[i + 1], lines[i]):
            start = i
            break
    assert start is not None, f"{path.name} has no {heading!r} heading"
    levels: list[str] = []
    for i in range(len(lines) - 1):
        if lines[i].strip() and _is_underline(lines[i + 1], lines[i]):
            char = lines[i + 1].strip()[0]
            if char not in levels:
                levels.append(char)
    own_level = levels.index(lines[start + 1].strip()[0])
    end = len(lines)
    for j in range(start + 2, len(lines) - 1):
        if lines[j].strip() and _is_underline(lines[j + 1], lines[j]):
            if levels.index(lines[j + 1].strip()[0]) <= own_level:
                end = j
                break
    return "\n".join(lines[start + 2 : end])


def _flat(text: str) -> str:
    """Collapse whitespace so a phrase wrapped across lines still matches."""
    return " ".join(text.split())


def _translator_gentle_clues_names() -> set[str]:
    return set(
        re.findall(r'self\._visit_admonition\(\s*node,\s*"([a-z]+)"', _read(TRANSLATOR))
    )


def _default_deps_exports() -> set[str]:
    """Every name the generated default ``deps.typ`` exports that the
    translator and ``typsphinx-init`` rely on."""
    text = render_default_deps()
    names: set[str] = set()
    for items in re.findall(r'^#import "@preview/[^"]+": (.+)$', text, re.M):
        if items.strip() != "*":
            names.update(item.strip() for item in items.split(","))
    names.update(
        re.findall(r'^#import "@preview/[^"]+" as ([A-Za-z][\w-]*)$', text, re.M)
    )
    names.update(re.findall(r"^#let ([A-Za-z][\w-]*)", text, re.M))
    init_match = re.search(
        rf"^#let {re.escape(INIT_FUNCTION_NAME)}\(body\) = \{{(.*?)^\}}",
        text,
        re.M | re.S,
    )
    assert init_match, "render_default_deps() no longer defines typsphinx-init"
    # A name after `.` is a module member (`codly.lang-set_`), not an export.
    tokens = set(re.findall(r"(?<![.\w-])[A-Za-z][\w-]*", init_match.group(1)))
    names.update(tokens - {"show", "with", "body", "languages"})
    names.update(_translator_gentle_clues_names())
    return names


# --------------------------------------------------------------------------
# Derivation sanity
# --------------------------------------------------------------------------


def test_translator_emits_exactly_the_nine_gentle_clues_names():
    assert _translator_gentle_clues_names() == EXPECTED_GENTLE_CLUES_NAMES


def test_derived_export_list_covers_the_k3_contract():
    exports = _default_deps_exports()
    for name in ("codly", "codly-languages", "mi", "mitex", "render"):
        assert name in exports, (name, sorted(exports))
    assert "codly-init" not in exports, sorted(exports)
    assert "lang-set_" not in exports, sorted(exports)
    assert INIT_FUNCTION_NAME in exports
    assert EXPECTED_GENTLE_CLUES_NAMES <= exports


# --------------------------------------------------------------------------
# AC1: configuration.rst
# --------------------------------------------------------------------------


def _configuration_section() -> str:
    return _flat(_rst_section(CONFIGURATION_RST, "Typst Dependencies"))


def test_configuration_documents_typst_dependencies_path_rule():
    section = _configuration_section()
    assert "``typst_dependencies``" in section
    assert "relative to the source directory" in section
    assert "an absolute path" in section
    assert "``typst_template``" in section


def test_configuration_documents_one_global_file():
    section = _configuration_section()
    assert "One global file." in section
    assert "never one per template" in section


def test_configuration_documents_verbatim_copy():
    section = _configuration_section()
    assert "Verbatim copy." in section
    assert "byte-identical" in section
    assert "<outdir>/_typsphinx/deps.typ" in section


def test_configuration_documents_default_when_unset():
    section = _configuration_section()
    assert "Default when unset." in section
    assert "``None`` (the default)" in section
    assert "generates the default file" in section


def test_configuration_documents_the_build_stop():
    section = _configuration_section()
    assert "Build stop." in section
    assert "An empty string" in section
    assert "does not name an existing file stops the build" in section
    catalogue = _flat(_rst_section(CONFIGURATION_RST, "When the Build Stops"))
    for fragment in (
        "typst_dependencies: expected a file path (str) or None",
        "typst_dependencies: empty path",
        "typst_dependencies: file not found:",
        "typst_dependencies: not a regular file:",
    ):
        assert f"``{fragment}``" in catalogue, fragment


def test_configuration_states_a_replaced_file_is_not_guaranteed():
    section = _configuration_section()
    assert "Only the default package versions are supported." in section
    assert "not guaranteed" in section
    assert "at your own risk" in section


# --------------------------------------------------------------------------
# AC2/AC3: templates.rst
# --------------------------------------------------------------------------


def _templates_section_raw() -> str:
    return _rst_section(TEMPLATES_RST, "Package Dependencies (``deps.typ``)")


def _templates_section() -> str:
    return _flat(_templates_section_raw())


def test_templates_names_the_contract_path():
    section = _templates_section()
    assert f"``{DEPS_IMPORT_PATH}``" in section
    assert "public contract" in section
    for line in deps_preamble_lines():
        assert line in _templates_section_raw(), line


def test_templates_lists_every_exported_name():
    section = _templates_section()
    missing = sorted(
        name for name in _default_deps_exports() if f"``{name}``" not in section
    )
    assert not missing, f"templates.rst deps.typ section omits {missing}"


def test_templates_lists_the_default_versions():
    raw = _templates_section_raw()
    for package in DEFAULT_PACKAGES:
        row = f"   * - {package.name}\n     - {package.version}\n"
        assert row in raw, f"no default-version row for {package.spec}"


def test_templates_describes_typsphinx_init():
    section = _templates_section()
    assert f"``{INIT_FUNCTION_NAME}`` is a show function" in section
    assert "``codly.lang-set_``" in section
    assert "show: codly.lang-set_(languages: codly-languages)" in section
    assert "installs no rule that turns raw blocks into codly blocks" in section


def test_templates_codly_row_exports_the_module_not_codly_init():
    raw = _templates_section_raw()
    row = raw[raw.index("   * - codly\n") :]
    row = row[: row.index("   * - codly-languages")]
    assert "``codly``, imported as a module" in _flat(row), row
    assert "codly-init" not in row, row


def test_templates_carries_the_codly_1_3_migration_note():
    section = _templates_section()
    assert "**Migrating from codly 1.3.**" in section
    assert "``codly-init``" in section
    assert "``#show: codly.set_(...)``" in section
    assert '``#import "@preview/codly:2.0.0" as codly``' in section


def test_templates_tells_authors_to_import_rather_than_pin():
    section = _templates_section()
    raw = _templates_section_raw()
    assert "do not pin versions" in section
    assert re.search(rf'#import "{re.escape(DEPS_IMPORT_PATH)}": [a-z]', raw)


def test_templates_documents_the_drift_warning_as_best_effort():
    section = _templates_section()
    assert DRIFT_WARNING_PREFIX in section
    assert DRIFT_WARNING_MIDDLE in section
    assert "best-effort" in section
    assert "built at run time" in section


def test_templates_states_a_replaced_file_is_not_guaranteed():
    section = _templates_section()
    assert "Only the default versions in the table above are supported." in section
    assert "not guaranteed" in section
    assert "at your own risk" in section
    assert "must still export every name" in section


def test_deps_sections_make_no_compatibility_promise():
    for section in (_templates_section(), _configuration_section()):
        lowered = section.lower()
        assert "compatible" not in lowered
        assert "tested" not in lowered


def test_output_layout_names_the_reserved_directory_and_compile_root():
    text = _flat(_read(OUTPUT_LAYOUT_RST))
    assert "the reserved ``_typsphinx/`` output directory" in text
    assert "Both ``_template/`` and ``_typsphinx/`` are reserved" in text
    assert "imports ``/_typsphinx/deps.typ``" in text
    assert "which must be the output directory" in text
    assert "Passing the output directory as ``--root`` is always correct" in text


# --------------------------------------------------------------------------
# AC4: CHANGELOG [Unreleased]
# --------------------------------------------------------------------------


def _unreleased_section() -> str:
    lines = _read(CHANGELOG).splitlines()
    start = lines.index("## [Unreleased]")
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## ["):
        end += 1
    return _flat("\n".join(lines[start:end]))


def test_changelog_unreleased_records_the_change():
    section = _unreleased_section()
    assert "`<outdir>/_typsphinx/deps.typ`" in section
    assert "`typsphinx-init`" in section
    assert "`typsphinx/typst_deps.py`" in section
    assert "`typst_dependencies`" in section
    assert "drift warning" in section
    assert "`template dependency drift: ...`" in section
    assert "--root <outdir>" in section
    assert "### Planned for Future Releases" in section


def test_changelog_unreleased_records_the_codly_2_breaking_change():
    section = _unreleased_section()
    assert "**Breaking: codly is upgraded from 1.3.0 to 2.0.0" in section
    assert "`codly-init`" in section
    assert "`codly.new(...)`" in section
    assert "`#show: codly.set_(...)`" in section
    assert '`#import "@preview/codly:2.0.0" as codly`' in section
    assert "**Raw blocks written by users are no longer rendered through codly.**" in (
        section
    )
    assert "`.. raw:: typst`" in section


# --------------------------------------------------------------------------
# AC5: CLAUDE.md
# --------------------------------------------------------------------------


def _claude_preview_section() -> str:
    text = _read(CLAUDE_MD)
    start = text.index("### The `@preview` version-sync hazard")
    end = text.index("\n## ", start)
    return text[start:end]


def test_claude_md_preview_section_describes_the_single_source():
    section = _claude_preview_section()
    assert "`typsphinx/typst_deps.py`" in section
    assert "`<outdir>/_typsphinx/deps.typ`" in section
    assert "`tests/test_preview_version_sync.py`" in section
    assert "drift warning" in section
    assert "**three** places" not in section
    assert "lockstep" not in section


def test_claude_md_architecture_bullets_match_the_preamble():
    text = _read(CLAUDE_MD)
    writer_bullet = text[text.index("- **`writer.py`**") :]
    writer_bullet = writer_bullet[: writer_bullet.index("\n\n")]
    for line in deps_preamble_lines():
        assert f"`{line}`" in writer_bullet, line
    assert "codly init prepended" not in writer_bullet
    engine_bullet = text[text.index("- **`template_engine.py`**") :]
    engine_bullet = engine_bullet[: engine_bullet.index("\n\n")]
    assert "`deps.typ` preamble" in engine_bullet
    assert "generates package imports" not in engine_bullet
    surface = text[text.index("## Configuration surface") :]
    surface = surface[: surface.index("\n## ", 1)]
    assert "`typst_dependencies`" in surface

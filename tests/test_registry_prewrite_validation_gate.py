"""
Phase 53 plan 06: real-``sphinx-build`` subprocess gate closing ROADMAP
Phase 53 Success Criterion #3, the single gap left open by
``53-VERIFICATION.md``. ``resolve_registry_key()`` (CONF-14) was reached
only from ``_write_typst_files()``'s per-docname wrapper loop, which runs
strictly AFTER that docname's own content file -- and after every
earlier-sorted docname's content and wrapper files -- have already hit
disk. The pre-fix RED transcript recorded in
``.planning/phases/53-template-registry-foundation/53-06-RED-EVIDENCE.md``
proves the SET of ``.typ`` files surviving a failed build differed with the
offending master's sort position: with the bad key sorting last, `alpha`'s
content+wrapper survived; with it sorting first, nothing did but the two
surviving sets were still order-dependent. Post-fix,
``TypstBuilder._validate_registry_key_references()`` runs once from
``write()``, before ``prepare_writing()``, so BOTH orders leave zero
``.typ`` files and raise the byte-identical ``ExtensionError``.
"""

import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
BAD_LAST_FIXTURE_DIR = FIXTURES_DIR / "conf14_prewrite_bad_last_gate"
BAD_FIRST_FIXTURE_DIR = FIXTURES_DIR / "conf14_prewrite_bad_first_gate"
CONTROL_FIXTURE_DIR = FIXTURES_DIR / "conf14_prewrite_control_gate"

REGISTRY_KEY_ERROR_MARKER = "typst_documents entry names registry key"
NOT_REGISTERED_MARKER = "not a registered typst_document_templates key"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str = "typst"
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            builder,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


def _typ_files(build_dir: Path) -> list:
    """Sorted list of every ``.typ`` file under ``build_dir``, or an empty
    list when the directory does not exist. Returns the LIST, not a bool,
    so a failure message can name the survivors."""
    if not build_dir.exists():
        return []
    return sorted(build_dir.rglob("*.typ"))


def _extract_registry_key_message(combined_output: str) -> str:
    """Locate the substring ``REGISTRY_KEY_ERROR_MARKER`` in ``combined_output``
    and return the remainder of that line, for cross-build message-identity
    comparison."""
    for line in combined_output.splitlines():
        if REGISTRY_KEY_ERROR_MARKER in line:
            return line[line.index(REGISTRY_KEY_ERROR_MARKER) :]
    return ""


class TestRegistryKeyPreWriteGate:
    """CONF-14's up-front validation pass: a ``typst_documents`` entry
    naming an unregistered registry key leaves ZERO ``.typ`` files on disk,
    in both master orders, with a byte-identical error message
    (ROADMAP SC#3)."""

    def test_conf14_bad_key_sorting_last_writes_no_typ_files(self, tmp_path):
        """Pre-fix RED (53-06-RED-EVIDENCE.md): `alpha`'s content and
        wrapper files survive on disk because `beta` (the offending
        docname, sorted second) fails only after `alpha`'s write already
        completed. Post-fix: zero `.typ` files survive."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BAD_LAST_FIXTURE_DIR, build_dir)

        assert result.returncode != 0, (
            f"Expected the build to fail on an unregistered registry key:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            NOT_REGISTERED_MARKER in combined_output
        ), f"Expected the CONF-14 message substring:\n{combined_output}"
        survivors = _typ_files(build_dir)
        assert survivors == [], (
            f"Expected NO .typ file written when a registry-key reference "
            f"is bad, found: {survivors}"
        )

    def test_conf14_bad_key_sorting_first_writes_no_typ_files(self, tmp_path):
        """Pre-fix RED (53-06-RED-EVIDENCE.md): the offending docname
        (`aaa_bad`, sorted first) fails immediately, but the SURVIVING set
        differs from the bad-last fixture's -- that difference is the
        order-dependence this fix removes. Post-fix: zero `.typ` files
        survive here too."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BAD_FIRST_FIXTURE_DIR, build_dir)

        assert result.returncode != 0, (
            f"Expected the build to fail on an unregistered registry key:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            NOT_REGISTERED_MARKER in combined_output
        ), f"Expected the CONF-14 message substring:\n{combined_output}"
        survivors = _typ_files(build_dir)
        assert survivors == [], (
            f"Expected NO .typ file written when a registry-key reference "
            f"is bad, found: {survivors}"
        )

    def test_conf14_message_identical_across_both_master_orders(self, tmp_path):
        """The registry-key error text is order-independent: both fixtures
        name the same bad key (`nope`) against the same registered key
        (`good`), so the message is the same string regardless of which
        master's write triggers it."""
        build_dir_a = tmp_path / "build_a"
        build_dir_b = tmp_path / "build_b"
        result_a = _run_sphinx_build(BAD_LAST_FIXTURE_DIR, build_dir_a)
        result_b = _run_sphinx_build(BAD_FIRST_FIXTURE_DIR, build_dir_b)

        combined_a = result_a.stdout + result_a.stderr
        combined_b = result_b.stdout + result_b.stderr
        message_a = _extract_registry_key_message(combined_a)
        message_b = _extract_registry_key_message(combined_b)

        assert message_a, f"No registry-key error line found in build A:\n{combined_a}"
        assert message_b, f"No registry-key error line found in build B:\n{combined_b}"
        assert message_a == message_b, (
            f"Expected a byte-identical registry-key error message "
            f"regardless of master order:\nA: {message_a}\nB: {message_b}"
        )

    def test_control_config_builds_unchanged_typ_set(self, tmp_path):
        """TPL-03/TPL-04 no-op control: a four-element entry, a
        five-element entry with an explicit literal `typst` fifth element,
        an unusable one-element entry, and a declared-but-unreferenced
        registry key all build to exactly the same `.typ` set as before
        this plan's validation pass existed (ROADMAP SC#2)."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(CONTROL_FIXTURE_DIR, build_dir)

        assert (
            result.returncode == 0
        ), f"Expected the control build to succeed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        survivors = sorted(p.name for p in _typ_files(build_dir))
        expected = sorted(
            [
                "_template.typ",
                "five.typ",
                "five_out.typ",
                "four.typ",
                "four_out.typ",
                "index.typ",
            ]
        )
        assert survivors == expected, f"Expected exactly {expected}, found {survivors}"


class TestValidateRegistryKeyReferencesUnit:
    """In-process unit half of `_validate_registry_key_references()`,
    pinning every no-op / skip path that a subprocess build cannot cheaply
    exercise per-case: an empty `typst_documents`, each of
    `_is_usable_typst_documents_entry()`'s three False cases, TPL-04's
    four-element and explicit-`typst` pass-throughs, and the
    declaration-order/first-raise determinism decision recorded in
    `_validate_registry_key_references()`'s own docstring. Imports
    `TypstBuilder` / `resolve_template_registry` inside each test body,
    matching this repo's `TestIsUsableTypstDocumentsEntryUnit` convention."""

    def test_empty_typst_documents_does_not_raise(self, temp_sphinx_app):
        from typsphinx.builder import TypstBuilder
        from typsphinx.template_registry import resolve_template_registry

        app = temp_sphinx_app
        builder = TypstBuilder(app, app.env)
        builder._document_template_registry = resolve_template_registry(
            builder.config, str(app.srcdir)
        )
        builder.config.typst_documents = []

        assert builder._validate_registry_key_references() is None

    @pytest.mark.parametrize(
        "unusable_entry",
        [
            pytest.param((), id="empty_tuple"),
            pytest.param(("index",), id="one_element_tuple"),
            pytest.param((123, "t.typ"), id="non_str_docname"),
        ],
    )
    def test_unusable_entries_are_skipped_without_raising(
        self, temp_sphinx_app, unusable_entry
    ):
        from typsphinx.builder import TypstBuilder
        from typsphinx.template_registry import resolve_template_registry

        app = temp_sphinx_app
        builder = TypstBuilder(app, app.env)
        builder._document_template_registry = resolve_template_registry(
            builder.config, str(app.srcdir)
        )
        builder.config.typst_documents = [unusable_entry]

        assert builder._validate_registry_key_references() is None

    def test_four_element_and_explicit_typst_entries_do_not_raise(
        self, temp_sphinx_app
    ):
        from typsphinx.builder import TypstBuilder
        from typsphinx.template_registry import resolve_template_registry

        app = temp_sphinx_app
        builder = TypstBuilder(app, app.env)
        builder._document_template_registry = resolve_template_registry(
            builder.config, str(app.srcdir)
        )
        builder.config.typst_documents = [
            ("index", "manual.typ", "Title", "Author"),
            ("index", "manual2.typ", "Title", "Author", "typst"),
        ]

        assert builder._validate_registry_key_references() is None

    def test_two_bad_entries_raise_once_naming_the_first(self, temp_sphinx_app):
        from sphinx.errors import ExtensionError

        from typsphinx.builder import TypstBuilder
        from typsphinx.template_registry import resolve_template_registry

        app = temp_sphinx_app
        builder = TypstBuilder(app, app.env)
        builder._document_template_registry = resolve_template_registry(
            builder.config, str(app.srcdir)
        )
        builder.config.typst_documents = [
            ("index", "a.typ", "Title A", "Author A", "first-bad"),
            ("other", "b.typ", "Title B", "Author B", "second-bad"),
        ]

        with pytest.raises(ExtensionError) as exc_info_1:
            builder._validate_registry_key_references()
        with pytest.raises(ExtensionError) as exc_info_2:
            builder._validate_registry_key_references()

        message_1 = str(exc_info_1.value)
        message_2 = str(exc_info_2.value)
        assert message_1 == message_2, (
            f"Expected two consecutive calls to raise byte-identical "
            f"messages:\n1: {message_1}\n2: {message_2}"
        )
        assert repr("first-bad") in message_1
        assert repr("second-bad") not in message_1

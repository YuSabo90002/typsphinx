"""Tests for `typsphinx.template_registry` (Phase 53, plans 53-02/53-03).

In-process unit style, following
`tests/test_builder_output_stem.py::test_validate_output_path_collisions_raises_on_docname_collision`
(391-416): a `temp_sphinx_app` fixture, a directly-constructed `TypstBuilder`,
and direct calls into the module under test -- no subprocess build.
"""

import inspect
import os
from pathlib import Path

import pytest
from sphinx.errors import ExtensionError

from typsphinx.template_registry import (
    RESERVED_REGISTRY_KEY,
    TemplateRegistryEntry,
    _violates_conf17,
    resolve_registry_key,
    resolve_template_registry,
)
from typsphinx.writer import TypstWriter


def test_default_config_resolves_registry_with_only_the_typst_key(temp_sphinx_app):
    """TPL-03/D-02: a `conf.py` that sets nothing new (no
    `typst_document_templates`) still builds, and the registry resolved
    for it contains exactly one key, the synthesized built-in `"typst"`."""
    app = temp_sphinx_app
    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert list(registry.keys()) == [RESERVED_REGISTRY_KEY]
    assert registry[RESERVED_REGISTRY_KEY].key == RESERVED_REGISTRY_KEY


def test_four_element_tuple_and_explicit_typst_fifth_element_resolve_identically(
    temp_sphinx_app,
):
    """TPL-04: a four-element `typst_documents` tuple resolves to the SAME
    `TemplateRegistryEntry` object as the same tuple with a fifth element
    of the literal `"typst"` -- asserted with `is`, not equality, so a
    per-lookup copy would fail."""
    app = temp_sphinx_app
    registry = resolve_template_registry(app.config, str(app.srcdir))

    four_element_entry = ("index", "manual.typ", "Title", "Author")
    five_element_entry = ("index", "manual.typ", "Title", "Author", "typst")

    resolved_from_four = resolve_registry_key(registry, four_element_entry)
    resolved_from_five = resolve_registry_key(registry, five_element_entry)

    assert resolved_from_four is resolved_from_five


def test_two_entries_naming_same_user_defined_key_share_one_object(temp_sphinx_app):
    """TPL-05: two `typst_documents` entries naming the same registry key
    resolve to the IDENTICAL `TemplateRegistryEntry` object -- the dict
    value, not two per-entry copies -- asserted with `is`."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    (srcdir / "_templates").mkdir()
    (srcdir / "_templates" / "report.typ").write_text("")
    app.config.typst_document_templates = {
        "report": {"template": "_templates/report.typ"}
    }
    registry = resolve_template_registry(app.config, str(app.srcdir))

    entry_a = ("index", "a.typ", "Title A", "Author A", "report")
    entry_b = ("other", "b.typ", "Title B", "Author B", "report")

    resolved_a = resolve_registry_key(registry, entry_a)
    resolved_b = resolve_registry_key(registry, entry_b)

    assert resolved_a is resolved_b
    assert resolved_a.template == "_templates/report.typ"


def test_user_defined_key_omitting_template_function_gets_none_not_inherited(
    temp_sphinx_app,
):
    """D-10: a user-defined registry key whose definition omits
    `template_function` resolves to `template_function` `None` -- it does
    NOT inherit global `typst_template_function`."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    (srcdir / "sub").mkdir()
    (srcdir / "sub" / "custom.typ").write_text("")
    app.config.typst_template_function = "global_project_fn"
    app.config.typst_document_templates = {"custom": {"template": "sub/custom.typ"}}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert registry["custom"].template_function is None
    # The built-in "typst" key IS synthesized from the global value --
    # confirming the omission above is deliberate, not accidental.
    assert registry[RESERVED_REGISTRY_KEY].template_function == "global_project_fn"


def test_empty_typst_document_templates_resolves_to_only_the_typst_key(
    temp_sphinx_app,
):
    """D-02/TPL-03: an empty (or absent) `typst_document_templates` dict --
    the registered default -- is legal and resolves to a registry
    containing only the synthesized `"typst"` key."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert list(registry.keys()) == [RESERVED_REGISTRY_KEY]


def test_render_wrapper_builds_engine_from_resolved_entry_not_raw_config(
    temp_sphinx_app,
):
    """`render_wrapper()`'s own source region (Task 2 pins this with
    `inspect.getsource`) no longer reads `typst_template` / `typst_package`
    / `typst_template_function` off config -- confirmed structurally here
    by checking `template_entry` is now a parameter of the method."""
    signature = inspect.signature(TypstWriter.render_wrapper)
    assert "template_entry" in signature.parameters


def test_resolve_template_registry_accepts_srcdir_parameter(temp_sphinx_app):
    """The resolver accepts `srcdir` now even though this task's
    implementation does not yet consume it -- 53-03's CONF-17/D-08 checks
    need it, and the signature must not churn between waves."""
    app = temp_sphinx_app
    # Passing two different srcdir values must not change the result --
    # confirming this task genuinely performs no srcdir-dependent logic.
    registry_a = resolve_template_registry(app.config, str(app.srcdir))
    registry_b = resolve_template_registry(app.config, "/some/other/path")

    assert registry_a.keys() == registry_b.keys()


def test_template_registry_entry_is_frozen_dataclass():
    """`TemplateRegistryEntry` is a frozen dataclass carrying exactly the
    four fields `render_wrapper()` needs (RESEARCH.md Q1)."""
    entry = TemplateRegistryEntry(
        key="typst", template=None, package=None, template_function=None
    )
    assert entry.key == "typst"

    import dataclasses

    assert dataclasses.is_dataclass(entry)
    field_names = {f.name for f in dataclasses.fields(entry)}
    assert field_names == {"key", "template", "package", "template_function"}

    from dataclasses import FrozenInstanceError

    import pytest

    with pytest.raises(FrozenInstanceError):
        entry.key = "mutated"


# Phase 53 plan 02, Task 2: lock the singular-to-plural promotion with an
# invariant test on render_wrapper()'s OWN source region -- scoped via
# `inspect.getsource(TypstWriter.render_wrapper)`, never the whole of
# writer.py, which legitimately mentions the global config names in its
# module docstring and in OTHER functions (D-11's own `typst_package_imports`
# global read, for instance).

# The three globals render_wrapper() must no longer read directly off
# `config`, per this plan's promotion (D-10: template_function; the
# "typst"-only scoping of `parameter_mapping` is D-11, and typst_package_imports
# is explicitly OUT of this set -- it legitimately stays a global read).
_PROMOTED_GLOBAL_CONFIG_NAMES = (
    "typst_template",
    "typst_package",
    "typst_template_function",
)


def _render_wrapper_source() -> str:
    return inspect.getsource(TypstWriter.render_wrapper)


def _exact_quoted_config_read_matches(source: str, name: str) -> bool:
    """Whether ``source`` contains the EXACT quoted config-attribute name
    ``name``, matched by the name immediately followed by its closing
    quote character (``"typst_template"``) -- never a substring match.
    This is what keeps ``typst_template_mapping`` and
    ``typst_package_imports`` (both of which legitimately REMAIN in
    ``render_wrapper()`` per D-11 and the global-scope decision) from
    being mistaken for a hit on the shorter, promoted names."""
    return f'"{name}"' in source


def test_render_wrapper_reads_none_of_the_three_promoted_globals_by_exact_name():
    """The source region of `TypstWriter.render_wrapper` contains no
    whole-name config read of the three promoted globals
    (`typst_template`/`typst_package`/`typst_template_function`).
    Matching is by exact quoted name, not substring, so
    `typst_template_mapping` and `typst_package_imports` -- both of which
    legitimately REMAIN in this function per D-11 and the global-scope
    decision -- cannot be mistaken for a hit on the shorter names."""
    source = _render_wrapper_source()
    matched = [
        name
        for name in _PROMOTED_GLOBAL_CONFIG_NAMES
        if _exact_quoted_config_read_matches(source, name)
    ]
    assert not matched, (
        "render_wrapper() still reads the following promoted global(s) "
        f"directly off config, by exact quoted name: {matched!r} -- this "
        "reintroduces the singular template-config assumption Phase 53 "
        "promotes to a resolved TemplateRegistryEntry."
    )


def test_render_wrapper_source_contains_template_entry_identifier():
    """The same source region DOES contain the identifier
    `template_entry`, proving the read was REPLACED rather than merely
    deleted."""
    source = _render_wrapper_source()
    assert "template_entry" in source


def test_reserved_key_engine_gets_global_mapping_user_defined_key_gets_none(
    temp_sphinx_app,
):
    """D-11 edge: a `TemplateEngine` built for a user-defined key receives
    `parameter_mapping` `None`, while one built for the `"typst"` key
    receives the value of global `typst_template_mapping` -- asserted by
    constructing both entries and inspecting the engines
    `render_wrapper()` builds."""
    from docutils import nodes
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    app = temp_sphinx_app
    app.config.typst_template_mapping = {"project": "custom_title"}

    reporter = Reporter("", 2, 4)
    doctree = nodes.document("", reporter=reporter)
    doctree.settings = states.Struct()
    doctree += nodes.section()

    writer = TypstWriter(app.builder)

    reserved_entry = TemplateRegistryEntry(
        key=RESERVED_REGISTRY_KEY, template=None, package=None, template_function=None
    )
    user_entry = TemplateRegistryEntry(
        key="report", template=None, package=None, template_function=None
    )

    engines: dict = {}

    original_init = __import__(
        "typsphinx.template_engine", fromlist=["TemplateEngine"]
    ).TemplateEngine.__init__

    def _capture_init(self, *args, **kwargs):
        engines["parameter_mapping"] = kwargs.get("parameter_mapping")
        return original_init(self, *args, **kwargs)

    import typsphinx.template_engine as template_engine_module

    template_engine_module.TemplateEngine.__init__ = _capture_init
    try:
        writer.render_wrapper(
            ("index", "manual.typ", "T", "A"),
            doctree,
            "",
            "index.typ",
            template_entry=reserved_entry,
        )
        reserved_mapping = engines["parameter_mapping"]

        writer.render_wrapper(
            ("index", "manual.typ", "T", "A"),
            doctree,
            "",
            "index.typ",
            template_entry=user_entry,
        )
        user_mapping = engines["parameter_mapping"]
    finally:
        template_engine_module.TemplateEngine.__init__ = original_init

    assert reserved_mapping == {"project": "custom_title"}
    assert user_mapping is None


# ---------------------------------------------------------------------------
# Phase 53 plan 03, Task 1: CONF-18's seven-case key-shape denylist and
# CONF-16's reserved key.
#
# Every definition below is deliberately `{}` (neither `template` nor
# `package`) so these SHAPE-only tests stay valid unmodified once Task 2
# adds CONF-15/CONF-17/D-08 validation on top of the same
# `resolve_template_registry()` -- a definition carrying a `template` value
# pointing at a file that does not exist would start failing D-08's
# existence check the moment Task 2 lands, which is not what these tests
# are pinning.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_key,expected_substring",
    [
        ("", "empty or whitespace-only"),
        ("   ", "empty or whitespace-only"),
        (".", "'.' or '..'"),
        ("..", "'.' or '..'"),
        ("a/b", "path separator"),
        ("a\\b", "path separator"),
        ("CON", "Windows reserved device name"),
        ("nul", "Windows reserved device name"),
        ("CON.txt", "Windows reserved device name"),
        ("COM1", "Windows reserved device name"),
        ("LPT9", "Windows reserved device name"),
        ("foo.", "trailing dot"),
        ("foo ", "trailing space"),
    ],
)
def test_registry_key_shape_denylist_case_raises(
    temp_sphinx_app, bad_key, expected_substring
):
    """CONF-18: each of the seven denylist cases stops the build with a
    message naming that specific reason (D-01/D-02)."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {bad_key: {}}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    assert expected_substring in str(excinfo.value)


def test_registry_two_keys_differing_only_by_case_raises(temp_sphinx_app):
    """CONF-18 case 7: two registry keys differing only by case stop the
    build -- the comparison is performed via `TypstBuilder._collision_key()`
    (ROADMAP SC#4), not a second independently-written casefold."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {
        "Report": {},
        "report": {},
    }

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    assert "only by case" in str(excinfo.value)


@pytest.mark.parametrize(
    "accepted_key",
    [
        "paper:v2",  # Windows-illegal punctuation character
        "key\x01name",  # control character (0x01)
        ".hidden",  # leading dot
        "inner space",  # interior whitespace
    ],
)
def test_registry_key_deliberately_accepted_shapes_resolve_without_raising(
    temp_sphinx_app, accepted_key
):
    """D-02: the four shapes deliberately NOT in the denylist stay accepted
    in Phase 53, pinning that an eighth case cannot be added silently."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {accepted_key: {}}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert accepted_key in registry


@pytest.mark.parametrize("boundary_key", ["COM0", "LPT0", "ICONIC"])
def test_registry_key_reserved_name_boundary_not_rejected(
    temp_sphinx_app, boundary_key
):
    """Negative control: `COM0`/`LPT0` are NOT on the 22-name reserved list
    (D-02's exact citation), and `ICONIC` does not match the whole-stem
    comparison against `CON` (no dot, no whole-string match)."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {boundary_key: {}}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert boundary_key in registry


def test_registry_key_literal_typst_raises(temp_sphinx_app):
    """CONF-16: a user-defined key equal to the literal string `typst`
    stops the build -- it collides with the synthesized built-in key."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {"typst": {}}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    assert "reserved" in str(excinfo.value)


@pytest.mark.parametrize("case_variant_key", ["Typst", "TYPST"])
def test_registry_key_case_variant_of_typst_resolves_without_raising(
    temp_sphinx_app, case_variant_key
):
    """CONF-16/D-04: only the LITERAL string `typst` is reserved --
    `Typst`/`TYPST` pass as ordinary user-defined keys, because the
    case-collision check (case 7) compares REGISTERED keys against each
    other and the synthesized built-in is never a member of that set."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {case_variant_key: {}}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert case_variant_key in registry


def test_key_shape_validator_exposes_exactly_seven_distinct_rejection_reasons():
    """SC#4/T-53-03: the validator's rejection-reason enumeration is
    assertable as exactly seven distinct cases, not merely reviewed --
    pins against both silently loosening the denylist and silently adding
    an eighth case."""
    from typsphinx.template_registry import _KEY_SHAPE_REJECTION_CASES

    assert len(_KEY_SHAPE_REJECTION_CASES) == 7
    assert len(set(_KEY_SHAPE_REJECTION_CASES)) == 7


# ---------------------------------------------------------------------------
# Phase 53 plan 03, Task 2: CONF-15's xor, CONF-17's path arithmetic, and
# D-08's existence check -- accumulated into one raise.
# ---------------------------------------------------------------------------


def test_definition_with_both_template_and_package_raises(temp_sphinx_app):
    """CONF-15: a definition carrying both `template` and `package`
    stops the build."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    (srcdir / "both.typ").write_text("")
    app.config.typst_document_templates = {
        "combo": {"template": "both.typ", "package": "@preview/pkg:0.1.0"}
    }

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    assert "CONF-15" in str(excinfo.value)


@pytest.mark.parametrize(
    "definition",
    [
        {"template": "sub/solo_tpl.typ"},
        {"package": "@preview/pkg:0.1.0"},
        {},
    ],
)
def test_definition_with_template_xor_package_or_neither_resolves(
    temp_sphinx_app, definition
):
    """CONF-15: a definition carrying only `template`, only `package`, or
    neither all resolve without raising."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    (srcdir / "sub").mkdir()
    (srcdir / "sub" / "solo_tpl.typ").write_text("")
    app.config.typst_document_templates = {"solo": definition}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert "solo" in registry


def test_conf17_template_parent_is_srcdir_itself_raises(temp_sphinx_app):
    """CONF-17/D-07 rejection: a `template` whose resolved parent
    directory IS `srcdir` itself."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    (srcdir / "rootfile.typ").write_text("")
    app.config.typst_document_templates = {"bad": {"template": "rootfile.typ"}}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    assert "CONF-17" in str(excinfo.value)


def test_conf17_template_parent_is_ancestor_of_srcdir_raises(temp_sphinx_app):
    """CONF-17/D-07 rejection: a `template` whose resolved parent
    directory is an ANCESTOR of `srcdir`."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    (srcdir.parent / "ancestorfile.typ").write_text("")
    app.config.typst_document_templates = {"bad": {"template": "../ancestorfile.typ"}}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    assert "CONF-17" in str(excinfo.value)


def test_conf17_template_under_subdirectory_of_srcdir_resolves(temp_sphinx_app):
    """CONF-17/D-07 acceptance: a `template` under a SUBDIRECTORY of
    `srcdir` stays legal."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    (srcdir / "sub").mkdir()
    (srcdir / "sub" / "tpl.typ").write_text("")
    app.config.typst_document_templates = {"ok": {"template": "sub/tpl.typ"}}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert "ok" in registry


def test_conf17_template_in_sibling_directory_resolves(temp_sphinx_app):
    """CONF-17/D-07 acceptance: a `template` in a SIBLING directory of
    `srcdir`, reached through `..`, stays legal."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    sibling = srcdir.parent / "sibling"
    sibling.mkdir()
    (sibling / "tpl.typ").write_text("")
    app.config.typst_document_templates = {"ok": {"template": "../sibling/tpl.typ"}}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert "ok" in registry


def test_conf17_absolute_template_path_outside_srcdir_resolves(temp_sphinx_app):
    """CONF-17/D-07 acceptance: an absolute `template` path OUTSIDE
    `srcdir` stays legal."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    external = srcdir.parent / "external"
    external.mkdir()
    external_file = external / "tpl.typ"
    external_file.write_text("")
    app.config.typst_document_templates = {"ok": {"template": str(external_file)}}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert "ok" in registry


def test_conf17_cross_drive_commonpath_valueerror_is_not_a_violation(monkeypatch):
    """53-07 Task 1 / 53-REVIEW.md CR-02: `_violates_conf17()` returns
    `False`, not `True`, when `os.path.commonpath()` raises `ValueError`
    for two absolute paths on different Windows drives.

    This is a deliberate platform-independent simulation of the
    `windows-latest` CI lane's real behaviour, following D-05's precedent
    of validating Windows-shaped input identically on POSIX, rather than
    importing `ntpath`: `template_registry` binds `os` at import time and
    resolves `os.path.commonpath` at call time, so patching that attribute
    reaches the call under test, and `monkeypatch` reverts it afterward.
    """

    def _raise_cross_drive(_paths):
        raise ValueError("Paths don't have the same drive")

    monkeypatch.setattr(os.path, "commonpath", _raise_cross_drive)

    assert _violates_conf17("/elsewhere/tpl.typ", "/some/srcdir") is False


def test_conf17_cross_drive_valueerror_surfaces_as_extension_error_not_valueerror(
    temp_sphinx_app, monkeypatch
):
    """53-07 Task 1 / 53-REVIEW.md CR-02: with `os.path.commonpath()`
    monkeypatched to raise `ValueError` (simulating the `windows-latest`
    CI lane's real cross-drive behaviour, per D-05's POSIX-simulation
    precedent), a registry declaring an absolute `template` path under a
    directory that does not exist still raises this module's own
    `ExtensionError` (D-08's not-found failure) -- never a raw
    `ValueError` escaping as an internal exception.
    """
    app = temp_sphinx_app

    def _raise_cross_drive(_paths):
        raise ValueError("Paths don't have the same drive")

    monkeypatch.setattr(os.path, "commonpath", _raise_cross_drive)
    app.config.typst_document_templates = {
        "cross_drive": {"template": "/nonexistent_dir_xyz/tpl.typ"}
    }

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    assert "does not exist" in str(excinfo.value)


def test_user_defined_key_template_names_nonexistent_file_raises(temp_sphinx_app):
    """D-08: a user-defined key whose `template` names a file that does
    not exist stops the build."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {
        "missing": {"template": "does_not_exist.typ"}
    }

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    assert "does not exist" in str(excinfo.value)
    assert "typst_document_templates" in str(excinfo.value)


def test_builtin_typst_key_nonexistent_global_template_does_not_raise(
    temp_sphinx_app,
):
    """D-08: the built-in `typst` key's not-found path is UNCHECKED by
    this module -- it keeps reaching `resolve_template()`'s existing
    warn-and-fall-back behaviour unchanged. No `typst_document_templates`
    entry is declared here, so the only source of a "does the file exist"
    question is the SYNTHESIZED built-in key, which this module must never
    raise for."""
    app = temp_sphinx_app
    app.config.typst_template = "no_such_global_tpl.typ"

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert registry[RESERVED_REGISTRY_KEY].template == "no_such_global_tpl.typ"


def test_conf17_and_not_found_both_reported_in_one_raise(temp_sphinx_app):
    """D-09: one user-defined key whose `template` BOTH violates CONF-17
    AND names a nonexistent file produces a SINGLE `ExtensionError` whose
    message contains BOTH reasons."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {
        "both_broken": {"template": "rootfile_missing.typ"}
    }

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    message = str(excinfo.value)
    assert "CONF-17" in message
    assert "does not exist" in message


def test_three_independently_broken_keys_raise_once_order_independently(
    temp_sphinx_app,
):
    """D-03/D-05: a registry with three independently-broken keys
    produces exactly ONE `ExtensionError` naming all three, and the
    message text is byte-identical across two runs with the keys declared
    in a DIFFERENT `dict` insertion order -- proving the accumulation
    iterates via `sorted()`, not raw insertion order."""
    app = temp_sphinx_app

    # "missing"'s template lives under a subdirectory so its ONLY failure
    # is D-08's not-found check -- a bare top-level filename would ALSO
    # trip CONF-17 (parent == srcdir), which would make this test's exact
    # "3 invalid" count entangled with a second, unrelated validation
    # rule.
    forward = {
        "bad/slash": {},
        "typst": {},
        "missing": {"template": "sub/does_not_exist.typ"},
    }
    app.config.typst_document_templates = forward
    with pytest.raises(ExtensionError) as excinfo_forward:
        resolve_template_registry(app.config, str(app.srcdir))
    message_forward = str(excinfo_forward.value)

    reordered = {
        "missing": {"template": "sub/does_not_exist.typ"},
        "typst": {},
        "bad/slash": {},
    }
    app.config.typst_document_templates = reordered
    with pytest.raises(ExtensionError) as excinfo_reordered:
        resolve_template_registry(app.config, str(app.srcdir))
    message_reordered = str(excinfo_reordered.value)

    assert message_forward == message_reordered
    assert "'bad/slash'" in message_forward
    assert "'missing'" in message_forward
    assert "'typst'" in message_forward
    assert message_forward.startswith("typst_document_templates: 3 invalid")


# ---------------------------------------------------------------------------
# Phase 53 plan 07, Task 2: a non-`str` registry key and a truthy non-`dict`
# definition each join the accumulate-then-raise-once pass instead of
# crashing with a raw `AttributeError`/`TypeError` (53-REVIEW.md WR-02,
# WR-03; 53-VERIFICATION.md Anti-Patterns row 3).
# ---------------------------------------------------------------------------


def test_non_str_registry_key_raises_extension_error_not_attributeerror(
    temp_sphinx_app,
):
    """53-REVIEW.md WR-02 / 53-VERIFICATION.md Anti-Patterns row 3: a
    non-`str` registry key (e.g. an `int`) stops the build with this
    module's own `ExtensionError` naming the offending key, never a raw
    `AttributeError` from `key.strip()`."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {42: {}}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    message = str(excinfo.value)
    assert "is not a string" in message
    assert "42" in message


def test_non_dict_definition_raises_extension_error_not_attributeerror(
    temp_sphinx_app,
):
    """53-REVIEW.md WR-03: a truthy non-`dict` registry definition (a bare
    string) stops the build with this module's own `ExtensionError` naming
    the offending value, never a raw `AttributeError` from
    `definition.get(...)`."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {"bad_def": "not_a_dict"}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    message = str(excinfo.value)
    assert "must be a dict" in message
    assert "'not_a_dict'" in message


@pytest.mark.parametrize("falsy_definition", [None, "", 0])
def test_falsy_definition_still_normalizes_and_resolves(
    temp_sphinx_app, falsy_definition
):
    """53-REVIEW.md WR-03: a FALSY definition (`None`, `""`, `0`) still
    normalizes to an empty definition and resolves without raising -- the
    new non-`dict` guard only rejects TRUTHY non-`dict` values, exactly as
    it does today."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {"falsy": falsy_definition}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert registry["falsy"].template is None
    assert registry["falsy"].package is None
    assert registry["falsy"].template_function is None


def test_mixed_type_keys_raise_extension_error_not_sorted_typeerror(
    temp_sphinx_app,
):
    """53-REVIEW.md WR-02: a registry mixing an `int` key with a `str` key
    raises this module's `ExtensionError`, never the `TypeError`
    `sorted()` raises when it compares an `int` to a `str` -- the
    iteration key is total across mixed types."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {99: {}, "bad/slash": {}}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    message = str(excinfo.value)
    assert "is not a string" in message
    assert "path separator" in message


def test_mixed_type_key_message_is_byte_identical_across_insertion_orders(
    temp_sphinx_app,
):
    """TPL-01 ordering edge / D-03: the same malformed registry, declared
    in two different `dict` insertion orders -- including a mixed-type key
    set -- yields a byte-identical `ExtensionError` message, extending
    D-03's determinism guarantee over the new total iteration key."""
    app = temp_sphinx_app

    forward = {99: {}, "bad/slash": {}, "typst": {}}
    app.config.typst_document_templates = forward
    with pytest.raises(ExtensionError) as excinfo_forward:
        resolve_template_registry(app.config, str(app.srcdir))
    message_forward = str(excinfo_forward.value)

    reordered = {"typst": {}, "bad/slash": {}, 99: {}}
    app.config.typst_document_templates = reordered
    with pytest.raises(ExtensionError) as excinfo_reordered:
        resolve_template_registry(app.config, str(app.srcdir))
    message_reordered = str(excinfo_reordered.value)

    assert message_forward == message_reordered


def test_non_str_key_is_excluded_from_case_collision_comparison(temp_sphinx_app):
    """CONF-18 encoding edge (53-07 must_haves): a non-`str` key never
    reaches `TypstBuilder._collision_key()` -- `all_keys` stays
    `isinstance(key, str)`-filtered, so a registry mixing a non-`str` key
    with two case-colliding `str` keys reports BOTH failures in the one
    accumulated raise, proving the non-`str` key is excluded from CONF-18's
    case-collision comparison rather than crashing it."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {7: {}, "Report": {}, "report": {}}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    message = str(excinfo.value)
    assert "is not a string" in message
    assert "only by case" in message


# ---------------------------------------------------------------------------
# Phase 53 plan 08, Task 2: a truthy unusable `template` field joins the
# accumulate-then-raise-once pass instead of crashing with a raw `TypeError`
# from `os.path.join()` (53-REVIEW.md WR-02; 53-VERIFICATION.md
# Anti-Patterns row 3). Pre-fix RED transcript recorded in
# `.planning/phases/53-template-registry-foundation/53-08-RED-EVIDENCE.md`.
# ---------------------------------------------------------------------------


def test_non_path_template_field_raises_extension_error_not_typeerror(
    temp_sphinx_app,
):
    """Test F / 53-REVIEW.md WR-02: a definition whose `template` is
    `["a", "b"]` raises `ExtensionError` whose message contains `must be a
    path string` and the `repr` of the offending value; no `TypeError`
    escapes."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {"bad_tpl": {"template": ["a", "b"]}}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    message = str(excinfo.value)
    assert "must be a path string" in message
    assert repr(["a", "b"]) in message


def test_bytes_template_field_raises_extension_error_not_typeerror(temp_sphinx_app):
    """Test G: a definition whose `template` is `b"base.typ"` (bytes --
    the other value `os.path.join` refuses against a `str` srcdir) raises
    the same `ExtensionError` class with the same message shape."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {"bad_tpl": {"template": b"base.typ"}}

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    message = str(excinfo.value)
    assert "must be a path string" in message
    assert repr(b"base.typ") in message


def test_pathlike_template_field_still_resolves(temp_sphinx_app):
    """Test H (control): a definition whose `template` is a `pathlib.Path`
    pointing at a real file inside a subdirectory of `srcdir` resolves
    WITHOUT raising, and the resolved entry's `template` is that same
    `Path` -- proving the guard did not withdraw a working shape."""
    app = temp_sphinx_app
    srcdir = Path(str(app.srcdir))
    (srcdir / "sub").mkdir()
    tpl_path = srcdir / "sub" / "path_tpl.typ"
    tpl_path.write_text("")
    declared_template = Path("sub/path_tpl.typ")
    app.config.typst_document_templates = {"pathlike": {"template": declared_template}}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert registry["pathlike"].template == declared_template
    assert isinstance(registry["pathlike"].template, Path)


@pytest.mark.parametrize("falsy_template", [None, "", 0, []])
def test_falsy_template_field_still_resolves_verbatim(temp_sphinx_app, falsy_template):
    """Test I (parametrized control): a FALSY `template` -- `None`, `""`,
    `0`, `[]` -- still resolves without raising, and the resolved entry's
    `template` is that value verbatim, exactly as measured at HEAD."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {"falsy_tpl": {"template": falsy_template}}

    registry = resolve_template_registry(app.config, str(app.srcdir))

    assert registry["falsy_tpl"].template == falsy_template


def test_bad_typed_template_and_package_both_reported_in_one_raise(temp_sphinx_app):
    """Test J / D-09: a definition carrying BOTH a bad-typed `template`
    and a `package` reports BOTH the CONF-15 both-set failure and the
    type failure in the one accumulated raise."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {
        "combo_bad": {"template": ["a", "b"], "package": "@preview/pkg:0.1.0"}
    }

    with pytest.raises(ExtensionError) as excinfo:
        resolve_template_registry(app.config, str(app.srcdir))

    message = str(excinfo.value)
    assert "CONF-15" in message
    assert "must be a path string" in message


def test_bad_typed_template_message_is_byte_identical_across_insertion_orders(
    temp_sphinx_app,
):
    """Test K: the same registry -- a bad-typed `template` on one key plus
    an independently-broken second key -- declared in two different `dict`
    insertion orders yields two byte-identical message strings."""
    app = temp_sphinx_app

    forward = {
        "bad_tpl": {"template": ["a", "b"]},
        "bad/slash": {},
    }
    app.config.typst_document_templates = forward
    with pytest.raises(ExtensionError) as excinfo_forward:
        resolve_template_registry(app.config, str(app.srcdir))
    message_forward = str(excinfo_forward.value)

    reordered = {
        "bad/slash": {},
        "bad_tpl": {"template": ["a", "b"]},
    }
    app.config.typst_document_templates = reordered
    with pytest.raises(ExtensionError) as excinfo_reordered:
        resolve_template_registry(app.config, str(app.srcdir))
    message_reordered = str(excinfo_reordered.value)

    assert message_forward == message_reordered


# ---------------------------------------------------------------------------
# Phase 53 plan 03, Task 3: CONF-14's unregistered key and D-06's non-str
# element [4].
# ---------------------------------------------------------------------------


def test_resolve_registry_key_unregistered_key_raises_naming_registered_keys(
    temp_sphinx_app,
):
    """CONF-14: a `typst_documents` entry whose element [4] names a key
    absent from the resolved registry raises `ExtensionError`, and the
    message contains the sorted resolved registry keys."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {"paper": {}}
    registry = resolve_template_registry(app.config, str(app.srcdir))
    entry = ("index", "manual.typ", "T", "A", "nonexistent")

    with pytest.raises(ExtensionError) as excinfo:
        resolve_registry_key(registry, entry)

    message = str(excinfo.value)
    assert "nonexistent" in message
    assert "['paper', 'typst']" in message


def test_resolve_registry_key_empty_registry_lists_typst_not_empty_list(
    temp_sphinx_app,
):
    """CONF-14 empty edge: with `typst_document_templates` empty, the
    message lists `['typst']` -- the sorted resolved keys -- never an
    empty list."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {}
    registry = resolve_template_registry(app.config, str(app.srcdir))
    entry = ("index", "manual.typ", "T", "A", "nonexistent")

    with pytest.raises(ExtensionError) as excinfo:
        resolve_registry_key(registry, entry)

    assert "['typst']" in str(excinfo.value)


def test_resolve_registry_key_lookup_is_exact_str_equality_not_casefolded(
    temp_sphinx_app,
):
    """CONF-14 encoding edge: a registry declaring `Paper` does not
    satisfy an entry naming `paper`; the lookup is exact `str` equality,
    never case-folded."""
    app = temp_sphinx_app
    app.config.typst_document_templates = {"Paper": {}}
    registry = resolve_template_registry(app.config, str(app.srcdir))
    entry = ("index", "manual.typ", "T", "A", "paper")

    with pytest.raises(ExtensionError) as excinfo:
        resolve_registry_key(registry, entry)

    assert "'paper'" in str(excinfo.value)


@pytest.mark.parametrize("bad_value", [None, 123, ("a", "b")])
def test_resolve_registry_key_non_str_element_four_raises(temp_sphinx_app, bad_value):
    """D-06: an element [4] that is PRESENT but not a `str` -- `None`, an
    int, and a tuple -- each raises the same class of error, naming the
    offending value and the registered keys. It is neither tolerated-and-
    skipped nor coerced to the built-in key."""
    app = temp_sphinx_app
    registry = resolve_template_registry(app.config, str(app.srcdir))
    entry = ("index", "manual.typ", "T", "A", bad_value)

    with pytest.raises(ExtensionError) as excinfo:
        resolve_registry_key(registry, entry)

    message = str(excinfo.value)
    assert repr(bad_value) in message
    assert "['typst']" in message


def test_resolve_registry_key_absent_element_four_still_resolves_to_typst(
    temp_sphinx_app,
):
    """TPL-04 regression: an absent element [4] (a four-element tuple)
    still resolves to the built-in key without raising -- Task 3's D-06
    branch must not regress plan 53-02's behaviour."""
    app = temp_sphinx_app
    registry = resolve_template_registry(app.config, str(app.srcdir))
    entry = ("index", "manual.typ", "T", "A")

    resolved = resolve_registry_key(registry, entry)

    assert resolved is registry[RESERVED_REGISTRY_KEY]


def test_resolve_registry_key_bad_key_fails_identically_regardless_of_master_order(
    temp_sphinx_app,
):
    """SC#3: a multi-master `typst_documents` with two masters, one of
    them naming a bad key, fails identically whichever master would have
    been written first."""
    app = temp_sphinx_app
    registry = resolve_template_registry(app.config, str(app.srcdir))
    good_entry = ("index", "manual.typ", "T", "A")
    bad_entry = ("other", "other.typ", "T2", "A2", "does_not_exist")

    # Simulate "the bad master would have been written FIRST": resolve it,
    # then resolve the good one (which never raises).
    with pytest.raises(ExtensionError) as excinfo_bad_first:
        resolve_registry_key(registry, bad_entry)
    resolve_registry_key(registry, good_entry)
    message_bad_first = str(excinfo_bad_first.value)

    # Simulate "the bad master would have been written SECOND": resolve
    # the good one first, then the bad one.
    resolve_registry_key(registry, good_entry)
    with pytest.raises(ExtensionError) as excinfo_bad_second:
        resolve_registry_key(registry, bad_entry)
    message_bad_second = str(excinfo_bad_second.value)

    assert message_bad_first == message_bad_second

"""Tests for `typsphinx.template_registry` (Phase 53, plans 53-02/53-03).

In-process unit style, following
`tests/test_builder_output_stem.py::test_validate_output_path_collisions_raises_on_docname_collision`
(391-416): a `temp_sphinx_app` fixture, a directly-constructed `TypstBuilder`,
and direct calls into the module under test -- no subprocess build.
"""

import inspect

import pytest
from sphinx.errors import ExtensionError

from typsphinx.template_registry import (
    RESERVED_REGISTRY_KEY,
    TemplateRegistryEntry,
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
    app.config.typst_template_function = "global_project_fn"
    app.config.typst_document_templates = {"custom": {"template": "custom.typ"}}

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

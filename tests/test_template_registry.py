"""Tests for `typsphinx.template_registry` (Phase 53, plan 53-02).

In-process unit style, following
`tests/test_builder_output_stem.py::test_validate_output_path_collisions_raises_on_docname_collision`
(391-416): a `temp_sphinx_app` fixture, a directly-constructed `TypstBuilder`,
and direct calls into the module under test -- no subprocess build.
"""

import inspect

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

    import pytest
    from dataclasses import FrozenInstanceError

    with pytest.raises(FrozenInstanceError):
        entry.key = "mutated"

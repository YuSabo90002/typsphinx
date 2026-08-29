"""
MSG-05's gate: ``typsphinx/template_registry.py``'s two path-valued
``template`` interpolations -- the CONF-17 violation message and the
existence-check message -- route through ``quote_path()``.

Both routed sites raise ``sphinx.errors.ExtensionError``, so the only
observable this module asserts on is ``str(excinfo.value)`` (D-12). D-12
gives this site TWO independent RED shapes: a doubled backslash for a
``str`` template (the same shape every other still-``!r`` site in the
codebase gets), and a leaked ``pathlib`` class-name wrapper
(``PosixPath(...)``) for a ``Path`` template -- a shape with NO existing
coverage anywhere in the suite before this module.

This module asserts ONLY on strings ``typsphinx/template_registry.py``
itself emits -- never on a string emitted by ``builder.py`` or
``writer.py``, which belong to the sibling wave-2 plans (60-02, 60-03).

``TestRegistryTypeCheckMessageStaysReprQuoted`` is SC#3's exclusion
control: it drives the type-check branch (reached when ``template`` is
NOT ``str`` and NOT ``os.PathLike``) and must stay GREEN both before and
after MSG-05's fix -- that branch is deliberately left on Python's own
``repr()`` conversion, because routing it through ``quote_path()`` would
misrepresent a ``list``/``bytes`` value as a filesystem location AND
raise ``TypeError`` on the exact values it exists to report.
"""

import pathlib
import re

import pytest
from sphinx.errors import ExtensionError

from typsphinx.template_registry import resolve_template_registry


def _assert_no_doubled_separator(message: str) -> None:
    """No run of consecutive backslashes longer than 1 may appear -- that
    is what ``repr()`` escaping would produce and what this local guard
    exists to catch. Re-derived here (not imported) so this module makes
    no cross-import into ``tests/test_templates_path_collision_gate.py``,
    which is the ``builder.py`` wiring plan's exclusive privilege (D-11)."""
    doubled = re.findall(r"\\\\+", message)
    assert not doubled, (
        f"Expected every backslash run to be a single unescaped "
        f"separator, found a doubled/escaped run in:\n{message!r}"
    )


class TestRegistryTemplatePathQuoting:
    """RED shape 1 (D-12): a Windows-shaped ``str`` template's message
    must show single, unescaped separators -- never a doubled run, which
    is what ``!r``'s backslash-doubling produces today."""

    def test_conf17_violation_message_has_no_doubled_separator(
        self, temp_sphinx_app
    ):
        """A Windows-shaped ``str`` template whose join with ``srcdir``
        leaves the parent directory equal to ``srcdir`` itself fires the
        CONF-17 branch (a plain filename component has no separator that
        moves it below ``srcdir`` on a POSIX host, since a backslash is
        not a path separator there). The existence check also fires,
        since the file cannot exist -- both failures accumulate in one
        raise (D-09)."""
        app = temp_sphinx_app
        template = "C:\\Users\\runner\\base.typ"
        app.config.typst_document_templates = {"mykey": {"template": template}}

        with pytest.raises(ExtensionError) as excinfo:
            resolve_template_registry(app.config, str(app.srcdir))

        message = str(excinfo.value)
        assert "CONF-17" in message
        _assert_no_doubled_separator(message)
        assert template in message

    def test_existence_check_message_has_no_doubled_separator(
        self, temp_sphinx_app
    ):
        """A Windows-shaped ``str`` template prefixed with a forward-slash
        path component (``_typst/nested/...``) moves its resolved parent
        directory BELOW ``srcdir``, so the CONF-17 branch does NOT fire --
        only the existence-check branch does, since the file still cannot
        exist."""
        app = temp_sphinx_app
        template = "_typst/nested/C:\\Users\\runner\\base.typ"
        app.config.typst_document_templates = {"mykey": {"template": template}}

        with pytest.raises(ExtensionError) as excinfo:
            resolve_template_registry(app.config, str(app.srcdir))

        message = str(excinfo.value)
        assert "does not exist" in message
        _assert_no_doubled_separator(message)
        assert "CONF-17" not in message


class TestRegistryPathLikeTemplateNoClassWrapper:
    """RED shape 2 (D-12): a nonexistent ``pathlib.Path`` template's
    existence-check message must not leak Python's internal
    ``PosixPath(...)``/``WindowsPath(...)`` class-name wrapper. There is
    NO existing coverage anywhere in the suite for this shape before this
    module -- ``tests/test_template_registry.py``'s only ``Path``-typed
    template test (``test_pathlike_template_field_still_resolves``) is a
    control proving a ``Path`` template is a deliberately SUPPORTED shape
    that resolves without raising, which is exactly why leaking Python's
    internal representation when it does NOT resolve is a real
    user-facing defect and not a hypothetical."""

    def test_pathlike_template_existence_message_leaks_no_class_wrapper(
        self, temp_sphinx_app
    ):
        app = temp_sphinx_app
        template = pathlib.Path("/some/path/_templates/nested/base.typ")
        app.config.typst_document_templates = {"mykey": {"template": template}}

        with pytest.raises(ExtensionError) as excinfo:
            resolve_template_registry(app.config, str(app.srcdir))

        message = str(excinfo.value)
        assert "does not exist" in message
        assert str(template) in message
        assert "PosixPath" not in message


class TestRegistryTypeCheckMessageStaysReprQuoted:
    """SC#3's exclusion control. This class must be GREEN both BEFORE and
    AFTER MSG-05's fix -- the type-check branch (reached when ``template``
    is neither ``str`` nor ``os.PathLike``) is deliberately left on
    Python's own ``repr()`` conversion. Routing it through ``quote_path()``
    would both misrepresent a ``list``/``bytes`` value as a filesystem
    location AND raise ``TypeError`` on the exact values this branch
    exists to report -- SC#3 makes leaving it alone a MEASURED pass
    criterion rather than an oversight. Method names contain the token
    ``type_check_message_stays_repr_quoted`` so
    ``-k type_check_message_stays_repr_quoted`` selects exactly this
    class."""

    def test_list_template_type_check_message_stays_repr_quoted(
        self, temp_sphinx_app
    ):
        app = temp_sphinx_app
        template = ["a", "b"]
        app.config.typst_document_templates = {"bad_tpl": {"template": template}}

        with pytest.raises(ExtensionError) as excinfo:
            resolve_template_registry(app.config, str(app.srcdir))

        message = str(excinfo.value)
        assert "must be a path string" in message
        expected_repr = repr(template)
        assert expected_repr in message

    def test_bytes_template_type_check_message_stays_repr_quoted(
        self, temp_sphinx_app
    ):
        app = temp_sphinx_app
        template = b"base.typ"
        app.config.typst_document_templates = {"bad_tpl": {"template": template}}

        with pytest.raises(ExtensionError) as excinfo:
            resolve_template_registry(app.config, str(app.srcdir))

        message = str(excinfo.value)
        assert "must be a path string" in message
        expected_repr = repr(template)
        assert expected_repr in message

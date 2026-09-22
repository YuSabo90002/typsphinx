"""
QUA-14/Phase 74: the whole-tree census guard that keeps typsphinx's own
docstrings free of the two docutils message classes the phase cleared.

Requirement QUA-14 asks that a clean ``-b typst`` build of ``docs/source`` stop
reporting the docutils ``Unexpected indentation`` / ``Block quote ends without
a blank line`` message class raised by typsphinx's *own* docstrings. Phase 74
repaired the two docstrings that raised them (``typsphinx.pathfmt.quote_path``
and ``typsphinx.translator.TypstTranslator.visit_toctree``) by adding blank
lines only, and proved the result with one-shot clean-build evidence
(74-BASE-EVIDENCE.md, 74-QUA14-EVIDENCE.md, 74-TIP-EVIDENCE.md). Evidence files
do not run in CI. This module is what makes a reintroduction *detectable*
rather than hypothetical.

Why the docstring -> napoleon -> docutils route rather than a docs build?

1. It is the same route 74-01's scratch probe used to attribute the census to a
   named docstring, so the guard measures exactly what the evidence measured.
2. It needs only ``sphinx`` and ``docutils``, both in the ``dev`` extra. A
   ``-b typst docs/source`` build would need the ``docs`` extra (``myst_parser``,
   ``furo``), which worktree venvs provisioned with ``--extra dev`` alone do not
   have -- the guard would silently skip exactly where it is needed most.
3. It runs in well under a second, so it can sit in the ordinary suite.

Why a *census* rather than two named assertions: the requirement is whole-tree.
A guard that only re-checked the two docstrings Phase 74 happened to repair
would pass while a third docstring reintroduced the same defect. The sweep is
therefore derived from the package on disk:
``test_sweep_covers_every_package_module`` locks the swept module set to
``typsphinx/*.py``, so a module added later cannot quietly fall outside the
census, and ``test_sweep_reaches_the_qua14_anchor_docstrings`` pins the three
docstrings whose coverage the requirement names, so the sweep cannot go vacuous
while still reporting green.

The sweep root is derived from the imported package's own location, never from
the process working directory, so the guard is invariant to where pytest is
invoked from (the D-09 discipline of ``test_repr_census_guard.py``).

Only a docstring an object defines *itself* is judged. ``inspect.getdoc`` would
inherit a base class's docstring from third-party code (docutils'
``NodeVisitor``, for one), and typsphinx cannot fix a docstring it does not own.
``__doc__`` plus ``inspect.cleandoc`` reads the same text without the MRO walk.
"""

import contextlib
import importlib
import inspect
import io
import pathlib
import pkgutil
from collections.abc import Iterator
from typing import Any

from docutils.core import publish_doctree
from docutils.parsers.rst import directives, roles
from docutils.utils import SystemMessage
from sphinx.ext.napoleon import Config, GoogleDocstring

import typsphinx

# The two message classes QUA-14 names. Both are docutils warnings, not errors,
# which is why a docs build reports them without failing.
FORBIDDEN_MESSAGE_CLASSES: frozenset[str] = frozenset(
    {
        "Unexpected indentation",
        "Block quote ends without a blank line",
    }
)

# Derived from the imported package, never from the process working directory.
PACKAGE_ROOT = pathlib.Path(typsphinx.__file__).resolve().parent

# The docstrings whose coverage QUA-14 turns on: the two Phase 74 repaired, plus
# the one member of ``typsphinx/__init__.py`` that carries a docstring -- the
# package module is not a submodule, so a walk that forgets to seed itself with
# it drops a whole source file out of the census without changing any count.
ANCHOR_QUALNAMES: frozenset[str] = frozenset(
    {
        "typsphinx.setup",
        "typsphinx.pathfmt.quote_path",
        "typsphinx.translator.TypstTranslator.visit_toctree",
    }
)

_NAPOLEON_CONFIG = Config(napoleon_use_param=True, napoleon_use_rtype=True)


@contextlib.contextmanager
def _bare_docutils_registry() -> Iterator[None]:
    """
    Parse with docutils' directive/role registries emptied, then restore them.

    Sphinx registers its directives into docutils' *global* registry, and a
    Sphinx app built by an earlier test in the same process leaks them (the
    suite does not wrap every build in ``sphinx.util.docutils.docutils_namespace``).
    A ``SphinxDirective`` invoked from a bare ``publish_doctree`` then reaches for
    ``self.state.document.settings.env``, which does not exist, and raises
    ``AttributeError`` mid-parse -- so this module's verdict would depend on test
    ordering: green alone, exploding in the full suite. ``typsphinx/pdf.py``'s
    ``.. deprecated::`` is the live instance of this.

    Emptying the registries makes every such construct an ordinary
    "Unknown directive type" / "Unknown interpreted text role" docutils error --
    neither of them a class this guard matches -- so the census reads the same
    whether it runs first, last, or by itself. Catching the ``AttributeError``
    instead would be worse than the disease: the parse aborts part-way, the
    remaining lines of that docstring are never checked, and the guard reports
    green on a docstring it only half read.
    """
    saved_directives = dict(directives._directives)
    saved_roles = dict(roles._roles)
    directives._directives.clear()
    roles._roles.clear()
    try:
        yield
    finally:
        directives._directives.clear()
        directives._directives.update(saved_directives)
        roles._roles.clear()
        roles._roles.update(saved_roles)


def _docutils_messages(docstring: str) -> str:
    """
    Convert one docstring through napoleon and parse it with docutils, returning
    the captured system-message text (empty when the docstring parses cleanly).
    """
    converted = str(GoogleDocstring(docstring, _NAPOLEON_CONFIG))
    stream = io.StringIO()
    with _bare_docutils_registry():
        try:
            publish_doctree(
                converted,
                settings_overrides={
                    "report_level": 2,  # WARNING and above
                    "halt_level": 5,  # never raise on a message
                    "warning_stream": stream,
                    "traceback": True,
                },
            )
        except SystemMessage:
            # halt_level 5 makes this unreachable for the classes under test, but
            # a genuinely fatal construct must not abort the whole sweep.
            pass
    return stream.getvalue()


def _iter_modules() -> Iterator[Any]:
    """
    Yield the ``typsphinx`` package itself and every submodule.

    ``pkgutil.walk_packages`` yields submodules only, so ``typsphinx/__init__.py``
    has to be seeded explicitly. An unimportable module raises here rather than
    being skipped -- a census that swallows import errors reports green by
    measuring nothing.
    """
    yield typsphinx
    for module_info in pkgutil.walk_packages(typsphinx.__path__, "typsphinx."):
        yield importlib.import_module(module_info.name)


def _own_docstring(obj: Any) -> str | None:
    """Return the docstring ``obj`` defines itself, cleaned, or None."""
    raw = getattr(obj, "__doc__", None)
    if not raw or not isinstance(raw, str):
        return None
    return inspect.cleandoc(raw)


def _iter_docstrings() -> Iterator[tuple[str, str]]:
    """Yield ``(dotted qualname, docstring)`` for every docstring in the package."""
    for module in _iter_modules():
        module_doc = _own_docstring(module)
        if module_doc:
            yield module.__name__, module_doc

        for name, obj in inspect.getmembers(module):
            if getattr(obj, "__module__", None) != module.__name__:
                continue

            doc = _own_docstring(obj)
            if doc:
                yield f"{module.__name__}.{name}", doc

            if not inspect.isclass(obj):
                continue
            for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                if getattr(method, "__module__", None) != module.__name__:
                    continue
                method_doc = _own_docstring(method)
                if method_doc:
                    yield f"{module.__name__}.{name}.{method_name}", method_doc


def _collect_offenders() -> dict[tuple[str, str], str]:
    """
    Sweep the package and return ``{(qualname, message_class): message text}``
    for every docstring that raises one of the forbidden classes.
    """
    offenders: dict[tuple[str, str], str] = {}
    for qualname, docstring in _iter_docstrings():
        messages = _docutils_messages(docstring)
        if not messages:
            continue
        for message_class in FORBIDDEN_MESSAGE_CLASSES:
            if message_class in messages:
                offenders[(qualname, message_class)] = messages
    return offenders


def test_no_typsphinx_docstring_raises_a_forbidden_message_class() -> None:
    """
    QUA-14: the census of forbidden (qualname, message class) pairs is empty.

    The assertion is emptiness, not a recorded total -- there is no number here
    to bump. A failure names every offending docstring and quotes the docutils
    message so the fix is a blank line away, not a bisect away.
    """
    offenders = _collect_offenders()

    report = "\n".join(
        f"  {qualname}: {message_class}\n"
        + "\n".join(f"    {line}" for line in messages.strip().splitlines())
        for (qualname, message_class), messages in sorted(offenders.items())
    )
    assert not offenders, (
        f"{len(offenders)} typsphinx docstring/message-class pair(s) raise a "
        f"QUA-14 forbidden message class:\n{report}"
    )


def test_sweep_covers_every_package_module() -> None:
    """
    The swept module set equals ``typsphinx/*.py`` on disk.

    This is the non-vacuity floor. A count floor would not catch the failure
    that matters: ``typsphinx/__init__.py`` is not a submodule, so a sweep that
    only walks ``pkgutil.walk_packages`` silently omits a whole source file
    while every other number stays the same.
    """
    expected = {
        "typsphinx" if path.name == "__init__.py" else f"typsphinx.{path.stem}"
        for path in PACKAGE_ROOT.glob("*.py")
    }
    swept = {module.__name__ for module in _iter_modules()}

    assert swept == expected, (
        f"sweep does not match the package on disk; "
        f"missing: {sorted(expected - swept)}, unexpected: {sorted(swept - expected)}"
    )


def test_sweep_reaches_the_qua14_anchor_docstrings() -> None:
    """The three docstrings QUA-14 turns on are actually visited by the sweep."""
    swept = {qualname for qualname, _ in _iter_docstrings()}
    missing = ANCHOR_QUALNAMES - swept

    assert not missing, (
        f"the sweep no longer reaches {sorted(missing)}; the census is reporting "
        f"green on docstrings it never read"
    )


# --- detector self-tests -------------------------------------------------
#
# The census above is only as good as its detector. A guard whose detector has
# quietly stopped firing reports green by measuring nothing, which is the same
# outcome as no guard at all. The sample below carries the defect on purpose, in
# the exact shape the two repaired docstrings had: a paragraph, then a list with
# no blank line between (so docutils reads the bullets as paragraph text), then
# a two-space continuation line -- which is the indentation docutils does not
# expect -- and finally a dedent back out of it.

SAMPLE_WITH_DEFECT = """Summary line.

Delimiter rule, applied to the normalized string:
- apostrophe present, no double quote -> wrap in double quotes
  so an embedded apostrophe cannot close the delimiter early
- both quote characters present -> wrap in apostrophes

Trailing paragraph.
"""

# The Phase 74 repair, applied to that sample: one blank line, nothing else.
SAMPLE_REPAIRED = SAMPLE_WITH_DEFECT.replace(
    "normalized string:\n-", "normalized string:\n\n-"
)


def test_detector_fires_on_unexpected_indentation() -> None:
    """The detector reports ``Unexpected indentation`` for a sample that has it."""
    messages = _docutils_messages(SAMPLE_WITH_DEFECT)

    assert "Unexpected indentation" in messages, (
        f"sample no longer reproduces the message class; detector unproven.\n"
        f"docutils said:\n{messages}"
    )


def test_detector_fires_on_block_quote_without_blank_line() -> None:
    """The detector reports the block-quote class for a sample that has it."""
    messages = _docutils_messages(SAMPLE_WITH_DEFECT)

    assert "Block quote ends without a blank line" in messages, (
        f"sample no longer reproduces the message class; detector unproven.\n"
        f"docutils said:\n{messages}"
    )


def test_census_survives_a_leaked_sphinx_directive() -> None:
    """
    A Sphinx directive left in docutils' global registry by an earlier test does
    not break the census.

    Without ``_bare_docutils_registry`` this raises ``AttributeError`` from
    ``SphinxDirective.env`` and the sweep dies part-way through a docstring --
    the exact full-suite-only failure this module is built to not have.
    """
    from sphinx.util.docutils import SphinxDirective

    class _LeakyDirective(SphinxDirective):  # type: ignore[misc]
        has_content = True

        def run(self) -> list[Any]:
            _ = self.env  # the attribute a bare docutils parse cannot supply
            return []

    directives.register_directive("qua14-leak-probe", _LeakyDirective)
    try:
        messages = _docutils_messages(SAMPLE_WITH_DEFECT + "\n.. qua14-leak-probe::\n")
    finally:
        directives._directives.pop("qua14-leak-probe", None)

    assert "Unexpected indentation" in messages, (
        f"the leaked directive changed what the census can see.\n"
        f"docutils said:\n{messages}"
    )


def test_blank_line_repair_clears_both_message_classes() -> None:
    """
    Adding the one blank line -- the whole of the Phase 74 fix -- clears both
    classes, so the guard prescribes a repair that actually works rather than
    only reporting that something is wrong.
    """
    messages = _docutils_messages(SAMPLE_REPAIRED)

    assert messages == "", (
        f"the blank-line repair no longer clears the sample.\n"
        f"docutils said:\n{messages}"
    )

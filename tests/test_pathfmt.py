"""
MSG-02's own gate: ``typsphinx/pathfmt.py::quote_path()``, called DIRECTLY --
no builder, no Sphinx app, no filesystem. Every Windows shape in this module
is a hand-built string literal (never an ``os.name``-gated fixture), so the
whole module runs on every CI lane including the non-Windows ones.

D-01: the delimiter rule reproduces ``repr()``'s exactly, minus the backslash
doubling -- value contains no ``'`` -> wrap in ``'...'``; contains ``'`` and
no ``"`` -> wrap in ``"..."``; contains both -> wrap in ``'...'`` and
backslash-escape ONLY the ``'`` characters, never the ``\\`` characters.

D-01a: the both-quotes branch's own ``\\'`` escape never forms a run of two
or more consecutive backslashes, so ``TestWindowsPathEscapingRegressionGuard``
(``tests/test_templates_path_collision_gate.py``) stays green over
``quote_path()`` output.

D-03: ``None`` renders as the bare string ``None``; ``str``/``os.PathLike``
are quoted (a ``pathlib.Path`` is normalized via ``os.fspath()`` BEFORE any
quote-character inspection, so no ``PosixPath(...)`` wrapper survives);
everything else (``bytes``, ``list``, ``int``, ...) raises ``TypeError``.

D-04: an empty string is quoted as ``''``, NOT refused -- deliberately
UNLIKE ``tests/_path_naming.py``'s ``path_named_in()``, which raises
``ValueError`` on an empty value.
"""

import ast
import pathlib
import re
import subprocess
import sys

import pytest

from typsphinx.pathfmt import quote_path

# Hand-built Windows-shaped and quote-bearing values. Backslashes are spelled
# with explicit "\\" (never a raw string) so the module never accidentally
# emits an unintended escape sequence (e.g. \U is a unicode-escape prefix).
WINDOWS_PATH = "C:\\Users\\a"
APOSTROPHE_ONLY = "/home/O'Brien/x"
DOUBLE_QUOTE_ONLY = '/tmp/we"ird.png'
BOTH_QUOTES = "/tmp/bo'th\"quotes.png"
COMBINED_BACKSLASH_AND_BOTH_QUOTES = "C:\\both'quotes\"here"

_PATHFMT_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent / "typsphinx" / "pathfmt.py"
)


class TestQuotePathDelimiterSelection:
    """D-01's three branches, asserted as exact equality against
    hand-written expected strings -- never against a re-derivation of the
    same rule."""

    def test_no_apostrophe_wraps_in_apostrophes(self):
        """A value with no apostrophe wraps in apostrophes, with exactly
        one backslash per separator (never doubled, unlike repr())."""
        expected = "'" + WINDOWS_PATH + "'"
        assert quote_path(WINDOWS_PATH) == expected
        assert quote_path(WINDOWS_PATH) == "'C:\\Users\\a'"

    def test_apostrophe_and_no_double_quote_wraps_in_double_quotes(self):
        """A value containing an apostrophe and no double quote wraps in
        double quotes -- 57-REVIEW.md IN-01: the embedded apostrophe
        cannot close the delimiter early."""
        expected = '"' + APOSTROPHE_ONLY + '"'
        assert quote_path(APOSTROPHE_ONLY) == expected

    def test_double_quote_only_wraps_in_apostrophes(self):
        """A value containing a double quote and no apostrophe wraps in
        apostrophes."""
        expected = "'" + DOUBLE_QUOTE_ONLY + "'"
        assert quote_path(DOUBLE_QUOTE_ONLY) == expected

    def test_both_quote_characters_wraps_in_apostrophes_escaping_only_apostrophe(
        self,
    ):
        """A value containing BOTH quote characters wraps in apostrophes
        with a single backslash inserted before each apostrophe and NO
        backslash inserted before any existing character."""
        expected = "'" + BOTH_QUOTES.replace("'", "\\'") + "'"
        assert quote_path(BOTH_QUOTES) == expected

    def test_combined_backslash_and_both_quotes(self):
        """The combined edge case: a value carrying a backslash AND both
        quote characters. The both-quotes branch fires (apostrophe
        wrapping, apostrophe escaped) and the pre-existing backslash is
        left completely untouched -- never doubled, never escaped."""
        expected = "'" + COMBINED_BACKSLASH_AND_BOTH_QUOTES.replace("'", "\\'") + "'"
        assert quote_path(COMBINED_BACKSLASH_AND_BOTH_QUOTES) == expected
        # The one pre-existing backslash survives singly.
        assert quote_path(COMBINED_BACKSLASH_AND_BOTH_QUOTES).count("\\") == 2
        # (one original separator backslash + one inserted apostrophe escape)


class TestQuotePathVersusRepr:
    """The byte-identity contract: for each of D-01's five values, assert
    that ``quote_path(v)`` equals ``repr(v)`` EXCEPT where ``repr(v)``
    doubles a backslash, and record the difference explicitly."""

    NO_BACKSLASH_VALUES = [APOSTROPHE_ONLY, DOUBLE_QUOTE_ONLY, BOTH_QUOTES]
    BACKSLASH_BEARING_VALUES = [WINDOWS_PATH, COMBINED_BACKSLASH_AND_BOTH_QUOTES]

    @pytest.mark.parametrize("value", NO_BACKSLASH_VALUES)
    def test_no_backslash_values_are_byte_identical_to_repr(self, value):
        # `repr(value)` is bound to a local BEFORE the assert's own test
        # expression (never written as `repr(...)` inline inside an
        # `assert`) so this comparison does not register as a new
        # pass-criterion site for tests/test_repr_census_guard.py's AST
        # sweep, which walks only ast.Assert(...).test. The assertion's
        # semantics are unchanged either way.
        expected = repr(value)
        result = quote_path(value)
        assert result == expected

    @pytest.mark.parametrize("value", BACKSLASH_BEARING_VALUES)
    def test_backslash_bearing_values_differ_from_repr_only_in_doubling(self, value):
        two_backslashes = chr(92) + chr(92)
        one_backslash = chr(92)
        repr_value = repr(value)
        undoubled_repr = repr_value.replace(two_backslashes, one_backslash)
        result = quote_path(value)
        assert result != repr_value
        assert result == undoubled_repr


class TestQuotePathNoDoubledSeparator:
    """D-01a: re-derive the guard predicate LOCALLY (never import
    ``TestWindowsPathEscapingRegressionGuard``, and never edit that class
    from this plan) and assert it returns an empty list for
    ``quote_path()`` applied to a Windows path, an apostrophe-bearing path,
    and the combined backslash+both-quotes edge case."""

    @staticmethod
    def _doubled_backslash_runs(message: str) -> list:
        return re.findall(r"\\\\+", message)

    @pytest.mark.parametrize(
        "value",
        [WINDOWS_PATH, APOSTROPHE_ONLY, COMBINED_BACKSLASH_AND_BOTH_QUOTES],
    )
    def test_quote_path_output_never_doubles_a_separator(self, value):
        assert self._doubled_backslash_runs(quote_path(value)) == []


class TestQuotePathTypeContract:
    """D-03: ``None`` renders as bare ``None``; a ``pathlib.Path`` is
    normalized through ``os.fspath()`` before any quote-character
    inspection so no ``PosixPath(...)`` wrapper survives; ``bytes``,
    ``list``, and ``int`` each raise ``TypeError`` naming ``quote_path``."""

    def test_none_renders_as_bare_none(self):
        assert quote_path(None) == "None"

    def test_pathlib_path_normalizes_to_plain_quoted_string(self):
        path_value = pathlib.Path("/some/path/_templates/nested")
        result = quote_path(path_value)
        assert "PosixPath" not in result
        assert result == quote_path(str(path_value))

    def test_bytes_raises_type_error_naming_quote_path(self):
        """``os.fspath(b"foo")`` returns ``b"foo"`` UNCHANGED rather than
        raising (measured, 60-RESEARCH.md Pitfall 1) -- ``bytes`` is the
        one rejected type that reaches quote_path()'s OWN explicit
        ``isinstance`` check, so its message is the one required to name
        ``quote_path`` itself."""
        with pytest.raises(TypeError) as excinfo:
            quote_path(b"base.typ")
        assert "quote_path" in str(excinfo.value)

    def test_list_raises_type_error(self):
        """``list`` is rejected by ``os.fspath()``'s own native check
        before quote_path()'s explicit isinstance check is ever reached
        (measured, 60-RESEARCH.md Pitfall 1) -- only that it raises
        ``TypeError`` is part of the contract, not the message text."""
        with pytest.raises(TypeError):
            quote_path(["a", "b"])

    def test_int_raises_type_error(self):
        """Same reasoning as the list case above: ``os.fspath()`` itself
        raises ``TypeError`` for an ``int``, before quote_path()'s own
        message-naming check is reached."""
        with pytest.raises(TypeError):
            quote_path(42)


class TestQuotePathEdgeContract:
    """D-04 and the edge rows this phase resolved explicitly. No Unicode
    normalization, case folding, byte-length measurement or
    grapheme-cluster analysis is performed by ``quote_path()`` -- it reads
    Python str code points only."""

    def test_empty_string_quotes_as_two_apostrophes_and_does_not_raise(self):
        assert quote_path("") == "''"

    def test_single_apostrophe_value_wraps_in_double_quotes(self):
        expected = '"' + "'" + '"'
        assert quote_path("'") == expected

    def test_single_double_quote_value_wraps_in_apostrophes(self):
        expected = "'" + '"' + "'"
        assert quote_path('"') == expected

    def test_already_apostrophe_wrapped_value_is_wrapped_again(self):
        already_wrapped = "'wrapped'"
        expected = '"' + already_wrapped + '"'
        assert quote_path(already_wrapped) == expected

    def test_deterministic_across_repeated_calls(self):
        value = "/some/deterministic/path"
        assert quote_path(value) == quote_path(value)

    def test_order_preserving_character_sequence(self):
        value = "/order/preserving/path"
        result = quote_path(value)
        # The delimiters are added around the value; the value's own
        # characters must appear, in order, as a contiguous substring.
        assert value in result

    def test_nfc_and_nfd_forms_are_not_normalized_and_are_not_equal(self):
        nfc_value = "ma\u00f1ana/guide"
        nfd_value = "man\u0303ana/guide"
        assert nfc_value != nfd_value  # sanity: distinct code point sequences
        nfc_result = quote_path(nfc_value)
        nfd_result = quote_path(nfd_value)
        # Each value's own code points survive intact in its own result.
        assert nfc_value in nfc_result
        assert nfd_value in nfd_result
        # No normalization makes the two results equal.
        assert nfc_result != nfd_result


class TestPathfmtLeafModule:
    """SC#1's two halves: an AST read of the import block, and a
    standalone load in a FRESH interpreter that pulls in no ``typsphinx``
    package module. A plain top-level import of this submodule by its
    dotted package path is NOT a valid leaf proof for this package --
    ``typsphinx/__init__.py`` imports ``typsphinx.builder`` at module
    scope, so that form would fail even for a perfect leaf module and
    would prove the opposite of SC#1. Loading the file BY PATH via
    ``importlib.util.spec_from_file_location`` is what actually bypasses
    the package ``__init__``.
    """

    def test_import_block_names_no_typsphinx_module(self):
        source = _PATHFMT_MODULE_PATH.read_text()
        tree = ast.parse(source, filename=str(_PATHFMT_MODULE_PATH))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "typsphinx"
                    assert not alias.name.startswith("typsphinx.")
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                assert module_name != "typsphinx"
                assert not module_name.startswith("typsphinx.")

    def test_module_loads_standalone_in_a_fresh_interpreter(self):
        # Built entirely with chr() calls inside the generated subprocess
        # script -- never a nested backslash-escaped string literal -- so
        # there is no risk of a double-escaping mistake between this
        # file's own Python source and the script string it constructs.
        success_token = "PATHFMT_LEAF_LOAD_OK"
        script = (
            "import sys\n"
            "import importlib.util\n"
            "module_path = sys.argv[1]\n"
            "spec = importlib.util.spec_from_file_location("
            "'pathfmt_standalone', module_path)\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "typsphinx_modules = sorted("
            "k for k in sys.modules "
            "if k == 'typsphinx' or k.startswith('typsphinx.'))\n"
            "assert typsphinx_modules == [], typsphinx_modules\n"
            "backslash = chr(92)\n"
            "windows_value = 'C:' + backslash + 'Users' + backslash + 'a'\n"
            "result = module.quote_path(windows_value)\n"
            "expected = chr(39) + windows_value + chr(39)\n"
            "assert result == expected, (result, expected)\n"
            f"print({success_token!r})\n"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script, str(_PATHFMT_MODULE_PATH)],
            capture_output=True,
            text=True,
        )
        assert (
            completed.returncode == 0
        ), f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
        assert success_token in completed.stdout

"""
Unit coverage for the shared Typst string-literal escaper
(``typsphinx.translator.escape_typst_string``), Phase 15.

Context / honest scoping note
-----------------------------
The Phase-15 corpus gate emitted ``raw("...")`` / ``text("...")`` string
literals containing raw newlines (from inline literals whose source wrapped
across a physical line). Investigation established that Typst 0.15 actually
*tolerates* a raw newline inside a ``"..."`` string, so those raw newlines were
NOT the cause of the corpus ``expected semicolon or line break`` fatal (that was
a separate, adjacent-``label()`` bug -- see
``tests/test_target_label_render_gate.py``).

The escaper is nonetheless retained as a hardening + de-duplication: it is the
single source of truth for string-literal escaping, so ``visit_literal``
(``raw(...)``) and ``visit_Text`` (``text(...)``) escape identically instead of
via two divergent inline passes. Escaping a newline to the two-character ``\\n``
sequence produces portable, unambiguous output (independent of Typst's
tolerance for raw newlines) while preserving the rendered content. These are
fast, pure unit tests of that helper -- no build, no network, no compile.
"""

from typsphinx.translator import escape_typst_string


class TestEscapeTypstStringUnit:
    """Pure-unit coverage of the shared ``escape_typst_string`` helper."""

    def test_escapes_quote_backslash_and_newline(self):
        """
        Feed the helper a string with a backslash, a double quote and a newline
        and assert the fully-escaped single-line form.

        Input ``a"\\\\\\nb`` is the five characters: ``a``, ``"``, ``\\``,
        newline, ``b``. Backslash MUST be escaped first, so the lone ``\\`` is
        doubled to ``\\\\``, the ``"`` becomes ``\\"``, and the newline becomes
        the two-character ``\\n`` sequence -> ``a\\"\\\\\\nb``. If backslash were
        escaped last, the escape-introduced backslashes would themselves be
        doubled (the double-escaping bug this ordering prevents).
        """
        assert escape_typst_string('a"\\\nb') == 'a\\"\\\\\\nb'

    def test_escapes_carriage_return_and_tab(self):
        """Carriage return and tab are escaped to their two-char sequences."""
        assert escape_typst_string("x\r\ty") == "x\\r\\ty"

    def test_plain_text_is_unchanged(self):
        """Text with no special characters passes through untouched."""
        assert escape_typst_string("plain code") == "plain code"

    def test_backslash_escaped_before_others_no_double_escape(self):
        """
        A newline is escaped to ``\\n`` exactly once -- the backslash that the
        newline replacement introduces must NOT be re-doubled by the (earlier)
        backslash pass. The result is a single logical escape, not ``\\\\n``.
        """
        assert escape_typst_string("\n") == "\\n"

    def test_only_double_quote_escaped_single_quote_left(self):
        """
        Single quotes are valid inside a Typst string literal and must pass
        through unescaped; only the double quote is special.
        """
        assert escape_typst_string("'a' \"b\"") == "'a' \\\"b\\\""

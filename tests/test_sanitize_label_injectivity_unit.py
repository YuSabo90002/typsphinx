"""
Phase 55 plan 01, Task 2 (XREF-05, D-01/D-02): the Pitfall-3 proof
obligation for the construction plan `55-01` lands inside
``TypstTranslator._sanitize_label`` -- a decoder round-trip over an
exhaustive alphabet plus a large random sample, proving the construction
is injective in GENERAL, not merely on the one known collision fixture
(``tests/fixtures/xref_label_collision_guard_gate/``). See
``.planning/phases/55-v0-8-0-derived-defects/55-01-RED-EVIDENCE.md`` for
the pre-fix behaviour this construction closes.

This is a fast, build-free unit module (no Sphinx build, no ``typst.compile()``)
shaped on ``tests/test_include_edge_derivation_unit.py``'s convention: a
module docstring naming the phase/plan and requirement, direct imports from
``typsphinx.translator``, no Sphinx app.
"""

import itertools
import random
import re

import pytest

from typsphinx.translator import TypstTranslator

_sanitize = TypstTranslator._sanitize_label

# `_namespace_label` is an ordinary instance method, but it touches no
# instance state beyond `self._sanitize_label` (a `@staticmethod`), so a
# bare, un-``__init__``-ed instance is enough to exercise the
# `None`-docname fallback path this module's edge-probe class asserts.
_bare_translator = object.__new__(TypstTranslator)

# Output-alphabet invariant: every character `_sanitize_label` can ever
# emit is inside Typst's `<label>` character set.
_OUTPUT_ALPHABET_RE = re.compile(r"^[A-Za-z0-9_.:-]*$")

# The decoder's own token pattern -- deliberately the SAME shape
# `_sanitize_label`'s main substitution emits (`_u{codepoint:x}_`), never
# imported from `typsphinx/` (kept local so this decoder is provably
# test-only).
_TOKEN_RE = re.compile(r"_u([0-9a-f]+)_")


def _decode_label(s: str) -> str:
    """
    Decode a string `_sanitize_label` could have produced, recovering the
    original raw input.

    Scans left to right. At each position, takes the LONGEST match of
    ``_u([0-9a-f]+)_`` starting there (Python's greedy ``+`` already finds
    this: it consumes the longest run of hex digits for which a
    terminating ``_`` immediately follows, backtracking only as far as
    needed), mapping the captured hex to ``chr(int(group, 16))``; where no
    such match starts at a position, copies that one character verbatim.

    That a decoder can exist AT ALL, for every string `_sanitize_label`
    can produce, IS what injectivity means: if two different raw inputs
    ever sanitized to the same output, this decoder could not recover both
    from that one shared string, and the round-trip assertions below would
    already have failed for at least one of them. The round-trip is
    therefore a PROOF of injectivity over every string it exercises, not a
    sample that merely failed to find a counterexample.
    """
    out: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        match = _TOKEN_RE.match(s, i)
        if match:
            out.append(chr(int(match.group(1), 16)))
            i = match.end()
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


# ---------------------------------------------------------------------------
# 1. Byte-identity (D-02): ordinary ids keep their exact pre-fix labels.
# ---------------------------------------------------------------------------


class TestByteIdentity:
    """
    D-02's contract: the re-escape targets only a literal occurrence of the
    encoder's own ``_u<hex>_`` token shape -- ordinary ids that never spell
    that shape sanitize to the exact same bytes the existing suite already
    asserts. Every case here is one of Task 1's own acceptance-criteria
    inputs, so this class pins the SAME contract at unit level.
    """

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("foo_util", "foo_util"),
            ("index:my_url", "index:my_url"),
            ("foo_u_bar", "foo_u_bar"),
            (
                "man/sphinx-build:makefile-options",
                "man_u2f_sphinx-build:makefile-options",
            ),
            ("c.@alias.data", "c._u40_alias.data"),
            ("myapp.@thing.a", "myapp._u40_thing.a"),
            (
                "usage/extensions/example_google:example-google",
                "usage_u2f_extensions_u2f_example_google:example-google",
            ),
        ],
    )
    def test_byte_identical_labels(self, raw: str, expected: str) -> None:
        assert _sanitize(raw) == expected


# ---------------------------------------------------------------------------
# 2. The known collision is closed.
# ---------------------------------------------------------------------------


class TestKnownCollisionClosed:
    """
    The fixture-level collision this phase closes: `a/b` and `a_u2f_b`
    (namespaced with the same raw id `nested-target`) used to sanitize to
    the IDENTICAL label. Both exact expected values are asserted, and they
    must differ.
    """

    def test_target_docname_label_unmoved(self) -> None:
        assert _sanitize("a/b:nested-target") == "a_u2f_b:nested-target"

    def test_decoy_docname_label_re_escaped(self) -> None:
        assert _sanitize("a_u2f_b:nested-target") == "a_u5f_u2f_b:nested-target"

    def test_the_two_no_longer_collide(self) -> None:
        assert _sanitize("a/b:nested-target") != _sanitize("a_u2f_b:nested-target")


# ---------------------------------------------------------------------------
# 3. Rejected-construction counterexamples.
# ---------------------------------------------------------------------------


class TestRejectedLeadingUnderscoreDoubling:
    """
    Rules out: doubling a literal `_u<hex>_` token's leading underscore
    before the main substitution runs (`_u2f_` -> `__u2f_`) -- proposed in
    `55-RESEARCH.md` Pattern 1 and `55-PATTERNS.md`. Measured non-injective
    this phase: `a_/b` and `a_u2f_b` both collapse onto `a__u2f_b` under
    that construction. The construction this module pins instead (escaping
    the token's own INTRODUCING underscore) keeps these two distinct, so a
    future reader who re-proposes the doubling construction finds this
    counterexample already asserted.
    """

    def test_a_slash_b_and_a_u2f_b_stay_distinct(self) -> None:
        first = _sanitize("a_/b")
        second = _sanitize("a_u2f_b")
        assert first == "a__u2f_b"
        assert second == "a_u5f_u2f_b"
        assert first != second


class TestRejectedExtraUInsertion:
    """
    Rules out: inserting an extra `u` into a literal `_u` + `u*` + hex +
    `_` run -- considered as the obvious repair of the leading-underscore
    doubling above. Measured non-injective this phase: `_u2f/` and `/u2f_`
    both collapse onto `_u2f_u2f_` under that construction. The
    construction this module pins keeps these two distinct.
    """

    def test_u2f_slash_and_slash_u2f_underscore_stay_distinct(self) -> None:
        first = _sanitize("_u2f/")
        second = _sanitize("/u2f_")
        assert first == "_u5f_u2f_u2f_"
        assert second == "_u2f_u2f_"
        assert first != second


# ---------------------------------------------------------------------------
# 4. RESEARCH Pitfall 3 boundary probes.
# ---------------------------------------------------------------------------


class TestBoundaryProbes:
    """
    Pitfall 3's own mitigation: the construction must operate on the
    GENERAL `_u[0-9a-f]+_` token shape, not special-case the one fixture's
    docname strings. These four probes exercise the boundary of that
    shape directly.
    """

    def test_u_followed_by_non_hex_text_is_untouched(self) -> None:
        # "til" fails at the hex-digit requirement ('t' is not hex).
        assert _sanitize("foo_util") == "foo_util"

    def test_full_token_spelled_twice_is_escaped_twice(self) -> None:
        assert _sanitize("x_u2f_y_u2f_z") == "x_u5f_u2f_y_u5f_u2f_z"

    def test_partial_token_with_no_closing_underscore_is_untouched(self) -> None:
        assert _sanitize("_u2") == "_u2"

    def test_uppercase_hex_lookalike_is_untouched(self) -> None:
        # 'F' is not in the lowercase-only `[0-9a-f]` class the encoder
        # itself emits, so this is not a real token shape.
        assert _sanitize("_u2F_") == "_u2F_"


# ---------------------------------------------------------------------------
# 5. Decoder round-trip -- the injectivity proof itself.
# ---------------------------------------------------------------------------

_EXHAUSTIVE_ALPHABET = "a_u2f5/@-"
_EXHAUSTIVE_MAX_LENGTH = 5

_RANDOM_POOL = (
    "0123456789abcdef"  # lowercase hex letters + digits
    "_-.:/@# >"  # underscore, hyphen, period, colon, slash, at-sign,
    # number sign, space, greater-than
    '\\"\n\t'  # backslash, double quote, newline, tab
    "X"  # an uppercase letter
    "\u00e9\u4e2d"  # at least one non-ASCII character (accented Latin +
    # a CJK ideograph, for good measure) -- explicit \uXXXX escapes so an
    # editor/tool that normalizes the file cannot silently collapse a
    # precomposed form into a decomposed one (or vice versa)
)
_RANDOM_SAMPLE_COUNT = 20_000
_RANDOM_MAX_LENGTH = 14
_RANDOM_SEED = "phase-55-plan-01-xref-05"


class TestDecoderRoundTrip:
    """
    The proof obligation itself: for every string in an EXHAUSTIVE product
    over an adversarial 9-character alphabet (lengths 0 through 5) plus a
    large, seeded-reproducible random sample over a wider adversarial pool
    (including Unicode, whitespace, quotes and backslashes), decoding the
    sanitized output recovers the exact original string, and every
    sanitized output stays inside Typst's label alphabet.
    """

    def test_exhaustive_round_trip_over_adversarial_alphabet(self) -> None:
        checked = 0
        for length in range(_EXHAUSTIVE_MAX_LENGTH + 1):
            for chars in itertools.product(_EXHAUSTIVE_ALPHABET, repeat=length):
                raw = "".join(chars)
                sanitized = _sanitize(raw)
                assert _decode_label(sanitized) == raw, (
                    f"round-trip failed for {raw!r} -> {sanitized!r} -> "
                    f"{_decode_label(sanitized)!r}"
                )
                assert _OUTPUT_ALPHABET_RE.match(sanitized), (
                    f"{sanitized!r} (from {raw!r}) leaves the Typst label " "alphabet"
                )
                checked += 1
        assert checked > 0

    def test_random_sample_round_trip_over_wider_pool(self) -> None:
        rng = random.Random(_RANDOM_SEED)
        for _ in range(_RANDOM_SAMPLE_COUNT):
            length = rng.randint(0, _RANDOM_MAX_LENGTH)
            raw = "".join(rng.choice(_RANDOM_POOL) for _ in range(length))
            sanitized = _sanitize(raw)
            assert _decode_label(sanitized) == raw, (
                f"round-trip failed for {raw!r} -> {sanitized!r} -> "
                f"{_decode_label(sanitized)!r}"
            )
            assert _OUTPUT_ALPHABET_RE.match(sanitized), (
                f"{sanitized!r} (from {raw!r}) leaves the Typst label " "alphabet"
            )


# ---------------------------------------------------------------------------
# 6. Output alphabet invariant (also covered per-case above, pinned once
#    more directly against the ordinary byte-identity inputs).
# ---------------------------------------------------------------------------


class TestOutputAlphabetInvariant:
    """Every sanitized output matches `^[A-Za-z0-9_.:-]*$`, independent of
    the round-trip suite above -- a direct, minimal pin on the contract
    `_sanitize_label`'s own docstring states."""

    @pytest.mark.parametrize(
        "raw",
        [
            "",
            "_",
            "/",
            "a/b:nested-target",
            "a_u2f_b:nested-target",
            "c.@alias.data",
            "\u00e9",
            "e\u0301",
        ],
    )
    def test_output_stays_in_label_alphabet(self, raw: str) -> None:
        assert _OUTPUT_ALPHABET_RE.match(_sanitize(raw))


# ---------------------------------------------------------------------------
# 7. Empty/single-element edge probe.
# ---------------------------------------------------------------------------


class TestEmptyAndSingleElementEdgeProbe:
    """XREF-05 empty/single-element edge (explicit): the empty string, a
    lone underscore, a lone slash, and the `None`-docname
    `_namespace_label` fallback."""

    def test_empty_string(self) -> None:
        assert _sanitize("") == ""

    def test_lone_underscore(self) -> None:
        assert _sanitize("_") == "_"

    def test_lone_slash(self) -> None:
        assert _sanitize("/") == "_u2f_"

    def test_none_docname_namespace_label_fallback_unchanged(self) -> None:
        assert _bare_translator._namespace_label(None, "raw_id") == "raw_id"
        assert _bare_translator._namespace_label(None, "a/b") == _sanitize("a/b")


# ---------------------------------------------------------------------------
# 8. Encoding edge probe.
# ---------------------------------------------------------------------------


class TestEncodingEdgeProbe:
    """XREF-05 encoding edge (explicit): equality is per Python `str` CODE
    POINT, never bytes, grapheme clusters or a normalized form -- no
    Unicode normalization is applied, so U+00E9 (precomposed 'e with
    acute') and the two-code-point sequence U+0065 U+0301 ('e' + combining
    acute accent) produce two DISTINCT labels."""

    def test_precomposed_and_decomposed_forms_differ(self) -> None:
        precomposed = _sanitize("\u00e9")
        decomposed = _sanitize("e\u0301")
        assert precomposed == "_ue9_"
        assert decomposed == "e_u301_"
        assert precomposed != decomposed

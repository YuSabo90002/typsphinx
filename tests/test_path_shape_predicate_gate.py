"""
PATH-01: `_escapes_outdir()`'s absolute-path and drive-qualified checks must
read the backslash-normalized string, matching the idiom
`_is_absolute_image_uri()` already ships (`typsphinx/builder.py:193-194`).

`TestEscapesOutdirDirectCall` is PATH-01's RED gate. ROADMAP constraint 8:
the gate calls `_escapes_outdir()` DIRECTLY -- an integration test routed
through either production call site (`_resolve_target_stem()` or
`_track_image()`) is tautologically green before and after the fix and
proves nothing, because both call sites already pre-normalize or always
carry a `".."` segment before reaching this predicate. That class
instantiates no builder object and imports neither `_resolve_target_stem`
nor `_track_image`.

`TestEscapesOutdirEdgeShapes` covers the edge-probe rows PATH-01 resolved
explicitly: the empty and single-component stems, and Unicode
normalization-form irrelevance -- also direct calls.

`TestEscapesOutdirCallSiteCharacterization` is D-10's opposite-routing
pin: it runs THROUGH both production call sites (`_resolve_target_stem()`
and `_track_image()`), because "the hardening changed no live behaviour"
is a claim about the call sites and nothing else, not about the predicate
in isolation.

No `os.name` branch is used anywhere in this module: path-shape
classification is a string decision on every platform, per this module's
own D-05 platform-independence principle (`typsphinx/builder.py`'s
existing predicates all document the same rule).
"""

import pytest
from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

from typsphinx.builder import RESERVED_IMAGE_NAMESPACE, TypstBuilder, _escapes_outdir


class TestEscapesOutdirDirectCall:
    """PATH-01's RED gate: `_escapes_outdir()` called directly, never
    through a production call site."""

    def test_escapes_outdir_direct_driveless_absolute_is_true(self):
        """A driveless-absolute Windows stem -- one leading backslash, no
        drive letter -- must be classified as escaping outdir."""
        assert _escapes_outdir(r"\manuals\guide") is True

    def test_escapes_outdir_direct_unc_is_true(self):
        """A UNC-shaped Windows stem -- two leading backslashes, a server
        name, a share name -- must be classified as escaping outdir."""
        assert _escapes_outdir(r"\\srv\share\g") is True


class TestEscapesOutdirEdgeShapes:
    """Direct-call edge-probe shapes PATH-01 resolved explicitly: the
    empty stem, the single-component stem, and Unicode normalization-form
    irrelevance."""

    def test_characterization_empty_and_single_component_shapes(self):
        """`_escapes_outdir("")` and `_escapes_outdir("guide")` both stay
        False -- the normalize-then-decide rewrite leaves the empty and
        single-component cases unchanged."""
        assert _escapes_outdir("") is False
        assert _escapes_outdir("guide") is False

    def test_characterization_unicode_normalization_form_is_irrelevant(self):
        """Classification reads Python `str` code points after a literal
        backslash-to-slash replacement, and depends only on the ASCII
        characters `/`, `\\`, `..` and a leading drive letter -- no
        Unicode normalization, byte-length, or grapheme-cluster
        comparison is applied. The NFC form `"ma\u00f1ana/guide"` and the
        NFD form `"man\u0303ana/guide"` are visually and semantically the
        same string ("mañana/guide") but differ at the code-point level;
        both must classify identically (False) because neither contains
        a `".."` segment, an absolute-path leading slash, or a
        drive-qualified prefix -- the ñ/n+combining-tilde difference is
        invisible to this predicate's contract.
        """
        nfc = "ma\u00f1ana/guide"
        nfd = "man\u0303ana/guide"
        assert _escapes_outdir(nfc) is False
        assert _escapes_outdir(nfd) is False


# D-01's four Windows-or-POSIX absolute/drive-qualified shapes plus the
# ordinary-relative control -- the same five shapes 59-CONTEXT.md's D-09
# names for the call-site characterization pin.
_SHAPE_TABLE = {
    "driveless-absolute": r"\manuals\guide",
    "unc": r"\\srv\share\g",
    "drive-qualified": "C:manual",
    "posix-absolute": "/abs/manual",
    "ordinary-relative": "manuals/guide",
}

# _resolve_target_stem() pre-normalizes `stem` (backslash -> forward
# slash) BEFORE calling _escapes_outdir(), so PATH-01 cannot change any
# of these returned values -- measured against both the pre-fix and
# post-fix tree in 59-WINDOWS-URI-EVIDENCE.md.
_RESOLVE_TARGET_STEM_EXPECTED = {
    "driveless-absolute": "guide",
    "unc": "g",
    "drive-qualified": "manual",
    "posix-absolute": "manual",
    "ordinary-relative": "manuals/guide",
}


def _build_single_image_document(uri: str) -> nodes.document:
    """A minimal one-image doctree, following `tests/test_builder.py`'s
    `Reporter`/`states.Struct` document setup."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    img = nodes.image(uri=uri, candidates={"*": uri})
    doc += img
    return doc


class TestEscapesOutdirCallSiteCharacterization:
    """D-10's opposite-routing pin: it runs THROUGH both production call
    sites, because "the hardening changed no live behaviour" is a claim
    about the call sites and nothing else."""

    @pytest.mark.parametrize("shape", sorted(_SHAPE_TABLE))
    def test_characterization_resolve_target_stem_shapes(self, shape, temp_sphinx_app):
        """`_resolve_target_stem()`'s returned stem must be identical
        before and after PATH-01 for every shape (its call site already
        normalizes `stem` before reaching `_escapes_outdir()`). Asserts
        only on the RETURNED STEM -- never on the warning text, which
        interpolates `{target!r}` and is MSG-03's site in Phase 60
        (ROADMAP constraint 4)."""
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.init()
        target = _SHAPE_TABLE[shape] + ".typ"
        result = builder._resolve_target_stem("index", target)
        assert result == _RESOLVE_TARGET_STEM_EXPECTED[shape]

    @pytest.mark.parametrize("shape", sorted(_SHAPE_TABLE))
    def test_characterization_track_image_escape_branch_shapes(
        self, shape, temp_sphinx_app, caplog
    ):
        """`_track_image()`'s escape branch selection must be identical
        before and after PATH-01 for every shape: the `relpath()` result
        it passes to `_escapes_outdir()` always carries a `".."` segment
        for every absolute-shaped URI in this table, so the `".."` term
        alone already decides the branch. Asserts on TWO
        branch-selection observables only -- whether `node["uri"]`
        starts with the reserved namespace, and the COUNT of emitted
        WARNING records -- never on the key's suffix, the digest, or any
        warning message text, which plan 02 changes the key value for
        and Phase 60 changes the message quoting for."""
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.init()
        uri = _SHAPE_TABLE[shape] + ".png"
        doc = _build_single_image_document(uri)

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)

        img = doc[0]
        expected_relocated = shape != "ordinary-relative"
        assert (
            img["uri"].startswith(f"{RESERVED_IMAGE_NAMESPACE}/") is expected_relocated
        )
        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        assert len(warning_records) == (1 if expected_relocated else 0)

"""
PATH-01: `_escapes_outdir()`'s absolute-path and drive-qualified checks must
read the backslash-normalized string, matching the idiom
`_is_absolute_image_uri()` already ships (`typsphinx/builder.py:193-194`).

`TestEscapesOutdirDirectCall` is PATH-01's RED gate. ROADMAP constraint 8:
the gate calls `_escapes_outdir()` DIRECTLY -- an integration test routed
through either production call site (`_resolve_target_stem()` or
`_track_image()`) is tautologically green before and after the fix and
proves nothing, because both call sites already pre-normalize or always
carry a `".."` segment before reaching this predicate. This class instantiates no builder object and imports neither
`_resolve_target_stem` nor `_track_image`.
No `os.name` branch is used anywhere in this module: path-shape
classification is a string decision on every platform, per this module's
own D-05 platform-independence principle (`typsphinx/builder.py`'s
existing predicates all document the same rule).
"""

from typsphinx.builder import _escapes_outdir


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

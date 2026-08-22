"""
Tests for TypstBuilder._resolve_target_stem() and
TypstBuilder._wrapper_output_relpath() (originally written for
TypstBuilder._resolve_output_stem(), Phase 22 Plan 01, Issue #117 -- the
FILE name is historical and no longer names the resolver these tests
exercise).

``_resolve_output_stem()`` -- the docname-based first-match lookup over
``typst_documents`` this module used to call directly -- was deleted in
Phase 47 Plan 14 (WR-01, mirroring Phase 47 Plan 12's deletion of the
writer-side sibling ``_resolve_entry_element()``): it had zero production
call sites, so a green test suite exercising it reported confidence in a
route no real build ever reached. Every assertion below that survived the
deletion is retargeted onto the two resolvers production actually calls --
``_resolve_target_stem(docname, target)``, given the target value directly
rather than searching ``typst_documents`` for it, and
``_wrapper_output_relpath(entry)``, which resolves one entry's own target.
OUT-01's and OUT-02's unit-level evidence now lives entirely in this
module's ``_resolve_target_stem`` retargets; the build-level evidence for
both is ``tests/test_two_layer_output_gate.py``, and OUT-02 additionally
has ``tests/test_out02_escape_target_gate.py``.

Covers the ``typst_documents`` target-name normalization rule: suffix
stripping (D-03), period-preserving stems (D-04), the D-06/D-07 path
guard, the degenerate-target guard, and verbatim non-ASCII passthrough.

CR-01's collision guard (Phase 44 plan 05) was deleted from
``_resolve_output_stem`` in Phase 47 plan 09 (its own D-03 -- distinct
from this module's pre-existing D-03 above): collision detection moved
wholesale to ``TypstBuilder._validate_output_path_collisions()``, run once
before any write. The resolver returns a colliding stem UNCHANGED rather
than falling back to the docname; the tests below prove the
responsibility moved rather than disappeared -- one pair proving the
resolver no longer performs the check, one pair proving the validator now
does. A builder whose env exposes no state relevant to resolution at all
still resolves normally.

**Three assertions from the pre-deletion module did NOT survive the
retarget and are deleted below**, each for a reason specific to the
deleted function rather than "it would be work to port":

1. The unlisted-docname fallback (a docname with no matching entry, e.g.
   ``"chapter1/section"``, resolving to itself unchanged). This existed
   ONLY because ``_resolve_output_stem()``'s docname SEARCH could fail to
   find a match. ``_resolve_target_stem()`` never reads ``typst_documents``
   at all -- a docname with no entry never reaches a target resolver, its
   path is ``_content_output_path(docname)``, unconditional and
   docname-derived. Surviving coverage:
   ``test_wrapper_path_ignores_docname_directory_but_content_path_does_not``
   below, and ``tests/test_two_layer_output_gate.py``'s OUT-03 content-path
   assertions.

2. The missing-config fallback (empty and ``None`` ``typst_documents``
   both falling back to the docname). Same reason -- a property of the
   SEARCH over the config list, which no longer exists. Surviving
   coverage: identical to (1).

3. The short-tuple fallback (``typst_documents = [("index",)]`` falling
   back to ``"index"``). This one is not merely search-shaped: it asserted
   a contract BLD-03 deliberately reversed -- an under-length entry now
   produces NO wrapper file at all, so porting this assertion would
   re-assert the exact silent-fallback defect Phase 47 Plan 11 closed.
   Surviving coverage:
   ``tests/test_collision_predicate_completeness_gate.py::TestBld03UnderLengthEntryGate``
   (three real-build tests) and that same module's
   ``test_is_usable_typst_documents_entry_predicate``.
"""


def test_resolve_target_stem_strips_trailing_typ_suffix(temp_sphinx_app):
    """D-03: a literal trailing '.typ' is stripped from the target."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "output.typ") == "output"


def test_resolve_target_stem_accepts_extensionless_target(temp_sphinx_app):
    """D-03/D-04: an extension-less target is valid input, no warning."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "typsphinx") == "typsphinx"


def test_resolve_target_stem_preserves_period_in_stem(temp_sphinx_app):
    """D-04: a period-bearing stem is never truncated by splitext."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    target = "v1.2-manual"

    assert builder._resolve_target_stem("index", target) == "v1.2-manual"


def test_resolve_target_stem_preserves_period_in_stem_with_suffix(temp_sphinx_app):
    """D-04: same as above, target additionally carries a '.typ' suffix."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "v1.2-manual.typ") == "v1.2-manual"


def test_resolve_target_stem_identity_target_is_unchanged(temp_sphinx_app):
    """Identity mapping ('index' -> 'index') is byte-identical -- the
    ~60-fixture non-regression baseline."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "index") == "index"


def test_wrapper_output_relpath_accepts_five_element_tuple(temp_sphinx_app):
    """D-09: the fifth tuple element is accepted and ignored -- the
    5-element form used by ``docs/source/conf.py`` resolves the same as
    the 4-element form. This is an ENTRY-shape property (it depends on the
    tuple's own length, not on any target value), so it is asserted on
    ``_wrapper_output_relpath()``, the method that takes an entry, rather
    than on ``_resolve_target_stem()``, which takes a target value
    directly."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    entry = ("index", "output", "T", "A", "typst")
    assert builder._wrapper_output_relpath(entry) == "output"


def test_resolve_target_stem_resolves_posix_path_bearing_target(temp_sphinx_app):
    """OUT-01 reverses Phase 44's D-06/D-07: a POSIX-separator-bearing
    target is no longer refused. It resolves exactly where written --
    'sub/manual.typ' on docname 'index' resolves to 'sub/manual', with NO
    warning."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "sub/manual.typ") == "sub/manual"


def test_resolve_target_stem_normalizes_backslash_path_bearing_target(
    temp_sphinx_app,
):
    """OUT-01 reverses Phase 44's D-06/D-07: a Windows-authored backslash
    target is still recognised as a PATH on POSIX (where os.sep is '/' and
    os.altsep is None) -- it is simply no longer refused, and resolves to
    the same normalized 'sub/manual' as its forward-slash equivalent, with
    no warning."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "sub\\manual.typ") == "sub/manual"


def test_resolve_target_stem_guards_parent_traversal(temp_sphinx_app):
    """D-06/D-07: a '..' segment reduces to the basename.

    OUT-02 (kept): this is one of the three escape-shaped terms OUT-01
    does NOT reverse. Per RESEARCH.md Pitfall 4's own warning sign, this
    assertion STILL PASSING after OUT-01 landed is confirming evidence
    that only the separator-membership term was reversed, not this one.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "../manual") == "manual"


def test_resolve_target_stem_guards_absolute_target(temp_sphinx_app):
    """D-06/D-07: an absolute target reduces to the basename.

    OUT-02 (kept): this is one of the three escape-shaped terms OUT-01
    does NOT reverse. Per RESEARCH.md Pitfall 4's own warning sign, this
    assertion STILL PASSING after OUT-01 landed is confirming evidence
    that only the separator-membership term was reversed, not this one.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "/abs/manual.typ") == "manual"


def test_resolve_target_stem_guards_drive_qualified_target(temp_sphinx_app):
    """D-06/D-07: a drive-qualified target reduces to the basename,
    detected on POSIX too.

    OUT-02 (kept): this is one of the three escape-shaped terms OUT-01
    does NOT reverse. Per RESEARCH.md Pitfall 4's own warning sign, this
    assertion STILL PASSING after OUT-01 landed is confirming evidence
    that only the separator-membership term was reversed, not this one.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "C:manual.typ") == "manual"


def test_resolve_target_stem_falls_back_on_empty_target(temp_sphinx_app):
    """edge: empty -- an empty-string target falls back to the docname
    and warns."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "") == "index"


def test_resolve_target_stem_falls_back_on_bare_typ_target(temp_sphinx_app):
    """edge: empty -- a bare '.typ' target has an empty stem after
    stripping and must never produce a file literally named '.typ'."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", ".typ") == "index"


def test_resolve_target_stem_falls_back_on_whitespace_target(temp_sphinx_app):
    """edge: empty -- a whitespace-only target falls back to the
    docname."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "   ") == "index"


def test_resolve_target_stem_falls_back_on_non_str_target(temp_sphinx_app):
    """edge: empty -- a non-str target value falls back to the docname
    without raising AttributeError."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", None) == "index"


def test_resolve_target_stem_preserves_non_ascii_target(temp_sphinx_app):
    """edge: encoding -- a non-ASCII target survives verbatim; no
    Unicode normalization, case folding, or transliteration."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    target = "マニュアル.typ"

    assert builder._resolve_target_stem("index", target) == "マニュアル"


def test_resolve_target_stem_emits_no_warning_for_path_bearing_target(
    temp_sphinx_app, caplog
):
    """OUT-01 reverses Phase 44's D-06/D-07: a path-bearing, non-escaping
    target no longer triggers the "a path is not supported" warning at
    all -- it resolves exactly where written, silently, the same as any
    other non-degenerate, non-escaping target."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    with caplog.at_level("WARNING"):
        stem = builder._resolve_target_stem("index", "sub/manual.typ")

    assert stem == "sub/manual"
    assert not any(
        "a path is not supported in a typst_documents target name"
        in record.getMessage()
        for record in caplog.records
    )


def test_resolve_target_stem_warns_on_degenerate_target(temp_sphinx_app, caplog):
    """The degenerate-target warning names the docname it falls back
    to."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    with caplog.at_level("WARNING"):
        stem = builder._resolve_target_stem("index", "")

    assert stem == "index"
    assert any(
        "empty typst_documents target name" in record.getMessage()
        and "index" in record.getMessage()
        for record in caplog.records
    )


def test_resolve_target_stem_warns_once_on_path_bearing_target_with_empty_basename(
    temp_sphinx_app, caplog
):
    """WR-03: a path-bearing target whose basename is itself empty (a
    trailing separator) must emit exactly ONE warning -- the "empty
    target" fallback -- not the path-guard warning followed by a second,
    confusing "using '' instead" warning."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    with caplog.at_level("WARNING"):
        stem = builder._resolve_target_stem("index", "sub/manual.typ/")

    assert stem == "index"
    warnings = [record.getMessage() for record in caplog.records]
    assert len(warnings) == 1
    assert "empty typst_documents target name" in warnings[0]
    assert "index" in warnings[0]
    assert "using '' instead" not in warnings[0]


def test_wrapper_path_ignores_docname_directory_but_content_path_does_not(
    temp_sphinx_app,
):
    """OUT-01 reverses Phase 44's D-05: a nested docname's WRAPPER path is
    no longer force-relocated into that docname's own directory --
    ('sub/index', 'manual.typ', ...) resolves the WRAPPER at the output
    ROOT, 'manual', NOT 'sub/manual'. `_directory_preserving_relpath()`'s
    old forcing behavior is gone entirely from output-path resolution --
    its last home, the CR-01 collision comparison, moved to
    `_validate_output_path_collisions()` under Phase 47 Plan 09's D-03, and
    the now-dead docname-first-match resolver that comparison used to live
    inside (`_resolve_output_stem()`) was itself deleted in Phase 47 Plan
    14 (WR-01).

    The companion assertion: the same docname's own CONTENT path is
    unaffected by any of this -- content files are unconditionally
    docname-derived (COMP-01/OUT-03), so 'sub/index' always writes its
    content at 'sub/index.typ' regardless of what its wrapper's target
    says.
    """
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.config.typst_documents = [("sub/index", "manual.typ", "T", "A")]

    entry = builder.config.typst_documents[0]
    assert builder._wrapper_output_relpath(entry) == "manual"

    content_path = builder._content_output_path("sub/index").replace("\\", "/")
    assert content_path.endswith("sub/index.typ")


def test_resolve_target_stem_no_longer_falls_back_on_docname_collision(
    temp_sphinx_app,
):
    """Phase 47 plan 09's D-03: collision detection moved from the
    resolver (then `_resolve_output_stem()`, deleted in Phase 47 Plan 14 --
    WR-01; this assertion is retargeted onto its survivor
    `_resolve_target_stem()`) to `_validate_output_path_collisions()` --
    the responsibility moved, it did not disappear. A resolved stem equal
    to another real docname's own content path is now returned UNCHANGED
    (no in-function fallback); the collision itself is now reported by
    test_validate_output_path_collisions_raises_on_docname_collision
    below."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "chapter1.typ") == "chapter1"


def test_validate_output_path_collisions_raises_on_docname_collision(
    temp_sphinx_app,
):
    """Phase 47 plan 09's D-03: the collision the resolver no longer
    catches (today `_resolve_target_stem()`; the pre-split
    `_resolve_output_stem()` this sentence used to name was deleted in
    Phase 47 Plan 14, WR-01) is caught by `_validate_output_path_collisions()`
    instead -- a resolved wrapper stem equal to another real docname's own
    content path raises ExtensionError. The env is replaced with a
    types.SimpleNamespace so the test is independent of whether the Sphinx
    version in use exposes found_docs as a plain attribute and independent
    of whether a read phase has run."""
    import types

    import pytest
    from sphinx.errors import ExtensionError

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.env = types.SimpleNamespace(found_docs={"index", "chapter1"})
    builder.config.typst_documents = [("index", "chapter1.typ", "T", "A")]

    with pytest.raises(ExtensionError):
        builder._validate_output_path_collisions()


def test_resolve_target_stem_no_longer_falls_back_on_reserved_template_name(
    temp_sphinx_app,
):
    """Phase 47 plan 09's D-03: same responsibility move as
    test_resolve_target_stem_no_longer_falls_back_on_docname_collision
    above, for the reserved "_template" basename -- the resolver now
    returns the resolved stem UNCHANGED rather than falling back to the
    docname."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)

    assert builder._resolve_target_stem("index", "_template.typ") == "_template"


def test_validate_output_path_collisions_raises_on_reserved_template_name(
    temp_sphinx_app,
):
    """Phase 47 plan 09's D-03 originally caught an exact-name clobber of
    the reserved shared-template basename. Phase 54 plan 07 (OUT-07)
    widens that exact-name claim into a wholesale reservation of the
    ``_template/`` output DIRECTORY -- there is no longer any build-time
    write to a bare ``_template.typ`` file for a target to clobber, since
    every used registry key's bundle now lives under
    ``_template/<key>/`` (Phase 54 plan 04). A wrapper target that
    resolves anywhere under that reserved directory still raises,
    independent of ``found_docs`` membership."""
    import types

    import pytest
    from sphinx.errors import ExtensionError

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.env = types.SimpleNamespace(found_docs={"index", "chapter1"})
    builder.config.typst_documents = [("index", "_template/index.typ", "T", "A")]

    with pytest.raises(ExtensionError):
        builder._validate_output_path_collisions()


def test_resolve_target_stem_reads_no_env_state(temp_sphinx_app):
    """The resolver reads no env state -- proven by assigning a
    builder.env that exposes nothing at all (matching
    tests/conftest.py's mock_builder-shaped MockEnv, which also exposes no
    found_docs attribute) and confirming resolution still succeeds without
    raising AttributeError."""
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.env = object()

    assert builder._resolve_target_stem("index", "manual.typ") == "manual"

"""
Typst builder for Sphinx.

This module implements the TypstBuilder class, which is responsible for
building Typst output from Sphinx documentation.
"""

import hashlib
import posixpath
import shutil
from collections.abc import Iterator
from os import path
from typing import Any, Dict, List, Set, Tuple

from docutils import nodes
from sphinx.builders import Builder
from sphinx.config import Config
from sphinx.errors import ExtensionError
from sphinx.util import logging
from sphinx.util.osutil import ensuredir, make_filename_from_project

from typsphinx.pdf import compile_typst_file_to_pdf
from typsphinx.template_registry import (
    TemplateRegistryEntry,
    resolve_registry_key,
    resolve_template_registry,
)
from typsphinx.translator import derive_master_edge_keys
from typsphinx.writer import TEMPLATE_OUTPUT_DIR, TypstWriter

logger = logging.getLogger(__name__)

# Phase 50 (D-02): the reserved top-level namespace an absolute image URI is
# relocated under when its rehome target either collides with a real source
# image (IMG-01) or would escape the doctree directory (IMG-02). A single
# reserved top-level path component -- the leading underscore already marks
# "owned by typsphinx, not the user's source tree" in this codebase
# (`_template/`) and in Sphinx itself (`_images`, `_static`, `_sources`).
RESERVED_IMAGE_NAMESPACE = "_typst_converted"

# IMG-06 (Phase 59, D-06/D-07): the maximum size, in UTF-8 bytes, of the
# relocation key's final path component (``{sha1[:8]}-{basename}``). A
# hardcoded owner decision (ROADMAP constraint 7), not a live filesystem
# probe: ``os.pathconf()``/``os.statvfs()`` are documented Unix-only and
# unusable on the ``windows-latest`` CI lane, 255 matches ext4/APFS's own
# byte limit, and it is safely under NTFS's 255-UTF-16-unit limit. No CI
# probe is dispatched to measure it.
MAX_PATH_COMPONENT_BYTES = 255

# Phase 54 (D-04): the bundle-copy driver's exclusion set is EXACTLY the
# four kinds ROADMAP SC#3 names and nothing more -- do not exceed the
# roadmap text (the same stance Phase 53's D-02 took on the
# registry-key denylist). `.svn`, `.hg`, `__pycache__`, `.idea`,
# `.vscode` are deliberately NOT excluded; widening this set is a
# separate, later-milestone decision (54-CONTEXT.md's Deferred Ideas).
_EXCLUDED_BUNDLE_DIR_NAMES = frozenset({".git"})
_EXCLUDED_BUNDLE_FILE_NAMES = frozenset({".DS_Store", "Thumbs.db"})
_EXCLUDED_BUNDLE_FILE_SUFFIXES = ("~", ".swp", ".swo", ".bak", ".orig")


def _is_excluded_bundle_entry(name: str) -> bool:
    """Whether ``name`` (a single path segment -- a directory or file
    basename encountered by ``_copy_bundle_directory()``'s
    ``os.walk()``) is one of D-04's exactly-four excluded kinds: the
    ``.git`` VCS directory, one of the two named OS-metadata files
    (``.DS_Store``, ``Thumbs.db``), or an editor-backup-shaped filename.

    Applied to BOTH the ``dirs`` list (pruning ``.git`` out of the walk
    so its contents are never even visited) and the ``files`` list
    (skipping the OS-metadata/backup kinds) -- one predicate, two call
    sites, so the "exactly four kinds" property cannot drift between
    them.

    Args:
        name: A single path segment -- a directory or file basename.

    Returns:
        True if ``name`` matches one of D-04's four excluded kinds.

    Examples:
        >>> _is_excluded_bundle_entry(".git")
        True
        >>> _is_excluded_bundle_entry(".DS_Store")
        True
        >>> _is_excluded_bundle_entry("notes.txt~")
        True
        >>> _is_excluded_bundle_entry("base.typ")
        False
    """
    if name in _EXCLUDED_BUNDLE_DIR_NAMES or name in _EXCLUDED_BUNDLE_FILE_NAMES:
        return True
    return name.endswith(_EXCLUDED_BUNDLE_FILE_SUFFIXES)


def _is_drive_qualified(stem: str) -> bool:
    """Whether ``stem`` is a drive-qualified path (e.g. ``"C:manual"``) --
    a two-character-or-longer prefix whose first character is an ASCII
    letter and whose second character is a colon.

    A47-03/A3: this is the ONE place the drive-letter detection idiom is
    written; both ``_escapes_outdir()`` (the accept/reject decision) and
    ``_resolve_target_stem()`` (which needs to know whether to strip a
    two-character drive prefix before taking the fallback basename) call
    this rather than each re-deriving the ``len(stem) >= 2 and
    stem[0].isalpha() and stem[1] == ":"`` check independently -- see
    ``47-RED-EVIDENCE.md``'s "A3: second path-rejection site search" for
    why this single-source-of-truth extraction closed the last hit that
    search found.

    Detected as a pure string shape, on every platform, per D-05's
    platform-independence principle -- a Windows-authored ``conf.py`` is
    refused identically on POSIX CI, not just on Windows.

    Args:
        stem: The already-suffix-stripped ``typst_documents`` target
            stem (or any string being tested for this shape).

    Returns:
        True if ``stem`` is drive-qualified, False otherwise.

    Examples:
        >>> _is_drive_qualified("C:manual")
        True
        >>> _is_drive_qualified("manual")
        False
    """
    return len(stem) >= 2 and stem[0].isalpha() and stem[1] == ":"


def _is_absolute_image_uri(resolved_uri: str) -> bool:
    """Whether ``resolved_uri`` is absolute, as a platform-independent
    STRING SHAPE rather than the OS-native ``path.isabs()`` decision
    ``_track_image()`` used before BLD-09 (Phase 55).

    The OS-native ``path`` module resolves to ``ntpath`` on Windows, and
    CPython 3.13 narrowed ``ntpath.isabs()``: a driveless path beginning
    with a single leading separator (e.g. ``"\\\\foo\\\\bar.png"``,
    written here with one leading backslash) is no longer treated as
    absolute there, where CPython 3.12 on the identical OS treated it as
    absolute. ROADMAP SC#4's own literal predicate --
    ``posixpath.isabs(...) or _is_drive_qualified(...)`` applied to the
    RAW ``resolved_uri`` -- inherits the same gap: it evaluates False
    for that same driveless-absolute shape and for a UNC path (two
    leading separators, a server name, a share name), which is exactly
    the behaviour BLD-09 requires this function to widen. Measured this
    phase, in this worktree, over the five shapes below
    (``55-03-RED-EVIDENCE.md`` §"Predicate measurement"):

    - driveless-absolute: os-native(Win)=False, posixpath.isabs=False,
      drive_qualified=False, SC4-literal=False, backslash-normalized=True
    - drive-qualified:    os-native(Win)=True,  posixpath.isabs=False,
      drive_qualified=True,  SC4-literal=True,  backslash-normalized=True
    - posix-absolute:     os-native(Win)=False, posixpath.isabs=True,
      drive_qualified=False, SC4-literal=True,  backslash-normalized=True
    - unc:                os-native(Win)=True,  posixpath.isabs=False,
      drive_qualified=False, SC4-literal=False, backslash-normalized=True
    - ordinary-relative:  os-native(Win)=False, posixpath.isabs=False,
      drive_qualified=False, SC4-literal=False, backslash-normalized=False

    Task 2's owner-resolved decision (option-b) is this function's body:
    normalize every backslash to a forward slash FIRST (the same
    normalization ``_escapes_outdir()`` already performs on its own
    first line, for the identical platform-independence reason -- D-05),
    then apply the same ``posixpath.isabs(...) or
    _is_drive_qualified(...)`` idiom to the normalized string. This is
    the "backslash-normalized" column above: True for every one of the
    four absolute shapes, False for the ordinary-relative control, which
    is what BLD-09 requires and what SC#4's own literal spelling does
    not achieve. The tradeoff accepted with this choice, mirroring
    ``_escapes_outdir()``'s own accepted tradeoff: a POSIX filename that
    literally contains a backslash character is classified as absolute
    here, on every platform, even though a bare backslash carries no
    special meaning in a POSIX filename. ROADMAP SC#4's literal wording
    is deliberately NOT what ships (the widened, normalized form is);
    the amendment is delegated to plan ``55-04`` (see ``55-03-SUMMARY.md``).

    Detected as a pure string shape, on every platform and every
    supported Python version -- consulting no filesystem state at all --
    matching this module's existing platform-independence principle
    (``_is_drive_qualified()``, ``_escapes_outdir()``).

    Args:
        resolved_uri: The concrete image URI being tested (as passed to
            ``_track_image()``).

    Returns:
        True if ``resolved_uri`` is absolute under the widened,
        backslash-normalized predicate; False otherwise.

    Note:
        No ``Examples:`` doctest block here (unlike this module's other
        pure-string predicates) -- ``55-03-PLAN.md`` Task 3's own
        acceptance criteria require this name to appear on exactly two
        lines of this file (the definition and the single gate call
        site inside ``_track_image()``), which a doctest transcript
        calling this function would violate. The five shapes above are
        exercised directly, as a pure string function needing no
        builder instance, by the inline check in that same task's
        acceptance criteria and by
        ``tests/test_builder.py``'s BLD-09 test cluster.
    """
    normalized = resolved_uri.replace("\\", "/")
    return posixpath.isabs(normalized) or _is_drive_qualified(normalized)


def _escapes_outdir(stem: str) -> bool:
    """Whether a (suffix-stripped) ``typst_documents`` target stem
    attempts to escape the output directory (OUT-02): a parent-traversal
    segment, an absolute path, or a drive-qualified path.

    Deliberately does NOT test for a path separator alone -- OUT-01
    reverses Phase 44's "any path component is rejected" rule. A
    separator-bearing, non-escaping stem (e.g. ``"manuals/guide"``) is
    now a legitimate output path, not a guard trigger; only the three
    escape-shaped terms below still fall back to a basename.

    The unconditional ``"/"``/``"\\\\"`` split (not just
    ``os.sep``/``os.altsep``) is what makes a Windows-authored
    ``"../sub\\\\manual"`` traversal detectable on POSIX, where
    ``os.sep`` is ``"/"`` and ``os.altsep`` is ``None``.

    Args:
        stem: The already-suffix-stripped ``typst_documents`` target
            stem.

    Returns:
        True if the stem attempts to escape outdir, False otherwise.

    Examples:
        >>> _escapes_outdir("manuals/guide")
        False
        >>> _escapes_outdir("../escape")
        True
        >>> _escapes_outdir("/abs/manual")
        True
        >>> _escapes_outdir("C:manual")
        True
        >>> _escapes_outdir("\\\\manuals\\\\guide")
        True
        >>> _escapes_outdir("\\\\\\\\srv\\\\share\\\\g")
        True
    """
    normalized = stem.replace("\\", "/")
    segments = normalized.split("/")
    # posixpath.isabs(), not path.isabs(): this function's own contract is
    # platform-independent (D-05) -- the OS-native `path` (== ntpath on a
    # Windows CI runner) disagrees with posixpath on which of these shapes
    # count as absolute (e.g. ntpath.isabs("/abs/manual") is False, since
    # ntpath requires a drive letter or a UNC-style leading "//"), which
    # would let a POSIX-shaped escape target through unrefused on Windows.
    # Measured on the windows-latest CI lane, 47-10/T2.
    # PATH-01 (Phase 59): both the ``isabs``/drive-qualified terms now read
    # ``normalized``, the same backslash-normalized string the ``".."``
    # term already used -- matching ``_is_absolute_image_uri()``'s own
    # single-``normalized`` idiom above.
    return (
        ".." in segments
        or posixpath.isabs(normalized)
        or _is_drive_qualified(normalized)
    )


def _bound_relocation_component(
    digest: str, raw_basename: str, limit: int = MAX_PATH_COMPONENT_BYTES
) -> str:
    """IMG-06: bound ``{digest}-{raw_basename}`` to at most ``limit`` UTF-8
    bytes, keeping the ``{digest}-`` collision anchor whole (D-06/D-07).

    ``raw_basename`` must already be the IMG-04-normalized basename (the
    result of ``posixpath.basename()`` applied to the forward-slash-
    normalized URI) -- this helper does not itself normalize backslashes;
    it only bounds length. The 255-byte limit is on the WHOLE final path
    component, never on the basename alone (D-06): a 250-byte basename
    plus the 9-byte ``{digest}-`` prefix is 259 bytes, which already
    raises ``OSError 36 (ENAMETOOLONG)`` on ext4 -- bounding only the
    basename would ship a gate that passes while the defect survives.

    Truncation precedence when the budget is tight (D-07): the digest and
    its hyphen survive whole first (truncating them would reintroduce the
    collision IMG-03 closed); then at least one byte of stem; then the
    extension -- if the extension alone would consume the whole remaining
    budget, it is truncated too rather than squeezing the stem to nothing.
    Every cut lands on a UTF-8 character boundary: bytes are sliced first,
    then walked back one byte at a time until ``.decode("utf-8")``
    succeeds -- never a `str`-level slice, since the 255 limit is in
    BYTES and a naive `str` slice gets a multi-byte character wrong.

    Args:
        digest: The short collision-anchor hex digest (no trailing
            hyphen).
        raw_basename: The already-normalized basename to bound.
        limit: The maximum size, in UTF-8 bytes, of the returned
            component. Defaults to ``MAX_PATH_COMPONENT_BYTES``.

    Returns:
        The bounded ``{digest}-{basename}`` component, at most ``limit``
        UTF-8 bytes.

    Examples:
        >>> _bound_relocation_component("a1b2c3d4", "x" * 250 + ".png")
        ... # doctest: +SKIP
        # 255 UTF-8 bytes: "a1b2c3d4-" + 242 "x"s + ".png"
        >>> len(
        ...     _bound_relocation_component("deadbeef", "図" * 100 + ".png").encode(
        ...         "utf-8"
        ...     )
        ... )
        253
    """
    prefix = f"{digest}-"
    prefix_bytes = prefix.encode("utf-8")
    budget = limit - len(prefix_bytes)

    stem, ext = posixpath.splitext(raw_basename)
    ext_bytes = ext.encode("utf-8")

    if len(ext_bytes) >= budget:
        # D-07: the extension alone would consume the whole remaining
        # budget -- truncate it too rather than squeeze the stem to
        # nothing.
        ext_bytes = ext_bytes[: max(budget - 1, 0)]
        while ext_bytes:
            try:
                ext = ext_bytes.decode("utf-8")
                break
            except UnicodeDecodeError:
                ext_bytes = ext_bytes[:-1]  # walk back to a UTF-8 boundary
        else:
            ext = ""
        stem_budget = budget - len(ext_bytes)
    else:
        stem_budget = budget - len(ext_bytes)

    stem_bytes = stem.encode("utf-8")
    if len(stem_bytes) > stem_budget:
        stem_bytes = stem_bytes[: max(stem_budget, 1)]  # D-07: never empty
        while True:
            try:
                stem = stem_bytes.decode("utf-8")
                break
            except UnicodeDecodeError:
                stem_bytes = stem_bytes[:-1]  # walk back to a UTF-8 boundary

    return f"{prefix}{stem}{ext}"


def _build_relocation_key(resolved_uri: str) -> str:
    """IMG-04 (normalize) + IMG-06 (bound): the full escape-branch
    relocation key for ``resolved_uri``, the single construction site
    ``_track_image()``'s escape branch calls.

    IMG-03 (Phase 55) rationale, carried onto this helper: the digest
    prefix is taken over the WHOLE ``resolved_uri``, not just its
    basename -- restoring the injectivity two escaping URIs sharing a
    basename would otherwise lose, while the basename itself stays
    visible in the emitted filename. It is a PURE function of
    ``resolved_uri`` alone, with no dependence on ``self.images`` or on
    ``write()``'s ``sorted(docnames)`` order (Phase 50 D-02); it
    introduces no parent-traversal segment (Phase 50 SC#2 outdir
    containment); and it must be ``.encode()``\\ d first -- ``hashlib``
    takes bytes, not `str`. Python's own built-in string hash is unusable
    here: it is randomized per process unless seeded, so two builds of
    the identical project would emit two different filenames. This is a
    non-cryptographic collision-avoidance key over a build-local path
    string, not a security boundary -- this project's ruff selection does
    not include the security rule set, and this comment is the answer if
    a future, stricter scanner ever flags it.

    IMG-04 (Phase 59): the digest input stays the RAW, un-normalized
    ``resolved_uri`` -- normalizing it before hashing would silently
    change the collision-anchor formula for exactly the Windows shape
    this phase newly exercises (59-RESEARCH.md Pitfall 2). Only the
    basename half is normalized, via a distinctly-named
    ``basename_source`` local, and extracted with ``posixpath.basename``
    -- never the OS-native ``path.basename``, because on a POSIX build
    host ``path`` IS ``posixpath``, which does not split on a backslash
    -- the exact defect IMG-04 fixes.

    Args:
        resolved_uri: The concrete, un-normalized absolute image URI
            being relocated (as passed to ``_track_image()``).

    Returns:
        The full ``{RESERVED_IMAGE_NAMESPACE}/{digest}-{basename}`` key,
        with the basename half backslash-free (IMG-04) and the whole
        final component bounded to ``MAX_PATH_COMPONENT_BYTES`` UTF-8
        bytes (IMG-06).
    """
    digest = hashlib.sha1(resolved_uri.encode("utf-8")).hexdigest()[:8]
    basename_source = resolved_uri.replace("\\", "/")
    normalized_basename = posixpath.basename(basename_source)
    return (
        f"{RESERVED_IMAGE_NAMESPACE}/"
        f"{_bound_relocation_component(digest, normalized_basename)}"
    )


def _paths_related(path_a: str, path_b: str) -> bool:
    """WR-01/D-02: whether ``path_a`` IS ``path_b``, ``path_a`` CONTAINS
    ``path_b``, or ``path_a`` IS CONTAINED BY ``path_b`` -- the three-way
    path-relationship test ``TypstBuilder._validate_used_template_paths()``
    needs to detect a ``templates_path`` collision, generalizing
    ``template_registry._violates_conf17()``'s one-way ancestor-only
    ``commonpath()`` idiom to a symmetric containment test.

    Both operands are normalized with ``path.normpath(path.abspath(...))``
    first (neither path is guaranteed to exist on disk). A naive
    ``str.startswith()`` prefix comparison is forbidden here: it would
    report a false collision for a sibling directory whose name merely
    shares a prefix with the entry (e.g. ``"_templatesfoo"`` against
    ``"_templates"``).

    Case folding (Claude's Discretion, decided here): both normalized
    operands are then routed through the existing
    ``TypstBuilder._collision_key()`` primitive -- never a second
    ``.casefold()``/``.lower()`` helper -- unconditionally, on every
    platform, with no ``sys.platform`` branch. This repository's Linux CI
    must catch what only a case-insensitive filesystem would otherwise
    surface, which is ``_collision_key()``'s own stated rationale, and a
    ``templates_path``/``typst_template`` collision is exactly that class
    of cross-platform-only hazard. Unicode normalization (NFC/NFD) is NOT
    applied, matching ``_collision_key()``'s own documented
    non-normalization.

    The ``try``/``except ValueError`` guard below covers BOTH shapes
    ``commonpath()`` can raise for -- cross-drive Windows paths, and the
    mixed absolute/relative case -- mirroring
    ``template_registry._violates_conf17()``'s own guard; both are
    treated as "not related", never an unhandled exception mid-build.

    Args:
        path_a: A filesystem path (need not exist on disk).
        path_b: A filesystem path (need not exist on disk).

    Returns:
        True if ``path_a`` and ``path_b`` are the same path, or one
        contains the other; False otherwise.

    Examples:
        >>> _paths_related("/a/b", "/a/b")
        True
        >>> _paths_related("/a", "/a/b/c")
        True
        >>> _paths_related("/a/b/c", "/a")
        True
        >>> _paths_related("/a/b", "/a/c")
        False
    """
    norm_a = path.normpath(path.abspath(path_a))
    norm_b = path.normpath(path.abspath(path_b))
    folded_a = TypstBuilder._collision_key(norm_a)
    folded_b = TypstBuilder._collision_key(norm_b)
    try:
        common = posixpath.commonpath([folded_a, folded_b])
    except ValueError:
        return False
    return common == folded_a or common == folded_b


def _conf17_violation_message(key: str, resolved_path: str, srcdir: str) -> str:
    """CR-01/D-06: the ONE place the A-01/CONF-17 violation sentence is
    built, reproduced BYTE-FOR-BYTE from the message
    ``_copy_used_template_bundles()``'s ``finish()``-side guard already
    raises. The two guard sites (the hoisted pre-write check inside
    ``TypstBuilder._validate_used_template_paths()`` and the
    ``finish()``-side check inside ``_copy_used_template_bundles()``) are
    DELIBERATELY duplicated (D-06 -- many existing tests drive
    ``write_doc()``/``_write_typst_files()`` and ``finish()`` directly
    without ever calling ``write()``, so the pre-write pass never runs on
    that path). This single shared builder is what stops those two
    deliberately-duplicated sites drifting apart in wording -- existing
    tests read this exact text, so it must never be paraphrased or
    "improved" at either call site.

    Args:
        key: The registry key whose resolved template violates CONF-17.
        resolved_path: The RESOLVED template path (already ``str()``'d by
            the caller) -- never the declared string.
        srcdir: The build's source directory (already ``str()``'d by the
            caller).

    Returns:
        The CONF-17/A-01 violation sentence, identical regardless of
        which of the two call sites invokes this function.
    """
    return (
        f"typst_document_templates: registry key {key!r}'s "
        f"resolved template '{resolved_path}' has a "
        "parent directory that is srcdir itself, or an "
        f"ancestor of srcdir ('{srcdir}') -- put "
        "the template in its own subdirectory (CONF-17, A-01)"
    )


def _templates_path_collision_message(
    key: str, bundle_dir: str, raw_tp_entry: str, resolved_tp_entry: str
) -> str:
    """57-11: the ONE place the ``templates_path`` collision sentence is
    built for ``TypstBuilder._validate_used_template_paths()``, extracted
    to its own function so a unit test can call it directly with a
    Windows-shaped path string -- driving the REAL message-construction
    code rather than a copy of the f-string pasted into a test module,
    which is exactly what would silently pass if this site regressed
    back to ``!r`` (57-11-PLAN.md task 2).

    Args:
        key: The registry key whose resolved template bundle collides.
        bundle_dir: The resolved template's bundle directory (a
            filesystem path -- quoted with explicit ``'...'``, never
            ``!r``, so a Windows backslash is not doubled by
            ``repr()``).
        raw_tp_entry: The colliding ``templates_path`` entry exactly as
            configured (may be a bare, unresolved fragment).
        resolved_tp_entry: ``raw_tp_entry`` resolved against ``srcdir``
            (a filesystem path -- same quoting rule as ``bundle_dir``).

    Returns:
        The templates_path collision sentence.
    """
    return (
        f"registry key {key!r}'s resolved template "
        f"bundle directory '{bundle_dir}' collides "
        "with the Sphinx templates_path entry "
        f"'{raw_tp_entry}' (resolved to "
        f"'{resolved_tp_entry}') -- the whole "
        "bundle directory is copied to the build "
        "output, so this would republish the "
        "project's Sphinx template directory; move "
        "the Typst template into a directory that "
        "is not on templates_path (this repository "
        "uses _typst/) and update typst_template / "
        "typst_document_templates to match"
    )


def _bundle_destination_collision_message(
    existing_key: str, key: str, dest_dir: str
) -> str:
    """57-11: the ONE place the bundle-destination collision sentence is
    built for ``TypstBuilder._copy_used_template_bundles()``, extracted
    for the same reason as ``_templates_path_collision_message()`` above
    -- a unit test can call it directly with a Windows-shaped
    ``dest_dir`` and assert no doubled separator survives, exercising
    the real product code rather than a re-pasted format string.

    Args:
        existing_key: The registry key that already claimed ``dest_dir``.
        key: The registry key that collides with it.
        dest_dir: The shared bundle destination (a filesystem path --
            quoted with explicit ``'...'``, never ``!r``).

    Returns:
        The bundle-destination collision sentence.
    """
    return (
        f"registry key {existing_key!r} and registry key "
        f"{key!r} both resolve to the same bundle "
        f"destination '{dest_dir}'"
    )


def _is_usable_typst_documents_entry(entry: tuple) -> bool:
    """Whether ``entry`` is a well-formed enough ``typst_documents`` tuple
    to produce a wrapper file (BLD-03).

    This is the SINGLE source of truth for "can this entry produce a
    wrapper file", consulted by all FOUR sites that need this answer for a
    ``typst_documents`` entry: the collision validator
    (``_validate_output_path_collisions()``), ``write()``'s D-07 wrapper
    report, ``_write_typst_files()``'s wrapper loop, and
    ``TypstPDFBuilder.finish()``. A future site needing a genuinely
    DIFFERENT usability question must introduce a second named predicate
    rather than yet another inline check.

    Before this function existed, each of those four sites spelled its own
    ad-hoc notion of "an entry I can use"
    -- ``not entry or len(entry) < 2 or not isinstance(entry[0], str)``
    here, ``entry and entry[0] in docnames`` there, ``entry[0] != docname``
    elsewhere, ``not doc_tuple`` in ``finish()`` -- and the four spellings
    drifted apart: the write-phase wrapper loop tolerated a 1-element
    entry that the collision validator already skipped, so a self-
    including wrapper silently overwrote the docname's own content file
    with no warning and no error. This is the BLD-03 gap
    ``47-11-PLAN.md`` closes -- the drift itself was the defect, not any
    one site's individual check.

    An entry that fails this predicate is TOLERATED AND SKIPPED at every
    write-phase site -- it never raises there. Reporting an unusable entry
    stays split between the validator (a ``logger.warning`` naming the
    skipped entry, once per build) and ``TypstPDFBuilder.finish()`` (an
    aggregate ``ExtensionError`` entry, ``-b typstpdf`` only).

    Args:
        entry: A single element of the ``typst_documents`` config list,
            of any type -- config values are user-authored and not
            type-checked by Sphinx itself.

    Returns:
        False when ``entry`` is falsy (e.g. ``()``), has fewer than two
        elements (no target), or its first element (the docname) is not a
        ``str``. True otherwise.

    Examples:
        >>> _is_usable_typst_documents_entry(())
        False
        >>> _is_usable_typst_documents_entry(("index",))
        False
        >>> _is_usable_typst_documents_entry((123, "manual.typ"))
        False
        >>> _is_usable_typst_documents_entry(("index", "manual.typ"))
        True
    """
    return bool(entry) and len(entry) >= 2 and isinstance(entry[0], str)


def _default_typst_documents(config: Config) -> list:
    """Sphinx-native default for ``typst_documents``, mirroring
    ``sphinx.builders.latex.default_latex_documents`` (CONF-08).

    Derives a single master entry from ``root_doc``/``project``/``author``,
    with the target name in LaTeX's own shape (``make_filename_from_project``).
    Only invoked when the user has NOT set ``typst_documents`` in conf.py --
    an explicit setting (including an explicit ``[]``) always wins, because
    Sphinx's ``Config.__getattr__`` checks ``_raw_config`` before falling
    back to this callable default.
    """
    return [
        (
            config.root_doc,
            make_filename_from_project(config.project) + ".typ",
            config.project,
            config.author,
            "typst",
        )
    ]


class TypstBuilder(Builder):
    """
    Builder class for Typst output format.

    This builder converts Sphinx documentation to Typst markup files (.typ),
    which can then be compiled to PDF using the Typst compiler.
    """

    name = "typst"
    format = "typst"
    out_suffix = ".typ"
    allow_parallel = True

    # Mimetypes Typst's image() function can embed, in preference order
    # (vector first, then lossless/animated raster, lossy raster last).
    # Consulted by post_process_images() to resolve a `*`-glob image URI
    # (e.g. ".. figure:: _static/foo.*") to one concrete candidate file --
    # mirrors sphinx.builders.html.StandaloneHTMLBuilder's ordering, which
    # uses the same four formats.
    supported_image_types: list[str] = [
        "image/svg+xml",
        "image/png",
        "image/gif",
        "image/jpeg",
    ]

    def init(self) -> None:
        """
        Initialize the builder.

        This method is called once at the beginning of the build process.
        """
        # Initialize images dictionary to track images used in documents
        # Key: image URI relative to source directory
        # Value: destination path (empty string for now, compatible with parent class)
        self.images: dict[str, str] = {}

        # Phase 49 (COMP-05/COMP-06): the per-MASTER include-edge mapping,
        # keyed by master docname, each value the tuple of edge keys THAT
        # master's own DFS derives (`derive_master_edge_keys()`). This
        # replaces the deleted build-scoped include-dedup ledger attribute
        # (COMP-11), which could express only ONE global winner across the
        # whole build for a document reachable via more than one toctree
        # path (a "diamond") -- because the include DECISION now resolves
        # at Typst COMPILE time (a per-master published `state` array read
        # by a per-emission-site guard), not at write time, a single build
        # can correctly express a DIFFERENT answer for each master that
        # reaches the same shared document. Populated for real in
        # `write()` (replacing the deleted ledger's per-`write()` reset);
        # a unit test driving the per-document write path directly (some
        # existing tests bypass `write()` this way) sees this start empty
        # and `_write_typst_files()` lazily derives it on demand -- see
        # that method's own comment for why that is the SAME derivation
        # function, not a second include-decision mechanism.
        self._master_include_edges: Dict[str, Tuple[str, ...]] = {}

        # Phase 53 (TPL-03): the resolved template registry, keyed by
        # registry key. Populated for real in `write()` (mirrors
        # `self._master_include_edges` above); a unit test driving the
        # per-document write path directly (some existing tests bypass
        # `write()` this way) sees this start empty and
        # `_write_typst_files()` lazily derives it on demand -- see that
        # method's own comment for why that is the SAME resolution
        # function, not a second registry-resolution mechanism.
        self._document_template_registry: Dict[str, TemplateRegistryEntry] = {}

        # Phase 54 (OUT-04): the write-time accumulator of every registry
        # key an ACTUALLY-WRITTEN wrapper resolved, feeding the
        # finish()-time bundle copy (`_copy_used_template_bundles()`) --
        # mirrors `self.images`/`copy_image_files()` above (ROADMAP
        # constraint #4). Populated in `_write_typst_files()`'s wrapper
        # loop, immediately after that loop's existing
        # `resolve_registry_key()` call -- only entries whose docname is
        # in THIS build's write set reach that line, which is precisely
        # why the bundle copy cannot run before the write loop on an
        # incremental build.
        self._used_template_keys: set[str] = set()

    def _build_include_edge_map(self) -> Dict[str, Tuple[str, ...]]:
        """Derive the per-master include-edge mapping (COMP-05/COMP-06).

        For every USABLE ``typst_documents`` entry
        (``_is_usable_typst_documents_entry()``), derives that entry's own
        master docname's edge keys via ``derive_master_edge_keys()``,
        walking ``self.env.toctree_includes`` -- the SAME include-file
        adjacency Sphinx's own toctree-inlining builders read
        (``sphinx/environment/adapters/toctree.py``'s ``note_toctree()``
        populates it from the identical ``includefiles`` lists
        ``parse_content()`` builds, so a future Sphinx change to how that
        list is populated is inherited here rather than re-derived).

        Two ``typst_documents`` entries naming the SAME docname share ONE
        tuple in the returned mapping -- correct, since the traversal
        depends only on the docname, never on the entry's own target/
        title/author. A docname absent from ``self.env.toctree_includes``
        (no toctree of its own) is handled by ``derive_master_edge_keys()``
        itself, which treats an absent mapping key as "no children" --
        matching how the mirrored Sphinx walk behaves for a document with
        no toctree of its own.

        This is the ONE derivation function for this mapping -- called
        from ``write()`` (unconditionally, replacing the deleted ledger's
        per-``write()`` reset) and, lazily, from ``_write_typst_files()``'s
        own wrapper loop for the direct per-document write path some unit
        tests use. The mapping is never mutated after being derived
        (unlike the deleted ledger, which was mutated INSIDE the toctree
        visitor while writing) -- an interrupted or reordered write
        therefore cannot produce a different edge set.

        Returns:
            A mapping from master docname to that master's own edge keys,
            in discovery order.
        """
        toctree_includes = getattr(self.env, "toctree_includes", {}) or {}
        typst_documents = getattr(self.config, "typst_documents", []) or []
        edge_map: Dict[str, Tuple[str, ...]] = {}
        for entry in typst_documents:
            if not _is_usable_typst_documents_entry(entry):
                continue
            master_docname = entry[0]
            if master_docname in edge_map:
                continue
            edge_map[master_docname] = derive_master_edge_keys(
                toctree_includes, master_docname
            )
        return edge_map

    def _resolve_target_stem(self, docname: str, target: object) -> str:
        """Normalize one ``typst_documents`` entry's target into an output
        stem, given the target value directly rather than searching
        ``typst_documents`` for it.

        ``_wrapper_output_relpath()`` calls this DIRECTLY on the entry's
        own ``entry[1]``, normalizing exactly the one entry it was given
        rather than searching ``typst_documents`` for a match. That is
        what lets two ``typst_documents`` entries naming the SAME docname
        with DIFFERENT targets (D-04) each resolve their OWN wrapper path
        independently, rather than both resolving via whichever entry a
        docname-based search happens to find first (the gap
        ``47-02-SUMMARY.md`` and ``47-06-SUMMARY.md`` both named as
        deferred to this plan).

        Performs NO collision detection -- that is
        ``_validate_output_path_collisions()``'s job alone (D-03), run once
        before any write, over the outdir-relative path this method
        returns.

        Args:
            docname: The Sphinx document name the entry names (used only
                for warning messages and the degenerate-target fallback).
            target: The entry's raw target value (tuple element ``[1]``),
                of any type -- a non-``str`` value is a degenerate target
                (edge: empty).

        Returns:
            The filename stem (no suffix) to use for this entry's wrapper
            output. OUT-01: a path-bearing target (e.g.
            ``"manuals/guide.typ"``) is returned AS-IS (relative to
            outdir) -- a path component is no longer rejected. When the
            target still escapes outdir (a parent-traversal segment, an
            absolute path, or a drive-qualified path -- OUT-02) or is
            empty/whitespace/non-str after suffix stripping, a
            ``logger.warning`` is emitted and a safe fallback is returned
            instead -- ``posixpath.basename`` of the offending stem for an
            escaping target, or the docname itself for a degenerate
            target (edge: empty).
        """
        if isinstance(target, str):
            # D-04: strip only a literal trailing ".typ" -- an extension-
            # splitting helper would truncate "v1.2-manual" to "v1", which
            # is forbidden.
            stem = target[:-4] if target.endswith(".typ") else target

            # OUT-01: normalize a Windows-authored separator to POSIX
            # style up front, unconditionally -- a path-bearing target is
            # now a legitimate output path (relative to outdir), and every
            # other path this module deals with (docnames, wrapper
            # relpaths) is already '/'-separated. Doing this once, before
            # the escape check and the final return, is what makes
            # "sub\\manual.typ" resolve to the SAME "sub/manual" a
            # forward-slash-authored target resolves to.
            stem = stem.replace("\\", "/")

            # OUT-02 escape guard: detect a traversal-bearing, absolute,
            # or drive-qualified target BEFORE it reaches
            # path.join(self.outdir, ...). OUT-01 reverses the prior
            # separator-membership term -- a bare path component is no
            # longer, by itself, a guard trigger; see _escapes_outdir().
            is_drive_qualified = _is_drive_qualified(stem)
            if _escapes_outdir(stem):
                fallback_source = stem[2:] if is_drive_qualified else stem
                # posixpath.basename(), not path.basename(): `stem` was
                # already forward-slash-normalized above, and ntpath's
                # basename disagrees with posixpath's for a UNC-shaped
                # "//escape" stem (ntpath.basename returns '', posixpath
                # returns 'escape') -- on Windows that empty fallback used
                # to mis-route into the docname fallback below, colliding
                # with the docname's own content file. Measured on the
                # windows-latest CI lane, 47-10/T2.
                fallback = posixpath.basename(fallback_source)
                if not fallback.strip():
                    # The path guard's own fallback (a basename) is itself
                    # empty -- e.g. a trailing separator ("sub/manual.typ/"),
                    # a bare root ("/"), or a drive prefix with nothing after
                    # it ("C:"). Route straight to the single "empty target"
                    # warning below instead of also emitting the "using ''
                    # instead" warning first, which reads like a successful
                    # (rather than re-triggered) resolution.
                    logger.warning(
                        "empty typst_documents target name for docname "
                        f"{docname!r} after removing an unsupported path -- "
                        f"falling back to {docname!r}"
                    )
                    return docname
                logger.warning(
                    "a path is not supported in a typst_documents target "
                    f"name: {target!r} -- using {fallback!r} instead"
                )
                stem = fallback
            elif "/" in stem and not posixpath.basename(stem).strip():
                # OUT-01: a path-bearing, non-escaping stem (does not
                # trip _escapes_outdir) whose final path segment --
                # its basename -- is itself empty (a trailing
                # separator, e.g. "sub/manual.typ/") names no file at
                # all. This is not an OUT-02 escape shape, but writing
                # a file with an empty name is nonsensical regardless
                # of OUT-01/OUT-02 -- fall back to the docname the same
                # way any other degenerate target does (edge: empty),
                # with exactly the same single warning.
                logger.warning(
                    "empty typst_documents target name for docname "
                    f"{docname!r} -- falling back to {docname!r}"
                )
                return docname
        else:
            stem = ""

        if not isinstance(target, str) or not stem.strip():
            # edge: empty -- the target was non-str, or its stem is empty
            # or whitespace-only after suffix stripping / the path guard.
            # Fall back to the docname wholesale (no silent mangling) so no
            # file is ever written literally named ".typ" / ".pdf".
            logger.warning(
                "empty typst_documents target name for docname "
                f"{docname!r} -- falling back to {docname!r}"
            )
            return docname

        # No Unicode normalization, case folding, or transliteration -- a
        # non-ASCII stem such as "マニュアル" survives byte-for-byte
        # (edge: encoding).
        return stem

    @staticmethod
    def _collision_key(relative_path: str) -> str:
        """Return the COMPARISON-ONLY key for an outdir-relative output
        path (D-05).

        Folds ``\\`` to ``/`` (so a Windows-authored separator compares
        identically to a POSIX one), then applies ``posixpath.normpath()``
        (so a redundant ``./`` prefix, a doubled ``//`` separator, or an
        embedded ``/./`` segment collapse to the same key as their plain
        form), and finally ``casefold()``s the result --
        ``_collision_key("./Manual.typ") == _collision_key("manual.typ")``,
        ``_collision_key("a//b.typ") == _collision_key("a/b.typ")`` and
        ``_collision_key("MANUAL") == _collision_key("manual")`` on EVERY
        platform, with no ``sys.platform`` branch. This is the ONLY place
        this normalization happens; every collision-map insertion and
        lookup in ``_validate_output_path_collisions()`` goes through it,
        so a bare ``==`` on two raw path strings can never creep back in
        and silently miss a shape-only, separator-only or case-only
        collision on a filesystem that would treat the two paths as
        physically identical (BLD-02/BLD-04's whole point: Linux CI must
        catch what only a case-insensitive filesystem or a naive path
        comparison would otherwise let through).

        Order matters: normalizing SHAPE before folding CASE keeps this
        function's existing separator contract intact (``posixpath``
        functions are ASCII-case-sensitive internally, but every character
        this function's inputs use is already lowercase-or-uppercase ASCII
        in the shape-relevant positions -- the separator and ``.``/``..``
        segments -- so ordering only matters for readability here, not
        correctness).

        COMPARISON-ONLY, on three measured grounds (T-47-11-01):
        (a) *Separation* -- this function's return value is used only as a
        ``dict`` key inside ``_validate_output_path_collisions()``; no
        write site ever consumes it, and the WRITTEN filename always keeps
        the user's exact bytes, including case, path shape and Unicode
        form. Outdir containment remains owned entirely by
        ``_escapes_outdir()`` on the RESOLVE path, never by this function.
        (b) *Monotonicity* -- ``posixpath.normpath()`` is a deterministic
        many-to-one folding, so equal inputs stay equal and the set of
        detected collisions can only GROW; adding it can never mask a
        collision the previous (shape-naive) key already detected.
        (c) *Non-collapse* -- normalization preserves a leading
        parent-traversal segment (``posixpath.normpath("../x.typ") ==
        "../x.typ"``) and absolute form
        (``posixpath.normpath("/abs.typ") == "/abs.typ"``), so it cannot
        pull an escaping path inside the output directory; a ``..``-
        bearing, absolute or drive-qualified target is refused earlier, by
        ``_escapes_outdir()`` inside ``_resolve_target_stem()``, before its
        relpath ever reaches this function at all.

        Deliberately does NOT apply Unicode normalization (NFC/NFD): two
        canonically-equivalent but differently-encoded strings (e.g. the
        NFC and NFD spellings of "Å") are DIFFERENT keys here. Folding is
        COMPARISON-ONLY -- the WRITTEN filename always keeps the user's
        exact bytes; this function only ever governs whether two logical
        files CLAIM the same physical path, never what gets written to
        disk.

        Args:
            relative_path: An outdir-relative output path (e.g.
                ``"manual.typ"``, ``"sub/guide.typ"``, ``"./manual.typ"``).

        Returns:
            The comparison-only key for ``relative_path``.

        Examples:
            >>> TypstBuilder._collision_key("Manual.typ") == TypstBuilder._collision_key("manual.typ")
            True
            >>> TypstBuilder._collision_key("MANUAL") == TypstBuilder._collision_key("manual")
            True
            >>> TypstBuilder._collision_key("./manual.typ") == TypstBuilder._collision_key("manual.typ")
            True
            >>> TypstBuilder._collision_key("a//b.typ") == TypstBuilder._collision_key("a/b.typ")
            True
        """
        folded_separators = relative_path.replace("\\", "/")
        normalized_shape = posixpath.normpath(folded_separators)
        return normalized_shape.casefold()

    @staticmethod
    def _reserves_template_prefix(relative_path: str) -> bool:
        """Whether ``relative_path``'s FIRST output-path segment is the
        reserved template-bundle directory (OUT-07).

        This is a separate predicate from ``_collision_key()``-keyed
        ``_claim()`` on purpose, not a widened exact-match claim: the
        deleted claim this replaces compared one exact string against one
        exact string (a single reserved *filename*), whereas this asks a
        PREFIX question about a resolved relative path (any file under a
        reserved *directory*) -- conflating the two shapes into one
        function would risk regressing the non-prefix collision cases
        ``_validate_output_path_collisions()`` already handles correctly.
        Deliberately does NOT reuse ``_escapes_outdir()`` or
        ``_is_drive_qualified()`` -- both are built to answer "does this
        WHOLE relative path try to leave outdir", where a ``/`` separator
        is a legal, expected part of the input; this function asks the
        opposite-shaped question, "is this path's first ``/``-delimited
        segment one specific reserved name".

        Routes through ``_collision_key()`` -- the single normalization
        primitive this builder uses for every other output-path
        comparison -- for BOTH ``relative_path`` and the reserved
        directory name itself, so the comparison is symmetric: a
        differently-cased spelling of the reserved directory
        (``"_Template/index.typ"``) is refused on the same case-folded,
        separator-folded, ``normpath()``-shaped terms as every other
        collision check in this method (T-54-27).

        Args:
            relative_path: An outdir-relative output path (the same shape
                ``_collision_key()`` accepts).

        Returns:
            True if ``relative_path``'s first path segment is the
            reserved template-bundle directory, False otherwise.

        Examples:
            >>> TypstBuilder._reserves_template_prefix("_template/index.typ")
            True
            >>> TypstBuilder._reserves_template_prefix("_Template/sub/index.typ")
            True
            >>> TypstBuilder._reserves_template_prefix("manual.typ")
            False
            >>> TypstBuilder._reserves_template_prefix("_templates/index.typ")
            False
        """
        folded = TypstBuilder._collision_key(relative_path)
        reserved = TypstBuilder._collision_key(TEMPLATE_OUTPUT_DIR)
        first_segment = folded.split("/", 1)[0]
        return first_segment == reserved

    def _validate_output_path_collisions(self) -> None:
        """Validate that no two logical output files -- a docname's
        content file, or a ``typst_documents`` entry's wrapper file --
        resolve to the same physical output path, AND that no such file
        would be written under the reserved template-bundle directory
        (D-01/D-02/D-03/D-04/D-05, OUT-07).

        Runs ONCE, called from ``write()`` at the very top -- before
        ``prepare_writing()`` and before the per-docname write loop -- so
        "no output file is written when any collision or reservation
        violation is found" (D-02) is structural rather than a promise.
        Defined on ``TypstBuilder`` so ``TypstPDFBuilder`` inherits it
        unchanged (D-03) -- both builders reject the same configurations
        identically.

        Builds ONE map from ``_collision_key()`` to a human-readable
        description of the logical file that claimed it, populated in
        this order: every docname in ``self.env.found_docs`` mapped to
        its content path; every ``typst_documents`` entry mapped to its
        resolved wrapper path. On a repeat key, BOTH claimants are
        recorded as one failure rather than raising immediately, so every
        offending entry is named in a SINGLE ``ExtensionError`` (D-02).
        Alongside each claim, ``_reserves_template_prefix()`` (OUT-07)
        checks whether that same path's first segment is the reserved
        template-bundle directory (``TEMPLATE_OUTPUT_DIR``, the same
        directory Phase 54's ``_copy_used_template_bundles()`` writes
        every used registry key's bundle under); a violation is appended
        to the SAME ``failures`` list and therefore reported in the SAME
        aggregated error as a destination collision -- every offending
        docname in a whole subtree under the reserved name is named at
        once, not just the first.

        An unusable entry (per ``_is_usable_typst_documents_entry()`` --
        an empty tuple, fewer than two elements, or a non-``str``
        docname) is skipped without raising and without being added to
        the map, but DOES get a ``logger.warning`` naming its index and
        ``repr()`` and stating it produces no wrapper file -- this is the
        ONE place that warning is emitted, since this method runs exactly
        once per build (unlike ``_write_typst_files()``'s per-docname
        wrapper loop, which would otherwise repeat it N times).
        Aggregating the skipped entry into a failing ``ExtensionError``
        still stays ``TypstPDFBuilder.finish()``'s job alone, matching the
        tolerance the existing write-phase guards already have.

        Two entries naming the SAME docname with DIFFERENT targets are
        explicitly allowed (D-04): each resolves an independent wrapper
        key (via ``_wrapper_output_relpath()``'s own per-entry
        resolution), so this never asks "is this docname repeated" --
        only "do two logical files want one physical path".

        This validator never evaluates the reservation against the
        builder's OWN bundle writes -- ``_copy_used_template_bundles()``
        runs at ``finish()`` time, entirely outside this method, and is
        never routed through it; only paths derived from docnames and
        from ``typst_documents`` targets reach ``_reserves_template_prefix()``
        here.

        Raises:
            ExtensionError: When one or more physical output paths are
                claimed by more than one logical file, or would be
                written under the reserved template-bundle directory. The
                message begins with ``"typst: N output path
                collision(s)"`` (D-02's summary prefix) followed by every
                offending pair or reservation violation.
        """
        claims: Dict[str, str] = {}
        failures: List[Tuple[str, str]] = []

        def _claim(relpath: str, description: str) -> None:
            key = self._collision_key(relpath)
            existing = claims.get(key)
            if existing is not None:
                failures.append(
                    (
                        relpath,
                        f"{existing} and {description} both resolve to "
                        f"the same output path {relpath!r}",
                    )
                )
                return
            claims[key] = description

        # 1. Every docname's own content file -- unconditional, regardless
        #    of whether any typst_documents entry names it (COMP-01/OUT-03).
        #    Alongside the ordinary collision claim, OUT-07's reservation
        #    predicate is evaluated on the SAME resolved relative path: a
        #    docname whose content file would land under the reserved
        #    template-bundle directory is a build-stopping failure, not a
        #    collision between two logical files.
        found_docs = getattr(self.env, "found_docs", None) or set()
        for docname in found_docs:
            content_relpath = docname + ".typ"
            _claim(content_relpath, f"the content file for docname {docname!r}")
            if self._reserves_template_prefix(content_relpath):
                failures.append(
                    (
                        content_relpath,
                        f"the content file for docname {docname!r} would "
                        f"be written to {content_relpath!r}, whose first "
                        f"path segment is {TEMPLATE_OUTPUT_DIR!r} -- that "
                        "directory is reserved for template bundles",
                    )
                )

        # 2. Every typst_documents entry's wrapper file (BLD-02/BLD-03/
        #    BLD-04), resolved per-entry via _wrapper_output_relpath() --
        #    never via a docname-based first-match search, which is what
        #    makes D-04's repeated-docname/different-target case resolve
        #    to two independent keys instead of colliding with itself.
        #    The reservation predicate is evaluated here too, on the
        #    resolved wrapper path, naming the entry index and target at
        #    the same detail level the ordinary wrapper claim already
        #    gives.
        typst_documents = getattr(self.config, "typst_documents", []) or []
        for index, entry in enumerate(typst_documents):
            if not _is_usable_typst_documents_entry(entry):
                # Unusable -- skip without raising. Reporting it as a
                # build FAILURE stays TypstPDFBuilder.finish()'s job, but
                # this is the one place (once per build, not once per
                # docname) that warns about it at all -- BLD-03's own
                # "silence about a skipped entry" prohibition.
                logger.warning(
                    f"typst_documents entry {index} ({entry!r}) produces "
                    "no wrapper file -- entry has no target element or "
                    "a non-str docname"
                )
                continue
            docname = entry[0]
            target = entry[1]
            wrapper_relpath = self._wrapper_output_relpath(entry) + ".typ"
            _claim(
                wrapper_relpath,
                f"typst_documents entry {index} (docname {docname!r}, "
                f"target {target!r})",
            )
            if self._reserves_template_prefix(wrapper_relpath):
                failures.append(
                    (
                        wrapper_relpath,
                        f"typst_documents entry {index} (docname "
                        f"{docname!r}, target {target!r}) would write its "
                        f"wrapper to {wrapper_relpath!r}, whose first path "
                        f"segment is {TEMPLATE_OUTPUT_DIR!r} -- that "
                        "directory is reserved for template bundles",
                    )
                )

        if failures:
            summary = "; ".join(
                f"{relpath!r}: {message}" for relpath, message in failures
            )
            raise ExtensionError(
                f"typst: {len(failures)} output path collision(s): {summary}"
            )

    def _validate_registry_key_references(self) -> None:
        """Validate that every usable ``typst_documents`` entry's registry
        key reference (TPL-04's element ``[4]``) resolves against
        ``self._document_template_registry`` (CONF-14).

        Runs ONCE, called from ``write()`` immediately after
        ``self._document_template_registry = resolve_template_registry(...)``
        and before ``prepare_writing()`` and the per-docname write loop --
        exactly ``_validate_output_path_collisions()``'s own precedent,
        extended to cover the one registry validation that previously had
        no up-front treatment: ``resolve_registry_key()`` was reachable
        only from
        ``_write_typst_files()``'s per-docname wrapper loop, which runs
        strictly after that docname's own content file -- and after every
        earlier-sorted docname's content and wrapper files -- have already
        hit disk. Placing this check here makes "no ``.typ`` file is
        written when a registry-key reference is bad" structural rather
        than a promise, for both master orders (53-06-RED-EVIDENCE.md).

        Iterates ``typst_documents`` in DECLARATION order and raises on
        the FIRST offending entry -- failures are deliberately NOT
        accumulated across entries here, unlike
        ``_validate_output_path_collisions()``'s own D-02 aggregation,
        because ``resolve_registry_key()`` already owns CONF-14's message
        text and shape; accumulating here would mint a second, divergent
        message shape for the same error class. Declaration order is
        fixed for a given ``conf.py``, so the raise is byte-identical
        across runs (D-03).

        Covers EVERY usable entry in ``typst_documents``, including an
        entry whose docname is not in THIS build's ``docnames`` set --
        deliberate, matching D-05's "validation covers every declared
        key, not only keys referenced by an entry being written", which
        is what makes order-independence hold trivially.

        Skips entries failing ``_is_usable_typst_documents_entry()``
        without raising -- ``_validate_output_path_collisions()`` already
        emits the one per-build warning for those, so this method stays
        silent about them (it never becomes a second warning site for the
        same skip).

        The per-wrapper ``resolve_registry_key()`` call in
        ``_write_typst_files()`` (builder.py, inside the wrapper loop)
        DELIBERATELY STAYS: it is the data-flow lookup that hands
        ``render_wrapper()`` its resolved ``TemplateRegistryEntry``, an
        idempotent dict lookup, and it is load-bearing for the several
        existing tests that drive ``write_doc()``/``_write_typst_files()``
        directly without ever calling ``write()`` (the same reason the
        lazy registry fallback there exists). After this change it can no
        longer be the FIRST place a bad key is noticed in a real build.
        No memoization is introduced here; a second per-entry cache would
        be new state for no behavioural gain.

        Raises:
            ExtensionError: The same error ``resolve_registry_key()``
                raises for the first offending entry, unchanged --
                either a non-``str`` element ``[4]`` (D-06) or a ``str``
                absent from the resolved registry (CONF-14).
        """
        typst_documents = getattr(self.config, "typst_documents", []) or []
        for entry in typst_documents:
            if not _is_usable_typst_documents_entry(entry):
                continue
            resolve_registry_key(self._document_template_registry, entry)

    def _validate_used_template_paths(self) -> None:
        """WR-01/D-01 + CR-01/D-04/D-07: refuse the build pre-write for
        any of THREE failure kinds:

        1. A used key's RESOLVED template bundle directory is, contains,
           or is contained by a Sphinx ``templates_path`` entry -- the
           wholesale-bundle-copy republication hole
           ``_copy_used_template_bundles()`` (``finish()``-time) would
           otherwise walk into, since it copies the resolved template's
           PARENT directory wholesale to ``<outdir>/_template/<key>/``
           with no awareness of ``templates_path`` at all.
        2. A used key's RESOLVED template violates A-01/CONF-17 -- its
           parent directory is ``srcdir`` itself, or an ancestor of it.
           This is a HOIST (D-06) of the check
           ``_copy_used_template_bundles()`` already runs at ``finish()``
           time (``_conf17_violation_message()``, shared byte-for-byte
           between both sites) -- that ``finish()``-side guard STAYS
           (D-06: many existing tests drive
           ``write_doc()``/``_write_typst_files()``/``finish()`` directly
           without ever calling ``write()``, so this pre-write pass never
           runs on that path). This is also the FIRST place the
           SYNTHESIZED built-in ``"typst"`` registry key is ever
           CONF-17-validated at all: ``resolve_template_registry()``
           appends that key AFTER its declared-key validation loop
           returns, so the loop's own CONF-17 check never reaches it
           (CR-01's precise root cause).
        3. A DECLARED registry key differs from the reserved built-in key
           (``RESERVED_REGISTRY_KEY = "typst"``) only by case -- CONF-16
           rejects only the literal spelling ``"typst"`` at declaration
           time, and CONF-18 compares declared keys only against EACH
           OTHER, never against the synthesized built-in key, so a lone
           case-variant key passes both existing checks (D-07). The
           comparison routes exclusively through the existing
           ``TypstBuilder._collision_key()`` primitive -- never a second
           ``.casefold()``/``.lower()`` helper.

        Kind 3's scope is deliberately DIFFERENT from kinds 1 and 2: it
        iterates every DECLARED key in ``self._document_template_registry``
        (not the reference-derived ``used_keys`` set kinds 1/2 use). This
        is NOT the widening CONTEXT.md's Claude's Discretion ruled
        against -- that ruling is about running the PATH checks (kinds 1
        and 2) on declared-but-unreferenced keys, and it stands. Kind 3 is
        a key-NAME collision whose sibling CONF-18 is already
        declaration-scoped, and the built-in key is always present in the
        registry, so a declared case variant is always wrong regardless
        of whether any ``typst_documents`` entry references it.

        Runs ONCE, called from ``write()`` immediately after
        ``self._validate_registry_key_references()`` and before
        ``prepare_writing()`` (D-04) -- so a refusal leaves ZERO ``.typ``
        files on disk, exactly like this class's other two pre-write
        validators. This is the FIRST read of ``self.config.templates_path``
        anywhere in ``typsphinx/``.

        The checked key set for kinds 1 and 2 (D-05) is derived from every
        USABLE ``typst_documents`` entry
        (``_is_usable_typst_documents_entry()``), resolved through
        ``resolve_registry_key()`` -- including the entry
        ``_default_typst_documents()`` synthesizes when ``typst_documents``
        is unset -- never ``self._used_template_keys`` (still empty at
        this point in the build). This is reference-derived scope,
        applying to kinds 1 and 2 ONLY (kind 3's declaration-derived scope
        is documented above). A registry key that is DECLARED but
        referenced by no ``typst_documents`` entry is deliberately NOT
        checked by kinds 1/2 (Claude's Discretion, "do not widen"
        recommendation): their checked set stays reference-derived,
        matching ``_validate_registry_key_references()``'s own scope;
        such a key is still caught at ``finish()`` if it ever becomes
        used.

        For each used key, this method reproduces
        ``_copy_used_template_bundles()``'s own per-key resolution
        construction exactly (``template_path``, ``search_paths``,
        ``resolve_package_for_engine()``, ``TemplateEngine``,
        ``resolve_template()``) to obtain the RESOLVED bundle path -- never
        the declared string -- because the declared value and the resolved
        path genuinely differ for the ``"search"`` and ``"default"``
        priorities. D-06 already accepts this write()-vs-finish()
        duplication as the cost of covering both call paths. This
        resolution now runs for EVERY used key regardless of whether
        ``templates_path`` is even set, because the CONF-17 hoist check
        needs it unconditionally.

        A key whose entry carries ``package`` and no ``template`` has no
        bundle and is skipped, mirroring
        ``_copy_used_template_bundles()``'s own skip.

        The CONF-17 hoist check runs UNCONDITIONALLY on the resolved
        path, checked and appended (then ``continue``s to the next key)
        BEFORE the ``resolution.source == "default"`` skip below --
        unlike the ``templates_path`` branch, it does NOT skip
        ``source == "default"``: the packaged default's parent directory
        lives inside the installed Python package and can never be
        ``srcdir`` or an ancestor of it, so the CONF-17 predicate simply
        returns ``False`` for it and no special-case is warranted. The
        ``templates_path`` containment check for that SAME key is skipped
        when the key already violated CONF-17 (a template that already
        fails CONF-17 has nothing useful to say about ``templates_path``
        containment, and reporting both would be noise), and is skipped
        separately when ``resolution.source == "default"`` -- the
        packaged default's bundle lives inside the installed Python
        package, never under ``srcdir``, so the containment test is
        meaningless for it (and could be misleading under an editable
        install).

        ``templates_path`` entries are resolved against ``self.srcdir``
        (D-02), matching every other path resolution in this file. A
        project using Sphinx's separate ``-c`` confdir option is NOT
        covered by this method -- ``confdir`` defaults to ``srcdir`` in
        the near-universal case, but this method never reads
        ``self.confdir``. A non-``str`` ``templates_path`` member is
        skipped defensively rather than raising -- Sphinx already
        type-validates this config value as a list, and a malformed
        member is not this method's error class.

        Containment (``_paths_related()``) is case-folded unconditionally
        on every platform via ``TypstBuilder._collision_key()`` -- this
        repository's Linux CI must catch what only a case-insensitive
        filesystem would otherwise surface. Unicode normalization
        (NFC/NFD) is NOT applied, matching ``_collision_key()``'s own
        documented non-normalization.

        Multiple colliding keys, across ALL THREE failure kinds, are
        accumulated into ONE ``failures`` list and raised as a SINGLE
        ``ExtensionError``, iterated in ``sorted()`` key order (D-03), so
        the message is byte-identical across runs -- never a
        first-offender raise. The summary prefix
        (``"typst: N pre-write template path failure(s)"``) is
        deliberately failure-kind-neutral, feeding every kind into this
        SAME list.

        Raises:
            ExtensionError: When one or more used keys' resolved template
                bundle directories collide with a ``templates_path``
                entry, violate A-01/CONF-17, or when a declared registry
                key differs from the reserved built-in key only by case.
                Each ``templates_path`` failure message names the
                registry key, the resolved bundle directory, the
                colliding ``templates_path`` entry (both the raw config
                string and its resolved absolute path), the consequence
                (the whole bundle directory would be copied to build
                output, republishing this Sphinx template directory), and
                the remedy (move the Typst template into a directory
                that is not on ``templates_path`` -- this repository
                uses ``_typst/`` -- and update ``typst_template`` /
                ``typst_document_templates`` to match). Each CONF-17
                failure message is built by ``_conf17_violation_message()``,
                shared byte-for-byte with the ``finish()``-side guard.
                Each reserved-key case-collision failure message names
                the declared key and the reserved built-in key, states
                that both fold to the same bundle destination, states
                that CONF-18 does not catch it, and tells the user to
                rename the declared key or configure the built-in key
                through the global Typst template settings instead.
        """
        typst_documents = getattr(self.config, "typst_documents", []) or []
        used_keys: Set[str] = set()
        for entry in typst_documents:
            if not _is_usable_typst_documents_entry(entry):
                continue
            resolved_entry = resolve_registry_key(
                self._document_template_registry, entry
            )
            used_keys.add(resolved_entry.key)

        raw_templates_path = getattr(self.config, "templates_path", []) or []
        templates_path_entries: List[Tuple[str, str]] = []
        for raw_entry in raw_templates_path:
            if not isinstance(raw_entry, str):
                continue
            templates_path_entries.append(
                (raw_entry, path.join(str(self.srcdir), raw_entry))
            )

        failures: List[Tuple[str, str]] = []

        from typsphinx.template_registry import RESERVED_REGISTRY_KEY

        # D-07: reserved-key case-collision check (kind 3) -- scoped to
        # every DECLARED registry key, not the reference-derived
        # used_keys set kinds 1/2 below use (see docstring). Routes
        # exclusively through the existing _collision_key() folding --
        # never a second case-folding primitive.
        reserved_folded = self._collision_key(RESERVED_REGISTRY_KEY)
        for declared_key in sorted(self._document_template_registry):
            if declared_key == RESERVED_REGISTRY_KEY:
                continue
            if self._collision_key(declared_key) == reserved_folded:
                failures.append(
                    (
                        declared_key,
                        f"registry key {declared_key!r} differs from "
                        f"the built-in {RESERVED_REGISTRY_KEY!r} "
                        "registry key only by case -- both resolve to "
                        "the same bundle destination under the "
                        "output-path folding this project applies on "
                        "every platform; CONF-18 does not catch this "
                        "because it compares declared keys only "
                        "against each other and never against the "
                        f"synthesized built-in key -- rename "
                        f"{declared_key!r} to something that does not "
                        "fold to the reserved key, or drop it and "
                        "configure the built-in key through the "
                        "global Typst template settings "
                        "(typst_template / typst_package)",
                    )
                )

        if used_keys:
            from typsphinx.template_engine import (
                TEMPLATE_SEARCH_SUBDIR,
                TemplateEngine,
                resolve_package_for_engine,
            )
            from typsphinx.template_registry import _violates_conf17

            for key in sorted(used_keys):
                entry = self._document_template_registry[key]

                if entry.package and not entry.template:
                    # Package-alone: no bundle to check (mirrors
                    # _copy_used_template_bundles()'s own skip).
                    continue

                raw_template_path = entry.template
                template_path = None
                if raw_template_path:
                    template_path = path.join(self.srcdir, raw_template_path)
                search_paths = [path.join(str(self.srcdir), TEMPLATE_SEARCH_SUBDIR)]
                package_for_engine = resolve_package_for_engine(
                    entry.package, raw_template_path
                )

                template_engine = TemplateEngine(
                    template_path=template_path,
                    search_paths=search_paths,
                    typst_package=package_for_engine,
                    typst_template_function=entry.template_function,
                )
                resolution = template_engine.resolve_template()

                # CR-01/D-04/D-05/D-06: hoisted A-01/CONF-17 check.
                # Unlike the templates_path branch below, this does NOT
                # skip resolution.source == "default" -- the packaged
                # default's parent directory can never be srcdir or an
                # ancestor of it, so the CONF-17 predicate simply returns
                # False for it and no special-case is warranted.
                if _violates_conf17(str(resolution.path), str(self.srcdir)):
                    failures.append(
                        (
                            key,
                            _conf17_violation_message(
                                key, str(resolution.path), str(self.srcdir)
                            ),
                        )
                    )
                    # A template that already violates CONF-17 has
                    # nothing useful to say about templates_path
                    # containment -- reporting both for one key is noise.
                    continue

                if resolution.source == "default":
                    # The packaged default's bundle lives inside the
                    # installed Python package, never under srcdir --
                    # containment against a srcdir-relative
                    # templates_path entry is meaningless for it.
                    continue

                if templates_path_entries:
                    bundle_dir = path.dirname(str(resolution.path))

                    for raw_tp_entry, resolved_tp_entry in templates_path_entries:
                        if _paths_related(bundle_dir, resolved_tp_entry):
                            failures.append(
                                (
                                    key,
                                    _templates_path_collision_message(
                                        key,
                                        bundle_dir,
                                        raw_tp_entry,
                                        resolved_tp_entry,
                                    ),
                                )
                            )

        if failures:
            summary = "; ".join(f"{key!r}: {message}" for key, message in failures)
            raise ExtensionError(
                f"typst: {len(failures)} pre-write template path "
                f"failure(s): {summary}"
            )

    def get_outdated_docs(self) -> Iterator[str]:
        """
        Return an iterator of document names that need to be rebuilt.

        For now, we rebuild all documents on every build.

        Returns:
            Iterator of document names that are outdated
        """
        for docname in self.env.found_docs:
            yield docname

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        """
        Return the target URI for a document.

        Deliberately stays docname-based and does NOT follow the
        typst_documents target-name rename that ``_resolve_target_stem``
        applies to the on-disk filename via ``_wrapper_output_relpath``
        (Phase 22 / Issue #117). Its only
        consumer is ``translator.py:_resolve_xref_docname``, which uses this
        method as a round-trip identity to recover a cross-referenced
        document's DOCNAME from a refuri that Sphinx itself computed via
        ``Builder.get_relative_uri`` -- i.e.
        ``relative_uri(get_target_uri(from_), get_target_uri(to))``, so both
        endpoints pass through this same function. Every emitted Typst
        label is namespaced by SOURCE DOCNAME via
        ``translator.py:_namespace_label``, never by output filename.
        Making this method target-name-aware would desynchronize the
        recovered docname from the label namespace and break every
        cross-document link into or out of a renamed master with a Typst
        "label ... does not exist" compile fatal. This is a deliberate
        Phase 22 decision -- do not "fix" it in sympathy with the
        write-path rename.

        Args:
            docname: Name of the document
            typ: Type of the target (not used for Typst builder)

        Returns:
            Target URI string
        """
        return docname + self.out_suffix

    def prepare_writing(self, docnames: Set[str]) -> None:
        """
        Prepare for writing the documents.

        This method is called before writing begins. Creates the writer
        instance every wrapper/content write below uses; the per-key
        template bundle each wrapper imports is copied later, at
        ``finish()`` time (Phase 54, OUT-04), fed by the write-time
        ``self._used_template_keys`` accumulator -- not written here.

        Args:
            docnames: Set of document names to be written
        """
        # Create the writer instance
        self.writer = TypstWriter(self)

    def write(
        self,
        build_docnames: Set[str] | None,
        updated_docnames: Set[str],
        method: str = "update",
    ) -> None:
        """
        Override write() to preserve toctree nodes.

        By default, Sphinx's Builder.write() calls env.get_and_resolve_doctree()
        which expands toctree nodes into compact_paragraph with links.
        For Typst, we need the original toctree nodes to generate #include() directives.

        This method uses env.get_doctree() instead to preserve toctree nodes.

        Args:
            build_docnames: Document names to build (None = all)
            updated_docnames: Document names that were updated
            method: Build method ('update' or 'all')
        """
        if build_docnames is None or build_docnames == ["__all__"]:
            # build_all
            build_docnames = self.env.found_docs
        if method == "update":
            # build updated and specified
            docnames = set(build_docnames) | set(updated_docnames)
        else:
            # build all
            docnames = set(build_docnames)

        # D-02/D-03: validate BEFORE anything is written -- the per-docname
        # content and wrapper files below are the first things write()
        # produces on disk. Placed here, at the very top of write(), so a
        # collision leaves ZERO ".typ" files on disk (BLD-02's own gate
        # asserts no ".typ" file anywhere in the build directory).
        # TypstPDFBuilder inherits this unchanged (D-03).
        self._validate_output_path_collisions()

        # Phase 53 (TPL-03, D-03/D-09): resolve the template registry
        # ONCE per build, here -- after collision validation, before
        # `prepare_writing()` and the per-docname write loop below -- so
        # resolution is order-independent and every wrapper this write()
        # writes below sees the SAME resolved registry. Mirrors
        # `self._master_include_edges = self._build_include_edge_map()`
        # a few lines down.
        self._document_template_registry = resolve_template_registry(
            self.config, str(self.srcdir)
        )

        # Phase 53 plan 06 (CONF-14, ROADMAP SC#3): validate every usable
        # typst_documents entry's registry key reference HERE, before
        # prepare_writing() writes anything, so a bad key leaves ZERO
        # ".typ" files on disk regardless of that entry's docname sort
        # position -- covers EVERY declared entry, not only ones in this
        # build's docnames set (D-05), which is what makes the guarantee
        # order-independent.
        self._validate_registry_key_references()

        # Phase 54.1 (WR-01, D-04): validate every used registry key's
        # RESOLVED template bundle directory against templates_path HERE,
        # before prepare_writing() writes anything, so a collision leaves
        # ZERO ".typ" files on disk -- the wholesale bundle copy at
        # finish() would otherwise republish the project's own Sphinx
        # templates_path directory into build output.
        self._validate_used_template_paths()

        logger.info("preparing documents... ", nonl=True)
        self.prepare_writing(docnames)
        logger.info("done")

        # Phase 49 (COMP-05/COMP-06): derive the per-master include-edge
        # mapping UNCONDITIONALLY at the same position the deleted
        # write-time ledger's reset used to occupy -- after
        # prepare_writing() (so self.env.toctree_includes is fully
        # populated), before the per-docname write loop below (so every
        # wrapper this write() writes sees a freshly-derived, non-stale
        # mapping). Re-derived on every write() call so re-builds and
        # multiple write() invocations never carry stale edges across
        # masters -- mirrors the deleted ledger's own "clean start per
        # write()" contract, but the mapping itself is DERIVED, never
        # accumulated by mutation during writing.
        self._master_include_edges = self._build_include_edge_map()

        # Write individual documents
        warnings_count = 0
        for docname in sorted(docnames):
            # Use env.get_doctree() instead of env.get_and_resolve_doctree()
            # to preserve toctree nodes (Requirement 13.2)
            doctree = self.env.get_doctree(docname)
            self.env.apply_post_transforms(doctree, docname)

            # Log progress
            logger.info(f"writing output... [{docname}]", nonl=True)

            # Write the document
            self.write_doc(docname, doctree)

            logger.info(" done")

        # D-07: name the wrapper files this build wrote and state that
        # those are the files to compile. After the content/wrapper
        # split the outdir holds roughly twice as many .typ files as
        # before, with nothing in a filename alone distinguishing a
        # content file from a wrapper -- `-b typstpdf` already emits its
        # own "Compiling N master document(s)"/"Generated PDF" lines;
        # this is the missing symmetric message on the markup-only
        # builder. The _is_usable_typst_documents_entry() filter (BLD-03)
        # is what keeps this report from ever naming a path for an entry
        # the write-phase wrapper loop actually skipped -- a fourth
        # drift site 47-VERIFICATION.md did not enumerate: without it
        # this report would claim a wrapper file that was never written.
        typst_documents = getattr(self.config, "typst_documents", []) or []
        wrapper_relpaths = sorted(
            self._wrapper_output_relpath(entry) + ".typ"
            for entry in typst_documents
            if _is_usable_typst_documents_entry(entry) and entry[0] in docnames
        )
        if wrapper_relpaths:
            logger.info(
                f"typst: wrote {len(wrapper_relpaths)} wrapper file(s) -- "
                f"compile these: {', '.join(wrapper_relpaths)}"
            )

    def post_process_images(self, doctree: nodes.document) -> None:
        """
        Post-process images in the document tree.

        Collects all image nodes from the document tree and tracks them
        in self.images dictionary for later copying to the output directory.

        For a `*`-glob image URI (e.g. ``.. figure:: _static/foo.*``),
        Sphinx's read-phase ImageCollector leaves ``node["uri"]`` as the
        literal, unresolved glob string and instead records the concrete
        on-disk candidates in ``node["candidates"]`` keyed by mimetype --
        resolving that to one concrete file is the builder's responsibility
        (mirrors ``sphinx.builders.Builder.post_process_images``, as done by
        the HTML/LaTeX builders via their own ``supported_image_types``).
        This picks the best Typst-embeddable candidate and rewrites
        ``node["uri"]`` to the resolved path, so both the translator's
        ``visit_image`` (emits the path into the ``.typ``) and
        ``copy_image_files()`` (copies the file) see the concrete file.

        Doctrees that never passed through Sphinx's ``ImageCollector`` (e.g.
        hand-built doctrees in unit tests) have no ``candidates`` attribute
        at all; those fall back to the original bare-URI tracking so that
        behavior stays unchanged.

        Args:
            doctree: Document tree to process
        """
        from docutils.nodes import image

        for node in doctree.findall(image):
            candidates = node.get("candidates")
            if not candidates:
                # No candidates dict -- doctree never went through Sphinx's
                # ImageCollector (e.g. a hand-built test doctree). Preserve
                # the original bare-URI behavior.
                imguri = node.get("uri", "")
                if not imguri:
                    continue
                self._track_image(node, imguri)
                continue

            if "?" in candidates:
                # Non-local URI (data: URI or remote http(s):// image) --
                # nothing on disk to resolve or copy.
                continue

            if "*" in candidates:
                # Already a single concrete candidate (the common, non-glob
                # case -- ImageCollector sets candidates["*"] = node["uri"]).
                resolved_uri = candidates["*"]
            else:
                # Glob URI with multiple mimetype-keyed candidates. Pick the
                # best Typst-supported type, in preference order, and
                # rewrite node["uri"] to the concrete resolved path.
                resolved_uri = None
                for imgtype in self.supported_image_types:
                    candidate = candidates.get(imgtype)
                    if candidate:
                        resolved_uri = candidate
                        break
                if resolved_uri is None:
                    # No candidate matches a Typst-supported mimetype --
                    # degrade gracefully (warn, skip) rather than crash.
                    mimetypes = sorted(candidates)
                    logger.warning(
                        f"a suitable image for typst builder not found: "
                        f"{mimetypes} ({node.get('uri', '')})"
                    )
                    continue
                node["uri"] = resolved_uri

            if not resolved_uri:
                continue

            self._track_image(node, resolved_uri)

    def _track_image(self, node: nodes.image, resolved_uri: str) -> None:
        """
        Track a resolved image URI for later copying by copy_image_files().

        Sphinx's ``ImageConverter``/``ImageDownloader`` post-transforms
        rewrite ``node["uri"]`` to an ABSOLUTE filesystem path under
        ``<doctreedir>/images/...`` when an image needs conversion or
        download -- unlike ordinary images, which stay source-root-relative
        (Issue #130). ``os.path.join(srcdir_or_outdir, uri)`` silently
        discards its first argument once ``uri`` is absolute, so an
        unrehomed absolute URI makes ``copy_image_files()`` collapse ``src``
        and ``dest`` onto the identical path ("are the same file") and
        makes the translator's ``_compute_relative_image_path()`` prepend a
        bogus ``../..`` depth prefix onto an already-absolute path.

        An absolute ``resolved_uri`` is rehomed here to a
        ``doctreedir``-relative path (e.g. ``"images/foo.png"``), fitting
        the same source-root-relative convention ordinary images use, with
        the true absolute location kept as the ``self.images`` value so
        ``copy_image_files()`` can use it as the real copy source.

        Phase 50 widens the rehome with two further, filesystem-probed
        outcomes (IMG-01/IMG-02), both routed through the SAME reserved
        ``RESERVED_IMAGE_NAMESPACE`` top-level namespace so
        ``copy_image_files()`` still copies the file and every destination
        it computes (``path.join(self.outdir, imguri)``) lands under
        ``outdir`` -- a relocated key never carries a leading ``..``:

        - **Collision (D-01/D-02/D-03/D-04):** if a REAL source image
          already occupies the rehome target --
          ``path.isfile(path.join(self.srcdir, rel_uri))`` -- the converted
          image is relocated under the reserved namespace instead,
          SILENTLY. The probe is against the FILESYSTEM, never against
          ``self.images``' own accumulated keys: ``write()`` iterates
          ``sorted(docnames)``, so the real source image and the converted
          image can be tracked in either order depending on docname
          alphabetization, and a dict-membership check would make the
          outcome depend on that order (reintroducing exactly the
          write-order dependence D-02 rejects). A filesystem probe answers
          the same question regardless of traversal order.
        - **Escape (D-05/D-06/D-07):** if the rehome result would escape
          ``doctreedir`` -- a leading parent-traversal segment, detected by
          ``_escapes_outdir()`` -- or ``path.relpath()`` itself raises
          ``ValueError`` (the Windows cross-drive case, caught around the
          ``relpath()`` call itself so the crash path is closed), the
          image is likewise relocated under the reserved namespace, but
          WITH a warning: reaching this branch means a third-party
          extension placed an absolute URI somewhere none of Sphinx's own
          post-transforms ever write (``ImageDownloader``,
          ``DataURIExtractor`` and ``ImageConverter`` all write under
          ``<doctreedir>/images``).

        The common, non-colliding, non-escaping case (today's behavior and
        today's emitted path) is preserved unchanged -- this is the branch
        the D-12-pinned regression tests exercise.

        BLD-09 (Phase 55): the absolute-URI decision above is a
        platform-independent string shape owned by the module-level
        ``_is_absolute_image_uri`` predicate, not the OS-native
        absolute-path check this method used before. A
        rooted URI that escapes this gate reaches ``copy_image_files()``,
        where the platform's own destination join (``path.join(self.outdir,
        imguri)``) silently discards ``outdir`` once ``imguri`` is itself
        rooted -- which is why this gate is the containment boundary for
        every destination this builder writes, and not merely a
        convenience rewrite.

        Args:
            node: The image node whose ``uri`` should reflect the tracked
                path.
            resolved_uri: The concrete URI to track (already resolved from
                ``node["candidates"]`` by the caller).
        """
        # BLD-09: the platform-independent predicate, not the OS-native
        # absolute-path check -- see that helper's own docstring for the
        # measured reasoning (CPython 3.13's narrowed Windows behaviour and
        # the backslash-normalized widening Task 2's checkpoint selected).
        if _is_absolute_image_uri(resolved_uri):
            try:
                rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(
                    path.sep, "/"
                )
                # Cross-domain reuse: _escapes_outdir() is documented as a
                # typst_documents target-stem guard (OUT-02), but its body
                # is a pure string-shape test with no typst_documents
                # state threaded through it, so it answers the same "does
                # this relative path escape its base directory" question
                # for a rehomed image path too. Re-evaluate this call site
                # if that helper's contract is ever narrowed to something
                # OUT-02-specific.
                escaped = _escapes_outdir(rel_uri)
            except ValueError:
                # D-07: Windows cross-drive relpath() crash -- there is no
                # meaningful doctreedir-relative path to compute at all,
                # so treat this identically to an escape.
                rel_uri = ""
                escaped = True

            if escaped:
                # D-05/D-06: rehome result points outside doctreedir (or
                # could not be computed at all) -- relocate under the
                # reserved namespace and WARN, because reaching this
                # branch means a third-party extension placed an absolute
                # URI somewhere none of Sphinx's own post-transforms ever
                # do.
                #
                # IMG-04/IMG-06 (Phase 59): key construction extracted to
                # _build_relocation_key() -- see that function's own
                # docstring for the IMG-03 collision-anchor rationale it
                # carries forward, the IMG-04 normalize-then-basename
                # ordering, and the IMG-06 255-byte bound.
                key = _build_relocation_key(resolved_uri)
                logger.warning(
                    f"could not rehome image URI {resolved_uri!r} relative "
                    f"to the doctree directory -- relocated to {key!r}"
                )
            elif path.isfile(path.join(self.srcdir, rel_uri)):
                # D-01/D-03/D-04: a REAL source image already occupies the
                # target this rehome would produce -- relocate under the
                # same reserved namespace, SILENTLY (an ordinary, expected
                # shape for any project combining an images/ srcdir
                # layout with an image-conversion extension). Probed
                # against the FILESYSTEM, never against self.images -- see
                # this method's own docstring for why.
                key = f"{RESERVED_IMAGE_NAMESPACE}/{rel_uri}"
            else:
                # D-01: no collision -- today's behavior and today's
                # emitted path are preserved unchanged. This is the
                # branch all three D-12-pinned test assertions exercise.
                key = rel_uri

            node["uri"] = key
            if key not in self.images:
                self.images[key] = resolved_uri
            return

        # Store empty string as value to be compatible with parent class type
        if resolved_uri not in self.images:
            self.images[resolved_uri] = ""

    def _content_output_path(self, docname: str) -> str:
        """Return this docname's content file's absolute on-disk path
        (COMP-01/OUT-03).

        Unconditional, and a pure function of the docname alone -- a
        docname already carries its own ``/``-separated directory, so this
        needs no target resolution at all (COMP-01/OUT-03). Every docname
        gets a content file, regardless of whether any ``typst_documents``
        entry names it.

        Args:
            docname: The Sphinx document name being written.

        Returns:
            The content file's absolute on-disk path.
        """
        return path.normpath(path.join(self.outdir, docname + ".typ"))

    def _wrapper_output_relpath(self, entry: tuple) -> str:
        """Return the outdir-relative wrapper path (no suffix) for one
        ``typst_documents`` entry.

        OUT-01: the resolved stem is returned AS-IS, interpreted directly
        as a path relative to outdir -- no directory forcing.

        Resolves the entry's OWN target directly, via
        ``_resolve_target_stem(entry[0], entry[1])`` -- the only
        target-resolution route in the package. This is what makes D-04's
        repeated-docname case correct: two entries naming the same docname
        with different targets each get THEIR OWN wrapper path, rather
        than both resolving via whichever entry a docname search happens
        to find first (the gap ``47-02-SUMMARY.md`` and
        ``47-06-SUMMARY.md`` both named as deferred to this plan).

        Args:
            entry: The specific ``typst_documents`` tuple to resolve a
                wrapper path for.

        Returns:
            The outdir-relative wrapper path (no suffix).
        """
        docname = entry[0]
        target = entry[1] if len(entry) >= 2 else None
        return self._resolve_target_stem(docname, target)

    def _write_typst_files(self, docname: str, doctree: nodes.document) -> None:
        """Write this docname's content file, then every wrapper file for
        a ``typst_documents`` entry naming it.

        This is the ONE shared write path both ``TypstBuilder.write_doc``
        and ``TypstPDFBuilder.write_doc`` use -- byte-identical ``.typ``
        output across both builders is therefore structural (a single
        code path both builders run), not a maintained coincidence
        between two near-duplicate bodies.

        Requirement 13.1: 各 reStructuredText ファイルに対応する独立した
        .typ ファイルを生成する

        Requirement 13.12: ソースディレクトリ構造を保持して出力する

        Args:
            docname: Name of the document
            doctree: Document tree to be written
        """
        # Set current docname for template application logic
        self.current_docname = docname

        # Post-process images to track them for copying
        self.post_process_images(doctree)

        # Set the document on the writer
        self.writer.document = doctree

        # Write the CONTENT file -- unconditional, docname-derived
        # (COMP-01/OUT-03), regardless of any typst_documents entry.
        content_destination = self._content_output_path(docname)
        ensuredir(path.dirname(content_destination))
        self.writer.translate()
        with open(content_destination, "w", encoding="utf-8") as f:
            f.write(self.writer.output)

        content_relative_path = docname + ".typ"

        # Write a WRAPPER file for every typst_documents entry naming
        # this docname (D-04: two entries may name the same docname,
        # each producing its own wrapper -- see D-08 for title/author).
        # This is the ACTUAL data-destruction site BLD-03 closes: before
        # _is_usable_typst_documents_entry() existed, this loop's guard
        # tolerated a 1-element entry (`entry[0] != docname` alone) that
        # the collision validator already skipped, so a self-including
        # wrapper was written directly OVER the docname's own content
        # file this method just wrote above.
        typst_documents = getattr(self.config, "typst_documents", []) or []

        # Phase 49 (COMP-05/COMP-06): lazily derive the per-master
        # include-edge mapping if it is still empty. `write()` already
        # derives it unconditionally BEFORE the per-docname write loop
        # for a normal build; this is a fallback for the direct-call
        # per-document write path several existing unit tests use, which
        # invoke `write_doc()`/`_write_typst_files()` directly without
        # ever calling `write()`. This calls the SAME derivation function
        # (`_build_include_edge_map()`) `write()` itself calls -- it is a
        # lazy initialisation of one derivation point, NOT a second
        # include-decision mechanism.
        if not self._master_include_edges:
            self._master_include_edges = self._build_include_edge_map()

        # Phase 53 (TPL-03): lazily resolve the template registry if it is
        # still empty -- the SAME fallback shape as `_master_include_edges`
        # above, calling the SAME resolution function `write()` itself
        # calls. Load-bearing: many existing tests drive `write_doc()` /
        # `_write_typst_files()` directly without ever calling `write()`,
        # and without this fallback the registry would be empty for them.
        if not self._document_template_registry:
            self._document_template_registry = resolve_template_registry(
                self.config, str(self.srcdir)
            )

        for entry in typst_documents:
            if not _is_usable_typst_documents_entry(entry) or entry[0] != docname:
                continue
            wrapper_relpath = self._wrapper_output_relpath(entry)
            wrapper_destination = path.normpath(
                path.join(self.outdir, wrapper_relpath + ".typ")
            )
            ensuredir(path.dirname(wrapper_destination))
            wrapper_relative_dir = posixpath.dirname(wrapper_relpath)
            edge_keys = self._master_include_edges.get(docname, ())
            template_entry = resolve_registry_key(
                self._document_template_registry, entry
            )
            # Phase 54 (OUT-04): record this ACTUALLY-WRITTEN wrapper's
            # resolved registry key -- the finish()-time bundle copy
            # (`_copy_used_template_bundles()`) iterates exactly this
            # set, so a key no wrapper ever names gets no bundle copied
            # for it.
            self._used_template_keys.add(template_entry.key)
            wrapper_output = self.writer.render_wrapper(
                entry,
                doctree,
                wrapper_relative_dir,
                content_relative_path,
                edge_keys=edge_keys,
                template_entry=template_entry,
            )
            with open(wrapper_destination, "w", encoding="utf-8") as f:
                f.write(wrapper_output)

    def write_doc(self, docname: str, doctree: nodes.document) -> None:
        """
        Write a document.

        This method is called for each document that needs to be written.
        Delegates to ``_write_typst_files()``, the single write path
        shared with ``TypstPDFBuilder`` (which inherits this method
        unchanged).

        Args:
            docname: Name of the document
            doctree: Document tree to be written
        """
        self._write_typst_files(docname, doctree)

    def copy_image_files(self) -> None:
        """
        Copy image files to the output directory.

        Iterates through all tracked images and copies them from the
        source directory to the output directory, preserving relative paths.
        """
        if not self.images:
            return

        logger.info(f"Copying {len(self.images)} image file(s)...")

        for imguri, override_src in self.images.items():
            # Resolve source path. Image URIs are relative to source
            # directory, EXCEPT when _track_image() stashed the true
            # absolute source location here (Issue #130) -- e.g. a
            # converted/downloaded image, which never lived under srcdir.
            src = override_src if override_src else path.join(self.srcdir, imguri)

            # Resolve destination path
            dest = path.join(self.outdir, imguri)

            # Check if source file exists
            if not path.exists(src):
                logger.warning(f"Image file not found: {src}")
                continue

            # Ensure destination directory exists
            dest_dir = path.dirname(dest)
            ensuredir(dest_dir)

            # Copy the file
            try:
                shutil.copy2(src, dest)
                logger.debug(f"Copied image: {imguri}")
            except Exception as e:
                logger.warning(f"Failed to copy image {imguri}: {e}")

    def _copy_bundle_directory(
        self, src_dir: str, dest_dir: str, key: str, template_filename: str
    ) -> None:
        """Copy one registry key's resolved template bundle wholesale
        from ``src_dir`` to ``dest_dir`` (OUT-04) via ``os.walk()`` +
        ``shutil.copy2`` (D-02): no ``.typ`` skip (the template body
        travels this SAME path, not a separate write -- this is the
        ONLY route from a template directory to the output tree), a
        name-based exclusion for exactly D-04's four kinds
        (``_is_excluded_bundle_entry()``), and a fatal/non-fatal error
        split (D-05) keyed on whether the file being copied IS the
        resolved template file itself.

        An existing destination file is overwritten in place; this
        method never deletes anything under ``dest_dir`` first (D-01) --
        a destination file absent from ``src_dir`` is left alone,
        accepted behaviour on an incremental rebuild.

        Args:
            src_dir: The resolved template's own parent directory (the
                bundle source), an ABSOLUTE path -- the bundled
                ``"typst"`` key's source lives inside the installed
                package, not under ``srcdir``, so this is never assumed
                to be ``srcdir``-relative.
            dest_dir: ``<outdir>/_template/<key>/``, an ABSOLUTE path.
            key: The registry key this bundle belongs to (named in the
                ``ExtensionError`` message on a fatal failure).
            template_filename: The resolved template's own basename
                (e.g. ``"base.typ"``) -- the ONE file in this bundle
                whose copy failure, or absence after the walk, is FATAL
                rather than a warn-and-continue (D-05).

        Raises:
            ExtensionError: When copying the resolved template file
                itself fails, or when it was never found under
                ``src_dir`` at all -- ``-b typst`` must not report
                success over an output that cannot compile.
        """
        import os

        template_copied = False
        for root, dirs, files in os.walk(src_dir, followlinks=False):
            dirs[:] = [d for d in dirs if not _is_excluded_bundle_entry(d)]
            for file in files:
                if _is_excluded_bundle_entry(file):
                    continue
                src_file = path.join(root, file)
                rel_path = path.relpath(src_file, src_dir)
                dest_file = path.join(dest_dir, rel_path)
                is_template_file = rel_path.replace(path.sep, "/") == template_filename
                ensuredir(path.dirname(dest_file))
                try:
                    shutil.copy2(src_file, dest_file)
                    logger.debug(f"Copied bundle file for {key!r}: {rel_path}")
                    if is_template_file:
                        template_copied = True
                except Exception as e:
                    if is_template_file:
                        raise ExtensionError(
                            f"typst_document_templates: failed to copy the "
                            f"resolved template for registry key {key!r} "
                            f"from {src_file!r} to {dest_file!r}: {e}"
                        ) from e
                    logger.warning(
                        f"Failed to copy template bundle file {rel_path}: {e}"
                    )

        if not template_copied:
            raise ExtensionError(
                f"typst_document_templates: the resolved template for "
                f"registry key {key!r} ({template_filename!r}) was never "
                f"copied from {src_dir!r} to {dest_dir!r} -- a wrapper "
                "naming this key would import a file that does not exist"
            )

    def _copy_used_template_bundles(self) -> None:
        """Copy every USED registry key's resolved template bundle
        wholesale to ``<outdir>/_template/<key>/`` (OUT-04) -- the ONLY
        route from a template directory to the output tree. Called once
        from ``finish()``, fed by the write-time
        ``self._used_template_keys`` accumulator (mirrors
        ``self.images``/``copy_image_files()``, ROADMAP constraint #4).

        Returns immediately when the accumulator is empty -- a build
        that writes no wrapper creates no ``<outdir>/_template/``
        directory at all.

        Iterates ``sorted(self._used_template_keys)`` so log and error
        order is deterministic across runs of the same project (D-05's
        byte-identical property, mirroring
        ``resolve_template_registry()``'s own ``sorted()`` use).

        A key whose registry entry carries a ``package`` and no
        ``template`` has nothing to copy -- a package-alone master has
        no bundle -- and is skipped, matching
        ``render_wrapper()``'s own package-alone predicate exactly
        (``entry.package and not entry.template``).

        A key whose registry entry carries BOTH a ``package`` and a
        ``template`` is unsupported (D-03 -- the template wins, the
        package is ignored, mirroring ``resolve_package_for_engine()``'s
        own routing) and gets a ``logger.warning`` naming the key, ONCE
        per build here -- this warning used to be hosted by the
        single-file writer Phase 54 deleted from this class;
        ``render_wrapper()`` (``writer.py``) has no equivalent
        per-document warning of its own, so dropping this one silently
        would have been a genuine user-facing regression (T-54-20).

        A-01 (resolved ``54-CONTEXT.md`` assumption, not an open
        question): applies the SAME parent-directory predicate CONF-17
        already applies to every DECLARED key's ``template`` to the
        RESOLVED path of EVERY used key, including the synthesized
        ``"typst"`` key -- D-14 removes ``srcdir`` itself from the
        search path list, but that alone does not cover a
        ``typst_template`` (or a registry entry's ``template``) set to a
        bare filename with no directory component, which resolves
        directly under ``srcdir``. Raised before any file for that key
        is copied.

        Two used keys whose destinations fold to the same
        ``<outdir>/_template/<key>/`` path (case-differing on a
        case-insensitive filesystem) are accumulated and raise ONE
        aggregated ``ExtensionError`` naming both keys and the shared
        destination, following ``_validate_output_path_collisions()``'s
        own accumulate-then-raise-once idiom -- routed through the SAME
        ``_collision_key()`` folding, never a second normalization
        primitive. Every key resolves and is destination-checked BEFORE
        any bundle is actually copied, so a collision leaves zero bundle
        files written for the colliding pair.

        Raises:
            ExtensionError: On an A-01 violation (immediate, per key),
                or once, aggregated, when two used keys collide on their
                bundle destination.
        """
        # Defensive getattr: several existing unit tests construct a
        # builder directly (`TypstPDFBuilder(app, env)`) and call
        # `finish()` without ever calling `init()` (Sphinx's own
        # `Builder.__init__` does not call it -- only `app._init_builder()`
        # does) or `write()`. Such a builder wrote no wrapper at all, so
        # "nothing to copy" is the CORRECT answer, not a crash -- mirrors
        # CONF-19's own `getattr(config, "_raw_config", {})` defensiveness
        # convention elsewhere in this codebase.
        if not getattr(self, "_used_template_keys", None):
            return

        import importlib.resources

        from typsphinx.template_engine import (
            TEMPLATE_SEARCH_SUBDIR,
            TemplateEngine,
            default_template_bundle_traversable,
            resolve_package_for_engine,
        )
        from typsphinx.template_registry import RESERVED_REGISTRY_KEY, _violates_conf17
        from typsphinx.writer import TEMPLATE_OUTPUT_DIR

        destinations: Dict[str, Tuple[str, str]] = {}
        failures: List[Tuple[str, str]] = []
        to_copy: List[Tuple[str, Any, str, str]] = []

        for key in sorted(self._used_template_keys):
            entry = self._document_template_registry[key]

            # D-03/T-54-20: when a used key carries BOTH a Typst Universe
            # package and a custom template, the combination is
            # unsupported -- the template wins (the same routing
            # `resolve_package_for_engine()` applies below and inside
            # `render_wrapper()`) and the package is ignored end-to-end.
            # Relocated here from the single-file writer Phase 54 deleted
            # so the warning still fires exactly once per build, rather
            # than being silently dropped. Only the synthesized RESERVED
            # "typst" key can ever reach this branch -- CONF-15 already
            # rejects a DECLARED `typst_document_templates` entry naming
            # both `template` and `package` at config-read time, before
            # this method ever runs -- so the message names the two
            # GLOBAL config values it is actually built from, matching
            # this warning's wording from before its relocation
            # (test_package_template_routing.py's own substring check
            # depends on this exact phrasing).
            if entry.package and entry.template:
                assert key == RESERVED_REGISTRY_KEY
                logger.warning(
                    "Both 'typst_package' and 'typst_template' are "
                    "configured; this combination is unsupported. "
                    "'typst_template' will be honoured and "
                    "'typst_package' will be ignored."
                )

            if entry.package and not entry.template:
                # Package-alone: no bundle to copy (mirrors
                # render_wrapper()'s own package-alone predicate).
                continue

            raw_template_path = entry.template
            template_path = None
            if raw_template_path:
                template_path = path.join(self.srcdir, raw_template_path)
            search_paths = [path.join(str(self.srcdir), TEMPLATE_SEARCH_SUBDIR)]
            package_for_engine = resolve_package_for_engine(
                entry.package, raw_template_path
            )

            template_engine = TemplateEngine(
                template_path=template_path,
                search_paths=search_paths,
                typst_package=package_for_engine,
                typst_template_function=entry.template_function,
            )
            resolution = template_engine.resolve_template()
            resolved_path = resolution.path

            # A-01 guard: apply CONF-17's predicate to the RESOLVED path
            # of this used key -- closes the explicit-route half of the
            # source-tree-republication hole D-14 closes structurally
            # for the search-path route.
            if _violates_conf17(str(resolved_path), str(self.srcdir)):
                raise ExtensionError(
                    _conf17_violation_message(key, str(resolved_path), str(self.srcdir))
                )

            dest_dir = path.join(self.outdir, TEMPLATE_OUTPUT_DIR, key)
            dest_relpath = posixpath.join(TEMPLATE_OUTPUT_DIR, key)
            dest_key = self._collision_key(dest_relpath)
            existing = destinations.get(dest_key)
            if existing is not None:
                failures.append(
                    (
                        key,
                        _bundle_destination_collision_message(
                            existing[0], key, dest_dir
                        ),
                    )
                )
                continue
            destinations[dest_key] = (key, dest_dir)
            to_copy.append((key, resolution, dest_dir, resolved_path.name))

        if failures:
            summary = "; ".join(f"{key!r}: {message}" for key, message in failures)
            raise ExtensionError(
                f"typst_document_templates: {len(failures)} bundle "
                f"destination collision(s): {summary}"
            )

        for key, resolution, dest_dir, template_filename in to_copy:
            ensuredir(dest_dir)
            if resolution.source == "default":
                # The packaged default's bundle lives inside the
                # installed package -- hold as_file()'s context open
                # around the ENTIRE copy, not just the path lookup, so a
                # non-filesystem loader cannot clean up a temporary
                # extraction mid-copy (T-54-10).
                with importlib.resources.as_file(
                    default_template_bundle_traversable()
                ) as bundle_dir:
                    self._copy_bundle_directory(
                        str(bundle_dir), dest_dir, key, template_filename
                    )
            else:
                bundle_src = str(resolution.path.parent)
                self._copy_bundle_directory(
                    bundle_src, dest_dir, key, template_filename
                )

    def finish(self) -> None:
        """
        Finish the build process.

        This method is called once after all documents have been written.
        Copies image files, then copies every USED registry key's
        resolved template bundle wholesale to
        ``<outdir>/_template/<key>/`` (Phase 54, OUT-04) -- the ONLY
        route from a template directory to the output tree. The
        parallel asset-copy path this bundle copy superseded (three
        early returns, plus the explicit-list expander and its
        single-asset copier) was deleted in this same plan (`54-05`);
        "has no bundle" is now a per-key property of
        ``_copy_used_template_bundles()`` itself, not a build-wide
        early return.
        """
        self.copy_image_files()
        self._copy_used_template_bundles()


class TypstPDFBuilder(TypstBuilder):
    """
    Builder class for generating PDF output directly from Typst.

    This builder extends TypstBuilder to compile generated .typ files
    to PDF using the typst-py package.

    Requirement 9.3: TypstPDFBuilder extends TypstBuilder
    Requirement 9.4: Generate PDF from Typst markup
    """

    name = "typstpdf"
    format = "pdf"
    out_suffix = ".pdf"

    # write_doc() is inherited unchanged from TypstBuilder (which
    # delegates to _write_typst_files()) -- both builders write .typ
    # content and wrapper files identically during the write phase; only
    # finish() differs, compiling the wrapper files to PDF afterward.
    # This is what makes `-b typst` and `-b typstpdf` emit byte-identical
    # .typ output structural (one shared code path) rather than a
    # maintained coincidence between two near-duplicate bodies.

    def finish(self) -> None:
        """
        Finish the build process by compiling Typst files to PDF.

        After the parent TypstBuilder has generated .typ files,
        this method compiles them to PDF using typst-py.

        Only master documents (defined in typst_documents) are compiled to PDF.
        Included documents are not compiled individually.

        Every configured master is attempted, even if an earlier one fails:
        masters that compile successfully still get their .pdf written. A
        master can fail for three reasons -- a Typst compile error, a
        configured master whose .typ file was never generated, or a
        malformed typst_documents entry -- and all three are collected into
        the same failures list and reported together by a single
        ExtensionError raised after every entry has been attempted. That
        raise surfaces as a non-zero sphinx-build exit -- a build can no
        longer "succeed" while silently producing no PDF for a broken,
        missing, or malformed master.

        Requirement 9.2: Execute Typst compilation within Python
        Requirement 9.4: Generate PDF from Typst markup
        """
        # First, call parent finish() to copy image files
        # This ensures images are available before PDF compilation
        super().finish()

        # Get master documents from typst_documents config
        typst_documents = getattr(self.config, "typst_documents", [])

        if not typst_documents:
            # D-03: since typst_documents gained a derived default
            # (CONF-08), this branch is reachable ONLY via an explicit
            # `typst_documents = []` -- unset now resolves through
            # _default_typst_documents instead of ever being empty. The
            # wording says so, rather than reading as if the setting were
            # absent.
            logger.warning(
                "typst_documents is explicitly set to an empty list -- "
                "nothing will be compiled. Remove the setting entirely to "
                "use the derived default (root_doc/project/author)."
            )
            return

        logger.info(f"Compiling {len(typst_documents)} master document(s) to PDF...")

        failures: List[Tuple[str, str]] = []

        for doc_tuple in typst_documents:
            # doc_tuple format: (sourcename, targetname, title, author).
            # Resolve the stem ONCE so the .typ read-back path and the .pdf
            # write path can never drift from each other (Issue #117).
            # Mirror _is_usable_typst_documents_entry()'s own falsy-entry
            # guard here: a malformed entry (e.g. an empty tuple from a
            # misconfigured typst_documents) must not raise an uncaught
            # IndexError on doc_tuple[0] before that predicate's defenses
            # ever run.
            if not doc_tuple:
                logger.warning(f"Malformed typst_documents entry: {doc_tuple!r}")
                failures.append((repr(doc_tuple), "malformed typst_documents entry"))
                continue
            docname = doc_tuple[0]
            # BLD-01: _is_usable_typst_documents_entry() would also reject
            # a non-str docname (it checks isinstance(entry[0], str)), but
            # only with the generic "has no target element" message below.
            # Checking it here first gives a more specific diagnostic
            # ("has a non-str docname") before falling through to that
            # shared predicate's own, less specific failure branch.
            if not isinstance(docname, str):
                message = (
                    f"typst_documents entry has a non-str docname: "
                    f"{docname!r} -- expected a str"
                )
                logger.warning(message)
                failures.append((repr(docname), message))
                continue
            # BLD-03: the one remaining way _is_usable_typst_documents_entry()
            # can return False here -- doc_tuple is truthy and its docname
            # is a str (both already checked above), so this can only be
            # the "fewer than two elements" case, i.e. no target element
            # at all. Checked via the SAME predicate the collision
            # validator, the D-07 report and the write-phase wrapper loop
            # all consult, so this branch and those three sites can never
            # again independently drift on what counts as usable.
            if not _is_usable_typst_documents_entry(doc_tuple):
                message = (
                    f"typst_documents entry {doc_tuple!r} has no target "
                    "element -- expected at least a (docname, target) pair"
                )
                logger.warning(message)
                failures.append((docname, message))
                continue
            # Resolve the WRAPPER's outdir-relative path ONCE, through the
            # same _wrapper_output_relpath() the write phase used, so the
            # read-back path and the write path can never drift (Issue
            # #117) and so only WRAPPER files are ever compiled here --
            # content files are never independently compiled (COMP-02).
            wrapper_relpath = self._wrapper_output_relpath(doc_tuple)
            typ_file = path.normpath(path.join(self.outdir, wrapper_relpath + ".typ"))

            if not path.exists(typ_file):
                if docname not in self.env.found_docs:
                    message = (
                        f"Master document {docname!r} is not a known Sphinx document"
                        " -- check typst_documents for a typo, a stray '.rst' "
                        "suffix, or an exclude_patterns exclusion"
                    )
                else:
                    message = f"Master document not found: {typ_file}"
                logger.warning(message)
                failures.append((docname, message))
                continue

            try:
                # typ_file is already the wrapper's real on-disk location,
                # so the docname-relative #include()/image() paths the
                # translator emitted resolve by construction (D-01).
                pdf_bytes = compile_typst_file_to_pdf(typ_file, root_dir=self.outdir)

                # Write PDF file
                pdf_file = path.normpath(
                    path.join(self.outdir, wrapper_relpath + ".pdf")
                )
                with open(pdf_file, "wb") as f:
                    f.write(pdf_bytes)

                logger.info(f"Generated PDF: {pdf_file}")

            except Exception as e:
                logger.error(f"Failed to compile {typ_file}: {e}")
                failures.append((docname, str(e)))

        if failures:
            summary = "; ".join(f"{docname}: {err}" for docname, err in failures)
            raise ExtensionError(
                f"typstpdf: {len(failures)} master document(s) failed: {summary}"
            )

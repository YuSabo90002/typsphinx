"""
Typst builder for Sphinx.

This module implements the TypstBuilder class, which is responsible for
building Typst output from Sphinx documentation.
"""

import posixpath
import shutil
from collections.abc import Iterator
from os import path
from typing import Dict, List, Set, Tuple

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
from typsphinx.writer import TypstWriter

logger = logging.getLogger(__name__)

# Phase 50 (D-02): the reserved top-level namespace an absolute image URI is
# relocated under when its rehome target either collides with a real source
# image (IMG-01) or would escape the doctree directory (IMG-02). A single
# reserved top-level path component -- the leading underscore already marks
# "owned by typsphinx, not the user's source tree" in this codebase
# (`_template.typ`) and in Sphinx itself (`_images`, `_static`, `_sources`).
RESERVED_IMAGE_NAMESPACE = "_typst_converted"


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
    """
    segments = stem.replace("\\", "/").split("/")
    # posixpath.isabs(), not path.isabs(): this function's own contract is
    # platform-independent (D-05) -- the OS-native `path` (== ntpath on a
    # Windows CI runner) disagrees with posixpath on which of these shapes
    # count as absolute (e.g. ntpath.isabs("/abs/manual") is False, since
    # ntpath requires a drive letter or a UNC-style leading "//"), which
    # would let a POSIX-shaped escape target through unrefused on Windows.
    # Measured on the windows-latest CI lane, 47-10/T2.
    return ".." in segments or posixpath.isabs(stem) or _is_drive_qualified(stem)


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

    def _validate_output_path_collisions(self) -> None:
        """Validate that no two logical output files -- a docname's
        content file, a ``typst_documents`` entry's wrapper file, or the
        reserved ``_template.typ`` infrastructure file -- resolve to the
        same physical output path (D-01/D-02/D-03/D-04/D-05).

        Runs ONCE, called from ``write()`` at the very top -- before
        ``prepare_writing()`` (which writes the shared ``_template.typ``
        immediately) and before the per-docname write loop -- so "no
        output file is written when any collision is found" (D-02) is
        structural rather than a promise, and covers ``_template.typ``
        itself, not only content/wrapper files. Defined on
        ``TypstBuilder`` so ``TypstPDFBuilder`` inherits it unchanged
        (D-03) -- both builders reject the same configurations identically.

        Builds ONE map from ``_collision_key()`` to a human-readable
        description of the logical file that claimed it, populated in
        this order: the reserved ``_template.typ`` infrastructure file;
        every docname in ``self.env.found_docs`` mapped to its content
        path; every ``typst_documents`` entry mapped to its resolved
        wrapper path. On a repeat key, BOTH claimants are recorded as one
        failure rather than raising immediately, so every offending entry
        is named in a SINGLE ``ExtensionError`` (D-02).

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

        Raises:
            ExtensionError: When one or more physical output paths are
                claimed by more than one logical file. The message begins
                with ``"typst: N output path collision(s)"`` (D-02's
                summary prefix) followed by every offending pair.
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

        # 1. The reserved _template.typ infrastructure file
        #    (_write_template_file() writes it once, at the outdir root)
        #    -- inserted first so any later claimant is reported against
        #    it by name (D-01's reserved-file kind).
        _claim("_template.typ", "the reserved _template.typ infrastructure file")

        # 2. Every docname's own content file -- unconditional, regardless
        #    of whether any typst_documents entry names it (COMP-01/OUT-03).
        found_docs = getattr(self.env, "found_docs", None) or set()
        for docname in found_docs:
            _claim(docname + ".typ", f"the content file for docname {docname!r}")

        # 3. Every typst_documents entry's wrapper file (BLD-02/BLD-03/
        #    BLD-04), resolved per-entry via _wrapper_output_relpath() --
        #    never via a docname-based first-match search, which is what
        #    makes D-04's repeated-docname/different-target case resolve
        #    to two independent keys instead of colliding with itself.
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
        and before ``prepare_writing()`` (which writes the shared
        ``_template.typ`` immediately) -- exactly
        ``_validate_output_path_collisions()``'s own precedent, extended to
        cover the one registry validation that previously had no up-front
        treatment: ``resolve_registry_key()`` was reachable only from
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

        This method is called before writing begins.
        Writes the template file to the output directory for master documents to import.

        Args:
            docnames: Set of document names to be written
        """
        # Create the writer instance
        self.writer = TypstWriter(self)

        # Write template file for master documents to import
        self._write_template_file()

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

        # D-02/D-03: validate BEFORE anything is written -- including
        # prepare_writing()'s own _write_template_file() call just below,
        # which writes "_template.typ" to outdir immediately. Placed here,
        # at the very top of write(), so a collision leaves ZERO ".typ"
        # files on disk, not just zero content/wrapper files (BLD-02's own
        # gate asserts no ".typ" file anywhere in the build directory,
        # which "_template.typ" would violate if this ran any later).
        # TypstPDFBuilder inherits this unchanged (D-03).
        self._validate_output_path_collisions()

        # Phase 53 (TPL-03, D-03/D-09): resolve the template registry
        # ONCE per build, here -- after collision validation, before
        # `prepare_writing()`'s own `_write_template_file()` call -- so
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

        Args:
            node: The image node whose ``uri`` should reflect the tracked
                path.
            resolved_uri: The concrete URI to track (already resolved from
                ``node["candidates"]`` by the caller).
        """
        if path.isabs(resolved_uri):
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
                key = f"{RESERVED_IMAGE_NAMESPACE}/{path.basename(resolved_uri)}"
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

    def _write_template_file(self) -> None:
        """
        Write the template file to the output directory.

        This writes a separate template.typ file that master documents can import.
        Only writes if a template is configured (not using Typst Universe packages).
        """
        from typsphinx.template_engine import (
            TemplateEngine,
            resolve_package_for_engine,
        )

        config = self.config

        # Get template configuration
        raw_template_path = getattr(config, "typst_template", None)
        template_path = raw_template_path
        if template_path:
            # Resolve relative path from source directory
            import os

            template_path = os.path.join(self.srcdir, template_path)

        typst_package = getattr(config, "typst_package", None)

        # D-03: when BOTH a Typst Universe package and a custom template are
        # configured, the combination is unsupported. `typst_template` wins
        # (D-01's routing decision promotes it to the primary route) and
        # `typst_package` is ignored end-to-end -- named here rather than
        # silently dropped (T-22.2-11). This method runs exactly once per
        # build (see the single call site in `prepare_writing()`), so the
        # warning fires once per build, not once per master document.
        if typst_package and raw_template_path:
            logger.warning(
                "Both 'typst_package' and 'typst_template' are configured; "
                "this combination is unsupported. 'typst_template' will be "
                "honoured and 'typst_package' will be ignored."
            )

        # Skip if using a Typst Universe package ALONE (no custom template
        # configured) -- a package-alone master needs no separate template
        # file (D-01). When a custom template is ALSO configured, fall
        # through: the custom template must still be written regardless of
        # the package setting (D-03).
        if typst_package and not raw_template_path:
            return

        # Create template engine. The package value goes through the same
        # single routing helper writer.py uses (WR-04) so the two can never
        # disagree about package-vs-template routing -- BUG-A's failure shape.
        # Reaching here means a custom template IS configured, so the helper
        # suppresses the package; deriving it rather than hardcoding None keeps
        # one rule, one place.
        template_engine = TemplateEngine(
            template_path=template_path,
            search_paths=[self.srcdir],
            parameter_mapping=getattr(config, "typst_template_mapping", None),
            typst_package=resolve_package_for_engine(typst_package, raw_template_path),
            typst_template_function=getattr(config, "typst_template_function", None),
            typst_package_imports=getattr(config, "typst_package_imports", None),
        )

        # Get template content
        template_content = template_engine.get_template_content()

        # Write template file
        template_file_path = path.join(self.outdir, "_template.typ")
        with open(template_file_path, "w", encoding="utf-8") as f:
            f.write(template_content)

        logger.info(f"Template written to {template_file_path}")

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

    def copy_template_assets(self) -> None:
        """
        Copy template-associated assets to the output directory.

        When using custom Typst templates via typst_template configuration,
        this method copies assets (fonts, images, logos, etc.) referenced by
        the template to the output directory.

        Behavior:
        - If typst_template_assets is configured, copies only specified files/directories
        - If typst_template_assets is None (default), automatically copies entire template directory
        - If typst_template_assets is empty list, disables automatic copying
        - Skips .typ files to avoid duplicating template file (already handled by _write_template_file)

        This follows the same pattern as copy_image_files() from Issue #38.
        """

        # Early return if no custom template is configured
        template_path = getattr(self.config, "typst_template", None)
        if not template_path:
            return  # No custom template

        # Early return if using Typst Universe package (assets handled by Typst compiler)
        typst_package = getattr(self.config, "typst_package", None)
        if typst_package:
            return

        # Get template assets configuration
        template_assets = getattr(self.config, "typst_template_assets", None)

        # Check if explicitly disabled (empty list)
        if template_assets is not None and len(template_assets) == 0:
            logger.debug("Template asset copying disabled (empty list)")
            return

        logger.info("Copying template assets...")

        if template_assets:
            # Option 2: Explicit asset list
            self._copy_explicit_assets(template_assets)
        else:
            # Option 1: Automatic directory copy
            self._copy_template_directory(template_path)

    def _copy_template_directory(self, template_path: str) -> None:
        """
        Copy entire template directory to output (default behavior).

        Automatically copies all files in the template directory,
        excluding .typ files (which are handled separately).

        Args:
            template_path: Path to template file relative to source directory
        """
        import os

        # Get template directory path
        template_dir = path.dirname(template_path)
        if not template_dir:
            # Template is in root directory, no assets to copy
            return

        # Resolve absolute paths
        src_dir = path.join(self.srcdir, template_dir)
        dest_dir = path.join(self.outdir, template_dir)

        # Check if template directory exists
        if not path.exists(src_dir):
            logger.warning(f"Template directory not found: {src_dir}")
            return

        # Track copied files for logging
        copied_count = 0

        # Walk through directory and copy all files except .typ
        for root, _dirs, files in os.walk(src_dir):
            for file in files:
                # Skip .typ files (already handled by _write_template_file)
                if file.endswith(".typ"):
                    continue

                # Get source and destination paths
                src_file = path.join(root, file)
                rel_path = path.relpath(src_file, src_dir)
                dest_file = path.join(dest_dir, rel_path)

                # Ensure destination directory exists
                ensuredir(path.dirname(dest_file))

                # Copy the file
                try:
                    shutil.copy2(src_file, dest_file)
                    logger.debug(f"Copied template asset: {rel_path}")
                    copied_count += 1
                except Exception as e:
                    logger.warning(f"Failed to copy template asset {rel_path}: {e}")

        if copied_count > 0:
            logger.info(f"Copied {copied_count} template asset(s) from {template_dir}/")

    def _copy_explicit_assets(self, assets: list) -> None:
        """
        Copy explicitly specified assets.

        Supports individual files, directories, and glob patterns.

        Args:
            assets: List of asset paths (relative to source directory)
                   May include glob patterns like "*.png" or "fonts/*.otf"
        """
        import glob

        copied_count = 0

        for asset_pattern in assets:
            # Resolve absolute pattern path
            abs_pattern = path.join(self.srcdir, asset_pattern)

            # Check if pattern contains wildcards
            if "*" in asset_pattern or "?" in asset_pattern:
                # Expand glob pattern
                matches = glob.glob(abs_pattern, recursive=True)
                if not matches:
                    logger.warning(f"No files matched pattern: {asset_pattern}")
                    continue

                for match in matches:
                    if self._copy_single_asset(match, asset_pattern):
                        copied_count += 1
            else:
                # Single file or directory
                if self._copy_single_asset(abs_pattern, asset_pattern):
                    copied_count += 1

        if copied_count > 0:
            logger.info(f"Copied {copied_count} explicitly specified template asset(s)")

    def _copy_single_asset(self, src_path: str, original_pattern: str) -> bool:
        """
        Copy a single asset file or directory.

        Args:
            src_path: Absolute source path
            original_pattern: Original pattern from configuration (for error messages)

        Returns:
            True if successfully copied, False otherwise
        """

        # Check if source exists
        if not path.exists(src_path):
            logger.warning(f"Template asset not found: {original_pattern}")
            return False

        # Calculate relative path from source directory
        rel_path = path.relpath(src_path, self.srcdir)
        dest_path = path.join(self.outdir, rel_path)

        try:
            if path.isdir(src_path):
                # Copy directory recursively
                # Use copytree with dirs_exist_ok for Python 3.8+
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                logger.debug(f"Copied template asset directory: {rel_path}/")
            else:
                # Copy single file
                ensuredir(path.dirname(dest_path))
                shutil.copy2(src_path, dest_path)
                logger.debug(f"Copied template asset: {rel_path}")
            return True
        except Exception as e:
            logger.warning(f"Failed to copy template asset {rel_path}: {e}")
            return False

    def finish(self) -> None:
        """
        Finish the build process.

        This method is called once after all documents have been written.
        Copies image files and template assets to the output directory.
        """
        self.copy_image_files()
        self.copy_template_assets()


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

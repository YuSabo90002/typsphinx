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
from typsphinx.writer import TypstWriter

logger = logging.getLogger(__name__)


def _is_drive_qualified(stem: str) -> bool:
    """Whether ``stem`` is a drive-qualified path (e.g. ``"C:manual"``) --
    a two-character-or-longer prefix whose first character is an ASCII
    letter and whose second character is a colon.

    A47-03/A3: this is the ONE place the drive-letter detection idiom is
    written; both ``_escapes_outdir()`` (the accept/reject decision) and
    ``_resolve_output_stem()`` (which needs to know whether to strip a
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

        # Track absolute docnames already emitted as an #include() across the
        # WHOLE master include graph, so a document reachable via more than one
        # toctree path (a "diamond") is physically #included at most ONCE per
        # build. Sphinx's own doc/index.rst, for example, lists
        # usage/extensions/index both directly (its "Reference" toctree) and
        # nested under usage/index (its "User guide" toctree). Since Typst's
        # #include() flattens each file's content inline, including the same
        # .typ twice re-emits EVERY Typst <label> that file defines, and Typst
        # rejects the compiled master with "label ... occurs multiple times".
        # Deduplicating at include() granularity (the unit that is duplicated
        # is a whole document, not a single translator-emitted anchor) keeps
        # each label defined exactly once so every reference still resolves.
        self._included_docnames: set[str] = set()

        # The SET of docnames whose .typ is physically part of the compiled
        # master (each master in typst_documents plus the transitive toctree
        # closure reachable from it). Any doc NOT in this set -- e.g. an
        # ``:orphan:`` doc, which Sphinx excludes from EVERY toctree -- is
        # written as a .typ but never #include()d into the master, so the
        # anchors it emits do not exist in the compiled document. The
        # translator consults this set (via builder.master_included_docnames)
        # to DEGRADE a cross-document reference whose target lies outside it
        # to plain text, rather than emitting a link(<targetdoc:anchor>) label
        # link that would dangle and hard-fail typst.compile() with
        # "label ... does not exist". Populated up-front in write() (from the
        # fully-read env's toctree graph) so it is reliably available before
        # any reference is emitted; empty until then (an empty set means "no
        # masters / unknown" and suppresses degradation, preserving behavior
        # for hand-built test doctrees and mock builders).
        self.master_included_docnames: set[str] = set()

    def _compute_master_included_docnames(self) -> set[str]:
        """Compute the transitive toctree closure of the master document(s).

        The compiled master ``.typ`` (one per ``typst_documents`` entry)
        physically ``#include()``s the transitive closure of toctree entries
        reachable from its source doc -- exactly the set of documents whose
        anchors end up in the compiled document. This walks Sphinx's canonical
        ``env.toctree_includes`` (``dict[str, list[str]]`` mapping each doc to
        the docs it directly pulls in via ``toctree``) breadth-first from every
        master source docname, and includes the masters themselves.

        ``env.toctree_includes`` is the read-phase-resolved include graph, so
        ``:orphan:`` documents (excluded from every toctree) never appear in
        it -- which is precisely why a cross-reference to one must degrade.
        Glob toctrees are already expanded to concrete docnames in this map, so
        the resulting set matches what ``visit_toctree`` actually emits.

        Returns:
            The set of docnames included in some compiled master, or an empty
            set when no masters are configured (which the translator treats as
            "unknown" and does not degrade against).
        """
        typst_documents = getattr(self.config, "typst_documents", []) or []
        masters = [entry[0] for entry in typst_documents if entry]
        toctree_includes = getattr(self.env, "toctree_includes", {}) or {}

        included: set[str] = set()
        stack = list(masters)
        while stack:
            docname = stack.pop()
            if docname in included:
                continue
            included.add(docname)
            for child in toctree_includes.get(docname, []):
                if child not in included:
                    stack.append(child)
        return included

    def _resolve_output_stem(self, docname: str) -> str:
        """Resolve the output filename stem for a document.

        ``typst_documents``' target name (tuple element ``[1]``, published as
        the "Target name" contract at ``docs/configuration.rst:43``) governs
        the filename a master document is written and compiled under --
        ``typst_documents = [('index', 'manual.typ', ...)]`` must emit
        ``manual.typ`` / ``manual.pdf``, not ``index.typ`` / ``index.pdf``
        (Issue #117). This is the docname-based entry lookup; the actual
        normalization rule lives in ``_resolve_target_stem()``, which this
        delegates to once a matching entry is found -- every write/read-back
        site reaches that same normalization through one of these two
        methods, never re-deriving the rule.

        Args:
            docname: The Sphinx document name being written.

        Returns:
            The filename stem (no suffix) to use for this document's output.
            When ``docname`` has no matching ``typst_documents`` entry, the
            docname itself is returned unchanged (D-02) -- this is the
            common case for every document that is not a compiled master.
            Performs NO collision detection -- that moved wholesale to
            ``_validate_output_path_collisions()`` (D-03), run once before
            any write; this method (and ``_resolve_target_stem()``) never
            reads ``self.env.found_docs`` or the reserved ``_template``
            name, so a caller can never observe a silently-degraded stem
            here. The former CR-01 in-function fallback (warn, then return
            ``docname``) is gone -- a colliding stem is now returned
            AS-IS and caught by the validator before it is ever written.
        """
        typst_documents = getattr(self.config, "typst_documents", []) or []

        for entry in typst_documents:
            if entry and len(entry) >= 2 and entry[0] == docname:
                return self._resolve_target_stem(docname, entry[1])

        # D-02: toctree-included children (and any docname with no
        # typst_documents entry) keep docname + suffix. Silent -- this
        # is the overwhelmingly common case (every non-master document).
        return docname

    def _resolve_target_stem(self, docname: str, target: object) -> str:
        """Normalize one ``typst_documents`` entry's target into an output
        stem, given the target value directly rather than searching
        ``typst_documents`` for it.

        This is the normalization core ``_resolve_output_stem()`` delegates
        to after its own docname-based first-match lookup, and that
        ``_wrapper_output_relpath()`` calls DIRECTLY on a specific entry's
        own target -- bypassing the first-match lookup entirely. That is
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

        A malformed entry (empty tuple, fewer than two elements, or a
        non-``str`` docname) is skipped without raising and without being
        added to the map -- reporting a malformed entry stays
        ``TypstPDFBuilder.finish()``'s job alone, matching the tolerance
        the existing guard loops already have.

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
            if not entry or len(entry) < 2 or not isinstance(entry[0], str):
                # Malformed -- skip without raising or reporting. That
                # tolerance matches the existing guard loops; reporting a
                # malformed entry stays TypstPDFBuilder.finish()'s job.
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
        typst_documents target-name rename that ``_resolve_output_stem``
        applies to the on-disk filename (Phase 22 / Issue #117). Its only
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
        # at the very top of write(), rather than after
        # master_included_docnames is computed, so a collision leaves
        # ZERO ".typ" files on disk, not just zero content/wrapper files
        # (BLD-02's own gate asserts no ".typ" file anywhere in the build
        # directory, which "_template.typ" would violate if this ran any
        # later). TypstPDFBuilder inherits this unchanged (D-03).
        self._validate_output_path_collisions()

        logger.info("preparing documents... ", nonl=True)
        self.prepare_writing(docnames)
        logger.info("done")

        # Start each build with a clean include-dedup ledger so re-builds and
        # multiple write() invocations do not carry stale state across masters.
        self._included_docnames = set()

        # Compute the master include-set NOW (the read phase is complete, so
        # env.toctree_includes is fully populated) rather than lazily during
        # visit_toctree: a cross-document reference in one document may be
        # emitted BEFORE the toctree that includes its target is processed, so
        # the set must be fully known up-front for the degrade decision to be
        # reliable regardless of document write order.
        self.master_included_docnames = self._compute_master_included_docnames()

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
        # builder.
        typst_documents = getattr(self.config, "typst_documents", []) or []
        wrapper_relpaths = sorted(
            self._wrapper_output_relpath(entry) + ".typ"
            for entry in typst_documents
            if entry and entry[0] in docnames
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

        Args:
            node: The image node whose ``uri`` should reflect the tracked
                path.
            resolved_uri: The concrete URI to track (already resolved from
                ``node["candidates"]`` by the caller).
        """
        if path.isabs(resolved_uri):
            rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(path.sep, "/")
            node["uri"] = rel_uri
            if rel_uri not in self.images:
                self.images[rel_uri] = resolved_uri
            return

        # Store empty string as value to be compatible with parent class type
        if resolved_uri not in self.images:
            self.images[resolved_uri] = ""

    def _content_output_path(self, docname: str) -> str:
        """Return this docname's content file's absolute on-disk path
        (COMP-01/OUT-03).

        Unconditional, and a pure function of the docname alone -- a
        docname already carries its own ``/``-separated directory, so
        this needs no ``_resolve_output_stem()`` call. Every docname gets
        a content file, regardless of whether any ``typst_documents``
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
        ``_resolve_target_stem(entry[0], entry[1])`` -- never through
        ``_resolve_output_stem()``'s docname-based first-match search.
        This is what makes D-04's repeated-docname case correct: two
        entries naming the same docname with different targets each get
        THEIR OWN wrapper path, rather than both resolving via whichever
        entry a docname search happens to find first (the gap
        ``47-02-SUMMARY.md`` and ``47-06-SUMMARY.md`` both named as
        deferred to this plan).

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
        typst_documents = getattr(self.config, "typst_documents", []) or []
        for entry in typst_documents:
            if not entry or entry[0] != docname:
                continue
            wrapper_relpath = self._wrapper_output_relpath(entry)
            wrapper_destination = path.normpath(
                path.join(self.outdir, wrapper_relpath + ".typ")
            )
            ensuredir(path.dirname(wrapper_destination))
            wrapper_relative_dir = posixpath.dirname(wrapper_relpath)
            wrapper_output = self.writer.render_wrapper(
                entry, doctree, wrapper_relative_dir, content_relative_path
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
            # Mirror _resolve_output_stem's own length guard here: a
            # malformed entry (e.g. an empty tuple from a misconfigured
            # typst_documents) must not raise an uncaught IndexError on
            # doc_tuple[0] before that helper's defenses ever run.
            if not doc_tuple:
                logger.warning(f"Malformed typst_documents entry: {doc_tuple!r}")
                failures.append((repr(doc_tuple), "malformed typst_documents entry"))
                continue
            docname = doc_tuple[0]
            # BLD-01: _resolve_output_stem tolerates a docname of any type
            # (it only does `==` comparisons), but _directory_preserving_
            # relpath does not -- it calls posixpath.dirname(docname), which
            # raises a raw TypeError for anything that is not a str. Catch
            # it here, before either helper runs, so the failure joins the
            # existing failures list instead of killing the whole build.
            if not isinstance(docname, str):
                message = (
                    f"typst_documents entry has a non-str docname: "
                    f"{docname!r} -- expected a str"
                )
                logger.warning(message)
                failures.append((repr(docname), message))
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

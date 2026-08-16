"""
Typst translator for docutils nodes.

This module implements the TypstTranslator class, which translates docutils
nodes to Typst markup.
"""

import re
from typing import Any, Dict, List, NamedTuple, Tuple

from docutils import nodes
from sphinx import addnodes
from sphinx.errors import ExtensionError
from sphinx.locale import admonitionlabels
from sphinx.util import logging
from sphinx.util.docutils import SphinxTranslator

logger = logging.getLogger(__name__)

# Units docutils may normalize into `:width:`/`:height:` (via
# length_or_percentage_or_unitless / length_or_unitless) that are already
# valid Typst length units and should pass through unchanged.
_TYPST_PASSTHROUGH_UNITS = {"%", "em", "pt", "cm", "mm", "in"}

# Shared cross-phase indent quantum (D-08, 37-EMISSION-CONTRACT.md section 1).
# Phase 37 introduces this as the desc_signature hanging-indent step (SIG-07);
# Phase 38's IND-04 reuses this SAME constant for desc_content, field_list and
# block_quote rather than defining a second indent number -- do not introduce
# another one. Value is the owner's D-06 choice (compiled and compared against
# three renderings; see 37-CONTEXT.md).
SHARED_INDENT_STEP = "2.5em"

# Phase 48 plan 07 (G-48-4 / XREF-03 gap closure): the whole-document
# self-anchor's raw id, fixed at `__tsx-doc__`
# (48-EXPECTED-STRUCTURE.md "Phase 48 Plan 05" section 1). Deliberately
# carries BOTH an underscore and a hyphen -- unreachable from either raw-id
# source this codebase namespaces through `_namespace_label`: docutils'
# `make_id` never emits an underscore, even when its input already
# contains one (nine adversarial probes, section 1 Claim 1), and a Sphinx
# domain object id is built from Python identifiers, which structurally
# exclude a hyphen (section 1 Claim 2). ONE module-level constant, consumed
# by BOTH the definition site (`visit_document`, below) and the reference
# site (`visit_reference`'s cross-document branch) through the SAME
# `_namespace_label` call (D-13) -- never re-spelled at either.
_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN = "__tsx-doc__"

# Phase 55 plan 01 (XREF-05, D-01/D-02): `_sanitize_label`'s own encoding
# token alphabet (`_u{codepoint:x}_`) is a SUBSET of its "safe" character
# class, so a raw input that already spells the encoder's own token shape
# passes through the main substitution untouched -- collapsing two distinct
# inputs (e.g. docnames `a/b` and `a_u2f_b`) onto one label. This pattern
# matches the introducing underscore of any such literal run -- `u` followed
# by one or more lowercase hex digits, followed by either an underscore or a
# character the main substitution is about to escape -- so `_sanitize_label`
# can neutralise it BEFORE the main substitution runs. Matched via lookahead
# (the underscore itself is what gets replaced, not the whole run) so the
# pre-pass and the main substitution never have to agree on where the run
# ends. See `55-01-RED-EVIDENCE.md` and `tests/test_sanitize_label_injectivity_unit.py`.
_LABEL_TOKEN_INTRODUCER_RE = re.compile(r"_(?=u[0-9a-f]+(?:_|[^A-Za-z0-9_.:-]))")


class _ReferenceAnchorDecision(NamedTuple):
    """
    The single D-14 citing-site anchor judgement (WR-03, `40.1-CONTEXT.md`
    D-05/D-06/D-07): "does this ``nodes.reference`` get its own
    bracket-attached anchor, and if so what is that anchor's label?"

    Before Phase 40.1, this question was answered independently in TWO
    places -- ``visit_reference``'s own local computation (three
    conditions: ``node.get("ids")``, ``opens_wrapper``, ``not
    next_is_target``) and ``_citing_reference_has_own_anchor`` (one
    condition: ``not next_is_target`` alone, assuming the other two) --
    and nothing held them together. ``TypstTranslator._reference_anchor_
    decision`` (below) is now the ONE place that derives every field here,
    consumed by BOTH ``visit_reference`` (the anchor-EMITTING site) and
    ``visit_citation``'s backref loop (the anchor-CONSUMING site), so the
    two cannot silently drift apart again (D-05).

    Every field is derived from the node alone (D-09): the label-existence
    question this decision used to answer via a build-time degrade field
    (deleted in Phase 48) is now decided entirely at Typst compile time by
    ``_label_existence_guard()``'s ``query(<label>)`` -- this predicate no
    longer consults any builder state to decide whether a wrapper opens.

    Attributes:
        refuri: ``node.get("refuri", "")``.
        refid: ``node.get("refid", "")``.
        xref: ``self._resolve_xref_docname(refuri)`` result, or ``None``
            when ``refuri`` is empty or does not resolve to a local
            cross-document anchor.
        opens_wrapper: ``bool(refuri or refid)`` -- whether ANY link
            wrapper is opened at all (citation-derived or otherwise),
            unconditionally (D-09): whether the reference's TARGET is
            reachable in any particular compile is a question the D-07
            compile-time guard now answers, never a reason to withhold
            the citing site's OWN same-document anchor.
        next_is_target: whether the node's immediately-following sibling
            is a ``nodes.target`` -- has TWO consumers in
            ``visit_reference`` (Pitfall 3, `40.1-RESEARCH.md`): the D-14
            eligibility gate below, and the pre-existing
            target-attachment markup wrap that fires whenever the next
            sibling is a target regardless of ``ids``/``opens_wrapper``.
            Both must read this SAME value, computed once.
        eligible: ``bool(node.get("ids")) and opens_wrapper and not
            next_is_target`` -- D-05's judgement, unchanged in substance
            from the pre-Phase-40.1 code, just relocated to the single
            place it is now written.
        anchor_label: the anchor label (D-07, via D-13's single
            ``_namespace_label`` derivation point) when ``eligible``,
            else ``None``. Returning the LABEL (not just the boolean)
            means the link target ``visit_citation`` appends and the
            anchor ``visit_reference`` attaches come from the SAME
            expression -- closing the second, independent
            ``_namespace_label`` call this phase measured (D-07).

    This predicate is SILENT (Pitfall 2, `40.1-RESEARCH.md`): no
    ``logger`` call, no ``add_text``, no translator-state mutation. Phase
    48 deleted the build-time cross-document degrade-to-text warning this
    docstring used to reference -- no diagnostic replaces it (D-01); the
    only remaining build-time signal that a reference is broken is
    Sphinx's own resolver warnings.
    """

    refuri: str
    refid: str
    xref: Tuple[str, str] | None
    opens_wrapper: bool
    next_is_target: bool
    eligible: bool
    anchor_label: str | None


class _LabelGuardStrings(NamedTuple):
    """
    The D-07 shared guard-string pair returned by
    ``TypstTranslator._label_existence_guard()``: the exact bytes to emit
    immediately BEFORE a reference's body (``open_str``) and immediately
    AFTER it (``close_str``), wrapping the body in a Typst ``context { ...
    }`` block that decides at COMPILE TIME, per compiled wrapper, whether
    ``label`` actually exists in this particular ``#include()`` graph.

    Attributes:
        open_str: the prefix (if any), the ``context`` keyword, an
            opening brace, the ``let __tsx_body = `` binding, and the
            body opener (``[#{`` in code-mode-body form, bare ``[`` in
            markup-mode-body form).
        close_str: the body closer, a semicolon, then the conditional --
            ``if query(<label>).len() > 0 { link(<label>, __tsx_body) }
            else { __tsx_body }``, closed by the block's own final brace.
    """

    open_str: str
    close_str: str


def escape_typst_string(text: str) -> str:
    """Escape arbitrary text for embedding inside a Typst ``"..."`` string literal.

    Typst string literals cannot span physical lines and treat ``\\`` and ``"``
    specially, so every character that would break the literal (or be
    misinterpreted) must be escaped. This is the single source of truth for
    string-literal escaping across the translator: any site that emits
    ``raw("...")``, ``text("...")``, etc. from node-derived text routes through
    this helper so the class of problem is handled consistently.

    Escaping order is significant: backslash MUST be escaped first, otherwise
    the backslashes introduced by the later replacements would themselves be
    doubled.

    The newline/CR/tab escapes turn a literal control character into its
    two-character escape sequence (e.g. a raw ``\\n`` becomes the sequence
    ``\\`` + ``n``). Typst decodes that back into the original control character
    when rendering, so the visible content is preserved while the emitted
    ``.typ`` stays valid single-line syntax.

    Args:
        text: Raw text to escape (e.g. ``node.astext()``).

    Returns:
        Text safe to embed between double quotes in a Typst string literal.
    """
    text = text.replace("\\", "\\\\")  # Backslash (FIRST, avoids double-escaping)
    text = text.replace('"', '\\"')  # Quote
    text = text.replace("\n", "\\n")  # Newline
    text = text.replace("\r", "\\r")  # Carriage return
    text = text.replace("\t", "\\t")  # Tab
    return text


# Phase 49 (COMP-05/COMP-06/D-04..D-09): the per-master include graph moves
# the include DECISION from write time (a build-scoped ledger claiming a
# docname the first time any document's toctree names it, which can only
# ever pick ONE winner across the WHOLE build) to Typst COMPILE time (a
# per-master published `state` array, read by a per-emission-site guard).
# These five module-level symbols are the complete derivation surface;
# placed here, immediately after `escape_typst_string`, because every one
# of them depends on it and no import is needed for a same-module call.

# D-07: the namespaced Typst `state` key every wrapper publishes to and
# every guard reads from. A user-supplied `typst_template` is arbitrary
# Typst and may legitimately call `state("inc")` (or any other short,
# unnamespaced key) for its own purposes -- a project-prefixed key with a
# separator no bare identifier would use makes a silent collision with
# user template code implausible. Measured against a real `typst.compile()`
# in `49-EVIDENCE.md`'s State-syntax measurement; this literal spelling is
# fixed by that measurement, not a placeholder.
INCLUDE_STATE_KEY = "typsphinx:include-edges"


def _escape_include_edge_separators(text: str) -> str:
    """Escape literal occurrences of this module's edge-key FORMAT
    separators (``#`` and ``>``) inside a single already
    ``escape_typst_string()``-escaped docname component (Phase 55 plan 02,
    BLD-07).

    Two ordinary ``str.replace`` calls, nothing else: each literal ``#``
    becomes ``\\#``, then each literal ``>`` becomes ``\\>``. This is a
    SECOND, NARROWER rule than ``escape_typst_string()`` and is
    deliberately NOT folded into it -- ``escape_typst_string()`` is called
    from many sites across the translator that emit ordinary Typst string
    literals where ``#`` is meaningful markup syntax and must NOT be
    escaped; widening its four-character contract to also cover the two
    edge-key separators would churn unrelated emitted bytes across the
    whole module. This helper is applied ONLY inside
    ``make_include_edge_key()``, to each of the two docname components,
    never to the ``#``/``>`` the f-string itself inserts as the key
    format's own structural separators.

    Call-order is LOAD-BEARING and is why this helper runs AFTER
    ``escape_typst_string()``, never before: ``escape_typst_string()`` has
    already doubled every literal backslash in its input (its own
    docstring's "escaped first" rule), so by the time this helper runs, a
    literal backslash in the ORIGINAL docname is represented by an EVEN
    run of backslashes (``\\`` -> ``\\\\``, ``\\\\`` -> ``\\\\\\\\``, ...).
    This helper then introduces exactly ONE further backslash immediately
    before each literal ``#``/``>`` byte, so every literal separator
    character that was actually PRESENT in a docname component is now
    preceded by an ODD run of backslashes, while the key format's own two
    structural separators (inserted by the f-string in
    ``make_include_edge_key()`` after both components have already been
    escaped) are preceded by an EVEN run (usually zero, since no
    backslash immediately precedes them). That parity is what makes the
    three-part ``<parent>#<occurrence>><child>`` boundary uniquely
    locatable, and is therefore what makes the parent/child/occurrence
    triple-to-key map injective. Reversing the order (escaping the two
    separators BEFORE ``escape_typst_string()`` runs) does NOT hold this
    property: the later backslash-doubling pass would turn an
    originally-odd run even, destroying the parity invariant. This
    ordering and the resulting injectivity were brute-forced over 640,000
    ``(parent, child, occurrence)`` triples this phase (drawn from the
    alphabet ``a # > \\ 0 1 "`` with component lengths 0-3 and occurrences
    0, 1, 2 and 10): zero collisions with this construction, versus a
    first collision at ``('', '#0>', 0)`` against ``('#0>', '', 0)`` (both
    ``#0>#0>``) without it.

    The measured Typst-level fact this fix rests on: Typst keeps the
    escaping backslash as an ordinary character in the string VALUE (a
    two-character sequence, ``\\`` followed by the separator, not folded
    away) -- so two differently-escaped key spellings stay distinct
    inside the published ``state`` array at compile time. This property
    is pinned directly against a real ``typst.compile()`` by
    ``tests/test_include_edge_separator_collision_gate.py``'s language
    probe (``test_typst_language_keeps_escape_character_distinct``).

    Args:
        text: A single docname component, already passed through
            ``escape_typst_string()``.

    Returns:
        ``text`` with every literal ``#`` and ``>`` byte preceded by one
        additional backslash.
    """
    text = text.replace("#", "\\#")
    text = text.replace(">", "\\>")
    return text


def make_include_edge_key(
    parent_docname: str, child_docname: str, occurrence: int = 0
) -> str:
    """Derive the ONE edge-key spelling for a toctree parent/child pair
    (D-04/D-05).

    This is the SINGLE derivation point for this phase's edge-key format,
    called by BOTH the builder's graph computation
    (``TypstBuilder._build_include_edge_map()``, via
    ``derive_master_edge_keys()``) and the translator's own guard emission
    (``visit_toctree``). A second, independently-spelled edge-key
    expression anywhere in the codebase is exactly the drift class this
    single-function rule exists to reject -- and a mismatch between the
    two call sites would NOT fail the build: the guard would simply never
    fire, silently dropping the child's content with no diagnostic at any
    layer (T-49-02).

    Args:
        parent_docname: The docname whose toctree names ``child_docname``.
        child_docname: The docname being claimed.
        occurrence: The 0-based index of THIS emission site among the
            emission sites in ``parent_docname`` naming ``child_docname``
            (D-04's occurrence rule). Defaults to 0, the only value the
            graph side (``derive_master_edge_keys()``) can ever emit -- a
            child is claimed at its FIRST non-traversed appearance in its
            parent's ordered list, which is always occurrence 0.

    Returns:
        The edge key, e.g. ``"index#0>child"``. Both docnames route
        through ``escape_typst_string()`` (T-49-01) AND the
        separator-escaping helper above it (Phase 55 plan 02, BLD-07),
        so a docname containing a double quote, a backslash, a ``#`` or a
        ``>`` still produces a key that is byte-identical whether derived
        on the graph side or the emission side, and two structurally
        different edges can no longer collide onto one key. A docname
        containing NEITHER separator character produces a byte-identical
        key to before this fix, e.g.
        ``make_include_edge_key('index', 'child', 0) == 'index#0>child'``.
    """
    escaped_parent = _escape_include_edge_separators(
        escape_typst_string(parent_docname)
    )
    escaped_child = _escape_include_edge_separators(escape_typst_string(child_docname))
    return f"{escaped_parent}#{occurrence}>{escaped_child}"


# Phase 55 plan 02 (BLD-08): the fixed, documented policy bound on
# `derive_master_edge_keys()`'s own recursion depth. Re-measured directly
# in this worktree (`55-02-RED-EVIDENCE.md` "Depth headroom measurement"),
# not guessed: the interpreter's own default maximum call-stack depth is
# 1000 frames; the deepest linear include chain this function survives
# from a near-empty stack is 996; a 900-deep chain already raises
# `RecursionError` once roughly 100 extra Python caller frames sit above
# the walk -- which is why `55-RESEARCH.md`'s originally proposed value of
# 900 was REJECTED as unsafe. A real `sphinx-build` was measured at 11
# caller frames above this function, and a `pytest` plus `SphinxTestApp`
# stack is deeper still. 500 leaves roughly 495 frames of headroom below
# the measured 996-deep near-empty-stack ceiling for any embedder's own
# stack, while remaining two orders of magnitude beyond any real
# documentation tree. This is a FIXED POLICY CHOICE, deliberately NOT read
# from the interpreter's own call-stack limit at runtime, so behaviour
# does not vary by interpreter or embedder.
_MAX_INCLUDE_CHAIN_DEPTH = 500


def derive_master_edge_keys(
    toctree_includes: Dict[str, List[str]], master_docname: str
) -> Tuple[str, ...]:
    """Walk one master's own include graph and return its published edge
    keys, in document-order discovery order (COMP-05).

    A fresh RECURSIVE walk with an ordered ``traversed`` list threaded
    through the recursion -- seeded with ``[master_docname]`` before the
    walk begins, and appended to BEFORE recursing into each newly-claimed
    child -- mirroring Sphinx's own ``inline_all_toctrees()``
    (``sphinx/util/nodes.py:499-517``) and its two callers, both of which
    seed ``traversed`` with the compiling document's own docname. The
    composition rule this produces is document-order FIRST-ENCOUNTER-WINS:
    whichever parent's own ordered list reaches a shared child FIRST (in
    THIS master's own traversal) claims it; a later parent's own entry for
    the same child is dark (no edge emitted). This is NOT
    prefer-the-deeper-path, and it does NOT consult or port Sphinx's own
    ``document is referenced in multiple toctrees: [...], selecting: X <-
    Y`` message -- that message comes from a DIFFERENT function
    (``_check_toc_parents()``, ``sphinx/environment/__init__.py:942-959``),
    takes a plain lexicographic ``max(parents)`` tiebreak, and governs NONE
    of this DFS.

    The FORBIDDEN shape, by name and by defect: an explicit work-stack
    seeded with the master, fed by iterating each parent's children with
    forward ``append`` calls, and drained LAST-IN-FIRST-OUT (removing and
    processing the most-recently-appended element each iteration, the
    way a call stack unwinds) processes the LAST-listed child of any
    given parent FIRST, silently REVERSING sibling order with NO compile
    error -- this is a DIFFERENT, already Phase-48-deleted helper's own
    traversal shape (that helper solved a DIFFERENT problem, a flat
    cross-master docname union for XREF-safety), and COMP-05/SC#3 forbids
    reusing it here. This function's genuine recursion preserves document
    order; a naive forward-push LIFO stack does not. The recursion is
    deliberately PRESERVED by the depth bound below (Phase 55 plan 02,
    BLD-08), rather than replaced by that forbidden work-stack shape: a
    chain deeper than ``_MAX_INCLUDE_CHAIN_DEPTH`` now raises a named
    ``sphinx.errors.ExtensionError`` instead of an uncaught
    ``RecursionError`` escaping through Sphinx's own traceback. This bound
    can ONLY ever be reached by a genuinely deep ACYCLIC chain -- a CYCLE
    is already structurally dark through the ``traversed`` membership
    check at any depth (see above), so the raised message never claims a
    repeated document was found.

    Occurrence is always 0 on this side: a child is claimed by its parent
    at that child's FIRST non-traversed appearance in the parent's ordered
    list, which -- because ``traversed`` membership can only GROW, never
    shrink, during one master's walk -- is ALWAYS the occurrence-0
    appearance. A duplicate toctree entry for the same child (occurrence
    >= 1) is therefore structurally dark: no second, independent emission
    site exists on this side to ever claim it.

    Args:
        toctree_includes: A mapping from docname to its ordered
            include-file list (``env.toctree_includes``, or an equivalent
            mapping in a unit test). A docname absent from this mapping is
            treated as having no children, matching how the mirrored
            Sphinx walk behaves for a document with no toctree.
        master_docname: The master document's own docname -- the DFS seed.

    Returns:
        The master's edge keys, in discovery order, as an ordered tuple.

    Raises:
        ExtensionError: If the include chain reaches a depth greater than
            ``_MAX_INCLUDE_CHAIN_DEPTH`` edges below ``master_docname``.
    """
    traversed: List[str] = [master_docname]
    edge_keys: List[str] = []

    def walk(parent: str, depth: int, path: Tuple[str, ...]) -> None:
        if depth > _MAX_INCLUDE_CHAIN_DEPTH:
            raise ExtensionError(
                f"typsphinx: the include chain for master document "
                f"{master_docname!r} is a very deep toctree nesting -- "
                f"reached depth {depth}, exceeding the "
                f"{_MAX_INCLUDE_CHAIN_DEPTH}-edge bound, running from "
                f"{path[0]!r} to {path[-1]!r}."
            )
        for child in toctree_includes.get(parent, []):
            if child not in traversed:
                edge_keys.append(make_include_edge_key(parent, child, occurrence=0))
                traversed.append(child)
                walk(child, depth + 1, path + (child,))
            # else: already traversed -- dark, no edge emitted (first-encounter-wins)

    walk(master_docname, 0, (master_docname,))
    return tuple(edge_keys)


def render_include_edge_state(edge_keys: Tuple[str, ...]) -> str:
    """Render a wrapper's ``state`` publication line for ``edge_keys``.

    The array-literal rendering rule (measured against a real
    ``typst.compile()`` in ``49-EVIDENCE.md`` Probes 1-4): ``()`` for zero
    keys, and for one or more keys a parenthesized comma-separated list of
    double-quoted keys with an UNCONDITIONAL trailing comma after the LAST
    element. This uniform rule removes the ``len(keys) == 1`` special case
    RESEARCH Pitfall 1 warns is otherwise required: omitting the trailing
    comma on a SINGLE-element literal is not a syntax error at all -- Typst
    silently reparses ``("key")`` as a parenthesized STRING expression
    instead of a one-element array (``49-EVIDENCE.md`` Probe 5), and the
    published state's Typst type degrades from ``array`` to ``str`` with
    ZERO compile-time diagnostic at any layer. Every guard's ``in``
    membership test then silently degrades to substring containment
    against that one string. The uniform trailing-comma rule this function
    implements has no single-element special case, so this hazard cannot
    arise by construction.

    Args:
        edge_keys: The master's own edge keys, in discovery order (the
            return value of ``derive_master_edge_keys()``).

    Returns:
        The complete publication line, e.g.
        ``'#state("typsphinx:include-edges", ()).update(("index#0>child",))'``.
    """
    if not edge_keys:
        array_literal = "()"
    else:
        quoted_keys = ", ".join(f'"{key}"' for key in edge_keys)
        array_literal = f"({quoted_keys},)"
    return f'#state("{INCLUDE_STATE_KEY}", ()).update({array_literal})'


def render_include_guard(edge_key: str, include_relpath: str) -> str:
    """Render one content file's per-emission-site compile-time guard line.

    The condition and its opening ``{`` MUST stay on ONE unbroken physical
    line -- ``49-EVIDENCE.md`` Probe 7 measured a newline inserted between
    them against a real ``typst.compile()`` and got the verbatim parser
    error ``expected block``; Probe 7's passing variant keeps them on one
    line, which is what this function's returned template does
    unconditionally.

    This site is always reached from CODE mode: content-file bodies are
    unconditionally wrapped in a top-level ``#{ ... }`` code block
    (``writer.py``'s ``translate()``), so no markup-mode ``#`` prefix
    computation is needed here, unlike the reference and citation sites
    Phase 48 touched. A future change that violates that invariant (moving
    this guard's emission site into markup-mode body text) should fail
    loudly rather than silently emit a bare ``if``/``state`` scope keyword
    with no leading ``#``.

    Args:
        edge_key: The edge key this guard tests membership of (already
            escaped -- ``make_include_edge_key()`` routes both docnames
            through ``escape_typst_string()`` before this function ever
            sees the key).
        include_relpath: The relative path to the child's own content
            file, WITHOUT the ``.typ`` suffix (``_compute_relative_include_
            path()``'s own return shape). Routed through
            ``escape_typst_string()`` here (T-49-01's guard-side half of
            the escaping rule) so a docname-derived path containing a
            quote or backslash still produces a valid literal.

    Returns:
        The complete guard line, e.g.
        ``'if "index#0>child" in state("typsphinx:include-edges", ()).get() { include("child.typ") }'``.
    """
    escaped_relpath = escape_typst_string(include_relpath)
    return (
        f'if "{edge_key}" in state("{INCLUDE_STATE_KEY}", ()).get() '
        f'{{ include("{escaped_relpath}.typ") }}'
    )


class TypstTranslator(SphinxTranslator):
    """
    Translator class that converts docutils nodes to Typst markup.

    This translator visits nodes in the document tree and generates
    corresponding Typst markup.
    """

    def __init__(self, document: nodes.document, builder: Any) -> None:
        """
        Initialize the translator.

        Args:
            document: The docutils document to translate
            builder: The Sphinx builder instance
        """
        super().__init__(document, builder)
        self.builder = builder
        self.body = []

        # State management variables
        self.section_level = 0
        self.in_figure = False
        self.in_table = False
        self.table_colwidths: List[Any] = (
            []
        )  # Per-column colwidth accumulator (FID-01a D-01); init in
        # visit_table, consumed + reset in depart_table.
        self.in_thead = False  # Track if currently in table header
        self.in_caption = False
        self.list_stack = []  # Track list nesting: 'bullet' or 'enumerated'

        # Table caption state (TBL-01/TBL-02, Phase 25): a `.. table::` (and
        # equally csv-table/list-table) caption is stored by docutils as a
        # `title` CHILD of nodes.table -- visited WHILE self.in_table is
        # still True. add_text() already routes to self.table_cell_content
        # whenever in_table is True (see add_text), so the caption buffer
        # REUSES that existing dispatch rather than a self.body swap (a
        # self.body swap alone would not change add_text()'s routing
        # decision, silently misrouting the caption -- see visit_title).
        self.table_caption: str | None = (
            None  # Rendered caption text, consumed + reset in depart_table
        )
        self._in_table_caption: bool = (
            False  # Track if currently buffering a table caption title
        )
        self._caption_saved_list_state: Tuple[bool, bool] | None = (
            None  # (in_list_item, list_item_needs_separator) saved across
            # the caption title's buffering, mirrors the admonition-title
            # save/restore idiom
        )

        # TBL-05 (Phase 43): the STRUCTURAL captioned decision computed in
        # visit_table (`is_captioned`) -- whether this table's first child
        # is a nodes.title at all, independent of whether that title's
        # RENDERED content happens to be empty. Stashed here so depart_table
        # can gate its id-anchoring call on this value instead of on
        # self.table_caption's truthiness (D-05/D-07): a title whose only
        # child is a raw node with a non-typst format renders to the empty
        # string (visit_raw raises SkipNode), so the two checks can
        # genuinely disagree, and when they do the table's ids must still
        # anchor on at least one path or a same-document reference dangles.
        # Joins _push_table_state/_pop_table_state's snapshot set below, so
        # a nested captioned table's own decision does not clobber the
        # enclosing table's.
        self._table_is_captioned: bool = False

        # TBL-04 (Phase 43): a table nested inside another table's cell
        # would otherwise clobber the enclosing table's in-progress scalar
        # state, since every table_* scalar above is a flat instance
        # attribute with no notion of "which table is currently being
        # filled". _push_table_state()/_pop_table_state() save/restore a
        # full snapshot of that scalar set around a NESTED visit_table/
        # depart_table pair only (never for a top-level table, which stays
        # byte-identical) -- see the docstrings on those two methods.
        self._table_state_stack: List[Dict[str, Any]] = []

        # Figure-specific state
        self.figure_content = []
        self.figure_caption = ""
        self._saved_body_for_figure_caption: List[Any] | None = (
            None  # Body to restore after buffering a figure caption (buffer-swap idiom)
        )
        self._figure_block_width: str | None = (
            None  # Converted :figwidth: value (LEN-01); set in visit_figure,
            # consumed + reset in depart_figure. Typst's figure() rejects a
            # direct width: kwarg, so a non-None value means the whole
            # figure() call is wrapped in block(width: ...)[...] (D-03/Pitfall 3).
        )

        # FIG-01 (Phase 43): a figure nested inside another figure's legend
        # would otherwise clobber the enclosing figure's in-progress scalar
        # state, since every figure_* scalar above is a flat instance
        # attribute with no notion of "which figure is currently being
        # filled" -- mirrors _table_state_stack's TBL-04 fix (plan 43-01).
        # _push_figure_state()/_pop_figure_state() save/restore a full
        # snapshot of that scalar set around a NESTED visit_figure/
        # depart_figure pair only (never for a top-level figure, which stays
        # byte-identical) -- see the docstrings on those two methods.
        self._figure_state_stack: List[Dict[str, Any]] = []

        # Whether THIS figure (the one currently open) has a legend child --
        # set in visit_figure from a scan of node.children (the doctree is
        # fully built before any visiting begins, so this check is reliable
        # at visit time, same reasoning visit_table's captioned pre-check
        # documents). Gates the {...} body-wrap that lets the legend's
        # content join the image() call as ONE positional body argument
        # (43-RESEARCH.md Pattern 2). Never True for a figure with no
        # legend child, so an image-only figure's emitted bytes are
        # unaffected (SC#4).
        self._figure_has_legend: bool = False

        # Code block container state (Issue #20)
        self.in_captioned_code_block = False
        self.code_block_caption = ""
        self.code_block_label = ""

        # Unified code mode state
        self.in_paragraph = False
        self.paragraph_has_content = False  # Track if paragraph has any content nodes
        self.in_list_item = False  # Track if currently in a list item
        # Stack of prior in_list_item values, pushed on each visit_list_item
        # and popped on depart_list_item. A bare boolean loses the outer
        # item's context when a NESTED list closes (its depart_list_item would
        # otherwise reset the flag to False), which mis-classifies a paragraph
        # following a nested list as top-level and emits an unseparated
        # `par(...)` right after the nested `list(...)` -> `})par(` syntax error.
        self._list_item_stack: List[bool] = []

        # Stack of (in_list_item, list_item_needs_separator) pairs pushed by
        # visit_legend and popped by depart_legend (43-REVIEW.md CR-01,
        # Phase 43 gap closure). A figure's legend borrows the in-list-item
        # separator machinery purely to newline-separate its first child
        # from the preceding image(...) expression (see visit_legend's
        # docstring) -- but a legend can itself contain a NESTED figure
        # whose own legend also visits. Two flat scalars cannot represent
        # more than one level: the inner legend's visit_legend would
        # overwrite the outer legend's saved values with its own
        # already-mutated True/True before the outer depart_legend ever
        # restores them, leaking in_list_item=True into every sibling for
        # the rest of the document. A real stack (mirroring
        # _list_item_stack immediately above) makes each nesting level
        # independent, exactly like _push_figure_state/_pop_figure_state
        # does for the figure scalars proper.
        self._legend_list_item_stack: List[Tuple[bool, bool]] = []
        self.in_literal_block = False  # Track if currently in a code block

        # SIG-01..SIG-05 monospace-propagation flag (37-EMISSION-CONTRACT.md
        # section 2/4): True for the entire duration of a desc_signature's
        # emission (set in visit_desc_signature, cleared in
        # depart_desc_signature). Read by visit_Text, which routes every
        # signature-text run through the monospace primitive (raw(...))
        # instead of the proportional text(...) primitive, with no dedicated
        # per-node handler required for delimiters/keywords/spaces/etc.
        # A plain scalar, not a stack: desc_signature never nests inside
        # desc_signature.
        self.in_signature_text = False

        # SIG-04 D-05 discriminator state (37-EMISSION-CONTRACT.md section
        # 2/5.2): True once the CURRENT desc_parameter's own name (its
        # first text-only-leaf desc_sig_name child) has been emitted, so a
        # later desc_sig_name in the SAME parameter (part of a type
        # annotation) falls through to rule 3 instead of being italicised
        # again. Reset to False in visit_desc_parameter on entry. A scalar,
        # not a stack: desc_parameter never nests inside desc_parameter (a
        # desc_optional group holds desc_parameter SIBLINGS, each of which
        # resets the flag on its own entry).
        self._param_name_seen = False

        # SIG-08 emission-position marker (37-EMISSION-CONTRACT.md section 8;
        # made buffer-identifying by 38-05, 38-EMISSION-CONTRACT.md section
        # 6.4, closing the folded todo
        # .planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md):
        # records (id(self.body), len(self.body)) immediately after a `desc`'s
        # own parbreak() was emitted, so depart_desc can tell whether anything
        # has been emitted since -- the discriminator that lets a nested
        # `desc`'s duplicate break be suppressed without a desc-nesting-depth
        # counter. The identity half exists because self.body is reassigned
        # at multiple sites (visit_term/visit_definition via
        # _saved_body_stack, the admonition-title save/restore, the
        # figure-caption save/restore, plus the table-cell routing in
        # add_text) -- a bare position integer recorded against one buffer
        # could otherwise spuriously match (or fail to match) a position in a
        # DIFFERENT buffer after a swap. Comparing both halves, rather than
        # adding a sixth per-site guard, is the fix (the existing in_table
        # guard already demonstrates that per-site guards do not generalise).
        self._desc_break_marker: tuple[int, int] | None = None

        # Stream-based list rendering state (Issue #61)
        self.is_first_list_item = True  # Track if current item is first in list
        self.list_item_needs_separator = (
            False  # Track if + is needed before next element
        )
        self._in_reference_with_target = (
            False  # Track if reference has following target for markup mode wrapping
        )
        self._in_markup_mode = (
            False  # Track if currently inside markup mode block [...] for # prefix
        )
        # D-14 (Phase 40): the namespaced <docname:idN> anchor token for the
        # reference CURRENTLY being emitted, or None. Set in visit_reference,
        # consumed/cleared in depart_reference. A single scalar slot is
        # sufficient -- not a stack -- because a reference node cannot nest
        # inside another reference node (mirrors the existing
        # _reference_was_list_item_needs_separator precedent). This is a
        # NEW slot, never a fourth consumer of the _strong_was_* slots
        # (Phase 36 D-01/D-02 warn against exactly that).
        self._reference_own_anchor: str | None = None
        # D-07 (Phase 48): the D-07 guard's close string
        # (`_label_existence_guard()`'s `close_str`) for the guarded
        # cross-document reference CURRENTLY being emitted, or None. Set
        # in visit_reference's cross-document branch, consumed/cleared in
        # depart_reference in place of the plain closing parenthesis. A
        # single scalar slot, mirroring `_reference_own_anchor`'s own
        # lifecycle exactly -- a reference node cannot nest inside another
        # reference node.
        self._reference_guard_close: str | None = None
        # D-04 (Phase 48): a DEDICATED close-string slot for
        # visit_pending_xref/depart_pending_xref's own D-07 guard --
        # deliberately NOT shared with `_reference_guard_close`. This site
        # is unreachable through Sphinx's normal pipeline
        # (`ReferencesResolver` replaces every `pending_xref` node
        # unconditionally before the writer runs, `48-RED-EVIDENCE.md`'s
        # D-04 section), so a stale value here can never leak into a real
        # `visit_reference` call in practice -- but a dedicated slot means
        # this defence-in-depth site cannot corrupt the reachable one's
        # state even in principle, regardless of that argument.
        self._pending_xref_guard_close: str | None = None
        self.in_desc_parameter = (
            False  # Track if inside desc_parameter to avoid newlines between text nodes
        )
        self._in_link = False  # Track if inside link() function for + concatenation
        self._desc_parameter_has_content: bool = (
            False  # Track if desc_parameter has content for + separator
        )
        self._is_first_desc_signature_line: bool = (
            True  # Track if next desc_signature_line is the first (DESC-02);
            # reset per signature in visit_desc_signature
        )
        self._link_has_content: bool = (
            False  # Track if link has content for + separator
        )

        # Block-quote / epigraph attribution code-mode concat context. An
        # attribution node holds INLINE children directly (Text/emphasis/
        # literal/reference) -- no wrapping paragraph -- so, like a def-list
        # term or link body, adjacent children juxtapose in code mode unless
        # + separated. visit_attribution emits the attribution as a CODE-MODE
        # `attribution: { ... }` argument (mirroring the code-mode quote body,
        # bug #15) and activates this context so the children are evaluated
        # content (`emph({...}) + text(...) + raw(...)`), not literal prose --
        # a markup-mode `attribution: [ ... ]` argument would leave the
        # code-mode children as literal source that Typst typesets verbatim
        # (e.g. `text("Author")` shown as `text(“Author”)`).
        self._in_attribution = False
        self._attribution_has_content: bool = False

        # Definition list state
        self.in_definition_list = False
        self._in_term = False  # Track if buffering a def-list term for + concatenation
        self._term_has_content: bool = (
            False  # Track if the term buffer has content for + separator
        )
        self.current_term_buffer: str | List[str] | None = None
        self.current_definition_buffer: List[str] | None = None

        # Field-body code-mode concat context. A field body written inline on
        # its field line (e.g. ':default: The value of **x**') is COLLAPSED by
        # docutils to inline children (Text/strong/literal) directly under
        # field_body -- no wrapping paragraph. Those juxtapose in code mode
        # unless + separated (bug #8). Activated by visit_field_body for an
        # all-inline field body (the collapsed-inline case) AND for a field
        # body whose only child is a single nodes.paragraph (FLD-02, D-07,
        # the ordinary :param:/:returns: docstring case) -- both reuse the
        # SAME concat context; _field_body_stack saves the prior values for
        # nesting safety.
        self._in_field_body = False
        self._field_body_has_content: bool = False
        # Distinguishes the single-paragraph-unwrapped case (this flag True)
        # from the docutils-collapsed-inline case (this flag False while
        # _in_field_body is True) -- the ONE new attribute FLD-02 needs
        # (D-12). visit_paragraph/depart_paragraph read it to skip the
        # block-level par(...) wrapper; depart_field_body reads it to keep
        # _last_field_body_was_inline scoped to the genuinely collapsed case
        # only (the D-07/D-08 trap: naively setting that flag for BOTH cases
        # would let depart_field's FID-09 inter-field separator fire between
        # newly-inlined single-value fields and merge them onto one line).
        self._field_body_unwrapped_paragraph: bool = False
        self._field_body_stack: List[Tuple[bool, bool, bool]] = []
        # Whether the most recently departed field_body used the collapsed
        # inline form (see visit_field_body). depart_field reads this to
        # decide whether the FID-09 inter-field "  " separator applies --
        # it is only correct for inline-collapsed bodies, never for a
        # block-wrapped (par(...)) OR single-paragraph-unwrapped body
        # (CR-01, and FLD-02's D-07/D-08 trap above).
        self._last_field_body_was_inline = False

        # Stack of the code-mode concat context suppressed while an inline
        # block element (emphasis/strong/reference) emits its OWN block/argument
        # content. Each entry is the (flag, has_content) attribute-name pair
        # saved by _enter_inline_concat_element and restored by
        # _exit_inline_concat_element (or None when no context was active).
        self._inline_concat_stack: List[Tuple[str, str] | None] = []
        # (term, definition) pairs for the CURRENT (innermost) definition list.
        # Aliases the top of _deflist_items_stack so a nested definition list
        # cannot clobber the enclosing list's collected items.
        self.definition_list_items: List[Tuple[str, str]] = []
        # Stacks that make definition-list buffering re-entrant. A definition
        # may CONTAIN a nested definition list (e.g. an autodoc docstring whose
        # first block IS a definition list); each level must save/restore its
        # own body buffer, pending term, and item collection. A single slot
        # (the old self.saved_body / current_*_buffer) is overwritten by the
        # inner list, orphaning the outer body -- both the outer definition's
        # content AND any body written afterward (a desc_signature + its <id>
        # anchor) are then silently dropped, dangling the cross-reference link
        # (GATE-02 fatal #18). Mirrors the _list_item_stack (bug #4) and
        # _inline_concat_stack (bug #5) stack idiom.
        self._saved_body_stack: List[List[Any]] = []
        self._deflist_items_stack: List[List[Tuple[str, str]]] = []
        self._pending_term_stack: List[str | None] = []

        # Admonition title state (buffer-swap idiom, mirrors definition-list terms)
        self._pending_admonition_title: str | None = (
            None  # Rendered inline content of a dynamic (node-derived) title
        )
        self._in_admonition_title: bool = (
            False  # Track if currently buffering an admonition title node
        )
        self._saved_body_for_admonition_title: List[Any] | None = (
            None  # Body to restore after buffering an admonition title
        )
        self._custom_admonition_title: str | None = (
            None  # Static title: for the ten real Sphinx admonition types
            # (note, warning, tip, important, caution, seealso, hint, error,
            # danger, attention) this is looked up from
            # sphinx.locale.admonitionlabels inside _visit_admonition
            # (D-04/D-05); for todo_node it remains the caller-supplied
            # inert fallback ("Todo"), since todo_node is not a catalog key.
        )
        self._title_section_ids: List[str] = (
            []  # Parent section's ids, captured in visit_title for the
            # matching depart_title's anchor emission (see visit_title)
        )

        # Topic state (BLK-02/D-01/D-02/D-05): distinguishes a box-less
        # `.. contents::` topic (bullet_list pass-through) from a generic
        # `.. topic::` (rendered as a titled clue box via _visit_admonition)
        self._topic_is_contents: bool = False

        # Line block state (BLK-03/D-03/D-04): a single integer nesting-depth
        # counter -- docutils' own visitor recursion already provides the
        # "stack" for nested line_block, so no separate data structure is
        # needed. The two `_was_*` attributes save/restore the surrounding
        # in_paragraph/paragraph_has_content state around the outer
        # par({...}) wrapper (depth 0 only).
        self._line_block_depth: int = 0
        self._line_block_was_in_paragraph: bool = False
        self._line_block_was_paragraph_has_content: bool = False

        # Phase 49 (D-04's occurrence rule): per-document counter, keyed by
        # child docname, of how many of THIS document's own toctree entries
        # (flattened across every `.. toctree::` directive the document
        # has, in document order) have already named that child. A fresh
        # translator instance is constructed by `TypstWriter.translate()`
        # for EVERY document it translates (see that method), so this
        # counter is per-document without any explicit reset here.
        self._toctree_entry_occurrences: Dict[str, int] = {}

    def astext(self) -> str:
        """
        Return the translated text as a string.

        Returns:
            The translated Typst markup
        """
        return "".join(self.body)

    def add_text(self, text: str) -> None:
        """
        Add text to the output body or table cell content.

        Args:
            text: The text to add
        """
        if (
            hasattr(self, "in_table")
            and self.in_table
            and hasattr(self, "table_cell_content")
        ):
            self.table_cell_content.append(text)
        else:
            self.body.append(text)

    def _emit_forced_break(self, break_token: str) -> None:
        """
        Emit a real Typst stdlib break (``parbreak()``/``linebreak()``) as its
        own code-mode statement between two adjacent siblings.

        A source ``\\n`` between two code-mode statements is COSMETIC ONLY
        (proven at ``visit_desc_signature_line``) -- it satisfies the Typst
        parser but produces NO visual break, because bare ``text()``/
        ``strong()`` results are inline content that simply concatenates.
        This helper generalizes that idiom, but fixes a gap in the original:
        ``visit_desc_signature_line``'s break always fires INSIDE an
        already-open ``strong({...})`` block, where ``visit_strong`` has
        locally forced ``in_list_item = True`` for its children, so its
        trailing separator comes "for free" from the next child's own
        ``list_item_needs_separator`` check. A SIBLING-boundary break (between
        ``desc_signature``s, after a ``rubric``, after a ``desc``) usually is
        NOT inside such a block, so this helper appends its OWN unconditional
        trailing newline -- omitting it reproduces the "expected semicolon or
        line break" Typst fatal at sibling boundaries.

        Args:
            break_token: The Typst stdlib break call to emit, e.g.
                ``"parbreak()"`` or ``"linebreak()"``.
        """
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text(f"{break_token}\n")
        if self.in_list_item:
            self.list_item_needs_separator = True

    def _add_paragraph_separator(self) -> None:
        """
        Add + operator for concatenation in paragraph if not first node.

        In unified code mode, paragraph content nodes are concatenated with +.
        This method adds ' + ' before each node except the first one.
        """
        if self.in_paragraph and self.paragraph_has_content:
            self.add_text("\n")
        if self.in_paragraph:
            self.paragraph_has_content = True

    def _emit_id_anchors(
        self, node: nodes.Node, skip_ids: set[str] | None = None
    ) -> None:
        """
        Emit a zero-width ``[#metadata(none) <id>]`` Typst anchor for every id
        carried on a body element so a same-document ``link(<id>, ...)``
        reference resolves to it.

        docutils' ``PropagateTargets`` transform moves an explicit
        ``.. _target:`` id onto the ids of the *following* body element
        (paragraph, bullet/enumerated list, table, image, admonition,
        line-block, block-quote, definition-list, ...). Unless that element
        emits a matching ``<id>`` anchor, a same-document ``:ref:`` -- which
        ``depart_reference`` renders as ``link(<_sanitize_label(id)>, ...)`` --
        dangles, and ``typst.compile()`` aborts the ENTIRE document at the
        semantic label-resolution pass with ``label ... does not exist``.

        Mirrors the proven target-anchor form (``visit_target``, bug #2) and the
        desc-signature anchor (bug #17): a zero-content markup block that carries
        the label and joins cleanly as its own statement in the surrounding
        code-mode block. The surrounding newlines separate it from any adjacent
        code-mode expression on both sides (a bare code-mode ``label("id")``
        would juxtapose/fail to join). Every id is routed through
        ``_sanitize_label`` (bug #10) so the anchor name byte-matches the
        reference side. Ids are globally unique per document (docutils
        ``make_id``), so no label is defined twice; dedupe defensively.

        A node with NO ids emits nothing -- byte-for-byte unchanged output, so
        every existing anchorless-body-element expectation is preserved. Inside
        a list item the same leading-separator / needs-separator machinery the
        surrounding block visitors use is driven here, so the anchor and the
        element's own emission stay newline-separated (never ``]par(`` /
        ``]list(`` juxtaposition, never a stranded ``+``).

        ``skip_ids`` lets a caller that ALREADY anchors one of the node's ids
        by another mechanism suppress a duplicate definition here. There are
        two such callers, ``depart_figure`` and ``depart_table`` (Phase 25),
        and they share one rationale: both wrap their content in a Typst
        ``figure(...)`` that self-anchors ``ids[0]`` as that figure's own
        ``<label>`` postfix, so re-anchoring ``ids[0]`` here too would define
        the same label TWICE -- a Typst "label ... occurs multiple times"
        compile fatal. Both still need ``ids[1:]`` anchored here, because
        docutils' ``PropagateTargets`` transform lands an immediately
        preceding ``.. _target:``'s id there, and a same-document ``:ref:``
        to it would otherwise dangle. ``depart_table`` additionally passes an
        EMPTY ``skip_ids`` (anchoring every id, including ``ids[0]``) for a
        table that is structurally captioned but did NOT actually take the
        figure-wrapped branch (TBL-05, Phase 43: a title node whose rendered
        content is the empty string) -- nothing else self-anchors ``ids[0]``
        for that table, so skipping it here would leave it unanchored. The
        table caller also has a firing-order constraint the figure caller
        does not (Phase 42 / TBL-03): see the inline comments at its own
        call site for why it must run after ``self.in_table`` is cleared.
        When every id is skipped the method is a no-op (list-item bookkeeping
        is untouched), keeping output byte-for-byte identical.

        Args:
            node: The body-element node whose ``ids`` should be anchored.
            skip_ids: Raw docutils ids to NOT anchor here (already anchored by
                the caller). Defaults to anchoring every id.
        """
        ids = node.get("ids") or []
        if not ids:
            return
        skip = skip_ids or set()
        docname = self._current_docname()
        seen: set[str] = set()
        pending: list[str] = []
        for node_id in ids:
            if node_id in skip:
                continue
            label_id = self._namespace_label(docname, node_id)
            if label_id in seen:
                continue
            seen.add(label_id)
            pending.append(label_id)
        if not pending:
            return
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        for label_id in pending:
            self.add_text(f"\n[#metadata(none) <{label_id}>]\n")
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_document(self, node: nodes.document) -> None:
        """
        Visit a document node.

        Generates opening code block wrapper for unified code mode.

        Also builds the FN-01 footnote pre-pass index (D-01): a
        `{docutils-id: footnote-node}` dict built via
        `self.document.findall(nodes.footnote)` BEFORE any body content is
        visited, because footnote *definitions* are frequently positioned
        AFTER their citing footnote_references in source order (e.g. under
        a trailing `.. rubric:: Footnotes` -- see 14-RESEARCH.md "Verified
        Mechanism 2" finding 5). Uses `self.document`, not the `node`
        argument, per 14-RESEARCH.md Pitfall 4. `findall()` is used instead
        of D-01's literal `traverse()` wording -- `Node.traverse()` is
        deprecated in this repo's pinned docutils and raises under the
        project's strict `error::DeprecationWarning` pytest filter
        (pyproject.toml); `findall()` is its direct, non-deprecated
        replacement with identical semantics for this call. Deviation
        Rule 1 (auto-fixed bug). `self._emitted_footnote_ids` tracks which
        ids have already emitted their definition form (D-03).

        Args:
            node: The document node
        """
        self._footnote_index = {
            n["ids"][0]: n
            for n in self.document.findall(nodes.footnote)
            if n.get("ids")
        }
        self._emitted_footnote_ids: set = set()

        # Start code block for unified code mode (all content uses function syntax without # prefix)
        self.add_text("#{\n")

        # G-48-4 / XREF-03 (Phase 48 plan 07): every content file emits its
        # own whole-document self-anchor exactly once, immediately after
        # the opening code-block brace, in the established zero-width
        # `metadata` anchor form `_emit_id_anchors` already uses -- so a
        # whole-document reference (`visit_reference`'s cross-document
        # branch, below) has a real per-document label to guard against
        # instead of falling into the external-link string-url branch.
        # Emitted ONLY when the builder supplies a current docname:
        # hand-built test doctrees (no builder docname) keep byte-identical
        # output, matching every other `_current_docname()`-gated site.
        docname = self._current_docname()
        if docname:
            self_anchor_label = self._namespace_label(
                docname, _WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN
            )
            self.add_text(f"[#metadata(none) <{self_anchor_label}>]\n")

    def depart_document(self, node: nodes.document) -> None:
        """
        Depart a document node.

        Generates closing code block wrapper for unified code mode.

        Args:
            node: The document node
        """
        # Close code block for unified code mode
        self.add_text("}\n")

    def visit_section(self, node: nodes.section) -> None:
        """
        Visit a section node.

        Args:
            node: The section node
        """
        # Increment section level
        self.section_level += 1

    def depart_section(self, node: nodes.section) -> None:
        """
        Depart a section node.

        Args:
            node: The section node
        """
        # Decrement section level
        self.section_level -= 1
        # Add a newline after sections
        self.add_text("\n")

    def visit_title(self, node: nodes.title) -> None:
        """
        Visit a title node.

        Generates heading() function call with level parameter.
        Child text nodes will be wrapped in text() automatically.

        Exception: Inside an admonition or a topic (D-02), the title is not
        a section heading -- buffer its rendered inline content (via the
        standard inline visitors) so it can be attached as a code-block
        title argument at depart time instead of emitted here (see
        _depart_admonition). A `.. contents::` topic (D-05) additionally
        records the insertion point for its box-less bold label. A
        `.. table::`/csv-table/list-table CAPTION (TBL-01, Phase 25) is
        ALSO a title -- docutils stores it as a `title` child of
        nodes.table -- and is buffered here too, self-contained and
        checked FIRST (before the admonition/topic/section paths), since
        it must reuse `self.table_cell_content` as its buffer rather than
        a `self.body` swap (see the docstring on the branch below).

        Args:
            node: The title node
        """
        # TBL-01/Pattern 1 (Phase 25): a table caption is visited WHILE
        # self.in_table is still True (visit_table sets it before any
        # child, including this title, is visited). add_text()'s dispatch
        # rule is `self.in_table and hasattr(self, "table_cell_content")`
        # -- it does NOT consult self.body -- so buffering via a
        # self.body swap (the figure-caption idiom) would NOT change
        # where add_text() routes: every inline visitor called while
        # processing this caption (visit_Text, visit_emphasis, ...) would
        # still misroute into table_cell_content regardless. Reusing
        # table_cell_content as the buffer (which add_text() already
        # targets) is therefore required, not a stylistic choice
        # (25-RESEARCH.md Critical Pitfall 2). Checked first and
        # self-contained (its own save/restore, not the Pitfall-1 idiom
        # below) so it can `return` before emitting any heading() call --
        # the bug this fixes (25-RESEARCH.md Verified Mechanism 1) is that
        # a table-caption title previously fell through to the generic
        # section-heading path below, emitting a stray heading().
        if self.in_table:
            self._in_table_caption = True
            self.table_cell_content = []
            self._caption_saved_list_state = (
                self.in_list_item,
                self.list_item_needs_separator,
            )
            self.in_list_item = True
            self.list_item_needs_separator = False
            return

        # Pitfall-1 fix: a title's own children (Text, emphasis, strong,
        # ...) currently concatenate with NO separator, because a title's
        # child-stream sets neither in_paragraph nor in_list_item. Treat
        # this title's own children like list_item content -- mirrors the
        # exact idiom visit_emphasis/visit_strong already use for their own
        # children ("treat it like list_item"). Restored in depart_title on
        # EVERY return path below.
        self._title_was_in_list_item = self.in_list_item
        self._title_was_list_item_needs_separator = self.list_item_needs_separator
        self.in_list_item = True
        self.list_item_needs_separator = False

        # D-02: admonition titles AND topic titles are deferred via
        # buffer-swap -- nodes.topic is NOT a subclass of nodes.Admonition,
        # so this is a literal additive `or`, never an MRO trick. The
        # existing Admonition path body is untouched; only more parent
        # types now enter it.
        if isinstance(node.parent, nodes.Admonition) or isinstance(
            node.parent, nodes.topic
        ):
            # D-05: a `.. contents::` topic's title must be inserted BEFORE
            # the already-streaming bullet_list, not appended after (the
            # list is the topic's second child and streams to self.body
            # before depart_title/depart_topic run) -- record the insertion
            # point now, since nothing has been emitted for this topic yet
            # (title is always a topic's first child).
            if isinstance(node.parent, nodes.topic) and "contents" in (
                node.parent.get("classes", []) or []
            ):
                self._contents_title_insert_at = len(self.body)
            self._saved_body_for_admonition_title = self.body
            self.body = []
            self._in_admonition_title = True
            return

        # Sections always carry docutils-assigned ids (auto-slugged from the
        # title, or merged in from a preceding explicit `.. _label:` target)
        # -- internal cross-references (e.g. a figure's internal `:target:`,
        # FIG-02/D-03) resolve to these ids via refid and require a matching
        # Typst anchor to exist, or the compile aborts with "label does not
        # exist" (Issue #114 GATE-01 discovery). Typst's `<label>` anchor
        # syntax is only valid as a markup-mode postfix, so -- exactly like
        # visit_figure's bracket-wrap fix -- bracket-wrap the heading() call
        # in markup content when the parent section has ids.
        self._title_section_ids = (
            node.parent.get("ids") if isinstance(node.parent, nodes.section) else None
        ) or []
        # TOC-01/D-07: clamp to a minimum of 1 -- a top-level titled
        # non-section (section_level == 0) would otherwise pass a rejected
        # depth argument of 0 to the heading call below. Typst's relative
        # depth argument is constrained the same way its absolute level
        # argument was (values must be >= 1), so this clamp's mechanism
        # survives the level->depth switch unchanged; only the argument it
        # clamps is relative now, not an absolute final level.
        emitted_depth = max(1, self.section_level)
        # Pitfall-1 fix: wrap the title content in a code block {...} so
        # multi-child title content is one expression, not several
        # juxtaposed statements (mirrors _depart_admonition's existing
        # {...} wrap of the buffered admonition title).
        if self._title_section_ids:
            self.add_text(f"[#heading(depth: {emitted_depth}, {{")
        else:
            # Use heading() function (no # prefix in code mode)
            self.add_text(f"heading(depth: {emitted_depth}, {{")

    def depart_title(self, node: nodes.title) -> None:
        """
        Depart a title node.

        Closes heading() function call.

        Exception: Inside an admonition or topic, capture the buffered
        inline content as the pending title and restore the main output
        stream. A `.. contents::` topic (D-05) inserts its buffered title
        as a bold label ahead of its already-streamed bullet_list instead
        of consuming it as a box title argument. A table caption (TBL-01,
        Phase 25) captures the buffered `table_cell_content` into
        `self.table_caption` for `depart_table` to consume, instead of
        emitting a heading() close.

        Args:
            node: The title node
        """
        if self._in_table_caption:
            self.table_caption = "".join(self.table_cell_content).strip()
            self.table_cell_content = []
            self.in_list_item, self.list_item_needs_separator = (
                self._caption_saved_list_state
            )
            self._in_table_caption = False
            return

        if self._in_admonition_title:
            self._pending_admonition_title = "".join(self.body)
            if self._saved_body_for_admonition_title is not None:
                self.body = self._saved_body_for_admonition_title
            self._saved_body_for_admonition_title = None
            self._in_admonition_title = False
            self.in_list_item = self._title_was_in_list_item
            self.list_item_needs_separator = self._title_was_list_item_needs_separator

            if hasattr(self, "_contents_title_insert_at"):
                # D-05: insert (not append) the bold label at the recorded
                # index so it lands ABOVE the already-streamed bullet_list.
                label = f"strong({{{self._pending_admonition_title}}})\n\n"
                self.body.insert(self._contents_title_insert_at, label)
                self._pending_admonition_title = None
                del self._contents_title_insert_at
            return

        if self._title_section_ids:
            # Close the heading() call, attach the first id as the markup
            # anchor, and close the markup bracket opened in visit_title.
            # Typst only accepts one <label> per content element, so any
            # additional ids (e.g. both an auto-slugged name and a merged-in
            # explicit target name) get a zero-width metadata(none) anchor
            # each, pointing at the same document location.
            docname = self._current_docname()
            primary_id, *extra_ids = self._title_section_ids
            self.add_text(f"}}) <{self._namespace_label(docname, primary_id)}>]\n")
            for extra_id in extra_ids:
                self.add_text(
                    f"[#metadata(none) <{self._namespace_label(docname, extra_id)}>]\n"
                )
            self.add_text("\n")
        else:
            # Close heading() function
            self.add_text("})\n\n")
        self._title_section_ids = []
        self.in_list_item = self._title_was_in_list_item
        self.list_item_needs_separator = self._title_was_list_item_needs_separator

    def visit_subtitle(self, node: nodes.subtitle) -> None:
        """
        Visit a subtitle node.

        Generates emph() function for subtitle (no # prefix in code mode).
        Child text nodes will be wrapped in text() automatically.

        Args:
            node: The subtitle node
        """
        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Use emph() function for subtitle (no # prefix in code mode)
        self.add_text("emph(")

        # Store state to restore in depart
        self._subtitle_was_in_paragraph = was_in_paragraph

    def depart_subtitle(self, node: nodes.subtitle) -> None:
        """
        Depart a subtitle node.

        Closes emph() function.

        Args:
            node: The subtitle node
        """
        # Close emph() function
        self.add_text(")\n\n")

        # Restore paragraph state
        if hasattr(self, "_subtitle_was_in_paragraph"):
            self.in_paragraph = self._subtitle_was_in_paragraph
            delattr(self, "_subtitle_was_in_paragraph")

    def visit_compound(self, node: nodes.compound) -> None:
        """
        Visit a compound node.

        Compound nodes are containers that group related content.
        They are often used to wrap toctree directives.

        Args:
            node: The compound node
        """
        # A propagated explicit target (``.. _t:`` before a ``.. toctree::``,
        # which docutils wraps in a ``compound``) lands its id here; anchor it
        # so a same-document link(<id>, ...) resolves. A plain toctree compound
        # carries no ids -> no-op, byte-unchanged.
        self._emit_id_anchors(node)

    def depart_compound(self, node: nodes.compound) -> None:
        """
        Depart a compound node.

        Args:
            node: The compound node
        """
        pass

    def visit_container(self, node: nodes.container) -> None:
        """
        Visit a container node.

        Handle Sphinx-generated containers, particularly literal-block-wrapper
        for captioned code blocks (Issue #20).

        Args:
            node: The container node
        """
        # A referenceable target lands its id on the container: either an
        # explicit ``:name:`` on a captioned code block (the id sits on the
        # outer ``literal-block-wrapper`` container, NOT the inner
        # literal_block) or a propagated ``.. _t:`` before a
        # ``.. container::``. Anchor it so a same-document link(<id>, ...)
        # resolves. Guarded on ``names`` so the AUTO id docutils assigns to
        # every captioned code block for numref (ids present, names absent,
        # never referenced) is NOT anchored -- keeping the common
        # captioned-block output byte-for-byte unchanged.
        if node.get("names"):
            self._emit_id_anchors(node)
        # Check if this is a literal-block-wrapper (captioned code block)
        if "literal-block-wrapper" in node.get("classes", []):
            self.in_captioned_code_block = True
            # Caption and literal_block children will be processed separately
            # We need to extract caption text first
            for child in node.children:
                if isinstance(child, nodes.caption):
                    self.code_block_caption = child.astext()
                elif isinstance(child, nodes.literal_block):
                    # Extract label from :name: option
                    if child.get("names"):
                        self.code_block_label = child.get("names")[0]
        # Other container types: just process children
        pass

    def depart_container(self, node: nodes.container) -> None:
        """
        Depart a container node.

        Args:
            node: The container node
        """
        # Reset state after literal-block-wrapper
        if "literal-block-wrapper" in node.get("classes", []):
            self.in_captioned_code_block = False
            self.code_block_caption = ""
            self.code_block_label = ""

    def visit_paragraph(self, node: nodes.paragraph) -> None:
        """
        Visit a paragraph node.

        Wraps paragraph content in par() function for unified code mode.
        Code mode doesn't auto-recognize paragraph breaks from blank lines.

        FLD-02/D-07 (38-EMISSION-CONTRACT.md section 4.2) is checked FIRST,
        deliberately, ahead of the list-item fast-path below: a field body
        whose ONLY child is this single paragraph (the ordinary
        ``:param:``/``:returns:`` docstring shape) skips the ``par({``/
        ``})`` wrapper, because Typst's ``par(...)`` is intrinsically
        block-level and starts a new visual line regardless of any
        separator -- FLD-02's root defect. The order matters because
        nothing resets ``in_list_item`` for a
        ``field_list``/``field``/``field_body``/``paragraph`` nested inside
        a list item, so it remains True for a field-body paragraph
        documented inside a bullet or enumerated list item; checking
        ``in_list_item`` first would let it unconditionally win and
        reintroduce the exact pre-Phase-38 label/value split
        (38-VERIFICATION.md gap 1, 38-REVIEW.md CR-01). See
        visit_field_body's docstring for the classification and
        depart_field_body's for the D-07/D-08 trap this interacts with.

        Exception: Inside list items -- once the FLD-02 case above has
        already been ruled out -- paragraphs are not wrapped in par() to
        avoid syntax like "- par(text(...))" which is invalid. A 2nd+
        paragraph in a list item instead gets a real Typst parbreak()
        (FID-02) -- a bare source '\\n' between code-mode statements is
        cosmetic only and produces no visual break, so consecutive
        list-item paragraphs otherwise concatenate onto one running line.
        D-13 (38-EMISSION-CONTRACT.md section 4.5): this stray parbreak()
        also fires at the head of every bulleted list item whose sole
        content is a paragraph -- an ordinary list-item paragraph, or a
        multi-value field body's own bulleted list items -- and Phase 38
        leaves it in place by design; its exact shape is pinned by
        tests/test_inline_math_after_text_render_gate.py:291.

        Args:
            node: The paragraph node
        """
        # A propagated explicit target (docutils PropagateTargets) moves its id
        # onto the FOLLOWING paragraph's node["ids"]; emit the matching Typst
        # anchor(s) so a same-document link(<id>, ...) resolves. No ids -> no-op
        # (byte-unchanged). Emitted at paragraph block level -- before the par()
        # wrap and outside any inline concat context -- so it never juxtaposes
        # or strands a `+`. (GATE-02 corpus fatal #20: <xref-modifiers>.)
        self._emit_id_anchors(node)

        # FLD-02/D-07: skip the block-level par(...) wrapper for a
        # single-value field body's sole paragraph child. Checked BEFORE
        # in_list_item below -- see this method's docstring for why the
        # order is load-bearing, not incidental. The paragraph's children
        # then dispatch unmodified through the SAME inline-concat machinery
        # visit_field_body activated (_in_field_body /
        # _field_body_has_content) -- no par() to open, so in_paragraph
        # stays False and nothing else is emitted here.
        if self._field_body_unwrapped_paragraph:
            self.in_paragraph = False
            return

        # Skip par() wrapping inside list items; emit a real parbreak()
        # between the 2nd+ paragraph and its predecessor (FID-02). This is a
        # no-op for the FIRST paragraph in a list item, since
        # list_item_needs_separator is reset to False in visit_list_item.
        if self.in_list_item:
            self._emit_forced_break("parbreak()")
            self.in_paragraph = False
            return

        # Start par() with {} content block (no # prefix in code mode)
        self.in_paragraph = True
        self.paragraph_has_content = False
        self.add_text("par({")

    def depart_paragraph(self, node: nodes.paragraph) -> None:
        """
        Depart a paragraph node.

        Closes par({}) function and adds spacing.

        Mirrors visit_paragraph's ORDER exactly (see that method's
        docstring for why the order is load-bearing): the FLD-02/D-07
        branch is checked BEFORE the list-item branch, because
        ``in_list_item`` remains True for a field-body paragraph nested
        inside a list item and would otherwise win. No ``par({...})`` was
        opened for a single-value field body's sole paragraph, so there is
        nothing to close here either -- and, deliberately,
        ``list_item_needs_separator`` is NOT set for this case: the
        field-body paragraph opened no wrapper and emitted no block-level
        statement of its own, so there is nothing for a following sibling
        to be separated from that the field-body concat machinery and
        depart_field_body's own trailing bytes do not already handle.

        Args:
            node: The paragraph node
        """
        # FLD-02/D-07: mirrors the skip in visit_paragraph above. Checked
        # BEFORE in_list_item below -- see this method's docstring.
        if self._field_body_unwrapped_paragraph:
            self.in_paragraph = False
            return

        # Skip closing if inside list items; mark that a paragraph separator
        # is now needed before the next list-item sibling (FID-02) -- this is
        # the piece that was previously MISSING, so the helper in
        # visit_paragraph never actually fired a leading "\n" before the
        # 2nd+ paragraph's parbreak().
        if self.in_list_item:
            self.list_item_needs_separator = True
            return

        # Close par({}) content block and add spacing
        self.in_paragraph = False
        self.paragraph_has_content = False
        self.add_text("})\n\n")

    def visit_comment(self, node: nodes.comment) -> None:
        """
        Visit a comment node.

        Comments are skipped entirely in Typst output as they are meant
        for source-level documentation only.

        Args:
            node: The comment node

        Raises:
            nodes.SkipNode: Always raised to skip the comment
        """
        raise nodes.SkipNode

    def depart_comment(self, node: nodes.comment) -> None:
        """
        Depart a comment node.

        Args:
            node: The comment node

        Note:
            This method is not called when SkipNode is raised in visit_comment.
        """
        pass

    def visit_substitution_definition(
        self, node: nodes.substitution_definition
    ) -> None:
        """
        Visit a substitution_definition node.

        Non-rendering; content injected at use sites (substitution_reference,
        resolved by a docutils transform before the writer runs) -- matches
        docutils/Sphinx's HTML and LaTeX writers, which also skip this node.
        Without a handler, the node falls through to unknown_visit (warns but
        does not skip), letting its inline children leak out as juxtaposed
        top-level expressions.

        Args:
            node: The substitution_definition node

        Raises:
            nodes.SkipNode: Always raised to skip the definition and its
                children (the definition itself produces no output)
        """
        raise nodes.SkipNode

    def visit_raw(self, node: nodes.raw) -> None:
        """
        Visit a raw node.

        Pass through content if format is 'typst', otherwise skip.

        Args:
            node: The raw node

        Raises:
            nodes.SkipNode: When format is not 'typst'
        """
        format_name = node.get("format", "").lower()

        if format_name == "typst":
            # Output the raw Typst content directly
            content = node.astext()
            if content:  # Only add non-empty content
                self.add_text(content)
                self.add_text("\n\n")
            raise nodes.SkipNode
        else:
            # Skip content for other formats
            logger.debug(f"Skipping raw node with format: {format_name}")
            raise nodes.SkipNode

    def depart_raw(self, node: nodes.raw) -> None:
        """
        Depart a raw node.

        Args:
            node: The raw node

        Note:
            This method is not called when SkipNode is raised in visit_raw.
        """
        pass

    # ------------------------------------------------------------------
    # Code-mode inline concatenation (single source of truth)
    #
    # A def-list term (the code-mode 1st arg of terms.item), a link body (the
    # 2nd arg of link()), and a desc parameter list are all Typst code-mode
    # positions where two juxtaposed expressions are a syntax error
    # ("expected comma"). Adjacent inline sibling expressions in any of these
    # contexts must therefore be joined with " + ". The helpers below are the
    # ONE place that decides "which concat context is active" and "is this the
    # first sibling or a following one", so every inline visitor -- the leaf
    # visit_Text / visit_literal AND the block-opening visit_emphasis /
    # visit_strong / visit_reference -- participates uniformly.
    # ------------------------------------------------------------------

    #: Code-mode concat contexts as (active-flag, has-content-flag) attribute
    #: names, highest precedence first (mirrors the historical elif chain in
    #: visit_Text: desc parameter > link > term).
    _CONCAT_CONTEXTS: Tuple[Tuple[str, str], ...] = (
        ("in_desc_parameter", "_desc_parameter_has_content"),
        ("_in_link", "_link_has_content"),
        ("_in_term", "_term_has_content"),
        ("_in_field_body", "_field_body_has_content"),
        ("_in_attribution", "_attribution_has_content"),
    )

    def _inline_concat_context(self) -> Tuple[str, str] | None:
        """
        Return the ``(active-flag, has-content-flag)`` attribute-name pair of
        the currently active code-mode concat context (def-list term / link
        body / desc parameter), highest precedence first, or ``None`` when no
        such context is active.
        """
        for flag, has_content in self._CONCAT_CONTEXTS:
            if getattr(self, flag, False):
                return (flag, has_content)
        return None

    def _emit_inline_concat_separator(self) -> bool:
        """
        Emit ``" + "`` before the next inline expression when the active
        code-mode concat context already holds an earlier sibling.

        Returns ``True`` when a concat context is active (so the caller skips
        the list-item newline separator), ``False`` otherwise.
        """
        ctx = self._inline_concat_context()
        if ctx is None:
            return False
        if getattr(self, ctx[1]):
            self.add_text(" + ")
        return True

    def _mark_inline_concat_content(self) -> bool:
        """
        Record that the active concat context now holds a sibling expression,
        so the next inline expression is ``" + "`` separated.

        Returns ``True`` when a concat context is active, ``False`` otherwise.
        """
        ctx = self._inline_concat_context()
        if ctx is None:
            return False
        setattr(self, ctx[1], True)
        return True

    def _enter_inline_concat_element(self) -> bool:
        """
        Begin an inline element that opens its OWN block/argument (emphasis,
        strong, reference) and may be a direct sibling in a code-mode concat
        context.

        Emit the ``" + "`` separator when this element follows an earlier
        sibling, then SUPPRESS the outer concat context for the duration of the
        element's own content: inside the element the children are a fresh
        context (markup content for emph/strong, the link body for a
        reference), where re-applying the outer ``+`` would leak a stray
        operator, e.g. ``strong({ + text(...)})``. Always pushes onto
        ``_inline_concat_stack`` so it pairs 1:1 with
        :meth:`_exit_inline_concat_element` in the matching ``depart_*``.

        Returns ``True`` when a concat context was active (so the caller skips
        the list-item newline separator), ``False`` otherwise.
        """
        ctx = self._inline_concat_context()
        self._inline_concat_stack.append(ctx)
        if ctx is None:
            return False
        if getattr(self, ctx[1]):
            self.add_text(" + ")
        # Suppress the outer concat context inside this element's own content.
        setattr(self, ctx[0], False)
        return True

    def _exit_inline_concat_element(self) -> None:
        """
        Close an inline element opened by :meth:`_enter_inline_concat_element`:
        restore the suppressed outer concat context and record that this
        element is now a sibling expression, so the NEXT sibling is ``" + "``
        separated.
        """
        ctx = self._inline_concat_stack.pop()
        if ctx is None:
            return
        setattr(self, ctx[0], True)  # un-suppress the outer context flag
        setattr(self, ctx[1], True)  # this element = a sibling for the next one

    # ------------------------------------------------------------------
    # Signature typography helpers (Phase 37, SIG-01..SIG-07,
    # 37-EMISSION-CONTRACT.md sections 4-5). Shared by visit_Text's
    # in_signature_text branch, visit_desc_name/visit_desc_annotation's
    # text-only-leaf bold branch, and visit_desc_sig_name's D-05
    # discriminator -- ONE place each algorithm lives, per D-04's "no
    # second escaping helper" constraint.
    # ------------------------------------------------------------------

    def _escape_signature_text(self, text: str) -> str:
        """
        Escape a signature text run and inject the SIG-07/D-07
        break-opportunity escape, in the load-bearing order contract
        section 4 steps 2-3 specify: escape FIRST via the shared,
        unmodified ``escape_typst_string`` helper (D-04 -- no second
        escaping helper is written), THEN inject the break-opportunity
        escape after every period.

        Order is load-bearing: ``escape_typst_string`` doubles
        backslashes, so injecting the escape sequence before escaping
        would double ITS backslash too, emitting a literal two-character
        ``\\\\u{200B}`` instead of the intended Unicode escape sequence.
        ``.`` is neither produced nor consumed by ``escape_typst_string``,
        so injecting after escaping is safe in the other direction.

        The injected token is the 8-character Typst Unicode escape
        ``\\u{200B}`` -- NOT a literal invisible U+200B byte -- so the
        emitted ``.typ`` stays greppable, diffable and hand-derivable in
        a golden file. Injection is blanket over every period in the run
        (no length threshold, mirroring ``visit_literal``'s existing
        unconditional in-table injection) -- D-07 requires the break
        opportunity in every long dotted name, and routing every call
        site through this one helper is what guarantees no dotted-name
        carrying node type can be missed.
        """
        escaped = escape_typst_string(text)
        return escaped.replace(".", ".\\u{200B}")

    def _emit_signature_leaf_wrapper(self, node: nodes.Element, wrapper: str) -> None:
        """
        Emit a complete ``wrapper(raw("..."))`` call for a text-only-leaf
        signature node (a ``desc_name`` / ``desc_annotation`` whose every
        child is ``nodes.Text``, or a leaf ``desc_sig_name``), then raise
        ``nodes.SkipNode`` -- mirroring ``visit_literal``'s leaf-emission
        shape (``typsphinx/translator.py:1289-1367``): the paragraph
        separator, the concat-separator-or-list-item-newline fallback,
        the call itself (escaped + break-opportunity-injected via
        :meth:`_escape_signature_text`), then the mark-content-or-list-
        item-separator fallback.

        ``wrapper`` is ``"strong"`` (contract section 5.1's leaf branch /
        section 5.2 rule 1) or ``"emph"`` (section 5.2 rule 2) -- the
        two treatments SIG-01/SIG-04 require, sharing everything except
        the wrapper call name.
        """
        self._add_paragraph_separator()
        if not self._emit_inline_concat_separator():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        escaped = self._escape_signature_text(node.astext())
        prefix = "#" if self._in_markup_mode else ""
        self.add_text(f'{prefix}{wrapper}(raw("{escaped}"))')

        if not self._mark_inline_concat_content():
            if self.in_list_item:
                self.list_item_needs_separator = True

        raise nodes.SkipNode

    def visit_Text(self, node: nodes.Text) -> None:
        """
        Visit a text node.

        Wraps text in text() function for unified code mode.
        Uses string escaping (not markup escaping).

        Exception: Inside literal blocks, text is output directly
        without text() wrapping to preserve code content.

        Args:
            node: The text node
        """
        text_content = node.astext()

        # Inside literal blocks, output text directly (no wrapping)
        if self.in_literal_block:
            self.add_text(text_content)
            return

        # SIG-01..SIG-05 (37-EMISSION-CONTRACT.md section 4): inside a
        # desc_signature, every text-bearing descendant routes through the
        # monospace primitive raw(...) instead of the proportional text(...)
        # primitive -- this is what makes desc_addname, desc_sig_keyword,
        # desc_sig_space, desc_sig_punctuation, desc_sig_operator,
        # inline.default_value, desc_sig_literal_string/number and the
        # C/C++-only desc_sig_keyword_type get monospace "for free" with no
        # dedicated per-node handler (contract section 4.3). Unlike
        # in_literal_block above, this branch is NOT a bare unescaped
        # emission -- it still escapes and still participates in every
        # separator protocol (paragraph/concat/list-item), because
        # signature text is still prose-adjacent content, just typeset in
        # monospace. Do not collapse this into the in_literal_block shape.
        if self.in_signature_text:
            # Same FID-11 soft-wrap collapse as the plain-text path below.
            sig_text_content = text_content.replace("\n", " ")
            # Escape + inject the break-opportunity escape via the shared
            # helper (see its docstring for the load-bearing order
            # rationale) -- the SAME algorithm every signature leaf-
            # emission site (this branch, visit_desc_name/
            # visit_desc_annotation's bold leaf branch,
            # visit_desc_sig_name's bold/italic leaf branches) reuses, so
            # there is exactly one place the escape+ZWSP algorithm lives.
            sig_text_content = self._escape_signature_text(sig_text_content)

            self._add_paragraph_separator()
            if not self._emit_inline_concat_separator():
                if self.in_list_item and self.list_item_needs_separator:
                    self.add_text("\n")

            sig_prefix = "#" if self._in_markup_mode else ""
            self.add_text(f'{sig_prefix}raw("{sig_text_content}")')

            if not self._mark_inline_concat_content():
                if self.in_list_item:
                    self.list_item_needs_separator = True
            return

        # FID-11: a paragraph authored with reST soft/semantic source line
        # breaks and no inline markup at the wrap point is merged by
        # docutils into a SINGLE Text node carrying a literal '\n' where the
        # source line wrapped. escape_typst_string would otherwise turn that
        # embedded '\n' into the two-char "\n" escape inside the emitted
        # text("...") string, which Typst decodes back into a literal
        # control character -- forcing a HARD line break in the rendered
        # paragraph instead of the single-space reflow HTML/print
        # conventionally use for a soft wrap. Collapse to a single space
        # here, strictly BEFORE escaping (D-Disc-1, Pattern 2), so this does
        # not bypass or weaken escape_typst_string's own escaping. The
        # guard set is safe: in_literal_block already early-returned above;
        # line_block/line content uses a structural linebreak() via
        # depart_line, never an embedded '\n' in a line's own Text child;
        # inline raw()/literal content never routes through visit_Text at
        # all (visit_literal escapes node.astext() directly).
        text_content = text_content.replace("\n", " ")

        # Escape string content via the shared helper (order-safe, full set)
        text_content = escape_typst_string(text_content)

        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Add separator before text.
        # In a code-mode concat context (def-list term / link body / desc
        # parameter): use the + operator between adjacent inline expressions.
        # In list items: use a newline separator. In paragraphs: handled by
        # _add_paragraph_separator above.
        if not self._emit_inline_concat_separator():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Wrap in text() function (# prefix needed in markup mode)
        self.add_text(f'{prefix}text("{text_content}")')

        # Mark that content was added (so the next sibling is + / newline
        # separated).
        if not self._mark_inline_concat_content():
            if self.in_list_item:
                self.list_item_needs_separator = True

    def depart_Text(self, node: nodes.Text) -> None:
        """
        Depart a text node.

        Args:
            node: The text node
        """
        # Text nodes don't need closing
        pass

    def visit_emphasis(self, node: nodes.emphasis) -> None:
        """
        Visit an emphasis (italic) node.

        Generates emph() function call. Child text nodes will be
        wrapped in text() automatically.

        Args:
            node: The emphasis node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # If this emphasis is a sibling in a code-mode concat context (def-list
        # term / link body / desc parameter), + separate it and suppress that
        # context for the emph body (content mode, where an outer '+' would
        # leak). Otherwise fall back to the list-item newline separator.
        if not self._enter_inline_concat_element():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Save and reset list item separator for children (they're inside this element)
        was_list_item_needs_separator = self.list_item_needs_separator

        # Since emph({}) uses content block, treat it like list_item
        # Children need newline separators, not + operators
        was_in_list_item = self.in_list_item
        self.in_list_item = True
        self.list_item_needs_separator = False

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Use emph({}) function with content block
        self.add_text(f"{prefix}emph({{")

        # Store state to restore in depart
        self._emph_was_in_paragraph = was_in_paragraph
        self._emph_was_in_list_item = was_in_list_item
        self._emph_was_list_item_needs_separator = was_list_item_needs_separator

    def depart_emphasis(self, node: nodes.emphasis) -> None:
        """
        Depart an emphasis (italic) node.

        Closes emph({}) function call.

        Args:
            node: The emphasis node
        """
        # Close emph({}) function
        self.add_text("})")

        # Restore paragraph state
        if hasattr(self, "_emph_was_in_paragraph"):
            self.in_paragraph = self._emph_was_in_paragraph
            delattr(self, "_emph_was_in_paragraph")

        # Restore in_list_item state
        if hasattr(self, "_emph_was_in_list_item"):
            self.in_list_item = self._emph_was_in_list_item
            delattr(self, "_emph_was_in_list_item")

        # Restore and mark that next element needs separator
        if hasattr(self, "_emph_was_list_item_needs_separator"):
            # Restore previous state, then mark next element needs separator
            if self.in_list_item:
                self.list_item_needs_separator = True
            delattr(self, "_emph_was_list_item_needs_separator")

        # Restore the code-mode concat context suppressed for the emph body and
        # mark this emphasis as a sibling so the next term/link/desc expression
        # is + separated.
        self._exit_inline_concat_element()

    def visit_manpage(self, node: addnodes.manpage) -> None:
        """
        Visit a manpage node (:manpage: role).

        Renders the literal page-reference text (e.g. "ls(1)") italic,
        Sphinx-HTML-faithful (D-02), by delegating to visit_emphasis so the
        paragraph-separator / list-item / inline-concat-context /
        _in_markup_mode state machine is reused verbatim -- a manpage node
        duck-types fine since visit_emphasis performs no isinstance check on
        its argument, only reading self.* state (16-RESEARCH.md Pattern 2).

        No linkification per D-02a: with manpages_url unset, the node's
        single child stays a plain nodes.Text -- a reference child cannot
        occur in this configuration, so no link() is ever fabricated.

        Args:
            node: The manpage node
        """
        self.visit_emphasis(node)

    def depart_manpage(self, node: addnodes.manpage) -> None:
        """
        Depart a manpage node.

        Delegates to depart_emphasis (see visit_manpage).

        Args:
            node: The manpage node
        """
        self.depart_emphasis(node)

    def visit_strong(self, node: nodes.strong) -> None:
        """
        Visit a strong (bold) node.

        Generates strong() function call. Child text nodes will be
        wrapped in text() automatically.

        Args:
            node: The strong node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # If this strong is a sibling in a code-mode concat context (def-list
        # term / link body / desc parameter), + separate it and suppress that
        # context for the strong body (content mode, where an outer '+' would
        # leak). Otherwise fall back to the list-item newline separator.
        if not self._enter_inline_concat_element():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Save and reset list item separator for children (they're inside this element)
        was_list_item_needs_separator = self.list_item_needs_separator

        # Since strong({}) uses content block, treat it like list_item
        # Children need newline separators, not + operators
        was_in_list_item = self.in_list_item
        self.in_list_item = True
        self.list_item_needs_separator = False

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Use strong({}) function with content block
        self.add_text(f"{prefix}strong({{")

        # Store state to restore in depart
        self._strong_was_in_paragraph = was_in_paragraph
        self._strong_was_in_list_item = was_in_list_item
        self._strong_was_list_item_needs_separator = was_list_item_needs_separator

    def depart_strong(self, node: nodes.strong) -> None:
        """
        Depart a strong (bold) node.

        Closes strong({}) function call.

        Args:
            node: The strong node
        """
        # Close strong({}) function
        self.add_text("})")

        # Restore paragraph state
        if hasattr(self, "_strong_was_in_paragraph"):
            self.in_paragraph = self._strong_was_in_paragraph
            delattr(self, "_strong_was_in_paragraph")

        # Restore in_list_item state
        if hasattr(self, "_strong_was_in_list_item"):
            self.in_list_item = self._strong_was_in_list_item
            delattr(self, "_strong_was_in_list_item")

        # Restore and mark that next element needs separator
        if hasattr(self, "_strong_was_list_item_needs_separator"):
            # Restore previous state, then mark next element needs separator
            if self.in_list_item:
                self.list_item_needs_separator = True
            delattr(self, "_strong_was_list_item_needs_separator")

        # Restore the code-mode concat context suppressed for the strong body
        # and mark this strong as a sibling so the next term/link/desc
        # expression is + separated.
        self._exit_inline_concat_element()

    def visit_literal(self, node: nodes.literal) -> None:
        """
        Visit a literal (inline code) node.

        Generates raw() function call with backtick raw string.
        Uses backticks to avoid escaping issues.

        Args:
            node: The literal node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Add separator before the raw() expression.
        # In a code-mode concat context (def-list term / link body / desc
        # parameter), adjacent inline expressions must be + concatenated
        # (except the first); otherwise a list item uses a newline separator.
        # Shared with visit_Text via the concat helpers (single source of
        # truth), so a raw() that is a term/link/desc sibling is + separated.
        if not self._emit_inline_concat_separator():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        # Get code content directly
        code_content = node.astext()

        if self.in_table:
            # Zero-width space (U+200B) at natural break points so Typst's
            # line-breaker can wrap long unbroken dotted/underscored
            # identifiers inside a narrow fr-column table cell -- fr
            # columns alone do not wrap a single unbroken token (FID-01a
            # "Critical Finding", 18-RESEARCH.md). Gated on self.in_table
            # so prose/code-block literals stay byte-unchanged (F6 out of
            # scope). Inserted BEFORE escape_typst_string() -- U+200B is
            # not a character that helper treats specially.
            zwsp = chr(0x200B)  # zero-width space
            code_content = code_content.replace(".", "." + zwsp).replace(
                "_", "_" + zwsp
            )
        elif code_content and code_content[0] in ":;,)]}!?":
            # FID-10: a long run of colon-leading inline literal role tokens
            # (e.g. ``:cpp:any:`` ``:cpp:class:`` ...) overflows the page's
            # right margin instead of wrapping at the space between tokens.
            # Typst's line-breaker honors Unicode UAX14 rule LB13 ("do not
            # break before class CL/CP/EX/IS/SY, even after a space") for a
            # token starting with one of these no-break-before characters --
            # suppressing the break opportunity that would otherwise exist
            # right before the token, even though the preceding text(" ")
            # is real, breakable content (21-RESEARCH.md Pattern 1 /
            # Pitfall 1). A leading zero-width space gives the line-breaker
            # an explicit break opportunity at the token boundary without
            # touching a single visible glyph (D-04 -- boundary-only, never
            # break inside a token). Gated to this narrow character class so
            # the many existing exact-match raw("...") assertions elsewhere
            # (none of which start a literal with one of these characters)
            # stay byte-unchanged (Pitfall 1 / Assumption A1). This is a
            # NEW, independent elif sibling -- the self.in_table primitive
            # above stays completely isolated (D-05).
            zwsp = chr(0x200B)  # zero-width space
            code_content = zwsp + code_content

        # Escape code content for string parameter via the shared helper.
        # Must escape newline/CR/tab too (not just backslash+quote): an inline
        # literal whose source wraps across lines carries an embedded newline,
        # which would otherwise break the single-line Typst "..." string literal
        # ("expected semicolon or line break").
        escaped_code = escape_typst_string(code_content)

        # Generate raw() function with string parameter (no # prefix in code mode)
        # Using string instead of backtick raw literal for compatibility with + operator
        self.add_text(f'raw("{escaped_code}")')

        # Mark that content was added / next element needs a separator
        if not self._mark_inline_concat_content():
            if self.in_list_item:
                self.list_item_needs_separator = True

        # Skip processing child text nodes (we already got the content)
        raise nodes.SkipNode

    def depart_literal(self, node: nodes.literal) -> None:
        """
        Depart a literal (inline code) node.

        This is not called when SkipNode is raised in visit_literal.

        Args:
            node: The literal node
        """
        pass

    def visit_subscript(self, node: nodes.subscript) -> None:
        """
        Visit a subscript node.

        Generates sub() function call. Child text nodes will be
        wrapped in text() automatically.

        Args:
            node: The subscript node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Use sub() function (no # prefix in code mode)
        self.add_text("sub(")

        # Store state to restore in depart
        self._subscript_was_in_paragraph = was_in_paragraph

    def depart_subscript(self, node: nodes.subscript) -> None:
        """
        Depart a subscript node.

        Closes sub() function call.

        Args:
            node: The subscript node
        """
        # Close sub() function
        self.add_text(")")

        # Restore paragraph state
        if hasattr(self, "_subscript_was_in_paragraph"):
            self.in_paragraph = self._subscript_was_in_paragraph
            delattr(self, "_subscript_was_in_paragraph")

    def visit_superscript(self, node: nodes.superscript) -> None:
        """
        Visit a superscript node.

        Generates super() function call. Child text nodes will be
        wrapped in text() automatically.

        Args:
            node: The superscript node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Use super() function (no # prefix in code mode)
        self.add_text("super(")

        # Store state to restore in depart
        self._superscript_was_in_paragraph = was_in_paragraph

    def depart_superscript(self, node: nodes.superscript) -> None:
        """
        Depart a superscript node.

        Closes super() function call.

        Args:
            node: The superscript node
        """
        # Close super() function
        self.add_text(")")

        # Restore paragraph state
        if hasattr(self, "_superscript_was_in_paragraph"):
            self.in_paragraph = self._superscript_was_in_paragraph
            delattr(self, "_superscript_was_in_paragraph")

    def visit_bullet_list(self, node: nodes.bullet_list) -> None:
        """
        Visit a bullet list node.

        Outputs list( and prepares for stream-based item rendering.

        Args:
            node: The bullet list node
        """
        # A propagated explicit target can land its id on this list; anchor it
        # so a same-document link(<id>, ...) resolves (no ids -> no-op).
        self._emit_id_anchors(node)

        # Add + separator if nested in a list item
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        self.list_stack.append("bullet")
        self.add_text("list(")

        # Save parent list state and start fresh for nested list
        if len(self.list_stack) > 1:  # Nested list
            self._saved_is_first_list_item = self.is_first_list_item
            self._saved_list_item_needs_separator = self.list_item_needs_separator

        self.is_first_list_item = True

        # Mark that next element in parent list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

    def depart_bullet_list(self, node: nodes.bullet_list) -> None:
        """
        Depart a bullet list node.

        Closes the list() function.

        Args:
            node: The bullet list node
        """
        self.list_stack.pop()
        self.add_text(")")

        # Restore parent list state if nested
        if hasattr(self, "_saved_is_first_list_item"):
            self.is_first_list_item = self._saved_is_first_list_item
            delattr(self, "_saved_is_first_list_item")
        if hasattr(self, "_saved_list_item_needs_separator"):
            self.list_item_needs_separator = self._saved_list_item_needs_separator
            delattr(self, "_saved_list_item_needs_separator")

        # Add newlines only if this is a top-level list
        if not self.list_stack:
            self.add_text("\n\n")

    def visit_enumerated_list(self, node: nodes.enumerated_list) -> None:
        """
        Visit an enumerated (numbered) list node.

        Outputs enum( and prepares for stream-based item rendering.

        Args:
            node: The enumerated list node
        """
        # A propagated explicit target can land its id on this list; anchor it
        # so a same-document link(<id>, ...) resolves (no ids -> no-op).
        self._emit_id_anchors(node)

        # Add + separator if nested in a list item
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        self.list_stack.append("enumerated")
        self.add_text("enum(")

        # Save parent list state and start fresh for nested list
        if len(self.list_stack) > 1:  # Nested list
            self._saved_is_first_list_item = self.is_first_list_item
            self._saved_list_item_needs_separator = self.list_item_needs_separator

        self.is_first_list_item = True

        # Mark that next element in parent list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

    def depart_enumerated_list(self, node: nodes.enumerated_list) -> None:
        """
        Depart an enumerated (numbered) list node.

        Closes the enum() function.

        Args:
            node: The enumerated list node
        """
        self.list_stack.pop()
        self.add_text(")")

        # Restore parent list state if nested
        if hasattr(self, "_saved_is_first_list_item"):
            self.is_first_list_item = self._saved_is_first_list_item
            delattr(self, "_saved_is_first_list_item")
        if hasattr(self, "_saved_list_item_needs_separator"):
            self.list_item_needs_separator = self._saved_list_item_needs_separator
            delattr(self, "_saved_list_item_needs_separator")

        # Add newlines only if this is a top-level list
        if not self.list_stack:
            self.add_text("\n\n")

    def visit_list_item(self, node: nodes.list_item) -> None:
        """
        Visit a list item node.

        Adds comma separator if not first item, then prepares for item content.

        Args:
            node: The list item node
        """
        # Mark that we're in a list item (disable par() wrapping).
        # Push the prior value so a nested list's depart_list_item restores
        # the OUTER item's context instead of clobbering it to False.
        self._list_item_stack.append(self.in_list_item)
        self.in_list_item = True

        # Add comma before 2nd+ items
        if not self.is_first_list_item:
            self.add_text(", ")
        self.is_first_list_item = False

        # Wrap list item content in { } block
        # This allows multiple statements without + operator
        self.add_text("{\n")

        # Reset separator flag for item content
        self.list_item_needs_separator = False

        # A propagated explicit target (``.. _t:`` placed BETWEEN list items)
        # lands its id on the FOLLOWING list_item node -- not the bullet_list
        # (whose own ids are anchored in visit_bullet_list/visit_enumerated_list)
        # and not the item's inner paragraph. Anchor it here, inside the item's
        # ``{ }`` block, so a same-document link(<id>, ...) resolves. No ids ->
        # no-op; the helper drives the in-list-item separator machinery so the
        # anchor and the item's first content element stay newline-separated.
        self._emit_id_anchors(node)

    def depart_list_item(self, node: nodes.list_item) -> None:
        """
        Depart a list item node.

        Close the { } block wrapper and mark that we're no longer in a list item.

        Args:
            node: The list item node
        """
        # Close the { } block
        self.add_text("\n}")

        # Restore the prior context: after a nested list item closes we are
        # still inside the OUTER list item (True), while a top-level item
        # restores to False. This keeps the existing list_item_needs_separator
        # machinery driving newline separators for any block that follows a
        # nested list (list->par, list->list, ...), fixing the `})par(` class.
        if self._list_item_stack:
            self.in_list_item = self._list_item_stack.pop()
        else:
            self.in_list_item = False

    def visit_literal_block(self, node: nodes.literal_block) -> None:
        """
        Visit a literal block (code block) node.

        Implements Task 4.2.2: codly forced usage, with codly(highlights: ...)
        for :emphasize-lines: (codly 1.3.0 has no codly-range(highlight: ...) API)
        Design 3.5: All code blocks use codly; highlighted lines use codly(highlights: ...)
        Requirements 7.3, 7.4: Support line numbers and highlighted lines
        Issue #20: Support :linenos:, :caption:, and :name: options
        Issue #31: Support :lineno-start: and :dedent: options

        Args:
            node: The literal block node
        """
        # Anchor node["ids"] via the shared markup-block helper. Both a
        # ``:name:`` and a propagated ``.. _t:`` before the block set
        # node["ids"] (and names) on the literal_block; the reference side
        # resolves to the sanitized ID, so anchoring ids -- not names -- is
        # what a link(<id>, ...) needs. This REPLACES the old
        # depart_literal_block ` <label>` postfix (removed below): a bare
        # ` <label>` after a code-mode raw block does not join ("cannot join
        # content with label"), and it anchored the NAME, which diverges from
        # the id whenever the name contains characters docutils rewrites (e.g.
        # a space). Captioned ``:name:`` blocks carry the id on the outer
        # literal-block-wrapper CONTAINER (handled in visit_container), so the
        # inner literal_block has no ids there -> no-op, no double-define. A
        # plain code block has no ids -> no-op, byte-unchanged.
        self._emit_id_anchors(node)

        # Add newline separator if in list item and not first element
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Mark that we're in a literal block (disable text() wrapping)
        self.in_literal_block = True

        # Issue #20: Handle captioned code blocks
        # If we're in a captioned code block (literal-block-wrapper container),
        # wrap the code block in figure() (no # prefix in code mode)
        if self.in_captioned_code_block and self.code_block_caption:
            # Escape special characters in caption
            escaped_caption = self.code_block_caption
            # Start figure with caption (will add closing bracket in depart)
            # No # prefix in code mode
            self.add_text(f"figure(caption: [{escaped_caption}])[\n")

        # If in list item, wrap codly() calls and code block in { } to make
        # it an expression. FID-12: when this list-item wrapper is ALSO
        # opened immediately inside a captioned figure's markup-mode [...]
        # content (see the `figure(caption: [...])[` block above), a bare
        # '{' is parsed as LITERAL TEXT in Typst markup mode -- it does NOT
        # re-enter code mode, and the per-block codly config call that
        # follows leaks as visible prose instead of executing. Only '#{'
        # re-enters code mode from markup mode. When NOT captioned, we are
        # already in a CODE-mode context (top level, admonition, table
        # cell, or the enum()/list argument position), so the wrapper stays
        # bare, byte-unchanged from before.
        if self.in_list_item:
            wrapper_prefix = (
                "#"
                if (self.in_captioned_code_block and self.code_block_caption)
                else ""
            )
            self.add_text(f"{wrapper_prefix}{{\n")

        # Per-block codly config (number-format / offset / codly-range) is a
        # code-mode FUNCTION CALL, and whether it needs a leading `#` depends
        # on the surrounding Typst mode:
        #   * Document top level, admonitions (info({...})), list items and
        #     table cells all place the block in a CODE-mode `{ }` context,
        #     where a bare `codly(...)` executes -- emit it bare.
        #   * A CAPTIONED code block opens a MARKUP content block above
        #     (`figure(caption: [...])[`), where a bare `codly(...)` is typeset
        #     as LITERAL PROSE -- leaking the config text and, for codly-range,
        #     never applying the highlight (the corpus bug). There it must
        #     carry a leading `#` so Typst executes it.
        # The one exception is a captioned code block that is ALSO in a list
        # item: the `{ }` wrapper emitted just above re-enters code mode inside
        # the figure's `[...]`, so it is bare again. Hence: markup (needs `#`)
        # iff captioned AND not in a list-item `{ }` wrapper. Same markup/
        # code-mode confusion class as Phase-15 bug #15 (block_quote).
        in_markup_context = (
            self.in_captioned_code_block
            and self.code_block_caption
            and not self.in_list_item
        )
        codly_prefix = "#" if in_markup_context else ""

        # Check for :linenos: option (Issue #20)
        # If linenos is not set or False, disable line numbers in codly
        linenos = node.get("linenos", False)
        if not linenos:
            self.add_text(f"{codly_prefix}codly(number-format: none)\n")

        # Extract highlight_args if present (Task 4.2.2)
        highlight_args = node.get("highlight_args", {})
        hl_lines = highlight_args.get("hl_lines", [])

        # Issue #31: Support :lineno-start: option
        # Sphinx stores lineno-start in highlight_args['linenostart']. Note
        # that Sphinx's LiteralInclude directive ALWAYS populates
        # linenostart (defaulting to 1) even without an explicit
        # :lineno-start: option (see LiteralIncludeReader.__init__), so the
        # `!= 1` guard below is required to avoid a spurious codly() call
        # for the common "plain :linenos:" case.
        #
        # codly's @preview 1.3.0 codly() function has no `start` parameter
        # -- it accepts `offset` (int), an ADDITIVE delta applied as
        # `line.number + offset` where `line.number` is the raw block's
        # 1-indexed line number (see codly/1.3.0/src/lib.typ). To make the
        # first displayed line number equal Sphinx's `linenostart`, the
        # offset must be `linenostart - 1` (offset=0 is codly's default,
        # matching linenostart=1).
        lineno_start = highlight_args.get("linenostart")
        if linenos and lineno_start is not None and lineno_start != 1:
            self.add_text(f"{codly_prefix}codly(offset: {lineno_start - 1})\n")

        # Highlight the Sphinx :emphasize-lines: lines. codly 1.3.0 has NO
        # `codly-range(highlight: ...)` API -- codly-range(start, end) DISPLAYS
        # a line range and requires a positional `start`, so the old
        # `codly-range(highlight: (...))` call was invalid Typst that aborted
        # the compile with "missing argument: start" the moment it executed. It
        # only ever appeared to "work" in a markup context, where it leaked as
        # un-executed literal prose (never highlighting anything). The correct
        # per-line-highlight API is
        #   codly(highlights: ((line: N, start: 1, end: none, fill: <color>), ...))
        # -- start: 1 (column 1) + end: none (rest of the line) highlights the
        # whole emphasized line. codly clears `highlights` after each raw block,
        # so this is scoped to this block only (no bleed into later blocks).
        if hl_lines:
            highlight_entries = ", ".join(
                f"(line: {line}, start: 1, end: none, fill: yellow)"
                for line in hl_lines
            )
            # Trailing comma keeps a single-entry highlights tuple a valid array.
            self.add_text(f"{codly_prefix}codly(highlights: ({highlight_entries},))\n")

        # Typst code block syntax: ```language\ncode\n```
        # Extract language if specified
        language = node.get("language", "")
        if language:
            self.add_text(f"```{language}\n")
        else:
            self.add_text("```\n")

    def depart_literal_block(self, node: nodes.literal_block) -> None:
        """
        Depart a literal block (code block) node.

        Issue #20: Handle closing figure bracket and labels.

        Args:
            node: The literal block node
        """
        # Clear literal block flag
        self.in_literal_block = False

        # Close code block
        self.add_text("\n```\n")

        # Close the { } wrapper if we're in a list item
        if self.in_list_item:
            self.add_text("}")

        # Issue #20: Close figure wrapper if we're in a captioned code block
        if self.in_captioned_code_block and self.code_block_caption:
            # Close the figure's trailing content block with ]
            self.add_text("]")
            # Add label if present
            if self.code_block_label:
                self.add_text(
                    f" <{self._namespace_label(self._current_docname(), self.code_block_label)}>"
                )
            self.add_text("\n\n")
        else:
            # Normal code block - just add spacing. Any :name:/propagated-target
            # id is anchored by _emit_id_anchors in visit_literal_block (the old
            # ` <label>` postfix here failed to join a code-mode raw block with
            # a label and anchored the name instead of the id).
            self.add_text("\n")

        # Mark that next element in list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_definition_list(self, node: nodes.definition_list) -> None:
        """
        Visit a definition list node.

        Collects all term-definition pairs and generates terms() function
        in unified code mode.

        Args:
            node: The definition list node
        """
        # A propagated explicit target can land its id on this definition list;
        # anchor it so a same-document link(<id>, ...) resolves (no ids ->
        # no-op). Emitted here while self.body is still the real body -- before
        # visit_term/visit_definition redirect it to buffers.
        self._emit_id_anchors(node)

        # A def-list nested in a list item, following a sibling paragraph/block,
        # must be newline-separated from it: its terms(...) is emitted (in
        # depart) directly into the outer list item's code-mode content block,
        # where abutting the preceding statement (e.g. text("...")terms(...))
        # is a Typst syntax error ("expected semicolon or line break", GATE-02
        # fatal #8, configuration.typ:2009). Mirror the standard block-visitor
        # list-item separator (literal_block/bullet_list/...). Emitted here
        # (not depart) while self.body is still the real body -- visit_term/
        # visit_definition redirect self.body to buffers in between.
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
            self.list_item_needs_separator = False
        self.in_definition_list = True
        # Push a fresh item collection for THIS list and alias
        # definition_list_items to it, so a definition list nested inside one of
        # this list's definitions collects into its own frame (bug #18).
        self._deflist_items_stack.append([])
        self.definition_list_items = self._deflist_items_stack[-1]

    def depart_definition_list(self, node: nodes.definition_list) -> None:
        """
        Depart a definition list node.

        Generates terms() function with all collected term-definition pairs.

        Args:
            node: The definition list node
        """
        # Pop THIS list's item collection and restore the enclosing list's
        # frame (or reset to empty at the top level). in_definition_list stays
        # True while an enclosing definition list is still open, so a nested
        # list's depart does not prematurely clear the outer state (bug #18).
        items = self._deflist_items_stack.pop()
        if self._deflist_items_stack:
            self.definition_list_items = self._deflist_items_stack[-1]
            self.in_definition_list = True
        else:
            self.definition_list_items = []
            self.in_definition_list = False

        # Generate terms() function with all items (no # prefix in code mode).
        # The DEFINITION (2nd arg) is wrapped in a `{ ... }` content block: a
        # definition may hold several block-level children (a paragraph, then a
        # code fence, then a list), which depart_definition assembles as bare,
        # blank-line-separated statements. Blank-line separation of sequential
        # content is valid only at document top level; as a bare function
        # argument Typst reads the first statement (e.g. par({...})) as the
        # WHOLE argument and then expects a comma at the next statement
        # (codly(...)/a fence/list({...})) -> "expected comma" (GATE-02 fatal
        # #7, directives.typ:1718 + ~16 corpus files). Inside `{ }` Typst
        # auto-joins the statements into one content value -- a valid single
        # argument. The TERM (1st arg) keeps its own +-concat assembly (D-03/
        # bug #3/#5) untouched; we wrap only the definition arg.
        # FID-05: terms()'s built-in `separator` parameter defaults to a WEAK
        # h(0.6em) horizontal space, not a line break -- when a definition's
        # first content is bare inline (e.g. nested in a list_item, where
        # visit_paragraph early-returns per FID-02, or when the definition
        # opens with a nested list/field-list whose own first content is also
        # inline), nothing forces a break and the term flows onto the same
        # line as its definition. Setting separator: linebreak() unconditionally
        # fixes both sub-cases and is a no-op-visual-change for the
        # already-correct par()-wrapped case (a block cannot share a line with
        # preceding inline flow regardless of the separator). This is a
        # terms()-call-PARAMETER change -- NOT routed through the shared
        # _emit_forced_break helper (Pitfall 3): the bug is a Typst-layout
        # default, not a missing statement-boundary.
        if items:
            items_str = ", ".join(
                f"terms.item({term}, {self._wrap_definition_arg(definition)})"
                for term, definition in items
            )
            self.add_text(f"terms(separator: linebreak(), {items_str})\n\n")
        else:
            self.add_text("terms(separator: linebreak())\n\n")

        # A following sibling in the same list item must newline-separate from
        # this terms(...) statement.
        if self.in_list_item:
            self.list_item_needs_separator = True

    @staticmethod
    def _is_single_content_block(text: str) -> bool:
        """
        Return True if ``text`` is exactly one balanced ``{ ... }`` content
        block (its opening brace matches the final character), ignoring braces
        inside Typst double-quoted string literals.

        Used by :meth:`_wrap_definition_arg` to avoid double-wrapping a
        definition buffer that is already a single content value. No current
        translator emission produces such a buffer (definition children all
        start with a function name or a backtick fence), so this is a defensive
        guard, but it keeps the wrap idempotent.

        Args:
            text: The assembled definition buffer.

        Returns:
            True if ``text`` is a single ``{...}`` content block.
        """
        if len(text) < 2 or text[0] != "{" or text[-1] != "}":
            return False
        depth = 0
        in_string = False
        escaped = False
        for i, ch in enumerate(text):
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                # A close returning to depth 0 before the last char means the
                # buffer holds more than one top-level block -> must wrap.
                if depth == 0 and i != len(text) - 1:
                    return False
        return depth == 0

    def _wrap_definition_arg(self, definition: str) -> str:
        """
        Wrap a definition buffer so it is a single valid ``terms.item`` 2nd
        argument.

        A definition with multiple block-level children is assembled as bare,
        blank-line-separated statements, which are only valid at document top
        level. Enclosing them in a ``{ ... }`` content block makes Typst
        auto-join them into one content value. A single-block definition (a
        lone ``par({...})``) wraps to ``{par({...})}`` and renders identically.
        An empty definition becomes ``{}`` (valid empty content). Already
        single-``{...}`` buffers are returned unchanged to avoid double-wrapping.

        Args:
            definition: The assembled definition buffer.

        Returns:
            The definition as a single ``{ ... }``-wrapped argument.
        """
        if not definition:
            return "{}"
        if self._is_single_content_block(definition):
            return definition
        return f"{{{definition}}}"

    def visit_definition_list_item(self, node: nodes.definition_list_item) -> None:
        """
        Visit a definition list item node.

        Args:
            node: The definition list item node
        """
        # Definition list items don't need special markup
        pass

    def depart_definition_list_item(self, node: nodes.definition_list_item) -> None:
        """
        Depart a definition list item node.

        Args:
            node: The definition list item node
        """
        # Definition list items don't need closing
        pass

    def visit_term(self, node: nodes.term) -> None:
        """
        Visit a term (definition list term) node.

        Starts buffering term content.

        Args:
            node: The term node
        """
        # Start buffering term content. Push the current body onto the stack
        # (not a single saved_body slot) so a definition list nested inside this
        # list's definition restores its own level without orphaning this one
        # (bug #18).
        self._saved_body_stack.append(self.body)
        self.current_term_buffer = []
        self.body = self.current_term_buffer

        # Enter term concat context: adjacent inline expressions in the buffer
        # are + concatenated (the buffer becomes the code-mode 1st arg of
        # terms.item, where juxtaposition is a Typst syntax error).
        self._in_term = True
        self._term_has_content = False

    def depart_term(self, node: nodes.term) -> None:
        """
        Depart a term (definition list term) node.

        Saves buffered term content. If the term carries a docutils-assigned
        id (e.g. a `.. glossary::` entry), emits a Typst `<label>` anchor via
        the bracket-wrap markup form so a same-document `:term:` reference's
        `link(<term-id>, ...)` (visit_reference's refid branch, D-03) has a
        resolvable target instead of aborting the compile with "label does
        not exist" (XREF-01, D-04). Mirrors the visit_title/depart_title
        bracket-wrap anchor pattern (Phase 11) -- never `+`-join a bare
        `label(...)` onto content, which raises `TypstError: cannot add
        content and label`.

        Args:
            node: The term node
        """
        # Exit term concat context.
        self._in_term = False
        self._term_has_content = False

        # Get buffered term content
        if isinstance(self.current_term_buffer, list):
            term_content = "".join(self.current_term_buffer).strip()
        else:
            term_content = ""

        # Restore the body saved on entry (stack pop, not single slot).
        self.body = self._saved_body_stack.pop()

        if node.get("ids"):
            label_id = self._namespace_label(self._current_docname(), node["ids"][0])
            term_content = f"[#{{{term_content}}} <{label_id}>]"

        # Store term for later (will be paired with definition)
        self.current_term_buffer = term_content

    def visit_definition(self, node: nodes.definition) -> None:
        """
        Visit a definition (definition list definition) node.

        Starts buffering definition content.

        Args:
            node: The definition node
        """
        # Start buffering definition content. Push the current body AND capture
        # the pending term string: a definition list nested inside this
        # definition would otherwise overwrite the single saved_body /
        # current_term_buffer slots, dropping THIS definition's content and its
        # term when it departs (bug #18). The term was set to a str by
        # depart_term; anything else means no term to pair.
        self._saved_body_stack.append(self.body)
        self._pending_term_stack.append(
            self.current_term_buffer
            if isinstance(self.current_term_buffer, str)
            else None
        )
        self.current_definition_buffer = []
        self.body = self.current_definition_buffer

    def depart_definition(self, node: nodes.definition) -> None:
        """
        Depart a definition (definition list definition) node.

        Saves buffered definition content and pairs it with the term.

        Args:
            node: The definition node
        """
        # Read THIS definition's buffered content from self.body. Balanced
        # nested visit/depart pairs restore self.body to this definition's own
        # buffer, so it holds the full content (leading paragraph + any nested
        # terms(...)); the current_definition_buffer slot may have been
        # reassigned/None'd by a nested definition and can no longer be trusted
        # (bug #18).
        definition_content = "".join(self.body).strip()

        # Restore the body saved on entry (stack pop, not single slot).
        self.body = self._saved_body_stack.pop()

        # Pair the pending term (captured on entry, before any nested list could
        # clobber current_term_buffer) with this definition's content.
        term = self._pending_term_stack.pop()
        if term is not None:
            self.definition_list_items.append((term, definition_content))

        self.current_term_buffer = None
        self.current_definition_buffer = None

    def visit_figure(self, node: nodes.figure) -> None:
        """
        Visit a figure node.

        Generates figure() function call (no # prefix in code mode), unless
        docutils has assigned the figure an id -- which happens
        automatically whenever a figure carries a caption, for numref/
        cross-reference support, regardless of whether the user gave an
        explicit `:name:` -- in which case the call is bracket-wrapped in
        markup content (`[#figure(...) <label>]`). Typst's `<label>` anchor
        syntax is only valid as a markup-mode postfix; attaching it to a
        bare code-mode statement inside this translator's unified `#{ ... }`
        code-mode document wrapper is a Typst parse error ("expected
        semicolon or line break") that aborts the whole compile -- a real
        fatal bug discovered by Phase 11's GATE-01 real-compile acceptance
        gate (Issue #114), affecting every captioned figure, not just the
        FIG-01/FIG-02 cases that phase otherwise targets.

        Args:
            node: The figure node
        """
        # FIG-01 (Phase 43): self.in_figure already True means an ENCLOSING
        # figure is still open -- this figure node is NESTED inside its
        # legend (docutils' second-and-later-body-block classification).
        # Push a snapshot of the outer figure's in-progress scalar state
        # (see _push_figure_state's docstring for the full set) BEFORE
        # resetting below for the inner figure's own use, or the inner
        # figure's own depart_figure clobbers the outer's caption/width/
        # legend-flag (the FIG-01 defect). Read self.in_figure BEFORE
        # overwriting it, so the push only fires on genuine nesting; the
        # top-level (non-nested) path below is byte-identical to
        # pre-FIG-01 behavior.
        if self.in_figure:
            self._push_figure_state()

        self.in_figure = True
        self.figure_content = []  # Store figure content (image)
        self.figure_caption = ""  # Store caption text

        # Emit a leading newline separator when this figure follows a
        # sibling inside a list item, matching the block-visitor pattern
        # used by visit_table/visit_bullet_list/visit_enumerated_list/
        # _visit_admonition (bug #4). Without this, a figure that is not
        # the first element inside a list item's content block juxtaposes
        # directly against the preceding sibling's emitted expression --
        # e.g. `text("...")block(width: 40%)[#figure(` -- a Typst parse
        # error ("expected semicolon or line break") that aborts the whole
        # compile. This was previously missing here (CR-01), unlike every
        # other block-level visitor in this file.
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
            self.list_item_needs_separator = False

        # LEN-01: :figwidth: is assigned to node["width"] by docutils' Figure
        # directive. Convert here ONLY (depart_figure must not re-convert, or
        # the drop-warning would fire twice, breaking the one-warning-per-
        # occurrence contract). Typst's figure() rejects a direct width:
        # kwarg (verified real-compile failure), so a converted value wraps
        # the WHOLE figure() call in block(width: ...)[...] instead
        # (16-RESEARCH.md Pitfall 3) -- never passed as a figure() argument.
        # The block()'s own trailing [...] markup block hosts the #figure(
        # call for BOTH the ids and no-ids branches (the ids branch's
        # <label> close still lands inside it -- see depart_figure).
        figwidth = node.get("width")
        self._figure_block_width = (
            self._convert_length_to_typst(figwidth) if figwidth else None
        )

        # FIG-01: a legend child means this figure's body is MORE than just
        # the image -- the legend's content must join the image() call as
        # ONE positional body argument, or Typst raises a parse error at the
        # argument boundary (43-RESEARCH.md Pattern 2, Pitfall 4). Checked
        # here (doctree already fully built at visit time, same reliability
        # as visit_table's own captioned pre-check documents), so the `{`
        # opened below is unconditionally closed by depart_legend before
        # this figure's own depart_figure ever runs (docutils' balanced
        # walkabout() guarantees the matching legend child is visited).
        self._figure_has_legend = any(
            isinstance(child, nodes.legend) for child in node.children
        )

        if self._figure_block_width is not None:
            self.add_text(f"block(width: {self._figure_block_width})[#figure(\n")
        elif node.get("ids"):
            self.add_text("[#figure(\n")
        else:
            # Start figure with potential label (no # prefix in code mode)
            self.add_text("figure(\n")

        # Gated on legend presence ONLY -- an unconditional wrap would
        # change the emitted bytes for every existing image-only figure in
        # the corpus, breaking SC#4 byte-invariance (43-RESEARCH.md
        # Pitfall 5/Anti-Patterns). depart_legend emits the matching `}`.
        if self._figure_has_legend:
            self.add_text("{\n")

    def depart_figure(self, node: nodes.figure) -> None:
        """
        Depart a figure node.

        Args:
            node: The figure node
        """
        # Close the figure. The buffered caption holds rendered code-mode
        # output (text(...)/emph(...) calls produced by the buffer-swap in
        # depart_caption), so it must be wrapped in a {...} code block to be
        # evaluated -- not [...] markup, which would print the calls
        # literally instead of evaluating them.
        if self.figure_caption:
            self.add_text(f",\n  caption: {{{self.figure_caption}}}")

        # Add label if figure has ids. The trailing `]` closes the markup
        # bracket opened in visit_figure -- see that method's docstring for
        # why the label must live inside a markup-mode bracket pair. This
        # close is ALREADY correct when the LEN-01 block(width:)[...] wrapper
        # is open too: the block()'s own trailing `[...]` markup block is
        # what the `]` here closes (visit_figure opened exactly one bracket
        # in either case -- see that method).
        if node.get("ids"):
            label = self._namespace_label(self._current_docname(), node["ids"][0])
            self.add_text(f"\n) <{label}>]\n\n")
        elif self._figure_block_width is not None:
            # LEN-01: the no-ids branch normally has no markup bracket to
            # close, but the block(width: ...)[...] wrapper opened one in
            # visit_figure -- close it here.
            self.add_text("\n)]\n\n")
        else:
            self.add_text("\n)\n\n")

        # A captioned figure self-anchors ONLY ids[0] (its own caption/numref
        # id) in the ``) <label>]`` postfix above. A PROPAGATED explicit target
        # (``.. _t:`` before ``.. figure::``) lands a DIFFERENT id in ids[1:]
        # that would otherwise dangle -- anchor the remainder, skipping ids[0]
        # so it is not defined twice. Empty/single-id figures -> no-op.
        self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))

        # FIG-01 (Phase 43): restore the enclosing figure's scalar state
        # when THIS figure was nested inside another figure's legend;
        # otherwise fall through to the pre-FIG-01 unconditional teardown
        # (mirrors depart_table's was_nested branch, plan 43-01). was_nested
        # is read BEFORE popping -- _pop_figure_state() mutates the stack,
        # so "was there an enclosing frame for THIS figure" must be
        # captured first. Unlike depart_table, depart_figure already routes
        # every emission above through self.add_text (which only branches
        # on self.in_table, never self.in_figure -- see add_text), so no
        # routing-destination change is needed here: everything already
        # streamed into self.body in document order regardless of nesting.
        was_nested = bool(self._figure_state_stack)
        self._pop_figure_state()
        if not was_nested:
            self._figure_block_width = None
            self.in_figure = False
            self.figure_content = []
            self.figure_caption = ""

        # Mark that a following sibling in the same list item must be
        # separated (block-visitor pattern, bug #4; mirrors depart_table's
        # trailing block).
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_caption(self, node: nodes.caption) -> None:
        """
        Visit a caption node.

        Handles captions for both figures and code blocks (Issue #20).

        Args:
            node: The caption node
        """
        # For captioned code blocks, caption is already extracted in visit_container
        # We should skip output to avoid duplicate caption text
        if self.in_captioned_code_block:
            raise nodes.SkipNode
        # For figures, buffer-swap the body so the caption's inline children
        # render through the normal visitor chain (preserving emphasis/literal/etc.
        # and routing text through visit_Text's string-literal escaping) instead
        # of being re-derived later via node.astext() (mirrors the admonition-title
        # buffer-swap idiom; see visit_title/depart_title).
        if self.in_figure:
            self._saved_body_for_figure_caption = self.body
            self.body = []
            # A figure caption is a paragraph of inline content that
            # depart_figure renders into a `{...}` code block. Establish the
            # paragraph separator context so adjacent inline expressions
            # (text/emphasis/the reference-with-target markup wrapper/...) are
            # newline-separated via _add_paragraph_separator -- exactly as in a
            # real paragraph, which already renders these correctly. Without
            # it every inline sibling juxtaposes inside the code block
            # (`text(...)[wrapper]text(...)`, `text(...)emph(...)`), a Typst
            # parse error ("expected semicolon or line break"). Save/restore
            # for nesting safety.
            self._caption_was_in_paragraph = self.in_paragraph
            self._caption_was_paragraph_has_content = self.paragraph_has_content
            self.in_paragraph = True
            self.paragraph_has_content = False
        # For figures, start collecting caption text
        self.in_caption = True

    def depart_caption(self, node: nodes.caption) -> None:
        """
        Depart a caption node.

        Args:
            node: The caption node
        """
        # Capture the buffered caption content and restore the main output
        # stream (buffer-swap idiom; never node.astext(), which bypasses the
        # escaping applied by the normal visitor chain and caused the
        # double-emission/juxtaposition fatal bug).
        if self.in_figure:
            self.figure_caption = "".join(self.body)
            if self._saved_body_for_figure_caption is not None:
                self.body = self._saved_body_for_figure_caption
            self._saved_body_for_figure_caption = None
            # Restore the paragraph separator context saved in visit_caption.
            self.in_paragraph = self._caption_was_in_paragraph
            self.paragraph_has_content = self._caption_was_paragraph_has_content
        self.in_caption = False

    def visit_legend(self, node: nodes.legend) -> None:
        """
        Visit a figure's legend node (FIG-01, Phase 43).

        A ``legend`` is docutils' name for a figure's body content beyond
        its first caption paragraph (or, when the figure has no caption at
        all, everything after an empty first-comment placeholder --
        43-GATE-EVIDENCE-03.md). Before this handler existed,
        ``unknown_visit`` fired (warn and continue -- it does NOT skip
        children), so the legend's children streamed unwrapped directly
        after the enclosing figure's ``image(...)`` call, which Typst
        parses as an unwanted second argument -- a hard compile fatal
        (``TypstError: expected comma``/``unexpected argument``,
        43-RESEARCH.md Pitfall 4), not merely a dropped caption.

        ``visit_figure`` has already opened a ``{`` code block (gated on
        ``self._figure_has_legend``) so the legend's content joins the
        image as ONE positional body argument. This handler's only job is
        to establish the SEPARATOR context so the legend's first child
        newline-separates from the preceding ``image(...)`` expression
        instead of juxtaposing against it -- reusing the existing
        in-list-item separator machinery (the same mechanism
        ``visit_paragraph``/``_emit_forced_break`` already use for a
        paragraph inside a real bullet-list item), rather than inventing a
        new one.

        Pushes onto ``self._legend_list_item_stack`` (43-REVIEW.md CR-01)
        rather than saving into flat scalars -- a legend can itself contain
        a NESTED figure whose own legend also visits (a legend-in-legend
        shape), and two flat scalars cannot represent more than one
        nesting level: the inner legend's own save would overwrite the
        outer legend's saved values before the outer ``depart_legend``
        ever restores them. Mirrors ``_list_item_stack``
        (``visit_list_item``/``depart_list_item``, immediately above in
        ``__init__``) and ``_push_figure_state``/``_pop_figure_state``.

        No styling is emitted -- a bare structural pass-through, matching
        Sphinx's own LaTeX writer (43-RESEARCH.md/CONTEXT Deferred Ideas
        fences legend styling out of this phase).

        Args:
            node: The legend node
        """
        self._legend_list_item_stack.append(
            (self.in_list_item, self.list_item_needs_separator)
        )
        self.in_list_item = True
        self.list_item_needs_separator = True

    def depart_legend(self, node: nodes.legend) -> None:
        """
        Depart a figure's legend node (FIG-01, Phase 43; stacked in the
        CR-01 gap closure).

        Emits the closing ``}`` for the body block ``visit_figure`` opened
        (gated on ``self._figure_has_legend``), then pops the
        separator-context values ``visit_legend`` pushed.

        A no-op-safe pop (ASVS V5, mirroring ``depart_list_item``'s and
        ``_pop_figure_state``'s guard): an unbalanced ``depart_legend`` from
        a malformed doctree -- one with no matching prior ``visit_legend``
        -- falls back to ``False``/``False`` instead of raising
        ``IndexError`` out of the translator. Never call
        ``self._legend_list_item_stack.pop()`` or index ``[-1]`` directly.

        Args:
            node: The legend node
        """
        self.add_text("\n}")
        if self._legend_list_item_stack:
            self.in_list_item, self.list_item_needs_separator = (
                self._legend_list_item_stack.pop()
            )
        else:
            self.in_list_item = False
            self.list_item_needs_separator = False

    def visit_footnote(self, node: nodes.footnote) -> None:
        """
        Visit a footnote definition node (D-05).

        Emits nothing at the definition's natural (docutils) location -- the
        body is reached only via the D-01 pre-pass index (visit_document)
        plus the D-02 lazy render performed by visit_footnote_reference at
        the citing site. A defined-but-never-referenced footnote is
        therefore silently dropped (D-09), which is the intended behavior.

        No depart_footnote is defined: SkipNode guarantees it never fires.

        Args:
            node: The footnote definition node
        """
        raise nodes.SkipNode

    def visit_footnote_reference(self, node: nodes.footnote_reference) -> None:
        """
        Visit a footnote_reference node (D-02/D-03/D-04/D-06/D-08).

        The FIRST reference to a given id renders the footnote body lazily
        via the buffer-swap idiom (never node.astext() -- mirrors
        depart_caption above), skipping the footnote node's leading `label`
        child (D-06), and emits the bracket-wrapped, label-attached
        definition form `[#footnote({body}) <fn-id>]`. The bracket-wrap is
        required because Typst's `<label>` attachment postfix is markup-mode
        syntax and is a parse error as a bare statement inside this
        translator's unified `#{ ... }` code-mode wrapper (mirrors
        visit_figure's `[#figure(...) <label>]`; 14-RESEARCH.md Verified
        Mechanism 1).

        Every REPEAT reference to an already-emitted id emits the bare reuse
        form `footnote(<fn-id>)` -- no bracket-wrap, since `<label>` used as
        a plain call ARGUMENT is a code-mode Label value, not markup-mode
        attachment syntax (14-RESEARCH.md Verified Mechanism 1, finding 1).
        Typst's native footnote() auto-numbering owns numbering entirely
        (D-04); no docutils number/symbol is ever forced.

        A dangling refid (not present in the D-01 index) logs a
        logger.warning naming the refid and skips emitting anything --
        emitting a footnote(<missing-label>) call for a label that was
        never attached is a FATAL Typst compile abort ("label `<..>` does
        not exist in the document"), not a cosmetic issue (14-RESEARCH.md
        Pitfall 1); this guard is load-bearing and must run before any
        emission. `citation`/`citation_reference` are untouched (D-07).

        The footnote_reference node's own child (docutils' rendered marker
        number, e.g. "1"/"2") is never rendered -- Typst supplies its own
        marker via footnote()'s auto-numbering.

        No depart_footnote_reference is defined: SkipNode guarantees it
        never fires.

        Args:
            node: The footnote_reference node
        """
        refid = node.get("refid")
        footnote_node = self._footnote_index.get(refid)

        if footnote_node is None:
            logger.warning(
                "Dangling footnote reference: refid=%r not found in document",
                refid,
            )
            raise nodes.SkipNode

        # Namespace + sanitize here at the single derivation point so BOTH the
        # reuse-ref (footnote(<label>)) and the definition
        # ([#footnote(...) <label>]) branches below emit the identical,
        # Typst-valid, per-document-unique label name. Footnote definition and
        # reference are always in the SAME document, so the current docname
        # namespaces both consistently.
        label = self._namespace_label(self._current_docname(), f"fn-{refid}")

        # Statement-separator convention every other inline child already
        # uses (visit_emphasis/visit_strong/visit_literal all open this way).
        self._add_paragraph_separator()
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        if refid in self._emitted_footnote_ids:
            # D-03 reuse branch: a bare code-mode call, no bracket-wrap --
            # <label> as a function ARGUMENT is a plain code-mode Label
            # value (unlike the definition form's label-ATTACHMENT postfix).
            self.add_text(f"footnote(<{label}>)")
        else:
            # D-03 definition branch: bracket-wrap for the <label>
            # attachment postfix (Phase 11 precedent). Body sourced via
            # buffer-swap through the normal visitor chain (D-02), never
            # node.astext() -- skip only the footnote node's leading
            # `label` child by position (D-06/14-RESEARCH.md Pitfall 3).
            self._emitted_footnote_ids.add(refid)
            saved_body = self.body
            self.body = []
            # Save/restore in_paragraph + paragraph_has_content around the
            # nested walkabout (established convention: visit_emphasis/
            # visit_strong/visit_subscript/visit_superscript all do this
            # identically). Without this, the footnote body's own
            # `paragraph` child unconditionally resets both flags to
            # False/False on depart -- silently clobbering the OUTER
            # paragraph's separator state and dropping the "\n" statement
            # separator the next sibling (e.g. a trailing ".") needs,
            # which is a FATAL "expected semicolon or line break" Typst
            # compile abort (14-RESEARCH.md Pitfall 1 / t8), not a
            # cosmetic issue. Discovered via the GATE-01 real-compile
            # fixture (Rule 1 auto-fix).
            was_in_paragraph = self.in_paragraph
            was_paragraph_has_content = self.paragraph_has_content
            self.in_paragraph = False
            for child in footnote_node.children[1:]:
                child.walkabout(self)
            body_content = "".join(self.body)
            self.body = saved_body
            self.in_paragraph = was_in_paragraph
            self.paragraph_has_content = was_paragraph_has_content
            self.add_text(f"[#footnote({{{body_content}}}) <{label}>]")

        if self.in_list_item:
            self.list_item_needs_separator = True

        # D-06: the footnote_reference's OWN child (docutils' rendered
        # marker Text, e.g. "1"/"2") must never render.
        raise nodes.SkipNode

    def _citation_run_neighbour(self, node: nodes.citation, offset: int) -> bool:
        """
        Scan ``node.parent.children`` in direction ``offset`` (``-1``/``+1``)
        from ``node``'s own index, skipping siblings that emit NOTHING (a
        docutils ``comment`` or ``system_message`` -- ``visit_comment``
        raises ``SkipNode`` before emitting anything -- or an ids-less
        ``nodes.target``, WR-02 below), and report whether the first sibling
        that WOULD emit is another ``nodes.citation``.

        Both ``visit_citation`` (``offset=-1``, "is my PREVIOUS emitting
        sibling also a citation") and ``depart_citation`` (``offset=+1``, "is
        my NEXT emitting sibling also a citation") use this SAME helper, in
        opposite directions (D-05's run detection). Mirrors the established
        ``next_is_target`` sibling-lookahead idiom (``visit_reference``).

        Scanning THROUGH emit-nothing siblings is load-bearing, not a
        nicety: this repository's fixture convention puts a comment above
        and between constructs (D-06), and treating a comment as a run
        break would silently split one rendered reference list into two
        independently-aligned grids with no error anywhere.

        WR-02 (`40-REVIEW.md`): an ids-less ``nodes.target`` is ALSO skipped,
        for the same reason -- ``visit_target``'s "ids falsy" branch
        (``not node.get("ids")``) never writes an anchor, so treating it as a
        real (non-citation) sibling silently split one intended run into two
        independently-aligned grids, with no error anywhere (the same defect
        class as the comment/system_message case above, just a different
        node type). Measured caveat, recorded rather than papered over: this
        inertness is *approximate* inside list items -- ``visit_target``
        still writes a leading ``"\\n"`` when ``self.in_list_item and
        self.list_item_needs_separator``, and unconditionally sets
        ``self.list_item_needs_separator = True`` afterwards when
        ``self.in_list_item`` -- so an ids-less target is strictly *weaker*
        than ``comment``, whose ``visit_comment`` raises ``SkipNode`` before
        touching any separator state at all. This stays a literal,
        one-disjunct case rather than a general "does this node emit bytes"
        predicate (G2, `40.1-CONTEXT.md`/`40.1-02-PLAN.md`): the general
        claim would be false as written (per the list-item caveat just
        above), and generalising the emit-nothing concept beyond citations is
        explicitly deferred out of this phase.

        Args:
            node: The citation node currently being visited/departed.
            offset: ``-1`` to look at the previous sibling, ``+1`` for next.

        Returns:
            ``True`` when the first emitting neighbour in that direction is
            another citation (so the run continues); ``False`` otherwise
            (no parent, no such neighbour, or it emits something else).
        """
        if node.parent is None:
            return False
        children = node.parent.children
        i = node.parent.index(node) + offset
        while 0 <= i < len(children):
            sibling = children[i]
            if isinstance(sibling, (nodes.comment, nodes.system_message)) or (
                isinstance(sibling, nodes.target) and not sibling.get("ids")
            ):
                i += offset
                continue
            return isinstance(sibling, nodes.citation)
        return False

    def _find_citing_reference(self, refid: str) -> nodes.reference | None:
        """
        Find the same-document citing-site ``nodes.reference`` whose own
        ``ids`` contains ``refid`` (a docutils ``backrefs`` entry).

        Deliberately does NOT use ``self.document.ids[refid]``: measured
        this session that docutils' id registry can retain a STALE pointer
        to the ORIGINAL ``citation_reference`` node for a citing site nested
        several containers deep (e.g. inside a list item) even after
        Sphinx's citation-domain transform has replaced it in the tree with
        a resolved ``nodes.reference`` -- the stale node's own ``.parent``
        still points at its former parent, but it is no longer a member of
        that parent's ``.children``, so a naive ``parent.index(node)`` call
        raises ``ValueError``. Scanning ``self.document.findall(...)``
        queries the CURRENT tree structure directly and is immune to this.

        Args:
            refid: A docutils id string from a citation's ``backrefs`` list.

        Returns:
            The matching reference node, or ``None`` if not found.
        """
        for candidate in self.document.findall(nodes.reference):
            if refid in (candidate.get("ids") or []):
                return candidate
        return None

    def _whole_document_reference_eligible(
        self, node: nodes.reference, target_docname: str
    ) -> bool:
        """
        G-48-4 / XREF-03 (Phase 48 plan 07) ROUTING predicate, consulted
        exactly once, immediately after ``_reference_anchor_decision``'s
        own ``_resolve_xref_docname`` call: does a WHOLE-DOCUMENT reference
        (the resolver found no single anchor to target, an EMPTY-anchor
        resolution) get exposed through ``.xref`` -- and thus routed
        through the D-07 compile-time guard against its target's own
        whole-document self-anchor -- or does it keep the plain string-url
        form?

        This is a ROUTING decision, never a second degrade decision (the
        phase's own standing prohibition on a second degrade mechanism
        under any name): it only decides which of the D-07 guard's two
        existing outcomes -- the guarded ``xref is not None`` branch, or
        the string-url ``else`` branch -- a whole-document reference
        enters. The actual degrade-to-plain-text decision, for every
        guarded reference alike, is made once, by the guard's own
        ``query(<label>).len() > 0`` else-branch, at Typst compile time.

        Implements OPTION-A, the owner's choice recorded verbatim at the
        plan 48-05 blocking checkpoint (``48-EXPECTED-STRUCTURE.md``
        "Phase 48 Plan 05" section 6): "leave [Sphinx-generated pages] as
        they are -- guard only references that resolve onto a real
        document."

        Two conjuncts, both required -- exactly as plan 48-06's own unit
        gate specified this policy BEFORE any emitter existed (see that
        module's "Design split" docstring): the node must be
        Sphinx-internal AND the resolved target must be a real document.

        - ``node.get("internal")`` is the discriminator the checkpoint
          recorded as available to BOTH options: ``sphinx.util.nodes.
          make_refnode`` sets ``internal=True`` on every reference Sphinx
          itself builds, while a hand-written relative rST link carries no
          ``internal`` flag at all. Both options were chosen on the stated
          guarantee that they "preserve such asset links untouched", so
          dropping this conjunct is not option-a -- it is a defect against
          the decision as presented. Without it, a hand-written link to a
          genuine asset (``report.pdf``) is hijacked into a guarded jump to
          an unrelated document's self-anchor whenever a real document
          happens to share the asset's path stem (CR-01).
        - ``found_docs`` membership is what separates option-a from
          option-b: it withholds the guard from a Sphinx-internal
          reference whose target is NOT a real document, which is exactly
          the ``genindex`` / ``py-modindex`` / ``search`` population the
          owner chose to leave as-is.

        Read defensively (nested ``getattr`` with an empty-tuple default):
        a hand-built test doctree's stub builder may carry no ``env`` at
        all, or an ``env`` with no ``found_docs`` attribute; either case
        yields ``False`` (not eligible), keeping every existing hand-built-
        doctree test byte-unchanged rather than raising.

        Args:
            node: The reference node under judgement; its ``internal``
                flag is the first conjunct.
            target_docname: The docname ``_resolve_xref_docname`` resolved
                the whole-document refuri to.

        Returns:
            Whether the whole-document reference is eligible to be
            routed through the D-07 guard.
        """
        if not node.get("internal"):
            return False
        return target_docname in getattr(
            getattr(self.builder, "env", None), "found_docs", ()
        )

    def _reference_anchor_decision(
        self, node: nodes.reference
    ) -> _ReferenceAnchorDecision:
        """
        The SINGLE D-14 citing-site anchor judgement (WR-03, D-05/D-06/
        D-07, `40.1-CONTEXT.md`): does ``node`` get its own
        bracket-attached anchor, and if so what is that anchor's label?

        Before Phase 40.1 this was answered independently in TWO places
        that could silently disagree -- ``visit_reference``'s own local
        computation (``node.get("ids")``, ``opens_wrapper``, ``not
        next_is_target``) and the now-deleted ``_citing_reference_has_
        own_anchor`` (``next_is_target`` alone, assuming the other two
        held). Both ``visit_reference`` (the anchor-EMITTING site) and
        ``visit_citation``'s backref loop (the anchor-CONSUMING site, via
        ``_find_citing_reference``) now call THIS method and consume its
        answer, so the two cannot drift apart again.

        Derives every field from ``node`` alone (D-09, Phase 48) --
        ``refuri``/``refid``/``xref``/``opens_wrapper``/``next_is_target``
        are all re-derived here, exactly as ``visit_reference`` computed
        them locally before Phase 40.1, rather than accepting them as
        pre-computed booleans (a pure predicate over three booleans would
        leave the DERIVATION drifting upstream even with the judgement
        unified). ``opens_wrapper`` no longer consults any builder state:
        Phase 48 deleted the build-time all-masters union this method
        used to look up, so whether the reference's cross-document
        TARGET is reachable in any particular compile is answered
        entirely by ``_label_existence_guard()``'s ``query(<label>)`` at
        Typst compile time, never here. When
        eligible, the anchor label is computed via D-13's single
        ``_namespace_label`` derivation point (D-07) -- never a second
        label helper -- so the link target ``visit_citation`` appends and
        the anchor ``visit_reference`` attaches come from the SAME
        expression.

        SILENT by contract (Pitfall 2, `40.1-RESEARCH.md`): no
        ``logger`` call, no ``add_text``, no translator-state mutation.

        Note on ``next_is_target``'s parentless default: this differs
        from the deleted ``_citing_reference_has_own_anchor``, which
        returned ``True`` (i.e. "no target follows") for a parentless
        node. Here ``next_is_target`` simply defaults to ``False`` when
        there is no parent to look ahead in, matching
        ``visit_reference``'s own pre-existing lookahead exactly --
        ``visit_reference``'s form is the authority; the divergence
        between the two was itself an instance of the WR-03 defect class
        this predicate closes.

        Args:
            node: The reference node to judge (a citing-site reference
                looked up via ``_find_citing_reference``, or the node
                ``visit_reference`` is currently visiting).

        Returns:
            The full ``_ReferenceAnchorDecision`` for ``node``.
        """
        refuri = node.get("refuri", "")
        refid = node.get("refid", "")

        xref = self._resolve_xref_docname(refuri) if refuri else None
        # G-48-4 / XREF-03 (Phase 48 plan 07): `_resolve_xref_docname` now
        # also resolves a whole-document refuri (no single anchor) to an
        # EMPTY-anchor pair. Whether that empty-anchor resolution is
        # actually exposed through `.xref` -- and thus routed through the
        # D-07 guard -- is a POLICY question, decided here, immediately
        # after the resolver call, by `_whole_document_reference_eligible`
        # (see its own docstring for the two options the plan 48-05
        # checkpoint recorded and which one this predicate implements). An
        # anchored cross-document `xref` (non-empty anchor) is untouched.
        if (
            xref is not None
            and xref[1] == ""
            and not (self._whole_document_reference_eligible(node, xref[0]))
        ):
            xref = None

        # D-09 (Phase 48): unconditional. Whether the cross-document
        # target this reference points at is actually reachable in any
        # particular compile is now a question the D-07 compile-time
        # guard answers, never a reason to withhold the citing site's
        # OWN same-document anchor -- see _ReferenceAnchorDecision's
        # docstring.
        opens_wrapper = bool(refuri or refid)

        next_is_target = False
        if node.parent:
            node_index = node.parent.index(node)
            if node_index + 1 < len(node.parent.children):
                next_node = node.parent.children[node_index + 1]
                if isinstance(next_node, nodes.target):
                    next_is_target = True

        eligible = bool(node.get("ids")) and opens_wrapper and not next_is_target
        anchor_label = (
            self._namespace_label(self._current_docname(), node["ids"][0])
            if eligible
            else None
        )

        return _ReferenceAnchorDecision(
            refuri=refuri,
            refid=refid,
            xref=xref,
            opens_wrapper=opens_wrapper,
            next_is_target=next_is_target,
            eligible=eligible,
            anchor_label=anchor_label,
        )

    def _label_existence_guard(
        self, label: str, *, prefix: str = "", code_mode_body: bool = False
    ) -> _LabelGuardStrings:
        """
        The SINGLE D-07 shared guard-string derivation point (Phase 48,
        XREF-03/XREF-04): every site that must ask "does this label exist
        in THIS compile" -- ``visit_reference``'s cross-document branch,
        ``visit_citation``'s back-reference loop, and
        ``visit_pending_xref``/``depart_pending_xref`` -- calls this ONE
        method rather than building its own ``context``/``query`` string.
        Before Phase 48 that question was answered once, at BUILD time, by
        a Python union across every master's toctree closure, computed by
        a builder method that no longer exists. After Phase 47 that
        answer can no longer be a single per-docname
        value: the same content ``.typ`` is compiled zero, one, or many
        times -- once per wrapper that ``#include()``s it -- and the
        degrade decision must come out differently in each compile. This
        method moves the decision to Typst COMPILE time instead, wrapping
        the reference's body in a ``context { ... }`` block whose
        ``query(<label>)`` is evaluated fresh by whichever wrapper is
        compiling right now. A site that builds its own
        ``context``/``query`` string instead of calling this method is
        exactly the drift class D-07 exists to reject: never a second
        spelling.

        This method NEVER derives a label itself -- ``label`` is always
        the return value of ``_namespace_label()``, computed once by the
        caller and passed in unchanged, so the ``query(<L>)`` argument and
        the ``link(<L>, ...)`` argument inside the returned strings are
        always the identical string the caller obtained (XREF-03,
        edge/encoding): the demand side and the supply side can never
        spell the label differently.

        The bound identifier the guard's ``let`` statement introduces is
        fixed, project-wide, as ``__tsx_body`` -- every one of this
        phase's call sites and every gate asserting the emitted shape
        agrees on this exact spelling.

        ``close_str``'s conditional is emitted as ONE unbroken statement:
        the ``if query(<L>).len() > 0`` condition and its opening ``{``
        are never separated by a newline. Typst's parser requires them on
        one physical statement -- a newline there is a hard ``expected
        block`` parse error (research Pitfall 1), not a style choice.

        Args:
            label: The already-namespaced label to guard (the output of
                ``_namespace_label()`` -- never re-derived here).
            prefix: ``"#"`` when the guard is emitted from markup mode,
                ``""`` from code mode -- mirrors every other emission
                site's own prefix convention.
            code_mode_body: When ``True`` (the spelling every Phase 48
                call site uses, adopted by ``48-EVIDENCE.md``'s Body-mode
                measurement), the body streams in CODE mode
                (``[#{ ... }]``) so a caller whose children already
                stream in code mode today emits byte-identical child
                content, just nested one level deeper. When ``False``,
                the body streams in MARKUP mode (bare ``[ ... ]``) for a
                future caller whose children already stream in markup
                mode -- no site in this phase uses this branch.

        Returns:
            The ``_LabelGuardStrings`` pair: emit ``open_str`` immediately
            before the body, stream the body unchanged, then emit
            ``close_str`` immediately after it.
        """
        if code_mode_body:
            open_str = f"{prefix}context {{ let __tsx_body = [#{{"
        else:
            open_str = f"{prefix}context {{ let __tsx_body = ["
        close_body = "}]" if code_mode_body else "]"
        close_str = (
            f"{close_body}; if query(<{label}>).len() > 0 {{ "
            f"link(<{label}>, __tsx_body) }} else {{ __tsx_body }} }}"
        )
        return _LabelGuardStrings(open_str=open_str, close_str=close_str)

    def visit_citation(self, node: nodes.citation) -> None:
        """
        Visit a citation definition node (D-01..D-08, D-13, D-14, SC#5).

        Renders a RUN of consecutive sibling ``citation`` nodes as ONE
        two-column ``grid(columns: (auto, 1fr))`` (D-05): the first
        citation of a run opens the grid, each citation emits its own
        label/body row, and the last citation of a run (``depart_citation``)
        closes it. Run adjacency is decided by ``_citation_run_neighbour``,
        which scans THROUGH emit-nothing siblings (a comment must NOT break
        a run; a real paragraph MUST, D-06).

        Deliberately does NOT call ``_emit_id_anchors`` -- the citation
        anchors its OWN id via the label cell's bracket-wrap below instead;
        calling both would define the SAME label twice and abort the whole
        compile at Typst's semantic pass, the exact hazard ``visit_table``'s
        captioned-table comment documents.

        Label cell shapes (D-03/D-07), all sharing one derivation point
        (``_namespace_label`` over the CITATION's OWN ``node["docname"]``,
        never ``_current_docname()`` -- D-13, load-bearing for D-10's
        duplicate-key-across-two-documents case):

        - Zero backrefs: a plain, non-linked ``[Label]`` (D-07 -- the
          deliberate INVERSE of the footnote precedent, Phase 14 D-09,
          which silently drops an unreferenced footnote).
        - Exactly one backref: the label text itself (inside the brackets)
          becomes the back-link; no parenthesised marker (D-03).
        - Two or more backrefs: the bracketed label stays plain, followed
          by a parenthesised, comma-separated (no space) list of one-based
          ordinal markers, each linking to its own citing site (D-02/D-03).
          Built via an array ``.join(",")`` rather than ``+``-concatenation
          specifically so the separator is a BARE "," with nothing else
          between the two ``link(...)`` calls at the .typ-source level.

        A backref is skipped, and the remaining markers' ordinals are
        renumbered contiguously (achieved for free by enumerating the
        FILTERED list, never the raw ``backrefs``), in either of two cases:

        - Its citing site's own anchor ``_reference_anchor_decision``
          declines to grant (``decision.eligible`` is ``False`` -- WR-03,
          D-05/D-06/D-07, `40.1-CONTEXT.md`). This is the SAME predicate
          ``visit_reference`` consults to decide whether to emit that
          anchor in the first place, so the two sites cannot silently
          disagree about whether a citing site was actually anchored
          (the pre-Phase-40.1 defect this closes: a second, independent
          derivation -- ``_citing_reference_has_own_anchor``, checking
          only ``next_is_target`` -- could report "anchor exists" for a
          reference that ``visit_reference`` never anchored, e.g. because
          its ``opens_wrapper`` was ``False``, reproducing WR-01's
          dangling-label fatal by a second route).
        - Its citing site cannot be located at all in the resolved doctree
          (``_find_citing_reference`` returns ``None`` -- WR-01,
          `40-REVIEW.md`). Real, reproducible trigger: a citing
          ``[Label]_`` inside a ``.. only::`` block whose tag is never set.
          Sphinx's ``only``-tag filter transform runs AFTER the citation
          domain populates ``backrefs``, so a backref id can survive
          referencing a node the writer never sees; unfixed, this appended
          a ``link()`` target for a label nothing ever attaches -- a
          whole-document Typst compile fatal. Silent, deliberately (G1,
          `40.1-GATE-EVIDENCE-01.md` § 5): the citing site genuinely is
          not in the output document, so dropping its marker is the correct
          answer, not an error to report.

        The appended backref target is now ``decision.anchor_label`` --
        the SAME predicate's own label, not a second independent
        ``_namespace_label(docname, refid)`` call (D-07's whole point:
        the link target and the attached anchor come out of ONE
        expression). For a same-document backref the two values coincide
        today (this is exactly why SC#5's byte-identity control still
        holds after this change), but nothing enforced that equality
        before -- this closes that unenforced invariant rather than
        altering any current output.

        Separator protocols (SC#5), checked explicitly rather than by
        analogy to the footnote handlers (RESEARCH Pitfall 1 -- a citation
        is a Body element, never Inline, and cannot structurally nest in
        any of the five code-mode concat contexts, all Inline-only):

        - Paragraph protocol: mirrors ``_visit_admonition`` exactly -- no
          leading separator at top level; the previous sibling's own
          trailing break already separates it, and the grid's own trailing
          break (``depart_citation``) separates it from what follows.
        - List-item protocol: the leading newline on grid open (this
          method, first row of a run only) and ``list_item_needs_separator``
          set on grid close (``depart_citation``), both mirrored from the
          admonition pair.
        - Code-mode concat protocol: N/A on this (definition) side by
          construction -- a Body-level citation cannot appear inside any of
          ``_CONCAT_CONTEXTS`` (all Inline-only: desc parameter, link body,
          def-list term, field body, attribution). The concat protocol
          matters on the CITING side instead (Task 1, ``visit_reference``,
          exercised by the fixture's definition-list-term citing site).

        Args:
            node: The citation definition node.
        """
        is_first_of_run = not self._citation_run_neighbour(node, -1)
        if is_first_of_run:
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")
            # column-gutter/row-gutter values are Claude's Discretion (D-04).
            # Deliberately NOT "em"-suffixed literals (Phase 38 IND-04/SC#4,
            # tests/test_desc_content_indent_render_gate.py, asserts
            # translator.py carries exactly ONE numeric em-suffixed literal
            # -- the SHARED_INDENT_STEP assignment -- and citations must not
            # add a second one; 40-CONTEXT.md's own D-04/D-05 discretion
            # note separately says the citation grid does not consume or
            # redefine SHARED_INDENT_STEP, since it solves alignment via an
            # `auto`-sized grid column, not a fixed hanging-indent width).
            # "pt" units sidestep that gate entirely while landing close to
            # the RESEARCH probe's own 0.5em/0.8em suggestion.
            self.add_text(
                "grid(\n  columns: (auto, 1fr),\n"
                "  column-gutter: 6pt,\n  row-gutter: 9pt,\n"
            )

        # Render the label cell's content by walking the label node's OWN
        # CHILDREN (never the label node itself -- visit_label below skips
        # it) through the NORMAL visitor chain via the established
        # buffer-swap idiom (mirrors visit_footnote_reference): save
        # self.body, swap in a fresh list, walk, join, restore. This is
        # what routes the label's text through the SAME central
        # escape_typst_string path every other text node uses -- the whole
        # of this phase's V5 input-validation surface. in_paragraph and
        # paragraph_has_content are saved/restored around the swap because
        # a nested paragraph child (not expected for a label, but the
        # convention is applied uniformly) unconditionally resets both on
        # depart, which would silently clobber the OUTER separator state.
        label_node = node.children[0] if node.children else None
        saved_body = self.body
        self.body = []
        was_in_paragraph = self.in_paragraph
        was_paragraph_has_content = self.paragraph_has_content
        self.in_paragraph = False
        if label_node is not None:
            for child in label_node.children:
                child.walkabout(self)
        label_content = "".join(self.body)
        self.body = saved_body
        self.in_paragraph = was_in_paragraph
        self.paragraph_has_content = was_paragraph_has_content

        docname = node.get("docname")
        backref_targets = []
        for refid in node.get("backrefs") or []:
            ref_node = self._find_citing_reference(refid)
            # WR-01 (`40-REVIEW.md`): `ref_node is None` must ALSO take the
            # `continue` branch -- a backref naming a citing site the
            # `only`-tag filter pruned from the resolved doctree has no
            # `nodes.reference` to consult `_reference_anchor_decision`
            # against, and treating "not found" as "eligible" appends a
            # `link()` target for a label nothing ever attaches (see the
            # docstring above and `40.1-GATE-EVIDENCE-01.md`).
            if ref_node is None:
                continue
            # WR-03 (D-05/D-06/D-07, `40.1-CONTEXT.md`): consult the SAME
            # shared predicate `visit_reference` uses to decide whether it
            # anchored this citing site in the first place, and append
            # ITS label -- not a second, independently-derived
            # `_namespace_label(docname, refid)` call -- so the two sites
            # cannot silently disagree (`40.1-GATE-EVIDENCE-03.md`).
            decision = self._reference_anchor_decision(ref_node)
            if not decision.eligible:
                continue
            backref_targets.append(decision.anchor_label)

        # D-05 (48-RED-EVIDENCE.md failure mode 2): every back-reference
        # target below is routed through the shared _label_existence_guard
        # rather than a bare link(<label>, ...) call. SC#4 exempts an
        # ordinary same-document anchor from guarding because content files
        # are included wholesale -- but a citation back-reference target is
        # NOT guaranteed to exist even though it is same-document: its
        # presence depends on visit_reference having actually RUN on the
        # citing node, and visit_caption's SkipNode (translator.py, the
        # captioned-code-block route) can prune the walker from ever
        # reaching it while _find_citing_reference's document.findall scan
        # still structurally finds the node and judges it eligible. Unlike
        # an ordinary same-document target, this one can be judged eligible
        # with no anchor ever attached -- so it is guarded here even though
        # it is same-document.
        if len(backref_targets) == 1:
            guard = self._label_existence_guard(
                backref_targets[0], prefix="", code_mode_body=True
            )
            label_body = f"{guard.open_str}{label_content}{guard.close_str}"
        else:
            label_body = label_content

        label_expr = f'text("[") + {label_body} + text("]")'

        if len(backref_targets) >= 2:
            marker_parts = []
            for i, target in enumerate(backref_targets, start=1):
                guard = self._label_existence_guard(
                    target, prefix="", code_mode_body=True
                )
                marker_parts.append(f"{guard.open_str}[{i}]{guard.close_str}")
            markers = ",".join(marker_parts)
            label_expr += f' + text(" (") + ({markers}).join(",") + text(")")'

        # Attach the citation's OWN definition anchor via the bracket-wrap
        # label-attachment form -- the same shape depart_term uses --
        # derived from the citation's OWN docname (D-13), never
        # _current_docname(). No ids at all -> no attachment, per Claude's
        # Discretion in the plan (rather than emitting a malformed one).
        ids = node.get("ids") or []
        if ids:
            def_anchor = self._namespace_label(docname, ids[0])
            self.add_text(f"[#{{{label_expr}}} <{def_anchor}>], ")
        else:
            self.add_text(f"{label_expr}, ")

        # Open the body cell as a bare code block (NOT a function call) so
        # the citation's remaining children (its paragraph(s)) evaluate
        # inside it via the NORMAL visitor chain, exactly the way
        # _visit_admonition opens its own content block. The wrapping block
        # is what lets a MULTI-paragraph citation body join into one valid
        # grid-cell argument instead of juxtaposing as two adjacent
        # statements (the phase's classic defect shape).
        self.add_text("{")

    def depart_citation(self, node: nodes.citation) -> None:
        """
        Depart a citation definition node.

        Closes the body cell's code block and emits the row-trailing comma
        so the next row is a separate ``grid(...)`` argument. If the next
        emitting sibling is another citation (``_citation_run_neighbour``),
        the grid stays open for that row. Otherwise closes the grid call and
        emits the trailing break the same way ``_depart_admonition`` does,
        and sets ``list_item_needs_separator`` when inside a list item.

        Args:
            node: The citation definition node.
        """
        self.add_text("},")

        if self._citation_run_neighbour(node, 1):
            return

        self.add_text("\n)\n\n")
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_label(self, node: nodes.label) -> None:
        """
        Visit a citation's ``label`` child node.

        Fires for citations ONLY -- ``visit_footnote`` raises ``SkipNode``
        before its own ``label`` child is ever reached, and
        ``visit_footnote_reference`` walks ``footnote_node.children[1:]``,
        skipping its ``label`` child positionally rather than via a real
        handler. ``visit_citation`` above already renders THIS label's own
        children via a dedicated buffer-swap before the citation's
        remaining children (this node included) are walked normally by
        docutils -- so this handler's only job is to prevent the label's
        text from rendering a SECOND time into the body cell. As a side
        effect, this also removes the second ``unknown node type: <label
        ...>`` warning the shipped samples emit today (40-GATE-EVIDENCE-01/
        02.md).

        Raises:
            nodes.SkipNode: Always -- the label's children were already
                rendered by visit_citation.
        """
        raise nodes.SkipNode

    def _push_table_state(self) -> None:
        """
        Save the enclosing table's in-progress scalar state onto a private
        stack before resetting those scalars for a NESTED table's own use
        (TBL-04, Phase 43).

        Covers the full clobber-prone scalar set -- not just the 5 the
        original bug report named, but the larger set RESEARCH.md Pitfall 1
        measured to share the identical unconditional-write/
        unconditional-read shape: ``table_cells``, ``table_colcount``,
        ``table_colwidths``, ``table_caption``, ``table_cell_content``
        (existence + value), ``in_thead``, ``current_morecols``/
        ``current_morerows``, and ``_table_is_captioned`` (TBL-05, plan
        43-04: the STRUCTURAL captioned decision, which has the identical
        per-table clobber shape -- a nested captioned table's own decision
        must not overwrite the enclosing table's when the inner table's
        depart_table finishes). The morecols/morerows pair is read via
        ``getattr`` with a ``0`` default (ASVS V5): they are set lazily by
        the FIRST ``visit_entry`` ever called on this translator instance,
        so a malformed doctree that somehow reaches a nested table before
        any entry at all must not raise ``AttributeError`` here.

        Called only from ``visit_table`` when ``self.in_table`` is already
        True (i.e. this table node is nested inside another table's cell) --
        never for a top-level table, so the top-level path pushes nothing.
        """
        self._table_state_stack.append(
            {
                "table_cells": self.table_cells,
                "table_colcount": self.table_colcount,
                "table_colwidths": self.table_colwidths,
                "table_caption": self.table_caption,
                "table_cell_content": getattr(self, "table_cell_content", None),
                "in_thead": self.in_thead,
                "current_morecols": getattr(self, "current_morecols", 0),
                "current_morerows": getattr(self, "current_morerows", 0),
                "_table_is_captioned": self._table_is_captioned,
            }
        )

    def _pop_table_state(self) -> None:
        """
        Restore the enclosing table's scalar state after a NESTED table's
        ``depart_table`` has finished building its own rendered markup
        (TBL-04, Phase 43).

        A no-op on an empty stack (ASVS V5 / threat T-43-01): an unbalanced
        ``depart_table`` from a malformed doctree -- one with no matching
        prior nested ``visit_table`` -- must take the top-level path in the
        caller instead of raising ``IndexError`` out of the translator and
        killing a CI build. Never call ``self._table_state_stack.pop()`` or
        index ``[-1]`` directly; always guard through this method.
        """
        if not self._table_state_stack:
            return
        frame = self._table_state_stack.pop()
        self.table_cells = frame["table_cells"]
        self.table_colcount = frame["table_colcount"]
        self.table_colwidths = frame["table_colwidths"]
        self.table_caption = frame["table_caption"]
        if frame["table_cell_content"] is None:
            if hasattr(self, "table_cell_content"):
                del self.table_cell_content
        else:
            self.table_cell_content = frame["table_cell_content"]
        self.in_thead = frame["in_thead"]
        self.current_morecols = frame["current_morecols"]
        self.current_morerows = frame["current_morerows"]
        self._table_is_captioned = frame["_table_is_captioned"]

    def _push_figure_state(self) -> None:
        """
        Save the enclosing figure's in-progress scalar state onto a private
        stack before resetting those scalars for a NESTED figure's own use
        (FIG-01, Phase 43).

        Mirrors ``_push_table_state`` (TBL-04, plan 43-01): a nested figure
        arises when a ``figure`` node's ``legend`` child itself contains
        another ``figure`` node (docutils' second-and-later-body-block
        classification, 43-RESEARCH.md Pitfall 4). Covers ``in_figure``,
        ``figure_content``, ``figure_caption``, ``_figure_block_width``,
        ``_figure_has_legend`` and ``_saved_body_for_figure_caption`` -- the
        full clobber-prone scalar set touched anywhere in
        ``visit_figure``/``depart_figure``/``visit_caption``/``depart_caption``.

        Called only from ``visit_figure`` when ``self.in_figure`` is already
        True (i.e. this figure node is nested inside another figure's
        legend) -- never for a top-level figure, so the top-level path
        pushes nothing.
        """
        self._figure_state_stack.append(
            {
                "in_figure": self.in_figure,
                "figure_content": self.figure_content,
                "figure_caption": self.figure_caption,
                "_figure_block_width": self._figure_block_width,
                "_figure_has_legend": self._figure_has_legend,
                "_saved_body_for_figure_caption": self._saved_body_for_figure_caption,
            }
        )

    def _pop_figure_state(self) -> None:
        """
        Restore the enclosing figure's scalar state after a NESTED figure's
        ``depart_figure`` has finished emitting its own rendered markup
        (FIG-01, Phase 43).

        A no-op on an empty stack (ASVS V5, threat T-43-02): an unbalanced
        ``depart_figure`` from a malformed doctree -- one with no matching
        prior nested ``visit_figure`` -- must take the top-level teardown
        path in the caller instead of raising ``IndexError`` out of the
        translator and killing a CI build. Never call
        ``self._figure_state_stack.pop()`` or index ``[-1]`` directly;
        always guard through this method.
        """
        if not self._figure_state_stack:
            return
        frame = self._figure_state_stack.pop()
        self.in_figure = frame["in_figure"]
        self.figure_content = frame["figure_content"]
        self.figure_caption = frame["figure_caption"]
        self._figure_block_width = frame["_figure_block_width"]
        self._figure_has_legend = frame["_figure_has_legend"]
        self._saved_body_for_figure_caption = frame["_saved_body_for_figure_caption"]

    def visit_table(self, node: nodes.table) -> None:
        """
        Visit a table node.

        Args:
            node: The table node
        """
        # A propagated explicit target can land its id on this table; anchor it
        # so a same-document link(<id>, ...) resolves (no ids -> no-op). Emitted
        # while self.in_table is still False, so add_text routes to the real
        # body (not a stale table_cell_content buffer).
        #
        # TBL-02 (Phase 25, Critical Pitfall 3): a CAPTIONED table instead
        # self-anchors ids[0] as its own figure `<label>` postfix in
        # depart_table, mirroring depart_figure. Anchoring it here TOO would
        # define that id TWICE, aborting the whole compile at Typst's
        # semantic pass with "label ... occurs multiple times" -- a real
        # fatal invisible to any translator-only unit test. The doctree is
        # already fully built at visit_table time (docutils constructs the
        # whole tree before any visiting begins), so the captioned pre-check
        # is reliable here, before the title has even been visited. Skip the
        # call entirely for a captioned table; depart_table calls it with
        # skip_ids={ids[0]} AFTER emitting the figure's own <label>.
        # Non-captioned tables keep this unconditional call, unchanged.
        #
        # TBL-05 (Phase 43, D-07): this STRUCTURAL result is stashed on
        # self._table_is_captioned (below, AFTER the nested-table push) for
        # depart_table's anchoring decision. It is NOT made value-aware here
        # -- the doctree is fully built at visit_table time, but the
        # title's RENDERED content is only known after visit_title/
        # depart_title run, and a title whose only child is a raw node with
        # a non-typst format renders to the empty string (visit_raw raises
        # SkipNode) while its astext() is non-empty. Any astext()-based
        # pre-check would misclassify that case.
        is_captioned = bool(node.children) and isinstance(node.children[0], nodes.title)
        if not is_captioned:
            self._emit_id_anchors(node)

        # Emit a leading newline separator when this table follows a
        # sibling inside a list item, matching the block-visitor pattern
        # established in bug #4 (bullet_list/literal_block/definition_list/
        # block_quote/field_list). Otherwise depart_table's table( juxtaposes
        # against the preceding inline expression in the list-item content
        # block -- e.g. `text("Text styling commands:")table(` -- a Typst
        # parse error ("expected semicolon or line break"). table was the
        # one block visitor omitted from that fix. Use self.body.append
        # directly (NOT self.add_text) -- self.in_table is set True below,
        # and add_text() would misroute this newline into a stale
        # table_cell_content list left over from a PRIOR table on this
        # translator instance (same pitfall depart_table's table( emission
        # already avoids -- see the comment there).
        if self.in_list_item and self.list_item_needs_separator:
            self.body.append("\n")
            self.list_item_needs_separator = False

        # TBL-04 (Phase 43): self.in_table already True means an ENCLOSING
        # table is still open -- this table node is NESTED inside one of
        # its cells. Push a snapshot of the outer table's in-progress
        # scalar state (see _push_table_state's docstring for the full
        # set) before resetting for the inner table's own use below, or
        # the inner table's own depart_table clobbers the outer's
        # accumulated state (the TBL-04 defect). table_cell_content,
        # table_caption and in_thead are ALSO reset here, inside this
        # nested branch only, so the inner table starts genuinely fresh
        # instead of inheriting a caption/header-row flag left over from
        # the outer table's own in-progress title/thead -- both the push
        # and these extra resets live inside this branch, so the
        # top-level (non-nested) path below is byte-identical to
        # pre-TBL-04 behavior.
        if self.in_table:
            self._push_table_state()
            self.table_cell_content = []
            self.table_caption = None
            self.in_thead = False

        self.in_table = True
        self.table_cells = []  # Store cells for table generation
        self.table_colcount = 0  # Track number of columns
        self.table_colwidths = []  # Per-column colwidth accumulator (D-01)
        # TBL-05: assigned AFTER the push above (never before) -- the push
        # must capture the ENCLOSING table's own _table_is_captioned value
        # before this table's decision overwrites it, mirroring how
        # table_cells/table_colcount/table_colwidths are reset here too.
        self._table_is_captioned = is_captioned

    def _build_columns_fr_arg(self) -> str:
        """
        Build the Typst ``columns: (...)`` argument from captured colwidth
        values (FID-01a D-01/D-02).

        Falls back to equal 1fr-per-column when colwidth data is missing,
        all zero, or its length does not match table_colcount (defensive
        path -- not observed in any real docutils output tested during
        research, but nodes.colspec['colwidth'] is technically Optional
        per the docutils API).

        Returns:
            A Typst fr-weighted columns tuple string, e.g. "(1fr, 1fr)".
        """
        widths = self.table_colwidths
        n = self.table_colcount
        valid = len(widths) == n and n > 0 and all(w and w > 0 for w in widths)
        if not valid:
            widths = [1] * n
        return "(" + ", ".join(f"{w}fr" for w in widths) + ")"

    def _format_table_cell(self, cell: dict, indent: str = "  ") -> str:
        """
        Format a table cell with optional colspan/rowspan.

        Args:
            cell: Cell dictionary with 'content', 'colspan', 'rowspan'
            indent: Indentation string

        Returns:
            Formatted Typst cell string
        """
        content = cell["content"]
        colspan = cell.get("colspan", 1)
        rowspan = cell.get("rowspan", 1)

        # Normal cell (no spanning)
        if colspan == 1 and rowspan == 1:
            return f"{indent}{{{content}}},\n"

        # Cell with spanning - use table.cell()
        params = []
        if colspan > 1:
            params.append(f"colspan: {colspan}")
        if rowspan > 1:
            params.append(f"rowspan: {rowspan}")

        params_str = ", ".join(params)
        return f"{indent}table.cell({{{content}}}, {params_str}),\n"

    def depart_table(self, node: nodes.table) -> None:
        """
        Depart a table node.

        A CAPTIONED table (TBL-01/TBL-02, Phase 25 -- ``self.table_caption``
        truthy, i.e. a non-empty rendered caption; a whitespace/empty title
        strips to a falsy ``""`` and takes the plain-table path, never an
        empty-caption ``figure()``) wraps the inner ``table(...)`` call in
        ``figure(..., caption: {...}, kind: table)`` for native Typst
        "Table N" numbering, composed with the existing ``:width:`` ->
        ``block(width: ...)[...]`` wrap exactly like ``depart_figure``
        (D-04): the block wraps the WHOLE figure, and the ``<label>``
        bracket-close lands inside whichever markup bracket was opened.
        A caption-less table takes the byte-for-byte UNCHANGED plain-table
        path (SC#2).

        TBL-05 (Phase 43, D-05): RENDERING and ANCHORING are two separate
        decisions that are allowed to disagree, deliberately, matching
        Sphinx's own LaTeX builder measured against identical input.
        RENDERING keeps gating on ``self.table_caption``'s truthiness
        (unchanged from the paragraph above). ANCHORING instead gates on
        ``self._table_is_captioned``, the STRUCTURAL decision stashed by
        ``visit_table`` -- so a table whose title node exists but renders to
        the empty string still anchors its ids, even though it is NOT
        figure-wrapped and consumes NO table number. See the inline
        comments around ``structural_is_captioned``/``was_captioned`` below
        for the exact split.

        Args:
            node: The table node
        """
        # Generate Typst table() syntax (no # prefix in unified code mode).
        # Built as a local string (emission_str), never appended directly
        # here -- TBL-04 (Phase 43) needs to decide AFTER this block
        # whether the string's destination is the enclosing cell's buffer
        # (nested table) or self.body (top-level table); see the
        # destination-decision block below.
        emission_str: str | None = None
        if self.table_colcount > 0:
            # LEN-01: :width: is assigned to node["width"] by docutils'
            # Table.set_table_width(), shared by RSTTable/CSVTable/ListTable
            # -- one wiring covers all three directive types (they all
            # converge on nodes.table). Typst's table() rejects a direct
            # width: kwarg (verified real-compile failure, same as figure),
            # so a converted value wraps the WHOLE table() call in
            # block(width: ...)[...] instead (16-RESEARCH.md Pitfall 3).
            width = node.get("width")
            converted_width = self._convert_length_to_typst(width) if width else None

            # Separate header cells from body cells
            header_cells = [cell for cell in self.table_cells if cell.get("is_header")]
            body_cells = [
                cell for cell in self.table_cells if not cell.get("is_header")
            ]

            # Build the inner table(...) call as one string -- unchanged
            # emission logic, just assembled locally instead of appended
            # directly, so a captioned table can wrap it in figure(...)
            # below without re-deriving the cell-rendering logic.
            table_parts = [f"table(\n  columns: {self._build_columns_fr_arg()},\n"]
            if header_cells:
                table_parts.append("  table.header(\n")
                for cell in header_cells:
                    table_parts.append(self._format_table_cell(cell, indent="    "))
                table_parts.append("  ),\n")
            for cell in body_cells:
                table_parts.append(self._format_table_cell(cell, indent="  "))
            table_parts.append(")")
            table_code = "".join(table_parts)

            if self.table_caption:
                # TBL-01/D-02: figure-wrap with native "Table N" numbering.
                # kind: table is ALWAYS present. caption is a {...} code
                # block (already-rendered code-mode content, mirrors
                # depart_figure's caption: {self.figure_caption} wrap).
                figure_code = (
                    f"figure(\n{table_code},\n"
                    f"  caption: {{{self.table_caption}}},\n"
                    f"  kind: table\n)"
                )
                # D-04 three-way branch, mirroring depart_figure verbatim:
                # ids always self-anchor via the <label> postfix regardless
                # of width; width alone (no ids) closes a bracket with no
                # label; neither -> bare figure(...) statement.
                if node.get("ids"):
                    label = self._namespace_label(
                        self._current_docname(), node["ids"][0]
                    )
                    if converted_width is not None:
                        emission_str = (
                            f"block(width: {converted_width})[#{figure_code} "
                            f"<{label}>]\n\n"
                        )
                    else:
                        emission_str = f"[#{figure_code} <{label}>]\n\n"
                elif converted_width is not None:
                    emission_str = (
                        f"block(width: {converted_width})[#{figure_code}]\n\n"
                    )
                else:
                    emission_str = f"{figure_code}\n\n"
            else:
                # Caption-less path: byte-for-byte unchanged (SC#2).
                if converted_width is not None:
                    emission_str = f"block(width: {converted_width})[#{table_code}]\n\n"
                else:
                    emission_str = f"{table_code}\n\n"

        # TBL-03 (Phase 42): captured BEFORE self.table_caption is reset
        # below, because the original `if self.table_caption:` condition
        # cannot be re-evaluated after that reset -- re-reading it there
        # would evaluate False for every captioned table and silently
        # disable the propagated-anchor emission below while leaving the
        # caption-less path (which never had a bug) looking correct. The
        # `self.table_colcount > 0` conjunct mirrors the enclosing guard
        # this call site sat inside before the move, so a degenerate
        # zero-column captioned table keeps its current (no-op) emission.
        # Computed BEFORE the nested/top-level destination decision below,
        # since that decision may pop-and-restore self.table_caption to an
        # ENCLOSING table's value -- was_captioned must reflect THIS
        # table's own captioned status, not the outer one's.
        #
        # TBL-05 (Phase 43, D-05): was_captioned now ALSO answers "did this
        # table take the figure-wrapped branch above" -- it is exactly the
        # same condition the `if self.table_caption:` branch above tested,
        # captured here before any reset. This is reused below to decide
        # whether ids[0] is already self-anchored by that figure's own
        # <label> postfix (skip it) or not (anchor it too).
        was_captioned = self.table_colcount > 0 and bool(self.table_caption)

        # TBL-05 (Phase 43, D-05/D-07): the STRUCTURAL captioned decision
        # from visit_table, read here -- BEFORE the nested/top-level
        # destination decision below, for the identical reason was_captioned
        # is captured here rather than after: _table_is_captioned now joins
        # _push_table_state/_pop_table_state's snapshot set (TBL-04), so a
        # NESTED table's own depart_table would otherwise read the
        # ENCLOSING table's restored value instead of its own. This is the
        # ANCHORING gate (independent of whether the caption rendered to
        # anything); was_captioned above stays the RENDERING gate. The two
        # are allowed to disagree -- see the class docstring note below.
        structural_is_captioned = self._table_is_captioned

        # TBL-04 (Phase 43): decide the emission string's destination as an
        # EXPLICIT branch, never a blanket switch to self.add_text (Pitfall
        # 2 -- with self.in_table still True at this point, add_text would
        # misroute a TOP-LEVEL table's own render into whatever buffer
        # in_table's dispatch happens to point at, losing it entirely).
        # was_nested is captured BEFORE popping: _pop_table_state() mutates
        # the stack, so "was there an enclosing frame for THIS table" must
        # be read first.
        was_nested = bool(self._table_state_stack)

        if was_nested:
            # NESTED: restore the enclosing table's frame FIRST, then
            # append this table's own rendered markup into the RESTORED
            # enclosing cell's buffer -- never self.body. self.in_table
            # stays True (an enclosing table is still open) and
            # table_cell_content is NOT deleted; only the OUTERMOST
            # table's close (the else branch below, on a future depart)
            # does that, per the Phase 25 lifetime invariant extended
            # below.
            self._pop_table_state()
            if emission_str is not None:
                self.table_cell_content.append(emission_str)
        else:
            # TOP-LEVEL: byte-for-byte identical to pre-TBL-04 behavior --
            # self.body.append directly (never self.add_text; see Pitfall
            # 2 above), then clear self.in_table.
            if emission_str is not None:
                self.body.append(emission_str)
            self.in_table = False

        # TBL-02/Critical Pitfall 3: ids[0] is already self-anchored above
        # as the figure's own <label> -- anchoring it again here would
        # define it TWICE (Typst "label ... occurs multiple times" compile
        # fatal). Anchor only a PROPAGATED remainder id (ids[1:]); no-op
        # when there is none.
        #
        # TBL-03 (Phase 42): for a TOP-LEVEL table this call must run AFTER
        # self.in_table is cleared above -- add_text() (see that method)
        # diverts every append into self.table_cell_content while
        # self.in_table is set, and that buffer is `del`eted a few
        # statements below, so an anchor emitted from the old pre-reset
        # call site never reached self.body at all. For a NESTED table,
        # self.in_table is still True and table_cell_content has already
        # been restored to the ENCLOSING cell's buffer above, so add_text()
        # correctly routes this call's markup into that same buffer,
        # immediately after this table's own emission_str.
        #
        # TBL-05 (Phase 43, D-05): the GATE is now structural_is_captioned
        # (matches visit_table's unconditional-anchor skip above -- this
        # call fires exactly when that one did NOT, so a non-captioned
        # table is never anchored twice), not was_captioned. This closes
        # the TBL-05 dangling-anchor defect: a table whose title node
        # exists but renders to the empty string is structurally captioned
        # (visit_table skipped its own anchor call) yet was NOT
        # figure-wrapped above (was_captioned is False, since
        # self.table_caption stripped to ""), so without this change its
        # ids were anchored on NEITHER path. Whether ids[0] is skipped
        # still depends on was_captioned specifically -- it answers "did
        # this table actually take the figure-wrapped branch that
        # self-anchors ids[0]", which is a strictly narrower question than
        # "is this table structurally captioned". A table that is
        # structurally captioned but did NOT figure-wrap (was_captioned
        # False) anchors EVERY id here, since nothing else anchored ids[0]
        # for it (D-05's "not figure-wrapped, consumes no table number"
        # rendering side, matched by "anchors every id" on the anchoring
        # side).
        if structural_is_captioned:
            skip_ids = set(node.get("ids", [])[:1]) if was_captioned else set()
            self._emit_id_anchors(node, skip_ids=skip_ids)

        if not was_nested:
            # OUTERMOST close only: reset the scalar set for the next
            # top-level table / sibling, and delete table_cell_content so
            # hasattr() goes False for the NEXT table (Phase 25 invariant,
            # extended by TBL-04: a NESTED table's own close never reaches
            # this branch -- was_nested is True there -- so an inner
            # table's departure no longer tears down the outer table's
            # still-in-progress state).
            self.table_cells = []
            self.table_colcount = 0
            self.table_colwidths = []
            self.table_caption = None
            # Stale-buffer root-cause fix (25-RESEARCH.md Verified Mechanism
            # 2): table_cell_content is created by the FIRST table's
            # visit_entry and reset to [] (not deleted) at every
            # depart_entry, so it persists as an EXISTING attribute for the
            # rest of the translator's lifetime. A subsequent table's
            # caption title is visited before any of that table's OWN
            # visit_entry calls -- if table_cell_content still exists
            # (stale from a prior table), add_text() silently routes the
            # caption's content into it instead of falling through to
            # self.body, and the caption is lost entirely. Only `del` (not
            # a reset to []) makes hasattr() False again, so the NEXT
            # table's pre-entry add_text() calls correctly fall through.
            # TBL-04 (Phase 43): the `del` now fires ONLY when this table
            # was NOT nested, i.e. when the closing table is the OUTERMOST
            # one (the stack was already empty before this depart's own
            # pop attempt) -- an inner table's own close takes the
            # was_nested branch above instead and never reaches here, so
            # table_cell_content survives for the enclosing table to keep
            # appending into.
            if hasattr(self, "table_cell_content"):
                del self.table_cell_content

        # Mark that a following sibling in the same list item must be
        # separated (block-visitor pattern, bug #4).
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_tgroup(self, node: nodes.tgroup) -> None:
        """
        Visit a tgroup (table group) node.

        Args:
            node: The tgroup node
        """
        # Get column count from tgroup
        self.table_colcount = node.get("cols", 0)

    def depart_tgroup(self, node: nodes.tgroup) -> None:
        """
        Depart a tgroup (table group) node.

        Args:
            node: The tgroup node
        """
        pass

    def visit_colspec(self, node: nodes.colspec) -> None:
        """
        Visit a colspec (column specification) node.

        Args:
            node: The colspec node
        """
        # Capture colwidth instead of discarding it (FID-01a D-01) --
        # consumed by _build_columns_fr_arg() at depart_table.
        self.table_colwidths.append(node.get("colwidth"))
        raise nodes.SkipNode

    def depart_colspec(self, node: nodes.colspec) -> None:
        """
        Depart a colspec (column specification) node.

        Args:
            node: The colspec node
        """
        pass

    def visit_thead(self, node: nodes.thead) -> None:
        """
        Visit a thead (table header) node.

        Args:
            node: The thead node
        """
        # Mark that we're in the header section
        self.in_thead = True

    def depart_thead(self, node: nodes.thead) -> None:
        """
        Depart a thead (table header) node.

        Args:
            node: The thead node
        """
        # Mark that we're no longer in the header section
        self.in_thead = False

    def visit_tbody(self, node: nodes.tbody) -> None:
        """
        Visit a tbody (table body) node.

        Args:
            node: The tbody node
        """
        pass

    def depart_tbody(self, node: nodes.tbody) -> None:
        """
        Depart a tbody (table body) node.

        Args:
            node: The tbody node
        """
        pass

    def visit_row(self, node: nodes.row) -> None:
        """
        Visit a row (table row) node.

        Args:
            node: The row node
        """
        # Rows are processed by collecting entries
        pass

    def depart_row(self, node: nodes.row) -> None:
        """
        Depart a row (table row) node.

        Args:
            node: The row node
        """
        pass

    def visit_entry(self, node: nodes.entry) -> None:
        """
        Visit an entry (table cell) node.

        Args:
            node: The entry node
        """
        # Start collecting cell content
        self.table_cell_content = []

        # Read cell spanning attributes
        # morecols: number of additional columns (0 = normal cell)
        # morerows: number of additional rows (0 = normal cell)
        self.current_morecols = node.get("morecols", 0)
        self.current_morerows = node.get("morerows", 0)

    def depart_entry(self, node: nodes.entry) -> None:
        """
        Depart an entry (table cell) node.

        Args:
            node: The entry node
        """
        # Get cell content and add to table cells
        # Extract text from the accumulated body content since visit_entry
        cell_text = ""
        if hasattr(self, "table_cell_content") and self.table_cell_content:
            cell_text = "".join(self.table_cell_content).strip()

        if not cell_text:
            # If no content was captured, try to get text from the node
            cell_text = node.astext().strip()

        # Calculate colspan and rowspan from morecols/morerows
        # morecols=1 means 2 columns total (1 + 1 additional)
        colspan = self.current_morecols + 1
        rowspan = self.current_morerows + 1

        # Store cell with header/body distinction and spanning info
        self.table_cells.append(
            {
                "content": cell_text,
                "is_header": self.in_thead,
                "colspan": colspan,
                "rowspan": rowspan,
            }
        )
        self.table_cell_content = []

    def visit_block_quote(self, node: nodes.block_quote) -> None:
        """
        Visit a block quote node.

        Generates quote() function call (no # prefix in code mode).

        Args:
            node: The block quote node
        """
        # A propagated explicit target can land its id on this block quote;
        # anchor it so a same-document link(<id>, ...) resolves (no ids -> no-op).
        self._emit_id_anchors(node)

        # Emit a leading newline separator when this block quote follows a
        # sibling inside a list item, matching the block-visitor pattern
        # established in bug #4 (bullet_list/literal_block/definition_list).
        # Otherwise `quote[`/`quote(` juxtaposes against the preceding inline
        # expression in the list-item content block -- e.g.
        # `text(" functions:")quote[` -- a Typst parse error ("expected
        # semicolon or line break"). block_quote was the one block visitor
        # omitted from that fix.
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Emit the block quote as a CODE-MODE body -- quote(block: true, { ... })
        # -- NOT the markup-mode trailing content block quote[ ... ] (bug #15).
        # Every body child is a code-mode function call (par({text(...)}),
        # raw(...), link(...)). Inside a markup `[...]` block those bytes are
        # treated as LITERAL PROSE, so any markup-special char in a child
        # string literal -- e.g. the lone `_` in raw("_t") (Sphinx's `_t`
        # static-template suffix) -- opened a stray inline-emphasis span that
        # never closed -> "TypstError: unclosed delimiter". The `{ ... }`
        # content block evaluates the children as real function calls (the same
        # code-mode content-block wrapping used by par()/definition (bug #7)),
        # so their string-literal chars are inert. block: true keeps block
        # quotes rendering as block quotes. The attribution, when present,
        # closes this body block and is appended as a code-mode named argument
        # (see visit_attribution) -- so the opening is identical in both cases.
        self.add_text("quote(block: true, {")

    def depart_block_quote(self, node: nodes.block_quote) -> None:
        """
        Depart a block quote node.

        Args:
            node: The block quote node
        """
        # Check if there's an attribution child node. When present,
        # visit_attribution already closed the body `{` and opened the named
        # `attribution: {` argument, and depart_attribution closed that `}`;
        # so here we only close the quote() call. Otherwise we close both the
        # body block and the call.
        has_attribution = any(isinstance(child, nodes.attribution) for child in node)

        if has_attribution:
            self.add_text(")\n\n")
        else:
            self.add_text("})\n\n")

        # Mark that a following sibling in the same list item must be separated
        # (block-visitor pattern, bug #4).
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_attribution(self, node: nodes.attribution) -> None:
        """
        Visit an attribution node (quote attribution).

        Args:
            node: The attribution node
        """
        # Close the code-mode quote body block and open the attribution as a
        # named argument -- quote(block: true, { <body> }, attribution: {
        # <attr> }) -- a form Typst accepts (positional then named).
        #
        # The attribution value is a CODE-MODE `{ ... }` content block, NOT a
        # markup-mode `[ ... ]` block (mirroring the code-mode quote body,
        # bug #15). An attribution's inline children are emitted through the
        # code-mode visitors (visit_Text -> `text("...")`, visit_emphasis ->
        # `emph({...})`, visit_literal -> `raw("...")`, visit_reference ->
        # `link(...)`), each a bare (un-`#`-prefixed) function call. Inside a
        # markup `[...]` argument those bytes are LITERAL PROSE, so Typst
        # typesets them verbatim -- the author name renders as `text(“Author”)`
        # (curly quotes from smart-quote typography) instead of `Author`, and
        # a lone markup-special char in a child string literal (e.g. the `_` in
        # an inline literal ``_t``) opens a stray unclosed emphasis span that
        # aborts the compile. A `{ ... }` code block EVALUATES the children as
        # real content. Activating the _in_attribution concat context makes the
        # inline children + separated (`emph({...}) + text(...) + raw(...)`),
        # since attribution holds inline children directly (no wrapping
        # paragraph) that would otherwise juxtapose into a syntax error.
        self.add_text("}, attribution: {")
        self._in_attribution = True
        self._attribution_has_content = False

    def depart_attribution(self, node: nodes.attribution) -> None:
        """
        Depart an attribution node.

        Args:
            node: The attribution node
        """
        # Close the code-mode attribution content block and exit the concat
        # context. depart_block_quote closes the enclosing quote() call.
        self._in_attribution = False
        self.add_text("}")

    def visit_image(self, node: nodes.image) -> None:
        """
        Visit an image node.

        Generates image() function call (no # prefix in code mode).
        Adjusts image paths for nested documents (Issue #69).

        Args:
            node: The image node
        """
        # A propagated explicit target can land its id on a standalone (block)
        # image; anchor it so a same-document link(<id>, ...) resolves (no ids
        # -> no-op). Skipped inside a figure: the figure node owns the caption
        # id and emits its own `[#figure(...) <label>]` anchor, and an image
        # nested in a figure never carries a propagated block target.
        if not self.in_figure:
            self._emit_id_anchors(node)

        uri = node.get("uri", "")

        # Get current document name for path adjustment (Issue #69)
        current_docname = getattr(self.builder, "current_docname", None)

        # Adjust path based on output file location (Issue #69)
        adjusted_uri = self._compute_relative_image_path(uri, current_docname)

        # Add proper indentation if inside a figure
        if self.in_figure:
            self.add_text(f'  image("{adjusted_uri}"')
        else:
            # No # prefix in code mode
            self.add_text(f'image("{adjusted_uri}"')

        # Add optional attributes. Length values from docutils (:width:/:height:)
        # may use CSS units Typst does not understand (e.g. raw "px"), which
        # would abort the whole compile (Issue #114, FIG-01). Convert via
        # _convert_length_to_typst and drop the dimension entirely when the
        # unit is unsupported (D-02) -- never emit a raw unconverted unit.
        if "width" in node:
            converted_width = self._convert_length_to_typst(node["width"])
            if converted_width is not None:
                self.add_text(f", width: {converted_width}")

        if "height" in node:
            converted_height = self._convert_length_to_typst(node["height"])
            if converted_height is not None:
                self.add_text(f", height: {converted_height}")

        self.add_text(")")

    def depart_image(self, node: nodes.image) -> None:
        """
        Depart an image node.

        Args:
            node: The image node
        """
        # If inside a figure, don't add extra newlines (figure will handle spacing)
        if not self.in_figure:
            self.add_text("\n\n")

    def visit_target(self, node: nodes.target) -> None:
        """
        Visit a target node (label definition).

        Args:
            node: The target node
        """
        # Check if we're in a markup mode wrapper started by reference
        if (
            hasattr(self, "_in_reference_with_target")
            and self._in_reference_with_target
        ):
            # Re-enable markup mode for label output (was disabled for link content)
            self._in_markup_mode = True
            # Output label in markup mode (with # prefix in markup mode)
            if node.get("ids"):
                label_id = self._namespace_label(
                    self._current_docname(), node["ids"][0]
                )
                # FID-13 fix: no leading '\n'. The preceding content is
                # always the closing ')' of the reference's link(...) call
                # -- '#' unambiguously starts a new markup-embedded
                # expression with no separator needed. A leading '\n' here
                # renders as a visible space in Typst MARKUP mode (a
                # newline in markup content collapses to a space), which
                # combines with the genuinely-source-present following
                # space to produce a stray double space (D-03).
                self.add_text(f'#label("{label_id}")')
            # Close the markup block
            self.add_text("]")
            # Clear the flags
            self._in_reference_with_target = False
            self._in_markup_mode = False  # Exit markup mode
            # Mark separator needed for next element
            if self.in_list_item:
                self.list_item_needs_separator = True
            # Skip processing children as target is typically empty
            raise nodes.SkipNode

        # Original behavior for non-markup-wrapped targets
        # Add newline separator if in list item and not first element
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Generate a Typst anchor if the target has ids.
        #
        # Emit the anchor as a metadata-carrying markup block --
        # `[#metadata(none) <id>]` -- exactly like the extra-id anchors in
        # visit_title/depart_title. A bare code-mode `label("id")` is WRONG in
        # two ways: (a) two adjacent targets emit `label("id1")label("id2")`
        # with no separator, a Typst syntax error ("expected semicolon or line
        # break"); and (b) even a single bare label is a raw label *value*, so
        # joining it into a content block fails ("cannot join content with
        # label"). A `[#metadata(none) <id>]` block is genuine *content* with
        # the label attached, so it joins/concatenates cleanly, works both
        # singly and consecutively, and stays reachable via link(<id>).
        #
        # The surrounding newlines separate this markup block from any adjacent
        # code-mode expression on BOTH sides -- a preceding one
        # (text()/raw()/par()/a prior target) and a following one (e.g. the next
        # `par({...})`) -- which is required inside a `{...}` content block where
        # juxtaposed expressions need a line break between them (`]par(` and
        # `)label(` are both syntax errors otherwise).
        if node.get("ids"):
            label_id = self._namespace_label(self._current_docname(), node["ids"][0])
            self.add_text(f"\n[#metadata(none) <{label_id}>]\n")

        # Mark that next element in list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

        # Skip processing children as target is typically empty
        raise nodes.SkipNode

    def depart_target(self, node: nodes.target) -> None:
        """
        Depart a target node.

        Args:
            node: The target node
        """
        # Target is handled in visit
        pass

    def visit_pending_xref(self, node: nodes.Node) -> None:
        """
        Visit a pending_xref node (Sphinx cross-reference).

        D-04 (Phase 48, ``48-RED-EVIDENCE.md``): Sphinx's
        ``ReferencesResolver`` post-transform (``default_priority=10``,
        supported for every builder) replaces every ``pending_xref`` node
        in the document unconditionally before the writer runs -- so no
        such node survives to this handler through the normal pipeline,
        for any resolution outcome (resolved, unresolved, or unknown role
        all fall back to ``node.replace_self(...)``). This handler is
        applied anyway, as defence in depth: a future Sphinx version or an
        unusual extension interaction is not ruled out by the four source
        shapes measured this session.

        Args:
            node: The pending_xref node
        """
        # pending_xref nodes are typically resolved by Sphinx before reaching the writer
        # If we encounter one, it means resolution failed or we're in a special case
        # We handle it by generating a link to the target

        reftarget = node.get("reftarget", "")
        reftype = node.get("reftype", "")

        if reftarget:
            # Generate a link to the target
            # Sanitize the target for Typst label format. The legacy
            # `.`/`_`->`-` transform is kept for backward compatibility, then
            # routed through _sanitize_label so any remaining Typst-invalid
            # character (e.g. `@`) cannot abort the compile with an unclosed
            # label -- this pending_xref path is only a best-effort fallback
            # for references Sphinx failed to resolve.
            # Unresolved best-effort fallback: assume a same-document target and
            # namespace with the current docname so it matches a same-doc anchor
            # (all real anchors are now docname-namespaced).
            label = self._namespace_label(
                self._current_docname(),
                reftarget.replace(".", "-").replace("_", "-"),
            )
            # D-07: routed through the shared guard as defence in depth
            # (this site is otherwise unreachable, see the docstring
            # above). The `#` prefix below is preserved UNCHANGED from
            # this site's prior unconditional emission -- unlike
            # visit_reference, this handler does not compute a mode-aware
            # prefix (`"#" if self._in_markup_mode else ""`). That was
            # noticed and deliberately left unchanged: D-04's scope is
            # "bring this site under the guard", not "audit it for
            # unrelated mode bugs". The argument rests on research
            # assumption A2 (`48-RESEARCH.md`), which states no
            # third-party extension was observed emitting a fresh
            # `pending_xref` after `ReferencesResolver` runs -- and was
            # NOT independently tested. If A2 is wrong, this fixed `#`
            # prefix may not match the surrounding mode.
            # Children stream into a markup bracket below exactly as
            # before, so the non-code-mode body spelling is used.
            guard = self._label_existence_guard(label, prefix="#")
            self.add_text(guard.open_str)
            self._pending_xref_guard_close = guard.close_str
        # Continue processing children to get the link text

    def depart_pending_xref(self, node: nodes.Node) -> None:
        """
        Depart a pending_xref node.

        Args:
            node: The pending_xref node
        """
        reftarget = node.get("reftarget", "")
        if reftarget and self._pending_xref_guard_close:
            self.add_text(self._pending_xref_guard_close)
            self._pending_xref_guard_close = None

    def _compute_relative_include_path(
        self, target_docname: str, current_docname: str | None
    ) -> str:
        """
        Compute relative path for toctree #include() directive.

        This method calculates the relative path from the current document
        to the target document for use in Typst #include() directives.
        Uses PurePosixPath for OS-independent POSIX path handling.

        Args:
            target_docname: Target document name (e.g., "chapter1/section1")
            current_docname: Current document name (e.g., "chapter1/index"), or None

        Returns:
            Relative path string for #include() (e.g., "section1" or "../chapter2/doc")

        Examples:
            >>> _compute_relative_include_path("chapter1/section1", "chapter1/index")
            "section1"
            >>> _compute_relative_include_path("chapter2/doc", "chapter1/index")
            "../chapter2/doc"
            >>> _compute_relative_include_path("chapter1/doc", None)
            "chapter1/doc"

        Notes:
            This method implements Issue #5 fix for nested toctree relative paths.
            It handles three cases:
            1. current_docname is None: return absolute path
            2. Same directory: use relative_to() directly
            3. Cross-directory: calculate via common parent

        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        from pathlib import PurePosixPath

        logger.debug(
            f"Computing relative include path: target={target_docname}, "
            f"current={current_docname}"
        )

        # Fallback to absolute path if current_docname is None
        if not current_docname:
            logger.debug(f"No current document, using absolute path: {target_docname}")
            return target_docname

        current_path = PurePosixPath(current_docname)
        target_path = PurePosixPath(target_docname)
        current_dir = current_path.parent

        logger.debug(
            f"Path components: current_dir={current_dir}, " f"target_path={target_path}"
        )

        # Root directory case: use absolute path (backward compatibility)
        if current_dir == PurePosixPath("."):
            logger.debug(
                f"Current document is in root directory, "
                f"using absolute path: {target_docname}"
            )
            return target_docname

        # Try to compute relative path
        try:
            rel_path = target_path.relative_to(current_dir)
            result = str(rel_path)
            logger.debug(
                f"Same directory reference: {current_dir} -> {target_path}, "
                f"result: {result}"
            )
            return result
        except ValueError:
            # Different directory trees - build path via common parent
            logger.debug(
                "Cross-directory reference detected, calculating via common parent"
            )

            current_parts = current_dir.parts
            target_parts = target_path.parts

            # Find common parent by comparing path components
            common_length = 0
            for i, (c, t) in enumerate(zip(current_parts, target_parts, strict=False)):
                if c == t:
                    common_length = i + 1
                else:
                    break

            logger.debug(
                f"Common parent depth: {common_length}, "
                f"current_parts={current_parts}, target_parts={target_parts}"
            )

            # Build path: "../" from current to common parent
            up_count = len(current_parts) - common_length
            up_path = "../" * up_count if up_count > 0 else ""

            # Build path: from common parent to target
            down_parts = target_parts[common_length:]
            down_path = "/".join(down_parts) if down_parts else ""

            relative_path: str = up_path + down_path

            logger.debug(
                f"Cross-directory path calculation: up_count={up_count}, "
                f"up_path='{up_path}', down_path='{down_path}', "
                f"result: {relative_path}"
            )

            return relative_path

    def _compute_relative_image_path(
        self, image_uri: str, current_docname: str | None
    ) -> str:
        """
        Compute relative path for image() function.

        Adjusts image URIs from source-root-relative to output-file-relative.
        This is similar to _compute_relative_include_path() but for images.

        Args:
            image_uri: Image URI from Sphinx (source-root-relative)
            current_docname: Current document name (e.g., "chapter1/section1")

        Returns:
            Adjusted relative path for Typst image()

        Examples:
            >>> _compute_relative_image_path("images/logo.png", "chapter1/section1")
            "../images/logo.png"
            >>> _compute_relative_image_path("images/logo.png", "index")
            "images/logo.png"
            >>> _compute_relative_image_path("images/logo.png", None)
            "images/logo.png"

        Notes:
            This implements Issue #69 fix for nested document image paths.
            Uses the same logic as _compute_relative_include_path() from Issue #5.
        """
        from pathlib import PurePosixPath

        logger.debug(
            f"Computing relative image path: uri={image_uri}, "
            f"current={current_docname}"
        )

        # Fallback to absolute path if current_docname is None
        if not current_docname:
            logger.debug(f"No current document, using absolute path: {image_uri}")
            return image_uri

        current_path = PurePosixPath(current_docname)
        image_path = PurePosixPath(image_uri)
        current_dir = current_path.parent

        logger.debug(
            f"Path components: current_dir={current_dir}, image_path={image_path}"
        )

        # Root directory case: use absolute path (backward compatibility)
        if current_dir == PurePosixPath("."):
            logger.debug(
                f"Current document is in root directory, "
                f"using absolute path: {image_uri}"
            )
            return image_uri

        # Try to compute relative path
        try:
            rel_path = image_path.relative_to(current_dir)
            result = str(rel_path)
            logger.debug(
                f"Same directory reference: {current_dir} -> {image_path}, "
                f"result: {result}"
            )
            return result
        except ValueError:
            # Different directory trees - build path via common parent
            logger.debug(
                "Cross-directory reference detected, calculating via common parent"
            )

            current_parts = current_dir.parts
            image_parts = image_path.parts

            # Find common parent by comparing path components
            common_length = 0
            for i, (c, img) in enumerate(zip(current_parts, image_parts, strict=False)):
                if c == img:
                    common_length = i + 1
                else:
                    break

            logger.debug(
                f"Common parent depth: {common_length}, "
                f"current_parts={current_parts}, image_parts={image_parts}"
            )

            # Build path: "../" from current to common parent
            up_count = len(current_parts) - common_length
            up_path = "../" * up_count if up_count > 0 else ""

            # Build path: from common parent to image
            down_parts = image_parts[common_length:]
            down_path = "/".join(down_parts) if down_parts else ""

            relative_path: str = up_path + down_path

            logger.debug(
                f"Cross-directory path calculation: up_count={up_count}, "
                f"up_path='{up_path}', down_path='{down_path}', "
                f"result: {relative_path}"
            )

            return relative_path

    @staticmethod
    def _sanitize_label(name: str) -> str:
        """
        Sanitize a docutils id/name into a valid Typst label token.

        Typst's ``<label>`` anchor syntax, its ``label("...")`` value, and the
        ``link(<label>, ...)`` reference form all accept only a restricted
        character set for the label NAME. Empirically (typst 0.15) the only
        characters valid inside a ``<...>`` label are ``[A-Za-z0-9_.:-]``;
        every other character (notably ``@``, but also ``/ + # * ? ! ~ % & =``
        whitespace, brackets, quotes, etc.) makes Typst fail to close the
        label with ``error: unclosed label``, which aborts the ENTIRE compile.

        Docutils/Sphinx ids can contain such characters. In particular
        Sphinx's C-domain anonymous entities (``@data`` / ``@alias``) produce
        ids like ``c.Data.@data.a`` -- the ``@`` is what triggered the corpus
        ``unclosed label`` fatal. This helper maps every character outside the
        valid set to a collision-resistant token ``_u{codepoint:x}_`` (e.g.
        ``@`` -> ``_u40_``). That encoding:

        - uses only characters valid in a Typst label (``_``, digits, letters),
          and is safe as a leading character (starts with ``_``);
        - is deterministic and injective on the offending character (distinct
          characters map to distinct codepoint tokens), so it is collision-
          resistant -- unlike replacing every invalid char with a bare ``_``,
          which would collide ``a@b`` with ``a?b``;
        - leaves ids that are ALREADY valid byte-for-byte unchanged, so the
          vast majority of existing anchors/links (which already compile) are
          not churned and keep their exact current names.

        CRITICAL CORRECTNESS PROPERTY: this must be applied at every site that
        emits a label NAME -- both where a label is DEFINED (anchors,
        ``label("...")``) and where it is REFERENCED (``link(<...>, ...)``,
        ``footnote(<...>)``) -- so a definition and its reference sanitize to
        the SAME string and cross-references keep resolving.

        INJECTIVITY (Phase 55, XREF-05, D-01/D-02): the encoder's own token
        alphabet (``_u{codepoint:x}_``) is a SUBSET of its own safe character
        set, so a raw input that already spells that token shape passes
        through the main substitution below untouched -- two DIFFERENT raw
        inputs can then collapse onto the SAME label (e.g. docname ``a/b``
        and docname ``a_u2f_b`` both namespace-and-sanitize to
        ``a_u2f_b:nested-target``). Protecting only COMPLETE literal tokens
        present in the raw input is not enough, because the main substitution
        itself creates NEW token-shaped runs at the seam between literal text
        and an emitted token -- two constructions that tried this were
        measured non-injective this phase: doubling a literal token's leading
        underscore collides ``a_/b`` with ``a_u2f_b`` (both become
        ``a__u2f_b``), and inserting an extra ``u`` collides ``_u2f/`` with
        ``/u2f_`` (both become ``_u2f_u2f_``). The construction below instead
        escapes the run's own INTRODUCING underscore -- via the module-level
        ``_LABEL_TOKEN_INTRODUCER_RE`` pre-pass, run BEFORE the main
        substitution -- with the replacement ``_u5f_``, which is precisely
        what the encoder itself emits for a literal underscore (``ord("_")``
        is ``0x5f``), so no new escaping primitive is introduced. This is
        verified injective by an exhaustive decoder round-trip in
        ``tests/test_sanitize_label_injectivity_unit.py`` (the Pitfall-3
        proof obligation for this construction), over an exhaustive alphabet
        plus 400,000 random strings; see also ``55-01-RED-EVIDENCE.md``.

        Args:
            name: A docutils id/name (or a derived label such as ``fn-<id>``).

        Returns:
            The same string with every Typst-label-invalid character replaced
            by a ``_u{codepoint:x}_`` token, and every literal occurrence of
            the encoder's own token-introducing underscore re-escaped first.
        """
        name = _LABEL_TOKEN_INTRODUCER_RE.sub("_u5f_", name)
        return re.sub(
            r"[^A-Za-z0-9_.:-]",
            lambda m: f"_u{ord(m.group(0)):x}_",
            name,
        )

    def _current_docname(self) -> str | None:
        """Return the docname currently being written, or ``None``.

        The builder sets ``current_docname`` in ``write_doc`` before the
        translator runs. Hand-built test doctrees may have no builder docname;
        callers fall back to a bare (un-namespaced) label in that case.
        """
        return getattr(self.builder, "current_docname", None)

    def _namespace_label(self, docname: str | None, raw_id: str) -> str:
        """Namespace a docutils id/name by its owning document, then sanitize.

        The whole corpus is flattened into ONE Typst master via ``#include()``
        (each source doc becomes a ``.typ`` the master includes), but docutils
        ids are unique only WITHIN a document -- two different documents can
        carry the SAME section slug (e.g. ``info-field-lists``). Emitted as a
        bare ``<info-field-lists>`` twice, that is a duplicate Typst label, and
        the compile aborts at the semantic pass with ``label ... occurs
        multiple times`` as soon as anything references it.

        To keep every label unique per compiled master, every DEFINITION site
        (anchors, ``label("...")``, ``<label>`` postfixes, footnote labels)
        prefixes the SOURCE ``docname``; every REFERENCE site
        (``link(<...>, ...)``) recomputes the SAME namespace from its target's
        docname -- the current docname for a same-document reference, the
        TARGET docname (parsed from the cross-document refuri) for a
        cross-document reference -- so a link still lands on exactly the right
        anchor. Since the ``docname:id`` string is built identically on both
        sides and then run through the same ``_sanitize_label`` (docnames'
        ``/`` -> ``_u2f_``, ``:`` is label-valid and preserved), a definition
        and its reference always byte-match.

        A ``None`` docname (hand-built test doctrees with no builder docname)
        falls back to a bare sanitized label so those paths stay unchanged and
        internally consistent (every site sees the same ``None``).

        Args:
            docname: The owning document's name, or ``None``.
            raw_id: A docutils id/name (or a derived label such as ``fn-<id>``).

        Returns:
            A Typst-valid, per-document-unique label token.
        """
        if docname:
            return self._sanitize_label(f"{docname}:{raw_id}")
        return self._sanitize_label(raw_id)

    def _resolve_xref_docname(self, refuri: str) -> Tuple[str, str] | None:
        """Resolve a LOCAL cross-document refuri to ``(target_docname, anchor)``.

        Sphinx's reference resolver renders a resolved cross-document
        ``pending_xref`` as a ``reference`` whose refuri is
        ``<relative-path><out_suffix>#<anchor>`` (e.g.
        ``../domains/python.typ#info-field-lists`` relative to the current
        document's output path). This inverts that: it joins the relative path
        onto the current document's output URI, strips the builder's
        ``out_suffix``, and returns the target docname plus the anchor -- so the
        reference can be namespaced with the TARGET docname and thus match the
        anchor that target document emits.

        Returns ``None`` (leaving the caller to render a plain
        ``link("url", ...)``) for:

        - external URLs (any ``scheme://`` or ``mailto:`` / protocol-relative);
        - same-document ``#anchor`` refs (handled earlier by the caller --
          these have an empty ``path_part``, since the caller strips the
          leading ``#`` before ever consulting this method);
        - refuris whose path does not end in the builder's ``out_suffix``
          (arbitrary relative asset links), or when the current docname is
          unknown.

        A LOCAL whole-document refuri with no ``#anchor`` fragment (or an
        explicit but empty one, e.g. ``path.typ#``) resolves too (G-48-4 /
        XREF-03, Phase 48 plan 07): the SAME path arithmetic the anchored
        case uses, returned with an EMPTY anchor (``(target_docname,
        "")``) rather than ``None`` -- the caller (``_reference_anchor_
        decision``) is the single place that decides whether an empty-anchor
        resolution is actually exposed through its own ``.xref`` field; this
        method answers only "which document and which anchor", never policy.
        """
        if "://" in refuri or refuri.startswith(("mailto:", "//")):
            return None
        path_part, _, anchor = refuri.partition("#")
        if not path_part:
            return None
        suffix = getattr(self.builder, "out_suffix", "")
        if not suffix or not path_part.endswith(suffix):
            return None
        current = self._current_docname()
        if not current:
            return None
        import posixpath

        current_uri = self.builder.get_target_uri(current)
        base_dir = posixpath.dirname(current_uri)
        target_uri = posixpath.normpath(posixpath.join(base_dir, path_part))
        target_docname = target_uri[: -len(suffix)]
        return target_docname, anchor

    def _convert_length_to_typst(self, value: str) -> str | None:
        """
        Convert a docutils-normalized CSS length string to a Typst-valid length.

        Docutils' `length_or_percentage_or_unitless`/`length_or_unitless` option
        converters (see docutils/parsers/rst/directives/__init__.py) normalize
        `:width:`/`:height:` into a single "<value><unit>" string with no space
        (e.g. "200px", "50%", "300" for bare unitless). This helper rewrites
        that string into one Typst's length grammar accepts, or returns None if
        the unit cannot be represented (caller should then omit the attribute
        entirely, letting the image render at its natural size).

        Args:
            value: Docutils-normalized length string (e.g. "200px", "50%", "300").

        Returns:
            A Typst-valid length string, or None if the unit is unsupported.

        Examples:
            >>> _convert_length_to_typst("200px")
            "150pt"
            >>> _convert_length_to_typst("300")
            "225pt"
            >>> _convert_length_to_typst("50%")
            "50%"
            >>> _convert_length_to_typst("1pc")
            "12pt"
            >>> _convert_length_to_typst("2ex")
            None

        Notes:
            Implements Issue #114 (FIG-01) per the locked D-02 decision: px
            converts via the CSS-canonical 1px = 0.75pt; pc converts to pt
            (1pc = 12pt); %/em/pt/cm/mm/in pass through unchanged; any other
            unit (ex, ch, rem, vw, vh, vmin, vmax, Q, etc.) is unknown and is
            dropped with exactly one warning rather than emitted verbatim,
            which was the FIG-01 fatal Typst-compile-abort case.
        """
        match = re.fullmatch(r"(-?[0-9.]+)([a-zA-Zµ%]*)", value)
        if not match:
            logger.warning(f"Could not parse length value '{value}'; dropping.")
            return None

        number_str, unit = match.group(1), match.group(2)
        number = float(number_str)

        if unit == "" or unit == "px":
            # CSS canonical: 96px/in, 72pt/in -> 1px = 0.75pt
            return f"{number * 0.75:g}pt"
        if unit == "pc":
            return f"{number * 12:g}pt"  # 1 pica = 12 points
        if unit in _TYPST_PASSTHROUGH_UNITS:
            return value  # already Typst-valid, pass through unchanged

        logger.warning(
            f"Unsupported length unit '{unit}' in '{value}'; "
            "dropping dimension (image will use its natural size)."
        )
        return None

    def visit_toctree(self, node: nodes.Node) -> None:
        """
        Visit a toctree node (Sphinx table of contents tree).

        Requirement 13: Multi-document integration and toctree processing
        - Generate a compile-time state guard for each include-file entry
          (Phase 49, COMP-05/COMP-06 -- see below)
        - D-07: apply `set heading(offset: heading.offset + 1)` -- a
          context-relative increment, not an absolute assignment -- to
          lower heading levels. `set` is an absolute assignment on Typst's
          style chain, so a nested toctree scope would otherwise *replace*
          its parent's offset instead of adding to it, and nested toctrees
          would not compose. An included document's `.typ` is also a
          single shared file that different masters may include at
          different depths, so no single absolute value could be correct
          at every include site; a relative expression evaluated at
          layout time removes the need for one to exist.
        - Issue #5: Fix relative paths for nested toctrees
          - Calculate relative paths from current document
        - Issue #7: Simplify toctree output with single content block
          - Generate single #[...] block containing all guards
          - D-07: apply `heading.offset + 1` once per toctree, inside a
            `context { ... }` block (required because `heading.offset` is
            a context-dependent style query)

        Phase 49 (COMP-05/D-03): reads the toctree's INCLUDE-FILE list
        (`node["includefiles"]`), never its entry list
        (`node["entries"]`). Sphinx's own `parse_content` appends a
        `self`/external-URL entry only to `entries`, never to
        `includefiles` (`sphinx/directives/other.py:146-149`), so those
        entries produce no guard here at all -- closing the
        `TypstError: file not found (searched at .../self.typ)` compile
        fatal as a structural consequence of reading the right list, not a
        separate patch.

        Args:
            node: The toctree node

        Notes:
            This method generates Typst #include() directives for each toctree entry
            within a single content block #[...] to apply heading offset without
            displaying the block delimiters in the output. This simplifies the
            generated Typst code and improves readability.

            Phase 49: each `#include()` directive is now wrapped in its own
            one-line compile-time guard (`render_include_guard()`), still
            emitted within that same single content block, rather than as
            an unconditional call.
        """
        # Phase 49 (D-03): read the include-file list, not the entry list.
        includefiles = node.get("includefiles", [])

        logger.debug(f"Processing toctree with {len(includefiles)} include files")

        # If no include files, don't generate anything. A toctree whose
        # entries are all navigation constructs (self/external-URL) has a
        # non-empty `entries` list but an EMPTY `includefiles` list here --
        # this is the D-03 shift that makes such a toctree emit no
        # `context { ... }` block at all, rather than an empty one.
        if not includefiles:
            logger.debug("Toctree has no include files, skipping")
            raise nodes.SkipNode

        # Get current document name for relative path calculation
        current_docname = getattr(self.builder, "current_docname", None)

        logger.debug(
            f"Current document for toctree: {current_docname}, "
            f"include files: {includefiles}"
        )

        # Generate scope block for all guards (unified code mode)
        # Use {...} scope block to isolate set rules while maintaining code mode
        # D-07: `context` is required because `heading.offset` is a
        # context-dependent style query -- `set` alone cannot read the
        # ambient offset it is about to modify. This is a relative
        # increment, not an absolute assignment, so nested toctree scopes
        # accumulate instead of replacing their parent's offset.
        # Start scope block (no # prefix in code mode)
        self.add_text("context {\n")
        self.add_text("  set heading(offset: heading.offset + 1)\n")

        # Phase 49 (COMP-05/COMP-06): the include DECISION moves from
        # write time to Typst COMPILE time. A single content file, written
        # ONCE per docname, cannot both omit and emit the same include for
        # two different masters that each legitimately reach it via their
        # own, independent traversal -- the deleted build-scoped
        # include-dedup ledger attribute (COMP-11), which claimed a
        # docname globally, the first time ANY document's toctree named
        # it, could therefore express only ONE global winner across the
        # whole build, never a per-master answer. Every emission site below instead
        # emits a STATIC compile-time guard, unconditionally: each
        # wrapper (`writer.py`'s `render_wrapper()`) publishes ITS OWN
        # master's derived edge set as a Typst `state` array BEFORE
        # `#include()`-ing this content file, and the guard reads that
        # published state at compile time to decide whether THIS
        # PARTICULAR master's own traversal claimed this child.
        for docname in includefiles:
            # D-04: the occurrence is a per-DOCUMENT counter, keyed by
            # child docname, across ALL of this document's own toctree
            # entries (flattened in document order, mirroring
            # `env.toctree_includes[docname]`) -- not reset per
            # `.. toctree::` directive.
            occurrence = self._toctree_entry_occurrences.get(docname, 0)
            self._toctree_entry_occurrences[docname] = occurrence + 1

            edge_key = make_include_edge_key(
                current_docname or "", docname, occurrence=occurrence
            )

            # Compute relative path for include() (Issue #5 fix) -- this
            # helper survives Phase 49 completely unchanged.
            relative_path = self._compute_relative_include_path(
                docname, current_docname
            )

            logger.debug(
                f"Generated guard for toctree: {docname} -> {relative_path}.typ "
                f"(edge_key={edge_key!r})"
            )

            # Generate the guard line within the block (no # prefix in
            # code mode -- this site is always reached from code mode,
            # see render_include_guard()'s own docstring).
            self.add_text("  " + render_include_guard(edge_key, relative_path) + "\n")

        # End scope block
        self.add_text("}\n\n")

        # Skip processing children as we've handled the toctree entries
        raise nodes.SkipNode

    def depart_toctree(self, node: nodes.Node) -> None:
        """
        Depart a toctree node.

        Args:
            node: The toctree node
        """
        # Toctree is handled in visit
        pass

    def visit_reference(self, node: nodes.reference) -> None:
        """
        Visit a reference node (link).

        Generates link() function call (no # prefix in code mode).

        Args:
            node: The reference node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # WR-03 (D-05/D-06/D-07, `40.1-CONTEXT.md`): the single shared D-14
        # eligibility judgement, called ONCE here and consumed for
        # `refuri`/`refid`/`xref`/`opens_wrapper`/`next_is_target`/the D-14
        # guard below -- this method no longer re-derives any of them
        # locally, so this call site and `visit_citation`'s backref loop
        # cannot silently disagree about whether a citing site was
        # actually anchored (`40.1-GATE-EVIDENCE-03.md`). D-09 (Phase 48):
        # `opens_wrapper` is unconditional now -- no build-time degrade
        # decision is derived here any more.
        decision = self._reference_anchor_decision(node)
        refuri = decision.refuri
        refid = decision.refid
        xref = decision.xref

        # An empty-url reference (no refuri and no refid) opens NO wrapper: it
        # renders its children as plain inline content directly in the outer
        # context, so it must NOT enter/suppress a concat context (its children
        # participate in that context themselves). Every wrapper-opening path
        # (same-doc refid, internal #label, external URL) DOES enter: a link
        # that is a non-first sibling in a code-mode concat context (def-list
        # term / link body / desc parameter) is + separated, and that outer
        # context is suppressed for the link body -- handled by the link's own
        # _in_link context -- so no stray '+' leaks inside link(...).
        #
        # Concat/newline mutual exclusion (bug #9): capture whether a code-mode
        # concat context is active BEFORE _enter_inline_concat_element suppresses
        # its flag. Inside a concat context the '+' operator IS the separator, so
        # the list-item newline must NOT also fire -- otherwise a wrapper-opening
        # reference that is the first parameter emits
        #   text("(") +  <newline>  link(...)
        # stranding the '+' at end-of-line (no right operand) -> 'expected
        # expression'. Every other inline visitor (visit_Text / visit_literal /
        # visit_strong / visit_emphasis) already guards its newline this way; do
        # the same here rather than emitting the newline unconditionally.
        in_concat = self._inline_concat_context() is not None
        opens_wrapper = decision.opens_wrapper
        if opens_wrapper:
            self._enter_inline_concat_element()

        # Add list-item newline separator only when NOT in a concat context
        # (mutually exclusive with the concat '+' separator emitted above).
        if not in_concat and self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Whether the next sibling is a target node (for label attachment).
        # Needed in both list items and paragraphs in unified code mode, AND
        # by the D-14 guard just below -- both consumers read the SAME
        # `decision.next_is_target` value, computed once inside the shared
        # predicate (Pitfall 3, `40.1-RESEARCH.md`).
        next_is_target = decision.next_is_target

        # D-14 (Phase 40): give a citation-derived reference its own anchor so
        # a citation definition's back-reference marker (`visit_citation`)
        # has something to link to. `decision.eligible`/`decision.
        # anchor_label` are the SAME predicate `visit_citation`'s backref
        # loop consults (WR-03, `40.1-GATE-EVIDENCE-03.md`) -- applies only
        # when ALL of: the reference carries a non-empty own `ids` (verified
        # this session, 40-RESEARCH.md -- only citation-derived references
        # carry a populated `ids`; a `:ref:` or toctree-generated reference
        # carries `ids=[]`), a link wrapper is actually being opened, and
        # next is NOT a target. Mutually exclusive with next_is_target BY
        # DESIGN: next_is_target already owns the markup-mode bracket and
        # visit_target already attaches ITS OWN label to it -- a Typst
        # element can carry only one label. Consequence, stated honestly: a
        # citation-derived reference immediately followed by an explicit
        # target keeps the target's label and gets no back-reference anchor
        # of its own; visit_citation guards its own marker emission against
        # exactly this case via the same `decision.eligible`.
        self._reference_own_anchor = None
        if decision.eligible:
            self._reference_own_anchor = decision.anchor_label
            self.add_text("[")
            self._in_markup_mode = True

        # If next is target, wrap in markup mode for label attachment
        # In unified code mode, labels can only attach in markup mode blocks [...]
        if next_is_target:
            self.add_text("[")
            self._in_reference_with_target = True
            self._in_markup_mode = (
                True  # Enter markup mode - need # prefix for functions
            )

        # Save and reset list item separator for children (they're inside this element)
        was_list_item_needs_separator = self.list_item_needs_separator
        self.list_item_needs_separator = False

        # Internal same-document :target: (e.g. a figure/image target)
        # resolves to an empty/absent refuri with a populated refid instead
        # of a "#"-prefixed refuri. Handle it before the empty-URL guard so
        # it doesn't fall through to the plain-text fallback (FIG-02, D-03).
        if not refuri and refid:
            prefix = "#" if self._in_markup_mode else ""
            # A bare refid is a SAME-document target -> namespace with the
            # current docname so it matches the anchor that document emitted.
            label = self._namespace_label(self._current_docname(), refid)
            # SC#4/D-06 (Phase 48): deliberately UNGUARDED. Content files
            # are included wholesale (COMP-01), so a same-document
            # target's presence is guaranteed -- this branch stays on the
            # plain `link(<label>, ` form, never the D-07 guard.
            self.add_text(f"{prefix}link(<{label}>, ")

            # Replicate the method-end bookkeeping inline since this branch
            # returns early (mirrors the refuri branches below).
            if self._in_markup_mode:
                self._in_markup_mode = False
            self._in_link = True
            self._link_has_content = False
            self._reference_was_list_item_needs_separator = (
                was_list_item_needs_separator
            )
            return

        # Handle empty URLs (Typst 0.14+ rejects empty URLs)
        # This can occur with unresolved references, broken cross-references,
        # or malformed reStructuredText. Instead of generating invalid link("", ...),
        # we skip the link wrapper and render content as plain text.
        if not refuri:
            logger.warning(
                f"Reference node has empty URL. "
                f"Link will be rendered as plain text. "
                f"Check for broken references in source: {node.astext()}"
            )
            self._skip_link_wrapper = True
            return

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Check if it's an internal reference (starts with #)
        if refuri.startswith("#"):
            # Internal reference to a label in the SAME document -> namespace
            # with the current docname so it matches this document's anchor.
            label = self._namespace_label(self._current_docname(), refuri[1:])
            # SC#4/D-06 (Phase 48): deliberately UNGUARDED, same rationale
            # as the bare-refid branch above -- content files are included
            # wholesale, so a same-document target's presence is guaranteed.
            self.add_text(f"{prefix}link(<{label}>, ")
        elif xref is not None:
            # Resolved CROSS-document reference (`<relpath><out_suffix>#anchor`).
            # D-07/XREF-03 (Phase 48): whether the target document is part
            # of THIS compiled wrapper's include graph is no longer a
            # build-time Python decision (the deleted all-masters union) --
            # it is decided by Typst itself, per compile, via a
            # `query(<label>)` guard around the link. Namespace with the
            # TARGET docname so the guarded label byte-matches the anchor
            # the target document emits.
            #
            # G-48-4 (Phase 48 plan 07): an EMPTY anchor means this is a
            # WHOLE-DOCUMENT reference (`_resolve_xref_docname` found no
            # single anchor to target, and `_reference_anchor_decision`'s
            # `_whole_document_reference_eligible` gate already confirmed
            # it is eligible) -- it targets the target document's own
            # whole-document self-anchor (the module-level
            # `_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN`, emitted once per content
            # file by `visit_document`) instead of a specific anchor.
            target_docname, anchor = xref
            label = self._namespace_label(
                target_docname, anchor or _WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN
            )
            guard = self._label_existence_guard(
                label, prefix=prefix, code_mode_body=True
            )
            self.add_text(guard.open_str)
            self._reference_guard_close = guard.close_str
        else:
            # External reference (HTTP/HTTPS URL, whole-document ref, or other
            # relative path) -> plain string-url link, left unaffected.
            self.add_text(f'{prefix}link("{refuri}", ')

        # After outputting link()/the guard's open string, turn off markup
        # mode for content (the body). Content inside function arguments
        # or the guard's code-mode body is code mode (no # prefix).
        if self._in_markup_mode:
            self._in_markup_mode = False

        # Mark that we're inside link() to use + for concatenation
        self._in_link = True
        self._link_has_content = False

        # Store state to restore in depart
        self._reference_was_list_item_needs_separator = was_list_item_needs_separator

    def depart_reference(self, node: nodes.reference) -> None:
        """
        Depart a reference node.

        Args:
            node: The reference node
        """
        # Skip link wrapper closing if we skipped it in visit
        if getattr(self, "_skip_link_wrapper", False):
            self._skip_link_wrapper = False
            # D-14 (Phase 40): defensively clear the anchor slot here too.
            # This branch is only reachable on a path where opens_wrapper was
            # False, so visit_reference's D-14 guard never set the slot on
            # THIS node -- but clearing it unconditionally is cheap insurance
            # against a stale token leaking into the NEXT reference.
            self._reference_own_anchor = None
            # D-07 (Phase 48): defensively clear the guard-close slot too,
            # for the same reason -- this branch is unreachable from the
            # guarded cross-document path, but a stale token must never
            # leak into the NEXT reference.
            self._reference_guard_close = None
            # Restore list item separator state if needed
            if hasattr(self, "_reference_was_list_item_needs_separator"):
                if self.in_list_item:
                    self.list_item_needs_separator = True
                delattr(self, "_reference_was_list_item_needs_separator")
            return

        # Close the link function -- or, on the guarded cross-document
        # path, the D-07 guard's close string (`_label_existence_guard()`'s
        # `close_str`, stashed in visit_reference) IN PLACE OF the plain
        # closing parenthesis. Emitted FIRST, before the D-14 own-anchor
        # block below, so the whole `context { ... }` block is complete
        # before `#label("...")]` attaches -- the own-anchor label lands
        # OUTSIDE the guard's context block, attached to the block's
        # result rather than to the `let`-bound body (48-EVIDENCE.md's
        # Body-mode measurement, own-anchor composition probe).
        if self._reference_guard_close:
            self.add_text(self._reference_guard_close)
            self._reference_guard_close = None
        else:
            self.add_text(")")

        # Exit link context
        self._in_link = False

        # D-14 (Phase 40): close the own-ids bracket-wrap opened in
        # visit_reference, if any -- mirrors visit_target's own
        # `#label("...")` + "]" closing form for the next_is_target case
        # (the same markup-mode bracket mechanism, just closed here instead
        # of by a following target sibling).
        if self._reference_own_anchor:
            self.add_text(f'#label("{self._reference_own_anchor}")]')
            self._reference_own_anchor = None

        # Restore the outer code-mode concat context suppressed for the link
        # body (entered only on wrapper-opening paths, so the skip-wrapper
        # branch above returns before this) and mark the link as a sibling so
        # the next term/link/desc expression is + separated.
        self._exit_inline_concat_element()

        # Restore and mark that next element needs separator
        if hasattr(self, "_reference_was_list_item_needs_separator"):
            if self.in_list_item:
                self.list_item_needs_separator = True
            delattr(self, "_reference_was_list_item_needs_separator")

    def unknown_visit(self, node: nodes.Node) -> None:
        """
        Handle unknown nodes during visit.

        Args:
            node: The unknown node
        """
        # Log a warning for unknown nodes but don't raise an exception
        from sphinx.util import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"unknown node type: {node}")

    def unknown_departure(self, node: nodes.Node) -> None:
        """
        Handle unknown nodes during departure.

        Args:
            node: The unknown node
        """
        # Silently ignore unknown departures
        pass

    def _convert_latex_to_typst(self, latex_content: str) -> str:
        """
        Convert LaTeX math syntax to Typst native syntax.

        Implements Task 6.5: Basic LaTeX to Typst conversion
        Requirement 4.9: Fallback when typst_use_mitex=False

        Args:
            latex_content: LaTeX math content

        Returns:
            Typst native math content
        """
        # Basic conversion rules for common LaTeX commands
        result = latex_content

        # Greek letters: \alpha -> alpha, \beta -> beta, etc.
        greek_letters = [
            "alpha",
            "beta",
            "gamma",
            "delta",
            "epsilon",
            "zeta",
            "eta",
            "theta",
            "iota",
            "kappa",
            "lambda",
            "mu",
            "nu",
            "xi",
            "omicron",
            "pi",
            "rho",
            "sigma",
            "tau",
            "upsilon",
            "phi",
            "chi",
            "psi",
            "omega",
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
            "Epsilon",
            "Zeta",
            "Eta",
            "Theta",
            "Iota",
            "Kappa",
            "Lambda",
            "Mu",
            "Nu",
            "Xi",
            "Omicron",
            "Pi",
            "Rho",
            "Sigma",
            "Tau",
            "Upsilon",
            "Phi",
            "Chi",
            "Psi",
            "Omega",
        ]
        for letter in greek_letters:
            result = result.replace(f"\\{letter}", letter)

        # Fractions: \frac{a}{b} -> frac(a, b)
        result = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"frac(\1, \2)", result)

        # Sum: \sum_{lower}^{upper} -> sum_(lower)^upper
        result = re.sub(r"\\sum_\{([^}]+)\}\^\{([^}]+)\}", r"sum_(\1)^(\2)", result)
        result = re.sub(r"\\sum_\{([^}]+)\}", r"sum_(\1)", result)
        result = result.replace(r"\sum", "sum")

        # Integral: \int_{lower}^{upper} -> integral_(lower)^upper
        result = re.sub(
            r"\\int_\{([^}]+)\}\^\{([^}]+)\}", r"integral_(\1)^(\2)", result
        )
        result = re.sub(r"\\int_\{([^}]+)\}", r"integral_(\1)", result)
        result = result.replace(r"\int", "integral")

        # Product: \prod -> product
        result = result.replace(r"\prod", "product")

        # Square root: \sqrt{x} -> sqrt(x)
        result = re.sub(r"\\sqrt\{([^}]+)\}", r"sqrt(\1)", result)

        # Infinity: \infty -> infinity
        result = result.replace(r"\infty", "infinity")

        # Partial derivative: \partial -> diff (Typst uses diff or ∂)
        result = result.replace(r"\partial", "diff")

        # Common functions
        result = result.replace(r"\sin", "sin")
        result = result.replace(r"\cos", "cos")
        result = result.replace(r"\tan", "tan")
        result = result.replace(r"\log", "log")
        result = result.replace(r"\ln", "ln")
        result = result.replace(r"\exp", "exp")

        # If there are still backslashes, warn about unconverted syntax
        if "\\" in result:
            logger.warning(
                f"LaTeX math contains commands that may not convert well to Typst: {latex_content}"
            )

        return result

    def visit_math(self, node: nodes.math) -> None:
        """
        Visit an inline math node.

        Implements Task 6.2: LaTeX math conversion (mitex)
        Implements Task 6.3: Labeled equations
        Implements Task 6.4: Typst native math support
        Implements Task 6.5: Math fallback functionality
        Requirement 4.3: Inline math should use #mi(`...`) format (LaTeX)
        Requirement 4.9: Fallback when typst_use_mitex=False
        Requirement 5.2: Inline math should use $...$ format (Typst native)
        Requirement 4.7: Labeled equations should generate <eq:label> format
        Design 3.3: Support both mitex and Typst native math
        MATH-01 (backlog 999.1): participates in all three separator
        protocols -- paragraph, code-mode inline concat, and list-item --
        exactly as visit_literal does, so math is never juxtaposed against
        a preceding sibling with zero separator characters.

        Args:
            node: The inline math node
        """
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # Add separator before the mi(...)/$...$ expression.
        # In a code-mode concat context (def-list term / link body / desc
        # parameter), adjacent inline expressions must be + concatenated
        # (except the first); otherwise a list item uses a newline separator.
        # Shared with visit_Text / visit_literal via the concat helpers
        # (single source of truth), so math that is a term/link/desc
        # sibling is + separated.
        if not self._emit_inline_concat_separator():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        # Extract math content
        math_content = node.astext()

        # Task 6.4: Check if this is explicitly marked as Typst native
        is_typst_native = "typst-native" in node.get("classes", [])

        # Task 6.5: Check typst_use_mitex config (default to True)
        use_mitex = getattr(self.builder.config, "typst_use_mitex", True)

        if is_typst_native or not use_mitex:
            # Requirement 5.2: Typst native inline math syntax
            # Task 6.5: Convert LaTeX to Typst if use_mitex=False
            if not is_typst_native and not use_mitex:
                # Convert LaTeX syntax to Typst native
                math_content = self._convert_latex_to_typst(math_content)
            self.add_text(f"${math_content}$")
        else:
            # Requirement 4.3: LaTeX math via mitex (no # prefix in code mode)
            self.add_text(f"mi(`{math_content}`)")

        # Task 6.3: Add label if present
        if "ids" in node and node["ids"]:
            label = self._namespace_label(self._current_docname(), node["ids"][0])
            self.add_text(f" <{label}>")

        # Mark that content was added / next element needs a separator
        if not self._mark_inline_concat_content():
            if self.in_list_item:
                self.list_item_needs_separator = True

        # Skip children to prevent duplicate output of math content
        raise nodes.SkipNode

    def depart_math(self, node: nodes.math) -> None:
        """
        Depart an inline math node.

        Args:
            node: The inline math node
        """
        # No additional output needed
        pass

    def visit_math_block(self, node: nodes.math_block) -> None:
        """
        Visit a block math node.

        Implements Task 6.2: LaTeX math conversion (mitex)
        Implements Task 6.3: Labeled equations
        Implements Task 6.4: Typst native math support
        Implements Task 6.5: Math fallback functionality
        Requirement 4.2: Block math should use #mitex(`...`) format (LaTeX)
        Requirement 4.9: Fallback when typst_use_mitex=False
        Requirement 5.2: Block math should use $ ... $ format (Typst native)
        Requirement 4.7: Labeled equations should generate <eq:label> format
        Design 3.3: Support both mitex and Typst native math
        MATH-01 / D-01 (backlog 999.1): participates in the list-item
        separator protocol (display math shares the inline defect's root
        cause and was brought into scope by explicit owner decision) -- it
        is never a concat-context sibling, so only the in_list_item half
        of the pattern applies.

        Args:
            node: The block math node
        """
        # Anchor node["ids"] (a ``:label:`` equation id such as
        # ``equation-euler``, or a propagated ``.. _t:`` target before the
        # ``.. math::``) via the shared markup-block helper, BEFORE the
        # equation. This REPLACES the old ` <label>` postfix (removed below):
        # a bare ` <label>` after a code-mode ``$ ... $`` / ``mitex(...)``
        # expression does not parse ("expected semicolon or line break") and
        # aborts the compile. A same-document ``:eq:``/``:ref:`` renders
        # link(<id>, ...) and resolves to this anchor. No ids -> no-op.
        self._emit_id_anchors(node)

        # List-item separator only -- math_block is a block-level node and
        # is never a sibling inside one of the five code-mode concat
        # contexts, so the shared inline-concat separator helper is
        # intentionally not called here (that would wrongly emit a `+`
        # operator around a block expression). Placed AFTER
        # _emit_id_anchors, which drives this same separator bookkeeping
        # itself when it emits an anchor -- a guard placed before it would
        # double-separate.
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Extract math content
        math_content = node.astext()

        # Task 6.4: Check if this is explicitly marked as Typst native
        is_typst_native = "typst-native" in node.get("classes", [])

        # Task 6.5: Check typst_use_mitex config (default to True)
        use_mitex = getattr(self.builder.config, "typst_use_mitex", True)

        if is_typst_native or not use_mitex:
            # Requirement 5.2: Typst native block math syntax
            # Task 6.5: Convert LaTeX to Typst if use_mitex=False
            if not is_typst_native and not use_mitex:
                # Convert LaTeX syntax to Typst native
                math_content = self._convert_latex_to_typst(math_content)
            self.add_text(f"$ {math_content} $")
        else:
            # Requirement 4.2: LaTeX math via mitex (no # prefix in code mode)
            self.add_text(f"mitex(`{math_content}`)")

        # Task 6.3: the equation label/id is anchored by _emit_id_anchors above
        # (a code-mode ` <label>` postfix on the equation failed to parse).
        self.add_text("\n\n")

        # MATH-02 (Phase 34 review finding WR-01, Phase 36): unlike every
        # other block-level handler, this method already emitted its own
        # unconditional "\n\n" separator above -- so it must CLEAR the
        # shared flag rather than arm it. Arming it here stacked a second
        # separator on top of one already emitted, producing a redundant
        # extra blank line after block math inside a list item. Clearing
        # (rather than merely not setting) is required for the ``:label:``
        # path: `_emit_id_anchors` sets the flag to True BEFORE the math is
        # emitted, so this statement must run unconditionally afterward to
        # overwrite that state -- one statement covers both the plain and
        # the labelled forms, on both the mitex and native emission paths.
        if self.in_list_item:
            self.list_item_needs_separator = False

        # Skip children to prevent duplicate output of math content
        raise nodes.SkipNode

    def depart_math_block(self, node: nodes.math_block) -> None:
        """
        Depart a block math node.

        Args:
            node: The block math node
        """
        # No additional output needed
        pass

    # Admonition nodes (Task 3.4)
    # Requirement 2.8-2.10: Convert Sphinx admonitions to gentle-clues

    def _visit_admonition(
        self, node: nodes.Node, clue_type: str, custom_title: str = None
    ) -> None:
        """
        Helper method to visit any admonition node.

        Opens a code-mode content-block call (`clue_type({`) so the body
        (paragraphs/text/literals emitted downstream as `par({...})`,
        `text(...)`, `raw(...)`) evaluates instead of printing as literal
        Typst source. A title child, if present, is not read here — docutils
        will visit it normally via visit_title's admonition-aware branch,
        which defers the rendered title to `_depart_admonition`.

        Args:
            node: The admonition node
            clue_type: The gentle-clues function name (e.g., 'info', 'warning', 'tip')
            custom_title: Optional static custom title for the admonition
        """
        # A propagated explicit target can land its id on this admonition
        # (note/warning/generic/topic); anchor it so a same-document
        # link(<id>, ...) resolves (no ids -> no-op).
        self._emit_id_anchors(node)

        # Add newline separator if in list item and not first element
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

        # Reset per-admonition title state; stash the static custom title (if
        # any) for _depart_admonition to consume once the body has closed.
        self._pending_admonition_title = None

        # D-04/D-05: the ten real Sphinx admonition types are looked up ONCE
        # here, by the node's own docutils class name, against
        # sphinx.locale.admonitionlabels -- every catalog key is verified
        # byte-identical to its docutils node class name, so this single
        # lookup is the whole of D-04/D-05's implementation rather than ten
        # separate call-site edits. When the class name is not a catalog key
        # (todo_node, the generic admonition, topic), the caller's own
        # `custom_title` argument survives untouched. The catalog's values
        # are lazy i18n proxies, not plain strings, so the str() coercion
        # here is load-bearing: _depart_admonition's static-title branch
        # performs string operations on this value.
        catalog_key = node.__class__.__name__
        if catalog_key in admonitionlabels:
            custom_title = str(admonitionlabels[catalog_key])
        self._custom_admonition_title = custom_title

        # Open code-mode content-block (NOT markup-mode "[") so the body
        # evaluates in the translator's unified code mode.
        self.add_text(f"{clue_type}({{")

    def _depart_admonition(self) -> None:
        """
        Helper method to depart any admonition node.

        Closes the code-mode content-block body and attaches the title
        argument (if any) — a dynamic, node-derived title takes precedence
        over a static custom title. The dynamic title is buffered code-mode
        content (from visit_title's admonition branch) and MUST be wrapped
        in a code block `{ ... }`, not a content block `[ ... ]`, so its
        inline calls (text(...), emph(...)) evaluate. The static title (now
        sourced from the sphinx.locale.admonitionlabels catalog for the ten
        real types, D-04/D-05) is routed through escape_typst_string
        (T-39-01) before interpolation, since it can now contain non-ASCII
        or quote/backslash characters the catalog supplies -- no second,
        title-specific escaping routine is introduced.
        """
        self.add_text("}")

        title_expr = None
        if self._pending_admonition_title:
            title_expr = "{" + self._pending_admonition_title + "}"
        elif self._custom_admonition_title:
            escaped_title = escape_typst_string(str(self._custom_admonition_title))
            title_expr = f'"{escaped_title}"'

        if title_expr:
            self.add_text(f", title: {title_expr}")

        self.add_text(")\n\n")

        # Mark that next element in list item needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_note(self, node: nodes.note) -> None:
        """Visit a note admonition (converts to #info[])."""
        self._visit_admonition(node, "info")

    def depart_note(self, node: nodes.note) -> None:
        """Depart a note admonition."""
        self._depart_admonition()

    def visit_warning(self, node: nodes.warning) -> None:
        """Visit a warning admonition (converts to #warning[])."""
        self._visit_admonition(node, "warning")

    def depart_warning(self, node: nodes.warning) -> None:
        """Depart a warning admonition."""
        self._depart_admonition()

    def visit_tip(self, node: nodes.tip) -> None:
        """Visit a tip admonition (converts to #tip[])."""
        self._visit_admonition(node, "tip")

    def depart_tip(self, node: nodes.tip) -> None:
        """Depart a tip admonition."""
        self._depart_admonition()

    def visit_important(self, node: nodes.important) -> None:
        """Visit an important admonition (converts to #warning(title: "Important")[]).

        D-04/D-05: the title now comes from the `sphinx.locale.admonitionlabels`
        catalog lookup in `_visit_admonition`, not this static literal.
        """
        self._visit_admonition(node, "warning")

    def depart_important(self, node: nodes.important) -> None:
        """Depart an important admonition."""
        self._depart_admonition()

    def visit_caution(self, node: nodes.caution) -> None:
        """Visit a caution admonition (converts to #warning[])."""
        self._visit_admonition(node, "warning")

    def depart_caution(self, node: nodes.caution) -> None:
        """Depart a caution admonition."""
        self._depart_admonition()

    def visit_seealso(self, node: addnodes.seealso) -> None:
        """Visit a seealso admonition (converts to #tip[]).

        D-02: seealso joins the success bucket (the same `tip` function
        `visit_hint`/`visit_tip` already pass), not the note bucket.
        """
        self._visit_admonition(node, "tip")

    def depart_seealso(self, node: addnodes.seealso) -> None:
        """Depart a seealso admonition."""
        self._depart_admonition()

    def visit_hint(self, node: nodes.hint) -> None:
        """Visit a hint admonition (converts to #tip[]).

        D-02: hint is in the success bucket (`tip`), alongside `tip` itself
        and (as of this phase) `seealso`.
        """
        self._visit_admonition(node, "tip")

    def depart_hint(self, node: nodes.hint) -> None:
        """Depart a hint admonition."""
        self._depart_admonition()

    def visit_todo_node(self, node: nodes.Element) -> None:
        """
        Visit a todo_node (sphinx.ext.todo). Converts to #task[] (gentle-clues).

        Gated on `config.todo_include_todos`, mirroring every official
        Sphinx builder (html/latex/text/man/texinfo in sphinx/ext/todo.py),
        which each raise `nodes.SkipNode` when the config is False (the
        Sphinx default) -- internal author work-notes must never silently
        leak into published output (TODO-01, T-16-01). Unlike those
        builders, typsphinx does not register a dedicated node handler via
        `app.add_node`; docutils dispatches this method purely by the node
        class NAME (`todo_node`), so no import of `sphinx.ext.todo` is
        needed here.

        Note: todo_node carries its own `nodes.title` child (inserted by
        `sphinx.ext.todo.Todo.run()` at parse time), which visit_title's
        admonition-aware branch buffers and `_depart_admonition` prefers
        over `custom_title` -- the static "Todo" below is an inert,
        non-i18n fallback, not the actual title source (16-RESEARCH.md
        Pitfall 2).

        `task` is verified present in the pinned gentle-clues 1.3.1
        (D-01a) -- no base-`clue` fallback is required.
        """
        if not self.config.todo_include_todos:
            raise nodes.SkipNode
        self._visit_admonition(node, "task", custom_title="Todo")

    def depart_todo_node(self, node: nodes.Element) -> None:
        """Depart a todo_node."""
        self._depart_admonition()

    def visit_error(self, node: nodes.error) -> None:
        """Visit an error admonition (converts to #error[])."""
        self._visit_admonition(node, "error")

    def depart_error(self, node: nodes.error) -> None:
        """Depart an error admonition."""
        self._depart_admonition()

    def visit_danger(self, node: nodes.danger) -> None:
        """Visit a danger admonition (converts to #danger[]).

        D-03-R (gap G-39-1): supersedes D-03. The red family is three
        pairwise-distinct gentle-clues functions, not one collapsed
        function -- danger routes to its own `danger` id rather than to
        the function `visit_error` passes.
        """
        self._visit_admonition(node, "danger")

    def depart_danger(self, node: nodes.danger) -> None:
        """Depart a danger admonition."""
        self._depart_admonition()

    def visit_attention(self, node: nodes.attention) -> None:
        """Visit an attention admonition (converts to #memo[]).

        D-03-R (gap G-39-1): supersedes D-03. The red family is three
        pairwise-distinct gentle-clues functions, not one collapsed
        function -- attention routes to its own `memo` id rather than to
        the function `visit_error` passes, and it is still not in the
        warning bucket.
        """
        self._visit_admonition(node, "memo")

    def depart_attention(self, node: nodes.attention) -> None:
        """Depart an attention admonition."""
        self._depart_admonition()

    def visit_admonition(self, node: nodes.admonition) -> None:
        """Visit a generic ``.. admonition::`` (converts to #notify[]).

        D-09: maps to the gentle-clues `notify` function (accent `#1e66f5`),
        since the generic directive always supplies its own directive-
        derived title. The title flows through the existing admonition-aware
        `visit_title`/`depart_title` buffer-swap automatically; no
        `custom_title` is passed here.
        """
        self._visit_admonition(node, "notify")

    def depart_admonition(self, node: nodes.admonition) -> None:
        """Depart a generic admonition."""
        self._depart_admonition()

    def visit_topic(self, node: nodes.topic) -> None:
        """Visit a topic node (BLK-02/D-01/D-02/D-05/D-10).

        A non-contents `.. topic::` renders as a titled `abstract` box
        (D-10), reusing the same admonition helper as `.. admonition::`
        (D-01) -- the widened visit_title/depart_title buffer-swap (D-02) is
        what makes the title actually get consumed by _depart_admonition.

        A `.. contents::` topic (carrying the `contents` class) is instead
        box-less pass-through (D-05): its title is rendered as a bold label
        (handled entirely by visit_title/depart_title's insert-index trick)
        and its child bullet_list renders through the existing, unmodified
        list visitors -- no clue box wraps it here.
        """
        self._topic_is_contents = "contents" in (node.get("classes", []) or [])
        if self._topic_is_contents:
            # The clue-box path (_visit_admonition) anchors node['ids'] for a
            # normal topic; the box-less contents path returns early, so anchor
            # a propagated target's id here too (no ids -> no-op).
            self._emit_id_anchors(node)
            return
        self._visit_admonition(node, "abstract")

    def depart_topic(self, node: nodes.topic) -> None:
        """Depart a topic node (BLK-02/D-01/D-02/D-05)."""
        if self._topic_is_contents:
            self._topic_is_contents = False
            return
        self._depart_admonition()

    # Line block nodes (BLK-03/D-03/D-04)

    def visit_line_block(self, node: nodes.line_block) -> None:
        """
        Visit a line_block node (an address, epigraph, or poetry stanza).

        Only the outermost line_block (depth 0) opens the `par({...})`
        wrapper -- a nested line_block (docutils nests these directly, no
        intermediate wrapper node) shares the same wrapper as its parent.
        `self._line_block_depth` is a single integer counter; docutils' own
        visitor recursion already provides the nesting "stack" for free, so
        no separate stack data structure is needed (see 13-RESEARCH.md
        "Don't Hand-Roll").
        """
        depth = self._line_block_depth
        if depth == 0:
            # A propagated explicit target can land its id on the outermost
            # line_block; anchor it so a same-document link(<id>, ...) resolves
            # (no ids -> no-op). Only at depth 0, before the par({ wrapper --
            # a nested line_block shares the parent's wrapper and never carries
            # a propagated block target.
            self._emit_id_anchors(node)
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")
            self._line_block_was_in_paragraph = self.in_paragraph
            self._line_block_was_paragraph_has_content = self.paragraph_has_content
            self.add_text("par({")
            self.in_paragraph = True
            self.paragraph_has_content = False
        self._line_block_depth = depth + 1

    def depart_line_block(self, node: nodes.line_block) -> None:
        """Depart a line_block node, closing the wrapper once depth returns to 0."""
        self._line_block_depth -= 1
        if self._line_block_depth == 0:
            self.add_text("})\n\n")
            self.in_paragraph = self._line_block_was_in_paragraph
            self.paragraph_has_content = self._line_block_was_paragraph_has_content
            if self.in_list_item:
                self.list_item_needs_separator = True

    def visit_line(self, node: nodes.line) -> None:
        """
        Visit a line node (one line inside a line_block).

        Emits a per-depth `h(...)` indent spacer for nested line_blocks
        (D-03/D-04) -- a plain code-mode stdlib call, no markup-mode
        bracket-wrap needed (unlike the Phase 11 `<label>`-anchor case,
        `h()` never carries a label). An empty `line` node (no Text child)
        falls through to depart_line's bare linebreak() for free -- no
        special-casing required.
        """
        self._add_paragraph_separator()
        indent_units = self._line_block_depth - 1
        if indent_units > 0:
            self.add_text(f"h({indent_units * 1.5}em)")

    def depart_line(self, node: nodes.line) -> None:
        """
        Depart a line node.

        Emits a REAL `linebreak()` call -- a source '\\n' between two
        code-mode statements is cosmetic-only (DESC-02 precedent), so this
        is what actually produces the visible line break.
        """
        self.add_text("\nlinebreak()")

    # Inline nodes (Task 7.4)
    # Requirement 3.1: Inline cross-references and links

    def visit_inline(self, node: nodes.inline) -> None:
        """
        Visit an inline node.

        Inline nodes are generic containers for inline content.
        They are often used for cross-references with specific CSS classes.

        Task 7.4: Handle inline nodes, especially those with 'xref' class
        Requirement 3.1: Cross-references and links

        VER-01 (Phase 12): Sphinx's ``VersionChange.run()`` bakes the exact,
        already-localized version-directive label wording directly into the
        doctree as a ``nodes.inline(classes=["versionmodified", <kind>])`` at
        directive-parse time (confirmed via live doctree dump, 12-RESEARCH.md
        Part 1) -- so no import of Sphinx's internal changeset-domain label
        map, and no label reconstruction, is needed here. This supersedes
        12-CONTEXT.md D-01's speculated import-based mechanism while
        honoring its "sourced from Sphinx, not hardcoded" intent: the
        translator only detects the already-classed inline and italicizes
        it (D-02's unboxed layout) by delegating to the proven
        `visit_emphasis` dummy-node idiom.
        """
        if "versionmodified" in node.get("classes", []):
            dummy_emph = nodes.emphasis()
            self.visit_emphasis(dummy_emph)
            return
        # Inline nodes are transparent containers - we just process their children
        # The CSS classes (like 'xref', 'doc', 'std-ref') are mainly for HTML/CSS styling
        # For Typst output, we simply render the text content
        pass

    def depart_inline(self, node: nodes.inline) -> None:
        """
        Depart an inline node.

        VER-01 (Phase 12): mirrors `visit_inline`'s classed-dispatch branch --
        see that method's docstring for the full rationale.
        """
        if "versionmodified" in node.get("classes", []):
            dummy_emph = nodes.emphasis()
            self.depart_emphasis(dummy_emph)
            return
        pass

    # Version-change directives (Phase 12, VER-01): `versionadded` /
    # `versionchanged` / `deprecated` / `versionremoved` all parse to a
    # single `addnodes.versionmodified` wrapping a paragraph whose first
    # child is the classed `nodes.inline` handled above. This pass-through
    # pair exists purely to silence the ×972 unknown_visit warning -- the
    # child paragraph already renders correctly through the existing
    # visit_paragraph chain (see 12-RESEARCH.md Pattern 1).

    def visit_versionmodified(self, node: addnodes.versionmodified) -> None:
        """Visit a versionmodified node (transparent pass-through)."""
        pass

    def depart_versionmodified(self, node: addnodes.versionmodified) -> None:
        """Depart a versionmodified node (transparent pass-through)."""
        pass

    # API description nodes (Issue #55)
    # Requirement: API説明ノードの処理

    def visit_index(self, node: addnodes.index) -> None:
        """
        Visit an index node.

        Index entries are skipped in Typst/PDF output as we don't generate indices.
        """
        raise nodes.SkipNode

    def depart_index(self, node: addnodes.index) -> None:
        """Depart an index node."""
        pass

    # Trivial structural node handlers (Phase 12, BLK-01/04/05/06): four
    # small additive handlers reusing already-proven idioms from elsewhere
    # in this file (emit-then-SkipNode, pass-through, bare SkipNode, and
    # dummy-Text-node delegation respectively).

    def visit_transition(self, node: nodes.transition) -> None:
        """
        Visit a transition node (a `----` horizontal rule in RST).

        Emits a full-width Typst rule via ``line(length: 100%)`` -- a
        genuine content gap otherwise, since a bare transition renders
        nothing today (BLK-01). Self-closing node: no children to
        descend into, so this always raises SkipNode.
        """
        # A propagated explicit target (``.. _t:`` before a ``----`` rule)
        # lands its id on the transition; anchor it so a same-document
        # link(<id>, ...) resolves (no ids -> no-op, byte-unchanged).
        self._emit_id_anchors(node)
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text("line(length: 100%)\n\n")
        if self.in_list_item:
            self.list_item_needs_separator = True
        raise nodes.SkipNode

    def depart_transition(self, node: nodes.transition) -> None:
        """Depart a transition node (unreached; kept for symmetry)."""
        pass

    def visit_glossary(self, node: addnodes.glossary) -> None:
        """
        Visit a glossary node (`.. glossary::` directive wrapper).

        Transparent pass-through (BLK-04): the wrapped `definition_list`
        child already renders via `visit_definition_list`, and the term
        anchor is provided by the `depart_term` fix from Plan 12-02 --
        do NOT duplicate that anchor logic here.

        A propagated explicit target (``.. _t:`` before ``.. glossary::``)
        lands its id on THIS glossary node (distinct from the per-term
        anchors); anchor it so a same-document link(<id>, ...) resolves. A
        plain glossary carries no ids -> no-op, byte-unchanged.
        """
        self._emit_id_anchors(node)

    def depart_glossary(self, node: addnodes.glossary) -> None:
        """Depart a glossary node (transparent pass-through)."""
        pass

    def visit_tabular_col_spec(self, node: nodes.Node) -> None:
        """
        Visit a tabular_col_spec node (`.. tabularcolumns::` directive).

        This is a LaTeX-only column-width hint with no Typst equivalent
        (BLK-05). The node is self-closing, so raising SkipNode here
        safely drops it with no risk of leaking the raw column-spec
        content into the compiled output.
        """
        raise nodes.SkipNode

    def visit_abbreviation(self, node: nodes.abbreviation) -> None:
        """
        Visit an abbreviation node (`:abbr:` role).

        No-op: the term's own Text child renders via the normal chain.
        """
        pass

    def depart_abbreviation(self, node: nodes.abbreviation) -> None:
        """
        Depart an abbreviation node.

        Appends the expansion inline as " (expansion)" (BLK-06). Stateless
        -- expands on every occurrence, not just the first (D-08). The
        expansion is author-controlled RST, so it is routed through a
        dummy `nodes.Text` delegated to `visit_Text` -- inheriting the
        existing string-escaping regime -- rather than `node.astext()` or
        a raw f-string interpolation (V5 Input Validation, Pitfall 7).

        FID-14: the auto-generated PEP 3102 keyword-only ("*") and PEP 570
        positional-only ("/") signature separators are represented as an
        `abbreviation` node whose OWN visible text is exactly "*" or "/" --
        the sole reliable, narrow-scope signal (no distinguishing
        classes/ids exist). Suppress the appended explanation ONLY for
        those two exact cases; a genuine `:abbr:` role's acronym text is
        never bare "*"/"/", so it keeps its inline expansion unchanged
        (D-Disc-3).
        """
        explanation = node.get("explanation", "")
        if explanation and node.astext() not in ("*", "/"):
            dummy_text = nodes.Text(f" ({explanation})")
            self.visit_Text(dummy_text)

    # Graceful-degrade net for out-of-scope graphical nodes (Issue #114,
    # DEG-01/DEG-02): unlike visit_index's silent skip, these nodes must
    # leave a reader-visible trace (D-01) -- a bordered native-Typst
    # placeholder naming the node, plus exactly one warning -- rather than
    # silently vanishing or leaking raw DOT/diagram-spec source.

    def _visit_graphical_placeholder(self, node: nodes.Node, node_label: str) -> None:
        """
        Shared graceful-degrade helper for out-of-scope graphical nodes.

        Emits a visible bordered placeholder block naming the node type
        (D-01), logs exactly one warning, and skips the node's children
        entirely -- graphviz/inheritance_diagram store their real content
        (DOT source / class-hierarchy spec) as node attributes rather than
        human-readable Text children, so descending would risk leaking raw
        source instead of rendering anything useful.

        Uses native Typst rect()/box() (Typst stdlib) rather than the
        gentle-clues admonition functions used for note/warning/etc, per
        D-01: a placeholder must not be visually confusable with a real
        admonition.

        Args:
            node: The out-of-scope node (graphviz or inheritance_diagram).
            node_label: Human-readable node-type name for the warning and
                placeholder text.
        """
        logger.warning(
            f"{node_label} is not supported in Typst output; rendering placeholder"
        )
        self.add_text(
            f'rect(text("[{node_label} diagram omitted]"), '
            "stroke: 0.5pt, inset: 8pt, radius: 2pt)\n\n"
        )
        raise nodes.SkipNode

    def visit_graphviz(self, node: nodes.Node) -> None:
        """Visit a graphviz node; renders a placeholder (DEG-01, D-01)."""
        self._visit_graphical_placeholder(node, "graphviz")

    def visit_inheritance_diagram(self, node: nodes.Node) -> None:
        """Visit an inheritance_diagram node; renders a placeholder (DEG-02, D-01)."""
        self._visit_graphical_placeholder(node, "inheritance diagram")

    def visit_desc(self, node: addnodes.desc) -> None:
        """
        Visit a desc node (API description container).

        Desc nodes contain API descriptions (classes, functions, methods, etc.).

        An explicit target (``.. _target:``) immediately preceding an
        object-description directive (e.g. ``.. option::``) has its id
        propagated by docutils' ``PropagateTargets`` transform onto THIS
        outer ``desc`` container -- a DIFFERENT id than the one on
        ``desc_signature`` (bug #17 anchors that one). In the overwhelming
        common case (no preceding explicit target) ``desc`` carries no ids
        at all, so this is a no-op / byte-unchanged for existing output.
        Mirrors the established container-anchor pattern (bug #20) used by
        visit_bullet_list/visit_table/visit_block_quote/etc: anchor BEFORE
        any child (signature/content) is visited.
        """
        self._emit_id_anchors(node)
        # Reset per desc (FID-03): tracks whether the NEXT desc_signature
        # child is this desc's first, so sibling signatures (overloads /
        # alias groups / multi-option directives) get a leading linebreak()
        # while a lone signature stays byte-unchanged. A plain scalar (not a
        # stack) is safe here -- a desc's own desc_signature children are
        # always fully processed (doctree order) before its desc_content
        # (which may hold nested desc children) is entered, so a nested
        # desc's own reset never races the outer desc's already-completed
        # signature loop.
        self._is_first_desc_signature = True

    def depart_desc(self, node: addnodes.desc) -> None:
        """
        Depart a desc node.

        Add spacing after API description blocks.

        Emits a real Typst parbreak() (FID-06) -- back-to-back body-less desc
        siblings (e.g. confvals with only :type:/:default: fields, no body
        paragraph) previously concatenated onto one running line because a
        bare cosmetic "\\n\\n" produces no visual break in Typst code mode.
        Applying parbreak() (even when the desc's last content already ends
        in a par()) is verified harmless -- no double-gap artifact -- so no
        body-less-detection guard is needed for THAT case; sibling body-less
        desc nodes always have something emitted between their two
        departures (id anchors, the next signature's wrapper), so the SIG-08
        suppression below never fires for them (see
        tests/test_desc_bodyless_concat_render_gate.py, this fix's control).

        SIG-08 (D-12, 37-EMISSION-CONTRACT.md section 8): a nested `desc`
        (e.g. a py:method:: inside a py:class::) used to emit an
        unconditional parbreak() for its own departure and again for the
        outer desc's departure, producing two adjacent parbreak() statements
        with nothing between them. Suppressed here via an emission-position
        marker (self._desc_break_marker), mirroring the
        _is_first_desc_signature scalar-flag idiom (visit_desc, above): if
        nothing has been appended to self.body since the immediately
        preceding desc's own parbreak() was recorded, this desc's break is
        redundant and is skipped. The early return deliberately does NOT
        update the marker, so three levels of nesting still yield exactly
        one parbreak() rather than one per pair.

        Phase 38 (D-10, 38-EMISSION-CONTRACT.md section 6.2/6.3): the
        sentence above is still literally true, but the REASON it stays
        true changed once depart_desc_content stopped being `pass`.
        depart_desc_content now always appends the body wrapper's closing
        bytes (`})\\n`) to self.body between an inner desc's departure and
        this method's own comparison, so a literal reading of "nothing has
        been appended" would be false for every nested desc -- the
        suppression would never fire again. It stays correct because
        depart_desc_content itself propagates this marker through its own
        close (records whether the marker still matched immediately before
        emitting `})\\n`, then re-advances the marker past those bytes if it
        did): the wrapper's closing bytes are deliberately made to count as
        nothing for this comparison, without actually being absent from the
        emitted output. depart_desc's own comparison below is therefore
        unchanged and needs no code change -- only this corrected premise.

        This is deliberately NOT implemented as a desc-nesting-depth
        counter. A depth counter would suppress the INNER desc's break
        unconditionally, which is wrong whenever the outer desc_content
        continues with more content after the nested member -- the member
        and the following paragraph would then run together with no
        separation between them. The correct discriminator is "was anything
        emitted between the two departures", not "how deep am I" -- a depth
        counter cannot see the difference between "the outer desc has
        nothing left" and "the outer desc has more content coming".

        The FID-03 sibling linebreak() in visit_desc_signature is a
        different mechanism solving a different problem (separating
        signature LINES within one visual block, not separating one desc
        paragraph-block from the next) and deliberately does not converge
        with this one.

        Inside a table cell, add_text routes into table_cell_content rather
        than self.body (see add_text), so len(self.body) would not advance
        between two departures there and the marker-based suppression would
        fire wrongly. The `not self.in_table` guard retains the pre-phase
        unconditional behaviour inside tables.

        Buffer-swap hazard (D-10, 38-EMISSION-CONTRACT.md section 6.4,
        closing the folded todo
        .planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md):
        self.body is reassigned at multiple sites beyond the table-cell one
        above -- visit_term/visit_definition (via _saved_body_stack), the
        admonition-title save/restore, and the figure-caption save/restore.
        A marker recorded as a bare position integer could compare against a
        DIFFERENT list after such a swap, spuriously suppressing a needed
        break or spuriously letting a duplicate through. self._desc_break_marker
        is therefore a (id(self.body), len(self.body)) pair, not a bare int
        -- comparing both halves closes the hazard without adding a sixth
        per-site guard, since the existing table-cell guard already
        demonstrates that per-site guards do not generalise.
        """
        if not self.in_table and self._desc_break_marker == (
            id(self.body),
            len(self.body),
        ):
            return
        self._emit_forced_break("parbreak()")
        self._desc_break_marker = (id(self.body), len(self.body))

    def visit_desc_signature(self, node: addnodes.desc_signature) -> None:
        """
        Visit a desc_signature node (API element signature).

        Signatures are rendered as typeset code: a page-keep-together block
        carrying a hanging-indent paragraph (SIG-07 + SIG-09, D-10), with
        every text-bearing descendant routed through the monospace primitive
        via ``self.in_signature_text`` (SIG-01..SIG-05, read by visit_Text).

        Sibling desc_signatures (overloads / alias groups / multi-option
        directives) emit a real Typst linebreak() BEFORE every signature
        after the first (FID-03) -- a source '\\n' between two code-mode
        statements is cosmetic-only (produces zero visual break), so
        linebreak() (via the shared _emit_forced_break helper) is required
        to stack them on separate lines rather than concatenating onto one
        running line. A desc with a single signature (the overwhelming
        common case) emits zero extra bytes (the flag stays True through
        the only signature) -- byte-for-byte unchanged.

        ADM-06 / Phase 37: this handler owns its own emission -- it no
        longer delegates to visit_strong via a dummy strong() node. The
        block below WAS a deliberate verbatim copy of visit_strong's body
        (D-01: triplication is the decision, not an accident to be
        refactored away) up through Phase 36; Phase 37 is the phase that
        note anticipated -- desc_signature's emission now diverges from
        visit_strong's in exactly one literal: the opening wrapper call
        changes from ``strong({`` to the composed
        ``block(sticky: true, par(hanging-indent: {SHARED_INDENT_STEP}, {``
        form (37-EMISSION-CONTRACT.md section 3, post-Wave-3 amendment,
        plan 37-09). ``above``/``below`` are deliberately NOT overridden --
        Typst's own ``block()`` default spacing is used. An earlier version
        of this wrapper explicitly zeroed both (``above: 0pt, below: 0pt``);
        that zeroing was found, by the post-merge gate, to remove ALL
        vertical separation on both sides of every signature -- not a
        redundant amount, exactly 0pt -- causing every signature's glyphs to
        overlap the first line of its own description body. Measured (this
        plan, via ``context measure(...)`` deltas in real paragraph flow):
        dropping the override restores 13.2pt on both sides, byte-identical
        to ordinary paragraph-to-paragraph spacing. The original fear that
        default spacing would reintroduce a SIG-08-shaped doubled-gap defect
        does not hold: plan 37-05 already removed the duplicate
        ``parbreak()`` at its emission source (``depart_desc``'s
        emission-position marker), so there is no second break left for
        block-spacing collapse to double up on -- verified by re-rendering
        the SIG-08 nested-desc fixture under this wrapper, which shows
        uniform, single-gap spacing. ``sticky: true`` continues to carry
        SIG-09's keep-with-next unchanged. The hanging indent is D-06's
        chosen, non-negotiable overflow mechanism (a column-grid alternative
        and font-shrinking were both measured and rejected by the owner) --
        neither may be reintroduced here as an improvement. Everything else
        in this block (the paragraph-separator call, the concat-element
        enter/exit pair, the in_paragraph/in_list_item/
        list_item_needs_separator save-and-restore, and the
        `_strong_was_*` attribute names shared with
        visit_strong/depart_strong on purpose, D-02) stays byte-identical --
        renaming those attributes is Phase 39's deferred repair and would
        change emitted bytes outside this plan's scope.
        """
        if not self._is_first_desc_signature:
            self._emit_forced_break("linebreak()")
        self._is_first_desc_signature = False

        # --- begin verbatim copy of visit_strong's body (D-01) ---
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # If this strong is a sibling in a code-mode concat context (def-list
        # term / link body / desc parameter), + separate it and suppress that
        # context for the strong body (content mode, where an outer '+' would
        # leak). Otherwise fall back to the list-item newline separator.
        if not self._enter_inline_concat_element():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Save and reset list item separator for children (they're inside this element)
        was_list_item_needs_separator = self.list_item_needs_separator

        # Since strong({}) uses content block, treat it like list_item
        # Children need newline separators, not + operators
        was_in_list_item = self.in_list_item
        self.in_list_item = True
        self.list_item_needs_separator = False

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # SIG-01..SIG-05: every text-bearing descendant of this signature
        # routes through visit_Text's monospace branch for the signature's
        # entire duration (cleared in depart_desc_signature, before the
        # anchor loop).
        self.in_signature_text = True

        # SIG-07 + SIG-09 (D-10): the ONE composed wrapper -- block()'s
        # sticky:true carries the page-keep-together (SIG-09), par()'s
        # hanging-indent carries the overflow mechanism (SIG-07). Replaces
        # ONLY the pre-Phase-37 `strong({` literal (contract section 3).
        # above/below are NOT overridden (post-Wave-3 amendment, plan
        # 37-09): Typst's own block() default spacing is used, restoring
        # ordinary paragraph-to-paragraph separation on both sides of the
        # signature -- an earlier `above: 0pt, below: 0pt` override
        # removed ALL of that spacing and made every signature overlap
        # the first line of its own description body.
        self.add_text(
            f"{prefix}block(sticky: true, "
            f"par(hanging-indent: {SHARED_INDENT_STEP}, {{"
        )

        # Store state to restore in depart
        self._strong_was_in_paragraph = was_in_paragraph
        self._strong_was_in_list_item = was_in_list_item
        self._strong_was_list_item_needs_separator = was_list_item_needs_separator
        # --- end verbatim copy of visit_strong's body ---

        # Reset per signature (DESC-02): each desc_signature starts fresh,
        # so consecutive signatures don't carry over a stray linebreak().
        self._is_first_desc_signature_line = True

    def depart_desc_signature(self, node: addnodes.desc_signature) -> None:
        """
        Depart a desc_signature node.

        ADM-06 / Phase 37: this handler owns its own emission -- the block
        below WAS a deliberate verbatim copy of depart_strong's body (D-01)
        up through Phase 36. Phase 37 makes it diverge in exactly one
        literal: the closing call changes from ``})`` to ``}))`` -- one
        ``}`` closing the content block, one ``)`` closing ``par(``, one
        ``)`` closing ``block(`` (37-EMISSION-CONTRACT.md section 3),
        matching visit_desc_signature's composed wrapper open. The
        `_strong_was_*` attribute names are shared with depart_strong on
        purpose (D-02); see visit_desc_signature's docstring for the
        deferred-repair note.
        """
        # --- begin verbatim copy of depart_strong's body (D-01) ---
        # Close block(par({...})) -- matches visit_desc_signature's composed
        # wrapper open (contract section 3).
        self.add_text("}))")

        # Restore paragraph state
        if hasattr(self, "_strong_was_in_paragraph"):
            self.in_paragraph = self._strong_was_in_paragraph
            delattr(self, "_strong_was_in_paragraph")

        # Restore in_list_item state
        if hasattr(self, "_strong_was_in_list_item"):
            self.in_list_item = self._strong_was_in_list_item
            delattr(self, "_strong_was_in_list_item")

        # Restore and mark that next element needs separator
        if hasattr(self, "_strong_was_list_item_needs_separator"):
            # Restore previous state, then mark next element needs separator
            if self.in_list_item:
                self.list_item_needs_separator = True
            delattr(self, "_strong_was_list_item_needs_separator")

        # Restore the code-mode concat context suppressed for the strong body
        # and mark this strong as a sibling so the next term/link/desc
        # expression is + separated.
        self._exit_inline_concat_element()
        # --- end verbatim copy of depart_strong's body ---

        # SIG-01..SIG-05: clear the monospace-propagation flag now that the
        # signature's content is closed, before the anchor loop below (the
        # anchors are orthogonal to typography and were never affected by
        # the flag).
        self.in_signature_text = False

        # Emit a Typst anchor for every id on the signature so same-document
        # cross-references resolve to this API declaration. depart_reference's
        # refid branch emits ``link(<_sanitize_label(refid)>, ...)`` for a
        # same-document xref, but the anchor it points at was never emitted
        # here -- unlike visit_target/visit_title/depart_term, desc_signature
        # (the node type carrying API-declaration ids) emitted none, so every
        # ``:c:func:``/``:py:func:`` style refid link to a declaration dangled
        # with Typst's semantic ``label ... does not exist``.
        #
        # Mirror the proven target-anchor form -- ``[#metadata(none) <id>]`` --
        # a zero-content markup block that carries the label and joins cleanly
        # as its own statement in the surrounding code-mode block (a bare
        # code-mode ``label("id")`` would juxtapose/fail to join). Route every
        # id through _sanitize_label so the anchor name byte-matches the
        # reference side (both sides use the same helper). Multiple ids
        # (aliases/overloads) each get an anchor; a signature with NO ids emits
        # nothing (byte-unchanged). ids are globally unique per document
        # (docutils make_id), so no label is defined twice; dedupe defensively.
        docname = self._current_docname()
        seen_labels: set[str] = set()
        for node_id in node.get("ids", []):
            label_id = self._namespace_label(docname, node_id)
            if label_id in seen_labels:
                continue
            seen_labels.add(label_id)
            self.add_text(f"\n[#metadata(none) <{label_id}>]")
        # Add extra spacing after signature
        self.add_text("\n")

    def visit_desc_returns(self, node: addnodes.desc_returns) -> None:
        """
        Visit a desc_returns node (a signature's return-type annotation).

        SIG-06 / D-13 (37-EMISSION-CONTRACT.md section 7): emits a real
        rightwards-arrow glyph (U+2192) before the return type, not the
        pre-phase ASCII "->" -- the three-expression monospace form
        `raw(" ") + raw("\\u{2192}") + raw(" ")` is the exact shape that
        was compiled and pypdf-extraction-verified this session; a single
        `raw(" -> ")`-shaped literal was not. Resolved return-type xref
        children already stream through the unmodified visit_reference
        refid branch -- no extra code needed for that case.
        """
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text('raw(" ") + raw("\\u{2192}") + raw(" ")')
        if self.in_list_item:
            self.list_item_needs_separator = True

    def depart_desc_returns(self, node: addnodes.desc_returns) -> None:
        """Depart a desc_returns node."""
        pass

    def visit_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
        """
        Visit a desc_signature_line node (one line of a genuine multi-line
        signature, e.g. a C++ template declaration).

        Emits a real Typst linebreak() before every line after the first
        (DESC-02) -- a source '\\n' between two code-mode statements is
        proven cosmetic-only (produces zero visual break), so linebreak()
        (Typst stdlib) is required. The first line emits nothing extra,
        keeping the single-line case (one desc_signature_line, or none)
        backward-compatible.
        """
        if not self._is_first_desc_signature_line:
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")
            self.add_text("linebreak()")
            if self.in_list_item:
                self.list_item_needs_separator = True
        self._is_first_desc_signature_line = False

    def depart_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
        """Depart a desc_signature_line node."""
        pass

    def visit_desc_content(self, node: addnodes.desc_content) -> None:
        """
        Visit a desc_content node (API description content).

        Opens the shared indent step around the description body
        (IND-01/02/03/05, D-01, 38-EMISSION-CONTRACT.md section 2):
        ``pad(left: SHARED_INDENT_STEP, {`` -- the exact block-quote analog
        (visit_block_quote, above) applied to a run of code-mode body
        statements, reusing that pattern's own reasoning for why the body
        must be a ``{ ... }`` content block (bug #15). Routed through
        self.add_text (D-12), never self.body.append: add_text routes into
        table_cell_content when self.in_table, and the 38-01 fixture proved
        a direct append breaks a desc inside a table cell. Nesting composes
        with NO depth counter (D-01) -- each pad closes structurally when
        its own node's depart_desc_content runs, so IND-05 (depth cannot
        leak to a following sibling) is asserted by that closure, not
        implemented by resetting anything.

        Separator bookkeeping (D-12, decided by the fixture, section 2.6):
        desc_content structurally always follows a desc_signature departure,
        which itself unconditionally ends in a raw "\\n" (see
        depart_desc_signature's anchor-loop spacing line) -- so, unlike
        block_quote, this leading guard is not required to avoid a Typst
        parse fatal. It is still emitted, mirroring the block-visitor
        pattern (bug #4) byte-for-byte with block_quote/field_list, because
        depart_desc_signature ALSO sets list_item_needs_separator = True
        when in a list item -- the guard's own "\\n" then lands on top of
        the signature's already-present "\\n" (a harmless extra blank line
        in code mode, never a parse error) rather than diverging from every
        other block visitor's leading-guard shape. Falsified by
        ``tests/fixtures/desc_content_indent_render_gate/index.rst``'s
        "List-Item Desc CONTROL" section (a py:function:: nested inside a
        bullet-list item, exercised via
        tests/test_desc_content_indent_render_gate.py) and confirmed
        non-regressing against tests/test_desc_bodyless_concat_render_gate.py
        (no list item involved, guard is a no-op there).
        """
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text(f"pad(left: {SHARED_INDENT_STEP}, {{")

    def depart_desc_content(self, node: addnodes.desc_content) -> None:
        """
        Depart a desc_content node.

        Closes the body wrapper opened in visit_desc_content: ``})\\n``
        (38-EMISSION-CONTRACT.md section 2). The trailing "\\n" is
        load-bearing, not cosmetic (section 2.2): depart_desc immediately
        follows with _emit_forced_break("parbreak()"), which prepends no
        newline of its own outside a list item, so a bare "})" would
        juxtapose the pad(...) expression against parbreak() on one
        physical source line -- the Typst "expected semicolon or line
        break" fatal class this codebase has hit four separate times.
        depart_block_quote (the direct analog) already carries the same
        trailing newline for the same reason.

        D-10 marker propagation (section 6.2): depart_desc suppresses a
        duplicate parbreak() by testing whether self._desc_break_marker
        still equals len(self.body) -- "was anything emitted between the
        two departs". Before this handler had a body, that test was
        reliable because nothing at all was appended between an inner and
        an outer desc's departure. Now that this handler always emits the
        close, len(self.body) would advance on EVERY nested desc's
        departure and the suppression could never fire again. Fixed by
        recording, before emitting the close, whether the marker still
        matches the pre-close position; emitting the close; and if it did
        match, advancing the marker to the POST-close position. depart_desc
        then still sees "nothing happened" (its own comparison against the
        advanced marker is unaffected) and correctly suppresses its own
        duplicate for a nested desc with no trailing sibling content. This
        makes the wrapper's closing bytes a byte sequence that counts as
        nothing for the suppression's purposes, without actually being
        absent. depart_desc itself needs no code change under this fix
        (see its own docstring for the corrected premise).

        The `not self.in_table` guard mirrors depart_desc's own: inside a
        table cell, add_text routes into table_cell_content rather than
        self.body, so len(self.body) does not advance there and comparing
        against it would be meaningless (and is never read, since
        depart_desc's own check is guarded the same way).

        The marker is a (id(self.body), len(self.body)) pair, not a bare
        position integer (D-10, 38-EMISSION-CONTRACT.md section 6.4) --
        self.body is reassigned at several sites (visit_term/
        visit_definition, the admonition-title and figure-caption
        save/restores) and a bare integer could otherwise be compared
        against a different buffer after a swap. See depart_desc's own
        docstring for the buffer-swap hazard this closes.
        """
        marker_was_untouched = not self.in_table and self._desc_break_marker == (
            id(self.body),
            len(self.body),
        )
        self.add_text("})\n")
        if marker_was_untouched:
            self._desc_break_marker = (id(self.body), len(self.body))
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_desc_inline(self, node: addnodes.desc_inline) -> None:
        """
        Visit a desc_inline node (an inline signature fragment, e.g.
        :cpp:expr:).

        Transparent pass-through (DESC-04, D-06): desc_inline is a distinct
        Sphinx node class from desc_signature, so node-type dispatch alone
        satisfies D-06's strong()-suppression -- do NOT delegate to
        visit_strong the way visit_desc_signature does, that would
        reintroduce the strong() wrapper this requirement forbids.
        """
        pass

    def depart_desc_inline(self, node: addnodes.desc_inline) -> None:
        """Depart a desc_inline node."""
        pass

    def visit_desc_annotation(self, node: addnodes.desc_annotation) -> None:
        """
        Visit a desc_annotation node (type annotations like 'class', 'async', etc.).

        SIG-03 (37-EMISSION-CONTRACT.md section 5.1): identical treatment
        to visit_desc_name -- a desc_annotation and a desc_name in the
        SAME signature must render with the byte-identical wrapper shape.
        When every child is a text-only nodes.Text leaf (the py/option/c/
        rst-domain case), emit the complete bold-monospace form via
        _emit_signature_leaf_wrapper and skip further descent. Otherwise
        stay a no-op and let the children dispatch normally under
        self.in_signature_text -- flattening a non-leaf subtree via
        node.astext() is the RESEARCH Pitfall 3 hazard.
        """
        if all(isinstance(child, nodes.Text) for child in node.children):
            self._emit_signature_leaf_wrapper(node, "strong")

    def depart_desc_annotation(self, node: addnodes.desc_annotation) -> None:
        """
        Depart a desc_annotation node.

        Space after annotation is handled by desc_sig_space node.
        """
        # Don't add space here - desc_sig_space handles it
        # Don't set list_item_needs_separator - let next node handle it
        pass

    def visit_desc_addname(self, node: addnodes.desc_addname) -> None:
        """
        Visit a desc_addname node (module name prefix).

        SIG-02: deliberately stays a no-op. self.in_signature_text alone
        gives every descendant Text node regular-weight monospace
        (raw(...), no strong()) via visit_Text's branch -- that IS SIG-02.
        Do not add a wrapper here.
        """
        pass

    def depart_desc_addname(self, node: addnodes.desc_addname) -> None:
        """Depart a desc_addname node."""
        pass

    def visit_desc_name(self, node: addnodes.desc_name) -> None:
        """
        Visit a desc_name node (function/class name).

        SIG-01 (37-EMISSION-CONTRACT.md section 5.1): when every child is
        a text-only nodes.Text leaf (the py/option/c/rst-domain case),
        emit the complete bold-monospace form via
        _emit_signature_leaf_wrapper and skip further descent. Otherwise
        (measured: the C++ domain nests a desc_sig_name inside desc_name)
        stay a no-op and let the nested desc_sig_name handle itself via
        visit_desc_sig_name's rule 1 -- flattening a non-leaf subtree via
        node.astext() would silently drop a resolved cross-reference's
        hyperlink while still passing a substring check (RESEARCH
        Pitfall 3).
        """
        if all(isinstance(child, nodes.Text) for child in node.children):
            self._emit_signature_leaf_wrapper(node, "strong")

    def depart_desc_name(self, node: addnodes.desc_name) -> None:
        """
        Depart a desc_name node.

        Only reached for the non-leaf branch (visit_desc_name's leaf
        branch raises nodes.SkipNode, so depart is never called for a
        leaf desc_name -- its separator bookkeeping is functionally
        preserved through _emit_signature_leaf_wrapper's own
        mark-content fallback instead).
        """
        # Mark that next element needs separator (for parameterlist)
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_desc_parameterlist(self, node: addnodes.desc_parameterlist) -> None:
        """
        Visit a desc_parameterlist node (parameter list container).

        Parameters are concatenated with + inside monospace parentheses.

        SIG-05 (37-EMISSION-CONTRACT.md section 6): the five parameter-list
        delimiter sites -- this opening paren, the closing paren in
        depart_desc_parameterlist, the comma-space separator in
        depart_desc_parameter, and the optional-group brackets in
        visit_desc_optional/depart_desc_optional -- all emit through the
        raw(...) monospace primitive. Every other signature delimiter
        (operator and punctuation nodes: desc_sig_operator,
        desc_sig_punctuation, etc.) already reaches monospace "for free"
        via the self.in_signature_text flag (contract section 4.3) rather
        than through a dedicated handler, so SIG-05's "every delimiter is
        monospace" truth is satisfied jointly by these five sites plus that
        flag -- not by these five sites alone.

        These five delimiters are hardcoded ASCII carrying no user-supplied
        text, so no escape_typst_string call is added at these sites --
        that omission is deliberate (T-37-01's mitigation), not an
        oversight: every site that DOES carry user text already routes
        through the shared escaping helper via the monospace branch added
        in plan 37-06.
        """
        # Add separator before opening paren
        if self.in_list_item and self.list_item_needs_separator:
            self.body.append("\n")

        # Output opening paren as raw (monospace) with + after it
        self.body.append('raw("(") + ')

        # Mark that parameterlist started
        self.in_desc_parameter = True
        self._desc_parameter_has_content = (
            False  # First parameter doesn't need + before it
        )

    def depart_desc_parameterlist(self, node: addnodes.desc_parameterlist) -> None:
        """Depart a desc_parameterlist node."""
        # Output closing paren as raw (monospace), with + before it
        if self._desc_parameter_has_content:
            self.body.append(" + ")
        self.body.append('raw(")")')
        self.in_desc_parameter = False

    def visit_desc_parameter(self, node: addnodes.desc_parameter) -> None:
        """
        Visit a desc_parameter node (individual parameter).

        SIG-04 / D-05 (37-EMISSION-CONTRACT.md section 5.2): resets
        self._param_name_seen to False for THIS parameter, mirroring
        visit_desc_parameterlist's existing per-scope
        _desc_parameter_has_content = False reset idiom -- so
        visit_desc_sig_name's rule 2 italicises only the FIRST text-only-
        leaf desc_sig_name child of each parameter. A scalar (not a
        stack) is correct here: desc_parameter nodes never nest inside
        desc_parameter nodes -- a desc_optional group holds desc_parameter
        SIBLINGS, and each resets the flag on its own entry.
        """
        self._param_name_seen = False
        # No changes needed - already in desc_parameter context from parameterlist
        # Don't reset _desc_parameter_has_content here - it's managed by depart_desc_parameter

    def depart_desc_parameter(self, node: addnodes.desc_parameter) -> None:
        """
        Depart a desc_parameter node.

        Add comma + space between parameters if not last.
        """
        # Add comma between parameters (raw(...): SIG-05 monospace delimiter)
        if node.next_node(descend=False, siblings=True):
            self.body.append(' + raw(", ")')
            self._desc_parameter_has_content = True

    def visit_desc_optional(self, node: addnodes.desc_optional) -> None:
        """
        Visit a desc_optional node (trailing optional parameter group,
        e.g. printf(fmt[, args[, more]])).

        Literal-bracket-wraps the optional group, reusing the existing
        _desc_parameter_has_content flag (DESC-03, zero new state). A
        nested desc_optional is a structural doctree sibling, not a
        parent-child relationship the handler needs to track -- the
        identical handler firing again for the nested node produces
        correctly nested brackets with no depth counter.
        """
        if self._desc_parameter_has_content:
            self.add_text(" + ")
        self.add_text('raw("[")')
        self._desc_parameter_has_content = True

    def depart_desc_optional(self, node: addnodes.desc_optional) -> None:
        """
        Depart a desc_optional node.

        D-11 (37-EMISSION-CONTRACT.md section 6.1): when this optional
        GROUP itself has a following sibling, Sphinx's own HTML writer
        puts the separator INSIDE the closing bracket -- measured this
        session -- so this handler emits the same ", " separator
        depart_desc_parameter emits, through the monospace primitive,
        immediately BEFORE the closing bracket.

        Two things are load-bearing here:

        1. The sibling test is against the desc_optional node ITSELF,
           mirroring what depart_desc_parameter already does for a
           desc_parameter's own following sibling -- NOT against
           desc_optional's last child. The group's last parameter has no
           following sibling of its own, which is exactly why the
           separator Sphinx emits (because the *group* has one) was
           previously lost.
        2. The nested-optional case (e.g. printf(fmt[, args[, more]]))
           is UNCHANGED by this guard, because both of its optional
           groups are last children -- this is the fix's non-regression
           CONTROL, not a case to later "extend" the fix to cover.

        Contract section 6.2 corrects CONTEXT.md D-11's second half: the
        closing bracket and a following parameter are ALREADY explicitly
        + joined on the current tree (depart_desc_optional already sets
        _desc_parameter_has_content = True below), so that half is a
        non-regression assertion, not a code change.
        """
        if node.next_node(descend=False, siblings=True):
            self.add_text(' + raw(", ")')
        self.add_text(' + raw("]")')
        self._desc_parameter_has_content = True

    def visit_field_list(self, node: nodes.field_list) -> None:
        """
        Visit a field_list node (structured fields like Parameters, Returns).

        Opens the field list's own indent step (FLD-01, D-03,
        38-EMISSION-CONTRACT.md section 3): ``pad(left: SHARED_INDENT_STEP,
        {`` -- the SAME shared constant desc_content's body wrapper uses, so
        under that wrapper's composition (no depth counter, D-01) a field
        list nested inside a description body simply lands one further step
        in. Emitted AFTER the existing bug #4 leading-separator guard below,
        which is unchanged, and routed through self.add_text (D-12), never
        self.body.append -- a field list inside a table cell misroutes
        without it (38-EMISSION-CONTRACT.md section 3.1).

        Separator bookkeeping (D-12, decided by the fixture): this handler
        keeps the SAME leading-guard shape as visit_desc_content's own
        decision (38-05-SUMMARY.md) and visit_block_quote's bug #4
        precedent -- consistency with the established block-visitor pattern
        over a byte-count-minimal implementation. Falsified against
        tests/test_field_list_in_list_item_render_gate.py (a genuine field
        list inside a bullet-list item) and confirmed non-regressing
        against tests/test_desc_bodyless_concat_render_gate.py.
        """
        # Emit a leading newline separator when this field list follows a
        # sibling inside a list item, matching the block-visitor pattern
        # established in bug #4 (bullet_list/literal_block/definition_list/
        # block_quote). Otherwise visit_field_name's strong( juxtaposes
        # against the preceding inline expression in the list-item content
        # block -- e.g. `text("For example:")strong(` -- a Typst parse error
        # ("expected semicolon or line break", GATE-02 fatal #12). field_list
        # was the one block visitor omitted from that fix.
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
            self.list_item_needs_separator = False
        self.add_text(f"pad(left: {SHARED_INDENT_STEP}, {{")

    def depart_field_list(self, node: nodes.field_list) -> None:
        """
        Depart a field_list node.

        Closes the indent step opened in visit_field_list: ``})\\n``
        (38-EMISSION-CONTRACT.md section 3), replacing the pre-phase bare
        ``self.body.append("\\n")``. Routed through self.add_text (D-12) --
        the pre-phase direct append bypassed table-cell routing entirely, so
        a field list inside a table cell misroutes today regardless of the
        wrapper (section 3.1); this conversion fixes that byte-identically
        outside a table.
        """
        self.add_text("})\n")

        # Mark that a following sibling in the same list item must be
        # separated (block-visitor pattern, bug #4).
        if self.in_list_item:
            self.list_item_needs_separator = True

    def visit_field(self, node: nodes.field) -> None:
        """
        Visit a field node (individual field in a field list).
        """
        pass

    def depart_field(self, node: nodes.field) -> None:
        """
        Depart a field node.

        Emit an inter-field double-space separator (FID-09) when this field
        has a following sibling, mirroring depart_desc_parameter's "am I the
        last sibling" idiom. The double space is wrapped in BOTH a leading
        AND a trailing newline so it never juxtaposes with the neighboring
        strong(...) call on one physical source line -- a leading-only
        newline is a real Typst "expected semicolon or line break" fatal.

        Only applies when the field body just closed used the collapsed
        inline form (see visit_field_body/depart_field_body). A
        paragraph-wrapped / block field body (the common ``:param:``/
        ``:type:``/``:returns:`` docstring case, and any field value on its
        own blank-line-separated line) already gets adequate separation from
        depart_field_body's trailing newline plus the next field's fresh
        strong( statement -- adding "  " there lands as a stray leading
        two-space indent glued to the next field's label (CR-01).
        """
        if self._last_field_body_was_inline and node.next_node(
            descend=False, siblings=True
        ):
            self.add_text('\ntext("  ")\n')

    def visit_field_name(self, node: nodes.field_name) -> None:
        """
        Visit a field_name node (field name like 'Parameters', 'Returns').

        Field names are rendered in bold with a colon (no # prefix in code mode).
        """
        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Use strong() function (no # prefix in code mode)
        self.add_text("strong(")

        # Store state to restore in depart
        self._field_name_was_in_paragraph = was_in_paragraph

    def depart_field_name(self, node: nodes.field_name) -> None:
        """Depart a field_name node."""
        # Close strong() and add a colon followed by a breakable space
        # (FID-09) -- the space is a real content value inside the +-joined
        # strong() expression, restoring the "Type: int" colon-space that
        # was previously emitted as a bare colon with no trailing space.
        self.add_text(' + text(": "))\n')

        # Restore paragraph state
        if hasattr(self, "_field_name_was_in_paragraph"):
            self.in_paragraph = self._field_name_was_in_paragraph
            delattr(self, "_field_name_was_in_paragraph")

    def visit_field_body(self, node: nodes.field_body) -> None:
        """
        Visit a field_body node (field content).

        A field body written inline on its field line (e.g. a confval
        ``:default: The value of **html_title**``) is COLLAPSED by docutils:
        its children are inline nodes (Text/strong/literal/reference) DIRECTLY
        under ``field_body``, with no wrapping ``paragraph``. Emitted into the
        code-mode content block those adjacent expressions juxtapose
        (``text("The value of ")strong({...})``) -- a Typst syntax error
        ("expected semicolon or line break", GATE-02 fatal #8). Activate the
        shared inline-concat context (bug #5 machinery) so they are ``+``
        separated into one content value.

        A SECOND case reuses the same concat context (FLD-02, D-07,
        38-EMISSION-CONTRACT.md section 4.2): a field body whose ONLY child
        is a single ``nodes.paragraph`` -- the ordinary ``:param:``/
        ``:returns:``/``:rtype:`` docstring shape docutils produces (verified
        by reading ``sphinx/util/docfields.py``'s ``Field.make_field`` /
        ``GroupedField.make_field``'s ``can_collapse`` branch: this shape is
        ALWAYS exactly one paragraph, never heuristic). Pre-phase this value
        was unconditionally wrapped in Typst's block-level ``par(...)``,
        which starts a new visual line regardless of any separator -- that
        is FLD-02's whole defect. ``_field_body_unwrapped_paragraph`` marks
        this case so ``visit_paragraph``/``depart_paragraph`` can skip the
        ``par({``/``})`` wrapper for exactly this one paragraph, letting its
        children dispatch unmodified through the SAME
        ``_in_field_body``/``_field_body_has_content`` machinery the
        collapsed-inline case already exercises -- no second concat
        mechanism.

        A multi-value body (multiple ``:param:`` entries collapsed by
        docutils into ONE ``field_body`` containing a ``bullet_list``) is
        neither of the above: its ``all_inline`` check is False and its
        child count is not exactly one paragraph, so it falls through to the
        existing block path unchanged (FLD-02's non-regression half).
        """
        self._field_body_stack.append(
            (
                self._in_field_body,
                self._field_body_has_content,
                self._field_body_unwrapped_paragraph,
            )
        )
        all_inline = all(
            isinstance(child, (nodes.Text, nodes.Inline)) for child in node.children
        )
        single_paragraph = len(node.children) == 1 and isinstance(
            node.children[0], nodes.paragraph
        )
        if all_inline:
            self._in_field_body = True
            self._field_body_has_content = False
            self._field_body_unwrapped_paragraph = False
        elif single_paragraph:
            self._in_field_body = True
            self._field_body_has_content = False
            self._field_body_unwrapped_paragraph = True
        else:
            self._in_field_body = False
            self._field_body_unwrapped_paragraph = False

    def depart_field_body(self, node: nodes.field_body) -> None:
        """
        Depart a field_body node.

        Restore the concat context saved by :meth:`visit_field_body` and add a
        newline after the field body.

        The D-07/D-08 trap (FLD-02): ``_last_field_body_was_inline`` gates
        ``depart_field``'s FID-09 inter-field ``"  "`` separator, which is
        only correct for the genuinely docutils-collapsed-inline body (two
        fields legitimately sharing one line, e.g. a confval's
        ``:type:``/``:default:``). The new single-paragraph-unwrapped case
        (above) also sets ``_in_field_body = True`` to reuse the SAME concat
        context, but must NOT let the separator fire between consecutive
        single-value fields -- doing so would merge ``Returns:``,
        ``Return type:`` and ``Raises:`` onto one line and produce a ZERO
        interval where D-08 measured 20.438pt per field. Excluding
        ``_field_body_unwrapped_paragraph`` from this flag is what keeps the
        separator scoped to the collapsed-inline case only, with zero change
        needed to :meth:`depart_field` itself.

        The other half of D-08's own trap: a single-value field body's sole
        paragraph no longer gets a "free" paragraph boundary from ``par(...)``
        the way it used to (that block-level wrapper is exactly what
        visit_paragraph now skips for this case). Consecutive single-value
        fields must still occupy separate paragraphs -- so when THIS field
        body was the single-paragraph-unwrapped case AND its parent ``field``
        has a following sibling, emit a real ``parbreak()`` here, before
        popping back to the parent's saved state (this is the one place that
        still has access to both facts at once). Re-derived from the doctree
        (``node.parent``'s own next-sibling check), not a second new
        instance attribute. Wrapped in a LEADING newline (unlike
        _emit_forced_break's list-item-only leading guard): the preceding
        content here is the paragraph's last bare inline expression with no
        trailing separator of its own, so a bare "parbreak()" would
        juxtapose directly against it -- the same "expected semicolon or
        line break" fatal class this codebase has hit before.
        """
        # Remember whether THIS field body was collapsed-inline (never the
        # single-paragraph-unwrapped case), for depart_field's separator
        # decision (CR-01/D-08), before popping back to the parent's saved
        # state.
        self._last_field_body_was_inline = (
            self._in_field_body and not self._field_body_unwrapped_paragraph
        )
        if self._field_body_unwrapped_paragraph and node.parent is not None:
            if node.parent.next_node(descend=False, siblings=True) is not None:
                self.add_text("\nparbreak()\n")
        (
            self._in_field_body,
            self._field_body_has_content,
            self._field_body_unwrapped_paragraph,
        ) = self._field_body_stack.pop()
        self.add_text("\n")

    def visit_rubric(self, node: nodes.rubric) -> None:
        """
        Visit a rubric node (section subheading).

        Rubrics are rendered as subsection headings using strong({}) wrapper.

        ADM-06: this handler owns its own emission -- it no longer delegates
        to visit_strong via a dummy strong() node. The block below started as
        a verbatim copy of visit_strong's body (D-01: triplication is the
        decision, not an accident to be refactored away), and Phase 39 was
        named, at the time that copy was made, as the phase that would make
        it diverge.

        Phase 39 (D-13) has now made that divergence real for the save
        slots: this handler's three save slots are ``_rubric_was_*``, not
        the ``_strong_was_*`` names visit_strong/depart_strong and
        visit_desc_signature/depart_desc_signature still share between
        themselves (that pair's own sharing stays deliberate and unedited,
        D-02). Before this change, a nested inline ``strong`` firing while
        THIS rubric's state was saved under the shared name would silently
        clobber it -- `depart_strong`'s own `delattr` calls would delete the
        keys `depart_rubric` still needed to restore, leaving
        `self.in_list_item` stuck `True` for the rest of the document. That
        can no longer happen: the two save sites no longer write the same
        `self.__dict__` keys.

        This commit (D-11) also closes the double-blank-line wart the
        docstring previously described as deliberately preserved: when a
        rubric carries a propagated target (anchored via
        ``_emit_id_anchors`` immediately below), that emitter's own trailing
        newline is already the separator this rubric needs -- both the
        unconditional newline append and the leading list-item separator
        check that used to follow it are now suppressed for an anchored
        rubric, so it no longer double- (or triple-, via the re-armed
        list-item flag) counts a separator ``_emit_id_anchors`` already
        supplied. An unanchored rubric (no propagated target) takes neither
        branch differently and keeps today's byte shape exactly.
        """
        # A propagated explicit target (``.. _t:`` immediately before a
        # ``.. rubric::``) lands its id on this rubric node; anchor it so a
        # same-/cross-document link(<id>, ...) resolves (no ids -> no-op).
        # D-11: measure whether _emit_id_anchors actually emitted anything
        # (it is a no-op for an id-less node) so the guards below can tell
        # whether it already supplied this rubric's leading separator.
        body_len_before_anchors = len(self.body)
        self._emit_id_anchors(node)
        anchors_were_emitted = len(self.body) > body_len_before_anchors

        # D-11: _emit_id_anchors's own trailing "\n" (see its tail, above)
        # is this rubric's fair, sufficient separator share when it just
        # anchored a propagated target -- do not add a second one on top of
        # it. A rubric that anchored nothing owes exactly what it owed
        # before this guard existed.
        if not anchors_were_emitted:
            # Add newline before rubric
            self.body.append("\n")

        # --- begin verbatim copy of visit_strong's body (D-01) ---
        # Add separator if in paragraph and not first node
        self._add_paragraph_separator()

        # If this strong is a sibling in a code-mode concat context (def-list
        # term / link body / desc parameter), + separate it and suppress that
        # context for the strong body (content mode, where an outer '+' would
        # leak). Otherwise fall back to the list-item newline separator.
        #
        # D-11: when _emit_id_anchors just anchored a propagated target, its
        # tail re-arms ``list_item_needs_separator`` as a side effect of its
        # OWN bookkeeping (correct for every OTHER body-element handler that
        # calls it) -- without the ``not anchors_were_emitted`` guard this
        # branch would double-count that flag on top of the anchor's own
        # trailing newline, the second half of the same wart the guard above
        # closes.
        if not self._enter_inline_concat_element():
            if (
                not anchors_were_emitted
                and self.in_list_item
                and self.list_item_needs_separator
            ):
                self.add_text("\n")

        # Temporarily disable paragraph state for children
        was_in_paragraph = self.in_paragraph
        self.in_paragraph = False

        # Save and reset list item separator for children (they're inside this element)
        was_list_item_needs_separator = self.list_item_needs_separator

        # Since strong({}) uses content block, treat it like list_item
        # Children need newline separators, not + operators
        was_in_list_item = self.in_list_item
        self.in_list_item = True
        self.list_item_needs_separator = False

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Use strong({}) function with content block
        self.add_text(f"{prefix}strong({{")

        # Store state to restore in depart. D-13: these are the rubric's OWN
        # slots (``_rubric_was_*``), no longer the ``_strong_was_*`` names
        # visit_strong/depart_strong (and visit_desc_signature/
        # depart_desc_signature) still share between themselves -- a nested
        # inline ``strong`` firing while this rubric's state is saved here
        # can no longer overwrite it and have depart_strong's own delattr
        # calls delete it out from under depart_rubric.
        self._rubric_was_in_paragraph = was_in_paragraph
        self._rubric_was_in_list_item = was_in_list_item
        self._rubric_was_list_item_needs_separator = was_list_item_needs_separator
        # --- end verbatim copy of visit_strong's body ---

    def depart_rubric(self, node: nodes.rubric) -> None:
        """
        Depart a rubric node.

        Emits a real Typst linebreak() unconditionally after the rubric
        heading (FID-04) -- a rubric option-group heading (and the
        directive-option "Options" heading) previously merged onto the same
        line as the first following option/field because a bare cosmetic
        "\\n" produces no visual break in Typst code mode (both the rubric
        and whatever follows render via strong()). A rubric always needs
        separation from what follows, so this fires unconditionally --
        verified harmless at true end-of-document (nothing follows the
        trailing linebreak()): no compile error, no visible artifact.

        ADM-06: this handler owns its own emission -- the block below started
        as a verbatim copy of depart_strong's body (D-01) rather than a
        delegation to a dummy strong() node. Phase 39 (D-13) has now made it
        diverge: it restores from its own ``_rubric_was_*`` slots, not the
        ``_strong_was_*`` names depart_strong (and depart_desc_signature)
        still share between themselves (that pair's own sharing stays
        deliberate and unedited, D-02) -- see visit_rubric's docstring for
        the full rationale.
        """
        # --- begin verbatim copy of depart_strong's body (D-01) ---
        # Close strong({}) function
        self.add_text("})")

        # Restore paragraph state
        if hasattr(self, "_rubric_was_in_paragraph"):
            self.in_paragraph = self._rubric_was_in_paragraph
            delattr(self, "_rubric_was_in_paragraph")

        # Restore in_list_item state
        if hasattr(self, "_rubric_was_in_list_item"):
            self.in_list_item = self._rubric_was_in_list_item
            delattr(self, "_rubric_was_in_list_item")

        # Restore and mark that next element needs separator
        if hasattr(self, "_rubric_was_list_item_needs_separator"):
            # Restore previous state, then mark next element needs separator
            if self.in_list_item:
                self.list_item_needs_separator = True
            delattr(self, "_rubric_was_list_item_needs_separator")

        # Restore the code-mode concat context suppressed for the strong body
        # and mark this strong as a sibling so the next term/link/desc
        # expression is + separated.
        self._exit_inline_concat_element()
        # --- end verbatim copy of depart_strong's body ---

        # depart_strong's closing "})" carries no trailing separator of its
        # own (unlike depart_desc_signature, whose unconditional trailing
        # "\n" is what makes FID-03's leading-linebreak() placement safe at
        # the NEXT signature). Without this explicit "\n" here, linebreak()
        # would directly abut "})" with zero whitespace between two
        # code-mode statements -- confirmed via a real compile this session
        # to fail with "expected semicolon or line break" (Pitfall 1's
        # class of bug, encountered at the LEADING boundary this time).
        self.add_text("\n")
        self._emit_forced_break("linebreak()")

    def visit_title_reference(self, node: nodes.title_reference) -> None:
        """
        Visit a title_reference node (reference to a title).

        Title references are rendered in emphasis using emph({}) wrapper.
        """
        # Create a dummy emphasis node and use its visitor logic
        dummy_emph = nodes.emphasis()
        self.visit_emphasis(dummy_emph)

    def depart_title_reference(self, node: nodes.title_reference) -> None:
        """Depart a title_reference node."""
        # Use emphasis's depart logic
        dummy_emph = nodes.emphasis()
        self.depart_emphasis(dummy_emph)

    # Additional signature nodes (desc_sig_* family)

    def visit_desc_sig_keyword(self, node: addnodes.desc_sig_keyword) -> None:
        """Visit a desc_sig_keyword node (keywords in signatures like 'class', 'def').

        Stays a no-op: self.in_signature_text already gives this node's
        Text children monospace via visit_Text's branch (contract
        section 4.3) -- no dedicated handler is needed.
        """
        pass

    def depart_desc_sig_keyword(self, node: addnodes.desc_sig_keyword) -> None:
        """Depart a desc_sig_keyword node."""
        pass

    def visit_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
        """Visit a desc_sig_space node (whitespace in signatures).

        Stays a no-op: self.in_signature_text already gives this node's
        Text children monospace via visit_Text's branch (contract
        section 4.3) -- no dedicated handler is needed.
        """
        pass

    def depart_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
        """Depart a desc_sig_space node."""
        pass

    def visit_desc_sig_name(self, node: addnodes.desc_sig_name) -> None:
        """
        Visit a desc_sig_name node (names in signatures) -- the D-05
        discriminator (37-EMISSION-CONTRACT.md section 5.2), three
        mutually exclusive rules evaluated in order (each SkipNode-raising
        branch below makes the remaining checks unreachable for THIS
        node, which is what "mutually exclusive" means here):

        Rule 1: the node's parent is a desc_annotation or desc_name, and
        this node is itself a text-only leaf -> emit strong(raw(...)) and
        skip. This is what makes a non-leaf desc_name (measured: the C++
        domain nests a desc_sig_name inside desc_name) bold via its
        nested child instead of via desc_name itself. If the node is NOT
        a leaf, fall through to rule 3.

        Rule 2: the parent is a desc_parameter, this node is a text-only
        leaf, and self._param_name_seen is False -> set the flag, emit
        emph(raw(...)), and skip. This is the parameter's OWN name
        (SIG-04's italic). The leaf guard is the load-bearing safety
        property: measured across every parameter shape in
        37-RESEARCH.md's D-05 table plus the C++ domain, the FIRST
        desc_sig_name direct child of a desc_parameter is always the
        parameter's own name and always a leaf, while a LATER one belongs
        to the type annotation and may be a non-leaf (wrapping a resolved
        nodes.reference) -- if a first child ever arrived non-leaf, rule 3
        must catch it rather than this rule flattening it and silently
        dropping a hyperlink.

        Rule 3 (otherwise): no-op. Children dispatch normally under
        self.in_signature_text, so a type annotation wrapping a resolved
        cross-reference keeps emitting its UNMODIFIED visit_reference
        link(...) call with the monospace primitive inside -- the flag
        fires BENEATH visit_reference, it never replaces or flattens it.

        Deliberately does NOT discriminate on addnodes.pending_xref:
        measured, the translator never sees one -- Builder.write()
        resolves references before write_doc runs, so an unresolved xref
        is stripped to plain content (a bare Text child) and a resolved
        one becomes nodes.reference. A pending_xref check here would
        silently never fire -- this is the exact wrong turn
        37-CONTEXT.md's own D-05 text invites; 37-04-SUMMARY.md's
        unresolved-C-domain-type measurement (``PyTypeObject *type``, no
        intersphinx) independently confirms the mechanical rule-2 output
        this discriminator produces for a type that never resolves.
        """
        parent = node.parent
        is_leaf = all(isinstance(child, nodes.Text) for child in node.children)

        if (
            isinstance(parent, (addnodes.desc_annotation, addnodes.desc_name))
            and is_leaf
        ):
            self._emit_signature_leaf_wrapper(node, "strong")

        if (
            isinstance(parent, addnodes.desc_parameter)
            and is_leaf
            and not self._param_name_seen
        ):
            self._param_name_seen = True
            self._emit_signature_leaf_wrapper(node, "emph")

        # Rule 3 (otherwise): pass -- children dispatch normally under
        # self.in_signature_text.

    def depart_desc_sig_name(self, node: addnodes.desc_sig_name) -> None:
        """
        Depart a desc_sig_name node.

        Only reached for rule 3 (visit_desc_sig_name's rule 1/rule 2
        leaf branches raise nodes.SkipNode, so depart is never called for
        those).
        """
        pass

    def visit_desc_sig_punctuation(self, node: addnodes.desc_sig_punctuation) -> None:
        """Visit a desc_sig_punctuation node (punctuation in signatures like ':', '=').

        Stays a no-op: self.in_signature_text already gives this node's
        Text children monospace via visit_Text's branch (contract
        section 4.3) -- no dedicated handler is needed. Not given the
        flatten-and-skip shortcut either: a keyword-only separator
        operator was measured to wrap an abbreviation node, so
        flattening here would add a subtree-dropping hazard for no gain.
        """
        pass

    def depart_desc_sig_punctuation(self, node: addnodes.desc_sig_punctuation) -> None:
        """Depart a desc_sig_punctuation node."""
        pass

    def visit_desc_sig_operator(self, node: addnodes.desc_sig_operator) -> None:
        """Visit a desc_sig_operator node (operators in signatures).

        Stays a no-op: self.in_signature_text already gives this node's
        Text children monospace via visit_Text's branch (contract
        section 4.3) -- no dedicated handler is needed. Not given the
        flatten-and-skip shortcut either: the keyword-only separator
        operator was measured to wrap an abbreviation node, and
        flattening it buys nothing while adding a subtree-dropping
        hazard.
        """
        pass

    def depart_desc_sig_operator(self, node: addnodes.desc_sig_operator) -> None:
        """Depart a desc_sig_operator node."""
        pass

    # Literal nodes for API documentation

    def _emit_field_body_monospace_leaf(
        self, node: nodes.Element, wrapper: str
    ) -> None:
        """Emit a complete ``wrapper(raw("..."))`` call for a field-body
        monospace leaf (``literal_strong`` / ``literal_emphasis``), then
        raise ``nodes.SkipNode`` -- mirroring ``visit_literal``'s leaf-
        emission shape (``typsphinx/translator.py:1487-1565``): the
        paragraph separator, the concat-separator-or-list-item-newline
        fallback, the call itself, then the mark-content-or-list-item-
        separator fallback.

        Escaping goes through the shared ``escape_typst_string`` helper
        -- the SAME one ``visit_literal``'s leaf branch uses -- and
        deliberately NOT through ``_escape_signature_text`` /
        ``_emit_signature_leaf_wrapper``. Those unconditionally inject
        the SIG-07 zero-width-space break opportunity after every ``.``,
        and no FLD-03 requirement or CONTEXT decision authorizes that
        inside a field body: field bodies are not measured to overflow
        the way dotted signature qualnames are, and a parameter name
        copied out of the PDF must stay pasteable (38-EMISSION-
        CONTRACT.md section 5.3).

        ``wrapper`` is ``"strong"`` (bold monospace -- the parameter
        name, contract section 5.2 row 1) or ``"emph"`` (italic
        monospace -- the parameter type, section 5.2 row 2), D-05's
        deliberately-different-from-the-signature-family recipe.

        No special-casing on the node's parent: a resolvable ``:type:``
        nests this call inside an emitted ``link(...)`` call, and it
        composes correctly because ``link()``'s body argument is just a
        content value -- the same reason the signature family's own
        resolved-xref rule already works (37-EMISSION-CONTRACT.md
        section 5.2 rule 3, contract section 5.4).

        Monospace is reached ONLY through Typst's ``raw(...)``
        primitive -- never by naming a font family, which would
        silently shadow the Japanese build's CJK fallback with neither
        a warning nor an error.
        """
        self._add_paragraph_separator()
        if not self._emit_inline_concat_separator():
            if self.in_list_item and self.list_item_needs_separator:
                self.add_text("\n")

        escaped = escape_typst_string(node.astext())
        prefix = "#" if self._in_markup_mode else ""
        self.add_text(f'{prefix}{wrapper}(raw("{escaped}"))')

        if not self._mark_inline_concat_content():
            if self.in_list_item:
                self.list_item_needs_separator = True

        raise nodes.SkipNode

    def visit_literal_strong(self, node: nodes.inline) -> None:
        """Visit a literal_strong node: a field-body parameter name.

        Emits ``strong(raw("<escaped>"))`` -- bold monospace (FLD-03,
        38-EMISSION-CONTRACT.md section 5.2 row 1), deliberately
        DIFFERENT from the signature family's own name recipe (D-05):
        the reference's own recipe for a field-body parameter name,
        distinct from the plain-bold proportional field label.
        Delegates to :meth:`_emit_field_body_monospace_leaf`, which
        raises ``nodes.SkipNode`` -- ``depart_literal_strong`` is
        therefore never called (mirrors ``visit_literal`` /
        ``depart_literal``).

        No longer delegates through a dummy ``nodes.strong()`` node to
        :meth:`visit_strong` (D-09) -- this is deliberate: D-05 makes
        this node's target emission (bold MONOSPACE) diverge from
        ``strong``'s own emission (bold PROPORTIONAL), so the
        delegation was no longer a viable base to build on.
        """
        self._emit_field_body_monospace_leaf(node, "strong")

    def depart_literal_strong(self, node: nodes.inline) -> None:
        """Depart a literal_strong node.

        Unreachable: ``visit_literal_strong`` raises ``nodes.SkipNode``,
        so docutils' dispatcher never calls this depart. Kept as a stub
        -- exactly as ``depart_literal`` already is -- because the
        docutils dispatcher contract still wants a paired depart method
        present.
        """
        pass

    def visit_literal_emphasis(self, node: nodes.inline) -> None:
        """Visit a literal_emphasis node: a field-body parameter type.

        Emits ``emph(raw("<escaped>"))`` -- italic monospace (FLD-03,
        38-EMISSION-CONTRACT.md section 5.2 row 2), deliberately
        DIFFERENT from the signature family's own type recipe (D-05):
        the reference's own recipe for a field-body parameter type,
        distinct from the plain-bold proportional field label.
        Delegates to :meth:`_emit_field_body_monospace_leaf`, which
        raises ``nodes.SkipNode`` -- ``depart_literal_emphasis`` is
        therefore never called (mirrors ``visit_literal`` /
        ``depart_literal``).

        No longer delegates through a dummy ``nodes.emphasis()`` node
        to :meth:`visit_emphasis` (D-09) -- the last two dummy-node
        delegation sites in the translator, removed for the same
        reason ``visit_literal_strong``'s docstring gives.
        """
        self._emit_field_body_monospace_leaf(node, "emph")

    def depart_literal_emphasis(self, node: nodes.inline) -> None:
        """Depart a literal_emphasis node.

        Unreachable: ``visit_literal_emphasis`` raises
        ``nodes.SkipNode``, so docutils' dispatcher never calls this
        depart. Kept as a stub -- exactly as ``depart_literal`` already
        is -- because the docutils dispatcher contract still wants a
        paired depart method present.
        """
        pass

"""
Phase 39, GATE-01: ADM-01/ADM-02/ADM-03 bucket-routing and catalog-title
structural gates against the tree this plan starts from.

Every expected gentle-clues function name and every expected title string
below is hand-derived from ``.planning/phases/39-admonition-taxonomy-rubric-
nesting/39-CONTEXT.md`` (the locked bucket table, D-02/D-09/D-10), from
``theme.typ``/``predefined.typ`` in the pinned gentle-clues 1.3.1 sources,
and from ``sphinx.locale.admonitionlabels`` read directly inside this
module -- never from running the translator whose defects this module
records. This is a v0.7.0 GATE-01 module: every design defect asserted here
**compiles fine today** (there is no fatal to catch), so RED is a
structural region-scoped equality/absence mismatch, never a
``sphinx-build`` failure and never a ``typst.compile()`` error.

Region-scoping methodology (T-39-06): every bucket assertion goes through
``_clue_open_before``, which resolves the gentle-clues function name that
opened the box CONTAINING a given sentinel by scanning backward from the
sentinel's position for the nearest recognized clue-function open token
(``name({``). This is deliberately NOT a document-wide substring or count
search -- either form would green whenever ANY box in the document happens
to use the expected function, which is exactly the false-positive class a
mis-routed ``seealso`` riding on the real ``tip`` construct's token would
produce.

**G-39-1 (2026-08-02):** by owner decision, after a live A/B/C render
comparison, D-03 is superseded -- the red family stops being one collapsed
``error`` function and becomes three pairwise-distinct gentle-clues
functions (``error``, ``danger``, ``memo``), one per Sphinx type. The two
red-family defect cases now expect their own function rather than the
folded ``error`` function, and a new generalized invariant test asserts the
whole family's distinctness and title provenance in one build so a future
silent re-collapse fails rather than passes. This module's docstring
history at the point D-03 was first satisfied lives in
``39-GATE-EVIDENCE-01.md``; the G-39-1 reversal is recorded in
``39-GATE-EVIDENCE-05.md``.

Against the tree this plan starts from, this module reports:

- RED (must flip GREEN once ``visit_danger`` and ``visit_attention`` are
  re-routed to their own red-family function, per G-39-1 / plan 39-11): the
  two red-family point assertions (attention -> ``memo``, danger ->
  ``danger``) and the generalized red-family invariant test, whose
  distinctness assertion fails because all three red-family sentinels
  currently resolve to the single folded ``error`` function.
- GREEN throughout, by design, as CONTROLS (must never be "fixed" into a
  defect case): the seealso/generic-admonition/topic bucket tests and the
  catalog-title table-driven test (D-02/D-09/D-10/D-04/D-05 were already
  satisfied by earlier plans in this phase), the seven-type
  bucket-stability test (note, warning, tip, important, caution, hint,
  error -- none of these seven ever contained danger or attention, so the
  red-family sub-division does not touch this table), the base-``clue``-
  function absence guard over this plan's own ten admonition-fixture
  sentinels (unaffected: neither ``danger`` nor ``memo`` is the base
  ``clue`` function), the "attention is not in the warning bucket" test
  (ADM-02's surviving intent -- green whether attention resolves to
  ``error`` today or ``memo`` after the routing lands, because neither is
  ``warning``), and the ``_clue_open_before`` self-checks (a missing
  sentinel raises ``AssertionError`` naming the sentinel, independent of
  any fixture build).

See ``.planning/phases/39-admonition-taxonomy-rubric-nesting/
39-GATE-EVIDENCE-05.md`` for the verbatim RED/CONTROL split recorded
against a named commit, the corrected fixture-blast-radius grep, and the
measured ``lang.toml``/``theme.typ`` provenance.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest
from sphinx.locale import admonitionlabels

# ---------------------------------------------------------------------------
# Fixture / build plumbing
# ---------------------------------------------------------------------------


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (NEVER ``uv run sphinx-build``)
    -- the NixOS PATH-shadowing hazard restated in every render-gate module
    in this project (``tests/test_pdf_render_gate.py``'s own
    ``_run_sphinx_build_typst`` is the canonical form this clones): a stray
    non-Nix ``uv`` binary shadowing the correct Nix-provided ``uv`` earlier
    on PATH for subprocess children makes ``["uv", "run", ...]`` exit 127
    ("Could not start dynamically linked executable") when invoked from
    inside a pytest-launched subprocess, even though the same command
    succeeds when run directly in a shell. ``sys.executable -m sphinx``
    sidesteps that PATH-shadowing hazard entirely by reusing the exact
    interpreter/venv already running this test.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typst",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="session")
def admonition_bucket_gate_dir() -> Path:
    """Return the path to the admonition_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "admonition_render_gate"


@pytest.fixture(scope="session")
def topic_bucket_gate_dir() -> Path:
    """Return the path to the topic_line_block_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "topic_line_block_render_gate"


@pytest.fixture(scope="session")
def admonition_bucket_typ_text(
    admonition_bucket_gate_dir: Path, tmp_path_factory: pytest.TempPathFactory
) -> str:
    """
    Build ``admonition_render_gate`` once through ``-b typst`` for the whole
    session and return the emitted ``index.typ`` text.
    """
    build_dir = tmp_path_factory.mktemp("admonition_bucket_typ") / "_build"
    result = _run_sphinx_build_typst(admonition_bucket_gate_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return index_typ.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def topic_bucket_typ_text(
    topic_bucket_gate_dir: Path, tmp_path_factory: pytest.TempPathFactory
) -> str:
    """
    Build ``topic_line_block_render_gate`` once through ``-b typst`` for the
    whole session and return the emitted ``index.typ`` text.
    """
    build_dir = tmp_path_factory.mktemp("topic_bucket_typ") / "_build"
    result = _run_sphinx_build_typst(topic_bucket_gate_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return index_typ.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Region-scoping helpers
# ---------------------------------------------------------------------------

# The full set of gentle-clues function names any admonition/topic call site
# in typsphinx/translator.py can pass as `clue_type` to `_visit_admonition`
# -- note/success/warning/error-family bucket functions, the two non-bucket
# D-09/D-10 functions, `task` (todo_node, unchanged by this phase), and the
# base `clue` function itself (present pre-phase; disappears as a passed
# value after this phase per the phase-wide artifact census).
#
# G-39-1 (2026-08-02): `memo` is added here BEFORE any assertion below is
# re-targeted. `_CLUE_OPEN_RE` is built from this tuple, and
# `_clue_open_before` resolves a sentinel's box by scanning BACKWARD for the
# nearest recognized open token -- if `memo` were absent, the attention
# sentinel would resolve past its own box to whichever box precedes it in
# the fixture, reporting a neighbour's function name instead of raising. See
# the interpreter check recorded in 39-09-SUMMARY.md.
_CLUE_FUNCTION_NAMES = (
    "info",
    "tip",
    "warning",
    "error",
    "danger",
    "memo",
    "notify",
    "abstract",
    "task",
    "clue",
)

# `name({` -- the exact box-open shape `_visit_admonition` emits
# (`self.add_text(f"{clue_type}({{")`). Restricted to the known clue-function
# name set above so that OTHER identifier+({ shapes in the same document
# (most notably `par({`, which every admonition body itself opens with) are
# never mistaken for a clue box open.
_CLUE_OPEN_RE = re.compile(r"\b(" + "|".join(_CLUE_FUNCTION_NAMES) + r")\(\{")


def _clue_open_before(typ_text: str, sentinel: str) -> str:
    """
    Resolve which gentle-clues function opened the box CONTAINING
    ``sentinel``, region-scoped (T-39-06): locate ``sentinel`` in
    ``typ_text``, then scan BACKWARD for the nearest preceding clue-function
    box-open token and return just its function name.

    Raises ``AssertionError`` naming ``sentinel`` when the sentinel is
    absent from ``typ_text``, or when no clue-function box-open token
    precedes it -- so a fixture rename or a genuinely un-boxed sentinel
    fails as a clear structural assertion rather than surfacing as an
    uncaught ``ValueError``/``IndexError`` deep inside test internals.
    """
    sentinel_idx = typ_text.find(sentinel)
    if sentinel_idx == -1:
        raise AssertionError(
            f"{sentinel}: sentinel not found in emitted .typ text -- "
            "has the fixture been renamed or the sentinel removed?"
        )
    preceding = typ_text[:sentinel_idx]
    matches = list(_CLUE_OPEN_RE.finditer(preceding))
    if not matches:
        raise AssertionError(
            f"{sentinel}: no gentle-clues box-open token precedes this "
            "sentinel in the emitted .typ text -- the sentinel is not "
            "inside any recognized clue box"
        )
    return matches[-1].group(1)


def _title_arg_after(typ_text: str, sentinel: str) -> str | None:
    """
    Return the literal ``title:`` argument attached to the box containing
    ``sentinel`` -- the exact substring ``_depart_admonition`` appends after
    the body closes (either a quoted static literal like ``"See also"`` or a
    braced dynamic expression like ``{text("...")}``) -- or ``None`` when no
    title argument is present.

    Region-scoped exactly like ``_clue_open_before``: this locates the SAME
    box-open token, then balance-matches its content block's closing brace
    (bodies may themselves contain nested ``{``/``}`` from nested boxes,
    lists, etc., so a naive first-``}`` search would truncate early) before
    inspecting what immediately follows for a ``, title: ...`` argument.

    Raises ``AssertionError`` naming ``sentinel`` under the same conditions
    as ``_clue_open_before`` (sentinel absent / no enclosing box), and also
    if the enclosing box's braces are unbalanced or the title argument has
    an unrecognized shape (neither a quoted string nor a braced block) --
    every such failure names the sentinel so it is traceable back to one
    region.
    """
    sentinel_idx = typ_text.find(sentinel)
    if sentinel_idx == -1:
        raise AssertionError(
            f"{sentinel}: sentinel not found in emitted .typ text -- "
            "has the fixture been renamed or the sentinel removed?"
        )
    preceding = typ_text[:sentinel_idx]
    matches = list(_CLUE_OPEN_RE.finditer(preceding))
    if not matches:
        raise AssertionError(
            f"{sentinel}: no gentle-clues box-open token precedes this "
            "sentinel in the emitted .typ text -- the sentinel is not "
            "inside any recognized clue box"
        )
    open_match = matches[-1]
    # The box's content block starts at the '{' immediately after the
    # matched "name({" token, i.e. one character before the match's end.
    body_start = open_match.end() - 1
    depth = 0
    i = body_start
    while i < len(typ_text):
        if typ_text[i] == "{":
            depth += 1
        elif typ_text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    else:
        raise AssertionError(
            f"{sentinel}: unbalanced braces scanning the enclosing box's "
            "content block -- could not locate its matching closing brace"
        )
    body_end = i  # index of the matching closing '}'

    rest = typ_text[body_end + 1 :]
    stripped = rest.lstrip()
    if not stripped.startswith(", title:"):
        return None

    after_title = stripped[len(", title:") :].lstrip()
    if after_title.startswith('"'):
        # Quoted string literal -- find the closing unescaped quote.
        j = 1
        while j < len(after_title):
            if after_title[j] == "\\":
                j += 2
                continue
            if after_title[j] == '"':
                j += 1
                break
            j += 1
        else:
            raise AssertionError(
                f"{sentinel}: unterminated quoted title literal while "
                "scanning the title argument"
            )
        return after_title[:j]
    if after_title.startswith("{"):
        depth = 0
        j = 0
        while j < len(after_title):
            if after_title[j] == "{":
                depth += 1
            elif after_title[j] == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        else:
            raise AssertionError(
                f"{sentinel}: unbalanced braces scanning a braced title " "argument"
            )
        return after_title[:j]
    raise AssertionError(
        f"{sentinel}: title argument has an unrecognized shape "
        f"(neither a quoted string nor a braced block): "
        f"{after_title[:40]!r}"
    )


# ---------------------------------------------------------------------------
# `_clue_open_before` self-check (ADM-01/ADM-03 must_haves.prohibitions):
# provable independent of any fixture build that the region-scoping helper
# fails structurally, by name, rather than silently matching nothing.
# ---------------------------------------------------------------------------


def test_clue_open_before_raises_on_missing_sentinel() -> None:
    """A sentinel absent from the .typ text raises AssertionError naming it."""
    with pytest.raises(AssertionError, match="NOSUCHSENTINEL"):
        _clue_open_before('info({par({text("hello")})})', "NOSUCHSENTINEL")


def test_clue_open_before_raises_when_no_box_precedes_sentinel() -> None:
    """A sentinel present but with no preceding clue-function open raises."""
    with pytest.raises(AssertionError, match="LONESENTINEL"):
        _clue_open_before('par({text("LONESENTINEL body")})', "LONESENTINEL")


# ---------------------------------------------------------------------------
# DEFECT CASES -- ADM-01 (D-02), ADM-02/G-39-1 (attention -> memo, danger ->
# danger, each its own red-family function), ADM-03 (D-09, D-10).
# Each is RED against the untouched translator; each fails message names its
# decision. must_haves.prohibitions (ADM-01/ADM-03): every expected function
# name below is transcribed from 39-CONTEXT.md's locked bucket table (as
# reversed by G-39-1 for the red family) or from `theme.typ`/`predefined.typ`
# read directly, never read back from the translator's current output.
# ---------------------------------------------------------------------------


def test_seealso_routes_to_tip_bucket(admonition_bucket_typ_text: str) -> None:
    """D-02: seealso joins the success bucket (tip), not the note bucket."""
    actual = _clue_open_before(admonition_bucket_typ_text, "ADMONSEEALSOSENTINEL")
    assert actual == "tip", (
        f"D-02 violated: expected seealso's box to open with 'tip' "
        f"(the success bucket), got {actual!r}"
    )


def test_attention_routes_to_memo_function(admonition_bucket_typ_text: str) -> None:
    """G-39-1: attention resolves to its own 'memo' function, superseding
    D-03 -- the red family is three pairwise-distinct gentle-clues functions,
    not one collapsed function."""
    actual = _clue_open_before(admonition_bucket_typ_text, "ADMONATTENTIONSENTINEL")
    assert actual == "memo", (
        f"G-39-1 violated: expected attention's box to open with 'memo' "
        f"(its own red-family function, superseding D-03's single-function "
        f"fold), got {actual!r}"
    )


def test_danger_routes_to_danger_function(admonition_bucket_typ_text: str) -> None:
    """G-39-1: danger resolves to its own 'danger' function, superseding
    D-03 -- the red family is three pairwise-distinct gentle-clues functions,
    not one collapsed function."""
    actual = _clue_open_before(admonition_bucket_typ_text, "ADMONDANGERSENTINEL")
    assert actual == "danger", (
        f"G-39-1 violated: expected danger's box to open with 'danger' "
        f"(its own red-family function, superseding D-03's single-function "
        f"fold), got {actual!r}"
    )


# ---------------------------------------------------------------------------
# G-39-1: the generalized red-family invariant. A bucket is a gentle-clues
# function name, never a colour argument (D-01, still standing) -- so the
# red family's membership is asserted by function id, never by the accent
# colour literal that would otherwise identify it. Provenance (NOT test
# data) for each red-family id, hand-transcribed from
# ``~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/theme.typ`` this
# planning session:
#   - error:  accent rgb(210, 15, 57)  #d20f39 (red),    icon "crossmark.svg"
#   - danger: accent rgb(254, 100, 11) #fe640b (peach),  icon "danger.svg"
#   - memo:   accent rgb(230, 69, 83)  #e64553 (maroon), icon "excl.svg"
# ---------------------------------------------------------------------------

_RED_FAMILY_FUNCTIONS = ("error", "danger", "memo")


def test_red_family_types_route_to_distinct_clue_functions(
    admonition_bucket_typ_text: str,
) -> None:
    """
    G-39-1: the red family is three pairwise-distinct gentle-clues functions,
    not one collapsed function. Resolves all three red-family sentinels from
    ONE build (proving region-scope resolution stays stable when three
    equal-family boxes sit adjacent in the fixture), then asserts, in order:
    every resolved name is a member of ``_RED_FAMILY_FUNCTIONS``; the three
    names are pairwise distinct; and each of the three boxes carries a title
    argument, via ``_title_arg_after``, equal to the quoted
    ``sphinx.locale.admonitionlabels`` value for that type. RED today: all
    three sentinels resolve to ``error``, so the distinctness assertion
    fails even though the membership assertion (vacuously) does not.
    """
    sentinel_by_type = {
        "attention": "ADMONATTENTIONSENTINEL",
        "danger": "ADMONDANGERSENTINEL",
        "error": "ADMONERRORSENTINEL",
    }
    resolved = {
        node_type: _clue_open_before(admonition_bucket_typ_text, sentinel)
        for node_type, sentinel in sentinel_by_type.items()
    }

    non_members = {
        node_type: fn
        for node_type, fn in resolved.items()
        if fn not in _RED_FAMILY_FUNCTIONS
    }
    assert not non_members, (
        "G-39-1 violated: red-family type(s) resolved to a function outside "
        f"the hand-transcribed red-family set {_RED_FAMILY_FUNCTIONS!r}: "
        f"{non_members}"
    )

    resolved_functions = list(resolved.values())
    assert len(set(resolved_functions)) == len(resolved_functions), (
        "G-39-1 violated: the red family is not three pairwise-distinct "
        f"gentle-clues functions -- resolved {resolved!r}"
    )

    title_mismatches = []
    for node_type, sentinel in sentinel_by_type.items():
        expected_title = f'"{str(admonitionlabels[node_type])}"'
        actual_title = _title_arg_after(admonition_bucket_typ_text, sentinel)
        if actual_title != expected_title:
            title_mismatches.append(
                f"{sentinel} ({node_type}): expected {expected_title!r}, "
                f"got {actual_title!r}"
            )
    assert not title_mismatches, "Red-family title mismatch(es):\n" + "\n".join(
        title_mismatches
    )


def test_attention_is_not_in_the_warning_bucket(
    admonition_bucket_typ_text: str,
) -> None:
    """
    ADM-02's surviving intent, stated positively: leaving the orange warning
    bucket was the requirement; being byte-identical to the error type was
    only ever one way of expressing it, and G-39-1 supersedes that way.
    Green in both directions (today attention resolves to 'error', which
    already differs from 'warning'; after the routing lands it resolves to
    'memo', which still differs) -- this test must never be converted into a
    defect case.
    """
    attention_fn = _clue_open_before(
        admonition_bucket_typ_text, "ADMONATTENTIONSENTINEL"
    )
    warning_family_sentinels = (
        "ADMONWARNINGSENTINEL",
        "ADMONCAUTIONSENTINEL",
        "ADMONIMPORTANTSENTINEL",
    )
    collisions = []
    for sentinel in warning_family_sentinels:
        fn = _clue_open_before(admonition_bucket_typ_text, sentinel)
        if fn == attention_fn:
            collisions.append(f"{sentinel} shares {fn!r} with attention")
    assert not collisions, (
        "ADM-02 violated: attention shares a function with the warning "
        "bucket:\n" + "\n".join(collisions)
    )


def test_generic_admonition_routes_to_notify(topic_bucket_typ_text: str) -> None:
    """D-09: the generic .. admonition:: directive emits notify(), not clue()."""
    actual = _clue_open_before(topic_bucket_typ_text, "ADMONITIONCUSTOMSENTINEL")
    assert actual == "notify", (
        f"D-09 violated: expected the generic admonition's box to open "
        f"with 'notify', got {actual!r}"
    )


def test_topic_routes_to_abstract(topic_bucket_typ_text: str) -> None:
    """D-10: the .. topic:: directive emits abstract(), not clue()."""
    actual = _clue_open_before(topic_bucket_typ_text, "TOPICBODYSENTINEL")
    assert actual == "abstract", (
        f"D-10 violated: expected the topic's box to open with "
        f"'abstract', got {actual!r}"
    )


# ---------------------------------------------------------------------------
# CONTROLS -- these seven types' bucket routing does not move this phase.
# GREEN in both directions; this test must NEVER be converted into a defect
# case against any of these seven types.
# ---------------------------------------------------------------------------

# (sentinel, expected gentle-clues function) -- see 39-CONTEXT.md's locked
# bucket table. important/caution are CONTROL despite being folded into the
# `warning` function, because they are already routed there pre-phase.
_CONTROL_BUCKETS = (
    ("ADMONNOTESENTINEL", "info"),
    ("ADMONWARNINGSENTINEL", "warning"),
    ("ADMONTIPSENTINEL", "tip"),
    ("ADMONIMPORTANTSENTINEL", "warning"),
    ("ADMONCAUTIONSENTINEL", "warning"),
    ("ADMONHINTSENTINEL", "tip"),
    ("ADMONERRORSENTINEL", "error"),
)


def test_control_buckets_never_move(admonition_bucket_typ_text: str) -> None:
    """
    CONTROL: note, warning, tip, important, caution, hint and error keep
    their pre-phase bucket. This test must never be converted into a defect
    case for any of these seven types -- doing so would mean one of this
    milestone's non-moving buckets silently started moving.
    """
    mismatches = []
    for sentinel, expected in _CONTROL_BUCKETS:
        actual = _clue_open_before(admonition_bucket_typ_text, sentinel)
        if actual != expected:
            mismatches.append(f"{sentinel}: expected {expected!r}, got {actual!r}")
    assert not mismatches, "CONTROL bucket(s) moved:\n" + "\n".join(mismatches)


# ---------------------------------------------------------------------------
# Catalog titles -- D-04/D-05. Table-driven over all ten admonitionlabels-
# keyed types. Expected strings are read from sphinx.locale.admonitionlabels
# INSIDE this test (coercing the lazy i18n proxy with str()), never
# transcribed as literals, so the test cannot drift from the catalog.
# ---------------------------------------------------------------------------

# (sentinel, admonitionlabels key) -- the ten real Sphinx admonition types
# that have an entry in sphinx.locale.admonitionlabels. The generic
# .. admonition:: and .. topic:: directives are NOT in this table: they have
# no catalog entry and keep their existing node-supplied dynamic title path
# (D-09/D-10 change only which function boxes them, not their title source).
_CATALOG_TITLE_SENTINELS = (
    ("ADMONNOTESENTINEL", "note"),
    ("ADMONWARNINGSENTINEL", "warning"),
    ("ADMONTIPSENTINEL", "tip"),
    ("ADMONIMPORTANTSENTINEL", "important"),
    ("ADMONCAUTIONSENTINEL", "caution"),
    ("ADMONSEEALSOSENTINEL", "seealso"),
    ("ADMONHINTSENTINEL", "hint"),
    ("ADMONERRORSENTINEL", "error"),
    ("ADMONDANGERSENTINEL", "danger"),
    ("ADMONATTENTIONSENTINEL", "attention"),
)


def test_admonition_titles_match_locale_catalog(
    admonition_bucket_typ_text: str,
) -> None:
    """
    D-04/D-05: every one of the ten catalog-keyed admonition types carries
    its English ``sphinx.locale.admonitionlabels`` value as its title
    argument. RED today for eight of the ten (no title argument is emitted
    at all) and RED for seealso (casing: today's static literal is
    ``"See Also"``, the catalog's is ``"See also"``); GREEN today only for
    important (its pre-existing static ``custom_title="Important"`` already
    matches the catalog value byte-for-byte).
    """
    mismatches = []
    for sentinel, catalog_key in _CATALOG_TITLE_SENTINELS:
        expected_title = str(admonitionlabels[catalog_key])
        expected = f'"{expected_title}"'
        actual = _title_arg_after(admonition_bucket_typ_text, sentinel)
        if actual != expected:
            mismatches.append(
                f"{sentinel} ({catalog_key}): expected {expected!r}, " f"got {actual!r}"
            )
    assert not mismatches, "Catalog title mismatch(es):\n" + "\n".join(mismatches)


# ---------------------------------------------------------------------------
# Negative-direction guard for D-10's consequence -- the base `clue`
# function disappears as a value passed anywhere in typsphinx/ after this
# phase. Scoped to this plan's own ten admonition-fixture sentinels (see
# module docstring for why ADMONITIONCUSTOMSENTINEL/TOPICBODYSENTINEL are
# deliberately excluded: they are the D-09/D-10 DEFECT CASES tested above,
# and re-testing "not clue" for them here would just restate those
# equality assertions in negative form as an UNCOUNTED extra RED). Region-
# scoped via `_clue_open_before`, never a document-wide search.
# ---------------------------------------------------------------------------

_ALL_ADMONITION_FIXTURE_SENTINELS = tuple(
    sentinel for sentinel, _ in _CONTROL_BUCKETS
) + ("ADMONSEEALSOSENTINEL", "ADMONATTENTIONSENTINEL", "ADMONDANGERSENTINEL")


def test_no_real_admonition_type_ever_uses_base_clue(
    admonition_bucket_typ_text: str,
) -> None:
    """
    None of the ten real Sphinx admonition types (as opposed to the generic
    ``.. admonition::``/``.. topic::`` directives) ever routes through the
    base gentle-clues ``clue`` function, pre-phase or post-phase -- GREEN
    today by construction, and stays GREEN once D-09/D-10 land.
    """
    mismatches = []
    for sentinel in _ALL_ADMONITION_FIXTURE_SENTINELS:
        actual = _clue_open_before(admonition_bucket_typ_text, sentinel)
        if actual == "clue":
            mismatches.append(sentinel)
    assert not mismatches, (
        "Real admonition type(s) unexpectedly routed through the base "
        f"'clue' function: {mismatches}"
    )

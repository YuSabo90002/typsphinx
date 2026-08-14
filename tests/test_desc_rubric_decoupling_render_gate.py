"""
Phase 36's SC#1/SC#2 gate for the ADM-06 desc_signature/rubric decoupling.

D-01 says ``visit_strong``'s body must be copied verbatim into
``visit_desc_signature``/``depart_desc_signature`` and
``visit_rubric``/``depart_rubric`` -- each gets its own full copy of the
logic they currently borrow via a throwaway ``nodes.strong()`` dummy node
and a delegated call into ``visit_strong``/``depart_strong``. Every prior
GATE-01 fixture in this repo proved a compile fatal (RED == ``TypstError``,
GREEN == a valid ``%PDF``); ADM-06's defect already compiles fine today, so
milestone invariant #4 (v0.7.0's GATE-01 methodology change) redefines RED
here as two structural assertions instead:

- SC#1 (this module's ``test_desc_signature_and_rubric_do_not_delegate_to_
  visit_strong``): the four decoupled methods must no longer call
  ``self.visit_strong``/``self.depart_strong`` on a dummy node. At the time
  this gate was authored, ``visit_literal_strong``/``depart_literal_strong``
  -- a different, unrelated shared-delegation site (FLD-03's bold literal
  field-list values) -- were required to KEEP delegating, as an "over-reach
  guard" against a decoupling that went further than ADM-06's own four
  targets. Pre-decoupling (Phase 36) this failed: all six sites still
  delegated, and this method's own RED capture (recorded in
  ``36-GATE-EVIDENCE.md``) IS the RED substitute for a compile fatal.

  **Phase 38 (38-07, D-05/D-09) inverts the over-reach guard's own
  premise.** FLD-03 gives ``literal_strong``/``literal_emphasis`` their own
  leaf-emission bodies (bold/italic MONOSPACE, diverging from ``strong``'s
  plain bold PROPORTIONAL emission), so the delegation this guard protected
  is no longer a viable implementation and is itself removed -- the last
  two dummy-node delegation sites in the translator. ``NO_LONGER_
  DELEGATING_METHODS`` below (renamed from the Phase-36-era
  ``RETAINED_DELEGATION_METHODS``) and the ``DUMMY_STRONG_LITERAL`` count
  are updated to assert the post-Phase-38 state: zero delegating calls, zero
  remaining ``dummy_strong = nodes.strong()`` constructions. This migration
  is recorded in ``38-TEST-CENSUS.md`` row A2, which explicitly names this
  exact assertion as one Phase 38 legitimately trips and must rewrite in the
  same commit that removes the delegation, not just the code under test.
- SC#2 (``test_emitted_typ_is_byte_identical_to_golden``): the decoupling
  must not change a single emitted byte. Golden-file equality against
  ``golden.typ`` (captured from this same commit, before any decoupling
  edit exists -- D-07) stands in for "does not compile" as the assertion
  that would catch a regression.

``test_decoupling_fixture_still_compiles_to_pdf`` is a cheap compile-sanity
leg (36-RESEARCH.md Open Question 2) confirming the fixture -- which
combines a signature, sibling signatures, plain bold, an autodoc-style
Options rubric, a rubric with a propagated target inside a list item, and a
trailing rubric -- still reaches a valid PDF through the real
``typst.compile()`` path; it asserts nothing about PDF size or bytes
(Typst embeds a build timestamp in the PDF trailer, so PDF bytes are never
reproducible -- see ``36-CONTEXT.md`` D-04).

Only SC#1 and SC#2 run everywhere (no class-level skip -- a class-level skip
would let both pass silently by never running); the compile-sanity leg alone
is skipped when ``typst-py`` is unavailable.
"""

import ast
import difflib
import re
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

# Resolved relative to this test file's own location, never a bare relative
# path -- pytest may be invoked from any working directory.
TRANSLATOR_PATH = Path(__file__).resolve().parents[1] / "typsphinx" / "translator.py"

# The four methods D-01 requires to stop delegating to visit_strong/
# depart_strong (the ADM-06 decoupling target).
DECOUPLED_METHODS = (
    "visit_desc_signature",
    "depart_desc_signature",
    "visit_rubric",
    "depart_rubric",
)

# Phase 36's over-reach guard named these two methods as the ones that must
# KEEP delegating (a decoupling that also stripped FLD-03's bold-literal
# node handling would have failed that half of the assertion even though
# SC#1's own grep only names the desc_signature/rubric sites). Phase 38
# (38-07, D-05/D-09) removes literal_strong/literal_emphasis's own
# delegation -- FLD-03's bold/italic-MONOSPACE emission diverges from
# strong's/emph's plain-proportional emission, so delegating is no longer a
# viable base. Renamed and inverted accordingly: these two methods must now
# emit ZERO delegating calls, same as the four DECOUPLED_METHODS above.
NO_LONGER_DELEGATING_METHODS = (
    "visit_literal_strong",
    "depart_literal_strong",
)

# The literal dummy-node construction line every delegation site emitted
# before calling into visit_strong/depart_strong. Phase 36 left exactly 2
# (both owned by literal_strong); Phase 38's 38-07 removes those last 2, so
# the post-38-07 count is 0.
DUMMY_STRONG_LITERAL = "dummy_strong = nodes.strong()"


@pytest.fixture
def desc_rubric_decoupling_render_gate_dir():
    """Return the path to the desc_rubric_decoupling_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "desc_rubric_decoupling_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never bare ``sphinx-build`` /
    ``uv run sphinx-build``) so the exact interpreter/venv already running
    this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard (project memory: "NixOS sandbox test env").
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


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text). Same invocation shape as
    ``_run_sphinx_build_typst`` above.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


def _delegating_calls_in(func_node: ast.AST) -> list[str]:
    """
    Walk an ``ast`` function node and return the attribute names of every
    call of the form ``self.<name>(...)`` where ``<name>`` is
    ``visit_strong`` or ``depart_strong``.

    An empty list means the function contains no such delegating call.
    """
    delegating_names = {"visit_strong", "depart_strong"}
    found = []
    for sub_node in ast.walk(func_node):
        if not isinstance(sub_node, ast.Call):
            continue
        call_target = sub_node.func
        if not isinstance(call_target, ast.Attribute):
            continue
        if not isinstance(call_target.value, ast.Name):
            continue
        if call_target.value.id != "self":
            continue
        if call_target.attr in delegating_names:
            found.append(call_target.attr)
    return found


class TestDescRubricDecouplingRenderGate:
    """
    Phase 36's SC#1/SC#2 gate: the ADM-06 decoupling must (1) stop
    ``desc_signature``/``rubric`` from delegating to ``visit_strong``/
    ``depart_strong`` via a dummy ``strong`` node, and (2) change zero
    emitted bytes for the fixture's combined constructs. Originally (1) also
    required ``literal_strong``'s own delegation to survive untouched (the
    "over-reach guard"); Phase 38's 38-07 (D-05/D-09) legitimately removes
    that delegation too, so (1) now asserts zero delegating calls across all
    six historically-delegating methods -- see ``NO_LONGER_DELEGATING_
    METHODS`` above.

    Requirements: ADM-06.
    """

    def test_desc_signature_and_rubric_do_not_delegate_to_visit_strong(self):
        """
        The SC#1 assertion. Parses ``typsphinx/translator.py`` with
        ``ast.parse`` and checks, by method name, which handlers still call
        ``self.visit_strong``/``self.depart_strong`` on a dummy node.

        Pre-decoupling (this plan) this assertion FAILS -- all six
        delegation sites still exist, so this is the recorded RED. Runs
        unconditionally: no fixture, no typst-py requirement, and no skip.
        """
        source_text = TRANSLATOR_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source_text, filename=str(TRANSLATOR_PATH))

        functions_by_name: dict[str, ast.AST] = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions_by_name[node.name] = node

        # (a) The four decoupled methods must exist and must NOT delegate.
        for method_name in DECOUPLED_METHODS:
            assert method_name in functions_by_name, (
                f"Expected typsphinx/translator.py to define {method_name!r} "
                "-- the decoupling target is missing entirely."
            )
            delegating_calls = _delegating_calls_in(functions_by_name[method_name])
            assert delegating_calls == [], (
                f"{method_name} still delegates to {delegating_calls} via a "
                "dummy strong() node -- the ADM-06 decoupling (D-01: copy "
                "visit_strong's body verbatim instead of delegating) has not "
                "been applied yet."
            )

        # (b) Post-38-07: literal_strong/literal_emphasis must NOT delegate
        # either -- D-09 removed the last two dummy-node delegation sites in
        # the translator (38-TEST-CENSUS.md row A2's inversion).
        for method_name in NO_LONGER_DELEGATING_METHODS:
            assert method_name in functions_by_name, (
                f"Expected typsphinx/translator.py to define {method_name!r} "
                "-- literal_strong's own handlers must not be removed, only "
                "stop delegating."
            )
            delegating_calls = _delegating_calls_in(functions_by_name[method_name])
            assert delegating_calls == [], (
                f"{method_name} still delegates to {delegating_calls} via a "
                "dummy strong() node -- Phase 38's 38-07 (D-05/D-09) removes "
                "literal_strong's delegation to visit_strong/depart_strong: "
                "FLD-03's target emission (bold MONOSPACE) diverges from "
                "strong's own emission (bold PROPORTIONAL), so the "
                "delegation is no longer a viable base."
            )

        # (c) Zero remaining dummy-node construction sites. Phase 36 left
        # exactly 2 (both owned by literal_strong, the "over-reach guard"
        # surviving pair); Phase 38's 38-07 removes those last 2, so the
        # count inverts from ``== 2`` to ``== 0``.
        dummy_strong_count = source_text.count(DUMMY_STRONG_LITERAL)
        assert dummy_strong_count == 0, (
            f"Expected zero occurrences of {DUMMY_STRONG_LITERAL!r} in "
            "typsphinx/translator.py after 38-07's decoupling -- "
            "visit_literal_strong/depart_literal_strong no longer construct "
            f"a dummy strong() node -- found {dummy_strong_count}."
        )

    def test_emitted_typ_is_byte_identical_to_golden(
        self, desc_rubric_decoupling_render_gate_dir, temp_build_dir
    ):
        """
        The SC#2 assertion. Builds the fixture with ``-b typst`` and
        compares the emitted ``index.typ`` against the committed
        ``golden.typ`` (captured from this same pre-decoupling commit,
        D-07) with exact ``str`` equality. Runs unconditionally: no
        typst-py requirement (no compile needed for a ``-b typst`` build),
        and no skip.

        Phase 48 plan 07 (G-48-4 / XREF-03): ``golden.typ`` gained one line
        (``[#metadata(none) <index:__tsx-doc__>]``) immediately after the
        opening ``#{`` -- every content file with a builder-supplied
        current docname now emits its own whole-document self-anchor there
        (``48-EXPECTED-STRUCTURE.md`` "Phase 48 Plan 05" section 2's
        definition-site form, docname ``index``). This fixture's own
        content is otherwise untouched by this phase.
        """
        result = _run_sphinx_build_typst(
            desc_rubric_decoupling_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        actual_typ = typ_output.read_text(encoding="utf-8")

        golden_path = desc_rubric_decoupling_render_gate_dir / "golden.typ"
        golden_typ = golden_path.read_text(encoding="utf-8")

        assert actual_typ == golden_typ, (
            "Emitted .typ differs from the committed golden -- SC#2's "
            "byte-identity requirement is violated:\n"
            + "\n".join(
                difflib.unified_diff(
                    golden_typ.splitlines(),
                    actual_typ.splitlines(),
                    fromfile="golden.typ",
                    tofile="actual index.typ",
                    lineterm="",
                )
            )
        )

    @pytest.mark.skipif(
        not TYPST_AVAILABLE,
        reason="typst-py is required for the compile-sanity leg",
    )
    def test_decoupling_fixture_still_compiles_to_pdf(
        self, desc_rubric_decoupling_render_gate_dir, temp_build_dir
    ):
        """
        The cheap compile-sanity leg (36-RESEARCH.md Open Question 2).
        Builds the fixture with ``-b typstpdf`` and confirms it still
        reaches a valid PDF. Asserts nothing about PDF size or bytes --
        Typst embeds a build timestamp in the PDF trailer, so PDF bytes are
        never reproducible (36-CONTEXT.md D-04).
        """
        result = _run_sphinx_build_typstpdf(
            desc_rubric_decoupling_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        for fatal_signature in (
            "expected semicolon or line break",
            "expected comma",
            "Typst compilation failed",
        ):
            assert fatal_signature not in result.stderr, (
                f"typst.compile() rejected the fixture -- {fatal_signature!r} "
                f"found in stderr:\n{result.stderr}"
            )

        # Phase 47: TypstPDFBuilder compiles only wrapper files (R4). This
        # fixture's typst_documents entry targets "master.typ" (de-collided
        # from the pre-Phase-47 "index", which self-collided with the
        # docname-derived content file, index.typ) -- so the compiled PDF is
        # master.pdf, not index.pdf.
        pdf_output = temp_build_dir / "master.pdf"
        assert (
            pdf_output.exists()
        ), f"master.pdf was not produced:\nstderr: {result.stderr}"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_propagated_target_rubric_separator_run_is_not_yet_one(
        self, desc_rubric_decoupling_render_gate_dir, temp_build_dir
    ):
        """
        Phase 39's D-11 wart RED. RED today; expected GREEN once plan 39-06
        lands the fix. Measures the run of newline characters between the
        propagated-target anchor
        (``[#metadata(none) <index:decoupling-rubric-in-list-target>]``,
        emitted for the rubric inside the fixture's list item) and the
        following rubric's ``strong({`` wrapper open.

        Hand derivation, newline by newline, against
        ``typsphinx/translator.py:394-465`` (``_emit_id_anchors``) and
        ``typsphinx/translator.py:5789-5798`` (``visit_rubric``'s opening
        block) -- NOT authored by running a candidate fix and copying its
        output (``must_haves.prohibitions``, ADM-05):

        - ``_emit_id_anchors`` line 460-461: because ``in_list_item`` and
          ``list_item_needs_separator`` are both ``True`` (set by the
          preceding "First bullet text." list-item text), it appends ONE
          leading ``"\\n"`` before the anchor.
        - ``_emit_id_anchors`` line 462-463: for the rubric's one pending
          id, it appends ``f"\\n[#metadata(none) <{label_id}>]\\n"`` --
          note this ALSO carries its own leading ``"\\n"`` (folds into the
          run before the anchor) and its own TRAILING ``"\\n"`` immediately
          after the anchor's closing ``"]"``. That trailing newline is the
          anchor's fair share of the run this test measures.
        - ``_emit_id_anchors`` line 464-465: its tail re-arms
          ``list_item_needs_separator = True`` because we are still inside
          the list item.
        - ``visit_rubric`` line 5793-5794: appends an UNCONDITIONAL
          ``"\\n"`` ("Add newline before rubric") regardless of any flag --
          the first newline the rubric itself owes at this site.
        - ``visit_rubric`` line 5804-5806: ``_add_paragraph_separator()``
          is a no-op (not inside a paragraph); then, because
          ``list_item_needs_separator`` was JUST re-armed by
          ``_emit_id_anchors``'s own tail two steps above, the leading
          list-item separator check fires AGAIN and appends a SECOND
          ``"\\n"`` -- double-counting a flag ``_emit_id_anchors`` had
          already discharged with its own trailing newline.

        Today's run is therefore 1 (anchor's own trailing newline) + 1
        (rubric's unconditional newline) + 1 (rubric's separator-check
        double-count) = 3. The rubric owes ZERO further newlines at this
        site -- the anchor's own trailing newline already supplies the one
        separator needed -- so the correct run, once the double-count is
        removed, is 1.
        """
        result = _run_sphinx_build_typst(
            desc_rubric_decoupling_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        typ_output = temp_build_dir / "index.typ"
        actual_typ = typ_output.read_text(encoding="utf-8")

        anchor = "[#metadata(none) <index:decoupling-rubric-in-list-target>]"
        anchor_index = actual_typ.find(anchor)
        assert anchor_index != -1, (
            f"Expected propagated-target anchor {anchor!r} not found in "
            f"emitted .typ:\n{actual_typ}"
        )
        after_anchor = actual_typ[anchor_index + len(anchor) :]
        newline_run = re.match(r"\n*", after_anchor).group(0)
        measured_run = len(newline_run)

        expected_post_fix_run = 1
        assert measured_run == expected_post_fix_run, (
            f"D-11: measured a run of {measured_run} newline(s) between the "
            "propagated-target anchor and the rubric's strong({ wrapper "
            f"open (expected {expected_post_fix_run}, hand-derived above: "
            "_emit_id_anchors's own trailing newline is the anchor's fair "
            "share; visit_rubric's unconditional newline plus its "
            "re-armed separator check double-count on top of it). RED "
            "today (the untouched translator measures 3, from the "
            "double-count); expected GREEN once plan 39-06 lands the fix."
        )

    def test_control_non_propagated_target_rubrics_keep_current_byte_shape(
        self, desc_rubric_decoupling_render_gate_dir, temp_build_dir
    ):
        """
        CONTROL for the D-11 wart above. Passes today and must keep passing
        after plan 39-06's fix -- a fix that strips separators
        indiscriminately (rather than the specific
        ``_emit_id_anchors``/``visit_rubric`` double-count above) would
        break this assertion, since neither of these two rubrics carries a
        propagated target. Expected strings derived by reading
        ``golden.typ`` directly (D-07's byte-for-byte capture of this same
        commit), never by re-running the translator.
        """
        result = _run_sphinx_build_typst(
            desc_rubric_decoupling_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        typ_output = temp_build_dir / "index.typ"
        actual_typ = typ_output.read_text(encoding="utf-8")

        # The autodoc-style "Options" rubric -- from golden.typ.
        options_rubric_shape = (
            'par({text("The autodoc “Options” rubric shape.")})'
            '\n\n\nstrong({text("Options")})\nlinebreak()'
        )
        # The rubric at true end-of-document -- from golden.typ.
        trailing_rubric_shape = (
            'par({text("A rubric at true end-of-document.")})'
            '\n\n\nstrong({text("Trailing Heading")})\nlinebreak()'
        )
        assert options_rubric_shape in actual_typ, (
            "CONTROL regression: the autodoc-style Options rubric's byte "
            f"shape (no propagated target) changed:\n{actual_typ}"
        )
        assert trailing_rubric_shape in actual_typ, (
            "CONTROL regression: the trailing end-of-document rubric's "
            f"byte shape (no propagated target) changed:\n{actual_typ}"
        )

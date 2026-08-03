"""
SIG-09 real-render page-boundary acceptance gate (37-03-PLAN.md Task 2).

Proves that a signature and the first line of its description body are not
split across a page break: the signature's name, its parameter list, and
the first line of its description body must all land on the SAME compiled
page.

Measurement method (contract section 4.2 / RESEARCH.md): every page's text
is read via plain ``pypdf.extract_text()`` per PAGE (never the all-pages-
joined pattern ``tests/test_pdf_render_gate.py`` uses elsewhere, which
cannot express per-page containment) and never the per-glyph position-
callback extraction mode (measured unusable on Typst-generated PDFs in this
sandbox). Every extracted page's text strips U+200B first (contract
section 4.2's spurious-emission hazard), defensively -- this fixture's own
content injects no U+200B, but the helper stays consistent with every
other gate in this phase.

Page-height override mechanism (Task 2's required probe, done this
session): no existing fixture in this project overrides page geometry.
Three candidates were evaluated:

  (a) a ``typst_elements``/template-parameter override reaching
      ``project()`` via ``conf.py`` -- REJECTED: ``template_engine.py``'s
      ``ELEMENTS_ALLOWLIST`` only declares ``papersize``/``fontsize``/
      ``lang``; there is no page-height key, and adding one is
      configuration surface this phase does not own.
  (b) a fixture-local custom ``typst_template`` -- REJECTED: heavier than
      necessary (a whole parallel template) for a single geometry override
      this test only needs once.
  (c) compiling the emitted ``index.typ`` in the test with a small
      page-geometry preamble prepended -- CHOSEN. Verified by a real
      ``typst.compile()`` probe this session (see
      ``_insert_page_override``'s docstring for the exact mechanism and
      the clobbering hazard it avoids): the emitted ``.typ`` is otherwise
      UNMODIFIED apart from the inserted preamble, so the artifact under
      test stays the translator's own output.
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# The zero-width space character -- stripped from every compiled-PDF text
# read (contract section 4.2's spurious-emission hazard), defensively.
ZWSP = "\u200b"  # U+200B, written as an explicit escape (not an invisible literal)

# Sentinel tokens embedded in
# tests/fixtures/signature_page_boundary_render_gate/index.rst -- the
# signature's own name, its first parameter's name, and the first word of
# its description body's first line. Each is distinctive, at least 12
# characters, and does not occur elsewhere in the fixture (37-03-PLAN.md
# Task 2 acceptance criteria).
NAME_SENTINEL = "sigboundarynamesentinel"
PARAM_SENTINEL = "sigboundaryparamsentinel"
BODY_SENTINEL = "SIGBOUNDARYBODYFIRSTLINESENTINEL"

# The short-page geometry under which the untouched translator's
# signature/body split reproduces (found this session by sweeping page
# heights against the real compiled fixture -- 100-200pt all reproduce the
# split; 200pt/20pt was chosen as a round, comfortably-reproducible value).
PAGE_HEIGHT_PT = 200.0
PAGE_MARGIN_PT = 20.0

# Originally measured (37-03-PLAN.md Task 2) against the UNTOUCHED
# pre-Phase-37 translator (no block() wrapper, no sticky:true at all --
# the SIG-09 split defect this whole gate exists to catch was present)
# at PAGE_HEIGHT_PT/PAGE_MARGIN_PT: the fixture compiled to exactly 6
# pages. That baseline is not reachable once SIG-09 is genuinely fixed
# on this artificially short, page-boundary-tuned fixture -- see the
# post-Wave-3 note below -- so it is retired.
#
# Post-Wave-3 amendment (plan 37-09, real re-measurement, not a golden
# regenerated from output): once the desc_signature wrapper stops
# zeroing above/below and uses Typst's own block() default spacing
# (13.2pt at 11pt, measured byte-identical to ordinary
# paragraph-to-paragraph flow -- see 37-EMISSION-CONTRACT.md section 3),
# the boundary signature + its sticky:true-bound body no longer fits in
# the remaining room on page 6 of this deliberately tight
# (PAGE_HEIGHT_PT=200pt) fixture. `sticky: true`'s keep-together then
# correctly pushes the WHOLE unit onto page 7 as one piece (verified:
# `test_primary_signature_and_body_share_a_page` below still passes --
# name, params, and the body's first line all land together, on page 7
# instead of page 6) rather than letting it split or overlap. This is
# the keep-together mechanism doing exactly its job, not a spacing
# regression that leaks across the whole document -- swept in this
# worktree via a real compile at above/below values from 0em to 1.2em:
# the fixture stays at 6 pages up to 0.85em and only crosses to 7 pages
# at 0.9em and above, i.e. the extra page is specific to how much room
# THIS ONE keep-together unit needs, not a per-signature inflation that
# would compound across a real document. Re-pinned to 7, the real
# measured page count under the corrected wrapper.
#
# RENAMED at Phase 38 close (38-08-PLAN.md Task 1, closing the folded todo
# `2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md`):
# the identifier `EXPECTED_PAGE_COUNT_PRE_PHASE` had already held a
# *post*-Phase-37 value since plan 37-09 re-pinned it above, and Phase 38
# (structural indentation + info fields) measurably moves page counts in
# BOTH directions elsewhere in this fixture's blast radius -- shortening a
# document via the body-less single-value field-body reflow, widening
# field-list lines via the proportional-to-monospace parameter move -- so
# the "PRE_PHASE" name would have started lying a second time regardless of
# whether this specific fixture's own count happened to move. Renamed to
# `EXPECTED_PAGE_COUNT_CEILING` to describe what the constant actually IS
# -- the ceiling the `<=` guard below checks against -- rather than tying
# the name to any one phase's before/after boundary, so a future phase's
# own re-measure cannot make the name lie a third time.
#
# Re-measured 2026-08-01 against the post-Phase-38 translator (this
# worktree's base commit, 7ae016d, already contains 38-05/38-06/38-07's
# landed changes -- confirmed directly: `git log --oneline` shows those
# plans' commits as ancestors, and `typsphinx/translator.py` already
# contains `pad(left: {SHARED_INDENT_STEP}, {{` at both the desc_content
# and field_list wrapper sites before this measurement was taken). Real
# `sphinx-build -b typst` + the SAME `_insert_page_override` mechanism this
# module already uses + `typst.compile()` + `pypdf.PdfReader`:
#
#     $ uv run python <rebuild+compile+len(reader.pages) script, see
#       38-GATE-EVIDENCE.md Bucket D for the exact command run>
#     PAGE COUNT (boundary fixture): 7
#
# UNCHANGED at 7. Dominant reason: this fixture exists solely to isolate
# SIG-09's page-boundary keep-together behaviour on ONE artificially short
# page (PAGE_HEIGHT_PT=200pt) and contains no field list and no body-less
# single-value field -- neither of Phase 38's two page-count-moving
# mechanisms (the field-body shortening, the field-list widening) has any
# bytes to act on in this fixture, so the value that survived Phase 37
# survives Phase 38 by absence of applicable content, not by coincidence.
# This is a MEASUREMENT taken against the real post-phase build, never a
# hand-derived or regenerated expected string (milestone invariant #4).
EXPECTED_PAGE_COUNT_CEILING = 7


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run `sphinx-build -b typst` as a subprocess and return the completed
    process. Invoked as `sys.executable -m sphinx` -- see
    tests/test_pdf_render_gate.py's `_run_sphinx_build_typst` for the full
    NixOS-sandbox PATH-shadowing rationale this mirrors.
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


def _insert_page_override(base_source: str, height_pt: float, margin_pt: float) -> str:
    """
    Insert `#set page(height: ..., margin: ...)` as the FIRST statement of
    the `body` argument passed into `project()` -- i.e. immediately after
    the real `#show: project.with(...)` call's closing paren and the blank
    line that follows it in `template_engine.py`'s `render()` output.

    Verified by a real `typst.compile()` probe this session (Task 2's
    required probe): a `#set page(...)` placed at the very TOP of the file
    -- BEFORE `project()`'s own `set page(paper: papersize, ...)` call --
    is silently CLOBBERED, because Typst's `paper:` keyword sets width AND
    height together, discarding any earlier explicit height. Placed here
    instead -- chronologically AFTER `project()`'s own `set page()` call
    executes, inside the same function body -- only the fields this
    override explicitly names (`height`, `margin`) are overridden; the
    paper's width is untouched. `typsphinx/templates/base.typ`'s
    `project()` renders the title page and the table-of-contents page
    (each followed by its own `pagebreak()`) BEFORE `body`, so both of
    those keep the real A4 geometry; only the fixture's own translated
    content -- starting from `body` -- uses the short page height under
    test.

    This is mechanism (c) from the module docstring: the emitted `.typ` is
    otherwise UNMODIFIED apart from this inserted preamble, so the
    artifact under test stays the translator's own output. Locates the
    LATER of the document's two `#show: ` statements (the earlier one,
    `#show: codly-init.with()`, is unrelated) by searching from the
    `#import "_template.typ"` line onward.
    """
    template_import_idx = base_source.index('#import "_template.typ"')
    show_idx = base_source.index("#show: ", template_import_idx)
    insertion_idx = base_source.index(")\n\n", show_idx) + len(")\n\n")
    override = f"#set page(height: {height_pt}pt, margin: {margin_pt}pt)\n\n"
    return base_source[:insertion_idx] + override + base_source[insertion_idx:]


def _compile_and_extract_pages(index_typ_path: Path, build_dir: Path) -> list:
    """
    Insert the short-page-geometry override, compile the probe through the
    real `typst.compile()`, and return a list of per-page extracted text
    (index 0 = first page) -- a real per-page loop over `reader.pages`,
    never the all-pages-joined pattern, so per-page containment can be
    asserted.
    """
    base_source = index_typ_path.read_text(encoding="utf-8")
    probe_source = _insert_page_override(base_source, PAGE_HEIGHT_PT, PAGE_MARGIN_PT)
    probe_path = build_dir / "sig09_probe.typ"
    probe_path.write_text(probe_source, encoding="utf-8")
    pdf_path = build_dir / "sig09_probe.pdf"
    typst.compile(str(probe_path), output=str(pdf_path))

    reader = pypdf.PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text().replace(ZWSP, "")
        pages.append(text)
    return pages


def _find_page_index(pages: list, token: str):
    """Return the index of the FIRST page whose text contains `token`, or
    `None` if it appears on no page."""
    for i, text in enumerate(pages):
        if token in text:
            return i
    return None


@pytest.fixture(scope="class")
def signature_page_boundary_pages(tmp_path_factory):
    """
    Build the signature_page_boundary_render_gate fixture through
    `-b typst`, compile it (with the short-page override) through the real
    `typst.compile()`, and return the per-page extracted text -- ONCE per
    class, so every test method below reads a disjoint slice of the same
    real compile.

    Depends only on `tmp_path_factory` -- not a function-scoped
    fixtures-dir fixture -- to avoid a pytest ScopeMismatch (mirrors
    tests/test_pdf_render_gate.py's `topic_line_block_render_gate_pdf_text`
    precedent).
    """
    source_dir = (
        Path(__file__).parent / "fixtures" / "signature_page_boundary_render_gate"
    )
    build_dir = tmp_path_factory.mktemp("sig09_gate") / "_build"
    result = _run_sphinx_build_typst(source_dir, build_dir)
    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return _compile_and_extract_pages(index_typ, build_dir)


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the SIG-09 render gate",
)
class TestSignaturePageBoundaryRenderGate:
    """
    Real-compile per-page acceptance gate for SIG-09.

    Requirements: SIG-09 (37-CONTEXT.md D-09/D-10, 37-RESEARCH.md
    "D-09 / SIG-09: page-boundary keep-together, empirically proven",
    37-03-PLAN.md Task 2).
    """

    def test_two_page_precondition_guard(self, signature_page_boundary_pages):
        """
        At least two pages must exist. Without this guard, a fixture that
        accidentally fits entirely on one page would pass the primary
        assertion below VACUOUSLY (every sentinel trivially "shares a
        page" when there is only one page) -- exactly the failure mode
        milestone invariant #4 exists to prevent. This guard passes
        pre-phase and must keep passing.
        """
        assert len(signature_page_boundary_pages) >= 2, (
            f"expected at least 2 pages under the short-page geometry "
            f"({PAGE_HEIGHT_PT}pt height); got "
            f"{len(signature_page_boundary_pages)} -- the primary "
            "containment assertion would be vacuous."
        )

    def test_page_count_does_not_inflate(self, signature_page_boundary_pages):
        """
        Pitfall 1 guard: the compiled page count must not GROW beyond the
        pinned ceiling. Post-Wave-3 amendment (plan 37-09): the ceiling
        itself was re-pinned from 6 to 7 -- see EXPECTED_PAGE_COUNT_CEILING's
        own comment for the full reasoning and the above/below sweep data
        (that comment also records Phase 38's own re-measure, unchanged at
        7, and the rename from EXPECTED_PAGE_COUNT_PRE_PHASE this phase
        made to close the folded todo). In short: this fixture is
        deliberately built with almost no page slack so the SIG-09
        signature/body split defect reproduces; once the corrected wrapper
        restores real paragraph spacing around the boundary signature, that
        signature + its sticky:true-bound body no longer fits in the room
        left on page 6, and `sticky: true` correctly pushes the whole unit
        to page 7 as one piece rather than splitting or overlapping it --
        confirmed by `test_primary_signature_and_body_share_a_page` below,
        which still passes (the unit lands together, just one page later).
        This guard still catches the failure mode it exists for: a
        per-signature spacing regression that inflates the page count
        BEYOND the corrected wrapper's own real, re-measured ceiling.
        """
        actual = len(signature_page_boundary_pages)
        assert actual <= EXPECTED_PAGE_COUNT_CEILING, (
            f"page count grew from the pinned ceiling of "
            f"{EXPECTED_PAGE_COUNT_CEILING} to {actual} -- likely a "
            "signature-wrapper spacing regression."
        )

    def test_primary_signature_and_body_share_a_page(
        self, signature_page_boundary_pages
    ):
        """
        SIG-09 primary: the signature's name, its parameter list, and the
        first line of its description body must all land on the SAME
        compiled page.

        Pre-phase (this session, against the untouched translator, at
        PAGE_HEIGHT_PT/PAGE_MARGIN_PT): the name and the parameter both
        land on page index 4, but the body's first-line sentinel is pushed
        to page index 5 -- SIG-09's exact defect, reproduced with a real
        page-break fixture. This assertion FAILS (RED) against the
        untouched translator; 37-06 (Wave 3) makes it pass by wrapping the
        signature in `block(sticky: true, ...)` (D-09/D-10).
        """
        pages = signature_page_boundary_pages
        name_idx = _find_page_index(pages, NAME_SENTINEL)
        param_idx = _find_page_index(pages, PARAM_SENTINEL)
        body_idx = _find_page_index(pages, BODY_SENTINEL)

        assert name_idx is not None, f"{NAME_SENTINEL!r} not found on any page"
        assert param_idx is not None, f"{PARAM_SENTINEL!r} not found on any page"
        assert body_idx is not None, f"{BODY_SENTINEL!r} not found on any page"

        assert name_idx == param_idx == body_idx, (
            f"signature name (page index {name_idx}), its parameter list "
            f"(page index {param_idx}), and the first line of its "
            f"description body (page index {body_idx}) are NOT all on the "
            "same page -- SIG-09 page-boundary defect."
        )

"""
Phase 48 plan 06, Task 3: real ``sphinx-build`` -> ``typst.compile()`` ->
``pypdf`` render gate for the whole-document cross-reference guard fix
(G-48-4 / XREF-03 gap closure), recorded RED against the unfixed emitter.

``tests/fixtures/xref_whole_document_guard_gate/`` (built in Task 1)
exercises the whole-document reference form (``:doc:``) in both outcomes at
once, inside a single compiled master: a whole-document reference to
``included`` (toctree-reachable, so ``manual.typ`` DOES ``#include()``
``included.typ``) and one to ``orphan`` (marked ``:orphan:``, in no
toctree, so ``manual.typ`` never ``#include()``s ``orphan.typ``).

Every asserted value in this module is taken from
``48-EXPECTED-STRUCTURE.md``'s "Phase 48 Plan 05 -- Whole-Document
Reference Path" section §§3-5 -- never read off a fresh build (binding
constraint #6). Every flipping test here was recorded RED (as a strict
``xfail``) against the unfixed translator; plan 48-07 lands the emitter fix
and flips each one to a plain, non-xfail assertion.
"""

import io
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

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"
WHOLE_DOCUMENT_FIXTURE_DIR = FIXTURES_DIR / "xref_whole_document_guard_gate"

# TypstPDFBuilder.out_suffix (typsphinx/builder.py:1245) -- the fixture is
# built via `-b typstpdf`, so every emitted cross-document refuri (guarded
# or, pre-fix, plain string-url) ends in THIS suffix, not `.typ`.
OUT_SUFFIX = ".pdf"

INCLUDED_BODY_MARKER = "INCLUDED_BODY_MARKER_TEXT"
ORPHAN_BODY_MARKER = "ORPHAN_BODY_MARKER_TEXT"

# 48-EXPECTED-STRUCTURE.md §3's fully-substituted reference-site form for
# docname `included`/`orphan`, tolerant of the body's exact content bytes
# (`.*?`) since only the GUARD SHAPE -- not the body -- is under test here
# (mirrors tests/test_xref_compile_time_guard_render_gate.py's own
# `_PER_MASTER_GUARD_PATTERN`/`_COLLISION_GUARD_PATTERN` convention).
# re.DOTALL: the emitted body streams across a real newline between the
# guard's open string and its first child, the same translator emission
# characteristic that sibling module's pattern already accounts for.
_INCLUDED_GUARD_PATTERN = re.compile(
    r"context \{ let __tsx_body = \[#\{.*?\}\]; "
    r"if query\(<included:__tsx-doc__>\)\.len\(\) > 0 \{ "
    r"link\(<included:__tsx-doc__>, __tsx_body\) \} else \{ __tsx_body \} \}",
    re.DOTALL,
)
_ORPHAN_GUARD_PATTERN = re.compile(
    r"context \{ let __tsx_body = \[#\{.*?\}\]; "
    r"if query\(<orphan:__tsx-doc__>\)\.len\(\) > 0 \{ "
    r"link\(<orphan:__tsx-doc__>, __tsx_body\) \} else \{ __tsx_body \} \}",
    re.DOTALL,
)


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, per this
    repo's established NixOS-sandbox-safe convention -- every gate module in
    this suite carries its OWN copy of this helper rather than importing a
    sibling module's.
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


def _strip_raw_literals(typ_text: str) -> str:
    """Drop ``raw("...")`` inline-literal segments before scanning for
    labels -- prose that quotes a label/reference form as an rST inline
    literal renders as a ``raw("...")`` string literal, not a real Typst
    label expression, and would masquerade as one in a naive scan."""
    return re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)


def _classify_link_annotations(pdf_bytes: bytes):
    """
    Classify every ``/Link`` annotation across every page of the compiled
    PDF into three buckets and return all three:

    - ``named_dests``: every ``/Dest`` that is a plain STRING (a named PDF
      destination) -- the label string itself.
    - ``positional_dest_pages``: for every ``/Dest`` that is a non-string
      array (``[page_ref, /XYZ, x, y, z]``), the resolved page OBJECT the
      first array element points at.
    - ``uri_actions``: every ``/A`` action whose ``/S`` is ``/URI`` -- the
      URI string.

    **Why the positional bucket exists** (measured this phase,
    ``tests/test_xref_compile_time_guard_render_gate.py``'s
    ``_link_annotation_dests`` docstring already records the same finding
    for the anchored-xref gate): Typst registers a NAMED PDF destination
    only for a label that participates in the document's ``#outline()``
    (i.e. a heading anchor). A link to a label that is NOT a heading anchor
    -- exactly the self-anchor form this gap fix introduces
    (``#metadata(none) <label>``, §2) -- still compiles and still produces a
    real, working ``/Link`` annotation, but its ``/Dest`` is an unnamed
    POSITIONAL array (page reference + ``/XYZ`` + coordinates) with no
    string to recover. Verified directly against a real compiled PDF this
    session (``tests/fixtures/xref_orphan_degrade_render_gate/``'s own
    metadata-only ``included-target`` anchor): its ``/Dest`` is an
    ``IndirectObject`` resolving to ``[IndirectObject(...), '/XYZ', x, y,
    z]``, never a string -- the same shape this helper resolves below via
    ``PdfReader.get_page_number()`` on the array's first element.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    named_dests: list[str] = []
    positional_dest_pages: list = []
    uri_actions: list[str] = []
    for page in reader.pages:
        annots = page.get("/Annots") or []
        for annot in annots:
            obj = annot.get_object()
            if obj.get("/Subtype") != "/Link":
                continue
            dest = obj.get("/Dest")
            if isinstance(dest, str):
                named_dests.append(dest)
                continue
            if dest is not None:
                dest_array = dest.get_object()
                page_ref = dest_array[0]
                positional_dest_pages.append(page_ref.get_object())
                continue
            action = obj.get("/A")
            if action is not None:
                action_obj = action.get_object()
                if action_obj.get("/S") == "/URI":
                    uri_actions.append(str(action_obj.get("/URI")))
    return named_dests, positional_dest_pages, uri_actions


@pytest.fixture(scope="class")
def whole_document_guard_build(tmp_path_factory):
    """
    Build ``xref_whole_document_guard_gate`` ONCE per class via
    ``-b typstpdf`` and return the emitted content files' text plus the
    compiled master PDF's bytes. Deliberately does NOT assert
    ``result.returncode == 0`` at fixture level (mirrors
    ``tests/test_xref_compile_time_guard_render_gate.py``'s
    ``per_master_guard_build`` convention) -- this fixture's own build DOES
    exit 0 both before and after this phase's fix (G-48-4 is a
    "compiles fine, produces wrong output" defect, not a compile fatal), but
    keeping the fixture tolerant lets each test record its own outcome
    rather than a fixture-level assertion erroring every test in the class.
    """
    build_dir = tmp_path_factory.mktemp("xref_whole_document_guard")
    result = _run_sphinx_build_typstpdf(WHOLE_DOCUMENT_FIXTURE_DIR, build_dir)

    def _read_text(name: str) -> str:
        path = build_dir / name
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _read_bytes(name: str) -> bytes:
        path = build_dir / name
        return path.read_bytes() if path.exists() else b""

    return {
        "result": result,
        "index_typ": _read_text("index.typ"),
        "included_typ": _read_text("included.typ"),
        "orphan_typ": _read_text("orphan.typ"),
        "manual_pdf": _read_bytes("manual.pdf"),
    }


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the whole-document xref guard gate",
)
class TestXrefWholeDocumentGuardRenderGate:
    """
    XREF-03 / G-48-4: the whole-document reference path (``:doc:``), which
    pre-fix always renders as a plain string-url ``link("<target>.pdf",
    ...)`` -- a dead link the build itself never detects (exit 0, a valid
    compiled PDF).

    **Honesty note on the destination-page assertion**
    (``test_pdf_positional_destination_resolves_to_included_page`` below):
    this fixture's compiled master PDF measures 3 pages (title page, table
    of contents, and ONE content page carrying every body element -- the
    master's own heading, both reference paragraphs, and the included
    document's heading/marker all collapse onto that single content page).
    The destination-page assertion is therefore TRUE but WEAK in the sense
    ``48-EXPECTED-STRUCTURE.md`` §5 flags: it correctly rules out the
    destination landing on the title page or the table-of-contents page,
    but there is only ONE content page for the assertion to distinguish
    against, so it would not catch a destination that pointed at the wrong
    ANCHOR on that same page. The measured page count (3) and this
    assertion's strength are recorded verbatim in
    ``48-RED-EVIDENCE.md``'s "Phase 48 Plan 06 -- Whole-Document Render
    Gate RED" section.
    """

    def test_build_exits_0_no_dangling_label(self, whole_document_guard_build):
        """
        Invariance -- TRUE pre-fix (G-48-4 does not break the compile; the
        dead links are plain string-url ``link()`` calls, not label
        references, so Typst never raises a dangling-label error for them)
        and remains TRUE post-fix (the guard's ``query(<label>)`` degrades
        gracefully when a label is absent -- it never raises). NOT an
        xfail, per this plan's own explicit instruction: this defect does
        not break the compile.
        """
        result = whole_document_guard_build["result"]
        combined = result.stdout + result.stderr
        assert result.returncode == 0, (
            f"Expected -b typstpdf to exit 0:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert (
            "does not exist in the document" not in combined
        ), f"Typst reported a dangling label:\n{combined}"

    def test_reference_visible_text_present_in_pdf(self, whole_document_guard_build):
        """
        D-02 invariance: a degraded reference renders exactly the same
        visible text as the linked form -- both references' link text (the
        target document's title, per Sphinx's ``:doc:`` auto-text rule) is
        present in the extracted PDF text, whether the reference happens to
        be clickable in this compile or not. TRUE both pre- and post-fix.
        """
        reader = pypdf.PdfReader(io.BytesIO(whole_document_guard_build["manual_pdf"]))
        full_text = "".join(page.extract_text() for page in reader.pages)

        assert "Included Whole-Document Target" in full_text, (
            "manual.pdf is missing the included reference's visible text:\n"
            f"{full_text}"
        )
        assert "Orphan Whole-Document Target" in full_text, (
            "manual.pdf is missing the orphan reference's visible text "
            f"(D-02 invariance):\n{full_text}"
        )

    def test_orphan_body_marker_never_appears_in_master_pdf(
        self, whole_document_guard_build
    ):
        """
        Invariance: the orphan document's body marker does NOT appear
        anywhere in the compiled master's text -- ``orphan.typ`` is never
        ``#include()``d into ``manual.typ``, which is what makes the
        degrade half of this fixture real. TRUE both pre- and post-fix
        (this gap's fix changes how the REFERENCE to ``orphan`` renders, not
        whether ``orphan``'s own content is included).
        """
        reader = pypdf.PdfReader(io.BytesIO(whole_document_guard_build["manual_pdf"]))
        full_text = "".join(page.extract_text() for page in reader.pages)

        assert ORPHAN_BODY_MARKER not in full_text, (
            f"orphan.typ's body marker unexpectedly appears in the compiled "
            f"master's text -- orphan.typ should never be #include()d:\n"
            f"{full_text}"
        )

    def test_index_typ_carries_both_guard_expressions(self, whole_document_guard_build):
        """
        48-EXPECTED-STRUCTURE.md §3: the emitted ``index.typ`` carries the
        fully-substituted D-07 guard expression for BOTH the included
        document's self-anchor label and the orphan document's -- today,
        neither whole-document reference is guarded at all (both are plain
        string-url ``link()`` calls).
        """
        index_typ = _strip_raw_literals(whole_document_guard_build["index_typ"])

        included_match = _INCLUDED_GUARD_PATTERN.search(index_typ)
        orphan_match = _ORPHAN_GUARD_PATTERN.search(index_typ)

        assert included_match is not None, (
            "index.typ does not carry the guarded expression for "
            f"included:__tsx-doc__:\n{index_typ}"
        )
        assert orphan_match is not None, (
            "index.typ does not carry the guarded expression for "
            f"orphan:__tsx-doc__:\n{index_typ}"
        )

    def test_index_typ_carries_no_string_url_link_to_targets(
        self, whole_document_guard_build
    ):
        """
        48-EXPECTED-STRUCTURE.md §4: the emitted ``index.typ`` carries NO
        string-url form naming either target's output file -- i.e. no
        ``link("included.pdf", ...)`` / ``link("orphan.pdf", ...)`` anywhere
        -- the whole point of routing the whole-document case through the
        guard instead of the external-link ``else`` branch. Today: BOTH
        string-url forms are present (this is the defect itself).
        """
        index_typ = _strip_raw_literals(whole_document_guard_build["index_typ"])

        assert 'link("included' + OUT_SUFFIX not in index_typ, (
            f"index.typ still carries a string-url link to included{OUT_SUFFIX}:\n"
            f"{index_typ}"
        )
        assert 'link("orphan' + OUT_SUFFIX not in index_typ, (
            f"index.typ still carries a string-url link to orphan{OUT_SUFFIX}:\n"
            f"{index_typ}"
        )

    def test_included_and_orphan_typ_each_carry_self_anchor_once(
        self, whole_document_guard_build
    ):
        """
        48-EXPECTED-STRUCTURE.md §4: ``included.typ`` and ``orphan.typ``
        each carry their OWN self-anchor exactly once -- today, neither
        emits any self-anchor at all.
        """
        included_typ = whole_document_guard_build["included_typ"]
        orphan_typ = whole_document_guard_build["orphan_typ"]

        assert included_typ.count("<included:__tsx-doc__>") == 1, (
            f"expected included.typ's self-anchor exactly once, found "
            f"{included_typ.count('<included:__tsx-doc__>')}:\n{included_typ}"
        )
        assert orphan_typ.count("<orphan:__tsx-doc__>") == 1, (
            f"expected orphan.typ's self-anchor exactly once, found "
            f"{orphan_typ.count('<orphan:__tsx-doc__>')}:\n{orphan_typ}"
        )

    def test_master_pdf_zero_uri_actions_ending_in_out_suffix(
        self, whole_document_guard_build
    ):
        """
        48-EXPECTED-STRUCTURE.md §5: the compiled master PDF carries ZERO
        URI actions whose target ends in the builder's ``out_suffix`` --
        both whole-document references route through the guard now, never
        the string-url branch. Today: TWO (``included.pdf``,
        ``orphan.pdf``).
        """
        _, _, uri_actions = _classify_link_annotations(
            whole_document_guard_build["manual_pdf"]
        )
        suffix_uri_actions = [u for u in uri_actions if u.endswith(OUT_SUFFIX)]

        assert suffix_uri_actions == [], (
            f"expected zero URI actions ending in '{OUT_SUFFIX}', found "
            f"{sorted(suffix_uri_actions)}"
        )

    def test_pdf_positional_destination_resolves_to_included_page(
        self, whole_document_guard_build
    ):
        """
        48-EXPECTED-STRUCTURE.md §5: the compiled master PDF carries
        EXACTLY ONE link annotation with a POSITIONAL (non-string)
        destination -- the whole-document reference to ``included``, whose
        target is a ``metadata`` anchor (§2's zero-width form), not a
        heading anchor, so Typst never registers a NAMED destination for it
        (see ``_classify_link_annotations``'s docstring). That destination
        resolves to a page carrying ``included``'s body marker. See this
        class's own docstring for the honesty caveat on this assertion's
        strength (measured 3-page fixture, single content page). Today:
        zero positional destinations exist for this reference at all (it is
        a plain string-url link, no ``/Dest`` whatsoever).
        """
        _, positional_dest_pages, _ = _classify_link_annotations(
            whole_document_guard_build["manual_pdf"]
        )

        assert len(positional_dest_pages) == 1, (
            f"expected exactly one positional-destination link annotation, "
            f"found {len(positional_dest_pages)}"
        )

        reader = pypdf.PdfReader(io.BytesIO(whole_document_guard_build["manual_pdf"]))
        page_num = reader.get_page_number(positional_dest_pages[0])
        assert (
            page_num is not None
        ), "could not resolve the positional destination back to a page"
        page_text = reader.pages[page_num].extract_text()

        assert INCLUDED_BODY_MARKER in page_text, (
            f"expected the positional destination's page (index {page_num}) "
            f"to carry {INCLUDED_BODY_MARKER!r}, got:\n{page_text}"
        )

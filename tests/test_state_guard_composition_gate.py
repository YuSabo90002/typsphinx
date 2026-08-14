"""
Phase 49 plan 02 -- COMP-07/COMP-08/COMP-09/COMP-10 composition acceptance
gate, driving the two fixtures Task 1 of this plan built
(``tests/fixtures/state_guard_two_master_gate/``,
``tests/fixtures/state_guard_mirror_pair_gate/``) against the post-fix
state-guarded include mechanism 49-04 lands.

Every asserted value below is a substitution into
``49-EXPECTED-STRUCTURE.md``'s ``## Emission contract`` (the state key
``typsphinx:include-edges``, the ``<parent>#<occurrence>><child>`` edge-key
format, the array-literal rendering rule, the guard-line shape) applied to
this plan's own ``## Fixture specification`` entries 1 and 2, hand-derived
by walking each fixture's own ``conf.py``/``.rst`` content against the
traversal rule -- never read off a build (binding constraint #6).

Resolved heading levels are queried from the COMPILED document via
``typst.query(..., field="level", root=<build_dir>)`` rather than grepped
out of the emitted ``.typ`` markup, because a ``.typ`` grep cannot observe
an offset Typst resolves at layout time (the same reason
``tests/test_heading_depth_render_gate.py`` queries the compiled artifact
instead of the source).

Every post-fix assertion that cannot pass until 49-04 lands is recorded as
``pytest.mark.xfail(strict=True)`` with a reason paraphrasing the matching
``49-RED-EVIDENCE.md`` transcript and naming 49-04 as the plan that flips
it -- so this module exits 0 on this plan's own tree while an accidental
early pass surfaces loudly as XPASS. Three tests are NOT marked xfail
because ``49-RED-EVIDENCE.md`` recorded them as already-passing invariance
baselines on the unfixed tree: single-master builds are unaffected by this
phase's change (no shared-across-masters child exists to lose), an empty
toctree's include-file list already emits no ``context { ... }`` block
today (Task 1's own read of the emitted ``emptytoc.typ`` confirmed this),
and a master with no toctree at all already resolves its own heading at
the top level (Failure mode 4's ``soloist`` control).
"""

import hashlib
import re
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

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TWO_MASTER_DIR = FIXTURES_DIR / "state_guard_two_master_gate"
MIRROR_PAIR_DIR = FIXTURES_DIR / "state_guard_mirror_pair_gate"
SINGLE_MASTER_DIR = FIXTURES_DIR / "xref_orphan_degrade_render_gate"

# D-07 -- the namespaced Typst `state` key, measured and adopted in
# 49-EVIDENCE.md's State-syntax measurement.
STATE_KEY = "typsphinx:include-edges"

# The wrapper's state-publication line shape (## Emission contract): capture
# group 1 is the array-literal body between `.update((` and `))`, empty for
# a zero-key project.
STATE_PUBLICATION_PATTERN = re.compile(
    re.escape(f'#state("{STATE_KEY}", ())') + r"\.update\(\((.*?)\)\)"
)

# Hand-derived per-master edge sets (## Fixture specification entry 1, plus
# this plan's own nested-docname/empty-toctree additions, walked against
# the ## Emission contract's traversal rule -- see 49-02-PLAN.md and this
# module's own docstring; never read off a build).
TWO_MASTER_EDGE_KEYS = {
    "manual.typ": (
        "index#0>zmid",
        "zmid#0>shared",
        "shared#0>sub/nested",
        "sub/nested#0>emptytoc",
    ),
    "bmanual.typ": (
        "bmaster#0>shared",
        "shared#0>sub/nested",
        "sub/nested#0>emptytoc",
    ),
}

# Hand-derived per-master edge sets (## Fixture specification entry 2, plus
# this plan's own no-nesting-control addition).
MIRROR_PAIR_EDGE_KEYS = {
    "mastera.typ": ("xmastera#0>zmid", "zmid#0>shared"),
    "masterb.typ": ("xmasterb#0>shared", "xmasterb#0>zmid"),
    "solomaster.typ": (),
}


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path, extra_args: tuple = ()
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard and guaranteeing the worktree's own editable
    ``typsphinx`` copy is what compiles the fixtures.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typst",
            *extra_args,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


def _extract_pdf_text(pdf_path: Path) -> str:
    """Compile+readback helper: join every page's ``pypdf`` extracted text
    with newlines, matching the idiom ``tests/test_pdf_render_gate.py``
    uses throughout."""
    reader = pypdf.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() for page in reader.pages)


def _query_heading_levels(typ_path: Path, root: Path) -> list:
    """Return the ordered list of *resolved* heading levels for the
    compiled document at ``typ_path``. ``root`` MUST be the build
    directory, never the ``.typ`` file's own directory -- the emitted
    ``include()`` paths are relative to the build root and Typst resolves
    them against ``root`` during ``query``/``compile`` (the same rule
    ``tests/test_heading_depth_render_gate.py`` documents)."""
    import json

    result = typst.query(str(typ_path), "heading", field="level", root=str(root))
    return json.loads(result)


def _extract_body_text(body: dict) -> str:
    """Defensively derive plain text from a Typst heading element's
    ``body`` content dict -- mirrors
    ``tests/test_heading_depth_render_gate.py``'s helper of the same
    name."""
    if not isinstance(body, dict):
        return repr(body)
    if body.get("func") == "text" and "text" in body:
        return body["text"]
    if body.get("func") == "sequence" and not body.get("children"):
        return ""
    return repr(body)


def _query_heading_outline(typ_path: Path, root: Path) -> list:
    """Return the ordered ``(level, title)`` pairs for the compiled
    document at ``typ_path``. Same ``root=`` requirement as
    ``_query_heading_levels``."""
    import json

    result = typst.query(str(typ_path), "heading", root=str(root))
    elements = json.loads(result)
    return [(el["level"], _extract_body_text(el.get("body"))) for el in elements]


def _level_for_title(outline: list, title: str) -> int:
    """Locate the resolved level of the heading whose body text equals
    ``title``, or fail with a message naming the whole outline."""
    for level, body_title in outline:
        if body_title == title:
            return level
    raise AssertionError(f"No heading titled {title!r} found in outline: {outline}")


def _toctree_entries(rst_text: str) -> list:
    """Extract the ordered list of bare toctree entry names from a
    document's own ``.rst`` source (source-level, never build-derived) --
    used to confirm two mirror-pair masters differ ONLY in entry order."""
    lines = rst_text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == ".. toctree::")
    entries = []
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(":"):
            continue
        entries.append(stripped)
    return entries


def _render_edge_keys_literal(keys: tuple) -> str:
    """Render a tuple of edge keys as the Emission contract's array-literal
    body (the text between ``.update((`` and ``))``): empty for zero keys,
    otherwise a comma-separated, double-quoted list with an UNCONDITIONAL
    trailing comma after the last element (D-09/Pitfall 1 -- the same rule
    for arity 1 as for arity 2+)."""
    if not keys:
        return ""
    return ", ".join(f'"{key}"' for key in keys) + ","


@pytest.fixture(scope="class")
def two_master_build(tmp_path_factory):
    """
    Build ``tests/fixtures/state_guard_two_master_gate`` ONCE per class and
    return a record with both wrappers' paths/text, both compiled PDFs'
    extracted text, the emitted content files' text, and the shared
    content file's SHA-256 digest.
    """
    source_dir = TWO_MASTER_DIR
    build_dir = tmp_path_factory.mktemp("state_guard_two_master") / "_build"

    result = _run_sphinx_build_typst(source_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    manual_typ = build_dir / "manual.typ"
    bmanual_typ = build_dir / "bmanual.typ"
    assert manual_typ.exists(), "manual.typ (master A wrapper) was not emitted"
    assert bmanual_typ.exists(), "bmanual.typ (master B wrapper) was not emitted"

    manual_pdf = build_dir / "manual.pdf"
    bmanual_pdf = build_dir / "bmanual.pdf"
    typst.compile(str(manual_typ), output=str(manual_pdf))
    typst.compile(str(bmanual_typ), output=str(bmanual_pdf))

    shared_typ = build_dir / "shared.typ"
    nested_typ = build_dir / "sub" / "nested.typ"
    emptytoc_typ = build_dir / "emptytoc.typ"

    return {
        "build_dir": build_dir,
        "manual_typ": manual_typ,
        "bmanual_typ": bmanual_typ,
        "manual_wrapper_text": manual_typ.read_text(encoding="utf-8"),
        "bmanual_wrapper_text": bmanual_typ.read_text(encoding="utf-8"),
        "manual_pdf_text": _extract_pdf_text(manual_pdf),
        "bmanual_pdf_text": _extract_pdf_text(bmanual_pdf),
        "index_content": (build_dir / "index.typ").read_text(encoding="utf-8"),
        "zmid_content": (build_dir / "zmid.typ").read_text(encoding="utf-8"),
        "shared_content": shared_typ.read_text(encoding="utf-8"),
        "bmaster_content": (build_dir / "bmaster.typ").read_text(encoding="utf-8"),
        "nested_content": nested_typ.read_text(encoding="utf-8"),
        "emptytoc_content": emptytoc_typ.read_text(encoding="utf-8"),
        "shared_digest": hashlib.sha256(shared_typ.read_bytes()).hexdigest(),
    }


@pytest.fixture(scope="class")
def mirror_pair_build(tmp_path_factory):
    """
    Build ``tests/fixtures/state_guard_mirror_pair_gate`` ONCE per class and
    return a record with all three wrappers' paths/text and the build
    directory (needed as the ``root=`` for every ``typst.query`` call).
    """
    source_dir = MIRROR_PAIR_DIR
    build_dir = tmp_path_factory.mktemp("state_guard_mirror_pair") / "_build"

    result = _run_sphinx_build_typst(source_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    mastera_typ = build_dir / "mastera.typ"
    masterb_typ = build_dir / "masterb.typ"
    solomaster_typ = build_dir / "solomaster.typ"
    for wrapper in (mastera_typ, masterb_typ, solomaster_typ):
        assert wrapper.exists(), f"{wrapper.name} was not emitted"

    return {
        "build_dir": build_dir,
        "mastera_typ": mastera_typ,
        "masterb_typ": masterb_typ,
        "solomaster_typ": solomaster_typ,
        "mastera_wrapper_text": mastera_typ.read_text(encoding="utf-8"),
        "masterb_wrapper_text": masterb_typ.read_text(encoding="utf-8"),
        "solomaster_wrapper_text": solomaster_typ.read_text(encoding="utf-8"),
    }


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the composition gate",
)
@pytest.mark.slow
class TestStateGuardTwoMasterComposition:
    """
    COMP-07/COMP-08/COMP-09 real-compile gate over
    ``state_guard_two_master_gate`` -- defect A (a document toctree'd by
    two masters), the diamond (one shared content file, two masters), and
    document-order interleaving.
    """

    @pytest.mark.xfail(strict=True, reason="flips in 49-04 (RED mode 1)")
    def test_shared_chapter_appears_in_both_masters_pdf(self, two_master_build):
        """COMP-07 / SC#1: the shared marker's occurrence count is exactly
        1 in EACH of the two masters' compiled PDFs. xfail pre-fix:
        49-RED-EVIDENCE.md Failure mode 1 measured SHARED-CHAPTER-MARKER
        present 0 times in manual.pdf (master A) and 1 time in
        bmanual.pdf (master B) -- the build-scoped ledger claims `shared`
        for whichever parent's toctree translates first (bmaster,
        alphabetically), not per master."""
        manual_count = two_master_build["manual_pdf_text"].count(
            "SHARED-CHAPTER-MARKER"
        )
        bmanual_count = two_master_build["bmanual_pdf_text"].count(
            "SHARED-CHAPTER-MARKER"
        )
        assert manual_count == 1, (
            f"expected exactly 1 occurrence of SHARED-CHAPTER-MARKER in "
            f"manual.pdf (master A), got {manual_count}"
        )
        assert bmanual_count == 1, (
            f"expected exactly 1 occurrence of SHARED-CHAPTER-MARKER in "
            f"bmanual.pdf (master B), got {bmanual_count}"
        )

    @pytest.mark.xfail(strict=True, reason="flips in 49-04 (no guard yet)")
    def test_nested_docname_child_included_and_edge_key_escapes_unchanged(
        self, two_master_build
    ):
        """COMP-07, encoding: the path-separator-docname child sub/nested
        appears exactly once in EACH master's PDF, and the emitted guard
        line in shared.typ carries the docname exactly as
        escape_typst_string() produces it -- unchanged, since `sub/nested`
        contains no character the helper escapes. xfail pre-fix: the
        nested-docname child sub/nested is reachable pre-fix ONLY through
        bmaster's own unconditional include chain, and neither shared.typ
        nor sub/nested.typ carries any state-guard
        `if "..." in state(...).get() { ... }` line yet -- the current
        translator emits a bare `include("sub/nested.typ")` with no guard
        at all."""
        manual_count = two_master_build["manual_pdf_text"].count(
            "NESTED-DOCNAME-BODY-MARKER"
        )
        bmanual_count = two_master_build["bmanual_pdf_text"].count(
            "NESTED-DOCNAME-BODY-MARKER"
        )
        assert manual_count == 1, (
            f"expected exactly 1 occurrence of NESTED-DOCNAME-BODY-MARKER "
            f"in manual.pdf, got {manual_count}"
        )
        assert bmanual_count == 1, (
            f"expected exactly 1 occurrence of NESTED-DOCNAME-BODY-MARKER "
            f"in bmanual.pdf, got {bmanual_count}"
        )

        guard_pattern = re.compile(
            r'if "shared#0>sub/nested" in state\('
            + re.escape(f'"{STATE_KEY}"')
            + r', \(\)\)\.get\(\) \{ include\("sub/nested\.typ"\) \}'
        )
        assert guard_pattern.search(two_master_build["shared_content"]), (
            f"expected a state-guarded include line for sub/nested in "
            f"shared.typ, with the docname unchanged by escaping:\n"
            f"{two_master_build['shared_content']}"
        )

    @pytest.mark.xfail(strict=True, reason="flips in 49-04 (RED mode 1)")
    def test_shared_child_position_per_master_traversal(self, two_master_build):
        """COMP-07 / COMP-10: master A (index) resolves `shared` NESTED
        one level below `zmid` (first-encounter-wins via zmid's own
        toctree); master B (bmaster) resolves `shared` DIRECT, one level
        below its own heading -- both queried against the COMPILED
        document with the build directory as query root. xfail pre-fix:
        49-RED-EVIDENCE.md Failure mode 1 shows `Shared` entirely absent
        from manual.pdf's compiled outline -- master A's own toctree
        entry for `shared` is silently skipped (already claimed by
        bmaster's earlier translation), so there is no nested position to
        query at all."""
        build_dir = two_master_build["build_dir"]

        manual_outline = _query_heading_outline(
            two_master_build["manual_typ"], build_dir
        )
        index_level = _level_for_title(manual_outline, "Index")
        zmid_level = _level_for_title(manual_outline, "ZMid")
        shared_level_a = _level_for_title(manual_outline, "Shared")
        assert zmid_level == index_level + 1, (
            f"expected ZMid one level below Index "
            f"(index={index_level}, zmid={zmid_level})"
        )
        assert shared_level_a == zmid_level + 1, (
            f"expected Shared NESTED one level below ZMid in master A "
            f"(zmid={zmid_level}, shared={shared_level_a}) -- master A "
            f"must resolve the shared child at the position zmid's own "
            f"claim dictates, not its own direct entry"
        )

        bmanual_outline = _query_heading_outline(
            two_master_build["bmanual_typ"], build_dir
        )
        bmaster_level = _level_for_title(bmanual_outline, "BMaster")
        shared_level_b = _level_for_title(bmanual_outline, "Shared")
        assert shared_level_b == bmaster_level + 1, (
            f"expected Shared DIRECT, one level below BMaster in master B "
            f"(bmaster={bmaster_level}, shared={shared_level_b})"
        )

    @pytest.mark.xfail(strict=True, reason="flips in 49-04 (RED mode 1)")
    def test_document_order_interleaving_preserved(self, two_master_build):
        """COMP-08: master A's pypdf-extracted text preserves document
        order -- the prose-before marker, then ZMid's own body, then
        Shared's own body (nested under ZMid post-fix), then the trailing
        "Indices and tables" section's prose-after marker, strictly
        increasing offsets. Every marker asserted here is plain ASCII with
        no zero-width characters (a zero-width space poisons pypdf
        extraction at an unrelated glyph boundary -- a hazard measured in
        v0.7.0 Phase 37). xfail pre-fix: 49-RED-EVIDENCE.md Failure mode 1
        measured SHARED-CHAPTER-MARKER absent (count 0) from manual.pdf
        entirely, so the shared-body position in this ordered sequence
        cannot be observed at all until the shared chapter reaches
        master A."""
        text = two_master_build["manual_pdf_text"]
        before_offset = text.index("PROSE-BEFORE-MARKER")
        zmid_offset = text.rindex("ZMid")
        shared_offset = text.index("SHARED-CHAPTER-MARKER")
        after_offset = text.rindex("PROSE-AFTER-MARKER")
        assert before_offset < zmid_offset < shared_offset < after_offset, (
            f"expected strictly increasing offsets "
            f"(before={before_offset}, zmid={zmid_offset}, "
            f"shared={shared_offset}, after={after_offset}) in:\n{text}"
        )

    def test_empty_include_file_list_emits_no_scope_block(self, two_master_build):
        """COMP-08, empty: emptytoc's own toctree contributes NO entries
        to includefiles, so its emitted content file carries no
        `context { ... }` block at all -- and its surrounding prose
        (reached, both pre- and post-fix, via bmaster's own unbroken
        include chain: bmaster -> shared -> sub/nested -> emptytoc, which
        involves no cross-master claim contest) still appears in source
        order in the compiled PDF. This is an INVARIANCE guard, not an
        xfail: 49-RED-EVIDENCE.md's Task 1 measurement of the emitted
        emptytoc.typ already shows no `context {` construct on the
        unfixed tree."""
        emptytoc_content = two_master_build["emptytoc_content"]
        assert "context {" not in emptytoc_content, (
            f"expected no context {{ ... }} block for an empty toctree, "
            f"got:\n{emptytoc_content}"
        )

        text = two_master_build["bmanual_pdf_text"]
        before_offset = text.index("EMPTYTOC-PROSE-BEFORE-MARKER")
        after_offset = text.index("EMPTYTOC-PROSE-AFTER-MARKER")
        assert before_offset < after_offset, (
            f"expected EMPTYTOC-PROSE-BEFORE-MARKER before "
            f"EMPTYTOC-PROSE-AFTER-MARKER in bmanual.pdf "
            f"(before={before_offset}, after={after_offset}):\n{text}"
        )

    @pytest.mark.xfail(strict=True, reason="flips in 49-04 (RED mode 2)")
    def test_diamond_shared_content_file_identical_across_masters(
        self, two_master_build
    ):
        """COMP-09: the shared child's marker count is exactly 1 in EACH
        master's PDF AND exactly one shared content file exists on disk
        with the digest 49-RED-EVIDENCE.md's Failure mode 2 recorded -- the
        digest comparison is what proves the per-master difference comes
        from the wrapper's published state, not from two divergent
        content files. xfail pre-fix: 49-RED-EVIDENCE.md Failure mode 2
        shows the SAME on-disk shared.typ (one SHA-256 digest) still
        produces a 0/1 marker-count split, not 1/1 -- a build-scoped
        ledger picks exactly one winner across the whole build, not one
        winner per master."""
        manual_count = two_master_build["manual_pdf_text"].count(
            "SHARED-CHAPTER-MARKER"
        )
        bmanual_count = two_master_build["bmanual_pdf_text"].count(
            "SHARED-CHAPTER-MARKER"
        )
        assert (
            manual_count == 1
        ), f"expected exactly 1 occurrence in manual.pdf, got {manual_count}"
        assert (
            bmanual_count == 1
        ), f"expected exactly 1 occurrence in bmanual.pdf, got {bmanual_count}"

        build_dir = two_master_build["build_dir"]
        shared_files = sorted(build_dir.rglob("shared.typ"))
        assert (
            len(shared_files) == 1
        ), f"expected exactly one shared.typ on disk, found: {shared_files}"
        expected_digest = (
            "672b5d2c7c86e73b12c503341e61477983317d7ac6fef08cb5f8a8f4dff012b5"
        )
        assert two_master_build["shared_digest"] == expected_digest, (
            f"shared.typ's SHA-256 digest changed from the "
            f"49-RED-EVIDENCE.md Failure mode 2 recording "
            f"({expected_digest}); got {two_master_build['shared_digest']} "
            f"-- if this fixture's content genuinely changed, update the "
            f"digest AND re-record Failure mode 2, do not silently patch "
            f"this constant"
        )

    @pytest.mark.xfail(strict=True, reason="flips in 49-04 (no #state yet)")
    def test_published_edge_sets_match_specification_two_master(self, two_master_build):
        """The published edge sets themselves: for each of manual.typ and
        bmanual.typ, the emitted wrapper's state publication line lists
        EXACTLY the edge keys 49-EXPECTED-STRUCTURE.md's Emission contract
        derives for that master, in DFS discovery order, rendered with the
        array-literal trailing-comma rule -- a structural regex assertion
        over the emitted line, not a full-file exact-string diff, per
        binding constraint #6. xfail pre-fix: neither manual.typ nor
        bmanual.typ carries any #state("typsphinx:include-edges", ())
        publication line yet -- the current wrapper body is a bare
        #include(...) with nothing preceding it."""
        pattern = STATE_PUBLICATION_PATTERN
        for wrapper_name, wrapper_text_key in (
            ("manual.typ", "manual_wrapper_text"),
            ("bmanual.typ", "bmanual_wrapper_text"),
        ):
            wrapper_text = two_master_build[wrapper_text_key]
            match = pattern.search(wrapper_text)
            assert match is not None, (
                f"expected a #state(...).update((...)) publication line "
                f"in {wrapper_name}:\n{wrapper_text}"
            )
            expected = _render_edge_keys_literal(TWO_MASTER_EDGE_KEYS[wrapper_name])
            assert match.group(1) == expected, (
                f"{wrapper_name}'s published edge keys "
                f"({match.group(1)!r}) did not match the specification's "
                f"derived set ({expected!r})"
            )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the mirror-pair heading-level gate",
)
@pytest.mark.slow
class TestStateGuardMirrorPairComposition:
    """
    COMP-09/COMP-10 real-compile gate over ``state_guard_mirror_pair_gate``
    -- two masters differing only in one toctree's entry order, plus the
    ``soloist`` no-nesting control.
    """

    @pytest.mark.xfail(strict=True, reason="flips in 49-04 (RED mode 4)")
    def test_mirror_pair_resolved_heading_levels_and_source_divergence(
        self, mirror_pair_build
    ):
        """COMP-09 / COMP-10: xmastera resolves Shared NESTED one level
        below ZMid; xmasterb resolves Shared AND zmid both DIRECT, one
        level below its own heading -- the two masters' .rst sources
        differ only in the order of their toctree's two entries, so the
        divergence is attributable to traversal order alone. xfail
        pre-fix: 49-RED-EVIDENCE.md Failure mode 4 measured [1,1,1,2,2]
        for xmastera (Shared placed DIRECT, a sibling of ZMid, not
        nested under it -- the write-time ledger emits both of
        xmastera's own toctree entries unconditionally within the SAME
        scope) and [1,1,1] for xmasterb (both children entirely absent,
        claimed by xmastera's earlier translation)."""
        build_dir = mirror_pair_build["build_dir"]

        mastera_outline = _query_heading_outline(
            mirror_pair_build["mastera_typ"], build_dir
        )
        xmastera_level = _level_for_title(mastera_outline, "XMasterA")
        zmid_level_a = _level_for_title(mastera_outline, "ZMid")
        shared_level_a = _level_for_title(mastera_outline, "Shared")
        assert zmid_level_a == xmastera_level + 1, (
            f"expected ZMid one level below XMasterA "
            f"(xmastera={xmastera_level}, zmid={zmid_level_a})"
        )
        assert shared_level_a == zmid_level_a + 1, (
            f"expected Shared NESTED one level below ZMid in xmastera "
            f"(zmid={zmid_level_a}, shared={shared_level_a})"
        )

        masterb_outline = _query_heading_outline(
            mirror_pair_build["masterb_typ"], build_dir
        )
        xmasterb_level = _level_for_title(masterb_outline, "XMasterB")
        shared_level_b = _level_for_title(masterb_outline, "Shared")
        zmid_level_b = _level_for_title(masterb_outline, "ZMid")
        assert shared_level_b == xmasterb_level + 1, (
            f"expected Shared DIRECT, one level below XMasterB "
            f"(xmasterb={xmasterb_level}, shared={shared_level_b})"
        )
        assert zmid_level_b == xmasterb_level + 1, (
            f"expected ZMid ALSO direct, one level below XMasterB "
            f"(xmasterb={xmasterb_level}, zmid={zmid_level_b}) -- zmid's "
            f"own claim on shared is lost, but zmid itself still resolves "
            f"as xmasterb's direct second entry"
        )

        xmastera_rst = (MIRROR_PAIR_DIR / "xmastera.rst").read_text(encoding="utf-8")
        xmasterb_rst = (MIRROR_PAIR_DIR / "xmasterb.rst").read_text(encoding="utf-8")
        assert _toctree_entries(xmastera_rst) == [
            "zmid",
            "shared",
        ], "xmastera.rst's toctree entries changed from ['zmid', 'shared']"
        assert _toctree_entries(xmasterb_rst) == [
            "shared",
            "zmid",
        ], "xmasterb.rst's toctree entries changed from ['shared', 'zmid']"

    def test_no_nesting_control_resolves_at_top_level(self, mirror_pair_build):
        """COMP-10, empty: a master with no toctree at all (soloist)
        resolves its own heading at the top level, proving the offset
        mechanism adds nothing when there is nothing to nest. This is an
        INVARIANCE guard, not an xfail: 49-RED-EVIDENCE.md's Failure mode
        4 measured this already holding on the unfixed tree
        ([1, 1, 1] -- template headings plus Solo Master, all at level
        1)."""
        build_dir = mirror_pair_build["build_dir"]
        outline = _query_heading_outline(mirror_pair_build["solomaster_typ"], build_dir)
        solo_level = _level_for_title(outline, "Solo Master")
        assert solo_level == 1, (
            f"expected Solo Master's own heading to resolve at the top "
            f"level with nothing to nest; got {solo_level} in {outline}"
        )

    @pytest.mark.xfail(strict=True, reason="flips in 49-04 (no #state yet)")
    def test_published_edge_sets_match_specification_mirror_pair(
        self, mirror_pair_build
    ):
        """The published edge sets themselves: for each of mastera.typ,
        masterb.typ and solomaster.typ, the emitted wrapper's state
        publication line lists EXACTLY the edge keys the specification
        derives -- including solomaster.typ's empty `()` (a master with an
        empty edge set still publishes the state, just with zero keys).
        xfail pre-fix: none of mastera.typ/masterb.typ/solomaster.typ
        carries any #state("typsphinx:include-edges", ()) publication
        line yet."""
        pattern = STATE_PUBLICATION_PATTERN
        for wrapper_name, wrapper_text_key in (
            ("mastera.typ", "mastera_wrapper_text"),
            ("masterb.typ", "masterb_wrapper_text"),
            ("solomaster.typ", "solomaster_wrapper_text"),
        ):
            wrapper_text = mirror_pair_build[wrapper_text_key]
            match = pattern.search(wrapper_text)
            assert match is not None, (
                f"expected a #state(...).update((...)) publication line "
                f"in {wrapper_name}:\n{wrapper_text}"
            )
            expected = _render_edge_keys_literal(MIRROR_PAIR_EDGE_KEYS[wrapper_name])
            assert match.group(1) == expected, (
                f"{wrapper_name}'s published edge keys "
                f"({match.group(1)!r}) did not match the specification's "
                f"derived set ({expected!r})"
            )


@pytest.fixture(scope="class")
def single_master_pdf_text(tmp_path_factory):
    """
    Build ``tests/fixtures/xref_orphan_degrade_render_gate`` (an EXISTING
    single-master fixture, not one this plan owns) ONCE per class and
    return its compiled PDF's ``pypdf``-extracted text.

    Module-level, not a class-scoped instance method (pytest deprecates
    class-scoped fixtures defined as instance methods -- this project's
    own ``filterwarnings = ["error::DeprecationWarning"]`` escalates that
    warning to a hard error), matching the ``two_master_build``/
    ``mirror_pair_build`` fixtures above.
    """
    build_dir = tmp_path_factory.mktemp("single_master_invariance") / "_build"
    result = _run_sphinx_build_typst(SINGLE_MASTER_DIR, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    master_typ = build_dir / "master.typ"
    assert master_typ.exists(), "master.typ was not emitted"
    pdf_path = build_dir / "master.pdf"
    typst.compile(str(master_typ), output=str(pdf_path))
    return _extract_pdf_text(pdf_path)


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the single-master invariance control",
)
@pytest.mark.slow
class TestStateGuardSingleMasterInvariance:
    """
    COMP-07, single-master invariance control: this phase's fix must not
    be a change that only happens to work for two masters -- an EXISTING
    single-master fixture's rendered content stays byte-identical in the
    sense that mattered before this phase (the reachable body content is
    unchanged), asserted against content read literally from the
    fixture's OWN .rst source, never from a build.
    """

    def test_single_master_build_unaffected_by_composition_change(
        self, single_master_pdf_text
    ):
        """COMP-07: a single-master project (no document toctree'd by more
        than one master, so no first-encounter-wins contest exists at
        all) still renders its own included document's content -- taken
        literally from tests/fixtures/xref_orphan_degrade_render_gate/
        included.rst's own heading text, not from a build. This is an
        INVARIANCE guard, not an xfail: this phase's mechanism change only
        alters the DECISION for content reachable from more than one
        master, which a single-master project never exercises."""
        expected_heading = "Included Target Section"
        assert expected_heading in single_master_pdf_text, (
            f"expected {expected_heading!r} (read literally from "
            f"included.rst) in the compiled single-master PDF text:\n"
            f"{single_master_pdf_text}"
        )

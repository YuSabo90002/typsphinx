"""
TOC-01 resolved-level render gate (Phase 44.1, plan 01, SC#1/SC#2/SC#5).

This module proves -- against a real compile, not a grep of emitted ``.typ``
-- that a document reached through a ``toctree`` resolves its own title one
level below its parent's, and that nested toctrees compose so a grandchild
resolves two levels below the master.

The measurement technique is new for this suite: every other render gate
under ``tests/`` ends in a PDF-text-extraction round trip from a compiled
PDF. This gate instead asks Typst itself for the *resolved* heading level
via ``typst.query(..., field="level", root=...)`` -- it needs no PDF and no
PDF-text-extraction dependency, because heading *level* (as opposed to body
text) is available directly from the compiled document's introspectable
tree.

Fixture: ``tests/fixtures/integration_nested_toctree`` (parent ``index.rst``
-> child ``chapter1/index.rst`` -> grandchildren ``chapter1/section1.rst``
and ``chapter1/section2.rst``), reused as-is per 44.1-CONTEXT.md's
"Claude's Discretion" note -- it already has the required
parent -> child -> grandchild shape and builds clean today.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import typsphinx

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path, extra_args: tuple = ()
) -> subprocess.CompletedProcess:
    """
    Run `sphinx-build -b typst` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as `sys.executable -m sphinx` (the sphinx-build console entry
    point's module form) rather than shelling out to the package-manager
    `run sphinx-build` idiom: this guarantees the exact interpreter/venv
    already running this test is reused, with no dependency on external
    PATH resolution of a package-manager executable. This mattered in this
    project's dev sandbox specifically -- a stray non-Nix package-manager
    binary installed into `.venv/bin` (shadowing the correct Nix-provided
    one earlier on PATH for subprocess children) made the
    `run sphinx-build` subprocess form exit 127 ("Could not start
    dynamically linked executable") when invoked from inside a
    pytest-launched subprocess, even though the same command succeeded when
    run directly in a shell. That cause was removed by QUA-04 (2026-08-10);
    `sys.executable -m sphinx` is kept regardless, because it depends on no
    PATH resolution at all -- a better reason than the hazard ever was.

    `extra_args` is an optional tuple of additional sphinx-build CLI
    arguments (e.g. `("-D", "todo_include_todos=0")`) spliced into the
    command list before the source dir -- default `()` keeps every
    pre-existing call site unchanged.
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


def _query_heading_levels(typ_path: Path, root: Path) -> list:
    """
    Return the full, ordered list of *resolved* heading levels for the
    compiled document at `typ_path`.

    `root` MUST be the build directory, never the `.typ` file's own
    directory -- the emitted `include()` paths inside a master document are
    relative to the build root, and Typst resolves them against `root`
    during `query`/`compile`. Passing the file's own directory as `root`
    would make every `include()` inside a subdirectory-nested master resolve
    incorrectly (or not at all).

    `typst.query` returns a JSON string, not a Python object -- this must be
    `json.loads`-ed by the caller (here, internally).
    """
    result = typst.query(str(typ_path), "heading", field="level", root=str(root))
    return json.loads(result)


def _extract_body_text(body: dict) -> str:
    """
    Defensively derive plain text from a Typst heading element's `body`
    content dict.

    The common case is `{"func": "text", "text": "..."}`. Some headings
    (e.g. the template's own outline-caption heading) have an empty
    `{"func": "sequence", "children": []}` body instead -- return the empty
    string for that shape rather than raising. Any other shape not
    recognized here falls back to `repr(body)` so a test failure message
    still names *something* identifiable instead of crashing the assertion
    machinery itself.
    """
    if not isinstance(body, dict):
        return repr(body)
    if body.get("func") == "text" and "text" in body:
        return body["text"]
    if body.get("func") == "sequence" and not body.get("children"):
        return ""
    return repr(body)


def _query_heading_outline(typ_path: Path, root: Path) -> list:
    """
    Return the full, ordered list of `(level, title)` pairs for the compiled
    document at `typ_path` -- a companion to `_query_heading_levels` that
    also names *which* heading sits at which level, so assertion failure
    messages and evidence-file records are self-describing instead of bare
    integer lists.

    Same `root=` requirement as `_query_heading_levels` applies here.
    """
    result = typst.query(str(typ_path), "heading", root=str(root))
    elements = json.loads(result)
    return [(el["level"], _extract_body_text(el.get("body"))) for el in elements]


@pytest.fixture(scope="class")
def nested_toctree_heading_outline(tmp_path_factory):
    """
    Build `tests/fixtures/integration_nested_toctree` ONCE per class and
    return `(levels, outline, master_typ, build_dir)` for the compiled
    master document.

    `tmp_path_factory`-based (not the function-scoped `tmp_path`) so this
    fixture can be class-scoped without a pytest ScopeMismatch -- mirrors
    `admonition_render_gate_pdf_text` in `tests/test_pdf_render_gate.py`,
    which depends only on `tmp_path_factory` for the identical reason.
    """
    source_dir = Path(__file__).parent / "fixtures" / "integration_nested_toctree"
    build_dir = tmp_path_factory.mktemp("heading_depth_render_gate") / "_build"

    result = _run_sphinx_build_typst(source_dir, build_dir)
    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    master_typ = build_dir / "index.typ"
    assert master_typ.exists(), "index.typ was not generated"

    levels = _query_heading_levels(master_typ, build_dir)
    outline = _query_heading_outline(master_typ, build_dir)
    return levels, outline, master_typ, build_dir


def _level_for_title(outline: list, title: str) -> int:
    """
    Locate the resolved level of the heading whose body text equals `title`
    in an `(level, title)` outline, or fail with a message naming the whole
    outline (so a lookup miss is debuggable, not a bare KeyError).
    """
    for level, body_title in outline:
        if body_title == title:
            return level
    raise AssertionError(f"No heading titled {title!r} found in outline: {outline}")


@pytest.mark.skipif(
    not TYPST_AVAILABLE, reason="typst-py is required for the resolved-level gate"
)
@pytest.mark.slow
class TestToctreeHeadingDepthRenderGate:
    """
    Real-compile acceptance gate for TOC-01 (Phase 44.1): a document reached
    through a `toctree` must resolve its own title exactly one level below
    its parent's -- and nested toctrees must compose, so a grandchild
    resolves two levels below the master (D-07).

    Every expected value below was derived by running `sphinx-build -b
    typst` and `typst.query` in the same session that authored this file,
    against a mechanically-substituted scratch copy of this fixture's
    pre-fix build output (the `level:` -> `depth:` and toctree-scope-opener
    substitutions that plan 01's tasks 2 and 3 land for real) -- not copied
    from 44.1-CONTEXT.md or any other planning document.
    """

    def test_child_document_title_resolves_one_level_below_master(
        self, nested_toctree_heading_outline
    ):
        """SC#1: the child ("Chapter 1") resolves one level below the
        master ("Nested Toctree Test")."""
        _levels, outline, _master_typ, _build_dir = nested_toctree_heading_outline
        master_level = _level_for_title(outline, "Nested Toctree Test")
        child_level = _level_for_title(outline, "Chapter 1")
        assert child_level == master_level + 1, (
            f"expected child_level == master_level + 1 "
            f"(master={master_level}, child={child_level}); outline={outline}"
        )

    def test_grandchild_title_resolves_one_level_below_child(
        self, nested_toctree_heading_outline
    ):
        """SC#2 (D-07): the grandchild ("Section 1") resolves one level
        below the child ("Chapter 1"), i.e. two below the master."""
        _levels, outline, _master_typ, _build_dir = nested_toctree_heading_outline
        master_level = _level_for_title(outline, "Nested Toctree Test")
        child_level = _level_for_title(outline, "Chapter 1")
        grandchild_level = _level_for_title(outline, "Section 1")
        assert grandchild_level == child_level + 1, (
            f"expected grandchild_level == child_level + 1 "
            f"(child={child_level}, grandchild={grandchild_level}); "
            f"outline={outline}"
        )
        assert grandchild_level == master_level + 2, (
            f"expected grandchild_level == master_level + 2 "
            f"(master={master_level}, grandchild={grandchild_level}); "
            f"outline={outline}"
        )

    def test_resolved_level_sequence_is_exact_and_ordered(
        self, nested_toctree_heading_outline
    ):
        """
        The ordering edge: assert the FULL resolved-level sequence
        positionally against an expected list, never with `in`, `set()`,
        `sorted()`, or a count -- a set/count assertion would not detect two
        headings swapping levels.

        Expected sequence derived in this session by applying both of
        plan 01's substitutions (`heading(level:` -> `heading(depth:`, and
        the toctree scope opener `{ set heading(offset: 1) }` ->
        `context { set heading(offset: heading.offset + 1) }`) to a scratch
        copy of this fixture's pre-fix build output, then re-running
        `typst.query(..., field="level", root=...)` against the substituted
        copy: `[1, 1, 1, 2, 3, 4, 3, 4]`, for the outline
        `(template caption, "Contents", "Nested Toctree Test", "Chapter 1",
        "Section 1", "Content of section 1", "Section 2",
        "Content of section 2")`.
        """
        levels, outline, _master_typ, _build_dir = nested_toctree_heading_outline
        expected = [1, 1, 1, 2, 3, 4, 3, 4]
        assert levels == expected, (
            f"resolved level sequence mismatch: got {levels}, "
            f"expected {expected}; outline={outline}"
        )

    def test_resolved_level_sequence_is_stable_across_repeated_queries(
        self, nested_toctree_heading_outline
    ):
        """
        The ordering backstop: querying the SAME already-built master twice
        (no rebuild) must return the identical list. Whether Typst's
        `query` introspection order is *specified* and stable is not
        established by any source artifact available to this phase
        (44.1-01-PLAN.md `flagged_assumptions` #1) -- this test checks it
        empirically rather than assuming it.
        """
        _levels, _outline, master_typ, build_dir = nested_toctree_heading_outline

        levels_a = _query_heading_levels(master_typ, build_dir)
        levels_b = _query_heading_levels(master_typ, build_dir)
        assert (
            levels_a == levels_b
        ), f"repeated query of the same build disagreed: {levels_a} != {levels_b}"


@pytest.mark.slow
class TestNoHeadingOffsetOutsideVisitToctree:
    """
    SC#8 (Phase 44.1, plan 04): nothing outside `visit_toctree` introduces a
    heading offset -- carried by a permanent two-leg guard rather than by
    inspection alone.

    Leg 1 (static) reads the packaged `typsphinx/templates/base.typ`
    directly through the installed package (`Path(typsphinx.__file__)`, not
    a checkout-relative path) and asserts it contains no
    `heading(offset` construct at all.

    Leg 2 (live) builds `tests/fixtures/integration_nested_toctree` (a
    fixture with no custom `typst_template` or `typst_package` configured,
    so `TypstBuilder._write_template_file` falls through to the packaged
    default and writes it as `_template.typ` at the build's output root --
    the same fixture `nested_toctree_heading_outline` above already builds)
    and asserts the emitted `_template.typ` ALSO contains no
    `heading(offset` construct. This is the half a static grep of the
    packaged source cannot cover, because `_write_template_file` composes
    what it actually writes (parameter substitution, asset copying) rather
    than copying the source file byte-for-byte.

    Both legs assert absence, which is vacuous on its own (an empty or
    unbuilt input would also show no `heading(offset` construct) -- so both
    legs share one non-vacuity control: the SAME build's own master `.typ`
    MUST contain the offset expression `visit_toctree` emits, proving the
    searched construct is producible in this exact build and that its
    absence from the template is therefore informative, not accidental.
    """

    def test_packaged_base_typ_carries_no_heading_offset(self):
        """
        Static leg: read the packaged `typsphinx/templates/base.typ`
        through the installed package location, not a path relative to
        this test file's own checkout position -- so the guard follows
        wherever `typsphinx` is actually installed from (matters for a
        worktree/editable-install setup where checkout-relative and
        installed-package paths can diverge).
        """
        template_path = Path(typsphinx.__file__).parent / "templates" / "base.typ"
        assert template_path.exists(), f"expected {template_path} to exist"
        content = template_path.read_text(encoding="utf-8")
        assert "heading(offset" not in content, (
            "typsphinx/templates/base.typ must not introduce its own "
            "heading offset -- that responsibility belongs solely to "
            "visit_toctree (SC#8)"
        )

    def test_emitted_template_file_carries_no_heading_offset(
        self, nested_toctree_heading_outline
    ):
        """
        Live leg: the `_template.typ` actually WRITTEN by
        `TypstBuilder._write_template_file` for a real build must also
        carry no `heading(offset` construct -- this is composed output
        (parameter substitution applied), not a copy of the packaged
        source, so it must be checked independently of the static leg.
        """
        _levels, _outline, _master_typ, build_dir = nested_toctree_heading_outline
        emitted_template = build_dir / "_template.typ"
        assert (
            emitted_template.exists()
        ), f"expected {emitted_template} to have been written by the build"
        content = emitted_template.read_text(encoding="utf-8")
        assert "heading(offset" not in content, (
            "the emitted _template.typ must not introduce its own heading "
            "offset -- that responsibility belongs solely to visit_toctree "
            "(SC#8)"
        )

    def test_offset_expression_is_producible_in_the_same_build(
        self, nested_toctree_heading_outline
    ):
        """
        Non-vacuity control for both legs above: the SAME build's master
        `.typ` DOES contain the offset expression `visit_toctree` emits --
        proving the searched construct is producible in this exact build,
        so its absence from the template (both packaged and emitted) is
        informative rather than an artifact of an empty/unbuilt input.
        """
        _levels, _outline, master_typ, _build_dir = nested_toctree_heading_outline
        content = master_typ.read_text(encoding="utf-8")
        assert "set heading(offset: heading.offset + 1)" in content, (
            "expected the master's own .typ to contain the offset "
            "expression visit_toctree emits -- if this fails, the "
            "absence asserted by the two legs above would be vacuous"
        )

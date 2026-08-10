"""
Pipeline-stage writer enumeration and end-to-end falsification gate for
CONF-09's ``authors`` precedence rule (Phase 44.2, round-4 gap closure).

**The enumeration axis is the PIPELINE STAGE that determines the emitted
``authors`` -- deliberately widened from the sibling module's
``map_parameters()``-only frame.** ``tests/test_params_authors_writers.py``
enumerates writers inside ``TemplateEngine.map_parameters()`` alone; this
module enumerates across the whole pipeline -- ``map_parameters()`` AND
``TypstWriter.translate()`` -- because a ``params``-carrier write inside
``render()`` used to be a real, later-stage writer of the same key that a
``map_parameters()``-only frame could not see.

**Phase 45.1 (D-B) update.** ``render()``'s two-call additive union
(``all_params.update(params)`` then
``all_params.update(self.typst_template_params)``) is GONE, replaced by a
single boolean-guarded exclusive branch
(``if self.typst_template_params_specified: all_params = dict(...)  else:
all_params = dict(...)``). This is a plain ``Name`` assignment, not a
``Subscript`` assign or an ``.update()`` call on a ``PARAMS_CARRIERS`` name,
so ``render()`` no longer appears in this module's AST-walked stage-site
enumeration at all -- the whole-strategy swap this branch performs cannot be
expressed as a per-key "writer" in this pipeline-stage frame, by
construction. ``test_render_applies_template_function_params_after_map_parameters_output``
below is re-derived from an order assertion (D-04's old mechanism) into a
structural assertion about the new exclusive branch (D-B's mechanism); it
is kept unlinked from ``EXPECTED_STAGE_SITES``/``REACHABLE_STAGE_KNOBS``/
``UNREACHABLE_STAGE_PROOFS`` below since the site it used to pin no longer
exists in that enumeration's terms.

Rounds 1, 2 and 3 of this correction each derived their search set from the
prose being corrected rather than from the code: round 1 enumerated config
shapes, round 2 enumerated the mapping's source key, and round 3 built a
per-sentence enumeration whose row space was ``SOURCE_KEYS x TARGET_KEYS x
presence`` -- it graded nine sites in ``configuration.rst`` but had no axis
at all for ``render()``'s later merge, so the false clause it was built to
catch sat inside one graded site's own cited line range, ungraded. Widening
the frame from one function to the pipeline is what this module tests, not
the render()-stage behaviour itself -- ``render()`` and ``map_parameters()``
are both correct and have been throughout this phase; four rounds of
failure are all text failures.

This module therefore enumerates every stage from the CODE (an ``ast`` walk
over ``typsphinx/template_engine.py`` and ``typsphinx/writer.py``) and
requires every enumerated stage to be classified REACHABLE (it can
determine the emitted ``authors``) or UNREACHABLE-WITH-PROOF (a named test
in this module proves it cannot), under a partition assertion that admits
no silent drop of an enumerated site from either class.

**Deliberate convention note.** ``44.2-PATTERNS.md`` prescribes discrete,
individually-named functions over ``@pytest.mark.parametrize`` for this
phase's precedence modules; this module keeps that convention throughout,
including its two real-``sphinx-build`` gates below.
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

from typsphinx.template_engine import TemplateEngine

REPO_ROOT = Path(__file__).resolve().parents[1]

TEMPLATE_ENGINE_PATH = REPO_ROOT / "typsphinx" / "template_engine.py"
WRITER_PATH = REPO_ROOT / "typsphinx" / "writer.py"
CONFIGURATION_RST_PATH = (
    REPO_ROOT / "docs" / "source" / "user_guide" / "configuration.rst"
)

# The local names that carry template parameters anywhere in `typsphinx/`.
# A new carrier name appearing in the source (e.g. a future
# `extra_params` dict) is itself a FRAME CHANGE -- it must be added here
# deliberately, after being read and understood, never discovered later by
# a silently-blind walker that only ever looked at "params"/"all_params".
PARAMS_CARRIERS = ("params", "all_params")

# Hand-declared, sorted tuple of every `<relpath>::<function>::<assign|
# update>::<slice>` id `_stage_sites()` is expected to find at GAP_BASE.
# Frozen by READING typsphinx/template_engine.py:387-535 and
# typsphinx/writer.py:176-335 -- never by calling `_stage_sites()` and
# pasting its output, which would make `test_pipeline_stage_sites_that_
# can_determine_authors_are_exactly_these` a tautology that passes for any
# pipeline, including one with an unenumerated tenth site.
#
# `map_parameters()` writes `params["authors"]` at TWO distinct source
# sites: the `typst_authors` seed (first, unqualified id) and the
# non-package back-fill (second occurrence of the same literal target
# key). Both produce the identical base id
# `typsphinx/template_engine.py::map_parameters::assign::authors` under
# the `<relpath>::<function>::<kind>::<slice>` scheme -- `_stage_sites()`
# disambiguates same-function repeats with a `#<n>` ordinal suffix on the
# second and later occurrence (in source order) so the seed and the
# back-fill remain separately addressable dict keys below. This is a
# deliberate, documented widening of the bare id scheme, made necessary by
# a real collision the naive scheme would hit -- not an arbitrary choice.
#
# Phase 45.1 (D-B): `render()` no longer contributes any site here.
# `typsphinx/template_engine.py::render::update::params` and
# `::render::update::self.typst_template_params` are GONE -- D-B replaced
# both `.update()` calls with a single `all_params = dict(...)` /
# `all_params = dict(...)` boolean-guarded plain-`Name` assignment, which
# `_StageSiteVisitor` (by design) does not track: it only tracks `Subscript`
# assigns and `.update()` calls on a `PARAMS_CARRIERS` name, and a
# whole-dict swap is neither.
EXPECTED_STAGE_SITES = tuple(
    sorted(
        [
            "typsphinx/template_engine.py::map_parameters::assign::authors",
            "typsphinx/template_engine.py::map_parameters::assign::authors#2",
            "typsphinx/template_engine.py::map_parameters::assign::template_key",
            "typsphinx/template_engine.py::map_parameters::assign::title",
            "typsphinx/template_engine.py::map_parameters::assign::date",
            "typsphinx/template_engine.py::map_parameters::assign::key",
            "typsphinx/writer.py::translate::update::toctree_options",
        ]
    )
)

# Hand-declared dict, stage-site id -> the user-facing config knob that
# controls it. Every entry is REACHABLE: there exists a real configuration
# in which this site's write is the one that survives to the emitted
# `authors`.
REACHABLE_STAGE_KNOBS = {
    # W1 (round 3's frame): the typst_authors seed. Reachable whenever no
    # later stage replaces it.
    "typsphinx/template_engine.py::map_parameters::assign::authors": "typst_authors",
    # W2 (round 3's frame): the mapping loop's params[template_key] =
    # value. Reachable whenever an entry of typst_template_mapping targets
    # "authors".
    "typsphinx/template_engine.py::map_parameters::assign::template_key": "typst_template_mapping",
    # W3 (round 3's frame, but its true controlling knob was never named):
    # the non-package back-fill's params["authors"] = () default.
    # Reachable whenever nothing above wrote "authors" AND typst_package
    # is unset -- typst_package is the guard that decides whether this
    # back-fill runs at all (`if not self.typst_package:`), so it is the
    # knob that controls this specific site, not typst_authors again.
    "typsphinx/template_engine.py::map_parameters::assign::authors#2": "typst_package",
    # W7 -- THE WRITER ROUND 3'S FRAME EXCLUDED ENTIRELY -- REMOVED per
    # D-B. Pre-45.1, this was reachable whenever typst_template_function
    # was a dict carrying params["authors"], winning per render()'s merge
    # ORDER. Post-D-B there is no per-key "write" left to enumerate here:
    # when "params" is declared, render()'s exclusive branch discards
    # EVERY key map_parameters() produced (not just "authors") and
    # replaces the whole dict with the declared set. That whole-strategy
    # swap is proven directly by
    # test_render_applies_template_function_params_after_map_parameters_output
    # below, deliberately OUTSIDE this partition -- it is not expressible
    # as a per-key REACHABLE/UNREACHABLE row in this pipeline-stage frame.
}

# Hand-declared dict, stage-site id -> the name of the test IN THIS MODULE
# that proves the site cannot determine the emitted `authors`. Never
# derived from the code's own output -- each proof is either a structural
# fact about the site's OWN id (its literal target key differs from
# "authors", so it cannot write that key by construction) or a dedicated
# behavioural/AST test.
UNREACHABLE_STAGE_PROOFS = {
    # The back-fill's OTHER two literals target "title" and "date" -- not
    # "authors" -- proven definitionally by the enumeration itself: an id
    # whose slice differs from "authors" cannot write params["authors"].
    "typsphinx/template_engine.py::map_parameters::assign::title": (
        "test_pipeline_stage_sites_that_can_determine_authors_are_exactly_these"
    ),
    "typsphinx/template_engine.py::map_parameters::assign::date": (
        "test_pipeline_stage_sites_that_can_determine_authors_are_exactly_these"
    ),
    # The typst_elements loop's params[key] = ... is gated by
    # ELEMENTS_ALLOWLIST (papersize/fontsize/lang -- no "authors" key ever
    # reaches this assignment; an unknown key raises ExtensionError before
    # reaching params at all), so its slice can never be the literal
    # "authors" either.
    "typsphinx/template_engine.py::map_parameters::assign::key": (
        "test_pipeline_stage_sites_that_can_determine_authors_are_exactly_these"
    ),
    # writer.py's params.update(toctree_options) -- a REAL params writer
    # in the pipeline, excluded by proof of its returned key set.
    "typsphinx/writer.py::translate::update::toctree_options": (
        "test_toctree_options_cannot_reach_authors_or_title"
    ),
}

SEED_NAME = "Jane Doe"
TEMPLATE_FUNCTION_AUTHOR = "FROM TEMPLATE FUNCTION"


def _write_three_knob_project(srcdir: Path, with_template_function: bool) -> None:
    """Write a tmp-path Sphinx project exercising the exact three-knob
    configuration ``44.2-VERIFICATION.md`` reproduced with a real
    ``sphinx-build``: ``typst_authors`` set (the seed), a
    ``typst_template_mapping`` that deliberately targets ONLY ``title`` --
    so the seed survives stage 1 (``map_parameters()``) by the published
    stage-1 rule -- and, when ``with_template_function`` is True, a
    ``typst_template_function`` dict form carrying ``params["authors"]``.
    ``with_template_function`` is the ONLY difference between this project
    and its control: the single conditional branch below is the entire
    delta."""
    (srcdir / "index.rst").write_text(
        "Test Document\n=============\n\nThis is a test document.\n"
    )
    conf_lines = [
        "project = 'P'",
        "author = 'A'",
        "release = '1.0'",
        "extensions = ['typsphinx']",
        "typst_documents = [('index', 'index', 'T', 'Entry Author')]",
        f"typst_authors = {{{SEED_NAME!r}: {{'organization': 'MIT'}}}}",
        "typst_template_mapping = {'project': 'title'}",
    ]
    if with_template_function:
        conf_lines.append(
            "typst_template_function = {"
            "'name': 'project', "
            f"'params': {{'authors': ({TEMPLATE_FUNCTION_AUTHOR!r},)}}"
            "}"
        )
    (srcdir / "conf.py").write_text("\n".join(conf_lines) + "\n")


def _run_sphinx_build_typst(srcdir: Path, outdir: Path) -> subprocess.CompletedProcess:
    """Run ``sphinx-build -b typst`` as a subprocess via ``sys.executable
    -m sphinx`` -- never a ``["uv", "run", "sphinx-build", ...]`` form.
    This project's documented PATH-shadowing hazard makes that form fail
    environmentally (returncode 127) even when the same command succeeds
    in a plain shell, and under worktree isolation the interpreter running
    THIS test process is the one whose editable ``typsphinx`` install must
    be exercised -- ``sys.executable`` guarantees that; a resolved ``uv``/
    ``sphinx-build`` binary on PATH does not."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(srcdir), str(outdir)],
        capture_output=True,
        text=True,
    )


def test_three_knob_build_emits_template_function_authors_not_the_seed(tmp_path):
    """The exact configuration ``44.2-VERIFICATION.md`` reproduced with a
    real ``sphinx-build``: no published sentence had a falsification
    attempt against this row for three rounds. ``typst_authors`` is set,
    the mapping targets only ``title`` (the seed survives stage 1), and
    ``typst_template_function``'s dict-form ``params["authors"]`` replaces
    it at stage 2 (``render()``)."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()
    _write_three_knob_project(srcdir, with_template_function=True)

    outdir = tmp_path / "build"
    result = _run_sphinx_build_typst(srcdir, outdir)

    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    emitted = (outdir / "index.typ").read_text(encoding="utf-8")
    assert TEMPLATE_FUNCTION_AUTHOR in emitted
    assert SEED_NAME not in emitted


def test_three_knob_control_build_without_template_function_emits_the_seed(
    tmp_path,
):
    """The attribution control: byte-identical to the gate above except
    ``typst_template_function`` is absent. Without this control the first
    test could pass because the MAPPING ate the seed rather than the
    render stage replacing it; with it, the difference between the two
    builds is attributable to the render stage's ``typst_template_params``
    merge alone, and to nothing in the mapping."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()
    _write_three_knob_project(srcdir, with_template_function=False)

    outdir = tmp_path / "build"
    result = _run_sphinx_build_typst(srcdir, outdir)

    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    emitted = (outdir / "index.typ").read_text(encoding="utf-8")
    assert SEED_NAME in emitted
    assert TEMPLATE_FUNCTION_AUTHOR not in emitted


def _module_ast(path: Path) -> ast.Module:
    """Parse `path` and return its `Module` node."""
    return ast.parse(path.read_text(encoding="utf-8"))


def _function_def(path: Path, name: str) -> ast.FunctionDef:
    """Return the `FunctionDef` node named `name` in `path`, raising a
    named `AssertionError` -- never returning `None` -- if it is absent."""
    for node in ast.walk(_module_ast(path)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name}() not found in {path}")


class _StageSiteVisitor(ast.NodeVisitor):
    """Tracks the ENCLOSING `FunctionDef` for every node via an explicit
    stack (never `ast.walk()`'s flat, parent-less traversal, which cannot
    answer "which function is this node inside"). Collects, in visitation
    (source) order, every `Assign` whose target is a `Subscript` on a
    `Name` in `PARAMS_CARRIERS`, and every `.update(...)` `Call` whose
    receiver is such a `Name`."""

    def __init__(self) -> None:
        self.func_stack: list[str] = []
        self.findings: list[tuple[str, str, str]] = []  # (func, kind, slice)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.func_stack.append(node.name)
        self.generic_visit(node)
        self.func_stack.pop()

    def visit_Assign(self, node: ast.Assign) -> None:
        if self.func_stack:
            func_name = self.func_stack[-1]
            for target in node.targets:
                if not (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Name)
                    and target.value.id in PARAMS_CARRIERS
                ):
                    continue
                slice_node = target.slice
                if isinstance(slice_node, ast.Constant) and isinstance(
                    slice_node.value, str
                ):
                    slice_repr = slice_node.value
                elif isinstance(slice_node, ast.Name):
                    slice_repr = slice_node.id
                else:
                    slice_repr = ast.unparse(slice_node)
                self.findings.append((func_name, "assign", slice_repr))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self.func_stack:
            func_name = self.func_stack[-1]
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "update"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in PARAMS_CARRIERS
                and node.args
            ):
                arg_repr = ast.unparse(node.args[0])
                self.findings.append((func_name, "update", arg_repr))
        self.generic_visit(node)


def _stage_sites() -> list[str]:
    """Walk BOTH `TEMPLATE_ENGINE_PATH` and `WRITER_PATH`, tracking the
    enclosing `FunctionDef` for each node, and return a SORTED list of id
    strings -- one per AST node found, duplicates preserved (so two
    `Assign` nodes sharing a literal target produce two list entries).

    Id format: `<relpath>::<enclosing function>::<assign|update>::<literal
    slice, dynamic Name id, or unparsed first argument>`. When the same
    base id recurs within one function -- `map_parameters()`'s seed and
    back-fill both target the literal "authors" -- the second and later
    occurrences (in source order) get a `#<n>` ordinal suffix, matching
    the frozen `EXPECTED_STAGE_SITES` declaration above."""
    ids: list[str] = []
    for path in (TEMPLATE_ENGINE_PATH, WRITER_PATH):
        relpath = path.relative_to(REPO_ROOT).as_posix()
        visitor = _StageSiteVisitor()
        visitor.visit(_module_ast(path))
        counts: dict[str, int] = {}
        for func_name, kind, slice_repr in visitor.findings:
            base = f"{relpath}::{func_name}::{kind}::{slice_repr}"
            counts[base] = counts.get(base, 0) + 1
            ids.append(base if counts[base] == 1 else f"{base}#{counts[base]}")
    return sorted(ids)


def _author_information_section() -> str:
    """Read `CONFIGURATION_RST_PATH`, slice from the ``Author
    Information`` dash-underlined section title to the next dash-
    underlined section title at the same level (``Paper Size and
    Format``), and return the slice with whitespace collapsed to single
    spaces -- so a re-wrap of the paragraph cannot fool the knob-presence
    gate below."""
    lines = CONFIGURATION_RST_PATH.read_text(encoding="utf-8").splitlines()

    section_starts = [
        i
        for i in range(len(lines) - 1)
        if lines[i].strip()
        and lines[i + 1].strip()
        and set(lines[i + 1].strip()) == {"-"}
        and len(lines[i + 1].strip()) >= len(lines[i].strip())
    ]
    titles = [lines[i].strip() for i in section_starts]

    assert "Author Information" in titles, (
        "'Author Information' dash-underlined section title not found in "
        "configuration.rst"
    )
    idx = titles.index("Author Information")
    start = section_starts[idx]
    end = section_starts[idx + 1] if idx + 1 < len(section_starts) else len(lines)

    return re.sub(r"\s+", " ", "\n".join(lines[start:end]))


def test_pipeline_stage_sites_that_can_determine_authors_are_exactly_these():
    """AST-walks `typsphinx/template_engine.py` and `typsphinx/writer.py`
    for every write site on `PARAMS_CARRIERS` and compares the result
    against a frozen, hand-declared expectation -- never the reverse.

    This is the sole authority `REACHABLE_STAGE_KNOBS`,
    `UNREACHABLE_STAGE_PROOFS`, the D-05 comment in
    `typsphinx/template_engine.py`, and the published two-stage rule in
    `docs/source/user_guide/configuration.rst` must all be re-derived
    from -- not the reverse. It also stands as the PROOF for the three
    UNREACHABLE stage sites whose id's own literal target differs from
    "authors" (`assign::title`, `assign::date`, `assign::key`): a site
    whose slice is not the string "authors" cannot, by construction, be
    the assignment that writes `params["authors"]`."""
    consequence = (
        "A pipeline stage that can determine the emitted authors was "
        "added, removed, or moved. Before changing this expectation, "
        "re-derive: the published two-stage rule in "
        "docs/source/user_guide/configuration.rst, the D-05 comment in "
        "typsphinx/template_engine.py, and REACHABLE_STAGE_KNOBS / "
        "UNREACHABLE_STAGE_PROOFS above. Round 3's per-sentence "
        "enumeration missed exactly this class of writer because its "
        "frame was one function (map_parameters()) rather than the whole "
        "pipeline."
    )
    assert sorted(_stage_sites()) == sorted(EXPECTED_STAGE_SITES), consequence


def test_reachable_and_unreachable_stages_partition_the_enumeration():
    """`REACHABLE_STAGE_KNOBS` and `UNREACHABLE_STAGE_PROOFS` together
    must cover `EXPECTED_STAGE_SITES` exactly, with no overlap -- no
    enumerated site may be silently dropped from both classes, and none
    may be claimed by both. Every `UNREACHABLE_STAGE_PROOFS` value must
    name a function that actually exists at module level in this file."""
    expected = set(EXPECTED_STAGE_SITES)
    reachable = set(REACHABLE_STAGE_KNOBS)
    unreachable = set(UNREACHABLE_STAGE_PROOFS)

    unclassified = expected - (reachable | unreachable)
    over_classified = (reachable | unreachable) - expected
    assert not unclassified and not over_classified, (
        f"partition mismatch -- enumerated but unclassified: "
        f"{sorted(unclassified)}; classified but not enumerated: "
        f"{sorted(over_classified)}"
    )

    overlap = reachable & unreachable
    assert not overlap, (
        f"stage sites classified as BOTH reachable and "
        f"unreachable-with-proof: {sorted(overlap)}"
    )

    for site_id, proof_name in UNREACHABLE_STAGE_PROOFS.items():
        assert proof_name in globals() and callable(globals()[proof_name]), (
            f"UNREACHABLE_STAGE_PROOFS[{site_id!r}] names {proof_name!r}, "
            "which is not a module-level function in this file"
        )


def test_toctree_options_cannot_reach_authors_or_title():
    """`writer.py` calls `params.update(toctree_options)` between
    `map_parameters()` and `render()` -- a REAL `params` writer in the
    pipeline, not a hypothetical one. It is excluded from REACHABLE by
    PROOF of its returned key set, not by assumption: statically, every
    `Dict` literal `extract_toctree_options()` can return has exactly the
    keys `toctree_maxdepth`/`toctree_numbered`/`toctree_caption`; and
    dynamically, a doctree carrying no toctree node returns `{}`."""
    func = _function_def(TEMPLATE_ENGINE_PATH, "extract_toctree_options")
    literal_keys: set[str] = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            for key_node in node.value.keys:
                assert isinstance(key_node, ast.Constant) and isinstance(
                    key_node.value, str
                ), "extract_toctree_options() returns a Dict with a non-literal-str key"
                literal_keys.add(key_node.value)

    assert literal_keys == {"toctree_maxdepth", "toctree_numbered", "toctree_caption"}
    assert "authors" not in literal_keys
    assert "title" not in literal_keys

    from docutils import nodes
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    reporter = Reporter("", 2, 4)
    doctree = nodes.document("", reporter=reporter)
    doctree.settings = states.Struct()
    doctree += nodes.section()

    engine = TemplateEngine()
    assert engine.extract_toctree_options(doctree) == {}


def test_render_applies_template_function_params_after_map_parameters_output():
    """Phase 45.1 (D-B) re-derivation: this test used to pin the ORDER of
    `render()`'s two `all_params.update(...)` calls -- the mechanism D-04
    rested on ("needs no new code"). D-B replaced that additive-union merge
    with a single boolean-guarded EXCLUSIVE branch, so there is no longer an
    order to pin; there is one assignment, not two updates. This test now
    pins the STRUCTURE of that exclusive branch instead: `render()` must
    contain exactly one `if self.typst_template_params_specified:` whose
    `then`-branch assigns `all_params` from `self.typst_template_params`
    (the declared set) and whose `else`-branch assigns `all_params` from
    `params` (the auto-derived set) -- the same "whole-strategy switch, not
    a per-key override" shape D-05 already established for
    `map_parameters()`'s `if not self.typst_package:` gate. If this branch
    were ever removed or the two arms transposed, D-B's published rule
    would invert or vanish silently -- no other behavioural test in the
    suite names the branch structure itself, only its externally observable
    effect."""
    func = _function_def(TEMPLATE_ENGINE_PATH, "render")

    def _is_all_params_dict_assign(node: ast.stmt, source_name: str) -> bool:
        return (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "all_params"
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "dict"
            and len(node.value.args) == 1
            and ast.unparse(node.value.args[0]) == source_name
        )

    matching_ifs = [
        node
        for node in ast.walk(func)
        if isinstance(node, ast.If)
        and ast.unparse(node.test) == "self.typst_template_params_specified"
    ]
    assert len(matching_ifs) == 1, (
        f"Expected exactly one `if self.typst_template_params_specified:` "
        f"branch in render(), found {len(matching_ifs)}"
    )
    branch = matching_ifs[0]

    assert len(branch.body) == 1 and _is_all_params_dict_assign(
        branch.body[0], "self.typst_template_params"
    ), "The `if` branch must assign `all_params = dict(self.typst_template_params)`"
    assert len(branch.orelse) == 1 and _is_all_params_dict_assign(
        branch.orelse[0], "params"
    ), "The `else` branch must assign `all_params = dict(params)`"


def test_authors_section_names_every_stage_knob_that_can_write_authors():
    """Every REACHABLE stage's user-facing config knob must be named in
    the Author Information section a user configures against -- a stage
    the code can reach but the prose never names is undocumented
    behaviour. A PRESENCE assertion only (FA-03): it cannot prove the
    surrounding English is accurate, only that a reachable knob is not
    silently missing."""
    section = _author_information_section()
    for site_id, knob in REACHABLE_STAGE_KNOBS.items():
        assert knob in section, (
            f"{knob!r} (controls {site_id}) is not named in the Author "
            "Information section of configuration.rst -- a stage the "
            "code can reach must be named in the section a user "
            "configures against."
        )


def test_configuration_rst_stage1_bullets_name_stage2_override_explicitly():
    """Drift guard for a round-4 residual fix (44.2-GATE-EVIDENCE-06.md
    §4, S-14/S-16): the two Precedence-block bullets illustrating a
    mapping that does NOT target ``authors`` -- ``{"author":
    "doc_authors"}`` and ``{"project": "authors"}`` -- describe what
    Stage 1's OWN output contains, not the final rendered document. The
    ORIGINAL wording ("Both values are then passed" / "What lands in
    authors is then...") was graded NARROWER-THAN-CODE against a real
    render()-stage override (``typst_template_function``'s
    ``params["authors"]``) because it read as an unscoped claim about the
    final output. The fix names the Stage 1 scope explicitly and
    cross-references Stage 2's override; this guard fails if that
    cross-reference is ever silently dropped, reintroducing the same
    unscoped-claim shape that produced four rounds of failure."""
    text = CONFIGURATION_RST_PATH.read_text(encoding="utf-8")
    normalized = re.sub(r"\s+", " ", text)

    for needle in (
        "Stage 1's own output then carries both",
        "subject to stage 2's override above",
        "Stage 1's own output for ``authors`` is then the project name",
        "again subject to stage 2's override",
    ):
        assert needle in normalized, f"MISSING from configuration.rst: {needle}"

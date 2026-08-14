"""
Phase 49 plan 05, Task 1 -- the COMP-11 removal gate and the assumption-
delta contract test (COMP-05, COMP-06, COMP-11, SC#4).

COMP-11 is a removal requirement: the build-scoped include-dedup ledger
attribute (declared in ``TypstBuilder.init()``, read once from
``visit_toctree``, written once from the same visitor, reset once per
``write()``) is gone. A removal asserted only once in a passing
``49-04-SUMMARY.md`` regresses silently the first time a future change
reaches for a convenient global ledger again -- and this phase's whole
subject is a class of failure (a shared content file silently dropping a
master's own child) that produces NO diagnostic at any layer. This module
turns that removal claim, SC#4's repo-wide-grep obligation, and the
assumption-delta checkpoint's own contract test into a COMMITTED,
falsifiable gate.

Structural vs. behavioural assertions, named explicitly per this plan's
own action text:

- STRUCTURAL (reads the production package's own source text via ``ast``,
  never a build): ``TestLedgerRemovalFromProductionPackage``,
  ``TestLedgerRemovalFromRepositoryProse``,
  ``TestToctreeVisitorEmitsNoUnconditionalInclude``,
  ``TestExactlyOneStateKeySpelling``. A structural assertion over source
  text can be defeated by a refactor that relocates the emission
  elsewhere -- which is exactly why each one is paired with a
  behavioural counterpart wherever a behavioural form exists.
- BEHAVIOURAL (reads a real build's emitted output, or the builder's own
  runtime mapping): ``TestExactlyOnePublicationPerWrapper``,
  ``TestAssumptionDeltaContract``.

Every expected value below substitutes into
``49-EXPECTED-STRUCTURE.md``'s ``## Emission contract``, applied to this
plan's own fixtures (``state_guard_two_master_gate``,
``state_guard_three_master_gate``, both built in 49-02/49-03) -- never
re-derived from this plan's own emitter output (ROADMAP binding
constraint #6).
"""

import ast
import inspect
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Dict, Iterator, Set

import pytest
from sphinx.testing.util import SphinxTestApp

from typsphinx.translator import INCLUDE_STATE_KEY, TypstTranslator

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCTION_PACKAGE_ROOT = REPO_ROOT / "typsphinx"

# Repo-wide sweep roots, per SC#4 / ROADMAP milestone invariant #4: an
# "anywhere under X" claim is checked over the WHOLE tree -- production
# package, tests (which covers tests/fixtures/ as a subtree), docs source
# and examples -- never scoped to only the files a requirement happens to
# name. ``.planning/`` is DELIBERATELY EXCLUDED: its own history
# legitimately records the deleted symbol (e.g. this phase's own
# ``49-04-SUMMARY.md``, ``49-01-PLAN.md``'s "Symbols this phase DELETES"
# section) and is not itself shippable source, prose or fixture content.
REPO_WIDE_SCAN_ROOTS = (
    PRODUCTION_PACKAGE_ROOT,
    REPO_ROOT / "tests",
    REPO_ROOT / "docs",
    REPO_ROOT / "examples",
)

# Text-file suffixes the repo-wide prose sweep reads (source, markup and
# generated-artifact prose) -- binary assets (images, PDFs) are never
# opened as text.
_TEXT_FILE_SUFFIXES = {".py", ".rst", ".md", ".txt", ".typ", ".cfg", ".toml"}

# The ONE deleted symbol COMP-11 requires be gone from the production
# package and from the repository's own non-planning prose -- named here
# as a single module-level constant, with this comment stating it is the
# deleted symbol, so this test module's own TEXT is the only place the
# literal spelling appears (every other reference in this module goes
# through this constant).
DELETED_LEDGER_ATTRIBUTE = "_included_docnames"

# This test module's OWN file -- excluded from the repo-wide prose sweep
# below, since this module's own text is, by the constant's own comment
# above, the deliberate single place the deleted symbol's literal
# spelling appears (inside DELETED_LEDGER_ATTRIBUTE's own assignment and
# this module's own docstrings/comments narrating it).
THIS_FILE = Path(__file__).resolve()

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TWO_MASTER_DIR = FIXTURES_DIR / "state_guard_two_master_gate"
THREE_MASTER_DIR = FIXTURES_DIR / "state_guard_three_master_gate"


# ---------------------------------------------------------------------------
# Shared walking/collection helpers -- implemented in Python, never by
# shelling out to a text-search command-line tool, so this module is
# portable to the Windows CI lanes.
# ---------------------------------------------------------------------------


def _iter_python_files(root: Path) -> Iterator[Path]:
    """Yield every ``*.py`` file under ``root``, sorted for deterministic
    failure messages. Yields nothing for a root that does not exist."""
    if not root.exists():
        return
    yield from sorted(root.rglob("*.py"))


def _iter_text_files(root: Path) -> Iterator[Path]:
    """Yield every file under ``root`` whose suffix is a known text
    format (see ``_TEXT_FILE_SUFFIXES``), sorted for deterministic
    failure messages."""
    if not root.exists():
        return
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in _TEXT_FILE_SUFFIXES:
            yield path


def _word_boundary_pattern(name: str) -> "re.Pattern[str]":
    """A word-boundary-anchored pattern for ``name`` -- excludes a
    DIFFERENT symbol, already deleted in Phase 48, that MERELY ENDS in
    the same suffix and would also match a naive substring search
    (49-04-SUMMARY.md's own recorded false-positive lesson)."""
    return re.compile(r"\b" + re.escape(name) + r"\b")


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run
    sphinx-build``, never a resolved ``sphinx-build`` binary) so the exact
    interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard and guaranteeing the
    worktree's own editable ``typsphinx`` copy is what compiles the
    fixtures -- mirrors ``tests/test_pdf_render_gate.py`` and
    ``tests/test_master_include_set_predicate_gate.py``'s own helper of
    the same name.
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


# ---------------------------------------------------------------------------
# 1. The ledger is absent from the production package -- COMP-11
# ---------------------------------------------------------------------------


class TestLedgerRemovalFromProductionPackage:
    """COMP-11: the deleted build-scoped include-dedup ledger attribute is
    gone from the production package's own source. STRUCTURAL."""

    def test_ledger_absent_from_production_package(self):
        """COMP-11: walking every ``*.py`` file under ``typsphinx/`` finds
        zero occurrences of the deleted ledger attribute's name, word-
        boundary matched."""
        pattern = _word_boundary_pattern(DELETED_LEDGER_ATTRIBUTE)
        offending = []
        for path in _iter_python_files(PRODUCTION_PACKAGE_ROOT):
            text = path.read_text(encoding="utf-8")
            if pattern.search(text):
                offending.append(str(path.relative_to(REPO_ROOT)))
        assert not offending, (
            f"COMP-11: expected zero occurrences of the deleted ledger "
            f"attribute {DELETED_LEDGER_ATTRIBUTE!r} anywhere under "
            f"typsphinx/, found it in: {offending}"
        )


# ---------------------------------------------------------------------------
# 2. The ledger is absent from the repository's own prose -- COMP-11/SC#4
# ---------------------------------------------------------------------------


class TestLedgerRemovalFromRepositoryProse:
    """SC#4 / ROADMAP milestone invariant #4: the same absence, checked
    REPO-WIDE -- production package, tests (including tests/fixtures/),
    docs source and examples -- never scoped to only the files a
    requirement happens to name. STRUCTURAL. The ``.planning/`` directory
    is EXPLICITLY EXCLUDED (see the module-level comment above
    ``REPO_WIDE_SCAN_ROOTS``): its own history legitimately records the
    deleted symbol."""

    def test_ledger_absent_from_repo_wide_prose(self):
        """SC#4: the repo-wide sweep -- typsphinx/, tests/, docs/,
        examples/ -- finds zero occurrences of the deleted ledger
        attribute's name; ``.planning/`` is excluded, not silently
        omitted."""
        pattern = _word_boundary_pattern(DELETED_LEDGER_ATTRIBUTE)
        offending = []
        for scan_root in REPO_WIDE_SCAN_ROOTS:
            for path in _iter_text_files(scan_root):
                if path.resolve() == THIS_FILE:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if pattern.search(text):
                    offending.append(str(path.relative_to(REPO_ROOT)))
        assert not offending, (
            f"SC#4: expected zero occurrences of the deleted ledger "
            f"attribute {DELETED_LEDGER_ATTRIBUTE!r} anywhere under "
            f"typsphinx/, tests/, docs/ or examples/ (.planning/ is "
            f"deliberately excluded -- see this module's own comment), "
            f"found it in: {offending}"
        )


# ---------------------------------------------------------------------------
# 3. The toctree visitor emits no unconditional include -- COMP-11
# ---------------------------------------------------------------------------


def _visitor_source_dedented() -> str:
    """``inspect.getsource()`` for ``TypstTranslator.visit_toctree``,
    dedented so it parses as a standalone module via ``ast.parse()``."""
    return textwrap.dedent(inspect.getsource(TypstTranslator.visit_toctree))


def _visitor_docstring_line_range() -> "tuple[int, int] | None":
    """The (1-based, inclusive) line range of ``visit_toctree``'s own
    docstring within ``_visitor_source_dedented()``'s text -- ``None`` if
    the function carries no docstring. Used to exclude the docstring's
    own prose (which legitimately narrates ``#include()`` as an example)
    from the structural include-call scan below."""
    tree = ast.parse(_visitor_source_dedented())
    func_node = tree.body[0]
    assert isinstance(func_node, ast.FunctionDef)
    if (
        func_node.body
        and isinstance(func_node.body[0], ast.Expr)
        and isinstance(func_node.body[0].value, ast.Constant)
        and isinstance(func_node.body[0].value.value, str)
    ):
        doc_node = func_node.body[0]
        return (doc_node.lineno, doc_node.end_lineno)
    return None


class TestToctreeVisitorEmitsNoUnconditionalInclude:
    """COMP-11: the toctree visitor's own emission loop routes every
    include call through the shared guard-rendering function
    (``render_include_guard()``) or the surviving relative-path helper
    (``_compute_relative_include_path()``) -- never a raw, unconditional
    ``include(...)`` construction, and never a membership test against a
    builder attribute (the shape of the deleted dedup read). STRUCTURAL."""

    def test_every_include_bearing_code_line_routes_through_the_guard_helpers(
        self,
    ):
        """COMP-11: every non-comment, non-docstring line inside
        ``visit_toctree`` that contains an ``include(`` call is produced
        through ``render_include_guard()`` or
        ``_compute_relative_include_path()`` -- the docstring's own
        narrative uses of ``#include()`` (e.g. "Generate Typst
        #include() directives") are excluded, since they describe the
        mechanism rather than emit anything."""
        source = _visitor_source_dedented()
        docstring_range = _visitor_docstring_line_range()
        include_call_pattern = re.compile(r"\binclude\s*\(")
        sanctioned = ("render_include_guard(", "_compute_relative_include_path(")

        offending = []
        for lineno, line in enumerate(source.splitlines(), start=1):
            if docstring_range and docstring_range[0] <= lineno <= docstring_range[1]:
                continue
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if include_call_pattern.search(stripped) and not any(
                name in stripped for name in sanctioned
            ):
                offending.append((lineno, line))

        assert not offending, (
            f"COMP-11: found a raw include(...) call inside "
            f"visit_toctree not routed through render_include_guard()/"
            f"_compute_relative_include_path(): {offending}"
        )

    def test_visitor_genuinely_calls_the_shared_guard_rendering_function(self):
        """COMP-11: the positive companion to the assertion above -- the
        visitor's own body DOES call ``render_include_guard()`` at least
        once, confirming the prior test is not vacuously passing because
        the visitor emits no include-bearing text at all."""
        source = _visitor_source_dedented()
        assert "render_include_guard(" in source, (
            "expected visit_toctree's own body to call "
            "render_include_guard() -- the shared guard-rendering "
            "function this phase's emission contract requires"
        )

    def test_visitor_contains_no_membership_test_against_a_builder_attribute(
        self,
    ):
        """COMP-11: the shape of the deleted dedup read (``docname in
        self.builder.<attr>`` / ``self.builder.<attr>.add(docname)``) is
        structurally absent from ``visit_toctree``'s own body -- the
        include DECISION no longer resolves via a builder-side membership
        check at write time."""
        source = _visitor_source_dedented()
        membership_pattern = re.compile(r"in\s+self\.builder\.\w+")
        assert not membership_pattern.search(source), (
            "COMP-11: found a membership test against a builder "
            "attribute inside visit_toctree -- this is the deleted "
            "dedup ledger's own write-time read shape"
        )


# ---------------------------------------------------------------------------
# 4. Exactly one state-key spelling exists -- COMP-06/D-07
# ---------------------------------------------------------------------------

_STATE_CALL_PATTERN = re.compile(r'state\(\s*"((?:[^"\\]|\\.)*)"')


def _reconstruct_fstring_shape(node: ast.JoinedStr) -> str:
    """Reconstruct an f-string AST node's own SOURCE SHAPE -- literal
    fragments verbatim, each interpolation rendered as ``{<expr>}`` --
    so a regex can be applied to it the same way it would to a plain
    string literal."""
    parts = []
    for value in node.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            parts.append(value.value)
        elif isinstance(value, ast.FormattedValue):
            parts.append("{" + ast.unparse(value.value) + "}")
    return "".join(parts)


def _collect_docstring_constant_ids(tree: ast.AST) -> Set[int]:
    """Return the ``id()`` of every AST ``Constant`` node that IS a
    module/class/function docstring (its containing body's own first
    statement, a bare string expression) -- so a docstring's own worked
    example (e.g. ``render_include_edge_state()``'s ``Returns:`` section)
    is excluded from the state-call literal collection below, which is
    about genuine emission SITES, not documentation."""
    ids: Set[int] = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr):
                value = body[0].value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    ids.add(id(value))
    return ids


def _module_level_string_constants(tree: ast.Module) -> Dict[str, str]:
    """Collect every module-level ``NAME = "literal"`` / ``NAME: T =
    "literal"`` assignment's own resolved string value, keyed by name --
    used to resolve a ``{NAME}`` f-string interpolation captured inside a
    ``state(...)`` call site back to its own literal value."""
    constants: Dict[str, str] = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = node.value.value
        elif (
            isinstance(node, ast.AnnAssign)
            and node.value is not None
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and isinstance(node.target, ast.Name)
        ):
            constants[node.target.id] = node.value.value
    return constants


def _collect_state_call_first_arg_literals(root: Path) -> Set[str]:
    """Collect every DISTINCT resolved literal string passed as the
    first argument to a Typst ``state(...)`` call, across every ``.py``
    file under ``root`` -- collected STRUCTURALLY via ``ast``, not
    assumed absent beyond one known spelling (the module's own
    acceptance criteria requires this, not a bare occurrence count of
    one known string).

    Comments are never part of the AST (excluded for free); each file's
    own module/class/function DOCSTRING is explicitly excluded (see
    ``_collect_docstring_constant_ids``) -- a second spelling would be
    detected here, not assumed absent."""
    literals: Set[str] = set()
    for path in _iter_python_files(root):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        docstring_ids = _collect_docstring_constant_ids(tree)
        module_constants = _module_level_string_constants(tree)
        for node in ast.walk(tree):
            shape = None
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if id(node) in docstring_ids:
                    continue
                shape = node.value
            elif isinstance(node, ast.JoinedStr):
                shape = _reconstruct_fstring_shape(node)
            if shape is None:
                continue
            for match in _STATE_CALL_PATTERN.finditer(shape):
                captured = match.group(1)
                identifier_match = re.fullmatch(r"\{(\w+)\}", captured)
                if identifier_match:
                    identifier = identifier_match.group(1)
                    literals.add(module_constants.get(identifier, captured))
                else:
                    literals.add(captured)
    return literals


class TestExactlyOneStateKeySpelling:
    """COMP-06/D-07: exactly one spelling of the namespaced Typst
    ``state`` key exists in the production package -- collected
    STRUCTURALLY by walking every genuine ``state(...)`` call site's
    first argument, not by counting occurrences of one known string.
    STRUCTURAL. A second spelling anywhere is exactly the drift class
    D-07's namespacing decision exists to reject."""

    def test_production_package_contains_the_contract_state_key(self):
        """D-07: the production package's own ``state(...)`` call sites
        collectively contain the contract's own state key,
        ``INCLUDE_STATE_KEY``."""
        literals = _collect_state_call_first_arg_literals(PRODUCTION_PACKAGE_ROOT)
        assert INCLUDE_STATE_KEY in literals, (
            f"D-07: expected the contract's own state key "
            f"{INCLUDE_STATE_KEY!r} among the collected state(...) call "
            f"literals, found: {literals}"
        )

    def test_exactly_one_distinct_state_key_literal_exists(self):
        """COMP-06: the total number of DISTINCT string literals passed
        as the first argument to a Typst ``state(...)`` call, across the
        whole production package, is exactly one -- a second spelling
        anywhere is detected here, not assumed absent."""
        literals = _collect_state_call_first_arg_literals(PRODUCTION_PACKAGE_ROOT)
        assert len(literals) == 1, (
            f"COMP-06: expected exactly one distinct state-key literal "
            f"in the production package, found {len(literals)}: "
            f"{literals}"
        )


# ---------------------------------------------------------------------------
# 5. Exactly one publication line per wrapper -- COMP-06. BEHAVIOURAL.
# ---------------------------------------------------------------------------

_PUBLICATION_LINE_PATTERN = re.compile(
    r'^#state\("' + re.escape(INCLUDE_STATE_KEY) + r'", \(\)\)\.update\(.*\)$'
)
_INCLUDE_LINE_PREFIX = "#include("

# The three-master fixture's own typst_documents targets
# (tests/fixtures/state_guard_three_master_gate/conf.py, read literally --
# never re-derived from a build) -- three wrappers, so this is not merely
# a two-master coincidence (49-EXPECTED-STRUCTURE.md fixture spec entry 8,
# SC#2's "not 2-master-specific" coverage obligation).
_THREE_MASTER_WRAPPER_NAMES = ("manual1.typ", "manual2.typ", "manual3.typ")


@pytest.mark.skipif(
    not TYPST_AVAILABLE, reason="typst-py is required to build the fixture"
)
class TestExactlyOnePublicationPerWrapper:
    """COMP-06: every emitted wrapper carries EXACTLY one state
    publication line, immediately followed by that wrapper's own content
    ``#include(...)`` line, with nothing between them -- the Emission
    contract's ``## The wrapper body shape`` template, checked against a
    real ``-b typst`` build of the three-master fixture. BEHAVIOURAL."""

    def test_each_wrapper_publishes_once_immediately_before_its_include(self, tmp_path):
        """COMP-06: for each of the three-master fixture's three
        wrappers, exactly one state publication line exists, and it is
        immediately followed (no intervening line) by that wrapper's own
        content ``#include(...)`` line -- the emitted wrapper-body shape
        this phase's whole mechanism depends on."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build_typst(THREE_MASTER_DIR, build_dir)
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        for wrapper_name in _THREE_MASTER_WRAPPER_NAMES:
            wrapper_path = build_dir / wrapper_name
            assert wrapper_path.exists(), f"{wrapper_name} was not emitted"
            text = wrapper_path.read_text(encoding="utf-8")
            lines = text.splitlines()

            publication_indices = [
                i
                for i, line in enumerate(lines)
                if _PUBLICATION_LINE_PATTERN.match(line)
            ]
            include_indices = [
                i
                for i, line in enumerate(lines)
                if line.startswith(_INCLUDE_LINE_PREFIX)
            ]

            assert len(publication_indices) == 1, (
                f"{wrapper_name}: expected exactly one state publication "
                f"line, found {len(publication_indices)}:\n{text}"
            )
            assert len(include_indices) == 1, (
                f"{wrapper_name}: expected exactly one content "
                f"#include(...) line, found {len(include_indices)}:\n"
                f"{text}"
            )
            assert publication_indices[0] + 1 == include_indices[0], (
                f"{wrapper_name}: expected the publication line "
                f"immediately followed by the #include(...) line with "
                f"nothing between them (publication at physical line "
                f"{publication_indices[0]}, include at "
                f"{include_indices[0]}):\n{text}"
            )


# ---------------------------------------------------------------------------
# 6/7. The assumption-delta contract test, plus non-mutation during
# writing -- COMP-05/COMP-06. BEHAVIOURAL.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not TYPST_AVAILABLE, reason="typst-py is required to build the fixture"
)
class TestAssumptionDeltaContract:
    """The assumption-delta contract test the checkpoint after 49-04's
    own tracer required: the builder's include mapping is keyed by
    MASTER DOCNAME, and for the two-master fixture it carries at least
    two keys whose values DIFFER.

    A FAILURE anywhere in this class means the per-master include graph
    has collapsed back to ONE GLOBAL include set -- the singular
    assumption this phase promoted away from, and the exact failure mode
    defect A (49-RED-EVIDENCE.md Failure mode 1) grew out of. This is
    what makes the promoted-plural identity FALSIFIABLE, not merely
    documented. BEHAVIOURAL."""

    def test_mapping_is_keyed_by_master_docname_with_differing_values(self, tmp_path):
        """COMP-05/COMP-06: ``_master_include_edges`` is keyed by master
        docname, carries at least two keys for the two-master fixture,
        and those two keys' values DIFFER -- and each value is a TUPLE
        of edge keys (never a bare docname), so no attribute on the
        builder holds a single flat set of docnames spanning masters."""
        outdir = tmp_path / "build"
        app = SphinxTestApp(buildername="typst", srcdir=TWO_MASTER_DIR, builddir=outdir)
        try:
            app.build()
            mapping = app.builder._master_include_edges

            assert "index" in mapping and "bmaster" in mapping, (
                f"expected the two-master fixture's own master docnames "
                f"('index', 'bmaster') as keys, got: {sorted(mapping)}"
            )
            assert len(mapping) >= 2, (
                f"expected at least two master keys for this fixture, "
                f"got {len(mapping)}: {sorted(mapping)}"
            )

            index_edges = mapping["index"]
            bmaster_edges = mapping["bmaster"]
            assert index_edges != bmaster_edges, (
                "A FAILURE HERE MEANS: the per-master include graph has "
                "collapsed back to one global include set -- the "
                "singular assumption this phase promoted away from, and "
                "the same failure mode defect A grew out of. The two "
                "masters' own edge sets must differ, because each "
                "master's DFS is independently seeded and walked with "
                "no cross-master coordination.\n"
                f"index: {index_edges}\nbmaster: {bmaster_edges}"
            )

            for master_docname, edges in mapping.items():
                assert isinstance(edges, tuple), (
                    f"expected {master_docname}'s own edge set to be a "
                    f"TUPLE of edge keys (never a single flat set of "
                    f"docnames spanning masters), got "
                    f"{type(edges).__name__}: {edges}"
                )
                for edge_key in edges:
                    assert (
                        isinstance(edge_key, str)
                        and "#" in edge_key
                        and ">" in edge_key
                    ), (
                        f"expected {master_docname}'s own edge set to "
                        f"hold EDGE KEYS (the "
                        f"<parent>#<occurrence>><child> format), not "
                        f"bare docnames -- got {edge_key!r}"
                    )

            assert not hasattr(app.builder, DELETED_LEDGER_ATTRIBUTE), (
                "expected no attribute on the builder holding a single "
                "flat set of docnames spanning masters (the deleted "
                "ledger's own shape)"
            )
        finally:
            app.cleanup()

    def test_mapping_unmutated_by_running_write_phase_again(self, tmp_path):
        """COMP-05/COMP-06: the mapping is DERIVED, never accumulated by
        mutation during writing -- the property the deleted ledger did
        NOT have (it was mutated INSIDE the toctree visitor while
        documents were being written). Re-running the write phase over
        every document a second time produces the SAME mapping."""
        outdir = tmp_path / "build"
        app = SphinxTestApp(buildername="typst", srcdir=TWO_MASTER_DIR, builddir=outdir)
        try:
            app.build()
            builder = app.builder
            snapshot = dict(builder._master_include_edges)

            builder.write(None, set(app.env.found_docs), method="all")

            assert builder._master_include_edges == snapshot, (
                "the per-master include-edge mapping changed after "
                "re-running the write phase over every document -- "
                "expected it unchanged, since the mapping is DERIVED, "
                "not accumulated by mutation during writing\n"
                f"before: {snapshot}\nafter: {builder._master_include_edges}"
            )
        finally:
            app.cleanup()

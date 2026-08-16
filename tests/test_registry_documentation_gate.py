"""
Phase 56 plan 01 (DOC-15/D-06): the two-way registry error-catalogue gate.

**What this locks.** ``docs/source/user_guide/configuration.rst``'s
"Per-Document Templates" subsection publishes a "When the Build Stops"
error catalogue describing every config-caused ``ExtensionError`` shape
``typsphinx/template_registry.py`` and ``typsphinx/builder.py`` can
raise for the ``typst_document_templates`` registry and its bundle
copy. This module pins that catalogue to the REAL shipped messages in
both directions: every clause the catalogue publishes must exist in the
code (docs -> code), and every registry/bundle ``ExtensionError`` shape
the code raises -- unless explicitly denylisted with a written reason --
must be published (code -> docs).

**Design constraint, copied from ``tests/test_docs_contract_claims_gate.py``
for the same stated reason.** Discovery of both the code side (every
``raise ExtensionError(...)`` call site under ``typsphinx/*.py``, found
by parsing with ``ast``) and the docs side (every multi-word
double-backtick inline literal inside the catalogue region, found with
``re``) is run-time text/AST scanning, never a hardcoded shape list.
This module imports no ``typst``, never spawns ``sphinx-build`` as a
child process, and reads only ``.py``/``.rst`` text -- so it never
skips, in any CI lane, ever.

**AST, not a per-line regex (D-06).** Two of the raise sites in
``typsphinx/*.py`` defeat a naive line-oriented scan: ``builder.py:2151``
raises through a shared helper function (``_conf17_violation_message()``),
so the leading clause is not an inline string literal at the raise site
itself and must be resolved by following one level of same-module call
indirection; and ``template_registry.py:422`` builds its message from
Python's implicit adjacent string-literal concatenation (two string
tokens, no ``+``), which CPython has already merged into one AST
``Constant``/``JoinedStr`` chunk by the time this module parses it -- the
scanner does not re-implement concatenation, it simply reads what
``ast.parse()`` already merged.

**The single-literal-chunk rule (D-05).** Every published fragment must
be found inside ONE literal chunk of a discovered message, never only
across a chunk boundary -- an aggregated ``{summary}`` body built at
RUNTIME from several messages joined together must never be mistaken for
a match. This is what stops a published fragment from silently drifting
to describe the wrong shape, or an aggregate body from being quoted
wholesale (forbidden by D-05).
"""

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TYPSPHINX_PKG_DIR = REPO_ROOT / "typsphinx"
CONFIGURATION_RST_PATH = (
    REPO_ROOT / "docs" / "source" / "user_guide" / "configuration.rst"
)

CATALOGUE_HEADING = "When the Build Stops"

# Phase 56 plan 01 (D-06): the three ExtensionError shapes that are
# deliberately OUT OF SCOPE for the registry/bundle catalogue above, with
# the measured reason each is excluded. Every key must still match a real
# discovered shape (TestErrorCatalogueAgreesWithCode's stale-exclusion
# check enforces this) -- an entry here is not a promise, it is a
# verified fact about the current source.
EXCLUDED_ERROR_SHAPES = {
    "master document(s) failed:": (
        "builder.py:2377 -- the typstpdf PDF-compile failure aggregate "
        "raised inside TypstPDFBuilder.finish(). This reports a Typst "
        "COMPILE failure, not a registry or bundle conf.py "
        "misconfiguration, so it does not belong in this catalogue."
    ),
    "typst_elements: unknown key": (
        "template_engine.py:567 -- CONF-04's typst_elements allowlist "
        "guard, already documented in this page's own typst_elements "
        "coverage (the 'Paper Size and Format' / 'Document Language' "
        "sections). Unrelated to the typst_document_templates registry."
    ),
    "the include chain for master document": (
        "translator.py:415 -- BLD-08's toctree include-chain depth "
        "bound. A toctree-structure abort, not a conf.py "
        "misconfiguration; the registry never participates in it."
    ),
}


class ErrorShape:
    """One discovered ``raise ExtensionError(...)`` call site: the module
    it lives in, its line number, and its ordered list of literal string
    chunks (see ``_decompose_chunks()``)."""

    __slots__ = ("module", "line", "chunks", "normalized")

    def __init__(self, module: str, line: int, chunks: list) -> None:
        self.module = module
        self.line = line
        self.chunks = chunks
        # A placeholder-joined form, carried on the record for readable
        # assertion messages only. Matching logic below NEVER checks a
        # published fragment against this joined string -- every match is
        # checked against ONE chunk at a time (the single-literal-chunk
        # rule, D-05), so a fragment that would only appear once chunks
        # are concatenated together can never be credited here.
        self.normalized = "".join(chunks)

    def __repr__(self) -> str:
        return f"ErrorShape({self.module}:{self.line})"


def _iter_source_modules() -> list:
    """Every ``*.py`` file directly under ``typsphinx/``, in sorted order
    -- run-time discovery, never a hardcoded file list."""
    return sorted(TYPSPHINX_PKG_DIR.glob("*.py"))


def _module_level_functions(tree: ast.Module) -> dict:
    return {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}


def _function_return_value(func_def: ast.FunctionDef, module_name: str):
    """The single ``ast.Return`` value inside ``func_def`` -- the only
    indirection level this scanner supports (D-06)."""
    returns = [
        node.value
        for node in ast.walk(func_def)
        if isinstance(node, ast.Return) and node.value is not None
    ]
    if len(returns) != 1:
        raise AssertionError(
            f"{module_name}: function {func_def.name!r}, called through "
            f"an ExtensionError argument, does not have exactly one "
            f"Return statement (found {len(returns)}) -- the call-through "
            f"resolver supports only a function with a single Return."
        )
    return returns[0]


def _decompose_chunks(
    node: ast.AST, functions_by_name: dict, module_name: str, lineno: int
) -> list:
    """Reduce an ``ExtensionError`` call's first argument to its ordered
    list of literal string chunks.

    Three shapes are handled: a bare string constant; an f-string
    (``ast.JoinedStr``), where each ``ast.Constant`` contributes one
    chunk and each ``ast.FormattedValue`` is a chunk boundary
    contributing none; and a call to a function defined at module scope
    in the SAME module, resolved by decomposing that function's own
    single ``Return`` value the same way (``builder.py:2151``'s call
    through ``_conf17_violation_message()``). Anything else is a test
    failure naming the file and line -- never a silent drop.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.JoinedStr):
        chunks = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                chunks.append(value.value)
            # ast.FormattedValue contributes no chunk -- interpolation
            # boundary.
        return chunks
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        func_name = node.func.id
        func_def = functions_by_name.get(func_name)
        if func_def is None:
            raise AssertionError(
                f"{module_name}:{lineno}: ExtensionError's argument calls "
                f"{func_name!r}, which is not defined at module scope in "
                f"the same module -- the scanner supports only one level "
                f"of same-module call-through indirection and must not "
                f"silently drop this shape."
            )
        return _decompose_chunks(
            _function_return_value(func_def, module_name),
            functions_by_name,
            module_name,
            lineno,
        )
    raise AssertionError(
        f"{module_name}:{lineno}: ExtensionError's argument is a "
        f"{type(node).__name__}, not a string constant, an f-string, or "
        f"a resolvable same-module function call -- the scanner does not "
        f"know how to decompose it into literal chunks."
    )


def _discover_error_shapes() -> list:
    """Every ``raise ExtensionError(...)`` call site under
    ``typsphinx/*.py``, discovered by parsing each module with ``ast`` --
    never a hardcoded shape list (milestone invariant #11)."""
    shapes = []
    for module_path in _iter_source_modules():
        text = module_path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(module_path))
        functions_by_name = _module_level_functions(tree)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "ExtensionError"
                and node.args
            ):
                chunks = _decompose_chunks(
                    node.args[0], functions_by_name, module_path.name, node.lineno
                )
                shapes.append(
                    ErrorShape(module=module_path.name, line=node.lineno, chunks=chunks)
                )
    return shapes


def _catalogue_region_text() -> str:
    """Every line of ``configuration.rst`` from the ``When the Build
    Stops`` heading (found by its title TEXT, never by line number) up
    to but excluding the next section-underline-only line."""
    text = CONFIGURATION_RST_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    heading_idx = None
    for i, line in enumerate(lines):
        if line.strip() == CATALOGUE_HEADING:
            heading_idx = i
            break
    if heading_idx is None:
        raise AssertionError(
            f"configuration.rst does not contain a {CATALOGUE_HEADING!r} " "heading."
        )
    underline_re = re.compile(r"^[=\-~^]+$")
    start = heading_idx + 2  # past the heading text and its own underline
    end = len(lines)
    for j in range(start, len(lines)):
        candidate = lines[j].strip()
        if candidate and underline_re.match(candidate):
            end = j
            break
    return "\n".join(lines[start:end])


def _published_fragments() -> list:
    """Every double-backtick inline literal inside the catalogue region
    that contains at least one space -- a multi-word literal is a QUOTE
    of a message the code raises; a single-token literal is a config or
    identifier name and is exempt."""
    region = _catalogue_region_text()
    fragments = re.findall(r"``([^`]+)``", region)
    return [fragment for fragment in fragments if " " in fragment]


# --------------------------------------------------------------------------
# Pure comparison helpers -- both the real assertions below and
# TestCatalogueGateHasTeeth's synthetic self-tests call these SAME
# functions, so a helper that stops detecting anything fails in both
# places at once.
# --------------------------------------------------------------------------


def _is_shape_excluded(shape: ErrorShape, excluded_fragments: dict) -> bool:
    return any(
        fragment in chunk for fragment in excluded_fragments for chunk in shape.chunks
    )


def _stale_exclusions(excluded_fragments: dict, shapes: list) -> list:
    """Excluded fragments that no longer match ANY discovered shape."""
    return [
        fragment
        for fragment in excluded_fragments
        if not any(fragment in chunk for shape in shapes for chunk in shape.chunks)
    ]


def _shape_is_covered(shape: ErrorShape, published_fragments: list) -> bool:
    return any(
        fragment in chunk for chunk in shape.chunks for fragment in published_fragments
    )


def _uncovered_shapes(
    shapes: list, published_fragments: list, excluded_fragments: dict
) -> list:
    """Code -> docs direction: discovered shapes that are neither
    excluded nor published anywhere in the catalogue."""
    return [
        shape
        for shape in shapes
        if not _is_shape_excluded(shape, excluded_fragments)
        and not _shape_is_covered(shape, published_fragments)
    ]


def _matching_shapes(fragment: str, shapes: list) -> list:
    """Every discovered shape with at least one chunk containing
    ``fragment`` (docs -> code direction)."""
    return [
        shape for shape in shapes if any(fragment in chunk for chunk in shape.chunks)
    ]


def _chunks_containing_fragment(fragment: str, chunks: list) -> list:
    """Indices of ``chunks`` that individually contain ``fragment`` --
    the single-literal-chunk rule (D-05) checks this is exactly one,
    never zero (spans a boundary) and never more than one."""
    return [index for index, chunk in enumerate(chunks) if fragment in chunk]


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


class TestErrorCatalogueAgreesWithCode:
    """D-06's two-way leading-clause gate: every published fragment
    matches the code, and every registry/bundle ExtensionError shape the
    code raises is published (unless denylisted with a written reason)."""

    def test_discovery_finds_at_least_ten_shapes(self):
        shapes = _discover_error_shapes()
        assert shapes, (
            "The AST scan discovered zero ExtensionError call sites -- a "
            "vacuous scan would let this guard pass without ever "
            "checking anything."
        )
        assert len(shapes) >= 10, (
            f"Discovered only {len(shapes)} ExtensionError call sites "
            f"under typsphinx/*.py; expected at least 10. Either the "
            f"scanner regressed, or a raise site was removed without "
            f"updating this floor."
        )

    def test_every_excluded_fragment_still_matches_a_discovered_shape(self):
        shapes = _discover_error_shapes()
        stale = _stale_exclusions(EXCLUDED_ERROR_SHAPES, shapes)
        assert not stale, (
            f"{stale} are in EXCLUDED_ERROR_SHAPES but no longer match "
            f"any discovered shape -- a stale exclusion. Remove them "
            f"from EXCLUDED_ERROR_SHAPES."
        )

    def test_code_to_docs_every_non_excluded_shape_is_published(self):
        shapes = _discover_error_shapes()
        published = _published_fragments()
        uncovered = _uncovered_shapes(shapes, published, EXCLUDED_ERROR_SHAPES)
        assert not uncovered, (
            f"{uncovered} raise ExtensionError with no matching published "
            f"fragment in configuration.rst's catalogue and no "
            f"EXCLUDED_ERROR_SHAPES entry -- either publish a fragment "
            f"for it or add a denylist entry with a reason."
        )

    def test_docs_to_code_every_fragment_matches_exactly_one_shape(self):
        shapes = _discover_error_shapes()
        published = _published_fragments()
        problems = [
            (fragment, len(_matching_shapes(fragment, shapes)))
            for fragment in published
            if len(_matching_shapes(fragment, shapes)) != 1
        ]
        assert not problems, (
            f"{problems} -- each published fragment must match exactly "
            f"one discovered ExtensionError shape (0 = invented or "
            f"stale, 2+ = ambiguous)."
        )

    def test_single_literal_chunk_rule(self):
        shapes = _discover_error_shapes()
        published = _published_fragments()
        problems = []
        for fragment in published:
            matches = _matching_shapes(fragment, shapes)
            if len(matches) != 1:
                continue  # reported by the uniqueness test above
            containing = _chunks_containing_fragment(fragment, matches[0].chunks)
            if len(containing) != 1:
                problems.append(
                    (fragment, matches[0].module, matches[0].line, containing)
                )
        assert not problems, (
            f"{problems} -- a published fragment must live inside "
            f"exactly ONE literal chunk of its matching shape, never "
            f"zero (spanning an interpolation boundary) and never more "
            f"than one (D-05's 'never the aggregated body' rule)."
        )

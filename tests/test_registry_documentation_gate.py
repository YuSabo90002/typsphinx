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

from typsphinx.template_registry import _KEY_SHAPE_REJECTION_CASES

REPO_ROOT = Path(__file__).resolve().parent.parent
TYPSPHINX_PKG_DIR = REPO_ROOT / "typsphinx"
DOCS_SOURCE_DIR = REPO_ROOT / "docs" / "source"
README_PATH = REPO_ROOT / "README.md"
EXAMPLES_DIR = REPO_ROOT / "examples"
CONFIGURATION_RST_PATH = DOCS_SOURCE_DIR / "user_guide" / "configuration.rst"

CATALOGUE_HEADING = "When the Build Stops"

# Phase 56 plan 02 (D-07/DOC-15): the "registry key naming rules"
# sub-subsection heading and the case-name -> distinguishing-phrase map.
# Keys are checked for exact set-equality against
# ``set(_KEY_SHAPE_REJECTION_CASES)``, so a renamed or an eighth case
# fails loudly here rather than silently going unchecked.
NAMING_RULES_HEADING = "Registry Key Naming Rules"

CASE_NAME_TO_PHRASE = {
    "empty_or_whitespace_only": "Empty or whitespace-only",
    "dot_or_dotdot": "Exactly ``.`` or ``..``",
    "contains_path_separator": "Contains a path separator",
    "windows_reserved_device_name": "Windows reserved device name",
    "trailing_dot": "Ends with a trailing dot",
    "trailing_space": "Ends with a trailing space",
    "case_collision": "Differs from another declared key only by case",
}

# Phase 56 plan 01 (D-02/DOC-15): the retracted element [4] definition
# ("Document class ... accepted and ignored") must survive on no
# published surface. This is the exact four-word phrase that named it.
RETRACTED_ELEMENT_FOUR_PHRASE = "accepted and ignored"

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


def _region_text_by_heading(heading: str) -> str:
    """Every line of ``configuration.rst`` from ``heading`` (found by its
    title TEXT, never by line number) up to but excluding the next
    section-underline-only line -- shared by every doc-gate class in this
    module that binds a code-side enumeration to one section of the
    page."""
    text = CONFIGURATION_RST_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    heading_idx = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            heading_idx = i
            break
    if heading_idx is None:
        raise AssertionError(f"configuration.rst does not contain a {heading!r} heading.")
    underline_re = re.compile(r"^[=\-~^]+$")
    start = heading_idx + 2  # past the heading text and its own underline
    end = len(lines)
    for j in range(start, len(lines)):
        candidate = lines[j].strip()
        if candidate and underline_re.match(candidate):
            end = j
            break
    return "\n".join(lines[start:end])


def _catalogue_region_text() -> str:
    """Every line of ``configuration.rst``'s ``When the Build Stops``
    section -- see ``_region_text_by_heading()``."""
    return _region_text_by_heading(CATALOGUE_HEADING)


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
# The element [4] retraction sweep (D-02/DOC-15, Task 3) -- a separate
# concern from the error-catalogue gate above, sharing this module only
# because both are D-06-shaped never-skipping doc<->code checks.
# --------------------------------------------------------------------------

# Empty by design -- unlike EXCLUDED_CLAIM_PAGES in
# tests/test_docs_contract_claims_gate.py, docs/source/changelog.rst is
# NOT excluded here, because RETRACTED_ELEMENT_FOUR_PHRASE does not
# appear in it. An empty exclusion set is the honest current state, not
# a placeholder waiting to be filled in -- if a future edit reintroduces
# the phrase somewhere it belongs historically, add a reasoned entry
# then, rather than pre-excluding a page that has nothing to exclude
# today.
EXCLUDED_SWEEP_PATHS: dict = {}


def _iter_policed_sweep_files() -> list:
    """Every ``*.rst`` under ``docs/source/``, plus ``README.md``, plus
    every ``*.md``/``*.rst``/``*.py`` under ``examples/`` -- the exact
    policed surface 54.1 D-08/D-12 established, discovered at run time
    via ``rglob`` over repository-relative roots, never a written file
    list."""
    files = set(DOCS_SOURCE_DIR.rglob("*.rst"))
    if README_PATH.is_file():
        files.add(README_PATH)
    for pattern in ("*.md", "*.rst", "*.py"):
        files |= set(EXAMPLES_DIR.rglob(pattern))
    return sorted(files)


def _phrase_present(text: str, phrase: str) -> bool:
    return phrase in text


def _files_containing_phrase(phrase: str, files: list) -> list:
    """Repository-relative paths (posix form) of every file in
    ``files`` whose text contains ``phrase``, skipping anything listed
    in ``EXCLUDED_SWEEP_PATHS``."""
    offending = []
    for file_path in files:
        rel = file_path.relative_to(REPO_ROOT).as_posix()
        if rel in EXCLUDED_SWEEP_PATHS:
            continue
        text = file_path.read_text(encoding="utf-8")
        if _phrase_present(text, phrase):
            offending.append(rel)
    return offending


def _shape_by_fragment(shapes: list, identifying_fragment: str) -> ErrorShape:
    """The discovered shape whose chunks contain ``identifying_fragment``
    -- used only to DERIVE synthetic teeth-test inputs from the real
    discovered shapes at run time, never to type an ambiguous fragment by
    hand."""
    for shape in shapes:
        if any(identifying_fragment in chunk for chunk in shape.chunks):
            return shape
    raise AssertionError(
        f"No discovered shape contains {identifying_fragment!r} -- the "
        f"teeth test that derives an ambiguous fragment from it cannot "
        f"run."
    )


def _common_prefix(text_a: str, text_b: str) -> str:
    length = min(len(text_a), len(text_b))
    index = 0
    while index < length and text_a[index] == text_b[index]:
        index += 1
    return text_a[:index]


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


class TestCatalogueGateHasTeeth:
    """D-06 anti-vacuity: synthetic known-bad inputs fed DIRECTLY to the
    same pure helpers ``TestErrorCatalogueAgreesWithCode`` uses, proving
    each of the gate's five failure modes actually fires. Without these,
    the real assertions above could pass vacuously if a helper silently
    stopped detecting anything."""

    def test_an_undocumented_code_shape_is_detected(self):
        # Without this test, test_code_to_docs_every_non_excluded_shape_
        # is_published could pass vacuously if _shape_is_covered() always
        # returned True.
        published = _published_fragments()
        undocumented_shape = ErrorShape(
            module="synthetic.py",
            line=1,
            chunks=[
                "a sentence deliberately absent from every published "
                "catalogue fragment"
            ],
        )
        assert not _shape_is_covered(undocumented_shape, published), (
            "_shape_is_covered() reported a synthetic shape whose chunk "
            "text appears in no published fragment as COVERED -- the "
            "code-to-docs coverage check would pass vacuously."
        )

    def test_an_invented_published_clause_is_detected(self):
        # Without this test, test_docs_to_code_every_fragment_matches_
        # exactly_one_shape could pass vacuously if _matching_shapes()
        # always returned a non-empty list.
        shapes = _discover_error_shapes()
        invented_fragment = "a phrase no ExtensionError message ever raises"
        matches = _matching_shapes(invented_fragment, shapes)
        assert not matches, (
            f"_matching_shapes() found {matches} for a fragment invented "
            f"for this test, present in no real message -- the docs-to-"
            f"code direction would pass vacuously for an invented clause."
        )

    def test_an_ambiguous_published_clause_is_detected(self):
        # Without this test, test_docs_to_code_every_fragment_matches_
        # exactly_one_shape could pass vacuously if _matching_shapes()
        # never reported more than one match. The ambiguous fragment is
        # DERIVED from two real discovered shapes at run time (their
        # shared "typst: " leading prefix), never typed by hand.
        shapes = _discover_error_shapes()
        shape_a = _shape_by_fragment(shapes, "output path collision(s):")
        shape_b = _shape_by_fragment(shapes, "pre-write template path failure(s):")
        ambiguous_fragment = _common_prefix(shape_a.chunks[0], shape_b.chunks[0])
        assert ambiguous_fragment, (
            "The two shapes this test derives an ambiguous fragment from "
            "no longer share a common prefix -- the test's own premise "
            "broke; re-derive it from the current source."
        )
        matches = _matching_shapes(ambiguous_fragment, shapes)
        assert len(matches) > 1, (
            f"_matching_shapes({ambiguous_fragment!r}, ...) found only "
            f"{matches} -- expected more than one discovered shape to "
            f"share this derived prefix, so the uniqueness check would "
            f"pass vacuously for a genuinely ambiguous fragment."
        )

    def test_a_fragment_spanning_an_interpolation_boundary_is_detected(self):
        # Without this test, test_single_literal_chunk_rule could pass
        # vacuously if _chunks_containing_fragment() credited a fragment
        # that only exists once two separate literal chunks are
        # concatenated together -- exactly what D-05 forbids.
        chunk_one = "the alpha be"
        chunk_two = "ta feature works"
        synthetic_shape_chunks = [chunk_one, chunk_two]
        spanning_fragment = chunk_one[-8:] + chunk_two[:10]  # "alpha beta feature"
        assert spanning_fragment not in chunk_one
        assert spanning_fragment not in chunk_two
        spanning_matches = _chunks_containing_fragment(
            spanning_fragment, synthetic_shape_chunks
        )
        assert not spanning_matches, (
            f"_chunks_containing_fragment() credited the spanning "
            f"fragment {spanning_fragment!r} against chunks "
            f"{synthetic_shape_chunks!r} -- a fragment that only exists "
            f"once chunks are concatenated must never be credited as a "
            f"single-chunk match."
        )
        single_chunk_fragment = chunk_one[-8:]  # fully inside chunk_one alone
        single_chunk_matches = _chunks_containing_fragment(
            single_chunk_fragment, synthetic_shape_chunks
        )
        assert single_chunk_matches == [0], (
            f"_chunks_containing_fragment() failed to credit a fragment "
            f"drawn entirely from one real chunk -- expected match index "
            f"[0], got {single_chunk_matches}."
        )

    def test_a_stale_exclusion_is_detected(self):
        # Without this test, test_every_excluded_fragment_still_matches_
        # a_discovered_shape could pass vacuously if _stale_exclusions()
        # never reported anything as stale.
        shapes = _discover_error_shapes()
        synthetic_excluded = {
            "a phrase deliberately excluded but present in no real shape": (
                "synthetic exclusion for the teeth test -- never a real "
                "denylist entry."
            )
        }
        stale = _stale_exclusions(synthetic_excluded, shapes)
        assert stale == list(synthetic_excluded), (
            f"_stale_exclusions() failed to report the synthetic "
            f"exclusion as stale -- got {stale}, expected "
            f"{list(synthetic_excluded)}. The staleness check would pass "
            f"vacuously for a genuinely stale exclusion."
        )


class TestRetractedElementFourDefinitionIsGone:
    """D-02/DOC-15: the retracted "accepted and ignored" definition of
    ``typst_documents`` element [4] survives on no published surface --
    swept repo-wide at discovery time (milestone invariant #4/#11), never
    scoped to the one line the retraction is known to have touched."""

    def test_retracted_phrase_absent_from_every_policed_file(self):
        files = _iter_policed_sweep_files()
        offending = _files_containing_phrase(RETRACTED_ELEMENT_FOUR_PHRASE, files)
        assert not offending, (
            f"The retracted phrase {RETRACTED_ELEMENT_FOUR_PHRASE!r} still "
            f"appears in {offending} -- DOC-15 requires it survive on no "
            f"published surface."
        )

    def test_no_stale_sweep_exclusion(self):
        discovered = {
            path.relative_to(REPO_ROOT).as_posix()
            for path in _iter_policed_sweep_files()
        }
        stale = set(EXCLUDED_SWEEP_PATHS) - discovered
        assert not stale, (
            f"{sorted(stale)} are in EXCLUDED_SWEEP_PATHS but were not "
            f"discovered by the sweep -- a stale exclusion. Remove them "
            f"from EXCLUDED_SWEEP_PATHS."
        )

    def test_sweep_predicate_has_teeth(self):
        # Without this test, test_retracted_phrase_absent_from_every_
        # policed_file could pass vacuously if _phrase_present() stopped
        # matching anything.
        synthetic_text = (
            '5. Document class (usually "typst") -- accepted and '
            "ignored: typsphinx reads nothing from this position."
        )
        assert _phrase_present(synthetic_text, RETRACTED_ELEMENT_FOUR_PHRASE), (
            "The sweep predicate failed to detect the retracted phrase "
            "in a synthetic known-bad string -- this guard would pass "
            "vacuously."
        )


# --------------------------------------------------------------------------
# Phase 56 plan 02 (D-07/DOC-15): the registry key naming rules gate --
# the published seven-case table bound to _KEY_SHAPE_REJECTION_CASES by
# import, never transcription.
# --------------------------------------------------------------------------


def _naming_rules_region_text() -> str:
    return _region_text_by_heading(NAMING_RULES_HEADING)


def _region_missing_phrases(region: str, name_to_phrase: dict) -> list:
    """Names whose distinguishing phrase from ``name_to_phrase`` is absent
    from ``region`` -- shared pure helper: both the real assertions and
    the teeth tests below call this SAME function."""
    return [name for name, phrase in name_to_phrase.items() if phrase not in region]


class TestKeyNamingRulesMatchTheCode:
    """D-07: the published seven registry-key rejection cases, in the
    fixed order the code checks them, held to
    ``typsphinx.template_registry._KEY_SHAPE_REJECTION_CASES`` by import
    -- an eighth case added in code fails this class until the page names
    it."""

    def test_exactly_seven_cases_in_the_code(self):
        assert len(_KEY_SHAPE_REJECTION_CASES) == 7, (
            f"_KEY_SHAPE_REJECTION_CASES has "
            f"{len(_KEY_SHAPE_REJECTION_CASES)} entries, expected exactly "
            f"7 -- CONF-18's denylist is locked at seven cases; if an "
            f"eighth was genuinely added, CASE_NAME_TO_PHRASE and the "
            f"published naming-rules table must grow with it."
        )

    def test_phrase_map_keys_match_the_code_exactly(self):
        assert set(CASE_NAME_TO_PHRASE) == set(_KEY_SHAPE_REJECTION_CASES), (
            f"CASE_NAME_TO_PHRASE's keys {sorted(CASE_NAME_TO_PHRASE)} do "
            f"not exactly match _KEY_SHAPE_REJECTION_CASES "
            f"{sorted(_KEY_SHAPE_REJECTION_CASES)} -- a renamed or added "
            f"case must not go silently unchecked."
        )

    def test_every_case_phrase_is_published(self):
        region = _naming_rules_region_text()
        missing = _region_missing_phrases(region, CASE_NAME_TO_PHRASE)
        assert not missing, (
            f"{missing} have no distinguishing phrase published in the "
            f"'Registry Key Naming Rules' region of configuration.rst."
        )

    def test_region_names_casefold_and_no_unicode_normalization(self):
        region = _naming_rules_region_text()
        assert "casefold" in region, (
            "The 'Registry Key Naming Rules' region does not name "
            "'casefold' -- the comparison rule must be stated precisely."
        )
        assert "no Unicode normalization" in region, (
            "The 'Registry Key Naming Rules' region does not state that "
            "no Unicode normalization is applied."
        )

    def test_teeth_a_missing_phrase_is_detected(self):
        # Without this test, test_every_case_phrase_is_published could
        # pass vacuously if _region_missing_phrases() stopped detecting
        # anything.
        synthetic_region = "\n".join(
            phrase
            for name, phrase in CASE_NAME_TO_PHRASE.items()
            if name != "trailing_dot"
        )
        missing = _region_missing_phrases(synthetic_region, CASE_NAME_TO_PHRASE)
        assert missing == ["trailing_dot"], (
            f"_region_missing_phrases() failed to report the deliberately "
            f"omitted 'trailing_dot' case as missing from a synthetic "
            f"region -- got {missing}. This guard would pass vacuously "
            f"for a genuinely incomplete naming-rules page."
        )

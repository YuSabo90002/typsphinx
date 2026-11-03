"""
SC2 surface gate (T002): every Sphinx code block in the generated content
``.typ`` files is exactly one code-mode codly 2.0 ``codly.new(raw(...), ...)``
expression, and no ``` fence or 1.3-era ``codly(...)`` call survives.

Five real ``-b typst`` builds are inspected: ``tests/roots/test-basic``,
``examples/basic``, ``examples/advanced``, typsphinx's own ``docs/source`` and
the purpose-made ``tests/fixtures/codly2_render_gate`` fixture. The fixture
supplies the code-block contexts the four projects lack (a captioned listing
and a table cell); the union of all five must contain a block in each of the
four contexts SC2 names (captioned figure, list item, admonition, table cell).

Content files are every ``.typ`` file outside ``_typsphinx/`` and
``_template/`` that is not a ``typst_documents`` wrapper -- one per docname.
For each document the build's own doctree pickle (``-d <doctrees>``) is the
oracle: the code-mode ``codly.new(raw(`` occurrences in its content file must
equal its literal_block + doctest_block count, each must parse against the
emission grammar, and the decoded ``raw()`` strings must equal the nodes'
texts in document order.

"Code-mode" matters: typsphinx's own docs mention ``codly.new(raw(...))`` in
inline literals, which the translator emits as Typst string literals
(``raw("codly.new(raw(...))")``). Text inside a string literal is content,
not an expression, so the count skips string-literal spans.

The ``codly(`` absence check runs over the WHOLE text, string literals
included, with one bounded exemption (INTENT correction C5): in the
docs/source build only, a hit inside an inline ``raw("...")`` literal of
``changelog.typ`` whose decoded text occurs verbatim in ``CHANGELOG.md`` --
the released-history entries that quote the 1.3-era output. Each tolerated
literal is listed in ``CHANGELOG_TOLERATED`` and every other hit fails.

Builds run as ``sys.executable -m sphinx`` so the interpreter running the test
is reused. Assertions compare text only (no native paths, no colour codes).
"""

import bisect
import importlib.util
import os
import pickle
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from docutils import nodes

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_SOURCE_DIR = REPO_ROOT / "docs" / "source"
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "codly2_render_gate"

# Project id -> source dir. The docs tree needs the `docs` extra.
PROJECTS = {
    "test-basic": REPO_ROOT / "tests" / "roots" / "test-basic",
    "examples-basic": REPO_ROOT / "examples" / "basic",
    "examples-advanced": REPO_ROOT / "examples" / "advanced",
    "docs-source": DOCS_SOURCE_DIR,
    "fixture": FIXTURE_DIR,
}

# The four projects SC2 names; the absence checks run over exactly these. The
# fixture is excluded there because its E2 encoding block deliberately holds
# backtick runs inside its raw() string; for it, only code-mode text (string
# literals removed) must be fence-free.
SC2_PROJECTS = ("test-basic", "examples-basic", "examples-advanced", "docs-source")

# Projects whose documents must contain at least one code block in total.
PROJECTS_WITH_CODE = ("examples-basic", "examples-advanced", "docs-source", "fixture")

# Single-segment module names only (see tests/test_bibliography_docs_gate.py).
_DOCS_EXTRA_MODULES = ("myst_parser", "sphinx_autodoc_typehints", "furo")

# The exact inline-literal texts tolerated by the C5 exemption: released
# CHANGELOG entries quoting codly 1.3-era output. Each must still occur
# verbatim in CHANGELOG.md, and each must actually be hit.
CHANGELOG_TOLERATED = frozenset({"{ codly(...) }", "#codly(number-format: none)"})

FENCE = "```"
BARE_CODLY_RE = re.compile(r"(^|[^.a-z-])codly\(", re.MULTILINE)
STRING_RE = re.compile(r'"(?:[^"\\]|\\.)*"')
CODLY_NEW = "codly.new(raw("

# The T001 Interface-contract grammar of one code block, anchored at
# "codly.new(". Named arguments are optional but must appear in this order.
EXPRESSION_RE = re.compile(
    r'codly\.new\(raw\((?P<code>"(?:[^"\\]|\\.)*"), block: true'
    r'(?:, lang: "(?P<lang>(?:[^"\\]|\\.)*)")?\)'
    r"(?:, number-enabled: false)?"
    r"(?:, offset: -?\d+)?"
    r"(?:, highlighted: \((?:-?\d+,|-?\d+(?:, -?\d+)+)\))?"
    r"(?:, skip-last-empty: false)?"
    r"\)"
)
CAPTION_SUFFIX_RE = re.compile(r', caption: text\("(?:[^"\\]|\\.)*"\), kind: raw\)\n')
_ESCAPES = {"\\": "\\", '"': '"', "n": "\n", "r": "\r", "t": "\t"}


def _docs_extras_available() -> bool:
    for name in _DOCS_EXTRA_MODULES:
        try:
            if importlib.util.find_spec(name) is None:
                return False
        except ModuleNotFoundError:
            return False
    return True


def decode_typst_string(literal: str) -> str:
    """Decode a Typst ``"..."`` string literal (quotes included)."""
    assert literal[0] == '"' and literal[-1] == '"', literal
    body = literal[1:-1]
    out = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        nxt = body[i + 1]
        if nxt == "u":
            close = body.index("}", i)
            out.append(chr(int(body[i + 3 : close], 16)))
            i = close + 1
            continue
        out.append(_ESCAPES[nxt])
        i += 2
    return "".join(out)


def string_spans(src: str) -> list[tuple[int, int]]:
    """``(start, end)`` of every ``"..."`` string literal in ``src``."""
    spans = []
    pos = src.find('"')
    while pos >= 0:
        match = STRING_RE.match(src, pos)
        assert match is not None, f"unterminated string literal at offset {pos}"
        spans.append(match.span())
        pos = src.find('"', match.end())
    return spans


def enclosing_span(spans: list[tuple[int, int]], pos: int) -> tuple[int, int] | None:
    starts = [start for start, _ in spans]
    k = bisect.bisect_right(starts, pos) - 1
    if k >= 0 and spans[k][0] < pos < spans[k][1]:
        return spans[k]
    return None


def code_contexts(block: nodes.Element) -> set[str]:
    """The SC2 contexts a code block sits in."""
    found = set()
    parent = block.parent
    while parent is not None:
        if isinstance(parent, nodes.container) and "literal-block-wrapper" in (
            parent.get("classes", [])
        ):
            found.add("captioned figure")
        elif isinstance(parent, nodes.list_item):
            found.add("list item")
        elif isinstance(parent, nodes.Admonition):
            found.add("admonition")
        elif isinstance(parent, nodes.entry):
            found.add("table cell")
        parent = parent.parent
    return found


@dataclass
class Document:
    project: str
    docname: str
    path: Path
    text: str
    blocks: list[nodes.Element]


@dataclass
class Build:
    project: str
    outdir: Path
    documents: list[Document]
    wrappers: set[str]
    all_typ: set[str]


def _build(project: str, tmp_root: Path) -> Build:
    outdir = tmp_root / "out"
    doctrees = tmp_root / "doctrees"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-E",
            "-b",
            "typst",
            "-d",
            str(doctrees),
            str(PROJECTS[project]),
            str(outdir),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "LC_ALL": "C"},
    )
    assert result.returncode == 0, (
        f"typst build of {project} failed\n--- stdout ---\n{result.stdout}"
        f"\n--- stderr ---\n{result.stderr}"
    )
    env = pickle.loads((doctrees / "environment.pickle").read_bytes())
    wrappers = {
        f"{entry[1].removesuffix('.typ')}.typ" for entry in env.config.typst_documents
    }
    documents = []
    for pickle_path in sorted(doctrees.rglob("*.doctree")):
        docname = pickle_path.relative_to(doctrees).with_suffix("").as_posix()
        tree = pickle.loads(pickle_path.read_bytes())
        blocks = list(
            tree.findall(
                lambda n: isinstance(n, (nodes.literal_block, nodes.doctest_block))
            )
        )
        path = outdir / f"{docname}.typ"
        assert path.is_file(), f"{project}: no content file for docname {docname}"
        documents.append(
            Document(project, docname, path, path.read_text(encoding="utf-8"), blocks)
        )
    all_typ = {
        p.relative_to(outdir).as_posix()
        for p in outdir.rglob("*.typ")
        if p.relative_to(outdir).parts[0] not in ("_typsphinx", "_template")
    }
    return Build(project, outdir, documents, wrappers, all_typ)


@pytest.fixture(scope="module")
def builds(tmp_path_factory) -> dict[str, Build]:
    if not _docs_extras_available():
        pytest.skip(
            "docs extras absent (myst-parser / sphinx-autodoc-typehints / furo): "
            "the docs/source build aborts before reaching typsphinx -- install "
            "the `docs` extra to run this gate."
        )
    return {
        project: _build(project, tmp_path_factory.mktemp(f"codly2_{project}"))
        for project in PROJECTS
    }


def _all_documents(builds: dict[str, Build]) -> list[Document]:
    return [doc for build in builds.values() for doc in build.documents]


def _code_mode_expressions(doc: Document) -> list[re.Match]:
    """Every ``codly.new(raw(`` outside a string literal, parsed."""
    spans = string_spans(doc.text)
    matches = []
    pos = doc.text.find(CODLY_NEW)
    while pos >= 0:
        if enclosing_span(spans, pos) is None:
            match = EXPRESSION_RE.match(doc.text, pos)
            assert match is not None, (
                f"{doc.project}:{doc.docname}: codly.new expression does not match "
                f"the emission grammar: {doc.text[pos : pos + 200]!r}"
            )
            matches.append(match)
        pos = doc.text.find(CODLY_NEW, pos + 1)
    return matches


class TestContentFileSet:
    def test_content_files_are_docnames_plus_wrappers(self, builds):
        """Every .typ outside _typsphinx/ and _template/ is either a docname's
        content file or a typst_documents wrapper -- nothing escapes the scan."""
        for build in builds.values():
            content = {f"{doc.docname}.typ" for doc in build.documents}
            assert build.all_typ == content | build.wrappers, build.project
            assert not content & build.wrappers, build.project
            for wrapper in build.wrappers:
                text = (build.outdir / wrapper).read_text(encoding="utf-8")
                assert "#include(" in text, f"{build.project}: {wrapper} is no wrapper"


class TestCodeModeEmission:
    def test_count_equals_doctree_code_blocks(self, builds):
        for doc in _all_documents(builds):
            expressions = _code_mode_expressions(doc)
            assert len(expressions) == len(doc.blocks), (
                f"{doc.project}:{doc.docname}: {len(expressions)} code-mode "
                f"codly.new(raw( expressions for {len(doc.blocks)} "
                "literal_block + doctest_block nodes"
            )

    def test_decoded_code_equals_doctree_text_in_order(self, builds):
        for doc in _all_documents(builds):
            decoded = [
                decode_typst_string(m.group("code"))
                for m in _code_mode_expressions(doc)
            ]
            assert decoded == [
                block.astext() for block in doc.blocks
            ], f"{doc.project}:{doc.docname}"

    def test_expression_shape_and_termination(self, builds):
        """No leading `#`; a plain expression ends its line, a captioned one
        is the first argument of figure(..., caption: text(...), kind: raw).

        A table cell's ``{...}`` body is emitted with its trailing whitespace
        trimmed, so there the expression is followed by the cell's closing
        brace instead of the newline.
        """
        for doc in _all_documents(builds):
            for match in _code_mode_expressions(doc):
                start, end = match.span()
                where = f"{doc.project}:{doc.docname}: {match.group(0)[:120]!r}"
                assert doc.text[start - 1 : start] != "#", where
                if doc.text[:start].endswith("figure("):
                    assert CAPTION_SUFFIX_RE.match(doc.text, end), where
                else:
                    assert doc.text[end : end + 1] in ("\n", "}"), where

    def test_projects_contain_code_and_test_basic_has_none(self, builds):
        for project in PROJECTS_WITH_CODE:
            total = sum(len(doc.blocks) for doc in builds[project].documents)
            assert total > 0, f"{project} has no code block to gate"
        basic = builds["test-basic"]
        assert sum(len(doc.blocks) for doc in basic.documents) == 0
        assert all(CODLY_NEW not in doc.text for doc in basic.documents)

    def test_every_sc2_context_is_covered(self, builds):
        covered = set()
        for doc in _all_documents(builds):
            for block in doc.blocks:
                covered |= code_contexts(block)
        assert covered == {
            "captioned figure",
            "list item",
            "admonition",
            "table cell",
        }

    def test_no_other_raw_block_form(self, builds):
        """A code-mode raw(..., block: true) is only ever codly.new's body."""
        for doc in _all_documents(builds):
            spans = string_spans(doc.text)
            for match in re.finditer(r"raw\(", doc.text):
                if enclosing_span(spans, match.start()) is not None:
                    continue
                if doc.text[: match.start()].endswith("codly.new("):
                    continue
                literal = STRING_RE.match(doc.text, match.end())
                if literal is None:
                    continue
                tail = doc.text[literal.end() : literal.end() + 13]
                assert not tail.startswith(", block: true"), (
                    f"{doc.project}:{doc.docname}: bare raw block "
                    f"{doc.text[match.start() : match.start() + 120]!r}"
                )


class TestAbsence:
    def test_no_fence_in_sc2_projects(self, builds):
        for project in SC2_PROJECTS:
            for doc in builds[project].documents:
                assert FENCE not in doc.text, f"{project}:{doc.docname}"

    def test_no_fence_in_fixture_code_mode_text(self, builds):
        for doc in builds["fixture"].documents:
            code_mode = STRING_RE.sub('""', doc.text)
            assert FENCE not in code_mode, f"fixture:{doc.docname}"

    def test_no_bare_codly_call_outside_the_changelog_exemption(self, builds):
        changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
        tolerated = []
        for doc in (d for p in SC2_PROJECTS for d in builds[p].documents):
            spans = string_spans(doc.text)
            for match in BARE_CODLY_RE.finditer(doc.text):
                pos = match.end() - len("codly(")
                where = (
                    f"{doc.project}:{doc.docname}: "
                    f"{doc.text[max(pos - 40, 0) : pos + 60]!r}"
                )
                span = enclosing_span(spans, pos)
                assert (
                    doc.project == "docs-source" and doc.docname == "changelog"
                ), f"bare codly( call: {where}"
                assert span is not None, f"bare codly( outside a string: {where}"
                before = doc.text[: span[0]]
                assert before.endswith("raw(") and not before.endswith(
                    CODLY_NEW
                ), f"codly( string is not an inline raw() literal: {where}"
                decoded = decode_typst_string(doc.text[span[0] : span[1]])
                assert decoded in changelog, f"not verbatim CHANGELOG text: {where}"
                assert decoded in CHANGELOG_TOLERATED, f"unlisted exemption: {where}"
                tolerated.append(decoded)
        assert set(tolerated) == CHANGELOG_TOLERATED
        assert len(tolerated) == len(CHANGELOG_TOLERATED)

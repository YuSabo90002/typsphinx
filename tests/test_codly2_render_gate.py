"""
SC3/SC4 surface gate (T002): codly 2.0 code blocks as they render in the PDF.

The fixture ``tests/fixtures/codly2_render_gate`` is built once with
``sys.executable -m sphinx -E -b typstpdf`` (which also writes the content
``.typ`` and, via ``-d``, the doctree pickles). The PDF is then read with
pypdf in two ways:

* text runs with their page coordinates (``extract_text(visitor_text=...)``),
  grouped into rows by baseline. Each code block's rows are found by its
  unique sentinel; a digits-only run left of the code is its line number and
  a run in the right-hand part of the page is codly's language badge (every
  fixture code line is short, so code never reaches that region);
* filled shapes from the page content stream (a small q/Q/cm/path/fill
  interpreter). A row is *highlighted* when a row-sized fill covering its code
  column carries a paint that no row of an un-highlighted control block ever
  carries (codly's default zebra stripes are therefore not mistaken for
  highlights). This compares structure -- which rows are highlighted -- never
  an exact colour value, so it fails if ``highlighted`` is empty, shifted by
  the offset or carries an extra line.

Assertions compare text and structure only: no native paths, no ANSI colour
codes, no exact colours (CI runs ubuntu/windows/macos). The build runs with
``LC_ALL=C`` so Sphinx's out-of-range warning text is English.
"""

import os
import pickle
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from docutils import nodes

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf
    from pypdf.generic import ContentStream

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst and pypdf are required for the codly 2.0 render gate",
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "codly2_render_gate"
ENCODING_SNIPPET = FIXTURE_DIR / "encoding_snippet.txt"
TAB_SNIPPET = FIXTURE_DIR / "tab_snippet.txt"

CODLY_NEW = "codly.new(raw("
STRING_RE = re.compile(r'"(?:[^"\\]|\\.)*"')
# One code-block expression of T001's Interface contract, anchored at
# "codly.new(" (the named arguments are optional, in this order).
EXPRESSION_RE = re.compile(
    r'codly\.new\(raw\((?P<code>"(?:[^"\\]|\\.)*"), block: true'
    r'(?:, lang: "(?P<lang>(?:[^"\\]|\\.)*)")?\)'
    r"(?P<named>(?:, number-enabled: false)?"
    r"(?:, offset: -?\d+)?"
    r"(?:, highlighted: \((?:-?\d+,|-?\d+(?:, -?\d+)+)\))?"
    r"(?:, skip-last-empty: false)?)"
    r"\)"
)
_ESCAPES = {"\\": "\\", '"': '"', "n": "\n", "r": "\r", "t": "\t"}

# A badge run sits in the right-hand part of the code block.
BADGE_REGION = 0.7
# A fill taller than this is not a single code row.
MAX_ROW_FILL_HEIGHT = 30.0


def decode_typst_string(literal: str) -> str:
    """Decode a Typst ``"..."`` string literal (quotes included)."""
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


@dataclass
class Run:
    x: float
    text: str


@dataclass
class Row:
    page: int
    y: float
    runs: list[Run]
    badge_x: float

    @property
    def body_runs(self) -> list[Run]:
        return [r for r in self.runs if r.x < self.badge_x]

    @property
    def number(self) -> int | None:
        body = self.body_runs
        if body and re.fullmatch(r"\d+", body[0].text.strip()):
            return int(body[0].text.strip())
        return None

    @property
    def code_runs(self) -> list[Run]:
        body = self.body_runs
        return body[1:] if self.number is not None else body

    @property
    def code_x(self) -> float:
        return self.code_runs[0].x

    @property
    def code(self) -> str:
        text = "".join(r.text for r in self.code_runs)
        # pypdf separates the number run from the code with one space.
        return text[1:] if self.number is not None and text[:1] == " " else text

    @property
    def badge(self) -> str:
        return "".join(r.text for r in self.runs if r.x >= self.badge_x).strip()

    @property
    def text(self) -> str:
        return "".join(r.text for r in self.runs).replace("\xa0", " ")


@dataclass
class Fill:
    page: int
    x0: float
    x1: float
    y0: float
    y1: float
    paint: tuple


@dataclass
class Pdf:
    rows: list[Row] = field(default_factory=list)
    fills: list[Fill] = field(default_factory=list)

    def block(self, token: str) -> list[Row]:
        found = [row for row in self.rows if token in row.code]
        assert found, f"no PDF row contains sentinel {token!r}"
        return found

    def row_with(self, needle: str) -> Row:
        found = [row for row in self.rows if needle in row.text]
        assert len(found) == 1, f"{needle!r}: {len(found)} rows"
        return found[0]

    def covering_fills(self, page: int, y: float, x: float) -> list[Fill]:
        return [
            f
            for f in self.fills
            if f.page == page
            and f.y0 - 0.5 <= y <= f.y1 + 0.5
            and f.x0 <= x <= f.x1
            and f.y1 - f.y0 < MAX_ROW_FILL_HEIGHT
        ]

    def row_paints(self, row: Row) -> list[tuple]:
        return [f.paint for f in self.covering_fills(row.page, row.y, row.code_x)]


def _mul(m, n):
    """PDF matrix product ``m x n`` (``cm`` pre-multiplies the CTM)."""
    a, b, c, d, e, f = m
    p, q, r, s, t, u = n
    return (
        a * p + b * r,
        a * q + b * s,
        c * p + d * r,
        c * q + d * s,
        e * p + f * r + t,
        e * q + f * s + u,
    )


def _page_fills(reader, page, index: int) -> list[Fill]:
    """Every filled path on the page, as a page-space bounding box + paint."""
    fills = []
    ctm = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    paint: tuple = ()
    stack = []
    points: list[tuple[float, float]] = []
    for operands, op in ContentStream(page.get_contents(), reader).operations:
        if op == b"q":
            stack.append((ctm, paint))
        elif op == b"Q":
            ctm, paint = stack.pop()
        elif op == b"cm":
            ctm = _mul(tuple(float(v) for v in operands), ctm)
        elif op in (b"sc", b"scn", b"rg", b"g", b"k"):
            paint = tuple(
                round(float(v), 3) for v in operands if isinstance(v, (int, float))
            )
        elif op in (b"m", b"l"):
            points.append((float(operands[0]), float(operands[1])))
        elif op in (b"c", b"v", b"y"):
            vals = [float(v) for v in operands]
            points.extend(zip(vals[0::2], vals[1::2], strict=True))
        elif op == b"re":
            x, y, w, h = (float(v) for v in operands)
            points.extend([(x, y), (x + w, y + h)])
        elif op in (b"f", b"F", b"f*", b"B", b"B*", b"b", b"b*"):
            if points:
                mapped = [
                    (x * ctm[0] + y * ctm[2] + ctm[4], x * ctm[1] + y * ctm[3] + ctm[5])
                    for x, y in points
                ]
                xs = [p[0] for p in mapped]
                ys = [p[1] for p in mapped]
                fills.append(Fill(index, min(xs), max(xs), min(ys), max(ys), paint))
            points = []
        elif op in (b"n", b"S", b"s"):
            points = []
    return fills


def _read_pdf(path: Path) -> Pdf:
    reader = pypdf.PdfReader(path)
    pdf = Pdf()
    for index, page in enumerate(reader.pages):
        badge_x = float(page.mediabox.width) * BADGE_REGION
        by_y: dict[float, list[Run]] = {}

        def visit(text, cm, tm, _font, _size, by_y=by_y):
            if not text.strip():
                return
            x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
            by_y.setdefault(round(y, 1), []).append(Run(x, text))

        page.extract_text(visitor_text=visit)
        for y in sorted(by_y, reverse=True):
            pdf.rows.append(Row(index, y, sorted(by_y[y], key=lambda r: r.x), badge_x))
        pdf.fills.extend(_page_fills(reader, page, index))
    return pdf


@dataclass
class Gate:
    result: subprocess.CompletedProcess
    typ: str
    expressions: list[re.Match]
    blocks: list[nodes.Element]
    pdf: Pdf
    outdir: Path

    def expression(self, token: str) -> re.Match:
        found = [m for m in self.expressions if token in m.group("code")]
        assert len(found) == 1, f"{token!r}: {len(found)} codly.new expressions"
        return found[0]


@pytest.fixture(scope="module")
def gate(tmp_path_factory) -> Gate:
    root = tmp_path_factory.mktemp("codly2_render_gate")
    outdir = root / "out"
    doctrees = root / "doctrees"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-E",
            "-b",
            "typstpdf",
            "-d",
            str(doctrees),
            str(FIXTURE_DIR),
            str(outdir),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "LC_ALL": "C"},
    )
    assert result.returncode == 0, (
        f"typstpdf build failed\n--- stdout ---\n{result.stdout}"
        f"\n--- stderr ---\n{result.stderr}"
    )
    typ = (outdir / "index.typ").read_text(encoding="utf-8")
    # Code-mode occurrences only: skip text inside string literals.
    spans = [m.span() for m in STRING_RE.finditer(typ)]
    expressions = []
    for pos in (m.start() for m in re.finditer(re.escape(CODLY_NEW), typ)):
        if any(start < pos < end for start, end in spans):
            continue
        match = EXPRESSION_RE.match(typ, pos)
        assert match is not None, typ[pos : pos + 200]
        expressions.append(match)
    tree = pickle.loads((doctrees / "index.doctree").read_bytes())
    blocks = list(
        tree.findall(
            lambda n: isinstance(n, (nodes.literal_block, nodes.doctest_block))
        )
    )
    return Gate(
        result, typ, expressions, blocks, _read_pdf(outdir / "master.pdf"), outdir
    )


def _highlight_paints(gate: Gate) -> set[tuple]:
    """Paints on rows of un-highlighted blocks (codly's plain row styling)."""
    plain = set()
    for token in ("nolnblk", "numonblk", "tenstartblk", "singleblk", "capblk"):
        for row in gate.pdf.block(token):
            plain.update(gate.pdf.row_paints(row))
    return plain


def _highlighted(gate: Gate, token: str) -> list[int]:
    """Per row of the block: how many highlight fills cover its code."""
    plain = _highlight_paints(gate)
    return [
        sum(1 for paint in gate.pdf.row_paints(row) if paint not in plain)
        for row in gate.pdf.block(token)
    ]


class TestBuild:
    def test_one_expression_per_code_block(self, gate):
        assert len(gate.expressions) == len(gate.blocks)
        decoded = [decode_typst_string(m.group("code")) for m in gate.expressions]
        assert decoded == [block.astext() for block in gate.blocks]

    def test_no_codly_1_3_styling_in_emitted_typ(self, gate):
        for match in gate.expressions:
            named = match.group("named")
            for word in ("fill", "zebra", "stroke", "radius", "paint", "highlights"):
                assert word not in named, match.group(0)
        assert "fill:" not in gate.typ
        assert re.search(r"(^|[^.a-z-])codly\(", gate.typ, re.MULTILINE) is None


class TestLineNumbers:
    def test_block_without_linenos_shows_no_numbers(self, gate):
        rows = gate.pdf.block("nolnblk")
        assert len(rows) == 2
        assert [row.number for row in rows] == [None, None]

    def test_linenos_starts_at_one(self, gate):
        assert [r.number for r in gate.pdf.block("numonblk")] == [1, 2, 3]

    def test_lineno_start_ten(self, gate):
        assert [r.number for r in gate.pdf.block("tenstartblk")] == [10, 11, 12]
        assert ", offset: 9" in gate.expression("tenstartblk").group("named")

    def test_lineno_start_one_emits_no_offset(self, gate):
        assert "offset" not in gate.expression("onestartblk").group("named")
        assert [r.number for r in gate.pdf.block("onestartblk")] == [1, 2]

    def test_lineno_start_zero_and_thousand(self, gate):
        assert [r.number for r in gate.pdf.block("zerostartblk")] == [0, 1]
        assert [r.number for r in gate.pdf.block("bigstartblk")] == [1000, 1001]


class TestEmphasizedLines:
    def test_emphasize_alone_highlights_exactly_line_two(self, gate):
        assert ", highlighted: (2,)" in gate.expression("emphblk").group("named")
        assert _highlighted(gate, "emphblk") == [0, 1, 0, 0]

    def test_emphasize_with_lineno_start_highlights_displayed_eleven(self, gate):
        named = gate.expression("comboblk").group("named")
        assert ", offset: 9, highlighted: (11,)" in named
        rows = gate.pdf.block("comboblk")
        assert [row.number for row in rows] == [10, 11, 12]
        assert _highlighted(gate, "comboblk") == [0, 1, 0]
        assert rows[1].code.startswith("comboblk_b")

    def test_ranges_and_duplicates_highlight_each_line_once(self, gate):
        named = gate.expression("dedupeblk").group("named")
        assert ", highlighted: (2, 3, 4, 6)" in named
        assert _highlighted(gate, "dedupeblk") == [0, 1, 1, 1, 0, 1, 0]

    def test_out_of_range_line_warns_and_still_compiles(self, gate):
        assert "line number spec is out of range" in gate.result.stderr
        assert ", highlighted: (2,)" in gate.expression("rangeblk").group("named")
        assert _highlighted(gate, "rangeblk") == [0, 1, 0]

    def test_control_blocks_are_not_highlighted(self, gate):
        for token in ("nolnblk", "numonblk", "tenstartblk"):
            assert set(_highlighted(gate, token)) == {0}, token


class TestLanguages:
    def test_language_block_shows_python_badge(self, gate):
        for token in ("nolnblk", "numonblk", "singleblk", "listblk", "cellblk"):
            rows = gate.pdf.block(token)
            assert rows[0].badge == "Python", token
            assert all(row.badge == "" for row in rows[1:]), token
            assert gate.expression(token).group("lang") == "python"

    def test_no_language_renders_without_badge(self, gate):
        for token in ("nolangblk", "nonelangblk"):
            match = gate.expression(token)
            assert match.group("lang") is None, match.group(0)
            assert "lang:" not in match.group(0)
            rows = gate.pdf.block(token)
            assert len(rows) == 1
            assert rows[0].badge == "", token

    def test_doctest_block_keeps_python(self, gate):
        assert gate.expression("doctestblk").group("lang") == "python"
        rows = gate.pdf.block("doctestblk")
        assert rows[0].badge == "Python"


class TestEmptyAndSingleLine:
    def test_empty_block_renders_one_row_with_badge(self, gate):
        expected = (
            'codly.new(raw("", block: true, lang: "python"), '
            "number-enabled: false, skip-last-empty: false)"
        )
        assert expected in [m.group(0) for m in gate.expressions]
        before = gate.pdf.row_with("EMPTYBEFOREMARK")
        after = gate.pdf.row_with("EMPTYAFTERMARK")
        assert before.page == after.page
        between = [
            row
            for row in gate.pdf.rows
            if row.page == before.page and after.y < row.y < before.y
        ]
        assert [row.badge for row in between] == ["Python"]
        assert all(not row.body_runs for row in between)
        code_x = gate.pdf.block("singleblk")[0].code_x
        row_fills = [
            f
            for f in gate.pdf.fills
            if f.page == before.page
            and after.y < f.y0
            and f.y1 < before.y
            and f.x0 <= code_x <= f.x1
            and f.y1 - f.y0 < MAX_ROW_FILL_HEIGHT
        ]
        assert len(row_fills) == 1, row_fills

    def test_single_line_block(self, gate):
        rows = gate.pdf.block("singleblk")
        assert len(rows) == 1
        assert rows[0].badge == "Python"
        assert rows[0].code.replace(" ", "") == 'singleblk_a="onlyline"'

    def test_literalinclude_trailing_newline_adds_no_row(self, gate):
        text = TAB_SNIPPET.read_text(encoding="utf-8")
        assert text.endswith("\n")
        match = gate.expression("inclblk")
        assert decode_typst_string(match.group("code")) == text
        rows = gate.pdf.block("inclblk")
        assert [row.number for row in rows] == [1, 2]
        following = gate.pdf.rows[gate.pdf.rows.index(rows[-1]) + 1]
        assert following.number is None, following.text


def _rendered_line_pattern(line: str) -> str:
    """Regex for one source line as pypdf extracts it from the PDF.

    A tab renders as whitespace (Typst lays tabs out as spaces, C4). A
    non-ASCII character extracts as itself where a font covers it, and as
    exactly one NUL -- Typst's .notdef glyph -- where none does: typst-py's
    embedded fonts have no CJK or emoji coverage, so the ubuntu and windows
    CI runners render those code points as tofu (see
    tests/test_diagraph_escaping_render_gate.py). Byte identity of every
    character is proven on the emitted .typ string instead.
    """
    parts = []
    for ch in line:
        if ch == "\t":
            parts.append("[ \t]+")
        elif ord(ch) > 127:
            parts.append(f"(?:{re.escape(ch)}|\x00)")
        else:
            parts.append(re.escape(ch))
    return "".join(parts)


class TestEncoding:
    def test_raw_string_decodes_to_source_bytes(self, gate):
        # read_text (universal newlines) -- Sphinx reads the include the same
        # way, so a CRLF checkout compares equal too.
        source = ENCODING_SNIPPET.read_text(encoding="utf-8")
        for needle in ('"', "\\", "`", "```", "````", "#", "$", "\t", "日本語", "😀"):
            assert needle in source, needle
        assert re.search(r"[ \t]\n", source), "no trailing whitespace in snippet"
        match = gate.expression("enc_quote")
        decoded = decode_typst_string(match.group("code"))
        assert decoded == source
        block = next(b for b in gate.blocks if "enc_quote" in b.astext())
        assert decoded == block.astext()

    @staticmethod
    def _assert_rows_match_source(pdf: Pdf) -> None:
        lines = ENCODING_SNIPPET.read_text(encoding="utf-8").split("\n")
        assert lines[-1] == ""
        lines = lines[:-1]
        first = pdf.block("enc_quote")[0]
        rows = pdf.rows[pdf.rows.index(first) :][: len(lines)]
        for row, line in zip(rows, lines, strict=True):
            assert re.fullmatch(_rendered_line_pattern(line), row.code), (
                line,
                row.code,
            )

    def test_pdf_text_equals_source_with_tabs_as_whitespace(self, gate):
        self._assert_rows_match_source(gate.pdf)

    def test_pdf_text_with_embedded_fonts_only(self, gate, tmp_path):
        """The CI case: no system font covers CJK or emoji."""
        pdf_path = tmp_path / "embedded-fonts-only.pdf"
        typst.compile(
            str(gate.outdir / "master.typ"),
            output=str(pdf_path),
            root=str(gate.outdir),
            ignore_system_fonts=True,
        )
        self._assert_rows_match_source(_read_pdf(pdf_path))


class TestCaptionedListings:
    def _text(self, gate: Gate) -> str:
        return "\n".join(row.text for row in gate.pdf.rows)

    def test_listings_and_figure_are_numbered_separately(self, gate):
        text = self._text(gate)
        first = text.index("Listing 1: Capone first listing")
        figure = text.index("Figure 1: Figcap image figure")
        second = text.index("Listing 2: Cap ]br #x $m$")
        assert first < figure < second
        assert "Listing 3" not in text
        assert "Figure 2" not in text

    def test_captioned_blocks_are_raw_kind_figures(self, gate):
        for match in gate.expressions:
            if "capblk" in match.group("code"):
                assert gate.typ[: match.start()].endswith("figure(")
                assert gate.typ[match.end() :].startswith(", caption: text(")
        assert gate.typ.count("figure(codly.new(") == 2
        assert 'caption: text("Cap ]br #x $m$"), kind: raw)' in gate.typ

    def test_numref_and_ref_resolve(self, gate):
        text = self._text(gate)
        assert "Reference by number: NUMREFSENT 1." in text
        assert "Reference by name: Cap ]br #x $m$." in text

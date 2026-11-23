"""
Real-compile gate for the nodes issue #194 reported as fatal under ``typstpdf``.

At a31fd6ca an rST option list, a definition-list classifier or a Sphinx
``productionlist`` had no Typst visitor: ``unknown_visit`` warned and
descended, so the children's code-mode expressions were juxtaposed in the
``#{ ... }`` body and ``typst.compile()`` aborted the whole master with
``TypstError: expected semicolon or line break``. This gate builds one small
fixture project per construct under ``tests/fixtures/unhandled_nodes_render_gate/``
through ``-b typstpdf`` (the only path that compiles) and asserts:

- SC1 option lists render as ``terms(...)`` with monospace options, italic
  monospace arguments, ``, `` joins and docutils' delimiters preserved;
- SC2 classifiers sit inside their own ``terms.item`` term as `` : `` + italics;
- SC3 productionlists render as a three-column monospace ``grid(...)`` whose
  productions carry anchors that ``:token:`` references link to;
- SC4 a test-only visitor-less node still warns, still shows its text, and
  no longer breaks the compile in any placement.

Every build runs under ``LC_ALL=C`` because the ``unknown node type`` warning
text is asserted (CI runs in English).
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

from pypdf import PdfReader

FIXTURES = Path(__file__).parent / "fixtures" / "unhandled_nodes_render_gate"

pytestmark = pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the unhandled-nodes render gate",
)


class _Build:
    """The result of one ``-b typstpdf`` fixture build."""

    def __init__(self, result: subprocess.CompletedProcess, outdir: Path) -> None:
        self.result = result
        self.outdir = outdir

    @property
    def output(self) -> str:
        return self.result.stdout + self.result.stderr

    @property
    def typ(self) -> str:
        return (self.outdir / "index.typ").read_text(encoding="utf-8")

    @property
    def pdf_path(self) -> Path:
        return self.outdir / "master.pdf"

    def pdf_text(self) -> str:
        reader = PdfReader(self.pdf_path)
        return "\n".join(page.extract_text() for page in reader.pages)

    def pdf_link_count(self) -> int:
        reader = PdfReader(self.pdf_path)
        count = 0
        for page in reader.pages:
            for annot in page.get("/Annots") or []:
                if annot.get_object().get("/Subtype") == "/Link":
                    count += 1
        return count

    def unknown_warnings(self) -> list[str]:
        return [
            line for line in self.output.splitlines() if "unknown node type" in line
        ]


def _build(name: str, outdir: Path) -> _Build:
    """
    Build fixture ``name`` with ``sys.executable -m sphinx -b typstpdf -E``
    under ``LC_ALL=C`` and return the captured result.
    """
    env = dict(os.environ, LC_ALL="C", LANG="C")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            "-E",
            str(FIXTURES / name),
            str(outdir),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    return _Build(result, outdir)


def _assert_compiled(build: _Build) -> None:
    assert build.result.returncode == 0, (
        "sphinx-build -b typstpdf failed:\n"
        f"stdout: {build.result.stdout}\nstderr: {build.result.stderr}"
    )
    assert "expected semicolon or line break" not in build.output, build.output
    assert "Typst compilation failed" not in build.output, build.output
    assert build.pdf_path.exists(), f"master.pdf missing:\n{build.output}"
    assert build.pdf_path.read_bytes()[:4] == b"%PDF"


@pytest.fixture(scope="module")
def option_list_build(tmp_path_factory):
    return _build("option_list", tmp_path_factory.mktemp("option_list"))


@pytest.fixture(scope="module")
def classifier_build(tmp_path_factory):
    return _build("classifier", tmp_path_factory.mktemp("classifier"))


@pytest.fixture(scope="module")
def productionlist_build(tmp_path_factory):
    return _build("productionlist", tmp_path_factory.mktemp("productionlist"))


@pytest.fixture(scope="module")
def fallback_build(tmp_path_factory):
    return _build("fallback", tmp_path_factory.mktemp("fallback"))


class TestOptionList:
    """SC1 (E1-E3): option lists render as ``terms(...)``."""

    def test_compiles_without_unknown_node_warning(self, option_list_build):
        _assert_compiled(option_list_build)
        assert option_list_build.unknown_warnings() == []

    def test_single_item_between_paragraphs(self, option_list_build):
        typ = option_list_build.typ
        assert (
            'par({text("Paragraph before the single option.")})\n\n'
            'terms(separator: linebreak(), terms.item(raw("-a"), '
            '{par({text("option a")})}))\n\n'
            'par({text("Paragraph after the single option.")})'
        ) in typ

    def test_group_options_arguments_and_delimiters(self, option_list_build):
        typ = option_list_build.typ
        assert (
            'terms.item(raw("-c") + raw(" ") + emph(raw("FILE")) + text(", ") + '
            'raw("--see") + raw("=") + emph(raw("FILE")), '
            '{par({text("Read the config from FILE.")})})'
        ) in typ
        assert 'terms.item(raw("-v") + text(", ") + raw("--verbose"), ' in typ
        assert 'terms.item(raw("--long-only"), ' in typ

    def test_escaped_description(self, option_list_build):
        assert (
            r'text("Description with \"quotes\", back\\slash and #hash.")'
            in option_list_build.typ
        )

    def test_pdf_text(self, option_list_build):
        text = option_list_build.pdf_text()
        for expected in (
            "-a",
            "option a",
            "-c FILE, --see=FILE",
            "Read the config from FILE.",
            "-v, --verbose",
            "--long-only",
            'Description with "quotes", back\\slash and #hash.',
        ):
            assert expected in text, f"{expected!r} missing from PDF text:\n{text}"


class TestClassifier:
    """SC2 (E4, E5): classifiers render inside their term."""

    def test_compiles_without_unknown_node_warning(self, classifier_build):
        _assert_compiled(classifier_build)
        assert classifier_build.unknown_warnings() == []

    def test_classifiers_inside_term_in_source_order(self, classifier_build):
        typ = classifier_build.typ
        assert (
            'terms(separator: linebreak(), terms.item(text("term") + text(" : ") + '
            'emph(text("c1")) + text(" : ") + emph(text("c2")), '
        ) in typ
        assert 'terms.item(text("plain"), ' in typ
        # Nothing is emitted before the terms(...) call any more.
        assert 'text("c1")terms(' not in typ

    def test_inline_markup_kept_inside_term(self, classifier_build):
        assert (
            'terms.item(text("marked") + text(" : ") + '
            'emph(emph({text("emphasis")}) + text(" classifier")) + text(" : ") + '
            'emph(raw("literal") + text(" classifier")), '
        ) in classifier_build.typ

    def test_pdf_text(self, classifier_build):
        text = classifier_build.pdf_text()
        assert "term : c1 : c2" in text, text
        assert "marked : emphasis classifier : literal classifier" in text, text


class TestProductionlist:
    """SC3 (E6, E7): productionlists render as an anchored grammar grid."""

    def test_compiles_without_unknown_node_warning(self, productionlist_build):
        _assert_compiled(productionlist_build)
        assert productionlist_build.unknown_warnings() == []

    def test_three_column_grid_with_continuations(self, productionlist_build):
        typ = productionlist_build.typ
        assert (
            "grid(columns: 3, column-gutter: 6pt, row-gutter: 8pt, "
            '[#raw("expr") <index:grammar-token-expr>], raw("::="), '
            'link(<index:grammar-token-term>, raw("term")) + raw(" (\\"+\\" ") + '
        ) in typ
        assert (
            '[#raw("factor") <index:grammar-token-factor>], raw("::="), '
            'raw("NUMBER"), '
            '[], [], raw("| \\"(\\" ") + link(<index:grammar-token-expr>, '
            'raw("expr")) + raw(" \\")\\""), '
            '[], [], raw("| \\"-\\" ") + link(<index:grammar-token-factor>, '
            'raw("factor")))'
        ) in typ

    def test_group_named_productionlist(self, productionlist_build):
        assert (
            '[#raw("stmt") <index:grammar-token-grp-stmt>], raw("::="), '
            'raw("expr") + raw(" \\";\\""))'
        ) in productionlist_build.typ

    def test_token_references(self, productionlist_build):
        typ = productionlist_build.typ
        assert 'link(<index:grammar-token-expr>, \nraw("expr"))' in typ
        assert 'link(<index:grammar-token-grp-stmt>, \nraw("grp:stmt"))' in typ
        # An unresolved :token: is plain monospace text, never a link.
        assert 'raw("nosuchtoken")' in typ
        assert "nosuchtoken>" not in typ
        assert productionlist_build.pdf_link_count() >= 2

    def test_pdf_text(self, productionlist_build):
        text = productionlist_build.pdf_text()
        for expected in (
            'expr ::= term ("+" term)*',
            "factor ::= NUMBER",
            '| "(" expr ")"',
            '| "-" factor',
            'stmt ::= expr ";"',
            "nosuchtoken",
        ):
            assert expected in text, f"{expected!r} missing from PDF text:\n{text}"


class TestUnknownVisitFallback:
    """SC4 (E8, N1, N2): visitor-less nodes still warn and still compile."""

    PLACEMENTS = (
        "head",
        "para",
        "parastart",
        "body",
        "bodynext",
        "item",
        "itemstart",
        "itemblock",
        "cell",
        "cellonly",
        "cellblock",
        "cellafter",
        "term",
        "defblock",
    )

    def test_compiles(self, fallback_build):
        _assert_compiled(fallback_build)

    def test_warning_kept_for_every_placement(self, fallback_build):
        warnings = "\n".join(fallback_build.unknown_warnings())
        for word in self.PLACEMENTS:
            assert f">{word}-alpha <literal>{word}-beta</literal></unknown_" in (
                warnings
            ), f"no unknown node type warning for {word!r}:\n{warnings}"

    def test_body_level_children_are_separated(self, fallback_build):
        typ = fallback_build.typ
        assert '\ntext("body-alpha ")\nraw("body-beta")\n' in typ
        assert 'raw("body-beta")text(' not in typ
        assert '{text("cellblock-alpha ")\nraw("cellblock-beta")' in typ

    def test_text_in_pdf_for_every_placement(self, fallback_build):
        text = fallback_build.pdf_text()
        for word in self.PLACEMENTS:
            assert f"{word}-alpha" in text, f"{word}-alpha missing:\n{text}"
            assert f"{word}-beta" in text, f"{word}-beta missing:\n{text}"

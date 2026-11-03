"""
M004 SC5/SC8: build gate for the shipped ``examples/basic`` and
``examples/advanced`` samples.

SC5: a ``typstpdf`` build of each sample, straight from the shipped tree
into ``tmp_path``, exits 0 and produces a non-empty ``%PDF`` file for every
``typst_documents`` target (``TypstPDFBuilder.finish()`` raises on a compile
failure, so exit 0 plus a real PDF is a genuine compile signal).

SC8 (doc-audit queue rows 2 and 3, fix-doc): ``examples/advanced/README.md``
claims are checked against what the translator actually emits in a
``typst`` build of the sample -- the README's quoted inline-math form is
READ FROM THE README (never hard-coded here) and must occur verbatim in the
emitted content, and a seealso admonition renders through ``tip(`` and not
``info(``. The sample has no seealso of its own, so that half builds a
``tmp_path`` copy of the sample with one appended.

Every build writes only under ``tmp_path``; nothing is written inside
``examples/``. Assertions compare emitted text only (no paths, no colour
codes), keeping the gate OS-neutral.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[1]
BASIC_DIR = REPO_ROOT / "examples" / "basic"
ADVANCED_DIR = REPO_ROOT / "examples" / "advanced"
ADVANCED_README = ADVANCED_DIR / "README.md"

# Each sample's typst_documents target names (conf.py), as PDF basenames.
EXPECTED_PDFS = {
    "basic": (BASIC_DIR, ["basic-example.pdf"]),
    "advanced": (ADVANCED_DIR, ["advanced-example.pdf"]),
}


def _run_sphinx(builder: str, src: Path, out: Path) -> subprocess.CompletedProcess:
    """Run ``sys.executable -m sphinx -E -b <builder> <src> <out>``."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-E", "-b", builder, str(src), str(out)],
        capture_output=True,
        text=True,
    )


def _assert_ok(result: subprocess.CompletedProcess, label: str) -> None:
    assert result.returncode == 0, (
        f"sphinx-build failed for {label}:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def _content_text(out: Path) -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(out.rglob("*.typ")))


def _readme_inline_math_form() -> str:
    """The inline-math form the README quotes after ``**Inline:** ... →``."""
    readme = ADVANCED_README.read_text(encoding="utf-8")
    match = re.search(r"^\*\*Inline:\*\*.*?→ ``(.+?)``", readme, re.MULTILINE)
    assert match, "README.md no longer quotes an **Inline:** math form"
    return match.group(1).strip()


@pytest.mark.skipif(
    not TYPST_AVAILABLE, reason="typst-py is required for the typstpdf gate"
)
@pytest.mark.parametrize("sample", sorted(EXPECTED_PDFS))
def test_example_typstpdf_build_produces_pdf(sample, tmp_path):
    src, pdf_names = EXPECTED_PDFS[sample]
    out = tmp_path / "pdf"
    result = _run_sphinx("typstpdf", src, out)
    _assert_ok(result, f"examples/{sample}")
    for name in pdf_names:
        pdf = out / name
        assert pdf.is_file(), f"{name} was not produced for examples/{sample}"
        data = pdf.read_bytes()
        assert data[:4] == b"%PDF", f"{name} is not a PDF"
        assert len(data) > 4, f"{name} is empty"


def test_advanced_readme_inline_math_form_is_emitted(tmp_path):
    form = _readme_inline_math_form()
    assert not form.startswith("#"), f"README still shows a markup form: {form!r}"
    out = tmp_path / "typ"
    _assert_ok(_run_sphinx("typst", ADVANCED_DIR, out), "examples/advanced")
    assert form in _content_text(out), (
        f"README's inline-math form {form!r} does not occur in the emitted "
        f"content of examples/advanced"
    )


def test_advanced_seealso_renders_through_tip(tmp_path):
    src = tmp_path / "src"
    shutil.copytree(
        ADVANCED_DIR, src, ignore=shutil.ignore_patterns("__pycache__", "_build")
    )
    index = src / "index.rst"
    index.write_text(
        index.read_text(encoding="utf-8") + "\n.. seealso::\n   Seealso probe body.\n",
        encoding="utf-8",
    )
    out = tmp_path / "typ"
    _assert_ok(_run_sphinx("typst", src, out), "examples/advanced copy")
    text = (out / "index.typ").read_text(encoding="utf-8")
    probe = text.index("Seealso probe body.")
    head = text[:probe]
    call_start = max(head.rfind("tip("), head.rfind("info("))
    assert call_start != -1, "seealso body is not inside an admonition call"
    assert head[call_start:].startswith("tip("), (
        "seealso is not rendered through tip(): " f"{text[call_start:probe + 40]!r}"
    )

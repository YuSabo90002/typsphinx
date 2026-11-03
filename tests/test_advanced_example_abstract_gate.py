"""
M007 SC2: the ``ieee_abstract`` example in ``docs/source/examples/advanced.rst``
must not carry embedded newlines.

A Typst string renders a newline as a hard line break, so a triple-quoted
multi-line ``ieee_abstract`` passed through
``TemplateEngine._format_typst_value`` shows stray breaks in the abstract
(at the start, mid-sentence and at the end). M006 fixed the same pattern in
``examples/charged-ieee/approach1/conf.py`` (commit 3c23c646); this gate pins
the documentation example to the same single-line form.

The ``ieee_abstract`` assignment is located by parsing the code block with
``ast`` and its right-hand side is evaluated with ``ast.literal_eval`` -- the
block is never executed.
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

from typsphinx.template_engine import TemplateEngine

ADVANCED_RST = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "source"
    / "examples"
    / "advanced.rst"
)

EXPECTED_WORDS = (
    "This paper presents novel approaches to machine learning "
    "applications in computer vision."
).split()


def _code_blocks(text: str) -> list[str]:
    """Return the dedented bodies of every ``.. code-block::`` in *text*."""
    lines = text.splitlines()
    blocks: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith(".. code-block::"):
            directive_indent = len(lines[i]) - len(lines[i].lstrip())
            body: list[str] = []
            i += 1
            while i < len(lines):
                line = lines[i]
                if line.strip() and (
                    len(line) - len(line.lstrip()) <= directive_indent
                ):
                    break
                body.append(line)
                i += 1
            blocks.append(textwrap.dedent("\n".join(body)).strip("\n"))
            continue
        i += 1
    return blocks


def _ieee_abstract_value() -> str:
    text = ADVANCED_RST.read_text(encoding="utf-8")
    for block in _code_blocks(text):
        if "ieee_abstract" not in block:
            continue
        tree = ast.parse(block)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "ieee_abstract"
            ):
                value = ast.literal_eval(node.value)
                assert isinstance(value, str)
                return value
    raise AssertionError(f"no ieee_abstract assignment found in {ADVANCED_RST}")


def test_ieee_abstract_has_no_embedded_newline() -> None:
    value = _ieee_abstract_value()
    assert "\n" not in value
    assert "\r" not in value


def test_ieee_abstract_keeps_the_same_words() -> None:
    assert _ieee_abstract_value().split() == EXPECTED_WORDS


def test_formatted_ieee_abstract_has_no_line_break() -> None:
    formatted = TemplateEngine()._format_typst_value(_ieee_abstract_value())
    assert "\n" not in formatted
    assert "\r" not in formatted
    assert formatted == '"' + " ".join(EXPECTED_WORDS) + '"'

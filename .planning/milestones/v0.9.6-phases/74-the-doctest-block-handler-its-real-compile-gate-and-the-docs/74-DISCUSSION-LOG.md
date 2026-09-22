# Phase 74: The `doctest_block` Handler, Its Real-Compile Gate, and the Docstring reST Errors - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-19
**Phase:** 74-the-doctest-block-handler-its-real-compile-gate-and-the-docstring-rest-errors
**Areas discussed:** Language tag, Handler implementation shape

Gray areas presented: Language tag; Handler implementation shape; QUA-14 fix granularity; GATE-01
fixture structure. The owner selected the first two.

Pre-discussion measurement (this session): five fences through `typst.compile()` — `pycon`, none,
`text`, `bogusxyz` byte-identical (11531 B, `5428a015b02591d5`), `python` distinct (12654 B,
`9bb09e20e0d2d05a`); `codly-languages` 0.1.10 has `python` and no `pycon`. SVG per-glyph census
was run before the first question and quoted in the option descriptions.

---

## Language tag

| Option | Description | Selected |
|--------|-------------|----------|
| python | 28 function-name glyphs blue, 24 string glyphs green, `>>>` red, 3 punctuation black; codly "Python" label/icon; output lines coloured as Python source | ✓ |
| pycon | all 58 glyphs black; byte-identical to no tag; no codly entry; semantically accurate per Pygments/Sphinx | |
| text | black, byte-identical; codly "Plain Text" label; states "no highlighting" explicitly | |

**User's choice:** python

| Option | Description | Selected |
|--------|-------------|----------|
| Honour existing value (Recommended) | use non-empty `node["language"]`, else python | ✓ |
| Always python | ignore any existing value | |

**User's choice:** Honour existing value. **Notes:** `highlight_language` not followed — Sphinx
itself rewrites `>>>`-led blocks to `pycon` (`sphinx/highlighting.py:148-151`).

---

## Handler implementation shape

| Option | Description | Selected |
|--------|-------------|----------|
| Branch on the literal side (Recommended) | delegating handlers; language line falls back to python for doctest_block; no doctree mutation; literal_block byte-unchanged | ✓ |
| Inject into node and delegate | write `node["language"] = "python"` then delegate | |
| Standalone handler | separate visit/depart; duplicates separator/anchor/flag discipline | |

**User's choice:** Branch on the literal side

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit methods (Recommended) | typed delegating visit/depart with docstrings; widen literal annotations to a union (html5 shape) | ✓ |
| Class-attribute alias | two-line alias (latex/texinfo shape) | |

**User's choice:** Explicit methods

| Option | Description | Selected |
|--------|-------------|----------|
| Whole output-tree diff (Recommended) | diff base vs tip clean `-b typst` trees; every hunk must be a doctest region or a QUA-14 docstring region | ✓ |
| Existing suite green suffices | rely on literal_block render gates | |

**User's choice:** Whole output-tree diff

---

## Claude's Discretion

- QUA-14 fix granularity: minimal blank-line/indentation repair, census-driven over the whole tree, no new guard test.
- GATE-01 fixture structure: one module, one synthetic fixture root, module-scoped `-b typstpdf` build, both contexts, (b) at non-first position; pypdf optional; optional unit test for the honour path.

## Deferred Ideas

None raised. Reviewed-not-folded todos recorded in CONTEXT.md `<deferred>`.

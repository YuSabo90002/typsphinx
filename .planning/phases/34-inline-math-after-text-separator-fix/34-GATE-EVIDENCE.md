# Phase 34 GATE-01 Evidence: RED -> GREEN Record

<!-- Section headings below use an em-dash (—), matching 34-01-PLAN.md's
     required literal headings verbatim. -->


This file is the phase's RED->GREEN evidence record for MATH-01 / backlog 999.1
(GATE-01). Plan 01 appends the RED sections below. Plan 02 (the fix) and Plan 03
(the regression sweep) append their own GREEN sections to this same file.

## RED — pre-fix run (SC#4, D-02)

- **Commit measured:** `26f8395ba55e4dd851e07046b6bab42bb5222939` (Plan 01 Task 2's
  commit, `test(34-01): add GATE-01 gate test module for both math emission paths`
  -- `typsphinx/` is untouched at this commit; `git status --porcelain typsphinx/`
  is empty).
- **Date:** 2026-07-28T13:45:10Z
- **Commands:**
  ```
  uv run pytest tests/test_inline_math_after_text_render_gate.py -q --tb=long
  ```
  and, for the isolated per-construct capture:
  ```
  uv run python -m sphinx -b typstpdf tests/fixtures/inline_math_after_text_render_gate <scratch>/mitex
  uv run python -m sphinx -b typstpdf -D typst_use_mitex=0 tests/fixtures/inline_math_after_text_render_gate <scratch>/native
  ```

### Verbatim pytest failure output

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3db2c6f1abcca4d1
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests/test_inline_math_after_text_render_gate.py FF                      [100%]

=================================== FAILURES ===================================
_ TestInlineMathAfterTextRenderGate.test_typstpdf_separates_inline_math_mitex_path _

    def test_typstpdf_separates_inline_math_mitex_path(
        self, inline_math_after_text_render_gate_dir, temp_build_dir
    ):
        """Build the fixture with the mitex default and confirm every
        construct compiles, separates correctly, and round-trips through the
        PDF text extraction."""
        result = _run_sphinx_build_typstpdf(
            inline_math_after_text_render_gate_dir, temp_build_dir
        )

        # 1. The build must exit cleanly.
>       assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
E       AssertionError: sphinx-build -b typstpdf failed:
E         stdout: Sphinx v9.1.0 ...(build progress, omitted for brevity)...
E         stderr: Typst compilation failed at .../index.typ: TypstError: expected semicolon or line break
E         ERROR: Failed to compile .../index.typ: Typst compilation failed: TypstError: expected semicolon or line break
E         Location: .../index.typ
E         Details: expected semicolon or line break
E         ...
E         sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: expected semicolon or line break
E         Location: .../index.typ
E         Details: expected semicolon or line break
E       assert 2 == 0
E        +  where 2 = CompletedProcess(...).returncode

tests/test_inline_math_after_text_render_gate.py:127: AssertionError
_ TestInlineMathAfterTextRenderGate.test_typstpdf_separates_inline_math_native_path _

    def test_typstpdf_separates_inline_math_native_path(
        self, inline_math_after_text_render_gate_dir, temp_build_dir
    ):
        """Build the SAME fixture with ``-D typst_use_mitex=0`` (the native
        ``$...$`` math path) and confirm the same separator correctness."""
        result = _run_sphinx_build_typstpdf(
            inline_math_after_text_render_gate_dir,
            temp_build_dir,
            extra_args=("-D", "typst_use_mitex=0"),
        )

        # 1. The build must exit cleanly, with the same fatal signatures
        # absent.
>       assert result.returncode == 0, (
            f"sphinx-build -b typstpdf (native math) failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
E       AssertionError: sphinx-build -b typstpdf (native math) failed:
E         stderr: Typst compilation failed at .../index.typ: TypstError: expected semicolon or line break
E         ERROR: Failed to compile .../index.typ: Typst compilation failed: TypstError: expected semicolon or line break
E         Location: .../index.typ
E         Details: expected semicolon or line break
E       assert 2 == 0
E        +  where 2 = CompletedProcess(...).returncode

tests/test_inline_math_after_text_render_gate.py:273: AssertionError
=========================== short test summary info ============================
FAILED tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_mitex_path
FAILED tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_native_path
============================== 2 failed in 0.56s ===============================
```

Both failures are on the `result.returncode == 0` assertion (step 1 of each
test method), driven by a real `TypstError: expected semicolon or line break`
raised out of `TypstPDFBuilder.finish()` -- NOT a collection error, ImportError,
missing-fixture error, or a skip. RED confirmed against the unfixed translator.

## RED — verbatim Typst errors

All four subsections below were measured directly (not via pytest) by building
the fixture to a scratch directory once per path:
`uv run python -m sphinx -b typstpdf tests/fixtures/inline_math_after_text_render_gate <scratch>/mitex`
and the same command plus `-D typst_use_mitex=0` to `<scratch>/native`. Both
paths independently raise the identical `TypstError: expected semicolon or line
break` (Typst reports only the first parse failure it reaches, but the emitted
`.typ` -- produced by `write_doc` before `finish()` aborts -- shows every
juxtaposed construct simultaneously; see the reproduction matrix below).

### Construct B -- bullet list item (mitex path)

Verbatim Typst error (mitex build):
```
Typst compilation failed at <scratch>/mitex/index.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <scratch>/mitex/index.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <scratch>/mitex/index.typ
Details: expected semicolon or line break
```

Verbatim juxtaposed line from the emitted `<scratch>/mitex/index.typ`:
```
text("Text before math ")mi(`E=mc^2`)
```

Verbatim juxtaposed line from `<scratch>/native/index.typ` (native path,
identical shape with the mitex call swapped for the native span):
```
text("Text before math ")$E=mc^2$
```

### Construct C -- collapsed confval field body (mitex path)

Verbatim juxtaposed line from `<scratch>/mitex/index.typ` (the `:default:`
field body -- prose then math following a sibling):
```
text("The value of ")mi(`x`) + text(" computed inline")
```
The `:type:` field body (math as the sole/first expression) emits cleanly with
no leading operator, confirming the boundary edge does NOT need a fix:
```
mi(`x`)
```
Native-path equivalent from `<scratch>/native/index.typ`:
```
text("The value of ")$x$ + text(" computed inline")
```

### Construct D -- definition-list term (mitex path)

Verbatim juxtaposed line from `<scratch>/mitex/index.typ`:
```
terms(separator: linebreak(), terms.item(text("Term ")mi(`E=mc^2`), {par({text("Definition body text.")})}))
```
Native-path equivalent from `<scratch>/native/index.typ`:
```
terms(separator: linebreak(), terms.item(text("Term ")$E=mc^2$, {par({text("Definition body text.")})}))
```

### Construct E -- display math in a list item, `visit_math_block` (mitex path)

Verbatim juxtaposed line from `<scratch>/mitex/index.typ`:
```
text("Text before block math.")mitex(`E = mc^2`)
```
Native-path equivalent from `<scratch>/native/index.typ`:
```
text("Text before block math.")$ E = mc^2 $
```

All four measurements match RESEARCH.md's "Code Examples" section exactly (same
juxtaposition shape, same `expected semicolon or line break` Typst error).

## RED — construct reproduction matrix

| Construct | Context | Path | Reproduced fatal? | Evidence pointer |
|-----------|---------|------|--------------------|-------------------|
| A -- top-level paragraph (control) | `par({...})`, `in_paragraph=True` | mitex + native | **no** (Pitfall 1 control -- already works; `par({text("With space before math: ")\nmi(`E=mc^2`)\ntext(" after.")})` emitted byte-identically) | `<scratch>/mitex/index.typ` lines 24-26, `<scratch>/native/index.typ` lines 24-26 |
| B -- bullet list item | `list({...})`, `in_list_item=True` | mitex + native | **yes** | "RED -- verbatim Typst errors" > Construct B above |
| C -- collapsed confval field body (`:default:`) | inline-concat context (`_in_field_body`) | mitex + native | **yes** | "RED -- verbatim Typst errors" > Construct C above |
| C -- collapsed confval field body (`:type:`, sole math) | inline-concat context, first sibling | mitex + native | no (boundary edge already emits cleanly with no leading operator -- nothing to separate FROM) | `<scratch>/mitex/index.typ` line 50, `<scratch>/native/index.typ` line 50 |
| D -- definition-list term | inline-concat context (`_in_term`) | mitex + native | **yes** | "RED -- verbatim Typst errors" > Construct D above |
| E -- display math in a list item | `list({...})`, `in_list_item=True`, `visit_math_block` | mitex + native | **yes** | "RED -- verbatim Typst errors" > Construct E above |
| F -- list item, sole content is math | `list({...})`, first/only content | mitex + native | no (single-element edge -- no preceding sibling to juxtapose against; `list({\nparbreak()\nmi(`a+b`)\n})` emits cleanly) | `<scratch>/mitex/index.typ` lines 78-81, `<scratch>/native/index.typ` lines 78-81 |

D-02's bar (list-item construct B AND at least one concat-context construct C
or D reproducing the fatal) is met: B, C (`:default:`), D, and E all reproduce
the fatal; A and F do not (expected, per the boundary/edge analysis in
34-01-PLAN.md `must_haves`).

## Pre-fix full-suite baseline

- **Command:** `uv run pytest -q --tb=no -rf` (per-worktree provisioning per
  CLAUDE.md: `uv sync --extra dev` + the documented `.venv/bin/uv` symlink fix
  for the NixOS `stub-ld` ELF hazard, project memory "NixOS sandbox test env").
- **Result:** `2 failed, 647 passed, 1 skipped in 57.69s`
- **Failing node IDs (excluded from this baseline -- intentionally RED per
  SC#4, not counted as environmental noise):**
  - `tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_mitex_path`
  - `tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_native_path`
- **Sorted list of OTHER failing node IDs (the actual NixOS-environmental
  baseline Plan 03 must compare against):** none. With the `.venv/bin/uv`
  symlink fix applied (replacing the generic-linux ELF `uv` wheel installed by
  `uv sync` with a symlink to the Nix-store `uv`, per project memory), this run
  shows **zero** environmentally-failing tests -- the previously-documented
  "~45 integration tests fail purely environmentally" class (RESEARCH.md
  "Environment Availability") is not present in this run. The 1 skip is inside
  `tests/test_corpus_gate.py` (its own documented network-dependent skip,
  D-05), unrelated to this phase.
- **Consequence for Plan 03:** the expected clean full-suite state after the
  fix lands is `649 passed, 1 skipped, 0 failed` (the two gate tests flipping
  from FAILED to PASSED, nothing else changing). Any additional failure in
  Plan 03's post-fix run is a real regression, not environmental noise.

## GREEN — post-fix run (SC#4, D-02)

- **Commit measured:** `a737e16510081f940d897666ab5181a7df2da3f7` (Plan 02's
  third commit, `fix(34-02): GATE-01 fixture math content is invalid under
  native Typst` -- the final state of Plan 02: `visit_math` and
  `visit_math_block` both fixed, plus the deviation-fix documented below).
- **Date:** 2026-07-28T14:03:10Z
- **Commands (same as the RED section, verbatim):**
  ```
  uv run pytest tests/test_inline_math_after_text_render_gate.py -q --tb=long
  ```
  and, for the isolated per-construct capture:
  ```
  uv run python -m sphinx -b typstpdf tests/fixtures/inline_math_after_text_render_gate <scratch>/mitex
  uv run python -m sphinx -b typstpdf -D typst_use_mitex=0 tests/fixtures/inline_math_after_text_render_gate <scratch>/native
  ```

### Verbatim pytest passing output

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab37272bc5ac642fb
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests/test_inline_math_after_text_render_gate.py ..                      [100%]

============================== 2 passed in 0.66s ===============================
```

Both direct scratch builds (mitex default and `-D typst_use_mitex=0`) exited
`0` with empty stderr -- no `TypstError`, no `Typst compilation failed`,
no `ExtensionError`. `<scratch>/mitex/index.pdf` and `<scratch>/native/index.pdf`
both exist, are non-empty (39939 bytes each), and begin with the `%PDF` magic
bytes.

### Per-commit sampling set (RESEARCH.md Validation Architecture)

```
uv run pytest tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py tests/test_inline_math_after_text_render_gate.py -q
```
Result: `25 passed in 0.73s` (23 pre-existing math-module tests + the 2
GATE-01 gate tests, all green, zero failures).

### Post-fix full-suite baseline

```
uv run pytest -q --tb=no -rf
```
Result: `649 passed, 1 skipped in 56.74s` -- exactly the state Plan 01's
RED section predicted as the consequence of a correct fix: the two gate
tests flipped from FAILED to PASSED, the pre-existing 1 skip
(`tests/test_corpus_gate.py`, D-05, unrelated) is unchanged, and there is
zero new failure anywhere in the 649-test corpus.

## GREEN — emitted separator per construct

One subsection per construct, showing the post-fix emitted line(s) side by
side with the pre-fix (RED) capture, on the path each was measured on. A
mid-plan deviation changed the fixture's math content from `E=mc^2` to
`E = m c^2` (see "Diff scope" below) -- the RED capture below is quoted from
Plan 01's original recording and therefore still shows the pre-deviation
`E=mc^2` spelling; the separator SHAPE (newline / `+` / absence of either)
is what this section verifies, and it is identical under both spellings.

### Construct B -- bullet list item

- RED (mitex, unfixed translator): `text("Text before math ")mi(`E=mc^2`)`
  -- juxtaposed, zero separator characters.
- GREEN (mitex, fixed translator, post-deviation content):
  ```
  text("Text before math ")
  mi(`E = m c^2`)
  ```
  -- exactly one newline separator.
- RED (native, unfixed translator): `text("Text before math ")$E=mc^2$`
  -- juxtaposed.
- GREEN (native, fixed translator, post-deviation content):
  ```
  text("Text before math ")
  $E = m c^2$
  ```
  -- exactly one newline separator.

### Construct C -- collapsed confval field body (`:default:`)

- RED (mitex): `text("The value of ")mi(`x`) + text(" computed inline")`
  -- missing the leading `+` between the prose sibling and the math call.
- GREEN (mitex, fixed translator): `text("The value of ") + mi(`x`) + text(" computed inline")`
  -- exactly one `+` separator inserted before the math call; content (`x`)
  is unaffected by the deviation fix (only `E=mc^2`-shaped constructs
  needed correction).
- GREEN (native, fixed translator): `text("The value of ") + $x$ + text(" computed inline")`
  -- same shape.
- The `:type:` field body (math as the sole/first expression) still emits
  cleanly with **no** leading operator on both paths post-fix (`mi(`x`)` /
  `$x$` alone) -- confirming the boundary edge from Plan 01's RED matrix
  stays correct after the fix (no stray leading `+`).

### Construct D -- definition-list term

- RED (mitex): `terms(separator: linebreak(), terms.item(text("Term ")mi(`E=mc^2`), {par({text("Definition body text.")})}))`
  -- juxtaposed, missing `+`.
- GREEN (mitex, fixed translator, post-deviation content):
  ```
  terms(separator: linebreak(), terms.item(text("Term ") + mi(`E = m c^2`), {par({text("Definition body text.")})}))
  ```
  -- exactly one `+` separator.
- GREEN (native, fixed translator, post-deviation content):
  ```
  terms(separator: linebreak(), terms.item(text("Term ") + $E = m c^2$, {par({text("Definition body text.")})}))
  ```
  -- same shape.

### Construct E -- display math in a list item (`visit_math_block`)

- RED (mitex): `text("Text before block math.")mitex(`E = mc^2`)` -- juxtaposed
  (this construct's RED source already had the `E = mc^2` spacing form,
  unrelated to the D-01 fix or the deviation).
- GREEN (mitex, fixed translator, post-deviation content):
  ```
  text("Text before block math.")
  mitex(`E = m c^2`)
  ```
  -- exactly one newline separator.
- GREEN (native, fixed translator, post-deviation content):
  ```
  text("Text before block math.")
  $ E = m c^2 $
  ```
  -- exactly one newline separator.

### Construct A -- top-level paragraph (control, byte-identical)

- GREEN (mitex, fixed translator, post-deviation content):
  ```
  par({text("With space before math: ")
  mi(`E = m c^2`)
  text(" after.")})
  ```
  and
  ```
  par({text("No space where")
  mi(`E = m c^2`)
  text("immediately follows.")})
  ```
  -- identical shape to the RED capture (single newline, same as before the
  fix), confirming the fix does not double-separate the already-working
  top-level-paragraph path (RESEARCH.md Pitfall 1). Since Construct A never
  reproduced the fatal in RED (it is a regression guard, not a defect
  reproduction), there is no "before" juxtaposed line to diff against here
  -- the comparison is that the newline-separated shape is unchanged
  before and after the fix.

## RED → GREEN verdict

The gate `tests/test_inline_math_after_text_render_gate.py` (both
`test_typstpdf_separates_inline_math_mitex_path` and
`test_typstpdf_separates_inline_math_native_path`) **failed** against
commit `26f8395ba55e4dd851e07046b6bab42bb5222939` (Plan 01's unfixed
translator; RED section above) with `result.returncode == 2` and the
verbatim Typst error `TypstError: expected semicolon or line break`, and
**passes** against commit `a737e16510081f940d897666ab5181a7df2da3f7`
(Plan 02's fixed translator; this section) with `2 passed, 0 failed,
0 skipped`.

Constructs that flipped from a reproduced fatal (RED) to a correct,
exactly-one-separator emission (GREEN): **B** (bullet list item, both
paths), **C** `:default:` (collapsed confval field body concat context,
both paths), **D** (definition-list term concat context, both paths), and
**E** (display math in a list item, `visit_math_block`, both paths).
Constructs that did not reproduce the fatal in RED and remain
byte-identical/unregressed in GREEN: **A** (top-level paragraph control),
**C** `:type:` (math as first/sole expression in a concat context -- no
leading operator, before or after the fix), and **F** (list item whose
sole content is math -- no preceding sibling to separate from).

## Diff scope

```
$ git diff --stat af187d36c5bcbbdb0bb5cb03ddc9f37fa6fd7b5e..HEAD
 .../inline_math_after_text_render_gate/index.rst   | 10 ++---
 tests/test_inline_math_after_text_render_gate.py   | 17 ++++----
 typsphinx/translator.py                            | 45 ++++++++++++++++++++++
 3 files changed, 59 insertions(+), 13 deletions(-)
```

- `typsphinx/translator.py` -- the production fix (`visit_math`,
  `visit_math_block`), 45 insertions, 0 deletions, no lines removed.
- `tests/fixtures/inline_math_after_text_render_gate/index.rst` and
  `tests/test_inline_math_after_text_render_gate.py` -- the Plan 02
  deviation fix: `E=mc^2` -> `E = m c^2` throughout, so the fixture's math
  content is valid under real Typst native-math parsing (unrelated to the
  separator defect; see the deviation entry in `34-02-SUMMARY.md`). No
  exact-string assertion was weakened to a substring check -- only the
  literal math content changed, verified against real emitted bytes from a
  direct scratch build of both paths.
- **No file under `tests/test_math_*.py` was touched**
  (`git status --porcelain tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py`
  is empty at HEAD) and **no `@preview` version string changed**
  (`uv run pytest tests/test_preview_version_sync.py -q` -> `3 passed`).

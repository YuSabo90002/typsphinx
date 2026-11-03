---
id: T002
title: Prove codly 2.0 code blocks at the surface — option/edge/caption PDF gate and the four-project code-mode .typ gate
wave: 1
deps: [T001]
status: done
agent: build_T002
base: f02c214194731a8ba4b8a7415d1cf29afa9ebe50
worktree: null
task_branch: null
files:
  - tests/fixtures/codly2_render_gate
  - tests/test_codly2_render_gate.py
  - tests/test_codly2_output_gate.py
  - typsphinx/translator.py
  - tests/test_translator.py
---

# T002 — Prove codly 2.0 code blocks at the surface — option/edge/caption PDF gate and the four-project code-mode .typ gate

## Context

T001 lands the codly 2.0.0 deps.typ and the `codly.new(raw(...), ...)` emission (Interface contract below) with the old tests rewritten. This task proves the result where users see it: a purpose-made fixture compiled with `typstpdf` (line numbers on/off, `:lineno-start:`, `:emphasize-lines:` alone and combined with `:lineno-start:`, badges, empty and one-line blocks, encoding round-trip, captioned listings vs image figures, `:numref:`), and `typst` builds of `tests/roots/test-basic`, `examples/basic`, `examples/advanced` and `docs/source` checked for the code-mode shape and the absence of fences and `codly(` calls. Two SYNTHESIS rules are medium confidence and must be confirmed here before T003 builds the examples and docs: an empty/whitespace-only block gets `skip-last-empty: false` (otherwise codly renders a hairline with no row or badge) and a literalinclude whose text ends in a newline does not gain a spurious empty numbered row; Sphinx's `default` language (no argument, `highlight_language` unset) maps to no language, so no "default" badge appears. Research facts: codly 2.0 `highlighted` is keyed by displayed numbers and ignores out-of-range entries silently; duplicate entries shift the default palette, so the emission dedupes; Sphinx itself filters out-of-range `:emphasize-lines:` with a "line number spec is out of range" warning; `figure(codly.new(raw(...)))` is a `kind: raw` figure with supplement "Listing" on the listing counter, separate from image figures; Typst renders tabs as spaces in PDF text (C4).

## Approach

- Fixture `tests/fixtures/codly2_render_gate/` (conf.py with `extensions = ["typsphinx"]`, `numfig = True`, `highlight_language` left unset; index.rst; a literalinclude source file containing a tab, trailing whitespace and a trailing newline; a small image — an SVG text file is enough). Give each block a unique sentinel so tests can find its lines in PDF text; keep code lines from starting with digits so number detection is unambiguous.
- `tests/test_codly2_render_gate.py`: build the fixture once per module with `sys.executable -m sphinx -E -b typstpdf` (and `-b typst` where `.typ` is inspected) into `tmp_path_factory`; read PDF text with pypdf. Observe highlights in the compiled output, not only in `.typ` text: e.g. pypdf content-stream fill rectangles against text-line y positions, or `typst.compile(..., format="png")` of the built wrapper and per-row non-background detection — the coder chooses, but the check must fail if `highlighted` is empty, shifted by the offset, or carries an extra line. Compare structure (rows highlighted / not highlighted), never exact colour values, file paths or ANSI codes (CI runs ubuntu/windows/macos). Skip only through the existing `TYPST_AVAILABLE`/`PYPDF_AVAILABLE` style flags; the Verify installs both, so the run must report no skips.
- `tests/test_codly2_output_gate.py`: `typst` builds of the four projects (docs/source needs the docs extra: myst-parser, furo, sphinx-autodoc-typehints; graphviz-dependent docs gates already exist — follow how `tests/test_bibliography_docs_gate.py` builds the real docs tree). Content files = every `.typ` outside `_typsphinx/` and `_template/` that is not a `typst_documents` wrapper. Count literal_block + doctest_block nodes per document from the build's doctree pickles (`-d <doctrees>`) and assert the number of `codly.new(raw(` occurrences in that document's content file equals it, and that no other code-block form exists. For examples/basic, examples/advanced and docs/source the count must be > 0; test-basic has no code block and must show 0 `codly.new`.
- Absence checks over those content files: no ``` run, and no match of `(^|[^.a-z-])codly\(`. Bounded exception (pending owner ruling — see PLAN.md Dependency notes, LESSONS 002): in the docs/source build only, a `codly\(` match is tolerated when it lies inside an inline `raw("...")` string literal (not the first argument of `codly.new(`) in `changelog.typ` whose decoded text occurs verbatim in `CHANGELOG.md`; the test asserts every tolerated hit by that rule and fails on any other. If the owner rules the exemption out, this exception is removed and the two historical CHANGELOG lines are reworded instead (out of this task's files — report back).
- If a gate exposes an emission defect (e.g. the empty-block or `default` rule does not render as stated), fix it in `typsphinx/translator.py` only within T001's Interface contract and update `tests/test_translator.py` accordingly; a fix that needs a different contract shape is a `NEEDS-ORCHESTRATOR` block. Any translator change must keep T001's Verify passing.
- Docstring rule from T001 holds: no ``` and no bare `codly(` in docstrings of autodoc'd modules.

## Interface contract

- deps.typ (generated by `render_default_deps()`), import and init lines, exactly:
  - `#import "@preview/codly:2.0.0" as codly`
  - `#import "@preview/codly-languages:0.1.10": *` (other three import lines unchanged)
  - `#let typsphinx-init(body) = {` / `  show: codly.lang-set_(languages: codly-languages)` / `  body` / `}`
- One code block (literal_block or doctest_block), one code-mode expression, no leading `#`, no ``` fence, no `{`/`#{` wrapper, followed by a newline:
  `codly.new(raw("ESC", block: true[, lang: "LANG"])[, number-enabled: false][, offset: OFF][, highlighted: (H1, H2, ...)][, skip-last-empty: false])`
  - `ESC` = `escape_typst_string(node.astext())`
  - `, lang: "LANG"` omitted when the language is `""`, `"none"` or `"default"`; doctest_block without a language → `lang: "python"`
  - `number-enabled: false` iff `node["linenos"]` is false
  - `offset: OFF` with `OFF = linenostart - 1` iff linenos is true and `highlight_args["linenostart"]` is set and `!= 1`
  - `highlighted:` iff `hl_lines` is non-empty: `sorted(set(hl_lines))`, each plus `OFF` when an offset is emitted, separated by `, `; a single entry is `(K,)`
  - `skip-last-empty: false` iff `node.astext().strip() == ""`
  - named arguments appear in the order above
- Captioned code block (literal-block-wrapper container): `figure(<the codly.new expression>, caption: text("ESC_CAPTION"), kind: raw)` with `ESC_CAPTION = escape_typst_string(caption.astext())`; the figure carries no `<label>`; a `:name:` is anchored only by the `[#metadata(none) <LABEL>]` that `visit_container` emits before it.

## Intent coverage

- SC2
- SC3
- SC4

## Acceptance criteria

1. SC2: in the content `.typ` files of `typst` builds of `tests/roots/test-basic`, `examples/basic`, `examples/advanced` and `docs/source`, every literal_block and doctest_block (including those inside captioned figures, list items, admonitions and table cells — the fixture or projects must contain at least one of each context, the fixture supplying any the projects lack) is exactly one `codly.new(raw(...), ...)` expression; the per-document count of `codly.new(raw(` equals the doctree's literal_block + doctest_block count.
2. SC2 absence: over those same content files `grep -rn '```'` finds nothing and `grep -rnE '(^|[^.a-z-])codly\('` finds nothing except the AC3 exemption.
3. The only tolerated `codly\(` hits are inside inline `raw("...")` literals of docs/source `changelog.typ` whose decoded text occurs verbatim in `CHANGELOG.md`; the test lists and checks each one and fails on any hit outside that rule.
4. SC3: in the fixture PDF, a block without `:linenos:` shows no line numbers; a `:linenos:` block shows numbers starting at 1; `:lineno-start: 10` shows 10 as its first number; `:emphasize-lines:` highlights exactly the named lines in the compiled output; a block with a language shows codly 2.0's language badge text (e.g. "Python"). No 1.3-era styling is set (no `fill:` or highlight paint in emitted `.typ`).
5. E5 (criterion SC3): with `:lineno-start: 10` and `:emphasize-lines: 2`, the highlighted row is the 2nd source line, displayed as 11, and no other row is highlighted.
6. SC4: a `code-block` with `:caption:` and `:name:` renders as "Listing N: <caption>" numbered in the listing sequence (two captioned blocks → Listing 1 and Listing 2) while an image figure in the same document is "Figure 1"; a `:numref:` and a `:ref:` to the listing's name compile and their text appears in the PDF (E8); a caption `Cap ]br #x $m$` renders verbatim.
7. E2: a block containing `"`, `\`, a backtick, ``` and ```` runs, `#`, `$`, a tab, CJK, emoji and trailing whitespace (the tab via literalinclude) is emitted as a `raw("...")` string literal that, decoded with Typst's string escapes, equals the literal_block's text byte-for-byte (tabs and trailing whitespace included), and the compiled PDF text equals the source text with each tab compared as rendered whitespace.
8. E3: an empty `code-block` and a single-line block both compile and render as a codly block — the empty one shows its language badge (one empty row, via `skip-last-empty: false`); a literalinclude whose text ends in a newline shows no extra empty numbered row.
9. E4: `:lineno-start: 1` emits no `offset:`; `:lineno-start: 0` displays 0 as its first number and `:lineno-start: 1000` displays 1000.
10. E6: `:emphasize-lines: 2-4,4,6` emits `highlighted: (2, 3, 4, 6)` and highlights lines 2, 3, 4 and 6 once each in the compiled output; an out-of-range line number produces Sphinx's own "out of range" warning and the build still compiles.
11. E7: a block with no language (no argument with `highlight_language` unset, and an explicit `none`) renders as a codly block with no badge and no `lang:` in its `raw(...)`; a doctest_block keeps `lang: "python"` and shows the Python badge.
12. The Verify run reports no skipped test in the two new gate files, and any translator change keeps T001's Verify passing.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && uv run python -c "import typst, pypdf, myst_parser, furo" && LC_ALL=C uv run pytest tests/test_codly2_render_gate.py tests/test_codly2_output_gate.py -o addopts="" -q -rs > "${TMPDIR:-/tmp}/t002-gates.log" 2>&1; rc=$?; cat "${TMPDIR:-/tmp}/t002-gates.log"; test $rc -eq 0 && ! grep -qiE '[0-9]+ skipped' "${TMPDIR:-/tmp}/t002-gates.log" && LC_ALL=C uv run pytest tests/ && uv run black --check typsphinx tests && uv run ruff check typsphinx tests && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-03 — created by planner
- 2026-11-03 — build_T002: implemented within `files`; no translator change needed (`typsphinx/translator.py` and `tests/test_translator.py` untouched — every SYNTHESIS medium-confidence rule rendered as stated: empty block → one row + Python badge via `skip-last-empty: false`; literalinclude with trailing newline → rows 1,2 only; `default`/`none` → no `lang:`, no badge).
  - Fixture `tests/fixtures/codly2_render_gate/` (conf.py `numfig = True`, `highlight_language` unset; index.rst; `tab_snippet.txt`, `encoding_snippet.txt` — `.txt` so ruff/black never lint the deliberate tab/trailing whitespace; `figure.svg`). Contexts: captioned listing, list item, admonition, table cell.
  - `tests/test_codly2_render_gate.py` (24 tests): one `-E -b typstpdf -d` build; PDF read with pypdf as positioned text rows (line number = digits-only first run, badge = run in the right 30% of the page) plus a q/Q/cm/path/fill content-stream interpreter; a row is highlighted when a row-sized fill over its code column carries a paint absent from every row of un-highlighted control blocks (structure, no colour constants). Covers AC4–AC11, incl. Listing 1 / Figure 1 / Listing 2 ordering, numref/ref text, out-of-range warning (LC_ALL=C in subprocess env). E2 PDF text: tab ↔ whitespace, each non-ASCII char ↔ itself or one NUL (.notdef) — measured: compiling with `ignore_system_fonts=True` (the ubuntu/windows CI case, cf. test_diagraph_escaping_render_gate) extracts CJK/emoji as `\x00`; a dedicated test recompiles that way. Byte identity is asserted on the decoded `.typ` string vs the file (read_text, CRLF-safe) and the doctree text.
  - `tests/test_codly2_output_gate.py` (10 tests): `-b typst -d` builds of test-basic, examples/basic, examples/advanced, docs/source and the fixture; content files = docname `.typ` (set asserted equal to all non-`_typsphinx`/`_template` `.typ` minus `env.config.typst_documents` wrappers). Interpretation note for AC1: the count of `codly.new(raw(` is taken over code-mode text only (string-literal spans skipped), because docs/source inline literals legitimately contain that text (`api/index`, `changelog`, `user_guide/templates` carry 2 extra in-string hits each); each code-mode hit must also parse against the Interface-contract grammar, and decoded raw() strings must equal the doctree literal/doctest texts in order. Expression termination: `\n`, or `}` in a table cell (the cell body is emitted with trailing whitespace trimmed). ``` and `codly\(` absence run over the WHOLE text of the four SC2 projects; the fixture is excluded from the whole-text fence check (its E2 block holds backtick runs in its string) and checked on code-mode text instead. C5 exemption: exactly `{ codly(...) }` and `#codly(number-format: none)` in docs `changelog.typ` inline `raw("...")` literals, each verified verbatim in CHANGELOG.md and each required to be hit.
  - Mutation check (translator temporarily mutated, restored byte-identical): dropping the highlight offset, dropping `highlighted`, adding a duplicate/extra line, dropping `skip-last-empty`, keeping `default` as a language, and a leading `#` each turned the gates red.
  - Verify (exact command, primary checkout): exit 0 — gate files 34 passed, no skips; `LC_ALL=C uv run pytest tests/` 1879 passed, 1 skipped, 0 failed; black --check 390 unchanged; ruff clean; mypy clean.
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t002-verify): pass, exit 0; output tail:
  ```
   + sphinxcontrib-bibtex==2.7.0
   + sphinxcontrib-devhelp==2.0.0
   + sphinxcontrib-htmlhelp==2.1.0
   + sphinxcontrib-jsmath==1.0.1
   + sphinxcontrib-qthelp==2.0.0
   + sphinxcontrib-serializinghtml==2.0.0
   + tomli-w==1.2.0
   + tox==4.64.10
   + tox-uv==1.37.2
   + tox-uv-bare==1.37.2
   + twine==7.0.0
   + types-docutils==0.23.0.20260923
   + typing-extensions==4.16.0
   + typsphinx==0.9.8 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t002-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  All done! ✨ 🍰 ✨
  390 files would be left unchanged.
  ```

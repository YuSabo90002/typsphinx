# Evidence — pitfalls

<!-- Written by one researcher role. Consumed by the decider. -->

Dimension: pitfalls
Questions assigned: Exact codly 2.0 field names/semantics for line numbers off, start number (`offset` value for `:lineno-start: N`), and whole-line highlights relative to offset.; Does `figure(codly.new(raw(...)), caption: ...)` keep `kind: raw` auto-detection, or must typsphinx pass `kind: raw`? (User expects it works — codly 2.0 docs show captioned listings; captioned blocks get no SC2 exception either way.)

Experiment setup (all findings marked "experiment"): fresh dir `/tmp/claude-1000/codly2.4o9k` (outside the repo), typst-py 0.15.0 via `/home/yuta/Documents/typsphinx/.venv/bin/python -I`, `@preview/codly:2.0.0` fetched by typst-py into `~/.cache/typst/packages/preview/codly/2.0.0/`, text extracted with pypdf, visuals checked by rendering PNG (`typst.compile(..., format="png")`). Sphinx probes built the current HEAD (46a72b5f) typsphinx against throwaway projects in the same dir.

## Finding: codly 2.0 `highlighted` is keyed by DISPLAYED line numbers; typsphinx must add the offset

- **Claim**: In codly 2.0.0, `highlighted` entries target displayed numbers (source line + `offset`). `codly.new(raw("b1\nb2\nb3", block: true), offset: 9, highlighted: (11,))` highlights the 2nd source line (shown as 11); the same block with `highlighted: (2,)` highlights nothing and raises no error. To honour Sphinx `:lineno-start: N` + `:emphasize-lines: k` (E5), typsphinx must emit `offset: N - 1` and `highlighted: (k + N - 1, ...)`.
- **Source**: `~/.cache/typst/packages/preview/codly/2.0.0/src/args.yaml` lines 189-193 ("Whole-row highlight configurations keyed by displayed line numbers, including offsets and skips") and 1227-1235 (`highlighted-line.line`: "Displayed line number to highlight, including offsets and skips"); https://codly.dherse.dev/v2.0.0/migration-1.3.html ("If an offset shows source line 2 as number 12, target `12`."); experiment `hl.typ` rendered to `hl.png`.
- **Confidence**: high
- **Why it matters here**: SC3/E5 demand the 2nd source line be highlighted under `:lineno-start: 10`; emitting Sphinx's `hl_lines` verbatim silently highlights the wrong line or nothing.

## Finding: The E5 off-by-offset defect already exists in the current 1.3 output

- **Claim**: Current HEAD emits `codly(offset: 9)` + `codly(highlights: ((line: 2, ...),))` for `:lineno-start: 10` / `:emphasize-lines: 2`, and the compiled PDF shows lines 10-12 with no highlight at all — codly 1.3 also compares highlight `line` against the offset-adjusted number (`src/lib.typ:367` `.filter(x => x.line == it.number)` where the line is rebuilt as `raw.line(line.number + offset, ...)` at 1520-1521). The migration guide confirms "The line coordinate is the displayed number, in both 1.3 and 2.0."
- **Source**: experiment `sp2/` (Sphinx build of current typsphinx, `out/index.typ` lines 8-9, page 3 PNG); `~/.cache/typst/packages/preview/codly/1.3.0/src/lib.typ:367,1520-1528`; https://codly.dherse.dev/v2.0.0/migration-1.3.html
- **Confidence**: high
- **Why it matters here**: the migration cannot carry the existing `hl_lines` mapping forward as "known good"; the existing `tests/fixtures/codly_offset_render_gate` covers `:lineno-start:` only, never combined with `:emphasize-lines:`, so no gate catches it today.

## Finding: codly 2.0 field names for the three options

- **Claim**: Line numbers off = `number-enabled: false` (default `true`; `number-format` no longer exists for this); start number = `offset: <int>` added to source numbers (default `0`, also accepts `auto`/label), so `:lineno-start: N` → `offset: N - 1`; whole-line highlight = `highlighted: (<int> | (line, color) | (line: n, color: c), ...)`, an int casts to a highlighted-line. `highlights:` still exists but is the character-span API.
- **Source**: `~/.cache/typst/packages/preview/codly/2.0.0/src/args.yaml:57-61,95-101,189-200`; `codly.typ:438-455` (highlighted-line casts from int / `(line, color)` / dict); experiments `sem.typ` (offset -1 → first number 0; offset 999 → 1000; `number-enabled: false` → no numbers).
- **Confidence**: high
- **Why it matters here**: E4 boundaries hold directly (`lineno-start: 0` → `offset: -1` renders 0; 1000 → `offset: 999`); `:lineno-start: 1` must emit no offset per E4 (current `!= 1` guard is reusable).

## Finding: `highlighted` with `number-enabled: false` still works; out-of-range entries are silently ignored

- **Claim**: `codly.new(raw("n1\nn2", block: true), number-enabled: false, highlighted: (2,))` highlights `n2`; `highlighted: (5,)` on a 2-line block compiles and highlights nothing.
- **Source**: experiment `hl.typ` / `hl.png`
- **Confidence**: high
- **Why it matters here**: `:emphasize-lines:` without `:linenos:` keeps working (offset is 0 then, so displayed = source); E6 out-of-range lines cannot break compilation even if they slipped through.

## Finding: Duplicate `highlighted` entries change colors — typsphinx must dedupe

- **Claim**: Sphinx does not dedupe `hl_lines` (`parse_line_num_spec("2-4,4,6")` → `[1,2,3,3,5]` → `hl_lines [2,3,4,4,6]`; current HEAD emits line 4 twice). In codly 2.0 the default highlight paint rotates through a palette per entry, so `highlighted: (2,3,4,4,6)` paints line 4 and 6 with different colors than `(2,3,4,6)` (duplicate consumes a palette slot and overlays). Explicit `(n, yellow)` pairs give a single uniform color.
- **Source**: `.venv/lib/python3.13/site-packages/sphinx/util/_lines.py:4-29`; `sphinx/directives/code.py:127-140`; experiment `sp/out/index.typ` (current emission with duplicated `line: 4`) and `dup.typ`/`dup.png`.
- **Confidence**: high
- **Why it matters here**: E6 requires 2,3,4,6 highlighted once each; emit `sorted(set(hl_lines))`. Also note: codly 2.0's default look is a multi-colour palette, not 1.3-era yellow — C1 says follow the 2.0 default, so no `fill: yellow` should be carried over.

## Finding: Out-of-range emphasize lines are filtered by Sphinx with a warning before typsphinx sees them

- **Claim**: `CodeBlock.run` warns "line number spec is out of range(1-%d)" and keeps only `x < nlines`; LiteralInclude does the same against the selected lines (`code.py:485-493`). Observed: `:emphasize-lines: 2-4,4,6,9` on a 6-line block → WARNING and `9` absent from the node.
- **Source**: `.venv/lib/python3.13/site-packages/sphinx/directives/code.py:127-140,485-494`; experiment `sp2` build log ("WARNING: line number spec is out of range(1-6): '2-4,4,6,9'")
- **Confidence**: high
- **Why it matters here**: E6 "follow Sphinx's own warning behavior" needs no typsphinx logic beyond passing (deduped) `hl_lines`; for literalinclude, lines are relative to the included snippet, so the same `+ (linenostart - 1)` translation applies with `:lineno-match:`.

## Finding: `figure(codly.new(raw(...)), caption: ...)` keeps `kind: raw` auto-detection

- **Claim**: With no `kind` argument, `figure(codly.new(raw("...", lang: "py", block: true)), caption: [..])` gets `kind: raw`, supplement `[Listing]`, and shares the raw-figure counter with a plain `figure(raw(...))`, separate from image figures: output "Listing 1: Code A … Listing 2 … Listing 3: Plain C … Figure 1"; `counter(figure.where(kind: raw)).final()` = `(3,)`, image counter `(1,)`; `@lstA` → "Listing 1". Even a str body `codly.new("s = 1", lang: "py")` is detected as `raw`. Passing `kind: raw` is not required.
- **Source**: experiments `fig.typ`, `strbody.typ`; https://typst.app/docs/reference/model/figure/ ("If set to `auto`, the figure will try to automatically determine its kind… Automatically detected kinds are tables and code." / "All figures of the same kind share a common counter.")
- **Confidence**: high
- **Why it matters here**: SC4/E8 holds without a `kind:` argument; passing `kind: raw` explicitly is harmless belt-and-braces if the decider wants independence from detection.

## Finding: codly 2.0 adds hidden per-line figures when the enclosing figure carries a label

- **Claim**: With `block-label: auto` (default) and a label on the enclosing figure, codly emits one hidden `figure(kind: "codly-line", supplement: none, outlined: false)` per code line (`query(figure)` returned `"codly-line"` entries; accessing `.supplement.text` on them errors "cannot access fields on type none"). typsphinx today anchors `:name:` via a preceding `[#metadata(none) <doc:name>]`, not a label on the figure, so `block-label` resolves to none and no per-line figures are emitted; raw-kind numbering is unaffected either way.
- **Source**: `~/.cache/typst/packages/preview/codly/2.0.0/src/lib.typ:24-29,661-691`; `args.yaml:45-51` (`block-label`); experiment `fig.typ` (first run error, second run kinds list); `sp/out/index.typ` (metadata anchor before `figure(`).
- **Confidence**: high
- **Why it matters here**: keep the metadata-anchor pattern (or pass `block-label: none`); moving the label onto the figure would add hidden figures that any `query(figure)` in a user template must tolerate.

## Finding: `escape_typst_string` (translator.py:158) is reusable for `raw("...")` and round-trips E2 content except tabs

- **Claim**: Code containing `"`, `\`, ``` ``` ``` and ```` ```` ```` runs, `#`, `$`, `@ref`, `<lbl>`, `*b*`, `_i_`, CJK, emoji, `é`, a literal `\u{41}`, and trailing spaces, passed through `escape_typst_string` into `codly.new(raw("...", lang: "python", block: true), number-enabled: false, lang-position: none)`, extracts from the PDF identical to the source on every line except the tab line: `\tindented_by_tab` comes back as two spaces. Plain Typst `raw` renders tabs as spaces too (`tab.typ`), so this is Typst behaviour, not escaping.
- **Source**: `typsphinx/translator.py:158-189`; https://typst.app/docs/reference/foundations/str/ (escapes `\\ \" \n \r \t \u{…}`); experiments `esc.py` (`DIFF '\tindented_by_tab' '  indented_by_tab'`), `tab.typ`.
- **Confidence**: high
- **Why it matters here**: E2 as worded ("tabs … round-trip byte-identical in the PDF text") is not achievable through any raw-based rendering; the held-out check needs to compare tabs as expanded spaces (or the `.typ` string decode) — a verification-design issue to rule on, not an implementation bug.

## Finding: The current ``` fence already breaks on backtick runs; raw("...") fixes it

- **Claim**: Current HEAD emits code text verbatim inside a ```` ```python ```` fence (`visit_Text` early-returns `add_text(text_content)` when `in_literal_block`, translator.py:1808-1810), so a line `a = "```"` closes the fence early. The escaped string-literal form has no delimiter collision (verified in `esc.py`).
- **Source**: `typsphinx/translator.py:1808-1810,2575-2580,2604`; experiment `sp/out/index.typ` (fence containing ``` ``` ```).
- **Confidence**: high
- **Why it matters here**: E2 backtick-run coverage is a real regression test against an existing defect; implementation must stop the per-Text-node passthrough and emit `escape_typst_string(node.astext())` once.

## Finding: `parsed-literal` children leak markup into the code block today

- **Claim**: A `.. parsed-literal::` containing `**bold**` is a `literal_block` with element children; current HEAD visits them and writes `strong({bold}) text` inside the fence (rendered as literal text). Under the new emission, child visitors would write Typst code into the middle of the `raw("...")` string, breaking it, unless the translator emits `node.astext()` and skips children.
- **Source**: experiment `sp/out/index.typ` (block ```` ```default\nstrong({bold}) text ````); `typsphinx/translator.py:1808` (only Text is special-cased).
- **Confidence**: high
- **Why it matters here**: SC2 covers every literal_block; parsed-literal is a literal_block with children, so the new visitor must `raise nodes.SkipNode` (or equivalent) after emitting; inline formatting in parsed-literal is necessarily lost in `raw()`.

## Finding: Captions are inserted unescaped into a markup block today — `]` aborts the compile

- **Claim**: `visit_container` stores `caption.astext()` and `visit_literal_block` emits `figure(caption: [{caption}])[` with no escaping (the "Escape special characters" comment does nothing). A caption `Cap *star* #hash $m$ ]br` produced `figure(caption: [Cap star #hash $m$ ]br])[` and `typstpdf` failed with "unclosed delimiter"; `#hash` would execute and `$m$` becomes math. In code mode, `caption: text("Cap ]br #x $m$")` (string escaped) renders verbatim ("Listing 1: Cap ]br #x $m$").
- **Source**: `typsphinx/translator.py:1385-1391,2471-2477`; experiment `sp/` (build error "TypstError: unclosed delimiter"), experiment `nest.typ`.
- **Confidence**: high
- **Why it matters here**: rewriting the captioned path to pure code mode (C2/SC2) is the moment to route the caption through `escape_typst_string` (or the translator's normal inline rendering); keeping `[{caption}]` keeps a markup-mode island and this defect.

## Finding: No-language blocks arrive as `language="default"`, which codly 2.0 shows as a "default" badge

- **Claim**: `.. code-block::` without an argument gets `literal['language'] = highlight_language` (Sphinx default `'default'`); current HEAD emits ```` ```default ````. codly 2.0 displays unknown language keys verbatim ("Missing keys display the original language key with default-color"): `raw(..., lang: "default")` shows badge "default", `lang: "none"` shows "none"; only `lang: none` (or omitted) shows no badge.
- **Source**: `.venv/lib/python3.13/site-packages/sphinx/directives/code.py:155-164`; `codly/2.0.0/src/args.yaml:375-389`; experiments `sem.typ` (CASE10 "none" badge, CASE11 "default" badge, CASE12 no badge), `sp/out/index.typ`.
- **Confidence**: high
- **Why it matters here**: E7 (no badge for no-language / `highlight_language` none) requires mapping at least `""` and `"none"` to an omitted `lang`; whether `"default"` maps to no-language or to python (Sphinx HTML highlights `default` as Python) is a decision to rule on, otherwise SC3's badge check produces "default" badges across docs.

## Finding: Empty code blocks render as a hairline with no row and no badge by default

- **Claim**: `codly.new(raw("", lang: "py", block: true))` compiles but renders only a thin rule (no row, no badge, no number); whitespace-only `"   "` behaves the same; adding `skip-last-empty: false` renders one empty numbered row with the badge. Default `skip-last-empty: true` also drops a trailing whitespace-only last line (`"x\n   "` shows only `x`). Sphinx accepts an empty `.. code-block:: python` (no `assert_has_content`; current HEAD emits an empty fence).
- **Source**: `codly/2.0.0/src/args.yaml:136-140` (`skip-last-empty`); experiments `empty.typ`/`empty.png`, `sp/out/index.typ`; `sphinx/directives/code.py` CodeBlock (`has_content = True`, no `assert_has_content`).
- **Confidence**: high
- **Why it matters here**: E3 "empty block … render as a codly block" is only visibly true with `skip-last-empty: false` for empty/whitespace-only bodies; one-line blocks render normally.

## Finding: Form feed, vertical tab, NEL and U+2028 become extra raw lines

- **Claim**: After `escape_typst_string`, code containing `\x0c`, `\x0b`, `\x85` or ` ` compiles but Typst's raw splits there (PDF shows `1 x` / `2 y`), while Sphinx counts lines by `\n` only; `\x1b`/`\x00` stay inline; `\r\n` is one break.
- **Source**: experiment (control-character loop, `cc.typ`).
- **Confidence**: medium
- **Why it matters here**: an included source with form feeds (e.g. `literalinclude` of C/Python files with page breaks) would shift displayed numbers and `highlighted` targets relative to Sphinx; pre-existing with the fence too, out of E-table scope but worth a known-limitation note.

## Finding: codly.new works as a pure code-mode expression in list items, admonitions, table cells and figures

- **Claim**: Inside one `#{ ... }` block, `list({ text(..); linebreak(); codly.new(...) }, { figure(codly.new(...), caption: text(..)) })`, gentle-clues `info({ codly.new(...) })`, `table(columns: (1fr, 2fr), [cell], codly.new(...))`, and `[#metadata(none) <lbl>]` + `figure(...)` + `link(<lbl>, ..)` all compile and render; no `#` prefix or `#{` re-entry is needed anywhere. In a narrow table cell a long first line wraps and the inline badge overlaps code text.
- **Source**: experiment `nest.typ`/`nest.png`; contrast `typsphinx/translator.py:2479-2521` (`wrapper_prefix`/`codly_prefix` mode juggling).
- **Confidence**: high
- **Why it matters here**: confirms C2 — the `codly_prefix` and list-item `{`/`#{` wrappers (FID-12 leak class) can be deleted for code blocks; the badge overlap in narrow cells is codly default styling (C1 says keep defaults).

## Finding: Many existing tests encode the 1.3 emission strings

- **Claim**: Literal 1.3 strings (`codly(`, `number-format`, `codly-init`, ```` ``` ````) appear in 16 test files, heaviest in `tests/test_translator.py` (64 lines), `tests/test_pdf_render_gate.py` (29), `tests/test_template_codly.py` (15), `tests/test_codly_caption_listitem_leak_render_gate.py` (5), `tests/test_deflist_definition_multiblock_render_gate.py` (5), `tests/test_doctest_block_render_gate.py` (4).
- **Source**: `grep -cE 'codly\(|number-format|codly-init|```' tests/*.py`
- **Confidence**: medium
- **Confidence note**: counts include incidental matches such as docs-gate backticks
- **Why it matters here**: SC9 (0 failed) depends on rewriting these assertions in the same task as the emission change; the leak gates (FID-12, config leak) should be re-pointed at the new invariant (no `codly(` / no fence) rather than deleted.

## Assigned questions — answers

- Exact codly 2.0 field names/semantics for line numbers off, start number (`offset` value for `:lineno-start: N`), and whole-line highlights relative to offset. → `number-enabled: false` disables the number gutter; `offset: N - 1` makes the first displayed number N (integer added to source numbers; `0`/`-1`/`999` verified); `highlighted: (...)` takes DISPLAYED numbers (source + offset), so typsphinx must translate Sphinx `hl_lines` k → `k + N - 1` and dedupe; mismatched numbers are silently ignored. Sources: codly 2.0.0 `src/args.yaml`, migration-1.3 page, experiments `sem.typ`/`hl.typ`/`dup.typ`. The same displayed-number rule already applied in 1.3, so current HEAD's lineno-start+emphasize output highlights nothing.
- Does `figure(codly.new(raw(...)), caption: ...)` keep `kind: raw` auto-detection, or must typsphinx pass `kind: raw`? (User expects it works — codly 2.0 docs show captioned listings; captioned blocks get no SC2 exception either way.) → Yes. Kind `raw`, supplement "Listing", raw-figure counter separate from images, `@label` → "Listing n"; no `kind: raw` needed (experiments `fig.typ`, `strbody.typ`; Typst figure docs).

## Dead ends

- codly 2.0 docs site for a `kind` statement — the migration page does not mention figure `kind`; resolved by experiment instead.
- Using pypdf text extraction to verify highlights — highlights are backgrounds, not text; PNG rendering was required.
- Inline-literal helper near translator.py:2098 as a separate escaper — `visit_literal` itself delegates to the shared `escape_typst_string` (translator.py:158); its zero-width-space insertions (table/colon-leading cases) are inline-only and must not be reused for code blocks.

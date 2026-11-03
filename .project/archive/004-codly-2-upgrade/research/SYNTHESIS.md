# Synthesis

<!-- Written by the decider role. The planner treats Decisions as settled. -->

## Settled

- codly pin — `DEFAULT_PACKAGES` codly spec becomes `@preview/codly:2.0.0`; 2.0.0 is the latest release and needs Typst 0.15.0, matching the locked typst-py 0.15.0; elembic 1.1.1 is a transitive download, not a sixth pinned package (INTENT SC1; evidence-stack.md § codly 2.0.0 is the latest codly; it requires Typst 0.15.0)
- codly-languages — stays `@preview/codly-languages:0.1.10` imported `*`; it is current, has no codly dependency, every entry carries `name`, and badges render under codly 2.0 — no bump (INTENT C1 ruling 3a; evidence-stack.md § codly-languages 0.1.10 is current and works unchanged with codly 2.0)
- Other `@preview` packages — mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7 unchanged; codly 2.0 does not force a bump (INTENT Scope: out)
- No 1.3 shim — no `codly-init` alias, no state-style `codly(...)` compatibility layer; the break is disclosed in CHANGELOG + templates.rst (INTENT Scope: out, user ruling 1a, N1)
- No global raw→codly show rule — `typsphinx-init` installs no `show raw` rule; only typsphinx's explicit `codly.new` calls render through codly (INTENT E9, C3)
- Visual design — codly 2.0 defaults for colours, radius, badge look; no `fill: yellow` or other 1.3-era styling carried over (INTENT C1, SC3, Scope: out)
- Code-mode output — every literal_block and doctest_block becomes one code-mode `codly.new(raw(...), ...)` expression; the ``` fence, `codly_prefix` and the list-item `{` / `#{` wrappers are deleted (INTENT C2, SC2; evidence-pitfalls.md § codly.new works as a pure code-mode expression in list items, admonitions, table cells and figures)
- String escaping — the code body goes through the existing `escape_typst_string` (translator.py:158), whose docstring already names it the single escaper for `raw("...")`; its inline-literal zero-width-space variants are not used (typsphinx/translator.py:158-189; evidence-pitfalls.md § `escape_typst_string` (translator.py:158) is reusable for `raw("...")` and round-trips E2 content except tabs)
- Line numbers off — a block without `:linenos:` gets `number-enabled: false` (codly 2.0 default is numbers on) (evidence-stack.md § line numbers off = `number-enabled: false`; INTENT SC3)
- Start number — `offset: N - 1` only when `linenos` is true and `linenostart != 1` (existing guard reused; `0` → `offset: -1`, `1000` → `offset: 999`); never `offset: auto` (evidence-stack.md § `offset` is additive; `:lineno-start: N` needs `offset: N - 1`; INTENT E4)
- Emphasized lines — `highlighted: (...)` keyed by DISPLAYED numbers: emit `sorted(set(hl_lines))` each plus the emitted offset (`k + N - 1` when an offset is emitted, `k` otherwise); out-of-range lines are already filtered by Sphinx with its own warning (evidence-stack.md § whole-line highlights = `highlighted`, keyed by DISPLAYED numbers (offset included); evidence-pitfalls.md § Duplicate `highlighted` entries change colors — typsphinx must dedupe; § Out-of-range emphasize lines are filtered by Sphinx with a warning before typsphinx sees them; INTENT E5, E6)
- doctest_block language — keeps the existing node-class `python` fallback; `highlight_language` is still not followed (typsphinx/translator.py:2573-2582 D-02/D-03; INTENT E7)
- Figure kind detection — `figure(codly.new(raw(...)), ...)` is auto-detected as `kind: raw`, supplement Listing, sharing the listing counter, separate from image figures (evidence-pitfalls.md § `figure(codly.new(raw(...)), caption: ...)` keeps `kind: raw` auto-detection; INTENT SC4, E8)
- Bundled `templates/base.typ` — needs no codly code change; it only imports deps.typ `*` (comment text mentioning codly-init may need a wording touch) (evidence-stack.md § migration cost against the existing code)
- Drift scanner — `_PREVIEW_PIN_RE` matches `@preview/codly:2.0.0` regardless of `: *` vs ` as codly`; no scanner change (evidence-stack.md § migration cost against the existing code)
- Release work — no version bump, release section, tag or publish in this milestone (INTENT Scope: out, user ruling 4a)
- Doc-audit rulings — charged-ieee approach1 adds `"title"` to `typst_template_function["params"]` (fix-code); advanced README says seealso renders through `#tip` and shows code-mode `mi(...)` without `#` (fix-doc) (INTENT C1 rulings 5-1/5-2/5-3, SC7, SC8; DOCS-AUDIT.md Remediation queue rows 1-3)

## Decisions

### deps.typ codly import shape and `PreviewPackage` model

- **Decision**: deps.typ imports codly as a module: `#import "@preview/codly:2.0.0" as codly`. Extend the frozen dataclass `PreviewPackage` with an optional `alias: str | None = None` field; `import_line()` returns `#import "SPEC" as ALIAS` when `alias` is set and the existing `#import "SPEC": ITEMS` form otherwise. The codly entry becomes `PreviewPackage(spec="@preview/codly:2.0.0", items="", alias="codly")` (or `items` made optional — planner's choice as long as exactly one form is set and validated). The spec literal stays only in `typst_deps.py`; `tests/test_preview_version_sync.py`'s import-line assertion is rewritten to compare against `package.import_line()` and a literal expected list showing ` as codly`. deps.typ's exported names become `codly` (module), `codly-languages`, `mi`, `mitex`, the gentle-clues names, `render`, `typsphinx-init`; `codly-init` disappears.
- **Runner-up**: keep `items="*"` for codly — lost because codly 2.0's top level defines `line`, `highlight`, `range`, `ref`, `info`, ... which re-export through deps.typ and broke the translator's `line(length: 100%)` and made `codly.new` unreachable. A free-form "import clause" string replacing `items` also lost: it changes the meaning of `items` for the four unchanged packages and embeds Typst syntax in the data model.
- **Evidence**: evidence-stack.md § `import "@preview/codly:2.0.0": *` shadows Typst builtins and breaks typsphinx output; `as codly` does not; evidence-stack.md § migration cost against the existing code; typsphinx/typst_deps.py:36-71; tests/test_preview_version_sync.py:94-123
- **Confidence**: high

### typsphinx-init body

- **Decision**: `typsphinx-init(body)` becomes `{ show: codly.lang-set_(languages: codly-languages); body }` (one show rule, multi-line formatting as today). No `codly-init`, no `show raw` rule, no `codly.set_` defaults, no highlight paint (user ruling Q2 a: codly 2.0's default multi-colour palette is kept).
- **Runner-up**: additionally set `show: codly.set_(number-enabled: false)` globally and emit `number-enabled: true` only for `:linenos:` blocks — lost because it changes codly's default for any `codly.new` a user writes in a template, while per-block `number-enabled: false` keeps each emitted expression self-contained.
- **Evidence**: evidence-stack.md § language badge comes from `raw(lang:)` plus `codly.lang-set_(languages: ...)`; no language → no badge; evidence-stack.md § line numbers off = `number-enabled: false`; INTENT E9
- **Confidence**: high

### Emission shape of one code block

- **Decision**: `visit_literal_block` emits, as one code-mode expression and then `raise nodes.SkipNode` (doing the `depart_literal_block` cleanup inline before raising): `codly.new(raw("ESCAPED", block: true[, lang: "L"]), [number-enabled: false, ][offset: N-1, ][highlighted: (a, b, ...), ][skip-last-empty: false])` where ESCAPED is `escape_typst_string(node.astext())`. The `lang` argument sits inside `raw(...)` (not on `codly.new`). A single-entry `highlighted` keeps a trailing comma (`(11,)`). Children are never visited, so parsed-literal inline markup is flattened to its text (necessarily lost in `raw()`), and the `in_literal_block` passthrough in `visit_Text` is no longer reached for code blocks. List-item separators are kept; the list-item `{`/`#{` wrapper and `codly_prefix` are removed.
- **Runner-up**: keep visiting children and accumulate Text into the string — lost because element children (parsed-literal `strong` etc.) would write Typst code into the middle of the string literal and break it, and the current per-Text passthrough is exactly what lets ``` runs close the fence today.
- **Evidence**: evidence-pitfalls.md § `parsed-literal` children leak markup into the code block today; § The current ``` fence already breaks on backtick runs; raw("...") fixes it; § codly.new works as a pure code-mode expression in list items, admonitions, table cells and figures; evidence-stack.md § string escaping into `raw("...")` round-trips the hard characters
- **Confidence**: high

### Empty and whitespace-only code blocks

- **Decision**: emit `skip-last-empty: false` only when `node.astext().strip() == ""`; all other blocks keep codly's default `skip-last-empty: true`.
- **Runner-up**: always emit `skip-last-empty: false` — lost because literalinclude text ends in a newline and would gain a spurious empty numbered row; omitting it entirely lost because an empty block then renders as a hairline with no row or badge, failing E3 "renders as a codly block".
- **Evidence**: evidence-pitfalls.md § Empty code blocks render as a hairline with no row and no badge by default; evidence-stack.md § Dead ends (empty block)
- **Confidence**: medium — verify in wave 1 that a literalinclude block and an empty block both render as intended in PDF

### Language mapping for Sphinx's `default` / `none` / empty language

- **Decision**: `language` values `""`, `"none"` and `"default"` map to an omitted `lang` (no badge, no Typst syntax highlighting); every other value is passed through as `lang: "VALUE"` (`text` → "Plain Text" badge; unknown keys show the key verbatim, codly's default). doctest_block → `python`.
- **Runner-up**: map `"default"` to `"python"` (Sphinx HTML highlights `default` as Python with lenient fallback) — lost because Typst cannot reproduce the fallback, so plain `::` blocks of shell output or prose would be labelled "Python" and syntax-coloured as Python, while today's ```` ```default ```` output has no highlighting; mapping to no-language preserves current colouring and avoids a false badge. Passing `"default"` through lost outright: it shows a literal "default" badge across the docs.
- **Evidence**: evidence-pitfalls.md § No-language blocks arrive as `language="default"`, which codly 2.0 shows as a "default" badge; evidence-stack.md § language badge comes from `raw(lang:)` plus `codly.lang-set_(languages: ...)`; no language → no badge; INTENT E7
- **Confidence**: medium — it is the safer reading of E7, but the reviewer of SC3 should see a project with `highlight_language` unset produce no badges on `::` blocks and accept that

### Captioned code blocks: caption text, kind, anchor

- **Decision**: the captioned path is pure code mode: `figure(codly.new(...), caption: text("ESCAPED_CAPTION"), kind: raw)` with the caption from `caption.astext()` through `escape_typst_string`. Pass `kind: raw` explicitly. Keep the existing `[#metadata(none) ...label]` anchor emitted before the figure (and the `_emit_id_anchors` route); do not attach the label to the figure and do not set `block-label`.
- **Runner-up**: rely on auto-detection without `kind:` — works today (high-confidence experiment) but couples listing numbering to codly 2.0's element internals in a two-week-old package; explicit `kind: raw` costs nothing and still yields supplement "Listing". Rendering caption children through the translator's inline visitors lost: larger change, today's output already uses `astext()`, and it would reopen a markup-mode island. Putting the label on the figure lost because codly then emits one hidden `codly-line` figure per code line, which user templates' `query(figure)` must tolerate.
- **Evidence**: evidence-pitfalls.md § `figure(codly.new(raw(...)), caption: ...)` keeps `kind: raw` auto-detection; § Captions are inserted unescaped into a markup block today — `]` aborts the compile; § codly 2.0 adds hidden per-line figures when the enclosing figure carries a label; typsphinx/translator.py:1375-1395, 2463-2477
- **Confidence**: high

### Existing tests and fixtures that encode 1.3 output

- **Decision**: rewrite the 1.3-string assertions (16 files; heaviest `tests/test_translator.py`, `tests/test_pdf_render_gate.py`, `tests/test_template_codly.py`) in the SAME task as the emission change, asserting the new `codly.new(raw(...), ...)` shape. Leak/nesting gates (`test_codly_caption_listitem_leak_render_gate.py`, `test_codly_config_leak_render_gate`-family, `test_deflist_definition_multiblock_render_gate.py`, `test_doctest_block_render_gate.py`) are kept and re-pointed at the new invariant (no ``` and no bare `codly(` in output, PDF compiles, no leaked config text) rather than deleted. The `typst_dependencies_override` fixture's user deps file is migrated to the 2.0 shape (`as codly`, `codly.lang-set_`) because the emitted `codly.new` needs `codly` to be a module; the `template_dependency_drift` fixture may keep its deliberate 1.3.0 pin only if that test never compiles it.
- **Runner-up**: delete obsolete leak gates — lost because they cover the nesting contexts (captioned figure, list item, deflist, doctest) that SC2 still requires to hold.
- **Evidence**: evidence-pitfalls.md § Many existing tests encode the 1.3 emission strings; tests/fixtures/typst_dependencies_override/deps/my-deps.typ:3-12; tests/fixtures/template_dependency_drift/user_deps.typ:3-10
- **Confidence**: medium — counts include incidental matches; the planner must grep for the exact set when scoping the task

### Contract docs and migration note content

- **Decision**: templates.rst export table changes the codly row from ``codly``, ``codly-init`` to ``codly`` (module: `codly.new`, `codly.set_`, `codly.lang-set_`, ...) and the `typsphinx-init` paragraph says it registers `codly-languages` through `codly.lang-set_` and installs no raw→codly rule; the `info, codly` example import (templates.rst:186) is checked against the new names. The CHANGELOG Unreleased entry (breaking) states: codly 2.0.0 upgrade; `codly-init` and the state-style `codly(...)` calls are gone, templates use `codly.new(...)` / `codly.set_`; user `typst_dependencies` files must import codly ` as codly`; raw blocks written by users (custom templates, `.. raw:: typst`) are no longer rendered through codly by `typsphinx-init`.
- **Runner-up**: document only the export-name change — lost because a user `typst_dependencies` file importing codly with `*` silently breaks every generated code block, which N1 forbids leaving undisclosed.
- **Evidence**: evidence-stack.md § `import "@preview/codly:2.0.0": *` shadows Typst builtins and breaks typsphinx output; `as codly` does not; docs/source/user_guide/templates.rst:150-186; INTENT SC6, N1
- **Confidence**: high

## For the planner

- **Wave-1 blockers**: (1) the `typst_deps.py` change (`as codly` import, new `typsphinx-init`) plus the translator emission rewrite must land together with the test rewrites, because once deps.typ exports a module named `codly` every 1.3-style `codly(...)` call in output fails to compile and the whole render-gate suite goes red; (2) a fixture build proving in PDF/PNG: `number-enabled: false`, `:linenos:` from 1, `:lineno-start: 10` + `:emphasize-lines: 2` highlighting displayed 11, `0`/`1000` starts, `2-4,4,6` deduped, empty block with `skip-last-empty: false`, literalinclude with trailing newline, captioned listing numbered separately from an image figure with a working `:numref:`; (3) the medium-confidence decisions (empty-block rule, `default`→no-language) are confirmed by that fixture before docs/examples work begins.
- **Walking skeleton**: `tests/roots/test-basic` built with `typst` emits a deps.typ with `#import "@preview/codly:2.0.0" as codly` and the new `typsphinx-init`, its content `.typ` files contain only `codly.new(raw(...), ...)` code blocks (no ```, no bare `codly(`), and `typstpdf` compiles it with a language badge visible — then extend to examples/basic, examples/advanced, charged-ieee and `tox -e docs-pdf`.
- **Pitfalls → tasks**: existing lineno-start + emphasize-lines bug (current output highlights nothing) → emission task must add the offset to `highlighted` and add a combined-option PDF gate (the existing `codly_offset_render_gate` covers lineno-start only); ``` inside code → emission task adds an E2 fixture with ``` and ```` runs, `"`, `\`, `#`, `$`, CJK, emoji, trailing spaces; `]` / `#` / `$` in a caption → captioned-path task routes the caption through `escape_typst_string` and adds a gate with `Cap ]br #x $m$`; parsed-literal children → emission task skips children (`SkipNode`) and gates a parsed-literal with `**bold**`; Sphinx `hl_lines` duplicates → emission task dedupes/sorts; `default` language badge → emission task maps it away and the docs build shows no "default" badge; hidden `codly-line` figures → keep the metadata anchor, never label the figure; `*` import shadowing `line`/`info` → deps task uses `as codly` and a gate compiles a document containing a transition and an admonition; user `typst_dependencies` override fixture → deps task migrates it; line-separator drift (`\x0c`, `\x0b`, `\x85`, U+2028 split raw lines, shifting displayed numbers and `highlighted` targets vs Sphinx's `\n` count) → accepted known limitation, noted in CHANGELOG or code comment, no transformation (E2/C4 requires the emitted string to be byte-identical); narrow table-cell badge overlap → codly default, accept (C1); OS-neutral tests (CI ubuntu/windows/macos) → every new gate compares text, not paths/colour codes; project Verify and every docs-touching task Verify need `--extra dev --extra docs` installed (17 docs gates skip otherwise) and should run under `LC_ALL=C`.

## User rulings

- Q1 (E2 tab check), 2026-11-03, user: "Q1 a" — E2 is checked as: the Typst string literal emitted in the content `.typ` decodes to the source code text byte-for-byte (tabs and trailing whitespace included), and the compiled PDF text equals the source text with each tab compared as rendered whitespace. Recorded in INTENT.md as correction C4.
- Q2 (emphasize-lines colour), 2026-11-03, user: "Q2 a" — keep codly 2.0's default multi-colour `highlighted` palette; typsphinx sets no highlight paint (`typsphinx-init` gets no `codly.highlight-set_`). Dedupe/sort of `hl_lines` remains required so the palette order is stable.

## Still unknown

- Line-separator drift for form feed / vertical tab / NEL / U+2028 in included sources — accept risk (known limitation; pre-existing with the fence)
- Other Sphinx lexer names absent from codly-languages (e.g. `pycon`, `console`, `python3`) show their key verbatim as the badge — accept risk (codly default behaviour; no INTENT criterion covers lexer aliasing)
- codly 2.0.0 is two weeks old; defects may surface under typst-py 0.15 compilation of the full docs — plan: wave-1 spike (the walking skeleton and `tox -e docs-pdf` early)

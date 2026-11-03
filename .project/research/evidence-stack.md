# Evidence — stack

<!-- Written by one researcher role. Consumed by the decider. -->

Dimension: stack
Questions assigned: Exact codly 2.0 field names/semantics for line numbers off, start number (`offset` value for `:lineno-start: N`), and whole-line highlights relative to offset.; Is codly-languages 0.1.10 compatible with codly 2.0, and which version is current?; Which names should deps.typ export (`import "@preview/codly:2.0.0" as codly` vs `*`)?

Method note: package sources were downloaded from `https://packages.typst.org/preview/codly-2.0.0.tar.gz` and `.../codly-languages-0.1.10.tar.gz` and read directly (`codly.typ`, `src/args.yaml`, `lib.typ`). Empirical checks compiled with typst-py 0.15.0 (`/home/yuta/Documents/typsphinx/.venv/bin/python`, `typst.compile`) in `/tmp/claude-1000/codly-exp.hizd/`; PDF text via pypdf, highlight rows via PNG pixel sampling at 72 ppi (row height 15 px: line 1 = y 15-29, line 2 = y 30-44, ...).

## Finding: codly 2.0.0 is the latest codly; it requires Typst 0.15.0

- **Claim**: The Typst Universe index lists codly versions up to 2.0.0 (compiler `0.15.0`); the previous release is 1.3.0 (compiler 0.12.0). No 2.0.x patch release exists. The package's `typst.toml` says `compiler = "0.15.0"`, and codly 2.0.0 depends on `@preview/elembic:1.1.1` (`codly.typ` line 1).
- **Source**: https://packages.typst.org/preview/index.json (filtered for `codly`); `codly-2.0.0/typst.toml`; `codly-2.0.0/codly.typ`; https://typst.app/universe/package/codly ("Requires Typst 0.15.0 or newer")
- **Confidence**: high
- **Why it matters here**: Confirms the SC1 pin `@preview/codly:2.0.0` matches the project's `typst>=0.15.0,<0.16` constraint; elembic is a transitive download, not a sixth package typsphinx has to pin.

## Finding: line numbers off = `number-enabled: false`

- **Claim**: The `codly.new` element field is `number-enabled` (type `option(bool)`, default `true`). `codly.new(raw("aaa\nbbb\nccc", lang: "python", block: true), number-enabled: false)` compiled and the PDF text was `aaa / Python / bbb / ccc` with no numbers; the same block without the field rendered `1 ddd / 2 eee / 3 fff`.
- **Source**: `codly-2.0.0/src/args.yaml` lines 57-61 (`number-enabled`); https://codly.dherse.dev/v2.0.0/migration-1.3.html ("For one block: codly.new(..., number-enabled: false)"); experiment `t1.typ` sections A and B
- **Confidence**: high
- **Why it matters here**: Replaces the 1.3-only `codly(number-format: none)` the translator emits at `translator.py:2531-2533`; the 2.0 default is numbers ON, so a block without `:linenos:` must pass `number-enabled: false` (SC3 "no line numbers").

## Finding: `offset` is additive; `:lineno-start: N` needs `offset: N - 1`

- **Claim**: `offset` (type `int | label | auto`, default `0`) is "added to source numbers". Observed: `offset: 9` → first displayed number 10; `offset: 999` → 1000; `offset: -1` → 0 (negative offsets compile). So the mapping is the same as the current 1.3 code: `offset = linenostart - 1`, and `linenostart == 1` needs no `offset` (E4).
- **Source**: `codly-2.0.0/src/args.yaml` lines 95-101; migration page ("The numeric form keeps its old meaning: add that number to the displayed line numbers."); experiment `t1.typ` sections C, D, E (PDF text `10 ggg`, `1000 jjj`, `0 lll`)
- **Confidence**: high
- **Why it matters here**: The existing `lineno_start - 1` arithmetic at `translator.py:2554-2556` carries over unchanged; `:lineno-start: 0` (E4) works as `offset: -1`. `offset: auto` is NOT the Sphinx default — it renumbers a range excerpt from 1 — so do not use it.

## Finding: whole-line highlights = `highlighted`, keyed by DISPLAYED numbers (offset included)

- **Claim**: The whole-row field is `highlighted` (array of `highlighted-line`, castable from `int` or `(line, color)`); its `line` is "Displayed line number to highlight, including offsets and skips". Observed on a 6-line block: no offset + `highlighted: (2,)` → band at y 30-44 (row 2); `offset: 9` + `highlighted: (11,)` → row 2; `offset: 9` + `highlighted: (2,)` → no band at all, and no error. `highlights` (plural) is a separate character-span field also keyed by displayed numbers.
- **Source**: `codly-2.0.0/src/args.yaml` lines 189-202 and 1227-1240; migration page ("If an offset shows source line 2 as number 12, target `12`."; "Offsets affect displayed numbers, line-reference labels, and highlight `line` coordinates."); experiments `h_none_2___.typ`, `h_9_11___.typ`, `h_9_2___.typ`
- **Confidence**: high
- **Why it matters here**: Sphinx `hl_lines` are 1-based source-line indices, so with `:lineno-start: N` the translator must emit `highlighted: (hl + (N - 1), ...)` (E5: `:lineno-start: 10` + `:emphasize-lines: 2` → `highlighted: (11,)`). Emitting the raw Sphinx index silently highlights the wrong line or nothing; when `:linenos:` is off but `:lineno-start:` set, whatever offset is emitted must be added consistently (or no offset emitted and raw indices used).

## Finding: `highlighted` cycles a multi-colour default palette per entry; out-of-range lines are silently ignored

- **Claim**: Without explicit colours, each `highlighted` entry takes the next colour of the theme palette: `highlighted: (2, 3, 4, 6)` produced rows of (212,215,233) blue, (213,229,214) green, (252,226,204) orange, (225,209,235) purple. Duplicates consume a colour (`(2, 4, 2)` painted row 2 orange, row 4 green). `highlighted: (99,)` on a 6-line block compiled with no band and no error. An explicit paint, e.g. `highlighted: ((11, red),)`, gave (255,65,54). The palette default is `themes-impl.presets.thesis.at("highlight-colors")`, configurable through `codly.highlight-set_(fill: ...)` ("Default paint or nonempty cycling palette ... explicit paints do not consume a color").
- **Source**: `codly-2.0.0/src/args.yaml` lines 551-560 and 189-195; experiments `h_none_2_3_4_6__.typ`, `h_none_2_4_2__.typ`, `h_none_99___.typ`, `h_9__11__red____.typ` (px2.py pixel samples)
- **Confidence**: high
- **Why it matters here**: SC3 says styling follows codly 2.0's default, but a multi-line `:emphasize-lines:` will render rainbow bands under that default; the decider must choose between "pure default palette" and a single paint (per entry or via `highlight-set_`). Dedup is required for E6 (`2-4,4,6` once each); out-of-range lines are harmless for compilation (E6).

## Finding: language badge comes from `raw(lang:)` plus `codly.lang-set_(languages: ...)`; no language → no badge

- **Claim**: With `#show: codly.lang-set_(languages: codly-languages)` active, `codly.new(raw(..., lang: "python", block: true))` rendered the badge text `Python`; `lang: "text"` rendered `Plain Text`; a `raw(..., block: true)` with no `lang` rendered no badge. A `codly.new("x = 1\ny = 2", lang: "python")` string body also works (field `lang`, default `auto`). The 1.3 `codly(languages: ...)` call is replaced by `codly.lang-set_`; "Every definition must now have a `name`."
- **Source**: `codly-2.0.0/src/args.yaml` lines 14-28 and 375-440 (`lang` element, `languages` field); `codly.typ` (`#let lang-set_(..args) = { e.set_(lang, ..args) }`); migration page; experiments `t1.typ` (A, G), `s.typ`, `i5.typ`
- **Confidence**: high
- **Why it matters here**: Gives the exact `typsphinx-init` body (`show: codly.lang-set_(languages: codly-languages)`, no `codly-init`, no `show raw` rule — E9) and confirms E7 (no language → no badge) and SC3's badge.

## Finding: codly-languages 0.1.10 is current and works unchanged with codly 2.0

- **Claim**: 0.1.10 is the newest codly-languages on Typst Universe (published 2025-10-28, same timestamp as 0.1.9); its `typst.toml` has no dependency on codly; its only export `codly-languages` is a dictionary whose 513 entries all carry `name:`, `color:`, `icon:`. Passing it to `codly.lang-set_(languages: codly-languages)` under codly 2.0.0 compiled and displayed `Python` / `Plain Text` badges. Its README/universe page still shows a codly 1.3.0 usage example; codly 2.0's own universe page shows the companion at 0.1.8 with `codly.lang-set_(languages: codly-languages)`.
- **Source**: https://packages.typst.org/preview/index.json; https://typst.app/universe/package/codly-languages; `codly-languages-0.1.10/typst.toml`, `lib.typ` (entry count via grep: 513 entries, 0 lacking `name:`); https://typst.app/universe/package/codly; experiments `t1.typ`, `i5.typ`, `s.typ`
- **Confidence**: high
- **Why it matters here**: Answers the C1 3a ruling: no codly-languages bump is needed or available; keep `@preview/codly-languages:0.1.10` with `items="*"` (it exports only `codly-languages`). Only codly's spec in `DEFAULT_PACKAGES` changes.

## Finding: `import "@preview/codly:2.0.0": *` shadows Typst builtins and breaks typsphinx output; `as codly` does not

- **Claim**: codly 2.0's entrypoint defines top-level `line`, `highlight`, `range`, `ref`, `selector`, `number`, `file`, `header`, `footer`, `lang`, `language`, `skip`, `diff`, `callout`, `annotation`, `theme`, `info`, `new`, `codly`, plus `*-set_`/`*-show_` helpers. With a `deps.typ` of `codly: *` + `codly-languages: *` + `gentle-clues: *` imported via `#import "deps.typ": *`, `#line(length: 100%)` failed with `elembic: element 'codly-line': missing positional field 'body'`, and `codly.new(...)` failed with `cannot access fields on user-defined functions` (under `*`, `codly` is the bare constructor alias, not a module). With `#import "@preview/codly:2.0.0" as codly` in `deps.typ` and the consumer doing `#import "deps.typ": *`, `codly.new(raw("print(1)", lang: "python", block: true), offset: 4)` rendered `5 print(1)` with the `Python` badge, and `line(length: 1cm)`, `highlight[x]`, `range(2)` kept their builtin meaning. `codly-init` no longer exists (`unresolved import`).
- **Source**: `codly-2.0.0/codly.typ` (top-level `#let` list; `#let new = codly`; `#import "src/lib.typ": __codly-block-info as info`); typst.app universe page and migration page both import `as codly`; experiments `i1.typ`, `i2.typ`, `i4.typ`, `i5.typ`, `i6.typ`, `ci.typ`, `star/main.typ`, `star/main2.typ`
- **Confidence**: high
- **Why it matters here**: The translator emits `line(length: 100%)` for transitions (`translator.py:6618`) and `info(...)` admonitions via gentle-clues; `items="*"` for codly would break both, so the `PreviewPackage` for codly needs an `as codly` import form (the current `import_line()` only supports `": {items}"`, `typst_deps.py:60-62`). deps.typ then exports the single name `codly` (a module) instead of `codly`, `codly-init`; the templates.rst table (lines ~150-171) row changes from ``codly``, ``codly-init`` to ``codly`` (module: `codly.new`, `codly.set_`, `codly.lang-set_`, ...).

## Finding: migration cost against the existing code

- **Claim**: Pieces touched: `typst_deps.py` `DEFAULT_PACKAGES[0]` spec plus an import-form change (`PreviewPackage.items`/`import_line()` cannot express `as codly` today) and `_INIT_FUNCTION` (`show: codly-init.with()` + `codly(languages: codly-languages)` → `show: codly.lang-set_(languages: codly-languages)`); `translator.visit_literal_block`/`depart_literal_block` (`translator.py:2439-2605`): the fence, `codly_prefix`, list-item `{`/`#{` wrapper and the three `codly(...)` config emissions are replaced by one `codly.new(raw("<escaped>", lang: "<l>", block: true), number-enabled: false?, offset: N-1?, highlighted: (...)?)` expression; `templates/base.typ` only imports deps.typ `*` and needs no codly change (it calls no codly function); `templates.rst` export table and the `typsphinx-init` description paragraph. The `_PREVIEW_PIN_RE` scanner matches `@preview/codly:2.0.0` regardless of `: *` vs ` as codly`, so the drift warning keeps working.
- **Source**: `/home/yuta/Documents/typsphinx/typsphinx/typst_deps.py` lines 36-85, 120-125; `/home/yuta/Documents/typsphinx/typsphinx/translator.py` lines 2439-2605, 6618; `/home/yuta/Documents/typsphinx/typsphinx/templates/base.typ` lines 1-11; `/home/yuta/Documents/typsphinx/docs/source/user_guide/templates.rst` lines 140-190
- **Confidence**: high
- **Why it matters here**: Bounds the plan: one leaf-module change, one translator method pair, docs; no template code change in `base.typ`.

## Finding: string escaping into `raw("...")` round-trips the hard characters

- **Claim**: `codly.new(raw("tab\there \"q\" \\ ``` # $ 日本 😀", block: true, lang: "text"))` compiled and pypdf text read `tab here "q" \ ``` # $ 日本 😀` (tab extracted as space). Only `\` and `"` needed escaping in the Typst string literal (plus `\t`/`\n` if chosen); backtick runs, `#`, `$` and non-ASCII are inert inside a string.
- **Source**: experiment `s.typ`
- **Confidence**: medium
- **Confidence note**: one sample; trailing whitespace and `\r` not tested here — pitfalls owns E2
- **Why it matters here**: Shows the code-mode `raw("...")` form removes the ``` fence's backtick-run problem; feeds the escaping function design for SC2/E2.

## Assigned questions — answers

- Exact codly 2.0 field names/semantics for line numbers off, start number (`offset` value for `:lineno-start: N`), and whole-line highlights relative to offset. → Line numbers off: `number-enabled: false` (default `true`). Start number: `offset: N - 1` (additive; omit for N = 1; `N = 0` → `offset: -1` works). Whole-line highlights: `highlighted: (k, ...)` (or `(k, paint)`), where k is the DISPLAYED number, i.e. Sphinx source index + `offset`; a non-displayed k is silently ignored; entries cycle a multi-colour default palette unless a paint is given. Sources: `codly-2.0.0/src/args.yaml`, migration-1.3 page, experiments `t1.typ`, `h_*.typ`.
- Is codly-languages 0.1.10 compatible with codly 2.0, and which version is current? → Yes: 0.1.10 is current (2025-10-28, Universe index), has no codly dependency, every entry has the `name` codly 2.0 requires, and `codly.lang-set_(languages: codly-languages)` compiled with badges under codly 2.0.0. No bump.
- Which names should deps.typ export (`import "@preview/codly:2.0.0" as codly` vs `*`)? → `as codly`. `*` re-exports `line`, `highlight`, `range`, `ref`, `info`, ... through deps.typ and broke `line(length: 100%)` (emitted by `translator.py:6618`) and made `codly.new` unreachable. With `as codly`, deps.typ exports `codly` (module) + `codly-languages` + the unchanged mitex/gentle-clues/diagraph names + `typsphinx-init`; `codly-init` disappears (breaking, N1).

## Dead ends

- codly 2.0 docs site (`codly.dherse.dev/v2.0.0/`) — only the migration page was read; field semantics were taken from `src/args.yaml` in the published tarball, which is the declaration source the docs are generated from.
- Searching for a codly-languages release newer than 0.1.10 or one declaring codly 2.0 support — none exists on the Universe index; its universe page does not mention codly 2.0.
- `codly.new(raw("", block: true))` (empty block) rendered no visible number or text in PDF extraction; whether that satisfies E3 "renders as a codly block" is left to pitfalls.

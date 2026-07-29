# Stack Research

**Domain:** Typst module/import mechanics and typesetting primitives for API-reference layout (typsphinx v0.7.0 "API rendering design overhaul")
**Researched:** 2026-07-29
**Confidence:** HIGH (Typst mechanics and function signatures verified against `typst.app/docs` current pages and the Typst changelog; typsphinx's own current behavior verified by reading `writer.py`/`builder.py`/`template_engine.py`/`pyproject.toml` directly)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Typst standard library only (no new package) | typst 0.15.x (already pinned, `pyproject.toml:30`) | All new layout primitives (signatures, hanging indent, two-column fields, admonition boxes, colored rules, page-break avoidance) | Every primitive the redesign needs — `raw`, `block`, `pad`, `grid`, `table`, `terms`, `stack`, `stroke`/dictionary sides, `place`, `par(hanging-indent:)` — is stdlib. No `@preview` package supplies anything this milestone needs that stdlib lacks (see "What NOT to Use" and the explicit verdict below) |
| A second bundled `.typ` module, e.g. `typsphinx/templates/_styles.typ` | New file, shipped by typsphinx itself | Consolidates the styling primitives (signature block, field table, admonition box, colored rule, hanging-indent wrappers) into one importable unit instead of inline Python string emission | Matches the milestone's explicit goal ("Style consolidated into an importable Typst module") and mirrors the *already-working* pattern typsphinx uses for `templates/base.typ` — same packaging mechanism, same per-file-import discipline `writer.py` already implements for the four `@preview` imports |

### Supporting Libraries

None. The four already-bundled `@preview` packages (`codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1`) are unchanged by this milestone — nothing in the redesign needs a fifth. See the explicit "no new `@preview` package" verdict below.

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Real `typst.compile()` GATE-01 fixtures (already the project's standing pattern) | Proves each new Typst primitive actually compiles under 0.15 | No new tool needed — `typsphinx/pdf.py`'s existing `compile_typst_file_to_pdf` wrapper is sufficient; the milestone's own invariant already requires this per node-handler change |

## Installation

No installation step. Nothing here is a Python or Typst package dependency — it is (a) Typst standard-library syntax used inside a new bundled `.typ` file, and (b) a `pyproject.toml` package-data glob that **already** covers the new file with zero edits (see finding 5 below).

```bash
# No `pip install` / `npm install` — this section is intentionally empty.
# The only "installation" step is placing the new .typ file under
# typsphinx/templates/ and writing it to outdir at build time (see below).
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| Bundle a second `.typ` file (`_styles.typ`) shipped inside the `typsphinx` package, imported via `#import "_styles.typ": *` from every generated file | A Typst Universe `@preview` package for admonitions/signatures (e.g. something in the spirit of `gentle-clues` but for API signatures) | Only once v0.7.0's explicit deferral (publish later) is acted on — publishing now would violate the milestone's "no fifth `@preview` lockstep site" invariant and adds a network dependency (`typst.compile()` must fetch the package) that a bundled file avoids entirely |
| `raw(lang: "python", ...)` (Typst stdlib, built-in syntax highlighting) for monospace signature text | `codly` (already bundled) applied to signatures too | `codly` is designed for fenced, numbered, framed **code blocks** with line-continuation/line-highlight features; it is the wrong tool for a single-line or few-line API signature that needs monospace + colour only. Reserve `codly` for literal `.. code-block::` output (unchanged), use bare `raw()` for signatures |
| `block(stroke: (left: 2pt + color), inset: ..., breakable: false)` for an admonition-style box with a coloured left rule | `gentle-clues` (already bundled, used today for `.. note::`/`.. warning::` etc.) | Keep using `gentle-clues` for the admonition family (`.. note::`, `.. warning::`, etc.) since it is already bundled and already wired in `templates/base.typ:16-19`/`writer.py:158`. Use bare stdlib `block`+`stroke` dictionary only for the **new** desc/field-list primitives that have no equivalent in `gentle-clues`'s API (a signature block is not an admonition) |
| `state()` + `context` for a document-wide override (e.g. an accent color threaded through many independently-defined helper functions) | Plain function parameters / `.with()` partial application | Only reach for `state()` if a style value must be read from many call sites without being explicitly threaded as a parameter. For this milestone's per-primitive constants (indent width, rule color, field-table column width) plain parameters with defaults are simpler, avoid `context`, and are what the existing three custom templates already use as their idiom (see the override story below) |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| A fifth `@preview` package for signatures/admonitions/citations | Violates the milestone's explicit invariant ("the `@preview` package count stays at **four**... this milestone creates no fifth version-lockstep site") and every capability needed is already in stdlib | Bundle a plain `.typ` module inside the `typsphinx` Python package (ships with the wheel, no network fetch, no version-lockstep test to add) |
| `locate()` / `style()` / `state.at(location)` (Typst's pre-0.13 reactive-layout API) | **Removed** in Typst 0.13 (`typst.app/docs/changelog/0.13.0` — "Removed... `style`, `styles`, `measure`... `state.at`, `counter.at`... `locate`") — this codebase pins `typst>=0.15.0,<0.16` (`pyproject.toml:30`), so any doc/tutorial still showing `locate()` is stale for this project | `context` blocks (the current mechanism for anything that needs to read state/location) — but this milestone does not need `state`/`context` at all (see Alternatives above) |
| `par(hanging-indent:)` to indent an entire block (including its first line) under a heading | `hanging-indent` only affects **wrapped continuation lines of a genuine paragraph** — Typst 0.13 introduced "a distinction between proper paragraphs and just inline-level content" that this property depends on; it does not indent a first line, and does not apply to a `block`/`box` that isn't laid out as a paragraph | `pad(left: 1.5em)[...]` or `block(inset: (left: 1.5em))[...]` to indent an *entire* block uniformly (e.g. `desc_content` under a `desc_signature`, or a nested `py:method::` under its parent `py:class::`) |
| `@import`ing a file purely to get its bare `#show`/`#set` rules to "just apply" | **Does not work.** `#import "x.typ": *` only binds **named** top-level values (`let` bindings — including functions) into the importer's scope. A bare, unnamed `#show raw: ...`/`#set text(...)` statement at a module's top level has no name and is never surfaced by `import` — it only affects that module's own internal evaluation | Wrap the styling in a **named function** that takes `body` and applies the rules internally (`#let with-api-styles(body) = { show raw: ...; body }`), then either call it explicitly (`#show: with-api-styles`) or, if it must apply file-wide with no wrapping call, ship it as something the caller `#include()`s (not `#import`s) at the point where the effect should start — see the module/import mechanics section below |

## Stack Patterns by Variant

**If styling must apply automatically to every subsequent statement in a generated `.typ` file (document-wide, no per-call wrapping):**
- Expose it as a named function, e.g. `#let with-api-styles(body) = { show raw.where(block: false): set text(font: "..."); body }`, and have every generated file (master template `project()` call site, and each included-document's import preamble in `writer.py`) invoke `#show: with-api-styles` right after the `#import "_styles.typ": *` line — this is a textually-scoped show rule, "in effect until the end of the current block or file" per Typst's own styling docs, so it must be re-invoked per generated file exactly like the four `@preview` imports already are.
- Because `writer.py` already re-declares its four `@preview` imports per included document (`writer.py:154-158`), add the new module's import + `#show:` invocation as two more lines in that exact same list — no new architectural mechanism, just one more entry in an existing, already-solved problem.

**If styling is per-call (a signature block, a field table, an admonition-style box):**
- Expose it as a plain function taking `body`/data plus named style parameters with defaults, e.g. `#let api-signature(body, fill: rgb("#f5f5f5"), rule: 2pt + blue) = {...}`. The translator calls `api-signature([...])` directly in the emitted code-mode block — no `show`/`set` needed, no scoping subtlety, and it is trivially overridable per call site with `.with(...)`.

**If a custom user template wants to override:**
- For the per-call functions: `#import "_styles.typ": api-signature` then locally shadow it — `#let api-signature = api-signature.with(fill: my-color)` — before it's used; Typst's ordinary lexical shadowing handles this with zero special machinery.
- For the document-wide `with-api-styles` show-wrapper: don't call it at all, and instead declare an equivalent `#show raw.where(...): ...` of their own (exactly the pattern the three existing custom templates already use for headings/links — e.g. `examples/advanced/_templates/custom.typ:25-53`) — later show-set rules for the same selector win over earlier ones (Typst's own styling docs: "later rules overwriting previous ones"), so a custom template can also call the bundled wrapper **and then** add its own override rule afterward in the same file, and the override composes correctly rather than being silently discarded.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| `typst>=0.15.0,<0.16` (`pyproject.toml:30`) | All functions cited below | Every signature quoted was fetched live from `typst.app/docs` (current = 0.15 docs) on 2026-07-29; none of the functions used here (`raw`, `block`, `box`, `pad`, `grid`, `table`, `terms`, `stack`, `stroke`, `place`, `par`) have an open deprecation as of 0.15 |
| `par(hanging-indent:)` / `par(first-line-indent:)` | Typst ≥0.13 | 0.13 reworked paragraph vs. inline-content handling (breaking change) — irrelevant here since this project only ever targets 0.15, but relevant if any documentation snippet consulted during implementation predates 0.13 |
| `codly:1.3.0` / `codly-languages:0.1.10` / `mitex:0.2.7` / `gentle-clues:1.3.1` | Unchanged by this milestone | The 3-way version-sync surface (`writer.py`, `template_engine.py`, `templates/base.typ`) stays exactly as-is; a fourth site (`examples/advanced/_templates/custom.typ`) already exists unguarded per PROJECT.md's carried-forward note — do not add a fifth anywhere |

---

## 1. Typst module/import mechanics — verdict

**Mechanism, verified against `typst.app/docs/reference/scripting`:**

- `#import "path.typ"` evaluates `path.typ` and inserts the resulting **module value** into scope under the file's own stem name (e.g. `path`).
- `#import "path.typ": name` evaluates `path.typ`, then extracts the **named** top-level bindings `name` (must be `let`-bound in `path.typ` — a value, which may itself be a function) into the current file's scope.
- `#import "path.typ": *` does the same for **all** named top-level bindings ("loads all variables defined in a module").
- `#include "path.typ"` evaluates `path.typ` and returns the **content** it produces — a fundamentally different operation from import (content, not a set of named bindings).

**The `#include()` no-import-inheritance constraint — verified precisely, not assumed:**

typsphinx's own `writer.py:151-152` states: *"Typst's #include() does not inherit imports from parent file, so each file needs its own imports."* This is confirmed independently by three sources: Typst's own GitHub issue tracker (`typst/typst#595`, "Imports that are global to the project", **closed as not planned**), a GitHub discussion (`typst/typst#4809`) where a maintainer explains "You did it the other way around... You included the child file on the parent file, which does basically nothing" for the reverse direction, and the Typst community forum ("Why can't I use a function in a chapter even though I imported it at the start of my main file?" — verbatim answer: *"Imports don't carry over from the files including them."*). Typst modules can only see what they created themselves or imported directly — a `#include()`d child file does not inherit its parent's `#import` statements, and this is Typst's deliberate, permanent design (the feature request to change it was closed as not planned), not a bug that might be fixed. **typsphinx's `writer.py` comment is accurate and current for typst 0.15.**

**Do `show` rules propagate through import?**

No — and this is a load-bearing distinction the milestone's module design must get right. `#import` only surfaces **named** `let` bindings. A bare, unnamed top-level `#show selector: ...` or `#set ...` statement inside an imported module file has no name, so it is never extracted by `import` — it only takes effect within that module file's own (discarded) top-level evaluation. This is corroborated by the Typst forum thread "How can I create a set of shared `set` and `show` rules which can be imported into a theme?": the working pattern shown there uses `#include "styling.typ"` (not import) *inside* a template function's body, immediately before the `body` parameter is inserted — because `include` splices the included file's code in place, its bare `#show`/`#set` statements execute in the *including* file's scope at that exact point, and (per Typst's own styling docs: "show rules are in effect until the end of the current block or file") remain in effect for everything that follows, in that same block, until the block/file ends.

**Practical consequence for the new module (`_styles.typ`):**

1. Ship the layout **primitives** (signature block, field table, admonition-style box, hanging/indent wrapper, colored-rule box) as **named functions** (`#let api-signature(body, ...) = {...}`, etc.). These import cleanly via `#import "_styles.typ": *`, exactly like `codly-init`/`gentle-clues`'s functions already do.
2. If any effect needs to apply **automatically to everything that follows**, without an explicit per-call wrapper (e.g. "every `raw` block inside a `desc_content` should use monospace font X"), expose it as a **named wrapper function** taking `body` (`#let with-api-styles(body) = { show ...; body }`) and have every generated file invoke it explicitly via `#show: with-api-styles` right after importing — do **not** rely on bare top-level show rules "leaking" through import; they won't.
3. Because every generated `.typ` file — master or included — needs its own `#import "_styles.typ": *` line (the same constraint already handled for the four `@preview` packages), the new module's import belongs in exactly the two places `writer.py` already manages this: the included-document preamble (`writer.py:153-159`) and the master-document path via `template_engine.py`'s rendering (through `templates/base.typ`, which is itself never `#include()`d/`#import`ed — it is read as **text** and directly emitted, so its own top-level statements, e.g. `#show link: ...` at `templates/base.typ:31-37`, apply directly with no import/include indirection at all — a third, simpler case that does not have the propagation problem because it *is* the top level of the compiled file).

**The override story:**

- Per-call primitives: a custom template imports the module and locally shadows a name with `.with(...)` partial application (`#let api-signature = api-signature.with(fill: my-color)`) — ordinary Typst lexical shadowing, no special mechanism required.
- Document-wide wrapper (`with-api-styles`): a custom template either skips calling it and writes its own equivalent `#show` rules (the exact pattern all three existing custom templates already use for headings/links, e.g. `examples/advanced/_templates/custom.typ:25-53`), or calls it and then layers a further `#show` rule for the same selector afterward — Typst composes show-set rules in declaration order, "later rules overwriting previous ones" per the official styling docs, so this composes correctly rather than silently losing the override.
- `state()`/`context` is **not** needed for this milestone's override story — it solves a different problem (a value read from many independently-defined call sites without explicit parameter threading, e.g. a document-wide theme color library). Community guidance (the `typst-community/guidelines` project, multiple forum threads) converges on: use plain function parameters for anything with a small number of call sites, reserve `state()` for genuinely non-parameter-threadable cases. This milestone's primitives are all directly called by the translator, so plain parameters suffice.

---

## 2. Typst typesetting primitives — current-syntax signatures (typst 0.15, verified 2026-07-29)

All signatures below were fetched live from `typst.app/docs/reference/...` (current = 0.15 docs).

### `raw` — monospace, syntax-highlighted signature/code text

```typst
raw(
  text: str,
  block: bool = false,
  lang: none | str = none,
  align: alignment = start,
  syntaxes: str | path | bytes | array = (),
  theme: none | auto | str | path | bytes = auto,
  tab-size: int = 2,
) → content
```

**For this layout problem:** `raw(lang: "python", "class Foo:")` gets monospace font + built-in syntax colouring **for free, from Typst's standard library** — no `@preview` package required. This is the correct tool for API-signature text (`desc_signature`/`desc_name`/`desc_sig_*` nodes), replacing the current `strong(text(...))` proportional-bold emission. Reserve the already-bundled `codly` package for actual fenced `.. code-block::` output (multi-line, line-numbered code) — `codly` is the wrong tool for a signature line; bare `raw()` is right-sized and dependency-free.

### `par` — hanging indent for *wrapped continuation lines* of one paragraph

```typst
par(
  leading: length,
  spacing: length,
  justify: bool,
  justification-limits: dictionary,
  linebreaks: auto | str,
  first-line-indent: length | dictionary,  // default (amount: 0pt, all: false)
  hanging-indent: length,                  // default 0pt
  body: content,
) → content
```

`hanging-indent`: *"The indent that all but the first line of a paragraph should have."* This is a paragraph-internal property, not a block-indent tool — it only affects **line-wrapping** within one `par`. **Typst 0.13 breaking change (still current behavior at 0.15):** Typst introduced a formal distinction between "proper paragraphs" and "just inline-level content," which `hanging-indent`/`first-line-indent` depend on — this property will not do anything on content that never forms a genuine paragraph (a lone `raw` block, for instance). Use it only where the intent is genuinely "wrapped lines of running prose indent under the first line" (e.g. a long field description that wraps).

### `block` — indenting/framing/page-break control for a whole unit

```typst
block(
  width: auto | relative,
  height: auto | relative | fraction,
  breakable: bool = true,
  fill: none | color | gradient | tiling = none,
  stroke: none | length | color | gradient | stroke | tiling | dictionary = (:),
  radius: relative | dictionary = (:),
  inset: relative | dictionary = (:),
  outset: relative | dictionary = (:),
  spacing: auto | relative | fraction = 1.2em,
  above: auto | relative | fraction = auto,
  below: auto | relative | fraction = auto,
  clip: bool = false,
  sticky: bool = false,
  body: none | content = none,
) → content
```

**`inset: (left: 1.5em)`** — indenting an entire block (all lines, unlike `par`'s `hanging-indent`) under a heading, e.g. `desc_content` under its `desc_signature`, or a nested `py:method::` under its parent `py:class::`. This is the correct primitive for "indent a whole block" (item 2 of the question) — `par(hanging-indent:)` is the wrong tool for that job (see above).

**`breakable: false`** — *"Whether the block can be broken and continue on the next page."* Default `true`. Set to `false` to keep a signature + its immediately following content together: *"the block will jump to its own page"* rather than splitting mid-content across a page boundary, per the official docs' own worked example. This is the correct primitive for "page-break avoidance between a signature and its description" (item 2) — it is a coarser tool than true CSS-style "keep-with-next" (it moves the *whole* block, not just prevents a split at one join point), but for a signature+short-description unit this is the right, simple fit; do not reach for `place`/`place.flush()` for this (see `place` below — it solves a different problem).

**`stroke: (left: 2pt + color)`** — a coloured **left rule only**. `block`'s `stroke` dictionary accepts the same per-side keys as `rect` (`top`, `right`, `bottom`, `left`, plus `x`/`y` shorthands and `rest` for "everything not explicitly set") — *"A dictionary describing the stroke for each side individually... omitted keys will use their previously set value, or the default stroke if never set."* Combined with `fill: color.lighten(90%)` and `inset:`, this is the correct primitive for a "framed or tinted box with a coloured left rule" (item 2) — the classic admonition-box look, buildable from stdlib alone without `gentle-clues` for anything that isn't a genuine admonition node.

### `box` — inline-level container (sizes content within a line)

```typst
box(
  width: auto | relative | fraction = auto,
  height: auto | relative = auto,
  baseline: auto | relative | dictionary | alignment = (at: auto, shift: 0% + 0pt),
  fill: none | color | gradient | tiling = none,
  stroke: none | length | color | gradient | stroke | tiling | dictionary = (:),
  radius: relative | dictionary = (:),
  inset: relative | dictionary = (:),
  outset: relative | dictionary = (:),
  clip: bool = false,
  body: none | content = none,
) → content
```

Used when a styled element (e.g. a small type-annotation pill on a parameter) must sit **inline within a paragraph** rather than as its own block — `block` would force a line break, `box` would not.

### `pad` — uniform block-level indent

```typst
pad(
  left: relative = 0% + 0pt,
  top: relative = 0% + 0pt,
  right: relative = 0% + 0pt,
  bottom: relative = 0% + 0pt,
  x: relative = 0% + 0pt,
  y: relative = 0% + 0pt,
  rest: relative = 0% + 0pt,
  body: content,
) → content
```

A lighter-weight alternative to `block(inset:)` when no fill/stroke/breakability control is needed — just "shift this content in by N" (e.g. nested member indentation). Prefer `block(inset:)` when the same call site also needs `fill`/`stroke`/`breakable` (avoids stacking two wrapper calls); prefer bare `pad` when indentation is the *only* effect needed.

### `grid` — two-column aligned term/description layout (structural)

```typst
grid(
  columns: auto | int | relative | fraction | array = (),
  rows: auto | int | relative | fraction | array = (),
  gutter: auto | int | relative | fraction | array = (),
  column-gutter: auto | int | relative | fraction | array = (),
  row-gutter: auto | int | relative | fraction | array = (),
  inset: relative | array | dictionary | function = (:),
  align: auto | array | function | alignment = auto,
  fill: none | color | gradient | tiling | array | function = none,
  stroke: none | length | color | gradient | stroke | tiling | array | dictionary | function = (:),
  ..children: content,
) → content
```

For `field_list` → a two-column "Parameters"/"Returns" table (item 1 of the FEATURES gap), `grid(columns: (auto, 1fr), ...)` with the field name in column 1 and body in column 2 gives real column alignment without visible table borders (grid draws no strokes by default, unlike `table`).

### `table` — structural/tabular content with visible rules

```typst
table(
  columns: auto | int | relative | fraction | array = (),
  rows: auto | int | relative | fraction | array = (),
  gutter: auto | int | relative | fraction | array = (),
  column-gutter: auto | int | relative | fraction | array = (),
  row-gutter: auto | int | relative | fraction | array = (),
  inset: relative | array | dictionary | function = 0% + 5pt,
  align: auto | array | function | alignment = auto,
  fill: none | color | gradient | tiling | array | function = none,
  stroke: none | length | color | gradient | stroke | tiling | array | dictionary | function = 1pt + black,
  ..content,
) → content
```

Semantically distinct from `grid` per Typst's own docs: use `table` when the content is genuinely tabular data (announced as a table to assistive technology); use `grid` when arranging content that merely needs alignment (a term/description pair is arguably borderline — this project already uses `table`-as-`figure` for genuine RST tables, so **prefer `grid`, not `table`, for the field-list two-column layout** to avoid conflating "API doc field alignment" with "user-authored data table" semantics and to avoid an unwanted visible-border default).

### `terms` — term/description list (the RST `field_list` semantic match)

```typst
terms(
  tight: bool = true,
  separator: content = h(amount: 0.6em, weak: true),
  indent: length = 0pt,
  hanging-indent: length = 2em,
  spacing: auto | length = auto,
  ..children: content | array,
) → content
```

Worth flagging even though `grid` is the recommendation above: `terms` is Typst's *native* term-list element (its own `hanging-indent` is per-item, unlike `par`'s) and is closer to `field_list`'s actual semantics (a term + its description) than either `grid` or `table`. It is a legitimate alternative to `grid` for the field-list redesign — the requirements-definition step should pick one deliberately rather than defaulting to whichever is mentioned first; `grid` gives more explicit column-width control (useful when aligning "Parameters"/"Returns"/"Raises" labels to a common width), while `terms` is the more semantically native element and needs less manual column-width tuning.

### `stack` — sequential layout along one axis

```typst
stack(
  dir: direction = ttb,
  spacing: none | relative | fraction = none,
  ..children: relative | fraction | content,
) → content
```

Lower-level than `grid`/`table` — useful inside a custom primitive function body for stacking a signature block above its content block with explicit `spacing:`, when `block`'s own `above`/`below` spacing isn't granular enough.

### `stroke` — the type used by every `stroke:` parameter above

```typst
stroke(
  paint: auto | color | gradient | tiling,
  thickness: auto | length,
  cap: auto | str,
  join: auto | str,
  dash: none | auto | str | array | dictionary,
  miter-limit: auto | float,
) → stroke
```

In practice for this milestone, the shorthand forms suffice: `2pt + blue` (thickness + color), or a dictionary `(left: 2pt + blue)` for per-side strokes (see `block` above) — the full constructor is rarely called directly.

### `place` — NOT the tool for signature/description page-break avoidance

```typst
place(
  alignment: auto | alignment = start,
  scope: str = "column",
  float: bool = false,
  clearance: length = 1.5em,
  dx: relative = 0% + 0pt,
  dy: relative = 0% + 0pt,
  body: content,
) → content
```

`place` overlays or floats content **out of the normal flow** — it is for figures/margin notes/watermarks, not for "keep these two flow elements together." Its `float: true` mode positions content at a container's top/bottom and displaces in-flow content, with `place.flush()` to force pending floats to settle — none of that is what "avoid breaking a signature away from its description" needs. **Use `block(breakable: false)` for that instead** (see above); do not use `place` for this requirement.

---

## 3. Does the redesign need a new `@preview` package? — explicit verdict

**No.** Every capability required by the four target features (desc/field_list redesign, admonition/rubric/topic redesign, the styling module itself, citation rendering) is available in Typst 0.15's standard library:

- Monospace + syntax-coloured signatures → stdlib `raw()` (built-in syntax highlighting, no package)
- Hanging/first-line indent → stdlib `par(hanging-indent:, first-line-indent:)`
- Whole-block indent under a heading → stdlib `pad`/`block(inset:)`
- Two-column term/description layout → stdlib `grid` or `terms`
- Framed/tinted boxes with a coloured left rule → stdlib `block(fill:, stroke: (left: ...), inset:)`
- Page-break avoidance between signature and description → stdlib `block(breakable: false)`
- A `thebibliography`-equivalent labelled citation list → stdlib `terms`/`grid` + Typst's native `label`/`link` (the same anchor/link machinery `desc_signature`'s cross-reference support already uses, per `translator.py:4695-4720`)

**A package that *would* help but is explicitly out of scope:** a purpose-built academic bibliography package (e.g. something in the spirit of a BibTeX-style citation-list renderer, or Typst's own built-in `bibliography()`/`cite()` machinery, which is a *separate* stdlib feature from plain citation-node rendering and pulls in CSL-processing complexity) could produce a more polished citation list than a hand-built `terms`/`grid` construction. **This is out of scope for v0.7.0**: the milestone's own requirement is a `thebibliography`-equivalent labelled list with a working `[Label]` → definition link — not full bibliography/CSL support — and pulling in Typst's `bibliography()` function would be a materially larger scope change (it expects `.bib`/`.yml` bibliography files, CSL styles, and a different citation-node mapping than docutils' `citation`/`citation_reference` nodes provide) than this milestone's greenfield `visit_citation`/`visit_label`/`visit_citation_reference` handlers call for. Write the v0.7.0 requirement against stdlib-only (`terms`/`grid` + `label`/`link`), and file Typst's native bibliography support as a distinct, future, deliberately-scoped item if ever wanted.

**Conclusion:** the milestone's own invariant — "the `@preview` package count stays at **four** ... this milestone creates no fifth version-lockstep site" — is achievable with zero tension against the typesetting requirements. No requirement should be written that implies a new package.

---

## 4. Typst Universe packaging requirements (for the deferred future publication — informs the API boundary only)

**Kept short per the question's own scope note — this is not being done this milestone.**

A package submitted to `typst/packages` (the repository backing Typst Universe) needs a root `typst.toml` manifest:

- **Required by the compiler itself:** `name` (the package's identifier within its namespace), `version` (full major.minor.patch, SemVer), `entrypoint` (path to the `.typ` file evaluated on import).
- **Required additionally for submission to `typst/packages`:** `authors` (list, each optionally with email/homepage/GitHub handle), `license` (a valid SPDX-2 expression; the package must also ship a `LICENSE` file or link to one), `description` (short, proofread — it appears in the package list verbatim).
- **Naming rules:** package names must not be "the obvious or canonical name" for the functionality (a naming-squat rule), must not contain the word "typst" (redundant in context), and must use `kebab-case` if multi-word.
- **Structural constraint that matters for the API-boundary decision now:** within a package, all paths are resolved relative to the **package root**, and package code cannot read files outside the package (no reaching into the consuming project's directory) — a package cannot assume access to project-level resources unless the *consuming* document explicitly passes them in (e.g. via the `path` constructor, per Typst's own docs). Reproducibility is enforced by immutability: once submitted, package versions cannot be changed or removed except in exceptional cases, and every import must pin an exact version (no version ranges).

**What this means for the module's API boundary today (the only actionable takeaway for this milestone):** design `_styles.typ`'s public functions to be **self-contained** — taking `body`/data and style parameters as explicit arguments, not reaching for anything outside the module file itself (no reads of project-relative paths, no assumptions about sibling files). That is precisely the same discipline a Typst Universe package's `entrypoint` file would need, so nothing in a stdlib-only, parameter-driven module design precludes later publication — this is a "don't paint yourself into a corner" check, not new work.

---

## 5. Python-side packaging — verified against the actual files

**Current declaration (`pyproject.toml:70-71`):**

```toml
[tool.setuptools.package-data]
"typsphinx" = ["templates/*.typ"]
```

This is a **glob**, not an enumerated file list. **Finding: shipping a second `.typ` file (e.g. `typsphinx/templates/_styles.typ`) requires zero `pyproject.toml` changes** — the existing `templates/*.typ` pattern already matches any new file dropped into `typsphinx/templates/`. Confirmed by reading the manifest directly; no `MANIFEST.in` or other packaging config exists in this repository that would need a matching update.

**How the existing `base.typ` is located and loaded (`template_engine.py:260-272`):**

```python
def get_default_template_path(self) -> str:
    package_dir = Path(__file__).parent
    template_dir = package_dir / "templates"
    default_template = template_dir / "base.typ"
    return str(default_template)
```

A plain filesystem path relative to `__file__` — not `importlib.resources`. This works because setuptools installs declared `package-data` as real files under `site-packages/typsphinx/templates/`, so `Path(__file__).parent / "templates" / "_styles.typ"` would resolve identically for a new bundled file, with the same reliability the existing code already depends on (no editable-install/zipped-egg edge case introduced — this repo's own worktree-isolation setup already exercises this exact path pattern via `uv sync --extra dev`).

**How the builder currently writes the bundled template to the output directory (`builder.py:521-592`, `_write_template_file`):**

Called once per build from `prepare_writing()` (`builder.py:328-332`). It resolves the template via `TemplateEngine.get_template_content()` (which internally calls the priority-walk `resolve_template()`, falling back to the bundled `base.typ` when no custom `typst_template`/package config is set), then writes the **content string** to `outdir/_template.typ` — skipped entirely when a `typst_package` is configured alone (no custom template), per the D-01 routing rule documented at `builder.py:560-566`.

**What shipping a second bundled `.typ` module needs, concretely:**

1. **No `pyproject.toml` change** (finding above — the glob already covers it).
2. **A new builder method paralleling `_write_template_file()`**, e.g. `_write_styles_module()`, called from `prepare_writing()` alongside the existing call (`builder.py:332`). Unlike `_write_template_file()`, this should run **unconditionally** (not gated on the `typst_package`-alone D-01 exception) — because, per the milestone's own description, the new module is imported by **every** generated file (master *and* included documents), not only by master documents that apply a template. Read the bundled file the same way `get_default_template_path()` does (`Path(__file__).parent / "templates" / "_styles.typ"`) and write its content verbatim to `outdir/_styles.typ` (or a name of the requirements' choosing) at the outdir root — mirroring `_template.typ`'s placement so the same depth-based relative-import-path computation `writer.py`'s `_compute_template_import_path()` already implements for `_template.typ` (`writer.py:73-119`) can be reused/generalized for the new file, rather than inventing a second path-relativization scheme.
3. **Do not** route this through `copy_template_assets()`/`_copy_template_directory()`/`_copy_explicit_assets()` (`builder.py:630-802`) — that machinery is keyed off the **user's** `typst_template` config and copies **user project** assets (fonts, images, logos) referenced by a **custom** template; it has no knowledge of typsphinx's own bundled package resources and copying through it would incorrectly make the styles module's presence conditional on the user having configured a custom template at all.
4. **Import-path wiring** follows the exact model `writer.py` already uses for the four `@preview` imports: add one `#import "..._styles.typ": *` line (relativized like `_template.typ` already is) to (a) the included-document preamble block (`writer.py:153-159`) and (b) the master-document template rendering path (either inside `templates/base.typ` itself as a plain top-level `#import`, since `base.typ` is emitted as literal text at the top of the compiled master and therefore has no include/import-inheritance problem of its own — or via the same relative-path mechanism as `_template.typ` if the module must also be reachable independently of which template a user has configured).

## Sources

- `typst.app/docs/reference/scripting` — import/include semantics, verified 2026-07-29 (WebFetch)
- `typst.app/docs/reference/styling` — show/set rule scoping and precedence ("in effect until the end of the current block or file"; "later rules overwriting previous ones"), verified 2026-07-29 (WebSearch/tavily)
- `typst.app/docs/reference/text/raw`, `.../model/par`, `.../layout/block`, `.../layout/box`, `.../layout/pad`, `.../layout/grid`, `.../model/table`, `.../model/terms`, `.../layout/stack`, `.../layout/place`, `.../visualize/stroke`, `.../visualize/rect` — function signatures, verified live 2026-07-29 (WebFetch, current = 0.15 docs)
- `typst.app/docs/changelog/0.13.0`, `0.14.0`, `0.15.0` — breaking-change history (`locate`/`style`/`state.at` removal in 0.13; paragraph/inline-content distinction in 0.13), verified 2026-07-29 (tavily search + WebFetch)
- `github.com/typst/typst` issue #595 ("Imports that are global to the project", closed not planned) and discussion #4809 — confirms `#include()` import-non-inheritance is deliberate, permanent Typst design, not a bug (tavily search)
- Typst community forum: "Why can't I use a function in a chapter even though I imported it at the start of my main file?", "How can I create a set of shared `set` and `show` rules which can be imported into a theme?", "How can I have global configuration parameters for a module/package?", "How to have different color schemes for template?" — override/theming idioms (tavily search)
- `github.com/typst/packages` `docs/manifest.md` — `typst.toml` requirements for Typst Universe submission (tavily search)
- typsphinx repository, read directly: `typsphinx/writer.py:41-166` (master/included branching, per-file `@preview` re-import, `_compute_template_import_path`), `typsphinx/builder.py:328-332,521-592,630-802` (`prepare_writing`, `_write_template_file`, `copy_template_assets` family), `typsphinx/template_engine.py:260-330` (`get_default_template_path`, `resolve_template` priority walk), `typsphinx/translator.py:4619-5096` (current `desc_*`/`field_list`/`rubric` emission), `pyproject.toml:70-71` (`package-data` glob), `typsphinx/templates/base.typ` (existing bundled template, direct-text-emission model), `examples/advanced/_templates/custom.typ` (existing custom-template override idiom), `CLAUDE.md` (the `@preview` version-sync hazard), `.planning/PROJECT.md` (v0.7.0 milestone scope)

---
*Stack research for: Typst module/import mechanics and typesetting primitives for typsphinx v0.7.0*
*Researched: 2026-07-29*

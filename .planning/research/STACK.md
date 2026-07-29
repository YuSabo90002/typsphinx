# Stack Research

**Domain:** Typst module/import mechanics and typesetting primitives for API-reference layout (typsphinx v0.7.0 "API rendering design overhaul")
**Researched:** 2026-07-29 (styling-mechanism section re-researched and empirically re-verified 2026-07-29 against the owner's revised per-directive-function proposal)
**Confidence:** HIGH (Typst mechanics and function signatures verified against `typst.app/docs` current pages and the Typst changelog; typsphinx's own current behavior verified by reading `writer.py`/`builder.py`/`template_engine.py`/`pyproject.toml` directly; **the per-directive restyling mechanism section below is additionally verified by actually compiling ~15 minimal Typst programs with this repo's own `typst-py 0.15.0` venv — every verdict in that section has a reproducible compiled example, not just documentation reasoning**)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Typst standard library only (no new package) | typst 0.15.x (already pinned, `pyproject.toml:30`) | All new layout primitives (signatures, hanging indent, two-column fields, admonition boxes, colored rules, page-break avoidance) | Every primitive the redesign needs — `raw`, `block`, `pad`, `grid`, `table`, `terms`, `stack`, `stroke`/dictionary sides, `place`, `par(hanging-indent:)` — is stdlib. No `@preview` package supplies anything this milestone needs that stdlib lacks (see "What NOT to Use" and the explicit verdict below) |
| A second bundled `.typ` module, e.g. `typsphinx/templates/_typsphinx.typ` | New file, shipped by typsphinx itself | One function **1:1 with each API/description directive kind** (`api-signature`, `api-field-name`, …), each with a baked-in default look **and** a distinct Typst `<label>` so a user's own template can restyle exactly one kind via `show <label>: ...` — see the dedicated decision section below | Matches the milestone's explicit goal ("Style consolidated into an importable Typst module", and the owner's revised 1:1-per-directive proposal) and mirrors the *already-working* pattern typsphinx uses for `templates/base.typ` — same packaging mechanism, same per-file-import discipline `writer.py` already implements for the four `@preview` imports |

### Supporting Libraries

None. The four already-bundled `@preview` packages (`codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1`) are unchanged by this milestone — nothing in the redesign needs a fifth. See the explicit "no new `@preview` package" verdict below.

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Real `typst.compile()` GATE-01 fixtures (already the project's standing pattern) | Proves each new Typst primitive actually compiles under 0.15 | No new tool needed — `typsphinx/pdf.py`'s existing `compile_typst_file_to_pdf` wrapper is sufficient; the milestone's own invariant already requires this per node-handler change. This same technique (`.venv/bin/python` + `typst.compile()` + `pypdf` text extraction) is what produced every verdict in the "Per-Directive User Restyling" section below |

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
| Bundle a second `.typ` file (`_typsphinx.typ`) shipped inside the `typsphinx` package, imported via `#import "_typsphinx.typ": *` from every generated file | A Typst Universe `@preview` package for admonitions/signatures (e.g. something in the spirit of `gentle-clues` but for API signatures) | Only once v0.7.0's explicit deferral (publish later) is acted on — publishing now would violate the milestone's "no fifth `@preview` lockstep site" invariant and adds a network dependency (`typst.compile()` must fetch the package) that a bundled file avoids entirely |
| `raw(lang: "python", ...)` (Typst stdlib, built-in syntax highlighting) for monospace signature text | `codly` (already bundled) applied to signatures too | `codly` is designed for fenced, numbered, framed **code blocks** with line-continuation/line-highlight features; it is the wrong tool for a single-line or few-line API signature that needs monospace + colour only. Reserve `codly` for literal `.. code-block::` output (unchanged), use bare `raw()` for signatures |
| `block(stroke: (left: 2pt + color), inset: ..., breakable: false)` for an admonition-style box with a coloured left rule | `gentle-clues` (already bundled, used today for `.. note::`/`.. warning::` etc.) | Keep using `gentle-clues` for the admonition family (`.. note::`, `.. warning::`, etc.) since it is already bundled and already wired in `templates/base.typ:16-19`/`writer.py:158`. Use bare stdlib `block`+`stroke` dictionary only for the **new** desc/field-list primitives that have no equivalent in `gentle-clues`'s API (a signature block is not an admonition) |
| `state()` + `context` for a document-wide override (e.g. an accent color threaded through many independently-defined helper functions) | Plain function parameters / `.with()` partial application | Only reach for `state()` if a style value must be read from many call sites without being explicitly threaded as a parameter. For this milestone's per-primitive constants (indent width, rule color, field-table column width) plain parameters with defaults are simpler, avoid `context`, and are what the existing three custom templates already use as their idiom. (`state()` is also empirically confirmed to work for the *per-directive restyling* problem — see the decision section below — but the label-selector mechanism wins that specific decision on simplicity; this row's guidance about plain constants is unaffected) |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| A fifth `@preview` package for signatures/admonitions/citations | Violates the milestone's explicit invariant ("the `@preview` package count stays at **four**... this milestone creates no fifth version-lockstep site") and every capability needed is already in stdlib | Bundle a plain `.typ` module inside the `typsphinx` Python package (ships with the wheel, no network fetch, no version-lockstep test to add) |
| `locate()` / `style()` / `state.at(location)` (Typst's pre-0.13 reactive-layout API) | **Removed** in Typst 0.13 (`typst.app/docs/changelog/0.13.0` — "Removed... `style`, `styles`, `measure`... `state.at`, `counter.at`... `locate`") — this codebase pins `typst>=0.15.0,<0.16` (`pyproject.toml:30`), so any doc/tutorial still showing `locate()` is stale for this project | `context` blocks (the current mechanism for anything that needs to read state/location) |
| `par(hanging-indent:)` to indent an entire block (including its first line) under a heading | `hanging-indent` only affects **wrapped continuation lines of a genuine paragraph** — Typst 0.13 introduced "a distinction between proper paragraphs and just inline-level content" that this property depends on; it does not indent a first line, and does not apply to a `block`/`box` that isn't laid out as a paragraph | `pad(left: 1.5em)[...]` or `block(inset: (left: 1.5em))[...]` to indent an *entire* block uniformly (e.g. `desc_content` under a `desc_signature`, or a nested `py:method::` under its parent `py:class::`) |
| `@import`ing a file purely to get its bare `#show`/`#set` rules to "just apply" | **Does not work.** `#import "x.typ": *` only binds **named** top-level values (`let` bindings — including functions) into the importer's scope. A bare, unnamed top-level `#show raw: ...`/`#set text(...)` statement has no name and is never surfaced by `import` — it only affects that module's own internal evaluation | Ship each restylable primitive as a **named function returning labeled content** (`#let api-signature(body) = [#block(...) <typsphinx-signature>]`), and have the *user's own template* write `show <typsphinx-signature>: it => {...}` — this is the winning mechanism from the decision section below, and it composes correctly across `#include()` with zero per-file wrapper-invocation ceremony |
| `#show mysig: it => {...}` where `mysig` is a bare user-defined `#let` function (the owner's originally-proposed literal syntax) | **Empirically disproven** (this is the orchestrator's own pre-verified finding, reproduced again while researching the alternatives below): Typst raises `only element functions can be used as selectors`. `show`/`set` selectors only accept genuine **element functions** (Typst's own built-ins like `figure`, `heading`, `raw`, or a future user-defined element type). Plain `#let` functions are not element functions — this is confirmed current, unresolved Typst behavior (`typst/typst#147`, open since 2023-03-22, see decision section below) | Attach a `<label>` (or a `figure(kind: "...")`) to the function's *return content*, and `show`/select on **that** instead of on the function itself — see the decision section immediately below |

## Per-Directive User Restyling — Mechanism Decision

**Owner's goal (verbatim from the re-run brief):** *"a user must be able to restyle each API directive kind independently, from their own template, without patching typsphinx."* The literal mechanism the owner originally proposed (`#show mysig: it => {...}` selecting directly on a bare `#let` function) is disproven — Typst's `show`/`set` selectors only accept genuine **element functions**, and a plain `#let` function is not one. This section evaluates every alternative that *can* deliver the same functional goal, with a real `typst.compile()` run backing every verdict (all runs executed with this repo's own `.venv/bin/python`, `typst-py 0.15.0`, in `/tmp/.../scratchpad/typst-tests/`).

### Comparison table

| Mechanism | Works? | Side effects | Works across `#include()` | Works in code mode | Requires template cooperation | Per-kind granularity |
|---|---|---|---|---|---|---|
| **1. `figure(kind: "...")`** | **Yes** | Composes *badly* with a user's own generic `show figure: ...` rule — both fire, nested (measured). Needs `supplement: none, caption: none` boilerplate on every call to suppress unwanted captioning/auto-numbering. `outline(target: figure)` (not the project-default `outline()`, which only targets headings) would list typsphinx's signature blocks unless the user adds a `.where(kind: ...)` filter. Zero extra vertical spacing versus a bare `block()` when caption/supplement are suppressed (measured) | **Yes** (measured) | Yes, trivially (plain function call, no special syntax) | No — sane baked-in defaults render with no template at all | Yes — one `kind:` string per directive |
| **2. Label selector (`<label>`)** ← **winner** | **Yes** | None observed beyond: never use the styling label itself as a `link()`/`ref()` target (raises "label occurs multiple times" fatal, as expected — but typsphinx would never do this). Fires on **every** occurrence of a repeated, non-unique label with no special declaration needed (measured) | **Yes** (measured) | Yes, but requires the `[#expr <label>]` bracket-content wrapping form — a bare code-mode expression cannot carry a label suffix directly (`raw(...) <label>` is a parse error; `[#raw(...) <label>]` is not) | No — sane baked-in defaults render with no template at all | Yes — one distinct label per directive |
| **3. `state()` + `context`** | **Yes** | Works, but heavier ceremony: needs one `state()` declaration *and* one `context {...}` wrapper per directive kind, both bundled and imported. The `context` requirement is fully internal to the shipped function — the translator's call site is an ordinary function call, unaffected | **Yes** (measured — a state update issued inside the master's `project()`, *before* `#include(...)`, is visible to `context` reads inside the included file) | Yes — the function itself does `context {...}` internally, so callers never write `context` | No — state's own default value renders with no template at all | Yes — one state variable per directive |
| **4. Styles dict threaded through `project(api-styles: (...), body)`** | **No, as literally proposed** | N/A — proven inert: passing the dict has **zero effect** on the translator's emitted calls, because those calls resolve their target function via each generated file's own *static* `#import`, completely independent of any runtime argument value passed into `project()` (measured directly — output stayed at the shipped default in every case) | N/A (doesn't work) | N/A | Requires a template, but the template still can't make it work without secretly reimplementing mechanism 3 internally (converting the dict into `state()` updates) — at that point it *is* mechanism 3 with extra indirection, not an independent mechanism | N/A |
| **5. `#let` shadowing / re-binding in the template file** | **No** | N/A — proven inert: a custom template's own `#let api-signature = ...` rebinding only changes *that file's* lexical scope. The translator's emitted calls live in a different file (the master `.typ` or an included `.typ`) that resolved `api-signature` via its **own** `#import` line at the top of that file — an entirely separate, already-resolved binding the template's shadowing cannot reach (measured directly) | N/A (doesn't work) | N/A | Requires a template, and still doesn't work | N/A |
| **6. User-definable custom "element" functions** (would make the owner's original literal syntax work) | **Not available in Typst 0.15** | N/A | N/A | N/A | N/A | N/A |

### Verbatim minimal Typst source for each verdict

**1. `figure(kind:)` — works, but collides with a user's own generic figure rule:**

```typst
#let api-signature(body) = figure(
  kind: "typsphinx-signature", supplement: none, caption: none, body,
)

#show figure.where(kind: "typsphinx-signature"): it => [SPECIFIC-RULE-FIRED #it.body]
#show figure: it => [GENERIC-RULE-FIRED #it]   // a user's OWN, unrelated rule

#api-signature(raw("sig one", lang: "python"))
#figure(table(columns: 2, [a],[b],[c],[d]), caption: [A real table])
```
Compiled output (text-extracted from the produced PDF):
```
GENERIC-RULE-FIRED SPECIFIC-RULE-FIRED sig one
GENERIC-RULE-FIRED
a b
c d
Table 1: A real table
```
Both rules fire, nested, on the typsphinx element — a generic `show figure: ...` a user writes for their *own* figures unavoidably also wraps typsphinx's signature blocks unless the user remembers to exclude `kind: "typsphinx-signature"` explicitly. This is a genuine, measured composability risk unique to this mechanism.

Zero-extra-spacing check (position markers via `context here().position()` before/after a bare `block()` vs. the `figure(kind:)`-wrapped equivalent, both with identical fill/inset): the gap between markers was **19.87mm in both cases**, i.e. `figure(kind:, caption: none, supplement: none)` adds no spacing/float/breakable side effect beyond an equivalent `block()` once captioning is suppressed.

Outline-pollution check: typsphinx's own `base.typ` calls `outline(depth: ..., indent: auto)` with **no** `target:` argument — Typst's outline default target is `heading` only, so this default call never lists figures of any kind (measured: a doc with one `figure(kind: "typsphinx-signature")` and one real captioned table produced an outline containing only the heading). Pollution only appears if a user explicitly writes `outline(target: figure)` (measured: this listed both the typsphinx element and the real table) — avoidable with `outline(target: figure.where(kind: "table"))` but is an easy foot-gun to omit.

**2. Label selector — the winner:**

```typst
#show <typsphinx-signature>: it => [STYLED[#it]]

[#raw("sig one", lang: "python") <typsphinx-signature>]
[#raw("sig two", lang: "python") <typsphinx-signature>]
```
Compiled output: `STYLED[sig one]` and `STYLED[sig two]` — fires on **every** occurrence of a repeated, non-unique label, no per-instance declaration needed.

Collision check against typsphinx's existing `_emit_id_anchors()` unique-anchor pattern (`[#metadata(none) <label>]`, one per node id): a doc combining a repeated styling label with typsphinx's real unique-anchor pattern, plus a `link()` to one of the unique anchors, compiles cleanly. The **only** failure mode is trying to `link()`/`ref()` the *repeated* styling label itself:
```
label `<typsphinx-signature>` occurs multiple times in the document
```
— which typsphinx would never do (it only `show`s that label, never links to it), so this is not a real risk in practice, only a documented constraint on what the label must never be used for.

**#include() propagation — the decisive test:**

```typst
// _typsphinx.typ (shipped module)
#let api-signature(body) = [#body <typsphinx-signature>]

// child.typ (an INCLUDED, non-master document — gets an import prelude, no template)
#import "_typsphinx.typ": api-signature
= Chapter A
#api-signature(raw("def foo():", lang: "python"))

// main.typ (the MASTER document)
#import "_typsphinx.typ": api-signature
#let project(body) = {
  show <typsphinx-signature>: it => [STYLED-BY-TEMPLATE[#it]]
  body
}
#show: project
#include "child.typ"
```
Compiled output:
```
Chapter A
STYLED-BY-TEMPLATE[def foo():]
```
**The master's template-level `show <label>: ...` rule, established inside `project()` before `body`, reaches content generated inside the `#include()`d child file** — even though the child file never imports or calls anything related to styling itself. This works because Typst show rules apply to the **realized content tree** for the remainder of the enclosing block, and `#include()` splices the child's content into that same tree at the point of inclusion — it is not a scoping boundary for already-established show rules, only for `#import` bindings (the `writer.py:151-152` constraint is specifically about imports, not about show-rule reach).

**Code-mode compatibility check** (translator emits `#{ ... }`, not markup):
```typst
#let api-signature(body) = [#body <typsphinx-signature>]
#show <typsphinx-signature>: it => [STYLED[#it]]
#{
  par({ api-signature(raw("class Foo:", lang: "python")) })
}
```
Compiled output: `STYLED[class Foo:]`. Works, but note the syntax constraint measured along the way: a bare code-mode expression cannot carry a label suffix (`raw(body, lang: "python") <typsphinx-signature>` is a parse error, `expected semicolon or line break`); the module's `#let` functions must wrap their return value in `[#... <label>]` bracket-content syntax, not attach the label to a code-mode value directly. `figure(kind: ...)` (mechanism 1) does **not** have this constraint — `kind:` is an ordinary named parameter, usable directly in code mode with no bracket-wrapping.

**Tweak-not-replace idiom** (a user narrows one property instead of rewriting the whole element):
```typst
#show <typsphinx-signature>: it => {
  set text(fill: blue)
  it
}
```
Compiles cleanly — `it` is the labeled element itself, and its own fields (e.g. `it.body` for a labeled `block()`) are directly accessible, exactly like a built-in element's fields:
```typst
#let api-signature(body) = [#block(fill: rgb("#f5f5f5"), inset: 6pt,
  raw(body, block: true, lang: "python")) <typsphinx-signature>]

#show <typsphinx-signature>: it => block(
  fill: rgb("#eef6ff"), inset: 8pt, stroke: (left: 2pt + blue), it.body,
)
```
Compiles and correctly re-wraps only the inner `raw()` content in the new box.

**3. `state()` + `context` — also works, heavier ceremony:**

```typst
// _typsphinx.typ
#let typsphinx-sig-style = state("typsphinx-sig-style", "DEFAULT")
#let api-signature(body) = context {
  let s = typsphinx-sig-style.get()
  [STATE=#s: #body]
}

// main.typ
#import "_typsphinx.typ": typsphinx-sig-style, api-signature
#let project(body) = {
  typsphinx-sig-style.update("OVERRIDDEN-BY-TEMPLATE")
  body
}
#show: project
#api-signature(raw("class Bar:", lang: "python"))
#include "child.typ"     // child.typ also calls api-signature(...)
```
Compiled output:
```
STATE=OVERRIDDEN-BY-TEMPLATE: class Bar:
STATE=OVERRIDDEN-BY-TEMPLATE: def foo():
```
Confirms the state update issued in the master's `project()`, before `#include(...)`, is visible to `context` reads on **both** sides of the include boundary — for the same underlying reason as mechanism 2 (state resolves against final document order, not per-file scope). The `context` requirement lives entirely inside the module's own function body; the caller (translator, or a user's template) never writes `context` itself.

**4. Naive dict-argument to `project()` — proven inert:**

```typst
// _typsphinx.typ: DEFAULT function, statically bound at each import site.
#let api-signature(body) = [DEFAULT-STYLE: #body]

// main.typ
#import "_typsphinx.typ": api-signature
#let project(api-styles: (:), body) = {
  // api-styles is a local variable here; nothing reads it.
  body
}
#show: project.with(api-styles: (signature: it => [OVERRIDDEN: #it]))
#api-signature(raw("class Bar:", lang: "python"))
#include "child.typ"     // child.typ also calls api-signature(...) directly
```
Compiled output: `DEFAULT-STYLE: class Bar: DEFAULT-STYLE: def foo():` — the overriding value **never takes effect anywhere**, in the master file or the included file. This directly answers the quality-gate's crux question: yes, `body` is lazy Typst content and `project()` *can* establish state/show rules that later reach it (mechanisms 2 and 3 prove that half) — but a plain unused function **argument** has no channel into an already-statically-imported call site. The dict would have to be turned into `state()` updates inside `project()` to have any effect, which collapses mechanism 4 into mechanism 3 with an extra layer of indirection and no benefit.

**5. `#let` shadowing in the template file — proven inert across files:**

```typst
// _typsphinx.typ
#let api-signature(body) = [DEFAULT-STYLE: #body]

// custom_template.typ (the USER's own file)
#import "_typsphinx.typ": api-signature as base-signature
#let api-signature(body) = [SHADOWED-IN-TEMPLATE: #base-signature(body)]
#let project(body) = body

// main.typ (what writer.py actually emits: imports project from the
// template, AND separately imports api-signature directly for its own
// emitted calls -- exactly matching how @preview imports work today)
#import "custom_template.typ": project
#import "_typsphinx.typ": api-signature
#show: project
#api-signature(raw("class Bar:", lang: "python"))
```
Compiled output: `DEFAULT-STYLE: class Bar:` — the template's shadowed `api-signature` is never consulted, because `main.typ` resolved its own `api-signature` name via its own `#import` line, a completely separate static binding. Lexical shadowing cannot cross a file boundary in Typst; this mirrors the general fact already established in the "module/import mechanics" section below (imports bind names per-file, not globally).

**6. Custom element functions — checked against the current upstream issue tracker:**

Directly measured via the GitHub API (2026-07-29): `typst/typst#147`, "Support for user-defined elements/types" — **state: `open`**, opened 2023-03-22, most recent activity 2026-02-16 (11 comments). Typst maintainer `laurmaedje` (2023-03-25): *"We plan to add support for user-defined element functions in the future. These would also work with set and show."* Same maintainer (2024-10-01, in response to a "still no progress?" comment): *"Active work on this hasn't started yet."* No further status update is recorded after that as of the measurement date. **Conclusion: this capability does not exist in Typst 0.15 and has no committed timeline** — it cannot be relied on for v0.7.0, or realistically for any near-term Typst release.

**`set` rules specifically, for completeness** (the owner's brief said "via `show` or `set`"): `set` rules cannot target a label selector at all, only element functions — confirmed:
```typst
#set <typsphinx-signature>(fill: red)
```
fails to parse: `expected identifier`. So of the owner's two named mechanisms, only `show` is deliverable; `set` is not, for the same underlying reason mechanism 6 is unavailable (no element-function machinery to hang a `set` rule on).

### Recommendation

**Winner: label selectors (mechanism 2).** It is the simplest mechanism that fully satisfies the owner's functional goal, and it is the one with the fewest sharp edges once measured:

- No figure-family baggage to suppress (no `caption`/`supplement`/`kind` ceremony, no counter, no outline entry, no risk of a user's own unrelated `show figure: ...` rule silently also firing on typsphinx's elements — measured to happen with mechanism 1).
- Fires on every occurrence, needs no per-file registration beyond the one `#import` typsphinx already manages for every generated file.
- Confirmed to reach across `#include()` boundaries exactly the same way mechanism 3 does, because both rely on the same underlying fact: show/state effects apply to the realized document tree, not per source file.
- Composes with the "tweak, don't replace" idiom (`show <label>: it => { set text(...); it }`) as well as full replacement.
- Requires **no** template cooperation for correct default rendering — a template that imports nothing from the module still gets typsphinx's own baked-in default look, satisfying "the three existing custom templates keep working unmodified."

**Runner-up: `figure(kind: "...")` (mechanism 1).** Fully functional and arguably more "Typst-idiomatic" (`kind` exists precisely for "a custom object living in the figure family"), and it loses only on ergonomics/safety margin, not capability: (a) the measured composability collision with a user's own generic `show figure: ...` rule is a real, easy-to-hit foot-gun that a project shipping this to end users would need to document defensively; (b) every call site needs `supplement: none, caption: none` boilerplate purely to suppress machinery this milestone doesn't want; (c) `outline(target: figure)` pollution is avoidable but is one more thing a user must remember to filter. If a future requirement specifically wants typsphinx's signature/field blocks to participate in Typst's native "List of Figures" machinery, mechanism 1 becomes attractive again — that is not this milestone's ask.

**`state()` + `context` (mechanism 3)** is a legitimate complementary tool for a genuinely different problem (a *scalar* theme value, like one shared accent color, read from many independently-defined call sites with no natural "one function per consumer" shape) but is unnecessary machinery for "restyle this one directive kind" when a label selector already solves it with less code and no `context` ceremony at any call site.

**Mechanisms 4 and 5 are ruled out**, not merely disfavored — both are empirically inert for this problem, for the same root cause: Typst's `#import` bindings (and therefore the translator's emitted function calls) are resolved statically, per file, at each file's own `#import` statement, and neither a runtime argument value nor a same-named `#let` binding in an unrelated file can retroactively redirect an already-resolved import.

**Mechanism 6 (and, by extension, the owner's originally literal `show mysig: ...` syntax) is confirmed not achievable in Typst 0.15**, and is not on any committed Typst roadmap as of this research date (`typst/typst#147`, open, no active work as of the last maintainer comment). This is the one part of the owner's original framing that cannot be delivered as literally stated — see the explicit limitation note below.

### The resulting module API surface

```typst
// typsphinx/templates/_typsphinx.typ (shipped inside the typsphinx package,
// written to outdir alongside _template.typ, imported by every generated
// .typ file — master AND included — exactly like the four @preview imports)

// One function per desc_*/field_*/admonition directive kind, 1:1 as the
// owner proposed. Each: (a) has a sane, typographically-designed DEFAULT
// baked directly into the function body, so a template that imports
// nothing from this module still renders correctly; (b) wraps its content
// in ONE distinct <label>, giving a user's own template an independent,
// per-kind restyling hook via `show`.

#let api-signature(body) = [#block(
  fill: rgb("#f5f5f5"),
  inset: 6pt,
  radius: 2pt,
  raw(body, block: true, lang: "python"),
) <typsphinx-signature>]

#let api-field-name(body) = [#strong(body) <typsphinx-field-name>]

// ... the same shape repeats for the remaining directive kinds in scope
// this milestone (api-desc-content / hanging-indent body wrapper,
// api-field-body, api-admonition-title, etc.) -- one label, one baked-in
// default, per kind. The exact primitive set is a requirements-definition
// decision (see the typesetting-primitives section below for the stdlib
// building blocks each one would use); the label/default-styling PATTERN
// documented here is what this research verifies, not the final function
// list.
```

The translator's emission is an ordinary function call, unchanged in shape from what `translator.py` already does for e.g. `strong(...)`:

```python
# translator.py, illustrative -- same call shape works from code mode
self.body.append(f'api-signature("{escaped_signature_text}")')
```

A user's own template, to restyle **only** the signature kind and leave every other directive kind at typsphinx's shipped default:

```typst
// the user's own _templates/custom.typ -- imports project() only, exactly
// as the three existing in-repo custom templates already do
#let project(body) = {
  show <typsphinx-signature>: it => block(
    fill: rgb("#eef6ff"),
    inset: 8pt,
    stroke: (left: 2pt + blue),
    it.body,
  )
  // <typsphinx-field-name> and every other kind: untouched, stays default
  body
}
```

This exact shape — default-only master, default-only included document, and a template overriding one kind while a second kind stays default — was compiled together as one scenario (both a `main_defaults.typ` with no template and a `main_override.typ` with the above `project()`, each including a child document that also calls both primitive functions): the defaults-only run rendered both kinds at their shipped defaults everywhere (master and included document alike); the override run rendered `<typsphinx-signature>` as `CUSTOM-SIG[...]` in **both** the master-level and the included-file-level calls, while `<typsphinx-field-name>` remained unstyled/default in both places — confirming per-kind granularity and `#include()` propagation simultaneously, in the shape typsphinx's actual pipeline uses.

### What the owner's original proposal cannot get, stated explicitly

The owner's proposal, read literally — *"define style functions 1:1 with the directives... the template can then apply styling to those functions via `show` or `set`"* — asked for the **function itself** to be the thing `show`/`set` selects on (`show api-signature: ...`, or `set api-signature(...)`). That literal syntax is **not achievable** in Typst 0.15: `show`/`set` selectors require genuine element functions, user-defined element functions do not exist yet (`typst/typst#147`, open, no committed timeline), and `set` additionally never accepts a label selector as a substitute (confirmed above — `set <label>(...)` fails to parse regardless of element-function status).

What **is** fully achievable, and delivers the owner's actual functional goal (independent per-directive restyling from the user's own template, with zero typsphinx patching, defaults intact when the template does nothing) is the label-selector pattern above: the directive-kind function stays a plain `#let` function (as the owner asked), but the thing a template `show`s is the **label the function attaches to its own output**, not the function's name. Any resulting requirement/roadmap language should say "restyle via `show <label>: ...`" rather than promising "`show api-signature: ...`" or "`set api-signature(...)`" — the latter two are not deliverable on the current Typst version this project targets.

## Stack Patterns by Variant

**Per-directive restyling (the primary ask this milestone needs):** see the "Per-Directive User Restyling — Mechanism Decision" section above in full — the short version is: ship one function per directive kind, each returning `[#default-look <distinct-label>]`; a user's template overrides one kind with `show <that-label>: it => {...}`; nothing is required of a template that does nothing.

**If a genuinely document-wide, non-per-directive value is needed** (e.g. one shared accent color read by several *different* primitive functions, rather than "restyle this one directive kind"): use `state()` + `context`, following the same cross-`#include()`-safe pattern verified in mechanism 3 above — declare the state in the bundled module, update it from the user's `project()` before `body`, read it via an internal `context` block inside each consuming primitive function so no caller ever has to write `context` itself.

**If styling is a simple, non-restylable-by-users constant** (an internal layout constant with no user-facing override story at all, e.g. a fixed inset amount): a plain function parameter with a default is simplest — no `show`, no `state`, no label, just `#let api-signature(body, inset: 6pt) = {...}`.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| `typst>=0.15.0,<0.16` (`pyproject.toml:30`) | All functions cited below | Every signature quoted was fetched live from `typst.app/docs` (current = 0.15 docs) on 2026-07-29; none of the functions used here (`raw`, `block`, `box`, `pad`, `grid`, `table`, `terms`, `stack`, `stroke`, `place`, `par`, `figure`, `state`) have an open deprecation as of 0.15. The label-selector and `figure(kind:)` mechanisms above were compiled directly against this repo's pinned `typst-py 0.15.0`, not inferred from documentation |
| `par(hanging-indent:)` / `par(first-line-indent:)` | Typst ≥0.13 | 0.13 reworked paragraph vs. inline-content handling (breaking change) — irrelevant here since this project only ever targets 0.15, but relevant if any documentation snippet consulted during implementation predates 0.13 |
| `codly:1.3.0` / `codly-languages:0.1.10` / `mitex:0.2.7` / `gentle-clues:1.3.1` | Unchanged by this milestone | The 3-way version-sync surface (`writer.py`, `template_engine.py`, `templates/base.typ`) stays exactly as-is; a fourth site (`examples/advanced/_templates/custom.typ`) already exists unguarded per PROJECT.md's carried-forward note — do not add a fifth anywhere |
| User-defined element functions (`typst/typst#147`) | Not in 0.15, no committed release target | Do not design the module API around this landing during v0.7.0 — the label-selector pattern is the correct present-day substitute, not a stopgap pending #147 |

---

## 1. Typst module/import mechanics — verdict

**Mechanism, verified against `typst.app/docs/reference/scripting`:**

- `#import "path.typ"` evaluates `path.typ` and inserts the resulting **module value** into scope under the file's own stem name (e.g. `path`).
- `#import "path.typ": name` evaluates `path.typ`, then extracts the **named** top-level bindings `name` (must be `let`-bound in `path.typ` — a value, which may itself be a function) into the current file's scope.
- `#import "path.typ": *` does the same for **all** named top-level bindings ("loads all variables defined in a module").
- `#include "path.typ"` evaluates `path.typ` and returns the **content** it produces — a fundamentally different operation from import (content, not a set of named bindings).

**The `#include()` no-import-inheritance constraint — verified precisely, not assumed:**

typsphinx's own `writer.py:151-152` states: *"Typst's #include() does not inherit imports from parent file, so each file needs its own imports."* This is confirmed independently by three sources: Typst's own GitHub issue tracker (`typst/typst#595`, "Imports that are global to the project", **closed as not planned**), a GitHub discussion (`typst/typst#4809`) where a maintainer explains "You did it the other way around... You included the child file on the parent file, which does basically nothing" for the reverse direction, and the Typst community forum ("Why can't I use a function in a chapter even though I imported it at the start of my main file?" — verbatim answer: *"Imports don't carry over from the files including them."*). Typst modules can only see what they created themselves or imported directly — a `#include()`d child file does not inherit its parent's `#import` statements, and this is Typst's deliberate, permanent design (the feature request to change it was closed as not planned), not a bug that might be fixed. **typsphinx's `writer.py` comment is accurate and current for typst 0.15.**

**Do `show`/`state` effects propagate through `#include()` despite imports not doing so? — yes, and this is the load-bearing distinction the module design turns on.**

`#import` is a strictly per-file, static, name-binding operation — it never propagates, as established above. But `show` rules and `state()` updates are a **completely different kind of mechanism**: they act on the realized document content tree for the remainder of the enclosing block, and `#include()` splices the included file's content into that tree at the point of inclusion. The "Per-Directive User Restyling" section above empirically proves this distinction matters in practice: a master document's `show <label>: ...` rule (or `state().update(...)` call), established inside `project()` before `#include(...)` runs, **does** reach content generated inside the included file — even though that same file's own `#import "_typsphinx.typ": api-signature` line is completely independent of, and unaffected by, anything the master's template does. Do not conflate "imports don't propagate across `#include()`" (true) with "show/state effects don't propagate across `#include()`" (false, measured) — the milestone's styling-module design depends on getting this distinction right.

**Do bare, unnamed top-level `show`/`set` statements propagate through `#import` (a different question from the one above)?**

No. `#import` only surfaces **named** `let` bindings. A bare, unnamed top-level `#show selector: ...` or `#set ...` statement inside an imported module file has no name, so it is never extracted by `import` — it only takes effect within that module file's own (discarded) top-level evaluation. This is corroborated by the Typst forum thread "How can I create a set of shared `set` and `show` rules which can be imported into a theme?": the working pattern shown there uses `#include "styling.typ"` (not import) *inside* a template function's body, immediately before the `body` parameter is inserted — because `include` splices the included file's code in place, its bare `#show`/`#set` statements execute in the *including* file's scope at that exact point. This fact is why the winning per-directive mechanism does **not** rely on a bare top-level show rule inside `_typsphinx.typ` "leaking" through import — instead, each primitive function attaches its own `<label>`, and it is the **user's own template file** that writes the (named, file-local) `show <label>: ...` rule, which needs no propagation-through-import at all because it is declared directly in the file where it needs to take effect (`project()`, which then reaches included content via the show/state mechanism described above, not via import).

**Practical consequence for the new module (`_typsphinx.typ`):**

1. Ship the per-directive primitives as **named functions** returning **labeled content** (`#let api-signature(body) = [#... <typsphinx-signature>]`, etc. — see the decision section above for the full pattern and its verification). These import cleanly via `#import "_typsphinx.typ": *`, exactly like `codly-init`/`gentle-clues`'s functions already do.
2. Because every generated `.typ` file — master or included — needs its own `#import "_typsphinx.typ": *` line (the same constraint already handled for the four `@preview` packages), the new module's import belongs in exactly the two places `writer.py` already manages this: the included-document preamble (`writer.py:153-159`) and the master-document path via `template_engine.py`'s rendering (through `templates/base.typ`, which is itself never `#include()`d/`#import`ed — it is read as **text** and directly emitted, so its own top-level statements, e.g. `#show link: ...` at `templates/base.typ:31-37`, apply directly with no import/include indirection at all — a third, simpler case that does not have the propagation problem because it *is* the top level of the compiled file).
3. `state()`/`context` is **not** needed to deliver the per-directive restyling goal — the label-selector mechanism delivers it with strictly less machinery (see decision section). Reserve `state()` for a genuinely different problem class (one scalar value shared by many independently-defined call sites, e.g. a document-wide theme color).

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
- Per-directive user restyling → stdlib `<label>` + `show <label>: ...` (see the decision section above) — no package needed for this either
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

**What this means for the module's API boundary today (the only actionable takeaway for this milestone):** design `_typsphinx.typ`'s public functions to be **self-contained** — taking `body`/data and style parameters as explicit arguments, not reaching for anything outside the module file itself (no reads of project-relative paths, no assumptions about sibling files). The label-selector pattern recommended above fits this cleanly: each function's only "public surface" beyond its return value is the fixed label name it attaches, which is exactly the same discipline a Typst Universe package's `entrypoint` file would need — this is a "don't paint yourself into a corner" check, not new work.

---

## 5. Python-side packaging — verified against the actual files

**Current declaration (`pyproject.toml:70-71`):**

```toml
[tool.setuptools.package-data]
"typsphinx" = ["templates/*.typ"]
```

This is a **glob**, not an enumerated file list. **Finding: shipping a second `.typ` file (e.g. `typsphinx/templates/_typsphinx.typ`) requires zero `pyproject.toml` changes** — the existing `templates/*.typ` pattern already matches any new file dropped into `typsphinx/templates/`. Confirmed by reading the manifest directly; no `MANIFEST.in` or other packaging config exists in this repository that would need a matching update.

**How the existing `base.typ` is located and loaded (`template_engine.py:260-272`):**

```python
def get_default_template_path(self) -> str:
    package_dir = Path(__file__).parent
    template_dir = package_dir / "templates"
    default_template = template_dir / "base.typ"
    return str(default_template)
```

A plain filesystem path relative to `__file__` — not `importlib.resources`. This works because setuptools installs declared `package-data` as real files under `site-packages/typsphinx/templates/`, so `Path(__file__).parent / "templates" / "_typsphinx.typ"` would resolve identically for a new bundled file, with the same reliability the existing code already depends on (no editable-install/zipped-egg edge case introduced — this repo's own worktree-isolation setup already exercises this exact path pattern via `uv sync --extra dev`).

**How the builder currently writes the bundled template to the output directory (`builder.py:521-592`, `_write_template_file`):**

Called once per build from `prepare_writing()` (`builder.py:328-332`). It resolves the template via `TemplateEngine.get_template_content()` (which internally calls the priority-walk `resolve_template()`, falling back to the bundled `base.typ` when no custom `typst_template`/package config is set), then writes the **content string** to `outdir/_template.typ` — skipped entirely when a `typst_package` is configured alone (no custom template), per the D-01 routing rule documented at `builder.py:560-566`.

**What shipping a second bundled `.typ` module needs, concretely:**

1. **No `pyproject.toml` change** (finding above — the glob already covers it).
2. **A new builder method paralleling `_write_template_file()`**, e.g. `_write_style_module_file()`, called from `prepare_writing()` alongside the existing call (`builder.py:332`). Unlike `_write_template_file()`, this should run **unconditionally** (not gated on the `typst_package`-alone D-01 exception) — because, per the milestone's own description, the new module is imported by **every** generated file (master *and* included documents), not only by master documents that apply a template. Read the bundled file the same way `get_default_template_path()` does (`Path(__file__).parent / "templates" / "_typsphinx.typ"`) and write its content verbatim to `outdir/_typsphinx.typ` (or a name of the requirements' choosing) at the outdir root — mirroring `_template.typ`'s placement so the same depth-based relative-import-path computation `writer.py`'s `_compute_template_import_path()` already implements for `_template.typ` (`writer.py:73-119`) can be reused/generalized for the new file, rather than inventing a second path-relativization scheme.
3. **Do not** route this through `copy_template_assets()`/`_copy_template_directory()`/`_copy_explicit_assets()` (`builder.py:630-802`) — that machinery is keyed off the **user's** `typst_template` config and copies **user project** assets (fonts, images, logos) referenced by a **custom** template; it has no knowledge of typsphinx's own bundled package resources and copying through it would incorrectly make the styles module's presence conditional on the user having configured a custom template at all.
4. **Import-path wiring** follows the exact model `writer.py` already uses for the four `@preview` imports: add one `#import "..._typsphinx.typ": *` line (relativized like `_template.typ` already is) to (a) the included-document preamble block (`writer.py:153-159`) and (b) the master-document template rendering path (either inside `templates/base.typ` itself as a plain top-level `#import`, since `base.typ` is emitted as literal text at the top of the compiled master and therefore has no include/import-inheritance problem of its own — or via the same relative-path mechanism as `_template.typ` if the module must also be reachable independently of which template a user has configured).

## Sources

- `typst.app/docs/reference/scripting` — import/include semantics, verified 2026-07-29 (WebFetch)
- `typst.app/docs/reference/styling` — show/set rule scoping and precedence ("in effect until the end of the current block or file"; "later rules overwriting previous ones"), verified 2026-07-29 (WebSearch/tavily)
- `typst.app/docs/reference/text/raw`, `.../model/par`, `.../layout/block`, `.../layout/box`, `.../layout/pad`, `.../layout/grid`, `.../model/table`, `.../model/terms`, `.../layout/stack`, `.../layout/place`, `.../visualize/stroke`, `.../visualize/rect`, `.../model/figure`, `.../foundations/state` — function signatures, verified live 2026-07-29 (WebFetch, current = 0.15 docs)
- `typst.app/docs/changelog/0.13.0`, `0.14.0`, `0.15.0` — breaking-change history (`locate`/`style`/`state.at` removal in 0.13; paragraph/inline-content distinction in 0.13), verified 2026-07-29 (tavily search + WebFetch)
- `github.com/typst/typst` issue #595 ("Imports that are global to the project", closed not planned) and discussion #4809 — confirms `#include()` import-non-inheritance is deliberate, permanent Typst design, not a bug (tavily search)
- `github.com/typst/typst` issue **#147** ("Support for user-defined elements/types", **open**, opened 2023-03-22, latest activity 2026-02-16, 11 comments) — directly measured via `gh api repos/typst/typst/issues/147` and its comments feed 2026-07-29; maintainer `laurmaedje` confirms user-defined element functions (which would make `show`/`set` work directly on a bare function) are planned but "active work on this hasn't started yet" (2024-10-01, most recent maintainer status update on record)
- `github.com/typst/typst` issues **#662** ("What is an element function?") and **#6141** ("add warning/error message for show-rules with symbols") — corroborate that only element functions are valid `show`/`set`/`query` selectors, and that Typst currently gives no warning when a show rule silently has no effect on a non-element-function selector (WebSearch)
- **Direct empirical verification, this session, `.venv/bin/python` + `typst-py 0.15.0` + `pypdf`** — ~15 minimal Typst programs compiled to prove every verdict in the "Per-Directive User Restyling" section: `figure(kind:)` composability collision with a generic `show figure:` rule; `figure(kind:)` zero-extra-spacing measurement via `context here().position()`; `outline()` default-vs-explicit-`target:figure` pollution; label-selector per-occurrence firing; label/unique-anchor non-collision and the "duplicate label" fatal boundary; label-selector propagation across a real two-file `#include()`; label-selector code-mode compatibility and its bracket-wrapping syntax requirement; `it.body`/tweak-not-replace field access; `state()`+`context` propagation across `#include()`; the naive `project(api-styles: (...))` dict-argument inertness; `#let` shadowing-across-files inertness; the `set <label>(...)` parse failure. Source files and outputs preserved at `/tmp/claude-1000/-home-yuta-Documents-typsphinx/da10050d-a94f-45a4-b5e7-3556727242d7/scratchpad/typst-tests/` for this session
- Typst community forum: "Why can't I use a function in a chapter even though I imported it at the start of my main file?", "How can I create a set of shared `set` and `show` rules which can be imported into a theme?", "How can I have global configuration parameters for a module/package?", "How to have different color schemes for template?" — override/theming idioms (tavily search)
- `github.com/typst/packages` `docs/manifest.md` — `typst.toml` requirements for Typst Universe submission (tavily search)
- typsphinx repository, read directly: `typsphinx/writer.py:41-166` (master/included branching, per-file `@preview` re-import, `_compute_template_import_path`), `typsphinx/builder.py:328-332,521-592,630-802` (`prepare_writing`, `_write_template_file`, `copy_template_assets` family), `typsphinx/template_engine.py:260-330` (`get_default_template_path`, `resolve_template` priority walk), `typsphinx/translator.py:4619-5096` (current `desc_*`/`field_list`/`rubric` emission), `pyproject.toml:70-71` (`package-data` glob), `typsphinx/templates/base.typ` (existing bundled template, direct-text-emission model), `examples/advanced/_templates/custom.typ`, `docs/source/_typst/custom_template.typ` (existing custom-template override idiom, both re-read in full for this re-run), `CLAUDE.md` (the `@preview` version-sync hazard), `.planning/PROJECT.md` (v0.7.0 milestone scope), `.planning/research/ARCHITECTURE.md` (the two import-injection sites, master/include split, style-module-plumbing build-order recommendation)

---
*Stack research for: Typst module/import mechanics and typesetting primitives for typsphinx v0.7.0*
*Researched: 2026-07-29 (styling-mechanism section re-researched and empirically verified 2026-07-29)*

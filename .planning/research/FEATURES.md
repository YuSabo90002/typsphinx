# Feature Research

**Domain:** Sphinx builder / reST→Typst translator — "real-world robustness" (v0.6.0, Issue #114)
**Researched:** 2026-07-11
**Confidence:** HIGH (translator.py read directly for existing conventions) / MEDIUM (docutils/Sphinx node internals, cross-checked against Sphinx's own `extdev/nodes` docs + `sphinx.addnodes` source) / MEDIUM-LOW (a couple of Typst-side syntax recommendations flagged individually below — verify with a real `typst compile` before locking the requirement)

> Supersedes the previous (2026-07-09) version of this file, which researched the **v0.5.0 forward-ecosystem** milestone (Sphinx 9/typst 0.15 pin work). This version researches the **v0.6.0 real-world robustness** milestone (Issue #114 fatal-bug fix + high-frequency dropped-node support).

## Context: why most gaps are non-fatal but two are fatal

`typsphinx`'s `TypstTranslator` is a `docutils.nodes.SparseNodeVisitor`-style visitor: a node type with no `visit_X`/`depart_X` method falls through to the generic "unknown node" path, which **logs a warning and drops/degrades the content** — it does not abort the build. That is the mechanism behind the ~1979 warnings on a real Sphinx `doc/` build: `versionmodified`, `desc_returns`, footnotes, `topic`, etc. are all silently dropped or text-flattened today, but the **PDF still compiles**.

The Issue #114 pair is categorically different: `visit_figure`/`visit_image`/`visit_reference` already have handlers, but for two input shapes they emit **syntactically invalid Typst source** (`invalid number suffix: px`, and an illegal `link(url, image(...))text(caption)` juxtaposition). That is a `typst.TypstError` raised by the *compiler*, at `finish()`/PDF-compile time — it aborts the **entire** document (a whole book-length master doc, since a single `#include`d file's malformed `.typ` poisons the parent compile). This is why Issue #114 must land before any node-support work: every other fix in this milestone is validated by literally compiling Sphinx's `doc/` tree, and that compile is currently impossible.

**Rule of thumb for categorization below:** "FATAL" = raises `TypstError` at compile time today (2 known cases). Everything else is "non-fatal / warning-only" = a `visit_*`/`depart_*` method is simply missing or the render is degraded, and Sphinx-doc's own text still fully compiles around it.

## Feature Landscape

### P0 — Fatal Bugs (Issue #114 core, must land first)

| Bug | Root Cause | Correct Typst Form | Complexity | Depends On |
|-----|-----------|---------------------|------------|------------|
| `px`/CSS length units on `image(width:/height:)` | `visit_image` (translator.py:1527-1533) copies Sphinx's `node["width"]`/`node["height"]` (e.g. `"300px"`) into `width: {width}` verbatim. Typst's length type has no `px` unit — `invalid number suffix: px`. | Convert recognized CSS units to Typst units before emission: `px`→`pt` (numeric conversion, not passthrough — `Npx` is **never** valid Typst), bare numbers → append a default unit, `%`/`em`/`in`/`cm`/`pt` pass through as-is (already-valid Typst length/ratio suffixes). A small `_convert_css_length(value: str) -> str` helper is the right shape; unrecognized units should log-and-drop rather than emit garbage. | LOW–MEDIUM | Existing `visit_image` |
| `:target:`-linked figure invalid juxtaposition | `visit_figure`/`visit_image`/`visit_reference` currently compose independently: a `reference` wrapping an `image` inside a `figure` produces `link(url, image(...))` (wrong call shape — `link` takes a body as its 2nd *content-block* argument when given a destination, not two positional exprs) immediately followed by the caption text with no separator, i.e. `link(...)text(...)` — two adjacent expressions is a Typst parse error. | `#figure(link("url")[#image("path")], caption: [Caption text])` — i.e., `link(dest)[content]` (content-block form, not `link(dest, content)`), and the caption must remain the `figure()` function's own `caption:` **named argument**, never bare trailing text. | MEDIUM (needs `visit_figure`/`visit_reference`/`visit_image` to cooperate — currently they don't share enough state to know "the image inside me is target-wrapped") | `visit_figure`, `visit_image`, `visit_reference` — this is the one node type in this milestone that requires touching **three** existing handlers together, not just adding one |

**Both bugs share one fix pattern worth calling out to the requirements author:** the figure/image code path needs a shared "am I inside a `:target:`-wrapped figure image" flag (mirroring the existing `in_figure`/`in_caption` booleans already on the translator) so `visit_reference` knows to emit `link("url")[` + defer to `visit_image` for the content instead of the normal `link("url", ...)` two-arg form it uses everywhere else. Do not special-case only figures — a `:target:`-linked *standalone* image (no figure wrapper) hits the same bug and needs the same content-block `link[...]` form.

### Table Stakes (must render for a technical/API doc to be usable)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `versionmodified` (`versionadded`/`versionchanged`/`deprecated`/`versionremoved`) | 972 occurrences in Sphinx's own docs alone — any API reference of nontrivial age uses these constantly; missing them silently deletes deprecation warnings from the PDF, which is worse than a rendering glitch | LOW | See dedicated spec below — reuse the `emph`/`strong` primitives already used by `visit_rubric`/`visit_field_name`, **not** the gentle-clues admonition box |
| Empty-`refuri` / `refid` cross-reference fix | 596 occurrences; current `visit_reference` (translator.py:1970) reads `node.get("refuri", "")` only — it never checks `refid`, so same-document anchor links (a very common, always-resolved case) are misdiagnosed as broken and degraded to plain text | LOW–MEDIUM | See dedicated analysis below — likely the single highest-leverage fix in this milestone by volume |
| `desc_returns` | 187 occurrences; every typed function/method signature with a return annotation (`def f(x) -> int`) uses it | LOW | Direct extension of the existing `desc_parameterlist`/`desc_parameter` `text(...)` pattern (translator.py:2577-2621) |
| `desc_signature_line` | 59 occurrences; multi-line signatures (C++ templates, long overloaded signatures) split across lines — without this, either the lines run together with no break or (worse) crash on missing-node | LOW–MEDIUM | Sibling-position check identical to `depart_desc_parameter`'s `next_node(descend=False, siblings=True)` idiom, inserting `linebreak()` instead of `text(", ")` |
| `desc_inline` | 13 occurrences; inline signature fragments from roles like `:cpp:expr:` | LOW | Same children as `desc_signature` but must **not** apply the `strong()` block-signature wrapper (that wrapper is only correct for a standalone declaration, not text embedded mid-sentence) |
| `desc_optional` | 6 occurrences; optional trailing parameters, e.g. C `printf(fmt[, args])` | LOW–MEDIUM | Bracket-wrap (`text("[")` / `text("]")`) around the optional parameter run; must support nesting (`desc_optional` inside `desc_optional`) for multi-level optional args |
| `footnote` / `footnote_reference` | Common in prose-heavy docs (not counted in the milestone's headline list, but explicitly named as a target); currently unimplemented → silently dropped | MEDIUM–HIGH | See dedicated spec below — the correct Typst-native design is architecturally different from a literal docutils port |
| `transition` | Horizontal-rule scene breaks (`----`); trivial but currently unimplemented → silently dropped, losing document structure signal | LOW | Empty node (docutils disallows children) — pure `visit`, no `depart` needed |
| `topic` | Named boxed asides (`.. topic:: Title`); has a `title` child + body, structurally identical to the admonition nodes already supported | LOW | **Reuse `_visit_admonition`/`_depart_admonition` verbatim** with `clue_type="clue"` — topic's `title` child already routes through the existing admonition-aware `visit_title` buffer-swap. Cheapest table-stakes item in this milestone. |
| `line` / `line_block` | Addresses, epigraphs, poetry-style content where line breaks must be preserved verbatim (not reflowed) | LOW–MEDIUM | Emit each `line`'s content followed by an explicit `linebreak()`; nested `line_block`s (indentation levels) need a left-indent wrapper (`pad(left: ...)` or block-level indent param) |
| `glossary` | Sphinx's `addnodes.glossary` is a thin wrapper around a `definition_list` (already fully supported) | TRIVIAL | Pure no-op `visit_glossary`/`depart_glossary` (pass-through) — this is a "free" table-stakes fix that costs almost nothing since `definition_list`/`term`/`definition` are already built (translator.py:1029-1161) |
| `tabular_col_spec` | LaTeX-only directive hint (`.. tabularcolumns::`) carrying column-format strings irrelevant to any other builder | TRIVIAL | `raise nodes.SkipNode` — identical one-liner to the existing `visit_colspec` (translator.py:1323-1331). Column widths are already driven by `tgroup`'s `cols` count, not this node. |
| `abbreviation` | `:abbr:`\`HTML (Hyper Text Markup Language)\` — common in technical prose; docutils' `explanation` attribute holds the expansion, HTML renders it as a hover tooltip which has no PDF equivalent | LOW | Render inline as `text` content followed by the explanation in parens, e.g. `HTML (Hyper Text Markup Language)`, since a printed PDF can't hover-reveal a tooltip |

### Differentiators (valuable, not required for a usable API doc)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| `todo_node` (`sphinx.ext.todo`) | Structurally an admonition (has `Admonition`+`Element` shape, paragraph children) — reusing existing machinery is nearly free once footnotes/topic patterns exist | LOW | Reuse `_visit_admonition("warning", custom_title="Todo")`. Note most *published* docs set `todo_include_todos = False`, so Sphinx itself strips these before the writer ever runs — low real-world volume in a release build, but Sphinx's own `doc/` source (the milestone's benchmark corpus) does contain live todos |
| `manpage` role (`:manpage:`\`ls(1)\`\`) | Cosmetic correctness for Unix/systems docs; low volume | TRIVIAL | Reuse the existing "dummy node, borrow another visitor's logic" pattern already used for `rubric`→`strong` (translator.py:2687-2705) — borrow `visit_emphasis` or `visit_literal` |
| CSS-length conversion helper generalized beyond `px` (e.g. `em`, unitless legacy HTML width like `width="300"`) | Robustness beyond the two Issue #114 units specifically found in the corpus | LOW | Natural byproduct of building the `_convert_css_length` helper for the P0 fix — worth generalizing once, not fixing `px` only and hitting the next unit as a new bug next milestone |

### Anti-Features / Out of Scope (graceful-degrade only, not full support)

| Feature | Why It Looks Attractive | Why Full Support Is Out of Scope This Milestone | What To Do Instead |
|---------|--------------------------|---------------------------------------------------|---------------------|
| `graphviz` node (`sphinx.ext.graphviz`) full rendering | Sphinx docs use it for architecture diagrams; "just render the diagram" sounds achievable | Each Sphinx *builder* must independently shell out to the `dot` CLI and rasterize/vectorize the DOT source into an image (`html_visit_graphviz`, `latex_visit_graphviz` — there is no generic cross-builder path); this is a whole new subsystem (subprocess management, image-format negotiation, error handling for missing `dot`), not a translator method | Add an explicit `visit_graphviz` that emits a clearly-visible placeholder (`#block(fill: silver)[Diagram omitted — Typst rendering not supported]`) and logs **one** controlled warning, instead of relying on the generic unknown-node fallback (which risks partial/garbled raw DOT source leaking into the PDF via untranslated `Text` children before the SkipNode point is reached) |
| `inheritance_diagram` (`sphinx.ext.inheritance_diagram`) full rendering | Same appeal as graphviz — "just render the class hierarchy image" | Same blocker as graphviz (it *generates* a graphviz graph internally) plus its own image-map/clickable-node HTML-only features that have no PDF analog at all | Same graceful-degrade placeholder pattern as graphviz — one shared helper, two `visit_*` registrations |
| Literal 1:1 port of docutils' footnote backref plumbing (`backrefs` list → manual anchor/jump-link generation) | It's "the same information the HTML writer uses," so it feels like the natural translation target | Typst's `footnote()` function is **not** an anchor-and-jump-link primitive like HTML's `<sup><a href="#fnN">`; it is a first-class content type with its own automatic numbering, page-bottom placement, and (per Typst's docs) its own reuse-by-label mechanism for a footnote cited more than once. Re-implementing HTML-style manual backref IDs on top of that would fight the tool instead of using it. | Map `footnote`/`footnote_reference` directly onto Typst's native `footnote[...]` mechanism (see spec below) and drop the backref/anchor bookkeeping entirely — it's not just unnecessary, it's the *wrong* target representation |
| Fixing every one of the ~1979 warning-class node gaps this milestone | The number is dramatic and "zero warnings" is an appealing bar | Many of the 1979 are long-tail/rare nodes not in the milestone's named target list; chasing all of them risks scope creep on a milestone whose actual gate is "Sphinx's own `doc/` compiles with no *fatal* errors," not "zero warnings" | Ship the named high-frequency set (this table), re-measure the real warning count against Sphinx's `doc/` build, and let the *next* milestone's research target whatever's left in the long tail |

## Deep Dives (per the quality gate)

### `versionmodified` — rendered form

**Node shape:** `sphinx.addnodes.versionmodified` (subclasses `docutils.nodes.Admonition` + `nodes.TextElement`). Attributes: `type` (one of `"versionadded"`, `"versionchanged"`, `"deprecated"`, `"versionremoved"`), `version` (the version string, e.g. `"0.6"`). Children: inline nodes for a same-line explanation (`.. versionadded:: 0.6\n\n   Some inline explanation.` puts that explanation's inline nodes directly as children of the `versionmodified` node itself — it behaves like a paragraph, not a container-of-paragraphs) *or*, if the directive has an indented body (multiple paragraphs), those paragraphs are nested-parsed as full block children.

**Do not render this as a gentle-clues admonition box.** Sphinx's own HTML/LaTeX writers deliberately render `versionmodified` as a **compact, unboxed, italicized inline label** ("*Added in version 0.6:* description text"), visually distinct from `note`/`warning`/`danger` boxes — treating it as a full callout box would be denser and more visually loud than every other Sphinx-generated PDF a reader has seen, and would look wrong next to `desc_content` bodies that mix several of these per API entry.

Recommended concrete Typst form (mirrors the existing `emph`/`strong` helper-reuse convention, e.g. `visit_rubric`):

```
emph(text("Added in version 0.6: ")) + <inline/paragraph children, rendered normally>
```

with the label text sourced from a small `type → label template` map (`"versionadded"` → `"Added in version {v}"`, `"versionchanged"` → `"Changed in version {v}"`, `"deprecated"` → `"Deprecated since version {v}"`, `"versionremoved"` → `"Removed in version {v}"` — matching Sphinx's own `sphinx.locale.versionlabels` dict so the wording matches what users already expect from the HTML/LaTeX builds of the *same* source). LOW complexity; no new translator state needed beyond the label map and reading `node["type"]`/`node["version"]`.

### `desc_returns` / `desc_signature_line` / `desc_inline` / `desc_optional` — autodoc signature sub-parts

These are all children that live **inside** the already-supported `desc_signature` (translator.py:2511-2527) and, for `desc_parameterlist`/`desc_optional`, inside the already-supported `desc_parameterlist` (translator.py:2577-2621). None require new architecture — each slots into the existing "emit `text(...)` literals, join with the sibling-check idiom from `depart_desc_parameter`" pattern:

- **`desc_returns`** — a `desc_signature` child holding the return-type annotation (Python's `-> int`, etc.). Emit `text(" → ") + <children>` on visit; no special depart logic needed (children render themselves via the existing inline-node visitors, exactly like `desc_addname`/`desc_name` already do today with zero-op visit/depart pairs).
- **`desc_optional`** — a `desc_parameterlist` child wrapping a run of optional trailing parameters (e.g. `printf(fmt[, args])`). Bracket-wrap: `text("[")` on visit, `text("]")` on depart, reusing `_desc_parameter_has_content`/comma-join logic already in `depart_desc_parameter`. Must recurse correctly — `desc_optional` can nest inside `desc_optional` for multi-level optional args (some C APIs do this) — no new state, just correct recursive containment (the existing visitor-pattern recursion already handles this "for free" as long as visit/depart don't assume single-level nesting).
- **`desc_signature_line`** — a child of `desc_signature` used only when `is_multiline=True` (multi-line C++ template signatures, long overload lists). Each line is its own sibling node; insert `linebreak()` between them using the identical `node.next_node(descend=False, siblings=True)` sibling-check already used by `depart_desc_parameter` (translator.py:2612-2621), just swapping the separator from `text(", ")` to `linebreak()`.
- **`desc_inline`** — same children shape as `desc_signature` but used **inline in running prose** (e.g. the `:cpp:expr:` role). Critically, it must **not** call the `strong()`-wrapper dummy-node trick that `visit_desc_signature` uses (translator.py:2517-2519) — that bold-block styling is correct for a standalone declaration header, wrong for a fragment embedded mid-sentence. Simplest correct behavior: pure pass-through (no wrapper at all); a nice-to-have refinement (not required) would route it through the same monospace styling as `literal` since `cpp:expr`-style fragments conventionally render in code font.

### Footnote / footnote_reference — the Typst-native design

**docutils node shapes:**
- `footnote` — attributes `ids` (its own anchor id), `names` (the footnote's label, auto-generated digit for `[#]_` or an explicit symbol/name), `backrefs` (list of ids of every `footnote_reference` that points at it), `auto` (truthy for auto-numbered). Children: a `label` node (the rendered number/symbol) followed by one or more `paragraph` children (the footnote body). By the time the translator sees this tree, docutils' footnote-numbering transform has already resolved auto-numbers to concrete digits — no numbering logic needs to happen in the translator.
- `footnote_reference` — attributes `refid` (the id of the target `footnote` node), `ids` (its own id, listed in that footnote's `backrefs`), `auto`. Single `Text` child (the already-resolved number).

**Recommended Typst mapping — do not do a literal 1:1 structural port.** Typst's `footnote[...]` is a call-site content primitive: wherever you write `#footnote[body]` is where the reference marker appears, and Typst auto-numbers, auto-places at the page bottom, and auto-generates the click target. This is architecturally different from docutils, where the footnote's *body* commonly lives physically elsewhere in the document (end of section, end of document) from its *reference* mark(s).

Concrete approach:
1. Pre-pass (at `visit_document` time, or lazily on first `footnote_reference` encountered): walk the doctree once and build `self._footnote_bodies: dict[str, str]` mapping each `footnote` node's id → its rendered Typst body content (render its paragraph children through the normal translator machinery into a string buffer, the same buffering technique already used for `term`/`definition` in `visit_term`/`visit_definition`, translator.py:1086-1161).
2. `visit_footnote` on the *footnote node itself* (in its natural, often-inconvenient document position) should **not** emit anything directly — `raise nodes.SkipNode` after the pre-pass has already captured its content, since Typst places the note wherever `footnote[...]` was *called*, not where the docutils footnote definition happened to sit.
3. `visit_footnote_reference` looks up `self._footnote_bodies[node["refid"]]` and emits `footnote[<body>]` inline at the reference's position.
4. For a footnote referenced **more than once** (`len(footnote["backrefs"]) > 1`), Typst supports re-citing a previously-placed footnote by label rather than duplicating the note — emit the full `footnote[...]` (with a label, e.g. `<fn-<id>>`) only at the *first* reference, and `footnote(<fn-<id>>)` at every subsequent one. **Flag for verification:** confirm this exact re-citation call form against a real `typst compile` before locking the requirement wording — the label-reuse mechanism is documented but the precise call syntax should be spot-checked, not assumed from this research.

This is the most architecturally involved item in the milestone (needs a genuine pre-pass, not just new `visit_*` methods slotted into the existing single-walk pattern) — flag it for its own phase/plan rather than bundling it with the trivial table-stakes items above.

### Empty-URL cross-reference (×596) — genuinely broken vs. resolution gap

**Current code** (translator.py:1970-1983):
```python
refuri = node.get("refuri", "")
if not refuri:
    logger.warning(...)
    self._skip_link_wrapper = True
    return
```

This checks **only** `refuri`. docutils' `reference` node has three possible resolution attributes, not one:
- `refuri` — external URL or cross-document link (what's checked today)
- `refid` — same-document internal anchor (points at another node's `ids` entry) — **not checked at all today**
- `refname` — an unresolved by-name reference; in a clean build this should not survive to the writer (Sphinx's cross-reference machinery either resolves `pending_xref` nodes into `refuri`/`refid`-bearing `reference` nodes, or — on genuine failure — typically degrades the *pending_xref* itself into plain text/`problematic` well before the writer's `visit_reference` ever runs)

**The strong, code-grounded hypothesis:** most of the 596 "empty URL" hits are same-document anchors resolved via `refid` (section links within the current file, glossary/`:term:` links, footnote-like cross-refs, etc.) that ARE fully resolved — the translator just never learned to look at the field they're resolved into. The existing code already proves this pattern is understood: it has a special case for `refuri.startswith("#")` → `link(<label>, ...)` (translator.py:1988-1992) for internal links, but that only fires if Sphinx happened to put the anchor in `refuri` as `"#id"` rather than in `refid` directly — which is the less common of the two internal-link encodings.

**Recommended fix:** before falling back to plain text, also check `node.get("refid")`, and if present, route through the *same* internal-link branch (`link(<label>, ...)`) already used for `#`-prefixed `refuri`. Only degrade to plain text when **both** `refuri` and `refid` are absent/empty — that residual case is genuinely rare in well-formed reST (docutils typically converts a truly-unresolvable reference into a `problematic` node + `system_message` well upstream, not a clean `reference` node with nothing to point at), so after this fix the plain-text fallback path should fire far less often, and its warning becomes a meaningful "look at this" signal instead of routine noise.

**Caveat for the roadmap:** the exact post-fix count reduction should be measured empirically against the real Sphinx `doc/` corpus (re-run the same build, diff the warning count) rather than assumed from this analysis — the 596 figure is almost certainly dominated by the `refid` gap, but confirming the residual genuinely-broken count requires an actual build.

## Feature Dependencies

```
Fatal bug fix (px units + target-linked figure)
    └──blocks──> everything else (nothing else can be validated against a real
                 typst-compile of Sphinx's doc/ tree until this compiles clean)

desc_returns / desc_optional / desc_signature_line / desc_inline
    └──requires──> existing desc_signature / desc_parameterlist / desc_parameter
                    handlers (already built) — these are pure extensions, no new
                    subsystem

Empty-refid reference fix
    └──requires──> existing visit_reference's #-prefixed-refuri internal-link
                    branch (already built) — extend the condition, don't rewrite it

footnote / footnote_reference
    └──requires──> a genuine doctree pre-pass (net-new capability — no existing
                    translator code does a two-pass walk today)
    └──enhances──> nothing else in this milestone; fully independent

topic
    └──requires──> _visit_admonition / _depart_admonition (already built) — direct
                    reuse, cheapest table-stakes item here

glossary
    └──requires──> definition_list / term / definition (already built) — pure
                    pass-through wrapper, near-zero net-new code

graphviz / inheritance_diagram placeholders
    └──conflicts with──> "full diagram rendering" (explicitly out of scope this
                          milestone; do not let placeholder work expand into a
                          real DOT-rendering subsystem)
```

## MVP Definition

### Launch With (v0.6.0)

- [ ] `px`/CSS-length conversion for `image(width:/height:)` — FATAL, blocks the whole milestone's validation gate
- [ ] `:target:`-linked figure → `link("url")[#image(...)]` content-block form — FATAL, same gate
- [ ] `versionmodified` (all four types) rendered as unboxed emph-label + body
- [ ] `refid` handling added to `visit_reference` (the empty-URL fix)
- [ ] `desc_returns`, `desc_optional`, `desc_signature_line`, `desc_inline`
- [ ] `footnote` / `footnote_reference` via the Typst-native pre-pass + `footnote[...]` design
- [ ] `transition`, `topic`, `line`/`line_block`, `glossary`, `tabular_col_spec`, `abbreviation`
- [ ] `visit_graphviz`/`visit_inheritance_diagram` graceful-degrade placeholders (warn, don't abort)

### Add After Validation (v0.6.x)

- [ ] `todo_node` proper admonition styling — trigger: someone actually ships docs with `todo_include_todos = True`
- [ ] `manpage` role styling — trigger: a systems-docs user reports it missing
- [ ] Generalize the CSS-length converter beyond `px` (unitless legacy widths, `em`) — trigger: the next fatal-bug report that isn't `px`

### Future Consideration (v2+)

- [ ] Real `graphviz`/`inheritance_diagram` rendering (shell out to `dot`, rasterize/vectorize into an image, wrap in `figure()`) — defer until a user explicitly asks for diagrams in the PDF output; this is a full subsystem, not a translator fix
- [ ] Long-tail of the remaining ~1979-warning corpus not named in this milestone — re-measure after this milestone ships, target the next-highest-frequency residual in a future milestone

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|----------------------|----------|
| `px` unit fatal fix | HIGH | LOW–MEDIUM | P1 |
| `:target:` figure fatal fix | HIGH | MEDIUM | P1 |
| Empty-URL/`refid` fix | HIGH (596×) | LOW–MEDIUM | P1 |
| `versionmodified` | HIGH (972×) | LOW | P1 |
| `desc_returns` | MEDIUM (187×) | LOW | P1 |
| `desc_signature_line` | MEDIUM (59×) | LOW–MEDIUM | P1 |
| `topic` | MEDIUM | LOW (reuse) | P1 |
| `glossary` | MEDIUM | TRIVIAL (reuse) | P1 |
| `tabular_col_spec` | LOW | TRIVIAL | P1 |
| `transition` | MEDIUM | LOW | P1 |
| `line`/`line_block` | MEDIUM | LOW–MEDIUM | P1 |
| `footnote`/`footnote_reference` | MEDIUM–HIGH | MEDIUM–HIGH | P1 (but its own plan/phase) |
| `desc_optional` | LOW (6×) | LOW–MEDIUM | P2 |
| `desc_inline` | LOW (13×) | LOW | P2 |
| `abbreviation` | LOW | LOW | P2 |
| Graphviz/inheritance placeholders | MEDIUM (prevents noisy/garbled degrade) | LOW | P2 |
| `todo_node` styling | LOW | LOW | P3 |
| `manpage` styling | LOW | TRIVIAL | P3 |
| Full graphviz/inheritance rendering | MEDIUM | HIGH | P3 / v2+ |

**Priority key:** P1 = must have for this milestone's gate (real Sphinx `doc/` compiles clean through `typstpdf`); P2 = should have, low-risk adds once P1 lands; P3 = defer to a later milestone.

## Sources

- `typsphinx/translator.py` (read directly, lines ~1100-2800): existing `visit_figure`/`visit_image`/`visit_reference`/`_visit_admonition`/`desc_*` conventions — this project's own established idioms are the primary source for "what should the new code look like."
- `.planning/PROJECT.md` — v0.6.0 milestone scope, Issue #114 framing, target node list with frequency counts.
- [Doctree node classes added by Sphinx](https://www.sphinx-doc.org/en/master/extdev/nodes.html) — `versionmodified`, `desc_returns`, `desc_signature_line`, `desc_inline`, `desc_optional` definitions (MEDIUM confidence, official docs).
- [sphinx.addnodes source](https://www.sphinx-doc.org/en/master/_modules/sphinx/addnodes.html) — node class hierarchy confirmation.
- [`versionmodified` node-name issue #5660](https://github.com/sphinx-doc/sphinx/issues/5660) and [issue #8016](https://github.com/sphinx-doc/sphinx/issues/8016) — confirms `type`/`version` attribute usage across versionadded/versionchanged/deprecated/versionremoved.
- [Typst `footnote` reference docs](https://typst.app/docs/reference/model/footnote/) — native numbering/placement model, label-reuse mechanism (flagged above as needing a real-compile spot-check on exact re-citation syntax).
- docutils node reference (`reference`/`footnote`/`footnote_reference`/`transition`/`topic`/`line_block`/`substitution_definition` attribute shapes) — MEDIUM confidence, drawn from established docutils spec knowledge rather than a single fetched page; recommend a quick cross-check against `docutils.nodes` docstrings during implementation if any attribute name is in doubt.

---
*Feature research for: Sphinx→Typst translator, v0.6.0 real-world robustness milestone*
*Researched: 2026-07-11*

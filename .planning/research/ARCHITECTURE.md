# Architecture Research: v0.6.0 Real-World Robustness (Issue #114 fix + high-frequency node support)

**Domain:** docutils-node-to-Typst-markup visitor pattern (single file: `typsphinx/translator.py`, ~2794 lines, ~140 `visit_*`/`depart_*` methods)
**Researched:** 2026-07-11
**Confidence:** HIGH — every claim below is traced against the actual current source (line numbers cited), not the previous milestone's forward-port research (which covered dependency/API compatibility, not node semantics). This document supersedes the 2026-07-09 ARCHITECTURE.md for the v0.6.0 milestone; that file's Sphinx-9/typst-0.15 compatibility findings remain valid background but are no longer this milestone's focus.

> **One MEDIUM-confidence item flagged explicitly:** the exact docutils child-node shape of `addnodes.versionmodified` and the precise semantics of `document.footnotes`-style pre-collection were reasoned from docutils/Sphinx API conventions, not verified against a live doctree dump in this research pass. Both recommendations degrade gracefully if the exact shape differs slightly (see each section's "verify" note) — build a throwaway `python -c "sphinx-build ... ; print(doctree.pformat())"` dump before finalizing those two handlers.

## Standard Architecture (unchanged pipeline — confirmed, no new components needed)

```
doctree ──▶ TypstTranslator (visitor, translator.py) ──▶ body string ──▶ TemplateEngine ──▶ .typ ──▶ [PDF compile]
                    │
                    ├─ self.body: list[str]  (accumulator; add_text() appends)
                    ├─ ~20 boolean/stack state vars tracking nesting context
                    └─ buffer-swap idiom: self.saved_body = self.body; self.body = []; ...; restore
```

Every fix and every new node handler in this milestone is a **change inside `translator.py` only** (plus, in one case, a generalization of an `isinstance()` check that already exists there). No changes are needed to `writer.py`'s import blocks (Typst's `footnote()`, code-mode blocks `{...}`, and the `link()`/`figure()` functions used below are all stdlib — no new `@preview` package required) and no changes to `builder.py` or `pdf.py`. This is a **narrow, single-file, high-density milestone** — the risk is entirely in getting individual `visit_*`/`depart_*` interactions right, not in restructuring the pipeline.

## Part 1 — Issue #114 bug 2: figure + `:target:` + caption (traced against actual code)

### Current node nesting

For `.. figure:: img.png\n   :target: https://example.com\n\n   Caption text.`, docutils produces:

```
figure
├── reference (refuri="https://example.com")
│   └── image (uri="img.png")
└── caption
    └── Text("Caption text.")
```

### Current code-generation path (traced line-by-line)

1. `visit_figure` (`translator.py:1163`) — sets `self.in_figure = True`, resets `self.figure_content`/`self.figure_caption`, emits `"figure(\n"` (line 1177).
2. `visit_reference` (`translator.py:1930`) is called on the `reference` child. It checks `next_is_target` (lines 1946–1954) by inspecting the reference's **next sibling** — but the reference's next sibling here is `caption`, not a `target` node, so `next_is_target = False`. `refuri` is non-empty (the `:target:` URL), so the empty-URL branch (lines 1972–1983) is not taken. Since `self._in_markup_mode` is `False` (top-level code mode), `prefix = ""`, and it emits `link("https://example.com", ` (line 1995) — **valid so far**. It sets `self._in_link = True` (line 2003).
3. `visit_image` (`translator.py:1501`) is called on the nested `image` child. Because `self.in_figure` is `True`, it takes the indented branch (line 1521): emits `'  image("img.png"'`, then optional `width`/`height` (see Part 2), then `")"` (line 1535).
4. `depart_image` (`translator.py:1537`) — since `self.in_figure` is `True`, skips trailing newlines (line 1545).
5. `depart_reference` (`translator.py:2009`) — emits the closing `")"` (line 2027), clears `_in_link` (line 2030). **At this point the accumulated body is `figure(\nlink("https://example.com",   image("img.png"))` — this half is syntactically valid Typst on its own.**
6. `visit_caption` (`translator.py:1201`) — since `self.in_captioned_code_block` is `False` (this is a figure, not a literal-block-wrapper), it does **not** raise `SkipNode`; it just sets `self.in_caption = True` (line 1215). **It does not buffer-swap `self.body`.**
7. The caption's `Text` child then goes through the *generic* `visit_Text` (`translator.py:443`). Because `self.in_paragraph`, `self.in_list_item`, `self.in_desc_parameter`, and `self._in_link` are all `False` at this point (caption is none of those contexts), none of the separator branches fire, and it falls straight through to `self.add_text(f'{prefix}text("{text_content}")')` (line 495) — **appended directly to the live `self.body` stream**, immediately after the figure's `link(...)` call, with **no comma, no operator, no wrapping**.
8. `depart_caption` (`translator.py:1217`) — since `self.in_figure` is `True`, sets `self.figure_caption = node.astext()` (line 1226) — capturing the caption a **second time**, as plain escaped-free text (discarding any inline markup), for later re-emission in step 9.
9. `depart_figure` (`translator.py:1179`) — since `self.figure_caption` is truthy, emits `,\n  caption: [{self.figure_caption}]` (line 1188), then the closing `)` (plus optional `<label>`) (lines 1191–1195).

**Resulting (broken) output:**
```
figure(
link("https://example.com",   image("img.png"))text("Caption text."),
  caption: [Caption text.]
) <label>
```

This is exactly the "invalid juxtaposition" described in the milestone brief: `image("img.png"))text("Caption text.")` is two adjacent expressions with no separator inside a function-call argument position — a Typst parse error — **and** the caption is duplicated (once broken, once correct) because `visit_caption`/`depart_caption` has no buffer-swap, unlike every other place in this file that defers rendered content (admonition titles, definition-list terms/definitions).

### Root cause (single, precise)

**`visit_caption` is the only "deferred content" producer in the file that does not follow the buffer-swap idiom.** Compare:
- `visit_term`/`depart_term` (`translator.py:1086–1121`): swaps `self.body` to `self.current_term_buffer`, restores after.
- `visit_title`'s admonition branch (`translator.py:208–211`) / `depart_title`'s counterpart (`translator.py:229–234`): swaps `self.body` to `[]`, restores, captures joined content into `self._pending_admonition_title`.
- `visit_caption`/`depart_caption` (`translator.py:1201–1227`): **no swap** — children write straight into the live stream, and `depart_caption` separately re-derives content via `node.astext()` (which also silently discards inline markup like `emphasis`/`strong` inside a caption — a pre-existing minor correctness gap, now compounded into a fatal one).

### Recommended fix — buffer-swap the caption, not a markup-mode rewrite

Apply the **exact same buffer-swap idiom** already proven for admonition titles:

1. `visit_caption`: if `self.in_figure` (and not `self.in_captioned_code_block`), save `self.body`, set `self.body = []`, mark `self._in_figure_caption = True` (or reuse `self.in_caption`, already set). Let children render normally through the existing visitors (preserving `emphasis`/`strong`/`reference` markup — a strict improvement over `node.astext()`).
2. `depart_caption`: join the buffer, restore `self.body`, store the **rendered code-mode string** (not plain text) into `self.figure_caption`.
3. `depart_figure`: emit `f",\n  caption: {{{self.figure_caption}}}"` — note **`{...}` (code block), not `[...]` (markup block)** — because the buffered content is code-mode function calls (`text(...)`, `emph({...})`, etc.); wrapping it in `[...]` would treat those calls as literal text (the same markup/code-mode hazard that caused the v0.5.0 admonition bug). A code block whose statements are content-producing expressions is exactly the pattern already used for list items (`translator.py:900–902`) and admonition bodies (`translator.py:2321`) — multiple bare content expressions on separate lines join automatically.

**Fixed output:**
```
figure(
link("https://example.com",   image("img.png")),
  caption: {text("Caption text.")}
) <label>
```

### Why NOT switch to the milestone brief's literal `link(url)[#image(...)]` markup-sugar form

The milestone context suggests `#figure(link(url)[#image(...)], caption: [...])` as the target shape. That is valid Typst, but it is **not the minimal fix** and reintroduces exactly the class of risk this codebase has been burned by once already (the v0.5.0 admonition markup/code-mode bug):
- It requires `visit_reference`/`visit_image` to toggle `self._in_markup_mode` specifically when inside a figure's `:target:` link — a **new, figure-specific branch** in two already-complex, heavily-shared visitor methods used by every reference and every image in the document, not just figures.
- The current two-positional-argument form `link("url", image(...))` (already emitted, and already correct as traced above) is fully equivalent Typst and requires **zero changes** to `visit_reference`/`visit_image`.

**Recommendation: fix only `visit_caption`/`depart_caption`/`depart_figure` (3 methods, ~10 lines). Do not touch `visit_reference` or `visit_image` for this bug.** This keeps the fix isolated, testable independently of the reference/image machinery, and consistent with the file's existing idiom.

## Part 2 — px→pt length-unit conversion (shared helper)

### Where the bug lives

`visit_image` (`translator.py:1527–1533`):
```python
if "width" in node:
    width = node["width"]
    self.add_text(f", width: {width}")
if "height" in node:
    height = node["height"]
    self.add_text(f", height: {height}")
```
`node["width"]`/`node["height"]` come from docutils' `:width:`/`:height:` option parsing, which accepts CSS-style length strings (`"300px"`, bare numbers assumed `px`, or already-valid CSS units like `"50%"`, `"2in"`). Typst's length grammar does **not** recognize `px` as a unit (valid Typst units: `pt`, `mm`, `cm`, `in`, `em`, `%`). Emitting `width: 300px` verbatim is emitted as **fatal Typst syntax error** (unknown unit), independent of the figure/caption bug in Part 1 — this is Issue #114 bug 1.

### Where the shared helper belongs

`grep` confirms `"width"`/`"height"` appear **only** in `visit_image` today — no other node currently emits a length. But length attributes are a *category* of problem (any future node with `:width:`/`:scale:`/similar — e.g. a `figure`-level `:figwidth:`, or a table `:widths:`) will hit the same unit mismatch. Follow the file's existing precedent for shared, reusable, non-visitor logic: `_compute_relative_image_path` (`translator.py:1748`) and `_compute_relative_include_path` (`translator.py:1637`) are both private instance methods placed near the visitor methods that use them, with docstrings and doctest-style examples.

**Recommendation:** add a `_convert_length_to_typst(self, value: str) -> str` (or a module-level pure function, since it needs no `self` state — a `@staticmethod` is more honest here than an instance method, but keep it adjacent to `_compute_relative_image_path` for discoverability) directly above `visit_image`. Responsibilities:
- Strip/convert `px` → `pt` (docutils/CSS `px` and Typst `pt` are not numerically identical units in a strict print sense, but `px`→`pt` 1:1 passthrough, i.e. treating the numeric value as already being in `pt`, or a documented approximate CSS-`px`-to-`pt` ratio, is the pragmatic choice already implied by the milestone brief: "convert `px`/CSS length units to Typst-valid `pt` (or drop)" — a fixed ratio (96 CSS px per inch, 72 pt per inch → `pt = px * 0.75`) is the more correct conversion if precision matters; a straight passthrough is acceptable if the milestone's bar is "don't fatal-error," which is the stated bar here).
- Pass through already-valid Typst units unchanged (`%`, `pt`, `mm`, `cm`, `in`, `em`).
- Handle a bare numeric string (no unit) — docutils' default assumption is `px`, so treat identically to explicit `px`.
- On anything unparseable, **degrade, don't fatal**: log a warning via the existing module-level `logger` (`translator.py:16`) and drop the attribute entirely (Typst will use the image's natural size) rather than emit a syntactically-broken length.

Call it from both the `width` and `height` branches in `visit_image`, replacing the current verbatim `f"{width}"`/`f"{height}"` interpolation. No other visitor method needs to change for this milestone's scope, but this is the correct integration point for any *future* length-bearing attribute.

## Part 3 — Integration points for new/fixed stateful node handlers

This translator already has exactly **four** reusable state patterns. Every new handler in this milestone should map onto one of them — introducing a fifth pattern should be treated as a design smell requiring justification.

| Pattern | Where it lives today | Mechanism | New handlers that should reuse it |
|---|---|---|---|
| **Buffer-swap (defer rendered content)** | `visit_term`/`depart_term` (1086–1121), `visit_definition`/`depart_definition` (1123–1161), admonition title branch in `visit_title`/`depart_title` (190–238) | Save `self.body`, point it at a scratch list, let children render normally through existing visitors, join + restore at depart | **Figure caption fix** (Part 1); **footnote body pre-pass** (below) |
| **Dummy-node delegation** | `visit_desc_signature`/`depart_desc_signature` (2511–2527, delegates to `visit_strong`/`depart_strong`), `visit_rubric` (2687), `visit_title_reference` (2707), `visit_literal_strong`/`visit_literal_emphasis` (2771–2793) | Construct a throwaway `nodes.strong()`/`nodes.emphasis()` and call the existing visitor on it, reusing all its paragraph/list-item state juggling for free | **`topic` title** (render as a `strong({...})` line, not a `heading()`); **`desc_returns`** (reuse `desc_annotation`-style passthrough, or emphasis-delegate for the arrow) |
| **Code-mode `+`-concatenation flag pair** | `in_desc_parameter`/`_desc_parameter_has_content` (73–79, used in `visit_Text` 477–483, and `visit_desc_parameterlist`/`depart_desc_parameterlist` 2577–2602), mirrored by `_in_link`/`_link_has_content` (76, 80–82) | A boolean "am I inside this construct" + a boolean "has a prior sibling already been emitted" pair, checked in the shared `visit_Text` to decide whether to prepend `" + "` | **`desc_optional`** (bracket-wrapped optional params inside `desc_parameterlist`, same `+`-joining, plus literal `text("[")`/`text("]")` around the buffered group) |
| **List-item-style newline-joining `{}` block** | `visit_list_item`/`depart_list_item` (883–919), and reused by `visit_emphasis`/`visit_strong` which temporarily set `self.in_list_item = True` around their own children (541–543, 611–613) so `visit_Text` uses newline separators instead of `+` | Open with `"{\n"`, temporarily flip `in_list_item = True` + reset `list_item_needs_separator`, let children stream in with newline separators, close with `"}"`, restore flags | **`topic`** body, **`line_block`**/**`line`** (each `line` behaves like a list item's content block), **`versionmodified`** body (reuses the *admonition* variant of this pattern directly, see below) |

### `versionmodified` (`.. versionadded::` / `.. versionchanged::` / `.. deprecated::`) → reuse the admonition pattern verbatim

`addnodes.versionmodified` carries a `type` attribute (`"versionadded"`/`"versionchanged"`/`"deprecated"`) and a `version` attribute, with inline message content as direct children (no separate title child — unlike `nodes.Admonition` subclasses, there's nothing for `visit_title`'s buffer-swap branch to intercept). This is architecturally simpler than a real admonition: the "title" is fully known from node attributes at `visit` time, not derived from child markup.

**Integration:** call the existing `_visit_admonition`/`_depart_admonition` helper pair (`translator.py:2292–2345`) directly — no new state needed:
```python
def visit_versionmodified(self, node):
    kind = node.get("type", "versionadded")
    version = node.get("version", "")
    clue_type = {"versionadded": "tip", "versionchanged": "info", "deprecated": "warning"}.get(kind, "info")
    title = {"versionadded": "Added in version", "versionchanged": "Changed in version",
             "deprecated": "Deprecated since version"}.get(kind, kind) + f" {version}"
    self._visit_admonition(node, clue_type, custom_title=title)

def depart_versionmodified(self, node):
    self._depart_admonition()
```
`_visit_admonition`/`_depart_admonition` already handle the `custom_title` (static Python string) path (`translator.py:2339–2340`, `2317`) exactly this way for `visit_important`/`visit_seealso` (2375–2397) — this is a one-for-one template match, zero new state variables. **This is the single highest-value, lowest-risk handler in the milestone** (×972 occurrences per PROJECT.md, and it's a near-copy-paste of an already-proven pattern).

**Verify note (MEDIUM confidence):** confirm via a real doctree dump that `versionmodified`'s children are inline content directly (not wrapped in a nested `paragraph`) — if Sphinx does wrap them in an inner `paragraph`, the existing `visit_paragraph`'s `in_list_item` skip-`par()`-wrapping branch (`translator.py:351–353`) needs `self.in_list_item` (or an equivalent flag) set around the admonition body the same way it already is for admonition content generally — check whether `_visit_admonition` callers currently rely on this; if `note`/`warning` admonitions already correctly render nested paragraphs (they do, per the Phase 8.1 fix), `versionmodified` gets this for free through the same code path.

### Empty-URL cross-references (×596) → extend `visit_reference`, not a new node

This is **not a new node handler** — it's a gap in the existing `visit_reference` empty-URL branch (`translator.py:1972–1983`). Docutils `reference` nodes carry `refuri` (external/resolved) **or** `refid` (internal same-document anchor, set when a reference resolves to an in-document target rather than an external/cross-doc URI). The current code only ever reads `node.get("refuri", "")`; when a reference is an internal anchor, `refuri` may legitimately be empty while `refid` holds the resolvable target id — today that falls straight into the "empty URL, render as plain text" branch (lines 1976–1983) and logs a warning, discarding a perfectly resolvable link. This mirrors the *already-present* internal-link convention one branch below it: `if refuri.startswith("#")` (line 1989) treats a `#`-prefixed `refuri` as an internal label reference and emits `link(<label>, ...)` — the fix is to add a **parallel branch checked before the empty-URL bail-out**: if `refuri` is empty but `node.get("refid")` is present, treat it exactly like the `#`-prefixed case (`link(<refid>, ...)`) instead of falling through to plain text.

**Integration point:** insert the `refid` check between the `refuri` extraction (line 1970) and the empty-URL branch (line 1976), inside `visit_reference` — no new state variables, no new visitor method. **Verify note:** confirm `refid` values are already valid Typst label identifiers (same sanitization as done for `pending_xref` at `translator.py:1622`, `label = reftarget.replace(".", "-").replace("_", "-")`) — reuse that same sanitization helper (or extract it into a tiny shared method) rather than duplicating the two `.replace()` calls inline a third time (it currently appears once in `visit_pending_xref`; a `refid` branch would be the second use — factor it out at that point).

### `desc_returns` / `desc_signature_line` / `desc_inline` / `desc_optional` → extend the existing `desc_*` family, not a parallel system

All four slot into the **already-established** `desc_signature`/`desc_content`/`desc_parameterlist`/`desc_parameter`/`desc_sig_*` family (`translator.py:2495–2767`), which already has three sub-patterns to choose from:
- **Pure passthrough** (`desc_annotation`, `desc_addname`, `desc_name`, `desc_sig_keyword`, `desc_sig_name`, `desc_sig_punctuation`, `desc_sig_operator` — all just `pass`/`pass`, letting their `Text` children stream through whatever the surrounding context is): use this shape for `desc_inline` (it's the inline-flavored twin of `desc_signature`, appearing inline in running prose rather than as a block-level signature — it should **not** delegate to `visit_strong` like `desc_signature` does, since that would force bold+newline block spacing into inline text; treat it like `visit_inline` (`translator.py:2459–2478`), a transparent no-op container).
- **Dummy-node delegation with a literal prefix** (`desc_signature` bolds via `nodes.strong()` delegation, `translator.py:2511–2527`): `desc_returns` (the `-> ReturnType` return-type annotation) should emit a literal `text(" -> ")`-equivalent prefix (mirroring how `desc_parameterlist` emits a literal `text("(")` at `translator.py:2588`) before letting its children stream through as plain passthrough — no delegation needed, just one `add_text` in `visit_desc_returns` and nothing in `depart_desc_returns`.
- **`+`-concatenation flag pair** (`in_desc_parameter`/`_desc_parameter_has_content`, `translator.py:2577–2621`): `desc_optional` (docutils/Sphinx's bracketed-optional-parameter wrapper, e.g. `foo(a[, b])`) is a **sub-region inside** `desc_parameterlist` — it should wrap its children in literal `text("[")`/`text("]")` (matching the parenthesis convention already used for the parameter list itself) while **remaining inside** the parent's existing `in_desc_parameter` flag scope (don't toggle it off/on — the optional-bracket region still needs comma-joining consistent with its siblings).
- **New, narrow bookkeeping needed for `desc_signature_line` only**: this node wraps *one line of a multi-line overloaded signature* inside a single `desc_signature`. It needs exactly one new boolean, following the `is_first_list_item` precedent (`translator.py:63, 802, 898`): e.g. `self._is_first_desc_signature_line`, reset in `visit_desc_signature` and consulted in `visit_desc_signature_line` to decide whether to prepend a newline before rendering the line's own bold delegation. This is the **only genuinely new state variable** required across all four `desc_*` additions — everything else is either zero-state passthrough or reuse of `in_desc_parameter`.

### `topic` / `line_block` → generalize `visit_title`'s parent-type dispatch, then reuse the list-item `{}` pattern

**`visit_title`'s current dispatch is narrower than it needs to be.** It special-cases exactly one condition: `isinstance(node.parent, nodes.Admonition)` (`translator.py:208`), deferring the title to a `title:` keyword argument. `topic` is **not** an `nodes.Admonition` subclass, so a `topic`'s title child falls through to the default branch and gets rendered as `heading(level: self.section_level, ...)` (line 215) — **incorrect**, because a topic's title is a block label, not a numbered section heading, and emitting it as `heading()` both pollutes the document's heading/TOC structure and uses the wrong `section_level` (topics can nest inside sections without being sections themselves).

**Recommended generalization:** extend `visit_title`'s dispatch to a third branch — `isinstance(node.parent, nodes.topic)` — that renders the title **immediately, inline, as a bold line** (not deferred to a kwarg, since there is no Typst-side `topic()` function with a `title:` parameter the way gentle-clues admonitions have): delegate to `visit_strong`/`depart_strong` (the same dummy-node-delegation pattern used by `desc_signature`/`rubric`), followed by a newline, then let the topic's remaining body children stream in below it. This is a **three-way branch inside one method** (admonition → defer-to-kwarg, topic → render-inline-as-strong, default → heading), not three separate methods — keep it that way to preserve the single dispatch point.

`visit_topic`/`depart_topic` itself then just needs the list-item-style `{}` wrapper (open `"{\n"`, set `self.in_list_item = True` for the duration so nested `Text`/`paragraph` children join with newlines instead of the default paragraph `par({...})` block-spacing, close `"}\n\n"`, restore prior `in_list_item`) — structurally identical to how `visit_emphasis`/`visit_strong` already borrow `in_list_item` as a generic "join children with newlines, not `+`" signal (`translator.py:541–543, 611–613`).

`line_block`/`line`: same `{}` + `in_list_item`-borrowing pattern, with one addition — `visit_line` (not `visit_line_block`) must insert a literal `linebreak()` **before** every line except the first (mirroring the `is_first_list_item`/`list_item_needs_separator` precedent: add `self._is_first_line` state, reset in `visit_line_block`, consulted in `visit_line`). Nested `line_block` (poetry indentation) is architecturally just a nested instance of the same pattern (directly comparable to how `bullet_list`/`enumerated_list` already save/restore `is_first_list_item`/`list_item_needs_separator` for nesting, `translator.py:797–800, 821–826`) — but nested indentation rendering (`pad(left: ...)`) is a cosmetic detail not required by this milestone's stated scope; implement flat (no indentation) first and treat indentation as a follow-up if it surfaces in the real Sphinx-docs corpus.

### `footnote` / `footnote_reference` → the one handler that needs a genuinely new pattern (document-order pre-pass)

**This is architecturally different from everything else in this milestone**, and should be treated as such in planning. Docutils places a `footnote` node's numbered *definition* (label + body paragraphs) at the point in the tree where `.. [1] Body text.` was written or where Sphinx auto-collects footnotes — commonly **after** the `footnote_reference` inline node that cites it, since the citation appears in running prose earlier than the definition block. Typst's native `#footnote[body]` model is the opposite: the body is supplied **inline at the point of citation**, and Typst itself handles numbering/back-reference and can render the definition at the bottom of the page automatically — there is no separate "define later, reference now" split to preserve.

Because the *reference* is visited before the *definition* in normal document-order traversal, the existing buffer-swap idiom (which always defers content from a point **earlier** in the tree to a point **later** in the same subtree, e.g. term→definition, title→admonition-close) does not directly apply — it assumes forward order, not backward.

**Recommended pattern — one-time pre-pass, not placeholder substitution:**
1. In `visit_document` (`translator.py:144–154`, the very first visitor method called by `self.document.walkabout(self.visitor)` in `writer.py:72`), before emitting `"#{\n"`, run a **query-only pre-scan** (`self.document.findall(nodes.footnote)` — a pure tree query, not a visit; it does not consume or interfere with the subsequent real walkabout). For each footnote found, render its body by buffer-swapping `self.body` to a scratch list and manually calling `child.walkabout(self)` on each non-`label` child (the `label` child holds the auto-generated footnote number marker text and should be skipped — Typst's `#footnote[]` generates its own number). Store the joined result keyed by the footnote's id(s) into a new `self.footnote_bodies: dict[str, str] = {}` (initialized in `__init__`, next to the other collection-state dicts like `self.definition_list_items`).
2. `visit_footnote`/`depart_footnote` (encountered again later during the *real* walkabout, since `findall()` didn't remove anything from the tree): since the body was already rendered and will be emitted at the reference site, `visit_footnote` should `raise nodes.SkipNode` immediately (following the same "already handled, skip re-processing" precedent as `visit_target`, `translator.py:1592-1593`, and `visit_literal`, `translator.py:688`) — the footnote definition location itself produces no output.
3. `visit_footnote_reference` (new): look up `self.footnote_bodies` by the reference's `refid`, and emit `f"footnote({{{body}}})"` inline (code-mode call wrapping the pre-rendered code-mode content in a `{...}` block — same "code block evaluates to its last/joined content expression" convention as the figure-caption fix in Part 1). `raise nodes.SkipNode` afterward (a `footnote_reference` node's own children are typically just the visible bracketed number text, e.g. `[1]`, which Typst's `#footnote[]` already generates automatically and must not be duplicated).

**Why this is the highest-risk handler in the milestone:** it is the only place requiring (a) a full-tree pre-scan decoupled from the streaming visitor, (b) manually driving `child.walkabout(self)` on a subset of a node's children outside the normal traversal (bypassing the SkipNode set at step 2, since that pre-pass happens *before* the real walkabout reaches the footnote node), and (c) a lookup-dict keyed by id rather than any of the four existing state patterns. Budget real test-fixture time for it (nested footnotes, multiple footnotes in one paragraph, footnote inside a list item) and do not assume the admonition/definition-list precedent transfers cleanly.

**Verify note (MEDIUM confidence):** confirm docutils' actual attribute name for cross-linking a `footnote_reference` to its `footnote` (commonly `refid`, matching the same attribute already read in the empty-URL-reference fix above) via a real doctree dump before implementing — and confirm `nodes.label` is in fact the correct child-type-to-skip inside a footnote body (this is standard docutils footnote structure but should be confirmed against the actual Sphinx-generated tree, not assumed from generic docutils documentation).

## Part 4 — Graceful degradation: the fallback already exists, gap is 2 targeted overrides

`TypstTranslator.unknown_visit`/`unknown_departure` (`translator.py:2038–2059`) **already implement** a generic "unknown node → warn, don't abort" seam:
```python
def unknown_visit(self, node):
    logger.warning(f"unknown node type: {node}")

def unknown_departure(self, node):
    pass
```
This is not a new seam to design — it is docutils' own `nodes.NodeVisitor.dispatch_visit()`/`dispatch_departure()` mechanism (base class behavior, inherited via `SphinxTranslator` → `nodes.NodeVisitor`): for any node type without an explicit `visit_<ClassName>` method, dispatch falls back to `self.unknown_visit`. **Critically, `unknown_visit` here does not raise `SkipNode` or `SkipChildren`**, so docutils' default traversal continues to descend into the unknown node's children after logging — meaning any human-readable text nested inside an otherwise-unhandled node still renders (a reasonable, already-correct default for most "just haven't implemented this yet" cases).

**The actual gap for this milestone's `graphviz`/`inheritance_diagram` requirement:** these Sphinx-extension nodes typically store their real content (DOT source, class-hierarchy spec) as **node attributes**, not as child `Text` nodes meant for human reading — so if they happen to have any incidental text children (e.g., a caption or `:alt:`-derived child), `unknown_visit`'s default "descend into children" behavior could dump irrelevant fragments into the output rather than nothing. The correct fix is **not** to generalize `unknown_visit` further (it is already a sufficient last-resort net for the general case) but to add two small, explicit, targeted overrides:
```python
def visit_graphviz(self, node):
    logger.warning("graphviz diagrams are not supported in Typst output; skipping")
    raise nodes.SkipNode

def visit_inheritance_diagram(self, node):
    logger.warning("inheritance diagrams are not supported in Typst output; skipping")
    raise nodes.SkipNode
```
placed near `visit_index` (`translator.py:2483–2489`), which already follows exactly this "log-and-skip" shape for a different out-of-scope node type. No `depart_*` needed (never reached once `SkipNode` is raised). **This is a 2-method, ~10-line addition — do it early (Part 5, Phase 1), since it's what lets the rest of the milestone iterate against the real Sphinx `doc/` corpus without individual out-of-scope nodes derailing a full-corpus compile run.**

## Part 5 — Recommended build order (dependency-justified)

**Phase 1 — Fatal-bug fix + degradation net (must ship first; unblocks everything downstream)**
1. px→pt length helper (Part 2) — isolated to `visit_image`, zero dependencies.
2. Figure caption buffer-swap fix (Part 1) — isolated to `visit_caption`/`depart_caption`/`depart_figure`, zero dependencies on (1).
3. `visit_graphviz`/`visit_inheritance_diagram` explicit skip overrides (Part 4) — isolated, zero dependencies.

*Rationale: these three are independent of each other and independent of every node handler below, but (1)+(2) are the two fatal bugs blocking Sphinx's own docs from compiling at all (per PROJECT.md), and (3) is what makes the Phase 3 "run against the real corpus" verification step actually usable (a full-corpus compile run is only a useful feedback tool once it doesn't abort on the first `graphviz` node it hits).* All three can be built in parallel (different methods, no shared state) and landed together or in quick succession.

**Phase 2 — Low-risk, high-value, template-reuse handlers (parallel-safe; each independent of the others)**
4. `versionmodified` — direct reuse of `_visit_admonition`/`_depart_admonition`, zero new state (Part 3). Highest single-node frequency (×972) for the effort.
5. Empty-URL `refid` fallback in `visit_reference` — small, contained, extends existing code (Part 3). Second-highest frequency (×596).
6. `desc_returns`/`desc_inline`/`desc_optional` — reuse existing `desc_*` passthrough/`+`-concatenation patterns (Part 3), one new boolean only for the related `desc_signature_line`.

*Rationale: all reuse an already-proven pattern with at most one new state variable combined; none touch shared/high-traffic methods like `visit_reference`'s core link logic (the `refid` fallback is additive) or `visit_Text` in a way that risks regressing existing coverage. Safe to parallelize across contributors/PRs.*

**Phase 3 — Shared-dispatch-point changes (do together, single PR; touches `visit_title`, a method every admonition and every section heading already depends on)**
7. Generalize `visit_title`'s `isinstance(node.parent, nodes.Admonition)` branch to a three-way dispatch adding `topic` (Part 3). **Must include regression tests for existing admonition titles** (the Phase 8.1 fix) alongside new topic-title tests, since this is the one change in the milestone that edits an already-load-bearing shared method rather than adding new isolated methods.
8. `topic`/`line_block`/`line` body wrappers (Part 3) — depend on (7) landing first for their title rendering to be correct.

**Phase 4 — Footnote pre-pass (highest complexity; do last among node handlers)**
9. `footnote`/`footnote_reference` (Part 3) — the only genuinely new architectural pattern (document-order pre-pass + id-keyed lookup dict). Has no dependency on Phases 1–3, but deliberately sequenced last so the team is applying a brand-new pattern with the confidence of several already-shipped, simpler wins behind it, and so any fixture/test-harness improvements made along the way (e.g., a `doctree.pformat()` dump helper for verifying MEDIUM-confidence node shapes) are already in place to de-risk it.

**Phase 5 — Full-corpus verification (depends on all of the above)**
10. Compile Sphinx's own `doc/` tree end-to-end through `typstpdf` (the milestone's stated acceptance bar). Catalog any remaining `unknown_visit` warnings by frequency — this becomes the backlog input for a future milestone, not a blocker for this one (per PROJECT.md's "highest-frequency" framing, not "every node").

## Sources

- `typsphinx/translator.py` (own repo, read in full: lines 1–2794) — HIGH, primary source. Cited line numbers: `visit_figure`/`depart_figure` 1163–1199, `visit_caption`/`depart_caption` 1201–1227, `visit_image`/`depart_image` 1501–1546, `visit_target` 1548–1603, `visit_reference`/`depart_reference` 1930–2036, `unknown_visit`/`unknown_departure` 2038–2059, `visit_term`/`depart_term` 1086–1121, `visit_definition`/`depart_definition` 1123–1161, admonition helpers `_visit_admonition`/`_depart_admonition` 2292–2345 + all `visit_note`/`visit_warning`/etc. callers 2351–2454, `visit_title`/`depart_title` 190–238, `desc_*` family 2495–2767, `visit_index` 2483–2493, `visit_list_item`/`depart_list_item` 883–919, `visit_emphasis`/`visit_strong` 515–653, `_compute_relative_image_path`/`_compute_relative_include_path` 1637–1851.
- `typsphinx/writer.py` (own repo, read in full) — HIGH, primary source: master-vs-included branch and hardcoded `@preview` import block (lines 36–153) confirmed to need no changes for this milestone (all new handlers use Typst stdlib functions only).
- `.planning/PROJECT.md` — HIGH, primary source: milestone scope, frequency counts (`versionmodified` ×972, empty-URL refs ×596), Issue #114 bug description, out-of-scope boundary.
- `.planning/codebase/ARCHITECTURE.md` (2026-07-04 codebase map) — HIGH, primary source: confirms overall pipeline shape and pre-existing "Fragile Areas" callout on `TypstTranslator` state management (translator.py:19–92), which this milestone's new handlers must not worsen.
- `.planning/codebase/CONCERNS.md` (2026-07-04 codebase map) — HIGH, primary source: independently flags the same `translator.py` state-management fragility and nested-image-path fragility this research builds on.
- docutils/Sphinx node-attribute conventions (`refuri`/`refid`/`refname` on `reference`, `label` child + numbered-definition shape of `footnote`, `addnodes.versionmodified` `type`/`version` attributes) — MEDIUM confidence, reasoned from standard docutils/Sphinx API conventions (training knowledge), **not verified against a live doctree dump in this research pass**; flagged per-section above with an explicit "verify" note where the exact shape affects the design.

---
*Architecture research for: typsphinx v0.6.0 real-world robustness (Issue #114 + high-frequency node support)*
*Researched: 2026-07-11*

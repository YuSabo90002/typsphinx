# Stack Research

**Domain:** Sphinx→Typst translator robustness (v0.6.0, Issue #114 + high-frequency dropped-node support)
**Researched:** 2026-07-11
**Confidence:** HIGH

## Bottom Line

**No new runtime dependency and no new `@preview` package is required for v0.6.0.** Every target node type in scope (figure/image units, `versionmodified`, empty-URL refs, autodoc `desc_returns`/`desc_signature_line`/`desc_inline`/`desc_optional`, `footnote`/`footnote_reference`, `transition`, `topic`, `line`/`line_block`) maps onto either a **native Typst 0.15 construct** already reachable from code-mode, or the **already-bundled `gentle-clues` package** via the existing `_visit_admonition`/`_depart_admonition` helper. This is pure `typsphinx/translator.py` work (new `visit_*`/`depart_*` methods + one small unit-conversion helper) — it does not touch `pyproject.toml`, `uv.lock`, `writer.py`'s import list, `template_engine.py`'s import list, or `templates/base.typ`. **The 3-way `@preview` version-sync surface (writer.py / template_engine.py / templates/base.typ) is untouched by this milestone.**

## Recommended Stack

### Core Technologies (unchanged from v0.5.0)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Sphinx | 9.1 | doctree source | Already pinned; no version change needed for this work |
| docutils | 0.22.4 | node types (`versionmodified`, `footnote`, `transition`, `topic`, `line_block`, image length attrs) | Already pinned; all target nodes already exist in this docutils/Sphinx version — nothing to upgrade |
| typst (typst-py) | 0.15.x | compile target | Already pinned; `footnote()`, `line()`, and the length-unit grammar used below are all present and stable in 0.15 (verified against the live typst.app/docs/reference pages, not guessed) |
| Python | 3.12–3.13 | runtime | Unchanged |

### Supporting Libraries — **none added**

No new PyPI package and no new `@preview` package is needed. The four bundled `@preview` packages are reused as-is:

| Library | Version | Purpose | Relevance to v0.6.0 |
|---------|---------|---------|---------------------|
| `@preview/gentle-clues` | 1.3.1 (unchanged) | boxed callouts | Reused for `versionmodified` (added/changed/deprecated/removed) via the existing `_visit_admonition` helper — **no version bump** |
| `@preview/codly` | 1.3.0 (unchanged) | code blocks | Not touched by this milestone |
| `@preview/codly-languages` | 0.1.10 (unchanged) | codly language defs | Not touched |
| `@preview/mitex` | 0.2.7 (unchanged) | LaTeX math | Not touched |

### Development Tools

Unchanged: `uv`, `tox`/`tox-uv`, `black`, `ruff`, `mypy`, `pytest`. No new dev-tool needed; the smoke-gate pattern from Phase 8.1/9 (`tests/test_pdf_render_gate.py`, `tests/test_preview_smoke_gate.py`) is the template to extend with fixtures for the new node types, not a new tool.

## Node-Type → Typst-Construct Mapping (verified, Typst 0.15)

| Target node | Typst 0.15 construct | New dependency? | Notes |
|---|---|---|---|
| `image`/`figure` — `px`/CSS length units | **Native**: convert numerically to `pt` before emitting `image(..., width: <N>pt)` | None | Typst's length grammar supports `pt`, `mm`, `cm`, `in`, `em` (and ratios via `%`) — confirmed on the official Length reference page. **`px` does not exist as a Typst length unit** — a bare `"300px"` string passed through verbatim (today's behavior, `translator.py:1527-1533`) is exactly the Issue #114 fatal-compile bug. Conversion: `1px = 0.75pt` (CSS canonical 96px/in ÷ 72pt/in — cross-verified across multiple independent conversion references, non-controversial CSS-spec fact). `%`/`em` pass through unchanged (both are native Typst relative-length units); `ex`, `pc` (docutils-legal but rare) should convert to `pt`/`em` equivalents or fall back to a safe default with a logged warning rather than emit invalid syntax. |
| `figure` `:target:`-linked (Issue #114) | **Native**: `#figure(link(<url-or-label>)[#image(...)], caption: [...])` | None | `link()` takes exactly one destination + one content body — juxtaposing `link(url, image(...))` as two positional args (today's implied bug) is invalid syntax. Fix is purely a call-shape correction, no package involved. |
| `versionmodified` (`versionadded`/`versionchanged`/`deprecated`/`versionremoved`) | **Already-bundled `@preview/gentle-clues` 1.3.1**, reusing the existing `_visit_admonition`/`_depart_admonition` helper (same one that already renders `note`/`warning`/`tip`/`error`/`danger`/generic `admonition`) | None (no version bump) | Confirmed via Sphinx source (`sphinx/domains/changeset.py` `VersionChange.run()`): the node is `class versionmodified(nodes.Admonition, nodes.TextElement)` with `.type` ∈ `{added, changed, deprecated, removed}` and `.version`. Sphinx **already embeds** the "Added in version X" label as an `inline` node inside the versionmodified node's own children (first child of a `paragraph`) — the translator does **not** need to synthesize label text itself, just needs `visit_versionmodified`/`depart_versionmodified` methods that dispatch on `node['type']`. Suggested clue mapping (reusing only clue-function names already proven to compile in this repo per Phase 8.1's validated set — `info`/`tip`/`warning`/`danger`/`error`/base `clue`): `added`→`tip`, `changed`→`info`, `deprecated`→`warning`, `removed`→`danger`. |
| empty-URL cross-references | **Native** (already partially handled) | None | `visit_reference` (`translator.py:1972-1983`) already detects `refuri == ""` and degrades to plain text with a logged warning — this is not a new-stack problem, it's a translator-logic problem (the milestone goal is "resolve where possible" — e.g. falling back to an internal Typst `label`/anchor when a `refid` exists on the node even though `refuri` is empty — pure Python/tree-walking work, no library). |
| `desc_returns`, `desc_signature_line`, `desc_inline`, `desc_optional` | **Native** — same pattern as the already-implemented `desc_signature`/`desc_annotation`/`desc_name`/`desc_parameterlist`/`desc_parameter` siblings (`translator.py:2511-2621`), i.e. plain `text()`/`strong()`/passthrough code-mode concatenation | None | These are Sphinx `addnodes` (not docutils core), but they're structurally identical in kind to the already-supported `desc_*` family — no markup beyond what `strong()`/`text()`/inline concatenation already provides. `desc_optional` wraps optional-parameter groups (needs bracket punctuation, same shape as `desc_parameterlist`'s paren handling); `desc_signature_line` is a multi-line-signature grouping wrapper (pass-through block); `desc_inline` is an inline-signature variant (pass-through inline); `desc_returns` is a return-type annotation (render like `desc_annotation`, e.g. prefixed with `" → "`). |
| `footnote` / `footnote_reference` | **Native**: Typst's `footnote()` function | None | Verified on typst.app/docs/reference/model/footnote: `footnote(numbering: str|function, body: label|content) → content`; footnote text at the definition site can be labeled (`#footnote[...] <fn>`) and re-referenced elsewhere via `footnote(<fn>)`. **Design note (not a stack gap):** docutils keeps `footnote_reference` (use-site) and `footnote` (definition, with matching `ids`/`refid`) as separate tree nodes, whereas Typst wants the full footnote body supplied at the `footnote()` call itself. The translator needs a small pre-pass (index `footnote` definitions by id before/while walking) so `visit_footnote_reference` can emit `footnote[<looked-up body>]<label>` and the later `visit_footnote` for the same id can `raise nodes.SkipNode` (or, for a second reference to the same footnote, emit `footnote(<label>)`). This is a tree-walking/bookkeeping concern, not a dependency concern. |
| `transition` | **Native**: `line(length: 100%)` | None | Verified on typst.app/docs/reference/visualize/line: `line(start, end, length: relative = 0%+30pt, angle, stroke: ... = 1pt+black)`. `transition` is a leaf node (no children) — emit `line(length: 100%)\n\n` in code mode (no `#` prefix, consistent with the rest of the code-mode body) and `raise nodes.SkipNode` (nothing to descend into). |
| `topic` | **Native**: `block()` with an inline bold title, e.g. `block(width: 100%, inset: 8pt, radius: 2pt, stroke: 0.5pt + gray)[#strong[<title>]\n<body>]` or simpler — a `text`/`strong` title line followed by the normal block content, no special container needed | None | `topic` is a generic titled container (used for things like a document abstract or a table-of-contents-adjacent aside) — no admonition semantics, so `gentle-clues` is not the right mapping; a plain Typst `block`/`pad` is sufficient and keeps the milestone dependency-free. Treat as parallel to the existing `visit_block_quote`/`visit_container` pattern (`translator.py:1448`, `:299`) rather than the admonition pattern. |
| `line` / `line_block` | **Native**: preserve breaks with Typst's `linebreak()` (code-mode function call) between each `line` child, wrapped in a left-padded `block`/`pad(left: 1em)[...]` to mirror docutils' indentation semantics | None | No package needed — this is the same category of "preserve author-controlled line breaks" as poetry/addresses; `linebreak()` is core Typst, present since early versions and unchanged in 0.15. |
| Out-of-scope graphical nodes (`graphviz`, `inheritance_diagram`) | **N/A — explicitly deferred to graceful `logger.warning` + `SkipNode`**, no rendering attempted | None | Milestone scope explicitly excludes rendering these; the only "stack" implication is confirming the existing `unknown_visit`/`unknown_departure` fallback (`translator.py:2038-2059`) already warns-and-continues without raising, so an explicit `visit_graphviz`/`visit_inheritance_diagram` pair that logs a clearer warning and calls `raise nodes.SkipNode` is enough — still zero new dependencies. |

## Installation

```bash
# No installation changes for v0.6.0 — pyproject.toml, uv.lock, and the
# three @preview-import declaration sites are untouched by this milestone.
uv sync --extra dev --locked   # unchanged from v0.5.0
```

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| Reuse `gentle-clues` (already bundled) for `versionmodified` | Add a dedicated "changelog"/"version-badge" `@preview` package | Would add a 4th→5th sync point across `writer.py`/`template_engine.py`/`templates/base.typ` for a cosmetic improvement (a colored badge vs. an already-available boxed callout) that the milestone's own bias ("avoid dependency growth" during a maintenance/robustness cycle) argues against. `gentle-clues`'s existing `tip`/`info`/`warning`/`danger` clue functions (already proven to compile clean under typst 0.15 per Phase 7/8.1) cover the four `versionmodified` types with zero new sync risk. |
| Native `line(length: 100%)` for `transition` | A `@preview` "rule"/divider package | None exists that's simpler than one native function call; adding a package for a single-line primitive is pure overhead. |
| Native `footnote()` for `footnote`/`footnote_reference` | Manual superscript-number + end-of-page manual list (mimicking pre-Typst LaTeX `\footnotetext`-by-hand approach) | Typst's built-in footnote mechanism already handles numbering, page-breaking, and back-references — reimplementing that logic manually in the translator would be strictly worse and is exactly what the native function exists to avoid. |
| Numeric `px→pt` conversion (`1px = 0.75pt`) inline in translator | Pull in a units/CSS-length-parsing library (e.g. a `pint`-style dependency) | Massive overkill for a single fixed ratio conversion on a small, closed set of docutils length units (`px, pt, %, em, ex, mm, cm, in, pc`); a ~15-line helper function is sufficient and keeps the "no new dependency" posture for a maintenance milestone. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| Passing docutils `width`/`height` length strings straight through to `image(width: ...)` (current behavior) | This is the literal Issue #114 fatal bug — Typst has no `px` unit and raises a hard compile error, aborting the whole `typstpdf` build | Parse the docutils length string (`re.match(r'([\d.]+)(px|pt|%|em|ex|mm|cm|in|pc)?', value)`), convert `px`→`pt` (`× 0.75`) and leave already-native units (`pt`, `mm`, `cm`, `in`, `em`, `%`) unchanged; for `ex`/`pc` either convert (`1pc = 12pt`, `1ex ≈ 0.5em` as a documented approximation) or drop the attribute with a logged warning rather than emit invalid syntax |
| `link(url, image(...))` two-positional-arg juxtaposition for target-linked figures | Not valid Typst `link()` call shape (`link` takes one destination + one content body) — this is the second half of the Issue #114 fatal bug | `link(dest)[#image(...)]` or `#figure(link(dest)[#image(...)], caption: [...])` |
| A new `@preview` package for anything in this milestone's scope | Every target node type is coverable natively or via the already-bundled `gentle-clues`; adding a package here would grow the 3-way version-sync surface for no functional gain, contradicting the milestone's maintenance/robustness framing | Native Typst 0.15 constructs (`footnote()`, `line()`, `block()`, `linebreak()`, length-unit literals) + the existing `gentle-clues` clue functions |

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| typst 0.15.x | `footnote()`, `line()`, native length units (`pt`/`mm`/`cm`/`in`/`em`/`%`) | All verified live against the current typst.app/docs/reference pages (footnote, visualize/line, layout/length) — no `px` unit exists in any typst version to date, this is not a 0.15-specific gap |
| `@preview/gentle-clues` 1.3.1 | typst 0.15.x | Already confirmed compiling clean under typst 0.15 (Phase 7/8.1 smoke gate); no version change needed to add `versionmodified` support since it reuses the same clue functions already exercised |
| docutils 0.22.4 length-attribute grammar | Sphinx 9.1 image/figure directives | `width`/`height` option values on `image`/`figure` directives accept `px|pt|%|em|ex|mm|cm|in|pc`-suffixed measures (via `docutils.parsers.rst.directives.length_or_percentage_or_unitless`/`length_or_unitless`) — this is the exact unit set the conversion helper must handle |

## Sources

- https://typst.app/docs/reference/layout/length/ — Length unit grammar (`pt`, `mm`, `cm`, `in`, `em`; no `px`) — HIGH confidence, official Typst reference, fetched live
- https://typst.app/docs/reference/visualize/line/ — `line()` signature (`length: relative = 0% + 30pt`, `stroke: 1pt + black`) — HIGH confidence, official Typst reference, fetched live
- https://typst.app/docs/reference/model/footnote/ — `footnote()` signature and label/re-reference pattern — HIGH confidence, official Typst reference, fetched live
- https://github.com/sphinx-doc/sphinx/blob/master/sphinx/domains/changeset.py — `VersionChange.run()`: confirms `versionmodified` node structure, `.type`/`.version` attributes, and that the "Added/Changed in version X" label is pre-embedded as an `inline` node child — HIGH confidence, primary source (Sphinx's own code), fetched live
- CSS canonical `96px = 72pt` (⇒ `1px = 0.75pt`) — HIGH confidence, cross-checked across multiple independent conversion references, a long-standing non-controversial CSS-spec-derived constant
- `/home/yuta/Documents/typsphinx/typsphinx/translator.py` (read directly, lines 1163-2789) — existing `visit_figure`/`visit_image`/`visit_reference`/`_visit_admonition`/`visit_desc_*`/`unknown_visit` implementations — HIGH confidence, first-party source of truth for what's already built vs. what's missing
- `/home/yuta/Documents/typsphinx/typsphinx/writer.py` and `template_engine.py` (read directly) — confirms the exact 3 `@preview` import lines this milestone must NOT touch (versions: codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1) — HIGH confidence, first-party
- `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` — Phase 8.1 history confirming which gentle-clues clue-function names (`info`/`warning`/`tip`/`error`/`danger`/base `clue`) are already validated compiling under typst 0.15 in this exact repo — HIGH confidence, first-party validated history
- Gentle-clues clue-type name list from a general WebSearch — **discarded as unreliable**: the search surfaced an old `0.4.0`-era README (`abstract`/`question`/`memo`/etc.) that does not match this repo's already-verified 1.3.1 usage; the in-repo Phase 8.1 evidence (validated by an actual `typst compile` smoke gate) supersedes it. Do not use `success`/`abstract`/`memo`/etc. clue names without re-verifying against the actual 1.3.1 package source.

---
*Stack research for: typsphinx v0.6.0 real-world robustness (Issue #114 + high-frequency dropped-node support)*
*Researched: 2026-07-11*

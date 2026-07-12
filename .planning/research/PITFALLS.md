# Pitfalls Research

**Domain:** Sphinx→Typst translator node-handler development (typsphinx v0.6.0, "real-world robustness")
**Researched:** 2026-07-11
**Confidence:** HIGH (grounded in direct read of `typsphinx/translator.py`, `tests/test_pdf_render_gate.py`, `.planning/PROJECT.md`, `.planning/codebase/CONCERNS.md`, and official Typst documentation)

## Critical Pitfalls

### Pitfall 1: One bad node aborts the ENTIRE PDF — there is no partial-compile fallback

**What goes wrong:**
`typst.compile()` (in `pdf.py`) is a single all-or-nothing call over the whole master document (and everything it `#include()`s). If **any** node handler anywhere in the tree emits syntactically invalid Typst — one bad `width:`, one unescaped caption, one malformed `link()` — the entire `typstpdf` build fails with `TypstCompilationError`, not just the offending page. This is categorically different from the `typst` (markup-only) builder or the HTML builder, where a bad node degrades one region of output. For a large corpus like Sphinx's own `doc/` tree (the v0.6.0 acceptance target), a single rare node instance (e.g. one `versionchanged` inside one obscure page) is fatal to the whole run.

**Why it happens:**
Node-handler work is naturally done and tested one node type at a time (unit tests, small fixtures). It is easy to ship a handler that is correct for the common case tested but produces invalid syntax on an edge-case attribute value (a percentage width, an empty title, a caption containing `_` or `[`) that only appears somewhere deep in a 900-page real corpus — and that one instance takes down the whole compile.

**How to avoid:**
- Treat "does it compile" as the primary correctness signal for every new/changed handler, not "does the string look right" (see Pitfall 9).
- Add the real Sphinx `doc/` corpus (or a growing subset of it) as a standing `typst.compile()` regression fixture as soon as Issue #114 is fixed — every phase after that should compile it and fail loudly on any `TypstError`, the same way `tests/test_preview_smoke_gate.py` already does for the four `@preview` packages.
- Prefer handlers that are structurally incapable of emitting invalid syntax (e.g. always closing what they open, always going through a single length-normalization helper) over handlers that are merely tested against today's known inputs.

**Warning signs:**
- A new visitor method with `add_text` calls that are conditionally skipped (`if X: skip`) without a matching skip on the paired `depart_`/closing text — orphaned open parens/brackets compile fine on the happy path and only break on the conditional branch.
- Any handler that trusts a docutils attribute value (`width`, `refuri`, caption text) to already be Typst-safe.

**Phase to address:** Every phase in this milestone — this is the standing acceptance bar, not a one-time fix. The Issue #114 fix phase should also stand up the real-corpus compile gate described in Pitfall 9, since every subsequent node-handler phase depends on it to catch fatal regressions.

---

### Pitfall 2: Markup-mode vs. code-mode mismatch (the v0.5.0 admonition precedent, recurring)

**What goes wrong:**
typsphinx's translator runs in "unified code mode": function calls are emitted bare at the top level (`heading(...)`, `figure(...)`, `image(...)`) with `#` only required inside markup content blocks (`[...]`). A handler that assumes the wrong mode for its position either (a) emits literal, uncompiled-looking Typst source into the output as inert text (the exact v0.5.0 admonition bug: admonition bodies rendered as literal `par({text(...)})` because `_visit_admonition` opened a markup block `[` where the body's `par({...})`/`text(...)` calls needed code-mode evaluation instead), or (b) emits a bare `#`-prefixed call inside code mode, which is itself invalid syntax there.

**Why it happens:**
The two modes look almost identical in the emitted string and both "look plausible" to a human skimming the generated `.typ`, so this class of bug survives casual review and even passes loose substring assertions (`"info[" in output`). It was *invisible for months* in typsphinx — the admonition bug predated the milestone that finally exposed it, because nothing had ever actually compiled the code path to PDF before.

**How to avoid:**
- Whenever adding a handler that opens a *content-taking* construct (figure caption, footnote body, admonition title, table cell, line-block line), decide explicitly: is this position code-mode (bare function calls, no `#`) or markup-mode (needs `#` prefix, `[...]` content blocks)? Write that decision down in the docstring, as `_visit_admonition`/`visit_title` already do.
- Follow the established buffer-swap pattern (see `visit_title`/`depart_title` around line 190–235, and `_visit_admonition`/`_depart_admonition` around line 2292–2345) for any new construct that needs to defer or transform inline content: swap `self.body` to a private list, let the normal visitor chain render into it (so `emph`/`literal`/etc. still work), then read the buffer back and re-emit it in the correct mode/argument position.
- Never build new inline content by calling `node.astext()` and interpolating the plain string directly (see Pitfall 3, Pitfall 7) — that bypasses the mode question entirely and silently reintroduces both the escaping bug and the double-emission bug at once.

**Warning signs:**
- A visitor that does `self.add_text(f"...[{something}]...")` where `something` came from `node.astext()` rather than from a buffer populated by the normal visit chain.
- Generated `.typ` where a construct's body reads as Typst source text rather than typeset prose when eyeballed in a real compiled PDF (not just the `.typ` file).

**Phase to address:** Every node-handler phase in this milestone (figure/caption, footnote, versionmodified, line_block, topic all introduce new content-taking constructs). Call this out explicitly in each phase's plan review checklist.

---

### Pitfall 3: The figure-caption leak — a NEW, not-yet-fixed instance of the exact double-emission bug class (found during this research)

**What goes wrong:**
Reading `visit_caption`/`depart_caption` (translator.py ~1201–1227) against `visit_Text` (~443–473) shows the admonition-title bug's sibling is still live for figure captions. `depart_caption` extracts the caption via `self.figure_caption = node.astext()` for later use as `caption: [...]` in `depart_figure` — but it never suppresses the normal visitor traversal of the caption's children. Those children (plain `Text` nodes) still get visited by `visit_Text`, which unconditionally appends `text("...")` into whatever `self.body` currently is (there's no `self.in_caption` check there). Net effect: the caption's text is emitted **twice** — once as a stray `text("caption text")` call juxtaposed directly after the preceding sibling (e.g. right after `image(...)` or after `link(url, image(...))`, with no `+` or newline separator — itself independently invalid, see Pitfall 4), and once, correctly, later as the `caption: [...]` argument. This is very likely the literal mechanism behind the milestone's cited buggy output `link(url, image(...))text(caption)`.

**Why it happens:**
`depart_caption` was written to grab the *plain-text* caption via `astext()` (probably to avoid dealing with inline markup), but nothing turns off or buffers the *actual* visitor traversal of the caption's children, so both paths fire. It is the same root cause the admonition-title fix (Phase 8.1) closed for `visit_title`/`depart_title` — but that fix was never generalized to `visit_caption`.

**How to avoid:**
- Apply the exact same buffer-swap pattern already used for admonition titles: in `visit_caption`, swap `self.body` to a private buffer *before* children are visited (not after, in `depart_caption`); in `depart_caption`, read the buffer back as the rendered caption content and restore `self.body`. This also fixes the inline-markup loss (`astext()` throws away any `emph`/`literal` inside a caption) as a side benefit.
- Ensure `depart_figure`'s `caption: [...]` interpolation uses the *rendered* buffered content (which is already markup-mode-safe if visited through the normal chain) rather than a raw string requiring separate escaping.

**Warning signs:**
- Any `depart_*` that computes content via `node.astext()` while the node's children were *not* explicitly skipped (no `raise nodes.SkipNode`, no buffer swap in the matching `visit_*`).
- A compiled PDF where figure captions with a `:target:` link show duplicated or garbled text near the image.

**Phase to address:** The Issue #114 figure/image fix phase — this is squarely in scope and should be fixed alongside the length-unit and link-juxtaposition work, using the real-compile acceptance gate (Pitfall 9) to prove it, exactly as Phase 8.1 did for admonitions.

---

### Pitfall 4: Function-call juxtaposition — sibling code-mode expressions need an explicit `+` (or newline/semicolon), never bare concatenation

**What goes wrong:**
Typst's scripting/code-mode syntax requires expressions in a code block to be separated by a line break or `;` (confirmed via the official Typst syntax/scripting reference). Two function calls placed back-to-back with nothing between them (`image(...)text(...)`, or a caption's stray `text(...)` landing right after a closing `)`) is a parse error, not silently-ignored text. The existing, correct pattern for this in typsphinx is visible in `visit_desc_parameterlist`/`visit_desc_parameter`/`depart_desc_parameter` (~2577–2621): every sibling is explicitly joined with `' + '` and a `_desc_parameter_has_content`-style flag tracks whether a separator is needed before the next one. Any new handler that emits sibling content (figure body + caption, footnote marker + body, a new `desc_returns`/`desc_optional` sibling next to existing `desc_parameter`s) must plug into this same join-with-`+` discipline or reintroduce this exact class of bug.

**Why it happens:**
It's easy to write a new `visit_X`/`depart_X` pair that "looks right" in isolation — each function call is individually well-formed — and forget that in code mode, *placement next to a sibling* is itself a syntax decision. This is invisible until a real value from a real corpus places two such siblings adjacent to each other (e.g. an image directly followed by a caption, or a signature followed by a new `desc_returns` node).

**How to avoid:**
- For every new node type that can appear as a *sibling* inside an existing code-mode sequence (figure content, desc_signature line, footnote content), explicitly decide and implement the separator: reuse the `_desc_parameter_has_content`-style boolean-flag pattern, or wrap the new content in an explicit content-block `[...]` argument to a named parameter (e.g. `caption:`, `title:`) so it's never juxtaposed as a bare sibling expression at all.
- Prefer routing new content through a *named argument* (`figure(..., caption: [...])`, `clue({...}, title: {...})`) over positional/sequential juxtaposition wherever the target function supports it — named arguments sidestep the separator problem entirely.
- For the `:target:`-linked figure specifically: the correct target shape per the milestone is `figure(link(...)[#image(...)], caption: [...])` — note `image(...)` here is inside a markup content block (`[#image(...)]`) as the link's *body argument*, not code-mode juxtaposed after it. Confirm which of `link`'s two forms (content-block second argument vs. code-mode second positional argument) is used, and don't mix the two conventions within the same call.

**Warning signs:**
- Any place a new visitor's `add_text` output would end up directly adjacent (no `+`, no newline, no comma) to another function call's closing `)` in the same code-mode context.
- Compile errors mentioning "expected semicolon" or "expected expression" near a figure/signature line in the generated `.typ`.

**Phase to address:** Issue #114 figure/image fix phase (for `link`+`image`+caption); the autodoc `desc_returns`/`desc_signature_line`/`desc_inline`/`desc_optional` phase (for signature siblings) — both must be reviewed against this pattern explicitly, not just against unit-string output.

---

### Pitfall 5: px→pt is not 1:1 — naive unit pass-through emits units Typst doesn't understand

**What goes wrong:**
`visit_image` (translator.py ~1527–1533) currently does `self.add_text(f", width: {width}")` with **zero unit handling** — whatever string docutils put in `node["width"]` (e.g. `"200px"`, `"50%"`, `"3em"`, `"2in"`, `"1pc"`, or a bare unitless number) is interpolated verbatim into the Typst source. Typst's length type supports only `pt`, `mm`, `cm`, `in`, and `em` (font-relative) — **`px` is not a valid Typst unit** (confirmed via the official Typst length reference and an open Typst feature request to add one). `:width: 200px` therefore emits `width: 200px`, which is a hard compile error, aborting the whole document (Pitfall 1). `pc` (pica) is similarly unsupported natively. `%` alone is fine as-is (Typst's ratio/relative-length type accepts a bare `50%` for `width:`/`height:` directly), and `em` passes through unchanged since Typst supports it natively — but only if the surrounding code doesn't also try to re-append a unit suffix.

**Why it happens:**
Docutils' `:width:`/`:height:` directive options accept CSS-style length strings (`%`, `em`, `ex`, `px`, `in`, `cm`, `mm`, `pt`, `pc`, or unitless) and preserve them as-is without any conversion — docutils itself never converts units, it only validates the syntax. It's tempting to assume "docutils already validated it, so it's a safe length string" and pass it straight through, but "syntactically valid CSS length" and "syntactically valid Typst length" are different, only-partially-overlapping grammars.

**How to avoid:**
Write one shared length-normalization helper (analogous to `_compute_relative_image_path`) used by every place a `width`/`height` value reaches Typst output, with this mapping:

| Docutils unit | Typst handling | Conversion |
|---|---|---|
| `%` | pass through unchanged | none — `50%` is valid Typst ratio syntax as-is |
| `em` | pass through unchanged | none — Typst supports `em` natively as a font-relative length |
| `in`, `cm`, `mm` | pass through unchanged | none — all three are native Typst absolute units |
| `pt` | pass through unchanged | none — already the Typst native unit |
| `px` | **convert to `pt`** | `pt = px * 0.75` (CSS reference pixel: 96px/in ÷ 72pt/in = 0.75) |
| unitless bare number | treat as `px` (docutils/HTML convention), then convert | same as `px` above |
| `pc` (pica) | **convert to `pt`** | `pt = pc * 12` (1 pica = 12 points, no native Typst unit) |
| `ex` | no Typst equivalent | approximate as `0.5em` (typical x-height/em-height ratio) or drop with a `logger.warning`, never pass through raw |

Never string-strip a trailing unit suffix blindly (e.g. `width[:-2]`) — `%`, `em`, `pt`, `in`, `cm`, `mm` are 2 characters but `px`/`pc` are also 2, and blind stripping either double-strips a valid unit's letters or fails to recognize which suffix was present at all. Parse the unit suffix explicitly (regex match on the trailing alpha run), don't assume length.

**Warning signs:**
- Any `width`/`height` interpolation without a length-normalization call in front of it.
- `TypstError` mentioning "unknown unit" or a numeric-parse failure anywhere near an `image(...)` or `figure(...)` call, when compiling a corpus that contains `:width: NNpx` (very common in hand-authored Sphinx docs, including likely several in Sphinx's own `doc/` tree).
- A "fix" that only handles `%` (because that's the example in the bug report) and ignores `px`/`pc`/`ex`/unitless, which are just as common in a large real corpus.

**Phase to address:** Issue #114 figure/image fix phase (this is the explicit REQ target — "convert `px`/CSS length units to Typst-valid `pt` (or drop)"). Verification should include at least one fixture image with `:width: 200px`, one with `:width: 50%`, one with `:width: 3em`, and one with a bare unitless number, each proven to compile via the real-render gate (Pitfall 9), not just a string assertion.

---

### Pitfall 6: Footnote modeling mismatch — docutils' split footnote/footnote_reference vs. Typst's single inline `footnote[...]`

**What goes wrong:**
Docutils represents a footnote as **two separate, disconnected nodes**: a `footnote_reference` (the inline superscript marker at the point of use, which may appear multiple times for the same footnote if referenced twice) and a `footnote` node (the footnote's actual body content, which docutils places as a sibling block — often at the end of the section/document, not adjacent to the reference — and which is visited by the translator entirely separately from its reference(s)). Typst's model is the opposite: `footnote[body]` is a **single inline call at the point of reference** — it simultaneously inserts the superscript marker *and* carries the body content, and Typst's layout engine automatically places the rendered note at the bottom of the page and auto-numbers it (confirmed via the official Typst footnote documentation). A naive one-visitor-per-docutils-node-type port (`visit_footnote_reference` emits a marker, `visit_footnote` separately emits the body wherever docutils put that node in the tree) will produce one of:
- the footnote body rendered as an ordinary floating paragraph wherever docutils placed the `footnote` node (often visually disconnected from its reference, sometimes at the very end of the document), with **no** auto-numbered marker tying it to its reference(s), or
- if a naive `footnote[...]` call is emitted at *both* the reference and the body's docutils location, a **doubled** footnote (two numbered notes for one logical footnote), or
- for a footnote referenced from two places (`footnote_reference` appearing twice pointing at the same `footnote` id) — a genuine one-to-many relationship docutils supports natively but Typst's `footnote[]` doesn't directly model (Typst has no native "same footnote referenced twice" primitive without manually reusing a label/counter).

**Why it happens:**
This is a structural, not cosmetic, mismatch between the two document models — it's the same category of issue as the title/caption double-emission bugs (Pitfall 2/3), but arising from the *source* format's structure rather than a translator bug, so it can't be fixed with a simple buffer swap alone; it needs a deliberate design decision up front. Confirmed via direct code search: no `visit_footnote*` methods exist anywhere in `translator.py` today — this is entirely greenfield work, not a bug fix.

**How to avoid:**
- Do NOT visit the `footnote` node's body independently and separately visit each `footnote_reference`. Instead, resolve `footnote_reference`'s target `refid`, look up the corresponding `footnote` node's content at the reference site, and emit a single `footnote[...]` call inline at each `footnote_reference` occurrence — buffering the footnote body's rendered content (same buffer-swap pattern as Pitfall 2) so it can be replayed inline wherever it's referenced.
- Explicitly decide (and test) the "referenced twice" case: either accept a duplicate note per Typst's model (simplest, and arguably correct visually — Typst will just show the number twice, once per reference, which is standard behavior even in LaTeX), or investigate Typst's footnote re-use idiom (a labeled counter) only if the corpus (Sphinx's own docs) actually exercises this case.
- Make sure the docutils `footnote` node itself is a documented no-op / `SkipNode` at its *own* tree location once its content has been captured for inline replay — otherwise its body renders a second time wherever docutils physically placed it.

**Warning signs:**
- A compiled PDF with footnote numbers that don't match, or footnote text appearing at the very end of the document collected together rather than per-page.
- Any implementation that emits `footnote[...]` inside `visit_footnote` (the body node) rather than at `visit_footnote_reference` (the inline marker node).

**Phase to address:** The footnote/footnote_reference support phase (new node handlers, currently entirely unimplemented). This needs its own design note before implementation, not just an incremental patch.

---

### Pitfall 7: Escaping — three DIFFERENT escaping regimes exist, and using the wrong one for new content is invisible until compile

**What goes wrong:**
typsphinx already has (at least) two distinct escaping regimes in active use, and a new handler that borrows the wrong one — or bypasses both via `astext()` — silently produces either broken syntax or a security-adjacent injection-style bug (arbitrary user doc content reinterpreted as Typst markup):
1. **String-literal escaping** (`visit_Text`, ~456–468): backslash, then quote, then `\n`/`\r`/`\t`, in that exact order, for content going inside a `"..."` string argument to `text(...)`. Order matters — escaping backslash *after* quote would double-escape.
2. **Markup-mode escaping**: content going inside a bare `[...]` content block is NOT a string literal — Typst markup-special characters (`_`, `*`, `` ` ``, `#`, `[`, `]`, `<`, `@`, leading `-` for lists, etc.) are live syntax there, not literal text. The `visit_caption`/`depart_figure` path (Pitfall 3) is a live example of the trap: `self.figure_caption = node.astext()` grabs *raw* plain text and later interpolates it directly into `caption: [{self.figure_caption}]` — a markup content block — with **zero markup escaping**. A caption like `"Config_file (draft) [v2]"` will have `_file` trigger emphasis and `[v2]` parse as bracketed content, corrupting or breaking the layout, because `astext()` bypasses both escaping regimes entirely.
3. **Label/identifier constraints** (`visit_target`, `label(...)`) — Typst labels accept a fairly restrictive character set; docutils-generated `ids` (from heading slugs) are usually ASCII+hyphen and safe, but any handler that builds a label from *user-supplied* text (rather than docutils' own sanitized `ids` list) risks emitting a label Typst's parser rejects outright.

**Why it happens:**
Escaping-regime choice is implicit in *where* a value is being interpolated (string argument vs. markup content block vs. label), and that's easy to get wrong when adding a new handler by analogy to an existing one that happens to interpolate in the other regime. `astext()` is especially seductive because it "just works" for the common case (plain ASCII words with no markup-special characters) and only breaks on the corpus-scale edge case.

**How to avoid:**
- Never use `node.astext()` to source content that will be interpolated into generated Typst output, for *any* new handler — always let the normal visit/depart chain render it (through a buffer swap if it needs to be deferred/repositioned), so it automatically inherits whichever escaping regime the destination code path already applies consistently.
- When adding a genuinely new interpolation site (e.g. a footnote label, a `versionmodified` version string), explicitly identify which of the three regimes applies and either reuse the existing helper (`visit_Text`'s escape sequence) or write a matching one — don't ad-hoc a partial subset of escaping "for now."

**Warning signs:**
- Any new `f"...{value}..."` where `value` came from `.astext()`, `.get(...)`, or a raw docutils attribute rather than a rendered/escaped buffer.
- Test fixtures that only use plain-ASCII-word captions/labels/titles — they will not exercise this class of bug at all; fixtures need at least one caption/title containing `_`, `*`, `` ` ``, `[`, or `]`.

**Phase to address:** Figure/caption fix phase (Pitfall 3's fix must apply markup escaping, not `astext()`), and as a standing review item for every new content-emitting handler this milestone (versionmodified strings, footnote text, topic titles, line-block lines).

---

### Pitfall 8: "Fixing" empty-URL references by emitting `link("", ...)` — Typst rejects it, and the fix must generalize to every new reference-like path

**What goes wrong:**
`visit_reference` (~1976–1983) already has the correct fix for plain `reference` nodes: an empty `refuri` sets `_skip_link_wrapper = True` and falls through to plain-text rendering instead of emitting `link("", ...)`, which Typst's `link` function rejects outright (empty URLs are invalid `link` destinations as of the typst-py version this project pins — this is the codebase's own documented rationale, referencing the historical Issue #77 empty-URL fix). The trap for this milestone is that "empty-URL cross-reference handling" is explicitly a v0.6.0 target for *new* node paths — and each new path that builds its own `link(...)` call (rather than delegating to the existing `visit_reference`) can reintroduce the exact same bug if it doesn't independently guard the empty-URL case. Any new autodoc/`desc_*` cross-reference handling, or `pending_xref`-derived internal reference nodes not already routed through `visit_reference`, is at risk.

**Why it happens:**
The guard lives in one specific method (`visit_reference`); it's easy to forget it needs to be duplicated (or better, centralized) for any other code path that also ends up building a `link(...)` call — e.g. if the empty-URL cross-reference work adds a *different* resolution attempt (trying to resolve the target before giving up) that has its own separate call site emitting `link(...)`.

**How to avoid:**
- Centralize link-emission behind a single helper (`_emit_link(url, content)`) that internally applies the empty-URL guard once, and have every reference-like handler — present and future — call through it, rather than each handler reimplementing the `if not refuri: ...` check inline.
- For the "resolve where possible" half of this REQ (reduce silent plain-text degradation): resolution failures should still degrade to the *existing* plain-text fallback path, not a new, unguarded `link("", ...)` attempt as a "best effort."

**Warning signs:**
- A new handler with its own `f'link("{url}", ...'` construction that doesn't check for falsy `url` first.
- `TypstError` messages referencing an invalid/empty link destination surfacing only on a large real corpus (broken cross-references are common at scale, rare in small hand-written fixtures).

**Phase to address:** The empty-URL cross-reference handling phase (explicit v0.6.0 target, REQ frequency ×596 in Sphinx docs — meaning this WILL be exercised heavily by the real-corpus compile gate).

---

### Pitfall 9: Testing with string-agreement asserts alone proves nothing about whether the output compiles

**What goes wrong:**
The admonition bug (Phase 8.1) is the project's own proof of this: loose in-process substring assertions like `"info[" in output` passed for months while the *actual* rendered PDF showed literal, uncompiled Typst source text (`par({text(...)})`) instead of typeset prose — because the assertion checked that a *substring pattern* appeared somewhere in the generated string, not that the generated string, when compiled, produced the intended visual result. A pure string/AST-level unit test cannot distinguish "syntactically valid Typst that happens to contain this substring" from "Typst that compiles and typesets correctly" from "Typst that fails to compile at all" — it can only tell you the string looks like what a human expected, not what the compiler will do with it.

**Why it happens:**
Unit tests on translator output are fast, hermetic, and easy to write against the translator in isolation, so they're the natural first (and often only) layer of testing added for a new node handler. Wiring up a real `sphinx-build → typst.compile() → pypdf text-extraction` round trip is more setup, so it's tempting to treat string-level tests as sufficient — but they test the wrong contract (has the string got the shape I expect) rather than the one that actually matters (does this compile, and does the compiled PDF contain the intended text).

**How to avoid:**
Follow — and extend — the precedent already established in `tests/test_pdf_render_gate.py` (D-04, Phase 8.1) for every new node handler in this milestone:
1. `sphinx-build -b typst` a small real fixture project exercising the new node.
2. `typst.compile()` the emitted `.typ` — this is the acceptance gate; a `TypstCompilationError` here is an unconditional test failure, regardless of what any string assertion says.
3. Extract text with `pypdf` and assert the intended prose is present *and* that known literal-leak signatures (`"par({"`, `'text("'`, `'raw("'`, or any other raw-source-looking substring) are **absent** — a negative-control assertion, matching the existing `LEAK_SIGNATURES` pattern.
4. Reserve pure string/unit-level translator tests for fast, fine-grained regression coverage *in addition to*, never *instead of*, the real-compile gate for any node that emits new syntax shapes (new function calls, new nesting, new argument positions).

**Warning signs:**
- A PR/plan that adds a new `visit_*`/`depart_*` pair with only `assert "some_string" in output`-style tests and no `typst.compile()` step anywhere in its test additions.
- CI green on a feature branch with no `docs-pdf`/real-corpus compile step exercised for that specific node type.

**Phase to address:** Every node-handler phase this milestone should ship its own `test_pdf_render_gate.py`-style fixture (or extend the existing one) exercising the new node through a real compile — not just the final "compile Sphinx's own docs" acceptance phase at the end.

---

### Pitfall 10: Graceful degradation done wrong — silent swallowing, or a fallback that itself can't compile

**What goes wrong:**
The milestone explicitly wants `graphviz`/`inheritance_diagram` (and other out-of-scope graphical nodes) to "warn without aborting the compile." Two distinct wrong ways to implement this: (a) a bare `except Exception: pass` / a `raise nodes.SkipNode` with no `logger.warning` at all — silently dropping content with no trace, which is exactly the "Broad Exception Handling" tech-debt pattern already flagged project-wide in `.planning/codebase/CONCERNS.md` (broad `except Exception` in `builder.py`/`pdf.py`); and (b) a fallback that *does* warn correctly but emits a "safe-looking" placeholder that is itself invalid Typst in some contexts — e.g. emitting a bare content block `[Graphviz diagram omitted]` at a position where the surrounding code expects a code-mode expression (reintroducing Pitfall 2's mode mismatch inside the very code meant to prevent fatal errors), or emitting an opening call with no matching close if the node's `visit_*` degrades but its `depart_*` doesn't know it degraded (reintroducing Pitfall 1's orphaned-state hazard).

**Why it happens:**
"Graceful degradation" is often implemented reactively, at the point something is observed to throw, rather than designed as a deliberate no-op path with its own state-safety guarantees; and the project's existing broad-`except Exception` pattern (already documented tech debt) makes it the path of least resistance to copy.

**How to avoid:**
- Always pair a degradation with an explicit `logger.warning(...)` naming the node type and location (mirroring the existing empty-URL warning at `visit_reference` ~1977) — never silent.
- Design the degraded fallback as a *no-content* `raise nodes.SkipNode` in `visit_*` wherever possible (skip cleanly before any output/state is touched), rather than opening a construct in `visit_*` and trying to close it safely in `depart_*` after something went wrong — the safest degradation opens nothing.
- If a placeholder string is emitted at all, emit it through the *same* code path (code-mode `text("...")` call) as ordinary text at that position, never a bespoke ad-hoc string that hasn't been checked against the current mode (Pitfall 2).
- Cover the degraded path with the same real-compile acceptance gate (Pitfall 9) as any other handler — "doesn't crash the translator" is not the same as "the compile still succeeds."

**Warning signs:**
- A new `visit_graphviz`/`visit_inheritance_diagram` with a `try/except Exception: pass` body and no logger call.
- A degradation path with no dedicated test asserting the surrounding document still compiles when the degraded node is present.

**Phase to address:** The graceful-degradation phase for graphical/out-of-scope nodes (explicit v0.6.0 target).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| Using `node.astext()` instead of buffer-swapping through the real visit chain | Fast to write, works for plain-ASCII-word test fixtures | Silently drops inline markup, bypasses both escaping regimes (Pitfall 3, 7) | Never for new content-emitting handlers in this milestone |
| String-only unit assertions (`"X" in output`) as the only test for a new handler | Fast, no `typst`/`pypdf` dependency needed | Cannot detect literal-source leaks or syntax errors — proven false-negative by the admonition bug | Acceptable only as a *supplement* to a real-compile gate, never standalone |
| Bare `except Exception: pass` for graceful degradation | Quick to add, unblocks the immediate crash | Silent content loss with no diagnostic trail; masks the next real bug (CONCERNS.md already flags this pattern project-wide) | Never — always pair with `logger.warning` |
| Passing docutils length strings straight through without unit normalization | Zero code for the "already looks numeric" case | Fatal compile break on the very first `px`/`pc`/bare-unitless value in a large corpus | Never — always route through one shared length helper |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|-------------------|
| docutils `image`/`figure` `:width:`/`:height:` options | Assume the string is already Typst-safe because docutils "validated" it | Route through a dedicated CSS-length→Typst-length normalizer (Pitfall 5) before interpolation |
| docutils `footnote`/`footnote_reference` split-node model | Port 1:1 as two independent visitors | Resolve the reference→body relationship explicitly and emit a single inline `footnote[...]` per reference (Pitfall 6) |
| `typst-py` (`pdf.py`) compile call | Treat a `TypstCompilationError` on one node as a scoped/local failure | Treat it as fatal for the entire document/build — design every handler assuming zero tolerance (Pitfall 1) |
| gentle-clues / mitex / codly `@preview` packages | Bump one version without checking the other two sync points | `writer.py` / `template_engine.py` / `templates/base.typ` must stay in lockstep — guarded by `test_preview_version_sync.py`, but a *new* sync point (e.g. a new package for graphviz rendering) needs the same guard added explicitly |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Full always-rebuild strategy (`get_outdated_docs()` returns everything) combined with a large corpus | Every debug iteration on a single-node fix recompiles all of Sphinx's `doc/` tree | Out of scope for this milestone per PROJECT.md, but worth budgeting extra CI/dev-loop time for the "compile Sphinx's own docs" acceptance phase specifically | Noticeable once the corpus reaches Sphinx's own doc-tree scale (hundreds of files) — exactly this milestone's target |
| Accumulating `self.body` as a single in-memory list for the whole master document | Memory grows linearly with document size; not a blocker at Sphinx-doc scale but worth knowing | No action needed this milestone; flagged as a pre-existing scaling limit in CONCERNS.md | 10k+ page documents (well beyond this milestone's target) |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Interpolating raw caption/title/label text into a markup `[...]` block without escaping markup-special characters | Any Sphinx author's prose can accidentally (or, in a shared-doc-source setting, deliberately) inject Typst markup/behavior via ordinary-looking text (`_`, `*`, `#`, `[`) that reaches an unescaped interpolation site | Never skip markup escaping for any interpolation into a `[...]` content block; treat this as an injection class of bug, not just a cosmetic one (Pitfall 7) |
| Emitting `link(refuri, ...)` for external URLs without any scheme/format check | Malformed or unexpected schemes in `refuri` reaching `typst.compile()` unfiltered — low severity here since Typst itself will reject genuinely malformed links, but still worth a defensive check given this is user/author-controlled content flowing into a compiler | Keep the existing empty-URL guard (Pitfall 8) and consider it the template for any additional URL-shape validation added alongside the empty-URL REQ work |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-------------------|
| Silent degradation with no warning (Pitfall 10) | Author writes a `.. graphviz::` diagram, gets a PDF with no error but also no diagram and no indication anything was skipped — discovered only by manual proofreading of a 900-page PDF | Always log a `logger.warning` naming the doc/node so it's visible in `sphinx-build` output, matching the existing empty-URL warning precedent |
| A single obscure node deep in a 900-page corpus aborts the *entire* build with a raw `TypstCompilationError` traceback | Author gets no indication of *which* Sphinx source file/line caused it — Typst's own error message references `.typ` line numbers, not the original `.rst` | Not literally a v0.6.0 REQ, but worth threading the source docname through to the warning/error path wherever a new degradation or fallback is added, so failures are diagnosable at real-corpus scale |

## "Looks Done But Isn't" Checklist

- [ ] **Figure/image width fix:** Often missing the `px`/`pc`/unitless/`ex` cases — verify with fixtures covering all of `%`, `em`, `px`, `pc`, `in`, `cm`, `mm`, and a bare unitless number, each proven via real compile (not just the `%` case from the bug report)
- [ ] **Figure caption fix:** Often missing the escaping half of the fix — verify a caption containing `_`, `*`, `` ` ``, `[`, `]` compiles and renders those characters literally, not as markup
- [ ] **Footnote support:** Often missing the "referenced twice" case and the "footnote appears at the correct page position, not just at the document's original docutils tree position" case — verify with a fixture that references the same footnote from two places
- [ ] **Empty-URL cross-reference handling:** Often only the plain `reference` node path is guarded — verify every new/other reference-emitting path added this milestone (autodoc `desc_*` cross-refs, etc.) independently rejects empty URLs
- [ ] **Graceful degradation (graphviz/inheritance_diagram):** Often missing the `logger.warning` half of "warn without aborting" — verify the build log, not just the exit code, shows the skip
- [ ] **versionmodified/desc_returns/desc_optional/desc_inline/transition/topic/line_block:** Often tested only with string-level asserts — verify each has at least one real-compile (`typst.compile()`) test, not just a translator-output unit test

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|-----------------|
| Figure-caption double emission (Pitfall 3) reaches a released version | LOW | Same fix pattern as the admonition-title fix (buffer-swap in `visit_caption`/`depart_caption`); small, isolated, well-precedented change |
| px→pt unit bug ships and breaks a downstream user's build | LOW–MEDIUM | Single shared length-normalization helper; retrofit is mechanical once written, but requires a version bump / changelog entry since it changes rendered output size for existing `:width:` values |
| Footnote model chosen turns out wrong for the "referenced twice" case after ship | MEDIUM | Requires revisiting the buffering design (Pitfall 6) — cheaper to get the design review right before implementation than to patch after, since it affects how footnote content is threaded through the tree |
| A one-off `TypstCompilationError` slips through into the real-corpus acceptance phase at the very end of the milestone | HIGH (time) | This is exactly why Pitfall 1/9's per-phase real-compile gates exist — recovery cost balloons if the first real-compile check happens only at the final "compile Sphinx's own docs" phase instead of incrementally per node-handler phase |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| 1. One bad node aborts the whole compile | Standing bar for every phase; formalized by phase 1 (Issue #114 fix) standing up the real-corpus compile gate | Every phase's plan includes a real `typst.compile()` step, not just unit tests |
| 2. Markup/code-mode mismatch | Every content-emitting handler phase | Docstring states which mode the handler assumes; reviewed against the buffer-swap precedent |
| 3. Figure-caption leak | Issue #114 figure/image fix phase | `test_pdf_render_gate.py`-style fixture with a captioned, `:target:`-linked figure; asserts no leaked `text(` substring near the caption |
| 4. Function-call juxtaposition | Issue #114 fix phase (link+image+caption) and the autodoc `desc_*` phase | Compile-gate fixtures for both a linked figure and a signature with a new `desc_returns`/`desc_optional` sibling |
| 5. px→pt unit conversion | Issue #114 fix phase | Fixtures for `%`, `em`, `px`, `pc`, `in`, `cm`, `mm`, unitless — each compiles and yields the expected rendered size |
| 6. Footnote modeling | Footnote/footnote_reference phase | Fixture with a single footnote referenced twice; compiles and both references show a marker |
| 7. Escaping regimes | Figure/caption phase + standing review for every new interpolation site | Fixtures include markup-special characters (`_`, `*`, `` ` ``, `[`, `]`) in captions/titles/version strings |
| 8. Empty-URL `link("", ...)` trap | Empty-URL cross-reference handling phase | Every new reference-emitting code path has its own empty-URL-guard test |
| 9. String-agreement-only testing | Standing bar for every phase | Each phase ships or extends a `test_pdf_render_gate.py`-style real-compile fixture |
| 10. Graceful-degradation done wrong | Graphviz/inheritance_diagram degradation phase | Build-log assertion that a warning was logged; compile-gate fixture proves the surrounding document still compiles |

## Sources

- `typsphinx/translator.py` — direct read of `visit_image`/`depart_image` (~1501–1546), `visit_figure`/`depart_figure` (~1163–1199), `visit_caption`/`depart_caption` (~1201–1227), `visit_reference`/`depart_reference` (~1930–2036), `visit_title`/`depart_title` (~190–238), `_visit_admonition`/`_depart_admonition` (~2292–2345), `visit_desc_parameterlist`/`visit_desc_parameter`/`depart_desc_parameter` (~2577–2621), `visit_Text` (~443–473) — HIGH confidence (primary source)
- `.planning/PROJECT.md` — v0.5.0 admonition markup/code-mode bug precedent, `kai` break history, v0.6.0 milestone scope — HIGH confidence (primary source)
- `.planning/codebase/CONCERNS.md` — broad-exception-handling tech debt, translator state-management fragility — HIGH confidence (primary source)
- `tests/test_pdf_render_gate.py` — the existing D-04 real-compile acceptance-gate precedent (`sphinx-build → typst.compile() → pypdf` text-extraction with negative-control leak signatures) — HIGH confidence (primary source)
- [Length – Typst Documentation](https://typst.app/docs/reference/layout/length/) — confirms Typst's native length units are `pt`, `mm`, `cm`, `in`, `em` (no `px`) — HIGH confidence (official docs)
- [Add a `px` unit for length · Issue #6849 · typst/typst](https://github.com/typst/typst/issues/6849) — confirms `px` is not currently a Typst unit (open feature request) — HIGH confidence (official upstream repo)
- [Relative Length – Typst Documentation](https://typst.app/docs/reference/layout/relative/) and [Ratio Type – Typst Documentation](https://typst.app/docs/reference/layout/ratio/) — confirms bare `50%` is valid Typst syntax for `width:`/`height:` — HIGH confidence (official docs)
- [Footnote – Typst Documentation](https://typst.app/docs/reference/model/footnote/) — confirms Typst's inline `footnote[...]` auto-numbering/auto-placement model — HIGH confidence (official docs)
- [Syntax – Typst Documentation](https://typst.app/docs/reference/syntax/) and [Scripting – Typst Documentation](https://typst.app/docs/reference/scripting/) — confirms code-mode expressions require line-break/semicolon separation (juxtaposition is a parse error) — HIGH confidence (official docs)
- CSS px→pt conversion factor (96px/in ÷ 72pt/in = 0.75pt/px) — standard, well-established typographic constant — HIGH confidence (widely documented convention, e.g. W3C CSS length reference)
- Docutils `length_or_percentage_or_unitless` directive-option convention (accepts `%`, `em`, `ex`, `px`, `in`, `cm`, `mm`, `pt`, `pc`, or bare unitless) — MEDIUM confidence (standard, long-established docutils convention, consistent with the milestone's own problem statement, not independently re-verified against docutils 0.22 source in this pass)

---
*Pitfalls research for: typsphinx v0.6.0 real-world robustness (Sphinx→Typst node-handler development)*
*Researched: 2026-07-11*

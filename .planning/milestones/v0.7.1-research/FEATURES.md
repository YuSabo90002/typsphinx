# Feature Research: API Reference Rendering (v0.7.0)

**Domain:** Sphinx-generated API reference documentation, rendered to print-quality PDF
**Researched:** 2026-07-29
**Confidence:** HIGH — every claim below is grounded either in a live measurement of the design
authority PDF (`https://app.readthedocs.org/projects/sphinx/downloads/pdf/master/`, fetched
2026-07-29, 200/application-pdf/3,227,122 bytes/703 pages) or in the Sphinx LaTeX source that
*produced* that PDF, both cited inline. One area (citations) has **MEDIUM** confidence because
the authority PDF contains no live rendered citation — see §6's caveat.

## Method

The authority PDF was downloaded and inspected three ways, cross-checked against each other:

1. **`pdftotext -layout`** (whole-document text dump) to locate representative pages by content
   search (e.g. the exact prose of a `.. warning::` block, so the PDF page number is derived from
   the actual doc source, not guessed).
2. **`pdftotext -bbox`** (per-word PDF-point bounding boxes) on selected pages, to get *exact*
   indentation values in PDF points rather than eyeballing — this is what grounds every indent
   number below.
3. **`pdftoppm`** page rasterization, visually inspected, to confirm colour/box/icon treatment
   that text extraction cannot capture.
4. **The Sphinx LaTeX source that emits the PDF**, read directly from the installed `sphinx`
   package (identical to `sphinx-doc/sphinx/sphinx/texinputs/*.sty` and
   `sphinx-doc/sphinx/sphinx/writers/latex.py` on GitHub): `writers/latex.py` (Python macro
   emission — the *ground truth* for which LaTeX macro, i.e. which font, wraps each node type) and
   `texinputs/sphinxlatex{objects,admonitions,styletext,lists,shadowbox,indbibtoc}.sty` +
   `texinputs/sphinx.sty` + `texinputs/sphinxpackageboxes.sty` (the macro *definitions* — colours,
   box parameters). File:line citations below refer to this installed copy
   (`sphinx==9.1.1`, matching the PDF's `/Producer` metadata "Sphinx Documentation, Release 9.1.1").

All PDF-point values are relative to a 72pt (1in) left page margin and a 10pt body font (the
authority's `doc/conf.py` sets no `pointsize` key, so Sphinx's LaTeX default `10pt` applies —
confirmed by `doc/conf.py:90-107`, no `pointsize` entry).

---

## 1. Object signatures (`desc_signature` family)

### Findings

**Font/weight is per-node-type, not a blanket bold wrap.** Sphinx's LaTeX writer wraps each
signature sub-node in a *different* macro (`sphinx/writers/latex.py:918-1101`):

| Node | LaTeX macro | Resolves to | Typeface |
|---|---|---|---|
| `desc_addname` (module/class qualifier prefix, e.g. `sphinx.application.`) | `\sphinxcode{\sphinxupquote{…}}` (`:936`) | `\texttt{#1}` (`sphinxlatexstyletext.sty:13`) | regular-weight **monospace** |
| `desc_name` (the object's own name) | `\sphinxbfcode{\sphinxupquote{…}}` (`:928`) | `\textbf{\sphinxcode{#1}}` (`:14`) | **bold monospace** |
| `desc_annotation` (leading keyword: `class `, `exception `, `async `) | `\sphinxbfcode{\sphinxupquote{…}}` (`:1098`) | same as `desc_name` | **bold monospace — identical styling to the name.** LaTeX does not visually distinguish the keyword from the name by weight/colour; the only distinguishing factor is the literal text (`"class "` vs the identifier) |
| `desc_inline` (inline fragment, e.g. C++ `:cpp:expr:`) | `\sphinxcode{\sphinxupquote{…}}` (`:919`) | `\texttt{#1}` | regular-weight monospace |
| individual `desc_parameter` (a parameter inside the parens) | `\sphinxparam{#1}` (`:1050`) | `\emph{#1}` (`sphinxlatexstyletext.sty:25`) | **italic, PROPORTIONAL — not monospace.** This includes the parameter's type annotation, since the annotation's `desc_sig_*` children have no LaTeX visitor override and simply inherit the ambient `\emph` font |
| parens `(` `)` around the parameter list, `[` `]` for a type-parameter list | `\pysigarglistopen`/`close` → `\sphinxcode{(}`/`\sphinxcode{)}` (`sphinxlatexobjects.sty:127-128`) | monospace | regular monospace |
| parameter separator comma (single-line signature, the common case) | `\sphinxparamcomma` = literal `", "` (`sphinxlatexstyletext.sty:85`) | plain proportional text, **not monospace** | plain text |
| optional-parameter bracket group (e.g. `printf(fmt[, args[, more]])`) | `\sphinxoptional{#1}` = `\Large[`···`\Large]` (`:28-29`) | large proportional brackets, **not code-styled** | proportional, enlarged |
| return annotation arrow | `{ $\rightarrow$ … }` (`:949-953`) | math-mode right arrow | proportional; the return type itself is whatever ambient font its content carries (usually plain/hyperlinked text, not forced monospace) |

Visually confirmed on p.355 of the authority PDF (`Sphinx.application.Sphinx.connect` overload
listing — 21 stacked signatures, chosen because it shows wrapping, parameter styling, and
cross-reference colouring in one place): parameter names and their annotations (`event: Literal[…]`,
`callback: Callable[…]`, `priority: int = 500`) render in italic proportional type; cross-referenced
type names inside them (`Sphinx`, `Config`, `BuildEnvironment`, `int`, `str`, `None`) are additionally
tinted with the document's hyperlink colour; the object name (`Sphinx.connect`) is bold.

**No box, frame, or background tint on a signature.** `sphinxlatexobjects.sty`'s `fulllineitems`/
`\pysigline*` family (lines 59-278) is pure `list`-environment hanging-indent typesetting — there is
no `\fbox`, `\fcolorbox`, or `framed` call anywhere in the signature-rendering code (contrast with
admonitions, §4, which do use `framed`). **Table stake: a signature is plain text with font
distinctions, never a coloured/bordered block.**

**Wrapping and continuation indent.** A signature whose parameter list overflows the line wraps
inside a `\parbox` (`\py@sigparams`, `sphinxlatexobjects.sty:133-138`) positioned to start exactly
where the parameter list opens (right after the object name and, if present, the module prefix) —
so continuation lines align under the **first parameter**, not under the left margin and not under
the object name. Confirmed visually on p.355: every wrapped `Sphinx.connect(…)` overload's second
line (e.g. `500) → int`) starts at the same x-position as `event:` on the line above, not at the
line's own left margin.

**Sibling signatures sharing one description** (overloads, alias groups, multi-option directives)
stack with `\smallskipamount` between them (`\sphinxsignaturesep`, `sphinxlatexobjects.sty:93-94`,
default `\smallskipamount` ≈ 3pt plus stretch/shrink) and NO extra indent relative to each other —
this already matches typsphinx's existing `FID-03` `linebreak()`-between-siblings behaviour
(`translator.py:4664-4682`); **no further work needed here.**

### Table

| Feature | Classification | Complexity | Notes |
|---|---|---|---|
| `desc_name` in bold monospace | Table stakes | Low | Currently `strong()` (proportional bold) — needs `raw()`/monospace wrap, weight `bold` |
| `desc_addname` in regular monospace | Table stakes | Low | Currently `pass` (no styling at all) |
| `desc_annotation` keyword in bold monospace, identical weight/font to `desc_name` | Table stakes | Low | Currently `pass`; do **not** italicize or differently-colour it — the authority treats it identically to the name |
| Parameter names + inline type annotations in italic proportional (not monospace) | Table stakes | Medium | Requires distinguishing `desc_parameter`'s font from `desc_name`'s — currently `desc_parameterlist`/`desc_parameter` emit plain `text()`, no italics |
| Parens/brackets around parameter list in monospace | Table stakes | Low | Currently plain `text("(")`/`text(")")` — already visually plausible since default body font may already look proportional; needs explicit `raw()` wrap to be correct |
| Return arrow rendered distinctly (e.g. `→`), return type not force-monospaced | Table stakes | Low | `desc_returns` already emits `" -> "` (translator.py:4724-4741); swap ASCII arrow for a real arrow glyph or Typst symbol, verify return-type child isn't wrapped in `raw()` |
| Hanging continuation indent aligned to first parameter on signature wrap | Differentiator | Medium-High | Typst doesn't have LaTeX's `\parbox`-at-arbitrary-width primitive as directly; achievable via a fixed/measured `#h()` offset or a Typst `block`/`grid` with a computed first-line hang. Genuinely improves long `Callable[[...], ...]`-style signatures, which are common in the corpus (p.355 has 21 of them) |
| No box/frame/background tint on signatures | Anti-feature guard (verify, don't add) | — | Nothing to build — the risk is *adding* a code-block-style background (à la `codly`) to "make signatures pop," which the authority explicitly does not do. Flag as a thing NOT to add |
| Per-token syntax highlighting of signature internals (colouring `desc_sig_operator`/`desc_sig_keyword` differently) | Anti-feature | — | The authority's LaTeX writer has **no visitor overrides at all** for the `desc_sig_*` family (verified: zero hits for `visit_desc_sig_` in `writers/latex.py`) — every fragment inside a parameter inherits the same italic. Adding Pygments-style token colouring would be a deviation from the design authority, not a match to it, and risks looking gaudy/inconsistent with the rest of the greyscale-safe document. Out of scope for "faithful" |

---

## 2. Description body indentation (`desc_content`, cumulative nesting)

### Findings

Measured with `pdftotext -bbox` on p.164 of the authority PDF (`class sphinx.builders.Builder`,
chosen because its class body genuinely nests attribute and method members via `autoclass`-style
member listing, unlike some hand-authored pages in the same corpus that flatten members to
top-level `.. method::` directives at the same margin as the class — see caveat below):

| Element | x-position (pt from page edge) | Indent from page margin (72.0pt) | What it is |
|---|---|---|---|
| `class sphinx.builders.Builder` (top-level signature) | 72.0 | 0 | signature margin |
| `This is the base class for all builders.` (class's own `desc_content` prose) | 96.9 | **+24.9pt** (≈2.5em @10pt) | level-1 indent |
| `Overridable Attributes` (a rubric, nested inside the class body) | 96.9 | +24.9pt | same level as body prose — rubric does **not** get its own indent rule, it inherits whatever context it's in |
| `name:    ClassVar[str] = ''` (a nested attribute's own signature) | 96.9 | +24.9pt | **same indent as the class's body text** — a nested member's signature aligns with the parent's `desc_content` margin, it is not pushed a further level right |
| `The builder's name. This is the value…` (that attribute's own description body) | 118.8 | +46.8pt total, **+21.9pt beyond its own signature** | level-2 indent — confirms the indent is genuinely **cumulative**: attribute body = class body indent + one more increment |
| `Core Methods` (rubric between attribute list and method list) | 96.9 | +24.9pt | same as level 1 — again, rubric follows structural nesting, no special-case |
| `final build_all() → None` (nested method signature) | 96.9 | +24.9pt | level 1, same as any other nested member signature |
| `Build all source files.` (that method's description) | 118.8 | +46.8pt | level 2 |

A second, independent measurement (p.354, `Sphinx.require_sphinx`'s `Parameters` field) gives an
almost identical step size: field body text starts at **+21.9pt** beyond the field-list block,
which itself starts +21.9pt beyond plain body text (see §3). **The recurring indent quantum across
every measured nesting context is ≈22–25pt (≈2.2–2.5em at the document's 10pt body size)** — one
consistent unit reused for object-description nesting, field-list indent, and (by LaTeX's `quote`
mechanics) any other block quote. This is a strong, reusable finding: pick one indent constant and
apply it uniformly rather than inventing different magic numbers per node type.

**Caveat on "cumulative for nested objects":** Sphinx's own `doc/` corpus mixes two authoring
styles — some pages (e.g. `sphinx.application.Sphinx`) list every method as a **sibling**
`.. method::` directive at the module/class's own top level (not nested inside the class's
`desc_content` in the doctree), so those pages show methods flush with the class signature, not
indented under it. This is an authoring-style artifact of Sphinx's own docs, not a rule about how
nesting *should* render — the `sphinx.builders.Builder` page (genuine `autoclass`-style nesting)
is the correct reference for how a *truly nested* `desc` renders, and it unambiguously shows one
indent level per nesting depth, cumulative.

### Table

| Feature | Classification | Complexity | Notes |
|---|---|---|---|
| `desc_content` indented one step relative to its `desc_signature` | Table stakes | Medium | Currently both `visit_desc_content`/`depart_desc_content` are `pass` (translator.py:4767-4775) — zero indent today, this is defect (2) named in PROJECT.md. A single constant (e.g. Typst `pad(left: X)` or list/indent construct) applied per nesting depth |
| Indentation genuinely cumulative across nesting depth (method-inside-class = 2 indent steps from page margin) | Table stakes | Medium | Currently a nested `py:method::`/`py:attribute::` renders at the same margin as a top-level `py:function::` — defect (3) in PROJECT.md. Requires the translator to track/emit a nesting-depth counter, since Typst has no LaTeX-style automatic `\@totalleftmargin` accumulation from an enclosing list context |
| Rubric/subheading text nested inside a class body indents WITH the body, not flush to the page margin | Table stakes | Low-Medium | Follows directly from making `desc_content` indent structural (rubric is just another child of `desc_content`) rather than special-cased |
| One shared indent constant (~2.2–2.5em) reused for all indent contexts (desc nesting, field lists, block quotes) | Differentiator | Low | Cheap once the base primitive exists — a single named constant in the new style module keeps everything visually consistent and is much easier to tune later than N independent magic numbers |
| Indenting BOTH the signature line and its body by the same amount (rather than only the body) | Anti-feature | — | The authority never indents a nested member's own *signature* beyond its parent's body margin — only the member's *description* gets the extra step. Indenting the nested signature itself as far as its description would over-indent and doesn't match any measured case |

---

## 3. Info fields (`field_list`: Parameters, Returns, Return type, Raises, Variables, Keyword Arguments)

### Findings

**Structural container: a `description` list wrapped in `quote`.** `sphinx/writers/latex.py:1541-1557`:

```python
def visit_field_list(self, node): self.body.append(r'\begin{quote}\begin{description}')
def depart_field_list(self, node): self.body.append(r'\end{description}\end{quote}')
visit_field_name = visit_term      # -> \sphinxlineitem{...}, a bold run-in label
visit_field_body = visit_definition
```

So each field ("Parameters", "Returns", "Return type", …) is a `description`-list **run-in bold
label followed by prose** (`\sphinxlineitem`, `sphinxlatexlists.sty:19-42` — the label is
typeset, then the body text flows on the same line if it fits, wrapping with a hanging indent
under the label's width if it doesn't). This is **not** a two-column table and **not** a plain
definition list without the run-in behaviour — it specifically collapses onto one line when short.

Measured (p.354, `Sphinx.require_sphinx`'s `Parameters` field): the field list sits **+21.9pt**
right of plain `desc_content` body text (the `quote` wrapper's own indent — the same ≈22pt unit
from §2), and the field body's own wrapped continuation is a further **+18.7pt** past the field
name (the width of the "Parameters" label + label separator).

**Multi-parameter rendering is genuinely bulleted, not run together.** The grouping logic lives in
docutils-independent Sphinx code (`sphinx/util/docfields.py`), so it applies identically regardless
of output format:

- `GroupedField`/`TypedField.list_type = nodes.bullet_list` (`docfields.py:201`) — when a field
  (e.g. "Parameters") has **more than one** entry, Sphinx wraps them in a `bullet_list`, one
  `list_item` per parameter (`docfields.py:335-337`).
- When a field has **exactly one** entry and the field type allows collapsing (`can_collapse=True`,
  true for `Parameters`), Sphinx instead emits a single inline paragraph with no bullet at all
  (`docfields.py:331-333`) — this already matches typsphinx's existing `_last_field_body_was_inline`
  collapsed-inline-form logic (`translator.py:4989-5008`), so **no new work needed for the
  collapse rule itself**, only for the surrounding font treatment.

**Exact `name (type) – description` construction**, from `TypedField.make_field.handle_item`
(`docfields.py:295-328`), is domain-independent doctree structure — the SAME structure a typsphinx
translator sees regardless of output format:

1. Parameter name → wrapped in `addnodes.literal_strong` → LaTeX: `\sphinxstyleliteralstrong{\sphinxupquote{…}}` = `\sphinxbfcode{…}` (`sphinxlatexstyletext.sty:50`) = **bold monospace**.
2. If a type was given: literal `" ("` + type name (wrapped in `addnodes.literal_emphasis` →
   `\sphinxstyleliteralemphasis{…}` = `\emph{\sphinxcode{…}}` (`:48`) = **italic monospace**) + literal `")"`.
3. If description content exists: literal `" -- "` (renders as an en-dash in LaTeX's ligature
   handling) + the description prose.

So inside a "Parameters" field, per parameter: **name = bold monospace, type = italic monospace,
description = plain prose**, separated by literal `" ("`/`") "`/`" -- "` — a **different** font
recipe from a signature's own parameter list (§1's `\sphinxparam` = italic *proportional*, not
monospace). This distinction (proportional-italic in the signature vs. monospace-bold/italic in
the field-list echo of the same parameter) is a genuinely surprising, precise finding worth
preserving faithfully.

### Table

| Feature | Classification | Complexity | Notes |
|---|---|---|---|
| Field name (`Parameters`, `Returns`, …) as a bold run-in label | Table stakes | Low | Already implemented (`translator.py:4960-4982`, `strong()` + `": "`) — largely correct, keep |
| Field list indented one step (≈22pt/2.2em) beyond the surrounding description body | Table stakes | Medium | Not currently indented at all — field lists render flush with `desc_content`'s (also currently zero) indent |
| Multi-value field body rendered as a bulleted list | Table stakes | Low | Field-body construction already produces a real `bullet_list` node in the doctree (docutils-level, domain-independent) — typsphinx's existing `visit_bullet_list` should already handle it once it's reached; verify no special-casing suppresses the bullet inside a field body |
| Single-value field body collapses to inline prose, no bullet | Table stakes | Already done | `_last_field_body_was_inline` (translator.py:4989 area) already implements this — no new work |
| Parameter name bold monospace, type italic monospace, `" (" ")" " -- "` separators, inside a field body | Table stakes | Medium | Requires distinguishing `literal_strong`/`literal_emphasis`-equivalent doctree nodes and giving them monospace treatment distinct from the plain-bold field name label |
| Reusing the *same* italic-proportional treatment as signature parameters (§1) for field-list parameter echoes | Anti-feature | — | Authority deliberately uses a **different** recipe (monospace bold/italic) in the field list vs. the signature (proportional italic) — collapsing these to one style would be unfaithful, not simpler |
| A literal two-column/grid table for Parameters | Anti-feature | — | Never what the authority does — it's a `description` list, not a table. A grid table also breaks awkwardly across pages compared to a flowing description list |

---

## 4. Admonitions (note, warning, tip, caution, danger, error, hint, important, attention, seealso, generic `.. admonition::`)

### Findings

**Structural family: `sphinxheavybox`, a `framed`-based coloured box with a distinct title row**
(`sphinxlatexadmonitions.sty:115-190` for the box, `:320-367` for the title row `\sphinxdotitlerow`).
Visually confirmed on p.213 of the authority PDF (a `.. warning::` block, deliberately chosen
because it sits on a page with *no* chapter-specific style override, unlike the `.. note::` on
p.439 which lives inside a demonstration chapter that intentionally re-themes its own admonitions
— see the explicit caveat below): sharp-cornered box, thin solid border in the type's colour,
title row with a **tinted background band + icon + bold title text (no trailing colon)**, body
region with a neutral near-white background, **no drop shadow**.

**Colour buckets (4 groups, from `sphinx.sty:280-284,819-869`), not 10 independent colours:**

| Bucket | Border colour | Title bg / fg | Members |
|---|---|---|---|
| "note" (blue) | `#86989B` (generic `admonition-bordercolor`) | bg `#D0DEFA` / fg `#145DEA` | `note`, and the **generic** `.. admonition::` (which the LaTeX writer hardcodes to type `"note"` — `writers/latex.py:1790-1791`) |
| "success" (green) | `#86989B` | bg `#DCEFE6` / fg `#51AE80` | `hint`, `tip`, `seealso` |
| "warning" (orange) | `#940000` (`warning-bordercolor`) | bg `#F8E4D2` / fg `#DD7A21` | `important`, `caution`, `warning` |
| "error" (red) | `#B40000` (`error-bordercolor`) for `error`, `#940000` for the others | bg `#EEDCDC` / fg `#AE5050` | `attention`, `danger`, `error` |
| "todo" (purple, `sphinx.ext.todo`-only) | `#86989B` | bg `#E2CCFE` / fg `#7100FF` | `todo` |

Body background for every type is the same near-white `#F7F7F7` (`sphinx.sty:281`) — the
distinguishing signal is the **title row's** background + the border colour + the icon, not the
body fill.

**Current typsphinx mapping has two concrete bucket mismatches** (translator.py:4170-4305), fixable
inside the existing gentle-clues vocabulary (`info`/`warning`/`tip`/`danger`/`error`/`task`/`clue`
— no new package, per the milestone invariant):

- `seealso` → currently `info` (blue "note" bucket). **Authority buckets `seealso` with
  `hint`/`tip` (green "success" bucket)** — should map to `tip`, not `info`.
- `attention` → currently `warning` (orange bucket). **Authority buckets `attention` with
  `danger`/`error` (red "error" bucket)** — should map to `danger`, not `warning`.
- generic `.. admonition::` → currently `clue` (unstyled — no icon, no colour). **Authority
  renders it identically to `note`** (blue, icon, coloured title row), just with the directive's
  own custom title text substituted for "Note" — should map to `info` with the dynamic title
  (which the translator already threads through via `_pending_admonition_title`), not the
  unstyled base `clue`.

Everything else already lines up correctly: `note`→blue, `hint`/`tip`→green (already both map to
`tip`), `important`/`caution`/`warning`→orange (already all map to `warning`), `danger`/`error`
→red (already correct).

**Greyscale-print anti-feature risk:** the 4 title-bucket colours are close in *luminance* to each
other when desaturated (a light blue, light green, light peach, and light red-pink title band are
all pastel, mid-high-luminance tints) — in true black-and-white printing the title bands become
visually similar shades of light grey, and only the **border colour** (2 distinct greys: `#86989B`
generic vs. `#940000`/`#B40000` for warning-class) and the **icon shape** remain reliably
distinguishing. This means: relying on background hue *alone* to tell `note` from `hint` from
`seealso` is unsafe for greyscale output — the icon and border-colour/weight differences (and, for
gentle-clues, whatever icon glyphs it ships) are what actually carry the distinction in monochrome,
so they must not be dropped even if colour rendering is otherwise deprioritized.

### Table

| Feature | Classification | Complexity | Notes |
|---|---|---|---|
| Distinct colour/icon per admonition **bucket** (4 groups, not 10 independent styles) | Table stakes | Already mostly done | gentle-clues already provides distinct colours/icons per clue kind — this is about *which* kind each docutils node maps to, not building new visual treatment |
| `seealso` → same bucket as `hint`/`tip` (green), not `note` (blue) | Table stakes (fix) | Low | One-line change: `visit_seealso` from `self._visit_admonition(node, "info", ...)` to `"tip"` |
| `attention` → same bucket as `danger`/`error` (red), not `warning`/`caution` (orange) | Table stakes (fix) | Low | One-line change: `visit_attention` from `"warning"` to `"danger"` |
| Generic `.. admonition::` styled like `note` (blue, icon, coloured title) with the directive's own custom title, not unstyled | Table stakes (fix) | Low | One-line change: `visit_admonition` from `"clue"` to `"info"` — the dynamic-title plumbing already exists |
| Body background near-white/neutral (same across all types) | Already correct / verify | Low | Confirm gentle-clues' body fill doesn't vary loudly by type; the authority's distinguishing signal is the title row, not the body |
| Icon or shape distinct enough to survive greyscale, independent of colour | Table stakes | N/A (dependency-bound) | Depends on whatever icon set gentle-clues ships — verify it isn't colour-only |
| Title row with tinted background band distinct from box body | Table stakes | Already done | gentle-clues boxes already do this structurally per the "Existing features" note in the milestone context |
| Adding a drop shadow to admonition boxes | Anti-feature | — | The authority's admonitions (`sphinxheavybox`) have **no shadow** — only `topic`/`contents`/`sidebar` boxes do (§5). Adding one to note/warning would blur the visual grammar that currently separates "aside" boxes from "structural" boxes |
| Rounded corners on admonitions (as seen in the p.439 demo chapter) | Anti-feature (context-dependent) | — | That page is a **user-customized** demonstration of `sphinxsetup`, not the default. The default (p.213) is sharp-cornered. Don't take the demo chapter as the baseline |

---

## 5. `rubric`, `topic`, `.. contents::` (local TOC), and `seealso` shape

### Findings

**`rubric` is NOT a distinct visual style at all — it's whatever context it's in, bold, no box.**
LaTeX doesn't even have a dedicated `visit_rubric` in `writers/latex.py` beyond routing it through
the same paragraph/heading-adjacent machinery used for other inline-styled block text (confirmed:
`Overridable Attributes` and `Core Methods` on p.164 — both `.. rubric::`-shaped subheadings inside
a class body — render at exactly the class body's own indent level, §2's level-1 indent, in a bold
weight, with no box, no rule, no colour). A rubric is structurally "a bold line that participates
in whatever indent context surrounds it," which is materially different from a real section
`title` (which resets to the page margin and gets numbering/TOC participation) and from an
admonition (no box).

**`topic` and `.. contents::` (local TOC) are BOTH boxed** — this is a genuine, concrete divergence
from typsphinx's current behaviour. `writers/latex.py:671-682`:

```python
def visit_topic(self, node):
    if 'contents' in node.get('classes', []):
        self.body.append(r'\begin{sphinxcontents}')   # boxed
    else:
        self.body.append(r'\begin{sphinxtopic}')       # boxed
```

Both `sphinxtopic` and `sphinxcontents` are `sphinxShadowBox` instances (`sphinxlatexshadowbox.sty:
152-155`) sharing the exact same box machinery as admonitions (`\spx@boxes@fcolorbox`,
`\sphinxdotitlerow` title row) **plus a drop shadow by default** (`sphinx.sty` sets
`div.topic_box-shadow-TeXcolor`/`div.contents_box-shadow-TeXcolor` unconditionally,
`:797-808`) — this is the one visual family in the whole authority document that *does* get a
shadow, distinguishing "structural aside" boxes (topic/contents/sidebar) from "note-style" boxes
(admonitions, no shadow). Default border/background colours for both are the same generic
`admonition-bordercolor`/`admonition-bgcolor` as the blue/grey "note" bucket, with title-row colours
matching the "note" bucket too (`sphinx.sty:863-869`).

typsphinx currently implements `.. topic::` as a boxed `clue`, matching this — **but implements
`.. contents::` (detected via the `contents` class) as box-less pass-through** (`translator.py:
4307-4335`, comment "D-05: box-less"). Per the authority, this is a divergence: a local TOC should
get the *same* boxed treatment as a `.. topic::`, not be rendered as a bare bold label + bullet
list.

**`seealso` is structurally its own admonition type** (`sphinxseealso` environment,
`sphinxlatexadmonitions.sty:264-270`) in the green "success" colour bucket (§4) — not a special
non-boxed shape. typsphinx already renders it as a boxed clue (currently in the wrong colour
bucket, per §4's fix list); no structural change needed here beyond the colour fix already noted.

### Table

| Feature | Classification | Complexity | Notes |
|---|---|---|---|
| `rubric` renders as bold text with no box, at whatever indent its container is at | Table stakes | Low-Medium | Currently `strong()` + unconditional `linebreak()` (translator.py:5034-5076) — already roughly right in spirit (bold, no box); the outstanding gap is that it doesn't yet participate in §2's cumulative indent because nothing does yet |
| `rubric` visually distinct from a real section heading (no numbering, no larger size jump, no page-break/TOC entry) | Table stakes | Already correct | Nothing in the current implementation gives rubric heading-like behaviour beyond bold — keep it that way |
| `.. topic::` renders as a boxed, titled aside (shares admonition box family) | Table stakes | Already done | `translator.py:4291-4328` already reuses the admonition helper for `topic` |
| `.. contents::` (local TOC) renders in the SAME boxed style as `.. topic::`, not box-less | Table stakes (fix, diverges from current) | Medium | Current `_topic_is_contents` branch explicitly skips the box (D-05). This research finds the authority does NOT skip it — flag for requirements-definition to decide whether to align or keep the deliberate divergence (may have been a considered UX choice; worth revisiting given this new evidence) |
| Drop shadow on `topic`/`contents` boxes, but NOT on note/warning/etc. admonitions | Differentiator | Medium | A genuine, distinguishing visual signal in the authority that nothing in typsphinx currently implements (gentle-clues boxes have no shadow option verified either way) — moderate value, moderate cost, not required for basic fidelity |
| Giving `rubric` a box (treating it like a mini-admonition) | Anti-feature | — | The authority never boxes a rubric — it is pure inline-bold text. Boxing it would visually conflate two different Sphinx concepts (rubric = a bold aside-heading; topic = a boxed aside) that the authority keeps distinct |

---

## 6. Citations (`citation`, `label`, `citation_reference`)

### Findings — MEDIUM confidence (see caveat)

**Caveat:** Sphinx's own `doc/` corpus contains no functioning `.. [Label] text` citation +
`[Label]_` reference pair — grepped exhaustively (`grep -rEn '^\.\. \[[A-Za-z0-9_-]+\][ \t]'` and
`grep -rEn '\[[A-Za-z][A-Za-z0-9_-]*\]_'` across `doc/`) and found only two docutils **footnotes**
(numeric `.. [1]`, a different node type) and one citation-syntax example shown as prose text
inside `usage/restructuredtext/basics.rst` (documenting the syntax, not using it). **The design
authority PDF therefore has no live rendered citation to point at.** This section is grounded
entirely in the LaTeX source that *would* render one (`sphinxlatexindbibtoc.sty` and
`writers/latex.py:2131-2165`, both explicitly named as secondary references in the milestone
context) — i.e. it is authoritative about mechanism, not independently visually confirmed against
the live PDF the way §§1-5 are.

**Bibliography container = plain LaTeX `thebibliography`, no extra styling.**
`sphinxlatexindbibtoc.sty:33-37`: `sphinxthebibliography` is just `\cleardoublepage` +
`\begin{thebibliography}{#1}` — no colour, no box, no icon. It is deliberately the vanilla LaTeX
bibliography list, unlike admonitions/topics.

**Hanging-indent width is dynamically sized to the widest label, capped at 8 characters.**
`writers/latex.py:2131-2141`:

```python
citations = list of nodes.citation
labels = [c[0] for c in citations]           # the label node of each citation
longest_label = max(labels, key=len)
if len(longest_label) > MAX_CITATION_LABEL_LENGTH:  # = 8 (line 40)
    longest_label = longest_label[:MAX_CITATION_LABEL_LENGTH]
self.body.append(r'\begin{sphinxthebibliography}{%s}' % longest_label)
```

`thebibliography`'s mandatory argument sets `\labelwidth`/`\leftmargin` to the *typeset width of
that string* — i.e. the entire list's hanging indent is computed from whichever citation label in
the document is longest (capped at 8 characters to avoid a pathologically wide margin from one
long custom label). **This is a concrete, implementable rule**: don't hardcode a fixed hanging
indent — measure (or approximate from) the widest label actually present, capped at a sane
character count.

**Per-entry label**: `\bibitem[Label]{docname:id}` (`writers/latex.py:2146-2151`) — plain LaTeX
`\bibitem[…]` bracket-label mechanics. Standard LaTeX `thebibliography` does **not** bold the
bracketed label (unlike `description`'s `\item[term]`, which does bold via `\bfseries`) — it is
plain body-weight text in brackets, e.g. `[Ref]`.

**Ordering: doctree/source order, not sorted.** `visit_thebibliography` iterates `node` (the
citation nodes in document order) with no `sorted()`/comparator call anywhere in the function —
citations render in the order the `.. [Label]` directives appear in the source document, matching
plain LaTeX `thebibliography` behaviour (which is always emission order of `\bibitem` calls, never
auto-sorted).

**No automatic "Bibliography" heading.** Nothing in `visit_thebibliography`/`sphinxthebibliography`
inserts a section title — the heading text ("Bibliography", "References", …) is ordinary author
content (a regular `.. rubric::` or section heading placed before the citation list in the source),
handled by typsphinx's existing title/rubric/section visitors, not a special citation-specific
concern.

**In-text citation reference**: `\sphinxcite{docname:refname}` = `\cite{...}` (`writers/latex.py:
2156-2161`, `sphinxlatexindbibtoc.sty:66`) — a plain LaTeX `\cite`, which with `hyperref` (which
Sphinx's LaTeX build always loads) renders as a **bracketed, hyperlinked label** (e.g. `[Ref]`,
clickable, jumping to the matching `\bibitem` anchor) in the body's normal (non-bold, non-italic)
weight.

### Table

| Feature | Classification | Complexity | Notes |
|---|---|---|---|
| `[Label]` bracket format for both the bibliography entry and the in-text reference | Table stakes | Low | Both use the same literal bracket-label text — no divergence between definition-site and reference-site formatting |
| Bracketed label NOT bold (plain body weight) | Table stakes | Low | Easy to get wrong by reflexively bolding it the way `field_name`/list terms are bolded elsewhere — the authority specifically does not |
| Hanging indent for wrapped multi-line entries, sized to (approximately) the widest label present | Table stakes | Medium | Requires either measuring label widths at build time or picking one reasonable fixed value (e.g. based on typical `[Author2020]`-style label length) — Typst has no direct equivalent of LaTeX's dynamic `\settowidth`-driven `thebibliography{arg}`, so an approximation is acceptable |
| Entries ordered by document/declaration order, never alphabetically sorted | Table stakes | Low | Simple to satisfy — just iterate citations in doctree order, don't add a sort step |
| In-text citation reference is a clickable link to its bibliography entry | Table stakes | Medium | Depends on typsphinx's existing anchor/label-link infrastructure (`_sanitize_label`, same-document `link(<id>, ...)` pattern already used for `desc_signature` ids, footnotes, and general cross-references) — should reuse that machinery rather than build new |
| No box/background/icon around the bibliography list | Table stakes | Low | Plain list, not an admonition-family box — resist the temptation to make citations "look nicer" with a boxed treatment; that would diverge from the authority |
| No auto-generated "Bibliography"/"References" heading | Table stakes (verify, don't build) | — | The heading is ordinary author-authored section content; typsphinx's existing section/title handling already covers it — nothing citation-specific to add here |
| Alphabetical or author-name sorting of the bibliography | Anti-feature | — | Would diverge from both plain LaTeX and Sphinx's own citation ordering (doctree/declaration order) — looks like an improvement but isn't faithful, and complicates the implementation for no benefit the authority itself doesn't provide |
| Numbered citation style (`[1]`, `[2]`, …) as the ONLY supported form | Anti-feature (scope risk) | — | reST citations use author-chosen labels (`[Ref]`, `[Knuth1998]`, …), not auto-numbers — auto-numbering is a *footnote* concern (already implemented), not a citation one; conflating the two would break the labels docutils actually assigns |

---

## Feature Dependencies

```
Style module (new importable Typst module, bundled + copied like _template.typ)
    └──required-by──> ALL of §1 (signature fonts), §2 (indent), §3 (field-list fonts), §5 (rubric weight)
                       (a shared constant for "the ~22pt/2.2em indent unit," and shared raw()/bold
                        helpers for "bold monospace" / "italic monospace" / "italic proportional,"
                        belong in one place rather than being reinvented per node-visitor)

§2 (desc_content indent, cumulative)
    └──required-by──> the visual distinguishability that motivates this whole milestone
                       (PROJECT.md defect 3: "a nested py:method:: renders at the same left margin
                       as a top-level py:function::")

§2 (desc_content indent)
    └──shares-a-constant-with──> §3 (field_list's own extra +21.9pt step is the SAME unit, applied once more)

§4 (admonition colour-bucket fixes: seealso, attention, generic admonition)
    └──independent-of──> §1/§2/§3 (desc_* redesign) — these are three one-line reassignments
                          of an existing gentle-clues call, no shared infrastructure, can ship
                          in the same phase or a separate one with no ordering constraint

§5 (rubric)
    └──benefits-from──> §2's indent infrastructure (a rubric needs to sit at whatever indent
                         level its container has reached — it has no indent rule of its own)

§5 (.. contents:: boxed-vs-box-less decision)
    └──conflicts-with──> the current D-05 box-less choice — needs an explicit requirements-phase
                          decision (align with authority vs. keep the deliberate divergence),
                          not a default "just do what LaTeX does"

§6 (citations)
    └──requires──> the existing same-document anchor/link machinery (`_sanitize_label`,
                    `[#metadata(none) <id>]` anchors, `link(<id>, ...)` refs) already proven for
                    `desc_signature` ids and footnotes — reuse, don't reinvent
    └──independent-of──> §1-§5 (citations are a wholly separate node family; can be sequenced
                          in any order relative to the desc_*/admonition work)
```

### Dependency notes

- **The style module is the load-bearing prerequisite for §1/§2/§3/§5**, per the milestone's own
  target-features description ("Style consolidated into an importable Typst module"). Building the
  monospace/bold/italic/indent primitives once, in that module, before wiring them into each
  `visit_desc_*`/`visit_field_*`/`visit_rubric` handler avoids repeating the same font-selection
  logic six times.
- **§2 and §3 share one indent constant** (measured identically at ≈22pt/2.2em in two independent
  contexts — see §2's and §3's Findings) — implementing them with two different hardcoded values
  would be both wasteful and a fidelity risk if the values ever drift apart.
- **§4's three colour-bucket fixes are the cheapest, lowest-risk items in this entire research
  scope** — each is a one-argument change to an existing, already-correct call site
  (`_visit_admonition(node, "info"→"tip")`, etc.), with zero new infrastructure. They can land
  independently of the larger desc_*/indent work and would be a reasonable "quick win" item within
  the phase.
- **§5's `.. contents::` boxed-vs-box-less question is a genuine open decision**, not a bug fix —
  D-05 was presumably a deliberate choice at the time, and this research surfaces new evidence
  (the authority boxes it) that the requirements-definition step should weigh, not silently
  override.
- **§6 has no shared code with §1-§5** beyond the pre-existing anchor/link infrastructure — it can
  be planned, sequenced, and reviewed independently.

---

## Complexity & Cost Summary

**Cheap (small, mostly mechanical changes to existing call sites):**
- §4's three colour-bucket fixes (seealso, attention, generic admonition) — one-line each
- §1's `desc_addname`/`desc_name` monospace/bold wraps — analogous to existing `strong()` wrap, swap the primitive
- §3's field-name bold label — already correct, no change

**Medium (need new state/logic, but follow established patterns in the codebase):**
- §2's cumulative indent (needs a nesting-depth counter/stack — no such counter exists today for `desc`, though the codebase has precedent for similar depth-tracking, e.g. `_line_block_depth`)
- §3's field-list indent (reuses §2's constant, needs `visit_field_list`/`depart_field_list` to apply it)
- §3's monospace-bold/italic parameter-echo styling inside field bodies (needs to distinguish this from the plain-bold field-name label, and from §1's proportional-italic signature-parameter styling — two different "italic" and two different "bold" recipes coexisting)
- §1's signature-parameter italic-proportional styling (needs to NOT reuse whatever primitive §3 uses for its bold-monospace/italic-monospace)
- §6's citation round trip (new node family, but reuses proven anchor/link machinery)

**Medium-High (genuinely new capability, no close existing precedent):**
- §1's hanging continuation indent for wrapped long signatures (Typst has no direct `\parbox`-at-computed-width equivalent; needs either a measured/computed offset or an accepted approximation)
- §6's dynamic/approximated citation-label hanging-indent width

**Explicitly out of scope / do not build (anti-features):**
- Per-token signature syntax highlighting (§1)
- Boxing/framing signatures (§1)
- Drop shadows on admonitions (§4) — reserve shadow for topic/contents if that differentiator is picked up (§5)
- Rounded corners on default admonitions (§4) — that's a customized-chapter artifact, not the baseline
- Boxing rubrics (§5)
- Alphabetically sorting or auto-numbering the bibliography (§6)

---

## Sources

**Primary — live-measured design authority:**
- `https://app.readthedocs.org/projects/sphinx/downloads/pdf/master/` — fetched 2026-07-29,
  200/application-pdf/3,227,122 bytes/703 pages/pdflatex-1.40.22, "Sphinx Documentation, Release
  9.1.1"
  - p.164 (`class sphinx.builders.Builder`) — cumulative desc_content indent measurement
  - p.213 (`.. warning::` inside `usage/extensions/autodoc.rst`) — default (non-customized) admonition box appearance
  - p.354 (`Sphinx.require_sphinx`) — field-list indent + Parameters field measurement
  - p.355 (`Sphinx.connect` overload listing) — signature font/wrap/parameter styling, visually confirmed
  - p.439 (`.. note::` inside `latex.rst`, "LaTeX Customization" chapter) — explicitly identified and
    excluded as a **user-customized** admonition example (the chapter demonstrates `sphinxsetup`
    overrides on itself), not used as a default-styling source

**Primary — the LaTeX source that produces the authority PDF** (installed copy,
`sphinx==9.1.1`, identical to `sphinx-doc/sphinx` on GitHub at the matching tag):
- `sphinx/writers/latex.py` — the Python macro-emission ground truth for every node → LaTeX-macro mapping cited above (line numbers given per-claim in the body)
- `sphinx/texinputs/sphinxlatexobjects.sty` — `fulllineitems`, `\pysigline*` family, signature list mechanics
- `sphinx/texinputs/sphinxlatexadmonitions.sty` — `sphinxheavybox`, `\sphinxdotitlerow`, admonition dispatch
- `sphinx/texinputs/sphinxlatexstyletext.sty` — `\sphinxcode`/`\sphinxbfcode`/`\sphinxparam`/`\sphinxoptional`/`\sphinxstyleliteral{strong,emphasis}` definitions
- `sphinx/texinputs/sphinxlatexlists.sty` — `\sphinxlineitem` (field-list run-in label mechanics)
- `sphinx/texinputs/sphinxlatexshadowbox.sty` — `sphinxtopic`/`sphinxcontents`/`sphinxsidebar`, shadow-box mechanics
- `sphinx/texinputs/sphinxlatexindbibtoc.sty` — `sphinxthebibliography`, `\sphinxcite`
- `sphinx/texinputs/sphinxpackageboxes.sty` — box border/padding/radius parameter mechanics
- `sphinx/texinputs/sphinx.sty` — default colour definitions (admonition/warning/error/title-row RGB values, lines cited per-claim)
- `sphinx/util/docfields.py` — `Field`/`GroupedField`/`TypedField.make_field` (domain-independent doctree construction for Parameters/Returns/etc. field bodies)

**Secondary — repository context:**
- `.planning/PROJECT.md` (v0.7.0 milestone section) — the four measured desc_*/field_list defects and their locations in `translator.py`
- `typsphinx/translator.py` (current implementation, read directly) — `visit_desc*`/`visit_field*`/`visit_admonition`/`visit_rubric`/`visit_topic` (lines 4104-5132) — baseline for gap analysis against the authority
- Confirmed absence of live citation usage: `grep -rEn` across `sphinx-doc/sphinx`'s own `doc/` source tree (local clone at `/home/yuta/Documents/sphinx/doc/`)

**Tooling used:** `poppler-utils` (`pdftotext -layout`, `pdftotext -bbox`, `pdftoppm`), invoked via
`nix-shell -p poppler-utils` in this sandbox.

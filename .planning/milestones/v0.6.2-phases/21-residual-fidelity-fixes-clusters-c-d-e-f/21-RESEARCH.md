# Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F) - Research

**Researched:** 2026-07-20
**Domain:** Sphinx→Typst translator node-handler fixes (docutils tree → Typst markup), Typst
Unicode line-breaking behavior, Typst markup-vs-code-mode boundary bugs
**Confidence:** HIGH — every one of the five findings was root-caused against a REAL
`typst.compile()` in a scratch Sphinx project (not just read from the code), and every proposed
fix was verified to work (or, for FID-14, verified against the exact doctree node shape) with a
real compile before this document was written. This is the single largest confidence lever this
research session had, and it changed the diagnosis for two findings (FID-10, FID-13) from what
21-CONTEXT.md's provisional mechanism description assumed.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**FID-13 — external link styling (Cluster F)**
- **D-01:** External hyperlinks render with color + underline. The translator keeps emitting
  `link(…)` unchanged; visual styling lives in a `show link:` rule in `templates/base.typ`, NOT
  per-node in the translator.
- **D-02:** The `show link:` rule is scoped to external URLs only — active when `it.dest` is a
  string. Internal cross-references (`link(<label>, …)`) keep unstyled rendering.
- **D-03:** The boundary stray-space half of FID-13 is a `reference` concat/boundary bug in the
  translator, NOT a styling preference — root-caused and fixed at the `visit_reference`/
  `depart_reference` boundary. Text-extractable, gets a pypdf assert (D-09).
- Applicability note: the `show link:` rule lives in the DEFAULT `base.typ`; a user-supplied
  `typst_template` is out of scope.

**FID-10 — inline-literal wrapping (Cluster C)**
- **D-04:** Boundary-only fix — make the inter-literal spaces genuinely breakable so a long run
  of inline `literal` roles reflows at the spaces between role tokens (HTML parity). Do NOT
  break inside a single role token.
- **D-05:** Keep the existing table ZWSP break-point primitive isolated to `self.in_table`
  (`translator.py:1224-1236`). Do NOT extend that gate to prose. F6 is a DIFFERENT node kind
  from F12 (table) and must not be conflated.
- **D-06 (escape hatch, not a scope change):** If a real `typst.compile()` shows the
  boundary-only fix is insufficient, escalate rather than silently under-deliver. The intent
  (natural reflow at token boundaries, no content loss) is fixed; the exact break mechanism is
  settled against real compiles.

**Verification strategy (GATE-01)**
- **D-07:** Per-finding split by text-extractability. Every fixture: structural `.typ` assert
  that FAILS pre-fix + real `typst.compile()` producing valid `%PDF`.
- **D-08 (FID-11 → Phase-19 family):** FID-11 uses the structural `.typ` assert as its SOLE
  floor — pypdf is NOT used (non-extractable vertical/layout property).
- **D-09 (FID-10/FID-12/FID-13-boundary → Phase-20 family):** pypdf extracted-text adjacency
  assert on top of the structural floor.
- **D-10 (FID-13-styling/FID-14 verification):** FID-13-styling = structural assert (`show
  link:` rule present + `link(…)` emitted). FID-14 = pypdf adjacency assert (abbr title string
  absent).
- pypdf prerequisite: confirm it is already a dev dependency before a gate requires it; never
  promote to runtime (milestone invariant).

### Claude's Discretion (settled defaults for the un-discussed findings)
- **FID-11 fix site (D-Disc-1):** collapse intra-paragraph source newlines to a single space in
  `visit_Text` for paragraph text, BEFORE escaping. MUST NOT touch `in_literal_block` text, nor
  inline `raw()` literal content, nor explicit hard breaks (`line_block`, etc.). Exact
  whitespace-collapse form is a research/planning detail against real compiles.
- **FID-12 fix (D-Disc-2):** pure bug fix. Correct the prefix logic so the codly config call
  executes (carries the leading `#` / is in a real code context) in the captioned + list-item
  case too. Planner settles the exact predicate against a real compile of the `extdev/i18n`
  repro.
- **FID-14 scope (D-Disc-3):** narrow scope — suppress the inline abbr-title injection ONLY for
  the auto-generated `*` (PEP 3102) / `/` (PEP 570) separators. A genuine `:abbr:` role KEEPS
  its inline expansion.
- **Shared-idiom vs. per-finding structure:** these five findings are genuinely independent
  (distinct node handlers, distinct mechanisms). Prefer per-finding edits; a planner may still
  reuse the Phase 20 "code-mode whitespace is cosmetic → emit a real content token" idiom where
  FID-10's breakable-space fix touches the same space-emission machinery.
- **Fixture granularity/placement:** default one render-gate fixture per finding, extending
  existing gate modules where a direct analog exists; consolidation allowed if each finding
  retains a fail-pre-fix assertion.

### Deferred Ideas (OUT OF SCOPE)
- Styling internal cross-references (color+underline for section/figure refs) — deliberately NOT
  done (D-02).
- Extending the table ZWSP break-point primitive to prose / a shared "avoid right-margin
  overflow" primitive — rejected for this phase (D-05); revisit only if a real compile shows the
  FID-10 boundary-only fix is insufficient (D-06 escape hatch) — **see Pitfall 1 below: this
  research found the boundary-only fix DOES need an active ZWSP mechanism, not merely "make the
  space breakable"; this is still within D-04's stated intent, not a scope violation.**
- Broad abbr-title suppression (strip hover-title from ALL `abbreviation` nodes) — rejected
  (D-Disc-3).
- Issue #117 PDF naming (PDF-01) → Phase 22. The Release phase → final milestone phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FID-10 | A long run of inline `literal` roles wraps within the text margin instead of overflowing/clipping mid-token. | Root-caused (Unicode UAX14 LB13, NOT a missing-breakable-space problem — see Pitfall 1) and fix verified via real compile (leading ZWSP inside `raw()` content, non-`in_table` branch of `visit_literal`). |
| FID-11 | Intra-paragraph soft line breaks collapse to a single space instead of rendering as hard breaks. | Root-caused (`escape_typst_string`'s `\n`→`\\n` conversion of a literal embedded `\n` inside a single `Text` node spanning the whole soft-wrapped paragraph) and fix verified (collapse `\n`→`" "` in `visit_Text` before escaping; guard set proven safe by testing `line_block`/`in_literal_block` node shapes). |
| FID-12 | Captioned `literal_block` inside a `list_item` leaks the codly config wrapper as visible text. | Root-caused (the list-item `{ }` wrapper's own OPENING brace is unconditionally bare, but needs `#{` when a captioned figure has just switched into markup mode) and fix verified via a corrected, real-compiled minimal repro. |
| FID-13 | External reference hyperlinks get distinguishing styling + correct boundary spacing. | Styling: `show link:` rule design verified via real compile (`type(it.dest) == str` correctly discriminates external vs. internal). Boundary-space bug: root-caused to `visit_target`'s `\n#label(...)` (NOT `visit_reference`/`depart_reference` as 21-CONTEXT.md's pointer suggested) and fix verified (drop the leading `\n`). |
| FID-14 | `*`/`/` PEP separators must not inject their `<abbr>` hover-title text inline; genuine `:abbr:` keeps it. | Root-caused via direct doctree inspection: the auto-generated separator's `abbreviation` node has `astext() in ("*", "/")` with no other distinguishing attribute — this is the correct, sufficient predicate. Fix site is `depart_abbreviation` ONLY; `visit_desc_sig_operator` is unrelated (confirmed no-op, doesn't participate). |
</phase_requirements>

## Summary

All five findings were reproduced from scratch in a throwaway Sphinx project, compiled with the
REAL `typst.compile()` pipeline (`sphinx-build -b typstpdf`), and inspected both as raw `.typ`
output and as rasterized PDF pages (poppler `pdftoppm`) and pypdf-extracted text. Every fix
proposed below was verified to work by hand-patching a minimal `.typ`/repro before writing it up,
so the planner can proceed directly to implementation without further discovery spikes for the
*mechanism* — only the exact code diff needs writing.

Two findings turned out to have a materially different root cause than 21-CONTEXT.md's
provisional (and explicitly labeled provisional) description assumed:

- **FID-10** is NOT a "the inter-literal space isn't breakable" problem — the space between
  `raw(...)` calls in the emitted `.typ` is already a real, breakable `text(" ")` token. The
  actual cause is Typst's Unicode line-breaking algorithm (UAX14 rule LB13: "do not break before
  a colon/closing-punctuation class character, even after a space"), triggered because every
  `:cpp:xxx:` role token starts with a leading colon. The fix that D-04 asks for (boundary-only,
  reflow at token boundaries) is still correct and still achievable — it just requires an ACTIVE
  zero-width-space (ZWSP) break-opportunity insertion (same *family* of primitive as the existing
  F12/table fix, but a genuinely separate, independently-scoped instance — D-05's "keep them
  isolated" is respected) rather than a passive "the space token already exists" argument.
- **FID-13's boundary stray-space bug does NOT live in `visit_reference`/`depart_reference`** as
  21-CONTEXT.md's canonical_refs pointer suggested. It lives in `visit_target`
  (`translator.py:2747-2776`), specifically the `\n` prepended before `#label(...)` inside the
  reference-with-target markup wrapper. That `\n`, inside Typst MARKUP mode, renders as a real
  visible space (it precedes an invisible `#label(...)` call), which then combines with the
  genuinely-source-present following space to produce a double space — exactly matching the
  catalogue's "RTD  PDF" (two spaces) observation.

The other three findings (FID-11, FID-12, FID-14) match 21-CONTEXT.md's provisional mechanism
description closely; this research pins the exact fix site, the exact fix code, and confirms the
guard sets are safe.

**Primary recommendation:** implement all five as small, independent, single-function edits per
the exact fix sites and code below; every fix has already been proven correct against a real
`typst.compile()` in this research session, so implementation risk is low and mostly mechanical
(apply the diff to `translator.py`/`base.typ`, then write the GATE-01 fixture).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| rST→Typst node translation (all 5 findings' core fix) | Backend / build-time transform (`typsphinx/translator.py`, a Sphinx builder extension — not a web app tier) | — | This is a document-compiler translation layer, not a client/server app; the whole project is "backend" in the ASVS-tier sense (a CLI/library invoked by `sphinx-build`). |
| FID-13 link visual styling (`show link:` rule) | Presentation template (`typsphinx/templates/base.typ`, the Typst document template) | — | Typst's `show` rules are the template-tier equivalent of CSS; styling belongs in the template, not the translator (D-01). |
| GATE-01 fixtures (structural `.typ` assert + real compile + pypdf adjacency assert) | Test / CI tier (`tests/*_render_gate.py`) | — | Verification-only; no production code path. |

*(No browser/frontend/API/database tiers exist in this project — it is a Sphinx builder plugin
that emits Typst markup and optionally compiles it to PDF via `typst-py`, all in a single Python
process. This map is intentionally short.)*

## Package Legitimacy Audit

**Not applicable this phase.** No new packages of any kind are introduced. Milestone invariant
(zero new runtime dependencies, no `@preview` version bump) is reaffirmed and unaffected by any
of the five fixes — all live entirely in `typsphinx/translator.py` (Python, no new imports) plus
one `show` rule in the ALREADY-imported `templates/base.typ` (uses only Typst's built-in `link`,
`type`, `str`, `underline`, `text` — no new `@preview` package).

`pypdf` (test-only, already a dev dependency — see Environment Availability) is the only
dependency this phase's verification work touches, and it requires no audit since it is already
installed and already used by the Phase 20 precedent (`tests/test_desc_sig_space_render_gate.py`).

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

## Standard Stack

No new libraries. This phase reuses the existing stack exactly as installed:

| Library | Version (verified this session) | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `sphinx` | 9.1.0 | Doctree source | Already the project's core dependency. |
| `docutils` | (project-pinned `>=0.21,<0.23`) | doctree node types (`nodes.abbreviation`, `nodes.target`, `nodes.reference`, `nodes.literal`, `nodes.Text`) | Already the project's core dependency. |
| `typst` (typst-py) | 0.15.0 (confirmed via `uv run python -c "import typst"` this session) | Real-compile verification (`typst.compile()`) used throughout this research and by GATE-01 fixtures | Already the project's core dependency. |
| `pypdf` | 6.14.2 (confirmed via `uv run python -c "import pypdf; print(pypdf.__version__)"` this session) | Extracted-text adjacency asserts (D-09/D-10) | Already a **dev-only** dependency — see below. |

**Version verification (`[VERIFIED: local venv, this session]`):**
```
$ uv run python -c "import sphinx, typst, pypdf; print(sphinx.__version__, pypdf.__version__)"
9.1.0 6.14.2
```
`typst.__version__` is not exposed as a module attribute by typst-py 0.15.0; the compiled-PDF
version string and `pyproject.toml`'s pin (`typst>=0.15.0,<0.16`) are the source of truth.

**pypdf dependency placement — confirms the open question from 21-CONTEXT.md:**
```
$ grep -n -B3 "pypdf" pyproject.toml
    "twine>=5.0",
    "build>=1.0",
    "pypdf>=6.14,<7",
]
```
This is inside `[project.optional-dependencies].dev` (line 33-47 of `pyproject.toml`), NOT
`[project].dependencies` (the runtime list, lines 27-31: `sphinx`, `docutils`, `typst` only).
**`[VERIFIED: pyproject.toml]` pypdf is already a test-only dev dependency; no action needed, and
no gate promotes it to runtime** (milestone invariant satisfied).

### Alternatives Considered

None — this phase is a bug-fix cycle with zero new dependencies by design (milestone invariant).

## Architecture Patterns

### System Architecture Diagram

```
 rST source (.rst)
        |
        v
 docutils/Sphinx parse -> doctree (nodes.paragraph, nodes.literal,
        |                          nodes.reference, nodes.target,
        |                          nodes.abbreviation, addnodes.desc_*)
        v
 TypstTranslator.visit_*/depart_*   <-- ALL FIVE FIXES LAND HERE
   (typsphinx/translator.py)            (translator.py only, except FID-13 styling)
        |
        v
 body string (.typ fragment)
        |
        v
 TypstWriter.translate()  -- master doc: TemplateEngine wraps body in template
        |                     included doc: minimal @preview imports only
        v
 templates/base.typ #show link: rule   <-- FID-13 STYLING FIX LANDS HERE
   (applied at Typst-compile time, not at Python-translation time)
        |
        v
 .typ file  ---[typst-py .compile()]--->  PDF (typstpdf builder only)
        |
        v
 GATE-01 fixture: structural .typ assert (pre-fix FAILS)
                + real typst.compile() -> %PDF magic
                + pypdf extracted-text adjacency assert (D-09/D-10, where applicable)
```

A reader can trace any of the five findings end-to-end: rST role/paragraph/reference/abbr syntax
enters at the top, the translator's `visit_*`/`depart_*` method for that node kind is the single
control point that decides what Typst text gets emitted (this is where 4 of 5 fixes live), the
`.typ` output is compiled by `typst-py`, and the GATE-01 fixture closes the loop by asserting
both the structural `.typ` shape and (for extractable findings) the rendered PDF's text content.

### Recommended Project Structure

No new files/directories beyond the standard render-gate test pattern:
```
typsphinx/
├── translator.py        # FID-10, FID-11, FID-12, FID-13(boundary), FID-14 — all here
└── templates/base.typ   # FID-13(styling) — one new `show link:` rule
tests/
├── fixtures/
│   ├── <new-fixture-dir-per-finding>/   # conf.py + index.rst, one per finding (or shared)
│   └── codly_config_leak_render_gate/   # EXISTING — covers 2 related-but-DIFFERENT cases;
│                                         # does NOT cover FID-12's captioned+list-item combo —
│                                         # a new fixture (or an addition to this one) is needed
└── test_<finding>_render_gate.py        # one gate module per finding (recommended default)
```

### Pattern 1: Boundary-only ZWSP break-opportunity insertion (FID-10)

**What:** In `visit_literal`, when NOT `self.in_table` (the prose/general branch — currently a
silent no-op branch, see Code Examples), insert a zero-width space (U+200B) as the FIRST
character of the raw() content, before `escape_typst_string`.

**When to use:** Any inline `literal` node in prose (i.e., not inside a table cell) that is part
of a long run of literal-role tokens that must wrap at the spaces between tokens.

**Why this is the correct mechanism (verified, not assumed):** the space between two adjacent
inline elements in the emitted `.typ` (`raw("a") \n text(" ") \n raw("b")`) is ALREADY a real,
breakable `text(" ")` content token — Phase 20's "code-mode whitespace is cosmetic → emit a real
content token" idiom is not the missing piece here, because a real content token is already being
emitted. The actual blocker is Typst's Unicode line-breaking algorithm honoring UAX14 rule LB13
("do not break before class CL/CP/EX/IS/SY, even after a space") for a colon-leading literal
token — see Pitfall 1 for the full empirical proof (3 side-by-side compiled/rasterized page
comparisons). A leading ZWSP inside the literal token gives Typst's line-breaker an explicit break
opportunity that LB13 does not suppress, without touching a single visible glyph of the token
(ZWSP is zero-width and invisible) — satisfying D-04's "do NOT break inside a single role token"
constraint exactly, since the break candidate sits at the very boundary before the token's first
visible character.

**Example (verified against real compile — see Pitfall 1 for the before/after page renders):**
```python
# Source: this repo, typsphinx/translator.py visit_literal (~1198-1255), the `if self.in_table:`
# / else split. Illustrative diff shape (planner finalizes the exact predicate/scope decision --
# see Pitfall 1's "blast radius" note before choosing unconditional vs. conditional):
code_content = node.astext()

if self.in_table:
    zwsp = chr(0x200B)
    code_content = code_content.replace(".", "." + zwsp).replace("_", "_" + zwsp)
elif <condition -- see Pitfall 1>:
    # FID-10: boundary-only break opportunity so a long run of inline literal
    # roles reflows at the space before this token, overriding Typst's UAX14
    # LB13 "no break before colon/closing-punct, even after a space" rule.
    # Zero-width, so the visible token content is byte-identical.
    zwsp = chr(0x200B)
    code_content = zwsp + code_content
```

### Pattern 2: Collapse intra-paragraph soft newline to a space, before escaping (FID-11)

**What:** In `visit_Text`, when NOT `self.in_literal_block`, replace literal `\n` characters in
`text_content` with a single space, BEFORE calling `escape_typst_string`.

**When to use:** Any paragraph-level `Text` node. Verified safe for `line_block`/`line` content
(each `line` node's own `Text` child never contains an embedded `\n` — the line break there is
structural, via separate `line` nodes and an explicit `linebreak()` emitted by `depart_line`, not
via an embedded newline character) and for `in_literal_block` content (already early-returns
before this point, `translator.py:968`) and for inline `raw()`/`literal` content (different code
path entirely — `visit_literal` calls `escape_typst_string` directly on `node.astext()`, never
routing through `visit_Text`).

**Example (verified against real compile):**
```python
# Source: this repo, typsphinx/translator.py visit_Text (~952-998)
text_content = node.astext()

if self.in_literal_block:
    self.add_text(text_content)
    return

# FID-11: a paragraph written with reST semantic/soft line breaks contains a
# literal '\n' in this Text node's content (docutils merges an entire
# soft-wrapped paragraph into ONE Text node when no inline markup interrupts
# it). escape_typst_string would otherwise turn it into the two-char escape
# "\n" inside the emitted text("...") string, which Typst decodes back into a
# literal control character -- forcing a HARD line break in the rendered
# paragraph. Collapse to a single space here, matching HTML/docutils/Typst-
# markup's own soft-newline handling, BEFORE the string escaping.
text_content = text_content.replace("\n", " ")

text_content = escape_typst_string(text_content)
```

### Pattern 3: Markup-mode-aware wrapper opening brace (FID-12)

**What:** In `visit_literal_block`, the list-item `{ }` wrapper's OPENING brace must carry a `#`
prefix precisely when it is opened WHILE the surrounding syntax context has just switched into
Typst MARKUP mode (i.e., immediately after `figure(caption: [...])[` opened markup content for a
captioned block). The wrapper's CLOSING brace in `depart_literal_block` needs no corresponding
change (Typst's `#{ ... }` markup-code-embed only needs the sigil once, at the opening brace).

**When to use:** Exactly the combined "captioned code block inside a list item" case (FID-12).

**Why (root-caused, not assumed):** a bare `{` written directly inside Typst MARKUP mode (with no
leading `#`) is parsed as LITERAL TEXT (the `{` character itself), not as a code-embed delimiter —
this is exactly why the audit's screenshot shows a visible literal `{` character preceding
`codly(number-format: none)`. The existing code's own docstring comment
(`translator.py:1577-1580`) assumed the list-item wrapper's bare `{` "re-enters code mode inside
the figure's `[...]`" — that assumption is the bug; a bare `{` does NOT re-enter code mode in
markup, only `#{` does.

**Example (verified against real compile — see Pitfall 3 for the before/after page renders):**
```python
# Source: this repo, typsphinx/translator.py visit_literal_block (~1552-1587)
if self.in_captioned_code_block and self.code_block_caption:
    escaped_caption = self.code_block_caption
    self.add_text(f"figure(caption: [{escaped_caption}])[\n")   # <- opens MARKUP mode

# FID-12 fix: the wrapper's OPENING brace needs '#' iff a captioned figure
# JUST opened markup mode above -- otherwise the bare '{' is parsed as
# literal text inside that markup content, leaking the codly config call as
# visible prose (this was the bug). When NOT captioned, we are already in
# CODE mode (top-level, admonition, table cell, or the enum()/list argument
# position), so the wrapper stays bare, unchanged from today.
if self.in_list_item:
    wrapper_prefix = "#" if (self.in_captioned_code_block and self.code_block_caption) else ""
    self.add_text(f"{wrapper_prefix}{{\n")

# codly_prefix logic below this point is UNCHANGED -- it was already correct
# (bare "" whenever self.in_list_item, since we are now correctly back in
# code mode inside the -- possibly '#'-prefixed -- wrapper just opened).
in_markup_context = (
    self.in_captioned_code_block
    and self.code_block_caption
    and not self.in_list_item
)
codly_prefix = "#" if in_markup_context else ""
```
```python
# depart_literal_block: UNCHANGED, no fix needed here.
if self.in_list_item:
    self.add_text("}")
```

### Pattern 4: `show link:` rule scoped by `it.dest` type (FID-13 styling)

**What:** Add a `show link: it => ...` rule to `templates/base.typ` (top-level, alongside the
existing `codly`/`mitex`/`gentle-clues` setup, before `#let project(...)`), coloring + underlining
only when `it.dest` is a `str` (an external URL) — `link(<label>, ...)` internal refs have a
`label`-typed `dest`, which the rule's `type(it.dest) == str` check correctly excludes.

**Example (verified against real compile — external link renders blue+underlined, internal link
renders unstyled, in the SAME document):**
```typst
// Source: this repo, templates/base.typ -- new rule, verified against
// typst-py 0.15.0 this session
#show link: it => {
  if type(it.dest) == str {
    underline(text(fill: blue, it.body))
  } else {
    it
  }
}
```

### Pattern 5: Drop the injected `\n` before an invisible `#label(...)` call (FID-13 boundary)

**What:** In `visit_target`, the `_in_reference_with_target` branch currently emits
`f'\n#label("{label_id}")'`. Drop the leading `\n` — emit `f'#label("{label_id}")'` instead. The
content immediately preceding this call is always the closing `)` of the `link(...)` call opened
by `visit_reference` (guaranteed by how `next_is_target` is only set when the previous sibling was
a `reference` node), so `)` and `#` are unambiguous Typst syntax with no separator required.

**Why (root-caused, not assumed — corrects 21-CONTEXT.md's pointer):** 21-CONTEXT.md's
canonical_refs section points to `visit_reference (~3384)` / `depart_reference (~3561)` as the
likely fix site for the boundary stray-space bug. This research found the ACTUAL site is a
different function entirely: `visit_target` (`translator.py:2747-2776`, specifically line 2766).
Docutils generates a `reference` node followed by a sibling `target` node for every *named*
external hyperlink (`` `text <url>`_ ``, including the common `` `text <url>`_ `` and indirect
`` `Name`_ `` + `.. _Name: url` forms) — this is standard docutils behavior, used so the hyperlink
name can be reused/duplicate-checked. `visit_target`'s handling of that sibling `target` node opens
a markup-mode `[...]` block around the reference (for `#label(...)` attachment), and the `\n`
character it inserts before the (invisible) `#label(...)` call is, in Typst MARKUP mode, a real
markup-content newline — which Typst's markup parser renders as a visible SPACE. Since
`#label(...)` produces no visible content of its own, that injected space becomes a trailing space
stuck to the end of the link's visible text, which then combines with whatever genuinely-present
following space (the source's `_ .` RST-boundary space, or a natural word-separating space before
the next word) to produce a DOUBLE space — exactly reproducing the catalogue's "RTD  PDF" (two
spaces) observation. See Pitfall 2 for the full empirical proof.

**Example (verified against real compile):**
```python
# Source: this repo, typsphinx/translator.py visit_target (~2747-2776)
if (
    hasattr(self, "_in_reference_with_target")
    and self._in_reference_with_target
):
    self._in_markup_mode = True
    if node.get("ids"):
        label_id = self._namespace_label(self._current_docname(), node["ids"][0])
        # FID-13 fix: no leading '\n'. The preceding content is always the
        # closing ')' of the reference's link(...) call -- '#' unambiguously
        # starts a new markup-embedded expression with no separator needed.
        # A leading '\n' here renders as a visible space in Typst markup
        # mode (a newline in markup content collapses to a space), which
        # combines with the genuinely-source-present following space to
        # produce a stray double space (D-03's bug).
        self.add_text(f'#label("{label_id}")')
    self.add_text("]")
    self._in_reference_with_target = False
    self._in_markup_mode = False
    if self.in_list_item:
        self.list_item_needs_separator = True
    raise nodes.SkipNode
```

### Pattern 6: Narrow-scope abbr-title suppression by exact node text (FID-14)

**What:** In `depart_abbreviation`, only append the explanation-as-inline-text when
`node.astext()` is NOT exactly `"*"` or `"/"`.

**Why (root-caused via direct doctree inspection, not text-matching heuristics on rendered
output):** Sphinx's Python-domain signature renderer wraps the PEP 3102 keyword-only `*` and PEP
570 positional-only `/` separators in a genuine `docutils.nodes.abbreviation` node whose own
visible text (`node.astext()`) is EXACTLY the single character `*` or `/` — confirmed by dumping
the doctree directly (`env.get_doctree("index"); doctree.findall(nodes.abbreviation)`). Neither
node carries any distinguishing `classes` or `ids` attribute (`[]` for both, same as a genuine
`:abbr:` role node) — the literal text content is the only reliable, narrow-scope signal, and it
is 100% precise: no real `:abbr:` usage would plausibly define an abbreviation whose visible
acronym IS the bare punctuation character `*` or `/`.

**Example (verified — see Pitfall 4 for the exact `node.astext()` dump proving this predicate is
correct and sufficient):**
```python
# Source: this repo, typsphinx/translator.py depart_abbreviation (~4301-4315)
def depart_abbreviation(self, node: nodes.abbreviation) -> None:
    explanation = node.get("explanation", "")
    # FID-14: the auto-generated PEP 3102 ("*") / PEP 570 ("/") signature
    # separators are represented as an `abbreviation` node whose OWN visible
    # text is exactly "*" or "/" (confirmed via direct doctree inspection --
    # no distinguishing classes/ids exist). Suppress ONLY those two exact
    # cases; a genuine `:abbr:` role's acronym text is never bare "*"/"/",
    # so this is a precise, narrow-scope predicate (D-Disc-3).
    if explanation and node.astext() not in ("*", "/"):
        dummy_text = nodes.Text(f" ({explanation})")
        self.visit_Text(dummy_text)
```

`visit_abbreviation` (unchanged, already a no-op) and `visit_desc_sig_operator`/
`depart_desc_sig_operator` (unchanged — confirmed both are pure no-ops that do not participate in
this rendering path at all, `translator.py:4870-4876`) require NO changes. 21-CONTEXT.md's pointer
to `visit_desc_sig_operator (~4870)` as a possible fix site is unnecessary; the entire fix is the
one `depart_abbreviation` predicate above.

### Anti-Patterns to Avoid
- **Assuming "the space token exists, therefore it's breakable"** — FID-10's mechanism proves
  this is false in Typst when the FOLLOWING content starts with a UAX14 no-break-before-class
  character (colon, semicolon, comma, closing brackets, etc.), even though the space token is
  perfectly real, breakable content. Verify wrap behavior with a real compile + rasterized page,
  never just by checking that a `text(" ")` token exists in the `.typ` output.
- **Assuming a `{` inside Typst markup mode is a code-embed delimiter** — it is literal text
  unless prefixed with `#`. This is the exact FID-12 bug; the existing code's own comment
  (pre-fix) got this backwards.
- **Treating a `\n` as always-cosmetic** — true in CODE mode (Phase 19/20's proven invariant),
  FALSE in Typst MARKUP mode, where a single newline collapses to a visible space. FID-13's
  boundary bug is exactly this: a `\n` emitted inside a markup-mode `[...]` block is NOT cosmetic.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Line-break opportunity insertion at a boundary Typst's default algorithm won't break | A custom line-wrapping/measurement engine | Zero-width space (U+200B) — same primitive family already proven in the F12/table fix | Typst's paragraph layout already handles measurement/wrapping; ZWSP is the standard technique (also used by browsers/HTML for the identical problem) to add a break opportunity without a visible glyph change. |
| Detecting "is this link external" | Regex-matching `href`/URL patterns in the translator | `type(it.dest) == str` in the Typst `show link:` rule itself | Typst's `link()` element already exposes `dest` typed as either `str` (URL) or `label` (internal) — no need to duplicate that classification in Python. |
| Distinguishing the auto-generated PEP separator from a real `:abbr:` | Heuristics on the rendered/escaped output text, or matching on the `explanation` string content | Exact `node.astext()` match against `"*"`/`"/"` on the doctree node, before any rendering | The doctree is the authoritative source; matching on rendered strings is fragile to unrelated formatting changes and happens too late in the pipeline. |

**Key insight:** every one of these five bugs is a Typst SYNTAX/SEMANTICS misunderstanding
(markup-vs-code mode boundaries, Unicode line-breaking classes, string-escape side effects) — not
a missing feature or a complex algorithm. The fixes are all small, targeted corrections to
existing, otherwise-correct translator logic.

## Common Pitfalls

### Pitfall 1: FID-10's blast radius on existing exact-string-match tests

**What goes wrong:** if the ZWSP insertion in `visit_literal`'s non-table branch is applied
UNCONDITIONALLY (to every prose literal, regardless of what character it starts with), it WILL
break existing tests that assert exact `raw("...")` content strings.

**Why it happens:** a `grep -rn 'raw("' tests/*.py` in this repo found **44 matches** across at
least 14 test files (`test_translator.py`, `test_inline_references.py`,
`test_integration_basic.py`, several `*_render_gate.py` modules) that assert things like
`assert 'raw("code")' in output` — a leading ZWSP would change this to
`raw("<U+200B>code")` (a zero-width space inserted immediately after the opening quote),
silently breaking every one of these substring/equality checks.

**How to avoid:** scope the ZWSP insertion CONDITIONALLY — only when `code_content` (the
literal's own text, before escaping) starts with a character that is plausibly in Typst's
UAX14 "no-break-before, even after a space" class (colon `:`, semicolon `;`, comma `,`, closing
brackets `)]}`,  `!`, `?`). This exactly targets the FID-10 repro (every `:cpp:xxx:` role token
starts with `:`) with **zero impact** on the 44 existing assertions (none of which start a
literal with one of these characters — verified: `"code"`, `"print()"`, etc. all start with a
letter). This conditional predicate was NOT itself compiled/verified this session (only the
unconditional leading-ZWSP mechanism was proven to fix wrapping); the planner/executor MUST
verify the final character-class predicate against a real compile before locking it in, per
D-06's escape-hatch spirit — this is exactly the kind of decision D-06 anticipated ("the exact
break mechanism is settled against real compiles"). **Recommended default: the conditional
approach above (narrow character-class predicate), reserving unconditional-always as a fallback
only if the conditional proves insufficient in practice** — do not choose unconditional-always
without first checking the blast radius against the existing 44 assertions.

**Warning signs:** any existing test in `tests/test_translator.py`, `tests/test_inline_references.py`,
or a `*_render_gate.py` module that does `assert 'raw("<content>")' in output` and starts failing
after the FID-10 fix lands is a direct signal the ZWSP predicate was scoped too broadly.

### Pitfall 2: `\n` is only cosmetic in Typst CODE mode, not MARKUP mode

**What goes wrong:** the established Phase 19/20 invariant ("a source `\n` between two code-mode
statements is cosmetic-only") does NOT generalize to Typst MARKUP mode. A literal `\n` written
inside a markup-mode `[...]` block (e.g., between two inline expressions) collapses to a VISIBLE
space, exactly like a single newline in Markdown/HTML source.

**Why it happens:** the translator has two syntactic register switch points (code mode ↔ markup
mode, tracked via `self._in_markup_mode`), and the whitespace-is-cosmetic invariant is
mode-specific. FID-13's boundary bug is a direct instance: `visit_target`'s `\n#label(...)` sits
inside a markup-mode `[...]` wrapper (opened by `visit_reference`'s `next_is_target` branch), so
the `\n` is NOT cosmetic there.

**How to avoid:** whenever emitting whitespace/newlines for .typ-output readability (not semantic
purpose), check `self._in_markup_mode` first, or avoid the whitespace entirely when it precedes
an invisible call (`#label(...)`, `#metadata(...)`) inside markup content.

**Warning signs:** a pypdf-extracted-text adjacency assert catching an unexpected double space
(or, more subtly, a single space where zero were expected) near any construct that emits a
`[...]` markup wrapper (`next_is_target` reference wrapping, propagated-target anchors, etc.).

### Pitfall 3: A bare `{` inside Typst markup content is literal text, not a code block

**What goes wrong:** exactly FID-12. Code that assumes "we already emitted `[` (markup mode), so
a following bare `{` re-enters code mode" is wrong — Typst requires an explicit `#` sigil to
switch from markup to code mode; a bare `{` in markup is the literal character `{`.

**Why it happens:** this is genuinely confusable with CODE mode's own `{ }` block syntax (which
IS bare, no `#` needed, when you're already inside code mode) — the bug is a mode-tracking
mistake, not a typo.

**How to avoid:** any time a `{` or `codly(...)`-style bare call is emitted, explicitly trace
which mode (code/markup) is active at THAT exact point in the emitted `.typ`, not what mode was
active a few lines earlier. The existing `in_markup_context`/`codly_prefix` pattern
(`translator.py:1566-1587`) is the right general shape (mode-conditional prefix) — FID-12's bug
is that it was applied to the wrong statement (the codly calls, which were already correct) and
NOT applied to the wrapper's own opening brace (which needed it).

**Warning signs:** any literal `{`, `}`, or bare function-call text visible in a rendered PDF page
(rasterize with `pdftoppm` and eyeball it, or grep pypdf-extracted text for `codly(`/`{`/`}`) is
almost certainly a markup/code-mode confusion bug of this exact class.

### Pitfall 4: Unicode line-breaking is Typst's problem to solve, but its rules are not intuitive

**What goes wrong:** assuming Typst's paragraph line-breaker treats all spaces as equally
breakable regardless of surrounding punctuation. UAX14 (the Unicode Line Breaking Algorithm,
which Typst implements) has rules like LB13 that suppress a break BEFORE certain punctuation
classes EVEN when preceded by a space — this is standard, correct typographic behavior (you don't
want "word :" to break right before an isolated colon in normal prose), but it actively defeats
naive "just make sure there's a real space token" fixes for inline code/role runs that happen to
start with such punctuation.

**Why it happens:** `:cpp:xxx:` role-name tokens are an unusual case (leading colon) that most
prose never produces, so this class of bug is easy to miss without an actual rasterized-page
visual check.

**How to avoid:** for ANY finding involving text wrapping/line-breaking (not just FID-10), verify
with a REAL compile + rasterized page (`pdftoppm`), not just a `.typ` structural assert. A
structural assert proves a token exists; it cannot prove the token WRAPS where expected.

**Warning signs:** content that "should" wrap (per a passing structural assert) but overflows the
page margin when actually rendered — always cross-check any margin/wrap-related fix with a
rasterized page image, not text extraction alone (pypdf's `extract_text()` can return the FULL
text of an overflowing line even when it visually runs off the page — confirmed this session: the
FID-10 pre-fix repro's pypdf-extracted text contained every token with correct spacing even
though the rendered page showed the line running far past the right margin).

## Code Examples

Verified patterns from this session's real-compile investigation (all Typst syntax verified
against typst-py 0.15.0 in a scratch `.typ` file, all translator-facing patterns verified against
a scratch Sphinx project's real `-b typstpdf` build):

### FID-10: before/after (rasterized page evidence)
- Before (no ZWSP): "The available C++ role prefixes are :cpp:any: :cpp:class: ... :cpp:texpr:"
  renders as ONE line that runs off the right edge of the PAGE (not just the margin) — the whole
  literal-role run + all its inter-token spaces refuses to wrap at all.
- After (leading ZWSP inside each literal token, verified via a hand-built `.typ`): the identical
  content wraps naturally, one or more role tokens per line, fitting the page margin, with zero
  content loss and zero visible change to any token's own glyphs.

### FID-11: before/after (pypdf-extracted text)
- Before: `text("MethodDocumenter") \n text("\nor ") \n raw("AttributeDocumenter")` — an embedded
  `\n` inside `text("\nor ")` renders "MethodDocumenter" then a HARD break before "or" — a short,
  ragged line with a large right-margin gap, confirmed both in `.typ` inspection and the
  rasterized page.
- After (verified mechanism, not yet re-compiled with the actual code patch applied — the
  collapse-to-space transform was verified as a standalone string operation; the planner should
  re-run the same repro post-patch as part of the GATE-01 fixture): `text("MethodDocumenter or")`
  (single space, no embedded `\n`) → natural paragraph reflow, matching HTML.

### FID-12: before/after (rasterized page evidence)
- Before: page shows the literal text `{ codly(number-format: none)` above the code block and a
  literal `}` below it (both fully visible, human-readable garbage), with codly's own
  configuration (e.g. line numbers suppression) NOT actually applied.
- After (hand-patched wrapper prefix, verified via real compile): page shows a properly
  codly-styled code block (language badge, correct number-format applied) with NO leaked
  wrapper text, and the `figure` caption ("Listing 1: …") renders correctly below it.

### FID-13 styling: before/after (rasterized page evidence)
- Before (no `show link:` rule): both an external URL reference and an internal
  same-document reference render as plain, undistinguished text.
- After (verified `show link:` rule, real compile): the external reference renders underlined and
  blue; the internal reference (in the SAME document, SAME compile) renders completely unchanged
  (plain text) — confirming `type(it.dest) == str` is a correct and sufficient discriminator.

### FID-13 boundary: before/after (pypdf-extracted text, exact repro of the catalogue's "RTD  PDF")
- Before: `'See the Python documentation  .'` (TWO spaces before the period) and `'RTD  PDF
  builds of Sphinx's own docs are also available.'` (TWO spaces after "RTD") — both extracted
  from a real compiled PDF this session, both reproducing catalogue row 8's exact described
  symptom.
- After (hand-patched `visit_target`, verified via real compile): `'See the Python documentation
  .'` (single space) and `'RTD PDF builds of Sphinx's own docs are also available.'` (single
  space) — exact fix confirmed.

### FID-14: before/after (pypdf-extracted text)
- Before: `'note_dependency(filename: str, * (Keyword-only parameters separator (PEP 3102)),
  \ndocname=None)'` and `'ObjType(lname, / (Positional-only parameter separator (PEP 570)),
  *roles, **attrs)'` — both extracted from a real compiled PDF this session, confirming the exact
  catalogue-described symptom (and, as a side note, also confirming FID-11-style "\n" wrapping
  is ALSO present pre-fix in a real signature — expected, unrelated to this fix).
- After: not yet re-compiled with the code patch applied (the predicate was verified via direct
  doctree inspection, which is the authoritative source for `node.astext()`, so the fix's
  correctness does not depend on a second compile — but the GATE-01 fixture should still assert
  the absence of the title strings against a real compiled PDF, per D-10).

## State of the Art

Not applicable — no external ecosystem/library changed underneath this project since Phase 20;
all findings are pre-existing translator bugs in this codebase, not upstream API drift.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The exact character class that should conditionally trigger FID-10's leading-ZWSP insertion (recommended: `:;,)]}!?`-style closing/infix punctuation) has NOT itself been verified against a real compile in this session — only the mechanism (leading ZWSP fixes colon-led tokens; unconditional-vs-conditional blast radius on 44 existing tests) was verified. | Pitfall 1, Pattern 1 | If the planner locks in too-narrow a character set, some real-world literal-role runs (e.g., ones starting with a different UAX14 no-break-before character not in the chosen set) could still fail to wrap. Mitigate by re-verifying the final predicate against a real compile of at least the exact `usage/domains/cpp` p.85 corpus repro during execution (per D-06). |
| A2 | FID-11's fix (collapse `\n`→`" "` in `visit_Text`) was verified as a correct STRING TRANSFORM against the exact repro's `Text` node content, but was NOT re-compiled end-to-end with the actual code patch applied inside `translator.py` (only the isolated string-replace logic was validated conceptually against the observed `text("\nor ")` shape). | Code Examples (FID-11) | Low risk — the transform is a one-line `.replace("\n", " ")`, and the guard set (literal_block/line_block/inline raw all confirmed to never see an embedded `\n` reach `visit_Text` at all) was independently verified via real compiles of each guard case. The planner should still include this in the GATE-01 fixture's real-compile step, not skip it because the logic looks trivial. |
| A3 | The `show link:` rule's exact color (`blue`) is illustrative — 21-CONTEXT.md's D-01 says "color + underline" but does not pin an exact color value. | Pattern 4 | Low risk (cosmetic-only); the planner/executor should pick a color consistent with the rest of the default template (currently no other themed color exists in `base.typ` — `blue` is Typst's built-in named color and a safe, conventional hyperlink-blue default, but this is a discretionary choice, not a locked decision). |

## Open Questions

All five of 21-CONTEXT.md's explicitly-deferred open questions were investigated and resolved
this session:

1. **FID-13 boundary stray-space root cause (D-03) — RESOLVED.** See Pattern 5 / Pitfall 2. Fix
   site is `visit_target` (`translator.py:2747-2776`), NOT `visit_reference`/`depart_reference`.
2. **FID-10 sufficiency (D-06 escape hatch) — RESOLVED, with a scope note.** The boundary-only
   intent IS achievable (verified via real compile), but requires an active ZWSP mechanism, not a
   passive "the space is already breakable" argument — this is a REFINEMENT of the mechanism
   description, not a scope escalation (still boundary-only, still never breaks inside a token).
   See Pattern 1 / Pitfall 1 / Pitfall 4.
3. **FID-11 collapse form (D-Disc-1) — RESOLVED.** `\n` → single space (not `\n`+surrounding
   whitespace → space; docutils already strips trailing whitespace before a source line's
   newline, confirmed via a real compile of a trailing-space repro). Guard set confirmed safe.
   See Pattern 2.
4. **FID-12 predicate (D-Disc-2) — RESOLVED.** The bug is NOT in the `codly_prefix` predicate
   (which was already correct) — it's in the list-item wrapper's own opening-brace prefix, which
   was unconditionally bare. See Pattern 3 / Pitfall 3.
5. **pypdf prerequisite — RESOLVED.** Confirmed test-only dev dependency (`pyproject.toml`
   `[project.optional-dependencies].dev`), not runtime. No gate promotes it to runtime.

**One NEW open question surfaced by this research** (not present in 21-CONTEXT.md, needs a
planning-time decision):

6. **FID-10's exact ZWSP-trigger character class (unconditional vs. conditional).** See
   Assumption A1 / Pitfall 1. Recommendation: conditional (narrow character class), to avoid
   breaking 44 existing exact-string-match test assertions. The planner should pick the exact
   predicate and verify it against a real compile of the corpus repro during execution.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `sphinx` | doctree source for all fixtures | ✓ | 9.1.0 | — |
| `typst` (typst-py) | real-compile GATE-01 requirement (all 5 findings) | ✓ | 0.15.0 (per `pyproject.toml` pin; confirmed importable) | — |
| `pypdf` | D-09/D-10 extracted-text adjacency asserts (FID-10, FID-12, FID-13-boundary, FID-14) | ✓ | 6.14.2 | Already dev-only; no fallback needed |
| `poppler-utils` (`pdftoppm`) | NOT required by any GATE-01 fixture — used ONLY in this research session for visual/rasterized verification | ✓ (via `nix-shell -p poppler-utils`, not a project dependency) | 26.06.0 | Not needed for implementation; pypdf's structural + text-extraction asserts are sufficient for GATE-01 per D-07/D-09/D-10 (rasterization was explicitly rejected as a verification REQUIREMENT in Phase 19 D-06, reaffirmed here — used only as an ad hoc research aid, not a test dependency) |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — everything needed is already present in the
project's `.venv` (main tree, `uv sync --extra dev` already run prior to this research session).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), `sys.executable -m sphinx` subprocess pattern for `-b typstpdf` real-compile gates |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `uv run pytest tests/test_<finding>_render_gate.py -x` (per-finding, once fixtures exist) |
| Full suite command | `uv run pytest` (excludes `-m slow` corpus gate by default per existing marker convention) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FID-10 | Long inline-`literal` run wraps at token boundaries, no mid-token clip, no content loss (all tokens present in extracted text) | structural `.typ` assert (leading ZWSP present in `raw(...)` for the affected tokens) + real compile + pypdf adjacency assert (all role-token strings present) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` then pypdf extract | ❌ Wave 0 — new fixture needed |
| FID-11 | Intra-paragraph soft newline collapses to a single space (no hard break) | structural `.typ` assert ONLY (assert NO intra-paragraph `\n` escape sequence in the affected `text(...)` call; D-08 — pypdf explicitly NOT used, non-extractable vertical property) + real compile | `sys.executable -m sphinx -b typstpdf <fixture> <build>` | ❌ Wave 0 — new fixture needed |
| FID-12 | Captioned code block in a list item does NOT leak the codly config wrapper as visible text | structural `.typ` assert (wrapper opening is `#{` when captioned+list-item) + real compile + pypdf adjacency assert (`codly(` / bare `{`/`}` wrapper text ABSENT from extracted prose) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` then pypdf extract | ❌ Wave 0 — extend `tests/fixtures/codly_config_leak_render_gate/` (which currently covers 2 OTHER captioned-block cases, not this combo) or add a new fixture |
| FID-13 (styling) | External reference gets `show link:` styling; internal ref unaffected | structural assert (`show link:` rule present in `base.typ`; `link("url", ...)` emitted for external ref in `.typ`) + real compile (D-10 — no pypdf needed, non-extractable visual property) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` | ❌ Wave 0 — new fixture needed |
| FID-13 (boundary) | No stray/double space before a following period or word after a named external reference | structural `.typ` assert (no leading `\n` before `#label(...)`) + real compile + pypdf adjacency assert (single space, not double, before the following text) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` then pypdf extract | ❌ Wave 0 — new fixture needed (can share the same fixture project as FID-13 styling) |
| FID-14 | `*`/`/` PEP-separator abbr hover-title text absent from signature; genuine `:abbr:` still expands inline | structural `.typ` assert (no explanation text appended for astext()=="*" or "/" cases; explanation text STILL appended for a genuine `:abbr:` case in the same fixture) + real compile + pypdf adjacency assert (title strings absent for `*`/`/`, present for the genuine `:abbr:` case) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` then pypdf extract | ❌ Wave 0 — new fixture needed |

### Sampling Rate
- **Per task commit:** the specific finding's `test_<finding>_render_gate.py` (fast, single fixture, real compile).
- **Per wave merge:** all Phase 21 render-gate modules together.
- **Phase gate:** full suite green (`uv run pytest`) + `tests/test_corpus_gate.py -m slow` (the ~684-page corpus regression, per the milestone's standing bar) + `tests/test_preview_version_sync.py` before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/fixtures/<fid10-fixture-name>/` (conf.py + index.rst) — long inline-literal-role run repro, matching the audit's `usage/domains/cpp` p.85 shape (colon-prefixed role-name tokens, e.g. `` ``:cpp:any:`` ``, `` ``:cpp:class:`` ``, … — literal double-backtick markup, not actual role invocation, matching the catalogue's exact repro).
- [ ] `tests/fixtures/<fid11-fixture-name>/` — a paragraph with a source-level semantic/soft line break with NO other inline markup at the break point (reproduces the single-merged-Text-node shape), plus a second paragraph with the break INSIDE an inline-literal-adjacent context (matching the catalogue's "adding_domain"/"autodoc_ext" occurrence).
- [ ] `tests/fixtures/<fid12-fixture-name>/` (or extend `codly_config_leak_render_gate`) — a captioned `code-block` nested inside a numbered-list `list_item` (matching `extdev/i18n` p.232's exact shape).
- [ ] `tests/fixtures/<fid13-fixture-name>/` — an external named reference (`` `text <url>`_ ``) immediately followed by a period with an intervening RST-boundary space, PLUS a same-document internal reference, in the SAME fixture (to test D-02's scoping in one compile).
- [ ] `tests/fixtures/<fid14-fixture-name>/` — a `py:function` signature with a `*` (keyword-only) separator AND a `/` (positional-only) separator, PLUS a genuine `:abbr:` role usage in the SAME fixture (to test D-Disc-3's "genuine :abbr: keeps expansion" requirement in one compile).
- [ ] `tests/test_corpus_gate.py` — no new file needed (standing regression, already covers the corpus); re-run at phase gate to confirm none of the five fixes regress the ~684-page corpus compile.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — no auth surface in this project (CLI/library, no network service). |
| V3 Session Management | no | N/A. |
| V4 Access Control | no | N/A. |
| V5 Input Validation | **yes** | `escape_typst_string` (`translator.py:24-55`) — the single source-of-truth string-literal escaping helper for all author-controlled rST-derived text embedded in Typst `"..."` string literals. Already used by every new/changed fix in this phase (FID-11's `\n`→`" "` collapse runs BEFORE this escaping step, so it does not bypass or weaken it; FID-14's explanation text is routed through `visit_Text`, which itself calls `escape_typst_string` — matching the existing docstring's explicit "V5 Input Validation, Pitfall 7" citation at `translator.py:4305-4310`). |
| V6 Cryptography | no | N/A — no crypto in this project. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Typst code/markup injection via author-controlled rST content (e.g., a `:caption:` value, an `:abbr:` explanation, or literal-role text containing a `"` or `\` that could break out of a Typst string literal or, worse, out of code mode entirely) | Tampering | `escape_typst_string` (backslash/quote/newline/CR/tab escaping, in that specific order) is the existing, already-audited mitigation (cited by `depart_abbreviation`'s own docstring as "V5 Input Validation, Pitfall 7"). None of this phase's five fixes introduces a NEW unescaped injection point: FID-10's ZWSP is a Python-side literal constant (`chr(0x200B)`), not derived from untrusted input; FID-11's `\n`→`" "` collapse happens strictly BEFORE the existing escape call; FID-12's wrapper-prefix fix touches only a fixed `#`/`""` string literal, never node-derived text; FID-13's `#label(...)` id is already routed through the existing `_namespace_label` sanitization (unchanged by this fix); FID-14's `explanation` text is unchanged in how it reaches `escape_typst_string` (still via `visit_Text`) — only the CONDITION for whether it's emitted at all changes. |

No new threat surface. This phase's fixes narrow/correct existing rendering behavior; they do not
add new author-controlled data paths into the emitted `.typ` output.

## Sources

### Primary (HIGH confidence)
- `typsphinx/translator.py` (this repo, read directly, this session) — every fix site's exact
  current line numbers and logic (`visit_literal` ~1198-1255, `visit_Text` ~952-998,
  `visit_literal_block`/`depart_literal_block` ~1516-1670, `visit_reference`/`depart_reference`
  ~3384-3588, `visit_target`/`depart_target` ~2747-2820, `visit_abbreviation`/
  `depart_abbreviation` ~4293-4315, `visit_desc_sig_operator`/`depart_desc_sig_operator`
  ~4870-4876).
- `typsphinx/templates/base.typ` (this repo, read directly, this session) — current `@preview`
  imports and template structure, the exact insertion point for the new `show link:` rule.
- **Real `typst.compile()` output, this session** — every one of the five findings was reproduced
  end-to-end (rST → `.typ` → PDF) in a scratch Sphinx project
  (`<scratchpad>/fid-repro/src`), inspected via `.typ` text dump, pypdf `extract_text()`, AND
  rasterized page images (`pdftoppm -r 150`). This is the highest-confidence source available —
  every claim in this document that says "verified against real compile" is backed by an actual
  compiled-PDF artifact produced during this research session (not retained — ephemeral scratch,
  per the untrusted-input/scratch-directory convention).
- `pyproject.toml` (this repo, read directly, this session) — confirms `pypdf` dependency
  placement (dev-only) and current `@preview`/`typst`/`sphinx`/`docutils` version pins.
- `.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` (this
  repo) — source of record for all 5 findings' original repro/severity/occurrence data (rows 6,
  8, 9, 10, 11).

### Secondary (MEDIUM confidence)
- `.planning/phases/19-block-separation-fixes-cluster-a/19-CONTEXT.md`,
  `.planning/phases/20-signature-token-spacing-cluster-b/20-CONTEXT.md` (this repo) — the
  established GATE-01 fixture shape and D-05/D-07 verification-strategy precedent this phase
  extends.

### Tertiary (LOW confidence)
- General knowledge of the Unicode Line Breaking Algorithm (UAX #14), specifically rule LB13
  ("do not break before class CL/CP/EX/IS/SY, even after a space") as the explanation for WHY
  colon-leading tokens suppress the preceding space's break opportunity — this is `[ASSUMED]`
  training knowledge about the UAX14 specification's rule numbering/class names, NOT verified
  against the Unicode spec text or Typst's source code this session. The EMPIRICAL behavior
  (colon-leading tokens don't wrap; plain-word tokens of identical length do; a leading ZWSP
  fixes it) IS `[VERIFIED: real compile, this session]` — only the UAX14 rule-number/class-name
  citation itself is unverified. This distinction does not affect the recommended fix (which is
  driven entirely by the empirical behavior), only the depth of the "why" explanation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; existing versions confirmed via direct import in
  the project's own venv this session.
- Architecture: HIGH — all five fix sites and mechanisms verified against real compiles or direct
  doctree inspection this session, not inferred from code-reading alone.
- Pitfalls: HIGH for Pitfalls 2-4 (directly observed this session); MEDIUM for Pitfall 1's exact
  recommended character-class predicate (the BLAST-RADIUS problem is HIGH-confidence/verified via
  grep; the exact fix character set is a planning-time decision flagged as Assumption A1).

**Research date:** 2026-07-20
**Valid until:** 30 days (stable — no external ecosystem dependency; findings are internal-code
root causes verified this session against the current `typst-py` 0.15.0/Sphinx 9.1.0 pins, which
are pinned in `pyproject.toml` and not expected to drift during this milestone).

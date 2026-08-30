# Feature Research

**Domain:** Sphinx-to-Typst translator emitter defect (v0.9.2 milestone: `visit_image()` separator fix)
**Researched:** 2026-08-30
**Confidence:** HIGH (nearly every claim below is MEASURED against a real Sphinx build + real `typst.compile()`, not inferred from reading alone)

## Measurement provenance

All rows marked **MEASURED** were built and compiled on this machine, at HEAD
(`main`, unmodified — this is pre-fix behavior), as follows:

- Probe project: `/tmp/claude-1000/-home-yuta-Documents-typsphinx/f02be4ed-caf0-468a-897c-407113bde367/scratchpad/probe/src/` (conf.py + one `.rst` per scenario, all listed in one `typst_documents` registry with `<docname>-out` targets to satisfy the docname/target-collision rule).
- Build: `/home/yuta/Documents/typsphinx/.venv/bin/python -m sphinx -b typst -q src out` (run from the probe project root).
- Compile: for each `out/<docname>-out.typ` (the true master/wrapper file, template-applied, `#include()`-ing the content file — this is what `-b typstpdf` actually compiles), ran:
  ```python
  import typst
  typst.compile(f"out/{docname}-out.typ", root="out")
  ```
- Rows marked **INFERRED** are derived from reading `visit_image`/`depart_image`/`visit_figure`/`depart_figure`/`visit_paragraph`/`visit_list_item`/`visit_legend`/`add_text`/`_add_paragraph_separator`/`_emit_inline_concat_separator` in `typsphinx/translator.py` but were not independently built+compiled in this session (noted per-row why).

The pending todo's own 4-row matrix (`.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`) **reproduces exactly** — the `sub_mid_sentence` emission below is byte-identical to the todo's reproduction, and its FAIL verdict reproduces.

## Q1 — Failing shapes (exhaustive, by measurement)

The todo's 4-row matrix is a strict subset of what actually fails. **Extended finding: this is not four shapes, it is any image node anywhere in the doctree that is not literally the first thing on its output line** — the failure surface is much broader than "paragraph or list item," and includes shapes the todo never tested: table cells, definition-list bodies, admonitions, footnotes, field-list bodies, section titles, and a figure's own legend body. All of these fail for the exact same single root cause (`visit_image()` has no leading-separator check at all, unlike every sibling inline/block visitor), so a correct general fix (mirroring `visit_Text`'s triad: `_add_paragraph_separator()` / `_emit_inline_concat_separator()` / `in_list_item`+`list_item_needs_separator`) closes all of them at once — this is why the categorization in Q3 puts "extend the todo's matrix" under **table stakes**, not "nice to have."

| # | Shape | rST source (key lines) | Emitted Typst (key excerpt) | Compiles? | Status |
|---|-------|------------------------|------------------------------|-----------|--------|
| 1 | Substitution image mid-sentence | `.. \|sub\| image:: img.png` + `Inline substitution \|sub\| in a sentence.` | `par({text("Inline substitution ")image("img.png")\n\n\ntext(" in a sentence.")})` | **NO** — `TypstError: expected semicolon or line break` | MEASURED (reproduces todo row 2) |
| 2 | Two substitution images adjacent | `Two in a row \|sub\| \|sub\| here.` | `par({text("Two in a row ")image("img.png")\n\n\ntext(" ")image("img.png")\n\n\ntext(" here.")})` | **NO** (two independent unseparated boundaries in one paragraph) | MEASURED (reproduces todo row 3) |
| 3 | Image (substitution) inside a list item, mid-text | `- item with \|sub\| inline` | `list({\nparbreak()\n\ntext("item with ")image("img.png")\n\n\ntext(" inline")\n})` | **NO** | MEASURED (reproduces todo row 4) |
| 4 | **Block-level `.. image::` as 2nd element inside a list item** (new — not in todo) | `- First paragraph text.\n\n  .. image:: img.png` | `list({\nparbreak()\n\ntext("First paragraph text in the item.")image("img.png")\n\n\n})` | **NO** | MEASURED |
| 5 | Image inside a table cell (list-table) | `* - Cell text \|sub\| after text` | `{par({text("Cell text ")image("img.png")\n\n\ntext(" after text")})}` inside `table(...)` | **NO** | MEASURED |
| 6 | Image inside a definition-list body | `Term\n    Definition text \|sub\| after text.` | `terms.item(text("Term"), {par({text("Definition text ")image("img.png")\n\n\ntext(" after text.")})})` | **NO** | MEASURED |
| 7 | Image inside an admonition (`.. note::`) | `.. note::\n\n   First sentence here. \|sub\| trailing.` | `info({par({text("First sentence here. ")image("img.png")\n\n\ntext(" trailing.")})\n\n}, title: "Note")` | **NO** | MEASURED |
| 8 | Image inside a footnote body | `.. [#f1] Footnote text \|sub\| after text.` | `[#footnote({par({text("Footnote text ")image("img.png")\n\n\ntext(" after text.")})\n\n}) <...>]` | **NO** | MEASURED |
| 9 | Image inside a figure's legend, mid-text | `.. figure:: img.png\n\n   Caption.\n\n   Legend paragraph with \|sub\| inline.` | `[#figure({\n  image("img.png")\nparbreak()\n\ntext("Legend paragraph with ")  image("img.png")\ntext(" inline.")\n}, caption: {...}) <...>]` | **NO** | MEASURED — note the literal `"  "` (two-space) prefix `visit_image` always adds when `in_figure` is cosmetic indentation, not a line-break; it does not save this boundary |
| 10 | Two images adjacent inside a legend | `\|sub\| \|sub\| two subs in legend.` (as legend body) | `image("img.png")\ntext(" ")  image("img.png")\ntext(" two subs in legend.")` | **NO** | MEASURED |
| 11 | Image after inline **literal**, not plain text | `` Some ``literal text`` then \|sub\| after it. `` | `par({text("Some ")\nraw("literal text")\ntext(" then ")image("img.png")\n\n\ntext(" after it.")})` | **NO** | MEASURED |
| 12 | Image after **emphasis**, not plain text | `Some *emphasis text* then \|sub\| after it.` | `par({text("Some ")\nemph({text("emphasis text")})\ntext(" then ")image("img.png")\n\n\ntext(" after it.")})` | **NO** | MEASURED |
| 13 | Image after a **reference** (external link), not plain text | `` Some `external link <https://example.com>`_ then \|sub\| after it. `` | `par({text("Some ")\n[#link("https://example.com", \ntext("external link"))#label(...)]\ntext(" then ")image("img.png")\n\n\ntext(" after it.")})` | **NO** | MEASURED |
| 14 | **`:image:`-shaped field-list body** — a field body paragraph containing a substitution image | `:Returns: Some return text \|sub\| after text.` | `pad(left: 2.5em, {strong(text("Returns") + text(": "))\ntext("Some return text ")image("img.png")\n\n + text(" after text.")\n})` | **NO** | MEASURED — this is also a **concat-context** juxtaposition, not just a paragraph one; confirms `visit_image` also needs the `_emit_inline_concat_separator()` half of the fix, not only the paragraph half |
| 15 | **Substitution image inside a section title** (new — not in todo) | `Title Text \|sub\|\n=================` | `[#heading(depth: 1, {text("Title Text ")image("img.png")\n\n}) <...>]` | **NO** | MEASURED |
| 16 | Image with `:width:` **and** mid-sentence (dimensions do not change the verdict — the failure is entirely about the boundary *before* `image(`, not its arguments) | `.. \|sub\| image:: img.png\n   :width: 50px` + `Some text before \|sub\| and after.` | `par({text("Some text before ")image("img.png", width: 37.5pt)\n\n\ntext(" and after.")})` | **NO** | MEASURED |

**Blast radius, independently confirmed:** the probe's `index.rst` toctree `#include()`s every scenario document. `index-out.typ` **also failed to compile** even though `index.rst` itself contains no image — because Typst's `#include()` re-parses the included file at compile time, one bad content file poisons every master that transitively includes it. This directly corroborates the milestone framing ("no PDF for any master document in the project, not just the offending one") independent of the todo's own claim.

## Q2 — Shapes that must keep working unchanged (measured)

| # | Shape | rST source | Emitted Typst | Compiles? | Status |
|---|-------|-------------|----------------|-----------|--------|
| A | Standalone block-level `.. image::`, with text before and after | `Some text before.\n\n.. image:: img.png\n\nSome text after.` | `par({text("Some text before.")})\n\nimage("img.png")\n\npar({text("Some text after.")})` | **YES** | MEASURED |
| B | `.. figure::` (image indented 2 spaces inside `figure(` call) | `.. figure:: img.png\n\n   A caption.` | `[#figure(\n  image("img.png"),\n  caption: {text("A caption.")}\n) <...>]` | **YES** | MEASURED |
| C | Image first in its paragraph | `\|sub\| leading image then text.` | `par({image("img.png")\n\ntext(" leading image then text.")})` | **YES** | MEASURED (reproduces todo row 1) |
| D | Image with `:width:`/`:height:` (standalone, first in doc) | `.. image:: img.png\n   :width: 200px\n   :height: 100px` | `image("img.png", width: 150pt, height: 75pt)` | **YES** | MEASURED |
| D2 | Image with `:scale:`/`:align:` | `.. image:: img.png\n   :scale: 50%\n   :align: center` | `image("img.png")` — **`:scale:`/`:align:` are silently dropped, no kwargs emitted at all** | **YES** | MEASURED — confirms by code reading (no `"scale"`/`"align"` string anywhere in `translator.py`) and by build: these options have zero effect on emission today, so they cannot interact with this fix either way |
| E | Image with a propagated explicit target landing an id on it | `.. _mytarget:\n\n.. image:: img.png` | `[#metadata(none) <...:mytarget>]\nimage("img.png")` | **YES** | MEASURED |
| F | Figure that also has a legend, where the legend has **no image of its own** (plain legend text) | `.. figure:: img.png\n\n   A caption.\n\n   A plain legend paragraph, no images here.` | `[#figure({\n  image("img.png")\nparbreak()\n\ntext("A plain legend paragraph...")\n}, caption: {...}) <...>]` | **YES** | MEASURED |
| G | `.. figure::` nested inside a list item, after a preceding paragraph | `- First paragraph text.\n\n  .. figure:: img.png\n\n     Caption.` | `list({\nparbreak()\n\ntext("First paragraph text.")\n[#figure(\n  image("img.png"),\n  caption: {...}\n) <...>]\n\n\n})` | **YES** | MEASURED — `visit_figure` already has its own `in_list_item`/`list_item_needs_separator` check; this is why figures already survive this class of bug |
| H | `.. figure::` as the *first* element of a list item | `- .. figure:: img.png\n\n     Caption.` | `list({\n[#figure(\n  image("img.png"),\n  caption: {...}\n) <...>]\n\n\n})` | **YES** | MEASURED |
| I | Bare block `.. image::` as the *first* element of a list item (no preceding sibling) | `- .. image:: img.png` | `list({\nimage("img.png")\n\n\n})` | **YES** | MEASURED — confirms the rule is strictly "preceded by a sibling," not "inside a list item" |

**These 9+ shapes are the regression surface.** The general fix (mirroring `visit_Text`'s separator triad) must leave every one of these byte-identical, because each already relies on a DIFFERENT existing mechanism staying undisturbed: B/G/H rely on `visit_figure`'s own separator check (untouched by this fix); C/I rely on "nothing precedes me, so no separator flag is set" (also untouched); F relies on `depart_paragraph`'s existing `list_item_needs_separator = True` bookkeeping for the legend's own paragraph, which must still see a properly-updated flag after any image the fix touches.

## Q3 — Categorization

Owner-confirmed measurement (`PROJECT.md`, binding constraint #2) states that of fourteen inline constructs placed mid-sentence (`:ref:`, inline literal, emphasis, `:abbr:`, `:kbd:`, `:manpage:`, citation reference, `:term:`, `:index:`, `:guilabel:`, external link, footnote reference, `:math:`, `:download:`), the image is the *only* unseparated juxtaposition. **This reproduces.** A dedicated probe (`inline_construct_survey.rst`, all fourteen constructs placed mid-sentence in one document) was built and compiled: `out/inline_construct_survey-out.typ` compiled **OK**, and inspection of the emitted body confirms every one of the fourteen already emits either a real line break or a `+`-concat separator around itself (e.g. citation references and footnote references already start with a leading `\n[#footnote(...` / `\n[#link(...`, `:math:` already renders as `mi(...)`  on its own line, `:download:` as `raw(...)` on its own line). **No contradiction found; the milestone's "single site, not a class" framing holds.**

### Table Stakes (must be in v0.9.2)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `visit_image()` gains a leading-separator check mirroring `visit_Text`'s triad (`_add_paragraph_separator()` for paragraph context, `_emit_inline_concat_separator()` for concat context (field-list bodies, def-list terms), `in_list_item`/`list_item_needs_separator` fallback otherwise) | This is the actual bug; without it `-b typstpdf` produces zero PDFs for any project that places an image anywhere but the very start of its container | LOW | One function, ~10-15 lines added, follows an established pattern used ~15+ times elsewhere in the same file |
| After emitting, mark `list_item_needs_separator = True` when `in_list_item` (the "mark trailing" half of the same triad, currently entirely absent from both `visit_image`/`depart_image`) so a second image-then-non-image sibling (or vice versa) inside a list item/legend also separates correctly | Needed for rows 3, 4, 9, 10 above and to keep internal separator-flag bookkeeping consistent with every other visitor | LOW | Depends on the previous item (same PR/commit) |
| The separator decision must key off the *same flags* other visitors use (`in_paragraph`+`paragraph_has_content`, `in_list_item`+`list_item_needs_separator`, `_inline_concat_context()`) — **not** a blanket "insert `\n` unless `in_figure`" — so shapes B/C/D/E/G/H/I above stay byte-identical | A naive unconditional `\n` before every non-figure image would still be correct for the FAIL rows but is the wrong invariant to reason about; the todo itself already flags this ("mirror what the surrounding inline emitters... already do... rather than a bare unconditional `\n`") | LOW–MEDIUM | Depends on item 1; this is where a wrong implementation would silently break the two-space figure-indent shape or double-blank-line existing paragraphs |
| Real-`typst.compile()` regression gate covering, at minimum, the full measured set above — not just the todo's original 4+2 — since a correct general fix already makes all of rows 1-16 pass, and asserting on all of them is what actually proves generality vs. a shape-specific patch | The emitted string "looks plausible" per the todo — only the parser rejects it, so a string-only assertion is worthless; PROJECT.md's binding constraint already requires binding "all four measured failing shapes... and the two shapes that must keep passing," this research shows there are at least 16 failing + 9 passing worth binding | MEDIUM | Depends on the fix landing; test fixtures can be lifted near-verbatim from the probe `.rst` files enumerated in Q1/Q2 above |
| Update/close the pending todo (`2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`) with the extended matrix so the audit trail matches what was actually fixed | The todo's matrix undercounts the defect's true surface; leaving it as-is misrepresents what the regression gate proves | LOW | Documentation-only, no code dependency |

### Differentiators (nice, not required)

| Feature | Value Proposition | Complexity | Notes |
|---------|--------------------|------------|-------|
| A short doc-comment in `visit_image()` cross-referencing `visit_Text`'s triad by name (the way `_emit_forced_break`'s docstring cross-references its own precedent) | Makes the next person who touches this function find the established pattern instead of re-deriving it | LOW | Pure documentation; zero behavioral risk |
| A cheaper, non-compiling string-level regression test (regex for `)text\(...\)image\(` / `)image\(...\)image\(` juxtaposition shapes) run alongside the mandatory real-compile gate | Faster signal in environments where a full Typst compile is unavailable or slow | LOW | Strictly additive; the real-compile gate remains authoritative per PROJECT.md binding constraint #2 in the milestone context |
| Testing the `image_dimensions_mid_sentence` combination (width kwarg + preceded by sibling text) explicitly, beyond the baseline `image_with_dimensions` (dimensions alone, first in doc) | Confirms the fix's separator insertion happens strictly *before* `image(` and doesn't disturb the width/height kwarg-append logic that runs *after* it | LOW | Fixture already exists from this research; cheap to fold into the table-stakes test suite rather than treating as separate work |

### Anti-Features (must NOT be built this milestone)

| Feature | Why it looks appealing | Why it's out of scope / problematic | Alternative |
|---------|--------------------------|--------------------------------------|-------------|
| Auditing/fixing separator handling for the other fourteen inline constructs (`:ref:`, literal, emphasis, `:abbr:`, `:kbd:`, `:manpage:`, citation reference, `:term:`, `:index:`, `:guilabel:`, external link, footnote reference, `:math:`, `:download:`) | "While we're in here fixing juxtaposition bugs, why not fix the whole family?" | **Measured in this research** (`inline_construct_survey.rst`, real compile: OK) — none of these are broken. PROJECT.md is explicit: "this milestone fixes one emitter; it does not audit a family." Touching untested code paths in a one-defect patch release risks introducing new regressions with no reported symptom to justify the risk | Leave a note in the closed todo / a future backlog item if a NEW report ever surfaces a break in one of these; don't preemptively touch them |
| Adding `:scale:`/`:align:` image-option support | These options are visibly silently dropped right now (measured), and "fixing image handling" reads as an invitation to also fix this | Confirmed by code reading (no `"scale"`/`"align"` handling anywhere in `translator.py`) and by build (measured: zero effect on emission) to be a **completely unrelated feature gap** — it has no interaction with the juxtaposition defect (the failure is entirely about the boundary *before* `image(`, proven by row 16 above where `:width:` + mid-sentence still fails identically to no dimensions at all) | File as a separate backlog item if wanted; do not fold into this milestone |
| Refactoring the separator/concat-context machinery (`_add_paragraph_separator`, `_emit_inline_concat_separator`, `in_list_item`/`list_item_needs_separator`) into one unified helper used everywhere | The duplication across ~15 call sites is real and a legitimate future cleanup target | This milestone's binding constraint is explicitly "a single site, not a class" (D-constraint #2) — touching all 15 existing call sites to "unify" them is the opposite of a minimal, low-risk patch release fix, and risks regressing the 9+ MEASURED-passing shapes in Q2 | Leave as a separate refactor-scoped milestone/todo if pursued later |
| Changing figure/legend visual layout, indentation, spacing, or caption/legend styling while touching `visit_image`/`visit_figure` | The 2-space figure-body indent and the double-blank-line paragraph spacing look like incidental artifacts worth "cleaning up" while in the area | These are pre-existing, intentional, tested emission shapes (see Q2 rows B/F/G/H) with zero relationship to the defect; changing them is a byte-level regression against the existing test suite, not a fix | Out of scope; leave byte-identical |
| Inventing a new "does the output already end at a line boundary" introspection over `self.body` (e.g. checking the last character of `"".join(self.body)`) | Reads as more "obviously correct" than reusing flags, since it directly answers the stated question ("does the current output already end at a line boundary") | The existing flag-based machinery (`paragraph_has_content`, `list_item_needs_separator`, `_inline_concat_context()`) already answers this correctly for every other visitor and is what the fix must key off of (per the todo's own solution text); a from-scratch `self.body`-inspecting check would diverge from the established pattern, likely mis-handle the legend's cosmetic `"  "` indent (row 9 shows this literal is NOT a line boundary but also isn't flagged by any existing state), and introduce a second, parallel way of answering the same question elsewhere in the file | Reuse the existing flags exactly as `visit_Text` does |

## Feature Dependencies

```
[visit_image() leading-separator check]
    └──requires (same fix)──> [visit_image()/depart_image() trailing
                                list_item_needs_separator bookkeeping]
                                   └──must preserve──> [visit_figure()'s existing
                                                          in_list_item separator check
                                                          (Q2 rows B/G/H — untouched)]
                                   └──must preserve──> [depart_image()'s existing
                                                          trailing "\n\n" when not
                                                          in_figure (Q2 rows A/C/D/E —
                                                          untouched)]

[Real-compile regression gate over the full measured matrix]
    └──requires──> [the fix above landing first]

[Closing the pending todo with the extended matrix]
    └──requires──> [the fix + gate above being described accurately]
```

### Dependency Notes

- **The leading-separator check and the trailing-bookkeeping fix are one indivisible change**, not two phases: a leading-only fix would still leave `list_item_needs_separator` never set `True` after an image, which — while not itself causing a NEW compile failure today (because `depart_image`'s own unconditional `"\n\n"` already covers the immediate-next-sibling boundary in the non-figure case) — leaves the flag machinery internally inconsistent with every other visitor's pattern and is the direct cause of row 9/10's legend-internal failures, where `in_figure` is simultaneously true and the `in_list_item` reuse is what must fire.
- **The fix must not regress `visit_figure`'s own separator check.** `visit_figure` already independently implements the identical `in_list_item`/`list_item_needs_separator` pattern for the figure-as-a-whole (Q2 rows B/G/H). The image fix runs on the SAME flags but must not double-fire a separator when a figure already just cleared `list_item_needs_separator = False` right before visiting its own primary image (this is the mechanism that must be reasoned through, not merely tested — see the Anti-Feature entry above about not inventing a parallel introspection mechanism).
- **The regression gate cannot precede the fix.** A red-then-green TDD ordering is natural here (write the compile-gate tests against the CURRENT broken tree first, watch them fail with the exact `expected semicolon or line break` error, then land the fix and watch them turn green) — this is a single phase's natural internal ordering, not a cross-phase dependency.

## MVP Definition

### Launch With (v0.9.2)

- [ ] `visit_image()` leading-separator check (paragraph / concat-context / list-item triad) — the actual defect
- [ ] `visit_image()`/`depart_image()` trailing `list_item_needs_separator` bookkeeping — completes the same triad, needed for legend-internal and consecutive-image cases
- [ ] Real-`typst.compile()` regression gate over the full measured FAIL set (rows 1-16 above) and the full measured OK set (rows A-I above)
- [ ] Close/update the pending todo with the extended trigger matrix

### Add After Validation (not this milestone, but cheap if convenient)

- [ ] A faster string-level (non-compiling) regression check alongside the compile gate
- [ ] Explicit width+mid-sentence combination test (`image_dimensions_mid_sentence`)

### Future Consideration (explicitly out of scope, do not build now)

- [ ] Auditing the other fourteen inline constructs for the same defect class (measured clean; no known break to fix)
- [ ] `:scale:`/`:align:` image-option support (unrelated existing feature gap, silently dropped today)
- [ ] Unifying the separator/concat-context machinery into one shared helper (legitimate future refactor, wrong scope for a one-emitter patch release)

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|----------------------|----------|
| `visit_image()` separator fix (leading + trailing bookkeeping) | HIGH — currently blocks 100% of PDF output for any project with a mid-content image | LOW | P1 |
| Real-compile regression gate over the full measured matrix | HIGH — this is what makes the fix trustworthy at all, per PROJECT.md's own framing ("the emitted string looks plausible; only the parser rejects it") | MEDIUM | P1 |
| Todo closure with extended matrix | LOW (documentation) but blocks an honest audit trail | LOW | P1 (cheap, should ride along) |
| Faster string-level regression check | LOW-MEDIUM | LOW | P3 |
| `:scale:`/`:align:` support | MEDIUM (separate feature) | MEDIUM-HIGH (unscoped) | P3 (different milestone) |
| Inline-construct family audit | LOW (measured already clean) | MEDIUM (touches ~14 more call sites) | P3 (do not build absent a new report) |

## Sources

- `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` (`## Current Milestone: v0.9.2` section — binding constraints, scope fence)
- `/home/yuta/Documents/typsphinx/.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` (original 4-row matrix, reproduced and extended)
- `/home/yuta/Documents/typsphinx/typsphinx/translator.py` — `visit_image`/`depart_image` (~line 4718), `visit_figure`/`depart_figure` (~line 2915), `visit_legend`/`depart_legend` (~line 3135), `visit_paragraph`/`depart_paragraph` (~line 1410), `visit_list_item`/`depart_list_item` (~line 2373), `add_text`/`_add_paragraph_separator` (~line 887/933), `_emit_inline_concat_separator`/`_mark_inline_concat_content`/`_enter_inline_concat_element` (~line 1651), `visit_Text` (~line 1790, the template the fix should mirror)
- Probe project built and compiled in this session: `/tmp/claude-1000/-home-yuta-Documents-typsphinx/f02be4ed-caf0-468a-897c-407113bde367/scratchpad/probe/` (24+ scenario `.rst` files, one Sphinx project, built with `sphinx -b typst`, each master compiled with `typst.compile(..., root="out")` via the main-tree `.venv`)

# Phase 39: Admonition Taxonomy + Rubric Nesting - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Make every admonition land in the colour bucket its type implies, give the generic
`.. admonition::` and `.. topic::` a real styled box instead of the bare base `clue`, prove the four
buckets stay apart in greyscale, and settle what the `rubric` handler owes now that Phase 38's
indent already carries it.

**In scope** — the handlers that pick the clue function and the rubric's own emission:

- `_visit_admonition` / `_depart_admonition` (`typsphinx/translator.py:4337, 4373`) — the shared
  helper that emits `{clue_type}({` … `}, title: …)`.
- Every per-type visitor that names a clue function: `visit_note` (4401), `visit_warning` (4409),
  `visit_tip` (4417), `visit_important` (4425), `visit_caution` (4433), `visit_seealso` (4441),
  `visit_hint` (4449), `visit_todo_node` (4461), `visit_error` (4493), `visit_danger` (4501),
  `visit_attention` (4509), `visit_admonition` (4522), `visit_topic` (4538).
- `visit_rubric` / `depart_rubric` (`typsphinx/translator.py:5767, 5833`) and the three shared
  single-slot save attributes they read/write with `visit_strong` / `depart_strong` (1429, 1474) and
  `visit_desc_signature` / `depart_desc_signature`.
- `pyproject.toml`'s `[dev]` extra (D-06 adds `pillow`).
- The admonition/rubric halves of `tests/test_admonitions.py`, `tests/test_topics.py`,
  `tests/test_pdf_render_gate.py`, and the five rubric-touching test modules and five fixtures.

**Out of scope:**

- `SHARED_INDENT_STEP` (`typsphinx/translator.py:29`) and the `pad(left: …)` wrapper Phase 38 put
  around `desc_content` — the rubric consumes it, it does not re-define it. Phase 38 D-01/D-02 stand.
- `block_quote` — Phase 38 D-04 recorded it as an intentional non-consumer of the indent. Do not
  re-open it here.
- `desc_signature` and its inline children — Phase 37 owns them and is complete. The rubric's
  handler shares attribute names with `visit_desc_signature`'s copy (Phase 36 D-02), so a fix must
  not change `desc_signature`'s emitted bytes.
- The box-less `.. contents::` topic path — locked by the v0.6.x D-05 decision; TOP-01 (boxing the
  local TOC) stays deferred.
- Citations — Phase 40.
- User-overridable styling — dropped from v0.7.0 at scoping.

</domain>

<decisions>
## Implementation Decisions

Every value cited below was measured **this session (2026-08-02)** by four means, none from recall:

1. reading `sphinx.sty` (Sphinx 9.1.0, `.venv/lib/python3.13/site-packages/sphinx/texinputs/`) for
   the authoritative bucket taxonomy and its RGB palette;
2. reading the pinned gentle-clues 1.3.1 sources in the Typst package cache
   (`~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/{clues,theme,predefined}.typ`,
   `lang.toml`, `assets/*.svg`);
3. real `sphinx-build -b typst` and `-b typstpdf` runs over hand-written probe projects, with left
   edges read back through `pypdf`'s `visitor_text` (`cm[4] + tm[4]`);
4. a real `sphinx-build` with `language = "ja"` that printed `sphinx.locale.admonitionlabels` from an
   `env-before-read-docs` hook.

### The bucket taxonomy — ADM-01, ADM-02

Measured from `sphinx.sty` (Sphinx's own four title-band groups, lines 819–860):

| Sphinx bucket | title bg / fg | Sphinx types in it |
|---|---|---|
| note | `#d0defa` / `#145dea` | `note` |
| success | `#dcefe6` / `#51ae80` | `hint`, `tip`, `seealso` |
| warning | `#f8e4d2` / `#dd7a21` | `important`, `caution`, `warning` |
| error | `#eedcdc` / `#ae5050` | `attention`, `danger`, `error` |

- **D-01: a bucket is a gentle-clues function; its colour is that function's default.** No
  `accent-color:` is ever passed. Measured defaults from `theme.typ`: `info` `#04a5e5`, `tip`
  `#179299`, `warning` `#df8e1d`, `error` `#d20f39`. The Sphinx palette above is the taxonomy source
  only, never the colour source. Rejected alternative: pinning Sphinx's four RGB values through
  `accent-color:` — it decouples from the package theme but puts a colour literal on every emitted
  admonition and enlarges the exact-string migration.
- **D-02: the success bucket is `tip` (teal `#179299`), not `success` (green `#40a02b`).** `hint` and `tip` already emit `tip(…)`, so ADM-01 is discharged by moving `seealso` into it. ADM-01's parenthetical "(green 'success')" names Sphinx's bucket, not a required Typst colour; the teal stays.
- **D-03: `danger` folds into `error` too.** Measured: today `danger` emits `danger(…)` = peach `#fe640b` while `error` emits `error(…)` = red `#d20f39`, so "the same bucket as danger/error" is not well-defined against pre-phase code. Collapsing `attention`, `danger` and `error` onto `error(…)` makes the red bucket a single function, which is what ADM-02 asserts.
  **Superseded 2026-08-02 under gap G-39-1.** See "Reversal — recorded 2026-08-02 (gap G-39-1)" below and decision **D-03-R**: the red family stays a family of three distinct clue functions rather than one collapsed `error()` call.

Resulting bucket table (this is the contract the planner implements). **The `error` row is superseded 2026-08-02 under gap G-39-1** — see the reversal section below for the red family's replacement table. The `note`, `success` and `warning` rows are unchanged and still in force:

| Bucket | Function | accent (measured) | Sphinx types routed to it |
|---|---|---|---|
| note | `info` | `#04a5e5` | `note` |
| success | `tip` | `#179299` | `hint`, `tip`, `seealso` |
| warning | `warning` | `#df8e1d` | `warning`, `caution`, `important` |
| error | `error` | `#d20f39` | `attention`, `danger`, `error` |
| (outside the four) | `task` | `#8839ef` | `todo_node` — unchanged |
| (outside the four) | `notify` | `#1e66f5` | generic `.. admonition::` — D-07 |
| (outside the four) | `abstract` | `#209fb5` | `.. topic::` — D-08 |

### Admonition titles — a direct consequence of folding

Folding functions folds gentle-clues' default titles with them (`_predefined-clue` derives the title
from the function id through linguify), so `.. danger::` would have shown "Error".

- **D-04: titles come from `sphinx.locale.admonitionlabels`, passed as `custom_title`.** Measured live: in a real build with `language = "ja"` the catalog resolves to Japanese with no extra `locale.init` call — `{'attention': '注意', 'caution': '注意', 'danger': '危険', 'error': 'エラー', 'hint': 'ヒント', 'note': '注釈', 'seealso': '参考', 'tip': 'Tip', 'warning': '警告', 'important': '重要'}`. This is the same source Sphinx's own HTML and LaTeX builders use.
- **D-05: apply it to all ten types, not only the ones whose folded default drifts.** One source of truth for the header text; typsphinx's admonition titles then match every other Sphinx builder. Two measured costs the planner must accept, not treat as bugs: (a) in `ja`, `.. tip::` regresses from gentle-clues' 「ヒント」 to the catalog's untranslated "Tip", and `.. note::` moves from 「情報」 to 「注釈」; (b) `seealso`'s literal changes from `"See Also"` to the catalog's `"See also"`. Every admonition's emitted string changes, so the migration covers `tests/test_admonitions.py` (18 clue-call assertions), `tests/test_topics.py` (3) and `tests/test_pdf_render_gate.py` (4) in full.

Note: `todo_node` is not in `admonitionlabels` (`sphinx.ext.todo` carries its own `_('Todo')`), and it
already receives its real title from the node's own `title` child via the `visit_title` buffer swap —
the static `custom_title="Todo"` is an inert fallback. Leave that path alone.

### Greyscale distinguishability — ADM-04 (the milestone's only `[V]`)

Measured luminances (`0.2126R + 0.7152G + 0.0722B` over sRGB), header band = `accent.lighten(85%)`
exactly as `clues.typ` derives it:

| Bucket | accent L | header band | band L |
|---|---|---|---|
| note (`info`) | 53.1% | `#d9f2fb` | 93.1% |
| success (`tip`) | 47.2% | `#dceff0` | 92.2% |
| warning (`warning`) | 59.2% | `#faeedd` | 93.9% |
| error (`error`) | 23.3% | `#f8dbe1` | 88.5% |

The bands span **5.4 percentage points** — this reproduces exactly the defect ADM-04 states. The left
stroke (2pt, accent at full saturation) spans **35.9 points**, and the four icons differ by *shape*
(`info.svg` "i", `tip.svg`, `warning.svg` triangle-!, `crossmark.svg` ✕). Icons carry baked-in fills
(`#1074c6`, `#ffcc4d`, `#dd2e44`) and are **not** tinted by `accent-color`.

- **D-06: no styling change is made for ADM-04.** The claim to prove is that the icon shapes plus the existing 2pt accent stroke already carry the distinction, which is precisely what ADM-04 says must carry it ("icon and border, not hue alone"). Rejected alternatives, both available if UAT rejects: per-bucket `stroke-width:` and per-bucket `header-color:`. `clue()`'s left edge is `(thickness:, paint:, cap:)` — **a dashed stroke cannot be specified**, so that lever does not exist.
- **D-07: the greyscale render is produced with Pillow, added to `pyproject.toml`'s `[dev]` extra.** `typst.compile(input, format="png", ppi=…)` rasterises (typst-py 0.15.0, signature verified); `Image.open(…).convert("L")` desaturates. Measured: **PIL, numpy, ImageMagick, ghostscript, `pdftoppm` and `mutool` are all absent** from this environment, so no zero-dependency path exists except hand-rolling a PNG codec on zlib+struct, which was rejected as verification cost with no product value. Desaturating inside Typst is measurably impossible — the icons' colours are baked into the SVGs and `accent-color` does not reach them. The render and the owner's sign-off are committed as phase artifacts.
- **D-08: no fallback lever is pre-agreed.** If the owner cannot distinguish the four kinds from the greyscale render, the lever is chosen then, against the actual render. The phase is expected to stop at that UAT checkpoint if that happens.

### Generic `.. admonition::` and `.. topic::` — ADM-03

Measured pre-phase state: both route through `_visit_admonition(node, "clue")` and emit
`clue({…}, title: {text("…")})`. **The title is already emitted** — the gap ADM-03 names is the
styling: `clue`'s default `accent-color` is navy `#000080` (band `#d9d9ec`, L 85.6%) and its `icon`
defaults to `none`. Sphinx puts both under its neutral grey title band; gentle-clues 1.3.1 has **no
grey clue** (all 18 predefined clues are chromatic), so matching Sphinx's grey would require the
colour literal D-01 rules out.

- **D-09: the generic admonition directive emits `notify(…)`** — `.. admonition::` gets accent `#1e66f5`, band `#dde8fe` (L 90.7%), `bell.svg`. Its default title never surfaces because the directive always supplies its own. Rejected: `memo` (`#e64553`, `excl.svg`) — measured too close to the error bucket in both hue and band luminance (91.1% vs 88.5%) and its "!" icon reads as a warning; `abstract` — reserved for topic by D-10; `idea` — measured **identical** to the warning bucket (`#df8e1d`, band `#faeedd`), distinguishable only by icon.
- **D-10: the topic directive emits `abstract(…)`** — `.. topic::` gets accent `#209fb5`, band `#def1f4` (L 93.0%), `abstract.svg` (a document). The document icon matches "a self-contained aside lifted out of the body", and it separates topic from the generic admonition, which Sphinx also treats as distinct. Accepted cost: `#209fb5` sits near the success bucket's teal `#179299` (accent L 52.4 vs 47.2; band 93.0 vs 92.2) — acceptable because topic is not one of the four kinds SC#4 judges. Consequence: `_visit_admonition`'s callers split into two, and the base `clue` function disappears from the codebase entirely (the box-less `.. contents::` path is untouched).

### Rubric — ADM-05 / SC#3

**Measured: ADM-05 already holds.** A real `-b typstpdf` build of a probe with a `py:class::`
containing a `py:method::`, each carrying a `.. rubric::`, read back through `pypdf`:

| Site | x |
|---|---|
| page margin | 70.87pt |
| class `desc_content` body | 98.37pt |
| `Options` rubric inside the class body | **98.37pt** |
| nested method `desc_content` body | 125.87pt |
| `Notes` rubric inside the method body | **125.87pt** |
| top-level rubric (no container) | 70.87pt |

Phase 38's `pad(left: SHARED_INDENT_STEP, …)` already carries the rubric; the rubric needs — and gets
— no indent rule of its own, exactly as ADM-05 words it.

- **D-11: the phase asserts ADM-05 and additionally folds the two known rubric defects.** Assertion-only was rejected: `visit_rubric`'s own docstring records the double-blank-line wart as "Phase 39 owns the repair", and the pending todo below is filed with `resolves_phase: 39`.
- **D-12: SC#3's indentation claim becomes an invariance guard, and ROADMAP.md SC#3 is corrected to say so.** A RED cannot be recorded against pre-phase code because the property already holds — the same situation Phase 36's SC#3 hit, resolved the same way (see ROADMAP.md "Roadmap Evolution", Phase 36 edit). The phase's classic RED comes from the folded todo instead (measured below), so the milestone's GATE-01 bar is still met by real evidence, not by a waiver.
- **D-13: the RED fixture for the rubric half is the `par()` drop.** Measured on a real `-b typst` build: a `.. rubric:: A **bold** rubric` emits `strong({text("A ") strong({text("bold")}) text(" rubric")})`, after which **every subsequent paragraph in the document** emits a bare `text("…")` instead of `par({text("…")})`, to the end of the file. Assert `par({text("First paragraph after the rubric.")})` — red today, green after the fix.

### Test migration — SC#5

- **D-14: the blast-radius census recorded at discussion time is the starting point, and must be re-taken at planning time rather than trusted.** Measured 2026-08-02: admonition emission assertions live in `tests/test_admonitions.py` (18 clue calls), `tests/test_topics.py` (3), `tests/test_pdf_render_gate.py` (4); rubric is referenced by `tests/test_desc_rubric_decoupling_render_gate.py`, `tests/test_rubric_option_concat_render_gate.py`, `tests/test_rubric_propagated_target_render_gate.py`, `tests/test_signature_typography_multi_signature_page_count_gate.py`, `tests/test_translator.py` and five fixtures under `tests/fixtures/` (`desc_rubric_decoupling_render_gate`, `rubric_option_concat_render_gate`, `rubric_propagated_target_render_gate`, `footnote_render_gate`, `signature_typography_gate`). Expected strings are re-derived by hand, never by copying failing output.

### Claude's Discretion

- How the `admonitionlabels` lookup is threaded into `_visit_admonition` (a module-level mapping from
  node class name to catalog key, versus a `custom_title` at each call site) — an implementation
  shape, not a decision.
- Escaping of the title inside the emitted Typst string literal now that titles can be non-ASCII.
- Which real API page SC#3's autodoc "Options" measurement is taken from.
- The greyscale render's PPI, page selection and file naming.

### Folded Todos

- **`.planning/todos/pending/2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md`**
  (`resolves_phase: 39`) — `visit_strong`, `visit_rubric` and `visit_desc_signature` each hold their
  own verbatim copy of the same save/restore body and, per Phase 36 D-02, deliberately share the
  three single-slot attributes `_strong_was_in_paragraph`, `_strong_was_in_list_item`,
  `_strong_was_list_item_needs_separator`. A real `strong` child inside a rubric consumes and deletes
  all three before the outer `depart_rubric` restores, so `in_list_item` stays `True` for the rest of
  the document. Folded because it is a defect in the handler this phase owns and it supplies the
  phase's classic RED (D-13). Any fix must keep `desc_signature`'s emitted bytes unchanged (Phase 37
  is complete and its golden file is a fixed point).
- The double-blank-line wart recorded inline in `visit_rubric`'s docstring
  (`typsphinx/translator.py:5781-5787`): a rubric carrying a propagated target inside a list item
  runs the leading-separator check twice on top of an unconditional newline. Not filed as a separate
  todo; folded by D-11 because the docstring names Phase 39 as its owner.

### Reversal — recorded 2026-08-02 (gap G-39-1)

**This is a deliberate design reversal by the owner, made after a live A/B/C render comparison
shown during UAT — it is not a defect repair.** D-03 above was a correct implementation of what
ADM-02 asked for at the time it was written; the owner is now asking for something different,
having seen the folded red bucket rendered. The owner's three messages are quoted verbatim below
from `39-UAT.md`'s `reason` field, each followed by an accurate English rendering that preserves
the nuance rather than paraphrasing it away, following the same discipline `39-ADM04-SIGNOFF.md`
§4 uses for a recorded owner verdict elsewhere in this phase.

**Message 1:**

> 「うわ、デンジャーはgentle-clueのデンジャーに振った方が良かったかも」

English rendering: *"Oh — maybe it would have been better to route `danger` to gentle-clues' own
`danger` [function] after all."* (An exclamation of realization, followed by second-guessing the
D-03 fold specifically for `danger`.)

**Message 2:**

> 「Bでもっかい再構成しないとまずいな」

English rendering: *"I need to restructure this again with option B, or it's going to be a
problem."* (もっかい = もう一回, "one more time"; まずいな carries "that would be bad/not good,"
i.e. leaving it as-is is unacceptable — this is the moment the reversal becomes a decision rather
than a passing thought.)

**Message 3:**

> 「Attentionはgentle-cleuのmemoにすっか」

English rendering: *"Let's make `attention` [go to] gentle-clues' `memo` [function]."* (すっか is a
casual contraction of する か, "shall we/let's do [it]" — the owner extending the same reversal
from `danger` to `attention` after being shown Sphinx's own per-type icon assignment.)

- **D-03-R: the red family sub-divides into three distinct clue functions.** All three red-family
  types stay in the red family; each gets its own gentle-clues function rather than being
  collapsed onto one. The mapping: `danger` routes to the package's own `danger` id (function
  `danger(...)`), `attention` routes to the package's `memo` id (function `memo(...)`), and `error`
  is unchanged (function `error(...)`). D-01's rule — a bucket is expressed as a function name,
  never as a colour argument — is explicitly **NOT** reversed by D-03-R; only the cardinality of
  the red bucket changes, from one function to three.

Red-family table (measured 2026-08-02 from the installed
`~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/theme.typ`; the accent column is measured
provenance for this record, never an emitted value — D-01 stands, no `accent-color:` argument is
passed anywhere):

| Sphinx type | Clue function | accent (measured provenance) | icon (measured) | Requirement served |
|---|---|---|---|---|
| `danger` | `danger` | `#fe640b` (peach) | `danger.svg` | ADM-02 |
| `attention` | `memo` | `#e64553` (maroon) | `excl.svg` | ADM-02 |
| `error` | `error` | `#d20f39` (red) | `crossmark.svg` | ADM-02 |

Two measured facts bound the change and are recorded here rather than assumed: all three
`@preview` import sites (`typsphinx/writer.py:158`, `typsphinx/template_engine.py:615`,
`typsphinx/templates/base.typ:19`) already use the wildcard form
`#import "@preview/gentle-clues:1.3.1": *`, so both `danger` and `memo` are already in scope and
no pin moves — `tests/test_preview_version_sync.py`'s three-surface (plus `examples/`) check is
unaffected. gentle-clues supplies its own linguify default title for every predefined id it ships,
including `memo` (`en` = "Memorize"), so the `sphinx.locale.admonitionlabels` `custom_title` path
from D-04/D-05 must keep winning over both new ids' defaults, exactly as it already does for
`danger`/`error`/`note`/etc. `39-UAT.md`'s `measured_context` claimed the `memo` id has no
Japanese entry and falls back to `en` — that claim is **wrong**: the installed `lang.toml` carries
a `[lang.ja]` block with `memo = "覚える"` (line 168 of
`~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/lang.toml`, read directly this session).
This does not change what typsphinx emits, since `custom_title` already overrides gentle-clues'
own titles for every predefined id — but the record should state the measured value rather than
repeat the UAT's incorrect claim.

**What this reversal does NOT touch:** ADM-01's success bucket, the warning group, ADM-03's
generic-admonition (`notify`) and topic (`abstract`) routing, ADM-05's rubric work, and D-04/D-05's
`sphinx.locale.admonitionlabels` title source. All of those stand exactly as recorded above.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` § "Phase 39: Admonition Taxonomy + Rubric Nesting" — the five success
  criteria. **SC#3 is corrected by D-12**; treat the current wording as superseded.
- `.planning/REQUIREMENTS.md` §"Admonitions, rubric, and topic (ADM)" (lines 106–129) — ADM-01..ADM-05
  verbatim, plus ADM-06 marked complete.
- `.planning/STATE.md` § "Operator Next Steps" — records that Phase 39 must consume
  `SHARED_INDENT_STEP` rather than a private literal, that ADM-04 is a real human UAT checkpoint, and
  that `/gsd-plan-phase 39` must pass `--skip-ui`.

### Upstream phase decisions this phase must not re-open
- `.planning/phases/38-structural-indentation-info-fields/38-CONTEXT.md` — D-01 (the `pad(left: …)`
  around `desc_content`, and that no depth counter exists), D-02 (`SHARED_INDENT_STEP` stays
  `"2.5em"`), D-04 (`block_quote` is an intentional non-consumer; settled by owner ruling, do not
  re-open).
- `.planning/phases/36-shared-emission-seam-cleanup/36-CONTEXT.md` — D-01 (the triplication of
  `visit_strong`'s body is the decision, not an accident) and D-02 (the three `_strong_was_*`
  attribute names are shared on purpose). Both bear directly on the D-11/D-13 fix.
- `.planning/phases/37-signature-typography-the-desc-family/37-EMISSION-CONTRACT.md` — the signature
  emission shape a rubric fix must not disturb.

### External sources measured for this phase
- `.venv/lib/python3.13/site-packages/sphinx/texinputs/sphinx.sty` lines 281–309 and 819–869 — the
  authoritative four-bucket taxonomy and its RGB palette.
- `~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/theme.typ` — every predefined clue's accent
  colour and icon file.
- `~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/clues.typ` — `clue()`'s full parameter list
  and how `header-color` is derived (`accent.lighten(85%)`); confirms no dashed-stroke lever exists.
- `~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/lang.toml` — the linguify title catalog that
  D-04/D-05 deliberately stop relying on.
- `sphinx.locale.admonitionlabels` — the title source D-04 adopts.

### Project conventions
- `CLAUDE.md` § "The `@preview` version-sync hazard" — `gentle-clues` is pinned in three places plus
  `examples/` and `docs/source/_typst/custom_template.typ`. This phase does not bump the pin, but any
  planner touching the import line must know.
- `CLAUDE.md` § "Worktree-isolated execution" — worktree isolation is the standing execution mode;
  per-worktree `uv sync --extra dev` + `uv run` are mandatory. **D-07 adds `pillow` to that extra**,
  so worktrees must re-sync.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `_visit_admonition(node, clue_type, custom_title=None)` / `_depart_admonition()`
  (`typsphinx/translator.py:4337, 4373`) — every admonition already funnels through one helper that
  emits `{clue_type}({` and closes with `}, title: {expr})`. Both the bucket re-routing (D-01..D-03)
  and the title change (D-04/D-05) are changes to *what is passed in*, not to the emission mechanism.
- The `visit_title` / `depart_title` buffer swap (`typsphinx/translator.py:599-690`) already defers a
  node-supplied admonition title into `_pending_admonition_title`, and `_depart_admonition` prefers it
  over `custom_title`. The generic `.. admonition::` and `.. topic::` titles ride this path today and
  need no new plumbing for ADM-03.
- Phase 38's `pad(left: SHARED_INDENT_STEP, { … })` around `desc_content` — already measured to carry
  the rubric (see D-11). Nothing new is needed for ADM-05's mechanism.

### Established Patterns

- **A bucket is expressed as a function name, never as a colour argument** (D-01). Emitted admonitions
  stay short and carry no colour literals.
- **Deliberate triplication** (Phase 36 D-01): `visit_strong`, `visit_rubric` and
  `visit_desc_signature` each carry their own copy of the same body. The D-11 fix must not
  "refactor away" the duplication — it must break the *shared attribute slots* (Phase 36 D-02) without
  changing `desc_signature`'s emitted bytes.
- **GATE-01 (v0.7.0 amendment):** structural / regex / `pypdf` RED defined before any code, except
  where the property already holds — then an invariance guard, per Phase 36's SC#3 precedent (D-12).
- Non-regression is proven by re-running the full-corpus `-b typstpdf` gate
  (`tests/test_corpus_gate.py`) green after the change (SC#5).

### Integration Points

- `pyproject.toml` `[project.optional-dependencies] dev` — D-07 adds `pillow`. Runtime dependencies
  are untouched.
- `tests/test_preview_version_sync.py` watches the `gentle-clues` pin across `writer.py`,
  `template_engine.py`, `templates/base.typ` and `examples/**/*.typ`. This phase changes which clue
  *functions* are called, not the pin, so the sync test should stay green — confirm, do not assume.
- The `@preview` import is a wildcard (`#import "@preview/gentle-clues:1.3.1": *`), so `notify` and
  `abstract` are already in scope with no import change.

</code_context>

<specifics>
## Specific Ideas

- The owner rejected `memo` for the generic admonition after seeing the measured proximity to the
  error bucket, and rejected `idea` for topic after seeing that its accent is byte-identical to the
  warning bucket's. The standing preference this reveals: **a new box's colour must be measurably
  clear of every colour already in use**, checked before it is proposed — not justified afterwards.
- The owner chose the Sphinx translation catalog over both the hard-coded English strings and
  gentle-clues' own linguify titles, accepting the measured `ja` regression on `.. tip::`. Matching
  Sphinx's other builders beat preserving one better Japanese string.

</specifics>

<deferred>
## Deferred Ideas

- **`.. tip::`'s Japanese title.** D-05 accepts a measured regression: Sphinx's `ja` catalog leaves
  `tip` untranslated ("Tip") where gentle-clues has 「ヒント」. Restoring it would mean overriding the
  catalog for one type — a translation-quality question, not a taxonomy one, and arguably an upstream
  Sphinx locale contribution.
- **A neutral grey bucket.** Sphinx renders the generic admonition and `.. topic::` on a neutral grey
  band; gentle-clues has no grey clue, so matching it needs an explicit colour literal that D-01 rules
  out. Revisit only if the "no colour literals" rule is ever relaxed.
- **TOP-01** (boxing the `.. contents::` local TOC) — already deferred at v0.7.0 scoping; the
  box-less path stands.

### Reviewed Todos (not folded)

- `2026-07-22-citation-node-support-untracked.md` — belongs to Phase 40 (CIT-01..CIT-06); matched only
  on generic keywords.
- `2026-07-29-release-notes-body-from-changelog-section.md` — belongs to Phase 41 (REL-04).
- `2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md` — `depart_desc`'s break
  bookkeeping, a Phase 37/38 seam. Not folded: this phase does not touch `desc_signature` emission,
  and folding it would put Phase 37's completed golden file back in play.
- `2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md` — a Phase 37 test-naming
  defect, not an admonition or rubric concern.
- `2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md` — `visit_desc_sig_name`
  docstring hygiene; a `desc_*` handler this phase does not open.
- `2026-07-25-derive-typst-lang-duplicated-warning-block.md` — `template_engine`, unrelated.
- `2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md` — builder input hardening, unrelated.
- `2026-07-29-project-md-unterminated-html-comments.md` — planning-doc hygiene, unrelated.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — deferred as Future requirement LNK-01.

</deferred>

---

*Phase: 39-Admonition Taxonomy + Rubric Nesting*
*Context gathered: 2026-08-02*

# Architecture Research — v0.6.3 Integration Map

**Domain:** Sphinx→Typst translator (docutils visitor pipeline), maintenance milestone
**Researched:** 2026-07-23
**Confidence:** HIGH (every claim below is a direct line-cited read of the current `main` tree at commit `9f8e075`, not an external/inferred source)

This document supersedes the 2026-07-11 (v0.6.0) `ARCHITECTURE.md` in this file for the current v0.6.3 milestone. It is not a greenfield "what should the architecture be" doc — it is a precise **integration map** for two v0.6.3 code changes against the existing `typsphinx` pipeline (doctree → `TypstTranslator` → body string → `TemplateEngine` → `.typ`), so a planner can slot the changes in without breaking the state machines already load-bearing in `translator.py`/`writer.py`/`template_engine.py`.

## 1. Captioned-table figure wrap — current control flow

### 1.1 `visit_title`/`depart_title` (`typsphinx/translator.py:453-584`)

**Existing branches, in dispatch order (`visit_title`, line 453):**

1. **Universal entry save (453-480):** every title, regardless of context, saves `self._title_was_in_list_item` / `self._title_was_list_item_needs_separator` and forces `self.in_list_item = True; self.list_item_needs_separator = False` for its own children (Pitfall-1 fix — a title's Text/emphasis/strong children need the list-item newline-separator idiom or they run together with no separator). **This save/restore happens on EVERY return path** — it is the first thing that runs and the state-var pair is the one and only thing every branch below must restore before returning.
2. **Admonition/topic branch (487-503):** `isinstance(node.parent, nodes.Admonition) or isinstance(node.parent, nodes.topic)` → buffer-swap: `self._saved_body_for_admonition_title = self.body; self.body = []; self._in_admonition_title = True; return`. A `.. contents::` topic additionally records `self._contents_title_insert_at = len(self.body)` for later re-insertion above the toctree bullet list.
3. **Section-heading branch (505-529, the fallthrough/default):** computes `self._title_section_ids` from `node.parent.get("ids")` (only non-empty when `node.parent` is `nodes.section`), clamps `emitted_level = max(1, self.section_level)`, and emits `heading(level: N, {` (bracket-wrapped `[#heading(...)` when the section carries ids, for the anchor postfix).

**`depart_title` (531-584)** mirrors: if `self._in_admonition_title`, captures `"".join(self.body)` as `self._pending_admonition_title`, restores `self.body`, restores the `in_list_item`/`list_item_needs_separator` pair, and returns (534-562, with the contents-topic insert-at-index special case). Otherwise (section-heading path) it closes `heading(...)`, emits the anchor `<label>` postfix if `self._title_section_ids` is non-empty, and — critically — **also** restores `in_list_item`/`list_item_needs_separator` at the very end (582-584), unconditionally, for this branch too.

**Where a table-caption branch must slot in:** as a **third branch**, parallel to admonition/topic, distinguished the same way (`isinstance(node.parent, nodes.table)` — a docutils `.. table:: Caption` directive inserts a `title` node as the table's first child, so `node.parent` is `nodes.table`; confirmed empirically against `9f8e075` in the driving todo). It must:

- Run the buffer-swap idiom exactly like the admonition-title branch (`_saved_body_for_..._title = self.body; self.body = []`), **not** `node.astext()` (loses inline markup/escaping).
- Also mirror `depart_caption`'s figure-caption idiom (`translator.py:2166-2210`) by establishing a paragraph-separator context for multi-child inline content: save `in_paragraph`/`paragraph_has_content`, force `in_paragraph = True; paragraph_has_content = False` for the duration of the buffered children, restore on depart. Without this, sibling inline nodes inside the caption (e.g. `text(...)` next to `emph(...)`) juxtapose with no separator — the same class of Typst parse fatal ("expected semicolon or line break") FIG-02/D-Disc-1 already fixed for figure captions.
- **Return early**, bypassing the section-heading `heading()` emission entirely — this is the actual bug being fixed (currently the table-caption title falls through to branch 3 because it matches neither `Admonition` nor `topic`).
- Restore `in_list_item`/`list_item_needs_separator` from the universal entry-save (step 1 above) on both the new visit-branch-taken-early-return and the new depart-branch, exactly like the admonition-title branch already does — **do not** rely on the section-heading branch's restore at the tail of `depart_title` (582-584), since the new branch must `return` before reaching it, same as the admonition branch does.

**Flagged risk — buffer-state clobber (footnote-phase precedent):** v0.6.0 Phase 14's footnote buffer-swap hit exactly this class of bug — the buffer-swap clobbered the OUTER paragraph's `in_paragraph`/`paragraph_has_content` separator state, aborting any footnote followed by trailing text, and had to be fixed with the file's own save/restore convention (see `PROJECT.md` Phase 14 entry: "the buffer-swap clobbered the outer paragraph's `in_paragraph`/`paragraph_has_content` separator state"). The new table-caption branch touches the SAME two state vars (`in_paragraph`/`paragraph_has_content`) for the SAME reason (establishing a paragraph-like separator context inside a buffer). **The planner must write an explicit save/restore pair for `in_paragraph`/`paragraph_has_content` around the table-caption buffer**, using local instance-attribute names distinct from `_caption_was_in_paragraph`/`_caption_was_paragraph_has_content` (those belong to `visit_caption`/`depart_caption`) — matching the file's existing one-buffer-one-name-pair convention (e.g. `_saved_body_for_admonition_title` vs. `_saved_body_for_figure_caption`), so no accidental cross-buffer name reuse can reintroduce this exact class of bug.

### 1.2 The stale `table_cell_content` buffer — the SECOND bug, and why it is real

`add_text()` (`translator.py:253-267`) routes text to `self.table_cell_content` (not `self.body`) whenever `self.in_table and hasattr(self, "table_cell_content")`. `table_cell_content` is set in `visit_entry` (`translator.py:2584-2598`) and reset to `[]` — **never deleted** — in `depart_entry` (`translator.py:2600-2631`). `visit_table`/`depart_table` (`translator.py:2337-2485`) reset `table_cells`/`table_colcount`/`table_colwidths` at both start and end, but **never touch `table_cell_content`**.

Consequence: on the **first** table encountered by a given `TypstTranslator` instance, `table_cell_content` does not exist yet, so `hasattr()` is `False` and a table-title's `add_text()` calls correctly land in `self.body` (or, after the fix, the new buffer-swapped `self.body = []`). On the **second or later** table in the same document, `table_cell_content` is a leftover (empty, but present) list attribute from the prior table's last `depart_entry`. Because `self.in_table` is set `True` before the title's children are visited, `add_text()`'s `hasattr` check is now `True` even though no `visit_entry` has run for the current table — **every** `add_text()` call inside the title (including the new buffer-swap target, since the buffer-swap only redirects `self.body`, not `add_text()`'s routing decision) silently vanishes into the stale `table_cell_content` list instead of the swapped `self.body`. This is precisely the "caption swallowed by a stale buffer" bug the driving todo names, and it will **still bite the new caption buffer-swap** unless fixed independently.

**Required companion fix:** make `table_cell_content`'s absence, not its emptiness, mean "not currently inside an entry." Concretely: `del self.table_cell_content` (guarded by `hasattr`) at the end of `depart_table` (after line 2480, alongside the existing `table_cells`/`table_colcount`/`table_colwidths` reset), and defensively at the top of `visit_table` too (alongside the existing 2368-2370 resets), so `add_text()`'s `hasattr(self, "table_cell_content")` check reliably reflects "inside an entry right now" rather than "an entry was ever visited on this translator instance." This is a small, generically-correct fix orthogonal to the caption feature itself — it should ship in the SAME plan/commit as the caption buffer-swap (both touch `visit_table`/`depart_table`), since the caption feature is what first makes the latent bug user-visible/testable (a captioned SECOND table is precisely the todo's regression case).

### 1.3 `visit_table`/`depart_table` (`translator.py:2337-2485`) — table emission today, and where `figure()` composes

`visit_table` (2337-2370): emits `_emit_id_anchors(node)` (a **fully independent** `[#metadata(none) <label>]` bracket statement, decoupled from the `table(...)` call itself — see §1.4), the list-item leading-separator idiom, then sets `self.in_table = True` and resets the three per-table accumulators.

`depart_table` (2422-2485) builds the emission via **`self.body.append` directly, never `self.add_text`** (2444, explicit comment: avoids the same stale-`table_cell_content` misrouting hazard as §1.2, because `self.in_table` is still `True` at this point). Current 2-way branch on `converted_width = self._convert_length_to_typst(node.get("width"))`:

```
if converted_width is not None:
    body.append(f"block(width: {converted_width})[#table(\n  columns: {cols},\n")
else:
    body.append(f"table(\n  columns: {cols},\n")
... header_cells / body_cells via _format_table_cell ...
if converted_width is not None:
    body.append(")]\n\n")
else:
    body.append(")\n\n")
```

`_build_columns_fr_arg()` (2372-2391) and `_format_table_cell()` (2393-2420) are unaffected by the caption change — they only shape the INNER `table(...)` call, which stays byte-identical whether or not it is wrapped in `figure(...)`.

**Composition point:** the caption wrap and the width wrap are **orthogonal, nestable wrappers** around the same inner `table(\n  columns: ...,\n  ...\n)` call — exactly the same two-orthogonal-wrappers shape `visit_figure`/`depart_figure` (`translator.py:2039-2151`) already established for `figure()` + `block(width:...)[...]` (LEN-01). Four cases, composed the same way `depart_figure` composes width with the figure-open bracket:

| Caption? | Width? | Emission |
|---|---|---|
| No | No | `table(\n  columns: ...,\n  ...\n)\n\n` — **unchanged, current code path** |
| No | Yes | `block(width: W)[#table(\n  columns: ...,\n  ...\n)]\n\n` — **unchanged, current code path** |
| Yes | No | `figure(\n  table(\n    columns: ...,\n    ...\n  ),\n  caption: {<buffered caption>},\n  kind: table,\n)\n\n` — bare code-mode statement (no `#` prefix), mirrors `visit_figure`'s own no-ids/no-width bare `figure(\n` open (line 2099) |
| Yes | Yes | `block(width: W)[#figure(\n  table(\n    columns: ...,\n    ...\n  ),\n  caption: {<buffered caption>},\n  kind: table,\n)]\n\n` — markup-mode `#figure(` inside the `block(...)[...]` bracket, mirrors `depart_figure`'s own width+figure composition (2093-2094 / 2126-2130) |

The caption content itself is inserted as `caption: {<joined buffered body>}` — a `{...}` code-mode block, never `[...]` markup — mirroring `depart_figure`'s own `caption: {{self.figure_caption}}` emission (`translator.py:2113-2114`), because the buffered content is already-rendered `text(...)`/`emph(...)` Typst **calls**, not literal markup text.

**Practical slot:** add a `self.table_caption: str = ""` instance var (mirrors `self.figure_caption`, init alongside it in `__init__`), populated by the new `depart_title` branch (§1.1) instead of `self.figure_caption`. In `depart_table`, branch the SAME `converted_width is not None` check on `bool(self.table_caption)` as a second, orthogonal axis (4 emission cases as above), and reset `self.table_caption = ""` alongside the existing `table_cells`/`table_colcount`/`table_colwidths` reset at 2477-2480.

### 1.4 Table ids/anchors — no interaction risk

Unlike figures (which self-anchor `ids[0]` inside their own `[#figure(...) <label>]` bracket and pass `skip_ids` to `_emit_id_anchors` for any REMAINING propagated-target ids — `depart_figure`, `translator.py:2123-2139`), **tables anchor ALL their ids unconditionally and independently** via `_emit_id_anchors(node)` at the very top of `visit_table` (`translator.py:2348`), **before** `self.in_table` is even set `True`. This is a standalone bracket statement (`[#metadata(none) <label>]`) that has nothing to do with the `table(...)`/`figure(...)` call structure. **Conclusion for the planner: the caption/figure-wrap change requires zero changes to id/anchor handling** — table id anchoring is already fully decoupled from the table-body-emission code the caption change touches.

### 1.5 Cell content shape (for test-porting)

`visit_entry`/`depart_entry` (`translator.py:2584-2631`) accumulate a cell's content string from whatever nodes are inside the `entry` — typically a `paragraph` node. `visit_paragraph`/`depart_paragraph` (`translator.py:697-751`) wrap non-list-item paragraph content in `par({...})` (734: `self.add_text("par({")`). Combined with `visit_Text`'s `text("...")` wrap (`translator.py:1009`), a plain table cell's captured `content` string is `par({text("...")})`, and `_format_table_cell()` (2393-2420, no colspan/rowspan) wraps that in an outer `{...}`, producing the driving todo's cited current cell literal `{par({text("...")})}` with `columns: (1fr, 1fr)` for a 2-column table with no colwidth data (`_build_columns_fr_arg`'s equal-1fr fallback, 2386-2391). Ported PR#98 test assertions must match this shape, not PR#98's original (pre-FID-01a-colwidth, pre-`par()`-wrap) cell format.

## 2. `typst_elements` non-mapping-key pass-through

### 2.1 Current data flow (why the keys are dropped today)

1. `writer.py:200-209` (inside `TypstWriter.translate()`, the master-document branch): builds `sphinx_metadata = {"project": ..., "author": ..., "release": ..., "copyright": ...}`, then `sphinx_metadata.update(typst_elements)` — this merges arbitrary user keys (e.g. `papersize`, `fontsize`) into the SAME dict as the four canonical Sphinx-derived keys, with no way to later distinguish "structural metadata" from "opaque template kwargs."
2. `writer.py:212`: `params = template_engine.map_parameters(sphinx_metadata)`.
3. `template_engine.py:186-245` (`TemplateEngine.map_parameters`): loops `for sphinx_key, template_key in self.parameter_mapping.items()` — `self.parameter_mapping` defaults to `DEFAULT_PARAMETER_MAPPING` (`template_engine.py:62-66`, exactly `{"project": "title", "author": "authors", "release": "date"}`, 3 keys). **Any key present in `sphinx_metadata` that is not a KEY of `self.parameter_mapping` is never looked at — the loop only iterates the mapping, not the metadata.** `copyright` is silently dropped by the same mechanism today (pre-existing, out of this milestone's stated scope — see §2.3 below). `papersize`/`fontsize`/any other `typst_elements` key is dropped identically.
4. `template_engine.py:398-414` (`render()`): the resulting `params` dict (plus `self.typst_template_params`, D-08 override-wins) becomes the `#show: project.with(key: value, ...)` argument list — **whatever key IS present in `params` at this point reaches the template function verbatim, unchecked.** This is the existing, already-accepted precedent for "trust the config, let `typst.compile()` fail loud on a bad kwarg" (see `typst_authors` at 239-243 and `typst_template_function["params"]` at 405-407, neither of which is validated against the target function's signature).

### 2.2 `base.typ` already accepts the two keys the milestone cares about — no template change needed for them

`typsphinx/templates/base.typ:39-48` — `project()`'s signature already declares `papersize: "a4"` (46) and `fontsize: 11pt` (47) as named parameters, consumed at 54-61 (`set page(paper: papersize, ...)`, `set text(size: fontsize, ...)`). **These two keys are NOT missing from the template — they are missing from the DATA PATH that would populate them from `typst_elements`.** The fix is entirely a `writer.py`/`template_engine.py` data-flow change; `base.typ` requires **no edit** for `papersize`/`fontsize` specifically. (Any OTHER arbitrary key a user puts in `typst_elements` that `project()` does NOT declare will still hit a Typst "unexpected named argument" compile error once forwarded — this is the same accept-and-fail-loud contract as `typst_template_function["params"]` already has, not a regression, and does not require `base.typ` to declare every conceivable key defensively.)

### 2.3 Recommended integration point — and the `copyright` trap to avoid

**Do not** simply "stop dropping unmapped keys" inside the existing `map_parameters()` loop by iterating `sphinx_metadata` instead of `self.parameter_mapping` — that would ALSO forward `copyright` (already merged into the same dict at `writer.py:200-209`) straight into `#show: project.with(copyright: ..., ...)`, which `base.typ`'s `project()` does not declare, breaking every existing build that sets Sphinx's standard `copyright` config value. `copyright`-key handling is explicitly **out of scope** for this milestone (the driving todo names only `typst_elements`'s non-mapping keys — `papersize`/`fontsize` et al. — as discovery #1; `copyright` was never claimed to work and isn't mentioned as broken).

**The keys that must pass through are structurally distinguishable from `sphinx_metadata`'s 4 canonical keys ONLY if `typst_elements` is kept as its own dict, not merged into `sphinx_metadata`.** Recommended slot:

- `writer.py:208-209`: stop `sphinx_metadata.update(typst_elements)`. Keep `typst_elements` as a separate local (`typst_elements = getattr(config, "typst_elements", {})`).
- `template_engine.py`'s `map_parameters()` signature gains an explicit second parameter carrying the opaque pass-through dict, e.g. `def map_parameters(self, sphinx_metadata: Dict[str, Any], extra_params: Dict[str, Any] | None = None) -> Dict[str, Any]:` — forwarded with `params.update(extra_params or {})` as a final step, **after** the existing D-05 title/authors/date back-fill guard (219-226) and the D-07 `typst_authors` override (239-243), so it composes as a simple additive final merge and does not need to touch either existing conditional.
- `writer.py:212` becomes `params = template_engine.map_parameters(sphinx_metadata, typst_elements)`.

This keeps `map_parameters()` as the single, already-documented seam ("Sphinx metadata → template parameters," per its own docstring) while making the type signature itself encode the distinction the driving todo's problem statement draws: 4 known Sphinx-derived keys vs. N opaque `typst_elements` keys the template/package function's own signature is trusted to validate at compile time.

### 2.4 Interaction with `typst_package` (Phase 22.2 `resolve_package_for_engine()`) — low risk, same merge path

`resolve_package_for_engine()` (`template_engine.py:15-39`) only decides WHICH `typst_package` value `TemplateEngine.__init__` receives (template-wins-over-package routing, D-01/D-03) — it has no interaction with `map_parameters()`'s key set at all. On the package-ALONE path, `self.parameter_mapping = {}` (D-05, `template_engine.py:100-104`, "only pass what the user explicitly mapped") and the title/authors/date back-fill guard is skipped (219-226) — but the recommended `extra_params` merge in §2.3 is unconditional and happens regardless of `self.typst_package`, so `typst_elements` keys reach a package function's `.with(...)` call exactly the same way they reach `base.typ`'s `project()` — consistent with the already-established "explicit config always forwards, package function signature is trusted/unchecked" contract `typst_template_function`/`typst_authors` already use. **No new branch on `self.typst_package` is needed inside `map_parameters()` for this change** — this is the one place the two Phase-22.2/v0.6.3 changes share code (`template_engine.py`'s `map_parameters()` body) but they compose additively (D-05/D-07's existing guards stay untouched; the new step runs strictly after them).

`builder.py`'s `_write_template_file()` (`builder.py:521-592`, calls `TemplateEngine(...).get_template_content()` at line 585) is **NOT** in this data path at all — it only ever writes the template's raw TEXT once per build; it never calls `map_parameters()` or touches `typst_elements`. **No `builder.py` change is required or at risk for this item.**

## 3. `typst_toctree_defaults` deletion — confirmed touch points, no consumer to unwire

Grep-confirmed (2026-07-23, current tree) — the config value is **registered but never read** anywhere in `typsphinx/`:

| File | Line(s) | What's there |
|---|---|---|
| `typsphinx/__init__.py` | 47 | `app.add_config_value("typst_toctree_defaults", None, "html", [dict, type(None)])` — the sole registration; delete this line |
| `typsphinx/translator.py` / `writer.py` / `builder.py` / `template_engine.py` | — | **zero references** — confirmed no consumer; `TemplateEngine.extract_toctree_options()` (`template_engine.py:273-318`) reads toctree options directly from the doctree's `addnodes.toctree` node (`maxdepth`/`numbered`/`caption` attributes), never from this config value |
| `docs/configuration.rst` | 223, 245, 355 | documents it (this whole file is ALSO the orphan-docs todo's separate deletion target — see PROJECT.md) |
| `examples/advanced/conf.py` | 86 | sets it in an example `conf.py` |
| `examples/advanced/README.md` | 250 | documents the example |
| `README.md` | 208 | one-line mention in the Configuration Options list |
| `tests/test_config_toctree_defaults.py` | whole file (9-236) | every test in this file asserts registration-only (`hasattr`/equality against `app.config.typst_toctree_defaults`), never output — **delete the whole file**, mirroring the Phase 22.2 CONF-01 precedent (`typst_output_dir`/`typst_author_params` were deleted file-and-all, not stubbed) |
| `tests/test_documentation_configuration.py` | 40 | lists `"typst_toctree_defaults"` in an expected-config-names table — needs updating (removal) alongside the `__init__.py` deletion or this test will start asserting a name that no longer exists |
| `CHANGELOG.md` | 553 | historical `[Unreleased]`-era entry — leave untouched (past changelog entries are not rewritten) |

**Confirmed: deletion is a pure subtraction with no wiring to redo** — `extract_toctree_options()` already independently sources toctree options from the doctree, so removing the dead config value changes zero runtime behavior. This is the lowest-risk item of the three.

## 4. Suggested build order

**Independent (no shared file surface, can run in parallel waves):**

- **Captioned-table figure wrap** (§1) touches `translator.py` only (`visit_title`/`depart_title`, `visit_table`/`depart_table`, plus one new `__init__` state var `table_caption`) + a new/extended test file. It does not touch `writer.py`, `template_engine.py`, or `__init__.py`.
- **`typst_toctree_defaults` deletion** (§3) touches `__init__.py` (1 line), docs/examples, and one whole test-file deletion + one test-file edit. It does not touch `translator.py`, `writer.py`, or `template_engine.py`.

**These two can be planned/executed as fully independent waves — zero file overlap.**

**Shares file surface with Phase 22.2 (`template_engine.py`) — sequence-sensitive within its own item, not across items:**

- **`typst_elements` pass-through** (§2) is the only item touching `template_engine.py` (`map_parameters()`) and `writer.py` (the `sphinx_metadata`/`typst_elements` split) — the exact two files Phase 22.2 (CONF-01..03, WR-04) already modified for `typst_package` routing (`resolve_package_for_engine`), the D-05/D-07 guards inside `map_parameters()`, and the essential-imports hoist in `render()`. There is **no direct conflict** (the new `extra_params` merge is additive and runs after the existing D-05/D-07 logic per §2.3), but because this is the ONE file both a prior-milestone change and this milestone's change touch, it should **not** run in the same wave as an unrelated `template_engine.py` edit if one is ever introduced later in this milestone (none currently is — the `translator.py`-only and `__init__.py`-only items are already isolated). Recommend planning this item on its own wave/plan so its diff against `map_parameters()` is easy to review in isolation, and so its new `test_typst_elements_passthrough_gate.py`-style regression fixture (mirroring `tests/test_package_only_config_gate.py`'s real-`typst.compile()` config→output gate pattern, per the driving todo's explicit requirement) exercises the CURRENT, post-22.2 `map_parameters()`/`resolve_package_for_engine()` code, not a stale mental model of it.

**Recommended sequencing:**

1. `typst_toctree_defaults` deletion (§3) — trivial, zero-risk, unblocks nothing but blocks nothing either; do it first to shrink the diff surface early.
2. Captioned-table figure wrap (§1) — the largest, most state-machine-sensitive change (`visit_title` branch + stale-buffer companion fix + `depart_table` 4-way composition); give it its own wave given the buffer-clobber risk flagged in §1.1.
3. `typst_elements` pass-through (§2) — touches the file Phase 22.2 most recently reshaped; do it last (or at least not concurrently with any other `template_engine.py` touch) so its real-compile gate is written and verified against the final, current state of `map_parameters()`.

All three items are independent enough that 1 and 3 could also run in the same wave as 2 (no file-content overlap with `translator.py`), but 1-then-2-then-3 is the safest ordering if the milestone prefers strictly sequential phases.

## Sources

- `typsphinx/translator.py` (current `main`, commit `9f8e075`) — `visit_title`/`depart_title` (453-584), `visit_caption`/`depart_caption` (2153-2210), `visit_figure`/`depart_figure` (2039-2151), `visit_table`/`depart_table`/`_build_columns_fr_arg`/`_format_table_cell` (2337-2485), `visit_entry`/`depart_entry` (2584-2631), `visit_paragraph`/`depart_paragraph` (697-751), `add_text` (253-267), `_emit_id_anchors` (311-359), `__init__` state-var block (58-243)
- `typsphinx/writer.py` (current `main`) — `TypstWriter.translate()` (117-247), `sphinx_metadata`/`typst_elements` merge (200-209)
- `typsphinx/template_engine.py` (current `main`) — `DEFAULT_PARAMETER_MAPPING` (62-66), `TemplateEngine.__init__` (68-121), `map_parameters()` (186-245), `render()` (333-420), `resolve_package_for_engine()` (15-39), `extract_toctree_options()` (273-318)
- `typsphinx/templates/base.typ` (current `main`) — `project()` signature (39-93)
- `typsphinx/builder.py` (current `main`) — `_write_template_file()` (521-592, confirmed NOT in the `typst_elements` data path)
- `typsphinx/__init__.py` (current `main`) — config-value registration block (43-61)
- `.planning/todos/pending/2026-07-23-reimplement-pr-98-captioned-table-figure-wrap.md` — driving todo, root-caused repro on commit `9f8e075`
- `.planning/todos/pending/2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md` — driving todo, root-caused with a real temp-project `sphinx-build -b typst` + grep-for-zero-occurrences repro
- `.planning/PROJECT.md` (v0.6.3 Current Milestone section + Phase 14 Key Decision entry on the footnote buffer-swap clobber precedent)
- `tests/test_config_toctree_defaults.py`, `tests/test_package_only_config_gate.py` (existing test patterns cited as precedent for the required new gates)

---
*Architecture research for: typsphinx v0.6.3 (config & docs 実測整合 + captioned tables)*
*Researched: 2026-07-23*

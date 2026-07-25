# Pitfalls Research

**Domain:** typsphinx v0.6.3 — reimplementing PR#98 (captioned-table figure wrap), `typst_elements` pass-through, and docs/config cleanup
**Researched:** 2026-07-23
**Confidence:** HIGH (all findings derived directly from reading the current `main` source — `typsphinx/translator.py`, `typsphinx/template_engine.py`, `typsphinx/writer.py`, `typsphinx/templates/base.typ`, `tests/test_package_only_config_gate.py` — plus the three pending-todo root-cause docs and `.planning/PROJECT.md`'s FN-01/22.2 decision history. No external web research was needed; this is a same-repo static-analysis pitfalls pass. Supersedes the prior v0.6.0-era PITFALLS.md that lived at this path.)

## Critical Pitfalls

### Pitfall 1: Caption content silently swallowed by the `table_cell_content` buffer (the highest-value trap in this milestone)

**What goes wrong:**
`TypstTranslator.add_text()` (translator.py:253-267) routes ALL text through this check, in this order:
```python
if hasattr(self, "in_table") and self.in_table and hasattr(self, "table_cell_content"):
    self.table_cell_content.append(text)
else:
    self.body.append(text)
```
`self.in_table` is set `True` in `visit_table` (translator.py:2367) **before** any child of the table — including its `title` child (the `.. table:: Caption` text) — is visited, and stays `True` until `depart_table` (translator.py:2477). `table_cell_content` is created by `visit_entry` (translator.py:2592) and, once created, is **never deleted** — it persists as an instance attribute for the rest of the document's translation, reset to `[]` only at the top/bottom of each `visit_entry`/`depart_entry` pair. So: for the very first table encountered in a document, `hasattr(self, "table_cell_content")` is `False` and `add_text` correctly falls through to `self.body`. For the **second and every subsequent table** in the same document, `table_cell_content` already exists (left over from the first table's cells) — so if the new caption-buffering code follows the pattern used elsewhere in this file (buffer-swap `self.body = []`, then let the caption's child nodes stream through the normal visitor chain via `add_text`), every one of those `add_text` calls gets redirected into the stale `table_cell_content` list instead of the swapped `self.body`. The caption is captured nowhere, and the swapped-out `self.body` list you intended to `"".join()` stays empty. This is worse than the todo's framing ("stale buffer from a previous table") suggests — it is not a staleness bug that only bites occasionally, it is a **structural priority-ordering bug in `add_text` itself**: `self.in_table` is checked before anything about the caller's own buffer-swap state, so a body-swap alone (the idiom `visit_caption`/`depart_caption` already uses successfully for **figure** captions, translator.py:2153-2210) does **not** work inside a table, regardless of staleness.

**Why it happens:**
The existing figure-caption buffer-swap (translator.py:2166-2210) is proven and looks like the obvious template to copy for table captions. But it works there specifically because `self.in_figure` (the guard `visit_caption` checks) is orthogonal to `self.in_table` — nothing in `add_text` special-cases `in_figure`. A table caption is structurally different: it lives *inside* the very node (`nodes.table`) whose `in_table` flag is what `add_text` special-cases. Copying the figure-caption idiom verbatim into `visit_title`'s new table-caption branch reproduces this bug by construction, and it will not show up in a single-table test fixture — only in a fixture with **two or more tables in one document**, exactly the shape of the todo's own listed regression case ("stale buffer 漏れ防止").

**How to avoid:**
Temporarily set `self.in_table = False` (in addition to the `self.body = []` swap) for the duration of the title/caption's children being visited, then restore `self.in_table = True` in the matching `depart_title` branch — mirroring how the existing admonition-title branch (`_in_admonition_title`, translator.py:487-503, 546-562) fully reroutes state rather than relying on the body-swap alone. This is the only way to let arbitrary inline content (emphasis, strong, references — the todo's "インラインマークアップ保持" test) stream through the real visitor chain and land in the swapped `self.body` rather than being hijacked by the `in_table` check.

**Warning signs:**
A test with a single captioned table passes, but a fixture with two captioned tables (or one plain table followed by one captioned table) in the same document silently drops the second caption — no exception, no warning, just missing text in the emitted `.typ`. Also watch for `table_cell_content` unexpectedly non-empty right after a table's `depart_table` runs (a leaked caption sitting in it).

**Phase to address:**
The PR#98 reimplementation phase. Must be proven by a regression fixture with **at least two tables in one document, the second one captioned** — a single-table fixture cannot catch this class of bug.

---

### Pitfall 2: `visit_title`/`depart_title` branch must `return` early, or the table caption still emits a stray `heading()`

**What goes wrong:**
`visit_title` currently dispatches on `isinstance(node.parent, nodes.Admonition) or isinstance(node.parent, nodes.topic)` first (translator.py:487-503), and **returns** inside that branch. Everything below that check — the section-id anchor logic, the `emitted_level = max(1, self.section_level)` clamp, and the `heading(level: ..., {` emission (translator.py:514-529) — is the fallback path for every title whose parent is neither an Admonition nor a topic. A `nodes.table`'s `title` child parent is `nodes.table`, which matches neither existing check, so it currently falls all the way through to the section-heading emission — this is the exact bug the todo describes (the spurious `heading(level: 1, {text("My caption")})` before the table). Adding a new `elif isinstance(node.parent, nodes.table):` branch to intercept this is correct, but if that branch is added **without an explicit `return`** (or in a way that lets execution continue into the section-heading code below), the fix is a no-op: both the caption buffer AND the stray heading get emitted. The same applies symmetrically to `depart_title`: `depart_title`'s `if self._in_admonition_title:` branch (translator.py:546-562) also `return`s early; a new table-caption branch must do the same, restoring `self.in_list_item`/`self.list_item_needs_separator` from the values saved at the top of `visit_title` (translator.py:477-480) exactly as the admonition branch already does (translator.py:552-553) — forgetting that restore leaks the title's list-item spoof state into the table's own subsequent siblings.

**Why it happens:**
`visit_title`/`depart_title` handle five conceptually distinct "what is a title inside" cases (section, admonition, topic, contents-topic, and now table) inside one method via sequential `if`/`elif` dispatch with early returns. It is easy to add a new elif clause that mutates state and emits the caption buffer but forgets that the method's *default* behavior (falling to the bottom) is "emit a section heading" — the safe behavior for a brand new branch is "return", not "fall through, unless you explicitly intend to also run the section logic."

**How to avoid:**
Insert the new `nodes.table` check as its own `elif` beside the admonition/topic check (or as a second top-level `if isinstance(node.parent, nodes.table): ...; return` guard before the section-id logic), and unit-test specifically that a captioned table's emitted `.typ` contains **zero** occurrences of `heading(` for that title. Mirror the admonition branch's full save/restore contract (in_list_item, list_item_needs_separator) on every return path in both `visit_title` and `depart_title`.

**Warning signs:**
Grep the emitted `.typ` for `heading(level:` immediately preceding a `table(`/`figure(...table(...` call — any hit is this bug recurring.

**Phase to address:**
PR#98 reimplementation phase, same fixture as Pitfall 1.

---

### Pitfall 3: `caption` + `:width:` composition — get the nesting order wrong and you either lose the width or get a markup/code-mode compile error

**What goes wrong:**
The existing (caption-less) `:width:` handling in `depart_table` wraps the **whole `table()` call** in `block(width: ...)[#table(\n...)]` (translator.py:2444-2453) using raw `self.body.append` (never `add_text`, to dodge Pitfall 1's routing hazard). Meanwhile the existing `:figwidth:` handling for **figures** (`visit_figure`/`depart_figure`, translator.py:2078-2132) applies width differently: it wraps the **whole `figure(...)` call**, not just its inner `image(...)`, in `block(width: ...)[#figure(\n...)]`. When a table gains a caption and becomes a `figure(table(...), caption: {...}, kind: table)`, there are two plausible ways to combine this with an existing `:width:`, and picking the wrong one either silently changes what the width constrains or breaks the Typst markup/code-mode contract:
- **(a)** Width wraps only the inner `table(...)` — `figure(block(width: ...)[#table(...)], caption: {...}, kind: table)` — constrains just the table, figure() sizes itself around it.
- **(b)** Width wraps the whole `figure(...)` call — `block(width: ...)[#figure(\n  table(...),\n  caption: {...},\n  kind: table\n)]` — constrains the whole titled/numbered figure block, matching the existing `visit_figure`/`depart_figure` precedent exactly.

Both are syntactically valid Typst, but they are **not equivalent**, and the codebase has an existing, real-compile-proven precedent for exactly this class of decision: `figure()`/`table()` both **reject a direct `width:` kwarg** (documented at translator.py:2081-2084 and 2431-2437, "verified real-compile failure"), which is why `block(width: ...)[...]` exists at all. Whichever nesting is chosen, **the `#` prefix requirement inside a markup `[...]` bracket is the sharpest failure mode**: `block(width: ...)[#table(...)]`/`block(width: ...)[#figure(...)]` both need the `#` before the code-mode function call because the bracket switches Typst into markup mode — a bare `table(` or `figure(` with no `#` inside that bracket is not a function call at all in markup mode and either silently prints as literal text or produces a parse error, exactly the class of bug already fought and documented in `visit_figure`'s own docstring (translator.py:2043-2055) and the Phase 8.1 admonition markup/code-mode bug in `.planning/PROJECT.md`'s Key Decisions.

**Why it happens:**
This is a genuinely new composition — neither `:width:`-without-caption nor `caption`-without-`:width:` alone exercises it, and the two existing precedents (plain-table width-wrap, figure width-wrap) disagree with each other on *what* gets wrapped, so there is no single "obviously correct" thing to copy. A rushed reimplementation is likely to reuse the OLD caption-less wrap verbatim (option a, since it requires the least code change to `depart_table`) without checking whether that is actually the desired semantic once a caption/figure-numbering box is introduced.

**How to avoid:**
Prefer mirroring the existing `visit_figure`/`depart_figure` precedent (option b: width wraps the whole `figure(...)` call) for consistency — it reuses exactly the same bracket-open-in-`visit_title`/bracket-close-in-`depart_table` discipline already proven correct for image figures, rather than inventing a new inner-wrap shape that has never been real-compile-tested in this file. Whichever option is chosen, write it down as an explicit decision (not an implicit byproduct of "whatever was easiest to patch"), and the regression fixture MUST include a table with **both** a caption and a `:width:` in the same document — no existing fixture exercises this combination today.

**Warning signs:**
A real `typst.compile()` failure with a Typst parse error mentioning "expected semicolon or line break" or "unexpected argument" on a captioned+widthed table; or (silent, worse) a compile that succeeds but the caption/table renders full-width instead of the configured width, indicating the wrap landed in the wrong place.

**Phase to address:**
PR#98 reimplementation phase — this must be its own named regression-fixture case (caption + width composition), not assumed to be covered by testing caption and width separately.

---

### Pitfall 4: A caption-less table must stay a plain `table()` — never speculatively `figure()`-wrap

**What goes wrong:**
If the new caption-detection logic is implemented as "always emit `figure(table(...), kind: table)` and only conditionally add `caption:`," every plain, uncaptioned table in the entire corpus (the overwhelming majority of tables in real docs) gets pulled into Typst's figure/counter machinery — silently adding a "Table N" numbering context to tables that were never meant to be numbered, polluting any List of Tables / numref counters and changing document layout (figures get different spacing/placement rules than bare `table()`) for content that has nothing to do with this todo.

**Why it happens:**
It is tempting to unify the two code paths into one `figure(...)` emission with an optional `caption:` argument, because it looks like less code — but `kind: table` numbering activates regardless of whether `caption:` is empty, so "no caption" must gate the *entire* figure-wrap decision, not just the `caption:` argument.

**How to avoid:**
Mirror the existing `figure_caption` state-variable pattern exactly (translator.py:91-92, `self.figure_caption = ""`, checked truthy in `depart_figure` at line 2113): add a parallel `self.table_caption` (or similar) reset to `None`/`""` in `visit_table`, set only by the new table-title branch, and have `depart_table` branch on `if self.table_caption:` to decide `figure(table(...), caption: {...}, kind: table)` vs. plain `table(...)` — never default to figure-wrapping and merely omit `caption:`.

**Warning signs:**
Any existing (pre-milestone) table-only test's expected output changes from `table(` to `figure(...table(` — that is this bug, a regression on every existing captionless table.

**Phase to address:**
PR#98 reimplementation phase; must be locked by the todo's own fourth listed test ("キャプション無しは非 figure").

---

### Pitfall 5: `kind: table` self-anchoring can duplicate a label already anchored by `visit_table`'s unconditional `_emit_id_anchors` call

**What goes wrong:**
`visit_table` unconditionally calls `self._emit_id_anchors(node)` at the very top (translator.py:2348), **before** `self.in_table` is even set — this anchors every id currently on the table node (e.g., a propagated `.. _target:` before the table, or an explicit `:name:`) as a zero-width `[#metadata(none) <label>]`. `_emit_id_anchors` was specifically designed with a `skip_ids` parameter (translator.py:311-360) for exactly one existing caller, `depart_figure`, which self-anchors `ids[0]` inside its own `[#figure(...) <label>]` markup postfix and passes `skip_ids={ids[0]}` to `_emit_id_anchors` so that id is not defined twice (translator.py:2134-2139, 2139's docstring explicitly documents this contract). If the table reimplementation copies `depart_figure`'s `[#figure(...) <label>]`-style self-anchoring for numref support (a natural thing to reach for once you're already mirroring `depart_figure`'s bracket-wrap pattern per Pitfall 3) **without** also changing `visit_table`'s early, unconditional `_emit_id_anchors(node)` call to skip that same id, a named/targeted captioned table emits the SAME `<label>` twice in one document — a genuine Typst compile fatal ("label already defined"-class error), not a cosmetic bug.

**Why it happens:**
`visit_table`'s early anchor call long predates this todo and exists for a different, narrower purpose (propagated explicit targets landing on ANY table, captioned or not) — it is easy to forget it exists while focused on the new caption/figure-wrap logic, especially since it fires at `visit_table` time, far from where the new label logic would be added in `depart_table`.

**How to avoid:**
If (and only if) the reimplementation adds `<label>`-based self-anchoring for numref on captioned tables, thread the exact same `skip_ids=set(node.get("ids", [])[:1])` pattern `depart_figure` already uses, and confirm via a fixture with both an explicit `:name:` on a captioned table AND a compile — not just string assertions, since a duplicate-label error is a real-compile-only failure (string-diff tests would never see it, since the emitted text is syntactically fine, just semantically invalid at Typst's label-resolution pass). If the todo's scope is genuinely limited to Typst-native `kind: table` auto-numbering with **no** id/label/numref support added, explicitly confirm and record that decision — and confirm `visit_table`'s early `_emit_id_anchors` call is left completely untouched (no new anchor logic added anywhere near it) so this collision risk never activates.

**Warning signs:**
A named captioned table (`:name: my-table` + `.. table:: Caption`) compiles successfully via `-b typst` (source generation) but fails at `typst.compile()` with a label-related error — this only shows up on the real-compile gate, never on unit-level string assertions.

**Phase to address:**
PR#98 reimplementation phase — scope this explicitly (label/numref support in or out) before writing the regression fixture, since the fixture shape differs depending on the answer.

---

### Pitfall 6: Blind `typst_elements` pass-through → "unexpected argument" fatal on ANY unrecognized key (the #1 way to turn "dead but harmless" into "fatal")

**What goes wrong:**
Today, `typst_elements` non-mapping keys are silently dropped (`map_parameters` only forwards the 3 `DEFAULT_PARAMETER_MAPPING` keys — template_engine.py:186-213) — dead but harmless. The moment (A) is implemented to forward these keys through to `project.with(...)`, **every** key in `typst_elements` becomes a literal named argument in a real Typst function call. Typst has no equivalent of Python's `**kwargs` catch-all on the calling side for this pattern — `base.typ`'s `project()` function has a **fixed, explicit parameter list** (`title`, `authors`, `date`, `toctree_maxdepth`, `toctree_numbered`, `toctree_caption`, `papersize`, `fontsize`, `body` — templates/base.typ:39-48). Passing ANY key not in that list — a typo (`paper_size` instead of `papersize`), a plausible-sounding but non-existent key (`lang`, `margin`, `theme`), or simply a key that made sense for one user's custom template but not the default one — produces a hard Typst compile error ("unexpected argument") that aborts the ENTIRE PDF build. This is qualitatively different from every other dead-config fix in this project's history (`typst_output_dir`, `typst_toctree_defaults`): those configs being dead meant "your setting is ignored"; a naive blind pass-through means "your setting can now break your build," and it does so for **custom templates and Typst-Universe packages too** — `TemplateEngine.__init__` explicitly documents (template_engine.py:100-106) that on the package-only path, "a Typst function signature cannot be introspected from Python," so there is no way to validate keys against an arbitrary package's function signature at all — any pass-through key not in that package's signature is unconditionally fatal, with zero validation possible ahead of the real compile.

**Why it happens:**
The natural, minimal-diff implementation of (A) is "stop dropping the keys" — i.e., delete the filtering that currently protects every user from this exact failure mode. It is easy to implement and test against the two headline example keys (`papersize`, `fontsize`, both of which `base.typ`'s `project()` already happens to declare — see `templates/base.typ:46-47`) without noticing that the pass-through is now *generic*, and will forward literally anything the user puts in the dict.

**How to avoid:**
Scope the pass-through narrowly and document the contract loudly: only forward `typst_elements` keys that the active template's function is known to accept. For the bundled default template this means whitelisting exactly `base.typ`'s `project()` parameter names (or, more robustly, adding a catch-all `..sink` / dict-based extension point to `project()` itself in `templates/base.typ` so unknown keys are absorbed rather than rejected — a template-side change, not just a Python-side change). For custom templates and Typst-Universe packages, the docs must state explicitly that `typst_elements` non-mapping keys are forwarded VERBATIM and unvalidated, and an unrecognized key is the user's own responsibility to get right — this is a compile-time contract, not a soft warning. Under no circumstances should the implementation attempt to "guess" a safe subset by inspecting `base.typ` at runtime (fragile, template-path-dependent); a static, versioned whitelist paired with a `templates/base.typ` update in lockstep is the safe approach.

**Warning signs:**
Any `typst_elements` key that doesn't appear verbatim in `templates/base.typ`'s `project(...)` signature (or the active custom template's/package's own function signature) will compile-fail loudly — which is actually the GOOD outcome (loud, not silent); the pitfall is if that failure isn't anticipated and tested for, so the first person to hit it is a real end user, not a regression fixture.

**Phase to address:**
Dead-config-cleanup phase (typst_elements pass-through, item A). Must ship BOTH a positive fixture (a recognized key changes output) AND a negative fixture (an unrecognized key raises a real `typst.compile()` error) — the CONF-03 precedent (`tests/test_package_only_config_gate.py`'s `TestPreFixBasisFailureProof`) is the template for the negative case.

---

### Pitfall 7: `sphinx_metadata` already contains a poison key (`copyright`) — a naive "forward everything not in the mapping" scan breaks EVERY project, not just `typst_elements` users

**What goes wrong:**
`writer.py:200-209` builds `sphinx_metadata` as `{"project": ..., "author": ..., "release": ..., "copyright": config.copyright}`, THEN merges `typst_elements` into that SAME dict via `sphinx_metadata.update(typst_elements)` (writer.py:209) — by the time `map_parameters()` sees it, there is no way to tell, from the dict alone, which keys came from Sphinx's own baseline metadata (`project`/`author`/`release`/`copyright`) and which came from the user's `typst_elements`. If the pass-through implementation is written as "for every key in `sphinx_metadata` not already consumed by `self.parameter_mapping`, forward it as an extra kwarg" (the natural generalization of the existing `map_parameters` loop, template_engine.py:204-213), then **`copyright` — which every Sphinx project has, either explicitly set or Sphinx's own default — gets unconditionally forwarded** as a `copyright: "..."` argument to `project.with(...)`, even for users who never touched `typst_elements` at all. Since `base.typ`'s `project()` has no `copyright` parameter (templates/base.typ:39-48), this is Pitfall 6's "unexpected argument" fatal, except triggered universally on ship day — not an edge case gated behind opt-in config, a **regression that breaks the default template path for every existing user**.

**Why it happens:**
`map_parameters(sphinx_metadata)`'s single-dict signature (template_engine.py:186) doesn't distinguish the origin of its keys, and `writer.py` merges the two sources together (line 209) before calling it — so any implementation that scans the merged dict for "leftover" keys will treat `copyright` exactly like a genuine `typst_elements` entry.

**How to avoid:**
Change the call contract so pass-through candidates are sourced ONLY from `typst_elements` itself — e.g. pass `typst_elements` into `map_parameters` (or a new method) as its own explicit argument, captured in `writer.py` BEFORE the `sphinx_metadata.update(typst_elements)` merge, rather than inferred by set-difference against the post-merge dict. Any regression fixture for this change MUST include a baseline case with `typst_elements = {}` (the default, no pass-through configured, but `copyright` still present in `conf.py` as it is in virtually every real Sphinx project) and assert the emitted `#show: project.with(...)` call contains no `copyright:` argument — this is the single highest-value assertion in the whole fixture, because it is the one most likely to be silently skipped by someone testing only the "happy path" of an explicitly configured `typst_elements` key.

**Warning signs:**
The `TestPackageOnlyConfigGate`-style fixture passes with an explicit `typst_elements` dict configured, but a completely unrelated existing test project (any fixture with a `conf.py` that sets `copyright = "..."`, which is nearly all of them) starts failing to compile after this change lands.

**Phase to address:**
Dead-config-cleanup phase (typst_elements pass-through, item A) — this must be the FIRST negative-case fixture written, before the positive papersize/fontsize cases, precisely because it is the one most likely to be missed.

---

### Pitfall 8: Typed vs. string Typst values — `fontsize: "20pt"` (a Python str) does not become a Typst length, it becomes a Typst string, and that's a type error

**What goes wrong:**
`_format_typst_value()` (template_engine.py:422-453) has an unconditional rule: `isinstance(value, str) → f'"{escaped}"'`. Every Python string value is quoted, with no exceptions. `base.typ`'s `project()` declares `fontsize: 11pt` as its default (templates/base.typ:47) — an **unquoted Typst length literal**, used inside the function body as `set text(size: fontsize, lang: "en")` (templates/base.typ:61). Typst's `set text(size: ...)` strictly requires a `length` value; passing a `str` there is a real Typst type error ("expected length, found string"), not a silently-tolerated mismatch. So even AFTER (A) is implemented to forward `typst_elements` keys correctly (fixing Pitfall 6/7's "does it get forwarded at all" question), `typst_elements = {"fontsize": "20pt"}` emits `fontsize: "20pt"` into the `project.with(...)` call — syntactically valid Typst, but it fails at the `set text(size: fontsize)` line inside `project()` with a type error, a DIFFERENT and equally fatal failure mode from the missing-argument case. `papersize`, by contrast, genuinely IS meant to be a Typst string (`page(paper: papersize)` — templates/base.typ:55, and Typst's own `page()` API takes `paper:` as a string like `"a4"`/`"us-letter"`), so the SAME blanket string-quoting rule is *correct* for `papersize` and *wrong* for `fontsize` — there is no single rule that works for both of this todo's two headline example keys.

**Why it happens:**
Python's config values have no native "Typst length" type — `conf.py` can only supply a plain string or number, and `_format_typst_value`'s job is to guess how to render an arbitrary Python value as Typst source. The existing rule (quote every string) was written for genuinely string-typed template parameters (`title`, `toctree_caption`) and was never designed to also carry length-typed values through the same code path.

**How to avoid:**
Do not treat this as solved by "just forward the value." Either (a) detect a length-like pattern (a numeric prefix followed by a recognized Typst unit — this project already has exactly this detection logic in `translator.py`'s `_TYPST_PASSTHROUGH_UNITS = {"%", "em", "pt", "cm", "mm", "in"}`, translator.py:18-21, used by `_convert_length_to_typst` for a *different* purpose — CSS-length node attributes — but the same regex-and-strip idea applies) and emit such values unquoted, while leaving genuinely string-typed values (like `papersize`) quoted; or (b) make `fontsize` accept a Python number (interpreted as points) and format it as `f"{value}pt"` unquoted, documenting that a raw string is NOT length-safe. Whichever approach is chosen, it must be a documented, tested rule — not an accidental byproduct — and the length-detection logic should be evaluated for reuse against (not blind duplication of) the existing `_TYPST_PASSTHROUGH_UNITS`/`_convert_length_to_typst` machinery in `translator.py`, noting that machinery lives in a different module (translator, not template_engine) and operates on docutils node attributes, not template-engine config dicts — reuse may mean extracting a shared helper, not importing across an unrelated module boundary.

**Warning signs:**
`typst_elements = {"fontsize": "20pt"}` compiles the `#show: project.with(...)` call syntactically fine (string diff assertions pass), but a REAL `typst.compile()` on that output fails inside `project()`'s own body — a failure that only a real-compile fixture (not a string-assertion-only test) will ever catch. This is precisely why GATE-01's standing bar requires a real `typst.compile()`, not just emitted-text assertions, for this exact class of change.

**Phase to address:**
Dead-config-cleanup phase (typst_elements pass-through, item A). Must be a named fixture case distinct from the `papersize` case — do not assume "one string key worked, therefore all string keys work," since `papersize` and `fontsize` have opposite correctness requirements under the current `_format_typst_value` rule.

---

### Pitfall 9: `typst_template_mapping` REPLACES the default mapping, it does not extend it — pass-through logic must not assume the default 3-key set is always present

**What goes wrong:**
`TemplateEngine.__init__` sets `self.parameter_mapping = parameter_mapping` (the raw value of `typst_template_mapping`, if the user set it — template_engine.py:98-99) with **no merge** against `DEFAULT_PARAMETER_MAPPING`. A user who sets `typst_template_mapping = {"project": "heading"}` to rename just one mapped key loses the `author`→`authors` and `release`→`date` mappings entirely (pre-existing behavior, not new). If the new pass-through logic for `typst_elements` is implemented by computing "keys not present in `self.parameter_mapping`'s *values*" or by hard-coding an assumption that `project`/`author`/`release` are always mapped, it will misbehave for any project that has customized `typst_template_mapping` — either double-forwarding a key that's already mapped under a different name, or failing to recognize a genuinely-unmapped `typst_elements` key because the mapping shape it expected isn't there. This interacts with the already-repaired `typst_package` path too (Phase 22.2, D-05): on the package-only route, `self.parameter_mapping` defaults to `{}` (not `DEFAULT_PARAMETER_MAPPING`, template_engine.py:100-104), specifically so nothing is back-filled into a Typst-Universe package function that never asked for it — a pass-through implementation that doesn't respect this same "package path passes nothing by default" philosophy would reintroduce exactly the class of bug Phase 22.2's D-05/BUG-B fixed for `date`.

**Why it happens:**
`typst_template_mapping` and `typst_elements` are two independently user-configurable knobs feeding into the same `map_parameters()` call; it's easy to design the `typst_elements` pass-through in isolation, tested only against the DEFAULT mapping, without re-checking the interaction when `typst_template_mapping` is ALSO customized or when the package-only route (empty default mapping) is active.

**How to avoid:**
Base the pass-through decision on `typst_elements`'s own keys directly (per Pitfall 7's recommendation — pass `typst_elements` as an explicit, separate argument), and for each `typst_elements` key, only skip forwarding it if that EXACT key is present in `self.parameter_mapping`'s current keys (whatever that mapping resolved to — default, user-overridden, or the empty package-path default) — never assume the 3-key default shape is present. Add a fixture combining `typst_template_mapping` (customized) with `typst_elements` (pass-through keys) to prove the two configs compose correctly, plus a fixture confirming the package-only path's "pass nothing unless explicitly configured" invariant still holds with a `typst_elements` pass-through key configured.

**Warning signs:**
A `typst_elements` pass-through key that IS covered by a customized `typst_template_mapping` gets forwarded twice under two different names, or a legitimate pass-through key is dropped because the mapping-presence check assumed the default 3-key shape.

**Phase to address:**
Dead-config-cleanup phase (typst_elements pass-through, item A) — cross-reference against the Phase 22.2 CONF-02/CONF-03 fixture shapes (`tests/test_package_only_config_gate.py`) since this todo explicitly names that gate as its template.

---

### Pitfall 10: A vacuous GATE-01 regression fixture — proving nothing, passing either way

**What goes wrong:**
A fixture that merely asserts "the build succeeds" or "the config value is registered / appears somewhere in the emitted text" passes identically whether or not the actual fix is present — this is precisely the failure mode that let `typst_output_dir`, `typst_toctree_defaults`, and the `typst_elements` non-mapping-key gap survive for multiple milestones behind registration-only tests (`tests/test_config.py:112-156`, `tests/test_config_toctree_defaults.py:9-236` — both explicitly cited in the pending todo as tests that check `hasattr(app.config, "typst_toctree_defaults")` / value equality on the CONFIG object, never on emitted OUTPUT). For PR#98 specifically: a fixture that checks `"figure(" in text` without ALSO checking `"heading(level:" not in text` near the table, or without a real `typst.compile()`, would pass even if Pitfall 2's fallthrough bug is present (both `figure(...)` AND a stray `heading(...)` get emitted — the substring assertion is satisfied either way).

**Why it happens:**
Positive-only assertions ("the new thing is present") are easier to write than negative/differential ones ("the old broken thing is absent," "this exact config value changes this exact byte range of output," "this real compile fails without the fix"), and they're the ones that naturally come to mind first when writing a fixture for a new feature.

**How to avoid:**
Follow the two-part discipline already established by Phase 22.2's `test_package_only_config_gate.py` and required by this milestone's standing GATE-01 bar: (1) a `TestPreFixBasisFailureProof`-style class that reconstructs the pre-fix shape FROM the post-fix emitted output (e.g., for typst_elements: strip the pass-through argument back out and confirm a DIFFERENT compile-time behavior results; for PR#98: re-insert a stray `heading(` before the `figure(` and confirm the reconstructed document either compiles to visibly different content or — where applicable — fails a real compile) and (2) for every phase touching this milestone's three change classes, actually re-run the CURRENT gate test against the PRE-FIX commit (e.g. `git stash`/`git checkout <parent>` the source change only, keep the test) and confirm it goes RED, then restore the fix and confirm GREEN — the literal red→green discipline `.planning/PROJECT.md`'s Phase 22.2 verification history describes ("verifier re-ran the current gate against the pre-fix commit to prove red→green"). A fixture that has never been observed to fail is not proven to test anything.

**Warning signs:**
A new fixture that passes on the very first run, before the implementation code exists (comment it out and the test still passes) — the clearest possible signal of a vacuous fixture.

**Phase to address:**
Every phase in this milestone (PR#98, typst_elements pass-through, typst_toctree_defaults removal) — this is the standing GATE-01 bar restated, not a one-off pitfall.

---

### Pitfall 11: Docs "working example" written before the pass-through implementation actually ships — reintroducing a phantom (just a differently-shaped one)

**What goes wrong:**
`docs/source/user_guide/configuration.rst:197-200` currently shows `typst_papersize = "a4"` / `typst_fontsize = "11pt"` as top-level config names — both unregistered phantoms (per the phantom-config-names todo). The natural-seeming fix, once (A) ships, is to rewrite these as a `typst_elements = {"papersize": "a4", "fontsize": "11pt"}` example. But per Pitfall 8, `fontsize` as a plain Python string is NOT correctly handled by `_format_typst_value`'s blanket string-quoting unless the pass-through implementation specifically adds length-vs-string handling for it. If the docs example is written and merged BEFORE that length-handling half of (A) is actually implemented and proven, the doc goes from "cites a phantom config name that Sphinx silently warns about or ignores" to "cites a real, registered config path that reliably crashes `typst.compile()` if a reader copies it verbatim" — a strictly worse failure mode (loud, fatal, and shipped as an official example) than the one it was meant to fix. This is the exact ordering dependency flagged in the phantom-config-names todo's own Solution section (its cross-reference to the typst_elements todo's D-18): "`typst_papersize`/`typst_fontsize` 系の記述は削除のみが安全" ("only deletion is safe") until the pass-through's type-handling is actually done.

**Why it happens:**
Docs and implementation for the same feature are natural to bundle into one mental "fix the fontsize story" task, and it's tempting to write the "after" example as soon as the config value is *registered* and *forwarded at all* — without separately confirming the forwarded value round-trips through `_format_typst_value` as the CORRECT Typst type, not just "some value that appears in the output."

**How to avoid:**
Sequence strictly: (1) ship and prove (A)'s pass-through including Pitfall 8's typed-value handling, with a real-compile fixture showing `fontsize` specifically (not just `papersize`) compiles correctly end-to-end; only then (2) write the docs "working example" using `typst_elements` for `papersize`/`fontsize`, and — as extra insurance — add a docs-example compile check (or reuse an existing `docs-pdf`-style gate) that actually builds the documented example rather than trusting it by inspection. Until (1) is proven, the phantom-names doc fix should only DELETE the broken `typst_papersize`/`typst_fontsize` lines, never replace them with an unverified `typst_elements` example.

**Warning signs:**
A docs PR that adds a `typst_elements = {"fontsize": ...}` example lands in the same or an earlier commit than the fixture proving `fontsize`'s type handling — check commit/plan ordering, not just content correctness.

**Phase to address:**
The docs-cleanup phase must be sequenced AFTER (not parallel with, and not before) the typst_elements pass-through phase for this specific pair of lines — the two other phantom fixes (`typst_author`→`typst_authors`, deleting `typst_use_codly`/`typst_code_line_numbers`) have no such dependency and can proceed independently.

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| Whitelist only `papersize`/`fontsize` (the two named example keys) instead of a general pass-through mechanism for `typst_elements` | Smaller diff, avoids Pitfall 6's "any unknown key is fatal" surface entirely for the default template | Any OTHER `typst_elements` key a user adds still silently drops (the ORIGINAL bug, just narrowed) — reopens the same class of dead-config bug for a subset of keys | Acceptable as an explicit, documented v1 scope-narrowing (mirrors this project's own precedent of "B: delete" for `typst_toctree_defaults`) — NOT acceptable if the docs claim general `typst_elements` pass-through without qualification |
| Reuse the OLD caption-less `:width:` wrap verbatim for the captioned case (Pitfall 3, option a) instead of the figure-precedent wrap (option b) | Less code to write, reuses `_build_columns_fr_arg`/`_format_table_cell` exactly as-is | Diverges from the `visit_figure`/`depart_figure` precedent for width semantics, creating two different "what does width mean" answers in the same file depending on whether a table has a caption | Acceptable only if explicitly decided and documented as intentional, not a default fallen into by omission |
| Skip `<label>`/numref support for captioned tables entirely in this milestone (Pitfall 5) | Avoids the duplicate-label collision risk entirely — `kind: table` auto-numbering alone needs no id/label logic | Users who add `:name:` to a captioned table for cross-referencing get no working `:numref:` — a known, if unrequested, gap | Acceptable for this milestone since the todo's stated scope is "Table N" auto-numbering, not cross-reference support — should be recorded as an explicit follow-up item, not silently absent |

## "Looks Done But Isn't" Checklist

- [ ] **Captioned table renders as `figure(...)`:** verify with a fixture containing a SECOND table (captioned or not) in the same document — a single-table fixture cannot expose Pitfall 1's `table_cell_content` routing bug.
- [ ] **Caption + `:width:` composition:** verify a fixture exists combining BOTH in one table — testing them separately proves nothing about the combination (Pitfall 3).
- [ ] **`typst_elements` pass-through "works":** verify BOTH `papersize` (string, correctly quoted) AND `fontsize` (length, must NOT be blindly quoted) are separately fixture-tested — proving one does not prove the other (Pitfall 8).
- [ ] **`typst_elements` pass-through is "safe":** verify a fixture with `typst_elements = {}` (default, untouched) still compiles with no `copyright:`/other baseline-metadata leakage into `project.with(...)` — Pitfall 7 is invisible unless specifically tested.
- [ ] **Regression fixtures actually regress:** verify each new gate test was observed RED against the pre-fix commit before being accepted GREEN (Pitfall 10) — not merely "the test exists and currently passes."
- [ ] **Docs `typst_elements` fontsize/papersize example:** verify the example itself was fed through a real `sphinx-build`/`typst.compile()`, not just read for plausibility (Pitfall 11).

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|----------------|-----------------|
| Pitfall 1 (caption swallowed by table_cell_content) | LOW | Add the `self.in_table = False` save/restore around the caption buffer-swap in `visit_title`/`depart_title`; no data model change needed, purely a state-flag fix |
| Pitfall 2 (fallthrough to heading emission) | LOW | Add the missing `return` on the new table-caption branch; verify via the "zero `heading(` occurrences" grep-style assertion |
| Pitfall 3 (wrong width/caption nesting) | MEDIUM | Requires picking and re-deriving the correct wrap order, likely a `depart_table` rewrite of the width-wrap branch; low risk of data loss but needs a fresh compile-verified fixture |
| Pitfall 5 (duplicate label) | LOW–MEDIUM | Add `skip_ids` threading to the new label-emission site, matching `depart_figure`'s existing contract exactly; low cost IF label support is added deliberately, MEDIUM if it was added accidentally and needs to be identified first |
| Pitfall 6/7 (unexpected-argument fatal on unknown/poison keys) | LOW | Narrow the pass-through to an explicit whitelist or a dedicated `typst_elements`-only source dict; both are small, localized changes to `writer.py`/`template_engine.py` |
| Pitfall 8 (typed vs string values) | MEDIUM | Requires adding length-detection logic (regex or explicit numeric+unit convention) to `_format_typst_value` or a wrapper around it — a real (small) feature, not a one-line fix |
| Pitfall 10 (vacuous fixture) | LOW | Re-run the existing fixture against the parent commit; if it passes red-then-green is missing, add the reconstruction/negative-case class per `TestPreFixBasisFailureProof`'s pattern |
| Pitfall 11 (premature docs example) | LOW | Revert the docs example to a deletion-only fix until the implementation dependency (Pitfall 8) is proven; no code change needed, purely a documentation-ordering fix |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| 1. Caption swallowed by table_cell_content | PR#98 reimplementation | Two-table-in-one-document fixture, real `typst.compile()`, caption text present in output |
| 2. visit_title fallthrough to heading() | PR#98 reimplementation | Assert zero `heading(level:` occurrences adjacent to the table's `figure(`/`table(` call |
| 3. caption + :width: nesting | PR#98 reimplementation | Dedicated fixture combining both, real compile, plus an explicit written decision on which wraps which |
| 4. Caption-less table stays plain table() | PR#98 reimplementation | Existing captionless-table tests must show byte-identical `table(` output (no figure wrap) after the change |
| 5. kind: table label collision | PR#98 reimplementation | Named + captioned table fixture, real compile (string-only assertions cannot catch this) |
| 6. Unknown-key unexpected-argument fatal | typst_elements pass-through phase | Negative fixture: an unrecognized key raises a real `typst.compile()` error (not just registered) |
| 7. sphinx_metadata poisoning (copyright leak) | typst_elements pass-through phase | Baseline fixture with `typst_elements = {}` but `copyright` set in conf.py — assert no `copyright:` in the show-rule call region |
| 8. Typed vs string values (fontsize) | typst_elements pass-through phase | Fixture specifically for `fontsize`, real compile, distinct from the `papersize` fixture |
| 9. typst_template_mapping interaction | typst_elements pass-through phase | Fixture combining a customized `typst_template_mapping` with a `typst_elements` pass-through key |
| 10. Vacuous fixture | Every phase (standing GATE-01 bar) | Red→green discipline: gate re-run against the pre-fix commit, observed to fail, before being accepted |
| 11. Premature docs example | Docs-cleanup phase, sequenced AFTER the pass-through phase | Docs PR review checks commit ordering against the pass-through phase's fixture landing first |

## Sources

- `typsphinx/translator.py` (this repo, `main` @ 9f8e075) — `visit_title`/`depart_title` (lines 453-584), `visit_table`/`depart_table` (2337-2485), `visit_entry`/`depart_entry` (2584-2631), `add_text` (253-267), `_emit_id_anchors` (311-382), `visit_figure`/`depart_figure`/`visit_caption`/`depart_caption` (2039-2210) — read directly for this research
- `typsphinx/template_engine.py` (same commit) — `DEFAULT_PARAMETER_MAPPING`/`map_parameters` (62-66, 186-245), `_format_typst_value` (422-453), `TemplateEngine.__init__`'s package-path parameter_mapping note (98-106) — read directly
- `typsphinx/writer.py` (same commit) — `sphinx_metadata` construction and `typst_elements` merge (200-216) — read directly
- `typsphinx/templates/base.typ` (same commit) — `project()` signature and body (39-93) — read directly
- `tests/test_package_only_config_gate.py` (same commit) — the CONF-03 red→green / difference-matrix fixture pattern this milestone's GATE-01 bar is explicitly modeled on — read directly
- `.planning/PROJECT.md` — FN-01 footnote buffer-clobber lesson (Requirements/Validated section, Phase 14 entry) and Phase 22.2 CONF-01..03 dead-config precedent (Key Decisions, Phase 22.2 entries)
- `.planning/todos/pending/2026-07-23-reimplement-pr-98-captioned-table-figure-wrap.md`
- `.planning/todos/pending/2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md`
- `.planning/todos/pending/2026-07-22-user-guide-configuration-phantom-config-names.md`
- `docs/source/user_guide/configuration.rst` (lines 140-254) — the phantom `typst_papersize`/`typst_fontsize`/`typst_author`/`typst_use_codly`/`typst_code_line_numbers` examples

---
*Pitfalls research for: typsphinx v0.6.3 milestone (config/docs 実測整合 + captioned tables)*
*Researched: 2026-07-23*

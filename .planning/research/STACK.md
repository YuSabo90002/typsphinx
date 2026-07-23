# Stack Research — v0.6.3 (config pass-through + captioned tables)

**Domain:** Sphinx→Typst translator maintenance (not greenfield) — Typst 0.15.x / Sphinx 9.1 / docutils 0.22 API facts only
**Researched:** 2026-07-23
**Confidence:** HIGH (all claims below either read from this repo's own source at the cited file:line, or empirically verified by a real `typst.compile()` in this repo's own `.venv` — see `## Verification method`)

This is a maintenance milestone on a mature codebase. There is no "recommended stack" to choose — the runtime is pinned (`typst>=0.15,<0.16`, `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, Python 3.12–3.13) and **zero new dependencies** is a hard invariant. This document instead answers the four technical-API questions the milestone's two code changes depend on, each with a file:line anchor into this repo and/or a real-compile proof.

## Verification method

Real Typst compiles were run directly against this repo's installed `typst-py` (`.venv/lib/python3.13/site-packages/typst`, resolves to typst 0.15.x per the pinned `uv.lock`) via `typst.compile(path)`, not against typst.app docs alone. Every claim marked "(verified: real compile)" below reproduces with a `.venv/bin/python -c "import typst; typst.compile(...)"` invocation you can re-run. Typst reference-page facts (figure/caption/kind semantics) were cross-checked against the official `https://typst.app/docs/reference/model/figure/` page.

---

## Q1 — `figure(table(...), caption:, kind: table)`: exact syntax, numbering, gotchas

### Exact syntax (confirmed against typst.app/docs/reference/model/figure/)

```typst
#figure(
  table(columns: (1fr, 1fr), [A], [B], [C], [D]),
  caption: [My caption],
  kind: table,
) <label>
```

`figure()` parameters relevant here:

| Param | Default | Behavior |
|---|---|---|
| `body` | required | figure content |
| `caption` | `none` | figure caption; itself exposes `position` (`top`/`bottom`, default `bottom`), `separator` (auto-localized), `body` |
| `kind` | `auto` | counter-selection key. `auto` **auto-detects** `table` when `body` is a `table` element, `raw` for code, else `image`. Explicit `kind: table` is therefore **not required for auto-detection to work** when the direct body is a `table(...)` call — but is still the correct thing to emit explicitly, because... |
| `supplement` | `auto` | the caption prefix text (e.g. "Table"). `auto` resolves from `kind` + active `text(lang:)` — for `kind: table` this resolves to `"Table"` (localized), for default/`image` kind to `"Figure"`. **No manual supplement string is needed** for the table case. |
| `numbering` | `"1"` | counter format |
| `outlined` | `true` | whether it appears in `#outline(target: figure)`-style listings |

**Auto-numbering:** Yes — `figure(..., kind: table)` auto-numbers via a counter scoped to `kind: table` that is **independent of the `kind: image`/default-figure counter**. First captioned table in a document renders as "Table 1", second as "Table 2", regardless of how many `kind: image`/plain figures precede it. Confirmed by real compile of a two-table document (both auto-numbered 1, 2 sequentially, `image`-kind figures unaffected).

**Cross-referencing:** Standard Typst label/ref — `<label>` postfix on the `figure(...)` call (markup-mode only, same constraint that already governs `visit_figure`'s `<label>` emission, see below), referenced via `@label` in markup mode. The reference text auto-renders as `"Table N"` (using the figure's own `supplement`+`numbering`), exactly mirroring how `@fig-label` already renders `"Figure N"` for typsphinx's existing image figures. **Verified: real compile** — `figure(table(...), caption:.., kind: table) <tbl-mylabel>` followed by `See @tbl-mylabel for details.` compiles clean, 10180 bytes output.

### Gotcha 1 — `columns: (1fr, ...)` inside `figure(table(...))`: NONE found

typsphinx's existing `depart_table` (translator.py:2422-2486) already emits `table(columns: (Nfr, ...), ...)` (fr-weighted, from `_build_columns_fr_arg()`, translator.py:2372-2391). **Verified: real compile** that wrapping this exact fr-weighted table shape in `figure(..., caption:, kind: table)` with a label and a cross-reference compiles cleanly — `fr` units inside a table nested in a figure are not a problem (figures don't impose a sizing context that breaks `fr` resolution the way, e.g., a bare inline context would).

### Gotcha 2 — composing with the existing `:width:` → `block(width:...)[...]` wrap

`depart_table` currently wraps the **whole `table()` call** in `block(width: ...)[#table(...)]` when `:width:` is set (translator.py:2444-2453, LEN-01 precedent). The analogous, already-proven-in-this-codebase pattern for figures is `visit_figure`/`depart_figure` (translator.py:2039-2145), which wraps the **whole `figure()` call** (not just the image) in `block(width: ...)[#figure(\n...)]` when `:figwidth:` is set (translator.py:2093-2094, 2126-2130).

**Verified: real compile of both possible compositions** — `block(width:)[#figure(table(...), caption:, kind: table)]` ("width outside", wraps the whole figure) and `figure(block(width:)[#table(...)], caption:, kind: table)` ("width inside", wraps only the table) **both compile successfully**. Recommend "width outside" (mirrors `visit_figure`'s existing idiom exactly, keeps one wrapping convention project-wide) — i.e. when a captioned `.. table:: Caption` also has `:width:`, emit:

```typst
block(width: <converted>)[#figure(
  table(
    columns: (...),
    ...
  ),
  caption: {...},
  kind: table,
)]
```

not the reverse nesting. This is a design recommendation, not a compile requirement (both work) — flagging so the planner picks one consciously rather than drifting.

### Gotcha 3 — id/label anchoring already handled differently for tables than for figures

`visit_figure` bracket-wraps the whole call in markup mode (`[#figure(...) <label>]`) specifically because Typst's `<label>` postfix is markup-mode-only syntax, invalid inside the translator's default unified code-mode statement stream (translator.py:2043-2056, a real fatal discovered by GATE-01/Issue #114).

`visit_table`, by contrast, does **not** use this pattern at all — it calls `self._emit_id_anchors(node)` at the very top of `visit_table` (translator.py:2348), **before** `self.in_table = True` is set, emitting a **separate zero-width anchor statement ahead of the table**, not a `<label>` postfix on the table/figure call itself. This existing id-anchor call is independent of the caption/figure-wrap work and does not need to change — a `<label>` postfix is only needed additionally if the milestone wants `.. table::` blocks to support `@ref`-style Typst cross-referencing with `"Table N"` text (not explicitly required by the milestone's stated scope, which only asks for the caption+numbering wrap). If added later, it must follow the `visit_figure` markup-bracket idiom, not `_emit_id_anchors`'s idiom — they are two different, non-interchangeable mechanisms already coexisting in this file.

---

## Q2 — Undeclared `.with()` kwarg: compile error or silently ignored? Does base.typ need to change?

**Verified: real compile.** Calling `project.with(title: "x", unknownparam: "y")` against a `project()` that does not declare `unknownparam` produces a hard `typst.TypstError`:

```
ERROR: unexpected argument: unknownparam
```

This is **not** silently ignored — every undeclared kwarg aborts the whole compile. This is the load-bearing fact for the milestone: any pass-through fix that forwards an unmapped `typst_elements` key straight into `#show: project.with(...)` will **fatal the compile** unless the target `project()` already declares a matching parameter.

**base.typ does NOT need to change for `papersize`/`fontsize` specifically.** Read directly: `typsphinx/templates/base.typ:39-48` —

```typst
#let project(
  title: "",
  authors: (),
  date: none,
  toctree_maxdepth: 2,
  toctree_numbered: false,
  toctree_caption: "Contents",
  papersize: "a4",
  fontsize: 11pt,
  body
) = {
```

`papersize` and `fontsize` are **already declared parameters** (defaults `"a4"` / `11pt`, base.typ:46-47, and already consumed at base.typ:56/61 — `page(paper: papersize)`, `text(size: fontsize, ...)`). The bug is entirely on the Python side: `template_engine.py`'s `map_parameters()` never forwards these keys to `params`, so `project.with(...)` is called *without* `papersize:`/`fontsize:` at all, and the declared defaults silently win. **This is the opposite of a base.typ gap** — the template function's signature is already correct and ready to receive these two keys; only the Python wiring is dead.

### Gotcha — `fontsize` as a Python `str` value breaks even after wiring is fixed

The milestone's own example config is `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}` (PROJECT.md milestone description). `TemplateEngine._format_typst_value()` (template_engine.py:422-453) formats any Python `str` as a **quoted** Typst string literal (`.replace(...)` + `f'"{escaped}"'`, template_engine.py:437-440). So a naive pass-through of `typst_elements["fontsize"] = "20pt"` renders `fontsize: "20pt",` in the generated `.typ` — a quoted string, not the unquoted Typst length literal `20pt` that base.typ's `set text(size: fontsize)` (base.typ:61) requires.

**Verified: real compile** — `project.with(fontsize: "20pt")` against a `project(fontsize: 11pt, body)` that does `set text(size: fontsize)` fails with:

```
ERROR: expected length, found string
```

`papersize` does **not** have this problem — `page(paper: papersize)` (base.typ:55) genuinely wants a Typst `str` (e.g. `"us-letter"`), so the existing string-quoting behavior of `_format_typst_value` is *correct* for `papersize` and *wrong* for `fontsize`. **This means a correct implementation of (A) cannot treat every `typst_elements` value identically** — it must distinguish length-like values (which need to render as bare/unquoted Typst length literals) from string-like values (which should stay quoted). The translator already owns exactly this parsing logic: `_convert_length_to_typst()` (translator.py:3285-3343) parses a `"<number><unit>"` string via `re.fullmatch(r"(-?[0-9.]+)([a-zA-Zµ%]*)", value)` and returns a bare Typst length string (e.g. the raw source text `20pt`, unquoted) or `None` for unsupported units. That helper lives on `TypstTranslator` (translator.py), not on `TemplateEngine` (template_engine.py) — the two modules are otherwise independent (`TemplateEngine` has no translator/doctree dependency), so either (a) duplicate/extract a minimal length-detection helper into `template_engine.py`, or (b) special-case known length-typed keys (`fontsize`) at the point `typst_elements` is consumed in `writer.py`, converting them to a raw-Typst-code sentinel that `_format_typst_value` must be taught to pass through unquoted. Flag this specifically for the planner — the milestone's own PROJECT.md example (`fontsize: "20pt"`) will not compile without this fix, even after the dead-wiring bug itself is fixed.

### Existing precedent for the correct "direct pass-through" plumbing shape

`writer.py:214-216` already does exactly the pattern needed, for toctree options — bypassing `map_parameters()`'s restrictive mapping-key loop entirely:

```python
toctree_options = template_engine.extract_toctree_options(self.document)
params.update(toctree_options)
```

The same shape (`params.update(typst_elements)` called directly in `writer.py`, rather than routing `typst_elements` through `sphinx_metadata` pre-`map_parameters()` as currently happens at writer.py:208-209) is the natural, lowest-risk fix location — it mirrors an already-shipped, already-tested pattern in the same file rather than inventing a new one. Currently `typst_elements` is folded into `sphinx_metadata` (`sphinx_metadata.update(typst_elements)`, writer.py:209) and then filtered away by `map_parameters()`'s `for sphinx_key, template_key in self.parameter_mapping.items()` loop (template_engine.py:205), which only iterates the 3 `DEFAULT_PARAMETER_MAPPING` keys (`project`/`author`/`release`, template_engine.py:62-66) — any key not in that mapping, including every `typst_elements` key, is silently dropped, exactly as the pending todo (`2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md`) documents.

There is also an **already-working alternate path** for arbitrary param pass-through worth knowing about: `typst_template_function = {"name": "project", "params": {"papersize": "us-letter"}}` already reaches `project.with(...)` today, unfiltered, via `render()`'s `all_params.update(self.typst_template_params)` (template_engine.py:405-407, D-08). This confirms the template-function-call plumbing itself has no structural blocker — only the simpler, documented `typst_elements` config's specific pipeline (`sphinx_metadata` → `map_parameters()`) is broken.

---

## Q3 — docutils doctree structure for `.. table:: Caption`; how caption is stored; how Sphinx numbers tables

**Source read directly:** `.venv/lib/python3.13/site-packages/docutils/parsers/rst/directives/tables.py`.

- `Table.make_title()` (tables.py:46-57) builds a `nodes.title(title_text, '', *text_nodes)` from the directive's argument text (parsed via `self.state.inline_text(...)`, so inline markup like `**bold**` inside the caption survives as real child nodes, not flattened text).
- All three concrete directive classes — `RSTTable` (grid/simple table syntax, tables.py:169-172), `CSVTable` (tables.py:316-318), `ListTable` (tables.py:448-450) — end with the identical line: `if title: table_node.insert(0, title)`.

**Confirmed doctree shape:** the caption is stored as a `nodes.title` node **inserted as the table node's FIRST child**, i.e. `table` → `[title, tgroup, ...]`. It is **not** a `caption` node (unlike `.. figure::`, which uses a distinct `nodes.caption` type — see `visit_caption`/`depart_caption`, translator.py:2153+). This is exactly why the generic `visit_title` dispatch currently mishandles it: `visit_title` has no branch for "parent is a table", so it falls through to the plain section-heading path and emits `heading(level: N, {...})` (translator.py:517-529) unconditionally.

**What `visit_title`/`depart_title` actually receive today for this case:** `node.parent` is `nodes.table`. `visit_title` currently checks only `isinstance(node.parent, nodes.Admonition) or isinstance(node.parent, nodes.topic)` (translator.py:487-489) — `nodes.table` matches neither, so it falls through to the default heading-emission branch. Because `visit_table` (translator.py:2367) has already set `self.in_table = True` *before* the title's children are visited (title is the table's first child, visited immediately after `visit_table` returns), every `add_text()` call made while rendering the title's own children routes through `add_text()`'s table-cell-buffer branch (translator.py:260-267: `if hasattr(self, "in_table") and self.in_table and hasattr(self, "table_cell_content"): self.table_cell_content.append(text)`), **not** `self.body`, for every table **after the first one in a document** (`table_cell_content` is only ever initialized in `visit_entry`/reset in `depart_entry`, translator.py:2592/2631 — never in `__init__`, so it doesn't exist as an attribute for the very first table, meaning the first table's stray heading leaks into `self.body` normally, but a second+ table's stray heading text is silently swallowed into a stale, disconnected `table_cell_content` list left over from the previous table's last cell — confirmed by direct code trace, not just the todo's prose claim). This double failure mode (heading-leak on table #1, silent swallow on table #2+) is exactly what the pending todo (`2026-07-23-reimplement-pr-98-captioned-table-figure-wrap.md`) describes and is the mechanism the fix must close by adding an explicit `isinstance(node.parent, nodes.table)` branch to `visit_title`/`depart_title` that buffer-swaps (mirroring the existing admonition/topic buffer-swap idiom at translator.py:487-503/546-562, and the caption buffer-swap idiom at `visit_caption`/`depart_caption`, translator.py:2166-2187) rather than falling through to the heading path.

**Existing cell format to match for tests:** `_format_table_cell()` (translator.py:2393-2420) emits normal cells as `{indent}{{{content}}},\n` — confirmed at translator.py:2410, i.e. `{par({text("...")})},` — and `_build_columns_fr_arg()` (translator.py:2372-2391) falls back to `(1fr, 1fr)` when colwidth data is absent/equal — both match the pending todo's stated migration target for the ported PR#98 test assertions (`{par({text(...)})}`, `columns: (1fr, 1fr)`).

**Sphinx `numfig`/`Table %s` numbering: NOT used by typsphinx, confirmed by exhaustive grep.** `grep -rn "numfig" typsphinx/` returns zero hits anywhere in the package. typsphinx's translator never touches Sphinx's own `numfig`/`numfig_format` table-numbering machinery (the system that drives HTML/LaTeX builders' "Table %s" labels via the `std` domain) — table/figure numbering in typsphinx's output is entirely delegated to **Typst's own** `kind:`-scoped figure counter (Q1), which is why the milestone's target design (`figure(table(...), caption:, kind: table)`) is the right shape: it hands numbering off to Typst natively rather than trying to thread Sphinx's `numfig` state through. No `config.numfig`/`config.numfig_format` reads are needed anywhere in this fix.

---

## Q4 — `typst_toctree_defaults` deletion: confirmed inert, deletion is safe

`grep -rn "typst_toctree_defaults" typsphinx/` returns exactly **one** hit, the registration line itself:

```
typsphinx/__init__.py:47:    app.add_config_value("typst_toctree_defaults", None, "html", [dict, type(None)])
```

No reference anywhere else in `typsphinx/translator.py`, `typsphinx/writer.py`, `typsphinx/builder.py`, or `typsphinx/template_engine.py`. The actual toctree options (`maxdepth`/`numbered`/`caption`) that DO reach the template are read directly from the doctree's `addnodes.toctree` node by `TemplateEngine.extract_toctree_options()` (template_engine.py:273-318, reading `toctree.get("numbered", False)` / `toctree.get("maxdepth", 2)` / `toctree.get("caption", "")` off the live toctree node, not off any Sphinx config value). **Deleting the `__init__.py:47` registration line is therefore a pure, inert code removal with zero behavioral impact on `typsphinx/` package code** — confirmed by the grep, not inferred.

Outside the package itself, `typst_toctree_defaults` is additionally referenced in 4 non-package locations the milestone's docs-fidelity work area (#3, out of this STACK research's technical-API scope) already targets for deletion: `docs/configuration.rst:223,245,355`, `examples/advanced/conf.py:86`, `examples/advanced/README.md:250`, `README.md:208`. None of these affect the Python package's runtime behavior; they are documentation/example surfaces only.

---

## Summary table for the roadmapper

| Question | Verdict | Confidence | Evidence |
|---|---|---|---|
| Q1: `figure(table(...), caption:, kind: table)` syntax | Exact syntax confirmed; auto-numbers "Table N" independently of image-figure counter; `fr`-columns and `:width:` composition both compile clean | HIGH | typst.app docs + 3 real compiles in this repo's venv |
| Q2: does base.typ need new params? | **No** — `papersize`/`fontsize` already declared (base.typ:46-47) with matching defaults; bug is 100% Python-side (`map_parameters` drops unmapped keys) | HIGH | Direct source read + real-compile proof of the undeclared-kwarg fatal |
| Q2 gotcha: `fontsize: "20pt"` as Python str | **Breaks** even after wiring fix — renders as a quoted Typst string, `set text(size: "20pt")` is a real Typst type error | HIGH | Real compile: `ERROR: expected length, found string` |
| Q3: table caption doctree shape | `nodes.title` inserted as `table`'s first child (`table` → `[title, tgroup, ...]`), NOT a `caption` node; Sphinx `numfig` is unused by typsphinx entirely | HIGH | docutils `tables.py` source read + exhaustive grep |
| Q4: `typst_toctree_defaults` deletion safety | Confirmed inert outside its own registration line; deletion is pure removal | HIGH | `grep -rn` across `typsphinx/` |

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|---|---|---|
| (Q2) Fix via `params.update(typst_elements)` directly in `writer.py` (mirrors the existing toctree_options pattern) | Fix via widening `DEFAULT_PARAMETER_MAPPING` to a dynamic identity map inside `map_parameters()` | Only if there is a future need to *rename* `typst_elements` keys before they reach the template (not the milestone's stated need — `papersize`→`papersize` etc. is already identity); the direct-`update()` route is simpler and has an exact precedent already shipped |
| (Q1) `block(width:...)[#figure(...)]` — width wraps the whole figure | `figure(block(width:...)[#table(...)], ...)` — width wraps only the table | Both compile; only choose the "width inside" form if a future requirement needs the caption to NOT be constrained by the width box (not currently a requirement) |
| (Q1) Rely on Typst's native `kind: table` auto-counter for "Table N" | Thread Sphinx's `numfig`/`numfig_format` state through the translator | Only if a future requirement needs typsphinx's table numbers to match an HTML/LaTeX build's numbers exactly (cross-builder consistency) — out of scope; no existing wiring for this exists anywhere in the package today |

## What NOT to Use

| Avoid | Why | Use Instead |
|---|---|---|
| Passing `typst_elements` values straight through `_format_typst_value()` unmodified | Silently mis-types any length-like string value (e.g. `"20pt"`) as a quoted Typst string, producing a hard `expected length, found string` compile fatal for `fontsize` specifically | Detect length-like values (reuse/extract `_convert_length_to_typst`'s regex) and format them as raw/unquoted Typst source, not as a formatted-string literal |
| Adding a `kind: table` handling path that also emits a `<label>` postfix via `_emit_id_anchors()` | `_emit_id_anchors()` emits a separate anchor statement, not a markup-mode `<label>` postfix on the call itself — mixing the two anchor mechanisms on the same node is inconsistent with how `visit_figure` already does it | If table cross-referencing via `<label>`/`@ref` is added, follow the `visit_figure`/`depart_figure` markup-bracket idiom (translator.py:2039-2151) exactly, not `_emit_id_anchors` |
| Assuming `.. table:: Caption`'s title is a `caption` node (figure-style) | It's a `nodes.title`, not `nodes.caption` — a different docutils node type entirely, per direct read of `tables.py`'s `make_title()` | Add an explicit `isinstance(node.parent, nodes.table)` branch to the existing `visit_title`/`depart_title` dispatch |

## Sources

- `typsphinx/templates/base.typ:1-93` (`project()` signature, read in full)
- `typsphinx/template_engine.py:62-66,186-245,405-420,422-453` (`DEFAULT_PARAMETER_MAPPING`, `map_parameters`, `render`, `_format_typst_value`)
- `typsphinx/writer.py:150-247` (per-document template render call, `sphinx_metadata`/`typst_elements`/`toctree_options` plumbing)
- `typsphinx/translator.py:260-267` (`add_text` table-cell-buffer routing), `:453-620` (`visit_title`/`depart_title`), `:2039-2151` (`visit_figure`/`depart_figure`), `:2153-2210` (`visit_caption`/`depart_caption`), `:2337-2486` (`visit_table`/`_build_columns_fr_arg`/`depart_table`), `:2584-2631` (`visit_entry`/`depart_entry`), `:3285-3343` (`_convert_length_to_typst`)
- `typsphinx/__init__.py:47` (`typst_toctree_defaults` registration, sole reference)
- `.venv/lib/python3.13/site-packages/docutils/parsers/rst/directives/tables.py` (`Table.make_title`, `RSTTable.run`, `CSVTable.run`, `ListTable.run` — read in full)
- Real `typst.compile()` runs against this repo's pinned `typst-py` (0.15.x per `uv.lock`) — HIGH confidence, reproducible: undeclared-kwarg fatal, string-vs-length-typed-fatal, `figure(table(fr-columns), caption, kind: table, <label>)` + `@label` cross-ref, both `block(width:)[figure(...)]` / `figure(block(width:)[table(...)])` compositions
- [Figure - Typst Documentation](https://typst.app/docs/reference/model/figure/) — `figure()`/`caption`/`kind`/`supplement` parameter semantics (WebFetch-verified against the live reference page, cross-checked against real-compile behavior above)
- `.planning/todos/pending/2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md`, `.planning/todos/pending/2026-07-23-reimplement-pr-98-captioned-table-figure-wrap.md` — root-cause context these findings confirm/extend
- `.planning/PROJECT.md` (Current Milestone section) — scope framing

---
*Stack research for: typsphinx v0.6.3 — config pass-through + captioned tables*
*Researched: 2026-07-23*

# Feature Research

**Domain:** Sphinx→Typst PDF builder — maintenance milestone v0.6.3 (config pass-through fidelity + captioned-table rendering + docs accuracy)
**Researched:** 2026-07-23
**Confidence:** MEDIUM (grounded primarily in direct codebase inspection — HIGH confidence; two external claims about Sphinx/LaTeX baseline behavior — MEDIUM confidence, tavily-verified against official Sphinx docs)

> Supersedes the previous (2026-07-11) version of this file, which researched the **v0.6.0 real-world robustness** milestone (Issue #114 fatal-bug fix + high-frequency dropped-node support). This version researches the **v0.6.3 config & docs 実測整合 + captioned tables** milestone: (1) `typst_elements` non-mapped-key pass-through + `typst_toctree_defaults` deletion, (2) PR#98-derived captioned-table `figure()` wrap, (3) docs fidelity (orphan file deletion + 5 phantom config names).

## Feature Landscape

### Table Stakes (Must Match Sphinx's Own HTML/LaTeX Baseline)

These are the behaviors a Sphinx PDF builder is expected to reproduce faithfully. typsphinx already accepts this bar for figures (v0.6.0/v0.6.1 FIG-01/FIG-02); captioned tables are the one node kind where it currently regresses to source-code-literal output.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `.. table:: Caption` → numbered "Table N" | Confirmed (MEDIUM confidence, tavily+official-docs cross-check): Sphinx's `numfig_format` default is `{'table': 'Table %s'}`; **the LaTeX builder always assigns table numbers regardless of the `numfig` config** — PDF output is expected to number tables unconditionally, unlike HTML which gates behind `numfig=True`. typsphinx's own `figure()` handling already numbers captioned figures unconditionally via Typst's native auto-numbering (no `numfig`-equivalent plumbing exists anywhere in the codebase — confirmed via grep, zero hits). The correct target is `figure(table(...), caption: {...}, kind: table)`, which gets Typst-native "Table N" numbering for free, with **zero new config surface**. | MEDIUM | `typsphinx/translator.py` `visit_title`/`depart_title` (:453/:531) must buffer the caption when `self.in_table` (a NEW branch parallel to the existing `Admonition`/`topic` buffer-swap, not a replacement of it) instead of falling through to the generic section-heading path; `depart_table` (:2422) must wrap in `figure(..., kind: table)` |
| Caption-less table stays plain `table()` | docutils only attaches a `title` child to a `table` node when the `.. table:: Caption` directive argument is given — a bare `.. table::`, `.. csv-table::` (no caption), or `.. list-table::` has NO title child, so the existing plain `table(...)`/`block(width:...)[#table(...)]` path is untouched by construction. Sphinx never numbers or figure-wraps a caption-less table in HTML or LaTeX. | LOW (regression-only) | This is the negative-space guarantee the PR#98-derived test suite must assert explicitly (the todo's 4th test: "キャプション無しは非 figure") — not a new code path, a proof the new branch is scoped correctly and never fires for the majority of tables in the corpus, which have no caption |
| `:width:` composes with caption | The existing `:width:` → `block(width: ...)[#table(...)]` wrap (LEN-01, Phase 16) and the new caption wrap are two independent axes on the same `depart_table` call — a table can have both, either, or neither. | MEDIUM | Must nest correctly: `block(width: ...)[#figure(table(...), caption: ..., kind: table)]` when both apply — the todo explicitly flags this as the composition risk; a naive patch that special-cases one axis will silently drop the other for the caption+width intersection case |
| `:ref:`/`:numref:` resolve to a captioned table | Docutils auto-assigns a table an `id` whenever it carries a caption (same rule as figures) — this is what makes cross-referencing possible. typsphinx already has generic `refid`/`:ref:`/`:numref:`-shaped cross-reference infrastructure (`_emit_id_anchors`, XREF-01, v0.6.0 Phase 12) and figures already anchor their id via the `) <label>]` bracket-wrap in `depart_figure`. | LOW (reuse, not new) | `depart_table`'s new figure-wrap branch should reuse `depart_figure`'s exact `ids`-present bracket-and-anchor idiom (mirror, don't reinvent) so a captioned table's id anchors for free — infrastructure reuse, not a new feature to design |
| `typst_elements["papersize"]`/`["fontsize"]` affect actual PDF output | README's Custom Templates example (and the milestone context itself) explicitly names `{"papersize": "us-letter", "fontsize": "20pt"}` as the motivating case — a PDF-page-format setting a user writes in `conf.py` that silently has zero effect is the exact "registered but dead" defect class this milestone's config sweep targets (3rd/4th instance after `typst_output_dir`/`typst_package` in Phase 22.2). Confirmed empirically dead by grep of generated `.typ` output (0 occurrences of the configured values). | MEDIUM | See "typst_elements pass-through scope" section below — the fix is NOT free-form; `fontsize` has a real type-mismatch trap (see Pitfalls) |
| Docs match the registered config surface | `docs/source/user_guide/configuration.rst` is the one config-reference page reachable from the toctree (post-Phase-22.4 D-12 relink) — every example a reader can copy-paste into `conf.py` must either work or not exist on the page at all. 5 of its examples currently name unregistered config values. | LOW | Pure prose edit once the pass-through lands for papersize/fontsize; pure deletion for the codly pair and the bare-tuple `typst_author` |
| Orphan `docs/configuration.rst` removed | 526-line file, unreachable from any toctree, references a package name (`sphinxcontrib.typst`) that has never been this project's name — pure dead weight with zero readers able to find it organically, but a search-engine or direct-URL visitor could still land on wrong instructions | LOW | Deletion only — no rewrite needed since it's unreachable |
| `typst_toctree_defaults` removed everywhere | Registered (`__init__.py:47`) but referenced nowhere in `translator.py`/`writer.py`/`builder.py`/`template_engine.py` (confirmed by grep) — real toctree option resolution (`maxdepth`/`numbered`/`caption`) happens per-directive via `TemplateEngine.extract_toctree_options()` reading the doctree, never this config value. Per-directive `:maxdepth:` already covers the use case; wiring a second global-default layer adds config surface without adding capability. | LOW | Delete from `__init__.py:47`, `docs/configuration.rst` (moot if that file is also deleted), `examples/advanced`, `README.md:208`, and `tests/test_config_toctree_defaults.py` (registration-only tests, 236 lines, all assert existence not effect — the todo explicitly notes these tests never caught the defect) |

### `typst_elements` Pass-Through — Recommended Scope (Curated, Not Arbitrary)

**Root cause (confirmed by direct code read, HIGH confidence):** `TemplateEngine.map_parameters()` (`template_engine.py:186-213`) loops over `self.parameter_mapping.items()` — which defaults to `DEFAULT_PARAMETER_MAPPING = {"project": "title", "author": "authors", "release": "date"}` (3 keys only) — and **silently drops any key not in that mapping**. `writer.py:208-209` merges `typst_elements` into `sphinx_metadata` first, so `papersize`/`fontsize` genuinely reach `map_parameters()`'s input, but are then discarded by the loop shape itself, never by a deliberate filter.

**What `base.typ`'s `project()` already declares (read directly, HIGH confidence):**

```
title, authors, date,                                # <- covered by DEFAULT_PARAMETER_MAPPING (project/author/release)
toctree_maxdepth, toctree_numbered, toctree_caption,  # <- covered by extract_toctree_options() (doctree-derived, NOT typst_elements)
papersize, fontsize,                                  # <- DECLARED but UNREACHABLE from any config today
body
```

This means exactly **two** `project()` parameters — `papersize` and `fontsize` — are dead ends with no config path at all, and they already exist in the function signature. No `base.typ` change is required to wire them.

**Recommendation: curated allowlist, not arbitrary key pass-through.**

- **Pass through directly (table stakes):** any `typst_elements` key whose name **exactly matches** an already-declared `project()` parameter not otherwise sourced (today: `papersize`, `fontsize`). Forward verbatim by key name — no renaming needed, unlike the Sphinx-native `project`/`author`/`release` keys, which exist specifically to translate Sphinx-native names into template-native ones.
- **Do NOT implement blind arbitrary-key forwarding of the whole `typst_elements` dict into `project.with(...)`.** A typo or a key that doesn't match any `project()` parameter (e.g. `{"paper_size": "a4"}` instead of `{"papersize": "a4"}`) produces a hard Typst compile error ("unexpected named argument") on the *default* template — turning a silent-no-op bug into a build-breaking one for any user who mistypes a key. This is the real tension the milestone context calls out, and it argues for filtering, not for "support everything."
- **This is not gold-plating avoidance for its own sake — it's avoiding duplicate machinery.** `typst_template_function` already has an established, working, genuinely-arbitrary key/value pass-through path: `typst_template_function = {"name": "ieee", "params": {"abstract": "...", "index-terms": [...]}}` renders every `params` entry verbatim via `_format_typst_value()` into `#show: <func>.with(...)` (confirmed at `template_engine.py:397-411`; this is how the existing `docs/source/user_guide/configuration.rst` "Typst Package" example already works for **custom/package templates**). `typst_elements` pass-through should be scoped to the **bundled default template's own declared knobs** — a narrower, safer sibling — not a second general-purpose arbitrary-params channel that duplicates `typst_template_function.params`'s job with a weaker safety story (no matching function signature to fail against on the package path, since Python can't introspect a Typst function's parameter names).
- **`lang` is NOT currently a `project()` parameter** — it's hardcoded (`set text(size: fontsize, lang: "en")`, `base.typ:61`). Supporting `typst_elements["lang"]` would require a `base.typ` change (add a `lang: "en"` parameter, wire it into the `set text(...)` call) — this is a legitimate v2/differentiator, not table-stakes for this milestone, since the milestone's own motivating example only names `papersize`/`fontsize`.

**Critical pitfall to flag for planning (HIGH confidence, direct code read):** `papersize` and `fontsize` are **not interchangeable in how they must be emitted**. `_format_typst_value()` (`template_engine.py:422-453`) quotes every Python `str` as a Typst string literal. `papersize` is correctly a Typst **string** (`paper: "a4"` / `paper: "us-letter"` — matches `page(paper: papersize, ...)`), so passing the Python string `"us-letter"` through verbatim is correct. `fontsize`, however, is declared in `project()`'s own signature as an **unquoted Typst length** (`fontsize: 11pt`, no quotes) consumed by `set text(size: fontsize, ...)` — `text()`'s `size:` parameter requires a length, not a string. If a user writes the milestone's own example, `typst_elements = {"fontsize": "20pt"}` (a Python **string**, exactly as shown in the milestone context and README), naive pass-through via `_format_typst_value()` emits `fontsize: "20pt"` — a quoted string where Typst expects a length — which is a **real compile-time type error**, not a silent no-op. The implementation must special-case length-shaped values (parse a `"20pt"`/`"1.2em"`-style string and emit it unquoted, or accept only numeric-typed input) — analogous to the existing `_convert_length_to_typst` helper already used elsewhere in `translator.py` for CSS-length conversion, though that helper lives in a different module and converts a different unit family, so it is pattern-reusable, not directly reusable. **This must be covered by the mandated config→output real-`typst.compile()` regression fixture** — a registration-only test would not catch a compile-time type error either, since the failure only manifests when Typst actually parses the emitted `.typ`.

### Anti-Features / Explicit Over-Reach (Out of Scope for This Milestone)

| Feature | Why It Looks Tempting | Why It's Over-Reach Here | What To Do Instead |
|---------|------------------------|---------------------------|---------------------|
| Auto-generated "List of Tables" page | HTML/LaTeX-adjacent tooling sometimes has this; sounds like a natural companion to "Table N" numbering | Confirmed (tavily+official docs, MEDIUM confidence): **no official Sphinx builder auto-generates a List of Tables** — LaTeX users who want one add `\listoftables` manually themselves; it is not part of Sphinx's own numfig/caption machinery at all. There is no baseline to "match faithfully" here — building one would be a genuinely new feature invented from scratch, not a fidelity fix | Nothing — not even deferred; there's no Sphinx precedent motivating it |
| `numfig`-gated table numbering (config toggle) | Sphinx's own HTML builder gates figure/table numbering behind the `numfig` config (default `False`) | typsphinx has **never** implemented `numfig` gating anywhere (zero references in the codebase) — figures are unconditionally auto-numbered by Typst's native `figure()` today, and the LaTeX builder (the closer analog for a single-PDF-document builder) **always** numbers regardless of `numfig`. Adding a `numfig`-style toggle now would be new config surface inconsistent with the figure precedent already shipped, not a fidelity fix | Ship unconditional native Typst numbering for tables, matching the already-shipped figure behavior |
| Arbitrary `typst_elements` key pass-through (any key, forwarded blind) | Feels more "complete" / avoids maintaining an allowlist | Duplicates `typst_template_function.params`'s already-shipped arbitrary-pass-through role, with a weaker safety story on the default-template path (no function-signature contract to validate against short of a real compile); risks converting a currently-silent-but-harmless no-op into a hard build break for any conf.py typo | Curated allowlist scoped to `project()`'s actually-declared, currently-unreachable params (`papersize`, `fontsize` today) |
| `typst_papersize`/`typst_fontsize` as **top-level** config values (mirroring the phantom docs names literally) | The phantom docs already use this shape; least-diff "just register what's written" | These are genuinely different config surface than `typst_elements["papersize"]` — adding two more top-level `add_config_value()` registrations to satisfy stale docs text would grow the config surface rather than shrink it, working against this milestone's own "dead config cleanup" theme (its stated goal is fewer inert options, not more registered options that mirror docs typos) | Route through the existing `typst_elements` dict (already registered, already documented, just currently broken) |
| Rewriting `typst_author` (singular) as a new "simple tuple" mode under `typst_authors` | Minimizes deleted doc content; the "Simple Format" framing is appealing to keep | The **real, registered** `typst_authors` (`__init__.py:57`) is typed `[dict, type(None)]` and its actual consumption in `template_engine.py` (`_convert_to_authors_tuple` / D-07 in `map_parameters`) expects the **detailed dict** shape (`{"Name": {"department": ..., ...}}`) shown directly below it in the same docs page — there is no code path that accepts a bare tuple of name strings under `typst_authors`, and standard Sphinx `author` (a single string) already covers the truly simple case | Delete the "Simple Format" subsection outright; the adjacent "Detailed Format" subsection already documents the one real, working shape |

## Feature Dependencies

```
[typst_elements curated pass-through: papersize/fontsize]
    └──REQUIRED BY──> [docs: typst_papersize/typst_fontsize → working typst_elements examples]
                           (docs cannot show a WORKING example until the pass-through exists --
                            the phantom-names todo explicitly calls this out as a hard ordering
                            constraint, not a preference: "D-18 が解決されるまでは...削除のみが安全")

[captioned-table figure-wrap]
    └──independent of──> [typst_elements pass-through]
                           (no shared code path -- visit_title/depart_table vs.
                            template_engine.map_parameters -- can ship in either order
                            or in parallel)

[typst_toctree_defaults deletion]
    └──independent of──> [both of the above]
                           (pure deletion across __init__.py/docs/examples/README/tests;
                            no runtime code depends on it today, confirmed by grep)

[orphan docs/configuration.rst deletion]
    └──independent of──> [everything else]
                           (unreachable file; safe to delete in any order)

[docs: 5 phantom-name fixes]
    └──requires──> [typst_elements pass-through, for 2 of the 5 names only]
    └──no dependency──> [the other 3 names: typst_author, typst_use_codly,
                          typst_code_line_numbers are pure deletions regardless
                          of what else ships]
```

### Dependency Notes

- **Docs rewrite for `typst_papersize`/`typst_fontsize` requires the `typst_elements` pass-through to land first:** the phantom-names todo itself flags this ordering hazard — writing a "working" `typst_elements = {"papersize": ..., "fontsize": ...}` example into the docs before the pass-through ships would just create a **6th** silently-dead-config instance in the docs, the exact defect class this milestone exists to eliminate. If sequencing puts the docs phase before the pass-through phase, the safe interim move is deletion-only for those two names (same as the other 3).
- **Captioned-table figure-wrap and `typst_elements` pass-through do not share any code path** (`translator.py` visitor-pattern vs. `template_engine.py` parameter mapping) and can be planned as independent phases/waves with no sequencing constraint between them.
- **`typst_toctree_defaults` deletion is the lowest-risk item in the milestone** — it is provably dead (zero runtime references via grep across all 4 core modules), so its removal cannot regress any existing behavior; the only work is deleting registration + docs + example + the 236-line registration-only test file, `tests/test_config_toctree_defaults.py`, which the todo explicitly names as never having caught the defect in the first place.

## MVP Definition (Milestone-Scoped, Not Product-Scoped)

This is a bugfix/maintenance milestone, not a product launch — "MVP" here means the minimum bounded correct fix per item, with an explicit line against scope creep on each.

### Ship This Milestone

- [ ] `.. table:: Caption` → `figure(table(...), caption: {...}, kind: table)`, unconditional native "Table N" numbering, composed correctly with the existing `:width:` wrap — real-compile regression fixture covering caption-only, caption+width, caption-with-inline-markup, and the caption-less negative case (4 tests, mirroring the PR#98-derived todo)
- [ ] `typst_elements["papersize"]` and `["fontsize"]` reach `project()`'s already-declared same-named parameters; `fontsize`'s string→unquoted-length emission handled correctly — real-compile config→output regression fixture (mirrors Phase 22.2's `test_package_only_config_gate.py` pattern)
- [ ] `typst_toctree_defaults` deleted from `__init__.py`, `docs/configuration.rst` (or moot if deleted), `examples/advanced`, `README.md:208`, and its registration-only test file
- [ ] Orphan `docs/configuration.rst` deleted
- [ ] `docs/source/user_guide/configuration.rst`: `typst_author` → delete "Simple Format" section; `typst_use_codly`/`typst_code_line_numbers` → delete (both occurrences, :154/:160 and :245-246); `typst_papersize`/`typst_fontsize` → rewrite as working `typst_elements` examples **iff** the pass-through phase has already landed in the same milestone, else delete-only

### Explicitly Not This Milestone (Backlog / Never)

- [ ] List-of-tables auto-generation — no Sphinx precedent exists to match; would be invented, not ported
- [ ] `numfig`-style config gating for table/figure numbering — inconsistent with the already-shipped unconditional figure-numbering precedent
- [ ] Arbitrary (non-allowlisted) `typst_elements` key pass-through — duplicates `typst_template_function.params`'s existing role with a weaker safety story
- [ ] `typst_elements["lang"]` support — requires a `base.typ` change (new `project()` parameter) the milestone's own motivating example (papersize/fontsize only) doesn't ask for; candidate for a future milestone if requested
- [ ] `typst_papersize`/`typst_fontsize` as new **top-level** `add_config_value()` registrations — would grow config surface, working against this milestone's own dead-config-cleanup theme

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Captioned-table figure-wrap (Table N numbering) | HIGH — silent heading-injection bug affects every `.. table:: Caption` in any real doc corpus | MEDIUM | P1 |
| `typst_elements` papersize/fontsize pass-through | HIGH — the single most commonly-requested PDF customization (page size, font size) is currently a complete no-op | MEDIUM (incl. the fontsize type-mismatch fix) | P1 |
| `typst_toctree_defaults` deletion | LOW direct user value, HIGH project-hygiene value (closes a known-dead-config class) | LOW | P1 (cheap, bounded, matches milestone theme) |
| Orphan `docs/configuration.rst` deletion | LOW (unreachable page) but non-zero risk reduction (direct-URL/search-engine visitors) | LOW | P1 |
| 5 phantom config names in `user_guide/configuration.rst` | MEDIUM — directly prevents a copy-paste-from-docs user from writing dead config into `conf.py` | LOW (once the ordering dependency on the pass-through phase is respected) | P1 |
| `typst_elements["lang"]` support | LOW-MEDIUM (i18n users) | MEDIUM (base.typ change) | P3 (future milestone) |
| List-of-tables generation | LOW-MEDIUM (nice-to-have for large reference docs) | HIGH (no Sphinx baseline to port from) | Not planned |

**Priority key:**
- P1: In this milestone
- P3: Future consideration, not currently requested by any motivating example
- Not planned: No Sphinx-ecosystem precedent to match; would be net-new feature invention, contrary to the milestone's maintenance-cycle framing (PROJECT.md "Out of Scope": "New translation features / new reST constructs — this is a maintenance cycle, not a feature cycle")

## Baseline Comparison (Sphinx HTML/LaTeX vs. typsphinx Target)

| Behavior | Sphinx HTML | Sphinx LaTeX (closer PDF analog) | typsphinx Target |
|----------|-------------|-----------------------------------|-------------------|
| `.. table:: Caption` numbering | "Table N" only if `numfig=True` (default `False`) | **Always** numbered, `numfig` irrelevant (MEDIUM confidence, tavily+docs-confirmed) | Always numbered (matches LaTeX; matches typsphinx's own existing unconditional figure-numbering) |
| Table without caption | Never numbered | Never numbered | Never numbered — stays plain `table()`, no `figure()`/`kind: table` wrap |
| `numref` to a table | Works when numbered | Works when numbered | Should work for free via existing generic `refid`/id-anchor infrastructure once the id anchor is wired into the new figure-wrap branch (mirror `depart_figure`) |
| List of Tables page | Not auto-generated | Not auto-generated (manual `\listoftables` only) | Not built — no baseline motivates it |
| `latex_elements` config shape | N/A | **Curated dict of known keys** (`papersize`: `a4paper`/`letterpaper`; `pointsize`: `10pt`/`11pt`/`12pt`; plus `preamble`/`geometry`/`fncychap`/etc. — MEDIUM confidence, tavily+docs-confirmed) each mapped to a specific template insertion point, **not** arbitrary blind pass-through to `\documentclass` | `typst_elements` should follow the same shape: a curated, known-key dict (today: `papersize`, `fontsize`) mapped to specific `project()` parameters — direct architectural precedent for the "curated over arbitrary" recommendation above |

## Sources

- `typsphinx/templates/base.typ` (direct read, HIGH confidence) — authoritative source for `project()`'s declared parameter set
- `typsphinx/template_engine.py` (direct read, HIGH confidence) — `DEFAULT_PARAMETER_MAPPING`, `map_parameters()`, `_format_typst_value()`, `typst_template_function` params handling
- `typsphinx/writer.py` (direct read, HIGH confidence) — `sphinx_metadata`/`typst_elements` merge site
- `typsphinx/translator.py` (direct read, HIGH confidence) — `visit_title`/`depart_title`, `visit_table`/`depart_table`, `visit_figure`/`depart_figure`/`visit_caption`/`depart_caption` (the buffer-swap idiom to mirror), grep confirming zero `numfig` references anywhere in the codebase
- `typsphinx/__init__.py` (direct read, HIGH confidence) — the 12 registered `typst_*` config values (lines 44-62)
- `docs/source/user_guide/configuration.rst` (direct read, HIGH confidence) — the 5 phantom config-name locations
- `.planning/todos/pending/2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md`, `.planning/todos/pending/2026-07-22-user-guide-configuration-phantom-config-names.md`, `.planning/todos/pending/2026-07-23-reimplement-pr-98-captioned-table-figure-wrap.md` (project root-cause records, HIGH confidence — pre-investigated with file/line evidence)
- Sphinx official docs, `numfig`/`numfig_format` config semantics, tables-without-captions-not-numbered, LaTeX-always-numbers-regardless-of-numfig, no-auto-List-of-Tables (MEDIUM confidence — tavily search cross-checked against `sphinx-doc.org/en/master/usage/configuration.html`)
- Sphinx official docs, `latex_elements` curated-key-dict shape (`papersize`/`pointsize`/`preamble`/etc.) (MEDIUM confidence — tavily search cross-checked against `sphinx-doc.org/en/master/latex.html`)

---
*Feature research for: typsphinx v0.6.3 (config & docs fidelity + captioned tables)*
*Researched: 2026-07-23*

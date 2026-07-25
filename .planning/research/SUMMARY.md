# Research Summary — typsphinx v0.6.3

**Project:** typsphinx — Sphinx→Typst PDF translator
**Domain:** Maintenance milestone — config/docs fidelity + captioned-table rendering
**Researched:** 2026-07-23
**Confidence:** HIGH (direct source reads + real `typst.compile()` verification)

## Executive Summary

typsphinx v0.6.3 is a bounded maintenance milestone targeting three specific defects in a mature, production codebase: (1) two fatal bugs in captioned-table rendering from visit_title's stale dispatch and a leftover buffer from adjacent table cells, (2) Python-side wiring failure preventing two already-declared Typst template parameters (`papersize`, `fontsize`) from reaching output, and (3) five phantom config names shipped in documentation referring to unregistered values. All three changes are independently scoped with one critical sequencing constraint: documentation rewrite for `typst_elements` examples must occur AFTER the pass-through implementation is proven, to avoid shipping a "working" example that actually fails at `typst.compile()` time.

**Recommended approach:** Four independent phases in strict order (trivial deletion → translator fixes → config wiring → docs cleanup). Each phase includes real-compile regression fixtures; the captioned-table phase must test multi-table documents to expose the stale-buffer bug. The pass-through phase adds one parameter to an existing method while leaving Phase 22.2's prior code untouched—low integration risk.

**Key risks and mitigations:** (a) **State-machine fallthrough in `visit_title`** — new table-caption branch must explicitly `return` early and set `in_table = False` during buffering to prevent routing to stale cell buffer; single-table tests cannot expose this. (b) **Type mismatch in `fontsize`** — unlike `papersize` (Typst string, correctly quoted), `fontsize` is Typst length literal that breaks if quoted; requires special handling. (c) **Documentation ordering** — docs example showing `typst_elements = {"fontsize": "20pt"}` written before type-handling proof converts silent-no-op into fatal compile error for copy-paste users.

## Key Findings

### Recommended Stack (from STACK.md)

**Core technical facts verified by direct source read + real `typst.compile()`:**
- **Typst `figure(table(...), caption: {...}, kind: table)` auto-numbers** as "Table N" via independent counter, auto-supplement localized, no manual numbering config needed
- **`papersize`/`fontsize` already declared in base.typ** (lines 46–47) — bug is 100% Python-side (`map_parameters()` filters them out), NOT a template gap
- **Undeclared Typst kwargs are fatal** — `project.with(unknownkey: ...)` aborts compile with "unexpected argument" error; pass-through must be curated, not arbitrary
- **`fontsize` type mismatch:** `base.typ` declares `fontsize: 11pt` (unquoted length), consumed by `set text(size: fontsize)`. Python `_format_typst_value()` quotes every string → `fontsize: "20pt"` (quoted) → Typst type error ("expected length, found string"), even after wiring fix. `papersize` IS correctly a Typst string. These two keys have OPPOSITE type requirements.
- **Table caption is `nodes.title`, not `nodes.caption`** — docutils inserts as first child. This is why `visit_title`'s existing dispatch (checks only `Admonition`/`topic` parents) falls through to section-heading emission, emitting stray `heading()`.
- **`typst_toctree_defaults` is confirmed inert** — grep zero hits in `translator.py`, `writer.py`, `builder.py`, `template_engine.py`. Deletion is pure code removal.

### Expected Features (from FEATURES.md)

**Captioned-table numbering (table stakes):**
- Tables with captions: `figure(table(...), caption: {...}, kind: table)` for native "Table N" numbering
- Tables without captions: stay plain `table()` — never speculatively figure-wrapped
- Caption + `:width:` compose correctly — width wraps whole `figure()` call (matching `visit_figure` precedent)

**`typst_elements` pass-through (curated, not arbitrary):**
- `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}` reaches `project()` parameters
- Curated allowlist only (only `base.typ`'s declared params today), NOT arbitrary forwarding (which duplicates `typst_template_function.params` with weaker safety)
- NOT new top-level `typst_papersize`/`typst_fontsize` registrations (would grow surface, working against dead-config-cleanup theme)

**Config cleanup:**
- Orphan `docs/configuration.rst` deleted (unreachable, 526 lines, wrong package name)
- Five phantom names in `docs/source/user_guide/configuration.rst`: `typst_author` (delete "Simple Format"), `typst_use_codly`/`typst_code_line_numbers` (delete), `typst_papersize`/`typst_fontsize` (delete-only for now; rewrite as working examples ONLY after pass-through proven)

**Critical dependency:** Docs rewrite for `papersize`/`fontsize` examples can ONLY happen after pass-through phase ships and is proven end-to-end. Otherwise, docs show a "working" example that actually fails at compile time (Pitfall 11).

### Architecture Approach (from ARCHITECTURE.md)

**Three independent changes, minimal file overlap:**

1. **Captioned-table figure wrap** — only `translator.py` (new branch + one instance var):
   - Add `elif isinstance(node.parent, nodes.table):` to `visit_title`/`depart_title` with buffer-swap + explicit `self.in_table = False` guard (Pitfall 1 prevention)
   - Add explicit `del self.table_cell_content` in `depart_table` (fixes stale buffer on 2nd+ tables)
   - Branch `depart_table` on new `self.table_caption` instance var for 4-case emission matrix (caption/width combinations)

2. **`typst_elements` pass-through** — two files, one new parameter:
   - `writer.py`: keep `typst_elements` separate (don't merge into `sphinx_metadata`)
   - `template_engine.py`'s `map_parameters()`: add `extra_params: Dict[str, Any] | None = None` parameter, merge via `params.update(extra_params or {})` AFTER D-05/D-07 guards (additive, leaves Phase 22.2 code untouched)
   - Implement length-vs-string handling for `fontsize` (detect length patterns, emit unquoted vs. string values quoted)

3. **`typst_toctree_defaults` deletion** — pure removal:
   - `__init__.py:47` registration deleted
   - `tests/test_config_toctree_defaults.py` deleted entire file (registration-only, never caught the defect)
   - `tests/test_documentation_configuration.py:40` updated

### Critical Pitfalls (from PITFALLS.md — Top 5)

1. **Stale `table_cell_content` buffer swallows caption on 2nd+ tables** (Pitfall 1 — HIGHEST PRIORITY) — `add_text()` routes through stale buffer on second table because attribute persists from first. Prevention: (a) Set `self.in_table = False` during caption buffer-swap, (b) Explicitly `del self.table_cell_content` at `depart_table`. **Single-table tests cannot expose; 2+ table fixture mandatory.**

2. **`visit_title` falls through to section-heading, emitting stray `heading()`** (Pitfall 2) — New table-caption branch must explicitly `return` early and restore state-flags exactly as admonition-title branch does. Forgetting return causes both caption AND stray heading to emit.

3. **Caption + `:width:` nesting — wrong order silently changes semantics** (Pitfall 3) — Width must wrap whole `figure()` call (option b), not just inner table (option a), to match `visit_figure` precedent. Both are syntactically valid but have different sizing semantics. **Fixture must test caption+width together, not separately.**

4. **Type mismatch: `fontsize: "20pt"` quoted string becomes Typst type error** (Pitfall 8 — CRITICAL) — Unlike `papersize` (Typst string, quoted correctly), `fontsize: 11pt` is Typst length consumed by `set text(size: fontsize)` which rejects strings. Implementation must distinguish and handle separately. **Fixture must test papersize AND fontsize separately; proving one doesn't prove other.**

5. **Arbitrary key pass-through converts "dead but harmless" into "fatal for any typo"** (Pitfall 6 — CRITICAL) — Undeclared kwargs to `project.with(...)` abort compile. Curated whitelist required to avoid universal breakage. **Negative fixture case mandatory: unrecognized key raises real `typst.compile()` error.**

## Implications for Roadmap

### Phase 1: Delete `typst_toctree_defaults` (Trivial — 0 Risk)
**Delivers:** 1-line deletion from `__init__.py`, deletion of 236-line test file, docs/examples updates. **No behavioral impact (grep-proven inert).**

### Phase 2: Reimplement PR#98 — Captioned tables (Translator — High Risk/Value)
**Delivers:** `.. table:: Caption` → `figure(table(...), caption: {...}, kind: table)` with native "Table N" numbering. Caption-less tables stay plain. Caption+width compose correctly. **Must test with 2+ tables in one document to expose stale-buffer bug. Standing GATE-01 bar: real-compile fixture with 4 cases, red→green proof.**

### Phase 3: `typst_elements` pass-through (Config — Medium Risk/High Value)
**Delivers:** `typst_elements = {"papersize": "...", "fontsize": "..."}` in conf.py actually reaches PDF template. Correct type handling (string vs. length). Curated whitelist (only `base.typ` params). **Must sequence AFTER Phase 2 to isolate state-machine risk. Standing GATE-01 bar: positive cases for papersize and fontsize (separately!), negative case (unknown key fails loudly), baseline case (copyright doesn't leak), integration case (template_mapping interaction). Red→green proof mandatory.**

### Phase 4: Docs cleanup (Trivial — Strictly Ordered)
**Delivers:** Orphan file deleted, 5 phantom names removed/rewritten (delete-only for fontsize/papersize examples UNLESS Phase 3 has shipped). **Strict dependency: papersize/fontsize example rewrite ONLY after Phase 3 proven (Pitfall 11 prevention).**

**Ordering:** Phase 1 → Phase 2 → Phase 3 → Phase 4 (strict). Rationale: Phase 2 proves translator stability before Phase 3 adds config changes; Phase 3 must prove before Phase 4 docs examples (Pitfall 11).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Direct source reads + real `typst.compile()` verification on repo's installed `typst-py` 0.15.x |
| Features | MEDIUM–HIGH | Direct reads of source code + Sphinx LaTeX precedent (tavily-verified) |
| Architecture | HIGH | Direct line-number reads of current `main` @ 9f8e075; Phase 22.2 cross-checked |
| Pitfalls | HIGH | All grounded in direct code trace; prevention strategies mirror proven codebase patterns |

**Overall: HIGH** — Direct source reads verify all technical claims; real-compile verification de-risked biggest unknowns. Residual risk in state-machine correctness (Pitfalls 1–2) and type handling (Pitfall 8), both with clear prevention strategies grounded in existing patterns.

## Sources

- `.planning/research/STACK.md` — Typst figure/table caption API, `project.with()` undeclared-kwarg behavior, docutils table-caption node structure, `typst_toctree_defaults` inertness (real `typst.compile()` verified)
- `.planning/research/FEATURES.md` — captioned-table table-stakes vs out-of-scope, curated `typst_elements` key set, per-phantom-name disposition, Sphinx HTML/LaTeX baseline comparison
- `.planning/research/ARCHITECTURE.md` — current `visit_title`/`depart_title`/`visit_table`/`depart_table` control flow, caption+width composition point, `map_parameters()` `extra_params` injection design, build order
- `.planning/research/PITFALLS.md` — 11 milestone-specific pitfalls (buffer clobber, unknown-arg fatal, fontsize length type, docs ordering), red→green fixture discipline, pitfall-to-phase mapping

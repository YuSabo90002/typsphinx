# Phase 26: `typst_elements` papersize/fontsize Pass-Through (dead-config sweep round 2, part A) - Context

**Gathered:** 2026-07-24
**Status:** Ready for planning
**Mode:** `--auto` (decisions auto-selected — recommended option per gray area; review before planning)

<domain>
## Phase Boundary

Make `typst_elements` keys that the template's `project()` function actually declares (`papersize`, `fontsize`) flow from `conf.py` into the emitted `#show: project.with(...)` call, so a documented `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}` takes effect in the compiled PDF instead of being silently dropped.

**In scope:** the Python-side wiring only — `writer.py` (stop laundering `typst_elements` through the Sphinx-metadata dict) and `template_engine.py` (`map_parameters` merges a curated allowlist additively, with per-key emission typing and loud rejection of unknown keys). GATE-01 fixtures: positive `papersize`, positive `fontsize` (separately), negative unknown-key, copyright-non-leak — each a real `typst.compile()` case with red→green proof.

**Out of scope (scope anchor — do NOT drift):**
- `base.typ` is **byte-unchanged** (SC#5). No template edits, no new `project()` params.
- No new top-level `typst_papersize` / `typst_fontsize` config names — `typst_elements` is the only surface (mirrors Sphinx LaTeX's `latex_elements`).
- No `typst_toctree_defaults` work — that was Phase 24 (part B, done).
- No docs edits — the phantom `papersize`/`fontsize` doc examples are Phase 27 (which depends on this phase shipping first).
- No `@preview` version bump / no new runtime deps (milestone invariant). The 3-way version-sync surface stays untouched.
- Do NOT widen the allowlist to `title`/`authors`/`date`/`toctree_*` — those already arrive via `parameter_mapping` and `extract_toctree_options`; adding them to the elements allowlist would create double-source collisions.

</domain>

<decisions>
## Implementation Decisions

### Emission mechanism (papersize = string, fontsize = length)
- **D-01:** `papersize` is emitted as a **quoted Typst string** (`papersize: "us-letter"`) — the existing `_format_typst_value` string branch already does this correctly, no special handling needed for it.
- **D-02:** `fontsize` is emitted as an **unquoted Typst length** (`fontsize: 20pt`, not `"20pt"`). Achieve this with a minimal **raw-Typst marker** — a tiny wrapper (e.g. a `RawTypst`/`_RawTypstValue` class holding a string) that `_format_typst_value` recognizes and emits **verbatim**. The allowlist wraps the `fontsize` value in this marker; the string branch stays untouched. Chosen over pre-rendering the value inline in `map_parameters` because pre-rendered strings re-enter `_format_typst_value`'s string branch and come back quoted — the exact "double-formatting trap" the existing D-07 comment warns about. The marker is the type-safe path.

### Curated allowlist (definition, location, contents)
- **D-03:** Define the allowlist as a **module-level constant** in `template_engine.py` (e.g. `ELEMENTS_ALLOWLIST`), mapping each supported key to its emission type: `{"papersize": <string>, "fontsize": <length/raw>}`. **Hand-maintained**, not auto-derived by parsing `base.typ` (a `.typ` signature can't be reliably introspected from Python, and most `project()` params already come from other paths).
- **D-04:** Contents = **exactly `papersize` and `fontsize`** for this phase. These are the two `project()`-declared keys that read as document "elements." Keep the constant small and documented so adding a future key is a one-line, obviously-correct change.
- **D-05:** `map_parameters` gains the merge responsibility: `writer.py` passes `typst_elements` to `map_parameters` as a **separate argument** (SC#5 — no more `sphinx_metadata.update(typst_elements)`). Inside `map_parameters`, after the existing mapping/back-fill/`typst_authors` logic, iterate `typst_elements`, validate each key against the allowlist, and add the typed value to `params` **additively** (never touching the Phase 22.2 / D-05 package-path back-fill guard or the D-07 authors override).

### Fail-loud on unknown key
- **D-06:** An unrecognized `typst_elements` key **raises** `sphinx.errors.ExtensionError` (or `ConfigError`) at build time — a hard abort, not a warning — inside `map_parameters` where the allowlist is consulted. Chosen over a warning because SC#3 wants the failure to replace a cryptic downstream `typst.compile()` abort with an actionable Python-side error.
- **D-07:** The error message names the offending key and lists the supported keys, e.g. `typst_elements: unknown key 'foo' — supported keys: papersize, fontsize`. The negative GATE-01 fixture asserts this raises (and does NOT emit an undeclared kwarg into the `.typ`).

### Copyright / baseline-metadata non-leak
- **D-08:** Non-leak is **structural**, not a filter: because `map_parameters` only ever emits keys from `parameter_mapping` ∪ the elements allowlist, `copyright` (and any other baseline Sphinx metadatum) can never reach `project()`. Reinforce by dropping the now-dead `"copyright"` entry from the metadata dict gathered in `writer.py` (nothing consumes it once `typst_elements` no longer rides along in that dict). The copyright-non-leak GATE-01 fixture asserts `copyright:` never appears in the emitted `#show: project.with(...)`.

### fontsize input format
- **D-09:** Accept the `fontsize` value as a user-supplied **Typst length string** (`"20pt"`, `"1.2em"`, …) and emit it unquoted verbatim — **no Python-side length-grammar validation**. A malformed length is the user's own literal Typst and will fail at compile; we don't second-guess it. (Documenting "must be a valid Typst length" is Phase 27's job.)

### Claude's Discretion
- Exact class name / file placement of the raw-Typst marker, exact constant name, and whether validation lives in a small helper vs. inline in `map_parameters` — planner/executor decide, provided the SC#5 lock (writer keeps `typst_elements` separate; allowlist merges additively; `base.typ` byte-unchanged) and the D-07 double-formatting guard hold.
- Fixture project layout under `tests/roots/` vs. inline `conf.py` construction — executor picks whatever matches the existing GATE-01 fixture convention from Phases 22.x/25.

### Folded Todos
- **`2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md`** (`resolves_phase: 26`) — the driving todo. Documents the exact defect: `writer.py:208-209` `sphinx_metadata.update(typst_elements)` + `map_parameters` dropping non-mapped keys ⇒ `papersize`/`fontsize` never appear in the `.typ` (grep-0 confirmed by the todo author). Its `typst_toctree_defaults` half (discovery #5) was already resolved by Phase 24 — only the `typst_elements` half (part A) is this phase. Solution option **(A)** (implement the pass-through path) is chosen; option (B) (delete the config) is rejected because `typst_elements` is the intended `latex_elements` analog and CONF-04 requires it to work.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirement & roadmap
- `.planning/REQUIREMENTS.md` §CONF-04 — the curated-allowlist / string-vs-length / fail-loud / non-leak contract in the requirement's own words.
- `.planning/ROADMAP.md` §"Phase 26" — the 5 Success Criteria, the GATE-01 fixture mandate (papersize + fontsize separately + negative unknown-key + copyright-non-leak, each real `typst.compile()` red→green), and the milestone invariant (no `@preview` bump, `base.typ` byte-unchanged).

### Code to change (the whole surface)
- `typsphinx/writer.py:200-213` — metadata gather + `typst_elements = getattr(...)` + `sphinx_metadata.update(typst_elements)`. This is the launder-through-metadata site to fix; `typst_elements` must be passed to `map_parameters` separately instead, and the dead `"copyright"` key dropped from the gathered dict.
- `typsphinx/template_engine.py:62-66` — `DEFAULT_PARAMETER_MAPPING` (only `project`/`author`/`release`); the reason non-mapped keys are dropped.
- `typsphinx/template_engine.py:186-245` — `map_parameters()`, the additive-merge site. Preserve the `if not self.typst_package` back-fill guard (D-05) and the `typst_authors` override (D-07).
- `typsphinx/template_engine.py:399-455` — the `#show: project.with(...)` render loop and `_format_typst_value()` (string branch quotes; `None`→`none` is the precedent for an unquoted non-string). The raw-Typst marker plugs in here.

### Byte-frozen source of truth
- `typsphinx/templates/base.typ:39-63` — the `project()` signature: `papersize: "a4"`, `fontsize: 11pt` are the two declared "element" params and the allowlist's authority. **MUST stay byte-unchanged** (SC#5).

### Driving todo
- `.planning/todos/pending/2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md` — defect evidence, affected test files (`tests/test_config.py:112-156`, `tests/test_config_template_mapping.py:240` phantom comment, registration-only tests), and the (A)/(B) decision.

### Prior-art fixtures
- Phase 22.x CONTEXT/PLAN artifacts under `.planning/phases/22*` — the CONF-01..03 dead-config precedent (`typst_output_dir`/`typst_package`) and the GATE-01 real-`typst.compile()` fixture pattern to mirror.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_format_typst_value()` (`template_engine.py:422-455`) — the single value formatter feeding the `project.with(...)` render loop. Its `None → "none"` branch is the precedent for emitting an unquoted non-string; the raw-Typst marker adds one more branch of the same shape.
- `map_parameters()` (`template_engine.py:186-245`) — already the one place metadata→params happens; the allowlist merge belongs here, right after the `typst_authors` override.
- Existing GATE-01 real-`typst.compile()` fixtures from Phases 22.x/25 — copy the layout for the four required Phase 26 fixtures.

### Established Patterns
- **Dropped-unless-mapped:** `map_parameters` only emits keys present in `parameter_mapping`. This is *why* the config is dead — and *why* the non-leak (SC#4) is free once the merge is additive and scoped to the allowlist.
- **Package-path back-fill guard (D-05):** on `self.typst_package`, defaults (`title`/`authors`/`date`) are NOT back-filled. The elements merge must run without disturbing this guard.
- **Double-formatting trap (D-07):** never pre-render a Python value to a Typst string before it passes through `_format_typst_value` — it comes back quoted. Drives the marker-class choice for `fontsize`.

### Integration Points
- `writer.py` `_render_master` → `TemplateEngine.map_parameters(sphinx_metadata, typst_elements=...)` → `render()` → `_format_typst_value()`. New data flows through exactly this chain; no new call sites.

</code_context>

<specifics>
## Specific Ideas

- Concrete target emission (from README/CONF-04 example): `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}` must produce `papersize: "us-letter"` and `fontsize: 20pt` (note: quoted vs unquoted) in `#show: project.with(...)`, and the compiled PDF must use us-letter paper at 20pt body text.
- The two positive fixtures must be **separate** (SC#1/SC#2) — a combined papersize+fontsize case would hide a per-key emission-type bug.

</specifics>

<deferred>
## Deferred Ideas

- **Widening the allowlist beyond papersize/fontsize** (e.g. `lang`, margins) — a future config request, its own phase; keep the constant minimal now.

### Reviewed Todos (not folded)
The auto-fold heuristic surfaced several score≥0.4 todos that are **out of this phase's scope** (keyword over-match on shared words like "dead/config/sweep/phase/typst"). Deliberately NOT folded — folding them would be scope creep:
- `2026-07-22-citation-node-support-untracked.md` — translator citation/label handler gap; unrelated feature, not config wiring.
- `2026-07-22-delete-orphan-docs-configuration-rst.md` — Phase 27 (docs cleanup).
- `2026-07-22-user-guide-configuration-phantom-config-names.md` — Phase 27; explicitly *depends on* this phase shipping so the phantom `papersize`/`fontsize` examples become working `typst_elements` examples.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — CI/docs, future milestone.

</deferred>

---

*Phase: 26-typst-elements-papersize-fontsize-pass-through-dead-config-sweep-round-2-part-a*
*Context gathered: 2026-07-24*

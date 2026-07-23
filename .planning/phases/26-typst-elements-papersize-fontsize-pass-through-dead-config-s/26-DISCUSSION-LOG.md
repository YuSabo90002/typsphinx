# Phase 26: `typst_elements` papersize/fontsize Pass-Through - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-24
**Phase:** 26-typst-elements-papersize-fontsize-pass-through-dead-config-sweep-round-2-part-a
**Mode:** `--auto` (no interactive prompts — recommended option auto-selected per area)
**Areas discussed:** Emission mechanism, Curated allowlist, Fail-loud behavior, Copyright non-leak, fontsize input format

---

## Emission mechanism (papersize=string vs fontsize=length)

| Option | Description | Selected |
|--------|-------------|----------|
| Raw-Typst marker class | Wrap `fontsize` in a marker `_format_typst_value` emits verbatim; `papersize` uses existing string branch | ✓ |
| Pre-render inline in `map_parameters` | Build the Typst string before render | |
| Special-case `fontsize` in the render loop | Hardcode an unquoted branch keyed on the param name | |

**Auto-selected:** Raw-Typst marker class (recommended).
**Notes:** Pre-rendering re-enters the string branch and comes back quoted — the "double-formatting trap" the existing D-07 comment warns about. `None → "none"` is the precedent for an unquoted non-string value.

---

## Curated allowlist (location & contents)

| Option | Description | Selected |
|--------|-------------|----------|
| Module-level constant in `template_engine.py`, keys `papersize`+`fontsize` | Hand-maintained `{key: emission-type}` map | ✓ |
| Auto-derive from `base.typ` `project()` signature | Parse the `.typ` to discover allowed keys | |
| Include all `project()` params (title/authors/date/toctree_*) | Broad allowlist | |

**Auto-selected:** Module-level constant, exactly papersize+fontsize (recommended).
**Notes:** `.typ` signatures can't be reliably introspected from Python; title/authors/date/toctree_* already arrive via `parameter_mapping`/`extract_toctree_options`, so including them would double-source and collide.

---

## Fail-loud behavior (unknown key)

| Option | Description | Selected |
|--------|-------------|----------|
| Raise `ExtensionError`/`ConfigError` at build | Hard abort in `map_parameters`, message names key + lists allowed | ✓ |
| Emit a Sphinx warning, drop the key | Non-fatal | |
| Let it pass through and fail at `typst.compile()` | Status quo failure mode | |

**Auto-selected:** Hard raise with actionable message (recommended).
**Notes:** SC#3 wants the failure to replace a cryptic downstream compile abort with a Python-side error naming the key.

---

## Copyright / baseline-metadata non-leak

| Option | Description | Selected |
|--------|-------------|----------|
| Structural (additive allowlist) + drop dead `copyright` from gathered dict + fixture | Non-leak guaranteed by construction | ✓ |
| Explicit denylist filter of baseline keys | Filter copyright/etc. before render | |

**Auto-selected:** Structural (recommended).
**Notes:** `map_parameters` only emits `parameter_mapping` ∪ allowlist keys, so baseline metadata can never reach `project()`. A denylist would be redundant.

---

## fontsize input format

| Option | Description | Selected |
|--------|-------------|----------|
| Pass-through string verbatim, no validation | Trust user's Typst length; malformed fails at compile | ✓ |
| Validate/normalize the length grammar in Python | Reject non-length strings early | |

**Auto-selected:** Pass-through verbatim (recommended).
**Notes:** The value is the user's literal Typst; documenting "must be a valid Typst length" is Phase 27's job.

## Claude's Discretion

- Marker class name / placement, allowlist constant name, helper-vs-inline validation.
- Fixture project layout (`tests/roots/` vs inline `conf.py`), matching existing GATE-01 convention.

## Deferred Ideas

- Widening the allowlist beyond papersize/fontsize (lang, margins) — future phase.
- Reviewed-but-not-folded todos (citation-node-support, orphan-docs, phantom-config-names, linkcheck-CI) — out of scope; belong to Phase 27 or a future milestone. The auto-fold score≥0.4 heuristic over-matched on shared keywords; deliberately not folded to avoid scope creep.

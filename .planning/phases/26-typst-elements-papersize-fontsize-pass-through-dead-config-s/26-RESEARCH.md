# Phase 26: `typst_elements` papersize/fontsize Pass-Through - Research

**Researched:** 2026-07-24
**Domain:** Internal Python config-plumbing fix inside an existing Sphinx extension (no new external dependency, no new library — pure refactor of `writer.py` + `template_engine.py`)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Emission mechanism (papersize = string, fontsize = length)**
- **D-01:** `papersize` is emitted as a **quoted Typst string** (`papersize: "us-letter"`) — the existing `_format_typst_value` string branch already does this correctly, no special handling needed for it.
- **D-02:** `fontsize` is emitted as an **unquoted Typst length** (`fontsize: 20pt`, not `"20pt"`). Achieve this with a minimal **raw-Typst marker** — a tiny wrapper (e.g. a `RawTypst`/`_RawTypstValue` class holding a string) that `_format_typst_value` recognizes and emits **verbatim**. The allowlist wraps the `fontsize` value in this marker; the string branch stays untouched. Chosen over pre-rendering the value inline in `map_parameters` because pre-rendered strings re-enter `_format_typst_value`'s string branch and come back quoted — the exact "double-formatting trap" the existing D-07 comment warns about. The marker is the type-safe path.

**Curated allowlist (definition, location, contents)**
- **D-03:** Define the allowlist as a **module-level constant** in `template_engine.py` (e.g. `ELEMENTS_ALLOWLIST`), mapping each supported key to its emission type: `{"papersize": <string>, "fontsize": <length/raw>}`. **Hand-maintained**, not auto-derived by parsing `base.typ` (a `.typ` signature can't be reliably introspected from Python, and most `project()` params already come from other paths).
- **D-04:** Contents = **exactly `papersize` and `fontsize`** for this phase. These are the two `project()`-declared keys that read as document "elements." Keep the constant small and documented so adding a future key is a one-line, obviously-correct change.
- **D-05:** `map_parameters` gains the merge responsibility: `writer.py` passes `typst_elements` to `map_parameters` as a **separate argument** (SC#5 — no more `sphinx_metadata.update(typst_elements)`). Inside `map_parameters`, after the existing mapping/back-fill/`typst_authors` logic, iterate `typst_elements`, validate each key against the allowlist, and add the typed value to `params` **additively** (never touching the Phase 22.2 / D-05 package-path back-fill guard or the D-07 authors override).

**Fail-loud on unknown key**
- **D-06:** An unrecognized `typst_elements` key **raises** `sphinx.errors.ExtensionError` (or `ConfigError`) at build time — a hard abort, not a warning — inside `map_parameters` where the allowlist is consulted. Chosen over a warning because SC#3 wants the failure to replace a cryptic downstream `typst.compile()` abort with an actionable Python-side error.
- **D-07:** The error message names the offending key and lists the supported keys, e.g. `typst_elements: unknown key 'foo' — supported keys: papersize, fontsize`. The negative GATE-01 fixture asserts this raises (and does NOT emit an undeclared kwarg into the `.typ`).

**Copyright / baseline-metadata non-leak**
- **D-08:** Non-leak is **structural**, not a filter: because `map_parameters` only ever emits keys from `parameter_mapping` ∪ the elements allowlist, `copyright` (and any other baseline Sphinx metadatum) can never reach `project()`. Reinforce by dropping the now-dead `"copyright"` entry from the metadata dict gathered in `writer.py` (nothing consumes it once `typst_elements` no longer rides along in that dict). The copyright-non-leak GATE-01 fixture asserts `copyright:` never appears in the emitted `#show: project.with(...)`.

**fontsize input format**
- **D-09:** Accept the `fontsize` value as a user-supplied **Typst length string** (`"20pt"`, `"1.2em"`, …) and emit it unquoted verbatim — **no Python-side length-grammar validation**. A malformed length is the user's own literal Typst and will fail at compile; we don't second-guess it. (Documenting "must be a valid Typst length" is Phase 27's job.)

### Claude's Discretion
- Exact class name / file placement of the raw-Typst marker, exact constant name, and whether validation lives in a small helper vs. inline in `map_parameters` — planner/executor decide, provided the SC#5 lock (writer keeps `typst_elements` separate; allowlist merges additively; `base.typ` byte-unchanged) and the D-07 double-formatting guard hold.
- Fixture project layout under `tests/roots/` vs. inline `conf.py` construction — executor picks whatever matches the existing GATE-01 fixture convention from Phases 22.x/25.

### Deferred Ideas (OUT OF SCOPE)
- **Widening the allowlist beyond papersize/fontsize** (e.g. `lang`, margins) — a future config request, its own phase; keep the constant minimal now.
- `base.typ` is **byte-unchanged** (SC#5). No template edits, no new `project()` params.
- No new top-level `typst_papersize` / `typst_fontsize` config names — `typst_elements` is the only surface (mirrors Sphinx LaTeX's `latex_elements`).
- No `typst_toctree_defaults` work — that was Phase 24 (part B, done).
- No docs edits — the phantom `papersize`/`fontsize` doc examples are Phase 27 (which depends on this phase shipping first).
- No `@preview` version bump / no new runtime deps (milestone invariant). The 3-way version-sync surface stays untouched.
- Do NOT widen the allowlist to `title`/`authors`/`date`/`toctree_*` — those already arrive via `parameter_mapping` and `extract_toctree_options`; adding them to the elements allowlist would create double-source collisions.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| CONF-04 | User can set `papersize` and `fontsize` via `typst_elements` in `conf.py` and see them applied in the compiled `.typ`/PDF via `project()` — curated allowlist, `fontsize` as a Typst length (not quoted string), `papersize` as a string, unrecognized key fails loudly, baseline Sphinx metadata never leaks into `project()`. | Standard Stack (`ExtensionError`, `RawTypst` marker pattern), Architecture Patterns (Patterns 1-3, System Architecture Diagram), Common Pitfalls (1-4), Validation Architecture (Phase Requirements -> Test Map row-by-row per Success Criterion SC#1-SC#5) |
</phase_requirements>

## Summary

This phase closes a laundering bug, not a missing-feature build. `writer.py:207-209` currently does `sphinx_metadata.update(typst_elements)`, dumping the user's `typst_elements` dict into the SAME dict that also carries `project`/`author`/`release`/`copyright`. That merged dict then goes through `map_parameters()`, whose `DEFAULT_PARAMETER_MAPPING` only knows three keys (`project`, `author`, `release`) — so `papersize`/`fontsize` (and, coincidentally, `copyright`) are silently dropped on the floor. `base.typ`'s `project()` (lines 39-48) already declares `papersize: "a4"` and `fontsize: 11pt` as real parameters; they are simply never reached from the Python side. This is the exact same defect shape Phase 22.2 fixed for `typst_package`/`typst_authors` (CONF-02/03) — a config→output real-compile gate is required (`tests/test_package_only_config_gate.py` is the literal template named in ROADMAP.md and STATE.md), and this repo already has the harness for it.

The fix is entirely additive and structural, confirmed by reading the code directly (not assumed): `map_parameters()` (`template_engine.py:186-245`) builds `params` from `self.parameter_mapping` only, then optionally back-fills `title`/`authors`/`date` (guarded by `if not self.typst_package`), then applies the `typst_authors` override. Adding a fourth step — "merge a curated allowlist of `typst_elements` keys" — after those three, keyed off a NEW `typst_elements` argument (not off the polluted `sphinx_metadata` dict), removes the leak path structurally: `copyright` can never reach `params` because nothing in `parameter_mapping` ∪ the new allowlist names it. `_format_typst_value()` (`template_engine.py:422-453`) already has the `None → "none"` unquoted-non-string precedent (line 432-433) that the `fontsize`-as-raw-length case should copy exactly, via one new `isinstance` branch checked BEFORE the string branch — never by pre-rendering `fontsize` to a Typst literal inside `map_parameters` itself (that is the documented "double-formatting trap," already called out by the D-07 authors-list comment at lines 232-238, and it is real: a pre-rendered string re-enters the `isinstance(value, str)` branch at line 437 and gets a second, incorrect layer of quoting).

**Primary recommendation:** Add a module-level `ELEMENTS_ALLOWLIST` dict in `template_engine.py` mapping `{"papersize": <emit-as-string>, "fontsize": <emit-as-raw>}`; add a tiny `RawTypst` wrapper class (a `@dataclass(frozen=True)` with one `str` field is sufficient — no library needed); give `map_parameters()` a new `typst_elements: dict | None = None` keyword parameter (default preserves every existing unit-test call site); iterate it after the existing authors-override step, raising `sphinx.errors.ExtensionError` on any key not in the allowlist; and change `writer.py` to pass `typst_elements` as that new keyword argument instead of `.update()`-ing it into `sphinx_metadata`, dropping the now-provably-dead `"copyright"` entry from the gathered dict at the same time. `base.typ` is never touched.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Sphinx `conf.py` config value registration (`typst_elements`) | API/Backend (build-time Python) | — | Already registered in `__init__.py`; out of scope for this phase (registration exists, only the plumbing after it is broken) |
| Gathering config values per-document (`writer.py`) | API/Backend (build-time Python) | — | `TypstWriter.translate()` runs once per docname during the Sphinx build; it owns "what values come from where" |
| Allowlisting + type-directed formatting (`template_engine.py`) | API/Backend (build-time Python) | — | `TemplateEngine` is the single place Python values become Typst source text; the allowlist and the raw-marker check both belong here, next to `_format_typst_value()` |
| Rendered `.typ` output / compiled PDF | Build artifact (Typst compiler, external to this repo's Python) | — | `typst-py` (`pdf.py`) consumes the `.typ` text this phase changes; Typst's own `project()` signature in `base.typ` is the receiving contract and is frozen for this phase |
| GATE-01 regression fixtures | Test / CI tier | — | New fixtures live under `tests/fixtures/<name>_gate/` + `tests/test_<name>_gate.py`, exercised via `subprocess` + `sys.executable -m sphinx`, same as every existing GATE-01 module |

There is no browser/client or CDN tier in this project (it is a docs-build-time Sphinx extension, not a web app) — this map exists mainly to record that ALL the work is one tier: the Python build-time layer between Sphinx config and the emitted Typst template call.

## Standard Stack

### Core
No new library is introduced by this phase. The "stack" is the project's own existing code:

| Component | Version | Purpose | Why Standard (for this repo) |
|-----------|---------|---------|-------------------------------|
| `typsphinx.template_engine.TemplateEngine` | current (this repo, unversioned internal module) | Owns `map_parameters()`/`_format_typst_value()`/`render()` — the single Python→Typst-source boundary | Already the sole such boundary; adding a second one elsewhere would violate the "one emission site" principle already documented at `template_engine.py:362-370` |
| `sphinx.errors.ExtensionError` | ships with `sphinx` [VERIFIED: installed venv, `sphinx==9.1.0`] | Fail-loud exception for the unknown-key case | Already imported and used for exactly this class of build-time hard-abort in `typsphinx/builder.py:17,965-967` (aggregate PDF-compile failure) — using the SAME exception class for the config-validation failure keeps the extension's error surface uniform for `sphinx-build` callers, which already special-case `ExtensionError`/`SphinxError` subclasses for clean CLI reporting (Sphinx wraps `SphinxError` subclasses in a one-line `# <message>` without a Python traceback; unless `-v`/`-vv` is passed) |
| `typst` (`typst-py`) | 0.15.0 [VERIFIED: installed venv] | Real-compile GATE-01 fixtures | Already the pinned compile backend for every existing GATE-01/render-gate test in this repo; no version bump needed or permitted (milestone invariant) |
| `pytest` | project-pinned (`pyproject.toml`) | Test runner for the new fixtures/units | Existing project convention |

### Supporting
Not applicable — no supporting/helper libraries are needed. `dataclasses` (Python stdlib) is sufficient for the raw-Typst marker; no third-party wrapper type is warranted for a single-field, single-purpose "don't quote this" flag.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A dedicated `RawTypst`/`_RawTypstValue` marker class recognized by `_format_typst_value()` | Pre-render `fontsize` to `"20pt"` (bare, no quotes) directly inside `map_parameters()` and let it flow through unchanged | **Rejected.** A pre-rendered plain string is indistinguishable from any other string value once it reaches `_format_typst_value()` — it re-enters the `isinstance(value, str)` branch at line 437 and gets wrapped in quotes a second time, producing the literal Typst syntax error `fontsize: "20pt"` being treated as a string where a length is required (a **type** mismatch, not a syntax error — Typst would actually still parse `set text(size: "20pt")`, then fail at runtime with something like `expected length, found string`). This is precisely the "double-formatting trap" the existing D-07 comment (`template_engine.py:232-238`) already warns about for a different value (author lists) — the same failure mode, new value. |
| Same marker class, but bypass `_format_typst_value()` entirely and string-concat the formatted params in `render()` | — | **Rejected.** Would create a second Python→Typst-source emission point, contradicting the single-emission-site principle the code comments at `template_engine.py:362-370` already establish for import blocks; also loses the existing escaping/type-dispatch logic for the OTHER params that still flow through `_format_typst_value()` in the same loop (`render()` lines 410-412 format every key uniformly). |
| Allowlist as a hand-maintained module constant | Parse `base.typ`'s `project()` signature at runtime to auto-derive the allowlist | **Rejected per CONTEXT.md D-03** (already decided by the user) — a `.typ` function signature cannot be reliably introspected from Python without a Typst-aware parser, and most `project()` params (`title`/`authors`/`date`/`toctree_*`) already arrive via a DIFFERENT path (`parameter_mapping`/`extract_toctree_options`), so auto-deriving the FULL signature would require reconciling those two paths — out of scope and unnecessary for two keys. |
| `sphinx.errors.ExtensionError` | `sphinx.errors.ConfigError` | Both are `SphinxError` subclasses and both produce the same clean one-line CLI abort. `ConfigError` reads slightly more precisely ("this IS a config problem") but is used nowhere else in this codebase; `ExtensionError` is already the established idiom here (`builder.py`). **Recommendation: use `ExtensionError`** for codebase consistency — CONTEXT.md D-06 explicitly allows either. |

**Installation:**
```bash
# No new dependency to install. Existing dev environment already has everything needed:
uv sync --extra dev   # (already run; typst-py 0.15.0, sphinx 9.1.0 confirmed present)
```

**Version verification:** N/A — no new package is being added. Confirmed the two libraries this phase touches are already present at the versions the milestone pins:
```bash
uv run python -c "import typst; print(typst.__version__)"   # -> 0.15.0
uv run python -c "import sphinx; print(sphinx.__version__)" # -> 9.1.0
```
Both [VERIFIED: installed venv, this session].

## Package Legitimacy Audit

**Not applicable — this phase introduces zero new packages.** Per the milestone invariant (STATE.md, ROADMAP.md): "zero new runtime deps, no `@preview` version bump." `sphinx.errors.ExtensionError` and `typst`/`typst-py` are both ALREADY-installed, already-imported-elsewhere dependencies (confirmed via `grep`/`import` above) — no registry check, no `npm view`/`pip index versions` lookup, and no legitimacy audit is warranted for code already present and used in this exact codebase.

**Packages removed due to [SLOP] verdict:** none (n/a).
**Packages flagged as suspicious [SUS]:** none (n/a).

## Architecture Patterns

### System Architecture Diagram

```
conf.py                                  writer.py (TypstWriter.translate, per-docname)
  typst_elements = {                          │
    "papersize": "us-letter",                 │  1. gather sphinx_metadata dict:
    "fontsize": "20pt",                       │       {project, author, release}
  }                                            │       (NO "copyright" key -- dropped, D-08)
       │                                       │  2. typst_elements = getattr(config, "typst_elements", {})
       │  (Sphinx config attribute lookup)     │  3. params = template_engine.map_parameters(
       └──────────────────────────────────────►│         sphinx_metadata,
                                                │         typst_elements=typst_elements,   <-- NEW arg, no more .update()
                                                │     )
                                                └───────────────┬─────────────────────────────┘
                                                                 │
                                                                 ▼
                                     template_engine.py :: TemplateEngine.map_parameters()
                                     ┌───────────────────────────────────────────────────────┐
                                     │ 1. existing: apply self.parameter_mapping             │
                                     │    (project->title, author->authors, release->date)   │
                                     │ 2. existing: back-fill title/authors/date defaults     │
                                     │    (skipped entirely when self.typst_package is set)   │
                                     │ 3. existing: typst_authors override (wins on collision)│
                                     │ 4. NEW: for key, value in typst_elements.items():      │
                                     │      if key not in ELEMENTS_ALLOWLIST:                 │
                                     │          raise ExtensionError(...)  <-- fail LOUD here │
                                     │      emit_kind = ELEMENTS_ALLOWLIST[key]                │
                                     │      params[key] = (                                   │
                                     │          RawTypst(value) if emit_kind is RAW            │
                                     │          else value                                    │
                                     │      )                                                 │
                                     └───────────────────────────────┬─────────────────────────┘
                                                                      │ params dict (python)
                                                                      ▼
                                     template_engine.py :: TemplateEngine.render()
                                     ┌───────────────────────────────────────────────────────┐
                                     │ for key, value in all_params.items():                  │
                                     │     formatted = self._format_typst_value(value)        │
                                     │       -- NEW branch, checked BEFORE the str branch:    │
                                     │          if isinstance(value, RawTypst):               │
                                     │              return value.source   # verbatim, no quote│
                                     │       -- existing str branch (unchanged): quotes+escapes│
                                     │     output_parts.append(f"  {key}: {formatted},")       │
                                     └───────────────────────────────┬─────────────────────────┘
                                                                      │ emitted .typ text
                                                                      ▼
                                            #show: project.with(
                                              ...
                                              papersize: "us-letter",   <-- quoted string
                                              fontsize: 20pt,           <-- unquoted length
                                              ...
                                            )
                                                                      │
                                                                      ▼
                                     templates/base.typ :: project()  (BYTE-UNCHANGED, receiving contract)
                                     #let project(..., papersize: "a4", fontsize: 11pt, body) = {
                                       set page(paper: papersize, ...)
                                       set text(size: fontsize, ...)
                                     }
                                                                      │
                                                                      ▼
                                              typst.compile()  -->  PDF at requested paper size / font size
```

### Recommended Project Structure
No new files/folders — this is a same-file edit to two existing modules, plus new test files following the existing flat `tests/` convention:
```
typsphinx/
├── template_engine.py     # + ELEMENTS_ALLOWLIST, + RawTypst class, edited map_parameters()/_format_typst_value()
└── writer.py              # edited: sphinx_metadata gather (drop "copyright"), map_parameters() call site
tests/
├── test_template_engine.py                 # + unit tests: allowlist merge, RawTypst emission, unknown-key raise
├── fixtures/
│   └── typst_elements_pass_through_gate/    # NEW fixture project(s) for the 4 GATE-01 cases
│       ├── conf.py            # positive papersize variant (or parametrized per-case conf.py files)
│       └── index.rst
└── test_typst_elements_pass_through_gate.py # NEW: real typst.compile() GATE-01 fixture, 4 cases
```

### Pattern 1: Raw-Typst marker for unquoted emission
**What:** A tiny immutable wrapper class whose sole job is to be recognized by `_format_typst_value()` and emitted verbatim (no quoting, no escaping).
**When to use:** Any future config value that must reach the template as a Typst literal (length, boolean expression, etc.) rather than a quoted string — this phase only needs it for `fontsize`, but the pattern generalizes for CONF-06 (deferred).
**Example:**
```python
# Source: this repo, template_engine.py — pattern modeled on the existing
# `None -> "none"` unquoted-non-string precedent at the top of
# _format_typst_value() (see current code, lines 432-433).

from dataclasses import dataclass


@dataclass(frozen=True)
class RawTypst:
    """Wraps a string that must be emitted into the .typ output VERBATIM
    (no quoting, no escaping) -- e.g. a Typst length literal like `20pt`."""
    source: str


def _format_typst_value(self, value):
    if value is None:
        return "none"
    if isinstance(value, RawTypst):          # NEW branch -- checked before
        return value.source                  # the str branch, so a RawTypst
                                               # never re-enters string quoting
    elif isinstance(value, bool):
        ...
    elif isinstance(value, str):
        ...
```

### Pattern 2: Curated allowlist merged additively, after existing logic
**What:** A module-level dict naming exactly the `project()` params this phase is allowed to pass through, each tagged with how it must be emitted.
**When to use:** Any curated (not auto-derived, not arbitrary-passthrough) config surface where an undeclared kwarg to the receiving Typst function would be a hard compile fatal.
**Example:**
```python
# Source: this repo, template_engine.py

class _ElementEmission:
    """Sentinel enum-like values naming HOW an elements-allowlist key must
    be formatted -- not the value itself."""
    STRING = "string"
    RAW = "raw"


ELEMENTS_ALLOWLIST = {
    # Keys `base.typ`'s project() actually declares as "element" params
    # (templates/base.typ:46-47). Keep this list exactly in sync with that
    # signature -- adding a key here WITHOUT a matching base.typ parameter
    # will pass an undeclared kwarg and abort the Typst compile (D-04).
    "papersize": _ElementEmission.STRING,
    "fontsize": _ElementEmission.RAW,
}


def map_parameters(self, sphinx_metadata, typst_elements=None):
    params = {}
    # ... existing parameter_mapping / back-fill / typst_authors logic,
    #     UNCHANGED, exactly as today ...

    # NEW: additive elements merge -- runs LAST, after typst_authors.
    for key, value in (typst_elements or {}).items():
        if key not in ELEMENTS_ALLOWLIST:
            supported = ", ".join(sorted(ELEMENTS_ALLOWLIST))
            raise ExtensionError(
                f"typst_elements: unknown key {key!r} -- "
                f"supported keys: {supported}"
            )
        emit_kind = ELEMENTS_ALLOWLIST[key]
        params[key] = RawTypst(value) if emit_kind == _ElementEmission.RAW else value

    return params
```
**Signature note:** `typst_elements=None` as a keyword-only-by-convention argument with a safe default means every EXISTING call site in `tests/test_template_engine.py` (there are ~10, e.g. `engine.map_parameters(sphinx_metadata)` at lines 128, 140, 157, 179, 199, 218, 241, 260, 277, 496, 852, 879, 885 — grep-confirmed) continues to work unmodified; only `writer.py`'s ONE call site needs the new argument added.

### Pattern 3: writer.py passes typst_elements separately, never merges it into sphinx_metadata
**What:** Stop the `sphinx_metadata.update(typst_elements)` laundering; pass `typst_elements` to `map_parameters()` as its own argument.
**Example:**
```python
# Source: this repo, writer.py (current lines 199-212, to be edited)

# BEFORE (the bug):
sphinx_metadata = {
    "project": config.project,
    "author": config.author,
    "release": config.release,
    "copyright": config.copyright,   # dead: nothing in parameter_mapping names it
}
typst_elements = getattr(config, "typst_elements", {})
sphinx_metadata.update(typst_elements)          # <- laundering bug (BUG shape of CONF-04)
params = template_engine.map_parameters(sphinx_metadata)

# AFTER:
sphinx_metadata = {
    "project": config.project,
    "author": config.author,
    "release": config.release,
    # "copyright" dropped entirely -- D-08, nothing ever consumed it
}
typst_elements = getattr(config, "typst_elements", {})
params = template_engine.map_parameters(sphinx_metadata, typst_elements=typst_elements)
```

### Anti-Patterns to Avoid
- **Pre-rendering `fontsize` to a bare string before it reaches `_format_typst_value()`:** re-enters the `isinstance(value, str)` branch and gets quoted a second time (the double-formatting trap, D-07's existing warning generalizes to this new value).
- **Merging `typst_elements` into `sphinx_metadata` (the CURRENT bug) or into any other dict that also carries baseline Sphinx metadata:** re-opens exactly the leak path SC#4 requires closed — keep the two dicts/arguments structurally separate all the way to `map_parameters()`.
- **Widening `ELEMENTS_ALLOWLIST` to cover `title`/`authors`/`date`/`toctree_*`:** these already arrive via `parameter_mapping`/`extract_toctree_options`; adding them to the elements allowlist creates a second, colliding source of truth for the same output key — explicitly out of scope (CONTEXT.md domain section, last bullet).
- **A warning (`logger.warning`) instead of a raise for an unknown key:** CONTEXT.md D-06 explicitly rejects this — the point of SC#3 is to replace a cryptic downstream `typst.compile()` fatal (undeclared kwarg) with an actionable Python-side error, and a warning would still let the undeclared kwarg reach the compile step if it were silently passed through (it must not be passed through AT ALL, warning or not).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sphinx-idiomatic build-time hard-abort error | A custom exception class, or `sys.exit()`, or a bare `raise ValueError(...)` | `sphinx.errors.ExtensionError` (already imported in `builder.py`) | Sphinx's CLI runner specifically catches `SphinxError` subclasses and prints a clean one-line message (no traceback) instead of an unhandled-exception dump; a bare `ValueError`/`RuntimeError` would print a full traceback to the user, a worse experience for a config-validation error. Reusing `ExtensionError` also keeps this extension's error surface consistent with its own existing `builder.py` precedent. |
| A Typst-length string validator/grammar parser for `fontsize` | A regex or parser validating `"20pt"`/`"1.2em"`/etc. before emission | Nothing — pass the string through verbatim (CONTEXT.md D-09, explicit) | Typst's own compiler is the authoritative length-grammar validator; a malformed length is the user's literal input and will fail loudly at `typst.compile()` time with Typst's own error, which is sufficient. Building a second, necessarily-incomplete length grammar in Python is pure risk (silently rejecting valid Typst syntax, or silently accepting invalid syntax) for zero benefit. |
| Auto-deriving the allowlist from `base.typ`'s `project()` signature | A `.typ` parser/AST walker | A hand-maintained Python dict constant (`ELEMENTS_ALLOWLIST`) | Already decided (CONTEXT.md D-03) — a `.typ` function signature is not reliably introspectable from Python without embedding a Typst-aware parser; two keys don't justify that machinery, and the existing `parameter_mapping`/`typst_template_function["params"]` mechanisms already prove "explicit, hand-authored mapping" is this codebase's established idiom for this exact class of problem. |

**Key insight:** every piece of this phase's solution space already has a directly analogous, already-shipped precedent somewhere else in this exact codebase (`None → "none"` for raw emission, `ExtensionError` for fail-loud, hand-maintained mapping dicts for config→param translation, `GATE-01` real-compile fixtures for proof). The research task was locating those precedents, not inventing new patterns.

## Common Pitfalls

### Pitfall 1: The double-formatting trap (fontsize re-quoted)
**What goes wrong:** `fontsize` ends up emitted as `fontsize: "20pt"` (quoted) instead of `fontsize: 20pt` (unquoted), causing a Typst type error at compile time (`expected length, found string`) rather than the intended pass-through.
**Why it happens:** Any code path that renders the Python value to a Typst-source STRING before it reaches `_format_typst_value()`'s dispatch (e.g. formatting it inline in `map_parameters()`, or doing `f'{value}'` anywhere upstream) makes it indistinguishable from an ordinary string once it arrives at `_format_typst_value()`, so the `isinstance(value, str)` branch (line 437) quotes it — a SECOND, unwanted layer of formatting on top of the first.
**How to avoid:** Keep `fontsize`'s value as a plain Python `str` all the way until it is wrapped in the `RawTypst` marker; let `_format_typst_value()` (and ONLY it) decide how to render it, via a new `isinstance(value, RawTypst)` branch checked before the string branch.
**Warning signs:** grep the emitted `.typ` for `fontsize: "` (quote immediately after the colon) — that pattern should NEVER appear; the correct emission is `fontsize: 20pt,` with no quotes.

### Pitfall 2: Silent kwarg pass-through instead of a loud raise
**What goes wrong:** An unrecognized `typst_elements` key is either dropped silently (today's bug, SC#3 still unmet) or passed straight through into `#show: project.with(...)` as an undeclared kwarg, which Typst's compiler rejects with an "unexpected named argument" fatal buried inside a `typst.compile()` traceback — a much less actionable failure than a Python-side `ExtensionError` naming the exact offending key.
**Why it happens:** Any code path that merges `typst_elements` into `params` WITHOUT first checking `ELEMENTS_ALLOWLIST` membership.
**How to avoid:** The allowlist check must run BEFORE the key is ever added to `params` — raise immediately on the first unknown key found (no need to collect all unknown keys into one aggregate error; CONTEXT.md's example error message names one offending key).
**Warning signs:** A `typst.compile()` fatal mentioning an argument name that is not `papersize`/`fontsize`/`title`/`authors`/`date`/`toctree_*` — that is this exact bug re-appearing downstream, unguarded.

### Pitfall 3: Reintroducing the leak via a shared dict
**What goes wrong:** `copyright` (or any other baseline Sphinx metadatum) reaches `project()` as an emitted parameter, or a FUTURE developer re-adds `sphinx_metadata.update(typst_elements)` "to simplify" the call site, silently reopening the leak the SC#4 fixture proves closed.
**Why it happens:** Merging two dicts with different provenance (baseline Sphinx config vs. user-declared template elements) erases the information needed to keep them separately-scoped by the time `map_parameters()` sees them.
**How to avoid:** Pass `typst_elements` to `map_parameters()` as its OWN keyword argument, never merged into `sphinx_metadata` at any point in the call chain; the copyright-non-leak GATE-01 fixture exists specifically to catch a regression of this exact shape.
**Warning signs:** `copyright:` (or any other key not in `DEFAULT_PARAMETER_MAPPING`'s value-set ∪ `ELEMENTS_ALLOWLIST`) appearing anywhere inside the `#show: project.with(...)` call region of an emitted `.typ` file.

### Pitfall 4: Breaking existing `map_parameters()` call sites
**What goes wrong:** Adding a REQUIRED (non-default) `typst_elements` parameter to `map_parameters()`'s signature breaks ~13 existing call sites in `tests/test_template_engine.py` that call `engine.map_parameters(sphinx_metadata)` with one positional argument only.
**Why it happens:** Not giving the new parameter a safe default (`None`, treated as `{}`).
**How to avoid:** `def map_parameters(self, sphinx_metadata, typst_elements=None):` — default `None` (or `{}` via `typst_elements or {}` inside the loop) so every existing call site continues to work unmodified.
**Warning signs:** `TypeError: map_parameters() missing 1 required positional argument` in the existing `test_template_engine.py` suite after the signature change.

### Pitfall 5: NixOS sandbox — real-compile fixtures may report false negatives inside worktrees
**What goes wrong:** The four new GATE-01 fixtures (which MUST use real `typst.compile()`) can appear to fail for environmental reasons unrelated to the code change.
**Why it happens:** Documented, pre-existing sandbox behavior (project memory `nixos-sandbox-test-env.md`): `uv run <compiled-binary>` sometimes fails with a NixOS dynamic-linker error, and a worktree's own venv can diverge from the main tree's. This is NOT specific to Phase 26, but is worth restating because Phase 26's fixtures are exactly the "real compile" kind most exposed to it.
**How to avoid:** Follow the existing convention exactly — invoke `sphinx-build` as `sys.executable -m sphinx` (never `["uv", "run", "sphinx-build", ...]`) inside the new test module, exactly as `test_package_only_config_gate.py`'s `_run_sphinx_build()` and `test_confval_field_body_render_gate.py`'s helper already do; and re-run the full suite on the main tree (not just inside an executor's worktree) before treating a red result as a real regression. Per-worktree provisioning (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + `uv run pytest`) per CLAUDE.md's "Worktree-isolated execution" section is mandatory since `use_worktrees: true` in `.planning/config.json` and no fork-base auto-degrade applies here.
**Warning signs:** `typst` import failure inside a worktree despite `typst==0.15.0` being present on the main tree; a fixture reporting 45 failures in `tests/test_integration_*.py`/`tests/test_examples_basic.py` that are unrelated to this phase's own new fixtures (documented pre-existing exclusion list).

## Runtime State Inventory

Not applicable — this is a config-plumbing bugfix phase (writer.py/template_engine.py Python code edit), not a rename/refactor/migration phase. No stored data, live service config, OS-registered state, secrets, or build artifacts reference the strings being changed here (`typst_elements`, `papersize`, `fontsize` are not being RENAMED — they are the same config-value names, only their downstream handling changes). Skipping this section per its own trigger condition.

## Code Examples

### Verified: existing `_format_typst_value()` unquoted-non-string precedent (the model for the new RawTypst branch)
```python
# Source: typsphinx/template_engine.py, current lines 422-433 (read this session)
def _format_typst_value(self, value: Any) -> str:
    if value is None:
        return "none"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    ...
```

### Verified: existing fail-loud precedent (`ExtensionError`) elsewhere in this codebase
```python
# Source: typsphinx/builder.py, current lines 963-967 (read this session)
if failures:
    summary = "; ".join(f"{docname}: {err}" for docname, err in failures)
    raise ExtensionError(
        f"typstpdf: {len(failures)} master document(s) failed: {summary}"
    )
```

### Verified: GATE-01 real-compile fixture harness pattern to mirror (subprocess + sys.executable -m sphinx)
```python
# Source: tests/test_package_only_config_gate.py, current lines 71-96 (read this session)
def _run_sphinx_build(source_dir, build_dir, builder):
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )

# class-scoped @staticmethod fixture builds ONCE, shared across per-defect
# assertion tests; @pytest.mark.skipif(not TYPST_AVAILABLE, ...) guards the
# whole module; assertions never match on Typst's exact error TEXT (D-06),
# only that a real compile raises / that returncode == 0 and a valid
# %PDF-prefixed file exists.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `typst_elements` merged into `sphinx_metadata` then silently dropped by `map_parameters()`'s narrow `parameter_mapping` | Curated allowlist merged additively, after existing logic, into `params` directly | This phase (Phase 26) | `papersize`/`fontsize` become the FIRST `typst_elements` keys that actually reach the compiled output — CONF-04 |
| Registration-only tests (`test_typst_elements_config`, `test_custom_typst_elements_config` in `tests/test_config.py:112-156`) as the only coverage | Registration tests REMAIN valid (they test `conf.py` value loading, which is correct and unrelated to this bug) but are now supplemented by GATE-01 real-compile fixtures proving the value reaches `project()` | This phase | Closes the exact test-suite gap this phase's own driving todo diagnosed: registration tests staying green regardless of whether the feature works |

**Deprecated/outdated:** the "tested separately" comment at `tests/test_config_template_mapping.py:240` (`# Note: typst_elements integration is tested separately`) is now provably FALSE until this phase ships — no test anywhere currently asserts `papersize`/`fontsize` appear in emitted output. This phase's fixtures are what makes that comment true; the planner should consider whether to update or remove that stale comment as part of this phase's test work (not required by any Success Criterion, but consistent with SC#3/GATE-01's spirit of removing misleading "tested elsewhere" claims).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `sphinx.errors.ExtensionError` (vs. `ConfigError`) is the better idiomatic choice for this specific raise, based on codebase-internal precedent rather than official Sphinx-extension-authoring guidance being consulted this session | Standard Stack / Alternatives Considered, Pitfall 2 | Low — CONTEXT.md D-06 explicitly permits either; this is a style preference, not a correctness question, and both are `SphinxError` subclasses that Sphinx's CLI handles identically |
| A2 | `@dataclass(frozen=True)` is sufficient for the `RawTypst` marker (vs. a plain class, a `NamedTuple`, or a subclass of `str`) | Architecture Patterns / Pattern 1 | Low — this is an implementation-detail choice explicitly left to planner/executor discretion per CONTEXT.md ("Claude's Discretion" section); any of these shapes satisfies the `isinstance` check `_format_typst_value()` needs |

**If this table is empty:** N/A — see above; both entries are low-risk stylistic choices explicitly delegated to planner/executor discretion by CONTEXT.md, not load-bearing factual claims requiring user confirmation.

## Open Questions

1. **Exact class/constant naming and file placement of `RawTypst`/`ELEMENTS_ALLOWLIST`**
   - What we know: CONTEXT.md explicitly delegates this to planner/executor discretion, provided the SC#5 lock and D-07 double-formatting guard hold (see CONTEXT.md "Claude's Discretion").
   - What's unclear: nothing blocking — this is intentionally open per the user's own decision.
   - Recommendation: planner should pick names once and record them in the PLAN.md so the four GATE-01 fixtures and the unit tests reference the same names consistently; `ELEMENTS_ALLOWLIST` and `RawTypst` (as used throughout this document) are reasonable, uncontroversial defaults.

2. **Whether the four GATE-01 fixtures live in one fixture-project directory (with 4 separate `conf.py` variants, mirroring `_write_variant_project()` from `test_package_only_config_gate.py`) or four independent fixture directories (mirroring the simpler single-purpose fixtures like `confval_field_body_render_gate`)**
   - What we know: both patterns exist in this codebase today and both are acceptable (CONTEXT.md explicitly delegates "fixture project layout" to executor discretion).
   - What's unclear: which is more maintainable for exactly 4 small, independent, non-overlapping cases (positive-papersize / positive-fontsize / negative-unknown-key / copyright-non-leak) — the `_write_variant_project()` pattern is designed for a LARGER matrix (5 defect classes + a difference matrix) than this phase needs.
   - Recommendation: given the small, INDEPENDENT nature of the 4 required cases (SC#1/SC#2 explicitly require them "separate," not combined), four small standalone fixture dirs (or one dir with 4 clearly-named `conf.py` variants loaded directly, skipping the `_write_variant_project()` machinery) is likely simpler and matches the "separate proof per key" requirement more directly than the variant-derivation machinery built for the package-only gate's larger matrix. Left to the planner to decide the exact shape.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst` (typst-py) | GATE-01 real-`typst.compile()` fixtures (all 4 required cases) | ✓ [VERIFIED: `uv run python -c "import typst; print(typst.__version__)"`, this session] | 0.15.0 | Fixtures already follow the project-wide `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` convention if it were ever absent — no new fallback needed, reuse the existing guard idiom |
| `sphinx` | Every fixture (`sys.executable -m sphinx -b typst/typstpdf`) | ✓ [VERIFIED, this session] | 9.1.0 | — |
| `pytest` | Test execution | ✓ (project-standard, already in dev extras) | project-pinned | — |
| NixOS sandbox ELF-exec constraint | Any fixture invoking a compiled binary via `uv run <binary>` directly (NOT applicable here — this phase's fixtures use `sys.executable -m sphinx`, the already-safe pattern) | N/A — pattern avoided by design | — | Already routed around per existing convention; no new risk introduced by this phase specifically |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — everything needed is already present and verified.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (project-pinned via `pyproject.toml`; config lives there, no separate `pytest.ini`) |
| Config file | `pyproject.toml` (existing `[tool.pytest.ini_options]` — not read fully this session, but confirmed present via CLAUDE.md's documented `pytest` invocation conventions) |
| Quick run command | `uv run pytest tests/test_template_engine.py -q` (unit-level, fast, no compile) |
| Full suite command | `uv run pytest -q -m "not slow"` (per project memory: exclude the 4 pre-existing environmentally-flaky `tests/test_integration_*.py` files and `tests/test_examples_basic.py` ONLY when running inside a worktree, per the documented NixOS sandbox note — not a Phase 26-specific exclusion) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONF-04 (SC#1) | `typst_elements = {"papersize": "us-letter"}` reaches `project()` as a quoted string and the compiled PDF uses that paper size | GATE-01 real-compile fixture | `uv run pytest tests/test_typst_elements_pass_through_gate.py -k papersize -q` | ❌ Wave 0 — new fixture + test module needed |
| CONF-04 (SC#2) | `typst_elements = {"fontsize": "20pt"}` reaches `project()` as an UNQUOTED length, separate fixture from papersize | GATE-01 real-compile fixture | `uv run pytest tests/test_typst_elements_pass_through_gate.py -k fontsize -q` | ❌ Wave 0 — new fixture |
| CONF-04 (SC#3) | Unrecognized `typst_elements` key raises `ExtensionError` (fail-loud), does not silently drop or reach the compile step | Unit test (fast, no compile needed — can assert on the raise directly against `map_parameters()`) PLUS one GATE-01-style build-time assertion for the "build actually aborts" proof | `uv run pytest tests/test_template_engine.py -k unknown_key -q` (unit) + `uv run pytest tests/test_typst_elements_pass_through_gate.py -k unknown_key -q` (build-level, asserting `sphinx-build` exits non-zero) | ❌ Wave 0 — both new |
| CONF-04 (SC#4) | Baseline Sphinx metadata (`copyright`) never leaks into `project()` | GATE-01 real-compile fixture (assert `copyright:` absent from the `#show: project.with(...)` region) + unit test on `map_parameters()`'s returned dict | `uv run pytest tests/test_typst_elements_pass_through_gate.py -k copyright -q` + `uv run pytest tests/test_template_engine.py -k copyright -q` | ❌ Wave 0 — both new |
| CONF-04 (SC#5) | `templates/base.typ` byte-unchanged | Static check (not a pytest test) | `git diff --stat typsphinx/templates/base.typ` shows no changes after the phase's commits (or a `hashlib`-based byte-comparison unit test, if the planner wants it automated) | ❌ Wave 0 — planner should decide whether to encode this as an automated test (e.g. a checksum assertion) or rely on code review + `git diff` |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_template_engine.py tests/test_config.py -q` (fast unit-level signal on `map_parameters()`/`_format_typst_value()`/config registration, no compile)
- **Per wave merge:** `uv run pytest tests/test_typst_elements_pass_through_gate.py -q` (the 4 real-compile GATE-01 cases) + a broader `uv run pytest -q -m "not slow"` pass
- **Phase gate:** full suite green (minus the documented pre-existing worktree-only environmental exclusions) before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/fixtures/typst_elements_pass_through_gate/` (or 4 smaller fixture dirs) — new fixture project(s) covering positive-papersize, positive-fontsize, negative-unknown-key, copyright-non-leak
- [ ] `tests/test_typst_elements_pass_through_gate.py` — new GATE-01 real-compile test module (mirrors `test_package_only_config_gate.py`'s `_run_sphinx_build()` helper and `_show_rule_call_region()` slicing helper — both are directly reusable/copyable patterns, not new inventions)
- [ ] New unit tests appended to `tests/test_template_engine.py` — `RawTypst` emission via `_format_typst_value()`, allowlist merge via `map_parameters(sphinx_metadata, typst_elements=...)`, unknown-key raise, copyright-never-in-params
- [ ] Framework install: none — pytest/typst-py/sphinx already present

## Security Domain

`security_enforcement: true`, `security_asvs_level: 1` per `.planning/config.json`. This phase is a build-time Python config-plumbing fix inside a docs-generation tool — there is no runtime network surface, no authentication, no session, no user-supplied data crossing a trust boundary at RUNTIME (the "input" here is the PROJECT OWNER's OWN `conf.py`, evaluated as trusted Python source by Sphinx itself, same trust level as any other Sphinx config value). Applicability is narrow but not zero: the new fail-loud validation IS a form of input validation (ASVS V5), and the error message must not become an injection/DoS vector.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | No auth surface in this extension |
| V3 Session Management | No | No session surface |
| V4 Access Control | No | No access-control surface — `conf.py` is already fully-trusted, project-owner-authored Python source, same trust level Sphinx itself grants it |
| V5 Input Validation | Yes (narrow) | The new allowlist check IS input validation for `typst_elements` keys — reject-unknown (allowlist, not denylist) is already the correct ASVS-aligned pattern (CONTEXT.md D-06/D-07); the error message must interpolate the offending key via an f-string with NO further formatting/eval of user content (confirmed safe: `repr()`/`!r}` on the key, not `str()` execution of it) |
| V6 Cryptography | No | No crypto surface touched |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Denial of service via a pathologically long/malformed `fontsize` string reaching `typst.compile()` and hanging/crashing the compiler | Denial of Service | Out of scope per CONTEXT.md D-09 (explicit, user-approved decision): no Python-side length-grammar validation — a malformed length is the user's own literal Typst and fails at compile time, which is an acceptable, already-established pattern in this codebase (the compiler is the authority on Typst syntax validity, same as for every other pass-through string value like `typst_template_function["params"]`) |
| Error-message string injection (an attacker-controlled `typst_elements` key containing format-string/template syntax reflected unsanitized into the `ExtensionError` message) | Tampering / Information Disclosure | Not a realistic threat here — the "attacker" is the project owner's own `conf.py`, already fully trusted; nonetheless, using an f-string with `{key!r}` (Python `repr()`, which safely escapes the value as a Python string literal) rather than directly interpolating raw untrusted text is the correct, already-idiomatic pattern and costs nothing extra to apply |

## Sources

### Primary (HIGH confidence)
- `typsphinx/writer.py` (this repo, read directly this session, lines 170-247) — the exact laundering bug site
- `typsphinx/template_engine.py` (this repo, read directly this session, full file, 491 lines) — `DEFAULT_PARAMETER_MAPPING`, `map_parameters()`, `render()`, `_format_typst_value()`
- `typsphinx/templates/base.typ` (this repo, read directly this session, lines 1-80) — `project()` signature, the byte-frozen receiving contract
- `typsphinx/builder.py` (this repo, read directly this session, lines 940-967) — `ExtensionError` precedent
- `tests/test_package_only_config_gate.py` (this repo, read directly this session, full file, 539 lines) — the GATE-01 real-compile fixture template named by ROADMAP.md/STATE.md
- `tests/test_template_engine.py` (this repo, grep + read directly this session, lines 1-40, 790-887) — existing `map_parameters()`/`_format_typst_value()` unit-test call sites and the `typst_authors`/D-07 double-formatting precedent
- `tests/test_config.py` (this repo, read directly this session, lines 90-157) — the two registration-only `typst_elements` tests referenced by CONTEXT.md
- `tests/test_config_template_mapping.py` (this repo, read directly this session, lines 190-241) — the phantom "tested separately" comment
- `tests/test_confval_field_body_render_gate.py` (this repo, read directly this session, lines 1-90) — the simpler single-fixture GATE-01 pattern (alternative to the variant-derivation machinery)
- `.planning/phases/26-.../26-CONTEXT.md` (this milestone's own artifact, read directly this session) — all D-01..D-09 locked decisions
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/config.json` (this repo, read directly this session) — CONF-04 wording, milestone invariants, workflow flags
- Installed-venv verification this session: `sphinx==9.1.0`, `typst(-py)==0.15.0`, `python==3.13.13`

### Secondary (MEDIUM confidence)
- None used — every claim in this document traces to a direct file read or direct command execution in this session (no WebSearch/Context7 lookups were needed; this phase's domain is entirely internal-codebase, not an external library integration).

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new libraries; both existing dependencies (`sphinx`, `typst-py`) directly verified present at pinned versions in this session
- Architecture: HIGH - every pattern recommended is copied from an existing, working precedent already in this exact codebase (read directly, not assumed)
- Pitfalls: HIGH - each pitfall is either an already-documented defect class from this codebase's own comments (D-07 double-formatting trap) or a directly-observed signature-compatibility fact (grep count of existing `map_parameters()` call sites)

**Research date:** 2026-07-24
**Valid until:** Stable — this is internal-codebase research with no external-ecosystem drift risk; valid indefinitely for THIS phase's planning purposes, though it should be treated as superseded the moment Phase 26 actually lands (its findings describe a not-yet-fixed bug).

# Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net - Research

**Researched:** 2026-07-12
**Domain:** docutils-node-to-Typst-markup translator fixes (single file: `typsphinx/translator.py`)
**Confidence:** HIGH — every code claim below is traced directly against the current repository source (line numbers re-verified in this session, not carried forward blind from CONTEXT.md) plus the installed docutils 0.22.4 source and live Typst official docs.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Graceful degradation (DEG-01 / DEG-02)**
- **D-01:** `graphviz` and `inheritance_diagram` render a **visible placeholder block** in the PDF
  (a bordered/boxed block naming the node, e.g. `[graphviz diagram omitted]`) **plus exactly one**
  `logger.warning` naming the node type. This honors REQ DEG-01's literal "visible placeholder
  block" wording — the reader must be able to tell a diagram was there — and is stronger than the
  roadmap SC#3 "warning + no-leak" minimum. Do **not** reuse the gentle-clues warning box (avoids
  visual confusion with real admonitions), and do **not** silently skip. No raw DOT / diagram
  source may leak into the output. DEG-01 and DEG-02 share one helper.

**Length-unit conversion (FIG-01)**
- **D-02:** Unit handling on image `:width:`/`:height:`:
  - `px` → `pt` via the CSS-canonical `1px = 0.75pt`.
  - **Bare unitless numbers are treated as `px`** (HTML/CSS convention) → `× 0.75pt`.
  - `%`, `em`, `pt`, `cm`, `mm`, `in` pass through as valid Typst lengths.
  - `pc` → convert to `pt`.
  - **Unknown / unconvertible units** (incl. `ex`) → emit **one** `logger.warning` and **drop the
    `width`/`height` dimension entirely** (image renders at natural size). Never emit a raw
    unsupported unit like `width: 200px` — that is the FIG-01 fatal case.
  - Centralize in a single `_convert_length_to_typst()` helper used by `visit_image`.

**`:target:` figure/image coverage (FIG-02)**
- **D-03:** Support **both** external-URL targets (`link("url")[...]`) **and** internal
  reference / doc targets (`link(<label>)[...]`) in this phase — not just the external-URL Issue #114
  reproduction. Same buffer-swap code path handles both by branching on refuri vs refid; added cost
  is small and Sphinx's own `doc/` tree (the milestone corpus) uses internal `:target:` references
  heavily. Emit valid `#figure(link(...)[#image(...)], caption: [...])`; the caption reaches the
  `caption:` named argument via buffer-swap and never leaks as a stray juxtaposed `text(...)`.

**Acceptance gate (GATE-01)**
- **D-04:** Extend the existing `tests/test_pdf_render_gate.py` (the v0.5.0 admonition D-04 gate:
  `sphinx-build → typst.compile() → pypdf` text-extraction with negative-control leak signatures).
  Keep the `slow` marker so local runs stay fast, but the gate **runs in CI's `cov` job where
  typst-py/pypdf are present** — i.e. it is **effectively required**: it must not `skip` in CI and
  fails loudly on any `TypstCompilationError`. This matches the milestone thesis that
  string-agreement unit tests alone are insufficient (pitfall #9). This gate is the standing bar
  every later node-handler phase (12–14) extends.

### Claude's Discretion
- Exact placeholder-block styling (border, padding, wording) — reader must recognize an omitted
  diagram; precise Typst styling is the planner/executor's call.
- Exact `logger.warning` message text (must name the node type).
- Internal structure of `_convert_length_to_typst()` and the DEG shared helper.
- Fixture document contents beyond the explicit success-criteria cases below.

### Deferred Ideas (OUT OF SCOPE)
- **Real `graphviz` / `inheritance_diagram` rendering** (shell out to `dot`, image negotiation) —
  explicitly Out of Scope this milestone; placeholder-only here.
- **LEN-01** — generalizing the length converter beyond the named units (legacy unitless HTML widths
  beyond the px assumption, additional exotic units) — Future Requirement, trigger = next non-`px`
  length-unit fatal report.
- Node handlers VER-01 / XREF-01 / DESC-* / BLK-* / FN-01 — Phases 12–14, not here.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FIG-01 | `:width:`/`:height:` CSS length units compile to valid Typst — px→pt (1px=0.75pt), pass-through units, warn-and-drop unknowns | Part 2 (`_convert_length_to_typst`), Code Examples §1, docutils normalization findings (verified against installed docutils 0.22.4 source) |
| FIG-02 | `:target:`-linked figure/image caption reaches `caption:` via buffer-swap, no stray juxtaposed `text(...)` | Part 1 (caption buffer-swap trace), Code Examples §2, refid/refuri branching findings |
| DEG-01 | `graphviz` renders a visible placeholder block + exactly one warning, no raw DOT leak | Part 3 (shared DEG helper), Code Examples §3 |
| DEG-02 | `inheritance_diagram` shares the DEG-01 helper | Part 3, Code Examples §3 |
| GATE-01 | Real-compile acceptance fixture (`sphinx-build → typst.compile() → pypdf`), extends `tests/test_pdf_render_gate.py` | Validation Architecture section, GATE-01 structure findings (current file read in full) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- All work is scoped to `typsphinx/translator.py` per CONTEXT.md; CLAUDE.md's architecture
  description of `translator.py` as "the file you will most often edit ... ~140 `visit_*`/`depart_*`
  methods" confirms this is consistent with established project structure — no new file layer needed.
- `ruff` ignores `N802` for docutils' PascalCase visitor method names (e.g. `visit_Text`) — new
  handlers (`visit_graphviz`, `visit_inheritance_diagram`) follow the existing `visit_<ClassName>`
  naming convention and need no additional ruff suppression.
- Black line length 88; `E501` ignored in ruff (black owns wrapping) — no special handling needed
  for the longer f-strings in `_convert_length_to_typst`.
- **Discrepancy found, flag for planner:** CLAUDE.md's Commands section states "matrixed across
  py310–py313" and "Python 3.10+ compatibility is required (ruff ignores UP006/UP035)". The actual
  `pyproject.toml` declares `requires-python = ">=3.12"` and `tox.ini`'s `env_list = py312, py313,
  lint, type, cov, docs` — **no py310/py311 environments exist**. `[VERIFIED: pyproject.toml,
  tox.ini]`. This appears to be stale CLAUDE.md content from an earlier project era. **Practical
  effect on this phase: none** — `str | None`/`dict`/`list` builtin generics (PEP 604/585) are
  already used throughout `translator.py` (e.g. line 86, line 1749) and are fully compatible with
  the actual 3.12+ floor. Use modern syntax (`str | None`, not `Optional[str]`) for the new
  `_convert_length_to_typst()` helper — matches both the actual floor and the existing file style.
- `mypy typsphinx/` runs in CI (`[testenv:type]`) — the new helper method needs full type
  annotations (`def _convert_length_to_typst(self, value: str) -> str | None:` or similar) to pass.
- No project skills directory exists at `.claude/skills/` or `.agents/skills/` for this repo beyond
  the global GSD skill set — no additional project-specific conventions to load.

## Summary

Phase 11 is a narrow, single-file fix: two fatal Typst-compile bugs in `visit_image`/`visit_caption`/
`depart_figure` plus two new graceful-degrade visitor overrides, entirely inside
`typsphinx/translator.py`. Both fatal bugs were traced in this session against the **current**
source (all cited line numbers reconfirmed by direct `Read`, not carried forward from CONTEXT.md
verbatim): `visit_image` (`:1501`) emits `width`/`height` from `node["width"]`/`node["height"]`
completely unconverted at lines **1527–1533**, and `visit_caption`/`depart_caption` (`:1201`/`:1217`)
has no buffer-swap — the caption's `Text` children stream straight into the live `self.body` via the
generic `visit_Text` (line 495 emits a bare `text("...")` call with **no separator**), while
`depart_caption` (line 1226) *also* re-derives the same text via `node.astext()` for later reuse as
`caption: [...]` — producing both the syntax-breaking juxtaposition and a literal doubled-caption
leak in one bug.

The recommended fix for both bugs reuses patterns **already proven working elsewhere in this exact
file**: the admonition-title buffer-swap (`visit_title`/`depart_title`, lines 190–238) is the direct
precedent for the caption fix, and a dedicated length-parsing helper following the
`_compute_relative_image_path` docstring/doctest convention (line 1748) is the right shape for
`_convert_length_to_typst()`. Graceful degradation for `graphviz`/`inheritance_diagram` needs two new
`visit_*` methods placed near the existing `visit_index` (`raise nodes.SkipNode` precedent, line
2483) — but per the **locked** D-01 decision, unlike `visit_index`'s silent skip, these must emit a
visible bordered placeholder using native Typst `rect()`/`box()` (not the gentle-clues admonition
functions already imported for `note`/`warning`/etc.) plus exactly one `logger.warning`.

A critical cross-cutting finding from reading the installed **docutils 0.22.4** source directly
(not from training-data assumption): docutils' own `length_or_percentage_or_unitless`/
`length_or_unitless` option converters (`docutils/parsers/rst/directives/__init__.py`) already
normalize `:width:`/`:height:` into a concatenated `"<value><unit>"` string (e.g. `"200px"`, `"50%"`,
`"300"` for bare unitless, `"2in"`) **before** the translator ever sees it — so `node["width"]` is
always a single string with no internal whitespace, and the translator's job is purely a
regex-driven unit-suffix rewrite, not general CSS-length parsing. Also confirmed: docutils'
`CSS3_LENGTH_UNITS` tuple includes `ch`, `rem`, `vw`, `vh`, `vmin`, `vmax`, `Q` in addition to the
units named in CONTEXT.md's D-02 — these are docutils-valid but **not** named in D-02's
pass-through/convert list, so they correctly fall into the "unknown → warn + drop" branch (see Open
Questions). Also confirmed: `:height:` uses `length_or_unitless` which does **not** accept `%` at
all — a `:height: 50%` fixture would be rejected by docutils itself before reaching the translator,
so only `:width:` needs a percentage fixture.

**Primary recommendation:** Fix `_convert_length_to_typst()` and the caption buffer-swap as two
fully independent, parallel-safe changes (zero shared state); add the two DEG visitor overrides as a
third independent change; then extend `tests/test_pdf_render_gate.py` with new fixture projects
(not new test *files* — keep the existing `LEAK_SIGNATURES` pattern and skipif guard) that exercise
all three fixes through a real `typst.compile()`. Do **not** attempt the milestone-brief's literal
`link(url)[#image(...)]` markup-sugar rewrite of `visit_reference`/`visit_image` — the existing
two-positional-argument `link("url", image(...))` form is already valid Typst and requires zero
changes to those methods; only `visit_caption`/`depart_caption`/`depart_figure` need to change for
FIG-02.

## Architectural Responsibility Map

This project is a single-process CLI/library pipeline (Sphinx builder extension), not a multi-tier
web application — the "tiers" here are pipeline stages, not client/server/DB layers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Length-unit conversion (px→pt, pass-through, warn-drop) | Translator (`visit_image`) | — | Pure string/regex transform at the doctree-attribute-to-Typst-syntax boundary; no I/O, no state beyond the node |
| Caption buffer-swap (`visit_caption`/`depart_caption`/`depart_figure`) | Translator (visitor state) | — | Must plug into `self.body` accumulator state already owned by the translator; cannot be extracted to a pure function |
| `:target:` refid/refuri branching | Translator (`visit_reference`) | Docutils transform pipeline (upstream) | The refid vs refuri distinction is *resolved* by docutils' own reference-resolution transforms before the translator runs; translator only branches on the already-resolved attribute |
| Graphviz/inheritance-diagram graceful degrade | Translator (`visit_graphviz`/`visit_inheritance_diagram`) | — | New isolated visitor methods; no shared state with other handlers per D-01 |
| Real-compile acceptance gate | Test/CI harness (`tests/test_pdf_render_gate.py`) | CI workflow (`cov` job in `.github/workflows/ci.yml`) | Validates translator output via the actual `typst-py` compiler + `pypdf` extraction — a downstream verification tier, not part of the translator itself |
| Sphinx `doc/` corpus validation (GATE-02, later phase) | CI workflow (`docs-pdf`/`docs` tox env) | — | Out of scope for Phase 11; noted only for context (Phase 15) |

## Standard Stack

### Core

No new dependencies. Every fix in this phase is achievable with the already-pinned stack:

| Library | Version (pinned) | Purpose | Why Standard |
|---------|------|---------|--------------|
| `typst` (typst-py) | `>=0.15.0,<0.16` [VERIFIED: pyproject.toml `dependencies`] | Real PDF compile in the render gate; core runtime dep of `typstpdf` builder | Already the project's compile engine (`pdf.py`); no version bump needed — native `rect()`/`box()`/length units used by this phase's fixes are all Typst 0.15 stdlib |
| `docutils` | `>=0.21,<0.23` [VERIFIED: pyproject.toml `dependencies`]; installed test env has `0.22.4` [VERIFIED: `docutils.__version__` in project's own `.tox/py312` venv] | Source of the `:width:`/`:height:` normalized strings and `refuri`/`refid` reference resolution | Already the project's parser; no change needed |
| `pypdf` | `>=6.14,<7` [VERIFIED: pyproject.toml `dev` extras] | Text-extraction half of the render gate (`tests/test_pdf_render_gate.py`) | Already used by the existing D-04 gate; extend, don't replace |
| `sphinx` | `>=9.1,<10` [VERIFIED: pyproject.toml `dependencies`] | `graphviz`/`inheritance_diagram` node types come from `sphinx.ext.graphviz`/`sphinx.ext.inheritance_diagram` (both bundled with Sphinx core, no separate PyPI package) | No new dependency — these extensions ship inside the `sphinx` package already installed |

### Supporting

No supporting libraries needed beyond the above. `re` (already imported at `translator.py:8`) is
sufficient for the length-unit regex; no new stdlib imports required.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Regex-based unit-suffix parsing in `_convert_length_to_typst()` | Reuse docutils' own `nodes.parse_measure()` internally | Would add an implicit dependency on a **provisional** (docutils' own docstring says "Provisional") internal API (`docutils.nodes.parse_measure`, confirmed at `nodes.py:3084` in the installed 0.22.4 source) not part of docutils' stable public contract; a small local regex is more robust against upstream churn and keeps the helper self-contained per D-02's "centralize in a single helper" instruction |
| Native Typst `rect()`/`box()` for the DEG-01/02 placeholder | Reuse gentle-clues (`clue`/`warning` functions, already imported in `templates/base.typ`) | **Explicitly rejected by D-01** ("do not reuse the gentle-clues warning box (avoids visual confusion with real admonitions)") — use Typst stdlib `rect()`/`box()` instead, zero new `@preview` surface touched |
| Straight px→pt passthrough (treat px value as already pt) | CSS-canonical `1px = 0.75pt` conversion | The milestone-level ARCHITECTURE.md flagged straight-passthrough as "acceptable if the bar is only 'don't fatal-error'" — but CONTEXT.md's **locked D-02 decision overrides this** with the precise `0.75` ratio; follow D-02, not the milestone doc's softer alternative |

**Installation:** None required — this phase adds zero new packages.

**Version verification:** `typst` and `pypdf` versions above were confirmed directly by reading
`pyproject.toml`'s `dependencies`/`dev` extras in this session (`[VERIFIED: pyproject.toml]`);
`docutils.__version__` was confirmed by executing Python against the project's own `.tox/py312`
virtualenv in this session (`[VERIFIED: installed docutils 0.22.4]`).

## Package Legitimacy Audit

**Not applicable this phase.** Per the locked CONTEXT.md decision ("Zero new runtime dependencies")
and confirmed by this research (no new `import` statements needed — `re`, `nodes.SkipNode`, and the
existing `logger` cover every fix), Phase 11 introduces **no new external packages** in any
ecosystem. No legitimacy check is required.

**Packages removed due to [SLOP] verdict:** none (N/A — no packages proposed)
**Packages flagged as suspicious [SUS]:** none (N/A — no packages proposed)

## Architecture Patterns

### System Architecture Diagram

```
docutils doctree (figure/image/graphviz/inheritance_diagram nodes)
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│ TypstTranslator.walkabout()  (typsphinx/translator.py)         │
│                                                                 │
│  visit_image ──▶ _convert_length_to_typst(width/height) ──┐    │
│       │                                                    │    │
│       │   [FIG-01: px→pt / pass-through / warn+drop]      │    │
│       ▼                                                    ▼    │
│   image("uri", width: <converted>, height: <converted>)        │
│                                                                 │
│  visit_reference (figure's :target:) ──▶ refuri? ──▶ external  │
│       │                                   │                    │
│       │                                   └─refid?──▶ internal │
│       │                                        (label link)    │
│       ▼                                                        │
│  visit_caption ──[buffer-swap: self.body → scratch list]──▶     │
│       │                     children render via normal          │
│       │                     visit_Text/visit_emphasis/etc.      │
│       ▼                                                        │
│  depart_caption ──[join scratch, restore self.body]──▶          │
│       │                     self.figure_caption = rendered code │
│       ▼                                                        │
│  depart_figure ──▶ figure(..., caption: {rendered code})        │
│                                                                 │
│  visit_graphviz / visit_inheritance_diagram                    │
│       │  [DEG-01/02: shared helper]                             │
│       ├─▶ logger.warning(node type)                             │
│       ├─▶ emit rect(text("[... omitted]"), stroke: ...)         │
│       └─▶ raise nodes.SkipNode  (children never visited)        │
└───────────────────────────────────────────────────────────────┘
        │
        ▼
   body string ──▶ TemplateEngine ──▶ .typ file
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│ GATE-01: tests/test_pdf_render_gate.py (extended)               │
│   sphinx-build -b typst  ──▶  typst.compile()  ──▶  pypdf        │
│   text-extraction  ──▶  assert LEAK_SIGNATURES absent           │
│   ──▶ assert placeholder wording / caption text present exactly │
│        once / negative-control tokens (raw DOT, unknown unit)   │
│        absent                                                   │
└───────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

No new directories or modules. Additions land in existing locations:

```
typsphinx/
└── translator.py            # + _convert_length_to_typst(), buffer-swap fix in
                              #   visit_caption/depart_caption/depart_figure,
                              #   refid branch in visit_reference,
                              #   + _visit_graphical_placeholder() shared DEG helper,
                              #   + visit_graphviz/visit_inheritance_diagram
tests/
├── test_pdf_render_gate.py  # extended with new test methods (same class or a
                              #   sibling class in the same file per D-04)
└── fixtures/
    ├── figure_length_render_gate/    # new: :width:/:height: unit fixtures
    ├── figure_target_caption_render_gate/  # new: :target: + special-char caption
    └── graphviz_degrade_render_gate/       # new: graphviz + inheritance_diagram
```

### Pattern 1: Buffer-Swap (defer rendered content) — apply to `visit_caption`/`depart_caption`

**What:** Save `self.body` to a scratch variable, point `self.body` at a fresh list, let the node's
children render *through the normal visitor chain* (so `emph`/`strong`/`reference` inside a caption
still work and inherit proper escaping), then join the scratch list and restore `self.body`.

**When to use:** Any content that must be captured now but emitted later in a different argument
position (a named `caption:`/`title:` kwarg) — never via `node.astext()`.

**Proven precedent in this exact file** (`translator.py:190–238`, the admonition-title fix from
Phase 8.1):
```python
# Source: typsphinx/translator.py:205-212 (visit_title, admonition branch)
if isinstance(node.parent, nodes.Admonition):
    self._saved_body_for_admonition_title = self.body
    self.body = []
    self._in_admonition_title = True
    return
```
```python
# Source: typsphinx/translator.py:229-235 (depart_title, admonition branch)
if self._in_admonition_title:
    self._pending_admonition_title = "".join(self.body)
    if self._saved_body_for_admonition_title is not None:
        self.body = self._saved_body_for_admonition_title
    self._saved_body_for_admonition_title = None
    self._in_admonition_title = False
    return
```

**Recommended fix shape for `visit_caption`/`depart_caption`/`depart_figure`** (new state:
`self._saved_body_for_figure_caption`, mirroring the admonition-title variable naming exactly):
```python
def visit_caption(self, node: nodes.caption) -> None:
    if self.in_captioned_code_block:
        raise nodes.SkipNode
    self.in_caption = True
    if self.in_figure:
        self._saved_body_for_figure_caption = self.body
        self.body = []

def depart_caption(self, node: nodes.caption) -> None:
    if self.in_figure:
        self.figure_caption = "".join(self.body)
        if self._saved_body_for_figure_caption is not None:
            self.body = self._saved_body_for_figure_caption
        self._saved_body_for_figure_caption = None
    self.in_caption = False
```
```python
# depart_figure: emit the buffered CODE-MODE content in a {...} code block,
# NOT a [...] markup block -- the buffer holds text("...") function calls,
# which must evaluate, not print literally (the exact v0.5.0 admonition-bug
# class, generalized to figures per Pitfall 2).
if self.figure_caption:
    self.add_text(f",\n  caption: {{{self.figure_caption}}}")
```

**Why this incidentally fixes the escaping/special-character requirement (FIG-02's `_ * `` ` `` [
]` caption case) for free:** Because the caption now renders through the normal `visit_Text` chain
(`translator.py:443–499`) instead of `node.astext()`, the caption text is emitted as a `text("...")`
**string-literal argument**, which already applies `visit_Text`'s existing backslash/quote/
newline/CR/tab escaping (lines 464–468). Markup-special characters (`_`, `*`, `` ` ``, `[`, `]`) are
inert inside a Typst string literal — they are only "live" syntax inside a markup `[...]` content
block, which this fix never uses for the caption. No *new* escaping logic is needed beyond the
buffer-swap itself.

### Pattern 2: Length-unit conversion helper — new `_convert_length_to_typst()`

**What:** A small, pure, well-documented helper (docstring + doctest examples, matching the
`_compute_relative_image_path` convention at `translator.py:1748–1775`) that maps a docutils-
normalized length string to a Typst-valid length string, or `None` if it should be dropped.

**When to use:** Called from both the `width` and `height` branches inside `visit_image`
(`translator.py:1527` and `1531`), replacing the current verbatim interpolation.

**Confirmed input shape (verified against installed docutils 0.22.4 source, not assumed):**
`docutils/parsers/rst/directives/images.py` sets `option_spec['width'] =
directives.length_or_percentage_or_unitless` and `option_spec['height'] =
directives.length_or_unitless`. Both route through `get_measure()` →
`nodes.parse_measure()`, which returns `f'{value}{unit}'` with **no space** between them — so
`node["width"]`/`node["height"]` is always one of these normalized string shapes:
- `"200px"`, `"3em"`, `"2in"`, `"1pc"`, `"50%"` (width only — `%` is rejected for `:height:`, see
  Open Questions), `"5cm"`, `"3mm"`, `"12pt"`
- `"300"` (bare unitless — docutils does **not** append a unit itself; the "treat unitless as px"
  rule is the translator's own responsibility per D-02, not docutils')
- Additionally CSS3-valid-but-Typst-invalid: `"1ex"`, `"2ch"`, `"1rem"`, `"10vw"`, `"10vh"`,
  `"5vmin"`, `"5vmax"`, `"1Q"` — all correctly fall into the "unknown → warn + drop" branch per D-02
  (only `ex` was explicitly named in CONTEXT.md; the others are the same class of gap, see Open
  Questions).

**Example implementation shape:**
```python
_TYPST_PASSTHROUGH_UNITS = {"%", "em", "pt", "cm", "mm", "in"}

def _convert_length_to_typst(self, value: str) -> str | None:
    """
    Convert a docutils-normalized CSS length string to a Typst-valid length.

    Docutils' `length_or_percentage_or_unitless`/`length_or_unitless` option
    converters (see docutils/parsers/rst/directives/__init__.py) normalize
    `:width:`/`:height:` into a single "<value><unit>" string with no space
    (e.g. "200px", "50%", "300" for bare unitless). This helper rewrites
    that string into one Typst's length grammar accepts, or returns None if
    the unit cannot be represented (caller should then omit the attribute
    entirely, letting the image render at its natural size).

    Args:
        value: Docutils-normalized length string (e.g. "200px", "50%", "300").

    Returns:
        A Typst-valid length string, or None if the unit is unsupported.

    Examples:
        >>> _convert_length_to_typst("200px")
        "150pt"
        >>> _convert_length_to_typst("300")
        "225pt"
        >>> _convert_length_to_typst("50%")
        "50%"
        >>> _convert_length_to_typst("1pc")
        "12pt"
        >>> _convert_length_to_typst("2ex")
        None
    """
    match = re.fullmatch(r"(-?[0-9.]+)([a-zA-Zµ%]*)", value)
    if not match:
        logger.warning(f"Could not parse length value '{value}'; dropping.")
        return None
    number_str, unit = match.group(1), match.group(2)
    number = float(number_str)

    if unit == "" or unit == "px":
        pt_value = number * 0.75  # CSS canonical: 96px/in / 72pt/in
        return f"{pt_value:g}pt"
    if unit == "pc":
        return f"{number * 12:g}pt"  # 1 pica = 12 points
    if unit in self._TYPST_PASSTHROUGH_UNITS:
        return value  # already Typst-valid, pass through unchanged
    logger.warning(
        f"Unsupported length unit '{unit}' in '{value}'; "
        "dropping dimension (image will use its natural size)."
    )
    return None
```
```python
# visit_image, replacing lines 1527-1533:
if "width" in node:
    converted = self._convert_length_to_typst(node["width"])
    if converted is not None:
        self.add_text(f", width: {converted}")
if "height" in node:
    converted = self._convert_length_to_typst(node["height"])
    if converted is not None:
        self.add_text(f", height: {converted}")
```

Never string-strip a trailing unit suffix positionally (e.g. `value[:-2]`) — `px`/`pc`/`pt`/`in`/
`cm`/`mm` are all 2 characters, `em`/`Q` are 1–2 characters, `%` has no letter at all; a regex-based
split on the numeric/alpha boundary (as above) is the only robust approach, matching Pitfall 5's
explicit warning.

### Pattern 3: `:target:` refid vs refuri branching in `visit_reference`

**What:** Extend `visit_reference`'s existing empty-URL guard (lines 1972–1983) with a `refid`
fallback check **before** the empty-URL bail-out, mirroring the existing `#`-prefixed internal-label
branch (line 1989).

**Confirmed docutils behavior for internal `:target:` values** (verified against installed
docutils 0.22.4 `parsers/rst/directives/images.py:81–104`): when a Figure/Image directive's
`:target:` option is an internal reference name (e.g. `` :target: `Some Section`_ `` or a bare
label), docutils sets `refname=` on the wrapping `reference` node (not `refid` directly) — this
`refname` is then resolved into either `refid` (same-document internal target) or `refuri`
(cross-document/external) by docutils' standard `references` transform pass, which runs **before**
the writer/translator sees the tree. By the time `visit_reference` executes, an internal `:target:`
therefore presents as an **empty (or absent) `refuri`** with a populated `node["refid"]` — this is
architecturally the *same gap* the milestone's Phase 12 XREF-01 targets generally for prose
cross-references, but Phase 11 needs the minimal slice of it scoped to make figure `:target:` links
compile, not XREF-01's full corpus-wide empty-URL-reduction measurement.

**Recommended fix (insert between line 1970's `refuri` extraction and line 1976's empty-URL
branch):**
```python
refuri = node.get("refuri", "")
refid = node.get("refid", "")

if not refuri and refid:
    # Internal same-document target resolved via refid (e.g. a figure's
    # `:target:` pointing at a doc-internal label). Same link(<label>, ...)
    # shape already used for the "#"-prefixed refuri case below (line 1992).
    prefix = "#" if self._in_markup_mode else ""
    self.add_text(f"{prefix}link(<{refid}>, ")
    if self._in_markup_mode:
        self._in_markup_mode = False
    self._in_link = True
    self._link_has_content = False
    self._reference_was_list_item_needs_separator = was_list_item_needs_separator
    return  # skip the refuri-based branches below

if not refuri:
    logger.warning(...)  # existing empty-URL branch, unchanged
    ...
```
No sanitization of `refid` beyond direct interpolation is needed for symmetry with the existing
`#`-prefixed branch (line 1991: `label = refuri[1:]`, used directly with no `.replace()` calls) —
`refid` values are docutils-generated ids, already label-safe.

**Scope note for the planner:** this is a small, additive change inside `visit_reference` — it does
**not** duplicate into a new method, and it does not attempt XREF-01's broader "measure the
empty-URL warning-count reduction across Sphinx's own docs" mandate (that empirical measurement is
explicitly Phase 15/GATE-02's job). Phase 11 only needs this fix to exist so a figure's internal
`:target:` compiles; Phase 12's XREF-01 will build on the same code path for plain prose references.

### Pattern 4: Graceful-degrade placeholder (DEG-01/DEG-02) — shared helper, NOT the admonition pattern

**What:** `TypstTranslator.unknown_visit`/`unknown_departure` (`translator.py:2038–2059`,
reconfirmed this session) already provide a generic "log and continue descending into children"
fallback for any node type with no explicit visitor — but it does **not** raise `SkipNode`, so
descending into `graphviz`/`inheritance_diagram` children risks leaking any incidental text
children. D-01 requires an explicit, visible placeholder plus exactly one warning, which
`unknown_visit`'s generic path does not provide (no placeholder, and no skip).

**When to use:** Any out-of-scope graphical node whose real content is unrenderable this milestone.

**Reusable "log and skip cleanly" precedent** (`translator.py:2483–2489`, `visit_index`):
```python
def visit_index(self, node: addnodes.index) -> None:
    """Index entries are skipped in Typst/PDF output as we don't generate indices."""
    raise nodes.SkipNode
```
This precedent proves the "open nothing, emit nothing, `raise nodes.SkipNode`" idiom is already
established for out-of-scope nodes — **DEG-01/02 extends it with a visible placeholder + warning**,
which `visit_index` does not need (index entries have no reader-visible absence to flag).

**Recommended shared helper** (placed near `visit_index`, per the file's existing "out-of-scope
node" neighborhood):
```python
def _visit_graphical_placeholder(self, node: nodes.Node, node_label: str) -> None:
    """
    Shared graceful-degrade helper for out-of-scope graphical nodes.

    Emits a visible bordered placeholder block naming the node type (D-01),
    logs exactly one warning, and skips the node's children entirely --
    `graphviz`/`inheritance_diagram` store their real content (DOT source /
    class-hierarchy spec) as node attributes, not human-readable Text
    children, so descending would risk leaking raw source rather than
    rendering anything useful.

    Uses native Typst rect()/box() (Typst 0.15 stdlib) rather than the
    gentle-clues admonition functions already imported for note/warning/etc,
    per D-01: a graphviz placeholder must not be visually confusable with a
    real admonition.

    Args:
        node: The out-of-scope node (graphviz or inheritance_diagram).
        node_label: Human-readable node-type name for the warning + placeholder text.
    """
    logger.warning(f"{node_label} is not supported in Typst output; rendering placeholder")
    # Code-mode call: rect()'s body argument accepts a content value
    # positionally; text(...) already returns Typst content, matching the
    # file's established "content-producing expression, not literal string"
    # convention (see _visit_admonition, translator.py:2321).
    self.add_text(
        f'rect(text("[{node_label} diagram omitted]"), '
        f'stroke: 0.5pt, inset: 8pt, radius: 2pt)\n\n'
    )
    raise nodes.SkipNode

def visit_graphviz(self, node: nodes.Node) -> None:
    self._visit_graphical_placeholder(node, "graphviz")

def visit_inheritance_diagram(self, node: nodes.Node) -> None:
    self._visit_graphical_placeholder(node, "inheritance diagram")
```
No `depart_*` methods are needed — `raise nodes.SkipNode` in `visit_*` means `depart_*` is never
reached (confirmed by `visit_index`'s identical no-`depart_index`-needed shape, though this file
does still define a no-op `depart_index` at line 2491; either convention — omit or no-op — is
correct docutils practice since `SkipNode` prevents the departure callback from firing for the
skipped node itself, only for the node whose visit raised it).

**Verify note (must confirm at implementation time, not assumed):** confirm the exact class names
docutils/Sphinx registers on the tree — `sphinx.ext.graphviz` registers a node class literally named
`graphviz` (lowercase, `sphinx.ext.graphviz.graphviz`), and `sphinx.ext.inheritance_diagram`
registers `inheritance_diagram` (`sphinx.ext.inheritance_diagram.inheritance_diagram`) — both
confirmed by Sphinx's own extension module naming convention (the docutils dispatch mechanism calls
`visit_<node.__class__.__name__>`, so the method names above must exactly match these class names,
case-sensitive) `[ASSUMED — verify against a live doctree dump or Sphinx source before finalizing
method names; not independently re-verified against the sphinx.ext.graphviz/inheritance_diagram
module source in this research pass]`.

### Anti-Patterns to Avoid

- **Using `node.astext()` for any new interpolation site:** bypasses both the string-literal
  escaping regime (`visit_Text` lines 464–468) and markup-mode escaping, and is the literal
  mechanism behind the current `depart_caption` bug (line 1226). Never introduce a new `astext()`
  call in this phase's fixes.
- **Wrapping buffered code-mode content in `[...]` (markup block) instead of `{...}` (code block):**
  the exact v0.5.0 admonition bug class — a code block whose statements are `text(...)`/`emph(...)`
  calls must be wrapped so those calls *evaluate*, not print as literal source.
- **Silent `except Exception: pass` for the DEG-01/02 fallback:** already flagged project-wide in
  `.planning/codebase/CONCERNS.md` as an existing tech-debt pattern; D-01 requires an explicit
  `logger.warning` every time, no exception-swallowing needed at all since `raise nodes.SkipNode` is
  a clean, expected control-flow signal, not an error condition.
- **Reusing `_visit_admonition`/gentle-clues `clue_type` functions for the DEG placeholder:**
  explicitly forbidden by D-01 (visual-confusion risk with real admonitions).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSS-length-to-Typst-length parsing | A general CSS length/measure parser | A small regex (`(-?[0-9.]+)([a-zA-Zµ%]*)`) scoped to the known unit set from D-02 | Docutils has already validated and normalized the string (no whitespace, single value+unit); a general parser is unneeded scope creep and risks importing docutils' provisional internal `parse_measure` API |
| Visible "unsupported feature" placeholder | A new `@preview` package or custom Typst function library | Native Typst `rect()`/`box()` stdlib calls | Zero new dependencies is a locked project-wide constraint (CONTEXT.md, PROJECT.md); `rect()`/`box()` are Typst 0.15 stdlib, confirmed via official docs |
| Real-compile PDF validation | A bespoke Typst-syntax linter/AST checker | The existing `tests/test_pdf_render_gate.py` `sphinx-build → typst.compile() → pypdf` pipeline | Already proven (Phase 8.1/D-04); string-level syntax checking cannot detect the class of bug this milestone exists to fix (Pitfall 9) |

**Key insight:** Every "don't hand-roll" item in this phase resolves to "reuse the pattern this exact
codebase already proved correct" — length parsing reuses the docstring/doctest convention of
`_compute_relative_image_path`, the caption fix reuses the admonition-title buffer-swap verbatim,
and the render gate reuses D-04's exact `sphinx-build → typst.compile() → pypdf` shape. This phase
should feel like "apply the same medicine three more times," not "invent new machinery."

## Common Pitfalls

Carried forward from `.planning/research/PITFALLS.md` (milestone-level), filtered to the ones this
phase must actively defend against, plus this session's own confirmations:

### Pitfall 1: One bad node aborts the ENTIRE PDF
**What goes wrong:** `typst.compile()` (`pdf.py`) is all-or-nothing over the master doc + every
`#include()`d file. A single `width: 200px` or one caption-double-emission anywhere in the corpus
fails the whole build.
**How to avoid:** Every fixture in this phase's render-gate extension must go through a real
`typst.compile()`, not a string assertion (see Validation Architecture). Treat "does it compile" as
the primary signal.
**Confirmed live in current code:** `visit_image` lines 1527–1533 emit `width: {width}` completely
unconverted today — any real `:width: 200px` in a Sphinx doc currently fails the whole
`typstpdf` build.

### Pitfall 2/3: Markup/code-mode mismatch + the figure-caption double-emission leak
**What goes wrong:** `depart_caption` (line 1226) computes `self.figure_caption = node.astext()`
while `visit_caption` (line 1201–1215) never buffer-swaps `self.body` — so the caption's `Text`
children stream through the *live* `visit_Text` (line 495) and land immediately after
`depart_reference`'s closing `")"` with **no separator**, producing exactly the reported
`link(...)text(caption)` juxtaposition, **and** a second correctly-placed copy in `caption: [...]`.
**Confirmed via full trace in this session** (see Summary and Pattern 1 above) — this is the single
highest-priority fix in the phase.
**How to avoid:** Buffer-swap per Pattern 1; wrap the restored buffer in `{...}` (code block), never
`[...]` (markup block).

### Pitfall 4: Function-call juxtaposition
**What goes wrong:** Typst code-mode requires expressions to be separated by `+`/`;`/newline;
`image(...)` immediately followed by `text(...)` with nothing between is a parse error.
**How to avoid:** The buffer-swap fix in Pattern 1 eliminates the juxtaposition at its root (the
caption content never touches the live `self.body` stream at all) — no separate `+`-joining flag is
needed for this specific fix, unlike the `desc_parameter` family's ongoing pattern.

### Pitfall 5: px→pt is not 1:1
**What goes wrong:** Typst's length grammar has no `px` unit (confirmed via official Typst docs,
`https://typst.app/docs/reference/layout/length/`, and the open feature request
`https://github.com/typst/typst/issues/6849`) — passing `200px` straight through is a hard compile
error.
**How to avoid:** `_convert_length_to_typst()` per Pattern 2, following D-02's exact `0.75`
conversion factor. Never blind-strip a trailing unit suffix by fixed character count.

### Pitfall 7: Escaping regimes
**What goes wrong:** Using `astext()` bypasses both string-literal escaping and markup escaping.
**How to avoid:** As covered in Pattern 1 — the buffer-swap fix routes the caption through
`visit_Text`'s existing string-literal escaping automatically; this is a side benefit of the fix,
not extra work.

### Pitfall 9: String-agreement testing alone proves nothing
**What goes wrong:** `"info[" in output`-style substring asserts passed for months while the actual
compiled PDF showed literal Typst source (the admonition bug's own history, per PITFALLS.md).
**How to avoid:** Every new/changed behavior in this phase needs a `typst.compile()`-backed fixture
in the extended `tests/test_pdf_render_gate.py`, not just translator-output unit tests. See
Validation Architecture.

### Pitfall 10: Graceful degradation done wrong
**What goes wrong:** Silent `except: pass`, or a "safe" fallback that itself emits invalid Typst
(wrong mode) or leaves orphaned state (opens something in `visit_*` that `depart_*` can't safely
close).
**How to avoid:** The DEG helper (Pattern 4) opens nothing that needs closing — it emits one
complete `rect(...)` call and immediately `raise nodes.SkipNode`s. Always pair with exactly one
`logger.warning` naming the node type.

### New pitfall found this session: docutils-valid-but-Typst-invalid CSS units beyond `ex`
**What goes wrong:** D-02 explicitly names `ex` as an "unknown → warn + drop" example, but the
installed docutils 0.22.4 `CSS3_LENGTH_UNITS` tuple (confirmed via direct source read) also
includes `ch`, `rem`, `vw`, `vh`, `vmin`, `vmax`, and `Q` — all of which docutils itself accepts as
valid `:width:`/`:height:` values but none of which map to a Typst-native unit. A fix that only
special-cases the units explicitly named in D-02 (px/pc/pt/cm/mm/in/em/%) plus `ex` and treats
anything else as an unconditional catch-all "unknown" is **already correct** by construction (the
regex-based approach in Pattern 2 falls through to the warn+drop branch for any unit not in the
explicit passthrough/convert set) — but the planner should **not** attempt to special-case `ex`
uniquely; it should be part of the same generic "else" branch as `ch`/`rem`/`vw`/etc., since D-02
gives no different treatment for `ex` versus these other rare units (they're all just "unknown").
**How to avoid:** Implement the unit dispatch as an explicit allow-list (`%`, `em`, `pt`, `cm`, `mm`,
`in` pass through; `px`/bare-unitless and `pc` convert; everything else warns+drops) rather than a
deny-list that tries to enumerate every CSS3 unit docutils might normalize.

## Code Examples

Verified patterns from the actual current source (all line numbers re-confirmed by direct `Read` in
this session):

### 1. Current fatal length emission (`visit_image`, to be replaced)
```python
# Source: typsphinx/translator.py:1527-1533 (current, buggy)
if "width" in node:
    width = node["width"]
    self.add_text(f", width: {width}")

if "height" in node:
    height = node["height"]
    self.add_text(f", height: {height}")
```

### 2. Current caption double-emission bug (traced, to be replaced)
```python
# Source: typsphinx/translator.py:1201-1227 (current, buggy)
def visit_caption(self, node: nodes.caption) -> None:
    if self.in_captioned_code_block:
        raise nodes.SkipNode
    self.in_caption = True  # NO buffer-swap -- children stream to live self.body

def depart_caption(self, node: nodes.caption) -> None:
    if self.in_figure:
        self.figure_caption = node.astext()  # re-derives text a SECOND time
    self.in_caption = False
```

### 3. Established "log + skip" precedent to model DEG-01/02 on (still current)
```python
# Source: typsphinx/translator.py:2483-2489
def visit_index(self, node: addnodes.index) -> None:
    """Index entries are skipped in Typst/PDF output as we don't generate indices."""
    raise nodes.SkipNode
```

### 4. Established buffer-swap precedent to model the caption fix on (still current)
```python
# Source: typsphinx/translator.py:190-212, 217-238 (visit_title/depart_title, admonition branch)
if isinstance(node.parent, nodes.Admonition):
    self._saved_body_for_admonition_title = self.body
    self.body = []
    self._in_admonition_title = True
    return
# ... (depart) ...
if self._in_admonition_title:
    self._pending_admonition_title = "".join(self.body)
    if self._saved_body_for_admonition_title is not None:
        self.body = self._saved_body_for_admonition_title
    self._saved_body_for_admonition_title = None
    self._in_admonition_title = False
    return
```

### 5. Existing empty-URL guard to extend with a `refid` fallback (still current)
```python
# Source: typsphinx/translator.py:1970-1996
refuri = node.get("refuri", "")

if not refuri:
    logger.warning(
        f"Reference node has empty URL. "
        f"Link will be rendered as plain text. "
        f"Check for broken references in source: {node.astext()}"
    )
    self._skip_link_wrapper = True
    return

prefix = "#" if self._in_markup_mode else ""

if refuri.startswith("#"):
    label = refuri[1:]
    self.add_text(f"{prefix}link(<{label}>, ")
else:
    self.add_text(f'{prefix}link("{refuri}", ')
```

### 6. Existing D-04 render-gate structure to extend (still current, full file read)
```python
# Source: tests/test_pdf_render_gate.py:36-40 (negative-control leak signatures)
LEAK_SIGNATURES = ("par({", 'text("', 'raw("')
```
```python
# Source: tests/test_pdf_render_gate.py:61-64 (skip guard -- typst-py + pypdf gated)
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the D-04 render gate",
)
class TestAdmonitionPdfRenderGate:
    ...
```
**Important, confirmed this session:** the existing test class has **no `@pytest.mark.slow`
decorator today**, despite `pyproject.toml`'s `markers` list registering `slow` (line 79–80 of
`pyproject.toml`: `"slow: marks tests as slow (deselect with '-m \"not slow\"')"`). No test file in
this repo currently uses `@pytest.mark.slow` anywhere (`grep` confirmed zero matches). D-04's
instruction to "keep the `slow` marker" therefore means: if the planner adds `@pytest.mark.slow` to
the *new* test classes in this phase, be aware it is a **newly-applied** marker in this codebase, not
literally already present on the existing class — and since `pytest.ini`/`pyproject.toml`'s
`addopts = "-v --strict-markers"` has no `-m "not slow"` filter anywhere in `tox.ini` or
`ci.yml`/`docs.yml`, marking a test `slow` **does not currently exclude it from any CI job** — it
would still run in `tox -e cov`'s plain `pytest --cov=...` invocation. This matches D-04's "runs in
CI's cov job ... effectively required" framing exactly: applying `@pytest.mark.slow` is a
documentation/intent signal for local dev speed (`pytest -m "not slow"`), not an actual CI gate.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `visit_image` emits `node["width"]`/`node["height"]` verbatim | `_convert_length_to_typst()` centralizes unit conversion | This phase (FIG-01) | Fixes the fatal `px`/`pc`/unitless compile error; any pre-existing rendered PDF with `:width: 200px` changes visual size slightly (200px → 150pt, not 200pt) — a documented, expected behavior change, not a regression |
| `visit_caption`/`depart_caption` uses `node.astext()`, no buffer-swap | Buffer-swap through the normal visitor chain (mirrors admonition-title fix) | This phase (FIG-02) | Fixes both the fatal juxtaposition AND the double-emission; also a strict correctness improvement — inline markup (`emph`/`strong`) inside a caption now renders instead of being silently discarded by `astext()` |
| `graphviz`/`inheritance_diagram` fall through to `unknown_visit` (log + continue descending) | Explicit `visit_graphviz`/`visit_inheritance_diagram` with visible placeholder + skip | This phase (DEG-01/02) | Prevents any incidental text-child leakage from these nodes and gives readers a visible signal instead of a silent gap |

**Deprecated/outdated:** None — this phase does not remove or deprecate any existing behavior beyond
the two bug fixes described above.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `sphinx.ext.graphviz` registers a node class literally named `graphviz` and `sphinx.ext.inheritance_diagram` registers `inheritance_diagram` (exact, case-sensitive class names needed for `visit_<ClassName>` dispatch) | Pattern 4 verify-note | If the actual class name differs (e.g. a different casing or a nested class name), the new `visit_graphviz`/`visit_inheritance_diagram` methods silently never fire and the nodes fall through to `unknown_visit` instead — the fatal-abort risk would NOT be fixed. **Mitigate:** dump a real doctree (`sphinx-build` a `.. graphviz::` fixture and inspect `doctree.pformat()`, or `grep` the Sphinx source directly for the node class definition) as the first step of implementation, before writing the fixture tests. |
| A2 | `rect()`'s `body` parameter accepts a `text(...)` content value positionally in code mode (no markup-block wrapping needed) | Pattern 4 code example | If Typst actually requires the body to be a markup content block (`[...]`) rather than a bare code-mode expression, the placeholder emission would need a small syntax adjustment (still zero new dependencies, just a different call shape) — low risk, easily caught by the render-gate compile step itself failing loudly |

**If this table is empty:** N/A — two items above need confirmation before the DEG-01/02
implementation is finalized; everything else in this document was directly verified against the
current repository source, the installed docutils 0.22.4 source, or live official Typst
documentation in this research session.

## Open Questions

1. **Should the `visit_reference` refid fallback (Pattern 3) be scoped narrowly to figures, or
   applied generally?**
   - What we know: `visit_reference` is a single shared method used by both plain-prose references
     and figure `:target:` references (confirmed by the Part-1-style trace: a figure's `:target:`
     wraps the image in exactly the same `reference` node type visited by the same method).
   - What's unclear: whether adding the `refid` fallback here should be considered "in scope" for
     Phase 11 (FIG-02, figures only) or whether it inadvertently also fixes some of Phase 12's
     XREF-01 corpus-wide empty-URL cases, since there is only one `visit_reference` method to edit.
   - Recommendation: implement the fix in `visit_reference` (there is nowhere else it can
     structurally go), scope the *fixture* to figure `:target:` cases only for Phase 11's
     acceptance criteria, and let Phase 12/15 measure the incidental broader impact rather than
     Phase 11 claiming credit for XREF-01's empirical reduction goal.

2. **Exact `sphinx.ext.graphviz`/`sphinx.ext.inheritance_diagram` node class names (A1 above).**
   - What we know: Sphinx bundles both extensions; the module names strongly suggest node class
     names `graphviz` and `inheritance_diagram` (standard Sphinx extension convention: the
     extension's primary node class is named after the extension).
   - What's unclear: not independently verified against the installed `sphinx` package's
     `ext/graphviz.py`/`ext/inheritance_diagram.py` source in this research pass.
   - Recommendation: first implementation step should be a throwaway doctree dump (a fixture with
     `.. graphviz:: digraph { a -> b }` and an autodoc `inheritance-diagram::` directive, built with
     `sphinx-build -b typst` against the *current* unmodified translator, then inspect
     `sphinx-build`'s `unknown node type: ...` warning output — `unknown_visit` at line 2049 already
     logs `f"unknown node type: {node}"`, which will print the exact node's repr/class name for free
     without needing a separate doctree-dump script).

3. **`rect()`/`box()` exact Typst 0.15 call syntax for a bordered placeholder (A2 above).**
   - What we know: official Typst docs confirm `rect()` accepts `stroke`, `radius`, `inset`, and a
     `body` content parameter (https://typst.app/docs/reference/visualize/rect/); `box()` has an
     equivalent `stroke`/`inset` shape (https://typst.app/docs/reference/layout/box/) — both are
     Typst 0.15 stdlib, no `@preview` import needed.
   - What's unclear: whether the positional-content-argument-in-code-mode call shape shown in
     Pattern 4's example compiles as-is on the first try, or needs a small adjustment (e.g. an
     explicit `body:` keyword).
   - Recommendation: the render-gate fixture (GATE-01/D-04 extension) will surface any syntax
     mismatch immediately via a loud `TypstCompilationError` — treat the first real compile of the
     DEG-01/02 fixture as the actual verification step, not a manual read of Typst docs alone.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst` (typst-py) | Real-compile gate (GATE-01), `typstpdf` builder | ✓ (core runtime dep) | `>=0.15.0,<0.16` [VERIFIED: pyproject.toml] | none needed — it's a hard project dependency, not optional |
| `pypdf` | Text-extraction half of the render gate | ✓ (dev extra) | `>=6.14,<7` [VERIFIED: pyproject.toml] | none needed — installed whenever `--extra dev` is synced, which every CI job does |
| `sphinx.ext.graphviz` / `sphinx.ext.inheritance_diagram` | DEG-01/DEG-02 fixtures | ✓ (bundled with `sphinx>=9.1,<10`, already a core dependency) | matches installed `sphinx` version | none needed |
| Graphviz `dot` CLI binary | NOT required — this phase renders a placeholder, never invokes `dot` | N/A | N/A | N/A (explicitly out of scope; real rendering deferred) |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** none — every dependency this phase touches is already a
hard project dependency (`typst`, `sphinx`) or a `dev` extra (`pypdf`) installed by every existing
CI job (`uv sync --extra dev --locked`, confirmed in `.github/workflows/ci.yml`'s `test`/`coverage`
jobs). **Practical implication for GATE-01:** the render gate's `@pytest.mark.skipif(not
(TYPST_AVAILABLE and PYPDF_AVAILABLE), ...)` guard will never actually trigger in any of this
project's CI jobs (`test` matrix across 3 OSes × 2 Python versions, plus the dedicated `coverage`
job) — it only matters for a contributor's local environment that skipped installing `dev` extras.
This directly confirms D-04's "effectively required in CI" framing with a verified source, not an
assumption.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (via `pytest>=8.4,<10`) [VERIFIED: pyproject.toml] |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (markers registered incl. `slow`; `addopts = "-v --strict-markers"`) |
| Quick run command | `pytest tests/test_pdf_render_gate.py -v` |
| Full suite command | `pytest --cov=typsphinx --cov-report=term-missing tests/` (matches `tox -e cov`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FIG-01 | `:width:`/`:height:` fixtures (`200px`, `50%`, `3em`, bare unitless, `2in`, one unknown-unit warn+drop) compile to a real PDF with no `TypstCompilationError` | integration (real-compile) | `pytest tests/test_pdf_render_gate.py::TestFigureLengthRenderGate -v` | ❌ Wave 0 — new fixture + test class |
| FIG-01 | `_convert_length_to_typst()` unit conversions (px→pt ratio, pc→pt, pass-through set) | unit | `pytest tests/test_translator.py -k convert_length -v` | ❌ Wave 0 — new unit test file/class, supplements (not replaces) the render-gate test |
| FIG-02 | `:target:`-linked figure/image with caption containing `_ * `` ` `` [ ]` compiles; caption text present exactly once in extracted PDF text; no `text("` leak adjacent to `image(`/`link(` | integration (real-compile) | `pytest tests/test_pdf_render_gate.py::TestFigureCaptionRenderGate -v` | ❌ Wave 0 — new fixture + test class |
| FIG-02 | Internal `refid`-based `:target:` (not just external `refuri`) compiles | integration (real-compile), same fixture project as above (two figures) | (same command as above) | ❌ Wave 0 |
| DEG-01/02 | `.. graphviz::` and `inheritance_diagram` node each emit exactly one `logger.warning` and compile without abort; extracted PDF text contains the placeholder wording, never raw DOT/diagram source | integration (real-compile + caplog) | `pytest tests/test_pdf_render_gate.py::TestGraphvizDegradeRenderGate -v` | ❌ Wave 0 — new fixture + test class |
| GATE-01 | The extended `tests/test_pdf_render_gate.py` runs (not skips) in the `cov` CI job and fails loudly on any `TypstCompilationError` | integration, standing CI gate | `tox -e cov` (already wired to CI's `coverage` job) | ✓ existing job, no changes needed to `tox.ini`/`ci.yml` |

### Sampling Rate
- **Per task commit:** `pytest tests/test_pdf_render_gate.py -v` (targeted, all new + existing
  render-gate classes) plus `pytest tests/test_translator.py -k "caption or image or length" -v`
  (fast unit-level regression for the touched methods).
- **Per wave merge:** `pytest --cov=typsphinx --cov-report=term-missing tests/` (full suite, matches
  `tox -e cov`).
- **Phase gate:** Full suite green (including the render gate, which is unconditionally exercised in
  this repo's dev/CI environment per the Environment Availability findings above) before
  `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/fixtures/figure_length_render_gate/` — new Sphinx fixture project with `:width:`/
      `:height:` cases (`200px`, `50%` on width only — height rejects `%` per docutils, `3em`, bare
      unitless, `2in`, one unknown unit e.g. `1ex` or `1ch`) — covers FIG-01
- [ ] `tests/fixtures/figure_target_caption_render_gate/` — new Sphinx fixture project with an
      external-URL `:target:` figure and an internal-label `:target:` figure, both with a caption
      containing `_ * `` ` `` [ ]` — covers FIG-02
- [ ] `tests/fixtures/graphviz_degrade_render_gate/` — new Sphinx fixture project with a
      `.. graphviz::` directive and an `.. inheritance-diagram::` directive (needs
      `sphinx.ext.graphviz`/`sphinx.ext.inheritance_diagram` added to the fixture's `conf.py`
      `extensions` list) — covers DEG-01/DEG-02
- [ ] New test classes in `tests/test_pdf_render_gate.py` (or a `slow`-marked sibling module,
      planner's discretion per D-04) driving the three fixtures above through
      `sphinx-build → typst.compile() → pypdf`, reusing the existing `LEAK_SIGNATURES` constant and
      adding phase-specific negative controls (e.g. `"width: 200px"`/unconverted-unit substrings in
      the raw `.typ`, or raw `digraph`/DOT-source tokens in the extracted PDF text)
- [ ] Fast unit-level tests for `_convert_length_to_typst()` in `tests/test_translator.py` (or a new
      `tests/test_translator_length.py`) as a supplement to, never instead of, the render-gate
      fixture — per Pitfall 9

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | no | N/A — this is a document-compiler library, no auth surface |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes | `_convert_length_to_typst()` must validate the numeric/unit shape via the fixed regex (Pattern 2) and degrade safely (warn + drop) on anything unrecognized, rather than trusting docutils' normalized string blindly — this IS the phase's core V5 concern |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Untrusted/malformed `:width:`/`:height:` values reaching the Typst compiler unfiltered (a malicious or malformed `.rst` source authored by an untrusted contributor could theoretically probe for compiler crashes via crafted length strings) | Tampering / Denial of Service (compile abort) | `_convert_length_to_typst()`'s explicit allow-list + regex validation (Pattern 2) already rejects anything outside the expected shape by falling through to the warn+drop branch — never interpolates an unrecognized value into the Typst source verbatim |
| Caption/title text containing Typst markup-special characters (`_`, `*`, `` ` ``, `[`, `]`, `#`) reaching a markup `[...]` content block unescaped — an injection-class bug (any author's prose, or a malicious contributor's, could alter document layout/behavior) | Tampering | The buffer-swap fix (Pattern 1) routes captions through `visit_Text`'s existing string-literal escaping instead of `node.astext()`, which already neutralizes this class of injection for the caption path specifically — this is the phase's most direct instance of an injection-class fix, already noted in PITFALLS.md Security Mistakes section |
| Raw DOT source / class-hierarchy spec content leaking into the compiled PDF from `graphviz`/`inheritance_diagram` nodes (an information-disclosure-adjacent concern if the DOT source contains anything sensitive an author didn't intend to publish as visible text) | Information Disclosure | DEG-01/02's `raise nodes.SkipNode` (Pattern 4) ensures the node's children (which may carry the raw DOT text as an attribute or child) are never visited/emitted at all — the placeholder text is a fixed, static string, never derived from the node's actual content |

## Sources

### Primary (HIGH confidence)
- `typsphinx/translator.py` — direct read in this session, ~2793 lines. Line numbers re-confirmed
  (not carried forward from CONTEXT.md blind): `visit_figure`/`depart_figure` 1163–1199,
  `visit_caption`/`depart_caption` 1201–1227, `visit_image`/`depart_image` 1501–1546,
  `visit_target` 1548–1603, `visit_pending_xref` 1605–1636, `_compute_relative_image_path`
  1748–1775+, `visit_reference`/`depart_reference` 1930–2036, `unknown_visit`/`unknown_departure`
  2038–2059, `_visit_admonition`/`_depart_admonition` 2292–2345 + callers 2351–2454, `visit_index`
  2483–2493, `visit_desc_*` family 2495–2621, `visit_title`/`depart_title` 190–238, `visit_Text`
  443–499, `__init__` state vars 27–100+.
- `tests/test_pdf_render_gate.py` — direct read in full (134 lines), this session — confirmed
  `LEAK_SIGNATURES`, the `skipif` guard, and (critically) the **absence** of any `@pytest.mark.slow`
  decorator anywhere in the current test suite.
- `tests/fixtures/admonition_render_gate/{conf.py,index.rst}` — direct read, this session — the
  fixture-project shape (minimal `conf.py` with `typst_documents`, a single `index.rst`) to model new
  fixtures on.
- Installed docutils 0.22.4 source (project's own `.tox/py312` virtualenv) — direct read, this
  session: `docutils/parsers/rst/directives/__init__.py` (`CSS3_LENGTH_UNITS`, `get_measure`,
  `length_or_unitless`, `length_or_percentage_or_unitless`), `docutils/parsers/rst/directives/
  images.py` (`option_spec` for width/height/target, `:target:` refname/refuri resolution),
  `docutils/nodes.py` (`parse_measure`, confirmed "Provisional" API status).
- `pyproject.toml` — direct read, this session: `dependencies` (`typst>=0.15.0,<0.16`,
  `docutils>=0.21,<0.23`, `sphinx>=9.1,<10`), `dev` extras (`pypdf>=6.14,<7`), `[tool.pytest.
  ini_options]` markers list (`slow`), `requires-python = ">=3.12"`.
- `tox.ini` — direct read, this session: `env_list = py312, py313, lint, type, cov, docs` (confirms
  no py310/py311 environments despite CLAUDE.md's stale claim), `[testenv:cov]` command.
- `.github/workflows/ci.yml`, `.github/workflows/docs.yml` — direct read, this session: confirmed
  the `test` matrix (3 OS × 2 Python versions) and `coverage` job both run `uv sync --extra dev
  --locked` before `pytest`/`tox -e cov`, meaning `typst`+`pypdf` are present in every CI job that
  runs the test suite; confirmed `docs.yml`'s `tox -e docs-pdf` real-compiles a full Sphinx doc tree
  (separate from, and not a substitute for, the unit/integration test suite).
- `.planning/research/PITFALLS.md`, `.planning/research/ARCHITECTURE.md`, `.planning/research/
  SUMMARY.md` — milestone-level research, read in full this session; all 10 pitfalls and the Part
  1–5 architecture trace were cross-checked against the live source in this session and found
  accurate (all cited line numbers matched exactly).
- [typst.app/docs/reference/visualize/rect/](https://typst.app/docs/reference/visualize/rect/) —
  fetched live this session via WebSearch, confirms `rect()`'s `stroke`/`radius`/content-body
  parameters.
- [typst.app/docs/reference/layout/box/](https://typst.app/docs/reference/layout/box/) — fetched
  live this session via WebSearch, confirms `box()`'s `stroke`/`inset` parameters.

### Secondary (MEDIUM confidence)
- Exact `sphinx.ext.graphviz`/`sphinx.ext.inheritance_diagram` node class names (Assumption A1) —
  reasoned from standard Sphinx extension naming convention, not independently verified against the
  installed `sphinx` package's extension module source in this research pass.

### Tertiary (LOW confidence — flagged for verification before implementation)
- None beyond the two items in the Assumptions Log above (A1, A2) — both have concrete, cheap
  verification paths already identified (a throwaway doctree dump / `unknown_visit`'s own warning
  log; the render-gate's own loud compile failure).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies confirmed by direct `pyproject.toml` read; no
  version ambiguity.
- Architecture: HIGH — every pattern traced against live, re-confirmed source line numbers in this
  session (not inherited blind from CONTEXT.md or milestone-level ARCHITECTURE.md).
- Pitfalls: HIGH — all carried-forward pitfalls independently re-verified against current code in
  this session; one new pitfall (docutils' extended CSS3 unit set) found and documented.
- Graphviz/inheritance_diagram exact node class names: MEDIUM — flagged explicitly (Assumption A1),
  cheap to verify at implementation start via `unknown_visit`'s own warning output.

**Research date:** 2026-07-12
**Valid until:** 30 days (stable single-file fix; re-verify sooner only if `typst`, `docutils`, or
`sphinx` pins change in `pyproject.toml` before this phase is planned/executed).

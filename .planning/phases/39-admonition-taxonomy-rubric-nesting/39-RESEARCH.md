# Phase 39: Admonition Taxonomy + Rubric Nesting - Research

**Researched:** 2026-08-02
**Domain:** docutils→Typst node-handler taxonomy remapping (gentle-clues bucket routing), a
save/restore attribute-slot bug in a shared translator idiom, and a Pillow-based visual-UAT
artifact pipeline.
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Every value cited below was measured **this session (2026-08-02)** by four means, none from recall:
reading `sphinx.sty` (Sphinx 9.1.0) for the authoritative bucket taxonomy and its RGB palette;
reading the pinned gentle-clues 1.3.1 sources in the Typst package cache; real `sphinx-build -b
typst`/`-b typstpdf` runs over hand-written probe projects with left edges read back through
`pypdf`'s `visitor_text`; and a real `sphinx-build` with `language = "ja"` printing
`sphinx.locale.admonitionlabels` from an `env-before-read-docs` hook.

**The bucket taxonomy (ADM-01, ADM-02):**
- **D-01: a bucket is a gentle-clues function; its colour is that function's default.** No
  `accent-color:` is ever passed. Measured defaults: `info` `#04a5e5`, `tip` `#179299`, `warning`
  `#df8e1d`, `error` `#d20f39`.
- **D-02: the success bucket is `tip` (teal `#179299`), not `success` (green `#40a02b`).** `hint`
  and `tip` already emit `tip(…)`; ADM-01 is discharged by moving `seealso` into it.
- **D-03: `danger` folds into `error` too.** Collapsing `attention`, `danger` and `error` onto
  `error(…)` makes the red bucket a single function.

Resulting bucket table: note→`info` (`note`); success→`tip` (`hint`, `tip`, `seealso`);
warning→`warning` (`warning`, `caution`, `important`); error→`error` (`attention`, `danger`,
`error`); outside the four: `task` (`todo_node`, unchanged), `notify` (generic `.. admonition::`,
D-07 below), `abstract` (`.. topic::`, D-08 below).

**Admonition titles:**
- **D-04: titles come from `sphinx.locale.admonitionlabels`, passed as `custom_title`.** Measured
  live with `language = "ja"`: `{'attention': '注意', 'caution': '注意', 'danger': '危険', 'error':
  'エラー', 'hint': 'ヒント', 'note': '注釈', 'seealso': '参考', 'tip': 'Tip', 'warning': '警告',
  'important': '重要'}`.
- **D-05: apply it to all ten types, not only the ones whose folded default drifts.** Two measured
  costs the planner must accept, not treat as bugs: (a) in `ja`, `.. tip::` regresses from
  gentle-clues' 「ヒント」 to the catalog's untranslated "Tip", and `.. note::` moves from 「情報」
  to 「注釈」; (b) `seealso`'s literal changes from `"See Also"` to the catalog's `"See also"`.
  Migration covers `tests/test_admonitions.py` (18 clue-call assertions), `tests/test_topics.py`
  (3) and `tests/test_pdf_render_gate.py` (4) in full.

`todo_node` is not in `admonitionlabels` and already receives its real title from the node's own
`title` child; the static `custom_title="Todo"` is an inert fallback — leave that path alone.

**Greyscale distinguishability (ADM-04, the milestone's only `[V]`):** the four bands span 5.4
percentage points of luminance (reproducing the defect); the left stroke (2pt, accent at full
saturation) spans 35.9 points; the four icons differ by shape.
- **D-06: no styling change is made for ADM-04.** The claim to prove is that icon shapes plus the
  existing 2pt accent stroke already carry the distinction. Rejected alternatives (available if
  UAT rejects): per-bucket `stroke-width:`/`header-color:`. No dashed-stroke lever exists.
- **D-07: the greyscale render is produced with Pillow, added to `pyproject.toml`'s `[dev]`
  extra.** `typst.compile(input, format="png", ppi=…)` rasterises; `Image.open(…).convert("L")`
  desaturates. PIL, numpy, ImageMagick, ghostscript, `pdftoppm` and `mutool` are all absent from
  this environment. The render and the owner's sign-off are committed as phase artifacts.
- **D-08: no fallback lever is pre-agreed.** If the owner cannot distinguish the four kinds, the
  lever is chosen then, against the actual render.

**Generic `.. admonition::` and `.. topic::` (ADM-03):** both route through
`_visit_admonition(node, "clue")` today; the title is already emitted — the gap is styling.
- **D-09: the generic `.. admonition::` emits `notify(…)`** — accent `#1e66f5`. Rejected: `memo`
  (too close to error bucket), `abstract` (reserved for topic), `idea` (identical to warning
  bucket).
- **D-10: `.. topic::` emits `abstract(…)`** — accent `#209fb5`. Consequence: `_visit_admonition`'s
  callers split into two, and the base `clue` function disappears from the codebase entirely (the
  box-less `.. contents::` path is untouched).

**Rubric (ADM-05 / SC#3):** **Measured: ADM-05 already holds** — a real `-b typstpdf` build of a
`py:class::` containing a `py:method::`, each carrying a `.. rubric::`, showed the rubric's left
edge exactly matches its containing `desc_content` body's edge, at both nesting levels.
- **D-11: the phase asserts ADM-05 and additionally folds the two known rubric defects** (the
  double-blank-line wart and the `par()`-drop bug below). Assertion-only was rejected.
- **D-12: SC#3's indentation claim becomes an invariance guard, and ROADMAP.md SC#3 is corrected
  to say so.** A RED cannot be recorded against pre-phase code because the property already holds
  — the same resolution as Phase 36's SC#3.
- **D-13: the RED fixture for the rubric half is the `par()` drop.** Measured: `.. rubric:: A
  **bold** rubric` emits `strong({text("A ") strong({text("bold")}) text(" rubric")})`, after which
  every subsequent paragraph emits a bare `text("…")` instead of `par({text("…")})`. Assert
  `par({text("First paragraph after the rubric.")})` — red today, green after the fix.

**Test migration (SC#5):**
- **D-14: the blast-radius census recorded at discussion time is the starting point, and must be
  re-taken at planning time rather than trusted.** Measured 2026-08-02: `tests/test_admonitions.py`
  (18 clue calls), `tests/test_topics.py` (3), `tests/test_pdf_render_gate.py` (4); rubric is
  referenced by `tests/test_desc_rubric_decoupling_render_gate.py`,
  `tests/test_rubric_option_concat_render_gate.py`,
  `tests/test_rubric_propagated_target_render_gate.py`,
  `tests/test_signature_typography_multi_signature_page_count_gate.py`, `tests/test_translator.py`
  and five fixtures under `tests/fixtures/`. Expected strings are re-derived by hand, never by
  copying failing output.

### Claude's Discretion

- How the `admonitionlabels` lookup is threaded into `_visit_admonition` (a module-level mapping
  from node class name to catalog key, versus a `custom_title` at each call site) — an
  implementation shape, not a decision.
- Escaping of the title inside the emitted Typst string literal now that titles can be non-ASCII.
- Which real API page SC#3's autodoc "Options" measurement is taken from.
- The greyscale render's PPI, page selection and file naming.

### Deferred Ideas (OUT OF SCOPE)

- **`.. tip::`'s Japanese title.** D-05 accepts a measured regression: Sphinx's `ja` catalog leaves
  `tip` untranslated ("Tip") where gentle-clues has 「ヒント」. A translation-quality question, not
  a taxonomy one.
- **A neutral grey bucket.** gentle-clues has no grey clue; matching Sphinx's neutral grey band
  would need an explicit colour literal that D-01 rules out. Revisit only if the "no colour
  literals" rule is ever relaxed.
- **TOP-01** (boxing the `.. contents::` local TOC) — already deferred at v0.7.0 scoping; the
  box-less path stands.
- Citations — Phase 40. User-overridable styling — dropped from v0.7.0 at scoping.
- `SHARED_INDENT_STEP` and the `pad(left: …)` wrapper — Phase 38 owns this; the rubric consumes it,
  does not re-define it.
- `block_quote` — Phase 38 D-04 recorded it as an intentional non-consumer of the indent.
- `desc_signature` and its inline children — Phase 37 owns them and is complete; a rubric fix must
  not change `desc_signature`'s emitted bytes.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|--------------|---------------------|
| ADM-01 | `seealso` renders in the same bucket as `hint`/`tip` (green "success"), not the blue "note" bucket it uses today | Bucket Routing Table (D-02); GATE-01 RED Design row ADM-01 — new fixture required, none exists today |
| ADM-02 | `attention` renders in the same bucket as `danger`/`error` (red), not the orange "warning" bucket it uses today | Bucket Routing Table (D-03); GATE-01 RED Design row ADM-02 — shares the new ADM-01 fixture |
| ADM-03 | A generic `.. admonition::` renders as a styled box carrying its own custom title, not the unstyled base `clue` it produces today | Bucket Routing Table (D-09); GATE-01 RED Design row ADM-03 — extend existing `topic_line_block_render_gate`-backed test with a `.typ`-string assertion |
| ADM-04 | Admonition types stay distinguishable in greyscale — carried by icon and border, not hue alone | Pitfall 5 (BT.601 vs BT.709 formula), Code Examples (Pillow render pipeline), Validation Architecture (manual-only `[V]`, no mechanical test possible) |
| ADM-05 | A `rubric` nested inside a description body indents with that body rather than sitting flush to the page margin | Architecture Patterns "Rubric Indent Inheritance" (D-12 invariance guard, mechanism already verified via `pad(left: SHARED_INDENT_STEP` at translator.py:5255/5569); Pitfall 1/GATE-01 table for the D-11/D-13 defects folded alongside it |
</phase_requirements>

## Summary

39-CONTEXT.md already measured and locked every factual value this phase needs — the four-bucket
taxonomy, every gentle-clues colour/luminance figure, the `sphinx.locale.admonitionlabels` catalog
contents, the pypdf x-position proof that ADM-05 already holds, and an initial test-blast-radius
census. This research does not re-derive any of that. It verifies those claims directly against
the current `typsphinx/translator.py` and the installed toolchain (all confirmed to match
CONTEXT.md exactly), and then builds the layer CONTEXT.md deliberately left to planning: how each
requirement gets validated mechanically, what the concrete GATE-01 RED fixtures/assertions are,
which fix shape resolves the D-11/D-13 attribute-slot collision without touching
`desc_signature`'s emitted bytes, a precise re-take of the blast-radius census (with a materially
narrower list of assertions that actually need editing than the raw "18/3/4" counts suggest), and
a verified, minimal Pillow greyscale-render pipeline for ADM-04's UAT artifact.

Three findings go beyond what CONTEXT.md recorded and materially affect planning:

1. **`tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` (Phase 36's SC#2
   byte-identity gate) will legitimately change** if the double-blank-line wart (D-11) is fixed —
   its fixture contains exactly the "rubric with a propagated target inside a list item" shape the
   wart describes. This is not a regression to avoid; it is an expected, deliberate byte change
   this phase must re-derive and re-commit.
2. **No existing real-compile fixture contains `seealso`, `attention`, or `danger`.** The only
   fixture with any admonition content (`topic_line_block_render_gate`) has `note`/`warning`/a
   generic `.. admonition::` only. ADM-01/ADM-02's compiled-PDF half of their success criteria has
   no fixture to attach to today — a new or extended fixture is required, not optional.
3. **Pillow's actual `Image.convert("L")` desaturation uses the ITU-R BT.601 luma weights
   (0.299/0.587/0.114), not the BT.709/sRGB relative-luminance weights
   (0.2126/0.7152/0.0722) 39-CONTEXT.md's D-06 table used for its analytical prediction.** The
   owner's UAT sign-off must be made against the real Pillow-rendered artifact, not against the
   D-06 table's numbers — the two formulas are close but not identical, so the rendered greys will
   not exactly match the predicted luminances.

**Primary recommendation:** Implement D-01..D-05's bucket/title routing as table-driven changes to
the 13 call sites in `_visit_admonition`'s callers (a concrete before/after table is below); fix
D-11/D-13 by giving `visit_rubric`/`depart_rubric` their *own* uniquely-named save/restore
attributes (breaking the `_strong_was_*` collision) rather than converting the shared slots into a
stack or touching `visit_strong`/`visit_desc_signature`; build one new small local fixture for the
ADM-01/ADM-02 compiled-PDF RED (no existing fixture covers those three types); and treat SC#3 as an
invariance guard per D-12, re-derived from a small local `py:class::`/`py:method::`+rubric probe
rather than the network-dependent Sphinx corpus.

## Architectural Responsibility Map

Single-tier project (a Sphinx builder — Python translator producing Typst source, no browser/
server split), so this map records translator-internal responsibility instead of client/server
tiers.

| Capability | Primary Owner | Secondary Owner | Rationale |
|------------|---------------|------------------|-----------|
| Bucket → gentle-clues function routing (ADM-01/ADM-02) | `_visit_admonition` call sites (13 `visit_X` methods, `typsphinx/translator.py:4401-4551`) | — | Each admonition type's handler already funnels through one shared emission helper; only the `clue_type` argument at the call site changes |
| Admonition title source (D-04/D-05) | `_visit_admonition`/`_depart_admonition` (`4337-4399`) | `sphinx.locale.admonitionlabels` (external, read-only) | The helper already has a `custom_title` parameter; only its value source changes, not its plumbing |
| Generic admonition/topic styling (ADM-03) | `visit_admonition`/`visit_topic` (`4522-4559`) | — | Two of the 13 callers change their `clue_type` argument from the now-removed base `clue` to `notify`/`abstract` |
| Rubric indent inheritance (ADM-05) | Phase 38's `pad(left: SHARED_INDENT_STEP, {...})` around `desc_content` (`5255`, `5569`) — **already shipped, out of scope this phase** | `visit_rubric` (consumes, does not define) | D-12: this is an invariance guard, not new code |
| Rubric's own emission correctness (D-11/D-13) | `visit_rubric`/`depart_rubric` (`5767-5889`) | `visit_strong`/`depart_strong` (`1429-1501`, read-only dependency via shared attribute names) | The bug is a slot collision between two *different* handlers' state, not a logic error in either handler alone |
| Greyscale render artifact (ADM-04) | New test/tooling code (Pillow + `typst.compile(format="png")`) | `pyproject.toml` `[dev]` extra | Build-time verification tooling, not translator/runtime code |

## Standard Stack

No new runtime dependency (milestone invariant #1). No new `@preview` package (milestone invariant
#2) — the four already-imported gentle-clues functions this phase touches (`info`, `tip`,
`warning`, `error`) plus the three newly-*used*-but-already-imported ones (`notify`, `abstract`,
`task`) are all covered by the existing wildcard import
`#import "@preview/gentle-clues:1.3.1": *` (writer.py/template_engine.py/templates/base.typ,
unchanged this phase).

### Core (unchanged this phase)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `gentle-clues` | 1.3.1 (pinned, `@preview`) | Admonition box rendering | Already the project's sole admonition-box primitive; this phase only changes *which* of its 18 predefined functions each Sphinx type routes to |
| `typst` (typst-py) | 0.15.0 (installed, matches `pyproject.toml`'s `>=0.15.0,<0.16` pin) [VERIFIED: `.venv/lib/python3.13/site-packages/typst`, `importlib.metadata.version("typst")`] | Compile `.typ` → PDF/PNG | `typst.compile(input, output=None, ..., format=None, ppi=None, ...)` confirmed to accept `format="png", ppi=<float>` in this exact installed version — this IS the mechanism D-07 requires, verified directly against the venv, not assumed from the package's docs |

### New dev-only dependency
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pillow` | Latest on PyPI at research time: **12.3.0** [VERIFIED: `https://pypi.org/pypi/pillow/json` `info.version`, fetched directly this session] — pin loosely (e.g. `pillow>=11,<13`) consistent with the project's other `[dev]` bounds, exact floor is Claude's Discretion per CONTEXT.md | Desaturate the ADM-04 render (`Image.open(...).convert("L")`) | Dev-only, added to `pyproject.toml`'s `[project.optional-dependencies] dev` array (D-07). Confirmed absent from both the bare-system Python and this repo's `.venv` before this phase — a real new install, not already transitively present |

**Version verification performed:** `.venv/bin/python -c "import importlib.metadata as m; print(m.version('typst'))"` → `0.15.0`; PyPI JSON API fetched directly for `pillow` → `12.3.0`. Neither package needed a training-data guess — both confirmed against the installed venv / live registry.

**Installation:**
```bash
# pyproject.toml [project.optional-dependencies] dev += "pillow>=11,<13" (or the planner's chosen floor)
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
```

### Alternatives Considered (already rejected by D-07, recorded for planner awareness)
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pillow | numpy + hand-rolled PNG decode | Confirmed absent from the environment too; zero-dependency path requires hand-rolling a PNG codec — rejected as verification cost with no product value (D-07) |
| Pillow | System tool (`pdftoppm`, `mutool`, ImageMagick `convert`, ghostscript) | All confirmed absent from `PATH` in this environment (re-verified this session, matches D-07's measurement) — no external-binary path exists |
| Pillow | Desaturate inside Typst itself | Measurably impossible — gentle-clues' icons are baked-fill SVGs; `accent-color` does not reach them (D-06) |

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|--------------|---------|-------------|
| `pillow` | PyPI | Latest release 2026-07-01; project itself is the long-established PIL/Pillow lineage | Unavailable to the legitimacy checker for PyPI (`weeklyDownloads: null`) | `https://github.com/python-pillow/Pillow` | **SUS** | Flagged by protocol — see note below |

**Note on the SUS verdict:** the checker's *only* negative signal is `unknown-downloads` — PyPI
download-count telemetry isn't wired into the checker the way npm's is, so `weeklyDownloads: null`
alone trips the SUS threshold regardless of the package's actual standing. The other three signals
(`exists: true`, a long-lived canonical GitHub org/repo, `deprecated: false`) are all clean, and
`pillow` is one of the Python ecosystem's most widely depended-on imaging libraries. **This does
not override the gate protocol**: per the Package Legitimacy Gate, a SUS verdict must still be kept
with an inline warning and the planner must insert a `checkpoint:human-verify` task before the
`pyproject.toml` edit that adds it lands, even though the underlying cause here is a checker
coverage gap rather than a real legitimacy concern.

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** `pillow` — planner must add a `checkpoint:human-verify`
task immediately before (or as part of) the `pyproject.toml` dev-extra edit.

## Architecture Patterns

### Admonition Emission Pipeline (current, unchanged by this phase)

```
docutils node (nodes.note / nodes.warning / addnodes.seealso / ... / nodes.admonition / nodes.topic)
        │
        ▼
visit_X(node)  ──────────────►  _visit_admonition(node, clue_type, custom_title=None)
        │                              │
        │                              ├─ emits id anchors (_emit_id_anchors)
        │                              ├─ resets _pending_admonition_title / stashes custom_title
        │                              └─ opens  "{clue_type}({"
        ▼
[node's title child, if any, buffered via visit_title's                (dynamic title path —
 admonition-aware branch into _pending_admonition_title]                 ALWAYS wins if present)
        │
        ▼
[node's body children stream normally — par({...}), text(...), raw(...), nested lists/code]
        │
        ▼
depart_X(node)  ─────────────►  _depart_admonition()
                                       │
                                       ├─ closes body "}"
                                       ├─ title_expr = pending (dynamic) OR custom_title (static)
                                       ├─ emits ", title: {expr}" if either present
                                       └─ closes  ")\n\n"
```

**What this phase changes:** only the `clue_type` and `custom_title` ARGUMENTS at each of the 13
`visit_X` call sites (table below). The helper itself, the title buffer-swap, and the id-anchor
emission are untouched — this is a data change, not a control-flow change.

### Bucket Routing Table — implementation-ready (D-01..D-05, D-09, D-10)

| Type | Node class | `clue_type` today | `clue_type` after this phase | `custom_title` today | `custom_title` after this phase |
|------|-----------|-------------------|-------------------------------|------------------------|-----------------------------------|
| note | `nodes.note` | `info` | `info` (unchanged) | none | catalog `"Note"` |
| warning | `nodes.warning` | `warning` | `warning` (unchanged) | none | catalog `"Warning"` |
| tip | `nodes.tip` | `tip` | `tip` (unchanged) | none | catalog `"Tip"` |
| important | `nodes.important` | `warning` | `warning` (unchanged) | static `"Important"` | catalog `"Important"` (same string, different source) |
| caution | `nodes.caution` | `warning` | `warning` (unchanged) | none | catalog `"Caution"` |
| **seealso** | `addnodes.seealso` | `info` | **`tip`** (D-02) | static `"See Also"` | catalog **`"See also"`** (D-05, lowercase "a") |
| hint | `nodes.hint` | `tip` | `tip` (unchanged) | none | catalog `"Hint"` |
| todo_node | n/a (`sphinx.ext.todo`) | `task` | `task` (unchanged) | static `"Todo"` (inert fallback) | **unchanged** — `todo_node` is not an `admonitionlabels` key; leave this path alone per CONTEXT.md |
| error | `nodes.error` | `error` | `error` (unchanged) | none | catalog `"Error"` |
| **danger** | `nodes.danger` | `danger` | **`error`** (D-03) | none | catalog `"Danger"` |
| **attention** | `nodes.attention` | `warning` | **`error`** (D-03) | none | catalog `"Attention"` |
| **admonition** (generic) | `nodes.admonition` | `clue` | **`notify`** (D-09) | none | none — dynamic (node-supplied) title always wins here |
| **topic** (non-`contents`) | `nodes.topic` | `clue` | **`abstract`** (D-10) | none | none — dynamic title always wins |

**Verified fact that simplifies D-04/D-05's implementation (Claude's Discretion item 1 in
CONTEXT.md):** every one of the ten `admonitionlabels` keys is byte-identical to its docutils node
class's `__name__` (`note`→`note`, `warning`→`warning`, … `addnodes.seealso.__name__`→`seealso`).
[VERIFIED: `sphinx.locale.admonitionlabels` read directly via `.venv/bin/python`, session 2026-08-02]

```python
from sphinx.locale import admonitionlabels

# In _visit_admonition, centralize the lookup instead of threading a static
# string through all 13 call sites individually:
def _visit_admonition(self, node, clue_type, custom_title=None):
    ...
    default_title = admonitionlabels.get(node.__class__.__name__)
    if default_title is not None:
        custom_title = str(default_title)  # force the lazy i18n proxy to str
    self._custom_admonition_title = custom_title
```

This ONE change at the shared helper (rather than 10 individual edits) correctly:
- Applies the catalog title to all 10 real admonition types, with zero special-casing.
- Leaves `todo_node` untouched (`"todo_node"` is not a dict key, so `.get()` returns `None` and the
  caller's own `custom_title="Todo"` argument survives unchanged).
- Leaves `admonition`/`topic` untouched (`"admonition"`/`"topic"` are not dict keys either — no
  static title is ever injected on these two, matching D-09/D-10's "its default title never
  surfaces" reasoning).
- Lets every existing `custom_title=` argument at the 13 call sites become dead code that can be
  deleted (`visit_important`'s `custom_title="Important"`, `visit_seealso`'s
  `custom_title="See Also"` — the catalog now supplies both, and for `seealso` supplies the
  DIFFERENT, correct casing).

**`str(default_title)` is load-bearing, not defensive filler**: `admonitionlabels` values are
Sphinx `_LazyString` i18n proxies (confirmed via direct read — `pprint.pprint` on the dict showed
`i'Attention'`-style reprs), not plain `str` instances. An f-string interpolation like
`f'"{value}"'` calls `str()`/`__format__` implicitly and works correctly either way, but assigning
the *proxy itself* to `self._custom_admonition_title` and later doing string operations on it
(escaping — see Pitfall 3 below) requires an explicit `str()` coercion first.

### Rubric Indent Inheritance (ADM-05 — already correct, D-12 invariance guard)

```
desc  (py:class::)
 └─ desc_signature  → "class Foo"
 └─ desc_content
      │  visit_desc_content opens: pad(left: SHARED_INDENT_STEP, {
      ├─ rubric "Options"        ← lands INSIDE the pad() wrapper automatically
      ├─ desc  (py:method::, nested)
      │   └─ desc_signature → "method(...)"
      │   └─ desc_content
      │        │ visit_desc_content opens a SECOND, nested pad(left: SHARED_INDENT_STEP, {
      │        └─ rubric "Notes"   ← lands inside BOTH nested pad() wrappers → deeper indent
      │      (close)
      │  (close)
      (close)
```

`visit_rubric` performs **no** indent logic of its own — its output is just whatever text/`strong`
call it emits, streamed into `self.body` at whatever nesting depth `visit_desc_content` has already
opened. This is mechanically why ADM-05 already holds (verified independently this session by
reading `pad(left: {SHARED_INDENT_STEP}, {{` at `typsphinx/translator.py:5255` and `:5569` —
`visit_desc_content`, not `visit_rubric`). Nothing in this phase's D-11/D-13 fix touches this
mechanism.

### Recommended Project Structure (no new files/directories)

This phase edits `typsphinx/translator.py` in place (no new modules), extends
`pyproject.toml`'s existing `[dev]` array, and adds/extends fixtures under the existing
`tests/fixtures/` convention. No structural reorganization.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| String-literal escaping for the (now catalog-sourced, potentially non-ASCII) admonition title | A second, ad-hoc escape routine "because titles are different now" | `escape_typst_string` (`typsphinx/translator.py:32`) — the project's single source of truth for Typst string-literal escaping | Every other text-bearing emission site in the translator already routes through it (Phase 38's own Security Domain section names this exact rule for its own new leaf sites). Non-ASCII text needs NO extra handling from this helper — Typst strings are UTF-8-safe; only quote/backslash/control characters need escaping |
| Grayscale desaturation of the ADM-04 render | A hand-rolled RGB→L conversion, or shelling out to a system tool | `PIL.Image.convert("L")` | D-07 already measured every system-tool alternative absent from this environment; Pillow's `convert("L")` is one call and is the industry-standard primitive for exactly this operation |
| Multi-page PNG output naming for the render fixture | Ad-hoc per-page file-splitting logic | A single-page probe fixture (see Pitfall 2 below), or Typst's own `{n}`/`{p}` output-template mechanism if multi-page is unavoidable | Typst's CLI/typst-py both require a page-number template in the output filename the moment a compiled document has more than one page; sidestepping this by keeping the probe fixture to exactly one page is simpler than implementing template-based naming for a UAT artifact |

**Key insight:** every "don't hand-roll" item above already has an established project idiom
(`escape_typst_string`) or a directly-verified library primitive (`Image.convert("L")`,
`typst.compile(format="png")`) — there is no genuinely new infrastructure decision in this phase,
only correctly reusing what already exists.

## Common Pitfalls

### Pitfall 1: The `_strong_was_*` triple-collision (D-11/D-13's root cause)

**What goes wrong:** `visit_strong`, `visit_desc_signature`, and `visit_rubric` each save their
caller's `in_paragraph`/`in_list_item`/`list_item_needs_separator` state into THREE
instance-attribute names that are IDENTICAL STRING LITERALS across all three handlers
(`self._strong_was_in_paragraph`, `self._strong_was_in_list_item`,
`self._strong_was_list_item_needs_separator` — confirmed by grep: exactly these three names appear
at `1470-1472`/`1487-1501` (`visit_strong`/`depart_strong`), `5082-5084`/`5112-5126`
(`visit_desc_signature`/`depart_desc_signature`), and `5828-5830`/`5859-5873`
(`visit_rubric`/`depart_rubric`), nowhere else in the file). Python instance attributes are just
`self.__dict__` keys — three handlers writing the same key means the SECOND writer overwrites the
FIRST writer's saved value, and the FIRST writer's `depart_*` `delattr()` call deletes state the
outer caller still needs restored.

**Why it happens (traced this session against the current code):** a `.. rubric:: A **bold**
rubric` walks as `rubric → Text("A ") → strong → Text("bold") → strong-close → Text(" rubric")`.
1. `visit_rubric` saves `was_in_list_item = self.in_list_item` (whatever it was BEFORE the rubric —
   call it `X`), sets `self.in_list_item = True`, and stores `self._strong_was_in_list_item = X`.
2. The nested `strong` child's `visit_strong` runs next. It reads `self.in_list_item` (now `True`,
   set by the rubric) as ITS OWN "before" state, and **overwrites**
   `self._strong_was_in_list_item = True` — clobbering the rubric's saved `X`.
3. The `strong` node's `depart_strong` runs, restores `self.in_list_item = True` (its own saved
   value, correct for itself) and — critically — calls `delattr(self, "_strong_was_in_list_item")`.
4. `depart_rubric` runs last. Its own restore block is `if hasattr(self,
   "_strong_was_in_list_item"): ...` — but the attribute was just DELETED in step 3, so the whole
   restore is silently skipped. `self.in_list_item` is left at `True` (the value the `strong` child
   needed), never restored to the rubric's true "before" value `X`.

**Downstream effect (verified by reading `visit_paragraph`, `typsphinx/translator.py:826-899`):**
every subsequent `nodes.paragraph` in the document checks `if self.in_list_item:` BEFORE checking
whether it should open `par({...})`. Since `in_list_item` is now permanently stuck `True`,
`visit_paragraph` takes the list-item branch (`self._emit_forced_break("parbreak()"); return`)
instead of opening `par({`. Its `Text` children still emit via `visit_Text`, which ALWAYS wraps in
`text("...")` regardless of paragraph state — so the net effect matches D-13's measured claim
exactly: `par({text("...")})` becomes a bare `text("...")` for every paragraph after the offending
rubric, to the end of the document.

**How to avoid — the recommended fix shape (Fix A):** give `visit_rubric`/`depart_rubric` their own
uniquely-named slots (e.g. `_rubric_was_in_paragraph`, `_rubric_was_in_list_item`,
`_rubric_was_list_item_needs_separator`), leaving `visit_strong`'s and `visit_desc_signature`'s
`_strong_was_*` names completely untouched:

```python
# visit_rubric — only the three assignment lines change:
self._rubric_was_in_paragraph = was_in_paragraph
self._rubric_was_in_list_item = was_in_list_item
self._rubric_was_list_item_needs_separator = was_list_item_needs_separator

# depart_rubric — only the three hasattr/restore blocks change name:
if hasattr(self, "_rubric_was_in_paragraph"):
    self.in_paragraph = self._rubric_was_in_paragraph
    delattr(self, "_rubric_was_in_paragraph")
# ...same pattern for the other two
```

With this rename, a nested `strong` inside a `rubric` uses `_strong_was_*` (its own, private slot)
and the rubric uses `_rubric_was_*` (a DIFFERENT slot) — no collision, regardless of nesting order
or depth. This is a **minimal, surgical fix**: zero risk to `desc_signature`'s emitted bytes (its
code is not touched at all), zero risk to `visit_strong` itself (also not touched), and it is
explicitly the divergence `visit_rubric`'s own docstring anticipates ("Phase 39 … is the phase that
will make this diverge from `visit_strong`'s body").

**Alternative fix shapes considered and their tradeoffs:**
| Shape | Description | Tradeoff |
|-------|-------------|----------|
| **A (recommended)** | Rename only `visit_rubric`/`depart_rubric`'s three slots | Minimal diff, zero touch to `desc_signature`/`visit_strong`, matches the docstring's anticipated divergence |
| B | Convert the three flat attributes into a shared stack (`list`), pushed/popped by all three handlers | Generalizes to any future nesting depth/combination, but requires editing `visit_strong` AND `visit_desc_signature` too — both are explicitly OUT of this phase's scope (`desc_signature` belongs to completed Phase 37; its "golden file is a fixed point" per the folded todo). Higher blast radius for no requirement this phase actually needs |
| C | Bundle the three into one tuple/namedtuple attribute instead of three separate names, still on `visit_rubric` only | Functionally identical to A, marginally tidier, same risk profile — a stylistic choice, not a different fix |
| D | Rename `visit_strong`'s slots instead of `visit_rubric`'s | Equally fixes the rubric/strong collision, but touches a handler this phase does not own (`visit_strong` is in the phase's Domain section only insofar as `rubric`/`desc_signature` *read* its attribute names, not as an edit target) — backwards from Fix A's ownership boundary |

Verify the fix with a NEW real-compile fixture (`.. rubric:: A **bold** rubric` followed by an
ordinary paragraph) asserting `par({text("...")})` on the paragraph AFTER the rubric — this is
D-13's own prescribed RED (see GATE-01 RED Design below).

### Pitfall 2: The double-blank-line wart interacts with `_emit_id_anchors`, not `visit_rubric` alone

**What goes wrong:** a rubric carrying a propagated target INSIDE a list item emits three
newlines in a row instead of the intended one, producing a visible extra blank line between the
anchor and the rubric's `strong({` open.

**Why it happens (traced this session):** `visit_rubric`'s body is:
```python
self._emit_id_anchors(node)      # (a)
self.body.append("\n")           # (b) unconditional
if not self._enter_inline_concat_element():
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")      # (c) conditional
```
`_emit_id_anchors` (`typsphinx/translator.py:394-465`) itself ends with:
```python
if self.in_list_item:
    self.list_item_needs_separator = True   # (a-tail)
```
So when the rubric is inside a list item AND carries a propagated id: (a) emits the anchor's own
trailing `"\n[...]\n"` AND sets `list_item_needs_separator = True` as a side effect; (b) then
unconditionally appends a second `"\n"`; (c) then — because `list_item_needs_separator` is now
`True` from (a)'s tail — appends a THIRD `"\n"`. Three stacked newlines where one was intended.

**How to avoid:** this is independent of Pitfall 1 (it fires even with Fix A applied) and needs its
own small change — e.g. drop the unconditional `self.body.append("\n")` at (b) when
`_emit_id_anchors` already handled separation (it always leaves `list_item_needs_separator` in a
known state), or check `self.list_item_needs_separator` BEFORE calling `_emit_id_anchors` and only
add (b)'s newline when it was `False` going in. Exact shape is Claude's Discretion (D-11 folds this
in without prescribing the mechanism); verify by extending the EXISTING
`rubric_propagated_target_render_gate` fixture (or a new one) with a rubric-inside-a-list-item
case carrying a propagated target, and asserting the anchor/rubric byte-gap shrinks to one newline.

### Pitfall 3: Static admonition titles are emitted WITHOUT escaping today

**What goes wrong:** `_depart_admonition`'s static-title branch is:
```python
elif self._custom_admonition_title:
    title_expr = f'"{self._custom_admonition_title}"'
```
This interpolates the raw string directly into a Typst string literal with no call to
`escape_typst_string`. Safe today only because every static title is a hardcoded ASCII literal with
no quote/backslash characters (`"Important"`, `"See Also"`, `"Todo"`). Once titles are sourced from
`sphinx.locale.admonitionlabels` (D-04), the string is still author-controlled data flowing through
one more layer of indirection — the same category of leaf-emission site Phase 38's own Security
Domain section flagged for its comparable leaf sites.

**How to avoid:** route the static-title branch through `escape_typst_string` before interpolating:
```python
elif self._custom_admonition_title:
    title_expr = f'"{escape_typst_string(str(self._custom_admonition_title))}"'
```
Low risk in practice (no `admonitionlabels` value in any locale is expected to contain a quote or
backslash), but zero-cost to fix and consistent with the project's "one escaping helper" rule
(Don't Hand-Roll table above).

### Pitfall 4: Typst PNG export requires a page-number template for multi-page documents

**What goes wrong:** per Typst's own docs (confirmed this session — see Sources) and the `typst-py`
README's own multi-page example, `typst.compile(..., format="png")` on a document with MORE THAN
ONE PAGE requires the `output` filename to contain a page-number template (`{n}`/`{p}`); without
it, multi-page PNG export either errors or behaves ambiguously. `typst.compile(...)` called WITHOUT
an `output=` path returns image bytes directly (a single `bytes` object for one page; for multiple
pages the underlying binding returns a *sequence*), matching the README's own `images = typst.compile(...)` naming (plural for the multi-page case).

**How to avoid:** keep the ADM-04 render probe fixture to exactly ONE page (achievable by keeping
it small — four short admonitions and nothing else forces no page break at A4). This sidesteps the
templated-filename mechanism entirely and keeps the render pipeline a single `typst.compile(...,
format="png", ppi=<N>)` call returning one `bytes` object, directly consumable by
`PIL.Image.open(io.BytesIO(png_bytes))`.

### Pitfall 5: The D-06 analytical luminance table uses a DIFFERENT formula than Pillow's actual desaturation

**What goes wrong:** CONTEXT.md's D-06 table computed luminance as `0.2126R + 0.7152G + 0.0722B`
(the ITU-R BT.709 / sRGB relative-luminance weights, the WCAG-contrast convention). Pillow's actual
`Image.convert("L")` — the tool D-07 selects to PRODUCE the UAT artifact — uses the ITU-R BT.601
luma weights instead: `L = R*299/1000 + G*587/1000 + B*114/1000` [CITED:
https://pillow.readthedocs.io/en/latest/reference/Image.html]. The two formulas are close (both
weight green heaviest) but not identical — BT.601 weights red more and green less than BT.709.

**Why it matters:** the D-06 table's percentages (band L 88.5%–93.9%, spanning "5.4 percentage
points") are a prediction from the WRONG formula for what Pillow will actually produce. This is not
a blocking defect — the owner's ADM-04 sign-off is (correctly, per D-07) made by looking at the
REAL rendered-and-desaturated PNG, not the analytical table — but the planner/executor should not
be surprised if the real artifact's perceived grey-band separation differs slightly from the D-06
numbers, and should not attempt to "fix" the render to match the table (the table was always
described as analytical scaffolding, not a target).

**How to avoid confusion:** when writing the render pipeline's own documentation/docstring, note
explicitly that the UAT artifact uses Pillow's BT.601 conversion, not the D-06 table's BT.709
figures — so a future reader does not think the two disagree due to a bug.

## Code Examples

### The Pillow greyscale-render pipeline (verified minimal shape)

```python
# Source: verified this session against typst 0.15.0's compile() signature
# (help(typst.compile) in the project's own .venv) and Pillow's documented
# Image.convert("L") behavior (pillow.readthedocs.io/en/latest/reference/Image.html)
import io
from pathlib import Path
import typst
from PIL import Image

def render_admonition_greyscale(typ_path: Path, ppi: float, out_png: Path) -> Path:
    """Compile a single-page .typ probe to PNG, desaturate, and save.

    The probe MUST be exactly one page (Pitfall 4) -- typst.compile(...,
    format="png") on a multi-page document requires a page-number template
    in the output filename, which this pipeline deliberately avoids.
    """
    png_bytes = typst.compile(str(typ_path), format="png", ppi=ppi)
    # A single-page compile returns one `bytes` object directly (verified
    # against typst-py 0.15.0's installed signature this session).
    image = Image.open(io.BytesIO(png_bytes))
    greyscale = image.convert("L")  # ITU-R BT.601 luma weights (Pitfall 5)
    greyscale.save(out_png)
    return out_png
```

Suggested artifact location (Claude's Discretion per CONTEXT.md — PPI/page-selection/naming are
explicitly left open): `.planning/phases/39-admonition-taxonomy-rubric-nesting/` alongside the
phase's other artifacts, e.g. `39-ADM04-GREYSCALE.png`, so the owner sign-off has a stable,
committed path to reference. A PPI of 150 is a reasonable default (Typst's own CLI default is 144;
150 is close and round) — this is Claude's Discretion, not a locked value.

### The Fix-A rename (Pitfall 1's fix), diffed against current code

```python
# BEFORE (typsphinx/translator.py:5828-5830, visit_rubric):
self._strong_was_in_paragraph = was_in_paragraph
self._strong_was_in_list_item = was_in_list_item
self._strong_was_list_item_needs_separator = was_list_item_needs_separator

# AFTER:
self._rubric_was_in_paragraph = was_in_paragraph
self._rubric_was_in_list_item = was_in_list_item
self._rubric_was_list_item_needs_separator = was_list_item_needs_separator

# BEFORE (typsphinx/translator.py:5859-5873, depart_rubric):
if hasattr(self, "_strong_was_in_paragraph"):
    self.in_paragraph = self._strong_was_in_paragraph
    delattr(self, "_strong_was_in_paragraph")
if hasattr(self, "_strong_was_in_list_item"):
    self.in_list_item = self._strong_was_in_list_item
    delattr(self, "_strong_was_in_list_item")
if hasattr(self, "_strong_was_list_item_needs_separator"):
    if self.in_list_item:
        self.list_item_needs_separator = True
    delattr(self, "_strong_was_list_item_needs_separator")

# AFTER (same structure, renamed slots):
if hasattr(self, "_rubric_was_in_paragraph"):
    self.in_paragraph = self._rubric_was_in_paragraph
    delattr(self, "_rubric_was_in_paragraph")
if hasattr(self, "_rubric_was_in_list_item"):
    self.in_list_item = self._rubric_was_in_list_item
    delattr(self, "_rubric_was_in_list_item")
if hasattr(self, "_rubric_was_list_item_needs_separator"):
    if self.in_list_item:
        self.list_item_needs_separator = True
    delattr(self, "_rubric_was_list_item_needs_separator")
```

`strong({...})` open/close bytes (`"strong({"` / `"})"`) are UNCHANGED — this is a state-bookkeeping
rename only, confirmed safe against `test_rubric_option_concat_render_gate.py`'s explicit literal
locks on `'strong({text("Structure Options")})'` and `'strong({text("Trailing Heading")})'` (that
test file's own comments say "Left byte-identical on purpose; do not migrate this lookup" — Fix A
honors that constraint exactly, since it changes zero emitted bytes).

## GATE-01 RED Design

Per the v0.7.0 GATE-01 amendment: every design defect must have a structural/regex/`pypdf` RED
recorded before any fix code, EXCEPT where the property already holds (SC#3/ADM-05 — an invariance
guard per D-12).

| Req | Property under test | RED status today | Fixture | Assertion shape |
|-----|---------------------|-------------------|---------|------------------|
| ADM-01 | `seealso` groups with `hint`/`tip` | **RED today** (currently emits `info(`) | NEW — no existing fixture contains `seealso` (verified: repo-wide grep of `tests/fixtures/` for `seealso`/`danger`/`attention` finds zero hits) | `.typ` string assert: `"tip({" in typ_text` at the seealso site; compiled-PDF: body sentinel present, `title` reads `"See also"` |
| ADM-02 | `attention` groups with `danger`/`error` | **RED today** (currently emits `warning(`; `danger` currently emits its OWN `danger(`, not `error(`) | Same NEW fixture as ADM-01 (combine both — cheaper than two fixtures) | `.typ` string assert: BOTH `attention` and `danger` sites emit `"error({"` | compiled-PDF: both body sentinels present |
| ADM-03 | Generic `.. admonition::` is styled + titled | **RED today** (emits unstyled `clue({`) — title itself already present (pre-existing, not the gap) | Extend `topic_line_block_render_gate` (already has `.. admonition:: Custom *Title*`) | `.typ` string assert: `"notify({" in typ_text` (currently `"clue({"`); compiled-PDF: `"Custom Title"` still present (already asserted at `test_pdf_render_gate.py:1165`, unaffected) |
| ADM-04 | 4 buckets distinguishable in greyscale | **N/A — `[V]` visual UAT, no automated RED** | New probe `.typ`/`.rst` with one instance of each of the 4 bucket types | No automated assertion — see Validation Architecture below |
| ADM-05 | Rubric inherits container indent | **GREEN today (invariance guard, D-12)** | New small local fixture: `py:class::` containing `py:method::`, each carrying `.. rubric::` (mirrors CONTEXT.md's own measurement probe) | `pypdf` x-position: rubric's left edge == its containing `desc_content` body's left edge, for both nesting levels (matches the measured table in 39-CONTEXT.md exactly) |
| D-13 (folded todo, this phase's classic RED) | `strong` nested in `rubric` must not corrupt subsequent `in_list_item` state | **RED today** (measured this session by tracing the code — see Pitfall 1) | NEW: `.. rubric:: A **bold** rubric` followed by an ordinary paragraph | `.typ` string assert: `'par({text("First paragraph after the rubric.")})' in typ_text` |
| D-11 double-blank-line wart | Rubric+propagated-target+list-item emits ONE newline, not three | **RED today** (measured this session — Pitfall 2) | Extend `rubric_propagated_target_render_gate` OR `desc_rubric_decoupling_render_gate`'s existing "rubric carrying a propagated target, inside a list item" case | Regex/count assert on the exact newline run between the anchor's close and the rubric's `strong({` open |

**Note on `desc_rubric_decoupling_render_gate`'s golden.typ:** this fixture ALREADY contains the
exact "rubric with propagated target inside a list item" shape the D-11 wart describes (see fixture
`.rst` excerpt below). Fixing the wart will change `golden.typ`'s bytes for that one rubric. This
is Phase 39's own, IN-SCOPE change — `test_emitted_typ_is_byte_identical_to_golden`
(`tests/test_desc_rubric_decoupling_render_gate.py:272-310`) will need its `golden.typ` regenerated
and hand-verified (never copied from the fixed code's own output without review, per D-14's "never
by copying failing output" rule) as part of this phase's plan, not treated as an unexpected
regression to chase down.

```
# tests/fixtures/desc_rubric_decoupling_render_gate/index.rst (excerpt, confirmed this session):
* First bullet text.

  .. _decoupling-rubric-in-list-target:

  .. rubric:: A Rubric In A List Item

  More text after the rubric.
```

## Blast-Radius Re-Take (D-14 — re-taken, not trusted)

Re-ran the census live this session. **Raw counts match CONTEXT.md exactly** (18 clue-call
assertions in `test_admonitions.py`, 3 `clue({`-related assertions in `test_topics.py`, 4 in
`test_pdf_render_gate.py`, plus the five named rubric-touching modules and five fixtures — repo-wide
grep for clue-function-open strings across `tests/` finds only these three files; repo-wide grep for
`seealso`/`danger`/`attention`/`.. admonition::`/`.. topic::` content across `tests/fixtures/`
finds only one fixture, `topic_line_block_render_gate/index.rst`).

**Refinement beyond CONTEXT.md's raw count — which of the 18 `test_admonitions.py` assertions
actually go RED**, traced by reading every test function in the file:

| Line | Test | Assertion | Goes RED under D-01..D-03/D-09/D-10? |
|------|------|-----------|----------------------------------------|
| 49 | `test_note_converts_to_info` | `"info({" in output` | No — note stays `info` |
| 68 | `test_warning_converts_to_warning` | `"warning({" in output` | No — warning stays `warning` |
| 87 | `test_tip_converts_to_tip` | `"tip({" in output` | No — tip stays `tip` |
| 108, 110 | `test_important_converts_to_warning_with_title` | `"warning({" in output`, `', title: "Important"' in output` | No — bucket unchanged; catalog's English "Important" is byte-identical to the current static string |
| 128 | `test_caution_converts_to_warning` | `"warning({" in output` | No — caution stays `warning` |
| **147, 149** | `test_seealso_converts_to_info_with_title` | `"info({" in output`, `', title: "See Also"' in output` | **YES** — must become `"tip({"` (D-02) and `', title: "See also"'` (D-05, lowercase) |
| 169 | `test_admonition_with_multiple_paragraphs` | `"info({" in output` | No — plain `note`, unaffected |
| 193, 196 | `test_nested_admonitions` | `"info({" in output`, `"warning({" in output` | No — outer `note`/inner `warning`, both unaffected |
| 223 | `test_nested_list_in_note` | `"info({" in output` | No |
| 244 | `test_nested_code_block_in_note` | `"info({" in output` | No |
| 269, 311 | title-preservation tests | `"info({" in output` | No |
| 338 | `test_hint_converts_to_tip` | `"tip({" in output` | No — hint stays `tip` |
| 357 | `test_error_converts_to_error` | `"error({" in output` | No — error stays `error` |
| **376** | `test_danger_converts_to_danger` | `"danger({" in output` | **YES** — must become `"error({"` (D-03); test name itself becomes misleading and should be renamed |
| **400** | `test_attention_converts_to_warning` | `"warning({" in output` | **YES** — must become `"error({"` (D-03); test name should be renamed |
| **428** | `test_generic_admonition_converts_to_clue` | `"clue({" in output` | **YES** — must become `"notify({"` (D-09); test name should be renamed |

**Net: 5 of the 18 assertions (across 4 test functions) actually require edits**; the other 13 stay
green untouched because their bucket assignment doesn't move and their titles (where checked) are
byte-identical in English between the old static string and the new catalog value. **All 4 affected
test function NAMES also become misleading** (`test_danger_converts_to_danger`,
`test_attention_converts_to_warning`, `test_generic_admonition_converts_to_clue`,
`test_seealso_converts_to_info_with_title`) and should be renamed in the same commit, not just their
bodies — D-14's "re-derived by hand" instruction extends to names, since a stale name is itself a
form of incorrect documentation.

**`test_topics.py`'s 3 assertions:** lines 59 and 90 (`assert "clue({" in output` for a normal
topic) must become `assert "abstract({" in output` (D-10); line 134 (`assert "clue({" not in
output`, the box-less `.. contents::` control) is UNAFFECTED — D-10 doesn't touch the contents
path, so this negative assertion remains true.

**`test_pdf_render_gate.py`'s 4 assertions** (`test_admonitiontitleregression_multichild`, lines
1157-1173): checks body SENTINELS (`ADMONITIONNOTESENTINEL`, `ADMONITIONWARNINGSENTINEL`,
`ADMONITIONCUSTOMSENTINEL`) and a directive-SUPPLIED title (`"Custom Title"`) — none of these are
catalog-default titles, and `note`/`warning`/generic-`admonition` don't change bucket. **None of
these 4 assertions need to change** for ADM-01/02/03's own sake, BUT this fixture's `.. admonition::
Custom *Title*` DOES need its emitted-call assertion added (currently absent — the compiled-PDF
half of ADM-03 is covered, the `.typ`-string half is not, per the GATE-01 RED table above).

**Rubric-touching modules — confirmed, with the specific golden-file impact flagged above:**
`test_desc_rubric_decoupling_render_gate.py` (golden.typ WILL change, Pitfall 2/GATE-01 table),
`test_rubric_option_concat_render_gate.py` (confirmed UNAFFECTED — its two rubrics are neither
nested-with-strong nor list-item+propagated-target), `test_rubric_propagated_target_render_gate.py`
(confirmed UNAFFECTED — its propagated-target rubric is NOT inside a list item),
`test_signature_typography_multi_signature_page_count_gate.py` (confirmed UNAFFECTED — only
REFERENCES `desc_rubric_decoupling_render_gate/golden.typ` in a comment, has no rubric content of
its own), `test_translator.py::test_rubric_rendering` (a tautological `"..." in output or "Methods"
in output` assertion — technically in the census, practically will not go RED regardless of the
fix).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `typst` (typst-py) | ADM-04 render, all `-b typstpdf` GATE-01 fixtures | Yes | 0.15.0 (matches pin) | — |
| `pypdf` | ADM-05 x-position measurement, all compiled-PDF text assertions | Yes (already a `[dev]` dependency, `>=6.14,<7`) | — (already installed per prior phases) | — |
| `pillow` | ADM-04 greyscale desaturation | **No — must be added** (D-07) | Target: latest `12.3.0`, planner picks exact floor | None viable (Pitfall/Alternatives above) — this is a hard `[dev]`-extra add, not optional |
| System PNG/PDF tools (`pdftoppm`, `mutool`, ImageMagick `convert`, ghostscript) | Would-be Pillow alternative | No (all absent, re-confirmed this session) | — | N/A — Pillow is the only viable path (matches D-07) |

**Missing dependencies with no fallback:** `pillow` — must be added to `pyproject.toml`'s `[dev]`
extra as an in-scope task of this phase (D-07), gated behind a `checkpoint:human-verify` per the
Package Legitimacy Audit's SUS disposition.

**Worktree-isolation consequence (CLAUDE.md "Worktree-isolated execution" — standing execution
mode, not conditional):** every executor worktree runs its own
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` from ITS OWN checked-out
`pyproject.toml`. This means: **the `pyproject.toml` edit adding `pillow` must land (be committed)
in a wave/plan that any LATER plan importing `PIL` depends on** — either (a) put the
`pyproject.toml` edit and the Pillow-using render code in the SAME plan (simplest — one worktree,
one `uv sync` picks up both), or (b) if split across plans/waves, ensure the plan carrying the
`pyproject.toml` edit is sequenced strictly BEFORE (not merely parallel with) any plan that runs
`import PIL`. A parallel-wave worktree created from a base ref that predates the `pyproject.toml`
edit will `uv sync` successfully but WITHOUT pillow installed, and `import PIL` will fail at test
time with no obvious connection to the missing edit. Flag this explicitly in the plan's task
ordering, not just its dependency graph comments.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ (project pin: `pytest>=8.4,<10`), config in `pyproject.toml` `[tool.pytest.ini_options]` |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`, markers `slow`/`integration`) |
| Quick run command | `uv run pytest tests/test_admonitions.py tests/test_topics.py -x` (fast, no `typst.compile()`, no `slow` marker) |
| Full suite command | `uv run pytest -m "not slow"` for the fast tier; `uv run pytest` (unfiltered) for the full gate including every `slow`-marked real-compile fixture; the milestone's own full-corpus gate is `uv run pytest tests/test_corpus_gate.py -m slow` (network-dependent, skips gracefully offline) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| ADM-01 | `seealso` emits `tip({`, groups with hint/tip | unit + PDF render-gate | `uv run pytest tests/test_admonitions.py -k seealso -x` (unit); `uv run pytest tests/test_pdf_render_gate.py -k <new fixture name> -x` (compiled-PDF) | Unit: ✅ (edit existing); PDF: ❌ Wave 0 — new/extended fixture needed |
| ADM-02 | `attention`/`danger` both emit `error({` | unit + PDF render-gate | `uv run pytest tests/test_admonitions.py -k "attention or danger" -x`; same new PDF fixture as ADM-01 | Unit: ✅ (edit existing); PDF: ❌ Wave 0 (share fixture with ADM-01) |
| ADM-03 | Generic `.. admonition::` emits `notify({` + carries its title into compiled PDF | unit + PDF render-gate | `uv run pytest tests/test_admonitions.py -k generic_admonition -x`; `uv run pytest tests/test_pdf_render_gate.py -k AdmonitionTitleRegression -x` (title half already exists; `.typ`-call half needs a new assertion added to the SAME fixture) | Unit: ✅ (edit existing); PDF title: ✅ (already exists, add function-name assert alongside it) |
| ADM-04 | 4 buckets stay distinguishable in greyscale | **manual-only** (`[V]` — visual UAT, no mechanical test possible per REQUIREMENTS.md's own legend) | N/A — produce `39-ADM04-GREYSCALE.png` via the Pillow pipeline (Code Examples above), owner inspects and signs off in phase artifacts | Wave 0: ❌ — new render-and-desaturate script needed (not a pytest test at all) |
| ADM-05 | Rubric left edge == containing body's left edge (nested + top-level) | `pypdf` geometry, **invariance guard (D-12)** | New: `uv run pytest tests/test_rubric_indent_invariance.py -x` (or added to an existing rubric-touching module) | ❌ Wave 0 — new small local fixture (`py:class::`/`py:method::` each with `.. rubric::`) + pypdf x-position assertions mirroring CONTEXT.md's measured table |
| D-13 (folded, this phase's classic RED) | `strong` nested in `rubric` doesn't corrupt later `par()` wrapping | `.typ`-string assert, real `-b typst` build | New: `uv run pytest tests/test_rubric_strong_nesting_render_gate.py -x` (suggested name) | ❌ Wave 0 — new fixture: `.. rubric:: A **bold** rubric` + a following paragraph |
| D-11 (folded, double-blank-line wart) | Rubric+propagated-target+list-item emits exactly one separator newline | Regex/count assert, real `-b typst` build | Extend `tests/test_rubric_propagated_target_render_gate.py` or `tests/test_desc_rubric_decoupling_render_gate.py` | Partial — fixture with the SHAPE already exists (`desc_rubric_decoupling_render_gate`); a NEW assertion counting the newline run must be added |
| SC#5 (test migration) | Full-corpus `-b typstpdf` gate green after all admonition/rubric edits | integration, network-dependent | `uv run pytest tests/test_corpus_gate.py -m slow` | ✅ exists — re-run as the phase's final gate, not a new test |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_admonitions.py tests/test_topics.py -x` (fast unit tier, <5s, no compile)
- **Per wave merge:** `uv run pytest -m "not slow"` (everything except real-compile/corpus tests) plus any `slow`-marked render-gate fixtures this phase adds or touches directly (`uv run pytest tests/test_pdf_render_gate.py tests/test_desc_rubric_decoupling_render_gate.py tests/test_rubric_*.py -x`)
- **Phase gate:** full suite green (`uv run pytest`) before `/gsd-verify-work`; the full-corpus `-b typstpdf` gate (`tests/test_corpus_gate.py -m slow`) re-run green per SC#5, network permitting (skips, does not fail, when offline — do not treat a skip as the SC#5 gate passing; it must actually run at least once before phase close)

### Wave 0 Gaps
- [ ] New/extended real-compile fixture covering `seealso`/`attention`/`danger` for ADM-01/ADM-02's compiled-PDF half — no existing fixture contains these three types (confirmed by repo-wide grep)
- [ ] New assertion (not a new fixture) on the existing `topic_line_block_render_gate`-backed test for ADM-03's `notify({` emission — the compiled-PDF title half already exists
- [ ] New small local fixture (`py:class::` + nested `py:method::`, each with `.. rubric::`) + `pypdf` x-position assertions for ADM-05's invariance guard
- [ ] New fixture (`.. rubric:: A **bold** rubric` + trailing paragraph) for D-13's classic RED
- [ ] New assertion extending an existing propagated-target rubric fixture for D-11's double-blank-line wart
- [ ] New (non-pytest) render-and-desaturate script/task for ADM-04's UAT artifact, plus the artifact's committed output path
- [ ] `pyproject.toml` `[dev]` extra edit (adds `pillow`) — gated behind `checkpoint:human-verify` per the Package Legitimacy Audit
- [ ] `golden.typ` regeneration for `tests/test_desc_rubric_decoupling_render_gate.py` if the D-11 wart fix is applied (expected, not a regression — see GATE-01 RED Design note above)
- [ ] Rename 4 misleading test-function names in `test_admonitions.py` (danger/attention/generic-admonition/seealso tests) alongside their body edits

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|-------------------|
| V2 Authentication | no | N/A — build-time Sphinx extension, no runtime auth surface |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes | `escape_typst_string` (`typsphinx/translator.py:32`) — the sole escaping helper. This phase's ONE new leaf-emission concern (Pitfall 3: the static admonition-title branch in `_depart_admonition`) must route through it, matching every other text-bearing emission site in the translator, and must NOT introduce a second title-specific escaping routine |
| V6 Cryptography | no | N/A — no cryptographic operation anywhere in this pipeline |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Typst string-literal injection via an unescaped admonition title now sourced from an external catalog (`sphinx.locale.admonitionlabels`) rather than a hardcoded Python literal | Tampering | Route the static-title branch of `_depart_admonition` through `escape_typst_string` before interpolation (Pitfall 3) — low real-world likelihood (locale strings are Sphinx-authored, not end-user input), but the class of bug is identical to prior phases' T-37-01/T-38-equivalent findings and the fix is one line |
| A structurally-required newline/separator silently miscounted (Pitfall 1/2's collision and double-blank-line bugs) merging or over-separating adjacent blocks | Denial of service (rendering-correctness class, mirrors Phase 37's T-37-05 / Phase 38's equivalent) | Both fixes ship with real-compile GATE-01 fixtures (GATE-01 RED Design table above) asserting the EXACT expected byte shape, not just "compiles" |
| A new runtime dependency slipping in via this phase's `pyproject.toml` edit | Tampering (supply chain) | `pillow` is dev-only (never a runtime dependency — milestone invariant #1 unaffected); Package Legitimacy Audit ran and flagged it `SUS` (checker coverage gap, not a real finding) — gated behind `checkpoint:human-verify` per protocol regardless |

## Sources

### Primary (HIGH confidence)
- Direct reads of `typsphinx/translator.py` this session: `_visit_admonition`/`_depart_admonition`
  (4337-4399), all 13 `visit_X`/`depart_X` admonition call sites (4401-4559), `visit_strong`/
  `depart_strong` (1429-1501), `visit_desc_signature`/`depart_desc_signature` (4970-5126),
  `visit_rubric`/`depart_rubric` (5767-5889), `_emit_id_anchors` (394-465), `visit_paragraph`/
  `depart_paragraph` (826-940), `visit_Text` (1206-1308), `escape_typst_string` (32-63), both
  `pad(left: SHARED_INDENT_STEP` sites (5255, 5569).
- Direct `.venv` introspection this session: `help(typst.compile)` (confirms `format`/`ppi`
  parameters exist in the installed 0.15.0), `importlib.metadata.version("typst")` → `0.15.0`,
  `from sphinx.locale import admonitionlabels; pprint.pprint(dict(...))` (confirms all 10 keys and
  English values, including `seealso` → `"See also"` lowercase).
- Direct repo-wide `grep`/`Read` of `tests/test_admonitions.py` (full file, 434 lines),
  `tests/test_topics.py` (grep), `tests/test_pdf_render_gate.py` (targeted sections),
  `tests/test_desc_rubric_decoupling_render_gate.py` (full file, 350 lines),
  `tests/test_rubric_option_concat_render_gate.py` (full file, 179 lines),
  `tests/test_rubric_propagated_target_render_gate.py` (grep + fixture `.rst`),
  `tests/test_signature_typography_multi_signature_page_count_gate.py` (grep),
  `tests/test_translator.py` (grep for `rubric`), and the four fixture `.rst` files named above.
- `gsd-tools query package-legitimacy check --ecosystem pypi pillow` — this session, verdict `SUS`
  with reasons `["unknown-downloads"]`, `exists: true`, `repoUrl:
  https://github.com/python-pillow/Pillow`.
- Direct PyPI JSON API fetch (`https://pypi.org/pypi/pillow/json`) this session — `info.version` →
  `12.3.0`.

### Secondary (MEDIUM confidence)
- [CITED: https://typst.app/docs/reference/png] — official Typst docs confirming PNG export is
  resolution-bound (PPI), default PPI 144, and multi-page documents require a page-number template
  in the output filename.
- [CITED: https://github.com/messense/typst-py] — `typst-py` README's own multi-page
  (`output="hello{n}.png"`) and single-image (`typst.compile(..., format="png", ppi=144.0)`)
  usage examples, consistent with this session's own `help(typst.compile)` introspection.
- [CITED: https://pillow.readthedocs.io/en/latest/reference/Image.html] — official Pillow docs
  confirming `Image.convert("L")` uses the ITU-R BT.601 luma transform
  (`L = R*299/1000 + G*587/1000 + B*114/1000`), the basis for Pitfall 5.

### Tertiary (LOW confidence)
- None — every claim in this document traces to a direct code/environment read this session or an
  official-documentation citation. 39-CONTEXT.md's own measured decisions (D-01 through D-14) are
  treated as locked upstream inputs, not re-derived, per the research scope guidance; they are not
  re-tagged with confidence levels here since they are inputs, not this session's findings.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|-----------------|
| A1 | The suggested `pillow` version floor (`>=11,<13`) is a reasonable default matching the project's other `[dev]` bound style | Standard Stack | Low — explicitly flagged as Claude's Discretion per CONTEXT.md; planner/owner can pick any floor that resolves to a version supporting `Image.convert("L")` (present since Pillow's earliest releases) |
| A2 | A single-page probe fixture is sufficient for ADM-04's greyscale render (Pitfall 4's recommended mitigation) | Common Pitfalls / Code Examples | Low — if the owner wants all four bucket types visible with more surrounding context that pushes past one page, the render pipeline needs the `{n}`-template extension; flagged explicitly as a fallback path, not hidden |
| A3 | Fix Shape A (rename only `visit_rubric`'s slots) is sufficient and no other nesting scenario (e.g. `emphasis` inside `rubric`) shares the collision | Pitfall 1 | Low — verified via grep that `_strong_was_*` names appear ONLY at the three sites named; `visit_emphasis` uses its own, differently-named `_emph_was_*` slots (confirmed via the same grep sweep for `in_list_item` usage), so no other collision exists today |

**If this table is empty:** N/A — see above; all three logged assumptions are low-risk and already
flagged as Discretion or verified against the actual grep sweep, not left unverified.

## Open Questions

1. **Exact naming/location for the new fixtures this phase adds.**
   - What we know: at minimum, one new fixture for ADM-01/ADM-02 (seealso/attention/danger), one
     new fixture (or fixture extension) for D-13's classic RED, one new small local fixture for
     ADM-05's invariance guard, and one extension for D-11's wart.
   - What's unclear: whether the planner combines any of these into ONE fixture (e.g. the ADM-05
     probe could also carry the D-13 rubric-with-bold-title case, since both are rubric-focused) or
     keeps them separate for isolation/clarity.
   - Recommendation: prefer separate, narrowly-scoped fixtures (matches this repo's existing
     convention — nearly every fixture directory maps to exactly one defect/property), but combining
     ADM-01+ADM-02 into one fixture (both need `seealso`/`attention`/`danger` content anyway) is
     efficient and low-risk.

2. **Whether SC#3's "real API page" language requires actual `sphinx.ext.autodoc`+napoleon
   extraction, or a hand-authored `py:class::`/`.. rubric::` probe is sufficient.**
   - What we know: CONTEXT.md's OWN measurement methodology used a hand-authored probe (not real
     autodoc extraction), and the resulting docutils node SHAPE (`desc` → `desc_content` → `rubric`)
     is identical either way — `visit_rubric`/`visit_desc_content` cannot distinguish a
     hand-authored rubric from an autodoc-generated one.
   - What's unclear: whether a stricter reading of SC#3's prose demands wiring up a real
     `autodoc`+`napoleon`/`numpydoc` extraction against an actual importable Python module.
   - Recommendation: use the hand-authored local probe (matches CONTEXT.md's own precedent, keeps
     the gate fast/deterministic/network-free) unless the owner specifically objects during plan
     review — flag this choice explicitly in the plan so it's visible for that review.

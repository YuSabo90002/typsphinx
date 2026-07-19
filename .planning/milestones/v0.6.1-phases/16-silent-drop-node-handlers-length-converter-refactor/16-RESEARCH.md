# Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor - Research

**Researched:** 2026-07-16
**Domain:** docutils/Sphinx node-visitor translation (`typsphinx/translator.py`) + a locally-cached
Typst `@preview` package (`gentle-clues:1.3.1`)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**todo_node (TODO-01)**
- **D-01: Box via the admonition helper as `task` + title "Todo".** Reuse the existing
  `_visit_admonition(node, "task", custom_title="Todo")` / `_depart_admonition()` pair
  (translator.py:3643). `task` is the closest semantic gentle-clues clue for a "to-be-done work
  item"; the title `"Todo"` matches Sphinx's own HTML admonition heading. The todo body (child
  paragraphs/lists) flows through the normal chain, exactly like `note`/`warning`.
- **D-01a: Fallback if `task` is absent.** gentle-clues 1.3.1 must actually expose a `task` clue
  function. The researcher MUST verify this against the bundled gentle-clues version; if `task` is
  not a valid clue, fall back to the base `clue` function with `custom_title="Todo"` (same treatment
  as generic `.. admonition::`, translator.py:3796). Do not invent a new package or bump the version.
- **D-01b: `todolist` is out of scope.** Only `todo_node` is in scope (the requirement and the
  corpus drop are `todo_node` ×10). The `todolist` aggregation node is NOT handled in this phase.

**manpage (MAN-01)**
- **D-02: Render as `emph` (italic), Sphinx-HTML-faithful.** Emit `#emph[` on visit, let the
  node's own `Text` child render `ls(1)` through the normal chain, emit `]` on depart. This matches
  Sphinx's HTML `<em class="manpage">` and LaTeX `\sphinxstyleliteralemphasis` (both italic).
  Chosen over the no-op passthrough (which loses the manpage distinction) and over `raw()`
  monospace (which diverges from Sphinx's italic rendering).
- **D-02a: No linkification.** `manpages_url`-based linking is a separate Sphinx feature and is out
  of scope — render the literal page-reference text only, per the requirement.

**CSS-length converter (LEN-01)**
- **D-03: Proactive — audit and wire every length-bearing site (not image-only).** SC#3 explicitly
  requires the conversion "reused at every length-bearing site." The researcher audits every node
  that can carry a CSS-length attribute (`:width:`/`:height:` on image — already wired; `:figwidth:`
  on figure; `:width:` on `.. table::` / `.. csv-table::` / `.. list-table::`; any other
  length-normalized attribute docutils produces) and routes each through `_convert_length_to_typst`.
- **D-03a: Boundary between "fix" and "enable" — both are in scope, neither is scope creep.** For
  each audited site classify it:
  - *Currently emits a length to Typst but un-/mis-converted* → route through the shared helper (this
    is the original px→pt bug class the helper was created to prevent).
  - *Currently ignores the length entirely* (e.g. figure `:figwidth:`, table `:width:` are not
    presently passed to Typst at all) → wire it in through the shared helper. Because SC#3 mandates
    "every length-bearing site," this wiring IS the LEN-01 requirement, not a new capability —
    document it as such so the scope guard is not tripped during review.
- **D-03b: Single source of truth, no duplicated conversion.** After the refactor there must be
  exactly one conversion implementation (`_convert_length_to_typst`); no site may contain its own
  px→pt / pc→pt arithmetic. The unsupported-unit → drop-with-one-warning contract (D-02 from Phase
  11) is preserved at every wired site.

### Claude's Discretion
- Exact `emph`/wrapper punctuation and whitespace for `manpage`.
- The precise predicate/order for auditing length-bearing sites and the exact per-site wiring shape
  (planner/executor call), provided D-03b's single-source invariant holds.
- Fixture document contents beyond the explicit success-criteria cases (each of the three changes
  needs at least one real-compile fixture per SC#4).
- Exact `logger.warning` wording for any unsupported-unit drop at newly-wired sites.

### Deferred Ideas (OUT OF SCOPE)
- `todolist` node handling (the `.. todolist::` aggregation directive) — out of scope for Phase 16;
  candidate for a future fidelity phase if the corpus needs it.
- `manpages_url`-based linkification of `:manpage:` references — separate Sphinx feature, out of
  scope.

None of the above are blockers; captured so they are not lost.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TODO-01 | `.. todo::` (`todo_node`) renders its body as an admonition-style block instead of being silently dropped; `unknown node type: <todo_node>` warning eliminated (×10 in corpus). | Verified `task` clue exists in the pinned gentle-clues 1.3.1 (read directly from `~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/predefined.typ`); verified via a real `typst.compile()` + PDF-text-extraction round trip that `task(title: "Todo")[...]` compiles AND the explicit title overrides `task`'s internal auto-title (no duplicate-argument error). Verified via Sphinx source (`sphinx/ext/todo.py`) that `todo_node` already carries a `nodes.title` child (unlike note/warning) and that Sphinx's own HTML/LaTeX writers gate rendering on `config.todo_include_todos` (default `False`) — a semantics point the planner must decide on. |
| MAN-01 | `:manpage:` (`manpage` node) renders as literal page-reference text (e.g. `ls(1)`) instead of being dropped; `unknown node type: <manpage>` warning eliminated (×10 in corpus). | Verified via `translator.py`'s existing `visit_emphasis`/`depart_emphasis` (the real precedent for italic wrapping) that inline wrapping in this codebase is `{prefix}emph({{...}})` — a code-mode function call with a conditional `#` prefix based on `self._in_markup_mode`, NOT bare `#emph[...]` markup as CONTEXT.md's D-02 phrasing literally states. Verified via Sphinx source (`sphinx/roles.py` `Manpage.run()`) that the node's single child is a plain `Text` node unless `manpages_url` is configured (confirmed unset in this project's `docs/conf.py` and the corpus's `doc/conf.py`). |
| LEN-01 | CSS-length → Typst-length conversion generalized into one shared helper reused at every length-bearing site; no duplicated conversion logic. | Verified exhaustively via `grep` across the entire installed docutils package that exactly two directive families use `length_or_percentage_or_unitless`/`length_or_unitless`: `images.py` (image width/height, figure figwidth) and `tables.py` (table/csv-table/list-table width) — this closes the audit with certainty, no other docutils directive needs wiring. Verified via real `typst.compile()` that Typst's built-in `table()` and `figure()` functions do NOT accept a `width` argument directly (`unexpected argument: width`) but that wrapping content in `#block(width: X)[...]` compiles correctly for both. |
</phase_requirements>

## Summary

All three items in this phase are narrow, additive `translator.py` changes with existing precedent
in the codebase, and every non-trivial design question was resolved this session by reading the
actual pinned dependency source and/or running a real `typst.compile()` — not by inference. The
locked CONTEXT.md decisions (D-01/D-02/D-03) are all implementable as written, but three important
nuances were discovered that the planner must account for:

1. **TODO-01**: gentle-clues 1.3.1's `task` clue is real and DOES accept an explicit `title:`
   override safely (empirically proven — no duplicate-argument compile error, confirmed by real PDF
   text extraction showing "Todo" rendered, not "Task N"). Separately, `todo_node` already carries
   its own `nodes.title` child (Sphinx inserts `nodes.title(text=_('Todo'))` at index 0), which the
   translator's existing `visit_title` admonition-aware buffer-swap will pick up automatically
   (since `todo_node` subclasses `nodes.Admonition`) — meaning the *dynamic* title always wins over
   the `custom_title="Todo"` static fallback. This is harmless (same text, non-i18n case) but the
   planner should know the `custom_title` argument is effectively inert here, not load-bearing.
   Separately and more importantly: **every official Sphinx builder (HTML, LaTeX, text, man,
   texinfo) gates todo-body rendering on `config.todo_include_todos` (default `False`), skipping the
   body entirely via `nodes.SkipNode` when unset.** This is not covered by CONTEXT.md and is a
   genuine open decision — see Open Questions.

2. **MAN-01**: The actual established "wrap in italic" pattern in this codebase
   (`visit_emphasis`/`depart_emphasis`) is materially more complex than CONTEXT.md's literal
   `#emph[` / `]` phrasing: it conditionally emits a `#` prefix based on `self._in_markup_mode`,
   opens a code-mode content block (`emph({`...`})`, not markup brackets), and participates in the
   paragraph-separator / list-item-separator / inline-concat-context state machine
   (`_enter_inline_concat_element`/`_exit_inline_concat_element`). `manpage`'s handler must either
   replicate this state handling or (preferred, DRY) delegate directly to
   `self.visit_emphasis(node)`/`self.depart_emphasis(node)` — Python duck-typing makes this a safe
   alias since neither method does an `isinstance` check on the node argument. The `visit_abbreviation`
   pattern CONTEXT.md's canonical_refs pointed to is a *different* shape (no-op visit + depart-time
   text append) and is not analogous to manpage's "wrap the existing Text child" requirement.

3. **LEN-01**: The audit is closed and exhaustive (verified via `grep` of docutils' own directive
   source, not assumption): only `image` (width/height, already wired), `figure` (`:figwidth:` →
   `node["width"]`, unwired), and `table`/`csv-table`/`list-table` (`:width:` → `node["width"]`, all
   three converge on the single `nodes.table` type, unwired) ever populate a
   `length_or_percentage_or_unitless`/`length_or_unitless`-normalized attribute. Wiring is exactly
   two new call sites (`visit_figure`, `visit_table`/`depart_table`), not three. Both Typst's
   `figure()` and `table()` functions reject a `width:` argument directly — confirmed by a failing
   real compile (`unexpected argument: width`) — so the wiring shape must wrap the figure/table call
   in `#block(width: X)[...]`, not pass `width:` as a kwarg to `figure()`/`table()` themselves.

**Primary recommendation:** Implement all three items as three separate small PLAN.md's per the
proposed 16-01/16-02/16-03 split; each is independently low-risk, has a clear existing pattern to
follow, and needs its own real-compile fixture per GATE-01/SC#4. For LEN-01 specifically, wire
`visit_figure` and `visit_table`/`depart_table` to read `node.get("width")` and, when present, wrap
the whole figure/table call in `#block(width: <converted>)[...]`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `todo_node` → Typst admonition rendering | Translator (`typsphinx/translator.py`, `visit_todo_node`/`depart_todo_node`) | Typst package (`@preview/gentle-clues:1.3.1`, `task` clue) | The translator owns node→Typst-source mapping; gentle-clues owns the visual box rendering at compile time. No builder/template/writer changes needed. |
| `manpage` → literal italic text | Translator (`typsphinx/translator.py`, `visit_manpage`/`depart_manpage`, delegating to the existing `visit_emphasis`/`depart_emphasis` machinery) | — | Purely an inline-node → `emph()` mapping; no other tier involved. |
| CSS-length → Typst-length conversion | Translator (`typsphinx/translator.py`, `_convert_length_to_typst` + its call sites in `visit_image`, `visit_figure`, `visit_table`/`depart_table`) | — | Single shared helper method on the translator; no builder/template/writer changes needed. |

## Standard Stack

### Core
No new libraries. This phase touches only `typsphinx/translator.py` — zero new runtime dependencies,
per the milestone invariant.

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `@preview/gentle-clues` | 1.3.1 (already pinned, unchanged) | Admonition-style box rendering for `task` clue | Already the project's single admonition-rendering package; `task` clue confirmed present in the exact pinned version (see Package Legitimacy Audit — not a new install, so the audit is informational only). |

### Supporting
N/A — no supporting libraries needed for this phase.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `task` clue for `todo_node` | base `clue` function with `custom_title="Todo"` (D-01a fallback) | Not needed — `task` is confirmed present and works correctly with a title override. Keep as documented fallback only if a future gentle-clues version drops `task` (unlikely; not anticipated). |
| Delegating `visit_manpage`→`visit_emphasis` | Writing a bespoke, simplified visit/depart pair | A bespoke simpler pair risks silently dropping the paragraph-separator/list-item/inline-concat state handling that real documents need (manpage roles can appear inside list items, table cells, definition-list terms, etc. — all places `visit_emphasis` already handles correctly). Delegation is DRY and behavior-complete for free. |

**Installation:** None — no new packages.

**Version verification:** `@preview/gentle-clues:1.3.1` is already declared in `writer.py`,
`template_engine.py`, and `templates/base.typ` (the 3-way version-sync surface) and is untouched by
this phase. Verified present in the local Typst package cache at
`~/.cache/typst/packages/preview/gentle-clues/1.3.1/` — the exact pinned version, so no drift risk
between what was inspected and what ships.

## Package Legitimacy Audit

No new packages are installed by this phase (milestone invariant: zero new runtime dependencies, the
3-way `@preview` version-sync surface stays untouched). The only package referenced (`gentle-clues`)
is already a locked, existing dependency of the project — audited here only for completeness/context,
not as a new-install gate.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `@preview/gentle-clues` 1.3.1 | Typst Universe (`@preview`) | Pre-existing project dependency, unchanged this phase | N/A (Typst Universe has no npm-style download counter) | Confirmed present locally at `~/.cache/typst/packages/preview/gentle-clues/1.3.1/`, `typst.toml` present | OK (pre-existing, not re-audited for legitimacy — already in production use since Phase 12) | No action — reused as-is |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
docutils doctree (todo_node / manpage / figure[width] / table[width])
        |
        v
TypstTranslator.visit_*/depart_* (typsphinx/translator.py)
   |-- visit_todo_node/depart_todo_node
   |       -> delegates to _visit_admonition(node, "task", custom_title="Todo")
   |          + _depart_admonition()   [reused, unmodified]
   |       -> body children (paragraphs/lists) stream through the SAME
   |          visit_paragraph/visit_Text/etc. chain used by note/warning
   |
   |-- visit_manpage/depart_manpage
   |       -> delegates to visit_emphasis(node)/depart_emphasis(node)
   |          [reused, unmodified state machine]
   |       -> the node's Text child streams through visit_Text unchanged
   |
   |-- visit_figure (reads node.get("width"))  --\
   |-- visit_table / depart_table (reads         |--> _convert_length_to_typst(value)
   |       node.get("width"))                   /       [single shared helper,
   |                                                      already exists at ~line 3009]
   |       -> if converted is not None: wrap the figure()/table() call in
   |          #block(width: <converted>)[ ... ] (Typst rejects width: as a
   |          direct figure()/table() kwarg -- verified by real compile)
   v
body string  ->  TemplateEngine (unchanged)  ->  .typ file  ->  typst.compile()  ->  PDF
```

### Recommended Project Structure
No new files/directories for source code — all three changes live inside
`typsphinx/translator.py`. New test fixture directories follow the existing
`tests/fixtures/<name>_render_gate/` convention:
```
tests/
├── fixtures/
│   ├── todo_render_gate/        # NEW — TODO-01 GATE-01 fixture (conf.py + index.rst)
│   └── manpage_render_gate/     # NEW — MAN-01 GATE-01 fixture (conf.py + index.rst)
│                                 # LEN-01 can extend the existing
│                                 # figure_length_render_gate fixture (figwidth cases)
│                                 # and add a new table-width case (new or extended fixture)
└── test_pdf_render_gate.py      # extend with new test_* functions per fixture
```

### Pattern 1: Admonition reuse for `todo_node` (TODO-01)
**What:** `todo_node` subclasses `docutils.nodes.Admonition`, exactly like `note`/`warning`/etc.
already handled via `_visit_admonition`/`_depart_admonition`. Reuse this machinery verbatim.
**When to use:** Any Sphinx/docutils node whose class inherits `nodes.Admonition` and needs a
gentle-clues box.
**Example (mirrors the existing `visit_hint`/`depart_hint` pair at translator.py:3755):**
```python
# Source: typsphinx/translator.py:3643 (_visit_admonition), :3707-3765 (note/warning/hint precedent)
def visit_todo_node(self, node) -> None:
    """Visit a todo_node (sphinx.ext.todo). Converts to #task[] (gentle-clues)."""
    self._visit_admonition(node, "task", custom_title="Todo")

def depart_todo_node(self, node) -> None:
    """Depart a todo_node."""
    self._depart_admonition()
```
Note: `todo_node` already carries a `nodes.title` child (Sphinx inserts it at directive-parse
time — see `sphinx/ext/todo.py` `Todo.run()`, `todo.insert(0, nodes.title(text=_('Todo')))`).
Because `todo_node` is an `nodes.Admonition` subclass, the translator's existing
`visit_title`/`depart_title` admonition branch (`isinstance(node.parent, nodes.Admonition)`,
translator.py:441) fires automatically and buffers this title into `_pending_admonition_title`,
which `_depart_admonition` prefers over `custom_title` (translator.py:3692-3696). This means the
rendered title comes from the *dynamic* path (the node's own title child), not the static
`custom_title="Todo"` argument — both happen to render "Todo" in the non-i18n case, so behavior
matches D-01's intent, but a test asserting internals (not just PDF text) should target the dynamic
path.

### Pattern 2: Inline-wrap delegation for `manpage` (MAN-01)
**What:** `manpage` (a `sphinx.addnodes.manpage`, subclassing `docutils.nodes.Inline` +
`FixedTextElement`) needs to wrap its single child in italic (`emph`) exactly like `visit_emphasis`
already does for `*emphasis*` rST markup — same separator/paragraph/list-item/inline-concat-context
handling is required for correctness in every context manpage roles can appear (paragraphs, list
items, table cells, definition-list terms).
**When to use:** Any inline node needing the SAME rendering as native `*emphasis*` with zero
additional attributes/state.
**Example (delegation avoids duplicating ~50 lines of state machinery):**
```python
# Source: typsphinx/translator.py:950-1023 (visit_emphasis/depart_emphasis, the pattern reused)
def visit_manpage(self, node) -> None:
    """Visit a manpage node (:manpage: role). Renders as italic, Sphinx-HTML-faithful (D-02)."""
    self.visit_emphasis(node)

def depart_manpage(self, node) -> None:
    """Depart a manpage node."""
    self.depart_emphasis(node)
```
If the planner prefers NOT to delegate (e.g. to keep `manpage` semantically distinct in the
diff/history), a bespoke pair MUST still replicate: `_add_paragraph_separator()`,
`_enter_inline_concat_element()`/`_exit_inline_concat_element()` pairing, the
`self.in_list_item`/`list_item_needs_separator` save-swap-restore dance, and the
`"#" if self._in_markup_mode else ""` prefix. Delegation is the lower-risk option and is the
recommended default.

**Verified node-child shape:** `sphinx/roles.py` `Manpage.run()` sets the node's single child to a
plain `nodes.Text(text)` UNLESS the project's `manpages_url` config is set, in which case the child
is a `nodes.reference` instead (out of scope per D-02a; not present in this project's `docs/conf.py`
or in the corpus's `doc/conf.py` — confirmed via `grep`, no matches for `manpages_url` in either).

### Pattern 3: Length-bearing site wiring (LEN-01)
**What:** `_convert_length_to_typst` already exists and is fully correct (Phase 11); LEN-01 is
audit + wire-in, not a rewrite. The audit is CLOSED — confirmed via `grep -rn
"length_or_percentage_or_unitless\|length_or_unitless"` across the entire installed docutils
`parsers/rst/directives/` tree: only `images.py` (image width/height, figure figwidth) and
`tables.py` (table/csv-table/list-table width — all three converge on the single `nodes.table`
type via `Table.set_table_width()`) ever populate a length-normalized attribute. No other docutils
directive needs wiring.
**When to use:** Any node visitor emitting a Typst length from a docutils length-normalized
attribute (`node["width"]`/`node["height"]`).
**Example (figure — new code; mirrors `visit_image`'s existing width/height block at
translator.py:2510-2518):**
```python
# Source: typsphinx/translator.py:2472-2520 (visit_image, the reference pattern)
def visit_figure(self, node) -> None:
    ...  # existing figure setup unchanged
    figwidth = node.get("width")  # set by docutils' Figure directive from :figwidth:
    converted = self._convert_length_to_typst(figwidth) if figwidth else None
    if converted is not None:
        self.add_text(f"block(width: {converted})[\n")  # Typst figure() rejects width: directly
    if node.get("ids"):
        self.add_text("[#figure(\n")
    else:
        self.add_text("figure(\n")
    # depart_figure must close the matching "]" if converted is not None
```
**Verified constraint (real compile):** Typst's `figure()` and `table()` functions do NOT accept a
`width:` argument — `typst.compile()` on `#figure(width: 50%, [x], caption: [c])` fails with
`unexpected argument: width`; same failure for `table(columns: 2, width: 50%, ...)`. The verified
working pattern is wrapping the WHOLE call: `#block(width: 50%)[#figure(...)]` /
`#block(width: 50%)[#table(...)]` — both confirmed to compile via a real `typst.compile()` in this
session.

### Anti-Patterns to Avoid
- **Duplicating px/pc arithmetic at a new call site:** D-03b requires exactly one implementation.
  Any new site must call `self._convert_length_to_typst(value)`, never reimplement the `* 0.75` /
  `* 12` math locally.
- **Passing `width:` directly to `figure()`/`table()`:** confirmed a hard Typst compile error
  (`unexpected argument: width`) — always wrap in `#block(width: ...)[...]` instead.
- **Assuming `custom_title="Todo"` is what renders the title text:** `todo_node`'s own title child
  wins via the dynamic buffer-swap path; don't build a test that depends on the static path firing.
- **Writing a bespoke `visit_manpage` that skips the inline-concat-context pairing:** will silently
  break manpage roles used inside list items / table cells / definition-list terms (a "+ "-separator
  leak or a missing separator) — exactly the class of "silent mis-render" this milestone's Phase 17
  audit exists to catch. Delegate to `visit_emphasis`/`depart_emphasis` instead.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Admonition-style box rendering | A custom Typst `block()`/`rect()` construction for the todo box | `_visit_admonition(node, "task", custom_title="Todo")` + `_depart_admonition()` | Already exists, already handles the id-anchor / list-item-separator / dynamic-title machinery correctly for 12 other admonition types. |
| Italic inline wrapping with correct separator handling | A new state machine for manpage's paragraph/list-item/concat-context bookkeeping | Delegate to `visit_emphasis`/`depart_emphasis` | The existing method already handles every context manpage can appear in (paragraphs, list items, def-list terms, table cells) — reinventing it risks missing an edge case. |
| CSS length parsing/conversion | A second `_convert_length_to_typst`-like function scoped to figure/table | The existing `self._convert_length_to_typst()` (translator.py:3009) | It is already correct (px=0.75pt, pc=12pt, %/em/pt/cm/mm/in passthrough, unknown→drop+warn) — D-03b explicitly forbids a second implementation. |

**Key insight:** All three "problems" in this phase already have a correct, tested solution
elsewhere in `translator.py`. The entire phase is properly scoped as "wire existing machinery to two
more node types + N more call sites," not "build new rendering logic."

## Common Pitfalls

### Pitfall 1: `todo_include_todos` config gating (TODO-01)
**What goes wrong:** Sphinx's own HTML5 (`visit_todo_node`) and LaTeX (`latex_visit_todo_node`)
writers both check `self.config.todo_include_todos` (default `False`, set via
`app.add_config_value('todo_include_todos', False, ...)` in `sphinx/ext/todo.py`) and `raise
nodes.SkipNode` — skipping the todo body entirely — when it is `False`. Every other official Sphinx
builder (text, man, texinfo) behaves the same way. If typsphinx's new `visit_todo_node` ALWAYS
renders the body regardless of this config, it diverges from every other builder's fidelity contract
— a class of bug this very milestone (Phase 17/18) exists to hunt down elsewhere.
**Why it happens:** `todo_node` is unconditionally inserted into the doctree by `Todo.run()`
regardless of config — the config check happens per-builder, at render time, not at parse time. It
is easy to miss this because the node's mere *presence* in the doctree looks the same either way.
**How to avoid:** The planner should decide explicitly whether `visit_todo_node` mirrors Sphinx's
official builders (`raise nodes.SkipNode` when `not self.config.todo_include_todos`) or always
renders. Recommendation: mirror the official builders for fidelity-consistency — this also matches
how the real Sphinx `doc/` corpus is configured (`todo_include_todos = 'READTHEDOCS' not in
os.environ`, confirmed in `doc/conf.py` at the corpus's pinned tag — effectively `True` for local/CI
runs, which is why the audit saw ×10 `todo_node` warnings). The GATE-01 fixture for this phase MUST
explicitly set `todo_include_todos = True` in its `conf.py`, mirroring the corpus, or the fixture
won't exercise the render path at all (regardless of which gating choice is made).
**Warning signs:** A fixture whose `conf.py` omits `todo_include_todos` and still expects rendered
todo content in the PDF — will pass today (if the new handler ignores the config) but silently
diverges from HTML/LaTeX output for any user who has NOT set `todo_include_todos = True`.

### Pitfall 2: `custom_title` is inert for `todo_node`, unlike other admonitions
**What goes wrong:** Someone debugging "why does the todo title say X" might assume
`custom_title="Todo"` is the source of the rendered title and try to change it there, when the
actual value comes from the node's own `nodes.title` child (dynamic path, always wins over
`custom_title` per `_depart_admonition`'s `if self._pending_admonition_title: ... elif
self._custom_admonition_title: ...`).
**Why it happens:** Every OTHER admonition this helper is reused for (`note`, `warning`, `hint`,
etc.) has NO title child — so `custom_title` is normally the only source of the title, making
`todo_node` a surprising exception.
**How to avoid:** Document this inline (a one-line comment on `visit_todo_node`) so future
maintainers don't waste time. Functionally harmless for D-01 (both paths render "Todo" in English,
non-i18n builds) — no code change required, just documentation.
**Warning signs:** A locale/i18n build where Sphinx's gettext catalog translates "Todo" differently
than a hypothetical hardcoded string would — the dynamic path (correctly) follows the locale; if
someone "fixes" this by removing the title child before it reaches `visit_title`, they'd break
locale-correctness.

### Pitfall 3: `figure()`/`table()` reject `width:` as a direct keyword argument
**What goes wrong:** The naive, seemingly obvious wiring — `figure(..., width: 50%)` or
`table(..., width: 50%, ...)` — is a Typst compile-time error (`unexpected argument: width`),
verified via a real `typst.compile()` in this session. This would abort the ENTIRE PDF build for any
document using `:figwidth:` or table `:width:`, i.e. a NEW fatal-compile regression, not a silent
mis-render — directly contradicting the milestone invariant of shipping only low-risk, additive
changes.
**Why it happens:** Typst's built-in `figure()`/`table()` functions don't expose a `width`
parameter (unlike `image()`, `block()`, or `rect()`, which do).
**How to avoid:** Wrap the whole `figure(...)`/`table(...)` call in `#block(width:
<converted>)[...]` — verified working via real compile in this session for both cases.
**Warning signs:** Any code path that pattern-matches `visit_image`'s `add_text(f", width:
{converted_width}")` line and copies it into `visit_figure`/`depart_table` verbatim — this pattern
is specific to `image()`, which DOES accept `width`/`height` kwargs; it does not generalize to
`figure()`/`table()`.

### Pitfall 4: `emph({...})`/manpage delegation inside a figure caption or other markup-mode context
**What goes wrong:** `visit_emphasis` conditionally emits `#emph({` when `self._in_markup_mode` is
`True` (e.g. inside a figure caption, per translator.py:2546/2557) and bare `emph({` otherwise. A
`manpage` role used inside a figure caption relies on this toggle firing correctly; a bespoke
non-delegating `visit_manpage` that hardcodes `#emph[` (as CONTEXT.md's literal D-02 phrasing
suggests) would break in code-mode contexts (double `#` or a markup/code-mode mismatch parse error).
**Why it happens:** The translator is NOT uniformly in one mode — it toggles between Typst code mode
(most of the document body) and markup mode (figure captions, a few other spots) via
`self._in_markup_mode`.
**How to avoid:** Delegate to `visit_emphasis`/`depart_emphasis` (Pattern 2) so the existing,
already-correct prefix logic is reused automatically.
**Warning signs:** A fixture that only tests manpage inside a plain paragraph (code-mode default)
would NOT catch this bug — the GATE-01 fixture should include at least one manpage-in-caption or
manpage-in-list-item case to exercise the mode toggle and separator state machine.

## Code Examples

### Real-compile verification: `task(title: "Todo")` compiles and the override wins
```python
# Verified this session via typst-py against the pinned gentle-clues 1.3.1
# (real typst.compile() -> PDF -> pypdf text extraction, not a string-agreement assert)
import typst
from pypdf import PdfReader

# test.typ:
#   #import "@preview/gentle-clues:1.3.1": *
#   #task(title: "Todo")[Some body content here for override test.]
#   #task[Some body content here for default test.]
typst.compile("test.typ", output="test.pdf")
text = PdfReader("test.pdf").pages[0].extract_text()
# text == 'Todo\nSome body content here for override test.\nTask 2\n...'
#           ^^^^ explicit override wins, no duplicate-argument error
#                                                          ^^^^^^ default auto-title +
#                                                                 shared task counter
#                                                                 (increments even when
#                                                                 the title is overridden)
```

### Real-compile verification: `figure()`/`table()` reject `width:`, `block(width:)` wrapper works
```python
# Verified this session via typst-py
import typst

# FAILS: "unexpected argument: width"
typst.compile_string_would_fail = """
#figure(width: 50%, [x], caption: [c])
"""

# WORKS:
typst.compile_string_works = """
#block(width: 50%)[
  #figure([x], caption: [c])
]
"""
```

## State of the Art

No external ecosystem drift applies here — this is entirely internal-codebase mechanics (existing
translator patterns + a version-pinned, already-cached Typst package). N/A for this phase.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Delegating `visit_manpage`→`visit_emphasis` (passing a `manpage` node instance where the type hint says `nodes.emphasis`) is safe because neither method performs an `isinstance` check on the node argument. | Pattern 2 | LOW — verified by reading the full body of both methods this session (no `isinstance(node, ...)` calls found); if a future refactor of `visit_emphasis` adds a type-check, this would need updating, but nothing in the current code does. Tag as VERIFIED (source read), not assumed — kept in this log only as a forward-compatibility note. |
| A2 | Recommending `visit_todo_node` gate on `config.todo_include_todos` (mirroring Sphinx's official builders) rather than always rendering. | Pitfall 1 / Open Questions | MEDIUM — this is a design recommendation, not a locked CONTEXT.md decision. If the planner chooses "always render" instead, it must be a deliberate, documented choice (not an oversight), since it diverges from every official Sphinx builder's behavior and could itself become an AUD-01 (Phase 17) finding if not caught here. |

**If this table is empty:** N/A — two items above need explicit planner sign-off; all other claims
in this document were verified via direct source reads or real `typst.compile()` runs this session.

## Open Questions

1. **Should `visit_todo_node` gate on `self.config.todo_include_todos`?**
   - What we know: Every official Sphinx builder (HTML, LaTeX, text, man, texinfo) skips the todo
     body (`raise nodes.SkipNode`) when this config is `False` (the default). The real corpus
     (`doc/conf.py`) effectively sets it `True` for local/CI runs, which is why the audit saw ×10
     todo_node instances with content to warn about.
   - What's unclear: CONTEXT.md's D-01/success-criteria don't mention this config at all — SC#1 says
     "renders its body content... instead of being silently dropped," which is compatible with
     either "always render" or "render only when todo_include_todos is True."
   - Recommendation: Gate on `todo_include_todos` for fidelity-consistency with every other Sphinx
     builder (this is directly in the spirit of the milestone's "renders faithfully to the source"
     core value). The GATE-01 fixture must set `todo_include_todos = True` explicitly regardless of
     which choice is made, so the render path is actually exercised.

2. **Exact fixture layout for LEN-01's figure/table width cases.**
   - What we know: `tests/fixtures/figure_length_render_gate/` already exists and tests IMAGE
     `:width:` nested inside a `.. figure::` (not figure's own `:figwidth:`). A genuinely new case
     (figure `:figwidth:` and table `:width:`) is needed.
   - What's unclear: Whether to extend `figure_length_render_gate` with new figwidth cases or create
     a fresh fixture directory, and whether table-width gets its own fixture or shares one.
   - Recommendation: Left to Claude's Discretion per CONTEXT.md — extending the existing
     `figure_length_render_gate` fixture with figwidth cases (co-located with the existing
     image-width cases, since both exercise the same `_convert_length_to_typst` helper) and adding a
     new `table_width_render_gate` fixture (table has a structurally different node/visitor) is a
     reasonable default split.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst` (typst-py) | GATE-01 real-compile fixtures (SC#4) | ✓ | Confirmed via local venv `typst-py` package, matches STATE.md's noted "typst 0.15.0 present" | — |
| `pypdf` | PDF text-extraction assertions in `tests/test_pdf_render_gate.py` (existing pattern, reused) | ✓ | Confirmed importable in project venv | — |
| `@preview/gentle-clues:1.3.1` (Typst package cache) | TODO-01's `task` clue | ✓ | Confirmed present at `~/.cache/typst/packages/preview/gentle-clues/1.3.1/`, exact pinned version | — |
| Sphinx corpus clone (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`) | GATE-03/full-corpus regression (later phases, referenced for context) | ✓ | Already cloned, `doc/conf.py` confirmed to set `todo_include_todos` effectively `True` locally | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), existing `tests/test_pdf_render_gate.py` real-compile gate pattern |
| Config file | `pyproject.toml` |
| Quick run command | `pytest tests/test_pdf_render_gate.py -k todo_render_gate` (or `manpage_render_gate` / `figure_length` / new table-width test name, once written) |
| Full suite command | `pytest -m "not slow"` (excludes `test_corpus_gate.py`'s slow full-corpus clone-and-compile test) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TODO-01 | `.. todo::` renders as a `task`-styled box with "Todo" title in the compiled PDF | render-gate (real `typst.compile()` + pypdf text extraction) | `pytest tests/test_pdf_render_gate.py::TestClass::test_todo_pdf_renders_body_and_title -x` | ❌ Wave 0 — new fixture `tests/fixtures/todo_render_gate/` + new test function needed |
| MAN-01 | `:manpage:` renders as italic literal text (e.g. `ls(1)`) in the compiled PDF, including inside a figure caption / list item to exercise the mode-toggle | render-gate | `pytest tests/test_pdf_render_gate.py::TestClass::test_manpage_pdf_renders_italic_text -x` | ❌ Wave 0 — new fixture `tests/fixtures/manpage_render_gate/` + new test function needed |
| LEN-01 | `.. figure:: :figwidth:` and `.. table:: :width:` convert px→pt (and drop unknown units with one warning) and produce a compilable PDF | render-gate | `pytest tests/test_pdf_render_gate.py::TestClass::test_figure_figwidth_pdf_converts_and_compiles -x` / `test_table_width_pdf_converts_and_compiles -x` | ❌ Wave 0 — extend `figure_length_render_gate` fixture with figwidth cases; new `table_width_render_gate` fixture (or extend an existing table fixture) |

### Sampling Rate
- **Per task commit:** `pytest tests/test_pdf_render_gate.py -k "todo or manpage or figwidth or table_width"`
- **Per wave merge:** `pytest -m "not slow"`
- **Phase gate:** Full suite green (`pytest -m "not slow"`, plus `mypy typsphinx/`, `ruff check .`,
  `black --check .` per CLAUDE.md commands) before `/gsd-verify-work`. `tests/test_corpus_gate.py`
  (`slow`) is a good manual sanity check locally (corpus already cached at
  `~/.cache/typsphinx-corpus-gate`) but is not required per-commit.

### Wave 0 Gaps
- [ ] `tests/fixtures/todo_render_gate/conf.py` + `index.rst` — `sphinx.ext.todo` extension enabled,
      `todo_include_todos = True` set explicitly (mirroring the real corpus's effective config),
      one `.. todo::` block with a paragraph body.
- [ ] `tests/fixtures/manpage_render_gate/conf.py` + `index.rst` — at least one `:manpage:` role in
      a plain paragraph AND at least one inside a figure caption or list item (to exercise the
      `_in_markup_mode` toggle / inline-concat-context pairing per Pitfall 4).
- [ ] Extend `tests/fixtures/figure_length_render_gate/index.rst` with `:figwidth:` cases (px,
      unsupported-unit-drop) alongside the existing image-`:width:` cases.
- [ ] New `tests/fixtures/table_width_render_gate/` (or extend an existing table fixture) —
      `.. table:: :width:` and/or `.. list-table:: :width:` cases.
- [ ] New test functions in `tests/test_pdf_render_gate.py` for each of the above, following the
      existing `test_figure_length_pdf_converts_px_and_drops_unknown_unit` pattern (real compile +
      pypdf text/`.typ`-content assertions, never string-agreement-only).

*(No framework install needed — pytest, typst-py, and pypdf are all already project dependencies.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | This phase touches only local docutree→Typst text generation; no auth surface. |
| V3 Session Management | No | N/A — build-time tool, not a service. |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal | The todo body and manpage literal text are author-controlled RST that flow into generated Typst source via the EXISTING, unmodified `visit_Text`/`escape_typst_string` escaping regime — no new unescaped string interpolation is introduced by any of the three changes. The one new interpolation point is the converted length value (`f", width: {converted_width}"` / `f"block(width: {converted})["`), which is produced entirely by `_convert_length_to_typst`'s own regex-validated, numeric-only output (`re.fullmatch(r"(-?[0-9.]+)([a-zA-Zµ%]*)", value)`, already in production since Phase 11) — not raw author text. |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Typst source injection via unescaped todo/manpage body text | Tampering | Already mitigated by the existing `visit_Text`/`escape_typst_string` regime, reused unmodified — both new handlers route all leaf text through the same chain as every other node type. |
| Fatal compile-abort from `figure(width:)`/`table(width:)` misuse as a denial-of-service vector | Denial of Service (build-time) | Confirmed and closed by this research: the verified `#block(width: ...)[...]` wrapper pattern avoids the `unexpected argument: width` fatal entirely — Pitfall 3 documents this explicitly so the planner does not reintroduce it. |
| Malformed/unsupported length unit reaching Typst unconverted (regression of the original FIG-01 fatal) | Tampering / Denial of Service | Already mitigated: `_convert_length_to_typst` drops unsupported units with exactly one `logger.warning` rather than emitting them verbatim (D-02 from Phase 11) — LEN-01 preserves this contract at every newly-wired site (D-03b), no new risk introduced. |

## Sources

### Primary (HIGH confidence — verified directly this session)
- `typsphinx/translator.py` (repository source, read directly) — `_convert_length_to_typst`
  (:3009-3067), `visit_image`/`depart_image` (:2472-2529, the width/height wiring reference),
  `visit_figure`/`depart_figure` (:1868-1932), `visit_table`/`depart_table` (:2118-2210+),
  `_visit_admonition`/`_depart_admonition` (:3643-3810, incl. every `note`/`warning`/`hint`/etc.
  precedent), `visit_emphasis`/`depart_emphasis` (:950-1023), `visit_abbreviation`/
  `depart_abbreviation` (:4047-4060+), `_enter_inline_concat_element`/`_exit_inline_concat_element`
  (:852-891), `visit_title`'s admonition-aware branch (:407-457), `_in_markup_mode` toggling
  (:2546, :2557).
- `~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/predefined.typ` and `clues.typ` (the exact
  pinned Typst package, read directly from local cache) — confirms `task` clue exists, its exact
  implementation (`title: _get-title-for("task") + get-task-number(), ..args`), and `clue()`'s base
  signature.
- `.venv/lib/python3.13/site-packages/sphinx/ext/todo.py` (Sphinx 9.1.0 installed package, read
  directly) — `todo_node` class definition (`nodes.Admonition, nodes.Element`), `Todo.run()`
  (title-child insertion), `visit_todo_node`/`latex_visit_todo_node` (the `todo_include_todos` gate),
  `app.add_config_value('todo_include_todos', False, ...)`.
- `.venv/lib/python3.13/site-packages/sphinx/roles.py` (Sphinx 9.1.0 installed package, read
  directly) — `Manpage.run()` (:534-550), confirms the node's child is `nodes.Text` unless
  `manpages_url` is configured.
- `.venv/lib/python3.13/site-packages/sphinx/addnodes.py` (read directly) — `manpage` class MRO
  (`Inline`, `FixedTextElement`, `TextElement`).
- `.venv/lib/python3.13/site-packages/docutils/parsers/rst/directives/images.py` and `tables.py`
  (installed docutils package, read directly) — `Image`/`Figure` option specs and `Figure.run()`'s
  `figure_node['width'] = figwidth` assignment; `Table.set_table_width()` and its three callers
  (`RSTTable`, `CSVTable`, `ListTable`).
- Full-tree `grep` of `.venv/lib/python3.13/site-packages/docutils/parsers/rst/directives/*.py` for
  `length_or_percentage_or_unitless`/`length_or_unitless` — exhaustively confirms only
  `images.py`/`tables.py` use these normalizers (closes the LEN-01 audit with certainty).
- Real `typst.compile()` runs (this session, via the project's own `typst-py` dependency, format
  PDF, text-extracted with `pypdf`) — confirmed `task(title: "Todo")[...]` compiles and the override
  wins over the internal default title (no duplicate-argument error); confirmed `figure(width:
  ...)`/`table(..., width: ...)` both fail with `unexpected argument: width`; confirmed
  `#block(width: ...)[#figure(...)]` / `#block(width: ...)[#table(...)]` both compile successfully.
- `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc/conf.py` (the actual corpus fixture used by
  `tests/test_corpus_gate.py`, read directly) — confirms
  `todo_include_todos = 'READTHEDOCS' not in os.environ` and no `manpages_url` setting.
- `tests/fixtures/figure_length_render_gate/` and `tests/test_pdf_render_gate.py` (repository
  source, read directly) — the existing GATE-01 fixture + real-compile-and-pypdf-extract test
  pattern this phase's new fixtures/tests should follow.
- `.planning/phases/14-footnotes-doctree-pre-pass/14-RESEARCH.md` (prior phase, read for house
  style) — Security Domain section format precedent for this codebase.

### Secondary (MEDIUM confidence)
None — every claim in this document was verified directly against primary source (installed package
code, local Typst package cache, or a real `typst.compile()` run) this session, not sourced from web
search or training-data recall.

### Tertiary (LOW confidence)
None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; the one referenced package (gentle-clues) was
  inspected at its exact pinned version directly from the local cache.
- Architecture: HIGH — every pattern (admonition reuse, emphasis delegation, length-site wiring) was
  verified by reading the actual existing implementation, not inferred from CONTEXT.md's summary
  phrasing alone (which in two places — `#emph[` and the D-01a fallback trigger condition —
  understated the actual implementation complexity/nuance).
- Pitfalls: HIGH — all four documented pitfalls were either confirmed by a real `typst.compile()`
  failure/success this session or by reading Sphinx/docutils source directly; none are speculative.

**Research date:** 2026-07-16
**Valid until:** Stable for the life of this pinned dependency set (gentle-clues 1.3.1, docutils/
Sphinx versions unchanged) — re-verify only if `@preview/gentle-clues` is ever bumped (guarded by
the existing `test_preview_version_sync.py`) or if the Sphinx/docutils pin changes.

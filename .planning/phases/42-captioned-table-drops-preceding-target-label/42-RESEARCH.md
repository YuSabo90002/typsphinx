# Phase 42: Captioned Table Drops Preceding Target Label - Research

**Researched:** 2026-08-03
**Domain:** docutils→Typst translator anchor/label emission (`typsphinx/translator.py`), GATE-01
render-gate test conventions, release-artifact reconciliation
**Confidence:** HIGH

## Summary

The defect is **reproduced and root-caused in this session** (not merely re-stated from the owner's
report or the discuss-phase throwaway measurement). A standalone target immediately before a
captioned table propagates its id onto `node["ids"]` (confirmed directly from the pickled doctree:
`['tbl-name', 'tbl-target']`), and a real `sphinx-build -b typstpdf` aborts with the exact fatal
`TypstError: label \`<index:tbl-target>\` does not exist in the document`. The mechanism is exactly
the hypothesis carried into this phase: `depart_table`'s trailing
`self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))` call (line 3341) fires while
`self.in_table` is still `True` (cleared only at line 3351), and `add_text` (lines 423-437) routes
*every* text append into `self.table_cell_content` whenever `self.in_table` is `True` — so the
anchor markup is silently appended to a buffer that is discarded (`del self.table_cell_content` at
line 3367-3368) rather than reaching `self.body`. `depart_figure` is not affected because `add_text`
never checks `self.in_figure` at all — only `self.in_table` gates the buffer diversion, and no other
call site in the file combines a body-level (non-cell) anchor emission with a still-set
buffer-diverting flag. This was verified by patching the file locally (single-line-move: run the
skipped-id anchor call after `self.in_table = False`), confirming all four D-01 shapes now compile
clean with both labels present and no duplicate-label fatal, and that the entire existing test suite
(805 passed / 1 skipped — identical to Phase 41's own recorded baseline) stays green with the patch
in place. The patch was then reverted (`git checkout -- typsphinx/translator.py`) before this file
was written — **no production code was changed by this research session**.

**Primary recommendation:** implement D-05 as a minimal, surgical move — hoist the existing
`_emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))` call (currently line 3341, inside the
`if self.table_caption:` branch) to fire *after* `self.in_table = False` (currently line 3351),
gated on a `was_captioned` boolean captured before `self.table_caption` is reset to `None`. Nothing
else in `depart_table`, `_emit_id_anchors`, or `add_text` needs to change. Build the GATE-01 fixture
as a **new** dedicated fixture directory (not an extension of the already-green
`captioned_table_render_gate/`), mirroring the existing `paragraph_propagated_target_render_gate` /
`desc_container_propagated_target_render_gate` "one fixture per fixed node type" convention, because
this phase's RED is a real compile fatal that would otherwise contaminate the already-passing
sentinel-count assertions in the existing captioned-table gate during the RED-recording window.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| docutils doctree → Typst markup translation (id/anchor emission) | Translator (`typsphinx/translator.py`, in-process Python, not a network tier) | — | This is a single-process document-compiler pipeline (doctree → string → `.typ` → optionally `typst.compile()`), not a client/server or browser application — the "tier" concept from web architectures maps loosely onto "which visitor method owns which emission." `depart_table`/`_emit_id_anchors`/`add_text` are all the same tier: in-process translator state. |
| GATE-01 regression-fixture authoring | Test harness (`tests/fixtures/*`, `tests/test_*_render_gate.py`) | — | Fixtures + pytest modules are the project's standing acceptance-gate mechanism; this phase adds to that layer, not to the translator's public API. |
| Release-artifact reconciliation (CHANGELOG, invariant sweep) | Release tooling / planning docs (`CHANGELOG.md`, `.planning/`) | — | SC#6 touches documentation/process artifacts, not runtime code. |

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TBL-03 | A captioned table immediately preceded by a standalone target emits Typst labels for **both** ids, so the surviving reference resolves; caption-less path stays byte-for-byte unchanged; keeps the classic `TypstError` GATE-01 RED. | Root cause confirmed by direct doctree inspection + real `typst.compile()` failure (see "The exact code path" below); fix mechanically verified working for all four D-01 shapes with the full suite green; caption-less byte-invariance already covered by the existing `TestTableInListItemRenderGate`'s top-level control table, which passed unchanged under the experimental patch. |

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: the RED gate fixture matrix covers all four measured-failing shapes.** They are: a
  target plus a `:name:`-carrying captioned table; a target plus a captioned table with no
  `:name:`; a captioned table inside a bullet-list item; and two consecutive standalone targets
  before one captioned table. All four were observed aborting a real compile during this
  discussion. The caption-less table case rides along as the byte-invariance control.

- **D-02: the id that owns the figure label does not change.** The first id stays the figure's
  own `<label>` and the remaining ids stay `metadata(none)` anchors, exactly as the code does
  today. Only the fact that the remaining ids never reach the body is fixed. Rationale — because
  typsphinx renders references as `link(<label>, …)`, the jump resolves against either anchor
  form, so promoting the human-authored id would change existing output for no functional gain.

- **D-03: the GREEN side asserts a successful compile plus the structure of the emitted output.**
  Both labels must be present and no label may be defined twice, so the fix cannot silently trade
  the dangling label for the duplicate-label fatal the in-code TBL-02 rationale warns about.

- **D-04: the caption-less path's byte invariance is proven by an empty two-build diff.** Two
  `sphinx-build -b typst` runs at a named pre-fix commit and a named post-fix
  commit, diff recorded in an evidence file. Same method as Phase 36's SC#2, not a golden file
  committed to the repo.

- **D-05: the fix is a call-ordering change inside the table departure handler only.** The
  `_emit_id_anchors` call moves after the point where the in-table flag is cleared. No new
  argument on the shared helper, no change to `add_text`, no other call site touched.

- **D-06: a repo-wide sweep runs for the same misrouting class.** Findings outside the image
  path are filed as todos and not fixed here; a finding in the image path **is** fixed inside
  this phase (owner's condition, stated verbatim during discussion). The sweep's result is
  recorded as evidence either way, including a null result.

- **D-07: the image-path measurement is re-taken formally inside the sweep.** The measurement
  made during this discussion is reference material only and is not admissible as phase evidence.

- **D-08: the whitespace-only-title branch divergence is filed as a todo.** The visit-side and
  depart-side captioned checks use different axes, so a table whose title renders to an empty
  string may emit no anchor on either path. Whether rST can even reach that state is unverified.
  Nothing in this phase is changed for it.

- **D-09: a permanent figure regression gate is added.** Phase 25 modelled the table path on the
  figure path, so a durable gate stops a future table-side change from being copied back into a
  broken figure path. This also discharges SC#2.

- **D-10: the figure gate covers the three measured shapes.** A `:name:`-carrying figure with a
  preceding target, a figure with no `:name:` and a preceding target, and a figure inside a
  bullet-list item. The two-consecutive-targets shape is not measured for figures and is not
  required.

### Claude's Discretion

- **SC#6 reconciliation mechanics.** The owner accepted the proposed handling without further
  discussion: add the TBL-03 line directly to the CHANGELOG's unreleased `## [0.7.0]` section;
  re-measure Phase 41's SC#4 invariant sweep over a SHA range that includes Phase 42 and write
  the result as a **new** evidence file under this phase's directory rather than editing any
  `41-*` artifact; and if `phase.complete` flips the REL-04 / REL-05 checkboxes or traceability
  rows, revert that before committing (Phase 41 hit this exact behaviour on 2026-08-03).
- Fixture file layout, test module naming, plan and commit granularity, and whether the new
  shapes extend the existing captioned-table fixture or get their own.

### Deferred Ideas (OUT OF SCOPE)

- The whitespace-only-title branch divergence between the table visit and departure handlers —
  todo to be filed by this phase, not fixed here (D-08).
- Any non-image misrouting the repo-wide sweep discovers — todo only (D-06).
- Promoting the human-authored id to the figure label instead of the first id — rejected for this
  phase (D-02); revisit only if a `:numref:` requirement ever needs it.

## Project Constraints (from CLAUDE.md)

- **Worktree isolation is the standing execution mode**, not conditional on this phase's low
  parallelism. Every executor must run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra
  dev` before anything else in its worktree, then invoke every subsequent command through `uv run`
  (e.g. `uv run pytest`, `uv run python -m sphinx …`). This is required because the main `.venv`'s
  PEP-660 editable finder resolves `import typsphinx` to the MAIN checkout's absolute path — a
  worktree that skips this step edits files correctly but tests against the unchanged main-tree
  package.
- **Always invoke Sphinx as `sys.executable -m sphinx` / `uv run python -m sphinx`**, never a bare
  `sphinx-build` or `uv run sphinx-build` — this project's NixOS dev sandbox has a stray non-Nix
  `uv` shim that shadows the correct one for subprocess children, an already-documented hazard every
  existing render-gate test module works around identically (see `_run_sphinx_build_typst` in
  `tests/test_pdf_render_gate.py`).
- **Black (88 cols), ruff, mypy** must all pass clean (`black --check .`, `ruff check .`, `mypy
  typsphinx/`) — this phase's fix is a small code-location move inside `depart_table`, well within
  normal linting.
- **N802 is ignored project-wide** for docutils' PascalCase visitor method names — irrelevant here,
  no new visitor method is added.
- **Do not modernize typing imports** (`Dict`/`List` → `dict`/`list`) — irrelevant to this phase's
  diff, but a reminder not to "clean up" nearby `List`/`Tuple` imports in `translator.py` while
  editing `depart_table`.
- This phase does not touch `@preview` package versions, `writer.py`, or `template_engine.py` — the
  fix is confined to `typsphinx/translator.py`.

## Architectural Responsibility Map — commit-graph note

Not applicable beyond the table above; this phase has no browser/frontend/API-tier distinctions to
map (see the earlier Architectural Responsibility Map section for the actual mapping used).

## 1. The exact code path (verified against the current tree, not the stale todo line numbers)

The pending todo (`2026-08-03-captioned-table-drops-preceding-target-label.md`) cites line numbers
from an earlier tree snapshot (`depart_table` at 3249, self-anchor at 3318-3328, `_emit_id_anchors`
call at 3341). **These happen to still match the current tree** (re-verified this session against
HEAD `ae13907`), but do not assume they will stay stable — the file is ~6900 lines and grows every
phase.

### `visit_table` (line 3149) — the captioned pre-check and why it is safe

```python
# typsphinx/translator.py:3149-3175 (verbatim, current tree)
def visit_table(self, node: nodes.table) -> None:
    ...
    # A propagated explicit target can land its id on this table; anchor it
    # so a same-document link(<id>, ...) resolves (no ids -> no-op). Emitted
    # while self.in_table is still False, so add_text routes to the real
    # body (not a stale table_cell_content buffer).
    #
    # TBL-02 (Phase 25, Critical Pitfall 3): a CAPTIONED table instead
    # self-anchors ids[0] as its own figure `<label>` postfix in
    # depart_table, mirroring depart_figure. Anchoring it here TOO would
    # define that id TWICE, aborting the whole compile at Typst's
    # semantic pass with "label ... occurs multiple times" -- a real
    # fatal invisible to any translator-only unit test. The doctree is
    # already fully built at visit_table time (docutils constructs the
    # whole tree before any visiting begins), so the captioned pre-check
    # is reliable here, before the title has even been visited. Skip the
    # call entirely for a captioned table; depart_table calls it with
    # skip_ids={ids[0]} AFTER emitting the figure's own <label>.
    # Non-captioned tables keep this unconditional call, unchanged.
    is_captioned = bool(node.children) and isinstance(node.children[0], nodes.title)
    if not is_captioned:
        self._emit_id_anchors(node)
    ...
    self.in_table = True
    self.table_cells = []
    self.table_colcount = 0
    self.table_colwidths = []
```

This call site is **not** the bug: it fires before `self.in_table = True`, so `add_text` routes to
`self.body` correctly. It is deliberately skipped for a captioned table because `depart_table`
handles that case later (comment states the contract explicitly).

### `depart_table` (line 3249) — the captioned branch, the self-anchor, and the bug

```python
# typsphinx/translator.py:3249-3368 (verbatim, current tree)
def depart_table(self, node: nodes.table) -> None:
    ...
    if self.table_colcount > 0:
        ...
        table_code = "".join(table_parts)               # line 3302

        if self.table_caption:                            # line 3304 -- captioned branch
            figure_code = (
                f"figure(\n{table_code},\n"
                f"  caption: {{{self.table_caption}}},\n"
                f"  kind: table\n)"
            )
            if node.get("ids"):                            # line 3318
                label = self._namespace_label(
                    self._current_docname(), node["ids"][0]
                )
                if converted_width is not None:
                    self.body.append(
                        f"block(width: {converted_width})[#{figure_code} "
                        f"<{label}>]\n\n"
                    )
                else:
                    self.body.append(f"[#{figure_code} <{label}>]\n\n")  # line 3328
            elif converted_width is not None:
                self.body.append(...)
            else:
                self.body.append(f"{figure_code}\n\n")

            # TBL-02/Critical Pitfall 3: ids[0] is already self-anchored
            # above as the figure's own <label> -- anchoring it again
            # here would define it TWICE (Typst "label ... occurs
            # multiple times" compile fatal). Anchor only a PROPAGATED
            # remainder id (ids[1:]); no-op when there is none.
            self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))  # line 3341 -- THE BUG SITE
        else:
            # Caption-less path: byte-for-byte unchanged (SC#2).
            if converted_width is not None:
                self.body.append(f"block(width: {converted_width})[#{table_code}]\n\n")
            else:
                self.body.append(f"{table_code}\n\n")

    self.in_table = False                 # line 3351 -- flag cleared HERE, three statements after the bug site
    self.table_cells = []
    self.table_colcount = 0
    self.table_colwidths = []
    self.table_caption = None             # line 3355 -- self.table_caption itself is reset here
    if hasattr(self, "table_cell_content"):
        del self.table_cell_content        # lines 3367-3368
```

**The exact in-table flag that `add_text` branches on is `self.in_table`** (no other name — the
phase description's "the in-table flag" refers to this single boolean, initialized `False` at line
162, set `True` at `visit_table` line 3194, cleared `False` at `depart_table` line 3351). `add_text`
itself:

```python
# typsphinx/translator.py:423-437 (verbatim)
def add_text(self, text: str) -> None:
    if (
        hasattr(self, "in_table")
        and self.in_table
        and hasattr(self, "table_cell_content")
    ):
        self.table_cell_content.append(text)
    else:
        self.body.append(text)
```

`_emit_id_anchors` (line 481-552) itself calls `self.add_text(...)` for every pending anchor (line
550: `self.add_text(f"\n[#metadata(none) <{label_id}>]\n")`) — it never calls `self.body.append`
directly. So the call at line 3341 fires while `self.in_table` is still `True` (not cleared until
line 3351, **10 lines and 3 statements later**), and `hasattr(self, "table_cell_content")` is also
still `True` at that point (only deleted at lines 3367-3368, after the anchor call has already run).
Every `add_text` call inside `_emit_id_anchors` at line 3341's call time therefore appends into
`self.table_cell_content` — a list that is about to be `del`eted three statements later and was
never read again after the table's own cells were assembled into `table_code` (line 3302). The
anchor text is not merely misplaced; it is discarded outright.

**D-05's claim ("move the call after the in-table flag is cleared") is mechanically possible** and
was verified working this session (see "Verified fix" below). The precise, minimal move:

1. Capture `was_captioned = bool(self.table_caption)` **before** line 3355 resets
   `self.table_caption = None` (a local variable is needed because the existing `if
   self.table_caption:` branch check at line 3304 cannot be re-used after the reset).
2. Delete the call at line 3341 from inside the `if self.table_caption:` branch.
3. Insert `if was_captioned: self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))`
   after `self.in_table = False` (line 3351) — before or after the other four reset lines does not
   matter functionally (verified: `add_text`'s routing decision only depends on `self.in_table`,
   which is already `False` by then; `hasattr(self, "table_cell_content")` no longer matters once
   `in_table` is `False`, so ordering relative to the `del` at line 3367 is immaterial).

**What does NOT break by moving the call:**
- The `figure()` wrap's own close (`) <label>]`) at lines 3318-3334 is unaffected — it is emitted via
  `self.body.append` directly (never `add_text`), and happens before the move point regardless.
- The `list_item_needs_separator` bookkeeping `_emit_id_anchors` performs internally (lines 547,
  551-552) reads/writes `self.in_list_item` / `self.list_item_needs_separator`, neither of which is
  touched by any of the five reset lines (3351-3355) or the `del` at 3367-3368 — moving the call past
  those lines changes nothing about that bookkeeping.
- The caption-less path (the `else:` branch at line 3342) is completely untouched by this move — it
  never called `_emit_id_anchors` and still does not; **verified experimentally**: the existing
  `TestTableInListItemRenderGate`'s top-level control table (a byte-invariance control for a
  non-captioned table) still passed with the moved call in place.
- Nothing downstream of `depart_table` reads `self.table_cell_content` or `self.table_caption` after
  this point in the same document build, so reordering relative to their resets is safe.

## 2. The figure path analogue (D-09/D-10) — why figures are unaffected, in code terms

`depart_figure` (line 2480) has the **structurally identical** self-anchor + skip-ids pattern:

```python
# typsphinx/translator.py:2502-2522 (verbatim)
if node.get("ids"):
    label = self._namespace_label(self._current_docname(), node["ids"][0])
    self.add_text(f"\n) <{label}>]\n\n")
elif self._figure_block_width is not None:
    self.add_text("\n)]\n\n")
else:
    self.add_text("\n)\n\n")

# A captioned figure self-anchors ONLY ids[0] (its own caption/numref
# id) in the ``) <label>]`` postfix above. A PROPAGATED explicit target
# (``.. _t:`` before ``.. figure::``) lands a DIFFERENT id in ids[1:]
# that would otherwise dangle -- anchor the remainder, skipping ids[0]
# so it is not defined twice. Empty/single-id figures -> no-op.
self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))   # line 2518

self._figure_block_width = None
self.in_figure = False    # line 2522 -- cleared AFTER the anchor call, unlike depart_table
```

**The difference that matters:** `depart_figure`'s trailing `_emit_id_anchors` call (line 2518) fires
*before* `self.in_figure = False` (line 2522) — the same *ordering* as `depart_table`'s bug. But this
is harmless for figures because **`add_text` never checks `self.in_figure` at all** — re-read the
`add_text` body above: the only flag it consults is `self.in_table` (combined with
`hasattr(self, "table_cell_content")`). There is no `in_figure`-gated buffer in the class; figure
content is buffered separately, by *local Python variables* (`self.figure_content`,
`self.figure_caption`, both reset to fresh values in `visit_figure`/`depart_figure` and never
consulted by `add_text`), not by a flag `add_text` itself branches on. So even though
`_emit_id_anchors`'s internal `self.add_text(...)` calls fire while `self.in_figure` is still `True`,
they always fall through to the `else: self.body.append(text)` branch — the correct destination.

**This is the load-bearing fact for D-09's regression gate**, and it means the gate should assert
something *stronger* than "the figure case currently works" — it should assert the actual anchor
text lands in `self.body`/the emitted `.typ` at all four propagated-target shapes (D-10's three
figure shapes: named, unnamed, list-item), so that if a *future* change ever introduces an
`in_figure`-gated buffer diversion analogous to `in_table`'s (e.g. to fix some other figure-caption
bug), this gate catches the regression the same class of defect this phase fixes for tables.

**Verified this session** (real `sphinx-build -b typst` + `-b typstpdf`, reusing
`tests/fixtures/figure_target_caption_render_gate/image.png` as the image asset): a target +
`:name:`-carrying figure emits **both** `<index:fig-name>` (self-anchor postfix) and
`[#metadata(none) <index:fig-target>]` (propagated-remainder anchor), and the `-b typstpdf` build
produces a valid non-empty PDF with no `TypstError` in stderr. This directly confirms the CONTEXT.md
throwaway measurement ("Captioned figures are unaffected") as phase-grade evidence, not merely
carried-over hearsay.

**One important scoping note for D-10's gate:** the existing
`tests/fixtures/figure_target_caption_render_gate/` fixture is **not** the same test shape — its two
figures use the docutils `:target:` **option** (`.. figure:: image.png` with `:target:
internal-anchor-section_`), which creates a `reference`-wrapped figure (a click-through hyperlink on
the image), not a standalone `.. _label:` **target directive** preceding the figure (the
`PropagateTargets`-transform id-propagation case this phase is about). These are two entirely
different docutils mechanisms that happen to share the word "target." D-09/D-10's new gate needs a
**new** fixture using the standalone-target-directive shape, not an extension of
`figure_target_caption_render_gate/`.

## 3. Test/fixture conventions, measured from the repo

### GATE-01 fixture layout (established pattern, ~30 existing fixture directories)

`tests/fixtures/<name>/` contains a minimal `conf.py` (project/author/release, `extensions =
["typsphinx"]`, `typst_documents = [(...)]` making `index` a **master** document so the writer
applies the full template — required for `TypstPDFBuilder.finish()` to actually attempt a
compile), plus `index.rst` with distinctive ALLCAPS sentinel tokens (e.g. `TBLCAPFIRSTSENTINEL`) so
`full_text.count(sentinel)` assertions can prove exact-once occurrence in extracted PDF text.
`numfig = True` is needed whenever `:numref:` is used (not needed for plain `:ref:`).

### `tests/test_pdf_render_gate.py` structure

One shared module houses many fixture-driven test classes. The load-bearing helpers:
- `_run_sphinx_build_typst(source_dir, build_dir, extra_args=())` — `subprocess.run([sys.executable,
  "-m", "sphinx", "-b", "typst", ...])`, captured text, never raises.
- A **class-scoped** pytest fixture (e.g. `captioned_table_render_gate_artifacts`, line ~2519) builds
  + compiles ONCE per test class and returns a small container object (`.typ_source`, `.full_text`)
  so multiple thin test methods share one real compile rather than re-running it per method.
- The crux of every GATE-01 module: `typst.compile(str(index_typ), output=str(pdf_output))` called
  **without** try/except — any `TypstCompilationError`/`typst.TypstError` propagates and fails the
  whole class loudly, which is the actual proof a fatal is gone.

### The classic-RED convention (this phase's own RED shape, per milestone invariant #4's TBL-03
exception) — precedent: `tests/test_paragraph_propagated_target_render_gate.py` and
`tests/test_desc_container_propagated_target_render_gate.py`, `tests/test_rubric_propagated_target_render_gate.py`,
`tests/test_deflist_nested_definition_render_gate.py`, `tests/test_desc_signature_anchor_render_gate.py`

These are the **exact precedent pattern for TBL-03** — each is a "propagated target before body
element X" real-compile regression gate, driving `-b typstpdf` (not `-b typst`, since the semantic
label-resolution fatal only fires inside `TypstPDFBuilder.finish()`'s `typst.compile()` call) and
asserting:
1. `result.returncode == 0` (the subprocess itself did not crash);
2. `"does not exist in the document" not in result.stderr` (the specific fatal signature, logged not
   raised inside `TypstPDFBuilder.finish()`);
3. the propagated-target anchor (`[#metadata(none) <docname:target-id>]`) is present in the emitted
   `.typ`;
4. a generic **anchor-name == reference-name** sweep: every `link(<name>, ...)` in the emitted source
   has a matching `[#metadata(none) <name>]` anchor — `dangling = link_names - anchor_names` must be
   empty;
5. `index.pdf` exists, non-empty, starts with `%PDF`.

**Recording the RED literally:** per the recorded convention in `40-GATE-EVIDENCE-01.md` ("classic
compile-fatal RED"), the fixture + test module is written and committed **while the bug still
exists** (verified: `git status --porcelain typsphinx/` empty at that commit — "no source changes"),
`uv run pytest <module> -v` is run and its **verbatim** failure output (including the real
`TypstError` text, captured either from `result.stderr` assertions failing, or from a direct
`typst.compile()` call inside the test itself) is pasted into a `*-GATE-EVIDENCE-NN.md` file. Only
then does the fix land in a separate, later commit, and the same module is re-run to GREEN. **This
phase does not need to "reconstruct" a pre-fix basis the way Phase 25's `TestCaptionedTablePreFixBasisFailureProof`
had to** (that class existed because Phase 25's own bug no longer existed in the code by the time its
gate was written) — TBL-03's bug is live in the current tree, so the classic real-compile RED can and
should be captured directly against the unfixed `depart_table`, exactly like the five modules named
above.

### D-01 discretion: new fixture vs. extending `captioned_table_render_gate/`

**Recommendation: give TBL-03 its own new fixture directory(ies)**, not an extension of
`tests/fixtures/captioned_table_render_gate/`. Evidence for this:

1. **Contamination risk during the RED window.** `captioned_table_render_gate/index.rst` is the
   fixture behind `TestCaptionedTableRenderGate`, an **already-GREEN** class with five exact-count
   sentinel assertions (`full_text.count(sentinel) == 1`). Since typst.compile() aborts the ENTIRE
   document on a single dangling label, adding a target+captioned-table pair that fails pre-fix to
   the SAME `index.rst` would make `TestCaptionedTableRenderGate`'s own currently-passing assertions
   fail too during the RED-recording window — mixing an unrelated (already-shipped) requirement's
   regression coverage into this phase's own RED capture.
2. **Convention precedent.** Every other "propagated target before node type X" regression is its own
   dedicated fixture + module (`paragraph_propagated_target_render_gate`,
   `desc_container_propagated_target_render_gate`, `rubric_propagated_target_render_gate`,
   `deflist_nested_definition_render_gate`, `desc_signature_anchor_render_gate`) — none of these
   extend an existing unrelated-node's fixture. TBL-03 fits this same "one fixture family per fixed
   defect class" shape.
3. **D-01's four shapes plus D-10's three figure shapes are naturally two families** (table-side,
   figure-side) that should land as two fixtures: e.g.
   `tests/fixtures/captioned_table_propagated_target_render_gate/` (D-01's four shapes) and
   `tests/fixtures/figure_propagated_target_render_gate/` (D-09/D-10's three shapes, using a real
   image asset like `figure_target_caption_render_gate/image.png`).
4. **`table_in_list_item_render_gate/` already proves the "top-level control + list-item case in one
   fixture" pattern works well** (its own top-level control table already discharges a byte-invariance
   assertion) — the new table-side fixture can follow the same shape: one control (caption-less)
   table plus the four D-01 propagated-target shapes.

This is Claude's Discretion per CONTEXT.md; the planner may choose otherwise, but the above is the
measured basis for this recommendation.

## 4. The byte-invariance method (D-04) — reusable command sequence

Phase 36's `36-GATE-EVIDENCE.md` (§ "Post-decoupling diff") is the precedent, measured directly:

```
# 1. Identify the two named commits: pre-fix (this phase's start / a commit before the
#    depart_table move lands) and post-fix (the commit that contains ONLY the call-ordering move).

# 2. Build each commit in its own throwaway git worktree, with its own per-worktree venv
#    (CLAUDE.md's standing worktree-isolation provisioning):
git worktree add <scratch>/pre-fix-wt <PRE_FIX_SHA>
(cd <scratch>/pre-fix-wt && env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev)

git worktree add <scratch>/post-fix-wt <POST_FIX_SHA>
(cd <scratch>/post-fix-wt && env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev)

# 3. Build the SAME caption-less fixture (or the control table inside the new fixture) from
#    each worktree, using that worktree's own venv:
(cd <scratch>/pre-fix-wt  && uv run python -m sphinx -b typst -q -E <path-to-caption-less-fixture> <scratch>/pre-fix-build)
(cd <scratch>/post-fix-wt && uv run python -m sphinx -b typst -q -E <path-to-caption-less-fixture> <scratch>/post-fix-build)

# 4. The proof:
diff <scratch>/pre-fix-build/index.typ <scratch>/post-fix-build/index.typ
# Verbatim output must be EMPTY, exit status 0.
```

Record both named commit SHAs, both worktree build commands (verbatim, with exit statuses), and the
empty `diff` output in a `42-GATE-EVIDENCE-NN.md` file, exactly as `36-GATE-EVIDENCE.md` did. **A
`git diff --stat` between the two named commits will show more than just `translator.py`** if any
other commits (evidence files, STATE.md updates, orchestrator tracking commits) land between them —
Phase 36's own evidence file explicitly measured and explained this noise; isolate the production-code
diff with `git diff --stat <BASE>..<HEAD> -- typsphinx/` specifically.

**This session's own quick verification stood in for this formal method** (not a substitute for it):
the experimental single-line-move patch was applied in-place (not via worktree, since this was a
read-only research session in the main tree), the full test suite was re-run (`805 passed, 1
skipped` — unchanged from Phase 41's own recorded baseline), and `TestTableInListItemRenderGate`'s
top-level control table specifically passed unchanged. The patch was then reverted with `git checkout
-- typsphinx/translator.py` and confirmed byte-identical to a pre-patch backup. This gives strong
confidence the move works and does not need the full two-worktree ceremony to be *discovered* — but
the phase's own SC#4 (D-04) still requires the formal, evidence-recorded worktree diff as the actual
phase deliverable, not this session's throwaway confirmation.

## 5. The repo-wide sweep (D-06/D-07)

**Every `_emit_id_anchors` call site in `typsphinx/translator.py` (21 total), with owning
visit/depart method and image-path classification:**

| Line | Owning method | In-table-context risk? | Classification |
|------|---------------|--------------------------|-----------------|
| 853 | `visit_compound` | No | non-image |
| 884 | `visit_container` (code-block caption) | No | non-image |
| 960 | `visit_paragraph` | No (see note below) | non-image |
| 1777 | `visit_bullet_list` | No | non-image |
| 1832 | `visit_enumerated_list` | No | non-image |
| 1910 | `visit_list_item` | No | non-image |
| 1961 | `visit_literal_block` | No | non-image |
| 2133 | `visit_definition_list` | No | non-image |
| 2518 | `depart_figure` (`skip_ids={ids[0]}`) | No — `add_text` never checks `in_figure` (§2 above) | **image path** — measured unaffected |
| 3175 | `visit_table` (unconditional, non-captioned only) | No — fires before `self.in_table = True` | non-image (table, but not the bug) |
| **3341** | **`depart_table`** (`skip_ids={ids[0]}`) | **YES — the bug** | non-image (table) |
| 3532 | `visit_block_quote` | No | non-image |
| 3644 | `visit_image` (**the literal image-path call site**) | No | **image path** — measured unaffected |
| 4814 | `visit_math_block` | No | non-image |
| 4902 | `depart_math_block` | No | non-image |
| 5137 | `visit_topic` | No | non-image |
| 5169 | `visit_line_block` | No | non-image |
| 5310 | `visit_transition` | No | non-image |
| 5336 | `visit_glossary` | No | non-image |
| 5447 | `visit_desc` | No | non-image |
| 6392 | `visit_rubric` | No | non-image |

**Every `self.in_*` flag assignment in the file was also enumerated** (`in_figure`, `in_table`,
`in_captioned_code_block`, `in_paragraph`, `in_list_item` — 30+ assignment sites). Cross-checked
against `add_text`'s own body (lines 423-437): **`self.in_table` is the ONLY flag `add_text` reads.**
Every other flag (`in_figure`, `in_paragraph`, `in_list_item`, `in_captioned_code_block`) governs
*different* mechanisms — local buffer-swap idioms that temporarily replace `self.body` itself (e.g.
`self._saved_body_for_admonition_title = self.body; self.body = []` at lines 704-705, restored at
764-766; the analogous figure-caption swap at 2551-2552/2583-2585; definition-list term/definition
buffers via `self._saved_body_stack` at 2318-2320/2356 and 2380-2387/2407) — and every one of those
swaps is restored **before** the enclosing node's own depart-time `_emit_id_anchors` call could ever
fire, because the swap is fully contained within a single child node's visit/depart pair, not spread
across the parent's entire visit-to-depart lifetime the way `self.in_table` is.

**Note on `visit_paragraph` (line 960) and the other non-table sites:** if any of these nodes sits
*inside* a table cell (e.g. a paragraph with its own propagated target, nested in a cell), its
`_emit_id_anchors` call correctly routes into `table_cell_content` via `add_text` — this is the
**desired** behavior (CONTEXT.md's own measurement: "A target placed inside a table cell routes
correctly into the cell content and compiles"), not a second instance of the bug. The bug is
specifically that `depart_table`'s **own trailing anchor call for the table's own remaining ids**
(not any cell's content) fires while the table-cell-buffer-diversion flag is still (incorrectly, for
that specific call) set.

**Sweep conclusion (this session's own measurement, offered as strong evidence — D-07 still requires
the phase to re-take this formally as its own recorded finding, not transcribe this table verbatim):**
`self.in_table` is the only add_text-consulted, buffer-diverting flag in the entire file; the ONLY
site where a non-cell-content `_emit_id_anchors` call fires while that flag is (wrongly) still set is
`depart_table` line 3341 — the fix already inside this phase's scope. **No image-path finding
exists** — `visit_image` (line 3644) and `depart_figure` (line 2518) were both measured unaffected
(§2 above; `visit_image`'s own call is never nested inside a table's own post-cell trailing-anchor
context the way `depart_table`'s is). D-06's "an image-path finding IS fixed inside this phase"
condition is therefore moot: there is nothing to fix beyond the table fix itself. **Recommend the
phase's own formal sweep record this explicitly as a null result** for the image-path branch, with
the reusable sweep command:

```bash
# Enumerate every call site that could route through add_text while a buffer-diverting flag is set:
grep -n "_emit_id_anchors(" typsphinx/translator.py
grep -n "def add_text" -A 15 typsphinx/translator.py   # confirm which flag(s) it actually consults
grep -n "self\.in_[a-z_]* = True\|self\.in_[a-z_]* = False" typsphinx/translator.py
```

## 6. SC#6 reconciliation mechanics

### CHANGELOG insertion point (measured, exact line numbers as of HEAD `ae13907`)

`CHANGELOG.md` lines 50-55:

```
50:### Fixed
51:
52:- **Block math inside a list item no longer emits a redundant blank line (MATH-02)** — the extra
53:  blank line between the math expression and the following paragraph break, carried over from the
54:  v0.6.5 Phase 34 review, is gone.
55:
56:### Verified
```

TBL-03 belongs under the existing `## [0.7.0]` entry's `### Fixed` heading (line 50), as a new bullet
inserted after the MATH-02 bullet (after line 54, before the blank line 55) — following the same D-02
Keep-a-Changelog semantics Phase 41 already applied (a real compile-fatal defect being repaired is
"Fixed," matching MATH-02's own precedent), and the same D-01 granularity (5-6 bullets at
user-visible-change grain, requirement ID in trailing parentheses). Suggested bullet shape (planner
should verify final wording against the actual landed fix):

```
- **A captioned table preceded by a standalone target no longer drops the target's label
  (TBL-03)** — both the table's own name-derived label and the propagated target's label are now
  emitted, so a reference to either resolves instead of aborting the compile on a dangling label.
```

Note: the `## [0.7.0]` heading itself (line 10) currently reads `## [0.7.0] - 2026-08-03` — if Phase
42 lands on a different date, the planner/owner should decide whether to update this date (out of
this research's scope to decide; flagging as an open question below).

### SC#4 invariant-sweep re-measurement — exact command shape and SHA range

Phase 41's own `41-SC4-INVARIANTS.md` measured the milestone diff against BASE
`51e02b6b61b314c99740883fb4bee7ce7b9be76b` (the `v0.6.5` tag commit, `git describe` confirms
`v0.6.5-1-g51e02b6`). Phase 42's re-measurement should use the **same BASE**, extending HEAD to
include Phase 42's own commits:

```bash
# Same BASE as 41-SC4-INVARIANTS.md; HEAD is Phase 42's own tip, not Phase 41's.
git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- typsphinx/
git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- pyproject.toml
git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- uv.lock
git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- docs/
```

Per `41-CONTEXT.md` D-11's own precedent (Phase 41's sweep read `40.1-NONREGRESSION.md` §4's
"change-site → RED manifest" table rather than re-deriving Phase 40.1's evidence from scratch), Phase
42's own evidence file should include an analogous **change-site → RED manifest** table (see
`40.1-NONREGRESSION.md` §4 for the exact format: change-site/warning/evidence-file/RED-form/
provenance/pytest-selector/recording-commit columns) for its own single `depart_table` change, so a
**future** milestone's sweep can read Phase 42's evidence file the same way Phase 41 read Phase
40.1's, without re-deriving it. Per CONTEXT.md's explicit instruction, this manifest must be written
as a **new** file under `.planning/phases/42-.../`, never by editing any `41-*` artifact.

### REL-04/REL-05 checkbox-flip hazard — exact file, exact lines

`.planning/REQUIREMENTS.md`:
- Line 208: `- [ ] **REL-04** [M]: ...` — currently unchecked, must stay unchecked through this
  phase's own commits (it is close-side work per Phase 41's own scope decision).
- Line 212: `- [ ] **REL-05** [M]: ...` — same.
- Lines 337-338 (Traceability table): `| REL-04 | Phase 41 | Pending |` and `| REL-05 | Phase 41 |
  Pending |` — must stay `Pending`.

`phase.complete`/`state.planned-phase` has **twice** in this project's history (Phase 41 itself, per
`STATE.md`'s own record, and the general hazard `41-HANDOFF.md` item 6 names explicitly) auto-flipped
a deferred requirement's checkbox against an explicit CONTEXT decision. **Concrete mitigation for
Phase 42's own close:** run `git diff --name-only -- .planning/REQUIREMENTS.md` immediately after any
`phase.complete`-family command runs and before committing; if lines 208, 212, 337, or 338 show an
unintended change, revert it (`git checkout -- .planning/REQUIREMENTS.md` then re-apply only the
TBL-03 checkbox/traceability-row flip by hand) before committing.

## 7. Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (`pyproject.toml` `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`, `addopts = "-v --strict-markers"`, markers `slow`/`integration`, `filterwarnings = ["error::DeprecationWarning", "error::PendingDeprecationWarning"]`) |
| Quick run command | `uv run pytest tests/test_<new_fixture>_render_gate.py -v` |
| Full suite command | `uv run pytest` (805 passed / 1 skipped baseline, measured this session, unchanged from Phase 41's own recorded number) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TBL-03 (SC#1/SC#3) | Real compile fails pre-fix with `TypstError: label ... does not exist`, and compiles + resolves both labels post-fix, for all four D-01 shapes | classic real-compile RED→GREEN (milestone invariant #4 exception) | `uv run pytest tests/test_captioned_table_propagated_target_render_gate.py -v` | ❌ Wave 0 — new module + fixture |
| TBL-03 (SC#2) | Whether captioned figures share the drop — answered NO this session, needs its own recorded proof | real-compile positive control (D-09 permanent gate) | `uv run pytest tests/test_figure_propagated_target_render_gate.py -v` | ❌ Wave 0 — new module + fixture (D-09/D-10) |
| TBL-03 (SC#4) | Caption-less path byte-for-byte unchanged | two-worktree byte-diff (D-04), recorded as evidence, not a pytest assertion | see §4 command sequence above | N/A — evidence-file method, not a test file |
| TBL-03 (SC#5/D-06) | Repo-wide sweep for the same misrouting class, image-path finding fixed if found | manual code sweep, recorded as evidence | `grep -n "_emit_id_anchors(" typsphinx/translator.py` + manual classification (§5 above) | N/A — evidence-file method |

### Sampling Rate
- **Per task commit:** the new fixture's own module (`uv run pytest tests/test_captioned_table_propagated_target_render_gate.py -v`, and the figure one once it exists).
- **Per wave merge:** `uv run pytest` (full suite).
- **Phase gate:** full suite green, `black --check .` / `ruff check .` / `mypy typsphinx/` all clean, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/fixtures/captioned_table_propagated_target_render_gate/` (or the planner's chosen name)
      — `conf.py` + `index.rst` covering D-01's four shapes plus a caption-less control table.
- [ ] `tests/test_captioned_table_propagated_target_render_gate.py` — the classic RED→GREEN module,
      following the `test_paragraph_propagated_target_render_gate.py` shape exactly (§3 above).
- [ ] `tests/fixtures/figure_propagated_target_render_gate/` — new fixture (NOT an extension of
      `figure_target_caption_render_gate/`, which tests a different docutils mechanism — see §2's
      scoping note), covering D-10's three shapes, reusing an existing image asset (e.g. copy
      `figure_target_caption_render_gate/image.png`).
- [ ] `tests/test_figure_propagated_target_render_gate.py` — the permanent D-09 regression gate.
- [ ] No new framework install needed — pytest, `typst-py`, and `pypdf` are all already present and
      exercised by the existing render-gate suite.

## Package Legitimacy Audit

**Not applicable.** This phase adds no new runtime or dev dependency — the fix is a call-ordering
move inside `typsphinx/translator.py`, and the new tests reuse the already-present `typst`/`pypdf`
dev dependencies exercised by every existing `*_render_gate.py` module. `git diff --stat <BASE>..HEAD
-- pyproject.toml uv.lock` must stay empty across this phase's own commits (verify as part of the
milestone-invariant sweep, §6 above).

## Standard Stack

Not applicable in the conventional sense (no new library is introduced). The phase's own "stack" is
entirely this project's existing testing conventions:

| Component | Version (measured this session) | Purpose |
|-----------|-----------|---------|
| pytest | 9.1.1 | test runner |
| Sphinx | 9.1.0 | doctree construction |
| docutils | 0.22.4 | node tree, `PropagateTargets` transform |
| typst (typst-py) | already pinned in `pyproject.toml`/`uv.lock` (unchanged) | real `.typ` → PDF compile, the source of the classic `TypstError` RED |
| pypdf | already pinned (unchanged) | PDF text extraction for sentinel assertions |

## Architecture Patterns

### System Architecture Diagram

```
docutils doctree (nodes.table with node["ids"] = [name_id, target_id, ...])
        │
        ▼
  visit_table  ──(captioned? skip; else: _emit_id_anchors(node) -- SAFE, in_table still False)──▶ self.body
        │
        │  self.in_table = True   ◄── buffer-diverting flag turns ON here
        ▼
  [title/caption buffered via visit_title → self.table_cell_content]
  [cells visited: visit_entry/visit_row/... → self.table_cell_content, consumed into table_code]
        │
        ▼
  depart_table
        │
        ├─ table_code assembled from self.table_cells (already-buffered content)
        │
        ├─ captioned? ─┬─ YES: figure(...) <label> self-anchors ids[0]  (self.body.append -- SAFE, bypasses add_text)
        │               │       _emit_id_anchors(node, skip_ids={ids[0]})  ◄── BUG: fires while
        │               │       self.in_table is STILL True → add_text() misroutes into
        │               │       self.table_cell_content (about to be discarded) instead of self.body
        │               │
        │               └─ NO:  plain table(...) emitted (self.body.append -- unchanged, SC#2 control)
        │
        ├─ self.in_table = False        ◄── flag turns OFF here, AFTER the bug fires today
        ├─ self.table_caption = None
        └─ del self.table_cell_content  (buffer discarded — the anchor text emitted into it is lost)

FIX (D-05): move the `_emit_id_anchors(node, skip_ids={ids[0]})` call to AFTER `self.in_table = False`
            (gated on a `was_captioned` flag captured before `self.table_caption` resets), so
            add_text() correctly falls through to self.body.
```

### Recommended Project Structure

No structural change — the fix lives entirely inside the existing `depart_table` method in
`typsphinx/translator.py`. New files are test-only:

```
tests/
├── fixtures/
│   ├── captioned_table_propagated_target_render_gate/   # NEW — D-01's four shapes + control
│   │   ├── conf.py
│   │   └── index.rst
│   └── figure_propagated_target_render_gate/            # NEW — D-09/D-10's three shapes
│       ├── conf.py
│       ├── index.rst
│       └── image.png                                    # reuse figure_target_caption_render_gate/image.png
├── test_captioned_table_propagated_target_render_gate.py  # NEW — classic RED→GREEN module
└── test_figure_propagated_target_render_gate.py           # NEW — permanent regression gate
```

### Pattern: propagated-target real-compile regression gate

**What:** a fixture pairing a standalone `.. _label:` target immediately before the node type under
test, plus a `:ref:`/`:numref:` reference to both the target's label and the node's own `:name:`
label, driven through `-b typstpdf` and asserting the classic dangling-label `TypstError` is gone.
**When to use:** whenever a body-element visitor's id-anchoring path is being fixed or hardened
against docutils' `PropagateTargets` transform.
**Example** (adapted from `tests/test_paragraph_propagated_target_render_gate.py`, verified working
pattern):
```python
# Source: tests/test_paragraph_propagated_target_render_gate.py (existing precedent in this repo)
result = _run_sphinx_build_typstpdf(fixture_dir, temp_build_dir)
assert result.returncode == 0, f"...\nstderr: {result.stderr}"
assert "does not exist in the document" not in result.stderr, "dangling label -- fix not in effect"
typ_text = (temp_build_dir / "index.typ").read_text(encoding="utf-8")
assert "[#metadata(none) <index:my-target>]" in typ_text
scan_text = re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)
link_names = set(re.findall(r"link\(<([^>]+)>", scan_text))
anchor_names = set(re.findall(r"\[#metadata\(none\) <([^>]+)>\]", scan_text))
dangling = link_names - anchor_names
assert not dangling, f"dangling labels: {sorted(dangling)}"
pdf_output = temp_build_dir / "index.pdf"
assert pdf_output.exists() and pdf_output.stat().st_size > 0
```

### Anti-Patterns to Avoid
- **Widening the fix into `add_text` or `_emit_id_anchors` itself** — explicitly rejected by D-05 and
  the owner's specifics note ("declined to widen the fix into the shared emission helper"). The
  correct fix is call-site relocation only.
- **Extending the already-green `captioned_table_render_gate/index.rst` with a pre-fix-failing case**
  — would make an unrelated, already-shipped requirement's assertions fail during the RED-recording
  window (§3 above).
- **Asserting on the literal text of the `TypstError` message** — this repo's own precedent
  (`TestCaptionedTablePreFixBasisFailureProof`'s docstring, and D-06 in Phase 25) explicitly warns
  against matching exception message text; assert only that a real compile call raises/logs the
  `"does not exist in the document"` *substring* (already the pattern all five precedent modules use)
  or that `typst.compile()` raises at all, never a full-string match.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Real-compile regression proof | A custom subprocess/compile harness | The existing `_run_sphinx_build_typst`/`_run_sphinx_build_typstpdf` helpers and class-scoped artifact fixtures already in `tests/test_pdf_render_gate.py` and the five propagated-target modules | Already NixOS-sandbox-hardened (`sys.executable -m sphinx`, never a bare `sphinx-build`) and already proven against exactly this defect class |
| Dangling-label detection | A hand-rolled label/reference matcher | The `link(<name>, ...)` vs. `[#metadata(none) <name>]` regex-diff idiom already used in every propagated-target gate | Directly reusable, already correctly excludes literal `raw("...")` string content that merely *documents* the syntax |

**Key insight:** this defect class (docutils `PropagateTargets` dropping onto a body element whose
visitor doesn't anchor it, or — this phase's twist — anchors it into a buffer that gets discarded)
has been fixed and gated five times already in this codebase (paragraph, bullet list, desc-container,
rubric, deflist-nested-definition). TBL-03 is the sixth instance of the same class, and the sixth
gate should look structurally identical to the first five, not reinvent the assertion shape.

## Common Pitfalls

### Pitfall 1: Assuming `self.in_figure` gates `add_text` the same way `self.in_table` does
**What goes wrong:** a naive reader of `depart_figure`'s docstring/comments (which describe an
analogous-looking self-anchor + skip-ids pattern) might assume figures have the same "buffer
diversion while a flag is set" hazard and therefore need the same call-ordering fix.
**Why it happens:** `depart_figure`'s `_emit_id_anchors` call ALSO fires before `self.in_figure =
False`, which superficially looks like the same ordering bug.
**How to avoid:** `add_text` (lines 423-437) is the single source of truth — it checks ONLY
`self.in_table`. Grep it before assuming any other flag matters.
**Warning signs:** a fix that touches `depart_figure`'s statement order at all is almost certainly
unnecessary and outside D-05's locked scope (call-ordering change inside the table departure handler
**only**).

### Pitfall 2: Reordering `self.table_caption = None` relative to the moved anchor call without
capturing `was_captioned` first
**What goes wrong:** if the moved `_emit_id_anchors` call is guarded by `if self.table_caption:`
directly (re-reading the same condition used at line 3304) instead of a captured boolean, it will
always evaluate `False` post-move, because `self.table_caption = None` (line 3355) already ran by
construction if the move lands after all five reset lines — silently disabling the fix for every
captioned table, including the four D-01 shapes, while leaving the caption-less path (which never had
a bug) untouched. This would look deceptively like "no code path executes the new call" rather than
loudly failing.
**Why it happens:** the five reset statements (3351-3355) are easy to move past without noticing
`self.table_caption` is one of them.
**How to avoid:** capture `was_captioned = bool(self.table_caption)` as a local variable BEFORE line
3355 runs (verified this session — see §1's exact patch description).
**Warning signs:** the new fixture's GREEN assertions pass for the *caption-less control* but the
D-01 shapes still show the dangling-label fatal — a sign the guard condition is stale.

### Pitfall 3: Treating `figure_target_caption_render_gate/` as already covering D-09/D-10
**What goes wrong:** re-using the existing figure fixture for the new permanent regression gate,
assuming its `:target:`-carrying figures already exercise the propagated-target-id mechanism.
**Why it happens:** both use the word "target"; the fixture's own docstring even discusses
"internal/external `:target:` refid/refuri branching," which sounds adjacent.
**How to avoid:** `:target:` is a docutils **directive option** producing a `reference`-wrapped
figure (an image that is itself a hyperlink) — a completely different code path
(`visit_reference`/`depart_reference`) from a standalone `.. _label:` **target directive** placed
before the figure (which triggers `PropagateTargets` and lands an id on `node["ids"][1:]`, the
mechanism this phase is about). Confirmed by reading both fixtures' `index.rst` — neither existing
figure fixture contains a standalone target directive.
**Warning signs:** a "new" figure gate that reuses the old fixture's `index.rst` unchanged will not
actually exercise D-10's three shapes at all.

## Code Examples

### Real compile trace of the unfixed defect (this session, verified against HEAD `ae13907`)

```
$ uv run python -m sphinx -b typstpdf -q -E <fixture-with-target-plus-named-captioned-table> <build>
Typst compilation failed at .../index.typ: TypstError: label `<index:tbl-target>` does not exist in the document
ERROR: Failed to compile .../index.typ: Typst compilation failed: TypstError: label `<index:tbl-target>` does not exist in the document
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: label `<index:tbl-target>` does not exist in the document
```

### Real doctree `node["ids"]` contents at `depart_table` time (this session, all four D-01 shapes)

```
target + :name:-carrying table:      ids: ['tbl-name', 'tbl-target']            names: ['tbl-name', 'tbl-target']
target + no-:name: table:            ids: ['id1', 'tbl-target-noname']          names: ['tbl-target-noname']  (id1 is docutils' auto id, unnamed)
table inside a bullet-list item:     ids: ['tbl-name-li', 'tbl-target-li']      names: ['tbl-name-li', 'tbl-target-li']
two consecutive targets + table:     ids: ['tbl-name-two', 'tbl-target-b', 'tbl-target-a']   (NOTE: chained-target order is REVERSED relative to source order -- target-b before target-a -- do not assume source order when writing assertions; match by NAME, not position)
```

## State of the Art

Not applicable — this is a same-codebase regression fix, not an ecosystem/library update. The
"pattern" that has evolved across this project's history is the propagated-target real-compile gate
itself (five prior instances, cited throughout this document); TBL-03 continues that pattern rather
than introducing a new one.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The whitespace-only-title state (D-08) may not be reachable via a plain `.. table:: ` (trailing-whitespace-only) argument — measured this session: docutils produced NO title child at all for that input, so `is_captioned` was `False` and the table anchored correctly via the non-captioned path. Whether some OTHER construct (e.g. a substitution reference expanding to empty inline content inside a table title) produces a genuinely empty-but-present title node was not tested. | §1 preamble / D-08 (out of scope, filed as todo regardless) | Low — D-08 is explicitly deferred to a todo either way; this note only affects how urgently that todo should be prioritized, not this phase's own scope. |
| A2 | The CHANGELOG bullet wording suggested in §6 is a draft, not a locked phrasing; the planner/owner should finalize it against the actual landed fix description, following D-01/D-02's granularity and section-placement rules from `41-CONTEXT.md`. | §6 | Low — cosmetic; does not affect SC#6's mechanical requirement (a TBL-03 line exists under `### Fixed`). |
| A3 | Whether the `## [0.7.0]` CHANGELOG heading's date (`2026-08-03`, currently matching Phase 41's close date) should be updated if Phase 42 lands on a later date was not decided by this research — flagged as an open question below. | §6 | Low — a stale date is cosmetic, not a compile-affecting or requirement-affecting defect. |

## Open Questions

1. **Should the `## [0.7.0]` CHANGELOG date (line 10, currently `2026-08-03`) be updated to Phase
   42's own actual landing date, or left as Phase 41's close date?**
   - What we know: Phase 41 set the date to its own close date (2026-08-03) as part of SC#2; Phase
     42 was promoted the same day but has not yet executed.
   - What's unclear: whether "release date" should track the milestone's LAST phase to land (Phase
     42, whenever it actually executes) or stay as originally written.
   - Recommendation: decide at plan time or defer to the owner during discuss-phase follow-up; this
     is a one-line, low-risk cosmetic decision that does not block SC#6's mechanical requirement (a
     TBL-03 bullet existing under `### Fixed`).

2. **Whether the D-08 whitespace-only-title state is reachable at all via any rST construct** remains
   genuinely open — this session's own probe (a literal trailing-whitespace `.. table:: ` argument)
   found docutils suppresses the title node entirely in that specific case, which is a data point
   *against* reachability but not a proof of unreachability for every possible construct (e.g.
   substitution references, replace directives, or raw markup that might produce a title node whose
   rendered text strips to empty while the node itself still exists). Per D-08, this phase files a
   todo rather than resolving it — the todo should carry this session's negative-but-inconclusive
   finding so the next investigator does not re-run the same trivial probe.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst` (typst-py) | Real-compile GATE-01 assertions | ✓ | already pinned, unchanged this session | — |
| `pypdf` | PDF text extraction for sentinel assertions | ✓ | already pinned, unchanged this session | — |
| `uv` | Worktree provisioning, all command execution | ✓ (with the documented NixOS `.venv/bin/uv`+`ruff` symlink shim, per CLAUDE.md/MEMORY.md) | — | — |
| Sphinx | Doctree construction, `sys.executable -m sphinx` | ✓ | 9.1.0 (measured this session) | — |
| docutils | `PropagateTargets` transform | ✓ | 0.22.4 (measured this session) | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — this phase's environment is fully provisioned already
in the main tree (confirmed: `.venv/bin/python` exists, `import typsphinx` resolves to the repo's own
package, full suite ran clean this session).

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Not applicable — this is a document-compiler pipeline, no auth surface |
| V3 Session Management | No | Not applicable |
| V4 Access Control | No | Not applicable |
| V5 Input Validation | Marginal — already handled, unchanged by this fix | rST source (including author-chosen target/`:name:` ids) is already routed through `_sanitize_label` (bug #10, referenced at line 504) and `_namespace_label` before being embedded in emitted Typst source; this fix reuses those same helpers unchanged (verified: `_emit_id_anchors`'s own body, lines 481-552, is not touched by the D-05 move — only its CALL SITE inside `depart_table` moves) |
| V6 Cryptography | No | Not applicable — no cryptographic operation in this phase |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Denial of Service (build-time) via a dangling or duplicate Typst label aborting the ENTIRE document compile | Denial of Service | This IS the defect class this phase fixes (a malformed or adversarially-crafted-but-unlikely `:name:`/target combination could already abort any build before this fix, and D-03 requires the fix not trade one DoS-class fatal for another — a duplicate-label fatal). No new mitigation is introduced beyond continuing to route every id through the existing `_sanitize_label`/`_namespace_label`/`skip_ids`-guarded `_emit_id_anchors` path, unchanged. |

Given the negligible security surface (an internal document-compiler defect fix touching no
authentication, session, access-control, or cryptographic code, and reusing existing input-sanitization
helpers unchanged), no new ASVS-driven work is created by this phase beyond continuing to exercise
the pre-existing `_sanitize_label` path, which the fix does not touch.

## Sources

### Primary (HIGH confidence — verified directly this session against the live tree)
- `typsphinx/translator.py` (HEAD `ae13907`) — `visit_table` (3149-3197), `depart_table`
  (3249-3368), `add_text` (423-437), `_emit_id_anchors` (481-552), `visit_figure`/`depart_figure`
  (2418-2531), `visit_target`/`depart_target` (3689-3771) — read directly, quoted verbatim above.
- Real `sphinx-build -b typst` / `-b typstpdf` runs against six purpose-built scratch fixtures (the
  four D-01 shapes, the figure analogue, and the whitespace-only-title probe), including a pickled
  doctree inspection confirming `node["ids"]`/`node["names"]` contents at each shape.
- An experimental single-line-move patch, applied and reverted in this session, confirmed the D-05
  fix mechanism against the full test suite (805 passed / 1 skipped, matching Phase 41's own
  recorded baseline) and the existing table-related test classes
  (`TestCaptionedTableRenderGate`, `TestCaptionedTablePreFixBasisFailureProof`,
  `TestTableInListItemRenderGate`).
- `tests/test_paragraph_propagated_target_render_gate.py`,
  `tests/test_desc_container_propagated_target_render_gate.py`,
  `tests/test_rubric_propagated_target_render_gate.py`,
  `tests/test_pdf_render_gate.py` (`TestCaptionedTableRenderGate`,
  `TestCaptionedTablePreFixBasisFailureProof`) — read directly, quoted/paraphrased above.
- `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` — byte-invariance method,
  quoted directly.
- `.planning/phases/40.1-citation-degradation-hardening/40.1-NONREGRESSION.md` — change-site → RED
  manifest format, quoted directly.
- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-HANDOFF.md`,
  `.planning/phases/41-v0-7-0-release-automation-release-prep/41-CONTEXT.md`,
  `.planning/phases/41-v0-7-0-release-automation-release-prep/41-SC4-INVARIANTS.md` — SC#6
  mechanics, SHA base, checkbox-flip hazard.
- `CHANGELOG.md`, `.planning/REQUIREMENTS.md` — exact line numbers measured directly via `grep -n`.

### Secondary (MEDIUM confidence)
- None used beyond primary sources this session — all claims above were independently verified
  against the live tree rather than taken from the discuss-phase throwaway measurement.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: N/A (no new stack; existing conventions only)
- Architecture / root cause: HIGH — directly reproduced, doctree-inspected, and fix-verified this
  session; not carried over from the discuss-phase throwaway measurement
- Pitfalls: HIGH — each pitfall backed by a direct code read or an experimental probe run this
  session
- Test conventions: HIGH — five existing precedent modules read in full
- SC#6 mechanics: HIGH — exact line numbers and SHA bases measured directly against the live tree

**Research date:** 2026-08-03
**Valid until:** until `typsphinx/translator.py`'s `depart_table`/`add_text`/`_emit_id_anchors`
region is next touched by an unrelated phase, or 14 days, whichever is sooner (this is an
actively-developed file with frequent line-number churn — re-verify line numbers before citing them
in a plan if more than a few days have passed).

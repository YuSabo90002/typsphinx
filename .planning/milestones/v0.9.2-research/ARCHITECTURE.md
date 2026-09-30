# Architecture Research: v0.9.2 `visit_image()` separator fix

**Domain:** Sphinx→Typst translator internals (docutils visitor, code-mode emission)
**Researched:** 2026-08-30
**Confidence:** HIGH — every claim below is either a direct `grep`/line-number read of
`typsphinx/translator.py` at HEAD, or a real `typst.compile()` run against generated
fragments in the scratchpad (not the repo tree). No claim rests on memory of Typst
semantics alone.

## Answer to Q1 — Mapping the existing separator discipline

The translator's code-mode body is a single `#{ ... }` block. Two juxtaposed
expressions with nothing between them (`text("a")image("b")`) is `expected semicolon
or line break`. Every inline emitter except `visit_image()` already participates in
one shared discipline built from four primitives:

| Mechanism | file:line | What it does | Drives / driven by | Invariant maintained |
|---|---|---|---|---|
| `add_text()` | `translator.py:887` | Single write funnel. Routes to `self.table_cell_content` when `self.in_table and hasattr(self, "table_cell_content")`, else `self.body`. | Called by every `visit_*`/`depart_*` that emits bytes. | The buffer distinction (`body` vs `table_cell_content`) is invisible to callers — nobody outside `add_text()` needs to know which one is live. |
| `_emit_forced_break()` | `translator.py:903` | Emits a real Typst `parbreak()`/`linebreak()` statement between siblings; a bare source `"\n"` is proven **cosmetic only** (see its own docstring, citing `visit_desc_signature_line`) — it satisfies the parser but adds no visual break. | `visit_paragraph` (2nd+ paragraph in a list item), `visit_rubric`, `visit_desc`-family siblings. | A sibling boundary that needs a *visible* break gets a real stdlib break, not just a parser-satisfying `\n`. |
| `in_paragraph` / `paragraph_has_content` + `_add_paragraph_separator()` | flags declared `~627-629`; method at `translator.py:933` | `if in_paragraph and paragraph_has_content: add_text("\n")`, then unconditionally sets `paragraph_has_content = True` when `in_paragraph`. First child in a paragraph emits nothing; every subsequent child gets a leading `"\n"`. | Set by `visit_paragraph` (`:1410`, only when **not** in a list item and **not** an FLD-02 unwrapped field body); read+mutated by `visit_Text`, `visit_emphasis`/`visit_strong` (entry), `visit_literal`, `visit_math`, `visit_footnote_reference`, `visit_reference`. | The paragraph's `par({...})` body never juxtaposes two children with zero separator. |
| `in_list_item` / `_list_item_stack` | flag `~627`; stack `~630-637` | Bare boolean loses outer context when a *nested* list's `depart_list_item` resets it — the stack (pushed in `visit_list_item` `:2373`, popped in `depart_list_item` `:2409`) preserves the outer item's `True` across a nested list. | `visit_list_item`/`depart_list_item`. | A paragraph immediately following a nested list inside an outer list item is still correctly classified as "inside a list item" (not top-level), so it doesn't emit an unseparated `par(...)`. |
| `list_item_needs_separator` | flag declared `~700-702` | `if in_list_item and list_item_needs_separator: add_text("\n")`, then the emitter sets it back to `True` after its own content (directly, or via `_mark_inline_concat_content()`). Reset to `False` on entry to a fresh list item/paragraph. | Read+set by essentially every block and inline visitor when `in_list_item` is `True` — `visit_Text`, `visit_literal`, `visit_math`, `visit_footnote_reference`, `visit_reference`, `visit_target` (`:4826`/`:4849`), `visit_figure` (`:2964`)/`depart_figure` (`:3129`), `visit_table`, `_emit_forced_break`. | Two siblings inside one list item's content block are always `"\n"`-separated, regardless of node type. |
| `_CONCAT_CONTEXTS` / `_inline_concat_context()` / `_emit_inline_concat_separator()` / `_mark_inline_concat_content()` / `_enter_inline_concat_element()` / `_exit_inline_concat_element()` | table `:1631`; methods `:1639`, `:1651`, `:1666`, `:1679`, `:1707` | Five mutually-exclusive scalar contexts (`in_desc_parameter`, `_in_link`, `_in_term`, `_in_field_body`, `_in_attribution`) where siblings must be joined with Typst `" + "`, not a bare newline, because they're expression operands, not block statements. `_emit_inline_concat_separator()` and `_mark_inline_concat_content()` are pure read/emit or read/mutate helpers with **no other side effect**; `_enter_/_exit_inline_concat_element()` additionally suppress/restore the outer context so a nested block element (`emph({...})`) doesn't leak a stray `+` into its own children. | Read by `visit_Text`, `visit_literal`, `visit_math`; entered/exited by `visit_emphasis`/`depart_emphasis`, `visit_strong`/`depart_strong`, `visit_reference` (opens when `decision.opens_wrapper`). | Adjacent expressions inside a def-list term / link body / desc parameter / field body / attribution are `+`-joined; a block-shaped inline element correctly suppresses that `+` for its own interior. |
| `_emit_id_anchors()` / `visit_target`'s `\n[#metadata(none) <id>]\n` | `translator.py:4785` (visit_target), helper documented `~972` | Emits a **markup-mode** zero-width content block (`[#metadata(none) <id>]`), never a bare code-mode `label(...)` call, and wraps it in a leading+trailing `"\n"` **unconditionally** (not gated on any boundary check). This is safe *because* `[...]` markup content joins cleanly with any adjacent code-mode expression on both sides in Typst's content-joining semantics — unlike a bare `label(...)` call, which is a raw `Label` value, not `content`, and cannot be joined at all. | `visit_target`, `_emit_id_anchors` (shared by `depart_figure`, `depart_table`, `visit_paragraph`, etc.). | A same-document `:ref:`/`:numref:` target always resolves, and the anchor never itself becomes a juxtaposition hazard. |
| `visit_Text` (`:1790`) / `visit_emphasis` (`:1903`) / `visit_literal` (`:2092`) / `visit_footnote_reference` (`:3229`) / `visit_math` (`:5932`) / `visit_math_block` (`:6010`) / `visit_reference` (`:5534`, covers `:download:` too — there is **no** dedicated `visit_download_reference`; Sphinx's `download_reference` node is handled generically by `visit_reference`) | — | Every one of these opens with `self._add_paragraph_separator()` (or, for list-only contexts like `visit_math_block`, just the `in_list_item`/`list_item_needs_separator` check), then `if not self._emit_inline_concat_separator(): if self.in_list_item and self.list_item_needs_separator: self.add_text("\n")`, emits its own call, then `if not self._mark_inline_concat_content(): if self.in_list_item: self.list_item_needs_separator = True`. | — | **This triad is the actual, load-bearing, already-proven-correct convention** — confirmed independently by `.planning/PROJECT.md`'s own measurement: 14 inline construct types were placed mid-sentence and scanned; exactly one (image) was unseparated, because "Footnote, math and download each already emit a leading `\n`" via this exact mechanism. |

**The true precedent for `visit_image()` is the `_add_paragraph_separator()` +
`_emit_inline_concat_separator()` + `in_list_item`/`list_item_needs_separator` triad**
used verbatim by `visit_Text`, `visit_literal`, `visit_math`, `visit_footnote_reference`,
and `visit_reference` — **not** `visit_target`'s unconditional `\n[...]\n` form. The two
are solving different problems: `visit_target` emits a zero-width *markup* content block
that Typst can join to anything on either side with no operator at all, so an
unconditional wrap is correct there; `image(...)` is a code-mode *function call*
operand exactly like `text(...)`/`raw(...)`/`$...$`, which must be joined the way those
are (conditionally, and with `+` inside a concat context) or a stray `+`/redundant
separator results. `visit_image()` (`:4718`) currently calls none of these — it goes
straight from `_emit_id_anchors()` to `self.add_text(f'image("{escaped_uri}"')` with
no leading-separator check at all, which is the entire defect.

## Answer to Q2 — Comparing candidate mechanisms

Measured with a scratch harness that monkey-patches `visit_image` in-process (real
`TypstTranslator`, real docutils nodes, real `typst.compile()` against the emitted
fragments — see verification log below) against six shapes: mid-sentence inline
image, leading image, two images in a row, image in a list item, image in a table
cell paragraph, and a nested figure (control).

**(a) Unconditional `"\n"` before `image(` in the non-figure branch.**
Emits a newline every time, no matter what precedes. Fixes all four broken shapes.
*Breaks:* nothing test-visible (confirmed no test depends on the exact byte adjacency
around a non-figure `image(...)`), but it is the **wrong shape** for this codebase's
own convention: every other inline emitter conditions its separator on actual prior
content (`paragraph_has_content`, concat-context state, `list_item_needs_separator`),
never unconditionally. Using it here would (1) add a stray leading `"\n"` even when
image is the very first paragraph child — cosmetically harmless, but silently
diverges from the "leading image" trigger-matrix row that already compiles correctly
today for a *reason* (nothing precedes it) — and (2) does nothing for the
`_CONCAT_CONTEXTS` case (`_in_attribution`, `_in_link`, etc.), where the correct
separator is `" + "`, not `"\n"` — an unconditional `"\n"` there would still be a
syntax error (a bare newline is not a valid infix operator). Rejected: solves only
the paragraph/list-item shapes the todo enumerates, not the whole hazard class this
translator's discipline otherwise covers.

**(b) A conditional separator that inspects whether the current output already ends
at a line boundary.** This requires a brand-new "does buffer X already end in
whitespace/newline" predicate. **Searched for and confirmed absent**: no
`endswith("\n")`, no `rstrip().endswith(...)`, no "boundary" predicate exists
anywhere in `translator.py` today (`grep` returned nothing). Building one means: (1)
correctly choosing between `self.body` and `self.table_cell_content` — i.e.
re-deriving `add_text()`'s own `self.in_table and hasattr(self, "table_cell_content")`
routing rule at the call site, which the file's own comment at `add_text()`
(`:896-899`) and the `_desc_break_marker` docstring (`~757-780`, discussing why a
raw position integer is unsafe across the multiple buffer-reassignment sites) both
warn against — this is exactly the kind of duplicated per-site guard the codebase has
already burned effort on generalizing away from; (2) it says nothing about the
`_CONCAT_CONTEXTS` case, where the correct separator is `+`, not a boundary check —
"ends in a newline" is simply the wrong question to ask inside a link body or
attribution; (3) it can't distinguish "safe because we're in a fresh figure" from
"unsafe because we're mid-paragraph with content that happens to have just emitted a
break" without *also* tracking figure/paragraph state, which the flag machinery
already tracks precisely — so the predicate would end up re-deriving state that
already exists in named booleans, just less legibly. Rejected: no precedent, would be
a second, parallel bookkeeping system alongside the flag-based one, and doesn't
generalize to concat contexts.

**(c) Driving the existing `list_item_needs_separator` machinery.** Correct but
incomplete on its own — it only covers the list-item shape (`- item with |sub|
inline`), not the plain-paragraph mid-sentence shape (`Inline substitution |sub| in
a sentence.`, which is a *paragraph*, not a list item — `visit_paragraph` at
`:1410` only special-cases `in_list_item`; a top-level paragraph opens `par({` and
uses `in_paragraph`/`paragraph_has_content` instead, per the table above). Using (c)
alone would leave the mid-sentence-in-a-plain-paragraph shape — the bug report's own
primary reproduction — unfixed.

**(d) A shared helper any inline emitter can call.** This already exists — it is the
triad identified in Q1 (`_add_paragraph_separator()` + `_emit_inline_concat_separator()`
+ the `in_list_item`/`list_item_needs_separator` check), not a new helper to write.

**Recommendation: (c)+(d) merged — call the existing triad verbatim, scoped to the
`else` (non-`in_figure`) branch of `visit_image()`, exactly the way `visit_Text` /
`visit_literal` / `visit_math` already do it.** Concretely, in the non-figure branch
of `visit_image()` (`:4733-4735` today), immediately before
`self.add_text(f'image("{escaped_uri}"')`:

```python
self._add_paragraph_separator()
if not self._emit_inline_concat_separator():
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
```

and, for full parity with the same precedent (so a following sibling inside a concat
context or list item is itself correctly separated from the image), immediately
after the `)` that closes the `image(...)` call in `depart_image()`'s non-figure
branch:

```python
if not self._mark_inline_concat_content():
    if self.in_list_item:
        self.list_item_needs_separator = True
```

This is why the task's "cosmetic-only newline" note matters, and the answer is: **it
matters, but it does not block this recommendation.** `depart_image()`'s existing
`"\n\n"` (non-figure branch, `:4778`) already unconditionally guarantees the
*trailing* boundary. Adding the triad's own bookkeeping (`paragraph_has_content =
True`, `list_item_needs_separator = True`) on top of that guarantee is **provably
redundant but harmless** in exactly the cases where it fires redundantly: measured
directly (see verification log) — the "leading image" and "two images in a row"
shapes gain one *extra* blank line (`"\n\n"` → `"\n\n\n"`) between the image and its
following sibling, compared to pre-fix output. Per `_emit_forced_break()`'s own
docstring, a bare source `"\n"` between two code-mode statements inside `#{ ... }`
is cosmetic only — it satisfies the parser and has **zero** visual effect on the
rendered PDF (no test in the suite asserts exact newline-count adjacency around a
non-figure `image(...)` — confirmed by `grep`, see Q4). Trading a provably invisible
extra blank line for using the *exact same, already-tested, already-understood*
mechanism every other inline node uses — rather than inventing a leaner but novel
read-only variant that has no precedent anywhere else in the file — is the safer
choice for a fix this narrowly scoped and this close to a release.

**`in_figure` interaction (addressed explicitly, not silently skipped):** the fix
touches **only** the `else` branch of `if not self.in_figure:` in `visit_image()`
(`:4733`/`:4751`). The `in_figure` branch (`self.add_text(f'  image("{escaped_uri}"')`,
`:4752`) is untouched. This is provably safe, not just convention-following: an
`image` node is always the *first* child docutils visits inside a `figure` (image,
then optional `caption`, then optional `legend` — verified against
`visit_figure`/`visit_caption`/`visit_legend` node-order assumptions throughout the
file, e.g. the `_figure_has_legend` scan at `:2982`). Whatever branch `visit_figure`
took (`:2996-3003`: `figure(\n`, `[#figure(\n`, or `block(width:...)[#figure(\n`,
optionally followed by `{\n` for a legend body) always ends in `"\n"` by the time
`visit_image` runs — so even the general triad, if run unconditionally inside
`in_figure`, would be a no-op there (`in_paragraph` is `False` inside a figure body,
no concat context is active, and `visit_figure` itself already drained
`list_item_needs_separator` at `:2964-2966` before opening `figure(`). Measured
directly: the figure case is byte-for-byte **unchanged** (`CHANGED: False`) whether or
not the fix is applied. The recommendation keeps the branch split anyway (rather than
relying on that no-op proof and merging the branches) because it is the minimum-diff
change and keeps the already-passing exact-byte figure tests (Q4) trivially safe
against any future change to the triad's own logic.

**`in_table` interaction (addressed explicitly):** `add_text()` (`:887`) is the
*only* place that knows whether output goes to `self.body` or
`self.table_cell_content` — every mechanism in the recommended fix (`add_text()`
itself, `_add_paragraph_separator()`, `_emit_inline_concat_separator()`) is
flag-driven and calls `add_text()` for its own emission, so it **never needs to know
which buffer is live**. This is precisely why (b)'s "inspect the buffer" predicate is
inferior: it would have to duplicate `add_text()`'s routing decision at the call
site, while the flag-driven triad sidesteps the question entirely. Measured directly:
an image mid-sentence inside a table-cell paragraph (`in_table=True`, `in_paragraph=True`,
output accumulating in `table_cell_content`) is broken identically to the plain-paragraph
case pre-fix (`expected semicolon or line break`) and fixed identically post-fix,
verified by a real `typst.compile()` of the generated `table(...)` fragment.

**`_in_attribution` interaction (addressed explicitly):** `_in_attribution` is one of
the five `_CONCAT_CONTEXTS` entries (`:1636`). An image inside a block-quote
attribution that already has a prior sibling is, **today, already broken** (bare
juxtaposition, no operator at all — this is a pre-existing latent defect, not
something the fix introduces or need avoid regressing, since nothing exercises it).
Measured directly: pre-fix, `visit_image` inside `_in_attribution` with
`_attribution_has_content=True` emits a bare `image("img.png")` with nothing before
it; post-fix, `_emit_inline_concat_separator()` correctly emits `" + image("img.png")"`
— the same shape `visit_Text`/`visit_literal` already produce in that context. Net
effect: a previously-untested, previously-broken corner is fixed for free by reusing
the shared helper, at zero cost to any passing test.

## Answer to Q3 — The "already ends at a line boundary" predicate

**Not needed for the recommended mechanism**, and this is deliberate, not an
omission: the recommendation in Q2 never inspects `self.body` or
`self.table_cell_content` directly. It reads only three existing scalar/stack flags
(`self.in_paragraph`, `self.paragraph_has_content`, the five `_CONCAT_CONTEXTS`
flags via `_inline_concat_context()`, and `self.in_list_item` /
`self.list_item_needs_separator`) — all already maintained correctly by the
surrounding block visitors regardless of which buffer `add_text()` is currently
routing into.

**Confirmed absent from the codebase** (the question asks to search before
proposing a new one): `grep -n 'endswith("\\n")\|rstrip().endswith\|\[-1:\]'` across
`translator.py` returns nothing. No such predicate exists anywhere in this file
today. If a future change ever needs one anyway (out of scope for this milestone),
the specification would have to be:

- **Buffer to inspect:** whichever `add_text()` would route into right now — i.e.
  `self.table_cell_content if (self.in_table and hasattr(self, "table_cell_content"))
  else self.body` — the exact condition at `:896-899`, not a fixed choice of one or
  the other.
- **Empty buffer:** counts as "already at a line boundary" (no separator needed) —
  this is what makes every `test_translator.py` unit test that calls
  `translator.visit_image(image)` on a freshly constructed translator (empty
  `self.body`) continue to emit `image("...")` with no leading anything.
- **Trailing empty-string chunk:** a list-of-fragments buffer can have `""` as its
  last-appended element (e.g. from a conditional `add_text("")` somewhere); the
  predicate would need to walk backward past empty strings to find the last
  non-empty chunk's last character, not just check `buffer[-1]`.
- **Trailing spaces:** should **not** count as a line boundary — Typst's own
  `"expected semicolon or line break"` is specifically about needing a newline (or
  semicolon) between statements; trailing spaces before that boundary are
  irrelevant to the parser but the predicate must not be fooled into treating
  `"...  "` (trailing spaces, no newline) as safe.

This specification is recorded for completeness per the question, but the
recommended fix in Q2 does not require it and the planner should not build it for
this milestone.

## Answer to Q4 — Blast radius

**No handler calls into `visit_image()`/`depart_image()` indirectly** — docutils'
`walkabout()` dispatches `visit_image`/`depart_image` directly by node type; nothing
in `translator.py` invokes either method as a helper from another `visit_*`. The
only structural dependency is `visit_figure`/`depart_figure` relying on `image`
being the figure's first child (see Q2's `in_figure` analysis) — unaffected, since
the fix doesn't touch the `in_figure` branch.

**Tests with `image(` assertions** (from `grep -rln "image(" tests/`, 144 total
matches across 20 files): every non-figure-scoped assertion is a **substring**
check (`assert 'image("...")' in output` / `in typ_text`), never an exact
full-string or `startswith` comparison — confirmed by `grep -n "output ==\|
output.startswith\|astext() =="` across `test_translator.py` (only one exact-equality
hit in the whole file, `assert output == ""`, unrelated to images). A leading `"\n"`
or an extra redundant blank line elsewhere in the same fragment cannot break a
substring check. The two tests with **exact, position-sensitive** string matches are
both in the untouched `in_figure` branch:

- `tests/test_nested_figure_render_gate.py:256` — `'  image("img.png"),\n'` inside
  `[#figure(\n  image("img.png"),\n  caption: {...}\n) <index:id4>]` (the
  image-only-figure byte-invariance control for FIG-01).
- `tests/test_pdf_render_gate.py:2303` — `'block(width: 60%)[#figure(\n
  image("image.png")\n)]'`.

Both are figure-branch-only and both were measured **byte-unchanged** by the
scratch harness with the recommended fix applied.

**Achievability of the project's "zero pre-existing test edits" standard: yes,
achievable, and verified, not merely asserted.** The scratch-harness compile log
(all runs against the real `TypstTranslator`, real `typst.compile()`, root =
scratch dir, never touching the repo tree):

```
before_mid   (Inline substitution |sub| in a sentence.)      FAIL: expected semicolon or line break
after_mid    (same, with the recommended fix)                OK
before_two   (Two in a row |sub| |sub| here.)                 FAIL: expected semicolon or line break
after_two    (same, fixed)                                    OK
before_list  (- item with |sub| inline)                       FAIL: expected semicolon or line break
after_list   (same, fixed)                                    OK
before_table (image mid-sentence inside a table cell)          FAIL: expected semicolon or line break
after_table  (same, fixed)                                     OK
figure       (nested figure control)                           byte-identical before/after (CHANGED: False)
```

No test in the existing suite needs to change. New regression tests are additive
only, and per the todo's own instruction should assert on a real
`typst.compile()`, not just the emitted string (the string `text("...")image(...)`
*looks* plausible — only the parser rejects it — which is exactly why this defect
survived every prior suite run undetected).

## Answer to Q5 — Build order

Dependencies, in the order they must be satisfied:

1. **`visit_image()`/`depart_image()` fix** (translator.py, the mechanism from Q2)
   — must land first; everything else in the milestone is either testing it,
   documenting it, or shipping the release that contains it.
2. **Regression gate** — a real-compile test binding the four broken shapes
   (mid-sentence substitution image, two images in a row, image in a list item,
   any image preceded by sibling content) **and** the two shapes that must keep
   passing byte-identical (image first in its paragraph — control for the
   redundant-blank-line tradeoff in Q2; image inside `.. figure::` — control for
   the `in_figure` branch). This depends on step 1 existing to test against, and
   should be written/executed together with or immediately after it (TDD-red-then-
   green is fine either order, but the gate must exist before the phase is
   considered done — this is the "single site, not a class" milestone framing
   from `PROJECT.md`, so the gate is the proof that the *right* single site was
   fixed).
3. **CHANGELOG curation** — depends on step 1+2 being complete and committed, since
   the `## [0.9.2]` entry needs to describe the actual fix (not a planned one), and
   per `PROJECT.md`'s binding constraints, this entry also folds in v0.9.1's
   already-completed-but-never-published `## [Unreleased]` bullets (PATH-01,
   IMG-04..IMG-07, MSG-01..MSG-05) — no separate `## [0.9.1]` heading, since that
   version was never released.
4. **Version bump** (`pyproject.toml` as sole literal, `uv.lock` + `README.md` in
   lockstep) — depends on step 3 only in the sense that both are "release-prep"
   bookkeeping and are conventionally done together in one phase; the version
   number itself has no code dependency on the changelog text.
5. **Release-prep checkbox fence** — per `PROJECT.md`'s binding constraint 5, a
   SHA-256 of `REQUIREMENTS.md` must be recorded at phase head and re-verified at
   close, guarding against `phase.complete`'s auto-flip-to-`[x]` defect that has
   fired at five consecutive prior release-prep closes. This is a process gate
   around steps 3-4, not a separate code dependency.
6. **Tag + PyPI publish + GitHub Release** — must be strictly last; depends on
   1-5 all being merged to the branch that gets tagged. Per binding constraint 6,
   `release.yml`'s `create-release` job has a known-flaky history (failed on the
   v0.7.0 tag with `uv: command not found`, green since v0.8.0/v0.9.0) — a failure
   here is handled inside this same step, not deferred to a follow-up milestone,
   since REL-09 (publish to PyPI) is the one requirement this whole milestone
   exists to finally close.

Recommended phase shape: **Phase A (fix + gate)** = steps 1-2 together (the gate
is the acceptance criterion for the fix, so splitting them into separate phases
buys nothing and risks a phase boundary where "fixed" is claimed before "proven by
real compile"). **Phase B (release-prep)** = steps 3-5. **Phase C (publish)** = step
6, kept separate so a publish-path failure (constraint 6) doesn't block re-running
just the fix or the changelog curation if either needs a fixup pass first.

## Sources

- `typsphinx/translator.py` (HEAD, 2026-08-30) — all file:line citations above are
  direct reads of this file at the current commit; no external documentation was
  needed since this is entirely an internal-mechanism question.
- `.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`
  — original defect report, reproduction matrix, and root-cause framing.
- `.planning/PROJECT.md` (`## Current Milestone: v0.9.2`) — scope, binding
  constraints (including the 14-construct sweep that established this is "a
  single site, not a class"), and release-process obligations (REL-09, the
  checkbox-fence guard, the `release.yml` flake history).
- `tests/test_translator.py`, `tests/test_nested_figure_render_gate.py`,
  `tests/test_pdf_render_gate.py`, and the other 18 files matched by
  `grep -rln "image(" tests/` — surveyed for assertion shape (substring vs. exact)
  to assess blast radius.
- Scratch-harness verification (this session, under
  `/tmp/claude-1000/-home-yuta-Documents-typsphinx/f02be4ed-caf0-468a-897c-407113bde367/scratchpad/imgfix/`):
  a monkey-patched `TypstTranslator.visit_image` exercising the recommended triad
  against six real docutils-node shapes, each compiled with the real `typst`
  Python package (not merely string-inspected) to confirm before=FAIL/after=OK for
  the four broken shapes and before=after (byte-identical) for the figure control.
  No file in the actual repository working tree was modified to produce this
  evidence.

---
*Architecture research for: typsphinx v0.9.2 (`visit_image()` separator fix)*
*Researched: 2026-08-30*
